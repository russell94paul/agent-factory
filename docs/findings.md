# Findings ledger — corrected premises, so no lane pays for the same mistake twice

**Read this before starting a lane. Append to it before closing one.**

Parallel lanes fail in a specific way: two sessions independently inherit the same wrong premise
and both build on it. That is not hypothetical here — R1 named Prefect as the cause of the
false-`succeeded` defect, the claim was carried into R3 as an entire question, and nobody checked
it until a one-line grep did. Every entry below is a premise that looked true and was not.

## What belongs here

Only **corrections to things another lane would otherwise believe.** Not progress, not decisions,
not what you built — boot prompts and `docs/evidence/` already carry those. The test is: *would a
session in another lane get this wrong without being told?*

Every entry carries four things, and an entry missing any of them is not a finding:

| Field | Why it is mandatory |
|---|---|
| **BELIEVED** | the premise as another lane would state it, in their words |
| **ACTUALLY** | what is true |
| **MEASURED BY** | the discriminating test, so the reader can re-run it rather than trust you |
| **AFFECTS** | lanes, gates or files that inherit the premise |

⭐ **Closing a lane with nothing to add is itself an entry.** Write `NOTHING TO REPORT` with the
date and lane. Silence has to mean "checked and found nothing", not "nobody looked" — the same
distinction between ZERO and NOT-RECORDED that the contract's four verdicts exist to protect.

---

## 2026-08-22 · session: evaluator isolation + render loop

### F1 — The false `succeeded` has nothing to do with Prefect

- **BELIEVED** — "Prefect's final-state rules let a parent flow return COMPLETED over failed
  children" (R1, then carried into R3 as a whole question).
- **ACTUALLY** — the build plane at `:8765` is a bespoke engine that **does not import Prefect**.
  The verdict is computed from a last-write-wins per-stage status field, so a stage that failed
  100 times and succeeded once contributes nothing to `any_failed`.
- **MEASURED BY** — `grep -n "import prefect" orchestrator/pipelines.py` → no hits, at `3da40f6`.
  One grep. Full write-up in `docs/evidence/false-succeeded-mechanism.md`.
- **AFFECTS** — control-plane lane (`truthful`, `from-history`), and any Prefect-idiom fix. R2's
  recommended primitives are **not available to us** and each must be built; see
  `docs/research/answers/R2-followup.md`.

### F2 — The 5 unmeasured attempts cannot be placed in the sequence

- **BELIEVED** — the 5 `stage_started` events with no outcome can be interleaved into the run
  order, since 115 starts − 110 terminals = 5.
- **ACTUALLY** — walking the log and pairing each start to a following terminal locates **24**
  unterminated starts, not 5. Terminals do not reliably follow their own start, so any placement
  is fabrication. They are drawn past a divider, in no order, and the figure says so.
- **MEASURED BY** — walk `pipe_4ba17e16.json` events for `trigger-run` in order, incrementing on
  `stage_started` and clearing on a terminal; count the starts cleared by another start → 24.
- **AFFECTS** — anything reasoning about attempt ordering, retry counts, or per-attempt cost. The
  earlier version of this inference reported 82 failures where the counters say 100.

### F3 — `grain_confirmed` is not a field, and adding it breaks every blueprint load

- **BELIEVED** — settle the grain question by setting `grain_confirmed` in
  `blueprints/windsorai_gep.yaml`.
- **ACTUALLY** — `ConnectorTarget` has no such field and `targets.load_target` raises on unknown
  keys by design. Adding it to the YAML breaks every load until the dataclass gains the field.
- **MEASURED BY** — `_ALLOWED = set(ConnectorTarget.__dataclass_fields__)` in `factory/targets.py`;
  `grain_confirmed` is absent.
- **AFFECTS** — grain lane. Add the field to `ConnectorTarget` in the same commit.

### F4 — The loop gates are measuring a three-month-old history

- **BELIEVED** — "3 of 14 runs finished", "a stage fails 6.1× more than it succeeds" and "4
  orphans" describe the system now.
- **ACTUALLY** — all 14 audit files date from **2026-05-26 to 05-28**. Nothing has run in the
  orchestrator since, and it is not currently running (nothing listening on `:8765`). The numbers
  are true of a history that stopped three months ago; the gates do not say so.
- **MEASURED BY** — `ls -la orchestrator/data/audits/*.json`; `netstat -ano | grep :8765` → empty.
- **AFFECTS** — every loop and judgement gate, and any claim that a control "fixed" a rate. Fixing
  a control changes nothing measurable until runs happen again. Making the gates carry the age of
  their evidence is unclaimed work.

### F5 — Instruments in this repo have produced three confident false results in one session

