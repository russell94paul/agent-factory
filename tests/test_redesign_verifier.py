"""The redesign contract — and the two measurements that say it had to exist.

⭐ **The load-bearing test is `test_the_m_contract_certifies_the_defect_this_preset_exists_to_fix`.**
It pins the reason this module is not just `pbi_model_change` with a bigger budget: evidence
carrying GP-318's signature defect — the slicer responds, every visual paints, and `ME Spend`
returns the grand total for every brand — scores **PASS=12** under M1-M12, and FAILs under the
redesign contract. If that test ever goes green on both, R3 has stopped working and the estate is
certifying inert axes again.

The second measurement is `test_a_redesign_is_permanently_unmeasurable_under_the_m_contract`: M4
refuses any non-additive change, so registering `model-redesign` against the M-contract would have
wired a gate that cannot pass. That is the trap F87 was recorded about, avoided by measuring
first.
"""
from __future__ import annotations

import copy
import json
import pathlib

import pytest

from factory import control, presets, verifiers
from factory.contract import Unmeasurable, Verdict
from factory.pbi_contract import PbiTarget, build_contract
from factory.redesign_contract import build_redesign_contract
from factory.provider import AgentResult


#: A complete redesign observation set: every probe answered, including the two the M-contract
#: has no field for — the pre-state, and the per-member values that reveal an inert axis.
GOOD = {
    "target": {
        "dataset_id": "ds-66151728",
        "dataset_name": "Marketing Model",
        "environment": "TEST",
        "allow_environments": ["TEST"],
        # ⚠ A redesign renames and deletes. Declaring otherwise would be the lie that makes the
        # M-contract appear to apply.
        "additive_only": False,
        "protected_objects": ["Sales Measures[Locked Total]"],
        "writable_fields": ["Sales Measures[ME Spend]"],
        "anchors": {"ME Spend": 2890054.50},
        "baseline": {"GASP": 82135.29},
        "must_be_blank_not_zero": ["MEP Grounded Spend"],
        "bound_reports": ["rpt-exec"],
        "min_refresh_seconds": 5.0,
        "tolerance": 0.01,
        # the population, enumerated — not the measures somebody remembered
        "population": ["ME Spend", "GASP", "MEP Grounded Spend"],
        # ⭐ the declaration that makes the inert-axis defect measurable at all
        "must_slice_by": {"ME Spend": ["Brand"]},
    },
    "observations": {
        "rollback": {"path": "rollback/ds-66151728.tmsl", "captured_before_change": True,
                     "bytes": 41238, "parses": True},
        "pre_state": {"captured_before_change": True, "source": "XMLA, pre-deploy",
                      "measures": {"ME Spend": 2750000.00, "GASP": 82135.29,
                                   "MEP Grounded Spend": None}},
        "writes": {
            "dataset_id": "ds-66151728", "environment": "TEST",
            "fields": [{"field": "Sales Measures[ME Spend]", "appended": True}],
            "renamed": [{"object": "GASP", "to": "Gross Ad Spend",
                         "dependents": ["rpt-exec / Spend by Brand"],
                         "dependents_rewritten": True}],
            "deleted": [],
            "touched": ["Sales Measures[ME Spend]"],
            "added": ["Sales Measures[ME Spend]"],
        },
        "refresh": {"status": "Completed", "duration_seconds": 118.4,
                    "partition_dates": ["2026-08-30"]},
        "dax": {"measures": {"ME Spend": 2890054.50, "GASP": 82135.29,
                             "MEP Grounded Spend": None},
                "blankness": {"MEP Grounded Spend": "BLANK"}},
        "source": {"measures": {"ME Spend": 2890054.50}},
        "bindings": {"escaped_json_decoded": True,
                     "bound_fields": ["Sales Measures[ME Spend]", "Sales Measures[GASP]"]},
        "render": {"reports": {"rpt-exec": {"visuals_total": 14, "visuals_errored": [],
                                            "visuals_blank": []}}},
        "interact": {"controls": [{"name": "Date slicer", "responded": True},
                                  {"name": "Brand filter", "responded": True}]},
        # ⭐ what `interact` cannot say: the numbers actually differed across the members
        "slices": {"measures": {"ME Spend": {"Brand": {
            "members": ["Acme", "Borealis", "Cinder"],
            "values": [1200000.00, 900000.00, 790054.50],
            "grand_total": 2890054.50}}}},
    },
}


