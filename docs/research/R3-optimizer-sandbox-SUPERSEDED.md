> # SUPERSEDED 2026-08-21 — do not run this.
>
> Replaced by `R3-control-plane-and-optimizer.md`. Two of its questions were answered before it
> was ever sent: R2 concluded "one end-to-end agent, not the three-agent team", so the team
> configuration space this asked how to search is a space we are not going to build; and its Q10
> ("is building an optimizer now the right move at all?") was answered independently by both R1
> and R2 — fix the control plane first.
>
> Kept for the record, because what a prompt asked before the evidence arrived is part of the
> evidence trail.

# R3 — The optimizer, its bounds, the sandbox, and scaffolding

**Run last** — its shape depends on R1's fitness function and R2's topology. Paste everything
inside the fence. Save the answer as `docs/research/answers/R3-answer.md`.

**Read the bounding question (Q4) as the important one.** We have already had the incident this
prompt is trying to prevent, twice, and we now have the numbers.

---

```
You are advising a small data-engineering company (about 4 engineers) building an internal "agent
factory" — LLM agents organised into teams that migrate and maintain data connectors along the path
vendor API -> Azure container -> Prefect 3 -> Snowflake -> BI/chat surfaces. Cloud is Azure
(Container Instances / Container Apps) with Snowflake as the warehouse.

Assume we will shortly have (a) an eval harness that can score one agent team on one connector
migration, and (b) a minimum team topology. We want an optimizer that can search for a better
configuration, and we want it bounded before it is capable.

=====================================================================
PART A — MEASURED CONTEXT
=====================================================================
[M] = measured from production event logs on 2026-08-21. [R] = earlier internal review, not
re-verified.

Why bounding is question one for us, in our own numbers:

- [M] Our pipeline has recorded 1,004 restart events with NO ATTEMPT CAP. The worst single case is
      352 restarts of one stage within one run.
- [M] A documented consequence: a stage failed on a timeout, the cloud container carried on running
      because nothing killed it, the stage was auto-restarted with no cap, and ten containers
      consumed an entire 10-core cloud region quota overnight, blocking every human operator.
- [R] A prior autonomous mechanism kept its attempt counter in an in-memory module-level dict, so
      every process restart handed it a fresh budget. It re-dispatched a permanently-failing stage
      every 30 minutes overnight.
- [R] A separate loop ran 965 times, recorded its own 1.6% success rate, and never adjusted.
- [M] Cost is recorded only on success events, so 1,001 recorded failures contribute $0.00 to the
      cost total. We cannot currently reconstruct true spend from our own logs.
- [M] 22 gate-approval events across all runs, ZERO refusals; 5 of 7 gates have no programmatic
      check at all.

An optimizer that "iterates until optimal" on top of that substrate is the overnight incident with
a bigger bill. We want the bounds designed first and the search designed second.

Tenancy, which we consider a hard requirement rather than a nice-to-have:
- [M] We serve multiple clients from shared infrastructure. We have already had an incident where
      a single vendor API key returned EVERY client's accounts — an unfiltered pull would land one
      client's rows in another client's warehouse table, and nothing downstream would detect it.
- Our eval contract has a tenancy assertion, and it currently returns UNMEASURABLE because nobody
  has written down which account ids are in scope. It correctly refuses to certify.

=====================================================================
PART B — THE QUESTIONS
=====================================================================
Separate ESTABLISHED PRACTICE from VENDOR CLAIM from OPEN RESEARCH throughout. For every safety
mechanism, give a concrete implementation, not a principle.

1. SEARCH SPACE. For an agent configuration — prompt, model, reasoning effort, tool set, context
   layout, retry policy, turn cap, budget — what is the evidence on which dimensions actually move
   outcomes, and by what order of magnitude? Which are known to be LOW-YIELD and can be dropped
   from the search entirely? We would rather search three dimensions that matter than eight that
   do not.

2. METHOD. Compare evolutionary/mutation search, Bayesian optimisation, bandit methods, and
   LLM-proposed mutations (an LLM suggesting the next configuration to try). Which suit a search
   where EACH EVALUATION COSTS MINUTES TO HOURS AND REAL MONEY and deploys real infrastructure?
   Include sample-efficiency numbers where published. How many evaluations does each method
   realistically need to beat a hand-tuned baseline?

3. OVERFITTING AND GOODHART. With a small eval corpus — ours is currently calibrated on ONE real
   successful run — how do teams stop an optimizer overfitting to it? Held-out sets, rotating
   corpora, adversarial cases: what actually works, and what is the published evidence on
   optimizer-induced eval degradation in practice? Given a corpus of one, is running an optimizer
   at all defensible, or is corpus growth a hard prerequisite? Give the minimum corpus size you
   would accept and the reasoning.

4. BOUNDING — THE HIGHEST-RISK PART. Give concrete implementations, not principles, for:
   a. A spend ceiling that SURVIVES A PROCESS RESTART. Our prior failure was an in-memory
      counter. Where does the counter live, what writes it, what reads it before dispatch, and how
      is the check made atomic against concurrent runners?
   b. A hard iteration cap, and where it is enforced so the thing being bounded cannot raise it.
   c. A kill switch reachable by a human MID-RUN, including how it stops work already dispatched
      to cloud containers that no longer have a parent process watching them.
   d. Detecting a search that is not converging, and stopping it automatically.
   e. Orphan detection: our containers outlive the stage that launched them. What is the standard
      pattern for guaranteeing a launched workload is either finished or killed?
   Cite real systems that implement these, and any published post-mortems where each failed.

5. SANDBOXING. For running agent-generated code that deploys infrastructure, compare Docker,
   gVisor, Firecracker, E2B, Modal, Daytona, and ephemeral cloud environments. Judge on: startup
   latency, cost per run, blast-radius containment, and whether cloud credentials can be scoped
   per sandbox so a compromised or confused run cannot reach beyond its own client. We are on
   Azure with Snowflake — weight the answer to that stack.

6. TENANCY. What is the correct isolation model for an optimizer that touches multi-client data
   paths? What is the MINIMUM gate set that must include a tenancy check, and where in the
   lifecycle must that check sit so it cannot be skipped? Is per-tenant credential scoping at the
   sandbox boundary achievable on Azure + Snowflake, and what does it cost operationally?

7. COST TELEMETRY. Given our logs currently record cost only on success, what is the minimum event
   schema that makes spend reconstructable after the fact — including for runs that failed, were
   killed, or orphaned a container? What do mature systems record per agent invocation?

8. SCAFFOLDING. What is the current best way to generate and maintain a multi-service Python repo
   skeleton of this kind — cookiecutter, copier, Nx, Bazel, uv workspaces, or an AI scaffolder?
   Judge specifically on keeping GENERATED PROJECTS UPDATABLE as the template evolves (template
   drift is the usual killer), and monorepo versus polyrepo for a 4-engineer team.

9. AUTORESEARCH. Assess github.com/karpathy/autoresearch honestly — what it actually is, what it
   does and does not provide, its maturity and activity, and whether it is a suitable base or
   better treated as a reference design. Do not assume it does what its name suggests; check the
   repository.

10. THE PREREQUISITE QUESTION. Given everything above — 1 of 13 readiness gates currently passing,
    a corpus of one, gates that have never refused, and no attempt cap — is building an optimizer
    now the right move at all? If your honest answer is "fix the substrate first, and here is the
    ordered list", say that instead of designing the optimizer. We will take that answer.

=====================================================================
CONSTRAINTS
=====================================================================
- Separate OBSERVED from MARKETED.
- For every safety mechanism: a concrete implementation, not a principle. "Use a persisted
  counter" is not an answer; "write to X with this transaction semantics, read before dispatch at
  Y" is.
- Where the honest answer is "this is unsolved", say so.
- We would rather be told to build less.

=====================================================================
DELIVERABLE
=====================================================================
1. A direct answer to Q10 — build the optimizer now, or fix the substrate first with an ordered
   list. Lead with this.
2. If an optimizer: its architecture, its search space reduced to the dimensions that matter, and
   its method with expected evaluation counts.
3. The bounding mechanisms, implemented concretely — ceiling, cap, kill switch, non-convergence
   detection, orphan reaping.
4. A sandbox recommendation with cost per iteration on Azure.
5. A tenancy isolation model and the minimum gate set.
6. A cost-telemetry event schema.
7. A scaffolding recommendation.
8. A verdict on autoresearch: base, reference, or neither.
9. What remains unknown, stated separately.
```
