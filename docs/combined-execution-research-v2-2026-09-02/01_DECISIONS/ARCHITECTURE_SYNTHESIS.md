# Architecture Synthesis — what to build, reuse, defer

## 1. North-star framing

Treat **Agent Factory** as an engineering platform for measurable, evidence-backed agent work and an **Agentic IDE / Command Surface** for operators. It may eventually compile and operate richer synthetic organizations, but do not make a novelty claim around an "organization OS" or organizational compiler category.

The research reconciliation is decisive on one point: the **category framing is occupied/prior art; several mechanisms remain useful**. Build the mechanisms that solve measured problems. Do not inherit a research programme merely because its vocabulary is attractive.

## 2. Canonical runtime model

Keep these existing truths authoritative:

- `TaskStore` = canonical work/event record.
- dependency/block events = canonical task-DAG history.
- work projection = derived operability/readiness view.
- claims/session inventory = live ownership/liveness.
- evidence classes + task close rules = outcome proof.
- Switchboard = projection + action surface, never a new database.

A new mission layer should initially be a **preset/compiler into TaskStore**, not a competing mission store.

### Minimal P0 abstraction

```text
Mission Preset
    + Execution Preset/Team
    + Operator inputs
           |
           v
Mission Preset Adapter
           |
           v
Canonical TaskStore work + dependency events
           |
           +--> existing readiness / coordination / claims / sessions
           |
           +--> existing START SYNCED / deploy mechanisms
           |
           +--> evidence + artifacts
           |
           v
       Switchboard projection
```

## 3. Goal-aware adaptive orchestration

Build this as a **thin control loop** over the existing work projection.

### P0 control loop

```text
observe canonical state
    -> derive READY work
    -> filter by mission/target
    -> filter by policy + conflicts + concurrency
    -> prioritise using existing coordination logic
    -> start allowed work via existing guarded start mechanism
    -> observe completion / failure / human gate
    -> recompute
```

### Three modes

- `MANUAL`: nothing starts automatically.
- `GUARDED`: starts only when the existing guarded policy says the human is not substituting for a missing control.
- `AUTO`: automatically starts policy-allowed READY work, still respecting hard stop policies and concurrency.

The existing P1 UI already exposes these modes. P0 must make them operational.

## 4. Separate Goal, Mandate, and Success Contract

Do **not** put deadlines/permissions inside the existing falsifiable GreenContract. The Agent Army evidence model correctly distinguishes mission authority/budget/deadline from success evidence.

Use a lightweight **ExecutionMandate** for scheduler context:

```yaml
execution_mandate:
  goal_id: marketing-meeting-ready
  target_work_id: marketing-001-meeting-ready
  deadline: 2026-09-02T12:00:00-07:00
  mode: GUARDED
  max_parallel: 3
  scope_profile: deadline_p0
```

Success remains on tasks/evals. A deadline changes scheduling urgency; it does not change what PASS means.

## 5. Dynamic critical path, without overclaiming

There are currently two graph scales in the repo:

1. readiness-gate graph (`board.DEPENDS`);
2. task/work dependency graph recovered from append-only task events.

Do not pretend they are one graph tonight. For mission execution, compute critical path/ancestor closure over the **task graph** to the selected target node. The existing gate critical path remains a platform-readiness diagnostic.

### `RUN DAG`

Start every policy-allowed READY node within the selected mission/run, limited by concurrency and conflicts.

### `RUN CRITICAL PATH`

Start only policy-allowed READY nodes that are ancestors of the selected target milestone. Deprioritise unrelated work; do not delete it.

## 6. Scope degradation

The corpus found this is genuinely absent. Do **not** invent automatic scope dropping under deadline pressure tonight.

P0 behaviour:

- priority and scheduling may adapt;
- non-critical work may be paused/deprioritised;
- success criteria may not be silently weakened;
- skipping/dropping a required node needs a human-authored decision with provenance.

Future design can add `MUST / SHOULD / COULD` or equivalent importance classes plus authority rules, but only after the approval/governance work is settled.

## 7. Organizations and hierarchy

Do not encode a mandatory five-level ladder such as Agent → Team → Team Manager → Master → Army into the runtime ontology.

Prefer:

- canonical Agent and Team concepts;
- organizations as configurable graphs/topologies later;
- supervisor/manager tiers as optional topology roles/presets;
- display hierarchies as UI lenses, not runtime invariants.

The frontier L1–L8 ladder is useful as an exploration/maturity taxonomy, not as a required implementation sequence.

## 8. Org-IR / organization compiler

**Defer generic Org-IR.** The current P0 need is a narrow preset-to-task compiler. Revisit Org-IR after:

- at least one real agent run exists;
- RB-01/RB-02 prior-art/trace work is complete;
- a second workload proves current presets cannot represent the needed variation;
- the model-binding/revalidation issue is addressed.

## 9. Evolution / hyper-tuning

Keep the concept, defer the machinery.

Any future archive of winning agent/team configurations must include model/tool/config bindings and a revalidation cadence. A "best organization" is not a timeless asset. The current evidence says winning placement can flip across model families.

## 10. Evidence/knowledge model

The sibling repo's strongest directly useful concept is to **not collapse Observation, Claim, Evidence and Knowledge into one memory object**. Provenance needs a root/group identity so repeated copies of one source cannot masquerade as corroboration.

Do not migrate the whole evidence schema tonight. Post-deadline, reconcile terminology first and add the smallest provenance field(s) that prevent duplicate evidence-chain counting.

## 11. Mission Assurance Receipt

Adopt as a **projection**, not a subsystem. It has excellent value-to-machinery ratio because most inputs already exist.

Required extra rule: a receipt must include **limits/unmeasured**, or refuse to imply assurance outside the evaluated envelope.

Implement after the Marketing path if time permits; otherwise first post-deadline UI enhancement.

## 12. Self-maintenance

Use bounded self-hosting only:

```text
certification loss
    -> quarantine
    -> route to last-certified/fallback
    -> human-visible incident
```

No autonomous code edits in the self-repair path until the system can independently evaluate its own changes outside the actor's authority boundary.
