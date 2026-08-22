"""Closing a lane, and handing the session on — both generated from measured state.

Two different things wear the word "handoff" and they want different homes:

  LANE     one lane finishing. What it changed, what is left, what the next person must not
           re-derive. Belongs on the lane card, where the claim is.
  SESSION  everything that moved while you were here, across lanes. Belongs on its own tab,
           because it spans them and it is what a cold session actually reads.

**Almost none of it should be typed.** Gate verdicts, commits, dirty worktrees, findings added,
claims held — all measured. The only thing a human must supply is the part no instrument can see:
what you were part-way through, and what you would warn the next person about. So the generated
handoff carries the facts and leaves exactly one hole for judgement, rather than asking somebody
to restate at midnight what the repo already knows.

⚠ **The preflight is a report, not a gate.** It runs the checks a lane is supposed to pass and
says which failed; it does not refuse. Refusing here would put the only exit behind a web button,
and a session that cannot close cleanly must still be able to close honestly — an override that
records *why* is worth more than a block someone works around by never clicking it.
"""
from __future__ import annotations

import datetime as _dt
import pathlib
import subprocess
import sys
from typing import Dict, List, Optional

REPO = pathlib.Path(__file__).resolve().parent.parent
#: Boot prompts are cross-repo session memory and live in aldc-launchpad by long-standing
#: convention. Writing them here instead would create the fifth artefact home CLAUDE.md warns of.
BOOT = REPO.parent / "aldc-launchpad" / "boot-prompts"


def _run(args: List[str], cwd: Optional[pathlib.Path] = None, timeout: int = 300):
    try:
        r = subprocess.run(args, cwd=str(cwd or REPO), capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=timeout)
        return r.returncode, (r.stdout + r.stderr).strip()
    except subprocess.TimeoutExpired:
        return 124, f"timed out after {timeout}s"
    except Exception as exc:                                       # noqa: BLE001
        return 125, f"{type(exc).__name__}: {exc}"


def preflight(lane_id: str) -> List[dict]:
    """The checks a lane is meant to pass before closing. Each returns ok + a one-line detail."""
    from . import findings
    out: List[dict] = []

    code, out_txt = _run([sys.executable, "-m", "pytest", "-q"])
    last = out_txt.strip().splitlines()[-1] if out_txt.strip() else "(no output)"
    out.append({"check": "the suite is green", "ok": code == 0, "detail": last[:120]})

    for script, label in (("build_tracker.py", "the published tracker matches the gate set"),
                          ("build_plan.py", "the build plan matches the lanes")):
        code, txt = _run([sys.executable, f"scripts/{script}", "--check"])
        out.append({"check": label, "ok": code == 0,
                    "detail": (txt.splitlines()[-1] if txt else "")[:120]})

    # A lane that closes without touching the ledger has not said whether it learned anything,
    # and silence has to mean "checked", not "nobody looked".
    hits = findings.by_lane().get(lane_id, [])
    nothing = findings.nothing_to_report()
    out.append({"check": "the findings ledger was touched",
                "ok": bool(hits) or nothing > 0,
                "detail": (f"{len(hits)} finding(s) reach this lane; "
                           f"{nothing} NOTHING TO REPORT entr(ies) in the ledger")})
    return out


def lane_state(lane_id: str) -> dict:
    """What is measurably true about this lane right now."""
    from . import claims, worktrees
    from .lanes import LANES
    from .readiness import PASS, measure
    lane = next((l for l in LANES if l.id == lane_id), None)
    verdicts = {g.id: r.verdict for g, r in measure()}
    wts = {w["lane"]: w for w in worktrees.status()}
    return {
        "lane": lane_id,
        "gates": {g: verdicts.get(g, "?") for g in (lane.gates if lane else [])},
        "passing": [g for g in (lane.gates if lane else []) if verdicts.get(g) == PASS],
        "worktree": wts.get(lane_id),
        "claim": claims.active().get(lane_id),
    }


