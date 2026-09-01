"""Delivery #001 as an executable fixture.

Two halves, and the second is the load-bearing one.

The first half asserts that the real compiled record still says what the forensic reconstruction
established. These are regression tests over *meaning*, not over formatting — they use the real
`.data/tasks.jsonl` and the real authored fixture, so a generator change that quietly drops a
finding fails here.

The second half feeds the compiler **deliberately malformed input** and asserts it refuses. A
validator that has never been shown refusing is a validator nobody has tested, and this repo has
paid for that distinction repeatedly. Every negative control below was watched failing before it
was written down.
"""
from __future__ import annotations

import copy
import pathlib

import pytest

from factory import assertions as A
from factory import case_study as CS
from factory import context as CTX
from factory import forensic_source as FS
from factory import projection as P

ROOT = pathlib.Path(__file__).resolve().parent.parent
NARRATIVE = ROOT / "missions" / "delivery-001" / "case-study.yaml"
TASKS = ROOT / ".data" / "tasks.jsonl"
MISSION = ROOT / ".data" / "missions" / "marketing-model-reconstruction-v1.json"
PROSE = ROOT / "docs" / "case-studies" / "delivery-001-marketing-model.md"


@pytest.fixture(scope="module")
def study():
    return CS.assemble(NARRATIVE, tasks_path=TASKS, mission_path=MISSION, root=ROOT)


def _issue(study, iid):
    for i in study.issues:
        if i.id == iid:
            return i
    raise AssertionError(f"issue {iid} is not in the compiled record")


def _kpi(study, kid):
    for k in study.kpis:
        if k.id == kid:
            return k
    raise AssertionError(f"kpi {kid} is not in the compiled record")


def _doc():
    import yaml
    return yaml.safe_load(NARRATIVE.read_text(encoding="utf-8"))


def _compile(doc, tmp_path, name="d.yaml"):
    import yaml
    p = tmp_path / name
    p.write_text(yaml.safe_dump(doc, allow_unicode=True, sort_keys=False), encoding="utf-8")
    return CS.assemble(p, tasks_path=TASKS, mission_path=MISSION, root=ROOT)


# =============================================================================================
# 1-11 — the Delivery #001 assertions the gate named
# =============================================================================================

def test_1_wrong_field_lookup_and_duplicate_tasks_survive(study):
    i = _issue(study, "M-01")
    assert i.track == CS.FACTORY_MISSION
    assert i.escape_distance == 4 and i.potential_escape == 0
    assert "INSTRUMENTATION_GAP" in i.root_causes
    assert i.basis == A.MEASURED


def test_2_completion_counts_declared_tasks_not_duplicated_children(study):
    """The mission record declares 8 tasks; the store holds 10 children of the mission task.

    The client-facing basis is the declared set. This asserts the case study reports the same
    population the client review does, so the two artifacts cannot quote different progress.
    """
    assert study.diagnostics["mission_declared_tasks"] == 8
    k = _kpi(study, "K-5")
    assert k.measurability == CS.MEASURABLE_NOW
    assert k.value == "50", "4 of the 8 declared tasks are done, not 4 of 10 children"


def test_3_corrected_metric_hierarchy_is_recorded_as_refuted(study):
    i = _issue(study, "M-03")
    assert "STALE_CONTEXT" in i.root_causes
    assert i.escape_distance == 1, "marking it 'verify' held it to one boundary"
    assert i.still_open is False


def test_4_mer_contradiction_is_preserved_not_resolved(study):
    i = _issue(study, "H3")
    assert i.basis == A.CONTRADICTORY
    assert len(i.sides) >= 2, "a contradiction naming one position has been resolved silently"
    positions = {s["position"] for s in i.sides}
    assert len(positions) == 2, "both directions of the formula must survive compilation"


