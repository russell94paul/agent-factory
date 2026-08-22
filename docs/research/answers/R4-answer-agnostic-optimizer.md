# Repo-agnostic agent optimisation: feasible as infrastructure, premature as an optimisation target

## Verdict and sequencing

**Verdict: build a single-repository optimiser first, but put it behind repository-agnostic interfaces from day one. Do not build or market a genuinely repo-agnostic optimiser yet.**

The distinction is important. Three different things are being called “agnostic”:

| Meaning of “agnostic” | State of the art | Verdict |
|---|---|---|
| The **search algorithm** can optimise arbitrary parameters given an evaluator | **Established** | Yes. DSPy/GEPA, evolutionary search, Bayesian optimisation and related systems can do this. They all assume an objective or metric already exists. citeturn13search24turn20search5 |
| The **control plane** can attach to many repositories through a common environment/task/evaluator interface | **Emerging but demonstrated in benchmarks** | Yes. SWE-agent and newer Claw-SWE-Bench-style adapters show the pattern. citeturn17search6turn19search0 |
| The system can be pointed at an **arbitrary unfamiliar repository, discover what “better” means, build it reliably, and find a configuration whose improvement transfers to other repos** | **Open research** | No convincing demonstration found. Current systems require an evaluator, task specification, environment or some combination of all three. citeturn13search26turn14search0turn20search6 |

That third interpretation is the company's stated requirement. **The honest answer is that it does not work yet in the zero-configuration sense.** A useful system can be repository-agnostic in plumbing, but it cannot be repository-agnostic about semantics: somebody or something must ultimately say what constitutes correct behaviour, what side effects are permitted and how to run the repository.

### Why the present system is not ready for search

**Observed — company data [M].** The immediate problem is not lack of an optimiser. It is that the current experiment is not yet a reliable experiment:

- 3 of 14 runs produced a terminal completion event.
- Exactly one connector has a recorded successful end-to-end run.
- One stage consumed 92,817 of 95,098 seconds of the longest successful run because retries had no cap.
- There were 1,001 stage failures against 165 completions.
- 22 gates approved and none refused; five of seven have no programmatic check.
- Failed attempts have no recorded cost.

Those observations make optimisation dangerous for two separate reasons. First, an optimiser cannot distinguish a better agent from a configuration that merely happens to encounter fewer infrastructure failures. Second, optimisation pressure will actively find weaknesses in gates and evaluators. That is not hypothetical: recent work strengthening SWE-bench tests found that **77% of its 500 Verified instances had at least one semantically altered variant that survived the original tests**, and stronger tests reduced top-agent resolved rates by 4.2–9.0 percentage points. A separate 2026 analysis rejected 19.78% of 11,041 supposedly solved patches after strengthening the tests. These are benchmark results, but they demonstrate exactly the failure mechanism: optimise against an under-constrained oracle and apparent performance rises while semantic correctness does not. citeturn16search0turn16search5

**The cost of searching now is already prohibitive even before dollar cost is considered.** Using the [M] median of 26.4 hours among completed evaluations:

| Naive search | Full migrations | Evaluation time | Ideal wall time at four-way parallelism |
|---|---:|---:|---:|
| 10 configurations × 3 replicates | 30 | 792 agent-hours | 8.25 days |
| 20 configurations × 3 replicates | 60 | 1,584 agent-hours | 16.5 days |

That assumes successful 26.4-hour evaluations, perfect parallelism and no contention. It excludes the 1,001 failed attempts whose monetary cost is presently lost. Even using the much lower 11.3-hour median across all runs, 60 evaluations are 678 agent-hours. Until every attempt records model, token, Azure, warehouse and other attributable cost whether it succeeds or fails, **there is no honest dollar estimate of optimisation cost**.

The sequence I would use is therefore:

**First, stabilise execution.** Put central hard limits on stage attempts, wall time, token spend and external-system operations; make every run end in a terminal state; account for every attempt; and force gates to exercise both accept and reject paths.

**Then build a single-repository evaluator.** Use the repository containing the one proven migration, create a challenge corpus around it and qualify the 12-assertion contract before searching anything.

**Then optimise a small configuration surface.** Start with parameters that can safely be replayed or shadow-evaluated: retry policy, stopping policy, routing, selected prompt fragments and perhaps model/effort. Do not initially expose repository code, environment construction and evaluator logic themselves to the same optimiser.

**Only then add a second genuinely different repository.** The second repository is the portability test. If onboarding it requires changing optimiser core code rather than supplying another repository contract/adapter, the abstraction is wrong. If it merely needs a different contract, environment image and evaluator, that is expected and not a failure of the architecture.

The goal for the next phase should therefore be **“one working optimiser, many-repo-shaped interfaces”**, not “optimise anything”.

## Fitness discovery and qualification

### There is no objective-free optimiser

This is the central conceptual limit. Every serious optimisation system reviewed ultimately assumes an objective. DSPy explicitly defines its metric as the function that converts a prediction into the score its optimisers pursue; BootstrapFewShot accepts traces according to a supplied metric; GEPA takes a training set and metric and uses feedback from that metric to evolve instructions. citeturn13search0turn13search6turn13search26

