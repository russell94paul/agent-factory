"""Baseline presets — ticket type and size choose a starting configuration, with its reasons.

An operator opening a new client ticket should not start from an empty `AgentSpec`. The choices
that matter — model, effort, turn and spend caps, what the agent must not do, and which
deterministic check owns the verdict — are largely determined by **what kind of ticket it is** and
**how big it is**. This module holds that mapping.

⚠ **BASIS, stated because half this file is a judgement.**

* The **types** are MEASURED. Each is generalised from real delivered tickets, cited per row. They
  are not invented archetypes; every one has a ticket behind it and a verifier that was actually
  used.
* The **assignments** — which model, which caps, which prohibition — are ASSUMED. They are a
  judgement, written down here so they can be argued with rather than improvised per session.
  `factory.lanes` makes the same declaration for the same reason, and this module deliberately
  copies its shape: a model is never given without a `model_why`, and never without an
  **escalation trigger** naming the condition under which the choice is wrong.

⭐ **A preset is a starting point with its reasoning attached, not a lookup table.** The reason is
the load-bearing half: an operator who disagrees with `haiku` needs to see *why* haiku was chosen
in order to know whether their ticket is the exception. A bare model name gives them nothing to
argue with, so they either accept it blindly or ignore the table entirely.

**Sizes are ordinal, never hours.** Inherited from `factory.lanes.SIZE` for exactly the reason
stated there: an hours figure would be read as a plan.

⛔ **What a preset does NOT decide.** It does not decide whether the work is safe to dispatch. That
is the contract's job, and a preset naming a verifier is a claim that one *applies*, not that one
*has been wired*. `verifier_state` says which, and it is the field to read before trusting a row.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Dict, List, Optional

from .lanes import SIZE

#: A verifier that exists and runs today, versus one this row asserts *should* apply but which
#: nobody has wired. The distinction is the difference between a preset and a wish.
WIRED = "wired"          #: the check exists and has been run
AVAILABLE = "available"  #: the mechanism exists; this ticket type has not been put through it
UNBUILT = "unbuilt"      #: named because it is the right check — nothing implements it yet


@dataclass(frozen=True)
class Preset:
    """One (ticket type, size) starting configuration."""

    type_id: str
    title: str
    #: The real ticket(s) this type is generalised from. MEASURED — a type with no ticket behind
    #: it does not belong in this table.
    seen_in: str
    #: What the work actually touches. Drives which implementation session is needed.
    #: A tuple, not a list: the dataclass is frozen, and a mutable member would make that promise
    #: false for this field alone — and would silently make Preset unhashable.
    layers: tuple
    size: str
    model: str
    #: Why this model, in a sentence an operator can disagree with.
    model_why: str
    #: The condition under which the model choice is wrong. Without this a preset is a rule; with
    #: it, it is advice.
    escalate_when: str
    effort: str
    max_turns: int
    budget_usd: float
    #: The explicit "must not". Every agent carries one; the field is not optional here.
    prohibition: str
    #: The deterministic, non-LLM check that should own the verdict for this type.
    verifier: str
    verifier_state: str
    #: What only a human can settle for this type. Empty string means nothing known.
    needs_paul: str = ""

    def as_spec_kwargs(self) -> dict:
        """The subset that seeds an `AgentSpec`. Deliberately partial — `name`, `role` and `prompt`
        are the operator's, and a preset that filled them would be pretending to know the task."""
        return {
            "model": self.model,
            "effort": self.effort,
            "max_turns": self.max_turns,
            "budget_usd": self.budget_usd,
            "prohibition": self.prohibition,
        }


