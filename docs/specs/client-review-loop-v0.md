# Client Review Loop V0 — queued capability, not started

**Filed 2026-08-31 from Paul's specification. NOT DESIGNED, NOT BUILT.**

⛔ **Explicitly gated.** *"Do not build UI yet. Do not interrupt the current priority of getting
`marketing-model-reconstruction-v1` into TEST."* This file exists so the specification survives
outside a session transcript. Nothing here has been reconciled against the repo.

`next:` when the TEST candidate exists — **and step one is the inspection, not the design.**

## The objective

Make Client Review a **native phase of Agent Factory**, not a separate UI or application. The UI
becomes a projection of the domain model, built only after the lifecycle works headlessly.

**Success condition:** the Factory can execute a complete client-review decision lifecycle — from
pre-review analysis through approved work — without relying on UI-specific state or on anyone
manually interpreting a chat transcript.

## ⛔ The instruction that governs everything below

> *"FIRST inspect the repo for existing primitives before creating new ones. Do not duplicate an
> existing concept under a new name."*

That is the same rule that has paid every time it was applied this week, and the same trap the
bootstrap pack walked into. Every contract below must be reconciled against what exists **before**
a line is written.

### Leads to verify first — NOT conclusions

Noted from this session's recovery so the next one does not re-derive them. Each is a **lead**;
confirm it in code before building on it.

| The spec asks for | Candidate primitive already here | Verify |
|---|---|---|
| missions / tasks / DAG | `factory/tasks.py` (append-only, evidence-gated close), `.data/tasks.jsonl` | ⚠ ticket-level `blocked_by` is `[]` in all 189 events — the DAG field exists and is unused |
| evidence / provenance | `factory/evidence.py` — classes `TARGET/CONSUMER/REGRESSION/ROLLBACK`, states `ABSENT/ASSERTED/SATISFIED` | close() already refuses without evidence |
| claims / permissions | `factory/claims.py` — `O_EXCL`, three-valued liveness | |
| approval gates | `factory/contract.py` five verdicts; `presets.needs_paul` is **display-only** | ⚠ only `Lane.needs_paul` is enforcing-ish |
| evaluation | `factory/contract.py`, `pbi_contract.py`, `redesign_contract.py` | |
| event / state mechanisms | `factory/events.py` — 9 closed event kinds, terminal kinds must carry a `Verdict` | ⛔ **Do not invent a parallel bus.** `factory/bus.py` is the live channel (5 kinds, ephemeral) |
| knowledge writeback | `docs/findings.d/` read as data by `factory/findings.py`; the wiki | |
| work-item abstraction | `factory/presets.py` (6 ticket types), `factory/registry.py` (shape × layer → workflow) | |
| **NOT present** | no memory system, no vector store, no RAG, no graph db — sole runtime dep is `pyyaml` | measured |

## The eleven contracts, as specified

1. **ReviewCandidate** — `MISSING_INFORMATION · REQUIREMENT_AMBIGUITY · BUSINESS_RULE ·
   DESIGN_DECISION · POTENTIAL_IMPROVEMENT · DATA_GAP · UNUSED_CAPABILITY · SCOPE_QUESTION ·
   TECHNICAL_RISK · UX_OPPORTUNITY · CLIENT_OPPORTUNITY · AC_CLARIFICATION`.
   ⭐ **A ReviewCandidate is NOT a requirement and NOT a ticket.**
2. **ClientQuestion** — `ANSWERED_VERIFIED · ANSWERED_INFERRED · RESEARCH_REQUIRED ·
   DESIGN_REQUIRED · WAITING_ON_CLIENT · CLOSED`. Preserves meeting origin, affected
   model/data components, priority, evidence, verified resolution.
3. **ClientReviewSession** — agenda, candidates, questions, decisions, requirement changes,
   business rules, client preferences, scope changes, action items, model version, TEST
   environment, post-meeting reconciliation state, approval state.
4. **ClientVision** — business outcomes, priorities, business questions, decision workflows,
   analytical capabilities, business rules, metrics, dimensions, technical constraints, UX
   preferences, deferred interests. **Every item carries confidence/provenance and supports
   supersession.**
5. **ScopeDelta** — review may **PROPOSE**; only explicit approval updates approved scope.
   Client review must never silently mutate scope.
6. **TicketProposal** — the required path, and no shortcut through it:
   `evidence → candidate/question → client decision or verified research → impact analysis →
   ticket proposal → human approval → task`.
7. **Research / design escalation** — a question or candidate may spawn an existing Factory
   mission/task for `RESEARCH_REQUIRED` or `DESIGN_OPTIONS_REQUIRED`; the resulting evidence must
   link back to the originating question and be reviewable at the next session.
8. **Review Candidate Pass** — a reusable pre-meeting agent-team workflow. Inputs: current TEST
   model, client vision, confirmed requirements, open questions, scope, historical decisions,
   current implementation, validation results, project evidence. Output: **ranked**
   ReviewCandidates, each carrying `why_flagged · supporting_evidence · client_value_hypothesis ·
   current_state · uncertainty · dependencies · implementation_impact ·
   recommended_client_question`.
   ⛔ **The team may SUGGEST but must never classify its own idea as a client requirement.** A
   skeptical/relevance filter runs before promotion to the review queue.
9. **Post-meeting reconciliation** — provider-neutral intake (live capture, transcript, summary,
   historical state). **No Avoma-specific coupling** unless an adapter already exists. Outputs
   distinguish `DISCUSSED · PROPOSED · CONFIRMED · APPROVED · DEFERRED · REJECTED`.
10. **Events** — observable by a future UI: `review.candidate.created`, `client.question.created`,
    `client.question.answered`, `client.review.started/completed/reconciled`,
    `client.requirement.confirmed`, `client.preference.recorded`,
    `scope.change.proposed/approved`, `research.requested`, `design_options.requested`,
    `ticket.proposed`, `ticket.approved`, `validation.completed`.
    ⛔ Integrate with the existing mechanism; **do not invent a parallel event bus.**
11. **Storage boundary** — LOCAL/TRANSIENT: raw transcripts, provider payloads, active meeting
    state, credentials. DURABLE: approved requirements, decisions, business rules, client
    preferences, scope changes, resolved questions, research conclusions, design decisions, ticket
    provenance, validation evidence.
    ⛔ **Do not commit sensitive raw client material merely to make the workflow persistent.**

## V0 test — before any UI

Simulate one review cycle on the Marketing Model, demonstrating: the pre-review pass generates
candidates; suggestions stay separate from requirements; the client marks one HIGH PRIORITY and one
NOT NEEDED; one question is answered from verified implementation evidence; one becomes
`RESEARCH_REQUIRED`; one becomes `DESIGN_OPTIONS_REQUIRED`; one approved change proposes a scope
delta; the delta requires approval; an approved item produces a `TicketProposal`;
rejected/deferred items remain durable knowledge; `ClientVision` learns the expressed priorities;
and **the next preparation uses those decisions and does not repeat rejected suggestions without
new evidence.**

Produce the resulting artifact/state graph. Build no UI until that lifecycle runs.