- **BELIEVED** — a probe that returns a specific number has measured something.
- **ACTUALLY** — three separate false results, all confident, all in one day:
  1. the render probe measured across **both** svgs in `#failed` → *"119 marks, 1 inside the band,
     min gap −201px"*;
  2. it reported a text collision on `--max-turns` × `--max-budget-usd` — false, because
     `getBoundingClientRect()` on a **wrapped inline** returns the union of its line boxes;
  3. the tracker test used `html.escape()` with default `quote=True`, turning `impeccable's` into
     `impeccable&#x27;s`, and reported the `chain` gate missing from a page it was plainly on.
- **MEASURED BY** — each was caught by checking the finding against the DOM before reporting it.
  None would have been caught by re-running the probe.
- **AFFECTS** — every lane. Before reporting a defect, verify it against the thing itself. The
  readiness gate for this already exists in spirit: *a probe must not be able to match its own
  source.*

### F6 — `claude-in-chrome` is not the only way to render, and is not worth waiting for

- **BELIEVED** — the render pass is blocked until the Chrome extension connects.
- **ACTUALLY** — Playwright drives the same installed Chrome with none of that chain in the path.
  `pip install playwright`, then `python scripts/render_pass.py`. The extension chain is healthy
  at every inspectable link (installed, enabled, right account, native host registered and
  spawnable, no policy) and `list_connected_browsers` still returns `[]`.
- **MEASURED BY** — `docs/evidence/render-pass-2026-08-22.md`, which tabulates every link.
- **AFFECTS** — artifact lane, and anyone tempted to spend another session on the extension.

### F7 — I fed R6 a false constraint, and it changed the answer

- **BELIEVED** — stated as fact in `docs/research/R6-automation-and-alerting.md`: *"there is
  currently no runner budget or appetite for one."* I wrote it as a constraint on the question.
- **ACTUALLY** — the same GitHub org already runs three Actions workflows in
  `prefect-connectors` (`ci.yml`, `quality-gate.yml`, `branch-sync.yml`). Actions is available and
  in daily use. `agent-factory` simply has no `.github/workflows` directory, which is an absence,
  not a constraint.
- **MEASURED BY** — `ls prefect-connectors/.github/workflows/` → three files. One command.
- **AFFECTS** — every lane, and R6's answer itself. R6 explicitly deferred *"a full CI on every
  push"* on the strength of my sentence, and instead ranked a nightly scheduled check first. Read
  its Q1 with that correction in hand: CI-on-push may well be the right first move after all, and
  the honest position is that R6 was never asked the real question.

⭐ **This is the F1 pattern, committed by me, inside a prompt whose own Method note warns against
it.** *An object named by a ticket, boot prompt or handoff is a hypothesis, not a finding.* A
constraint asserted in a research prompt is exactly that kind of object, and I asserted one I had
not checked — while telling the reader to check everything I asserted. Before writing a constraint
into a prompt, measure it; a research pass optimises against the world you describe, not the one
you have.

### F8 — Two servers can hold port 8099, and you verify against the stale one

- **BELIEVED** — killing the listener on 8099 and starting a new one means the page you then
  fetch is the page you just built.
- **ACTUALLY** — `local_tracker.py` sets `socketserver.TCPServer.allow_reuse_address = True`, so a
  second process binds the same port happily. `netstat` showed **two** LISTENING entries and curl
  was served by the older one. Every "restart and check" in this session could silently have
  verified against pre-change code.
- **MEASURED BY** — `netstat -ano -p TCP | grep :8099 | grep LISTENING` → two rows, two PIDs. The
  tell was a freshly-started server whose log file stayed empty while the page still answered 200.
- **AFTER** — kill **every** PID on the port, confirm the count is 0, then start one and confirm
  it is 1. Do not kill `head -1`.
- **AFFECTS** — every lane. Any local service verified by restart-then-fetch, and specifically
  anyone trusting a tracker page to reflect the code they just edited.

### F9 — ast.parse does not catch every SyntaxError; compile() does

- **BELIEVED** — `ast.parse(src)` passing means a patched module is syntactically valid.
- **ACTUALLY** — it builds the tree only. Symbol-table errors are invisible to it: `global X`
  appearing after X is used elsewhere in the same function parses cleanly and fails at compile.
  A patch script printed "wired and parses" and the server then refused to start.
- **MEASURED BY** — on the same source, `ast.parse(t)` succeeded and `compile(t, "f.py", "exec")`
  raised `SyntaxError: name '_HANDOFF_NOTE' is used prior to global declaration`.
- **AFFECTS** — every lane, and any patch-then-verify loop. Use `compile(src, name, "exec")`:
  same cost, catches strictly more.

### F10 — Windows Terminal eats semicolons in the command you hand it

- **BELIEVED** — `wt new-tab ... powershell -Command "Set-Location X; claude Y"` runs both halves.
- **ACTUALLY** — `;` is **wt's own subcommand separator**. It splits the invocation there and
  tries to launch the remainder as a program. The observable result is a tab that opens in the
  right directory and does nothing else, plus
  `error 2147942402 (0x80070002) ... The system cannot find the file specified`.
