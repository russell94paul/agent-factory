# Implementation Roadmap — From Session UI to Configurable Agents

## Stage 0 — Keep the simple session UI
Do not wait for the full Army UI.

Add only:
- Agent Version selector.
- Mission ID.
- Config hash.
- Run/eval result.
- basic trace/events.
- replay button.

This turns existing sessions into experimental data.

## Stage 1 — AgentDefinition v0.1
Implement a deliberately smaller subset:
- identity;
- model profile;
- tools;
- context;
- budget;
- communication phenotype;
- evaluation link;
- config hash.

Add JSON Schema/Pydantic validation.

## Stage 2 — Agent Registry + Lockfile
Create:
- immutable AgentVersion;
- certification status;
- dependency pins;
- diff view;
- rollback.

## Stage 3 — Event/Telemetry substrate
Append-only runtime events.
Project:
- agent status;
- mission status;
- communication graph;
- cost;
- evals.

Do not store operational history as mutable YAML.

## Stage 4 — Benchmark Vault
Before serious tuning:
- 20–50 representative replayable missions;
- explicit green contracts;
- failure cases;
- held-out split;
- repeat stochastic trials.

## Stage 5 — Communication v0.1
Start with typed:
REQUEST, RESPONSE, EVIDENCE, BLOCKER, CONTRADICTION, HANDOFF, STATUS_DELTA, ESCALATION.

Add 3 phenotypes:
- quiet_specialist;
- concise_scout;
- loud_coordinator.

## Stage 6 — Relationship edges
Track observed pair history.
Do not automatically change routing yet.

## Stage 7 — Manual experiments
UI lets operator compare configurations side by side:
- A/B config;
- same mission replay;
- metrics and trace diff.

## Stage 8 — Automated tuning v0
Tune only 8–12 safe fields.
Use random/TPE first.
Save Pareto candidates.

## Stage 9 — TeamDefinition / TeamGenome
Compose:
- AgentVersions;
- relation policy;
- topology;
- workspace;
- manager;
- success contract.

## Stage 10 — Shadow Twin
Run candidate team configs in replay/shadow before promotion.

## Stage 11 — Capability-based staffing
Intent Contract → required capabilities → certified candidates → cheapest safe coverage.

## Stage 12 — Evolution Chamber
Only now expand to:
- topology search;
- quality-diversity;
- optimizer-suggested workflows;
- automated candidate generation.

## UI progression

```text
TODAY
Session list
   ↓
Agent selector + config inspector
   ↓
Config diff + replay
   ↓
Benchmark / experiment view
   ↓
Team composition view
   ↓
Communication graph
   ↓
Mission graph
   ↓
Simulation tournament / Pareto view
   ↓
Army / organizational command environment
```

The experimental substrate is more important than the final visual metaphor at the beginning.
