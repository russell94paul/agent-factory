# Control-plane lane — evidence

Lane `control-plane`, gates `cap`, `reaper`, `concurrency`, `bounded`, `truthful`,
`from-history`. Code in `prefect-connectors/orchestrator/`, branch `lane/control-plane`.

**Session 1 (2026-08-22, morning) measured: 7 of 30 gates → 14 of 30. All six lane
gates FAIL → PASS.** ⚠ That is this document's FIRST session only, and it is not the
current number — an independent review found it read as a live headline. Session 2,
below, measured 15 of 30 before and 15 of 30 after: the count did not move, because
the work was making already-passing gates honest. `python -m factory.readiness` is
always the live answer.

⚠ **The lane earns 6 of that +7, not 7.** `chain` also flipped FAIL→PASS in the same
window. `g_impeccable_precedence_settled` reads
`~/.claude/skills/living-systems-ui/SKILL.md` — outside both repos, untouched by this
diff, and the artifact lane's work. Caught by an independent review re-deriving the figure
rather than accepting it; the original wording here attributed it to this lane.

---

## Where the measurement was taken from

`python -m factory.readiness` resolves the connectors checkout as a **sibling of the
factory root** (`factory/readiness.py:34`). Run from this worktree that is
`agent-factory/.worktrees/prefect-connectors`, so the lane works in a git worktree of
`prefect-connectors` on branch `lane/control-plane`, created from `3da40f6`.

⚠ `orchestrator/data/` is **gitignored**, so a fresh worktree has no audit history and
every history-measured gate returns UNMEASURABLE. `audits/` (14 files) and
`pipelines.json` were copied from the main checkout so the lane measures the same history
the estate does.

| file | what it is |
|---|---|
| `readiness-before.txt` | full gate output before any change in this lane |
| `readiness-after.txt` | full gate output after |
| `mutations.txt` | the connectors-side mutation harness — do the TESTS depend on the controls? |
| `probe-mutations.txt` | the factory-side mutation harness — do the GATES depend on the controls? |
| `rollback/` | pre-change `pipelines.json` and `pipe_29b8edf6.json`, captured by `--apply` |

## Baseline, measured

```
python -m factory.readiness   ->  7 of 30 gates pass
```

7, not the 9 the boot prompt records, for two reasons that are both about *where the lane
is run from*, not about anything regressing:

- `isolated` reads `$AGENT_FACTORY_EVALUATOR`, set in `HKCU\Environment` and not exported
  into this shell — NOT_RUN, not FAIL;
- `ticket` looks for `aldc-launchpad/boot-prompts/drafts` as a sibling of the factory
  root, which in a worktree it is not — UNMEASURABLE.

Neither is a control-plane gate and this lane changes neither.

| gate | before | after |
|---|---|---|
| `cap` | a cap exists on a path that did not run | the restarting path is capped, and was watched refusing |
| `bounded` | no attempt cap on restart | failure is bounded at 5 attempts, watched |
| `concurrency` | bounded per wave, not per stage dispatch | stage dispatch is bounded at 4, watched deferring |
| `reaper` | no lease, timeout or reaper for dispatched work | dispatched work is leased and reaped, watched |
| `from-history` | the verdict reads current state, not history | the verdict is derived from the event log |
| `truthful` | 1 pipeline claims a state its log contradicts | recorded status agrees with the event log |

---

## ⭐ Two of the six gates could never have passed

Before any work: an AST walk over each probe, counting the kinds of `Return` it can reach.

```
g_failure_is_bounded          returns=['_fail']            raises=0
g_orphans_are_reaped          returns=['_fail']            raises=0
g_attempt_cap_on_the_live_path returns=['_fail','_pass']   raises=0
g_concurrency_is_reserved…    returns=['_fail','_pass']    raises=1
g_verdict_is_computed…        returns=['_fail','_pass']    raises=1
g_status_matches_reality      returns=['_pass','_fail']    raises=3
```

`bounded` and `reaper` had **exactly one return path each**. They were constants, not
instruments: no amount of work on the build plane could have moved them, and both had
been read for a day as measurements of an unbounded, unreaped system. `reaper` also
searched `orchestrator/engine/work_guard.py` — whose lease covers repo locks between
agents — and never looked in `pipelines.py`, where `reclaim_orphaned_stages` already
lived.

That is the finding this lane would have missed by treating the gate list as the
specification. It is recorded in `docs/findings.md` as F11.

---

## What was built

`orchestrator/pipelines.py` gained a **CONTROL PLANE** section. The build plane imports no
workflow framework (finding F1), so none of this is configuration — each control is code
that had to exist. All of them refuse out loud: a refusal writes `control_refused` to the
append-only audit trail.

| control | constant | what refuses |
|---|---|---|
| attempt cap | `MAX_ATTEMPTS_PER_STAGE = 5` | `retry_stage`, `restart_from_stage`, and `_build_stage_requests` |
| dispatch ceiling | `MAX_PARALLEL_STAGE_DISPATCH = 4` | `_build_stage_requests`, across every pipeline |
| lease + reaper | `LEASE_GRACE_MIN = 15` | `reap_expired_leases()`, on its own thread |
| verdict from history | — | `terminal_verdict()` replays the append-only log |

Design decisions that are not obvious, each made for a measured reason:

- **The counter is on the persisted record.** `pipeline_agent._recovery_attempts` is a
  module-level dict that empties on every restart, so a cap built on it bounds a *process*
  rather than a *stage*.
- **The cap is enforced at the choke point too.** `retry_stage` and `restart_from_stage`
  are where a human asks. `_build_stage_requests` is where every attempt actually happens,
  including the watchdog's — which on 2026-08-13 re-dispatched one permanently-failing
  stage every 30 minutes overnight.
- **An override buys exactly one more attempt, audited.** An unoverridable cap does not
  stop the loop, it moves it: on 2026-08-14 the way past the mechanism was to delete the
  pipeline, which destroyed the evidence too.
- **`clear context` no longer zeroes the counter.** A cap a dashboard checkbox can reset
  is a suggestion.
- **Manual gates hold no dispatch slot.** A gate waiting on a human consumes no compute,
  and counting it would let two paused runs deadlock every other pipeline — a ceiling
  causing the outage it was added to prevent.
- **The reaper terminates; it never re-dispatches.** That is the whole distinction from
  `recover_stale_pipelines`. `trigger-run` launches an ACI backfill that *survives* the
  orchestrator; re-dispatching it lands the same rows twice.
