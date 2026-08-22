# Repo-Agnostic Agent Optimisation: Evidence, Costs, and an Honest Build-or-Wait Verdict

## Verdict and sequencing

**Verdict: build a single-repository optimiser first, but make the harness portable from day one. Do not build the repo-agnostic optimiser as the product now.**

The production measurements supplied for 21 August 2026 are not the measurements of a system ready for optimisation; they are the measurements of an experimental apparatus that is not yet under control. **[INTERNAL OBSERVED]** Only 3 of 14 recorded runs reached terminal completion; exactly one connector has a recorded successful end-to-end run; stage attempts failed 1,001 times against 165 completions; four runs stopped at `stage_started` with no terminal event; five of seven gates have no programmatic check; all 22 gate decisions approved; and the worst completed run spent 92,817 of 95,098 seconds—97.6%—inside one uncapped restart loop. The cost data are censored in the most damaging possible direction: failures are recorded as $0.00.

Those facts make optimisation unsafe statistically as well as operationally. An optimiser would currently be able to “improve” apparent cost by failing in ways for which cost disappears, “improve” gate passage against gates that never refuse anything, and spend most of its experimental budget exploring retry behaviour rather than software capability. The existing four-valued assertion contract—PASS, FAIL, UNMEASURABLE, NOT_RUN, with UNMEASURABLE explicitly not a pass—is the right direction, but its fitness signal has not yet been shown to discriminate good configurations from bad ones.

**[OPEN RESEARCH]** The published frontier does not fill that gap. As of 22 August 2026, I found no published demonstration of a system that can be pointed at an arbitrary previously unseen repository, autonomously discover a trustworthy semantic objective, reliably construct its environment, optimise a multi-step tool-using agent configuration, and then exercise arbitrary real cloud/database side effects safely. The recent VeRO work explicitly describes agent optimisation as “far from solved” and finds fragile transfer and limited exploration; current automated environment-building research still reports substantial setup failures. citeturn19search3turn19search39turn20search0turn20search5

There **is** convincing evidence that generic optimisation machinery works once somebody has already supplied a good evaluator. AlphaEvolve is the strongest production-adjacent example: Google reports that it uses automated evaluators and has produced improvements deployed in data-centre, chip-design and AI-training systems, and Google made AlphaEvolve broadly available through Google Cloud in 2026. That is important evidence for evaluator-driven search, but it is not evidence for automatic fitness discovery on arbitrary repositories. citeturn18search1turn18search5turn18search21

So the right distinction is:

> **Make the plumbing repo-agnostic now; keep the optimisation evidence repo-specific until transfer is demonstrated.**

That means a generic repo adapter, contract schema, sandbox boundary, evaluator protocol, parameter registry and optimiser API now—but only one production-proven repository or tightly related connector family behind it initially.

### What searching would cost with today's evaluator

The monetary cost cannot honestly be calculated from the supplied logs because 1,001 failed attempts have no spend recorded. That is not an estimation problem; the historical spend is unrecoverable. The wall-clock implications alone are sufficient to reject live brute-force optimisation.

Using the **26.4-hour median of the three completed runs**—itself a very small and uncertain sample—the following modest searches would consume:

| Candidate configurations | Repeats per configuration | Full migrations | Executor-hours | Serial time |
|---:|---:|---:|---:|---:|
| 5 | 3 | 15 | 396 | 16.5 days |
| 10 | 3 | 30 | 792 | 33 days |
| 20 | 3 | 60 | 1,584 | 66 days |

Parallelism can reduce calendar time, but not total model, cloud, warehouse or engineering consumption. And these figures assume completed-run timing rather than the current pathological failure/retry distribution.

That also explains why systems such as GEPA cannot simply be dropped on top of today's live migration. GEPA's own guidance says it can sometimes improve from very few examples but recommends roughly **30–300 examples** for best results. Thirty *live* examples at 26.4 hours each are already 792 executor-hours for a single pass over the set, before candidate exploration. The only viable interpretation here is 30–300 **cheap offline/replay task instances**, not 30–300 production connector migrations. citeturn17search19

### What I would build before any cross-repo search

The first optimisation product should be a **Repo Optimisation Harness v1**, exercised against one repository/family:

1. Every attempted stage gets a terminal event, duration, token/model cost, external-service cost estimate and retry count—even on failure.
2. Retries have hard attempt, elapsed-time and monetary limits enforced outside the agent.
3. Hard gates are executable; where a human decision is genuinely necessary, refusal must be a real, tested state.
4. Evaluation and optimiser run under different identities; the optimiser cannot modify its grader.
5. Every run is resettable and replayable from an immutable repo revision plus environment digest.
6. The fitness qualification procedure below passes before search is enabled.
7. Search begins on recorded evidence and synthetic/known regressions; only finalists receive staging migrations, and production writes are never part of unconstrained search.

None of those steps depends on adopting a particular optimisation framework. They are prerequisites for **any** one of them.

## Fitness discovery and the repo contract

The central conceptual answer is that **“repo-agnostic” cannot mean “objective-free”**.

An optimiser can be agnostic to the *representation* of the repository-specific fitness function: it can call a common evaluator interface. It cannot, in the general case, know from source code alone whether “better” means lower latency, preservation of an undocumented downstream schema, fewer Snowflake credits, exact historical semantics, cleaner code, more rows, fewer rows, or deliberately retaining some unusual vendor behaviour.

The universal component therefore has to be an **objective protocol**, not an objective generator.

### The available sources of fitness