def test_5_source_clone_ambiguity_is_not_claimed_as_solved(study):
    i = _issue(study, "H4")
    cf = A.Counterfactual(**i.counterfactual)
    assert cf.capability == "Source Cartography"
    assert cf.maturity == A.IMPLEMENTED_NOT_EXERCISED
    assert not cf.is_observed, "cartography did not run before the defect and must not read as proven"


def test_6_knowledge_available_but_not_consumed_is_the_largest_pattern(study):
    p = next(p for p in study.patterns if p.name == "KNOWLEDGE_AVAILABLE_BUT_NOT_CONSUMED")
    assert p.count == 8
    assert "M-05" in p.issue_ids, "the deny-list recurrence belongs to this pattern"
    assert "M-13" in p.issue_ids, "so does the Artifact Generator reproducing it"


def test_7_stale_superseded_task_ids_in_artifact_headers_still_open(study):
    i = _issue(study, "M-02")
    assert i.still_open is True
    assert "MISSING_PROVENANCE" in i.root_causes


def test_8_scope_that_could_not_be_seen_is_recorded(study):
    i = _issue(study, "M-07")
    assert "MANUAL_HANDOFF" in i.root_causes
    cf = A.Counterfactual(**i.counterfactual)
    assert cf.strength == A.WOULD_BLOCK and cf.maturity == A.PROPOSED


def test_9_parallelism_is_a_blind_instrument_not_a_number(study):
    k = _kpi(study, "K-10")
    assert k.measurability == CS.BLIND_INSTRUMENT
    assert k.value is None, "three claims sharing one pid is not a measurement of concurrency"


def test_10_routing_instrumentation_is_not_recorded_never_zero(study):
    k = _kpi(study, "K-9")
    assert k.measurability == CS.REQUIRES_NEW_INSTRUMENTATION
    assert k.value is None
    assert k.basis == A.NOT_RECORDED


def test_11_exercised_capabilities_are_separable_from_simulated_ones(study):
    cfs = [A.Counterfactual(**c) for c in
           [x.counterfactual for x in study.issues + study.scenes if x.counterfactual]]
    observed = [c for c in cfs if c.is_observed]
    simulated = [c for c in cfs if not c.is_observed]
    assert observed and simulated, "the record must contain both, or the distinction is untested"
    assert all(c.basis == A.SIMULATED for c in simulated)
    assert all(c.exercised_proof for c in observed), "EXERCISED must name proof it ran"
    names = {c.capability for c in observed}
    assert any("Client Review" in n for n in names), \
        "the Client Review actually ran on this delivery and should be the exercised example"


# =============================================================================================
# Negative controls — the validator, watched refusing
# =============================================================================================

def test_a_dangling_anchor_fails_the_build(tmp_path):
    doc = _doc()
    doc["issues"][0]["evidence_refs"] = [
        "docs/case-studies/delivery-001-marketing-model.md#no-such-anchor"]
    with pytest.raises(FS.SourceError, match="anchor not declared"):
        _compile(doc, tmp_path)


def test_a_missing_file_reference_fails_the_build(tmp_path):
    doc = _doc()
    doc["issues"][0]["evidence_refs"] = ["docs/case-studies/does-not-exist.md"]
    with pytest.raises(FS.SourceError, match="file does not exist"):
        _compile(doc, tmp_path)


def test_a_duplicate_anchor_in_the_prose_is_refused(tmp_path):
    p = tmp_path / "prose.md"
    p.write_text("# A\n<!-- anchor: dup -->\n# B\n<!-- anchor: dup -->\n", encoding="utf-8")
    with pytest.raises(FS.SourceError, match="duplicate anchor"):
        FS.read(p)


def test_duplicate_record_ids_are_refused(tmp_path):
    doc = _doc()
    doc["issues"].append(copy.deepcopy(doc["issues"][0]))
    with pytest.raises(FS.SourceError, match="duplicate id"):
        _compile(doc, tmp_path)


