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
| **The five-verdict contract** | `factory/contract.py:32` (`Verdict`); aggregation rule in `ContractResult.verdict`; `README.md` scope table | `PASS / FAIL / UNMEASURABLE / ERROR / NOT_RUN`. Neither `UNMEASURABLE` nor `ERROR` can be collapsed into `FAIL` or `PASS`, and `ERROR` outranks `FAIL` — *"if the apparatus broke we cannot claim the failure we think we saw was real."* **`ERROR` was added 2026-08-31** (`ba57f66`) after this document recorded its absence; see the FIXED section below. ⚠ **Five in the enum, six in effective use:** `REFUSED` (`evaluator_service/service.py:62`) is a verdict to the client — `UNSCORED_VERDICTS` (`factory/evaluator.py:65`) — but is not a `Verdict` member; it is the *service* refusing to score, not an assertion outcome, so the separation may be correct. And `Unmeasurable` is still defined three separate times, with three different docstrings, at `contract.py`, `readiness.py:42` and `schedule.py:54` — **unresolved**. |
| **Grader separation** | `factory/corpus.py` (corpus is hashed JSON under `evals/`, verified on load, not executable Python); `evaluator_service/` + `factory/evaluator.py` (three routes, no fourth); `factory/certify.py:15-17` (the stated distinction) and `:79,82` (the flags) `--calibrate` vs `--remote` | An agent that can edit its own grader is not graded. `--calibrate` scores in-process and is explicitly *"worthless as evidence that an agent did not grade itself"*. `corpus.py` names the remaining gap honestly: separation is evident and attributed, not yet *enforced*. |
| **Evidence-gated close** | `factory/evidence.py` + `factory/tasks.py:163` | Refusal lives in the **store**, not in a convention an agent can forget. |

### ⛔ …and the verdict model is one category coarser than the 1990s art

Added 2026-08-30. Two independent passes went looking for prior art on the four-verdict contract
and both found it in a maintained international standard. **Verified here against the primary
standards text**, not a summary — ITU-T Z.140 (07/2001), TTCN-3 core language, clause 24.2
"Verdict values and overwriting rules":

> "The verdict can have five different values: **pass, fail, inconc, none and error** i.e., the
> distinguished values of the `verdicttype`."
> — ITU-T Z.140 §24.2. `NOTE: inconc means an inconclusive verdict.`

Table 20 gives the overwriting rules, and they are **monotone** — a verdict may only get worse.
Current `inconc` with `pass` assigned stays **`inconc`**. That is precisely the non-collapsing
property `contract.py` exists to provide, and the mapping is one-to-one: `PASS↔pass`, `FAIL↔fail`,
`UNMEASURABLE↔inconc`, `NOT_RUN↔none`. The lineage runs back to ISO/IEC 9646 (1991); the current
maintained edition is ETSI ES 201 873-1 (where the same material sits at clause 24.1 / Table 30 —
clause and table numbering drifted between editions, so cite the edition you read).

**The fifth is the one we are missing**, and the standard is explicit about why it is separate:

> "The **error** verdict is special in that it is **set by the test system** to indicate that a test
> case (i.e., run-time) error has occurred. It **shall not be set by the set operation**. **No other
> verdict value can override an error verdict.**"
> — ITU-T Z.140 §24.2.1

Three properties, all of which we lack: it is raised by the *harness* rather than by the check, it
cannot be asserted by the thing being tested, and it **dominates everything**. We fold that case
into `UNMEASURABLE`:

```python
except Unmeasurable as exc:                       # contract.py:55 — the instrument says it cannot look
    return AssertionResult(self.name, Verdict.UNMEASURABLE, str(exc))
except Exception as exc:                          # contract.py:57 — the instrument BROKE
    return AssertionResult(self.name, Verdict.UNMEASURABLE,
                           f"instrument raised {type(exc).__name__}: {exc}")
```

Two different situations, one verdict. *"The instrument correctly reports it cannot measure"* and
*"the instrument crashed"* are not the same fact, and the second usually means something is wrong
with **us**, not with the thing under test.

⭐ **This repository's founding principle is that you must never collapse two kinds of not-knowing,
and it was collapsing two kinds of not-knowing.** That was not a research point; it was a defect in
the control.

## ✅ FIXED — `Verdict.ERROR` landed

The paragraph above described the state at `b4bac0d`. It is **no longer true**, and this document is
worthless if it says otherwise. Merged to `main` via `ba57f66`
(`fix/fifth-verdict-apparatus-error`). Verified on `main` at the time of writing:

```python
class Verdict(str, Enum):                       # factory/contract.py:32
    PASS = "PASS"
    FAIL = "FAIL"
    UNMEASURABLE = "UNMEASURABLE"   # instrument declined to run — NOT a pass
    ERROR = "ERROR"                 # the apparatus itself broke — NOT a measurement
    NOT_RUN = "NOT_RUN"
```

All three properties the standard requires are present:

| Property | Where |
|---|---|
| Separated from `UNMEASURABLE` | `Assertion.run` — `except Unmeasurable` → `UNMEASURABLE`; `except Exception` → `ERROR`, commented *"our own instrument fell over… TTCN-3 `error`"* |
| **Dominates `FAIL`** | `ContractResult.verdict` checks `ERROR` **before** `FAIL`: *"if the apparatus broke we cannot claim the failure we think we saw was real"* |
| Not scored as a measurement | `ERROR` is in `UNSCORED_VERDICTS` (`tests/test_contract.py:96`) |

Tests cover it, including the regression guard that matters most —
*"the fix must not sweep declared inconclusiveness into ERROR"* (`test_contract.py:68`).