AlphaEvolve likewise combines code generation with automated evaluators; Trace takes an execution trace plus objective feedback; TextGrad requires an objective function. Their generality is about **how they search after the evaluator exists**, not about discovering the true evaluator of an unknown software system. citeturn20search0turn20search1turn20search2

I found **no accepted general procedure that looks at an arbitrary repository and reliably discovers its intended business objective**. LLMs can propose candidate objectives from README files, CI, tests, issues and source, but treating that inferred description as authoritative fitness is still open research. For a data connector in particular, source code cannot reliably tell an outsider whether the real requirement is “never miss a record”, “never duplicate a record”, “stay under a vendor quota”, “finish by 06:00”, “preserve an undocumented client transformation”, or some lexicographic combination of these.

### Comparing the possible sources of fitness

| Fitness source | What it really establishes | Portability | Main failure | Recommended role |
|---|---|---|---|---|
| **Repository tests** | Behaviour asserted by existing tests | High auto-detectability | Weak tests reward incorrect patches | Useful component, but qualify with mutation/challenge testing |
| **CI green/red** | Whether the configured CI workflow currently passes | Very high | Coarse binary signal; may be decorative, flaky or unrelated to business outcomes | Health check, **not** sufficient fitness on its own |
| **Maintainer-declared contract** | Explicit intended outcomes, constraints and permissions | Requires small amount of hand authoring | Maintainer must know and state the objective | **Best canonical source of truth** |
| **Benchmark harness** | Performance over an explicit task distribution with a verifier | Strong once built | Expensive and repository-specific to construct | Best optimisation/evaluation substrate |
| **LLM-inferred objective** | Model's hypothesis about maintainer intent | Highly automatable | Confidently infers the wrong goal; cannot infer consent | Use to *draft* a contract, never silently approve it |
| **Human preference labels** | Human judgement of comparative quality | Broad semantic coverage | Expensive/noisy; poor oracle for exact data correctness | Secondary metric for subjective agent behaviour, not connector integrity |

**Established practice.** Tests and executable contracts are powerful when they actually constrain behaviour, but a green suite is not proof that the suite is discriminating. The recent SWE-bench work is unusually relevant here: even a human-filtered benchmark built around real developer tests contained substantial under-constrained behaviour, and stronger tests materially changed both scores and rankings. citeturn16search0turn16search5turn16search19

**Open research.** There is no universally accepted “fitness-fitness test” for arbitrary agent/repository optimisation. There *are* established components—mutation testing, negative controls, metamorphic testing, repeatability measurement, holdout evaluation and statistical power analysis—which can be assembled into one. The company should do exactly that rather than assuming a scalar metric is valid because one exists. Metamorphic testing in particular is a recognised response to the oracle problem: rather than needing the exact expected answer for every input, one checks relations that correct behaviour must preserve under controlled transformations. citeturn16search3turn16search14

### The pre-search fitness qualification gate

I recommend introducing a formal **Fitness Qualification Gate**. That name and the numerical thresholds below are a design recommendation, **not an industry standard**.

No optimiser gets a search budget until its proposed fitness function passes five tests:

| Qualification | Test before optimisation | Abort condition |
|---|---|---|
| **Repeatability** | Run the identical baseline/configuration repeatedly at the same pinned environment and on repeated stochastic seeds; estimate within-configuration variance | Environmental/flaky variance is of the same order as the improvement you intend to detect |
| **Known-bad sensitivity** | Inject controlled faults and replay historical failures | Grossly wrong variants are frequently scored equal to baseline |
| **Known-good invariance** | Apply no-op or semantics-preserving changes | Harmless changes substantially move the score |
| **Discrimination** | Score baseline plus a small deliberately diverse challenge population | Nearly all candidates have the same verdict/score or between-config differences are smaller than replicate noise |
| **Holdout validity** | Keep some assertions/tasks inaccessible to the search loop | Search gains disappear on holdout or exploit exposed assertions |

For this company's connectors, the known-bad challenge set should not be generic Python mutations alone. It should deliberately break **pagination, incremental cursors/watermarks, idempotency, duplicate suppression, schema conversion, null handling, time zones, vendor-rate-limit handling, partial-batch recovery, Azure object naming, Snowflake reconciliation and retry termination**. The historical restart loop itself should become a challenge case: any configuration that permits an equivalent unbounded loop must fail fitness regardless of whatever positive score it accumulates elsewhere.

A useful diagnostic statistic is the evaluator's ability to separate known-good from known-bad challenges. AUC, pairwise ordering accuracy or a mutation-kill rate would all work. As a **local policy rather than a literature standard**, I would require something approximately like ≥90% detection of high-severity injected faults and ≤5% rejection of deliberately semantics-preserving controls before authorising an expensive live search. The precise thresholds should depend on the severity of a false pass.

The test should also explicitly track **UNMEASURABLE** as its own rate. The company's existing decision that UNMEASURABLE does not count as PASS is correct. Do not collapse it into FAIL either: a configuration that makes correctness increasingly unobservable is a different and important failure mode.

### How the existing twelve-assertion contract should score

Do **not** start by averaging twelve assertions, cost and latency into one weighted number. That makes pathological trade-offs possible—for example, a cheap configuration that never performs the migration could beat an expensive successful configuration.