- **The reaper runs ungated by the agent toggle.** An orphaned container leaks the shared
  quota whether or not anyone has the agent switched on.
- **The verdict fails closed.** `audit.get_audit` returns an empty event list for both "no
  such file" and "corrupt file". A verdict computed from that list is a false `succeeded`
  produced by the very defect it is meant to remove, so an unreadable history is
  `UNMEASURABLE` and the run is `failed`.

---

## Negative controls — every control watched refusing

`prefect-connectors/tests/orchestrator/test_control_plane.py`, **46 tests, all passing**.
Every control is exercised in both directions, because a guard that refuses everything
passes a cap test while silently disabling the feature.

| refuses | permits |
|---|---|
| `retry_stage` at the cap raises `ControlRefused(control="attempt_cap")` | a stage can be retried right up to the cap |
| `restart_from_stage` at the cap, **before** it nulls `stage["error"]` | a first dispatch is never refused |
| `_build_stage_requests` at the cap — the path with nobody watching | — |
| an empty/whitespace override reason is not an override | a reasoned override buys exactly one attempt, then refuses again |
| ceiling+3 concurrent dispatches → only `MAX` granted | deferred stages stay `pending` and are dispatched when a slot frees |
| the ceiling holds across two pipelines | manual gates never consume a slot |
| an expired lease is reaped to `failed`, never `pending` | a live lease is not reaped |
| — | a manual gate gets no lease at all |
| — | a stage with no measurable lease is NOT-MEASURABLE, not expired |
| a run that succeeded over 100 failures reads `clean=False` | a clean run still reads `succeeded` |
| a missing log gives `basis=UNMEASURABLE, status=failed` | a tolerated `continue_on_failure` still lets a run succeed |
| a stage the log never saw finish cannot make a run succeed | a genuinely running pipeline is left alone by the reconciler |
| a run nothing can advance is closed rather than left `running` | a terminal status is never revised |
| the sweep never touches a stage a human must release | a stranded pipeline is swept up when slots free |
| a full ceiling stays full | the sweep rechecks dependencies rather than trusting the mark |
| reaping the last runnable stage closes the run | reaping one stage of a live run does not close it |

### Two defects the negative controls found, before any of this ran anywhere real

1. **The override was decoration.** The choke-point cap check did not know about it, so an
   override granted at `retry_stage` was refused two calls later by
   `_build_stage_requests`. It logged loudly and changed nothing. Now it leaves a
   single-use `_cap_grant` token the choke point consumes.
2. **A start with no recorded end still counted as success.** `unrecorded` only looked for
   stages missing from the log *entirely*, so a stage the log saw start and never saw
   finish passed. The record's status field was doing the work again — the exact
   substitution `terminal_verdict()` exists to remove.

### Two more found by tracing the change rather than by a test failing

Neither of these had a failing test to point at them. Both were found by asking what the
new code depended on and then checking, and both are recorded in `docs/findings.md`.

3. **The dispatch ceiling could strand a whole pipeline (F14).** A deferred stage is left
   `pending`, and the claim "`_find_ready_stages` will offer it again on the next sweep"
   was not checked. `on_session_complete` re-offers only when a stage *in that same
   pipeline* completes, and `recover_stale_pipelines` has exactly one caller —
   `pipeline_agent._run_watchdog` — which returns early on `if not _enabled`, and the agent
   is off by default. A run that got zero stages dispatched had nothing that would ever
   come back for it, which is the documented six-people-six-connectors case. Fixed by
   `dispatch_deferred_stages()` on the reaper's ungated thread, which offers **only** the
   stages the ceiling itself marked — never the ones `reclaim_orphaned_stages` left pending
   for a human, whose ACI backfill may still be landing rows.

4. **⭐ The reaper recreated the defect this lane exists to remove (F17).** Reaping the last
   runnable stage marked the *stage* `failed` and left the *run* at `running` over a log
   ending `stage_failed` — `pipe_29b8edf6`'s exact shape. Nothing would have closed it:
   `on_session_complete` fires only when a session reports, and a reaped stage has no
   session left to report. The same is true of a stage the attempt cap closes at the choke
   point. Measured by driving it:
   ```
   reaped: [{'pipeline_id': 'pipe_x', 'stage': 'only', ...}]
   stage : failed
   PIPELINE STATUS AFTER REAPING THE ONLY STAGE: running
   ```
   Fixed: `reap_expired_leases()` reconciles what it reaped, and server.py's periodic loop
   reconciles unconditionally.

---

## Mutation harnesses — is any of it load-bearing?

A green suite proves the tests pass, not that they matter. Two harnesses, one per
instrument.

### `mutations.txt` — do the TESTS depend on the controls?

`prefect-connectors/tests/orchestrator/mutate_control_plane.py`. Disables each control and
requires the matching tests to fail. **7 of 7 load-bearing.**

```
cap                       10 failed   both cap checks removed
concurrency                4 failed   ceiling branch removed
reaper                     5 failed   reap_expired_leases returns nothing
from-history: verdict      1 failed   any_failed reads pipeline["stages"] again
from-history: clean        2 failed   retry count dropped from `clean`
from-history: fail-closed  1 failed   missing log treated as an empty one
truthful: reachability     3 failed   _reachable asks only whether a pending stage EXISTS
```

⭐ The first `from-history` mutation kills **one of six** verdict tests. The history
replay's unique contribution is narrower than the class name implies, which is why `clean`
and fail-closed get their own mutations. Reporting "the history replay is load-bearing"
off the class alone would have been a broader claim than the measurement supports.

### `probe-mutations.txt` — do the GATES depend on the controls?

`scripts/mutate_readiness_probes.py`. Copies `orchestrator/` to a scratch tree, deletes the
control there, points `$PREFECT_CONNECTORS` at the copy and re-runs the gate. Nothing under
the real checkout is ever written. **6 of 6 flip off PASS.**

```
cap           both cap checks removed             PASS -> FAIL
bounded       ceiling at the choke point          PASS -> FAIL
concurrency   dispatch ceiling branch             PASS -> FAIL
reaper        reap_expired_leases reaps nothing   PASS -> FAIL
reaper        terminal kill -> recover instead    PASS -> FAIL
from-history  missing log treated as empty        PASS -> FAIL
```

`truthful` is absent on purpose: it measures a data record rather than a code control, so
its mutation is the connectors-side `truthful: reachability` above.

---

## The probes were rewritten, and that needs defending

