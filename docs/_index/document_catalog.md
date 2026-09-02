# Document catalog — the Agent Factory corpus, grouped by subject

**Generated 2026-09-02** against `agent-factory` @ `fc78074` (branch `main`).
Companion to [`corpus_manifest.yaml`](corpus_manifest.yaml), which holds the machine-readable
record for every artifact. This file is the reading map.

**A document appears under every category it belongs to.** Twenty-two of them appear three times
or more; that repetition is information, not redundancy — it says which documents are load-bearing
across the corpus.

---

## ⛔ Read these four first, in this order

Everything else in this catalog is easier to weigh once these are in hand. Together they are
about 45 KB.

| # | Document | What it settles |
|---|---|---|
| 1 | [`docs/agent-army/README.md`](../agent-army/README.md) | The boundary. Research does not imply implementation; Agent Army research lives in a **sibling repository**. |
| 2 | [`docs/agent-army/CURRENT_STATE.md`](../agent-army/CURRENT_STATE.md) | What of the research vocabulary exists in code. Every row cites `file:line`. **Outranks every other document on that question**, including the manifest. |
| 3 | [`.agent-platform/RECONCILIATION.md`](../../.agent-platform/RECONCILIATION.md) | A prior reconciliation of an inbound pack against this estate. Its conclusion constrains everything downstream: *"the pack's category framing is dead and its engineering patterns are live. Mine it for mechanisms; do not adopt its programme."* |
| 4 | [`docs/research/agent-factory-concept-inventory.md`](../research/agent-factory-concept-inventory.md) | The 26 concepts as built, the do-not-re-ask list, and the seven axes on which **no pass has looked at all**. |

Then, if you have time for two more: [`docs/case-studies/delivery-001-marketing-model.md`](../case-studies/delivery-001-marketing-model.md)
(the only test of the design against real mistakes) and
[`docs/research/SYNTHESIS.md` §7 and §17](../research/SYNTHESIS.md) (where the passes disagree, and
where the record audits itself).

---

## ⚠ Four facts that change how you read everything below

1. **The whole corpus is 13 days old.** First commit 2026-08-20, last 2026-09-01. The 719 indexed
   files were produced in under two weeks.
2. **No agent has ever been dispatched for real.** MEASURED 2026-09-02: `.data/runs.jsonl` holds 10
   rows — `FINISHED`×3, `FAIL`×1, `UNMEASURABLE`×6, **zero `PASS`**; all 7 `agent_returned` events
   carry `dry_run=True`. Every organizational proposal in this corpus sits above an execution layer
   that has not yet completed one real run.
3. **The nine inbound research packs are not independent sources.** Five carry the same
   `Agent Factory Vision.txt` byte-for-byte; three carry the same 56 KB ZEUS pack. Their agreement
   with one another is duplication, not corroboration.
4. **Sole runtime dependency is `pyyaml`.** No DAG engine, no Prefect, no queue, no vector store, no
   RAG. Execution is synchronous Python plus `subprocess`. (MEASURED, `.agent-platform/PACK_CONFORMANCE.md`.)

---

## Vision

The intent layer. States what the system is *for*. Never a specification.

| Document | Note |
|---|---|
| [`BRAIN-DUMP.md`](../../BRAIN-DUMP.md) | The origin record, recovered verbatim after a crash. Every concept the corpus later argues about is named here first, in one page, without evidence. |
| [`.agent-platform/bootstrap/source/Agent Factory Vision.txt`](../../.agent-platform/bootstrap/source/Agent%20Factory%20Vision.txt) | The most downstream-influential document in the corpus. Origin of Org-IR, the ten organization presets, the Evolution Chamber and the Research Compiler. **Duplicated at 6 paths.** Authority: none. |
| [`.agent-platform/bootstrap/VISION.md`](../../.agent-platform/bootstrap/VISION.md) | The pack's north-star statement. Its founding category claim is refuted in `RECONCILIATION.md` §1.1. |
| [`docs/specs/product-end-state.md`](../specs/product-end-state.md) | The repository's own answer: two products, and the factory is not the client-facing one. §7 labels its own assumptions `ASSUMED`. |
| [`docs/artifacts/project.html`](../artifacts/project.html) | The showcase surface. Deliberately decoupled from the board. |
| [`.agent-platform/bootstrap/docs/ENTREPRENEUR_SCENARIOS.md`](../../.agent-platform/bootstrap/docs/ENTREPRENEUR_SCENARIOS.md) | Seven scenarios the platform would enable. Aspiration, no evidence. |

## Architecture

| Document | Note |
|---|---|
| [`docs/specs/architecture-v0.md`](../specs/architecture-v0.md) | **Four planes** (decide/run/prove/approve) and **the isolation ladder** — tier chosen by what the task touches. Explicitly a strawman; §7 lists five ways it may be wrong. Carries `MEASURED / DERIVED / REASONED / BET` per claim. |
| [`docs/reviews/external/deepseek.md`](../reviews/external/deepseek.md) | A **competing decomposition**: five layers L1 elicitation → L2 contract state machine → L3 execution → L4 assurance → L5 learning. The only non-Anthropic reading in the corpus. |
| [`docs/specs/golden-workflow-fit.md`](../specs/golden-workflow-fit.md) | One concrete workflow used as the instrument for finding architecture gaps. Includes an explicit **anti-gap list**. |
| [`docs/research/answers/R18-answer-our-factory-internal-audit.md`](../research/answers/R18-answer-our-factory-internal-audit.md) | Audits the code with `path:line` citations. Judges the isolation ladder. **Never absorbed** (SYNTHESIS §17.3). |
| [`docs/research/answers/R14-answer-structure-model-and-joy.md`](../research/answers/R14-answer-structure-model-and-joy.md) | Attacks the decomposition and proposes an object model. **Never absorbed** (SYNTHESIS §17.2). |
| [`docs/raw_research/agent_factory_rd_consolidation_pack/03_HYPERMESH_ARCHITECTURE.md`](../raw_research/agent_factory_rd_consolidation_pack/03_HYPERMESH_ARCHITECTURE.md) | HyperMESH: mission knowledge view, context compiler, Knowledge Change Request. |
| [`docs/raw_research/agent-factory-bootstrap-pack/docs/03-design/REPO_ARCHITECTURE_SEED.md`](../raw_research/agent-factory-bootstrap-pack/docs/03-design/REPO_ARCHITECTURE_SEED.md) | A repo-shape seed. Explicitly "not yet a migration plan". |
| [`.agent-platform/bootstrap/BUILD_START_TO_FINISH.md`](../../.agent-platform/bootstrap/BUILD_START_TO_FINISH.md) | A 15-stage build flow, Stage 0 "bootstrap the bootstrapper". |
| [`docs/design/artifact-generator-proposal.md`](../design/artifact-generator-proposal.md) | Answers *"why can this not simply be a module?"* for every new component it proposes. Written, executed and validated in 48 hours. |

