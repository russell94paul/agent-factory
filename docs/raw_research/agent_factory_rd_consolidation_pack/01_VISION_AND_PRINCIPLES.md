# Vision and System Principles

## Core vision

Agent Factory should become an experimental platform for computational organizational intelligence.

A standard Agent is approximately:

```text
Model + Prompt + Tools
```

The target Agent architecture is closer to:

```text
Versioned Agent Genome
+ Persistent Second Brain
+ HyperMESH Federation
+ Mission Context Compiler
+ Adaptive Retrieval
+ Capability Model
+ Health / Readiness
+ Curriculum
+ Communication Policy
+ Relationship Graph
+ Evaluation History
+ Certification
```

The long-term loop is:

```text
Mission
  -> requirements
  -> Agent / Team / Organization configuration
  -> simulation / replay
  -> evaluation
  -> certification
  -> deployment
  -> evidence
  -> better configuration
```

## Architectural thesis

Treat the complete computational organization—not merely the model or prompt—as a constrained,
versioned optimization space conditioned on mission requirements.

Possible optimization scopes:

- skill/tool
- cognitive module
- Agent
- Agent Team
- Team Manager
- multi-team
- Army
- Command
- project-specific organization

## Evidence versus configuration

Configurable:

- desired role
- tools
- model
- reasoning strategy
- permissions
- memory/retrieval profile
- communication policy
- training policy
- topology
- budgets

Observed:

- mission count
- mission success rate
- rework rate
- time-to-green
- cost per success
- learning velocity
- knowledge contribution quality
- skill evidence
- team synergy
- reliability

Performance targets belong in optimization objectives:

```yaml
development_targets:
  oauth_bug_fix:
    target_pass_rate: 0.98
```

Measured evidence remains separate:

```yaml
experience:
  oauth_bug_fix:
    missions: 42
    observed_pass_rate: 0.91
```

## Self-improvement rule

Self-improvement means:

```text
candidate change
 -> evaluation
 -> evidence
 -> certification
 -> promotion
```

It does NOT mean:

```text
agent rewrites own prompt
 -> assumes improvement
```

## Organizational levels

```text
Agent
 -> Team
 -> Army
 -> Organization
 -> Portfolio
```

Not every level must be a command hierarchy. Some can be capability namespaces, routing pools,
policy domains or economic/portfolio views.
