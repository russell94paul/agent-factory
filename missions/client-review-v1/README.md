# Agent Factory — Client Review v1 Mission Pack

## Purpose

This pack is a focused implementation bundle for delivering a production-quality **Client Review & Acceptance** component inside Agent Factory.

It is intentionally scoped for rapid delivery. It does **not** require re-processing the entire Agent Factory / Agent Army research corpus before implementation.

## Recommended placement

Copy this folder into the Agent Factory repository as:

```text
missions/client-review-v1/
```

Result:

```text
agent-factory/
└── missions/
    └── client-review-v1/
        ├── README.md
        ├── 00-MISSION.md
        ├── 01-PRODUCT-REQUIREMENTS.md
        ├── 02-CLIENT-REVIEW-SPEC.md
        ├── 03-DATA-CONTRACT.md
        ├── 04-DEFINITION-OF-DONE.md
        ├── 05-CLIENT-REVIEW-DEMO-RUNBOOK.md
        └── MASTER-PROMPT.md
```

## How to use

1. Copy this folder into the Agent Factory repo.
2. Open a fresh Claude Code / coding-agent session at the repository root.
3. Paste the contents of `MASTER-PROMPT.md`.
4. Let the agent inspect the existing repo before making broad changes.
5. Keep the mission focused on a reliable Client Review vertical slice.

## Immediate objective

Produce a client-facing review experience that clearly communicates:

1. What the client asked for.
2. What has been delivered.
3. Evidence that it works.
4. Decisions required from the client.
5. Risks/blockers.
6. What happens next.
7. Review / acceptance state.

## Research rule

Do not re-synthesize all historical research as a prerequisite.

Use targeted reconciliation only:

```text
Client Review use-case
        ↓
current repository + current architecture
        ↓
relevant recent research/docs only
        ↓
reuse existing primitives
        ↓
working vertical slice
```

A broader Agent Factory / Agent Army research delta reconciliation can happen after this delivery milestone.
