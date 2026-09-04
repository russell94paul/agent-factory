# Crucial / Useful Features Recovered from `.agent-platform`

This is a feature-level reconciliation against the existing 92-concept index and the deadline execution pack.

| Feature | Delta status | What to do | Priority |
|---|---|---|---|
| **Execution Surface Router** | Under-indexed and explicitly `NOT YET` in `PACK_CONFORMANCE` | Add execution requirements to DAG nodes and choose local Remote Control / cloud / isolated worktree / read-only surface without creating a second scheduler | **P0/P1** |
| **Evidence-gated Autonomy Ladder** | Present in backlog RB-15 but absent as a named concept | Treat it as a **projection over existing readiness gates**, never as `PROGRESS.yaml`; use `LOCKED/EXPERIMENTAL/PROVISIONAL/EARNED` for operator comprehension | **P1/P2** |
| **Mission Assembly Plan** | Partially overlaps adaptive team formation but adds a deterministic compile sequence: task family/risk -> capabilities -> prior experts -> availability -> topology -> context/comms -> budget/gates | Build only after real runs; initially extend mission presets, not generic Org-IR | **P2** |
| **Conditional Swarming + Rich Availability** | Under-indexed | Preserve fields such as load, tool/env access, cost lane, latency, recent experience, health, permissions; swarm only for diversity/parallel exploration/independent verification | **P2/P3** |
| **Capability Record / Certified Team Registry** | Existing registry concept is narrower | Extend existing registry with conditions, eval history, validity windows, cost/latency, reliability/regressions and evidence refs. Reuse A2A-style discovery metadata instead of inventing discovery | **P2** |
| **Synthesis Inbox** | Missing as a first-class UI mechanism | Queue research/review/agent outputs that require reconcile/disposition. It directly addresses many-session operator load | **P1/P2** |
| **Promotion Board** | Missing as UI projection | Render autonomy/readiness unlocks from canonical gates; never maintain progress separately | **P2** |
| **Communication Overlay** | Existing typed-message concepts cover semantics, not operator compression | Visualize causal evidence/warning/handoff/challenge events; adopt only after real cross-team traffic exists | **P3** |
| **Compute & Integration Fabric** | Under-indexed | Keep agent-to-agent communication separate from runtime/tool adapters. Define generic adapter/compute-node capabilities before DGX/provider-specific control planes | **P3** |
| **Autonomous Product Lifecycle / Venture Compiler** | Bundle-only, absent from concept index | Keep as a vertical built on the same mission/eval/policy substrate: Discover -> Validate -> Design -> Build -> Launch -> Learn -> Operate -> Improve -> Decide | **P3/P4** |
| **Opportunity Intelligence** | Bundle-only | Market signal -> structured `OpportunityHypothesis` with evidence, assumptions, falsification and BUILD/VALIDATE/PARK/REJECT recommendation | **P3/P4** |
| **Customer & Market Learning Loop** | Bundle-only | Convert permissioned telemetry/support/experiment signals into provenance-preserving evidence and cheapest falsification experiments | **P3/P4** |
| **Portfolio Experiment Allocator** | Bundle-only | `KILL/HOLD/IMPROVE/SCALE/MORE_EVIDENCE`; multi-objective resource allocation with opportunity cost and hard constraints | **P4** |
| **Commercial Autonomy Policy** | Partially represented by bounded autonomy | Specialize the Mandate layer for money, public claims, outreach, privacy, contracts and deployment; do not let revenue rewrite evaluator rules | **P3/P4** |
| **Research Job State Machine** | Bundle-only; prior research system is stronger | Do **not** create a second research queue. Borrow execution-surface/status fields into the existing `agent-army-research` backlog only if useful | **P2** |
| **Pattern Extraction / Reference Miner** | Existing meta-tool and research-process concepts partially cover it | Keep “mine patterns, do not clone” as a reusable research skill; no new subsystem | **P2** |

## Highest leverage additions

### 1. Execution Surface Router — implementable now

The source policy already specifies the metadata shape:

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

This fits Goal-Aware Adaptive Orchestration naturally: surface selection becomes a scheduling constraint, not a second orchestration architecture.

### 2. Certified Capability Record — major future multiplier

A useful registry record should bind **what an agent/team claims it can do** to **the conditions under which that claim was measured**:

- exact config/version identity;
- task family and conditions;
- evidence count and refs;
- success/reliability/regression history;
- confidence and validity window;
- cost and latency;
- required tools/permissions/runtime;
- certification state.

This becomes the input for later mission assembly, configuration search and a possible capability marketplace.

### 3. Synthesis Inbox — immediate operator productivity

The user's current workflow already has many parallel Claude/research sessions. A Synthesis Inbox is not decorative UI: it is a queue of outputs whose **next operation is reconcile/disposition**, preventing completed research from disappearing into transcripts.

### 4. Venture / Customer / Portfolio loop — strategically valuable, correctly deferred

These documents contain a coherent commercial loop that the prior 92-concept index did not expose as first-class mechanisms:

```text
market evidence
  -> OpportunityHypothesis
  -> bounded validation
  -> VenturePlan / mission graph
  -> build + launch
  -> customer/market signals
  -> experiments
  -> KILL / HOLD / IMPROVE / SCALE
  -> certified reusable capabilities
```

This should be preserved because it gives Agent Factory a natural way to create and operate autonomous online businesses later. It should **not** be allowed to jump ahead of the first certified team and real eval evidence.
