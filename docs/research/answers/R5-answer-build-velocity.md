# R5 – Improving Build Velocity (Time-to-Run)

We examined each question, summarising evidence and making **targeted recommendations** (with sources) to shorten *time to a first certifiable end-to-end run*. We rank suggestions by likely impact on that goal. Statements marked **observed** refer to practices seen in comparable (LLM/agent) settings; others are reasoned or from related software teams.

---

## 1. Backlog Growth: Discovery vs Scope Definition

As a team measures the system, new gates (work items) will naturally appear. Agile/process literature confirms this: early uncertainty is high and scope emerges over time. For example, the *Cone of Uncertainty* indicates that until initial sprints are done, exact scope is unknowable. Scrum guides recommend focusing first on highest-priority work and deferring details, not rigidly freezing scope. Similarly, Sonatayfy’s analysis of 60+ organizations (“Backlog Illusion”) shows that a growing backlog is usually due to intake exceeding throughput, not merely mismanagement. Importantly, *velocity alone* can be misleading: teams might close X points per sprint, yet if >X new points are added each sprint, true progress lags. 

In this context, the rapidly expanding gate set likely reflects *legitimate discovery of missing work*, not just sloppy planning. **Evidence:** TechTarget (2008) warns that “requirements freeze” is usually misguided – new awareness of needed requirements often emerges only after early implementation. In other words, this “scope creep” may really be uncovering unmet needs. To distinguish cases:
- If newly measured gates reveal *omitted-but-important tasks*, discovery should be embraced and backlog adjusted.  
- If tasks appear as refinement of already-known features, it may be scope-control slippage. 

**When to freeze:** In agile practice you generally *never fully freeze* backlog early; rather, lock in sprint scope per iteration and continuously groom. However, you should aim to *converge* the backlog: as uncertainty reduces, intake should roughly match output. A useful metric is the intake-to-throughput ratio: when it stays near 1 (throughput ≈ intake) for a sustained period, scope is stabilizing. Freezing too early (before key uncertainties are resolved) risks missing vital tasks; freezing too late means endless replanning. 

**Recommendation:** Continue measuring to discover missing work, but impose a cadence: plan a few “discovery spikes” up front (timeboxed analysis) to identify big unknowns, then enter a more stable build phase. Track intake vs throughput explicitly (the “Backlog Illusion” suggests adding it to dashboards). If intake >> throughput persists, treat it as a structural issue (possibly overambitious goals), not just normal progress. In summary, view the growing denominator as mostly a positive discovery process at this stage, while instituting metrics to catch chronic imbalance early.

*Impact:* Medium. Ensuring realistic scope will prevent endless backlog growth but adds overhead early. This helps avoid downstream coordination tax.

---

## 2. Parallel Agent Sessions: Speed and Coordination

**Observation:** In practice today, running multiple agents in parallel on one repo frequently causes merge conflicts. A large empirical study of 33K agent-generated GitHub PRs found that *same-agent* PRs in flight conflicted 19.8% of the time, and PRs from different agents conflicted ~41.7%. Most conflicts were **structural** (e.g. one agent deleting a file another edited) rather than simple line edits. This confirms that without coordination, parallel agents easily step on each other. In that study, virtually all “co-active” (overlapping) PRs were by the same agent framework, showing that even one model running twice causes trouble.

**Constraints:** In our case, we identified *file-locality* as the main constraint: two sessions editing the same file conflict, so they are run serially. This mirrors human practice: Jonas Braadbaart reports using Git worktrees so each coding agent works on disjoint subtrees, which avoids merge hell. His advice: “a proper system architecture… first create a reference design before agents work in parallel”. Worktrees allow independent contexts that merge later with manual review. 

**Coordination cost:** Evidence suggests the cost of full parallelism is high without coordination. The GitHub study implies a non-trivial fraction of work would require manual merge resolution. Reducing conflict means constraining concurrency – either by locking files or ensuring agents pick disjoint tasks. For example, the “STORM” system (arXiv 2024) gives each agent an isolated file state and only merges when safe. In STORM experiments, careful merge checking boosted throughput (an 18.7% improvement on one benchmark) by catching conflicts early. Such schemes are still academic, but they illustrate that agent frameworks can manage state. 

