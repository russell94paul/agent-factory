"""Which lanes have a LIVE agent session right now — the fact claims alone cannot tell you.

A claim says "someone intends to work this lane". It does not say a process is running, and on
2026-08-22 that gap opened for real: `finish()` released control-plane's claim while its session
was still alive (idle, but alive), a relaunch saw a free lane and started a second agent — and for
a while there were **three control-plane sessions sharing one worktree and one branch**. That is
precisely the shared-checkout arrangement the whole lane model exists to avoid, recreated from the
inside by the tool written to close lanes safely.

Nothing collided, because two of the three were idle. That is luck, not a control.

The instrument is Claude Code's own session registry: `~/.claude/sessions/<pid>.json`, which
carries `cwd`, `pid` and `status`, and is written by every session. A file whose pid is no longer
running is stale — the file outlives the process, so **liveness must be checked against the process
table, not against the file's existence.** Getting that backwards would report every historical
session as live and refuse every launch.
"""
from __future__ import annotations

import json
import os
import pathlib
import subprocess
from typing import Dict, List, Optional

REGISTRY = pathlib.Path.home() / ".claude" / "sessions"


def _running_pids() -> Optional[set]:
    """Live claude pids, or None when we could not look.

    None is NOT an empty set. "I cannot see the process table" and "nothing is running" are
    different verdicts, and collapsing them would let a guard silently pass.
    """
    try:
        if os.name == "nt":
            out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq claude.exe", "/FO", "CSV", "/NH"],
                                 capture_output=True, text=True, timeout=8).stdout
            pids = set()
            for line in out.splitlines():
                parts = [p.strip('" ') for p in line.split('","')]
                if len(parts) > 1 and parts[1].isdigit():
                    pids.add(int(parts[1]))
            return pids
        out = subprocess.run(["pgrep", "-f", "claude"], capture_output=True, text=True,
                             timeout=8).stdout
        return {int(x) for x in out.split() if x.isdigit()}
    except Exception:                                              # noqa: BLE001
        return None


def live_by_lane() -> Dict[str, List[dict]]:
    """lane id -> live sessions in that lane's worktree. Empty dict if the registry is absent."""
    out: Dict[str, List[dict]] = {}
    if not REGISTRY.is_dir():
        return out
    alive = _running_pids()
    for f in REGISTRY.glob("*.json"):
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except Exception:                                          # noqa: BLE001
            continue
        cwd = str(d.get("cwd", ""))
        parts = cwd.replace("\\", "/").split("/")
        if ".worktrees" not in parts:
            continue
        lane = parts[parts.index(".worktrees") + 1] if parts.index(".worktrees") + 1 < len(parts) else None
        if not lane:
            continue
        pid = d.get("pid")
        if alive is not None and pid not in alive:
            continue                                               # stale file, process gone
        out.setdefault(lane, []).append(
            {"pid": pid, "status": d.get("status"), "cwd": cwd, "unverified": alive is None})
    return out


def live(lane: str) -> List[dict]:
    return live_by_lane().get(lane, [])


def duplicates() -> Dict[str, List[dict]]:
    """Lanes running MORE THAN ONE session — two agents in one worktree, on one branch."""
    return {k: v for k, v in live_by_lane().items() if len(v) > 1}
