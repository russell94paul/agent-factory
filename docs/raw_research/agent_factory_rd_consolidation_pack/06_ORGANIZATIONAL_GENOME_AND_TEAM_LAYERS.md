# Organizational Genome and Team Layers

## Organizational Genome

Agent Genome describes one Agent.

Organizational Genome describes:

- Agents
- roles
- teams
- topology
- communication
- knowledge architecture
- management
- routing
- resources
- training
- evaluation

Long-term loop:

```text
Mission
 -> Organizational requirements
 -> Organizational Genome
 -> variation
 -> simulation
 -> selection
 -> certification
 -> deployment
 -> evidence
 -> next generation
```

## Project-specific organization

A huge project can be compiled into a temporary organization.

Inputs:

- architecture docs
- research reports
- implementation specs
- tickets
- repo graph
- historical failures
- team performance
- delivery dates
- budgets
- dependencies

Project Intelligence Compilation:

```text
Docs + Tickets + Repos + History
 -> Project Knowledge Graph
 -> Project Mission Graph
 -> capability requirements
 -> workstreams
 -> dependencies
 -> uncertainty
 -> risk
 -> critical path
 -> organizational requirements
```

The optimizer can then ask:

> What organization should exist to execute this project?

## Team Layer

A Team Layer is a capability namespace/routing pool, not necessarily another command hierarchy.

Example:

```text
DATA PLATFORM LAYER
|- Pipeline Monitoring Team
|- Pipeline Triage Team
|- Pipeline Implementation Team
|- Data Quality Team
|- Schema Migration Team
|- Database Performance Team
|- Snowflake Team
|- Power BI Semantic Model Team
|- Dashboard Reliability Team
|- Infrastructure Team
```

Other layers:

- Product Engineering
- Security
- Research
- Factory Self-Maintenance
- Client Delivery
- Knowledge Intelligence

## Team Blueprint Registry

Potential presets:

- rapid-triage
- deep-root-cause
- pipeline-repair
- data-anomaly
- schema-migration
- powerbi-semantic-model
- ui-feature
- security-audit
- research
- reliability
- performance
- incident-response

Do not instantiate every blueprint.

Mission routing should search/reuse an existing team where possible, otherwise compose and evaluate a candidate team.
