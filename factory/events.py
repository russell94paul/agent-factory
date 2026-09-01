"""The run event stream — the one record that cannot be rebuilt afterwards.

Every other fact about a run survives its death. Git says what was committed, the transcripts say
what it cost, the worktree says whether anything was left dirty. **What was NOT chosen survives
nowhere.** By the time a run finishes, the configuration it ran under is the only configuration
anyone can see, and the question "what else was eligible, and why this one" has no answer left in
the world. R19 §5 states it as the rule this module exists to hold:

    The eligible set costs nothing to write and cannot be reconstructed afterwards.

So `RunLog.start` **refuses** a run with no eligible set. Not warns — refuses. Every other field
here can be backfilled by someone patient; that one is gone the instant the process exits.

⭐ **Every terminal event carries a verdict, and `GreenContract` is what assigns it.** Never the
agent, never the provider, never the UI. `verdict()` takes a `contract.Verdict` and nothing else,
so an event stream that cannot express UNMEASURABLE is not constructible here. That distinction is
the reason this repository exists; a stream that collapsed it would make every downstream number a
claim about the system rather than a measurement of it.

⚠ **Five verdicts, not four.** ERROR was added to `factory.contract` after most of this estate's
prose was written — TTCN-3's ``none < pass < inconc < fail < error`` (ITU-T Z.140 §24.2), where
``error`` is set by the *test system* rather than the test case. A boot prompt or design note
saying "the four verdicts" predates it. This module takes the enum, so it cannot fall behind.

**Why this is not a third ledger, which was the explicit risk.**

    .data/events.jsonl   THIS — the stream. Append-only, one line per thing that happened,
                         written as it happens. It is the source.
    .data/runs.jsonl     the FOLD. `factory.runs.record` writes one durable summary row per run,
                         derived from the stream by `fold()`. It is not a second observation of
                         the same events; it is this file, summarised, for the surfaces that want
                         one row per run rather than a history.
    prefect-connectors/.sessions   a DIFFERENT POPULATION, in another repository, read by
                         `g_work_is_attributable`. It counts that repo's sessions. Folding it in
                         here would join two things that do not count the same unit, which is how
                         a reconciliation becomes a fabrication. It stays where it is, on purpose,
                         and this sentence is the record of that decision.

⚠ **Ordering is file order, not timestamp order.** Two events inside one run can share a
timestamp to the microsecond. `seq` is the authority within a run and is monotonic per `RunLog`;
across runs, only the file's order means anything.

⚠ A torn final line is skipped, never fatal — `bus.py`'s rule. A crashed writer must not make the
whole history unreadable.
"""
from __future__ import annotations

import datetime as _dt
import json
import os
import pathlib
import uuid
from typing import Any, Dict, Iterable, List, Optional

from . import repo as _repo
from .contract import Verdict

#: Every kind of thing that can be recorded. A closed set on purpose: an unknown kind is a typo
#: that would otherwise sit in the stream looking like data, and a fold that silently ignores it
#: reports a run as having skipped a step it actually took.
KINDS = (
    "run_started",        # ⭐ carries the eligible set. Refused without one.
    "preflight_checked",  # what this run was told about its own prior failures — see preflight.py
    "worktree_ready",
    "claim_taken",
    "agent_dispatched",
    "agent_returned",
    "evidence_gathered",
    "verdict_assigned",   # terminal — carries a Verdict AND a failure_family when not PASS
    "run_finished",       # terminal — carries a Verdict AND a failure_family when not PASS
    "run_aborted",        # terminal — carries a Verdict (ERROR or NOT_RUN) + a failure_family
)

#: Kinds that state an outcome. Each MUST carry a verdict; the writer refuses otherwise.
TERMINAL = ("verdict_assigned", "run_finished", "run_aborted")


class EventError(ValueError):
    """The event could not be written, and the message says which rule refused it."""


def path() -> pathlib.Path:
    """The stream, in the PRIMARY worktree.

    ⚠ Not `__file__.parent.parent`. A controller running inside a lane worktree would otherwise
    write to that worktree's `.data/`, and a per-worktree event stream is not a stream — that is
    F70/F71, already paid for twice by `bus.py` and `runs.py`.
    """
    return _repo.data() / "events.jsonl"


def _now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat()


