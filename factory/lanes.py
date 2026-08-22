"""Parallel lanes — which gates can be worked at the same time without colliding.

The board already says what can *start* (no unmet dependency). That is not the same as what can
run *in parallel*: 16 gates are startable and two sessions editing `orchestrator/pipelines.py`
at once will simply conflict. The binding constraint is **file locality**, not the dependency
graph.

⚠ **Basis, stated because this is the one file here that is not measured.** Gate membership and
dependency order are MEASURED (`factory.readiness`, `factory.board`). The *grouping into lanes*
is ASSUMED — a judgement about which gates touch the same files, made by reading them. It is
written down here rather than improvised per session so it can be argued with and corrected.
Effort sizes are ASSUMED too, and deliberately ordinal (S/M/L) rather than hours: an hours figure
would be read as a plan, and `factory.schedule` already refuses to project a completion date for
reasons it explains.

Gate ids are validated against `factory.readiness.GATES` at import, the same way `DEPENDS` in
`factory.board` is — a renamed gate breaks this loudly rather than silently dropping out of a lane.
"""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Dict, List, Optional, Set

from .readiness import GATES

SIZE = {"S": "under an hour", "M": "a session", "L": "more than a session"}

#: Prepended to every lane prompt. One copy, because five copies means four of them go stale.
PREAMBLE = """FIRST: read agent-factory/docs/findings.md — corrected premises from other lanes, so
you do not rebuild a mistake somebody already paid for. Six are seeded; one is a research answer
that named the wrong component and was carried into a second research question before anyone
checked it.

"""

#: Appended to every lane prompt.
POSTAMBLE = """

SUB-AGENTS — use them, and be token-conscious about it. Match the model to the work rather than
letting a sub-agent inherit yours:

  haiku    mechanical lookup: find where X lives, count occurrences, grep a convention
  sonnet   multi-step research, exploration, running a runbook, most code execution
  opus     code review, security review, and stress-testing a design

Do not spend opus on a grep, and do not run a whole session on opus because one step in it is
hard. Shut a sub-agent down the moment its deliverable lands; do not let one loop.

⚠ A sub-agent's report is a claim, not a measurement. Three of one session's own instruments
returned confident false results (finding F5), every one caught only by checking the finding
against the artefact itself. Verify before you act on it, and before you write it down.

REVIEWER — before you close this lane, run a review sub-agent on opus over your diff. Not a
rubber stamp: give it the lane's gates and ask specifically whether any control you added has
been WATCHED REFUSING something, whether any number you are reporting was measured or inferred,
and what you changed that nothing tests. Fix what it finds or record why not. A lane that closes
green without an independent read is the shape of defect this whole programme exists to stop.

LAST: append what you learned to agent-factory/docs/findings.md — corrected premises only — or
write NOTHING TO REPORT with the date and lane. Silence has to mean checked, not unlooked-at."""


@dataclass(frozen=True)
class Lane:
    id: str
    title: str
    why: str
    repo: str
    touches: str
    size: str
    gates: List[str] = field(default_factory=list)
    prompt: str = ""
    needs_paul: str = ""
    #: Recommended model for the SESSION running this lane, with its reason. ASSUMED, like the
    #: grouping — but stated per lane rather than as one blanket rule, because the answer differs
    #: and the token cost is real. Sub-agent models are chosen inside the lane; see POSTAMBLE.
    model: str = "sonnet"
    model_why: str = ""

    @property
    def full_prompt(self) -> str:
        """What actually gets copied or launched: shared guidance, this lane's specifics, and any
        operator answer to its declared blocker."""
        from .operator import block
        return PREAMBLE + self.prompt + POSTAMBLE + block(self)


