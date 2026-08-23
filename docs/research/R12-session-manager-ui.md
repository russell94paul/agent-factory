# R12 — Managing many concurrent agent sessions: what the substrate must know, and whether to adopt one that exists

**Status: DISPATCHED 2026-08-23.** Written 2026-08-23. Paste the whole file. The answer is filed at
`docs/research/answers/R12-answer-session-manager-ui.md`.

⚠ **Standing rule in this estate: an object named by a handoff is a hypothesis, not a finding.**
Every figure in §1 was measured on 2026-08-23 and cites its instrument. Apply the same suspicion to
`doctly/switchboard` — **read its source, not its README** — and tier every claim (§7).

---

## 0. What this asks, and the three prompts it must not re-ask

The operator is running enough concurrent agent sessions that he can no longer tell which terminal
is doing what. That is the question: **what must a session-management layer know, and should we
build it, adopt `github.com/doctly/switchboard`, or extend it?**

**This is the substrate, not the presentation.** Three neighbouring prompts already exist and this
one must extend rather than duplicate them. If you find yourself answering any of these, stop and
say so:

| Prompt | Asked | State |
|---|---|---|
| **R7** — session manager | what should *run* sessions: PTYs, supervision, leases, multiplexing, failure recovery | **answered** — read `answers/R7-answer-session-manager.md` in the pack |
| **R8 §2.6** — agent terminal | state of the art for supervising N agents; human factors, attention, alarm fatigue | split out into R9 at R8's own invitation |
| **R9** — game-styled supervision UI | does a game HUD *skin* help or hurt | dispatched 2026-08-23, alongside this |

R7 asked what runs a session. R9 asks what it should look like. **R12 asks what the layer between
them must know to be honest** — how a session is discovered, named, addressed, resumed, costed, and
how the operator learns that one of them is blocked on a question.

A good answer may conclude **"adopt switchboard and delete your plans"**, and that would be a
better outcome than a design. We are not attached to building this.

---

## 1. What we measured today, and the instruments that said so

Every row below is from a live machine on 2026-08-23, not from a design document.

### 1.1 The identity failure, stated exactly

| Figure | Value | Instrument |
|---|---|---|
| Live `claude.exe` sessions on one workstation | **12** | `Win32_Process` + `~/.claude/sessions/*.json` |
| Sessions sharing the single name `boot pre-flight verification` | **5** | the session registry |
| Distinct lanes those 5 sessions were working in | **4** | their `cwd` |
| Live sessions in the **same** lane worktree and branch (`control-plane`) | **3** | registry, joined on `cwd` |
| Sessions carrying a name that identifies the work | **2 of 12** | registry |

⭐ **The name is inherited from the boot prompt that spawned the terminal, not from the work.** Five
terminals launched from one boot prompt are five rows reading `boot pre-flight verification`, and
the only thing distinguishing them is a working directory the operator has to look up. A question
from one of them can only be answered by messaging all five and letting four ignore it.

`scripts/local_tracker.py::_launch_script` already sets `CLAUDE_CODE_SESSION_NAME` per lane. **No
live session demonstrates it, and no test asserts it reaches the process** — which is precisely the
defect class our own spec names: *"a declared setting that nothing reads is worse than no setting,
because it reports as configured."* Treat "we fixed naming" as `INFERRED`, not `OBSERVED`.

### 1.2 Three sessions, one branch — the control that does not exist

`factory/sessions.py` was written after `finish()` released a claim while its session was still
alive, a relaunch saw a free lane, and three agents ended up sharing one worktree. Nothing
collided, **because two of the three were idle. That is luck, not a control.** Finding F73 states
it: *a claim is not a process.*

The state persists today: three live sessions in `control-plane`.

### 1.3 What the substrate already publishes, unused

Claude Code writes two registries that nothing in our UI reads:

```
~/.claude/sessions/<pid>.json    pid · kind(interactive|bg) · status(idle|busy|waiting)
                                 name · cwd · agent · jobId · messagingSocketPath
~/.claude/jobs/<id>/state.json   state · tempo · tokens · inFlight{tasks,queued}
                                 detail · needs · output.result · children[artifacts]
```

⭐ **`needs` is the field that matters and nobody is reading it.** Of 9 jobs on disk, **4 are
`blocked` with the question written out in plain English** — *"okay to read ZEUS_ALDC_API_KEY?"*,
*"renumber Governor's findings into a wider block before merge?"* — and no surface shows them. The
agents are not stuck because they cannot ask. They are stuck because the asking goes nowhere.

`factory/sessions.py` reads the first registry for liveness. **The second is untouched.**

### 1.4 Per-lane cost — measured today, for the first time

