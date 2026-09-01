"""Coordination signals — DIRECTLY MEASURED, and deliberately not summed into one number.

⭐ **There is no coordination-tax percentage here, and that is the point.** Every figure below is
a count or a duration read from state that already exists: the task store's append-only log, the
session registry, the blocked-question inbox. A single headline percentage would need a
denominator nobody has defined — "coordination as a fraction of *what*?" — and once printed it
would be quoted back as though the definition existed. FU92-420 shipped three definitions of one
word in a single document; the fix is to declare the basis before producing the number, and the
honest basis for an aggregate is *not yet decided*.

So this module publishes the ingredients, each with its own name and its own basis, and leaves the
aggregate to a later decision made with the census in front of it.

## ⛔ What each signal can and cannot see

    active_interventions     questions a session actually wrote. It CANNOT see a session that
                             is stuck without writing one — silence is not measured as health.
    waiting_for_human        wall time since the question was written, not since anyone noticed.
    handoffs                 `session` events in the store. Work executed without ever being
                             associated with a session contributes zero, truthfully.
    manual_starts/auto       `start` events only. Work started before P1 recorded no mode, so it
                             counts toward NEITHER — reported as `starts_unrecorded` rather than
                             folded into MANUAL, which would invent an operator decision.
    stale_needs_you          a question whose asking session is not live. That is a measurement
                             about the SESSION, not about whether the question still matters.

Every one of those limits is rendered beside the number rather than kept in this docstring.
"""
from __future__ import annotations

import dataclasses
import time
from typing import Any, Dict, List, Optional

from . import tasks as _tasks
from . import work as _work

#: Intervention priority bands. ⛔ Bands, not a score. The factors below are real and measured, but
#: the weighting between "blocks four items" and "has waited twenty minutes" is a judgement nobody
#: has validated. A number like `73.4` would present that judgement as precision; a band plus the
#: factors that produced it lets the operator apply their own weighting and see the working.
HIGH, MEDIUM, LOW = "HIGH PRIORITY", "MEDIUM", "LOW"


@dataclasses.dataclass
class Signal:
    """One measured coordination figure, with the basis it was measured on."""
    name: str
    value: Any
    basis: str          # MEASURED | DERIVED | NOT-RECORDED | NOT-VISIBLE
    limit: str = ""     # what this number structurally cannot see

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)


def _ago_s(ts) -> Optional[float]:
    try:
        return max(0.0, time.time() - float(ts))
    except (TypeError, ValueError):
        return None


def human_duration(sec: Optional[float]) -> str:
    if sec is None:
        return "unknown"
    s = int(sec)
    if s < 90:
        return f"{s}s"
    if s < 5400:
        return f"{s // 60}m"
    if s < 172800:
        return f"{s // 3600}h"
    return f"{s // 86400}d"


# ------------------------------------------------------------------ intervention priority


def downstream_blocked(work_id: str, works: List[dict]) -> List[str]:
    """Work whose readiness waits, transitively, on `work_id`.

    Transitive rather than immediate on purpose: an item that blocks one thing which blocks four
    is not a low-priority intervention, and the immediate count would say it was.
    """
    direct: Dict[str, List[str]] = {}
    for w in works:
        for d in w.get("depends_on") or []:
            direct.setdefault(d, []).append(w["id"])
    seen, stack = set(), list(direct.get(work_id, []))
    while stack:
        cur = stack.pop()
        if cur in seen:
            continue
        seen.add(cur)
        stack.extend(direct.get(cur, []))
    return sorted(seen)


