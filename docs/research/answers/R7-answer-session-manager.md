# R7 — A session manager for agent teams: what to adopt, what to build, what to automate

## Verdict on Switchboard  
Switchboard is a full-featured Claude Code session manager, but it does **not neatly fit our constraints**. It launches each session in a real PTY (via `node-pty`) and can optionally use isolated Git worktrees if given the `--worktree` flag. By default it reuses the project directory, so we would need to force the `--worktree` option on each lane to enforce one worktree per lane. It persists session history in the Claude JSONL files and caches metadata in SQLite, watching `~/.claude/projects` for changes. In principle it could integrate with our branch-per-lane setup by spawning each lane with `--worktree`, and capturing its file edits via the built-in MCP bridge. However, **Switchboard embeds terminals in its UI** (“Every open session renders its full terminal in a card”), which violates our constraint against in-page terminals. Adopting it “as is” would trade one user interface (Windows Terminal tabs) for another (an Electron app), without clear gains. We might _fork_ or cherry-pick ideas instead: e.g. its session-scanning, MCP integration, and session-transition logic, but build our own front end.  
- **Pros:** Supports true PTYs for each session; can isolate worktrees via `--worktree`; captures Claude edits via MCP; persists and reloads sessions from disk.  
- **Cons:** Requires embedding terminals in an Electron UI (contra our policy); shares directory by default (needs explicit worktree flag); heavy architecture beyond our immediate needs.  
- **Conclusion:** Switchboard is best viewed as **inspiration** rather than a drop-in solution. We should *not* adopt it wholesale; instead, build only the needed pieces (PTY management, file watching, MCP hooks) that plug into our existing orchestrator and front end. *Observed:* Switchboard’s design is verified in practice; *Extrapolated:* whether its UI patterns translate to our multi-agent context is speculative. 

## 1. Agent-Team Configuration (TeamSpec)  
We must allow *declarative assembly* of teams, not hardcode them. Prior art suggests putting roles, models, tools, and possibly goals into a spec. For example, the **CrewAI** framework has a **role-based model** where each agent is given a defined persona, goal and backstory. Similarly, an OpenAgent (oh-my-openagent) team-mode uses a JSON *TeamSpec* listing each member’s role or prompt “kind” (e.g. writing, category) and enforces eligible agent types. A TeamSpec might include agent *names*, *models* or skill presets, permitted *subagents*, and the “GreenContract” criteria for output. However, too much detail tends to go unused: in practice teams only tune a few knobs (e.g. choice of specialist vs generalist, or tool sets). The trick is to capture only salient dimensions (model family, core role, important tools) and let defaults fill in the rest. We should version each TeamSpec (as in CrewAI’s YAML or OpenAgent’s JSON), so that a certification is pinned to the exact configuration that produced it.  

- **What it catches:** A TeamSpec makes the setup reproducible and auditable. By listing roles and their scopes in one place (like CrewAI’s persona definitions or OpenAgent’s member list), we ensure every run starts with the intended composition. Pinning the spec to a commit prevents drift (the run’s verdict can’t outlive the spec).  
- **What it cannot catch:** It can’t guarantee the team design itself is optimal – a spec encodes *what* team was used, not whether that team was *fit for purpose*. It also can’t prevent an LLM from ignoring its persona or using extra tools.  
- **Enforcing execution:** We’ll parse the TeamSpec at launch to spawn the right sessions. Tools can validate the spec (as OpenAgent does) and reject invalid configs. We can treat an agent-specified team (like Claude’s free-form prompt for teammates) as **observations** of a spec, but require approval or translation into our formal spec (observed in Claude, extrapolated for us).  

_Label: Observed (teams with roles in CrewAI, JSON configs in OpenAgent); Extrapolated (our exact schema, since no standard exists)._  

## 2. Optimizing a Team for the Task  
Currently we lack a live *fitness* signal (the 12-assertion GreenContract is unmeasurable). So we cannot yet auto-tune the team by search. In early stages, the best we can do is **heuristic routing**: match tasks to roles based on obvious signals (e.g. code-heavy tasks get a “coding specialist” agent, documentation tasks get a “writer” agent). We should also record historical successes: if past tasks similar in scope were solved well by certain agent types or prompt styles, suggest reusing that combination (akin to a simple retrieval of “similar ticket logs”). For now, an expensive eval (actually running the team) is the only true test of fitness.  

The *cheapest proxy* fitness function is likely **self-consistency**: did the team meet *some* readiness gates (e.g. all tests pass)? Or reduction in unresolved tasks? This is better than the vacuous “ran without crashing” metric we’ve seen. However, even that could be gamed (e.g. a lazy agent claiming “done” without doing work). We must watch for that trap and not auto-promote “passed” status based solely on LLM chatter.  

