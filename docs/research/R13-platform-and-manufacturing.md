# R13 — The manufacturing step, the platform, and the UI that has to make delivery move

**Status: READY TO DISPATCH.** Written 2026-08-23. File the answer at
`docs/research/answers/R13-answer-platform-and-manufacturing.md` and nowhere else.

**§0 settled 2026-08-23: the in-page terminal is put to the pass as an open question**, on the
explicit record that two prior attempts failed on it. R7 restated our own position back to us; R12
was never told the constraint existed. This time it is neither asserted nor omitted — it is asked,
with both prior failures named so the pass cannot repeat either.

## How to run this

**Paste everything inside the fence. Nothing outside it needs to go with it.**

⚠ **This repo is private.** A research tool cannot fetch `agent-factory`, `prefect-connectors`,
`clients`, `core_api`, `eclipse` or the wiki — not by URL, not by search. So the fence carries every
figure inline rather than citing a path. **If a returned answer quotes one of our file paths as
though it read it, it did not — treat that answer as contaminated.**
`docs/specs/agent-factory-technical-and-business-spec.md` may be attached as a supplementary file,
but the fence must stand alone without it.

---

## §0 — The in-page terminal, and why it is asked rather than asserted

**Decision, 2026-08-23: put it to the pass as an open question.** The fence carries it as `E8`.

This is the third time this question has been in front of a researcher and the first time it has
been *asked*. R7 restated our own position instead of challenging it, so we learned nothing. R12 was
never given the constraint at all and duly recommended adopting an Electron app whose entire model
is an embedded terminal per session — **an answer cannot respect a rule it was not given**, so its
"adopt" is not a refutation of R7, it is an answer to a different question.

⚠ **Both failure modes are now named inside the fence**, which is the point: a pass told only
*"we do not embed terminals"* returns our own position with citations, and a pass told nothing
returns a terminal grid. Asking it explicitly, with both prior failures on the record, is the only
form that can come back gradeable.

⭐ **The consequence of leaving it open is that E8 gates E1 and E7.** Nothing downstream about UI
substrate is decidable until it is answered, so grade E8 first when the answer lands — and if the
pass ducks it or hands our position back a third time, that section is void and the rest of the UI
answer is read with it discounted.

Paul's own position on 2026-08-23 was *"terminal mode needs to exit"*. It is **deliberately not
stated in the fence**, so the answer is evidence rather than an echo.

---

