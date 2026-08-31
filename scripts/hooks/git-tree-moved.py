#!/usr/bin/env python3
"""Tell a session when the checkout moved under it, before it writes to git.

Measured 2026-08-31: the primary checkout's HEAD moved twice during one session —
`6d9e94a -> aef21e7 -> ee4bc8d`, both `pull --ff-only` of PRs merged from cloud sessions. Nothing
raced and nothing was lost, but the session had no way to know, and the operator's reasonable
reading was *"why do branches keep getting opened on that repo?"*. The answer was that they were
not: work arrived that had already been merged elsewhere.

The dangerous version of this is older and did cost something. On 2026-08-23 four sessions were
live in one checkout, one ran `git add` across a directory another was mid-edit in, and the commit
shipped a tree that **did not import**. It was never pushed, so it was contained by luck rather
than by a control. Neither session acted wrongly — which is what makes it a design problem.

⭐ **The control is one worktree per session; this hook is only the reminder.** A linked worktree
has its own HEAD and its own index, so a session working in one cannot be moved by another. This
hook therefore says nothing at all inside a worktree — the discipline is already in force there —
and speaks only in the primary checkout, which is the shared surface.

What it does, on a git command that WRITES:

  1. remembers this session's first-seen branch and HEAD for this repo;
  2. on every later write, compares — and if either moved, says so, naming both;
  3. names any other live Claude session, because a shared index is the older hazard.

Silent and inert everywhere else:
  · not a git write command  -> nothing (the overwhelmingly common case; one substring scan)
  · inside a linked worktree -> nothing (the isolation is the control, not this)
  · nothing moved            -> nothing
  · any error at all         -> nothing, exit 0

⛔ It NEVER returns a permission decision, and it must not. A hook that blocks `git commit` on a
false positive costs more than the hazard it guards: the 2026-08-23 damage was an unpushed commit,
recoverable in a minute. Refusing a legitimate commit at 3am is not. It only ever adds text.
"""
import json
import os
import subprocess
import sys
import time

#: Verbs that MUTATE git state. A read (`git log`, `git status`, `git diff`) cannot be spoiled by
#: the tree having moved, so warning about it would be noise — and a hook that cries wolf on every
#: `git status` is a hook people turn off.
_WRITE_VERBS = (
    "git add", "git commit", "git merge", "git rebase", "git reset",
    "git checkout", "git switch", "git cherry-pick", "git stash",
)


def _git(*args, cwd=None):
    """One git call, short timeout, never raises. Returns stripped stdout or None."""
    try:
        r = subprocess.run(("git",) + args, cwd=cwd, capture_output=True,
                           text=True, timeout=5)
    except Exception:                                              # noqa: BLE001
        return None
    if r.returncode != 0:
        return None
    return (r.stdout or "").strip() or None


def _is_linked_worktree(cwd):
    """True when this cwd is a linked worktree rather than the primary checkout.

    `--git-common-dir` is the shared `.git`; `--git-dir` is this worktree's own. They differ
    exactly when we are in a linked worktree, which is the isolation this hook does not need to
    warn about.
    """
    common = _git("rev-parse", "--git-common-dir", cwd=cwd)
    own = _git("rev-parse", "--git-dir", cwd=cwd)
    if not common or not own:
        return False
    return os.path.abspath(os.path.join(cwd, common)) != os.path.abspath(os.path.join(cwd, own))


def _state_path(root, session):
    return os.path.join(root, ".data", "tree-watch", f"{session}.json")


def _contention(root):
    """This repo's row from `sessions.contended_repos()`, or None.

    ⛔ **Do not invent a helper here.** The first draft of this hook called
    `sessions.live_sessions()`, which does not exist, behind a `hasattr` guard — so the branch
    would have been permanently dead and the hook would have shipped a warning it could never
    print. That is the inert-control defect, in a hook written about controls.

    `contended_repos()` is the right instrument and it already answers exactly this: it counts
    sessions against the **process table** (a registry file outlives its process, so presence is
    not liveness) and it exists specifically for the failure `collisions()` cannot see — a session
    whose cwd is one repo running `git add` in another. Its rows carry
    `attribution: NOT-MEASURABLE` on purpose; this hook must preserve that and describe a
    condition, never name a culprit.
    """
    try:
        sys.path.insert(0, root)
        from factory import sessions as _s
        target = os.path.normcase(os.path.abspath(root))
        for row in _s.contended_repos():
            if os.path.normcase(os.path.abspath(row.get("path", ""))) == target:
                return row
    except Exception:                                              # noqa: BLE001
        return None
    return None


