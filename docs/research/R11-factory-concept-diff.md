# R11 — What do the other agent factories make first-class that we have no name for?

**Status: DISPATCHED 2026-08-23.** Written 2026-08-23. Paste the whole file. The answer is filed at
`docs/research/answers/R11-answer-factory-concept-diff.md`.

Read `docs/research/agent-factory-concept-inventory.md` first — it is the frozen baseline this
prompt exists to diff against, written deliberately **before** any external product was looked at.

⚠ **Standing rule in this estate: an object named by a handoff is a hypothesis, not a finding.**
Every figure in §1 was measured from code or from filed answers on 2026-08-22/23 and cites where.
Apply the same suspicion to every vendor claim you meet — read the source or the docs, not the
launch post, and tier everything (§7).


## Run log

| Run | Dispatched | Outcome |
|---|---|---|
| 1 | 2026-08-23 | Answer filed 2026-08-23. |

> Kept because `factory.dispatch` reads a status line and the presence of an answer file, and by its own account cannot see whether a prompt was ever actually pasted anywhere. Without this table "which did I send, and when?" is not answerable from disk. **Add a row every time this prompt is dispatched.**

---

## 0. The question, and what it is not

We have built an agent factory. Ten research passes have graded its *design decisions*, and seven
have come back. **None of them has looked at what other people's factories actually ship as
concepts.** R1–R7 are literature- and practice-driven; they answered "is this defensible" and "what
does the evidence say", never "what object does Google's ADK make first-class that we do not have a
word for".

So this is a **vocabulary and concept diff**, not an architecture review.

**It is emphatically NOT:**
- a request to re-open team topology, the optimiser, the eval harness, or the control plane — §2
  lists what is settled and what it cost to settle;
- a "you should adopt framework X" recommendation. We are not migrating. R1 already concluded
  *"adding another eval framework today would not materially improve your assurance"* and R2's
  deferral list makes framework migration conditional on fault injection we have not run;
- a feature comparison table. A feature is not a concept. `--worktree` is a flag; *"the certified
  object includes the permissions it held"* is a concept.

**What we want back is a diff**, and §5 fixes its shape.

**You are explicitly permitted — encouraged — to conclude that we already have it.** An answer that
returns "of the 30 concepts I found, 24 are PRESENT under your names, 4 are on your own deferral
list, 2 are genuinely ABSENT" is a *better* result than one that invents gaps. The failure mode we
are guarding against is a generic agent-framework listicle.

---

## 1. What we have, measured

Enumerated from the modules on 2026-08-22, full table in the concept inventory.

| | Measured |
|---|---|
| Concepts enumerated from code | **26**, each citing its module |
| Readiness gates registered in `readiness.GATES` | **30** (certification 8, judgement 8, handover 7, bounded 4, loop 3) |
| Test modules | **16** |
| Research passes filed | **R1–R7**, ~370 KB of answers |
| Passes written but not yet sent | R8, R9, R10 — and this one |
| Live certification state | `connector-e2e/windsorai@CLIENT-A: UNMEASURABLE (PASS=11, UNMEASURABLE=1)` — A12 blocked on undeclared tenant scope |

The load-bearing ones, in our vocabulary:

- **GreenContract** — a named set of falsifiable assertions; the root success object.
- **Four verdicts, never collapsed** — `PASS` / `FAIL` / `UNMEASURABLE` / `NOT_RUN`. `UNMEASURABLE`
  is raised by a probe as an exception, so a dark instrument cannot read as healthy.
- **The negative control** — `mutate_and_expect_failure` breaks the world and asserts the contract
  stops being green. Gated by `test_eval_can_fail.py`. An eval nobody has proved can fail is
  decoration.
- **The config IS the version** — an agent is a (prompt, model, effort, tools, retry, turns, budget)
  tuple; change one element and its certification does not transfer.
- **Evaluator as a principal** — an external service with its own identity, three fields in, verdict
  out, write-once verdict store. The client cannot name the corpus it is scored against.
- **Append-only, evidence-gated task ledger** — current state is a fold over events; a task cannot
  close without evidence attached.
- **Activity metrics cannot exist alone** — registering one without a paired outcome metric raises
  `GoodhartViolation`.
- **Parallelism bound by file locality, not the dependency graph**, with one git worktree per lane
  and a claim lock that refuses conflicting lanes.

Two facts about the *gaps* that shape what is worth asking:

1. `deploy.py` streams a transcript to a file. **There is no structured trajectory object** — no
   span, no typed event stream, nothing another tool could read.
2. `blueprint.py` holds `TeamSpec` and `AgentSpec` with a version hash over composition, and
   **nothing executes them.** `grep` finds one caller: a test.

---

## 2. Settled — do not re-answer these

Seven passes bought these. Re-deriving them wastes the run, and an answer that contradicts them
without new evidence will be discarded.

