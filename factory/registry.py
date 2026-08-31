"""Which workflow implements a (shape, layer) — and what version of it ran.

The estate has two halves that have never known about each other. `MEASURED` 2026-08-30, against the
committed tree::

    grep -rn "inquest\\|conclave\\|assay\\|vigil\\|prospect" factory/ blueprints/ scripts/   # (nothing)

On one side, `~/.claude/skills/` holds six adversarial councils and `~/.claude/commands/` holds two
repo stage machines — between them the *methods* this estate actually delivers work with, one of them
carrying MEASURED evidence on a real ticket (GP-311's council of five caught six factual errors in an
inherited case file before any of it reached a partner). On the other side, this package holds the
contracts, the verdicts, the evidence classes and the run ledger — the *proving* apparatus. Neither
could name the other, so no run record could ever say which method produced it.

This module is the join, and it is deliberately thin.

⭐ **The version of a workflow is the hash of its text.** `blueprint.py` opens with *"the config that
IS the version"* for `AgentSpec`; the same argument applies with more force to a workflow whose entire
behaviour is prose. A `SKILL.md` edited between two runs is a different workflow, and a certification
earned under one must not silently transfer to the other. So `Workflow.version` hashes the file.

⚠ **BASIS.** The *routing* — which shape and layer each workflow serves — is `ASSUMED`, a judgement
written here so it can be argued with rather than improvised per session, exactly as `lanes.py` and
`presets.py` declare for the same reason. What is `MEASURED` is narrower and stated per row in
``evidence``: whether this workflow has ever been run on real work, and where that is recorded.

⛔ **What this does NOT do.** It does not dispatch, and it does not certify. Naming a workflow for a
shape is a claim that one *applies*, never that it has been *proved to work* — the same distinction
`presets.verifier_state` exists to keep visible. Read ``evidence`` before trusting a row, and
``unproven()`` before treating the table as coverage.
"""
from __future__ import annotations

import hashlib
import os
import pathlib
from dataclasses import dataclass
from typing import Dict, List, Optional

#: The shape of the unknown. What decides the METHOD.
#:
#: Derived from R19's 16-type taxonomy (MEASURED across all 59 wiki ticket pages) collapsed onto the
#: question each type actually asks. A ticket type says what the work touches; a shape says what you
#: do not yet know, which is what picks a council.
SHAPES = (
    "diagnose",   # why is this wrong
    "review",     # is this diff safe
    "measure",    # how much / how many
    "watch",      # will it tell us when it breaks
    "decide",     # should we do this at all
    "design",     # what should the structure BE
    "build",      # spec -> ship
)

#: What the work touches. What decides the VERIFIER, the deploy path and the rollback shape.
LAYERS = (
    "connector",
    "warehouse",
    "semantic_model",
    "app",
    "infra",
    "client_doc",
)

#: Where a workflow's text lives. Both are real and they behave differently, which is the point of
#: recording it: a SKILL fires on its own description, a COMMAND fires only when a human types it.
SKILL = "skill"
COMMAND = "command"

#: Has this workflow been run on real work, and is that recorded anywhere we can point at?
PROVEN = "proven"        #: run on a real ticket, with a citation
DECLARED = "declared"    #: the method exists and is written down; no run of it is recorded here
UNBUILT = "unbuilt"      #: named because it is the right method — nothing implements it yet


def _home() -> pathlib.Path:
    """The Claude Code config root. Env-overridable so a test never reads the real estate."""
    override = os.environ.get("CLAUDE_CONFIG_HOME")
    return pathlib.Path(override) if override else pathlib.Path.home() / ".claude"


@dataclass(frozen=True)
class Workflow:
    """One method, and the evidence that it is a method rather than an intention."""

    id: str
    kind: str                 #: SKILL | COMMAND
    shapes: tuple             #: which unknowns it answers
    layers: tuple             #: () means layer-agnostic — it works wherever the shape applies
    #: What it ends at. A workflow whose end state is unstated cannot be told it is finished.
    ends_at: str
    state: str                #: PROVEN | DECLARED | UNBUILT
    #: The citation for `state`. MEASURED where it names a real ticket; empty is only valid for UNBUILT.
    evidence: str = ""

    @property
    def path(self) -> pathlib.Path:
        if self.kind == SKILL:
            return _home() / "skills" / self.id / "SKILL.md"
        return _home() / "commands" / f"{self.id}.md"

    @property
    def version(self) -> Optional[str]:
        """sha256 of the workflow's own text, or None if it is not on disk.

        ⛔ `None` is not "unchanged" and not "version zero" — it is NOT-VISIBLE, and a caller that
        renders it as a version has collapsed a missing instrument into a measurement. Callers ask
        `installed()` when they need to know which.
        """
        p = self.path
        if not p.is_file():
            return None
        return hashlib.sha256(p.read_bytes()).hexdigest()[:12]

    @property
    def installed(self) -> bool:
        return self.path.is_file()