Our own spec said *"nothing currently records what a lane spent."* That was true of our code, not
of the substrate: `~/.claude/projects/<slug>/<session>.jsonl` carries a `usage` block on every
assistant message, so cost is recoverable **retroactively**, for lanes that ran before anyone
thought to instrument them. Built today as `factory/runs.py`:

| Lane | Output tokens | Cache read | Wall clock | Model | Commits |
|---|---|---|---|---|---|
| control-plane | **1,188,083** | 302,442,227 | 22.6 h | opus-5 | 25 |
| artifact | 226,859 | 54,945,137 | 19.4 h | sonnet-5 | 5 |
| certify | 235,623 | 54,917,368 | 1.7 h | sonnet-5 | 4 |
| judgement | — | — | — | — | **never launched** |
| grain | — | — | — | — | **never launched** |

Note the shape: **one lane on opus spent 5× the output tokens of either sonnet lane, and 5.5× the
cache traffic, for 5× the commits.** Whether that is good value is exactly the question a session
manager should let an operator ask, and could not until today.

### 1.5 A crash, and what it revealed about attach

Today a session's host shell died. The findings, in order:

1. **The agent process survived its terminal** and kept working — a subagent was still writing to
   the transcript three minutes after the window was gone. Liveness and visibility are independent.
2. **There is no reattach.** `claude --resume <id>` from a new terminal starts a *second* process
   against the same session id; both append to one transcript and diverge.
3. **Resume refused with `Session … is currently running as a background agent (bg). Use
   `claude agents` to find and attach, or add --fork-session`** — the registry knew, and the
   refusal was correct.
4. **Spawning a session from inside a session poisons it.** The relaunch inherited
   `CLAUDE_CODE_CHILD_SESSION=1` and registered as `kind: bg` — headless, with no TTY, requiring
   `claude agents` to reach. Our launcher clears this marker in the generated `.ps1`; a UI that
   spawns terminals any other way will hit it.

**A session manager that cannot distinguish *alive* from *visible* from *attachable* will lie to
its operator.** These are four states, not two: `RUNNING-ATTACHED`, `RUNNING-ORPHANED`,
`EXITED-RESUMABLE`, `EXITED-GONE`.

### 1.6 What a finished lane leaves behind: nothing

`finish()` asserts, pushes, announces, then **deletes the claim**. The bus is rooted at
`parent.parent/.data`, which inside a worktree is *that worktree's* `.data` — so it is per-lane
(F71) and holds **one event in the entire estate**. An hour after a lane finishes, it is
indistinguishable from a lane that never ran. `factory/runs.py` (today) is the first durable
record; everything before it is `NOT-RECORDED`, which is **not** the same as zero.

---

## 2. The subject: `github.com/doctly/switchboard`

An Electron desktop app, ~328 stars, ~179 commits, macOS/Windows/Linux, that reads the same
substrate we do. Its README claims a session browser over `~/.claude/projects`, a SQLite metadata
cache, full-text search across session content, a grid of **live terminals**, fork-and-resume from
any point, status notifications for permission prompts, and a diff side panel.

**Every one of those is `MARKETED` until you read the source.** The gap between "renders live
terminals" and "renders a transcript tail that looks live" is the whole question, and a README
cannot tell you which it is.

### 2.1 What we need established about it, from code

1. **Attach or resume?** Does it connect to a *running* process — and if so, how, given the
   reattach problem in §1.5 — or does it only spawn new sessions and replay transcripts? This is
   the single most load-bearing question in this brief.
2. **How does it discover sessions?** Transcript directory scan, the `sessions/<pid>.json`
   registry, process table, or its own spawns only? Does it check liveness against the process
   table, or infer it from file existence? (A file outlives its process; getting this backwards
   reports every historical session as live.)
3. **Does it know about `kind: bg`, `jobId`, `needs`, or `status`?** Or is its notion of
   "needs attention" derived from parsing the transcript for permission prompts?
4. **What does SQLite cache, and can it go stale?** Our standing rule: *a stale number may only be
   shown if it is labelled stale, with its age, in the same string as the number.* Does it
   re-measure, or remember?
5. **Windows.** We are Windows-first. Does the terminal layer work there, or is it a
   node-pty-on-POSIX story with a Windows build that compiles and disappoints?
6. **What is its identity model?** Does it show a session's *name*, and would our five identically
   named sessions be five indistinguishable cards in its grid too?
7. **Extension surface.** Plugin, IPC, config, or fork-and-patch? What is the cost of teaching it
   about lanes, claims, worktrees and gates — concepts it has no reason to know?
8. **Security posture.** It is an Electron app reading every transcript on the machine. Node
   integration, context isolation, CSP, auto-update channel, and what leaves the machine.

