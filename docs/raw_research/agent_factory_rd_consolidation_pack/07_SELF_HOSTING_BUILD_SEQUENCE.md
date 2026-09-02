# Agent Factory Self-Hosting Build Sequence

## Goal

Do not wait for the complete Factory before using the Factory.

Reach a minimum self-hosting kernel.

## AF-SH0 — Agent Factory Self-Hosting Point

Requirements:

- Agent configuration works
- Mission representation exists
- bounded execution works
- evaluations work
- evidence persists
- Factory Architect exists
- Factory Architect can inspect repo and canonical design
- Factory Architect can propose new Agent configs
- humans approve early Agent creation
- independent verification exists
- Agents can work against Factory tickets

After AF-SH0:

```text
Before: humans build Agent Factory
After:  humans + Agent Factory build Agent Factory
```

## Phases

### Phase 0 — Research consolidation

Produce:

- canonical architecture
- glossary
- research backlog
- accepted/rejected concepts
- implementation DAG

### Phase 1 — Measurement substrate

Preserve/harden:

- Mission/Green contracts
- Evidence
- Evaluator
- Corpus
- Certification
- event records
- cost/latency
- artifacts
- failure classifications

Gate:

> Can we prove whether one Agent succeeded?

### Phase 2 — Agent Genome v1

Build:

- AgentSchema
- AgentConfig
- AgentVersion
- AgentLock
- AgentRegistry
- CapabilityProfile
- Permissions
- Tools
- Model
- Prompt
- Budget
- Knowledge profile
- Evaluation profile

Start with ~30-50 meaningful execution-affecting fields.

### Phase 3 — Mission Model

Build:

- Mission
- MissionContract
- MissionRequirements
- MissionState
- MissionEvidence
- MissionOutcome
- MissionArtifacts
- MissionEvents

Normalize tickets into missions.

### Phase 4 — Agent telemetry

Collect:

- mission count
- verdict
- time-to-green
- cost
- turns
- tool usage
- failures
- rework
- human intervention
- knowledge retrieval
- context usage
- config version

### Phase 5 — Factory Architect v0

Responsibilities:

- read canonical architecture
- inspect repo
- map architecture component -> implementation state
- propose next ticket
- identify needed specialist
- propose Agent config
- implement bounded work where appropriate
- run tests/evidence
- never redefine evaluator

Initial authority:

```yaml
mode: supervised
production_write: bounded
team_creation: propose_only
agent_creation: propose_only
deployment: human_gate
```

### Phase 6 — HyperMESH v0

Start with:

- A-MESH
- Project T-MESH
- hybrid retrieval
- provenance
- Mission Context Pack

Evaluate with/without HyperMESH.

### Phase 7 — Skills and capability

Build:

- Skill Registry
- Skill Evidence
- Skill Readiness
- Mission Capability Requirements
- Agent-to-Skill matching

### Phase 8 — Agent Architect

Agent #2.

Creates/reuses candidate Agent configs and evaluates them.

### Phase 9 — Independent Verifier

Agent #3.

Protects evaluation integrity.

### Phase 10 — Research Scout

Agent #4.

Produces research candidates, never direct production truth.

### Phase 11 — HyperMESH Cartographer

Agent #5.

Maintains entities, provenance, staleness and indexing.

### Phase 12 — Factory Development Team v1

Combine Architect + Implementer + Verifier + Research Scout.

This is the point where the Factory actively helps build the rest of itself.

### Later

- Team Composer
- Simulation
- Optimization Lab
- Curriculum Optimizer
- Sentinel
- Agent Army
- progressive autonomy

## Self-hosting progression

```text
AF-SH0 Factory Architect works on Factory
AF-SH1 Factory generates Agents
AF-SH2 Factory forms Teams
AF-SH3 Factory optimizes Teams
AF-SH4 Factory maintains itself
AF-SH5 Factory operates bounded autonomous projects
```
