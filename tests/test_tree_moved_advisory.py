"""The checkout-moved advisory: it must fire when the tree moved, and shut up otherwise.

A warning that cries wolf gets switched off, and a warning nobody has watched fire is decoration.
Both failure modes are pinned here.

⭐ **The most important test in this file is the last one.** The first draft of this advisory
called `sessions.live_sessions()` — a function that does not exist — behind a `hasattr` guard, so
the contention branch would have been permanently dead and the module would have shipped a warning
it could never print. That is the inert-control defect, committed while writing a control. The
structural test at the bottom exists so the next invented helper fails loudly instead.
"""
from __future__ import annotations

import importlib.util
import json
import pathlib

import pytest

from factory import repo as _repo

#: ⚠ NOT `_repo.primary()`. This is the third time that expression has been wrong in two days:
#: it resolves to the shared primary checkout, so a test run from a lane worktree would load the
#: PRIMARY's copy of the hooks and silently test code other than the code under test. The first
#: version of this file did exactly that and errored on a file that does not exist there yet.
#: `repo.primary()` is right for shared STATE and wrong for the SOURCE you are exercising. See
#: F91, and `test_repo_root.py::test_readiness_does_not_derive_the_estate_root_from_its_own_file`.
HOOKS = pathlib.Path(__file__).resolve().parent.parent / "scripts" / "hooks"


def _load(name):
    spec = importlib.util.spec_from_file_location(name.replace("-", "_"), HOOKS / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def tm():
    return _load("git-tree-moved")


def _payload(cmd, cwd=None, session="unit-test-session"):
    return {"tool_input": {"command": cmd},
            "cwd": str(cwd or _repo.primary()),
            "session_id": session}


# --------------------------------------------------------------------------- silence

@pytest.mark.parametrize("cmd", ["ls -la", "git status", "git log --oneline", "git diff",
                                 "pytest -q", "python -m factory.demo"])
def test_a_command_that_cannot_be_spoiled_by_a_moved_tree_is_silent(tm, cmd):
    """Reads cannot be spoiled by the tree having moved, so warning about them is noise —
    and a hook that fires on every `git status` is a hook people disable."""
    assert tm.advisory(_payload(cmd)) is None


def test_the_first_write_of_a_session_is_a_baseline_not_a_finding(tm, tmp_path, monkeypatch):
    """Nothing to compare against yet. Reporting a move here would be a false positive on the
    very first commit of every session."""
    monkeypatch.setattr(tm, "_state_path", lambda root, s: str(tmp_path / f"{s}.json"))
    assert tm.advisory(_payload("git commit -m x", session="fresh")) is None


def test_an_unmoved_tree_is_silent(tm, tmp_path, monkeypatch):
    monkeypatch.setattr(tm, "_state_path", lambda root, s: str(tmp_path / f"{s}.json"))
    p = _payload("git commit -m x", session="steady")
    assert tm.advisory(p) is None          # baseline
    assert tm.advisory(p) is None          # nothing moved since


# --------------------------------------------------------------------------- it fires

def test_a_moved_head_is_reported_with_both_values(tm, tmp_path, monkeypatch):
    """Measured on 2026-08-31: HEAD moved 6d9e94a -> aef21e7 -> ee4bc8d mid-session, both times
    a `pull --ff-only` of work merged elsewhere. The session had no way to know."""
    state = tmp_path / "moved.json"
    monkeypatch.setattr(tm, "_state_path", lambda root, s: str(state))
    p = _payload("git commit -m x", session="moved")
    assert tm.advisory(p) is None
    was = json.loads(state.read_text(encoding="utf-8"))
    state.write_text(json.dumps({**was, "head": "deadbee"}), encoding="utf-8")

    body = tm.advisory(p)
    assert body, "the advisory did not fire on a moved HEAD"
    assert "deadbee" in body and was["head"] in body, "a move must name BOTH values"
    assert "moved" in body.lower()


def test_a_moved_branch_is_reported(tm, tmp_path, monkeypatch):
    state = tmp_path / "branch.json"
    monkeypatch.setattr(tm, "_state_path", lambda root, s: str(state))
    p = _payload("git add -A", session="branchmove")
    assert tm.advisory(p) is None
    was = json.loads(state.read_text(encoding="utf-8"))
    state.write_text(json.dumps({**was, "branch": "some/other-branch"}), encoding="utf-8")

    body = tm.advisory(p)
    assert body and "some/other-branch" in body
    assert "worktree" in body, "the advisory must name the remedy, not just the hazard"


# --------------------------------------------------------------------------- boundaries

def test_it_is_silent_inside_a_linked_worktree(tm, tmp_path, monkeypatch):
    """⭐ The whole design claim. A worktree has its own HEAD and its own index, so a session in
    one cannot be moved by another — the isolation IS the control, and this advisory is only the
    reminder for the shared surface. Warning inside a worktree would train the reader to ignore it.
    """
    monkeypatch.setattr(tm, "_state_path", lambda root, s: str(tmp_path / f"{s}.json"))
    monkeypatch.setattr(tm, "_is_linked_worktree", lambda cwd: True)
    p = _payload("git commit -m x", session="in-worktree")
    tm.advisory(p)
    assert tm.advisory(p) is None


def test_it_never_returns_a_permission_decision(tm):
    """⛔ Structural, and non-negotiable. A hook that blocks a commit on a false positive costs
    more than the hazard: the 2026-08-23 damage was one unpushed commit, recoverable in a minute.
    This module must only ever add text."""
    src = (HOOKS / "git-tree-moved.py").read_text(encoding="utf-8")
    for forbidden in ("permissionDecision", "\"deny\"", "'deny'", "exit(1)", "exit(2)"):
        assert forbidden not in src, f"the advisory must not be able to block a command: {forbidden}"


def test_every_failure_path_is_swallowed(tm, monkeypatch):
    """A broken advisory must not break the command it was advising on."""
    monkeypatch.setattr(tm, "_git", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom")))
    try:
        assert tm.advisory(_payload("git commit -m x")) is None
    except Exception as exc:                                       # noqa: BLE001
        pytest.fail(f"the advisory raised instead of staying quiet: {exc!r}")


# --------------------------------------------------------------------------- the inert branch

def test_the_contention_helper_it_depends_on_actually_exists():
    """⭐ The test that would have caught this module's own first draft.

    It called `sessions.live_sessions()`, which does not exist, behind a `hasattr` guard — so the
    contention branch could never fire and nobody would have noticed, because its absence looks
    exactly like "no contention". Pin the real name.
    """
    from factory import sessions
    assert hasattr(sessions, "contended_repos"), (
        "git-tree-moved.py calls sessions.contended_repos(); if it was renamed, the advisory's "
        "contention branch has gone silently inert rather than failing")
    rows = sessions.contended_repos()
    assert isinstance(rows, list)
    for row in rows:
        assert "attribution" in row, (
            "rows must keep carrying attribution: NOT-MEASURABLE — the advisory reports a "
            "condition, never an accusation, and it relies on this field to say so")


def test_the_bus_hook_still_delivers_bus_traffic():
    """The advisory rides inside lane-bus.py to share one interpreter start. It must not have
    displaced the thing that hook was already for."""
    src = (HOOKS / "lane-bus.py").read_text(encoding="utf-8")
    assert "bus.unread" in src and "bus.render" in src and "bus.mark_read" in src
    assert "_tree_advisory" in src
    assert 'if "git " in' in src, (
        "the checker's import must stay gated on a free substring test — loading it on every "
        "tool call cost this hook 213ms -> 273ms, paid mostly by commands that are not git")