LANES: List[Lane] = [
    Lane(
        id="control-plane",
        title="Bound the loop",
        why="Five gates, one file, and the biggest reliability win on the board. A stage with no "
            "attempt cap took the whole 10-core quota on 2026-08-14, and 4 of 14 runs are still "
            "sitting at stage_started with nothing to time them out.",
        repo="prefect-connectors",
        touches="orchestrator/pipelines.py",
        size="L",
        gates=["cap", "reaper", "concurrency", "bounded", "truthful", "from-history"],
        prompt=(
            "Work the control-plane gates in the agent-factory readiness set. Read\n"
            "aldc-launchpad/boot-prompts/evaluator-isolated-next-2026-08-22.md first, then\n"
            "agent-factory/docs/research/answers/R2-followup.md — it explains that our build\n"
            "plane is a BESPOKE engine at :8765 that does not import Prefect, so none of\n"
            "Prefect's retry/concurrency primitives are available and each control has to be\n"
            "built.\n\n"
            "Gates: cap, reaper, concurrency, bounded, truthful, from-history.\n"
            "All six live in prefect-connectors/orchestrator/pipelines.py.\n\n"
            "The mechanism behind `truthful` and `from-history` is already diagnosed in\n"
            "agent-factory/docs/evidence/false-succeeded-mechanism.md: the terminal verdict is\n"
            "computed from a last-write-wins per-stage status field, so a stage that failed 100\n"
            "times and succeeded once contributes nothing to any_failed. Do not re-derive it.\n\n"
            "Measure with `python -m factory.readiness` in agent-factory before and after.\n"
            "Every control needs a negative control: make it refuse something, and commit the\n"
            "proof. A mechanism nobody has watched refuse is not a control."),
    ),
    Lane(
        id="certify",
        title="Wire one instrument",
        why="`certified` is the head of the only dependency chain on the board "
            "(isolated -> certified -> tenancy). All 12 assertions return UNMEASURABLE against a "
            "live target because no probe is wired to anything.",
        repo="agent-factory",
        touches="factory/connector_contract.py",
        size="M",
        gates=["certified", "breadth", "corpus"],
        prompt=(
            "Wire a real instrument to the GreenContract in agent-factory so `certified` can\n"
            "stop reporting UNMEASURABLE. Read\n"
            "aldc-launchpad/boot-prompts/evaluator-isolated-next-2026-08-22.md first.\n\n"
            "The contract is factory/connector_contract.py; Probes refuses everything by design\n"
            "and CtxProbes reads a recorded world. You are adding a real subclass.\n\n"
            "START with A1 (config satisfiable) and A5 (regression suite) — both may be\n"
            "reachable from the prefect-connectors checkout alone, with no secret at all. Prove\n"
            "that before asking for a credential.\n\n"
            "STOP and ask Paul before touching any vault or Key Vault secret. Name the exact\n"
            "secret and source, get an explicit yes. No session has ever requested one.\n\n"
            "UNMEASURABLE must never become PASS just because a probe now exists but cannot\n"
            "reach its instrument."),
        needs_paul="explicit per-secret approval before any credential is read",
    ),
    Lane(
        id="judgement",
        title="Make the gates able to refuse",
        why="2 of 7 pipeline gates have a programmatic check; the rest are a human clicking "
            "approve. A gate never observed refusing is decoration — the same rule this repo "
            "already applies to evals.",
        repo="prefect-connectors",
        touches="orchestrator/pipelines.py gate definitions",
        size="M",
        gates=["refuses", "checks", "attributable", "honest", "general", "ceiling", "cost"],
        prompt=(
            "Work the judgement gates in the agent-factory readiness set. Read\n"
            "aldc-launchpad/boot-prompts/evaluator-isolated-next-2026-08-22.md first.\n\n"
            "Gates: refuses, checks, attributable, honest, general, ceiling, cost.\n\n"
            "⚠ COORDINATE: these touch prefect-connectors/orchestrator/pipelines.py, the same\n"
            "file as the control-plane lane. Run this lane only if that one is NOT running, or\n"
            "agree a split first. The dependency graph allows both; the filesystem does not.\n\n"
            "`checks` is measured as: how many pipeline gates carry a gate_check. `refuses` is\n"
            "measured as: has any gate ever been observed refusing a run. The second is the hard\n"
            "one and it is the point — add the check, then make it refuse something on purpose\n"
            "and commit the audit record proving it did."),
    ),
    Lane(
        id="artifact",
        title="Run impeccable at the readout",
        why="Gate `chain` is unstated and impeccable's 59 deterministic detector rules have never "
            "been pointed at the artifact. It is the instrument the static checks lacked, and it "
            "needs no browser and no credentials.",
        repo="agent-factory",
        touches="docs/artifacts/agent-factory.html, ~/.claude/skills/",
        size="S",
        gates=["chain"],
        prompt=(
            "Two things, both in agent-factory, neither needing a browser or a credential.\n\n"
            "1. Gate `chain`: state impeccable's place in the skill chain, in writing, in\n"
            "   ~/.claude/skills/living-systems-ui/SKILL.md — the probe reads that file and\n"
            "   looks for 'impeccable'. It overlaps artifact-design, artifact-motion and\n"
            "   living-systems-ui and the precedence has never been written down.\n\n"
            "2. Run impeccable's detector against docs/artifacts/agent-factory.html. Four\n"
            "   defects were found there on 2026-08-22 by rendering it (see\n"
            "   docs/evidence/render-pass-2026-08-22.md); the question is what a 59-rule static\n"
            "   detector finds that the render pass did not, and vice versa. Record both.\n\n"
            "⚠ Do NOT run this at the same time as anyone editing the artifact — check with\n"
            "Paul first. Verify with `python scripts/render_pass.py` (needs `pip install\n"
            "playwright`) and `python -m pytest`, which now fails if the page drifts."),
    ),
    Lane(
        id="grain",
        title="Settle the landing-table grain",
        why="The calibration world assumes two accounts sharing two campaign ids. If the real "
            "table holds one account, the declared primary key is wrong and A9 is calibrated "
            "against a mistake.",
        repo="agent-factory",
        touches="blueprints/windsorai_gep.yaml, factory/connector_contract.py",
        size="S",
        gates=["grain"],
        prompt=(
            "Settle gate `grain` in agent-factory. One Snowflake query decides it:\n\n"
            "  SELECT COUNT(DISTINCT account_id), COUNT(*), COUNT(DISTINCT campaign_id)\n"
            "  FROM QA_DG1_GEP_PREFECT_PR.WINDSORAI__PR.google_ads_CAMPAIGN\n"
            "  WHERE date = '2026-07-22';\n\n"
            "20 rows across 18 campaigns on one date cannot be unique on\n"
            "(account_id, campaign_id, date) under a single account. One account means the\n"
            "declared primary key is wrong.\n\n"
            "⚠ TRAP: `grain_confirmed` is NOT a field on ConnectorTarget, and\n"
            "targets.load_target raises on unknown keys — adding it to the blueprint breaks\n"
            "every load until the dataclass gains the field. Add it to ConnectorTarget in the\n"
            "same commit.\n\n"
            "⚠ Ask Paul before using any Snowflake credential. Name the secret and source."),
        needs_paul="Snowflake credential approval, and he may just know the answer",
    ),
]



