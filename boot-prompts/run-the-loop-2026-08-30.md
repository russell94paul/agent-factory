# Boot — bound the loop, then run a ticket through it

**Written:** 2026-08-29, late. **Refreshed:** 2026-08-29 ~20:45, after the tickets-tab count defect
was fixed and the dependency graph became real.
**For:** the next session.

**Supersedes** `intake-platform-design-lock-2026-08-30.md` for sequencing — that brief's divergence
pass is **done**; read its outputs, do not re-run it.
**Read alongside** `execution-plane-2026-08-30.md`, which is the session *after* this one and says so
itself. Do not start there while `cap`/`reaper`/`ceiling` are red.

`next:` **Run one supervised lane, and put the run in the corpus.**
`python scripts/local_tracker.py --serve --port 8099`, launch the `certify` lane, watch it, answer
it if it blocks. Done when gate `breadth` reads **2 cases** instead of *"1 case, 0 strata"*.

**Why this and not RUN-01, which every earlier version of this file led with:** F78 measured which
repository each gate probes. **Four of the five `UNATTENDED` gates — `cap`, `ceiling`, `concurrency`,
`reaper` — grep `prefect-connectors`.** No agent-factory work moves them. **All five
`OUTPUT-UNCERTIFIED` gates are local.** The plan spent its effort on the verdict this repo cannot
move while the one it can move sat untouched.

`breadth` is the cheapest of the five because its remedy is to **run** the loop rather than write
more of it — and `launch.py` already argues a supervised run is *"the only way to measure the loop
at all"*.

⚠ **There is no spend ceiling on that path.** `SUPERVISED-OK` means a human is the ceiling. Watch it.

⛔ **RUN-01a/02a are still real engineering** — `RepoDeployer` has zero callers, so the launcher
genuinely is unbounded — but they are no longer the lead, because they were chosen for a gate they
cannot move. If you do them, expect no verdict to change, and do **not** re-point `CONNECTORS` to
force one. Read `docs/findings.d/F77-*.md` and `F78-*.md` first.

⚠ **`python -m factory.launch` takes ~9 minutes and prints nothing until it finishes.** It is not
hung — see the gotcha below. Budget for it, run it with `python -u`, and do not re-run it casually.

---

## Stop designing. The instrument already chose the direction.

Verdict **measured 2026-08-29 ~21:00**, exit 0, full run — the three headline verdicts are unchanged
from the afternoon reading:

```
May I RUN an agent, with me watching?     SUPERVISED-OK
    3 rows in .data/runs.jsonl · 5 questions waiting · process table readable
May I LEAVE it running, unattended?       UNATTENDED-BLOCKED
    cap         FAIL  a cap exists on a path that did not run
    reaper      FAIL  no lease, timeout or reaper for dispatched work
    ceiling     FAIL  no spend ceiling enforced before dispatch      <-- RUN-01
    concurrency FAIL  bounded per wave, not per stage dispatch
    bounded     FAIL  no attempt cap on restart
May I TRUST what it produced?             OUTPUT-UNCERTIFIED
    suite       FAIL  21 failed, 409 passed, 2 xfailed (0:02:39)     <-- see below, phantom
    certified   NOT_RUN  12 assertions have no instrument wired
    corpus      FAIL  tamper-evident, but separation is not enforced
    version     FAIL  9 dimensions absent from the version
    breadth     FAIL  1 case, 0 strata — below any calibration threshold
```

Teams: `Data Pipeline Orchestrator` **0 of 7**, UNATTENDED-BLOCKED · `Power BI Data Model Designer`
UNGATED.

`launch.py` states what that position costs, in its own words:

> *"You are the cap, the reaper and the spend ceiling."*

⛔ **This table was the whole brief in every earlier version of this file, and it is no longer the
lead** — see the `next:` block. It is kept because RUN-03/04 still matter and the split below is
still the correct reading of RUN-01/02. But ⛔ **"done when a verdict moves" is false for RUN-01 and
RUN-02,**
and that was the load-bearing error in the first version of this file. See `docs/findings.d/F77-*`
and `F78-*`: **four of the five UNATTENDED gates probe `prefect-connectors`, not this repo.**

