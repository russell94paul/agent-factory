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