## Agents

| Document | Note |
|---|---|
| [`docs/agent-army/CURRENT_STATE.md`](../agent-army/CURRENT_STATE.md) | What exists, per concept, with code evidence. |
| [`docs/raw_research/agent2_sihre_consolidation_pack/01_agent_definition_and_layers.md`](../raw_research/agent2_sihre_consolidation_pack/01_agent_definition_and_layers.md) | A baseline agent definition, canonical layers, and capability vs skill vs authority. |
| [`docs/raw_research/agent2_sihre_consolidation_pack/03_agent2_concept_registry.md`](../raw_research/agent2_sihre_consolidation_pack/03_agent2_concept_registry.md) | **35 concepts** with definition / mechanism / benefit / priority. The most structured concept list in the inbound corpus. |
| [`docs/raw_research/agent_factory_agent_genome_research_pack/01_CURRENT_DESIGN_SYNTHESIS.md`](../raw_research/agent_factory_agent_genome_research_pack/01_CURRENT_DESIGN_SYNTHESIS.md) | The **four-layer agent model** (genotype/phenotype/history/fitness) and the **five field classes**. |
| [`docs/protocol/prompts/`](../protocol/prompts/) | Ten named agent roles, each with input/output contracts, stop conditions and evidence requirements. **None is wired to a dispatch path.** |
| [`docs/research/answers/R2-answer-topology.md`](../research/answers/R2-answer-topology.md) | One worker + a non-LLM verifier + a human. The evidence base for refusing extra agents. |
| [`blueprints/windsorai_client_a.yaml`](../../blueprints/windsorai_client_a.yaml) | The one connector target with a calibrated contract. |

## Agent configuration

The corpus's densest single theme. Four packs and one built module argue about it.

| Document | Note |
|---|---|
| [`docs/raw_research/agent-config-research-pack/`](../raw_research/agent-config-research-pack/) | ⭐ **The only inbound pack that read this repository.** Executive assessment cites `blueprint.py`, `presets.py`, `metrics.py`, `registry.py`, `readiness.py` by path and concludes *"extend those seams; do not create a parallel configuration product."* Carries `SHA256SUMS.txt`. |
| [`…/agent-config-research-pack/03-parameter-catalog.md`](../raw_research/agent-config-research-pack/03-parameter-catalog.md) | A 20-family agent/team parameter catalog. |
| [`…/agent-config-research-pack/02-configuration-and-storage.md`](../raw_research/agent-config-research-pack/02-configuration-and-storage.md) | YAML-in-git for intent, event store for observation, lockfile for resolution. A storage matrix. |
| [`docs/raw_research/agent_factory_agents_as_configuration_research_pack/`](../raw_research/agent_factory_agents_as_configuration_research_pack/) | Same thesis, concept-first. Agent Health Vector, Mission Requirement Vector, READY-UP. |
| [`docs/raw_research/agent_factory_agent_genome_research_pack/`](../raw_research/agent_factory_agent_genome_research_pack/) | Genome/phenotype, agent registry + lockfile, relationship edges, communication phenotypes. |
| [`docs/raw_research/agent_factory_rd_consolidation_pack/02_AGENT_GENOME.md`](../raw_research/agent_factory_rd_consolidation_pack/02_AGENT_GENOME.md) | Prompt → Config → Evaluate, with architecture presets. |
| [`docs/specs/architecture-v0.md` §5](../specs/architecture-v0.md) | The `AgentSpec` this repository actually proposes, with the tier field. And the rule: **a spec field that nothing reads is worse than no field.** |
| [`docs/specs/terminal-configuration.md`](../specs/terminal-configuration.md) | Per-lane model/effort/cost configuration, and what must never be automated. |
| [`docs/findings.d/F90-…`](../findings.d/F90-the-run-record-names-a-repo-the-controller-cannot-put-an-agent-in.md) | The measured instance of exactly that defect: `TeamSpec.repo` is inside the version hash and nothing reads it. **OPEN.** |

## Agent teams

| Document | Note |
|---|---|
| [`blueprints/orchestrator_team.yaml`](../../blueprints/orchestrator_team.yaml) | ⭐ **Built, tested and rejected on evidence — and kept.** Records the quantified threshold that would unlock it. The most instructive single file in the corpus. |
| [`docs/research/answers/R2-answer-topology.md`](../research/answers/R2-answer-topology.md) | The evidence. Read the −3.5% **with its interval** (−18.6% to +25.7%); the figure that actually supports the decision is the −70% on sequential planning. |
| [`docs/research/answers/R19-answer-work-taxonomy-and-team-selection.md`](../research/answers/R19-answer-work-taxonomy-and-team-selection.md) | How a team gets chosen for a ticket, framed as **an eligibility filter with a negative control** — refusal first, choice second. |
| [`docs/raw_research/agent_factory_agents_as_configuration_research_pack/04_RESEARCH_PROMPTS/04_…MISSION_MATCHING_AND_DYNAMIC_TEAMS.md`](../raw_research/agent_factory_agents_as_configuration_research_pack/04_RESEARCH_PROMPTS/04_DEEP_RESEARCH_MISSION_MATCHING_AND_DYNAMIC_TEAMS.md) | Dynamic team formation and topology selection, with a maturity ladder. |
| [`docs/raw_research/agent_factory_rd_consolidation_pack/08_PRESET_AGENTS_AND_TEAMS.md`](../raw_research/agent_factory_rd_consolidation_pack/08_PRESET_AGENTS_AND_TEAMS.md) | Suggested first agents and first teams. |
| [`docs/raw_research/agent-config-research-pack/04-team-metrics-and-formulas.md`](../raw_research/agent-config-research-pack/04-team-metrics-and-formulas.md) | Team metric families, agent health, team health, struggle score, communication effectiveness. |

## Agent armies

