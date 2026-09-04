# Agent Factory — Deadline Execution Pack

**Decision date:** 2026-09-02  
**Hard target:** Marketing Model meeting-ready by **2026-09-02 12:00 Pacific**.  
**Primary product milestone:** Switchboard can create/select the Marketing mission, choose an execution preset/team, launch it, show live state, auto-advance safe work, stop at human gates, and expose the resulting artifacts/evidence.

## The decision

Do **not** start another architecture rewrite and do **not** dispatch the research backlog before the deadline.

The repository already contains most of the substrate the desired Agentic IDE needs:

- canonical append-only work in `TaskStore`;
- dependency recovery and READY derivation;
- priority reasoning over downstream blockers and critical-path membership;
- claims and session liveness;
- worktree isolation;
- evidence-gated completion;
- bounded deployment primitives;
- a validated P1 Switchboard;
- CREATE WORK, START SYNCED, APPROVE/REJECT;
- per-work `MANUAL / GUARDED / AUTO` controls and pause/resume;
- a rendered mission DAG;
- a schedule instrument that already accepts a target date;
- a client-review renderer already validated on real work.

The highest-value missing seam is narrower:

> **The UI and policy can decide that work may start, but no autonomous execution pump acts on that decision.**

Tonight, extend the existing substrate rather than creating a second scheduler, second task model, second mission database, or new organizational runtime.

## Deadline order

1. Protect/revalidate the Marketing meeting artifact independently of new platform work.
2. Add the thin mission-preset adapter needed to create the Marketing DAG from Switchboard.
3. Wire preset/team selection into the existing P1 CREATE flow.
4. Add `RUN DAG`, `RUN CRITICAL PATH`, and a deterministic autonomy pump over canonical work.
5. Make APPROVE/REJECT and task completion wake the pump automatically when an autonomous run is active.
6. Execute a fresh Marketing vertical slice through the UI with at least one **real, non-dry-run agent step** if the live repo permits it.
7. Validate artifacts/evidence and preserve the already-meeting-ready fallback.
8. Complete the bounded Sales Model patch in parallel where safe; integrate it into Switchboard only after Marketing is proven.

## Hard non-goals before the meeting

- no generic Org-IR/compiler;
- no Agent → Manager → Master → Army mandatory hierarchy;
- no simulation/evolution chamber;
- no vector/graph memory platform;
- no generic graph editor;
- no automatic deadline-based scope deletion;
- no autonomous code self-modification;
- no broad research wave;
- no new source of truth for Switchboard.

## Architecture principle

**Goal-aware adaptive orchestration is a policy/scheduling layer over canonical work, not a new work system.**

Recompute what is READY, important, blocked, conflicting and safe after every meaningful event. The initial DAG is a plan, not a sacred sequence. However, before governance for scope mutation exists, adaptation may reorder/start/pause work but must not silently weaken success criteria.

## If the clock gets tight

Use this degradation order:

1. Drop visual polish.
2. Drop generic mission authoring; keep two presets.
3. Drop automatic deadline scoring; retain Run Critical Path.
4. Drop Mission Assurance Receipt if it threatens the meeting artifact.
5. Do **not** drop Marketing artifact validation.
6. Do **not** let Switchboard work destroy the known-good Marketing fallback.

Read next: `01_DECISIONS/ARCHITECTURE_SYNTHESIS.md`, then `02_DEADLINE/TONIGHT_CRITICAL_PATH.md`, then give Claude `07_CLAUDE/CLAUDE_PLAN_MODE_MASTER_PROMPT.md`.
