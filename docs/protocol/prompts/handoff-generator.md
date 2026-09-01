# Handoff Generator — ⛔ DESIGN

Turns a finished piece of work into a machine-readable handoff.

## INPUT CONTRACT
- the run's own events, the task contract, the artifacts produced
- ⚠ **NOT the agent's memory of what it did.** Every field must be readable off something on disk.

## OUTPUT CONTRACT
A `HandoffContract v1` that passes `HANDOFF_CONTRACT.schema.json` with all six write-time refusals
satisfied.

## STOP CONDITIONS
- ⛔ `not_done` cannot be produced → stop. An absent `not_done` is nobody having asked; `[]` is an
  assertion. Only one of those is acceptable output.
- a `verification.verdict` of `PASS` that did not come from a `GreenContract` → ⛔ refuse to emit it
- an `artifacts_to_consume` ref that does not resolve → fix it or drop it; never emit it

## EVIDENCE REQUIREMENTS
`evidence[]` rows carry a class (`TARGET` / `CONSUMER` / `REGRESSION` / `ROLLBACK`) and a basis
(`MEASURED` / `DERIVED` / `ASSUMED`). ⚠ Four rows of the same class satisfy a count and prove almost
nothing — see `factory/evidence.py`. An analysis has nothing to roll back; use `evidence.ANALYSIS`
as a declared policy rather than filing an empty `ROLLBACK` row.
