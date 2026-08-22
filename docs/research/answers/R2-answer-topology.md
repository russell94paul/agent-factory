# Evidence-based design for your first agent team

## Executive verdict

**Direct recommendation: start with one end-to-end implementation agent, not the three-agent architect → implementer → tester team. Put planning inside that agent’s workflow, and put authoritative verification outside the agent entirely.**

The minimum topology I would certify first is:

> **deterministic orchestrator → one coding agent → independent executable verifier → human-only privileged gates**

The coding agent should plan, inspect, modify, test, repair and prepare the change in one continuous context. It may run the same tests repeatedly for feedback, but it **cannot author the authoritative PASS bit**. That bit should come from a non-LLM verifier running an immutable contract in a clean environment. An LLM reviewer should be optional and exception-driven, not a mandatory third hop.

That conclusion is unusually strong because your own production evidence points in the same direction as the strongest recent multi-agent evidence. Your recorded stage-attempt completion rate is only **165 / (1,001 + 165) = 14.2%**, four runs have an unclosed `stage_started`, three “COMPLETED” runs contain 115, 21 and 15 stage failures, and you have 1,004 restarts including a 352-restart stage. Most importantly, you say the substantive work inside stages was mostly correct and **all measured failures were at seams**. In that setting, adding two mandatory LLM-to-LLM handoffs is treating the wrong variable.

The strongest broad experimental study I found tested **180 configurations across five architectures, three model families and four agentic benchmarks**. Multi-agent systems averaged **−3.5% performance relative to single-agent baselines** across the study, with a very wide 95% interval of −18.6% to +25.7%. The result depended strongly on task structure: a centralised system improved a parallelisable financial task by **80.9%**, while every tested multi-agent architecture degraded sequential PlanCraft performance by **39% to 70%**. Once a single-agent baseline exceeded roughly **45%**, multi-agent gains tended to diminish or become negative; the fitted capability coefficient was −0.408 with \(p<0.001\). Tool-heavy tasks were especially coordination-sensitive. citeturn3view0turn3view1

That is **OPEN RESEARCH**, not production infrastructure evidence. These are controlled agentic benchmarks; they do not deploy your containers or write Snowflake. But the direction of the result is highly relevant because connector migration is predominantly a **sequential, shared-state software-engineering task**, exactly the class on which decomposition did poorly. citeturn3view0

Anthropic provides the strongest counterexample, but it actually reinforces the distinction. Its production research system uses an orchestrator with parallel subagents and reports a **90.2% improvement over single-agent Claude Opus 4 on Anthropic’s internal research evaluation**. It also reports that its multi-agent system uses roughly **15× the tokens of ordinary chat**, and explicitly says multi-agent systems are a poor fit when agents need extensive shared context or have many dependencies; Anthropic specifically notes that coding tasks are generally less parallelisable and that agents remain weak at real-time coordination and delegation. That is valuable **VENDOR ENGINEERING EVIDENCE**, but for breadth-first research, not stateful infrastructure modification. citeturn2view0turn2view2

There is also evidence that relatively simple single-agent or low-orchestration approaches remain competitive in software engineering. Agentless used localisation → repair → patch validation rather than an autonomous multi-agent organisation and reported **32.0% on SWE-bench Lite at an average $0.70 per issue**. The original SWE-agent demonstrated that a single interactive tool-using agent could solve repository issues, while newer long-horizon benchmarks continue to show a steep fall in performance as tasks become release-sized and span many files and tests. citeturn4search2turn4search22turn0search1 These are again **benchmarks, not real production side effects**.

### The decision threshold

I would **not** use the paper’s approximately 45% single-agent crossover as an automatic rule. It is an empirical prior from four benchmark families, not a production law. Your local flip criterion should be an A/B test.

A three-agent configuration should replace the one-agent configuration only when, on the **same representative connector tasks, same total monetary/token allowance and same authoritative verifier**, it demonstrates something on the order of:

| Unlock condition | Recommended evidence |
|---|---|
| End-to-end quality | At least **+10 percentage points absolute terminal success**, with a confidence interval excluding no improvement |
| Or efficiency | At least **20% lower cost or elapsed time** at statistically indistinguishable success |
| Safety | No increase in unintended side effects, privilege violations, orphan runs or unbounded retry incidents |
| Seams | Every mandatory handoff ≥ **99% accepted-and-correctly-consumed** on the evaluation set |
| Workload shape | Repeated evidence that at least two substantial subtasks can execute independently rather than serially sharing the same repo state |
| Scale | Enough representative runs to establish the above; I would treat 50 tasks as an exploratory screen, not certification |

Those percentages are **my recommended governance thresholds**, not published universal constants.

The short practical answer is therefore:

**One agent now. A team later only if your own eval demonstrates decomposition beats continuity.**

## What the research says about your three proposed roles

Your sketch contains a good control philosophy wrapped around an unnecessarily agentic decomposition. I would retain much of the philosophy while changing who owns each function.

### Architect

**Grade: planning function B+; separate mandatory architect agent D+.**

Planning itself has real evidence behind it. A 2026 study analysed **16,991 SWE-agent trajectories** across four models, SWE-bench Verified and SWE-bench Pro, under eight plan conditions. Removing the normal navigation → reproduction → patch → validation plan consistently reduced performance; periodic reminders could improve compliance. But it also found that a bad or poorly aligned plan could hurt **more than having no explicit plan**, and that harder SWE-bench Pro tasks reduced plan compliance by an average **13%**. citeturn14view0turn15view2