Five probes in `factory/readiness.py` were replaced. **These are the instruments that grade
this lane**, so the rules held to are stated rather than implied:

1. only a probe that is **not an instrument** (a constant verdict) or that measures the
   **wrong artefact** is replaced;
2. every replacement is **strictly harder to satisfy by decoration** than the one it
   replaces — a grep becomes an executed refusal;
3. every replacement gets a **mutation test**: remove the control, the gate must fall off
   PASS. All six above.

What each old probe could be satisfied by, and what the new one does:

| gate | old probe | satisfied by | new probe |
|---|---|---|---|
| `bounded` | one return path, `_fail` | nothing, ever | asks for 50 dispatches of one stage, counts how many are granted |
| `reaper` | one return path, `_fail`; greps `work_guard.py` | nothing, ever | expires a lease, requires a terminal kill and a live lease spared |
| `concurrency` | greps `pipelines.py` for lowercase `max_parallel` | a comment | asks for ceiling+3, then asks a second pipeline, then checks gates do not starve work |
| `cap` | regex near two function names | a comment | drives both paths past the ceiling and requires each to refuse |
| `from-history` | `any_failed = any(… for x in NAME)`, is `"event" in NAME` | renaming a variable | drives a stage to fail 7× then succeed and requires the verdict to have seen all 7 |

Every rewritten gate's evidence now carries the **date window of the history it cites**
(finding F4). The recorded runs stop at 2026-05-28, so "worst 352 restarts" is a fact about
a history that ended three months ago, and the gates now say so.

If the build plane will not import, the probes raise `Unmeasurable` — a gate that cannot
establish its instrument has not measured anything, and UNMEASURABLE is not a pass.

### And nothing was watching the probes

`tests/test_readiness_probes_can_pass.py` (new, 59 passed + 2 xfailed) is the mirror of
`test_eval_can_fail.py`: every gate must have a reachable PASS **and** a way of refusing.
It would have caught `bounded` and `reaper` the day they were written. Its limit is stated:
it proves a PASS is *written*, not that any input reaches it.

It found three more defective probes on its first run, all outside this lane and all
recorded in `docs/findings.md`:

- **`corpus`** — `g_corpus_is_tamper_evident` returns `_fail` on every branch, including
  the one where all four sub-checks passed. Same class as `bounded` and `reaper`.
- **`tenancy`** — `g_tenancy_declared` raises `Unmeasurable` when `allowed_tenants` is
  empty. But an empty list *is* a measurement, and reporting it as "no instrument" rather
  than FAIL collapses two of the contract's four verdicts.
- the three research follow-up gates return `_pass`/`_notrun` and never `_fail`, which is
  **correct** — "not asked yet" is NOT_RUN. The first version of the refuse test called
  that a defect; the test was wrong, and it was measured before it was believed.

---

## `truthful` — a data record, corrected rather than rewritten

`pipe_29b8edf6` recorded `running` over a log ending `stage_failed` at `git-commit-and-pr`,
since 2026-05-28. Not merely stale: **structurally unreachable**. `on_session_complete`
asked only whether a pending stage *exists*, and ten did — every one downstream of that
failed stage, which carries no `continue_on_failure`, so none could ever become ready.

`scripts/reconcile_pipeline_records.py` is two-step by design:

```
--dry-run (default)   computes corrections on a scratch COPY; the data directory is
                      never opened for writing
--apply --rollback    copies every file it will touch, writes, then re-reads and checks
                      each correction against the one the dry run predicted
```

Dry run and apply agreed exactly:

```
pipe_29b8edf6   running -> failed
    basis            MEASURED
    clean            False
    failures in log  1
    closed because nothing further can ever run: True
```

`pipe_fc674dfd` is untouched — status `created`, six pending stages, no failed dependency,
so genuinely un-started. A reconciler that closed it too would make the record agree with
the log by lying in the other direction.

⚠ **Applied to the lane's copy only.** Writing to the main checkout's data directory was
refused by the permission classifier, correctly — it is outside this worktree. The command
for the real record is in the handover below.

### Two knock-on effects on gates this lane does not own

| gate | before | after | is it a regression? |
|---|---|---|---|
| `finishes` | 3/14 runs finished | 4/14 | No — the run genuinely reached a terminal state; nothing had recorded it |
| `honest` | 3 completed runs carried failures | 4 | No, but **the listing is wrong** |

`g_success_means_correct` counts a run as "reporting success over failures" whenever a
`pipeline_completed` event coexists with a `stage_failed`. It never reads the status the
run actually reported. `pipe_29b8edf6` now reports **failed**, and its own
`pipeline_completed` event carries `final_status: "failed"` in its details — verified by
reading the audit file, not inferred. The correction is one line, and it belongs to the
judgement lane, which shares `pipelines.py` with this one.

---

## The independent read, and what it found

An opus reviewer was given the lane's gates and five questions: has each control been
*watched* refusing; which numbers were measured and which inferred; **is this
goalpost-moving**; what changed that nothing tests; and correctness/blast radius. Every
finding below was reproduced before it was fixed. Ten findings; the four that matter:

### ⭐ Two gates could not see the defects they are named for

**`from-history`.** Reverting `any_failed` to the original last-write-wins expression —
one edit, nothing else — left the gate reading PASS and all 45 tests passing. The gate was
satisfied by a system that still had the defect it exists to detect.

