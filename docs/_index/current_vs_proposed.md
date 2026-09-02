# Current vs proposed — capability matrix

**Generated 2026-09-02** against `agent-factory` @ `fc78074` (branch `main`).
**Amended 2026-09-02** @ `7b19baf` by the `.agent-platform` delta pass — Part 10, nine rows, plus
a re-measured row count in the Summary that turned up a pre-existing drift of three. See
[`agent_platform_delta_synthesis.md`](agent_platform_delta_synthesis.md).

---

## How to read this table

**The column vocabulary is not invented for this document.** `factory/assertions.py` already defines
a maturity ladder for exactly this question, enforced by a dataclass that raises rather than by a
convention. The six requested columns map onto it:

| Column | `factory/assertions.py` term | Means |
|---|---|---|
| **Research only** | `PROPOSED` | Named in a document. Not designed. |
| **Designed** | `SIMULATED` | A design exists. Nothing is built. |
| **Specified** | — | A contract, schema or spec exists that code could be written against |
| **Partial** | between `SIMULATED` and `IMPLEMENTED_NOT_EXERCISED` | Some mechanism exists and is cited; the capability as described is not built |
| **Implemented** | `IMPLEMENTED_NOT_EXERCISED` | The code exists, is imported and is covered by a test |
| **Validated** | `EXERCISED` | **It ran, against real work, and we saw it.** Requires a reference to the evidence of it running |

⭐ **The distinction between the last two columns is the one that matters**, and the corpus states
why in code:

> Naming the code shows it **exists**; it does not show it **RAN**. […] even a fully built
> capability that no mission invoked is `IMPLEMENTED_NOT_EXERCISED`, not `EXERCISED`.
> — `factory/assertions.py`

**`UNKNOWN` is used wherever the repository does not support a conclusion.** It is a real value, not
a gap in the analysis, and it appears three times — all in Part 9 (CI, deployment target,
observability). Elsewhere, an empty row would mean the same thing, so every capability row carries
at least one mark.

**Legend:** `●` = the capability sits at this level · `○` = partially · blank = no.
**Evidence** cites the path that establishes the level. A row with no evidence path is `UNKNOWN`.

---

## Part 1 — Measurement, contracts and gates

*This is where the estate is strongest, and it is the part no inbound research pack describes.*

| Capability | Research only | Designed | Specified | Partial | Implemented | Validated | Evidence |
|---|---|---|---|---|---|---|---|
| Five-verdict contract (PASS/FAIL/UNMEASURABLE/ERROR/NOT_RUN) | | | ● | | ● | ● | `factory/contract.py:32`; `tests/test_contract.py:68`; ISO/IEC 9646 · ITU-T Z.140 §24.2 lineage in `README.md` |
| Connector GreenContract A1–A12 | | | ● | | ● | ○ | `factory/connector_contract.py`; `docs/evidence/phase-a-windsorai.md` — **REPLAYED against one recorded run, not a live measurement** |
| Power BI model contract M1–M12 | | | ● | | ● | | `factory/pbi_contract.py` — built **before** any Power BI agent, deliberately |
| Model-redesign contract R1–R4 | | | ● | | ● | | `factory/redesign_contract.py`; motivated by `docs/findings.d/F89` |
| Negative control (`mutate_and_expect_failure`) | | | | | ● | ● | `factory/evals.py`; `tests/test_connector_contract.py::test_every_assertion_has_been_proved_able_to_fail` — 12/12 assertions calibrated |
| Eval corpus as hashed, tamper-evident data | | | | | ● | ● | `evals/corpus/` + `MANIFEST.sha256`; `factory/corpus.py` raises `CorpusError`. ⛔ **ONE file, ONE connector, 6,762 bytes; 48 connectors never scored** |
| Grader separation (evaluator as a principal) | | | | ○ | ● | ○ | `evaluator_service/{app,service,store}.py`, 3 routes, write-once store; `docs/evidence/evaluator-isolation-2026-08-22.md`. ⚠ R3 ranks a *local* process **5 of 5, "mostly theatre"** — correct in design, weak in deployment |
| Readiness gates (30, measured from files at run time) | | | | | ● | ● | `factory/readiness.py`; MEASURED 2026-09-02: `len(GATES) == 30` |
| Gates refusing an empty population | | | | | ● | ● | `tests/test_gates_refuse_an_empty_population.py`; `docs/findings.d/F94` — 6 gates were passing over an absence; fixed with 15 tests |
| Evidence classes (TARGET/CONSUMER/REGRESSION/ROLLBACK) | | | | | ● | ● | `factory/evidence.py:48,68-70`; `factory/tasks.py:163` raises `EvidenceRequired`. ⚠ Cannot verify ROLLBACK was captured *before* the mutation (`evidence.py:27`) |
| Goodhart pairing (activity metric requires an outcome anchor) | | | | | ● | ● | `factory/metrics.py` raises `GoodhartViolation`; `factory/reliability.py` `suspicious()` |
| Counterfactual maturity ladder | | | | | ● | ● | `factory/assertions.py` `MATURITIES`; enforced by `Counterfactual.__post_init__`; rendered at `case_study_render.py:274` |
| `instrument_live` — a zero from a blind instrument is flagged | | | | | ● | ● | `factory/reliability.py` `Rate.__str__`; `tests/test_recurrence_preflight.py` carries the negative control |
| Quality gates (7 named) | | ● | ● | ○ | | | `docs/protocol/QUALITY_GATES.md` — 2 built (KNOWN_FAILURE, VERIFICATION), 1 half (OUTPUT_CONTRACT, opt-in per call), 4 DESIGN |
| Expected-work manifest + `scope_hash` | ● | ● | | | | | `R3` calls it *"the biggest missing control"*; `absorption-backlog.md` AB-01 — **the build order has no step for it** |
| `pass@k` / `pass^k` reporting | ● | | | | | | `R1`; `absorption-backlog.md` AB-07 |
| First-attempt contract pass rate (FACPR) | ● | | | | | | `R3`; `absorption-backlog.md` AB-02 |
| Side-effect / reconciliation checks | ● | | | | | | `R1` (graded **High** omission) and `R17` §4.7 independently: *"none of these receipts describes what the agent did to a shared warehouse"* |
| Fitness Qualification Gate (5 pre-search tests) | | ● | | | | | `R4`; `absorption-backlog.md` AB-05. ⭐ Test 2 (known-bad sensitivity) is already implemented as the negative control |