The important detail is that this evidence supports **a plan**, not **a second planner identity**. The study placed the plan in the same programming agent’s context. It does not demonstrate that a separate agent should produce the plan and disappear before implementation. citeturn14view0

The findings actually give a reason to be sceptical of your prohibition:

> “Must not write implementation code. A planner that implements is not planning.”

That is a human organisational intuition, not an evidence-backed property of LLM systems. In a sequential software task, implementation reveals information: an undocumented API shape, a failing fixture, a hidden dependency, a staging/prod mismatch, a tool error. A planner that is forbidden to remain the task owner cannot cheaply incorporate those observations. You have intentionally created a context discontinuity precisely where your production system is already weak.

The same plan study found concrete cases where a mandated reproduction phase caused incorrect tests and repeated patch/test loops; under the no-plan condition, the same model skipped the defective reproduction step and produced the correct patch. citeturn15view0 That is an argument for **adaptive plan revision by the executing agent**, not for immutable delegation from an upstream planner.

**Recommendation:** retain an explicit planning phase, but make it an artefact generated by the implementation owner. Require something like:

```text
inspect/reproduce
→ write structured plan
→ record expected evidence for each step
→ implement
→ revise plan explicitly when observations invalidate it
→ self-test
→ submit candidate to independent verifier
```

You can enforce “plan before write” structurally if useful. Do not create a planner handoff merely to make the boxes resemble a human engineering organisation.

A dedicated architect becomes defensible later when it is doing something that genuinely benefits from separate context—for example decomposing a migration into three largely independent connectors that three workers can pursue concurrently. That is the situation in which the centralised multi-agent experiments show upside. citeturn3view0turn3view1

### Implementer

**Grade: B+ as drawn; A− if made the end-to-end task owner.**

The strongest choices in this role are worktree isolation and the principle that the implementer does not own authoritative acceptance.

The weak part is making a “mid-tier” model an architectural constant before you have measured it. Model tier is an experimental variable, not a role property. In a four-engineer company, saving a few dollars on implementation while increasing retries, investigation cycles or engineer intervention can easily be negative-value. The broad scaling study specifically found that agent architecture interacts with underlying model capability, rather than compensating for it uniformly. citeturn3view0

I would therefore make the first certified worker:

> **planner + implementer + developmental tester**

It should be allowed, and encouraged, to run the authoritative test command during development. Preventing self-testing would remove useful feedback. What it must not be able to do is publish the authoritative result or modify what “PASS” means.

That distinction is important:

**self-testing is good; self-certification is not.**

### Tester

**Grade: A for the independent-verification idea; C− as a mandatory LLM agent; A if replaced by an external deterministic verifier.**

There is evidence that LLM self-assessment and LLM judgement are unreliable enough that you should not make a model’s prose verdict authoritative. Studies of LLM evaluators find measurable self-preference: evaluators can rate their own model family’s generations more favourably even when human annotators do not establish the corresponding quality advantage. citeturn5search10turn5search32

Code review evidence is even more relevant. A 2026 study over more than **1,400 code-review instances** across HumanEval, MBPP and QuixBugs found large false-negative behaviour when LLMs were asked to explain and repair code. For GPT-4o, for example, rejection of correct HumanEval code rose from **26.2%** under direct judgement to **73.2%** under an explain/repair condition; on MBPP the corresponding figures were **35.9% and 87.9%**. citeturn0search7

That evidence does **not** establish that “a different tester agent” is inherently accurate. In fact it argues against substituting a second model’s judgement for evidence. A tester LLM can be independently wrong, overcorrect, or inherit the same model-family biases.

Your strongest tester requirement is therefore not the agent; it is this sentence:

> “Must not report PASS when an instrument could not run.”

I would turn that from English into code:

```python
if any(required_instrument.status != "EXECUTED"):
    verdict = "UNMEASURABLE"
elif any(required_check.status != "PASS"):
    verdict = "FAIL"
else:
    verdict = "PASS"
```

The authoritative verifier should run against the candidate commit, preferably in a fresh environment, with read-only access to the evaluation contract. It should persist the actual commands, environment digest and outputs that generated the verdict.

An LLM tester can then be invoked for things that truly require semantic judgement—“does this migration preserve the business meaning of this oddly documented field?”—but it should produce **advisory evidence**, not be capable of transforming a deterministic failure or unavailable instrument into PASS.

### The prohibitions

**Grade: excellent policy intent; inadequate enforcement mechanism if they exist only in prompts.**

The research does not support treating an LLM `MUST NOT` as a hard boundary.

AgentDojo evaluated stateful tool-using agents across **97 realistic tasks, 629 security cases and 70 tools**. In one GPT-4o condition, a generic prompt-injection attack achieved **45.8% targeted attack success**; some task suites reached much higher attack rates. Moving constraints into tool-level filtering reduced GPT-4o’s targeted attack success to **7.5%** in one configuration, although such filtering also becomes difficult when legitimate and prohibited actions use the same tools. The authors’ broader conclusion is that prompt-based defences are not reliable enough for security-critical enforcement. citeturn7view0turn7view2turn7view3

The software-plan study reaches a similar conclusion under benign rather than adversarial conditions: system-prompt plans are advisory, compliance varies by model and context pressure, and trajectories deviate from instructed phases. citeturn14view0turn15view2

So I would grade the actual controls this way:

