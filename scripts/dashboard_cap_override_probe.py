"""Watch the dashboard refuse, and watch the override reach the wire.

The attempt cap's override existed only in `server.py`. `static/index.html` never sent
`override_reason`, so an operator who hit the cap got — and this is the part that turned a
gap into a defect — a **green success toast**, because `api()` returns the parsed body
whatever the HTTP status and the caller read `result.dispatched || 0`. The refusal was
invisible at the one surface a human watches, and the routes past it were curl or Delete
Pipeline, which is the 2026-08-14 workaround that destroyed the evidence along with the
loop.

This probe is the consumer-layer check for that fix: a real Chromium, the real
`index.html`, the real functions, and — the part that matters — **the real refusal
message, produced by driving `check_attempt_cap` in this process**, not a string typed
here. `isAttemptCapRefusal` is a regex, and finding F19 in this programme is a regex guard
that had never been shown to match the line it was written for. A pattern tested against a
message the test invented proves nothing.

    python scripts/dashboard_cap_override_probe.py [--screenshot DIR]

Exit 0 means all eight behaviours were watched happening in a browser.
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import sys
import tempfile

FACTORY = pathlib.Path(__file__).resolve().parent.parent
CONNECTORS = pathlib.Path(os.environ.get("PREFECT_CONNECTORS",
                                         FACTORY.parent / "prefect-connectors"))
INDEX = CONNECTORS / "orchestrator" / "static" / "index.html"


def real_refusal_message() -> str:
    """The message the engine actually produces, by making it refuse."""
    sys.path.insert(0, str(CONNECTORS))
    from orchestrator import pipelines as engine
    from orchestrator.engine import audit as audit_trail

    tmp = pathlib.Path(tempfile.mkdtemp(prefix="cap-probe-"))
    audit_trail.configure(tmp, tmp / "sessions")
    engine.configure(tmp)
    engine._pipelines.clear()
    stage = {"name": "trigger-run", "status": "failed", "depends_on": [], "type": "script",
             "timeout_min": 10, "_attempts": engine.MAX_ATTEMPTS_PER_STAGE}
    pipeline = {"id": "pipe_probe", "ticket_id": "GP-PROBE", "ticket_title": "cap probe",
                "pipeline_type": "connector-migration", "client_code": "GEP",
                "status": "running", "stages": [stage], "params": {}, "prior_results": {},
                "budget_usd": 0}
    engine._pipelines["pipe_probe"] = pipeline
    try:
        engine.check_attempt_cap(pipeline, stage, "probe")
    except engine.ControlRefused as exc:
        return str(exc)
    raise SystemExit("the cap did NOT refuse at the ceiling — nothing to test")


DRIVER = """
(async (message) => {
  const seen = [];
  const toasts = [];
  let prompted = null;

  window.fetch = async (url, opts) => {
    const body = opts && opts.body ? JSON.parse(opts.body) : {};
    seen.push({ url: String(url), body });
    if (body.override_reason) {
      return new Response(JSON.stringify({ ok: true, dispatched: 1 }),
                          { status: 200, headers: {'Content-Type': 'application/json'} });
    }
    return new Response(JSON.stringify({ error: message }),
                        { status: 400, headers: {'Content-Type': 'application/json'} });
  };

  const realToast = window.toast;
  window.toast = (m, t) => { toasts.push({ m, t }); realToast(m, t); };
  window.loadPipelines = async () => {};

  // 1. the operator supplies a reason
  window.prompt = (q) => { prompted = q; return '  credential was fixed, GP-318  '; };
  await window.retryStage('pipe_probe', 'trigger-run');
  const withOverride = { seen: seen.slice(), toasts: toasts.slice(), prompted };

  // 2. the operator cancels
  seen.length = 0; toasts.length = 0;
  window.prompt = () => '';
  await window.retryStage('pipe_probe', 'trigger-run');
  const cancelled = { seen: seen.slice(), toasts: toasts.slice() };

  // 3. whitespace is not a reason
  seen.length = 0; toasts.length = 0;
  window.prompt = () => '   ';
  await window.restartFrom('pipe_probe', 'trigger-run');
  const blank = { seen: seen.slice(), toasts: toasts.slice() };

  return { withOverride, cancelled, blank };
})
"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--screenshot", default="")
    args = ap.parse_args()

    if not INDEX.is_file():
        print(f"no dashboard at {INDEX}")
        return 2

    message = real_refusal_message()
    print(f"the engine's own refusal:\n  {message}\n")

    from playwright.sync_api import sync_playwright

    with sync_playwright() as pw:
        browser = pw.chromium.launch(channel="chrome")
        page = browser.new_page()
        # `confirm` guards the fresh-restart path and would block forever unattended.
        page.add_init_script("window.confirm = () => true;")
        page.goto(INDEX.as_uri())
        page.wait_for_function("typeof window.retryStage === 'function'", timeout=15000)
        result = page.evaluate(DRIVER, message)

        if args.screenshot:
            out = pathlib.Path(args.screenshot)
            out.mkdir(parents=True, exist_ok=True)
            # A fresh page: the driver above leaves a stack of toasts part-way through
            # their 4-second expiry, and a screenshot of those reads as a rendering bug
            # rather than as the two states an operator actually sees.
            page.goto(INDEX.as_uri())
            page.wait_for_function("typeof window.toast === 'function'", timeout=15000)
            page.evaluate("(m) => window.toast(m, 'error')", message)
            page.evaluate("() => window.toast('Attempt cap overridden — one more attempt, recorded', 'success')")
            page.wait_for_timeout(600)  # let the toast transition finish before capturing
            page.screenshot(path=str(out / "cap-override-toasts.png"))
            print(f"screenshot -> {out / 'cap-override-toasts.png'}")
        browser.close()

    ok = True

    def check(label, cond, detail=""):
        nonlocal ok
        ok = ok and bool(cond)
        print(f"  {'ok ' if cond else '!! '} {label}{('  — ' + detail) if detail else ''}")

    a = result["withOverride"]
    check("the refusal was recognised as a cap refusal, not a generic error",
          a["prompted"] is not None,
          "the operator was asked for a reason" if a["prompted"] else
          "NO PROMPT — the regex in isAttemptCapRefusal did not match the real message")
    check("the first request carried no override", len(a["seen"]) >= 1
          and "override_reason" not in a["seen"][0]["body"])
    check("the second request carried the override to the wire",
          len(a["seen"]) == 2 and a["seen"][1]["body"].get("override_reason")
          == "credential was fixed, GP-318",
          json.dumps(a["seen"][1]["body"]) if len(a["seen"]) == 2 else f"{len(a['seen'])} request(s)")
    check("the refusal was shown to the operator as an ERROR, not a success",
          any(t["t"] == "error" for t in a["toasts"]),
          "; ".join(f"[{t['t']}] {t['m'][:60]}" for t in a["toasts"]))
    check("no success toast was raised before the override succeeded",
          [t["t"] for t in a["toasts"]].count("success") == 1)

    b = result["cancelled"]
    check("cancelling sends NOTHING", len(b["seen"]) == 1,
          f"{len(b['seen'])} request(s)")
    check("cancelling says nothing was retried",
          any("nothing was retried" in t["m"] for t in b["toasts"]))

    c = result["blank"]
    check("a whitespace-only reason is not an override", len(c["seen"]) == 1,
          f"{len(c['seen'])} request(s)")

    print()
    print("WATCHED: the dashboard refuses, and the override reaches the wire."
          if ok else "FAILED: the dashboard did not behave as claimed.")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
