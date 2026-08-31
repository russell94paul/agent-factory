# Agent Communication & Interaction Protocol — Design Target

## Why this exists

A multi-agent organization needs more than task assignment. It needs bounded, typed, observable interaction without either:

- everyone chatting with everyone; or
- every interaction bottlenecking through one LLM manager.

This document defines the **research/design target**, not a frozen proprietary standard.

## Core primitives to investigate

```text
announce_presence
announce_availability
declare_capability
declare_confidence
request_help
offer_support
request_review
publish_observation
publish_evidence
publish_claim
challenge_claim
broadcast_warning
propose_plan
propose_subtask
accept_task
handoff_task
subscribe
unsubscribe
share_artifact
publish_learning
synthesize_state
close_loop
```

## Typed envelope candidate

Every interaction should eventually be representable with:

```text
message_id
mission_id
organization_id
sender
recipients / topic
type
priority
created_at
expires_at
correlation_id
causation_id
content_ref / payload
confidence
provenance_refs
authority_scope
ack_policy
visibility
```

## Communication classes

- directive;
- question;
- observation;
- evidence;
- claim;
- warning;
- proposal;
- decision;
- handoff;
- state update;
- learning / after-action record.

## Required properties

1. **Observable** — every material coordination event can be traced/replayed.
2. **Bounded** — subscriptions, priorities, expiries, and rate limits avoid message storms.
3. **Permissioned** — sender/receiver authority and knowledge access are explicit.
4. **Correlated** — events connect to mission/task/artifact/evidence lineage.
5. **Asynchronous-first** — agents do not need simultaneous context windows.
6. **Interruptible** — high-priority warnings can wake the right participant.
7. **Anti-loop** — deduplication, hop/causation tracking, TTL and acknowledgement semantics.
8. **Human-readable when needed** — important events surface in Mission Control.

## Research boundary

Before creating a custom wire protocol, compare existing standards/patterns including MCP, A2A-style agent interaction, pub/sub/event buses, actor messaging, blackboard/shared-workspace systems, workflow events, and tracing standards.

A custom protocol is justified only for a concrete missing semantic that cannot be expressed by adapting an existing standard.
