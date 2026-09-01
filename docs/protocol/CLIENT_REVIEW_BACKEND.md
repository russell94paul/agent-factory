# Client review backend — ⛔ DESIGN, DEFERRED. A separate mission owns this.

**Do not build from this file.** RAPID-RELIABILITY-01 was explicitly told not to expand into the
Client Review work, and the dedicated mission is being handled separately. This exists for one
narrow purpose: to show that the eleven contracts in `docs/specs/client-review-loop-v0.md` **need
no new mechanism** — so that mission starts from a mapping rather than from a blank page, and does
not invent a parallel event bus or a second findings store on its way in.

## The mapping

| spec contract | carried by an existing primitive |
|---|---|
| `ReviewCandidate` | a `Task` (parent = the review session) whose contract JSON carries `candidate_type` and `ranked_by`. ⭐ Its claims are `INFERRED` and carry no `evidence_ref` — **the schema is what stops a suggestion becoming a requirement**, not a convention |
| `ClientQuestion` | a `Task` + a claim state. `ANSWERED_VERIFIED` = `CONFIRMED` with `evidence_ref`; `ANSWERED_INFERRED` = `INFERRED`; `RESEARCH_REQUIRED` / `DESIGN_REQUIRED` = `UNKNOWN` + a child task; `WAITING_ON_CLIENT` = `block()` |
| `ClientReviewSession` | a parent `Task`; agenda = its children; decisions = `HANDOFF` bodies |
| `ClientVision` | a `ContextPack` of kind `client-vision`. `ContextRef` already carries source + checked-on and defaults to `UNVERIFIED`; supersession is a new ref, which is exactly what §4 asks for |
| `ScopeDelta` | `DECISION_REQUEST` → human `ACK` → `HANDOFF` carrying `permits`. **PROPOSE cannot mutate scope: only an ACKed `DECISION_REQUEST` writes the approved-scope evidence row** |
| `TicketProposal` | a `Task` that cannot close without an `evidence_class=TARGET` row naming the approving decision |
| research / design escalation | `TaskStore.create(parent=question_id)` + `block()`. `dispatch.py`'s five states already separate *unsent* from *in flight* — the distinction §7 needs |
| §10 events | new entries in `events.KINDS` — ⛔ **one stream, as §10 itself demands** |
| §11 storage boundary | LOCAL = `.data/` (gitignored, `bus.py`'s rule); DURABLE = `docs/` + the task store |

## The two lifecycles, as event sequences

```
client asks → client.question.created            (claim state: UNKNOWN)
  A. evidence exists  → CONFIRMED + evidence_ref → question.answered(VERIFIED)
  B. no evidence      → research.requested → child task → GreenContract verdict
                      → HANDOFF back, evidence_ref set → CONFIRMED
                      → the next session's ContextPack carries it        ← the loop closes

agent suggests → review.candidate.created         (claim state: INFERRED, always)
  → skeptical filter (relevance + duplicate against prior REJECTED)
  → client prioritises → scope.change.proposed
  → impact analysis    → ticket.proposed
  → DECISION_REQUEST → human ACK → scope.change.approved → Task → TEST
```

⭐ **No suggestion can silently become a requirement, and it is enforced twice.** The claim state is
`INFERRED` with no `evidence_ref`, so the handoff schema refuses `CONFIRMED`; and promotion requires
a human `ACK` on a `DECISION_REQUEST`. A rejected candidate stays durable and rides in the next
session's `ContextPack`, which is what stops the same suggestion being re-proposed without new
evidence.

## ⚠ Corrected premise, carried here so the mission does not inherit it

`docs/specs/client-review-loop-v0.md` states that ticket-level `blocked_by` is `[]` in all 189
events and the DAG field is unused. **That was true when filed and is now false** — the store holds
25 `block` events from `marketing-model-reconstruction-v1`. The correction has been applied in that
file itself; it is repeated here because a mapping that inherits a retired premise builds on it.

Regenerate:
```bash
python -c "import json;print(sum(1 for l in open('.data/tasks.jsonl',encoding='utf-8') if l.strip() and json.loads(l)['kind']=='block'))"
```
