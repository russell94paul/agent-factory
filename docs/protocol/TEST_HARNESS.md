# Test harness — ⚠ one real fixture, and an honest account of what does not exist

## ⛔ The constraint, stated first

**There are eight recorded runs, none of them multi-agent, and none has ever produced a PASS.**
Calling a fixture set built on that a "replay corpus" would be the sampling error the analysis gate
forbids. What exists is **one real replayable case** and nine anchors that are not yet replayable.

```bash
python scripts/replay_recurrence.py     # shadow-mode replay of the live stream
python -m pytest tests/test_recurrence_preflight.py
```

## The ten cases

| case | anchor | replayable today |
|---|---|---|
| **known recurring failure** | ✅ **REAL** — GP-327's seven runs, 1 FAIL + 5 UNMEASURABLE + 1 NOT_RUN | ✅ **YES** — `tests/test_recurrence_preflight.py` |
| missing artifact | ✅ REAL — F87, a declared verifier with no callable | ⚠ as a classification case only |
| unstated assumption | ✅ REAL — F89, a contract reused for a second ticket type | ⛔ no |
| wrong dependency | ✅ REAL — F77/F78, acceptance criterion on the wrong repo | ⛔ no |
| duplicate task | ✅ REAL — F73, three sessions in one worktree | ⛔ no |
| novel failure | ✅ REAL — F95 | ⛔ no |
| contradictory evidence | ✅ REAL — F83, one boolean answering two questions | ⛔ no |
| unsupported claim | ✅ REAL — F84, a zero-consumer count from a blind grep | ⛔ no |
| successful handoff | ⛔ synthetic — none has ever occurred | ⛔ no |
| requirement wrongly inferred | ⛔ synthetic — no client-review history | ⛔ no |

## Why the fixture is copied into the test rather than read from `.data/`

`.data/` is gitignored, machine-local, **and still being written to by live sessions**. A test that
read it would pass or fail depending on what somebody else ran an hour ago — `WRONG_POPULATION`,
reproduced inside its own regression test. So `GP327_EVENTS` is a frozen verbatim reduction, and
`scripts/replay_recurrence.py` is the separate instrument that reads the live stream.

⚠ **If the two disagree, the stream has moved.** That is information, not a failure.

## What the fixture actually proves

1. Attempts 2–7 each receive attempt *n−1*'s verdict; attempt 1 receives **silence**.
2. The seven runs separate into **six `DECLARATION_WITHOUT_MECHANISM` and one `UNBOUNDED_RETRY`** —
   not seven of anything. A taxonomy that bucketed all seven together would be describing "GP-327
   failed" rather than classifying how, and the two have different repairs.
3. The prevention check distinguishes a fixed preset (`add-measure` → `CLEARED`) from an unfixed one
   (`ui-control` → `STILL_PRESENT`).
4. ⛔ Nothing is refused, and `Match` exposes no affordance by which a caller could refuse.
5. `UNCLASSIFIED` and `NOT-RECORDED` stay separate: all seven fixture runs are NOT-RECORDED.

## Two defects the harness itself found

Recorded because a harness that never caught anything is not evidence that it works.

1. **The preflight read the future.** `before=` skipped the matching run id instead of truncating at
   it, so replaying attempt 1 handed it the six attempts that had not happened yet. Caught by the
   first run of `test_every_attempt_after_the_first_is_shown_its_predecessor`. Now anchored by
   `test_a_preflight_cannot_read_the_future`.
2. **The packet contradicted itself.** `previous_reason` returned the first non-passing assertion,
   which on all six GP-327 runs was `outcome_observable` — a dry-run symptom — beside a family of
   `DECLARATION_WITHOUT_MECHANISM`. ⭐ **Every test passed at the time**; it was found by reading
   `scripts/replay_recurrence.py`'s output, because the tests asserted the family and none read the
   prose beside it. Now anchored by `test_the_reason_names_the_assertion_the_family_came_from`.

## CURRENT vs PROTOCOL_V1 — ⛔ EXPERIMENT tier, not run

**The rejection rule, stated before any result is seen:** reject V1 if recurrence does not fall on
the GP-327 family, **or** if median added context exceeds the 200-word budget. A harness whose pass
criterion is chosen after seeing the numbers is a conclusion wearing a method's clothes.

**⚠ It cannot run yet.** CURRENT-vs-V1 needs runs that (a) execute a real agent and (b) can reach a
PASS. Today `first_pass_green_rate` is `0/8` with `instrument_live=False`; a comparison whose
outcome metric has never registered a non-zero would measure nothing. **The comparison is gated on
one wired verifier reaching a real PASS, not on a date.**
