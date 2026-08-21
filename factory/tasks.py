"""Task store — append-only, evidence-gated.

Two rules that matter more than the schema:

1. **Append, never overwrite.** An agent that sets a field wholesale destroys what another agent
   wrote. Every mutation is an event; current state is a fold over events.
2. **A task cannot close without evidence.** ``status=done`` with an empty ``evidence`` list is
   rejected by the store, not by convention. This is the smallest possible version of the
   GreenContract discipline and it is what stops a team reporting completions with no outcomes.
"""
from __future__ import annotations

import json
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

OPEN, CLAIMED, BLOCKED, DONE, ABANDONED = "open", "claimed", "blocked", "done", "abandoned"
_TERMINAL = {DONE, ABANDONED}


class EvidenceRequired(Exception):
    """Raised when a close is attempted with no evidence attached."""


@dataclass
class Event:
    ts: float
    actor: str
    kind: str
    data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Task:
    id: str
    title: str
    owner: Optional[str] = None
    parent: Optional[str] = None
    status: str = OPEN
    blocked_by: List[str] = field(default_factory=list)
    evidence: List[Dict[str, Any]] = field(default_factory=list)
    events: List[Event] = field(default_factory=list)

    def to_dict(self) -> dict:
        d = {k: v for k, v in self.__dict__.items() if k != "events"}
        d["events"] = [e.__dict__ for e in self.events]
        return d


class TaskStore:
    """File-backed, append-only. Safe for several agents because nothing is ever overwritten."""

    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._tasks: Dict[str, Task] = {}
        if self.path.exists():
            self._load()

    # ---- persistence -----------------------------------------------------
    def _load(self) -> None:
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            self._apply(json.loads(line), replay=True)

    def _emit(self, ev: dict) -> None:
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(ev) + "\n")
        self._apply(ev)

    def _apply(self, ev: dict, replay: bool = False) -> None:
        kind, tid = ev["kind"], ev["task"]
        if kind == "create":
            self._tasks[tid] = Task(id=tid, title=ev["data"]["title"],
                                    parent=ev["data"].get("parent"))
        t = self._tasks.get(tid)
        if t is None:
            return
        if kind == "claim":
            t.owner, t.status = ev["actor"], CLAIMED
        elif kind == "block":
            t.status = BLOCKED
            t.blocked_by.append(ev["data"]["by"])          # append, never replace
        elif kind == "unblock":
            t.blocked_by = [b for b in t.blocked_by if b != ev["data"]["by"]]
            t.status = CLAIMED if t.owner else OPEN
        elif kind == "evidence":
            t.evidence.append(ev["data"])                   # append, never replace
        elif kind == "close":
            t.status = ev["data"]["status"]
        elif kind == "note":
            pass
        t.events.append(Event(ev["ts"], ev["actor"], kind, ev.get("data", {})))

    # ---- api -------------------------------------------------------------
    def create(self, title: str, actor: str = "human", parent: str | None = None) -> str:
        tid = uuid.uuid4().hex[:8]
        self._emit({"ts": time.time(), "actor": actor, "kind": "create",
                    "task": tid, "data": {"title": title, "parent": parent}})
        return tid

    def claim(self, tid: str, actor: str) -> None:
        self._emit({"ts": time.time(), "actor": actor, "kind": "claim", "task": tid, "data": {}})

    def block(self, tid: str, by: str, actor: str) -> None:
        self._emit({"ts": time.time(), "actor": actor, "kind": "block",
                    "task": tid, "data": {"by": by}})

    def unblock(self, tid: str, by: str, actor: str) -> None:
        self._emit({"ts": time.time(), "actor": actor, "kind": "unblock",
                    "task": tid, "data": {"by": by}})

    def add_evidence(self, tid: str, kind: str, ref: str, actor: str,
                     basis: str = "MEASURED") -> None:
        """basis is MEASURED | DERIVED | ASSUMED — an assumed 'proof' is not a proof."""
        if basis not in {"MEASURED", "DERIVED", "ASSUMED"}:
            raise ValueError(f"basis must be MEASURED|DERIVED|ASSUMED, got {basis!r}")
        self._emit({"ts": time.time(), "actor": actor, "kind": "evidence", "task": tid,
                    "data": {"kind": kind, "ref": ref, "basis": basis}})

    def close(self, tid: str, actor: str = "system", status: str = DONE) -> None:
        """⭐ Cannot close as done without at least one MEASURED or DERIVED piece of evidence."""
        t = self._tasks[tid]
        if status == DONE:
            usable = [e for e in t.evidence if e.get("basis") in {"MEASURED", "DERIVED"}]
            if not usable:
                raise EvidenceRequired(
                    f"task {tid} cannot close as done: no MEASURED or DERIVED evidence attached "
                    f"({len(t.evidence)} assumed-only item(s))")
        self._emit({"ts": time.time(), "actor": actor, "kind": "close",
                    "task": tid, "data": {"status": status}})

    def get(self, tid: str) -> Task:
        return self._tasks[tid]

    def open_tasks(self) -> List[Task]:
        return [t for t in self._tasks.values() if t.status not in _TERMINAL]

    def all(self) -> List[Task]:
        return list(self._tasks.values())
