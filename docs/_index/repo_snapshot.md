# Repository snapshot — what the Agent Factory implementation actually is

**Measured 2026-09-02** against `agent-factory` @ `fc78074`, branch `main`, working tree dirty
(16 modified, 9 untracked).

**Purpose:** give an architecture reviewer enough of the real system to judge the proposals in this
corpus against it. Every claim here is either **CONFIRMED** (measured, with the command) or
**INFERRED** (a reading of the code, marked as such). Those two are never mixed in a sentence.

---

## ⛔ Five facts to hold before reading anything else

Each is `CONFIRMED` and each contradicts an assumption a reader arriving from the research packs is
likely to bring.

| # | Fact | Command |
|---|---|---|
| 1 | **The sole runtime dependency is `pyyaml`.** No DAG engine, no Prefect, no queue, no database, no vector store, no RAG, no async runtime, no web framework. | `cat pyproject.toml` |
| 2 | **Execution is synchronous Python plus `subprocess`.** 103 `subprocess` references; 1 `asyncio`. | `grep -rc subprocess --include=*.py factory evaluator_service scripts` |
| 3 | **No agent has ever completed a real run.** 10 run rows, **zero `PASS`**; 7 `agent_returned` events, **all `dry_run=True`**. | see §10 |
| 4 | **There is no LLM judge anywhere.** Every verdict is deterministic Python. `provider.py:11-13`: *"a provider never names its own verdict."* | `.agent-platform/PACK_CONFORMANCE.md` test 1.2 |
| 5 | **All persistent state is JSONL and JSON files under `.data/`**, which is gitignored and machine-local. | `cat .gitignore` |

---

## 1. Shape of the repository

```
agent-factory/
├── factory/               22,817 lines · 63 modules · THE PACKAGE
├── evaluator_service/        469 lines ·  5 modules · a deliberate sibling, not a submodule
├── scripts/                9,441 lines · 34 scripts · builders, probes, render checks
├── tests/                    954 tests · 50 modules
├── blueprints/                       2 · what "green" means, as data
├── evals/                            2 · the hashed corpus + its manifest
├── missions/                        12 · mission document sets
├── docs/                           563 files · the corpus this index describes
├── .agent-platform/                113 files · an imported pack, authority NONE
├── boot-prompts/                    23 · session handoffs
└── .data/                (gitignored) append-only ledgers, claims, bus, worktree state
```

`CONFIRMED`. Line counts from `wc -l`; test count from `pytest --collect-only -q`.

**There are no `apps/`, `services/`, `agents/`, `packages/` or `infra/` directories.** The research
packs propose that shape (`Agent Factory Vision.txt` §1); this repository does not have it.

---

## 2. Applications and services

`CONFIRMED`. There are **two** deployable things and one of them has never been deployed.

### `evaluator_service/` — the only network-facing service

Stdlib-only HTTP. **Three routes and no fourth:**

| Route | Contract |
|---|---|
| `GET /health` | what this evaluator *is*: identity, bundle hash, corpus, store |
| `POST /evaluate` | `{artifact_uri, artifact_sha256, run_id}` → a verdict |
| `GET /verdict/<id>` | read back a recorded verdict |

**There is no route that writes a verdict without scoring one**, and none that accepts a corpus from
the submitter. Everything the grading depends on — the corpus, the corpus root, the assertion set,
the identity — is resolved **from this service's own configuration, on every request**.

The verdict store is **write-once**: *"a verdict already recorded cannot be replaced by a later,
kinder one. Rollback to a nicer answer is the cheapest attack on a certification scheme, and it
needs no cleverness."*

It is a *sibling package*, not a module inside `factory/`, and imports `factory` rather than the
reverse — *"so lifting it out is a packaging change and not a refactor."*

⚠ `INFERRED`: it is designed to run somewhere the graded agent holds no credential for. **Nothing in
the repository records that it has been deployed anywhere**, and R3 ranks a separate *local* process
**5 of 5, "mostly theatre."** The boundary is correct in design and unproven in deployment.

