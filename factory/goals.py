"""How close are we to the three things we are actually trying to build?

The thirty readiness gates answer *"can an agent team run a connector migration unattended"*. That
is one question, and the operator has three: **a configuration that identifies an agent**, **an
optimizer that can run in a sandbox**, and **a first agent team that completes a run.** Those are
not phases — they cut across phases — so this module groups gates by goal.

⚠ **The grouping is the only authored thing here and it is a judgement.** Every number below is
measured, but *which gates constitute a goal* is a decision someone made, and a progress bar over
the wrong set is a confident-looking lie. So the map is small, it is validated on import against
the live gate list, and the UI prints it in full rather than hiding it behind a percentage. Argue
with the map, not with the arithmetic.

**A goal with no measurable gates reports NOT-MEASURED, not 0%.** Zero and "nothing has looked" are
different claims, and only one of them is about the work.
"""
from __future__ import annotations

from typing import Dict, List

from .readiness import GATES, NOT_RUN, PASS, UNMEASURABLE, measure

#: goal -> (one-line intent, gate ids). Grouped from what each gate ASKS, not from its phase.
GOALS: Dict[str, tuple] = {
    "First agent team completes a run": (
        "A team that starts, stays bounded, and finishes without a human. These are the gates the "
        "353-restart loop in the migration audits fails: `cap` is the control that stops it.",
        ["finishes", "succeeds", "bounded", "cap", "reaper", "concurrency", "ceiling"],
    ),
    "Optimizer can run in a sandbox": (
        "An evaluator the agent cannot impersonate, a blast radius that can be certified, and a "
        "corpus wide enough to calibrate against. Isolation is the load-bearing one.",
        ["isolated", "tenancy", "certified", "breadth", "general"],
    ),
    "Configuration identifies the agent": (
        "Being able to say which agent, on which config, produced a given artefact — and prove the "
        "grader was not the thing being graded.",
        ["version", "attributable", "chain", "corpus", "durable"],
    ),
}


def _validate() -> None:
    """Every goal must name live gates. A goal pointing at a deleted gate silently shrinks."""
    ids = {g.id for g in GATES}
    bad = []
    for goal, (_, gate_ids) in GOALS.items():
        if not gate_ids:
            bad.append(f"goal {goal!r} names no gates")
        for gid in gate_ids:
            if gid not in ids:
                bad.append(f"goal {goal!r} names {gid!r}, which is not a gate")
    if bad:
        raise ValueError(
            "the goal map has gone stale:\n  " + "\n  ".join(bad) +
            "\nEvery goal must name live gates. Fix the map or restore the gate.")


_validate()


def progress() -> List[dict]:
    """Per goal: passing, total, and the gates behind the number — all from one measure() call."""
    verdict = {g.id: r.verdict for g, r in measure()}
    out = []
    for goal, (why, gate_ids) in GOALS.items():
        gates = [{"id": gid, "verdict": verdict.get(gid, NOT_RUN)} for gid in gate_ids]
        passing = sum(1 for g in gates if g["verdict"] == PASS)
        # A goal every one of whose gates is UNMEASURABLE or NOT_RUN has not been measured at all.
        # Reporting that as 0% would be a claim about the work rather than about the instrument.
        looked = sum(1 for g in gates if g["verdict"] not in (UNMEASURABLE, NOT_RUN))
        out.append({
            "goal": goal, "why": why, "gates": gates,
            "passing": passing, "total": len(gates),
            "basis": "MEASURED" if looked else "NOT-MEASURED",
            "blocking": [g["id"] for g in gates if g["verdict"] != PASS],
        })
    return out


def coverage() -> dict:
    """How much of the gate set the three goals actually span — the honest denominator check."""
    covered = {gid for _, ids in GOALS.values() for gid in ids}
    allids = {g.id for g in GATES}
    return {"covered": len(covered), "total": len(allids),
            "uncovered": sorted(allids - covered)}