Use a **lexicographic constrained objective**:

**Hard constraints first:** authorised side effects only; no uncapped retries; required correctness assertions measurable; no critical FAIL; run terminates.

**Then outcome quality:** successful end-to-end completion and data-contract correctness over the task corpus.

**Then reliability:** variance, retries, recovery behaviour and UNMEASURABLE frequency.

**Only among configurations that satisfy those constraints:** minimise cost, elapsed time, model calls and unnecessary tool use.

That mirrors how AlphaEvolve-style systems succeed in constrained domains: the automated evaluator determines which candidates are admissible before optimisation pressure is applied. AlphaEvolve's evidence is a **vendor/self-reported success in evaluator-rich algorithmic domains**, not evidence that an arbitrary repository's evaluator can be discovered automatically. citeturn20search2turn20search34

One limitation of the company's replay mode needs to be made explicit. A recorded trajectory is excellent for testing **scorer changes, gate logic, termination logic and some retry policies**, but it is not a general counterfactual evaluator for a different prompt, model or tool set: those changes would have produced a different trajectory, which the recording does not contain. Treat replay as the first, cheap fidelity level—not as proof that a prompt/model configuration would behave the same live.

## Minimum repository interface

The right abstraction is not “any Git repository”. It is **any repository that satisfies an optimisation contract**.

There is useful prior art, but nothing currently unifies environment, objective and external-side-effect authorisation into the complete contract this company needs.

**SWE-bench** supplies a repository-specific task—roughly repository/commit plus issue statement—and judges the resulting patch using executable tests. The original benchmark consists of real issues and corresponding fixes; its task specification is therefore much richer than “here is a Git URL”. citeturn16search4turn16search10

**SWE-agent** similarly expects explicit information. Its current CLI can be given a repository, problem statement and Docker image, while batch instances include environment configuration, problem statement and a `base_commit` used to reset the repository. Recent SWE-agent documentation deliberately simplified environment handling by making a Docker image the starting point and recommending that the image contain the required dependencies. citeturn17search2turn17search6turn17search34

**Claw-SWE-Bench is particularly relevant newer prior art.** It separates a fixed evaluation substrate—prompt, task set, execution container, runtime budget, patch extraction and evaluator—from a replaceable harness adapter. On 350 tasks across eight languages and 43 repositories, adapter design alone changed Pass@1 from 19.1% to 73.4% with the same GLM 5.1 model. This is benchmark evidence, not production evidence, but the architectural lesson is strong: a small explicit adapter boundary is much more realistic than assuming arbitrary agents and repositories compose automatically. citeturn19search0

**Dev Containers, Nix and Python lockfiles solve only the environment half.** A `devcontainer.json` describes how tooling can construct or access a well-defined runtime stack; Nix provides declarative/reproducible environments; `uv.lock` pins exact resolved Python dependencies to make installations reproducible. None says what business outcome constitutes success. citeturn17search4turn17search16turn18search3turn18search7

Aider's benchmark/test integration is similarly useful but smaller in scope: it lets a repository/test command participate in the feedback loop. It is not a universal semantic contract for the repository.

### A practical minimum `RepoContract`

I would make this a versioned machine-readable object, regardless of whether the file is literally called `optimizer.yaml`.

| Field | Can usually be auto-detected? | Must ultimately be declared/confirmed? |
|---|---|---|
| Repository URI and immutable base commit | Yes | Commit should be frozen for each experiment |
| Language/package manager/runtime candidates | Yes | Only where detection is ambiguous |
| Dockerfile/devcontainer/flake/lockfile | Yes | Maintainer approves canonical environment |
| Setup/build/test candidate commands | Often | **Yes** for the commands that define valid execution |
| Task corpus/replay bundle | No reliable general method | **Yes** |
| Acceptance assertions/verifier | Tests/CI can be proposed | **Yes** |
| Hard constraints and FAIL/UNMEASURABLE semantics | No | **Yes** |
| Reset/cleanup semantics for external state | Partly | **Yes** |
| Permitted network destinations | No | **Yes** |
| Permitted Azure/Snowflake/Prefect/vendor capabilities | No | **Yes** |
| Credential capability references | No | **Yes** |
| Runtime/token/API-cost/attempt budgets | Defaults possible | Owner sets risk envelope |
| Allowed output: local diff, branch, PR, deployment | No | **Yes** |
| Minimum practically meaningful improvement/degradation | No | Owner/product decision |

The system can and should auto-draft most of the mechanical half by scanning `pyproject.toml`, `uv.lock`, `poetry.lock`, requirements files, Dockerfiles, `devcontainer.json`, Nix files, CI workflows, test directories, README instructions and package metadata.

What it **must not auto-authorise** is the semantic half. An LLM can say “this looks like a Snowflake ingestion connector and these appear to be its tests”; it cannot infer that a client's production database is fair game, that missing 0.1% of rows is acceptable, or that pushing a branch which triggers a deployment workflow is consented.

That is the minimum irreducible hand-written portion of agnosticism: **intent and authority**.

## Environment reproducibility and cross-repository transfer

### Environment setup is a real blocker, not a solved implementation detail

The strongest current empirical evidence is bad news for zero-touch repository agnosticism.

