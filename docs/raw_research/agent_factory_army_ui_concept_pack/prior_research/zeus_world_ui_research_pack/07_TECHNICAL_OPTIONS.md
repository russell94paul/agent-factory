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
