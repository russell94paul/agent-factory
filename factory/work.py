"""Canonical work — one view model over the TaskStore, so arbitrary work is operable.

⭐ **This is not a second task system.** Every field below is read from, or written to,
`.data/tasks.jsonl` through :class:`factory.tasks.TaskStore`. There is no new ledger, no queue
database and no UI-only work object. `TaskStore` stays the canonical truth; this module is the
join that makes it *operable* — it adds derivation (readiness, target resolution, conflicts) and
nothing that could disagree with the store.

## ⛔ The premise this module was written to kill

P0's READY projection required `.data/missions/<id>.json`. A mission manifest carried three things
the store could not: a **readable label** for an opaque `uuid4[:8]` id, a **contract**
(resource claim, access, model) and a **membership list**. So any new piece of work needed a
bespoke Python script to construct a manifest before the Switchboard could see it at all — measured
as the `MISSION_MANIFEST_REQUIRED` / `MANIFEST_CREATION_TOOL_MISSING` seams during dogfooding.

The seam chosen here is the smallest one that removes it:

    caller-chosen task id   →  the label IS the id, so no mapping is needed
    task.contract           →  the contract lives on the task
    task.depends_on         →  the graph lives on the task
    manifest (optional)     →  an OVERLAY for the one legacy mission, not a requirement

A manifest is still read when present, and still supplies labels and contracts for the historical
`marketing-model-reconstruction-v1` mission whose tasks have opaque ids. Work created after P1
needs none. Both kinds render through the same :class:`Work` rows, which is what stops the estate
growing a second model of the same thing.

## ⛔ UNKNOWN is not PASS

:func:`readiness` returns a *reason per check*, and a check that could not be measured returns
``UNMEASURED`` — never ``True``. `is_ready` is the AND over checks that all returned an explicit
pass. This is the same rule `factory.readiness` enforces for gates, applied to work: an absent
measurement rendering as a green tick is how a page teaches an operator to trust it wrongly.
"""
from __future__ import annotations

import dataclasses
import pathlib
import re
from typing import Any, Dict, List, Optional

from . import repo as _repo
from . import tasks as _tasks
from .tasks import TaskStore

# ------------------------------------------------------------------ readiness verdicts
#
# Four, not two. `NOT_APPLICABLE` and `UNMEASURED` both render as "not a pass" and mean opposite
# things: one is a check that correctly does not apply, the other is a check that could not be run.
# Collapsing them is how a measurement gap becomes a claim about the work.
PASS, FAIL, UNMEASURED, NOT_APPLICABLE = "PASS", "FAIL", "UNMEASURED", "N/A"

#: Work states the operator acts on. Distinct from `TaskStore`'s five, for the reason
#: `switchboard` already states: the store says what a task *is*, these say what can be *done*.
DRAFT = "DRAFT"
READY = "READY"
BLOCKED = "BLOCKED"
RUNNING = "RUNNING"
NEEDS_HUMAN = "NEEDS_HUMAN"
WAITING_GATE = "WAITING_GATE"
DONE = "DONE"
ABANDONED = "ABANDONED"

#: state -> the ONE primary action. Button soup is a design failure: an operator scanning a card at
#: 2am on a phone should read one verb, not choose between six.
PRIMARY_ACTION = {
    DRAFT:       "VALIDATE",
    BLOCKED:     "RESOLVE",
    NEEDS_HUMAN: "RESPOND",
    READY:       "START SYNCED",
    RUNNING:     "OPEN",
    WAITING_GATE: "REVIEW",
    DONE:        "REVIEW OUTCOME",
    ABANDONED:   "—",
}

#: Compact visibility marks. The glyph carries the value without colour, so a screenshot, a
#: greyscale render and a colour-blind reader all still see PRIVATE.
VISIBILITY_MARK = {
    _tasks.PUBLIC:          ("\U0001F310", "PUBLIC"),
    _tasks.PRIVATE:         ("\U0001F512", "PRIVATE"),
    _tasks.REVIEW_REQUIRED: ("◐", "REVIEW"),
}


@dataclasses.dataclass
class Check:
    """One readiness question and its measured answer. `verdict` is never a bare bool."""
    name: str
    verdict: str
    detail: str = ""

    @property
    def ok(self) -> bool:
        """⛔ PASS only. `NOT_APPLICABLE` is handled by the caller, never silently promoted."""
        return self.verdict == PASS


