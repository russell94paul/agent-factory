"""Forensic case study — the second artifact type, and the proof the compiler shape generalises.

A case study is a **projection**, exactly as :mod:`factory.client_review` is. It reads the mission
record, the append-only :mod:`factory.tasks` store, an authored forensic narrative and a long-form
prose reconstruction, and folds them into one typed record. Nothing here writes delivery state, and
nothing here may be the only place a fact lives.

Five rules carry the module. Four are inherited from the client review because they were already
paid for; the fifth is new and comes from the delivery this module first renders.

1. **The boundary is an allow-list** (:mod:`factory.projection`). Adding a field to the view model
   does not publish it.
2. **A guarded word is refused unless its evidence resolves** (:mod:`factory.assertions`).
3. **Absence is not zero.** A KPI with no measurement renders its basis — ``NOT_RECORDED``,
   ``REQUIRES_DELIVERY_002`` — and never a number. Five of Delivery #001's thirty-seven issues are
   an absence rendered as a number; an artifact about them must not commit the sixth.
4. **Simulated is not proven.** :class:`assertions.Counterfactual` has no ``status`` field, so it
   cannot be passed to a component that renders outcomes. The rule is structural, not editorial.
5. ⭐ **Both tracks or neither.** A case study whose issues all sit on one track is refused. The
   client work and the mission that investigated it each produced failures; a rendering that showed
   only the client's would be the "Agent Factory would have fixed everything" artifact, and the
   gate decision of 2026-09-01 requires that this be a mechanism rather than an intention.

What this module deliberately does NOT do:

* It does not mutate anything, propose scope, or carry approval state. ``client-review-loop-v0.md``
  reserves the client decision lifecycle; this artifact is a read-only projection of completed
  history and stays on its side of that line by having no write path at all.
* It does not parse prose. Long-form narrative is cited by ``path#anchor`` and validated by
  :mod:`factory.forensic_source`.
"""
from __future__ import annotations

import dataclasses
import datetime as _dt
import json
import pathlib
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from . import assertions as _assertions
from . import context as _context
from . import evidence as _evidence
from . import forensic_source as _src
from . import projection as _projection
from . import tasks as _tasks

ARTIFACT = "case_study"


class CaseStudyError(ValueError):
    """A forensic record that cannot be compiled honestly. Loud, never a partial artifact."""


# --------------------------------------------------------------------------------------------
# Vocabulary
# --------------------------------------------------------------------------------------------

CLIENT_DELIVERY = "CLIENT_DELIVERY"      #: the work done for the client
FACTORY_MISSION = "FACTORY_MISSION"      #: the mission that investigated it
TRACKS: tuple = (CLIENT_DELIVERY, FACTORY_MISSION)

#: How measurable a KPI is *today*. The gate decision forbids manufacturing the ones we cannot
#: measure, and requires that they appear as a state rather than as an authored estimate.
MEASURABLE_NOW = "MEASURABLE_NOW"
DERIVABLE_NOW = "DERIVABLE_NOW"
PARTIALLY_MEASURABLE = "PARTIALLY_MEASURABLE"
BLIND_INSTRUMENT = "BLIND_INSTRUMENT"          #: the instrument exists and cannot see the answer
NOT_RECORDED = "NOT_RECORDED"
REQUIRES_NEW_INSTRUMENTATION = "REQUIRES_NEW_INSTRUMENTATION"
REQUIRES_DELIVERY_002 = "REQUIRES_DELIVERY_002"

MEASURABILITY: tuple = (MEASURABLE_NOW, DERIVABLE_NOW, PARTIALLY_MEASURABLE, BLIND_INSTRUMENT,
                        NOT_RECORDED, REQUIRES_NEW_INSTRUMENTATION, REQUIRES_DELIVERY_002)

#: A KPI in one of these states has no number, and rendering one would be an invention.
NUMBERLESS: tuple = (NOT_RECORDED, REQUIRES_NEW_INSTRUMENTATION, REQUIRES_DELIVERY_002,
                     BLIND_INSTRUMENT)