| Document | Note |
|---|---|
| [`docs/agent-army/README.md`](../agent-army/README.md) | The boundary and the one rule. |
| [`docs/agent-army/APPROVED_CONCEPTS.md`](../agent-army/APPROVED_CONCEPTS.md) | ⭐ **Empty, on purpose.** Four requirements for approval; two now exist, two do not. Records that the sibling repo's Wave 0 synthesis **falsified the programme's founding premise**. |
| [`docs/agent-army/IMPLEMENTATION_HANDOFFS.md`](../agent-army/IMPLEMENTATION_HANDOFFS.md) | The promotion path. Zero handoffs exist in any state. |
| [`docs/agent-army/RESEARCH_REPO.md`](../agent-army/RESEARCH_REPO.md) | The source-of-truth split across two repositories. |
| [`docs/raw_research/agent_factory_army_ui_concept_pack/`](../raw_research/agent_factory_army_ui_concept_pack/) | The full Army operating vocabulary, world UI and 20-track research backlog. |
| [`docs/raw_research/converted/Beyond_Agent_Armies_Frontier_Architectures.md`](../raw_research/converted/Beyond_Agent_Armies_Frontier_Architectures.md) | ✅ **Now readable** (2026-09-02). The eight-level ladder L1–L8 with an explicit refusal to make L4–L8 mandatory; twelve architecture cards each carrying a failure mode and a smallest useful experiment; twelve novelty hypotheses framed for prior-art attack; a mission-signature → topology table. ⚠ Cites `Agent Factory Vision.txt` and nothing else internal — **not** the Wave 0 synthesis it contradicts. Original `.docx` preserved beside it. |
| [`docs/raw_research/converted/Agent_Factory_Frontier_Architecture_Prioritization_Pack.md`](../raw_research/converted/Agent_Factory_Frontier_Architecture_Prioritization_Pack.md) | ✅ **Now readable** (2026-09-02). The decision companion: P0/P1/P2/P3-Lab ranking, per-architecture minimum valuable implementation, promotion gates G0–G7, and the **Mission Assurance Receipt**. ⚠ Its scores are declared *"directional planning judgments, not measured ROI"* by its own §4 — basis `ASSUMED`. |
| [`docs/_index/agent_army_wave0_supplement.md`](agent_army_wave0_supplement.md) | ⭐ **Read this before either document above.** The 2026-09-02 supplementary pass: what the sibling repo's Wave 0 synthesis concluded, where the two frontier documents collide with it, and the prior-art map for Goal-Aware Adaptive/Dynamic Orchestration. Everything tagged `SOURCE FACT` / `PRIOR SYNTHESIS` / `PROPOSAL` / `SPECULATION` / `UNRESOLVED`. |
| [`docs/research/agent-factory-research-prompts.md` line 55](../research/agent-factory-research-prompts.md) | Where the Agent Army was first cut: *"level 5 — cut for now… with zero certified teams…"* |

## Organizational architecture

| Document | Note |
|---|---|
| [`docs/raw_research/agent_factory_army_ui_concept_pack/05_ORGANIZATION_HIERARCHY_AND_SERVICE_DESIGNATIONS.md`](../raw_research/agent_factory_army_ui_concept_pack/05_ORGANIZATION_HIERARCHY_AND_SERVICE_DESIGNATIONS.md) | ⭐ **Arbitrarily nested service designations — topology as data, not a hard-coded five levels.** The single most reusable organizational idea in the inbound corpus. |
| [`docs/raw_research/agent_factory_chat_design_pack/06_ORGANIZATION_HIERARCHY_AND_SERVICE_DESIGNATIONS.md`](../raw_research/agent_factory_chat_design_pack/06_ORGANIZATION_HIERARCHY_AND_SERVICE_DESIGNATIONS.md) | The same idea, different framing. |
| [`docs/raw_research/agent_factory_rd_consolidation_pack/06_ORGANIZATIONAL_GENOME_AND_TEAM_LAYERS.md`](../raw_research/agent_factory_rd_consolidation_pack/06_ORGANIZATIONAL_GENOME_AND_TEAM_LAYERS.md) | Organizational genome, project-specific organizations, team blueprint registry. |
| [`docs/raw_research/agent-factory-bootstrap-pack/schemas/org-ir.seed.schema.yaml`](../raw_research/agent-factory-bootstrap-pack/schemas/org-ir.seed.schema.yaml) | The only concrete Org-IR schema in the corpus. Marked *"seed only. Do not implement as canonical until architecture synthesis approves it."* |
| [`docs/raw_research/agent-factory-bootstrap-pack/docs/07-implementation/FEATURE_INTEGRATION_SEEDS.md` §1, §4, §11](../raw_research/agent-factory-bootstrap-pack/docs/07-implementation/FEATURE_INTEGRATION_SEEDS.md) | Org compiler, ten organization presets, and *"do not assume Agent → Team → Army is the only hierarchy"*. |
| [`docs/raw_research/agent2_sihre_consolidation_pack/04_recursive_sihre_and_morphological_cognition.md`](../raw_research/agent2_sihre_consolidation_pack/04_recursive_sihre_and_morphological_cognition.md) | Recursive routing/trust at expert → agent → team → army → factory levels. |
| [`.agent-platform/RECONCILIATION.md` §1.1](../../.agent-platform/RECONCILIATION.md) | ⛔ **The category is occupied and the novelty claim refuted.** AOE is organisation-oriented MAS with a metamodel (Moise+), a runtime (JaCaMo) and a textbook; `arXiv:2607.25446` (IMACS) *is* the organizational-compiler thesis. |
| [`docs/raw_research/converted/Beyond_Agent_Armies_Frontier_Architectures.md`](../raw_research/converted/Beyond_Agent_Armies_Frontier_Architectures.md) §2, §4 | ⭐ **The eight-level ladder and the twelve architecture cards** — the content `concept_index.yaml` C-OR-04 was a placeholder for. Each card carries a *main failure mode* and a *smallest useful experiment*, which is what a topology tournament (GAP-14 / RB-04) needs. |
| [`docs/raw_research/converted/Agent_Factory_Frontier_Architecture_Prioritization_Pack.md`](../raw_research/converted/Agent_Factory_Frontier_Architecture_Prioritization_Pack.md) §5, §11, §12 | The P0–P3 ranking, the **"what I would explicitly not build yet"** list, and promotion gates G0–G7 — which independently match the sibling repo's Evolution Chamber promotion chain. |
| [`docs/_index/agent_army_wave0_supplement.md`](agent_army_wave0_supplement.md) §3 | ⭐ **Read before acting on either.** Five collisions between the two documents above and the sibling's Wave 0 synthesis — including the one that opened **CN-29**. |

## Communication / protocols

