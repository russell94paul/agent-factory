# R8 — An agent factory for data engineering: team architecture, sandboxes, and what we should have built

**Status: NOT DISPATCHED.** Written 2026-08-22. Paste the whole file. The answer lands beside it as
`docs/research/answers/R8-answer-data-engineering-agent-factory.md`.

Read `R2-topology.md`, `R3-control-plane-and-optimizer.md`, `R5-build-velocity.md` and
`R7-session-manager.md` first if you have them. R2 asked what shape the build plane should be, R3
what controls it needs, R5 measured what parallel agent sessions actually cost us, R7 asked what
should *run* the sessions. **This one asks what the factory should be when the work is data
engineering rather than software engineering** — a domain where "the tests pass" is not evidence
that anything is correct.

⚠ **Standing rule in this estate: an object named by a handoff is a hypothesis, not a finding.**
Everything in the "what we have" tables below was measured on 2026-08-22 and cites where. Treat
every vendor claim you meet with the same suspicion — read the source, not the launch post, and
tier every claim you report (see §7).

---

## 0. Why data engineering changes the problem

Most agent-orchestration writing assumes the work is **code**: the agent edits a file, tests run, CI
is the oracle. Our work is **data**, and four things break that assumption:

1. **The oracle is downstream and expensive.** A warehouse view can be syntactically perfect, pass
   every test, deploy cleanly, and be wrong in a way only visible when a dashboard renders a number
   a human recognises as impossible. Our own standing rule is that a query-layer check is *not* a
   render check — a repoint once passed DAX parity while every visual showed "Error loading data".
2. **Blast radius is not bounded by the repo.** An agent that writes SQL can drop a table, exhaust a
   warehouse, or silently change a number a client is invoiced against. `git revert` does not undo
   a `CREATE OR REPLACE` that stripped ownership and a share grant.
3. **Correctness is a *measurement*, not a test.** "Did this change only what it should?" is a
   before/after row-count and delta question against production-scale data. It cannot be answered in
   a unit test, and it cannot be answered without touching something real.
4. **Credentials are the whole job.** Data agents need warehouse, API and vault access by
   definition. Every sandbox story that assumes "no network, no secrets" answers a different
   question than ours.

**A good answer to this brief is one that takes those four seriously.** An answer that recommends a
generic multi-agent framework without addressing the downstream oracle or the credential boundary
has not read the question.

---

## 1. What we have, measured 2026-08-22

A working parallel-lane factory, built over a handful of sessions. Three lanes ran end to end for
the first time on the day this was written.

| Capability | State | Evidence |
|---|---|---|
| Isolated git worktree + branch per agent | **built** | `factory/worktrees.py`; 3 lanes, 20 commits, zero cross-lane conflicts |
| Lanes grouped by **file locality**, not dependency order | built | `factory/lanes.py` |
| Conflict graph, machine-derived | built | max independent set = **3** — we cannot run 4 agents |
| Claim/lease per lane, refusing overlap | built | `factory/claims.py`, `STALE_AFTER = 4h`, does **not** auto-expire |
| Durable corrections ledger, one file per finding | built | `docs/findings.d/`, after three lanes collided writing one file |
| Live agent-to-agent channel + hook delivery | built (today) | `factory/bus.py`, injected as `additionalContext` |
| Lane close: assert → push → announce → release, never merge | built (today) | `factory/finish.py` |
| 30 readiness gates, re-measured per request | built | `factory/readiness.py` — **9 of 30 pass** |
| Evaluator as a separate principal | partial | R3 ranks a separate local process **rank 5, "mostly theatre"** |
| Cost per agent run | **not instrumented** | nothing records tokens or wall clock |
| Sandboxing of any kind | **none** | agents run as the user, with the user's credentials |
| Data-layer blast-radius control | **none** | no dry-run gate, no row-count diff, no rollback capture |

### The numbers that should shape your answer