@pytest.fixture()
def good():
    return copy.deepcopy(GOOD)


def _ctx(tmp_path: pathlib.Path, evidence=None) -> dict:
    if evidence is not None:
        p = tmp_path / verifiers.EVIDENCE_RELPATH
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(evidence), encoding="utf-8")
    return {"worktree": tmp_path}


# ================================================================ why this module had to exist
def test_a_redesign_is_permanently_unmeasurable_under_the_m_contract(tmp_path, good):
    """⛔ Measurement 1. M4 refuses every non-additive change, so the M-contract can never pass one.

    Registering `model-redesign` against `pbi_model_change` would have wired a gate that cannot
    pass — a verifier the agent cannot satisfy however well it works, which is the trap F87 was
    recorded about.
    """
    with pytest.raises(Unmeasurable) as exc:
        verifiers.pbi_model_change(_ctx(tmp_path, good))

    assert "M4-additive-manifest" in str(exc.value)
    assert "additive_only" in str(exc.value)


def test_the_m_contract_certifies_the_defect_this_preset_exists_to_fix(tmp_path, good):
    """⭐⛔ Measurement 2, and the whole reason R3 exists.

    The `model-redesign` preset names its defect class in its own `model_why`: *"a slice that
    returns the grand total on every member — it neither errors nor blanks, so it looks
    healthy"*. Here `ME Spend` returns the grand total for all three brands. The slicer responds.
    Every visual paints. Every anchor holds.

    M1-M12 says **PASS**. The redesign contract says **FAIL** and names the measure.

    `M11` is satisfied by `responded: True`, which a repainting visual reports whether or not the
    number changed. `interact` asks whether the control responded; `slices` asks whether the
    numbers moved. Only the second can see this.
    """
    total = 2890054.50
    good["observations"]["slices"]["measures"]["ME Spend"]["Brand"].update(
        values=[total, total, total])

    # the M-contract, given an additive target so M4 does not short-circuit the comparison
    m_only = copy.deepcopy(good)
    m_only["target"]["additive_only"] = True
    m_only["observations"]["writes"]["renamed"] = []
    res_m = build_contract(PbiTarget(**{k: v for k, v in m_only["target"].items()
                                        if k not in ("population", "must_slice_by")}),
                           _ctx_probes()).run(m_only["observations"])
    assert res_m.verdict is Verdict.PASS, res_m.summary()
    assert "PASS=12" in res_m.summary()

    # the redesign contract, on the same defect
    ok, detail = verifiers.pbi_model_redesign(_ctx(tmp_path, good))
    assert ok is False
    assert "R3-no-axis-is-inert" in detail
    assert "IS the grand total" in detail, \
        "the failure must say the value is the grand total, which is what makes it this defect"
    assert "ME Spend" in detail and "Brand" in detail


def _ctx_probes():
    from factory.pbi_contract import CtxProbes
    return CtxProbes()


# ================================================================================ it can PASS
def test_the_redesign_verifier_can_reach_a_pass(tmp_path, good):
    """The positive control. Without it every refusal below proves only that it always refuses."""
    ok, detail = verifiers.pbi_model_redesign(_ctx(tmp_path, good))
    assert ok is True, detail
    assert "PASS=15" in detail


def test_the_redesign_contract_keeps_every_m_assertion_but_the_one_it_replaces():
    c = build_redesign_contract(PbiTarget(dataset_id="x"))
    names = [a.name for a in c.assertions]

    assert "M4-additive-manifest" not in names, "M4 must be replaced, not kept alongside R2"
    assert "R2-renames-carry-their-dependents" in names
    for n in ("M1-rollback-captured-first", "M8-absence-renders-blank", "M10-every-visual-paints",
              "M11-controls-respond", "M12-change-is-reachable"):
        assert n in names, f"{n} was dropped on the way through"
    assert len(names) == 15


def test_the_substitution_is_verified_not_assumed(monkeypatch):
    """⛔ If pbi_contract renames M4, this module must refuse rather than silently ship one
    fewer check than it believes it has."""
    from factory import redesign_contract as rc
    monkeypatch.setattr(rc, "REPLACES", "M4-under-a-different-name")
    with pytest.raises(RuntimeError, match="cannot verify the substitution"):
        rc.build_redesign_contract(PbiTarget(dataset_id="x"))


