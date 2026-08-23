"""The roadmap is a join over the board, and it must stay one.

The roadmap tab exists because someone asked for the sequence of work and what can run in
parallel. Both were already computed — `board()` returns DONE/READY/BLOCKED per gate and
`critical_path()` returns the chain — so the risk here is not that the arithmetic is wrong. It is
that the two AUTHORED maps in `factory/roadmap.py` (TEAMS and ACTIONS) quietly drift away from the
gates they name, or that the derived view starts describing work the board does not contain.

These tests are aimed at exactly that: the derived parts must equal the board, and the authored
parts must be provably about live gates.
"""
from __future__ import annotations

import datetime

import pytest

from factory import board as boardlib
from factory import roadmap as rm
from scripts import local_tracker as lt  # noqa: E402


# --------------------------------------------------------------------------- derived == board


def test_the_waves_are_exactly_the_board_and_lose_nothing():
    """Every gate appears in exactly one wave.

    A roadmap that drops a gate is worse than no roadmap: it reads as complete. This would fail if
    `waves()` ever filtered — which is the tempting change the first time a band looks crowded.
    """
    rows = boardlib.board()
    seen = [g["id"] for band in rm.waves() for g in band["gates"]]
    assert sorted(seen) == sorted(g.id for g, _, _, _ in rows)
    assert len(seen) == len(set(seen)), "a gate appears in more than one wave"


def test_the_ready_band_is_the_boards_ready_set():
    """"What can run in parallel" must be READY, not a judgement layered on top of it.

    The whole claim the tab makes is that parallelism is definitional. If this band were ever
    computed some other way the claim would become an assertion, and a false one.
    """
    ready_board = {g.id for g, _, st, _ in boardlib.board() if st == boardlib.READY}
    ready_tab = {g["id"] for band in rm.waves() if band["key"] == boardlib.READY
                 for g in band["gates"]}
    assert ready_tab == ready_board


def test_nothing_in_the_ready_band_is_waiting_on_anything():
    """READY means no unmet dependency. If one had unmet edges the parallel claim would be false."""
    for band in rm.waves():
        if band["key"] != boardlib.READY:
            continue
        for g in band["gates"]:
            assert not g["unmet"], f"{g['id']} is READY but waits on {g['unmet']}"


def test_every_blocked_gate_names_what_blocks_it():
    """"Blocked" with no named blocker is the uninformative half of the word."""
    for band in rm.waves():
        if band["key"] != boardlib.BLOCKED:
            continue
        assert band["gates"], "no blocked gates — this test has nothing to prove"
        for g in band["gates"]:
            assert g["unmet"], f"{g['id']} is BLOCKED but names no unmet dependency"


def test_the_critical_path_matches_the_board_and_is_a_real_chain():
    """Each hop must actually depend on the one before it, or the 'sequence' is decoration."""
    ch = rm.chain()
    assert [h["id"] for h in ch] == boardlib.critical_path()
    for prev, nxt in zip(ch, ch[1:]):
        assert prev["id"] in boardlib.DEPENDS.get(nxt["id"], []), (
            f"{nxt['id']} does not depend on {prev['id']} — the chain is not a chain")


# --------------------------------------------------------------------------- authored maps


def test_the_authored_maps_only_name_live_gates():
    """`_validate()` runs on import; this proves it is actually load-bearing.

    Point a team at a gate that does not exist and the module must refuse to import, rather than
    silently shrinking the team's denominator — which is how a progress bar starts lying.
    """
    ids = {g.id for g in rm.GATES}
    for name, spec in rm.TEAMS.items():
        for gid in spec["gates"]:
            assert gid in ids, f"TEAMS[{name}] names dead gate {gid}"
    for a in rm.ACTIONS:
        if a.gate:
            assert a.gate in ids, f"ACTIONS[{a.id}] names dead gate {a.gate}"


def test_the_validator_refuses_a_dead_gate(monkeypatch):
    """The proof that the guard above can fail — the repo's standing rule for every assertion."""
    monkeypatch.setitem(rm.TEAMS, "Bogus Team",
                        {"intent": "x", "gates": ["no-such-gate-anywhere"], "blocked_on": None})
    with pytest.raises(ValueError, match="does not exist"):
        rm._validate()


def test_the_validator_refuses_a_changed_action_count(monkeypatch):
    """Eighteen is a fact about the record, not a coincidence. Changing it must be deliberate."""
    monkeypatch.setattr(rm, "ACTIONS", rm.ACTIONS[:-1])
    with pytest.raises(ValueError, match="eighteen"):
        rm._validate()


