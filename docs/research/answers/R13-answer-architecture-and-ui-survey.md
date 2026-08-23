# R13 — Architecture and UI Survey

**Executive summary:** We recommend an **orchestrated actor/supervisor model** with explicit coordination and provenance logging, surfaced through an **event-driven desktop UI** implemented as a VS Code extension (with Monaco for editing and built‑in Git support). This leverages proven OTP-like supervision for reliability, offloads heavy UI to VS Code (avoiding hand‑rolled editors), and enables incremental, real‑time updates.  Our first change would be **urgent human notifications** (e.g. system toast or Slack/OS push alerts) for agent questions, since the measured backlog shows humans are the bottleneck (agents queue for days).

## 1. Orchestration architectures

We surveyed standard multi-agent coordination patterns:

- **Orchestrator–Worker (Planner/Executor):** A central planner “fans out” tasks to workers and merges results.  Assumes tasks decompose into parallelizable subtasks.  Failure mode: conflicting or duplicate outputs if two workers inadvertently do the same work.  Real examples: workflow engines like Airflow/Prefect or Celery, which split a job among tasks.  With a 3-lane conflict graph, an orchestrator just schedules up to 3 at once; it *doesn’t* magically raise concurrency beyond the graph – it merely rearranges assignment without breaking the fundamental cap.

- **Hierarchical (Supervisor Trees):** Managers delegate to sub-managers/workers.  Good for complex multi-step goals spanning domains.  Assumes a strict hierarchy with well-defined responsibilities.  Failure: “goal drift” between layers or bottlenecks at higher levels.  Real production: Erlang/OTP supervision trees used in telecom and messaging stacks (WhatsApp, RabbitMQ, CouchDB).  Here, supervisors isolate failures (restart only failed process).  This tree can support >3 concurrent workers if each supervisor spawns independent branches, but conflicts in shared resources still cap overall concurrency.

- **Blackboard (Shared Workspace):** Agents read/write a common global state.  Assumes loosely-coupled agents collaborating via a memory space.  Failure: race conditions and lost updates (two agents overwriting each other’s writes).  Classic AI example: the *Hearsay-II* speech system or manufacturing scheduling boards.  In practice, blackboard gives maximum flexibility: new agents can join by posting to shared state.  But under a 3-lane conflict cap, it may allow dynamic task splitting (e.g. agents can grab subtasks from the board), possibly easing concurrency, but still cannot override the underlying conflict constraints.

- **Actor/Supervisor (Erlang-style):** Tree of supervised lightweight processes, each monitoring children.  Assumes independent actors communicate via messages.  Failure mode: if a child crashes, only its supervisor restarts it (one-for-one); higher-level failures can cascade via strategies (one-for-all, rest-for-one).  Production use: WhatsApp, massive telecom systems.  This effectively implements a hierarchical model with automatic recovery.  With 3 lanes, actors can run fully in parallel up to resource limits; they won’t *exceed* the lane cap set by the conflict graph since conflicts still apply.

- **Contract-Net / Auction:** Agents *bid* for announced tasks.  Assumes tasks can be awarded to the “best” agent, suiting dynamic resource allocation.  Failure: if agents mis-bid or tasks oversubscribe, work can be left unclaimed or over-allocated.  Used in multi-robot or manufacturing scenarios (the FIPA Contract Net Protocol).  It can in theory better utilize spare capacity by letting idle agents bid, potentially raising concurrency if extra agents are available. But given our fixed 3‐lane constraint, an auction would still halt after 3 winners.

- **Stigmergic (Indirect Coordination):** Agents coordinate via side-effects on shared environment (e.g. pheromone trails).  Assumes tasks can signal subgoals via environment traces.  Failure: subtleties in interaction (agents chasing stale signals or deadlocks).  Typical in swarm robotics or ant-colony systems.  Like blackboard, it maximizes emergent parallelism, but again cannot violate a hard concurrency limit in practice.

