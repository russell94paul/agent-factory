# Spec — the control room: from managing sessions to running teams

**Written 2026-08-23.** Accompanies `R12-session-manager-ui.md` and its answer
(`answers/R12-answer-session-manager-ui.md`, filed 05:11 today). Extends
`terminal-configuration.md` (the pane layout) and `architecture-v0.md` (the four planes). Like
architecture-v0, this is **a strawman to be attacked**, not a conclusion — a concrete proposal gets
an argument back, and an argument is worth more than a survey.

Every claim carries its basis:

`MEASURED` we ran it and have the number · `DERIVED` computed from something measured ·
`REPORTED` a boot prompt, answer or prior session said so and it was not re-measured today ·
`REASONED` an argument from constraints · `BET` a judgement call that could be wrong

---

## 0. The question, answered

> *"Is it a bad idea to set up a UI for managing sessions now? I feel if we do it, we'd be faster."*

**No — but the UI is not the part that makes you faster, and that matters for what gets built
first.**

Three things cost measurable time today. **Two of them are not UI problems at all**, and both can
be fixed before anything is rendered:

| # | The cost | Is it a UI problem? |
|---|---|---|
| 1 | **4 agents sat blocked on questions written in plain English that no surface shows** `MEASURED` | No. It is an unread file. |
| 2 | **5 of 12 live sessions share one name**; the only thing telling them apart is a `cwd` you look up by hand `MEASURED` | No. One env var and a test. |
| 3 | A page load re-runs 30 probes serially on a single-threaded server — **~19 s**, and two concurrent requests return empty `MEASURED` | Yes, and it is the reason the instrument we already have goes unused. |

⭐ **An agent blocked on an unread question is the cheapest failure in the estate to fix and the
most expensive to leave.** It burns no tokens, produces nothing, and holds a lane seat — of which
there are three. On 2026-08-23 four were in that state, one of them waiting on a yes/no that takes
a human four seconds to answer. Nothing about fixing that requires a UI; it requires reading
`~/.claude/jobs/<id>/state.json`.

**So: build it, in slices, smallest first — and put a stop line in.** Slices 0–2 (§5) are days and
remove measured wait. Slice 3 (the terminal grid / attach layer) is the expensive one and is
**held behind §6**: the data-pipeline team migrating a connector for real.

**What would make it a bad idea** is the failure mode this repo exists to prevent: the control room
becomes the project. A session manager proves nothing about whether an agent team can land rows in
a warehouse. The repo's own README states the ordering — *do not add a team, an optimizer or a UI
until the instrument can register a failure* — and readiness is **10 of 30 gates** `REPORTED`
(boot prompt, 2026-08-23 04:00; not re-measured in this session). A control room built on top of an
instrument that passes a third of its own gates is a nicer window onto an unproven machine.

---

## 1. What we measured, and with what

Every row was taken on a live machine on 2026-08-23. Instruments named, per house rule.

### 1.1 Identity

| Figure | Value | Instrument |
|---|---|---|
| Live `claude.exe` sessions on this workstation | **12** | `Win32_Process` + `~/.claude/sessions/*.json` |
| Sessions sharing the single name `boot pre-flight verification` | **5** | the session registry |
| Distinct lane worktrees those 5 were in | **4** | their `cwd` |
| Live sessions in the *same* worktree and branch (`control-plane`) | **3** | registry, joined on `cwd` |
| Sessions whose name identifies the work | **2 of 12** | registry |

The name is inherited from the boot prompt that spawned the terminal, **not from the work**. Five
terminals launched from one prompt are five identical rows. A question from one of them can only be
answered by messaging all five and letting four ignore it.

`scripts/local_tracker.py::_launch_script` already sets `CLAUDE_CODE_SESSION_NAME` per lane. **No
live session demonstrates it and no test asserts it reaches the process.** Per this estate's own
rule — *a declared setting that nothing reads is worse than no setting, because it reports as
configured* — naming is `INFERRED`, not fixed.

### 1.2 The blocked-question channel

