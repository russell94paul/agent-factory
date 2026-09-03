"""Mission presets — a compiler into canonical work, and then it stops existing.

    python -m factory.missions --list
    python -m factory.missions --preset marketing-meeting-v1 --plan     # writes nothing
    python -m factory.missions --preset marketing-meeting-v1 --create
    python -m factory.missions --preset marketing-meeting-v1 --status

⭐ **There is no mission entity, no mission database and no manifest.** A preset is a YAML file
read once; `TaskStore.create` writes the stage's title, objective, repo, visibility and contract
onto the task itself, `depend()` writes the durable edges, and from that moment the projection in
`factory/work.py` is the only thing that knows the mission exists. Nothing here is consulted at
run time, which is the whole reason it cannot become a second source of truth.

The mission's own row is the **parent** of every stage, and that is how run membership is
answered: a stage belongs to the run when `work.parent == <mission id>`. `2da0c097` ("Absorption
backlog") and `.data/missions/marketing-model-reconstruction-v1.json` already use parent/child
this way, so this is the house pattern rather than an invention. The difference from the earlier
script is that the contract now travels **on the task** instead of in a sidecar manifest, so
`work.project()` needs no overlay to see it.

⛔ **Three refusals, each of which was MEASURED on this checkout on 2026-09-02 rather than
   reasoned about.** A preset that trips any of them compiles work the autonomy pump can never
   start, and — this is the dangerous part — the work still *looks* fine on the page. It sits in
   DRAFT, or it sits in READY while every autonomous start is refused, and nothing says why
   unless somebody opens the inspector.

1. **A stage with no `repo` can never be READY.** `work.readiness` returns `repo UNMEASURED` and
   `work._state_for` makes an UNMEASURED check DRAFT, deliberately and permanently. 54 of the 91
   rows in the live store are in exactly that state.

2. **A stage with no `resource_claim` can never be READY.** Same route, via
   `contract UNMEASURED` — "absence of a declaration is not evidence of isolation".

3. **Two stages may not share a WRITE `resource_claim`.** `work._conflicts` pairs any two stages
   sharing a claim when either declares WRITE, and `work.guarded_start` refuses on a **declared**
   conflict whether or not the other side is live. Both stages are then permanently ineligible
   for an autonomous start. READ-only stages may share a claim; writers may not. This one is the
   subtlest of the three because the stages reach READY and only the *start* is refused.

These are checked by :func:`validate` before anything is written, and the CLI refuses rather than
warning — a preset that cannot execute is not a preset with a caveat.
"""
from __future__ import annotations

import argparse
import pathlib
import sys
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from . import repo as _repo
from . import tasks as _tasks
from . import work as _work
from .tasks import TaskStore

#: Presets ship with the repository, beside the missions they belong to. Not under `.data/`:
#: `.data/` is runtime state, and a preset is source.
PRESETS_DIR = _repo.primary() / "missions" / "presets"

#: Stage kinds. `human_gate` is the only one that is not runnable, and it is the only one that
#: may carry a `hold`. The rest differ only in what their objective tells the session to do —
#: there is no deterministic executor in this repo, so every runnable stage is an agent session
#: that has been told exactly which command to run.
RUNNABLE = ("deterministic", "agent")
HUMAN_GATE = "human_gate"
KINDS = RUNNABLE + (HUMAN_GATE,)


class PresetRefused(Exception):
    """A preset that cannot compile to executable work. Raised BEFORE anything is written."""


@dataclass
class Stage:
    id: str
    title: str
    kind: str = "deterministic"
    objective: str = ""
    repo: str = ""
    autonomy: str = _tasks.MANUAL
    resource_claim: str = ""
    access: str = "READ"
    depends_on: List[str] = field(default_factory=list)
    hold: str = ""
    requires_approval: str = ""
    model: str = ""
    effort: str = ""

    @property
    def runnable(self) -> bool:
        return self.kind in RUNNABLE


@dataclass
class Preset:
    id: str
    title: str
    objective: str = ""
    repo: str = ""
    visibility: str = _tasks.PRIVATE
    target: str = ""
    constraints: List[str] = field(default_factory=list)
    stages: List[Stage] = field(default_factory=list)
    path: Optional[pathlib.Path] = None

    @property
    def mission_id(self) -> str:
        """The parent row's id. Derived from the preset id so it is predictable and typeable."""
        return self.id.upper()

    def stage(self, sid: str) -> Optional[Stage]:
        return next((s for s in self.stages if s.id == sid), None)