#: The routing table. Every row's `evidence` is what separates it from a wish.
WORKFLOWS: List[Workflow] = [
    Workflow(
        id="inquest", kind=SKILL,
        shapes=("diagnose",), layers=(),
        ends_at="a proven root cause and a fix whose regression test fails without it",
        state=PROVEN,
        evidence="GP-311 — ran as a council of five; caught six factual errors in the inherited case "
                 "file before any of it reached a partner. The estate's only MEASURED evidence for a "
                 "multi-agent formation on real work.",
    ),
    Workflow(
        id="conclave", kind=SKILL,
        shapes=("review",), layers=(),
        ends_at="a merge or block decision a human signs",
        state=PROVEN,
        evidence="ALDC-739 — founding run; four numbered reference runs recorded in the skill. The "
                 "`advocate` seat was promoted from optional to standard after it proved a headline "
                 "BLOCKER belonged to trunk rather than the PR.",
    ),
    Workflow(
        id="assay", kind=SKILL,
        shapes=("measure",), layers=("warehouse", "client_doc"),
        ends_at="a published figure that carries its counting basis",
        state=PROVEN,
        evidence="FU92-420 — the audit that went through five revisions with zero deploys. The only "
                 "ticket in the corpus that damaged a client relationship, and no change gate would "
                 "have caught any of it.",
    ),
    Workflow(
        id="vigil", kind=SKILL,
        shapes=("watch",), layers=("connector", "infra"),
        ends_at="an armed watch whose silence has been proved to mean health",
        state=PROVEN,
        evidence="ALDC-656. Also FU92-421, where deploying a monitor built to catch silent "
                 "non-firing surfaced four independent faults in the monitor itself.",
    ),
    Workflow(
        id="prospect", kind=SKILL,
        shapes=("decide",), layers=(),
        ends_at="a decision, with the boundary probe that could have halted it",
        state=DECLARED,
        evidence="No run on a real bet is recorded in this repo. The method is written and its gates "
                 "are specified; that is not the same as having been run.",
    ),
    Workflow(
        id="keel", kind=SKILL,
        shapes=("design",), layers=("warehouse", "semantic_model"),
        ends_at="an ACCEPTED design a human approves — never a built one",
        state=DECLARED,
        evidence="Written 2026-08-30 from the GP-318/GP-319 defect ledger. Every lens and every "
                 "anti-pattern cites a measured defect, but the council itself has not yet been run. "
                 "Its first run is the GEP marketing model.",
    ),
    Workflow(
        id="gep-feature", kind=COMMAND,
        shapes=("build",), layers=("warehouse", "semantic_model", "app"),
        ends_at="a deployed change with its artifact.yaml stage history closed",
        state=PROVEN,
        evidence="clients/GEP/tickets/GP-197/artifact.yaml and GP-199/artifact.yaml — two live "
                 "instances carrying stage_history, per-layer changes and deploy_history. This is "
                 "the Job object docs/specs/golden-workflow-fit.md called MISSING.",
    ),
    Workflow(
        id="prefect-connector", kind=COMMAND,
        shapes=("build",), layers=("connector",),
        ends_at="a connector deployed and verified against landed rows",
        state=DECLARED,
        evidence="The stage machine is written (scoping / implementing / local-test / deploy / "
                 "verify). No artifact from a completed run is recorded in this repo.",
    ),
    Workflow(
        id="army", kind=SKILL,
        shapes=SHAPES, layers=(),
        ends_at="whatever the decomposed task ends at — it is the fallback, not a method",
        state=DECLARED,
        evidence="The general orchestrator, for work no specific council covers. ⚠ Until 2026-08-30 "
                 "it shipped with no YAML frontmatter, so its H1 was used as its trigger and it was "
                 "among the least triggerable skills in the library.",
    ),
]


# ---------------------------------------------------------------------------
# Validation at import. A malformed row would hand a caller a routing decision with no argument
# attached, which is the one thing this module exists to prevent.
_ids = [w.id for w in WORKFLOWS]
if len(_ids) != len(set(_ids)):
    raise ValueError(f"duplicate workflow id(s): {sorted({i for i in _ids if _ids.count(i) > 1})}")