| Document | Note |
|---|---|
| [`docs/agent-communication.md`](../agent-communication.md) | ✅ **BUILT.** The record/channel split, five typed kinds, one file per writer. Derived from a real three-way merge failure. |
| [`docs/protocol/AGENT_COMMUNICATION_PROTOCOL.md`](../protocol/AGENT_COMMUNICATION_PROTOCOL.md) | ⛔ **DESIGN.** Six message types, four boundary moments, six acknowledgement states. Compare with the built version above: five kinds, running, versus six types, not. |
| [`docs/protocol/HANDOFF_CONTRACT.schema.json`](../protocol/HANDOFF_CONTRACT.schema.json) | ⛔ DESIGN. The machine-readable envelope. |
| [`docs/protocol/METRICS.md` §H](../protocol/METRICS.md) | Communication-error attribution: three conditions and a table of deterministic discriminators. **Requires naming the upstream record**, otherwise it is an implementation defect, not a communication defect. |
| [`.agent-platform/bootstrap/docs/COMMUNICATION_PROTOCOL.md`](../../.agent-platform/bootstrap/docs/COMMUNICATION_PROTOCOL.md) | Typed envelope candidate and communication classes. |
| [`docs/raw_research/agent_factory_agent_genome_research_pack/presets/communication_phenotypes.yaml`](../raw_research/agent_factory_agent_genome_research_pack/presets/communication_phenotypes.yaml) | Quiet / Loud / Mumbler / Concise Scout / Challenger / Coordinator compiled into measurable parameters. |
| [`docs/raw_research/agent_factory_army_ui_concept_pack/08_COMMUNICATION_AND_COORDINATION.md`](../raw_research/agent_factory_army_ui_concept_pack/08_COMMUNICATION_AND_COORDINATION.md) | Signals channels and coordination features. |
| [`docs/findings.d/F70-…`](../findings.d/F70-a-shared-ledger-cannot-survive-parallel-lanes.md) · [`F71-…`](../findings.d/F71-lanes-still-cannot-see-each-other-live.md) | The measured failure that produced the split, and the part still **OPEN**: lanes cannot see each other live. |

## Memory / knowledge

The most contested area in the corpus. Five packs propose a fabric; two research answers and one
built mechanism argue against building it as specified.

| Document | Position |
|---|---|
| [`docs/research/R06B-collective-cognition-and-knowledge-architecture.md`](../research/R06B-collective-cognition-and-knowledge-architecture.md) | ⭐ **Written, never dispatched.** Asks what *none* of the nine existing stores can do, rather than designing a tenth. Supersedes the pack's version. Its header records that `factory/` **cannot see it** — a blind-instrument finding about the dispatch tool itself. |
| [`docs/research/answers/R10-answer-hierarchical-wiki-agent-training.md`](../research/answers/R10-answer-hierarchical-wiki-agent-training.md) | *"We already have **six** overlapping stores… adding a seventh would be a mistake… retire or merge at least one."* Its own numbers are flagged unverified. |
| [`docs/protocol/KNOWN_FAILURE_PREFLIGHT.md`](../protocol/KNOWN_FAILURE_PREFLIGHT.md) | ✅ **BUILT** — and deliberately the narrowest possible form: **deterministic key lookup, no retrieval, no similarity, no embedding index**, WARN-ONLY. |
| [`docs/findings.d/README.md`](../findings.d/README.md) | ⭐ A working knowledge-object schema, derived from three real failures, enforced by a parser and a test. The corpus's most transferable artifact. |
| [`.agent-platform/bootstrap/docs/COLLECTIVE_COGNITION.md`](../../.agent-platform/bootstrap/docs/COLLECTIVE_COGNITION.md) | Proposes the fabric: knowledge objects, mission-shaped graph, context compiler. |
| [`docs/raw_research/agent_factory_rd_consolidation_pack/03_HYPERMESH_ARCHITECTURE.md`](../raw_research/agent_factory_rd_consolidation_pack/03_HYPERMESH_ARCHITECTURE.md) | HyperMESH + Mission Context Compiler + Knowledge Change Request. |
| [`docs/raw_research/agent_factory_army_ui_concept_pack/09_INTELLIGENCE_KNOWLEDGE_MEMORY.md`](../raw_research/agent_factory_army_ui_concept_pack/09_INTELLIGENCE_KNOWLEDGE_MEMORY.md) | Distinguishes explicit doctrine from historical experience. |
| [`docs/raw_research/agent2_sihre_consolidation_pack/research_prompts/DR04_CONTEXTUAL_TRUST_KG_MESH.md`](../raw_research/agent2_sihre_consolidation_pack/research_prompts/DR04_CONTEXTUAL_TRUST_KG_MESH.md) | Transactive memory — the system knowing who knows what. |
| [`docs/absorption-backlog.md` AB-13](../absorption-backlog.md) | The unactioned instruction: enumerate the six, retire or merge one, **before any new store lands**. |

## Evaluation

| Document | Note |
|---|---|
| [`README.md`](../../README.md) | The five verdicts, never collapsed, with their ISO/IEC 9646 and ITU-T Z.140 lineage. `UNMEASURABLE` is not a pass; `ERROR` dominates `FAIL`. |
| [`docs/evidence/phase-a-windsorai.md`](../evidence/phase-a-windsorai.md) | Calibration: every assertion **observed failing** before the suite meant anything. |
| [`docs/research/answers/R1-answer-eval-harness.md`](../research/answers/R1-answer-eval-harness.md) | Grades the harness. Keep `GreenContract`; do not adopt a general LLM-eval framework. Names side-effect and reconciliation checks as a **High** omission. |
| [`docs/findings.d/F76-…`](../findings.d/F76-the-eval-can-fail-what-it-cannot-do-is-generalise.md) | ⭐ The correction that matters: the eval **can** fail — what is unproven is that it **generalises**. |
| [`evals/`](../../evals/) | The corpus, as hashed data verified on load. **One file, one connector, 6,762 bytes.** 48 connectors have never been scored. |
| [`docs/evidence/evaluator-isolation-2026-08-22.md`](../evidence/evaluator-isolation-2026-08-22.md) | Grader separation, watched refusing. *Who holds the credential*, not the process boundary. |
| [`docs/protocol/METRICS.md`](../protocol/METRICS.md) | Ten metrics, two built. `instrument_live=False` on a zero. **A rate over an empty population is not zero.** |
| [`docs/protocol/QUALITY_GATES.md`](../protocol/QUALITY_GATES.md) | Seven gates, six deterministic **by design** — "an agent asked whether it handed over enough context will answer yes". |
| [`docs/raw_research/zeus_world_ui_research_pack/05_EVALUATION_PROTOCOL.md`](../raw_research/zeus_world_ui_research_pack/05_EVALUATION_PROTOCOL.md) | ⭐ A graduation rule with target thresholds and a prototype ladder. Theme-independent; survives the Zeus supersession entirely. |
| [`docs/raw_research/agent_factory_agent_genome_research_pack/evaluation/monitoring_benchmarking_spec.md`](../raw_research/agent_factory_agent_genome_research_pack/evaluation/monitoring_benchmarking_spec.md) | Observability levels, a benchmark vault, credit assignment. *"Do not optimize all of these."* |
| [`docs/raw_research/agent-factory-bootstrap-pack/docs/06-experiments/EVALUATION_GATES.md`](../raw_research/agent-factory-bootstrap-pack/docs/06-experiments/EVALUATION_GATES.md) | A minimum gate shape. |