**Open research — benchmark-only.** EnvBench studied 329 Python and 665 JVM repositories selected specifically because simple deterministic setup scripts were insufficient. Its best tested workflow successfully configured only **6.69% of the Python repositories and 29.47% of the JVM repositories**. Those are not random-repository rates—EnvBench deliberately selects the difficult tail—but they show how little justification there is for assuming an LLM can bootstrap arbitrary Python environments reliably. citeturn14search0

**Open research — benchmark construction.** SWE-rebench V2, a 2026 language-agnostic task-construction pipeline, reports that even with an interactive setup agent, **only around 20% of repositories succeeded on a single setup attempt**. The project therefore treats repository setup as its own expensive synthesis stage rather than something a coding agent casually does every time. citeturn14search1

MEnvAgent reports improved automated environment construction across ten languages using planning/execution/verification and environment reuse; this remains benchmark-construction evidence, not evidence of arbitrary client repositories being safely onboarded to a production agent system. citeturn14search2turn14search14

At the other end of the scale, the daVinci-Env/OpenSWE project reports **45,320 executable Docker environments spanning more than 12,800 repositories**, constructed on a 64-node cluster. Its authors report spending **$891,000 on environment construction and another $576,000 on trajectory sampling/curation, about $1.47 million overall**. This is a research-team self-report and should not be interpreted as a unit price for this company; it is valuable as evidence that large-scale repository environment creation is itself a substantial engineering/computational project. citeturn15search2

These figures use different definitions of “successful setup”, so they should **not** be combined into an average success rate. The consistent finding is what matters: environment synthesis remains expensive and unreliable on heterogeneous repositories.

### Recommendation for this company

Make environment onboarding a **one-time repository admission process, not part of every optimiser trial**.

The resolution order should be:

**Use the repository's own reproducible environment first.** If a pinned Docker image, Dockerfile/devcontainer, Nix configuration or Python lockfile already works, treat it as authoritative. Dev Containers explicitly exist to carry runtime/tool metadata; Nix declaratively recreates environments; `uv.lock` records exact dependency resolutions. citeturn17search16turn18search0turn18search7

**Otherwise run a bounded environment-synthesis agent in an isolated bootstrap sandbox.** It can infer Python version, install commands and system packages, but its result is not accepted until the repository's build/test/verifier runs from a clean start.

**After a small bounded number of attempts, escalate to a human and cache the result.** The exact cap is company policy rather than a scientific constant; the important result from current environment research is that retries improve yield but no evidence supports allowing indefinite retries. Your own 97.6%-of-run restart loop is an extreme demonstration of why “try again” cannot be the fallback policy.

**Freeze the successful environment by image digest and associate it with the repository commit or compatibility range.** Optimisation candidates should start from that frozen substrate. Do not let prompt/model search silently mutate the environment being used to judge prompt/model search.

For predominantly Python repositories, `uv` is attractive as a fast implementation choice **where the repository can validly be represented by a locked Python environment**, but it does not solve native libraries, external services, OS-level dependencies or historical versions by itself. Its official documentation makes the narrower reproducibility claim: a lockfile captures exact dependency versions for consistent installations. citeturn18search1turn18search10

### Transfer is the point where the “agnostic” claim breaks

I found **no published evidence that an agent configuration optimised on repository A remains optimal on an unseen repository B**. The closest empirical work generally points in the opposite direction.

A useful way to summarise the evidence is:

| Configuration dimension | Evidence on transfer | Recommendation |
|---|---|---|
| **Prompt/repository instructions** | Strongly repository/task dependent | Re-optimise |
| **Model** | Large performance differences, but cost/performance ranking depends on workload | Re-benchmark |
| **Tool set / harness** | Large interactions with agent/model/task | Re-optimise |
| **Team topology / communication** | Prompt optimisation gains depend on topology and task | Re-optimise |
| **Retry/effort budget** | More attempts can improve pass@k, but marginal value and loop risk vary | Transfer the existence of caps, not the cap value |
| **Isolation, immutable reset, telemetry, cost accounting** | Domain-independent engineering controls | Transfer unchanged |
| **Evaluator/task distribution/environment** | Intrinsically repository-specific | Must be onboarded per repo |

**Open research — benchmark-only.** Claw-SWE-Bench found model choice moved Pass@1 by **29.4 percentage points** and harness choice by **27.4 points** under its controlled sweeps; merely changing the adapter with the model held fixed moved 19.1% to 73.4%. That is extraordinarily strong evidence against treating “the agent configuration” as a portable constant. citeturn19search0

Prompt optimisation is similarly conditional. MAS-PromptBench explicitly studies prompt-optimisation gains across task distribution, workflow topology, communication protocol and team size; its central finding is that gains depend on those structural choices rather than behaving as a universal prompt upgrade. This is benchmark evidence, not production evidence. citeturn19search1

More directly, recent repository-guidance work tunes instructions using repository-specific synthetic bug probes. It raises mean SWE-bench Verified resolution from a 25.5% unguided baseline to 33.0% for one studied model/configuration, while also reporting evidence that guidance quality can degrade under another model. That is evidence for **repository-specific adaptation**, not a universal guidance file. citeturn19search11

