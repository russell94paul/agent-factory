# Release Notes

## 2026-08-31 — Claude Research subscription-first revision

- Removed the active OpenAI Deep Research API bridge and API-key requirement.
- Added `docs/CLAUDE_RESEARCH_WORKFLOW.md`.
- Added `claude-research-orchestrator`.
- Research waves now compile exact Claude Research prompt packets and a dependency-aware queue.
- Added deterministic raw-report ingestion checks.
- Rewrote kickoff instructions around repository evidence → narrow web search → Claude Research.
- Human research work is reduced to triggering a prepared Research job and returning the raw report.
- Kept provider-neutral seams so a supported automated Research adapter can be added later without changing downstream synthesis.

# Bootstrap Pack Release Notes

## Regenerated 2026-08-31

Added:

- web-first Remote Control / Claude Code web operating model;
- execution-surface decision policy;
- helper script for Remote Control worktree server mode;
- cloud-session launch examples;
- detailed source notes for Super Simple Software Factory;
- detailed source notes for Inkwell / Factory in a Box;
- expanded Bootstrap Commander prompt with dynamic session placement and automated research routing.

The architectural principle remains unchanged: reference implementations are mined for patterns and failure semantics, never treated as product templates.

## Vision/venture alignment update

Added:

- evidence-gated `ROADMAP_TO_VISION.md` rank progression;
- gamified Mission Control product direction and UI evolution;
- commercial/venture parallel track before full north-star completion;
- product positioning and entrepreneur scenario artifacts;
- R29 Customer & Market Learning Fabric;
- R30 Gamified Mission Control;
- R31 Commercial Autonomy & Governance;
- roadmap-rank-tracker and customer-learning-loop skills;
- platform progress schema;
- venture-wave-1 manifest;
- roadmap and venture flywheel diagrams;
- updated Bootstrap Commander instructions prioritizing communication, roadmap visibility and bounded commercial experimentation.

## Branding + kickoff refresh

- Corrected project boundary: this project is independent of the company's Zeus project/product family.
- Reframed working product names as Agent Army / Agent Factory / Command Forge / Venture Corps.
- Added `KICKOFF_GUIDE.md` with exact operator steps.
- Added `CLAUDE_KICKOFF_PROMPT.md` as a single copy/paste first-session prompt.
- Added `BRANDING_NOTE.md` and removed Zeus from the gamified Mission Control example.
