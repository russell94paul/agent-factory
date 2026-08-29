"""Calibration for factory/live_probes.py — the first REAL instrument on the connector contract.

Every other test on this contract (test_connector_contract.py) scores a recorded or synthetic
world through CtxProbes. These tests point the live subclass at an actual prefect-connectors
checkout on disk and prove it can both refuse (no checkout, no summary line, a broken run, a
moved hook) and measure (the real windsorai classes construct, the real suite runs) — the two
things a probe that "now exists" must be shown doing before its wiring counts for anything.
"""
from __future__ import annotations

import subprocess

import pytest

from factory.connector_contract import Probes, build_contract
from factory.contract import Verdict, Unmeasurable
from factory.live_probes import (
    WindsorAiGepProbes, _BlindWindsorAiProbes, _default_connectors_root, _repo_root, probes_for,
)
from factory.targets import load_target
from factory.calibration import BLUEPRINT

_ROOT = _default_connectors_root()
_HAS_CHECKOUT = _ROOT.is_dir() and (_ROOT / "connector" / "connectors" / "windsorai.py").is_file()

requires_checkout = pytest.mark.skipif(
    not _HAS_CHECKOUT, reason=f"no prefect-connectors checkout at {_ROOT}")


def _fake(stdout="", stderr="", returncode=0):
    class _FakeResult:
        pass
    r = _FakeResult()
    r.stdout, r.stderr, r.returncode = stdout, stderr, returncode
    return r


def _mock_pytest_call_only(fake_result, real_run):
    """Intercept only the `python -m pytest ...` subprocess call; pass everything else (the
    `git rev-parse` / `git status` calls inside `_revision()`) through to the real
    subprocess.run — else a test about pytest-output parsing silently breaks revision lookup
    for every test in this file that happens to run after it."""
    def _run(cmd, *a, **k):
        if "pytest" in cmd:
            return fake_result
        return real_run(cmd, *a, **k)
    return _run


def _probe(root="."):
    p = WindsorAiGepProbes.__new__(WindsorAiGepProbes)
    p.root, p.test_paths = root, []
    return p


# ---------------------------------------------------------------- path resolution


def test_default_root_is_anchored_to_git_not_a_hardcoded_parent_count(monkeypatch):
    """⭐ The regression review caught: a hardcoded `.parent.parent.parent` is only correct at
    one nesting depth, and was silently wrong once this file is imagined outside a worktree.
    `_repo_root()` must resolve to the MAIN clone's directory regardless of where it's called
    from — verified here by independently re-running the same git primitive it's built on
    (`--git-common-dir`, whose parent is the main clone), not a hardcoded expected path. This
    still catches the regression under review: a hardcoded parent-count doesn't move with
    nesting depth, `--git-common-dir` does."""
    monkeypatch.delenv("PREFECT_CONNECTORS", raising=False)
    from pathlib import Path
    common = subprocess.run(["git", "rev-parse", "--git-common-dir"], cwd=".",
                            capture_output=True, text=True)
    assert common.returncode == 0, "this test requires running inside a git checkout"
    common_path = Path(common.stdout.strip())
    if not common_path.is_absolute():
        common_path = Path(".").resolve() / common_path
    expected = common_path.resolve().parent
    assert _repo_root() == expected
    assert _default_connectors_root() == expected.parent / "prefect-connectors"


def test_env_var_overrides_the_default_root(monkeypatch):
    monkeypatch.setenv("PREFECT_CONNECTORS", "Z:/somewhere/else")
    from pathlib import Path
    assert _default_connectors_root() == Path("Z:/somewhere/else")


# ---------------------------------------------------------------- refuses when it cannot look


def test_missing_checkout_is_unmeasurable_not_a_crash_and_not_a_pass():
    with pytest.raises(Unmeasurable):
        WindsorAiGepProbes(connectors_root="Z:/nowhere/prefect-connectors")


def test_probes_for_falls_back_to_a_blind_probe_that_names_the_reason(monkeypatch):
    """The base refusing Probes() says 'no instrument configured' — indistinguishable from
    'nobody has wired this yet'. A wired instrument that cannot reach its subject must say WHY,
    or a vanished checkout reads identically to A1/A5 never having been built at all."""
    monkeypatch.setenv("PREFECT_CONNECTORS", "Z:/nowhere/prefect-connectors")
    target = load_target(BLUEPRINT)
    p = probes_for(target)
    assert isinstance(p, _BlindWindsorAiProbes)
    assert type(p) is not Probes
    with pytest.raises(Unmeasurable, match="Z:.nowhere.prefect-connectors"):
        p.config({})
    with pytest.raises(Unmeasurable, match="Z:.nowhere.prefect-connectors"):
        p.suite({})


def test_probes_for_only_covers_windsorai_at_gep():
    from dataclasses import replace
    other = replace(load_target(BLUEPRINT), connector="some_other_connector")
    assert type(probes_for(other)) is Probes


def test_suite_reports_unmeasurable_when_pytest_prints_no_summary(monkeypatch):
    """A probe whose subprocess ran but produced nothing parseable must refuse, not guess."""
    monkeypatch.setattr(subprocess, "run",
                        lambda *a, **k: _fake("collected 0 items\n", returncode=5))
    with pytest.raises(Unmeasurable, match="no summary line"):
        _probe().suite({})


def test_suite_reports_unmeasurable_when_the_subprocess_itself_fails(monkeypatch):
    def _boom(*a, **k):
        raise OSError("python not found")
    monkeypatch.setattr(subprocess, "run", _boom)
    with pytest.raises(Unmeasurable, match="could not run"):
        _probe().suite({})