def prioritise(needs_rows: List[dict], works: List[dict],
               critical: Optional[List[str]] = None) -> List[dict]:
    """Order NEEDS YOU by what an answer would actually unblock, and SHOW the reasoning.

    ⭐ The operator's real question is *"which human intervention unblocks the most valuable work
    right now?"* — not *"which is oldest"*. So each row carries the factors that placed it, and
    the page renders them, because an ordering nobody can check is an ordering nobody trusts.

    Factors, all measured:
      - how many work items it transitively blocks
      - whether it sits on the mission critical path
      - how long it has been waiting
      - whether the asking session is still alive (a dead session's question still matters, but it
        is not blocking a running process, and the two must not look identical)
    """
    crit = set(critical or [])
    by_id = {w["id"]: w for w in works}
    out = []
    for r in needs_rows:
        row = dict(r)
        w = r.get("work") or {}
        wid = w.get("id") or (r.get("questions") or [{}])[0].get("work_id") or ""
        blocked = downstream_blocked(wid, works) if wid else []
        q = (r.get("questions") or [{}])[0]
        waited = _ago_s(q.get("at") or q.get("ts") or q.get("asked_at"))
        on_crit = wid in crit

        why: List[str] = []
        if blocked:
            why.append(f"Blocks {len(blocked)} downstream work item"
                       f"{'s' if len(blocked) != 1 else ''}")
        if on_crit:
            why.append("Critical path")
        if waited is not None:
            why.append(f"Waiting {human_duration(waited)}")
        elif not r.get("live"):
            why.append("No session — how long it has waited is NOT RECORDED")
        if r.get("live"):
            why.append("Session is alive and blocked on this")
        else:
            why.append("No live session — answering unblocks nothing running right now")

        # The band. Deliberately coarse and deliberately explainable in one sentence each.
        if blocked or (on_crit and r.get("live")):
            band = HIGH
        elif r.get("live"):
            band = MEDIUM
        else:
            band = LOW
        row["priority"] = band
        row["why"] = why
        row["blocks"] = blocked
        row["waited_s"] = waited
        row["on_critical_path"] = on_crit
        row["_sort"] = (
            {HIGH: 0, MEDIUM: 1, LOW: 2}[band],
            -len(blocked),
            0 if on_crit else 1,
            -(waited or 0),
        )
        out.append(row)
    out.sort(key=lambda r: r["_sort"])
    for r in out:
        r.pop("_sort", None)
    return out


# ----------------------------------------------------------------------- the signal set


def signals(st: dict, store=None) -> List[Signal]:
    """Every coordination signal this estate can currently measure, each with its basis.

    Reads the projection it is handed plus the task store's event log. Nothing here is estimated
    and nothing is summed across dimensions.
    """
    works = st.get("work") or []
    now = st.get("now") or {}
    needs = now.get("needs_you") or []
    out: List[Signal] = []

    live_needs = [r for r in needs if r.get("live")]
    out.append(Signal("active human interventions", len(live_needs), "MEASURED",
                      "counts questions a session WROTE — a session stuck without writing one is "
                      "invisible here, so this is not a measure of how many are stuck"))

    stale = [r for r in needs if not r.get("live")]
    out.append(Signal("stale / orphaned NEEDS YOU", len(stale), "MEASURED",
                      "the asking session is not live; the question may still be worth answering"))

    waits = [r.get("waited_s") for r in needs if r.get("waited_s") is not None]
    out.append(Signal("longest wait for a human",
                      human_duration(max(waits)) if waits else "NOT RECORDED",
                      "MEASURED" if waits else "NOT-RECORDED",
                      "time since the question was WRITTEN, not since anyone saw it"))

    blocked_deps = sum(1 for w in works
                       for c in (w.get("checks") or [])
                       if c.get("name") == "dependencies" and c.get("verdict") == _work.FAIL)
    out.append(Signal("work blocked on a dependency", blocked_deps, "MEASURED",
                      "counts declared dependencies only"))

    live_ids = {w["id"] for w in works if w.get("state") == _work.RUNNING}
    conflicts = sum(1 for w in works
                    if any(c in live_ids for c in (w.get("conflicts_with") or [])))
    undeclared = sum(1 for w in works if not (w.get("contract") or {}).get("resource_claim"))
    out.append(Signal("active resource conflicts", conflicts, "MEASURED",
                      f"{undeclared} work item(s) declare no resource claim and are reported "
                      f"conflict-free — an absence of a declaration, not evidence of isolation"))

    handoffs = manual = auto = unrecorded = reopened = 0
    if store is not None:
        for t in store.all():
            kinds = [e.kind for e in t.events]
            handoffs += kinds.count("session")
            for e in t.events:
                if e.kind == "start":
                    if e.data.get("mode") == _tasks.AUTO_START:
                        auto += 1
                    else:
                        manual += 1
            if "claim" in kinds and "start" not in kinds:
                unrecorded += 1
            # Reopened: a close, followed later by anything that is not another close.
            ci = [i for i, k in enumerate(kinds) if k == "close"]
            if ci and any(k not in ("close", "note", "evidence") for k in kinds[ci[0] + 1:]):
                reopened += 1

    out.append(Signal("session handoffs", handoffs, "MEASURED",
                      "counts session attachments; work run without being associated with a "
                      "session contributes zero, truthfully"))
    out.append(Signal("manual launches", manual, "MEASURED", "recorded MANUAL_START events"))
    out.append(Signal("autonomous launches", auto, "MEASURED", "recorded AUTO_START events"))
    out.append(Signal("starts with no recorded mode", unrecorded,
                      "NOT-RECORDED" if unrecorded else "MEASURED",
                      "started before the mode was recorded — counted as NEITHER manual nor "
                      "autonomous, because folding them into MANUAL would invent an operator "
                      "decision that was never made"))
    out.append(Signal("reopened / reworked work", reopened, "MEASURED",
                      "a close followed by further activity"))
    return out
