"""The roadmap — sequence, parallelism, and the two agent teams we are actually building toward.

    python -m factory.roadmap

**There is no task list in this file either.** `board.py` already refuses to keep one, for a reason
worth restating: a hand-typed list whose *status* is computed still drifts, because the list itself
is not. So the work here is `board.board()` — gate not passing is a task, and *everything READY is
parallelisable by definition*. This module adds only the three things a board cannot derive:

    TEAMS    the end states someone named out loud, which no probe can infer
    ACTIONS  the eighteen decisions the research produced, which live in prose nothing globs
    waves()  the READY/BLOCKED partition rendered as sequence, straight off board()

⚠ **The first two are AUTHORED and the UI says so on every row.** They are validated on import
against the live gate list, so a renamed gate breaks the build rather than leaving a dangling edge —
but validation only proves an edge *resolves*, never that the judgement behind it is right. Argue
with the map; the arithmetic is not the part that can be wrong.

⭐ **An action linked to a gate takes its status FROM the gate, always.** Only an action no gate can
see keeps an authored status, and those render as `AUTHORED` — deliberately weaker-looking than
`MEASURED`, because they are. That asymmetry is the whole design: it makes the hand-maintained part
visibly hand-maintained instead of letting it borrow the credibility of the measured part.
"""
from __future__ import annotations

from typing import Dict, List, Optional

from .readiness import GATES, PASS, measure
from .board import BLOCKED, DEPENDS, DONE, READY, board, critical_path
from .goals import GOALS

#: An action whose truth no gate can see. Rendered as AUTHORED, never as MEASURED.
AUTHORED, MEASURED = "AUTHORED", "MEASURED"
#: Authored lifecycle for an ungated decision.
DECIDED, SHIPPED, SUPERSEDED = "DECIDED", "SHIPPED", "SUPERSEDED"


class Action:
    """One of the eighteen decisions. `gate` is the only thing that can override `state`."""

    def __init__(self, id: str, text: str, source: str, state: str = DECIDED,
                 gate: Optional[str] = None, note: str = ""):
        self.id, self.text, self.source = id, text, source
        self.state, self.gate, self.note = state, gate, note


# ---------------------------------------------------------------------------------------------
# The eighteen decided actions, from SYNTHESIS.md §12.8, §13.7 and §14.7. Each was written the day
# its own pass landed and none knew what the others would say — which is exactly why R16 exists to
# attack the set, and why nothing here claims the set is consistent with itself.
ACTIONS: List[Action] = [
    # ---- §12.8 (R10/R11/R12) -----------------------------------------------------------------
    Action("a1", "Do not adopt switchboard on this evidence — retire the no-embedded-terminal "
                 "constraint in writing, or re-ask R12 with it stated.", "§12.8.1",
           state=SUPERSEDED,
           note="§14.7.6 settled the terminal as a decision, which closes the re-ask half."),
    Action("a2", "Build the four liveness states into factory/sessions.py.", "§12.8.2",
           state=SHIPPED,
           note="sessions.py reports four states incl. RUNNING-ORPHANED — the state a crashed "
                "window leaves behind, and the one switchboard structurally cannot see."),
    Action("a3", "Surface `needs` ourselves, and make it interrupt rather than badge.", "§12.8.3",
           state=DECIDED,
           note="sessions.blocked() returns them; the interrupt half is not built."),
    Action("a4", "Record the guardrail gap as a real absence — a pre-action layer, distinct from "
                 "the readiness gates.", "§12.8.4", state=DECIDED),
    Action("a5", "Skills over corpus — the wiki's leverage is procedure synthesis, not retrieval.",
           "§12.8.5", state=DECIDED),
    Action("a6", "Narrow R11's 'observability wholly ABSENT' — factory/runs.py already implements "
                 "the cost-paired-with-outcome direction.", "§12.8.6", state=SHIPPED),
    # ---- §13.7 (R8/R15) ----------------------------------------------------------------------
    Action("a7", "Make the existing tracker instant instead of adopting a desktop app.", "§13.7.1",
           state=SHIPPED,
           note="⚠ SHIPPED, but NOT by the mechanism this action prescribes, and the action's own "
                "number was wrong. It says 'thread the server and parallelise the probes, "
                "9.3 s -> ~1.2 s'. F77 had already established that parallelism floors at the "
                "slowest single task (9.39 -> 9.16 s), so the 1.2 s was never reachable. What "
                "actually worked, 2026-08-23: thread the server AND cache the suite gate against a "
                "content hash of tests/+factory/ — measured 27.3 s cold to 0.84 s warm. The stale "
                "figure survived into a decided action; that is the drift R16 is meant to catch."),
    Action("a8", "Containerise agent execution on one machine before any cloud step.", "§13.7.2",
           state=DECIDED, gate="isolated"),
    Action("a9", "Adopt the mandatory-clone rule — enforceable in code, no new discipline.",
           "§13.7.3", state=DECIDED),
    Action("a10", "Restate the unattended goal as a 30-45 minute unbroken run, in the readiness "
                  "set.", "§13.7.4", state=DECIDED, gate="finishes"),
    Action("a11", "Read switchboard's `open-terminal` handler and settle the attach contradiction.",
           "§13.7.5", state=SHIPPED,
           note="✅ SETTLED 2026-08-23. main.js @ 4c5a6da: activeSessions is an in-process Map "
                "(:101) and open-terminal (:1288) returns reattached only when it already holds "
                "the id; zero hits for any OS liveness probe. R12 right, R15 wrong — and "
                "re-verified against the raw file rather than taken on one citation. ⭐ The real "
                "finding is that switchboard has NO guard: it issues `claude --resume <id>` and "
                "delegates the check to a CLI it cannot see, so exited / running-elsewhere / "
                "refused all render identically. That is an absent liveness concept, not a bug — "
                "which is why our four states are a lead."),
    Action("a12", "Take R8's isolation argument; leave its scheduling and messaging "
                  "recommendations.", "§13.7.6", state=DECIDED),
    # ---- §14.7 (R13) -------------------------------------------------------------------------
    Action("a13", "Platform: a VS Code extension, not a desktop app.", "§14.7.1", state=DECIDED),
    Action("a14", "Build the notification channel first — three passes and one measurement agree.",
           "§14.7.2", state=DECIDED),
    Action("a15", "Stop surveying orchestration topologies — seven checked, none moves the cap.",
           "§14.7.3", state=SHIPPED),
    Action("a16", "Config hash: adopt the OTel GenAI field set.", "§14.7.4",
           state=DECIDED, gate="version"),
    Action("a17", "Discount R13's migration section — it guessed our surfaces.", "§14.7.5",
           state=SHIPPED),
    Action("a18", "Settle the terminal question as a decision and delete it from every prompt.",
           "§14.7.6", state=SHIPPED),
]