**Findings-ledger (knowledge sharing):** The idea of recording resolved issues for others is akin to a **shared knowledge base**. In human teams, issue trackers or decision logs serve this purpose. In AI agent settings, some projects persist “findings” in a structured log (the reddit example calls it a *ledger*), blocking progress until high-priority issues (P0/P1) are resolved. This resembles an “artifact store” that agents consult. We found no academic name for it, but it’s analogous to **shared memory or stateful logs** in multi-agent systems. 

**Recommendation:** Constrain parallelism by design. Use separate worktrees or branches for disjoint tasks, with at most one agent touching a file at once. Invest in simple locking or task-claiming (e.g. agent grabs tasks by file path). If parallel runs are needed, add an auto-merge step: run a merge tool (like STORM) after each agent run to detect conflicts, so agents can replan if conflict arises. Maintain a central “knowledge store” (findings ledger) where unresolved issues are logged, and gate progress on them as in the ai-blueprint example. This ledger concept has no standard name, but it effectively functions as a **shared memory/issue queue** that all sessions can query. 

*Impact:* High. Permitting safe parallel runs can drastically speed overall throughput, but only if conflicts are controlled. The data show unmanaged parallelism yields ~20–40% merge-conflict rates, so adopting scoped parallelism or merge-checking will have an immediate effect. Coordination artifacts (worktree, locks, shared ledger) are borrowed from human multi-threading (and are being tested in agent tools). 

---

## 3. Verification vs. Construction Ratio

This project has spent ~⅓ of time on instrument verification, catching false alarms before acting. Is that excessive? Without references on “LLM project QA cost”, we turn to general testing practice. It’s common that testing and build times are comparable, especially if automation is weak. However, we can likely reduce manual checks with better automated testing:

- **Property-based testing (PBT):** Recent research (PGS framework) shows that anchoring verification in high-level **properties/invariants** (rather than example I/O) greatly improves LLM code correctness. For instance, instead of checking exact text, assert structural invariants (“factors multiply back to original” in a factorization task). PGS achieved +23–37% pass-rate gains using PBT. Applying PBT here could mean specifying contract invariants for each gate or generated output, so agents self-check more robustly. 

- **Differential testing / fuzzing:** Other teams use *differential test-time scaling* (e.g. DiffCodeGen) to pick the best among multiple LLM outputs. They generate N candidates, fuzz inputs, and select the program that agrees most with others. This boosts reliability without extra human verification. It’s shown to improve single-run success with minimal LLM calls. For our instruments, we could run two independent checkers or mutate inputs to catch inconsistencies, catching errors automatically.

- **Mutation testing of controls:** Already done (breaking guards) – this is a known best practice (metamorphic testing for code) to validate the tests themselves. It’s in line with “shift-left” testing. 

The three false positives in one session suggest the **instrumentation is brittle**. If we had more systematic test-generation, those would be auto-detected. For example, property tests or differential checks could have flagged “implausible negative gap” or escaped HTML differences automatically. 

**Recommendation:** Keep rigorous verification but invest in reusable automated tests. Start writing **clear contracts/invariants** for each gate output (e.g. ordering constraints, count checks) and encode them as PBT or assertion checks. Use differential runs: for any given probe, run it twice (or via two different methods) and compare results. If mismatch, fail fast. Where feasible, add a second independent implementation (e.g. a simpler Python check) to cross-check. These investments (drawing on practices from PBT and differential test-time selection) should reduce the manual review burden. 

*Impact:* Medium. In the short term, adding automated checks costs development time, but in our case third of effort was already spent verifying. Stronger tests could cut future verification time. Likely diminishing returns beyond key invariants; focus first on the most failure-prone instruments (e.g. multi-SVG render or HTML diffs) and basic contract checks.

---

## 4. Surface Drift Mitigation

