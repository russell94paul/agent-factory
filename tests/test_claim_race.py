"""Claiming a lane must be atomic, because the transport no longer makes it so by accident.

`claim()` reads `blockers()` and then writes, with nothing in between. That was safe only because
`socketserver.TCPServer` served one request at a time — a property of the transport, not of the
code. The tracker server was made threaded on 2026-08-23 to stop one slow render blocking every
other viewer, and that silently removed the serialisation.

`/start/<lane>` is a GET. A double-click, a browser prefetch, or two people looking at the board is
enough for two requests to pass the same check and both write — which is **F73 re-opened at the
HTTP layer**: two agents, one worktree, one branch.

These tests run real threads against the real function. A test that mocked the lock would prove
only that the mock works.
"""
from __future__ import annotations

import threading

import pytest

from factory import claims


@pytest.fixture()
def lane_id():
    from factory.lanes import LANES
    assert LANES, "no lanes defined — nothing to claim"
    return LANES[0].id


@pytest.fixture(autouse=True)
def _isolated_claims(tmp_path, monkeypatch):
    """Never touch the real .data/claims — these tests create and destroy claims."""
    root = tmp_path / "claims"
    monkeypatch.setattr(claims, "ROOT", root)
    yield
    for f in root.glob("*"):
        f.unlink()


def test_only_one_of_many_concurrent_claims_wins(lane_id):
    """The whole point. Twenty threads race for one lane; exactly one may succeed."""
    wins, losses = [], []
    barrier = threading.Barrier(20)

    def go():
        barrier.wait()                      # maximise the overlap on the check-then-write
        try:
            claims.claim(lane_id, who="racer")
            wins.append(1)
        except claims.ClaimError:
            losses.append(1)

    threads = [threading.Thread(target=go) for _ in range(20)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=30)

    assert len(wins) == 1, (
        f"{len(wins)} threads claimed the same lane — the check-then-write is not atomic, "
        "and two agents would be pointed at one worktree and one branch")
    assert len(losses) == 19


def test_the_lock_is_released_so_a_later_claim_can_proceed(lane_id):
    """A lock held after an exception would turn a race into a permanent deadlock."""
    claims.claim(lane_id, who="first")
    with pytest.raises(claims.ClaimError):
        claims.claim(lane_id, who="second")          # refused inside the lock
    claims.release(lane_id)
    claims.claim(lane_id, who="third")               # must not hang or fail
    assert claims.blockers(lane_id)


def test_an_abandoned_lock_is_stolen_rather_than_wedging_the_board(lane_id, monkeypatch):
    """A crashed holder must not make the board permanently unclaimable.

    Deadlock-instead-of-race is not a fix; it is the same outage with a different cause.
    """
    claims.ROOT.mkdir(parents=True, exist_ok=True)
    lock = claims.ROOT / ".claim.lock"
    lock.write_text("stale", encoding="utf-8")
    monkeypatch.setattr(claims, "_LOCK_ABANDON", 0.0)     # everything is instantly abandoned
    claims.claim(lane_id, who="after-crash")              # must not raise
    assert claims.blockers(lane_id)


def test_a_held_lock_eventually_refuses_rather_than_hanging_forever(lane_id, monkeypatch):
    """If someone really is holding it, the caller must get an error, not an infinite wait."""
    claims.ROOT.mkdir(parents=True, exist_ok=True)
    (claims.ROOT / ".claim.lock").write_text("held", encoding="utf-8")
    monkeypatch.setattr(claims, "_LOCK_TIMEOUT", 0.15)    # give up quickly
    monkeypatch.setattr(claims, "_LOCK_ABANDON", 3600.0)  # but do not consider it abandoned
    with pytest.raises(claims.ClaimError, match="claim lock"):
        claims.claim(lane_id, who="waiter")
