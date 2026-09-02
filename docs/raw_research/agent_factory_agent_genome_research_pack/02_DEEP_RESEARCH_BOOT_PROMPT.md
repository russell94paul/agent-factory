# Deep Research Boot Prompt — Agent Genome & Organizational Hypertuning

You are conducting a **deep architecture + prior-art + experimental-design investigation** for an existing project called **Agent Factory**.

Your job is not to generate a generic survey of AI agents. You must analyze the supplied Agent Factory design artifacts as the baseline system, identify gaps, compare against prior art and current research, and return changes that can be encoded into the platform.

---

## PRIMARY OBJECTIVE

Design the research basis for an extremely expressive but empirically grounded **Agents-as-Config / Agent Genome** system.

The long-term platform should be able to:

1. Define individual agents as versioned executable configurations.
2. Define Agent Teams as compositions of agents + relationships + communication topology + shared policies.
3. Define Agent Armies / higher organizational forms as compositions of teams and organizational protocols.
4. Run replay/sandbox/shadow simulations over many candidate configurations.
5. Hypertune agent, relationship, communication, memory, tool, topology and governance parameters.
6. Discover multiple Pareto-optimal configurations for different mission classes rather than one universal “best agent.”
7. Promote only configurations that pass held-out evaluation, safety/policy gates, replay/shadow validation and recertification.
8. Track enough telemetry to learn which agent/team/organization design works, while avoiding Goodhart’s law, confounding and overfitting.

The configuration is conceptually the agent's **brain/genome**, but use precise engineering terminology. Do not anthropomorphize where measurable parameters are possible.

---

## CURRENT PROJECT BASELINE — TREAT AS CONSTRAINTS

The existing design already includes or proposes:

- Agent → Agent Team → Agent Army as the simple operator-facing hierarchy.
- Agent Factory / Organizational Compiler.
- Intent Contracts and versioned Org-IR.
- Mission Hypergraph / Mesh.
- Collective Cognition / bounded Global Workspace.
- Constitutional Institution / Type System.
- Shadow Twin / counterfactual organization.
- replay, simulation and evaluation.
- capability registry and readiness/preflight.
- Evolution Chamber for candidate designs.
- bounded self-hosting reconciliation.
- deterministic rails for classification/gating/known operations, with agents used for ambiguous synthesis/novel work.
- provenance, evidence, human gates and rollback.
- current missing substrate: per-change green contracts, team eval harness, versioned blueprints/lockfile, stronger monitoring, readiness, organization-level success contracts.

Do not replace these with a greenfield framework unless evidence demonstrates a material advantage.

---

## CORE HYPOTHESIS

An Agent Definition should behave like:

> executable capability contract + job specification + model/tool manifest + memory/context policy + communication policy + authority/security policy + certification record

not merely a system prompt/persona.

The agent data model should separate:

### A. GENOTYPE
Configuration values that can be deliberately changed.

### B. PHENOTYPE
Behavior observed during actual missions.

### C. HISTORY / STATE
Append-only evidence, mission outcomes and experience.

### D. FITNESS / READINESS
Derived mission-conditioned scores.

Research whether this separation is correct and propose a better one if prior art supports it.

---

# RESEARCH QUESTIONS

## R1 — Agent configuration / agent genome

Investigate how an Agent Definition should represent:

### Identity / role
- stable ID and immutable version identity;
- role, mission position, organizational level;
- archetype;
- domain specialization;
- seniority / certification level.

### Model configuration
- model/provider/profile;
- temperature or stochastic controls where available;
- reasoning effort;
- fallback models;
- escalation thresholds;
- routing policies;
- model mixtures/ensembles.

### Cognitive/control architecture
- planning strategy;
- planning depth/horizon;
- reflection/self-critique frequency;
- verification tendency;
- hypothesis count;
- exploration/exploitation;
- uncertainty threshold;
- stopping policy;
- retry/replan policy;
- deliberation budget;
- decomposition granularity;
- deterministic vs agentic operations.

### Context engineering
- context budget;
- retrieval policy;
- recency/freshness weighting;
- provenance weighting;
- diversity requirements;
- evidence threshold;
- summarization/compression strategy;
- contradiction inclusion;
- historical-similarity policy;
- context reservation for tools/reasoning;
- role-specific context compilation.

