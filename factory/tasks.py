"""Task store — append-only, evidence-gated.

Two rules that matter more than the schema:

1. **Append, never overwrite.** An agent that sets a field wholesale destroys what another agent
   wrote. Every mutation is an event; current state is a fold over events.
2. **A task cannot close without evidence.** ``status=done`` with an empty ``evidence`` list is
   rejected by the store, not by convention. This is the smallest possible version of the
   GreenContract discipline and it is what stops a team reporting completions with no outcomes.
3. **Evidence carries a typed class, not just a label.** Four pieces of evidence that all answer
   the same question satisfy rule 2 and prove almost nothing. ``evidence_class`` names which of
   the four questions in :mod:`factory.evidence` an artefact answers, so ``close(require=...)``
   can refuse a delivery that never proved its target or never captured a rollback.
"""
from __future__ import annotations

import json
import re
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from . import evidence as _evidence

OPEN, CLAIMED, BLOCKED, DONE, ABANDONED = "open", "claimed", "blocked", "done", "abandoned"
_TERMINAL = {DONE, ABANDONED}

#: Closed character set for a caller-chosen task id. It travels into URLs, filenames and PowerShell
#: arguments, so it is constrained once here rather than escaped correctly at every use — the same
#: reason `bus` caps a message length in one place.
_ID_OK = re.compile(r"^[A-Za-z0-9._-]{1,64}$")


class EvidenceRequired(Exception):
    """Raised when a close is attempted with no evidence attached."""


@dataclass
class Event:
    ts: float
    actor: str
    kind: str
    data: Dict[str, Any] = field(default_factory=dict)


#: Visibility is a property of the WORK, not of the surface that renders it. It travels with the
#: task through its whole lifecycle so a projection can never widen it by omission — an absent
#: value defaults to the closed one, never the open one.
PUBLIC, PRIVATE, REVIEW_REQUIRED = "PUBLIC", "PRIVATE", "REVIEW_REQUIRED"
VISIBILITIES = (PUBLIC, PRIVATE, REVIEW_REQUIRED)

#: ⭐ The default for work whose visibility was never stated. It is PRIVATE and it must stay
#: PRIVATE: a default of PUBLIC would mean every historical row — created before this field
#: existed — silently became publishable the moment the field was added.
DEFAULT_VISIBILITY = PRIVATE

# ------------------------------------------------------------------------- autonomy policy
#
# ⭐ How a piece of work is ALLOWED to start. It is a property of the work, recorded in the same
# append-only log as everything else, so "who decided this could run unattended" is answerable
# after the fact rather than being a setting somebody remembers changing.
#
#: The operator starts it. READY work waits, indefinitely, for an explicit START SYNCED.
MANUAL = "MANUAL"
#: The system MAY start it — only when every deterministic safety condition passes. See
#: `factory.work.guarded_start`. Anything unmeasured, gated, conflicted or needing approval stops
#: it, and the stop is the default rather than the exception.
GUARDED = "GUARDED"
#: Reserved. P1 implements MANUAL and GUARDED semantics; AUTO is accepted and recorded so the
#: vocabulary does not have to change later, and it currently behaves exactly as GUARDED.
#: ⛔ It is deliberately NOT "GUARDED without the guards" — an unconditional autonomous start is
#: the uncontrolled recursive execution this design refuses to build.
AUTO = "AUTO"
AUTONOMIES = (MANUAL, GUARDED, AUTO)

#: ⛔ MANUAL. Every row written before this field existed replays through the fold with this
#: value, so adding autonomy to the model cannot make anything eligible to start on its own.
DEFAULT_AUTONOMY = MANUAL

