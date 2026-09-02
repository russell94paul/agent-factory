# Deep Research Prompt 01 — Agents-as-Configuration

You are conducting architecture research for **Agent Factory**, a platform intended to construct, operate, evaluate and evolve agents, agent teams and larger agent organizations.

## Primary question

What is the best architecture for representing agents and teams as **declarative, typed, versioned configuration**, while cleanly separating reusable configuration, runtime state, learned state, secrets, policy and deployment provenance?

Do not assume YAML is the answer. Evaluate it.

## Research objectives

Conduct a deep comparison of:

- YAML
- JSON
- TOML
- CUE
- HCL
- Dhall / Nickel / Jsonnet where relevant
- Pydantic or equivalent typed runtime models
- JSON Schema
- protobuf / typed IDLs where relevant
- Git-backed configuration
- relational registry storage
- document storage
- event sourcing
- policy engines such as OPA/Rego
- secrets managers
- lockfile patterns
- configuration compilers / intermediate representations

## Prior art to inspect

Research current agent frameworks and adjacent systems. Include, where relevant:

- declarative configuration in major agent frameworks;
- workflow/orchestration systems;
- Kubernetes / CRDs/operators;
- GitOps;
- Terraform and infrastructure-as-code;
- Nix/Guix concepts;
- ML experiment configuration;
- feature stores/model registries;
- game entity/component configuration;
- robotics;
- policy-as-code;
- plugin/capability registries.

For every prior-art system, distinguish:
- what it actually implements;
- what is transferable;
- what does not transfer;
- how mature/proven the idea is.

## Required architecture distinctions

Evaluate a model with these separate objects:

1. Preset
2. Runtime Instance
3. Runtime State
4. Learned Profile
5. Mission Overlay
6. Deployment Lockfile

Determine whether this is the right split.

## Configuration ontology

Develop an exhaustive but organized parameter taxonomy covering at minimum:

- identity;
- role;
- mission affinity;
- expertise;
- cognition;
- uncertainty behavior;
- risk behavior;
- communication;
- memory;
- collaboration;
- temporal behavior;
- resources/budgets;
- tools;
- authority/autonomy;
- learning/adaptation;
- security;
- evaluation;
- deployment;
- observability;
- provenance;
- lifecycle.

For every major parameter family specify:

- desired-state vs observed-state;
- static vs dynamic;
- inheritable vs non-inheritable;
- mission-overridable vs immutable;
- self-mutable vs policy-gated;
- evidence source;
- evaluation approach.

## Self-modification

Research safe self-modifying configuration.

Propose a field-level mutability model such as:

- IMMUTABLE
- OWNER_MUTABLE
- MANAGER_MUTABLE
- MISSION_MUTABLE
- AGENT_SELF_MUTABLE
- LEARNED_ONLY

Identify which categories should never be self-mutable.

## Composition

Research:
- inheritance;
- traits/mixins;
- composition;
- overlays;
- precedence;
- environment-specific overrides;
- conflict resolution;
- defaults;
- constraints;
- schema migrations;
- backwards compatibility.

Recommend a deterministic resolution algorithm.

## Reproducibility

Design an agent/team lockfile capable of reproducing a deployment.

Consider:
- preset version;
- prompt version/hash;
- model/provider;
- tool versions;
- skill versions;
- policy versions;
- memory snapshot references;
- retrieval policy;
- evaluation contract;
- environment;
- dependency graph;
- organization topology.

## UI implications

Explain how configuration should power:
- visual agent builder;
- preset browser;
- diff between versions;
- mission overlays;
- advanced/raw YAML editor;
- schema-generated forms;
- invalid-config warnings;
- deployment preview;
- provenance timeline.

## Security

Threat-model configuration itself:
- privilege escalation;
- unsafe tool addition;
- malicious prompt/config mutation;
- secret leakage;
- inherited unsafe defaults;
- schema bypass;
- unreviewed self-modification;
- poisoned learned profiles.

## Output format

Produce:

1. Executive conclusion
2. Recommended architecture
3. Storage decision matrix
4. Configuration language comparison table
5. Canonical object model
6. Exhaustive parameter taxonomy
7. Mutability policy
8. Composition/override semantics
9. Versioning and migration strategy
10. Lockfile specification
11. Security threat model
12. UI implications
13. Suggested Agent Config Schema v1
14. Suggested Team Config Schema v1
15. Open questions
16. Experiments
17. Prioritized implementation roadmap

Clearly label:
- established prior art;
- reasoned inference;
- speculative Agent Factory innovation.

Use primary sources and recent technical documentation wherever possible.
