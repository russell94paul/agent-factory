"""The known-failure preflight, replayed against the real GP-327 history.

⭐ **The fixture is not invented.** `GP327_EVENTS` below is a verbatim reduction of the seven
GP-327 runs in `.data/events.jsonl` as they stood on 2026-08-31 — same order, same verdicts, same
assertion names, same abort reason. It is copied into the test rather than read from `.data/`
because `.data/` is gitignored, machine-local and still being written to by live sessions: a test
that read it would pass or fail depending on what somebody else ran an hour ago, which is the
`WRONG_POPULATION` family reproduced inside its own regression test.

⛔ **The negative controls are the point.** Any test suite can show a preflight producing a
warning. These also show it staying silent on a first attempt, refusing to classify a failure it
does not understand, and — the one that matters most — **never refusing a run**.
"""
from __future__ import annotations

import json

import pytest

from factory import events, preflight, reliability, runs
from factory.contract import Verdict

# --------------------------------------------------------------------------------- the fixture

_VERIFIER_UNWIRED = ("preset 'ui-control' declares a WIRED verifier but the controller was given "
                     "no callable to run. The declaration and the wiring disagree.")
_NOT_OBSERVABLE = "headless-cli cannot observe this run's outcome (dry run …)"
_CAP = ("attempt cap reached for ui-control-agent:gp-327 (2/2). Escalate to a human — do not "
        "raise the cap to get past this.")


def _results(work_landed: str):
    return [
        {"name": "agent_dispatched", "verdict": "PASS", "detail": "the provider dispatched"},
        {"name": "outcome_observable", "verdict": "UNMEASURABLE", "detail": _NOT_OBSERVABLE},
        {"name": "exited_clean", "verdict": "UNMEASURABLE", "detail": "not observable"},
        {"name": "transcript_kept", "verdict": "UNMEASURABLE", "detail": "no transcript expected"},
        {"name": "work_landed", "verdict": work_landed, "detail": "the worktree is unchanged"},
        {"name": "ticket_verifier", "verdict": "UNMEASURABLE", "detail": _VERIFIER_UNWIRED},
        {"name": "cost_measured", "verdict": "UNMEASURABLE", "detail": "cost basis NOT-RECORDED"},
    ]


#: The seven GP-327 runs, oldest first. Attempts 1,2,4,5,6,7 are contract verdicts; attempt 3 is
#: the abort where the cap those six had spent finally refused a dispatch.
GP327_EVENTS = []


def _run(run_id, at, verdict, *, aborted=False, work_landed="UNMEASURABLE"):
    base = {"run": run_id, "ticket": "GP-327", "at": at}
    GP327_EVENTS.append({**base, "seq": 1, "kind": "run_started", "chosen": "ui-control",
                         "rule": "the preset whose type_id matches the ticket",
                         "eligible": [{"id": "ui-control", "chosen": True}],
                         "team": "ui-control-team"})
    if aborted:
        GP327_EVENTS.append({**base, "seq": 2, "kind": "run_aborted", "verdict": verdict,
                             "why": _CAP})
        return
    GP327_EVENTS.append({**base, "seq": 2, "kind": "verdict_assigned", "verdict": verdict,
                         "contract": "run", "results": _results(work_landed)})
    GP327_EVENTS.append({**base, "seq": 3, "kind": "run_finished", "verdict": verdict})


_run("20260830T133448-a1ffafae", "2026-08-30T13:34:48+00:00", "FAIL", work_landed="FAIL")
_run("20260830T133548-76230bbb", "2026-08-30T13:35:48+00:00", "UNMEASURABLE")
_run("20260831T034120-d9f606a8", "2026-08-31T03:41:20+00:00", "NOT_RUN", aborted=True)
_run("20260831T034638-1a0176a8", "2026-08-31T03:46:38+00:00", "UNMEASURABLE")
_run("20260831T034640-d39718fa", "2026-08-31T03:46:40+00:00", "UNMEASURABLE")
_run("20260831T034641-226e9417", "2026-08-31T03:46:41+00:00", "UNMEASURABLE")
_run("20260831T044024-46467dfe", "2026-08-31T04:40:24+00:00", "UNMEASURABLE")