```
~/.claude/jobs/<id>/state.json    state · tempo · tokens · inFlight · detail · needs · output
```

**9 jobs on disk, 4 in state `blocked`, each with the question written out in English** —
*"okay to read ZEUS_ALDC_API_KEY?"*, *"renumber Governor's findings into a wider block before
merge?"* — and **no surface anywhere shows the `needs` field.** `MEASURED`

`factory/sessions.py` reads the *other* registry (`~/.claude/sessions/<pid>.json`) for liveness.
This one is untouched by every line of code we have.

This is not alarm fatigue. It is **alarm absence**: the signal exists, is well-formed, and is
never surfaced. The agents are not stuck because they cannot ask. They are stuck because the asking
goes nowhere.

### 1.3 Cost — measurable all along, measured for the first time today

Our own spec said *"nothing currently records what a lane spent."* That was true of **our code**,
not of the substrate: every assistant message in `~/.claude/projects/<slug>/<session>.jsonl` carries
a `usage` block, so cost is recoverable **retroactively, for lanes that ran before anyone
instrumented anything.** Built as `factory/runs.py`. `MEASURED`

| Lane | Output tokens | Cache read | Wall | Model | Commits |
|---|---|---|---|---|---|
| control-plane | **1,188,083** | 302,442,227 | 22.6 h | opus-5 | 25 |
| artifact | 226,859 | 54,945,137 | 19.4 h | sonnet-5 | 5 |
| certify | 235,623 | 54,917,368 | 1.7 h | sonnet-5 | 4 |
| judgement | — | — | — | — | **never launched** |
| grain | — | — | — | — | **never launched** |

One opus lane spent ~5× either sonnet lane's output for ~5× the commits. **One observation, not a
law** — but it is the first time the question could be asked at all, and "is this lane worth its
model" is exactly what a supervisor should let an operator ask.

The join is the slug: each of `: \ / .` in a path becomes one dash. Get it wrong and every lane
silently reports `NOT-RECORDED`, because the directory is simply never found.

### 1.4 The concurrency ceiling is a *file* ceiling

```
lanes       control-plane · certify · judgement · artifact · grain
conflicts   control-plane <-> judgement   (both write orchestrator/pipelines.py)
            certify       <-> grain       (both write factory/connector_contract.py)
max set     3
```

`DERIVED` from `factory/lanes.py::conflicts()`, not assumed. Two agents editing one file is the
**41.7% cross-agent conflict rate** R5 measured across ~33,000 agent-generated PRs. `REPORTED`

⭐ **A UI that assumes ten concurrent agents is answering a question we do not have.** The cap
lifts by splitting files or by moving data work to T2 clone isolation (§2.1), not by adding panes.

---

## 2. Current architecture

### 2.1 The four planes

From `architecture-v0.md`, unchanged:

```
APPROVE   humans only. merge · per-secret grant · promote to prod
          never automated — finish() already refuses to merge
   ▲ evidence bundle                                    │ decisions
PROVE     readiness gates · GreenContract · findings.d · run audits
          the evaluator is a SEPARATE PRINCIPAL the agent cannot be
   ▲ artefacts + measurements                           │ certify request
RUN       the isolation ladder — T0 worktree · T1 container · T2 container + clone
   ▲ claims · bus · finish                              │ dispatch
DECIDE    conflict graph · claims · scheduling · caps · budgets
```

The isolation ladder, with today's honest state:

| Tier | Environment | May touch | State |
|---|---|---|---|
| **T0** | git worktree, operator machine | repo files only | **built** `MEASURED` |
| **T1** | container, egress allowlist, read-only warehouse role | repo + `SELECT` | not built |
| **T2** | container + ephemeral zero-copy clone schema, dropped on exit | full DDL/DML **inside the clone** | not built |

The boundary that matters is RUN↔PROVE: the thing being measured must not be the thing measuring.
R3 ranks a separate local process as *"mostly theatre"*, so **that boundary is currently
aspirational** — the evaluator needs its own identity and credentials before the diagram is honest.
`REPORTED`

