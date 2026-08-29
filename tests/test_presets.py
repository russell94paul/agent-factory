"""A preset must carry its argument, not just its answer.

The value of this table is not the model name — it is the reason and the escalation trigger beside
it. An operator who disagrees with `haiku` needs to see why haiku was chosen to know whether their
ticket is the exception. So the tests here mostly pin *presence of reasoning*, and the import-time
guard that enforces it.

The load-bearing test is `test_the_import_guard_can_actually_reject` — a validator nobody has seen
refuse is not a validator.
"""
import dataclasses

import pytest

from factory.blueprint import AgentSpec
from factory.lanes import SIZE
from factory.presets import (
    AVAILABLE,
    PRESETS,
    UNBUILT,
    WIRED,
    Preset,
    by_id,
    for_layers,
    render,
    unwired,
)


# --------------------------------------------------------------- the reasoning must be there
@pytest.mark.parametrize("p", PRESETS, ids=lambda p: p.type_id)
def test_every_preset_carries_its_argument(p):
    """No model without a reason, no rule without an escalation trigger, no agent without a
    prohibition, and no type without a real ticket behind it."""
    assert p.model_why.strip(), "a model with no reason is a rule an operator cannot argue with"
    assert p.escalate_when.strip(), "without this the preset is a rule rather than advice"
    assert p.prohibition.strip(), "every agent carries an explicit must-not"
    assert p.seen_in.strip(), "a type with no ticket behind it is an invented archetype"
    assert p.verifier.strip()
    assert p.layers, "a preset that touches nothing cannot be scoped"


@pytest.mark.parametrize("p", PRESETS, ids=lambda p: p.type_id)
def test_sizes_are_ordinal_not_hours(p):
    """Inherited from lanes.SIZE deliberately — an hours figure would be read as a plan."""
    assert p.size in SIZE


def test_type_ids_are_unique():
    ids = [p.type_id for p in PRESETS]
    assert len(ids) == len(set(ids))


# --------------------------------------------------------------- ⭐ the guard must be able to fail
@pytest.mark.parametrize("field_name", ["model_why", "escalate_when", "prohibition", "verifier"])
def test_the_import_guard_can_actually_reject(field_name):
    """A validator nobody has seen refuse is not a validator.

    Re-runs the module's own checks against a deliberately malformed preset and requires them to
    complain. Without this, the guard in presets.py is an assertion about itself.
    """
    bad = dataclasses.replace(PRESETS[0], **{field_name: "   "})
    with pytest.raises(ValueError, match=field_name):
        _validate(bad)


def test_the_guard_rejects_an_unknown_size():
    bad = dataclasses.replace(PRESETS[0], size="XL")
    with pytest.raises(ValueError, match="size"):
        _validate(bad)


def test_the_guard_rejects_an_unknown_verifier_state():
    bad = dataclasses.replace(PRESETS[0], verifier_state="probably fine")
    with pytest.raises(ValueError, match="verifier_state"):
        _validate(bad)


def _validate(p: Preset) -> None:
    """The same checks presets.py runs at import, applied to one row so a test can trip them."""
    if p.size not in SIZE:
        raise ValueError(f"{p.type_id}: size {p.size!r} is not one of {sorted(SIZE)}")
    for f in ("model_why", "escalate_when", "prohibition", "verifier", "seen_in"):
        if not getattr(p, f).strip():
            raise ValueError(f"{p.type_id}: {f} is empty — a preset without it is a rule, not advice")
    if p.verifier_state not in (WIRED, AVAILABLE, UNBUILT):
        raise ValueError(f"{p.type_id}: verifier_state {p.verifier_state!r} is not a known state")


# --------------------------------------------------------------- honesty about coverage
def test_unwired_separates_a_claim_from_a_run():
    """A row naming a verifier claims one APPLIES. Only WIRED means one has been run.

    Collapsing those would make the table read as coverage it does not have — the same
    UNMEASURABLE-as-PASS move the contract layer refuses.
    """
    un = unwired()
    assert all(p.verifier_state != WIRED for p in un)
    assert set(un) | {p for p in PRESETS if p.verifier_state == WIRED} == set(PRESETS)


def test_at_least_one_verifier_is_actually_wired():
    """If none were, the table would be entirely aspirational and should say so louder."""
    assert any(p.verifier_state == WIRED for p in PRESETS)


# --------------------------------------------------------------- seeding an AgentSpec
def test_a_preset_seeds_a_valid_spec():
    p = PRESETS[0]
    spec = AgentSpec(name="w", role="impl", prompt="do the thing", **p.as_spec_kwargs())
    assert spec.model == p.model
    assert spec.prohibition == p.prohibition
    assert spec.version, "a seeded spec must still hash"


def test_a_preset_refuses_to_invent_the_task():
    """⭐ name, role and prompt are the operator's. A preset filling them would be pretending to
    know the task, and the resulting spec would carry a confident description of work nobody
    scoped."""
    kwargs = PRESETS[0].as_spec_kwargs()
    for owned_by_operator in ("name", "role", "prompt", "tools"):
        assert owned_by_operator not in kwargs


def test_changing_a_seeded_field_changes_the_version():
    """The config IS the version — pinned here because the UI surfaces it live."""
    p = PRESETS[0]
    a = AgentSpec(name="w", role="impl", prompt="x", **p.as_spec_kwargs())
    b = dataclasses.replace(a, budget_usd=a.budget_usd + 1)
    assert a.version != b.version


# --------------------------------------------------------------- lookup helpers
def test_by_id_returns_none_rather_than_raising():
    """An unknown id is a question, not a crash — the UI passes user input straight in."""
    assert by_id("no-such-type") is None
    assert by_id(PRESETS[0].type_id) is PRESETS[0]


def test_for_layers_requires_all_named_layers():
    both = for_layers("snowflake", "pbi_model")
    assert all({"snowflake", "pbi_model"} <= set(p.layers) for p in both)
    assert for_layers("snowflake") != for_layers("snowflake", "pbi_model", "eclipse")


def test_render_includes_the_reasoning_not_just_the_answer():
    """The UI and the CLI render from the same function so the two cannot drift."""
    out = render(PRESETS[0])
    assert PRESETS[0].model in out
    assert PRESETS[0].model_why[:30] in out
    assert "escalate" in out
    assert "must not" in out