@pytest.fixture
def stream(tmp_path, monkeypatch):
    """Point the event stream at a temp file holding the GP-327 history.

    ⚠ Every test in this file uses it. A test that wrote to the real `.data/events.jsonl` would
    put fabricated runs into the ledger the metrics are computed from.
    """
    p = tmp_path / "events.jsonl"
    p.write_text("\n".join(json.dumps(e) for e in GP327_EVENTS) + "\n", encoding="utf-8")
    monkeypatch.setattr(events, "path", lambda: p)
    return p


# ------------------------------------------------------------------------------- the replay

def test_every_attempt_after_the_first_is_shown_its_predecessor(stream):
    """⭐ The hypothesis, stated as a test: attempts 2..7 each receive attempt n-1's verdict.

    This is the whole claim of the patch. If it fails, the patch has no reason to exist.
    """
    ids = [e["run"] for e in GP327_EVENTS if e["kind"] == "run_started"]
    assert len(ids) == 7, "the fixture is the seven real GP-327 runs"

    first = preflight.check("GP-327", {}, before=ids[0])
    assert first.prior == [], "the first attempt has no history and must be told nothing"
    assert first.packet == "", "silence on a first attempt — a preflight that always speaks is skimmed"

    for n, run_id in enumerate(ids[1:], start=2):
        m = preflight.check("GP-327", {}, before=run_id)
        assert m.matched, f"attempt {n} was shown nothing"
        assert m.attempt_number == n
        assert m.last.run == ids[n - 2], f"attempt {n} must be shown attempt {n - 1}"
        assert m.last.verdict in ("FAIL", "UNMEASURABLE", "NOT_RUN")
        assert m.packet.startswith("KNOWN_FAILURE_MATCH")


def test_a_preflight_cannot_read_the_future(stream):
    """⚠ Regression. The first version skipped the matching run id instead of truncating at it.

    Replaying attempt 1 therefore handed it the six attempts that had not happened yet, so every
    replayed attempt looked equally well-informed and the replay proved nothing. Caught by the
    test above on its first run; this is the anchor that keeps it caught.
    """
    ids = [e["run"] for e in GP327_EVENTS if e["kind"] == "run_started"]
    for n, run_id in enumerate(ids, start=1):
        seen = [a.run for a in preflight.prior_attempts("GP-327", before=run_id)]
        assert seen == ids[:n - 1], f"attempt {n} must see exactly the {n - 1} runs before it"


def test_the_six_verifier_runs_land_in_one_family_and_the_cap_abort_does_not(stream):
    """Six DECLARATION_WITHOUT_MECHANISM, one UNBOUNDED_RETRY — not seven of anything.

    A taxonomy that put all seven in one bucket would be describing "GP-327 failed" rather than
    classifying how, and the two have different repairs: wire a verifier, versus stop spending the
    cap on dry runs.
    """
    attempts = preflight.prior_attempts("GP-327")
    assert len(attempts) == 7
    families = [a.family for a in attempts]
    assert families.count(preflight.DECLARATION_WITHOUT_MECHANISM) == 6
    assert families.count(preflight.UNBOUNDED_RETRY) == 1
    assert attempts[2].family == preflight.UNBOUNDED_RETRY, "attempt 3 is the cap abort"
    assert attempts[2].classified_by.startswith("provider_cap")


def test_the_reason_names_the_assertion_the_family_came_from(stream):
    """⚠ Regression. The packet must not explain its family with an unrelated symptom.

    The first version took the FIRST non-passing assertion, which on all six GP-327 contract runs
    was `outcome_observable` — "headless-cli cannot observe this run's outcome (dry run)". So the
    packet named DECLARATION_WITHOUT_MECHANISM and then gave a dry-run symptom as the reason: two
    lines that contradict each other, which is worse than saying nothing. Found by replaying the
    real stream through `scripts/replay_recurrence.py`; every test at the time still passed,
    because they all asserted the family and none read the prose beside it.
    """
    for a in preflight.prior_attempts("GP-327"):
        if a.family == preflight.DECLARATION_WITHOUT_MECHANISM:
            assert a.reason.startswith("ticket_verifier:"), a.reason
            assert "declares a WIRED verifier" in a.reason
        elif a.family == preflight.UNBOUNDED_RETRY:
            assert a.reason.startswith("attempt cap reached")
        assert "cannot observe this run" not in a.reason


