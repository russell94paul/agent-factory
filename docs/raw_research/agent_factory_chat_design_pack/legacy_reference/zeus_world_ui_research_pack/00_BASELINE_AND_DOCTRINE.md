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
