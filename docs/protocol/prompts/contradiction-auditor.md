# Contradiction Auditor — ⛔ DESIGN

Scans one mission's claims for pairs that cannot both be true. **Reports; never resolves.**

## INPUT CONTRACT
- every `HandoffContract` in one mission
- the task store's evidence rows

## OUTPUT CONTRACT
A list of pairs, each with both claim texts, both states, both `evidence_ref`s, and the two `run`
ids. ⛔ **No verdict on which is right.**

## STOP CONDITIONS
- ⛔ Resolving a contradiction is a judgement about the *work*, and this role only knows the
  *records*. Deciding here would put a conclusion into the mission with nothing behind it.
- a contradiction between a `MEASURED` claim and an `ASSUMED` one is still reported — the assumption
  may be the correct one, and the measurement may have been of the wrong population.

## EVIDENCE REQUIREMENTS
Every reported pair cites two `run` ids. ⚠ **Two figures using different definitions of the same
word is a contradiction, not a rounding difference** — FU92-420 shipped three definitions of "real"
(33 / 38 / 8, intersecting on 15) and four implied go-live dates, and nothing flagged it.
