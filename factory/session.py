"""What should this session do, which skill does it, and where may it write?

⭐ **Every fact in this brief already existed. None of it reached the operator.** The complaint
that produced this module was *"I don't know what the phases are, what tickets are in them, what
the dependencies are, and I keep hitting branch conflicts between worktrees"* — and all four were
computed, in this package, wired to nothing:

    phases            roadmap.waves()          DONE / READY / BLOCKED, derived from gate verdicts
    dependencies      lanes.waits_on()         which lane waits on which gate
    parallelism       lanes.conflicts()        which lanes touch the same files
    priority          lanes.unblocks()         how many others a lane releases
    who holds what    claims.active()          O_EXCL, liveness against the process table
    which skill       registry.for_shape()     (shape x layer) -> council or command

So this module is a **join, not a new mechanism**, in the same spirit as `registry.py` — which
joins the councils to the factory and, until this file, had zero importers outside its own tests.
It is the estate's signature defect, and wiring is the estate's highest-yield move.

## ⛔ The one thing that genuinely did not exist

`registry` routes on a **shape** — *what do you not yet know?* — and **nothing carried one.**
`Lane` has `id/title/why/repo/touches/size/gates/prompt/needs_paul/model`; `Preset` has
`type_id/layers/verifier/...`. Neither declares a shape, so the router could not be reached from
the work. `LANE_SHAPE` below is that missing edge, and it is **AUTHORED, not derived** — declared
here so it can be argued with rather than improvised per session, exactly as `lanes.py` and
`presets.py` declare theirs, and validated on import for the same reason.

## What this deliberately does NOT do

It does not dispatch, and it does not decide. It prints a brief and — only when asked — takes a
claim and makes a worktree. The agent is still launched by a human running the named skill. That
boundary is the same one `launch.py` states about itself: *"it is not permission, and it never
dispatches anything."*
"""
from __future__ import annotations

import argparse
import os
from typing import Dict, List, Optional

from . import board as _board
from . import claims as _claims
from . import findings as _findings
from . import lanes as _lanes
from . import registry as _registry
from . import roadmap as _roadmap
from . import worktrees as _worktrees

#: lane id -> the shape of its unknown, which is what picks a workflow.
#:
#: ⚠ **BASIS: AUTHORED.** This is the judgement `registry.py` says the routing is — *"what is
#: MEASURED is narrower and stated per row"*. A lane's gates say what it must prove; they do not
#: say what kind of not-knowing the work is. Only a person can say that, so a person says it here
#: once, in the open, instead of a session guessing it each time.
LANE_SHAPE: Dict[str, str] = {
    "control-plane": "build",      # the execution path exists and must be made to work
    "certify":       "measure",    # how much of the corpus can the contract actually see
    "judgement":     "review",     # are the gates themselves sound
    "artifact":      "design",     # what should the published surface BE
    "grain":         "decide",     # settle an open question about the landing table
}


def _validate() -> None:
    """Fail at import if the authored map has drifted from the lanes or the shapes.

    The pattern is `goals.py`'s, and the reason is the same: a hand-written map that names
    something which no longer exists is worse than no map, because it still looks authoritative.
    """
    known = {l.id for l in _lanes.LANES}
    named = set(LANE_SHAPE)
    missing = sorted(known - named)
    ghosts = sorted(named - known)
    bad = sorted(s for s in LANE_SHAPE.values() if s not in _registry.SHAPES)
    if missing or ghosts or bad:
        raise ImportError(
            f"LANE_SHAPE has drifted: unmapped lanes {missing}, lanes that no longer exist "
            f"{ghosts}, shapes not in registry.SHAPES {bad}")


_validate()


def _passing() -> set:
    """Gate ids currently passing, from the board. The input every lanes/ function wants."""
    return {g.id for g, _r, st, _u in _board.board() if st == _board.DONE}


