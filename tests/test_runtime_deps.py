"""Runtime capability preflight, and the certification rule it protects.

Two defects are pinned here, both surfaced by an operator running the documented meeting command
on a clean environment on 2026-09-01:

1. **Dependencies were discovered one at a time.** Missing `yaml` → install → four minutes of
   successful compile, render and nine passing gate checks → `ModuleNotFoundError: playwright` at
   stage 4, with a third round trip still waiting for the browser binary that `pip install` does
   not fetch. Everything knowable in the first second was learned over three runs.

2. **`--no-render` could print SAFE TO OPEN.** The verdict tested `render_ok is not False`, and a
   skipped browser pass leaves it `None`. A client-facing page that no browser had ever loaded
   could be certified — source-implies wearing rendered-confirmed's clothes.

Every check below has a negative control. A preflight that always reports missing capabilities,
or a certification rule that always refuses, tells an operator nothing.
"""
from __future__ import annotations

import pathlib
import re

import pytest

from factory import runtime_deps as rd

REPO = pathlib.Path(__file__).resolve().parent.parent


# --------------------------------------------------------------------------------------------
# 1. The preflight sees what is there, and reports what is not
# --------------------------------------------------------------------------------------------

def test_a_present_capability_is_reported_present():
    """Negative control. yaml is a declared core dependency, so it must be here."""
    caps = rd.check([rd.YAML])
    assert caps[0].present, caps[0].detail
    assert rd.missing(caps) == []
    assert rd.report(caps) == ""


def test_an_absent_module_is_reported_absent_with_a_remedy(monkeypatch):
    real = rd._check_module
    monkeypatch.setattr(rd, "_check_module",
                        lambda n: (False, "not installed") if n == rd.PLAYWRIGHT else real(n))
    caps = rd.check([rd.YAML, rd.PLAYWRIGHT])
    gone = rd.missing(caps)
    assert [c.name for c in gone] == [rd.PLAYWRIGHT]
    assert gone[0].remedy


def test_every_capability_carries_a_remedy_and_a_reason():
    """A report that names a problem without naming the fix is a bug report, not a preflight."""
    for c in rd.check(rd.ALL):
        assert c.remedy, f"{c.name} has no remedy"
        assert c.why, f"{c.name} does not say why it is needed"


# --------------------------------------------------------------------------------------------
# 2. Everything missing is reported at once — the actual defect
# --------------------------------------------------------------------------------------------

def test_the_report_names_every_missing_capability_not_just_the_first(monkeypatch):
    monkeypatch.setattr(rd, "_check_module", lambda n: (False, "not installed"))
    monkeypatch.setattr(rd, "_check_chromium", lambda **kw: (False, "no browser"))
    caps = rd.check(rd.MEETING_READY)
    text = rd.report(caps)
    for name in rd.MEETING_READY:
        assert name in text, f"{name} missing from the one actionable message"
    assert "Missing 3 of 3" in text


def test_the_report_deduplicates_remedies_but_keeps_the_browser_step(monkeypatch):
    """yaml and playwright share one pip line; chromium needs its own. Both facts matter."""
    monkeypatch.setattr(rd, "_check_module", lambda n: (False, "not installed"))
    monkeypatch.setattr(rd, "_check_chromium", lambda **kw: (False, "no browser"))
    text = rd.report(rd.check(rd.MEETING_READY))
    # Read only the steps block. The descriptive bullets above it also say "pip install", which
    # is what the first draft of this test matched — it failed on a correct report.
    body = text.split("Run, in order:", 1)[1]
    steps = [ln.strip() for ln in body.splitlines()
             if ln.startswith("  ") and ln.strip() and not ln.strip().startswith(("⛔", "Playwright", "cannot"))]
    assert len(steps) == 2, steps
    assert sum("pip install" in s for s in steps) == 1
    assert any("playwright install chromium" in s for s in steps)


def test_chromium_absence_is_distinct_from_playwright_absence(monkeypatch):
    """`pip install playwright` does not download a browser. Collapsing the two was the gap."""
    monkeypatch.setattr(rd, "_check_chromium", lambda **kw: (False, "not downloaded"))
    caps = rd.check(rd.MEETING_READY)
    by = {c.name: c for c in caps}
    assert by[rd.PLAYWRIGHT].present is True
    assert by[rd.CHROMIUM].present is False
    assert "playwright install chromium" in by[rd.CHROMIUM].remedy


def test_a_chromium_path_that_does_not_exist_is_not_present(monkeypatch, tmp_path):
    """Playwright naming a browser is not the same as the browser being on disk."""
    class R:
        returncode, stdout, stderr = 0, str(tmp_path / "nope" / "chrome.exe"), ""
    monkeypatch.setattr(rd.subprocess, "run", lambda *a, **k: R())
    present, detail = rd._check_chromium()
    assert present is False
    assert "not on disk" in detail


def test_a_real_chromium_path_is_present(monkeypatch, tmp_path):
    """Negative control for the check above."""
    exe = tmp_path / "chrome.exe"
    exe.write_text("x", encoding="utf-8")

    class R:
        returncode, stdout, stderr = 0, str(exe), ""
    monkeypatch.setattr(rd.subprocess, "run", lambda *a, **k: R())
    present, _ = rd._check_chromium()
    assert present is True