- **MEASURED BY** — Paul's first real click. Every prior test was a dry run that inspected the
  command without executing it, so nothing had exercised wt's parsing.
- **AFFECTS** — every lane, since any of them can launch a terminal. Put **no semicolons** in the `-Command` payload;
  use `--startingDirectory` for the cwd. And note the lesson under it: a dry run proves the
  command you built, never the thing that will parse it.

---

## 2026-08-22 · lane: control-plane

### F11 — Two of the six gates this lane was given could never have passed

- **BELIEVED** — the readiness gate list is the specification: work the system until each
  gate flips. `bounded` says "no attempt cap on restart" and `reaper` says "no lease,
  timeout or reaper", so building a cap and a reaper will move them.
- **ACTUALLY** — `g_failure_is_bounded` and `g_orphans_are_reaped` each had **exactly one
  return path, `_fail`**. They were constants wearing an instrument's clothes: no work on
  the build plane could ever have moved them, and both had been read for a day as
  measurements of an unbounded, unreaped system. `g_orphans_are_reaped` also searched
  `orchestrator/engine/work_guard.py` — whose lease covers **repo locks between agents** —
  and never looked in `pipelines.py`, where `reclaim_orphaned_stages` already lived.
  A third, `g_corpus_is_tamper_evident` (gate `corpus`, **certify lane**), is the same
  shape: `_fail` on every branch including the one where all four of its sub-checks pass,
  so moving the corpus out via `$AGENT_FACTORY_EVALS` — the fix the gate itself
  recommends — would change nothing it reports.
- **MEASURED BY** — AST-walk `factory/readiness.py`, counting the `Return` kinds each probe
  can reach:
  ```
  g_failure_is_bounded   returns=['_fail']  raises=0
  g_orphans_are_reaped   returns=['_fail']  raises=0
  ```
  Now enforced by `tests/test_readiness_probes_can_pass.py`, which asserts every gate has a
  reachable PASS **and** a way of refusing. It fails loudly on `corpus`, allowlisted as
  `xfail` with the argument written out.
- **AFFECTS** — every lane. **Read your gate's probe before working the gate.** A gate is a
  claim about an instrument, and three of thirty were not instruments. The stronger check
  is `scripts/mutate_readiness_probes.py`: remove the control, the gate must fall off PASS.

### F12 — The `honest` gate counts a run recorded as FAILED as one reporting success

- **BELIEVED** — `g_success_means_correct` measures "a run reports success over failures it
  could not see", so a run in its bad list claimed to succeed.
- **ACTUALLY** — it counts any run whose log holds **both** a `pipeline_completed` event and
  at least one `stage_failed`. It never reads the status the run actually reported. A run
  correctly recorded as `failed` lands in the list identically to one that lied.
  `pipe_29b8edf6` is now exactly that case.
- **MEASURED BY** — read `g_success_means_correct` in `factory/readiness.py`: the only
  fields consulted are `event_type`. Then read
  `prefect-connectors/orchestrator/data/audits/pipe_29b8edf6.json` — its `pipeline_completed`
  event carries `{"final_status": "failed"}` in `details`, so the correction is available
  and one line long.
- **AFFECTS** — the judgement lane, which owns `honest`. Its headline number will overcount
  the moment any failing run is correctly closed — which is what fixing `truthful` does.

### F13 — An empty `allowed_tenants` is reported as UNMEASURABLE, but it is a measurement

- **BELIEVED** — `tenancy` returning UNMEASURABLE means no instrument could be established.
- **ACTUALLY** — `g_tenancy_declared` reads the blueprint successfully and raises
  `Unmeasurable` when the list is empty. The instrument worked; the answer was "none
  declared". That is FAIL. Collapsing "I could not look" into "I looked and found nothing"
  is the exact confusion the contract's four verdicts exist to prevent, and it is the only
  non-pass outcome that probe has — so `tenancy` has never been able to refuse anything.
- **MEASURED BY** — `factory/readiness.py::g_tenancy_declared`; its only non-`_pass` exit is
  `raise Unmeasurable`. Caught by `tests/test_readiness_probes_can_pass.py` on first run,
  allowlisted as `xfail`.
- **AFFECTS** — the certify lane, which owns `tenancy`.

### F14 — `recover_stale_pipelines` has one caller and it is switched off by default

- **BELIEVED** — a stage left `pending` will be picked up again, because
  `recover_stale_pipelines` sweeps periodically.
- **ACTUALLY** — it has **exactly one caller**, `pipeline_agent._run_watchdog`, which returns
  early on `if not _enabled` — and the agent is disabled by default, deliberately, per
  HACKATHON.md. The only other re-offer path is `on_session_complete`, which fires **only
  when a stage in that same pipeline completes**. A run with nothing dispatched has nothing
  that will come back for it.