def test_a_gated_action_takes_its_state_from_the_gate_not_the_author():
    """The asymmetry the module is built on: a measurement outranks a person's claim.

    ⚠ This used to assert that at least one real action was gated. As of 2026-08-23 **none is** —
    R16 §2.1 showed all three edges were wrong and they were removed, so the honest count is
    0 MEASURED / 18 AUTHORED. Asserting "at least one" would now force someone to re-add a bad
    edge to get the suite green, which is the worst thing a test can do.

    So the OVERRIDE LOGIC is proved against a constructed action instead. The path stays tested
    whether or not the real map happens to use it.
    """
    for a in rm.actions():
        if a["gate"]:
            assert a["basis"] == rm.MEASURED
            assert a["state"] == (rm.SHIPPED if a["verdict"] == "PASS" else rm.DECIDED)

    # `suite` is a live gate, so this exercises the real measure() path rather than a stub.
    probe = rm.Action("zz-probe", "probe", "§x", state=rm.SUPERSEDED, gate="suite",
                      why_gate="test-only probe of the override path")
    rm.ACTIONS.append(probe)
    try:
        row = next(a for a in rm.actions() if a["id"] == "zz-probe")
        assert row["basis"] == rm.MEASURED, "a gated action must not report AUTHORED"
        assert row["state"] != rm.SUPERSEDED, (
            "the authored state survived a gate edge — the gate must win, always")
        assert row["state"] == (rm.SHIPPED if row["verdict"] == "PASS" else rm.DECIDED)
    finally:
        rm.ACTIONS.remove(probe)


def test_an_ungated_action_is_never_labelled_measured():
    """An authored claim must not borrow the credibility of a measured one."""
    for a in rm.actions():
        if not a["gate"]:
            assert a["basis"] == rm.AUTHORED, f"{a['id']} claims MEASURED with no gate behind it"


def test_a_team_with_no_gates_reports_ungated_and_not_zero():
    """"Nothing is measuring this" and "measured at zero" are different claims.

    The Power BI team has no contract yet, so it has no gates. Rendering it as 0% would invent a
    denominator and imply the work had been assessed and found absent.
    """
    ungated = [t for t in rm.teams() if not t["gates"]]
    assert ungated, "no ungated team — this guard has nothing to protect"
    for t in ungated:
        assert t["basis"] == "UNGATED"
        assert t["total"] == 0
        assert t["unblock"], "an ungated team must say what would unblock it"


# --------------------------------------------------------------------------- contradictions


def test_contradictions_are_gates_that_pass_with_an_unmet_dependency():
    """The panel must describe the condition it claims to, or it is a decoration that cries wolf."""
    st = {g.id: (s, u) for g, _, s, u in boardlib.board()}
    for c in rm.contradictions():
        status, unmet = st[c["id"]]
        assert status == boardlib.DONE
        assert unmet and set(c["unmet"]) == set(unmet)


def test_contradictions_is_empty_when_no_gate_passes_over_an_unmet_edge(monkeypatch):
    """Proof the detector can return nothing — otherwise a always-non-empty panel proves nothing."""
    monkeypatch.setattr(rm, "board", lambda: [])
    assert rm.contradictions() == []


# --------------------------------------------------------------------------- the tab itself


@pytest.fixture(scope="module")
def page() -> str:
    return lt.render(datetime.datetime(2026, 8, 23, 12, 0), "roadmap")


def test_the_roadmap_route_is_registered():
    """A tab absent from TABS is a page nothing links to."""
    assert any(key == "roadmap" for key, _, _ in lt.TABS)


def test_the_tab_renders_and_identifies_itself(page):
    assert "<h1>Roadmap</h1>" in page
    assert "Start here" not in page, "lane content leaked onto the roadmap tab"


def test_the_tab_states_the_unplaced_gates_rather_than_implying_completeness(page):
    """A roadmap implies it covers everything. This one does not, and must say which gates."""
    up = rm.unplaced()
    assert up["unplaced"], "nothing unplaced — this guard has nothing to protect"
    for gid in up["unplaced"]:
        assert gid in page, f"{gid} is on no goal and no team, and the page does not say so"


def test_the_tab_shows_every_one_of_the_eighteen_actions(page):
    """Rendering a subset would let a decision quietly stop being tracked."""
    for a in rm.ACTIONS:
        assert a.source.replace("§", "&sect;") in page or a.source in page, (
            f"action {a.id} ({a.source}) is not on the page")


# --------------------------------------------------------------------------- the R16 §2.1 defect


def test_a_gate_edge_must_carry_a_stated_reason():
    """Three edges were authored without one and all three were wrong.

    `_validate()` can only prove a gate EXISTS. Nothing can automatically check that the gate's
    QUESTION matches the action's SUBJECT — so the control is that a human had to write the
    sentence. Weak, but it makes the mismatch get considered instead of assumed.
    """
    for a in rm.ACTIONS:
        if a.gate:
            assert a.why_gate.strip(), (
                f"{a.id} links gate {a.gate!r} with no why_gate — the exact shape of the three "
                "edges R16 2.1 found wrong")


def test_the_why_gate_guard_can_fail():
    """Proof the check above is not vacuous — the rule this repo holds every gate to."""
    rm.ACTIONS.append(rm.Action("zz-probe", "probe", "§x", gate="suite"))
    try:
        with pytest.raises(ValueError, match="why_gate"):
            rm._validate()
    finally:
        rm.ACTIONS.pop()
    rm._validate()          # and the map is valid again once the probe is removed


def test_no_action_claims_measured_without_a_gate_behind_it():
    """The asymmetry the module rests on, restated as an assertion.

    As of 2026-08-23 the honest count is 0 MEASURED / 18 AUTHORED. That is allowed. What is not
    allowed is an action rendering MEASURED on an edge nobody justified.
    """
    for a in rm.actions():
        if a["basis"] == rm.MEASURED:
            src = next(x for x in rm.ACTIONS if x.id == a["id"])
            assert src.gate and src.why_gate.strip(), (
                f"{a['id']} renders MEASURED without a justified gate edge")