def new_run_id() -> str:
    """Sortable-ish and unique. The timestamp prefix makes a listing readable; the random tail is
    what actually guarantees two concurrent controllers do not collide."""
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y%m%dT%H%M%S") + "-" + uuid.uuid4().hex[:8]


def _append(rec: Dict[str, Any]) -> Dict[str, Any]:
    p = path()
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, default=str) + "\n")
    return rec


class RunLog:
    """One run's writer. Holds the run id and the sequence counter, and nothing else.

    Constructed only through `start()`, because a `RunLog` that exists without a `run_started`
    event on disk is a run whose eligible set was never written — the one loss this module is
    here to prevent.
    """

    def __init__(self, run_id: str, seq: int = 0):
        self.run_id = run_id
        self._seq = seq

    # ------------------------------------------------------------------ writing
    @classmethod
    def start(cls, ticket: str, eligible: Iterable[Dict[str, Any]], chosen: Optional[str],
              rule: str, **fields: Any) -> "RunLog":
        """Open a run. **Refuses without the eligible set.**

        `eligible` is every configuration that passed the filter, each as
        ``{"id": ..., "chosen": bool, "why": ...}``. `rule` names the filter that produced it, in
        words an operator can disagree with — "the preset whose type_id matches the ticket" is a
        rule; "selected" is not.

        ⛔ An empty eligible set is refused rather than recorded as ``[]``. ``[]`` is ambiguous
        between *nothing was eligible* — a real and interesting state — and *nobody wrote it
        down*, and that is precisely the ZERO-vs-NOT-RECORDED collapse this estate keeps paying
        for. A run with genuinely nothing eligible should not be started; it should be aborted
        with `run_aborted`, which says so.
        """
        el = [dict(e) for e in (eligible or [])]
        if not el:
            raise EventError(
                "run_started requires the eligible set: every configuration that passed the "
                "filter, which was chosen, and under what rule. It costs nothing to write now "
                "and CANNOT be reconstructed once this process exits (R19 §5). If nothing was "
                "eligible, that is a run_aborted, not a run_started with an empty list.")
        for e in el:
            if "id" not in e or "chosen" not in e:
                raise EventError(
                    f"eligible entry {e!r} needs at least 'id' and 'chosen'. A list that does not "
                    "say which one was taken records the candidates and loses the decision.")
        if not (rule or "").strip():
            raise EventError(
                "run_started requires `rule` — the filter that produced the eligible set. Without "
                "it the list is a set of names and the reasoning is gone.")
        ids = [e["id"] for e in el]
        chosen_ids = [e["id"] for e in el if e.get("chosen")]
        if chosen is not None and chosen not in ids:
            raise EventError(
                f"chosen={chosen!r} is not in the eligible set {ids!r}. A choice outside the set "
                "means the set is not what the filter actually produced.")
        if chosen is not None and chosen_ids != [chosen]:
            raise EventError(
                f"the eligible set marks {chosen_ids!r} as chosen but the run says {chosen!r}. "
                "These must agree or the record contradicts itself.")

        log = cls(new_run_id())
        log._emit("run_started", ticket=ticket, eligible=el, chosen=chosen, rule=rule,
                  host=os.environ.get("COMPUTERNAME") or os.environ.get("HOSTNAME", ""),
                  **fields)
        return log

    def _emit(self, kind: str, **fields: Any) -> Dict[str, Any]:
        if kind not in KINDS:
            raise EventError(f"{kind!r} is not a known event kind. Known: {list(KINDS)}")
        self._seq += 1
        return _append({"at": _now(), "run": self.run_id, "seq": self._seq,
                        "kind": kind, **fields})

    def emit(self, kind: str, **fields: Any) -> Dict[str, Any]:
        """Record a non-terminal event. Terminal kinds go through `verdict()` / `finish()`."""
        if kind in TERMINAL:
            raise EventError(
                f"{kind!r} states an outcome, so it must carry a verdict assigned by a "
                "GreenContract. Use verdict(), finish() or abort() — they take a Verdict and "
                "nothing else, which is what stops an agent or a provider naming its own result.")
        return self._emit(kind, **fields)

    def verdict(self, verdict: Verdict, contract: str, results: Optional[List[dict]] = None,
                failure_family: Optional[str] = None, classified_by: str = "",
                **fields: Any) -> Dict[str, Any]:
        """Record the verdict a `GreenContract` assigned, with the per-assertion detail."""
        return self._emit("verdict_assigned", verdict=_verdict_value(verdict),
                          contract=contract, results=list(results or []),
                          **_family_fields(verdict, failure_family, classified_by), **fields)

    def finish(self, verdict: Verdict, failure_family: Optional[str] = None,
               classified_by: str = "", **fields: Any) -> Dict[str, Any]:
        return self._emit("run_finished", verdict=_verdict_value(verdict),
                          **_family_fields(verdict, failure_family, classified_by), **fields)

    def abort(self, verdict: Verdict, why: str, failure_family: Optional[str] = None,
              classified_by: str = "", **fields: Any) -> Dict[str, Any]:
        """End a run that never got as far as a verdict of its own.

        ⚠ `verdict` is still required and still comes from the enum. An abort is ERROR when our
        apparatus broke and NOT_RUN when it never started — those are different remedies (fix the
        harness, versus nothing happened) and a single "aborted" flag cannot tell them apart.
        """
        return self._emit("run_aborted", verdict=_verdict_value(verdict), why=why,
                          **_family_fields(verdict, failure_family, classified_by), **fields)

    def preflight(self, **fields: Any) -> Dict[str, Any]:
        """What this run was told about its own prior failures, before anything was dispatched.

        ⛔ Non-terminal on purpose: a preflight states no outcome, carries no verdict, and — in V0
        — cannot stop anything. `preflight.Match.would_refuse` rides along as a recorded shadow of
        a policy that is not in force. See `factory.preflight`.
        """
        return self._emit("preflight_checked", **fields)


