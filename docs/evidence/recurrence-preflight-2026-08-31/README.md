# Evidence — known-failure preflight (RAPID-RELIABILITY-01 BUILD_NOW)

**Branch** `reliability/recurrence-preflight`, isolated worktree `.worktrees/reliability`, based on
`ddea66d`. ⛔ The active `marketing-model-reconstruction-v1` mission's working tree was not touched.

## Files here

| file | what it is |
|---|---|
| `replay-shadow-mode.txt` | ⭐ the full shadow-mode replay of all 8 recorded runs — regenerate with `python scripts/replay_recurrence.py` |

## Regenerating every number in the report

```bash
python scripts/replay_recurrence.py                 # the replay, packet sizes, would_refuse census
python -m factory.reliability                       # metrics 7 and 9, and the Goodhart check
python -m factory.preflight                         # invocations table + unclassified share
python -m pytest tests/test_recurrence_preflight.py  # 29 tests
python -m pytest                                     # full suite
```

## Baseline vs patch — MEASURED

| | base `ddea66d` | branch |
|---|---|---|
| suite | **648 passed, 2 xfailed** (202.67 s) | **679 passed, 2 xfailed** (206.78 s / 219.55 s over two runs) |
| delta | — | **+31, zero regressions** — 29 in `tests/test_recurrence_preflight.py`, 2 added to `tests/test_control_run.py` |

⚠ Run twice; identical both times. The boot README warns of an unidentified flaky test at roughly
one run in four — it did not appear in either run here, which is weak evidence of absence, not
evidence it is gone.

## Shadow-mode result

| | |
|---|---|
| runs in `.data/events.jsonl` | 8 |
| would have emitted a warning | **6** — GP-327 attempts 2–7 |
| silent | 2 — GP-327 attempt 1, and GP-401 (also a first attempt) |
| marked `would_refuse` (shadow, never acted on) | **5** |
| packet size | mean **94.8 words / 807 chars**, max 95 — budget 200 words |
| classification of recorded failures | 8 failures, **all NOT-RECORDED** (the field postdates them) |

## ⚠ Two defects this work found in itself

Recorded because a harness that never caught anything is not evidence that it works.

1. **The preflight read the future.** `before=` skipped the matching run id instead of truncating at
   it, so a replay of attempt 1 was handed the six attempts that had not happened yet — every
   replayed attempt then looked equally well-informed and the replay proved nothing. Caught by the
   first execution of the replay test. Anchored by `test_a_preflight_cannot_read_the_future`.
2. **The packet contradicted itself.** `previous_reason` returned the first non-passing assertion,
   which on all six GP-327 contract runs was `outcome_observable` ("cannot observe this run's
   outcome — dry run") — printed directly beneath `failure_family: DECLARATION_WITHOUT_MECHANISM`.
   ⭐ **Every test passed at the time.** It was found by reading the replay output, because the
   tests asserted the family and none read the prose beside it. Anchored by
   `test_the_reason_names_the_assertion_the_family_came_from`.

## ⭐ The finding worth keeping beyond this patch

`deploy.AttemptLedger` already injects prior failures into the next prompt, and it was **live,
correct by its own lights, and silent** through all seven GP-327 attempts.
`.data/attempts.json.pre-F85.bak` records why:

```json
"ui-control-agent:gp-327": {"count": 2, "attempts": [
  {"n": 1, "outcome": "ok", "detail": "dry run", "limit": "none"},
  {"n": 2, "outcome": "ok", "detail": "dry run", "limit": "none"}]}
```

Both attempts are `outcome: "ok"` because the **provider** exited zero on a dry run, and
`failures()` filters on `outcome != "ok"`. So `context()` returned the empty string on every retry.

**The ledger reads what the provider observed; a verdict is what a `GreenContract` assigned.** Those
are different questions, and a retry-context mechanism that reads only the first is blind to every
non-PASS verdict. Families: `BLIND_INSTRUMENT` + `COLLAPSED_STATE`.
