# Boot: P0 autonomy pump + mission presets — 2026-09-02

**Branch:** `switchboard/p0-autonomy` off `0d3ba52` (`main`). **UNCOMMITTED — 6 new files, 2 modified.**
**Tests:** `python -m pytest -q` → **exit 0, 1020 collected** (was 954 at session start; +66 new).
**Meeting:** was 2026-09-02 12:00 PDT. **POSTPONED to 2026-09-03.** Nothing was delivered or shown.
**Client artifact:** `docs/artifacts/client-review-navira.html`, 48,213 bytes,
sha256 `b6d09ee9a00c8783…`, verdict **SAFE TO OPEN** (gate READY_WITH_WARNINGS + RENDERED_CONFIRMED).

---

> `next:` **Prove Gates 4 and 5 on the live UI, in that order, before touching anything else.**
>
> The pump is built and unit-tested but **has never started a real agent**. Restart the supervised
> server so it loads the new routes (`hot_reload` structurally cannot reload `local_tracker.py` —
> it defines the running `Handler`), un-pause the run, press RUN DAG, and confirm one real terminal
> opens with `start_mode=AUTO_START` recorded. Then block/approve the evidence gate and confirm the
> next node starts with **no second command**.
>
> ```
> python scripts/switchboard_dev.py --port 8110          # restart to load the new routes
> python -m factory.autonomy status                       # confirm 1 START, 2 HUMAN_GATE
> # then in the browser at http://127.0.0.1:8110/switchboard : RESUME, then RUN DAG
> ```
>
> ⛔ **Do not start with Gate 6 (the full agent review).** That was the mistake available yesterday:
> it is a 45-minute-class task and starting it first buys a half-finished run instead of a proven
> mechanism. Gates 4 and 5 are provable in minutes and are the actual deliverable — a node does not
> have to *complete* its work to prove that the pump started it and that approval continued it.
> Those are separable, and conflating them is what nearly burned the last hour before the deadline.

---

## ⚠ State the run was left in, deliberately

The run **`marketing-meeting-v1-20260902-111431`** exists and is **PAUSED**.

It was paused on purpose at session close, because **the pump fires once per Switchboard render**
while a run is active and unpaused. Leaving it active meant the next person to load the page —
after a server restart — would silently spawn a real Claude session in a real terminal. Un-pause it
deliberately, when you are watching.

```
python -c "import sys;sys.path.insert(0,'.');from factory import autonomy as A;print([(m.run_id,'PAUSED' if m.paused else 'ACTIVE') for m in A.mandates()])"
```

The two servers still listening (**:8110** supervised, **:8099**) are running **pre-pump code** and
therefore cannot pump at all. That is the only reason it is safe right now.

---

## ⭐ The findings most likely to be lost

These are the reason the work took a session and the reason it works. None is in the research pack;
all three were measured on this checkout.

**F-2 — a stage with no `repo` AND no `resource_claim` can never leave DRAFT, ever.**
`work.readiness` returns `repo UNMEASURED` / `contract UNMEASURED`, and `work._state_for` makes an
UNMEASURED check DRAFT deliberately and permanently. **54 of the 91 live rows are in exactly that
state**, and the store had **zero READY rows** at session start. So a mission preset that omits
either field compiles work the pump can never start — and the page looks completely healthy.
`factory/missions.py` refuses such a preset before writing anything.

**F-5 — `work.guarded_start` refuses on a *declared* resource conflict, live or not**
(`factory/work.py:530`). Two stages sharing a claim where either declares WRITE are therefore
**both permanently ineligible for an autonomous start**, while sitting in READY looking fine. Every
WRITE claim must be unique across a preset; READ-only stages may share. This is subtler than F-2
because readiness passes and only the *start* is refused.

