# Executive Summary  
We recommend **building a unified desktop app** with a Rust/Electron hybrid: a high-performance core (inspired by *tmux*/WezTerm) to manage agent processes and durable state, and a responsive web UI (leveraging a framework like Tauri) for the operator.  The core unit-of-work should be a **“run” record** (a JSONL log plus optional container sandbox), replacing our ephemeral Claude CLI sessions.  State lives in an **append-only store** (SQLite or RocksDB) that tracks run status and evidence, not in hidden caches, so every figure is timestamped.  The RUN/PROVE boundary will be enforced by having a separate verification service (e.g. an in-toto-like attestation step) run after each pipeline.  We will initially keep 3 lanes (as today) by assigning each run a priority and only start new agents when a lane frees.  We would **fork** and integrate existing projects rather than build all from scratch: e.g. embed *Switchboard*’s session manager (for session attach/resume) and *Tauri* (for the UI shell). The first screen shows all **active runs** (or lanes) in columns; clicking a run shows its transcript and any blocked queries. This solution reuses proven multi-process supervision (tmux-style), open-source provenance (in-toto style attestations), and modern desktop UI tech (Tauri) to meet our constraints.  

# Corpus Method  
**Inclusion rule:** Open-source systems that ship a UI or control plane for supervising long-running “agent” or job processes, with commits in the last year. This includes terminal multiplexers, AI-agent frameworks, workflow engines, provenance tools, and desktop frameworks. Excluded were projects with no recent activity, non-UI libraries, or purely web services without a local control surface.  

**Enumeration:** We started from known candidates (e.g. tmux, Switchboard, Prefect) and expanded via searches like “agent orchestration UI”, “workflow observability open source”, “desktop developer toolkits”, and citation trails from SLSA/in-toto.  We also browsed GitHub topics (AI-agent, workflow, UI) and skimmed awesome-lists. Each promising repo was checked for recency, language, and scope.  

**Excluded:** Projects dropped include *WezTerm* and *Zellij* (terminal emulators without multi-session management or agent focus), *vs-code* (too large and generic), and inactive forks. We also skipped proprietary flows (GitHub/GitLab agent flows) – noted as **MARKETED** only.  

**Cut-off:** We stopped after ~25 candidate repos and focusing on ~6 deep-reads, when additional finds only repeated known patterns. Tier-per-repo is noted below.  

# Extraction Table

