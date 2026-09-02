# 06 — State and Interaction Model

## Principle

Do not build the world around sprites. Build it around a typed organizational state model and event stream.

## Core domain entities

```text
Organization
Campaign
Mission
Objective
Team
Agent
Human
Capability
Artifact
Decision
Gate
Environment
Repository / Worktree / Sandbox
Tool
Context Packet
Knowledge Item
Evidence
Dependency
Communication
Evaluation
Incident
Resource / Budget
```

## Minimum world-facing event taxonomy

### Mission
- mission.created
- mission.started
- mission.blocked
- mission.resumed
- mission.completed
- mission.failed
- mission.cancelled
- mission.priority_changed

### Team / agent
- team.assembled
- team.reorganized
- agent.assigned
- agent.started
- agent.waiting
- agent.needs_help
- agent.completed
- agent.failed
- agent.context_pressure

### Communication
- help.requested
- evidence.published
- claim.challenged
- decision.requested
- decision.made
- handoff.started
- handoff.accepted
- warning.broadcast

### Logistics / readiness
- context.missing
- context.stale
- credential.unavailable
- tool.unavailable
- environment.unready
- dependency.blocked
- compute.constrained
- budget.threshold

### Engineering execution
- branch.created
- worktree.created
- file.changed
- conflict.detected
- tests.started
- tests.failed
- tests.passed
- review.requested
- review.rejected
- review.approved
- deploy.started
- deploy.failed
- deploy.succeeded
- rollback.started

### Evaluation / learning
- eval.started
- eval.completed
- champion.challenged
- candidate.promoted
- candidate.rejected
- learning.extracted
- knowledge.accepted
- contradiction.detected
- meta_tool.proposed

## Projection rule examples

```text
mission.blocked + credential.unavailable
=> squad halted + ZEUS Logistics route marked unavailable

conflict.detected(file overlap)
=> convergence/collision marker between two teams

agent.needs_help
=> distress signal available

context.stale
=> intelligence/supply route marked stale

gate.awaiting_human
=> command authorization marker

high uncertainty claim cluster
=> fog density increases in affected objective
```

## Command compiler

World interactions should compile into typed commands.

### Example: drag specialist onto mission

```json
{
  "command": "mission.add_specialist",
  "mission_id": "M-184",
  "capability": "oauth-authentication",
  "candidate": "agent:hermes-17",
  "handoff_mode": "compiled_context",
  "reason": "operator_direct_manipulation"
}
```

### Example: draw a boundary and request review

```json
{
  "command": "scope.create_review_mission",
  "targets": ["repo:A/path/x", "repo:A/path/y"],
  "success_criteria": ["no regression", "security review"],
  "risk": "medium"
}
```

Before execution:

```text
Gesture / world command
        ↓
Intent compiler
        ↓
Scope preview
        ↓
Permission / budget / risk check
        ↓
Human confirmation if required
        ↓
Runtime command
        ↓
Events
        ↓
World + dense UI projections update
```

## Two independent state layers

### Operational truth
Authoritative backend state.

### World presentation
Camera, layout, animation, selected targets, avatar cosmetics, harmless social state.

Never let presentation state silently become operational truth.

## Search remains essential

A world without universal search becomes a maze.

Minimum command/search actions:

```text
Go to mission
Go to agent
Go to repo
Go to incident
Go to approval
Ask ZEUS
Show blockers
Show unknowns
Show collisions
Show things waiting on me
```
