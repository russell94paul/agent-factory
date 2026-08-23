# R14 — Attack our structure, name the right objects, and design something people are glad to open

**Status: NOT DISPATCHED.** Written 2026-08-23. Paste the whole file. Attach
`docs/research/ui-surface-inventory.md` **and the repo** — this pass is worth little without the
code, and §2 explains exactly what to read.
The answer is filed at `docs/research/answers/R14-answer-structure-model-and-joy.md`.


## Run log

| Run | Dispatched | Outcome |
|---|---|---|
| 1 | 2026-08-23 | ⚠ **Recorded as dispatched, but it never ran.** Corrected 2026-08-23 on Paul's word. The row is kept rather than deleted: a send that did not happen is exactly what this table exists to catch, and erasing it would leave the same blind spot that made "which did I upload?" unanswerable. |
| 2 | pending | Dispatch with `R14-evidence-pack.md` attached (372 KB, rebuild with `scripts/build_r14_pack.py`). |

> Kept because `factory.dispatch` reads a status line and the presence of an answer file, and by its own account cannot see whether a prompt was ever actually pasted anywhere. Without this table "which did I send, and when?" is not answerable from disk. **Add a row every time this prompt is dispatched.**

---

## Who we need you to be

**A staff-level engineer with a designer's eye, brought in to review a codebase that works and to
say what is wrong with its bones.** You have done the unglamorous half of this job: you can read
eight thousand lines of Python and tell which module is load-bearing, which is a god-object wearing
a tidy docstring, which abstraction is one concept pretending to be three, and which convention has
quietly forked into two.

And you care how software *feels*. You believe an instrument panel can be beautiful without being
decorative, that motion should carry information or not exist, and that a tool someone opens twenty
times a day earns craft in a way a landing page never does.

**Be adversarial about the structure and generous about the ambition.** We would rather be told the
module boundaries are wrong now than discover it at twenty thousand lines.

**Ground every structural claim in a file and a line.** If you cannot see something, write
`NOT-SUPPLIED` and name it. We have twice paid for a research pass that answered from a summary
instead of the source, and both times we only found out afterwards.

---

## 0. What this pass is NOT — three neighbours, so you do not re-answer them

| Pass | Asked | State |
|---|---|---|
| **R11** | what concepts do other agent factories make first-class that we have no name for | **ANSWERED** — read `answers/R11-answer-factory-concept-diff.md`. Do not re-survey vendors |
| **R12** | should we adopt an existing session manager | **ANSWERED** — adopt-with-caveats; its own evidence undercut it |
| **R13** | survey every architecture, stack and tool that could build this; make "fast" a number | **in flight, dispatched the same day as this** |

**R13 looks outward at the option space. R14 looks inward at what we built and forward at what it
should feel like.** If you find yourself recommending a UI stack or benchmarking Electron against
Tauri, stop — that is R13's. If you find yourself listing what CrewAI calls a Crew, stop — that is
R11's, and it is answered.

**What is left, and what we want from you:** is our decomposition right, are our objects the right
objects, and what would make this a joy to use.

## 1. What the system is, so you can judge whether the code matches

> **A team of agents did the work, and we can prove it — or we can prove we could not tell.**

An **evidence** product, not a process product. It exists because two earlier mechanisms in this
estate acted without anything measuring whether the action helped — one produced *233 diagnoses,
234 escalations and 0 fixes over 81 days*; another ran *965 times, recorded its own 1.6% success
rate, and never adjusted*.

Four planes, hard boundary between RUN and PROVE (the thing measured must not be the thing
measuring):

```
APPROVE   humans only. merge · per-secret grant · promote to prod
PROVE     readiness gates · a four-valued contract · findings ledger · run audits
RUN       T0 git worktree · T1 container · T2 container + ephemeral DB clone
DECIDE    conflict graph · claims · scheduling · caps · budgets
```

**Agents are Claude Code CLI sessions**, one git worktree and branch each, writing JSONL
transcripts and registering in `~/.claude/sessions/<pid>.json`. Python, Windows-first, Azure,
Snowflake, Prefect 3 as the *run* plane; the build plane is bespoke and does not import Prefect.

## 2. The codebase, measured 2026-08-23 — read these first

```
factory/ + scripts/ + evaluator_service/     8,772 lines of Python
tests/                                       1,654 lines  (19%)
docs/                                        71 files, 8.6 MB
```

**Read in this order:** `contract.py` (what "done" and "I could not tell" mean — everything depends
on it) → `readiness.py` → `lanes.py` → `claims.py` → `worktrees.py` → `finish.py` → `runs.py` →
`sessions.py` → `bus.py` → `board.py`.