#: The five types. Each row's `seen_in` is the evidence that it is a real shape of work.
#:
#: Sizes: a type carries the size it USUALLY is. An operator can override, and the escalation
#: trigger is where the override is argued for.
PRESETS: List[Preset] = [
    Preset(
        type_id="ui-control",
        title="UI control change",
        seen_in="GP-327 — client sent a screenshot: 'what are these filters? Can we remove them?'",
        layers=("eclipse",),
        size="S",
        model="haiku",
        model_why=(
            "read a live document, compare two fields, remove an entry. No design decision in it — "
            "the judgement is entirely in the pre-check, which is deterministic."
        ),
        escalate_when=(
            "the filter carries a value. An empty filter is inert and removing it is a UI change; "
            "one with a value is a DATA change wearing a UI change's clothes, and that is a design "
            "question — escalate to sonnet and re-scope."
        ),
        effort="low",
        max_turns=25,
        budget_usd=1.0,
        prohibition=(
            "Must not modify any dashboard whose filter carries a non-empty locked_value or "
            "default_value. Must not deploy to PROD. Abort rather than assume the author checked."
        ),
        verifier="read the live Cosmos doc; assert both locked_value AND default_value are empty",
        verifier_state=WIRED,
        needs_paul="PROD promotion.",
    ),
    Preset(
        type_id="add-measure",
        title="Add a measure to a live semantic model",
        seen_in="GP-329 — ad-spend lines requested in the Cost & Margin folder",
        layers=("pbi_model",),
        size="S",
        model="sonnet",
        model_why=(
            "an additive DAX alias against an existing model is execution after a decided design, "
            "but the model is worked concurrently by others, so the change must be surgical."
        ),
        escalate_when=(
            "the measure needs a new column, a relationship, or touches the warehouse. That is no "
            "longer additive and becomes a dimension-gap ticket — re-scope, do not stretch this."
        ),
        effort="medium",
        max_turns=40,
        budget_usd=2.5,
        prohibition=(
            "Must not apply a full-TMSL rollback — the model is worked concurrently and a full "
            "replace reverts another engineer's work. Additive alias only. Must not write any "
            "credential into an exported artefact."
        ),
        verifier="DAX validation against the applied model; assert the alias resolves and no "
                 "existing measure changed",
        verifier_state=AVAILABLE,
        needs_paul="Design sign-off on naming and folder placement.",
    ),
    Preset(
        type_id="dimension-gap",
        title="Dimension gap / blank row on a dashboard",
        seen_in="GP-328 — 274 of 1,019 sellers collapsed into one blank member across 21+ dashboards",
        layers=("snowflake", "pbi_model", "eclipse",),
        size="M",
        model="sonnet",
        model_why=(
            "three layers, but each change is small and the shape is known once the grain mismatch "
            "is found. The hard part is locating it, which is a query, not a design."
        ),
        escalate_when=(
            "the warehouse says the data is clean. GP-328 had zero NULLs and zero orphan keys and "
            "the warehouse actively misled — the answer appeared only in DAX at the DASHBOARD's "
            "timeframe. If three warehouse hypotheses are refuted, stop and re-scope as a "
            "wrong-number ticket."
        ),
        effort="medium",
        max_turns=60,
        budget_usd=5.0,
        prohibition=(
            "Must not conclude from warehouse queries alone. Must not change a visual's field "
            "binding without recording the before state. Must not deploy to PROD."
        ),
        verifier="DAX at the dashboard's default timeframe, not the visual's; assert member count "
                 "before and after",
        verifier_state=AVAILABLE,
        needs_paul="PROD promotion; confirmation that the new dimension grain is the intended one.",
    ),
    Preset(
        type_id="wrong-number",
        title="A wrong number the client can see",
        seen_in="GP-322 — allocated ad cost read 3.6x campaign spend",
        layers=("snowflake",),
        size="L",
        model="opus",
        model_why=(
            "diagnosis, not execution. GP-322's cause was a circular dependency broken by "
            "materialisation order — a fact table built 16 seconds before its own denominator. "
            "Seven hypotheses were refuted before the real one."
        ),
        escalate_when=(
            "it is NOT diagnosis. If the cause is already known and the ticket is only the fix, "
            "this is execution — drop to sonnet and save the budget."
        ),
        effort="high",
        max_turns=120,
        budget_usd=15.0,
        prohibition=(
            "Must not deploy a fix to any schema other than a shadow copy. Must not claim a root "
            "cause without a discriminating test whose result was predicted before it ran. Must "
            "not close while any competing hypothesis remains unrefuted."
        ),
        verifier="shadow-schema replay: apply the fix to a copy, assert the number moves to the "
                 "expected value AND that out-of-scope rows are unchanged",
        verifier_state=AVAILABLE,
        needs_paul="Sign-off before any production schema change.",
    ),
    Preset(
        type_id="model-redesign",
        title="The model is unusable — redesign the surface",
        seen_in="GP-318 / GP-319 — audit of a 356-measure model; inert axes and false zeros",
        layers=("pbi_model", "snowflake",),
        size="L",
        model="opus",
        model_why=(
            "an audit across hundreds of measures, where the defect class is a slice that returns "
            "the grand total on every member — it neither errors nor blanks, so it looks healthy. "
            "Finding that requires reasoning about what SHOULD have differed."
        ),
        escalate_when=(
            "a scoping premise handed down in the ticket turns out to be wrong. GP-318 had two "
            "refuted by measurement — one named the wrong object entirely, and another's proposed "
            "COALESCE would have published '$0 ad spend' across 23 marketplaces whose true verdict "
            "was NOT-RECORDED. Stop and re-scope rather than implementing the stated premise."
        ),
        effort="high",
        max_turns=150,
        budget_usd=25.0,
        prohibition=(
            "Must not fill an absent value with zero. An absent platform is NOT-RECORDED, not "
            "zero, and publishing the difference is the defect this ticket type exists to fix. "
            "Must not overwrite live model state without asserting the before state first."
        ),
        verifier="pre/post assertion battery — capture live state before overwriting, replay after. "
                 "GP-318 caught 10 self-inflicted defects this way and review caught none",
        verifier_state=AVAILABLE,
        needs_paul="Design sign-off; PROD promotion.",
    ),
]


