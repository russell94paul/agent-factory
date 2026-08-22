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

## 2026-08-22 · session: boot pre-flight + three-lane launch

### F11 — Gate `finishes` can never pass, however well the agent performs

- **BELIEVED** — "3/14 runs finished" is a score that improves as the loop gets more reliable, so
  landing the reaper and re-running the loop will move it. [[F4]] says the numbers are stale;
  the natural inference is that fresh runs fix them. For this gate that inference is wrong.
- **ACTUALLY** — `readiness.py:175` passes only on `len(fin) == len(runs)` — **every** recorded
  run finished, all-time, with no window. Four runs (`pipe_5546c123`, `pipe_66d2326d`,
  `pipe_7274e774`, `pipe_c34bfbe5`) sit at `stage_started` with no terminal event and, being
  history, will never gain one. Each new run increments both sides, so the ratio can approach
  14/18, 14/50 — never equality. The gate is not a hard target, it is unreachable: a perfect
  agent from now until forever still reads FAIL. A gate that cannot pass is the mirror of the
  decoration-gate this repo already refuses — it stops being a measurement and becomes a wall,
  and the board reports failure at work that is already fixed.
- **MEASURED BY** — read `factory/readiness.py:175`; the pass condition is equality, not a rate.
  Then note the four ids in the gate's own evidence lines. No run appended after today can
  satisfy it, because the shortfall is in runs that already ended.
- **AFFECTS** — control-plane lane (`finishes`, and the `reaper` it is building), and anyone
  reading the 30-gate score as progress. The reaper is the fix, but only if it **backfills a
  terminal event for those four historical runs** rather than only bounding future dispatch —
  emitting terminal events for new work leaves this gate exactly where it is. Decide deliberately
  whether a reaper-emitted terminal counts as "finished"; if it does not, the gate needs a window
  instead.

### F12 — Gate `succeeds` is an all-time ratio, so one bad day poisons it permanently

- **BELIEVED** — "a stage fails 6.1× more than it succeeds" is a current reliability rate, and a
  run of good stages will pull it back over the line.
- **ACTUALLY** — `readiness.py:188` passes on `done > failed` counted over **every audit file
  ever written**, unwindowed and undated. It stands at 165 completed against 1001 failed, so
  flipping it needs **837 net successful stage completions** — with zero new failures, 837
  consecutive good stages. Most of the 1001 come from the single 2026-08-14 incident where an
  uncapped restart loop took the region quota (352 restarts of `trigger-run` in one run), so the
  metric permanently carries a fault that has since been capped. It answers "has this system ever
  been reliable" when the question every reader asks of it is "is it reliable now".
- **MEASURED BY** — read `factory/readiness.py:180-190`: `_counts(_audits())` over
  `orchestrator/data/audits/*.json`, no date filter, pass condition `done > failed`. Arithmetic:
  1001 − 165 = 836, so 837 net successes to cross. Compare against the incident evidence already
  in the `bounded` gate.
- **AFFECTS** — control-plane and judgement lanes, and any before/after claim made with
  `python -m factory.readiness`. Either window the ratio (last N runs, or since a stated date) or
  quarantine the incident's audits behind a declared exclusion — and whichever is chosen, the gate
  must **state its basis in its own evidence line**, so the number is never read as current when
  it is cumulative. Do not simply delete the audits: that destroys the evidence the `bounded` gate
  cites.
