"""The autonomy planner — the seam where policy stops deciding and starts acting.

    python -m factory.autonomy status
    python -m factory.autonomy plan   --run <id>          # explain, start nothing
    python -m factory.autonomy pause  --run <id>
    python -m factory.autonomy resume --run <id>

⭐ **What was missing, precisely.** `work.guarded_start` has always answered "may the system start
this without a human?", and P1's own inspector said so in as many words: *"GUARDED decides; it
does not act."* Every other part existed — readiness derivation, claims, conflicts, the recorded
start mode, pause. The only absent piece was something that reads the decision and pulls the
trigger. This module is that piece, and it is deliberately two halves:

    plan()   pure. Reads a projection, returns an explained decision per candidate. No side
             effects, no spawning, no imports of the start mechanism. Testable on a tmp store.
    the pump lives in `scripts/local_tracker.py`, because that is where the existing start
             mechanism (`start_synced`) lives. It calls `plan()` and then that.

Keeping them apart is not tidiness. A planner that can spawn is a planner whose refusals cannot
be tested without spawning, and the refusals are the part that matters.

⛔ **Two safety properties, and they are not negotiable.**

**The planner never starts anything `work.guarded_start` refuses.** It calls that function; it
does not reimplement, relax or shortcut it. `guarded_start` is the single home of the human-gate,
publication-boundary, unresolved-conflict, unmeasured-condition and operator-pause stops. A second
opinion about safety is a second safety model, and the estate has already been burned by a check
that passed at one layer while the real condition lived at another.

⚠ **This is a deliberate deviation from the deadline pack**, which specified
`AUTO: require_guarded_start_allowed: false`. That would have made AUTO the one mode able to cross
the publication boundary and skip an unmeasured condition — i.e. it would have moved the safety
model *into the run mode*, where it is set by whoever clicked last. Instead the two axes are kept
orthogonal:

    per-work `autonomy` (MANUAL/GUARDED/AUTO)  decides WHICH work is eligible
    the run's `mode`    (MANUAL/GUARDED/AUTO)  decides WHETHER the pump acts, and keeps acting

MANUAL work therefore never auto-starts under any run mode, which is what the brief asked for
anyway. AUTO buys continuation without a tap; it does not buy fewer refusals.

**There is no timer and no loop.** No `threading.Timer`, no `sched.scheduler`, no background
thread, no `while True` around a start. The pump is called from exactly four places, all of them
either an operator action or a page the operator is looking at:

    1. an explicit RUN DAG / RUN CRITICAL PATH POST
    2. after `/switchboard/resolve` records an APPROVE or REJECT      <- this is auto-continuation
    3. on RESUME
    4. once per Switchboard render, while an active unpaused run exists

(4) is the completion wakeup, and it is honest about what it is: there is no in-process completion
event in this repo, so continuation happens on the next render rather than instantaneously. A
background poller would have been faster and would also have been the "uncontrolled recursive
autonomous execution" the brief forbids. The UI states the actual latency rather than implying
none.

⛔ **A failed start is not retried.** `start_synced` failing leaves the work READY, so the next
pump would try again, and again — the accidental infinite retry that this estate has already seen
in a prior system. So the pump records the failure on the mandate and the planner refuses that id
until a human clears it (`--clear-failure`). One attempt, visible, no classifier, no budget
arithmetic. Classified transient retry is a post-deadline design.
"""
from __future__ import annotations

import argparse
import dataclasses
import datetime as _dt
import json
import pathlib
import sys
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from . import repo as _repo
from . import tasks as _tasks
from . import work as _work

# ------------------------------------------------------------------------------ vocabulary

#: What the planner decided about one candidate. Every one carries a reason; a verdict without
#: a reason is a scalar score in disguise, and the pack is explicit that an unvalidated
#: scheduling score should not be invented.
START = "START"
WAIT = "WAIT"
BLOCKED = "BLOCKED"
HUMAN_GATE = "HUMAN_GATE"
PAUSED = "PAUSED"
VERDICTS = (START, WAIT, BLOCKED, HUMAN_GATE, PAUSED)

#: Run selection. DAG starts everything eligible in the run; CRITICAL_PATH starts only eligible
#: ancestors of the target milestone. Neither deletes or rewrites anything outside its selection —
#: unselected work is left alone, not dropped. Automatic scope degradation is deliberately absent.
DAG, CRITICAL_PATH = "DAG", "CRITICAL_PATH"
RUN_MODES = (DAG, CRITICAL_PATH)

#: Reasons that mean "a person decides", so the UI can separate a queue from an inbox. Matched
#: against `guarded_start`'s own text rather than re-deriving the condition, so the two can never
#: disagree about what a human gate is.
_HUMAN_MARKERS = ("a human decides", "publication boundary", "requires_approval",
                  "approval_required", "security_review", "publication_gate")

