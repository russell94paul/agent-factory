### F92 — `g_output_is_certified` had no in-suite guard and a timeout shorter than the pytest it starts, so the suite paid a full certify per measuring test and orphaned the grandchild when it gave up

Found during the bootstrap wave by an inventory pass over the evaluation system, and verified here
by reading both spawn sites and timing the result.

## Two defects in one gate, and they compound

`g_contract_suite_green` carries a recursion guard whose comment calls it *"load-bearing"*. The
gate directly beneath it in the same file does the same class of thing — shells out to a
subprocess that runs pytest — and had **no guard at all**.

**⚠ Correct the tempting description before it spreads.** This is *not* the suite invoking itself.
`certify.py` does not import `readiness`, so there is no cycle:

```bash
grep -n "^from\|^import" factory/certify.py | grep -i readiness   # (nothing)
```

It is something less obvious and, for a while, more expensive: an ordinary gate that reaches into
a **second repository** and runs its test suite, for a verdict the run asking the question cannot
use. The chain is `board()` → `measure()` → `g_output_is_certified` → `subprocess factory.certify`
→ `live_probes.py:188` → `subprocess pytest` against the connectors checkout.

- **BELIEVED** — `board()` is a cheap projection over gate verdicts, so a test that renders a
  measuring surface costs about what its assertions cost.

- **ACTUALLY** — every call to `board()` paid a full subprocess `certify`, which itself paid a full
  pytest run in another repository. `tests/test_roadmap.py` calls `board()` in ~20 tests, so the
  file could not finish. And the two timeouts were **inverted**: the outer bound on `certify` was
  `120`, the inner bound on the pytest it starts is `300` (`live_probes.py:188`).
  `subprocess.run(timeout=...)` kills only the **direct child**, so the outer timeout killed
  `certify` and left its pytest grandchild running unattended — the parent reporting a timeout for
  work that had not stopped.

- **MEASURED BY** — timing the same file before and after the guard, nothing else changed:

  ```
  before   tests/test_roadmap.py    terminated at 120s, never completed
  after    tests/test_roadmap.py    20 passed in 39s
  ```

  Per-test cost before, from `pytest --durations` on the full suite: `168.89s`, `143.32s`,
  `132.75s`, `90.09s`, `87.04s`, `80.69s`, `74.19s`, `64.76s` — eight tests in one file, ~840s of
  a 35-minute suite, all of it the same certify. The inverted bound is verified by reading the two
  literals; `subprocess.run`'s kill-the-direct-child behaviour is documented, not measured here.

  ⚠ **The orphan half is reported, not reproduced by me.** The inventory pass reported observing
  orphaned `certify`+`pytest` pairs alive 25+ minutes past both timeouts. A process-table sweep
  during this session found **none** — by then the runs that would have produced them had ended.
  The defect that permits it is structural and verified; the sighting is second-hand.

- **AFFECTS** — `factory/readiness.py` and everything derived from `readiness.GATES`:
  `factory/board.py`, `roadmap.py`, `flow.py`, `goals.py`, and `scripts/local_tracker.py`, which
  re-measures per request. It is also the likeliest explanation for a tracker render taking
  **6m38s** against a documented *"~10-19 s a page"* (`docs/research/ui-surface-inventory.md:66`),
  though that render was measured by a different pass and not re-timed after this fix.

  ⛔ **And it kept the suite gate permanently red for an instrument reason.** The suite could not
  finish inside `g_contract_suite_green`'s own 300s bound, `.data/suite-cache.json` only ever
  caches a PASS by design, so the cache could never fill and every render re-paid the whole cost.
  A gate reporting FAIL because its instrument could not run in time is the shape this file exists
  to refuse.

- **KIND** — INSTRUMENT

- **CHANGES** — `g_output_is_certified` now returns NOT_RUN under `AGENT_FACTORY_IN_SUITE=1`,
  mirroring `g_contract_suite_green`, and says which command to run for the verdict instead. The
  outer bound is expressed as `_CERTIFY_INNER_TIMEOUT_SEC + 120` so the relationship between the
  two numbers survives someone editing either. Two tests in `tests/test_suite_cache.py`, beside
  the existing guard test: one asserting the gate does not shell out under the flag, one asserting
  the outer bound exceeds the inner by **reading the inner literal out of `live_probes.py`** rather
  than restating it — a copy of that number would rot the way a mutation anchor does (F-family).

  ⚠ **NOT_RUN is a real loss, not a free win.** The board now carries one more unmeasured gate
  whenever it is rendered from inside the suite. That is the honest verdict — the running suite
  genuinely cannot use certify's answer — but anyone reading a board produced under the flag must
  read `NOT_RUN` as *"nobody looked"*, never as *"fine"*. Outside the suite the gate is unchanged
  and still measures.

- **STATUS** — ADOPTED
