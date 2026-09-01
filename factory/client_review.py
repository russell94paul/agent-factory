"""Client Review — a read model over Factory delivery state.

The Client Review is a **projection**, never a system of record. It reads the mission record,
the append-only :mod:`factory.tasks` store and an authored narrative file, and folds them into
one client-safe contract. Nothing here writes delivery state, and nothing here may be the only
place a fact lives.

Three rules carry the module, and each exists because the estate has already paid for it.

1. **The client boundary is an ALLOW-list, never a deny-list.**
   On 2026-08-31 a deny-list over a credential file ("drop lines containing 'password'") let three
   plaintext passwords through, because the vault stores them in markdown tables and the word
   *password* is in the header row, never the data rows. A guard is only as wide as the relation it
   derives over. So :func:`client_safe` copies the fields named in :data:`CLIENT_SAFE`, and
   everything else — every field a future contributor adds, every field nobody thought about — is
   dropped by default. **Adding a field to the read model does not publish it.**

2. **A guarded word is refused unless its evidence resolves.**
   ``VERIFIED``, ``DEPLOYED``, ``ACCEPTED``, ``HEALTHY``, ``ON TRACK`` and their kin are claims
   about the world. :func:`ground` will not let one render as fact unless a file on disk backs it
   and a task-evidence row carries a basis in :data:`evidence.USABLE`. An outcome whose evidence
   does not resolve degrades to ``CLAIMED`` — it is not silently dropped, and it is not silently
   promoted.

3. **Absence is four different things, and they never collapse.**
   ``LIVE`` / ``LAST_VERIFIED`` / ``STALE`` / ``UNAVAILABLE`` are distinct, for the same reason
   :mod:`factory.contract` keeps ``UNMEASURABLE`` out of ``FAIL``: an instrument that could not
   look has not reported health. A client review that renders "no risks" from a risk register it
   could not read is the 965-run loop wearing a suit.

What this module deliberately does NOT do:

* It does not decide scope. ``docs/specs/client-review-loop-v0.md`` reserves that — a review may
  *propose*, and only an explicit approval moves approved scope. Every item here therefore carries
  :data:`Origin`, so something the factory suggested can never be read as something the client
  asked for.
* It does not invent narrative. Prose comes from an authored review file whose every claim must
  name evidence; this module's job is to check that the evidence is real, not to write the claim.
"""
from __future__ import annotations

import dataclasses
import datetime as _dt
import json
import pathlib
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional, Sequence

from . import assertions as _assertions
from . import evidence as _evidence
from . import projection as _projection
from . import tasks as _tasks

# --------------------------------------------------------------------------------------------
# Vocabulary
# --------------------------------------------------------------------------------------------

#: How fresh the projection is. Four states, never three — see rule 3 in the module docstring.
#: Extracted 2026-09-01 to :mod:`factory.assertions` so the case-study artifact shares ONE
#: vocabulary with this one. Re-exported here: every existing caller and test keeps working.
LIVE = _assertions.LIVE
LAST_VERIFIED = _assertions.LAST_VERIFIED
STALE = _assertions.STALE
UNAVAILABLE = _assertions.UNAVAILABLE

FRESHNESS: tuple = (LIVE, LAST_VERIFIED, STALE, UNAVAILABLE)

#: Grounding of a client-visible claim. Borrowed wholesale from :mod:`factory.evidence` rather
#: than renamed, so the two cannot drift into two vocabularies for one idea.
GROUNDED = _assertions.GROUNDED      #: evidence resolves and carries a usable basis
CLAIMED = _assertions.CLAIMED        #: someone asserted it; nothing usable backs it
UNGROUNDED = _assertions.UNGROUNDED  #: nobody attached anything

#: Who originated an item. Closes the hole the v1 data contract leaves open: without this, a
#: suggestion the factory generated is indistinguishable from something the client requested.
#: ``docs/specs/client-review-loop-v0.md`` contract 8 — *"the team may SUGGEST but must never
#: classify its own idea as a client requirement."*
CLIENT = "CLIENT"
FACTORY_PROPOSED = "FACTORY_PROPOSED"
ORIGINS: tuple = (CLIENT, FACTORY_PROPOSED)

#: Acceptance lattice. Monotone: nothing moves backwards without an explicit CHANGES_REQUESTED.
NOT_READY = "NOT_READY"
READY_FOR_REVIEW = "READY_FOR_REVIEW"
READY_FOR_ACCEPTANCE = "READY_FOR_ACCEPTANCE"
ACCEPTED = "ACCEPTED"
CHANGES_REQUESTED = "CHANGES_REQUESTED"
ACCEPTANCE_STATES: tuple = (NOT_READY, READY_FOR_REVIEW, READY_FOR_ACCEPTANCE,
                            ACCEPTED, CHANGES_REQUESTED)

#: Words that assert something about the world rather than describe an intention. None of these
#: may render as fact without resolved evidence. Compared case-insensitively against the whole
#: status string, so "ON TRACK" and "on track" are the same guarded claim.
GUARDED_WORDS: frozenset = frozenset({
    "success", "successful", "verified", "validated", "deployed", "accepted",
    "healthy", "on track", "ready", "complete", "completed", "passed", "passing",
    "confirmed", "proven", "live", "green",
})

#: What a guarded word degrades to when its evidence does not resolve. Deliberately not "FAILED" —
#: we did not measure a failure, we failed to measure.
UNSUBSTANTIATED = "UNSUBSTANTIATED"

#: How a *plan item's* status was arrived at. Borrowed from :mod:`factory.assertions` rather than
#: named afresh, so the review cannot grow a second vocabulary for "how do we know this".
#:
#: ⭐ This exists because on 2026-09-01 the narrative said the data-cartography milestone was
#: ``BLOCKED`` and the five design milestones ``NOT_STARTED``, while the task store — the same
#: store this module already reads for grounding — recorded R3, D1, D2, D3 and D4 closed with
#: evidence. A hand-typed status rendered as fact, in a client-facing artifact, with the real
#: state sitting one file away. A status nobody checked is not a status; it is a guess in the
#: shape of one.
PLAN_DERIVED = _assertions.DERIVED              #: read from the task store, which is append-only
PLAN_NOT_RECORDED = _assertions.NOT_RECORDED    #: no canonical task backs this. NOT "not started"

#: Canonical task status → client-facing plan status. ``factory.tasks`` owns the left column;
#: nothing here may invent a sixth state for it.
_TASK_TO_PLAN: Dict[str, str] = {
    "done": "DONE",
    "blocked": "BLOCKED",
    "claimed": "IN_PROGRESS",
    "open": "NOT_STARTED",
    "abandoned": "NOT_DELIVERED",
}

#: What a plan item renders as when it names a canonical task the store cannot show us. Distinct
#: from ``NOT_STARTED``: one says the work has not begun, the other says we could not look.
PLAN_UNKNOWN = "NOT_RECORDED"

LIVE_WINDOW_SEC = 15 * 60          #: within this, the projection is LIVE
STALE_AFTER_SEC = 24 * 60 * 60     #: beyond this, say STALE out loud