def workflow_for(lane_id: str) -> Optional[_registry.Workflow]:
    """The council or command that does this lane's kind of work, or None."""
    shape = LANE_SHAPE.get(lane_id)
    if not shape:
        return None
    lane = next((l for l in _lanes.LANES if l.id == lane_id), None)
    hits = _registry.for_shape(shape, None)
    if not hits:
        return None

    # ⛔ Prefer the LAYER-AGNOSTIC workflow, not the layer-specific one. The first version of this
    # did the opposite and routed `control-plane` — agent-factory's own execution path — to
    # `gep-feature`, which is a GEP warehouse/PBI stage machine. A lane carries a `repo` and a
    # `touches` set but **no layer**, so there is nothing to match a layer-specific workflow
    # against, and picking one anyway is a guess wearing a routing decision's clothes.
    #
    # The councils are layer-agnostic by design — `inquest`, `conclave`, `prospect` are methods
    # for a kind of not-knowing, not for a technology. A layer-specific command only wins once
    # something declares the layer, which nothing does yet.
    general = [w for w in hits if not w.layers and w.id != "army"]
    if general:
        return general[0]

    # ⛔ REFUSE RATHER THAN GUESS. If every workflow for this shape declares a layer and the lane
    # declares none, there is no route — only a resemblance. Measured 2026-08-31: `build` has
    # exactly two workflows, `gep-feature` (warehouse/semantic_model/app) and `prefect-connector`
    # (connector), both client-layer machines. So **agent-factory's own build work has no
    # workflow**, and saying `gep-feature` would have sent the control-plane lane down a GEP
    # warehouse stage machine.
    #
    # That gap is a finding, not a routing problem to paper over. `army` remains the honest
    # fallback and the caller names it as one; this returns None so the brief can say WHY.
    return None


def brief(passing: Optional[set] = None) -> Dict:
    """Everything a session needs to choose its work, derived on every call.

    ⭐ **Derived, never stored.** Last session's run row, findings and gate verdicts change what
    this returns without anyone editing prose. A stored plan is the thing the boot prompts kept
    becoming — correct when written, confidently wrong a day later.
    """
    passing = _passing() if passing is None else passing
    waits = _lanes.waits_on(passing)
    clash = _lanes.conflicts()
    held = _claims.active()
    runnable = _lanes.runnable_now(passing)

    rows = []
    for lane in _lanes.LANES:
        w = workflow_for(lane.id)
        holder = held.get(lane.id)
        blocked_by_claim = sorted(
            other for other in clash.get(lane.id, []) if other in held)
        rows.append({
            "lane": lane.id,
            "title": lane.title,
            "shape": LANE_SHAPE.get(lane.id),
            "repo": lane.repo,
            "needs_paul": bool(getattr(lane, "needs_paul", None)),
            "waits_on": list(waits.get(lane.id) or []),
            "conflicts_with": list(clash.get(lane.id) or []),
            "held_by": getattr(holder, "who", None) if holder else None,
            "blocked_by_a_live_claim": blocked_by_claim,
            "workflow": w.id if w else None,
            "workflow_kind": w.kind if w else None,
            "workflow_state": w.state if w else None,
            "runnable": (lane.id in runnable
                         and lane.id not in held
                         and not blocked_by_claim),
        })

    return {
        "waves": [{"key": b["key"], "gates": [g["id"] for g in b["gates"]]}
                  for b in _roadmap.waves()],
        "critical_path": list(_roadmap.critical_path()),
        "lanes": rows,
        "design_debt": [f.id for f in _findings.design_debt()],
        "unproven_workflows": [w.id for w in _registry.unproven()],
    }


