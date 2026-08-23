"""The suite cache must not become the thing that serves a stale green.

The `suite` gate shells out to a full pytest run and is 97.6% of a `measure()`. Caching it took a
page render from 27.3 s to 0.84 s — but a cache is a machine for showing an old number as if it
were current, which is the exact drift this whole project exists to remove. The first version
shipped with three real holes, all found by attacking it rather than by testing it:

    scripts/ was not in the fingerprint      — and the suite imports it, so the one file being
                                               edited could not invalidate its own cache
    the artifact HTML was not in it          — and `test_tracker_is_current.py` reads it
    the environment was not in it            — and $PREFECT_CONNECTORS changes the verdict,
                                               which is F72 coming back through the cache door

These tests exist so those cannot come back quietly.
"""
from __future__ import annotations

import json
import time

import pytest

from factory import readiness as R


# --------------------------------------------------------------------------- the fingerprint


def test_the_fingerprint_covers_every_directory_the_suite_imports():
    """`from scripts import local_tracker` makes scripts/ a suite input. So it must be hashed."""
    covered = {str(f.relative_to(R.FACTORY)).replace("\\", "/") for f in R._suite_inputs()}
    roots = {c.split("/")[0] for c in covered}
    for needed in ("tests", "factory", "scripts"):
        assert needed in roots, f"{needed}/ is a suite input but is not in the fingerprint"


def test_the_fingerprint_covers_the_artifact_the_suite_reads():
    """test_tracker_is_current.py reads docs/artifacts/agent-factory.html and asserts on it."""
    covered = {str(f.relative_to(R.FACTORY)).replace("\\", "/") for f in R._suite_inputs()}
    artifact = "docs/artifacts/agent-factory.html"
    if not (R.FACTORY / artifact).is_file():
        pytest.skip("no artifact on disk to include")
    assert artifact in covered


def test_editing_the_tracker_changes_the_fingerprint(tmp_path, monkeypatch):
    """The hole that mattered most: the file under active edit must invalidate its own cache."""
    target = R.FACTORY / "scripts" / "local_tracker.py"
    before = R._suite_fingerprint()
    original = target.read_bytes()
    try:
        target.write_bytes(original + b"\n# fingerprint probe\n")
        assert R._suite_fingerprint() != before, (
            "editing scripts/local_tracker.py did not change the fingerprint — "
            "the cache would serve a verdict measured against different code")
    finally:
        target.write_bytes(original)
    assert R._suite_fingerprint() == before, "the probe did not restore cleanly"


def test_the_environment_is_part_of_the_fingerprint(monkeypatch):
    """F72 through the cache door: same bytes, different checkout, different verdict."""
    before = R._suite_fingerprint()
    monkeypatch.setenv("PREFECT_CONNECTORS", r"C:\some\other\checkout")
    assert R._suite_fingerprint() != before, (
        "$PREFECT_CONNECTORS does not affect the fingerprint, but it affects the verdict")


# --------------------------------------------------------------------------- serving rules


class _FakeRun:
    """A stand-in for a completed pytest run, so a cache MISS costs nothing and is observable.

    Asserting on the CALL rather than on a raised sentinel matters here: the gate wraps its
    subprocess in `except Exception -> Unmeasurable`, so anything thrown from the stub arrives as
    Unmeasurable and stops distinguishing "it re-ran" from "it broke".
    """
    returncode = 0
    stdout = "999 passed in 0.01s"
    stderr = ""


def _cache(monkeypatch, tmp_path, *, verdict, age_sec, fingerprint=None):
    """Plant a cache entry and return a list that records every attempt to re-run the suite."""
    f = tmp_path / "suite-cache.json"
    f.write_text(json.dumps({
        "fingerprint": fingerprint if fingerprint is not None else R._suite_fingerprint(),
        "at": time.time() - age_sec, "verdict": verdict,
        "headline": "999 passed", "evidence": [], "source": "tests/"}), encoding="utf-8")
    monkeypatch.setattr(R, "_SUITE_CACHE", f)
    # The suite-wide recursion guard would otherwise short-circuit before the cache logic runs.
    monkeypatch.delenv("AGENT_FACTORY_IN_SUITE", raising=False)
    ran = []
    monkeypatch.setattr(R.subprocess, "run", lambda *a, **k: (ran.append(1), _FakeRun())[1])
    return ran


def test_a_fresh_passing_cache_is_served_with_its_age_in_the_headline(monkeypatch, tmp_path):
    """The house rule: a cached figure carries its age in the SAME STRING as the figure."""
    ran = _cache(monkeypatch, tmp_path, verdict=R.PASS, age_sec=120)
    res = R.g_contract_suite_green()
    assert not ran, "a fresh passing cache was ignored and the suite re-ran"
    assert res.verdict == R.PASS
    assert "999 passed" in res.headline
    assert "cached" in res.headline and "2m ago" in res.headline, res.headline