@dataclasses.dataclass
class Work:
    """One operable piece of work. Every field is read from the store or derived from it."""
    id: str
    title: str
    objective: str = ""
    repo: str = ""
    status: str = _tasks.OPEN
    visibility: str = _tasks.DEFAULT_VISIBILITY
    depends_on: List[str] = dataclasses.field(default_factory=list)
    depends_on_artifacts: List[Dict[str, Any]] = dataclasses.field(default_factory=list)
    conflicts_with: List[str] = dataclasses.field(default_factory=list)
    contract: Dict[str, Any] = dataclasses.field(default_factory=dict)
    evidence: int = 0
    evidence_refs: List[str] = dataclasses.field(default_factory=list)
    session_id: Optional[str] = None
    parent: Optional[str] = None
    owner: Optional[str] = None
    #: MANUAL | GUARDED | AUTO. Defaults closed; see `tasks.DEFAULT_AUTONOMY`.
    autonomy: str = _tasks.DEFAULT_AUTONOMY
    #: MANUAL_START | AUTO_START | None -- how the last start was decided.
    start_mode: Optional[str] = None
    #: The operator's stop. Outranks the policy, always.
    autonomy_paused: bool = False
    #: Live `block` holds from the store that are NOT satisfied dependencies -- an explicit
    #: "this cannot proceed", including holds naming something outside the task store.
    blocked_by: List[str] = dataclasses.field(default_factory=list)
    #: True when this row's label/contract came from a mission manifest rather than the task.
    from_manifest: bool = False
    mission: str = ""
    #: Filled by `project()`.
    state: str = DRAFT
    checks: List[Check] = dataclasses.field(default_factory=list)
    blocked_reason: str = ""
    needs: List[dict] = dataclasses.field(default_factory=list)

    @property
    def is_ready(self) -> bool:
        return self.state == READY

    @property
    def action(self) -> str:
        return PRIMARY_ACTION.get(self.state, "—")

    @property
    def visibility_mark(self) -> tuple:
        return VISIBILITY_MARK.get(self.visibility, ("●", self.visibility or "UNSET"))

    def to_dict(self) -> dict:
        d = dataclasses.asdict(self)
        d["action"] = self.action
        d["is_ready"] = self.is_ready
        d["visibility_glyph"], d["visibility_label"] = self.visibility_mark
        allowed, reasons = guarded_start(self)
        d["guarded_start_allowed"] = allowed
        d["guarded_stop_reasons"] = reasons
        return d


# ---------------------------------------------------------------------------- the store


def store_path() -> pathlib.Path:
    """The shared task store — `repo.data()`, never a path derived from this module's location.

    See `factory/repo.py`: a store resolved per-worktree is not shared, and work created in one
    lane would be invisible to every other one.
    """
    return _repo.data() / "tasks.jsonl"


def open_store() -> TaskStore:
    return TaskStore(store_path())


# ------------------------------------------------------------------------ construction


_SLUG = re.compile(r"[^A-Za-z0-9]+")


def slug_id(title: str, prefix: str = "") -> str:
    """A readable, addressable id derived from the title. Deterministic, so it can be predicted."""
    base = _SLUG.sub("-", (title or "").strip()).strip("-").upper()[:48] or "WORK"
    return f"{prefix}-{base}".strip("-") if prefix else base


def create(title: str, *, objective: str = "", repo: str = "", visibility: str = _tasks.PRIVATE,
           work_id: Optional[str] = None, depends_on: Optional[List[str]] = None,
           artifacts: Optional[List[Dict[str, Any]]] = None,
           resource_claim: str = "", access: str = "", actor: str = "operator",
           parent: Optional[str] = None, store: Optional[TaskStore] = None) -> Work:
    """Create canonical work through the operator path. No manifest, no bespoke script.

    ⛔ Dependencies are written as DURABLE `depend` edges, never as `block` status events. A
    `block` is erased by its `unblock` and the graph forgets its own shape; the edge has to
    outlive its own satisfaction or the DAG is only correct while it is unfinished.

    The order matters: the task exists before any edge points at it, so a failure part-way leaves
    a real piece of work with fewer edges rather than an edge to nothing.
    """
    st = store if store is not None else open_store()
    contract = {}
    if resource_claim:
        contract["resource_claim"] = resource_claim
        contract["access"] = (access or "WRITE").upper()
    tid = st.create(title=title, actor=actor, parent=parent,
                    tid=work_id or slug_id(title), objective=objective, repo=repo,
                    visibility=visibility, contract=contract)
    for dep in (depends_on or []):
        st.depend(tid, dep, actor=actor)
    for a in (artifacts or []):
        st.depend_on_artifact(tid, ref=a["ref"], kind=a.get("kind", "artifact"),
                              satisfied_when=a.get("satisfied_when", "EXISTS"), actor=actor)
    return next(w for w in project(store=st) if w.id == tid)