Currently four “views” (CLI, server, HTML, published artifact) are generated and cross-checked. This ensures no silent drift, but it’s complex. Many engineering projects solve this with a **single source of truth**. For example, static site generators (Docs-as-code) keep content in one format (e.g. Markdown) and regenerate all outputs, using CI to detect any manual edits. Similarly, infrastructure-as-code uses a declarative state and checks “apply” against it for drift. 

In our context, one could centralise the true measurement data (e.g. JSON or database) and have all surfaces render from that. Then a CI job simply regenerates them and diffs from the committed assets, failing if they differ. In fact, the ai-blueprint approach advocates exactly that level of rigor: they ran a live-agent harness that **asserts** all gating conditions hold on the actual output. While [5] specifically praised their ledger-checking, the principle applies: **automate re-generating each surface and compare**. 

We found little direct literature on “documentation drift” in AI pipelines, but general advice is to minimize duplicated logic. If feasible, maintain one canonical “readout model” and derive other views with scripts. Then use `--check` in CI (as you already do) to catch drift. Some teams skip multiple static artifacts entirely and use a dynamic server/UI driven from the data source, eliminating drift. 

**Recommendation:** If the generator scripts are reliable, keep them but treat the outputs as *generated code*: commit them only through automated builds and fail CI on mismatches. Alternatively, see if you can merge surfaces: e.g. serve one source over both CLI and web via the same renderer. But if multiple surfaces remain, maintain a robust “regeneration + diff” CI step (akin to `hash -C fast` in docs publishing). The current four-surfaces approach is safe but heavy; reducing to a single canonical output (with clients/viewers) could pay off in reduced test overhead. If adopting new patterns, mimic tools like Sphinx or Docusaurus that auto-build all docs from one master source, and commit only via CI.

*Impact:* Low-to-Medium. Drift between views is dangerous, but existing scripts already catch it. The big win would be a simpler pipeline (one generator) rather than many. This is more architecture work than operational speed, so its effect on initial run time is modest. (No specific external case studies found for exactly this scenario, so this advice is extrapolated from “docs-as-code” best practice.)

---

## 5. “Team One” Executor: New Runner vs Existing Orchestrator

This question is key: **we need a functioning “Team 1” end-to-end run asap**. 

- *Existing orchestrator:* An 18-stage bespoke pipeline already exists (though dormant since May). It presumably can run the full agent team end-to-end (but without a completion cap). The advantage: leverages existing code. The downside: it’s complex and hasn’t been used, so there may be unknown breakages or configuration drift. Adapting it with controls might take effort to understand all stages and plug in our new tasks.

- *New runner:* Building a minimal “runner” in this repo, perhaps using the Agents SDK or a simple loop, could be faster if the orchestrator is brittle. It could be narrowly scoped to just launch one session of each step, without all 18 stages.

We found no direct studies comparing build-from-scratch vs reuse orchestrator. However, software practice suggests **start simple** to unblock the pipeline. A prototype runner that does: load spec → spawn agents per stage → collect and verify outputs, might yield a quick sanity check. Meanwhile, the orchestrator can be refactored in parallel. 

**Controls before cloud dispatch:** Critical. An uncontrolled loop nearly burned the quota before. Best practices (from security research) call for *strict sandboxing and resource limits* for agent code. For example, run each agent in a container or VM with:
- Limited CPU/memory (e.g. docker with `--memory 512m --cpus 1.0`).
- No new privileges (`--security-opt no-new-privileges`), read-only file system except work directory, no network by default. 
These are recommended by security guides for agent code. 
Also enforce a max restart count or timeout per step. For instance, use a “circuit breaker” in orchestration: if an agent container fails N times (e.g. 3–5) or exceeds T minutes, abort rather than spin indefinitely. AWS ECS’s deployment circuit breaker is an example that stops after ~10 retries. Even better, apply our own loop guard: cap tries or implement exponential backoff so we don’t exhaust resources. 
Finally, user interactions/commands to the orchestrator should have an approval or audit step before launching containers, as an extra human-in-loop check (per NIST CAISI guidance).