| Figure | Value | Basis |
|---|---|---|
| Cross-agent conflict rate on a **shared** branch | 41.7% | MEASURED, R5 |
| Max concurrent lanes (conflict graph) | 3 | DERIVED from `lanes.py` |
| Recorded runs that finished with no human | **3 of 14** | MEASURED, audits |
| Stage attempts failed vs completed, all-time | 1001 / 165 | MEASURED — mostly one uncapped-restart incident |
| Worst restarts in a single run | 352 | MEASURED |
| Gate events that were ever a **refusal** | **0 of 22** | MEASURED |
| Eval corpus size / strata | 1 case, 0 strata | MEASURED — R1 says a 10%-prevalence blind spot needs **29** cases |
| Dimensions covered by the agent version hash | **0 of 15** | MEASURED — prompt, model, tools, contract version all unhashed |

⭐ **Read those last three together.** We have an evaluation harness whose corpus cannot detect
anything, a gate set never observed refusing, and no way to say which agent produced a result. That
is the actual state of "certified output" here, and any architecture you recommend has to improve
it or it is decoration.

---

## 1b. Our own strawman — please attack it

We wrote an initial architecture *before* dispatching this, deliberately: an open question gets a
survey back, a concrete proposal gets an argument back. It is
`agent-factory/docs/specs/architecture-v0.md`, and its central claim is:

> **An agent's isolation tier is chosen by what its task touches, not by what kind of agent it is** —
> T0 worktree (files only, no egress, no DB verbs) · T1 container + egress allowlist + read-only
> warehouse role · T2 container + an **ephemeral zero-copy clone schema** where full DDL is
> permitted and thrown away.

The argument for it is that our 3-lane ceiling is a *file*-conflict limit, which is a property of
code work — two agents building two views in two clone schemas share no file and no row, so the
cap should not generalise to data work.

**We think the two most likely ways that is wrong are:**

1. Snowflake zero-copy clones may be cheap to create but expensive to validate against, and a clone
   of a *share* may not behave like the real thing. If T2 is not actually cheap the idea collapses.
2. "Data work does not conflict" is asserted, not measured. Two agents can absolutely collide on a
   shared dimension table or the same `REPORT_COMMON` object — the conflict graph may need
   *different edges*, not fewer.

Tell us if either is fatal, and tell us if there is a fifth option we have not seen. **We would
rather be told the ladder is wrong now than discover it at tier 2.**

---

## 2. The questions

### 2.1 Team architecture — go deep, and be concrete

Enumerate and **compare** the multi-agent topologies that are actually in production use, not a
taxonomy for its own sake. At minimum:

- **Orchestrator–worker / supervisor** (a planner decomposes, workers execute, supervisor merges)
- **Hierarchical / manager-of-managers** — where does it stop paying?
- **Blackboard** (shared workspace, agents opportunistically contribute) — our `findings.d` +
  `bus` is a degenerate blackboard; is the full pattern worth it?
- **Actor model / supervisor trees** (Erlang-style restart strategies) — our reaper and attempt cap
  are a poor reimplementation of `one_for_one`; should we adopt the real semantics?
- **Market / auction / contract-net** — agents bid for tasks. Does this ever beat static assignment
  when the tasks have a known conflict graph like ours?
- **Swarm / stigmergic** — agents coordinate only through artefacts left in the environment.
- **Debate / adversarial pairs** — one agent produces, another refutes. We already do this manually:
  a reviewer agent found **6 real defects** in a lane's own diff on 2026-08-22, and another found 4
  more, "three of them mine and one of them severe". **Should the reviewer be structural rather than
  a habit?**

For each: what does it assume about task decomposability, what does it cost in tokens and wall
clock, what is its failure mode under partial failure, and **which real system uses it**.

Then answer directly: **given a conflict graph that caps us at 3 concurrent lanes, which topology
raises the ceiling, and which merely reorganises the same three agents?**

### 2.2 Agent communication — mechanisms, not vibes

Compare, with real systems as evidence:

- shared filesystem / blackboard (ours today)
- message bus / pub-sub, and whether ordering and delivery guarantees matter here
- direct RPC or handoff (`handoff` in OpenAI Swarm, `transfer_to_agent` patterns)
- structured artefact passing (a typed contract between stages)
- context injection into a running agent (what we built today via a hook)
- shared memory / vector store as an implicit channel — and the contamination risk

Specific questions we have paid for:
- **We separated the durable record from the live channel** after a shared ledger file collided
  three ways. Is that split standard practice, and what is it called in the literature?
- **A lane cannot currently ask another lane a question** — every real question needed a human. Is
  agent-to-agent request/response worth building, or is human-in-the-loop the correct terminus for
  a question an agent cannot answer itself?
- What is the evidence on **context poisoning between agents** — one agent's wrong conclusion
  propagating? We have a live instance: a research answer named the wrong component and it was
  carried into a second research question before anyone checked (finding F1).

### 2.3 Sandboxes and autonomous completion — the part to go furthest on

**This is the section most likely to change what we build.** Survey what is genuinely current for
running an agent that must complete a task autonomously, with real credentials, without a human
watching:

- **microVMs** — Firecracker, Cloud Hypervisor. Boot time, snapshot/restore, per-task isolation.
- **Container + syscall filtering** — gVisor, Kata, seccomp/landlock profiles.
- **Managed agent sandboxes** — E2B, Modal, Daytona, Fly Machines, Cloudflare Containers,
  Anthropic's own sandbox tooling. For each: isolation boundary, cold start, filesystem
  persistence, network egress control, secret injection model, and cost.
- **Devcontainers / ephemeral CI runners** as a poor-man's sandbox.
- **Snapshot-and-fork**: can an agent branch its *entire world* (fs + process + db) to explore two
  options and discard one? Which systems actually do this today?

Then the questions that matter for us specifically:

1. **Egress control with real credentials.** We need Snowflake, Azure Key Vault and vendor APIs
   reachable, and nothing else. What is the current best practice — proxy allowlist, credential
   masking with sentinel substitution at a proxy, short-lived scoped tokens, or all three?
2. **The database is not in the sandbox.** Isolating the filesystem does nothing when the dangerous
   verb is `CREATE OR REPLACE` on a shared warehouse. What patterns exist for *data* sandboxing —
   zero-copy clones (Snowflake `CLONE`), transactional rollback, shadow schemas, dbt's
   `--defer`/`--target`? Which of these can be made **mandatory** rather than conventional?
3. **Autonomy verification.** How do teams prove an agent's isolation actually held, rather than
   trusting it? R3's line for us was that isolation must be machine-checkable **evidence** —
   network/IMDS/rootfs/caps/net-io-zero — not trust. What does the state of the art check?
4. **What is the longest an agent is reliably left alone in production today**, by anyone, and what
   makes that possible? Cite specifics; we have 3-of-14 and would like to know what good looks like.

### 2.4 Our architecture vs the optimal scalable one

Give us a **direct comparison table** — current vs recommended — across at least: isolation unit,
concurrency ceiling, scheduling, communication, failure handling, evaluation, cost control,
credential boundary, data blast radius, and observability.

Then answer the uncomfortable question honestly: **is the worktree-on-one-machine model a stepping
stone or a dead end?** It gave us zero cross-lane conflicts and is capped at three agents on one
laptop. If the answer is "scale it to remote sandboxes", say what breaks first — we already know
one thing that breaks, because `~/.claude/skills/` is not worktree-isolated and an edit there is
instantly global (F53).

Sequence the migration. **What is the smallest change with the largest effect**, and what must
*not* be built yet?

### 2.5 Experimental team structures worth trying

Beyond the settled patterns, what is genuinely being experimented with that we could run as a
lane next week? Candidates we have heard of and want assessed with evidence, plus anything we
have missed:

