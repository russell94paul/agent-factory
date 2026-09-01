# Metrics — two built, eight NOT-RECORDED, and the difference stated

**Built:** `factory/reliability.py` (metrics 7 and 9) · `python -m factory.reliability`
**Design:** everything else here.

## ⛔ The join that did not exist

`events.py` describes `.data/runs.jsonl` as *the fold* of `.data/events.jsonl`. **MEASURED
2026-08-31: not one of the 10 rows carried a run id.** Eight runs in the stream, seven controller
rows in the ledger, and no key between them. Worse, both files agreed on a field called `lane` that
holds a **lane id** in rows written by `finish()` and a **ticket id** in rows written by the
controller — one name over two populations, which is how a reconciliation becomes a fabrication.

✅ Fixed: `runs.record(..., run=log.run_id)`, and `run` is now first in `runs.ATTRIBUTION` so
`unattributed()` counts joinability. `finish()` writes lane rows with no event stream, and those
correctly record `NOT-RECORDED` rather than a blank.

Without this key, every metric that needs *"what did this run go on to do"* is unanswerable, not
zero.

## The ten

Basis is stated per metric. **Six cannot be baselined today, and that is the finding rather than a
gap to paper over.**

### 7 · Dependency Violation Rate — ✅ BUILT, MEASURABLE

```
tasks claimed while a declared blocker was still open  /  tasks claimed
```

**Data:** `.data/tasks.jsonl` `block` / `unblock` / `claim` events — live, 25 block edges.
**Baseline:** MEASURED. **Gamed by:** not declaring dependencies. **Counter-metric:**
`undeclared_dependency_discovered_late`.

⚠ It **replays the store in file order** rather than reading the fold. The question is *was this
task blocked at the moment somebody took it*; the fold only knows what is true now. A task blocked
after it was claimed is not a violation, and one unblocked before it was claimed is not either.

### 9 · First-Pass GREEN Rate — ✅ BUILT, MEASURABLE, and the honest value is zero

```
runs reaching PASS with no earlier attempt at the same ticket  /  runs reaching a terminal verdict
```

**Baseline: 0 / 8, MEASURED — and `instrument_live = False`.**

⭐ **The flag is the finding.** The stream can express PASS; the enum and the contract both do. But
no run has ever produced one, so this zero has **not been shown to be a measurement rather than a
blind instrument**. `Rate.__str__` prints `⚠ [instrument NEVER seen to register a non-zero]` and
`tests/test_recurrence_preflight.py` carries the negative control that proves the counter *can*
register a green when one exists. Do not quote this rate without the flag.

⚠ Denominator is runs that reached a terminal **verdict**, not runs that started. A run whose
process died before a verdict was assigned had its outcome observed by nobody; counting it as
non-green reports our own crash as the ticket's failure.

**Gamed by:** weakening the contract. **Counter-metric:** assertion count × `verifier_state` census.

### 1 · Known Error Recurrence Rate — ⛔ DESIGN

```
runs whose failure_family has been seen before on this ticket  /  completed runs
```
**Basis: NOT-RECORDED.** The field landed 2026-08-31; every historical terminal event predates it.
**Retrospectively derivable** for the seven GP-327 runs via `classify_recorded` — see the replay.
**Gamed by:** classifying everything as novel. **Counter-metric:** `unclassified_failure_share`
(✅ built, `preflight.unclassified_share()`).

### 2 · Known Failure Share — ⛔ DESIGN. NOT-RECORDED, same cause as 1.

### 3 · Agent Communication Defect Rate — ⛔ DESIGN
**Basis: NOT-MEASURABLE — the denominator is 0.** No multi-agent run has executed. A rate over an
empty population is not zero. **Counter-metric:** `implementation_defect_rate`, published in the
same table or "communication" becomes the bucket everything falls into.

### 4 · Handoff First-Pass Acceptance — ⛔ DESIGN. NOT-RECORDED; no handoff has ever been emitted.
**Gamed by:** ACKing everything. **Counter-metric:** ⭐ `downstream_rework_after_ack`.

### 5 · Clarification Rate — ⛔ DESIGN. NOT-RECORDED.
**Gamed by:** never asking. **Counter-metric:** `defects_downstream_of_silent_handoffs`.

### 6 · Duplicate Work Rate — ⚠ PARTIAL
`sessions.duplicates()` and `claims.active()` are live; matching a run against *completed task
titles* is not wired. **Gamed by:** narrowing the match key. **Counter-metric:**
`refused_starts_later_shown_legitimate`.

### 8 · Preventable Failure Rate — ⛔ DESIGN
```
failures whose family had a packet at start  /  all failures
```
Becomes measurable as soon as `preflight_checked` events accumulate — `invocations()` already
carries `warning_emitted` beside `eventual_verdict`.

### 10 · Mean Recovery Time — ⚠ PARTIAL
Timestamps are on disk and GP-327 gives seven points, but **n = 1 ticket**. One ticket is a hint,
not a distribution. **Gamed by:** abandoning instead of recovering. **Counter-metric:**
`abandonment_rate`.

## The Goodhart pairing is enforced, not documented

`reliability.metric_set()` registers `known_failure_warnings` as an **activity** metric anchored to
`first_pass_green_rate`. `factory.metrics` raises `GoodhartViolation` if an activity metric names no
registered outcome, and `suspicious()` reports activity climbing over a zero outcome in one line.

⚠ **This patch is exactly the kind of work that produces a 234/0 dashboard** — a warning counter
that goes up while nothing improves. The pairing is the control against measuring ourselves.

## §H · Communication error attribution — ⛔ DESIGN, and the guard comes first

A defect is communication-caused only when **all three** hold:

1. the information existed upstream and was **recorded somewhere** at handoff time;
2. it was absent, wrong-versioned or mis-stated in the envelope;
3. had it been correct, the receiver's action would have differed — as a falsifiable counterfactual.

| symptom | deterministic discriminator |
|---|---|
| missing artifact | ref present upstream, absent from `artifacts_to_consume` |
| wrong artifact/version | `sha` mismatch |
| unstated assumption | claim `ASSUMED` upstream, arrives absent or as `CONFIRMED` |
| receiver misread contract | `required_receiver_behavior` ≠ what the receiver's events show |
| dependency completion uncommunicated | `unblock` exists; no `HANDOFF` references it |
| contradictory claims propagated | two `CONFIRMED` claims, same subject, opposite states |
| **UNKNOWN → FACT** | ⭐ claim state upgrades across a boundary with no new `evidence_ref` |
| duplicate work | metric 6's key |
| stale context | `NACK_STALE`'s test |
| unacknowledged blocking state | `block` event with no `BLOCKED` message |

⛔ **If the information was never recorded anywhere, it is an implementation or analysis defect, not
a communication defect.** Attribution requires naming the upstream record.
