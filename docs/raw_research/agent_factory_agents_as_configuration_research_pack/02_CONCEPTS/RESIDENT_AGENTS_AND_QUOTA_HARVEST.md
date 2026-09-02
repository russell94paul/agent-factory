# Resident Agents + Quota Harvest Scheduler

## Resident / Embedded Agents

A resident agent is not created for a single mission and destroyed immediately.

It persists around an environment long enough to build useful familiarity.

Possible lifecycle classes:

- Ephemeral Agent
- Mission Agent
- Campaign Agent
- Resident Agent
- Institutional Agent

Potential resident scopes:
- repository;
- team;
- product;
- client;
- platform;
- data domain;
- infrastructure;
- knowledge graph.

Expected benefits:
- architectural familiarity;
- lower repeated context-loading cost;
- recognition of recurring failures;
- awareness of local conventions;
- drift detection;
- long-horizon maintenance knowledge.

Risks:
- stale beliefs;
- memory contamination;
- overfitting to local conventions;
- hidden state;
- configuration drift;
- authority creep.

Required controls:
- periodic re-evaluation;
- explicit memory provenance;
- refresh cycles;
- drift detection;
- reproducible checkpoints;
- bounded authority;
- retirement/replacement policy.

## Quota Harvest Scheduler

Original idea:
A triage/bug agent monitors how much model/tool usage remains before a usage window resets and opportunistically picks useful tasks so spare capacity is not wasted.

Recommended framing:

> **Maximize useful expected value from otherwise-expiring compute capacity.**

Do not optimize directly for consuming every token.

### Good candidate tasks
- regression evals;
- historical failure classification;
- stale documentation refresh;
- memory cleanup;
- duplicate knowledge detection;
- test generation;
- benchmark runs;
- low-risk tech debt;
- research scouting;
- backlog labeling;
- provenance audits.

### Default-excluded tasks
- unsupervised production deploys;
- irreversible migrations;
- high-blast-radius refactors;
- security-sensitive changes;
- tasks that cannot safely checkpoint.

### Candidate task score

Priority =
(Utility * Confidence * LearningValue * Interruptibility)
/
(ExpectedCost * Risk)

Then modify for:
- deadline;
- staleness;
- resource expiration;
- dependencies;
- estimated completion probability.

## Research questions

- How accurately can remaining usable capacity be estimated?
- How should uncertain task duration be modeled?
- How should partial work be checkpointed?
- Can low-value "busy work" emerge through Goodhart pressure?
- How do we prove the scheduler is generating incremental value rather than wasting compute?
