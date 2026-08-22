# Control-plane lane — evidence

Lane `control-plane`, gates `cap`, `reaper`, `concurrency`, `bounded`, `truthful`, `from-history`.
Code lives in `prefect-connectors/orchestrator/`, branch `lane/control-plane`.

## Where the measurement was taken from

`python -m factory.readiness` resolves the connectors checkout as a **sibling of the factory
root** (`factory/readiness.py:34`). Run from this worktree that is
`agent-factory/.worktrees/prefect-connectors`, so the lane works in a git worktree of
`prefect-connectors` on branch `lane/control-plane`, created from `3da40f6`.

⚠ `orchestrator/data/` is **gitignored**, so a fresh worktree has no audit history and every
history-measured gate returns UNMEASURABLE. `audits/` (14 files) and `pipelines.json` were
copied from the main checkout so the lane measures the same history the estate does. The copy
is read-only evidence; nothing in this lane writes back to the main checkout's data directory.

| file | what it is |
|---|---|
| `readiness-before.txt` | full gate output before any change in this lane |
| `readiness-after.txt` | full gate output after |
| `negative-controls.txt` | captured pytest run of the refusal tests |

## Baseline, measured

```
python -m factory.readiness   ->  7 of 30 gates pass
```

7, not the 9 the boot prompt records, for two reasons that are both about *where the lane is
run from*, not about anything regressing:

- `isolated` reads `$AGENT_FACTORY_EVALUATOR`, which is set in `HKCU\Environment` and is not
  exported into this shell — NOT_RUN, not FAIL;
- `ticket` looks for `aldc-launchpad/boot-prompts/drafts` as a sibling of the factory root,
  which in a worktree it is not — UNMEASURABLE.

Neither is a control-plane gate and this lane changes neither. All six lane gates read **FAIL**:

| gate | baseline headline |
|---|---|
| `cap` | a cap exists on a path that did not run |
| `bounded` | no attempt cap on restart |
| `concurrency` | concurrency is bounded per wave, not per stage dispatch |
| `reaper` | no lease, timeout or reaper for dispatched work |
| `from-history` | the verdict reads current state, not history |
| `truthful` | 1 pipeline(s) claim a state their log contradicts |