# ------------------------------------------------------------------------- the projection


def _manifest_overlay(manifests: List[dict]) -> Dict[str, dict]:
    """task id -> {label, contract, mission} for the legacy manifested mission.

    ⚠ An OVERLAY, not a requirement. It exists so the historical mission — whose tasks carry
    opaque `uuid4[:8]` ids and whose contracts were only ever written in the manifest — keeps
    rendering exactly as it did in P0. Nothing created after P1 needs an entry here, and the
    absence of a manifest is no longer a reason for a task to be invisible.
    """
    out: Dict[str, dict] = {}
    for m in manifests or []:
        labels = m.get("labels") or {}
        contracts = m.get("contracts") or {}
        # A manifest MAY declare the repo its tasks act on. `marketing-model-reconstruction-v1`
        # does not, and it is deliberately not defaulted here: inferring "the repo the manifest
        # file happens to live in" is the inherit-the-target move, and it would turn an
        # unanswered question into a rendered green.
        mrepo = m.get("repo") or ""
        for label, tid in labels.items():
            out[tid] = {"label": label, "contract": contracts.get(tid, {}) or {},
                        "repo": mrepo, "mission": m.get("mission") or m.get("_id", "")}
        mt = m.get("mission_task")
        if mt and mt not in out:
            out[mt] = {"label": m.get("_id", mt), "contract": {},
                       "mission": m.get("mission") or m.get("_id", "")}
    return out


def _legacy_edges(task: _tasks.Task, known: set) -> List[str]:
    """Dependency edges recovered from the append-only `block` event log.

    ⛔ Not `Task.blocked_by` — `unblock()` deletes from that field, so a mission whose
    dependencies are all satisfied renders as a set of unrelated tasks. Used ONLY for rows that
    predate `depend`; new work carries real edges and never reaches this.
    """
    seen, deps = set(), []
    for ev in task.events:
        if ev.kind != "block":
            continue
        by = ev.data.get("by")
        if by and by in known and by not in seen:
            seen.add(by)
            deps.append(by)
    return deps


def _conflicts(rows: Dict[str, Work]) -> None:
    """Fill `conflicts_with` from declared resource claims. Two READERS are not a conflict.

    Over-reporting a conflict and under-reporting one end the same way — a scheduler nobody
    believes. A task with NO declared claim conflicts with nothing here, which is an absence of a
    declaration and not evidence of isolation; `project()` surfaces that as a check, not silence.
    """
    for a in rows.values():
        ra = (a.contract or {}).get("resource_claim")
        if not ra:
            continue
        wa = (a.contract or {}).get("access") == "WRITE"
        for b in rows.values():
            if b.id == a.id:
                continue
            cb = b.contract or {}
            if cb.get("resource_claim") != ra:
                continue
            if wa or cb.get("access") == "WRITE":
                a.conflicts_with.append(b.id)
        a.conflicts_with = sorted(set(a.conflicts_with))


def _artifact_ok(spec: Dict[str, Any]) -> Check:
    """Is an artefact dependency satisfied? Measured against the disk, from the shared root.

    Relative refs resolve against `repo.primary()` so the answer does not depend on which worktree
    asked — the same reason `.data/` resolves there.
    """
    ref = str(spec.get("ref") or "")
    if not ref:
        return Check("artifact", UNMEASURED, "an artefact dependency with no ref")
    p = pathlib.Path(ref)
    if not p.is_absolute():
        p = _repo.primary() / ref
    try:
        exists = p.exists()
    except OSError as exc:
        return Check("artifact", UNMEASURED, f"could not stat {ref}: {exc}")
    return (Check("artifact", PASS, f"{ref} exists") if exists
            else Check("artifact", FAIL, f"{ref} does not exist"))