def test_a_cached_failure_is_never_served(monkeypatch, tmp_path):
    """F20/F21: a gate that cannot pass is as broken as one that cannot refuse.

    A FAIL can be fixed by an environment change with no bytes touched, so replaying it would keep
    the board red over a suite that now passes.
    """
    ran = _cache(monkeypatch, tmp_path, verdict=R.FAIL, age_sec=120)
    R.g_contract_suite_green()
    assert ran, "a cached FAIL was replayed instead of being re-earned"


def test_an_expired_cache_is_not_served(monkeypatch, tmp_path):
    """The negative control must be re-earned on a clock, not replayed from JSON forever."""
    ran = _cache(monkeypatch, tmp_path, verdict=R.PASS, age_sec=R._SUITE_TTL_SEC + 60)
    R.g_contract_suite_green()
    assert ran, "an expired cache was served — the negative control was never re-earned"


def test_a_cache_from_different_code_is_not_served(monkeypatch, tmp_path):
    """The whole point of keying on content."""
    ran = _cache(monkeypatch, tmp_path, verdict=R.PASS, age_sec=10, fingerprint="deadbeef")
    R.g_contract_suite_green()
    assert ran, "a cache keyed to different code was served"


def test_a_future_dated_cache_does_not_render_a_negative_age(monkeypatch, tmp_path):
    """A backward clock correction must not print '-3m ago' — that reads as a glitch to ignore."""
    assert R._age(-200) == "0s ago"


def test_age_has_a_day_bucket():
    """Without one, a five-day-old cache reads '120h 0m ago', which nobody parses as stale."""
    assert R._age(5 * 86400 + 3600) == "5d 1h ago"


# --------------------------------------------------------------------------- recursion guard


def test_the_gate_refuses_to_run_the_suite_from_inside_the_suite(monkeypatch):
    """Without this, one test rendering a measuring tab fans out pytest without bound.

    It did: 14 nested processes before it was killed. NOT-RUN is also the honest verdict — a suite
    cannot measure itself while it is still running.
    """
    monkeypatch.setenv("AGENT_FACTORY_IN_SUITE", "1")
    ran = []
    monkeypatch.setattr(R.subprocess, "run", lambda *a, **k: (ran.append(1), _FakeRun())[1])
    res = R.g_contract_suite_green()
    assert not ran, "the gate recursed into pytest from inside the suite"
    assert res.verdict == R.NOT_RUN
    assert "inside itself" in res.headline


def test_the_guard_is_set_for_the_whole_suite():
    """conftest sets it at import so no test has to remember — proven by reading it here."""
    import os
    assert os.environ.get("AGENT_FACTORY_IN_SUITE") == "1"


# --------------------------------------------------------------------------- atomicity


def test_the_cache_write_is_atomic(monkeypatch, tmp_path):
    """Threaded server + two cold viewers = interleaved writes = invalid JSON = a pytest herd."""
    f = tmp_path / "suite-cache.json"
    monkeypatch.setattr(R, "_SUITE_CACHE", f)
    R._cache_write({"fingerprint": "x", "at": time.time(), "verdict": R.PASS,
                    "headline": "h", "evidence": [], "source": "tests/"})
    assert json.loads(f.read_text(encoding="utf-8"))["fingerprint"] == "x"
    assert not list(tmp_path.glob("*.tmp")), "a temp file was left behind"


def test_a_write_failure_never_breaks_the_measurement(monkeypatch, tmp_path):
    """A cache that cannot be written must not fail the thing it was speeding up."""
    monkeypatch.setattr(R, "_SUITE_CACHE", tmp_path / "nope" / "x.json")
    monkeypatch.setattr(R.os, "replace",
                        lambda *a, **k: (_ for _ in ()).throw(OSError("disk full")))
    R._cache_write({"fingerprint": "x", "at": time.time(), "verdict": R.PASS,
                    "headline": "h", "evidence": [], "source": "tests/"})   # must not raise


# --------------------------------------------------------------------------- the page's own claim


def test_no_surface_claims_it_caches_nothing():
    """⛔ The page must not assert a freshness property it does not have.

    R13 called this *"the only defect that makes every other number on the page unreliable"*, and
    it was live for part of 2026-08-23: the suite gate was cached the same day that four strings
    still told the reader nothing on the page was.

    A reader who catches one such claim being false has no way to know which of the other numbers
    to trust — which is worse than the cache itself ever was. So the absolute phrasings are banned
    and the honest one names the exception.
    """
    import pathlib
    banned = ("nothing on this page is cached", "never caches", "nothing here is cached",
              "no caching", "nothing is cached")
    offenders = []
    for f in sorted((R.FACTORY / "scripts").glob("*.py")) + \
             sorted((R.FACTORY / "factory").glob("*.py")):
        for i, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            low = line.lower()
            for phrase in banned:
                if phrase in low:
                    offenders.append(f"{f.name}:{i}  {line.strip()[:90]}")
    assert not offenders, (
        "these assert the surface caches nothing, which is false — the suite gate is cached:\n  "
        + "\n  ".join(offenders))


def test_the_ban_can_actually_fail():
    """Proof the guard above is not vacuous."""
    probe = 'w("Nothing on this page is cached; it re-ran when you loaded it.")'
    assert "nothing on this page is cached" in probe.lower()
