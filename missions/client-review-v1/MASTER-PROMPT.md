# MASTER PROMPT — Client Review v1 Implementation Mission

You are working inside the existing **Agent Factory** repository.

This is a focused implementation mission for a component in the existing client delivery process.

## Read first

Read every file in:

```text
missions/client-review-v1/
```

Read them in this order:

1. `00-MISSION.md`
2. `01-PRODUCT-REQUIREMENTS.md`
3. `02-CLIENT-REVIEW-SPEC.md`
4. `03-DATA-CONTRACT.md`
5. `04-DEFINITION-OF-DONE.md`
6. `05-CLIENT-REVIEW-DEMO-RUNBOOK.md`

Treat those files as the product intent and delivery constraints for this mission.

---

# Objective

Deliver a reliable, polished **Client Review & Acceptance** vertical slice within Agent Factory.

The immediate use-case is a real client-facing review workflow, potentially including a live meeting presentation.

The desired client journey is:

```text
WHAT YOU ASKED FOR
        ↓
WHAT WE DELIVERED
        ↓
PROOF IT WORKS
        ↓
WHAT WE NEED FROM YOU
        ↓
RISKS / BLOCKERS
        ↓
WHAT HAPPENS NEXT
        ↓
REVIEW / ACCEPTANCE
```

The goal is not maximum feature count.

The goal is to make Agent Factory turn internal delivery execution into a transparent, evidence-backed, low-friction client experience.

---

# Critical scope rule

DO NOT re-process, re-synthesize or re-architect the entire Agent Factory / Agent Army research corpus as a prerequisite.

This repository has evolved and may contain newer concepts than older research artifacts.

For this mission, use **targeted delta reconciliation only**.

Start from:

1. the actual current repository implementation;
2. current architecture/navigation documentation;
3. the current UI;
4. existing mission/project state;
5. evidence/provenance mechanisms;
6. approval/decision mechanisms;
7. event/state APIs;
8. metrics/observability;
9. memory/client context;
10. any existing delivery or client-review components.

Only then consult research/docs that are directly relevant to this feature.

Prefer recent/current architecture over superseded documents.

If you find meaningful architectural contradictions, record them for later reconciliation. Do not turn this mission into a platform redesign unless an existing architectural conflict genuinely blocks implementation.

---

# Phase 1 — Repository reconnaissance

Before making substantial changes, inspect actual implementation—not documentation alone.

For every Client Review requirement classify existing support as:

```text
REUSE
EXTEND
ADD
DEFER
```

Specifically identify existing primitives for:

- project/mission state;
- ticket/intake data;
- Intent Contracts or semantic contracts;
- client/project context;
- evidence;
- provenance/content origin;
- approvals/approval tokens;
- task DAGs;
- event bus/SSE;
- metrics;
- Prefect/run state;
- test/eval results;
- deployment verification;
- risks/blockers;
- memory;
- notifications;
- UI/project views;
- acceptance/completion state.

Prefer reuse.

Do not introduce another:

- mission state system;
- orchestration engine;
- event bus;
- evidence store;
- memory service;
- approval system;
- client database;

unless the existing architecture demonstrably cannot support the requirement.

---

# Phase 2 — Establish the Client Review read model

Implement one coherent client-facing data contract based on:

`03-DATA-CONTRACT.md`

Treat Client Review as a projection/read model over existing Agent Factory state.

Target transformation:

```text
Agent Factory internal state
           ↓
Client Review assembler
           ↓
client visibility / confidentiality filtering
           ↓
claim grounding
           ↓
canonical client_review model
           ↓
UI
```

Do not make the Client Review model a competing source of truth.

Map existing state into it.

If the repository already has a compatible read model, extend it rather than duplicating it.

---

# Phase 3 — Client safety and grounding

Client Review is a trust surface.

Every major client-facing status statement must derive from real state or evidence.

Never present unsupported:

- SUCCESS;
- VERIFIED;
- DEPLOYED;
- ACCEPTED;
- HEALTHY;
- ON TRACK;
- READY;

as factual system state.

Represent freshness explicitly where useful:

```text
LIVE
LAST_VERIFIED
STALE
UNAVAILABLE
```

Do not expose:

- credentials;
- secrets;
- internal prompts;
- hidden reasoning;
- internal-only postmortems;
- unnecessary infrastructure details;
- private agent scratch state.