---

## Part 2 — Agents and configuration

| Capability | Research only | Designed | Specified | Partial | Implemented | Validated | Evidence |
|---|---|---|---|---|---|---|---|
| Config-as-identity (content-derived version id) | | | ● | | ● | ○ | `factory/blueprint.py`; `factory/readiness.py` `VERSION_DIMENSIONS`. ⛔ **6 of 15 dimensions covered**; `SYNTHESIS` §15.1 — the gate checking this *could never pass* (a U+0008 in its regex) |
| Baseline presets by ticket type and size | | | | | ● | ○ | `factory/presets.py` — evidence-labelled configs with reasons, escalation conditions, budgets, prohibitions, verifier state |
| Verifier registry (named check → callable) | | | | | ● | ○ | `factory/verifiers.py`; `docs/findings.d/F87` — the one preset claiming a WIRED verifier had **nothing behind it** |
| Bounded deployment (worktree + turn cap + dollar cap) | | | | | ● | ○ | `factory/deploy.py`; `AttemptLedger` persisted so a cap survives restart. ⚠ `docs/findings.d/F85` — two *plan-only* runs spent the cap that stops a real one |
| Provider seam (how an agent is started, swappable) | | | | | ● | | `factory/provider.py` — *"a provider never names its own verdict"* |
| Four-layer agent model (genotype/phenotype/history/fitness) | | ● | ● | | | | `agent_genome_research_pack/01_CURRENT_DESIGN_SYNTHESIS.md` + `schemas/agent_genome.schema.yaml`. Only the genotype layer exists |
| Five field classes (TUNABLE/DECLARED/MEASURED/DERIVED/POLICY) | | ● | ● | | | | `agent_genome_research_pack/schemas/field_classification.yaml`. ⭐ Same idea as `SYNTHESIS` §6's never-optimise list, reached independently |
| Agent registry + lockfile | | ● | ● | ○ | | | `agent-config-research-pack/configs/resolved-config.lock.example.json`; `factory/registry.py` distinguishes proven/declared/unbuilt workflows but is not a registry of agents |
| Agent phenotype / communication phenotype presets | | ● | ● | | | | `agent_genome_research_pack/presets/communication_phenotypes.yaml` |
| Agent health vector / mission requirement vector | ● | ● | | | | | `agents_as_configuration_research_pack/02_CONCEPTS/MISSION_READINESS_AND_READY_UP.md` |
| Pre-deployment readiness uplift (READY-UP) | ● | ● | ● | | | | ⚠ **Contested** — `contradictions.md` CN-04 |
| Relationship edges (14 dimensions, versioned) | | ● | ● | | | | `agent_genome_research_pack/schemas/relationship_edge.schema.yaml`. Zero multi-agent runs, so zero edges observed |
| SIHRE cognitive kernel / morphological cognition | ● | | | | | | `agent2_sihre_consolidation_pack/02,04` |
| Cognitive portfolio / error-correlation selection | ● | | | | | | `agent2_sihre_consolidation_pack/05` + `DR02` |
| Contextual Bayesian trust / earned autonomy | ● | | | | | | `agent2_sihre_consolidation_pack/03` + `DR04` |
| Agent physiology / homeostasis / graceful degradation | ● | | | | | | `agent2_sihre_consolidation_pack/03` + `DR05` |
| Viable Cognitive Entity (Agent 2.0) | ● | | | | | | `agent2_sihre_consolidation_pack/03` + `DR08`. Its own §08 says the claim needs prior-art evidence first |

---

## Part 3 — Teams, organizations and orchestration

