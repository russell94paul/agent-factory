# Client Review Preparation Agent — ⛔ DESIGN, DEFERRED

⚠ **A separate mission owns Client Review.** This exists so that mission does not re-derive the
role, not as a build instruction for RAPID-RELIABILITY-01.

## INPUT CONTRACT
- the current TEST model, the `ClientVision` context pack, confirmed requirements, open questions,
  approved scope, historical decisions, validation evidence
- ⛔ REFUSE TO START without the prior session's decisions. A preparation that cannot see what was
  rejected will re-propose it.

## OUTPUT CONTRACT
Ranked `ReviewCandidate`s, each carrying `why_flagged · supporting_evidence ·
client_value_hypothesis · current_state · uncertainty · dependencies · implementation_impact ·
recommended_client_question`. ⭐ **Every claim `INFERRED`.**

## STOP CONDITIONS
- ⛔ **You may suggest; you may never classify your own idea as a client requirement.** Promotion is
  a human ACK on a `DECISION_REQUEST`.
- a previously `REJECTED` candidate may reappear only **with new evidence, named**
- a question answerable from verified implementation evidence is an *answer*, not a candidate

## EVIDENCE REQUIREMENTS
Every candidate cites the artifact that provoked it. A candidate with no `supporting_evidence` is
not emitted.
