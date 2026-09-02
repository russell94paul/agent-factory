# Deep-research and build sequence

## Why several reports are required

One giant report would mix ontology, storage, metrics, psychology-inspired behavior, team science,
optimization and UI into one synthesis. Run focused waves, then one adversarial synthesis.

## Wave 0 — evidence and vocabulary lock

**Goal:** prevent new ideas from contradicting existing repo evidence.

Inputs:

- current repository and tests;
- existing Agent Army research pack and approved/current-state records;
- the missing document mentioned by the user;
- existing artifacts and switchboard design;
- any separate `agent-army-research` repository.

Outputs:

- evidence inventory;
- canonical glossary;
- duplicate/conflicting concepts;
- code-to-concept seam map;
- explicit `MEASURED / DERIVED / STATED / ASSUMED` labels.

Gate: no product concept advances if it cannot name a current seam, a new seam and its precondition.

## Wave 1 — configuration languages and storage

Research YAML + JSON Schema, CUE, Dhall/Nickel-style typed configuration, CRD/GitOps patterns,
policy-as-code, event sourcing, bitemporal capability stores and secret-reference patterns.

Answer:

- authoring versus canonical format;
- inheritance/overlay semantics;
- unknown-field and conflict behavior;
- identity hashing and lockfiles;
- migrations and backwards compatibility;
- semantic diffs and recertification;
- config registry and distribution;
- prompt-to-config safety.

Deliverable: storage ADR with a tested example compiler spike.

## Wave 2 — agent parameter ontology

Research current agent frameworks, operating-system process controls, aviation crew-resource
management, military mission command, incident command, manufacturing cells, sports team roles,
organizational psychology, human factors and adaptive user interfaces.

For every imported parameter require:

```text
source concept → agent translation → behavioral hypothesis → observable signal
→ evaluation → risk → default → allowable mutation scope
```

Deliverable: modular schema and parameter acceptance rubric.

## Wave 3 — metrics, credit and communication

Research team effectiveness, multi-agent credit assignment, communication information gain,
coordination overhead, Goodhart resistance, calibration, confidence intervals, sequential versus
parallel task fit, and missing-instrument semantics.

Deliverables:

- metric dictionary;
- event semantic conventions;
- team-health and struggle models;
- communication-effectiveness evaluation;
- leaderboard and title governance;
- minimum telemetry plan.

Gate: each activity metric has an outcome anchor and every score can be falsified.

## Wave 4 — capability matching and readiness uplift

Research constraint solvers, recommender systems, skill taxonomies, competency graphs,
multi-objective ranking, team formation, portfolio/knapsack selection, uncertainty-aware matching
and just-in-time training.

Deliverables:

- mission requirement schema;
- capability evidence schema;
- hard-filter + ranking baseline;
- readiness intervention catalog;
- expected-uplift model;
- recommend-only prototype and simulation set.

Gate: matcher must explain exclusions, missing requirements and confidence.

## Wave 5 — MESH and cognitive relationships

Research distributed knowledge systems, blackboard architectures, publish/subscribe, shared mental
models, transactive memory, retrieval policies, knowledge graphs, provenance, access control,
stigmergy and organizational learning.

Deliverables:

- MESH protocol definition;
- typed knowledge objects and packet schema;
- scan/publish/promotion triggers;
- cognitive bond and lineage policies;
- cross-tenant and cross-repo privacy model;
- retrieval/runtime cost experiment.

Gate: compare MESH against baseline retrieval on accuracy, latency, cost and leakage risk.

## Wave 6 — optimization and evolution

Research configuration-space optimization, Bayesian optimization, evolutionary search,
champion/challenger deployments, causal ablations, meta-learning, curriculum generation and
Goodhart/adversarial robustness.

Deliverables:

- bounded optimizer interface;
- parameter search-space declarations;
- sandbox and grader separation;
- Pareto frontier for quality/cost/latency/risk;
- stop and rollback policies;
- agent/formation/doctrine optimization hierarchy.

Gate: no optimizer until the target evaluation reliably fails and independent grading is enforced.

## Wave 7 — Agent World and product experience

Research configuration IDEs, lineage UIs, mission control, operational digital twins, simulation,
portfolio dashboards, explainable recommendation and progressive disclosure.

Deliverables:

- Config Studio IA;
- Agent Lineage/Family tab;
- Sentinel and readiness views;
- team metric dashboards;
- portfolio operations overview;
- permissioned configuration marketplace design.

Gate: UI must show canonical state and confidence, not invent health or activity.

## Final synthesis

Use an independent adversarial reviewer to produce:

- accepted concepts;
- rejected/deferred concepts;
- novelty/prior-art boundaries;
- security and operational risks;
- architecture deltas;
- ADR proposals;
- research-to-implementation handoffs;
- prioritized backlog with preconditions;
- a falsification plan for the whole Agents-as-Configuration thesis.

## Implementation phases

| Phase | Build | Exit criterion |
| --- | --- | --- |
| P0 | Config V2 schema, loader, compiler, lockfile, diff | Existing blueprints round-trip without identity drift |
| P1 | Metric/event dictionary and telemetry | Baseline run produces complete attributable signals |
| P2 | Capability registry and transparent matcher | Candidate ranking reproduces expert selection on pilot set |
| P3 | Readiness uplift recommend-only | At least one intervention predicts and measures real uplift |
| P4 | Adaptive communication experiment | Same-budget test shows outcome/cost improvement |
| P5 | MESH prototype | Beats baseline retrieval without unacceptable cost/leakage |
| P6 | Config Studio and lineage views | Operators can understand and safely approve config diffs |
| P7 | Bounded optimizer | Independent eval shows champion improvement and safe rollback |
| P8 | Sentinel and portfolio operations | Proven reliable product telemetry and action policies |

## Artifacts Claude needs before implementing

1. Repository tree and current branch/commit.
2. `README.md`, `BRAIN-DUMP.md` and current roadmap.
3. `factory/blueprint.py`, `presets.py`, `registry.py`, `metrics.py`, `readiness.py`, `events.py`,
   `handoff.py`, `context.py`, `control.py` and tests.
4. Current YAML blueprints and JSON schemas.
5. Agent Army research answers, synthesis, ADRs and implementation handoffs.
6. Switchboard/tracker UI source and screenshots.
7. Existing memory/wiki service contracts and sample knowledge objects.
8. Eval corpus manifest plus representative passing/failing examples.
9. Sanitized run events and outcome/cost metrics.
10. Current security, RBAC, tenant and secret-reference contracts.
11. The additional document mentioned in the request.
12. A manifest giving provenance, sensitivity and last-checked date for every artifact.