### `factory/switchboard_p1.py` — the operator surface

A locally-served HTML surface (`scripts/switchboard_dev.py`). Renders a projection over existing
state; **adds no facts.** See §8.

---

## 3. The package — 63 modules, by role

`CONFIRMED` (paths, line counts, docstrings). Groupings are `INFERRED`.

### 3.1 The foundation — what "done" means

| Module | Lines | Role |
|---|---:|---|
| `contract.py` | 138 | `GreenContract` and the five verdicts. **Deliberately dependency-free.** ERROR checked before FAIL. |
| `evals.py` | 98 | `mutate_and_expect_failure` — the negative control |
| `corpus.py` | 110 | the known-good world as **hashed data**, verified on load; raises rather than degrading |
| `calibration.py` | 68 | the calibration point; no longer *builds* the world |
| `targets.py` | 24 | loads a `ConnectorTarget` from a blueprint — *the contract is code, "green" is data* |
| `connector_contract.py` | 316 | A1–A12. **Every assertion states a positive fact that must be observed** |
| `pbi_contract.py` | 498 | M1–M12, written **before** any Power BI agent existed |
| `redesign_contract.py` | 253 | R1–R4 on top of M1–M12, because a redesign is a different change shape |
| `live_probes.py` | 273 | real instruments for A1 and A5, reachable with no credential and no network |
| `certify.py` | 144 | CLI: judge one connector, emit a machine-readable verdict |
| `evaluator.py` | 242 | the agent's **only** route to a verdict, deliberately narrow |
| `assertions.py` | 278 | grounding, freshness, **8 evidence bases**, and the counterfactual maturity ladder |

### 3.2 State — append-only, evidence-gated

| Module | Lines | Role |
|---|---:|---|
| `tasks.py` | 409 | append-only store. Current state is a **fold over events**. `EvidenceRequired` raised by the store |
| `evidence.py` | 152 | four evidence classes, three states. Refusal lives in the store, not in a convention |
| `events.py` | 408 | the run event stream — *"the one record that cannot be rebuilt afterwards"* |
| `runs.py` | 301 | the lane run ledger; basis `RECORDED / RECONSTRUCTED / NOT-RECORDED` |
| `bus.py` | 157 | the **live** channel: ephemeral, machine-local, one file per writer |
| `findings.py` | 185 | reads the findings ledger **as data**, routed by `AFFECTS` |
| `claims.py` | 390 | `O_EXCL` locks; stale claims still block |
| `sessions.py` | 450 | live-session detection, verified against the **process table**, not file existence |
| `work.py` | 577 | one view model over the task store. *"This is not a second task system."* |
| `context.py` | 243 | `ContextRef` with a **required** non-empty source |

### 3.3 Measurement — 30 gates and the things that read them

| Module | Lines | Role |
|---|---:|---|
| `readiness.py` | 1,948 | **30 gates across 5 phases**, each measured from a named file at run time |
| `goals.py` | 86 | groups gates by goal; a goal with no measurable gate reports `NOT-MEASURED`, never `0%` |
| `board.py` | 167 | **the board is generated from the gates.** There is no task list in this file |
| `plan_gates.py` · `roadmap.py` | 312 · 377 | same refusal, restated: no hand-typed list |
| `flow.py` | 173 | the readiness graph laid out **from the data** |
| `metrics.py` | 75 | raises `GoodhartViolation` if an activity metric names no outcome |
| `reliability.py` | 177 | the two metrics that need no new field; carries `instrument_live` |
| `preflight.py` | 678 | known-failure preflight — deterministic key lookup, **no retrieval** |
| `schedule.py` | 217 | *"when will this be done"* — by declining to produce a date it cannot support |
| `coordination.py` | 240 | coordination signals, **deliberately not summed into one number** |

### 3.4 Execution — the control plane

