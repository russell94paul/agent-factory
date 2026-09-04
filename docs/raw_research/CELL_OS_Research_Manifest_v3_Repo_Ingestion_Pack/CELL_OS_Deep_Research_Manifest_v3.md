# CELL OS Deep Research Manifest v3

**Version:** 3.0  
**Date:** 2026-09-03  
**Status:** CONTROLLED DRAFT — ingest and reconcile during Phase 1; do not dispatch until activation gates pass  
**Supersedes:** CELL_OS_Optimized_Deep_Research_Prompt_Manifest_v2.md as the proposed forward queue  
**Preserves:** SIHRE_Recommended_Deep_Research_Report_Queue_Legacy.md as historical evidence only

## 1. Revised north star

CELL OS is a configurable operating system for constructing, operating, measuring and improving artificial organizations.

Its first flagship domain is **CELL-Q**, an adaptive multi-model quantitative research and simulation organization. CELL-Q exists to stress-test the generic CELL OS architecture through historical replay, synthetic environments, offline experiments and paper research. It does not define the generic platform and must not introduce live-account execution into the initial scope.

CELL OS should eventually let governed Operatives help design and implement bounded parts of an organization, but no self-building or self-improvement claim is valid without evidence, evaluation, human gates and rollback.

## 2. Repository-grounded baseline

This manifest incorporates the measured Phase 1 audit of agent-factory at commit 827f871 on main.

| Fact | Measured baseline | Consequence |
|---|---:|---|
| Runtime shape | One Python distribution and one flat factory package | Do not impose an empty monorepo |
| Runtime dependencies | PyYAML only | Prefer minimal additions |
| Runtime modules | 68 | Extend only where justified |
| Runtime lines | 23,939 | Existing coupling must be respected |
| Dependency centre | factory/contract.py | New contracts must integrate deliberately |
| Tracked files | 892 | Migration must preserve history and paths |
| Working-tree files | 1,079 | Untracked intake requires reversible handling |
| Documentation files | 560 | Corpus governance is a core problem |
| Existing indexed records | 719 claimed versus 888 measured | Perform an index delta, not a rebuild |
| Tests | 1,016 passed, 2 failed, 2 xfailed | AMBER is the honest baseline ceiling |
| Recorded runs | 10 rows, zero PASS | No local performance inference is valid |
| Returned runs | Seven, all dry-run | Experiment calibration is blocked |
| Named new CELL OS concepts in code | Zero | Treat them as designs, not implementations |

The repository README remains the governing instruction document until a canonical repository-instructions file is approved. Its verdict and basis vocabularies must not be collapsed or silently replaced.

Seven documentation paths are runtime-coupled through hard-coded reads. Research recommendations must not assume they can be moved.

## 3. Status model

### 3.1 Architecture maturity

Use these labels as supplemental architecture metadata without replacing the README verdict system:

- PROVEN — runtime and evidence exist;
- PARTIAL — some implementation and evidence exist;
- SPECIFIED — an accepted specification exists;
- PROPOSED_EXTERNAL — an approved design input exists outside the previous repository corpus;
- EXPERIMENTAL — a falsifiable R&D hypothesis exists;
- NOT_VISIBLE — the search instrument could not inspect the relevant source;
- ABSENT — a sufficiently capable instrument found no source;
- SUPERSEDED — an explicit decision replaced it.

### 3.2 Four independent readiness axes

Every research topic must report four separate states:

1. RESEARCH_READINESS — sufficient question and source scope exist for literature or architecture research.
2. EXPERIMENT_READINESS — data, harnesses and observations exist to test it.
3. IMPLEMENTATION_READINESS — contracts, dependencies and acceptance tests are defined.
4. PROMOTION_READINESS — evidence supports making it canonical or operational.

No mission history can block experiment or promotion readiness without automatically blocking literature research.

## 4. Current implementation versus proposed architecture

### 4.1 Measured implementation anchors

The following have measured code or repository anchors and should be reused:

- factory/contract.py;
- factory/blueprint.py;
- factory/evals.py;
- factory/calibration.py;
- factory/readiness.py;
- factory/forecast.py;
- factory/roadmap.py;
- existing findings, evidence, research-answer and artifact paths;
- existing corpus indexes and regeneration commands;
- existing progress artifacts;
- existing NERVE and Switchboard research.