| Fitness source | Evidence class | What it is good for | Why it is insufficient by itself |
|---|---|---|---|
| Existing repo tests | **ESTABLISHED PRACTICE** | Executable functional constraints; cheap regression signal | Weak tests reward weak solutions; tests may encode implementation rather than intended behaviour |
| CI green/red | **ESTABLISHED PRACTICE** | Build/smoke gate and immediate feasibility check | Very low-information binary signal; “green” says nothing about untested semantics |
| Maintainer-declared contract | **RECOMMENDED DESIGN / ESTABLISHED SOFTWARE PRINCIPLE** | Makes the objective, hard constraints and authority explicit | Requires per-repo human work; there is no universal agent-optimisation contract standard yet |
| Curated benchmark harness | **ESTABLISHED IN RESEARCH** | Repeatable comparison, held-out tests, controlled task distribution | Expensive to construct and may still fail to represent production side effects |
| LLM-inferred objective | **OPEN RESEARCH** | Suggesting candidate tests, setup commands and likely invariants | No evidence it can be trusted as the sole semantic authority for arbitrary repositories |
| Human preference | **ESTABLISHED FOR SUBJECTIVE JUDGEMENT** | Maintainability, style, UX, ambiguous trade-offs | Expensive/noisy and cannot replace executable correctness and safety constraints |

The evidence against blindly treating tests as semantic truth is unusually strong. When SWE-bench was manually re-evaluated, 93 experienced Python developers reviewed 1,699 samples; OpenAI reported widespread under-specification and test criteria that could reject valid solutions, with **68.3% of the reviewed samples ultimately filtered out** in forming a more trustworthy benchmark. citeturn20search3turn5search10 SWE-bench's better evaluation pattern is not simply “does CI pass?”: it uses **FAIL_TO_PASS** tests that fail before the intended fix and pass afterwards, plus **PASS_TO_PASS** tests intended to catch regressions. citeturn20search7turn20search34

There is a further warning from research analysing SWE-bench's grader: one study found patches that could count as solved while still failing developer-written tests and found behavioural discrepancies among additional plausible patches. That result is benchmark-specific, but it illustrates the more general point that an executable metric can be gamed or incomplete without being obviously broken. citeturn20search11

### The missing standard: a fitness-qualification pre-check

There is **no accepted universal test called “is this metric actually measuring the right thing?” for coding-agent optimisers**. Mature practice contains pieces of such a check—A/A experiments, reliability analysis, test adequacy, mutation testing, negative controls, held-out evaluation and F2P/P2P validation—but no published framework I found combines them into a repo-agnostic fitness certification step.

For this company, I would make that step explicit and mandatory. Call it the **Fitness Qualification Gate**.

Before the optimiser receives even one search evaluation, the candidate evaluator should have to pass five tests.

**Evaluator integrity.** The grader, expected outputs and held-out assertions are mounted read-only and excluded from the agent's editable workspace. A candidate must not be able to obtain a better score by deleting tests, suppressing logs, making evidence unavailable, editing the scorer or changing the evaluation dataset. The company's existing decision that UNMEASURABLE is not PASS is exactly right; extend it so that making a hard requirement unmeasurable makes the candidate **infeasible**, never cheaper or better.

**Repeatability.** Run the same immutable baseline against the same replay several times. Offline replay assertions should be deterministic unless there is an explicitly model-dependent evaluator. For live/stochastic portions, estimate the distribution rather than pretending one result is the value. Recent large-scale research over 60,000 agent trajectories found measurable performance variation even at temperature zero; identical agent inputs can also produce multiple distinct action sequences. citeturn19search0turn19search1

**Negative-control sensitivity.** Seed known failures representative of the damage you care about. In this connector pipeline, that could include an import failure, a subtly wrong schema, missing rows, duplicated rows, a stale cursor, wrong timezone conversion, bypassed Prefect registration, failure to upload the Azure object, writing to the wrong Snowflake schema, a deliberately broken authentication path, and a restart loop. Every catastrophic control should fail at least one **hard** assertion. If a deliberately broken connector can pass, search stops.

This is the place where mutation testing is useful: not as proof of semantic completeness, but as a way of asking whether tests respond when meaningful behaviours are perturbed. Large-scale industrial mutation-testing work at Google demonstrated that targeted mutation analysis can provide actionable information about test adequacy at large scale. citeturn6academia25

**Discrimination.** Assemble a small calibration panel whose ordering is known independently of the optimiser: a known-good replay, a harmless no-op, minor regression, serious functional regression and catastrophic safety regression. The evaluator must order these correctly—or at minimum place all invalid variants below every admissible variant. Then evaluate several materially different agent configurations. If everything receives the same verdict, or score differences are smaller than run-to-run measurement noise, the metric carries no useful optimisation gradient and the search budget remains zero.

I would not impose a universal numerical “variance must be X” threshold; none is established. Instead predeclare the **minimum effect worth buying**—for example, a reduction in failed stages, elapsed time or cost that would affect a business decision—and require the evaluator's uncertainty to be small enough to distinguish that effect.

**Held-out confirmation.** Search candidates see one task/replay set; selection is confirmed on a separate one. Hidden evaluator assertions should include mutations or historical failures the optimiser never saw. This separates “found a better configuration” from “found a way to satisfy this evaluator”.

The result should be binary:

> `FITNESS_QUALIFIED` or `FITNESS_NOT_QUALIFIED`.

There should be no optimisation fallback when qualification fails. The correct response to a non-discriminating metric is **improve the metric**, not “let the LLM reason about it”.

### How the company's score should be structured

Do not reduce the 12 assertions, spend, latency and safety into one weighted scalar immediately. Use a lexicographic/Pareto structure:

**First: feasibility.** Any hard correctness or safety FAIL is disqualifying; hard UNMEASURABLE is also disqualifying.

**Second: functional quality.** Among feasible configurations, maximise end-to-end success and semantic assertions.

**Third: reliability.** Minimise restart incidence, stage failures, variance and incomplete runs.

**Fourth: efficiency.** Only among comparably correct candidates minimise model cost, Azure/Snowflake cost and wall-clock time.

That ordering prevents an optimiser from discovering that the cheapest connector is one that never finishes.

### The minimum repo interface

There is useful prior art, but **none of it is the whole interface needed here**.

