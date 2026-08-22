"""Every mutation anchor must still match the source it was copied from.

A mutation harness works by holding a **copy of a line of production source** and replacing
it. That makes the anchor a duplicate, and duplicates rot: rename a variable, add a
parameter, reflow a line, and the anchor silently stops matching. The harness itself
reports ANCHOR-MISSING and exits non-zero — but only when someone runs it, and it takes
about twenty minutes because every mutation copies a tree and runs pytest.

That gap is not hypothetical. On 2026-08-22 the reaper's termination call gained a
`_deadline` argument, and both harnesses' anchors for "the call that kills the cloud work"
stopped matching. The connectors harness caught it on the next run. The factory harness had
last been run BEFORE the refactor and was still reporting "All 12 mutations flipped their
gate off PASS" — a true statement about a tree that no longer existed, and one already
quoted in a commit message.

⚠ **An instrument whose input is a copy of the source certifies the version it last ran
against, not the one in the tree.** This test closes that window: it runs in seconds, in
the ordinary suite, and fails the moment an anchor goes stale — so the twenty-minute
harness is never the thing that discovers it.

It deliberately checks only that each anchor is present **exactly once**. Whether removing
it actually changes a verdict is what the harnesses are for; this is the cheap precondition
without which their answers are meaningless.
"""
from __future__ import annotations

import importlib.util
import pathlib

import pytest

from factory.readiness import CONNECTORS

FACTORY = pathlib.Path(__file__).resolve().parent.parent


def _load(path: pathlib.Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _harnesses():
    """(harness label, MUTATIONS list, default target, how a row names its target)."""
    out = []

    probe = FACTORY / "scripts" / "mutate_readiness_probes.py"
    if probe.is_file():
        m = _load(probe, "mutate_readiness_probes")
        # (gate id, edits, removes[, target])
        out.append(("mutate_readiness_probes.py", m.MUTATIONS, 1, 3))

    conn = CONNECTORS / "tests" / "orchestrator" / "mutate_control_plane.py"
    if conn.is_file():
        m = _load(conn, "mutate_control_plane")
        # (label, edits, selector, removes[, target])
        out.append(("mutate_control_plane.py", m.MUTATIONS, 1, 4))

    return out


def _rows():
    rows = []
    for harness, mutations, edits_at, target_at in _harnesses():
        for row in mutations:
            label = row[0]
            edits = row[edits_at]
            target = row[target_at] if len(row) > target_at else "orchestrator/pipelines.py"
            rows.append((harness, label, target, edits))
    return rows


ROWS = _rows()


def test_there_are_mutations_to_check():
    """A zero from an instrument that cannot see is not a measurement."""
    assert ROWS, (
        "no mutation rows were loaded — either both harnesses are missing or their "
        "MUTATIONS shape changed, and this test would then pass by seeing nothing")


@pytest.mark.parametrize(
    "harness,label,target,edits",
    ROWS,
    ids=[f"{h.split('.')[0]}::{lbl}" for h, lbl, _, _ in ROWS],
)
def test_every_anchor_appears_exactly_once_in_its_target(harness, label, target, edits):
    path = CONNECTORS / target
    if not path.is_file():
        pytest.skip(f"{target} not present at {CONNECTORS}")
    src = path.read_text(encoding="utf-8")
    for anchor, _replacement in edits:
        n = src.count(anchor)
        assert n == 1, (
            f"{harness} :: {label!r} — its anchor appears {n} time(s) in {target}, so the "
            f"mutation cannot be applied and that control is UNTESTED. The anchor is a "
            f"copy of production source; something refactored the line under it.\n\n"
            f"anchor:\n{anchor}")
