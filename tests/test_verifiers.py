"""The first wired ticket verifier, and the proof that it can reach every verdict.

`factory/pbi_contract.py` — 12 assertions, ~460 lines — existed complete and unused from the day
it was written. `factory/presets.py` named a check for `add-measure` in prose. Nothing joined
them, so `control.ticket_verifier` reported *"the declaration and the wiring disagree"* on every
run. `factory/verifiers.py` is the join.

⭐ **The load-bearing test here is `test_model_layer_evidence_alone_is_unmeasurable`.** Everything
else guards a boundary around it. An estate that lets DAX parity alone stand in for a validated
dashboard is the estate that shipped GP-293, where every visual rendered "Error loading data"
while the parity check passed.

⛔ **Every verdict this file asserts is also asserted to be reachable in the other direction.** A
verifier that has never been observed to FAIL is a gate that cannot fail, and this repository has
already shipped one of those (`bash-guard.sh`, exit 127, blocking nothing for months while
reporting success).
"""
from __future__ import annotations

import copy
import json
import pathlib

import pytest

from factory import control, presets, verifiers
from factory.contract import Unmeasurable, Verdict
from factory.presets import WIRED
from factory.provider import AgentResult


# --------------------------------------------------------------------------------- the fixture
#: A complete, passing observation set: every probe answered, including the two — render and
#: interact — that only a renderer can answer. Built once and deep-copied per test so a mutation
#: cannot leak between them.
GOOD = {
    "target": {
        "dataset_id": "ds-66151728",
        "dataset_name": "Marketing Model",
        "workspace": "ws-1",
        "environment": "TEST",
        "allow_environments": ["TEST"],
        "additive_only": True,
        "protected_objects": ["Sales Measures[GASP]"],
        "writable_fields": ["Sales Measures[ME Spend]"],
        "anchors": {"ME Spend": 2890054.50},
        "baseline": {"GASP": 82135.29},
        "must_be_blank_not_zero": ["MEP Grounded Spend"],
        "bound_reports": ["rpt-exec"],
        "min_refresh_seconds": 5.0,
        "tolerance": 0.01,
    },
    "observations": {
        "rollback": {"path": "rollback/ds-66151728.tmsl", "captured_before_change": True,
                     "bytes": 41238, "parses": True},
        "writes": {
            "dataset_id": "ds-66151728", "environment": "TEST",
            "fields": [{"field": "Sales Measures[ME Spend]", "appended": True}],
            "renamed": [], "deleted": [],
            "touched": ["Sales Measures[ME Spend]"],
            "added": ["Sales Measures[ME Spend]"],
        },
        "refresh": {"status": "Completed", "duration_seconds": 118.4,
                    "partition_dates": ["2026-08-30"]},
        "dax": {"measures": {"ME Spend": 2890054.50, "GASP": 82135.29},
                "blankness": {"MEP Grounded Spend": "BLANK"}},
        "source": {"measures": {"ME Spend": 2890054.50}},
        "bindings": {"escaped_json_decoded": True,
                     "bound_fields": ["Sales Measures[ME Spend]", "Sales Measures[GASP]"]},
        "render": {"reports": {"rpt-exec": {"visuals_total": 14, "visuals_errored": [],
                                            "visuals_blank": []}}},
        "interact": {"controls": [{"name": "Date slicer", "responded": True},
                                  {"name": "Brand filter", "responded": True}]},
    },
}


def _ctx(tmp_path: pathlib.Path, evidence=None) -> dict:
    """A run context whose worktree holds `evidence` at the agreed path."""
    if evidence is not None:
        p = tmp_path / verifiers.EVIDENCE_RELPATH
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(evidence) if not isinstance(evidence, str) else evidence,
                     encoding="utf-8")
    return {"worktree": tmp_path}


@pytest.fixture()
def good():
    return copy.deepcopy(GOOD)