def test_a_re_derived_family_says_so(stream):
    """A family read off an event that never carried the field must not look like a recorded one.

    The fixture predates `failure_family` entirely, so every classification here is re-derived.
    Presenting that as if the field had been written would be the NOT-RECORDED/UNCLASSIFIED
    collapse this module exists to keep open.
    """
    for a in preflight.prior_attempts("GP-327"):
        assert "re-derived" in a.classified_by
        assert "NOT-RECORDED" in a.classified_by


def test_the_cap_message_rule_has_not_rotted():
    """⚠ The one text-matching rule in the classifier, guarded against the F19 defect.

    `provider_cap` matches a literal prefix of the message `deploy.RepoDeployer.run_agent` raises.
    A regex guard that silently stops matching the line it was written to catch is a finding this
    repository has already paid for; this test is the anchor that makes the rot loud.
    """
    import inspect

    from factory import deploy
    src = inspect.getsource(deploy.RepoDeployer.run_agent)
    assert preflight._CAP_PREFIX in src, (
        "the attempt-cap message in deploy.py no longer starts with the prefix "
        f"{preflight._CAP_PREFIX!r} that preflight's `provider_cap` rule matches. Fix the rule — "
        "do not weaken this test.")


# ------------------------------------------------------------------ the shadow policy is shadow

def test_would_refuse_is_computed_and_never_enforced(stream):
    """⛔ V0 is WARN-ONLY. A Match must expose no way to stop a run.

    Deliberately a structural assertion rather than a behavioural one: `check()` returning
    normally proves this call did not refuse, and the attribute census proves no caller *could*
    read a refusal off it.
    """
    m = preflight.check("GP-327", {}, before="20260831T044024-46467dfe")
    assert isinstance(m.would_refuse, bool)
    assert m.as_event()["policy"] == "WARN_ONLY_V0"
    assert not hasattr(m, "refuse") and not hasattr(m, "raise_if_known")


def test_would_refuse_needs_a_prevention_check_not_just_a_recurrence(stream):
    """The shadow policy fires only when a check confirms the blocker is still present.

    Without a prevention check, recurrence alone must not set `would_refuse` — that policy would
    refuse every legitimate retry-after-a-fix, and nothing in eight runs has yet shown us a false
    positive because nothing has yet shown us anything.
    """
    bare = preflight.check("GP-327", {}, before="20260831T044024-46467dfe")
    assert bare.prevention.available is False, "no preset in ctx -> no check is possible"
    assert bare.prevention.result == preflight.NOT_RECORDED
    assert bare.would_refuse is False


def test_the_prevention_check_distinguishes_a_fixed_ticket_from_a_repeat(stream):
    """⭐ The field that makes the packet worth reading: is the blocker still there?

    `ui-control` still declares WIRED with nothing behind it (F87), so the check reports
    STILL_PRESENT and the shadow policy would refuse. `add-measure` has a registry callable, so
    the same history against a fixed preset reports CLEARED and would not.
    """
    from factory import presets

    unfixed = preflight.check("GP-327", {"preset": presets.by_id("ui-control")},
                              before="20260831T044024-46467dfe")
    assert unfixed.prevention.available is True
    assert unfixed.prevention.result == "STILL_PRESENT"
    assert unfixed.would_refuse is True, "shadow only — nothing acts on this"

    fixed = preflight.check("GP-327", {"preset": presets.by_id("add-measure")},
                            before="20260831T044024-46467dfe")
    assert fixed.prevention.result == "CLEARED"
    assert fixed.would_refuse is False, "a cleared blocker is a legitimate retry"


def test_the_packet_stays_inside_its_budget(stream):
    """A preflight that dumps history into every context is the failure it exists to prevent."""
    for run_id in [e["run"] for e in GP327_EVENTS if e["kind"] == "run_started"][1:]:
        m = preflight.check("GP-327", {}, before=run_id)
        assert len(m.packet.split()) <= preflight.MAX_PACKET_WORDS
        assert m.as_event()["context_packet_words"] == len(m.packet.split())


# ------------------------------------------------------------------- UNCLASSIFIED vs NOT-RECORDED

