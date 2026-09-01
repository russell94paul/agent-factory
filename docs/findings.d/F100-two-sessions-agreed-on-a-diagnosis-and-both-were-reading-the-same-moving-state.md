### F100 — two sessions independently reported the same defect, agreed, and were both wrong because they were reading the same mutable state mid-change

Filed 2026-09-01. The test they diagnosed was correct throughout, and it started passing with **no
change to the code they blamed**.

## The sequence

```
Client Review session   full suite -> 689 passed, 1 failed
                        tests/test_client_review.py::test_the_navira_review_assembles_and_renders
                        "delivered outcomes report ASSERTED, its test expects GROUNDED"
                        -> concluded: Client Review defect

Reliability session     full suite on clean main -> same single failure
                        -> concluded: owned by Client Review, did not touch it

Mission Commander       R3 completes; its two evidence files land
                        same test, same code, by name:  1 passed
```

**Nobody fixed anything.** R3 had no evidence file, so the review's R3 outcome was `ASSERTED`; the
test asserted `GROUNDED`; completing R3 supplied the evidence and the outcome became `GROUNDED`.
The test was **right the whole time** — it was reading a mission in which one of eight tasks had no
evidence, and saying so.

## The causal record, stated so history is not rewritten

```
BEFORE R3 EVIDENCE   claim status observed: ASSERTED
                     test expected:         GROUNDED
                     result:                FAIL

R3 COMPLETES         docs/evidence/marketing-model-v1/R3-preflight-readonly-proof.md
                     docs/evidence/marketing-model-v1/R3-cartography.md

AFTER R3 EVIDENCE    same test, no Client Review code change:  PASSED
```

⭐ **Client Review did not fix this and must not be recorded as having fixed it.** This is a clean
Delivery #001 example of an artifact changing because its **canonical evidence** changed — which is
precisely what a client-review surface is supposed to do. The mechanism worked; two observers read
it mid-flight and mistook correct behaviour for a defect.

## The rule

> **Agreement between observers reading the same mutable state is not independent corroboration.**

Two sessions concurring feels like corroboration and is not, when both sampled one moving system
within the same window. It is one observation counted twice. The same shape produced the shared-index
collision earlier that day, where `git diff --cached` showed four files and `git commit` shipped
eighteen.

**Therefore: a diagnosis about shared mutable mission state must carry enough state identity to be
reproducible**, or it is an anecdote:

```
git HEAD
mission / task revision or event boundary
evidence snapshot (as-of)
test invocation
observation time, where it matters
```

Neither report carried a HEAD. Had either done so, the third session would have seen immediately
that it was measuring a different commit.

⚠ **A diagnosis about changing state must be re-measured against current state before being
promoted to a defect.** Re-measuring cost one command here.

## Smallest future enforcement seam

⛔ **Do not build a snapshot system for this.** The cheap seam already exists: `factory/handoff.py`
composes cross-session reports, and `runs.jsonl` now carries a stable run identity from
RAPID-RELIABILITY-01. The minimal change is that a **failure claim** in a handoff carries the HEAD
and mission event-boundary it was measured at, and a reader refuses to inherit a failure whose HEAD
does not match the current one — the same discipline `verified_at` applies to a credential in
[[F99]]. One field, one check, no new subsystem.

- **BELIEVED** — two independent sessions reporting the same failure is strong corroboration, so
  the diagnosis can be acted on without re-measuring.

- **ACTUALLY** — they were not independent. Both read one mutable mission store while a third
  session was actively completing a task inside it, and neither recorded the state it sampled.
  The agreed diagnosis was wrong, the blamed code was correct, and the failure resolved with no
  change to it.

- **MEASURED BY** — running the disputed test **by name** on the current HEAD after R3 landed,
  rather than inferring its status from a green suite (a skipped or deselected test also fails to
  fail):
  ```bash
  python -m pytest "tests/test_client_review.py::test_the_navira_review_assembles_and_renders" -v
  1 passed
  ```

- **AFFECTS** — **every lane**, and every cross-session handoff: any report that asserts a test
  failure, a count, or a mission status without naming the state it was measured against.
  Concretely `factory/handoff.py`, `docs/protocol/HANDOFF_CONTRACT.schema.json` (which now exists
  and is the natural home for the required field), `tests/test_client_review.py`, and the
  Delivery #001 case-study record.

- **KIND** — PROCESS

- **STATUS** — OPEN