Fresh-repository benchmarks show a broader distribution-shift problem. SWE-bench Live reported materially lower performance on newly collected/fresher tasks than on SWE-bench Verified for the same agent setup, with additional differences between repositories already represented in SWE-bench and new repositories. Because task difficulty and contamination differ, this is not a clean experiment proving “repo transfer failure”, but it is directly inconsistent with assuming benchmark-optimised configurations travel unchanged. citeturn2view0

The retry dimension is only partially transferable. SWE-rebench V2 explicitly sees more environment-setup attempts raise success probability, yet still treats attempt count as a cost/yield trade-off. The transferable rule is therefore **“bounded retry with diminishing-return stopping”**, not “three retries” or “ten retries” as a universal optimum. citeturn14search1

So the plain answer is:

> **Today, a repo-agnostic optimiser is best understood as N repository-specific optimisations sharing one control plane, search engine, telemetry schema, sandbox and contract format. The “agnostic” achievement is chiefly the plumbing. The optimised result itself is not known to transfer.**

Cross-repository meta-learning—using previous repositories to choose promising priors on a new one—is a sensible later research direction. It should be treated as a hypothesis to test, not an architectural assumption.

## Prior art and the build-versus-adopt verdict

All of the major optimisation frameworks are useful, but **none eliminates the fitness/environment problem**.

| System | What it optimises | Required evaluator | Multi-step/tool workflows? | Evidence with real external side effects | Fit here |
|---|---|---|---|---|---|
| **DSPy BootstrapFewShot** | Few-shot demonstrations from successful traces | User-supplied metric/training examples | Yes, within DSPy programs | Reviewed evidence is documentation/benchmarks; no demonstrated arbitrary-repo production writer | Useful inner primitive |
| **DSPy MIPROv2** | Instructions and few-shot examples, jointly searched | User-supplied metric/dev set | Yes, DSPy programs | Benchmark/documentation evidence; no arbitrary-repo side-effect production evidence found | Useful for prompt/config subspace |
| **GEPA** | Instructions/prompts using reflective proposals from execution feedback | Training set plus metric; benefits from textual feedback | Yes; explicitly trace/feedback oriented | Benchmark evidence in the research reviewed; no demonstrated unknown-repo production deployment with external writes | **Closest useful inner optimiser** |
| **TextGrad** | Textual variables, prompts, code-like artefacts through “text gradients” | Objective/loss feedback | Compound computation graphs | Research applications only in reviewed primary evidence; not arbitrary production repos | Interesting research, more invasive |
| **Trace / OptoPrime** | Prompts, code, hyperparameters and heterogeneous workflow parameters from traces | General feedback/objective | Yes; its central abstraction is workflow execution traces | Research platform; examples span optimisation/code debugging/controller design, not production repo maintenance | Conceptually very close, less mature operationally |
| **FAPO** | Prompts first, then permitted pipeline-structure changes inside a standardised workspace | Explicit score function | Yes, specifically multi-step LLM pipelines | Six-benchmark research evaluation; no real client-side-effect production evidence found | Worth watching; still assumes standardised workspace/evaluator |
| **OpenEvolve** | Code variants under an evolutionary evaluator | Executable evaluator/metrics | Primarily code optimisation | Open-source research/demo evidence; its own issue tracker states whole-repository optimisation was not supported and asks for it | Not the right substrate today |
| **AlphaEvolve** | Algorithm/program variants under automated evaluators | Automated evaluator, generally highly precise | Autonomous code/evolution loop | **Yes, but vendor/self-reported**: Google reports deployment of evolved algorithms in its infrastructure; now offered as a Google Cloud product | Strong proof of evaluator-driven optimisation, not proof of repo agnosticism |

BootstrapFewShot's official contract makes the dependency explicit: a callable metric determines which generated traces become demonstrations. citeturn13search0turn13search12

DSPy's optimisation family likewise revolves around user-supplied metrics; its documentation says all optimisers consume numeric scoring and that GEPA additionally consumes natural-language feedback to guide reflective evolution. MIPROv2 searches instructions and demonstrations rather than discovering the application's true objective. citeturn13search15turn13search24turn4search4

**GEPA is the best match for the inner prompt-search problem.** It is especially attractive because this company already records rich traces and has a structured assertion contract: GEPA can exploit textual execution feedback rather than only a black-box scalar. What it does **not** provide is a repository onboarding contract, environment synthesiser, safe side-effect executor or proof that the supplied metric is good. citeturn13search6

**TextGrad** generalises the optimisation metaphor further, propagating natural-language feedback through a computation graph and demonstrating experiments in question answering, coding, molecular optimisation and radiotherapy planning. Those are research demonstrations; the paper is not evidence of autonomous agents safely changing arbitrary client repositories and data planes. citeturn20search0

**Trace** is perhaps the closest conceptual research architecture to a heterogeneous “agent configuration optimiser”: its OPTO formulation feeds execution traces and feedback into a generative optimiser and allows prompts, code and hyperparameters to be treated as optimisable variables. The authors explicitly describe it as an open research platform. Its reported experiments do not establish production-safe optimisation of arbitrary repositories with Snowflake/Azure-type side effects. citeturn20search5turn20search37