### 2.2 The comparison we actually want

A **direct table: switchboard vs our tracker vs the ideal**, across at least — session discovery,
liveness detection, identity/naming, attach vs resume, cost visibility, blocked-question surfacing,
multi-repo/worktree awareness, staleness handling, and Windows support.

Then the decision, argued: **adopt, adopt-and-extend, take the ideas and build, or ignore.** Say
what we would lose in each case. If adopting means giving up lane/claim/gate concepts, say whether
those concepts are worth the loss.

---

## 3. The questions beyond switchboard

### 3.1 The session-manager substrate, generally

What does the state of the art make first-class that neither we nor switchboard have? Compare real
systems — tmux/zellij session managers, Warp, VS Code's terminal API, `screen`, orchestration UIs
from agent frameworks, and anything shipping in 2026 that supervises N agent processes. For each:
what is the unit of identity, how is a dead session distinguished from a quiet one, and how does a
question from an agent reach a human?

### 3.2 Naming and addressing

Our five-identical-names failure is not unique. **How do multi-process supervisors solve identity?**
Content-derived names, user-assigned, hierarchical (project/lane/attempt), or stable ids with
display names layered on? What survives a restart, and what should a name be derived *from* — the
task, the worktree, the branch, or the boot prompt? (Ours derives from the boot prompt, which is
why five terminals share one.)

### 3.3 The blocked-question channel

Four agents are blocked on written questions no surface shows. What is the evidence on **routing an
agent's question to a human** — inbox, per-session badge, a single merged queue, push notification,
interrupt? What does the research say about the failure mode we are in: not alarm fatigue, but
**alarm absence**, where the signal exists and is never surfaced? And what is the right behaviour
when two agents ask at once?

### 3.4 Cost as a supervision signal

Now that per-lane cost is measurable (§1.4), what should a supervisor *do* with it? Live burn rate,
budget per lane, an alert when a lane's spend detaches from its commits, comparative cost per
outcome? Cite anyone actually doing this. Distinguish what is useful from what merely looks like a
dashboard — our metrics module refuses an activity metric with no paired outcome metric, and cost
without an outcome to anchor it is exactly such a metric.

### 3.5 Productivity — what actually makes a small team ship faster

Beyond supervision: **what changes throughput** when one operator drives several agents? Candidates
we want assessed with evidence, plus what we have missed — templated session launches, a queue of
prepared prompts, session forking to explore two options, cross-session search, replay/undo,
checkpoint-and-branch, batch approval of routine permissions, and handoff automation between
sessions. For each, say whether the evidence is a **paper, a benchmark, a production deployment, or
a demo** — and say which are traps that add ceremony without throughput.

---

## 4. Constraints any recommendation must respect

- **Windows-first** on the operator's machine. WSL exists; say what changes.
- **Three concurrent lanes** is the current ceiling, from a file-conflict graph (`factory/lanes.py`).
  A UI that assumes ten agents is answering a question we do not have yet.
- **Small team.** A design needing a platform team to run is wrong regardless of merit.
- **Per-secret human approval is a hard rule.** A supervisor that batch-approves credential access
  is out, however convenient. Batch-approving *file reads* is a different question and is open.
- **No stale number without its age in the same string.** A cached view that can quietly show
  yesterday's state is the drift this project exists to remove.
- **The existing instrument panel is never removed**, only added to.

## 5. What a good answer looks like

- **Opinionated.** Adopt, extend, or build — pick one and defend it.
- **Sourced from code** for anything about switchboard. A README claim repeated back is worth
  nothing to us; we have been burned by exactly that.
- **Costed.** Rough effort for each path, and what we stop being able to do.
- **Willing to say "you already have this"** — if the answer is that `sessions.py` plus fifty lines
  of tracker HTML gets 80% of switchboard, that is the most valuable answer available.

## 6. Deliverable shape

1. Executive answer — adopt / extend / build, and the first change to make.
2. Switchboard, from source: what it actually does, per §2.1's eight questions.
3. The comparison table of §2.2, and the decision argued.
4. The substrate: identity, liveness, attach, and the four states of §1.5.
5. The blocked-question channel.
6. Cost as a supervision signal.
7. Productivity features, tiered by evidence quality, including the traps.
8. What you would refuse to build, and why.

## 7. Tier every claim

`OBSERVED` — you read the source or ran it · `REPORTED` — a credible postmortem or paper ·
`MARKETED` — the vendor or README says so and nobody independent has confirmed it · `INFERRED` —
your reasoning from the above.

**A `MARKETED` claim may not be used as a design premise.** Everything in §2 about switchboard is
currently `MARKETED`. Moving those to `OBSERVED` is most of this brief's value.