### 4.2 Proposed external design inputs

The following were introduced through approved project conversations and attached design manifests. Their earlier absence from the repository does not reject them, but none is implemented merely because it is listed here:

- Operative Canonical Layered Model;
- mandatory Operative Kernel and optional layers;
- Mission Compiler;
- Claims–Evidence Graph;
- Capability Graph and capability envelopes;
- Causal World Model;
- Shadow Execution Twin;
- Temporal Executive;
- Earned Authority;
- Operative Immune System;
- Cognitive Economics Engine;
- Experience-to-Doctrine Compiler;
- Domain Plane;
- Domain Genome and Compiler;
- Domain Fabric;
- Domain Data Plane;
- MESA;
- Recursive Operative Genesis;
- CELL-Q.

Each must pass architecture, experiment and promotion gates before becoming canonical.

### 4.3 Naming collision requiring an explicit decision

Cell Blueprint, Cell Genome and Configuration Genome currently appear to describe overlapping ideas. factory/blueprint.py is the implementation anchor. Research must not create a fourth synonym. The canonical terminology decision must specify whether Genome is a property or versioned configuration of a Blueprint, or whether one term supersedes the other.

## 5. Local activation gates — not Deep Research

Complete these repository actions before dispatching the full queue:

### Gate P0-A — Source intake

- ingest v2, v3 and the legacy twenty-report queue as external design sources;
- preserve hashes and provenance;
- reconcile the repository DR01–DR08 queue, legacy twenty-report queue and v3;
- update the research registry and next-action record.

### Gate P0-B — Make existing canon visible

- surface CELL_OS_Canonical_Terminology_vNext.md;
- surface KNOWN_TERMINOLOGY_COLLISIONS.md;
- convert and inspect the two CELL OS DOCX files;
- inspect or extract the XLSX and PDF through appropriate read-only tooling;
- revise all NOT_VISIBLE findings after inspection.

### Gate P0-C — Corpus integrity

- run the existing index regeneration/delta mechanism;
- add the missing CELL OS records;
- preserve existing indexes and provenance;
- identify duplicate and superseded artifacts.

### Gate P0-D — Migration safety

- resolve the active-worktree decision;
- identify the authoritative checkout;
- protect the seventeen overlapping modified files;
- preserve the AMBER test baseline;
- remeasure HEAD before each migration batch.

### Gate P0-E — Observation generation

After the safe migration gates permit it, complete at least one bounded, non-dry-run, non-financial repository mission with acceptance evidence.

This gate is required before local covariance estimation, empirical ablation, homeostasis threshold calibration or performance claims. It is not required for narrow prior-art or architecture research.

## 6. Common Deep Research contract

Apply this contract to every lane:

1. Read the supplied CELL OS corpus and completed research before external search.
2. State the precise unresolved question and why local measurement cannot answer it alone.
3. Reuse completed R1–R19 work; do not rerun answered questions.
4. Prefer original research, official standards and first-party technical documentation.
5. Distinguish sourced fact, measured repository fact, inference, design proposal and speculative R&D.
6. Seek disconfirming evidence and preserve unresolved disagreements.
7. Distinguish novelty of a primitive from novelty of a combination or implementation.
8. Never infer implementation from documentation.
9. Report the four readiness axes separately.
10. For every recommended component specify responsibility, runtime scope, inputs, outputs, state, dependencies, configuration, failure modes, evidence and benchmark.
11. Compare benefits against cost, latency, complexity, safety, maintainability and coordination overhead.
12. Prefer the smallest stable kernel and attachable mission-conditioned capabilities.
13. Use KEEP, MODIFY, MERGE, RESEARCH, DEFER or REJECT decisions.
14. Produce citations and a compact claim-to-source ledger.
15. Keep CELL-Q within historical replay, synthetic environments, offline experiments and paper research.
16. Do not provide live-account integration, order-execution instructions or specific investment recommendations.

## 7. Deep Research lane sequence

# CELL-DR-01 — Canonical Architecture Validation and Prior-Art Delta

## Decision question

What is the smallest coherent and defensible CELL OS architecture after reconciling the measured agent-factory implementation, completed research and approved external design inputs?

