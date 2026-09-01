# Client Review — Live Meeting Runbook

> ⭐ **Updated 2026-08-31 against the implementation.** The flow below is unchanged; what follows
> is how to actually open it, and the three places the built page differs from the assumptions.
>
> **Open it — one command, as of 2026-09-01:**
> ```bash
> python scripts/meeting_ready.py --open
> ```
> It compiles from canonical state, renders, runs the meeting-readiness gate, and loads the built
> page in a real browser before telling you whether it is safe to open. Exit 0 means safe; exit 1
> names exactly what is blocking. The refresh contract is `06-D5-REFRESH-CONTRACT.md`.
>
> ⭐ **Statuses on the page are no longer typed.** Milestones, next steps, risk state and evidence
> paths are derived from `.data/tasks.jsonl` and the mission record. When a task closes, the page
> changes on the next regeneration with no edit to the narrative. Ten hand-typed statuses were
> measured contradicting the record on 2026-09-01 — see the refresh contract.
>
> The longhand still works, and is what the one command runs:
> ```bash
> python -m factory.client_review missions/client-review-v1/reviews/navira-marketing-model.yaml \
>   --mission .data/missions/marketing-model-reconstruction-v1.json \
>   --out docs/artifacts/client-review-navira.html
> ```
>
> ⛔ **`--tasks` is gone on purpose — do not add it back.** It used to read
> `--tasks .data/tasks.jsonl`, relative to the working directory. Run from the primary checkout
> that is right; run it from any worktree and it resolves to a `.data/` holding no task store, and
> the artefact reported **all four delivered outcomes as UNSUBSTANTIATED** with freshness
> `UNAVAILABLE` — a client document understating fully evidenced work, produced by the command
> this runbook told you to run, at the moment it told you to run it. Measured 2026-09-01.
>
> It now resolves through `factory.repo`, so it is correct from anywhere. `--mission` is still
> passed explicitly, because omitting it means *"there is no mission record"* — a different
> statement from *"I could not find it"* — and a relative `.data/...` path is now resolved against
> the shared root as a fallback.
>
> Two safety nets sit behind that, and neither depends on you getting the directory right:
> `factory.client_review.publication_block()` inspects the FINISHED document, and `--out` refuses
> to write when the result understates its own evidence. If you ever see that refusal, the fix is
> the working directory, not `--force`.
>
> Then open `docs/artifacts/client-review-navira.html` in a browser. **It is a single static
> file — no server, no build, no network call at render time.** If every service in the estate is
> down, it still opens and still tells the truth about when it was last verified. Regenerate it
> shortly before the meeting so the freshness stamp reads `LIVE`.
>
> **Live Meeting mode:** the button top-right, the `m` key, or `?mode=meeting` in the URL. It
> raises the whole type scale (17px → 20px at the root, so headings scale too), narrows the
> measure, and hides operator-only detail. The choice persists in `localStorage`.
>
> **Three differences from the original assumptions:**
>
> 1. **There is no "since your last review".** This is the first review of this project, so the
>    hero says so explicitly rather than inventing a delta. The `05:15` section below still works;
>    the `01:15` framing should be *"here is what we completed"*, not *"since last time"*.
> 2. **Evidence drill-down is per-outcome, not a separate hunt.** Each delivered outcome carries
>    its own `Proof it works` disclosure. Open one from within the DELIVERED section at `02:00`;
>    the standalone EVIDENCE section is the index, not the demo.
> 3. **The left margin carries the grade.** Every outcome shows `EVIDENCE VERIFIED` / `CLAIMED` /
>    `NO EVIDENCE` and whether *you asked for this* or *we proposed this*. That margin is the
>    strongest thing on the page — point at it at `02:00`. A claim whose artefact does not resolve
>    renders as `UNSUBSTANTIATED` and cannot show a green word; that is the mechanism, and it is
>    worth one sentence to the client.

## Goal

Present the delivery as a transparent, evidence-backed process rather than as a collection of engineering tools.

Target duration: approximately 5–7 minutes for the core walkthrough.

## 00:00 — Open Client Review

Suggested framing:

> This is the current delivery state for your project. Rather than asking you to follow engineering tools, we translate the work into the outcomes, evidence, decisions and next steps that matter to you.

Show:

- project/client;
- overall status;
- review readiness;
- outstanding client decisions;
- last verified timestamp.

## 00:30 — What You Asked For

Show the compiled requirement / Intent Contract.

Cover:

- objective;
- requested outcome;
- major acceptance criteria;
- important assumptions.

Suggested framing:

> This is our current understanding of the outcome you asked us to deliver. It gives both our team and the delivery system one explicit definition of success.

## 01:15 — Since Your Last Review / Delivered

Show the meaningful outcomes completed.

Avoid reading raw tasks or commits.

Suggested framing:

> These are the changes that materially affect your outcome since the last review.

## 02:00 — Evidence

Open one strong evidence drill-down.

Suggested framing:

> We don't want a green status badge to mean "trust us." Each major delivery claim can be tied back to validation evidence.

Show, where available:

- successful execution;
- test results;
- fresh data/output;
- schema/parity validation;
- deployment verification.

## 03:00 — Decisions Required

Open the client decision section.

Suggested framing:

> This is the only thing currently requiring your attention. Everything that can safely continue without this decision keeps moving.

Show:

- decision;
- recommendation;
- alternatives;
- impact;
- blocking/non-blocking state.

## 04:00 — Risks / Blockers

Show only meaningful client-facing risks.

Suggested framing:

> We also surface anything that could affect delivery rather than leaving it buried in an engineering tool.

For each important risk, explain:

- impact;
- mitigation;
- whether client action is required.

## 04:45 — What's Next

Show the next meaningful outcomes.

Suggested framing:

> Once the current work and any required decision are complete, these are the next outcomes—not just the next internal tasks.

## 05:15 — Acceptance

Show review/acceptance state.

Suggested framing:

> When the delivery reaches acceptance readiness, this same view becomes the evidence-backed acceptance record.

## Demo discipline

During the live meeting:

- stay in the client-safe view;
- avoid unnecessary internal-agent detail;
- do not over-explain the agent architecture unless asked;
- use evidence rather than unsupported confidence language;
- if state is stale, say so and show the last verified timestamp;
- do not rely on a fragile live integration if cached verified evidence is available;
- keep the client focused on outcomes, decisions and next steps.

## Strong closing idea

> The goal is that you shouldn't need to chase us for status. You should be able to see what was requested, what is complete, what proves it, anything we need from you, and exactly what happens next.
