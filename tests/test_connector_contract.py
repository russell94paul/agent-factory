"""Calibration for the windsorai GreenContract.

The point of this file is not that the contract passes. It is that each assertion has been shown
to FAIL when the thing it claims to measure is broken. A green suite from a contract nobody
proved could fail is the 965-run loop again.
"""
from __future__ import annotations

from dataclasses import replace

import copy

import pytest

from factory.calibration import SESSION, calibration_target, known_good_world
from factory.connector_contract import CtxProbes, Probes, build_contract
from factory.contract import Verdict
from factory.targets import load_target
from factory.calibration import BLUEPRINT


def contract():
    return build_contract(calibration_target(), CtxProbes())


def verdict_of(world, name):
    res = contract().run(world)
    return next(r for r in res.results if r.name.startswith(name))


# ---------------------------------------------------------------- 1. known-good


def test_known_good_world_is_green():
    """Calibration run 1: the contract must not cry wolf on a run we know landed."""
    res = contract().run(known_good_world())
    assert res.verdict is Verdict.PASS, res.summary() + " | " + str(res.failures())
    assert len(res.results) == 12


# ---------------------------------------------------------------- 2. every assertion can fail


def _broken(**changes):
    w = copy.deepcopy(known_good_world())
    for path, value in changes.items():
        top, _, key = path.partition("__")
        if key:
            w[top][key] = value
        else:
            w[top] = value
    return w


def _drop_an_account():
    w = copy.deepcopy(known_good_world())
    w["landed"]["rows"] = [r for r in w["landed"]["rows"] if r["account_id"] != "9876543210"]
    w["run"]["emitted_rows"] = len(w["landed"]["rows"])
    return w


def _foreign_tenant():
    w = copy.deepcopy(known_good_world())
    w["landed"]["rows"][0]["account_id"] = "5555555555"
    return w


def _stale_session():
    w = copy.deepcopy(known_good_world())
    for row in w["landed"]["rows"]:
        row["___ALDC___GLOBAL_SESSION_ID___"] = "an-earlier-session"
    return w


def _source_disagrees():
    w = copy.deepcopy(known_good_world())
    w["source"]["per_key_counts"]["1234567890"] = 30
    return w


# One registered mutation per assertion. An assertion with no entry here has never been shown to
# fail, and the coverage test below refuses to let that ship.
MUTATIONS = {
    "A1":  (_broken(config__accounts=[]),                     "no accounts resolved"),
    "A2":  (_broken(credential__status=401),                  "HTTP 401"),
    "A3":  (_broken(image__built_at=1787305000),              "predates the merge"),
    "A4":  (_broken(deployment__image_digest="sha256:other"), "deployment pins"),
    "A5":  (_broken(suite__failed=3),                         "3 failing test"),
    "A6":  (_broken(run__state="CRASHED"),                    "ended CRASHED"),
    "A7":  (_stale_session(),                                 "other session"),
    "A8":  (_broken(run__emitted_rows=40),                    "delta 20"),
    "A9":  (_drop_an_account(),                               "absent from landing"),
    "A10": (_source_disagrees(),                              "source 30, landed 18"),
    "A11": (_broken(forbidden__secret_hits=1),                "secret value"),
    "A12": (_foreign_tenant(),                                "outside scope: 5555555555"),
}

EXTRA_CASES = [
    ("A3", _broken(image__imports=False), "does not import"),
    ("A3", _broken(image__commit="deadbee"), "built from deadbee"),
]


@pytest.mark.parametrize("aid,world,fragment",
                         [(k, w, f) for k, (w, f) in MUTATIONS.items()] + EXTRA_CASES)
def test_assertion_fails_when_its_subject_breaks(aid, world, fragment):
    r = verdict_of(world, aid)
    assert r.verdict is Verdict.FAIL, f"{aid} did not fail: {r}"
    assert fragment in r.detail, r.detail


def test_every_assertion_has_been_proved_able_to_fail():
    """⭐ The negative control over the whole contract.

    A contract is only worth its verdict if each of its claims has been observed failing. Add an
    assertion without registering a mutation and this test names it — which is the moment to
    write the mutation, not to relax the check.
    """
    declared = {a.name.split("-")[0] for a in contract().assertions}
    proved = set(MUTATIONS)
    assert declared == proved, f"never shown able to fail: {sorted(declared - proved)}"


def test_silent_empty_is_caught_by_a7_while_a6_still_passes():
    """⭐ The important calibration case.

    The connector runtime swallows non-200 responses and returns an empty dataframe, so the flow
    run reaches COMPLETED with nothing landed. A run-state check calls that success. A7 is what
    makes the difference between "the run finished" and "the work happened".
    """
    world = _broken(landed={"rows": []}, run__emitted_rows=0)
    assert verdict_of(world, "A6").verdict is Verdict.PASS
    a7 = verdict_of(world, "A7")
    assert a7.verdict is Verdict.FAIL
    assert "0 rows under this run's session" in a7.detail


def test_rows_from_a_previous_run_do_not_satisfy_a7():
    """A query against a table a prior run populated returns a healthy number and proves nothing."""
    world = copy.deepcopy(known_good_world())
    for row in world["landed"]["rows"]:
        row["___ALDC___GLOBAL_SESSION_ID___"] = "an-earlier-session"
    a7 = verdict_of(world, "A7")
    assert a7.verdict is Verdict.FAIL
    assert "other session" in a7.detail