def test_an_unmapped_failure_is_unclassified_not_the_nearest_family(stream):
    """GP-401's verifier was WIRED and the agent simply left no evidence — a different situation.

    It must not be filed as DECLARATION_WITHOUT_MECHANISM merely because the same assertion is
    UNMEASURABLE. An unclassified failure is a visible gap; a misclassified one is a gap that
    looks filled.
    """
    c = preflight.classify(
        preflight.SITUATION_CONTRACT, verdict=Verdict.UNMEASURABLE,
        results=[{"name": "ticket_verifier", "verdict": "UNMEASURABLE",
                  "detail": "the agent left no verification evidence at .factory/verification.json"}],
        verifier_declared_wired=True, verifier_callable_present=True)
    assert c.family == preflight.UNCLASSIFIED
    assert c.classified_by == "contract_unmapped"


def test_the_taxonomy_document_names_exactly_the_families_the_code_enforces():
    """⚠ The document and the closed set must not drift.

    This repository has lost three hand-maintained lists to silent drift. A taxonomy file naming a
    family the writer would refuse — or missing one it accepts — is a document that reads as
    authoritative and is wrong, which is the failure mode `registry.py` and `presets.py` both
    already guard against by checking their declarations against the mechanism.
    """
    import pathlib

    import yaml
    doc = pathlib.Path(__file__).resolve().parent.parent / "docs" / "protocol" / "FAILURE_TAXONOMY.yaml"
    listed = [f["family"] for f in yaml.safe_load(doc.read_text(encoding="utf-8"))["families"]]
    assert set(listed) == set(preflight.FAMILIES), (
        f"docs/protocol/FAILURE_TAXONOMY.yaml and factory.preflight.FAMILIES disagree: "
        f"{set(listed) ^ set(preflight.FAMILIES)}")
    assert len(listed) == len(set(listed)), "a family is listed twice"


def test_the_taxonomy_only_cites_findings_that_exist():
    """A family pointing at a finding nobody can open is a citation, not evidence."""
    import pathlib

    import yaml
    from factory import findings
    doc = pathlib.Path(__file__).resolve().parent.parent / "docs" / "protocol" / "FAILURE_TAXONOMY.yaml"
    known = {f.id for f in findings.load()}
    missing = {fid for fam in yaml.safe_load(doc.read_text(encoding="utf-8"))["families"]
               for fid in (fam.get("findings") or []) if fid not in known}
    assert not missing, f"the taxonomy cites findings that the ledger cannot see: {sorted(missing)}"


def test_the_ticket_key_agrees_with_the_controllers(stream):
    """⚠ Two definitions of one normalisation, anchored so drift is loud rather than silent.

    `preflight.ticket_key` and `control.Ticket.key` must agree. They are separate functions only
    because `control` imports `preflight`, so `preflight` cannot import `control` back. This is the
    F29 anchor pattern: a copy of a rule is a copy that drifts, and the guard is a test that
    compares them rather than a comment asking people to remember.
    """
    from factory.control import Ticket
    cases = ("GP-327", "gp-327", "FU92-420", "GP.327", "gp_327", "  GP-327  ", "GP--327",
             "", "   ", "!!!",                       # the fallback edge
             "X" * 80, "GP-" + "9" * 100)            # the truncation edge
    for raw in cases:
        assert preflight.ticket_key(raw) == Ticket(id=raw, title="t").key, raw
    assert preflight.ticket_key("") == "unnamed-ticket"
    assert len(preflight.ticket_key("X" * 80)) == 64


def test_recurrence_is_not_lost_to_the_case_the_operator_typed(stream):
    """⭐ The identity-loss this closes: one work item, two spellings, one history.

    `GP-327` and `gp-327` share a worktree, a claim and an attempt-cap key — they are the same work
    item to every other mechanism in the estate. A raw string match would have made the preflight
    the sole dissenter, and it would have failed by staying **silent**, which is the failure mode
    nobody notices.
    """
    lower = preflight.prior_attempts("gp-327")
    upper = preflight.prior_attempts("GP-327")
    assert [a.run for a in lower] == [a.run for a in upper] != []
    assert preflight.check("gp-327", {}).matched is True


def test_a_pass_cannot_carry_a_family():
    with pytest.raises(preflight.FamilyError):
        preflight.check_family(preflight.HARNESS_FAULT, Verdict.PASS)
    assert preflight.check_family(None, Verdict.PASS) is None


