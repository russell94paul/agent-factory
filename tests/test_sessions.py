"""The session board must not assert an order it cannot justify, or a card nobody can read.

Two failure modes, both silent, both asserted here rather than trusted:

* **an ordering that means nothing.** `running_order()` will always return waves; the
  question is whether any of them were earned. Today none are, and the module has to SAY so
  — a board that prints declaration order as a sequence is worse than one that prints
  nothing, because a reader will sequence their week by it.
* **a card with no title or description.** The surface's only job is letting somebody know
  what a handoff is about without opening it. A blank title reads as "no work here".
"""
from __future__ import annotations

import pytest

from factory import sessions as S
from factory.board import DEPENDS
from factory.lanes import LANES


# --------------------------------------------------------------------------- derivation


def test_every_gate_has_at_most_one_owner():
    """A gate worked by two sessions has no owner and no running order."""
    S.gate_owner()          # raises if a gate is claimed twice


def test_ordering_is_derived_not_declared():
    """Nothing in this module may carry a hand-maintained edge list.

    The whole reason `after()` projects `board.DEPENDS` is that a second source of truth
    drifts from the first silently. If someone adds a literal edge table here, this fails.
    """
    src = (S.__file__ and open(S.__file__, encoding="utf-8").read())
    for lane in LANES:
        assert f'"{lane.id}": [' not in src, (
            f"{lane.id!r} appears as a literal edge list in sessions.py — the ordering is "
            f"supposed to be derived from board.DEPENDS, not restated here")


def test_a_dependency_inside_one_session_is_not_an_edge_between_sessions():
    """`truthful` depends on `from-history` and both are control-plane. That is sequencing
    within a session, not a running order between sessions — a self-edge would make the
    session depend on itself and `running_order()` would raise a false cycle."""
    assert "control-plane" not in S.after()["control-plane"]
    assert DEPENDS["truthful"] == ["from-history"], (
        "the fixture this test reasons about moved; re-pick an intra-lane edge")


def test_a_dependency_on_an_unowned_gate_is_reported_separately():
    """`certify` depends on `isolated`, which no lane owns. No running order fixes that, so
    it must not appear as an `after` edge — it would look schedulable and never resolve."""
    assert "isolated" in S.blocked_by_gate()["certify"]
    assert "isolated" in S.unowned_gates()
    assert all("isolated" not in v for v in S.after().values())


def test_conflicts_are_symmetric_and_are_not_ordering():
    """Two sessions editing one file cannot run *concurrently*. Either order is fine, so a
    conflict must never leak into `after` — a reader who waits for it waits forever."""
    c = S.conflicts()
    for a, others in c.items():
        for b in others:
            assert a in c[b], f"{a}->{b} is a conflict but {b}->{a} is not"
    flat = {(a, b) for a, o in c.items() for b in o}
    assert flat, "no conflicts found at all — the touches parser has probably stopped working"
    aft = S.after()
    for a, b in flat:
        assert b not in aft.get(a, []), f"{b} is a conflict of {a} but also an ordering edge"


def test_the_two_real_collisions_are_found():
    """Both are real and only one of them was written down anywhere before this module.

    control-plane/judgement is in the boot prompt. certify/grain was not, and it is the same
    hazard: two sessions editing `factory/connector_contract.py`.
    """
    c = S.conflicts()
    assert "judgement" in c["control-plane"]
    assert "grain" in c["certify"]


def test_running_order_covers_every_session_exactly_once():
    waves = S.running_order()
    flat = [s for w in waves for s in w]
    assert sorted(flat) == sorted(l.id for l in LANES)
    assert len(flat) == len(set(flat))


def test_a_cycle_raises_rather_than_being_linearised(monkeypatch):
    """An unsatisfiable order is a design error in DEPENDS. Picking an arbitrary order hides
    it, and the board then asserts a sequence that cannot be run."""
    monkeypatch.setattr(S, "after", lambda: {"a": ["b"], "b": ["a"]})
    with pytest.raises(ValueError, match="cycle"):
        S.running_order()


# --------------------------------------------------------------------------- honesty


def test_the_report_refuses_to_present_a_meaningless_order():
    """⭐ The one that matters. While no lane-to-lane edge exists, the report must say so.

    `running_order()` always returns waves, so a reader seeing "wave 0: a, b, c" has no way
    to tell a derived order from an alphabetical one. If edges are ever added this assertion
    flips to the other branch — which is correct, and the test says which branch it is in.
    """
    # Whitespace-normalised before matching. The phrase wraps across a line in the rendered
    # report, so asserting the raw substring checked a pattern that could never match — the
    # exact shape of finding F19, in a test written to enforce honesty.
    text = " ".join(S._report().split())
    if any(S.after().values()):
        assert "NO ORDERING CONSTRAINTS EXIST" not in text, (
            "edges now exist, so the disclaimer must go — the report is claiming there is "
            "no order while deriving one")
    else:
        assert "NO ORDERING CONSTRAINTS EXIST" in text
        assert "that order means nothing" in text


def test_unowned_gates_are_surfaced():
    """12 gates belong to no lane. Nothing schedules them, so a board that lists only lanes
    quietly implies the work is covered."""
    assert S.unowned_gates()
    assert "belong to no session" in S._report()


# --------------------------------------------------------------------------- cards


@pytest.fixture(autouse=True)
def _isolated_store(tmp_path, monkeypatch):
    monkeypatch.setattr(S, "CARDS", tmp_path / "cards.jsonl")


def test_a_lane_card_takes_its_title_and_description_from_lanes():
    c = S.post("lane", body="what happened", session="control-plane")
    assert c.title == "Bound the loop"
    assert c.description.startswith("Five gates, one file")
    assert c.gates and c.after == [] and "judgement" in c.conflicts


@pytest.mark.parametrize("kwargs, missing", [
    ({"kind": "session", "body": "b", "description": "d"}, "title"),
    ({"kind": "session", "body": "b", "title": "t"}, "description"),
    ({"kind": "session", "body": "b", "title": "  ", "description": "d"}, "title"),
])
def test_a_card_without_a_title_or_a_description_is_refused(kwargs, missing):
    """Not defaulted — refused. A blank title on a board reads as 'no work here'."""
    with pytest.raises(S.CardError, match=missing):
        S.post(**kwargs)


def test_a_card_with_no_body_is_refused():
    with pytest.raises(S.CardError, match="heading"):
        S.post("session", body="   ", title="t", description="d")


def test_an_unknown_session_is_refused_and_says_what_is_known():
    with pytest.raises(S.CardError, match="control-plane"):
        S.post("lane", body="b", session="nonesuch")


def test_cards_are_append_only():
    """A later handoff for the same session is a NEW card. Editing one would destroy what a
    previous session said, which is the whole record."""
    a = S.post("lane", body="first", session="grain")
    b = S.post("lane", body="second", session="grain")
    got = S.cards(session="grain")
    assert [c.id for c in got] == [b.id, a.id], "newest first"
    assert {c.body for c in got} == {"first", "second"}


def test_a_corrupt_card_raises_rather_than_disappearing():
    """Skipping an unreadable line makes a handoff stop existing with nobody told."""
    S.post("lane", body="fine", session="grain")
    S.CARDS.write_text(S.CARDS.read_text(encoding="utf-8") + "{not json\n", encoding="utf-8")
    with pytest.raises(S.CardError, match="will not load"):
        S.cards()