**Where the control room sits: it is a DECIDE-plane surface with a read-only window onto RUN.** It
schedules, claims, launches, budgets, and routes questions to a human. It must never author a PASS
bit, and it must never approve a secret.

### 2.2 What exists in code

| Module | Does | State |
|---|---|---|
| `lanes.py` | lane roster, `touches`, conflict graph, dependency order, model recommendation | built, drilled |
| `claims.py` · `worktrees.py` | claim/release lock; one worktree + branch per lane | built |
| `sessions.py` | liveness from `~/.claude/sessions/<pid>.json`; refuses a second session in a claimed lane | built after `finish()` released a claim while its session was still alive |
| `finish.py` | assert · push · announce · **release claim** · record run. Refuses to merge | built |
| `runs.py` | the run ledger — cost/wall/model/commits, reconstructable from transcripts | built **today**; has never written a real `RECORDED` row |
| `bus.py` | inter-lane events | built, and **F71: rooted per-worktree, so lanes cannot see each other. 1 event in the estate** |
| `readiness.py` | 30 gates, re-measured per request | 10 pass `REPORTED` |
| `contract.py` · `connector_contract.py` · `certify.py` | the GreenContract — what "done" and "I could not tell" mean | built; calibrated on **1 case, 0 strata** |
| `blueprint.py` | `AgentSpec`, `TeamSpec`, version hash over composition | see §2.4 |
| `board.py` · `dispatch.py` · `synthesis.py` | research pipeline, findings routing | built |
| `scripts/local_tracker.py` | the instrument panel — four tabs, launch buttons, generated per-lane `.ps1` | built; **single-threaded, ~19 s/page** |

### 2.3 What the substrate publishes that we do not read

```
~/.claude/sessions/<pid>.json   pid · kind(interactive|bg) · status(idle|busy|waiting)
                                name · cwd · agent · jobId · messagingSocketPath
~/.claude/jobs/<id>/state.json  state · tempo · tokens · inFlight · detail · needs · output
~/.claude/projects/<slug>/*.jsonl   per-message usage blocks — tokens, cache, model, timing
```

`sessions.py` reads the first for liveness only — `status` is ignored. **The second is untouched.**
The third was untouched until `runs.py` today. Most of the control room already exists as data on
disk; what is missing is anything that reads it.

### 2.4 Declared but not executed — the gap the vision turns on

`blueprint.py` defines `AgentSpec` and `TeamSpec` with a version hash covering the composition.

- **`AgentSpec` is executed** — `deploy.py::run_agent(spec, task, wt, …)` consumes it. `MEASURED`
- **`TeamSpec` is not.** Its only callers are `load_team()` and `tests/test_blueprint.py`. **Nothing
  in the estate runs a team.** `MEASURED`

  *(R7's prompt said one caller for both; that was true when written and is now half true — the
  correction is recorded rather than smoothed.)*

Meanwhile the `hash` gate wants **15 identity dimensions and covers 0** `REPORTED`. So an agent
today is a prompt + a model + a gate list — a launcher input, not an artefact. **A repo called a
factory has no manufacturing step in it.**

### 2.5 The loop that actually runs today

```
tracker  →  pick lane  →  claim  →  worktree + branch  →  generated .ps1  →  Windows Terminal tab
                                                                                     │
   human reads a pane, answers a question, relays between lanes  ←──────────────  agent works
                                                                                     │
                                        finish()  →  assert · push · announce · release · record
```

It works. It produced 20 commits across three lanes on 2026-08-22 with **zero cross-lane
conflicts** `MEASURED`. **Nothing about it is repeatable without the person who invented it**, and
every closing act — releasing a claim, pushing a branch, reading the board, relaying a correction —
happens in a shell the operator has to find or open first.

---

## 3. Where the time actually goes

The wait ledger, which is the only justification a control room needs:

