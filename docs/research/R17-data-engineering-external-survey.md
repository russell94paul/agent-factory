# R17 — Agent factories for data engineering: the external half of R8, re-asked without a pack

**Status: DISPATCHED 2026-08-23.** Written 2026-08-23. Paste the whole file. **Attach nothing.** The
answer lands beside it as
`docs/research/answers/R17-answer-data-engineering-external-survey.md`.

**Pass type:** EXTERNAL_SURVEY
**Depends on:** none

_Read by `factory.research_run`, which draws this pass's button on the readiness board. DECLARED,
never inferred — a prompt that does not say gets no button. `EXTERNAL_SURVEY` is what tells the
runner to open 3-5 parallel lanes on **different search modalities**; independence risk is LOW
because the web is genuinely outside._

⚠ **This runs HERE, via the `deep-research` skill — not pasted into claude.ai.** An earlier draft of
this file said otherwise. The skill sweeps the open web first and reaches the same internet; what
the paste loop had was *distance*, and the skill buys that back deliberately. What it never had was
the repo, the wiki, the ledger or a verifier.

## Run log

| Run | Date | Outcome |
|---|---|---|
| 1 | 2026-08-23 | Dispatched from the readiness board — EXTERNAL_SURVEY run in-repo via the deep-research skill |
## ⭐ Why this exists, and why there is no evidence pack

R8 was run twice and failed the same way twice.

| Run | Setup | Outcome |
|---|---|---|
| 1 (08-22) | web access, **no repository access** | rejected, never filed. Its own verdict: the external survey is salvageable, *"the comparison against your actual factory is not yet sufficiently grounded."* |
| 2 (08-23) | web access **+ a 481 KB evidence pack attached**, whose own rule was *every internal claim must cite a file and a line from this pack* | filed — with **zero** file paths, **zero** line references, **6** evidence tiers in 26 KB, and **1** `NOT-SUPPLIED`. Structurally complete, evidentially ungrounded. |

Run 2's answer is not bad research. It is good external research with an internal audit bolted on
that never happened. **Asking one web-research pass to survey a literature *and* audit a 481 KB
attachment is the thing that failed, and asking more firmly is not a fix** — run 2 was already
asked as firmly as prose allows.

So R8 is split, and this is the external half:

```
R17 (this file)   the field. Web only. NO internal facts, so there is nothing to ground
                  and no pack to ignore.
R18               our own factory, audited from inside the repo by an agent that can open
                  the files and cite real line numbers. No pack either — it has the repo.
```

**Do not answer any question about our codebase.** If a question here seems to need one, it belongs
to R18: say so and move on. A named handoff is worth more than a thin answer.

## Neighbours — what this pass must NOT answer

| Pass | Owns | Status |
|---|---|---|
| **R18** | our factory: is the isolation ladder right *for us*, what to migrate, in what order | to be written |
| **R12 / R13 / R14** | the interface — session substrate, UI option space, our own IA and design brief | **all answered.** R8's agent-terminal strand is retired into these; do not re-survey supervision UI |
| **R15** | what people actually built, read repository by repository | answered |
| **R11** | which concepts other factories make first-class — vocabulary and taxonomy | answered |

⛔ **One question is deliberately left open and must stay open.** Whether an embedded terminal
belongs in the supervision surface has been answered by accident twice — once by a pass restating
our own position back to us, once by a pass never told the rule existed. Do not resolve it.

---

## 0. Why data engineering changes the problem

Most agent-orchestration writing assumes the work is **code**: the agent edits a file, tests run, CI
is the oracle. The work here is **data**, and four things break that assumption:

1. **The oracle is downstream and expensive.** A warehouse view can be syntactically perfect, pass
   every test, deploy cleanly, and be wrong in a way only visible when a dashboard renders a number
   a human recognises as impossible. A query-layer check is *not* a render check — a repoint once
   passed DAX parity while every visual showed "Error loading data".
2. **Blast radius is not bounded by the repo.** An agent that writes SQL can drop a table, exhaust a
   warehouse, or silently change a number a client is invoiced against. `git revert` does not undo
   a `CREATE OR REPLACE` that stripped ownership and a share grant.
3. **Correctness is a *measurement*, not a test.** "Did this change only what it should?" is a
   before/after row-count and delta question against production-scale data. It cannot be answered in
   a unit test, and it cannot be answered without touching something real.
4. **Credentials are the whole job.** Data agents need warehouse, API and vault access by
   definition. Every sandbox story that assumes "no network, no secrets" answers a different
   question.

**A good answer takes those four seriously.** An answer recommending a generic multi-agent framework
without addressing the downstream oracle or the credential boundary has not read the question.

## 0b. The only context you need about us

Stated so the recommendation lands somewhere real. **This is context, not a claim to verify** — you
have no way to check it and should not try.

