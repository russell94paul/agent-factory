# R14 — Attack our structure, name the right objects, and design something people are glad to open

**Status: ANSWERED 2026-08-23 (run 2).** Written 2026-08-23. Paste the whole file. Attach
`docs/research/ui-surface-inventory.md` **and the repo** — this pass is worth little without the
code, and §2 explains exactly what to read.
The answer is filed at `docs/research/answers/R14-answer-structure-model-and-joy.md`.


## Run log

| Run | Dispatched | Outcome |
|---|---|---|
| 2 | 2026-08-23 | **Answered — but NOT by an outside model.** Run locally as a Claude subagent with full read access to this repo, so for the first time the pass actually read the modules instead of a summary. ⚠ **That is a real trade and it cuts both ways.** The brief asked for an adversarial outside view of our bones; an agent reading our own code, in our own estate, with our own conventions in front of it, is **less independent** than the ChatGPT passes were. Weigh its structural findings as well-grounded and its judgement as partial. `NOT-SUPPLIED` should be near-absent in this answer — if it is, that is the access showing, not rigour. |
| 1 | 2026-08-23 | ⚠ **Recorded as dispatched, but it never ran.** Corrected 2026-08-23 on Paul's word. The row is kept rather than deleted: a send that did not happen is exactly what this table exists to catch, and erasing it would leave the same blind spot that made "which did I upload?" unanswerable. |
| 2 | pending | Dispatch with `R14-evidence-pack.md` attached (456 KB — includes the AMT proposal as §A2; rebuild with `scripts/build_r14_pack.py`). Prompt refreshed 2026-08-23 after R8, R13 and R15 all landed: the platform and topology questions are now closed and the terminal question is settled, so this pass is design-only. |

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

**You are the last pass. Every other prompt has answered, and their conclusions are settled.**

| Pass | Asked | Settled conclusion you must NOT re-open |
|---|---|---|
| **R8** | data-engineering factory, sandboxes, the isolation ladder | **The 3-lane cap is an artefact of file conflicts.** A container + its own DB clone per agent makes the ceiling resource-bound. Smallest step: containerise on ONE machine first |
| **R11** | which concepts other factories make first-class | ANSWERED. Do not re-survey vendor taxonomies |
| **R12** | should we adopt an existing session manager | ANSWERED, with caveats; its own evidence undercut it |
| **R13** | the option space — stacks, latency, approval, provenance | **The platform is a VS Code extension**, not a desktop app: the operator already lives in VS Code, and Monaco, LSP, Git and diffs come free. Electron is out on weight. **Do not re-litigate this.** ⚠ A **run 2 is in flight** repairing its migration section — it owns the question *"does an approval surface for a non-engineer fit inside a VS Code extension, given a non-engineer does not have VS Code open?"* **Leave that one to it.** |
| **R15** | read the field's source, repo by repo | ANSWERED. Its desktop-app recommendation **lost to R13's** |

⭐ **Two things are closed and must not be re-opened.** First, **topology**: R13 surveyed seven
orchestration patterns — orchestrator–worker, hierarchical, blackboard, actor/supervisor,
contract-net, stigmergic, generator–critic — and **none raises the concurrency cap**. Second, the
**platform**: it is a VS Code extension. If your answer proposes a new orchestration pattern or a
different UI stack, it is answering a question that is already closed.

**So what is left is exactly your two jobs, and nothing else:** is our decomposition right, and
what should this feel like to use. R13 gave screens and a latency budget; it gave **no design** —
zero mentions of type scale, colour system, hierarchy, empty states or contrast. That gap is why
you exist.

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
factory/ + scripts/ + evaluator_service/     9,342 lines of Python
tests/                                       1,804 lines  (19%) — 143 tests, all passing
docs/                                        71 files, 8.6 MB
readiness                                    10 of 30 gates
```

⚠ **One instrument caveat, because you will see the number and we would rather you distrust it
properly:** the readiness figure read 10, then 9, then 10 within twenty minutes on 2026-08-23, with
the headline agreeing with the PASS count *inside* each run. We have not found the cause. Treat
`10 of 30` as approximate and do not build an argument on its exact value.

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
 270  dispatch.py     which prompts are waiting, which are lying, and what to do next
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

## 4b. ⭐ One document in the pack is not ours, and not evidence

Section A2 of the evidence pack is **`amt-agent-management-terminal.md`** — a 62 KB proposal for an
"Agent-Management Terminal", found unfiled on 2026-08-23 and dated the day before. **No prompt of
ours produced it**, three later passes covered its ground without ever being shown it, and nothing
in it is measured against this repo or carries an evidence tier.

It proposes an Interrupt Inbox, an Agent Radar, Collision Detection, a Terminal Genome and
Resurrection Capsules — respectively the blocked-question channel, a global state view, our
two-agents-in-one-worktree defect, the config hash, and crash recovery.

**Treat it as a vision to argue with, not a finding.** We want to know which of its ideas survive
contact with the code in §2 — and which are the kind of feature that sounds excellent in a document
and dies on first use. Saying "most of this is decoration and here are the two that are not" is a
more useful answer than adopting the list.

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

**The terminal is an escape hatch, not the interface. This is settled — do not re-argue it.**

We asked four passes to argue it on the merits and got no argument back: one restated our own
position, one invented a user study to support it, one deferred to the operator. The lesson was
ours — we kept stating our position inside the question — so we have stopped asking. **Design for
no embedded terminal. A terminal may be launched on demand as an escape hatch and is never the
primary surface.** If you think that is wrong, say so in one paragraph at the end and move on; do
not build your answer around overturning it.

## 8. Tier every claim

`OBSERVED` — you read the source or ran it · `REPORTED` — a credible postmortem, paper or write-up ·
`MARKETED` — a vendor says so and nobody independent confirmed it · `INFERRED` — your reasoning.

**A `MARKETED` claim may not be a design premise.** We have shipped a gate that reported PASS while
measuring nothing and a launcher that announced one model while running another. Assume any
capability you cannot see the source of is absent until proven otherwise.