**F-4 — the test that forbade an autonomous executor went on passing after the executor shipped.**
`test_p1_ships_no_autonomous_executor` scanned for the literal strings `threading.Timer`,
`sched.scheduler` and `while True:\n        start_synced`. The pump uses none of them, so the day it
landed the guard asserting its absence stayed green. Its own docstring warned that "an absence is
exactly the kind of property that quietly stops being true" — and then it did, undetected. It is now
`test_the_autonomous_executor_is_bounded`, asserting real behaviour against a real store plus an AST
check a comment cannot satisfy. **Lesson: a string scan is not a structural guard.**

**F-3 (corrected) — the "Sales Model bounded change" is not agent-factory work at all.**
It is `GEP Test Models` → Data Model **`66151728-f00f-4a08-af91-6687de5f13dc`**, worked in
**aldc-launchpad** on `feature/gp318-navira-sales-model-repair` (commit `10d4959`, **UNPUSHED**),
which already has its own boot prompt (`aldc-launchpad/boot-prompts/navira-sales-model-repair-2026-09-02.md`),
DECISIONS D0–D8 and a deployment runbook. The pack's `04_MISSIONS/sales_model.yaml` is
`mode: modify_existing` against a target that does not exist in this repo. **Do not build a Sales
mission preset here.**

---

## ⛔ NOT done

- **No real agent has ever been started by the pump.** Zero `MARKETING-MEETING-*` rows carry a
  `start_mode`. The corpus's headline measurement gap — "no agent has ever completed a real
  non-dry-run controller run" — **is still open**. Nothing was faked to close it.
- **Gate 4 (RUN DAG) unproven end-to-end.** The route, `run_control` and `pump` are wired and unit
  tested; no HTTP POST has ever reached them, because the live servers run pre-pump code.
- **Gate 5 (approval resumes) unproven end-to-end.** Proven in a unit test
  (`test_releasing_the_hold_makes_downstream_startable`); never exercised through `/switchboard/resolve`.
- **Gate 6 / 7 not attempted.**
- **The new UI has never been rendered in a browser.** `_runs()` and `mission_form()` pass their
  Python tests and `render_check_switchboard_p1.py` was **not** run against them. Per the global
  consumer-layer rule this does not count as validated: a query-layer pass says nothing about
  whether every visual paints.
- **Nothing committed.** 6 new files + 2 modified sit in a checkout **five sessions share**.
- **Nothing pushed.** No release-gate sweep was run over the new files.
- **`.claude/commands/af-*.md` (6 files) are on disk but untracked** — they work locally now; they
  are not shared until committed.

## Blocked on a human

| item | what unblocks it |
|---|---|
| Commit + push the branch | Paul's go. He was asked at session close and the session ended first. |
| Un-pausing the run | Somebody watching the terminals when it starts spawning. |
| Gate 6's real agent run | ~45 min of wall clock and a decision that it is worth the spend. |
| The 2 presenter warnings on the artifact | Paul reading them: `mission_record_integrity` (8 declared vs 10 observed children — the client figure counts the declared set only) and `risks_still_current` (RISK-2 renders as resolved; confirm the wording reads closed, not open). Neither blocks SAFE TO OPEN. |

## Gotchas earned

- **`hot_reload` cannot reload `local_tracker.py`** — it defines the executing `Handler`, route table
  and `render()`. New routes need `switchboard_dev.py`'s full process restart. Re-measure, don't
  assume the page has your code.
- **`/healthz` 404s on both live servers.** They predate the route. Not a fault; not a liveness test
  either — use `/switchboard` (200, ~54 KB) or `Get-NetTCPConnection`.