class ReviewError(ValueError):
    """A read model that cannot be built honestly. Loud, never a silent empty review."""


# --------------------------------------------------------------------------------------------
# The client boundary — an allow-list, per object type
# --------------------------------------------------------------------------------------------

#: The ONLY fields that cross into the client view, per section. Anything absent from this map is
#: dropped, including fields added later. See rule 1.
#:
#: ⛔ Do not add a key here without asking what it exposes when the value is unexpected. The
#: question is not "is this field safe?" but "is every value this field can ever hold safe?"
CLIENT_SAFE: Dict[str, tuple] = {
    "project":    ("id", "name", "client", "subject"),
    "review":     ("status", "freshness_state", "last_updated", "last_verified_at",
                   "last_review_at", "basis"),
    "intent":     ("objective", "requested_outcome", "requirements", "assumptions",
                   "exclusions", "acceptance_criteria", "unresolved_ambiguities"),
    # `pending_writeups` is an INT, deliberately. It says how many completed pieces of work the
    # narrative has not written up yet; it must never carry their titles, which are internal
    # engineering strings ("R3 · Snowflake / data cartography — …") and not client language.
    "progress":   ("completion_percent", "completion_basis", "current_stage", "milestones",
                   "pending_writeups"),
    # Milestones are a nested list inside `progress`, so the `progress` row's own allow-list does
    # not reach them — every key a contributor puts on a milestone used to cross the boundary
    # untouched. Each milestone is now projected through this section in its own right.
    "milestone":  ("title", "status", "status_basis"),
    "delivered":  ("id", "title", "summary", "business_impact", "status", "grounding",
                   "origin", "evidence_refs", "writeup"),
    "evidence":   ("id", "type", "label", "status", "source", "verified_at", "summary",
                   "basis", "evidence_class"),
    "decisions":  ("id", "question", "context", "blocking", "recommendation", "options",
                   "status", "delivery_impact", "origin"),
    "risks":      ("id", "title", "severity", "impact", "mitigation", "owner",
                   "client_action_required", "origin", "state", "state_basis"),
    "next":       ("id", "title", "status", "dependency", "blocked_reason", "status_basis"),
    "acceptance": ("status", "accepted_at", "accepted_by", "notes", "unmet"),
}

_projection.register("client_review", CLIENT_SAFE)

#: Re-exported so existing callers and tests keep working after the 2026-09-01 extraction.
_FORBIDDEN_SUBSTRINGS: tuple = _projection.FORBIDDEN
LeakError = _projection.LeakError


def _scan(value, where):
    """Backstop scan. See :func:`factory.projection.scan`."""
    return _projection.scan(value, where)


def client_safe(section: str, row: Dict[str, Any]) -> Dict[str, Any]:
    """Project one row through the allow-list for `section`.

    Unknown sections raise. A typo'd section name that silently returned ``{}`` would empty a
    whole panel of the client view and look like "nothing to report".
    """
    try:
        return _projection.safe("client_review", section, row)
    except _projection.LeakError:
        raise
    except _projection.ProjectionError as exc:
        raise ReviewError(str(exc)) from None


# --------------------------------------------------------------------------------------------
# Grounding and freshness — extracted 2026-09-01 to factory.assertions, re-exported here.
# The behaviour is byte-identical; tests/test_client_review.py is the acceptance test.
# --------------------------------------------------------------------------------------------

is_guarded = _assertions.is_guarded
ground = _assertions.ground
enforce = _assertions.enforce
freshness = _assertions.freshness