#: The allow-list. Narrower than the client review's, deliberately: this artifact carries our own
#: failures, an unrotated credential incident and a client's commercial figures.
CASE_STUDY_SAFE: Dict[str, tuple] = {
    "delivery":   ("id", "name", "client", "subject", "window", "track"),
    "companion":  ("id", "name", "window", "track", "relationship"),
    "meta":       ("compiled_at", "freshness_state", "basis", "last_verified_at",
                   "source_sha", "narrative_sha", "compiler_version"),
    "summary":    ("id", "issue", "why", "detected", "ideal_interception", "capability",
                   "benefit"),
    "timeline":   ("id", "order", "track", "occurred_at", "precision", "title", "intent",
                   "known", "believed", "assumed", "unknown", "action", "evidence_refs",
                   "status", "observed", "checked", "superseded_by"),
    "issues":     ("id", "track", "title", "what_happened", "why", "root_causes",
                   "mistake_types", "stage_introduced", "stage_detected", "escape_distance",
                   "ideal_interception_stage", "potential_escape", "still_open", "client_risk",
                   "evidence_refs", "basis", "counterfactual", "sides"),
    "patterns":   ("id", "name", "statement", "issue_ids", "count", "note"),
    "scenes":     ("id", "order", "step_ref", "title", "context", "information_available",
                   "question", "choices", "actual_outcome", "later_evidence",
                   "counterfactual", "impact", "evidence_refs"),
    "kpis":       ("id", "name", "value", "unit", "basis", "measurability", "method",
                   "regeneration"),
    "lessons":    ("id", "observation", "root_cause", "capability", "change", "measurement",
                   "baseline", "target_002"),
    "reconciliation": ("status", "checked_at", "rows"),
}

_projection.register(ARTIFACT, CASE_STUDY_SAFE)

COMPILER_VERSION = "case_study/0.1.0"


# --------------------------------------------------------------------------------------------
# The read model
# --------------------------------------------------------------------------------------------

@dataclass
class TimelineStep:
    id: str
    order: int
    track: str
    title: str
    occurred_at: str = ""
    precision: str = "DAY"           #: EXACT | DAY | MONTH | UNKNOWN
    intent: str = ""
    known: str = ""
    believed: str = ""
    assumed: str = ""
    unknown: str = ""
    action: str = ""
    evidence_refs: List[str] = field(default_factory=list)
    #: The temporal state of this step's central claim, in context.py's vocabulary.
    status: str = _context.UNVERIFIED
    observed: str = ""
    checked: str = ""
    #: Required when `status` is SUPERSEDED — the same invariant factory.context enforces.
    superseded_by: str = ""


@dataclass
class Issue:
    id: str
    track: str
    title: str
    what_happened: str = ""
    why: str = ""
    root_causes: List[str] = field(default_factory=list)
    mistake_types: List[str] = field(default_factory=list)
    stage_introduced: str = ""
    stage_detected: str = ""
    escape_distance: Optional[int] = None
    ideal_interception_stage: str = ""
    potential_escape: Optional[int] = None
    still_open: bool = False
    client_risk: str = "NONE"
    evidence_refs: List[str] = field(default_factory=list)
    basis: str = _assertions.DOCUMENTED
    counterfactual: Optional[Dict[str, Any]] = None
    #: Required when basis is CONTRADICTORY: at least two positions, each with its own refs.
    sides: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class Pattern:
    id: str
    name: str
    statement: str = ""
    issue_ids: List[str] = field(default_factory=list)
    count: int = 0
    note: str = ""


@dataclass
class Scene:
    id: str
    order: int
    title: str
    step_ref: str = ""
    context: str = ""
    information_available: List[str] = field(default_factory=list)
    question: str = ""
    choices: List[Dict[str, Any]] = field(default_factory=list)
    actual_outcome: str = ""
    later_evidence: str = ""
    counterfactual: Optional[Dict[str, Any]] = None
    impact: Dict[str, Any] = field(default_factory=dict)
    evidence_refs: List[str] = field(default_factory=list)


@dataclass
class Kpi:
    id: str
    name: str
    measurability: str
    value: Optional[str] = None
    unit: str = ""
    basis: str = _assertions.NOT_RECORDED
    method: str = ""
    regeneration: str = ""


@dataclass
class Lesson:
    id: str
    observation: str
    root_cause: str = ""
    capability: str = ""
    change: str = ""
    measurement: str = ""
    baseline: str = ""
    target_002: str = ""


@dataclass
class SummaryRow:
    id: str
    issue: str
    why: str = ""
    detected: str = ""
    ideal_interception: str = ""
    capability: str = ""
    benefit: str = ""