| Wait | Size | Fixed by |
|---|---|---|
| Agent blocked on an unread written question | **hours per occurrence, ×4 today** | slice 1 — read `needs` |
| Operator identifying which pane is which | seconds, dozens of times a day | slice 0 — assert the name |
| Operator opening the instrument | ~19 s per look, so it goes unopened | slice 2 — thread the server |
| A lane finishing and leaving nothing behind | an hour later, indistinguishable from a lane that never ran | `runs.py`, built today |
| A dead terminal read as a dead agent | one real debugging session lost | slice 2 — the four states |

⭐ **Note what is not on this list: watching agents work.** A grid of live terminals is the most
attractive feature and the only one with no measured wait behind it. That is the whole reason it is
slice 3 and not slice 1.

---

## 4. The vision — teams assembled, run and certified through one surface

The escalation, in the order the evidence allows:

```
session manager   which processes exist, what are they called, which is blocked      ← slices 0–2
lane manager      which work is claimed, what conflicts, what a lane cost            ← mostly built
team manager      assemble a team for a ticket, version it, run it, certify it       ← the vision
factory           the team that migrates a pipeline, unattended, with evidence       ← §6
```

**The claim worth betting on:** *"teams can be easily assembled and then optimised for whatever the
task/ticket is."* `BET`

Concretely, and this is what the UI is *for* — not a dashboard:

1. **Pick a ticket.** Assemble a team: roles, models, effort, tool scopes, **isolation tier**, and
   the GreenContract that will certify the output.
2. **Version it.** `TeamSpec.hash` already covers the composition. Pin the hash to the verdict, so
   **a certification cannot outlive the configuration that earned it.**
3. **Run it** — claims, worktrees or clone schemas, budgets, caps.
4. **Certify it** — the contract returns one of five verdicts, never collapsed.
5. **Compare.** Two team compositions on comparable tickets, with cost and outcome side by side.
   That is the first honest version of "optimise a team", and it needs §1.3 to exist — which, as of
   today, it does.

**The counter-argument, kept in view.** R2 measured multi-agent architectures at **−3.5% average**
across 180 configurations, with sequential tasks degrading **39–70%** `REPORTED`, and said: start
with **one** end-to-end worker plus a non-LLM verifier. Nothing here contradicts that. **A UI for
composing and supervising teams is not an LLM manager** — no agent-to-agent channel, no LLM
architect, no LLM tester. The human is the manager; the UI is the manager's instrument. If a slice
of this design starts to look like agents coordinating agents, it has crossed R2's line and should
be cut.

**Why it plausibly is the future:** R11 surveyed nine frameworks and found *teams/crews*,
*workflows*, *guardrails*, *observability* and *human-in-the-loop approval* first-class nearly
everywhere. `REPORTED` What almost nobody has is the one thing this estate does have: **a contract
that can return "I could not tell", and a refusal to collapse it into a pass.** Team composition is
commodity; certified team composition is not. **That is the differentiator worth building toward,
and it is the reason to keep the control room subordinate to the contract rather than the other way
round.**

---

## 5. The build, in slices

Each slice names the gate that says it worked. **A slice with no gate is not a slice.**

### Slice 0 — make a session say what it is *(hours)*

- Assert `CLAUDE_CODE_SESSION_NAME` reaches the spawned process; today nothing proves it does.
- Name derived from **the work, not the boot prompt**: `lane:branch:attempt` — e.g.
  `control-plane:lane/control-plane:3`.
- **Gate:** a test that spawns through the real launcher and reads the name back out of the
  registry. Until it passes, naming stays `INFERRED`.

### Slice 1 — the blocked-question inbox *(a day, no UI required)*

- Read `~/.claude/jobs/<id>/state.json`; surface every `blocked` job's `needs` in one merged queue,
  oldest first, each showing session + lane + the question text.
- **Intrusive, not passive** — taskbar flash / OS notification. R12: an action-required
  notification that only badges will be missed. `REPORTED`
- Never auto-drop, never batch-approve. **Per-secret human approval is a hard rule**; one of the
  four questions on disk right now is a credential request.
- **Gate:** a fire drill. Block a real agent on a real question, and time how long until a human
  sees it. Before: unbounded (4 sat all day). Target: under a minute. **This is the only slice with
  a measured before-number, which makes it the one to build first.**

