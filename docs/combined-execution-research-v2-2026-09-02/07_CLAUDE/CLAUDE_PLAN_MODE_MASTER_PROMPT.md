# Claude Plan Mode Master Prompt — Deadline-First Agent Factory

You are operating in the live `agent-factory` repository.

This pack is a **proposed synthesis from an external review of the repository's research corpus and architecture supplement. It is not permission to blindly edit code.** Your first responsibility is to reconcile this pack against the live checkout.

## Hard objective

By **2026-09-02 12:00 Pacific**, maximize the probability of this outcome:

> Open Switchboard → create/select the Marketing Model mission → choose a compatible execution preset/team → launch → watch execution/status → automatically advance safe ungated work → stop at real human gates → inspect evidence/artifacts → obtain a meeting-ready Marketing deliverable.

Second objective: complete the bounded Sales Model changes without jeopardizing the Marketing deliverable.

## Read first

From this pack:

1. `00_START_HERE.md`
2. `01_DECISIONS/ARCHITECTURE_SYNTHESIS.md`
3. `01_DECISIONS/DECISION_REGISTER.yaml`
4. `02_DEADLINE/TONIGHT_CRITICAL_PATH.md`
5. `03_EXECUTION/tonight_dag.yaml`
6. `03_EXECUTION/autonomy_policy.yaml`
7. `04_MISSIONS/marketing_model.yaml`
8. `05_SWITCHBOARD/P0_FUNCTIONAL_SPEC.md`
9. `05_SWITCHBOARD/AUTONOMY_PUMP_DESIGN.md`

Then inspect the LIVE repo before trusting any file/line claim from the review pack.

Before planning, also read these live-repo sources if present:

- `.agent-platform/PACK_CONFORMANCE.md`
- `.agent-platform/RECONCILIATION.md`
- `.agent-platform/bootstrap/docs/EXECUTION_SURFACE_POLICY.md`
- `.agent-platform/bootstrap/docs/WEB_REMOTE_SESSION_RUNBOOK.md`
- `.agent-platform/bootstrap/schemas/mission-assembly.schema.json`
- `.agent-platform/bootstrap/schemas/capability-record.schema.json`

And from this V2 pack:

- `11_AGENT_PLATFORM_DELTA/SOURCE_COVERAGE_CORRECTION.md`
- `11_AGENT_PLATFORM_DELTA/CRUCIAL_FEATURES_DELTA.md`
- `11_AGENT_PLATFORM_DELTA/CONCEPT_CROSSWALK.yaml`

Treat `.agent-platform/bootstrap` as design input. `RECONCILIATION.md`, `PACK_CONFORMANCE.md`, canonical runtime state and live code outrank it when they disagree.


## Evidence you must verify in the live checkout

The review found these mechanisms, but you must re-measure them:

- `factory/tasks.py` canonical append-only TaskStore and evidence-gated close;
- `factory/work.py` canonical work projection/readiness and any autonomy fields;
- `factory/coordination.py` priority/downstream-block reasoning;
- `factory/board.py` dependency/critical-path logic;
- `factory/switchboard.py` state projection;
- `factory/switchboard_p1.py` CREATE, START SYNCED, APPROVE/REJECT, autonomy UI;
- `scripts/local_tracker.py` actual POST routes and action wiring;
- existing guarded-start/start/deploy mechanism;
- `factory/launch.py` supervised/guarded readiness boundary;
- `factory/schedule.py` target/deadline behavior;
- existing Marketing mission files, client-review renderer, and meeting-ready launch path;
- current tests, worktrees, claims, sessions and dirty files.

If the live repo differs, prefer measured live state and explain the difference.

## Critical architectural constraints

1. **Do not create a second task system.** Canonical work remains TaskStore/events.
2. **Switchboard remains a projection/action surface, not a new source of truth.**
3. **Do not build generic Org-IR, an organization OS, or a mandatory Agent→Manager→Master→Army hierarchy for this deadline.**
4. **Mission presets compile to existing canonical work.** A generic Mission entity/lifecycle is deferred unless the live code already contains one and reusing it is cheaper.
5. **Do not bypass readiness/safety to manufacture a real-run PASS.**
6. **No automatic weakening of success criteria.** Deadline pressure may reorder or pause work, not silently change PASS.
7. **No autonomous self-edit/release path.**
8. **No public push of client-bearing artifacts.** Respect existing release gates/gitignore controls.
9. **Never `git add -A` in a shared dirty checkout.** Use isolated worktrees/branches and stage explicit paths.
10. **Do not dispatch the research backlog before the deadline.**
11. **Do not create `PROJECT_STATE.yaml` or `PROGRESS.yaml` as parallel truth** if the live repo still derives those states from canonical gates/tasks.
12. **Prefer execution-surface metadata over manual session routing.** If cheap in the live repo, attach local/MCP/secrets/isolation/write-set constraints to runnable nodes and let the existing scheduler select a compatible surface.
13. **Do not build generic Mission Assembly, capability marketplace, Venture Compiler, Customer Learning Fabric or Portfolio Allocator before the meeting.** Preserve them as post-deadline concepts only.

