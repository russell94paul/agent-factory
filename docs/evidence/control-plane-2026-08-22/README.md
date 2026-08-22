# Control-plane lane — evidence

Lane `control-plane`, gates `cap`, `reaper`, `concurrency`, `bounded`, `truthful`,
`from-history`. Code in `prefect-connectors/orchestrator/`, branch `lane/control-plane`.

**Measured: 7 of 30 gates → 14 of 30. All six lane gates FAIL → PASS.**

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