- Four engineers. Windows-first operator machine, WSL available. **Azure** (Container Instances,
  Container Apps, Key Vault), **Snowflake**, **Prefect 3** as the run plane. The *build* plane —
  the thing that runs agent migrations — is bespoke and **does not import Prefect**, so none of
  Prefect's retry/concurrency primitives are available to it.
- Agents run today as parallel sessions in **git worktrees on one laptop**, capped at 3 concurrent
  lanes by a **file**-conflict graph. Zero cross-lane conflicts observed; a shared branch was
  measured at a 41.7% cross-agent conflict rate.
- **Per-secret human approval is a hard rule.** Any design where an agent self-serves credentials
  is out, however elegant.
- **Evidence-gated deploys are a hard rule**: prove the target object, validate at the layer the
  consumer actually reads, prove no regression, capture a rollback, then deploy.
- A design needing a platform team to operate is the wrong answer regardless of merit.

---

## 1. The questions

### 1.1 Team architecture — compare, do not taxonomise

Enumerate and **compare** the multi-agent topologies actually in production use:

- **Orchestrator–worker / supervisor** — planner decomposes, workers execute, supervisor merges
- **Hierarchical / manager-of-managers** — where does it stop paying?
- **Blackboard** — shared workspace, opportunistic contribution. Is the full pattern worth it over
  a directory of artefacts plus an append-only channel?
- **Actor model / supervisor trees** — Erlang `one_for_one` / `one_for_all` restart semantics. Is
  adopting the real semantics (Ray actors, Orleans, a Kubernetes controller) better than
  reimplementing a reaper and an attempt cap by hand?
- **Market / auction / contract-net** — does bidding ever beat static assignment when the tasks have
  a **known, static conflict graph**?
- **Swarm / stigmergic** — coordination only through artefacts left in the environment
- **Debate / adversarial pairs** — one produces, another refutes

For each: what it assumes about decomposability, what it costs in tokens and wall clock, its failure
mode under partial failure, and **which real system uses it**.

Then answer directly, because these are the decisions:

1. **Given a conflict graph that caps concurrency at 3, which topology raises the ceiling and which
   merely reorganises the same three agents?** We suspect none of them raise it — that the ceiling
   lifts by making tasks *independent* (per-agent database clones), not by re-drawing the
   coordination graph. Confirm or refute.
2. **Should an adversarial reviewer be structural rather than a habit?** In one day a reviewer
   sub-agent found 6 real defects in a lane's own diff and another found 4 more. What is the
   evidence on generator/critic as a *required* stage — its false-positive rate, its cost, and
   whether the critic must be a different model to be worth anything?

### 1.2 Communication — mechanisms, not vibes

Compare, with real systems as evidence: shared filesystem/blackboard · message bus, and whether
ordering and delivery guarantees matter here · direct RPC handoff (`transfer_to_agent` patterns) ·
structured typed artefact passing · context injection into a running agent · shared memory or vector
store as an implicit channel, and its contamination risk.

Three specific questions:

1. **Separating the durable record from the live channel.** A shared ledger file collided three ways
   when three isolated worktrees each appended the next sequential id. The fix was one append-only
   file per writer for the record, plus a separate ephemeral channel for live nudges. **Is that
   split standard practice, and what is it called in the literature?** Event sourcing? CQRS?
   Something else?
2. **Agent-to-agent request/response.** No lane can currently ask another lane a question, and every
   real question so far needed a *human* — a credential grant, a go/no-go. Is agent-to-agent Q&A
   worth building, or is human-in-the-loop the correct terminus for a question an agent cannot
   answer itself? What goes wrong in systems that built it?
3. **Context poisoning between agents.** What is the evidence on one agent's wrong conclusion
   propagating? We have a live instance: a research answer named the wrong component as the cause of
   a defect, and the misattribution was carried into a second research question before anyone
   checked — verification took one `grep`. What detects this class, cheaply?

### 1.3 Sandboxes and autonomous completion — go furthest here

**This is the section most likely to change what gets built.**

Survey what is genuinely current for running an agent that must complete a task autonomously, with
real credentials, without a human watching:

- **microVMs** — Firecracker, Cloud Hypervisor: boot time, snapshot/restore, per-task isolation
- **Container + syscall filtering** — gVisor, Kata, seccomp/landlock
- **Managed agent sandboxes** — E2B, Modal, Daytona, Fly Machines, Cloudflare Containers,
  Anthropic's own sandbox tooling. For each: isolation boundary, cold start, filesystem persistence,
  egress control, **secret injection model**, cost
- **Devcontainers / ephemeral CI runners** as a poor-man's sandbox
- **Snapshot-and-fork** — can an agent branch its *entire world* (fs + process + db) to explore two
  options and discard one? Which systems do this today?

Then the six that matter specifically:

1. **Egress control with real credentials.** Snowflake, Azure Key Vault and vendor APIs must be
   reachable and nothing else. Current best practice — proxy allowlist, credential masking with
   sentinel substitution at a proxy, short-lived scoped tokens, or all three?
