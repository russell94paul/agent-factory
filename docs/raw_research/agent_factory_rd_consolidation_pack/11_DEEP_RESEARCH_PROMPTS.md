# Deep Research Prompts

## Prompt A — HyperMESH

### Objective

Design and critically evaluate a hierarchical, federated, mission-aware knowledge architecture for Agent organizations.

Working model:

- A-MESH — Agent knowledge
- T-MESH — Team knowledge
- C-MESH — Command knowledge
- G-MESH — Global organizational knowledge
- HyperMESH — policy-controlled federation

### Required research

Compare against:

- knowledge graphs
- federated/distributed KGs
- temporal KGs
- GraphRAG
- hybrid RAG
- vector DBs
- blackboards
- shared workspaces
- global workspace architectures
- organizational memory
- transactive memory
- stigmergy
- pub/sub
- event sourcing
- data mesh/fabric
- semantic web / SPARQL federation
- provenance/truth-maintenance systems

For each determine:
1. prior art
2. implementation architecture
3. strengths
4. failure modes
5. what HyperMESH adds
6. whether contribution is meaningful or only terminology

### Architecture alternatives

Compare:

- centralized graph
- namespaced shared graph
- graph per Agent
- graph per Team
- hierarchical graphs
- federated graphs
- event-sourced fabric
- graph-of-graphs
- local-first memory
- materialized org views
- mission-projected graphs
- graph + vector
- unified graph/vector/text stores

### Security

Design cross-MESH access using:

- RBAC
- ABAC
- ReBAC
- purpose-bound access
- mission-scoped access
- row/node/edge permissions
- redaction
- derived views

### Mission Context Compiler

Research:
ticket -> formal Mission Contract -> authorization -> source selection -> retrieval -> conflict/freshness checks -> context compilation.

### Knowledge lifecycle

Design:
Agent -> A-MESH -> KCR -> validation -> dedupe -> contradiction -> temporal validity -> scope -> Team/Command/Global promotion.

### Dynamic retrieval/indexing

Investigate:
Retrieval Planner vs Index Optimizer.

### Evaluation

Measure:

- relevant-context recall
- irrelevant-context rate
- time to first useful evidence
- time to root cause
- mission success
- turns
- tokens
- latency
- cross-team reuse
- stale-information failures
- access leakage
- provenance completeness

### Output

Produce:
prior-art map, architecture matrix, recommended P0, scale-out design, security model, MCC spec,
KnowledgeRequest protocol, KCR protocol, storage options, evaluation plan, implementation roadmap,
research hypotheses and whitepaper opportunities.

---

## Prompt B — Enhanced Agent / Agent Genome

### Objective

Determine how to design a deeply configurable Agent whose behavior, cognition, knowledge, tools,
communication, authority, collaboration, health, training and resource use are expressed as a versioned Agent Genome.

### Research taxonomy

Cover:

- identity
- role
- domain
- authority
- model
- reasoning
- planning
- decomposition
- verification
- exploration
- skepticism
- risk
- autonomy
- escalation
- tools
- permissions
- budget
- retries
- context
- communication
- knowledge
- memory
- HyperMESH
- retrieval
- learning
- adaptation
- collaboration
- relationships
- health
- recovery
- evaluation
- certification
- lifecycle
- deployment
- prohibitions

Search transferable mechanisms from:

- cognition
- psychology
- neuroscience
- org science
- team science
- education
- military organization
- aviation
- medicine
- biology
- immune systems
- swarm systems
- markets
- sports
- manufacturing
- control theory
- distributed systems
- reliability engineering

Reject cosmetic anthropomorphism.

### Capability model

Separate:
declared specialization, certified capability, historical experience, current health,
mission readiness, team synergy, knowledge freshness, learning velocity.

### Curriculum

Design forecast-aware training from:
weaknesses + recent failures + future mission demand + capability gaps + resource budget.

### Agent Architect

Design an Agent Architect that can:
interpret role -> search presets -> create candidate Genome -> select knowledge profile -> test -> compare -> propose version.

It must not:
change success criteria, grant permissions, bypass evals, self-certify.

### Optimization

Study joint optimization over:
Agent Genome × model × tools × prompt × reasoning × retrieval × knowledge scope × communication × team topology × training.

### Output

Agent Genome spec, exhaustive taxonomy, presets, inheritance/composition, capability model,
health/readiness, curriculum, Agent Architect, lifecycle, version/certification strategy,
example presets, experiments, roadmap, novelty classification.

---

## Prompt C — Meta-Optimization and Configuration Science

### Objective

Design an optimization system that not only discovers strong Agent/Team configurations,
but learns which optimization strategy discovers them most efficiently.

### Core ideas

- mandatory failure postmortem
- configuration attribution
- forward optimization
- reverse optimization
- minimal contrast pairs
- optimizer portfolio
- optimizer racing
- multi-fidelity evaluation
- surrogate performance models
- quality-diversity archive
- Pareto frontier
- meta-optimizer / optimizer Genome

### Required questions

1. What algorithms are best for discrete, continuous, structural and mixed Agent config spaces?
2. How should the search strategy change by optimization phase?
3. How can failure traces identify likely config causes?
4. How can minimal PASS/FAIL contrast pairs improve attribution?
5. How should optimizer budget be allocated dynamically?
6. How can expensive simulations be reduced with multi-fidelity and surrogates?
7. How should the system prevent benchmark overfitting?
8. How should nested train/validation/certification corpora be structured?
9. How can meta-optimization avoid recursive self-gaming?
10. How can this extend from Agent to Team, Army, HyperMESH and pipelines?

### Output

Reference architecture, optimizer strategy library, experiment memory schema, failure postmortem schema,
portfolio controller, racing protocol, surrogate design, bidirectional search protocol,
quality-diversity/Pareto archive, meta-optimizer, evaluation and roadmap.

---

## Prompt D — Final Consolidation

### Objective

Review all Agent Factory research and current repo together and produce one canonical architecture.

Treat every concept as provisional.

Map dependencies among:

- Agent Genome
- HyperMESH
- Mission Context Compiler
- Knowledge Protocol
- Agent Communication
- Health
- Mission Readiness
- Curriculum
- Agent Architect
- Team Composer
- Organizational Compiler
- Org-IR
- evaluation
- certification
- Optimization Lab
- Meta-Optimization
- monitoring
- self-maintenance
- Army/Federation
- portfolio operations

Identify:

- duplicates
- contradictions
- missing contracts
- circular dependencies
- premature abstractions
- hidden security risks
- unmeasurable concepts
- components that should be config
- components that should remain deterministic infrastructure

Produce one canonical Technical Design and Implementation Document plus a diagram pack,
P0/P1/P2/P3 roadmap, migration from current repo, experiment plan, promotion gates,
rejected alternatives and whitepaper agenda.
