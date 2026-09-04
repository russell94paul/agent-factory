# Claude Delta Corpus / Research Prompt — `.agent-platform`

You are in the live `agent-factory` repo. This is a **delta reconciliation pass**, not a new corpus rebuild.

## Facts to verify first

Read:

- `.agent-platform/PACK_CONFORMANCE.md`
- `.agent-platform/RECONCILIATION.md`
- `docs/_index/concept_index.yaml`
- `docs/_index/high_leverage_concepts.md`
- `docs/research/backlog.yaml`
- `docs/research/dependency_graph.md`

Verify the reported fact that the prior session read all 19 bootstrap docs, 8 schemas, 6 scripts and 13 skills. If false, report the exact mismatch.

## Objective

Promote the useful concrete mechanisms in `.agent-platform/bootstrap/` that were represented only at bundle level and reconcile them with the existing canonical concepts/research backlog.

Do **not** rebuild the corpus and do **not** blindly restore the bootstrap pack's original build order.

## Required concept families

Inspect all source material relevant to:

1. Execution Surface Policy / Remote Control / cloud/worktree routing.
2. Autonomy Ladder / evidence-gated promotion.
3. Mission Assembly / conditional swarming / availability.
4. Capability Record / certified agent-team registry.
5. Synthesis Inbox / Promotion Board / mission-control evolution.
6. Compute & Integration Fabric / compute-node contract.
7. Autonomous Product Lifecycle / Venture Compiler.
8. Opportunity Intelligence.
9. Customer & Market Learning Loop.
10. Portfolio Experiment & Resource Allocator.
11. Commercial Autonomy Policy.
12. Research job lifecycle/state machine.
13. Pattern/reference implementation mining.
14. Typed message envelope fields not already represented canonically.

## Reconciliation rules

For each mechanism label exactly one:

- ALREADY_CANONICAL
- CANONICAL_BUT_UNDER-SPECIFIED
- PROMOTE_AS_NEW_CONCEPT
- MERGE_INTO_EXISTING
- PRESERVE_AS_FUTURE_VERTICAL
- REJECT_AS_DUPLICATE_SOURCE_OF_TRUTH
- RESEARCH_REQUIRED

For every proposed promotion, name:

- source files;
- existing related concept IDs;
- implementation status from live code;
- exact benefit;
- smallest experiment;
- unlock condition;
- whether it changes the current deadline plan.

## Research discipline

Do not dispatch broad research automatically.

Use this order:

1. repo evidence;
2. existing `agent-army-research` findings;
3. current primary standards/docs only when an external fact is needed;
4. create/modify a research mission only if the decision still cannot be made.

Where relevant, check at minimum:

- current Claude Code execution/session primitives for Execution Surface Policy;
- A2A Agent Card/discovery semantics for capability registry overlap;
- OpenTelemetry messaging/GenAI trace semantics for correlation/causation fields.

## Required outputs

Incrementally update, only where justified:

- `docs/_index/concept_index.yaml`
- `docs/_index/high_leverage_concepts.md`
- `docs/_index/current_vs_proposed.md`
- `docs/_index/research_gap_candidates.md`
- `docs/research/backlog.yaml`
- `docs/research/dependency_graph.md`

Create:

- `docs/_index/agent_platform_delta_synthesis.md`

The synthesis must contain:

1. coverage correction;
2. promoted/merged/rejected concepts;
3. research changes;
4. implementation-plan changes;
5. a section named **Deadline Impact**.

## Hard deadline rule

Unless live repo evidence proves otherwise, preserve this current ordering:

1. Marketing Model meeting-ready delivery;
2. Switchboard runnable mission vertical slice;
3. Sales bounded patch;
4. post-deadline measurement/research.

Do not let venture, Org-IR, capability-market, gamified-world or compute-fabric work enter the deadline critical path.

## HARD STOP

Stop after the delta synthesis and canonical-index/research-backlog updates. Do not implement the newly promoted concepts in this session.