def aborted(ticket: str, considered: Iterable[Dict[str, Any]], rule: str,
            verdict: Verdict, why: str, failure_family: Optional[str] = None,
            classified_by: str = "", **fields: Any) -> Dict[str, Any]:
    """A selection that never became a run — recorded without opening one.

    ⚠ There is no `run_started` here on purpose. Nothing started, and writing one so the schema
    looks tidy would put a run in the stream that never existed. What is worth keeping is the
    **considered** set: "we looked at all five presets and none matched this ticket" is a finding
    about the preset table, and it vanishes completely otherwise.

    `considered` is not `eligible`. Eligible means *passed the filter*; considered means *was
    looked at*. Naming them the same field would make an empty eligible set and a full considered
    set indistinguishable in the fold, which is the whole distinction this event exists to draw.
    """
    return _append({"at": _now(), "run": new_run_id(), "seq": 1, "kind": "run_aborted",
                    "ticket": ticket, "considered": [dict(c) for c in considered],
                    "rule": rule, "verdict": _verdict_value(verdict), "why": why,
                    "started": False,
                    **_family_fields(verdict, failure_family, classified_by), **fields})


def _family_fields(verdict: Verdict, family: Optional[str], classified_by: str) -> Dict[str, Any]:
    """The failure-family half of a terminal event, validated before it is written.

    ⭐ **Presence is the difference between UNCLASSIFIED and NOT-RECORDED.** Every terminal event
    written from here on carries the key: `UNCLASSIFIED` when the classifier could not place the
    failure, and a named family when it could. An event with *no* key at all is one written before
    this field existed, and a reader must report that as NOT-RECORDED rather than as an
    unclassified failure. Defaulting the key in the reader would erase that distinction — the same
    collapse as reporting UNMEASURABLE as FAIL, one level up.

    A PASS carries neither key. Nothing failed, so there is nothing to classify, and allowing a
    family on a green run would let a success be filed under a defect.
    """
    from .preflight import check_family
    fam = check_family(family, verdict)
    if fam is None:
        return {}
    return {"failure_family": fam, "classified_by": classified_by or "unspecified"}


def _verdict_value(v: Any) -> str:
    if not isinstance(v, Verdict):
        raise EventError(
            f"verdict must be a factory.contract.Verdict, got {type(v).__name__} ({v!r}). A "
            "string here is how a provider or an agent ends up naming its own outcome; the enum "
            "is what forces it to come from a GreenContract.")
    return v.value


# ------------------------------------------------------------------------------------ reading

def read(run: Optional[str] = None) -> List[dict]:
    """Every event, in file order. One run's events when `run` is given.

    A torn line is skipped rather than fatal: a writer killed mid-append must not take the whole
    history with it.
    """
    p = path()
    if not p.is_file():
        return []
    out = []
    for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except Exception:                                          # noqa: BLE001
            continue
        if run is None or rec.get("run") == run:
            out.append(rec)
    return out


