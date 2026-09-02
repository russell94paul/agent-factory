# Agent Genome

## Definition

An Agent Genome is the complete versioned desired-state configuration that determines how an Agent behaves.

Potential top-level namespaces:

```yaml
agent:
  identity:
  purpose:
  role:
  authority:

  model:
  cognition:
  reasoning:
  planning:
  execution:

  personality:
  behavior:
  communication:

  skills:
  capabilities:
  knowledge:
  memory:

  tools:
  integrations:
  environment:

  permissions:
  security:
  prohibitions:

  autonomy:
  escalation:
  risk:

  resources:
  budgets:
  context:

  reliability:
  recovery:
  health_policy:

  learning:
  adaptation:

  collaboration:
  relationships:

  evaluation:
  certification:

  lifecycle:
```

## Human-inspired configuration must map to mechanisms

| Human-inspired concept | Agent mechanism |
|---|---|
| Confidence | calibrated evidence strength |
| Curiosity | exploration budget |
| Patience | iteration / verification threshold |
| Caution | action-risk threshold |
| Sociability | communication propensity |
| Conscientiousness | verification/completion strictness |
| Experience | certified mission history |
| Stress | resource/contention/error-pressure indicator |
| Fatigue | accumulated degradation indicators |
| Expertise | validated capability score |
| Trust | historical evidence reliability |
| Independence | autonomy/escalation threshold |
| Creativity | search breadth / candidate diversity |
| Skepticism | evidence threshold |
| Persistence | retry/replan behavior |
| Focus | context allocation policy |

## Example architecture preset

```yaml
agent:
  identity:
    title: "Root Cause Specialist"
    desired_role: "senior_python_engineer"

  model:
    family: "configurable"
    effort: high

  cognition:
    working_style: hypothesis_driven
    skepticism: high
    exploration: medium
    verification_depth: high

  skills:
    target:
      - python
      - prefect
      - oauth
      - snowflake

  knowledge:
    hypermesh_profile: deep_root_cause_v2
    retrieval: adaptive
    max_context_tokens: 18000

  tools:
    allowed:
      - repo_search
      - tests
      - logs
      - docs
      - issue_tracker

  autonomy:
    mode: bounded_autonomous
    escalation_confidence_threshold: 0.65

  permissions:
    production_write: false

  evaluation:
    profile: connector_bug_fix_v3
```

## Preset examples

- Rapid Triage
- Deep Investigator
- Production Guardian
- Research Scout
- Code Intelligence Specialist
- Audit Specialist
- HyperMESH Cartographer
- Agent Architect
- Verifier
- Sentinel

## Prompt -> Config -> Evaluate

```text
Natural language Agent request
 -> Config Generator
 -> Candidate Agent Genome
 -> schema validation
 -> policy validation
 -> simulation
 -> held-out evaluation
 -> certification
 -> registry
```

The generated config is a proposal, never the unquestioned source of truth.
