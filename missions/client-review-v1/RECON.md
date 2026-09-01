> ## Where this landed, and why the commit message does not say so
>
> **Client Review v1 is committed in `b28c334`** — a commit titled *"docs(findings): three
> evidenced findings filed, and the R3 identity prepared"*, which describes a different
> workstream. The content is correct and complete; the message is another session's.
>
> **What happened, recorded because it will happen again.** This checkout is shared by four
> sessions. I staged my eleven files and, in the seconds before my own `git commit` ran, a
> concurrent session committed — taking everything in the shared index, mine included, under its
> message. This is the exact hazard `boot-prompts/README.md` documents: *"Staging by path does
> not protect you — another session's `git commit` takes whatever you have staged."* Staging by
> path is not the control. **The worktree is the control.**
>
> **Not repaired by rewriting history.** `b28c334` is on shared `main` with other sessions
> actively working; rebasing or amending it to split the commit would rewrite work that is not
> mine. The record is corrected here instead, where the mission's own documentation lives.
>
> Client Review v1 in `b28c334` is exactly these paths — everything else in that commit belongs
> to the findings/R3 workstream:
>
> ```
> factory/client_review.py
> factory/client_review_render.py
> tests/test_client_review.py
> missions/client-review-v1/**
> docs/artifacts/client-review-navira.html
> ```

# Phase 1 — Repository reconnaissance

**Measured 2026-08-31, `main @ ddea66d`.** Every row below was checked in code, not read from a
document. Commands are given so nothing here has to be trusted.

⛔ This file records what EXISTS. It records no implementation, because none has started.

## 0. The headline: the repo already has a Client Review spec, and it disagrees with the pack

`docs/specs/client-review-loop-v0.md` was filed **today** (`44bf6b8`) from Paul's own
specification. It is not superseded, and it is not the same document as this pack.

| | `client-review-loop-v0.md` (in repo) | this pack |
|---|---|---|
| shape | **decision lifecycle**, headless | **presentation read model**, UI |
| core objects | ReviewCandidate, ClientQuestion, ClientReviewSession, ClientVision, ScopeDelta, TicketProposal (11 contracts) | `client_review` projection: intent / delivered / evidence / decisions / risks / next / acceptance |
| sequencing | ⛔ *"Do not build UI yet."* *"Build no UI until that lifecycle runs."* | Phases 4–6 are the UI |
| the client | a party who **answers questions and approves scope changes** | a party who **reads status and approves one decision** |

They are not contradictory in intent — the pack's `decisions[]` is a thin projection of the v0
spec's ClientQuestion + ScopeDelta. They contradict on **sequencing**, and the pack is newer and
has a live client meeting behind it.

⚠ The overlap is not free. The pack's model has **no** ReviewCandidate, no ClientVision, no
supersession, and no PROPOSE/APPROVE split on scope. Building the pack's model as specified and
later adding the v0 lifecycle underneath it is possible; building the pack's model *as the system
of record for decisions* would collide with v0 contract 5 — "review may PROPOSE; only explicit
approval updates approved scope".

## 1. Classification of every pack requirement against real code

`REUSE` = exists and fits · `EXTEND` = exists, needs a field/mode · `ADD` = genuinely new ·
`DEFER` = out of v1