- **MEASURED BY** — `grep -rn "recover_stale_pipelines" orchestrator/` → one call site,
  `pipeline_agent.py:410`; the guard is at `pipeline_agent.py:406`.
- **AFFECTS** — every lane; the `concurrency` gate specifically. Anyone who leaves work
  `pending` and relies on "the next sweep". This lane's
  dispatch ceiling did exactly that and stranded whole pipelines until
  `dispatch_deferred_stages()` was added on the reaper's ungated thread.

### F15 — A git worktree of `prefect-connectors` has no audit history at all

- **BELIEVED** — making a worktree of the connectors repo gives you the system to measure.
- **ACTUALLY** — `orchestrator/data/` is gitignored (`orchestrator/data/.gitignore` is `*`),
  so a fresh worktree has **no `audits/` and no `pipelines.json`**. Every history-measured
  gate then returns UNMEASURABLE — which is not a pass, but is easy to read as "nothing
  wrong here" in a table of thirty rows.
- **MEASURED BY** — `git check-ignore -v orchestrator/data/audits/pipe_4ba17e16.json` →
  `orchestrator/data/.gitignore:1:*`. Then, against a copy of `orchestrator/` with `data/`
  removed: **14 gates report UNMEASURABLE, against 4 with the data present.** Ten gates
  silently stop measuring.
- **AFFECTS** — every lane, and the `control-plane` and `judgement` lanes specifically, since
  both work in `prefect-connectors`. Copy `audits/` and
  `pipelines.json` in, or you are measuring an empty world. Also: `factory/readiness.py:34`
  resolves the checkout as a **sibling of the factory root**, so from an agent-factory
  worktree it looks for `.worktrees/prefect-connectors`, not `repos/prefect-connectors`.

### F16 — `audit.get_audit()` cannot tell a missing log from a corrupt one

- **BELIEVED** — `get_audit(pid)["events"]` is the run's history.
- **ACTUALLY** — it returns `{"pipeline_id": pid, "events": []}` for **three** different
  situations: the audit trail is unconfigured, the file does not exist, and the file will
  not parse. Anything computing a verdict from that empty list turns an unreadable history
  into a clean bill of health — which is the false-`succeeded` defect (F1) rebuilt one
  layer down.
- **MEASURED BY** — `orchestrator/engine/audit.py:200-207`; three separate paths, one
  return value. `pipelines.stage_outcomes_from_history()` now raises `HistoryUnreadable`
  instead, and `terminal_verdict()` fails **closed** with `basis="UNMEASURABLE"`.
- **AFFECTS** — every lane. Anything reading the audit trail to decide something, in either
  repo; the `truthful`, `honest` and `from-history` gates most directly.

### F17 — A control that closes a stage with no session behind it strands its run

- **BELIEVED** — marking a stage `failed` is enough; the pipeline's own bookkeeping closes
  the run.
- **ACTUALLY** — the run is closed by `on_session_complete`, which fires **only when a
  session reports**. A stage closed by a reaper or refused by an attempt cap has no session
  left to report, so the record sits at `running` over a log ending `stage_failed` — which
  is `pipe_29b8edf6`'s exact shape, the defect the `truthful` gate exists to catch,
  recreated by the controls added to prevent orphans.
- **MEASURED BY** — driving `reap_expired_leases()` against a one-stage pipeline:
  ```
  reaped: [{'pipeline_id': 'pipe_x', 'stage': 'only', ...}]
  stage : failed
  PIPELINE STATUS AFTER REAPING THE ONLY STAGE: running
  ```
- **AFFECTS** — the judgement lane, and anyone adding a control that terminates a stage.
  Every such path must reconcile afterwards. `reap_expired_leases()` now calls
  `reconcile_status_with_history()`, and server.py's periodic loop reconciles
  unconditionally so the cap-refusal path is covered too.

### F18 — A probe that hands itself the state it wants to see has measured nothing

- **BELIEVED** — a gate that drives the engine and watches a control refuse is strong
  evidence. This lane replaced five greps with behavioural probes on exactly that argument
  and reported all six gates green.
- **ACTUALLY** — two of the five passed over systems with their defect intact, and an
  independent review found both by removing one line each:
  - `cap` built its own input (`_scratch_stage("stuck", _attempts=cap)`). Deleting the
    single line that *writes* `_attempts` left the gate reporting "capped, and was watched
    refusing" over an engine whose cap could never fire.
  - `from-history` checked `failures_in_log` and `clean`, both computed from the log
    **independently of `any_failed`**. Reverting `any_failed` to the original
    last-write-wins expression — one edit — left the gate PASS and all 45 tests passing.
  A probe that constructs the precondition proves the *comparison* fires. It does not
  prove the system ever reaches that state, which is the thing the gate claims.