def test_an_unknown_family_is_refused_rather_than_stored():
    with pytest.raises(preflight.FamilyError):
        preflight.check_family("LOOKS_ABOUT_RIGHT", Verdict.FAIL)


def test_an_omitted_family_becomes_unclassified_never_an_absent_key():
    """Going forward the key is always present; absence is reserved for history."""
    assert preflight.check_family(None, Verdict.FAIL) == preflight.UNCLASSIFIED


def test_unclassified_share_separates_the_three_states(stream):
    """All seven fixture runs predate the field, so every one is NOT-RECORDED, not UNCLASSIFIED."""
    share = preflight.unclassified_share()
    assert share["failures"] == 7
    assert share["not_recorded"] == 7
    assert share["unclassified"] == 0 and share["classified"] == 0
    assert share["unclassified_share"] is None, "a share over an empty population is not zero"
    assert share["basis"] == preflight.NOT_RECORDED


# --------------------------------------------------------------------------------- the writer

def test_a_terminal_event_records_its_family(tmp_path, monkeypatch):
    p = tmp_path / "events.jsonl"
    monkeypatch.setattr(events, "path", lambda: p)
    log = events.RunLog.start(ticket="T-1", chosen="ui-control", rule="r",
                              eligible=[{"id": "ui-control", "chosen": True}])
    log.finish(Verdict.FAIL, failure_family=preflight.HARNESS_FAULT, classified_by="a_rule")
    rec = [json.loads(ln) for ln in p.read_text(encoding="utf-8").splitlines()][-1]
    assert rec["failure_family"] == preflight.HARNESS_FAULT
    assert rec["classified_by"] == "a_rule"
    assert events.fold(log.run_id)["failure_family"] == preflight.HARNESS_FAULT


def test_a_green_terminal_event_carries_no_family_key(tmp_path, monkeypatch):
    p = tmp_path / "events.jsonl"
    monkeypatch.setattr(events, "path", lambda: p)
    log = events.RunLog.start(ticket="T-2", chosen="ui-control", rule="r",
                              eligible=[{"id": "ui-control", "chosen": True}])
    log.finish(Verdict.PASS)
    rec = [json.loads(ln) for ln in p.read_text(encoding="utf-8").splitlines()][-1]
    assert "failure_family" not in rec and "classified_by" not in rec


def test_preflight_is_a_non_terminal_kind(tmp_path, monkeypatch):
    """It states no outcome, so it must not be able to carry a verdict."""
    assert "preflight_checked" in events.KINDS
    assert "preflight_checked" not in events.TERMINAL


# ------------------------------------------------------------------------------ the join key

def test_a_recorded_run_can_be_joined_to_its_event_stream(tmp_path):
    """⭐ 8 runs in the stream, 7 rows in the ledger, and no key between them — until now."""
    import unittest.mock as _mock
    p = tmp_path / "runs.jsonl"
    with _mock.patch.object(runs, "path", lambda: p):
        r = runs.record("GP-327", "UNMEASURABLE", job="GP-327",
                        run="20260831T044024-46467dfe")
    assert r["run"] == "20260831T044024-46467dfe"
    assert "run" in runs.ATTRIBUTION, "unattributed() must count joinability"
    with _mock.patch.object(runs, "path", lambda: p):
        assert runs.unattributed()["run"] == 1


def test_a_row_written_without_a_run_id_says_not_recorded(tmp_path):
    """`finish()` closes lanes, which have no event stream. That is NOT-RECORDED, not a blank."""
    import unittest.mock as _mock
    p = tmp_path / "runs.jsonl"
    with _mock.patch.object(runs, "path", lambda: p):
        r = runs.record("some-lane", "FINISHED")
    assert r["run"] == runs.NOT_RECORDED


# --------------------------------------------------------------------------------- the metrics

def test_first_pass_green_is_zero_from_an_instrument_that_has_never_seen_green(stream):
    """⛔ The flag is the finding. 0/7 is only a measurement once we say the instrument is blind."""
    r = reliability.first_pass_green()
    assert r.numerator == 0 and r.denominator == 7
    assert r.basis == reliability.MEASURED
    assert r.instrument_live is False, (
        "no run has ever produced a PASS, so this zero has not been shown to be a measurement")
    assert "NEVER seen to register a non-zero" in str(r)


