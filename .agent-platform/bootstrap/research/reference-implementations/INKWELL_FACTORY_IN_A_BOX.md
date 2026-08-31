# Reference Note — Inkwell / Factory in a Box

Source: https://github.com/disler/inkwell-agent-sandboxes-and-software-factory

This note separates **observed upstream patterns** from **Agent Factory implications**. It is not a recommendation to clone Inkwell, its UI, prompts, or sandbox vendor choices.

## Observed upstream patterns

From the project's README and repository structure:

- three nested operational tiers: host-side sandbox orchestrator, in-sandbox orchestrator, and bounded software-factory agents;
- coding agents run inside the disposable sandbox next to the codebase;
- the host keeps privileged sandbox/provisioning credentials outside the worker environment;
- per-run inference credentials are scoped/capped and revoked at teardown;
- the sandbox lifecycle is explicitly modeled as create/fill/setup/execute/observe/teardown, with harvest as a non-destructive result-retrieval path;
- outside-only observability lets the operator watch the factory without manually driving each inner phase;
- the design supports best-of-N fan-out across independent sandboxes/configurations;
- harvested work is parked in separate refs rather than automatically merged;
- the application payload is intentionally separate from the factory that builds it.

## Agent Factory implications to test

These are hypotheses/inferences, not upstream claims:

1. Privilege boundaries should be structural: workers should not receive credentials that allow them to recursively create equally privileged workers.
2. The Evolution Chamber could use isolated candidate environments and non-destructive harvesting rather than allowing candidates to mutate the champion directly.
3. Best-of-N fan-out is a concrete early experiment pattern for team/prompt/model candidates.
4. External observation of isolated workers maps well to the Session Console / Mission Control concept.
5. Worktrees, containers, disposable VMs, DGX Spark nodes, and cloud sandboxes should all be treated as execution targets behind capability/lifecycle contracts rather than baked into organization logic.

## Questions for our architecture

- When are git worktrees enough, and when is a VM/container security boundary justified?
- Which credentials stay in the control plane versus entering a worker?
- What evidence must be harvested before teardown?
- How should candidate results be compared without auto-merging?
- How does this pattern generalize to self-maintenance and compute placement?

Use `research/prompts/RREF3_INKWELL_FACTORY_SANDBOX.md` for the full mining exercise.
