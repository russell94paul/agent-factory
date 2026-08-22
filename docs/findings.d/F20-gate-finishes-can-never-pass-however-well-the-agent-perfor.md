<!-- session: 2026-08-22 · boot pre-flight + three-lane launch -->

### F20 — Gate `finishes` can never pass, however well the agent performs


- **BELIEVED** — "3/14 runs finished" is a score that improves as the loop gets more reliable, so
  landing the reaper and re-running the loop will move it. [[F4]] says the numbers are stale;
  the natural inference is that fresh runs fix them. For this gate that inference is wrong.
- **ACTUALLY** — `readiness.py:175` passes only on `len(fin) == len(runs)` — **every** recorded
  run finished, all-time, with no window. Four runs (`pipe_5546c123`, `pipe_66d2326d`,
  `pipe_7274e774`, `pipe_c34bfbe5`) sit at `stage_started` with no terminal event and, being
  history, will never gain one. Each new run increments both sides, so the ratio can approach
  14/18, 14/50 — never equality. The gate is not a hard target, it is unreachable: a perfect
  agent from now until forever still reads FAIL. A gate that cannot pass is the mirror of the
  decoration-gate this repo already refuses — it stops being a measurement and becomes a wall,
  and the board reports failure at work that is already fixed.
- **MEASURED BY** — read `factory/readiness.py:175`; the pass condition is equality, not a rate.
  Then note the four ids in the gate's own evidence lines. No run appended after today can
  satisfy it, because the shortfall is in runs that already ended.
- **AFFECTS** — control-plane lane (`finishes`, and the `reaper` it is building), and anyone
  reading the 30-gate score as progress. The reaper is the fix, but only if it **backfills a
  terminal event for those four historical runs** rather than only bounding future dispatch —
  emitting terminal events for new work leaves this gate exactly where it is. Decide deliberately
  whether a reaper-emitted terminal counts as "finished"; if it does not, the gate needs a window
  instead.