def _iso(ts: Optional[float]) -> Optional[str]:
    if ts is None:
        return None
    return _dt.datetime.fromtimestamp(ts, _dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


# --------------------------------------------------------------------------------------------
# The read model
# --------------------------------------------------------------------------------------------

@dataclass
class Outcome:
    """One client-facing delivered outcome. Not a commit, not a task — an outcome."""
    id: str
    title: str
    summary: str = ""
    business_impact: str = ""
    status: str = "In progress"
    origin: str = CLIENT
    evidence_refs: List[str] = field(default_factory=list)
    grounding: str = UNGROUNDED
    #: AUTHORED when a human wrote the client-facing prose; PENDING when the work is closed in
    #: the record and nobody has yet said what it means for the client. PENDING renders as an
    #: explicit non-final state and blocks the meeting gate — it never renders as a finished item.
    writeup: str = "AUTHORED"


@dataclass
class EvidenceItem:
    id: str
    type: str
    label: str
    status: str
    source: str
    basis: str = "ASSUMED"
    evidence_class: Optional[str] = None
    verified_at: Optional[str] = None
    summary: str = ""


@dataclass
class Decision:
    id: str
    question: str
    context: str = ""
    blocking: bool = False
    recommendation: str = ""
    options: List[str] = field(default_factory=list)
    status: str = "OPEN"
    delivery_impact: str = ""
    origin: str = FACTORY_PROPOSED


@dataclass
class Risk:
    id: str
    title: str
    severity: str = "MEDIUM"
    impact: str = ""
    mitigation: str = ""
    owner: str = ""
    client_action_required: bool = False
    origin: str = FACTORY_PROPOSED
    #: ACTIVE until the canonical task the risk is about closes. A risk that is provably over is
    #: not deleted — deleting it would erase the fact that we found and cleared it — but it must
    #: not keep asking the client for action it no longer needs.
    state: str = "ACTIVE"
    state_basis: str = PLAN_NOT_RECORDED


@dataclass
class NextItem:
    id: str
    title: str
    status: str = "NOT_STARTED"
    dependency: str = ""
    blocked_reason: str = ""
    #: DERIVED when a canonical task backs this status; NOT_RECORDED when nothing does.
    status_basis: str = PLAN_NOT_RECORDED


@dataclass
class ClientReview:
    """The whole contract. Every section optional-safe: a missing list renders as an honest
    empty state, never as a broken page."""
    project: Dict[str, Any] = field(default_factory=dict)
    review: Dict[str, Any] = field(default_factory=dict)
    intent: Dict[str, Any] = field(default_factory=dict)
    progress: Dict[str, Any] = field(default_factory=dict)
    delivered: List[Outcome] = field(default_factory=list)
    evidence: List[EvidenceItem] = field(default_factory=list)
    decisions: List[Decision] = field(default_factory=list)
    risks: List[Risk] = field(default_factory=list)
    next: List[NextItem] = field(default_factory=list)
    acceptance: Dict[str, Any] = field(default_factory=dict)
    #: Operator-only. NEVER projected — it has no entry in CLIENT_SAFE, which is the control.
    diagnostics: Dict[str, Any] = field(default_factory=dict)

    def to_client_dict(self) -> Dict[str, Any]:
        """The client-safe payload. This is the only function a renderer may call.

        ``diagnostics`` is absent from the output because it is absent from ``CLIENT_SAFE``, not
        because it is deleted here — the boundary is the allow-list, and this method just walks it.
        """
        def rows(section, items):
            return [client_safe(section, dataclasses.asdict(i) if dataclasses.is_dataclass(i)
                                else i) for i in items]
        return {
            "project": client_safe("project", self.project),
            "review": client_safe("review", self.review),
            "intent": client_safe("intent", self.intent),
            "progress": client_safe("progress", self.progress),
            "delivered": rows("delivered", self.delivered),
            "evidence": rows("evidence", self.evidence),
            "decisions": rows("decisions", self.decisions),
            "risks": rows("risks", self.risks),
            "next": rows("next", self.next),
            "acceptance": client_safe("acceptance", self.acceptance),
        }


# --------------------------------------------------------------------------------------------
# The assembler
# --------------------------------------------------------------------------------------------

_STAGES = ("Understanding", "Planning", "Implementation", "Testing",
           "Validation", "Deployment", "Client Review", "Acceptance")


def _load_yaml(path: pathlib.Path) -> dict:
    """Load the authored narrative. yaml if available, else a json sibling.

    ``pyyaml`` is the repo's sole runtime dependency, so it is normally present; the json fallback
    exists so a demo machine without it still renders rather than dying mid-meeting.
    """
    if not path.exists():
        raise ReviewError(f"no review narrative at {path}")
    try:
        import yaml  # noqa: PLC0415
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except ImportError:
        alt = path.with_suffix(".json")
        if alt.exists():
            return json.loads(alt.read_text(encoding="utf-8"))
        raise ReviewError(
            f"pyyaml is unavailable and no json fallback at {alt}") from None


def _task_index(store, mission: dict) -> Dict[str, Any]:
    """Map every way a narrative can name a task onto the live task.

    Keys are the mission's own labels (``R3``, ``D5`` — the vocabulary the mission record already
    publishes in ``labels``) and raw task ids. Nothing new is invented: the linkage primitive was
    already in ``.data/missions/*.json``.
    """
    idx: Dict[str, Any] = {}
    if store is None:
        return idx
    by_id = {t.id: t for t in store.all()}
    for tid, t in by_id.items():
        idx[tid] = t
    for label, tid in (mission.get("labels") or {}).items():
        t = by_id.get(tid)
        if t is not None:
            idx[str(label)] = t
    return idx


def _refs_for(ref: Any, index: Dict[str, Any]) -> List[str]:
    """Evidence paths the task store itself already records against a task. Order preserved.

    ⭐ **Only rows with a usable basis are taken.** An ``ASSUMED`` row is, by the estate's own
    definition, not proof — putting one behind a "Proof it works" disclosure would promote an
    assumption by placing it where a client reads proofs.

    It also happens to be the honest reading of a real row. D5 closed on 2026-09-01 carrying
    ``docs/.../D5-recommendation.md (see 0a - sign-off and its limits)`` at basis ``ASSUMED`` — a
    pointer to a *section*, with prose appended, which can never resolve as a filesystem path. The
    same file is cited separately at basis ``DERIVED`` with a clean path, so the outcome grounds
    correctly and the caveat pointer stays out of the client's evidence list where it belongs.
    """
    if not ref:
        return []
    refs = [str(ref)] if isinstance(ref, str) else [str(x) for x in ref]
    out: List[str] = []
    for r in refs:
        t = index.get(r)
        for e in (getattr(t, "evidence", None) or []):
            p = e.get("ref")
            if p and p not in out and e.get("basis") in _evidence.USABLE:
                out.append(p)
    return out


def resolve_plan_status(raw: Dict[str, Any], index: Dict[str, Any]) -> tuple:
    """Decide what one plan item's status renders as, and on what basis.

    Returns ``(status, basis, drift)`` where ``drift`` is ``None`` or the typed value that the
    canonical store contradicts.

    Four outcomes, and they never collapse into each other:

    * **linked, resolvable, agrees** — canonical status, ``DERIVED``.
    * **linked, resolvable, disagrees** — canonical status wins, ``DERIVED``, and the typed value
      is returned as drift so the gate can refuse the artifact. The store is append-only and
      evidence-gated; the yaml is prose someone typed.
    * **linked, not resolvable** — ``NOT_RECORDED``. We could not look, so we do not publish the
      typed guess. This is the blind-instrument rule: a status from an instrument that could not
      see is not a status.
    * **not linked at all** — the typed value, basis ``NOT_RECORDED``. It still renders, because
      dropping it would silently empty the section, but it renders visibly unverified.
    """
    typed = str(raw.get("status") or "NOT_STARTED").upper()
    ref = raw.get("task") or raw.get("task_id")
    if not ref:
        return typed, PLAN_NOT_RECORDED, None
    refs = [str(ref)] if isinstance(ref, str) else [str(x) for x in ref]
    tasks = [index.get(r) for r in refs]
    if not tasks or any(t is None for t in tasks):
        return PLAN_UNKNOWN, PLAN_NOT_RECORDED, None

    states = [_TASK_TO_PLAN.get(t.status, PLAN_UNKNOWN) for t in tasks]
    canonical = _aggregate_plan(states)
    drift = typed if (raw.get("status") and canonical != typed) else None
    return canonical, PLAN_DERIVED, drift


def _aggregate_plan(states: Sequence[str]) -> str:
    """One status for a milestone that spans several tasks.

    A milestone is not done until its last task is. The order below is deliberate and the
    unknown case comes first: if any constituent task could not be read, the milestone's status
    is ``NOT_RECORDED`` — a partially-blind aggregate is not a measurement of the whole.
    """
    if PLAN_UNKNOWN in states:
        return PLAN_UNKNOWN
    if all(s == "DONE" for s in states):
        return "DONE"
    if "BLOCKED" in states:
        return "BLOCKED"
    if "IN_PROGRESS" in states or "DONE" in states:
        return "IN_PROGRESS"
    if "NOT_DELIVERED" in states:
        return "NOT_DELIVERED"
    return "NOT_STARTED"


def _resolve_state_path(given) -> pathlib.Path:
    """A `.data/` path, resolved against the SHARED root when it is relative and not here.

    ⛔ The documented regeneration command passes `--tasks .data/tasks.jsonl` and
    `--mission .data/missions/<id>.json`, both relative to the CWD. Run from the primary checkout
    they are right; run from any worktree they resolve to a `.data/` that holds neither file, and
    the review renders every delivered outcome as UNSUBSTANTIATED. The runbook says to regenerate
    "shortly before the meeting", so the failure lands exactly when nobody has time to notice it.

    Falls back rather than raising: a relative `.data/...` unambiguously means the estate's
    `.data`, and there is only one of those.
    """
    p = pathlib.Path(given)
    if p.exists() or p.is_absolute():
        return p
    from . import repo as _repo_mod
    parts = p.parts
    if ".data" in parts:
        rel = pathlib.Path(*parts[parts.index(".data") + 1:])
        candidate = _repo_mod.data() / rel
        if candidate.exists():
            return candidate
    candidate = _repo_mod.primary() / p
    return candidate if candidate.exists() else p


class UnsafeToPublish(Exception):
    """Raised when a client artefact would understate its own evidence."""


def publication_block(cr_obj) -> list:
    """Reasons this review must NOT be written to a client-facing file. Empty means it may be.

    ⭐ **The safety net that does not depend on anyone getting the CWD right.** Everything above
    makes the common case resolve correctly; this makes the uncommon case impossible to ship.

    ⚠ Deliberately checks the OUTPUT, not the inputs. A path that resolved by luck still passes,
    and a path that looked right but produced a degraded document still fails -- which is the right
    way round for a gate whose job is to protect the reader rather than the caller.
    """
    out = []
    if cr_obj.review.get("freshness_state") == UNAVAILABLE:
        out.append("freshness is UNAVAILABLE — the task store could not be read, so the page "
                   "cannot say when any of this was last verified")
    if cr_obj.progress.get("completion_basis") == "UNAVAILABLE":
        out.append("completion basis is UNAVAILABLE — no mission record was readable, so progress "
                   "is asserted rather than derived")
    bad = [o.title for o in cr_obj.delivered if o.grounding != GROUNDED]
    if bad and len(bad) == len(cr_obj.delivered) and cr_obj.delivered:
        out.append(f"all {len(bad)} delivered outcome(s) are ungrounded — that is the signature of "
                   f"a store that was not read, not of work without evidence")
    return out


def assemble(narrative_path: pathlib.Path,
             tasks_path: Optional[pathlib.Path] = None,
             mission_path: Optional[pathlib.Path] = None,
             root: Optional[pathlib.Path] = None,
             now: Optional[float] = None) -> ClientReview:
    """Fold Factory state plus an authored narrative into one client review.

    Every source is optional except the narrative. A missing task store yields ``UNAVAILABLE``
    freshness and ungrounded outcomes — a degraded but honest review — rather than an exception.
    That is Phase 6 demo resilience: the meeting must not die because one file moved.
    """
    root = pathlib.Path(root or pathlib.Path(__file__).resolve().parent.parent)
    doc = _load_yaml(pathlib.Path(narrative_path))

    # ---- task state (optional) -------------------------------------------------------------
    store = None
    task_rows: List[dict] = []
    tasks_readable = False
    # ⛔ **The DEFAULT must resolve through `factory.repo`, never against the CWD.**
    #
    # Measured 2026-09-01 -- same narrative, same code, differing only in the directory the build
    # was invoked from:
    #
    #     --tasks .data/tasks.jsonl   (the old CWD-relative default, run from a worktree)
    #         grounding  4x ASSERTED      status 4x UNSUBSTANTIATED
    #         freshness  UNAVAILABLE      completion_basis UNAVAILABLE
    #     resolved via factory.repo.data()
    #         grounding  4x SATISFIED     status 4x Complete
    #         freshness  LAST_VERIFIED    completion_basis DERIVED
    #
    # ⭐ The degradation is VISIBLE -- the client page renders "UNSUBSTANTIATED" four times -- so
    # this is not a hidden overclaim. It is the opposite, and still a delivery defect: the client
    # would be handed a document reporting four delivered outcomes as unsubstantiated when every
    # one is fully evidenced, produced by the command the runbook prescribes at the moment it
    # prescribes it. The fail-closed behaviour is correct and is left exactly as it was; what was
    # wrong is that a CWD-relative default made it fire spuriously.
    # ⛔ `None` means ABSENT and must keep meaning that. An earlier version of this fix made it
    # mean "resolve the default", which silently defeated
    # `test_an_unreadable_store_reports_no_undeclared_work_rather_than_zero`: that test passes
    # `tasks_path=None` precisely to simulate a store nobody can read, and the readiness gate
    # blocks on `tasks_readable is False`. Redefining the sentinel made the blind-instrument path
    # unreachable -- a helpful default defeating the control that exists to catch its absence.
    #
    # The real defect was never in this function. It was the CLI DEFAULT, which was the
    # CWD-relative string ".data/tasks.jsonl"; see `main()`. A caller who passes a path still gets
    # it resolved against the shared root when it is relative and not present here.
    if tasks_path is not None:
        tasks_path = _resolve_state_path(tasks_path)
    if mission_path is not None:
        mission_path = _resolve_state_path(mission_path)
    if tasks_path and pathlib.Path(tasks_path).exists():
        try:
            store = _tasks.TaskStore(pathlib.Path(tasks_path))
            tasks_readable = True
            for t in store.all():
                task_rows.extend(t.evidence or [])
        except Exception as exc:                                    # noqa: BLE001
            store, tasks_readable = None, False
            doc.setdefault("_load_error", f"{type(exc).__name__}: {exc}")

    mission = {}
    if mission_path and pathlib.Path(mission_path).exists():
        try:
            mission = json.loads(pathlib.Path(mission_path).read_text(encoding="utf-8"))
        except Exception:                                           # noqa: BLE001
            mission = {}

    # ---- last verified: the newest close/evidence event we can see --------------------------
    last_verified: Optional[float] = None
    if store is not None:
        for t in store.all():
            for ev in t.events:
                if ev.kind in ("evidence", "close"):
                    last_verified = max(last_verified or 0.0, ev.ts)

    fresh = freshness(last_verified, now=now, source_readable=tasks_readable)

    #: Every way the narrative can name a live task, resolved once. See :func:`_task_index`.
    index = _task_index(store, mission)
    drift: List[Dict[str, str]] = []

    cr = ClientReview()
    cr.project = dict(doc.get("project", {}))
    cr.intent = dict(doc.get("intent", {}))
    cr.acceptance = dict(doc.get("acceptance", {}))

    # ---- delivered outcomes, grounded against real files and real evidence rows -------------
    #: Which canonical tasks the narrative claims to have written up. Operator-only: the label is
    #: internal vocabulary and has no entry in CLIENT_SAFE, so it cannot reach the page.
    written_up: set = set()
    for raw in doc.get("delivered", []) or []:
        for ref in ([raw.get("task")] if isinstance(raw.get("task"), str)
                    else list(raw.get("task") or [])):
            written_up.add(str(ref))
        o = Outcome(
            id=str(raw.get("id", "")),
            title=raw.get("title", ""),
            summary=raw.get("summary", ""),
            business_impact=raw.get("business_impact", ""),
            status=raw.get("status", "In progress"),
            origin=raw.get("origin", CLIENT),
            # An authored list wins; an absent one is DERIVED from the task's own evidence rows.
            # Retyping a path that the append-only store already holds is a way to get it wrong.
            evidence_refs=(list(raw.get("evidence_refs", []) or [])
                           or _refs_for(raw.get("task"), index)),
        )
        if o.origin not in ORIGINS:
            raise ReviewError(f"outcome {o.id}: origin {o.origin!r} not in {ORIGINS}")
        o.grounding = ground(o.evidence_refs, task_rows, root)
        o.status = enforce(o.status, o.grounding)
        cr.delivered.append(o)

    # ---- evidence items ---------------------------------------------------------------------
    seen_refs = {r.get("ref"): r for r in task_rows}
    for raw in doc.get("evidence", []) or []:
        src = raw.get("source", "")
        backing = seen_refs.get(src, {})
        present = bool(src) and (root / src).exists()
        item = EvidenceItem(
            id=str(raw.get("id", "")),
            type=raw.get("type", "artefact"),
            label=raw.get("label", ""),
            source=src,
            summary=raw.get("summary", ""),
            basis=backing.get("basis", raw.get("basis", "ASSUMED")),
            evidence_class=backing.get("evidence_class", raw.get("evidence_class")),
            # An artefact that is not on disk is NOT_FOUND, never "verified". The presenter needs
            # to see that before the client does.
            status="VERIFIED" if (present and backing.get("basis") in _evidence.USABLE)
                   else ("PRESENT" if present else "NOT_FOUND"),
            verified_at=_iso(last_verified) if present else None,
        )
        cr.evidence.append(item)

    for raw in doc.get("decisions", []) or []:
        cr.decisions.append(Decision(
            id=str(raw.get("id", "")), question=raw.get("question", ""),
            context=raw.get("context", ""), blocking=bool(raw.get("blocking", False)),
            recommendation=raw.get("recommendation", ""),
            options=list(raw.get("options", []) or []),
            status=raw.get("status", "OPEN"),
            delivery_impact=raw.get("delivery_impact", ""),
            origin=raw.get("origin", FACTORY_PROPOSED)))

    for raw in doc.get("risks", []) or []:
        r_state, r_basis = "ACTIVE", PLAN_NOT_RECORDED
        if raw.get("task"):
            st, b, _ = resolve_plan_status({"task": raw["task"]}, index)
            if b == PLAN_DERIVED:
                r_state, r_basis = ("RESOLVED" if st == "DONE" else "ACTIVE"), PLAN_DERIVED
        cr.risks.append(Risk(
            id=str(raw.get("id", "")), title=raw.get("title", ""),
            severity=raw.get("severity", "MEDIUM"), impact=raw.get("impact", ""),
            mitigation=raw.get("mitigation", ""), owner=raw.get("owner", ""),
            # A resolved risk asks the client for nothing. Leaving this true would put a cleared
            # item back on the client's to-do list, which is the same lie as a stale status.
            client_action_required=(bool(raw.get("client_action_required", False))
                                    and r_state == "ACTIVE"),
            origin=raw.get("origin", FACTORY_PROPOSED),
            state=r_state, state_basis=r_basis))

    # ---- plan items: canonical task state overrides the typed one ---------------------------
    for raw in doc.get("next", []) or []:
        status, sbasis, d = resolve_plan_status(raw, index)
        if d:
            drift.append({"section": "next", "id": str(raw.get("id", "")),
                          "title": raw.get("title", ""), "task": str(raw.get("task") or ""),
                          "narrative_says": d, "canonical_says": status})
        item = NextItem(
            id=str(raw.get("id", "")), title=raw.get("title", ""),
            status=status,
            dependency=raw.get("dependency", ""),
            blocked_reason=raw.get("blocked_reason", ""),
            status_basis=sbasis)
        # A blocked_reason is prose about a block. Once the store says the work is no longer
        # blocked, that prose is a statement about a state that has ended — so it does not travel.
        if status != "BLOCKED":
            item.blocked_reason = ""
        cr.next.append(item)

    # ---- progress: DERIVED from real task state, never typed --------------------------------
    stage = doc.get("progress", {}).get("current_stage", _STAGES[0])
    milestones = []
    for raw in list(doc.get("progress", {}).get("milestones", []) or []):
        status, sbasis, d = resolve_plan_status(raw, index)
        if d:
            drift.append({"section": "milestone", "id": "",
                          "title": raw.get("title", ""), "task": str(raw.get("task") or ""),
                          "narrative_says": d, "canonical_says": status})
        milestones.append(client_safe("milestone", {"title": raw.get("title", ""),
                                                    "status": status, "status_basis": sbasis}))
    # ---- work that closed in the record and has no client-facing write-up yet ----------------
    #
    # ⭐ This is the honest-degradation path, and it is why the artifact can be regenerated the
    # moment a task closes without anybody editing prose. When the record says a task is DONE and
    # the narrative has not written it up, the review does not silently omit it — omission is
    # indistinguishable from completeness. It renders an explicit non-final entry instead:
    #
    #   * the **title** is the one already authored for that same task in ``next[]``. Nothing is
    #     invented; this is the client wording a human already chose for this piece of work. If
    #     no such wording exists, no entry is made — a title is a claim, and this will not write
    #     one on a human's behalf.
    #   * the **evidence** is whatever the task store already holds, so the entry is grounded by
    #     the same rule as every other outcome and cannot show a green word if the file is gone.
    #   * the **summary and business impact are empty**, because what the work *means for the
    #     client* is a semantic conclusion and this module does not author those.
    #   * the **origin is FACTORY_PROPOSED**, never CLIENT. The plan item's true provenance is not
    #     recorded anywhere, and of the two available values only one is safe to be wrong about:
    #     ``docs/specs/client-review-loop-v0.md`` contract 8 forbids the team classifying its own
    #     idea as a client requirement, so the error is taken in the conservative direction.
    pending = undeclared_completions(store, mission, written_up)
    _next_title = {}
    for raw in doc.get("next", []) or []:
        ref = raw.get("task") or raw.get("task_id")
        for r in ([str(ref)] if isinstance(ref, str) else [str(x) for x in (ref or [])]):
            _next_title.setdefault(r, raw.get("title", ""))
    for item in pending:
        title = _next_title.get(item["label"])
        if not title:
            continue
        o = Outcome(id=f"PENDING-{item['label']}", title=title,
                    status="Awaiting write-up", origin=FACTORY_PROPOSED,
                    evidence_refs=_refs_for(item["label"], index),
                    writeup="PENDING")
        o.grounding = ground(o.evidence_refs, task_rows, root)
        o.status = enforce(o.status, o.grounding)
        cr.delivered.append(o)

    pct, basis = _completion(store, mission)
    cr.progress = {"completion_percent": pct, "completion_basis": basis,
                   "current_stage": stage, "milestones": milestones,
                   "pending_writeups": len(pending)}

    # ---- review header ----------------------------------------------------------------------
    grounded_n = sum(1 for o in cr.delivered if o.grounding == GROUNDED)
    cr.review = {
        "status": doc.get("review", {}).get("status", "In delivery"),
        "freshness_state": fresh,
        "last_updated": _iso(now or _dt.datetime.now(_dt.timezone.utc).timestamp()),
        "last_verified_at": _iso(last_verified),
        "last_review_at": doc.get("review", {}).get("last_review_at"),
        "basis": "DERIVED" if tasks_readable else "UNAVAILABLE",
    }

    # ---- acceptance: computed, and it refuses to advance without grounding ------------------
    cr.acceptance = _acceptance(cr, doc.get("acceptance", {}) or {})

    # ---- operator-only. Never crosses the boundary; there is no CLIENT_SAFE["diagnostics"]. --
    cr.diagnostics = {
        "tasks_readable": tasks_readable,
        "task_evidence_rows": len(task_rows),
        "grounded_outcomes": grounded_n,
        "ungrounded_outcomes": len(cr.delivered) - grounded_n,
        "narrative": str(narrative_path),
        "root": str(root),
        "missing_evidence_files": [e.source for e in cr.evidence if e.status == "NOT_FOUND"],
        # ⭐ The evidence *index* section was already checked for missing files; the paths cited
        # by each delivered outcome were not. On 2026-09-01 that gap mattered: the D2–D4 evidence
        # existed only in another session's uncommitted worktree, so four outcomes silently
        # degraded to CLAIMED and the gate had nothing to name. A degrade is not a diagnosis.
        "unresolved_outcome_evidence": [
            {"outcome": o.id, "ref": r}
            for o in cr.delivered for r in o.evidence_refs if not (root / r).exists()],
        # Operator-only, and the reason this artifact is safe to regenerate unattended: where the
        # typed narrative and the append-only store disagree, the store wins on the page and the
        # disagreement is reported here rather than absorbed.
        "narrative_drift": drift,
        # Canonical work that closed with evidence and that the narrative has not written up.
        # Not a defect in this module — a signal that the prose is behind the delivery.
        "undeclared_completions": pending,
        # Operator-only. Surfaces the source defect that _completion's declared-set basis
        # deliberately steps around, so the fix cannot hide the fault.
        "mission_integrity": mission_integrity(store, mission),
    }
    return cr


def _completion(store, mission: dict) -> tuple:
    """Completion as a fraction of the mission's own declared tasks.

    Returns ``(percent, basis)``. The basis is the whole point: this repo's mission record carries
    ``estimate_basis: ASSUMED`` on every task, so an effort-weighted percentage would be an
    assumption dressed as a measurement. Counting closed children is at least ``DERIVED`` from
    something append-only, and it says so.
    """
    if store is None:
        return None, "UNAVAILABLE"

    # ⭐ THE COUNTING BASIS, DECLARED: one unit is one task the mission record LABELS. Not one
    # child of the mission task.
    #
    # Measured 2026-08-31 on `marketing-model-reconstruction-v1`: the mission task has **10**
    # children but the record declares **8** labelled tasks. R1 and R2 each exist twice — the
    # labelled task, and an unlabelled duplicate created later that carries the evidence rows.
    # Counting children unioned with labels scored 4 of 10 = 40%, double-counting two completed
    # workstreams and overstating delivery to the client by 15 points. Counting the declared
    # labels scores 2 of 8 = 25%, which is what the mission says the work is.
    #
    # The union was the intuitive basis and it was wrong. A basis chosen after seeing the data is
    # a conclusion wearing a method's clothes, so it is named here and tested in
    # `test_completion_counts_declared_tasks_not_duplicated_children`.
    labelled = set((mission.get("labels") or {}).values())
    if labelled:
        population = [t for t in store.all() if t.id in labelled]
    else:
        mission_task = mission.get("mission_task")
        population = [t for t in store.all() if t.parent and t.parent == mission_task]
    if not population:
        return None, "UNAVAILABLE"
    done = [t for t in population if t.status == _tasks.DONE]
    return round(100.0 * len(done) / len(population)), "DERIVED"


def mission_integrity(store, mission: dict) -> Dict[str, Any]:
    """Compare the mission record's DECLARED task set against the store's observed children.

    ⭐ Why this exists at all. :func:`_completion` counts the declared set, which is the correct
    client-facing basis — and it is also *defensive*, because it makes a duplicated workstream
    disappear from the client number. A defensive calculation that silently absorbs a source
    defect is how that defect becomes permanently invisible: the symptom is gone, so nobody looks.
    So the divergence the calculation stepped around is reported here instead.

    Measured 2026-08-31 on ``marketing-model-reconstruction-v1``: 8 declared, 10 observed. R1 and
    R2 each exist twice — the labelled task, plus an unlabelled duplicate carrying the evidence
    rows.

    ⛔ **Operator-only.** This dict names internal task ids, titles and statuses. It has no entry
    in :data:`CLIENT_SAFE` and must not be given one without a deliberate client-presentation
    design pass. It reaches nobody through :meth:`ClientReview.to_client_dict`.

    ⛔ **Reports, never repairs.** Reconciling the mission record belongs to mission control, not
    to a read model. Nothing here mutates the store or the record.
    """
    if store is None or not mission:
        return {"status": "UNAVAILABLE",
                "reason": "no task store or no mission record to compare",
                "declared_task_count": None, "observed_child_count": None,
                "duplicate_or_unexpected_tasks": [], "declared_not_observed": [],
                "client_progress_basis": "UNAVAILABLE"}

    labels: Dict[str, str] = dict(mission.get("labels") or {})
    declared = set(labels.values())
    mission_task = mission.get("mission_task")
    observed = [t for t in store.all() if t.parent and t.parent == mission_task]
    observed_ids = {t.id for t in observed}

    unexpected = [{"id": t.id, "title": t.title, "status": t.status}
                  for t in observed if t.id not in declared]
    missing = [{"label": lab, "id": tid} for lab, tid in sorted(labels.items())
               if tid not in observed_ids]

    status = "WARNING" if (unexpected or missing) else "OK"
    return {
        "status": status,
        "declared_task_count": len(declared),
        "observed_child_count": len(observed),
        "duplicate_or_unexpected_tasks": unexpected,
        "declared_not_observed": missing,
        "client_progress_basis": (
            f"declared logical task set ({len(declared)} task(s) named by the mission record); "
            f"{len(unexpected)} observed child(ren) excluded from the client figure"),
    }


def undeclared_completions(store, mission: dict, written_up: Iterable[str]) -> List[Dict[str, str]]:
    """Canonical tasks that closed DONE and that no client-facing outcome names.

    The narrative is prose; the store is the record. When the record moves and the prose does not,
    the review does not become wrong — it becomes *incomplete*, which is harder to see, because a
    section that is missing an entry looks exactly like a section that is complete. This makes the
    gap countable so the delivery gate can refuse on it.

    Silent on an unreadable store: nothing observed is not the same as nothing there, and this
    returning ``[]`` for an absent store would be exactly the blind zero the module exists to
    prevent. ``diagnostics["tasks_readable"]`` carries that distinction, and the gate reads it.
    """
    if store is None:
        return []
    claimed = {str(x) for x in (written_up or ())}
    by_id = {t.id: t for t in store.all()}
    out: List[Dict[str, str]] = []
    for label, tid in (mission.get("labels") or {}).items():
        t = by_id.get(tid)
        if t is None or t.status != _tasks.DONE:
            continue
        if str(label) in claimed or str(tid) in claimed:
            continue
        out.append({"label": str(label), "id": str(tid), "title": t.title})
    return out


def _acceptance(cr: ClientReview, authored: dict) -> dict:
    """Compute acceptance state, and list what is unmet.

    Acceptance is not a field somebody sets. It is refused while any outcome is ungrounded, any
    blocking decision is open, or any client-action risk stands — and the reasons are returned so
    the client can see *why* it is not yet acceptable, rather than a bare amber light.
    """
    def plural(n: int, one: str, many: str) -> str:
        # Client-facing copy, so no "decision(s)". The read model owns the wording because the
        # count and the noun have to agree, and only the assembler knows the count.
        return f"{n} {one if n == 1 else many}"

    unmet: List[str] = []
    ungrounded = [o.title for o in cr.delivered if o.grounding != GROUNDED]
    if ungrounded:
        unmet.append(plural(len(ungrounded), "outcome", "outcomes")
                     + " without resolved evidence")
    blocking = [d for d in cr.decisions if d.blocking and d.status.upper() == "OPEN"]
    if blocking:
        unmet.append(plural(len(blocking), "blocking decision", "blocking decisions")
                     + " awaiting your input")
    needs_client = [r for r in cr.risks if r.client_action_required]
    if needs_client:
        unmet.append(plural(len(needs_client), "risk", "risks")
                     + " needing a decision from you")
    pending = [n for n in cr.next if n.status != "DONE"]
    if pending:
        unmet.append(plural(len(pending), "planned outcome", "planned outcomes")
                     + " not yet delivered")

    declared = (authored.get("status") or "").upper()
    if declared == ACCEPTED and unmet:
        # An authored ACCEPTED over unmet criteria is exactly the unsupported claim this module
        # exists to refuse. Downgrade loudly rather than honour it.
        computed = READY_FOR_REVIEW
        unmet.insert(0, "an ACCEPTED status was declared but is not supported by state")
    elif unmet:
        computed = NOT_READY if len(unmet) > 2 else READY_FOR_REVIEW
    else:
        computed = declared if declared in ACCEPTANCE_STATES else READY_FOR_ACCEPTANCE

    return {"status": computed,
            "accepted_at": authored.get("accepted_at"),
            "accepted_by": authored.get("accepted_by"),
            "notes": authored.get("notes", ""),
            "unmet": unmet}


# --------------------------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------------------------

# --------------------------------------------------------------------------------------------
# The delivery gate — "can I safely open this in front of the client?"
# --------------------------------------------------------------------------------------------

#: Gate verdicts. Three, not two: an artifact that is safe to open but carries something the
#: presenter must know is a different thing from one that is simply fine, and collapsing the two
#: is how a known caveat becomes an unknown one at the worst possible moment.
GATE_READY = "READY"
GATE_READY_WITH_WARNINGS = "READY_WITH_WARNINGS"
GATE_NOT_READY = "NOT_READY"

BLOCK, WARN, PASS = "BLOCK", "WARN", "PASS"


def meeting_gate(cr: ClientReview) -> Dict[str, Any]:
    """Answer one question: can this be opened in front of the client?

    Every check derives from a contract this module already enforces — there is no new notion of
    correctness here, only a place where the existing ones are read together and given a verdict.
    A check that cannot fail is not a check, so each one below is paired with a test that makes it
    fire.

    Returns ``{"verdict", "checks": [{"id", "status", "detail"}], "blocking", "warnings"}``.
    """
    d = cr.diagnostics or {}
    checks: List[Dict[str, str]] = []

    def add(cid: str, status: str, detail: str) -> None:
        checks.append({"id": cid, "status": status, "detail": detail})

    # 1. Could we read the record at all? A review built from nothing renders a confident empty
    #    page, which is the single worst failure available to this artifact.
    if d.get("tasks_readable"):
        add("canonical_state_readable", PASS,
            f"task store read; {d.get('task_evidence_rows', 0)} evidence row(s)")
    else:
        add("canonical_state_readable", BLOCK,
            "the task store was not readable — every status on the page would be unverified")

    # 2. Freshness. UNAVAILABLE means we never saw a verification at all.
    fs = (cr.review or {}).get("freshness_state")
    if fs == UNAVAILABLE:
        add("freshness", BLOCK, "no verification timestamp is visible")
    elif fs == STALE:
        add("freshness", WARN,
            f"last verified {cr.review.get('last_verified_at')} — regenerate before the meeting")
    else:
        add("freshness", PASS, f"{fs} (verified {cr.review.get('last_verified_at')})")

    # 3. Typed status contradicting the append-only store.
    drift = d.get("narrative_drift") or []
    if drift:
        add("narrative_matches_canonical_state", BLOCK,
            "; ".join(f"{x['section']} {x['id'] or x['title'][:28]}: narrative says "
                      f"{x['narrative_says']}, record says {x['canonical_says']}"
                      for x in drift[:6]) + (f" (+{len(drift) - 6} more)" if len(drift) > 6 else ""))
    else:
        add("narrative_matches_canonical_state", PASS, "no typed status contradicts the record")

    # 4. Completed work with no client-facing write-up. Not wrong — incomplete, which is worse,
    #    because a section missing an entry looks exactly like a section that is complete.
    und = d.get("undeclared_completions") or []
    pending = [o.id for o in cr.delivered if o.writeup == "PENDING"]
    shown = {o.id.replace("PENDING-", "") for o in cr.delivered if o.writeup == "PENDING"}
    unnamed = [x["label"] for x in und if x["label"] not in shown]
    if pending or unnamed:
        detail = []
        if pending:
            detail.append(f"{len(pending)} outcome(s) render as awaiting write-up: "
                          + ", ".join(pending))
        if unnamed:
            detail.append(f"{len(unnamed)} completed task(s) appear nowhere on the page at all "
                          "(no client wording exists for them): " + ", ".join(unnamed))
        add("completed_work_is_written_up", BLOCK, "; ".join(detail))
    else:
        add("completed_work_is_written_up", PASS, "every completed task is written up")

    # 5. A status that renders as known but was never checked against anything.
    unchecked = [n.get("id") or n.get("title", "")[:24]
                 for n in ([dataclasses.asdict(x) for x in cr.next]
                           + list(cr.progress.get("milestones") or []))
                 if n.get("status_basis") != PLAN_DERIVED]
    if unchecked:
        add("no_status_rendered_without_a_basis", BLOCK,
            f"{len(unchecked)} plan item(s) render a status nothing verifies: "
            + ", ".join(str(x) for x in unchecked[:8]))
    else:
        add("no_status_rendered_without_a_basis", PASS,
            "every plan status is DERIVED from the task store")

    # 6. An artefact cited on the page that is not on disk.
    missing = list(d.get("missing_evidence_files") or [])
    missing += [f"{x['outcome']} → {x['ref']}"
                for x in (d.get("unresolved_outcome_evidence") or [])]
    if missing:
        add("cited_evidence_resolves", BLOCK,
            f"{len(missing)} cited artefact(s) not on disk in this checkout: "
            + ", ".join(missing[:5]) + (f" (+{len(missing) - 5} more)" if len(missing) > 5 else ""))
    else:
        add("cited_evidence_resolves", PASS, "every cited artefact resolves on disk")

    # 7. A guarded word that lost its evidence and degraded in place.
    unsub = [o.id for o in cr.delivered if o.status == UNSUBSTANTIATED]
    if unsub:
        add("no_unsubstantiated_claim", BLOCK,
            "outcome(s) degraded to UNSUBSTANTIATED: " + ", ".join(unsub))
    else:
        add("no_unsubstantiated_claim", PASS, "no claim degraded")

    # 8. Sections the runbook actually walks through.
    empty = [name for name, val in (("intent", cr.intent), ("delivered", cr.delivered),
                                    ("next", cr.next), ("evidence", cr.evidence)) if not val]
    if empty:
        add("required_sections_populated", BLOCK, "empty section(s): " + ", ".join(empty))
    else:
        add("required_sections_populated", PASS,
            f"{len(cr.delivered)} outcome(s), {len(cr.evidence)} evidence item(s), "
            f"{len(cr.decisions)} decision(s), {len(cr.next)} next item(s)")

    # 9. The boundary itself. If projection raises, nothing may be shown at all.
    try:
        cr.to_client_dict()
        add("client_boundary_holds", PASS, "allow-list projection and backstop scan both pass")
    except Exception as exc:                                        # noqa: BLE001
        add("client_boundary_holds", BLOCK, f"{type(exc).__name__}: {exc}")

    # 10. Operator-visible, presenter-relevant, not client-facing: warnings, never blocks.
    mi = d.get("mission_integrity") or {}
    if mi.get("status") == "WARNING":
        add("mission_record_integrity", WARN,
            f"{mi.get('declared_task_count')} declared vs {mi.get('observed_child_count')} "
            "observed children — the client figure counts the declared set only")
    else:
        add("mission_record_integrity", PASS, "mission record matches observed children")

    resolved = [r.id for r in cr.risks if r.state == "RESOLVED"]
    if resolved:
        add("risks_still_current", WARN,
            "risk(s) shown as resolved from the record: " + ", ".join(resolved)
            + " — confirm the wording reads as closed, not open")
    else:
        add("risks_still_current", PASS, "every listed risk is still active")

    blocking = [c for c in checks if c["status"] == BLOCK]
    warnings = [c for c in checks if c["status"] == WARN]
    verdict = (GATE_NOT_READY if blocking
               else (GATE_READY_WITH_WARNINGS if warnings else GATE_READY))
    return {"verdict": verdict, "checks": checks,
            "blocking": blocking, "warnings": warnings}


def main(argv=None) -> int:
    import argparse
    p = argparse.ArgumentParser(prog="python -m factory.client_review",
                                description="Assemble and render a Client Review.")
    p.add_argument("narrative", help="path to the authored review yaml")
    # ⛔ Not ".data/tasks.jsonl". A CWD-relative default meant the evidence strength of a
    # client-facing document depended on which directory the build was invoked from.
    # ⛔ Not ".data/tasks.jsonl". A CWD-relative default meant the evidence strength of a
    # client-facing document depended on which directory the build was invoked from. Resolved
    # here, at the CLI boundary, so `assemble()`'s `None`-means-absent contract is untouched.
    p.add_argument("--tasks", default=None,
                   help="task store (default: the shared .data/ resolved via factory.repo)")
    p.add_argument("--force", action="store_true",
                   help="write the artefact even if it understates its own evidence")
    p.add_argument("--mission", default=None)
    p.add_argument("--json", action="store_true", help="print the client-safe payload as json")
    p.add_argument("--out", default=None, help="write a self-contained HTML review here")
    p.add_argument("--gate", action="store_true",
                   help="run the meeting-readiness gate; exit 1 if it is NOT_READY")
    p.add_argument("--root", default=None,
                   help="checkout the cited evidence paths resolve against. Defaults to this "
                        "repo. Point it at a worktree when the evidence has not merged yet.")
    a = p.parse_args(argv)

    from . import repo as _repo_mod
    _tasks = pathlib.Path(a.tasks) if a.tasks else (_repo_mod.data() / "tasks.jsonl")
    cr = assemble(pathlib.Path(a.narrative),
                  tasks_path=_tasks,
                  mission_path=pathlib.Path(a.mission) if a.mission else None,
                  root=pathlib.Path(a.root) if a.root else None)
    if a.json:
        print(json.dumps(cr.to_client_dict(), indent=2))
    if a.out:
        blocks = publication_block(cr)
        if blocks and not getattr(a, "force", False):
            raise UnsafeToPublish(
                "refusing to write a client artefact that understates its own evidence:\n  - "
                + "\n  - ".join(blocks)
                + "\n\nThis is almost always the working directory: run it from the primary\n"
                  "checkout, or omit --tasks/--mission and let them resolve via factory.repo.\n"
                  "Pass --force only if you intend to publish the weaker claims.")
        from .client_review_render import render_html      # noqa: PLC0415
        pathlib.Path(a.out).write_text(render_html(cr), encoding="utf-8")
        print(f"wrote {a.out}")
    if a.gate:
        g = meeting_gate(cr)
        print(f"MEETING GATE  {g['verdict']}")
        for c in g["checks"]:
            mark = {"PASS": "  ok  ", "WARN": " warn ", "BLOCK": "BLOCK "}[c["status"]]
            print(f"  {mark} {c['id']:<36} {c['detail']}")
        if g["verdict"] == GATE_NOT_READY:
            return 1
        return 0

    if not a.json and not a.out:
        d = cr.diagnostics
        print(f"{cr.project.get('name','?')} — {cr.review['status']} "
              f"[{cr.review['freshness_state']}]")
        print(f"  acceptance      {cr.acceptance['status']}")
        for u in cr.acceptance["unmet"]:
            print(f"    unmet         {u}")
        print(f"  outcomes        {d['grounded_outcomes']} grounded, "
              f"{d['ungrounded_outcomes']} not")
        if d["missing_evidence_files"]:
            print(f"  ⚠ missing      {', '.join(d['missing_evidence_files'])}")

        # Operator-only, and printed loudly: the client figure is correct precisely because it
        # excluded these, which is why the exclusion has to be said out loud somewhere.
        mi = d.get("mission_integrity") or {}
        if mi.get("status") == "WARNING":
            print()
            print("MISSION_INTEGRITY_WARNING")
            print(f"  declared_task_count          {mi['declared_task_count']}")
            print(f"  observed_child_count         {mi['observed_child_count']}")
            print(f"  client_progress_basis        {mi['client_progress_basis']}")
            print("  duplicate_or_unexpected_tasks")
            for t in mi["duplicate_or_unexpected_tasks"]:
                print(f"    {t['id']}  {t['status']:<9} {t['title'][:58]}")
            for t in mi["declared_not_observed"]:
                print(f"    ⛔ declared but not observed: {t['label']} -> {t['id']}")
            print("  ⛔ not repaired here — reconciling the mission record is mission control's.")
    return 0


if __name__ == "__main__":                                          # pragma: no cover
    raise SystemExit(main())