# ================================================================== R1 — the pre/post battery
def test_a_before_state_captured_after_the_overwrite_is_a_fail(tmp_path, good):
    """The preset's own prohibition: must not overwrite live model state without asserting the
    before state first. Captured afterwards it measures the damage."""
    good["observations"]["pre_state"]["captured_before_change"] = False

    ok, detail = verifiers.pbi_model_redesign(_ctx(tmp_path, good))
    assert ok is False
    assert "R1-pre-state-captured-over-the-population" in detail
    assert "measurement of the damage" in detail


def test_an_unenumerated_population_is_unmeasurable(tmp_path, good):
    """GP-318 audited 356 measures. A redesign checked against a sample is not checked."""
    good["target"]["population"] = []

    with pytest.raises(Unmeasurable, match="population was not enumerated"):
        verifiers.pbi_model_redesign(_ctx(tmp_path, good))


def test_a_measure_with_no_pre_state_is_unmeasurable_not_fail(tmp_path, good):
    """We cannot say a measure moved if we never saw where it started."""
    del good["observations"]["pre_state"]["measures"]["GASP"]

    with pytest.raises(Unmeasurable) as exc:
        verifiers.pbi_model_redesign(_ctx(tmp_path, good))
    assert "no pre-state" in str(exc.value) and "GASP" in str(exc.value)


def test_a_captured_measure_that_was_never_replayed_is_unmeasurable(tmp_path, good):
    """R4. A battery that captures 356 and replays 40 has not found 316 to be fine — it has not
    looked at them, and that difference is the whole point of this repository."""
    del good["observations"]["dax"]["measures"]["MEP Grounded Spend"]

    with pytest.raises(Unmeasurable) as exc:
        verifiers.pbi_model_redesign(_ctx(tmp_path, good))
    assert "never replayed" in str(exc.value)
    assert "MEP Grounded Spend" in str(exc.value)


# ============================================================================ R2 — the renames
def test_a_rename_whose_dependents_were_not_rewritten_is_a_fail(tmp_path, good):
    """A TOM rename does not rewrite the DAX that references the old name, and this dataset has
    live reports bound to it."""
    good["observations"]["writes"]["renamed"][0]["dependents_rewritten"] = False

    ok, detail = verifiers.pbi_model_redesign(_ctx(tmp_path, good))
    assert ok is False
    assert "R2-renames-carry-their-dependents" in detail
    assert "GASP" in detail


def test_a_rename_reported_as_a_bare_name_is_unmeasurable(tmp_path, good):
    """'GASP was renamed' says nothing about what still points at it."""
    good["observations"]["writes"]["renamed"] = ["GASP"]

    with pytest.raises(Unmeasurable) as exc:
        verifiers.pbi_model_redesign(_ctx(tmp_path, good))
    assert "bare names" in str(exc.value)


def test_a_rename_listing_no_dependents_is_unmeasurable_not_a_pass(tmp_path, good):
    """⛔ An absent dependents list is NOT-VISIBLE, not 'nothing depends on it'."""
    good["observations"]["writes"]["renamed"][0].pop("dependents")

    with pytest.raises(Unmeasurable) as exc:
        verifiers.pbi_model_redesign(_ctx(tmp_path, good))
    assert "no dependents" in str(exc.value)


def test_a_rename_with_genuinely_no_dependents_passes(tmp_path, good):
    """The other side of it: an empty list is an answer, and must not be confused with a
    missing one. Without this, the assertion above could be satisfied by a check that simply
    always refuses."""
    good["observations"]["writes"]["renamed"][0]["dependents"] = []
    good["observations"]["writes"]["renamed"][0]["dependents_rewritten"] = False

    ok, detail = verifiers.pbi_model_redesign(_ctx(tmp_path, good))
    assert ok is True, detail


def test_a_redesign_may_still_not_touch_a_protected_object(tmp_path, good):
    """R2 keeps M4's protection. A redesign is not a licence to overwrite what was declared
    off limits."""
    good["observations"]["writes"]["touched"].append("Sales Measures[Locked Total]")

    ok, detail = verifiers.pbi_model_redesign(_ctx(tmp_path, good))
    assert ok is False
    assert "protected object" in detail and "Locked Total" in detail


