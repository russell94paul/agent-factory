"""The registry that turns a preset's *named* verifier into a callable the controller runs.

⭐ **This module is the difference between a preset naming a check and the factory running one.**
`factory.presets` describes, in prose, the deterministic check that owns the verdict for each
ticket type. `factory.control.assertions` will run one — but only if it is handed a callable, and
until now nothing ever handed it one. Every run therefore ended:

    [UNMEASURABLE] ticket_verifier  preset 'ui-control' declares a WIRED verifier but the
                                    controller was given no callable to run.

That message is the shape of the defect this estate keeps finding: a declaration with no
mechanism behind it. `ui-control` had claimed WIRED since the table was written — see F87.

⛔ **A registry entry is the ONLY thing that makes a verifier real.** `verifier_state=WIRED` is a
claim; `REGISTRY[type_id]` is the mechanism. They are checked against each other in
`tests/test_verifiers.py` rather than trusted, because this repository has already lost three
hand-maintained lists to silent drift.

⚠ **A verifier does not go and observe the world; it adjudicates what the run observed.** A
verifier that measured Power BI itself would be a second instrument with its own credentials, its
own failure modes and no record of what it saw. Instead the agent leaves its evidence at
`.factory/verification.json` inside its own worktree, and the verifier holds that evidence to a
contract. **A missing evidence file is UNMEASURABLE, never FAIL** — an agent that produced no
evidence has not been observed to fail, it has not been observed at all.
"""
from __future__ import annotations

import json
import pathlib
from typing import Callable, Dict, Optional, Tuple

from .contract import Unmeasurable, Verdict
from .pbi_contract import CtxProbes, PbiTarget, build_contract

#: Same shape as `factory.control.Verifier`, restated rather than imported so this module does
#: not depend on the controller — the controller imports this, and a cycle would make the
#: registry unimportable from anywhere the controller was not already loaded.
Verifier = Callable[[dict], Tuple[bool, str]]

#: Where an agent must leave what it observed, relative to its worktree. One fixed path, because
#: a verifier that goes looking for its evidence will eventually find somebody else's.
EVIDENCE_RELPATH = ".factory/verification.json"


class ApparatusError(RuntimeError):
    """Our own machinery broke while adjudicating — TTCN-3 `error`, not `inconc`.

    ⛔ Deliberately NOT a subclass of `Unmeasurable`. `factory.contract.Assertion.run` catches
    `Unmeasurable` as UNMEASURABLE and anything else as ERROR, and the two have different
    remedies: UNMEASURABLE says *wire the instrument*, ERROR says *the run itself is
    untrustworthy*. An inner contract that reached ERROR must not be flattened into "we could not
    look" on its way out — that is exactly the collapse `factory/contract.py` grew a fifth
    verdict to prevent.
    """


# ------------------------------------------------------------------------------- the evidence

def evidence_path(ctx: dict) -> pathlib.Path:
    wt = ctx.get("worktree")
    if not wt:
        raise Unmeasurable(
            "no worktree in the run context — there is nowhere to read evidence from")
    return pathlib.Path(wt) / EVIDENCE_RELPATH


def read_evidence(ctx: dict) -> dict:
    """The agent's own record of what it observed, or Unmeasurable.

    Every failure in here is UNMEASURABLE rather than FAIL, and that is load-bearing: a missing or
    unreadable evidence file means **nobody looked**. Returning FAIL would report the client's
    work as broken on the strength of our own paperwork being absent.
    """
    p = evidence_path(ctx)
    if not p.is_file():
        raise Unmeasurable(
            f"the agent left no verification evidence at {EVIDENCE_RELPATH} — nothing observed "
            "the ticket's actual work, so this is not a pass and not a failure")
    try:
        raw = p.read_text(encoding="utf-8")
    except OSError as exc:
        raise Unmeasurable(f"{EVIDENCE_RELPATH} could not be read: {exc}") from exc
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise Unmeasurable(f"{EVIDENCE_RELPATH} does not parse as JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise Unmeasurable(
            f"{EVIDENCE_RELPATH} holds {type(data).__name__}, not an object carrying 'target' "
            "and 'observations'")
    return data


