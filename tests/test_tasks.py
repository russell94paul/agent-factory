import pytest

from factory.tasks import DONE, EvidenceRequired, TaskStore


def test_cannot_close_without_evidence(tmp_path):
    s = TaskStore(tmp_path / "t.jsonl")
    tid = s.create("do a thing")
    with pytest.raises(EvidenceRequired):
        s.close(tid)


def test_assumed_evidence_is_not_enough(tmp_path):
    s = TaskStore(tmp_path / "t.jsonl")
    tid = s.create("do a thing")
    s.add_evidence(tid, "guess", "probably fine", actor="a", basis="ASSUMED")
    with pytest.raises(EvidenceRequired):
        s.close(tid)


def test_closes_with_measured_evidence(tmp_path):
    s = TaskStore(tmp_path / "t.jsonl")
    tid = s.create("do a thing")
    s.add_evidence(tid, "contract", "green", actor="a", basis="MEASURED")
    s.close(tid)
    assert s.get(tid).status == DONE


def test_evidence_appends_never_overwrites(tmp_path):
    s = TaskStore(tmp_path / "t.jsonl")
    tid = s.create("x")
    s.add_evidence(tid, "a", "1", actor="one", basis="MEASURED")
    s.add_evidence(tid, "b", "2", actor="two", basis="MEASURED")
    assert len(s.get(tid).evidence) == 2, "second write destroyed the first"


def test_survives_reload(tmp_path):
    p = tmp_path / "t.jsonl"
    s = TaskStore(p)
    tid = s.create("persist me")
    s.add_evidence(tid, "c", "ref", actor="a", basis="MEASURED")
    s.close(tid)
    assert TaskStore(p).get(tid).status == DONE
