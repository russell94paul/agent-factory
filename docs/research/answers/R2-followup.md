# R2 follow-up — our build plane is not Prefect. Move onto it, or reimplement it?

**Status: DISPATCHED, not answered.** This file holds the question and the grounding a research
pass needs. Paste it into the R2 topology thread. The answer lands beside it as
`R2-followup-answer.md`.

**Written 2026-08-22.** This is the highest-value unasked question in the programme: R2's topology
answer assumed Prefect primitives were available to us, and they are not, so several of its
recommendations are not implementable as written. That single misassumption is upstream of at
least four open readiness gates.

---

## The correction R2 needs before it can answer anything

R2's recommendations lean on Prefect primitives — retry limits, concurrency reservation,
work-pool slots, orphan reaping. **Those are not available primitives for the thing that needs
them.**

There are two planes in this estate and they are routinely conflated (we conflated them ourselves;
see `docs/evidence/false-succeeded-mechanism.md`):

| Plane | What it is | What it runs | Prefect? |
|---|---|---|---|
| **Run plane** | Prefect 3 | the *data* connectors — vendor API → container → Snowflake | yes |
| **Build plane** | the orchestrator at `:8765` | the 18-stage connector-*migration* pipeline, with agent stages | **no** |

`orchestrator/pipelines.py` does not import Prefect. Verified by grep at `3da40f6`: no
`import prefect` anywhere in the file. It is a **bespoke engine** with its own state file
(`pipelines.json`), its own append-only audit trail, and its own gate logic. It *drives* Prefect
via `prefect_proxy.py` and `stage_scripts/prefect_ops.py` for the data flows, but nothing about its
own execution is a Prefect flow.

So every control R2 recommended for the build plane is currently **something we would have to
build**, not something we would configure.

## What the build plane measurably lacks

Measured from `python -m factory.readiness`, 4 of 30 gates passing:

| Gate | Measured state |
|---|---|
| `bounded` | no attempt cap on restart. `pipelines.py` records the 2026-08-14 incident verbatim: a stage "auto-restarted with no attempt cap", and ten containers took the whole 10-core canadacentral quota |
| `cap` | a cap exists — on a path that did not run |
| `concurrency` | bounded per wave, not per stage dispatch |
| `reaper` | 4 of 14 runs sit at `stage_started` with no terminal event; nothing timed them out |
| `truthful` | terminal verdict computed from a last-write-wins status field, not from the append-only log — a stage that failed 100× and succeeded on the 101st contributes nothing to `any_failed` |
| `finishes` | 3 of 14 runs reached `pipeline_completed` |
| `succeeds` | a stage attempt fails 6.1× more often than it succeeds |
| `cost` | no spend ceiling enforced before dispatch |

Every one of these is a primitive a mature orchestrator ships with.

---

## The question

**1. Given that the build plane is a bespoke engine, what must we actually build?**
Enumerate the minimum set of control primitives the 18-stage agent-migration pipeline needs to run
unattended — attempt caps, orphan reaping/timeouts, per-stage concurrency reservation, spend
ceilings enforced *before* dispatch, and a terminal verdict computed from append-only history.
For each: what is the correct design given that our state is a JSON file plus an append-only event
log, and what is the negative control that proves it works?

**2. Should we move the build plane onto Prefect instead of reimplementing its primitives?**
We already run Prefect 3 for the run plane, so the operational knowledge and infrastructure exist.
Argue both sides against our actual constraints:

- **For:** retries, concurrency limits, work pools, timeouts, state history and a UI all exist and
  are maintained by someone else. We stop reimplementing an orchestrator badly.
- **Against:** the build plane's stages are *agent* stages — long-running, non-deterministic,
  needing worktree isolation and human gates. Prefect's model may fit data flows and not this. A
  migration costs us the bespoke gate logic and audit trail that already work, and it puts the
  thing that *supervises* connector migrations onto the same system it supervises — a shared
  failure mode.

**3. If the answer is "move", what is the migration path** that does not stop the pipeline, and
which parts stay bespoke? **If the answer is "reimplement", which primitives are genuinely cheap
to build correctly** and which are traps we should not attempt?

**4. Is there a third option we have not considered** — a lighter workflow engine, or a Prefect
deployment that wraps each agent stage as a single task while keeping our gate logic outside it?

## What a useful answer looks like

A recommendation with a stated basis, not a survey. Where you cite a Prefect capability, say
whether it applies to *long-running non-deterministic agent stages* or only to data tasks — that
distinction is exactly what the original R2 answer glossed, and it is why this follow-up exists.

## Method note

The estate's own rule, applied to its own research: *an object named by a ticket, boot prompt, or
handoff is a hypothesis, not a finding — walk the route yourself before adopting it.* R1 named
Prefect as the cause of the false-`succeeded` defect; it was wrong, and verifying took one grep.
Assume the same about anything in this document you can check.