def _fold(res, what: str) -> Tuple[bool, str]:
    """One contract's result, folded into one assertion's (ok, detail), lattice preserved.

    ⭐ The four branches are the whole point, because each maps to a different remedy:

    ============  ========================  ==========================================
    inner         becomes                   what it tells the operator
    ============  ========================  ==========================================
    PASS          (True, summary)           the ticket's work was observed to be right
    FAIL          (False, the failures)     the work is wrong — read which claim broke
    UNMEASURABLE  raise Unmeasurable        wire the missing probe
    ERROR         raise ApparatusError      our harness broke; distrust the whole run
    ============  ========================  ==========================================
    """
    v = res.verdict
    if v is Verdict.PASS:
        return True, res.summary()
    if v is Verdict.FAIL:
        # The failing assertions themselves, not a count: an operator needs to know WHICH claim
        # broke. A bare "FAIL=2" sends them back to re-run the contract by hand.
        return False, "; ".join(str(r) for r in res.failures()) or res.summary()
    if v is Verdict.ERROR:
        raise ApparatusError(
            f"{what} could not be adjudicated — an instrument raised inside the contract: "
            + "; ".join(str(r) for r in res.failures()))
    if v is Verdict.NOT_RUN:
        raise Unmeasurable(f"{what} ran no assertions at all")
    raise Unmeasurable(f"{what}: " + "; ".join(str(r) for r in res.failures()))


# ------------------------------------------------------------------------------ the verifiers

def pbi_model_change(ctx: dict) -> Tuple[bool, str]:
    """Adjudicate a Power BI model change against `factory.pbi_contract`'s M1-M12.

    `pbi_contract` has sat complete and unused since it was written — `roadmap.py` still carries
    the line *"grep -rln pbi_contract tests/ factory/ scripts/ returns nothing"*. It is precisely
    the deterministic check the `add-measure` preset already named in prose. This function is the
    join between the two.

    ⭐ **A green verdict here requires the consumer layer.** M10 (*every visual paints*) and M11
    (*each control responds*) are assertions XMLA and DAX cannot make, and the contract refuses to
    drop them. An agent that supplies only model-layer observations gets UNMEASURABLE — the honest
    answer, because on GP-293 a repoint passed DAX parity while every visual rendered "Error
    loading data". The standing rule that a dashboard change is validated at the *rendered
    surface* is therefore enforced by the contract instead of remembered by a person.
    """
    ev = read_evidence(ctx)

    target_kw = ev.get("target")
    if not isinstance(target_kw, dict):
        raise Unmeasurable(
            f"{EVIDENCE_RELPATH} declares no 'target' object — with no declared dataset id there "
            "is nothing to hold the change to")
    if not target_kw.get("dataset_id"):
        raise Unmeasurable(
            "the evidence names no target dataset_id. Identity is by ID, never by matching "
            "values — two datasets can hold identical numbers and still be different datasets")
    try:
        target = PbiTarget(**target_kw)
    except TypeError as exc:
        raise Unmeasurable(f"'target' does not describe a PbiTarget: {exc}") from exc

    observations = ev.get("observations")
    if not isinstance(observations, dict):
        raise Unmeasurable(
            f"{EVIDENCE_RELPATH} carries no 'observations' object, so every probe would refuse "
            "and the contract could report only that it had not looked")

    return _fold(build_contract(target, CtxProbes()).run(observations),
                 f"the Power BI model contract for {target.dataset_id}")


#: type_id -> the callable that owns that ticket type's verdict.
#:
#: ⛔ Add a row here ONLY when the callable can actually reach a verdict, and flip that preset's
#: `verifier_state` to WIRED in the same change. The consistency test refuses a disagreement in
#: either direction, so a half-landed wiring cannot ship.
REGISTRY: Dict[str, Verifier] = {
    "add-measure": pbi_model_change,
}


def for_type(type_id: Optional[str]) -> Optional[Verifier]:
    """The verifier for a ticket type, or None when nothing is wired for it.

    None is a real answer rather than an error: most presets name a check nobody has built, and
    `control.assertions` turns that into UNMEASURABLE with the reason attached.
    """
    if not type_id:
        return None
    return REGISTRY.get(type_id)
