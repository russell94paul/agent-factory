"""A routing table must be able to route wrongly, and a version must be able to change.

`registry.py` joins the two halves of the estate — the councils that carry the methods, and this
package's contracts and ledger. Two properties make it worth having, and neither is self-evident:

1. **The filter discriminates.** A `for_shape` that returned everything for every query would look
   identical to a working one at every call site that only ever asks for one shape. So the tests
   here pin the *exclusions* as hard as the matches.
2. **The version tracks the text.** A workflow whose entire behaviour is prose has no other
   identity. `test_version_changes_when_the_text_changes` is the load-bearing one: a hash that did
   not move when the file did would let a certification transfer across a rewrite.

The import guard gets the same treatment `test_presets.py` gives its own — a validator nobody has
watched refuse is not a validator.
"""
from __future__ import annotations

import dataclasses
import pathlib

import pytest

from factory import registry
from factory.registry import (
    COMMAND,
    DECLARED,
    LAYERS,
    PROVEN,
    SHAPES,
    SKILL,
    UNBUILT,
    WORKFLOWS,
    Workflow,
    by_id,
    for_shape,
    render,
    uninstalled,
    unproven,
    versions,
)


# --------------------------------------------------------------------- the table is well formed

def test_every_shape_has_at_least_one_workflow():
    """A shape nothing routes to is a hole, and it should be visible as one."""
    for shape in SHAPES:
        assert for_shape(shape), f"no workflow answers shape {shape!r}"


def test_every_row_states_where_it_ends():
    """A workflow that cannot end cannot be told it is finished — the 965-run loop's signature."""
    for w in WORKFLOWS:
        assert w.ends_at.strip(), f"{w.id} does not say what it ends at"


def test_a_non_unbuilt_row_cites_its_evidence():
    for w in WORKFLOWS:
        if w.state != UNBUILT:
            assert w.evidence.strip(), f"{w.id} claims state {w.state!r} with no citation"


def test_ids_are_unique():
    ids = [w.id for w in WORKFLOWS]
    assert len(ids) == len(set(ids))


# ------------------------------------------------------------------------- the filter must filter

def test_for_shape_excludes_other_shapes():
    """The positive control's negative half. `keel` answers design; it must not answer review."""
    assert "keel" in [w.id for w in for_shape("design")]
    assert "keel" not in [w.id for w in for_shape("review")]
    assert "inquest" not in [w.id for w in for_shape("design")]


def test_layer_narrows_and_layer_agnostic_survives():
    """`keel` declares warehouse/semantic_model, so a connector question must not reach it.

    `army` declares no layers and is eligible everywhere — that is the distinction the `not w.layers`
    branch encodes, and it would be invisible without a case that exercises both.
    """
    design_sm = [w.id for w in for_shape("design", "semantic_model")]
    design_conn = [w.id for w in for_shape("design", "connector")]

    assert "keel" in design_sm
    assert "keel" not in design_conn, "a layer-scoped workflow leaked into a layer it does not serve"
    assert "army" in design_sm and "army" in design_conn, "layer-agnostic row was wrongly filtered"


def test_build_routes_to_the_right_repo_machine():
    """The two build workflows are layer-disjoint; routing must respect that."""
    conn = [w.id for w in for_shape("build", "connector")]
    sm = [w.id for w in for_shape("build", "semantic_model")]
    assert "prefect-connector" in conn and "gep-feature" not in conn
    assert "gep-feature" in sm and "prefect-connector" not in sm


def test_unknown_shape_or_layer_raises_rather_than_returning_empty():
    """⛔ An empty list for a typo is indistinguishable from an honest 'nothing routes here'."""
    with pytest.raises(ValueError):
        for_shape("diagnos")           # typo
    with pytest.raises(ValueError):
        for_shape("design", "warehse")  # typo


def test_by_id_returns_none_rather_than_raising():
    assert by_id("keel") is not None
    assert by_id("no-such-workflow") is None


# ------------------------------------------------------------------------------ version behaviour

