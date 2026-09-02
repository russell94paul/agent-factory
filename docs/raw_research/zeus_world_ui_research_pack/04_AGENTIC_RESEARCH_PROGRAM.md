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