def test_first_pass_green_registers_a_green_when_one_exists(tmp_path, monkeypatch):
    """The negative control for the control: prove the instrument can see a non-zero."""
    p = tmp_path / "events.jsonl"
    monkeypatch.setattr(events, "path", lambda: p)
    log = events.RunLog.start(ticket="T-9", chosen="ui-control", rule="r",
                              eligible=[{"id": "ui-control", "chosen": True}])
    log.finish(Verdict.PASS)
    r = reliability.first_pass_green()
    assert r.numerator == 1 and r.denominator == 1 and r.instrument_live is True


def test_a_rate_over_an_empty_population_is_not_zero(tmp_path, monkeypatch):
    monkeypatch.setattr(events, "path", lambda: tmp_path / "nothing.jsonl")
    r = reliability.first_pass_green()
    assert r.value is None and r.basis == reliability.NOT_RECORDED
    assert "NOT-MEASURABLE" in str(r)


def test_dependency_violations_replays_order_not_final_state(tmp_path):
    """A task unblocked before it was claimed is not a violation; blocked-then-claimed is."""
    p = tmp_path / "tasks.jsonl"
    rows = [
        {"ts": 1, "actor": "a", "kind": "create", "task": "t1", "data": {"title": "clean"}},
        {"ts": 2, "actor": "a", "kind": "block", "task": "t1", "data": {"by": "x"}},
        {"ts": 3, "actor": "a", "kind": "unblock", "task": "t1", "data": {"by": "x"}},
        {"ts": 4, "actor": "a", "kind": "claim", "task": "t1", "data": {}},
        {"ts": 5, "actor": "a", "kind": "create", "task": "t2", "data": {"title": "dirty"}},
        {"ts": 6, "actor": "a", "kind": "block", "task": "t2", "data": {"by": "y"}},
        {"ts": 7, "actor": "a", "kind": "claim", "task": "t2", "data": {}},
    ]
    p.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
    r = reliability.dependency_violations(p)
    assert r.numerator == 1 and r.denominator == 2
    assert "t2" in r.detail and "t1" not in r.detail


def test_the_warning_counter_is_anchored_to_an_outcome(stream):
    """⚠ `known_failure_warnings` must be unregisterable without an outcome to anchor it."""
    from factory.metrics import GoodhartViolation, MetricSet
    ms = MetricSet("probe")
    with pytest.raises(GoodhartViolation):
        ms.activity("known_failure_warnings", paired_with="first_pass_green_rate")
    assert reliability.metric_set().get("known_failure_warnings").paired_with == \
        "first_pass_green_rate"


# ------------------------------------------------------------------------------ the invocation

def test_an_invocation_joins_to_what_the_run_went_on_to_do(tmp_path, monkeypatch):
    """⭐ The row that answers *did showing a run its previous failure change the outcome*.

    Without this join we would be measuring that warnings were generated — an activity metric with
    no outcome anchor, which is the exact thing this patch is most at risk of producing.
    """
    p = tmp_path / "events.jsonl"
    monkeypatch.setattr(events, "path", lambda: p)
    log = events.RunLog.start(ticket="T-7", chosen="ui-control", rule="r",
                              eligible=[{"id": "ui-control", "chosen": True}])
    log.preflight(ticket="T-7", attempt_number=2, prior_attempt_count=1,
                  prior_terminal_verdict="UNMEASURABLE",
                  prior_failure_family=preflight.DECLARATION_WITHOUT_MECHANISM,
                  same_family_as_prior=None, prevention_check_available=True,
                  prevention_check_result="STILL_PRESENT", context_packet_words=61,
                  warning_emitted=True, would_refuse=True, policy="WARN_ONLY_V0")
    log.emit("agent_dispatched", agent="a")
    log.finish(Verdict.UNMEASURABLE, failure_family=preflight.DECLARATION_WITHOUT_MECHANISM,
               classified_by="verifier_declared_not_wired")

    rows = preflight.invocations()
    assert len(rows) == 1
    row = rows[0]
    for f in ("attempt_number", "prior_attempt_count", "prior_terminal_verdict",
              "prior_failure_family", "same_family_as_prior", "prevention_check_available",
              "prevention_check_result", "context_packet_words", "warning_emitted",
              "would_refuse", "run_started", "eventual_verdict", "eventual_failure_family"):
        assert f in row, f"the approval requires {f} on every preflight invocation"
    assert row["run_started"] is True
    assert row["eventual_verdict"] == "UNMEASURABLE"
    assert row["eventual_failure_family"] == preflight.DECLARATION_WITHOUT_MECHANISM


