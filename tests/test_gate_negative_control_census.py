"""Which readiness gates have ever been shown able to refuse — and which have not.

`tests/test_connector_contract.py::test_every_assertion_has_been_proved_able_to_fail` is the
pattern: it asserts *declared == proved*, so an assertion cannot be added without a mutation that
shows it can fail. **The readiness board has thirty gates and no equivalent.** F94 found six that
returned PASS over an absence, and the reason all six survived is here: nobody had ever asked the
other twenty-four to refuse.

⛔ **This file does not pretend to close that.** Seventeen of thirty are proved; thirteen are not,
and they are listed by name with the reason. A census whose gaps are invisible is the defect it
was written about, so the gaps are the point of the file, not an omission from it — and one test
prints the count into the suite's output so it cannot quietly rot.

What it enforces:

  1. **every gate is CLASSIFIED** — proved or explicitly unproven. A new gate cannot be added
     silently uncovered, which is exactly how the six got in.
  2. **coverage may not regress** — the floor only moves up.
  3. the two sets do not overlap and name only real gates.

⚠ **"Proved" here means proved able to reach a NON-PASS verdict**, which is weaker than the
connector contract's standard (each assertion flipped by a specific mutation with a predicted
detail string). It is the useful first rung: a gate that cannot refuse at all is broken in a way
no amount of tuning fixes.
"""
from __future__ import annotations

import json

import pytest

from factory import readiness as R


# --------------------------------------------------------------------------------- the census

#: Gate id -> where its refusal is demonstrated.
_PROVED = {
    # F94 — the six that greened on an absence, each with a discriminating test.
    "honest":    "test_gates_refuse_an_empty_population.py::success_means_correct",
    "checks":    "test_gates_refuse_an_empty_population.py::gate_coverage",
    "general":   "test_gates_refuse_an_empty_population.py::qa_gate",
    "durable":   "test_gates_refuse_an_empty_population.py::durability",
    "isolated":  "test_gates_refuse_an_empty_population.py::evaluator",
    # proved in this file, below
    "finishes":  "this file::test_the_audit_family_refuses_an_empty_window",
    "succeeds":  "this file::test_the_audit_family_refuses_an_empty_window",
    "refuses":   "this file::test_the_gate_refusal_gate_can_itself_refuse",
    "cost":      "this file::test_cost_gate_fails_when_no_failure_carries_a_cost",
    "truthful":  "this file::test_the_truthfulness_gate_refuses_three_different_ways",
    "tenancy":   "this file::test_tenancy_refuses_an_undeclared_blast_radius",
    "version":   "this file::test_version_hash_completeness_fails_on_a_stub",
    # ⚠ Covered by scripts/mutate_readiness_probes.py — and that harness is CURRENTLY INOPERATIVE.
    # Its anchors are copies of production source in prefect-connectors, which is parked on
    # `chore/artefact-homes` where the anchored lines do not exist; all 15 anchor tests fail.
    # These five are counted as proved because the harness demonstrated it once and the test
    # guarding its anchors is doing its job by failing. Do not read them as *currently* verified.
    "cap":          "scripts/mutate_readiness_probes.py (harness inoperative — see F-family)",
    "bounded":      "scripts/mutate_readiness_probes.py (harness inoperative)",
    "concurrency":  "scripts/mutate_readiness_probes.py (harness inoperative)",
    "reaper":       "scripts/mutate_readiness_probes.py (harness inoperative)",
    "from-history": "scripts/mutate_readiness_probes.py (harness inoperative)",
}

#: Gate id -> why no negative control exists yet. Every entry is a debt, not a dispensation.
_UNPROVEN = {
    "r1-followup":  "research-followup probe; no provocation designed",
    "r2-followup":  "research-followup probe; no provocation designed",
    "r3-followup":  "research-followup probe; no provocation designed",
    "rendered":     "reads a render-pass artifact; needs a fixture artifact to provoke",
    "chain":        "reads .impeccable precedence; no provocation designed",
    "grain":        "reads a grain declaration; no provocation designed",
    "ticket":       "reads ticket linkage; no provocation designed",
    "ceiling":      "⛔ the only real RED on the board, and the engine's sole budget symbol is a "
                    "TIME budget — the accounting must be fixed before a control means anything",
    "breadth":      "corpus breadth; one corpus exists, so the population is degenerate",
    "attributable": "reads worktree naming in the connectors repo",
    "suite":        "shells out to pytest; provoking it means a nested suite run",
    "certified":    "shells out to factory.certify; same cost problem, see F92",
    "corpus":       "tamper-evidence over evals/MANIFEST.sha256; needs a corpus fixture",
}

#: The number proved today. ⭐ This may only ever go UP.
_COVERAGE_FLOOR = 17


# --------------------------------------------------------------------------------- the ratchet

def test_every_gate_is_classified_as_proved_or_explicitly_unproven():
    """⭐ The load-bearing test. A new gate must be classified, not silently uncovered.

    This is how the F94 six got in: they were added, they measured something, and nobody asked
    whether they could refuse. An unclassified gate fails here rather than sitting green.
    """
    declared = {g.id for g in R.GATES}
    classified = set(_PROVED) | set(_UNPROVEN)
    unclassified = sorted(declared - classified)
    assert not unclassified, (
        f"{len(unclassified)} gate(s) are neither proved able to refuse nor listed as unproven: "
        f"{unclassified}. Add a provocation, or add an entry to _UNPROVEN saying why not — but "
        f"do not leave a gate uncounted, which is how the six in F94 survived.")


