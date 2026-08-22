# The false `succeeded` is not Prefect — it is a last-write-wins status field

**Measured 2026-08-21** against `prefect-connectors` @ `3da40f6`. Corrects a diagnosis that two
research answers and one of our own prompts had already adopted.

## The inherited premise, and why it was wrong

R1 wrote:

> *"Prefect's final-state rules can produce precisely the semantic trap visible in your logs: if
> failures are captured as returned state rather than propagated, a parent flow may return
> successfully and become COMPLETED."*

Plausible, cites real Prefect behaviour, and **aimed at the wrong layer**. I then carried it into
R3 as a whole question — *"THE PREFECT TRAP"* — without walking the route myself. Paul's one-line
clarification that "Prefect is the tool that runs the data pipeline (scheduler)" is what surfaced
it.

**There are two planes in this estate and they are easy to conflate:**

| Plane | What it is | Runs |
|---|---|---|
| **Run plane** | Prefect 3 | the *data* connectors — vendor API → container → Snowflake |
| **Build plane** | the orchestrator at `:8765` | the 18-stage connector-*migration* pipeline with agent stages |

`orchestrator/pipelines.py` **does not import Prefect**. Verified: no `import prefect` anywhere in
the file. It is a bespoke engine with its own state file, its own append-only audit trail and its
own gate logic, which *drives* Prefect via `prefect_proxy.py` and `stage_scripts/prefect_ops.py`
for the data flows. The pipeline whose runs report `succeeded` over 115 failures is the build
plane, not a Prefect flow, so no Prefect final-state rule can be responsible for it.

## The actual mechanism

`orchestrator/pipelines.py:1669-1678` — and again at `:1771-1777`:

```python
all_done = all(s["status"] in ("completed", "failed", "skipped") for s in pipeline["stages"])
any_failed = any(
    s["status"] == "failed" and not s.get("continue_on_failure")
    for s in pipeline["stages"]
)

if all_done:
    final_status = "failed" if any_failed else "succeeded"
    pipeline["status"] = final_status
    audit_trail.record_pipeline_completed(pipeline_id, final_status)
```

`pipeline["stages"][i]["status"]` is **last-attempt-wins**. A stage that failed a hundred times and
succeeded on the hundred-and-first reads `completed`. So `any_failed` is `False` and the run is
`succeeded`.

The 115 failures were never in the object the verdict is computed from. They exist only in the
append-only event log, which nothing consults at this point.

⭐ **The verdict is not lying. It is answering a different question than the one anyone reads it
as.** `succeeded` is a true statement about the *final state of each stage*. It is read as a
statement about *the history that produced them*. Those two coincide exactly when nothing was
retried — which is the case this pipeline has almost never been in.

## The `running`-over-a-failed-log case, same file

`orchestrator/pipelines.py:1766`:

```python
if pipeline["status"] in ("failed",):
    pipeline["status"] = "running"
```

A restart resets `failed` → `running` before re-dispatching. If the restart then does not reach a
terminal state, the record sits at `running` indefinitely while its own log ends in `stage_failed`.
That is `pipe_29b8edf6`, and it is why the `truthful` readiness gate fails.

## Why this matters more than the label

The distinction changes the fix. If it were Prefect's final-state rules, the repair is a Prefect
idiom — `return_state`, `raise_on_failure`, a custom final-state hook. It is not, so:

1. **The status field cannot be the evidence.** A terminal verdict must be computed from the
   append-only history, or from a field that is itself append-only. R1's proposed vocabulary split
   — `EXECUTION_TERMINATED` versus `CONTRACT_PASS` — is right, and this is the mechanism that
   forces it.
2. **Retry-independent reliability needs the log, not the status.** "Succeeded on attempt 1" and
   "succeeded on attempt 101" are indistinguishable in `pipeline["stages"]` and trivially
   separable in the audit trail.
3. **`continue_on_failure` deserves its own look.** A stage carrying that flag is excluded from
   `any_failed` by design; nothing here checks how many stages carry it or whether any should.

## Consequence for R3, which is already running

R3's Q4 asks for the correct Prefect 3 idiom and a negative control for Prefect terminal semantics.
That question is aimed at the wrong plane and its answer will be about a component that does not
produce the defect. The rest of R3 — bounded execution, orphan reaping, gates that can refuse,
sandboxing, tenancy, evaluator isolation — is unaffected, because none of it named Prefect as the
thing at fault.

**Follow-up to ask in the R3 thread when it returns**, rather than re-running it:

> The false-COMPLETED defect is not in Prefect. Our agent pipeline runs on a bespoke engine whose
> terminal verdict is computed from a last-write-wins per-stage status field, so a stage that
> failed 100 times and then succeeded contributes nothing to `any_failed`. The failures exist only
> in an append-only event log that the verdict does not consult. Given that, what is the correct
> design for computing a terminal verdict from an append-only history rather than from current
> state, and how would you build a negative control proving a false `succeeded` is impossible?

## Method note

This is the estate's own rule applied to its own research: *an object named by a ticket, boot
prompt, or handoff is a hypothesis, not a finding — walk the consumer route yourself before
adopting it.* Two tells were present and I missed both. The named component could not produce the
symptom's shape, and nothing in the citation was a query against our code — it was a citation to
Prefect's documentation about Prefect's behaviour, which is only relevant if Prefect is in the
path. Verifying took one grep.