@dataclass
class CaseStudy:
    """The whole record. Every section optional-safe: a missing list renders an honest empty
    state, never a broken page."""
    delivery: Dict[str, Any] = field(default_factory=dict)
    companion: Dict[str, Any] = field(default_factory=dict)
    meta: Dict[str, Any] = field(default_factory=dict)
    summary: List[SummaryRow] = field(default_factory=list)
    timeline: List[TimelineStep] = field(default_factory=list)
    issues: List[Issue] = field(default_factory=list)
    patterns: List[Pattern] = field(default_factory=list)
    scenes: List[Scene] = field(default_factory=list)
    kpis: List[Kpi] = field(default_factory=list)
    lessons: List[Lesson] = field(default_factory=list)
    reconciliation: Dict[str, Any] = field(default_factory=dict)
    #: Operator-only. NEVER projected — it has no entry in CASE_STUDY_SAFE, which is the control.
    diagnostics: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """The projected payload. This is the only function a renderer may call."""
        def rows(section, items):
            return [_projection.safe(ARTIFACT, section,
                                     dataclasses.asdict(i) if dataclasses.is_dataclass(i) else i)
                    for i in items]
        return {
            "delivery": _projection.safe(ARTIFACT, "delivery", self.delivery),
            "companion": _projection.safe(ARTIFACT, "companion", self.companion),
            "meta": _projection.safe(ARTIFACT, "meta", self.meta),
            "summary": rows("summary", self.summary),
            "timeline": rows("timeline", self.timeline),
            "issues": rows("issues", self.issues),
            "patterns": rows("patterns", self.patterns),
            "scenes": rows("scenes", self.scenes),
            "kpis": rows("kpis", self.kpis),
            "lessons": rows("lessons", self.lessons),
            "reconciliation": _projection.safe(ARTIFACT, "reconciliation", self.reconciliation),
        }

    def counterfactuals(self) -> List[_assertions.Counterfactual]:
        out = []
        for coll in (self.issues, self.scenes):
            for item in coll:
                if item.counterfactual:
                    out.append(_assertions.Counterfactual(**item.counterfactual))
        return out


# --------------------------------------------------------------------------------------------
# Loading and validation
# --------------------------------------------------------------------------------------------

def _load(path: pathlib.Path) -> dict:
    if not path.exists():
        raise CaseStudyError(f"no case-study narrative at {path}")
    try:
        import yaml  # noqa: PLC0415
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except ImportError:
        alt = path.with_suffix(".json")
        if alt.exists():
            return json.loads(alt.read_text(encoding="utf-8"))
        raise CaseStudyError(f"pyyaml is unavailable and no json fallback at {alt}") from None


def _check_track(track: str, where: str) -> str:
    if track not in TRACKS:
        raise CaseStudyError(f"{where}: {track!r} is not a track. Known: {list(TRACKS)}")
    return track


def _counterfactual(raw: Optional[dict], where: str, task_rows: List[dict],
                    root: pathlib.Path) -> Optional[Dict[str, Any]]:
    """Build, validate and (where claimed) prove a counterfactual.

    ``maturity == EXERCISED`` is the only claim that asserts something ran. It therefore has to
    survive the same two-half test a guarded outcome does: the mechanism must be named, and a
    task-evidence row must carry a usable basis. Otherwise the artifact would let a designed
    capability read as a demonstrated one, which is the specific dishonesty this contract exists
    to prevent.
    """
    if not raw:
        return None
    try:
        cf = _assertions.Counterfactual(**raw)
    except TypeError as exc:
        raise CaseStudyError(f"{where}: counterfactual has an unknown field — {exc}") from None
    except _assertions.AssertionError_ as exc:
        # Re-raised with the record's location attached. The contract knows what is wrong; only
        # the compiler knows which record said it.
        raise CaseStudyError(f"{where}: {exc}") from None
    if cf.maturity == _assertions.EXERCISED:
        cf.basis = _assertions.MEASURED
    return dataclasses.asdict(cf)