for _w in WORKFLOWS:
    if _w.kind not in (SKILL, COMMAND):
        raise ValueError(f"{_w.id}: kind {_w.kind!r} is not a known kind")
    if _w.state not in (PROVEN, DECLARED, UNBUILT):
        raise ValueError(f"{_w.id}: state {_w.state!r} is not a known state")
    if not _w.shapes:
        raise ValueError(f"{_w.id}: names no shape, so nothing could ever route to it")
    for _s in _w.shapes:
        if _s not in SHAPES:
            raise ValueError(f"{_w.id}: shape {_s!r} is not one of {SHAPES}")
    for _l in _w.layers:
        if _l not in LAYERS:
            raise ValueError(f"{_w.id}: layer {_l!r} is not one of {LAYERS}")
    if not _w.ends_at.strip():
        raise ValueError(f"{_w.id}: ends_at is empty — a workflow that cannot end cannot be finished")
    if _w.state != UNBUILT and not _w.evidence.strip():
        raise ValueError(f"{_w.id}: state is {_w.state!r} with no evidence — that is a wish, not a row")


def by_id(workflow_id: str) -> Optional[Workflow]:
    """The workflow with this id, or None. Never raises — an unknown id is a question, not a crash."""
    return next((w for w in WORKFLOWS if w.id == workflow_id), None)


def for_shape(shape: str, layer: Optional[str] = None) -> List[Workflow]:
    """Every workflow that answers this shape, optionally narrowed to a layer.

    A workflow declaring no layers is layer-agnostic and always eligible. Returns a list, never a
    single winner: choosing between two eligible methods is a judgement, and `control.eligible()`
    already establishes that the set not taken is the thing you cannot reconstruct afterwards.
    """
    if shape not in SHAPES:
        raise ValueError(f"{shape!r} is not one of {SHAPES}")
    if layer is not None and layer not in LAYERS:
        raise ValueError(f"{layer!r} is not one of {LAYERS}")
    out = [w for w in WORKFLOWS if shape in w.shapes]
    if layer is not None:
        out = [w for w in out if not w.layers or layer in w.layers]
    return out


def unproven() -> List[Workflow]:
    """Workflows named for a shape that have never been run on real work.

    ⚠ Read this before treating the table as coverage. A row naming a method is a claim that one
    APPLIES; only PROVEN means one has actually been run and the run is cited.
    """
    return [w for w in WORKFLOWS if w.state != PROVEN]


def uninstalled() -> List[Workflow]:
    """Rows whose file is not on disk.

    A row here is NOT-VISIBLE, not absent: this reads one estate's `~/.claude`, and a different
    machine or a `CLAUDE_CONFIG_HOME` override legitimately sees fewer. Never report it as "the
    workflow does not exist" — report the path that was checked.
    """
    return [w for w in WORKFLOWS if not w.installed]


def versions() -> Dict[str, Optional[str]]:
    """id -> content hash, or None where the file is not on disk.

    The dict a dispatch record should carry, so a later question — did this run use the workflow we
    think it did — is answerable rather than reconstructed.
    """
    return {w.id: w.version for w in WORKFLOWS}


def render(w: Workflow) -> str:
    """One workflow as plain text — same content any UI shows, so the two cannot drift."""
    v = w.version
    lines = [
        f"{w.id}  [{w.kind}]  {'/'.join(w.shapes)}",
        f"  layers      {', '.join(w.layers) if w.layers else 'any'}",
        f"  ends at     {w.ends_at}",
        f"  state       [{w.state}] {w.evidence}" if w.evidence else f"  state       [{w.state}]",
        f"  version     {v}" if v else "  version     NOT-VISIBLE — no file at " + str(w.path),
    ]
    return "\n".join(lines)


def main() -> int:
    print(f"{len(WORKFLOWS)} workflows over {len(SHAPES)} shapes — routing ASSUMED, evidence MEASURED\n")
    for w in WORKFLOWS:
        print(render(w))
        print()

    for shape in SHAPES:
        got = for_shape(shape)
        mark = "  " if got else "⛔"
        print(f"{mark} {shape:9s} -> {', '.join(w.id for w in got) or 'NOTHING'}")

    print()
    un = unproven()
    if un:
        print(f"⚠ {len(un)} of {len(WORKFLOWS)} have never been run on real work: "
              f"{', '.join(w.id for w in un)}")
        print("  A named method is a claim that one APPLIES, not that one has been run.")
    miss = uninstalled()
    if miss:
        print(f"⚠ {len(miss)} not on disk at the path checked: {', '.join(w.id for w in miss)}")
        print("  NOT-VISIBLE from this estate — not proof of absence.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