## The key seam to close

The review found P1 already exposes `MANUAL`, `GUARDED`, `AUTO`, pause/resume, and a guarded-start decision, but its own UI states that **GUARDED decides; it does not act**.

Build the smallest reliable execution pump that turns canonical READY work + policy into starts using the existing start mechanism.

Required behavior:

- RUN DAG starts policy-allowed READY nodes up to max concurrency.
- RUN CRITICAL PATH starts only policy-allowed READY ancestors of the selected target.
- MANUAL never auto-starts.
- GUARDED auto-starts only if the current guarded-start decision allows it.
- AUTO still obeys hard safety/refusal policies, claims, conflicts and concurrency.
- operator PAUSE stops new starts.
- APPROVE/REJECT while an autonomous run is active wakes the planner and may start newly READY downstream work.
- completion wakes the planner when practical; if no event callback exists, add the smallest bounded adapter/poller rather than a new orchestration framework.
- no generic auto-retry; only retry classified transient failures within an attempt budget.


## Execution-surface routing addendum

The `.agent-platform` delta contains a high-leverage mechanism that is compatible with the existing architecture. For each executable DAG node, determine whether the live repo can cheaply carry metadata equivalent to:

```yaml
execution:
  preferred_surface: remote_control | cloud_web | either
  isolation: worktree | branch | read_only | serialized
  local_dependencies: []
  required_secrets: []
  required_mcp: []
  can_run_parallel: true
  writes: []
  gate_before_merge: true
```

Do not create a new scheduler for this. Treat these fields as constraints consumed by the existing planning/start path. If adding them threatens the Marketing critical path, defer implementation but include the exact post-deadline seam.

## Plan Mode task

Produce a concrete implementation plan BEFORE editing. The plan must:

### A. Re-measure state

Report:

- current HEAD/branch;
- dirty/untracked state;
- worktrees and active sessions/claims;
- exact P1 route/action seams;
- current tests;
- known-good Marketing artifact path/launch command;
- whether a real non-dry-run agent can run safely against the Marketing mission in the current repo;
- whether F90/cross-repo threading is on the critical path for Marketing or only for later Sales/connector work.

### B. Compare plan vs repo

For every proposed new module/change in this pack, label:

- REUSE AS-IS
- WIRE EXISTING
- SMALL EXTENSION
- NOT NEEDED
- BLOCKED

Do not rewrite a mechanism that already exists.

### C. Produce an executable DAG

Use dependency order, not a prose phase list. Identify:

- critical-path nodes;
- safe parallel lanes;
- file-touch conflicts;
- human gates;
- fallback triggers;
- acceptance tests per node.

### D. Preserve slash-command ergonomics

Inspect whatever slash-command convention already exists in this repo/user environment.

Create or update a compact command surface equivalent to:

- `/af-status`
- `/af-run-dag <run-or-mission>`
- `/af-run-critical <target>`
- `/af-pause <run>`
- `/af-resume <run>`
- `/af-phase <phase-id>` for targeted/manual recovery

If current command names already exist, preserve them and map this behavior onto them rather than inventing duplicates.

A phase command is an entry point into the DAG, not a separate source of sequencing truth.

### E. Plan explicit parallel sessions/worktrees

Prefer these lanes if the live file graph permits:

1. Delivery Safety — revalidate Marketing fallback/artifact.
2. Mission Adapter — preset→canonical-work compiler.
3. Switchboard UI — preset/team/run controls.
4. Autonomy Runtime — planner/pump and wakeups.
5. Sales Delivery — bounded Sales patch.

If two lanes edit the same files, merge them or order them; do not rely on wishful parallelism.

## Implementation priority

### MUST before meeting

- Marketing fallback protected.
- Marketing preset can be created/selected from Switchboard.
- execution/team preset can be chosen or deterministically bound.
- mission launches through existing execution mechanism.
- state/evidence/artifact visible.
- RUN DAG works.
- safe ungated work auto-continues.
- human gate blocks correctly.
- approval can resume downstream automatically.
- fresh Marketing vertical slice completed or a measured blocker recorded without destroying the fallback.

### SHOULD

- RUN CRITICAL PATH.
- deadline/target shown as execution mandate context.
- Sales patch completed.
- Mission Assurance Receipt from existing evidence.

### DEFER

Everything in the pack's non-goals list.

## Real-run rule

The corpus's most important measurement gap is that no agent has ever completed a real non-dry-run controller run. If the Marketing vertical slice can safely create that first run **without weakening any existing refusal**, do it and preserve the run/evidence record.

If it cannot, do not fake it. Record the blocker and continue with the strongest honest supervised/fallback path.

## Stop condition for Plan Mode

Stop after you have produced:

1. live-state reconciliation;
2. final executable DAG;
3. exact files/modules/routes you will edit;
4. parallel-lane/worktree plan;
5. acceptance tests;
6. fallback points;
7. slash-command mapping;
8. ordered execution commands.

Ask for approval of that plan if Plan Mode requires it. After approval, execute the DAG and automatically continue ungated work according to the policy above rather than asking for a new prompt after every phase.