# A type id must be unique, every model must carry a reason and an escalation trigger, and every
# size must be one the ordinal scale knows. A silently malformed preset would hand an operator a
# configuration with no argument attached, which is the one thing this module exists to prevent.
_ids = [p.type_id for p in PRESETS]
if len(_ids) != len(set(_ids)):
    raise ValueError(f"duplicate preset type_id(s): {sorted({i for i in _ids if _ids.count(i) > 1})}")
for _p in PRESETS:
    if _p.size not in SIZE:
        raise ValueError(f"{_p.type_id}: size {_p.size!r} is not one of {sorted(SIZE)}")
    for _f in ("model_why", "escalate_when", "prohibition", "verifier", "seen_in"):
        if not getattr(_p, _f).strip():
            raise ValueError(f"{_p.type_id}: {_f} is empty — a preset without it is a rule, not advice")
    if _p.verifier_state not in (WIRED, AVAILABLE, UNBUILT):
        raise ValueError(f"{_p.type_id}: verifier_state {_p.verifier_state!r} is not a known state")


def by_id(type_id: str) -> Optional[Preset]:
    """The preset for a type id, or None. Never raises — an unknown id is a question, not a crash."""
    return next((p for p in PRESETS if p.type_id == type_id), None)


def for_layers(*layers: str) -> List[Preset]:
    """Every preset touching all the named layers. Useful when the ticket names the change but not
    its type: 'it needs Snowflake and PBI' narrows the list without guessing."""
    want = set(layers)
    return [p for p in PRESETS if want <= set(p.layers)]


def unwired() -> List[Preset]:
    """Presets whose verifier is named but not wired.

    ⚠ Read this before treating the table as coverage. A row naming a verifier is a claim that one
    APPLIES; only `WIRED` means one has actually been run for that type.
    """
    return [p for p in PRESETS if p.verifier_state != WIRED]


def render(p: Preset) -> str:
    """One preset as plain text — the same content the UI shows, so the two cannot drift."""
    lines = [
        f"{p.title}  [{p.type_id}]  size {p.size} — {SIZE[p.size]}",
        f"  seen in     {p.seen_in}",
        f"  layers      {', '.join(p.layers)}",
        f"  model       {p.model} (effort {p.effort}) — {p.model_why}",
        f"  escalate    {p.escalate_when}",
        f"  caps        {p.max_turns} turns · ${p.budget_usd:.2f}",
        f"  must not    {p.prohibition}",
        f"  verifier    [{p.verifier_state}] {p.verifier}",
    ]
    if p.needs_paul:
        lines.append(f"  needs Paul  {p.needs_paul}")
    return "\n".join(lines)


def main() -> int:
    print(f"{len(PRESETS)} baseline presets — types MEASURED from real tickets, "
          f"assignments ASSUMED\n")
    for p in PRESETS:
        print(render(p))
        print()
    un = unwired()
    if un:
        print(f"⚠ {len(un)} of {len(PRESETS)} name a verifier that is not wired: "
              f"{', '.join(p.type_id for p in un)}")
        print("  A named verifier is a claim that one APPLIES, not that one has been run.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
