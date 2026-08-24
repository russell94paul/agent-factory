"""Which lanes are being worked right now, so a conflicting one can be refused.

`factory.lanes.conflicts()` says which lanes *cannot* run together. That is a static fact about
files. This is the missing dynamic half: which lane someone actually started. Without it the
conflict map is advice, and advice does not stop a second session opening the same file.

    claim("control-plane")        -> ok, recorded
    claim("judgement")            -> REFUSED: conflicts with control-plane, claimed 4m ago

⚠ **This is a convention with a staleness warning, not a lock, and the difference matters.**

A claim is a file. Nothing here can tell whether the session that wrote it is thinking, finished,
or dead — the same problem R6 names when it says *"alive ≠ working"* and recommends progress
markers over heartbeats. So:

  · a claim older than STALE_AFTER is reported as **stale**, not silently ignored, because
    "nobody released it" and "it is still running" look identical from here;
  · a stale claim still blocks, but the refusal says it is stale and how to release it — a
    control that quietly expires is one you cannot reason about;
  · `--force` exists, and using it is a decision the store records rather than a bypass it hides.

Claims live in `.data/claims/`, which is gitignored on purpose: "a session is running on this
machine" is a local fact and committing it would make every clone claim to be busy.
"""
from __future__ import annotations

import contextlib
import datetime as _dt
import json
import os
import pathlib
import re
import time
from dataclasses import dataclass
from typing import Dict, List, Optional

from . import repo as _repo

# ⚠ Shared across every worktree, so it resolves to the PRIMARY. A claim one lane takes
# that another cannot see is not a claim — and `__file__.parent.parent` gives each
# worktree its own private claim store. See factory/repo.py.
ROOT = _repo.data() / "claims"

#: A claim older than this is reported stale. Long enough that a real session working a large
#: lane is not nagged; short enough that a dead one does not block a morning.
STALE_AFTER = _dt.timedelta(hours=4)

_SAFE = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")

#: Claims on work that is NOT a lane — a reconcile run, a research pass, anything a button spawns
#: that must not be spawned twice.
#:
#: ⛔ A separate namespace rather than a new entry in `LANES`, deliberately. R14 measured that
#: `lane` is already four objects wearing one string — work package, file-conflict key, git branch,
#: directory, claim key, ledger key — and named that, not topology, as the reason the 3-lane cap
#: will not move. Registering "synthesis" as a lane to reuse `claim()` would have added a fifth
#: meaning to the most overloaded word in this codebase to save a dozen lines.
#:
#: The store and the lock are shared, because the race is identical. The conflict graph is not: a
#: task conflicts only with itself.
TASK_PREFIX = "task--"


class ClaimError(Exception):
    """The claim was refused. The message says by what, and what to do about it."""


