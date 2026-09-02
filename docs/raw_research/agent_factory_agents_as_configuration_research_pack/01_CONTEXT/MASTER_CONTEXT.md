# Master Context — Agent Factory / Agents-as-Configuration

## Product direction

Agent Factory is evolving from a task-specific multi-agent implementation system into a broader platform capable of constructing, operating, measuring, optimizing and evolving:

`Agent -> Agent Team -> Agent Army -> larger synthetic organizations`

The broader north star is an operating system / compiler for synthetic organizations. The existing Agent Factory remains the first production proving ground.

## Current architectural themes

Important existing or planned concepts include:

- declarative, versioned agent/team blueprints;
- organization compiler / Org-IR;
- mission briefs / intent contracts;
- agent effectiveness metrics;
- cost-per-agent / cost-per-accepted-outcome;
- human approval tokens / gates;
- task DAGs;
- memory and semantic knowledge services;
- shared knowledge / Collective Cognition / Agent KG Mesh;
- capability registry;
- evaluation service;
- simulation and evolution chamber;
- provenance;
- self-maintenance / autonomic repair;
- team factory;
- multiple organizational presets;
- mission control UI.

## New concept cluster

The current ideas should be treated as one connected design space:

1. Agents-as-Configuration
2. Agent Capability Profiles
3. Agent Health Vectors
4. Team Health Vectors
5. Mission Readiness
6. Mission-Agent Matching
7. Dynamic Team Formation
8. Pre-deployment Conditioning ("READY-UP")
9. Skill Capsules / temporary specialization
10. Agent Presets
11. Agent Phenotypes
12. Resident / Embedded long-running Agents
13. Configuration Evolution
14. Quota Harvest Scheduler
15. Team Communication Effectiveness
16. Config mutability / safety policies
17. Config provenance and lockfiles

## Original "last minute skill-up" idea

Before deployment there should be a pre-deployment action that compares the mission brief against the current agent/team state.

It should consider:

- deployment time available;
- current health/readiness scores;
- mission requirements;
- capability gaps;
- time/cost constraints;
- tool and knowledge freshness;
- context state;
- recent evaluation reliability.

The system then recommends interventions that maximize expected mission readiness within constraints.

Potential UI action:

**READY-UP**

Examples of interventions:

- load a skill capsule;
- retrieve recent relevant knowledge;
- refresh repository architecture;
- fetch similar incidents;
- warm tools/integrations;
- switch model or reasoning budget;
- increase verification depth;
- add a specialist or reviewer;
- change communication frequency;
- reduce autonomy;
- run a focused micro-eval.

The objective is not "maximize every health metric." It is:

> Find the cheapest/safest interventions that get mission readiness above the required threshold.

## Original team configuration ideas

The user's starting list included:

- Agent Team Type
- Communication / Sharing / Alerting Frequency
- Communication Effectiveness
- Feature Output / number of features
- Working Style
- Architecture
- Workflow
- Domain
- Hierarchy
- Manager
- North Star
- Repositories
- Technologies
- Agent Type / Army
- Mission Applicable Specialities / Skills
- examples: Python, AWS, Azure Cloud, SQL

This pack expands those into typed ontology candidates.

## Core research question

How far can configuration go before an agent becomes meaningfully differentiated in observable behavior, without degenerating into vague "personality prompting"?

Prefer configuration that has:

1. operational meaning;
2. an enforceable mechanism;
3. measurable output;
4. known side effects;
5. an evaluation method;
6. provenance;
7. bounded mutability.

## Key conceptual separation

### Desired state
Good candidate for Git-backed YAML/JSON/CUE/HCL-like configuration.

### Observed state
Good candidate for database / event store / time-series telemetry.

Do not store rapidly changing runtime telemetry in a static config file.

## Proposed object model

### Preset
Reusable versioned template.

### Instance
Concrete instantiated agent/team.

### Runtime State
Live state, availability, health, context, budget, tool state.

### Learned Profile
Empirical capability and reliability measurements by task/mission class.

### Mission Overlay
Temporary configuration changes applied for one mission.

### Lockfile
Exact resolved versions of prompts, models, tools, skills, policies, presets, memory snapshots where appropriate, and evaluation contracts needed to reproduce the deployment.

## Strong research hypothesis

The most interesting architecture may be:

`Agent Genome -> Mission/Environment Overlay -> Agent Phenotype -> Mission Fitness -> Selection/Evolution`

These terms are metaphors and must be translated into real software primitives and experiments.

## Safety principle

Agents must not be free to mutate every parameter.

Every configuration field should have an explicit mutability class, for example:

- IMMUTABLE
- OWNER_MUTABLE
- MANAGER_MUTABLE
- MISSION_MUTABLE
- AGENT_SELF_MUTABLE
- LEARNED_ONLY

Changes to high-risk fields should be policy-gated and provenance-recorded.
