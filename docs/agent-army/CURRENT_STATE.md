# Current state — what of Agent Army actually exists in this code

**Measured 2026-08-30** against branch `docs/agent-army-research-separation` (from
`feat/readiness-generator`, HEAD `b4bac0d`).

Regenerate the term sweep behind this document with:

```bash
grep -rniE "Agent Army|Artificial Organization|Mission Command|Intent Contract|Running Estimate|\
Organizational Compiler|Org-IR|Collective Cognition|stigmergy|morphogenetic|Evolution Chamber|\
Capability Readiness|Cognitive Logistics|Command World" --include="*.py" factory/ evaluator_service/ scripts/
```

At the time of writing that command returns **nothing**. Not one Agent Army term appears in any
Python module in this repository. Every `PARTIAL` below is a mechanism that solves a related
problem under a different name — never a partial implementation of the research vocabulary.

## Status vocabulary

| Status | Means |
|---|---|
| `IMPLEMENTED` | Exists, is imported, and is covered by a test |
| `PARTIAL` | Some mechanism exists and is cited; the concept as researched is not built |
| `PLANNED` | An accepted decision exists to build it, with a named precondition |
| `NOT IMPLEMENTED` | No code. Includes concepts deliberately cut |

> ⛔ **Nothing here is marked implemented because a research document describes it.** Every
> `IMPLEMENTED` and `PARTIAL` row cites a path, and most cite a line. Open the file before relying
> on the row.

---

## The table