**Recommendation:** Likely fastest path: build a minimal runner in-factory to get “team one” tentatively operational, with strict caps. This lets us test the end-to-end logic. In parallel, review or simplify the existing orchestrator. Ultimately, if stability and features of orchestrator are needed, port the working runner logic into it. In either case, require **sandboxing** by default: e.g. use gVisor or Kata containers if possible, and enforce seccomp/AppArmor profiles, network off by default. Enable a deployment-style circuit-breaker for retries: if a container doesn’t reach success in X attempts, stop the loop (AWS ECS supports this natively). 

*Impact:* Very High. Getting a prototype “team one” run is the gating step. A quick in-repo runner can unblock testing, but long-term an orchestrator with safe defaults may be better. Implementing container limits and circuit breakers is essential to avoid billing/overuse incidents (as seen before). 

---

## 6. Session/Handoff Model

The current session/boot-prompt with explicit handoff notes is a solid start, but multi-session AI workflows need careful context management. Research and best practice suggest **structured handoffs** over raw dumps. As XTrace and others note, handing off a “briefing” (objectives, constraints, decisions, artifacts) is far better than logs or summaries. For instance, include in the boot-prompt: the *problem definition, design decisions made so far, and references to evidence/docs*, rather than the entire chat history. 

Multi-agent memory research concurs: a **hierarchical memory** is ideal. That means global (project) knowledge, session- or role-specific memory, and private logs. Agents query the relevant tier rather than relying on the previous agent’s token window. In practice, this could mean storing key outcomes (e.g. “Schema X chosen,” “dep Y fixed”) in a shared store that the next session queries. The boot-prompt can then be minimal, since context is in memory. 

We found no direct case study of “hand-off becoming a second truth,” but the general principle is to minimize duplication. For example, don’t copy all docs: have sessions write to a canonical state store or knowledge base. If human engineers hand off to each other, they typically write a brief “status + next steps” rather than re-explaining everything. 

**Recommendation:** Use the session notes as a temporary summary but build out a *persistent memory layer* for truth. Structure handoffs as bullet lists of **action items, known facts, and blockers**, not a narrative. After each session, update a central record (an issue tracker or database) of “decisions made, tests added, next goals.” The next agent session should begin by querying this record (or a vector DB) to get relevant facts. This follows XTrace’s model: agents ask the memory “What do I need to know?” rather than ingesting raw text. 

*Impact:* Low-to-Medium. This improves robustness for long-running workflows but is likely not the bottleneck now. Since each session is short, manual handoffs suffice initially. However, formalizing it (especially the decision/action record) prevents duplicated work or forgotten context in multi-session pipelines. 

---

## Gaps in Evidence

- **Q1/Q4:** We found no studies specifically on *when exactly to freeze a measurement-derived backlog*. We infer from agile theory that backlog growth is expected in discovery phases.  
- **Q4 (Drift patterns):** No direct analog in literature for “multiple auto-generated surfaces.” Our advice is extrapolated from general best-practices (single source of truth, CI checks).  
- **Q6:** While we cite modern multi-agent memory ideas, little is published on *process handoffs* between agent-run sessions; we rely on analogy to human handoffs.

Other sub-questions have supporting evidence as noted above.

---

## Summary of Recommendations (ranked by impact on “time to run”)

1. **Prototype a lean runner with sandbox and circuit-breakers** (High impact) – fastest path to one full run, with strict resource limits.  
2. **Enable safe parallelism** (High) – use branching/worktrees or locks so multiple agents can work concurrently without file conflicts. Maintain a shared “findings ledger” for cross-session knowledge.  
3. **Automate and simplify surfaces** (Medium) – centralize output and use CI-diff to catch drift, reducing manual checks.  
4. **Enhance verification** (Medium) – apply property-based and differential testing to avoid manual instrument checks.  
5. **Manage backlog growth** (Medium) – accept early discovery, focus high-value work first, and monitor intake vs throughput.  
6. **Improve handoff/memory** (Low) – formalize briefings (decisions, tasks) and use a persistent memory store for multi-session consistency.

Each recommendation above is rooted in evidence or practice from either multi-agent AI projects or analogous software development research.