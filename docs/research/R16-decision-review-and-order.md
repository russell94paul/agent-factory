# R16 — Attack the eighteen decisions, and the order we intend to do them in

**Status: NOT DISPATCHED.** Written 2026-08-23. Paste the whole file and attach
`docs/research/R16-evidence-pack.md`. The answer is filed at
`docs/research/answers/R16-answer-decision-review-and-order.md`.

**Runs on:** DEEP_RESEARCH
**Depends on:** R13, R14

⚠ **The hold is lifted, and here is the basis so it can be argued with.** This file used to say
*"must not be sent yet — hold until R13 run 2 and R14 have both landed and been reconciled."*
Measured 2026-08-23: both are `ANSWERED` (`R13-answer-…-run2.md`, `R14-answer-…`), and
`synthesis.unsynthesised()` is empty with SYNTHESIS.md naming R13 22 times and R14 5 times.

⛔ **That last check is the weak one and this file will not pretend otherwise.** It asks whether the
synthesis *mentions* an id, not whether anyone engaged with it — the same check went green over R8's
answer while the document said three times that R8 was still outstanding. **"Landed" is measured;
"reconciled" is inferred from mention counts.** If R14's five mentions are passing references, this
pass will review a record that has not absorbed it.

## Run log

| Run | Dispatched | Outcome |
|---|---|---|
| 1 | **blocked** | Waited on R13 run 2 and R14. Hold lifted 2026-08-23 — both answered, both named in SYNTHESIS.md. |

---

## Who we need you to be

**Someone whose job is to find the one decision that is wrong, in a set that looks right.**

Thirteen research passes have answered. Their conclusions are reconciled into a single document and
have hardened into **eighteen numbered actions**. Each was written the day its own pass landed. **None
was written knowing what the others would say.** Nobody has ever checked that they are consistent
with each other, that the order is right, or that the thing we intend to do first is the right first
thing.

You are not reviewing the research. You are reviewing **the decisions the research produced, and the
sequence** — which is a different job and has never been done.

---

## 0. ⛔ The trap in this brief, stated so you can avoid it

**You are the least independent pass we will ever run.** Every previous one had its own footing —
one read repositories, one read the sandbox literature, one read the field. **You are reading our
conclusions.** If you work only from the synthesis you will be grading our homework with our answer
key, you will agree, and the agreement will be worth nothing.

Two rules follow, and they are the whole design of this pass:

1. **The answers directory is attached, not just the synthesis.** When a decision cites a pass, go
   and read what that pass actually said. **Several of our decisions summarise answers that do not
   quite support them, and finding those is most of the value here.**
2. ⭐ **You are scored on disagreements found, not on endorsement.** An answer that endorses all
   eighteen actions is a **failed run** and we will treat it as one. This is the same rule we hold
   our own gates to: `0 of 22 gate events were ever a refusal`, and a check that has never refused
   has not been shown to work. **If you genuinely cannot fault a decision, say which evidence would
   change your mind** — that is a finding too.

---

## 1. The eighteen decisions

Reconciled from thirteen answers, in `SYNTHESIS.md` §12.8, §13.7 and §14.7.

**From §12.8 (R10, R11, R12):**
1. Do not adopt switchboard on this evidence; retire the no-terminal constraint deliberately or re-ask.
2. Build four liveness states into `factory/sessions.py`.
3. Surface the agents' `needs` field ourselves — no external tool reads it.
4. Record the guardrail gap as a real absence: a pre-action layer, distinct from the readiness gates.
5. Skills over corpus — the wiki's leverage is procedure synthesis, not retrieval.
6. `runs.py` already implements cost-paired-with-outcome; the observability gap is narrower than claimed.

**From §13.7 (R8, R15):**
7. Do not adopt a desktop app. **Make the existing tracker instant** — thread the server, parallelise the probes.
8. Containerise agent execution **on one machine**, before any cloud step.
9. Adopt the mandatory-clone rule: no `CREATE OR REPLACE` on a shared schema without an explicit clone.
10. Restate the unattended goal as a **30–45 minute unbroken run**, not an unattended migration.
11. Read switchboard's `open-terminal` handler and settle the R12/R15 contradiction.
12. Take R8's isolation argument; leave its scheduling and messaging recommendations.