- **`curl` from the Bash tool cannot reach these localhost ports** (sandbox proxy: empty body, or a
  404 that is not the server's). PowerShell `Invoke-WebRequest` works. A `curl` 404 here is
  NOT-VISIBLE, not a measurement.
- **`TaskStore.close()` takes `require=`, not `evidence_ok=`**, and refuses a DONE with no
  MEASURED/DERIVED evidence. Test helpers must attach evidence first.
- **`claims.active()` was empty while 4 claim files sat on disk** — stale pids. The files are not the
  instrument; the function is.
- **`work.project()` defaults to `manifests=None`**, so the legacy mission's sidecar contracts are
  invisible unless you pass `sb.manifests()`. New presets put the contract **on the task**, so they
  need no overlay — that difference matters when comparing old and new rows.
- **`git switch -c` in this checkout moves the branch for every session sharing it.** It was a
  zero-file-change switch off HEAD, but HEAD had already moved `7b19baf` → `0d3ba52` under this
  session mid-work. Re-measure HEAD before every add/commit.

## Where things live

| thing | path |
|---|---|
| planner (pure, no side effects) | `factory/autonomy.py` |
| preset compiler + 3 refusals | `factory/missions.py` |
| the Marketing preset (6 stages, 5 edges, 2 holds) | `missions/presets/marketing-meeting-v1.yaml` |
| the pump + `/switchboard/run` + `/switchboard/mission` | `scripts/local_tracker.py` (+486 lines) |
| Runs panel + mission form | `factory/switchboard_p1.py` (+~180 lines) |
| tests | `tests/test_autonomy_pump.py` (34), `tests/test_missions_preset.py` (31) |
| amended guard | `tests/test_switchboard_p1.py::test_the_autonomous_executor_is_bounded` |
| slash commands | `.claude/commands/af-{status,run-dag,run-critical,pause,resume,phase}.md` |
| run mandate | `.data/runs/marketing-meeting-v1-20260902-111431.json` |
| store backup before the run was created | `.data/tasks.jsonl.pre-p0-autonomy-20260902T111422.bak` |
| fallback artifact + its checksums + the passing run log | `docs/evidence/deadline-2026-09-02/fallback/` |
| known-good artifact command | `python scripts/meeting_ready.py --root .worktrees/mission` |
| the research pack this came from | `implementation-packs/combined-execution-research-v2-2026-09-02/` |

## Deliberate deviations from the research pack

Keep these; each has a reason that outlived the deadline.

1. **AUTO does not bypass `guarded_start`.** The pack specified
   `AUTO: require_guarded_start_allowed: false`, which would have made AUTO the one mode able to
   cross the publication boundary and skip an unmeasured condition — moving the safety model into
   the run mode, where it is set by whoever clicked last. Instead: per-work `autonomy` decides
   **which** work is eligible; the run's `mode` decides **whether the pump acts and keeps acting**.
   MANUAL never auto-starts under any run mode. Asserted by
   `test_AUTO_run_mode_does_not_bypass_guarded_start`.
2. **Completion wakeup is pump-on-render, not a timer or thread.** There is no in-process completion
   event, so continuation happens on the next page load. The faster design is a background poller,
   and a background poller *is* the "uncontrolled recursive autonomous execution" the brief forbids.
   The UI states the real latency rather than implying none.
3. **No auto-retry.** A failed start is recorded on the mandate and refused thereafter; a human
   clears it with `python -m factory.autonomy clear-failure --run <run> --work <id>`. Without this
   the pump retries forever, because a failed start leaves the work READY.
4. **Execution-surface routing metadata deferred.** Exactly one execution surface exists (wt +
   PowerShell + `claude`, Windows-local). Metadata describing one surface is unfalsifiable
   decoration. **Post-deadline seam, named precisely:** put the pack's `execution:` block on
   `contract["execution"]` via `work.create`, and consume it as a new check in `work.readiness()` —
   no new scheduler.
5. **No `PROJECT_STATE.yaml` / `PROGRESS.yaml`.** The mandate holds only the operator's own choices;
   every derived fact is re-read from `work.project()`.

## Session boundary

This is a session boundary. The next session picks up **Gate 4 then Gate 5 on the live UI**, grounded
by this file. The Sales Model thread is a **different repo** and is grounded by
`aldc-launchpad/boot-prompts/navira-sales-model-repair-2026-09-02.md` — do not merge the two threads.
