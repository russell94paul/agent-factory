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


# =================================================================================================
# The inventory — every session on this machine, joined to what it is doing and what it wants.
#
# `live_by_lane()` above answers one narrow question (may this lane be launched) and answers it
# well. It cannot answer the question that actually confuses an operator at 4am: **which of these
# twelve terminals is which, which are alive, and which are waiting on me.**
#
# Three facts shaped this.
#
# **1. The name is not the identity, and neither is the directory.** On 2026-08-23 five live
# sessions were all called `boot pre-flight verification` — the name of the boot prompt that
# spawned them, not of the work. `CLAUDE_CODE_SESSION_NAME` is read once at startup, so a running
# session cannot be renamed and no fix reaches those five.
#
# The first version of this module said identity could therefore be derived from `cwd`. **That was
# wrong and the first run said so: six sessions were sharing one directory** (the launchpad repo
# root), so cwd disambiguates lanes and nothing else. What actually distinguishes two terminals in
# one directory is *what was asked of them*, so identity is derived from the session's own opening
# prompt, read from its transcript. That is the line an operator recognises.
#
# **2. Alive, visible and attachable are three different things.** A terminal died that morning
# while its agent kept working and kept writing to its transcript. Anything that reports two states
# lies about that session. Four are reported, plus one for "the instrument could not look".
#
# **3. `jobs/<id>/state.json` carries a `needs` field, in English, that nothing reads.** Four jobs
# were blocked on written questions while the operator had no surface showing them. That is not
# alarm fatigue, it is alarm absence, and it is the single most valuable thing in this join.
# =================================================================================================

JOBS = pathlib.Path.home() / ".claude" / "jobs"
TRANSCRIPTS = pathlib.Path.home() / ".claude" / "projects"

#: A session whose process is running and which owns a terminal.
RUNNING_ATTACHED = "RUNNING-ATTACHED"
#: Running, but with no terminal of its own — a background agent. Reach it with `claude agents`;
#: `claude --resume` will refuse, and forcing it starts a SECOND process on one session id.
RUNNING_ORPHANED = "RUNNING-ORPHANED"
#: Process gone, transcript on disk. `claude --resume <id>` from its cwd brings it back.
EXITED_RESUMABLE = "EXITED-RESUMABLE"
#: Process gone and no transcript found. Nothing to resume.
EXITED_GONE = "EXITED-GONE"
#: The process table could not be read. NOT the same as "nothing is running".
UNKNOWN = "UNKNOWN-INSTRUMENT-BLIND"


def _slug(cwd) -> str:
    s = str(cwd)
    for ch in (":", "\\", "/", "."):
        s = s.replace(ch, "-")
    return s


def _identity(cwd: str) -> dict:
    """What this session IS, derived from where it is running rather than what it calls itself."""
    parts = str(cwd).replace("\\", "/").rstrip("/").split("/")
    lane = None
    if ".worktrees" in parts:
        i = parts.index(".worktrees")
        if i + 1 < len(parts):
            lane = parts[i + 1]
    repo = None
    if "repos" in parts:
        i = parts.index("repos")
        if i + 1 < len(parts):
            repo = parts[i + 1]
    where = "/".join(parts[-2:]) if len(parts) >= 2 else str(cwd)
    return {"repo": repo, "lane": lane, "where": where}


def _job(job_id) -> dict:
    """state / tempo / tokens / detail / needs for a session, or {} when it has no job record."""
    if not job_id:
        return {}
    f = JOBS / str(job_id) / "state.json"
    if not f.is_file():
        return {}
    try:
        return json.loads(f.read_text(encoding="utf-8", errors="replace"))
    except Exception:                                              # noqa: BLE001
        return {}


