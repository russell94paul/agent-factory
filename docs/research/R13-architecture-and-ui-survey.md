# R13 — Survey every architecture and tool that could build this, before we build any of it

**Status: NOT DISPATCHED.** Written 2026-08-23. Paste the whole file. Attach
`docs/research/ui-surface-inventory.md` — it is our own frozen position and this prompt assumes you
have read it. The answer is filed at `docs/research/answers/R13-answer-architecture-and-ui-survey.md`.

---

## Who we need you to be

**You are a principal-level agentic systems architect who has re-architected live codebases, not
greenfield ones.** The work you are known for is taking a system that already runs, already has
users, and already carries a decade of decisions, and moving it to a better shape *without a
rewrite and without a freeze* — strangler-fig migrations, incremental cutovers, parallel-run
verification, and the judgement to say which parts must not be touched at all.

You are equally at home in two rooms most people only occupy one of:

- **The systems room.** Process supervision, PTYs and job control, filesystem watching, IPC,
  crash-safe local state, concurrency and conflict graphs, sandbox and isolation boundaries,
  credential handling. You know why a thing is slow, at the syscall level, not the framework level.
- **The interface room.** You build developer tools that feel *instant* — sub-frame input latency,
  virtualised lists over tens of thousands of rows, optimistic rendering, incremental
  re-measurement instead of full recomputation. You have opinions about why Linear, Warp, Figma and
  Sublime feel the way they do, and you can name the specific techniques rather than the vibe.

**What we are not asking for.** Not a taxonomy, not a feature list, and not enthusiasm. We want the
survey a sceptical architect would run *before* committing, including the options that would
embarrass us and the option of building nothing.

**The discipline we hold ourselves to, and will hold you to.** Every claim carries its basis (§7).
A vendor claim you have not seen the source or docs for is not evidence. If you cannot see
something, say `NOT-SUPPLIED` and name it — a gap you name is worth more to us than a gap you fill.
**We have been burned twice by research answering a question we did not ask**, and both times the
cause was a constraint we failed to state. §6 states them; if one of them makes a whole branch of
your answer impossible, say so loudly rather than routing around it.

---

## 1. What this system is, in one line — and why it decides everything

> **A team of agents did the work, and we can prove it — or we can prove we could not tell.**

That is the founding claim of the repo, and it means **this is an evidence product, not a process
product.** It exists because two earlier mechanisms in this estate acted without anything measuring
whether the action helped: one produced *233 diagnoses, 234 escalations and 0 fixes over 81 days*;
another ran *965 times, recorded its own 1.6% success rate, and never adjusted*. Both were capable.
Neither was measurable.

⭐ **Hold that against the market.** Every agent session manager we know of manages *processes*.
None answers *who did this work, under what configuration, and what proves it was correct.* If your
answer recommends something that is excellent at rendering terminals and silent on provenance, it
has optimised the wrong axis and we will say so.

## 2. The architecture as it stands

Four planes, with a hard boundary between RUN and PROVE — the thing being measured must not be the
thing doing the measuring:

```
APPROVE   humans only. merge · per-secret grant · promote to prod   ← never automated
PROVE     readiness gates · a contract with a four-valued verdict · findings ledger · run audits
RUN       isolation ladder — T0 git worktree · T1 container · T2 container + ephemeral DB clone
DECIDE    conflict graph · claims · scheduling · caps · budgets · a bespoke build plane at :8765
```

Stack: Python. Windows-first on the operator's machine. Azure (Container Instances, Container Apps,
Key Vault). Snowflake is the warehouse. Prefect 3 is the *run* plane; **the build plane at `:8765`
is bespoke and does not import Prefect**, so none of Prefect's retry or concurrency primitives are
available to it.

**Agents are Claude Code CLI sessions.** They write JSONL transcripts to
`~/.claude/projects/<slug>/<session>.jsonl` (which carry a `usage` block per message, so cost is
measurable retroactively), register themselves in `~/.claude/sessions/<pid>.json`, and background
agents publish state — including a `needs` question in plain English — to
`~/.claude/jobs/<id>/state.json`. Each agent works in its own git worktree on its own branch.

## 3. The measured state, 2026-08-23 — not estimates

```
readiness       10 of 30 gates pass
lanes           5 defined · max 3 concurrent, DERIVED from a file-conflict graph
                2 of the 5 have never been launched
autonomy        3 of 14 recorded runs finished with no human
gate refusals   0 of 22 gate events were ever a refusal
agent versioning  the config hash covers 0 of 15 dimensions — we cannot say which agent produced what
cost per lane   1.23M output tokens / 322M cache-read / 22.8h / opus / 25 commits   (one lane)
                 227k output / 55M cache-read / 19.4h / sonnet / 5 commits          (another)
sessions        12 running on one workstation · 5 shared a single name · 6 shared one directory
delivery        2 pull requests fully green, waiting 6 and 9 DAYS for a human to merge
UI latency      a tracker page load re-measures everything and takes 10–19 SECONDS
                two concurrent requests return empty — the server is single-threaded
```

⭐ **Read the last three together.** Our agents are not slow. Our *humans* are the queue: green work
waits days, and one agent sat on a written question nobody read. Any architecture that makes agents
more visible without making decisions faster has optimised the wrong end.

## 4. What to survey — go wide, this is the point of the pass

We want the **whole option space**, current as of your knowledge cutoff, with real names and links.

### 4.1 Agent orchestration and supervision architectures

Orchestrator–worker, hierarchical, blackboard, actor/supervisor trees (Erlang `one_for_one` and
friends), contract-net/auction, stigmergic, generator–critic pairs. For each: what it assumes about
task decomposability, its failure mode under partial failure, and **which real production system
uses it.** Then: given a conflict graph that caps us at three concurrent lanes, which of these
raises the ceiling and which merely rearranges the same three agents?