| Proposed prohibition | As prompt text | As an enforced boundary |
|---|---:|---:|
| Architect cannot implement | **D** | C if you truly need a read-only planner—but I would remove the role |
| Implementer cannot mark itself green | **D** | **A** when verifier identity/ACL prevents it |
| Tester cannot PASS an unrun instrument | **C** | **A** when verdict code is fail-closed |
| Team cannot deploy production | **D** | **A** when prod credentials/tool do not exist in its capability set |
| Team cannot alter eval corpus | **D** | **A** when corpus is immutable/read-only to worker identity |
| Team cannot raise attempt cap | **D** | **A** when retry policy lives outside agent-controlled state |

For side-effecting infrastructure, **permission topology outranks prompt topology**.

## Seam cost, communication topology, routing and refusal authority

### There is no credible universal “handoff tax” number

I did **not** find a published, production-quality result saying, for example, that an LLM handoff loses 12% or 30% of task information. Claims of that form should be treated sceptically.

The published evidence instead measures downstream manifestations of coordination cost.

The large 180-configuration scaling study found that, under a fixed budget, interaction count grew approximately as \(n^{1.724}\) with team size, which constrained useful teams in its experiments to roughly three or four agents. It also measured **17.2× error amplification** for independent multi-agent systems versus **4.4×** for centralised systems, suggesting that an explicit validator/coordinator can suppress—but not remove—cross-agent error propagation. citeturn3view0turn3view1

Anthropic reports operational versions of the same problem: early agents duplicated work, left coverage gaps, spawned excessive subagents and performed unnecessary searches when delegation was underspecified. Its engineers found synchronous subagents easier to reason about but a bottleneck, while asynchronous execution introduced additional state-consistency, result-coordination and error-propagation problems. citeturn2view0turn2view2

So **OPEN RESEARCH** can quantify coordination effects, but not translate one handoff into a universal percentage of context loss.

Your own system can—and should—measure it directly.

Define a seam event as:

```text
producer reached terminal state
AND expected artefact exists
AND artefact schema validates
AND consumer acknowledges exact artefact digest
AND consumer starts from intended environment/config
AND no hidden prerequisite was lost
```

Then record at least:

```text
handoff_id
producer_attempt_id
consumer_attempt_id
artifact_digest
contract_version
producer_environment_digest
consumer_environment_digest
handoff_started_at
handoff_accepted_at
acceptance_status
failure_class
```

Do not count “producer said done” as handoff success.

For planning purposes, the ordinary series-reliability model is useful: if an end-to-end process requires \(n\) independent seams whose success probabilities are \(r_i\), seam survival is approximately

\[
R_{\text{seams}} = \prod_i r_i .
\]

This is a standard reliability abstraction, not an agent-specific empirical law, and the independence assumption will often be false in your system. citeturn9search18

It nevertheless illustrates how unforgiving handoffs become. To retain **90% end-to-end seam reliability**:

| Mandatory seams | Required reliability of every seam if equal |
|---:|---:|
| 1 | 90.00% |
| 2 | 94.87% |
| 3 | 96.55% |
| 5 | 97.91% |
| 10 | 98.95% |

Your proposed architect → implementer → tester has at least two semantic ownership transfers before considering git, deployment and orchestration boundaries. Your larger four-level hierarchy creates several more.

Because **all your measured failures are already seam failures**, my prediction is not merely that three agents may cost more. It is that **three mandatory agents have a negative prior for your workload until you establish extremely high handoff reliability**.

That is an inference from your production evidence plus the published sequential-task results; it is not a published connector-migration experiment.

### Your five communication patterns

The evidence is very uneven.

| Pattern | Evidence status | What the evidence actually supports | Recommendation for you |
|---|---|---|---|
| `agent ↔ agent` | **OPEN RESEARCH** | Decentralised collaboration helped some navigation/research tasks: roughly +9.2% on BrowseComp-Plus and +5.7% on Workbench in the scaling study; it was about −41.4% on sequential PlanCraft. citeturn3view0 | Do not use for first connector team |
| `manager → agent` | **OPEN RESEARCH + VENDOR PRODUCTION RESEARCH** | Best-supported topology when work can be parallelised: +80.9% on the financial benchmark; Anthropic uses lead-agent → research-subagent organisation in production research. It still performed about −50.4% on PlanCraft. citeturn3view0turn2view0 | Only topology worth testing later |
| `manager ↔ manager` | **Mostly OPEN RESEARCH** | Hybrid/decentralised topologies exist in benchmarks, but there is no compelling side-effecting engineering evidence that peer supervisors outperform one coordinator | Defer |
| `army → managers` | **SPECULATIVE for this workload** | Hierarchical orchestration is expressible in frameworks, not validated for a four-engineer infrastructure shop | Defer |
| `army ↔ army` | **SPECULATIVE** | I found no documented, inspectable production software/data-engineering deployment showing peer top-level supervisors producing a measured reliability advantage | Do not build |

The last statement is necessarily an evidence-of-absence judgement: I cannot prove nobody has ever built such a system. I can say that I found **no credible production engineering case with measured outcomes** that would justify adopting it.

This is an important distinction. A framework’s ability to draw an edge between two supervisors is **not evidence that the topology is useful**.

### Dynamic team selection

Automated routing is a genuine research topic, but it is nowhere near a reason to add a selector agent to a domain with fewer than ten stable task classes.