| Module | Lines | Role |
|---|---:|---|
| `control.py` | 742 | **RunController — the assembly line.** Ticket in, verdict and durable record out |
| `deploy.py` | 281 | worktree + turn cap + dollar cap + persisted `AttemptLedger` |
| `provider.py` | 212 | the provider seam — the only place that knows how an agent is started |
| `worktrees.py` | 130 | one git worktree per lane |
| `lanes.py` | 408 | the conflict graph. `recommend()` returns *(lane, score, reason)* — *"a bare ranking is an oracle"* |
| `launch.py` | 217 | *"may I run an agent right now — and if so, how far may I trust it?"* |
| `presets.py` | 375 | ticket type + size → a starting configuration, **with its reasons** |
| `verifiers.py` | 218 | turns a preset's *named* verifier into a callable the controller runs |
| `blueprint.py` | 90 | **the config IS the version** |
| `finish.py` | 186 | assert, push, announce, release — and **never merge** |
| `teamplan.py` | 153 | per-team step sequencing over the board's dependency edges |
| `repo.py` | 72 | one resolver for *where are we?*, because three modules answered it three ways |
| `runtime_deps.py` | 164 | every runtime capability a command needs, checked **before it starts** |

### 3.5 Projection and artifacts

| Module | Lines | Role |
|---|---:|---|
| `client_review.py` + `_render.py` | 1,191 + 704 | a client-safe read model, and a single self-contained HTML file with no backend |
| `case_study.py` + `_render.py` | 614 + 603 | the second artifact type — *the proof the compiler shape generalises* |
| `projection.py` | 100 | the projection boundary — **an ALLOW-list, never a deny-list** |
| `forensic_source.py` | 203 | the prose boundary, **machine-validated**, because structured code depends on it |
| `switchboard.py` · `_p1.py` · `_render.py` | 1,420 · 1,291 · 493 | the operator surface, split projection/render |
| `console.py` | 236 | read what a session said, and reply. ⛔ *"This is NOT a terminal"* |
| `session.py` · `workplan.py` · `handoff.py` | 280 · 390 · 210 | session brief, work-session cards, generated handoffs |
| `operator.py` | 85 | human answers to blockers declared up front. Gitignored on purpose |

### 3.6 The research programme, as code

| Module | Lines | Role |
|---|---:|---|
| `dispatch.py` | 441 | which prompts are waiting — *and which ones are lying about it* |
| `synthesis.py` | 361 | is the decision record still current with the answers on disk |
| `research_run.py` | 380 | running a research pass **in the repo** |
| `registry.py` | 316 | which workflow implements a (shape, layer), and what version ran |

⚠ These four make `docs/research/` **executable**. `dispatch.py` globs it at module scope. Moving or
renaming files there breaks the build.

---

## 4. Module dependency structure

`CONFIRMED` — measured by AST, resolving `from . import x as _x` as well as `from .x import y`.

**Most depended-upon:**

| Module | In-package consumers |
|---|---:|
| `repo` | 16 |
| `contract` | 12 |
| `readiness` | 9 |
| `lanes` | 8 |
| `tasks` · `board` | 6 |
| `claims` · `worktrees` | 5 |
| `evidence` · `connector_contract` · `sessions` | 4 |

⭐ `contract.py` being second, at 138 lines and **zero dependencies of its own**, is the architecture
in one number: the success object is the most-depended-upon thing in the package and depends on
nothing.

**Fourteen modules have zero in-package consumers** — `certify`, `control`, `demo`, `finish`,
`flow`, `launch`, `plan_gates`, `reliability`, `research_run`, `runtime_deps`, `session`,
`switchboard_p1`, `teamplan`, `workplan`. `INFERRED`: these are **entry points**, not dead code —
20 modules carry an `if __name__ == "__main__"` block and most of this list is in it.

⚠ **A method note that is itself a finding.** The first version of this measurement missed
`from . import bus as _bus` entirely and reported 38 modules with zero consumers. That is
`docs/findings.d/F84` reproduced exactly — *"the zero-consumer count was measured by a blind grep"* —
in the instrument written to describe this repository. The corrected instrument is the one above.
**Treat any "unused module" claim about this codebase with suspicion unless the counter is shown to
see the aliased form.**