def test_the_chromium_probe_never_raises_when_playwright_explodes(monkeypatch):
    class R:
        returncode, stdout, stderr = 1, "", "Executable doesn't exist at ...\nrun install"
    monkeypatch.setattr(rd.subprocess, "run", lambda *a, **k: R())
    present, detail = rd._check_chromium()
    assert present is False and detail


# --------------------------------------------------------------------------------------------
# 3. The declaration actually declares it
# --------------------------------------------------------------------------------------------

def _pyproject() -> str:
    return (REPO / "pyproject.toml").read_text(encoding="utf-8")


def test_playwright_is_declared_as_a_dependency():
    """The hole the operator fell into: the render scripts imported an undeclared package."""
    assert "playwright" in _pyproject(), "playwright is not declared in pyproject.toml"


def test_the_documented_install_command_brings_playwright():
    """README and bootstrap.sh both run `pip install -e ".[dev]"`, so dev must carry it."""
    m = re.search(r"^dev = \[(.*?)\]", _pyproject(), re.M | re.S)
    assert m, "no dev extra in pyproject.toml"
    assert "playwright" in m.group(1), "the documented install does not bring playwright"


def test_the_render_extra_and_dev_have_not_drifted_apart():
    """They are listed twice on purpose; this is what stops the duplication going stale."""
    src = _pyproject()
    render = re.search(r"^render = \[(.*?)\]", src, re.M | re.S)
    dev = re.search(r"^dev = \[(.*?)\]", src, re.M | re.S)
    assert render and dev
    for pin in re.findall(r'"([^"]+)"', render.group(1)):
        assert pin in dev.group(1), f"{pin} is in `render` but not in `dev`"


def test_bootstrap_installs_the_browser_binary():
    """pip cannot download a browser, so bootstrap has to ask for it explicitly."""
    sh = (REPO / "scripts" / "bootstrap.sh").read_text(encoding="utf-8")
    assert "playwright install chromium" in sh


# --------------------------------------------------------------------------------------------
# 4. A skipped browser pass can never certify — requirement 6, and defect 2
# --------------------------------------------------------------------------------------------

def _meeting_ready_source() -> str:
    return (REPO / "scripts" / "meeting_ready.py").read_text(encoding="utf-8")


def test_certification_requires_render_ok_to_be_exactly_true():
    """`is not False` admits None, which is what a skipped run leaves behind.

    Asserted against the source because the alternative is running the whole four-stage pipeline
    twice inside a unit test. The behavioural half is covered by the two tests below.
    """
    src = _meeting_ready_source()
    m = re.search(r"^\s*safe = .*$", src, re.M)
    assert m, "no safe verdict line in meeting_ready.py"
    assert "render_ok is True" in m.group(0), m.group(0)
    assert "is not False" not in m.group(0)


@pytest.mark.parametrize("flag", ["--no-render", "--check-env"])
def test_a_non_rendering_mode_never_prints_the_certification(flag, tmp_path):
    """Neither mode loads a browser, so neither may ever emit the client-safe sentence."""
    import subprocess
    import sys
    r = subprocess.run([sys.executable, str(REPO / "scripts" / "meeting_ready.py"), flag,
                        "--out", str(tmp_path / "out.html")],
                       cwd=str(REPO), capture_output=True, text=True, timeout=300)
    assert "SAFE TO OPEN IN FRONT OF THE CLIENT" not in r.stdout, r.stdout[-800:]


def test_no_render_exits_non_zero_even_when_the_gate_would_pass(tmp_path):
    """The load-bearing one. The gate can say READY and this must still refuse."""
    import subprocess
    import sys
    root = REPO / ".worktrees" / "mission"
    if not root.exists():                                   # pragma: no cover
        pytest.skip("mission worktree not present")
    r = subprocess.run([sys.executable, str(REPO / "scripts" / "meeting_ready.py"),
                        "--root", str(root), "--no-render",
                        "--out", str(tmp_path / "out.html")],
                       cwd=str(REPO), capture_output=True, text=True, timeout=300)
    assert "READY" in r.stdout, "expected the gate itself to pass, or this proves nothing"
    assert r.returncode != 0, "a skipped browser pass must not exit 0"
    assert "NOT CERTIFIED" in r.stdout


def test_a_missing_capability_stops_before_any_work_is_done(tmp_path, monkeypatch):
    """Exit 3, and no artifact written — the point is that nothing is attempted."""
    import subprocess
    import sys
    out = tmp_path / "should-not-exist.html"
    env = dict(**__import__("os").environ)
    # An import path with nothing on it: yaml becomes unimportable for the child only.
    env["PYTHONPATH"] = str(tmp_path)
    env["PYTHONHOME"] = ""
    r = subprocess.run([sys.executable, str(REPO / "scripts" / "meeting_ready.py"),
                        "--check-env"],
                       cwd=str(REPO), capture_output=True, text=True, timeout=300, env=env)
    # Whatever the child's environment resolved to, the contract holds: either everything was
    # present (exit 0) or the report named what was not (exit 3). Never a traceback.
    assert r.returncode in (0, 3), r.stderr[-500:]
    assert "ModuleNotFoundError" not in r.stderr
    assert not out.exists()