# ------------------------------------------------------------------------------ loading


def available() -> List[str]:
    """Preset ids on disk. Derived from the directory, never a hand-maintained list."""
    if not PRESETS_DIR.is_dir():
        return []
    return sorted(p.stem for p in PRESETS_DIR.glob("*.yaml"))


def load(preset_id: str) -> Preset:
    """Read and validate a preset, or REFUSE. Never returns a preset that cannot compile."""
    try:
        import yaml
    except ImportError as exc:                                     # pragma: no cover
        raise PresetRefused(
            "REFUSED: PyYAML is not installed, so no preset can be read. `pip install pyyaml`."
        ) from exc

    pid = (preset_id or "").strip()
    if not pid:
        raise PresetRefused("REFUSED: no preset named. Available: " + (", ".join(available()) or "none"))
    path = PRESETS_DIR / f"{pid}.yaml"
    if not path.is_file():
        raise PresetRefused(f"REFUSED: no preset {pid!r} at {path}. "
                            f"Available: {', '.join(available()) or 'none'}")
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(raw, dict):
        raise PresetRefused(f"REFUSED: {path.name} is not a mapping.")

    default_repo = str(raw.get("repo") or "").strip()
    stages: List[Stage] = []
    for i, s in enumerate(raw.get("stages") or []):
        if not isinstance(s, dict):
            raise PresetRefused(f"REFUSED: stage {i} of {pid} is not a mapping.")
        stages.append(Stage(
            id=str(s.get("id") or "").strip(),
            title=str(s.get("title") or "").strip(),
            kind=str(s.get("kind") or "deterministic").strip(),
            objective=" ".join(str(s.get("objective") or "").split()),
            repo=str(s.get("repo") or default_repo).strip(),
            autonomy=str(s.get("autonomy") or _tasks.MANUAL).strip().upper(),
            resource_claim=str(s.get("resource_claim") or "").strip(),
            access=str(s.get("access") or "READ").strip().upper(),
            depends_on=[str(d).strip() for d in (s.get("depends_on") or [])],
            hold=str(s.get("hold") or "").strip(),
            requires_approval=str(s.get("requires_approval") or "").strip(),
            model=str(s.get("model") or "").strip(),
            effort=str(s.get("effort") or "").strip(),
        ))

    p = Preset(
        id=pid,
        title=str(raw.get("title") or pid).strip(),
        objective=" ".join(str(raw.get("objective") or "").split()),
        repo=default_repo,
        visibility=str(raw.get("visibility") or _tasks.PRIVATE).strip().upper(),
        target=str(raw.get("target") or "").strip(),
        constraints=[str(c) for c in (raw.get("constraints") or [])],
        stages=stages,
        path=path,
    )
    problems = validate(p)
    if problems:
        raise PresetRefused(f"REFUSED: {pid} cannot compile to executable work:\n  - "
                            + "\n  - ".join(problems))
    return p


