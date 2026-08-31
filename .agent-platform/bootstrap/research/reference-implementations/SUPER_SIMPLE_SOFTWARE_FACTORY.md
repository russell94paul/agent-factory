# Reference Note — Super Simple Software Factory

Source: https://github.com/disler/super-simple-software-factory

This note separates **observed upstream patterns** from **Agent Factory implications**. It is not a recommendation to copy the product or implementation.

## Observed upstream patterns

From the project's README and repository structure:

- deterministic Python owns the workflow graph, sequencing, retries, and acceptance;
- agents are bounded phases within that deterministic workflow;
- deterministic/code phases are used for known operations such as tests or commits rather than asking an agent to rediscover them;
- typed JSON envelopes carry structured outputs across phase seams;
- gates determine whether phase outputs are accepted;
- failure/correction can be routed back into the same session rather than always cold-starting;
- per-agent configuration separates agent identity/configuration from workflow call sites;
- agent configuration includes model, prompts, tool/harness choices, and write boundaries;
- traces/events are persisted for observability;
- the reusable factory is packaged as a Claude skill that can stamp starter machinery into another repository.

## Agent Factory implications to test

These are hypotheses/inferences, not upstream claims:

1. Agent Factory should compare its existing Prefect stage model against the upstream "bounded phase + deterministic rail" pattern before introducing new orchestration abstractions.
2. Typed seam envelopes may be a useful near-term precursor to the richer communication/evidence protocol.
3. The "skill is the installer/product" pattern may simplify our bootstrap pack and reduce custom bootstrap infrastructure.
4. Explicit write boundaries and deterministic rollback are good candidates for hardening autonomous coding workers.
5. A code-vs-agent phase distinction is an excellent anti-agent-inflation rule.

## Where this reference likely stops being sufficient for our north star

Research must test, rather than assume, limitations around:

- long-lived multi-team missions;
- event-driven agent-to-agent communication;
- shared cognition and mission-shaped knowledge graphs;
- expertise/availability-based swarm formation;
- cross-team learning;
- multi-organization/federated behavior;
- organizational simulation/evolution.

Use `research/prompts/RREF2_SUPER_SIMPLE_SOFTWARE_FACTORY.md` for the full mining exercise.