| CONCEPT | STATUS | CODE EVIDENCE | NOTES |
|---|---|---|---|
| **agent/team orchestration** | `PARTIAL` | `factory/lanes.py:125` `LANES` — 5 authored lanes; `factory/claims.py` lane claiming; `factory/worktrees.py` one worktree per lane; `factory/launch.py` launch admission; `factory/teamplan.py` per-team step sequencing over `board.DEPENDS`; `blueprints/orchestrator_team.yaml` | Five **authored** lanes worked by human-launched Claude Code sessions, isolated by git worktree. There is no agent that forms a team, no supervisor tier, and no agent-to-agent protocol. `teamplan.py` sequences a team's steps; it does not staff one. |
| **missions** | `NOT IMPLEMENTED` | — | No mission object, schema or lifecycle anywhere. The word appears in this codebase only inside `submission` and `PermissionError`. The nearest analogue is a *lane brief* (`factory/lanes.py`) and a *gate* (`factory/readiness.py:1394`), neither of which is a mission. |
| **sessions** | `IMPLEMENTED` | `factory/sessions.py` — reads Claude Code's own registry `~/.claude/sessions/<pid>.json`; `tests/test_claim_race.py`, `tests/test_contention.py` | Live-session detection, and the one subtlety is handled: liveness is checked against the **process table**, not the file's existence, because the registry file outlives the process. Built after three sessions shared one worktree on 2026-08-22. |
| **typed events** | `PARTIAL` | `factory/bus.py:48` `KINDS = ("correction","claimed","blocked","finished","note")`, rejected at `bus.py:74`; `factory/tasks.py:35` `Event` + append-only fold | Two typed event systems exist and **neither is an organizational event log.** The bus is deliberately ephemeral, machine-local, gitignored and one-file-per-writer (`bus.py:1-27`); the task store's events are per-task. There is no durable, replayable, cross-entity event stream. |
| **world-state projections** | `PARTIAL` | `factory/board.py:1-21` — every non-passing gate *is* a task, derived, never hand-listed; `factory/flow.py` graph laid out from `readiness.py` data; `factory/context.py:71` `ContextRef` with a required non-empty `source` | The projection *discipline* is unusually strong — `board.py` makes list/status drift structurally impossible, and `context.py:74` refuses a ref that cannot point back at its origin. But these project **gates and context**, not organizational state. Nothing is materialized. |
| **artifact evidence** | `IMPLEMENTED` | `factory/evidence.py:48` `CLASSES = (TARGET, CONSUMER, REGRESSION, ROLLBACK)`, states at `:68-70` `SATISFIED / ASSERTED / ABSENT`; `factory/tasks.py:163,169` `EvidenceRequired` raised by the store; `tests/test_evidence_classes.py` | The strongest Agent-Army-adjacent thing in the repo. A task **cannot** close with no evidence, and `close(require=...)` refuses a delivery that never proved its target or captured a rollback. Rows carry `MEASURED\|DERIVED\|ASSUMED` (`tasks.py:137`). Stated limit at `evidence.py:27`: it cannot verify that ROLLBACK was captured *before* the mutation. |
| **replay** | `PARTIAL` | `factory/certify.py:71,132` — recorded values are labelled `"REPLAYED, not a live measurement"`; `factory/runs.py:42` `RECONSTRUCTED` derives past runs from git + session transcripts | Replay exists as an *honesty label* and as retroactive reconstruction of lane cost. There is no timeline, no organizational state at time T, and nothing steps through history. |
| **Intent Contracts** | `NOT IMPLEMENTED` | `factory/contract.py` is a **GreenContract**, not an intent contract; `factory/launch.py:178,186` passes an `intent` string through unvalidated | Easy to mistake, so stated plainly: `contract.py` defines what *done* means (`Verdict.PASS/FAIL/UNMEASURABLE/NOT_RUN`, `contract.py:17-21`). An Intent Contract as researched — bounded authority, commander's intent, acceptable variation — has no representation. The `intent` field is a label on a launch record. |
| **knowledge objects** | `PARTIAL` | `docs/findings.d/` — one file per finding, F20–F82; `factory/findings.py` reads `docs/findings.md` **as data** so a lane is shown only the corrections that hit it | Corrected premises are durable, addressable, reviewed and merge with the branch — genuinely knowledge-object-shaped. But they are untyped Markdown, repo-local, have no provenance schema, no confidence, no promotion path and no reuse across repositories. |
| **skills** | `NOT IMPLEMENTED` | `factory/readiness.py:1346` and `factory/lanes.py:213` reference `~/.claude/skills/living-systems-ui/SKILL.md` | Referenced only as a **probe target** — a gate reads that file to check a claim was written down. There is no skill object, registry, versioning or publication path in the product. |
| **capability readiness** | `PARTIAL` | `factory/readiness.py:1394` `GATES` — 30 gates across 5 phases; `factory/goals.py` groups gates by goal; `factory/board.py`; `factory/launch.py` | Readiness is measured, and measured well — but it is readiness *of the factory*, not of an agent or a capability. `goals.py` is explicit that the grouping is the only authored thing and is validated on import. A goal with no measurable gate reports `NOT-MEASURED`, never `0%`. |
| **running estimates** | `NOT IMPLEMENTED` | — | Zero occurrences. The closest is `factory/runs.py` — a *retrospective* ledger of what lanes cost, with basis `RECORDED / RECONSTRUCTED / NOT-RECORDED` (`runs.py:42`). A running estimate is forward-looking and continuously revised; nothing here is. |
| **staff mesh** | `NOT IMPLEMENTED` | — | Zero occurrences. No staff functions, no echelon addressing, no non-task agents. |
| **organizational fields** | `NOT IMPLEMENTED` | — | Zero occurrences. No stigmergic substrate, no pheromone/gradient state, no field overlays. |
| **adaptive team formation** | `NOT IMPLEMENTED` | `factory/lanes.py:125` `LANES` is a literal list; `factory/teamplan.py` takes membership as given | Team membership is authored by a human and validated on import. Nothing selects members, sizes a team, or reshapes one at runtime. |
| **simulation** | `NOT IMPLEMENTED` | — | Zero occurrences of `simulat*` in `factory/`. `factory/corpus.py` loads a hashed known-good **world** for grading (`evals/`, verified against `evals/MANIFEST.sha256`), which is a fixture, not a simulator. |
| **Evolution Chamber** | `NOT IMPLEMENTED` | — | No optimizer at all. `README.md` "What is deliberately absent" lists **Optimizer**, unlocked by *"a working eval — the fitness function is the eval score"*. |
| **Command World** | `NOT IMPLEMENTED` | `docs/artifacts/agent-factory.html`, `docs/board/index.html`, `tracker.html` are generated dashboards | `README.md` lists **Platform UI** as deliberately absent, unlocked by *"numbers worth looking at"*. The existing surfaces are read-only status pages generated by `scripts/build_board_artifact.py` and `factory/schedule.py`. |
| **doctrine** | `NOT IMPLEMENTED` | one prose mention, `factory/live_probes.py:226` | That mention is about *measurement* doctrine (NOT-RECORDED vs NOT-VISIBLE), not organizational doctrine. |
| **federation** | `NOT IMPLEMENTED` | — | Zero occurrences of `federat*` anywhere in the codebase. |