---

## 5. The agent runtime

`CONFIRMED` in structure; ⚠ **almost entirely unexercised.**

```
ticket
  → presets.for_ticket()      pick model, effort, caps, prohibitions, verifier
  → blueprint                  hash the config; the hash IS the version
  → claims.claim(lane)         O_EXCL lock, refuse on overlap
  → worktrees.ensure()         isolated git worktree
  → provider.start()           the ONLY place that knows how an agent is launched
      └─ deploy.py             `claude` CLI + --max-turns + --max-budget-usd + stream-json
  → transcript                 streamed to disk
  → verifiers.resolve()        named check → callable
  → GreenContract.run()        deterministic verdict
  → events.append()            run_started … verdict_assigned … run_finished
  → runs.record()              the durable ledger row
  → finish()                   assert, push, announce, release. NEVER merge
```

**What is real:** every box above exists, is imported and is tested.

**What is not:** the loop has never completed with a real agent. `control.py`'s own docstring records
why it was written — *"every part below already existed and was tested. **Nothing called them in
order**, which is why `presets`, `worktrees`, `claims`, `deploy` and `runs` sat at zero consumers
between them."*

⚠ **`provider.py` exists to contain a known risk**, stated in its docstring: `deploy.py:230`
hard-codes `--max-turns`, `--max-budget-usd`, `--output-format stream-json` and `--model` against
*"an argv surface that is undocumented, unversioned and unpinned."*

---

## 6. Orchestration

`CONFIRMED`. **There is no orchestration engine.**

- **No DAG runner, no Prefect, no Airflow, no queue, no scheduler daemon.**
- Parallelism is **human-launched Claude Code sessions**, one per lane, isolated by git worktree.
- What can run in parallel is a **file-locality** question, not a dependency question:
  `lanes.conflicts()` computes which lanes write the same files; the ceiling is the maximum
  independent set of that graph.
- Mutual exclusion is `claims.py` — `O_EXCL` locks with liveness checked against the **process
  table**.
- Ordering within a team is `teamplan.py` over the board's `block` edges (**25 live**).

`INFERRED`: this is a deliberate scope decision, not an omission. `README.md` gates the missing
pieces behind named preconditions, and `.agent-platform/PACK_CONFORMANCE.md` 0.5 records the
measurement plainly: *"no DAG engine, no Prefect, no queue."*

---

## 7. Configuration and schemas

`CONFIRMED`.

| Artifact | What it is | Where |
|---|---|---|
| `AgentSpec` / `TeamSpec` | the config that **is** the version, content-hashed | `factory/blueprint.py` |
| `ConnectorTarget` | what "green" means for one connector, as data | `factory/targets.py` + `blueprints/*.yaml` |
| Presets | ticket type + size → starting config, with reasons, escalation conditions, budgets, prohibitions, verifier state | `factory/presets.py` |
| `FAILURE_TAXONOMY` | 10 families, **closed set in code**; the YAML is its index | `factory/preflight.py` + `docs/protocol/FAILURE_TAXONOMY.yaml` |
| `HANDOFF_CONTRACT.schema.json` | ⛔ DESIGN. Nothing reads it | `docs/protocol/` |
| 8 bootstrap-pack schemas | ⛔ imported, authority NONE, nothing reads them | `.agent-platform/bootstrap/schemas/` |

⚠ **Two known configuration defects, both recorded:**
- `F90` **(OPEN)** — `TeamSpec.repo` is inside the version hash and **nothing reads it**.
- `SYNTHESIS` §15.1 — `g_version_hash_is_complete` **could never pass**: a U+0008 in its regex. The
  gate measuring configuration completeness was itself broken.

**MEASURED:** the version hash covers **6 of 15** declared dimensions.

---

## 8. Storage