# ---------------------------------------------------------------------------------------------
#: The end states someone named out loud. NOT derivable from any probe — an agent team is a goal,
#: and goals live in people's heads until someone writes them down.
#:
#: ⚠ A team with no gates is reported UNGATED, never 0%. "Nothing is measuring this" and "this is
#: measured at zero" are different claims and only one of them is about the work.
TEAMS: Dict[str, dict] = {
    "Data Pipeline Orchestrator": {
        "intent": "The first team to run a connector migration end to end without a human. This "
                  "is the one the estate has evidence for: 948 of 1,001 recorded migration "
                  "failures are the unbounded-restart loop that `cap` exists to stop.",
        "gates": ["cap", "reaper", "bounded", "finishes", "succeeds", "concurrency", "ceiling"],
        "blocked_on": "cap",
    },
    "Power BI Data Model Designer": {
        "intent": "A team that produces Power BI model changes an operator can accept without "
                  "reading every line. Named alongside the pipeline team, and much further away.",
        "gates": [],
        "blocked_on": None,
        "unblock": "No contract exists for what its output must satisfy. Until one does, there is "
                   "nothing to gate and nothing to certify — so this team cannot have a "
                   "percentage, and a roadmap that gave it one would be inventing progress. "
                   "⚠ Microsoft's first-party agentic Power BI surface may define that contract "
                   "or may duplicate it; the doc is saved UNREAD and is MARKETED until exercised "
                   "against a real tenant.",
    },
}


def _validate() -> None:
    """Every authored edge must name a live gate. A stale one breaks the build, loudly."""
    ids = {g.id for g in GATES}
    bad = []
    for name, spec in TEAMS.items():
        for gid in spec["gates"]:
            if gid not in ids:
                bad.append(f"TEAMS[{name!r}] names gate {gid!r}, which does not exist")
        b = spec.get("blocked_on")
        if b and b not in ids:
            bad.append(f"TEAMS[{name!r}].blocked_on names {b!r}, which is not a gate")
    seen = set()
    for a in ACTIONS:
        if a.id in seen:
            bad.append(f"duplicate action id {a.id!r}")
        seen.add(a.id)
        if a.gate and a.gate not in ids:
            bad.append(f"ACTIONS[{a.id}] names gate {a.gate!r}, which does not exist")
    if len(ACTIONS) != 18:
        bad.append(f"ACTIONS holds {len(ACTIONS)}, but the record says eighteen decided actions. "
                   f"If the count really changed, change this check and say where.")
    if bad:
        raise ValueError("the roadmap map has gone stale:\n  " + "\n  ".join(bad) +
                         "\nFix the map or restore what it names.")


_validate()


def waves() -> List[dict]:
    """The board partitioned into what is done, what can start NOW, and what cannot.

    The middle group is the answer to "what can run in parallel" and it is not computed here — it
    is `board()`'s READY set, which is parallelisable by definition because READY means every
    dependency is already satisfied. Nothing else needs to be true for two READY gates to run at
    once.
    """
    rows = board()
    by = {DONE: [], READY: [], BLOCKED: []}
    for g, r, st, unmet in rows:
        by[st].append({"id": g.id, "phase": g.phase, "headline": r.headline,
                       "verdict": r.verdict, "unmet": unmet,
                       "unlocks": sorted(k for k, v in DEPENDS.items() if g.id in v)})
    return [
        {"key": DONE, "title": "Done", "gates": by[DONE],
         "why": "Passing. It is not work any more, and it disappears from the board by itself."},
        {"key": READY, "title": "Can start now — in parallel", "gates": by[READY],
         "why": "Every dependency already satisfied. These are parallelisable BY DEFINITION; "
                "there is no scheduling decision left to make about them."},
        {"key": BLOCKED, "title": "Blocked", "gates": by[BLOCKED],
         "why": "Waiting on a named gate. Each row says which — that is the whole content of "
                "'blocked', and a roadmap that only said 'later' would be hiding it."},
    ]