| | | done when |
|---|---|---|
| **RUN-01a** | spend ceiling on the launcher path | code + test in this repo. **Gate `ceiling` will not move.** |
| **RUN-01b** | ceiling in the connector control plane | gate `ceiling` moves — **BLOCKED**, see below |
| **RUN-02a** | turn cap + reaper on the path that runs | code + test in this repo. **Gates `cap`/`reaper` will not move.** |
| **RUN-02b** | same, in the connector control plane | gates move — **BLOCKED**, same reason |
| **RUN-03** | execute a TeamSpec | one preset runs one real ticket, ledger row appended, still SUPERVISED-OK |
| **RUN-04** | ticket → team entry point, then the UI button | one command takes a ticket id and produces a claimed lane running the matched preset |

**Why the `b` halves are blocked, and must stay blocked:** the accrued-cost figure a ceiling would
read is recorded only on `stage_completed`, so it is **blind to every failure** — a comparison
against it turns the gate green over a ceiling that cannot hold. And
`prefect-connectors/tests/orchestrator/mutate_control_plane.py` is **absent from that checkout**, so
no negative control exists to prove a newly-green gate can still refuse. This repo's standing rule:
a mechanism nobody has watched refuse is not a control.

⭐ **RUN-03 and RUN-04 are unaffected** — their acceptance is a real run and a real command, not a
sibling-repo probe. If the `a` halves feel unsatisfying because no verdict moves, **RUN-03 is the
ticket where progress becomes visible again.**

**RUN-01 and RUN-02 are SYNTHESIS §5 steps 1–2**, which R3 calls non-negotiable. RUN-03 comes after,
because an executor built before its bounds is an unbounded executor — the thing that *"staged a
fresh budget and re-dispatched all night"*. RUN-04's button is last because until RUN-03 exists it
has nothing to call.

⭐ **RUN-01a is a WIRE ticket, not a build ticket.** `deploy.py` already implements the ceiling and
the `AttemptLedger`. `RepoDeployer` has **zero callers** — so the launcher genuinely is unbounded,
and wiring it is real work regardless of what the gate says. Read RUN-02's gate text closely —
*"a cap exists on a path that did not run"* — that sentence is the finding, and note that it is a
sentence about `prefect-connectors/orchestrator/`, which is precisely how F77/F78 went unnoticed:
**the gate's words are equally true of this repo, and it is not measuring this repo.**

---

## ⭐ The finding most likely to be lost: the acceptance instrument is unusable under contention

`python -m factory.launch` is how all four RUN tickets are graded, and it has two properties nobody
wrote down.

**1. It takes ~9 minutes and prints nothing until the end.** Paul ran it and reported *"nothing
happening"*; a later run produced **zero bytes for 8 minutes** before completing normally with exit
0. It is not hung — it buffers, and it is slow because **one of its gates runs the entire pytest
suite** (`suite`, 2:39 of it). Use `python -u`, budget the wall-clock, and do not treat silence as
failure. Earlier text in this file calling the run `NOT-RECORDED` was correct when written; the run
subsequently finished and the measured verdict is above.

**2. ⛔ The instrument embeds the unreliable suite as a gate, so one of its own verdicts is
phantom.** `suite FAIL — 21 failed, 409 passed` is the *same* fluctuating suite whose failure count
moved **8 → 12 → 15 → 18 → 21 in one session with no code change**, because ~20 tests read the
`prefect-connectors` checkout live and other sessions move it. Measured condition during this run:
`../prefect-connectors` on `chore/artefact-homes` with **29 dirty files**, and
`tests/orchestrator/mutate_control_plane.py` absent.

So `OUTPUT-UNCERTIFIED` is currently carrying a failure that is a fact about a **sibling checkout**,
not about this repo's output. That does not change tonight's direction — `ceiling`, `cap` and
`reaper` fail on their own merits and RUN-01/02 are untouched by it — but **do not "fix" the 21
failures**, and do not read `suite` as a regression signal. A gate that cannot distinguish *our code
broke* from *someone moved a sibling branch* is reporting `NOT-VISIBLE` as `FAIL`. Worth its own
ticket.

Record the basis beside any suite number you quote:
```bash
git -C ../prefect-connectors branch --show-current
git -C ../prefect-connectors status --porcelain | wc -l
```

⚠ The earlier *"304 tests green"* claim in this file is **retired** — the suite is 432 tests
(409 + 21 + 2 xfail) and its green count was never stable enough to quote without its condition.

---

## Corrections since this file was first written — do not re-inherit the old version