`CONFIRMED`. **There is no database.** All state is files.

| Path | Shape | Committed? | Content |
|---|---|---|---|
| `.data/tasks.jsonl` | append-only JSONL | gitignored | **273 events** — the authoritative work record |
| `.data/events.jsonl` | append-only JSONL | gitignored | **61 run events** |
| `.data/runs.jsonl` | append-only JSONL | gitignored | **10 run rows** |
| `.data/bus/*.jsonl` | one file **per writer** + cursors | gitignored | live lane-to-lane messages |
| `.data/claims/*.json` | `O_EXCL` lock files | gitignored | who holds which lane |
| `.data/operator/*.json` | JSON | gitignored | human answers to declared blockers |
| `.data/attempts.json` | JSON | gitignored | the attempt ledger that survives restart |
| `evals/corpus/*.json` | hashed JSON + `MANIFEST.sha256` | **committed** | the known-good world |
| `docs/board/tickets.json` | JSON | **committed** | a **DERIVED** snapshot; *"never hand-edit"* |

⭐ **The committed/gitignored split is the design.** Authoritative mutable state is machine-local and
append-only; what is committed is either a hashed fixture or a derived snapshot that declares its own
source.

⚠ **Consequence for a reviewer:** cloning this repository gives you the *code* and the *corpus*, and
**none of the run history**. The numbers in this file came from a machine, not from the repository.

---

## 9. Memory

`CONFIRMED`. **There is no memory system in the sense the research packs mean.**

No vector store, no embedding index, no graph database, no retrieval layer, no RAG. The single
`embedding` match in the codebase is the English word in an HTML docstring.

What exists instead — four durable stores, each narrow and each with an enforcement mechanism:

| Store | Mechanism | Enforcement |
|---|---|---|
| `docs/findings.d/` — 33 corrected premises | one file per finding; `AFFECTS` routes to lanes | a test derives the expected set from the directory and **fails on any file the parser cannot see** |
| `factory/preflight.py` — 10 failure families | **deterministic key lookup**, no similarity | shadow-mode replay against real history |
| `factory/tasks.py` — 273 events | append-only fold; evidence-gated close | the store raises `EvidenceRequired` |
| `factory/context.py` — context refs | a **required** non-empty source | refuses a ref that cannot point back at its origin |

⚠ `docs/agent-army/CURRENT_STATE.md` grades the first of these `PARTIAL` and states the limit
precisely: *"genuinely knowledge-object-shaped, but untyped Markdown with no provenance schema, no
confidence, no promotion path and no reuse across repositories."*

---

## 10. Evaluation — the measured state

`CONFIRMED`. Reproduce:

```bash
python -m factory.certify blueprints/windsorai_client_a.yaml --calibrate
python -c "import factory.readiness as r; print(len(r.GATES))"
python -m pytest --collect-only -q | tail -1
python -c "import json;rows=[json.loads(l) for l in open('.data/runs.jsonl')];print(len(rows),[r['outcome'] for r in rows])"
```

| Measurement | Value |
|---|---|
| Contract result | `connector-e2e/windsorai@CLIENT-A: PASS (PASS=12)` — **REPLAYED against a recorded run, not live** |
| Assertions calibrated with a known-bad | **12 of 12**, enforced by `test_every_assertion_has_been_proved_able_to_fail` |
| Eval corpus | **1 file · 1 connector · 6,762 bytes.** 48 connectors never scored |
| Readiness gates | **30** — judgement 8, certification 8, handover 7, bounded 4, loop 3 |
| Tests | **954 across 50 modules** |
| Run ledger | **10 rows** — `FINISHED`×3, `FAIL`×1, `UNMEASURABLE`×6, **`PASS`×0** |
| Event stream | **61 events** — verdicts `FAIL`×2, `UNMEASURABLE`×12, `NOT_RUN`×1 |
| Real dispatches | **0.** All 7 `agent_returned` events carry `dry_run=True` |
| Reliability metrics | **2 of 10 built.** First-Pass GREEN Rate `0/8` with `instrument_live = False` |