def advisory(payload) -> "str | None":
    """The warning text for this payload, or None when there is nothing to say. Never raises.

    ⚠ The wrapper is not ceremony. `_advisory` shells out to git, imports `factory.sessions` and
    touches the filesystem — three ways to fail in a function whose whole contract is *"any error
    at all -> nothing"*. `lane-bus.py` already catches, so production was safe, but a public
    function that promises not to raise should keep that promise itself rather than relying on
    every caller to. Its own test proved it did not: `test_every_failure_path_is_swallowed`
    failed with `RuntimeError('boom')` before this existed.
    """
    try:
        return _advisory(payload)
    except Exception:                                              # noqa: BLE001
        return None


def _advisory(payload) -> "str | None":
    """The real work. See `advisory` for the no-raise guarantee that wraps it.

    ⭐ **Separated from `main()` on a measurement, not a preference.** A hook is a whole Python
    process, and on this machine that costs **213ms** for `lane-bus.py` against a bare-interpreter
    floor of **114ms** — paid on *every tool call*, in every session. Registering this as a second
    `PreToolUse` hook would have taken the per-call tax to roughly **415ms**, for a warning that
    fires a handful of times a day.

    So `lane-bus.py` imports this and calls it: one process, both jobs, no additional cost, and no
    change to `~/.claude/settings.json`. `main()` is kept so the checker can still be exercised
    standalone, which is how the cases below were proved.
    """
    cmd = ((payload.get("tool_input") or {}).get("command") or "")
    if not any(v in cmd for v in _WRITE_VERBS):
        return None

    cwd = payload.get("cwd") or os.getcwd()
    root = _git("rev-parse", "--show-toplevel", cwd=cwd)
    if not root:
        return None
    root = os.path.abspath(root)

    # The isolation is the control. Inside a worktree there is nothing to warn about.
    if _is_linked_worktree(cwd):
        return None

    branch = _git("rev-parse", "--abbrev-ref", "HEAD", cwd=root)
    head = _git("rev-parse", "--short", "HEAD", cwd=root)
    if not branch or not head:
        return None

    session = str(payload.get("session_id") or os.getpid())
    path = _state_path(root, session)
    prev = None
    try:
        with open(path, encoding="utf-8") as fh:
            prev = json.load(fh)
    except Exception:                                              # noqa: BLE001
        prev = None

    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        tmp = f"{path}.{os.getpid()}.tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump({"branch": branch, "head": head, "at": time.time()}, fh)
        os.replace(tmp, path)
    except Exception:                                              # noqa: BLE001
        pass          # a watcher that cannot write must not break the command it watched

    if not prev:
        return None      # first write of the session: a baseline, not a finding

    moved = []
    if prev.get("branch") != branch:
        moved.append(f"branch {prev.get('branch')} -> {branch}")
    if prev.get("head") != head:
        moved.append(f"HEAD {prev.get('head')} -> {head}")
    if not moved:
        return None

    lines = [
        "⚠ This checkout moved since you last wrote to git.",
        "",
        f"  repository : {root}",
    ] + [f"  {m}" for m in moved] + [
        "",
        "You are in the PRIMARY checkout, which every session on this machine shares.",
        "Re-measure before you act — `git rev-parse --abbrev-ref HEAD` — because a branch",
        "name you read earlier in this session may no longer be the one you are about to",
        "commit to.",
    ]
    row = _contention(root)
    if row and row.get("contended"):
        lines += ["",
                  f"  {row.get('sessions_with_this_cwd')} session(s) have this repo as their cwd "
                  f"({row.get('sessions_alive')} alive on this machine), and it holds "
                  f"{row.get('dirty')} uncommitted file(s).",
                  "  Which session wrote them is NOT-MEASURABLE — that is a condition, not an",
                  "  accusation. The 2026-08-23 hazard is one session `git add`-ing across a",
                  "  directory another is mid-edit in, shipping a HEAD that did not import."]
    lines += ["",
              "  If you are doing sustained work here, prefer your own worktree:",
              "    git worktree add .worktrees/<name> -b <branch>",
              "  and remove it when you merge. This hook is silent inside one."]

    return "\n".join(lines)


def main() -> int:
    """Standalone entry point, kept for exercising the checker directly.

    In normal operation nothing calls this — `lane-bus.py` imports `advisory()` so the two
    warnings share one interpreter start. See `advisory`'s docstring for the measurement.
    """
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except (ValueError, OSError):
        return 0
    body = advisory(payload)
    if not body:
        return 0
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": payload.get("hook_event_name", "PreToolUse"),
            "additionalContext": body,
        },
        "suppressOutput": True,
    }))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:                                              # noqa: BLE001
        sys.exit(0)