# ------------------------------------------------------------------------ it can reach a PASS
def test_the_verifier_can_reach_a_pass(tmp_path, good):
    """The positive control. Without it, every refusal below proves only that it always refuses."""
    ok, detail = verifiers.pbi_model_change(_ctx(tmp_path, good))
    assert ok is True, detail
    assert "PASS=12" in detail


# ------------------------------------------------------------------------ it can reach a FAIL
def test_a_wrong_anchor_is_a_fail_and_names_the_measure(tmp_path, good):
    """M6. The change did not produce the number it was supposed to produce."""
    good["observations"]["dax"]["measures"]["ME Spend"] = 2890000.00

    ok, detail = verifiers.pbi_model_change(_ctx(tmp_path, good))
    assert ok is False
    assert "M6-anchors-hold" in detail
    assert "2890000" in detail and "2890054.5" in detail


def test_an_out_of_scope_measure_that_moved_is_a_fail(tmp_path, good):
    """M7 — the regression check. GASP is in `baseline`; this change must not move it."""
    good["observations"]["dax"]["measures"]["GASP"] = 91000.00

    ok, detail = verifiers.pbi_model_change(_ctx(tmp_path, good))
    assert ok is False
    assert "M7-no-regression" in detail
    assert "GASP" in detail


def test_a_rollback_captured_after_the_change_is_a_fail(tmp_path, good):
    """M1. A rollback saved afterwards is a copy of the damage."""
    good["observations"]["rollback"]["captured_before_change"] = False

    ok, detail = verifiers.pbi_model_change(_ctx(tmp_path, good))
    assert ok is False
    assert "M1-rollback-captured-first" in detail


def test_a_false_zero_is_a_fail(tmp_path, good):
    """M8. 17 months of literal $0.00 where the source reports nothing — GP-318's B26.

    A 0 is a measurement claim about the client's business. Absence is not zero.
    """
    good["observations"]["dax"]["blankness"]["MEP Grounded Spend"] = "ZERO"

    ok, detail = verifiers.pbi_model_change(_ctx(tmp_path, good))
    assert ok is False
    assert "M8-absence-renders-blank" in detail


def test_writing_a_protected_object_is_a_fail(tmp_path, good):
    """M4. A TOM rename does not rewrite dependent DAX, and this dataset has live reports bound."""
    good["observations"]["writes"]["touched"].append("Sales Measures[GASP]")

    ok, detail = verifiers.pbi_model_change(_ctx(tmp_path, good))
    assert ok is False
    assert "M4-additive-manifest" in detail


# --------------------------------------------------------- ⭐ it refuses the consumer-layer gap
def test_model_layer_evidence_alone_is_unmeasurable(tmp_path, good):
    """⭐ THE ONE THAT MATTERS. DAX parity is not a validated dashboard.

    Strip the renderer and interaction observations and keep every model-layer fact perfect. The
    verdict must be UNMEASURABLE, never PASS: on GP-293 a repoint passed DAX parity while every
    visual rendered "Error loading data", because server-side data paths, name/ID resolution,
    RBAC and caching all fail AFTER the query succeeds.

    If this ever returns True, the contract has quietly dropped the two assertions only a
    renderer can make, and it is certifying the wrong layer.
    """
    del good["observations"]["render"]
    del good["observations"]["interact"]

    with pytest.raises(Unmeasurable) as exc:
        verifiers.pbi_model_change(_ctx(tmp_path, good))

    assert "M10-every-visual-paints" in str(exc.value)
    assert "M11-controls-respond" in str(exc.value)


def test_a_report_with_a_broken_visual_is_a_fail_not_unmeasurable(tmp_path, good):
    """And when the renderer IS wired, a broken visual is a failure — the other half of M10.

    Without this, `test_model_layer_evidence_alone_is_unmeasurable` would be satisfied by a
    render probe that can only ever refuse.
    """
    good["observations"]["render"]["reports"]["rpt-exec"]["visuals_errored"] = ["Spend by Brand"]

    ok, detail = verifiers.pbi_model_change(_ctx(tmp_path, good))
    assert ok is False
    assert "M10-every-visual-paints" in detail


