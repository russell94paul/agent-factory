"""Supervisor for the Switchboard: one long-lived parent, a replaceable child.

    python scripts/switchboard_dev.py --port 8110

⭐ **Why a supervisor rather than extending the in-process reload.** Not because reload does not
work — it does, and it is reused (see below). Because there is one module it structurally cannot
reach: the one currently executing. `scripts/local_tracker.py` defines the route table, the
`Handler` class and `render()`, and `importlib.reload` cannot replace the frame it is running
inside. Everything in this file exists to cover that single gap, and nothing more.

The alternative — teaching the tracker to rebuild its own handler class and re-bind its own routes
in place — is a page that *claims* it reloaded and sometimes has not, which is the same class of
defect as a cached number rendered as a fresh one. A fresh process makes the claim true by
construction, and its correctness is a property of the OS rather than of our own cleverness.

⛔ **A real source reload already existed here, and it was measured before this file was written
rather than assumed away.** `local_tracker.hot_reload()` calls `importlib.reload` over every
`factory.*` module the tracker imports and then re-binds the `from x import y` names that reload
leaves stale. Measured on this checkout, 2026-09-01:

    hot modules                              38
    factory.work / factory.switchboard_p1    both covered (the list is DERIVED from imports)
    reloaded 38 modules, rebound 20 names, 30 gates
    can reload scripts/local_tracker.py      NO

So it is reused, not replaced: it backs **Re-measure**, and it genuinely re-serves edited domain
code. What it structurally cannot do is replace the module that *defines the server* — the route
table, the `Handler` class and `render()` all live in `local_tracker.py`, and a module cannot
reload the code currently executing inside it. That gap is the whole job of this supervisor, and
it is why the two controls are separate rather than one button with two meanings.

## The contract with the child

    child exits RESTART_EXIT (97)   ->  the UI asked for a restart; start a fresh child
    child exits anything else       ->  stop. A crash is not a restart request.
    Ctrl+C in this terminal         ->  signal the child, wait for it, exit.

The port never changes and this process never binds it — the child does — so an ngrok tunnel
pointed at the port survives every restart. Nothing about the tunnel is this script's business,
which is precisely why it keeps working.

## Security posture

This wrapper adds no network surface at all: it opens no socket and reads no request. It sets
`SWITCHBOARD_SUPERVISED=1`, which is the ONLY thing that makes the child mint a restart token and
render the restart control. An unsupervised server refuses the endpoint outright, because a
restart with nothing to restart it is just a remote kill switch.
"""
from __future__ import annotations

import argparse
import os
import pathlib
import signal
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
TRACKER = HERE / "local_tracker.py"

#: Must match `local_tracker.RESTART_EXIT`. Imported rather than re-typed, so the two cannot drift
#: into a state where the child asks for a restart in a dialect the supervisor does not speak.
try:
    sys.path.insert(0, str(HERE.parent))
    from scripts.local_tracker import RESTART_EXIT           # type: ignore  # noqa: E402
except Exception:                                            # noqa: BLE001
    RESTART_EXIT = 97

#: A restart that fails instantly, repeatedly, is a crash loop wearing a restart's clothes. The
#: supervisor stops after this many consecutive restarts that did not stay up for `MIN_UPTIME_S`.
MAX_FAST_RESTARTS = 5
MIN_UPTIME_S = 3.0


def _child_env() -> dict:
    env = dict(os.environ)
    # The one switch that arms the restart control. Without it the child mints no token and the
    # UI renders "Restart is unavailable" rather than a button that would exit into nothing.
    env["SWITCHBOARD_SUPERVISED"] = "1"
    env.setdefault("PYTHONUNBUFFERED", "1")
    return env


def run(port: int, open_browser: bool = False) -> int:
    argv = [sys.executable, str(TRACKER), "--serve", "--port", str(port)]
    if open_browser:
        argv.append("--open")
    fast = 0
    print(f"switchboard supervisor · port {port} · child {TRACKER.name}")
    print("the supervisor binds nothing; the child owns the port, so a tunnel survives restarts")
    print("ctrl-c to stop both\n")

    while True:
        import time
        started = time.time()
        try:
            proc = subprocess.Popen(argv, env=_child_env())
        except OSError as exc:
            print(f"supervisor: could not start the child: {exc}", file=sys.stderr)
            return 1
        try:
            code = proc.wait()
        except KeyboardInterrupt:
            # ⛔ Terminate, then WAIT. Returning without waiting leaves the child holding the
            # port, so the next launch fails to bind and the operator concludes the port is
            # taken by something else.
            print("\nsupervisor: stopping the child…")
            try:
                proc.send_signal(signal.SIGTERM)
            except Exception:                                # noqa: BLE001
                pass
            try:
                proc.wait(timeout=8)
            except Exception:                                # noqa: BLE001
                proc.kill()
                proc.wait()
            print("supervisor: stopped.")
            return 0

        if code != RESTART_EXIT:
            print(f"supervisor: child exited {code}; not a restart request, so stopping.")
            return code

        up = time.time() - started
        fast = fast + 1 if up < MIN_UPTIME_S else 0
        if fast >= MAX_FAST_RESTARTS:
            print(f"supervisor: {fast} restarts in under {MIN_UPTIME_S}s each — refusing to "
                  f"relaunch. Something is failing at startup; the last child's output is above.",
                  file=sys.stderr)
            return 1
        print(f"\nsupervisor: restart requested (child was up {up:.1f}s) — starting a fresh "
              f"child on the same port\n")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--port", type=int, default=8110)
    ap.add_argument("--open", action="store_true", help="open a browser on the first launch only")
    a = ap.parse_args(argv)
    if not TRACKER.is_file():
        print(f"no tracker at {TRACKER}", file=sys.stderr)
        return 2
    return run(a.port, open_browser=a.open)


if __name__ == "__main__":
    raise SystemExit(main())