**FAPO is an important 2026 entrant.** It lets Claude Code inspect a standardised multi-step LLM pipeline, diagnose intermediate failures, first change prompts and then make scoped structural changes when attribution suggests a structural bottleneck. It reports outperforming GEPA in 15 of 18 model/benchmark comparisons across six benchmarks. This is **benchmark-only research**, and crucially FAPO is still given a standardised workspace and score function—the two things that are hard in this company's agnostic requirement. citeturn13search2

**OpenEvolve should not be mistaken for whole-repository optimisation simply because it is based on AlphaEvolve.** A February 2026 issue in the project explicitly states that its supported optimisation was a region in a single file and asks for whole-repository support. That is a direct mismatch for the requirement here. citeturn20search3

**AlphaEvolve is the strongest evidence that this general optimisation pattern can work in production when the evaluator is crisp.** Google reports that AlphaEvolve combines LLM code generation with automated evaluators and that resulting algorithms have been deployed in critical Google infrastructure; as of 2026, Google also markets AlphaEvolve through Google Cloud. These are **vendor claims/self-reports**, not independent demonstrations of arbitrary-repository autonomy. Its success strengthens the case for evaluator-first optimisation while weakening, rather than strengthening, the case for objective discovery: AlphaEvolve works because its target problems have executable, high-quality evaluators. citeturn20search2turn20search10turn20search34

### Adopt, extend or build

**Recommendation: build the outer optimisation control plane; adopt/extend GEPA for the prompt/instruction search subproblem where it fits.**

Do **not** reimplement prompt search from scratch unless integration proves harder than the algorithm is worth. GEPA is a good starting inner optimiser because it can exploit rich failure feedback and multi-step traces. But do not reorganise the company's whole architecture around DSPy solely to obtain GEPA if that creates a migration project.

The expensive and differentiating pieces are elsewhere:

1. repository contract and admission;
2. evaluator qualification;
3. frozen/reproducible execution environment;
4. capability-isolated side-effect runner;
5. run/task/config versioning;
6. complete attempt-level telemetry and cost accounting;
7. statistical experiment controller.

No reviewed optimiser supplies those as an arbitrary-repository system.

Karpathy's `autoresearch`, which the company is assessing separately, illustrates the same principle rather than invalidating it. Its reference loop is deliberately narrow: modify `train.py`, train for a fixed five-minute budget, evaluate whether the metric improved, retain or revert, repeat. That is why the loop is tractable: the editable surface, environment, budget and fitness are already fixed. It is an excellent illustration of **evaluator-first autonomous search**, but not evidence for repository agnosticism. citeturn13search1turn13search13

## Degradation detection and statistical confidence

“Point it at anything that is degrading” should be split out as a **monitoring subsystem**. An optimiser should not decide that something has degraded merely because the most recent stochastic run is worse.

### Established practice

Maintain a versioned baseline for each meaningful stratum—repository, task family, model, environment image, agent configuration—and compare new configurations on a **paired canary panel** wherever possible. Run old and new configurations on the same task/input/fixture distribution so task difficulty does not masquerade as regression.

For binary success metrics, compare proportions with an appropriate binomial/two-proportion method or, where observations are truly paired by task, McNemar-style paired analysis. For cost/latency and continuous quality metrics, use paired confidence intervals or bootstrap/permutation approaches. The experiment should declare a **minimum practically meaningful degradation** before seeing the result; “statistically different from zero” is not itself an operational threshold.

For continuous monitoring, established statistical process control is appropriate. A conventional Shewhart chart with ±3σ limits has an in-control false signal probability of about 0.0027 per point—an average false alarm every **371 points**. NIST notes that adding Western Electric-style supplementary rules makes false alarms substantially more frequent, about one per **91.75 points** on average. citeturn21search0turn21search8

CUSUM or EWMA is preferable when the concern is a small persistent drift rather than a single large shock, because those methods accumulate evidence from past observations rather than judging only the current point. Their decision thresholds should be chosen in terms of the shift one needs to detect and acceptable in-control average run length. citeturn21search1turn21search33

### How many samples are needed?

There is no universal sample size because it depends on baseline success probability, the degradation worth detecting, stochastic variance, pairing and desired false-positive/false-negative rates.

To make the scale concrete, using a standard normal approximation for **independent binary pass/fail observations**, a one-sided 5% type-I error rate, 80% power and equal sample sizes in baseline and candidate arms gives approximately:

| Baseline → degraded rate | Absolute regression | Required observations per arm |
|---|---:|---:|
| 50% → 40% | 10 percentage points | **305** |
| 50% → 35% | 15 points | **134** |
| 50% → 30% | 20 points | **74** |
| 70% → 60% | 10 points | **281** |
| 70% → 55% | 15 points | **128** |
| 70% → 50% | 20 points | **74** |

These are planning calculations, not a universal prescription. A well-designed **paired** canary test can require substantially fewer samples when outcomes are correlated, and sequential methods can often stop earlier when the change is large. Conversely, heterogeneous task mixes and clustered repository effects increase the effective requirement.

This gives a blunt answer for the company's current data: **14 total runs and three completions are nowhere near enough to make a reliable “it got 10 percentage points worse” claim.** At present, a completion-rate chart would mostly be measuring extreme uncertainty.

