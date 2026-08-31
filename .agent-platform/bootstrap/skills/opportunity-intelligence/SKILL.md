---
name: opportunity-intelligence
description: Compile market/customer questions into parallel research jobs, synthesize evidence, and emit falsifiable software opportunity hypotheses with monetization and distribution assumptions.
---

# Opportunity Intelligence

## Use when

- searching for software/SaaS opportunities;
- researching monetization for Agent Factory or a Factory-built product;
- comparing customer segments, pricing approaches or channels;
- converting vague "what should we build?" ideas into evidence-backed hypotheses.

## Procedure

1. Read current venture/product/project state and relevant Collective Cognition records.
2. State the decision the research must change.
3. Decompose independent questions into research jobs.
4. Use the `claude-research-orchestrator` / `research-wave-runner` path where deep external research is required; no API credential is needed in the active workflow.
5. Run independent jobs in parallel when they do not share mutable state.
6. Synthesize with `research-synthesizer`.
7. Separate sourced evidence, inference, assumptions and unknowns.
8. Produce one or more `OpportunityHypothesis` records.
9. Define cheapest falsification experiments before recommending build work.

## Required output per opportunity

- problem;
- target user/buyer;
- evidence;
- existing alternatives/competitors;
- why current alternatives may be insufficient;
- proposed value proposition;
- monetization hypotheses;
- distribution hypotheses;
- operational/support burden;
- key risks;
- confidence by claim;
- falsification criteria;
- next experiment;
- estimated research/build cost range when supportable;
- explicit `BUILD_NOW | VALIDATE_FIRST | PARK | REJECT` recommendation.

Never equate web enthusiasm, search volume, or competitor existence with proven willingness to pay.