2. ⭐ **The database is not in the sandbox.** Isolating a filesystem does nothing when the dangerous
   verb is `CREATE OR REPLACE` on a shared warehouse. What patterns exist for **data** sandboxing —
   Snowflake zero-copy `CLONE`, transactional rollback, shadow schemas, dbt `--defer`/`--target`?
   **Which can be made *mandatory* rather than conventional** — enforced by a grant the agent cannot
   widen, rather than by an instruction it can ignore?
3. **The economics of the clone, specifically.** Our whole scaling argument rests on this and it is
   the claim most likely to be wrong: *two agents in two ephemeral clone schemas conflict on
   nothing, so the 3-lane file-conflict cap does not generalise to data work.* Two ways it fails —
   **(a)** a zero-copy clone is cheap to *create* and the compute to *validate against it* is not,
   so per-agent clones are unaffordable at real concurrency; **(b)** a clone of a **share** may not
   behave like the real thing. Address both with sourced specifics on Snowflake's actual clone and
   credit semantics, and say plainly if either is fatal.
4. **Does data work actually conflict?** We assert two agents building two views in two schemas
   share no file and no row. Counter-case: they collide on a shared dimension table, a naming
   convention, or the same reporting object. Is the right fix *fewer* conflict edges or
   **different** ones? What do teams running parallel warehouse changes actually collide on?
5. **Autonomy verification.** How do teams *prove* isolation held rather than trusting it —
   machine-checkable evidence such as network/IMDS/rootfs/caps/net-io-zero? What does the state of
   the art check, and what does it miss?
6. **What is the longest an agent is reliably left alone in production today**, by anyone, and what
   makes that possible? Cite specifics. We have 3 of 14 runs finishing without a human and would
   like to know what good looks like.

### 1.4 Experimental structures worth trying next week

What is genuinely being experimented with, and for each: is the evidence a **paper**, a
**benchmark**, a **production deployment**, or a **demo**?

- generator/critic and constitutional self-critique loops
- **tournament / best-of-N with an independent judge** — one-run calibration is folklore
- role specialisation vs identical generalists — does specialisation actually beat a good prompt?
- long-lived agents with persistent memory vs fresh-context agents per task
- **an agent that writes and improves other agents' prompts** — is a self-improving prompt loop
  credible yet, or a known failure mode?
- economic controls: token budgets as a first-class scheduling input

⚠ **A demo is not evidence that something survives a bad day.** Say which of these you would refuse
to run against real credentials, and why.

---

## 2. Deliverable shape

1. **Executive answer** — the one change to make first, and why. One paragraph.
2. **Claims table** — see §3. Not optional, and it comes *before* the prose sections.
3. Team architecture: comparison, then the two direct answers in §1.1.
4. Communication: mechanism recommendation, with the record/channel split named.
5. **Sandboxes** — the depth section, including the data layer, not just the filesystem.
6. Experimental structures, tiered by evidence quality.
7. **What you would refuse to build, and why.**

**Opinionated.** We can read a taxonomy ourselves — tell us what to build, in what order, and what
to refuse. **Sourced** — link the repo, the paper, the postmortem. **Costed** — rough token and
money order of magnitude; "5 agents in parallel" and "5 agents in parallel plus 3 reviewing them"
are very different bills. **Willing to tell us we are wrong** — if the lane model is the wrong
abstraction for data work, say so plainly and say what replaces it.

## 3. ⭐ Tier every claim, in a table, because prose tiering did not survive two runs

Both prior runs were told to tier every claim. Run 2 produced **6 tier markers in 26 KB**. So the
tiering is now a **deliverable with a shape**, not an instruction: a table, before the prose, one
row per load-bearing claim.

| # | Claim | Tier | Source | What would falsify it |
|---|---|---|---|---|

- `OBSERVED` — you read the source or ran it
- `REPORTED` — a credible postmortem, paper, or benchmark
- `MARKETED` — the vendor says so and nobody independent has confirmed it
- `INFERRED` — your reasoning from the above

⛔ **A `MARKETED` claim may not be used as a design premise.** We have been burned specifically by
this: a gate that reported PASS while measuring nothing, a detector that silently degraded to
1 finding where the real engine reports 313, and a launcher that announced the model it was running
on while running a different one. **Assume any capability whose source you cannot see is absent
until proven otherwise.**

Every prose recommendation must reference a row number from that table. A recommendation with no row
is an opinion — which is fine, but label it one.

## 4. Explicitly out of scope

- **Anything about our codebase.** That is R18's and you cannot see it. Say `NOT-APPLICABLE` and
  move on.
- **Supervision UI and interface design.** R12, R13 and R14 own it and are answered.
- **Model choice and prompt-engineering technique.** A section on chain-of-thought reads as padding.