The full module map, largest first:

```
1029  readiness.py    30 gates, re-measured per request
 378  lanes.py        the conflict graph — file locality, not dependency order
 311  connector_contract.py   A1-A12, the GreenContract for a connector
 280  sessions.py     which sessions are live, and what they are blocked on
 245  runs.py         the lane run ledger + per-lane cost from transcripts
 217  schedule.py     how fast is this going
 204  handoff.py      closing a lane and handing the session on
 203  evaluator.py    the agent's only route to a verdict — a separate principal
 193  dispatch.py     which research prompts are waiting, and which are lying about it
 185  findings.py     the corrections ledger, as data
 159  finish.py       assert -> push -> announce -> release. Never merges
 158  board.py        tasks GENERATED from gates, so a list cannot drift from what is measured
 152  bus.py          the live channel between lanes
 150  claims.py       who holds which lane
 144  tasks.py        append-only, evidence-gated
 134  certify.py      judge a connector against its blueprint
 124  worktrees.py    one worktree per lane
 115  contract.py     four-valued verdict: PASS / FAIL / UNMEASURABLE / NOT_RUN
 110  corpus.py       the eval corpus, tamper-evident data rather than executed code
 102  deploy.py       put an agent in a repo, bounded
  93  synthesis.py    is the research record current with the answers on disk
  90  evals.py        the negative control that makes the harness mean anything
  85  demo.py · 80 operator.py · 75 metrics.py · 70 blueprint.py · 68 calibration.py · 24 targets.py
```

Internal coupling is almost flat — most modules import nothing from their siblings. `finish.py` is
the only hub (bus, claims, findings, runs, sessions, worktrees). `board.py` and `lanes.py` both
depend on `readiness.py`.

### 2.1 Three structural facts we want you to judge, not just note

1. **`readiness.py` is 1,029 lines — 12% of the codebase — and two modules depend on it.** It holds
   thirty gate definitions *and* the machinery that measures them. Is that a god-module, or is a
   gate registry legitimately one file? Say which, and if it should split, say along what seam.
2. **8 of 29 modules have no test: `board`, `claims`, `demo`, `deploy`, `handoff`, `operator`,
   `schedule`, `worktrees`.** Two of those — **`claims.py` and `worktrees.py` — are the
   concurrency-safety primitives**, the things that stop two agents sharing one branch. The suite is
   135 green tests over the *other* modules. What does that tell you about where our confidence
   actually comes from?
3. **State lives in at least five roots, under two conflicting conventions.** `bus.py`,
   `claims.py` and `operator.py` resolve to `parent.parent/.data`, which **inside a git worktree is
   that worktree's own `.data`** — so they are per-lane and invisible to each other. `runs.py`
   deliberately breaks that and resolves to the primary worktree. `sessions.py` reads three roots
   under `~/.claude`. **The convention forked and nothing enforces either half.** What is the right
   answer — a single store, a declared boundary per concern, or something else?

### 2.2 Flaws we already know — find the ones we do not

Listed so you do not spend the pass rediscovering them:

- The bus is per-worktree and holds **one event in the entire estate**; lanes cannot see each other
  live.
- A claim is a file, not a lock, and **not a process** — a released claim let a second agent into a
  live worktree.
- The findings ledger had to become a directory after three lanes wrote colliding ids into one file;
  one lane branched before that and its ids **still collide, and git merges it clean**.
- `0 of 22` gate events were ever a refusal. `0 of 15` version-hash dimensions are covered.
- The tracker re-measures 30 probes serially — **10–19 seconds a page** — and its server is
  single-threaded, so two concurrent requests return empty.

**Assume there are worse ones we have not found. Those are what we are paying for.**

## 3. The object model — the question underneath everything

We manage: **agents, agent teams, sessions, lanes, worktrees, claims, tasks, gates, findings, runs,
research prompts, blueprints, contracts.** That list grew by accretion; nobody designed it.

- Which of these are **genuinely first-class**, and which are two names for one thing, or one name
  hiding two? (Candidates for the second: *lane* is currently a unit of work, a file-conflict set,
  a branch and a terminal all at once. *Session* is a process, a transcript and an identity.)
- What is the **right primary object** of a system that manages agent teams — the agent, the team,
  the task, the session, the artefact, or the decision? Argue it.
- What is missing? What object would a mature version of this have that we have no word for —
  bearing in mind R11 already answered the *vendor* version of this question, so we want the one
  that falls out of **our** domain: certified delivery by an agent team.
- **Teams.** We have lanes but no team object at all. Should a team be first-class — composition,
  roles, a shared budget, a lifecycle — or is a team just a set of lanes with a name?