## Simulations

| Document | Position |
|---|---|
| [`docs/raw_research/agent_factory_agent_genome_research_pack/simulation/hypertuning_spec.md`](../raw_research/agent_factory_agent_genome_research_pack/simulation/hypertuning_spec.md) | **FOR.** Hierarchical search, multi-objective trial score, anti-overfitting, replication. |
| [`docs/raw_research/agent_factory_agent_genome_research_pack/simulation/search_space.yaml`](../raw_research/agent_factory_agent_genome_research_pack/simulation/search_space.yaml) | The proposed search space. |
| [`docs/specs/ui-future-features.md` §8](../specs/ui-future-features.md) | ⛔ **AGAINST.** *"Run simulations until it completes"* — the instinct to skip this is right, for a stronger reason than the instinct. |
| [`docs/specs/terminal-configuration.md` §5](../specs/terminal-configuration.md) | A narrower use that survives: **rehearse the harness without spending a token.** |
| [`docs/agent-army/CURRENT_STATE.md`](../agent-army/CURRENT_STATE.md) | MEASURED: zero occurrences of `simulat*` in `factory/`. `corpus.py` loads a fixture, which is not a simulator. |
| [`docs/raw_research/agent_factory_army_ui_concept_pack/11_EVALUATION_WARGAMES_DOCTRINE.md`](../raw_research/agent_factory_army_ui_concept_pack/11_EVALUATION_WARGAMES_DOCTRINE.md) | War games as the UI-facing form of the same idea, with required properties. |

## Optimization

| Document | Note |
|---|---|
| [`docs/research/answers/R4-answer-agnostic-optimizer.md`](../research/answers/R4-answer-agnostic-optimizer.md) + [`-run2`](../research/answers/R4-answer-agnostic-optimizer-run2.md) | Two independent runs, same verdict. Carries the **Fitness Qualification Gate** — five pre-search tests, each with an abort condition. Prior art: DSPy/MIPROv2, GEPA, TextGrad, Trace, OpenEvolve, AlphaEvolve. |
| [`docs/research/SYNTHESIS.md` §6](../research/SYNTHESIS.md) | The **never-optimise list** — retry caps, gate thresholds, tenancy checks, timeouts, evaluator thresholds, corpus. *"Safety specification, not hyperparameters."* And the screening order: model ≫ effort ≫ tool interface ≫ context layout ≫ prompt structure ≫ wording. |
| [`docs/raw_research/agent_factory_rd_consolidation_pack/05_OPTIMIZATION_AND_META_OPTIMIZATION.md`](../raw_research/agent_factory_rd_consolidation_pack/05_OPTIMIZATION_AND_META_OPTIMIZATION.md) | Optimization / reverse optimization / meta-optimization, optimizer portfolio, optimizer racing, mandatory post-run failure analysis. |
| [`docs/raw_research/agent_factory_rd_consolidation_pack/09_PIPELINE_AND_OBJECT_AGNOSTIC_OPTIMIZATION.md`](../raw_research/agent_factory_rd_consolidation_pack/09_PIPELINE_AND_OBJECT_AGNOSTIC_OPTIMIZATION.md) | Pipeline genome; an object-agnostic experimental engine. |
| [`docs/absorption-backlog.md` AB-05](../absorption-backlog.md) | The Fitness Qualification Gate was **rejected against a paraphrase**, not against the design that was already on file. |
| [`README.md`](../../README.md) | Optimizer is deliberately absent. Unlock: *"a working eval — the fitness function **is** the eval score."* |

## Self-improvement

| Document | Note |
|---|---|
| [`docs/raw_research/agent_factory_rd_consolidation_pack/07_SELF_HOSTING_BUILD_SEQUENCE.md`](../raw_research/agent_factory_rd_consolidation_pack/07_SELF_HOSTING_BUILD_SEQUENCE.md) | **AF-SH0**, the self-hosting point, and a staged progression. |
| [`.agent-platform/bootstrap/docs/AUTONOMY_LADDER.md`](../../.agent-platform/bootstrap/docs/AUTONOMY_LADDER.md) + [`ROADMAP_TO_VISION.md`](../../.agent-platform/bootstrap/ROADMAP_TO_VISION.md) | **Rank progression** as the roadmap primitive, each rank with a promotion rule. The natural competitor to `README.md`'s absence-table-with-unlock-conditions. |
| [`docs/raw_research/agent-factory-bootstrap-pack/docs/07-implementation/FEATURE_INTEGRATION_SEEDS.md` §9, §15](../raw_research/agent-factory-bootstrap-pack/docs/07-implementation/FEATURE_INTEGRATION_SEEDS.md) | Repetition → deterministic meta-tools; the self-hosting milestone staged through gates rather than as a switch. |
| [`docs/raw_research/agent_factory_rd_consolidation_pack/04_AGENT_HEALTH_READINESS_TRAINING.md`](../raw_research/agent_factory_rd_consolidation_pack/04_AGENT_HEALTH_READINESS_TRAINING.md) | Pre-deployment skill-up, curriculum optimizer, "experience is evidence". |
| [`docs/research/answers/R10-…`](../research/answers/R10-answer-hierarchical-wiki-agent-training.md) §4 | *"Auto-researcher loop: compound or corrupt?"* — the question this whole category turns on. |

## Self-maintenance

| Document | Note |
|---|---|
| [`.agent-platform/bootstrap/docs/SELF_MAINTENANCE.md`](../../.agent-platform/bootstrap/docs/SELF_MAINTENANCE.md) | Self-maintenance as a first-class goal; Agent Factory as its own client. |
| [`docs/raw_research/agent-factory-bootstrap-pack/docs/07-implementation/FEATURE_INTEGRATION_SEEDS.md` §7](../raw_research/agent-factory-bootstrap-pack/docs/07-implementation/FEATURE_INTEGRATION_SEEDS.md) | Reliability Corps, MAPE-K-shaped, *"deterministic detection/gating where practical"*. |
| [`docs/raw_research/agent-factory-bootstrap-pack/organizations/presets/factory-reliability-corps.seed.yaml`](../raw_research/agent-factory-bootstrap-pack/organizations/presets/factory-reliability-corps.seed.yaml) | The preset, as a seed. |
| [`.agent-platform/bootstrap/source/Agent Factory Vision.txt` §5](../../.agent-platform/bootstrap/source/Agent%20Factory%20Vision.txt) | The MAPE-K reinterpretation: observe → diagnose → intent contract → construct → simulate → evaluate → gate → canary → deploy → measure → writeback. |
| [`docs/protocol/`](../protocol/) (whole pack) | The **built** fragment of this idea: a run should not unknowingly repeat a failure whose evidence already exists in its own history. One hypothesis, nothing else. |