The cause is subtle and worth keeping: the probe's pass condition was `failures_in_log ==
FAILS and clean is False`, and both come from the replayed log **independently of
`any_failed`**. The probe proved the failure *count* comes from the log; it never proved
the *verdict* does. The ⭐ note further up this file got close — "narrower than the class
name implies" — and then still credited a kill to it. Measured in isolation, the history
replay's unique contribution was **zero tests and zero gates**.

Both now use a discriminating case: a stage whose log ends `stage_failed` and whose status
field says `completed`. The field says `succeeded`; the log says `failed`. In this engine
every status write is mirrored by an audit event, which is exactly *why* nothing caught it
— the two expressions agree on every state the engine can reach on its own, so the test
has to construct the one state where they cannot.

**`cap`.** Same shape. The probe handed itself a stage with `_attempts` already at the
ceiling, which proves the comparison fires and proves nothing about whether anything moves
the counter. Deleting the one line that writes `_attempts` left the gate reporting "watched
refusing" over an engine whose cap could never fire. It now drives a real dispatch and
asserts the counter moved.

### ⛔ A guard that never matched anything, inherited and repeated

`cap`'s protection against the dashboard resetting the counter was a regex requiring two
arbitrary characters and then the literal `_retry_count`. It never matched the line it was
written to catch: after `pop(` the source reads `"_retry_count`, so those two characters
consume `"_` and the literal lands one character too late. **The `not cleared` half of the
pass condition was vacuously true** — at `ea888b0`, and in this lane's rewrite, where a
commit message described it as a guard the gate enforced. Verified by running both patterns
against the real line from `server.py` at `3da40f6`. It now matches the quote explicitly
and covers `_attempts` too, since `attempts()` reads that field and guarding only the old
one would let a future `clear_context` zero the real counter with the gate still green.

### ⛔ An instrument that was measuring its own writes

`_history_window()` took every event in the audit files. The moment the reconciler wrote
`status_reconciled` and `verdict_recorded`, evidence about a history that stopped in May
began reading "2026-05-26 to **2026-08-22**" — as though the system had been busy through
August. It now counts only events a *run* produces, and reads 2026-05-26 to 2026-05-28.

### Four code defects, one severe and one client-visible

| # | defect | why it matters |
|---|---|---|
| F2 | **the dispatch ceiling is not atomic** — `free` is read, then `status="dispatched"` is written an audit round-trip later, and this module has no in-process lock | two threads each granted the FULL ceiling: eight concurrent dispatches against four, on a shared 10-core quota. **The 2026-08-14 shape, reachable through the control added to prevent it.** The same window let two callers dispatch the same stage — for `trigger-run`, two ACI backfills against one schema. The race pre-existed the lane; the lane added a third dispatcher and it is the only ungated one |
| F4 | `reconcile_status_with_history` skipped `budget_paused` | precisely the reaper's widest case, which a test celebrates finding. `truthful` was blind to it and `resume_pipeline` could not rescue it |
| F5 | **three more paths stranded their run**, and my fix lived in server.py | `skip_if_cataloged` and `resume_pipeline` too — and putting coverage in a 300-second loop made the invariant false for five minutes at a time and *permanently* false for every caller that is not the server. `_close_if_terminal` now runs at each call site |
| F7 | the early close posts a **"failed" completion to the client's Jira ticket and latches** | `jira_notifier` drops every completion after the first. Stage fails → ticket says "pipeline finished: failed" → operator fixes it and the run genuinely succeeds → the correction is silently swallowed |

### Both harnesses had criteria looser than their claims

- `mutate_control_plane.py` counted **any** non-zero pytest exit as LOAD-BEARING. Pytest
  exits 5 on "no tests collected", so a typo'd `-k` selector would have read as success.
  Now requires `rc == 1` and a summary naming failures.
- `mutate_readiness_probes.py` used `after != "PASS"`, which accepts UNMEASURABLE and
  ERROR — a mutation that merely broke the scratch tree's import would have reported
  LOAD-BEARING. Now requires FAIL: a gate must **refuse**, not merely fail to measure.
- The compound `from-history` mutation is split; its single kill belonged entirely to the
  unwitnessed-stage half, not to the history replay it was credited to.

**8 of 8 load-bearing in each harness**, up from 7 and 6, with the two previously
uncovered controls among them.

### What the review confirmed rather than overturned

The two-constants claim is true against git history. Both harnesses do real removals, not
perturbations. `1,004 / worst 352`, `3→4 of 14`, `4 of 14 at stage_started` and the
pre-existing `test_logbook` failure all re-derive independently. Both defects found by
tracing were real and are genuinely fixed.

### Accepted and NOT fixed, with reasons

- **`_reachable` computes the greatest fixed point**, so two mutually-dependent `pending`
  stages keep each other alive and the run can never be closed. Real, and latent: pipeline
  templates are static and acyclic. A least-fixed-point formulation has no such hole.
  Recorded rather than rewritten, because changing the closure rule with no live run to
  check it against trades a latent hole for an untested one.
- **`configure()` reconciles before the audit trail may exist**, in which case the
  `status_reconciled` events meant to preserve the record's history are silently dropped
  while the mass-failure is persisted. Safe at every current call site, ordered correctly
  in `server.py`, and nothing enforces it.
- **The cap's override is unreachable from the dashboard** — `server.py` plumbs
  `override_reason`, `static/index.html` never sends it. The design's own justification for
  the cap being safe is currently reachable only by curl. In the handover.
- **`restart_from_stage` checks the cap only for the target stage**, so a restart can be
  accepted and then die at a downstream stage already at its lifetime cap. Arguably correct
  behaviour; the response does not say so.
- **`reclaim_orphaned_stages`' "a human decides" contract was already unenforced** —
  `pending` + satisfied deps = ready, to every dispatch path, with or without this lane's
  sweep. The durable fix is a positive `_needs_human_release` flag honoured by
  `_find_ready_stages`, which also closes the pre-existing half. Out of this lane's scope.
- **`static/index.html:1746` now carries a stale comment** about `restart_from_stage`
  preserving `_retry_count`.

## Suites

| suite | result |
|---|---|
| `prefect-connectors` `tests/orchestrator` | **648 passed, 1 failed** |
| `prefect-connectors` whole suite | **871 passed, 1 failed** |
| `agent-factory` `pytest` | **all passed, 2 xfailed** (the two allowlisted probe defects) |

The one connectors failure is `test_logbook.py::TestResolution::test_recurrence_after_resolution_is_marked_regressed`
(`RESOLVED` where `REGRESSED` is expected). **Pre-existing**, and measured rather than
assumed: it fails identically on the unmodified main checkout at `3da40f6`. Unrelated to
this lane — it is the logbook's regression detection, not the control plane.

---

## Handover — what is NOT done

1. **The real record is still wrong.** One command, from this worktree:
   ```
   python scripts/reconcile_pipeline_records.py \
     --data C:/Users/PaulRussell/repos/prefect-connectors/orchestrator/data \
     --connectors C:/Users/PaulRussell/repos/agent-factory/.worktrees/prefect-connectors \
     --apply --rollback docs/evidence/control-plane-2026-08-22/rollback-main
   ```
   Run the dry form first; it prints exactly what `--apply` will do. Expect `finishes` to
   go 3/14 → 4/14 and `honest` to list a fourth run for the reason above.

2. **Nothing has run.** Every control here is proven against a driven engine and a test
   suite. None has been watched refusing during a *live* migration, because the
   orchestrator has not run since 2026-05-28 and the boot prompt's standing instruction is
   not to start an unattended one. The controls are what make a supervised run safer to
   attempt; they are not evidence that one succeeded.

3. **`MAX_ATTEMPTS_PER_STAGE = 5` and `MAX_PARALLEL_STAGE_DISPATCH = 4` are ASSUMED, not
   derived.** The cap is set above `pipeline_agent`'s existing 2 so the watchdog still
   hits its own limit first; the ceiling is set well under the 10-core canadacentral quota
   because one stage can launch more than one container. Neither number has been measured
   against real throughput, and the first live run is what would calibrate them.

4. **The reaper cannot kill the cloud work, only the stage.** `reap_expired_leases` closes
   the record and stops the slot leaking. An ACI container that outlived its stage keeps
   running; `prefect_ops._cleanup_stale_aci` exists and is called at startup, but nothing
   ties a reap to a container deletion. That is the remaining half of "dispatched work is
   either finished or killed", and this lane did not build it.

5. **`ceiling` and `cost` still FAIL** — no spend check before dispatch. They sit in the
   same phase and the same file, but they belong to the judgement lane's list, not this
   one's.

6. **The cap's override cannot be used from the dashboard.** `server.py` plumbs
   `override_reason` from the request body; `static/index.html` never sends it, so an
   operator who hits the cap gets a toast telling them to supply a reason with no field to
   supply it in. The routes past are curl or Delete Pipeline — and Delete Pipeline is the
   2026-08-14 workaround that destroyed the evidence. **The design's own argument for why
   an attempt cap is safe is currently not reachable from the UI.** One input and one
   field in the POST body.

7. **`tests/orchestrator/mutate_control_plane.py` mutates in place**, and its dirty-file
   guard does not cover a concurrent *reader*. It cost the reviewer three spurious
   full-suite failures when their read overlapped a run of it, and a tool timeout once
   killed it mid-mutation so the `finally` restore never ran (the guard caught that on the
   next invocation, but only for the next writer). `scripts/mutate_readiness_probes.py`
   already does the right thing by copying to a scratch tree; the connectors-side harness
   should do the same, or take a lockfile.

8. **`static/index.html:1746` carries a stale comment** — it says `restart_from_stage`
   preserves `_retry_count`, which is no longer the field the cap is measured against.

---

# Session 2 — 2026-08-22 — the half of each gate that was still decoration

**Measured: 15 of 30 gates before, 15 of 30 after. The number did not move, and that is
the finding.** All six lane gates were already PASS at the start of this session. Three of
them were passing over the defect they are named for.

| gate | what it said before | what it was still blind to |
|---|---|---|
| `reaper` | "dispatched work is leased and reaped, watched" | the **container**. Reaping closed the record and told a human to go and check whether the cloud work was still running. Ten containers taking a 10-core quota is the incident the gate exists for, and the record was never the thing holding the quota |
| `cap` | "the restarting path is capped, and was watched refusing" | the operator. The override existed only in `server.py`, and the dashboard rendered the refusal as a **green success toast** |
| — | `mutate_control_plane.py` reported 8 of 8 load-bearing | it mutated the real tree, and its verdict depended on a `-q` inherited from a different repository two directories up |

---

## 1. `reaper` — "either finished or killed" killed only the record

`reap_expired_leases` marked the stage `failed`, freed the dispatch slot, reconciled the
run — and its own error string handed the dangerous half to a person:

> *"If this stage launches cloud work, check whether it is still running before releasing
> it again."*

A control that asks someone else to do the dangerous part is not the control it is named
after, and the dangerous part is the documented one. `trigger-run` starts a Prefect flow
run whose ACI container **survives the orchestrator** — 2026-08-13, ten of them took the
whole 10-core canadacentral quota; 2026-08-15, an abandoned `seller_cloud` container was
still merging rows twenty minutes after its stage stopped waiting for it.

Two things had to exist before the reaper could kill anything.

**A durable handle.** The flow run id lived in a local variable on a thread-pool thread.
In the exact case that produces orphans — the orchestrator dies — the only handle on a
container burning a shared core died with it. `record_external_handle` writes it to the
persisted stage record and the append-only log **the moment Prefect answers**, at all
three `create_flow_run` sites, wired through `ScriptContext.report_external_handle` which
`server.py` binds per stage.

**A terminator that fails closed.** `orchestrator/engine/cloud_reaper.py`, registered by
`server.py` rather than imported by `pipelines.py`, so the engine still imports no cloud
SDK and a unit test drives the whole control plane with a fake.

Design decisions that are not obvious:

- **Cancel first, then delete.** `PrefectService.cancel_flow_run` sets CANCELLING, not
  CANCELLED, deliberately — the container belongs to the worker and only the worker can
  tear it down cleanly. But the reaper fires precisely when the worker may be gone and
  nobody will ever act on CANCELLING, so the container is checked and deleted anyway.
- **Ownership fails closed, and the rule is the repo's own.** Container groups are
  `<slugified-flow>-<run-uuid>` with no operator suffix, so two people running the same
  connector produce indistinguishable names. `owned_by_this_instance` reads
  ORCHESTRATOR_USER_SUFFIX off the container and returns False whenever it cannot tell.
  Unproven ownership is NOT_ATTEMPTED. On 2026-08-14 ten orphaned containers were cleared
  by hand and it was safe only because one person happened to be running that connector —
  an unattended reaper does not get to be lucky. A leaked container is recoverable; a
  colleague's live backfill deleted mid-merge is not.
- **Matching is on the run id, never a name fragment.** That is what makes a delete safe
  in a resource group six people share, and matching by name is why every cleanup call was
  a silent no-op until 2026-08-15.
- **The verdict is one of the contract's four, never a boolean.** KILLED / NOT_FOUND /
  NOT_ATTEMPTED / FAILED, plus NOT_RECORDED for a stage carrying no handle.
  ⚠ **NOT_RECORDED does not mean "it launched nothing."** It means we cannot tell, and
  every stage dispatched before this commit is in that state. Collapsing those is the
  false-`succeeded` defect one layer out.
- **A terminator that answers outside the vocabulary is not believed.** It becomes FAILED.
- **A terminator that raises still lets the record close.** A record left `dispatched`
  because Azure was unreachable is strictly worse than one closed with FAILED beside it.

### Watched refusing — 23 negative controls

`tests/orchestrator/test_cloud_reaper.py`, all passing.

| refuses | permits |
|---|---|
| a container whose ownership cannot be proven is **not deleted** | a container that is provably ours is cancelled and deleted |
| `ORCHESTRATOR_REAP_TERMINATES=off` touches nothing, and says the quota may still be held | a Prefect outage does not stop the container being freed |
| an empty run id never authorises a delete | the flow run is cancelled **before** the container is deleted |
| an unreadable container list is FAILED, not NOT_FOUND | no container for the run is NOT_FOUND, not KILLED |
| a failed delete says the container is still running | a live lease is never terminated |
| a verdict outside the four-word vocabulary is not believed | a handle survives the process that recorded it |
| a stage with no handle is NOT_RECORDED, and the operator is told it is an **unknown** | the same run recorded twice is recorded once |

### ⚠ The limit, stated rather than implied

**There is no Azure subscription in this suite and there is not going to be one.** The
decision logic is proven; the three `az`/Prefect seams behind it are not, and cannot be
from a laptop. The seams exist so that the untested surface is three functions rather than
a file. Nothing here has been watched deleting a real container.

### The gate could not see any of it

`g_orphans_are_reaped` passed with the entire termination path deleted. The F18 shape, one
gate over. It now requires the reap to **reach** the terminator carrying the stage's own
handle — where the handle is placed by `record_external_handle`, the same function
`server.py` binds into every script stage, rather than written into the dict by the probe
— requires a handle-less stage to report NOT_RECORDED, and checks the wiring at the source
(every launch site reports; the server binds the recorder; the server registers the
terminators).

---

## 2. `cap` — the refusal was invisible at the surface a human watches

The handover said the override was "unreachable from the dashboard: one input and one
field in the POST body." Tracing it found something worse.

`api()` has no `res.ok` check anywhere. It returns the parsed body whatever the status. So
`check_attempt_cap`'s 400 arrived as `{error: "..."}`, `retryStage` read
`result.dispatched || 0`, and the operator was shown

```
Retrying "trigger-run" with context — 0 dispatched          [success, green]
```

over a request the engine had refused. The `catch` block beneath it is dead code. The
routes past were curl or Delete Pipeline — and Delete Pipeline is the 2026-08-14
workaround that destroyed the evidence along with the loop. **The design's own argument
for why an attempt cap is safe rested on a path nobody could take and a refusal nobody
could see.**

Fixed with `apiStrict()` (deliberately a *second* function — there are forty-odd `api()`
call sites and most are page loads that must degrade quietly; making them all throw would
trade a silent action failure for a blank dashboard), `isAttemptCapRefusal()`, and
`retryWithCapOverride()`, which states that an override buys exactly one attempt and is
recorded, and sends nothing at all for a blank or whitespace reason — which is also what
`check_attempt_cap` refuses, so the two agree.

### Watched, in a real browser, against the engine's real message

`scripts/dashboard_cap_override_probe.py` drives the real `index.html` in Chromium. The
refusal text is produced by **driving `check_attempt_cap` in-process**, not typed into the
probe — finding F19 is a regex guard that had never been shown to match the line it was
written for, and a pattern tested against an invented message proves nothing.

```
ok  the refusal was recognised as a cap refusal, not a generic error
ok  the first request carried no override
ok  the second request carried the override to the wire
ok  the refusal was shown to the operator as an ERROR, not a success
ok  no success toast was raised before the override succeeded
ok  cancelling sends NOTHING
ok  cancelling says nothing was retried
ok  a whitespace-only reason is not an override
```

Run against the pre-change file it fails four of them and prints the defect verbatim.
Both transcripts and a screenshot of the two rendered toasts are in `dashboard/`.

Three cheap regression guards live in `tests/orchestrator/test_pipeline_routes.py` — the
file whose own docstring is about a feature that existed behind an unreachable route. One
builds the engine's refusal and asserts the dashboard's pattern matches it.

---

## 3. The mutation harness was the least safe thing in the repository

`tests/orchestrator/mutate_control_plane.py` is the instrument that proves the controls
are load-bearing. It had two defects.

**It mutated the real tree.** The dirty-file guard protected the harness's own restore,
not a concurrent *reader*: someone running the suite mid-mutation saw three spurious
failures in a file they had not touched. And a `finally` does not run when the process is
killed — a tool timeout left the working tree with a control removed. It now copies the
worktree (~8 MB) to a temp directory. Proven: `pipelines.py`'s sha256 is identical before
and after a full run, and `git status -- orchestrator/` is empty.

**⛔ Its verdict depended on where the checkout sits.** The summary parser anchored on
`^\d+ (passed|failed)`, which matches pytest's count line only when `-q` is in effect.
This lane's connectors worktree lives *inside* `agent-factory`, whose `pyproject.toml`
carries `addopts = "-q"`, and **pytest walks upwards for its rootdir config** — so the
suite was inheriting `-q` from an unrelated repository two directories up. The same files
anywhere else print `====== 10 failed, 36 deselected ======`, the anchor matches nothing,
and the harness announces *"12 control(s) that nothing tests"* about a suite that had just
failed exactly as designed.

Measured: identical command, identical files, run in the lane worktree and in a copy
outside `agent-factory`. Only the padding differs. **This is F19's shape one file over — a
pattern that had only ever been shown to match the reassuring case.** It was found because
the fix for the first defect changed the answer.

---

## 4. A defect this session introduced, and found by tracing rather than by a test

`reap_expired_leases` walks `_pipelines.values()` directly. Microseconds before this lane;
terminating cloud work shells out to `az` with 30- and 120-second timeouts, so the moment
termination moved inside that loop the window became **minutes** — and an HTTP handler
creating a pipeline during it raises `RuntimeError: dictionary changed size during
iteration`, killing the reaper thread that nothing restarts.

Walks a snapshot instead. A lock is the wrong answer: this module has no in-process lock
of its own (F21) and holding one across network I/O on the reaper thread would stall every
dispatcher behind an Azure timeout. Negative control: a terminator that creates a pipeline
mid-call, which is exactly what a slow `az` gives an HTTP handler time to do.

---

## 5. `truthful` — the real record is corrected at last

Approved by Paul after the dry run, which the previous session could not do because the
main checkout's data directory is outside the worktree.

```
pipe_29b8edf6   running -> failed
    basis            MEASURED
    clean            False
    failures in log  1
    closed because nothing further can ever run: True
```

Dry run and apply agreed exactly, and the apply re-reads each correction against the one
the dry run predicted. **No-regression, checked rather than assumed:** `pipe_fc674dfd` is
untouched at `created` with no verdict — six pending stages, no failed dependency, so
genuinely un-started. A reconciler that closed it too would make the record agree with the
log by lying in the other direction. Rollback captured in `rollback-main/` before the
write.

---

## Mutation harnesses after this session

| harness | before | after |
|---|---|---|
| `mutate_readiness_probes.py` — do the GATES depend on the controls? | 8 of 8 | **12 of 12** (the two extra are the review's own edits: the registration call, and `_report_run`'s body) |
| `mutate_control_plane.py` — do the TESTS depend on the controls? | 8 of 8 | **15 of 15** (12 after session 2's first pass; the 409 status, the control name in the body and the sweep budget came from the review) |

New mutations, all LOAD-BEARING: the termination call; the durable handle; the ownership
check that fails closed; the refusal to believe a verdict outside the vocabulary.

## Suites

| suite | result |
|---|---|
| `prefect-connectors` `tests/orchestrator` | **697 passed, 1 failed** at the end of session 2. Earlier in this file: 673 passed / 674 collected — I wrote 694, corrected it to 674, and 674 was the COLLECTED total. Wrong three times, corrected each time by someone re-deriving it |
| `agent-factory` `pytest` | **175 passed, 2 xfailed** |

The one failure is `test_logbook.py::TestResolution::test_recurrence_after_resolution_is_marked_regressed`,
pre-existing and unrelated — it fails identically on the unmodified checkout at `3da40f6`.

---

## Handover — still NOT done

1. **Nothing has run.** Unchanged from the last session and still the largest gap. Every
   control here is proven against a driven engine, a test suite and a browser. None has
   been watched refusing during a *live* migration, because the orchestrator has not run
   since 2026-05-28.
2. **No container has ever been deleted by this code.** The three `az`/Prefect seams in
   `cloud_reaper.py` are the untested surface, by construction. The first supervised run
   with an expired lease is what would exercise them, and the safest way to try it is with
   `ORCHESTRATOR_USER_SUFFIX` set — without it `owned_by_this_instance` returns False and
   every termination is NOT_ATTEMPTED, which is safe but proves nothing.
3. **Every stage dispatched before this session carries no handle**, so a reap of any of
   them reports NOT_RECORDED. That is honest, and it is not coverage.
4. **`MAX_ATTEMPTS_PER_STAGE = 5`, `MAX_PARALLEL_STAGE_DISPATCH = 4` and
   `LEASE_GRACE_MIN = 15` remain ASSUMED, not derived.** No live throughput has
   calibrated them.
5. **`ceiling` and `cost` still FAIL** — no spend check before dispatch. Same file, but
   the judgement lane's list.
6. **`_reachable` computes the greatest fixed point**, so two mutually-dependent `pending`
   stages keep each other alive. Latent — pipeline templates are static and acyclic.
   Carried forward unfixed from the last session, deliberately.
7. **`jira_notifier` still does not read the `reopenable` flag** (F22), so an early close
   can post a wrong, client-visible completion and latch it.

---

# The independent read, and the two things it found that were dead in production

An opus reviewer was given this lane's gates and the five questions the lane's brief
requires: has each control been **watched refusing**; which numbers were measured and which
inferred; **is this goalpost-moving**; what changed that nothing tests; correctness and
blast radius.

It reproduced everything it reported, and **every finding below was re-derived here before
it was fixed** — the sub-agent's report is a claim, not a measurement (F5).

## ⛔ 1. The cap's override was STILL unreachable. The route answered 404.

The previous section of this document claims the override now reaches the wire. It did not.

`ControlRefused` subclasses `ValueError` — deliberately, and its own docstring says so, "so
the HTTP layer's existing handlers turn it into a 4xx rather than a 500". *Which* 4xx is
not free. `_handle_post_pipeline_restart`'s `except ValueError` answers **404**, and both
of the dashboard's retry buttons POST to `/restart`. 404 says *the pipeline does not
exist*. The two handlers did not even agree — `/retry-stage` answered 400 for the identical
exception, and nothing in `server.py` mentioned `ControlRefused` at all.

Measured by driving the real handler with a stage at the cap: `404`.

### And the browser probe could not see it, for a reason worth keeping

The probe took deliberate care to use **the engine's real refusal message** rather than one
typed into the test — that is finding F19's discipline, and F19 is about a message. It then
wrote `{status: 400}` into its own fetch stub. The status is the half the browser guard
actually branched on.

So: the half that had already gone wrong once was measured, and the half that had not was
invented. Eight green checks over a control no operator could reach. One changed literal in
the review exposed it.

**The generalisation, now F25: take the whole answer from the thing that answers.** Anything
a probe supplies to itself is a premise, and the part nobody has been burned on yet is
exactly where the invention will be.

### What was done

* `_send_refusal` answers **409 Conflict** — the request was understood, the resource
  exists, the state forbids it — with `{"control": "attempt_cap", "refused": true}`.
  409 is emitted from nowhere else: `_send_refusal` is its only source and its only two
  callers are `except ControlRefused` clauses, so a client may treat 409 as a refusal
  without reading the body.
* The dashboard branches on the **field**. The regex over English prose is gone entirely —
  a stronger answer to F19 than a better-tested pattern.
* `tests/orchestrator/test_control_refusal_status.py` asserts the status and body on both
  routes, that a genuinely missing pipeline still reads as missing (the same collapse
  pointing the other way), that a reasoned override still gets through, and — structurally,
  by AST — that no future `_handle_*` can reach a cap-checked engine call without a
  refusal clause.
* The probe now drives `_handle_post_pipeline_restart` and takes **status and body** from
  it. Against a 404-answering server it fails six of ten checks (`dashboard/before-404.txt`).
* A second-order defect behind it: `retryWithCapOverride` toasted success without reading
  `dispatched`. The dispatch ceiling is checked *before* the `_cap_grant` is consumed, so
  with four stages already dispatched the override succeeds and nothing runs. It now says
  which happened.

**Checked and NOT defects**, recorded so nobody re-opens them: the structural guard also
flagged `_agent_restart` and `_ci_image_restart`. `_ci_image_restart` wraps its call in
`except Exception`; `_agent_restart` is bare, but both call sites inside
`pipeline_agent._handle_stage_failed` are wrapped and record `retry_failed`. So the
watchdog survives the cap refusing it — which matters, because the watchdog is the path
that re-dispatched one permanently-failing stage every thirty minutes overnight on
2026-08-13, and it is now guaranteed to meet the cap.

## ⛔ 2. The reaper's cloud half could be entirely dead, with the gate PASS and the suite green

Everything connecting the running server to the new reaper was a substring search. The
reviewer deleted the registration call and gutted `_report_run`'s body — **keeping the
import** — and got:

```
BEFORE   1 failed, 677 passed   |   PASS  Is dispatched work either finished or killed?
AFTER    1 failed, 677 passed   |   PASS  Is dispatched work either finished or killed?
                                     . 3 of 3 flow-run launch sites report their handle
                                     . server binds the recorder into every script stage: yes
                                     . server registers the cloud terminators at startup: yes
```

Every wiring line reading "yes" over a system where no handle is ever recorded and no
terminator ever registered. Reproduced here before fixing.

Why each grep survived:

| check | why it did not see the deletion |
|---|---|
| `"cloud_reaper" in src` | satisfied by the surviving `import` line alone |
| `src.index("cloud_reaper") < src.index("reaper_thread.start()")` | compares **string positions**; the import satisfies it, and so would a comment |
| `count("_report_run(ctx,")` | counts **call sites**, so gutting the callee is invisible |

This is F18 one hop further out. F18 was a probe handing itself its precondition; this is a
probe checking that a *wire exists* by looking for the word. **If a check would still pass
with the function body deleted, it is not measuring the function.**

### What was done

`server.build_script_context(req, wt_path=None)` and
`server.wire_cloud_terminators(engine)` are named seams, so the tests and the gate **call
them and ask the engine what it holds**:

* the returned context's callback really writes a handle to the record, and to **its own**
  stage — a script cannot report against someone else's run;
* `_TERMINATORS` afterwards contains `prefect_flow_run`, and the registered function **is**
  `cloud_reaper.terminate_prefect_flow_run` — `callable()` would have accepted a no-op,
  which is the same shape as the greps this replaced;
* `_report_run`'s **body** is driven, including that a broken engine seam cannot abort a
  backfill;
* launch sites `== ` reports, not `>=`, so a surplus mention cannot mask a missing one;
* ordering is asserted by **AST statement order**, not string index;
* the gate-check path builds its context through the same seam, and exactly one
  `ScriptContext(` construction site is asserted — the no-op default recorder is
  fail-**open**, so a hand-built context on a path that later launches cloud work would
  drop its handle silently.

The gate does all of this too, and drives `_report_run` itself. If `prefect_ops` will not
import it reports NOT-IMPORTABLE rather than quietly falling back to the count.

Both of the reviewer's edits are now mutations. `mutate_readiness_probes.py` gained a
per-mutation **target file** so a mutation can reach `server.py` and `prefect_ops.py`, and
its scratch tree now carries `.deploy` — without it `prefect_ops` cannot import and the
gate would FAIL for a reason unrelated to the mutation, which is a kill credited to the
wrong half (F18's tail).

## Finding 3 — an unbounded reap is the ceiling's own outage, arriving through the reaper

Traced, not reproduced: there is no Azure subscription here.

`_reaper_loop` runs `reap_expired_leases()` and then `dispatch_deferred_stages()`
**sequentially on the same thread**, and per F14 that sweep is the only ungated path that
ever picks a ceiling-deferred stage back up. Handles accumulate without bound —
`trigger_backfill_and_wait` records one per `create_flow_run` inside its launch loop, so a
30-partition backfill retried twice leaves ~90 on a single stage — and each costs up to
`az container list` 30s + `az container show` 20s + `az container delete` 120s.

So an unbounded reap does not merely run long: it strands exactly the pipelines the ceiling
deferred. **The outage the ceiling was added to prevent, arriving through the reaper.**

`TERMINATION_BUDGET_SEC = 120` bounds the whole sweep, not each stage. What it does not
reach is `NOT_ATTEMPTED` with its reason, **keeps its handles**, and is retried next sweep —
the budget defers work, it does not discard it. Four negative controls, including that a
sweep within budget still terminates everything, because a budget that refuses everything
is not a budget.

## And one the harness found about itself

Adding `_deadline` to the termination call stopped **both** harnesses' anchors for "the
call that kills the cloud work" from matching. The connectors harness reported
ANCHOR-MISSING and exited 1. The factory harness did not — it had last been *run* before
the refactor, and its "All 12 mutations flipped" was already quoted in a commit message: a
true statement about a tree that no longer existed.

A mutation anchor is a copy of production source, so it rots on refactor, and each harness
takes ~20 minutes. `tests/test_mutation_anchors_still_match.py` now checks all 28 anchors
in 0.07s inside the ordinary suite, so the slow harness is never what discovers a stale
one. Recorded as F29.

## What the review confirmed rather than overturned

Re-derived independently by the reviewer: the 26 negative controls; 12 of 12 connectors
mutations and 10 of 10 probe mutations at that commit; that the harness no longer touches
the real tree; the `-q` rootdir inheritance, checked hardest because it was the most
surprising; the real-record write and its no-regression claim, by diffing the rollback
snapshot against the live file (two records before, two after, exactly one field changed);
and that the `test_logbook` failure is pre-existing on every tree.

It also confirmed the gate was made **strictly harder, not merely different** —
`g_orphans_are_reaped`'s old pass condition is now an explicit `_fail` branch — while
noting correctly that three of the new sub-conditions were greps, which is Finding 2 above.

**Numbers it corrected:** `674 passed` was wrong (673 at that commit); the document's
headline still carried the previous session's `7 of 30 -> 14 of 30`; and "3 new probe
mutations" in a handoff was 2. Silence on everything else in that category means checked.

## Categories where the review found nothing — checked, not skipped

The four-verdict vocabulary and the refusal to believe an unrecognised one; the
NOT_RECORDED-vs-absence distinction in the engine, the audit event, the reap event and the
operator-facing sentence; the ownership fail-closed rule and run-id matching; the reap →
`_close_if_terminal` reconciliation (F17); in-process corruption of the pipeline store from
the new script-thread writer (two candidate paths, both died in verification); double
dispatch; and whether `apiStrict` breaks any existing dashboard path.

## ⚠ A decision that should be made out loud, not inherited from a docstring

`cloud_reaper.is_armed()` defaults **ON**, against the production resource group
`aldcprodrsgpprefectworkers1c`, with an env-var kill switch as the only brake and no
dry-run mode. The module argues the case explicitly — a default-off switch is off during
the incident — and the ownership check fails closed. The reviewer agreed with the argument
and still flagged it, correctly: *"an unattended process will `az container delete` in prod
by default"* is a call for a human to make, not something to inherit from a comment.
**Nobody has made it yet.**