| Capability | Research only | Designed | Specified | Partial | Implemented | Validated | Evidence |
|---|---|---|---|---|---|---|---|
| Lanes — parallelism bound by file locality | | | | | ● | ● | `factory/lanes.py:125`; MEASURED: 3 lanes, 20 commits, **zero cross-lane conflicts** |
| Worktree per lane | | | | | ● | ● | `factory/worktrees.py`; R5 and R6 reached it independently |
| Claims — mutual exclusion verified against the process table | | | | | ● | ● | `factory/claims.py` (O_EXCL); `factory/sessions.py`; `tests/test_claim_race.py`, `test_contention.py` |
| Team step sequencing over a dependency graph | | | | | ● | ○ | `factory/teamplan.py`; `factory/board.py` `DEPENDS`; 25 live block edges |
| RunController — ticket in, verdict and durable record out | | | | | ● | ○ | `factory/control.py`. ⚠ **Every recorded run was `dry_run=True`** |
| Three-agent orchestrator team | | | ● | | ● | ● | ⛔ **BUILT, TESTED AND REJECTED ON EVIDENCE.** `blueprints/orchestrator_team.yaml` — kept, not deleted, with a quantified unlock threshold |
| Single-worker + non-LLM verifier + human topology | | | ● | | ● | ○ | `R2`'s verdict; no LLM judge exists anywhere (`PACK_CONFORMANCE.md` 1.2) |
| Adaptive team formation / mission matching | ● | ● | | | | | ⛔ Deferred with a quantified unlock: ≥200 adjudicated examples plus static misrouting ≥10% |
| Eligibility filter with a negative control | | ● | | | | | `R19` §7 |
| Org-IR / organization compiler | ● | ● | ● | | | | `agent-factory-bootstrap-pack/schemas/org-ir.seed.schema.yaml` (marked *seed only*). ⛔ Category refuted — `contradictions.md` CN-01 |
| Organization presets (10 named) | ● | ● | | | | | ⚠ `factory/presets.py` is an **agent** preset library, not an organizational one |
| Arbitrarily nested service designations (topology as data) | ● | ● | | | | | `army_ui_concept_pack/05`; `chat_design_pack/06` |
| Formations / formation compiler | ● | | | | | | `chat_design_pack/00`; zeus pack Gate 5 requires it to *prove representational value* first |
| Missions as an object with a lifecycle | ● | | ● | ○ | | | ⛔ `CURRENT_STATE.md`: **no mission object, schema or lifecycle anywhere**. `missions/` is a directory of documents; `docs/specs/marketing-model-reconstruction-v1.md` is the closest thing to a mission spec |
| Higher-order structures (councils, guilds, federations, markets) | ● | ● | | | | | ✅ **Source now read.** Twelve architecture cards + an L1–L8 ladder in `converted/Beyond_Agent_Armies…md` §2, §4. `C-OR-04` raised `idea → designed`. ⛔ Wave 0's counter is unaddressed: supervisor tiers are `DO NOT BUILD` |
| Agent Army / supervisor tiers | ● | | | | | | ⛔ Deliberately absent. **Zero approved concepts, zero handoffs.** `CURRENT_STATE.md`'s 14-term sweep across `factory/` returns nothing |
| Federation | ● | | | | | | MEASURED: zero occurrences of `federat*` anywhere |
| Stigmergic coordination / organizational fields | ● | | | | | | MEASURED: zero occurrences |

### Added 2026-09-02 — seven capabilities recovered from the two converted `.docx`, plus one operator-proposed

⭐ **Read the Evidence column before the ● marks.** The striking result is that **three of these eight
are already PARTIAL**, and the source documents propose all three as new P0 substrate at
`Effort 3/5`. Their *direction* is not challenged by this; their **effort estimates are wrong in this
estate**, and a synthesis that adopts the Pack's sequencing without re-costing will under-value work
already done and over-cost work already started.