def test_a8_catches_the_gap_between_emitted_and_landed():
    world = _broken(run__emitted_rows=40)
    r = verdict_of(world, "A8")
    assert r.verdict is Verdict.FAIL and "delta 20" in r.detail


def test_a9_catches_a_partial_extraction_a6_cannot_see():
    """Calibration run 3: drop one requested account. The run still COMPLETED."""
    world = copy.deepcopy(known_good_world())
    world["landed"]["rows"] = [r for r in world["landed"]["rows"]
                               if r["account_id"] != "9876543210"]
    world["run"]["emitted_rows"] = len(world["landed"]["rows"])
    assert verdict_of(world, "A6").verdict is Verdict.PASS
    r = verdict_of(world, "A9")
    assert r.verdict is Verdict.FAIL and "absent from landing" in r.detail


def test_a9_catches_a_duplicated_primary_key():
    world = copy.deepcopy(known_good_world())
    world["landed"]["rows"].append(copy.deepcopy(world["landed"]["rows"][0]))
    world["run"]["emitted_rows"] = len(world["landed"]["rows"])
    r = verdict_of(world, "A9")
    assert r.verdict is Verdict.FAIL and "not unique" in r.detail


def test_a9_catches_the_wrong_date_and_null_spend():
    world = copy.deepcopy(known_good_world())
    world["landed"]["rows"][0]["date"] = "2026-07-21"
    world["landed"]["rows"][1]["spend"] = None
    r = verdict_of(world, "A9")
    assert r.verdict is Verdict.FAIL
    assert "not on the requested date" in r.detail and "null/negative spend" in r.detail


def test_a10_catches_loaded_consistently_wrong():
    """Internally consistent, and disagreeing with the source. A9 alone cannot see this."""
    world = copy.deepcopy(known_good_world())
    world["source"]["per_key_counts"]["1234567890"] = 30
    assert verdict_of(world, "A9").verdict is Verdict.PASS
    r = verdict_of(world, "A10")
    assert r.verdict is Verdict.FAIL and "source 30, landed 18" in r.detail


def test_a11_catches_a_leaked_secret():
    r = verdict_of(_broken(forbidden__secret_hits=1), "A11")
    assert r.verdict is Verdict.FAIL and "secret value" in r.detail


def test_a12_catches_another_clients_rows():
    """⭐ The tenancy gate this estate does not have.

    One ALDC vendor key returns every client's accounts. This is that leak, landed.
    """
    world = copy.deepcopy(known_good_world())
    world["landed"]["rows"][0]["account_id"] = "5555555555"      # a CLIENT-B account
    r = verdict_of(world, "A12")
    assert r.verdict is Verdict.FAIL and "outside scope: 5555555555" in r.detail


# ---------------------------------------------------------------- 3. unmeasurable is not a pass


def test_unconfigured_probes_report_unmeasurable_not_pass():
    """An unwired harness must refuse to certify. This is the `verify-qa-success` defect."""
    res = build_contract(calibration_target(), Probes()).run({})
    assert res.verdict is Verdict.UNMEASURABLE
    assert not res.is_green
    assert all(r.verdict is Verdict.UNMEASURABLE for r in res.results)


def test_a_crashing_instrument_is_unmeasurable_not_fail():
    world = _broken(landed=RuntimeError("snowflake connector timed out"))
    r = verdict_of(world, "A7")
    assert r.verdict is Verdict.UNMEASURABLE and "timed out" in r.detail


def test_an_unscoped_target_cannot_certify_tenancy():
    """A target declaring no account ids must block rather than wave through.

    This asserted the SHIPPED blueprint was unscoped until 2026-08-21, when the six CLIENT-A
    account ids were sourced from connector/accounts/CLIENT-A/deployments/windsorai.py and filled in.
    The property under test was never "the blueprint is empty" — it was "an empty scope blocks".
    So it now builds an unscoped target explicitly instead of relying on the shipped one staying
    incomplete, which is the kind of coupling that turns a real fix into a red suite.
    """
    unscoped = replace(load_target(BLUEPRINT), allowed_tenants=[])
    res = build_contract(unscoped, CtxProbes()).run(known_good_world())
    a12 = next(r for r in res.results if r.name.startswith("A12"))
    assert a12.verdict is Verdict.UNMEASURABLE
    assert "declares no tenancy scope" in a12.detail
    assert res.verdict is Verdict.UNMEASURABLE, "an unscoped target must not go green"


def test_the_shipped_blueprint_now_declares_a_scope():
    """The counterpart: having sourced the ids, the shipped target must actually carry them.

    Without this, deleting allowed_tenants would silently restore the old UNMEASURABLE and the
    suite above would still be green — a fix that can be undone without a test noticing.
    """
    target = load_target(BLUEPRINT)
    assert len(target.allowed_tenants) == 6, "six CLIENT-A Google Ads accounts, per GP-226"
    assert all("-" in t for t in target.allowed_tenants), (
        "Windsor emits account_id dash-formatted for this source")


def test_a_missing_session_id_is_unmeasurable_not_fail():
    world = _broken(run__session_id=None)
    r = verdict_of(world, "A7")
    assert r.verdict is Verdict.UNMEASURABLE and "cannot be attributed" in r.detail
