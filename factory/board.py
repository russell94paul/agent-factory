"""The task board — what is left, what blocks what, and what can run at the same time.

    python -m factory.board

Distinct from `factory.readiness`, and the distinction is the whole point:

    readiness  measures STATE   — "is the retry cap enforced?"     always computed
    board      tracks WORK      — "enforce the retry cap"          computed where it can be

Every task declares `done_when`. Where that is a readiness gate id, the task's status is **derived
from the gate** — it ticks itself when the world changes and it cannot be wrong about itself. Where
no probe can settle it, `done_when` is a sentence and the task is rendered as DECLARED, so a reader
can see at a glance which rows are trusting somebody's word.

That split exists because the thing this board replaces was a grid of checkboxes with no storage
behind them: ticking one and reloading lost the tick, and nothing stopped a box being green while
the repo said otherwise.

Dependencies are real edges, not decoration. A task is READY when every dependency is done, which
means **everything READY at once can run in parallel** — that is the answer to "what can we do
simultaneously", computed rather than guessed.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .readiness import measure

# Status values. NOT a checkbox: three of the four are computed.
DONE, READY, BLOCKED, DECLARED = "DONE", "READY", "BLOCKED", "DECLARED"

TRACKS = {
    "control": ("Control plane", "prefect-connectors — the loop the team will run in"),
    "certify": ("Certification", "agent-factory — can we believe the output"),
    "research": ("Research follow-ups", "questions already earned, not yet asked"),
    "surface": ("Verification surface", "can we see what we shipped"),
    "team": ("The first team", "everything above is a prerequisite for this"),
}


@dataclass
class Task:
    id: str
    title: str
    track: str
    done_when: str                      # a gate id, or a sentence if no probe exists
    gate: Optional[str] = None          # readiness gate whose PASS means this is done
    deps: List[str] = field(default_factory=list)
    size: str = "M"                     # S / M / L — rough, and labelled as rough
    why: str = ""
    owner: str = ""                     # only where a human is genuinely required


TASKS: List[Task] = [
    # ---------------------------------------------------------------- control plane
    Task("cap", "Enforce the retry cap on the path that actually restarts", "control",
         "readiness gate `cap` passes", gate="cap", size="M",
         why="MAX_RECOVERIES_PER_STAGE=2 exists and is enforced — on a path that logged none of "
             "the 1,004 restarts. restart_from_stage compares no count to any ceiling."),
    Task("ceiling", "Check accrued spend against a budget before dispatch", "control",
         "readiness gate `ceiling` passes", gate="ceiling", deps=["cost"], size="M",
         why="A ceiling read from a figure blind to failures is not a ceiling, so cost telemetry "
             "has to land first."),
    Task("concurrency", "Bound concurrent stage dispatch, not just waves", "control",
         "readiness gate `concurrency` passes", gate="concurrency", size="M",
         why="wave_scheduler bounds how many PIPELINES start. Ten containers took a region quota "
             "at the stage level."),
    Task("reaper", "Lease, timeout and reap dispatched work", "control",
         "readiness gate `reaper` passes", gate="reaper", size="L",
         why="Containers outlive the stage that launched them. 4 of 14 runs sit at stage_started "
             "with no terminal event."),
    Task("cost", "Record cost on every attempt, including failures", "control",
         "readiness gate `cost` passes", gate="cost", size="M",
         why="1,001 failed attempts contribute $0.00, so true spend is unrecoverable and no "
             "honest optimisation estimate exists."),
    Task("from-history", "Compute the terminal verdict from the append-only log", "control",
         "readiness gate `from-history` passes", gate="from-history", size="L",
         why="Current state cannot answer a question about what it cost to get there. This is the "
             "last-write-wins defect."),
    Task("checks", "Give every gate a programmatic check", "control",
         "readiness gate `checks` passes", gate="checks", size="M",
         why="5 of 7 gates have gate_check=None — a human clicking approve, not a control."),
    Task("refuses", "Prove a gate can refuse, with a drill", "control",
         "readiness gate `refuses` passes", gate="refuses", deps=["checks"], size="M",
         why="22 gate events, zero refusals. A gate never observed refusing is decoration — the "
             "same rule the contract applies to its own assertions."),
    Task("truthful", "Reconcile recorded status against the event log", "control",
         "readiness gate `truthful` passes", gate="truthful", deps=["from-history"], size="S",
         why="pipe_29b8edf6 is recorded `running` over a log ending in stage_failed."),
    Task("qa-general", "Make QA verification target the connector, not a smoke-test twin", "control",
         "readiness gate `general` passes", gate="general", size="M",
         why="promotion_ops.py:43 builds the deployment name as f\"smoke-test-{connector}\", so it "
             "can only ever validate one."),

    # ---------------------------------------------------------------- certification
    Task("evaluator", "Stand the evaluator up as its own principal", "certify",
         "readiness gate `isolated` passes", gate="isolated", size="L",
         why="R3 ranked the options for our threat model: an external service with separate "
             "credentials is rank 1, a separate local process is rank 5 and 'mostly theatre'. "
             "Moving files to another directory changes nothing."),
    Task("corpus", "Grow the corpus to two distributions across 15 strata", "certify",
         "readiness gate `breadth` passes", gate="breadth", size="L",
         why="One real success graded FOLKLORE. A blind spot affecting 10% of a stratum needs 29 "
             "cases for a 95% chance of being seen once."),
    Task("version", "Add the nine missing dimensions to the version hash", "certify",
         "readiness gate `version` passes", gate="version", size="M",
         why="contract_version first — a certification can currently outlive the contract that "
             "granted it."),
    Task("probes", "Wire the live probes so assertions can measure a real run", "certify",
         "readiness gate `certified` stops reporting NOT_RUN", gate="certified",
         deps=["evaluator"], size="L", owner="needs credential approval",
         why="All 12 assertions return UNMEASURABLE against a real target because Probes refuses "
             "every instrument by design."),
    Task("grain", "Settle the landing-table grain", "certify",
         "someone queries the table and reports whether it holds one account or more",
         size="S", owner="Paul or a live query",
         why="20 rows across 18 campaigns on one date cannot be unique on "
             "(account_id, campaign_id, date) under one account. If it is one, the declared "
             "primary key is wrong and the calibration world is built on a mistake."),
    Task("tenancy-fresh", "Re-confirm the six account ids against a live pull", "certify",
         "a live account list is compared to the six declared ids",
         deps=["probes"], size="S",
         why="Verified 2026-05-29, twelve weeks before use, and the source file itself says to "
             "confirm before activation."),

    # ---------------------------------------------------------------- research
    Task("r3-followup", "Ask R3 the false-succeeded correction", "research",
         "an answer lands in docs/research/answers/", size="S", owner="Paul runs it",
         why="R3's Q4 was aimed at Prefect. Our verdict comes from a bespoke engine's "
             "last-write-wins field. Drafted verbatim in docs/evidence/."),
    Task("r2-followup", "Ask R2 whether to move the build plane onto Prefect", "research",
         "an answer lands in docs/research/answers/", size="S", owner="Paul runs it",
         why="R2's prescription assumed Prefect's retry limits and concurrency reservation were "
             "available primitives. They are not. Nobody has asked whether to adopt Prefect "
             "rather than reimplement it — this is the highest-value unasked question."),
    Task("r1-followup", "Ask R1 whether anything else depended on the misattribution", "research",
         "an answer lands in docs/research/answers/", size="S", owner="Paul runs it",
         why="One-liner sanity check."),

    # ---------------------------------------------------------------- surface
    Task("browser", "Get claude-in-chrome connected", "surface",
         "tabs_context_mcp returns a tab", size="S", owner="likely a fresh session",
         why="Five defects shipped into a published figure and a human found every one. "
             "Extension v1.0.85 is installed on the right profile; the pairing is probably "
             "established at session start."),
    Task("render-pass", "Render-verify the artifact end to end", "surface",
         "every visual confirmed painting, at three widths, both themes",
         deps=["browser"], size="M",
         why="F1 of the quality gates. Static checks prove the file parses, not that it painted."),
    Task("impeccable", "Settle impeccable's precedence and run its detector", "surface",
         "the skill chain states where impeccable sits, and /impeccable audit has run once",
         size="M",
         why="A fifth design authority with a broad trigger. Its 59 deterministic detector rules "
             "are the instrument our static checks lacked — test whether they catch the three "
             "text collisions that shipped."),
    Task("jira", "Decide whether this work needs a ticket, and open one if so", "surface",
         "a key exists, or a decision is recorded that none is needed",
         size="S", owner="Paul",
         why="Draft is ready. No key exists and I will not guess one."),

    # ---------------------------------------------------------------- the team
    Task("worker-blueprint", "Write the single-worker blueprint R2 recommended", "team",
         "a blueprint exists for orchestrator -> worker -> non-LLM verifier -> human gates",
         deps=["from-history", "refuses"], size="M",
         why="The three-agent design is rejected and marked superseded. The replacement has not "
             "been written."),
    Task("first-run", "Run the first team on one connector, unattended", "team",
         "a run completes with the contract green and no human intervention",
         deps=["worker-blueprint", "probes", "corpus", "reaper", "cap"], size="L",
         why="This is the thing. Everything above exists so that a green result here means "
             "something."),
]


def status_of(task: Task, gates: Dict[str, str], done: Dict[str, bool]) -> str:
    if task.gate:
        if gates.get(task.gate) == "PASS":
            return DONE
    unmet = [d for d in task.deps if not done.get(d)]
    if unmet:
        return BLOCKED
    return READY if task.gate else DECLARED


def board() -> List[tuple]:
    """(task, status, unmet_deps) for every task, dependency-resolved."""
    results = measure()
    gates = {g.id: r.verdict for g, r in results}
    done: Dict[str, bool] = {}
    # Two passes: gate-derived first, then dependency resolution over the settled set.
    for t in TASKS:
        done[t.id] = bool(t.gate and gates.get(t.gate) == "PASS")
    out = []
    for t in TASKS:
        st = status_of(t, gates, done)
        unmet = [d for d in t.deps if not done.get(d)]
        out.append((t, st, unmet))
    return out


def main() -> int:
    rows = board()
    n_done = sum(1 for _, s, _ in rows if s == DONE)
    ready = [t for t, s, _ in rows if s == READY]
    declared = [t for t, s, _ in rows if s == DECLARED]

    print(f"\nTask board — {n_done} of {len(rows)} done, "
          f"{len(ready)} ready now, {len(declared)} awaiting a person\n")

    for key, (name, sub) in TRACKS.items():
        group = [(t, s, u) for t, s, u in rows if t.track == key]
        if not group:
            continue
        d = sum(1 for _, s, _ in group if s == DONE)
        print(f"  {name}  [{d}/{len(group)}]  — {sub}")
        for t, s, unmet in group:
            mark = {DONE: "[x]", READY: "[ ]", BLOCKED: "[~]", DECLARED: "[?]"}[s]
            dep = f"  waits on: {', '.join(unmet)}" if unmet else ""
            own = f"  ({t.owner})" if t.owner else ""
            print(f"    {mark} {t.size} {t.title}{dep}{own}")
        print()

    if ready:
        print("CAN RUN IN PARALLEL RIGHT NOW — no unmet dependencies between any of these:")
        for t in ready:
            print(f"    · [{t.track}] {t.title}")
    print("\n[x] done, derived from a readiness gate   [ ] ready   "
          "[~] blocked   [?] no probe can settle it")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