| Pack requirement | Existing primitive | Verdict |
|---|---|---|
| project/mission state | `.data/missions/*.json` + `factory/tasks.py` `TaskStore` (append-only, `.data/tasks.jsonl`) | **REUSE** |
| ticket/intake data | `factory/presets.py` (6 ticket types), `factory/control.py:53` `Ticket` | REUSE |
| Intent Contract / semantic contract | ⛔ **nothing named this.** `grep -ril intent_contract factory/ scripts/` returns empty. Nearest is the mission spec markdown plus `contracts.{id}` in the mission JSON, which is a *task* contract (model/effort/claim/evidence_required), not a client intent | **ADD** |
| client/project context | `factory/context.py` (context packs) | EXTEND |
| evidence | `factory/evidence.py` — classes `TARGET/CONSUMER/REGRESSION/ROLLBACK`, states `SATISFIED/ASSERTED/ABSENT`, `USABLE = ("MEASURED", "DERIVED")` | **REUSE** — this is the grounding primitive the pack asks for |
| provenance / basis | `evidence.py` MEASURED / DERIVED / ASSUMED; mission JSON carries `estimate_basis: ASSUMED` | REUSE |
| approvals / approval tokens | ⚠ `factory/claims.py` is a **lock**, not an approval. `presets.needs_paul` is **display-only**; only `Lane.needs_paul` gates anything (tracker `/start-all`). No approval token, no audit record of an approval | **ADD** |
| task DAG | `tasks.py` has `blocked_by`, and ⭐ **the mission uses it** — D1→D5 is a real chain, D1 blocked by `[R1, R2, R3]`. (Empty at *ticket* level, which is where the earlier "unused" reading came from.) | EXTEND |
| event bus / SSE | `factory/events.py` — append-only ledger, **9 closed kinds**, 3 terminal kinds must carry a `Verdict`. `factory/bus.py` — 5 ephemeral kinds. ⛔ **No SSE, no websocket, no EventSource anywhere** (`grep -ril 'text/event-stream\|websocket\|EventSource' factory/ scripts/` returns empty). The tracker is poll/refresh | REUSE (ledger) · DEFER (push) |
| metrics / observability | `factory/metrics.py`, `factory/readiness.py` (the gate board) | REUSE |
| Prefect / run state | `factory/runs.py`, `.data/runs.jsonl`, `factory/live_probes.py` | REUSE |
| test / eval results | `factory/contract.py` five verdicts, `connector_contract.py`, `pbi_contract.py` (M1–M12), `redesign_contract.py` (R1–R4) | **REUSE** — the strongest asset for "Proof It Works" |
| deployment verification | `factory/verifiers.py` registry — ⚠ **2 of 6 presets** have a runnable verifier | EXTEND |
| risks / blockers | `docs/findings.d/` read as data by `factory/findings.py`; `readiness.py` gates | EXTEND (internal-voiced; needs translation) |
| memory | ⛔ **none.** No memory service, no vector store, no RAG, no graph db. Sole runtime dep is `pyyaml` | **DEFER** |
| notifications | `scripts/hooks/lane-attention.py` (operator desktop only) | DEFER |
| UI / project views | `scripts/local_tracker.py` — 2,882 lines, stdlib `http.server`, **9 tabs, all operator-facing**: Tickets, Gates, Goals, Roadmap, Flow, Lanes, Sessions, Research, Handoff. Plus static `tracker.html` and `docs/artifacts/{agent-factory,orchestration-bench,project}.html` | **EXTEND** — a client-safe projection is a new surface on an existing server |
| acceptance / completion state | `tasks.py` terminal states `DONE` / `ABANDONED` with `EvidenceRequired` on close. No client acceptance event | **ADD** |

## 2. What the pack assumes that is not here

Stated plainly so the design does not inherit a hypothesis:

1. **"the current UI"** — there is one, and it is entirely operator-facing. There is no client-safe
   view, and therefore no existing filtering boundary to extend. The pack's Phase 3 ("if a UI
   currently mixes operator-only and client-safe data, introduce a boundary") applies in a stronger
   form: the tracker is 100% operator-only, so the boundary is a new surface, not a filter over an
   old one.
2. **memory / client-context service** — absent, measured.
3. **live push (SSE)** — absent, measured. Freshness must be timestamp-based, not stream-based.
   That is fine, and arguably better for the pack's own Phase 6 demo resilience.
4. **an approval mechanism** — absent. `needs_paul` is display-only outside `Lane`.
5. **an Intent Contract object** — absent under that or any name.

## 3. The only real project state available to populate the view

`.data/missions/marketing-model-reconstruction-v1.json` — the first and only mission.
Spec: `docs/specs/marketing-model-reconstruction-v1.md`. Subject is **Navira** (GEP is the Jira
project and the client; Navira is the modelled entity).

```
R1 ──┐
R2 ──┼──▶ D1 ──▶ D2 ──▶ D3 ──▶ D4 ──▶ D5
R3 ──┘
```

State as measured:

| task | state | evidence on disk |
|---|---|---|
| R1 stakeholder / client evidence | produced output | `docs/evidence/marketing-model-v1/R1-stakeholder-evidence.md` (43,110 b) — ⚠ **untracked** |
| R2 repo + wiki diff | produced output | `docs/evidence/marketing-model-v1/R2-repo-wiki-diff.md` (43,901 b) — ⚠ **untracked** |
| R3 Snowflake cartography | ⛔ **BLOCKED** | credential rotation decision pending — `boot-prompts/mission-wave1-checkpoint-2026-09-01.md` §1 |
| D1–D5 | not started | — |

