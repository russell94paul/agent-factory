"""Runtime capabilities a command needs, checked all at once, before it starts.

⭐ **Why this exists, measured 2026-09-01.** An operator ran the documented meeting command on a
clean environment. It failed on a missing ``yaml``. They installed PyYAML and ran it again. It
compiled, rendered, passed all nine blocking gate checks, reached ``READY_WITH_WARNINGS`` — and
*then* died at stage 4 on ``ModuleNotFoundError: No module named 'playwright'``. Two round trips,
the second one paid for after four minutes of work that had to be thrown away, and a third was
waiting behind it because ``pip install playwright`` does not install a browser.

That is a **discovery-one-at-a-time failure**, and the fix is not to add the missing package. It
is to ask every question before doing any work, and answer them in one message.

⛔ **A capability check is not a substitute for the real thing.** This module answers "could the
instrument run", never "did the instrument pass". `scripts/render_check_client_review.py` remains
the only thing that can say a page rendered, and nothing here may be read as evidence that it did.
The distinction is the same one the estate keeps paying for: an instrument that could not look has
not reported health.
"""
from __future__ import annotations

import importlib.util
import pathlib
import subprocess
import sys
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence

#: Capability names. Deliberately not "packages" — ``chromium`` is a browser binary that a package
#: install does *not* bring with it, and collapsing the two is exactly the gap that was measured.
YAML = "yaml"
PLAYWRIGHT = "playwright"
CHROMIUM = "chromium"

ALL: tuple = (YAML, PLAYWRIGHT, CHROMIUM)

#: What the meeting path needs. Named as a set so a caller states its requirement rather than
#: implying it by which import happens to fail first.
MEETING_READY: tuple = (YAML, PLAYWRIGHT, CHROMIUM)

#: The install line for each capability. `pip install -e ".[dev]"` is the repo's documented
#: bootstrap and now carries playwright; the browser download is a separate step because pip
#: cannot perform it.
_REMEDY: Dict[str, str] = {
    YAML: 'pip install -e ".[dev]"',
    PLAYWRIGHT: 'pip install -e ".[dev]"',
    CHROMIUM: f'"{sys.executable}" -m playwright install chromium',
}

_WHY: Dict[str, str] = {
    YAML: "reads the authored review narrative",
    PLAYWRIGHT: "drives the browser that validates the rendered page",
    CHROMIUM: "the browser itself — pip installs the driver, not the browser",
}


@dataclass(frozen=True)
class Capability:
    """One runtime capability and whether it is actually available here."""
    name: str
    present: bool
    detail: str
    remedy: str
    why: str


def _check_module(name: str) -> tuple:
    """Present iff importable. Uses find_spec so a broken module reports absent, not raises."""
    try:
        spec = importlib.util.find_spec(name)
    except (ImportError, ValueError):                       # pragma: no cover - defensive
        return False, "not importable"
    if spec is None:
        return False, "not installed"
    return True, (spec.origin or "installed")


#: Asks Playwright where chromium is, and prints only that. Run in a subprocess — see below.
_CHROMIUM_PROBE = (
    "from playwright.sync_api import sync_playwright\n"
    "with sync_playwright() as p: print(p.chromium.executable_path)\n"
)


def _check_chromium(timeout: float = 60.0) -> tuple:
    """Present iff Playwright can name a chromium executable that exists on disk.

    ⚠ **Asks Playwright where the browser is; does not guess a path.** A hard-coded cache
    directory would be a second source of truth for something Playwright already knows, and would
    give a confident wrong answer on any machine that moved it.

    ⚠ **Runs in a subprocess, for two reasons.** Starting and stopping the Playwright driver
    without doing any work leaves asyncio teardown warnings on stderr at interpreter shutdown —
    which would surface as alarming noise underneath an otherwise clean preflight. And a driver
    that hangs or crashes takes the child down, not the check.
    """
    ok, _ = _check_module(PLAYWRIGHT)
    if not ok:
        return False, "cannot be checked — playwright is not installed"
    try:
        r = subprocess.run([sys.executable, "-c", _CHROMIUM_PROBE],
                           capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return False, f"playwright did not answer within {timeout:.0f}s"
    except Exception as exc:                                # noqa: BLE001  - defensive
        return False, f"{type(exc).__name__}: {str(exc).strip()[:120]}"
    if r.returncode != 0:
        err = (r.stderr or "").strip().splitlines()
        return False, (err[-1][:140] if err else f"probe exited {r.returncode}")
    path = (r.stdout or "").strip()
    if not path or not pathlib.Path(path).exists():
        return False, f"playwright names {path or '<nothing>'}, which is not on disk"
    return True, path


def check(names: Optional[Sequence[str]] = None) -> List[Capability]:
    """Check every named capability. Never raises, never stops at the first failure."""
    out: List[Capability] = []
    for name in (names or ALL):
        if name == CHROMIUM:
            present, detail = _check_chromium()
        else:
            present, detail = _check_module(name)
        out.append(Capability(name=name, present=present, detail=detail,
                              remedy=_REMEDY.get(name, ""), why=_WHY.get(name, "")))
    return out


def missing(caps: Sequence[Capability]) -> List[Capability]:
    return [c for c in caps if not c.present]


def report(caps: Sequence[Capability]) -> str:
    """One actionable message covering everything that is absent.

    Deduplicates remedies and preserves their order, so an operator missing both packages and the
    browser is given two commands to run — not two commands per missing thing, and not one command
    followed later by another they could have run at the same time.
    """
    gone = missing(caps)
    if not gone:
        return ""
    lines = ["This environment cannot run the meeting validation.",
             "",
             f"Missing {len(gone)} of {len(caps)} required capabilities:"]
    for c in gone:
        lines.append(f"  - {c.name:<11} {c.why}")
        lines.append(f"                ({c.detail})")
    steps: List[str] = []
    for c in gone:
        if c.remedy and c.remedy not in steps:
            steps.append(c.remedy)
    lines += ["", "Run, in order:"]
    lines += [f"  {s}" for s in steps]
    lines += ["",
              "⛔ The browser step is separate and is not optional. `pip install` provides the",
              "   Playwright driver; it does not download a browser, and the rendered validation",
              "   cannot be skipped to reach a client-safe verdict."]
    return "\n".join(lines)


def summary(caps: Sequence[Capability]) -> str:
    """One line per capability, for the ok path where nothing is missing."""
    return "\n".join(f"  {'ok ' if c.present else 'MISSING'} {c.name:<11} {c.detail}"
                     for c in caps)
