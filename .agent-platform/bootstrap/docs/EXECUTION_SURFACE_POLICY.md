# Execution Surface Decision Policy

The Bootstrap Commander must choose an execution surface per task instead of treating "Claude session" as one uniform runtime.

## Decision order

```text
Task
 │
 ├─ Needs local MCP / service / unpublished files / local secrets?
 │       └─ YES → Remote Control local session
 │
 ├─ Writes code in parallel with another task?
 │       └─ YES → isolated worktree or independent cloud branch
 │
 ├─ Self-contained and repo is pushed to GitHub?
 │       └─ YES → cloud web session is eligible
 │
 ├─ Read-only research/reference analysis?
 │       └─ YES → either surface; choose cheapest/least disruptive
 │
 └─ Needs Claude subscription Research access?
         └─ Prefer local coordinator; workers submit research requests
```

## Mandatory task metadata

Every executable task in the build DAG should eventually carry:

```yaml
execution:
  preferred_surface: remote_control | cloud_web | either
  isolation: worktree | branch | read_only | serialized
  local_dependencies: []
  required_secrets: []
  required_mcp: []
  can_run_parallel: true
  writes:
    - path/prefix
  gate_before_merge: true
```

The scheduler may override a preference only when the substitute surface satisfies the same capabilities and security constraints.

## Collision rule

Two tasks may execute concurrently only when one of the following is true:

1. both are read-only;
2. they use separate git worktrees/branches;
3. a deterministic ownership/locking mechanism proves their mutable resources do not conflict.

"The agents will coordinate" is not a locking strategy.