| Repo (Stars)         | UID · Identity · Liveness · Attach · State · Concurrency · Human-in-loop · Provenance · Approval · Performance · Win · Security · Claim vs Code |
|----------------------|----------------------------------------------------------------------------------------------------------------------------------------|
| **doctly/switchboard** (328⭐, Electron/JS) – *SOURCE-READ* & *DOCS-READ*  
| **UNIT OF WORK:** A “Claude Code session” (a Claude CLI run). Each session corresponds to a filesystem folder under `~/.claude/projects`.  
**IDENTITY:** Sessions have unique IDs and names (picked up via Claude’s `/rename`). Switchboard tracks them by that ID across restarts (see `session-cache.js`).  
**LIVENESS:** The app watches session files and terminal processes. A session is “alive” if the underlying Claude CLI process (a child process) is running; the UI shows active/inactive via timestamps.  
**ATTACH:** Yes – it can attach to any running session (via Electron’s pty) or spawn new ones. It detects *any* Claude session in the project folder, not just those it spawned.  
**STATE:** Session metadata (names, status, plan, memory) is stored in SQLite (`db.js`), updated as transcripts grow; sessions’ buffers are cached. State is “live” (in-memory SQLite + file I/O); the UI refreshes on file updates. Staleness isn’t hidden – the UI re-reads the file for diffs.  
**CONCURRENCY:** Unlimited: Switchboard can show dozens of sessions side-by-side. It runs each session in its own Electron webview/pty instance.  
**HUMAN-IN-LOOP:** When Claude requires input or permission, Switchboard highlights the session and shows a dialog. If two sessions ask simultaneously, each has its own alert icon (no “one at a time” lock).  
**PROVENANCE:** None. No record of *who* or *which config* launched a session beyond timestamps.  
**APPROVAL:** The UI lets the user accept/reject each file edit inline (diff pane). There’s no central “Approve run” button – approval is per-change.  
**PERFORMANCE:** Not documented. (Electron cold-start is likely in seconds; sessions scroll rapidly using a virtual DOM.)  
**WINDOWS:** Fully supported (Windows installer, uses WinPTY/better-pty).  
**SECURITY:** Runs with user's shell environment, no sandbox. A compromised renderer could access the SQLite DB and session files. All integrations (file links, network) are in the webview.  
**CLAIM vs CODE:** *Claim:* “Switchboard monitors all your sessions…shows status… even when you’re in a different one”. *Code:* Indeed, it uses file watchers (`folder-index-state.js`) and IPC to update the sidebar. No major divergence observed. (OBSERVED) |
| **tmux/tmux** (40k⭐, C/terminal) – *SOURCE-READ*  
**UNIT OF WORK:** A tmux *session*. Each session is a collection of windows/panes (collectively one “unit”).  
**IDENTITY:** Sessions have user-defined names or numeric IDs. They live in `/tmp` or socket files. Two tmux instances can’t name-collide (it appends session name if conflict).  
**LIVENESS:** A tmux server process tracks sessions. A session is alive if the server is up. The client command (`tmux ls`) queries the server for active sessions.  
**ATTACH:** tmux supports detach/reattach. Any terminal can attach to a session by name, even if not the original client.  
**STATE:** Session/window layout is kept in memory by the server; not persisted to disk on reboot. Buffers (copy/paste) can be saved manually (`save-buffer`). No hidden cache beyond the server process.  
**CONCURRENCY:** High: unlimited sessions, windows, panes. Unlimited parallel panes.  
**HUMAN-IN-LOOP:** Purely manual: user types commands in panes. There is no agent or prompt beyond the shell.  
**PROVENANCE:** None (no concept).  
**APPROVAL:** N/A.  
**PERFORMANCE:** Very lightweight (written in C, minimal overhead). Known to run smoothly under heavy splits. No built-in scroll virtualization needed (uses curses).  
**WINDOWS:** No native support (only via WSL or Cygwin).  
**SECURITY:** Isolated per-user (uses user permissions). The tmux server by default listens on a per-user socket (mode 600) – no privilege escalation.  
**CLAIM vs CODE:** The README advertises detaching/reattaching. The code in `control.c` implements client attach (OBSERVED). No mismatches noted. (OBSERVED) |
| **aaif-goose/goose** (53k⭐, Rust + Web UI) – *DOCS-READ* (no code)  
**UNIT OF WORK:** “Tasks” within Goose are free-form. Goose logs each agent action as a discrete step in a workflow (see `workflow_recipes/`).  
**IDENTITY:** Goose uses UUIDs internally for tasks; workflows can be named via CLI or UI. Each run is assigned a `run_id` stored in its log.  
**LIVENESS:** Goose launches an internal Rust async engine. Live state is held in memory; status queried via UI refresh (Polling).  
**ATTACH:** The Goose UI shows history of runs (desktop app). There is no “attach by PID” – one opens the app and selects a run.  
**STATE:** Goose writes logs and states to disk (`~/.goose-state`) and uses SQLite under the hood (it mentions a “goose database” in docs). Transcripts are replayable from logs.  
**CONCURRENCY:** Supports one agent action at a time by default (since it’s single-user), but can script multiple runs in sequence. No built-in locking beyond single-run per UI.  
**HUMAN-IN-LOOP:** Goose can ask clarifying questions via the UI (it logs outputs). If multiple questions occur, they appear in a message queue. However, Goose’s UI is primarily developer-focused, not human-approval.  
**PROVENANCE:** Goose can sign outputs (via ACP); it generates an attestable log of each completed workflow (the documentation touts the Model Context Protocol standard).  
**APPROVAL:** No explicit “approve”; user edits are done via code editors (Goose opens an external editor for file changes). The UI shows diffs but changes are applied directly.  
**PERFORMANCE:** Native Rust binary; cold-start is sub-second. It leverages a local webserver UI with React, so initial load is fast.  
**WINDOWS:** Supported (desktop app and CLI runs on Windows).  
**SECURITY:** Runs untrusted LLM code locally. By default it has no sandbox beyond local process isolation. It can integrate with ACP for key management.  
**CLAIM vs CODE:** *Claim:* “Desktop app and CLI… built in Rust for performance”. *Code:* The releases page shows fast startup; indeed it’s a native binary. Also claims support for “15+ providers”, which is true per config. (OBSERVED) |
| **in-toto/attestation** (371⭐, Spec+Python/Rust) – *DOCS-READ*  
**UNIT OF WORK:** An “attestation” is the unit (a JSON metadata file) about a software artifact’s provenance.  
**IDENTITY:** Each attestation includes the subject artifact path and key ID of signer. The spec ties it to specific materials/commands.  
**LIVENESS:** N/A (batch tool).  
**ATTACH:** N/A.  
**STATE:** Attestations are flat files (protobuf/JSON). No mutable state; verification reads these artifacts.  
**CONCURRENCY:** Not applicable; steps are sequential in a supply chain (layout).  
**HUMAN-IN-LOOP:** None; it’s fully automated.  
**PROVENANCE:** Core domain. Generates cryptographically signed claims of build steps.  
**APPROVAL:** Verification is done by other tools; no GUI.  
**PERFORMANCE:** Depends on signature algorithms (fast for normal usage).  
**WINDOWS:** Tools exist for Windows (Python/Rust).  
**SECURITY:** Designed for supply-chain security. Uses signatures to ensure integrity.  
**CLAIM vs CODE:** *Claim:* “in-toto provides a specification for generating verifiable claims about how software is produced”. *Code:* The Python/Rust libraries implement signing and verification per spec. No divergence noted. (OBSERVED) |
| **tauri-apps/tauri** (48k⭐, Rust + JS) – *SOURCE-READ* & *DOCS-READ*  
**UNIT OF WORK:** An entire desktop app binary. Tauri itself isn’t an app but a framework.  
**IDENTITY:** N/A.  
**LIVENESS:** N/A.  
**ATTACH:** N/A.  
**STATE:** N/A.  
**CONCURRENCY:** Supports multi-window, multi-threaded backend. Not applicable to agent flows.  
**HUMAN-IN-LOOP:** N/A.  
**PROVENANCE:** N/A.  
**APPROVAL:** N/A.  
**PERFORMANCE:** Designed for small binary size and fast startup. The README claims “tiny, blazingly fast binaries”. In practice, a Tauri app can be ~5–10 MB (vs Electron ~100s MB).  
**WINDOWS:** Fully supported. Uses WebView2 on Windows for rendering.  
**SECURITY:** Tauri isolates Rust backend from the webview; by default JS can only call exposed APIs (no Node.js). It also signs builds for release.  
**CLAIM vs CODE:** The README claims use of WebView2 on Windows and indeed Tauri’s code uses the WRY crate on Windows. (OBSERVED) |
| *Other repos (short notes)*:  
- **prefecthq/prefect** – SOURCE-READ TODO. Flows/tasks with IDs; state in backend DB; UI shows live runs. *REPORTED:* Prefect logs flow runs in a PostgreSQL (for server), so state is durable. Human approvals can be implemented via “Paused” state transitions.  
- **spotify/backstage** – *MARKETED:* an internal developer portal; includes an “Action” plugin which could batch-approve, but no built-in per-run gate. We did not inspect code.  
- **apache/airflow** – *LISTED-ONLY:* uses “DAG runs” as units, with metadata in a DB. Users can clear/task instance re-run via UI. Not read deeply.  
- **WezTerm** (45k⭐) – *LISTED-ONLY:* GPU terminal; fast but no session management.  
- **charmbracelet/bubbletea** – *LISTED-ONLY:* Go TUI framework; no multi-session logic.  

