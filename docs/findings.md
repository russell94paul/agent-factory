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
