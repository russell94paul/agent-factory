---
name: roadmap-rank-tracker
description: Track Agent Factory progress toward evidence-gated autonomy ranks and emit operator-facing roadmap state without rewarding activity for its own sake.
---

# Roadmap Rank Tracker

## Use when

- planning or finishing a development wave;
- updating Mission Control progress;
- deciding whether the platform has earned a new autonomy capability;
- summarizing progress for the operator.

## Inputs

- `ROADMAP_TO_VISION.md`;
- `.agent-platform/PROJECT_STATE.yaml`;
- evaluation results;
- production mission evidence;
- current roadmap/tasks;
- relevant ADRs.

## Procedure

1. Recover the current rank and all rank exit criteria.
2. Gather evidence for each criterion. Do not infer implementation completion from prose or TODO status.
3. Assign each rank one state: `LOCKED | EXPERIMENTAL | PROVISIONAL | EARNED`.
4. Identify the smallest missing evidence needed for the next promotion.
5. Generate/update `.agent-platform/PROGRESS.yaml`.
6. Emit a concise operator summary:
   - current rank;
   - capabilities earned;
   - next unlock;
   - blockers;
   - measurable distance to unlock;
   - active experiments contributing evidence.
7. Never award progress for raw token usage, agent count, messages, branches or code volume.

## Promotion rule

A capability is earned by verified operational evidence, not because implementation exists or a model says it works.