- **MEASURED BY** — copy `orchestrator/` to a scratch tree, delete exactly one line, point
  `$PREFECT_CONNECTORS` at the copy, re-run the gate. `scripts/mutate_readiness_probes.py`
  now carries both mutations; each flips its gate PASS→FAIL only after the fix.
- **AFFECTS** — every lane. A behavioural probe is better than a grep and is still not
  self-validating. **Write the mutation before you believe the gate**, and make it remove
  the property rather than perturb it. And when a probe checks several things, ask which
  of them the mutation actually killed: this lane's compound mutation reported one kill
  and credited it to the wrong half.

### F19 — A regex guard in readiness.py has never matched the line it was written to catch

- **BELIEVED** — `cap`'s pass condition includes `not cleared`, guarding against the
  dashboard's "clear context" zeroing the attempt counter. This lane removed the offending
  `pop` from `server.py` and described the gate as enforcing it.
- **ACTUALLY** — the pattern is `pop\(\s*.._retry_count`. After `pop(` the source reads
  `"_retry_count`, so `..` consumes `"_` and the literal then has to match `retry_count`
  against `retry_count` one character too late. **It matches nothing.** The `not cleared`
  half of the condition has been vacuously true since `ea888b0`, and the lane repeated the
  claim without testing the pattern.
- **MEASURED BY** — `re.search(r"pop\(\s*.._retry_count", '        s.pop("_retry_count",
  None)')` → `False`, against the real line from `server.py` at `3da40f6`. The corrected
  pattern matches the quote explicitly and returns `True`; reintroducing the `pop` in a
  scratch copy now flips `cap` to FAIL.
- **AFFECTS** — every lane, and the `judgement` lane most (`checks`, `general`, `cost` and
  `ceiling` all rest on `_grep` or `re.findall` conditions). **A negative grep result is
  not evidence unless the pattern has been shown to match a positive case.** An absent
  match and a broken pattern are indistinguishable, and the broken one always reports the
  reassuring answer.

### F20 — An instrument that counts its own writes reports the wrong period

- **BELIEVED** — the audit files date from 2026-05-26 to 05-28 (F4), so a gate citing that
  window tells the reader how old its evidence is.
- **ACTUALLY** — `_history_window()` took **every** event in the files. The moment this
  lane's reconciler wrote `status_reconciled` and `verdict_recorded` events, the window
  stretched to "2026-05-26 to 2026-08-22" and evidence about a history that stopped in May
  began reading as though the system had been busy through August. The fix that made the
  gates carry the age of their evidence is the same fix that corrupted it.
- **MEASURED BY** — `python -m factory.readiness | grep "history,"` before and after
  restricting the window to events a *run* produces: `2026-05-26 to 2026-08-22` becomes
  `2026-05-26 to 2026-05-28`.
- **AFFECTS** — every lane, and anything that writes to the audit trail — which now
  includes the control plane, the reconciler and `scripts/reconcile_pipeline_records.py`.
  Any statistic over `audits/*.json` must exclude control-plane bookkeeping or it is
  measuring the measurer.

### F21 — `pipelines.py` has no in-process lock, and there are now three dispatchers

- **BELIEVED** — the file lock in `_flush()` makes concurrent access to the pipeline store
  safe enough.
- **ACTUALLY** — the file lock protects the *file*. `test_instance_isolation` states the
  rest in as many words: *"pipelines.py has no in-process lock of its own — the file lock
  is it."* Every read-then-write in that module is racy. This lane's dispatch ceiling was
  one: `free` was read at the top of `_build_stage_requests` and `status = "dispatched"`
  not written until an audit round-trip later, so two threads each granted the **full**
  ceiling — eight concurrent dispatches against four, on a shared 10-core quota. The same
  window let two callers dispatch the same stage, which for `trigger-run` is two ACI
  backfills against one landing schema.
- **MEASURED BY** — two callers each computing ready indices before either writes: 4 + 4
  granted against a ceiling of 4; and one stage reaching `_attempts: 2, status: dispatched`
  from a single ready set. Closed by `_DISPATCH_LOCK` plus a `status != "pending"` re-check
  under it.
- **AFFECTS** — the `judgement` lane, which edits the same file. There are now **three**
  dispatchers racing here — HTTP handlers, the agent watchdog, and this lane's reaper
  thread — and the reaper is the only one no toggle gates. Any new counter, ceiling or
  budget check added to `pipelines.py` must take `_DISPATCH_LOCK`, or it is advisory.

### F22 — `jira_notifier` latches on the first completion event and drops every later one

- **BELIEVED** — emitting `pipeline.completed` earlier (when the remaining stages became
  unreachable, rather than when they all resolved) is a bookkeeping improvement.
