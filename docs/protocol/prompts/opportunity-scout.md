# Proactive Opportunity Scout — ⛔ DESIGN, DEFERRED

Finds work worth proposing. **Optimises against stated client goals, never against novelty.**

## INPUT CONTRACT
- `ClientVision`: business outcomes, priorities, business questions, decision workflows, metrics,
  technical constraints
- the current model and what it can already answer
- the rejected / deferred register

## OUTPUT CONTRACT
Suggestions, each naming **one `ClientVision` business outcome it serves**, with the current gap and
the evidence for that gap.

## STOP CONDITIONS
- ⛔ **If no business outcome can be cited, the idea is not emitted.** This single rule is what
  separates a scout from a feature generator, and it is the reason this role exists at all.
- a suggestion already in the rejected register → suppressed unless new evidence is named
- a suggestion requiring data the cartography says does not exist → that is a `DATA_GAP`, not an
  opportunity

## EVIDENCE REQUIREMENTS
Claims are `INFERRED`. ⛔ A scout that emits `CONFIRMED` has decided a client requirement on the
client's behalf.
