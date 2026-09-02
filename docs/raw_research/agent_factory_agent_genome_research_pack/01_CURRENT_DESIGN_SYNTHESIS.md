# Current Design Synthesis — Agent Genome Focus

## What is already strong

The current design has already moved beyond “agent orchestration” toward an **organizational runtime**:
- mission state becomes typed and replayable rather than implicit session state;
- organizations are versioned candidates rather than hard-coded workflows;
- Collective Cognition is selective, provenance-aware organizational memory rather than transcript sharing;
- Shadow Twin/replay exists to compare alternatives before autonomous promotion;
- a Constitutional Type System can make unsafe/invalid organizations fail before runtime;
- bounded reconciliation makes self-maintenance safer than one unconstrained self-healing agent.

This is the correct substrate for Agent Genome research.

## The missing layer

The design is currently richer at the **organization level** than at the **agent definition level**.

Before large-scale evolutionary organization search, Agent Factory needs a precise definition of:

1. What an agent *is*.
2. Which parts are configurable.
3. Which parts are measured.
4. Which parts are learned/derived.
5. Which values can be mutated safely.
6. Which changes require recertification.
7. How capability claims are proven.
8. How relationship and communication behavior is represented.
9. How an agent is compared across mission classes.
10. How an agent configuration is reproduced exactly.

## Proposed four-layer model

### 1. Genotype
Mutable declarative configuration:
- model profile;
- reasoning/control strategy;
- context policy;
- memory policy;
- tool permissions;
- communication phenotype;
- initiative/escalation policy;
- planning parameters;
- critique/challenge tendency;
- collaboration style;
- budgets/timeouts;
- skill bindings;
- authority;
- safety constraints.

### 2. Phenotype
Observed mission behavior:
- actual message frequency;
- actual verbosity;
- initiative events;
- clarification count;
- information density;
- disagreement rate;
- tool strategy;
- planning depth;
- recovery behavior;
- delegation behavior;
- context usage;
- latency/cost.

### 3. Historical state
Append-only measurements:
- mission results;
- eval results;
- teammate outcomes;
- failure classes;
- domain experience;
- version history;
- certifications;
- calibration;
- drift;
- relationships.

### 4. Fitness/readiness
Derived, mission-conditioned metrics:
- capability fit;
- recent reliability;
- domain freshness;
- context readiness;
- tool/environment readiness;
- communication compatibility;
- team complementarity;
- risk/trust score;
- expected quality/cost/latency.

## Important correction to “track as many data points as possible”

Capture broad telemetry, but do not maximize the number of knobs.

Every field should be classified as:
- `TUNABLE`: candidate for simulation/search.
- `DECLARED`: fixed identity/contract.
- `MEASURED`: append-only observation.
- `DERIVED`: computed from evidence.
- `POLICY`: human/institution-governed; not automatically mutated.

This prevents a giant YAML from becoming an accidental source of truth for history and telemetry.

## Highest-leverage architectural addition

Add an **Agent Registry + Agent Lockfile** analogous to a model/package registry:

```text
AgentDefinition + Skills + Model Profile + Tool Set + Policy + Eval Suite
                              ↓
                        AgentVersion
                              ↓
                         Certification
                              ↓
                         AgentLockfile
```

A mission run should record the exact config hash and dependency versions.

## Relationship dynamics should be first-class

Do not hide team chemistry in prompts. Create versioned relationship edges:
- familiarity;
- trust;
- epistemic trust;
- reliability trust;
- complementarity;
- redundancy;
- deference;
- challenge propensity;
- communication affinity;
- historical success together;
- conflict rate;
- response latency;
- knowledge overlap;
- shared context overlap.

Then compare:
- individually elite agents vs compatible teams;
- homogeneous vs heterogeneous communication styles;
- manager-agent fit;
- challenger-builder pairings;
- stable teams vs dynamically assembled teams.

## “Quiet / loud / mumbler”

Keep these as UI-friendly labels, but compile them into measurable parameters.

Example:
- **Quiet**: low unsolicited-message probability, high novelty threshold, high batching, event-driven updates.
- **Loud**: high initiative, high broadcast tendency, low escalation threshold, frequent status deltas.
- **Mumbler**: low semantic density, high ambiguity, weak commitments; this is more useful as a detected anti-pattern than a desirable preset.
- **Concise Scout**: high novelty detection, short evidence-rich messages.
- **Challenger**: high contradiction/challenge probability, low deference, high evidence requirement.
- **Coordinator**: high routing/broadcast selectivity, moderate initiative, high acknowledgement discipline.

The simulation system should discover which phenotype fits which mission/topology rather than assuming one personality is universally best.
