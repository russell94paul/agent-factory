# Agent Factory — Agents-as-Configuration Research Pack

## Purpose

This pack converts a set of connected Agent Factory ideas into a structured research and design program for Claude.

The central hypothesis is:

> **Agents-as-Configuration + Capability + Health + Mission Readiness + Dynamic Conditioning + Mission Matching + Outcome Learning** can become a foundational control plane for Agent Factory.

The goal is not merely to create YAML files for prompts. The goal is to determine how Agent Factory can represent, instantiate, measure, condition, match, evaluate, evolve, reproduce and govern agents and agent teams as versioned software-defined entities.

## Recommended ingestion order

1. `01_CONTEXT/MASTER_CONTEXT.md`
2. `02_CONCEPTS/AGENTS_AS_CONFIGURATION_CONCEPT.md`
3. `02_CONCEPTS/MISSION_READINESS_AND_READY_UP.md`
4. `02_CONCEPTS/TEAM_METRICS_AND_HEALTH.md`
5. `02_CONCEPTS/AGENT_PHENOTYPE_AND_PRESETS.md`
6. `02_CONCEPTS/RESIDENT_AGENTS_AND_QUOTA_HARVEST.md`
7. `03_SCHEMAS/agent_config_example.yaml`
8. `03_SCHEMAS/team_config_example.yaml`
9. `04_RESEARCH_PROMPTS/`
10. `05_CLAUDE_BOOT/CLAUDE_MASTER_BOOT_PROMPT.md`

## Research order

Run the deep-research prompts in this order:

1. **Agents-as-Configuration**
2. **Agent Health + Mission Readiness**
3. **Agent Phenotypes / Human & Nature Inspired Configuration**
4. **Mission Matching + Dynamic Team Formation**
5. **Cross-Research Synthesis**

The first two are architecture-critical. The third is exploratory but potentially differentiating. The fourth operationalizes the first three. The synthesis prompt reconciles everything against Agent Factory.

## Important design principle

Keep these objects separate:

1. **Preset** — what the agent is designed to be.
2. **Instance** — a concrete instantiated agent.
3. **Runtime State** — the agent's current operational condition.
4. **Learned Profile** — evidence of what it has actually proven good at.
5. **Mission Overlay** — temporary mission-specific behavioral/configuration changes.

Also distinguish:

- **Capability** — can the agent do the work?
- **Health** — is the agent/system currently functioning well?
- **Mission Readiness** — is this agent, now, prepared for this particular mission?
- **Fitness** — how well did it actually perform on this class of mission?

## Desired research behavior

Do not merely collect prior art. For every relevant external concept:

`source concept -> transferable mechanism -> Agent Factory primitive -> measurable benefit -> risk -> experiment`

Prefer mechanisms that can be represented as typed, versioned, measurable configuration rather than vague prompt adjectives.

## Final target artifacts

Claude should ultimately help produce:

- Agent Configuration Specification v1
- Agent/Team Configuration Ontology v1
- Agent Health Vector v1
- Team Health Vector v1
- Mission Readiness Model v1
- Mission Matcher design
- READY-UP / Mission Conditioning design
- Agent Preset Library v1
- Agent Phenotype experimental ontology
- Configuration storage/versioning architecture
- Configuration security/mutability policy
- Agent Configuration Registry design
- Agent/Team lockfile design
- Evaluation and experiment plan
- Implementation priority map
