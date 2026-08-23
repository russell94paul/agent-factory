"""The lane run ledger — because a finished lane currently leaves no trace at all.

`finish()` asserts, pushes, announces and then **deletes the claim**. That is the whole record.
Ask "which lanes have completed, what did they cost, and what went wrong in the ones that didn't"
and there is nothing to read: the claim file is gone, the bus is per-worktree (F71) and holds one
event in the entire estate, and `.data/` has no history of any kind. A lane that ran for nineteen
hours and a lane that never launched are indistinguishable an hour later.

So this module records a run, and it does two things that are easy to get wrong.

**1. The ledger lives in the PRIMARY worktree, not the calling one.** `bus.py` and `claims.py`
resolve their root as ``parent.parent/.data``, which inside a worktree is *that worktree's*
``.data``. That is exactly F70/F71 — per-worktree files that cannot see each other — and a run
ledger with one copy per lane is not a ledger. The primary worktree is whatever
``git worktree list`` names first.

**2. A lane with no record is NOT a lane that did not run.** Everything before this module existed
is unrecorded, and reporting that as "0 runs" would be the ZERO-vs-NOT-RECORDED collapse this
estate keeps paying for. So every row carries a basis:

    RECORDED       finish() wrote it at the time — the outcome is the lane's own claim
    RECONSTRUCTED  derived after the fact from git + the session transcripts
    NOT-RECORDED   the lane exists, nothing ran, or nothing survived to measure

Cost is **measured, not estimated**: ``~/.claude/projects/<slug>/<session>.jsonl`` carries a
``usage`` block on every assistant message, so tokens, cache traffic, model and wall-clock are all
recoverable per lane — retroactively, for lanes that ran before anyone thought to instrument them.
This closes `terminal-configuration.md` section 3 ("nothing currently records what a lane spent")
and section 8's open item.
"""
from __future__ import annotations

import datetime
import json
import pathlib
import subprocess
from typing import List, Optional

FINISHED, REFUSED, ABANDONED = "FINISHED", "REFUSED", "ABANDONED"
RECORDED, RECONSTRUCTED, NOT_RECORDED = "RECORDED", "RECONSTRUCTED", "NOT-RECORDED"
MEASURED = "MEASURED"

TRANSCRIPTS = pathlib.Path.home() / ".claude" / "projects"


def _primary() -> pathlib.Path:
    """The primary worktree — the one shared root every lane can agree on.

    Falls back to this file's repo root when git cannot answer, which is the right failure: a
    ledger in the wrong place is recoverable, a crash on import is not.
    """
    here = pathlib.Path(__file__).resolve().parent.parent
    try:
        p = subprocess.run(["git", "-C", str(here), "worktree", "list", "--porcelain"],
                           capture_output=True, text=True, timeout=30)
        for line in (p.stdout or "").splitlines():
            if line.startswith("worktree "):
                return pathlib.Path(line[len("worktree "):].strip())
    except Exception:                                              # noqa: BLE001
        pass
    return here


def path() -> pathlib.Path:
    return _primary() / ".data" / "runs.jsonl"


def _now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


# ---------------------------------------------------------------------------------------------
# Cost, measured from the transcripts every session already writes.

def slug(cwd) -> str:
    """A working directory -> Claude Code's project-directory name.

    ``C:\\Users\\p\\repos\\agent-factory\\.worktrees\\control-plane`` becomes
    ``C--Users-p-repos-agent-factory--worktrees-control-plane``: every one of ``: \\ / .`` becomes
    a dash, which is why ``C:\\`` yields two dashes and ``\\.worktrees`` yields two.
    """
    s = str(cwd)
    for ch in (":", "\\", "/", "."):
        s = s.replace(ch, "-")
    return s


def cost(cwd) -> dict:
    """Measured cost of every session that ran in `cwd`. Basis NOT-RECORDED when none did."""
    empty = {"basis": NOT_RECORDED, "sessions": 0, "input": 0, "output": 0,
             "cache_write": 0, "cache_read": 0, "wall_clock_s": 0, "models": []}
    d = TRANSCRIPTS / slug(cwd)
    if not d.is_dir():
        return empty
    tin = tout = cw = cr = 0
    first = last = None
    models, n = set(), 0
    for f in d.glob("*.jsonl"):
        n += 1
        try:
            text = f.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for line in text.splitlines():
            try:
                rec = json.loads(line)
            except Exception:                                      # noqa: BLE001
                continue            # a torn append must not lose the rest — bus.py's rule
            ts = rec.get("timestamp")
            if ts:
                first = ts if first is None or ts < first else first
                last = ts if last is None or ts > last else last
            msg = rec.get("message")
            if not isinstance(msg, dict):
                continue
            u = msg.get("usage") or {}
            if u:
                tin += u.get("input_tokens", 0) or 0
                tout += u.get("output_tokens", 0) or 0
                cw += u.get("cache_creation_input_tokens", 0) or 0
                cr += u.get("cache_read_input_tokens", 0) or 0
                if msg.get("model"):
                    models.add(msg["model"])
    if not n:
        return empty
    secs = 0
    if first and last:
        try:
            a = datetime.datetime.fromisoformat(first.replace("Z", "+00:00"))
            b = datetime.datetime.fromisoformat(last.replace("Z", "+00:00"))
            secs = int((b - a).total_seconds())
        except ValueError:
            secs = 0
    return {"basis": MEASURED, "sessions": n, "input": tin, "output": tout,
            "cache_write": cw, "cache_read": cr, "wall_clock_s": secs,
            "models": sorted(models)}