@dataclass(frozen=True)
class Claim:
    lane: str
    since: _dt.datetime
    who: str
    note: str = ""

    @property
    def age(self) -> _dt.timedelta:
        return _dt.datetime.now(_dt.timezone.utc) - self.since

    @property
    def stale(self) -> bool:
        """The claim is OLD. It does **not** mean the session is gone — see :func:`holder`.

        These were the same thing until 2026-08-23, when three lanes claimed 29h earlier were
        reported "STALE — release it if that session is gone" while all three sessions were
        still running. Age is a clock reading; liveness is a measurement.
        """
        return self.age > STALE_AFTER

    def human_age(self) -> str:
        m = int(self.age.total_seconds() // 60)
        return f"{m}m ago" if m < 90 else f"{m // 60}h{m % 60:02d}m ago"


#: What actually holds a claim. Age cannot tell these apart, and the difference decides whether
#: releasing is housekeeping or is the act that puts a second agent into an occupied worktree.
HELD_LIVE = "HELD-LIVE"
HELD_GONE = "HELD-GONE"
HELD_UNVERIFIED = "HELD-UNVERIFIED"


def holder(lane: str):
    """(verdict, sessions) for who holds `lane` — measured against the process table.

    Three verdicts, never two. ``HELD_UNVERIFIED`` is the one that matters: a process table we
    could not read, or a session registry that is not there, is **not** evidence that nothing is
    running. Collapsing it into ``HELD_GONE`` is how a guard silently passes — the same
    distinction `sessions._running_pids` already draws by returning None rather than an empty set.

    Imported lazily: `sessions` imports nothing from this package and must stay that way, and a
    claim must still be readable on a machine where the process table cannot be probed at all.
    """
    try:
        from . import sessions as _sessions
        if not _sessions.REGISTRY.is_dir():
            return HELD_UNVERIFIED, []
        found = _sessions.live(lane)
    except Exception:                                              # noqa: BLE001
        return HELD_UNVERIFIED, []
    if any(s.get("unverified") for s in found):
        return HELD_UNVERIFIED, found
    if not found:
        return HELD_GONE, []
    return HELD_LIVE, found


def advice(lane: str) -> str:
    """The sentence a surface prints next to a claim. Never says "release it" unless measured.

    `finish()` has always consulted `sessions.live()` before releasing. This module did not, so
    the two disagreed about the same question and the one that talked to the operator was the one
    that had not looked.
    """
    verdict, found = holder(lane)
    if verdict == HELD_LIVE:
        who = ", ".join(f"{s['pid']}:{s.get('status') or '?'}" for s in found)
        return (f"session {who} is STILL RUNNING — do NOT release; a relaunch would start a "
                f"second agent in this worktree")
    if verdict == HELD_GONE:
        return "no live session found — safe to release"
    return ("liveness UNVERIFIED (process table or session registry unreadable) — do not assume "
            "the session is gone")


def _path(lane: str) -> pathlib.Path:
    if not _SAFE.match(lane or ""):
        raise ClaimError(f"{lane!r} is not a valid lane id")
    return ROOT / f"{lane}.json"


def active() -> Dict[str, Claim]:
    """Every recorded claim, stale ones included — they still block, and hiding them would make
    a blocked lane look free for reasons nobody could see."""
    out: Dict[str, Claim] = {}
    if not ROOT.is_dir():
        return out
    for f in sorted(ROOT.glob("*.json")):
        # Task claims share the store but are NOT lanes. Leaking one in here would put a phantom
        # row on the Lanes tab and make `blockers()` weigh it against the lane conflict graph,
        # where it has no meaning.
        if f.name.startswith(TASK_PREFIX):
            continue
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
            out[f.stem] = Claim(f.stem, _dt.datetime.fromisoformat(d["since"]),
                                d.get("who", "unknown"), d.get("note", ""))
        except Exception:                                          # noqa: BLE001
            # A corrupt claim blocks rather than vanishing: an unreadable claim is not an absent
            # one, the same rule the audit reader follows.
            out[f.stem] = Claim(f.stem, _dt.datetime.now(_dt.timezone.utc) - STALE_AFTER * 2,
                                "unreadable", "claim file will not parse")
    return out


def blockers(lane: str, claimed: Optional[Dict[str, Claim]] = None) -> List[Claim]:
    """Claims that forbid starting `lane` — itself if already claimed, plus any conflicting lane."""
    from .lanes import conflicts
    claimed = active() if claimed is None else claimed
    out = []
    if lane in claimed:
        out.append(claimed[lane])
    for other in conflicts().get(lane, []):
        if other in claimed:
            out.append(claimed[other])
    return out


#: How long a caller will wait for the claim lock before refusing.
_LOCK_TIMEOUT = 5.0
#: How old a lock must be before it is presumed abandoned and stolen.
#:
#: ⚠ These MUST be different numbers and abandon MUST be the larger. When both were 5.0 the steal
#: always fired first, so the wait could never expire and the refusal path was unreachable dead
#: code — a guard that cannot refuse, which is the defect this repo names most often. `claim()`
#: writes one small file, so a hold lasting longer than a minute is a crashed process, not a slow
#: one.
_LOCK_ABANDON = 60.0


@contextlib.contextmanager
def _exclusive():
    """Serialise the check-then-write in `claim()`. Required since the tracker server went threaded.

    WARNING: this used to be free and nobody noticed. `claim()` reads `blockers()` and then writes,
    with nothing in between. That was atomic only because `socketserver.TCPServer` handled one
    request at a time -- an accident of the transport, not a property of the code. Threading the
    server on 2026-08-23 removed it, and `/start/<lane>` is a GET, so a double-click or a browser
    prefetch was enough for two requests to pass the same check and both write. That is F73 (two
    agents, one worktree, one branch) re-opened at the HTTP layer.

    `O_CREAT|O_EXCL` is atomic on Windows and POSIX alike, so the lock file's own creation is the
    mutual exclusion. A lock older than the timeout is presumed abandoned and stolen -- a crashed
    holder must not wedge the board permanently, which would turn a race into a deadlock.
    """
    ROOT.mkdir(parents=True, exist_ok=True)
    lock = ROOT / ".claim.lock"
    deadline = time.monotonic() + _LOCK_TIMEOUT
    while True:
        try:
            os.close(os.open(str(lock), os.O_CREAT | os.O_EXCL | os.O_WRONLY))
            break
        # ⚠ PermissionError, not just FileExistsError. On Windows, O_CREAT|O_EXCL against a file
        # that another thread is concurrently deleting raises EACCES rather than EEXIST — so
        # catching only FileExistsError let a losing thread escape the retry loop entirely and
        # crash. Twenty racing threads reproduce it every time; two rarely do.
        except (FileExistsError, PermissionError):
            try:
                if time.time() - lock.stat().st_mtime > _LOCK_ABANDON:
                    lock.unlink()                       # abandoned by a crashed holder
                    continue
            except OSError:
                pass                                    # it vanished under us; just retry
            if time.monotonic() > deadline:
                raise ClaimError(
                    "could not acquire the claim lock -- another request is holding it. "
                    "If nothing is running, delete .data/claims/.claim.lock")
            time.sleep(0.02)
    try:
        yield
    finally:
        try:
            lock.unlink()
        except OSError:
            pass


def claim(lane: str, who: str = "", note: str = "", force: bool = False) -> Claim:
    """Record that `lane` is being worked. Refuses if a conflicting lane is claimed."""
    from .lanes import LANES
    if lane not in {l.id for l in LANES}:
        raise ClaimError(f"no lane {lane!r}")
    # The check and the write must be one indivisible step, or two callers both see "free".
    with _exclusive():
        found = blockers(lane)
        if found and not force:
            parts = []
            for c in found:
                what = "already claimed" if c.lane == lane else f"conflicts with {c.lane}"
                # The advice is measured against the process table, not read off the clock. The old
                # text said "STALE — release it if that session is gone" purely because the claim was
                # older than four hours, which on 2026-08-23 told the operator to release three claims
                # whose sessions were all still running.
                parts.append(f"{what} ({c.human_age()}"
                             + (f", {'STALE' if c.stale else 'held'}: {advice(c.lane)}")
                             + ")")
            raise ClaimError(f"cannot start {lane}: " + "; ".join(parts))
        ROOT.mkdir(parents=True, exist_ok=True)
        now = _dt.datetime.now(_dt.timezone.utc)
        payload = {"since": now.isoformat(), "who": who or os.environ.get("USERNAME", "unknown"),
                   "note": note, "forced": bool(found and force)}
        _path(lane).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return Claim(lane, now, payload["who"], note)


def release(lane: str) -> bool:
    """Drop a claim. Returns False if there was nothing to drop — not an error, because releasing
    twice is what a careful person does when unsure."""
    p = _path(lane)
    if not p.exists():
        return False
    p.unlink()
    return True


def parallel_set(passing: Optional[set] = None) -> List[str]:
    """The largest set of lanes that could run together right now, ignoring existing claims.

    Greedy over the recommendation order rather than a true maximum-independent-set: with five
    lanes the difference is nil, and a recommendation the reader can follow beats an optimum they
    cannot. Stated so nobody later mistakes it for exhaustive.
    """
    from .lanes import conflicts, recommend
    clash, chosen = conflicts(), []
    for lane, _score, _why in recommend(passing):
        if not any(other in chosen for other in clash.get(lane.id, [])):
            chosen.append(lane.id)
    return chosen


# ---------------------------------------------------------------------------------------------
# Task claims — re-entry guards for work a BUTTON spawns.
#
# The defect this closes, measured 2026-08-23: `/synthesize/start` had no guard at all, so two
# clicks opened two Claude Code sessions, each told to write `docs/research/SYNTHESIS.md`. Two
# agents writing one 76 KB document is last-write-wins — the loser's entire pass vanishes with no
# error anywhere. `/research/start` already refuses a second dispatch (ALREADY-SENT); this is the
# same refusal for work that is not a research prompt.
#
# ⚠ Liveness is measured against the PID we spawned, and gets THREE verdicts, never two. A process
# table we could not read is not evidence that nothing is running — the same distinction
# `sessions._running_pids` draws by returning None rather than an empty set, and the one `holder()`
# draws for lanes. Unverified FAILS CLOSED: it refuses, and says why, because the cost of a wrong
# refusal is a re-click and the cost of a wrong pass is a destroyed document.


def _task_path(key: str) -> pathlib.Path:
    if not _SAFE.match(key or ""):
        raise ClaimError(f"{key!r} is not a valid task key")
    return ROOT / f"{TASK_PREFIX}{key}.json"


def task_holder(key: str):
    """(verdict, payload) for whoever holds task `key`. HELD_GONE with no payload means free."""
    p = _task_path(key)
    if not p.exists():
        return HELD_GONE, None
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
    except Exception:                                              # noqa: BLE001
        # An unreadable claim is not an absent one — same rule as `active()`.
        return HELD_UNVERIFIED, {"pid": None, "note": "claim file will not parse"}
    pid = d.get("pid")
    if not pid:
        return HELD_UNVERIFIED, d
    try:
        from . import sessions as _sessions
        live = _sessions._running_pids()
    except Exception:                                              # noqa: BLE001
        live = None
    if live is None:
        return HELD_UNVERIFIED, d
    return (HELD_LIVE if int(pid) in live else HELD_GONE), d


def task_claim(key: str, pid: Optional[int] = None, who: str = "", note: str = "",
               force: bool = False) -> Claim:
    """Claim `key` for a spawned session, or refuse with a message saying what holds it.

    `pid` is recorded so the NEXT caller can measure liveness rather than read a clock. A claim
    whose session has exited is reclaimed automatically — a guard that wedges permanently after a
    crash turns a race into a deadlock, which is why `_exclusive()` steals an abandoned lock too.
    """
    with _exclusive():
        verdict, held = task_holder(key)
        if verdict != HELD_GONE and not force:
            age = ""
            try:
                since = _dt.datetime.fromisoformat((held or {}).get("since", ""))
                age = f", started {Claim(key, since, '').human_age()}"
            except Exception:                                      # noqa: BLE001
                pass
            if verdict == HELD_LIVE:
                raise ClaimError(
                    f"{key} is already running as pid {(held or {}).get('pid')}{age}. "
                    "Starting a second one would put two agents on the same file, and the loser's "
                    "work disappears without an error. Wait for it, or use force if you know it "
                    "is wedged.")
            why = ((held or {}).get("reason")
                   or ("no pid was recorded for it" if not (held or {}).get("pid")
                       else "the process table could not be read"))
            note = (held or {}).get("note")
            raise ClaimError(
                f"{key} may already be running{age} and liveness could NOT be verified — {why}. "
                + (f"It was claimed for: {note}. " if note else "")
                + "Refusing rather than guessing: not being able to look is not proof that "
                  "nothing is there.")
        ROOT.mkdir(parents=True, exist_ok=True)
        now = _dt.datetime.now(_dt.timezone.utc)
        payload = {"since": now.isoformat(), "pid": pid,
                   "who": who or os.environ.get("USERNAME", "unknown"),
                   "note": note, "forced": bool(verdict != HELD_GONE and force)}
        _task_path(key).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return Claim(key, now, payload["who"], note)


def task_release(key: str) -> bool:
    p = _task_path(key)
    if not p.exists():
        return False
    p.unlink()
    return True