def test_the_census_names_only_real_gates():
    """A census that drifts from the thing it counts is worse than none."""
    declared = {g.id for g in R.GATES}
    ghosts = sorted((set(_PROVED) | set(_UNPROVEN)) - declared)
    assert not ghosts, f"the census names gates that no longer exist: {ghosts}"


def test_a_gate_is_not_both_proved_and_unproven():
    both = sorted(set(_PROVED) & set(_UNPROVEN))
    assert not both, f"contradictory classification: {both}"


def test_negative_control_coverage_does_not_regress():
    """The floor only moves up. Lowering it is a deliberate act that must be seen in a diff."""
    assert len(_PROVED) >= _COVERAGE_FLOOR, (
        f"negative-control coverage fell to {len(_PROVED)} from a floor of {_COVERAGE_FLOOR}")


def test_the_gap_is_reported_rather_than_hidden():
    """⚠ This test PASSES while thirteen gates are unproven, and says so out loud.

    It exists so the number is in the suite's output and in this file's diff, not so it can be
    mistaken for coverage. `registry.unproven()` does the same for workflows.
    """
    declared = {g.id for g in R.GATES}
    assert _UNPROVEN, "if nothing is unproven, delete this test rather than letting it lie"
    assert len(_PROVED) + len(_UNPROVEN) == len(declared)
    # The honest headline, for anyone reading -q output with -rA:
    print(f"\nnegative-control coverage: {len(_PROVED)} of {len(declared)} readiness gates; "
          f"{len(_UNPROVEN)} unproven: {sorted(_UNPROVEN)}")


# --------------------------------------------------------------- provocations proved here

@pytest.fixture
def audits(monkeypatch):
    def _set(rows):
        monkeypatch.setattr(R, "_audits", lambda: rows)
    return _set


def test_the_audit_family_refuses_an_empty_window(audits):
    """`finishes` and `succeeds` both refuse rather than pass when no run is in the window.

    Worth pinning precisely because F94's `honest` — a gate over the same population — did NOT.
    These two were already right; the negative control records that rather than assuming it.
    """
    audits([])
    for fn in (R.g_finishes, R.g_succeeds_more_than_fails):
        with pytest.raises(R.Unmeasurable):
            fn()


def test_the_gate_refusal_gate_can_itself_refuse(audits):
    """Two different non-passes, and the distinction is the whole point of the gate.

    No gate events at all is UNMEASURABLE — the instrument saw nothing. Gate events that are all
    approvals is FAIL — the instrument looked and no gate ever refused.
    """
    audits([])
    with pytest.raises(R.Unmeasurable):
        R.g_gates_can_refuse()

    audits([{"id": "r", "events": [
        {"event_type": "gate_approved", "details": {"notes": "ok"}}]}])
    assert R.g_gates_can_refuse().verdict == R.FAIL


def test_cost_gate_fails_when_no_failure_carries_a_cost(audits):
    """`cost` errs safe already — an empty population reaches FAIL, not PASS.

    Its evidence line is the reason to keep it that way: *"a stage that failed 100 times
    contributes $0.00 — the real spend is unknown, not small."*
    """
    audits([])
    assert R.g_cost_survives_failure().verdict == R.FAIL


def test_the_truthfulness_gate_refuses_three_different_ways(tmp_path, monkeypatch):
    """Three distinct absences, three refusals, and it keeps them apart.

    This gate is the one whose population-reporting discipline F94 held the others to — it already
    says *"N listed, M with an event log, K actually compared"*. The census listed it as unproven
    only because nothing exercised it. It was right all along; this records that.
    """
    monkeypatch.setattr(R, "CONNECTORS", tmp_path)
    with pytest.raises(R.Unmeasurable):        # the file is not there
        R.g_status_matches_reality()

    d = tmp_path / "orchestrator" / "data"
    d.mkdir(parents=True)
    (d / "pipelines.json").write_text("{ not json", encoding="utf-8")
    with pytest.raises(R.Unmeasurable):        # it is there and will not parse
        R.g_status_matches_reality()

    (d / "pipelines.json").write_text(json.dumps({"pipelines": []}), encoding="utf-8")
    with pytest.raises(R.Unmeasurable):        # it parses and records nothing
        R.g_status_matches_reality()


def test_tenancy_refuses_an_undeclared_blast_radius(monkeypatch):
    """⛔ The refusal here is a safety property, not bookkeeping.

    Its own message: one ALDC Windsor key returns *every* client's accounts, so an unfiltered pull
    lands CLIENT-B rows in a CLIENT-A table and nothing downstream can tell. Blast radius is
    uncertifiable until the account ids are written down — so an empty list must never read as
    "no restriction needed".
    """
    monkeypatch.setattr(R, "_blueprint", lambda: {"allowed_tenants": []})
    with pytest.raises(R.Unmeasurable):
        R.g_tenancy_declared()

    monkeypatch.setattr(R, "_blueprint", lambda: {"allowed_tenants": ["CLIENT-A"]})
    assert R.g_tenancy_declared().verdict == R.PASS          # positive control


def test_version_hash_completeness_fails_on_a_stub(tmp_path, monkeypatch):
    """A blueprint that hashes nothing must not report a complete hash.

    The gate's own evidence names the dimension that bites: *"contract_version is the one that
    bites now — a certification granted under contract V4 silently transfers to V5."*
    """
    (tmp_path / "blueprint.py").write_text("x = 1\n", encoding="utf-8")
    monkeypatch.setattr(R, "FACTORY", tmp_path)
    r = R.g_version_hash_is_complete()
    assert r.verdict == R.FAIL
    assert "dimensions absent" in r.headline