| Settled | By | Verdict |
|---|---|---|
| Team topology | R2 | **Do not build the three-agent team.** One worker + non-LLM verifier + human for privileged ops. 180 configurations across 5 architectures: multi-agent averaged **−3.5%**; sequential tasks degraded **39–70%** |
| Eval framework | R1 | **Keep GreenContract as the authoritative domain verifier.** Do not replace it. Inspect AI is the only candidate worth adding later, as a *runner shell*, not a replacement |
| Optimiser timing | R3, R4 | **Not yet.** Bounded, reapable, fail-closed and independently evaluable first. Build repo-agnostic *interfaces* now; run no search |
| Trust boundary | R3 | Tamper-evidence is not a trust boundary. An external evaluator **service with its own identity** is; a separate local process is *"mostly theatre"* |
| Parallel isolation | R5, R6 | One branch/worktree per agent. Across ~33,000 agent-generated PRs, cross-agent PRs conflicted **41.7%** of the time, mostly structurally |
| Bounded autonomy | R7 | Five auto-actions, each refuse-by-default with explicit preconditions and a logged decision |
| Build order | R3, R5 | Nine steps, hard budget/concurrency caps first, **configuration search last** |

**The never-optimise list** — retry caps, gate thresholds, tenancy checks, timeout and concurrency
limits, evaluator thresholds, the corpus. These are *safety specification, not hyperparameters*.
R7 proposed readiness gates as a cheap fitness proxy and was **rejected** for exactly this reason:
optimising the candidate's own score changes the ruler rather than the system.

**The deferral list, with unlock thresholds already written down** — separate architect LLM,
mandatory tester LLM, `agent ↔ agent` messaging, `manager ↔ manager`, army tiers, dynamic
team-selection LLM, ten team types, the agentic gym, framework migration, supervisor tiers.

> ⭐ **This is the single most important instruction in this prompt.** Each of those ten has a
> stated unlock condition. If you find a concept that maps onto one of them, the verdict is
> `DEFERRED` and the useful contribution is **evidence that meets or moves the unlock threshold** —
> not a recommendation to build it. Reporting them as gaps is the predictable way to get this
> answer wrong ten times over.

**Owned by sibling passes, out of scope here:** data-engineering team architecture, sandboxes and
data-layer blast radius including zero-copy clones, shadow schemas and transactional rollback
(**R8**); the operator-facing supervision UI (**R9**); post-run learning, self-extending knowledge
bases and whether that loop compounds or corrupts (**R10**). Do not answer those.

---

## 3. The questions

Five axes. They were chosen because no filed pass has looked at any of them.

### 3.1 Concept enumeration from named factories — the core of this pass

Go through these and report **what each makes a first-class object**, in its own vocabulary, with a
citation:

- Anthropic — Claude Agent SDK, subagents, Skills, Agent Teams, Managed Agents
- OpenAI — Agents SDK, AgentKit, Evals
- Google — Agent Development Kit (ADK), Vertex Agent Engine, A2A
- Microsoft — Agent Framework (AutoGen/Semantic Kernel lineage), Foundry Agent Service
- LangChain — LangGraph, LangGraph Platform, LangSmith
- CrewAI, and any other framework with a genuinely distinct object model
- Product companies whose factory *is* the product — Factory.ai, Cognition, Sierra, Cursor's
  background agents

**Questions.** Which nouns recur across three or more of them that we have no word for? Which of
our 26 concepts has no counterpart anywhere — and is that because we are ahead, or because the
concept is load-bearing only in our peculiar situation? Where the same idea has different names
across vendors, what is the industry's settling vocabulary? Is there any convergent object model
emerging, or is every vendor's abstraction still bespoke?

⚠ Be specific about **what is actually shipped versus announced**. A concept in a keynote is not a
first-class object.

### 3.2 Observability and trace standards

R1 was scoped to *eval frameworks* and concluded not to add one. That verdict says nothing about
**tracing**, and we have none: `deploy.py` writes a transcript file and that is all.

**Questions.** What is the actual state of OpenTelemetry's GenAI semantic conventions — stable,
adopted, by whom? What do trace stores (Langfuse, LangSmith, W&B Weave, Braintrust, Arize) make
first-class that a transcript file does not? Is there a standard shape for an **agent trajectory** —
a typed, replayable event stream — and would emitting one be an *ingredient* of certification or
merely useful for debugging? Concretely: should a certified run emit a standard-shaped trace, and
what would that buy the evaluator that the current artefact+hash submission does not?

⚠ Watch the trap: R3 established that recorded evidence describes the old configuration's output,
and replay scores *the evaluator*, not an unrun candidate. Do not present tracing as a route to
cheap configuration search.

### 3.3 Task and environment packaging

**Questions.** Is there a portable standard for "a task an agent can be given and scored on" —
METR's task standard, Inspect's task format, the `verifiers` / environment-hub packaging, SWE-Gym,
anything else? What does packaging a task that way make possible that our corpus-plus-contract does
not? Our corpus is hash-pinned JSON documents plus a code contract; is that a local dialect of a
standard we should be speaking, or genuinely different in kind?

**Fence:** this is about *packaging and portability*, not about adopting an eval framework. R1
settled that. If the answer is "the standard exists but adopting it means replacing GreenContract",
the answer is no — tell us what could be adopted *underneath* it instead.

