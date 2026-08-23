# R7 — A session manager for agent teams: what to adopt, what to build, what to automate

**Status: ANSWERED 2026-08-22.** Written 2026-08-22. Paste the whole file. The answer is filed at
`docs/research/answers/R7-answer-session-manager.md`.

Read `R5-build-velocity.md` and `R6-automation-and-alerting.md` first if you have them — this
extends both. R5 measured what parallel agent sessions cost; R6 asked what should watch them; this
asks what should *run* them.

---

## The reference implementation to study

**Switchboard** — a Claude Code session manager: <https://github.com/doctly/switchboard>, shown at
<https://www.reddit.com/r/ClaudeAI/comments/1rr4xrk/showcase_i_built_a_claude_code_session_manager/>

⚠ **Read the code, not the demo.** A showcase post shows the happy path; we need to know how it
handles the parts that break. Specifically: how it attaches to and multiplexes real PTYs, how it
survives a session dying, whether sessions share a working tree or get isolated ones, how it
addresses a session to send input, and what it persists across restarts. Treat the README as a
claim and the source as the evidence — this estate's standing rule is that an object named by a
handoff is a hypothesis until you walk it yourself.

## What we already have, measured

A working orchestrator, built accidentally over one session, at `scripts/local_tracker.py` plus
`factory/` modules. It re-measures 30 readiness gates per request and serves four tabs.

| Capability | State |
|---|---|
| Lanes of work, grouped by **file locality** not dependency order | built |
| Dependency order + conflict map, both derived | built |
| Claim / release lock — a conflicting lane cannot be started | built, drilled |
| One **git worktree and branch per lane** | built |
| Launch into a titled Windows Terminal tab | built; **first real click found a live bug** |
| Pre-answered blockers injected into the launched prompt | built |
| Preflight + generated per-lane and per-session handoff | built |
| Open a new session already holding the handoff | built |
| Per-lane model recommendation (opus / sonnet / haiku) with reasons | built |
| Findings ledger routed to the lanes each entry affects | built |

**Hard-won constraints, all measured rather than assumed:**

- ⛔ **No in-page terminal.** Declined three times. It is a PTY bridge plus a multiplexer to arrive
  somewhere worse than the Windows Terminal already installed, and it turns a local web page into
  a keyboard-attached instruction channel into agents holding shell access. **If Switchboard does
  embed terminals, the interesting question is what it gains that outweighs this** — we want the
  argument, not the feature.
- **Parallelism is capped by files, not dependencies.** 16 of 30 gates have no unmet dependency;
  only **3 lanes** can run together because two pairs share a file. R5 measured why this matters:
  across ~33,000 agent-generated PRs, cross-agent PRs conflicted **41.7%** of the time, mostly
  structurally.
- **Measurement is expensive.** One gate shells out to a full `pytest`, so a page that measures
  costs 8–45s. Any live view must split cheap state from expensive state.
- **"Alive" is not knowable.** A session that is thinking, finished, or dead look identical from
  outside. We render progress markers (commits, dirty files) rather than heartbeats.

## What we need that a session manager alone does not give

This is the part the answer should spend most of its effort on.

### 1. An agent-team configuration surface

Teams should be **assembled**, not hardcoded. `factory/blueprint.py` already has `TeamSpec` and
`AgentSpec` with a version hash covering the composition — and **nothing executes it**; `grep`
finds exactly one caller, a test. So the data model exists and the runtime does not.

What we want: pick a task or ticket, assemble a team for it (roles, models, tool scopes, the
GreenContract that certifies its output), version it, run it, and keep the version pinned to the
verdict so a certification cannot outlive the configuration that earned it.

**Questions.** What does prior art actually do here — are there working examples of *composable*
agent teams rather than fixed pipelines? What belongs in a team spec beyond roles and models, and
what turns out to be over-configuration nobody tunes? How do you avoid a configuration surface so
expressive that every team is bespoke and none is comparable?

### 2. Optimising a team for the task

