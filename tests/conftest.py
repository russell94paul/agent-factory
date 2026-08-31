"""Suite-wide isolation for the run ledger.

Wiring `finish()` into `factory.runs` had an immediate and invisible side effect: the existing
`test_bus_and_finish.py` calls `finish.finish("certify", ...)` against a fixture, so every suite
run appended real rows to the real `.data/runs.jsonl`. Twelve of them landed before anyone looked,
and the tracker duly rendered *"certify — FINISHED, 12 recorded runs"* on a lane that had run
once, yesterday, before the ledger existed.

That is worse than a wrong number: it is a **fabricated history in the one instrument built to
stop history being lost**. So the redirect is autouse — no test has to remember it, and a test
added later cannot forget.

Tests that must assert against the *real* repo declare the `real_ledger` fixture and are skipped
by the redirect. That opt-out exists because the live assertions in `test_runs.py` are about where
the ledger resolves to on this machine; pointed at a tmp directory they would pass trivially, and
a check that cannot fail is not a check.
"""
from __future__ import annotations

import os

import pytest

from factory import runs

# ---------------------------------------------------------------------------------------------
# ⛔ Mark the whole run as being INSIDE the suite, before any test imports a measuring surface.
#
# The `suite` readiness gate shells out to `python -m pytest`. So the moment a test renders a tab
# that measures, it re-enters that gate, spawns the entire suite again, and the child does the
# same — unbounded fan-out. The first test to render the roadmap tab produced 14 nested pytest
# processes before it was killed.
#
# `readiness.g_contract_suite_green` reads this flag and reports NOT-RUN instead of recursing,
# which is also the honest verdict: a suite cannot measure itself while it is still running. Set
# here rather than in each test for the same reason the ledger redirect is autouse — a test added
# later cannot forget it.
os.environ["AGENT_FACTORY_IN_SUITE"] = "1"


@pytest.fixture()
def real_ledger():
    """Declare this to opt out of the redirect and see the real ledger path."""
    return True


@pytest.fixture(autouse=True)
def _isolate_run_ledger(tmp_path, monkeypatch, request):
    if "real_ledger" in request.fixturenames:
        return
    monkeypatch.setattr(runs, "_primary", lambda: tmp_path / "ledger-root")


@pytest.fixture(autouse=True)
def _isolate_event_stream(tmp_path, monkeypatch, request):
    """The same redirect, for `.data/events.jsonl`, for exactly the same reason.

    The run ledger got this fixture only after twelve fabricated rows had already landed in it and
    the tracker had rendered them as history. `factory.events` is the *source* that ledger is a
    fold of, so an unredirected test writing there would fabricate the same history one layer
    further upstream — and would do it with a full eligible set attached, which reads as more
    trustworthy, not less. Autouse, so a test added later cannot forget.
    """
    if "real_ledger" in request.fixturenames:
        return
    from factory import events
    monkeypatch.setattr(events, "path", lambda: tmp_path / "event-root" / "events.jsonl")