**This is the first Wave 0 finding to reach production code**, and it did so without an
implementation handoff — which is a boundary exception worth noting rather than hiding. It was a
defect fix in existing code, not a research concept being built, so
[APPROVED_CONCEPTS.md](APPROVED_CONCEPTS.md) stays empty and correct.

Full analysis: `agent-army-research/research/sources/W0-adversarial-refutation-novelty-claim.md`.

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

### ⚠ Correction — the −3.5% is not what the summary makes it sound like

Added 2026-08-30 after R01 checked the figure back to its source. **The blueprint header, and the
first version of this document, both quoted the mean without its interval.** The underlying answer,
`docs/research/answers/R2-answer-topology.md:15`, does carry it:

> "Multi-agent systems averaged **−3.5%** performance relative to single-agent baselines across the
> study, **with a very wide 95% interval of −18.6% to +25.7%**."

A mean whose confidence interval spans zero is **not** evidence that multi-agent coordination hurts
on average. It is evidence of very high variance and no detectable average effect. Two further
qualifiers are in `R2-answer-topology.md` and in neither downstream summary:

- the same study found a centralised system **improved** a parallelisable financial task by
  **+80.9%** — the effect is strongly task-structure dependent, in both directions;
- the answer explicitly labels this **"OPEN RESEARCH, not production infrastructure evidence"** —
  controlled agentic benchmarks, not systems that deploy containers or write to a warehouse.

**The decision to reject the three-agent blueprint still stands, but not on the −3.5%.** It stands
on the two things that survive scrutiny: the **sequential-task degradation**, which is the task
class connector migration actually belongs to, and **our own measured failures, which were all at
seams** — so adding two mandatory LLM-to-LLM handoffs treats the wrong variable.

### And the source has moved — the current version supports the decision better

Verified 2026-08-30 against the paper itself: **arXiv:2512.08296**, *Towards a Science of Scaling
Agent Systems* (Kim et al.), DOI `10.48550/arXiv.2512.08296`. Our header describes **v1**
(Dec 2025) — 180 configurations, four benchmarks. The live version is **v3** (8 Apr 2026):
**260 configurations, six benchmarks**, five architectures, three LLM families.

**v3 does not lead with an average at all.** Its abstract frames the finding as architecture–task
fit, and the aggregate mean is not the headline:

> "Relative performance change compared to single-agent baseline ranges from **+80.8%** on
> decomposable financial reasoning to **−70.0%** on sequential planning, demonstrating that
> **architecture-task alignment determines collaborative success**."

It also reports a capability-saturation effect — coordination yields diminishing returns once
single-agent baselines pass a threshold — and that architectures **without centralized
verification propagate errors more** than those with it.

That is a *better* argument for the blueprint decision than the one we were making. Connector
migration is sequential shared-state work — the −70.0% pole, named in the paper's own abstract.
And "no centralized verification propagates errors" is an independent argument for the
non-LLM authoritative verifier this repository already built (`evaluator_service/`).

### It was peer-reviewed, and the journal title is itself the finding

An earlier revision of this document said R01's "landed in Nature MI 2026" claim was unsupported
because the arXiv record shows no journal reference. **That was wrong, and the error was mine.**
Absence of a `journal-ref` field is not absence of a journal version — I inferred a negative from
an instrument I had not shown could see the thing.

The DOI resolves. Verified against Crossref:

> **`10.1038/s42256-026-01268-y`** — *"Capable language models can outgrow the benefits of
> collaboration"*, **Nature Machine Intelligence 8(7):1157–1172**, 24 July 2026, 20 authors.

It is **retitled**, which is why arXiv carries no journal-ref and why it is hard to find under the
preprint name. The Nature version is paywalled; arXiv v3 is not.

⭐ **The retitle matters more than the correction.** The preprint was called *Towards a Science of
Scaling Agent Systems* — neutral. What survived peer review is called **"Capable language models
can outgrow the benefits of collaboration."** The capability-saturation effect, not the aggregate
mean, is what the reviewed literature chose to lead with — and it is a direct argument that
multi-agent structure buys less as the underlying model gets better. Anyone weighing a supervisor
tier here should read that title as the finding.

Stated plainly because this document exists to be trusted: the argument as previously written here
was **stronger than the evidence supporting it**. The conclusion did not change; the reason did.

This remains an important input for the research programme — it is the one place we hold real
evidence bearing on the Agent Army thesis — but it should be carried forward *with its interval*.
See `agent-army-research/research/answers/R01-answer-prior-art-and-novelty-boundary.md` and
`agent-army-research/migration/MIGRATION-REPORT.md` §"Product discoveries".

⛔ **`blueprints/orchestrator_team.yaml:18` still states the mean without the interval.** That is a
product artefact and a deliberate record, so it is flagged here rather than edited — but anyone
quoting it forward should quote the answer file, not the header.

## Why so little is implemented

Not neglect — an explicit scope decision. `README.md` §"What is deliberately absent":

| Not here | Unlocked by |
|---|---|
| Agent Army / supervisor tiers | **One certified team, plus evidence a tier helps** |
| Optimizer | A working eval |
| More than one comms topology | A second team that actually needs to talk to the first |
| Gym | The eval corpus plus a scoreboard |
| Platform UI | Numbers worth looking at |

`docs/research/agentic-factory-research-prompts.md:55` records the same call: *"Agent Army (level 5)
— **Cut for now**. Crucible already asked whether levels 4–5 are real structure or ceremony. With
zero certified teams…"*, and `docs/DEEP-REVIEW-PROMPT.md:228` encodes the unlock rule as
*"agent army ← one certified team"*.

**The precondition has not been met.** No team is certified today, so the gate on Agent Army work
in this repository has not opened.
