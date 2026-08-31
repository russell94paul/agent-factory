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

from factory import deploy as deploy_mod
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
    """The cap is exhausted by REAL dispatches — and a dry run still reports that it is.

    ⚠ This test used to exhaust the cap with three `dry_run=True` calls, which is how F85 hid:
    the suite's own way of reaching the cap was the bug. Reading the cap costs nothing, so a
    plan-only call must still refuse and say why; what it must not do is spend one.
    """
    spec = AgentSpec(name="worker", role="impl", prompt="BASE PROMPT")
    dep = RepoDeployer(tmp_path, tmp_path / "sessions")
    wt = tmp_path / "wt-1"

    ledger.record("worker:wt-1")          # two real dispatches, which is what a cap counts
    ledger.record("worker:wt-1")

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
    assert written["would_be_attempt"] == 2


def test_a_first_dispatch_prompt_has_no_context_block(ledger, tmp_path):
    spec = AgentSpec(name="worker", role="impl", prompt="BASE PROMPT")
    dep = RepoDeployer(tmp_path, tmp_path / "sessions")

    dep.run_agent(spec, "port the connector", tmp_path / "wt-1", ledger=ledger, dry_run=True)

    written = json.loads((tmp_path / "sessions").glob("worker-*.jsonl").__next__()
                         .read_text(encoding="utf-8"))
    assert "PREVIOUS ATTEMPTS" not in written["prompt"]
    assert written["would_be_attempt"] == 1


# --------------------------------------------------------------------- the limit field
# "Did it run out of room" is a DIFFERENT question from "did it work". Modelled on
# inspect_ai's EvalSample.limit. Before this, a cap-kill was recorded as a plain failure
# and the retry was told to change approach — wrong advice when the approach was fine.
from factory.deploy import LIMIT_HIT, LIMIT_NONE, UNDETERMINED   # noqa: E402


def test_a_cap_kill_is_not_reported_as_a_wrong_approach(ledger):
    ledger.record("worker:wt-1")
    ledger.note_outcome("worker:wt-1", "exit 1", "turn ceiling reached", limit=LIMIT_HIT)

    rendered = ledger.context("worker:wt-1")
    assert "a cap ended it, not the approach" in rendered
    assert "continue it — do not restart from scratch" in rendered
    assert "Do something different" not in rendered, \
        "a run that merely ran out of turns must not be told its approach was wrong"


def test_an_undetermined_cause_refuses_to_prescribe(ledger):
    """The CLI gives no signal separating a cap-kill from a crash, so the honest render says so."""
    ledger.record("worker:wt-1")
    ledger.note_outcome("worker:wt-1", "exit 1", "no stderr captured", limit=UNDETERMINED)

    rendered = ledger.context("worker:wt-1")
    assert "UNDETERMINED" in rendered
    assert "Do not assume the previous approach was wrong" in rendered
    assert "Do something different" not in rendered


def test_a_known_non_cap_failure_still_says_change_approach(ledger):
    ledger.record("worker:wt-1")
    ledger.note_outcome("worker:wt-1", "exit 1", "assertion failed", limit=LIMIT_NONE)
    assert "Do something different" in ledger.context("worker:wt-1")


def test_a_real_dispatch_records_undetermined_not_none(ledger, tmp_path, monkeypatch):
    """⛔ The regression that matters: a non-zero exit must never be recorded as 'not a cap'.

    Asserting LIMIT_NONE there would be an unmeasured thing asserted as measured — the exact
    collapse this module refuses everywhere else.

    ⚠ This test did not do that. It was named for a real dispatch, performed a `dry_run=True`
    one, and asserted `limit == LIMIT_NONE` — the opposite value, on the one path that cannot
    exhibit the regression, since a dry run never reaches the exit-code branch at all. The
    mapping it claims to guard was untested from the day it was written. It now drives the real
    path with a stubbed process, which is the only way to reach that branch without an agent.
    """
    class _Proc:
        returncode = 1
        def communicate(self, input=None):        # noqa: A002 - mirrors subprocess' own name
            return ("", "Traceback: the connector module does not import")

    monkeypatch.setattr(deploy_mod.subprocess, "Popen", lambda *a, **k: _Proc())

    spec = AgentSpec(name="worker", role="impl", prompt="BASE")
    dep = RepoDeployer(tmp_path, tmp_path / "sessions")
    dep.run_agent(spec, "t", tmp_path / "wt-1", ledger=ledger)

    entry = ledger._entry("worker:wt-1")["attempts"][-1]
    assert entry["outcome"] == "exit 1"
    assert entry["limit"] == UNDETERMINED,         "a non-zero exit was recorded as demonstrably-not-a-cap, which nothing measured"
    assert "does not import" in entry["detail"]


# --------------------------------------------------------------- ⭐ F85: a plan is not an attempt
def test_a_dry_run_does_not_spend_an_attempt(ledger, tmp_path):
    """⛔ Plan-only must not consume the cap. Two dry runs used to make a ticket unrunnable.

    `max_attempts` is 2, so the second plan-only invocation exhausted the cap and every real
    dispatch afterwards was refused by a message that says the cap must not be raised to get
    past it. Measured live on `ui-control-agent:gp-327`, whose two blocking entries both read
    `detail: "dry run"`.
    """
    spec = AgentSpec(name="worker", role="impl", prompt="BASE PROMPT")
    dep = RepoDeployer(tmp_path, tmp_path / "sessions")
    wt = tmp_path / "wt-1"

    for _ in range(5):
        dep.run_agent(spec, "do the thing", wt, ledger=ledger, dry_run=True)

    assert ledger.attempts("worker:wt-1") == 0, "a plan-only run was counted as a dispatch"
    assert not ledger.exhausted("worker:wt-1")

    # and the real dispatch it was planning is still allowed to happen
    assert AttemptLedger(ledger.path, max_attempts=2).exhausted("worker:wt-1") is False


def test_a_dry_run_does_not_overwrite_the_previous_attempts_outcome(ledger, tmp_path):
    """The other half of the fix, and the more dangerous half.

    `note_outcome()` writes to `attempts[-1]`. A dry run that records no attempt of its own but
    still calls it would stamp "ok"/"dry run" onto the PREVIOUS REAL attempt — deleting a
    genuine failure from `failures()`, and so from the retry context the next real dispatch is
    given. The agent would then repeat the approach that already failed, against a cap it
    cannot raise.
    """
    spec = AgentSpec(name="worker", role="impl", prompt="BASE PROMPT")
    dep = RepoDeployer(tmp_path, tmp_path / "sessions")
    key = "worker:wt-1"

    ledger.record(key)
    ledger.note_outcome(key, "exit 1", "the migration was applied twice", limit=LIMIT_NONE)

    dep.run_agent(spec, "do the thing", tmp_path / "wt-1", ledger=ledger, dry_run=True)

    fails = ledger.failures(key)
    assert len(fails) == 1, "the real failure stopped being a failure"
    assert fails[0]["outcome"] == "exit 1"
    assert "applied twice" in ledger.context(key)
