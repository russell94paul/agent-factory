"""Client Review readiness — the record outranks the prose, and the gate can refuse.

Every test here exists because of one measured defect, found 2026-09-01 against the real
narrative and the live task store:

    the yaml said the data-cartography milestone was BLOCKED and five design items
    NOT_STARTED, while `.data/tasks.jsonl` — the same store this module already reads for
    evidence grounding — recorded R3, D1, D2, D3 and D4 all closed with evidence.

Ten hand-typed statuses would have rendered to a client as fact. The raw measurement is at
``docs/evidence/client-review-readiness-2026-09-01/narrative-drift.json``.

Each check below is paired with a negative control. A drift detector that always fires reports
nothing, and a gate that cannot pass is not a gate.
"""
from __future__ import annotations

import json
import pathlib

import pytest

from factory import client_review as cr
from factory import tasks as T
from factory.client_review_render import render_html


# --------------------------------------------------------------------------------------------
# Fixtures
# --------------------------------------------------------------------------------------------

@pytest.fixture()
def root(tmp_path):
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "real.md").write_text("evidence body", encoding="utf-8")
    return tmp_path


@pytest.fixture()
def linked(tmp_path):
    """A mission whose labels resolve: R1 closed with usable evidence, R2 still open."""
    s = T.TaskStore(tmp_path / "linked.jsonl")
    mid = s.create("mission", actor="t")
    r1 = s.create("R1", actor="t", parent=mid)
    s.add_evidence(r1, kind="analysis", ref="docs/real.md", actor="t", basis="MEASURED")
    s.close(r1, actor="t")
    r2 = s.create("R2", actor="t", parent=mid)
    m = tmp_path / "m.json"
    m.write_text(json.dumps({"mission_task": mid, "labels": {"R1": r1, "R2": r2}}),
                 encoding="utf-8")
    return s, m


def _write(tmp_path, doc) -> pathlib.Path:
    y = tmp_path / "review.yaml"                    # json is valid yaml
    y.write_text(json.dumps(doc), encoding="utf-8")
    return y


def _healthy(**over) -> dict:
    """A narrative with nothing wrong with it. Overridden per test to introduce one fault."""
    doc = {
        "intent": {"objective": "one agreed definition of the model"},
        "delivered": [{"id": "D-1", "title": "the reconstruction", "task": "R1",
                       "summary": "what we found", "evidence_refs": ["docs/real.md"]}],
        "evidence": [{"id": "E-1", "type": "analysis", "label": "ledger",
                      "source": "docs/real.md"}],
        "next": [{"id": "N-1", "title": "the next outcome", "task": "R2"}],
    }
    doc.update(over)
    return doc


def _gate(review, status):
    return {c["id"] for c in cr.meeting_gate(review)["checks"] if c["status"] == status}


# --------------------------------------------------------------------------------------------
# 1. A typed status never outranks the append-only record
# --------------------------------------------------------------------------------------------

def test_canonical_state_overrides_a_stale_typed_status(root, tmp_path, linked):
    s, m = linked
    y = _write(tmp_path, {"next": [{"id": "N-1", "title": "map it",
                                    "task": "R1", "status": "BLOCKED"}]})
    review = cr.assemble(y, tasks_path=s.path, mission_path=m, root=root)
    assert review.next[0].status == "DONE"
    assert review.next[0].status_basis == cr.PLAN_DERIVED
    drift = review.diagnostics["narrative_drift"]
    assert [(d["narrative_says"], d["canonical_says"]) for d in drift] == [("BLOCKED", "DONE")]


def test_an_agreeing_typed_status_records_no_drift(root, tmp_path, linked):
    """Negative control. A drift report that always fires reports nothing."""
    s, m = linked
    y = _write(tmp_path, {"next": [{"id": "N-1", "title": "x", "task": "R1", "status": "DONE"}]})
    review = cr.assemble(y, tasks_path=s.path, mission_path=m, root=root)
    assert review.diagnostics["narrative_drift"] == []


