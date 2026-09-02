# ZEUS WORLD UI — CONSOLIDATED RESEARCH PACK

> Research pack for a spatial, army-command-style Agentic IDE / agent-organization world. Research-only; no implementation commitment.


---

# 00 — Baseline and Doctrine

## Existing project direction

The existing Agent Army materials already establish several constraints that this research should preserve:

- The primary product is an **Agentic IDE / Mission Control**, not merely a monitoring dashboard.
- Missions, teams, agents, communication, evidence, evaluation, replay, and human gates are real operational objects.
- Gamification should reflect real engineering state rather than reward meaningless activity.
- Collective Cognition should retrieve useful historical missions/failures/decisions with provenance rather than dump transcripts into every agent.
- Dynamic organizations, capability registries, organizational debugging, simulation, and champion/challenger evaluation are later capability layers.
- The current roadmap recommends proving a focused Mission Console before building more ambitious organization-level UI.

The uploaded roadmap currently describes the Mission Console MVP as a focused surface for selecting a mission/client, launching or resuming work, seeing the DAG, blockers and evidence, handling human gates, inspecting diffs/artifacts, and replaying the result. The existing gamified Mission Control document says the early UI should answer what is running, broken, blocked, waiting on the human, and why.

## New research question

The ZEUS World is not a replacement for the underlying Agentic IDE model. It is a new **projection and command surface** over the same state.

### Research question

> Can a spatial, extremely gamified command world reduce operator time, clicks, context switching, and cognitive load while preserving or improving situation awareness, intervention quality, and auditability?

## The 8 design doctrines

### 1. Space must encode meaning

A location should communicate something stable:

- theatre = domain/project family;
- front line = priority / urgency;
- base = team ownership;
- formation = execution topology;
- route = dependency / handoff / context supply;
- fog = uncertainty;
- alert effect = real anomaly or blocker;
- territory/area = mission scope or organizational boundary.

If location is arbitrary decoration, spatial navigation becomes slower than a sidebar.

### 2. Macro-command before micro-management

The UI should make it possible to command **groups, objectives, policies, and formations**. Individual-agent control remains available through zoom, but should not be the default.

This is reinforced by recent human-swarm interface research: scalability depends strongly on whether the user can operate at a macro level rather than managing each member separately.

### 3. Semantic zoom is the navigation model

Zoom should change information density and available commands:

- Company → strategic objectives and major incidents.
- Theatre → projects/capabilities/resources.
- Campaign → mission portfolios and dependencies.
- Operation → mission graph, gates, risk, evidence.
- Squad → team topology, communication, handoffs.
- Agent → current plan, context, tools, artifacts.
- Execution → files, tool calls, logs, diffs, evidence.

No page change should be required for most drill-down tasks.

### 4. Direct manipulation should compile into typed commands

Dragging a specialist onto a blocked mission should not be a cosmetic move. It should compile to a structured action such as:

```text
ADD_SPECIALIST
mission_id
capability_required
candidate_agent
handoff_context
budget_delta
permission_delta
```

Then policy, budget, isolation, and approval rules execute normally.

### 5. The world must expose constraints, not hide them

Use an ecological-interface principle: expose the relationships and constraints the operator needs to reason about, not just a wall of metrics.

Examples:

- a unit is blocked **because its credential/context/tool supply route is missing**;
- a review bottleneck appears as a real queue at a gate;
- two teams are converging on the same code region;
- a mission appears close to the front because business impact is high and deadline is near.

### 6. Every gamified state needs a dense fallback

Right-click / target-lock should expose exact state immediately. The world cannot force users to interpret animation when they need a number, diff, error, approval, or evidence source.

### 7. Gamification cannot reward harmful proxy metrics

Do not reward:

- message volume;
- token consumption;
- number of agents spawned;
- number of tickets created;
- speed without quality;
- unnecessary autonomy;
- avoiding escalation.

Rewards should attach to verified outcomes, learning, collaboration, or harmless social participation.

### 8. The world renderer is replaceable

Domain state must not live in sprites, scene objects, or map coordinates. The world is a projection. A conventional dense UI and the world UI should be able to coexist over the same event/state model.

## The key equation

The world is useful when it removes repeated context expression.

```text
LOCATION + ZOOM + TARGET + FORMATION + GESTURE
= IMPLICIT CONTEXT
```

A conventional UI repeatedly asks:

- which project?
- which mission?
- which agent?
- which environment?
- which repo?
- which logs?
- which time range?

A good world should already know most of that from where the operator is and what is targeted.

---

# 01 — Reference Systems and Design Mining

## A. Current agent command interfaces

### 1. OpenAI Codex app

**Relevant pattern:** multi-agent command center, agents in parallel, isolated worktrees, review in context, skills, background automations.

**Steal:**
- parallel work as a first-class object;
- isolation visible to the user;
- one place to move between long-running agents;
- review artifacts/diffs without leaving the agent context.

**ZEUS optimization:** replace a project/thread list with a semantic theatre map and target-lock; keep the exact diff/review affordances available at tactical zoom.

### 2. Cursor Agents Window

**Relevant pattern:** many agents across repos/environments, cloud/local/worktree switching, `/multitask`, best-of-N, screenshots/demos, design-mode targeting.

**Steal:**
- parallelization as a command, not a configuration exercise;
- one-click environment movement;
- compare competing agent runs;
- direct targeting of UI elements.

**ZEUS optimization:** formations become a visual compiler for these parallelization patterns; worktrees/sandboxes become visible operating positions rather than hidden metadata.

### 3. Microsoft Magentic-UI

**Relevant pattern:** transparent plan, co-planning, co-tasking, action guards, parallel tasks, plan learning and retrieval.

**Steal:**
- human intervention at the right moments;
- plan visibility;
- action guards for consequential operations;
- learning from prior plans;
- clear statuses for needs-input / running / complete.

**ZEUS optimization:** action guards become command authorization gates; plan steps become operation objectives; intervention can occur via the map rather than only chat/plan panels.

### 4. LangGraph Studio

**Relevant pattern:** graph visualization, run from UI, edit state and rerun, manage threads/memory, add outputs to datasets.

**Steal:**
- state mutation + rerun for debugging;
- graph inspection;
- direct connection between execution and evaluation data.