```
You are advising a small data-and-analytics consultancy that has built an "agent factory" — a
system for producing agent teams whose output is CERTIFIED rather than believed. We have run
twelve prior research passes. This one asks three linked questions that none of them covered.

Everything below was measured by us on 2026-08-22/23 and carries a basis marker:
  [M] measured, instrument named   [D] derived from something measured
  [R] reported, inherited, not re-verified   [A] assumed, no measurement

Apply the same suspicion to every source you meet. Read the code or the documentation, never the
launch post, and tier every claim you return:
  OBSERVED  — you read the source or ran it
  DOCUMENTED — it is in official docs but you did not verify it
  MARKETED  — it is a vendor claim on a landing page
A claim with no citation is a rumour and we will discard it.

====================================================================
PART A — WHO WE ARE AND WHAT THE PRODUCT IS
====================================================================

We deliver the same unit of work repeatedly: pull vendor data through a connector, land it in
Snowflake, model it into a star schema, surface it in Power BI or a bespoke Next.js app. Measured
surface: 24 client directories, 139 connection configs, 739 extraction templates, 186 warehouse
SQL views, 104 reporting views. [M] Our control-plane API is 30,460 lines of Python across 21
routers; our portal UI is 22,715 lines of TypeScript across 18 API domains. [M]

THE FOUNDING FAILURE, and it decides everything:

This estate twice built mechanisms that ACTED without anything measuring whether the action
helped. One agent produced 233 diagnoses, 234 escalations and ZERO fixes over 81 days. [R] A
separate loop ran 965 times, recorded its own 1.6% success rate, and never adjusted. [R] Both were
capable. Neither was measurable.

The consequence is precise: a dashboard over the first mechanism would have shown 234 escalations
climbing steadily, and a self-improving loop pointed at that number would have optimised for
ESCALATING FASTER and called it progress. An activity metric with no outcome metric is not a weak
metric, it is an inverted one. Our code therefore RAISES an exception when an activity metric is
registered without a paired outcome metric, rather than warning.

THE PRODUCT THESIS, in one sentence from our README:

  "A team of agents did the work, and we can prove it — or we can prove we could not tell."

That is an EVIDENCE product, not a PROCESS product. Every session manager and agent platform we
have looked at manages processes. None of them answers: who did this work, under what
configuration, and what proves it was correct. We believe that is the only axis where we are not
starting from behind. Tell us if we are wrong about that — with citations.

====================================================================
PART B — WHAT WE HAVE BUILT (so you return a DIFF, not a survey)
====================================================================

29 Python modules, 5,180 LOC; 16 test modules; 30 readiness gates; 26 named concepts enumerated
from code. [M] The load-bearing ones:

1. GreenContract — a named set of falsifiable assertions; the root success object.
2. FOUR VERDICTS, NEVER COLLAPSED — PASS / FAIL / UNMEASURABLE / NOT_RUN. UNMEASURABLE is raised
   by a probe as an EXCEPTION, so a dark instrument cannot read as healthy. It is explicitly not
   a pass. Collapsing "I could not look" into "I looked and it was fine" is how a measurement that
   never happened passes for one that did.
3. THE NEGATIVE CONTROL — a harness that deliberately breaks the world and asserts the contract
   notices. A test fails the suite if any assertion has never been observed failing. An eval nobody
   has proved can fail is decoration.
4. THE CONFIG IS THE VERSION — an agent is a (prompt, model, effort, tools, retry, turns, budget)
   tuple; change one element and its certification does not transfer.
5. EVALUATOR AS A PRINCIPAL — a separate service; three fields in (artifact_uri, artifact_sha256,
   run_id), verdict out. The client cannot name the corpus it is scored against; the service
   resolves that from its own config. Write-once verdict store.
6. APPEND-ONLY, EVIDENCE-GATED WORK LEDGER — state is a fold over events; a task cannot close as
   done without at least one MEASURED or DERIVED piece of evidence attached. Enforced by the store,
   not by convention.
7. PARALLELISM BOUND BY FILE LOCALITY, not the dependency graph — one git worktree per lane, with
   claims that refuse overlapping lanes.
8. READINESS AS 30 MEASURED GATES — each measures from a named file AT RUN TIME and reports the
   path it measured from.

Three things we believe nobody ships, and want you to confirm or refute:
  (a) a verdict that can say "I could not tell" — every dashboard we have seen is two-valued;
  (b) provenance to a config hash: this artefact was produced by THIS agent, on THIS model, with
      THIS prompt, under THIS contract version. Our hash exists and covers 0 of 15 dimensions [M],
      so this is a gap with a name, not a feature;
  (c) cost paired with an outcome, ENFORCED rather than recommended.

====================================================================
PART C — THE ARCHITECTURE, AND THE CLAIM MOST LIKELY TO BE WRONG
====================================================================

Four planes with a hard boundary between them:

  APPROVE   humans only: merge, per-secret grant, promote to prod  <- never automated
  PROVE     readiness gates, contracts, findings ledger, run audits
  RUN       the isolation ladder (below)
  DECIDE    conflict graph, claims, scheduling, caps, budgets

The boundary that matters is RUN/PROVE: the thing being measured must not be the thing doing the
measuring.

THE ISOLATION LADDER is our genuinely novel claim, and the thing to attack first:

  An agent's isolation tier is chosen by WHAT ITS TASK TOUCHES, declared up front, and enforced —
  not by what kind of agent it is.

  T0  git worktree on the operator machine (BUILT). Repo files only. No network egress, no DB
      verbs. For code, docs, tests.
  T1  container, egress allowlist, read-only warehouse role. Repo + SELECT on real data. For
      analysis and reconciliation.
  T2  container + EPHEMERAL ZERO-COPY CLONE SCHEMA, dropped on exit. Full DDL/DML inside the clone
      only. For building views, migrations, backfills.

The argument: "do not touch prod" in a prompt is a REQUEST; a role with no grant on prod is a
CONTROL. We think this is what generic agent frameworks miss — isolating a filesystem does nothing
when the risk is DDL on a shared warehouse.

Where we think it is most likely wrong, and want you to check:
  - A zero-copy clone is cheap to CREATE; the compute to VALIDATE against it is not, and a clone
    of a SHARE may not behave like the real thing. If T2 is not actually cheap, the argument
    collapses. [A]
  - "Data work does not conflict" is asserted, not measured. [A] Two agents building two views can
    collide on a shared dimension table, a naming convention, or the same reporting object. The
    conflict graph may need DIFFERENT EDGES, not fewer.
  - T1/T2 assume containers on Windows via WSL. Unmeasured; start-up cost is a guess. [A]

====================================================================
PART D — QUESTION 1: THE MANUFACTURING STEP DOES NOT EXIST
====================================================================

This is the primary question. Our goal is to COMPOSE AGENT TEAMS FROM A PLATFORM AND DEPLOY THEM
INTO REPOSITORIES. Today the factory's output is a SESSION, not a SPEC. An agent is currently a
prompt string, a model and a gate list — that is launcher input, not a manufactured artefact.

The object we think we need:

  AgentSpec:
    id: navira-view-builder
    version: 7                              # bumped on ANY field below — that is the point
    prompt_ref: prompts/view-builder@a3f9c1 # content-addressed, never inline
    model / effort / tools
    tier: T2                                # chooses the sandbox — Part C
    budget: {tokens, wall_clock, warehouse_credits}
    contract: green@v5                      # which assertions certify it
    gates: [...]
    needs_human: [credential-grant, merge, promote]

Our gap list for "create a team and deploy it to a repo", measured:
  1. AgentSpec as a versioned artefact              ABSENT
  2. Version hash covering all 15 dimensions        0 of 15 [M]
  3. Content-addressed prompts                      ABSENT
  4. Tier declared and ENFORCED, refusal audited    ABSENT
  5. Bounded deployment into a repo                 BUILT (worktree + turn cap + spend cap +
                                                    an attempt ledger PERSISTED TO DISK so the cap
                                                    survives a restart)
  6. Per-repo contract to certify against           BUILT for connectors, not generalised
  7. Cross-repo targeting                           ABSENT — every path resolves from cwd
  8. A registry of certified specs to deploy FROM   ABSENT

A hard-won lesson that shapes this: A SPEC FIELD THAT NOTHING READS IS WORSE THAN NO FIELD. In one
month we produced a --model flag built into a dead variable, so every agent ANNOUNCED A MODEL IT
WAS NOT RUNNING ON; a code detector that silently degraded to 1 finding instead of 313; and gates
reporting PASS while measuring nothing.

ASK:
D1. Who has actually built agent-team manufacturing — a versioned, content-addressed agent/team
    spec that is composed in one place and deployed into repositories? Look at real
    implementations, not launch posts: Claude Agent SDK subagent definitions, OpenAI AgentKit,
    Google ADK + Agent Engine, Microsoft Agent Framework + Foundry, LangGraph Platform, CrewAI,
    Factory.ai, Cognition, Sierra, and anything on GitHub with real adoption. For each: what is the
    UNIT that gets versioned and deployed, and what is its identity derived from?
D2. What is the state of the art on VERSIONING an agent so a certification does not silently
    transfer? Which dimensions do real systems include in identity, and which do they miss? We
    believe there are ~15; tell us what we have wrong.
D3. Content-addressed prompts: who does this, what does it cost operationally, and what breaks?
D4. What is the right shape for a REGISTRY of certified specs — the thing a platform deploys from?
    Is there prior art beyond container-registry analogies?
D5. Cross-repo deployment: how do real systems target N repositories without every path resolving
    from the operator's working directory? What did they learn the hard way?

====================================================================
PART E — QUESTION 2: THE UI, AND WHAT IT IS ACTUALLY FOR
====================================================================

Paul's ask is "a complete overhaul optimising for speed and ease of monitoring". We think the
naive reading of that is a trap, and want you to tell us whether we are right.

WHAT WE MEASURED, and it reframes the question:

  runs finishing with no human                    3 of 14   [M]
  gate events that were ever a REFUSAL            0 of 22   [M]
  green PRs waiting on a human to press merge     2, for 6 and 9 DAYS  [M]
  agents blocked on a plain-English question
    written in a file nothing read                4         [M]
  concurrent lanes supported                      3         [D] max independent set of the
                                                            file-conflict graph
  page load on our existing tracker               10-19 s, and two concurrent requests
                                                  return empty (single-threaded)  [M]

Two green PRs waited NINE DAYS for a click. No amount of agent improvement touches that number.

Each of our four planes implies a different user, and only one is for a non-engineer:

  DECIDE   operator  — what can start, what conflicts, what it costs   partly built
  RUN      nobody, ideally — only the exceptions: stalled, orphaned,
           over-budget                                                 partly built
  PROVE    reviewer  — the verdict AND what it was measured with       partly built
  APPROVE  anyone, incl. a non-engineer — what was delivered, what
           proves it, approve or reject                                NOTHING EXISTS

So: the "normal user" surface and the measured delivery bottleneck are THE SAME SURFACE.

A refusal rate of exactly zero is not a clean bill of health — it is indistinguishable from a gate
that cannot refuse. Absence of alarms and absence of alarm CAPABILITY look identical from outside.

WHAT ALREADY EXISTS — four live surfaces and a fifth that DIED. Any new UI is the sixth thing built
to look at this work. The dead one is the cautionary case: a monorepo founded as a delivery
PLATFORM whose platform half stopped moving after four months while the operations half carried
every ticket. "Build a new platform UI" has been tried here and it died. Factor that in.

WHAT OUR EXISTING TRACKER DOES that a session manager does not, so you do not recommend rebuilding
it: every number RE-MEASURES ON REFRESH — there is no cache, because a page that can quietly show
yesterday's state is the exact drift this project exists to remove. Verdicts are four-valued. The
task board is GENERATED from the gates, so it cannot drift from what is measured. Its ranking
function states in writing which part is judgement, because a bare ranking is an oracle.

THE TWO REQUIREMENTS AS BUDGETS:
  Speed — currently 10-19 s per page. The interesting question is NOT "how do we cache this" but
    "how does a page stay HONEST and fast at the same time", because re-measuring on refresh is a
    CORRECTNESS property, not a performance compromise. If a figure must be cached, it carries its
    age in the same string.
  Monitoring — our measured failure is ALARM ABSENCE, not alarm fatigue. The signal existed and was
    never surfaced. Whatever surfaces a blocked agent's question must INTERRUPT, not badge.

ONE CONSTRAINT WE ARE DELIBERATELY NOT GIVING YOU — see E8. Every other constraint in Part H is
binding; the in-page terminal is the one we want argued rather than obeyed.

ASK:
E1. Given that this is an EVIDENCE product, what is the right PRIMARY OBJECT of the UI: the
    session, the lane, the artefact, or the decision? Argue it; do not list options.
E2. What does the state of the art do for the APPROVE plane — review-and-merge queues where the
    work was done by an agent? WHO HAS SHIPPED THIS, and what did they learn? This is the single
    most valuable thing you can return.
E3. What is the evidence on surfacing an agent's blocking question to a human so it is answered in
    MINUTES rather than DAYS? Interrupt, queue, inbox, push? Our measured latency is days.
E4. What would a NON-ENGINEER need in order to approve agent-produced work safely, and what has
    actually been tried? Include failures.
E5. How do teams present PROVENANCE and COST-PER-OUTCOME without it becoming a vanity dashboard?
E6. How do the fastest agent-observability UIs stay honest and fast simultaneously — what is the
    real architecture behind sub-second pages over live state, and what do they give up?
E7. Given four surfaces exist and a fifth died: WHAT SHOULD WE REFUSE TO BUILD?
E8. THE ONE WE KEEP FAILING TO GET ANSWERED — and we want it argued, not agreed with. Should a
    live terminal be embedded in the supervision UI at all, or is a terminal an ESCAPE HATCH you
    leave the page to reach?

    Read this part carefully, because two prior passes broke on it in opposite directions. One was
    handed our position and returned it to us with citations, which taught us nothing. The other
    was never told the question existed and recommended an Electron app whose entire model is an
    embedded terminal per session. WE ARE THEREFORE NOT TELLING YOU WHAT WE THINK. Take a side and
    defend it.

    What we can tell you is what we measured, and it cuts both ways:
      - a terminal DIED and its agent kept working, invisibly, for minutes. Alive, visible and
        attachable turned out to be three different properties and nothing distinguished them;
      - four agents sat blocked on questions written in plain English in a file nothing read, for
        days. A terminal would have shown those questions to anyone watching — and nobody was;
      - our operators DO drop to a terminal, routinely, and the work is fundamentally
        text-and-git-shaped;
      - the one substrate we evaluated has NO ATTACH: it re-uses only PTYs it spawned itself, and
        spawns a SECOND process against a live session id it did not launch. That is precisely the
        incident above, reproduced by design.

    Specifically: (a) in shipped supervision UIs for long-running agents, is a terminal a
    first-class pane, an escape hatch, or absent — with citations to real products, not launch
    posts; (b) what does an embedded terminal buy that a status list plus the transcript does not;
    (c) what does embedding one COST in practice — attach semantics, duplicate processes, state
    divergence, security surface; (d) if terminals are an escape hatch, what carries the load in
    the primary UI instead; (e) what evidence would settle this, that we could gather ourselves in
    under a week?

====================================================================
PART F — QUESTION 3: FOUR ABSENCES WE HAVE NAMED BUT NOT DESIGNED
====================================================================

Not deferred, not renamed. Nothing here has a stated unlock condition, which is itself the finding.

F1. GUARDRAILS AS A PRE-ACTION LAYER. Our gates evaluate FINISHED OUTPUT; a guardrail blocks a bad
    action BEFORE it happens. Worked example we already shipped: a function sent a workflow engine
    a CANCELLING signal BEFORE the ownership check ran — so the refusal protected the container and
    never protected the run. A post-hoc gate cannot catch that class. What is the real state of the
    art, and what does it cost?
F2. STRUCTURED TRACES. We derive tokens, cache traffic, model and wall-clock from a raw transcript,
    so telemetry is not wholly absent — but there is NO STRUCTURED TRAJECTORY OBJECT: no span, no
    typed event stream, nothing another tool could read. Should a certified run emit a
    standard-shaped trajectory (OpenTelemetry GenAI semantic conventions, or otherwise)? What is
    actually stable versus still churning?
F3. TASK AND ENVIRONMENT PACKAGING as one reproducible unit (task + environment + scoring). METR's
    task standard, Inspect's task format, verifiers-style environment packaging. Which is real,
    which is adopted, and would adopting one make our corpus portable?
F4. COMPENSATING ACTIONS. GIT REVERT DOES NOT UNDO A DROPPED TABLE. Our isolation ladder implies
    rollback semantics for data work and nobody has designed them. What is the actual practice —
    not the theory — for compensating a partially-applied warehouse change made by an autonomous
    agent?

====================================================================
PART G — DO NOT RE-ASK. Twelve passes, ~370 KB of answers already filed.
====================================================================

Re-asking these buys the same answer at full price. A pass that "discovers" one of these has
produced nothing. You may CONTRADICT any of them WITH NEW EVIDENCE — that is valuable. You may not
restate them as findings.

  R1  Eval harness. Keep our contract as the authoritative verifier; do NOT add a general LLM-eval
      framework. The weak parts are control-plane, not eval sophistication.
  R2  Topology. DO NOT build a three-agent architect->implementer->tester team. One end-to-end
      worker + a NON-LLM verifier holding the authoritative PASS bit + a human for privileged ops.
      Evidence: 180 configurations across 5 architectures and 4 benchmarks; multi-agent averaged
      -3.5%; SEQUENTIAL TASKS DEGRADED 39-70%, and our work is sequential shared-state work.
  R3  Control plane. Do not optimise yet — make it bounded, reapable, fail-closed and independently
      evaluable first. Tamper-evidence is not a trust boundary; an evaluator SERVICE is.
  R4  Agnostic optimiser. Not yet, but build repo-agnostic INTERFACES now: cheap now, expensive to
      retrofit.
  R5  Build velocity. Lean runner + sandbox + circuit-breakers is the gating step. Worktree per
      agent; 41.7% cross-agent conflict rate on a shared branch.
  R6  Automation. Branch per lane, merged one at a time.
  R7  Session managers. Inspiration, not adoption.
  R10 A hierarchical auto-updating wiki: NO. ~24% accuracy loss from 30k IRRELEVANT tokens even
      with the relevant content present; our wiki is ~1M tokens. The win is distilling procedures
      into INVOCABLE SKILLS, not growing a better corpus.
  R11 Concept diff against other factories. Seven absent concepts, every one costed as
      "significant engineering". None recommended now.
  R12 Session-manager substrate. Its own source-reading contradicted its summary: the tool it
      recommended HAS NO ATTACH and spawns a duplicate process against a live session id — which is
      exactly the incident that prompted the question.

FOUR INDEPENDENT PASSES CONVERGED WITHOUT BEING ASKED: "the weakest parts are control-plane
problems" / "control-plane changes are more urgent than agent architecture" / "this system should
not be optimised yet" / "the current experiment is not yet a reliable experiment". Treat as settled
unless you bring new MEASUREMENT.

NEVER OPTIMISE, and do not propose optimising: retry caps, gate thresholds, tenancy checks,
timeouts, evaluator thresholds, the corpus. These are SAFETY SPECIFICATION, not hyperparameters.
Optimising eventual success simply rewards more retries, and optimising on the candidate's own
score changes the ruler rather than the system.

DEFERRED WITH A STATED UNLOCK CONDITION — these are deliberate non-decisions, NOT gaps. Reporting
them as gaps is the single most likely way for this pass to waste itself:
  separate architect LLM; mandatory tester LLM; agent<->agent messaging; manager<->manager and
  army tiers; dynamic team-selection LLM; ten team types; an agentic gym ("training on current
  traces risks learning pathological loops"); framework migration; the optimiser itself.

====================================================================
PART H — CONSTRAINTS ANY RECOMMENDATION MUST RESPECT
====================================================================

Omitting one of these has already cost us two research passes.

  - WINDOWS-FIRST on the operator's machine. WSL exists; say what changes. This has already
    produced two platform-dependent instruments that were red everywhere else.
  - THREE CONCURRENT LANES today. A design assuming ten agents answers a question we do not have.
  - SMALL TEAM. Anything needing a platform team to operate is wrong regardless of merit.
  - PER-SECRET HUMAN APPROVAL IS A HARD RULE. No batch-approval of credentials, ever.
  - NO UNLABELLED STALE NUMBERS. A cached figure carries its age in the same string.
  - THE EXISTING INSTRUMENT PANEL IS NEVER REMOVED, only added to.
  - MERGING STAYS HUMAN.
  - In-page terminal: NOT a constraint — it is question E8. Argue it.

====================================================================
PART I — WHAT TO RETURN
====================================================================

A DIFF, not a survey. We would rather hear "of the 30 things I found, 24 you already have, 4 are on
your own deferral list, 2 are genuinely absent" than a list of invented gaps. THE FAILURE MODE WE
ARE GUARDING AGAINST IS A GENERIC AGENT-FRAMEWORK LISTICLE.

1. VERDICT TABLE. Every concept or practice you return gets exactly ONE verdict and a citation:
     PRESENT       we already have it, under our own name
     RENAMED       we have it under a different name — give the mapping
     DEFERRED      it is on our deferral list above, with an unlock condition
     ABSENT        genuinely missing and not deferred
     NOT-SEARCHED  no evidence exists either way — say so rather than guessing
2. DIRECT ANSWERS to D1-D5, E1-E8, F1-F4. ANSWER E8 EXPLICITLY AND TAKE A SIDE;
   a section that restates our constraints back to us is a failed section. Where the evidence is thin, SAY THE EVIDENCE IS THIN.
3. A RANKED BUILD ORDER for the manufacturing step and the UI, with what each unlocks and what it
   costs. Cost in engineering time, not adjectives — "significant engineering effort" is not a
   figure and a previous pass gave us nothing but that.
4. WHAT TO REFUSE TO BUILD, and why.
5. WHERE YOU DISAGREE WITH US. This is the most valuable section. Name the specific claim of ours
   you think is wrong and the evidence that makes you think so. An answer that validates everything
   we sketched is a wasted run.
6. YOUR OWN CONFIDENCE, per section, and what would change it.

You are explicitly permitted — encouraged — to conclude that we should BUILD LESS than we are
proposing. Three of our last three passes concluded exactly that, independently, and they were
right each time.
```

