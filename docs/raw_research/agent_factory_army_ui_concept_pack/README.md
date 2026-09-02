# Agent Factory — Army Command UI & Organizational Design Pack

## Purpose

This pack consolidates the concepts developed in the current design conversation into a reusable input for Agent Factory architecture, product design, research, and future implementation.

The pack intentionally separates:

1. **Primary Agentic IDE / Command Console** — the serious operating interface that should be built first.
2. **Army World / Battlefield View** — a spatial, highly gamified alternative projection over the same underlying state.
3. **Organizational architecture** — agents, squads, nested service designations, formations, commands, campaigns and doctrine.
4. **Coordination intelligence** — handoffs, collision detection, radio/signals, reinforcements, context logistics and command escalation.
5. **Autonomous improvement** — Advanced Projects Command / Black Site that mines company experience and runs controlled experiments.
6. **Metrics and learning** — especially Recurring Failure Rate and Preventable Recurrence Rate.
7. **Research program** — experimental and business-value-first research tracks.

## Core design rule

> The game world must not become a second source of truth. The Command Console and Battlefield View are projections of the same typed domain/event state and emit the same governed commands.

## Recommended reading order

1. `00_MASTER_INDEX.md`
2. `01_PRODUCT_VISION_AND_UI_LAYERS.md`
3. `02_PRIMARY_AGENTIC_IDE.md`
4. `03_ARMY_WORLD_UI.md`
5. `05_ORGANIZATION_HIERARCHY_AND_SERVICE_DESIGNATIONS.md`
6. `12_METRICS_HEALTH_AND_RECURRENCE.md`
7. `10_ADVANCED_PROJECTS_COMMAND_AUTONOMOUS_LAB.md`
8. `14_RESEARCH_BACKLOG_20_TRACKS.md`
9. `15_IMPLEMENTATION_ROADMAP.md`

## Historical material

The earlier ZEUS-branded world research is retained under `prior_research/` as prior art. The Army Command language supersedes the ZEUS world branding for the current design direction.