# ========================================================================= R3 — the inert axis
def test_an_axis_where_every_member_is_identical_is_a_fail(tmp_path, good):
    """Inert even when the shared value is not the grand total — it still is not slicing."""
    good["observations"]["slices"]["measures"]["ME Spend"]["Brand"]["values"] = [42.0, 42.0, 42.0]

    ok, detail = verifiers.pbi_model_redesign(_ctx(tmp_path, good))
    assert ok is False
    assert "R3-no-axis-is-inert" in detail
    assert "every member returns the same" in detail


def test_an_axis_that_was_never_sliced_is_unmeasurable_not_a_pass(tmp_path, good):
    """⛔ 'We did not slice that measure by that dimension' is not evidence that it works."""
    good["observations"]["slices"]["measures"]["ME Spend"] = {}

    with pytest.raises(Unmeasurable) as exc:
        verifiers.pbi_model_redesign(_ctx(tmp_path, good))
    assert "never sliced" in str(exc.value)
    assert "ME Spend by Brand" in str(exc.value)


def test_declaring_no_axes_is_unmeasurable(tmp_path, good):
    """Declaring none is not the same as finding none — otherwise the cheapest way to a green
    redesign is to declare nothing, which is exactly the gate this must not be."""
    good["target"]["must_slice_by"] = {}

    with pytest.raises(Unmeasurable) as exc:
        verifiers.pbi_model_redesign(_ctx(tmp_path, good))
    assert "declared as needing to slice" in str(exc.value)


def test_a_single_member_cannot_show_whether_an_axis_slices(tmp_path, good):
    good["observations"]["slices"]["measures"]["ME Spend"]["Brand"]["values"] = [2890054.50]

    with pytest.raises(Unmeasurable, match="single member"):
        verifiers.pbi_model_redesign(_ctx(tmp_path, good))


# ============================================================ the M-contract is not disturbed
def test_the_additive_contract_still_has_exactly_its_twelve_assertions():
    """⚠ Regression guard. `pbi_contract` gained two probes and two target fields for the
    redesign path; `add-measure` must be untouched by all of it."""
    names = [a.name for a in build_contract(PbiTarget(dataset_id="x")).assertions]
    assert len(names) == 12
    assert "M4-additive-manifest" in names
    assert not [n for n in names if n.startswith("R")]


# ================================================================= end to end through the runner
def test_the_runner_reaches_the_redesign_verifier_without_being_handed_one(tmp_path, good):
    """The registry resolution, for the second wired preset."""
    import subprocess

    from factory import runs
    from factory.provider import FakeProvider

    wt = tmp_path / "wt"
    wt.mkdir()
    for args in (["init", "-q"], ["config", "user.email", "t@t"], ["config", "user.name", "t"]):
        subprocess.run(["git", "-C", str(wt), *args], capture_output=True, check=True)
    (wt / "work.txt").write_text("redesigned\n", encoding="utf-8")
    ev = wt / verifiers.EVIDENCE_RELPATH
    ev.parent.mkdir(parents=True, exist_ok=True)
    ev.write_text(json.dumps(good), encoding="utf-8")

    t = wt / "transcript.jsonl"
    t.write_text('{"type":"result"}\n', encoding="utf-8")
    rows = []
    ctl = control.RunController(
        FakeProvider(result=AgentResult(provider="fake", dispatched=True, observable=True,
                                        in_flight=False, returncode=0, transcript=t)),
        worktree=lambda _k: wt, claim=lambda _k: None, release=lambda _k: None,
        verifier=None,
        record=lambda **kw: (rows.append(kw), dict(kw))[1],
        cost=lambda _c: {"basis": runs.MEASURED, "sessions": 1, "input": 5, "output": 7})

    res = ctl.run(control.Ticket(id="GP-318", title="redesign the surface",
                                 type_id="model-redesign"))

    assert res.verdict is Verdict.PASS, res.detail
    tv = [r for r in res.contract.results if r.name == "ticket_verifier"][0]
    assert "PASS=15" in tv.detail, "the verdict did not come from the redesign contract"


def test_the_redesign_preset_tells_the_agent_where_to_leave_evidence():
    preset = presets.by_id("model-redesign")
    prompt = control.team_for(control.Ticket(id="GP-318", title="t"), preset).agents[0].prompt
    assert verifiers.EVIDENCE_RELPATH in prompt
    assert "OMIT anything you did not measure" in prompt
