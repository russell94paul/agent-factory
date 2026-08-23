"""What one agent team actually has to do, in the order it has to do it.

The Lanes tab shows five lanes and thirty gates. An operator working toward **one team** wants a
different thing: *what are my steps, and which one is next.* That is not a subset of the board — it
is a different query over it, and getting it wrong is easy in two specific ways.

⛔ **A team's declared gate set is NOT self-contained, and a membership filter is therefore wrong.**
Measured 2026-08-23, `Data Pipeline Orchestrator` declares seven gates and needs **ten**:

    declared      cap  reaper  bounded  finishes  succeeds  concurrency  ceiling
    also required from-history (<- finishes)   general (<- succeeds)   cost (<- ceiling)

Show only the declared seven and you hand somebody a sequence that cannot be completed: they reach
`finishes` and are blocked by a step the filter hid from them. So the closure is taken over
`board.DEPENDS`, and a step pulled in that way is **marked as such** rather than quietly mixed in —
the operator should be able to see that three of their ten steps belong to somebody else's team.

⚠ **A step can have no lane.** `finishes` and `succeeds` are in the pipeline team's declared set and
**no lane claims either.** That is not an oversight to paper over: those two are UNMEASURABLE
because nothing has run, and no amount of editing code moves them. They need a supervised run. A
sequence that renders them as ordinary work items would send somebody looking for a file to change.
So `lane` is `None` and the caller is expected to say so out loud.

⭐ **UNGATED is not zero steps.** A team with no contract has nothing to sequence, and rendering it
as an empty list reads as *"nothing to do"* when the truth is *"nothing can be measured yet."* Same
distinction `launch.py` draws and the board draws with `NOT_RUN`.
"""
from __future__ import annotations

from typing import Dict, List, Optional

from .board import BLOCKED, DEPENDS, DONE, READY, board
from .lanes import LANES
from .roadmap import TEAMS

UNGATED = "UNGATED"


def teams() -> List[str]:
    return list(TEAMS)


def _owner() -> Dict[str, str]:
    """gate id -> the lane that claims it. Absent means no lane does."""
    return {g: l.id for l in LANES for g in l.gates}


def closure(declared: List[str]) -> Dict[str, bool]:
    """gate id -> was it DECLARED by the team (True) or pulled in as a prerequisite (False).

    Transitive over `board.DEPENDS`. A prerequisite outside the team's own list is still a step the
    team cannot finish without, and hiding it is how a sequence becomes uncompletable.
    """
    out = {g: True for g in declared}
    stack = list(declared)
    while stack:
        for dep in DEPENDS.get(stack.pop(), []):
            if dep not in out:
                out[dep] = False
                stack.append(dep)
    return out


def _layers(ids) -> List[List[str]]:
    """Topological layers: everything in layer N depends only on layers before it.

    Layers rather than a flat list because steps within one layer are genuinely parallel, and
    flattening them would imply an order the dependency graph does not actually require.
    """
    rem, out = set(ids), []
    while rem:
        layer = sorted(x for x in rem if not (set(DEPENDS.get(x, ())) & rem))
        if not layer:
            # A cycle. Emit the remainder as one layer rather than looping — the same rule
            # roadmap._validate holds: an edge that does not resolve must be loud, not silent.
            out.append(sorted(rem))
            break
        out.append(layer)
        rem -= set(layer)
    return out


def plan(team: str, rows: Optional[List[tuple]] = None) -> dict:
    """The ordered steps for one team.

    `rows` accepts an already-taken `board()` result so a page that has measured once does not
    measure again. Same-render reuse, the same promise `launch._verdicts` documents.
    """
    if team not in TEAMS:
        raise KeyError(f"no team {team!r}")
    spec = TEAMS[team]
    declared = list(spec.get("gates") or [])

    if not declared:
        return {"team": team, "state": UNGATED, "intent": spec.get("intent", ""),
                "note": spec.get("unblock") or
                        "no contract exists, so there is nothing to gate and nothing to sequence",
                "steps": [], "lanes": [], "declared": 0, "total": 0,
                "done": 0, "ready": 0, "blocked": 0, "unowned": []}

    rows = board() if rows is None else rows
    status = {g.id: st for g, _r, st, _u in rows}
    quest = {g.id: g.question for g, _r, st, _u in rows}
    head = {g.id: _r.headline for g, _r, st, _u in rows}
    owner = _owner()

    inset = closure(declared)
    steps = []
    for n, layer in enumerate(_layers(inset), 1):
        items = []
        for gid in sorted(layer, key=lambda x: (owner.get(x) or "~", x)):
            items.append({
                "gate": gid,
                "question": quest.get(gid, ""),
                "headline": head.get(gid, ""),
                "status": status.get(gid, "?"),
                "lane": owner.get(gid),
                "declared": inset[gid],
            })
        steps.append({"n": n, "items": items})

    flat = [i for s in steps for i in s["items"]]
    lanes_in_order, seen = [], set()
    for i in flat:
        if i["lane"] and i["lane"] not in seen:
            seen.add(i["lane"])
            lanes_in_order.append(i["lane"])

    return {
        "team": team,
        "state": spec.get("blocked_on") or "",
        "intent": spec.get("intent", ""),
        "note": "",
        "steps": steps,
        "lanes": lanes_in_order,
        "declared": len(declared),
        "total": len(inset),
        "done": sum(1 for i in flat if i["status"] == DONE),
        "ready": sum(1 for i in flat if i["status"] == READY),
        "blocked": sum(1 for i in flat if i["status"] == BLOCKED),
        # Steps nothing will do if somebody only works lanes. Named, not counted.
        "unowned": [i["gate"] for i in flat if not i["lane"]],
    }


def next_step(team: str, rows: Optional[List[tuple]] = None) -> Optional[dict]:
    """The first item that is READY, or None. What "which one do I do now" means."""
    p = plan(team, rows)
    for s in p["steps"]:
        for i in s["items"]:
            if i["status"] == READY:
                return i
    return None