def test_no_preflight_recorded_reads_as_not_recorded(tmp_path, monkeypatch):
    monkeypatch.setattr(events, "path", lambda: tmp_path / "none.jsonl")
    assert preflight.invocations() == []
    assert "NOT-RECORDED, not zero" in preflight.render_invocations()


# ------------------------------------------------------------------------- ⭐ THE COUNTERFACTUAL

#: `.data/attempts.json.pre-F85.bak`, verbatim — what the pre-patch instrument actually held while
#: GP-327 was failing the same way for the sixth time.
PRE_PATCH_LEDGER = {
    "ui-control-agent:gp-327": {
        "count": 2,
        "attempts": [
            {"n": 1, "at": "2026-08-30T13:34:48Z", "note": "", "outcome": "ok",
             "detail": "dry run", "limit": "none"},
            {"n": 2, "at": "2026-08-30T13:35:49Z", "note": "", "outcome": "ok",
             "detail": "dry run", "limit": "none"},
        ],
    }
}


def test_without_the_new_evidence_the_recurrence_conclusion_cannot_be_reached(stream, tmp_path):
    """⭐ The counterfactual, on real recorded data. The claim of this patch, stated as a test.

    BEFORE — `deploy.AttemptLedger` was the estate's prior-failure mechanism. It was live and
    correctly implemented, and it is handed here the exact contents it actually held during
    GP-327. It reports **no failures and an empty context**, because it reads the PROVIDER's
    outcome (`ok`, exit 0 on a dry run) and `failures()` filters on `outcome != "ok"`.

    AFTER — the preflight reads the same history from the event stream, where a `GreenContract`
    recorded a non-PASS verdict for every one of those attempts, and reaches the conclusion.

    ⛔ If this test ever passes trivially — if the BEFORE half starts finding failures — the
    counterfactual has evaporated and the patch's justification must be re-argued, not assumed.
    """
    from factory.deploy import AttemptLedger

    # ---- BEFORE: the mechanism that existed, with the data it actually had
    p = tmp_path / "attempts.json"
    p.write_text(json.dumps(PRE_PATCH_LEDGER), encoding="utf-8")
    ledger = AttemptLedger(p, max_attempts=2)
    assert ledger.attempts("ui-control-agent:gp-327") == 2, "it counted the attempts correctly"
    assert ledger.failures("ui-control-agent:gp-327") == [], (
        "the pre-patch instrument saw no failure — this is the defect, not a broken fixture")
    assert ledger.context("ui-control-agent:gp-327") == "", (
        "so it had nothing to tell attempt 3, and told it nothing")

    # ---- AFTER: the same history, read where the verdict lives
    m = preflight.check("GP-327", {}, before="20260831T044024-46467dfe")
    assert len(m.prior) == 6, "six prior non-PASS runs are visible in the stream"
    assert m.last.family == preflight.DECLARATION_WITHOUT_MECHANISM
    assert m.same_family_as_prior is True
    assert m.packet, "and there is something concrete to hand the next attempt"
    assert "declares a WIRED verifier" in m.packet


def test_the_two_instruments_answer_different_questions_by_construction(tmp_path):
    """Why the preflight is a complement, not a replacement — asserted, not asserted in prose.

    The ledger's key is `agent:worktree` and its verdict is the provider's exit. The preflight's
    key is the ticket and its verdict is the contract's. Neither can be derived from the other, so
    removing either loses a real signal.
    """
    from factory.deploy import AttemptLedger
    p = tmp_path / "a.json"
    p.write_text(json.dumps(PRE_PATCH_LEDGER), encoding="utf-8")
    led = AttemptLedger(p, max_attempts=2)
    # The ledger cannot be keyed by ticket: its key embeds the agent and the worktree name.
    assert led.attempts("GP-327") == 0, "the ledger has no notion of a ticket"
    assert led.attempts("ui-control-agent:gp-327") == 2
    # And it holds no verdict at all — only the provider's outcome string.
    rows = json.loads(p.read_text(encoding="utf-8"))["ui-control-agent:gp-327"]["attempts"]
    assert all("verdict" not in r for r in rows)
    assert all(r["outcome"] == "ok" for r in rows)


