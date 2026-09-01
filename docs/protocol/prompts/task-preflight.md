# Task Preflight Agent — ⛔ DESIGN

Runs before an implementer is dispatched. Assembles what this task must not walk into.

## INPUT CONTRACT
- the task contract (`.data/missions/<id>.json` row: `resource_claim`, `access`, `capability_class`,
  `evidence_required`, `expected_output`)
- `factory.preflight.check(ticket, {"preset": …})` — this ticket's own prior failures
- the task's `blocked_by` set from `TaskStore`
- ⛔ REFUSE TO START if `expected_output` names a path whose parent does not exist, or if any
  `blocked_by` entry is still open.

## OUTPUT CONTRACT
A `HandoffContract v1`, `required_receiver_behavior: VERIFY_THEN_CONSUME`, carrying `failures[]`
from the preflight match, `dangerous_assumptions[]`, and `permits` copied **verbatim** from the task
contract — never widened.

## STOP CONDITIONS
- the task contract declares `access: WRITE` and names no `resource_claim`
- a prior attempt's family is `retryability: NEVER` and its prevention check reports
  `STILL_PRESENT` — ⛔ **report it; do not refuse.** V0 is WARN-ONLY
- any credential would be required

## EVIDENCE REQUIREMENTS
Emits no evidence of its own. Every claim it passes on keeps the state it arrived with — ⛔ a
preflight that upgrades an `INFERRED` claim to `CONFIRMED` is the UNKNOWN→FACT defect.