**ZEUS optimization:** integrate this with temporal replay: zoom into an operation, rewind, alter a decision/context input, and replay from that point.

### 5. AutoGen Studio

**Relevant pattern:** visual prototyping and composition of multi-agent workflows; agent/tool/model/team components.

**Steal:**
- declarative team representation;
- ability to see team composition.

**Avoid:** treating a node editor as the whole product. ZEUS should compile common organizations from formations/intents, with explicit configuration available when needed.

### 6. OpenHands / Agent Canvas

**Relevant pattern:** browser UI, backend, workspace, and agent/model are separate concepts.

**Steal:** keep workspace/execution boundary explicit. A unit's visual presence must not blur which repo/container/worktree it can actually modify.

---

## B. Spatial / world interfaces

### 7. WorkAdventure

**Relevant pattern:** open-source virtual office, customizable worlds, avatars, proximity-triggered communication and social presence.

**Steal:**
- presence as a spatial property;
- lightweight spontaneous interactions;
- configurable maps/rooms;
- world as a social layer.

**Avoid:** making navigation itself mandatory for operational actions. Teleport/search/target-lock must exist.

### 8. OpenRA / OpenHV

**Relevant pattern:** RTS command maps, minimaps, fog, direct selection, spatial grouping, mission scripting, spectator/replay patterns.

**Steal as interaction research only:**
- minimap as company-wide anomaly/position overview;
- fog as uncertainty;
- group selection / control groups;
- direct action on a target;
- clear separation between strategic map and detail panels;
- replay as a first-class understanding tool.

**Licensing caution:** OpenRA is GPL-3.0. Mine interaction patterns; do not casually copy source/UI assets into a proprietary product.

---

## C. Canvas / graph / rendering references

### 9. tldraw

**Relevant pattern:** infinite canvas, custom shapes, multiplayer, agent/canvas experiments, workflow starter kit, branching conversations.

**Steal:** semantic infinite-canvas interaction research and rapid prototype ideas.

**Licensing caution:** the main SDK uses tldraw's own production license. Starter kits/examples may have separate terms. Do not assume the full SDK is permissively open source.

### 10. Flowise AgentFlow / React Flow family

**Relevant pattern:** visual agent/workflow nodes, connection validation, editing, natural-language flow generation.

**Steal:** connection validation and explicit topology editing when a user drills into a formation.

**ZEUS optimization:** use node-level editing only at the detailed organization-design layer, not as the default operator surface.

### 11. Sigma.js

**Relevant pattern:** WebGL graph visualization for thousands of nodes/edges.

**Use case:** ZEUS Signals/communication overlay, knowledge relations, or cross-team dependency graphs at large scale.

### 12. Phaser / PixiJS / Colyseus

**Phaser:** mature web game framework with scenes, input, cameras, animation, tilemaps, Canvas/WebGL.

**PixiJS:** lower-level high-performance rendering layer; useful if ZEUS wants a custom visualization engine rather than game semantics.

**Colyseus:** authoritative real-time multiplayer state synchronization and room model; relevant for social presence, not necessarily core operational state.

---

## D. Research literature to mine

### Human-swarm interaction

Recent 2026 work demonstrates interfaces for 100+ agents and reports that macro control can scale far better than individual micro-management; interaction techniques are scenario-dependent. This is highly relevant to ZEUS formations, semantic zoom, and command-by-objective.

### Mixed-initiative human–AI collaboration

Recent research frames effective human-agent collaboration as dynamic contribution from both sides, including modeling when agents should act versus seek guidance. ZEUS should research adaptive initiative rather than a fixed “human always clicks approve” model.

### Ecological Interface Design

EID is specifically aimed at complex sociotechnical systems and emphasizes making constraints and meaningful relationships visible so users can adapt to novel situations. This is a strong theoretical basis for supply lines, bottlenecks, readiness, and operational terrain rather than decorative dashboard art.

### Zoomable interfaces

Classic ZUI research shows spatial organization and scale can support navigation, but overview maps are not automatically faster for every task. ZEUS therefore needs empirical comparison rather than assuming a world is better.

---

# Reference mining conclusion

No single reference solves the ZEUS problem.

The design opportunity is the intersection of:

```text
Agent Command Center
+ Human-Swarm Control
+ Ecological Interface Design
+ Semantic Zoom
+ RTS Direct Manipulation
+ Multiplayer Presence
+ Agent Evaluation / Replay
= ZEUS World
```

---

# 02 — Ten Extremely Experimental ZEUS Concepts

These are deliberately high-risk research concepts. Each should be prototyped cheaply and killed if it does not beat a baseline task.

## X1 — ZEUS Adaptive Battlefield

**Idea:** the map reorganizes itself around the current Commander's Intent and operator role. A delivery-speed objective pulls bottlenecks, review gates, dependencies and high-impact missions into the dominant visual field. A reliability objective reorganizes around incidents, risky services and readiness.

**Traditional UI replaced:** static sidebar + manually configured dashboards + saved filters.

**Agentic research:** a layout agent learns which entities/relationships matter for a given task and produces a bounded layout recommendation. A second agent critiques whether the layout hides important state.

**Experiment:** compare static map vs adaptive map on 20 “find the critical issue” tasks.

**Kill if:** users become spatially disoriented or time-to-target worsens.

---

## X2 — ZEUS Formation Compiler

**Idea:** arrange agents/teams into a visual formation and have ZEUS compile the gesture into an organization topology: recon pair, parallel swarm, spearhead lead+specialists, review perimeter, pipeline, best-of-N tournament.

**Traditional UI replaced:** YAML/JSON team config + DAG editor + model/tool forms.

**Agentic research:** mine mission traces to discover common topology motifs and ask an organization-design agent to propose a minimal vocabulary of formations.

**Experiment:** configure the same 10 teams with forms, node editor, and formation UI; measure completion time and configuration errors.

**Kill if:** formation metaphors cannot faithfully represent real execution semantics.

---

## X3 — ZEUS Fog Intelligence

**Idea:** unknowns, unsupported assumptions and weakly-evidenced areas become literal fog. Recon agents reduce fog only when they publish evidence with provenance and confidence.

**Traditional UI replaced:** uncertainty fields, research checklists, hidden assumptions in notes.

**Agentic research:** evidence-classification agent maps mission claims to `known / contested / stale / unknown`; skeptic agent tests whether fog is warranted.