## Scope

Validate rather than repeat the already-completed broad novelty search. Compare only consequential unresolved architecture claims:

- Agent versus Operative versus Operative Cell;
- Cell versus Cell Mesh versus Organization;
- runtime kernel versus control plane;
- mandatory versus optional layers;
- Cell Blueprint, Cell Genome and Configuration Genome;
- HyperMESH, CELL ADAPT, CELL Foundry, MESA and Shadow Twin responsibilities;
- proposed Domain Plane and CELL-Q boundaries;
- recursive construction claims;
- existing multi-agent, organizational and workflow-system prior art.

## Required output

- canonical responsibility map;
- component boundary diagram;
- terminology decisions and collision register;
- measured current-versus-proposed matrix;
- required-versus-optional layer matrix;
- defensible differentiation statement;
- rejected complexity;
- decisions that require experiments;
- explicit changes required in later lanes.

## Readiness

Research-ready after P0-A through P0-C. Experiment readiness is not required.

# CELL-DR-02 — Link Semantics, Link Contracts and Link Fabric

## Decision question

What formal semantics should govern every connection between Operatives, Cells, Meshes, tools, memory, domains and organizations?

## Scope

This is the major gap identified by the measured design delta. Research:

- Link as a first-class typed entity;
- Link Contract;
- Link Type Registry;
- Link Fabric;
- ownership and authority;
- directionality and multiplicity;
- synchronous, asynchronous and event links;
- reliability, ordering and idempotency;
- capability and trust requirements;
- evidence and provenance flow;
- budgets, latency and failure policy;
- link health and degradation;
- local, cross-Mesh and federated links;
- reconfiguration and compatibility;
- CellBus relationship.

Compare relevant protocol, actor, workflow, graph, service-mesh and multi-agent contract approaches without copying their terminology blindly.

## Required output

- canonical Link schema;
- Link Contract schema;
- Link Type Registry;
- compatibility rules;
- failure and recovery state machine;
- observability requirements;
- security and governance rules;
- minimal implementation interface;
- tests for invalid, degraded and adversarial links;
- integration map for contract.py and CellBus.

## Readiness

Research-ready after P0-B. Experiment-ready after a minimal two-component test harness exists.

# CELL-DR-03 — HyperMESH Context, Memory, Evidence and Capability Substrate

## Decision question

How should CELL OS represent and retrieve context, memory, evidence, capabilities, doctrine and organizational state without creating one impossible universal database?

## Scope

Merge repository DR04, orphan R06B and related backlog questions. Research:

- context compilation;
- episodic, semantic, procedural and organizational memory;
- temporal and provenance-aware retrieval;
- Claims–Evidence Graph;
- Capability Graph;
- contextual trust;
- transactive memory;
- contradiction handling;
- confidence and evidence decay;
- memory consolidation and forgetting;
- graph, relational, event, vector and artifact stores;
- tenancy and access;
- Domain overlays;
- Goodhart resistance.

## Required output

- HyperMESH logical architecture;
- canonical object and relation model;
- storage-responsibility matrix;
- context-assembly contract;
- evidence and capability schemas;
- confidence and decay policy;
- contamination and false-consensus controls;
- minimal v1 design compatible with the current flat Python package;
- benchmark and failure-injection plan.

## Readiness

Research-ready after P0-B and P0-C. Local performance validation awaits real missions.

# CELL-DR-04 — Operative Kernel, Optional Layers, Lifecycle and Genesis

## Decision question

What is the minimum governed architecture that makes an Operative materially different from a conventional tool-using agent?

## Scope

Research:

- identity and evidence-backed experience;
- Mission Contracts and Mission Compiler;
- Cell Blueprint/Genome representation;
- context and cognition interfaces;
- skill and tool execution;
- memory mounts;
- evidence and verification;
- authority and budgets;
- health and readiness;
- temporal state;
- deployment and isolation;
- lifecycle, quarantine, recovery and retirement;
- optional profiles;
- bounded Operative Genesis.

The design must show which functions belong inside the Operative Kernel, the surrounding Operative Cell, shared Mesh services and the CELL OS control plane.

## Required output