⭐ **The last three rows are the most important facts in this document.** The instruments are
extensive and calibrated; the subject has not been measured.

---

## 11. UI

`CONFIRMED`. Four surfaces, all **projections**, none a source of truth.

| Surface | Served how | Note |
|---|---|---|
| **Switchboard** P0 + P1 | local HTTP (`scripts/switchboard_dev.py`) | every field read on every call from something already authoritative |
| **Board / tracker** | generated HTML | `docs/board/index.html`, `tracker.html` (gitignored) |
| **Published artifacts** | static HTML, single file, no backend | `docs/artifacts/` — ⚠ **read by code**; `readiness.py` yields `agent-factory.html` into the suite fingerprint **by name** |
| **Client-facing artifacts** | static HTML | evidence drill-down uses `<details>`, so it **works with JavaScript disabled** |

**Rendered validation is a first-class instrument:** 7 render-check scripts, 85 captures at three
viewports in both colour schemes, **plus a no-JS capture as the negative control.**

⛔ **No spatial/world UI, no semantic zoom, no agentic IDE.** `README.md` lists Platform UI as
deliberately absent, unlocked by *"numbers worth looking at."*

---

## 12. APIs

`CONFIRMED`.

- **Outward:** the evaluator's three routes (§2). That is the entire public API surface.
- **Inward:** the switchboard's local HTTP routes, tested by `tests/test_switchboard*.py` and
  `tests/test_tracker_routes.py`.
- **Not present:** no MCP server, no A2A endpoint, no agent-to-agent RPC, no webhook receiver.

---

## 13. Deployment and CI

⚠ **`UNKNOWN`, and the honesty matters.**

- `ls .github` → *No such file or directory*. `CONFIRMED`: **no GitHub Actions CI in this checkout.**
- `SYNTHESIS` §8 item 11 lists *"CI on push in `agent-factory`"* as **not started**.
- The evaluator is *designed* to be deployed elsewhere. Nothing records that it has been.
- Installation is `pip install -e ".[dev]"` plus `python -m playwright install chromium` — and the
  browser step is a **real step**: nothing that validates a rendered page works without it.
- `python scripts/meeting_ready.py --check-env` names everything missing in one message. That module
  exists because an operator hit **three separate missing dependencies in sequence**, each only after
  the previous was fixed (`factory/runtime_deps.py` docstring).

---

## 14. Observability

`CONFIRMED`, and it is the thinnest layer in the system.

| Present | Absent |
|---|---|
| Run event stream (`events.py`, 61 events) | ⛔ a **structured trajectory object** — `deploy.py` streams a raw transcript |
| Durable run ledger with a basis per row | ⛔ OpenTelemetry / GenAI semantic conventions |
| Live per-writer message bus | ⛔ any trace store (Langfuse, LangSmith, Weave) |
| 2 reliability metrics with Goodhart pairing | ⛔ 8 further metrics, all `NOT-RECORDED` or `NOT-MEASURABLE` |
| `instrument_live` flags on every rate | ⛔ any alerting or notification path |

`docs/research/agent-factory-concept-inventory.md` §4.2 names this as a **`NOT-SEARCHED` axis** — R1
was scoped to *eval frameworks* and its "don't add one" verdict **does not cover tracing.**

---

## 15. The major implementation seams

`INFERRED` — this is a reading of the code, and the most useful thing in this document for someone
deciding where to change it.