**Experiment:** ask operators to identify the riskiest unsupported assumption with/without fog.

**Kill if:** fog becomes a noisy confidence visualization rather than actionable uncertainty.

---

## X4 — ZEUS Ghost Battalion

**Idea:** overlay “ghosts” of similar past missions on the current operation. You can see where previous teams stalled, what information arrived late, where reviews rejected work, and which formation eventually succeeded.

**Traditional UI replaced:** searching old tickets, Git history, incident docs, chat history, prior agent sessions.

**Agentic research:** similarity agent retrieves relevant historical missions; causal summarizer extracts only comparable events; contradiction agent warns when the old case is misleading.

**Experiment:** diagnose five recurring failure classes using normal search versus ghost overlay.

**Kill if:** retrieval false positives create anchoring bias.

---

## X5 — ZEUS Intent Painting

**Idea:** draw/lasso a region or group and state an outcome: “recon these unknowns”, “stabilize this chain”, “review everything crossing this boundary”, “keep this objective under $20”. The gesture becomes a typed mission/policy.

**Traditional UI replaced:** selecting many rows, creating subtasks, assigning owners, setting filters/labels/budgets individually.

**Agentic research:** command compiler converts gesture + spatial target + natural language into an explicit intent contract; verifier agent checks scope ambiguity before execution.

**Experiment:** multi-object selection and bulk intervention tasks.

**Kill if:** users cannot reliably predict the scope of a painted command.

---

## X6 — ZEUS Cognitive Logistics

**Idea:** context, memory, credentials, tools, compute, schemas and environments appear as supply routes. Operators can see when a squad is “undersupplied” and can prioritize or reroute context/tools without opening separate settings pages.

**Traditional UI replaced:** context inspector + secrets status + dependency pages + environment status + agent tool configuration.

**Agentic research:** context compiler predicts minimum useful context for each role; logistics agent detects oversupply/undersupply; evaluator measures success/cost impact.

**Experiment:** resolve blocked-agent scenarios with conventional diagnostics vs supply map.

**Kill if:** the abstraction hides exact security/permission state.

---

## X7 — ZEUS Stigmergic Terrain

**Idea:** the world accumulates heat trails from repeated events. Repeated failures create hazardous terrain; frequently successful handoff paths become roads; ignored knowledge becomes overgrown; repeated agent tool sequences become visible “supply corridors”.

**Traditional UI replaced:** trend analysis across run logs and hidden process-mining dashboards.

**Agentic research:** process-mining agents cluster event sequences; anomaly agent distinguishes meaningful recurrence from volume artifacts.

**Experiment:** ask users to find the best automation/refactor opportunity from 500 historical missions.

**Kill if:** frequency is mistaken for importance.

---

## X8 — ZEUS Counterfactual Command Room

**Idea:** fork the world into several simulated futures. “Add reviewer”, “change model”, “parallelize”, “delay deployment”, “retrieve older case”. Each branch runs replay/simulation against frozen evidence/evals and visualizes different consequences.

**Traditional UI replaced:** manually opening separate worktrees/sessions, spreadsheet comparison, ad-hoc what-if reasoning.

**Agentic research:** experiment designer proposes meaningful variants; simulator/replay agent executes; judge produces Pareto comparison rather than a fake single score.

**Experiment:** architecture/agent-team decision tasks with hidden ground truth.

**Kill if:** simulations are not predictive enough to guide real decisions.

---

## X9 — ZEUS Autonomous Staff Officer

**Idea:** a persistent staff agent watches the operator's command patterns and proposes/executes low-risk coordination: group similar alerts, prepare handoffs, summon a known specialist, prepare AAR, pre-stage evidence, reorganize the view around the next likely decision.

**Traditional UI replaced:** manual coordination glue and repetitive navigation.

**Agentic research:** learn a task-scoped operator model; evaluate proactive actions by accepted/rejected intervention rate and time saved.

**Experiment:** shadow mode for several weeks; record what it would have done without executing.

**Kill if:** false-positive interventions interrupt more than they save.

---

## X10 — ZEUS Living Headquarters

**Idea:** operational and social presence share the world. Humans and agents have locations based on real team/mission state. Cross-team “intel events”, briefings, office hours, research quests and harmless social interactions are generated from real organizational activity.

**Traditional UI replaced:** presence dots + scattered team-status messages + some lightweight internal social tooling.

**Agentic research:** social summarizer generates non-sensitive, low-noise cross-team briefings; knowledge broker identifies useful cross-team encounters.

**Experiment:** measure whether people discover relevant work outside their team more often without increasing interruptions.

**Kill if:** it becomes mandatory virtual-office theatre or leaks sensitive work context.

---

# 03 — Ten Business-Value-First ZEUS Concepts

These concepts should be prioritized before the most cinematic world mechanics because they can directly reduce engineering time, delivery latency, failure rate, or coordination cost.

## B1 — ZEUS Satellite: Anomalies Only

**Function:** one command removes healthy activity and shows only incidents, blockers, waiting approvals, cost anomalies, stale context, abnormal queues and unanswered help requests.

**Replaces:** alert dashboard + approval inbox + queue dashboard + partial status meeting.

**Value hypothesis:** reduce “what needs me right now?” time to under 10 seconds.

**Metric:** time-to-first-correct-intervention; missed-critical-state rate.

---

## B2 — ZEUS Reinforcement Router

**Function:** a blocked team fires a help request. ZEUS selects candidate humans/agents using capability evidence, similar-mission success, current load, permissions and context fit, then prepares the handoff.

**Replaces:** asking Slack who knows X + agent browser + context copy/paste + assignment.

**Value hypothesis:** cut blocked time and unnecessary escalations.

**Metric:** blocked_minutes, handoff success, time-to-green after reinforcement.

---

## B3 — ZEUS Collision Control

**Function:** detects agents/teams modifying overlapping files, duplicating research, making incompatible decisions, or targeting the same scarce environment; visualizes convergence before it becomes damage.

**Replaces:** discovering collisions in Git/Slack/CI after work is already done.

**Value hypothesis:** reduce duplicate work and merge/rework cost.

**Metric:** avoided overlap events, merge conflict time, duplicate agent spend.

---

## B4 — ZEUS Command Authorization