- canonical layered model;
- mandatory kernel;
- optional layer catalog;
- lifecycle state machine;
- component contracts;
- configuration example grounded in blueprint.py;
- evidence-backed readiness schema;
- conventional-agent versus Operative benchmark;
- Genesis pipeline with human certification and rollback;
- minimal Operative v1 implementation path.

## Readiness

Research-ready after CELL-DR-01 and CELL-DR-03. Experimental proof requires P0-E.

# CELL-DR-05 — SIHRE Adaptive Cognition and Selective Verification

## Decision question

When should an Operative use direct reasoning, adaptive routing or a heterogeneous reasoning ensemble, and how should it control trust, disagreement and verification?

## Scope

Merge the surviving portions of legacy reports on:

- heterogeneous experts;
- cognitive portfolio theory;
- dynamic cognitive topology;
- contextual trust;
- Value of Information;
- selective research, testing and simulation;
- disagreement preservation;
- uncertainty calibration;
- correlated expert failure;
- trust updates under non-stationarity;
- abstention and human escalation;
- test-time compute allocation;
- recursive use across module, Operative and Mesh levels.

## Required output

- Direct, Adaptive and SIHRE profiles;
- expert and message contracts;
- routing and stopping policy;
- correlation-aware trust model;
- Value-of-Information policy;
- verification independence rules;
- uncertainty propagation contract;
- computational cost controls;
- synthetic benchmark now;
- empirical validation plan gated on P0-E.

## Readiness

Literature and architecture research are ready after CELL-DR-03 and CELL-DR-04. Local portfolio calibration is blocked until sufficient accepted missions exist.

# CELL-DR-06 — CELL ADAPT Optimization and Causal Contribution

## Decision question

How should CELL ADAPT optimize mixed configuration, cognition and topology variables safely and efficiently across multiple objectives?

## Scope

Research:

- discrete, continuous, conditional and graph variables;
- Bayesian, evolutionary, bandit and population methods;
- multi-objective and constrained optimization;
- surrogate and multi-fidelity methods;
- successive halving and early stopping;
- warm starts and transfer;
- causal experiment design;
- ablation and factorial experiments;
- interaction effects;
- Shapley approximations;
- Mesh Gradient;
- safe exploration;
- canaries and rollback;
- stable-field locks;
- reverse optimization;
- non-stationary objectives.

Do not optimize a metric that lacks a stable contract or validation instrument.

## Required output

- search-space and genome schema;
- optimizer-selection policy;
- Pareto promotion policy;
- causal-contribution framework;
- Mesh Gradient definition;
- experiment and ablation protocol;
- acceleration strategy;
- safe self-improvement envelope;
- research design usable before mission history;
- empirical stages activated as observations accumulate.

## Readiness

Method research is ready after CELL-DR-04 and CELL-DR-05. Measured ablation and local optimizer ranking require P0-E and multiple comparable runs.

# CELL-DR-07 — Cell Meshes, Recursive Control, Foundry and MESA

## Decision question

How should CELL OS construct, coordinate, diagnose and improve artificial organizations without unstable recursion or coordination overhead?

## Scope

Research:

- hierarchical, parallel, pipeline, council, market, swarm and federated topologies;
- Mesh Architecture, Topology and Hierarchy as distinct concepts;
- C-MESH, T-MESH and OS-MESH;
- Mission Hypergraphs;
- morphogenetic reconfiguration;
- recursive control stability;
- uncertainty propagation across levels;
- organizational health and debugging;
- Shadow Organization and counterfactual evaluation;
- CELL Foundry Discover → Translate → Prove;
- MESA separation of evidence, analogy and performance confidence;
- capability promotion;
- bounded Recursive Operative Genesis.

Include a strict filter against superficial biological or social analogy.

## Required output

- topology taxonomy and selection policy;
- recursive control contracts;
- coordination-cost model;
- safe reconfiguration invariants;
- organizational-debugger design;
- Shadow Organization architecture;
- Foundry and MESA records;
- recursive-improvement gates;
- experiments that can falsify each frontier proposal.

## Readiness

Research-ready after CELL-DR-02, CELL-DR-05 and CELL-DR-06. Performance promotion requires real Mesh observations.

# CELL-DR-08 — Domain Plane, Domain Genome and Cross-Domain Portability

