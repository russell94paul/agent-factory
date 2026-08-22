# R3 follow-up — the false `succeeded` is not Prefect, so Q4 was aimed at the wrong plane

**Status: DISPATCHED, not answered.** Ask this in the existing R3 thread rather than re-running
R3 — the rest of that pass (bounded execution, orphan reaping, gates that can refuse, sandboxing,
tenancy, evaluator isolation) is unaffected, because none of it named Prefect as the thing at
fault. The answer lands beside this file as `R3-followup-answer.md`.

**Written 2026-08-22**, from the correction measured in
[`docs/evidence/false-succeeded-mechanism.md`](../../evidence/false-succeeded-mechanism.md) against
`prefect-connectors` @ `3da40f6`.

---

## The question, verbatim

> The false-COMPLETED defect is not in Prefect. Our agent pipeline runs on a bespoke engine whose
> terminal verdict is computed from a last-write-wins per-stage status field, so a stage that
> failed 100 times and then succeeded contributes nothing to `any_failed`. The failures exist only
> in an append-only event log that the verdict does not consult. Given that, what is the correct
> design for computing a terminal verdict from an append-only history rather than from current
> state, and how would you build a negative control proving a false `succeeded` is impossible?

## The mechanism, so the answer can be specific

`orchestrator/pipelines.py:1669-1678`, and again at `:1771-1777`:

```python
all_done = all(s["status"] in ("completed", "failed", "skipped") for s in pipeline["stages"])
any_failed = any(
    s["status"] == "failed" and not s.get("continue_on_failure")
    for s in pipeline["stages"]
)
if all_done:
    final_status = "failed" if any_failed else "succeeded"
```

`pipeline["stages"][i]["status"]` is last-attempt-wins. The 115 recorded failures were never in the
object the verdict is computed from.

⭐ **The verdict is not lying — it answers a different question than the one anyone reads it as.**
`succeeded` is a true statement about the *final state of each stage*, read as a statement about
*the history that produced them*. Those coincide only when nothing was retried, which this pipeline
has almost never been.

A second shape, same file, `:1766`:

```python
if pipeline["status"] in ("failed",):
    pipeline["status"] = "running"
```

A restart resets `failed → running` before re-dispatching. If the restart never reaches a terminal
state the record sits at `running` for ever while its own log ends in `stage_failed`. That is
`pipe_29b8edf6`, and it is why the `truthful` readiness gate fails.

## Three things the answer should cover

1. **The vocabulary split.** R1 proposed `EXECUTION_TERMINATED` vs `CONTRACT_PASS`. We think that
   is right and this mechanism is what forces it — confirm or improve it, and say where each value
   is computed and stored.
2. **Retry-independent reliability.** "Succeeded on attempt 1" and "succeeded on attempt 101" are
   indistinguishable in `pipeline["stages"]` and trivially separable in the audit trail. What
   should the reliability metric actually be computed over?
3. **`continue_on_failure` deserves its own look.** A stage carrying that flag is excluded from
   `any_failed` by design. Nothing checks how many stages carry it, or whether any should.

## And the harder half of the question

**The negative control.** Not "does the new verdict function return `failed` on a failing history"
— that is the positive case. We want the construction that makes a false `succeeded`
*structurally impossible*, and a test that would catch its reintroduction. Our house rule is that
a mechanism nobody has watched refuse something is not a control, so the answer should say what,
concretely, is made to fail.

One case we already know is unresolved and cannot be reconstructed: `deploy-prefect` ended
`failed`, its run closed `succeeded`, and the audit log cannot explain its own verdict — the stored
stage statuses are gone from `pipelines.json`. Any design should say what it does when the history
is *incomplete*, which for us is not hypothetical.