### Slice 2 — honest state, and cost per lane *(days)*

- **Four states, never two:** `RUNNING-ATTACHED` · `RUNNING-ORPHANED` · `EXITED-RESUMABLE` ·
  `EXITED-GONE`. Derived from registry `status` + `kind` **joined against the process table** — a
  file outlives its process, and inferring liveness from file existence reports every historical
  session as live. A manager that cannot tell *alive* from *visible* from *attachable* will lie.
- Cost per lane from `runs.py`, **paired with an outcome** — tokens per commit, not tokens. Our own
  `metrics.py` refuses an activity metric with no paired outcome metric; cost with nothing to anchor
  it is exactly such a metric.
- Thread the tracker (`ThreadingHTTPServer` + a pool over the probes) and split cheap state from
  expensive state. **Never a silent cache** — *no stale number without its age in the same string as
  the number.*
- **Gate:** kill a terminal out from under a live agent. The surface must show `RUNNING-ORPHANED`,
  not `EXITED`. This is a real scenario, not a hypothetical — it happened on 2026-08-23.

### Slice 3 — attach, and the terminal grid *(HELD behind §6)*

R12's answer recommends **adopt `doctly/switchboard` and extend it**. `REPORTED` Its own
source-read says why that cannot be done naively:

> Switchboard never *attaches* to an arbitrary running process; it only re-uses PTYs **it itself
> spawned**. If no tracked PTY exists it **spawns a new CLI process with the same session id**.
> `OBSERVED` (R12 answer §2)

⛔ **That is the divergent-duplicate failure we already hit once**, when a resumed session appended
to a live transcript from two processes. Our lanes are launched by the tracker's generated `.ps1`,
so **every existing lane is exactly the case switchboard mishandles.** It also reads neither
registry — no `needs`, no `status`, no `kind: bg` — and derives attention from parsing ANSI/OSC
output. `OBSERVED`

Adoption is therefore conditional on one of:

| Path | Cost | What we lose |
|---|---|---|
| **Switchboard becomes the launcher** (it spawns every lane; we hand it worktree + prompt) | moderate | our `.ps1` generation, the `CLAUDE_CODE_CHILD_SESSION` clearing, lane/claim semantics unless patched in |
| **Patch it to read both registries** and to refuse resume when a live process exists | moderate, on a fork with no plugin API | ongoing merge burden against upstream |
| **Take the ideas, keep our launcher**, add a read-only pane list | low | the live-terminal grid |

**Recommendation:** `BET` — install it, point it at `~/.claude/projects`, and use it **read-only for
discovery and cross-session search** while our launcher keeps spawning. Do not let it start a
session against a lane until the duplicate-spawn behaviour is fixed on a fork with a test. Revisit
the full adopt after §6.

**Also still open and deliberately unresolved:** the standing refusal of an in-page terminal —
declined three times — because it turns a local web page into a keyboard-attached instruction
channel into agents holding shell access. Switchboard is a desktop app with `nodeIntegration:false`
and `contextIsolation:true` `OBSERVED`, which is a materially better posture than our web page would
have. **That is the strongest argument for adopting rather than building, and it should be weighed
explicitly rather than inherited.**

---

## 6. The acceptance test: the data-pipeline team migrates a connector

**This is the north star, and the stop line for §5 slice 3.** Everything above is scaffolding for
one claim:

> A team of agents migrated a data pipeline, and we can prove it — or we can prove we could not
> tell.

Team one's scope is **source → container → Prefect → warehouse.** Power BI is out until a team has
proved it can land rows. `REPORTED` (README)

**"Migrated successfully" means all of, and nothing less:**