- **ACTUALLY** — `jira_notifier` returns immediately if `entry["completed"]` is set, and
  persists that latch. So an early close posts *"pipeline finished: failed"* to the
  client's ticket and permanently suppresses the real completion: the operator fixes the
  credential, retries, the run genuinely succeeds, and the correction never arrives. The
  ticket keeps a completion comment that is wrong, client-visible, and silent.
- **MEASURED BY** — `orchestrator/engine/jira_notifier.py:353-364`, the
  `if entry.get("completed"): return` guard and `_save_state()` beneath it, against
  `pipelines._close_pipeline`, which now emits from two code paths rather than one.
  Mitigated by a `reopenable` flag on the event; the notifier does not yet read it.
- **AFFECTS** — the `judgement` lane and anyone changing **when** a run reaches a terminal
  state. Changing the timing of a terminal event is not an internal change: at least one
  downstream consumer treats the first one as final and writes to a client-facing surface.

---

## 2026-08-22 · lane: control-plane (second session)

### F23 — `ControlRefused` subclasses `ValueError`, so `/restart` answers a refusal with 404

- **BELIEVED** — a control that raises `ControlRefused` gets a sensible HTTP answer for
  free, because it subclasses `ValueError` and "the HTTP layer's existing handlers turn it
  into a 4xx rather than a 500". That sentence is in the exception's own docstring.
- **ACTUALLY** — *which* 4xx is not free, and it was wrong on the route that matters.
  `_handle_post_pipeline_restart`'s `except ValueError` answers **404**, and both of the
  dashboard's retry buttons POST to `/restart`. 404 tells the browser the pipeline does not
  exist, so no client can distinguish a refusal from a typo — and the attempt cap's
  override, which the cap's entire safety argument rests on, could never be offered. The
  two handlers did not even agree: `/retry-stage` answered 400 for the identical exception.
  Now 409 with `{"control": ..., "refused": true}` in the body, via `_send_refusal`.
- **MEASURED BY** — drive the real handler with a stage at the cap:
  subclass `server.OrchestratorHandler`, stub `_json_body`/`_send_json`/`_send_error_json`,
  set `_attempts = MAX_ATTEMPTS_PER_STAGE`, call
  `_handle_post_pipeline_restart("pipe_x")` with `{"stage_name": ...}` → `404`.
  `grep -c ControlRefused orchestrator/server.py` → `0`, at `a2c4820`.
  Now asserted by `tests/orchestrator/test_control_refusal_status.py`, including an AST
  check that no future `_handle_*` can reach a cap-checked call without a refusal clause.
- **AFFECTS** — the **judgement** lane most: `cost` and `ceiling` add controls to the same
  file that will refuse the same way. A new control that raises `ControlRefused` and is not
  caught explicitly inherits whatever status its handler's generic clause happens to use.
  Also every lane that adds a control a human is expected to be able to override.

### F24 — A wiring check that greps the source is satisfied by a surviving import

- **BELIEVED** — checking that the server is wired to a new mechanism with
  `"cloud_reaper" in source` / `"report_external_handle=" in source` is weak but adequate:
  if the string is there, the wiring is there.
- **ACTUALLY** — an independent review deleted the registration call and gutted the
  reporter's body, leaving the import and the call sites in place. **All three checks still
  read "yes", 677 tests still passed, and the gate still reported "dispatched work is
  leased, reaped and its cloud work killed"** over a system where no handle is ever
  recorded and no terminator ever registered. `"cloud_reaper" in src` was satisfied by the
  import alone; an ordering guard compared **string positions**, which the import also
  satisfies; and `count("_report_run(ctx,")` counts CALL SITES, so gutting the callee was
  invisible.
- **MEASURED BY** — in a scratch copy: replace `_cloud_reaper.register(engine)` with
  nothing and `_report_run`'s body with `pass`, then
  `PREFECT_CONNECTORS=<copy> python -m factory.readiness` → still PASS, all wiring lines
  "yes". Fixed by extracting `server.build_script_context()` and
  `server.wire_cloud_terminators()` as named seams the tests and the gate now **call**,
  asserting `_TERMINATORS` is non-empty and that a returned context's callback really
  writes a handle to the record. Both mutations are now in
  `scripts/mutate_readiness_probes.py`.
- **AFFECTS** — every lane. This is F18 one hop further out: F18 was about a probe handing
  itself its precondition; this is about a probe checking that a *wire exists* by looking
  for the word. **If a check would still pass with the function body deleted, it is not
  measuring the function.** Extract a named seam and call it.

### F25 — A probe that measures one half of an interface and invents the other

- **BELIEVED** — the browser probe for the cap override was rigorous: it derived the
  engine's real refusal **message** rather than typing one, precisely because F19 is about
  a pattern never shown to match a real line. Eight checks, all green.