### 4.2 The desktop/local-tool architecture decision

This is a local-first tool on Windows that must watch the filesystem, supervise processes and stay
instant. Survey **Electron, Tauri, Wails, native (WinUI/Qt), a local web server + browser, a TUI,
and a VS Code extension** — the last is genuinely open: our operator lives in VS Code already.
For each: cold start, memory, IPC cost, filesystem-watch fidelity on Windows, PTY support,
packaging and update story, and what it costs a small team to maintain.

### 4.3 Make "fast and smooth" a number, not an adjective

Our page takes 10–19 seconds because it re-measures thirty probes serially on every request, and we
have a standing rule that **it may never cache silently** — a surface that can quietly show
yesterday's state is the drift this project exists to remove.

So: **what is the architecture that is both always-current and instant?** Incremental
re-measurement, dependency-tracked invalidation, event-sourced projections, CRDTs, local SQLite
with change feeds, virtualised rendering, optimistic UI with reconciliation. Give us a **latency
budget** — first paint, interaction-to-response, full re-measure — and say what each technique
actually buys in milliseconds. Name the tools and libraries you would use.

### 4.4 The approval surface — the one nobody builds

Our APPROVE plane has **no interface at all**, and it is where delivery is measurably stuck. What
is the state of the art for **reviewing and approving work an agent produced** — the diff, the
evidence, the cost, the provenance, and a decision? Who ships this (GitHub/GitLab agent flows,
Graphite, Devin, Factory.ai, Cursor, Copilot Workspace, others)? What did they learn?

And the harder half: **could a non-engineer safely approve agent work**, and what would they need
to see? Has anyone tried it?

### 4.5 Provenance, lineage and the config hash

We want every artefact traceable to the agent, model, prompt, tool set and contract version that
produced it — and our hash currently covers **0 of 15 dimensions**. What standards or tools exist
(OpenTelemetry GenAI semantic conventions, SLSA/in-toto, ML model cards, data-lineage tools)? What
would you actually adopt, and what is over-engineering at our size?

### 4.6 Getting an agent's question to a human in minutes, not days

Our measured latency is **days**. Survey the mechanisms — interrupt, modal, OS notification, a
merged inbox, escalation, on-call routing — and the human-factors evidence on which of these are
answered promptly versus ignored. Our failure is **alarm absence**, not alarm fatigue: the signal
exists and no surface shows it. Say what changes when two agents ask at once.

### 4.7 Repo integration from the interface

Opening, reading and editing the files an agent is touching, showing diffs, staging and committing,
and driving worktrees — from inside the tool. What are the real options (LSP, tree-sitter, embedded
editors like Monaco/CodeMirror, libgit2/isomorphic-git, delegating to VS Code)? Where is the line
past which we are rebuilding an IDE badly?

### 4.8 Migration, because we are not starting clean

**Four interfaces already exist** and a fifth is dead. Whatever you recommend, sequence the
migration: what is the smallest change with the largest effect, what runs in parallel with what
exists, what must be retired, and **what must not be built yet**.

## 5. Deliverable shape

1. **Executive answer** — the single architecture you would commit to, and the first change to make.
2. Orchestration architectures compared, then a recommendation for a 3-lane conflict graph.
3. The desktop/local-tool decision, argued, with the runner-up and why it lost.
4. The performance architecture, with a latency budget in milliseconds.
5. The approval surface, including the non-engineer question.
6. Provenance and the config hash — what to adopt, what to skip.
7. The question-to-human channel.
8. Repo integration, and where the IDE line is.
9. A sequenced migration from four existing surfaces.
10. **What you would refuse to build, and why.**

## 6. Constraints — a recommendation that breaks one of these is not usable

- **Windows-first** on the operator's machine. WSL is available; say exactly what changes.
- **Small team.** Anything needing a platform team to operate is wrong regardless of merit.
- **Three concurrent lanes today.** A design assuming ten agents answers a question we do not have.
- **Per-secret human approval is a hard rule.** No batch-approval of credentials, ever, however
  elegant. Batch-approving *file reads* is a separate question and is open.
- **No unlabelled stale numbers.** A cached figure must carry its age in the same string as the
  figure, or not be shown.
- **The existing instrument panel is added to, never removed.**
- **Evidence-gated deploys are a hard rule**: prove the target object, validate at the layer the
  consumer reads, prove no regression, capture a rollback, then deploy.

### ⚠ The one constraint that is genuinely open — do not answer it by accident

We have had a standing rule that **no terminal is embedded in a page**. It has never been tested.
One pass restated our position back to us instead of challenging it; a second was never told the
rule existed and recommended adopting an Electron app built entirely around embedded terminals.

The operator's current position is that **terminal mode should exit** — that the terminal is an
escape hatch, not the interface. That points at retiring the rule, but it is not yet a decision.

**So treat it as an explicit question, not a background assumption:** *should a live terminal be
visible in this tool at all — never, as an escape hatch, or as the primary surface?* Argue it on
the merits. If your recommended architecture depends on the answer, give us both branches. **Do not
quietly assume either one.**

## 7. Tier every claim

`OBSERVED` — you read the source, the docs, or ran it · `REPORTED` — a credible postmortem, paper
or production write-up · `MARKETED` — the vendor says so and nobody independent has confirmed it ·
`INFERRED` — your reasoning from the above.

**A `MARKETED` claim may not be used as a design premise.** We have been burned specifically by
this: a gate that reported PASS while measuring nothing, a detector that silently degraded to
reporting 1 finding where the real engine reports 313, and a launcher that announced the model it
was running on while running a different one. **Assume any capability you cannot see the source or
documentation of is absent until proven otherwise.**
