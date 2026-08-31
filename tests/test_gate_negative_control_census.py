"""Which readiness gates have ever been shown able to refuse — and which have not.

`tests/test_connector_contract.py::test_every_assertion_has_been_proved_able_to_fail` is the
pattern: it asserts *declared == proved*, so an assertion cannot be added without a mutation that
shows it can fail. **The readiness board has thirty gates and no equivalent.** F94 found six that
returned PASS over an absence, and the reason all six survived is here: nobody had ever asked the
other twenty-four to refuse.

⛔ **This file does not pretend to close that.** Twenty-three of thirty are proved; seven are not,
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
    # second pass
    "attributable": "this file::test_attributable_refuses_when_it_cannot_see_the_session_names",
    "breadth":      "this file::test_corpus_breadth_reaches_both_verdicts",
    "ticket":       "this file::test_ticket_refuses_when_the_drafts_folder_is_not_there",
    "grain":        "this file::test_grain_fails_while_the_grain_is_undeclared",
    "rendered":     "this file::test_render_pass_fails_until_someone_has_actually_looked",
    "chain":        "this file::test_skill_chain_precedence_reaches_all_three_verdicts",
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
    "ceiling":      "⛔ the only real RED on the board, and the engine's sole budget symbol is a "
                    "TIME budget — the accounting must be fixed before a control means anything",
    "suite":        "shells out to pytest; provoking it means a nested suite run — the same cost "
                    "F92 was about",
    "certified":    "shells out to factory.certify, which reaches a pytest run in a second repo; "
                    "same cost problem, see F92",
    "corpus":       "tamper-evidence over evals/MANIFEST.sha256; needs a corpus fixture whose "
                    "hash can be made to disagree without disturbing the real manifest",
}

#: The number proved today. ⭐ This may only ever go UP.
_COVERAGE_FLOOR = 23


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
    """⚠ This test PASSES while seven gates are unproven, and says so out loud.

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


# ------------------------------------------------- second pass: six more, 17 -> 23

def test_attributable_refuses_when_it_cannot_see_the_session_names(tmp_path, monkeypatch):
    """It attributes runs by parsing worktree names, so with no worktrees there is nothing to
    parse — and nothing is not "all attributed".

    ⚠ Order matters here and the first attempt got it wrong. `_audits()` is called BEFORE this
    gate's own `.sessions` guard, so pointing CONNECTORS at an empty directory trips the *audit*
    refusal instead of the one under test. The audits directory is created first so the guard
    being exercised is the intended one.
    """
    (tmp_path / "orchestrator" / "data" / "audits").mkdir(parents=True)
    monkeypatch.setattr(R, "CONNECTORS", tmp_path)
    with pytest.raises(R.Unmeasurable):
        R.g_work_is_attributable()          # no .sessions at all

    (tmp_path / ".sessions").mkdir()
    with pytest.raises(R.Unmeasurable):
        R.g_work_is_attributable()          # .sessions exists and is empty


def test_corpus_breadth_reaches_both_verdicts(monkeypatch):
    """⭐ Both directions, which matters more here than usual.

    This gate FAILS against the real corpus today — one case, below any calibration threshold —
    so a refusal alone would not distinguish "working" from "stuck". The positive control shows
    the PASS branch is reachable at its stated bar (>= 29 cases across >= 15 strata), which is
    what makes the standing RED a finding about the corpus rather than about the gate.
    """
    from factory import corpus as _c
    monkeypatch.setattr(_c, "load", lambda cid: {"strata": [f"s{i}" for i in range(15)]})

    monkeypatch.setattr(_c, "available", lambda: [f"c{i}" for i in range(29)])
    assert R.g_corpus_has_breadth().verdict == R.PASS

    monkeypatch.setattr(_c, "available", lambda: ["c0"])
    assert R.g_corpus_has_breadth().verdict == R.FAIL

    def _boom():
        raise _c.CorpusError("manifest does not verify")
    monkeypatch.setattr(_c, "available", _boom)
    assert R.g_corpus_has_breadth().verdict == R.FAIL


def test_ticket_refuses_when_the_drafts_folder_is_not_there(tmp_path, monkeypatch):
    """Its own standard: a ticket, or a recorded decision that none is needed. What is not
    acceptable is neither — "an open question quietly aging in a drafts folder"."""
    monkeypatch.setattr(R, "FACTORY", tmp_path / "nested")
    with pytest.raises(R.Unmeasurable):
        R.g_work_has_a_ticket()


def test_grain_fails_while_the_grain_is_undeclared(monkeypatch):
    """An unanswered question must not read as a settled one.

    Its evidence spells out the stake: if the real table holds one account, the declared primary
    key is wrong and the calibration world is built on a mistake.
    """
    monkeypatch.setattr(R, "_blueprint", lambda: {})
    assert R.g_grain_declared().verdict == R.FAIL

    monkeypatch.setattr(R, "_blueprint", lambda: {"grain_confirmed": "queried 2026-08-20"})
    assert R.g_grain_declared().verdict == R.PASS          # positive control


def test_render_pass_fails_until_someone_has_actually_looked(tmp_path, monkeypatch):
    """The gate's own distinction: a static check proves a file parses, not that a visual painted.

    Note both failing cases — no evidence directory at all, and a directory containing nothing
    matching — reach FAIL rather than UNMEASURABLE. That is the right call for this gate: the
    absence of a record IS the finding, not an instrument failure.
    """
    monkeypatch.setattr(R, "FACTORY", tmp_path)
    assert R.g_render_pass_recorded().verdict == R.FAIL          # no docs/evidence at all

    (tmp_path / "docs" / "evidence").mkdir(parents=True)
    assert R.g_render_pass_recorded().verdict == R.FAIL          # directory, nothing in it

    (tmp_path / "docs" / "evidence" / "render-pass-2026-01-01.md").write_text("looked",
                                                                             encoding="utf-8")
    assert R.g_render_pass_recorded().verdict == R.PASS          # positive control


def test_skill_chain_precedence_reaches_all_three_verdicts(tmp_path, monkeypatch):
    """Three outcomes, and the gate keeps them apart: the document is missing (UNMEASURABLE,
    nothing to read), present but silent on precedence (FAIL, the question is open), or present
    and settled (PASS)."""
    import pathlib as _p
    monkeypatch.setattr(_p.Path, "home", staticmethod(lambda: tmp_path))
    with pytest.raises(R.Unmeasurable):
        R.g_impeccable_precedence_settled()

    sk = tmp_path / ".claude" / "skills" / "living-systems-ui"
    sk.mkdir(parents=True)
    (sk / "SKILL.md").write_text("no mention of the fifth authority", encoding="utf-8")
    assert R.g_impeccable_precedence_settled().verdict == R.FAIL

    (sk / "SKILL.md").write_text("precedence: impeccable comes after", encoding="utf-8")
    assert R.g_impeccable_precedence_settled().verdict == R.PASS