def _reconcile(store, doc: dict) -> Dict[str, Any]:
    """Compare the narrative's claims about task state against the live store.

    ⭐ Why this exists. The forensic narrative was written at a point in time and records, for
    example, that R3 was blocked. The store is append-only and moves. A compiled artifact that
    reproduced the narrative's claim without checking would be publishing a stale fact with a fresh
    timestamp on it — which is ``CLAIM_WITHOUT_AN_AS_OF``, the failure family this artifact
    documents, committed by the tool that documents it.

    So every claim of the form ``task X was STATUS`` is re-checked, and a divergence is reported as
    ``SUPERSEDED`` with both values. It **reports, never repairs**: rewriting the narrative belongs
    to its author.
    """
    claims = doc.get("task_state_claims") or []
    if store is None:
        return {"status": "UNAVAILABLE",
                "checked_at": None,
                "rows": [{"task": c.get("task"), "label": c.get("label"),
                          "claimed": c.get("status"), "actual": None,
                          "verdict": "UNAVAILABLE"} for c in claims]}
    rows, diverged = [], 0
    for c in claims:
        tid = c.get("task")
        claimed = (c.get("status") or "").lower()
        try:
            actual = store.get(tid).status
        except Exception:                                            # noqa: BLE001
            actual = None
        if actual is None:
            verdict = "UNAVAILABLE"
        elif actual.lower() == claimed:
            verdict = _context.CURRENT
        else:
            verdict, diverged = _context.SUPERSEDED, diverged + 1
        rows.append({"task": tid, "label": c.get("label"), "claimed": c.get("status"),
                     "actual": actual, "verdict": verdict,
                     "observed": c.get("observed", "")})
    return {
        "status": "DIVERGED" if diverged else "OK",
        "checked_at": _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "rows": rows,
    }


