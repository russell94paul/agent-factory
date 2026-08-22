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

import datetime as _dt
import json
import os
import pathlib
import re
from dataclasses import dataclass
from typing import Dict, List, Optional

ROOT = pathlib.Path(__file__).resolve().parent.parent / ".data" / "claims"

#: A claim older than this is reported stale. Long enough that a real session working a large
#: lane is not nagged; short enough that a dead one does not block a morning.
STALE_AFTER = _dt.timedelta(hours=4)

_SAFE = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")


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
        return self.age > STALE_AFTER

    def human_age(self) -> str:
        m = int(self.age.total_seconds() // 60)
        return f"{m}m ago" if m < 90 else f"{m // 60}h{m % 60:02d}m ago"


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


def claim(lane: str, who: str = "", note: str = "", force: bool = False) -> Claim:
    """Record that `lane` is being worked. Refuses if a conflicting lane is claimed."""
    from .lanes import LANES
    if lane not in {l.id for l in LANES}:
        raise ClaimError(f"no lane {lane!r}")
    found = blockers(lane)
    if found and not force:
        parts = []
        for c in found:
            what = "already claimed" if c.lane == lane else f"conflicts with {c.lane}"
            parts.append(f"{what} ({c.human_age()}"
                         + (", STALE — release it if that session is gone" if c.stale else "")
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