---

## What exists here that the research vocabulary does not name

Three mechanisms in this repository are more developed than anything in the research corpus and
have no counterpart in it. Any Agent Army design must either adopt them or explain why not.

| Mechanism | Where | Why it matters |
|---|---|---|
| **The four-verdict contract** | `factory/contract.py:17-21`; `README.md` scope table | `UNMEASURABLE` is never collapsed into `FAIL` or `PASS`. *"A check whose instrument could not run has not passed."* The research corpus has no equivalent — R30's metric lists have no way to say "the instrument was dark". |
| **Grader separation** | `factory/corpus.py` (corpus is hashed JSON under `evals/`, verified on load, not executable Python); `evaluator_service/` + `factory/evaluator.py` (three routes, no fourth); `factory/certify.py:19` `--calibrate` vs `--remote` | An agent that can edit its own grader is not graded. `--calibrate` scores in-process and is explicitly *"worthless as evidence that an agent did not grade itself"*. `corpus.py` names the remaining gap honestly: separation is evident and attributed, not yet *enforced*. |
| **Evidence-gated close** | `factory/evidence.py` + `factory/tasks.py:163` | Refusal lives in the **store**, not in a convention an agent can forget. |

---

## The finding that matters most

`blueprints/orchestrator_team.yaml` is a three-agent team blueprint that was **built, tested and
rejected on evidence**, and deliberately kept rather than deleted. Its header records:

> multi-agent averaging **−3.5%** against single-agent baselines across a 180-configuration study
> (5 architectures, 3 model families, 4 agentic benchmarks), with **sequential tasks degrading
> 39–70%** … *"THIS FILE IS KEPT, NOT DELETED. It is a hypothesis that was tested and rejected."*

It also records the threshold that would unlock it: a same-budget A/B on the same tasks and the
same authoritative verifier showing **≥10pp absolute terminal-success gain**, or **≥20% lower cost
at indistinguishable success**, with no increase in side effects and every mandatory handoff
**≥99% accepted-and-correctly-consumed**.

This is the single most important input this repository has for the research programme, and the
research corpus does not currently contain it. See
`agent-army-research/migration/MIGRATION-REPORT.md` §"Product discoveries".

## Why so little is implemented

Not neglect — an explicit scope decision. `README.md` §"What is deliberately absent":

| Not here | Unlocked by |
|---|---|
| Agent Army / supervisor tiers | **One certified team, plus evidence a tier helps** |
| Optimizer | A working eval |
| More than one comms topology | A second team that actually needs to talk to the first |
| Gym | The eval corpus plus a scoreboard |
| Platform UI | Numbers worth looking at |

`docs/research/agent-factory-research-prompts.md:55` records the same call: *"Agent Army (level 5)
— **Cut for now**. Crucible already asked whether levels 4–5 are real structure or ceremony. With
zero certified teams…"*, and `docs/DEEP-REVIEW-PROMPT.md:228` encodes the unlock rule as
*"agent army ← one certified team"*.

**The precondition has not been met.** No team is certified today, so the gate on Agent Army work
in this repository has not opened.