DyLAN dynamically selects contributory agents after a preliminary collaboration and reported improvements of up to **25 percentage points on particular MMLU subjects**. That is an interesting research result, but it comes from reasoning/code-generation benchmarks and includes an optimisation phase that itself costs inference. citeturn14view2

A very recent negative study is particularly relevant. It re-evaluated multi-agent orchestration systems and found **policy collapse** in MAS-Orchestra: despite supposedly routing agents according to difficulty, the controller settled into a difficulty-insensitive preference for expensive Debate and Reflexion configurations. It used Debate **84.9%** of the time on GPQA-Diamond and **79.2%** on the supposedly harder HLE-Math condition—the opposite of meaningful difficulty-responsive allocation. Another learned controller collapsed to a single cheap operation on **74.2%** of BrowseComp-Plus activations. citeturn14view1

Conversely, the scaling study could predict the best architecture for a held-out configuration about **87% of the time** using measurable task properties. That is evidence that routing by task characteristics is possible; it is not evidence that a free-running “team selection agent” is the right implementation. citeturn3view0turn3view1

For fewer than ten task types, I would use:

```text
task_type × risk_class -> worker_config_id + verifier_contract_id
```

stored as code/config, reviewed like any other routing rule.

There is **no published crossover at “N task types”**. The economically correct crossover is closer to:

\[
(\text{success}_{dynamic} - \text{success}_{static}) \times \text{value of success}
>
\text{router cost} + \text{misrouting risk} + \text{additional coordination cost}.
\]

For your governance, I would not unlock a learned/dynamic selector until you have at least roughly **200 adjudicated routing examples** and either the static router is ambiguous/wrong on **≥10%** of them, or a held-out dynamic-router evaluation demonstrates at least **+5 percentage points end-to-end success or ≥20% cost reduction** without increasing privileged misroutes. Again, those are recommended internal thresholds, not literature constants.

### Your gate problem really is a topology problem

Your 22 approvals with zero refusals do not, by themselves, prove that the gates are invalid. With only 22 observations, even a true 10% refusal process has about a **9.8% probability of producing zero refusals**. A simple one-sided 95% bound after 0/22 refusals is still roughly 12.7%.

But those statistics are almost beside the point because your implementation evidence is much stronger:

**five of seven gates have no programmatic check at all**, eight approvals carry no substantive note, and “COMPLETED” can coexist with tens or hundreds of recorded failures.

The authority to refuse is therefore not reliably instantiated.

This is a known control-design problem even if agent literature has not settled on one vocabulary for it. Mature security engineering calls for **separation of duties** and distinct enforcement authority; NIST SP 800-53 includes separation-of-duties controls precisely to prevent one actor from controlling incompatible portions of a decision process. citeturn20search2turn20search14 The agent-scaling experiments independently show that centralised checking can materially reduce error amplification relative to uncontrolled independent agents. citeturn3view0

Your gate should therefore be a **reference authority**, not a conversation partner:

```text
WORKER
  may: read repo, edit worktree, run developmental tests
  may not: write eval contract, write authoritative gate state

VERIFIER SERVICE
  may: read candidate commit + immutable eval contract
  may: write PASS / FAIL / UNMEASURABLE + evidence
  may not: alter candidate or contract

ORCHESTRATOR
  may: consume verifier verdict
  may not: reinterpret FAIL as COMPLETE

HUMAN
  alone may: production deploy, eval-contract changes,
             retry-cap changes, exceptional override
```

The verifier should be **fail closed**. No instrument means `UNMEASURABLE`, not “probably fine”. A failed required stage means the parent run cannot enter `SUCCEEDED`. An override should be a separate terminal fact—`HUMAN_OVERRIDE_ACCEPTED`—rather than silently rewriting history.

Before any gate earns autopilot authority, test the gate itself. Seed known-bad artefacts. A production safety gate that has never demonstrated the ability to refuse is not yet a gate.

## The minimum topology to build, and what to defer

### Recommended first certified topology

I would replace the three LLM roles with the following.

```text
                     immutable policy / budgets
                              |
                              v
                    +--------------------+
                    | Prefect/control     |
                    | plane               |
                    +---------+----------+
                              |
                              | task + repo + contract ID
                              v
                    +--------------------+
                    | ONE WORKER AGENT   |
                    |                    |
                    | inspect            |
                    | plan               |
                    | implement          |
                    | self-test          |
                    | repair             |
                    +---------+----------+
                              |
                        candidate commit
                              |
                              v
                    +--------------------+
                    | VERIFIER           |
                    | non-LLM authority  |
                    | clean environment  |
                    | immutable contract |
                    +---------+----------+
                              |
                  PASS / FAIL / UNMEASURABLE
                              |
                              v
                    +--------------------+
                    | Control plane      |
                    +---------+----------+
                              |
                    privileged operation?
                         /          \
                       no            yes
                       |              |
                    finish         HUMAN
```

There is **no LLM manager** in the first version. Prefect is the manager in the only sense that presently matters: it owns state.

There is **no mandatory LLM architect**.

There is **no mandatory LLM tester**.

There is **no agent-to-agent free text channel**.

State passes through typed persisted artefacts.

### Control-plane changes are more urgent than agent architecture

Before comparing one versus three agents, I would fix the invariants exposed by your measured logs.

A run should have only a small set of meaningful terminal states:

```text
SUCCEEDED
FAILED
NEEDS_HUMAN
CANCELLED
```

`SUCCEEDED` must be impossible unless every required terminal condition and gate is satisfied. “Completed execution while containing 115 failures” may be a technically meaningful workflow status, but it must not be your business-level success state.