## Safety / governance

| Document | Note |
|---|---|
| [`docs/specs/architecture-v0.md` §4, §9](../specs/architecture-v0.md) | The isolation ladder; and what does not change — merging stays human, per-secret approval stays human, evidence-gated deploys stay. |
| [`docs/research/answers/R3-answer-control-plane.md`](../research/answers/R3-answer-control-plane.md) | Bounded execution, orphan reaping, fail-closed gates, tenant isolation. **Tamper-evidence is not a trust boundary.** |
| [`docs/research/answers/R16-outside-evidence-lane.md` §3](../research/answers/R16-outside-evidence-lane.md) | ⚠ **A container does nothing about prompt injection — the lethal trifecta survives it intact.** |
| [`docs/protocol/QUALITY_GATES.md`](../protocol/QUALITY_GATES.md) | `BLAST_RADIUS` is the only mandatory human gate. `needs_paul` is **display-only today: it renders, it does not refuse.** |
| [`docs/protocol/ROLLOUT.md`](../protocol/ROLLOUT.md) | Kill criteria stated **before** the evidence, so they cannot be chosen to fit it. |
| [`docs/release-gate/AF-RELEASE-GATE-01-2026-09-01.md`](../release-gate/AF-RELEASE-GATE-01-2026-09-01.md) | ⛔ The publication boundary. **Read before redistributing any part of this corpus.** |
| [`docs/evidence/switchboard-security-preflight-2026-08-31.md`](../evidence/switchboard-security-preflight-2026-08-31.md) | A source-only security preflight before any third-party tool is launched. |
| [`.agent-platform/bootstrap/docs/COMMERCIAL_AUTONOMY_POLICY.md`](../../.agent-platform/bootstrap/docs/COMMERCIAL_AUTONOMY_POLICY.md) | What agents may do inside budgets and what requires a human. |
| [`docs/raw_research/agent2_sihre_consolidation_pack/05_quantitative_agent2_features.md`](../raw_research/agent2_sihre_consolidation_pack/05_quantitative_agent2_features.md) | **Tail-risk-aware autonomy** — authority from downside tails, not mean performance. |
| [`docs/agent-army/APPROVED_CONCEPTS.md`](../agent-army/APPROVED_CONCEPTS.md) · [`IMPLEMENTATION_HANDOFFS.md`](../agent-army/IMPLEMENTATION_HANDOFFS.md) | The governance boundary itself. |

## UI / UX

| Document | Note |
|---|---|
| [`docs/research/ui-surface-inventory.md`](../research/ui-surface-inventory.md) | What exists, measured. The four planes and who belongs in each. *"The factory is not a terminal manager."* |
| [`docs/specs/ui-future-features.md`](../specs/ui-future-features.md) | Three features with the evidence for and against each, plus a second batch. Read-only first; requirements refinement first. |
| [`docs/FACTORY-UI-PROMPT.md`](../FACTORY-UI-PROMPT.md) | ⭐ **Phase 0 is the event ledger, no UI — "this is the real work."** And an acceptance test written so a simulator cannot pass it. |
| [`docs/research/answers/R13-answer-architecture-and-ui-survey.md`](../research/answers/R13-answer-architecture-and-ui-survey.md) + [`run2`](../research/answers/R13-answer-architecture-and-ui-survey-run2.md) | The option space, then the four questions run 1 left open. Run 2 holds the **APPROVE-leaves-the-building** finding. |
| [`docs/research/answers/R14-answer-structure-model-and-joy.md`](../research/answers/R14-answer-structure-model-and-joy.md) §6 | The design brief: IA, hierarchy, colour, motion, delight. |
| [`docs/raw_research/zeus_world_ui_research_pack/`](../raw_research/zeus_world_ui_research_pack/) | Eight design doctrines, ten extreme experiments, ten business-value concepts, an evaluation protocol and ten readiness gates. **Theme superseded; protocol and gates are not.** |
| [`docs/raw_research/agent_factory_army_ui_concept_pack/03_ARMY_WORLD_UI.md`](../raw_research/agent_factory_army_ui_concept_pack/03_ARMY_WORLD_UI.md) | The battlefield view, and environmental storytelling mapped to real state. |
| [`docs/evidence/render-pass-2026-08-22.md`](../evidence/render-pass-2026-08-22.md) · [`impeccable-detector-pass-2026-08-22.md`](../evidence/impeccable-detector-pass-2026-08-22.md) | What a render pass catches that a static rule set cannot, **and the reverse**, both stated. |
| [`docs/design/session-ui-and-intake.html`](../design/session-ui-and-intake.html) | Session UI and intake design. |

## Switchboard / Mission Control

| Document | Note |
|---|---|
| [`docs/specs/control-room.md`](../specs/control-room.md) | From managing sessions to **running teams**. Build slices, an acceptance test, refusals, and a basis register. |
| [`docs/design/switchboard-redesign-2026-09-01/REDESIGN-BRIEF.md`](../design/switchboard-redesign-2026-09-01/REDESIGN-BRIEF.md) | ⭐ Hard constraints first, each carrying the failure that produced it. A model for handing design work outward. |
| [`docs/design/switchboard-redesign-2026-09-01/`](../design/switchboard-redesign-2026-09-01/) | The exact payload sent out: seven rendered surfaces, the CSS, the theme tokens, and the source that produced them. |
| [`docs/raw_research/zeus-switchboard-redesign-pack/`](../raw_research/zeus-switchboard-redesign-pack/) | ⭐ What came back — **the only inbound pack containing running code**, plus an integration contract (snapshot + ordered live stream + commands + safety boundaries). |
| [`docs/evidence/switchboard-p1-2026-09-01/README.md`](../evidence/switchboard-p1-2026-09-01/README.md) | Rendered validation in real Chromium, both schemes. *"Three controls, three true statements."* |
| [`docs/evidence/switchboard-security-preflight-2026-08-31.md`](../evidence/switchboard-security-preflight-2026-08-31.md) | The preflight before launch. |
| [`docs/research/answers/R12-answer-session-manager-ui.md`](../research/answers/R12-answer-session-manager-ui.md) | Identity and liveness as the substrate's load-bearing facts, and the blocked-question channel. |
| [`.agent-platform/bootstrap/docs/GAMIFIED_MISSION_CONTROL.md`](../../.agent-platform/bootstrap/docs/GAMIFIED_MISSION_CONTROL.md) · [`SESSION_UI_MVP.md`](../../.agent-platform/bootstrap/docs/SESSION_UI_MVP.md) | The pack's mission-control direction, and *"data model first"*. |
| [`docs/board/`](../board/) · [`docs/artifacts/agent-factory.html`](../artifacts/agent-factory.html) | The surfaces that actually ship. `tickets.json` declares its own authoritative source and *"never hand-edit"*. |