⚠ Every `estimate_basis` in that mission is `ASSUMED`. Any completion-percentage or
delivery-confidence figure derived from those estimates is `ASSUMED` and must render as such — the
pack's own rule against "opaque AI-generated health scores unless their basis is inspectable".

## 4. Architecture conflicts, for the later reconciliation mission

- **C1 — sequencing.** `client-review-loop-v0.md` forbids UI before the headless lifecycle runs;
  this pack is UI-first. The pack is newer and meeting-driven, so it proceeds; the v0 lifecycle is
  neither deleted nor contradicted, and the v1 read model must not become the system of record for
  decisions or scope.
- **C2 — two vocabularies for one domain.** `decisions[]` (pack) versus
  ClientQuestion + ScopeDelta + ReviewCandidate (v0). If v1 names its objects after UI elements,
  the later mission inherits a rename. Mitigation: name each v1 field after the v0 concept it
  projects.
- **C3 — `next[].dependency` is authored prose, not the real edge.** ⚠ Corrected after measuring:
  `blocked_by` is *not* unused — the mission's D1→D5 chain is real, and D1 is blocked by
  `[R1, R2, R3]`. The gap is the other direction: v1's `next[].dependency` is a hand-written
  string that could drift from the store's actual edges. Deriving it from `blocked_by` is the
  obvious v1.1, and it is listed in the next-five.
- ⛔ **C6 — the mission record and the task store disagree about what the work is.** The mission
  task has **10** children; the record declares **8** labelled tasks. R1 and R2 each exist twice —
  the labelled task, plus an unlabelled duplicate created later that carries the evidence rows.
  Counting children scored the client-facing figure at **40%**; counting the declared labels
  scores **25%**. The read model now counts labels and says so, but the duplication itself is a
  real defect in the mission record and should be reconciled at source.
- **C4 — approval has no record.** The pack's requirement that "acceptance must become an auditable
  delivery event" cannot be satisfied by any existing mechanism. It needs a new event kind, and
  `events.KINDS` is a **closed** tuple whose terminal members must carry a `Verdict`. Adding
  client-review kinds touches a deliberately sealed enum.
- **C5 — the pack has no ReviewCandidate.** The v0 spec's sharpest rule — *"the team may SUGGEST
  but must never classify its own idea as a client requirement"* — has no home in the v1 model.
  Anything the factory proposes would land in `decisions[]` indistinguishable from something the
  client actually asked for. That is a client-safety hole, not a feature gap.

## 5. Mission record

### REUSED — unchanged
- `factory/evidence.py` — `SATISFIED/ASSERTED/ABSENT` and `USABLE = (MEASURED, DERIVED)` are
  imported directly as the grounding vocabulary rather than restated, so the two cannot drift.
- `factory/tasks.py` `TaskStore` — the source of task state, evidence rows and their bases.
  Read-only; the read model never writes to it.
- `.data/missions/marketing-model-reconstruction-v1.json` — the declared task population.
- `docs/evidence/marketing-model-v1/*.md` — the artefacts the client drills into.

### EXTENDED
- Nothing. **No existing file was modified.** The slice is additive, which is why the regression
  surface is the whole suite passing unchanged rather than a diff review.

### ADDED
- `factory/client_review.py` — the assembler and read model. Allow-list client boundary, the
  guarded-word gate, four-state freshness, computed acceptance, `origin`.
- `factory/client_review_render.py` — self-contained HTML renderer; no backend, no build, no
  runtime fetch. Evidence drill-down is `<details>`, so it works with JS disabled.
- `missions/client-review-v1/reviews/navira-marketing-model.yaml` — the authored narrative.
- `tests/test_client_review.py` — 35 tests, weighted toward making each guard *fire*.
- `docs/artifacts/client-review-navira.html` — the generated review.

### DEFERRED
- memory / client-context service (absent; not needed for v1)
- SSE / live push (absent; timestamp freshness is sufficient and more demo-resilient)
- the v0 lifecycle's 11 contracts (ReviewCandidate, ClientVision, ScopeDelta, TicketProposal, …)
- an acceptance **event** — computing acceptance state is done; writing it into `events.KINDS`
  is not, because that tuple is deliberately closed and its terminal kinds must carry a `Verdict`
  (see C4). Opening it needs a decision, not a patch.
- a `/review` route on `scripts/local_tracker.py` — the static file is strictly more
  demo-resilient, and the tracker is a contended 2,882-line file.
