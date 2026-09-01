# Client-facing capabilities — ⛔ DESIGN, DEFERRED. Spec only, no UI.

**Deferred from this mission by the approval.** Recorded so the backend decisions in this pack are
made with their eventual consumers visible — not as a build queue.

⚠ Every one of these is **gated on the same precondition**: a run that can reach a real PASS. Today
`first_pass_green_rate` is `0/8` with `instrument_live=False`. A client-facing feature built over an
instrument that has never registered a green would be showing a client our measurement gap.

---

### 1 · Verified Meeting Copilot
**Client experience** — in the meeting, every answer badged `VERIFIED` / `INFERRED` / `UNKNOWN`, each
with its source.
**Backend** — claim states + `ContextPack` + `evidence_ref`.
**Trust rule** — ⛔ `UNKNOWN` is never rendered as an answer; it opens a research task.
**MVI** — a CLI over one model's evidence. **Mockable** — the live transcript intake.
**Why it is not decorative** — it can say *"I don't know, and here is the mission that will find
out."* A system that cannot say that is a guessing machine with good manners.

### 2 · Live Change Impact
**Client experience** — "what breaks if I change this dimension?"
**Backend** — dependency edges + `evidence_class=REGRESSION`.
**Trust rule** — ⚠ shows only **enumerated** dependents and states its coverage; never implies
completeness.
**MVI** — a text impact report. **Mockable** — the graph rendering.
**Why** — `redesign_contract` R2 already requires a rename to carry enumerated, rewritten
dependents. The data is real, not aspirational.

### 3 · Proactive Review Candidates
**Client experience** — a ranked list before the meeting, each item with evidence and a client-value
hypothesis.
**Backend** — the Review Candidate Pass + a skeptical filter.
**Trust rule** — ⛔ every candidate `INFERRED`; the ranking basis is published.
**MVI** — ranked markdown. **Mockable** — the ranking model.
**Why** — it suppresses previously-rejected items *unless new evidence exists*. That is what makes
it a briefing rather than a nag.

### 4 · Why-Does-This-Exist Traceability
**Client experience** — click any measure, see the decision, the meeting and the approval that
created it.
**Backend** — the `TicketProposal` provenance chain.
**Trust rule** — pre-protocol objects show `NOT-RECORDED`, never a reconstructed guess.
**MVI** — `git log` + a task-chain query. **Mockable** — the click surface.
**Why** — it answers the question that ends every model-handover argument.

### 5 · Design Option Comparison
**Client experience** — two or three designs side by side, each with what it can and cannot answer.
**Backend** — `keel` + the D2 analytical-question catalogue + per-option verdicts.
**Trust rule** — ⛔ options must differ **at the grain**, not cosmetically.
**MVI** — a markdown table (D3 already produces this shape). **Mockable** — the diff view.
**Why** — the trade-off, not the recommendation, is the only part a client can actually decide on.

### 6 · Meeting-to-TEST Loop
**Client experience** — "you asked for this on the 12th; it is in TEST; here is the evidence."
**Backend** — the full chain + `evidence_class=CONSUMER`.
**Trust rule** — ⛔ requires a **rendered-surface** artifact, not a passing query. GP-293 passed DAX
parity while every visual showed "Error loading data".
**MVI** — evidence links on the ticket. **Mockable** — the timeline.
**Why** — it closes the loop the client actually experiences as trust.
