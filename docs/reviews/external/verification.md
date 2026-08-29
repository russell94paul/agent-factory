# Verification — DeepSeek external review, 2026-08-29

Checked in-repo before any of it was ingested, because an external model cannot see the filesystem
and misattributed citations are the known failure mode of an external pass — not fabricated
conclusions.

**Source:** `deepseek.md` (33,677 chars, 535 lines).
**Prompt:** `docs/EXTERNAL-REVIEW-PROMPT.md`, including Variant B for the public repo.

## Did it deliver?

| Deliverable | State |
|---|---|
| D0 divergence rows | ✅ 12 items, real file:line citations |
| D1 absorption verdicts | ✅ 22 AB references |
| D2 diagrams | ✅ 5 Mermaid blocks, L1–L5 |
| D3 optimisations | ✅ 26 items |
| D4 ticket JSON | ✅ **valid JSON**, 15 items CIP-21…CIP-35, exact schema, no id collisions |
| D5 what I could not judge | ❌ **missing** |

D5's absence matters more than it looks: it is the section that would have said where the model was
guessing. Its absence is consistent with the labelling problem below.

**It read the right ref.** D0 opens *"Branch: `feat/readiness-generator` (157 commits ahead of
`main`)"* — the follow-up correcting it away from the skeleton `main` landed.

## Claims verified against the code

| # | Claim | Verdict | How |
|---|---|---|---|
| 1 | corpus is one file, **6,747 bytes** | ✅ **CONFIRMED** | exact match to an independent measurement taken before redaction |
| 2 | `test_eval_can_fail` never loads the corpus | ✅ CONFIRMED | no `corpus` reference in the file |
| 3 | `FACPR` absent from `metrics.py` | ✅ CONFIRMED | `grep -c` → 0 |
| 4 | `deploy.py` / `tasks.py` / `metrics.py` / `evals.py` have no live callers | ✅ **CONFIRMED** | `RepoDeployer` has **zero** references outside `factory/deploy.py`; the other three are imported only by `factory/demo.py`, which nothing imports |
| 5 | `g_version_hash_is_complete` could never pass — U+0008 in regex | ⚠️ **STALE, WRONG DIRECTION** | real defect, **already fixed**: `0b41f88` (08-21) had `rf"{d}"`, `13e746e` (08-23) fixed it to `rf"\b{d}\b"` under the title *"a gate that could never pass"* |
| 6 | the 41.7% figure reads as internal measurement | ◐ **PLAUSIBLE, not confirmed** | `factory/worktrees.py:3-4` attributes it to *"R5 from measurement"* — R5 is a research answer, so the provenance is stated; the wording is ambiguous rather than wrong |

### The finding worth acting on

**#4 is the most valuable thing in the pass.** `deploy.py` implements per-session budget caps and a
retry ledger — `AttemptLedger` exists specifically because *"stage a fresh budget and it
re-dispatched all night"*. The live launch path is
`scripts/local_tracker.py → _launch_script() → .ps1 → bare claude` and never touches any of it.

That is the same shape as the `jq` guard in `workflow-kit`: real code, correctly written, wired to
nothing, and indistinguishable from working until someone greps for callers.

### The finding that shows the risk

**#5 is a stale verdict pointing the wrong way.** It read `SYNTHESIS.md`, which describes the
pre-fix state, and reported a closed defect as live. When an external pass and our docs disagree,
**check which side is stale before believing either.** This will happen again.

## Two proposed tickets REJECTED, in writing

The prompt's rule 2 was *"do not propose anything already built."* Both of these were.

### CIP-22 — "Make `claims.claim()` atomic with `O_CREAT|O_EXCL`" — REJECTED

Already implemented. `claim()` wraps its check-and-write in `with _exclusive():`
(`factory/claims.py:252`), and `_exclusive()` uses `os.O_CREAT | os.O_EXCL`
(`factory/claims.py:219`) with a comment covering the Windows `PermissionError` case. The function
carries the exact rationale the ticket proposes:

> `# The check and the write must be one indivisible step, or two callers both see "free".`

### CIP-33 — "Add `ABANDONED` as a written outcome" — REJECTED

Already declared in two places: `factory/runs.py:41`
(`FINISHED, REFUSED, ABANDONED = ...`) and `factory/tasks.py:20-21`, where `ABANDONED` is part of
`_TERMINAL`.

*Narrow residual, not worth a ticket on its own:* `ABANDONED` is declared but has no writer in
`runs.py` — nothing sets it. If that matters it belongs as a line on CIP-25, not as its own item.

## The labelling problem

**All 15 tickets are `tier: OBSERVED`. None is `DERIVED` or `ASSUMED`.**

A review that never says "I am inferring this" is over-claiming its own certainty, and the two
rejected tickets are exactly where that shows — both were labelled OBSERVED against code that
already contained the thing being proposed. Treat the tier field in this response as
undifferentiated, and check any OBSERVED claim you intend to act on.

## Disposition

- **Load 13 of 15** (all but CIP-22 and CIP-33).
- **Start with CIP-21** (wire `deploy.py`) and **CIP-27** (fix the F72 `CONNECTORS` resolution) —
  both flow from verified finding #4 and from a finding this repo raised itself.
- **D1/D2/D3 are not yet absorbed.** They are read but unactioned, which is the condition
  `absorption-backlog.md` exists to end. Promotion to `docs/research/answers/R19-*.md` requires
  reconciling them into `SYNTHESIS.md` in the same sitting — see `README.md` in this folder.