def test_an_unlinked_plan_item_renders_but_says_it_is_unverified(root, tmp_path, linked):
    s, m = linked
    y = _write(tmp_path, {"next": [{"id": "N-9", "title": "x", "status": "NOT_STARTED"}]})
    review = cr.assemble(y, tasks_path=s.path, mission_path=m, root=root)
    # It still renders — dropping it would empty the section and read as "nothing planned".
    assert review.next[0].status == "NOT_STARTED"
    assert review.next[0].status_basis == cr.PLAN_NOT_RECORDED
    assert "not verified against the record" in render_html(review)


def test_a_link_the_store_cannot_resolve_publishes_nothing(root, tmp_path, linked):
    """The blind-instrument rule: we could not look, so we do not publish the typed guess."""
    s, m = linked
    y = _write(tmp_path, {"next": [{"id": "N-9", "title": "x", "task": "R9",
                                    "status": "NOT_STARTED"}]})
    review = cr.assemble(y, tasks_path=s.path, mission_path=m, root=root)
    assert review.next[0].status == cr.PLAN_UNKNOWN
    assert review.next[0].status != "NOT_STARTED"
    assert review.next[0].status_basis == cr.PLAN_NOT_RECORDED


def test_a_milestone_spanning_tasks_is_not_done_until_the_last_one_is(root, tmp_path, linked):
    s, m = linked
    y = _write(tmp_path, {"progress": {"milestones": [{"title": "both", "task": ["R1", "R2"]}]}})
    review = cr.assemble(y, tasks_path=s.path, mission_path=m, root=root)
    assert review.progress["milestones"][0]["status"] == "IN_PROGRESS"


def test_a_partly_blind_milestone_is_not_recorded_not_in_progress(root, tmp_path, linked):
    s, m = linked
    y = _write(tmp_path, {"progress": {"milestones": [{"title": "x", "task": ["R1", "R9"]}]}})
    review = cr.assemble(y, tasks_path=s.path, mission_path=m, root=root)
    assert review.progress["milestones"][0]["status"] == cr.PLAN_UNKNOWN


def test_a_milestone_cannot_smuggle_an_unnamed_field_to_the_client(root, tmp_path, linked):
    s, m = linked
    y = _write(tmp_path, {"progress": {"milestones": [
        {"title": "t", "task": "R1", "internal_note": "do not ship"}]}})
    review = cr.assemble(y, tasks_path=s.path, mission_path=m, root=root)
    assert "internal_note" not in review.progress["milestones"][0]
    assert "do not ship" not in render_html(review)


def test_a_blocked_reason_does_not_outlive_the_block(root, tmp_path, linked):
    s, m = linked
    y = _write(tmp_path, {"next": [{"id": "N-1", "title": "x", "task": "R1",
                                    "blocked_reason": "waiting on a rotation"}]})
    review = cr.assemble(y, tasks_path=s.path, mission_path=m, root=root)
    assert review.next[0].status == "DONE"
    assert "waiting on a rotation" not in render_html(review)


# --------------------------------------------------------------------------------------------
# 2. Work that closed and was never written up
# --------------------------------------------------------------------------------------------

def test_a_closed_task_with_no_write_up_is_counted(root, tmp_path, linked):
    s, m = linked
    review = cr.assemble(_write(tmp_path, {}), tasks_path=s.path, mission_path=m, root=root)
    assert [x["label"] for x in review.diagnostics["undeclared_completions"]] == ["R1"]


def test_a_written_up_task_is_not_counted_as_undeclared(root, tmp_path, linked):
    """Negative control for the same instrument."""
    s, m = linked
    y = _write(tmp_path, _healthy())
    review = cr.assemble(y, tasks_path=s.path, mission_path=m, root=root)
    assert review.diagnostics["undeclared_completions"] == []


def test_an_unreadable_store_reports_no_undeclared_work_rather_than_zero(root, tmp_path):
    """A zero from an instrument that could not look is not a measurement — the gate reads
    ``tasks_readable`` for that, and blocks on it, rather than trusting this empty list."""
    review = cr.assemble(_write(tmp_path, {}), tasks_path=None, mission_path=None, root=root)
    assert review.diagnostics["undeclared_completions"] == []
    assert review.diagnostics["tasks_readable"] is False
    assert "canonical_state_readable" in _gate(review, cr.BLOCK)


