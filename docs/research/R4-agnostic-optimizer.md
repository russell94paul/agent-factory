# R4 — The agnostic optimizer: portability, fitness discovery, transfer

**Run in parallel with R3** — different literature, no dependency between them. R3 asks how to
search and how to bound it; R4 asks whether the thing being searched can be made repo-agnostic at
all. Paste everything inside the fence. Save as `docs/research/answers/R4-answer.md`.

**Why this is separate.** R3 assumes the optimizer works on one known system. The requirement
"point it at any repo and it optimises whatever is degrading" is a harder and different problem:
the fitness function stops being a given and becomes something each repo must declare. That is an
interface-design question with its own prior art — and it decides whether the architecture must be
built for portability now (cheap) or retrofitted later (expensive), which is worth knowing even if
we build the single-repo version first.

---

```
You are advising a small data-engineering company (about 4 engineers). They have built an internal
"agent factory": LLM agents organised into teams that do software work on their own repositories —
principally migrating and maintaining data connectors along the path vendor API -> Azure container
-> Prefect 3 -> Snowflake -> BI/chat surfaces. Cloud is Azure, warehouse is Snowflake, code is
mostly Python.

They want an "agnostic optimizer": one component that can be pointed at ANY repository — theirs, a
client's, a new one — and search for a better agent configuration for the work that repository
needs. The word they use is agnostic; the requirement is portability across repos, not just across
tasks within one repo.

I want to know whether that is achievable, what it actually costs, and what the prior art is. Tell
us if the honest answer is that repo-agnostic optimisation does not work yet.

=====================================================================
PART A — MEASURED CONTEXT
=====================================================================
[M] = measured from their production event logs on 2026-08-21. [R] = from an earlier internal
review, not re-verified; weaker evidence. Do not treat [R] figures as equally solid.

- [M] One evaluation, for them, means one full connector migration scored end to end. Across 14
      recorded runs the median wall-clock is 11.3 hours; across the 3 runs that actually completed
      it is 26.4 hours.
- [M] In the longest completed run, ONE stage held 92,817 of 95,098 seconds — 97.6% of the run —
      stuck in a restart loop with no attempt cap.
- [M] 1,001 stage failures against 165 completions across all runs. A stage attempt fails 6.1x
      more often than it succeeds.
- [M] 3 of 14 runs reached a terminal completion event; 4 more sit at "stage_started" with no
      terminal event at all.
- [M] 22 gate-approval events, ZERO refusals. 5 of 7 gates have no programmatic check.
- [M] Cost is recorded only on success, so the 1,001 failures contribute $0.00 and true spend is
      unrecoverable from the logs.
- [M] Exactly 1 connector has a recorded successful end-to-end run. Their eval corpus is therefore
      calibrated on a single real success.
- [R] 49 connector modules; 59% will not currently import.
- [R] A prior autonomous agent produced 233 diagnoses, 234 escalations and ZERO fixes in 81 days.
- [R] A separate loop ran 965 times, recorded its own 1.6% success rate, and never adjusted.

They have built an eval contract of 12 assertions with four verdicts — PASS, FAIL, UNMEASURABLE,
NOT_RUN — where UNMEASURABLE explicitly does not count as a pass. It has two probe modes: one that
refuses every instrument by default, and one that replays a recorded run, so configurations can be
scored offline against recorded evidence as well as live.

=====================================================================
PART B — THE QUESTIONS
=====================================================================
Separate ESTABLISHED PRACTICE from VENDOR CLAIM from OPEN RESEARCH throughout. Where something has
not been demonstrated outside a benchmark, say so.

1. FITNESS DISCOVERY — THE CENTRAL PROBLEM.
   An optimizer needs a fitness function. Agnostic means it cannot be hard-coded. For an arbitrary
   repository, how does a system establish what "better" means?
   Compare, with evidence: the repo's existing test suite as fitness; CI green/red; a declared
   contract file the repo maintainer writes; a benchmark harness; an LLM inferring the objective
   from the codebase; human-labelled preference.
   Address the failure mode directly: if a repository's tests are weak or its CI is decorative,
   the fitness function rewards nothing and the optimizer will happily converge on garbage. How do
   mature systems detect that the fitness signal they were handed is not discriminating BEFORE
   spending a search budget on it? Is there an accepted "is this metric actually measuring
   anything" pre-check?

2. THE REPO INTERFACE.
   What is the MINIMUM a repository must declare to be optimizable by an external system? Is there
   prior art for such a contract — SWE-bench task specifications, SWE-agent / OpenHands repo
   adapters, Aider's benchmark harness, devcontainer.json, nix flakes, or anything newer? What do
   these actually require per repo, and how much of it can be auto-detected versus hand-written?

3. ENVIRONMENT REPRODUCIBILITY — the practical blocker.
   Agnostic means being able to BUILD AND RUN an arbitrary repository reliably. Reports from
   benchmark construction suggest per-repo environment setup is the dominant engineering cost.
   What is the measured success rate of automated environment setup across diverse repos? What
   approaches work — per-repo Docker images, devcontainers, nix, uv/poetry resolution, LLM-
   generated setup scripts — and what are their observed failure rates? Give real numbers from
   benchmark construction efforts if they have been published.

4. TRANSFER — the crux of "agnostic".
   Does an agent configuration optimised on repository A transfer to repository B? Is there
   published evidence either way for prompt, model, effort, tool-set and retry-policy choices? If
   configurations do NOT transfer, then an "agnostic optimizer" is really N independent
   optimisations sharing a harness, and the agnostic part is the plumbing rather than the result —
   say so plainly if that is what the evidence shows. If some dimensions transfer and others do
   not, say which.

5. PRIOR ART ON CONFIGURATION OPTIMISATION.
   Assess, specifically and honestly: DSPy and its optimizers (MIPROv2, BootstrapFewShot), GEPA,
   TextGrad, Trace, OpenEvolve, AlphaEvolve, and any newer entrant. For each: what does it
   optimise, what metric does it require, does it work on multi-step tool-using agents with real
   side effects, and is there evidence of production use outside benchmarks? Which of these is the
   closest existing thing to what this company wants, and would adopting it beat building?
   Note: they are separately assessing github.com/karpathy/autoresearch; do not spend the answer
   on it, but do say how it relates to the above.

6. DEGRADATION DETECTION.
   Their stated requirement is "point it at anything in the system that is degrading". That is a
   monitoring and changepoint-detection problem, distinct from optimisation. What is proven for
   detecting performance regression in agent or pipeline systems — control charts, changepoint
   detection, baseline comparison, canary scoring? How do you distinguish real degradation from
   variance in a stochastic system, and what sample size is needed before a "it got worse" alarm
   is trustworthy? What false-positive rates are reported?

7. SAFETY ACROSS UNKNOWN REPOS.
   An optimizer with write access to an arbitrary repository, possibly a client's. What is the
   correct isolation model? Cover credential scoping per repo, blast-radius containment, what the
   optimizer must never be able to reach, and how consent/authorisation is handled when the repo
   belongs to someone else. Are there published incidents of automated systems damaging
   repositories they were pointed at?

8. THE SEQUENCING QUESTION — answer this one directly.
   This company currently has ONE proven end-to-end success, an eval corpus of one, gates that
   have never refused, and no attempt cap on retries. Is building a repo-AGNOSTIC optimizer now
   defensible, or should they build a single-repo optimizer first and generalise later?
   Be concrete about what generalising later actually costs — which architectural decisions are
   cheap to make portable now and expensive to retrofit, and which are the reverse. If the honest
   answer is "the agnostic requirement is premature and here is what to build instead", say that.

=====================================================================
CONSTRAINTS
=====================================================================
- Separate OBSERVED from MARKETED. Benchmark-only results must be labelled as such — this company's
  work deploys containers and writes to a client-facing warehouse.
- For every claim about a framework, say whether there is evidence of production use with real side
  effects, or only benchmark/demo evidence.
- Where the honest answer is "nobody has demonstrated this", say so rather than reasoning to a
  plausible-sounding conclusion.
- They would rather be told the requirement is premature than be handed an architecture for it.

=====================================================================
DELIVERABLE
=====================================================================
1. A direct verdict on Q8 — agnostic now, or single-repo first — leading the answer.
2. A fitness-discovery design, including the pre-check that detects a non-discriminating metric
   before any budget is spent on it.
3. The minimum repo interface, with what can be auto-detected and what must be declared.
4. An environment-reproducibility recommendation with observed success rates.
5. A clear statement on transfer: which configuration dimensions transfer across repos and which
   do not, with the evidence.
6. A prior-art verdict: adopt, extend, or build — naming the specific system if adopting.
7. A degradation-detection method with the sample size needed to trust an alarm.
8. An isolation model for optimising repos the company does not own.
9. The list of architectural decisions that are cheap to make portable now versus expensive to
   retrofit later.
10. What remains unknown, stated separately from what you are confident about.
```
