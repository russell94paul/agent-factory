"""A gate must distinguish "I measured a population and it was clean" from "there was none".

Six gates could not. Each returned PASS over an absence — an empty population, a gutted file, an
unread exit code, or a string the graded party sets itself — and four of them did it with an
**empty evidence list**, which is the tell: a pass that cites nothing usually checked nothing.

⭐ This is the same rule the estate already holds every *verdict* to, applied one level down to the
*population*. `UNMEASURABLE` exists so "I could not look" never reads as "I looked and it was
fine". These gates looked at nothing and reported fine.

Every case below was run against the unfixed code first and observed to PASS; the predictions were
written from reading the source before the run. That ordering matters — a test written after the
fix pins whatever the fix happens to do.

⚠ **What these tests do NOT prove.** They pin the refusal, not the measurement. A gate that
refuses everything would satisfy every case here, so each block carries its positive control: the
same gate, given a real population, must still reach a verdict.
"""
from __future__ import annotations

import os
import pathlib

import pytest

from factory import readiness as R
from factory.pbi_contract import PbiTarget, Probes
from factory.redesign_contract import build_redesign_contract


# ------------------------------------------------------------------ 1. nothing ever completed

def test_success_means_correct_refuses_a_population_with_no_completed_run(monkeypatch):
    """The gate named for the estate's founding failure passed when nothing had succeeded.

    `bad` requires a run carrying BOTH `pipeline_completed` and `stage_failed`. A population where
    nothing completed yields no rows, and the gate reported *"no completed run carried failures"*
    — true, and not a measurement. Observed PASS with evidence `[]` before the fix.
    """
    monkeypatch.setattr(R, "_audits", lambda: [
        {"id": "only-ever-failed", "events": [{"event_type": "stage_failed"}] * 2}])
    r = R.g_success_means_correct()
    assert r.verdict == R.NOT_RUN, r.headline
    assert r.evidence, "a refusal that cites nothing is the defect it replaced"


def test_success_means_correct_still_reaches_a_verdict_over_a_real_population(monkeypatch):
    """Positive control. A gate that only ever refuses has not been fixed, it has been disabled."""
    monkeypatch.setattr(R, "_audits", lambda: [
        {"id": "clean", "events": [{"event_type": "pipeline_completed"}]}])
    assert R.g_success_means_correct().verdict == R.PASS

    monkeypatch.setattr(R, "_audits", lambda: [
        {"id": "success-over-failure",
         "events": [{"event_type": "stage_failed"}, {"event_type": "pipeline_completed"}]}])
    assert R.g_success_means_correct().verdict == R.FAIL


# ------------------------------------------------------------------ 2. every gate deleted

def test_gate_coverage_refuses_when_there_are_no_gates(monkeypatch):
    """`len(checked) == len(gates)` is `0 == 0`, so deleting every gate greened gate coverage."""
    monkeypatch.setattr(R, "_template",
                        lambda: {"p": {"stages": [{"name": "build", "type": "task"}]}})
    r = R.g_gates_have_checks()
    assert r.verdict == R.NOT_RUN, r.headline
    assert any("0 of 0" in e or "no gate" in e.lower() for e in r.evidence)


def test_gate_coverage_still_distinguishes_covered_from_uncovered(monkeypatch):
    """Positive control, both directions."""
    monkeypatch.setattr(R, "_template", lambda: {"p": {"stages": [
        {"name": "g", "type": "gate", "gate_check": "check_it", "gate_type": "qa"}]}})
    assert R.g_gates_have_checks().verdict == R.PASS

    monkeypatch.setattr(R, "_template", lambda: {"p": {"stages": [
        {"name": "g", "type": "gate", "gate_check": None, "gate_type": "qa"}]}})
    assert R.g_gates_have_checks().verdict == R.FAIL


# ------------------------------------------------------------------ 3. the file was gutted

def test_qa_gate_refuses_a_file_that_cannot_contain_the_thing_it_searches_for(tmp_path,
                                                                             monkeypatch):
    """The verdict is the ABSENCE of a substring, and the only assertion was `is_file()`.

    So an emptied file scored PASS with empty evidence. An absence is evidence only once the
    instrument has been shown able to see a presence.
    """
    d = tmp_path / "orchestrator" / "stage_scripts"
    d.mkdir(parents=True)
    (d / "promotion_ops.py").write_text("# contents deleted\n", encoding="utf-8")
    monkeypatch.setattr(R, "CONNECTORS", tmp_path)
    with pytest.raises(R.Unmeasurable):
        R.g_qa_gate_is_general()


def test_qa_gate_still_reaches_both_verdicts_over_a_plausible_file(tmp_path, monkeypatch):
    """Positive control. Anchors are calibrated against the real file: prefect-connectors@main is
    241 lines with 7 `def`s and 48 mentions of 'deployment'."""
    d = tmp_path / "orchestrator" / "stage_scripts"
    d.mkdir(parents=True)
    p = d / "promotion_ops.py"
    monkeypatch.setattr(R, "CONNECTORS", tmp_path)

    p.write_text("def promote(connector):\n    return f'{connector}-deployment'\n",
                 encoding="utf-8")
    assert R.g_qa_gate_is_general().verdict == R.PASS

    p.write_text("def promote(connector):\n    return f'smoke-test-{connector}-deployment'\n",
                 encoding="utf-8")
    assert R.g_qa_gate_is_general().verdict == R.FAIL


