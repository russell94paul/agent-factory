# R2 — Multi-agent topology: what is actually proven

**Run after R1** — its answer changes what a team needs to be measurable. Paste everything inside
the fence. Save the answer as `docs/research/answers/R2-answer.md`.

**This is the load-bearing one for us.** We have a three-agent team specification written from
judgement, with no method behind it and no run history. R2 is the framework we do not have.

---

```
You are advising a small data-engineering company (about 4 engineers) building an internal "agent
factory" — LLM agents organised into teams that migrate and maintain data connectors along the path
vendor API -> Azure container -> Prefect 3 -> Snowflake -> BI/chat surfaces.

We need to know whether the team structure we have sketched is defensible, and what the evidence
actually says about multi-agent structure for this kind of work. We have no method behind our
current design and we would rather be told it is wrong now than discover it after building it.

=====================================================================
PART A — MEASURED CONTEXT
=====================================================================
[M] = measured from production event logs on 2026-08-21. [R] = from an earlier internal review,
not re-verified; weaker evidence.

We already run an 18-stage connector-migration pipeline. It is a real DAG with typed stages
(script / LLM-agent / gate), per-stage model selection, token budgets, turn caps, dependency
edges, and git-worktree isolation per agent stage. It works. Across its 14 recorded runs:

- [M] 1,001 stage_failed against 165 stage_completed — a stage attempt fails 6.1x more often than
      it succeeds.
- [M] 3 of 14 runs reached a terminal completion event. 4 more sit at "stage_started" with no
      terminal event — neither finished nor failed, just open.
- [M] 1,004 restarts, no attempt cap. Worst: 352 restarts of a single stage in one run. A
      documented incident from this: ten containers consumed an entire 10-core cloud region quota
      overnight and blocked every human operator.
- [M] 3 runs reported COMPLETED while carrying 115, 21 and 15 recorded stage failures.
- [M] 22 gate-approval events, ZERO refusals — 14 noted "auto-pilot: conditions met", 8 empty.
- [M] 5 of 7 gates across all pipeline templates have no programmatic check (gate_check = None).
- [M] One agent run spent $0.91 over 18 minutes across three LLM stages and produced no commit;
      the stage that would have saved the work failed with "No commits between main and pipeline
      branch — nothing to PR".
- [M] Exactly 1 connector of the fleet has a recorded successful end-to-end run (2026-08-20, after
      ten prior failed attempts).
- [R] 49 connector modules, 59% will not currently import.
- [R] A prior autonomous agent: 233 diagnoses, 234 escalations, ZERO fixes, over 81 days.
- [R] A separate loop ran 965 times, recorded its own 1.6% success rate, and never adjusted.

CRITICAL PATTERN: every failure above is a SEAM failure. Nobody owned "did the deploy finish?",
"who reads this output?", "is staging the same as production?". The work inside each stage was
mostly fine. The joins between stages were where it died.

=====================================================================
PART B — WHAT WE HAVE SKETCHED (grade this)
=====================================================================
One team, called orchestrator-team, working ON the pipeline repo itself. Two levels, one topology
(manager -> agent). Three members:

  architect    — turns a request into staged work with an evidence gate on every stage.
                 Model: a frontier reasoning model, high effort. 40 turns, $5 ceiling.
                 Prohibition: "Must not write implementation code. A planner that implements is
                 not planning."

  implementer  — makes the change in an isolated git worktree.
                 Model: a mid-tier model, medium effort. 60 turns, $8 ceiling.
                 Prohibition: "Must not mark its own work green. The tester holds the contract."

  tester       — runs the eval contract and reports the verdict, including UNMEASURABLE.
                 Model: mid-tier, high effort. 40 turns, $5 ceiling.
                 Prohibition: "Must not report PASS when an instrument could not run."

Team-level prohibition: must not deploy to production, must not modify the eval corpus, must not
raise its own attempt cap. Each is a human decision.

Versioning: an agent is defined as the tuple (prompt, model, effort, tools, retry policy, turn cap,
budget). The version id is a hash of that tuple, so a silent prompt change cannot inherit a
certification granted to a different configuration. A team version is a hash over its members'
versions plus the topology and contract name.

WHAT WE HAVE NOT DONE: this team has never been run. Nothing establishes that three is the right
number, that these are the right three roles, or that manager->agent is the right topology. It was
written from judgement. We are asking you for the method we skipped.

A larger brief we have deliberately NOT built proposes: a four-level hierarchy (Agent -> Team ->
Team Manager -> Army), five communication topologies (agent<->agent, manager->agent,
manager<->manager, army->managers, army<->army), a "team selection" agent that picks members per
task, ten team types, and a training environment ("agentic gym").

=====================================================================
PART C — THE QUESTIONS
=====================================================================
Separate ESTABLISHED PRACTICE from VENDOR CLAIM from OPEN RESEARCH throughout.

1. THE BASELINE, HONESTLY. For long-horizon software tasks with tool use and real side effects, is
   there credible evidence that multi-agent decomposition outperforms ONE strong agent with good
   tools and a long context? Cite results with numbers. Include the negative results — cases where
   decomposition measurably hurt, and the mechanism by which it hurt. If the honest answer is that
   a single agent is the better default at our scale, say so directly.

2. GRADE OUR THREE ROLES. Architect / implementer / tester, with those prohibitions. Is
   plan-implement-verify a structure with evidence behind it, or is it an intuition borrowed from
   human team design that does not transfer? Specifically:
   a. Is separating planning from implementation supported, or does the planner lose the context
      that makes the plan good?
   b. Is a separate tester agent better than the implementer running the same contract? What is
      the evidence that self-assessment is unreliable in this setting, versus assumed to be?
   c. Are per-agent "prohibitions" (explicit must-nots in the prompt) known to be effective at
      constraining behaviour, or are they decorative? Cite compliance measurements if any exist.

3. SEAM COST, QUANTIFIED. Every handoff loses context. Is there published work quantifying that
   loss for tool-using agents? Given that ALL of our measured failures were seam failures, what
   does that predict about a 3-agent team versus a 1-agent team, and about the four extra handoff
   types in the larger brief? Is there a principled way to decide how many seams a task can afford?

4. TOPOLOGY. Of the five communication patterns in the larger brief, which are supported by
   evidence and which are speculative? Is there ANY demonstrated case of army<->army (peer
   supervisor) communication in a production engineering setting, as opposed to a research
   benchmark or a demo?

5. ROUTING. On the "team selection" agent — what is the state of the art in automated agent/team
   selection, and how does it compare to a static routing table for a domain with fewer than ten
   task types? Be concrete about the crossover point at which dynamic selection starts to pay.

6. FRAMEWORKS. Assess LangGraph, CrewAI, AutoGen, OpenAI Swarm/Agents SDK, Claude Agent SDK,
   Temporal-based approaches, and any newer entrant, specifically on: durable execution across
   hours, human approval gates mid-run, per-run cost ceilings that survive a process restart, and
   running untrusted generated code in a sandbox. Which are production-grade for side-effecting
   infrastructure work versus demo-grade?
   IMPORTANT: our existing 18-stage pipeline already does DAG orchestration, budgets, per-stage
   models, gates and worktree isolation. Answer explicitly whether adopting a framework would
   REPLACE something that already functions. "Adopt nothing new" is an acceptable conclusion.

7. VERSIONING AND ATTRIBUTION. How do production systems version an agent configuration and tie a
   run's outcome back to the exact version that produced it? What schema do they use, what
   retention, and what breaks at scale? Is hashing the config tuple (our approach) what others do,
   and what does it fail to capture — e.g. model provider changes behind a stable model name?

8. THE HIERARCHY QUESTION. Given ZERO certified teams today, is there any evidence-backed reason
   to build supervisor tiers now rather than after one team is proven? Argue both sides properly,
   then give a recommendation.

9. THE GATE PROBLEM AS A TOPOLOGY PROBLEM. Our gates never refuse (22 events, 0 refusals) and most
   have no check. Is "who is allowed to say no, and how do we know they can" a known design axis in
   multi-agent systems? What structures put refusal somewhere it cannot be optimised away by the
   party being judged?

=====================================================================
CONSTRAINTS
=====================================================================
- Separate OBSERVED from MARKETED. Benchmark results with no real side effects should be labelled
  as such — our work deploys containers and writes to a warehouse.
- Where a vendor claims production readiness without published evidence, say so.
- Prefer post-mortems and engineering write-ups with real numbers over launch posts.
- Tell us if our three-agent sketch is wrong. We would rather rebuild it now.

=====================================================================
DELIVERABLE
=====================================================================
1. A direct verdict: for our workload, one agent or a team? With the evidence and the threshold at
   which the answer would flip.
2. A graded critique of architect/implementer/tester and its prohibitions, role by role.
3. A recommended minimum topology for our first team, concretely specified.
4. An explicit deferral list — what NOT to build — each with the evidence threshold that would
   justify unlocking it.
5. A framework recommendation, including "keep what you have" if that is honest.
6. A versioning schema recommendation with its known failure modes.
7. What remains unknown, stated separately from what you are confident about.
```