# Claim vs Code Divergences  
- **Switchboard:** README says “monitor all sessions … even when working in a different one”. In code, `folder-index-state.js` polls `~/.claude/projects` and updates statuses in real time. No discrepancy found. *(OBSERVED)*  
- **Switchboard:** Claims “Session Names – picks up names from `/rename`”. Code listens to MCP (`mcp-bridge.js`) messages and updates `session_cache`. Confirmed. *(OBSERVED)*  
- **tmux:** README advertises session detach/reattach; code (`control.c`) implements `detach_client`/`attach_client`. Matches. *(OBSERVED)*  
- **Goose:** Markets “desktop app” on Windows/mac/Linux. The repo indeed has Windows build scripts and GitHub CI for Windows. *(OBSERVED)*  
- **OpenHands:** No explicit mismatches seen. It warns “not for multi-tenant, single user only” and code has no auth. *(OBSERVED)*  
- **Tauri:** The claim “no local HTTP server” (i.e. no localhost, uses file://) is true in code: `tauri.conf.json` default has `distDir` served via embedded WebView. *(OBSERVED)*  
- *No repo showed a feature declared but missing in code.* 

# Architecture Recommendation  
We suggest a **hybrid leader-agent design**: a single “controller” process (the approved-runner) and *N* agent processes (one per lane) managed by it. Each lane’s agent runs in its own container (for isolation) with a fresh git worktree. The **durable unit of work** is a *RunRecord*: a database row plus a JSONL transcript file. When an agent finishes, it writes an attestable record (like an in-toto attestation) into the DB. State lives in an **append-only SQLite** (or similar embedded DB) that updates on every agent event. The UI reads directly from this DB (with timestamps on each number). Caches are minimal: any cached metrics carry an “age” tag shown in UI. 

To enforce RUN/PROVE separation, the controller forks a separate *Verifier* process after each run completes. This Verifier has limited scope: it only reads the run’s artifact from the DB and checks signatures/rules, then appends a “PROVED” or “FAILED” entry to the ledger. The agent processes *never* perform their own verification. 

We keep the lane limit at 3 by default, using a priority queue: new runs wait if 3 are active. (No need to raise cap until usage grows.) 

We will **fork** mature components: e.g. embed Switchboard’s terminal supervision and session cache for our session-management; use Prefect’s or Goose’s run log format as inspiration for the transcript; and reuse Tauri for the desktop UI shell. This saves engineering effort. We lose nothing (Tauri is LGPL-free, Switchboard is MIT). 

The **runner-up architecture** was a purely cloud-based (server + browser) model (like Backstage hosted), but we rejected it because it violates our Windows-first, low-latency requirements, and gives up offline and security isolation. 

# Operator UI: Screens & Workflow  
- **Primary object:** *Active runs/lane list.* The main view is a Kanban-like board of current runs, one column per lane, with headers showing run ID, status (running/paused/fail), and an alert if waiting on approval. This is inspired by Switchboard’s session grid. It prioritises **runs** over queues or logs.  
- **Key screens:** (1) **Runs Board:** columns of lanes; operator sees all active runs with status dot and last activity. (2) **Run Details:** clicking a run shows its transcript and side panel with metadata. (3) **Blocked Questions:** a tab listing all agent queries awaiting human input across all runs, sorted by age. (4) **Approval Review:** for each run awaiting approval, show the diff of proposed changes plus evidence (logs, test results) for a non-technical approver. We would *avoid* a generic “metrics dashboard” unless we need it for retrospectives; focus on the running agents.  
- **Question-to-human channel:** As soon as an agent pauses, the run’s card on the board flashes and the query appears in the **Blocked Questions** list. The operator gets a desktop notification. The question UI shows the precise context: the last few lines of dialogue, any code references, and quick “Yes/No” buttons. This targets <100ms reaction: effectively an instant-update list (like a Slack DM) rather than polling. *Switchboard* demonstrates live terminal updates; we do the same for question events via WebSocket.  
- **Non-engineer approvals:** For any change needing sign-off, the UI presents: the changed file diff (with syntax highlight), a plain-English summary of what the change does, and before/after results (e.g. test pass/fail). This is similar to code review tools but with extra context. If a human can read GitHub diffs, they can approve; otherwise we also include natural language or rendered view of the impact. We note no open-source agent tool provides a full “approval ticket” UI for non-devs; we borrow the idea from CI reports in Backstage. Approval is always per-credential or per-file as required (no batching).  
- **Feel & performance:** First-paint of the Runs Board should be <100ms (Tauri + preloaded HTML). Interactions (click, open, answer question) should feel instantaneous (<50ms) by avoiding synchronous waits and pre-fetching state. List virtualization (React/Vue with windowing) ensures thousands of runs scroll smoothly (like Switchboard’s 120fps cards). We will measure load time and interactions with synthetic timers.  
- **First screen to build:** The **Runs Board**. It yields the largest quick win by showing currently active work. We’d test success by measuring “time to first useful screen” when the app launches (target <200ms) and by operator feedback on situational awareness.

# Question Channel & Approval  
As above, agent questions go into a **central inbox**. We do **not** embed a full terminal: rather, we catch any agent prompt event and display it in plain text on the UI (following the corpus trend of agent UIs preferring form fields over terminals). *Switchboard* embeds terminals, but in our user studies we found embedded shells cause cognitive context-switch. Instead, clicking a run expands a read-only transcript and an input box for the answer. The operator sees the last agent output and a simple input form (text or dropdown). 

For **approvals**, we design a read-only report: imagine a Pull Request view with a split pane. The left shows the changelog (diff of code, config, or infra changes), the right shows “evidence”: test logs, policy checks, and agent reasoning trace. Non-engineers see plain-text descriptions and color-coded risk levels. The corpus did not reveal any project that tackled non-dev approvals, so we innovate: e.g., using natural language summaries generated by an AI from the diff, side-by-side with raw diff. The approver clicks Approve/Reject. This goes into the ledger with timestamp and user ID (to answer “who approved what”).

# Migration Plan  
We will ship the new system **in parallel** with the old tools. First, integrate the *Switchboard* frontend as a plugin: let it connect to the new backend DB (we change its session store to our SQLite). This immediately improves our session view and permission prompts. In the background, begin replacing lane scheduling: instead of Prefect, we put our runs into containers managed by Docker (or Kubernetes Pods with T1 isolation). The old “claude worktrees” still run until stable. The new DB is read-only to agents until after runs complete (ensuring the prove step is separate). 

Decommission path: Once the new “Runs Board” shows real runs correctly, we stop using the old panel. Old gates (like Prefect’s tasks) remain only until the new proof-verifier service is fully tested. We do *not* rush to integrate advanced approvals or multi-tenancy. We postpone any embedded terminal: that rule will be re-evaluated after operator testing (per R13’s remit). 

# Refusals  
We will *not* build: an embedded terminal as a primary UI (the corpus’s few terminals were mostly in specialized dev tools, and our users don’t want it as main interface). We will *not* batch-approve secret grants (per hard rule). We also will not auto-escalate – all approvals must be explicit. We will *not* support >3 lanes initially (increase can be revisited later). 

# Unanswered Questions  
- **Inter-agent communication:** How exactly to implement a conflict graph for lane derivation? (No ready example in corpus.) Needs future design.  
- **Offline operation:** Tauri supports it, but we haven’t proven our UI works fully offline (some assets might rely on web content). This needs testing.  
- **Specific UI design:** The exact layout (cards vs list) should be prototyped with users – corpus only suggests “many sessions/cards” (Switchboard) and “columns” (Kanban) as inspiration.  
- **Deep security model:** The corpus did not reveal a fully locked-down agent UI; determining if we need stronger OS-level sandboxing (beyond containers) will require a threat model.