**Function:** all consequential gates appear in one operational command post with evidence, diff, risk, owner, expiry, rollback and suggested decision.

**Replaces:** approvals spread across GitHub, workflow UI, chat, deployment tools and email.

**Value hypothesis:** reduce human wait time without weakening governance.

**Metric:** human_wait_minutes, approval turnaround, unsafe approval rate.

---

## B5 — ZEUS Frontline Optimizer

**Function:** missions move toward the front based on explicit objective contribution, deadlines, dependency blocking, evidence strength, customer impact and risk. Operator can inspect why.

**Replaces:** priority labels + roadmap spreadsheets + standup reprioritization.

**Value hypothesis:** increase time spent on high-leverage work.

**Metric:** value-weighted lead time; percentage of work later classified as low-priority/rework.

---

## B6 — ZEUS Logistics Health

**Function:** context, tools, credentials, compute, environment readiness and upstream dependencies are summarized as readiness/supply state before and during missions.

**Replaces:** manual preflight across service dashboards/settings/docs.

**Value hypothesis:** prevent known non-retryable failures before run time.

**Metric:** preventable-failure rate, failed-start rate, diagnosis time.

---

## B7 — ZEUS After-Action Learning

**Function:** every completed mission produces a compact AAR: outcome, timeline, interventions, failure seams, reusable findings, changed assumptions, costs, and candidate knowledge updates.

**Replaces:** manual postmortem + retrospective + memory/documentation chores.

**Value hypothesis:** improve future missions while reducing documentation burden.

**Metric:** AAR reuse rate, retrieval usefulness, repeat-failure reduction.

---

## B8 — ZEUS Workflow Compression

**Function:** mines agent traces for stable repeated tool-call sequences and proposes deterministic composite tools/meta-tools, then evaluates them before promotion.

**Replaces:** agents repeatedly reasoning through identical low-variance procedures.

**Value hypothesis:** lower cost/latency and reduce hallucination surface.

**Metric:** LLM calls per mission, cost, latency, success/regression rate.

**Research anchor:** Microsoft Research's 2026 Agent Workflow Optimization work reports benefits from converting recurring tool sequences into deterministic meta-tools.

---

## B9 — ZEUS Intelligence Command

**Function:** cross-team autonomous research cell consumes failures, successes, customer demand, support signals, delivery metrics, agent traces and internal knowledge to identify high-leverage improvement hypotheses against an explicit success criterion.

**Replaces:** scattered improvement ideas, periodic innovation meetings, ad-hoc research.

**Value hypothesis:** continuously produce better-ranked improvement opportunities.

**Metric:** percentage of accepted hypotheses that beat baseline; realized objective impact; research cost per validated improvement.

---

## B10 — ZEUS Objective Ledger

**Function:** every mission and candidate improvement can be traced to the current business/engineering success criteria (delivery speed, quality, revenue, adoption, reliability) with evidence and uncertainty.

**Replaces:** disconnected OKRs, project roadmaps, engineering metrics and portfolio spreadsheets.

**Value hypothesis:** make “why are we doing this?” answerable from any point in the world.

**Metric:** prioritization agreement, abandoned low-value work, time from new evidence to reprioritization.

---

# 04 — Agentic Research Program

## Goal

Use agent teams to research and experimentally validate the ZEUS interaction model before the world is implemented.

## ZEUS Research Command

```text
Research Commander
│
├── UI Recon Agent
├── Human-Swarm / HCI Scholar
├── Agent Systems Analyst
├── Game Interaction Pattern Miner
├── Organizational Science Analyst
├── Skeptic / Red Cell
├── Benchmark Designer
├── Architecture Mapper
└── Synthesis Officer
```

### UI Recon Agent

Mines current coding-agent UIs, orchestration systems, workflow tools, observability consoles, virtual offices, strategy interfaces and spatial tools.

Output: interaction pattern catalogue with screenshots/links, not vague product summaries.

### Human-Swarm / HCI Scholar

Researches supervisory control, human-swarm interaction, situation awareness, ecological interface design, zoomable UIs, cognitive load, interruption and mixed-initiative collaboration.

Output: design principles with empirical support and limitations.

### Agent Systems Analyst

Maps proposed UI gestures to real agent/runtime primitives: isolation, subagents, worktrees, approval gates, context, agent memory, event streams, evaluation and replay.

Output: feasibility matrix.

### Game Interaction Pattern Miner

Studies strategy/simulation interaction patterns — selection, groups, minimaps, fog, camera controls, replay, hotkeys, alerts, production queues — purely as interface mechanisms.

Output: pattern → software-operation translation table.

### Organizational Science Analyst

Studies team topology, staffing, handoffs, coordination cost, shared mental models and cross-team information flow.

Output: organization metaphors that correspond to real coordination structures.

### Skeptic / Red Cell

Attempts to prove the world is slower, distracting, manipulative, inaccessible, or operationally misleading.

Output: failure modes and kill criteria.

### Benchmark Designer

Turns every proposed interaction into comparable tasks with baseline conventional UI and measurable outcomes.

### Architecture Mapper

Maps validated interactions to required domain state/events without choosing a renderer prematurely.

### Synthesis Officer

Produces ranked recommendations:

- BUILD FIRST
- PROTOTYPE
- RESEARCH MORE
- COSMETIC ONLY
- REJECT

---

# Research missions

## RUX-01 — Human-Swarm Command Vocabulary

**Question:** what group-level controls allow one engineer to direct 10, 50, 100+ agents without O(N) attention?

Research:
- group/formation commands;
- hierarchical control;
- adaptive autonomy;
- macro vs micro interaction;
- task-dependent control methods.

Output: minimal ZEUS command grammar.

## RUX-02 — Semantic Zoom and Spatial Memory

**Question:** when is zoomable spatial organization faster than hierarchy/search/sidebar navigation?

Research:
- semantic zoom;
- overview/minimap tradeoffs;
- spatial memory;
- focus+context techniques;
- navigation disorientation.

Output: zoom levels and information budget per level.

## RUX-03 — Mixed Initiative

**Question:** when should ZEUS act, suggest, wait, escalate, or ask a human?

Research:
- co-planning;
- co-tasking;
- adaptive autonomy;
- trust calibration;
- interruption costs;
- action guards.

Output: initiative policy and UX states.

## RUX-04 — Situation Awareness / Ecological Display