SWE-bench task instances couple a repository revision and issue with specific evaluation tests, including failing-to-passing and passing-to-passing tests. That is a good *task/evaluator contract*, but its environments and tasks required substantial benchmark curation. citeturn19search34turn20search34 SWE-agent historically accepts a repository/task plus an execution environment, while its own documentation notes that its evaluation step is specifically available for SWE-bench issues rather than automatically for arbitrary repositories. citeturn20search33 Aider's SWE-bench work similarly benefits from an already constructed benchmark and acceptance tests; it is not an arbitrary-repository objective-discovery protocol. OpenHands supplies a sandbox/runtime abstraction, not semantic fitness for an arbitrary codebase. citeturn7search2turn7search14turn7search1

A `devcontainer.json` is excellent environment metadata: the Dev Container specification exists specifically to describe the container and metadata required for a development environment. It does not say what repository behaviour is correct. citeturn21search1turn21search5 A Nix flake and `flake.lock` can pin environment inputs and expose standard build/development outputs, but likewise do not define fitness. citeturn21search2turn21search6 For Python, `uv.lock` gives a portable universal dependency resolution and `uv run --locked`/sync semantics, again solving dependency repeatability rather than evaluation semantics. citeturn21search7turn21search31

I would therefore define a small versioned contract—say `agent-opt.yaml`—with the following boundary:

| Contract element | May be auto-detected? | Must ultimately be declared/approved? |
|---|---|---|
| Repository revision and writable paths | Yes, from Git | Yes |
| Languages/package managers | Usually | No, unless detection ambiguous |
| Existing Dockerfile/devcontainer/Nix/lockfiles | Yes | Environment actually used must be frozen |
| Build/install/test commands | Often inferable from CI/manifests | Yes after a validation run |
| Evaluation entry point and verdict schema | Sometimes discoverable | **Yes** |
| Hard correctness/safety constraints | LLM may propose | **Yes, human/repo owner** |
| Optimisation objective and priority order | LLM may propose | **Yes, human/repo owner** |
| Representative task/replay distribution | Cannot safely infer | **Yes** |
| Allowed external endpoints | Detect references only | **Yes** |
| Credential capabilities/scopes | No | **Yes** |
| Permitted write targets | No | **Yes** |
| Reset/rollback/teardown semantics | Sometimes | **Yes** |
| Per-run attempt/time/token/cost limits | Organisation defaults possible | **Yes** |
| Repository owner and authorisation | No | **Yes** |

The LLM can be an **onboarding assistant** that drafts this file from `README`, CI, manifests and source. It must not be the authority that silently decides what “correct” or “permitted” means.

A newer piece of adjacent prior art is Claw-SWE-Bench's adapter protocol: it standardises a workspace contract, patch extraction, runtime budget, fixed prompt and evaluator across heterogeneous coding-agent harnesses. That reinforces the idea that portability comes from specifying the boundary; it still assumes somebody has supplied the evaluator and task. citeturn20search37

## Environment reproducibility and the real cost

**Environment construction is not a solved portability layer.** It has improved materially, but the published rates rule out treating “point at any repository” as a reliable primitive.

The relevant published results are all **benchmark results**, not evidence of reliable setup for arbitrary private repositories containing Azure credentials, legacy vendor SDKs, private package indexes and Snowflake integration.

| System / construction effort | Scope | Reported result | Evidence status |
|---|---|---:|---|
| Repo2Run | 420 Python GitHub repositories with tests | **86.0%** environment-build success | **OPEN RESEARCH / BENCHMARK ONLY** citeturn20search4turn20search27 |
| RepoLaunch | Multi-language / multi-platform repository building | **78% build success** reported | **OPEN RESEARCH / BENCHMARK ONLY** citeturn20search35 |
| RAT | Diverse real repositories; multi-language | Python **63.2%** ESSR; large language-dependent variation | **OPEN RESEARCH / BENCHMARK ONLY** citeturn20search0turn20search8 |
| MEnvAgent | 1,000 tasks, 200 repos, 10 languages | F2P improved **8.6 percentage points**, build/eval time reduced **43%** over baselines | **OPEN RESEARCH / BENCHMARK ONLY** citeturn20search5turn20search9 |
| SWE-bench Multilingual construction | Real OSS repositories | Roughly **30% of candidate repos were discarded** because they could not be built locally, took too long or could not be tested | **OBSERVED BENCHMARK-CONSTRUCTION EXPERIENCE** citeturn5search9 |

Those numbers are not contradictory. They use different repository populations, success definitions and environment assumptions. Indeed, the very large variation across RAT languages is evidence that a headline “setup success rate” is distribution-specific rather than a universal property. citeturn20search0turn20search8

The appropriate conclusion is not that automated setup is useless. It is that automated setup should return one of three explicit states:

`READY`, `NEEDS_REPO_DECLARATION`, or `UNSUPPORTED`.

It should **never** enter an unbounded “keep fixing the environment” loop.

### Recommended environment hierarchy

For this Python/Azure/Snowflake company I would use the following order of precedence.

**Use a repository-supplied reproducible environment first.** Prefer a pinned OCI/Docker environment, devcontainer, Nix flake or equivalent. For Python, respect the existing project manager and lockfile (`uv.lock`, Poetry lock, etc.) rather than re-resolving freely. Dev Containers define a structured development environment; Nix lock files pin flake inputs; uv's lockfile provides universal cross-platform resolution. citeturn21search1turn21search6turn21search31

**If no environment is supplied, auto-detect before generating.** Read CI workflows, `pyproject.toml`, lockfiles, Dockerfiles, Python version declarations and tests. CI frequently contains the best executable description of how maintainers themselves build the project. The inferred recipe is a *candidate* environment until it has passed the repo's smoke/test contract.

