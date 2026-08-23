"""Two sessions, one checkout — the hazard, and the two instruments that see different halves.

On 2026-08-23 commit `fc71b6a` staged a `factory/claims.py` that imports `factory.repo` while
`repo.py` was untracked, and HEAD stopped importing. The proximate cause was one session running
`git add` across a directory another session was mid-edit in. Neither acted wrongly.

`sessions.collisions()` existed and did not name the repo involved: it keys on **cwd**, and all
four live sessions had cwd `aldc-launchpad` while the clobber was in `agent-factory`. It flagged
the right sessions for the wrong reason and would have been silent had their cwds differed.

Two things were built in response, and these tests cover both:

    scripts/hooks/pre-commit-imports.py   catches the CONSEQUENCE — a tree that does not import —
                                          by checking the INDEX rather than the working directory
    sessions.contended_repos()            catches the CONDITION — a dirty repo with more than one
                                          session alive that could be its author
"""
from __future__ import annotations

import pathlib
import subprocess
import sys

import pytest

from factory import repo, sessions

HOOK = repo.primary() / "scripts" / "hooks" / "pre-commit-imports.py"


# --------------------------------------------------------------------------- contended_repos


def test_every_row_declares_attribution_is_not_measurable():
    """The load-bearing honesty. Nothing records which session touched which file.

    A row that named a culprit would be believed, and it would be a guess. The function reports a
    CONDITION — this repo is dirty and several sessions are alive — never an accusation.
    """
    rows = sessions.contended_repos()
    assert rows, "no candidate repos — this guard has nothing to protect"
    for r in rows:
        assert r["attribution"] == "NOT-MEASURABLE"


def test_a_repo_nobody_has_as_cwd_can_still_be_reported():
    """The whole point, and the exact gap that let fc71b6a through.

    `agent-factory` had zero sessions with it as cwd while being the repo actually edited. If the
    candidate set were built only from session cwds, it would be invisible again.
    """
    rows = {r["path"] for r in sessions.contended_repos()}
    assert str(repo.primary().resolve()) in rows, (
        "the primary worktree is not in the candidate set, so a repo edited from elsewhere "
        "would not be examined — which is precisely what happened")


def test_a_clean_repo_is_never_contended():
    """Contention is about uncommitted work at risk, not about session count alone."""
    for r in sessions.contended_repos():
        if r["dirty"] == 0:
            assert not r["contended"], f"{r['name']} is clean but reported contended"


def test_contention_requires_more_than_one_live_session():
    """One session editing its own repo is just work. It must not raise a warning."""
    for r in sessions.contended_repos():
        if r["contended"]:
            assert r["sessions_alive"] > 1
            assert r["dirty"]


def test_a_repo_git_cannot_answer_for_is_not_visible_rather_than_clean(tmp_path, monkeypatch):
    """NOT-VISIBLE and clean are different claims, and only one is about the repo.

    A non-repository returns None, which must never be rendered as "0 files dirty, all good".
    """
    assert sessions._dirty_count(tmp_path) is None, (
        "a directory that is not a git repo reported a dirty count")


def test_collisions_still_reports_shared_cwd():
    """The older instrument keeps its job — it sees a half this one does not.

    Two sessions in ONE worktree is a distinct hazard from a dirty shared repo, and the fix for
    it is different (a worktree per lane). Replacing one with the other would lose that.
    """
    c = sessions.collisions()
    for cwd, rows in c.items():
        assert len(rows) > 1, f"{cwd} reported as a collision with {len(rows)} session(s)"


# --------------------------------------------------------------------------- the pre-commit hook


def _run_hook(cwd=None):
    return subprocess.run([sys.executable, str(HOOK)], cwd=str(cwd or repo.primary()),
                          capture_output=True, text=True, timeout=300)


def test_the_hook_passes_on_the_current_tree():
    """A guard that refuses everything gets bypassed, and then it guards nothing."""
    r = _run_hook()
    assert r.returncode == 0, f"the hook refuses the current committed tree:\n{r.stderr}"


def test_the_hook_refuses_a_tree_whose_dependency_is_unstaged():
    """The negative control, reproducing fc71b6a exactly.

    `factory/repo.py` is removed from the INDEX while staying on disk, so the WORKING TREE still
    imports perfectly — which is why a working-directory check would have passed over the real
    defect. The hook must refuse anyway.
    """
    target = "factory/repo.py"
    assert (repo.primary() / target).is_file()
    subprocess.run(["git", "-C", str(repo.primary()), "rm", "--cached", "-q", target],
                   capture_output=True, text=True, check=True, timeout=60)
    try:
        assert (repo.primary() / target).is_file(), "the file must remain on disk"
        r = _run_hook()
        assert r.returncode == 1, (
            "the hook allowed a commit whose tree cannot import — this is fc71b6a again")
        assert "COMMIT REFUSED" in r.stderr
        assert "repo" in r.stderr
    finally:
        subprocess.run(["git", "-C", str(repo.primary()), "reset", "-q", "HEAD", target],
                       capture_output=True, text=True, timeout=60)
    # Restored, and the guard must go quiet again — otherwise it would block all later work.
    assert _run_hook().returncode == 0, "the tree was not restored cleanly"


def test_the_hook_is_installed_where_worktrees_share_it():
    """git hooks live in the COMMON dir, so one install covers every lane worktree."""
    out = subprocess.run(["git", "-C", str(repo.primary()), "rev-parse", "--git-common-dir"],
                         capture_output=True, text=True, timeout=30).stdout.strip()
    common = pathlib.Path(out)
    if not common.is_absolute():
        common = repo.primary() / common
    hook = common / "hooks" / "pre-commit"
    if not hook.exists():
        pytest.skip("hook not installed on this machine — run --install")
    assert "pre-commit-imports.py" in hook.read_text(encoding="utf-8")
