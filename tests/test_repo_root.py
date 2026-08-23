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


# --------------------------------------------------------------------------- the whole class


def _computes_data_root_from_file(line: str) -> bool:
    """True for a line that builds a `.data/` path out of this file's own location.

    Deliberately a substring test rather than a regex: the thing being detected is three literal
    tokens on one line, and a regex here would be harder to read than the rule it encodes.
    """
    s = line.lstrip()
    if s.startswith("#"):
        return False
    return "__file__" in s and ".parent.parent" in s and ".data" in s


def test_no_module_computes_a_shared_data_root_from_its_own_file():
    """A STRUCTURAL guard, because fixing instances did not work.

    This bug appeared five times — claims, worktrees, handoff, bus, operator — each found
    separately, each fixed separately, and every fix left the pattern available for the next
    module. `runs.py` even had the correct resolver and kept it private, which is precisely what
    let the others stay wrong.

    So the rule is enforced rather than remembered: **anything under `.data/` is estate-wide state
    and must resolve through `factory.repo`.** Git-tracked content may legitimately be
    checkout-relative — that is the real distinction, and it is why this targets `.data/` instead
    of banning the expression outright.
    """
    factory = repo.primary() / "factory"
    bad = []
    for f in sorted(factory.glob("*.py")):
        if f.name == "repo.py":
            continue
        for i, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            if _computes_data_root_from_file(line):
                bad.append(f"{f.name}:{i}  {line.strip()}")
    assert not bad, (
        "these build a .data/ path from __file__ instead of factory.repo, so the state is "
        "private to whichever worktree happens to run them:\n  " + "\n  ".join(bad))


def test_the_structural_guard_can_actually_fail():
    """Proof the check above is not vacuous — the rule this repo holds every gate to.

    Uses the exact line that shipped in bus.py, so if the detector is ever loosened past the real
    defect this fails rather than quietly passing everything.
    """
    shipped = 'ROOT = pathlib.Path(__file__).resolve().parent.parent / ".data" / "bus"'
    assert _computes_data_root_from_file(shipped), (
        "the guard would not have caught the bug that actually shipped")
    assert not _computes_data_root_from_file('ROOT = _repo.data() / "bus"'), (
        "the guard flags the corrected form, so it would block the fix")
    assert not _computes_data_root_from_file(
        '    # ROOT = pathlib.Path(__file__).resolve().parent.parent / ".data" / "bus"'), (
        "a commented-out line is documentation, not a defect")


def test_boot_prompts_resolve_to_the_real_cross_repo_home():
    """A lane's closing note is the human half that nothing can reconstruct.

    From inside a worktree this used to resolve to
    `<primary>/.worktrees/aldc-launchpad/boot-prompts`, which `mkdir(parents=True, exist_ok=True)`
    then created SILENTLY — writing the note into the directory that gets deleted when the
    worktree is removed. No error, no warning, and the one irreplaceable part of the handoff gone.
    """
    from factory import handoff
    assert handoff.BOOT.name == "boot-prompts"
    assert handoff.BOOT.parent.name == "aldc-launchpad"
    assert ".worktrees" not in handoff.BOOT.parts, (
        f"boot prompts would be written to {handoff.BOOT}, inside a worktree")


def test_the_event_bus_is_shared_across_the_estate():
    """A per-worktree bus is not a bus. Lanes run inside worktrees, which is where it mattered."""
    from factory import bus
    assert ".worktrees" not in bus.ROOT.parts, f"the bus at {bus.ROOT} is private to one worktree"
    assert bus.ROOT.parent.parent == repo.primary()


def test_operator_answers_are_visible_to_the_lane_that_asked():
    """Paul answers from the tracker in the primary; the lane reads from inside its worktree."""
    from factory import operator
    assert ".worktrees" not in operator.ROOT.parts
    assert operator.ROOT.parent.parent == repo.primary()