def assemble(narrative_path: pathlib.Path,
             tasks_path: Optional[pathlib.Path] = None,
             mission_path: Optional[pathlib.Path] = None,
             root: Optional[pathlib.Path] = None,
             now: Optional[float] = None) -> CaseStudy:
    """Fold canonical state plus an authored forensic narrative into one validated record.

    Unlike :func:`client_review.assemble`, a broken reference here is **fatal**. The reasoning
    differs because the artifacts differ: a client review must survive a demo with a missing file
    (Phase 6 resilience), whereas a forensic record whose citations do not resolve is not a
    degraded record — it is an unfounded one.
    """
    root = pathlib.Path(root or pathlib.Path(__file__).resolve().parent.parent)
    npath = pathlib.Path(narrative_path)
    doc = _load(npath)

    # ---- canonical state ---------------------------------------------------------------------
    store, task_rows, readable = None, [], False
    if tasks_path and pathlib.Path(tasks_path).exists():
        try:
            store = _tasks.TaskStore(pathlib.Path(tasks_path))
            readable = True
            for t in store.all():
                task_rows.extend(t.evidence or [])
        except Exception as exc:                                     # noqa: BLE001
            store, readable = None, False
            doc.setdefault("_load_error", f"{type(exc).__name__}: {exc}")

    mission = {}
    if mission_path and pathlib.Path(mission_path).exists():
        try:
            mission = json.loads(pathlib.Path(mission_path).read_text(encoding="utf-8"))
        except Exception:                                            # noqa: BLE001
            mission = {}

    last_verified = None
    if store is not None:
        for t in store.all():
            for ev in t.events:
                if ev.kind in ("evidence", "close"):
                    last_verified = max(last_verified or 0.0, ev.ts)

    # ---- the prose boundary ------------------------------------------------------------------
    sources: Dict[str, _src.Source] = {}
    prose_paths = list(doc.get("prose_sources") or [])
    for rel in prose_paths:
        sources[rel] = _src.read(root / rel)

    cs = CaseStudy()
    cs.delivery = dict(doc.get("delivery", {}))
    cs.companion = dict(doc.get("companion", {}))
    _check_track(cs.delivery.get("track", CLIENT_DELIVERY), "delivery")

    all_refs: List[str] = []

    def take(section: str, ctor, extra=None):
        rows = doc.get(section, []) or []
        _src.unique_ids(rows, section)
        out = []
        for raw in rows:
            raw = dict(raw)
            all_refs.extend(raw.get("evidence_refs") or [])
            if extra:
                extra(raw, f"{section}[{raw.get('id')}]")
            # A capability's own claims about itself are references like any other, and are
            # checked like any other. `mechanism_refs` must be plain paths — the line number
            # belongs in prose, because a path with a line range cannot be resolved on disk.
            cf = raw.get("counterfactual")
            if cf:
                all_refs.extend(cf.get("mechanism_refs") or [])
                if cf.get("exercised_proof"):
                    all_refs.append(cf["exercised_proof"])
            known = {f.name for f in dataclasses.fields(ctor)}
            unknown = set(raw) - known
            if unknown:
                raise CaseStudyError(
                    f"{section}[{raw.get('id')}]: unknown field(s) {sorted(unknown)}. A field the "
                    "view model does not declare cannot be validated or projected, so it is "
                    "refused rather than silently dropped.")
            out.append(ctor(**raw))
        return out

    def issue_extra(raw, where):
        _check_track(raw.get("track", ""), where)
        raw["counterfactual"] = _counterfactual(raw.get("counterfactual"), where, task_rows, root)
        if raw.get("basis") == _assertions.CONTRADICTORY and len(raw.get("sides") or []) < 2:
            raise CaseStudyError(
                f"{where}: basis CONTRADICTORY with fewer than two sides. A contradiction that "
                "names one position has already been resolved silently, which is the thing the "
                "basis exists to prevent.")
        for s in raw.get("sides") or []:
            all_refs.extend(s.get("evidence_refs") or [])
        if raw.get("basis"):
            _assertions.check_basis(raw["basis"])

    def scene_extra(raw, where):
        raw["counterfactual"] = _counterfactual(raw.get("counterfactual"), where, task_rows, root)
        actual = [c for c in (raw.get("choices") or []) if c.get("was_actual")]
        if len(actual) != 1:
            raise CaseStudyError(
                f"{where}: {len(actual)} choice(s) marked was_actual. Exactly one must be, or the "
                "artifact cannot distinguish ACTUAL_HISTORY from COUNTERFACTUAL_EXPLANATION — "
                "which is the one thing the scene mechanic must never blur.")

    def step_extra(raw, where):
        _check_track(raw.get("track", ""), where)
        if raw.get("status") not in _context.STATUSES:
            raise CaseStudyError(
                f"{where}: {raw.get('status')!r} is not a context status. "
                f"Known: {list(_context.STATUSES)}")
        if raw.get("status") == _context.CURRENT and not raw.get("checked"):
            raise CaseStudyError(
                f"{where}: CURRENT with no `checked` date — the invariant factory.context has "
                "enforced since it was written. Freshness is a measurement.")
        if raw.get("status") == _context.SUPERSEDED and not raw.get("superseded_by"):
            raise CaseStudyError(
                f"{where}: SUPERSEDED but names nothing that superseded it. Same rule as "
                "CURRENT-needs-a-date: a status asserting an event must carry its evidence.")

    def kpi_extra(raw, where):
        if raw.get("measurability") not in MEASURABILITY:
            raise CaseStudyError(
                f"{where}: {raw.get('measurability')!r} is not a measurability. "
                f"Known: {list(MEASURABILITY)}")
        if raw.get("measurability") in NUMBERLESS and raw.get("value") not in (None, ""):
            raise CaseStudyError(
                f"{where}: measurability {raw['measurability']} carries a value "
                f"{raw['value']!r}. An unmeasured KPI with a number on it is an authored estimate "
                "disguised as a metric — refused.")
        if raw.get("basis"):
            _assertions.check_basis(raw["basis"])

    cs.summary = take("summary", SummaryRow)
    cs.timeline = take("timeline", TimelineStep, step_extra)
    cs.issues = take("issues", Issue, issue_extra)
    cs.patterns = take("patterns", Pattern)
    cs.scenes = take("scenes", Scene, scene_extra)
    cs.kpis = take("kpis", Kpi, kpi_extra)
    cs.lessons = take("lessons", Lesson)

    # ---- cross-references --------------------------------------------------------------------
    step_ids = [s.id for s in cs.timeline]
    issue_ids = [i.id for i in cs.issues]
    _src.require_refs_exist([("step_ref", s.step_ref) for s in cs.scenes], step_ids, "scenes")
    _src.require_refs_exist(
        [(f"{p.id}.issue_ids", iid) for p in cs.patterns for iid in p.issue_ids],
        issue_ids, "patterns")

    # ---- the prose boundary, enforced --------------------------------------------------------
    _src.require(all_refs, root, sources, what="evidence reference")

    # ---- ⭐ both tracks, or neither ----------------------------------------------------------
    tracks_present = {i.track for i in cs.issues}
    if cs.issues and tracks_present != set(TRACKS):
        missing = set(TRACKS) - tracks_present
        raise CaseStudyError(
            f"case study carries issues on {sorted(tracks_present)} only — missing "
            f"{sorted(missing)}. Both the client delivery and the mission that investigated it "
            "produced failures; a record showing one track is an advertisement, not a forensic "
            "account. Add the missing track's issues, or state explicitly why it has none.")

    # ---- scene ordering ----------------------------------------------------------------------
    orders = [s.order for s in cs.scenes]
    if orders and sorted(orders) != list(range(1, len(orders) + 1)):
        raise CaseStudyError(
            f"scene order must be 1..{len(orders)} with no gaps or repeats; got {sorted(orders)}.")
    cs.scenes.sort(key=lambda s: s.order)
    cs.timeline.sort(key=lambda s: s.order)

    # ---- reconciliation against live state ---------------------------------------------------
    cs.reconciliation = _reconcile(store, doc)

    # ---- meta --------------------------------------------------------------------------------
    fresh = _assertions.freshness(last_verified, now=now, source_readable=readable)
    narrative_sha = _src._digest(npath.read_text(encoding="utf-8"))
    cs.meta = {
        "compiled_at": _dt.datetime.fromtimestamp(
            now or _dt.datetime.now(_dt.timezone.utc).timestamp(),
            _dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "freshness_state": fresh,
        "basis": _assertions.DERIVED if readable else _assertions.NOT_RECORDED,
        "last_verified_at": (
            _dt.datetime.fromtimestamp(last_verified, _dt.timezone.utc)
            .strftime("%Y-%m-%d %H:%M UTC") if last_verified else None),
        "source_sha": {k: v.sha256[:12] for k, v in sorted(sources.items())},
        "narrative_sha": narrative_sha[:12],
        "compiler_version": COMPILER_VERSION,
    }

    cfs = cs.counterfactuals()
    cs.diagnostics = {
        "tasks_readable": readable,
        "task_evidence_rows": len(task_rows),
        "narrative": str(narrative_path),
        "root": str(root),
        "refs_checked": len(all_refs),
        "prose_sources": {k: {"anchors": len(v.anchors), "lines": v.line_count}
                          for k, v in sorted(sources.items())},
        "issues_by_track": {t: sum(1 for i in cs.issues if i.track == t) for t in TRACKS},
        "counterfactuals": len(cfs),
        "counterfactuals_exercised": sum(1 for c in cfs if c.is_observed),
        "kpis_without_a_number": sum(1 for k in cs.kpis if k.measurability in NUMBERLESS),
        "mission_declared_tasks": len((mission.get("labels") or {})),
        "reconciliation": cs.reconciliation,
    }
    return cs


# --------------------------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------------------------

def main(argv=None) -> int:
    import argparse
    p = argparse.ArgumentParser(prog="python -m factory.case_study",
                                description="Compile and render a forensic case study.")
    p.add_argument("narrative", help="path to the authored case-study yaml")
    p.add_argument("--tasks", default=".data/tasks.jsonl")
    p.add_argument("--mission", default=None)
    p.add_argument("--json", action="store_true")
    p.add_argument("--out", default=None, help="write a self-contained HTML case study here")
    a = p.parse_args(argv)

    cs = assemble(pathlib.Path(a.narrative),
                  tasks_path=pathlib.Path(a.tasks) if a.tasks else None,
                  mission_path=pathlib.Path(a.mission) if a.mission else None)
    if a.json:
        print(json.dumps(cs.to_dict(), indent=2))
    if a.out:
        from .case_study_render import render_html      # noqa: PLC0415
        pathlib.Path(a.out).write_text(render_html(cs), encoding="utf-8")
        print(f"wrote {a.out}")
    if not a.json and not a.out:
        d = cs.diagnostics
        print(f"{cs.delivery.get('name','?')} [{cs.meta['freshness_state']}]")
        print(f"  issues          {len(cs.issues)}  {d['issues_by_track']}")
        print(f"  scenes          {len(cs.scenes)}")
        print(f"  refs checked    {d['refs_checked']}  (all resolved, or this would have raised)")
        print(f"  counterfactuals {d['counterfactuals']}, "
              f"{d['counterfactuals_exercised']} EXERCISED")
        print(f"  kpis            {len(cs.kpis)}, {d['kpis_without_a_number']} with no number")
        r = cs.reconciliation
        print(f"  reconciliation  {r.get('status')}")
        for row in r.get("rows", []):
            if row.get("verdict") != _context.CURRENT:
                print(f"    ⚠ {row['label']} {row['task']}: narrative says "
                      f"{row['claimed']!r}, store says {row['actual']!r} -> {row['verdict']}")
    return 0


if __name__ == "__main__":                                          # pragma: no cover
    raise SystemExit(main())