def test_a_cross_reference_to_a_missing_record_is_refused(tmp_path):
    doc = _doc()
    doc["scenes"][0]["step_ref"] = "T-NOPE"
    with pytest.raises(FS.SourceError, match="cross-reference"):
        _compile(doc, tmp_path)


def test_exercised_without_proof_it_ran_is_refused(tmp_path):
    doc = _doc()
    for i in doc["issues"]:
        if (i.get("counterfactual") or {}).get("maturity") == "EXERCISED":
            del i["counterfactual"]["exercised_proof"]
            break
    with pytest.raises(CS.CaseStudyError, match="exercised_proof"):
        _compile(doc, tmp_path)


def test_a_capability_claiming_code_must_name_it():
    with pytest.raises(A.AssertionError_, match="names none"):
        A.Counterfactual(capability="X", strength=A.WOULD_BLOCK,
                         maturity=A.IMPLEMENTED_NOT_EXERCISED)


def test_a_simulated_capability_cannot_declare_itself_measured():
    cf = A.Counterfactual(capability="X", strength=A.WOULD_BLOCK, maturity=A.PROPOSED,
                          basis=A.MEASURED)
    assert cf.basis == A.SIMULATED, "the authored file does not get to decide this"


def test_a_counterfactual_cannot_be_rendered_as_an_outcome():
    """The anti-flattening rule, asserted structurally rather than visually."""
    cf = A.Counterfactual(capability="X", strength=A.WOULD_WARN, maturity=A.PROPOSED)
    assert not hasattr(cf, "status"), "a counterfactual with a status could enter the outcome path"
    assert not hasattr(cf, "grounding")


def test_a_contradiction_with_one_side_is_refused(tmp_path):
    doc = _doc()
    for i in doc["issues"]:
        if i.get("basis") == "CONTRADICTORY":
            i["sides"] = i["sides"][:1]
            break
    with pytest.raises(CS.CaseStudyError, match="fewer than two sides"):
        _compile(doc, tmp_path)


def test_an_unmeasured_kpi_carrying_a_number_is_refused(tmp_path):
    doc = _doc()
    for k in doc["kpis"]:
        if k["measurability"] == "NOT_RECORDED":
            k["value"] = "0"
            break
    with pytest.raises(CS.CaseStudyError, match="authored estimate"):
        _compile(doc, tmp_path)


def test_a_single_track_case_study_is_refused(tmp_path):
    doc = _doc()
    keep = {i["id"] for i in doc["issues"] if i["track"] == "CLIENT_DELIVERY"}
    doc["issues"] = [i for i in doc["issues"] if i["id"] in keep]
    # Patterns cross-reference issues, and that integrity check fires first. Strip the dangling
    # references so the test exercises the track rule rather than the cross-reference rule.
    for p in doc["patterns"]:
        p["issue_ids"] = [x for x in p["issue_ids"] if x in keep]
    with pytest.raises(CS.CaseStudyError, match="advertisement, not a forensic account"):
        _compile(doc, tmp_path)


def test_a_scene_without_exactly_one_actual_choice_is_refused(tmp_path):
    doc = _doc()
    for c in doc["scenes"][0]["choices"]:
        c["was_actual"] = True
    with pytest.raises(CS.CaseStudyError, match="was_actual"):
        _compile(doc, tmp_path)


def test_current_without_a_checked_date_is_refused(tmp_path):
    doc = _doc()
    for s in doc["timeline"]:
        if s.get("status") == "CURRENT":
            s["checked"] = ""
            break
    with pytest.raises(CS.CaseStudyError, match="CURRENT with no"):
        _compile(doc, tmp_path)


def test_superseded_without_naming_what_superseded_it_is_refused(tmp_path):
    doc = _doc()
    for s in doc["timeline"]:
        if s.get("status") == "SUPERSEDED":
            s["superseded_by"] = ""
            break
    with pytest.raises(CS.CaseStudyError, match="names nothing that superseded it"):
        _compile(doc, tmp_path)


