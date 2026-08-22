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

from dataclasses import dataclass, field
from typing import Dict, List

from .readiness import GATES

SIZE = {"S": "under an hour", "M": "a session", "L": "more than a session"}


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
            "FIRST: read agent-factory/docs/findings.md — corrected premises from other\n"
            "lanes, so you do not rebuild a mistake somebody already paid for.\n"
            "LAST: append your own findings there before you close, or write\n"
            "NOTHING TO REPORT. Silence must mean checked, not unlooked-at.\n\n"
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
            "FIRST: read agent-factory/docs/findings.md — corrected premises from other\n"
            "lanes, so you do not rebuild a mistake somebody already paid for.\n"
            "LAST: append your own findings there before you close, or write\n"
            "NOTHING TO REPORT. Silence must mean checked, not unlooked-at.\n\n"
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
            "FIRST: read agent-factory/docs/findings.md — corrected premises from other\n"
            "lanes, so you do not rebuild a mistake somebody already paid for.\n"
            "LAST: append your own findings there before you close, or write\n"
            "NOTHING TO REPORT. Silence must mean checked, not unlooked-at.\n\n"
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
            "FIRST: read agent-factory/docs/findings.md — corrected premises from other\n"
            "lanes, so you do not rebuild a mistake somebody already paid for.\n"
            "LAST: append your own findings there before you close, or write\n"
            "NOTHING TO REPORT. Silence must mean checked, not unlooked-at.\n\n"
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
            "FIRST: read agent-factory/docs/findings.md — corrected premises from other\n"
            "lanes, so you do not rebuild a mistake somebody already paid for.\n"
            "LAST: append your own findings there before you close, or write\n"
            "NOTHING TO REPORT. Silence must mean checked, not unlooked-at.\n\n"
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

# A renamed gate must break this loudly rather than silently dropping out of a lane — the same
# contract DEPENDS in factory.board holds itself to.
_KNOWN = {g.id for g in GATES}
_BAD: Dict[str, List[str]] = {l.id: [g for g in l.gates if g not in _KNOWN] for l in LANES}
_BAD = {k: v for k, v in _BAD.items() if v}
if _BAD:
    raise ValueError(f"lanes reference unknown gate id(s): {_BAD}")


def coverage() -> Dict[str, List[str]]:
    """Which gates no lane claims. Not an error — some gates are this session's own work — but
    an unclaimed gate is one nobody has decided who does, which is worth being able to see."""
    claimed = {g for l in LANES for g in l.gates}
    return {"unclaimed": sorted(g.id for g in GATES if g.id not in claimed),
            "claimed": sorted(claimed)}