# ---------------------------------------------------------------------------------------------
# The ledger.

def record(lane: str, outcome: str, detail: str = "", problems: Optional[List[str]] = None,
           branch: str = "", commits: Optional[int] = None, cwd=None) -> dict:
    """Append one run. Called by `finish()` on BOTH success and refusal.

    A refusal is the row you most want later. "control-plane refused to finish: worktree dirty"
    is the issue the UI is asked to surface, and it is precisely the event that leaves no trace
    today — `NotFinished` raises, the operator fixes it or does not, and nothing remembers.
    """
    rec = {
        "at": _now(), "lane": lane, "outcome": outcome, "basis": RECORDED,
        "detail": detail, "problems": list(problems or []),
        "branch": branch, "commits": commits,
        "cost": cost(cwd) if cwd is not None else {"basis": NOT_RECORDED},
    }
    p = path()
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec) + "\n")
    return rec


def history(lane: Optional[str] = None) -> List[dict]:
    """Every recorded run, newest first. A torn line is skipped, never fatal."""
    p = path()
    if not p.is_file():
        return []
    out = []
    for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            rec = json.loads(line)
        except Exception:                                          # noqa: BLE001
            continue
        if lane is None or rec.get("lane") == lane:
            out.append(rec)
    return sorted(out, key=lambda r: r.get("at", ""), reverse=True)


def _integration_ref(cwd) -> str:
    """The branch a lane's commits are counted against — the primary worktree's checkout."""
    try:
        p = subprocess.run(["git", "-C", str(cwd), "worktree", "list", "--porcelain"],
                           capture_output=True, text=True, timeout=30)
        block = (p.stdout or "").split("\n\n")[0]
        for line in block.splitlines():
            if line.startswith("branch "):
                # NOT split("/")[-1]: the primary is on `feat/readiness-generator`, and taking the
                # last path segment yields `readiness-generator`, a ref that does not exist — so
                # rev-list fails and every lane reports `commits=None`, which reads as "no work".
                ref = line[len("branch "):].strip()
                return ref[len("refs/heads/"):] if ref.startswith("refs/heads/") else ref
    except Exception:                                              # noqa: BLE001
        pass
    return "HEAD"


def reconstruct(lane: str) -> dict:
    """What can still be known about a lane that ran before the ledger existed.

    Derived, never written: git says how much was committed, the transcripts say what it cost.
    Neither can say whether the lane *finished* — only that work happened — so `outcome` stays
    None rather than guessing FINISHED from a non-empty branch.
    """
    from . import worktrees as _wt
    cwd = _wt.path_for(lane)
    commits, branch, dirty = None, "", None
    if pathlib.Path(cwd).is_dir():
        try:
            b = subprocess.run(["git", "-C", str(cwd), "rev-parse", "--abbrev-ref", "HEAD"],
                               capture_output=True, text=True, timeout=30)
            branch = (b.stdout or "").strip()
            c = subprocess.run(["git", "-C", str(cwd), "rev-list", "--count", "HEAD",
                                "^" + _integration_ref(cwd)],
                               capture_output=True, text=True, timeout=60)
            if c.returncode == 0 and (c.stdout or "").strip().isdigit():
                commits = int(c.stdout.strip())
            s = subprocess.run(["git", "-C", str(cwd), "status", "--porcelain"],
                               capture_output=True, text=True, timeout=60)
            dirty = bool((s.stdout or "").strip())
        except Exception:                                          # noqa: BLE001
            pass
    c = cost(cwd)
    basis = RECONSTRUCTED if (commits or c["basis"] == MEASURED) else NOT_RECORDED
    return {"lane": lane, "outcome": None, "basis": basis, "branch": branch,
            "commits": commits, "dirty": dirty, "cost": c, "problems": [], "detail": ""}


def report() -> List[dict]:
    """One row per lane for the UI: the recorded run if there is one, else what can be derived."""
    from .lanes import LANES
    rows = []
    for lane in LANES:
        runs = history(lane.id)
        row = reconstruct(lane.id)
        row["title"] = lane.title
        row["runs"] = len(runs)
        if runs:
            latest = runs[0]
            row.update({"outcome": latest.get("outcome"), "basis": RECORDED,
                        "at": latest.get("at"), "problems": latest.get("problems", []),
                        "detail": latest.get("detail", "")})
            if latest.get("cost", {}).get("basis") == MEASURED:
                row["cost"] = latest["cost"]
        rows.append(row)
    return rows