## Decision question

How should a generic CELL OS acquire domain-specific data, concepts, skills, policies, evaluations and simulations without embedding the domain inside the Operative Kernel?

## Scope

The Domain family is a PROPOSED_EXTERNAL design input. This lane must first test whether a vertical Domain Plane is the correct abstraction.

Research:

- Domain Plane;
- Domain Genome and Compiler;
- Domain Fabric;
- Domain Data Plane;
- domain ontology and temporal semantics;
- domain skill and tool packs;
- domain evidence standards;
- domain policies and authority;
- domain evaluations and simulators;
- Domain Cell Mesh versus new Mesh categories;
- cross-domain translation;
- portability and negative transfer;
- Regime-Adaptive Domain Twins.

Avoid inventing DOMAIN-MESH or DOMAIN-DB if existing Cell Mesh and data abstractions already cover their semantics.

## Required output

- accept, modify or reject the Domain Plane;
- domain responsibility map;
- Domain Genome schema;
- compiler pipeline;
- data-plane decomposition;
- domain attachment contract;
- cross-domain portability test;
- minimal domain pack;
- architecture decision separating generic and domain-specific code.

## Readiness

Research-ready after a local Domain design record is added and CELL-DR-01, CELL-DR-03 and CELL-DR-07 complete. Implementation remains deferred.

# CELL-DR-09 — CELL-Q Offline Quantitative Research Organization

## Decision question

Can the proposed generic CELL OS architecture support a scientifically defensible quantitative research and simulation organization without contaminating the core platform?

## Scope and boundary

CELL-Q is limited to:

- historical replay;
- synthetic environments;
- offline experiments;
- paper research;
- educational model evaluation.

Exclude live accounts, brokerage connectivity, real-money execution, specific trades and investment recommendations.

Research the architecture for:

- hypothesis and idea generation;
- falsification planning;
- data quality and point-in-time correctness;
- event time, ingestion time and revision vintages;
- feature and signal lineage;
- experiment orchestration;
- robust backtesting methodology;
- leakage and data-snooping controls;
- multi-objective optimization;
- benchmark suites and hidden holdouts;
- model, dataset, feature and experiment registries;
- simulated multi-model allocation;
- correlation and dependency-aware evidence fusion;
- drift and degradation detection;
- fundamental, economic and news-event analysis;
- uncertainty, contradiction and abstention;
- model promotion, quarantine and retirement;
- post-experiment learning.

Do not treat agreement among dependent models as independent confirmation. Do not assume a universal bullish/bearish label is meaningful across entities, horizons and regimes.

## Required output

- complete idea-to-evidence lifecycle;
- deterministic software versus Operative responsibility map;
- point-in-time Domain Data Plane;
- experiment and model registry schemas;
- backtest and robustness standards;
- simulated multi-model evaluation architecture;
- evidence-fusion and abstention design;
- drift state machine;
- benchmark and leakage tests;
- paper-research Cell Mesh roles;
- smallest credible CELL-Q demonstration;
- proof that domain-specific concerns remain outside the generic kernel.

## Readiness

Research-ready after CELL-DR-08. Experiments require suitable historical or synthetic datasets; operational promotion is out of scope.

# CELL-DR-10 — Final MESA Synthesis and Build Program

## Decision question

Which researched components should become canonical CELL OS architecture, which require experiments, and what is the smallest credible build sequence?

## Scope

Synthesize all accepted reports. Perform external follow-up only for material unresolved contradictions.

Reconcile:

- measured implementation;
- completed R1–R19 evidence;
- repository DR01–DR08;
- legacy twenty-report queue;
- v2 and v3 manifests;
- canonical ontology;
- Operative architecture;
- Link Fabric;
- HyperMESH;
- SIHRE;
- CELL ADAPT;
- Mesh/Foundry/MESA;
- Domain Plane;
- CELL-Q;
- NERVE integration requirements;
- Project Tracker and forecast requirements.

## Required output

- final canonical architecture;
- terminology and entity model;
- current-versus-target matrix;
- component and interface catalog;
- required-versus-optional layers;
- architecture decision register;
- rejected and deferred concepts;
- experiment and benchmark program;
- implementation maturity ledger;
- dependency-ordered roadmap;
- Project Tracker source model;
- smallest self-building milestone;
- smallest CELL-Q offline demonstration;
- repository integration map;
- final research gap register.