def render(b: Optional[Dict] = None) -> str:
    """The brief as one screen. Scannable before it is complete."""
    b = brief() if b is None else b
    out: List[str] = ["SESSION BRIEF", "=" * 72, ""]

    counts = " · ".join(f"{w['key']} {len(w['gates'])}" for w in b["waves"])
    out += [f"BOARD        {counts}",
            f"CRITICAL     {' -> '.join(b['critical_path']) or '(none)'}",
            f"DESIGN DEBT  {', '.join(b['design_debt']) or 'none open'}", ""]

    ready = [r for r in b["lanes"] if r["runnable"]]
    out += ["RUNNABLE NOW" if ready else "RUNNABLE NOW   (nothing — see BLOCKED)", ""]
    for r in ready:
        star = " ⚠ needs Paul" if r["needs_paul"] else ""
        state = f" [{r['workflow_state']}]" if r["workflow_state"] else ""
        wf = f"{r['workflow']}{state}" if r["workflow"] else (
            "⛔ NO WORKFLOW — every workflow for this shape declares a layer "
            "and this lane declares none. `army` is the fallback, not a route.")
        out += [f"  {r['lane']:<15} {r['shape']:<9} -> {wf}{star}",
                f"  {'':<15} {r['title'][:60]}"]
        if r["conflicts_with"]:
            out += [f"  {'':<15} cannot run beside: {', '.join(r['conflicts_with'])}"]
        out += [""]

    blocked = [r for r in b["lanes"] if not r["runnable"]]
    if blocked:
        out += ["BLOCKED", ""]
        for r in blocked:
            why = []
            if r["held_by"]:
                why.append(f"claimed by {r['held_by']}")
            if r["blocked_by_a_live_claim"]:
                why.append(f"conflicts with live {', '.join(r['blocked_by_a_live_claim'])}")
            if r["waits_on"]:
                why.append(f"waits on {', '.join(r['waits_on'][:4])}")
            out += [f"  {r['lane']:<15} {'; '.join(why) or 'not runnable'}"]
        out += [""]

    if b["unproven_workflows"]:
        out += [f"⚠ workflows never run on real work: {', '.join(b['unproven_workflows'])}",
                "  Running one is how it stops being unproven.", ""]

    out += ["Take one with:  python -m factory.session --start <lane>",
            "  which claims the lane, makes its worktree, and prints the skill to invoke.",
            "Nothing here dispatches an agent."]
    return "\n".join(out)


def start(lane_id: str, who: str = "") -> Dict:
    """Claim the lane, make its worktree, and return what to run.

    ⛔ **This is where the branch conflict is actually solved.** A session does not name its own
    branch: `claims.claim` takes an `O_EXCL` lock and `worktrees.ensure` derives the path and the
    `lane/` branch from the lane id. Two sessions cannot be handed the same lane, because the
    second one's claim fails — and a lane that CONFLICTS with a live claim is refused before the
    lock is even attempted, because touching the same files is the collision the lock cannot see.
    """
    lane = next((l for l in _lanes.LANES if l.id == lane_id), None)
    if lane is None:
        raise SystemExit(f"no such lane: {lane_id!r}. Known: "
                         f"{', '.join(sorted(l.id for l in _lanes.LANES))}")

    held = _claims.active()
    clashing = sorted(o for o in _lanes.conflicts().get(lane_id, []) if o in held)
    if clashing:
        raise SystemExit(
            f"{lane_id} touches the same files as {', '.join(clashing)}, which "
            f"{'is' if len(clashing) == 1 else 'are'} live right now. Running both is the "
            f"2026-08-23 hazard. Wait, or take one of: "
            f"{', '.join(r['lane'] for r in brief()['lanes'] if r['runnable'])}")

    c = _claims.claim(lane_id, who=who or os.environ.get("USERNAME", "session"),
                      note=lane.title[:120])
    path, note = _worktrees.ensure(lane_id)
    wf = workflow_for(lane_id)
    return {"lane": lane_id, "claim": c, "worktree": str(path), "worktree_note": note,
            "workflow": wf.id if wf else None, "kind": wf.kind if wf else None,
            "shape": LANE_SHAPE.get(lane_id)}


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(prog="factory.session")
    ap.add_argument("--start", metavar="LANE", help="claim a lane and make its worktree")
    ap.add_argument("--release", metavar="LANE", help="release a lane's claim")
    ap.add_argument("--who", default="", help="who is taking it")
    args = ap.parse_args(argv)

    if args.release:
        ok = _claims.release(args.release)
        print(f"{'released' if ok else 'no claim held for'} {args.release}")
        return 0

    if args.start:
        r = start(args.start, who=args.who)
        print(f"lane      {r['lane']}  ({r['shape']})")
        print(f"worktree  {r['worktree']}")
        print(f"          {r['worktree_note']}")
        print(f"workflow  {r['workflow']} ({r['kind']})" if r["workflow"]
              else "workflow  (none routed for this shape)")
        print()
        print(f"Now run the {r['workflow']} workflow from that worktree.")
        print(f"Release it when done:  python -m factory.session --release {r['lane']}")
        return 0

    print(render())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
