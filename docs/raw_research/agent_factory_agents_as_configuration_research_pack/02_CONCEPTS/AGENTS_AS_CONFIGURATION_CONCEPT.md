# Agents-as-Configuration

## Thesis

Agent Factory should treat agents and agent teams as versioned, declarative software-defined entities rather than collections of prompts assembled ad hoc at runtime.

YAML may be the human authoring surface, but YAML should not be confused with the underlying architecture.

## Recommended conceptual pipeline

```text
Human authoring
    |
*.agent.yaml / *.team.yaml / *.army.yaml
    |
schema validation
    |
canonical Agent-IR / Org-IR
    |
versioned registry
    |
compiler/resolver
    |
runtime instance
    |
observations + outcomes
    |
learned profile / evolution
```

## Candidate storage responsibilities

### YAML
Good for:
- human-readable presets;
- environment overlays;
- mission overlays;
- team composition;
- policies/references;
- Git review/diffs.

Avoid:
- secrets;
- high-frequency telemetry;
- ephemeral runtime metrics;
- huge learned histories.

### JSON / canonical IR
Good for:
- normalized resolved representation;
- API transport;
- compiler output;
- interoperability;
- deterministic hashing.

### Typed models
Use schema/runtime validation such as Pydantic or equivalent.

### JSON Schema
Use for:
- external validation;
- UI form generation;
- language-independent contracts.

### CUE / constraint-oriented languages
Research whether a constraint-oriented language provides meaningful advantages for:
- inheritance;
- composition;
- constraints;
- environment overlays;
- validation;
- partial configuration;
- default resolution.

### Git
Use for:
- version history;
- code review;
- provenance;
- branch/promotion;
- diffs.

### Relational database
Use for:
- instances;
- mission assignments;
- current registry;
- learned capability profiles;
- relationships;
- indexing/search.

### Time-series/event store
Use for:
- health;
- task metrics;
- runtime observations;
- readiness history;
- config mutation events.

### Secret manager
Credentials must never live directly in reusable configuration.

### Policy engine
Research OPA/Rego or alternatives for:
- who can mutate what;
- environment restrictions;
- production authority;
- tool policies;
- data access;
- self-modification.

## Five separate objects

1. **Preset**
2. **Instance**
3. **Runtime State**
4. **Learned Profile**
5. **Mission Overlay**

A sixth object is recommended:

6. **Resolved Deployment Lockfile**

## Configuration ontology families

- identity;
- mission orientation;
- expertise;
- cognition;
- uncertainty;
- risk;
- behavioral tendencies;
- communication;
- memory;
- team/social behavior;
- temporal behavior;
- resources;
- tools;
- authority/autonomy;
- learning/adaptation;
- security;
- evaluation;
- deployment;
- observability;
- provenance;
- lifecycle.

## Design requirement

Every parameter should ideally specify:

- type;
- range/enum;
- default;
- semantic meaning;
- mutability class;
- owner;
- validation constraints;
- whether inherited;
- whether overridden by mission;
- whether learned;
- telemetry/evidence source;
- evaluation method;
- security sensitivity;
- compatibility/versioning behavior.
