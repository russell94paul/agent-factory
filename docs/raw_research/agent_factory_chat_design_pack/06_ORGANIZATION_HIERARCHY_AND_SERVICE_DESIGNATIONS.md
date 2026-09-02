# 06 — Organization Hierarchy & Service Designations

## Core decision

Service designation must be **configurable and arbitrarily nested**.

Do not store fixed columns:
`army_id, team_id, agent_id`.

Prefer:
`organization_node(id, parent_id, node_type, config_version, ...)`

## Example deep hierarchy

Army
└── Engineering Command
    └── Integration Corps
        └── Connector Division
            └── API Brigade
                └── Authentication Battalion
                    └── OAuth Company
                        └── Vendor Platoon
                            └── Incident Squad
                                └── Fireteam
                                    └── RAVEN-17

## Alternative hierarchy

Command
└── Task Force
    └── Research Cell
        └── Experiment Team
            └── Agent

The platform should support both.

## Service designation

A designation is a path through the organization graph/tree.

Example:
`Engineering Command / Integration Corps / Connector Division / Authentication Battalion / OAuth Company / Incident Squad / RAVEN-17`

## Semantic zoom

Do not render the full path everywhere.

Strategic view:
- Engineering Command

Operational:
- Connector Division / Authentication Battalion

Tactical:
- OAuth Company / Incident Squad

Agent:
- RAVEN-17

## Every node may own

### Identity
- name
- designation
- unit type
- callsign
- parent
- commander/manager
- config version

### Mission
- north star
- objectives
- active operations
- mission history

### Capabilities
- agents
- skills
- tools
- models
- certifications

### Doctrine
- workflow
- formations
- escalation
- communication policy
- autonomy policy

### Resources
- repos
- environments
- memory scopes
- budgets
- compute
- credentials references

### Performance
- mission success rate
- first-pass success
- recurring failure rate
- cost
- latency
- quality
- human intervention rate
- rework

### Health
- readiness
- unresolved blockers
- stale knowledge
- recurrence hotspots
- drift
- budget state

## Agent identity

Agents can have:
- technical role,
- service designation,
- callsign,
- experience rank,
- capability certifications,
- mission record,
- recurring-failure profile,
- current readiness.

Example:

RAVEN-17  
Role: Reconnaissance Agent  
Unit: Intelligence Command / API Recon Squad  
Callsign: Night Owl  
Specialties: API archaeology, root cause analysis, historical retrieval.

## Important separation

Real company authority must remain separate from gamified military rank.

Display:
- Real title: Head of Engineering
- World role: Engineering Command — Commanding Officer
- Experience rank: optional gamified progression

Never infer real managerial power from game rank.
