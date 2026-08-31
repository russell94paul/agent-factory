# Reference Implementations — Mine, Do Not Clone

## Paperclip

Paperclip is a useful reference for mundane control-plane concepts that Agent Factory should not blindly redesign from zero.

Candidate areas to mine:

- persistent task/session state;
- heartbeats / resumable execution;
- atomic task checkout;
- worktree isolation;
- agent adapter interfaces;
- runtime skill injection;
- budgets and hard stops;
- approval/governance flows;
- artifacts/work products;
- operator scanning and intervention;
- task dependencies and routines.

Known north-star differences to preserve:

- our communication model may need richer typed events than tasks/comments;
- our organizations may be graphs/topologies, not only strict reporting trees;
- swarms/dynamic mission assembly are first-class research topics;
- shared cognition / mission-shaped KG is central;
- capability evidence, Org-IR, evolution and self-maintenance extend beyond mundane task orchestration.

Use `reference-implementation-miner` and the Paperclip research prompt to classify each candidate:

`REUSE | ADAPT | RESEARCH | REJECT`

If code is directly reused, preserve the applicable upstream license notices and track provenance.


## Super Simple Software Factory

Use `https://github.com/disler/super-simple-software-factory` as a reference for deterministic software-factory mechanics, especially:

- deterministic code owning sequencing/retries/acceptance;
- bounded agent phases vs code phases;
- typed cross-phase envelopes;
- explicit gates and earned success;
- same-session correction loops;
- per-agent model/prompt/tool/harness configuration;
- repository write-boundary enforcement;
- trace/event persistence;
- packaging the factory itself as an installable Claude skill.

Primary challenge for us: determine which of these simpler patterns can replace unnecessary complexity in Agent Factory, and where they stop being sufficient once communication fabric, swarming, shared cognition, long-lived missions and dynamic organizations appear.

Use `RREF2_SUPER_SIMPLE_SOFTWARE_FACTORY.md`.

## Inkwell / Factory in a Box

Use `https://github.com/disler/inkwell-agent-sandboxes-and-software-factory` as a reference for safe out-of-the-loop execution and experimentation, especially:

- nested but bounded orchestration tiers;
- disposable execution sandboxes;
- host-vs-sandbox credential boundaries;
- per-run capped/revocable model credentials;
- mount → execute → observe → harvest → teardown lifecycle;
- outside-only observability;
- best-of-N fan-out across isolated sandboxes;
- non-destructive result harvesting;
- separating the application payload from the factory that builds it.

Primary challenge for us: decide where VMs/sandboxes are warranted versus worktrees/containers, and how these concepts inform the Evolution Chamber and future compute fabric (including DGX Spark) without hard-coding one sandbox vendor.

Use `RREF3_INKWELL_FACTORY_SANDBOX.md`.

## General mining rule

Before building a commodity subsystem, search for mature open-source/reference implementations. Extract invariants, failure handling, operator semantics and integration boundaries—not branding or surface-level UI.


## Local source notes in this pack

For a concise separation between upstream observations and our inferences, read:

- `research/reference-implementations/SUPER_SIMPLE_SOFTWARE_FACTORY.md`
- `research/reference-implementations/INKWELL_FACTORY_IN_A_BOX.md`

These notes are deliberately not implementation specifications. The `RREF*` prompts must still challenge whether each extracted pattern belongs in Agent Factory.
