# HyperMESH Architecture

## Working terminology

MESH = Mission-Enabled Shared Hyperknowledge.

Logical knowledge scopes:

| Scope | Name | Purpose |
|---|---|---|
| Agent | A-MESH | Agent working memory, evidence, hypotheses, mission history |
| Team | T-MESH | Team decisions, blockers, interfaces, shared state |
| Command | C-MESH | Coordination, escalation, cross-agent synthesis, capability map |
| Global | G-MESH | Reusable organizational knowledge, doctrine, certified patterns |
| Federation | HyperMESH | Policy-controlled network joining MESH scopes |

A Manager is still an Agent. It has an A-MESH plus role-based access to T-MESH/C-MESH.

## Recommended near-term topology

Do not start with one physical graph database per Agent.

Start with logical namespaces/partitions over a shared knowledge fabric:

```text
                    HyperMESH Gateway
                           |
                     Policy / Routing
                           |
       -------------------------------------------
       |                   |                     |
     G-MESH              T-MESH                A-MESH
       |                   |                     |
       ---------------- Knowledge Fabric ---------
                           |
              --------------------------------
              |              |               |
            Graph          Vector          Lexical
              |              |               |
              -------- Metadata/Time --------
```

Design interfaces so later deployment can become physically federated by tenant, Army, client or security domain.

## Access control

Use a combination of:

- RBAC: role-based
- ABAC: mission/team/client/repo/environment attributes
- ReBAC: relationships among Agent, Team, Mission, Repo, Knowledge
- purpose-bound access
- field/node/edge-level redaction

Prefer Knowledge Entitlements over simple can_read booleans.

Example entitlement:

```text
Agent A may:
- read summary
- read claims
- read anonymized evidence
- traverse dependency edges

Agent A may not:
- read raw transcript
- read secrets
- read client identifiers
- write Team B knowledge
- promote Team B knowledge
```

## Mission Knowledge View

An Agent should not directly "enter another team's graph".

Instead, the HyperMESH Gateway produces a permission-filtered temporary Mission Knowledge View.

Possible contents:

```text
Mission Context Graph
|- Ticket
|- Similar historical missions
|- Relevant knowledge
|- Relevant agents
|- Repository dependencies
|- Previous PRs
|- Warnings
|- Contradictions
|- Provenance
```

## Mission Context Compiler

```text
Raw Ticket
 -> Mission Normalizer
 -> Formal Mission Contract
 -> HyperMESH Query Planner
 -> Knowledge Entitlement
 -> Source Selection
 -> Retrieval Planner
 -> Conflict/Freshness/Evidence checks
 -> Context Compiler
 -> Mission Context Pack
 -> Agent
```

Mission contract fields can include:

- bug / feature / research
- repo
- language
- technologies
- components
- entities
- risk
- dates
- environment
- expected output
- success criteria
- uncertainty
- client/domain scope

## Knowledge Change Request (KCR)

Knowledge should be promoted, not immediately globally trusted.

```text
Agent execution
 -> A-MESH
 -> candidate learning
 -> KCR
 -> deduplicate
 -> provenance check
 -> confidence check
 -> contradiction check
 -> temporal validity
 -> permission/scope classification
 -> Agent-only / Team / Command / Global
 -> promotion
```

## Preserve history

Prefer temporal supersession:

```text
Fact X valid 2026-03-01 .. 2026-08-12
  SUPERSEDED_BY
Fact Y valid from 2026-08-12
```

Do not silently delete historical knowledge.

## Avoid the manager telephone game

Upper-level synthesis must retain links to lower-level evidence:

```text
Raw evidence ----------------------------+
Agent learning                            |
 -> Team abstraction --------------------|
 -> Command abstraction -----------------|
 -> Global abstraction ------------------|
                                         |
                         provenance <-----+
```

## Architecture options to research

- centralized shared graph
- namespaced shared graph
- hierarchical graphs
- federated graphs
- event-sourced knowledge fabric
- graph-of-graphs
- graph + vector dual store
- unified multi-index store
- local-first mesh
- temporary mission-projected mesh

Recommended P0:
namespaced shared graph + event-sourced knowledge objects + hybrid derived indexes + mission projections.

## Brain architecture presets

- Rapid Recall
- Deep Root Cause
- Code Intelligence
- Incident Brain
- Research Brain
- Historical Brain
- Audit Brain
- Federated Brain
- Exploration Brain
- Low-Cost Brain