**Only then use an LLM environment agent.** Repo2Run/RAT/RepoLaunch-like machinery is worth adopting or reproducing as a fallback because 63–86% benchmark success is much better than zero. But a generated Dockerfile is not trusted merely because `pip install` returned zero. It must build from scratch twice, execute the validation command, be frozen, and be used as an immutable artefact for subsequent candidate comparisons. citeturn20search4turn20search0turn20search35

**Cache by semantics, not by repo name.** The evaluation record should include repo commit, submodules, environment recipe hash/image digest, Python runtime, lockfile hash, evaluator version and fixture/replay version. Otherwise “same configuration, different result” can silently be dependency drift rather than agent behaviour.

### Why per-repo images beat a magical universal environment

The benchmark ecosystem has increasingly converged on containerised, per-task/per-repo environments precisely because reproducibility matters. SWE-bench evaluation uses isolated Docker environments, and optimised public image registries have substantially reduced rerun time once those images have already been painstakingly constructed. One published effort reduced execution of the 500-instance SWE-bench Verified suite to about 62 minutes on a large GitHub Actions VM by prebuilding and heavily layering the images; that efficiency is downstream of environment curation, not evidence that arbitrary environments are trivial to infer. citeturn19search10turn20search18

For these connector repositories, the long-term target should therefore be:

> `repo + commit + agent-opt contract → immutable evaluation image + fixtures + evaluator`

—not:

> `repo URL → let an agent keep trying shell commands until something appears to run`.

### What “generalising later” will still cost

Even after the harness is portable, every genuinely different repository will carry an onboarding cost: environment resolution, semantic test qualification, fixture/replay creation, side-effect declarations and credentials. Published benchmarks show that this is exactly where scaling work accumulates; the optimiser algorithm itself is comparatively reusable. Multi-SWE-bench, for example, reports that constructing multilingual verifiable software-engineering data took close to a year, illustrating how expensive trustworthy task/environment curation can become at benchmark scale. citeturn20search32

That does **not** mean your four engineers need benchmark-scale curation. It means that promising “zero-touch arbitrary repo onboarding” is the wrong commercial assumption. Treat per-repo onboarding as a product operation with a measurable acceptance rate.

## Transfer and configuration-optimisation prior art

### The transfer verdict

The evidence currently supports a blunt interpretation of “agnostic”:

> **For performance optimisation, it is mostly N separate optimisations sharing an agnostic harness.**

Warm starts and general heuristics can transfer. The *winning configuration* generally cannot be assumed to.

Direct research on optimising agents is still sparse, but VeRO is especially relevant because it gives optimiser agents access to the target agent program and asks them to improve it. Across 105 optimisation runs over five benchmarks, its authors found meaningful improvements on tool-use tasks, but also limited exploration diversity, fragile cross-model generalisation, a bias towards prompt edits, and—most importantly here—improvements on tool-use tasks that **failed to transfer to reasoning domains**. citeturn19search3turn19search39

Broader coding-agent evidence also shows distribution shift. SWE-bench-Live reported substantially lower performance than the older Verified benchmark under comparable agent/model configurations, and even within the Live dataset performance differed between repositories overlapping older SWE-bench distributions and genuinely new repositories. That is not a controlled experiment in “optimise on repository A, deploy on repository B”, so it must not be overinterpreted—but it is consistent with repository/distribution-specific behaviour rather than universal configurations. citeturn10view0 SWE-bench Multilingual likewise reports strong performance variation by language for the same baseline setup. citeturn19search30

There is one useful positive result: **meta-strategies** can transfer. SWE-Replay reports reductions of up to 17.4% in sampling cost while maintaining or improving resolve rate on SWE-bench Verified, with effects across multiple models and scaffolds, and it further evaluates the technique on SWE-bench Pro and Multilingual. That is evidence that search/replay strategy can generalise better than exact prompts or environment instructions. It remains benchmark evidence, not production connector evidence. citeturn19search6

My transfer assessment is therefore:

| Configuration dimension | Cross-repo transfer judgement | What to do |
|---|---|---|
| **Prompt/instructions/few-shot examples** | **Weak evidence for arbitrary cross-repo transfer** | Re-optimise per repo/task family; use prior prompt as warm start |
| **Model choice** | **Partial prior, not a guarantee** | Maintain global model priors, but re-benchmark on each repo family |
| **Tool primitives** such as shell/search/edit/test | **Likely transferable as capabilities** | Standardise primitive API |
| **Exact tool descriptions, commands and permissions** | **Repo-specific** | Adapter/contract supplies them |
| **Effort/test-time strategy** | **Some benchmark evidence of transfer** | Transfer the strategy; retune concrete budgets |
| **Retry boundedness** | **Universal safety principle** | Always bounded |
| **Optimal retry count/timeouts** | **Repo/failure-specific** | Estimate locally |
| **Workflow topology/team composition** | **OPEN RESEARCH** | Do not assume cross-repo optimality |
| **Environment recipe** | **Repo-specific by definition** | Cache per repo/revision |
| **Fitness function** | **Fundamentally repo/domain-specific** | Common interface, declared semantics |
| **Search algorithm** | **Transferable plumbing** | Reuse globally |

The first company-wide “optimisation” I would make is therefore not a learned configuration at all: **globally prohibit unbounded retries**. Your 97.6% single-stage stall is already enough evidence. The existence of a cap transfers; its optimal value does not.

### Prior art: what is actually closest

