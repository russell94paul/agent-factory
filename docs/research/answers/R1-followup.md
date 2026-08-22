# R1 follow-up — what else in the eval-harness answer rests on the Prefect misattribution?

**Status: DISPATCHED, not answered.** Ask this in the existing R1 thread. The answer lands beside
this file as `R1-followup-answer.md`.

**Written 2026-08-22**, from
[`docs/evidence/false-succeeded-mechanism.md`](../../evidence/false-succeeded-mechanism.md).

---

## What R1 got wrong, and how

R1 wrote:

> *"Prefect's final-state rules can produce precisely the semantic trap visible in your logs: if
> failures are captured as returned state rather than propagated, a parent flow may return
> successfully and become COMPLETED."*

Plausible, cites real Prefect behaviour, and **aimed at the wrong layer.** The pipeline that
reports `succeeded` over 115 failures is the **build plane** — the orchestrator at `:8765`, a
bespoke engine that does not import Prefect. The actual mechanism is a last-write-wins per-stage
status field; see `R3-followup.md` for the code.

We then carried the misattribution forward into R3 as a whole question ("THE PREFECT TRAP")
without walking the route ourselves. Verifying it took one grep.

## The question

**1. Which other conclusions in your eval-harness answer depend on that premise?**
Go back through it and mark each recommendation as: *unaffected*, *needs restating for a bespoke
engine*, or *no longer applies*. We are specifically unsure about anything that assumed Prefect's
state machine, retry semantics, or task-run history would be available to the harness as a source
of truth.

**2. Does the `EXECUTION_TERMINATED` / `CONTRACT_PASS` vocabulary split survive intact?**
We believe it does and that the real mechanism *strengthens* the case for it. Confirm, or say what
changes when the state store is a JSON file plus an append-only event log rather than a Prefect
backend.

**3. Where should the eval harness read run history from**, given that the authoritative history
is our own audit trail and the per-stage status field is not trustworthy? One case is already
unrecoverable: for `deploy-prefect` the stored stage statuses are simply gone from
`pipelines.json`, so any design must say what it does with an incomplete history.

**4. Was anything else in the answer sourced from vendor documentation rather than from our code?**
That is the tell we missed. The citation was to Prefect's docs about Prefect's behaviour, which is
only relevant if Prefect is in the path — and it is not. If other recommendations rest on the same
kind of citation, we would rather know now.

## Method note, offered rather than implied

Two tells were present when the misattribution was adopted and both were missed:

- **The named component could not produce the symptom's shape.** A Prefect final-state rule cannot
  explain a status field that is overwritten by the last attempt.
- **Nothing in the citation was a query against our code.**

This is the estate's own standing rule — *an object named by a ticket, boot prompt, or handoff is a
hypothesis, not a finding* — and we broke it on our own research. Treat anything asserted in this
document the same way.