- **What it catches:** A heuristic match-up of agents to task types can speed up initial runs. For instance, Claude’s “shared task list” model uses a lead to decompose tasks; we might pre-assign roles (design lead, implementer, reviewer) based on project attributes.  
- **What it cannot catch:** It won’t know the ideal team until after the fact. Without measuring actual output quality, we can only approximate. Any “fitness” we use is itself a hand-crafted heuristic (like “unit tests pass”).  
- **Triggering optimization:** Once we have quantitative outcomes (e.g. tests passed, reviewer satisfaction), we could justify an offline configuration search or a bandit-style role trial. Until then, we’ll rely on sensible defaults and human judgement.  

_Label: Extrapolated (no published system auto-tunes team config at run-time; we infer from known principles)._  

## 3. Series of Tasks per Team (Work Queue)  
Teams must process **queues of work**, not just a single change. The clearest prior art is Claude Code’s *shared task list*: one agent (the orchestrator) populates a live queue of atomic tasks, and other agents claim tasks, mark them done/blocked, and loop until completion. Each task carries status flags (pending, in-progress, completed, blocked) to drive coordination. Critically, each agent uses its own git worktree to avoid conflicts, and a blocked task stays in the queue until its dependency is resolved.  

We should adopt a similar unit-of-work: e.g. **file-level or issue-level tasks** that can be claimed. Each task can list prerequisites (which must be done first) to prevent unsafe parallelism. On failure (e.g. an agent admits it cannot finish a task), we treat it as “blocked” or “escalated”: the orchestrator or a human must fix or reassign it. We should cap retries to avoid infinite loops; e.g. retry a failing task once automatically, then stop and raise an alert. To keep queue ordering correct, we won’t reorder arbitrarily: tasks stay in their original sequence except to skip blocked ones (Claude skips blocking tasks temporarily).  

- **What it catches:** This catches unhandled parallel edits and lost work. The Claude blog notes that a well-structured task (scoped to specific files) *minimizes conflicts*. A shared queue exposes blockers immediately, so agents don’t blindly overwrite each other.  
- **What it cannot catch:** It can’t solve a fundamentally bad decomposition. If tasks were improperly defined or too granular, agents may idle or thrash. It also won’t handle an agent that silently does nothing on its task (there’s no heartbeat).  
- **Triggering actions:** We’ll implement “claim” semantics with atomic locks on tasks (open by one agent at a time). If a task fails repeatedly, we mark it as needing intervention. We should display unresolved tasks prominently. If an agent crashes mid-task, its task should revert to pending after a timeout. This ensures the queue doesn’t silently skip work.  

_Label: Observed (Claude Code shared task list with git-worktree isolation)._  

## 4. Autonomy, Bounded  
Some pipeline chores can be automated, but each has failure modes. We consider the candidates:

- **Auto-start next lane:** If a lane finishes (all gates passed), automatically launch the next available lane. *Safe if* lanes are independent and resources permit (we already bound parallelism by file conflicts). We’d enforce a semaphore or scheduler so “auto-start” only fires when claims and worktrees are free. To keep it safe: require the completed lane truly met all pass conditions (commit built, tests green) before spawning the successor. We log every auto-launch and allow an override “pause” to prevent runaway spinning. This is **Observational**: some CI/CD systems auto-trigger sequential jobs under clear conditions.  
  - *Purposeful firing:* The orchestrator or a watch process can detect a lane’s pass flags and queue the next. A human “hold” in the queue can disable it.

- **Auto-merge lanes:** Once a lane’s readiness checks all pass and there are no structural conflicts, automatically merge its branch. This mirrors GitLab’s “merge when checks pass” feature. It catches the routine case and frees the human from clicking “merge”.  
  - *Safe if:* all policy checks (CI, approvals, no conflicts) are truly satisfied. It *cannot catch* logic errors or missing approvals by itself.  
  - *Preventing misfires:* We should only auto-merge after explicit sign-off (like labeling PR “merge-when-green”) or after a lead’s approval. We can incorporate similar merge-check gating as GitLab does (pass all tests, code review done, no outstanding discussions). A control flag (like in GitLab) prevents silent merges if any new comment or commit appears during the wait.

- **Auto-answer known blockers:** If a blocker query is exactly the same as a previous one, and we have a recorded answer, we could auto-respond. *Safe if* we verify the context hasn’t changed. That means comparing the current code diff + error message to the archived case. We can allow auto-answer only when a deterministic match is found. To refuse, we require any slight variation to require a human check. This is extrapolated (we know nothing aborts exactly identical block responses in existing systems).

