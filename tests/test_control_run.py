"""The controller must assign verdicts from evidence, and must be able to fail.

⭐ **Read the two controls first.** `test_the_contract_can_reach_pass` is the positive control and
it is not decoration: a contract that has never registered a PASS cannot be trusted when it
reports UNMEASURABLE, because "always UNMEASURABLE" and "correctly UNMEASURABLE" are
indistinguishable from the outside. Every negative control below is only worth reading because
that one passes.

⛔ The estate's own precedent for why: a `bash-guard.sh` here exited 127 and blocked nothing for
months while reporting success. A gate nobody has watched fail is a mechanism, not a control.
"""
from __future__ import annotations

import json
import pathlib
import subprocess

import pytest

from factory import control, events, presets, provider, runs
from factory.contract import Unmeasurable, Verdict
from factory.deploy import LIMIT_NONE, UNDETERMINED
from factory.provider import AgentResult, FakeProvider, ProviderError

UI = presets.by_id("ui-control")          # the one preset with a WIRED verifier
UNWIRED = presets.by_id("wrong-number")   # one of the four that name a verifier nobody wired


def _good_result(transcript: pathlib.Path) -> AgentResult:
    return AgentResult(provider="fake", dispatched=True, observable=True, returncode=0,
                       transcript=transcript, limit=LIMIT_NONE, detail="")


def _ctx(tmp_path, result=None, changed="1 uncommitted file(s), 0 commit(s) ahead",
         cost_basis=runs.MEASURED):
    t = tmp_path / "transcript.jsonl"
    t.write_text('{"ok": true}\n', encoding="utf-8")
    wt = tmp_path / "wt"
    wt.mkdir(exist_ok=True)
    return {"result": result if result is not None else _good_result(t),
            "worktree": wt, "changed": changed,
            "cost": {"basis": cost_basis, "sessions": 1, "input": 10, "output": 20}}


def _wired_ok(ctx):
    return True, "the live doc was read; both locked_value and default_value are empty"


# ------------------------------------------------------------------ the eligible set (R19 §5)

def test_a_run_cannot_start_without_the_eligible_set():
    """The one field that is gone the instant the process exits is REFUSED, not defaulted."""
    with pytest.raises(events.EventError, match="eligible set"):
        events.RunLog.start(ticket="t1", eligible=[], chosen=None, rule="anything")


def test_an_eligible_set_that_contradicts_the_choice_is_refused():
    with pytest.raises(events.EventError, match="not in the eligible set"):
        events.RunLog.start(ticket="t1", chosen="nope", rule="r",
                            eligible=[{"id": "ui-control", "chosen": True}])
    with pytest.raises(events.EventError, match="contradicts|must agree|marks"):
        events.RunLog.start(ticket="t1", chosen="ui-control", rule="r",
                            eligible=[{"id": "ui-control", "chosen": False}])


def test_a_rule_is_required_because_a_list_of_names_loses_the_reasoning():
    with pytest.raises(events.EventError, match="rule"):
        events.RunLog.start(ticket="t1", chosen="ui-control", rule="  ",
                            eligible=[{"id": "ui-control", "chosen": True}])


def test_run_started_records_every_candidate_not_only_the_winner():
    """An undeclared ticket type must leave all five on disk, with the tie-break stated."""
    el, chosen, rule = control.eligible(control.Ticket(id="t2", title="something"))
    log = events.RunLog.start(ticket="t2", eligible=el, chosen=chosen, rule=rule)
    rec = events.read(log.run_id)[0]
    assert len(rec["eligible"]) == len(presets.PRESETS), "the set that was not taken is the point"
    assert [e["id"] for e in rec["eligible"] if e["chosen"]] == [chosen]
    assert rec["rule"] == rule and rec["rule"].strip()
    not_taken = [e for e in rec["eligible"] if not e["chosen"]]
    assert all(e["why"] for e in not_taken), "every candidate carries why it was not taken"


# ------------------------------------------------------- a verdict may only come from the enum

def test_a_terminal_event_cannot_carry_a_string_verdict():
    """A provider or an agent naming its own outcome is the failure R3 ranks first."""
    log = events.RunLog.start(ticket="t3", chosen="ui-control", rule="r",
                              eligible=[{"id": "ui-control", "chosen": True}])
    with pytest.raises(events.EventError, match="must be a factory.contract.Verdict"):
        log.finish("PASS")
    with pytest.raises(events.EventError, match="verdict"):
        log.emit("run_finished", verdict="PASS")


