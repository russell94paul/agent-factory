"""The windowed gates must still be able to PASS and to FAIL.

Windowing two unpassable gates (F20/F21) is one edit away from gaming them. A gate that can only
ever say UNMEASURABLE is a new wall, not a fix, and a window that lets an empty set read PASS is
worse than the wall it replaced. So each gate is exercised in all three directions against
synthesised audits, and the empty-window case is asserted to be UNMEASURABLE specifically — not
merely "not a pass".
"""
from __future__ import annotations

import pytest

from factory import readiness as R


def _run(rid, started, events):
    return {"id": rid, "events": [{"timestamp": started, "event_type": e,
                                   "stage_name": "s", "details": "{}"} for e in events]}


IN = "2026-08-22T10:00:00+00:00"      # inside the window
OLD = "2026-05-26T10:00:00+00:00"     # the uncontrolled era


@pytest.fixture
def audits(monkeypatch):
    def use(runs):
        monkeypatch.setattr(R, "_audits", lambda: list(runs))
    return use


# --------------------------------------------------------------- finishes

def test_finishes_passes_when_every_windowed_run_is_terminal(audits):
    audits([_run("a", IN, ["stage_started", "pipeline_completed"])])
    assert R.g_finishes().verdict == R.PASS


def test_finishes_fails_when_a_windowed_run_is_stranded(audits):
    """The gate must still refuse. This is the case the old all-time version could never reach
    for a good reason and now must reach for a bad one."""
    audits([_run("a", IN, ["stage_started", "pipeline_completed"]),
            _run("b", IN, ["stage_started"])])
    assert R.g_finishes().verdict == R.FAIL


def test_finishes_ignores_pre_window_runs_but_does_not_hide_them(audits):
    """Four historical runs are stuck forever. They must not make the gate unpassable, and they
    must not vanish — the count is named in the evidence."""
    audits([_run("old", OLD, ["stage_started"]),
            _run("a", IN, ["stage_started", "pipeline_completed"])])
    r = R.g_finishes()
    assert r.verdict == R.PASS
    assert any("1 run(s) started before it are excluded" in e for e in r.evidence), r.evidence


def test_finishes_is_unmeasurable_not_pass_on_an_empty_window(audits):
    """⭐ The whole safety of the change. No runs since the controls landed is the honest state
    today, and it must never be mistaken for the controls working."""
    audits([_run("old", OLD, ["stage_started", "pipeline_completed"])])
    with pytest.raises(R.Unmeasurable):
        R.g_finishes()


# --------------------------------------------------------------- succeeds

def test_succeeds_passes_when_the_windowed_rate_is_good(audits):
    audits([_run("a", IN, ["stage_completed", "stage_completed", "stage_failed"])])
    assert R.g_succeeds_more_than_fails().verdict == R.PASS


def test_succeeds_fails_when_the_windowed_rate_is_bad(audits):
    audits([_run("a", IN, ["stage_failed", "stage_failed", "stage_completed"])])
    assert R.g_succeeds_more_than_fails().verdict == R.FAIL


def test_succeeds_is_not_dragged_down_by_the_capped_incident(audits):
    """1001 historical failures must not require 837 net successes to overcome — that was F21."""
    audits([_run("incident", OLD, ["stage_failed"] * 1001),
            _run("a", IN, ["stage_completed", "stage_completed"])])
    r = R.g_succeeds_more_than_fails()
    assert r.verdict == R.PASS
    assert any("all-time" in e and "1001" in e for e in r.evidence), r.evidence


def test_succeeds_is_unmeasurable_not_pass_on_an_empty_window(audits):
    audits([_run("old", OLD, ["stage_completed"] * 50)])
    with pytest.raises(R.Unmeasurable):
        R.g_succeeds_more_than_fails()


def test_succeeds_is_unmeasurable_when_windowed_runs_carry_no_outcome(audits):
    audits([_run("a", IN, ["stage_started"])])
    with pytest.raises(R.Unmeasurable):
        R.g_succeeds_more_than_fails()


# --------------------------------------------------------------- F72 basis

def test_every_windowed_gate_states_its_basis(audits):
    audits([_run("a", IN, ["stage_started", "pipeline_completed", "stage_completed"])])
    for gate in (R.g_finishes, R.g_succeeds_more_than_fails):
        r = gate()
        assert any(e.startswith("basis: runs since") for e in r.evidence), (gate.__name__, r.evidence)
        assert any(str(R.CONNECTORS) in e for e in r.evidence), gate.__name__
