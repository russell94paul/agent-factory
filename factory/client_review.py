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

from . import evidence as _evidence
from . import tasks as _tasks

# --------------------------------------------------------------------------------------------
# Vocabulary
# --------------------------------------------------------------------------------------------

#: How fresh the projection is. Four states, never three — see rule 3 in the module docstring.
LIVE = "LIVE"                    #: read from live state within :data:`LIVE_WINDOW_SEC`
LAST_VERIFIED = "LAST_VERIFIED"  #: not live, but a verification timestamp is known
STALE = "STALE"                  #: older than :data:`STALE_AFTER_SEC`; say so, do not hide it
UNAVAILABLE = "UNAVAILABLE"      #: the source could not be read at all — NOT the same as "nothing"

FRESHNESS: tuple = (LIVE, LAST_VERIFIED, STALE, UNAVAILABLE)

#: Grounding of a client-visible claim. Borrowed wholesale from :mod:`factory.evidence` rather
#: than renamed, so the two cannot drift into two vocabularies for one idea.
GROUNDED = _evidence.SATISFIED    #: evidence resolves and carries a usable basis
CLAIMED = _evidence.ASSERTED      #: someone asserted it; nothing usable backs it
UNGROUNDED = _evidence.ABSENT     #: nobody attached anything

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
    "progress":   ("completion_percent", "completion_basis", "current_stage", "milestones"),
    "delivered":  ("id", "title", "summary", "business_impact", "status", "grounding",
                   "origin", "evidence_refs"),
    "evidence":   ("id", "type", "label", "status", "source", "verified_at", "summary",
                   "basis", "evidence_class"),
    "decisions":  ("id", "question", "context", "blocking", "recommendation", "options",
                   "status", "delivery_impact", "origin"),
    "risks":      ("id", "title", "severity", "impact", "mitigation", "owner",
                   "client_action_required", "origin"),
    "next":       ("id", "title", "status", "dependency", "blocked_reason"),
    "acceptance": ("status", "accepted_at", "accepted_by", "notes", "unmet"),
}

#: Substrings that must never appear in a client-visible string, whatever the allow-list says.
#: This is a second, independent gate — belt and braces — and it is explicitly NOT the primary
#: control, because a deny-list alone is what failed on 2026-08-31.
_FORBIDDEN_SUBSTRINGS: tuple = (
    "password", "passwd", "secret", "api_key", "apikey", "token=", "bearer ",
    "azure-kv:", "keyvault", "private_key", "-----begin",
)


class LeakError(ReviewError):
    """A client-visible string carried something the deny-gate recognised.

    Reaching this exception means the allow-list already failed. It is a backstop, and a hit here
    is a defect to fix in the projection — never something to suppress at the call site.
    """


def _scan(value: Any, where: str) -> Any:
    """Backstop scan. Raises rather than redacting: a silent redaction hides a broken boundary."""
    if isinstance(value, str):
        low = value.lower()
        for bad in _FORBIDDEN_SUBSTRINGS:
            if bad in low:
                raise LeakError(
                    f"{where}: client-visible string contains {bad!r}. The allow-list let this "
                    "through, which means the projection is wrong — fix the projection, do not "
                    "redact here.")
    elif isinstance(value, dict):
        for k, v in value.items():
            _scan(v, f"{where}.{k}")
    elif isinstance(value, (list, tuple)):
        for i, v in enumerate(value):
            _scan(v, f"{where}[{i}]")
    return value


def client_safe(section: str, row: Dict[str, Any]) -> Dict[str, Any]:
    """Project one row through the allow-list for `section`.

    Unknown sections raise. A typo'd section name that silently returned ``{}`` would empty a
    whole panel of the client view and look like "nothing to report".
    """
    if section not in CLIENT_SAFE:
        raise ReviewError(
            f"{section!r} has no client-safe field list. Add one to CLIENT_SAFE — a section with "
            "no allow-list is not publishable by default, and that is the intended behaviour.")
    out = {k: row[k] for k in CLIENT_SAFE[section] if k in row}
    return _scan(out, section)


# --------------------------------------------------------------------------------------------
# Grounding
# --------------------------------------------------------------------------------------------

def is_guarded(status: str) -> bool:
    """True when `status` asserts something that needs evidence behind it."""
    low = (status or "").strip().lower()
    if low in GUARDED_WORDS:
        return True
    return any(w in low.split() for w in GUARDED_WORDS if " " not in w) or \
        any(w in low for w in GUARDED_WORDS if " " in w)