# ------------------------------------------------------------------ 4. "pushed" was never tested

class _Run:
    """Stands in for `subprocess.run` across the gate's two calls."""

    def __init__(self, remote_rc=0, remote_out="origin\n", log_rc=0, log_out=""):
        self._r = (remote_rc, remote_out)
        self._l = (log_rc, log_out)
        self.calls = 0

    def __call__(self, argv, **kw):
        self.calls += 1
        rc, out = self._r if argv[:2] == ["git", "remote"] else self._l
        return type("R", (), {"returncode": rc, "stdout": out,
                              "stderr": "fatal: could not read from remote repository\n"})()


def test_durability_refuses_when_the_git_command_failed(monkeypatch):
    """It never inspected the return code. A remote NAMED by a command that exited 128 was
    reported as `pushed to origin`, with empty evidence."""
    monkeypatch.setattr(R.subprocess, "run", _Run(remote_rc=128))
    with pytest.raises(R.Unmeasurable):
        R.g_repo_is_durable()


def test_durability_fails_when_commits_exist_only_on_this_disk(monkeypatch):
    """⭐ The word in the headline is *pushed*, and nothing measured it. A repository 200 commits
    ahead of its remote reported itself durable."""
    monkeypatch.setattr(R.subprocess, "run",
                        _Run(log_out="abc1234 a commit that never left\ndef5678 nor this one\n"))
    r = R.g_repo_is_durable()
    assert r.verdict == R.FAIL, r.headline
    assert "2 commit" in r.headline


def test_durability_passes_only_when_every_commit_has_left(monkeypatch):
    """Positive control."""
    monkeypatch.setattr(R.subprocess, "run", _Run(log_out=""))
    r = R.g_repo_is_durable()
    assert r.verdict == R.PASS
    assert r.evidence, "a pass about durability must cite what it counted"


def test_durability_still_fails_with_no_remote_at_all(monkeypatch):
    monkeypatch.setattr(R.subprocess, "run", _Run(remote_out="\n"))
    assert R.g_repo_is_durable().verdict == R.FAIL


# ------------------------------------------------- 5. a string the graded party sets itself

def test_evaluator_gate_refuses_a_string_that_is_not_an_endpoint(monkeypatch):
    """⛔ The pass condition was `endpoint and impl` — any non-empty string.

    `AGENT_FACTORY_EVALUATOR=totally-not-a-service` returned PASS, headline *"the evaluator is a
    separate principal (remote deployment)"*, directly above its own evidence line reading
    *"health check: NO ANSWER — configured is not running"*. The variable is set by the party the
    gate exists to hold at arm's length, so an unvalidated string is a self-awarded pass.
    """
    monkeypatch.setenv("AGENT_FACTORY_EVALUATOR", "totally-not-a-service")
    r = R.g_evaluator_is_a_service()
    assert r.verdict == R.NOT_RUN, r.headline
    assert any("not an" in e and "endpoint" in e for e in r.evidence)


def test_evaluator_gate_still_passes_for_a_real_endpoint_that_is_merely_down(monkeypatch):
    """⚠ Positive control AND a deliberate boundary.

    Reachability stays out of the pass condition on purpose: this gate asks whether the evaluator
    IS a separate principal, not whether it is up this second, and a service that is down is still
    a separate principal. A string that is not an endpoint names no principal at all — a different
    claim, and the one that was going green.
    """
    monkeypatch.setenv("AGENT_FACTORY_EVALUATOR", "http://127.0.0.1:8787")
    assert R.g_evaluator_is_a_service().verdict == R.PASS


def test_evaluator_gate_refuses_when_nothing_is_configured(monkeypatch):
    monkeypatch.delenv("AGENT_FACTORY_EVALUATOR", raising=False)
    assert R.g_evaluator_is_a_service().verdict == R.NOT_RUN


# ------------------------------------------------- 6. an absent key is not an empty one

class _W(Probes):
    def __init__(self, payload):
        self._p = payload

    def writes(self, ctx):
        return self._p


def _r2(payload):
    c = build_redesign_contract(PbiTarget(dataset_id="x"), probes=_W(payload))
    return next(a for a in c.assertions if a.name.startswith("R2")).run({})


def test_r2_refuses_an_evidence_file_that_never_mentions_renames():
    """`w.get("renamed") or []` collapsed "reported empty" and "never reported" into one value.

    ⭐ The correct reasoning already lives twelve lines below in the same function, for the
    dependents list: *"An absent list is NOT-VISIBLE, not 'nothing depends on it' — enumerate,
    never assume."* R2 is the assertion about renames; an evidence file that never mentions them
    has reported nothing, not "nothing happened".
    """
    assert _r2({}).verdict.value == "UNMEASURABLE"


def test_r2_accepts_an_explicit_declaration_that_nothing_was_renamed():
    """Positive control — and the pair that makes the point. These two payloads were previously
    INDISTINGUISHABLE, both returning the same PASS."""
    res = _r2({"renamed": [], "deleted": [], "touched": []})
    assert res.verdict.value == "PASS"
    assert "declared explicitly" in res.detail