# ---------------------------------------------------------------------------------------------
# Model recommendation per lane. Kept as a table rather than inline so the reasoning sits in one
# readable place — and so changing a call is a one-line diff somebody will actually review.
_MODEL: Dict[str, tuple] = {
    "control-plane": ("opus",
        "designing controls for a bespoke engine, each needing a negative control — this is design work, not execution. Pair with /effort high."),
    "certify": ("sonnet",
        "wiring a probe to an existing contract is execution after a decided design. Escalate to opus only if A1/A5 turn out not to be reachable without a secret."),
    "judgement": ("sonnet",
        "adding gate predicates is mechanical once the predicate is chosen; the hard part is making one refuse, which is a test, not a design."),
    "artifact": ("sonnet",
        "run a detector, read its output, write one precedence paragraph. No architecture in it."),
    "grain": ("haiku",
        "one query and one dataclass field. Escalate only if the answer contradicts the declared primary key, which is then a design question."),
}

LANES = [replace(l, model=_MODEL[l.id][0], model_why=_MODEL[l.id][1])
         if l.id in _MODEL else l for l in LANES]

# A renamed gate must break this loudly rather than silently dropping out of a lane — the same
# contract DEPENDS in factory.board holds itself to.
_KNOWN = {g.id for g in GATES}
_BAD: Dict[str, List[str]] = {l.id: [g for g in l.gates if g not in _KNOWN] for l in LANES}
_BAD = {k: v for k, v in _BAD.items() if v}
if _BAD:
    raise ValueError(f"lanes reference unknown gate id(s): {_BAD}")


def _touch_set(lane: "Lane") -> set:
    """The files a lane writes, normalised. `touches` is prose with commas in it, deliberately —
    it is read by humans first — so this splits and strips rather than demanding a list."""
    return {part.strip().split()[0] for part in lane.touches.split(",") if part.strip()}


def conflicts() -> Dict[str, List[str]]:
    """lane id -> other lanes that write a file it also writes.

    Symmetric, and NOT a dependency: both lanes are startable, they just cannot be started at the
    same time. 16 gates having no unmet dependency says nothing about whether two sessions can
    edit orchestrator/pipelines.py simultaneously.
    """
    out: Dict[str, List[str]] = {l.id: [] for l in LANES}
    for i, a in enumerate(LANES):
        for b in LANES[i + 1:]:
            if _touch_set(a) & _touch_set(b):
                out[a.id].append(b.id)
                out[b.id].append(a.id)
    return {k: sorted(v) for k, v in out.items()}