---

## Grading the answer when it lands

1. **Where an answer's own evidence contradicts its executive summary, the evidence wins.** That
   rule already caught R12: its summary said "adopt", its OBSERVED section said the tool has no
   attach and spawns duplicates.
2. **Any concept returned with no citation is discarded**, however plausible.
3. **Any answer quoting one of our file paths as though it read it is contaminated** — the repo is
   private and unreachable. Check for this first; it is the cheapest tell.
4. **Every `DEFERRED` item it reports as a gap** is a sign the deferral list was not read, and
   downgrades the whole pass.
5. ⭐ **Grade E8 first.** If the pass ducked the in-page-terminal question, hedged it, or handed our
   own position back a third time, that section is void — record it as void rather than reading a
   preference into it, and discount the rest of the UI answer accordingly. Three passes failing the
   same question would itself be the finding: it would mean the question is not answerable from the
   literature and we have to settle it with the week-long experiment E8(e) asks for.
5. File at `docs/research/answers/R13-answer-platform-and-manufacturing.md`, then fold into
   `SYNTHESIS.md` **before acting on it**, recording disagreements rather than smoothing them.
   `factory/synthesis.py` globs exactly one directory — an answer filed anywhere else can never
   appear in `unsynthesised()`, so the currency test can never go red for it.

## See also

`../specs/agent-factory-technical-and-business-spec.md` — the full baseline, attachable as a
supplementary file · `ui-surface-inventory.md` · `agent-factory-concept-inventory.md` ·
`SYNTHESIS.md`
