# Agent Factory → Artificial Organization Platform Autonomous Bootstrap Pack

This pack is a **working bootstrap system**, not only a documentation bundle.

Its purpose is to let a Claude Code coordinator recover the existing Agent Factory, compile research, construct a dynamic build DAG, coordinate isolated parallel work, synthesize results, and progressively move more of the platform-building process into Agent Factory itself.

## Cost mode: Claude subscription first

The active bootstrap **does not require paid API usage**.

Research uses:

```text
Agent Factory repository evidence
        ↓
Claude Code web search for narrow questions
        ↓
Claude Research for deep multi-step questions
        ↓
Claude Code synthesis + project-state update
```

Claude Research is deliberately treated as a human-triggered execution surface in v0. Claude Code automates the queue, prompts, return contracts, ingestion, synthesis and downstream decisions. It does not pretend to have an undocumented programmatic Research launcher.

See `docs/CLAUDE_RESEARCH_WORKFLOW.md`.

## Start here

Read in this order:

1. `QUICKSTART.md`
2. `CLAUDE_KICKOFF_PROMPT.md`
3. `START_CLAUDE_HERE.md`
4. `VISION.md`
5. `ROADMAP_TO_VISION.md`
6. `BUILD_START_TO_FINISH.md`
7. `docs/CLAUDE_RESEARCH_WORKFLOW.md`
8. `docs/REFERENCE_IMPLEMENTATIONS.md`
9. `research/RESEARCH_PROGRAM.md`

## Core autonomous loop

```text
repo state
→ context compiler
→ current-vs-north-star reconciliation
→ reference implementation mining
→ evidence-gap classifier
→ Claude Code web search OR Claude Research queue
→ returned research artifacts
→ structured synthesis
→ dynamic build DAG
→ isolated implementation/review sessions
→ tests/evals/gates
→ state + knowledge update
→ next wave
```

## Included reference implementations

The pack treats adjacent systems as evidence/pattern sources, never product templates:

- **Paperclip** — task/session control-plane, heartbeats, budgets, approvals, workspaces and operator patterns.
- **Super Simple Software Factory** — deterministic workflow rail, bounded agent/code phases, typed seam envelopes, gates, per-agent configuration and skill-as-installer pattern.
- **Inkwell / Factory in a Box** — isolated sandbox execution, privilege/credential boundaries, outside observability, best-of-N fan-out and non-destructive harvesting.

## Core principle

> Higher autonomy is earned through verified capability. Automate repeated human coordination only after the inputs, outputs, failure modes, authority boundaries and evaluation criteria are explicit.

## Repository placement

```text
agent-factory/
├── .agent-platform/
│   ├── bootstrap/              # this pack
│   ├── PROJECT_STATE.yaml
│   └── research/
│       ├── RESEARCH_QUEUE.md
│       ├── queue/
│       └── runs/
├── .claude/skills/
├── existing Agent Factory code...
└── ...
```

Do not restructure the production repository before repo-context and reconciliation stages run.
