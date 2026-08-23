"""One git worktree per lane, so parallel sessions cannot collide on a shared branch.

Both research passes landed on this independently. R5 from measurement — across ~33,000
agent-generated PRs, *different-agent* PRs in flight conflicted **41.7%** of the time, and most
conflicts were **structural** (one agent deleting a file another edited) rather than line-level.
R6 recommends branch-per-lane as Observed practice. Agreement between independent passes is the
control; this is what acting on it looks like.

`factory.claims` stops two sessions taking the *same lane*. It does nothing about three sessions
committing to one branch, which is the thing that was actually measured as failing. A worktree
gives each lane its own checkout and its own branch, so merges become a deliberate step instead
of a race.

⛔ **Removal is never automatic.** A worktree can hold uncommitted work, and a lane released
because someone clicked the wrong button must not take an evening's edits with it. `release()` in
`claims` does not touch the filesystem; `remove()` here is explicit, refuses a dirty tree without
`force`, and is not wired to any button.

⚠ Windows hazard, carried from prior experience: removing a worktree through a live directory
junction can delete what the junction points at, not the link. There is no `node_modules` in this
repo so no junction is expected — but `remove()` checks the path is where it should be before
doing anything, rather than trusting the caller.
"""
from __future__ import annotations

import pathlib
import re
import subprocess
from typing import Dict, List, Optional, Tuple

from . import repo as _repo

# ⚠ The PRIMARY worktree, never `__file__.parent.parent`. Run from inside a lane worktree the
# latter resolves to that worktree, so ROOT becomes `<primary>/.worktrees/<lane>/.worktrees`,
# `existing()` matches nothing, and `is_dirty()` reports a dirty tree as clean — a gate that
# cannot refuse, feeding `finish.checks()`. Reproduced 2026-08-23; see factory/repo.py.
REPO = _repo.primary()
ROOT = REPO / ".worktrees"
BRANCH_PREFIX = "lane/"
_SAFE = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")


class WorktreeError(Exception):
    """The worktree could not be created or removed, and the message says why."""


def _git(*args: str, cwd: Optional[pathlib.Path] = None) -> Tuple[int, str]:
    r = subprocess.run(["git", *args], cwd=str(cwd or REPO), capture_output=True,
                       text=True, encoding="utf-8", errors="replace")
    return r.returncode, (r.stdout + r.stderr).strip()


def path_for(lane_id: str) -> pathlib.Path:
    if not _SAFE.match(lane_id or ""):
        raise WorktreeError(f"{lane_id!r} is not a valid lane id")
    return ROOT / lane_id


def existing() -> Dict[str, pathlib.Path]:
    """lane id -> worktree path, read from git rather than from the filesystem.

    `git worktree list` is the authority: a directory that looks like a worktree but git does not
    know about is not one, and trusting the directory is how you end up removing a stray folder
    and believing you cleaned up.
    """
    _, out = _git("worktree", "list", "--porcelain")
    found: Dict[str, pathlib.Path] = {}
    for line in out.splitlines():
        if line.startswith("worktree "):
            p = pathlib.Path(line[len("worktree "):].strip())
            try:
                rel = p.resolve().relative_to(ROOT.resolve())
            except (ValueError, OSError):
                continue
            if len(rel.parts) == 1:
                found[rel.parts[0]] = p
    return found


def ensure(lane_id: str, base: str = "HEAD") -> Tuple[pathlib.Path, str]:
    """Create the lane's worktree if absent. Returns (path, note). Idempotent."""
    p = path_for(lane_id)
    have = existing()
    if lane_id in have:
        return have[lane_id], "reused the existing worktree"
    branch = f"{BRANCH_PREFIX}{lane_id}"
    ROOT.mkdir(parents=True, exist_ok=True)
    code, out = _git("rev-parse", "--verify", branch)
    args = (["worktree", "add", str(p), branch] if code == 0
            else ["worktree", "add", "-b", branch, str(p), base])
    code, out = _git(*args)
    if code != 0:
        raise WorktreeError(f"git worktree add failed: {out.splitlines()[-1] if out else code}")
    return p, f"created worktree on branch {branch}"


def is_dirty(lane_id: str) -> bool:
    p = existing().get(lane_id)
    if p is None:
        return False
    _, out = _git("status", "--porcelain", cwd=p)
    return bool(out.strip())


def remove(lane_id: str, force: bool = False) -> str:
    """Explicit only. Refuses a worktree with uncommitted work unless forced."""
    p = existing().get(lane_id)
    if p is None:
        return f"no worktree for {lane_id}"
    if p.resolve().parent != ROOT.resolve():
        raise WorktreeError(f"{p} is not under {ROOT} — refusing to remove it")
    if is_dirty(lane_id) and not force:
        raise WorktreeError(
            f"{lane_id} has uncommitted changes. Commit them, or pass force — but read them "
            "first: this is the only copy.")
    code, out = _git("worktree", "remove", *(["--force"] if force else []), str(p))
    if code != 0:
        raise WorktreeError(f"git worktree remove failed: {out}")
    return f"removed the worktree for {lane_id} (branch {BRANCH_PREFIX}{lane_id} kept)"


def status() -> List[dict]:
    """What exists now, for the page to render. Dirty state included — an untouched worktree and
    one holding a day's work look identical otherwise."""
    out = []
    for lane_id, p in sorted(existing().items()):
        _, ahead = _git("rev-list", "--count", f"HEAD..{BRANCH_PREFIX}{lane_id}")
        out.append({"lane": lane_id, "path": str(p), "dirty": is_dirty(lane_id),
                    "commits_ahead": ahead.strip() if ahead.strip().isdigit() else "?"})
    return out