def ground(refs: Sequence[str], rows: Iterable[dict], root: pathlib.Path) -> str:
    """Return GROUNDED / CLAIMED / UNGROUNDED for a set of evidence references.

    ``GROUNDED`` requires **both** halves, and the two halves answer different questions:

    * every ref resolves to a file that exists under `root` — *the artefact is really there*;
    * at least one task-evidence row whose ``ref`` matches carries a basis in
      :data:`evidence.USABLE` — *somebody measured or derived it, rather than assuming it*.

    A file that exists but is backed only by an ``ASSUMED`` row is ``CLAIMED``. A ref naming a file
    that is not on disk is ``CLAIMED`` too, never ``GROUNDED`` — the claim survives, its promotion
    does not.
    """
    refs = [r for r in (refs or []) if r]
    if not refs:
        return UNGROUNDED
    by_ref = {r.get("ref"): r for r in rows if isinstance(r, dict)}
    all_present = all((root / r).exists() for r in refs)
    any_usable = any((by_ref.get(r) or {}).get("basis") in _evidence.USABLE for r in refs)
    if all_present and any_usable:
        return GROUNDED
    return CLAIMED


def enforce(status: str, grounding: str) -> str:
    """Return the status a client may see, given its grounding.

    A guarded word with anything less than :data:`GROUNDED` becomes :data:`UNSUBSTANTIATED`.
    Unguarded statuses ("In progress", "Blocked") pass through untouched — they describe an
    intention or an observable state, not a verified outcome.
    """
    if not is_guarded(status):
        return status
    return status if grounding == GROUNDED else UNSUBSTANTIATED


# --------------------------------------------------------------------------------------------
# Freshness
# --------------------------------------------------------------------------------------------

def freshness(last_verified: Optional[float], now: Optional[float] = None,
              source_readable: bool = True) -> str:
    """Classify how much the projection can be trusted as current.

    `source_readable=False` yields ``UNAVAILABLE`` regardless of timestamps: an unreadable source
    has not told us the state is old, it has told us nothing. Collapsing those is exactly the
    failure :mod:`factory.contract` keeps ``UNMEASURABLE`` separate to prevent.
    """
    if not source_readable:
        return UNAVAILABLE
    if last_verified is None:
        return UNAVAILABLE
    now = _dt.datetime.now(_dt.timezone.utc).timestamp() if now is None else now
    age = now - last_verified
    if age <= LIVE_WINDOW_SEC:
        return LIVE
    if age <= STALE_AFTER_SEC:
        return LAST_VERIFIED
    return STALE


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


@dataclass
class NextItem:
    id: str
    title: str
    status: str = "NOT_STARTED"
    dependency: str = ""
    blocked_reason: str = ""


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

    cr = ClientReview()
    cr.project = dict(doc.get("project", {}))
    cr.intent = dict(doc.get("intent", {}))
    cr.acceptance = dict(doc.get("acceptance", {}))

    # ---- delivered outcomes, grounded against real files and real evidence rows -------------
    for raw in doc.get("delivered", []) or []:
        o = Outcome(
            id=str(raw.get("id", "")),
            title=raw.get("title", ""),
            summary=raw.get("summary", ""),
            business_impact=raw.get("business_impact", ""),
            status=raw.get("status", "In progress"),
            origin=raw.get("origin", CLIENT),
            evidence_refs=list(raw.get("evidence_refs", []) or []),
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
        cr.risks.append(Risk(
            id=str(raw.get("id", "")), title=raw.get("title", ""),
            severity=raw.get("severity", "MEDIUM"), impact=raw.get("impact", ""),
            mitigation=raw.get("mitigation", ""), owner=raw.get("owner", ""),
            client_action_required=bool(raw.get("client_action_required", False)),
            origin=raw.get("origin", FACTORY_PROPOSED)))

    for raw in doc.get("next", []) or []:
        cr.next.append(NextItem(
            id=str(raw.get("id", "")), title=raw.get("title", ""),
            status=raw.get("status", "NOT_STARTED"),
            dependency=raw.get("dependency", ""),
            blocked_reason=raw.get("blocked_reason", "")))

    # ---- progress: DERIVED from real task state, never typed --------------------------------
    stage = doc.get("progress", {}).get("current_stage", _STAGES[0])
    milestones = list(doc.get("progress", {}).get("milestones", []) or [])
    pct, basis = _completion(store, mission)
    cr.progress = {"completion_percent": pct, "completion_basis": basis,
                   "current_stage": stage, "milestones": milestones}

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

def main(argv=None) -> int:
    import argparse
    p = argparse.ArgumentParser(prog="python -m factory.client_review",
                                description="Assemble and render a Client Review.")
    p.add_argument("narrative", help="path to the authored review yaml")
    p.add_argument("--tasks", default=".data/tasks.jsonl")
    p.add_argument("--mission", default=None)
    p.add_argument("--json", action="store_true", help="print the client-safe payload as json")
    p.add_argument("--out", default=None, help="write a self-contained HTML review here")
    a = p.parse_args(argv)

    cr = assemble(pathlib.Path(a.narrative),
                  tasks_path=pathlib.Path(a.tasks) if a.tasks else None,
                  mission_path=pathlib.Path(a.mission) if a.mission else None)
    if a.json:
        print(json.dumps(cr.to_client_dict(), indent=2))
    if a.out:
        from .client_review_render import render_html      # noqa: PLC0415
        pathlib.Path(a.out).write_text(render_html(cr), encoding="utf-8")
        print(f"wrote {a.out}")
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
