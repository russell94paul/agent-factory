# Client Review v1 — Delivery Mission

## Objective

Deliver a production-quality Client Review component within Agent Factory.

This component sits inside the broader client delivery process.

Its purpose is to transform internal Agent Factory execution state into a clear, trustworthy, client-safe review experience.

The immediate target is a usable vertical slice suitable for demonstrating during a live client meeting.

## Do NOT

- redesign Agent Factory;
- create a second orchestration system;
- recreate existing memory, event, approval, evidence, or mission primitives;
- re-process the entire Agent Army research corpus;
- introduce speculative abstractions unrelated to Client Review;
- expose raw internal agent reasoning or sensitive system information;
- prioritize visual novelty over a stable meeting experience.

## Do

- inspect the current repository;
- reuse existing primitives;
- identify relevant recent research only where necessary;
- reconcile this feature with the current architecture;
- produce a polished client-facing experience;
- preserve evidence and provenance;
- make all client-facing status statements grounded in actual project state.

## North-star user experience

A client should be able to open the Client Review and understand within approximately 30 seconds:

1. What did we ask for?
2. What has been completed?
3. What has changed?
4. Is it working?
5. What evidence proves that?
6. Are there risks or blockers?
7. Is anything required from us?
8. What happens next?

## Immediate success criterion

A presenter can confidently use the Client Review during a live client meeting without needing to switch repeatedly between internal engineering tools.