DEFAULT_MAX_PARALLEL = 3


def runs_dir() -> pathlib.Path:
    """Mandates live under the shared data root, like claims and the task store.

    See `factory/repo.py`: state resolved per-worktree is not shared, and a run created in one
    lane would be invisible to every other one.
    """
    return _repo.data() / "runs"


# ------------------------------------------------------------------------------ the mandate


@dataclass
class Mandate:
    """Scheduler context: authority, deadline, concurrency, selection. **Not** a success contract.

    ⭐ Kept separate from the falsifiable contracts on tasks and evals on purpose. A deadline
    changes what is urgent; it does not change what PASS means. Folding the two together is how a
    clock ends up quietly redefining done — and the pack, the repo's own GreenContract and the
    Agent Army evidence model all draw the same line.

    ⛔ This is not a parallel source of truth. It holds only what the operator chose. Everything
    derived — what is READY, running, blocked, eligible — is read from `work.project()` every
    time it is asked. There is no cached state here to go stale, which is why there is no
    `PROJECT_STATE.yaml` and no `PROGRESS.yaml`.
    """
    run_id: str
    mission: str = ""
    target: str = ""
    mode: str = _tasks.GUARDED
    run_mode: str = DAG
    max_parallel: int = DEFAULT_MAX_PARALLEL
    deadline: str = ""
    paused: bool = False
    actor: str = "operator"
    created: float = field(default_factory=time.time)
    #: work_id -> why its last start failed. The planner refuses these; a human clears them.
    failed: Dict[str, str] = field(default_factory=dict)

    @property
    def path(self) -> pathlib.Path:
        return runs_dir() / f"{self.run_id}.json"

    @property
    def deadline_at(self) -> Optional[_dt.datetime]:
        if not self.deadline:
            return None
        try:
            return _dt.datetime.fromisoformat(self.deadline)
        except ValueError:
            return None

    def remaining(self) -> Optional[_dt.timedelta]:
        d = self.deadline_at
        if d is None:
            return None
        now = _dt.datetime.now(d.tzinfo) if d.tzinfo else _dt.datetime.now()
        return d - now

    def save(self) -> pathlib.Path:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(dataclasses.asdict(self), indent=1), encoding="utf-8")
        return self.path


def load_mandate(run_id: str) -> Optional[Mandate]:
    p = runs_dir() / f"{(run_id or '').strip()}.json"
    if not p.is_file():
        return None
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    known = {f.name for f in dataclasses.fields(Mandate)}
    return Mandate(**{k: v for k, v in d.items() if k in known})


def mandates() -> List[Mandate]:
    """Every run on disk, newest first."""
    d = runs_dir()
    if not d.is_dir():
        return []
    out = [m for m in (load_mandate(p.stem) for p in d.glob("*.json")) if m is not None]
    return sorted(out, key=lambda m: m.created, reverse=True)


def active() -> List[Mandate]:
    """Runs that would act if pumped: not paused, and not in plan-only MANUAL mode."""
    return [m for m in mandates() if not m.paused and m.mode != _tasks.MANUAL]


# ------------------------------------------------------------------------------ graph


def ancestors(target: str, rows: Dict[str, "_work.Work"]) -> set:
    """Every piece of work `target` transitively depends on. Iterative; tolerates unknown ids.

    ⛔ Computed over the **task** dependency graph, never over `board.DEPENDS`. Those are two
    different graphs at two different scales — one is platform readiness gates, the other is the
    work a mission is made of — and `switchboard.state()` labels its own answer
    `critical_path_basis: DEPENDENCY` for exactly this reason. Treating them as one graph would
    aim RUN CRITICAL PATH at the wrong nodes.
    """
    seen: set = set()
    stack = list((rows[target].depends_on if target in rows else []))
    while stack:
        cur = stack.pop()
        if cur in seen:
            continue
        seen.add(cur)
        w = rows.get(cur)
        if w is not None:
            stack.extend(w.depends_on)
    return seen


def members(m: Mandate, rows: Dict[str, "_work.Work"]) -> List["_work.Work"]:
    """The work this run may touch. Selection only — nothing outside it is altered or dropped."""
    if m.run_mode == CRITICAL_PATH:
        if not m.target:
            return []
        want = ancestors(m.target, rows) | {m.target}
        sel = [rows[i] for i in want if i in rows]
    elif m.mission:
        sel = [w for w in rows.values() if w.parent == m.mission]
    else:
        sel = list(rows.values())
    # The mission's own container row is not runnable work.
    sel = [w for w in sel if (w.contract or {}).get("kind") != "mission"]
    if m.run_mode == CRITICAL_PATH and m.mission:
        sel = [w for w in sel if w.parent == m.mission or w.id == m.target]
    return sorted(sel, key=lambda w: w.id)


