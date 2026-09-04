# .agent-platform Coverage Correction

## What was actually missed

The `.agent-platform` tree was **not unread**. `PACK_CONFORMANCE.md` records that the prior reconciliation read:

- all 19 design docs;
- all 8 schemas;
- all 6 scripts;
- all 13 skills;
- plus the bootstrap entrypoints and roadmap material.

The real gap was **granularity**: `corpus_manifest.yaml` represented the 110-file bootstrap mostly as one rich bundle, while `concept_index.yaml` promoted only a subset of its concrete mechanisms into first-class concepts.

So the correct response is **not another full corpus rebuild**. It is a delta pass that:

1. promotes useful mechanisms that were only bundle-level notes;
2. crosswalks them to existing Agent Factory mechanisms so nothing is duplicated;
3. opens targeted research only where prior art or an empirical decision is genuinely missing;
4. patches the implementation roadmap only where the delta changes priority.

## Reconciliation rule

`.agent-platform/RECONCILIATION.md` and `PACK_CONFORMANCE.md` outrank the bootstrap pack when they provide measured live-repo evidence. The bootstrap pack is a north-star/design source, not runtime truth.

## Deadline effect

No recovered `.agent-platform` feature invalidates the current Marketing -> Switchboard -> Sales deadline order.

One feature **does deserve to move closer to P0/P1** because it directly reduces the operator's current multi-session friction without requiring a new orchestration system:

> **Execution Surface Routing** — attach task requirements for local services/secrets/MCP, worktree isolation, cloud eligibility, mutable resource ownership, and parallel safety; let the existing scheduler choose a compatible surface.

Everything else below is post-deadline unless the live repo proves it is already nearly free.