`stage_started` needs a lease/heartbeat and an explicit orphan timeout. Prefect itself distinguishes `Running`, `Retrying`, `Paused`, `Suspended`, `Completed`, `Failed`, `TimedOut` and `Crashed`; it supports configured retry limits and timeouts. citeturn16search0turn16search3

Retries should be externally capped. I would begin with **three total attempts** for a stage—initial attempt plus two repairs—unless a particular error class has evidence for another policy. Same-failure repetition should stop earlier. Your agent must have no tool by which it can mutate that cap.

Concurrency must also be outside the agent. Prefect already has global and tag-based concurrency limits, which can reserve capacity rather than letting ten containers consume the region quota. citeturn16search6turn16search18

Most importantly, give someone—or rather **something deterministic**—ownership of the seam:

```text
producer_done != handoff_done
```

A stage is not complete until the downstream contract has accepted its exact output.

### The deferral list

| Do **not** build yet | Why | Evidence that should unlock it |
|---|---|---|
| Separate architect LLM | Adds an ownership/context seam; planning evidence does not establish planner identity | Same-budget A/B showing ≥10 pp terminal-success gain or ≥20% efficiency gain without more seam failures |
| Mandatory tester LLM | Executable verifier is stronger; second model introduces judgement error and another seam | A non-executable semantic criterion where blinded external LLM judgement demonstrably improves agreement with expert humans |
| `agent ↔ agent` messaging | Benchmark-dependent and negative on sequential tasks | Production-like tasks with genuine concurrent branches and ≥5 pp net gain after coordination cost |
| `manager ↔ manager` | No production engineering case justifying it | At least several independently certified teams plus a measured inter-team coordination bottleneck |
| `army → managers` | Hierarchy before units exist | ≥3 stable team types, meaningful concurrent demand, and evidence one manager is an actual throughput/reliability bottleneck |
| `army ↔ army` | No production evidence found | A controlled local experiment or credible external production case showing a material reliability/throughput gain |
| Dynamic “team selection” LLM | <10 stable classes are easy to route deterministically; learned routing can collapse | ≥200 adjudicated examples plus static misrouting ≥10%, or held-out ≥5 pp success / ≥20% cost benefit |
| Ten team types | Premature ontology | Create a specialist only when enough tasks exist to show it beats the generic worker materially |
| “Agentic gym” / training environment | You currently lack a trustworthy outcome signal; training on current traces risks learning pathological loops | Stable verifier plus hundreds of clean, labelled successful/failed trajectories and a measurable skill deficit |
| Framework migration | Does not address your current failure mode | Fault-injection shows an invariant your existing Prefect/control plane cannot satisfy but candidate framework can |
| Autonomous production deployment | Current gates are not certified | External verifier with demonstrated negative controls, zero critical false-pass in certification, and explicit human risk decision |
| Autonomous retry-cap changes | Directly recreates your 352-restart incident class | I would **not** unlock this through ordinary agent performance; treat it as a privileged control-plane operation |

### The hierarchy question

There is one legitimate argument **for** building hierarchy early: it can force you to define interfaces, authority and state ownership before the system grows. Centralised orchestration also has substantially lower measured error amplification than independent multi-agent collaboration, and managers can be useful where many independent workers have to be allocated across parallel tasks. citeturn3view0turn3view1

But that is an argument for a **control plane**, not necessarily for a hierarchy of LLMs.

The argument **against** the proposed Agent → Team → Team Manager → Army stack is considerably stronger in your present state. You have zero certified teams, no evidence that three roles outperform one, no observed routing problem requiring a team selector, and a production failure distribution dominated by boundaries. The research finds superlinear coordination growth and negative returns on sequential tasks; Anthropic’s own successful multi-agent deployment warns against the pattern for highly shared-context coding work. citeturn3view0turn2view0

Therefore:

**Do not build supervisor tiers now. Build the data model so a supervisor could be added later, but instantiate zero supervisor LLMs until a certified worker topology gives you something worth supervising.**

An empty extension point is cheap. An operational hierarchy becomes a source of states, traces, prompts, handoffs, failure modes and certification obligations.

## Framework assessment

The framework market has moved substantially, but none of the major agent frameworks fixes the problem shown in your production logs automatically.

Your existing architecture already has DAG orchestration, model selection, budgets, turn limits, gates and isolated worktrees. The principal missing features are not “agent framework” features; they are **correct terminal semantics, durable caps, fail-closed gates and seam ownership**.

### Framework comparison