#: How a start was decided. Recorded on the `start` event so autonomy performance can be evaluated
#: later against outcomes, rather than reconstructed from timestamps and guesswork.
MANUAL_START, AUTO_START = "MANUAL_START", "AUTO_START"


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

    # ---- P1 generic-work fields ------------------------------------------------
    # All optional with closed defaults, because every row written before P1 replays through
    # the same fold and must not acquire a capability it was never granted.

    #: What the work is FOR, in the operator's words. `title` is the label; this is the intent.
    objective: str = ""
    #: The repository the work acts on. Needed before a session can be given a worktree.
    repo: str = ""
    #: PUBLIC | PRIVATE | REVIEW_REQUIRED. See DEFAULT_VISIBILITY.
    visibility: str = DEFAULT_VISIBILITY
    #: ⭐ DURABLE dependency edges — distinct from `blocked_by`, which `unblock()` deletes.
    #: A satisfied dependency must leave a trace, or a finished mission renders as unrelated
    #: tasks (the defect `switchboard._edges` works around by re-reading the event log).
    depends_on: List[str] = field(default_factory=list)
    #: Dependencies satisfied by a durable artefact rather than by another task. Kept separate
    #: so "this waits on a file that exists" can never be confused with "this waits on a task".
    depends_on_artifacts: List[Dict[str, Any]] = field(default_factory=list)
    #: The Claude session this work is being executed by, set only on a CONFIRMED live spawn.
    session_id: Optional[str] = None
    #: Declared resource claim + access, for the conflict check. `{"resource_claim":…,"access":…}`
    contract: Dict[str, Any] = field(default_factory=dict)
    #: MANUAL | GUARDED | AUTO. Defaults closed — see DEFAULT_AUTONOMY.
    autonomy: str = DEFAULT_AUTONOMY
    #: How this work was last started, if it has been. MANUAL_START | AUTO_START | None.
    start_mode: Optional[str] = None
    #: Set by `pause_autonomy`. A paused item is never eligible for a guarded start, whatever its
    #: policy says — the operator's stop outranks the policy, at all times.
    autonomy_paused: bool = False

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
        d = ev.get("data") or {}
        if kind == "create":
            self._tasks[tid] = Task(
                id=tid, title=d["title"], parent=d.get("parent"),
                objective=d.get("objective", "") or "",
                repo=d.get("repo", "") or "",
                # ⛔ `or DEFAULT_VISIBILITY` and not `d.get("visibility", DEFAULT_VISIBILITY)`:
                # a row carrying an explicit null must also fall closed.
                visibility=d.get("visibility") or DEFAULT_VISIBILITY,
                autonomy=d.get("autonomy") or DEFAULT_AUTONOMY,
                contract=dict(d.get("contract") or {}))
        t = self._tasks.get(tid)
        if t is None:
            return
        if kind == "depend":
            # Append, never replace, and idempotent — the same edge asserted twice is one edge.
            if d.get("on") and d["on"] not in t.depends_on:
                t.depends_on.append(d["on"])
        elif kind == "depend_artifact":
            t.depends_on_artifacts.append(dict(d))
        elif kind == "undepend":
            t.depends_on = [x for x in t.depends_on if x != d.get("on")]
        elif kind == "visibility":
            if d.get("to") in VISIBILITIES:
                t.visibility = d["to"]
        elif kind == "autonomy":
            if d.get("to") in AUTONOMIES:
                t.autonomy = d["to"]
        elif kind == "autonomy_pause":
            t.autonomy_paused = bool(d.get("paused", True))
        elif kind == "start":
            t.start_mode = d.get("mode") or MANUAL_START
        elif kind == "session":
            # None is meaningful: it detaches a session that is no longer live.
            t.session_id = d.get("session_id") or None
        elif kind == "meta":
            for f in ("objective", "repo", "title"):
                if d.get(f):
                    setattr(t, f, d[f])
            if d.get("contract"):
                t.contract.update(d["contract"])
        elif kind == "claim":
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
        t.events.append(Event(ev["ts"], ev["actor"], kind, d))

    # ---- api -------------------------------------------------------------
    def create(self, title: str, actor: str = "human", parent: str | None = None,
               tid: str | None = None, objective: str = "", repo: str = "",
               visibility: str | None = None, contract: Dict[str, Any] | None = None) -> str:
        """Create work. `tid` names it; omitted, it gets an opaque one.

        ⭐ **A caller-chosen id is what lets arbitrary work be operated without a manifest.**
        The opaque `uuid4[:8]` is unaddressable: an operator cannot type it, a dependency cannot
        cite it, and a mission manifest had to exist purely to map a readable label onto it. A
        stable id like `MARKETING-MODEL-FINALIZATION-01` removes that whole indirection.

        Ids are unique because the store is append-only: re-creating an existing id would replay
        as a second `create` and silently reset every field folded after the first one.
        """
        if tid is not None:
            tid = str(tid).strip()
            if not tid:
                raise ValueError("explicit task id cannot be blank")
            if not _ID_OK.match(tid):
                raise ValueError(
                    f"task id {tid!r} must be 1-64 chars of A-Z a-z 0-9 . _ - — it is used in "
                    f"URLs, filenames and shell arguments, so the character set is closed rather "
                    f"than escaped at each use")
            if tid in self._tasks:
                raise ValueError(f"task {tid!r} already exists — the store is append-only, so a "
                                 f"second create would reset the fields folded after the first")
        else:
            tid = uuid.uuid4().hex[:8]
        if visibility is not None and visibility not in VISIBILITIES:
            raise ValueError(f"visibility must be one of {VISIBILITIES}, got {visibility!r}")
        self._emit({"ts": time.time(), "actor": actor, "kind": "create", "task": tid,
                    "data": {"title": title, "parent": parent, "objective": objective,
                             "repo": repo, "visibility": visibility or DEFAULT_VISIBILITY,
                             "contract": dict(contract or {})}})
        return tid

    def depend(self, tid: str, on: str, actor: str = "human") -> None:
        """Record a DURABLE dependency edge: `tid` depends on task `on`.

        ⛔ Not `block()`. `block` is a *status* — `unblock` erases it, so a satisfied dependency
        leaves no edge behind and the graph forgets its own shape. This edge is permanent; whether
        it is *satisfied* is derived from the state of `on`, every time it is asked.
        """
        if on == tid:
            raise ValueError(f"task {tid!r} cannot depend on itself")
        if on not in self._tasks:
            raise KeyError(f"cannot depend on {on!r}: no such task in the store")
        if self._creates_cycle(tid, on):
            raise ValueError(f"{tid!r} -> {on!r} would close a dependency cycle; "
                             f"nothing in it could ever become ready")
        self._emit({"ts": time.time(), "actor": actor, "kind": "depend",
                    "task": tid, "data": {"on": on}})

    def depend_on_artifact(self, tid: str, ref: str, kind: str, actor: str = "human",
                           satisfied_when: str = "EXISTS") -> None:
        """A dependency satisfied by a durable artefact rather than by another task.

        ⭐ This exists so historical work does not have to be faked. The Marketing Model analysis
        is finished and its outputs are on disk; inventing a completed TaskStore row to stand in
        for it would put a fabricated completion record in the canonical ledger. An artefact edge
        says what is actually true — *this file must exist* — and is checked against the disk.
        """
        self._emit({"ts": time.time(), "actor": actor, "kind": "depend_artifact", "task": tid,
                    "data": {"ref": ref, "kind": kind, "satisfied_when": satisfied_when}})

    def set_autonomy(self, tid: str, to: str, actor: str = "human") -> None:
        """Set the execution policy. Recorded, so the decision has an author and a time."""
        if to not in AUTONOMIES:
            raise ValueError(f"autonomy must be one of {AUTONOMIES}, got {to!r}")
        self._emit({"ts": time.time(), "actor": actor, "kind": "autonomy",
                    "task": tid, "data": {"to": to}})

    def pause_autonomy(self, tid: str, paused: bool = True, actor: str = "human") -> None:
        """⭐ Available at ALL times, and it outranks the policy. A pause that could be refused
        because of the very state it is trying to stop would not be a pause."""
        self._emit({"ts": time.time(), "actor": actor, "kind": "autonomy_pause",
                    "task": tid, "data": {"paused": bool(paused)}})

    def record_start(self, tid: str, mode: str, actor: str = "system") -> None:
        """Record HOW a start was decided — MANUAL_START or AUTO_START.

        Separate from `claim`, which records that work began. This records who decided it should:
        the pair is what makes autonomy performance measurable later instead of inferred.
        """
        if mode not in (MANUAL_START, AUTO_START):
            raise ValueError(f"start mode must be {MANUAL_START} or {AUTO_START}, got {mode!r}")
        self._emit({"ts": time.time(), "actor": actor, "kind": "start",
                    "task": tid, "data": {"mode": mode}})

    def set_visibility(self, tid: str, to: str, actor: str = "human") -> None:
        if to not in VISIBILITIES:
            raise ValueError(f"visibility must be one of {VISIBILITIES}, got {to!r}")
        self._emit({"ts": time.time(), "actor": actor, "kind": "visibility",
                    "task": tid, "data": {"to": to}})

    def attach_session(self, tid: str, session_id: str | None, actor: str = "system") -> None:
        """Associate work with a live session — called only AFTER a spawn is confirmed."""
        self._emit({"ts": time.time(), "actor": actor, "kind": "session",
                    "task": tid, "data": {"session_id": session_id}})

    def set_meta(self, tid: str, actor: str = "human", **fields) -> None:
        """Amend objective / repo / title / contract. Append-only: the old value stays in the log."""
        allowed = {k: v for k, v in fields.items()
                   if k in {"objective", "repo", "title", "contract"} and v}
        if not allowed:
            return
        self._emit({"ts": time.time(), "actor": actor, "kind": "meta",
                    "task": tid, "data": allowed})

    def _creates_cycle(self, tid: str, on: str) -> bool:
        """Would `tid -> on` make `tid` reachable from `on`? Iterative, so a deep chain cannot
        blow the stack, and it tolerates edges to ids that are not in the store."""
        seen, stack = set(), [on]
        while stack:
            cur = stack.pop()
            if cur == tid:
                return True
            if cur in seen:
                continue
            seen.add(cur)
            t = self._tasks.get(cur)
            if t is not None:
                stack.extend(t.depends_on)
        return False

    def claim(self, tid: str, actor: str) -> None:
        self._emit({"ts": time.time(), "actor": actor, "kind": "claim", "task": tid, "data": {}})

    def block(self, tid: str, by: str, actor: str) -> None:
        self._emit({"ts": time.time(), "actor": actor, "kind": "block",
                    "task": tid, "data": {"by": by}})

    def unblock(self, tid: str, by: str, actor: str) -> None:
        self._emit({"ts": time.time(), "actor": actor, "kind": "unblock",
                    "task": tid, "data": {"by": by}})

    def add_evidence(self, tid: str, kind: str, ref: str, actor: str,
                     basis: str = "MEASURED", evidence_class: str | None = None) -> None:
        """basis is MEASURED | DERIVED | ASSUMED — an assumed 'proof' is not a proof.

        `kind` stays free text: it is the human label for *this* artefact ("shadow diff",
        "screenshot"). `evidence_class` is the typed one — which of the four questions in
        :mod:`factory.evidence` this artefact answers — and it is **validated when given**.

        ⚠ It is optional, and an unclassified row counts toward **nothing**. That is deliberate
        rather than lenient: making it mandatory would reclassify every historical row by
        guesswork, and a class inferred from a free-text label is exactly the "inferred from
        matching values" move the TARGET class exists to forbid.
        """
        if basis not in {"MEASURED", "DERIVED", "ASSUMED"}:
            raise ValueError(f"basis must be MEASURED|DERIVED|ASSUMED, got {basis!r}")
        data = {"kind": kind, "ref": ref, "basis": basis}
        if evidence_class is not None:
            data["evidence_class"] = _evidence.check(evidence_class)
        self._emit({"ts": time.time(), "actor": actor, "kind": "evidence", "task": tid,
                    "data": data})

    def coverage(self, tid: str, required=_evidence.DELIVERY):
        """Which of the required evidence classes this task's rows satisfy. See `factory.evidence`."""
        return _evidence.coverage(self._tasks[tid].evidence, required)

    def close(self, tid: str, actor: str = "system", status: str = DONE,
              require=None) -> None:
        """⭐ Cannot close as done without at least one MEASURED or DERIVED piece of evidence.

        `require` raises the bar from *"some evidence"* to *"these named classes"* — pass
        `factory.evidence.DELIVERY` for the four-artefact gate. It is opt-in per call because
        what a piece of work must prove is a property of the work, not of the store: an analysis
        has nothing to roll back, and forcing a ROLLBACK row would teach people to file empty
        ones. `evidence.ANALYSIS` exists so the reduced set is a declared policy rather than a
        quiet omission.
        """
        t = self._tasks[tid]
        if status == DONE:
            usable = [e for e in t.evidence if e.get("basis") in {"MEASURED", "DERIVED"}]
            if not usable:
                raise EvidenceRequired(
                    f"task {tid} cannot close as done: no MEASURED or DERIVED evidence attached "
                    f"({len(t.evidence)} assumed-only item(s))")
            if require:
                cov = _evidence.coverage(t.evidence, require)
                if not cov.complete:
                    raise EvidenceRequired(
                        f"task {tid} cannot close as done — required evidence is not "
                        f"satisfied:\n{_evidence.render(cov)}")
        self._emit({"ts": time.time(), "actor": actor, "kind": "close",
                    "task": tid, "data": {"status": status}})

    def get(self, tid: str) -> Task:
        return self._tasks[tid]

    def open_tasks(self) -> List[Task]:
        return [t for t in self._tasks.values() if t.status not in _TERMINAL]

    def all(self) -> List[Task]:
        return list(self._tasks.values())