### Memory
- working/episodic/semantic/procedural/organizational memory;
- read/write permissions;
- TTL/decay;
- consolidation;
- forgetting;
- contradiction retention;
- promotion to Collective Cognition;
- retrieval thresholds;
- memory confidence.

### Tools
- allowed tools;
- preferred tools;
- tool confidence;
- write boundaries;
- tool sequences/macros/meta-tools;
- failure handling;
- deterministic substitutions;
- tool-call budget.

### Skills
- skill IDs and versions;
- proficiency;
- confidence;
- freshness;
- certification evidence;
- prerequisite graph;
- mission-specific skill-up;
- micro-evals before deployment.

### Communication
Research a typed Agent Communication Protocol. Candidate parameters:
- initiative;
- unsolicited-message probability;
- update frequency;
- message verbosity;
- semantic density;
- novelty threshold;
- broadcast threshold;
- escalation threshold;
- response latency target;
- acknowledgement discipline;
- clarification tendency;
- evidence attachment policy;
- deference;
- assertiveness;
- challenge propensity;
- disagreement persistence;
- compression/batching;
- direct vs manager-mediated communication;
- pub/sub interests;
- hop limits/TTL;
- routing by role/capability/evidence need.

### Authority / governance
- permissions;
- delegation;
- approval scope;
- spend/tool limits;
- environment access;
- segregation of duties;
- human gate requirements;
- blast radius;
- constitutional rules;
- mutable vs immutable fields.

### Runtime
- budget;
- latency;
- turn cap;
- concurrency;
- timeout;
- retry cap;
- backoff;
- scheduling priority;
- resource class.

### Personality / behavior
Research whether human personality frameworks are useful or misleading for LLM agents.
Test whether useful dimensions are better expressed as operational parameters:
- sociability/communication initiation;
- assertiveness;
- caution;
- challenge tendency;
- exploration;
- risk tolerance;
- persistence;
- curiosity;
- precision;
- empathy/user sensitivity where relevant;
- autonomy preference.

Do not assume Big Five/MBTI/Belbin/etc. transfer. Find evidence.

---

## R2 — Relationship dynamics

Treat relationships as graph edges, not prose.

Research parameters such as:
- familiarity;
- collaboration history;
- observed success together;
- epistemic trust;
- execution trust;
- deference;
- authority;
- mentorship;
- rivalry/competition;
- challenge affinity;
- complementarity;
- redundancy;
- expertise overlap;
- context overlap;
- communication compatibility;
- handoff reliability;
- historical disagreement;
- disagreement resolution rate;
- responsiveness;
- load/capacity interaction;
- social/organizational distance.

Determine:
1. Which are causal candidates vs merely descriptive.
2. Which can be safely tuned.
3. Which should be learned from history.
4. How relationship effects can be separated from individual agent quality.
5. How to avoid spurious “team chemistry” conclusions.

---

## R3 — Communication science

Investigate:
- FIPA ACL / KQML;
- speech-act / performative-based protocols;
- actor model;
- event buses/pub-sub;
- blackboard/global-workspace systems;
- tuple spaces;
- gossip;
- stigmergy;
- Contract Net;
- incident-command communication;
- aviation crew-resource management;
- distributed-systems congestion control;
- telecom routing/QoS.

Compare topologies:
- direct pairwise;
- star;
- chain;
- tree;
- graph/mesh;
- hierarchical;
- capability routed;
- manager mediated;
- event-driven pub/sub;
- blackboard/global workspace;
- stigmergic;
- dynamic topology.

Explicitly investigate the **communication-reasoning gap**:
more messages may not produce better distributed reasoning.

Propose metrics:
- useful-message rate;
- message-to-action conversion;
- evidence propagation latency;
- duplicate information rate;
- missed-critical-message rate;
- clarification loops;
- coordination token cost;
- communication density;
- centrality/congestion;
- unresolved request age;
- contradiction-resolution latency.

---

## R4 — Simulation & hypertuning