- **Generator–Critic (Multi-stage “Review”):** A *generator* agent proposes actions or plans, and a separate *critic/verifier* agent inspects them before execution.  Assumes cheap validation relative to action cost.  Failure: delays if the critic blocks too often, or if both agents miscommunicate.  This pattern is explicitly used by some agent frameworks (e.g. Cursor’s “Auto-review” classifier) to govern autonomy.  It doesn’t itself raise parallel concurrency; it *adds* a control loop.

**Concurrency summary:** None of these patterns magically breaches a 3-lane cap.  Orchestrator and hierarchy merely redistribute work and still respect the conflict graph. Only patterns that dynamically generate more independent subtasks (blackboard, stigmergy) might *effectively* parallelize better, but they still cannot invalidate the underlying conflict constraints. In short, orchestration patterns address reliability and fault modes; raising the concurrency ceiling depends on task structure, not the orchestration style.

## 2. Desktop/local UI platform

We compared options for a **Windows-first** local UI, considering startup, memory, I/O, inter-process costs, features, and maintenance:

- **Electron:** Proven cross‑platform (runs VS Code, Slack, Discord). Cold starts are slow (launching a full Chromium), and memory use is *very high* – even a “Hello World” Electron app can use 100–200 MB RAM, and real apps (Slack, Discord) often exceed 500 MB. IPC between the Node backend and renderer is extra overhead. It has good PTY support via Node libraries, and filesystem watching via Node (though Windows watch has handle limits). Packaging produces very large binaries (often 50+ MB) due to bundling Chrome. Update: Squirrel or auto-update is standard. Maintenance: large (must manage Node and Chromium, security).

- **Tauri:** Rust core + system WebView (Edge WebView2 on Windows). Cold start and memory are much lower, since apps use OS-embedded WebView instead of bundling Chrome. (Benchmarks show multi-hundred-MB electron apps shrink to a few MB with Tauri.) IPC is via lightweight Rust↔JS channels, leaner than Electron’s. Filesystem-watch uses Rust’s `notify` (good cross‑platform fidelity). PTY support exists via Rust crates (less mature, but workable). Packaging yields tiny executables (built-in updates possible via Tauri). Maintenance: smaller community than Electron, but safer defaults (Rust security). Cost: needing Rust skill is higher, but team can stick to frontend for UI.

- **Wails:** Go-based, similar to Tauri but with Go backend. Uses system WebView, small binaries, faster startup, and Go’s ease of use for many devs. Performance and footprint are on par with Tauri; the trade-off is a smaller ecosystem.

