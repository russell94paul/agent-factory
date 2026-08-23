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

import pytest

from factory import runs


@pytest.fixture()
def real_ledger():
    """Declare this to opt out of the redirect and see the real ledger path."""
    return True


@pytest.fixture(autouse=True)
def _isolate_run_ledger(tmp_path, monkeypatch, request):
    if "real_ledger" in request.fixturenames:
        return
    monkeypatch.setattr(runs, "_primary", lambda: tmp_path / "ledger-root")
