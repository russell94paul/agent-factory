# Boot — Intake Platform: full review, and lock the design

**Written:** 2026-08-29 late. **For:** the next session.
**Goal of that session:** stop designing. Lock design, tracker, roadmap, dependencies, use-cases and
diagrams into one artifact Paul can follow while he works, and leave nothing still "to be decided".

`next:` **Start with the divergence pass (step 1). Do not re-plan.** The plan exists and is
published; what it lacks is a check against the code and a locked roadmap.

---

## Read first

- **Board + plan (published, state persists):** https://claude.ai/code/artifact/11564c9c-0aa2-4369-9911-2e2ad82cfbaf
- **Written plan:** `docs/CLIENT-INTAKE-PLATFORM-PLAN.md`
- **Tickets:** `.data/tasks.jsonl` — CIP-01 … CIP-20 exist (42 events)
- **Prompts already written:** `docs/CORPUS-AND-DESIGN-PROMPT.md` (in-repo pass),
  `docs/EXTERNAL-REVIEW-PROMPT.md` (external, incl. Variant B for the public repo)
- **Absorption backlog:** `docs/absorption-backlog.md` — AB-01…AB-19
- **The gates:** `../aldc-launchpad/workflow-kit/README.md`

⛔ **Do not open a new research lane.** Eighteen passes exist and nineteen conclusions are
unabsorbed. Any new question must name the answer that failed to cover it, by file and section.

---

## What is already true — do not rediscover it

- **The plan is written and published.** Six phases, 20 tickets, 10 pitfalls, 4 trade-off tables,
  three diagrams. It does not need rewriting; it needs checking and locking.
- **agent-factory is healthy.** 304 tests pass; `certify blueprints/windsorai_client_a.yaml
  --calibrate` returns A1–A12 PASS and labels itself REPLAYED. Verified 2026-08-29.
- **The repo was redacted.** Clients are `CLIENT-A` / `CLIENT-B`; the blueprint was renamed.
  Commit `62597d8` on `feat/readiness-generator`. ⚠ **Not pushed**, and **git history still
  carries the original names.**
- **The public repo is a skeleton.** `russell94paul/agent-factory` `main` is 18 files, last moved
  2026-08-20, **157 commits behind** the working branch. Anything browsing `main` sees almost
  nothing.
- **The Engineering Tracker (Part A) is approved but unbuilt** — `data/tracker/` holds one
  PBI-EVAL file. That is why the board is an artifact for now.

---

## The external review did NOT land

`docs/reviews/external/deepseek.md` is **0 bytes**.
`deepseek_w_SYNTHESIZE-ctx.md` is an acknowledgement of receiving SYNTHESIS.md, not the review —
no D0 divergence rows, no mermaid, no ticket JSON, no D5. It ends with a menu of offers.

**Two of its claims were verified anyway, and the result is instructive:**

| Claim | Verdict |
|---|---|
| "the eval corpus is one file, **6,747 bytes**" | ✅ exact — matches the pre-redaction byte count measured independently. It read real content. |
| "`g_version_hash_is_complete` could never pass — U+0008 in regex" | ⚠ **real, and already fixed.** `0b41f88` (08-21) had `rf"{d}"`; `13e746e` (08-23) fixed it to `rf"\b{d}\b"` under the title *"a gate that could never pass"*. |

⭐ **That second row is the risk in miniature: a STALE verdict pointing the wrong way.** It read
`SYNTHESIS.md`, which describes the pre-fix state, and reported a closed defect as live. **When the
real review arrives, check the direction of every divergence before believing either side.**

If the response is still missing, its best follow-up offer was #3 — *"a diff between what
SYNTHESIS.md claims is built vs what the code actually contains"* — which is D0, the deliverable
that never came. The other three offers are restatements of things that already exist.

---

## The session, in order

### 1. Divergence pass — the review that did not happen
Do it in-repo, where the filesystem is available and an external model's blind spot is not.
For each load-bearing claim in `SYNTHESIS.md` and `docs/CLIENT-INTAKE-PLATFORM-PLAN.md`:
`CLAIM / SOURCE / REALITY / VERIFIED_AT / VERDICT / IMPACT`.
Start with the five named in `EXTERNAL-REVIEW-PROMPT.md` Variant B. **Report direction** — our doc
stale, or the reviewer stale.

### 2. Lock the design
The plan's L1–L5 layers become decisions with owners and no open questions. Anything still open
becomes a ticket, not a paragraph. **Output: a decision record, not more prose.**

### 3. Roadmap + dependencies, visually
The board has dependency data (18 edges, all resolving) but renders them as text. Draw the real
graph — critical path, what unblocks what, what can run in parallel. **Geometry computed from the
dependency data, not eyeballed.**

### 4. Use-cases
Six, in the estate's proven form: *today* vs *after*, each with the measured number that makes the
difference real. Cover at minimum: client kickoff, a new connector, a client disputes a number,
a spec change mid-build, resuming after a gap, and running a review.

### 5. Diagrams
L1–L5, one per layer, inline SVG, `built` / `proposed` / `rejected` distinguished and legended.
L4 must draw **any path that bypasses a gate**. L5 must keep the evaluator **outside** the loop.

### 6. Fold it all into the published board
Republish to the **same URL** so Paul's saved ticket states survive. The board is the thing he
follows while working — every section must answer "what do I do next" without a second document.

---

## Constraints

- **Republish, never re-create.** Use the existing artifact URL; a new one loses his board state.
- **Every number carries the command that regenerates it.** `workflow-kit/measure.py` is the
  pattern; there are almost no hand-typed figures in the current board, deliberately.
- **Label basis everywhere** — MEASURED / DERIVED / ASSUMED / EXTERNAL / NOT-SUPPLIED.
- **The board mirrors, never owns.** Tickets live in `.data/tasks.jsonl`.
- **Ask before committing.** Paul approves commits.

---

## Open decisions Paul has not made

1. **Push the redaction?** It is committed locally and unpushed. Pushing renames a file an external
   model may be mid-way through citing.
2. **Remove the isolation comment?** `blueprints/windsorai_client_a.yaml:56-57` still describes a
   real data-isolation weakness (one key returning every client's accounts) on a public repo.
3. **Which pilot client and connector** for CIP-03. Nothing downstream can start without it.
4. **Does the public repo stay public**, given `main` is a skeleton and the working branch is where
   everything lives.

---

## Status — honest

- ✅ Plan written, board published, 20 tickets in the store, three diagrams drawn.
- ❌ **No ticket has been started.** All 20 are `todo`.
- ❌ The external review never delivered; D0 is still owed.
- ❌ Redaction unpushed; git history still carries client names.
- ❌ L1/L2/L5 layers are designed, not built. The questionnaire — the single highest-leverage
  artefact, worth 70–80% vs 30–40% spec completeness — does not exist yet.