**Question:** which relationships must the world expose so an operator can reason under novelty?

Research:
- constraints;
- dependencies;
- readiness;
- bottlenecks;
- failure propagation;
- resource limits.

Output: visual invariants for terrain, supply, gates and alert state.

## RUX-05 — Cognitive Logistics

**Question:** can context/memory/tools/credentials be represented as logistics without hiding exact technical state?

Output: supply abstraction schema + drill-down requirements.

## RUX-06 — Communication Compression

**Question:** how can hundreds of inter-agent messages become a few meaningful signals?

Research:
- typed messages;
- event aggregation;
- causal summaries;
- information routing;
- attention management.

Output: ZEUS Signals channels and summarization rules.

## RUX-07 — Formation Discovery

**Question:** which recurring team topologies actually appear in successful missions?

Method:
- mine traces;
- cluster organization graphs;
- correlate with task families and outcomes;
- identify minimal visual archetypes.

Output: formation library and evidence per formation.

## RUX-08 — Gamification Without Goodhart

**Question:** what social/game mechanics improve engagement without incentivizing spam, risk, token spend or competition over bad proxies?

Output: reward policy + prohibited metrics + opt-out/social/privacy rules.

## RUX-09 — Causal Replay / Ghost Operations

**Question:** can historical similarity + replay make diagnosis faster without anchoring the operator to irrelevant prior cases?

Output: ghost-overlay relevance criteria and contradiction warnings.

## RUX-10 — Autonomous Intelligence Command

**Question:** can a cross-team research organization identify higher-leverage improvements than normal backlog generation?

Method:
- freeze success objective;
- generate hypotheses from traces + customer/product signals;
- adversarially challenge each;
- run sandbox experiments;
- compare against historically selected work.

Output: leverage-ranking methodology and first experiment set.

## RUX-11 — World vs Dense UI Benchmark

**Question:** which tasks are genuinely faster in the world and which should stay conventional?

Output: routing policy such as:

```text
world-first: situation awareness, multi-team coordination, anomaly scanning, dependency reasoning
hybrid: debugging, team formation, replay, approvals
dense-first: code diff, log text, SQL, exact configuration, large tables
```

## RUX-12 — Accessibility and Low-Motion Command Mode

**Question:** can the same command model work without animation/spatial navigation for users who prefer keyboard/dense modes or need reduced motion?

Output: equivalent keyboard/command palette and low-motion projection.

---

# 05 — Evaluation Protocol

## Why this is mandatory

A world UI can feel impressive while being slower. The product claim should therefore be falsifiable:

> ZEUS World earns a primary workflow only when it matches or beats the conventional baseline on measurable operator outcomes, or creates a capability that the baseline does not provide.

## Core metrics

### Efficiency
- time to locate relevant mission/agent/problem;
- time to correct action;
- clicks / pointer actions;
- keystrokes;
- number of page/context switches;
- time spent waiting for view loads/navigation.

### Correctness
- correct target selected;
- correct action chosen;
- missed blocker/anomaly rate;
- unsafe or unintended action rate;
- configuration error rate.

### Situation awareness
After a short exposure, ask:
- What is most urgent?
- What is blocked?
- Why?
- Which team owns it?
- What is waiting on you?
- Which operations are likely to collide?
- Where is uncertainty highest?

### Cognitive load
Use a lightweight workload survey plus behavioral proxies:
- backtracking;
- repeated opens/closes;
- hover hunting;
- search usage;
- accidental commands.

### Agentic quality
- unnecessary agent spawns;
- duplicate work;
- human interventions;
- blocked minutes;
- handoff loss;
- cost per accepted outcome.

## Baseline task suite

### T1 — Find the critical blocker
Given 25 active missions, identify the one requiring immediate intervention and explain why.

**Baseline:** table/status dashboard.
**ZEUS:** satellite/anomaly view.

### T2 — Reinforce a blocked mission
Find the best specialist and provide necessary context.

**Baseline:** agent directory + Slack + mission page.
**ZEUS:** distress request + reinforcement router.

### T3 — Diagnose missing prerequisite
Determine whether a failing agent lacks context, credentials, tool access, environment readiness, or upstream data.

**Baseline:** multiple diagnostic panels.
**ZEUS:** logistics map + exact drill-down.

### T4 — Identify team collision
Two teams are independently changing an overlapping area.

### T5 — Configure a parallel team
Build a team with two scouts, two independent implementers and one reviewer.

**Compare:** form/YAML vs node editor vs formation compiler.

### T6 — Find highest uncertainty
Locate the most consequential unsupported assumption.

### T7 — Review approval request
Make a production/release decision from evidence, risk, diff and rollback.

### T8 — Understand a failed mission
Identify the first consequential divergence point.

**Compare:** logs/chat/Git vs temporal replay.

### T9 — Find a reusable learning
Determine whether a previous mission contains a relevant fix or pattern.

### T10 — Reprioritize portfolio
Given new customer/reliability evidence, determine which mission should move to the front.

### T11 — Explain organizational health
In 30 seconds, summarize what is running, blocked, waiting, risky and over budget.

### T12 — Switch from strategic to exact evidence
Move from company view to the exact code diff/log/evidence item without losing mission context.

## Target thresholds for a concept to graduate

A candidate should generally achieve at least one of:

- >=25% faster median task completion;
- >=40% fewer navigation/context-switch actions;
- materially lower missed-state/error rate;
- materially better situation-awareness score;
- unique capability not available in baseline with acceptable workload.

And it must not cause:

- worse consequential decision accuracy;
- hidden provenance;
- unclear action scope;
- increased unsafe actions;
- major accessibility regression.

## Prototype ladder

1. **Paper/Figma storyboard** — test comprehension only.
2. **Clickable 2D mock** — test navigation/commands with fake data.
3. **Replay prototype** — feed historical mission event traces; no live actions.
4. **Shadow mode** — connected to live state but commands do not execute.
5. **Sandbox command mode** — actions execute only in isolated missions.
6. **Bounded production mode** — only after measured advantage and policy gates.

---

# 06 — State and Interaction Model

## Principle

Do not build the world around sprites. Build it around a typed organizational state model and event stream.

## Core domain entities