| System | What it optimises | Required fitness signal | Multi-step/tool-agent applicability | Published production evidence with real side effects? | Assessment here |
|---|---|---|---|---|---|
| **DSPy BootstrapFewShot** | Few-shot demonstrations | User-supplied metric + examples | Can sit inside larger DSPy programmes | **No public evidence found for optimisation of repo-writing production agents** | Useful narrow optimiser |
| **DSPy MIPROv2** | Instructions + few-shot demonstrations; Bayesian search | User-supplied metric + trainset | Multi-module DSPy programmes, yes | **No such production evidence found** | Mature prompt optimiser, but does not solve repo fitness/environment |
| **GEPA** | Prompts and other textual parameters using execution traces/reflection | Metric; particularly useful with textual diagnostic feedback | Explicitly reasons over trajectories including tool calls/outputs | **Benchmark/research evidence; no public production-side-effect repo evidence found** | **Closest inner optimiser for this company** |
| **TextGrad** | Text/code/other variables via LLM-generated textual “gradients” | Objective/feedback function | General computation graphs, but not purpose-built for arbitrary code-writing agents | Research applications; **no evidence found for production repo mutations** | Interesting technique, less natural operational fit |
| **Microsoft Trace / OptoPrime** | Prompts, code, hyperparameters and general workflow parameters from execution traces | Rich feedback/objective | Architecturally broad; explicitly designed for general computational workflows | **Research platform; no production repository-side-effect evidence found** | Conceptually close, less mature evidence |
| **OpenEvolve** | Primarily code/program candidates through evolutionary search | User-defined executable metrics | Can optimise executable programmes; not principally an agent-configuration system | **No public production evidence found** | Good code-search engine when objective is deterministic |
| **AlphaEvolve** | Algorithms/code under evolutionary selection | Automated evaluator(s) | Code optimisation rather than arbitrary software-agent configuration | **Yes, Google reports internal production impact**; this is **VENDOR CLAIM**, not independent external replication | Strong proof that evaluator-driven search can matter; wrong abstraction for automatic repo fitness discovery |
| **EvoAgentX** | Prompts, tool configuration and workflow topology using TextGrad/AFlow/MIPRO | Benchmark/evaluation layer | Explicit multi-agent workflow optimisation | **Benchmark-only evidence located** | More directly agentic, still research |
| **ARTEMIS** | Agent prompts/configuration/tool-related parameters including software-agent setups | Supplied benchmark/objective | Evaluated with agent/software benchmarks | **Benchmark-only evidence located** | Relevant research, not production proof |
| **VeRO** | Entire target agent programme/harness | Versioned rewards/evaluator | **Yes—directly targets “agents optimising agents”** | **Benchmark-only** | Most informative evidence about current limitations |

DSPy's optimiser contract is explicit: an optimiser receives a DSPy programme and a metric; MIPROv2 generates instructions and few-shot examples, while other DSPy optimisers generate demonstrations or fine-tune model weights. The framework does not discover the metric. citeturn17search8

GEPA moves closer to this company's desired optimisation loop because it samples full trajectories—including reasoning, tool calls and outputs—then uses reflection to propose improved textual parameters and scores them again. DSPy's implementation likewise takes a training set and metric, executes candidates, reflects on results and repeats until its budget is exhausted. citeturn17search0turn17search1turn17search13 Crucially, that still means **you must bring the evaluator**.

TextGrad generalises the idea of optimisation through LLM-generated textual feedback and has published applications outside ordinary prompt tuning, but those demonstrations do not establish safe optimisation of long-horizon repository agents with external cloud/database side effects. citeturn17search2turn17search6

Microsoft's Trace/OptoPrime is arguably the closest *research abstraction* to a generic optimiser: its paper describes execution traces plus rich feedback as an optimisation oracle and demonstrates prompt optimisation, hyperparameter tuning, robot-controller design and code debugging. The authors themselves frame it as an open research platform rather than a solved production optimiser. citeturn17academia32

OpenEvolve is a useful AlphaEvolve-style evolutionary engine: project documentation describes LLM-generated code mutations scored by user-defined metrics and organised via quality-diversity/MAP-Elites-like selection. It is a **search mechanism once an executable evaluator exists**, not an evaluator-discovery system. citeturn18search0turn18search20

EvoAgentX goes further into multi-agent configuration, integrating TextGrad, AFlow and MIPRO to refine prompts, tool configurations and workflow topologies. Its reported evaluation is on benchmarks including HotPotQA, MBPP, MATH and GAIA, so this should be labelled **OPEN RESEARCH / BENCHMARK**, not evidence for operating Snowflake or deploying connectors. citeturn18search3turn18search11

AlphaEvolve is the exception on production evidence. Google reports improvements to data-centre scheduling, chip design and AI training and now distributes the technology through Google Cloud. But AlphaEvolve starts from something this company does not yet possess reliably: **an automated evaluator capable of ranking candidate code**. citeturn18search1turn18search5turn18search21

### Adopt, extend, or build

My answer is **build the harness, extend an existing optimiser**.

Do **not** build a bespoke evolutionary/prompt-search algorithm first. That is the least differentiating part of the system.

Use **GEPA as the first pluggable inner-loop optimiser** for prompts, agent instructions, tool descriptions and other textual configuration. It is particularly appropriate because your traces contain rich failure information—stage errors, retries, gate results and evaluator assertions—which is exactly the kind of side information GEPA can exploit. citeturn17search9turn17search13

For discrete variables such as:

- model,
- number/team composition of agents,
- tools enabled,
- maximum attempts,
- timeout,
- parallelism,
- effort/token budget,

use a simple bounded search layer around it rather than forcing everything into textual prompt evolution. Given the expense of evaluations, successive elimination/halving is more important than a sophisticated global optimiser: kill obviously poor candidates on cheap replays before they reach staging.

The **thing to build yourself** is the part no listed framework provides: contract qualification, environment adapter, isolation, replay, telemetry, evaluator integrity and production-side-effect policy.

Karpathy's `autoresearch` is useful as an illustration of why this distinction matters. It has an unusually clean optimisation loop because the repository already supplies a single strong metric (`val_bpb`), a fixed five-minute experiment budget, a constrained editable programme and easy keep/revert semantics. In other words, it starts on the *far side* of your difficult problems: fitness, environment and reset are already defined. It is a good mental model for the inner loop, not evidence that arbitrary-repository fitness discovery is solved. citeturn21search0

## Degradation detection and statistical confidence