### 3.4 Interop as an interface standard, not a messaging topology

R2 deferred `agent ↔ agent` messaging on evidence, and that deferral stands. **This is a different
question.** MCP is used across this estate as a tool interface but is not a factory *concept* here;
A2A, AGNTCY and similar are usually discussed as inter-agent chat, which we have declined.

**Questions.** Setting topology entirely aside: is there value in an agent, a tool, or a verifier
being addressable through a *standard interface* rather than a bespoke one — for substitutability,
for testing a component in isolation, for letting an evaluator talk to an agent it did not build?
What is actually standardised today at that layer versus merely proposed? Does agent **identity**
have any emerging standard — an agent as a principal with credentials and scoped permissions, which
R2 already flagged as a missing version dimension (*"an agent with prod credentials is not the same
certified object as one without them"*)?

### 3.5 The human approval workflow — mechanics, not the terminus

R7 gave us the *policy* layer: five auto-actions, refuse-by-default. R9 asks what the operator
*sees*. Neither asks what the approval **mechanism** is, and `operator.py` only handles blockers
declared *before* a session starts.

**Questions.** In systems that genuinely run agents unattended, what is the shape of the mid-run
approval surface? Specifically: how is a pending approval represented so it survives a restart; what
happens on timeout — does the run block, fail, or take a safe default, and which is right; how is an
approval bound to the exact artefact it approved, so it cannot be replayed against a later one; is
there prior art for **batching** approvals without turning them into rubber-stamps; and how do
systems avoid approval fatigue without quietly widening what runs unapproved?

**Constraint that cannot be traded away:** per-secret human approval is a hard rule in this estate.
Any design where an agent obtains a credential without a human in the loop is out of scope, not a
trade-off to be argued.

---

## 4. Constraints any recommendation must respect

1. **We are not migrating frameworks.** Recommendations must be adoptable *underneath or beside*
   what exists, or be explicitly labelled as requiring a migration we have not justified.
2. **One worker agent, non-LLM verifier, human for privileged operations.** R2 settled this on
   evidence. A recommendation whose value depends on a multi-agent topology is out of scope.
3. **The evaluator must remain a principal the graded party cannot impersonate.** Nothing may give
   an agent a route to name its own corpus or write its own verdict.
4. **Windows-first, local-first.** The estate runs on a Windows workstation with git worktrees and
   Windows Terminal. A recommendation that assumes a Linux CI cluster must say so.
5. **No in-page terminals.** Declined three times. R7 was asked to challenge this and instead
   restated it, so it stands *unchallenged rather than tested* — if you have a real argument, make
   it; otherwise treat it as fixed.
6. **Cost is not free but is not the binding constraint.** Do not optimise recommendations for token
   spend; optimise for whether a claim can be checked.

---

## 5. Deliverable shape — a diff, and it is not optional

Every concept you report gets **exactly one verdict**, and they are never collapsed:

| Verdict | Means |
|---|---|
| `PRESENT` | We have it, under our own name — give the mapping |
| `RENAMED` | We have it under a different name — give both names; the vocabulary gap is the finding |
| `DEFERRED` | It is on our deferral list — cite the unlock threshold and say whether your evidence moves it |
| `ABSENT` | Genuinely not present and not deferred — **this is the payload** |
| `NOT-SEARCHABLE` | You could not establish it either way — say what you could not see, and why |

For every `ABSENT`, we need four things or it is not actionable:

1. **What it is**, in one paragraph, in the vendor's own vocabulary and then in ours.
2. **Who ships it**, with a citation, and at what tier (§7).
3. **What it catches that we currently cannot** — a concrete failure that would get through our
   30 gates today and would not get through with this concept in place.
4. **What it costs**, including what it would make harder.

Rank the `ABSENT` list by (3), not by how novel it is.

Close with the honest count: how many concepts examined, how many in each verdict, and **what you
looked for and could not find** — a `NOT-SEARCHABLE` list is a real result and we would rather have
it than a confident silence.

---

## 6. Explicitly out of scope

Model choice, prompt-engineering technique, and anything about chain-of-thought. Also: the five
sibling-owned areas in §2, and any recommendation to adopt a framework wholesale.

---

## 7. Tier every claim you make

| Tier | Means |
|---|---|
| `OBSERVED` | You read the source, the API reference, or ran it |
| `DOCUMENTED` | Official docs or release notes say so |
| `MARKETED` | A vendor blog, launch post, or comparison page — the vendor wins its own comparison |
| `INFERRED` | Your reasoning by analogy — say so |

A vendor claim is **not a design premise**. This estate has a standing rule that an object named by
a handoff is a hypothesis until walked, and it applies to your sources too.

One worked example of why: two independent 2026 comparisons of agent sandbox cold-start disagree by
up to **113×** on the same four products, because they are silently measuring different events —
cold create versus resume-from-warm-pool. Either number quoted alone would be wrong. If two sources
disagree, that disagreement is the finding; report it rather than picking one.