def waits_on(passing: Optional[Set[str]] = None) -> Dict[str, List[str]]:
    """lane id -> lanes it must follow, derived from gate dependencies.

    A lane waits on another when one of its gates depends on a gate that lives in that other lane
    and is not yet passing. Dependencies on already-passing gates are satisfied and drop out, so
    this shrinks as work lands rather than describing a fixed plan.

    `passing` is injected rather than measured here so the caller can reuse a measurement it has
    already paid for — running 30 probes twice to draw one page would be silly.
    """
    from .board import DEPENDS
    passing = passing or set()
    owner = {gid: l.id for l in LANES for gid in l.gates}
    out: Dict[str, List[str]] = {}
    for lane in LANES:
        need = set()
        for gid in lane.gates:
            for dep in DEPENDS.get(gid, []):
                if dep in passing:
                    continue                       # satisfied; not a wait
                home = owner.get(dep)
                if home and home != lane.id:
                    need.add(home)
        out[lane.id] = sorted(need)
    return out


def runnable_now(passing: Optional[Set[str]] = None) -> List[str]:
    """Lanes with no unsatisfied lane-dependency. Conflicts are NOT applied — they constrain which
    of these may run together, which is a choice for whoever is starting one."""
    w = waits_on(passing)
    return sorted(l.id for l in LANES if not w[l.id])


def unblocks(lane_id: str, passing: Optional[Set[str]] = None) -> int:
    """How many not-yet-passing gates are waiting, transitively, on this lane's gates.

    This is the only ranking input that is about consequence rather than convenience, so it
    dominates the score. Computed from the authored dependency graph, not guessed.
    """
    from .board import DEPENDS
    passing = passing or set()
    mine = {g for l in LANES if l.id == lane_id for g in l.gates}
    # reverse edges: gate -> gates that wait on it
    rev: Dict[str, Set[str]] = {}
    for gid, deps in DEPENDS.items():
        for d in deps:
            rev.setdefault(d, set()).add(gid)
    seen, stack = set(), list(mine)
    while stack:
        cur = stack.pop()
        for nxt in rev.get(cur, ()):
            if nxt not in seen and nxt not in mine:
                seen.add(nxt)
                stack.append(nxt)
    return len([g for g in seen if g not in passing])


def recommend(passing: Optional[Set[str]] = None,
              running: Optional[Set[str]] = None) -> List[tuple]:
    """[(lane, score, reason)] best first. The reason is the point — a bare ranking is an oracle.

    ⚠ The WEIGHTING is a judgement, not a measurement. Stated here so it can be disagreed with:

      +100 per not-yet-passing gate that transitively waits on this lane   consequence
      +  8 if nothing in the lane is done yet                              momentum, cheap tiebreak
      -  5 per gate already passing                                        avoid re-treading
      - 40 if the lane needs Paul for something                            cannot start unattended
      - 60 if a conflicting lane is already running                        the seat is taken
      -  6 per gate in the lane                                            prefer a finishable lane
    """
    passing, running = passing or set(), running or set()
    waits, clash = waits_on(passing), conflicts()
    out = []
    for lane in LANES:
        if lane.id in running:
            continue                                   # already being worked; not a suggestion
        if waits[lane.id]:
            continue                                   # not startable; not a recommendation
        done = [g for g in lane.gates if g in passing]
        if len(done) == len(lane.gates):
            continue                                   # nothing left to do here
        blocked_by_running = sorted(set(clash[lane.id]) & running)
        n_unblocks = unblocks(lane.id, passing)
        score = (100 * n_unblocks + (8 if not done else 0) - 5 * len(done)
                 - (40 if lane.needs_paul else 0) - (60 if blocked_by_running else 0)
                 - 6 * len(lane.gates))
        bits = []
        if n_unblocks:
            bits.append(f"unblocks {n_unblocks} gate(s) downstream")
        bits.append(f"{len(lane.gates) - len(done)} gate(s) left")
        bits.append(f"run on {lane.model}")
        if blocked_by_running:
            bits.append(f"⚠ conflicts with {', '.join(blocked_by_running)}, already running")
        if lane.needs_paul:
            bits.append(f"needs Paul: {lane.needs_paul}")
        out.append((lane, score, " · ".join(bits)))
    return sorted(out, key=lambda r: -r[1])


def coverage() -> Dict[str, List[str]]:
    """Which gates no lane claims. Not an error — some gates are this session's own work — but
    an unclaimed gate is one nobody has decided who does, which is worth being able to see."""
    claimed = {g for l in LANES for g in l.gates}
    return {"unclaimed": sorted(g.id for g in GATES if g.id not in claimed),
            "claimed": sorted(claimed)}