I would start by running a smaller fixed canary panel repeatedly to estimate actual within-task stochastic variance. Then perform the power calculation using that variance and the minimum regression that matters commercially.

### Agent-specific work is promising but still research

**Open research — benchmark/preprint.** E-valuator reframes agent verification as sequential hypothesis testing using e-processes, giving decisions that remain statistically valid as a trajectory unfolds and explicitly targeting false-alarm control. Its experiments cover six datasets and three agents; that is promising, but it is not evidence of long-running production monitoring of data-engineering agents. citeturn21search2turn21search10

AgentAssay, another 2026 research system, proposes stochastic regression testing, agent mutation tests, metamorphic relations and sequential testing. Its paper reports 7,605 trials, 86% behavioural-regression detection in one comparison where binary testing detected none, and substantial trial/cost reductions from sequential methods. Those are **paper results, not established production operating characteristics**. citeturn21search7

For this company the practical detector should therefore be:

**Release-time:** paired canary comparison against the previous accepted configuration, with a predeclared degradation margin and confidence criterion.

**Online:** CUSUM/EWMA or control-chart monitoring on task-normalised residuals for completion, correctness, UNMEASURABLE rate, retries, cost and latency.

**Sequential peeking:** use a statistically valid sequential procedure rather than repeatedly running ordinary p-values after every new observation.

**Optimizer trigger:** confirmation of degradation should create a diagnosis/optimisation candidate event; it should **not** immediately grant the optimiser permission to rewrite anything.

Monitoring determines **whether** performance changed. Diagnosis determines **where** it changed. Optimisation determines **what intervention to try**. Collapsing all three into a single autonomous loop reproduces the pattern described in the weaker [R] evidence: repeated activity with no mechanism for learning whether the activity helped.

## Isolation, portability decisions and remaining unknowns

### Isolation for repositories the company does not own

An unknown repository is simultaneously **untrusted code, untrusted text and potentially client-controlled input**. The threat model therefore includes ordinary malicious code as well as prompt injection hidden in README files, source comments, tests, issue descriptions and tool output.

**Established security design.** The controller/LLM that decides what to do should be separated from the machine that executes untrusted repository code. Anthropic's engineering guidance on autonomous coding explicitly emphasises hard sandbox boundaries, filesystem/network controls and keeping sensitive credentials outside environments running untrusted code; it also describes the danger created when untrusted execution and credentials inhabit the same trust domain. citeturn12search5turn12search13

For client repositories I would use a disposable **VM or microVM-class boundary per optimisation run**, with a container inside it if containers are useful for reproducibility. The run gets no host Docker socket, no host credentials, no shared writable home directory and no credentials simply injected as environment variables for arbitrary shell processes.

Credentials should be capabilities brokered from outside the sandbox:

| Resource | Optimiser's maximum capability |
|---|---|
| **GitHub/client Git** | Read repository + create a dedicated branch/PR where explicitly approved; never organisation admin, branch protection admin or merge authority |
| **Azure** | Dedicated short-lived workload identity scoped to an ephemeral test resource group/storage namespace; no subscription-wide Contributor/Owner |
| **Snowflake** | Dedicated least-privilege role to an isolated test database/schema/warehouse; no production/client-facing write grants |
| **Prefect** | Separate test workspace/work pool/deployment namespace; no production deployment mutation |
| **Vendor APIs** | Read-only or sandbox/test tenant wherever available; mutation methods denied unless the contract explicitly requires them |
| **Package/model network** | Explicit destination allowlist; default-deny arbitrary outbound internet |

GitHub Apps are well suited to the source-control part because installations can be granted selected repository permissions rather than a shared all-powerful personal access token, and installation access tokens are short lived and can be repository/permission scoped. citeturn12search31turn12search0 Snowflake's role model similarly supports the least-privilege pattern of granting only required privileges to a custom role. citeturn12search18

The optimiser should **never** be able to reach, irrespective of what text inside the repository asks it to do:

production Snowflake schemas used by client-facing BI; production Prefect deployment controls; unrestricted vendor mutation endpoints; organisation-level GitHub administration; secrets vault contents; Azure subscription-level administrator credentials; the host/container runtime socket; cloud instance metadata credentials; arbitrary unrelated client repositories; or direct merge-to-main/deploy authority.

A subtle source-control point matters here: **pushing a branch is itself an external side effect**, because branch creation may trigger CI/CD. The safest default is to produce a signed diff/patch artefact inside the optimisation environment. A separate policy-controlled service may then create a PR after checking the repository's workflow triggers. The optimiser itself should never merge its own winning candidate.

For a client-owned repository, the repository contract should be activated only by an explicit client-authorised installation or equivalent grant specifying repository identity, permitted outputs, external resources and expiry. “They gave us a Git URL” is not authorisation to run arbitrary code against their cloud estate.

**Published incidents.** I did not find a well-documented public incident whose precise fact pattern is “a general repo optimiser was pointed at a client's repository and corrupted that repository”. That absence should not be mistaken for evidence of safety. The closest more serious evidence is adjacent: Anthropic reported 2026 evaluation incidents in which agent access through third-party evaluation infrastructure reached real external systems without authorisation, illustrating why an evaluation sandbox with open network paths is not a harmless sandbox. That is a **vendor incident report**, not an independent study, and it concerned unauthorised system access rather than repository corruption specifically. citeturn12search26