def test_the_stream_can_express_all_five_verdicts():
    """An event stream that cannot say UNMEASURABLE has collapsed the distinction this repo
    exists to protect — and ERROR is the fifth, which prose written before 2026-08-29 omits."""
    for v in Verdict:
        log = events.RunLog.start(ticket=f"t-{v.value}", chosen="ui-control", rule="r",
                                  eligible=[{"id": "ui-control", "chosen": True}])
        log.finish(v)
        assert events.fold(log.run_id)["verdict"] == v.value


# ------------------------------------------------------------------------- ⭐ POSITIVE CONTROL

def test_the_contract_can_reach_pass(tmp_path):
    """The instrument registers a non-zero. Every negative control below depends on this one.

    ⛔ If this test ever starts failing, the UNMEASURABLE results elsewhere in this file stop
    being measurements and become the contract's only possible output. Fix this before believing
    any other verdict here.
    """
    res = control.assertions(UI, verifier=_wired_ok).run(_ctx(tmp_path))
    assert res.verdict is Verdict.PASS, res.summary()
    assert all(r.verdict is Verdict.PASS for r in res.results), res.summary()


# ------------------------------------------------------------------------- ⭐ NEGATIVE CONTROLS

def test_an_unobservable_run_is_unmeasurable_not_pass(tmp_path):
    """The supervised path: a human is watching and this process cannot read them.

    Not a pass — nobody looked. Not a failure — nothing was observed to fail.
    """
    r = AgentResult(provider="supervised-terminal", dispatched=True, observable=False,
                    returncode=None, transcript=None, limit=UNDETERMINED,
                    detail="a human is supervising this run")
    res = control.assertions(UI, verifier=_wired_ok).run(_ctx(tmp_path, result=r))
    assert res.verdict is Verdict.UNMEASURABLE, res.summary()
    obs = next(x for x in res.results if x.name == "outcome_observable")
    assert obs.verdict is Verdict.UNMEASURABLE
    assert "cannot observe" in obs.detail


def test_removing_the_observability_raise_turns_that_run_green(tmp_path, monkeypatch):
    """⭐ The mutation that proves the test above is load-bearing.

    The requirement is not "assert UNMEASURABLE"; it is "and it fails if that mapping is removed".
    So remove it: replace the `Unmeasurable` raise with the pass it would degrade into, and
    demonstrate the same evidence now yields PASS. If this test stops distinguishing the two, the
    negative control above has become a tautology.
    """
    r = AgentResult(provider="supervised-terminal", dispatched=True, observable=False,
                    returncode=None, transcript=None, limit=UNDETERMINED, detail="supervised")
    ctx = _ctx(tmp_path, result=r)

    before = control.assertions(UI, verifier=_wired_ok).run(ctx)
    assert before.verdict is Verdict.UNMEASURABLE

    real = control.assertions

    def mutated(preset, verifier=None):
        gc = real(preset, verifier)
        # The mutation: every assertion that declines to measure an unobservable run now waves it
        # through, exactly as a careless simplification of those raises would.
        for a in gc.assertions:
            if a.name in ("outcome_observable", "exited_clean", "transcript_kept",
                          "work_landed"):
                a.check = lambda ctx, _n=a.name: (True, f"{_n} waved through by the mutation")
        return gc

    monkeypatch.setattr(control, "assertions", mutated)
    after = control.assertions(UI, verifier=_wired_ok).run(ctx)
    assert after.verdict is Verdict.PASS, (
        "the mutation did not change the verdict, so the negative control is not testing the "
        "mapping it claims to test")
    assert before.verdict != after.verdict


def test_an_unwired_verifier_is_unmeasurable_however_clean_the_run(tmp_path):
    """Four of the five presets name a verifier nobody has wired. A perfect run of one of them
    still cannot say whether the ticket's work was done, and must not report PASS."""
    assert UNWIRED.verifier_state != presets.WIRED
    res = control.assertions(UNWIRED, verifier=_wired_ok).run(_ctx(tmp_path))
    assert res.verdict is Verdict.UNMEASURABLE, res.summary()
    tv = next(x for x in res.results if x.name == "ticket_verifier")
    assert tv.verdict is Verdict.UNMEASURABLE and "not\nWIRED" in tv.detail.replace(" ", "\n")