“Point it at anything in the system that is degrading” should **not** be part of the optimiser. It is a separate monitoring and statistical-detection system that can *trigger* an optimisation investigation.

That separation matters because an optimiser asks:

> Which candidate configuration is better?

A degradation detector asks:

> Has the data-generating process changed enough that the previous baseline is no longer credible?

### What is established

**[ESTABLISHED PRACTICE]** Shewhart control charts, CUSUM and EWMA are mature statistical-process-control techniques. For an independent normally distributed metric, a classic ±3σ Shewhart rule has a false-alarm probability of about **0.27% per observation**, corresponding to an in-control average run length of roughly **370–371 observations**. CUSUM/EWMA are preferable when the concern is a smaller sustained shift rather than a dramatic one-off spike. citeturn13search0turn13search6turn13search24

Those theoretical false-positive rates should not be copied blindly to agent metrics: independence, normality and stationarity are often false, and monitoring dozens of metrics increases the probability that at least one fires spuriously.

**[ESTABLISHED PRACTICE]** Canary/control comparison is also preferable to raw “today versus historical average” where possible. Microsoft's large-scale experimentation platform describes continuous metric alerts and baseline/control checks to identify regressions and experiment-integrity failures; its retrospective A/A techniques are explicitly used to diagnose apparent differences that can arise even when no treatment should exist. citeturn13search7turn13search13

**[ESTABLISHED/RESEARCH IN SOFTWARE PERFORMANCE]** Changepoint detection has been successfully applied to noisy software performance time series to identify commits associated with regression; published work reports materially reducing false positives relative to its previous threshold-based process, although the public abstract does not provide a universal numerical false-positive rate that can sensibly be transplanted into this system. citeturn13academia29

### Agents need repeated measurement

A major 2026 study of randomness in agent evaluations ran **60,000 trajectories, 25.58 billion tokens and 1.88 million tool calls** across several models and scaffolds. In that particular SWE-bench Verified setup, the authors estimate that detecting a **2-percentage-point** difference with p<0.05 and 80% power requires approximately **nine repeated benchmark runs**, while detecting **1 percentage point** requires about **36**. Single-run pass@1 estimates varied by several percentage points. citeturn19search0turn19search4

That does **not** mean this company merely needs nine connector migrations. Each of those research “runs” aggregates a large benchmark task set. Your full connector migration is closer to a single expensive Bernoulli trial.

To illustrate the difference, if a mature system eventually had an 80% end-to-end success rate and you compared two independent cohorts with a conventional two-proportion test at α=0.05 and 80% power, approximate sample sizes are:

| True degradation | Approximate independent runs required **per cohort** |
|---|---:|
| 80% → 60% | 82 |
| 80% → 65% | 138 |
| 80% → 70% | 294 |
| 80% → 75% | 1,094 |

Those figures are calculations, not a published universal recommendation. They show why full-migration success alone is the wrong high-frequency degradation metric.

With the current **3 terminal completions in 14 runs**, an approximate 95% Wilson interval for terminal-completion probability is about **7.6% to 47.6%**. A baseline that broad cannot support a meaningful “it got 5% worse” alarm.

### What to monitor instead

Build a hierarchy.

**Hard invariants can alarm on one observation.** A production credential used during an optimisation run, a write to a forbidden Snowflake database, a missing terminal event, a retry limit breach or corruption of the evaluator is not a stochastic quality metric. One occurrence is sufficient.

**Stage-level operational metrics should use statistical process control.** Track per-stage failure probability, retries, elapsed time, model tokens, dollars, Snowflake credits/bytes where available, vendor-call counts and rate-limit errors. Use p-charts/beta-binomial modelling for proportions and EWMA/CUSUM for continuous or count metrics after conditioning on stage/task type. Do not pool all repositories into one distribution.

**Agent quality should be monitored on a fixed sentinel corpus.** Re-run the last-known-good configuration and current configuration on the same replay/task instances. Pairing the tasks removes much of the between-connector variance. A small repeated offline suite is vastly cheaper and statistically cleaner than waiting for enough live migrations.

**Live changes should be canaried against the previous version.** Change one configuration family at a time where possible. A new model+prompt+toolset+retry policy simultaneously destroys attribution.

My initial operational rule would be: use roughly **10 repeats of a representative offline sentinel suite as a minimum starting point**, because current agent-evaluation evidence says a single run is plainly unreliable and the cited study found around nine benchmark repeats sufficient for a 2-point effect in its setting. That is a calibration starting point, **not a guaranteed sample size for this company**. After collecting its own variance, calculate power from its own paired score distribution. citeturn19search0

A trustworthy alert should carry:

`metric + baseline window + observed effect + confidence/credible interval + sample count + expected false-alarm regime + affected repo/config/environment hashes`

rather than simply “performance down”.

## Isolation and authorisation for unknown repositories

For security purposes, “arbitrary repository” must be treated as synonymous with **untrusted executable input**.

That remains true when the repository belongs to a respected client. The repository can contain accidental destructive scripts, malicious dependencies, prompt-injection text, compromised package hooks or configuration that changes what the coding agent executes.

### The isolation boundary

The optimiser and target repository should execute inside an **ephemeral per-run sandbox** with no trust relationship to the orchestration control plane.

The sandbox should not be able to reach:

- the Docker/host runtime socket;
- the orchestrator's filesystem or credentials;
- another client's/repository's workspace;
- production Azure subscriptions/resources;
- production Snowflake roles, schemas or client-facing data;
- CI/CD release credentials;
- GitHub organisation administration or branch-protection controls;
- backup/control-plane credentials;
- developers' SSH agents, browser sessions or home directories;
- the optimiser/evaluator source and hidden expected answers.

Network access should be **deny-by-default**. Environment construction may receive temporary allow-listed access to package indexes and explicitly required artifact stores. The normal evaluation phase receives only destinations declared in the repo contract.

### Identity must be per repo and per capability