```text
Organization
Campaign
Mission
Objective
Team
Agent
Human
Capability
Artifact
Decision
Gate
Environment
Repository / Worktree / Sandbox
Tool
Context Packet
Knowledge Item
Evidence
Dependency
Communication
Evaluation
Incident
Resource / Budget
```

## Minimum world-facing event taxonomy

### Mission
- mission.created
- mission.started
- mission.blocked
- mission.resumed
- mission.completed
- mission.failed
- mission.cancelled
- mission.priority_changed

### Team / agent
- team.assembled
- team.reorganized
- agent.assigned
- agent.started
- agent.waiting
- agent.needs_help
- agent.completed
- agent.failed
- agent.context_pressure

### Communication
- help.requested
- evidence.published
- claim.challenged
- decision.requested
- decision.made
- handoff.started
- handoff.accepted
- warning.broadcast

### Logistics / readiness
- context.missing
- context.stale
- credential.unavailable
- tool.unavailable
- environment.unready
- dependency.blocked
- compute.constrained
- budget.threshold

### Engineering execution
- branch.created
- worktree.created
- file.changed
- conflict.detected
- tests.started
- tests.failed
- tests.passed
- review.requested
- review.rejected
- review.approved
- deploy.started
- deploy.failed
- deploy.succeeded
- rollback.started

### Evaluation / learning
- eval.started
- eval.completed
- champion.challenged
- candidate.promoted
- candidate.rejected
- learning.extracted
- knowledge.accepted
- contradiction.detected
- meta_tool.proposed

## Projection rule examples

```text
mission.blocked + credential.unavailable
=> squad halted + ZEUS Logistics route marked unavailable

conflict.detected(file overlap)
=> convergence/collision marker between two teams

agent.needs_help
=> distress signal available

context.stale
=> intelligence/supply route marked stale

gate.awaiting_human
=> command authorization marker

high uncertainty claim cluster
=> fog density increases in affected objective
```

## Command compiler

World interactions should compile into typed commands.

### Example: drag specialist onto mission

```json
{
  "command": "mission.add_specialist",
  "mission_id": "M-184",
  "capability": "oauth-authentication",
  "candidate": "agent:hermes-17",
  "handoff_mode": "compiled_context",
  "reason": "operator_direct_manipulation"
}
```

### Example: draw a boundary and request review

```json
{
  "command": "scope.create_review_mission",
  "targets": ["repo:A/path/x", "repo:A/path/y"],
  "success_criteria": ["no regression", "security review"],
  "risk": "medium"
}
```

Before execution:

```text
Gesture / world command
        ↓
Intent compiler
        ↓
Scope preview
        ↓
Permission / budget / risk check
        ↓
Human confirmation if required
        ↓
Runtime command
        ↓
Events
        ↓
World + dense UI projections update
```

## Two independent state layers

### Operational truth
Authoritative backend state.

### World presentation
Camera, layout, animation, selected targets, avatar cosmetics, harmless social state.

Never let presentation state silently become operational truth.

## Search remains essential

A world without universal search becomes a maze.

Minimum command/search actions:

```text
Go to mission
Go to agent
Go to repo
Go to incident
Go to approval
Ask ZEUS
Show blockers
Show unknowns
Show collisions
Show things waiting on me
```

---

# 07 — Technical Options (Research, Not Commitment)

## Recommended architecture direction to test

### Hybrid shell + spatial renderer

```text
DOM / application shell
- command palette
- exact tables
- approvals
- code/diff/log viewers
- accessible keyboard UI

        +

Spatial canvas / world renderer
- map
- units
- formations
- routes
- fog
- semantic zoom
- animations
- presence

        +

Shared authoritative domain/event layer
```

This avoids forcing source code, SQL, exact configuration and long-form evidence into a game canvas.

---

## Option A — Phaser

### Why research it
- mature web game framework;
- scenes/cameras/input/animation/tilemaps;
- Canvas/WebGL;
- TypeScript/JavaScript;
- large example ecosystem.

### Best fit
A truly game-like 2D operational world with avatars, bases, animation, camera transitions and map interaction.

### Risk
Can encourage game architecture to leak into application/domain architecture. Keep it as renderer/input layer only.

---

## Option B — PixiJS

### Why research it
High-performance 2D renderer with lower-level control than a full game framework.

### Best fit
If ZEUS needs a custom visualization/interaction engine without physics/game concepts.

### Risk
More UI/world behavior must be built by the team.

---

## Option C — DOM/SVG/Canvas prototype first

### Why research it
Your existing Agent Factory UI direction has historically favored a simple web stack. A stripped prototype can validate interaction concepts without committing to a game engine.

### Best fit
First replay/shadow-mode tests.

### Risk
May not represent final performance/feel of large animated worlds.

---

## Option D — WorkAdventure fork/integration research

### Why research it
It already demonstrates customizable virtual worlds, avatars and proximity interactions.

### Best fit
Social / company-presence experiments.

### Do not assume
That its world model is appropriate for the primary operational command system. Treat it as a reference/prototype candidate, not the ZEUS backend.

---

## Option E — tldraw / infinite canvas

### Why research it
Excellent interaction model for semantic zoom, custom shapes, collaborative canvas and agent-modifiable canvas prototypes.

### Licensing caution
The current main SDK requires a production license; examples/starter kits may have separate licenses. Validate licensing before architectural commitment.

---

## Option F — React Flow / Flowise-style node canvas

### Best fit
Detailed formation/org topology editor at low zoom, not the main command world.

### Research question
Can ZEUS use formation primitives for 80% of composition and expose a node editor only for the remaining complex cases?

---

## Option G — Sigma.js

### Best fit
Large communication/dependency/knowledge overlays where thousands of graph elements may be visible.

---

## Option H — Colyseus

### Why research it
Authoritative server model, real-time synchronized state, room model, presence/matchmaking primitives.

### Best fit
Optional multiplayer/social presence or dedicated shared-world sessions.

### Important
Operational mission truth likely already belongs in the Agent Factory/control plane. Do not duplicate it into a game server merely to animate avatars.

---

# Technical spike sequence

Do not start with “build the map.”

1. Build a **static event-to-world projection** from recorded missions.
2. Add semantic zoom and target-lock.
3. Add two direct commands (reinforce, inspect blocker).
4. Run benchmark vs dense baseline.
5. Add formation compiler prototype.
6. Add social/presence only after operational UX proves useful.