- generator/critic and constitutional self-critique loops
- **tournament / best-of-N with an independent judge** — R1 warns one-run calibration is folklore
- role specialisation vs identical generalists — does specialisation actually beat a good prompt?
- long-lived agents with persistent memory vs fresh-context agents per task
- an agent that **writes and improves other agents' prompts** — this repo is literally called a
  factory; is a self-improving prompt loop credible yet, or a known failure mode?
- economic controls: token budgets as a first-class scheduling input

For each, say whether the evidence is a **paper, a benchmark, a production deployment, or a demo**.

### 2.6 The agent terminal — a UI/UX strand

We are building a terminal where several agents work visibly at once, and we think the interaction
model is a genuinely new surface rather than a dashboard. Current state: one Windows Terminal
window, one pane per lane, per-lane colour and title, a bell + taskbar flash when an agent needs a
human, and a plain shell as a "conductor" pane. It is honest but it is a terminal multiplexer.

What we want to know: **what is the state of the art for supervising several autonomous agents at
once**, and what does the research say about the human factors — attention switching between N
concurrent agents, how to surface "this one needs you" without alarm fatigue, how to show an agent's
*intent* before it acts, and how interruption and steering should work mid-task. Cite real
interfaces. If this strand deserves its own brief, say so and we will split it.

---

## 3. Constraints any recommendation must respect

- **Windows-first on the operator's machine.** WSL is available; a recommendation that assumes Linux
  everywhere must say what changes.
- **Azure** is the cloud (Container Instances, Container Apps, Key Vault). Snowflake is the
  warehouse. Prefect 3 is the run plane; our build plane at `:8765` is **bespoke and does not import
  Prefect**, so none of Prefect's retry/concurrency primitives are available to it (R2-followup).
- **Per-secret human approval is a hard rule**, not a preference. Any design where an agent
  self-serves credentials is out, however elegant.
- **Evidence-gated deploys are a hard rule**: prove the target object, validate at the layer the
  consumer reads, prove no regression, capture a rollback, and only then deploy.
- Small team. A design needing a platform team to operate is the wrong answer regardless of merit.

---

## 4. What a good answer looks like

- **Opinionated.** We can read a taxonomy ourselves. Tell us what to build, in what order, and what
  to refuse.
- **Sourced.** Link the repo, the paper, the postmortem. A claim with no source is a hypothesis, and
  should be labelled one.
- **Costed.** Rough token and money order-of-magnitude per pattern. "Run 5 agents in parallel" and
  "run 5 agents in parallel and have 3 more review them" are very different bills.
- **Honest about maturity.** Separate what is in production somewhere, from what is in a paper, from
  what is a compelling demo. **A demo is not evidence that something survives a bad day.**
- **Willing to tell us we are wrong.** If worktree isolation, the conflict graph, or the whole
  lane model is the wrong abstraction for data work, say so plainly and say what replaces it.

## 5. Deliverable shape

1. Executive answer — the one change to make first, and why.
2. Team architecture: comparison, then a recommendation for our conflict graph.
3. Communication: mechanism recommendation, with the record/channel split assessed.
4. Sandboxes: the depth section — including data-layer sandboxing, not just filesystem.
5. Current vs optimal table, and a sequenced migration.
6. Experimental structures, tiered by evidence quality.
7. The agent-terminal UI strand — or a recommendation to split it.
8. What you would refuse to build, and why.

## 6. Explicitly out of scope

Model choice and prompt-engineering technique. We have those covered, and a section on
chain-of-thought will be read as padding.

## 7. Tier every claim you make

Use these labels inline, the same discipline we hold our own numbers to:

`OBSERVED` — you read the source or ran it · `REPORTED` — a credible postmortem or paper ·
`MARKETED` — the vendor says so and nobody independent has confirmed it · `INFERRED` — your
reasoning from the above.

**A `MARKETED` claim may not be used as a design premise.** We have been burned specifically by
this: a gate that reported PASS while measuring nothing, a detector that silently degraded to
reporting 1 finding where the real engine reports 313, and a launcher that announced the model it
was running on while running a different one. Assume any capability you cannot see the source of is
absent until proven otherwise.