| System | Hours / restart durability | Human gate mid-run | Restart-safe monetary ceiling | Untrusted generated code | Assessment for your case |
|---|---|---|---|---|---|
| **Your Prefect 3 control plane** | Strong workflow/state machinery; retries, timeouts, persisted run state; `Suspended` explicitly exits process pending resume. citeturn16search0turn16search3 | Yes; pause/suspend primitives exist | You already implement budgets; persist them as authoritative orchestration state | Your container/worktree layer | **Keep and harden** |
| **Temporal** | **Excellent**. Workflows can survive infrastructure failure and run for years; state reconstructed from event history. citeturn16search21 | **Excellent**: durable Signals/approval patterns can wait hours, days or indefinitely without holding compute. citeturn16search2turn16search5 | Straightforward to implement durably in workflow state, but application policy rather than an LLM-budget product feature | External activity/container required | **Production-grade control plane**, but likely unnecessary migration unless Prefect durability is inadequate |
| **LangGraph** | Real persistence/checkpoint support; durability depends on configuration. Its `exit` mode explicitly cannot recover intermediate state after a process crash, whereas stronger checkpoint modes trade performance for durability. citeturn17search2turn17search5 | Good: interrupts persist state and can wait indefinitely; approve/edit/reject supported. citeturn17search0turn17search6 | No compelling native durable monetary-budget mechanism; you would model it yourself in persisted state | Not fundamentally its security boundary; integrate external isolation | **Credible agent runtime**, but replaces functionality you already possess rather than solving your root cause |
| **CrewAI** | Current Flows advertise persistence and resumption of long-running workflows. citeturn18search18 | Current `@human_feedback` supports paused approval flows. citeturn18search4 | Usage metrics exist, but I found no strong documented restart-safe hard spend ceiling | CrewAI has deprecated its own code-execution facility in favour of E2B/Modal-style dedicated sandboxes. citeturn18search8 | **VENDOR-MARKETED production framework; no reason to replace your working orchestrator** |
| **AutoGen** | Team state can be saved/restored, but it is not the strongest durable workflow control plane | HITL exists; patterns require care around state | Application-level | Docker code executor available and recommended for generated code. citeturn19search0 | **Do not start a new strategic build here**; Microsoft has now made Agent Framework its successor |
| **Microsoft Agent Framework** | Microsoft describes robust long-running and HITL state and workflow checkpoints. citeturn18search2turn18search6 | Yes | Application-level unless surrounding Azure/runtime policy supplies it | Depends on integration | **Newer entrant; promising, but current production-readiness is primarily VENDOR CLAIM rather than independent operational evidence** |
| **OpenAI Swarm** | Stateless between calls | Basic pattern only | No | No production boundary | **Do not use.** OpenAI now explicitly labels Swarm experimental/educational and says it has been replaced by Agents SDK. citeturn21search3 |
| **OpenAI Agents SDK** | Base SDK has sessions/state; official docs point to Temporal, Restate, Dapr and DBOS integrations for durable long-running recovery. citeturn16search1 | Tool approvals and resumable run state are first-class | Turn limits are native; durable **monetary** cap remains your policy/control-plane concern. citeturn16search10turn16search16 | Sandbox Agents now exist with local/Docker/hosted clients, but the feature is explicitly **beta**. citeturn21search1turn21search6 | Good worker harness; **not a reason to replace Prefect** |
| **Claude Agent SDK** | Sessions can resume/fork, but the SDK itself runs the agent loop in your process; Anthropic distinguishes separate Managed Agents for long-running hosted agents. citeturn18search3turn18search11 | Permission/hooks machinery exists | Your application must enforce durable money policy | For Agent SDK, isolation is your environment; Anthropic’s managed product provides managed sandbox infrastructure separately. citeturn18search3 | Strong candidate **inside** a coding worker, not as your workflow control plane |

Two points deserve emphasis.

First, **durable execution and agent persistence are not identical**. Temporal’s defining abstraction is replayable durable workflow state. LangGraph checkpoints agent graph state. Agents SDK can serialize/resume agent state and now integrates with external durable runtimes. Claude Agent SDK can resume a session. Those are useful but materially different guarantees. Temporal explicitly documents that activity side effects must be designed for idempotency because replay/retry does not make arbitrary external operations magically exactly-once. citeturn16search8turn16search21

Second, LangGraph itself documents that replaying from a checkpoint can re-execute downstream LLM calls and API requests. That is precisely the kind of detail that matters when a tool creates a container or mutates Snowflake. citeturn17search11 Any framework still requires you to design idempotency keys and side-effect boundaries.

### What I would adopt

**Framework recommendation: adopt nothing new for orchestration now.**

Keep Prefect 3 and the git/container isolation you already have. Prefect already supports the controls your incident history says you need: explicit retry limits, timeouts, state transitions, suspension and global concurrency controls. citeturn16search0turn16search3turn16search6

The current architecture has not failed because it lacks an agent graph library. It failed while possessing an 18-stage graph.

I would consider one of the agent SDKs **inside the worker process** if it materially reduces your own tool-loop code. That is an implementation choice, not a system architecture migration.

Temporal deserves a separate evaluation only if fault injection shows that Prefect cannot deliver a durability invariant you actually require—for example, surviving arbitrary process death during a multi-day approval while preserving exactly which actions have and have not been committed. Prefect’s present functionality already covers a great deal of your stated requirement, so migrating before proving that gap would create another seam.

## Versioning and attribution

Your content-addressed approach is fundamentally sound.

**I would keep the hash design. I would substantially enlarge what is inside the hash and separately record what actually happened at runtime.**

There is no single industry-standard “agent build manifest” yet. OpenTelemetry’s emerging GenAI semantic conventions illustrate the direction: they distinguish an agent identifier/version, provider, requested model, **response model**, prompt information, tool definitions, token usage, evaluation data and workflow identity. citeturn20search3turn20search6

That distinction between requested and returned model is important. Your current tuple hashes:

```text
(prompt, model, effort, tools, retry policy, turn cap, budget)
```

but “tools” and “model” are not sufficiently precise.

For example, Anthropic documents explicit model-version semantics: current model IDs are pinned snapshots; older convenience aliases can resolve to dated releases. citeturn20search1 A versioning system should therefore store both what you requested and what provider/runtime metadata says actually answered.

### Recommended build schema

I would make an immutable manifest approximately like this:

```yaml
agent_build:
  schema_version: 1
  agent_build_id: "sha256:<canonical-manifest>"

  prompt:
    template_digest: "sha256:..."
    exact_system_prompt_digest: "sha256:..."
    prompt_source_git_sha: "..."
    skill_bundle_digest: "sha256:..."

  model:
    provider: "..."
    requested_model: "..."
    api_version: "..."
    reasoning_effort: "..."
    temperature: "..."
    top_p: "..."
    max_output_tokens: 0
    context_management_policy_digest: "sha256:..."

  tools:
    manifest_digest: "sha256:..."
    entries:
      - name: "git"
        schema_digest: "sha256:..."
        implementation_git_sha: "..."
        container_image_digest: "sha256:..."
      - name: "shell"
        ...
    mcp_server_manifest_digest: "sha256:..."

  runtime:
    agent_harness_git_sha: "..."
    dependency_lock_digest: "sha256:..."
    base_image_digest: "sha256:..."
    os_arch: "..."
    sandbox_policy_digest: "sha256:..."

  permissions:
    credential_scope_digest: "sha256:..."
    network_egress_policy_digest: "sha256:..."
    filesystem_policy_digest: "sha256:..."

  control:
    turn_cap: 0
    attempt_cap: 0
    retry_policy_digest: "sha256:..."
    monetary_budget: "..."
    wall_clock_timeout: "..."
    concurrency_class: "..."

  evaluation:
    contract_id: "..."
    contract_digest: "sha256:..."
    corpus_digest: "sha256:..."
    verifier_image_digest: "sha256:..."
```

Then hash the **canonical serialized bytes**, not an ad hoc concatenation of fields.

Your team version remains:

```text
team_build_id =
    hash(
        ordered member build IDs,
        topology definition,
        router version,
        handoff-contract versions,
        verifier-contract version,
        permission topology
    )
```

I would add the permission topology because changing “tester may now write the corpus” changes the effective system even if every prompt and model stays identical.

### The run record is separate from the build record

A build hash answers:

> “What configuration did we intend to run?”

A run record must answer:

> “What concrete system actually ran, against what input and environment?”

For every model invocation, capture at minimum the requested model plus returned model identity and provider response ID where available. OpenTelemetry explicitly separates `gen_ai.request.model` from `gen_ai.response.model` for this reason. citeturn20search3

For your workload, I would persist:

```yaml
run:
  run_id:
  team_build_id:
  started_at:
  terminal_state:

  input:
    request_digest:
    repo_commit:
    connector_id:
    vendor_api_schema_version:
    staging_environment_digest:

  stage_attempts:
    - attempt_id:
      stage_id:
      agent_build_id:
      attempt_number:
      parent_attempt_id:
      model_request_id:
      requested_model:
      returned_model:
      input_tokens:
      output_tokens:
      cost:
      start_state:
      terminal_state:
      candidate_commit:
      artifact_digests:
      failure_class:

  handoffs:
    - handoff_id:
      producer_attempt_id:
      consumer_attempt_id:
      artifact_digest:
      contract_digest:
      acceptance_status:

  gates:
    - gate_id:
      contract_digest:
      verifier_identity:
      evidence_digest:
      verdict: PASS | FAIL | UNMEASURABLE
      override_identity: null

  side_effects:
    - operation:
      idempotency_key:
      target_environment:
      request_digest:
      result_digest:
```

This would have made several of your current anomalies mechanically easy to diagnose.

### What your present hash misses

It does not yet capture:

**Tool implementation drift.** Two runs can both say `tools=["shell","git"]` while the shell image, CLI versions, PATH, credentials or wrappers differ.

**Sandbox/environment drift.** Base image, OS packages and egress policy change behaviour.

**Model routing.** The requested model name does not necessarily convey every detail of the served system. Record provider, exact requested identifier and provider-returned model metadata. OpenTelemetry already models the requested/response distinction. citeturn20search3

**Context-management drift.** Compaction, memory, retrieval order and truncation policy can radically alter behaviour without changing your top-level prompt.

**External knowledge drift.** Vendor API schemas, retrieved docs, MCP servers and repository state can change.

**Permissions.** An agent with prod credentials is not the same certified object as one without them.

**Verifier drift.** Certification against contract V4 must not silently transfer to contract V5.

**Harness drift.** The code that parses tool calls, handles retries or interprets termination is part of agent behaviour.

**Side-effect replay semantics.** The same build may behave differently after a crash depending on which API calls were committed externally.

Long-running deployments make attribution especially important. Anthropic describes “rainbow deployments” in which long-running agent instances from different software versions coexist during rollouts; this is exactly the kind of situation where “current version” is not a sufficient run identifier. citeturn2view2

### Retention

There is no established universal agent-retention period.

My recommendation is:

| Artefact | Retention |
|---|---|
| Agent/team build manifests and hashes | Indefinitely while any associated run or certification matters |
| Certification results and gate evidence | At least the lifetime of the certified version plus your normal engineering/audit horizon |
| Production side-effect/audit records | At least 1–2 years unless your contractual/compliance regime requires longer |
| Full prompts/tool outputs/traces | Shorter, for example 90–180 days by default, because these are expensive and can contain credentials, proprietary code or data |
| Aggregated metrics | Long-term |
| Raw sandbox/worktree contents | Only as long as needed once candidate commits and evidence digests are preserved |

Those durations are **policy recommendations**, not an industry standard.

