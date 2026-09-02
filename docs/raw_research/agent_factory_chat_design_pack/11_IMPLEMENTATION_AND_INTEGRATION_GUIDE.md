# 11 — Implementation & Integration Guide

## Not an implementation commitment

This pack is intended to inform the next Agent Factory architecture/design reconciliation.

## Recommended ordering

### Phase 0 — Domain/state model
Before world rendering, ensure stable typed entities/events for:
- campaign,
- mission/operation,
- objective,
- organization node,
- team,
- agent,
- assignment,
- decision,
- communication,
- handoff,
- artifact,
- dependency,
- context packet,
- resource,
- approval,
- evaluation,
- incident,
- failure family,
- recurrence,
- doctrine,
- experiment.

### Phase 1 — Serious Mission Command Console
Build/strengthen:
- mission list,
- DAG/timeline,
- attention queue,
- agent/team state,
- approvals,
- artifacts,
- communications,
- replay,
- metrics,
- intervention controls.

### Phase 2 — Coordination intelligence
Implement and evaluate:
- target lock,
- reinforcement routing,
- collision detection,
- smart handoffs,
- logistics/preflight diagnosis,
- autonomy levels,
- recurrence analysis.

### Phase 3 — Spatial prototype
Prototype only high-value interactions:
- Satellite/Surveillance Mode,
- semantic zoom,
- Front Line,
- supply/logistics visualization,
- formation editor,
- communication overlay.

### Phase 4 — Gamified world
Add:
- animated HQs,
- persistent presence,
- ranks,
- callsigns,
- social interactions,
- world events,
- humorous ambient storytelling.

### Phase 5 — Autonomous Advanced Projects Command
Only after strong:
- provenance,
- evaluation,
- replay,
- isolation,
- budget controls,
- objective versioning,
- failure classification,
- doctrine registry.

## Shared state, two UIs

Required architecture:

Domain/Event State
→ Command Console projection
→ Battlefield projection

World actions:
Battlefield gesture
→ typed command
→ permissions / Rules of Engagement
→ orchestration service
→ event
→ both UIs update.

Do not build a second hidden “game truth”.

## Organizational model

Use parent-linked configurable organization nodes.

Avoid fixed assumptions like:
`Agent -> Team -> Army`.

Allow arbitrary organization grammar and runtime task forces.

## Failure recurrence integration

Persist:
- incident identity,
- failure fingerprint,
- family membership,
- prior response,
- recurrence index,
- preventive knowledge available,
- knowledge retrieval/delivery outcome,
- prevention outcome.

This data becomes valuable for:
- health dashboards,
- Advanced Projects Command,
- doctrine updates,
- simulations,
- team/config optimization.

## Existing Agent Factory mapping

Likely integration points from the current platform:
- task DAG service → Operations / Battle Plans
- approval tokens → Command Authorization / ROE
- agent effectiveness → force performance
- semantic contracts → objective/metric semantics
- cost baselining → logistics/resources
- semantic memory → Military Intelligence
- auto-learner → AAR / doctrine candidate pipeline
- team/presence workers → Army-world presence
- SSE event bus → world event stream
- preflight → Logistics Health
- versioned team blueprints → Doctrine / Force Generation
- eval harness → Training & Evaluation Range
- mission history → Ghost Battalion / case retrieval
- failures → Threat/Recurring Threat system

## Key technical principle

**Game mechanic = projection of domain state.**

Examples:
- smoke/fire: failed or degraded operation,
- queue: throughput congestion,
- severed supply: missing dependency/context/credential,
- fog: uncertainty,
- returning threat: recurrence,
- traffic between units: communications,
- promotion/certification: passed evaluation.

## Build-kill discipline

Do not implement a world feature because it is cool.
For each feature define:
- operator task,
- conventional baseline,
- world interaction,
- measurable hypothesis,
- usability risk,
- safety risk,
- instrumentation,
- graduation threshold.