- **Auto-retry failures:** If a stage (e.g. a flaky test run) fails, automatically retry up to a small limit (say 3 tries). Common CI practice. *Safe if* the failure is non-deterministic; *trap:* persistent failure means auto-retry is futile. We’d embed a retry counter; once cap reached, we mark “needs attention” so it doesn’t loop forever.

- **Auto-split large lanes:** If a lane grows beyond a threshold (e.g. too many changed files or lines), we might automatically subdivide it. This is risky: agents might not know logical boundaries. We would be extremely conservative – maybe only suggest a split to the lead. For now, we treat this as a *flag, not an automatic action.*  
 
For each auto-action, the key is **explicit rules**. We should engineer each to “refuse” (no-op) unless preconditions are crystal clear. For instance, do not auto-merge if even one check is stale. Log every decision so operators can audit “why did it merge or not.”  

_Label: Extrapolated (these behaviors are common in CI or sketched in forums, but not widely automated in multi-agent code workflows)._  

## 5. Interface — A Living System, Not a Dashboard  
An effective UI should reflect the underlying model state, not just decorate. We **must not** show dummy gauges. Instead, use direct projections of task and session state. Drawing inspiration from orchestration consoles (e.g. Kubernetes or Argo CI pipelines) and Claude’s multi-agent panel: we can present a real-time view of each session or lane (perhaps as tiles or a Gantt chart). Each tile shows progress markers — e.g. number of commits, last-edit timestamp, number of tasks done vs remaining — since “alive” status is unknowable. For example, the MindStudio article notes that the shared task list *“gives you a clearer picture”* of progress than watching a single agent. We can show which tasks are done/in-progress per agent.

At-a-glance, operators need: **how many sessions are running vs idle vs blocked; how many pending tasks; any sessions waiting on input**. Like a NOC display, we might color-code cards (green for active, yellow for waiting on input, red for error). A collapsed “idle agents” row (as Claude does) could hide finished threads to reduce clutter. Detailed views (“on demand”) allow expanding a session to see its transcript or test logs.

Crucially, the UI grammar must differentiate *planned* vs *completed*. E.g., an unfinished task on the UI should look distinct from a completed one (like a gap-tooth bar graph, not a static number). Any figure that doesn’t change with underlying data is purely decorative. For instance, a “total tasks count” is fine if it increments as tasks start/finish, but a graph of CPU usage (unrelated to agent decisions) would be decoration. Where state is truly uncertain (session liveness), we instead show proxy signals (e.g. blinking “busy” if output recently arrived). 

We find few published examples specific to code-agent UIs, so much of this is **extrapolated** from general dashboards. In practice, we’ll refine the interface by user feedback and make it “living” (one source-of-truth for all sessions) as per our design rule. 

_Label: Extrapolated (drawing on general orchestration and Claude’s real-time indicators)._  

## Build Order

1. **Team Configuration Surface (Item 1):** Defining a TeamSpec is the foundation. We need this first to launch any multi-agent run. Without it we can’t reproducibly spawn a team.  
2. **Multi-Task Queue System (Item 3):** Next, implement the shared task queue and git-worktree isolation, since the team is useless without processing tasks reliably. The Claude shared task-list example is the blueprint here.  
3. **Autonomy Guards (Item 4):** With config and queuing in place, we can safely layer in autonomous triggers (next-lane start, auto-merge, retries) under strict guards. These accelerate the run and keep it flowing. GitLab’s auto-merge checks offer a model for the strict gating we’ll apply.  
4. **Team Optimization Aids (Item 2):** Once the loop works end-to-end, we can think about smart matching of agent roles or light-weight tuning. Early on this may be just suggestions (e.g. “try a different language model”). Only after we gather performance data does heavier optimization search make sense.  
5. **Interface (Item 5):** Finally, build the monitoring UI. The run-first approach helps us know what state needs visualizing. We use the rule “no static decoration” – e.g. real task counters, session cards with live status (as Claude does). The interface can evolve as operators interact with the system.  

Each stage “catches” different issues: TeamSpec catches mis-configuration; the queue catches conflicts; autonomy catches delays; optimization catches inefficiencies; the UI catches hidden problems. Gaps we cannot yet close: no known off-the-shelf tool will automatically pick or adjust team configs for code tasks, and we lack a robust metric for LLM success beyond manual review. Finally, many UI design choices remain open (“what to highlight first?”) and will require real-world iteration.

**Sources:** We base these recommendations on observed practices in Claude Code’s agent teams and modern multi-agent frameworks (CrewAI, Microsoft), as well as our own system’s measurements. We clearly mark where we infer by analogy rather than direct evidence.