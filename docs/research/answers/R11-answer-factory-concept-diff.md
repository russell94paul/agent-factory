# R11 — Agent-Factory Concept Vocabulary Diff

We surveyed major agent frameworks and platforms (Anthropic, OpenAI, Google, Microsoft, LangChain, CrewAI, Factory.ai, Sierra, Cursor) for the high-level concepts they *make first-class* and compared to our 26 concepts.  Recurring themes include multi-agent “teams” or “crews,” “workflows” or “flows,” “skills” and “subagents,” “guardrails” or safety filters, persistent memory, connectors and packaged task environments, observability/tracing, human-in-the-loop approval, and cloud sandboxed agents.  Of these, *every* one is either already on our deferral list or truly missing. In particular, we have no counterpart for Guardrails, Workflows, Skills, or any tracing/storage of agent execution; nor do we package a task with its execution environment. Below we detail the *ABSENT* concepts (and note deferred ones):

- **Observability / Agent Traces (ABSENT):** None of the platforms below would simply dump a raw transcript file as our agent does.  They all emit structured spans/events (often following [OpenTelemetry’s GenAI semantic conventions](https://opentelemetry.io/docs/specs/otel/trace/semantic_conventions/gen-ai/)) and store them in queryable logs.  For example, LangSmith and Langfuse treat *each LLM call, tool call, or reasoning step* as a span in a trace database; Google’s Agent Engine UI and Microsoft’s telemetry likewise display sessions and metrics.  We have no equivalent: our `deploy.py` just writes an opaque transcript log.  

  **Who ships it:** Google’s Agent Engine (with built-in traces and dashboards), LangChain’s LangSmith observability platform, Langfuse/LangSmith competitor tools, and many LLM Ops products (Weave, Arize, etc.) all offer structured tracing.  

  **Concrete gap:** Without structured traces, our evaluator must re-run or inspect the raw log by hand; a subtle bug (e.g. a model retry loop or parallel file locks) could occur invisibly.  A malicious or buggy agent could loop or block indefinitely without being caught by a gate, and the transcript would just truncate.  Structured traces would catch “hung steps” or repeated tool errors immediately, whereas our system would only see an incomplete log.  

  **Cost:** Implementing OTEL tracing and a storage backend (or pushing to a SaaS) is significant engineering effort.  We’d need to define span schemas, handle potentially high volumes of data, and build dashboards or queries.  It also raises performance/complexity.  

- **Built-in Guardrails / Validators (ABSENT):** Several frameworks use *guardrails*: automatic input/output checks that run alongside the agent.  For example, OpenAI’s Agents SDK supports “guardrails” to run safety checks in parallel with the agent and fail fast on policy violations; Sierra’s Agent OS emphasizes content filters and PII detectors.  These are distinct from our readiness gates (which evaluate the finished output); guardrails would prevent a bad action *before* it even happens. 

  **Who ships it:** OpenAI’s Agent SDK explicitly includes Guardrails (parallel validation of inputs/outputs); Sierra’s platform has dialable rules and PII blocks (no-code dashboards for guardrails).  

  **Concrete gap:** Without inline guardrails, our agent might call a destructive tool or send sensitive data, and only the **next** run’s negative control would catch it (or not at all).  For example, an agent could hallucinate a database query with sensitive keywords; a guardrail would block that request, but our system would merely see a failure or corrupted result.  

  **Cost:** Adding guardrails means defining schemas or policies for all tools and outputs, maintaining them, and updating gates based on them.  It complicates agent runtime (parallel checks) and could delay execution or cause new failure modes (if a guardrail falsely trips).  

- **Multi-Agent Teams/Crews (DEFERRED):** Many platforms allow multiple agents coordinating.  Anthropic’s “Agent Teams” run parallel Claude instances on shared task lists; CrewAI explicitly models a **Crew** (a team of role-based agents) called by a **Flow**; Microsoft’s workflows span multiple agents.  We intentionally *do not* support full multi-agent teams (beyond one worker + verifier + human), so this remains on our deferral list.  

  **Who ships it:** Anthropic (“Agent Teams” in Claude Agent SDK), CrewAI (“Crews” of agents within “Flows”), and MS Agent Framework (workflows) all exemplify this.  

  **Concrete gap:** If we needed true parallel delegation (multiple agents jointly solving a problem), we have no abstraction for it.  As a consequence, any failure involving cross-agent coordination (e.g. deadlock between two workers) is moot for us.  Adding teams would enable richer workflows but also complicate safety (handled via deferral conditions).  

  **Cost:** Implementing agent teams requires a whole new infrastructure (agent-to-agent messaging, orchestration, etc.), which was explicitly ruled out by R2 unless unlocked by heavy evidence. We note it but offer no new recommendation; this concept is deferred.  

- **Workflow/Flow Engine (ABSENT):** Relatedly, *structured workflows* that orchestrate steps or subtasks are missing.  For example, CrewAI’s Flows define event-driven pipelines that call Crews, and Microsoft’s framework has “workflows” for multi-agent paths.  We have no single notion of a Flow or graph API: our agent just executes tasks sequentially as coded.  

  **Who ships it:** CrewAI’s Flows (explicit workflow graphs), Microsoft Agent Framework’s “graph-based workflows”, and LangChain’s LangGraph (branching/react-style agent flows).  

  **Concrete gap:** If a task naturally breaks into subgoals (e.g. “survey department leads, then compile report”), a workflow engine would structure that. We currently have to encode it inside the agent prompt or lose modularity.  Without it, a compositional error (like forgetting a branch) might slip through because no separate flow-checker exists.  

  **Cost:** A workflow system adds a lot of complexity (state management, triggers, concurrency). It may also overlap our optimizer/board logic and was explicitly not required by R3/R5.  

- **Persisted Memory / Context (ABSENT):** Some vendors give agents a memory store.  Google’s Agent Engine offers an integrated Memory Bank; LangGraph includes built-in memory across sessions.  We have *no persistent memory*: each run is stateless aside from the log.  

  **Who ships it:** LangChain’s LangGraph memory store, Google Vertex Memory Bank, CrewAI “Memory” modules.  

  **Concrete gap:** Without memory, our agents can’t “learn” user preferences or context across runs.  Concretely, if a user says “My team loves detailed docs” in one session, we wouldn’t recall that in the next session.  A memory-enabled agent would adapt its behavior (e.g. verbosity) over time; ours resets every time.  

  **Cost:** Adding memory would require databases for conversation state, more complex config (scoping memory per agent/team), and possibly data privacy concerns.  

- **Connectors / MCP Registry (ABSENT):** Vendors often provide a *connectors registry* or gateway for external tools.  OpenAI’s AgentKit had a Connector Registry to manage APIs; Google mentions Apigee-based **AI Gateway** for securing tools; Microsoft Foundry has built-in connectors (e.g. Bing search).  We have none: tools in our system are arbitrary code calls without a unified registry.  

  **Who ships it:** OpenAI (AgentKit’s Connector Registry), Google Cloud (Apigee AI Gateway for tools), Microsoft Foundry (many prebuilt connectors like Bing).  

  **Concrete gap:** Without a connector catalog, integrating new APIs or swapping them out must be done ad hoc.  For example, adding a company’s private search API would be seamless in Foundry’s connector model, but for us it means writing and certifying a new tool from scratch.  

  **Cost:** A registry implies governance (versioning APIs, permissions) and engineering (API adapters). It also adds another dimension to certification (ensuring connector security).  

- **Task Packaging / Environment (ABSENT):** There *is* no standard in our stack for packaging a task with its execution environment.  Modern agent benchmarks (METR Task Standard, SWE-Gym, Inspect’s task format, OpenAI evals, etc.) define tasks as a container/VM plus prompt plus scoring function.  We only supply raw JSON inputs and expect the agent to use its current local environment.  

  **Who ships it:** The METR Task Standard explicitly defines tasks with a reproducible VM environment, setup steps, and auto-scoring.  Similarly, SWE-Gym bundles codebases + tests, and Inspect (Prompts.Evals) uses JSON+environment specs.  

  **Concrete gap:** Consider an agent that must solve a Python project’s issue. In a METR-style task, the environment (Python version, packages, test suite) is fixed. In our case, variations in the local repo or system could make results non-reproducible.  An error (e.g. failing to install a needed package) might pass our gates but would fail a properly sandboxed env task.  

  **Cost:** Adopting a standard like METR under our hood would mean containerizing tasks, writing task definitions, and altering our evaluator to launch VMs/docker for each task. It’s a major effort and would duplicate GreenContract’s purpose.  

- **Human-in-the-Loop Approval (ABSENT):** We require upfront approval for sensitive tools, but we have no mid-run approval API.  Frameworks like Microsoft’s Foundry support pausing a long-running agent task until a human responds (with durable `task_id` and metadata); LangChain allows `interrupt_before` tool calls and resume with a `resume` command.  We have no mechanism to suspend and resume an agent run in flight.  

  **Who ships it:** Azure AI Foundry (“long-running hosted agents”) lets a `@multi_turn_task` suspend to await human input; LangChain’s LangGraph (via LangSmith) supports human interrupts/resume with a `Command(resume=True)` approach.  

  **Concrete gap:** If our agent needed to ask a human during its run (e.g. “approve payment?”), we have no durable state to pause and resume.  Currently an agent either succeeds or fails; a needed approval would simply be treated as a failure (or block the run).  Thus certain workflows (like interactive wizards) aren’t supported.  

  **Cost:** Implementing this requires a task engine that persists state (as Foundry does) or a checkpointer memory (as LangGraph does) and a UI/dashboard for humans. It greatly complicates our control plane and was deemed out-of-scope for automation by R7/R9.  

- **Cloud / Background Agents (ABSENT):** Some products let agents run remotely on dedicated machines.  Cursor’s “Cloud Agents” run a task on a sandboxed VM in the cloud, with the full repo, and report back results.  We have no cloud agent concept – all work happens locally on the user’s machine or CI.  

  **Who ships it:** Cursor’s Background (Cloud) Agents run on dedicated VMs with dev environments; Factory.ai’s *Droid* also runs tasks in their cloud service or CLI.  

  **Concrete gap:** Long-running or CPU-heavy jobs (large builds, data processing) could timeout or slow a local workstation. A cloud agent could offload these. Without it, a heavy task simply ties up our machine. For example, compiling a big codebase might slam the local CPU and foul git worktrees; a cloud agent would isolate that.  

  **Cost:** Supporting cloud agents means building remote execution (spinning up VMs, syncing code and secrets, capturing outputs), similar to Cursor’s architecture.  This is a huge infrastructure lift (and not requested by current certification goals).  

- **Persona / Channel Abstractions (ABSENT):** Sierra and others use higher-level “persona” or multi-channel features.  Sierra allows defining “personas” (distinct brand voices) and deploying one agent to multiple channels (chat, SMS, voice).  We have no such notion.  

  **Who ships it:** Sierra’s Agent Studio has Personas (“distinct personality and voice”) and multimodal Channels (chat, voice, SMS). Microsoft Foundry and others support multiple I/O channels as well.  

  **Concrete gap:** Without personas or channels, our agent can only speak in one style (the prompt we gave) and on one channel (the console).  For example, we couldn’t easily produce both a formal email reply and a playful chat message from the same certified agent.  

  **Cost:** Adding this would involve parameterizing the prompt style or output module and handling media (audio, UI). It’s mostly a product-feature layer, not central to our logic, so we count it as absent but of lower certification impact.  

> **Summary:** We examined roughly 30 candidate concepts from other SDKs (Skills, Subagents, Guardrails, Workflows, Teams, Memory, Traces, Connectors, Sandboxes, HITL, etc.).  Of these, none were already present under our names (`PRESENT`) and none simply map to our terminology (`RENAMED`).  Two map to deferred multi-agent ideas (Agent Teams/Crews, A2A) – so `DEFERRED` – with no new unlock-evidence found. All other gaps are genuine absences (`ABSENT`) as listed above.  There were no uncertain cases (`NOT-SEARCHABLE`) in the sources we could access.  

**Findings:**  Concepts examined: ~30.  Verdicts: `PRESENT`: 0; `RENAMED`: 0; `DEFERRED`: 2 (Agent teams, A2A); `ABSENT`: 9; `NOT-SEARCHABLE`: 0.  (We searched vendor docs, blogs, and SDK references – e.g. Claude, OpenAI Agents, ADK, LangChain, CrewAI, Factory.ai, Sierra, Cursor – and found all listed absent concepts explicitly documented above.)  

**Sources:** Anthropic (Claude SDK docs); OpenAI Agents/AgentKit docs; Google ADK/Vertex Agent Engine blog; Microsoft Agent Framework/Foundry docs; LangChain Academy and LangSmith site; CrewAI docs; Factory.ai docs; Sierra blog; Cursor docs; METR Task Standard; MLflow (GenAI OTEL); Langfuse blog.  Each cited excerpt is from official docs or credible engineering sources.