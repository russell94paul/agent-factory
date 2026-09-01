# Handoff Receiver / ACK Checker — ⛔ DESIGN

Runs the six deterministic discriminators. **Judgement is not required and is not wanted.**

## INPUT CONTRACT
- one `HandoffContract`
- the filesystem, to resolve refs and shas
- upstream claims in the same mission, to detect contradiction

## OUTPUT CONTRACT
Exactly one state — **and the name of the discriminator that fired.**

| state | test |
|---|---|
| `NACK_INCOMPLETE` | an `outputs[].ref` does not resolve on disk |
| `NACK_STALE` | a referenced artifact's sha does not match the recorded one |
| `NACK_CONTRADICTORY` | two `CONFIRMED` claims, same subject, opposite states |
| `NACK_UNVERIFIED` | `verification` is `UNMEASURABLE`/`NOT_RUN` while behavior is `CONSUME` |
| `ACK_WITH_WARNINGS` | resolves, but a load-bearing claim is `INFERRED`/`ASSUMED` |
| `ACK` | none of the above fired |

## STOP CONDITIONS
- ⛔ Do not ACK to be agreeable and do not NACK to look rigorous. If no discriminator fires, the
  answer is `ACK`.
- a claim whose state was upgraded across the boundary with no new `evidence_ref` →
  `NACK_CONTRADICTORY`

## EVIDENCE REQUIREMENTS
⭐ A NACK is a caught defect, not a mission failure. It increments `handoff_intercepts` — an
**outcome** metric, which is what lets a defect-count activity metric be registered against it
without `factory.metrics` raising `GoodhartViolation`.
