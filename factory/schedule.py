"""How fast is this going, and when will it be done?

Both questions are answerable, and the second one currently is not — for a reason worth reporting
rather than papering over with a date.

**Where the history comes from.** Nothing new is recorded. Every commit that touched
`docs/artifacts/agent-factory.html` carries a generated headline of the form `n of N gates pass`,
and git carries the commit date. So the project's own progress is already an append-only,
tamper-evident log; this module reads it. That makes every number here MEASURED rather than
remembered.

**⭐ The finding that governs everything else: the denominator moves.**

    18:26  1 of 13      21:25  3 of 23
    19:33  3 of 15      00:32  9 of 30

Gates passed went 1 → 9. The gate set went 13 → 30. **Remaining went 12 → 21.** More work was
discovered than completed, because measuring the system is what reveals what is broken in it.

That is not a failure — early in a programme it is the correct shape, and a gate set that stopped
growing while the system was still poorly understood would be the worrying version. But it makes
"when will it be done" unanswerable today: an ETA computed from pass-rate alone divides by a
denominator that is still growing, and every such estimate flatters. This module therefore refuses
to emit a completion date until scope velocity settles, and says which criterion it is waiting for.

**"Ahead or behind schedule" needs a target, and there isn't one.** No deadline has been stated
anywhere in the programme. Velocity against no target is a speed, not a verdict, so the schedule
report says NOT-SET rather than inventing a baseline to be ahead of. Pass a target with
``--target YYYY-MM-DD`` and it becomes measurable immediately.

    python -m factory.schedule
    python -m factory.schedule --target 2026-09-05
"""
from __future__ import annotations

import argparse
import datetime as _dt
import pathlib
import re
import subprocess
import sys
from dataclasses import dataclass
from typing import List, Optional

REPO = pathlib.Path(__file__).resolve().parent.parent
ARTIFACT_REL = "docs/artifacts/agent-factory.html"
HEADLINE = re.compile(r"(\d+) of (\d+) gates pass")

#: Scope is "settled" when the gate total has not moved across this much recent history. Stated
#: as a number rather than a feeling so the refusal to project has a criterion you can argue with.
SETTLED_HOURS = 24.0


class Unmeasurable(Exception):
    """Not enough history to say anything. Distinct from "the answer is zero"."""


@dataclass(frozen=True)
class Snapshot:
    when: _dt.datetime
    passed: int
    total: int
    sha: str

    @property
    def remaining(self) -> int:
        return self.total - self.passed


def _git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True,
                          encoding="utf-8", errors="replace").stdout


def snapshots() -> List[Snapshot]:
    """Every dated `n of N gates pass` in the artifact's git history, oldest first."""
    shas = [s for s in _git("log", "--format=%H", "--", ARTIFACT_REL).split() if s]
    out: List[Snapshot] = []
    for sha in reversed(shas):
        blob = _git("show", f"{sha}:{ARTIFACT_REL}")
        m = HEADLINE.search(blob)
        if not m:
            continue
        iso = _git("show", "-s", "--format=%cI", sha).strip()
        if not iso:
            continue
        out.append(Snapshot(_dt.datetime.fromisoformat(iso), int(m.group(1)), int(m.group(2)), sha[:7]))
    if len(out) < 2:
        raise Unmeasurable(
            f"only {len(out)} dated snapshot(s) of the headline in git — a velocity needs two "
            "points. Commit the regenerated artifact at least twice.")
    return out


@dataclass(frozen=True)
class Velocity:
    hours: float
    passed_delta: int
    total_delta: int
    first: Snapshot
    last: Snapshot

    @property
    def pass_per_hour(self) -> float:
        return self.passed_delta / self.hours if self.hours else 0.0

    @property
    def scope_per_hour(self) -> float:
        return self.total_delta / self.hours if self.hours else 0.0

    @property
    def net_remaining_per_hour(self) -> float:
        """Positive means the backlog is growing faster than it is being burned down."""
        return self.scope_per_hour - self.pass_per_hour

    @property
    def scope_settled(self) -> bool:
        """Has the gate total held still across the last SETTLED_HOURS of history?"""
        cutoff = self.last.when - _dt.timedelta(hours=SETTLED_HOURS)
        recent = [s for s in _ALL if s.when >= cutoff] or [self.last]
        return len({s.total for s in recent}) == 1 and len(recent) >= 2


_ALL: List[Snapshot] = []


