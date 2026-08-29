# External review responses — the landing area

Where an answer from an outside model goes **before** it becomes part of the record.

## Why this folder exists rather than dropping it straight into `docs/research/answers/`

`factory/synthesis.py:116` globs `docs/research/answers/R[0-9]*-answer*.md`, and
`tests/test_synthesis_current.py::test_every_filed_answer_is_mentioned_in_the_synthesis` goes
**red** the moment a file matching that glob is not named in `SYNTHESIS.md`.

That is a feature — it is this repo's absorption-forcing mechanism, and absorption is the estate's
measured weakness (19 conclusions reached a mechanism and never reached the decision record). But it
means filing an answer is a **commitment to reconcile it now**, and it breaks `pytest` for every
other session in the repo until you do.

So: two stages.

## Stage 1 — land it here, unverified

```
docs/reviews/external/YYYY-MM-DD-<model>/
    response.md        the raw answer, exactly as returned — do not edit it
    prompt.md          the prompt that produced it (or a pointer to the file used)
    verification.md    your check of its claims, written as you check them
```

Nothing here is part of the record. The suite stays green. An answer can sit here while you decide
whether it is worth anything.

**Keep `response.md` verbatim.** If you correct it in place you lose the ability to tell what the
model actually said from what you wished it had said — which is the same failure as editing a
measurement.

## Stage 2 — promote, and reconcile in the same sitting

When it has been verified and you are ready to absorb it:

```
docs/research/answers/R19-answer-<slug>.md
```

Next `R` number: **R19** (R1–R18 exist; R13 and R16 have two files each).

Promotion is not a copy. It means:

1. Add the `R19` section to `SYNTHESIS.md` — this is what turns the suite green again.
2. Add any corrected premise to `docs/findings.md` using its schema
   (`BELIEVED / ACTUALLY / MEASURED BY / AFFECTS`).
3. Add any conclusion that reached a mechanism to `docs/absorption-backlog.md`, or create the task.
4. Run `python -m pytest -q` and confirm green before committing.

If you promote without doing 1–3, you have added a twentieth unabsorbed answer to a corpus whose
diagnosed problem is nineteen unabsorbed answers.

## Verifying an external answer — what to check first

An outside model cannot see the filesystem, and this repo's public default branch is a
**2026-08-20 skeleton, 157 commits behind** the working branch. So:

- **Every `OBSERVED` claim cites a file and section — open a sample and check.** Misattributed
  citations are the known failure mode of external passes, not fabricated conclusions.
- **Check which ref it read.** A claim verified against `main` is probably about the skeleton, not
  the current code. Those are `UNVERIFIABLE`, whatever the model labelled them.
- **`STALE` verdicts against our docs may be backwards** — if it read old code, our doc is right and
  its verdict is wrong. Check the direction before believing it.
- Its `D4` JSON is shaped for `factory.tasks.TaskStore.create()`. Verify before loading; the store
  is append-only, so a bad batch is awkward to remove.