# ------------------------------------------------------------------------------ the planner


@dataclass
class Decision:
    work_id: str
    verdict: str
    reason: str

    def __str__(self) -> str:                                      # pragma: no cover
        return f"{self.verdict:11} {self.work_id:38} {self.reason}"


@dataclass
class Plan:
    run_id: str
    decisions: List[Decision] = field(default_factory=list)
    running: int = 0
    capacity: int = 0
    note: str = ""

    @property
    def starts(self) -> List[str]:
        return [d.work_id for d in self.decisions if d.verdict == START]

    def by_verdict(self, v: str) -> List[Decision]:
        return [d for d in self.decisions if d.verdict == v]


def _human(reasons: List[str]) -> bool:
    joined = " ".join(reasons).lower()
    return any(mk.lower() in joined for mk in _HUMAN_MARKERS)


def plan(m: Mandate, rows: Optional[Dict[str, "_work.Work"]] = None,
         running: Optional[int] = None) -> Plan:
    """Decide, with a reason per candidate. **Pure** — reads a projection, returns decisions.

    The order of the tests is the design, and it mirrors `work.guarded_start`: every condition is
    a stop rather than a score, and the function only reaches START when it has run out of
    reasons to refuse.

      operator pause -> plan-only mode -> terminal -> unanswered question -> explicit hold
      -> not READY -> guarded-start refusal -> a previous failed start -> concurrency
      -> a writer already starting in this same batch -> START
    """
    if rows is None:
        rows = {w.id: w for w in _work.project()}

    # Concurrency is a property of the MACHINE, not of the run: every start opens a real terminal
    # running a real agent, so two runs cannot each have their own three.
    live = running if running is not None else sum(
        1 for w in rows.values() if w.state == _work.RUNNING)
    p = Plan(run_id=m.run_id, running=live, capacity=max(0, m.max_parallel - live))

    cands = members(m, rows)
    if not cands:
        p.note = (f"the run selects no work — "
                  + (f"target {m.target!r} is not in the store" if m.run_mode == CRITICAL_PATH
                     else f"no work has parent {m.mission!r}"))
        return p

    if m.paused:
        p.note = "the operator has PAUSED this run; running work may finish, nothing new starts"
        p.decisions = [Decision(w.id, PAUSED, "run is paused by the operator")
                       for w in cands if w.state not in (_work.DONE, _work.ABANDONED)]
        return p

    if m.mode == _tasks.MANUAL:
        p.note = ("run mode is MANUAL — the planner explains what it would do and starts nothing. "
                  "This is not a degraded AUTO; it is the plan-only mode.")
        for w in cands:
            if w.state in (_work.DONE, _work.ABANDONED):
                continue
            p.decisions.append(Decision(w.id, WAIT, "run mode is MANUAL — no start is automatic"))
        return p

    started = 0
    claimed_writes: set = set()
    for w in cands:
        if w.state in (_work.DONE, _work.ABANDONED):
            continue

        if w.needs:
            p.decisions.append(Decision(w.id, HUMAN_GATE,
                                        f"{len(w.needs)} unanswered question(s) recorded against "
                                        f"it — the next act is the answer, not a start"))
            continue

        if w.blocked_by:
            p.decisions.append(Decision(w.id, HUMAN_GATE,
                                        "held on " + ", ".join(w.blocked_by)
                                        + " — APPROVE or REJECT releases it"))
            continue

        if w.state != _work.READY:
            p.decisions.append(Decision(w.id, BLOCKED,
                                        f"state is {w.state}"
                                        + (f" — {w.blocked_reason}" if w.blocked_reason else "")))
            continue

        allowed, why = _work.guarded_start(w)
        if not allowed:
            p.decisions.append(Decision(
                w.id, HUMAN_GATE if _human(why) else WAIT, "; ".join(why[:3])))
            continue

        if w.id in m.failed:
            p.decisions.append(Decision(
                w.id, WAIT, f"a previous start failed and is not retried automatically "
                            f"({m.failed[w.id][:160]}) — clear it deliberately to re-attempt"))
            continue

        wc = w.contract or {}
        claim = wc.get("resource_claim") or ""
        if claim and wc.get("access") == "WRITE" and claim in claimed_writes:
            p.decisions.append(Decision(w.id, WAIT,
                                        f"another start in this same batch already writes {claim}"))
            continue

        if live + started >= m.max_parallel:
            p.decisions.append(Decision(w.id, WAIT,
                                        f"concurrency limit — {live} running, {started} starting, "
                                        f"max_parallel={m.max_parallel}"))
            continue

        started += 1
        if claim and wc.get("access") == "WRITE":
            claimed_writes.add(claim)
        p.decisions.append(Decision(w.id, START,
                                    f"READY, policy {w.autonomy}, guarded start allowed, "
                                    f"slot {live + started}/{m.max_parallel}"))
    return p