def test_an_undeclared_field_is_refused_rather_than_dropped(tmp_path):
    doc = _doc()
    doc["issues"][0]["severity_score"] = 9
    with pytest.raises(CS.CaseStudyError, match="unknown field"):
        _compile(doc, tmp_path)


def test_scene_order_must_be_contiguous(tmp_path):
    doc = _doc()
    doc["scenes"][0]["order"] = 99
    with pytest.raises(CS.CaseStudyError, match="scene order"):
        _compile(doc, tmp_path)


# =============================================================================================
# The boundary, and the promotion gate
# =============================================================================================

def test_diagnostics_has_no_allow_list_and_never_projects(study):
    assert "diagnostics" not in CS.CASE_STUDY_SAFE
    assert "diagnostics" not in study.to_dict()
    assert study.diagnostics, "the operator data exists — it is withheld, not absent"


def test_adding_a_field_to_the_view_model_does_not_publish_it(study):
    row = dict(study.to_dict()["issues"][0])
    row["internal_note"] = "operator only"
    assert "internal_note" not in P.safe(CS.ARTIFACT, "issues", row)


def test_the_leak_backstop_raises_rather_than_redacting():
    with pytest.raises(P.LeakError):
        P.safe(CS.ARTIFACT, "issues", {"id": "X", "title": "the password is hunter2"})


def test_documented_never_enters_the_promotion_gate():
    """The single most dangerous edit anyone could make to assertions.py."""
    assert A.PROMOTABLE == ("MEASURED", "DERIVED")
    assert A.DOCUMENTED not in A.PROMOTABLE
    assert A.SIMULATED not in A.PROMOTABLE


def test_reconciliation_reports_divergence_rather_than_republishing(study):
    """The narrative is a point-in-time account and the store moves under it."""
    rec = study.reconciliation
    assert rec["status"] in ("OK", "DIVERGED")
    for row in rec["rows"]:
        assert row["verdict"] in (CTX.CURRENT, CTX.SUPERSEDED, "UNAVAILABLE")
        if row["verdict"] == CTX.SUPERSEDED:
            assert row["claimed"] != row["actual"], "a divergence must show both values"


# =============================================================================================
# Renderer contract — inherited from the client review, because a second renderer must meet it too
# =============================================================================================

def test_the_generated_page_makes_no_external_requests(study):
    from factory.case_study_render import render_html
    html = render_html(study)
    for token in ("http://", "https://", "//fonts.", "<link", "src="):
        assert token not in html, f"{token!r} would make the page depend on something external"


def test_the_page_renders_without_a_task_store(tmp_path):
    """Degrade honestly: no store means UNAVAILABLE freshness, not a crash."""
    from factory.case_study_render import render_html
    cs = CS.assemble(NARRATIVE, tasks_path=tmp_path / "nope.jsonl",
                     mission_path=MISSION, root=ROOT)
    assert cs.meta["freshness_state"] == A.UNAVAILABLE
    assert cs.meta["basis"] == A.NOT_RECORDED
    assert render_html(cs)


def test_the_walkthrough_needs_no_javascript(study):
    """Static degradation: the reveal path must be CSS + native disclosure only."""
    from factory.case_study_render import render_html
    html = render_html(study)
    body = html.split("<script>")[0]
    from factory.case_study_render import e as esc
    for s in study.scenes:
        assert f'id="scene-{s.id}"' in body
        assert esc(s.actual_outcome)[:40] in body, "the actual outcome must be in the DOM already"
        for c in s.choices:
            assert esc(c["consequence"])[:40] in body,                 "every consequence must be present without JS"


def test_an_unmeasured_kpi_renders_its_state_not_a_zero(study):
    from factory.case_study_render import render_html
    html = render_html(study)
    assert "BLIND_INSTRUMENT" in html
    assert "REQUIRES_NEW_INSTRUMENTATION" in html