### What to make portable now

The architecture should be designed so that adding repository two does not force surgery on repository one's optimiser. Several decisions are inexpensive now but painful to retrofit after agent implementations proliferate:

| Make portable **now** | Why retrofitting later is expensive |
|---|---|
| Versioned `RepoContract` schema | Otherwise business semantics become scattered through prompts and Python branches |
| `Runner`/sandbox abstraction | Prevents agent code learning direct Azure/Docker/Snowflake assumptions |
| Immutable repo commit + environment-image identity | Required to compare experiments retrospectively |
| Configuration as versioned data | Model, prompts, tools, retries and budgets must be reproducible/searchable rather than hidden in code |
| Central attempt/wall/token/cost caps | Avoids every agent inventing incompatible retry semantics |
| Attempt-level telemetry including failures | Historical costs and failure distributions cannot be reconstructed later—your logs already demonstrate this |
| Explicit terminal status for every run/stage | Necessary for censored-run statistics and reliable optimisation |
| Vector score + hard constraints | Avoids locking the platform into one scalar objective |
| PASS/FAIL/UNMEASURABLE/NOT_RUN semantics | Your current four-state design is worth retaining |
| Task/evaluation dataset versioning and holdout partition | Otherwise later “improvement” can simply be benchmark drift |
| Capability broker outside execution sandbox | Retrofitting privilege isolation after agents directly consume credentials is a major security redesign |
| Content-addressed trace/replay bundle | Enables audit, offline scorer tests and reproducible debugging |

These are the parts of “agnostic” worth paying for immediately.

### What should deliberately wait

Other forms of generality are relatively cheap to add once a second real repository demands them and are expensive distractions for four engineers today:

Broad automatic package-manager detection; every language ecosystem; Nix support where no existing repository uses Nix; multiple clouds; automatic conversion of every CI vendor; sophisticated Bayesian/evolutionary/meta-learning search; cross-repository prompt priors; automated objective inference; arbitrary team-topology search; optimiser ensembles; elaborate dashboards; and support for client repository classes that have never actually been onboarded.

In particular, **do not make the optimisation algorithm the architectural centre**. Search algorithms are replaceable. Evaluators, trace formats, run identities, capability boundaries and repository contracts are much more expensive to migrate.

### What is known with reasonable confidence

**Established/observed:** the current company data is insufficient to support expensive live configuration search; unbounded retries and missing failure-cost accounting must be fixed before optimisation; arbitrary environment construction remains a substantial unsolved engineering problem; existing optimiser frameworks require metrics rather than discovering business truth; weak test suites can substantially overstate code-agent success; and standard statistical methods exist for distinguishing drift from stochastic variance once enough observations exist. citeturn14search0turn16search0turn21search0

**Benchmark-supported, not production-proven:** prompts, harnesses, models and orchestration choices interact strongly with the workload; repository-specific guidance can help; environment-setup agents improve with iteration but still fail frequently; GEPA/FAPO/Trace/TextGrad can optimise increasingly rich agentic programs when supplied with evaluators. citeturn19search0turn19search11turn13search2turn20search5

**Vendor/self-reported:** AlphaEvolve demonstrates meaningful production algorithm optimisation inside Google when given strong automated evaluators, and is now productised by Google Cloud. That is important prior art, but it is not an arbitrary repository optimiser. citeturn20search10turn20search34

### What remains unknown

There is **no demonstrated general method for inferring an arbitrary repository's true objective well enough to use it autonomously as fitness**.

There is **no published evidence I found that the configuration optimum learned on repository A remains the optimum on unseen repository B** across prompt, model, tool set, topology and retry policy.

There is **no credible generic success rate for environment setup on “any repository”**. Published figures are benchmark-specific and range dramatically with how difficult repositories are selected and what counts as successful setup. EnvBench's 6.69% Python result and SWE-rebench V2's roughly 20% one-attempt repository yield should therefore be read as warning signals, not forecasts for this company's repositories. citeturn14search0turn14search1

It is unknown whether the company's 12-assertion evaluator actually discriminates good from bad connector migrations. Its four-state verdict model is sensible, but that is a schema property, not evidence of oracle quality. It must survive the proposed mutation/challenge qualification.

It is unknown how much live optimisation really costs this company because [M] failed attempts have no spend attached. Any financial ROI estimate before repairing that telemetry would be fabricated.

It is unknown whether offline replay predicts gains in configurations that would alter the trajectory itself. For prompt/model/tool changes, replay is evidence about recorded behaviour, not a counterfactual run.

And there is no production evidence in the reviewed optimisation-framework literature showing a system that safely takes an unfamiliar client repository, automatically establishes its business fitness function, synthesises its environment, explores multi-step agent configurations with Azure/Snowflake-like external side effects, and produces a transferable optimum.

**That is why the agnostic requirement is premature.** Build the evaluator and optimiser around the one repository you can make scientifically trustworthy. Make the contract, runner, telemetry, safety boundary and configuration representation portable now. Admit repository two through those interfaces later.

The durable design principle is: **agnosticism can be a property of the control plane; today it is not a demonstrated property of the objective, environment, or optimum.**