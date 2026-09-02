# Preset Agents and Agent Teams

## Suggested first Agents

| Order | Agent | Purpose |
|---:|---|---|
| 1 | Factory Architect | Understand architecture and decompose Factory work |
| 2 | Agent Architect | Create/configure future Agents |
| 3 | Independent Verifier | Protect evaluation integrity |
| 4 | Research Scout | Supply technical and research knowledge |
| 5 | HyperMESH Cartographer | Maintain organizational knowledge |
| 6 | Implementation Engineer | Dedicated coding specialist |
| 7 | Test/Eval Engineer | Create adversarial evals and regression tests |
| 8 | Sentinel | Monitor Agents, Teams and missions |
| 9 | Curriculum Agent | Address capability weaknesses |
| 10 | Team Composer | Adaptive team formation |
| 11 | Optimization Scientist | Configuration experiments |
| 12 | Resource Scheduler | Budget/usage/capacity optimization |

## Example Agent presets

### Factory Architect

- title: Factory Systems Architect
- mission count: 0 initially
- mode: supervised -> bounded autonomous
- HyperMESH: broad project context
- strengths: decomposition, architecture, gap analysis
- cannot: self-certify, change evaluator, grant permissions
- training: architecture replay, repo familiarization, failure review

### Agent Architect

- title: Agent Systems Architect
- mode: propose/configure
- goal: produce candidate Agent Genomes
- inputs: role, mission family, required skills, budget, constraints
- output: versioned Agent config + evaluation plan

### Root Cause Specialist

- title: Triage Investigator
- mode: bounded autonomous
- HyperMESH: deep-root-cause
- style: high skepticism, high verification, hypothesis-driven
- focus: defect diagnosis

### Production Guardian

- risk: very low
- verification: very high
- permissions: restricted
- provenance: mandatory
- rollback awareness: high

### Research Scout

- novelty search: high
- source diversity: high
- production write: forbidden
- research output enters KCR pipeline

### Sentinel

- persistent observer
- reads permissioned telemetry
- detects: stalled teams, duplicate work, cost anomalies, repeated failure, knowledge islands
- not an unrestricted super-agent

### HyperMESH Cartographer

- entity normalization
- deduplication
- temporal supersession
- provenance
- knowledge usefulness
- index/retrieval evaluation

### Curriculum Agent

- reads skill gaps + future mission forecast
- produces dynamic training plans
- cannot silently change certified Agent versions

## Suggested first Teams

### Team 1 — Factory Development

```text
Architect
Implementer
Verifier
Tester
```

### Team 2 — Research & Design

```text
Research Scout
Systems Architect
Prior-Art Reviewer
Experiment Designer
```

### Team 3 — Reliability / Triage

```text
Sentinel
Triage Investigator
Implementation Engineer
Verifier
```

### Team 4 — Knowledge Intelligence

```text
HyperMESH Cartographer
Knowledge Curator
Retrieval Optimizer
Provenance Verifier
```

### Team 5 — Optimization Lab

```text
Experiment Designer
Configuration Optimizer
Failure Analyst
Counterfactual Optimizer
Meta-Optimizer
```
