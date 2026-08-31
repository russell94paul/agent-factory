#!/usr/bin/env python3
"""Deliver other lanes' traffic INTO a lane's context, without it having to remember to look.

A channel nobody reads is decoration — the defect this repo keeps meeting. Asking the agent to
poll `factory.bus` at checkpoints would be exactly that: it works right up until the session that
does not bother, which is the session that most needed telling.

So delivery is a hook. It fires on tool use, and when another lane has posted something unread it
returns the traffic as `additionalContext`, which Claude Code injects into the model's context.
The cursor advances only AFTER a successful emit, so a crash re-delivers rather than drops.

Silent and inert everywhere else:
  · not in a lane worktree  -> nothing (this runs in every session, most of which are not lanes)
  · nothing unread          -> nothing (the common case; costs one directory glob)
  · any error at all        -> nothing, exit 0. A message bus must never break a session.

It NEVER returns a permission decision. It only ever adds text.
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))


def main() -> int:
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except (ValueError, OSError):
        return 0
    try:
        from factory import bus
    except Exception:                                              # noqa: BLE001
        return 0

    # ⭐ A SECOND advisory rides in this process, deliberately. A hook is a whole interpreter
    # start: measured 2026-08-31, this file costs 213ms per tool call against a bare-interpreter
    # floor of 114ms, and it fires on EVERY call in EVERY session. Registering the checkout-moved
    # checker as its own PreToolUse hook would have doubled that tax to ~415ms for a warning that
    # fires a handful of times a day. So it is imported, not registered — and no change to
    # ~/.claude/settings.json is needed to get it.
    #
    # It is independent of the bus: it speaks in the PRIMARY checkout (where sessions share an
    # index) and is silent inside a lane worktree, which is exactly where the bus speaks. The two
    # almost never fire together, and if they do, both texts go out.
    # ⚠ The import itself is the cost, so gate it on a free substring test rather than paying it
    # on every call. Measured: loading the checker unconditionally took this hook 213ms -> 273ms;
    # behind this guard a non-git command pays nothing, and only a command that mentions git pays
    # the ~60ms to load and run the checker.
    extra = None
    if "git " in ((payload.get("tool_input") or {}).get("command") or ""):
        extra = _tree_advisory(payload)

    lane = bus.lane_from_cwd(payload.get("cwd"))
    pending = []
    if lane:
        try:
            pending = bus.unread(lane)
        except Exception:                                          # noqa: BLE001
            pending = []
    if not pending and not extra:
        return 0

    body = "\n\n".join(x for x in (bus.render(pending) if pending else None, extra) if x)
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": payload.get("hook_event_name", "PreToolUse"),
            "additionalContext": body,
        },
        "suppressOutput": True,
    }))
    try:
        if pending:
            bus.mark_read(lane, pending[-1].get("at"))
    except Exception:                                              # noqa: BLE001
        pass          # better to re-deliver than to lose
    return 0


def _tree_advisory(payload):
    """Load and run the checkout-moved checker. Never raises."""
    try:
        import importlib.util as _ilu
        _spec = _ilu.spec_from_file_location(
            "git_tree_moved",
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "git-tree-moved.py"))
        _m = _ilu.module_from_spec(_spec)
        _spec.loader.exec_module(_m)
        return _m.advisory(payload)
    except Exception:                                              # noqa: BLE001
        return None           # an advisory that cannot run must never break the command


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:                                              # noqa: BLE001
        sys.exit(0)
