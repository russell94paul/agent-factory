"""Closing a lane — the six manual steps nobody was doing.

On 2026-08-22 three lanes finished and NOTHING happened. The claim stayed held for four hours
(blocking relaunch), the branch stayed unpushed, nothing merged, nothing said so, and the board
could not tell a finished lane from a stalled one — both read as "N commits ahead, clean". Every
one of those steps was done by hand, after someone noticed.

`finish()` does the five that are safe to automate and refuses the sixth. **It does not merge.**
A merge is a judgement about whether the work is right, and this module only knows whether the
work is *complete*. Those are different questions and only one of them is mechanical.

⚠ It ASSERTS before it releases. A lane that "finished" with a dirty tree, or with no commits, or
with nothing written to the ledger, has not finished — it has stopped, and releasing its claim
would advertise a lie to the next session. Every refusal names what to do about it.
"""
from __future__ import annotations

import subprocess
from typing import List, Optional

from . import bus as _bus
from . import claims as _claims
from . import findings as _findings
from . import runs as _runs
from . import sessions as _sessions
from . import worktrees as _wt


class NotFinished(Exception):
    """The lane is not in a finishable state. The message says what is missing."""


def _git(lane: str, *args: str) -> tuple:
    p = subprocess.run(["git", "-C", str(_wt.path_for(lane)), *args],
                       capture_output=True, text=True, timeout=120)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def _integration(lane: str) -> str:
    """The branch this lane should be compared against: whatever the PRIMARY worktree has checked
    out. Not hardcoded — `feat/readiness-generator` today is not `main` tomorrow — and not
    `origin/HEAD`, which would count the integration branch's own commits as the lane's.
    """
    rc, out = _git(lane, "worktree", "list", "--porcelain")
    if rc == 0:
        block = out.split(chr(10) * 2)[0]   # the primary worktree is listed first
        for line in block.splitlines():
            if line.startswith("branch "):
                return line.split("/", 2)[-1] if line.count("/") >= 2 else line[len("branch "):]
    return "HEAD~1"                                   # last resort: at least one commit exists


def checks(lane: str, base: str | None = None) -> List[str]:
    """Everything that would refuse this finish. Empty list means finishable.

    Separated from finish() so the tracker can show WHY a lane is not closable without
    attempting it — a button that can only fail teaches nothing.
    """
    problems: List[str] = []
    path = _wt.path_for(lane)
    if not path.is_dir():
        return [f"no worktree at {path} — nothing to finish"]
    # A claim released out from under a LIVE session is how a second agent gets into the same
    # worktree. On 2026-08-22 exactly that happened: finish() released control-plane while its
    # session was still alive, a relaunch saw a free lane, and three sessions ended up sharing one
    # worktree and one branch. Nothing collided, which was luck rather than a control.
    livesess = _sessions.live(lane)
    if livesess:
        problems.append(
            "the lane still has {} live session(s) ({}) — close them before finishing, or a "
            "relaunch will start a second agent in this worktree".format(
                len(livesess), ", ".join(str(s["pid"]) + ":" + str(s["status"]) for s in livesess)))
    if _wt.is_dirty(lane):
        problems.append("the worktree is dirty — commit or discard before finishing; "
                        "uncommitted work does not survive the worktree being removed")
    # Commits unique to THIS lane — reachable from its HEAD and from no other branch. The
    # obvious `base..HEAD` was wrong and defaulted to `HEAD..HEAD`, which is always 0: it
    # reported three lanes with 4-5 commits each as having produced nothing. A check that
    # cannot distinguish "did nothing" from "did everything" is worse than no check.
    rc, out = _git(lane, "rev-list", "--count", f"{_integration(lane) if base is None else base}..HEAD")
    n = out.strip()
    if rc != 0:
        problems.append(f"cannot count commits: {out.strip()[:120]}")
    elif n.isdigit() and int(n) == 0:
        problems.append("no commits on this lane — a lane that finished without committing "
                        "produced nothing that outlives its terminal")
    # The ledger entry is the lane's own brief: append a finding, or NOTHING TO REPORT.
    # Silence has to mean checked, not unlooked-at.
    entries = [f for f in _findings.load() if lane in (f.affects or "").lower()]
    if not entries and _findings.nothing_to_report() == 0:
        problems.append("no findings entry and no NOTHING TO REPORT — write one, so silence "
                        "means checked rather than nobody looked")
    return problems


def finish(lane: str, push: bool = True, force: bool = False,
           remote: str = "origin", base: str | None = None) -> dict:
    """Assert, push, release, announce. Never merges."""
    done: List[str] = []
    branch = f"{_wt.BRANCH_PREFIX}{lane}"
    problems = checks(lane, base=base)
    if problems and not force:
        # Recorded BEFORE the raise. A refusal is the row you most want a week later — "why did
        # control-plane never close?" — and it is exactly the event that left no trace: the
        # exception propagates, the operator fixes it or does not, and nothing remembers either
        # way. Recording it costs one append and makes the UI able to answer the question.
        _record(lane, _runs.REFUSED, "refused to finish", problems, branch, base)
        raise NotFinished("; ".join(problems))
    if problems:
        done.append(f"forced past {len(problems)} check(s): {'; '.join(problems)}")

    if push:
        rc, out = _git(lane, "push", "-u", remote, branch)
        if rc != 0:
            # A failed push must NOT release the claim. Losing the branch is the thing this
            # whole step exists to prevent, so stop here and leave the lane claimed.
            msg = f"push failed, claim NOT released: {out.strip()[:200]}"
            _record(lane, _runs.REFUSED, "push failed", [msg], branch, base)
            raise NotFinished(msg)
        done.append(f"pushed {branch} to {remote}")

    try:
        _bus.post(lane, "finished",
                  f"{lane} finished. Branch {branch}"
                  + (" pushed." if push else " NOT pushed.")
                  + " Not merged — a human decides that.")
        done.append("announced on the bus")
    except _bus.BusError as exc:                                   # noqa: BLE001
        done.append(f"bus post skipped ({exc})")

    if _claims.release(lane):
        done.append("released the claim")
    else:
        done.append("no claim was held")

    # Last, and deliberately: the claim is gone by now, so this append is the ONLY thing that
    # will still say this lane finished. Recorded after the release rather than before so a run
    # that died mid-close is not remembered as a clean finish.
    _record(lane, _runs.FINISHED, "; ".join(done), [], branch, base)
    return {"lane": lane, "did": done, "merged": False}


def _record(lane: str, outcome: str, detail: str, problems: List[str], branch: str,
            base: str | None) -> None:
    """Append to the run ledger, and never let the ledger break a close.

    A failure to *record* a finish must not turn a finished lane into an exception — the work is
    pushed and the claim released by then, and raising here would report success as failure. It
    is a record, not a control.
    """
    try:
        rc, out = _git(lane, "rev-list", "--count",
                       f"{_integration(lane) if base is None else base}..HEAD")
        n = out.strip()
        commits = int(n) if rc == 0 and n.isdigit() else None
        _runs.record(lane, outcome, detail=detail, problems=problems, branch=branch,
                     commits=commits, cwd=_wt.path_for(lane))
    except Exception:                                              # noqa: BLE001
        pass