## Research system

| Document | Note |
|---|---|
| [`docs/research/README.md`](../research/README.md) | ⭐ **The neighbours discipline** — every pass carries a table naming what it must NOT answer. The corpus's strongest anti-duplication mechanism. |
| [`docs/research/SYNTHESIS.md`](../research/SYNTHESIS.md) | The decision record. *"Agreement is the control and divergence is the finding."* §17 audits itself and finds seven false statements about its own coverage. |
| [`docs/research/agent-factory-concept-inventory.md`](../research/agent-factory-concept-inventory.md) | Five survey verdicts never collapsed; the comparison basis declared **before** looking. |
| [`docs/reviews/external/README.md`](../reviews/external/README.md) | A two-stage intake for external answers: land unverified, then promote and reconcile in the same sitting. |
| [`docs/absorption-backlog.md`](../absorption-backlog.md) | ⭐ *"A written rejection closes a row. Silence does not."* Nineteen conclusions nobody actioned. |
| [`.agent-platform/bootstrap/docs/CLAUDE_RESEARCH_WORKFLOW.md`](../../.agent-platform/bootstrap/docs/CLAUDE_RESEARCH_WORKFLOW.md) | Subscription-first research, an operator loop, and an output contract per prompt. |
| [`docs/raw_research/agent-factory-bootstrap-pack/docs/08-research-backlog/prompts/CLAUDE_CORPUS_PREPARATION_PROMPT.md`](../raw_research/agent-factory-bootstrap-pack/docs/08-research-backlog/prompts/CLAUDE_CORPUS_PREPARATION_PROMPT.md) | The direct ancestor of this indexing pass, including its **stop condition**. |
| [`docs/CORPUS-AND-DESIGN-PROMPT.md`](../CORPUS-AND-DESIGN-PROMPT.md) | A previous, **unexecuted** attempt at the same job. `docs/corpus/` does not exist. |
| [`.agent-platform/bootstrap/source/Agent Factory Vision.txt` §9–§12](../../.agent-platform/bootstrap/source/Agent%20Factory%20Vision.txt) | The Organizational Research Compiler, its seven modes including **adversarial**, and structured per-mission output. |

## Implementation

| Document | Note |
|---|---|
| [`README.md`](../../README.md) | The build order, and what is deliberately absent with each unlock condition. |
| [`docs/research/SYNTHESIS.md` §5, §8](../research/SYNTHESIS.md) | The nine-step build order, optimisation last; and what changes in this repo. |
| [`docs/CLIENT-INTAKE-PLATFORM-PLAN.md`](../CLIENT-INTAKE-PLATFORM-PLAN.md) | Phases each with an exit criterion **that can fail**, plus a basis register and a "what this plan does not know" section. |
| [`docs/reviews/build-vs-adopt-2026-08-29.md`](../reviews/build-vs-adopt-2026-08-29.md) | Ten build/adopt verdicts, and a prerequisite for *any* adoption stated as a blocker. |
| [`docs/reviews/ticket-repo-crossref-2026-08-29.md`](../reviews/ticket-repo-crossref-2026-08-29.md) | Generated tickets audited against the code: REJECT / RESCOPE / AMBIGUOUS / CONFIRMED NOT STARTED. |
| [`boot-prompts/`](../../boot-prompts/) | 21 session handoffs, the closest thing to a continuous project log. Each states honestly what is **not** done. |
| [`docs/raw_research/agent-factory-bootstrap-pack/docs/07-implementation/IMPLEMENTATION_DAG_SEED.yaml`](../raw_research/agent-factory-bootstrap-pack/docs/07-implementation/IMPLEMENTATION_DAG_SEED.yaml) | Nine phases P0–P8 with seven required gate fields. Marked `status: seed_not_approved`. |
| [`docs/raw_research/agent_factory_agent_genome_research_pack/implementation/ROADMAP.md`](../raw_research/agent_factory_agent_genome_research_pack/implementation/ROADMAP.md) | Thirteen stages from session UI to configurable agents. Stage 0: *keep the simple session UI*. |
| [`docs/raw_research/agent_factory_army_ui_concept_pack/15_IMPLEMENTATION_ROADMAP.md`](../raw_research/agent_factory_army_ui_concept_pack/15_IMPLEMENTATION_ROADMAP.md) | Seven phases, Phase 0 *"preserve primary UI priority"*. |
| [`docs/agent-army/IMPLEMENTATION_HANDOFFS.md`](../agent-army/IMPLEMENTATION_HANDOFFS.md) | The only sanctioned route from research to work. Currently empty. |

## Evidence

| Document | Note |
|---|---|
| [`docs/case-studies/delivery-001-marketing-model.md`](../case-studies/delivery-001-marketing-model.md) | ⭐ 2,351 lines. **The Agent Factory counterfactual** — for each real mistake, would the machinery have caught it, and which control. Plus defect escape distance. |
| [`docs/evidence/marketing-model-v1/`](../evidence/marketing-model-v1/) | The mission's own evidence: claim ledger, contradictions, a **NOT-VISIBLE inventory**, and a read-only role watched refusing a write. |
| [`docs/evidence/control-plane-2026-08-22/README.md`](../evidence/control-plane-2026-08-22/README.md) | 67 KB. Every control watched refusing; mutation harnesses answering *"is any of this load-bearing?"* |
| [`docs/findings.d/`](../findings.d/) | 33 corrected premises, each with a discriminating test. |
| [`docs/evidence/false-succeeded-mechanism.md`](../evidence/false-succeeded-mechanism.md) | A measurement that invalidated a premise three research answers had been built on — and three follow-ups filed rather than a quiet re-read. |
| [`docs/evidence/live-probes-a1-a5-2026-08-22.md`](../evidence/live-probes-a1-a5-2026-08-22.md) | Watched succeeding **and** watched refusing, both required. |
| [`docs/evidence/recurrence-preflight-2026-08-31/README.md`](../evidence/recurrence-preflight-2026-08-31/README.md) | Shadow mode — run the mechanism against real history without letting it act. |
| [`docs/evidence/client-review-readiness-2026-09-01/README.md`](../evidence/client-review-readiness-2026-09-01/README.md) | `RENDERED_CONFIRMED`, and a vocabulary note stating what the contract cannot express. |
| [`docs/evidence/machine-local-state-2026-08-22.md`](../evidence/machine-local-state-2026-08-22.md) | State that lives outside every repository, and is therefore invisible to every gate. |

