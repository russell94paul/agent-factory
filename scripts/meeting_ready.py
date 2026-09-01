"""One command between "the record changed" and "this is safe to open in front of the client".

    python scripts/meeting_ready.py

It reads canonical state, compiles the view model, renders the artifact, runs the meeting gate and
then loads the built page in a real browser. Nothing here is new machinery — every step already
existed as a separate command, and every one of them had to be remembered, in order, under time
pressure, on the morning of a client meeting. This is the order, written down and executable.

    canonical state → compile → render → gate → rendered validation → open

Exit codes are the contract:

    0   READY / READY_WITH_WARNINGS and the page rendered. Safe to open.
    1   the gate refused, or the rendered check found a problem. NOT safe to open.
    2   the compile itself failed — there is no artifact at all.

⭐ **Both halves are required and neither substitutes for the other.** The gate reads the data and
cannot see a blank page; the render check loads the page and cannot see a stale number. The estate
has been burned by each failure separately: a query-layer check passing while every visual showed
an error, and a value rendering perfectly while meaning something that was no longer true.

Options:
    --root <path>     resolve cited evidence against another checkout (use when the mission's
                      evidence has not merged into this one yet)
    --no-render       skip the browser pass (CI without a browser). Says so in the output, and
                      the result is then SOURCE_CODE_IMPLIES, never RENDERED_CONFIRMED.
    --open            open the finished artifact in the default browser
"""
from __future__ import annotations

import argparse
import pathlib
import subprocess
import sys
import webbrowser

REPO = pathlib.Path(__file__).resolve().parent.parent

NARRATIVE = "missions/client-review-v1/reviews/navira-marketing-model.yaml"
TASKS = ".data/tasks.jsonl"
MISSION = ".data/missions/marketing-model-reconstruction-v1.json"
OUT = "docs/artifacts/client-review-navira.html"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python scripts/meeting_ready.py")
    ap.add_argument("--narrative", default=NARRATIVE)
    ap.add_argument("--tasks", default=TASKS)
    ap.add_argument("--mission", default=MISSION)
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--root", default=None,
                    help="checkout the cited evidence resolves against")
    ap.add_argument("--no-render", action="store_true",
                    help="skip the browser pass; the result is then not RENDERED_CONFIRMED")
    ap.add_argument("--open", action="store_true", help="open the artifact when it is ready")
    a = ap.parse_args(argv)

    sys.path.insert(0, str(REPO))
    from factory import client_review as cr                 # noqa: PLC0415
    from factory.client_review_render import render_html    # noqa: PLC0415

    root = pathlib.Path(a.root) if a.root else REPO
    out = REPO / a.out

    # ---- 1. canonical state → view model ---------------------------------------------------
    print("1/4  compiling from canonical state")
    print(f"       narrative  {a.narrative}")
    print(f"       tasks      {a.tasks}")
    print(f"       mission    {a.mission}")
    print(f"       root       {root}")
    try:
        review = cr.assemble(REPO / a.narrative,
                             tasks_path=REPO / a.tasks,
                             mission_path=REPO / a.mission,
                             root=root)
    except cr.ReviewError as exc:
        print(f"\nCOMPILE FAILED  {exc}")
        return 2

    d = review.diagnostics
    print(f"       {len(review.delivered)} outcome(s), {len(review.evidence)} evidence item(s), "
          f"{len(review.decisions)} decision(s) · freshness "
          f"{review.review['freshness_state']} · last verified "
          f"{review.review['last_verified_at']}")

    # ---- 2. render -------------------------------------------------------------------------
    print(f"2/4  rendering  {a.out}")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render_html(review), encoding="utf-8")
    print(f"       {out.stat().st_size:,} bytes, self-contained")

    # ---- 3. the gate -----------------------------------------------------------------------
    print("3/4  meeting gate")
    g = cr.meeting_gate(review)
    for c in g["checks"]:
        mark = {"PASS": "  ok  ", "WARN": " warn ", "BLOCK": "BLOCK "}[c["status"]]
        print(f"       {mark} {c['id']:<36} {c['detail']}")

    # ---- 4. rendered validation ------------------------------------------------------------
    render_ok = None
    if a.no_render:
        print("4/4  rendered validation SKIPPED (--no-render)")
    else:
        print("4/4  rendered validation (real browser)")
        r = subprocess.run(
            [sys.executable, str(REPO / "scripts" / "render_check_client_review.py"),
             "--html", a.out],
            cwd=str(REPO), capture_output=True, text=True)
        render_ok = (r.returncode == 0)
        for line in (r.stdout or "").splitlines():
            print(f"       {line}")
        if r.returncode != 0 and r.stderr:
            print(f"       {r.stderr.strip()[:600]}")

    # ---- verdict ---------------------------------------------------------------------------
    print()
    print(f"GATE            {g['verdict']}")
    print("RENDER          " + ("RENDERED_CONFIRMED" if render_ok
                                else ("SOURCE_CODE_IMPLIES (browser pass skipped)"
                                      if a.no_render else "FAILED")))
    print(f"ARTIFACT        {a.out}")

    safe = (g["verdict"] != cr.GATE_NOT_READY) and (render_ok is not False)
    if safe:
        print("\nSAFE TO OPEN IN FRONT OF THE CLIENT.")
        for c in g["warnings"]:
            print(f"  presenter should know: {c['id']} — {c['detail']}")
        if a.open:
            webbrowser.open(out.as_uri())
        return 0

    print("\nDO NOT OPEN THIS IN FRONT OF THE CLIENT YET.")
    for c in g["blocking"]:
        print(f"  blocking: {c['id']} — {c['detail']}")
    if render_ok is False:
        print("  blocking: the rendered page did not pass its own check (see above)")
    # The artifact still exists and still degrades honestly — that is the point of the pending
    # states. What is refused is the claim that it is finished, not the file.
    print(f"\nThe artifact at {a.out} is still valid to read internally: every unresolved item"
          "\nrenders as an explicit non-final state and no absence renders as a value.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
