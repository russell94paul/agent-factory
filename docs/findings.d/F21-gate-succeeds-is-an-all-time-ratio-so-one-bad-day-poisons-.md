<!-- session: 2026-08-22 · boot pre-flight + three-lane launch -->

### F21 — Gate `succeeds` is an all-time ratio, so one bad day poisons it permanently


- **KIND** — DESIGN
- **STATUS** — ADOPTED
- **BELIEVED** — "a stage fails 6.1× more than it succeeds" is a current reliability rate, and a
  run of good stages will pull it back over the line.
- **ACTUALLY** — `readiness.py:188` passes on `done > failed` counted over **every audit file
  ever written**, unwindowed and undated. It stands at 165 completed against 1001 failed, so
  flipping it needs **837 net successful stage completions** — with zero new failures, 837
  consecutive good stages. Most of the 1001 come from the single 2026-08-14 incident where an
  uncapped restart loop took the region quota (352 restarts of `trigger-run` in one run), so the
  metric permanently carries a fault that has since been capped. It answers "has this system ever
  been reliable" when the question every reader asks of it is "is it reliable now".
- **MEASURED BY** — read `factory/readiness.py:180-190`: `_counts(_audits())` over
  `orchestrator/data/audits/*.json`, no date filter, pass condition `done > failed`. Arithmetic:
  1001 − 165 = 836, so 837 net successes to cross. Compare against the incident evidence already
  in the `bounded` gate.
- **CHANGES** — window the ratio to runs started since `MEASURED_SINCE`, print the all-time figure beside it with a note on why they differ, and raise Unmeasurable on an empty window. **Built** in `factory/readiness.py` (`g_succeeds_more_than_fails`). The audits are NOT deleted — the `bounded` gate cites the 2026-08-14 incident as evidence.
- **AFFECTS** — control-plane and judgement lanes, and any before/after claim made with
  `python -m factory.readiness`. Either window the ratio (last N runs, or since a stated date) or
  quarantine the incident's audits behind a declared exclusion — and whichever is chosen, the gate
  must **state its basis in its own evidence line**, so the number is never read as current when
  it is cumulative. Do not simply delete the audits: that destroys the evidence the `bounded` gate
  cites.