| # | Condition | Instrument |
|---|---|---|
| 1 | Rows land in the target table, keyed and dated as declared | the landing table, queried |
| 2 | The GreenContract returns `PASS` — not `UNMEASURABLE` — against the run | `python -m factory.certify <blueprint>` |
| 3 | **Tenant scope holds.** One ALDC Windsor key returns *every* client's accounts; an unfiltered pull lands another client's rows in a CLIENT-A table and nothing downstream can tell | A12 against declared `allowed_tenants` |
| 4 | Validated **at the consumer's layer**, not only where the change was made | per the estate's evidence gate |
| 5 | No regression: out-of-scope rows unchanged, row counts stable, deltas equal to expectation | before/after |
| 6 | A rollback was captured **before** any prod mutation | saved DDL + revert |
| 7 | The run is in the ledger with cost, wall clock, model and commits | `.data/runs.jsonl`, a real `RECORDED` row |
| 8 | The team's `TeamSpec` hash is pinned to the verdict | `blueprint.py` |

`blueprints/windsorai_client_a.yaml` is the calibration target — chosen because windsorai landed its
first row ever on 2026-08-20 after ten attempts and zero completions, so the contract is calibrated
against **known-good**. A contract first exercised on a broken connector cannot tell *"the connector
is broken"* from *"the contract is wrong."*

**Two honesty notes carried forward, not smoothed:**

- The README records the calibration as **11 PASS / 1 UNMEASURABLE**, A12 blocking on an undeclared
  tenant scope. The blueprint has **since** declared `allowed_tenants`. `MEASURED` **Re-measure
  before quoting either number.**
- Those six account ids were verified **2026-05-29, ~12 weeks before the blueprint**, and the source
  file itself says *confirm against a live pull before activation*. A `PASS` on A12 means *"the
  landing matched what we declared"*, **not** *"what we declared is still correct."*

**And the sequencing that follows from it:** condition 7 cannot be met today, because
`.data/runs.jsonl` does not exist and **no real lane has closed since the ledger was built** — every
row the tracker shows is `RECONSTRUCTED` from git and transcripts. The `RECORDED` path is proven
only by tests. **The next lane to finish is therefore worth more than the next feature**, and slice
1 is what stops lanes from sitting blocked instead of finishing.

---

## 7. What we refuse to build

- **Batch approval of secrets.** Per-secret human approval is a hard rule. Batch-approving *file
  reads* is a different question and stays open.
- **A cache that can quietly show yesterday's state.** No stale number without its age in the same
  string.
- **Anything needing a platform team, a server, or a SaaS.** Small team, one workstation,
  Windows-first.
- **A design for ten or a hundred concurrent agents.** The ceiling is three, and it is a file
  ceiling (§1.4). Optimise for dozens at most, and only after T2 lifts the cap for data work.
- **Removal of the existing instrument panel.** It is added to, never replaced.
- **An LLM manager, an agent-to-agent channel, or an LLM-authored PASS bit.** R2's line, and §4's.
- **A live-terminal grid before §6 passes.** It is the most attractive feature with the least
  evidence behind it.

---

## 8. Basis register — attack these first

| Claim | Basis | How it dies |
|---|---|---|
| The inbox is the highest-value slice | `MEASURED` 4 blocked jobs, unbounded wait | if the fire drill shows questions were already reaching a human another way |
| Naming is broken | `MEASURED` 5 of 12 | — |
| Switchboard would duplicate-spawn our lanes | `OBSERVED` in R12's source read; **we have not run it here** | install it, point it at a lane, watch what it does. Do this before adopting anything |
| A UI makes the operator faster | `BET` | slices 0–2 ship and the wait ledger in §3 does not shrink |
| Team composition through a UI is the future | `BET` | R8's answer lands and says the unit of composition is something else entirely |
| Cost per commit is a useful supervision signal | `REASONED` from one day's data, n=3 lanes | a second week of data shows no relationship between spend and outcome |
| The 3-lane ceiling lifts with T2 | `DERIVED` | two clone-schema agents find a shared resource we did not model |

**Open, and blocking nothing yet:** `R8-data-engineering-agent-factory.md` is in flight and asks the
team-architecture question directly, in the data-engineering context where *"the tests pass"* is not
evidence. **Do not finalise §4 before it lands** — four research passes already told us to fix the
control plane first, we did not listen for a while, and the cost of guessing here is a rebuild.