## Experiments

| Document | Note |
|---|---|
| [`docs/raw_research/agent_factory_agent_genome_research_pack/experiments/EXPERIMENT_BACKLOG.md`](../raw_research/agent_factory_agent_genome_research_pack/experiments/EXPERIMENT_BACKLOG.md) | ⭐ **25 numbered experiments, highest information gain first** — spec/status split, frozen lockfile, quiet vs loud, communication governor, builder+challenger pair, relationship stability, mission readiness, and 18 more. The most actionable experiment list in the corpus. |
| [`docs/raw_research/agent-factory-bootstrap-pack/docs/06-experiments/EXPERIMENT_TEMPLATE.md`](../raw_research/agent-factory-bootstrap-pack/docs/06-experiments/EXPERIMENT_TEMPLATE.md) | Hypothesis / decision informed / candidates / dataset / baseline / primary metrics / **guardrail metrics** and nine more fields. |
| [`docs/research/answers/R10-…` §9](../research/answers/R10-answer-hierarchical-wiki-agent-training.md) | A two-week decisive experiment. |
| [`blueprints/orchestrator_team.yaml`](../../blueprints/orchestrator_team.yaml) | The one experiment that was actually run, and refused. Its unlock threshold is the template for any successor. |
| [`docs/evidence/control-plane-2026-08-22/README.md`](../evidence/control-plane-2026-08-22/README.md) | Mutation harnesses as an experimental method against one's own instruments. |
| [`docs/raw_research/zeus_world_ui_research_pack/09_IMPLEMENTATION_READINESS.md`](../raw_research/zeus_world_ui_research_pack/09_IMPLEMENTATION_READINESS.md) | Ten gates a concept must clear before implementation, including *"no Goodhart reward loop"*. |
| [`docs/protocol/TEST_HARNESS.md`](../protocol/TEST_HARNESS.md) | *"CURRENT vs PROTOCOL_V1"* — labelled EXPERIMENT tier, **not run**. |

## Miscellaneous

| Document | Note |
|---|---|
| [`docs/recon/verified-record-echelon0-2026-09-01.md`](../recon/verified-record-echelon0-2026-09-01.md) · [`leads-no-go-2026-09-01.md`](../recon/leads-no-go-2026-09-01.md) | ⚠ **Commercial venture recon, not platform architecture.** Indexed because it applies the same evidence machinery to a different subject — evidence about the machinery's transferability. One NO-GO, one conflicted GO. |
| [`.agent-platform/bootstrap/docs/COMPUTE_AND_INTEGRATION_FABRIC.md`](../../.agent-platform/bootstrap/docs/COMPUTE_AND_INTEGRATION_FABRIC.md) · [`research/prompts/RDGX_DGX_SPARK.md`](../../.agent-platform/bootstrap/research/prompts/RDGX_DGX_SPARK.md) | Compute placement and a specific hardware target. Unconnected to anything else in the corpus. |
| [`.agent-platform/bootstrap/docs/PRODUCT_NAMING_AND_POSITIONING.md`](../../.agent-platform/bootstrap/docs/PRODUCT_NAMING_AND_POSITIONING.md) · [`BRANDING_NOTE.md`](../../.agent-platform/bootstrap/BRANDING_NOTE.md) · [`…chat_design_pack/12_NAMING_AND_DESIGN_HISTORY.md`](../raw_research/agent_factory_chat_design_pack/12_NAMING_AND_DESIGN_HISTORY.md) | Naming and positioning. The design-history file is genuinely useful: seven stages of how the product concept moved. |
| [`docs/raw_research/agent2_sihre_consolidation_pack/06_cross_domain_inspirations.md`](../raw_research/agent2_sihre_consolidation_pack/06_cross_domain_inspirations.md) | Human behaviour → computational countermeasure, with a design rule. |
| [`docs/raw_research/agent_factory_agent_genome_research_pack/research/high_leverage_frameworks.md`](../raw_research/agent_factory_agent_genome_research_pack/research/high_leverage_frameworks.md) | ⭐ **24 named prior-art sources** — Kubernetes CRD+controller, Nix lockfiles, Open Policy Agent, FIPA ACL speech acts, OpenTelemetry traces, MASEval, MultiAgentBench and 17 more. The corpus's best prior-art index. |
| [`docs/raw_research/*.docx`](../raw_research/) (2 files, 635 KB) | ✅ **Content indexed 2026-09-02.** Both converted to `docs/raw_research/converted/`, read in full, and catalogued under *Agent armies* and *Organizational architecture* above. ⚠ **Residual limit:** their **twelve embedded figures were not extracted** — captions survive, diagrams do not. `research_gap_candidates.md` GAP-01 is narrowed to that. |
| [`tracker.html`](../../tracker.html) | Gitignored generated tracker. Not part of the corpus. |

---

## Where things are NOT

Stated so a reader does not conclude an absence is a gap.

| Looking for | It is not here because |
|---|---|
| Agent Army research documents | They moved to the **sibling repository `agent-army-research`** on 2026-08-30. `docs/agent-army/` is only the boundary. 155 markdown files, 3.6 MB, **not in this review pack**. |
| ADRs | This repository has **none**. The ADRs (ADR-0001..0007) are in the sibling repo and are *research* ADRs — they record how the research programme works, not product decisions. The nearest local equivalents are `SYNTHESIS.md` §6/§7 and `README.md`'s absence table. |
| `docs/spec/` (singular) | The directory is `docs/specs/` (plural), 9 files. |
| `docs/corpus/` | Never created. `CORPUS-AND-DESIGN-PROMPT.md` asked for it; the pass was never run. |
| A concept registry, claims ledger or decision ledger | The bootstrap pack ships **empty templates** for all three (`concepts: []`, `artifacts: []`, a 0-byte `claims.jsonl`). This `docs/_index/` directory is the work those templates asked for. |
| An optimizer, a gym, a supervisor tier, a second comms topology, a platform UI | Each is **deliberately absent** with a named unlock condition. `README.md` §"What is deliberately absent". Reporting them as gaps is the error `agent-factory-concept-inventory.md` §1 exists to prevent. |