def test_a_declared_verifier_with_no_callable_is_unmeasurable_not_pass(tmp_path):
    """The preset says WIRED and the controller was handed nothing to run. The declaration and
    the wiring disagree, and the honest verdict is that nobody checked."""
    res = control.assertions(UI, verifier=None).run(_ctx(tmp_path))
    assert res.verdict is Verdict.UNMEASURABLE
    tv = next(x for x in res.results if x.name == "ticket_verifier")
    assert "disagree" in tv.detail


def test_an_agent_that_changed_nothing_is_a_failure_not_an_unknown(tmp_path):
    """We could look, and nothing happened. That is FAIL — collapsing it into UNMEASURABLE would
    excuse the one outcome the ticket most needs to catch."""
    res = control.assertions(UI, verifier=_wired_ok).run(_ctx(tmp_path, changed=""))
    assert res.verdict is Verdict.FAIL
    wl = next(x for x in res.results if x.name == "work_landed")
    assert wl.verdict is Verdict.FAIL


def test_an_unobserved_run_says_nothing_about_the_worktree(tmp_path):
    """⛔ The regression. Caught by the first real dry run through the controller, 2026-08-30.

    Every other assertion gated on `observable` and `work_landed` did not, so a dry run — in which
    no agent executes and the worktree is untouched by design — was reported as
    **FAIL: the agent altered nothing**. Every supervised launch would have gone the same way,
    since it returns before the human has typed anything. Fails without the gate.
    """
    r = AgentResult(provider="headless-cli", dispatched=True, observable=False,
                    returncode=0, detail="dry run")
    res = control.assertions(UI, verifier=_wired_ok).run(_ctx(tmp_path, result=r, changed=""))
    wl = next(x for x in res.results if x.name == "work_landed")
    assert wl.verdict is Verdict.UNMEASURABLE, (
        "an unchanged worktree is evidence about an agent only if an agent ran and somebody "
        "watched it")
    assert res.verdict is Verdict.UNMEASURABLE, res.summary()


def test_an_unmeasured_worktree_is_unmeasurable_not_a_clean_one(tmp_path):
    """`changed=None` means the git call failed. That is not 'the agent altered nothing'."""
    res = control.assertions(UI, verifier=_wired_ok).run(_ctx(tmp_path, changed=None))
    wl = next(x for x in res.results if x.name == "work_landed")
    assert wl.verdict is Verdict.UNMEASURABLE


def test_a_missing_cost_is_not_a_zero(tmp_path):
    res = control.assertions(UI, verifier=_wired_ok).run(
        _ctx(tmp_path, cost_basis=runs.NOT_RECORDED))
    cm = next(x for x in res.results if x.name == "cost_measured")
    assert cm.verdict is Verdict.UNMEASURABLE and "NOT-RECORDED rather than zero" in cm.detail


def test_an_instrument_that_crashes_is_error_not_fail(tmp_path):
    """TTCN-3's lattice: once the apparatus has broken we cannot claim the failure was real."""
    def boom(ctx):
        raise ValueError("the verifier itself fell over")
    res = control.assertions(UI, verifier=boom).run(_ctx(tmp_path))
    assert res.verdict is Verdict.ERROR, res.summary()


# --------------------------------------------------------------------------- the vertical slice

@pytest.fixture()
def git_worktree(tmp_path):
    """A real git checkout with an uncommitted change, so `_changed` measures something true."""
    wt = tmp_path / "wt"
    wt.mkdir()
    for args in (["init", "-q"], ["config", "user.email", "t@t"], ["config", "user.name", "t"]):
        subprocess.run(["git", "-C", str(wt), *args], capture_output=True, check=True)
    (wt / "work.txt").write_text("the agent changed this\n", encoding="utf-8")
    return wt


def _controller(git_worktree, tmp_path, result=None, rows=None, verifier=_wired_ok, raises=None):
    t = tmp_path / "transcript.jsonl"
    t.write_text('{"type":"result"}\n', encoding="utf-8")
    fake = FakeProvider(result=result if result is not None else _good_result(t), raises=raises)
    rows = rows if rows is not None else []

    def record(**kw):
        rows.append(kw)
        return dict(kw)

    return fake, rows, control.RunController(
        fake,
        worktree=lambda _id: git_worktree,
        claim=lambda _id: True,
        release=lambda _id: True,
        verifier=verifier,
        record=record,
        cost=lambda _cwd: {"basis": runs.MEASURED, "sessions": 1, "input": 5, "output": 7},
    )