- **ACTUALLY** — it wrote `{status: 400}` into its own fetch stub. The route answers 404,
  and the browser guard branched on the status. So the probe proved the half that had
  already gone wrong once and assumed the half that had not, and reported a control as
  reachable when no operator could reach it. One changed literal in the review exposed it.
  The probe now drives `_handle_post_pipeline_restart` and takes **status and body**
  from the thing that answers; run against the 404 server it fails six of ten checks.
- **MEASURED BY** — `scripts/dashboard_cap_override_probe.py`, before/after transcripts in
  `docs/evidence/control-plane-2026-08-22/dashboard/`. `before-404.txt` is the probe
  against a server that answers 404.
- **AFFECTS** — every lane that writes a probe against an interface. F19 said *a pattern
  must be shown to match a positive case*; the generalisation is **take the whole answer
  from the thing that answers**. Anything the probe supplies to itself is a premise, not a
  measurement — and the part nobody has been burned on yet is exactly where the invention
  will be.

### F26 — pytest inherits `addopts` from a directory ABOVE the repo, so output parsing depends on where the checkout sits

- **BELIEVED** — a harness that reads pytest's summary line works the same wherever the
  repo is.
- **ACTUALLY** — pytest walks **upwards** for its rootdir config. The connectors worktrees
  for these lanes live inside `agent-factory`, whose `pyproject.toml` carries
  `addopts = "-q"`, so the connectors suite silently inherits `-q` from an unrelated
  repository two directories up and prints a bare `10 failed, 36 deselected in 13.53s`.
  The same files anywhere else print `====== 10 failed … ======`. A harness anchored on
  `^\d+ (passed|failed)` matched the first and not the second, and announced
  *"12 control(s) that nothing tests"* about a suite that had just failed exactly as
  designed.
- **MEASURED BY** — run the identical command in the lane worktree and in a copy of the
  same tree in the system temp directory; only the padding differs.
  `grep addopts agent-factory/pyproject.toml` → `-q`; `prefect-connectors` has none of its
  own.
- **AFFECTS** — every lane, and anything parsing tool output from a nested worktree. Also a
  reason to be careful reading a *green* run: the inheritance flows both ways.

### F27 — the reaper thread is also the only ungated dispatcher, so anything slow in a reap strands work

- **BELIEVED** — making the reaper do more (kill cloud work, call `az`) costs only reap
  latency.
- **ACTUALLY** — `_reaper_loop` runs `reap_expired_leases()` and then
  `dispatch_deferred_stages()` **sequentially on the same thread**, and per F14 that sweep
  is the only ungated path that ever picks a ceiling-deferred stage back up. Handles
  accumulate without bound — `trigger_backfill_and_wait` records one per `create_flow_run`
  inside its launch loop, so a 30-partition backfill retried twice leaves ~90 on one stage
  — and each costs up to `az container list` 30s + `az container show` 20s +
  `az container delete` 120s. An unbounded reap therefore strands exactly the pipelines the
  ceiling deferred: **the outage the ceiling exists to prevent, arriving through the
  reaper.** Bounded by `TERMINATION_BUDGET_SEC = 120` for the whole sweep; work not reached
  is `NOT_ATTEMPTED` with its reason, keeps its handles, and is retried next sweep.
- **MEASURED BY** — traced call path (`server.py::_reaper_loop`, `pipelines.py`
  `_terminate_external_work`, `cloud_reaper.py` subprocess timeouts). **Not reproduced
  against real Azure** — there is no subscription here, so this is a traced path, not a
  measurement. The budget's behaviour is tested with a fake clock.
- **AFFECTS** — the **judgement** lane directly: `cost` and `ceiling` want a spend check
  before dispatch, and the obvious place is that same loop. Anything added there is added
  in front of the only sweep that rescues deferred work.

### F28 — a reaper that closes the record has done half the job, and the gate could not tell

- **BELIEVED** — `reaper` PASS ("dispatched work is leased and reaped, watched") meant
  dispatched work is either finished or killed.
- **ACTUALLY** — it killed only the **record**. The Prefect flow run and its ACI container
  survive the orchestrator, and the reaped stage's own error string handed that half to a
  human: *"if this stage launches cloud work, check whether it is still running."* The
  record was never the thing holding the 10-core quota. Now: a durable handle recorded at
  every `create_flow_run`, a terminator that fails closed on unproven ownership, and the
  contract's four verdicts rather than a boolean.
  ⚠ **`NOT_RECORDED` does not mean "it launched nothing"** — it means we cannot tell, and
  every stage dispatched before 2026-08-22 is in that state.
- **MEASURED BY** — delete the termination call in a scratch copy and re-run the gate:
  it used to stay PASS; it now FAILs. Both mutations in `mutate_readiness_probes.py`.