If a UI currently mixes operator-only and client-safe data, introduce an explicit filtering/projection boundary.

---

# Phase 4 — Implement the core presenter journey

Optimize the interface for this exact sequence:

## 1. What You Asked For
Show objective, requested outcome, important requirements, assumptions and acceptance criteria.

## 2. What We Delivered
Show meaningful client-facing outcomes, not raw commits/task noise.

## 3. Proof It Works
Allow evidence drill-down for major delivered outcomes.

## 4. What We Need From You
Show only genuine client decisions, including recommendation, alternatives, delivery impact and blocking state.

## 5. Risks / Blockers
Translate meaningful delivery risk into client-understandable language.

## 6. What's Next
Show outcomes, not merely internal tasks.

## 7. Review / Acceptance
Expose readiness and acceptance state in an auditable way.

A client should understand the essential project state in approximately 30 seconds.

---

# Phase 5 — Live Meeting mode

If the current UI architecture allows it without destabilizing the core, implement a presentation-safe mode.

Live Meeting mode should:

- increase readability;
- reduce internal navigation/noise;
- hide operator/admin controls;
- preserve evidence drill-down;
- emphasize outcomes and decisions;
- avoid continuous distracting animation;
- be suitable for screen sharing.

Do not sacrifice reliability for theatrical effects.

Use `05-CLIENT-REVIEW-DEMO-RUNBOOK.md` as the target presenter flow.

---

# Phase 6 — Demo resilience

A live meeting must not fail because one integration is temporarily unavailable.

Design graceful degradation.

Where appropriate:

- retain last verified state;
- show verification timestamp;
- distinguish stale from live;
- preserve verified evidence;
- make refresh failures non-destructive;
- allow missing optional fields without breaking the page.

Never fake live data.

---

# Phase 7 — Quality and verification

Before declaring the mission complete:

1. run relevant existing tests;
2. add tests for any new Client Review assembler/read-model behavior;
3. test missing and partial data;
4. test sensitive-data filtering;
5. test evidence mapping;
6. test decision state;
7. test freshness state;
8. test the actual presenter journey;
9. inspect the UI at common desktop screen-sharing sizes;
10. fix client-visible rough edges relevant to a live meeting.

Do not weaken existing tests merely to make the new implementation pass.

---

# Definition of done

Use `04-DEFINITION-OF-DONE.md` as the authoritative scope checklist.

Anything listed as Nice-to-have is secondary.

If time/scope pressure exists, cut novelty before cutting:

1. reliability;
2. evidence grounding;
3. client safety;
4. clarity;
5. core presenter journey.

---

# Required implementation notes

As you work, maintain a concise mission record containing:

## REUSED
Existing Agent Factory primitives used unchanged.

## EXTENDED
Existing primitives extended.

## ADDED
Truly new code/components.

## DEFERRED
Ideas intentionally excluded from v1.

## ARCHITECTURE CONFLICTS
Important discrepancies or outdated assumptions discovered that should be handled in the later research/architecture reconciliation.

Do not derail the current mission to fix unrelated architectural issues.

---

# Final deliverables

When implementation is complete, provide:

## 1. Implemented
What now works end-to-end.

## 2. Reused
Which existing Agent Factory components were leveraged.

## 3. Extended / Added
What changed and why.

## 4. Deferred
What was deliberately excluded.

## 5. Tests / verification
What was run and what passed.

## 6. Live-meeting readiness
Any issue that could affect presenting this to a client.

## 7. Presenter runbook
Update `05-CLIENT-REVIEW-DEMO-RUNBOOK.md` if the actual implementation differs from the initial assumptions.

## 8. Architecture conflicts discovered
Anything to feed into the later Agent Factory / Agent Army delta-reconciliation mission.

## 9. Next five improvements
Rank by:

```text
client-delivery impact × implementation confidence
```

Do not rank by novelty.

---

# Final operating principle

The Client Review should make this statement true:

> The client does not need to chase the delivery team for status or decipher internal engineering tools. They can see what they requested, what has been delivered, the evidence that proves it, anything requiring their decision, meaningful risks, what happens next, and when the outcome is ready for acceptance.

Build the smallest reliable vertical slice that makes that experience real.
