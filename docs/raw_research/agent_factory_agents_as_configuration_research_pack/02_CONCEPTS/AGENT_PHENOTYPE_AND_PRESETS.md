# Agent Phenotype + Preset Library

## Goal

Create behaviorally differentiated agent presets using measurable configuration, not merely decorative personality language.

## Nature-inspired model

### Agent Genome
Stable declarative configuration.

### Mission / Environment
Task and operating context.

### Epigenetic / Mission Overlay
Temporary mission-specific configuration.

### Agent Phenotype
Observed runtime behavior.

### Fitness
Measured mission outcomes.

### Evolution
Promotion of configurations that perform better under controlled evaluation.

The biological terminology is a metaphor. Research must determine which parts map usefully to software and which do not.

## Parameter families

### Identity
- role;
- archetype;
- lineage;
- tags;
- specialization.

### Cognition
- planning depth;
- decomposition depth;
- reasoning budget;
- abstraction preference;
- breadth vs depth;
- exploration rate;
- exploitation rate;
- hypothesis count;
- alternative generation;
- counterfactual reasoning;
- causal reasoning;
- systems thinking;
- analogical reasoning;
- first-principles preference;
- pattern-match preference.

### Uncertainty
- confidence threshold;
- clarification threshold;
- verification threshold;
- evidence requirement;
- source diversity requirement;
- disagreement trigger;
- escalation threshold;
- assumption tolerance;
- ambiguity tolerance.

### Risk
- risk tolerance;
- change aversion;
- blast-radius tolerance;
- reversibility preference;
- experimentation tolerance;
- production-change tolerance;
- rollback sensitivity.

### Behavioral tendencies
- assertiveness;
- cooperativeness;
- persistence;
- patience;
- adaptability;
- conscientiousness;
- skepticism;
- curiosity;
- novelty seeking;
- independence;
- initiative;
- competitiveness;
- teaching orientation.

These should be translated into operational rules wherever possible.

Example:

Instead of:

`conscientiousness: high`

prefer a compiled behavior such as:

- pre-work requirement check required;
- max unresolved assumptions = 2;
- post-change validation required;
- self-review passes = 2.

### Communication
- verbosity;
- cadence;
- proactive alerting;
- disagreement style;
- evidence density;
- handoff detail;
- uncertainty disclosure.

### Memory
- retrieval depth;
- retrieval breadth;
- recency weighting;
- novelty weighting;
- failure memory weighting;
- cross-team memory scope;
- contradiction policy;
- forgetting policy.

### Social/team behavior
- delegation preference;
- collaboration preference;
- consultation threshold;
- leadership/followership preference;
- peer review frequency;
- consensus requirement;
- duplicate-work tolerance.

### Temporal
- mission horizon;
- urgency bias;
- deadline sensitivity;
- interruptibility;
- persistence;
- refresh frequency;
- checkpoint frequency.

### Resources
- token budget;
- cost budget;
- tool-call budget;
- context budget;
- parallelism;
- reserve fraction.

### Authority
- spawn agent;
- delegate;
- modify configuration;
- commit;
- open PR;
- merge;
- deploy;
- rollback;
- contact human.

## Initial preset candidates

### Scout
High breadth, exploration, novelty and information gathering.

### Surgeon
Small precise changes, low blast radius, high verification.

### Architect
Systems thinking, abstraction, dependency awareness.

### Historian
Heavy historical memory and prior-case retrieval.

### Skeptic
Actively searches for assumptions, counterexamples and contradictions.

### Firefighter
High urgency, incident triage, prioritization and fast synthesis.

### Auditor
Evidence-heavy, low assumption tolerance, traceability first.

### Integrator
Cross-domain synthesis and interface compatibility.

### Maintainer
Long-lived system familiarity, drift detection, safe maintenance.

### Mentor
Knowledge transfer and explainability.

### Optimizer
Repeated controlled experiments against explicit KPIs.

### Diplomat
Conflict resolution and shared-state convergence.

### Investigator
Hypothesis generation, evidence collection and elimination.

### Guardian
Security/compliance/risk-first behavior.

### Builder
Implementation throughput with bounded verification.

## Research requirement

For every preset:

1. define configuration deltas;
2. define intended mission classes;
3. define measurable expected advantage;
4. define failure modes;
5. design A/B or tournament evals;
6. establish whether the preset adds value beyond prompt wording.
