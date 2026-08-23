"""The task board — generated from the gates, not maintained beside them.

    python -m factory.board

**There is no task list in this file.** An earlier version had one: twenty-five hand-typed tasks
whose *status* was derived from the gates while the *list itself* was not. Add a gate and no task
appeared; delete one and an orphan lingered. That is a hand-maintained board wearing a computed
status, which is the same defect as a checkbox grid with nicer wiring.

So: **every gate that is not passing is a task.** The title, the reason and the evidence come from
the gate itself, so the board cannot describe work that nobody is measuring, and it cannot omit
work that somebody is. Adding a gate adds a task. Making a gate pass removes one. Drift is not
prevented here — it is structurally impossible.

The one thing that IS authored is `DEPENDS`, below, because "this must happen before that" is real
design knowledge and no probe can infer it. It is validated on import: every id must name a real
gate, so a renamed or deleted gate breaks the build rather than leaving a dangling edge.

    gate not passing            ->  a task
    gate passing                ->  done, and it disappears from the work
    every dependency satisfied  ->  READY, and everything READY is parallelisable by definition
"""
from __future__ import annotations

from typing import Dict, List, Set, Tuple

from .readiness import GATES, PASS, PHASES, measure

DONE, READY, BLOCKED = "DONE", "READY", "BLOCKED"

# ---------------------------------------------------------------------------------------------
# The only authored knowledge in this module: what must precede what. Keyed by gate id.
# Every entry is validated against the live gate list at import time.
DEPENDS: Dict[str, List[str]] = {
    # A ceiling read from a figure blind to failures is not a ceiling.
    "ceiling": ["cost"],
    # You cannot drill a gate that has no predicate to refuse with.
    "refuses": ["checks"],
    # Reconciling recorded status against the log presumes the log is what the verdict reads.
    "truthful": ["from-history"],
    # An assertion cannot measure a live run until the evaluator is a principal of its own.
    "certified": ["isolated"],
    # `tenancy` as it is actually implemented has NO dependency: reading allowed_tenants out of the
    # blueprint needs no live instrument. The edge here was written for a different question —
    # "is the declared list still CORRECT?" — which does need one, and which no gate asks.
    # Removed 2026-08-23. A PASS pointing at a NOT_RUN dependency is how the roadmap came to
    # sequence work that could already have started.
    #
    # ⚠ The missing gate is real, not a tidy-up: `tenancy-verified`, depending on `certified`,
    # confirming the six ids against a live pull. Its absence is why nothing on the board notices
    # that the declared list was last checked on 2026-05-29, ~12 weeks before the blueprint that
    # carries it. Adding it changes len(GATES) and the pinned artifact
    # tests/test_tracker_is_current.py asserts against, so it is its own job.
    # The corpus is scored by the contract; isolate the grader before growing what it grades.
    "breadth": ["isolated"],
    # A run only "finishes" meaningfully once it is bounded and its verdict is honest.
    "finishes": ["cap", "reaper", "from-history"],
    # Succeeding more often than failing is downstream of the loop being repaired at all.
    "succeeds": ["cap", "reaper", "general"],
    # Grain is a question about the table the contract asserts against.
    "grain": [],
    # Recording a render pass needs nothing but someone opening the page.
    "rendered": [],
}

# Cosmetic grouping only — the phases already come from readiness.py.
TRACK_ORDER = list(PHASES.keys())


def _validate() -> None:
    ids = {g.id for g in GATES}
    bad = []
    for k, vs in DEPENDS.items():
        if k not in ids:
            bad.append(f"DEPENDS key {k!r} is not a gate")
        for v in vs:
            if v not in ids:
                bad.append(f"DEPENDS[{k!r}] names {v!r}, which is not a gate")
    if bad:
        raise ValueError(
            "the dependency map has gone stale:\n  " + "\n  ".join(bad) +
            "\nEvery edge must name a live gate. Fix the map or restore the gate.")


_validate()


def board() -> List[Tuple[object, str, str, List[str]]]:
    """(gate, result, status, unmet) for every gate, dependency-resolved."""
    results = measure()
    verdict = {g.id: r.verdict for g, r in results}
    done: Set[str] = {gid for gid, v in verdict.items() if v == PASS}

    out = []
    for g, r in results:
        deps = DEPENDS.get(g.id, [])
        unmet = [d for d in deps if d not in done]
        if g.id in done:
            st = DONE
        elif unmet:
            st = BLOCKED
        else:
            st = READY
        out.append((g, r, st, unmet))
    return out


def critical_path() -> List[str]:
    """Longest dependency chain still unmet — the thing that cannot be parallelised away."""
    depth: Dict[str, int] = {}

    def d(gid: str, seen: Set[str]) -> int:
        if gid in depth:
            return depth[gid]
        if gid in seen:                      # a cycle would be an authoring error, not a state
            return 0
        deps = DEPENDS.get(gid, [])
        depth[gid] = 1 + max((d(x, seen | {gid}) for x in deps), default=0)
        return depth[gid]

    for g in GATES:
        d(g.id, set())
    deepest = max(depth, key=lambda k: depth[k])
    chain, cur = [deepest], deepest
    while DEPENDS.get(cur):
        cur = max(DEPENDS[cur], key=lambda k: depth.get(k, 0))
        chain.append(cur)
    return list(reversed(chain))


def main() -> int:
    rows = board()
    n_done = sum(1 for _, _, st, _ in rows if st == DONE)
    ready = [(g, r) for g, r, st, _ in rows if st == READY]

    print(f"\nTask board — generated from {len(rows)} gates, nothing typed by hand")
    print(f"{n_done} done, {len(ready)} can start now, "
          f"{sum(1 for _, _, st, _ in rows if st == BLOCKED)} blocked\n")

    mark = {DONE: "[x]", READY: "[ ]", BLOCKED: "[~]"}
    for phase in TRACK_ORDER:
        group = [(g, r, st, u) for g, r, st, u in rows if g.phase == phase]
        if not group:
            continue
        d = sum(1 for _, _, st, _ in group if st == DONE)
        print(f"  {PHASES[phase]}  [{d}/{len(group)}]")
        for g, r, st, unmet in group:
            dep = f"   waits on: {', '.join(unmet)}" if unmet else ""
            print(f"    {mark[st]} {g.question}{dep}")
            if st != DONE:
                print(f"        {r.headline}")
        print()

    if ready:
        print(f"PARALLELISABLE NOW — {len(ready)} with no unmet dependency:")
        for g, _ in ready:
            print(f"    · [{g.phase}] {g.question}")

    cp = critical_path()
    print(f"\nLongest dependency chain: {' -> '.join(cp)}")
    print("Everything else can be done alongside it.")
    print("\n[x] gate passes  [ ] ready  [~] blocked by a dependency")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
