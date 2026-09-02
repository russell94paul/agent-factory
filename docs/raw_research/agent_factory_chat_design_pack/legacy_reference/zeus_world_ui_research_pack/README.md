# ZEUS WORLD UI RESEARCH PACK

## Purpose

This pack defines a research program for a radically gamified, army-command-style ZEUS interface for operating agent teams. The goal is not to make a dashboard look like a game. The goal is to discover whether a spatial command world can let engineers understand, direct, intervene in, and learn from large agent organizations faster than conventional tabs, tables, queues, chats, and workflow pages.

**Status:** research-only. Do not commit to a rendering framework or world implementation until the interaction hypotheses are benchmarked.

## North-star hypothesis

> A spatial command interface can outperform a conventional agent dashboard when the world itself encodes ownership, priority, uncertainty, dependencies, communication, readiness, context supply, and organizational topology — and when macro commands operate on groups rather than forcing the user to micromanage individual agents.

## What is inside

1. `00_BASELINE_AND_DOCTRINE.md` — source-grounded starting point and design doctrine.
2. `01_REFERENCE_SYSTEMS.md` — current agent UIs, spatial worlds, graph/canvas systems, RTS interaction references, and what to steal/avoid.
3. `02_EXTREME_EXPERIMENTS.md` — 10 highly experimental interaction concepts.
4. `03_BUSINESS_VALUE_CONCEPTS.md` — 10 concepts optimized for engineering/business value.
5. `04_AGENTIC_RESEARCH_PROGRAM.md` — the autonomous research team and research missions to run before implementation.
6. `05_EVALUATION_PROTOCOL.md` — benchmark tasks, metrics, kill criteria, and comparison method against normal UI.
7. `06_STATE_AND_INTERACTION_MODEL.md` — domain/event model the world will need so game visuals remain truthful.
8. `07_TECHNICAL_OPTIONS.md` — technology/reference stack options, licensing cautions, and prototype paths.
9. `08_RESEARCH_PROMPTS.md` — ready-to-run prompts for agent research teams.
10. `09_IMPLEMENTATION_READINESS.md` — decision gates that must be passed before building the world.
11. `SOURCES.md` — research sources and links.

## Core rule

**No decorative telemetry.** If a building is burning, a supply route is broken, a squad is blocked, fog is present, a formation changes, or a unit requests reinforcement, that visual state must be backed by a real machine-readable state or explicitly marked as social/cosmetic.

## Research outcome we want

At the end of this pack's research program, ZEUS should have:

- a validated interaction vocabulary;
- a benchmark showing which world interactions beat conventional UI;
- a clear division between operational and cosmetic gamification;
- a domain/event model independent from the renderer;
- a shortlist of technical approaches;
- a list of concepts to build, defer, or kill;
- evidence for the first ZEUS World MVP.