def readiness(w: Work, rows: Dict[str, Work], running: set) -> List[Check]:
    """Every readiness question, each with an explicit verdict. READY is the AND of the passes.

    ⭐ **Readiness is derived here and nowhere else.** There is no `status=ready` an operator can
    choose, because a chosen readiness is an opinion wearing a measurement's clothes — and the one
    thing this page exists to stop is an operator starting work whose dependencies are unmet.

    The checks, and why each is a separate row rather than one boolean:

    - **dependencies** — every `depends_on` task closed `done`.
    - **artifacts** — every durable artefact dependency present on disk.
    - **target** — the work resolves to a real store row (see :func:`resolve`).
    - **repo** — a repository is named. Without one there is no worktree to spawn into.
    - **conflict** — no live writer holds the same declared resource.
    - **contract** — a resource claim is DECLARED. `UNMEASURED` when absent, never PASS:
      absence of a declaration is not evidence of isolation.
    - **gate** — a blocking gate. `NOT_APPLICABLE` when none is declared.
    """
    checks: List[Check] = []

    unmet = [d for d in w.depends_on if (rows.get(d).status if rows.get(d) else None) != _tasks.DONE]
    missing = [d for d in w.depends_on if d not in rows]
    if missing:
        checks.append(Check("dependencies", UNMEASURED,
                            "depends on " + ", ".join(missing) + " which is not in the store, so "
                            "whether it is finished cannot be measured"))
    elif unmet:
        checks.append(Check("dependencies", FAIL, "waits on " + ", ".join(unmet)))
    elif w.depends_on:
        checks.append(Check("dependencies", PASS, f"all {len(w.depends_on)} satisfied"))
    else:
        checks.append(Check("dependencies", NOT_APPLICABLE, "none declared"))

    if w.depends_on_artifacts:
        subs = [_artifact_ok(a) for a in w.depends_on_artifacts]
        bad = [c for c in subs if c.verdict == FAIL]
        unk = [c for c in subs if c.verdict == UNMEASURED]
        if bad:
            checks.append(Check("artifacts", FAIL, "; ".join(c.detail for c in bad)))
        elif unk:
            checks.append(Check("artifacts", UNMEASURED, "; ".join(c.detail for c in unk)))
        else:
            checks.append(Check("artifacts", PASS, f"all {len(subs)} present"))
    else:
        checks.append(Check("artifacts", NOT_APPLICABLE, "none declared"))

    # ⛔ An explicit `block` hold. Found by dogfooding P1 against real work: blocking
    # MARKETING-MODEL-FINALIZATION-01 on a human credential decision wrote `status=blocked` and
    # `blocked_by=[...]` to the store, and the projection still rendered it READY with a live
    # START SYNCED button. `_state_for` only knew about done/abandoned/claimed, and `_edges`
    # drops a `block` naming anything not in the store -- which is exactly how a hold on a
    # PERSON rather than a task disappears. A readiness layer whose whole purpose is to refuse
    # cannot be blind to the store's own word for refusal.
    if w.blocked_by:
        checks.append(Check("hold", FAIL, "explicitly blocked on " + ", ".join(w.blocked_by)))
    else:
        checks.append(Check("hold", NOT_APPLICABLE, "no explicit hold"))

    checks.append(Check("target", PASS, f"resolves to store row {w.id}"))

    # ⚠ UNMEASURED, not FAIL. A task that never declared a repository has not failed a check —
    # nobody ever asked it the question. It still cannot be READY, because START SYNCED has no
    # worktree to open, but the operator's action is to *declare* the repo (DRAFT -> VALIDATE),
    # not to unblock something. Every mission task predating P1 is in exactly this position.
    checks.append(Check("repo", PASS, w.repo) if w.repo
                  else Check("repo", UNMEASURED,
                             "no repository declared — there is no worktree to open, and which "
                             "repo it meant cannot be inferred from the task"))

    live_clash = sorted(c for c in w.conflicts_with if c in running)
    if live_clash:
        claim = (w.contract or {}).get("resource_claim") or "the same resource"
        checks.append(Check("conflict", FAIL,
                            f"a live writer holds {claim} — " + ", ".join(live_clash)))
    else:
        checks.append(Check("conflict", PASS, "no live conflicting writer"))

    if (w.contract or {}).get("resource_claim"):
        checks.append(Check("contract", PASS, w.contract["resource_claim"]))
    else:
        checks.append(Check("contract", UNMEASURED,
                            "no resource claim declared — reported conflict-free, which is an "
                            "absence of a declaration, not evidence of isolation"))

    gate = (w.contract or {}).get("blocking_gate")
    checks.append(Check("gate", FAIL, f"blocked by gate {gate}") if gate
                  else Check("gate", NOT_APPLICABLE, "none declared"))
    return checks