# ------------------------------------------------------------------------------ reporting


def report(m: Mandate, p: Optional[Plan] = None) -> str:
    """One screen an operator can act on. Counts are derived, never carried."""
    p = p if p is not None else plan(m)
    rem = m.remaining()
    o = [f"RUN        {m.run_id}",
         f"MISSION    {m.mission or '—'}",
         f"TARGET     {m.target or '—'}",
         f"MODE       {m.mode} / {m.run_mode}"
         + ("   ⏸ PAUSED BY OPERATOR" if m.paused else ""),
         f"CONCURRENCY {p.running} running, {p.capacity} slot(s) free of {m.max_parallel}"]
    if m.deadline:
        late = rem is not None and rem.total_seconds() < 0
        o.append(f"DEADLINE   {m.deadline}"
                 + (f"   {'OVERDUE by' if late else 'in'} "
                    f"{str(abs(rem)).split('.')[0]}" if rem is not None else "   (unparseable)"))
        o.append("           scheduling context only — it does not change what PASS means")
    if m.failed:
        o.append(f"FAILED     {len(m.failed)} start(s) not retried: {', '.join(sorted(m.failed))}")
    o.append("")
    if p.note:
        o.append(f"  {p.note}")
        o.append("")
    for v in VERDICTS:
        ds = p.by_verdict(v)
        if not ds:
            continue
        o.append(f"  {v}  ({len(ds)})")
        for d in ds:
            o.append(f"      {d.work_id:40} {d.reason}")
        o.append("")
    if not p.decisions:
        o.append("  nothing selected.")
    return "\n".join(o)


def status_report() -> str:
    """Every run on this machine, plus the projection's own headline counts."""
    rows = {w.id: w for w in _work.project()}
    from collections import Counter
    c = Counter(w.state for w in rows.values())
    o = [f"STORE      {_work.store_path()}",
         f"WORK       {len(rows)} row(s): "
         + ", ".join(f"{k}={v}" for k, v in sorted(c.items())),
         ""]
    ms = mandates()
    if not ms:
        o.append("no runs. `python -m factory.missions --preset <id> --create` then RUN DAG.")
        return "\n".join(o)
    for m in ms:
        o.append(report(m, plan(m, rows)))
        o.append("-" * 78)
    return "\n".join(o)


# ------------------------------------------------------------------------------ CLI


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Plan and control autonomous runs over canonical work.")
    ap.add_argument("verb", choices=("status", "plan", "pause", "resume", "clear-failure"))
    ap.add_argument("--run", default="", help="run id")
    ap.add_argument("--work", default="", help="work id, for clear-failure")
    a = ap.parse_args(argv)

    if a.verb == "status":
        print(status_report())
        return 0

    m = load_mandate(a.run)
    if m is None:
        print(f"REFUSED: no run {a.run!r} under {runs_dir()}. "
              f"Known: {', '.join(x.run_id for x in mandates()) or 'none'}", file=sys.stderr)
        return 2

    if a.verb == "plan":
        print(report(m))
        return 0
    if a.verb == "pause":
        m.paused = True
        m.save()
        print(f"{m.run_id}: PAUSED. Running work may finish; nothing new starts.")
        return 0
    if a.verb == "resume":
        m.paused = False
        m.save()
        print(f"{m.run_id}: resumed. Recomputing —\n")
        print(report(m))
        print("\n⚠ Resuming recorded the operator's decision. Starting the newly eligible work "
              "is the pump's job: POST /switchboard/resume, or RESUME in the Switchboard.")
        return 0
    if a.verb == "clear-failure":
        if not a.work:
            print("REFUSED: clear-failure needs --work.", file=sys.stderr)
            return 2
        if a.work not in m.failed:
            print(f"REFUSED: {a.work} has no recorded start failure on {m.run_id}.",
                  file=sys.stderr)
            return 2
        was = m.failed.pop(a.work)
        m.save()
        print(f"{m.run_id}: cleared the start failure on {a.work} ({was[:120]}). "
              f"It becomes eligible again on the next pump.")
        return 0
    return 2                                                       # pragma: no cover


if __name__ == "__main__":                                         # pragma: no cover
    raise SystemExit(main())