def test_an_inert_slicer_is_a_fail(tmp_path, good):
    """M11. A silent no-op filter is a finding, never an acceptable default."""
    good["observations"]["interact"]["controls"][1]["responded"] = False

    ok, detail = verifiers.pbi_model_change(_ctx(tmp_path, good))
    assert ok is False
    assert "M11-controls-respond" in detail
    assert "Brand filter" in detail


# ------------------------------------------------------- missing evidence is NOT a failed ticket
def test_a_missing_evidence_file_is_unmeasurable_not_fail(tmp_path):
    """⛔ The distinction the whole repository exists to protect.

    An agent that left no evidence has not been observed to fail. Reporting FAIL here would
    publish "the client's work is broken" on the strength of our own paperwork being absent —
    and it is the same defect F83 recorded, where an unobserved run was reported as an agent
    that did nothing.
    """
    with pytest.raises(Unmeasurable) as exc:
        verifiers.pbi_model_change(_ctx(tmp_path))
    assert verifiers.EVIDENCE_RELPATH in str(exc.value)


def test_evidence_that_does_not_parse_is_unmeasurable(tmp_path):
    with pytest.raises(Unmeasurable, match="does not parse as JSON"):
        verifiers.pbi_model_change(_ctx(tmp_path, "{not json at all"))


def test_evidence_naming_no_dataset_id_is_unmeasurable(tmp_path, good):
    """Identity is by ID, never by matching values — two datasets can hold identical numbers."""
    good["target"].pop("dataset_id")
    with pytest.raises(Unmeasurable, match="dataset_id"):
        verifiers.pbi_model_change(_ctx(tmp_path, good))


def test_an_unknown_target_field_is_unmeasurable_not_a_crash(tmp_path, good):
    good["target"]["some_field_that_does_not_exist"] = True
    with pytest.raises(Unmeasurable, match="does not describe a PbiTarget"):
        verifiers.pbi_model_change(_ctx(tmp_path, good))


# --------------------------------------------------------- ⭐ ERROR must not decay to UNMEASURABLE
def test_an_instrument_that_raises_is_error_not_unmeasurable(tmp_path, good):
    """⛔ TTCN-3's lattice, preserved across the fold.

    A probe that *declines* to look is UNMEASURABLE — wire the instrument. Our own apparatus
    falling over is ERROR — the run is untrustworthy. `_fold` must not flatten the second into
    the first on its way out, which it would do if `ApparatusError` subclassed `Unmeasurable`.
    """
    # A duration that is text rather than a number. The probe answers, so nothing DECLINES to
    # look; M5 then compares it against a float and our own instrument raises TypeError.
    good["observations"]["refresh"]["duration_seconds"] = "about two minutes"

    with pytest.raises(verifiers.ApparatusError) as exc:
        verifiers.pbi_model_change(_ctx(tmp_path, good))
    assert not isinstance(exc.value, Unmeasurable), \
        "ApparatusError must not be an Unmeasurable, or ERROR silently becomes UNMEASURABLE"


def test_the_run_contract_reports_error_for_a_broken_instrument(tmp_path, good):
    """The same thing observed one layer up, where it actually matters."""
    good["observations"]["refresh"]["duration_seconds"] = "about two minutes"
    preset = presets.by_id("add-measure")

    res = control.assertions(preset, verifiers.for_type("add-measure")).run(_ctx(tmp_path, good))
    tv = [r for r in res.results if r.name == "ticket_verifier"][0]
    assert tv.verdict is Verdict.ERROR, tv.detail