| Capability | Research only | Designed | Specified | Partial | Implemented | Validated | Evidence |
|---|---|---|---|---|---|---|---|
| **Mission hypergraph** — typed `MissionNode`/`MissionEdge`/`Artifact`/`Evidence` graph (`C-OR-06`) | | ● | | ● | | | ⭐ MEASURED: `factory/board.py:108 critical_path()` — *"longest dependency chain still unmet"* — over 30 gates and **11 declared dependency edges**; rendered `roadmap.py:276`; drawn `flow.py:52`. ⚠ **Its live output is 2 hops** (`['cost', 'ceiling']`), and `flow.py`'s docstring says *twelve* edges against a measured 11. At ticket scale `findings.d/F98` records **25 live block edges** on `.data/tasks.jsonl`. **ABSENT: the typing, and any unification of the gate graph with the ticket graph.** ⚠ Pack §6.1 ranks this P0 #1 at `Effort 3/5, Evidence High` as though greenfield |
| **Constitutional type system** — organizations that fail to compile (`C-OR-07`) | ● | ● | | | | | Pack §6.2 (P0 #2); `Beyond…` card C. Nothing in `factory/` compiles an organization. Nearest built: `C-GV-03`, `C-EV-07` — both enforce at run time on one agent. ⛔ Blocked behind the sibling's unresolved question 1: *is there any boundary that can enforce authority?* |
| **Shadow twin / counterfactual organization** (relates `C-EV-10`) | ● | ● | | | | | Pack §6.3 (P0 #3). ⚠ **Not the same object as `C-EV-10`.** `factory/assertions.py`'s `Counterfactual` has **no `status` field** and is deliberately un-renderable beside a real outcome — a *documentation* object. The Shadow Twin is a *runtime* organization. The two must not be conflated in a synthesis |
| **Bounded self-hosting reconciliation** — quarantine / rollback / route-to-last-certified (`C-SI-01`) | ● | ● | | | | | Pack §6.5 (P0 #5, highest score `4.75/5`). ⭐ Its constraint is the valuable part: *"one controller: certification loss → quarantine → fallback → human-visible incident. **No autonomous code edits.**"* This is `C-EV-03` scaled to organizations — the sibling states it as *"an organization that can certify its own capabilities is not certified"* |
| **Mission Assurance Receipt** — trust as a client-facing surface (`C-GV-06`) | | ● | | ● | | | ⭐ **Every one of its nine sections already has a producer**: `contract.py:17-21` (verdict), `corpus.py` (corpus hash), `evidence.py:48,68-70` (classes and states), `runs.py:42` (cost basis). *"The record is a join, not a new subsystem."* ABSENT: the join, the rendering, and a `limits.unmeasured` section the sibling calls load-bearing and §9 omits |
| **Quality-diversity organization archive** — many niche elites (`C-OR-08`) | ● | | | | | | Pack §6.11 (P2); `Beyond…` card G. ⛔ **Two blockers on file:** the simulation substrate is measured `ABSENT` everywhere (`PRODUCT-BOUNDARY.md` Layer 5), and **CN-29** — IMACS says every learned organizational result is model-binding-specific and expires with the binding |
| **Knowledge metabolism** — decay, contradiction load, active forgetting (`C-KN-07`) | ● | | | | | | `Beyond…` hypothesis 4; Pack §7. `factory/context.py:121,:71` already carries `source`, freshness and confidence — the three fields a decay policy would read. Nothing decays or forgets. ⚠ Stated in terms of `Claim`, a noun Wave 0 **deprecated** (four live senses measured in one codebase) |
| **Goal-aware adaptive/dynamic orchestration** (`C-TM-06`) | ● | | | ● | | | ⭐ MEASURED: dynamic critical path **BUILT** (`board.py:108`); adaptive prioritisation **BUILT** (`coordination.py:100 prioritise()`, ordering by transitive downstream-blocked count + critical-path membership + wait + session liveness, **rendering its reasoning**); mutable DAG **BUILT** (F98); deadline-aware scheduling **BUILT AS A REFUSAL** (`schedule.py`). ⛔ **Precondition unmet:** `schedule.py:26` — *"No deadline has been stated anywhere in the programme."* And `SYNTHESIS.md:1389` bounds the scheduling half: *"none touch the critical path `T∞`"* |

---

## Part 4 — Communication

| Capability | Research only | Designed | Specified | Partial | Implemented | Validated | Evidence |
|---|---|---|---|---|---|---|---|
| Durable record / live channel split | | | ● | | ● | ● | `docs/agent-communication.md`; `factory/bus.py:48,74`; `docs/findings.d/F70` — proven by a real three-way merge failure |
| Findings ledger as routed data (`AFFECTS` → lanes) | | | ● | | ● | ● | `factory/findings.py`; `tests/test_findings.py::test_every_findings_file_is_visible_to_the_ledger` |
| Lane finish as a mechanism (assert, push, announce, release) | | | | | ● | ● | `factory/finish.py` — **never merges** |
| Handoff generated from measured state | | | | | ● | ○ | `factory/handoff.py` (lane + session) |
| Typed agent↔agent protocol (6 types, 4 moments, 6 ACK states) | | ● | ● | | | | ⛔ `docs/protocol/AGENT_COMMUNICATION_PROTOCOL.md`: *"Nothing here is built."* Deferred behind a ≥5pp net-gain unlock |
| Handoff contract schema | | ● | ● | | | | `docs/protocol/HANDOFF_CONTRACT.schema.json` |
| Communication-defect attribution (3 conditions, 10 discriminators) | | ● | | | | | `docs/protocol/METRICS.md` §H. ⛔ Denominator is **0** — no multi-agent run has executed |
| Blocked-question channel | ● | ● | | ○ | | | `R12`; `factory/operator.py` handles blockers declared *before* the session, not during |
| Lanes seeing each other live | ● | | | | | | ⛔ `docs/findings.d/F71`, **OPEN**: *"fragments fix the merge, not the blindness"* |

---

## Part 5 — Memory and knowledge

| Capability | Research only | Designed | Specified | Partial | Implemented | Validated | Evidence |
|---|---|---|---|---|---|---|---|
| Corrected-premise ledger (findings.d, 33 entries) | | | ● | | ● | ● | `docs/findings.d/README.md`; `factory/findings.py` `by_kind()`, `design_debt()` |
| Failure taxonomy (10 families, closed set) | | | ● | | ● | ● | `factory/preflight.py` `FAMILIES`; `docs/protocol/FAILURE_TAXONOMY.yaml` is its index |
| Known-failure preflight (deterministic key lookup) | | | ● | | ● | ● | `factory/preflight.py`; shadow-mode replay over real history via `scripts/replay_recurrence.py`. ⛔ **WARN-ONLY; it refuses nothing** |
| Context as structure with a required source | | | | ○ | ● | ● | `factory/context.py:71,74` — refuses a ref that cannot point back at its origin. Structures a *lane prompt*, not organizational knowledge |
| Absorption backlog (19 unactioned conclusions) | | | ● | | ● | | `docs/absorption-backlog.md`. **0 of 19 rows closed** |
| Collective Cognition Fabric / HyperMESH | ● | ● | ● | | | | ⚠ **The most contested concept in the corpus** — `contradictions.md` CN-03 |
| Mission context compiler | ● | ● | | | | | `rd_consolidation_pack/03` |
| Knowledge graph / agent KG mesh | ● | ● | | | | | MEASURED: **no vector store, no embedding index, no graph database. Sole runtime dependency is `pyyaml`** |
| Knowledge Change Request protocol | ● | ● | | | | | `rd_consolidation_pack/03` |
| Near-miss memory (a lesson from a *successful* run) | ● | | | | | | `agent2_sihre_consolidation_pack/03`. ⭐ Genuinely absent — a success with a lesson currently leaves no trace |
| Cross-agent experience transfer | ● | ● | | | | | `.agent-platform/bootstrap/docs/COLLECTIVE_COGNITION.md` |
| Post-run learning / write-back | ● | | | | | | `concept-inventory` §4.5: *"Genuinely `ABSENT`, not `DEFERRED` — there is no unlock condition recorded for it either way, which is itself the finding"* |

---

## Part 6 — Optimization, simulation and self-improvement

| Capability | Research only | Designed | Specified | Partial | Implemented | Validated | Evidence |
|---|---|---|---|---|---|---|---|
| Optimizer of any kind | ● | ● | | | | | ⛔ Deliberately absent. Unlock: *"a working eval — the fitness function **is** the eval score"* |
| Never-optimise list (safety spec, not hyperparameters) | | | ● | | ● | | `SYNTHESIS` §6 — enforced socially; ⭐ identical in substance to the POLICY field class |
| Search screening order (model ≫ effort ≫ tools ≫ context ≫ prompt) | ● | ● | | | | | `SYNTHESIS` §6 |
| Repo-agnostic interfaces | ● | ● | | | | | `R4`: cheap now, expensive to retrofit. Not built |
| Simulation / hypertuning | ● | ● | ● | | | | MEASURED: **zero occurrences of `simulat*` as a mechanism in `factory/`.** The 16 hits are the *maturity label* `SIMULATED`, which is the opposite thing — an honesty marker, not a simulator |
| Rehearse the harness without spending a token | ● | ● | | | | | `docs/specs/terminal-configuration.md` §5. ⭐ The narrow survivor of the simulation family |
| Evolution chamber | ● | ● | | | | | `.agent-platform/bootstrap/`; refused by the same unlock as the optimizer |
| Repetition → deterministic meta-tools | ● | | | | | | Cites Microsoft Research. ⚠ Needs a structured trajectory object; `deploy.py` streams a transcript and no trajectory object exists |
| Self-hosting (AF-SH0) | ● | ● | | | | | ⛔ The base case does not exist — no real run has completed |
| Mandatory post-run failure analysis | ● | | ● | | | | `docs/protocol/prompts/post-task-aar.md` — nothing dispatches it |
| Curriculum optimizer / agentic gym | ● | ● | | | | | ⛔ Deferred: *"training on current traces risks learning pathological loops"* |

---

## Part 7 — Operator surfaces

| Capability | Research only | Designed | Specified | Partial | Implemented | Validated | Evidence |
|---|---|---|---|---|---|---|---|
| Switchboard P0 + P1 (projection over existing state) | | | ● | | ● | ● | `factory/switchboard.py`, `switchboard_p1.py`, `switchboard_render.py`; `docs/evidence/switchboard-p1-2026-09-01/README.md` — real Chromium, both schemes |
| Session console (read what a session said, reply) | | | | | ● | ● | `factory/console.py`. ⛔ *"This is NOT a terminal, and it must never be presented as one"* |
| Generated board / task artifact | | | | | ● | ● | `factory/board.py`; `scripts/build_board_artifact.py`; `docs/board/` |
| Readiness graph laid out from data | | | | | ● | ● | `factory/flow.py` — *"a figure that would look identical if the numbers were different is decoration"* |
| Client review artifact (projection + renderer) | | | ● | | ● | ● | `factory/client_review*.py`; `docs/evidence/client-review-readiness-2026-09-01/` — `RENDERED_CONFIRMED` |
| Forensic case-study artifact | | | ● | | ● | ● | `factory/case_study*.py`; `docs/case-studies/delivery-001-marketing-model.md` |
| Rendered validation (3 viewports × 2 schemes × no-JS) | | | | | ● | ● | 7 render-check scripts; 85 captures. The no-JS capture is the **negative control** |
| Embedded terminal | ● | ● | ● | | | | ⛔ **The blocking open decision.** Deliberately unanswered by R8, R13, R14 and R15 so no pass resolves it silently |
| Event ledger as the UI's substrate | | | ● | ○ | ● | ○ | `factory/events.py` — 61 events recorded. `FACTORY-UI-PROMPT.md` §3: *"Phase 0 — build the event ledger. No UI. This is the real work."* |
| Spatial / world UI, semantic zoom, spatial command language | ● | ● | ● | | | | ⛔ Deliberately absent. Unlock: *"numbers worth looking at"* |
| Agentic IDE / Mission Command Console | ● | ● | ● | ○ | | | The Switchboard is the surface that shipped instead |
| Gamified mission control | ● | ● | | | | | `.agent-platform/bootstrap/docs/GAMIFIED_MISSION_CONTROL.md` |

---

## Part 8 — Governance, safety and process

| Capability | Research only | Designed | Specified | Partial | Implemented | Validated | Evidence |
|---|---|---|---|---|---|---|---|
| Merging stays human (`finish()` refuses) | | | | | ● | ● | `factory/finish.py` |
| Operator answers to declared blockers | | | | | ● | ● | `factory/operator.py`; `.data/operator/<lane>.json`, gitignored on purpose |
| Isolation tier T0 (worktree, no egress, no DB verbs) | | | | | ● | ● | `factory/worktrees.py` + `factory/deploy.py` |
| Isolation tier T1 (container, egress allowlist, read-only role) | ● | ● | | | | | ⚠ Unmeasured on Windows/WSL; and *"a container does nothing about prompt injection"* |
| Isolation tier T2 (ephemeral zero-copy clone) | ● | ● | | | | | ⚠ *"The clone is a compromised oracle at exactly the layer our evidence rule exists to protect"* |
| Blast-radius gate (mandatory human) | | ● | ● | ○ | | | ⚠ The credential-use ledger exists (`scripts/credential_use.py`); **the gate does not** |
| `needs_paul` as a refusal | | ● | | ○ | | | ⛔ **Display-only today: it renders, it does not refuse** |
| Bounded autonomy as named auto-actions | ● | ● | | ○ | | | `R7`; `factory/launch.py` separates three questions conflated in "ready" |
| Publication boundary (all remote refs) | | | | | ● | ● | `docs/release-gate/AF-RELEASE-GATE-01-2026-09-01.md`; `capture_public_exposure.py`. ⛔ **BLOCKED, requires human authority** |
| Research/implementation boundary (approved handoffs only) | | | ● | | ● | | `docs/agent-army/IMPLEMENTATION_HANDOFFS.md` — the mechanism exists; **zero handoffs in any state** |
| Import without granting authority | | | | | ● | ● | `.agent-platform/README.md` + `RECONCILIATION.md` + `PACK_CONFORMANCE.md` (4 recorded deviations) |
| Research record self-check (`unsynthesised()`, `dispatch`) | | | | | ● | ● | `factory/synthesis.py`, `factory/dispatch.py`, `tests/test_synthesis_current.py`. ⚠ `F75`, `F93` — they detect *unmentioned*, not *unabsorbed* |
| Two-stage external-answer intake | | | ● | | ● | ● | `docs/reviews/external/README.md` + `verification.md` — 2 proposals rejected in writing |
| Commercial autonomy policy | ● | ● | | | | | `.agent-platform/bootstrap/docs/COMMERCIAL_AUTONOMY_POLICY.md` |

---

## Part 9 — Infrastructure

Recorded because an architecture reviewer arriving from the research packs will assume otherwise.
Every row MEASURED 2026-09-02.

| Capability | Status | Evidence |
|---|---|---|
| Runtime dependencies | **`pyyaml` only** | `pyproject.toml`. `playwright` is an extra, needed only for rendered validation |
| DAG / workflow engine | **NONE** | `PACK_CONFORMANCE.md` 0.5: *"no DAG engine, no Prefect, no queue; execution is synchronous Python + `subprocess`"* |
| Async runtime | **effectively none** | 1 `asyncio` hit across `factory/`, `evaluator_service/`, `scripts/` |
| Database | **NONE** | 1 `sqlite` hit, and it is inside a comment. State is JSONL files under `.data/` |
| Vector store / embedding index / RAG | **NONE** | the single `embedding` hit is the word "embedding" in an HTML docstring |
| Message queue / broker | **NONE** | `factory/bus.py` is append-only files, one per writer |
| HTTP surface | **stdlib only** | `evaluator_service/app.py` — *"the boundary is the point, not the framework"* |
| Container runtime | **NONE** | T1/T2 are designed, not built |
| CI | **UNKNOWN** | No workflow file was found under the indexed roots. `SYNTHESIS` §8 item 11 lists *"CI on push in agent-factory"* as **not started** |
| Deployment target | **UNKNOWN / local** | `evaluator_service` is *intended* to be lifted out to a host the graded agent holds no credential for. Nothing records that it has been |
| Observability / tracing | **NOT-SEARCHED** | `concept-inventory` §4.2: OpenTelemetry GenAI conventions, Langfuse/LangSmith/Weave and the trajectory-object question are untouched. `deploy.py` streams a transcript; there is **no structured trajectory object** |

---

## Part 10 — Added 2026-09-02 by the `.agent-platform` delta pass

Nine capabilities recovered by indexing the 110-file bootstrap tree at a finer granularity than the
corpus-preparation pass used — in particular its **eight JSON schemas, none of which the canonical
index had ever named**. Reconciliation, dispositions and unlock conditions:
[`agent_platform_delta_synthesis.md`](agent_platform_delta_synthesis.md).

⭐ **Read the Evidence column before the ● marks, again.** The pattern from the supplementary pass
repeats, narrowly: **two of the nine are already PARTIAL and one is already IMPLEMENTED**, while the
inbound `CRUCIAL_FEATURES_DELTA.md` prices one of them as a *"major future multiplier"*. The other
six are `NOT_IMPLEMENTED` and every one of those is a **measured zero from a grep run this pass**,
not an inference.

| Capability | Research only | Designed | Specified | Partial | Implemented | Validated | Evidence |
|---|---|---|---|---|---|---|---|
| **Execution-surface routing** — task metadata + surface selection (`C-GV-07`) | | ● | | | | | ⛔ MEASURED ZERO: `grep -rniE "remote_control\|cloud_web\|preferred_surface\|execution_surface" factory/ scripts/ blueprints/ missions/ \| wc -l` → **0**. No task carries an `execution:` block. ⭐ But clause 3 of its collision rule is BUILT — `claims.py:200-244` (`O_CREAT\|O_EXCL`, verified against the process table), `worktrees.py:38-39`, `lanes.py` (grouping by file locality, not the dependency graph). `PACK_CONFORMANCE` 4.3: the rule is *"honoured by discipline, not enforced"* |
| **Capability record** — a claim bound to its measured conditions (`C-AG-16`) | | | ● | ● | | | ⭐ `registry.py` versions a workflow by the **hash of its `SKILL.md` text** and `unproven()` returns 4 of 9 workflows never run on real work. ⛔ ABSENT, against the pack schema's 11 properties: `conditions`, `success_rate`, `evidence_count`, `cost`, `latency`, `valid_from`, `valid_until`. `grep -rniE "capability_record\|CapabilityRecord" factory/` → 0. `certify.py` holds the certification half, unjoined |
| **Synthesis inbox** — a disposition queue as a projection (`C-UI-07`) | | ● | | ● | | | ⭐ **Both halves exist and nothing joins them.** Content model: `docs/absorption-backlog.md`, whose `ACTION` field already includes *"reject it in writing"* — **19 rows and 2 whole answers carry no disposition** (`GAP-07`). Surface: `switchboard_p1.py`'s `NEEDS YOU` panel, fed by `sessions.blocked()` and `bus.unread()`. The backlog is a markdown file no projection reads |
| **Mission Assembly Plan** — a compiled, gated team object (`C-TM-07`) | | | ● | | | | `schemas/mission-assembly.schema.json` requires `participants`, `communication_routes`, `context_packets`, `gates`. ⛔ No mission object, schema or lifecycle exists. `grep -rniE "swarm"` across `factory/ scripts/ blueprints/ missions/ evals/ tests/` → **1 line, no mechanism**. Nearest built: a lane brief plus a gate, and `blueprints/orchestrator_team.yaml` — a 3-agent blueprint **built, tested and rejected on evidence** |
| **Mine the mechanism, never the identity** (`C-PR-08`) | | | | | | ● | ⭐ **VALIDATED and never named.** Executed 2026-08-31 on three MIT repos read from **source**: Paperclip (6,169 files), SSSF (21), Inkwell (24). No code taken, obligations recorded, five patterns that would let this estate **delete** rather than add, and one defect **inverted rather than inherited** — SSSF's `["echo", "PLACEHOLDER"]` quality block, where `echo` exits 0 and a stamped repo reports `verified=True` having tested nothing. `RECONCILIATION.md` §4 |
| **Compute & integration fabric** — the node contract (`C-OR-09`) | ● | | | | | | `grep -rniE "DGX\|compute_node\|compute node"` → **0**. Execution is synchronous Python + `subprocess`; sole runtime dep is `pyyaml`. ⛔ There is no second compute surface to abstract over |
| **Venture vertical** — opportunity → plan → lifecycle (`C-OR-10`) | | | ● | | | | `grep -rniE "venture\|opportunity_hypothesis"` → **0**, both terms. Two schemas exist in the pack. ⭐ `opportunity-hypothesis.schema.json` **requires** a `falsification` field and `venture-plan.schema.json` requires **both** success and failure criteria — `C-PR-03` reached independently, and stricter than most gates here. ⛔ Gated by `README.md:96`, one certified team |
| **Customer & market learning loop** (`C-KN-08`) | ● | | | | | | No product, no telemetry, no customer of the factory. Nothing in `factory/` reads an external signal of any kind. ⚠ `C-VD-02` binds hardest here: a silent channel and a customer without the problem are indistinguishable until the instrument is proved able to see a non-zero |
| **Portfolio allocation under opportunity cost** (`C-OP-07`) | ● | | | | | | `grep -rniE "portfolio.*allocat\|KILL/HOLD"` → **0**. ⛔ `C-OP-01` says the fitness function IS the eval score, and the eval corpus is one connector (`GAP-08`) — multi-objective allocation over an unvalidated single objective is premature by two steps |

⛔ **Six of the nine are gated, and the gates are not this pass's opinion.** `C-AG-16`, `C-TM-07`,
`C-OR-10`, `C-KN-08` and `C-OP-07` all sit behind `README.md`'s absence table or `GAP-09`;
`C-OR-09` sits behind having a second runtime. ⭐ **Exactly one has no unlock condition at all** —
`C-GV-07`, which schedules work rather than grading it, and is therefore not gated by the 0-PASS
ledger. That asymmetry is the delta pass's main sequencing result.

---

## Summary — where the estate actually is

**MEASURED 2026-09-02** by parsing this file's own tables — 112 capability rows across Parts 1–8,
plus 11 infrastructure rows in Part 9. Recount with:

    python -c "rows=[c for c in ([x.strip() for x in l.strip().strip('|').split('|')] for l in open('docs/_index/current_vs_proposed.md',encoding='utf-8') if l.lstrip().startswith('|')) if len(c)==8 and c[0]!='Capability' and not c[0].startswith('---')]; print(len(rows))"

> ⓘ **Re-measured 2026-09-02 by the `.agent-platform` delta pass.** The command above now returns
> **124**; it returned **115** immediately before Part 10 added nine rows.
>
> ⛔ **And that exposes a pre-existing drift of three, in the sentence directly above.** The prose
> says *112 + 11 = 123*; the published command has been returning **115** — it matches only rows
> with eight columns, so it does not count Part 9's infrastructure rows at all. The two numbers were
> never measuring the same thing. This is `C-VD-04` catching its own document: the count carried its
> regeneration command, the command was run, and the disagreement surfaced instead of compounding.
> **The command is right; the prose split is not, and is left as written rather than silently
> corrected, because which of 112/11 is wrong cannot be recovered without re-deriving the original
> pass's classifier — which was never published.**
>
> **The breakdown table below is NOT re-derived**, for the same reason: its six buckets do not map
> onto any stated rule (a row marked both `Specified ●` and `Partial ●` could land in either), so
> re-computing it with a different classifier would produce numbers that look like a correction and
> are not. The nine delta rows are stated separately instead:
>
> | Delta rows (Part 10) | Count |
> |---|---:|
> | **Validated** `●` | 1 — `C-PR-08`, practised 2026-08-31 and never named |
> | **Partial** | 2 — `C-AG-16`, `C-UI-07`; both are joins between two things already built |
> | **Specified or Designed** only | 3 |
> | **Research only** | 3 |

| Highest level reached | Count | Reading |
|---|---:|---|
| **Validated** `●` | 34 | It ran here, on real state, and was observed |
| **Validated** `○` only | 11 | Partially exercised — usually replayed, or run against a fixture rather than a live subject |
| **Implemented**, never exercised | 6 | The code exists and is tested; nothing has run it on real work |
| **Partial** | 8 | A mechanism exists under a different name; the capability as described is not built |
| **Specified or Designed** only | 36 | A contract, schema or design exists. Nothing is built |
| **Research only** | 17 | Named in a document. Not designed |

And in Part 9, **three of eleven infrastructure rows are `UNKNOWN`** — CI, deployment target and
observability. The repository does not support a conclusion on those.

⭐ **The distribution is the finding, and it is sharply bimodal.**

**Nearly everything validated is a measurement or a control** — the verdict lattice, negative
controls, evidence classes, readiness gates, rendered validation, the findings ledger, the failure
preflight, the publication boundary. This estate's built capability is *knowing whether something
worked*.

**Almost nothing about doing the work is validated.** The capability that would make all of it mean
something — an agent completing a real run — has **never happened**:

```
.data/runs.jsonl    10 rows    FINISHED x3, FAIL x1, UNMEASURABLE x6, PASS x0
.data/events.jsonl  61 events  7 agent_returned, all dry_run=True
```

So the honest one-line summary of this matrix is: **the instruments are real and the subject has not
yet been measured.** Fifty-three capabilities exist only as documents (36 designed or specified,
17 research-only), and the loop they would all sit inside has not completed once.

That is not a criticism of the sequencing. `README.md` argues at length that this ordering is
deliberate, and the two founding failures — 233 diagnoses / 234 escalations / 0 fixes over 81 days,
and a loop that ran 965 times at a self-recorded 1.6% success rate and never adjusted — are the
stated reason. But it is the single most important fact for an architecture reviewer to hold while
reading any proposal in this corpus.

---

## Method and limits

- Column assignment used, in order: (1) an explicit status marker in the document itself
  (`⛔ DESIGN`, `✅ BUILT`, `not started`); (2) a cited `path:line` verified to exist; (3) presence of
  a test module; (4) direct measurement (`grep`, module import, ledger read). Where none applied,
  the row is `UNKNOWN`.
- **`docs/agent-army/CURRENT_STATE.md` outranks this table** on any Agent Army concept — it cites
  `file:line` per row and was written against the code.
- ✅ ~~**Two capabilities could not be assessed** because their source is a `.docx` this pass could
  not read.~~ **Closed 2026-09-02.** Both were converted and read; seven capabilities they propose are
  added to Part 3 below under *"Added 2026-09-02"*. ⚠ **Residual:** their twelve embedded figures
  were not extracted, so a capability expressed only in a diagram is still missing.
  `research_gap_candidates.md` GAP-01.
- **CI is `UNKNOWN`, not absent.** MEASURED 2026-09-02: `ls .github` returns *No such file or
  directory*, and no workflow file was found under the indexed roots. That is evidence of no
  GitHub Actions CI in this checkout, not evidence that no CI exists anywhere, so the row stays
  `UNKNOWN` rather than becoming `NONE`. `SYNTHESIS.md` §8 item 11 lists *"CI on push in
  `agent-factory`"* as **not started**, which is the corpus's own reading.
