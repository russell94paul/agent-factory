"""Where the repository actually is — one resolver, so the estate cannot disagree with itself.

⚠ **This module exists because three modules answered "where are we?" three different ways.**
`claims.py`, `worktrees.py` and `runs.py` each computed a root, and only `runs.py` got it right —
privately, in a helper nobody else could reach. The other two used `__file__.parent.parent`, which
is correct in the primary checkout and **wrong inside a lane worktree**, where it resolves to the
worktree instead of the repo that owns it.

That is not a tidiness complaint. It produced a **false green in the finish path**, reproduced on
2026-08-23 in `.worktrees/certify`:

    git status --porcelain        ?? _falsegreen_probe.txt      (dirty)
    worktrees.existing()          {}                            (sees no worktrees at all)
    worktrees.is_dirty('certify') False                         (a gate that cannot refuse)

`existing()` filters `git worktree list` to paths under `<root>/.worktrees`. Run from inside
`<primary>/.worktrees/certify`, that root becomes
`<primary>/.worktrees/certify/.worktrees` — a directory no worktree lives under — so the filter
matches nothing, `is_dirty()` reports a dirty tree as clean, and `finish.checks()` stops warning
about uncommitted work in exactly the place uncommitted work is most likely to be lost.

**State shared between lanes must resolve to the primary worktree, or it is not shared.** Claims,
the worktree list and the run ledger are all that kind of state: a claim taken in one worktree that
another cannot see is not a claim.
"""
from __future__ import annotations

import functools
import pathlib
import subprocess

#: This file's own checkout. Correct in the primary, and the thing that is wrong in a worktree.
HERE = pathlib.Path(__file__).resolve().parent.parent


@functools.lru_cache(maxsize=1)
def primary() -> pathlib.Path:
    """The primary worktree — the one shared root every lane agrees on.

    `git worktree list --porcelain` lists the primary FIRST, from any worktree, so one call
    answers this from anywhere. Cached because it cannot change within a process and every claim
    check would otherwise shell out.

    Falls back to `HERE` when git cannot answer. That is the right failure: state in the wrong
    place is recoverable and visible, a crash on import is neither.
    """
    try:
        p = subprocess.run(["git", "-C", str(HERE), "worktree", "list", "--porcelain"],
                           capture_output=True, text=True, timeout=30)
        for line in (p.stdout or "").splitlines():
            if line.startswith("worktree "):
                return pathlib.Path(line[len("worktree "):].strip())
    except Exception:                                              # noqa: BLE001
        pass
    return HERE


def in_worktree() -> bool:
    """True when this code is running from a linked worktree rather than the primary.

    Worth being able to ask directly: several bugs in this repo have been "correct in the primary,
    silently wrong elsewhere", and that is a question the code should be able to pose about itself.
    """
    try:
        return primary().resolve() != HERE.resolve()
    except OSError:
        return False


def data() -> pathlib.Path:
    """The shared `.data/` root. Everything under it is estate-wide state, not per-worktree."""
    return primary() / ".data"
