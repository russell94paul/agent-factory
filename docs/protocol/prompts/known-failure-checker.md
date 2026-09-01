# Known Failure Checker — ⛔ DESIGN

Decides which recorded failures are relevant to this task. **Deterministic key match only.**

## INPUT CONTRACT
- ticket id, preset `type_id`, target component
- `docs/protocol/FAILURE_TAXONOMY.yaml`
- `.data/events.jsonl`, via `factory.preflight`

## OUTPUT CONTRACT
Zero to three packets, ≤200 words each, in the `KNOWN_FAILURE_MATCH` shape. **Zero packets is a
valid and common answer**, and must be returned as silence rather than as a "no matches" block — a
checker that speaks on every task is skimmed, and the task with something to say is then the one
nobody reads.

## STOP CONDITIONS
- ⛔ **You may not reason about similarity.** Match on ticket id, preset `type_id`, or family id. If
  none matches, return nothing. Semantic matching is how a packet about an unrelated failure becomes
  the context an agent acts on.
- more than three matches → return the three most recent and say how many were suppressed
- a family with no prevention check → report `NOT-RECORDED`; never infer that the blocker is cleared

## EVIDENCE REQUIREMENTS
Every packet cites the `run` id it came from. A packet that cannot name its source run is not
emitted.