Paul's words: *"teams can be easily assembled and then optimized with whatever the task/ticket is."*

R3 and R4 (earlier passes here) concluded that **configuration search must come last** — an
optimiser is a search over configurations, a search needs a fitness function, and the fitness
function is the eval. We have a 12-assertion GreenContract but every assertion is currently
UNMEASURABLE against a live target.

**Questions.** Given no live fitness signal yet, what is the *useful* form of "optimise the team
for this ticket" today — heuristic routing by task shape, retrieval of what worked on similar
tickets, something else? What is the cheapest signal that could stand in for a fitness function
without becoming the vacuous "it ran, therefore it worked" metric this estate has already shipped
twice? At what point does an actual optimiser become justified?

### 3. A series of tasks per team, not one

Today a lane is one unit of work started by hand. We want a team to be handed **a queue** and work
it, with dependencies between items and a human gate where one is genuinely needed.

**Questions.** What is the right decomposition unit — ticket, gate, file, something else? How do
queued agent tasks handle a mid-queue failure: stop, skip, retry, escalate? Our existing pipeline
had no attempt cap and once consumed an entire 10-core cloud quota, so bounded retry is not
optional. How do you keep a queue from silently reordering into whatever is easiest?

### 4. Autonomy, bounded

Paul wants autonomous features that improve productivity. This estate's signature failure is a
mechanism that *acts* without anything measuring whether the action worked — a pipeline agent that
ran 81 days producing 233 diagnoses and **zero fixes**, and an automated loop that ran 965 times,
self-recorded a 1.6% success rate, and never adjusted.

**Questions.** Which autonomous behaviours pay off in a multi-session agent setup and which are
traps? Candidates to grade: auto-starting the next eligible lane when one finishes; auto-merging a
lane whose gates all pass; auto-answering a declared blocker from a previous identical answer;
auto-retrying a failed stage under a cap; auto-splitting a lane that grows too large. **For each,
say what makes it safe to leave unattended and how you would make it demonstrably refuse.** A
control nobody has watched refuse something is decoration.

### 5. The interface — a living system, not a dashboard

We use the `living-systems-ui` design approach: one simulation model, a view that is a pure
projection of it, an inspector, and a visual grammar where a planned component never looks built.
Its rule: **a figure that would look identical if the numbers were different is decoration.**

**Questions.** What does excellent look like for *concurrent agent sessions specifically* — what
does an operator need at a glance versus on demand? Are there interfaces in adjacent domains
(orchestration consoles, CI dashboards, trading desks, NOC displays) whose grammar transfers? How
do you show a system where the most important state — is this session actually working — is
**unknowable**, without either faking certainty or drowning the view in caveats?

## What a useful answer looks like

1. **A verdict on Switchboard**: adopt it, fork it, take specific ideas, or build separately — with
   the reasoning, and specifically how it would or would not integrate with worktree-per-lane,
   file-locality conflicts and the claim lock we already have.
2. **A build order** for the five areas above, ranked by effect on *time to one certifiable
   end-to-end run by an assembled team*.
3. For every recommendation: **what it catches, what it cannot catch, and how to make it fire on
   purpose.**
4. Label each **OBSERVED** (seen working with LLM agents, multiple concurrent sessions, one
   repository) or **EXTRAPOLATED** (from human teams, single-agent work, or general practice).
   R6 found *no widely adopted standard* for multi-agent repo work — only blog posts and academic
   prototypes — so say plainly where you are reasoning by analogy.
5. **Name what you could not settle.** Four solid answers and two honest gaps beat six confident
   ones.

## Method note

The estate's own rule, applied to its own research: *an object named by a ticket, boot prompt or
handoff is a hypothesis, not a finding — walk the route yourself before adopting it.* An earlier
pass here named the wrong component as the cause of a defect and the claim was carried into a
second research question before anyone checked; verifying took one grep. A later prompt asserted a
constraint the author had never measured, and it demonstrably changed the ranking of the answer.
Assume the same about anything in this document you can check — including the table of what we
have built, which is a description of code you can read.