def velocity() -> Velocity:
    global _ALL
    _ALL = snapshots()
    first, last = _ALL[0], _ALL[-1]
    hours = (last.when - first.when).total_seconds() / 3600.0
    if hours <= 0:
        raise Unmeasurable("all snapshots share one timestamp — no elapsed time to divide by")
    return Velocity(hours, last.passed - first.passed, last.total - first.total, first, last)


def projection(v: Velocity) -> dict:
    """A completion estimate, or a refusal that names its own criterion."""
    if not v.scope_settled:
        return {"projectable": False,
                "reason": (f"the gate set is still growing — {v.first.total} to {v.last.total} in "
                           f"{v.hours:.1f}h ({v.scope_per_hour:.2f} gates/h). An ETA divided by a "
                           f"moving denominator is a flattering guess, not a projection."),
                "criterion": f"the total holds still for {SETTLED_HOURS:.0f}h of committed history"}
    if v.pass_per_hour <= 0:
        return {"projectable": False, "reason": "no gates have flipped in the measured window",
                "criterion": "at least one gate passes"}
    hours_left = v.last.remaining / v.pass_per_hour
    return {"projectable": True, "hours_left": hours_left,
            "eta": v.last.when + _dt.timedelta(hours=hours_left),
            "basis": f"DERIVED from {v.passed_delta} gates in {v.hours:.1f}h, scope settled"}


def against_target(v: Velocity, target: Optional[_dt.date]) -> dict:
    """Ahead or behind — only answerable against a target somebody actually set."""
    if target is None:
        return {"status": "NOT-SET",
                "detail": ("no target date has been stated anywhere in the programme. Velocity "
                           "without a target is a speed, not a verdict — pass --target "
                           "YYYY-MM-DD and this becomes measurable.")}
    proj = projection(v)
    if not proj["projectable"]:
        return {"status": "NOT-PROJECTABLE", "detail": proj["reason"]}
    eta = proj["eta"].date()
    delta = (target - eta).days
    return {"status": "AHEAD" if delta > 0 else ("ON TRACK" if delta == 0 else "BEHIND"),
            "detail": f"projected {eta.isoformat()} against target {target.isoformat()} "
                      f"({abs(delta)} day(s) {'early' if delta > 0 else 'late'})"}


def report(target: Optional[_dt.date] = None) -> str:
    v = velocity()
    proj = projection(v)
    sched = against_target(v, target)
    lines = [
        "Build velocity — MEASURED from the artifact's own git history",
        "",
        f"  window        {v.first.when:%Y-%m-%d %H:%M} -> {v.last.when:%Y-%m-%d %H:%M}  "
        f"({v.hours:.1f}h, {len(_ALL)} snapshots)",
        f"  gates passed  {v.first.passed} -> {v.last.passed}   "
        f"(+{v.passed_delta}, {v.pass_per_hour:.2f}/h)",
        f"  gate set      {v.first.total} -> {v.last.total}   "
        f"(+{v.total_delta}, {v.scope_per_hour:.2f}/h)",
        f"  REMAINING     {v.first.remaining} -> {v.last.remaining}   "
        f"({'+' if v.net_remaining_per_hour >= 0 else ''}{v.net_remaining_per_hour:.2f}/h)",
        "",
    ]
    if v.net_remaining_per_hour > 0:
        lines += ["  ⭐ The backlog is growing faster than it is being burned down. That is the",
                  "     expected shape while the system is still being measured — measuring is what",
                  "     reveals what is broken — but it means completion is not yet projectable.", ""]
    lines.append("Completion")
    if proj["projectable"]:
        lines += [f"  ETA {proj['eta']:%Y-%m-%d %H:%M}  ({proj['hours_left']:.1f}h of work left)",
                  f"  basis: {proj['basis']}"]
    else:
        lines += ["  NOT-PROJECTABLE — and that is a measurement, not a shrug.",
                  f"  {proj['reason']}", f"  will project once: {proj['criterion']}"]
    lines += ["", "Schedule", f"  {sched['status']} — {sched['detail']}"]
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="factory.schedule")
    ap.add_argument("--target", default=None, help="target completion date, YYYY-MM-DD")
    args = ap.parse_args(argv)
    target = _dt.date.fromisoformat(args.target) if args.target else None
    try:
        print(report(target))
    except Unmeasurable as exc:
        print(f"UNMEASURABLE: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