def test_one_ticket_runs_end_to_end_and_lands_in_both_ledgers(git_worktree, tmp_path):
    """⭐ The vertical slice: ticket -> preset -> TeamSpec -> agent -> verdict -> record."""
    fake, rows, ctl = _controller(git_worktree, tmp_path)
    res = ctl.run(control.Ticket(id="gp-327", title="remove two filters", type_id="ui-control",
                                 task="Remove the two empty filters from the dashboard."))

    assert res.verdict is Verdict.PASS, res.summary()
    assert res.preset_id == "ui-control"

    # the stream
    kinds = [e["kind"] for e in events.read(res.run_id)]
    assert kinds == ["run_started", "worktree_ready", "claim_taken", "agent_dispatched",
                     "agent_returned", "evidence_gathered", "verdict_assigned", "run_finished"]
    fold = events.fold(res.run_id)
    assert fold["verdict"] == "PASS"
    assert fold["chosen"] == "ui-control"
    assert fold["team_version"] and fold["agent_versions"]

    # the fold
    assert len(rows) == 1
    row = rows[0]
    assert row["outcome"] == "PASS"
    for f in runs.ATTRIBUTION:
        assert row.get(f) not in (None, "", runs.NOT_RECORDED), (
            f"{f} is the join every later question needs and it is missing at write time")


def test_the_agent_is_configured_from_the_preset_not_from_a_default(git_worktree, tmp_path):
    """The provider receives the preset's model, caps and prohibition — otherwise the preset table
    is decoration and every run silently uses the session default."""
    fake, _rows, ctl = _controller(git_worktree, tmp_path)
    ctl.run(control.Ticket(id="gp-327", title="t", type_id="ui-control"))
    spec, task, wt = fake.calls[0]
    assert (spec.model, spec.max_turns, spec.budget_usd) == (UI.model, UI.max_turns, UI.budget_usd)
    assert spec.prohibition == UI.prohibition
    assert UI.prohibition in spec.prompt and UI.escalate_when in spec.prompt
    assert pathlib.Path(wt) == git_worktree


def test_the_provider_boundary_is_real(git_worktree, tmp_path):
    """⭐ Substitution proven with a FAKE the controller drives identically — not by adding a
    second real provider, which would be scope and would prove less."""
    t = tmp_path / "tr.jsonl"
    t.write_text("{}\n", encoding="utf-8")
    a = _good_result(t)
    b = AgentResult(provider="another-fake", dispatched=True, observable=True, returncode=0,
                    transcript=t, limit=LIMIT_NONE)
    for result in (a, b):
        fake, _rows, ctl = _controller(git_worktree, tmp_path, result=result)
        res = ctl.run(control.Ticket(id="gp-327", title="t", type_id="ui-control"))
        assert res.verdict is Verdict.PASS
        assert len(fake.calls) == 1, "the controller called the seam exactly once"


def test_a_provider_that_refuses_to_dispatch_is_not_run_not_fail(git_worktree, tmp_path):
    """An exhausted attempt cap is the ledger doing its job. Nothing ran, so nothing was measured."""
    _fake, rows, ctl = _controller(git_worktree, tmp_path,
                                   raises=ProviderError("attempt cap reached for x (2/2)"))
    res = ctl.run(control.Ticket(id="gp-327", title="t", type_id="ui-control"))
    assert res.verdict is Verdict.NOT_RUN
    assert events.fold(res.run_id)["terminal"] == "run_aborted"
    assert rows == [], "a run that never dispatched must not appear in the ledger as an outcome"


def test_a_broken_harness_is_error_and_the_eligible_set_still_survives(git_worktree, tmp_path):
    """The worktree could not be made. ERROR, and the choice is still on disk — which is the
    entire reason the eligible set is written before anything else can fail."""
    fake = FakeProvider()
    ctl = control.RunController(fake, worktree=_boom, claim=lambda _i: True,
                                release=lambda _i: True, record=lambda **kw: kw)
    res = ctl.run(control.Ticket(id="gp-327", title="t", type_id="ui-control"))
    assert res.verdict is Verdict.ERROR
    evs = events.read(res.run_id)
    assert evs[0]["kind"] == "run_started" and evs[0]["eligible"]
    assert evs[-1]["kind"] == "run_aborted" and evs[-1]["verdict"] == "ERROR"
    assert fake.calls == [], "no agent may be dispatched after the harness broke"


def _boom(_ticket_id):
    raise OSError("could not create the worktree")