def _topic(cwd: str, session_id: str, limit: int = 90) -> str:
    """The session's opening prompt — the only thing that tells two terminals in one directory apart.

    Read from the transcript rather than the registry because the registry's `name` is inherited
    from whatever spawned the session and is routinely duplicated. Cheap: stops at the first real
    user turn instead of parsing the file. Hook output and system reminders are skipped — they are
    identical across sessions and would reintroduce the very collision this exists to break.
    """
    f = TRANSCRIPTS / _slug(cwd) / f"{session_id}.jsonl"
    if not f.is_file():
        return ""
    try:
        with f.open(encoding="utf-8", errors="replace") as fh:
            for _ in range(400):
                line = fh.readline()
                if not line:
                    break
                try:
                    d = json.loads(line)
                except Exception:                                  # noqa: BLE001
                    continue
                if d.get("type") != "user":
                    continue
                c = (d.get("message") or {}).get("content")
                if isinstance(c, list):
                    c = " ".join(x.get("text", "") for x in c
                                 if isinstance(x, dict) and x.get("type") == "text")
                if not isinstance(c, str):
                    continue
                c = c.strip()
                if not c or c.startswith("<") or c.startswith("Caveat:"):
                    continue
                c = " ".join(c.split())
                return c[:limit] + ("…" if len(c) > limit else "")
    except OSError:
        return ""
    return ""


def _has_transcript(cwd: str, session_id: str) -> bool:
    if not cwd or not session_id:
        return False
    return (TRANSCRIPTS / _slug(cwd) / f"{session_id}.jsonl").is_file()


def inventory() -> List[dict]:
    """Every registered session, richest-first: blocked before busy, busy before idle, dead last.

    Reads three sources and says which one each fact came from, because they disagree: the session
    registry is written by the session, the job state is written by the agent, and the process
    table is the only one that knows whether anything is still running.
    """
    out: List[dict] = []
    if not REGISTRY.is_dir():
        return out
    alive = _running_pids()
    for f in sorted(REGISTRY.glob("*.json")):
        try:
            d = json.loads(f.read_text(encoding="utf-8", errors="replace"))
        except Exception:                                          # noqa: BLE001
            continue
        pid, cwd = d.get("pid"), str(d.get("cwd", ""))
        sid = d.get("sessionId", "")
        job = _job(d.get("jobId"))

        if alive is None:
            state = UNKNOWN
        elif pid in alive:
            state = RUNNING_ORPHANED if d.get("kind") == "bg" else RUNNING_ATTACHED
        else:
            state = EXITED_RESUMABLE if _has_transcript(cwd, sid) else EXITED_GONE

        ident = _identity(cwd)
        out.append({
            "pid": pid, "session_id": sid, "cwd": cwd, "state": state,
            "name": d.get("name") or "",           # a LABEL. Not unique, not trusted — see header.
            "status": d.get("status"), "kind": d.get("kind"), "agent": d.get("agent"),
            "job_id": d.get("jobId"),
            "repo": ident["repo"], "lane": ident["lane"], "where": ident["where"],
            "topic": _topic(cwd, sid),
            "job_state": job.get("state"), "tempo": job.get("tempo"),
            "tokens": job.get("tokens"),
            "detail": job.get("detail") or "",
            "needs": job.get("needs") or "",       # the question nobody was reading
            "in_flight": (job.get("inFlight") or {}).get("tasks"),
        })

    rank = {RUNNING_ATTACHED: 1, RUNNING_ORPHANED: 0, UNKNOWN: 2,
            EXITED_RESUMABLE: 3, EXITED_GONE: 4}
    # Blocked first, always. A session with a written question outranks a busy one: the busy one is
    # making progress and the blocked one is not, and only one of them can be unblocked by a human.
    out.sort(key=lambda r: (0 if r["needs"] else 1, rank.get(r["state"], 9),
                            r["repo"] or "", r["where"]))
    return out


def blocked() -> List[dict]:
    """Sessions with a written question and nobody reading it."""
    return [r for r in inventory() if r["needs"]]


def collisions() -> Dict[str, List[dict]]:
    """Working directories holding MORE THAN ONE running session — two agents, one branch.

    Broader than `duplicates()`, which only sees lane worktrees. This catches any shared cwd,
    including the case that actually happened: three sessions in one control-plane worktree.
    """
    by_cwd: Dict[str, List[dict]] = {}
    for r in inventory():
        if r["state"] in (RUNNING_ATTACHED, RUNNING_ORPHANED):
            by_cwd.setdefault(r["cwd"], []).append(r)
    return {k: v for k, v in by_cwd.items() if len(v) > 1}
