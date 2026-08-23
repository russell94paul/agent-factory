"""Shared state must resolve to the primary worktree, from anywhere.

`claims.py` and `worktrees.py` both used `__file__.parent.parent` as the repo root. That is right
in the primary checkout and wrong inside a lane worktree, and the consequence was a **false green
in the finish path** — reproduced on 2026-08-23 in `.worktrees/certify`:

    git status --porcelain          ?? _falsegreen_probe.txt     (dirty)
    worktrees.existing()            {}                           (no worktrees at all)
    worktrees.is_dirty('certify')   False                        (a gate that cannot refuse)

`finish.checks()` reads `is_dirty()` to warn that uncommitted work will not survive the worktree
being removed. Inside a worktree that warning silently stopped existing.

`runs.py` already had the correct resolver and kept it private, which is precisely what let the
other two stay wrong — so these tests assert on the SHARED resolver and on every module that
should be using it, not on one call site.
"""
from __future__ import annotations

import pathlib

from factory import claims, repo, runs, worktrees


def test_the_primary_is_a_real_repository_root():
    """Whatever it resolves to must at least be a git checkout with this package in it."""
    p = repo.primary()
    assert p.is_dir(), p
    assert (p / "factory").is_dir(), f"{p} does not look like this repo"
    assert (p / ".git").exists(), f"{p} has no .git"


def test_the_primary_is_never_a_linked_worktree():
    """The whole point. `<primary>/.worktrees/<lane>` is the wrong answer, everywhere."""
    p = repo.primary().resolve()
    assert ".worktrees" not in p.parts, (
        f"the primary resolved to {p}, which is inside a linked worktree — shared state would be "
        "private to that lane")


def test_every_module_holding_shared_state_uses_the_same_root(real_ledger):
    """The fork, closed. Three modules answered this three ways and only one was right.

    Asserting each one lands under the SAME primary is what stops a fourth copy appearing.

    Takes `real_ledger` to opt out of conftest's autouse redirect, which points `runs._primary`
    at a tmp directory. Pointed there this assertion would compare two tmp paths and pass
    trivially — and a check that cannot fail is not a check.
    """
    primary = repo.primary().resolve()
    assert worktrees.REPO.resolve() == primary, "worktrees.REPO forked from the primary"
    assert claims.ROOT.resolve().parent.parent == primary, "claims.ROOT forked from the primary"
    assert runs._primary().resolve() == primary, "runs._primary forked from the primary"


def test_runs_delegates_rather_than_keeping_a_private_twin(real_ledger):
    """`runs` had the only correct copy, privately — which is why the others stayed broken.

    `real_ledger` opts out of the ledger redirect; see the note above.
    """
    assert runs._primary() == repo.primary()


def test_worktree_root_is_directly_under_the_primary():
    """If ROOT nests (…/.worktrees/<lane>/.worktrees) the `existing()` filter matches nothing."""
    assert worktrees.ROOT.resolve() == (repo.primary() / ".worktrees").resolve()
    assert worktrees.ROOT.resolve().parent == repo.primary().resolve()


def test_existing_finds_the_worktrees_git_reports():
    """`existing()` must agree with git, not with a path guess.

    This is the assertion that was false from inside a worktree: git listed four and `existing()`
    returned none, because the filter root had nested one level too deep.
    """
    import subprocess
    out = subprocess.run(["git", "-C", str(repo.primary()), "worktree", "list", "--porcelain"],
                         capture_output=True, text=True, timeout=30).stdout
    from_git = set()
    root = (repo.primary() / ".worktrees").resolve()
    for line in out.splitlines():
        if line.startswith("worktree "):
            p = pathlib.Path(line[len("worktree "):].strip()).resolve()
            try:
                rel = p.relative_to(root)
            except ValueError:
                continue
            if len(rel.parts) == 1:
                from_git.add(rel.parts[0])
    if not from_git:
        import pytest
        pytest.skip("no lane worktrees on this machine — nothing to agree about")
    assert set(worktrees.existing()) == from_git


def test_in_worktree_agrees_with_where_the_primary_points():
    """A direct way to ask 'am I somewhere that used to break things?'"""
    assert repo.in_worktree() == (repo.primary().resolve() != repo.HERE.resolve())