def test_suite_reports_unmeasurable_when_the_run_did_not_complete_cleanly(monkeypatch):
    """Exit code 2 (interrupted) etc. means the RUN broke, not that a number can be trusted."""
    monkeypatch.setattr(subprocess, "run",
                        lambda *a, **k: _fake("1 error in 0.1s", returncode=2))
    with pytest.raises(Unmeasurable, match="did not complete cleanly"):
        _probe().suite({})


def test_an_errored_test_cannot_read_as_a_clean_pass(monkeypatch):
    """⭐ The regression review caught: `suite()` only parsed 'passed'/'failed', so a run with
    'N passed, 1 error' (a fixture/setup failure — pytest's own separate bucket) matched
    'passed' and reported A5 as green. Real pytest reproduction: exit 1, '1 passed, 1 error'.
    The fix folds the error count into `failed` — this must NOT come back as failed=0."""
    real_run = subprocess.run
    fake = _fake("1 passed, 1 error in 0.01s", returncode=1)
    monkeypatch.setattr(subprocess, "run", _mock_pytest_call_only(fake, real_run))
    result = _probe(root=".").suite({})
    assert result["failed"] == 1, result   # the error, not silently dropped
    assert result["passed"] == 1


def test_returncode_zero_with_reported_failures_is_inconsistent_not_a_pass(monkeypatch):
    monkeypatch.setattr(subprocess, "run",
                        lambda *a, **k: _fake("1 failed, 4 passed in 0.1s", returncode=0))
    with pytest.raises(Unmeasurable, match="parsing disagrees"):
        _probe().suite({})


def test_returncode_one_with_nothing_parsed_as_failed_is_inconsistent(monkeypatch):
    monkeypatch.setattr(subprocess, "run",
                        lambda *a, **k: _fake("5 passed in 0.1s", returncode=1))
    with pytest.raises(Unmeasurable, match="parsing is incomplete"):
        _probe().suite({})


# ---------------------------------------------------------------- measures when it can


@requires_checkout
def test_config_constructs_the_real_windsorai_classes():
    cfg = WindsorAiGepProbes().config({})
    assert "WindsorAIConnection" in cfg["constructed"]
    assert "WindsorAIOptions" in cfg["constructed"]
    assert len(cfg["accounts"]) == 6, "six Navira Google Ads account ids, per GP-226"
    assert cfg["fields_count"] > 0


@requires_checkout
def test_config_is_unmeasurable_when_its_own_hook_into_the_deployment_moves(monkeypatch):
    """⭐ The regression review caught: reading a moved/renamed hook as 'no accounts' made A1
    report FAIL (a connector defect) for what is actually a probe defect. An upstream rename of
    the private constant this probe depends on must be UNMEASURABLE, not a fabricated FAIL."""
    import importlib
    deploy_mod = importlib.import_module("connector.accounts.GEP.deployments.windsorai")
    saved = deploy_mod._GOOGLE_ADS_ACCOUNT_IDS
    del deploy_mod._GOOGLE_ADS_ACCOUNT_IDS
    try:
        with pytest.raises(Unmeasurable, match="_GOOGLE_ADS_ACCOUNT_IDS"):
            WindsorAiGepProbes().config({})
    finally:
        deploy_mod._GOOGLE_ADS_ACCOUNT_IDS = saved


@requires_checkout
def test_a1_and_a5_measure_for_real_while_everything_else_still_refuses():
    """⭐ The regression this whole lane exists to prevent.

    Wiring two real instruments must not turn the other ten into a silent PASS. A1 must PASS on
    real construction; A5 must be an actual measurement (not UNMEASURABLE) of the real suite;
    every unwired assertion must stay UNMEASURABLE; and the contract's overall verdict must never
    read PASS while ten of twelve assertions were never measured.

    Scoped to `tests/test_windsorai.py` (one subprocess, ~15s) rather than the full repo suite —
    the full-suite path is the same `suite()` method with `test_paths=[]`, exercised live by
    `python -m factory.certify blueprints/windsorai_gep.yaml` (see docs/evidence/), not repeated
    here on every test run.
    """
    target = load_target(BLUEPRINT)
    res = build_contract(target, WindsorAiGepProbes(test_paths=["tests/test_windsorai.py"])).run({})
    by_name = {r.name.split("-")[0]: r for r in res.results}

    assert by_name["A1"].verdict is Verdict.PASS, by_name["A1"].detail
    assert by_name["A5"].verdict is Verdict.PASS, by_name["A5"].detail
    assert "15 passed" in by_name["A5"].detail, by_name["A5"].detail   # not a no-op: this fails
                                                                        # if the count is wrong

    still_unwired = {"A2", "A3", "A4", "A6", "A7", "A8", "A9", "A10", "A11", "A12"}
    for aid in still_unwired:
        assert by_name[aid].verdict is Verdict.UNMEASURABLE, (
            f"{aid} has no real instrument yet and must not report anything but UNMEASURABLE: "
            f"{by_name[aid]}")

    assert res.verdict is not Verdict.PASS, (
        "ten of twelve assertions are still unwired — the contract cannot be green")


@requires_checkout
def test_revision_is_marked_dirty_when_the_checkout_has_uncommitted_changes():
    """The checkout this session ran against IS dirty (untracked files from other work) — this
    asserts that fact is surfaced, not laundered into a clean-looking sha."""
    from factory.live_probes import _revision
    rev = _revision(_ROOT)
    status = subprocess.run(["git", "status", "--porcelain"], cwd=_ROOT,
                            capture_output=True, text=True)
    if status.stdout.strip():
        assert rev.endswith("-dirty"), rev
    else:
        assert not rev.endswith("-dirty"), rev