def _state_for(w: Work) -> str:
    """The one place a piece of work becomes READY. Order of the tests is the design.

    1. Terminal states are terminal — liveness never changes them.
    2. **A written question outranks everything**, including a live process: the operator's next
       act is the answer, not the observation that something is running.
    3. `claimed` is RUNNING — it is what the store says, and the agent writes the store.
    4. A `FAIL` on any check is BLOCKED, with that check's reason.
    5. ⛔ An `UNMEASURED` check is **DRAFT, never READY**. It is the reason DRAFT exists as a
       state rather than as "not started": the work is not refused, it is *not yet measurable*,
       and the operator's action is to make it measurable rather than to wait.
    """
    if w.status == _tasks.DONE:
        return DONE
    if w.status == _tasks.ABANDONED:
        return ABANDONED
    if w.needs:
        return NEEDS_HUMAN
    # ⛔ Before RUNNING. A task that was claimed and then blocked is NOT running: the store's
    # `block` sets status=blocked over the claim, and reading it as RUNNING would show a live
    # session that does not exist.
    if w.status == _tasks.BLOCKED or w.blocked_by:
        w.blocked_reason = ("explicitly blocked on " + ", ".join(w.blocked_by)
                            if w.blocked_by else "the store holds this task blocked")
        return BLOCKED
    if w.status == _tasks.CLAIMED:
        return RUNNING
    fails = [c for c in w.checks if c.verdict == FAIL]
    if fails:
        gate = [c for c in fails if c.name == "gate"]
        w.blocked_reason = "; ".join(c.detail for c in fails)
        return WAITING_GATE if gate and len(fails) == 1 else BLOCKED
    unk = [c for c in w.checks if c.verdict == UNMEASURED]
    if unk:
        w.blocked_reason = "; ".join(c.detail for c in unk)
        return DRAFT
    return READY


def project(store: Optional[TaskStore] = None, manifests: Optional[List[dict]] = None,
            needs_by_id: Optional[Dict[str, List[dict]]] = None) -> List[Work]:
    """Every piece of canonical work, with derived state. The whole domain layer in one call.

    Reads the store once. Manifests are an optional overlay for labels and contracts; passing
    `None` means "no overlay", not "no work" — which is the seam that made arbitrary work possible.
    """
    st = store if store is not None else open_store()
    overlay = _manifest_overlay(manifests or [])
    needs_by_id = needs_by_id or {}
    all_tasks = st.all()
    known = {t.id for t in all_tasks}

    rows: Dict[str, Work] = {}
    for t in all_tasks:
        ov = overlay.get(t.id) or {}
        contract = dict(ov.get("contract") or {})
        contract.update(t.contract or {})       # the task's own contract wins over the overlay
        deps = list(t.depends_on) or _legacy_edges(t, known)
        rows[t.id] = Work(
            id=t.id, title=t.title, objective=t.objective, repo=t.repo, status=t.status,
            visibility=t.visibility or _tasks.DEFAULT_VISIBILITY,
            depends_on=deps, depends_on_artifacts=list(t.depends_on_artifacts),
            contract=contract, evidence=len(t.evidence),
            evidence_refs=[str(e.get("ref", "")) for e in t.evidence],
            session_id=t.session_id, parent=t.parent, owner=t.owner,
            autonomy=t.autonomy, start_mode=t.start_mode,
            autonomy_paused=bool(t.autonomy_paused),
            blocked_by=list(t.blocked_by),
            from_manifest=bool(ov), mission=ov.get("mission", ""),
            needs=list(needs_by_id.get(t.id) or []))

    _conflicts(rows)
    running = {w.id for w in rows.values() if w.status == _tasks.CLAIMED}
    for w in rows.values():
        w.checks = readiness(w, rows, running)
        w.state = _state_for(w)
    return sorted(rows.values(), key=lambda w: (w.state != NEEDS_HUMAN, w.state != READY, w.id))


# --------------------------------------------------------------------- autonomy policy


#: Contract keys that mean a human must decide before this runs, whatever the policy says. Each is
#: a category the brief names explicitly; they are listed rather than inferred so that adding one
#: is a visible edit rather than a change in behaviour nobody can point at.
_HUMAN_GATE_KEYS = ("blocking_gate", "requires_approval", "approval_required",
                    "security_review", "publication_gate", "budget_ceiling", "risk_ceiling")