| # | Seam | Where | Why it matters |
|---|---|---|---|
| 1 | **Contract ↔ target** | `contract.py` / `targets.py` + `blueprints/` | The contract is code; "green" is data. One contract judges every connector. **The cleanest seam in the system.** |
| 2 | **Grader ↔ graded** | `evaluator.py` / `evaluator_service/` | Correct in design, unproven in deployment. R3's rank 5 vs rank 1 is *where it runs*, not *how it is written*. |
| 3 | **Provider seam** | `provider.py` | The only place that knows how an agent is started. Contains an undocumented, unpinned argv surface. **The natural insertion point for any other agent runtime.** |
| 4 | **Projection ↔ render** | `client_review.py` / `_render.py`, `case_study.py` / `_render.py`, `switchboard.py` / `_render.py` | Applied three times. *"The join is the part worth testing, and a test that has to parse HTML to assert a dependency rule is testing the wrong thing."* |
| 5 | **Projection boundary** | `projection.py` | An **ALLOW-list** of what may leave the Factory, per artifact type. Extracted when a second artifact type needed it, *"because a boundary that exists twice is a boundary that will diverge once."* |
| 6 | **Record ↔ channel** | `events.py`/`tasks.py` vs `bus.py` | Durable versus live. A decided split with a written rationale (F70/F71). |
| 7 | **Gates ↔ board** | `readiness.py` → `board.py` → `flow.py`/`roadmap.py` | Every non-passing gate **is** a task, derived. Add a gate and a task appears. |
| 8 | **Repo resolution** | `repo.py` | 16 consumers — the most depended-upon module. Exists because three modules answered *"where are we?"* three different ways and only one was right. |
| 9 | **Research ↔ code** | `dispatch.py`, `synthesis.py`, `readiness.py` | ⚠ `docs/research/` **is imported.** Markdown that is part of the build. |
| 10 | **Prose ↔ structure** | `forensic_source.py` | Structured code depends on prose structure, so the prose boundary is **machine-validated**. |

---

## 16. What an architecture reviewer should NOT assume

| Assumption | Reality |
|---|---|
| There is an agent framework here | There is a **contract**, a **task store** and a **launcher**. No framework. |
| Agents talk to each other | ⛔ Deliberately not built. `bus.py` carries lane-to-lane nudges between **human-launched** sessions. |
| There is a memory or knowledge layer | ⛔ None. Four narrow durable stores, no retrieval. |
| There is an optimizer, a gym, or a simulator | ⛔ None. Each is deliberately absent with a named unlock. The 16 `simulat*` matches are the *maturity label* `SIMULATED` — an honesty marker, the opposite of a simulator. |
| `docs/` is documentation | ⚠ Partly. `docs/research/`, `docs/artifacts/`, `docs/findings.d/`, `docs/specs/`, `docs/evidence/`, `docs/board/` are **read by code**. |
| The repository is the system | ⚠ The run history is `.data/`, gitignored and machine-local. A clone contains no evidence that anything ever ran. |
| Agent Army research is here | ⛔ It moved to the **sibling repository** on 2026-08-30. `docs/agent-army/` is the boundary only. |
| The proposals in `docs/raw_research/` describe this system | ⛔ **They were written without access to it.** `.agent-platform/README.md`: *"treat the description as a proposal from a stranger."* |

---

## 17. Confirmed vs inferred — the ledger for this document

**CONFIRMED** (a command was run, and its output read): the dependency list; line and module counts;
the test count; the gate count and phase distribution; the module dependency graph; the run, event
and task ledger contents; the absence of `.github`; the absence of a database, vector store, async
runtime and web framework; the three evaluator routes; `subprocess` and `asyncio` counts; contract
calibration output; corpus size; the committed/gitignored split.

**INFERRED** (a reading of the code, marked as such in place): the grouping of modules into roles;
that the fourteen zero-consumer modules are entry points rather than dead code; that the absence of
an orchestration engine is deliberate rather than incomplete; the seam analysis in §15; that the
evaluator has never been deployed remotely (an absence of evidence, not evidence of absence).

**⛔ NOT ESTABLISHED, and stated rather than guessed:** whether CI exists anywhere outside this
checkout; whether the evaluator has ever run as a separate principal in a real deployment; what the
two unread `.docx` files contain; whether the `windsorai` fixture's declared primary key is correct
(`docs/research/README.md` §4 question 3 — **if it is wrong, the calibration world is built on a
mistake**).