**From §14.7 (R13):**
13. **Platform: a VS Code extension**, not a desktop app.
14. Build the notification channel first.
15. Stop surveying orchestration topologies — seven checked, none moves the cap.
16. Config hash: adopt the OTel GenAI field set.
17. Discount R13's migration section — it guessed our surfaces.
18. Settle the terminal question as a decision and delete it from every prompt.

---

## 2. What we want, in priority order

### 2.1 ⭐ The incoherences — and here is one, so you can calibrate

Decisions written on different days do not know about each other. **We have already found one and we
are giving it to you deliberately, so that finding *only* this one counts as failing.**

> **7** says *do not build a desktop app; make the existing Python tracker instant.*
> **13** says *the platform is a VS Code extension.*
>
> If the platform is a VS Code extension, is making the Python tracker fast the right investment or
> throwaway work? Do they sequence (fast tracker now, extension later), or does one obsolete the
> other? **The synthesis never says, because the two were written a section apart.**

**Find the others.** Pairs to look at with suspicion, without limiting yourself to them: 2 and 13
(liveness states in a Python module, when the surface is moving to an extension); 3 and 14 (the
`needs` field and the notification channel are arguably one piece of work described twice); 8 and 10
(containerising on one machine, versus a target of 30–45 minute runs — does one enable the other, or
are they unrelated?); 1 and 18 (do not adopt switchboard *pending* a constraint decision, versus
settle that constraint and stop asking — is 1 already resolved by 18?).

### 2.2 The order

We intend to do them roughly in the order listed. **That order is an artefact of when each pass
answered, not a plan.**

Give us the sequence you would actually do, and for each of the first five: **what it unblocks, what
it costs, and what breaks if it is done third instead of first.** Where two items are the same work
described twice, say so and merge them.

⚠ **One measured fact should shape this and may not be visible in the decisions themselves:** our
bottleneck is not the agents. Two pull requests sat **green and mergeable for 6 and 9 days**, and
four agents were blocked on written questions nobody read. Any ordering whose first three items do
not move that number should say why.

### 2.3 The decisions that overstate their evidence

For each of the eighteen, check the pass it came from. We know of at least one case where a decision
is firmer than the answer beneath it. **Name every decision whose supporting answer is weaker than
the decision implies, and say what the honest version would be.**

### 2.4 What is missing

Eighteen actions came out of thirteen passes about architecture, sandboxes, sessions, UI and
provenance. **What is not on this list that should be?** Be specific — "you have no plan for X" is
useful only if X is real. Look especially for the thing every pass assumed somebody else was
handling.

---

## 3. Deliverable

1. **The incoherences**, ranked, each with the two decisions and what to do about it.
2. **The order you would actually do them in**, with the first five justified.
3. **Decisions that overstate their evidence**, with the honest version.
4. **What is missing.**
5. **The one decision you think is most likely to be wrong**, and what would prove it.

**Length: shorter than the synthesis.** If your answer is longer than the record it reviews, you have
restated rather than reviewed.

## 4. Constraints on any recommendation

Windows-first · small team, no platform team to operate anything · three concurrent lanes today ·
per-secret human approval is a hard rule · no unlabelled stale numbers · the existing instrument panel
is added to, never removed · **the terminal is an escape hatch and that is settled — do not reopen
it**, though you may say if you think decision 18 was reached badly.

## 5. Tier every claim

`OBSERVED` — you read the source or the answer · `REPORTED` — a credible postmortem or paper ·
`MARKETED` — a vendor says so and nobody independent confirmed it · `INFERRED` — your reasoning.

**Two warnings earned the hard way in this programme.** A `MARKETED` claim may not be a design
premise. And **do not cite evidence about us that you have not been given** — a previous pass
supported a recommendation with *"in our user studies we found…"*, and there were no user studies.
If you want a fact about our operators or our data, mark it `NOT-SUPPLIED` and ask.