| | |
|---|---|
| **D-1 is now CLOSED.** | The dependency graph was *authored, not derived*; the store's `blocked_by` was a populated-but-never-read field. It is now live: **18 tasks carry 18 real edges**, and `build_board_artifact.py:118` reads `t["blocked_by"]` from the store rather than `ticket-detail.json`. Earlier text in this file calling D-1 open was correct when written and is now wrong. |
| **The tickets tab was under-counting, and it is fixed** (`local_tracker.py:843`, Paul, tonight). | `RUN-` was missing from the lane classifier, so 4 RUN + 3 legacy tickets fell into `"other"` and were dropped from the total. **The "3 closed" was always right; the denominator was wrong** — 64 where it should have read 68. Unclassified tickets are now *counted and shown* instead of silently excluded, which is the actual fix. |
| **D-2 remains fixed, and its cause is the lesson.** | D5 was reported missing; it exists at `deepseek.md:528-541`. The cause was a **case-sensitive grep** against a heading reading *"What I Could Not Judge"* — a zero from an instrument nobody proved could see. **Five of D5's seven rows are still unticketed.** |
| **D-4 is still OPEN.** | The 70–80% vs 30–40% questionnaire figure is verbatim accurate but **basis-absent** — an unsourced projection from a food-waste ontology feasibility study, in a different domain. Apply `control-room.md` §8's basis register, including its *"how it dies"* column. **The intake-platform critical path was built on that number**; if it does not survive its basis label, that path is not the priority the earlier brief claimed — part of why this brief leads with RUN-01. |

Read, do not redo — produced by a parallel session:
`docs/reviews/divergence-2026-08-29.md` (22 claims: 13 CONFIRMED · 5 our doc stale · 2 reviewer
stale · 2 basis defect) · `docs/reviews/ticket-repo-crossref-2026-08-29.md` (**9 of 33 tickets wrong
about the repo**) · `docs/reviews/external/verification.md`.

---

## What is already true — do not rediscover it

- **The configurator exists and is good.** `python -m factory.presets` — five baseline presets, each
  with model, effort, turn and dollar caps, an escalation trigger and an explicit refusal. It decides
  which team a ticket type gets. **Nothing consumes that decision.** That is RUN-03/04.
- **Parallel sessions are already a solved problem — nobody was told.**
  `local_tracker.start_all_command(lane_ids, make=True, panes=True)` (`scripts/local_tracker.py:461`)
  issues **one Windows Terminal invocation for every eligible lane**, splitting one tab so all
  sessions are visible at once, alternating vertical/horizontal to stay near-square. `panes=False`
  gives a tab each. **Five lanes are launchable today**: `control-plane`, `certify`, `judgement`,
  `artifact`, `grain` — one agent, one prompt, one worktree, claimed atomically. A lane is not a
  team; that is the gap RUN-03 closes.
- **The certifier exists.** A1–A12 pass; `certify` labels its own basis (`REPLAYED`, not measured).
- **Nothing executes a `TeamSpec`** — `git grep "TeamSpec\|load_team"` outside `blueprint.py` returns
  nothing. SYNTHESIS §11.5 found this independently.

## ⭐ The lanes and the tickets are two names for one body of work, and nothing joins them

Raised by Paul 2026-08-29: *"All the lanes appear to be related to a past project… you can't execute
a ticket from here, and it should not default to tabs with lanes we are not working on."* The first
half is **half right, and the correction is the useful part.**

The five lanes are keyed to **readiness gate ids**, not to tickets — so they carry the earlier plan's
vocabulary while pointing at today's work:

| lane | gates | that is |
|---|---|---|
| `control-plane` | `cap` `reaper` `concurrency` `bounded` `truthful` `from-history` | **RUN-02** |
| `judgement` | `ceiling` `refuses` `checks` `attributable` `honest` `general` `cost` | **RUN-01** |
| `certify` | `certified` `breadth` `corpus` | the OUTPUT-UNCERTIFIED verdict |
| `artifact` | `chain` | earlier plan — *"run impeccable at the readout"* |
| `grain` | `grain` | earlier plan — landing-table grain, not on this path |

**Three of five are the RUN tickets under different names.** Two are genuinely off-path.

⭐ **The join already exists in data on both sides and nothing computes it.** Matching the gate ids
named in a ticket's acceptance against each lane's `gates` list resolves, with no new schema:

```
RUN-01 → ceiling             → judgement
RUN-02 → cap, reaper         → control-plane
RUN-03 → (no gate)           → the executor itself
RUN-04 → (no gate)           → the entry point itself
```

So **RUN-04's first version is a join, not a build** — same shape as RUN-01 being a wire ticket. And
this is the estate's signature defect again, in its fourth form: a hand-authored list
(`factory/lanes.py`) tracking a thing that could be derived, drifting from it in vocabulary while
still being correct in substance. `build_board_artifact.py`'s own docstring warns about exactly this
— *"three ticket-record systems already disagree in this estate."* Lanes are the fourth.

