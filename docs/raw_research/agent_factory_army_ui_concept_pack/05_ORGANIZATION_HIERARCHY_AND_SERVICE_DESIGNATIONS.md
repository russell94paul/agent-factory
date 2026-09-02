# Organizational Hierarchy & Service Designations

## Critical design decision

Do **not** hardcode a fixed hierarchy such as Army → Division → Squad → Agent.

Use recursive organizational nodes:

```text
organization_node
  id
  node_type
  display_name
  callsign
  parent_id -> organization_node.id
  commander_id
  config_version
```

This supports arbitrary depth.

## Example deep designation

```text
Army
└── Engineering Command
    └── Integration Corps
        └── Connector Division
            └── API Brigade
                └── Authentication Battalion
                    └── OAuth Company
                        └── Vendor Platoon
                            └── Incident Squad
                                └── RAVEN-17
```

## Example alternative hierarchy

```text
Research Command
└── Advanced Projects Command
    └── Black Site
        └── Experiment Program
            └── Research Cell
                └── Red Team
                    └── Agent
```

## Node capabilities

Every organizational node may own:

### Identity
- designation
- node type
- callsign
- insignia
- commander
- parent / children

### Mission
- commander's intent
- objectives
- operations
- campaign membership

### Capability
- agents
- skills
- tools
- models
- certifications

### Doctrine
- formations
- workflows
- escalation policy
- communication policy
- ROE

### Resources
- repositories
- environments
- memory scopes
- budget
- compute

### Performance
- success rate
- first-pass success
- recurring failure rate
- cost
- latency
- intervention rate
- quality

### Health
- readiness
- unresolved failures
- knowledge freshness
- configuration drift
- workload / capacity

## Semantic zoom

At strategic zoom show:

`Engineering Command`

At theatre zoom:

`Integration Corps / Connector Division`

At tactical zoom:

`Authentication Battalion / OAuth Company / Incident Squad / RAVEN-17`

The same organizational path is compressed according to information density.

## Configurable hierarchy preset example

See `schemas/service_designation.schema.yaml`.