# ------------------------------------------------------------------------------ the budget

def test_the_preflight_reads_the_stream_a_bounded_number_of_times(tmp_path, monkeypatch):
    """⚠ Regression, MEASURED. The first version was quadratic and blew a published budget.

    `runs()` + `fold()` per id re-read the whole file once per run: **84 ms at 8 runs, 3,726 ms at
    500, 12,666 ms at 1000**, against the 200 ms preflight budget in `docs/protocol/ROLLOUT.md`.
    After `events.fold_all()`: **49 ms at 1000 runs, 188 ms at 5000.**

    ⛔ Asserted by counting file reads, not by wall clock. A timing assertion in CI is flaky and
    would be disabled the first time a machine was busy — and a disabled budget test is worse than
    none, because the budget still looks enforced.
    """
    p = tmp_path / "events.jsonl"
    rows = []
    for i in range(60):
        rid = f"20260831T{i:06d}-{i:08x}"
        b = {"run": rid, "ticket": "GP-327", "at": "2026-08-31T00:00:00+00:00"}
        rows += [{**b, "seq": 1, "kind": "run_started", "chosen": "ui-control", "rule": "r",
                  "eligible": [{"id": "ui-control", "chosen": True}]},
                 {**b, "seq": 2, "kind": "run_finished", "verdict": "UNMEASURABLE",
                  "failure_family": preflight.UNCLASSIFIED, "classified_by": "t"}]
    p.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
    monkeypatch.setattr(events, "path", lambda: p)

    real_read, calls = events.read, []
    monkeypatch.setattr(events, "read", lambda run=None: (calls.append(run), real_read(run))[1])

    m = preflight.check("GP-327", {})
    assert len(m.prior) == 60
    assert len(calls) <= 2, (
        f"prior_attempts read the stream {len(calls)} times for 60 runs — it is scaling with the "
        "number of runs again, which is the quadratic defect this test exists to catch")


# ------------------------------------------------------- a broken check is not a missing one

def test_a_prevention_check_that_raises_is_not_reported_as_absent(stream, monkeypatch):
    """⚠ COLLAPSED_STATE, caught inside the module that names the family.

    A check that crashed and a family with no check both used to report NOT-RECORDED. They need
    different remedies — fix the check, versus write one — and only the first means the taxonomy's
    coverage number is a lie.
    """
    def _boom(_ctx):
        raise RuntimeError("the registry was unreadable")

    monkeypatch.setitem(preflight.PREVENTION, preflight.DECLARATION_WITHOUT_MECHANISM, _boom)
    m = preflight.check("GP-327", {"preset": object()}, before="20260831T044024-46467dfe")
    assert m.prevention.result == "CHECK_ERROR"
    assert m.prevention.result != preflight.NOT_RECORDED
    assert "RuntimeError" in m.prevention.error
    assert m.would_refuse is False, "a check that could not run has confirmed nothing"
    assert m.as_event()["prevention_error"].startswith("RuntimeError")


def test_a_family_with_no_check_is_not_reported_as_an_error(stream):
    """The other half of the pair — absence must stay absence."""
    m = preflight.check("GP-327", {}, before="20260831T034638-1a0176a8")
    assert m.last.family == preflight.UNBOUNDED_RETRY
    assert m.prevention.result == preflight.NOT_RECORDED
    assert m.prevention.error == ""


def test_an_unavailable_preflight_is_distinguishable_from_a_quiet_one():
    """⛔ The day the preflight breaks must not be the day it looks healthiest."""
    broken = preflight.unavailable("GP-327", RuntimeError("stream unreadable"))
    assert broken.packet == "" and broken.matched is False
    assert broken.as_event()["prevention_check_result"] == "CHECK_ERROR"
    assert "RuntimeError" in broken.as_event()["prevention_error"]