Research methods for optimizing mixed discrete/continuous/categorical configuration spaces:

- random/grid search baselines;
- Bayesian optimization;
- TPE;
- Hyperband/ASHA;
- population-based training;
- evolutionary/genetic algorithms;
- MAP-Elites / quality-diversity;
- multi-objective optimization / Pareto search;
- bandits;
- surrogate/performance predictors;
- Monte Carlo Tree Search;
- differentiable/search-free methods where applicable;
- LLM-driven reflective optimization;
- automated agent/workflow search such as ADAS, AgentSquare, AFlow and GEPA.

The search object is broader than prompts.

Candidate genome:

```yaml
agent:
  model: ...
  reasoning: ...
  context: ...
  memory: ...
  tools: ...
  communication: ...
  authority: ...

relationships:
  topology: ...
  edge_parameters: ...

organization:
  roles: ...
  manager_ratio: ...
  planning: ...
  gates: ...
  knowledge_policy: ...

runtime:
  budgets: ...
  concurrency: ...
```

Answer:
- What should be tuned jointly?
- What should be tuned hierarchically?
- What parameters have strong interaction effects?
- How can we prune a huge search space?
- When should parameters be frozen?
- How should promotions/rollback work?
- How do we prevent overfitting to repeated mission replays?
- How do we maintain held-out mission families?
- How do we detect evaluation leakage?
- How do we use shadow traffic/counterfactual organizations?

---

## R5 — Monitoring / observability / telemetry

Design levels:
1. runtime/system;
2. agent;
3. relationship/interaction;
4. team;
5. army/organization;
6. mission;
7. longitudinal learning/evolution.

For each metric classify:
- raw event;
- aggregate;
- derived;
- diagnostic;
- optimization objective;
- guardrail only.

Research OpenTelemetry-style tracing and current agent observability conventions.

Critical requirement:
A metric should not automatically become an optimization target.

---

## R6 — Evaluation & benchmarking

Evaluate the **whole agentic system**, not only the model.

Research:
- private mission benchmark construction;
- real failure replay;
- RED→GREEN acceptance;
- team credit assignment;
- topology comparison;
- harness/context effects;
- cost-normalized evaluation;
- uncertainty/calibration;
- ablations;
- factorial designs;
- causal inference;
- statistical power/repeated stochastic runs.

Benchmark:
- single agent vs multi-agent;
- static vs dynamic teams;
- homogeneous vs heterogeneous agents;
- quiet vs loud communication;
- direct vs routed communication;
- no shared memory vs bounded workspace;
- hand-crafted vs optimized config;
- stable teams vs dynamically assembled teams.

Build a Pareto frontier across:
quality, reliability, cost, latency, human attention, communication overhead, knowledge reuse, safety/trust.

---

## R7 — Cross-domain transfer

Search deeply for transferable mechanisms from:

### Manufacturing
Toyota Production System, jidoka, Andon, takt time, line balancing, Kanban, constraint theory, statistical process control, digital twins.

### Biology/ecology
immune systems, nervous systems, endocrine signaling, swarm intelligence, quorum sensing, mycelial/resource networks, ecological niches, evolutionary selection.

### Sports
team formations, role specialization, substitutions, matchups, coaching, playbooks, chemistry, scouting, opponent adaptation.

### Aviation / mission control
preflight, crew-resource management, flight checklists, telemetry, escalation, incident response, fail-safe states.

### Distributed computing / telecom
actors, supervision trees, control loops, consensus, gossip, routing, congestion control, QoS, backpressure.

### Organizations / economics
mechanism design, markets, team science, organizational psychology, polycentric governance, Viable System Model.

### Software/configuration
Kubernetes CRDs/controllers, Nix/Guix-style declarative configuration, policy-as-code, type systems, schema evolution, package/model registries, lockfiles.

For every borrowed mechanism:
- original problem;
- mechanism;
- evidence;
- what transfers;
- what does not;
- likely failure mode in LLM agents;
- smallest Agent Factory experiment.

---

# PRIOR-ART / NOVELTY ATTACK

For concepts such as Agent KG Mesh, Agent Genome, Agent Communication Protocol, Mission Readiness, skill-up, organizational evolution:

1. Search exact terms.
2. Search synonyms.
3. Search pre-LLM multi-agent systems.
4. Search organizational science and distributed systems.
5. Search current LLM-agent research.
6. Search open-source implementations.
7. Classify each concept:

A. known and directly implemented  
B. known but not applied in this way  
C. new combination of known mechanisms  
D. potentially novel mechanism  
E. too vague to evaluate

Do not use “groundbreaking” language without evidence.

---

# AGENT KG MESH HYPOTHESIS

Do not assume a single graph.

Investigate a **multi-graph organizational substrate** containing at minimum:

- Mission Graph: tasks, dependencies, blockers, evidence, artifacts.
- Knowledge Graph: claims, evidence, provenance, contradictions, temporal validity.
- Capability Graph: agents, skills, models, tools, readiness, certifications.
- Communication Graph: messages, subscriptions, routing, acknowledgements, unresolved requests.
- Relationship Graph: trust, familiarity, complementarity, authority, team history.

Research whether these should be:
- one heterogeneous property graph;
- separate graph projections over common IDs;
- event-sourced views;
- relational + graph projections;
- temporal graph;
- hypergraph.

Required queries:
- Who currently knows evidence relevant to the critical-path blocker?
- Which agent is certified and currently ready to solve it?
- Which agent/team has historically worked best with the current owner?
- Which contradiction invalidates current mission assumptions?
- Where is communication congestion?
- Which capability gap is recurring across missions?

---

# REQUIRED OUTPUTS

Produce exactly these artifacts:

1. `executive_decision.md`
2. `current_design_gap_analysis.md`
3. `agent_genome_reference_model.yaml`
4. `agent_runtime_event_model.yaml`
5. `relationship_model.yaml`
6. `communication_protocol.md`
7. `communication_phenotypes.yaml`
8. `monitoring_metric_catalog.yaml`
9. `evaluation_framework.md`
10. `simulation_hypertuning_architecture.md`
11. `search_space_v1.yaml`
12. `benchmark_suite_v1.md`
13. `agent_kg_mesh_prior_art.md`
14. `cross_domain_transfer_matrix.md`
15. `framework_reuse_matrix.md`
16. `top_25_experiments.md`
17. `architecture_deltas.md`
18. `org_ir_deltas.yaml`
19. `implementation_roadmap.md`
20. `sources.jsonl`

---

# DECISION LABELS

Every recommendation must be assigned exactly one:

- **ADOPT**
- **ADAPT**
- **EXPERIMENT**
- **DEFER**
- **REJECT**

And include:
- evidence strength;
- expected leverage;
- implementation dependency;
- risk;
- measurable success criterion.

---

# EXPERIMENTAL DISCIPLINE

No architecture earns promotion because it sounds intelligent.

Required progression:

```text
hypothesis
→ frozen config
→ deterministic/replayable benchmark
→ repeated stochastic trials
→ held-out missions
→ ablation
→ shadow twin
→ canary
→ certification
→ production preset
```

Any automatically optimized configuration must be reproducible via:
- configuration hash;
- model version/profile;
- skill/tool versions;
- policy version;
- benchmark version;
- seed/temperature where available;
- context/retrieval snapshot;
- environment/runtime version.

---

# IMPORTANT SKEPTICAL QUESTIONS

Attack these assumptions:

- More configurable parameters necessarily produce a better agent.
- Human personality taxonomies transfer to LLMs.
- More communication improves teams.
- More agents outperform one capable agent.
- simulated performance transfers to production.
- historical teammate success implies causal compatibility.
- a single aggregate Agent Health Score is safe.
- automated agent design should directly alter production.
- the best configuration is stationary.
- benchmark scores represent business value.

---

# FINAL SYNTHESIS QUESTION

Answer this precisely:

> Given an Intent Contract and a mission class, how should Agent Factory determine the **smallest, safest, lowest-cost agent/team/organization configuration** that reaches a required quality and reliability threshold, while retaining enough diversity to adapt when the mission distribution changes?

Frame this as constrained multi-objective organizational optimization, and give an architecture that can be implemented incrementally from the current session-based Agent Factory UI.