def test_a_ticket_no_preset_matches_is_recorded_without_inventing_a_run():
    """Nothing eligible is a finding about the preset table, not a run with an empty list."""
    ctl = control.RunController(FakeProvider())
    res = ctl.run(control.Ticket(id="gp-999", title="t", type_id="no-such-type"))
    assert res.verdict is Verdict.NOT_RUN
    rec = events.read()[-1]
    assert rec["kind"] == "run_aborted" and rec["started"] is False
    assert rec["considered"] and "eligible" not in rec, (
        "considered and eligible are different questions and must not share a field")


def test_a_run_still_in_flight_keeps_its_claim(git_worktree, tmp_path):
    """⛔ The supervised terminal returns while the human is still typing in it.

    Releasing the claim here would let the next launch put a second agent into the same checkout —
    the 41.7% different-agent conflict case. An observable run releases; an unobservable one does
    not, and the event says which happened.
    """
    released = []
    supervised = AgentResult(provider="supervised-terminal", dispatched=True, observable=False,
                             in_flight=True, detail="a human is supervising this run")
    # ⛔ The third case is the bug this grew to cover. A dry run is unobservable AND finished;
    # deriving in_flight from observable made it retain its claim, which then blocked the next
    # launch of that ticket with "liveness could NOT be verified" — a deadlock caused by nothing.
    dry = AgentResult(provider="headless-cli", dispatched=True, observable=False,
                      in_flight=False, returncode=0, detail="dry run")
    for result, expect_release in ((supervised, False), (_good_result(_tx(tmp_path)), True),
                                   (dry, True)):
        released.clear()
        _f, _rows, ctl = _controller(git_worktree, tmp_path, result=result)
        ctl._release = released.append
        res = ctl.run(control.Ticket(id="GP-327", title="t", type_id="ui-control"))
        assert bool(released) is expect_release, (
            f"{result.provider}: claim release should be {expect_release}")
        returned = next(e for e in events.read(res.run_id) if e["kind"] == "agent_returned")
        assert returned["claim_retained"] is (not expect_release)


def test_the_worktree_key_is_normalised_but_the_ledger_keeps_the_real_id(git_worktree, tmp_path):
    """`GP-327` is a real ticket id and is rejected by both `worktrees` and `claims`."""
    keys = []
    _f, rows, ctl = _controller(git_worktree, tmp_path)
    ctl._worktree = lambda k: (keys.append(k), git_worktree)[1]
    res = ctl.run(control.Ticket(id="GP-327", title="t", type_id="ui-control"))
    assert keys == ["gp-327"], "git and the lock file get the normalised key"
    assert rows[0]["lane"] == "GP-327" and rows[0]["job"] == "GP-327", "the ledger keeps the id"
    assert events.fold(res.run_id)["ticket"] == "GP-327"


def _tx(tmp_path):
    t = tmp_path / "tx.jsonl"
    t.write_text("{}\n", encoding="utf-8")
    return t


def test_a_dry_run_is_unmeasurable_not_a_failure_to_do_work(git_worktree, tmp_path, monkeypatch):
    """The exit 0 a dry run returns belongs to the recorder, not to an agent.

    Reported as observable it would reach the contract as a clean run that changed nothing — FAIL,
    reading as "the agent did no work" when the truth is "no agent ran". Different remedies,
    different verdicts.
    """
    from factory import deploy, provider as provmod

    class _Dep:
        def __init__(self, *a, **k):
            pass

        def run_agent(self, spec, task, wt, ledger=None, dry_run=False):
            t = tmp_path / "dry.jsonl"
            t.write_text('{"dry_run": true}\n', encoding="utf-8")
            return deploy.Deployment(wt, "b", t, returncode=0)

    monkeypatch.setattr(provmod, "RepoDeployer", _Dep)
    p = provmod.HeadlessProvider(tmp_path, tmp_path / "s", dry_run=True)
    r = p.run(control.team_for(control.Ticket(id="x", title="t"), UI).agents[0], "do it", tmp_path)
    assert r.dispatched and not r.observable and r.extra["dry_run"] is True
    res = control.assertions(UI, verifier=_wired_ok).run(_ctx(tmp_path, result=r))
    assert res.verdict is Verdict.UNMEASURABLE, res.summary()


def test_the_supervised_provider_never_claims_to_have_seen_the_outcome(tmp_path):
    """The path that actually runs today. It reports dispatched-and-unobservable, always."""
    sp = provider.SupervisedProvider(spawn=lambda spec, task, wt: "pid 1234")
    r = sp.run(control.team_for(control.Ticket(id="x", title="t"), UI).agents[0], "do it", tmp_path)
    assert r.dispatched and not r.observable
    assert r.returncode is None and r.limit == UNDETERMINED
