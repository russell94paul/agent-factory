"""The four evidence classes — and the negative control for each.

Every control in this repo ships with proof it can refuse. A slot that always says SATISFIED is
the free-string `kind` field with extra steps.
"""
from __future__ import annotations

import pytest

from factory import evidence as ev
from factory.tasks import EvidenceRequired, TaskStore


# --------------------------------------------------------------------------- the class itself

def test_an_unknown_class_is_refused_not_bucketed():
    """A typo must raise. Silently creating a fifth bucket makes a mandatory artefact optional."""
    with pytest.raises(ev.UnknownClass):
        ev.check("TARGETT")


def test_the_four_classes_are_the_four():
    assert ev.CLASSES == (ev.TARGET, ev.CONSUMER, ev.REGRESSION, ev.ROLLBACK)
    assert ev.DELIVERY == ev.CLASSES
    # ANALYSIS is a DECLARED reduction, not an accident: nothing to roll back, nothing to regress.
    assert set(ev.ANALYSIS) < set(ev.DELIVERY)


# ------------------------------------------------------------------------------- the three states

def test_absent_asserted_and_satisfied_are_three_different_answers():
    rows = [
        {"kind": "query", "ref": "q.sql", "basis": "MEASURED", "evidence_class": ev.TARGET},
        {"kind": "hunch", "ref": "note", "basis": "ASSUMED", "evidence_class": ev.CONSUMER},
        # REGRESSION and ROLLBACK: nothing at all
    ]
    cov = ev.coverage(rows)
    assert cov.state[ev.TARGET] == ev.SATISFIED
    assert cov.state[ev.CONSUMER] == ev.ASSERTED     # a claim is not a proof
    assert cov.state[ev.REGRESSION] == ev.ABSENT     # nobody looked
    assert cov.state[ev.ROLLBACK] == ev.ABSENT
    assert not cov.complete
    assert set(cov.missing) == {ev.CONSUMER, ev.REGRESSION, ev.ROLLBACK}


def test_an_assumed_row_never_satisfies_a_class():
    """The ASSERTED/SATISFIED line is the whole point — an assumed proof is not a proof."""
    rows = [{"kind": "k", "ref": "r", "basis": "ASSUMED", "evidence_class": c}
            for c in ev.CLASSES]
    cov = ev.coverage(rows)
    assert cov.missing == list(ev.CLASSES)
    assert all(s == ev.ASSERTED for s in cov.state.values())


def test_a_measured_row_upgrades_a_class_that_was_only_asserted():
    rows = [
        {"kind": "k", "ref": "r", "basis": "ASSUMED", "evidence_class": ev.TARGET},
        {"kind": "k", "ref": "r2", "basis": "DERIVED", "evidence_class": ev.TARGET},
    ]
    assert ev.coverage(rows).state[ev.TARGET] == ev.SATISFIED


def test_an_unclassified_row_counts_toward_nothing():
    """Four unclassified artefacts must not look like four answered questions."""
    rows = [{"kind": "screenshot", "ref": f"{i}.png", "basis": "MEASURED"} for i in range(4)]
    cov = ev.coverage(rows)
    assert cov.missing == list(ev.CLASSES)


def test_four_pieces_of_one_class_do_not_satisfy_four_classes():
    """The defect this module exists for, stated as a test."""
    rows = [{"kind": "shot", "ref": f"{i}.png", "basis": "MEASURED",
             "evidence_class": ev.CONSUMER} for i in range(4)]
    cov = ev.coverage(rows)
    assert cov.state[ev.CONSUMER] == ev.SATISFIED
    assert len(cov.missing) == 3


def test_a_complete_delivery_passes():
    """The positive control. A gate that only ever refuses is not a gate either."""
    rows = [{"kind": "k", "ref": "r", "basis": "MEASURED", "evidence_class": c}
            for c in ev.DELIVERY]
    cov = ev.coverage(rows)
    assert cov.complete and not cov.missing
    assert "COMPLETE" in cov.summary()


# ------------------------------------------------------------------------------ the store gate

def _store(tmp_path):
    return TaskStore(tmp_path / "tasks.jsonl")


def test_store_refuses_an_unknown_class_at_write_time(tmp_path):
    s = _store(tmp_path)
    tid = s.create("t")
    with pytest.raises(ev.UnknownClass):
        s.add_evidence(tid, "k", "r", actor="a", basis="MEASURED", evidence_class="ROLLBACKS")


def test_close_with_require_refuses_a_partial_delivery(tmp_path):
    """WATCHED REFUSING: one measured artefact satisfies the old rule and not the four-class one."""
    s = _store(tmp_path)
    tid = s.create("add source X to client Y reporting")
    s.add_evidence(tid, "dax", "82,135.29", actor="a", basis="MEASURED",
                   evidence_class=ev.CONSUMER)
    s.close(tid, actor="a")                                   # old rule: passes
    assert s.get(tid).status == "done"

    tid2 = s.create("same work, gated")
    s.add_evidence(tid2, "dax", "82,135.29", actor="a", basis="MEASURED",
                   evidence_class=ev.CONSUMER)
    with pytest.raises(EvidenceRequired) as exc:
        s.close(tid2, actor="a", require=ev.DELIVERY)
    msg = str(exc.value)
    assert ev.TARGET in msg and ev.ROLLBACK in msg            # names what is missing
    assert s.get(tid2).status != "done"


def test_close_with_require_lets_a_complete_delivery_through(tmp_path):
    s = _store(tmp_path)
    tid = s.create("complete delivery")
    for c in ev.DELIVERY:
        s.add_evidence(tid, c.lower(), f"docs/evidence/{c}.md", actor="a",
                       basis="MEASURED", evidence_class=c)
    s.close(tid, actor="a", require=ev.DELIVERY)
    assert s.get(tid).status == "done"


def test_the_class_survives_a_reload(tmp_path):
    """Append-only means the store is a fold over events; a typed field that does not replay is
    a typed field that exists only in memory."""
    p = tmp_path / "tasks.jsonl"
    s = TaskStore(p)
    tid = s.create("t")
    s.add_evidence(tid, "k", "r", actor="a", basis="MEASURED", evidence_class=ev.TARGET)
    again = TaskStore(p)
    assert again.coverage(tid).state[ev.TARGET] == ev.SATISFIED