# ------------------------------------------------------------------ the registry and the claim
def test_a_preset_may_not_claim_wired_without_a_callable():
    """⛔ Derived, not listed. `verifier_state=WIRED` is a claim; a REGISTRY entry is a mechanism.

    Checked in both directions. `ui-control` claimed WIRED for the life of the preset table with
    nothing behind it (F87), so every run of it reported "declares a WIRED verifier but the
    controller was given no callable" — a promise the code could not keep, and one no test asked
    about.
    """
    claimed = {p.type_id for p in presets.PRESETS if p.verifier_state == WIRED}
    registered = set(verifiers.REGISTRY)

    assert claimed - registered == set(), (
        f"preset(s) claim a WIRED verifier with no callable in verifiers.REGISTRY: "
        f"{sorted(claimed - registered)}. Either wire it or drop the row to AVAILABLE.")
    assert registered - claimed == set(), (
        f"verifiers.REGISTRY holds callable(s) for type(s) whose preset does not say WIRED: "
        f"{sorted(registered - claimed)}. The controller would run a check the table denies.")


def test_every_registered_type_is_a_real_preset():
    known = {p.type_id for p in presets.PRESETS}
    assert set(verifiers.REGISTRY) <= known, (
        f"registry names ticket type(s) no preset defines: {sorted(set(verifiers.REGISTRY) - known)}")


def test_for_type_returns_none_rather_than_raising():
    assert verifiers.for_type("dimension-gap") is None
    assert verifiers.for_type("") is None
    assert verifiers.for_type(None) is None


# -------------------------------------------------------- the controller actually reaches it
def _dispatched(tmp_path) -> AgentResult:
    t = tmp_path / "transcript.jsonl"
    t.write_text('{"ok": true}\n', encoding="utf-8")
    return AgentResult(provider="fake", dispatched=True, observable=True, in_flight=False,
                       returncode=0, transcript=t, detail="")


def test_the_controller_resolves_the_verifier_from_the_registry(tmp_path, good):
    """End to end through `control.assertions`, with nothing injected.

    This is the wiring under test: before it, `self.verifier` was always None and
    `ticket_verifier` reported that the declaration and the wiring disagreed.
    """
    preset = presets.by_id("add-measure")
    ctx = _ctx(tmp_path, good)
    ctx.update(result=_dispatched(tmp_path), changed="1 file changed",
               cost={"basis": "MEASURED", "sessions": 1, "input": 10, "output": 20})

    res = control.assertions(preset, verifiers.for_type(preset.type_id)).run(ctx)
    tv = [r for r in res.results if r.name == "ticket_verifier"][0]
    assert tv.verdict is Verdict.PASS, tv.detail
    assert res.verdict is Verdict.PASS, res.summary()


def test_without_the_registry_the_same_run_is_unmeasurable(tmp_path, good):
    """⛔ The negative control for the wiring itself.

    Same preset, same perfect evidence, no callable — the exact state every run was in before
    this change. It must NOT pass. If this ever goes green, `ticket_verifier` has stopped
    depending on there being a verifier at all, and the run contract has lost the only assertion
    that is about the client's problem rather than the harness.
    """
    preset = presets.by_id("add-measure")
    ctx = _ctx(tmp_path, good)
    ctx.update(result=_dispatched(tmp_path), changed="1 file changed",
               cost={"basis": "MEASURED", "sessions": 1, "input": 10, "output": 20})

    res = control.assertions(preset, None).run(ctx)
    tv = [r for r in res.results if r.name == "ticket_verifier"][0]
    assert tv.verdict is Verdict.UNMEASURABLE
    assert "given no callable" in tv.detail


# ------------------------------------------- ⭐ the wiring line itself, driven through the runner
@pytest.fixture()
def worktree_with_evidence(tmp_path, good):
    """A real git checkout that also holds the agent's verification evidence."""
    import subprocess
    wt = tmp_path / "wt"
    wt.mkdir()
    for args in (["init", "-q"], ["config", "user.email", "t@t"], ["config", "user.name", "t"]):
        subprocess.run(["git", "-C", str(wt), *args], capture_output=True, check=True)
    (wt / "work.txt").write_text("the agent changed this\n", encoding="utf-8")
    ev = wt / verifiers.EVIDENCE_RELPATH
    ev.parent.mkdir(parents=True, exist_ok=True)
    ev.write_text(json.dumps(good), encoding="utf-8")
    return wt