def validate(p: Preset) -> List[str]:
    """Every reason this preset could not produce startable work. Empty list means it can.

    ⭐ Deny by default, and each condition is a stop rather than a score — the same shape as
    `work.guarded_start`, for the same reason: an unmeasured condition is a stop.
    """
    out: List[str] = []
    if not p.stages:
        out.append("no stages")
    if p.visibility not in _tasks.VISIBILITIES:
        out.append(f"visibility {p.visibility!r} is not one of {_tasks.VISIBILITIES}")

    ids = [s.id for s in p.stages]
    for dup in sorted({i for i in ids if ids.count(i) > 1}):
        out.append(f"stage id {dup!r} appears {ids.count(dup)} times")
    known = set(ids)

    writers: Dict[str, List[str]] = {}
    for s in p.stages:
        if not s.id:
            out.append("a stage has no id")
            continue
        if not _tasks._ID_OK.match(s.id):
            out.append(f"{s.id!r} is not a legal task id (A-Z a-z 0-9 . _ - , 1-64 chars)")
        if not s.title:
            out.append(f"{s.id}: no title")
        if s.kind not in KINDS:
            out.append(f"{s.id}: kind {s.kind!r} is not one of {KINDS}")
        if s.autonomy not in _tasks.AUTONOMIES:
            out.append(f"{s.id}: autonomy {s.autonomy!r} is not one of {_tasks.AUTONOMIES}")
        if s.access not in ("READ", "WRITE"):
            out.append(f"{s.id}: access {s.access!r} is neither READ nor WRITE")

        # Refusal 1 and 2 — the DRAFT trap.
        if not s.repo:
            out.append(f"{s.id}: no repo declared, so it can never leave DRAFT "
                       f"(work.readiness -> repo UNMEASURED)")
        if not s.resource_claim:
            out.append(f"{s.id}: no resource_claim declared, so it can never leave DRAFT "
                       f"(work.readiness -> contract UNMEASURED)")

        # Refusal 3 — a shared WRITE claim is a permanent guarded-start refusal.
        if s.resource_claim and s.access == "WRITE":
            writers.setdefault(s.resource_claim, []).append(s.id)

        for d in s.depends_on:
            if d not in known:
                out.append(f"{s.id}: depends on {d!r}, which is not a stage of this preset")
            if d == s.id:
                out.append(f"{s.id}: depends on itself")

        if s.hold and s.kind != HUMAN_GATE:
            out.append(f"{s.id}: declares a hold but is kind {s.kind!r} — only a "
                       f"{HUMAN_GATE} may hold")
        if s.kind == HUMAN_GATE and not s.hold:
            out.append(f"{s.id}: is a {HUMAN_GATE} with no hold, so nothing would stop it")

    for claim, who in writers.items():
        others = [s.id for s in p.stages if s.resource_claim == claim and s.id not in who]
        if len(who) > 1 or others:
            out.append(
                f"resource_claim {claim!r} is declared WRITE by {', '.join(who)}"
                + (f" and shared with {', '.join(others)}" if others else "")
                + " — work.guarded_start refuses on a DECLARED conflict, so every one of those "
                  "stages would be permanently ineligible for an autonomous start")

    if not p.target:
        out.append("no target stage declared, so RUN CRITICAL PATH has nothing to aim at")
    elif p.target not in known:
        out.append(f"target {p.target!r} is not a stage of this preset")

    # A cycle would make the whole run unstartable. Checked here so the refusal names the preset
    # rather than surfacing as a KeyError from the store half-way through a create.
    if not out:
        for s in p.stages:
            seen, stack = set(), list(s.depends_on)
            while stack:
                cur = stack.pop()
                if cur == s.id:
                    out.append(f"{s.id}: is part of a dependency cycle")
                    break
                if cur in seen:
                    continue
                seen.add(cur)
                nxt = p.stage(cur)
                if nxt:
                    stack.extend(nxt.depends_on)
    return out


# ------------------------------------------------------------------------------ compiling


def _contract(p: Preset, s: Stage) -> Dict[str, Any]:
    """What travels with the stage. Everything the executing session or the planner needs."""
    c: Dict[str, Any] = {"mission": p.mission_id, "preset": p.id, "kind": s.kind}
    if s.resource_claim:
        c["resource_claim"] = s.resource_claim
        c["access"] = s.access
    if s.model:
        c["model"] = s.model
    if s.effort:
        c["effort"] = s.effort
    if p.constraints:
        c["constraints"] = list(p.constraints)
    # ⛔ Read by `work.guarded_start` via `_HUMAN_GATE_KEYS`: a stage declaring this can never
    # start without a human, whatever its policy says and whatever the run mode is.
    if s.requires_approval:
        c["requires_approval"] = s.requires_approval
    return c


def existing(p: Preset, store: TaskStore) -> List[str]:
    """Which of this preset's ids are already in the store. Non-empty means `create` refuses."""
    have = {t.id for t in store.all()}
    return [i for i in ([p.mission_id] + [s.id for s in p.stages]) if i in have]


def create(p: Preset, store: Optional[TaskStore] = None, actor: str = "operator") -> List[str]:
    """Compile the preset into canonical work. Idempotent by refusal, never by overwrite.

    ⛔ **The store is append-only, so a partial or repeated create is permanent.** Every id is
    checked before the first write, and the order is: mission row, then every stage row, then
    every edge, then the holds. Edges last means an edge can never point at a task that does not
    exist yet; holds last means a gate is never held before it is fully described.
    """
    st = store if store is not None else _work.open_store()

    clash = existing(p, st)
    if clash:
        raise PresetRefused(
            f"REFUSED: {', '.join(clash)} already exist in {_work.store_path()}. The store is "
            f"append-only, so a second create would replay as a second `create` event and reset "
            f"every field folded after the first. Nothing was written. To run this preset again, "
            f"give the stages new ids.")

    made: List[str] = []
    st.create(title=f"{p.id} — {p.title}", actor=actor, tid=p.mission_id,
              objective=p.objective, repo=p.repo, visibility=p.visibility,
              contract={"preset": p.id, "kind": "mission",
                        "constraints": list(p.constraints)})
    made.append(p.mission_id)

    for s in p.stages:
        st.create(title=s.title, actor=actor, tid=s.id, parent=p.mission_id,
                  objective=s.objective, repo=s.repo, visibility=p.visibility,
                  contract=_contract(p, s))
        made.append(s.id)

    for s in p.stages:
        for d in s.depends_on:
            st.depend(s.id, d, actor=actor)

    for s in p.stages:
        if s.autonomy != _tasks.DEFAULT_AUTONOMY:
            st.set_autonomy(s.id, s.autonomy, actor=actor)
        if s.kind == HUMAN_GATE and s.hold:
            # The store's own word for "a human must act". `resolve_hold` in the tracker is its
            # inverse and already has a UI, so this is the gate mechanism that is already wired
            # end to end rather than a new one.
            st.block(s.id, by=s.hold, actor=actor)

    return made


