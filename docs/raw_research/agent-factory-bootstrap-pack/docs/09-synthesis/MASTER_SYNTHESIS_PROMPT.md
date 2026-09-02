# Master Synthesis Prompt — Consolidated Agent Factory / Agentic Organization Architecture

Use this only **after** the corpus-preparation pass has produced a stable commit SHA.

You are the lead research architect for the next generation of the existing Agent Factory.

Your evidence base is:

- the exact repository at the corpus commit in `AGENT_RESEARCH_HANDOFF.yaml`
- current code/tests/runtime evidence
- source-of-truth snapshot
- raw research corpus
- concept registry
- claims/evidence map
- decisions and contradictions
- implementation map and doc/code drift
- research gaps and completed experiments

## Objective

Design a consolidated north-star architecture and path forward that extracts the highest-value compatible concepts from the research while aggressively eliminating duplication, accidental complexity, unsupported novelty claims and architecture that does not improve measurable outcomes.

The existing Agent Factory should remain a production proving ground unless evidence strongly justifies replacement.

## Required process

### A. Reconstruct current state
Summarize what actually exists and what current capabilities should be protected.

### B. Build the concept graph
Cluster concepts into coherent families. Identify concepts that are duplicates, complements, mutually exclusive, layered or independently useful.

### C. Evidence-rank
For every high-impact concept report evidence quality, prior art, internal implementation evidence, expected value, uncertainty and what would falsify the idea.

### D. Generate multiple candidate architectures
Do not jump to one solution. Produce at least 3 materially different architectures, including one deliberately simpler architecture.

### E. Architecture tournament
Score candidates on:
- mission success / quality
- reliability
- human trust / auditability
- cost
- latency
- scalability
- developer/operator productivity
- safety / blast radius
- maintainability
- self-maintainability
- research extensibility
- migration difficulty
- reversibility
- business/client value

### F. Select the north star
Explain why it wins and explicitly list important concepts that are rejected, deferred or isolated as experiments.

### G. Define canonical ontology and boundaries
Specify entity hierarchy/topologies, missions, agents, teams, organizations, skills, tools, memory, events, health, evals, policies, versions and promotion states.

Do not assume the final organization model must be a simple Agent -> Team -> Army hierarchy. Support the topology justified by evidence.

### H. Define deterministic vs agentic boundaries
For each major subsystem state what must be deterministic/testable and what benefits from agentic reasoning.

### I. Define platform architecture
Cover organization compiler/Org-IR if justified, runtime orchestration, collective cognition, evaluation/simulation, evolution, self-maintenance, research compiler, mission control/ZEUS, observability, provenance, security and external repo federation.

### J. Migration map
For each existing major component classify:
- KEEP
- GENERALIZE
- WRAP
- MOVE
- REWRITE
- RETIRE
- EXPERIMENT

Include concrete repository paths and migration risk.

### K. Implementation DAG
Create phases with dependencies, parallel workstreams, milestone outputs, RED->GREEN success criteria, regression gates, rollback paths and human decision points.

### L. Self-hosting path
Define staged milestones by which Agent Factory can safely maintain increasing portions of itself.

## Deliverables

Produce a consolidated pack under `docs/next-gen/` containing at minimum:

1. `00_EXECUTIVE_DECISION.md`
2. `01_CURRENT_STATE.md`
3. `02_CONCEPT_SYNTHESIS.md`
4. `03_ARCHITECTURE_TOURNAMENT.md`
5. `04_NORTH_STAR_ARCHITECTURE.md`
6. `05_CANONICAL_ONTOLOGY.md`
7. `06_ORG_IR_AND_CONFIG.md` if justified
8. `07_COLLECTIVE_COGNITION.md`
9. `08_EVAL_HEALTH_SIMULATION.md`
10. `09_EVOLUTION_SELF_MAINTENANCE.md`
11. `10_ZEUS_AGENTIC_IDE.md`
12. `11_REPO_AND_SERVICE_ARCHITECTURE.md`
13. `12_MIGRATION_MAP.md`
14. `13_IMPLEMENTATION_DAG.yaml`
15. `14_EXPERIMENT_PROGRAM.md`
16. `15_RESEARCH_BACKLOG.md`
17. `16_DECISION_LOG.md`
18. `17_SELF_HOSTING_ROADMAP.md`

Every major recommendation should link back to evidence, source concepts and current code where applicable.