def guarded_start(w: "Work") -> tuple:
    """May the system start this WITHOUT a human? Returns (allowed, reasons-it-must-not).

    ⭐ **Deny by default, and every condition below is a stop rather than a score.** The function
    returns True only when it has run out of reasons to say no — there is no threshold, no
    weighting and no "probably fine". An unmeasured condition is a stop, which is the whole
    difference between GUARDED and unattended.

    ⛔ **This decides; it does not act.** P1 deliberately ships no loop that calls this on a timer
    and spawns sessions. The brief's line is "do not implement uncontrolled recursive autonomous
    execution", and the honest way to honour it is that the *policy, the decision and the recorded
    outcome* exist and are inspectable, while the thing that would pull the trigger does not exist
    yet. A GUARDED item today tells the operator it COULD start and why it may; starting it is
    still a tap.

    The stops, in the order the brief names them:
      human gates, security, publication, unresolved conflicts, unknown/unmeasured conditions,
      explicit approval, configured budget/risk boundaries — plus the operator's own pause.
    """
    reasons: List[str] = []
    if w.autonomy_paused:
        reasons.append("autonomy is PAUSED for this work by the operator")
    if w.autonomy == _tasks.MANUAL:
        reasons.append("policy is MANUAL — it waits for an explicit START SYNCED")
    if w.state != READY:
        reasons.append(f"state is {w.state}, not READY")

    for c in w.checks:
        if c.verdict == FAIL:
            reasons.append(f"{c.name} FAILED: {c.detail}")
        elif c.verdict == UNMEASURED:
            # ⭐ The rule that makes GUARDED safe rather than optimistic.
            reasons.append(f"{c.name} is UNMEASURED — an unknown condition is a stop, not a pass")

    contract = w.contract or {}
    for key in _HUMAN_GATE_KEYS:
        if contract.get(key):
            reasons.append(f"contract declares {key}={contract[key]!r} — a human decides")

    if w.visibility != _tasks.PRIVATE:
        # PUBLIC or REVIEW_REQUIRED work touches the publication boundary.
        reasons.append(f"visibility is {w.visibility} — anything that is not PRIVATE crosses the "
                       f"publication boundary and a human decides")
    if w.conflicts_with:
        reasons.append("declares a resource conflict with "
                       + ", ".join(w.conflicts_with[:4]))
    return (not reasons), reasons


# ------------------------------------------------------------------- target resolution


class TargetRefused(Exception):
    """A target that did not resolve canonically. Raised BEFORE any context or spawn."""


def resolve(target: str, works: Optional[List[Work]] = None) -> Work:
    """Resolve an operator-supplied target to canonical work, or REFUSE.

    ⛔ **This is the safety-critical seam, and it fails closed.** The measured P0 defect was that
    an unresolved target fell through to a whole-mission startup packet *still labelled with the
    bogus target* — so a session opened believing it was working on something that does not exist,
    holding context for everything else. The packet's own title said the target's name.

    A target that does not name exactly one row raises. It does not return `None`, because a
    `None` at a call site is one forgotten `if` away from being the old behaviour again, and it
    does not pick the closest match, because guessing which work an operator meant is precisely
    the wrong-session dispatch that `quick_dispatch` already refuses to do.
    """
    t = (target or "").strip()
    if not t:
        raise TargetRefused("REFUSED: no target given. START SYNCED needs a piece of work to "
                            "ground the session in; a session with no target would receive "
                            "whole-mission context labelled as something specific.")
    rows = project() if works is None else works
    exact = [w for w in rows if w.id == t]
    if len(exact) == 1:
        return exact[0]
    ci = [w for w in rows if w.id.lower() == t.lower()]
    if len(ci) == 1:
        return ci[0]
    if len(ci) > 1:
        raise TargetRefused(f"REFUSED: {t!r} matches {len(ci)} pieces of work "
                            f"({', '.join(sorted(w.id for w in ci))}) — it is ambiguous, and "
                            f"picking one would ground a session in work nobody chose.")
    near = sorted(w.id for w in rows if t.lower() in w.id.lower())[:5]
    raise TargetRefused(
        f"REFUSED: {t!r} does not name any canonical work in {store_path()}. "
        + (f"Did you mean: {', '.join(near)}?" if near else
           "No work has a similar id. Create it first — nothing was opened and no context was "
           "compiled."))