def runs() -> List[str]:
    """Run ids, in the order they first appear."""
    seen, out = set(), []
    for rec in read():
        r = rec.get("run")
        if r and r not in seen:
            seen.add(r)
            out.append(r)
    return out


def fold(run: str) -> dict:
    """The current state of one run, derived from its events. This is what `runs.jsonl` is made of.

    ⚠ `verdict` is `None` when no terminal event has been recorded, and that is **not** NOT_RUN.
    A run whose process died before assigning a verdict is a run whose outcome nobody observed;
    reporting that as NOT_RUN would claim the run never happened, when the stream plainly says it
    started. `terminal` says which it is.
    """
    return _fold(run, read(run))


def fold_all() -> Dict[str, dict]:
    """Every run's state, from ONE pass over the file, in first-appearance order.

    ⭐ Added because `fold()` per run is quadratic and a caller had already crossed a published
    budget with it. `preflight.prior_attempts` called `runs()` then `fold()` for each id, and each
    `fold()` re-read the whole stream: **MEASURED 84 ms at 8 runs, 3.7 s at 500, 12.7 s at 1000**,
    against a stated 200 ms preflight budget. A start-time check that costs seconds is one people
    route around, and the routing-around is invisible.

    ⚠ It delegates to the same `_fold` as `fold()` rather than reimplementing the reduction. Two
    copies of a fold drift, and the one people read is the one that is wrong — this estate has
    lost three hand-maintained lists that way.
    """
    by: Dict[str, List[dict]] = {}
    for rec in read():
        r = rec.get("run")
        if r:
            by.setdefault(r, []).append(rec)
    return {r: _fold(r, evs) for r, evs in by.items()}


def _fold(run: str, evs: List[dict]) -> dict:
    """The reduction itself, over events already read. The single definition of a run's state."""
    if not evs:
        return {"run": run, "found": False}
    first = evs[0]
    term = [e for e in evs if e.get("kind") in TERMINAL]
    state = {
        "run": run, "found": True,
        "ticket": first.get("ticket"),
        "eligible": first.get("eligible", []),
        "chosen": first.get("chosen"),
        "rule": first.get("rule"),
        "started_at": first.get("at"),
        "events": len(evs),
        "kinds": [e.get("kind") for e in evs],
        "terminal": term[-1].get("kind") if term else None,
        "verdict": term[-1].get("verdict") if term else None,
        # ⚠ `.get`, and absent when the terminal event predates the field — that absence is what
        # `preflight` reads as NOT-RECORDED rather than as UNCLASSIFIED. Do not default it here.
        "failure_family": term[-1].get("failure_family") if term else None,
        "classified_by": term[-1].get("classified_by") if term else None,
        "why": term[-1].get("why") if term else None,
        "at": evs[-1].get("at"),
    }
    for key in ("team", "team_version", "agent_versions", "repo", "provider", "job"):
        if key in first:
            state[key] = first[key]
    for e in evs:
        if e.get("kind") == "agent_returned":
            state["returncode"] = e.get("returncode")
            state["transcript"] = e.get("transcript")
            state["limit"] = e.get("limit")
        if e.get("kind") == "verdict_assigned":
            state["results"] = e.get("results", [])
            state["contract"] = e.get("contract")
    return state


def render(run: str) -> str:
    """One run as plain text — the same content a UI would show, so the two cannot drift."""
    st = fold(run)
    if not st.get("found"):
        return f"{run}: no events recorded"
    lines = [f"{run}  ticket={st.get('ticket')}  {st.get('verdict') or 'no verdict recorded'}",
             f"  rule      {st.get('rule')}"]
    for e in st.get("eligible", []):
        mark = "->" if e.get("chosen") else "  "
        lines.append(f"  {mark} {e.get('id')}" + (f"  {e['why']}" if e.get("why") else ""))
    for e in read(run):
        lines.append(f"  [{str(e.get('seq')):>2}] {str(e.get('kind')):<18} {e.get('at')}")
    return "\n".join(lines)


def main(argv=None) -> int:
    ids = runs()
    if not ids:
        print(f"no runs recorded in {path()}")
        print("That is NOT-RECORDED, not zero: nothing has executed a TeamSpec through "
              "factory.control on this machine.")
        return 0
    print(f"{len(ids)} run(s) in {path()}\n")
    for r in ids:
        print(render(r))
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