- **AFFECTS** — every lane that adds a control terminating work with an outside effect.
  Ask what the control's name promises, then ask which half of it the gate can see. ⚠ And
  note the limit that remains: **no container has ever been deleted by this code.** There
  is no Azure subscription in the suite, so the three `az`/Prefect seams are untested by
  construction.

### F29 — A mutation anchor is a copy of the source, so a refactor disarms it silently

- **BELIEVED** — "all N mutations flipped their gate off PASS" is a current fact about the
  tree. A mutation harness that reports every control load-bearing has certified the code
  as it stands.
- **ACTUALLY** — the harness works by holding a **copy of a line of production source** and
  replacing it, so the anchor is a duplicate and duplicates rot. Adding a `_deadline`
  argument to the reaper's termination call stopped both harnesses' anchors matching. The
  connectors harness caught it on the next run (ANCHOR-MISSING, exit 1) — but the factory
  harness had last been run **before** the refactor and was still reporting *"All 12
  mutations flipped their gate off PASS"*, a true statement about a tree that no longer
  existed, already quoted in a commit message. **An instrument whose input is a copy of the
  source certifies the version it last ran against, not the one in the tree** — and each
  harness takes ~20 minutes, so nobody re-runs it casually.
- **MEASURED BY** — `tests/test_mutation_anchors_still_match.py` (new): loads both
  harnesses' `MUTATIONS` lists and asserts every anchor appears **exactly once** in its
  target file. 28 anchors, 0.07s, in the ordinary suite. Shown non-vacuous by pointing
  `$PREFECT_CONNECTORS` at a scratch tree with one mutated line: it reports
  `its anchor appears 0 time(s)`.
- **AFFECTS** — every lane that owns a mutation harness, which is now the control-plane and
  (via `scripts/mutate_readiness_probes.py`) anyone editing a gate's control. Two rules
  follow: **re-run the harness after the last refactor, not before**, and never quote a
  load-bearing count that predates a change to the lines it anchors on.

### F30 — A budget that "defers" work defers nothing unless something comes back for it

- **BELIEVED** — bounding an expensive sweep is safe because the work it declines is kept on
  the record and retried later. The skipped item's own detail said so, the constant's
  docstring said so, and a test named `..._survive_for_the_next_sweep` asserted it.
- **ACTUALLY** — `_terminate_external_work` had **one caller**, `reap_expired_leases`, which
  only reads stages whose status is `dispatched` — and the reap sets the stage to `failed`
  three lines later. Every skipped handle sat on a stage nothing would ever read again. A
  stage with 90 accumulated handles would have killed one or two and **leaked the rest
  permanently**, each holding a core on a shared 10-core quota. ⭐ The test could not see it:
  it asserted the handles were still on the record, which a record nothing will ever read
  again satisfies identically. **The promise was in the test's name, not its body.**
- **MEASURED BY** — four sweeps with a full budget each: `['run-00']`, then `NOTHING`,
  `NOTHING`, `NOTHING`. After adding `sweep_unterminated_handles()`: 2, 1, 1, 1 — all five.
  `tests/orchestrator/test_cloud_reaper.py::TestSkippedHandlesAreRetried` asserts the
  **drain**, not the storage.
- **AFFECTS** — every lane adding a bound to anything: a ceiling, a spend check, a rate
  limit. **The question is not "is the work kept" but "what reads it next, and would that
  thing still find it in the state this bound leaves it in?"** The judgement lane's `cost`
  and `ceiling` gates are the immediate case. And a corollary for tests: if a test's name
  promises a behaviour its body cannot observe, the name is the bug.

### F31 — An `except` guard that checks a clause EXISTS cannot see it made dead

- **BELIEVED** — asserting that a handler contains `except ControlRefused` prevents the
  route answering 404 for a refusal. The guard walked the AST, so it was not satisfiable by
  a comment or an import.
- **ACTUALLY** — Python dispatches except clauses **in order**, and `ControlRefused`
  subclasses `ValueError`, so a broad clause first makes the refusal clause **dead code with
  the clause still visibly present**. The guard passed over a swapped pair. Only a hardcoded
  behavioural parametrisation of two route names caught it — and a *new* route is in no such
  list, so a plausible `_handle_post_pipeline_release` shipped answering 404 with the whole
  suite green.
- **MEASURED BY** — swap the two clauses in `_handle_post_pipeline_restart`: the AST guard
  PASSED (`2 failed, 9 passed`, and the guard was among the 9). Add the new route: `24
  passed`, and it answered `404 | control field: None`. Both now fail: the guard compares
  handler **indexes** inside each `ast.Try`, and the behavioural parametrisation is
  **discovered** from the same walk instead of listed.
- **AFFECTS** — every lane. Two rules: **a structural guard over an ordered construct must
  assert the order**, and **derive a parametrised test's cases from the code rather than
  listing them**, or the case that matters is the one nobody added.
