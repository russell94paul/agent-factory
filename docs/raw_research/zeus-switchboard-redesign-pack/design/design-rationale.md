# Design rationale and feature roadmap

## Outcome

The Switchboard is designed around the operator's three recurring questions:

1. What needs my attention now?
2. What is each mission doing, why, and with what evidence?
3. What can I communicate or decide without losing context?

The answer is a single command surface: queue on the left, execution in the center, and
communications/decisions on the right. This layout is deliberately asymmetric. The live
mission has the largest area; navigation and communication remain available without
becoming equal-weight dashboard cards.

## Research translated into the design

- Command-oriented navigation: global search and action routing from one keyboard surface.
- Multiple views over one underlying work state rather than separate copies of tasks.
- Inbox mechanics: fast scanning, directional navigation and an explicit attention queue.
- Human-plus-agent delegation: the human remains accountable while an agent performs work.
- Editor mechanics: reusable prompt snippets, task presets and an integrated runtime dock.
- Workflow observability: ordered event history, retries, failures, recovery and checkpoints.

Reference products and official documentation used during design:

- Linear search: https://linear.app/docs/search
- Linear inbox: https://linear.app/docs/inbox
- Linear concepts and views: https://linear.app/docs/conceptual-model
- Linear agent delegation: https://linear.app/docs/assigning-issues
- VS Code snippets: https://code.visualstudio.com/docs/editing/userdefinedsnippets
- VS Code agent/session documentation: https://code.visualstudio.com/docs

## Productivity features in this pack

### Implemented interaction shells

- Command palette and keyboard-first routing.
- Focus mode that removes side-channel noise without changing the mission.
- Mission composer with auto-formation, priorities, budget and human gates.
- Typed communication targets plus explicit context attachments.
- Inline approval with operator identity and audit-language feedback.
- Live formation with semantic edge motion and progressive node detail.
- Unified activity/runtime dock for logs, terminal, metrics and context.
- Three coherent theme presets, density control and reduced motion.

### Next features after real data is connected

| Priority | Feature | Why it matters |
| --- | --- | --- |
| P0 | Persistent handoff capsules | New sessions receive only relevant, typed mission state. |
| P0 | Attention router | Ranks approvals, blocks, budget drift and stale missions by operator cost. |
| P0 | Evidence-aware approvals | Decision view shows claim, diff, tests, provenance and rollback together. |
| P1 | Formation compare | Compare team blueprint versions by outcome, cost, latency and rework. |
| P1 | Prompt/template arsenal | Versioned reusable mission, handoff and intervention commands. |
| P1 | Replay and time travel | Reconstruct why the system made a decision at any checkpoint. |
| P1 | Communication lenses | Filter one thread by decisions, handoffs, evidence, agents or humans. |
| P2 | Predictive intervention | Forecast likely gate failure, budget overrun or context exhaustion. |
| P2 | Spatial fleet map | Useful only once many concurrent missions exceed the queue/list model. |
| P2 | Voice command/briefing | Hands-free summaries using the same event stream and captions. |

## Features intentionally avoided

- A literal battlefield or office simulation: spatial metaphor adds navigation cost.
- Constant particles and glow: motion is reserved for causality and current execution.
- A free-form graph editor in the primary workflow: versioned formation configuration belongs
  in a dedicated constructor surface.
- Autonomous destructive controls: abort, publish, merge and deploy require backend policy.
- Hidden context inference: communication attachments must be inspectable and permissioned.

## Quality target

The implementation follows the Living Systems quality categories: technical fidelity,
simulation clarity, visual system, meaningful motion, accessibility and performance. Since
real architecture data was unavailable, the graph is explicitly labeled illustrative; this
avoids presenting a mock topology as measured system truth.