def test_a_pending_outcome_borrows_wording_a_human_already_wrote(root, tmp_path, linked):
    s, m = linked
    y = _write(tmp_path, {"next": [{"id": "N-1", "task": "R1",
                                    "title": "Map what marketing data exists"}]})
    review = cr.assemble(y, tasks_path=s.path, mission_path=m, root=root)
    pend = [o for o in review.delivered if o.writeup == "PENDING"]
    assert len(pend) == 1
    assert pend[0].title == "Map what marketing data exists"   # not invented
    assert pend[0].summary == ""                               # no conclusion authored
    assert pend[0].business_impact == ""
    assert pend[0].origin == cr.FACTORY_PROPOSED               # never "you asked for this"
    assert pend[0].evidence_refs == ["docs/real.md"]           # derived from the store


def test_no_client_wording_means_no_outcome_is_written_on_a_humans_behalf(root, tmp_path, linked):
    s, m = linked
    review = cr.assemble(_write(tmp_path, {}), tasks_path=s.path, mission_path=m, root=root)
    assert [o for o in review.delivered if o.writeup == "PENDING"] == []


def test_a_pending_outcome_renders_as_explicitly_non_final(root, tmp_path, linked):
    s, m = linked
    y = _write(tmp_path, {"next": [{"id": "N-1", "task": "R1", "title": "Map the data"}]})
    page = render_html(cr.assemble(y, tasks_path=s.path, mission_path=m, root=root))
    assert "AWAITING WRITE-UP" in page
    assert "not being presented as a conclusion" in page


def test_an_internal_task_title_never_reaches_the_page(root, tmp_path, linked):
    """The synthesised entry must borrow client wording, never the engineering task title."""
    s, m = linked
    y = _write(tmp_path, {"next": [{"id": "N-1", "task": "R1", "title": "Map the data"}]})
    review = cr.assemble(y, tasks_path=s.path, mission_path=m, root=root)
    page = render_html(review)
    for item in review.diagnostics["undeclared_completions"]:
        assert item["title"] not in page
        assert item["id"] not in page


def test_evidence_refs_are_derived_from_the_store_when_not_authored(root, tmp_path, linked):
    s, m = linked
    y = _write(tmp_path, {"delivered": [{"id": "D-1", "title": "t", "task": "R1",
                                         "summary": "s", "status": "Complete"}]})
    review = cr.assemble(y, tasks_path=s.path, mission_path=m, root=root)
    assert review.delivered[0].evidence_refs == ["docs/real.md"]
    assert review.delivered[0].grounding == cr.GROUNDED


def test_a_derived_evidence_list_takes_only_rows_with_a_usable_basis(root, tmp_path, linked):
    """An ASSUMED row is not proof and must not land behind "Proof it works".

    The real case, 2026-09-01: D5 closed carrying a ref that was a path plus prose —
    ``docs/.../D5-recommendation.md (see 0a - sign-off and its limits)`` at basis ASSUMED — which
    can never resolve as a filesystem path. Deriving it produced a phantom gate blocker on an
    outcome whose clean DERIVED citation of the same file was already resolving.
    """
    s, m = linked
    r1 = json.loads(m.read_text(encoding="utf-8"))["labels"]["R1"]
    s.add_evidence(r1, kind="note", actor="t", basis="ASSUMED",
                   ref="docs/real.md (see section 0a - sign-off and its limits)")
    y = _write(tmp_path, {"delivered": [{"id": "D-1", "title": "t", "task": "R1",
                                         "summary": "s"}]})
    review = cr.assemble(y, tasks_path=s.path, mission_path=m, root=root)
    assert review.delivered[0].evidence_refs == ["docs/real.md"]
    assert review.diagnostics["unresolved_outcome_evidence"] == []