## 4. Repo structure

- Is one package (`factory/`) with 29 flat modules right at 8.7k lines, and what does it become at
  30k? If it should be split — by plane (decide/run/prove/approve), by lifecycle, by something else?
- **Where should the boundary between library and CLI and service be?** We currently have a package,
  loose `scripts/`, a separate `evaluator_service/`, and a tracker that imports from all of them.
- Monorepo or not: today `agent-factory` holds code and contracts, while **its evidence, boot prompts
  and session memory live in a different repo entirely** (`aldc-launchpad`), and the connector
  runtime is a third. Is that separation sound, or is it why nothing can see everything?
- `docs/` is 8.6 MB and 71 files, and one directory (`docs/research/`) is load-bearing — an
  instrument globs it and a test fails if the record drifts. **Documentation that code depends on**:
  right, or a smell?

## 5. ⭐ The interface — and this is the part we care most about

**We want this to be a joy to open.** Not "clean", not "modern" — a tool an operator is *glad* to
look at on the fourteenth hour of a build, that makes the state of twelve agents legible at a
glance and never makes them feel behind. Bring everything you have.

**Design it for this moment:** 2am, twelve sessions running across four repositories, two of them
finished and waiting for a merge, one blocked on a question asked forty minutes ago, one quietly
burning tokens on a loop, and a person who has been awake too long and must decide what matters
next. That person should feel **oriented in under three seconds.**

Give us an opinionated design direction, and be specific enough to build from:

- **Information architecture.** What is on the first screen, what earns a second screen, and what
  should never be shown unless it is wrong. What is the resting state when everything is fine —
  because most of the time everything is fine, and a dashboard that looks alarming at rest teaches
  people to ignore it.
- **Hierarchy and rhythm.** Type scale, density, spacing, alignment, how a table of twelve sessions
  stays scannable. We would rather read one number than four charts.
- **Colour with a job.** Our verdicts are four-valued — `PASS` / `FAIL` / `UNMEASURABLE` /
  `NOT_RUN` — and **`UNMEASURABLE` is not a warning, it is "the instrument could not see"**. Most
  palettes have no room for that idea. Solve it. Light and dark, and accessible contrast in both.
- **Motion that encodes something.** Our standing rule: motion must carry information or not exist —
  a page that animates to signal that a machine made it is a failure. Where does motion genuinely
  help here (state transitions, an agent going quiet, a value being re-measured), and where is it
  noise?
- **Delight that survives the tenth viewing.** The difference between a flourish that earns its
  place and one that becomes friction. Give examples of both.
- **The emotional shape of failure.** How does a tool tell someone something is broken without
  making them feel it is their fault, and without crying wolf — given `0 of 22` of our gate events
  have ever been a refusal, so the first real refusal must land as *signal*.
- **Reference the specific.** Name interfaces that get this right and say *what technique* they use
  — not that Linear "feels good" but what it actually does about latency, hierarchy and empty states.

**The hard constraint, and it is what makes this interesting:** every number must be able to say how
old it is. We forbid a silently cached figure — a surface that can quietly show yesterday's state is
the drift this project exists to remove. **Design an interface that is both instant and never
lying about freshness.** That tension is the design problem; do not resolve it by dropping either
half.

## 6. Deliverable shape

1. **The three structural changes you would make first**, in order, with the seam for each.
2. Verdict on the object model — what is first-class, what collapses, what is missing.
3. Repo structure: what it should look like at 30k lines, and the migration that gets there.
4. The design direction — IA, hierarchy, colour, motion, states — concrete enough to build.
5. How freshness is expressed without making the interface anxious.
6. **What you would refuse to build, and what we should delete.**

## 7. Constraints

Windows-first · small team, no platform team to operate anything · three concurrent lanes today ·
per-secret human approval is a hard rule · **no unlabelled stale numbers** · the existing instrument
panel is added to, never removed.

⚠ **One question is genuinely open and must not be answered by accident.** We have a standing rule
that **no terminal is embedded in a page**. It has never been tested — one pass restated our
position back to us, another was never told it existed. The operator's current position is that
*terminal mode should exit*: the terminal is an escape hatch, not the interface. **If your design
depends on that, say which branch you took and design the other one too.**

## 8. Tier every claim

`OBSERVED` — you read the source or ran it · `REPORTED` — a credible postmortem, paper or write-up ·
`MARKETED` — a vendor says so and nobody independent confirmed it · `INFERRED` — your reasoning.

**A `MARKETED` claim may not be a design premise.** We have shipped a gate that reported PASS while
measuring nothing and a launcher that announced one model while running another. Assume any
capability you cannot see the source of is absent until proven otherwise.
