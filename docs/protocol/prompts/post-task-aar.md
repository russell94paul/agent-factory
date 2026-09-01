# Post-Task AAR — ⛔ DESIGN

Classifies what happened after a non-PASS outcome.

## INPUT CONTRACT
- the run's events and its contract results
- `docs/protocol/FAILURE_TAXONOMY.yaml`

## OUTPUT CONTRACT
One `failure_family` from the closed set, plus **the rule or observation that produced it**. A bare
family is not acceptable output — `classified_by` is what makes a classification arguable rather
than something a reader must accept.

## STOP CONDITIONS
- ⛔ **`UNCLASSIFIED` requires stating which families were checked and rejected.** "Novel" asserted
  without that census is an unexamined failure wearing a classification.
- ⛔ **Never map to the nearest-looking family.** A misclassified failure is a gap that looks filled,
  which is strictly worse than one you can see.
- ⛔ Do not add a family. One is added when **two** recorded failures share a mechanism *and* a
  repair.

## EVIDENCE REQUIREMENTS
If the failure is worth a durable record, write `docs/findings.d/F<n>-<slug>.md` with all four
mandatory fields — ⚠ the heading must be `### F<n> — title` or the parser cannot see it, which is
F86: the ledger was blind to eight findings for a day, including every correction the boot README
called load-bearing. Then add the finding id to that family's `findings` list in the taxonomy.