def test_a_usable_row_is_still_derived(root, tmp_path, linked):
    """Negative control: the basis filter must not drop everything."""
    s, m = linked
    r1 = json.loads(m.read_text(encoding="utf-8"))["labels"]["R1"]
    (root / "docs" / "second.md").write_text("more", encoding="utf-8")
    s.add_evidence(r1, kind="note", actor="t", basis="DERIVED", ref="docs/second.md")
    y = _write(tmp_path, {"delivered": [{"id": "D-1", "title": "t", "task": "R1",
                                         "summary": "s"}]})
    review = cr.assemble(y, tasks_path=s.path, mission_path=m, root=root)
    assert review.delivered[0].evidence_refs == ["docs/real.md", "docs/second.md"]


def test_an_authored_evidence_list_wins_over_the_derived_one(root, tmp_path, linked):
    s, m = linked
    y = _write(tmp_path, {"delivered": [{"id": "D-1", "title": "t", "task": "R1",
                                         "summary": "s", "evidence_refs": ["docs/chosen.md"]}]})
    review = cr.assemble(y, tasks_path=s.path, mission_path=m, root=root)
    assert review.delivered[0].evidence_refs == ["docs/chosen.md"]


# --------------------------------------------------------------------------------------------
# 3. A risk the record shows as closed stops asking the client to act
# --------------------------------------------------------------------------------------------

def test_a_risk_whose_task_closed_is_resolved_and_asks_for_nothing(root, tmp_path, linked):
    s, m = linked
    y = _write(tmp_path, {"risks": [{"id": "RISK-1", "title": "paused", "task": "R1",
                                     "client_action_required": True}]})
    review = cr.assemble(y, tasks_path=s.path, mission_path=m, root=root)
    assert review.risks[0].state == "RESOLVED"
    assert review.risks[0].state_basis == cr.PLAN_DERIVED
    assert review.risks[0].client_action_required is False
    page = render_html(review)
    assert "RESOLVED" in page
    # It is kept on the page. Deleting it would erase the fact that we found and cleared it.
    assert "paused" in page


def test_a_risk_whose_task_is_open_stays_active(root, tmp_path, linked):
    s, m = linked
    y = _write(tmp_path, {"risks": [{"id": "RISK-1", "title": "open one", "task": "R2",
                                     "client_action_required": True}]})
    review = cr.assemble(y, tasks_path=s.path, mission_path=m, root=root)
    assert review.risks[0].state == "ACTIVE"
    assert review.risks[0].client_action_required is True


def test_an_unlinked_risk_is_never_silently_resolved(root, tmp_path, linked):
    s, m = linked
    y = _write(tmp_path, {"risks": [{"id": "RISK-1", "title": "x",
                                     "client_action_required": True}]})
    review = cr.assemble(y, tasks_path=s.path, mission_path=m, root=root)
    assert review.risks[0].state == "ACTIVE"
    assert review.risks[0].state_basis == cr.PLAN_NOT_RECORDED
    assert review.risks[0].client_action_required is True


# --------------------------------------------------------------------------------------------
# 4. The meeting gate — every check must be capable of firing AND of not firing
# --------------------------------------------------------------------------------------------

def test_the_gate_passes_a_review_with_nothing_wrong(root, tmp_path, linked):
    """The load-bearing negative control. A gate that cannot pass tells the operator nothing."""
    s, m = linked
    review = cr.assemble(_write(tmp_path, _healthy()), tasks_path=s.path,
                         mission_path=m, root=root)
    g = cr.meeting_gate(review)
    assert [c for c in g["checks"] if c["status"] == cr.BLOCK] == []
    assert g["verdict"] in (cr.GATE_READY, cr.GATE_READY_WITH_WARNINGS)


def test_the_gate_blocks_on_a_stale_typed_status(root, tmp_path, linked):
    s, m = linked
    doc = _healthy(next=[{"id": "N-1", "title": "x", "task": "R1", "status": "NOT_STARTED"}])
    review = cr.assemble(_write(tmp_path, doc), tasks_path=s.path, mission_path=m, root=root)
    assert "narrative_matches_canonical_state" in _gate(review, cr.BLOCK)
    assert cr.meeting_gate(review)["verdict"] == cr.GATE_NOT_READY