def _runner(wt, verifier=None):
    from factory import runs
    from factory.provider import FakeProvider
    t = wt / "transcript.jsonl"
    t.write_text('{"type":"result"}\n', encoding="utf-8")
    fake = FakeProvider(result=AgentResult(
        provider="fake", dispatched=True, observable=True, in_flight=False, returncode=0,
        transcript=t, detail=""))
    rows = []
    return rows, control.RunController(
        fake,
        worktree=lambda _key: wt,
        claim=lambda _key: None,
        release=lambda _key: None,
        verifier=verifier,
        record=lambda **kw: (rows.append(kw), dict(kw))[1],
        cost=lambda _cwd: {"basis": runs.MEASURED, "sessions": 1, "input": 5, "output": 7},
    )


def test_the_runner_finds_its_verifier_without_being_handed_one(worktree_with_evidence):
    """⭐ THE WIRING. `RunController(verifier=None)` must still reach the registry.

    This is the line the whole change turns on — `self.verifier or verifiers.for_type(...)`. The
    CLI and the tracker both construct the controller without a verifier, so if the fallback goes
    away, every real dispatch silently returns to UNMEASURABLE while every test that injects one
    keeps passing. Injection is what the other tests use; nothing but this exercises the default.
    """
    rows, ctl = _runner(worktree_with_evidence, verifier=None)

    res = ctl.run(control.Ticket(id="gp-401", title="add ME Spend", type_id="add-measure"))

    assert res.verdict is Verdict.PASS, res.detail
    tv = [r for r in res.contract.results if r.name == "ticket_verifier"][0]
    assert tv.verdict is Verdict.PASS
    assert "PASS=12" in tv.detail, "the run's verdict did not come from the M1-M12 contract"
    assert rows and rows[0]["outcome"] == "PASS"


def test_the_runner_reports_the_ticket_wrong_when_the_evidence_says_so(worktree_with_evidence,
                                                                      good):
    """And the same path can FAIL — otherwise the test above only proves it can say yes."""
    good["observations"]["dax"]["measures"]["ME Spend"] = 1.0
    (worktree_with_evidence / verifiers.EVIDENCE_RELPATH).write_text(
        json.dumps(good), encoding="utf-8")

    _rows, ctl = _runner(worktree_with_evidence, verifier=None)
    res = ctl.run(control.Ticket(id="gp-401", title="add ME Spend", type_id="add-measure"))

    assert res.verdict is Verdict.FAIL, res.detail
    tv = [r for r in res.contract.results if r.name == "ticket_verifier"][0]
    assert "M6-anchors-hold" in tv.detail


# ------------------------------------------------------- the agent must be told its obligation
def test_a_wired_preset_tells_the_agent_where_to_leave_its_evidence():
    """⛔ A verifier the agent cannot satisfy is not a gate, it is a trap.

    `pbi_model_change` adjudicates `.factory/verification.json`. An agent never told to write one
    can only ever produce UNMEASURABLE, while appearing to have failed an obligation nobody
    stated. This asserts the prompt the provider is actually handed, not a design note.
    """
    preset = presets.by_id("add-measure")
    prompt = control.team_for(control.Ticket(id="GP-401", title="t"), preset).agents[0].prompt

    assert verifiers.EVIDENCE_RELPATH in prompt
    assert "OMIT anything you did not measure" in prompt, \
        "the instruction not to invent an observation is the one that keeps the apparatus honest"


def test_an_unwired_preset_does_not_demand_evidence_nothing_will_read():
    """The clause is conditional on purpose: asking for evidence no verifier reads trains an
    agent to produce paperwork, which is how a check becomes a ritual."""
    preset = presets.by_id("dimension-gap")
    prompt = control.team_for(control.Ticket(id="GP-402", title="t"), preset).agents[0].prompt

    assert verifiers.EVIDENCE_RELPATH not in prompt
    assert "nothing downstream can confirm your work" in prompt
