# Implementation Pack Prompt

Use only after a north-star architecture has been explicitly selected.

Translate the approved architecture into an executable engineering program for the existing `agent-factory` repository.

## Required outputs

- target repo tree
- package/service boundaries
- canonical schemas/contracts
- API/event contracts
- migration adapters
- feature flags
- storage migrations
- eval suites
- test strategy
- observability requirements
- security/permission model
- UI integration points
- implementation DAG
- parallel workstreams
- per-phase acceptance criteria
- rollback plan
- compatibility plan
- documentation updates
- deprecation schedule

## Rules

- Reuse proven existing components where practical.
- Every new abstraction must name the duplication/risk it removes.
- Every agentic subsystem needs an eval strategy.
- Every self-modifying path needs bounded permissions, sandbox/canary and rollback.
- Every migration phase must keep the current production proving ground operable unless explicitly approved otherwise.
- Prefer thin vertical slices over building unused platform layers.
- Use feature flags or adapters for reversible migrations.
- Separate schema introduction from broad runtime adoption where possible.

For each work item record:

- ID
- objective
- affected paths
- dependencies
- owner/team archetype
- deterministic vs agentic implementation
- test/eval
- success metric
- rollback
- risk
- expected effort class
- parallelizable_with
