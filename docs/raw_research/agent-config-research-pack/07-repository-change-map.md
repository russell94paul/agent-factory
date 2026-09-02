# Repository Change Map

This maps the proposed system onto existing Agent Factory seams. It is a design map, not a
recommendation to bypass the repository's existing evidence gates.

| Proposed capability | Existing seam | Recommended change | Improvement type | First proof required |
|---|---|---|---|---|
| Layered AgentConfig | `factory/blueprint.py` `AgentSpec` / `TeamSpec` | Add a compiler in `factory/config/`; compile into current specs before changing execution code | New Functionality, Architecture | Existing blueprint tests remain green; equivalent config has stable hash |
| Preset registry | `factory/presets.py` | Add versioned overlay rules and provenance; keep tickets, caps, reasons and prohibitions | New Functionality, Security | Every applied field shows source and precedence |
| Config identity | blueprint hashing | Hash canonical resolved JSON, not raw YAML; include every behavior-changing field | Security, Reliability | Same semantics produce same hash; changed authority changes hash |
| Config validation | bootstrap schemas | Replace unconstrained route/packet/gate objects; reject unknown fields where contracts are stable | Security, Developer Experience | Negative fixtures fail for typoed and extra fields |
| Mission matcher | capability and mission records | Rank certified configurations against a mission requirement graph | New Functionality, Performance | Historical replay beats a simple role/tag filter |
| Readiness uplift | `factory/readiness.py` | Add recommendation and post-action measurement; never directly write health | New Functionality, UI/UX, Reliability | Intervention predicts and measures a real gate improvement |
| Communication effectiveness | `docs/agent-communication.md`, metrics registry | Emit delivery, correct-consumption, contradiction and noise events | DB, Observability, Performance | Metric correlates with fewer handoff defects |
| MESH | durable record/live channel split | Add permissioned mission packets, provenance and promotion gates | New Functionality, DB, Security | Knowledge packet improves task outcome without leakage |
| Sentinel Observer | sessions/task events/findings | Read-only event consumer with alert dedupe, cooldown and draft tickets | Observability, Security, New Functionality | Synthetic incidents: acceptable recall and false-alert rate |
| Capability lineage | capability records and presets | Add lineage edges, generation and evidence inheritance rules; do not inherit scores blindly | DB, New Functionality, UI/UX | Derived configuration remains traceable and independently certifiable |
| Cognitive bonds | communication routes/context packets | Typed, reciprocal context-sharing contract with explicit permissions and wake triggers | New Functionality, Security | Handoff quality improves enough to cover added coordination cost |
| Surplus Capacity Queue | budgets, registry, verifier | Dispatch only safe, checkpointable, positive-value work; rank retained value, not token burn | Cost, Performance, New Functionality | More accepted output per allocation with no regression increase |
| Operations overview | sessions, findings, gates, metrics | Materialized read model for missions, teams, incidents and evidence freshness | UI/UX, DB, Observability | Operators find a struggling team and reason in under 30 seconds |
| Portfolio autopilot | future product/revenue sources | Keep behind explicit approval; produce proposals and tickets before autonomous changes | Business Intelligence, New Functionality, Security | Retrospective precision is high enough to justify engineering load |
| Config optimizer | config hash + outcome evidence | Propose bounded diffs, run controlled evaluations and preserve control configurations | R&D, Performance, Security | Repeated uplift across held-out missions, not one lucky run |

## Suggested modules

```text
factory/config/
  loader.py          # YAML/JSON input and URI resolution
  schema.py          # version dispatch and validation
  overlay.py         # deterministic layer precedence
  compiler.py        # canonical resolved representation
  identity.py        # stable serialization and hashing
  policy.py          # authority and safety caps
  provenance.py      # field-level source map
  migrations.py      # explicit schema-version upgrades
```

The compiler should target the existing `AgentSpec` and `TeamSpec` first. That creates a migration
path without forcing the runner, evaluation harness and factory registry to understand every new
authoring concept at once.

## Database additions

| Store | Minimal records | Why it is not YAML |
|---|---|---|
| Event store | run events, messages, alerts, interventions, state transitions | High-volume and time ordered |
| Capability ledger | subject, task family, conditions, evidence, confidence, validity | Queryable evidence history and decay |
| Configuration registry | source version, resolved lockfile, hash, certification | Immutable identity and audit |
| Knowledge catalog | typed object, provenance, permissions, expiry, embeddings/index refs | Large payloads and access control |
| Operational read model | current mission/team state and aggregates | Fast dashboards without replaying all events |
| Portfolio ledger | product, revenue/cost observations, audit findings, decisions | Business history and explicit provenance |

## UI tabs

| Tab | Primary job | Cutting-edge feature that earns its complexity |
|---|---|---|
| Switchboard | Run and communicate | Command palette, live event timeline, typed handoff composer, evidence preview |
| Configuration Studio | Build agents/teams | Prompt-to-config draft, layered diff, provenance inspector, mission-fit simulator |
| Deployment Room | Decide readiness | Health component radar, failed-gate explanation, intervention simulator, deploy/narrow/substitute/delay decision |
| Lineage | Inspect specialization | Capability growth timeline, generation graph, bond permissions and measured collaboration effect |
| Operations | Detect problems | Struggle map, deadlines, severity feed, evidence freshness, intervention history |
| Portfolio | Connect work to value | Product health, revenue/cost evidence, underperformance audit queue and approved remediation tickets |

## What not to build first

- Military ranks as permissions. Use an explicit authority matrix; rank can remain a display preset.
- A leaderboard based on token volume, features created or messages sent.
- Free-form sharing of entire second brains.
- Direct self-modification of production configurations.
- A world-scale Sentinel before event contracts, false-positive budgets and a kill switch exist.
- Decorative social simulation without measurable operational value.

