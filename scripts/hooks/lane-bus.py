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

    lane = bus.lane_from_cwd(payload.get("cwd"))
    if not lane:
        return 0
    try:
        pending = bus.unread(lane)
    except Exception:                                              # noqa: BLE001
        return 0
    if not pending:
        return 0

    body = bus.render(pending)
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": payload.get("hook_event_name", "PreToolUse"),
            "additionalContext": body,
        },
        "suppressOutput": True,
    }))
    try:
        bus.mark_read(lane, pending[-1].get("at"))
    except Exception:                                              # noqa: BLE001
        pass          # better to re-deliver than to lose
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:                                              # noqa: BLE001
        sys.exit(0)