# ------------------------------------------------------------------------------ reporting


def plan_report(p: Preset) -> str:
    """What `--create` would write. Writes nothing itself."""
    o = [f"PRESET   {p.id}  ({p.path.name if p.path else '?'})",
         f"TITLE    {p.title}",
         f"MISSION  {p.mission_id}   repo={p.repo or '—'}  visibility={p.visibility}",
         f"TARGET   {p.target}",
         f"STAGES   {len(p.stages)}", ""]
    for s in p.stages:
        gate = f"  HOLD {s.hold}" if s.hold else ""
        o.append(f"  {s.id}")
        o.append(f"      {s.kind:14} {s.autonomy:8} {s.access} {s.resource_claim}"
                 + (f"  {s.model}/{s.effort}" if s.model else "") + gate)
        o.append(f"      depends_on: {', '.join(s.depends_on) or 'none'}")
    o.append("")
    o.append(f"EDGES    {sum(len(s.depends_on) for s in p.stages)}")
    o.append(f"HOLDS    {sum(1 for s in p.stages if s.hold)}")
    o.append("")
    o.append("Nothing was written. `--create` would append "
             f"{1 + len(p.stages)} create event(s) to {_work.store_path()}.")
    return "\n".join(o)


def status_report(p: Preset, store: Optional[TaskStore] = None) -> str:
    """Where the run is now, read from the projection — not from this file."""
    st = store if store is not None else _work.open_store()
    rows = {w.id: w for w in _work.project(store=st)}
    if p.mission_id not in rows:
        return (f"{p.mission_id} is not in {_work.store_path()} — this preset has not been "
                f"created. `--create` would make it.")
    o = [f"MISSION  {p.mission_id}   {rows[p.mission_id].status}", ""]
    for s in p.stages:
        w = rows.get(s.id)
        if w is None:
            o.append(f"  {s.id:38} ABSENT")
            continue
        allowed, why = _work.guarded_start(w)
        o.append(f"  {s.id:38} {w.state:12} {w.autonomy:8} "
                 f"start={w.start_mode or '—'} ev={w.evidence}")
        o.append(f"      autonomous start: {'ALLOWED' if allowed else 'REFUSED — ' + '; '.join(why[:2])}")
    return "\n".join(o)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Compile a mission preset into canonical work.")
    ap.add_argument("--list", action="store_true", help="list presets on disk")
    ap.add_argument("--preset", default="", help="preset id")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--plan", action="store_true", help="print what would be created; write nothing")
    g.add_argument("--create", action="store_true", help="create the run")
    g.add_argument("--status", action="store_true", help="where the run is now")
    a = ap.parse_args(argv)

    if a.list or not a.preset:
        names = available()
        print(f"{len(names)} preset(s) in {PRESETS_DIR}:")
        for n in names:
            try:
                print(f"  {n:32} {load(n).title}")
            except PresetRefused as exc:
                print(f"  {n:32} ⛔ {str(exc).splitlines()[0]}")
        return 0 if names else 1

    try:
        p = load(a.preset)
    except PresetRefused as exc:
        print(exc, file=sys.stderr)
        return 2

    if a.create:
        try:
            made = create(p)
        except PresetRefused as exc:
            print(exc, file=sys.stderr)
            return 2
        print(f"created {len(made)} row(s): {', '.join(made)}")
        print()
        print(status_report(p))
        return 0
    if a.status:
        print(status_report(p))
        return 0
    print(plan_report(p))
    return 0


if __name__ == "__main__":                                         # pragma: no cover
    raise SystemExit(main())