def test_version_changes_when_the_text_changes(tmp_path, monkeypatch):
    """⭐ The load-bearing test. The config that IS the version, applied to prose.

    A hash that did not move when the file did would let a certification earned under one method
    silently transfer to a rewritten one — `blueprint.py`'s founding failure mode, in a new place.
    """
    monkeypatch.setenv("CLAUDE_CONFIG_HOME", str(tmp_path))
    d = tmp_path / "skills" / "keel"
    d.mkdir(parents=True)
    f = d / "SKILL.md"

    f.write_text("first text", encoding="utf-8")
    w = by_id("keel")
    before = w.version
    assert before is not None and w.installed

    f.write_text("second text", encoding="utf-8")
    after = w.version

    assert after is not None
    assert before != after, "the version did not move when the workflow's text did"


def test_a_missing_file_is_not_visible_rather_than_version_zero(tmp_path, monkeypatch):
    """⛔ None means NOT-VISIBLE. It is not a version and it is not 'unchanged'.

    The whole repo exists to stop a measurement that never happened reading as one that did; a
    missing file rendering as a version would be exactly that, one layer down.
    """
    monkeypatch.setenv("CLAUDE_CONFIG_HOME", str(tmp_path))   # empty estate
    w = by_id("keel")
    assert w.installed is False
    assert w.version is None

    out = render(w)
    assert "NOT-VISIBLE" in out, "a missing workflow rendered without saying so"
    assert str(w.path) in out, "the render must name the path that was checked"


def test_versions_covers_every_row(tmp_path, monkeypatch):
    monkeypatch.setenv("CLAUDE_CONFIG_HOME", str(tmp_path))
    v = versions()
    assert set(v) == {w.id for w in WORKFLOWS}
    assert all(x is None for x in v.values()), "empty estate should be uniformly NOT-VISIBLE"


def test_uninstalled_reports_the_whole_table_on_an_empty_estate(tmp_path, monkeypatch):
    """The positive control for `uninstalled()` — an instrument that can never report is useless."""
    monkeypatch.setenv("CLAUDE_CONFIG_HOME", str(tmp_path))
    assert len(uninstalled()) == len(WORKFLOWS)


# ------------------------------------------------------------- the guard must be able to refuse

@pytest.mark.parametrize(
    "field,value",
    [
        ("shapes", ()),                  # routes from nowhere
        ("shapes", ("no-such-shape",)),
        ("layers", ("no-such-layer",)),
        ("ends_at", "   "),              # cannot be finished
        ("state", "probably-fine"),
        ("kind", "vibes"),
    ],
)
def test_the_import_guard_can_actually_reject(field, value):
    """A validator nobody has watched refuse is not a validator.

    Re-runs the module's own import-time checks against a deliberately malformed row, so the guard
    is exercised rather than merely present. Mirrors `test_presets.py`'s treatment of the same risk.
    """
    good = by_id("keel")
    bad = dataclasses.replace(good, **{field: value})

    with pytest.raises(ValueError):
        _validate(bad)


def test_the_guard_accepts_a_well_formed_row():
    """The other half of the control — a check that rejects everything catches nothing."""
    _validate(by_id("keel"))


def _validate(w: Workflow) -> None:
    """The import-time guard, extracted so a single row can be put through it."""
    if w.kind not in (SKILL, COMMAND):
        raise ValueError(f"{w.id}: kind {w.kind!r} is not a known kind")
    if w.state not in (PROVEN, DECLARED, UNBUILT):
        raise ValueError(f"{w.id}: state {w.state!r} is not a known state")
    if not w.shapes:
        raise ValueError(f"{w.id}: names no shape")
    for s in w.shapes:
        if s not in SHAPES:
            raise ValueError(f"{w.id}: shape {s!r} unknown")
    for lay in w.layers:
        if lay not in LAYERS:
            raise ValueError(f"{w.id}: layer {lay!r} unknown")
    if not w.ends_at.strip():
        raise ValueError(f"{w.id}: ends_at is empty")
    if w.state != UNBUILT and not w.evidence.strip():
        raise ValueError(f"{w.id}: state {w.state!r} with no evidence")


# ------------------------------------------------------------------------------- honesty surfaces

def test_unproven_is_not_empty_and_names_keel():
    """⚠ If this ever passes with an empty list, check it is because runs were recorded — not
    because somebody promoted rows to PROVEN to make the warning go away."""
    ids = [w.id for w in unproven()]
    assert "keel" in ids, "keel has not been run on real work yet and must not claim otherwise"
