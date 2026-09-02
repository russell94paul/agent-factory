# Agent Factory — Agent Genome, Communication & Simulation Research Pack

**Purpose:** Turn the current Agent Factory direction into an implementation-ready research program focused on **Agents-as-Config**, agent/team relationship dynamics, communication protocols, monitoring, benchmarking, simulation, and automated configuration optimization.

This pack assumes the current platform direction already includes:
- Agent → Agent Team → Agent Army as the simple operator-facing hierarchy.
- Agent Factory / Organizational Compiler / Org-IR.
- Mission Hypergraph / Mesh.
- Collective Cognition / Global Workspace.
- Constitutional / policy type checking.
- Shadow Twin / replay / counterfactual evaluation.
- Evaluation, observability, capability registry, simulation, and an Evolution Chamber.
- Bounded self-maintenance and certified versioning.

## Core recommendation

Treat an agent configuration as a **versioned executable capability contract**, not a prompt persona.

Split the agent model into four layers:

1. **Genotype** — parameters you are allowed to configure/tune.
2. **Phenotype** — behavior observed during a mission.
3. **History / State** — immutable measurements and experience records.
4. **Fitness / Readiness** — derived scores used for routing, certification, and optimization.

Do **not** put every measured value back into the YAML as mutable config. Store telemetry/history as append-only events and derive snapshots.

## Pack map

- `01_CURRENT_DESIGN_SYNTHESIS.md` — grounded design review and gaps.
- `02_DEEP_RESEARCH_BOOT_PROMPT.md` — master prompt for a Deep Research run.
- `03_RESEARCH_PROGRAM.md` — linked research tracks and deliverables.
- `schemas/agent_genome.schema.yaml` — extensive proposed agent configuration model.
- `schemas/agent_runtime_event.schema.yaml` — event model for phenotype/history.
- `schemas/relationship_edge.schema.yaml` — relationship dynamics model.
- `presets/communication_phenotypes.yaml` — measurable versions of quiet/loud/etc.
- `presets/high_leverage_agents.yaml` — reusable agent presets.
- `simulation/hypertuning_spec.md` — simulation and optimization design.
- `simulation/search_space.yaml` — initial tunable parameter space.
- `evaluation/monitoring_benchmarking_spec.md` — observability/eval design.
- `research/high_leverage_frameworks.md` — external concepts to mine.
- `research/*_PROMPT.md` — focused research prompts.
- `experiments/EXPERIMENT_BACKLOG.md` — high-information experiments.
- `implementation/ROADMAP.md` — implementation sequence.
- `research_job_manifest.yaml` — machine-readable research handoff.

## Design rule

**Optimize outcomes, not agent activity.**

A larger agent population, more messages, more tool calls, longer reasoning, or higher utilization are not success metrics by themselves. Every optimization candidate must be tested against mission-level quality, reliability, cost, latency, human attention, safety/trust, and knowledge reuse.
