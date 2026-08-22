"""The channel must deliver, and the finish gate must refuse.

Two decoration risks, one each way. A bus nobody reads is the defect this repo keeps meeting, so
delivery and the cursor are asserted rather than assumed. And a finish check that always passes
would release claims on lanes that stopped rather than finished — advertising a lie to the next
session — so each refusal is exercised on purpose.
"""
from __future__ import annotations

import pytest

from factory import bus


@pytest.fixture(autouse=True)
def _isolate(tmp_path, monkeypatch):
    monkeypatch.setattr(bus, "ROOT", tmp_path / "bus")


# ------------------------------------------------------------------ the bus

def test_a_lane_does_not_read_its_own_traffic_back():
    bus.post("certify", "note", "mine")
    assert bus.unread("certify") == []
    assert [e["text"] for e in bus.unread("artifact")] == ["mine"]


def test_the_cursor_stops_redelivery_but_lets_new_traffic_through():
    bus.post("certify", "note", "first")
    assert len(bus.unread("artifact")) == 1
    bus.mark_read("artifact")
    assert bus.unread("artifact") == []
    bus.post("certify", "note", "second")
    assert [e["text"] for e in bus.unread("artifact")] == ["second"]


def test_two_lanes_never_write_the_same_file():
    """F70's lesson applied: the collision that produced three F11s cannot recur here."""
    bus.post("certify", "note", "a")
    bus.post("artifact", "note", "b")
    names = sorted(p.name for p in bus.ROOT.glob("*.jsonl"))
    assert names == ["artifact.jsonl", "certify.jsonl"]


def test_a_torn_line_does_not_lose_the_rest():
    bus.post("certify", "note", "good")
    (bus.ROOT / "certify.jsonl").open("a", encoding="utf-8").write("{not json\n")
    bus.post("certify", "note", "also good")
    assert [e["text"] for e in bus.unread("artifact")] == ["good", "also good"]


@pytest.mark.parametrize("kind,text", [("shouting", "x"), ("note", ""), ("note", "x" * 5000)])
def test_the_bus_refuses_junk(kind, text):
    with pytest.raises(bus.BusError):
        bus.post("certify", kind, text)


def test_an_unsafe_lane_id_is_refused():
    with pytest.raises(bus.BusError):
        bus.post("../../etc/passwd", "note", "hi")


def test_render_is_empty_for_no_traffic_and_names_the_sender_otherwise():
    assert bus.render([]) == ""
    bus.post("certify", "correction", "your premise is wrong", refs=["F30"])
    out = bus.render(bus.unread("artifact"))
    assert "certify" in out and "CORRECTION" in out and "F30" in out


def test_lane_is_recovered_from_a_worktree_path():
    assert bus.lane_from_cwd(r"C:\repos\agent-factory\.worktrees\certify") == "certify"
    assert bus.lane_from_cwd(r"C:\repos\agent-factory") is None


# --------------------------------------------------------------- the checks

def test_finish_checks_refuse_a_lane_with_no_worktree():
    from factory import finish
    problems = finish.checks("no-such-lane-xyz")
    assert problems and "nothing to finish" in problems[0]


def test_finish_refuses_rather_than_releasing_when_checks_fail(monkeypatch):
    """The load-bearing refusal: a lane that stopped must not have its claim released, because a
    released claim says 'this lane is done' to everyone who looks next."""
    from factory import finish
    monkeypatch.setattr(finish, "checks", lambda lane, base=None: ["dirty tree"])
    released = []
    monkeypatch.setattr(finish._claims, "release", lambda l: released.append(l) or True)
    with pytest.raises(finish.NotFinished):
        finish.finish("certify", push=False)
    assert released == [], "a failed check must not release the claim"


def test_a_failed_push_does_not_release_the_claim(monkeypatch):
    """Losing the branch is the thing finish() exists to prevent. If the push fails the lane stays
    claimed, so the next person sees an unfinished lane rather than a vanished one."""
    from factory import finish
    monkeypatch.setattr(finish, "checks", lambda lane, base=None: [])
    monkeypatch.setattr(finish, "_git", lambda lane, *a: (1, "fatal: no remote"))
    released = []
    monkeypatch.setattr(finish._claims, "release", lambda l: released.append(l) or True)
    with pytest.raises(finish.NotFinished) as e:
        finish.finish("certify", push=True)
    assert "claim NOT released" in str(e.value)
    assert released == []


def test_finish_never_merges(monkeypatch):
    from factory import finish
    monkeypatch.setattr(finish, "checks", lambda lane, base=None: [])
    monkeypatch.setattr(finish._claims, "release", lambda l: True)
    r = finish.finish("certify", push=False)
    assert r["merged"] is False
    assert not any("merge" in d.lower() for d in r["did"]), r["did"]


# ------------------------------------------------- a claim is not a process

def test_finish_refuses_while_a_session_is_still_live(monkeypatch):
    """The defect this guard exists for: finish() released a claim out from under a live session,
    a relaunch saw a free lane, and three agents ended up in one worktree on one branch."""
    from factory import finish, sessions
    monkeypatch.setattr(sessions, "live", lambda lane: [{"pid": 123, "status": "idle"}])
    monkeypatch.setattr(finish._wt, "is_dirty", lambda lane: False)
    monkeypatch.setattr(finish._wt, "path_for", lambda lane: __import__("pathlib").Path("."))
    problems = finish.checks("certify")
    assert any("live session" in p for p in problems), problems


def test_finish_allows_once_the_session_has_exited(monkeypatch):
    """The guard must be able to PASS, or it is a wall rather than a check."""
    from factory import finish, sessions
    monkeypatch.setattr(sessions, "live", lambda lane: [])
    problems = finish.checks("certify")
    assert not any("live session" in p for p in problems), problems


def test_a_stale_registry_file_is_not_a_live_session(tmp_path, monkeypatch):
    """The file outlives the process. Checking existence instead of liveness would report every
    historical session as live and refuse every launch."""
    from factory import sessions
    import json as _j
    monkeypatch.setattr(sessions, "REGISTRY", tmp_path)
    (tmp_path / "999999.json").write_text(_j.dumps(
        {"pid": 999999, "status": "idle", "cwd": "/repo/.worktrees/certify"}), encoding="utf-8")
    monkeypatch.setattr(sessions, "_running_pids", lambda: set())      # nothing running
    assert sessions.live("certify") == []
    monkeypatch.setattr(sessions, "_running_pids", lambda: {999999})   # now it is
    assert len(sessions.live("certify")) == 1


def test_unknown_process_table_is_not_reported_as_nothing_running(tmp_path, monkeypatch):
    """'I cannot see the process table' and 'nothing is running' are different verdicts."""
    from factory import sessions
    import json as _j
    monkeypatch.setattr(sessions, "REGISTRY", tmp_path)
    (tmp_path / "42.json").write_text(_j.dumps(
        {"pid": 42, "status": "busy", "cwd": "/repo/.worktrees/certify"}), encoding="utf-8")
    monkeypatch.setattr(sessions, "_running_pids", lambda: None)       # could not look
    live = sessions.live("certify")
    assert len(live) == 1 and live[0]["unverified"] is True