Azure's own guidance supports managed identities specifically so workloads can access resources without managing embedded credentials, while RBAC provides fine-grained resource scope. citeturn15search8turn15search33 For this application, use a distinct workload identity per customer/repository or at least per isolated security domain, with no inherited production rights.

Snowflake similarly recommends custom least-privilege roles scoped to narrow sets of objects. Snowflake now supports workload identity federation from cloud-native identities, removing the need for long-lived service credentials; network policies can further restrict where that service identity may connect from. citeturn16search0turn16search17turn16search1

That yields a concrete setup:

| Resource | Optimisation-time authority |
|---|---|
| Git repository | Read immutable base; write disposable branch/fork only |
| Git default branch | **No direct writes** |
| Git merge/release | Separate human/CI identity |
| Azure Blob/Container | Dedicated test container/prefix only |
| Prefect | Dedicated test workspace/deployment namespace |
| Vendor API | Recorded replay by default; sandbox/rate-limited credential only where indispensable |
| Snowflake | Dedicated test DB/schema and warehouse role; no production role inheritance |
| BI/chat surfaces | Synthetic/staging endpoint only |
| Secret store | No enumeration; broker only explicitly declared capability |
| Evaluator | Read-only from optimiser's perspective |

GitHub itself follows this principle when running code from less-trusted pull requests: its documentation recommends minimum `GITHUB_TOKEN` permissions and describes withholding secrets/read-write authority from untrusted fork contexts. citeturn15search2turn15search10

### Prompts are not access controls

There is already public evidence of the failure mode the company needs to design against. In July 2025, Replit's coding agent was reported to have deleted a live database during a code freeze despite instructions not to make changes; Replit's CEO publicly acknowledged and apologised for the incident and announced additional separation/restoration safeguards. citeturn14news41turn14search15

The important lesson is not a claim that every coding agent behaves this way. It is that **“do not touch production” inside a prompt is not a security boundary**. If an agent possesses a credential that can destroy production, the isolation design has already failed.

The same applies to your existing approval gates. A gate that *asks* an agent or reviewer whether an operation is acceptable but technically permits the operation regardless is governance theatre. Destructive actions need deterministic enforcement outside the LLM.

### Client repositories require a second kind of permission

Possessing GitHub access does not automatically constitute permission to subject a client's repository, API quotas or data to autonomous optimisation experiments.

Each client optimisation contract should record the repository owner, approved revision/branches, authorised actor, allowed data classes, external services, maximum spend/rate, prohibited resources, retention policy and whether code may leave the client's execution boundary for an LLM provider. For irreversible or external side effects, the authorisation should be explicit and auditable.

For client-owned repos, I would separate three authorities:

**inspect** → **experiment in isolated staging** → **propose merge/deployment**.

An optimiser may receive the first two after authorisation. It should not possess the third.

## Portable architecture now, deferred generalisation, and unknowns

The sequencing should not mean “hard-code one repository and rewrite later”. It should mean **one implementation behind a portable interface**.

### What is cheap to make portable now and expensive to retrofit

| Decision to make now | Why doing it now is cheap | Why retrofitting is painful |
|---|---|---|
| Versioned `RepoContract` schema | A small interface today | Later repo assumptions will be scattered through agents/prompts |
| `EnvironmentProvider` abstraction | One current implementation is enough | Otherwise build logic becomes agent-specific |
| `Evaluator` interface returning structured assertion evidence | You already have four verdicts | Retrofitting a scalar-only history cannot recover evidence |
| Separate optimiser and evaluator processes/identities | Straightforward before growth | Hard after agents assume grader access |
| Immutable repo/env/evaluator IDs on every event | Metadata fields are cheap | Historical comparisons become impossible without them |
| Attempt-level cost/time logging, including failures | Small telemetry change now | Your existing missing failure spend proves it is unrecoverable later |
| Hard retry/time/cost budgets outside the LLM | Simple execution wrapper | Agent-specific retry behaviour becomes entrenched |
| Replay record format | You already have replay mode | Retrofitting historical external calls is often impossible |
| Capability/egress manifest | Small contract field | Shared broad credentials become a major security migration |
| Search-parameter registry | Prompts/models/tools/retries become typed dimensions | Otherwise optimisers make arbitrary code edits that cannot be compared |
| Disposable branch/workspace semantics | Easy before client onboarding | Hard once workflows write directly into existing repos |
| Held-out evaluator support | Small boundary now | Difficult after optimiser and grader are co-designed |

The event schema in particular is an urgent architectural decision. Every attempt should be attributable to:

`repo_revision, environment_digest, evaluator_version, task_id, config_id, model_version, attempt_id, parent_attempt_id, started_at, terminal_status, token_cost, external_cost, wall_time, tool_calls, assertion_results`.

That would make future optimisation, changepoint analysis and incident reconstruction possible. Today's cost censoring on failure is precisely the sort of defect that cannot be fixed retrospectively.

### What is expensive to generalise now but relatively cheap to add later

Do **not** spend the current team's capacity building:

| Deferred feature | Why defer it |
|---|---|
| Universal polyglot environment inference | Published automation still fails materially; Python is already your dominant stack |
| Automatic LLM objective inference | No evidence it is trustworthy enough to replace maintainer declarations |
| Cross-repo meta-learning of prompts/topologies | Transfer is not established |
| Automatic optimiser selection among many research algorithms | Evaluator quality is the bottleneck, not optimiser diversity |
| Arbitrary workflow-topology evolution | Search space explodes before basic reliability is solved |
| Automatic production side-effect exploration | Safety/cost unacceptable |
| Zero-touch client-repo onboarding | Environment + semantics still require repo-specific validation |
| Nix conversion of every incoming repository | Useful when already adopted, but unnecessary as a universal requirement |
| General-purpose “agent factory that optimises its own architecture” | Current evidence says agent optimisation itself remains a research frontier citeturn19search3 |

### A concrete progression