def test_the_gate_blocks_when_a_cited_artefact_is_not_in_this_checkout(root, tmp_path, linked):
    """The 2026-09-01 case: D2–D4 evidence existed only in another session's worktree, so four
    outcomes degraded to CLAIMED and nothing named the files. A degrade is not a diagnosis."""
    s, m = linked
    doc = _healthy(delivered=[{"id": "D-1", "title": "t", "task": "R1", "summary": "s",
                               "evidence_refs": ["docs/not-in-this-checkout.md"]}])
    review = cr.assemble(_write(tmp_path, doc), tasks_path=s.path, mission_path=m, root=root)
    assert "cited_evidence_resolves" in _gate(review, cr.BLOCK)
    detail = [c["detail"] for c in cr.meeting_gate(review)["checks"]
              if c["id"] == "cited_evidence_resolves"][0]
    assert "docs/not-in-this-checkout.md" in detail      # it names the file, not just the count


def test_the_gate_blocks_when_completed_work_has_no_write_up(root, tmp_path, linked):
    s, m = linked
    doc = _healthy(delivered=[], next=[{"id": "N-1", "title": "Map the data", "task": "R1"}])
    review = cr.assemble(_write(tmp_path, doc), tasks_path=s.path, mission_path=m, root=root)
    assert "completed_work_is_written_up" in _gate(review, cr.BLOCK)


def test_the_gate_blocks_when_a_status_has_no_basis(root, tmp_path, linked):
    s, m = linked
    doc = _healthy(next=[{"id": "N-1", "title": "unlinked"}])
    review = cr.assemble(_write(tmp_path, doc), tasks_path=s.path, mission_path=m, root=root)
    assert "no_status_rendered_without_a_basis" in _gate(review, cr.BLOCK)


def test_the_gate_blocks_on_an_empty_required_section(root, tmp_path, linked):
    s, m = linked
    doc = _healthy(evidence=[])
    review = cr.assemble(_write(tmp_path, doc), tasks_path=s.path, mission_path=m, root=root)
    assert "required_sections_populated" in _gate(review, cr.BLOCK)


def test_the_gate_blocks_when_the_record_could_not_be_read(root, tmp_path):
    review = cr.assemble(_write(tmp_path, {}), tasks_path=None, mission_path=None, root=root)
    blocked = _gate(review, cr.BLOCK)
    assert "canonical_state_readable" in blocked
    assert "freshness" in blocked
    assert cr.meeting_gate(review)["verdict"] == cr.GATE_NOT_READY


def test_the_gate_warns_rather_than_blocks_on_a_resolved_risk(root, tmp_path, linked):
    """A resolved risk is presenter information, not a defect. It must not kill the meeting."""
    s, m = linked
    doc = _healthy(risks=[{"id": "RISK-1", "title": "cleared", "task": "R1"}])
    review = cr.assemble(_write(tmp_path, doc), tasks_path=s.path, mission_path=m, root=root)
    assert "risks_still_current" in _gate(review, cr.WARN)
    assert "risks_still_current" not in _gate(review, cr.BLOCK)


def test_the_gate_is_operator_only_and_reaches_no_page(root, tmp_path, linked):
    s, m = linked
    review = cr.assemble(_write(tmp_path, _healthy()), tasks_path=s.path,
                         mission_path=m, root=root)
    page = render_html(review)
    for c in cr.meeting_gate(review)["checks"]:
        assert c["id"] not in page


def test_the_gate_exit_code_is_one_when_not_ready(tmp_path, root, linked):
    """The CLI contract the one-command path depends on."""
    s, m = linked
    doc = _healthy(next=[{"id": "N-1", "title": "x", "task": "R1", "status": "NOT_STARTED"}])
    y = _write(tmp_path, doc)
    assert cr.main([str(y), "--tasks", str(s.path), "--mission", str(m),
                    "--root", str(root), "--gate"]) == 1


def test_the_gate_exit_code_is_zero_when_ready(tmp_path, root, linked):
    s, m = linked
    y = _write(tmp_path, _healthy())
    assert cr.main([str(y), "--tasks", str(s.path), "--mission", str(m),
                    "--root", str(root), "--gate"]) == 0