Every canonical recommendation must cite its supporting evidence and readiness state.

## Readiness

Run only after all accepted prior lanes are ingested and reconciled.

## 8. Product-surface disposition

Do not create another broad NERVE research lane by default. SWITCHBOARD-UX and NERVE-DESIGN already exist.

Create a local integration-gap audit that asks:

- which canonical runtime states lack a UI representation;
- which UI controls lack a backend contract;
- which prototype components are purely visual;
- which tracker metrics have a measurable source;
- how prototype HTML should be preserved while production components are introduced.

Only dispatch targeted external research if the audit identifies a consequential unanswered question.

## 9. Legacy queue disposition

| Legacy item | v3 disposition |
|---|---|
| Repository DR01 | Superseded by completed prior-art work and CELL-DR-01 delta |
| Repository DR02 | Merged into CELL-DR-05; empirical phase gated |
| Repository DR03 | Merged into CELL-DR-05 and CELL-DR-07 |
| Repository DR04 | Merged into CELL-DR-03 |
| Repository DR05 | Architecture in CELL-DR-04/05; calibration deferred |
| Repository DR06 | Merged into CELL-DR-04/06/09 |
| Repository DR07 | Analogy filter retained in CELL-DR-07 |
| Repository DR08 | Close by surfacing existing ontology |
| R06B | Merged into CELL-DR-03 |
| Legacy twenty-report queue | Preserved as historical; mapped into v3 |
| RB NOT_RESEARCH items | Convert to project tickets |

## 10. Execution order

| Wave | Work | Condition |
|---|---|---|
| Local 0 | P0-A through P0-D | Must precede dispatch |
| A | CELL-DR-01 | Establish canonical boundaries |
| B | CELL-DR-02 and CELL-DR-03 | May run separately after A |
| C | CELL-DR-04 | Requires A and B |
| D | CELL-DR-05 and CELL-DR-06 | Run separately after C |
| E | CELL-DR-07 | Requires D and Link semantics |
| Local Domain | Write approved Domain design record | Required before DR-08 |
| F | CELL-DR-08 | Requires A, B and E |
| G | CELL-DR-09 | Requires F |
| Observation | P0-E and further safe missions | Activates empirical branches |
| Final | CELL-DR-10 | Requires all accepted reports |

Do not launch every lane simultaneously. Each lane must receive accepted dependency outputs.

## 11. File identifiers

- CELL-DR-01-CANONICAL-ARCHITECTURE-DELTA
- CELL-DR-02-LINK-FABRIC
- CELL-DR-03-HYPERMESH
- CELL-DR-04-OPERATIVE-KERNEL
- CELL-DR-05-SIHRE-COGNITION
- CELL-DR-06-CELL-ADAPT
- CELL-DR-07-MESH-FOUNDRY-MESA
- CELL-DR-08-DOMAIN-PLANE
- CELL-DR-09-CELL-Q-OFFLINE-RESEARCH
- CELL-DR-10-FINAL-MESA-SYNTHESIS

Recommended report filename:

    CELL_DR_<number>_<short_name>_Report_<YYYY-MM-DD>.pdf

## 12. Report ingestion protocol

After each research run:

1. Preserve the original report unchanged under raw research.
2. Record prompt, date, source scope and report hash.
3. Update the research registry.
4. Produce a short synthesis and gap delta.
5. Separate sourced, measured, derived, proposed and speculative claims.
6. Record contradictions and supersession candidates.
7. Do not update canonical architecture without an explicit architecture decision.
8. Update the Project Tracker only from evidence-backed status changes.

## 13. Activation decision

This v3 manifest becomes dispatchable only when the Phase 1 addendum confirms:

- all attached source manifests are indexed;
- the canonical ontology is visible;
- binary-document visibility gaps are resolved or explicitly bounded;
- queue reconciliation is complete;
- the active worktree and overlapping edits are protected;
- CELL-DR-01 has a verified attachment list;
- no local measurement is being misclassified as external research.

Until then, its status remains CONTROLLED DRAFT.