At scale the hard problems become high-cardinality storage, secrets in traces, data-retention obligations, state-schema migrations, mutable external systems, and the impossibility of perfectly replaying side-effecting histories. Observability standards help correlate runs; they do not make a stochastic external world reproducible. OpenTelemetry’s semantic conventions standardise names and metadata, not deterministic replay. citeturn20search12turn20search15

## What is established, what is marketed, and what remains unknown

### What I would regard as established enough to design around

**ESTABLISHED PRACTICE:** side-effecting automation needs an external control plane for retries, timeouts, concurrency, privilege, durable state and approval. Prefect and Temporal both expose these primitives; they should not be delegated to a model’s discretion. citeturn16search3turn16search6turn16search21

**ESTABLISHED PRACTICE:** separation of duties is a real control mechanism. The actor producing a change should not possess the same authority required to independently approve a privileged consequence. citeturn20search2turn20search14

**ESTABLISHED PRACTICE:** executable evidence is preferable to an LLM’s subjective declaration when the property is executable. The agent may use tests as feedback, but the authoritative run should be independently generated and persisted.

**ESTABLISHED PRACTICE:** retry and concurrency caps must live outside the entity being capped. Your overnight ten-container incident is a particularly clear local demonstration.

**ESTABLISHED PRACTICE:** immutable/content-addressed version identifiers are a good foundation for attribution, provided the manifest covers the complete executable configuration rather than only prompt/model labels. Emerging GenAI observability standards explicitly carry agent version, model, provider, tools and evaluation metadata. citeturn20search3turn20search6

### What the research supports, but has not proved for your production workload

**OPEN RESEARCH:** multi-agent systems can substantially beat a single agent on tasks that are highly parallelisable, but can substantially lose on sequential/shared-state tasks. The measured range in the largest recent controlled study is dramatic: **+80.9%** in one parallelisable setting versus roughly **−39% to −70%** across multi-agent variants on a sequential one. citeturn3view0turn3view1

**OPEN RESEARCH:** centralised manager-worker coordination is a better prior than uncontrolled peer collaboration when multi-agent work is justified; independent-agent error amplification was measured at 17.2× versus 4.4× under centralisation. citeturn3view0

**OPEN RESEARCH:** explicit plans can improve programming-agent performance, but compliance is imperfect and inappropriate plans can actively hurt. This supports plan artefacts and adaptive planning, not a mandatory architect identity. citeturn14view0turn15view0

**OPEN RESEARCH:** dynamic agent selection can work on benchmarks, but learned orchestration can also collapse into non-adaptive policies. There is no established “ten task types” crossover point. citeturn14view2turn14view1

**OPEN RESEARCH:** LLMs exhibit enough evaluator bias and code-review miscalibration that self-certification should not be trusted. The evidence does not prove that simply using a second LLM solves the problem. citeturn5search10turn0search7

### What is principally vendor evidence or marketing

**VENDOR EVIDENCE:** Anthropic has a genuine production multi-agent research system and reports large internal-eval gains, but the workload is breadth-first research and Anthropic itself cautions that highly interdependent coding is a poor fit. citeturn2view0turn2view2

**VENDOR CLAIM / DOCUMENTED CAPABILITY:** LangGraph, CrewAI, OpenAI Agents SDK, Claude Agent SDK and Microsoft Agent Framework all have increasingly serious state, approval and orchestration features. Their documentation demonstrates that the mechanisms exist; it does **not** establish that adopting those frameworks will make your connector migration more reliable. citeturn17search3turn18search18turn16search1turn18search3turn18search2

**VENDOR CLAIM:** OpenAI calls Agents SDK the production-ready successor to Swarm; Microsoft calls Agent Framework the successor to AutoGen/Semantic Kernel. Those are useful product-lifecycle facts, not independent reliability benchmarks. citeturn21search3turn18search2

### The genuinely unknown questions

There is **no strong production literature establishing the optimal number of LLM agents for side-effecting data-engineering migrations**.

There is **no validated universal handoff-loss coefficient** for tool-using software agents.

There is **no credible evidence that architect / implementer / tester is intrinsically the correct three-agent decomposition**. The closest evidence supports planning and verification as *activities*, not three persistent identities.

There is **no evidence that your mid-tier implementation model is the cost-optimal choice** until you run it against the same contract as a stronger model.

There is **no established production crossover where dynamic team selection beats a static routing table based merely on the number of task classes**.

I found **no persuasive production engineering evidence for peer top-level “army ↔ army” supervisors**.

There is **no framework that removes the need to define idempotency, retry ownership, authoritative completion, immutable gates and privilege separation**. Temporal and Prefect can enforce the workflow mechanics; an agent framework cannot decide the semantics for you. citeturn16search8turn17search11

And most importantly, you still do not know the one baseline that your larger design assumes away:

> **How well does one strong, continuously-contextualised worker perform on your connector migrations when placed behind a competent control plane and a real verifier?**

Until that number exists, every extra agent, manager, selector and army is an unpriced hypothesis.

The three-agent sketch is therefore **not defensible as the first certified topology**. Its good ideas are the plan, worktree isolation, independent acceptance authority, immutable evals, finite budgets and human-only privileged changes. Keep those. Remove the two unnecessary LLM handoffs.

Your first “team” should deliberately be boring:

> **one agent that owns the work; one deterministic system that owns truth; one human boundary that owns irreversible authority.**

That topology attacks the failure mode you actually measured rather than the organisational complexity you might someday need.