- **Native (WinUI/Qt):** High performance, low memory. Cold starts are fast (true native code). WinUI/.NET or C++ apps are small and use native OS file watchers and PTY APIs. Qt (C++/QtQuick) is cross-platform but heavier to set up on Windows (binaris still smaller than Electron but larger than pure native). Update processes can leverage OS installers. Maintenance: highest effort (C++/C# skills) and slower UI iteration, but minimal runtime overhead.

- **Local webserver + Browser UI:** The UI runs in a desktop browser pointed at `localhost`. Startup overhead: launching a browser tab each time, possibly slower than a native app. Memory: depends on the browser (Chrome, Edge, etc.). IPC: zero if fully web-socket based. Filesystem-watch: can use Web APIs or rely on the server. PTY: must connect via web-socket or have the page drive a backend. Packaging: trivial (just ship web assets), but user dependency on a browser. Maintenance: separates UI (web) and local logic, moderate complexity.

- **Terminal UI (TUI):** A console app (e.g. curses). Cold start is fastest, memory is minimal. All I/O on STDIN/STDOUT or a TTY; filesystem-watch and PTY are trivial. No rich UI, however – only text displays. Very low maintenance but unsuited to graphical diffs or rich layouts.

- **VS Code Extension:** Runs inside the user’s existing VS Code. Launch overhead is negligible (editor is assumed running). Memory overhead is “free” since VS Code is already open (itself Electron). Uses the VS Code LSP and Git APIs for file I/O, editor, diffs, and version control. Filesystem watching and PTY support come from VS Code’s host environment (Node/Electron). Packaging/deployment via VS Code Marketplace. Maintenance: relatively low – we leverage VS Code features instead of reimplementing. Drawback: it only works if user is in VS Code.

**Comparison:** Electron is battle-tested but too heavy (≳100 MB overhead). Tauri/Wails reduce runtime bloat (few MB, lean start), but require Rust/Go upkeep. Native (WinUI) is super-fast but costly to build. A VS Code extension avoids most UI work entirely by reusing Monaco (the VS Code editor) and built-in Git, so we don’t reinvent an IDE. Its “cold start” is essentially instant (just open in VS Code) and memory “cost” is amortized in the already-running editor.

**Trade-offs:** If we prioritize “instant” and low additional cost, a VS Code extension wins (nearly zero new startup time, uses existing FS watchers, Git, etc.). A Tauri or Wails native app is a runner-up: lean than Electron and cross‑platform, but requires building a custom UI. Electron is out due to bloat. A TUI could be used as a last-resort fallback (fast, but limited interface – perhaps as the never‑primary terminal escape).

## 3. Performance architecture (latency budget)

We must make the UI *feel* real‑time with up‑to‑date data. Key techniques: **incremental updates** and **optimistic rendering**.

- **Dependency-tracked invalidation:** Compute each probe only when its inputs change. Maintain a dataflow graph of dependencies (similar to a build system or reactive framework). On change, re-run only affected probes. This avoids redoing all 30 serially.

- **Event-sourcing / change feed:** Instead of recomputing from scratch, log every change (agent action, commit, etc.) as an event. Use a local event store (e.g. SQLite with change‑notification triggers) to update derived state incrementally. This means new UI can quickly “catch up” by processing only the delta events.

- **CRDTs or real-time databases:** For distributed consistency, CRDTs (e.g. Yjs/Automerge) or a real-time DB could merge state across components, always reflecting latest. E.g. publish each finding to a local reactive store so views update immediately.

- **Virtualized rendering:** Render only visible rows (e.g. React Virtualized) to keep UI updates sub-100 ms even for thousands of items.

- **Optimistic UI:** Immediately show anticipated results (or “processing” placeholders) while recalculating. On data arrival, reconcile with the UI state.

- **WebSockets or push:** Have the backend push updates to the UI instead of client polling, eliminating fetch delays.

We set the **latency budget** roughly by user-perception guidelines:
- *First paint:* under ~100 ms (ideally ~50 ms) so interface appears instantaneous.
- *Interactive response:* actions (clicks, filters) should respond under ~50–100 ms to feel fluid.
- *Full re-measure/update:* ideally under ~500 ms (certainly <1 s) before the user notices staleness.

Each technique contributes: e.g. incremental invalidation can cut re-measure time from seconds to hundreds of ms; virtualized lists cut render cost to tens of ms; optimistic rendering masks actual delays. In sum, a combination (event‑driven push + incremental caching + virtualization) can bring full updates into the low‐hundreds‐ms range, with first‐paint and interactions ~50–100 ms for a seamless feel.

**Tools:** Use a modern reactive web stack (e.g. React/Vue/Svelte with fine-grained state tracking), local SQLite or a reactive JS store for events, and libraries like React Virtualized or Svelte’s built-in reactivity. Avoid blind caching (we must label any cached data with its timestamp, per rule). We can rely on Rust/Go client code to push updates via WebSockets to the UI.

## 4. Approval surface and human-in-the-loop

Currently **no UI exists** for human review. We explored existing agent-review workflows:

- **GitHub/GitLab agentic flows:** Both platforms now support AI-powered workflows. GitHub’s new *Agentic Workflows* let you write high-level automation in Markdown, executing via Copilot CLI. They enforce “read-only by default” and “safe outputs” for writes, implying manual approval gates. GitHub Copilot Workspace (technical preview) uses a task/breakdown UI where *developers explicitly approve, edit, or reject each step* of an AI-generated plan.

- **Graphite Agent:** A code review AI. It runs on each PR, comments inline, and even offers one-click fixes. It is seamlessly integrated into GitHub (via a GitHub App), and can “approve” a PR automatically if no issues remain. Graphite’s UX focuses on a developer audience: comments appear in the diff, and suggestions can be applied with one click.

- **Factory.ai Droid:** Provides automated PR code review. It posts inline comments for issues and even auto-approves the PR if everything passes. It runs as a GitHub/GitLab action or local CLI and requires explicit configuration depth. It treats the PR diff as the unit of work.

- **Cursor Cloud Agents:** In Cursor’s automation docs, an agent can *post comments* and, if permissions allow, *approve or request changes* on PRs. Their “Auto-review” mode introduces a classifier agent that permits low-stakes actions without breaking, but still prompts on high-stakes steps. Cursor learned that gating every little step leads to fatigue, so they adjust prompts based on risk.

- **Copilot Workspace:** This in-IDE system generates a multi-step plan from a user’s goal. Critically, *each step is subject to developer approval or editing before execution*. This ensures “human in the loop” at each stage. It’s an early experiment, but shows that users prefer reviewing AI steps, not blind trust.

**Lessons learned:** All mature agent systems that modify code do so via PRs or diffs with human review. The state of the art is **pull-request gating with AI assistance**. Proposed work is presented as a diff/commit, with evidence (lint/test results, cost estimates) given in the PR description or comments. Tools like Graphite and Factory focus on technical feedback.

A non‑engineer (e.g. PM or auditor) could in principle review content if it’s framed in domain terms. For that, we’d need to surface:
- **Context:** Why the change was made (e.g. prompt or user intent in plain language).
- **Proof:** Test results or logs showing correctness.
- **Cost/Time:** Resources expended (token usage, compute time).
- **Provenance:** Which agent/model performed it, and under which config (see next section).

We found **no off-the-shelf tool** targeting business users reviewing code changes. The closest analogy is “low-code” platforms where actions are more visual. In practice, we suspect a specialized UI (perhaps integrated into the approval UI) is needed to guide a non-tech user through a change (e.g. a side-by-side with a summary, green/red flags, links to design docs). This remains an open area.

## 5. Provenance, lineage, and config hashing

We must audit every artifact’s origin (agent, model, prompt, tools). Relevant standards/tools:

- **OpenTelemetry GenAI conventions:** A CNF initiative to standardize tracing for AI agents. It defines semantic fields for model calls, agent identities, token counts, etc. Tools like Arize AX now natively support the `gen_ai.*` attributes. By instrumenting our agents with these spans, we’d automatically capture agent IDs, model versions, prompt lengths, etc. Teams can then send traces to an observability backend (Arize, LightStep, etc.) for a full audit trail.

- **SLSA/in-toto (supply-chain provenance):** Originally for software builds, SLSA (“Supply-chain Levels for Software Artifacts”) specifies how to record build metadata. In-toto links steps and artifacts in a signed graph. The community is extending these ideas to ML: for example, SLSA is being “considered for ML model fine-tuning”. We could adopt an in-toto style approach for our *build-plane* and agent pipelines: attach signed provenance files to each agent run (model hashes, dependency versions, etc.). Given our scale, full cryptographic attestation (TEEs, blockchains) is overkill, but a simple SBOM-like manifest per run would be prudent.

- **Model Cards & Metadata:** Per-model documentation (model cards) can record the training data, baseline performance, and known limits. We should at least grab model identifiers and version hashes (e.g. OpenAI model versions, Claude model IDs) and log them with each session. This is akin to the standard “model card” best practice. (We note frameworks like MLflow or Neptune can log model metadata at training/inference time, though here we mostly consume models.)

- **Data Lineage tools:** For input data provenance, solutions like Pachyderm, Apache Atlas or the academic “Atlas” framework exist for ML lineage. But in our use case, inputs are code/repos, not large datasets, so we can probably track versions via Git (which inherently captures file ancestry). We should embed commit hashes and file-change hashes into our logs.

- **What to adopt:** At minimum, we should implement a structured audit log (in the ledger) capturing: agent ID (process ID), agent *config hash* (covering agent code, prompt template, model name/hash, tool versions), timestamp, and action outcome. We should align it with OpenTelemetry GenAI fields (if using an OTEL collector) so everything is correlated. For the build-plane itself, we should emit a SLSA-like provenance record. Generating a simple JSON “provenance record” as part of each commit could suffice.

- **Avoid over-engineering:** Full cryptographic signing or TEEs (as in Atlas) is unnecessary for our team. We also shouldn’t try to capture every single “micro” dependency; focusing on the 15 dimensions mentioned (model ID, prompt text/version, tool versions, commit hash, agent ID, etc.) is enough. If a standard (e.g. OpenSSF’s new model signing) matures, it could supplement our logs, but for now, custom logging is fine.

## 6. Agent-to-human notification

Our problem is *alarm absence*. The system already logs questions (“needs” in state.json) but nobody is paged. We surveyed human notification methods:

- **Inline/modals:** E.g. pop-up dialogs when the UI is open. If the operator’s browser window is active, we could flash a modal or banner. This has 100% visibility *only if* the user is actively looking at the UI. It solves nothing if the person is away or the tab is hidden.

- **OS Notifications:** Windows toast or Mac NotificationCenter alerts (via a desktop app or browser API). These have a good chance of grabbing attention quickly (<seconds if sound on). Studies show users respond to push notifications within minutes on average (faster than email) provided they have attention. This would alert the operator even if the UI is in background.

- **Merged inbox / chat (Slack/Teams):** Send an alert to a chat channel or user with the question and link. Push (mobile) notifications can accompany these. Anecdotally, chat pings get faster responses than email. If multiple agents fire, it may roll up to one message per agent or a merged digest.

- **Escalation / on-call:** If no response in X minutes, escalate to someone else. PagerDuty-style on-call (SMS/phone) is reliable for urgent alerts (people often respond <5 min) but requires defined schedules. If multiple agents ask, escalation logic must avoid pinging everyone at once – best is to bundle or treat it as a single incident.

- **Interrupt (modal USB key):** A last resort could be a blocking OS prompt (like entering a password), but this is user-hostile and we’d never do it.

*Evidence:* We didn’t find direct studies on AI-agent prompts, but human factors research (from incident management) shows passive channels (email) often take hours, while SMS/phone/vibration get <5 min responses. Our failure is not over-alerting (fatigue) but under-alerting.

**Plan:** We should route agent questions through a **real-time channel**. For example, integrate with Slack (Cursor style) or directly use OS notifications from the desktop app. If two agents ask simultaneously, batch them into one notification or ask first-in-first-handled to avoid confusion. For guarantee, an on-call rotation could be considered (though a single user is more likely here).

## 7. Repo integration and the IDE boundary

Our UI needs to open/edit repo files, show diffs, stage commits, etc. Options:

- **LSP (Language Server Protocol):** Provides syntax checking, completions, goto-definition, etc. We can run language servers (Pyright, tsserver, etc.) to power editor intelligence. A web UI can embed an LSP client (monaco-languageclient, etc.) to use LSP. In VS Code extension, LSP is built-in for many languages. LSP assumes a text-editor UI present.

- **Tree-sitter:** A fast parsing library for syntax trees. It can enable semantic highlighting or structural queries. For example, CodeMirror 6 uses Tree-sitter under the hood for high-quality editing. It’s an alternative to LSP for some tasks (like structural diff) but less common for full IDE features.

- **Embedded editors (Monaco / CodeMirror):** Both are full-featured code editors. Monaco (the core of VS Code) is very powerful: it has intellisense, multi-cursor, Vim mode plugins, etc. But it’s large (~5 MB of JS) and not tree-shakable. CodeMirror 6 is lighter, modular, and designed to be embedded, with excellent performance on large files. Either can be embedded in Electron/Tauri or in a web page.

- **Git libraries (libgit2 / isomorphic-git):** For staging, diff, commit, we can use libgit2 (C library, Node bindings exist) or isomorphic-git (JS implementation). Both let us script Git without shelling out. Alternatively, in a VS Code extension we can use the built-in `vscode.git` API, or simply invoke `git` CLI since it’s guaranteed on the operator machine.

- **VS Code delegation:** If we build a VS Code extension rather than a standalone app, we can rely on the editor for file editing and diff views. The extension can drive VS Code’s built-in Git view instead of re-implementing it. This avoids rebuilding any IDE UI. We just add UI panels or commands for agent queries and linking to files.

The line *past which we rebuild an IDE* is reached as soon as we start re-implementing code editing, syntax highlighting, search, diffing, branching, etc. That is a huge effort. To avoid that, our best bet is to either piggyback on VS Code (since the user is already there) or embed Monaco (essentially a headless VS Code). Building our own minimal editor (e.g. a raw textarea or primitive code mirror) would indeed be like rebuilding a code IDE.

**Recommendation:** Use **VS Code extension** for tight integration: it gives us Monaco editor, LSP, Git UI, diffing, etc. as provided. The alternative (e.g. a Tauri app with an embedded Monaco) is possible but duplicates so much. If not VS Code, then embed Monaco in a desktop app. CodeMirror could be used, but since we have to show complex diffs and rely on LSP, Monaco (or the editor in VS Code) is a safer choice.

We’d use LSP servers to get code intelligence (hover, find) in the IDE. For small features (like simple find/replace or diff highlighting) Tree-sitter might suffice, but it’s not essential. The key is to avoid reinventing too much.

## 8. Migration strategy

We must build on top of the existing four interfaces (and one dead one). Without detail on those, we assume multiple UIs (CLI, web panel, maybe Slack bot). Our approach: **incremental, parallel rollout**.

- **Quick wins:** First, add notification and monitoring to existing surfaces. For example, attach OS notifications or Slack alerts to the current web/CLI triggers. This alone can drastically cut the days-long bottleneck without touching agent logic.

- **Parallel UI:** Develop the new UI (likely the VS Code extension and/or a Tauri app with dynamic updates) *in parallel* to the old panel. Point agents to report to both. Over time, migrate users to the new UI by exposing more features (e.g. in VS Code extension, allow small tasks like viewing job states, then larger ones).

- **No big-bang:** We should *not* rip out the existing instrument panel immediately (rule forbids removal). Instead, augment it. E.g., run an event loop that pushes updates to both UIs.

- **Agent backend migration:** If we change orchestration (say from Prefect to an Erlang VM model), do it gradually. Start by containerizing existing agents (if not already) and layering supervision on top, without changing their behavior. Validate that logs/proofs still align.

- **Phased retirement:** Once the new UI and flow are fully operational and people trust it, deprecate old interfaces. But only after feature parity (maybe via a “backwards compatibility” mode that forwards user actions).

- **Do later:** Avoid building any surface that **forces a team freeze** or renders old one useless. For example, do not embed a full terminal interface or custom editor until we decide on that path. Also, do *not* try to batch-approve secrets or any security bypass (that’s a hard rule).

Throughout, follow Apptad’s advice: start with the simplest needed pattern and add complexity deliberately. In practice: fix the humans’ workflow first (notifications), then optimize performance (event-driven UI), then polish features (edit/diff integration). At each step, run the new component alongside the old so we can roll back if needed.

## 9. Refusals and out-of-scope choices

We will *explicitly* refuse to embed a live terminal as a primary interface. The operator has indicated the terminal should remain an **escape hatch only**. Therefore, we will not build the UI around an embedded shell or encourage a purely text-UI workflow. (We could allow launching a terminal window on demand, but it won’t be the main UI.)

We also refuse any approach that breaks the stated constraints: for example, we will not introduce any “batch-secret-approve” feature, we will not silently cache data (every timestamped value must be shown with age), and we will not assume more concurrent lanes (like unlimited agents) than the current graph allows. Any design requiring a large platform team (e.g. custom cloud service with ops) is out of scope for our small team.

In summary, solutions that **avoid the per-secret approval rule, hide staleness, or rebuild a monolithic IDE from scratch** are off-limits. We focus on tools and architectures that respect the evidence-driven, human-in-the-loop culture.