# Renderer decision experiment

Implement the same micro-scenario in no more than 1–2 days per option:

- 50 missions;
- 100 agents;
- 300 communication edges;
- animated state changes;
- zoom company → agent;
- select group;
- target-lock;
- one direct command;
- exact detail drawer.

Score:

- development speed;
- frame rate;
- memory;
- input latency;
- accessibility integration;
- DOM overlay integration;
- testability;
- agent-code-generation quality;
- license/commercial fit.

---

# 08 — Ready-to-Run Research Prompts

These prompts are intended for independent agent/deep-research missions. Require citations, source quality, contradictions, and falsifiable experiments.

## Prompt 1 — Human-Swarm Command

**Objective:** Design an evidence-backed control vocabulary for one human supervising 10–100+ software agents. Review human-swarm interaction, supervisory control, adaptive autonomy, hierarchical control and mixed-initiative systems. Separate physical-robot specifics from generalizable HCI results. For each interaction method, map it to software-agent command use cases. Deliver: prior art, empirical findings, limitations, candidate ZEUS interactions, experiments, and kill criteria.

## Prompt 2 — Semantic Zoom

**Objective:** Determine when a zoomable spatial UI can outperform hierarchical navigation for complex software/agent operations. Research semantic zoom, focus+context, minimaps/overviews, spatial memory, graph navigation and disorientation. Produce recommended abstraction levels, information density rules, keyboard equivalents, and benchmark tasks.

## Prompt 3 — Strategy-Game Interaction Mining

**Objective:** Study open-source strategy/simulation interfaces strictly for interaction design patterns: selection, groups, minimap, fog, queues, alerts, replay, direct manipulation, hotkeys, camera behavior and information layering. Do not copy visual assets/trade dress. Translate patterns into agent-team operations and identify where the metaphor breaks.

## Prompt 4 — Human-in-the-Loop Agent UX

**Objective:** Review current human-centered agent interfaces including Magentic-UI, Codex, Cursor Agents, LangGraph Studio, OpenHands and AutoGen Studio. Compare co-planning, parallelism, intervention, action guards, state editing, worktree isolation, artifact review, memory and evaluation. Identify missing interaction primitives for supervising organizations rather than single agents.

## Prompt 5 — Ecological Interface Design for Agent Operations

**Objective:** Apply Ecological Interface Design and situation-awareness theory to an agent organization. Determine the invariants/constraints operators need to perceive: authority, dependencies, readiness, context provenance, risk, budget, workload, failure propagation, uncertainty and gates. Propose visual encodings that support novel failure diagnosis.

## Prompt 6 — Agent Communication Compression

**Objective:** Design a system that converts thousands of agent/tool/team events into a small number of typed, actionable communication signals without destroying auditability. Research event abstraction, causal summarization, attention routing, observability aggregation and multi-agent communication protocols. Define false-positive/false-negative evaluation.

## Prompt 7 — Formation Discovery From Mission Traces

**Objective:** Given a corpus of mission traces, develop a method to infer recurring organizational topologies, task families and successful handoff patterns. Determine whether a small formation vocabulary can represent most useful teams. Include clustering features, outcome controls, confounding risks and visualization ideas.

## Prompt 8 — Gamification and Goodhart

**Objective:** Research gamification in technical/work environments with emphasis on intrinsic motivation, cooperation, autonomy and failure modes. Identify mechanics that strengthen remote-team cohesion without rewarding spam, unnecessary agent use, unsafe speed, ranking anxiety or performative work. Produce a ZEUS reward doctrine and opt-out/accessibility requirements.

## Prompt 9 — Causal Replay and Counterfactuals

**Objective:** Research causal debugging, workflow replay, deterministic reproduction, process mining, provenance and counterfactual analysis for agent systems. Design a ZEUS temporal replay model that can show where a mission diverged and test bounded alternative configurations without presenting simulation as certainty.

## Prompt 10 — Autonomous ZEUS Intelligence Command

**Objective:** Design a bounded autonomous research organization that consumes agent successes/failures, engineering telemetry, customer requests, support signals, product usage and internal knowledge to identify highest-leverage changes against a frozen success criterion. Include evidence ranking, adversarial review, experiment generation, sandbox evaluation, portfolio allocation and governance. Explicitly prevent the system from rewriting its own success metric.

## Prompt 11 — Technical Renderer Spike

**Objective:** Compare Phaser, PixiJS, DOM/SVG/Canvas, WorkAdventure-based prototyping, infinite-canvas frameworks and graph renderers for a hybrid agent command world. Evaluate performance, semantic zoom, animations, large entity counts, DOM overlays, accessibility, testing, multiplayer, licensing and maintainability. Recommend experiments, not a final architecture based on preference.

## Prompt 12 — Adversarial Review

**Objective:** Assume ZEUS World is a bad idea. Find the strongest evidence that spatial/gamified command interfaces can increase navigation time, distraction, cognitive load, accessibility problems, social pressure, ambiguity or operator error. Design the cheapest experiments that could disprove the world concept before implementation.

---

# 09 — Implementation Readiness Gates

The world should not move into a full build just because the concept is exciting.

## Gate 1 — Primary dense Mission Console exists

The product must already expose the operational truth needed to answer:

- what is running?
- what is blocked?
- why?
- what is waiting on me?
- what evidence exists?
- what changed?
- what did it cost?
- can I intervene/replay?

Reason: the world needs a trustworthy state model to project.

## Gate 2 — Event/state taxonomy is stable enough

At minimum, mission/team/agent/blocker/gate/context/evidence/eval events must exist or be derivable reliably.

## Gate 3 — 10–20 benchmark traces exist

Use real completed and failed missions. The first world prototype should run entirely from replay.

## Gate 4 — Three world interactions beat baseline

Recommended first candidates:

1. ZEUS Satellite anomaly scan.
2. Reinforcement routing/direct deployment.
3. Logistics/readiness diagnosis.

If these do not beat the dense UI, do not assume more animation will fix the problem.

## Gate 5 — Formation compiler proves representational value

Show that at least several recurring team topologies can be configured faster with no loss of explicitness.

## Gate 6 — Accessibility/keyboard equivalence

Every critical command has a non-spatial route:

```text
/zeus blockers
/zeus go M-184
/zeus reinforce M-184
/zeus approvals
/zeus replay M-184
```

