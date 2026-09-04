# Minimal Autonomy Pump

## Purpose

Close the measured P1 seam: policy already exists, but starting remains a tap.

## Preferred implementation shape

Keep a pure planner separate from side effects.

```python
plan = autonomy.plan(state, run_context)
# plan.actions is explainable and deterministic
for action in plan.start_actions:
    existing_start_mechanism(action.work_id, mode="AUTO")
```

### Planner inputs

- canonical work projection;
- selected run/mission membership;
- target work id;
- mode;
- pause state;
- max parallel;
- existing coordination priority signals;
- guarded-start decision/reasons;
- claims/session liveness/conflicts.

### Planner output

For every candidate, return either:

- `START`, with reason;
- `WAIT`, with reason;
- `BLOCKED`, with reason;
- `HUMAN_GATE`, with reason.

Do not emit a mysterious scalar scheduling score if the weighting is unvalidated. Reuse the repo's existing coarse priority bands/reasoning.

## Triggering

Prefer deterministic wakeups over a large async framework:

1. explicit `RUN DAG` / `RUN CRITICAL PATH` POST;
2. after `/resolve` records an approval/rejection;
3. after a work/session completion is observed;
4. on `RESUME`.

If completion cannot currently trigger in-process, a tiny bounded local runner/poller is acceptable as an adapter. Do not introduce Prefect/Temporal/Celery just to close this seam.

## Idempotency

Before starting, re-read canonical state and verify:

- still READY;
- no live session already attached;
- no claim/conflict arose;
- concurrency still available;
- run not paused.

The start operation must be safe to call twice in the sense that the second attempt refuses rather than creates a duplicate session.

## Retry

Do not implement generic auto-retry by default. The repo already has evidence of permanent failures being re-dispatched endlessly in prior systems. Retry only when a deterministic classifier says transient and an attempt budget remains.