def chain() -> List[dict]:
    """The critical path, with each hop's live status — the sequence parallelism cannot remove."""
    st = {g.id: (r, s) for g, r, s, _ in board()}
    out = []
    for gid in critical_path():
        r, s = st.get(gid, (None, None))
        out.append({"id": gid, "status": s,
                    "headline": r.headline if r else "(no such gate)"})
    return out


def teams() -> List[dict]:
    """Per named team: measured progress where gates exist, UNGATED where they do not."""
    verdict = {g.id: r.verdict for g, r in measure()}
    st = {g.id: s for g, _, s, _ in board()}
    out = []
    for name, spec in TEAMS.items():
        gids = spec["gates"]
        gates = [{"id": g, "verdict": verdict.get(g), "status": st.get(g)} for g in gids]
        passing = sum(1 for g in gates if g["verdict"] == PASS)
        out.append({
            "team": name, "intent": spec["intent"], "gates": gates,
            "passing": passing, "total": len(gids),
            "basis": MEASURED if gids else "UNGATED",
            "blocked_on": spec.get("blocked_on"),
            "unblock": spec.get("unblock", ""),
            "ready_now": [g["id"] for g in gates if g["status"] == READY],
        })
    return out


def actions() -> List[dict]:
    """The eighteen, with a gate's verdict overriding the authored state wherever one exists."""
    verdict = {g.id: r.verdict for g, r in measure()}
    out = []
    for a in ACTIONS:
        if a.gate:
            v = verdict.get(a.gate)
            state, basis = (SHIPPED if v == PASS else DECIDED), MEASURED
        else:
            state, basis = a.state, AUTHORED
        out.append({"id": a.id, "text": a.text, "source": a.source, "state": state,
                    "basis": basis, "gate": a.gate, "note": a.note,
                    "verdict": verdict.get(a.gate) if a.gate else None})
    return out


def contradictions() -> List[dict]:
    """Gates that PASS while a dependency they declare is still unmet.

    ⭐ This is a computed contradiction, not an authored worry, and it is the most useful thing on
    the roadmap. `board()` assigns DONE from the verdict alone, so a gate can report PASS while the
    thing it was declared to depend on has not happened. Exactly one of two statements is then true
    and both are worth knowing:

        the edge is wrong    — we asserted a prerequisite that is not really one
        the pass is vacuous  — the gate is green over the defect it is named for

    The estate has already been bitten by the second: three gates once passed over an intact
    control-plane defect and the readiness count did not move. A check that would still pass with
    the function body deleted is not measuring the function — so a pass that does not need its own
    prerequisite deserves the same suspicion.
    """
    rows = board()
    verdict = {g.id: r.verdict for g, r, _, _ in rows}
    out = []
    for g, r, st, unmet in rows:
        if st == DONE and unmet:
            out.append({"id": g.id, "headline": r.headline, "unmet": unmet,
                        "unmet_verdicts": {u: verdict.get(u) for u in unmet}})
    return out


def unplaced() -> dict:
    """Gates in no goal and on no team — the honest denominator check for a roadmap.

    A roadmap implies completeness. Ours does not have it, so the page says which gates nothing on
    it accounts for rather than letting the reader assume the picture is whole.
    """
    placed = {gid for _, gate_ids in GOALS.values() for gid in gate_ids}
    placed |= {gid for spec in TEAMS.values() for gid in spec["gates"]}
    allids = {g.id for g in GATES}
    return {"placed": len(placed & allids), "total": len(allids),
            "unplaced": sorted(allids - placed)}


if __name__ == "__main__":
    for wv in waves():
        print(f"\n== {wv['title']}  ({len(wv['gates'])})")
        for g in wv["gates"]:
            extra = f"   waits on {', '.join(g['unmet'])}" if g["unmet"] else ""
            print(f"   {g['id']:<14}{g['phase']:<14}{extra}")
    for c in contradictions():
        print(f"\n!! {c['id']} PASSES but waits on {', '.join(c['unmet'])} "
              f"-- either the edge is wrong or the pass is vacuous")
    print("\n== critical path")
    for h in chain():
        print(f"   {h['id']:<14}{h['status']}")
    print("\n== teams")
    for t in teams():
        print(f"   {t['team']:<32}{t['passing']}/{t['total']}  {t['basis']}")
    u = unplaced()
    print(f"\n== unplaced  {len(u['unplaced'])} of {u['total']}: {', '.join(u['unplaced'])}")