Reduced-motion mode must preserve operational content.

## Gate 7 — No Goodhart reward loop

Game rewards are reviewed against bad incentives before social rollout.

## Gate 8 — Social/presence privacy rules

World presence must not accidentally reveal:

- sensitive client context;
- confidential mission names;
- employee performance judgments;
- private agent conversations;
- inactivity as a proxy for employee performance.

## Gate 9 — Technical spike completed

Choose renderer only after comparable prototypes.

## Gate 10 — World and dense UI share the same command/state contracts

No separate “game backend” for operational truth.

---

# Recommended research order

## Wave A — Prove speed
1. RUX-11 World vs Dense UI benchmark.
2. RUX-04 ecological/situation awareness.
3. RUX-02 semantic zoom.
4. Prototype Satellite + target-lock + exact drilldown.

## Wave B — Prove agentic advantage
5. RUX-01 human-swarm command grammar.
6. RUX-03 mixed initiative.
7. RUX-07 formation discovery.
8. Prototype reinforcement + formation compiler.

## Wave C — Prove compounding value
9. RUX-05 cognitive logistics.
10. RUX-06 communication compression.
11. RUX-09 ghost/replay.
12. RUX-10 Intelligence Command.

## Wave D — Add the world/culture layer
13. RUX-08 gamification.
14. RUX-12 accessibility/low-motion.
15. social presence prototype.

---

# Initial BUILD / RESEARCH / DEFER recommendation

## BUILD FIRST (after baseline Mission Console)
- Satellite/anomalies-only view.
- Target-lock + command palette.
- Reinforcement router.
- Command authorization post.
- After-action replay/AAR.

## PROTOTYPE EARLY
- semantic zoom;
- logistics visualization;
- formations;
- fog/uncertainty;
- collision control.

## RESEARCH DEEPLY
- adaptive battlefield layout;
- ghost battalion;
- intent painting;
- counterfactual futures;
- autonomous staff officer;
- autonomous Intelligence Command opportunity selection.

## DEFER UNTIL OPERATIONAL VALUE EXISTS
- full avatar world;
- social buildings;
- cosmetics;
- ranks/collectibles;
- large multiplayer world events.

The social layer can be excellent, but it should arrive on top of a command model already proven faster than ordinary enterprise UI.

---

# Sources

## Project / uploaded source base

- `Agent Factory Vision.txt` — Agent Army/Factory north-star concepts, Research Army, Collective Cognition, organizational presets, self-maintenance.
- `GAMIFIED_MISSION_CONTROL.md` — existing product direction for a living operations base, real-state gamification, Mission Control evolution.
- `agent_army_progress_dashboard.html` — staged capability roadmap including Mission Console, communication, cognition, dynamic assembly, debugger/simulation, evolution.
- `paul_russell_vision_to_value_roadmap.html` — Agentic IDE / Mission Console product sequencing and branding notes.
- `PLATFORM_COMPLETION_FEATURES.md` — customer/market learning and portfolio experimentation concepts.
- `INKWELL_FACTORY_IN_A_BOX.md` — sandbox isolation, fan-out, observation and harvesting implications.

## Current agent UIs / developer tools

### OpenAI Codex
- https://openai.com/index/introducing-the-codex-app/
- https://openai.com/codex/

### Cursor
- https://prod.cursor.com/help/ai-features/multi-agent
- https://prod.cursor.com/docs/configuration/worktrees
- https://cursor.com/changelog/3-0
- https://cursor.com/changelog/04-24-26

### Microsoft Magentic-UI
- https://www.microsoft.com/en-us/research/publication/magentic-ui-report/
- https://www.microsoft.com/en-us/research/blog/magentic-ui-an-experimental-human-centered-web-agent/
- https://github.com/microsoft/magentic-ui

### LangGraph Studio
- https://github.com/langchain-ai/langgraphjs/blob/main/docs/docs/concepts/langgraph_studio.md

### AutoGen Studio
- https://github.com/microsoft/autogen/blob/main/python/packages/autogen-studio/README.md
- https://github.com/microsoft/autogen/issues/4202

### OpenHands
- https://github.com/OpenHands/docs/blob/main/openhands/usage/agent-canvas/overview.mdx

### Flowise AgentFlow
- https://github.com/FlowiseAI/Flowise/blob/main/packages/agentflow/README.md

## Spatial / virtual world / game interaction references

### WorkAdventure
- https://github.com/workadventure/workadventure

### OpenRA
- https://github.com/OpenRA/OpenRA

### OpenHV
- https://github.com/OpenHV/OpenHV

## Canvas / graph / rendering

### tldraw
- https://github.com/tldraw/tldraw
- https://github.com/tldraw/workflow-template
- License: https://github.com/tldraw/tldraw/blob/main/apps/docs/content/community/license.mdx

### Sigma.js
- https://github.com/jacomyal/sigma.js/

### Phaser
- https://github.com/phaserjs/phaser

### Colyseus
- https://github.com/colyseus/colyseus

## Research

### Human-swarm interaction
- Finger-based 3D human-swarm interaction interface: Design and human-subject evaluation (2026): https://doi.org/10.1016/j.eswa.2026.132234
- Designing Effective Human-Swarm Interaction Interfaces: Insights from a User Study on Task Performance (IEEE SMC 2025 / indexed 2026): https://doi.org/10.1109/SMC58881.2025.11343025

### Mixed-initiative human–AI
- Adaptive Agents for Mixed-Initiative Human-AI Collaborations (AAAI 2025): https://doi.org/10.1609/aaai.v39i28.35220

### Ecological Interface Design
- Vicente, Ecological interface design: progress and challenges: https://pubmed.ncbi.nlm.nih.gov/12118874/

### Zoomable UI
- Navigation Patterns and Usability of Zoomable User Interfaces with and without an Overview: https://www.sciencedirect.com/science/article/pii/B9781558609150500184

### Agent workflow optimization
- Microsoft Research — Optimizing Agentic Workflows using Meta-tools: https://www.microsoft.com/en-us/research/publication/optimizing-agentic-workflows-using-meta-tools/

## Source-use rule

Treat these as references to mine for principles, evidence and implementation options. Do not copy protected visual assets, branding or trade dress. Check licenses before reusing code.