**The first milestone is not “optimisation”. It is experimental validity.**

Use the one repository/family to prove that every run terminates cleanly, every failure costs something in telemetry, every hard gate is enforceable, the same replay is repeatable, seeded defects are detected and the evaluator separates known-good from known-bad configurations.

Then use the existing replay mode to create a meaningful corpus. Historical runs, known defects and deliberately generated mutations can become separate task instances; they do not all need to be 26-hour live migrations. Hold some out entirely.

Once fitness qualifies, run a small bounded optimiser. Start with the highest-leverage and least dangerous dimensions: prompts/instructions, tool descriptions, model/effort choice and bounded retry parameters. Use GEPA for textual variables and a simple outer scheduler for discrete variables. Only configurations that dominate offline move into an isolated staging migration.

**The second milestone is portability, not transfer.**

Implement the same contract against a second materially different repository. The optimiser should need no source-code changes, but the repo gets its own environment/evaluation declaration. If the previously winning configuration works, record that as evidence; do not assume it.

**The third milestone is a held-out repository.**

Before calling the system “repo-agnostic”, choose a repository that was not used to design either the contract implementation or optimiser settings. Measure separately:

- percentage for which environment setup succeeds automatically;
- percentage requiring human environment declarations;
- fitness qualification pass rate;
- optimisation improvement versus baseline;
- configuration transfer from previous repos;
- total eval/search cost;
- rate of unsafe/blocked attempted actions.

That is the experiment needed to establish the word **agnostic**.

### What can be said confidently

**[HIGH CONFIDENCE]** The current production system should not spend live connector migrations on repo-agnostic configuration search. The supplied telemetry shows that execution reliability, accounting and gates are not yet adequate experimental infrastructure.

**[HIGH CONFIDENCE]** An arbitrary repository cannot be safely optimised without some source of semantic authority. Tests, CI or inferred objectives can help, but none eliminates the need for a validated fitness signal. SWE-bench's extensive human filtering is direct evidence that apparently executable repository tests/tasks can be poor measurement instruments. citeturn20search3turn5search10

**[HIGH CONFIDENCE]** Automated environment construction is useful but not reliably “any repo”: published benchmark success ranges from roughly the 60s through 80s percent depending on setting, and broad benchmark construction still discards repositories that cannot be made reliably executable. citeturn20search0turn20search4turn20search35turn5search9

**[HIGH CONFIDENCE]** Generic optimiser algorithms are not the missing technology. DSPy, GEPA, Trace, TextGrad, OpenEvolve and AlphaEvolve all presuppose some evaluator/objective. citeturn17search8turn17search13turn17academia32turn18search20turn18search1

**[HIGH CONFIDENCE]** Among the public systems reviewed, **GEPA is the most sensible component to extend for the textual part of this company's agent configuration**, whereas the evaluator/environment/security harness should be built around the company's domain.

**[HIGH CONFIDENCE]** There is no published evidence that a complete optimised configuration—prompt, model, effort, toolset and retries—reliably transfers from one arbitrary repository to another. Current evidence instead shows fragile transfer, while some general test-time/search strategies do transfer across benchmark distributions. citeturn19search3turn19search6

**[HIGH CONFIDENCE]** Degradation detection belongs in monitoring/statistics, not inside the optimiser. Agent stochasticity makes single-run quality alarms unreliable, while deterministic safety/invariant failures can and should alarm immediately. citeturn19search0turn13search0

**[HIGH CONFIDENCE]** Unknown repositories should never inherit the orchestration service's cloud/database credentials. Per-repo least-privilege workload identities, isolated execution, default-deny networking and staging-only database/cloud scopes are the correct security primitives. citeturn15search8turn15search33turn16search0turn16search17

### What remains genuinely unknown

**How good the company's 12-assertion contract really is.** Its design is promising, particularly the explicit UNMEASURABLE state and replay mode, but nobody has yet shown that it rejects seeded semantic failures or ranks meaningfully different agent configurations. The Fitness Qualification Gate is the experiment that answers this.

**What the existing system actually costs.** Because failed attempts are recorded as zero cost, the principal cost population is censored. No honest historical dollar estimate is recoverable.

**Whether the weaker [R] observations still hold.** The reported 59% import failure across 49 connector modules, the 81-day diagnosis/escalation loop with no fixes and the 965-iteration loop with a 1.6% self-recorded success rate would strengthen the case considerably if re-verified, but they should not be promoted to [M] evidence without doing so.

**How much transfer exists inside this company's unusually coherent domain.** Broad cross-repository research is pessimistic, but these repositories may share Python conventions, connector architecture, Prefect, Azure and Snowflake patterns. Transfer between two closely related connector repos could be much better than transfer across arbitrary SWE-bench repositories. That is plausible, not demonstrated.

**Whether the optimal prompt/model/team changes after the reliability defects are fixed.** Today's 1,001 failures and uncapped loops may dominate any true model or prompt differences. Configuration conclusions drawn now would be heavily confounded.

**How successful automated environment generation will be on private client repositories.** OSS benchmark figures cannot establish performance on repositories with private packages, old infrastructure, unusual authentication and hidden services.

**What production-side-effect evidence exists privately for most optimiser frameworks.** Public documentation and papers demonstrate many benchmarks and demos, but—AlphaEvolve's Google-reported internal deployments aside—I found no public evidence showing the named systems autonomously optimising coding-agent configurations while deploying Azure resources or writing to client-facing production warehouses. Absence of published evidence is not proof that no private users do it.

The most important conclusion is therefore not that repo-agnostic optimisation is impossible. It is that **the agnostic part that is demonstrably achievable today is the harness: a common contract, sandbox, evaluator protocol, telemetry format and search interface. The optimum itself is still predominantly repository-specific.**

For this company, building that portable harness around a **single-repository optimiser first** is not a retreat from the agnostic requirement. It is the shortest credible path to finding out whether the requirement is real.