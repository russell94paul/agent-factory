# Start-to-Finish Build Flow

This is the intended progression, not a promise that every north-star component must be built. Every phase can delete or simplify later phases when evidence says they are unnecessary.


### Operating plane — continuous across all stages

Run the build through a web-first session topology:

- one coordinator with access to repository-local state, MCP/services and secrets;
- isolated Remote Control worktrees for local parallel writers;
- Claude Code web/cloud branches for self-contained independent tasks;
- a future Session Console that absorbs this external session topology into Agent Factory itself.

The bootstrap should progressively replace manual session launching/monitoring with Agent Factory capabilities as Stage 2+ matures.

## Stage 0 — Bootstrap the bootstrapper

**Goal:** make project context and research reproducible.

Build/establish:

- durable project state;
- repo-context compiler;
- research manifests;
- Claude skill installation path;
- Claude Research prompt queue + return inbox;
- research artifact storage;
- current-state reconciliation.

**Exit:** a fresh Claude session can recover the project, prepare an exact Claude Research job, ingest the returned raw report, synthesize it, and update project state with no API billing and no manual report reconciliation.

## Stage 1 — Harden the current Agent Factory

**Goal:** one production vertical proves reliable agent-team execution.

Build/harden:

- positive GREEN contracts;
- versioned/locked behavior artifacts;
- preflight viability checks;
- deterministic gates;
- eval harness;
- run evidence and attribution;
- cost/latency/outcome metrics.

**Exit:** a real workload goes RED→GREEN with evidence, regression tests pass, and the exact team/configuration is reproducible.

## Stage 2 — Build Command / Session Console MVP

**Goal:** eliminate terminal/tab coordination overhead.

Build:

- active task/session list;
- research job state;
- task DAG view;
- blockers/approvals;
- artifacts;
- Synthesis Inbox;
- reply/resume hooks where supported.

**Exit:** multiple independent workstreams can be launched/monitored without manual tab bookkeeping.

## Stage 3 — Communication + shared-state substrate

**Goal:** agents coordinate through typed, observable interactions.

Build:

- event/message envelope;
- availability/capability announcements;
- evidence/claim/warning/help/handoff events;
- subscription/routing rules;
- anti-loop/dedup/priority semantics;
- replay/audit.

**Exit:** at least one real mission uses typed coordination instead of ad-hoc transcript sharing, with measurable overhead and benefit.

## Stage 4 — Collective Cognition / mission context v0

**Goal:** make historical experience reusable without flooding every agent.

Build:

- provenance-aware knowledge records;
- mission similarity retrieval;
- experience summaries;
- mission-shaped context graph;
- role-specific context packets;
- contradiction/freshness metadata.

**Exit:** an experiment shows mission-specific context is at least as effective as the current baseline while improving cost, relevance, or correctness.

## Stage 5 — Capability + Mission Assembly v0

**Goal:** configure teams from demonstrated capability and mission needs.

Build:

- capability/experience records;
- availability/workload state;
- blueprint registry;
- deterministic mission assembler;
- swarm formation only where justified;
- communication/context routes emitted as part of the plan.

**Exit:** at least two mission families select or configure different proven organizations and beat/meet a fixed baseline under frozen evaluation.

## Stage 6 — Organization compiler / Org-IR experiment

**Goal:** test whether a distinct intermediate representation reduces complexity and improves portability/debuggability.

Build only if research/experiments justify it:

- intent contract;
- organization definition;
- resolved organization lock;
- validation/compiler passes;
- target adapters for existing Factory runtime.

**Exit:** Org-IR demonstrably simplifies or enables a capability that TeamBlueprint + existing DAGs cannot cleanly provide.

## Stage 7 — Integration + Compute Fabric

**Goal:** place organizational workloads on appropriate tools/runtimes/compute.

Build incrementally:

- normalized adapter capability model;
- runtime health/capacity;
- deployment plan;
- lifecycle/log/artifact hooks;
- first real target(s) only.

Possible future target: NVIDIA DGX Spark as local agent compute, alongside local/cloud/container runtimes.

**Exit:** Factory can discover one external runtime/compute target, validate capability, deploy a bounded workload, observe it, collect evidence, and terminate/rollback.

## Stage 8 — Organizational Debugger + Simulation

**Goal:** explain failures and compare candidate organizations safely.

Build:

- causal execution trace;
- artifact/knowledge lineage;
- seam attribution;
- replay;
- simulation scenarios;
- champion/challenger comparisons.

**Exit:** debugger correctly identifies seeded failure seams and simulation results predict real evaluation changes well enough to be useful.

## Stage 9 — Evolution Chamber

**Goal:** experimentally optimize prompts/skills/models/tools/context/topology without self-grading.

Build:

- candidate generator;
- immutable experiment specs;
- DEV/VALIDATION/REGRESSION/OOS gates;
- Pareto comparison;
- canary promotion/rollback;
- frozen evaluator authority.

**Exit:** one bounded artifact class improves under out-of-sample evaluation without violating hard constraints.

## Stage 10 — Self-Maintenance

**Goal:** Factory helps maintain its own components.

Build:

- drift/health detectors;
- maintenance intent generation;
- maintenance organization blueprint;
- repair simulation/test;
- approval/canary/rollback;
- knowledge writeback.

**Exit:** seeded platform faults are detected and repaired through the same governed mission lifecycle.

## Stage 11 — Higher-order organizations / federation

Only after lower layers are proven:

- multiple organizations;
- cross-organization knowledge/permission boundaries;
- temporal echelons;
- strategic research/doctrine;
- federated resource/capability exchange.

**Exit:** evidence proves this added hierarchy beats simpler composition.

## Promotion rule

> The platform does not rise in rank because a diagram says it can. Every rank is unlocked by the verification, recovery, and observability needed to make the next one safe and useful.

---

# Commercial/value track — begins before the north star is complete

Do not wait for Stage 11 before testing economic value.

After Stage 1 provides trustworthy evaluation and Stage 2 provides manageable parallel operations, begin bounded commercial experiments in parallel with the capability roadmap:

```text
Stage 1/2 Factory maturity
        ↓
Opportunity Intelligence
        ↓
small external validation
        ↓
Venture Compiler
        ↓
Factory builds bounded MVP
        ↓
launch gate
        ↓
customer/market evidence
        ↓
customer learning loop
        ↓
portfolio decision
  KILL | HOLD | IMPROVE | SCALE
        ↓
reusable capability/knowledge
        └───────────────→ Collective Cognition / Evolution
```

The value track itself becomes a source of evaluation data for the platform. A better organization is one that produces better verified outcomes under constraints, not merely one that completes more internal tasks.

## UI evolution track

The Build Command interface should evolve with the platform:

```text
Construction Console
    → Mission Command
    → Venture / Portfolio Command
    → Artificial Organization Observatory
```

See `ROADMAP_TO_VISION.md` and `docs/GAMIFIED_MISSION_CONTROL.md`.