def write_lane_handoff(lane_id: str, note: str, overrides: Optional[List[str]] = None) -> pathlib.Path:
    """Write the lane's closing note. The measured half is generated; `note` is the human half."""
    st = lane_state(lane_id)
    checks = preflight(lane_id)
    failed = [c for c in checks if not c["ok"]]
    stamp = _dt.datetime.now().strftime("%Y-%m-%d")
    BOOT.mkdir(parents=True, exist_ok=True)
    p = BOOT / f"lane-{lane_id}-{stamp}.md"
    n = 2
    while p.exists():
        p = BOOT / f"lane-{lane_id}-{stamp}-{n}.md"
        n += 1

    lines = [f"# Lane handoff — {lane_id} ({stamp})", "",
             "Generated from measured state by `factory.handoff`. The **Where it got to** section",
             "is the only part a human wrote; everything else was read from the repo.", "",
             "## Gates in this lane", ""]
    for g, v in st["gates"].items():
        lines.append(f"- `{g}` — **{v}**")
    w = st["worktree"]
    lines += ["", "## Working state", ""]
    if w:
        lines.append(f"- worktree `{w['path']}` on branch `lane/{lane_id}`")
        lines.append(f"- {w['commits_ahead']} commit(s) ahead of the base branch")
        lines.append("- ⚠ **uncommitted changes present — read them before removing the worktree**"
                     if w["dirty"] else "- working tree clean")
    else:
        lines.append("- no worktree; this lane was worked in the main checkout or not started")

    lines += ["", "## Preflight at close", ""]
    for c in checks:
        lines.append(f"- {'✅' if c['ok'] else '❌'} {c['check']} — {c['detail']}")
    if failed:
        lines += ["", f"⛔ **Closed with {len(failed)} failing check(s).** "
                      + ("Reason given: " + "; ".join(overrides) if overrides
                         else "No reason was recorded, which is itself worth knowing.")]

    lines += ["", "## Where it got to", "", note.strip() or "_(nothing recorded)_", "",
              "## Next", "",
              f"Read `agent-factory/docs/findings.md` first, then re-open this lane from the",
              f"tracker at `:8099/lanes`. Its prompt is generated and current — do not work from",
              f"a copy pasted earlier.", ""]
    p.write_text("\n".join(lines), encoding="utf-8")
    return p


def session_handoff(note: str = "") -> str:
    """The cross-lane handoff: everything that moved, assembled from measurement."""
    from . import claims, findings, synthesis, worktrees
    from .lanes import LANES
    from .readiness import GATES, PASS, measure
    from . import schedule

    results = measure()
    passing = [g.id for g, r in results if r.verdict == PASS]
    now = _dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    L: List[str] = [f"# Session handoff — {now}", "",
                    "Generated by `factory.handoff.session_handoff`. Every number below was",
                    "measured when this was produced; nothing is remembered.", "",
                    f"## State", "",
                    f"- **{len(passing)} of {len(GATES)} gates pass**"]
    try:
        v = schedule.velocity()
        L.append(f"- gates {v.first.passed} → {v.last.passed} ({v.pass_per_hour:.2f}/h); "
                 f"gate set {v.first.total} → {v.last.total} ({v.scope_per_hour:.2f}/h) "
                 f"over {v.hours:.1f}h")
        if v.net_remaining_per_hour > 0:
            L.append("- ⚠ the backlog is still growing faster than it is burned down, so no "
                     "completion date is projectable")
    except Exception as exc:                                       # noqa: BLE001
        L.append(f"- velocity UNMEASURABLE: {exc}")

    held = claims.active()
    L += ["", "## Lanes", ""]
    for lane in LANES:
        done = [g for g in lane.gates if g in passing]
        bits = [f"{len(done)}/{len(lane.gates)} gates", f"run on {lane.model}"]
        if lane.id in held:
            c = held[lane.id]
            bits.append(f"**CLAIMED** {c.human_age()}" + (" — STALE" if c.stale else ""))
        if lane.needs_paul:
            bits.append("needs Paul")
        L.append(f"- **{lane.id}** — {' · '.join(bits)}")

    wts = worktrees.status()
    if wts:
        L += ["", "## Worktrees", ""]
        for x in wts:
            L.append(f"- `{x['lane']}` — {x['commits_ahead']} ahead"
                     + (", **uncommitted changes**" if x["dirty"] else ", clean"))
        L.append("")
        L.append("Never removed automatically. A worktree can hold the only copy of a "
                 "session's work.")

    gap = synthesis.unsynthesised()
    L += ["", "## Records", "",
          f"- findings ledger: {len(findings.load())} entries, "
          f"{len(findings.unattached())} reaching no lane",
          f"- decision record: " + ("current" if not gap else
                                    f"⛔ does not mention {', '.join(gap)}")]

    L += ["", "## Carried by hand", "", note.strip() or
          "_(nothing recorded — the generated sections above are all there is)_", ""]
    return "\n".join(L)