**Three separate fixes, do not conflate them:**

1. **UI/UX, cheap, safe now** — the lane surface must not present `grain` and `artifact` as live
   work, and must show which RUN ticket a lane serves. `scripts/local_tracker.py` only.
2. **Derivation, RUN-04** — lane membership computed from ticket ↔ gate, so the two records cannot
   drift. Do not hand-edit the lane list to fix this; that is how it got here.
3. **Not a UI bug at all** — *"you can't execute a ticket from here"* is **RUN-03**. There is no
   button because there is no callee: nothing in the repo executes a `TeamSpec`. No UI change
   creates one.

⚠ `factory/lanes.py` was being refactored by a parallel session at the time of writing
(`ContextPack`, 33 insertions, uncommitted). **Do not edit it until that lands.**

## Working rules

- **Grep before proposing.** 9 of 33 tickets were wrong about the repo; two proposed things already
  built. If the symbol exists, the ticket is `wire` or `retire`, never `build`. Cite the grep.
- **Every gate ships with a negative control** — it must block bad input *and* let good work through.
- **Numbers carry their command**, and their condition. Do not type a count you did not just measure.
- **Derive lists; do not enumerate them.** Three hand-maintained allow-lists under-covered in one day
  (`TeamSpec.version`, `synthesis.session_prompt`, `local_tracker._HOT`) — and the lane classifier
  fixed tonight was a fourth. All four looked correct. Pair any list with a test that fails when an
  entry goes *missing*.
- **The board is generated.** Edit `docs/board/template.html` or `ticket-detail.json`, then
  `export_board.py && build_board_artifact.py`. **Never edit `docs/board/index.html`.**
- **Republish to the same artifact URL** — a new one loses Paul's saved ticket states.
- **Stage by path, never `git add -A`.** Three sessions were live in this checkout today; two edited
  the same two files and both survived by luck. `git status` shows other people's work.
- **Ask before committing.** Paul approves commits.

## Where things live

| | |
|---|---|
| `python scripts/local_tracker.py --serve --port 8099` | lands on **Tickets**; `/gates` is the readiness verdict |
| board artifact | `claude.ai/code/artifact/11564c9c-0aa2-4369-9911-2e2ad82cfbaf` — THE PATH lane first |
| showcase artifact | `claude.ai/code/artifact/f95b50b4-6602-479a-bbe6-197b74b08a95` |
| next session's brief | `boot-prompts/execution-plane-2026-08-30.md` — after RUN-01…03 |
| selection design | `docs/research/answers/R19-answer-work-taxonomy-and-team-selection.md` |
| unrun decision | `docs/BUILD-VS-ADOPT-PROMPT.md` — 277 lines, **never executed** |

## Status — honest

- ✅ RUN-01…04 exist, each with a `launch.py` gate as acceptance.
- ✅ D-1 closed; the board's DAG is now derived from the store.
- ✅ Tickets tab counts correctly and surfaces what it cannot classify.
- ❌ **No RUN ticket has been started.** **3 of 68** tracked tickets closed (`.data/tasks.jsonl`
  holds **71**: 2 done, 48 open, 18 blocked, 3 abandoned; 3 legacy rows sit outside the tracked
  lanes and are shown separately). Every closure predates today.
- ✅ `factory.launch` re-measured 2026-08-29 ~21:00, exit 0 — verdicts unchanged, `ceiling` still
  FAIL, so RUN-01 is still the right next action.
- ❌ Its `suite` gate is **phantom-failing** on a sibling checkout's state (21 failures). Needs a
  ticket: a gate that cannot tell *our code broke* from *someone moved a sibling branch* is
  reporting `NOT-VISIBLE` as `FAIL`.
- ❌ **4 commits unpushed** on `feat/readiness-generator` (`17a6a5a`, `08dedab`, `6f21d67`,
  `68ad22f`). A parallel session also has uncommitted work in the tree — `factory/context.py`,
  `factory/evidence.py`, `docs/specs/golden-workflow-fit.md` and two test files. **Not yours.**
- ❌ `main` is **189** commits behind; nothing merged.
- ❌ Git history still carries client names — the working tree is redacted, the history is not, and
  the repo is public.
- ❌ The corpus holds **one** recorded run — sensitivity is proved, breadth is not.
- ❌ D-4 open; five D5 rows unticketed; `BUILD-VS-ADOPT-PROMPT.md` never run.
