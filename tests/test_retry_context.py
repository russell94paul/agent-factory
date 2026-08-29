"""A retry must know why the attempt before it failed.

The ledger used to store one integer per key. That bounds re-dispatch — which was the bug it
was written for — but it means attempt 2 is dispatched with exactly the context attempt 1 had.
The agent has no memory of the run before it, so it re-derives the same approach and burns the
cap. These tests pin the fix and, more importantly, pin the things the fix must not break.

The load-bearing test here is `test_the_retry_prompt_carries_the_previous_failure`. Everything
else guards a boundary around it.
"""
import json

import pytest

from factory.deploy import CONTEXT_ATTEMPTS, AttemptLedger, RepoDeployer
from factory.blueprint import AgentSpec


@pytest.fixture()
def ledger(tmp_path):
    return AttemptLedger(tmp_path / "ledger.json", max_attempts=2)


# --------------------------------------------------------------------- the cap must survive
def test_a_legacy_int_ledger_still_holds_its_cap(tmp_path):
    """An existing ledger on disk holds a LIVE cap. Upgrading the format must not drop it.

    If this regresses, a permanently-failing stage gets a fresh budget the first time the new
    code reads an old file — which is the exact all-night re-dispatch the ledger exists to stop.
    """
    p = tmp_path / "legacy.json"
    p.write_text(json.dumps({"worker:wt-1": 2}), encoding="utf-8")

    led = AttemptLedger(p, max_attempts=2)
    assert led.attempts("worker:wt-1") == 2
    assert led.exhausted("worker:wt-1") is True


def test_the_cap_still_refuses_and_says_so(ledger, tmp_path):
    spec = AgentSpec(name="worker", role="impl", prompt="BASE PROMPT")
    dep = RepoDeployer(tmp_path, tmp_path / "sessions")
    wt = tmp_path / "wt-1"

    dep.run_agent(spec, "do the thing", wt, ledger=ledger, dry_run=True)
    dep.run_agent(spec, "do the thing", wt, ledger=ledger, dry_run=True)

    with pytest.raises(RuntimeError, match="attempt cap reached"):
        dep.run_agent(spec, "do the thing", wt, ledger=ledger, dry_run=True)


# --------------------------------------------------------------------- recording the reason
def test_a_failed_attempt_records_why(ledger):
    ledger.record("worker:wt-1")
    ledger.note_outcome("worker:wt-1", "exit 1", "ImportError: no module named connector.base")

    fails = ledger.failures("worker:wt-1")
    assert len(fails) == 1
    assert fails[0]["outcome"] == "exit 1"
    assert "ImportError" in fails[0]["detail"]


def test_an_unreported_outcome_counts_as_a_failure(ledger):
    """A dispatch that never reported back is not a success.

    The process died before it could say what happened. Treating that as 'ok' is the
    UNMEASURABLE-collapsed-into-PASS move this repository exists to refuse, applied to retries.
    """
    ledger.record("worker:wt-1")          # recorded, then the world ended — no note_outcome
    assert len(ledger.failures("worker:wt-1")) == 1
    assert "no outcome recorded" in ledger.context("worker:wt-1")


def test_a_successful_attempt_is_not_replayed_as_a_failure(ledger):
    ledger.record("worker:wt-1")
    ledger.note_outcome("worker:wt-1", "ok", "")
    assert ledger.failures("worker:wt-1") == []
    assert ledger.context("worker:wt-1") == ""


def test_note_outcome_is_safe_when_nothing_was_recorded(ledger):
    ledger.note_outcome("never:dispatched", "exit 1", "should not raise")
    assert ledger.failures("never:dispatched") == []


# --------------------------------------------------------------------- the context itself
def test_the_first_attempt_has_no_context(ledger):
    assert ledger.context("worker:wt-1") == ""


def test_context_is_bounded(ledger):
    """A permanently-failing key must not crowd the task out of its own prompt."""
    big = AttemptLedger(ledger.path, max_attempts=99)
    for i in range(CONTEXT_ATTEMPTS + 4):
        big.record("worker:wt-1")
        big.note_outcome("worker:wt-1", f"exit {i}", f"failure number {i}")

    rendered = big.context("worker:wt-1")
    assert rendered.count("· attempt ") == CONTEXT_ATTEMPTS


def test_context_replays_newest_first(ledger):
    big = AttemptLedger(ledger.path, max_attempts=99)
    big.record("worker:wt-1"); big.note_outcome("worker:wt-1", "exit 1", "OLDEST")
    big.record("worker:wt-1"); big.note_outcome("worker:wt-1", "exit 2", "NEWEST")

    rendered = big.context("worker:wt-1")
    assert rendered.index("NEWEST") < rendered.index("OLDEST")


# --------------------------------------------------------------------- ⭐ the one that matters
def test_the_retry_prompt_carries_the_previous_failure(ledger, tmp_path):
    """The whole point: attempt 2's prompt must contain attempt 1's failure.

    Asserted on what is actually sent — the dry-run transcript records the composed prompt, not
    just the task, precisely so this is checkable without launching an agent.
    """
    spec = AgentSpec(name="worker", role="impl", prompt="BASE PROMPT")
    dep = RepoDeployer(tmp_path, tmp_path / "sessions")
    wt = tmp_path / "wt-1"
    key = "worker:wt-1"

    # Attempt 1 ran and failed for a specific, recoverable reason.
    ledger.record(key)
    ledger.note_outcome(key, "exit 1", "the migration was applied twice; make it idempotent")

    dep.run_agent(spec, "port the connector", wt, ledger=ledger, dry_run=True)

    written = json.loads((tmp_path / "sessions").glob("worker-*.jsonl").__next__()
                         .read_text(encoding="utf-8"))
    prompt = written["prompt"]

    assert "make it idempotent" in prompt, "attempt 2 was dispatched without attempt 1's reason"
    assert "PREVIOUS ATTEMPTS" in prompt
    assert "BASE PROMPT" in prompt          # the agent's own prompt is not lost
    assert "port the connector" in prompt   # nor is the task
    assert written["attempt"] == 2


def test_a_first_dispatch_prompt_has_no_context_block(ledger, tmp_path):
    spec = AgentSpec(name="worker", role="impl", prompt="BASE PROMPT")
    dep = RepoDeployer(tmp_path, tmp_path / "sessions")

    dep.run_agent(spec, "port the connector", tmp_path / "wt-1", ledger=ledger, dry_run=True)

    written = json.loads((tmp_path / "sessions").glob("worker-*.jsonl").__next__()
                         .read_text(encoding="utf-8"))
    assert "PREVIOUS ATTEMPTS" not in written["prompt"]
    assert written["attempt"] == 1
