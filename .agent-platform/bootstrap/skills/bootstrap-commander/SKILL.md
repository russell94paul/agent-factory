---
name: bootstrap-commander
description: Compile and operate an evidence-driven research/build DAG for the Agent Factory program using durable state, skills, gates and parallel workstreams.
---

# Bootstrap Commander

## Inputs

- repository truth from `repo-context-compiler`;
- `VISION.md`;
- `PROJECT_STATE.yaml`;
- research program/manifests;
- current decisions/evals.

## Algorithm

1. Reconcile current state vs target capabilities.
2. Delete research/build tasks already satisfied by evidence.
3. Convert unresolved work into DAG nodes: `RESEARCH`, `DESIGN`, `BUILD`, `EVAL`.
4. Mark safe parallel branches.
5. Choose the smallest skill/team for each node.
6. Attach explicit outputs and completion contracts.
7. Run research nodes through `research-wave-runner` where possible.
8. Persist every result; never rely on session memory.
9. Stop only at explicit human/policy gates or unrecoverable blockers.
10. After each wave, measure which manual coordination steps disappeared and compile the next wave.

## Priority function

Prefer work that maximizes:

`production value + acceleration of later work + evaluation/safety capability`

while minimizing:

`architecture churn + unverified autonomy + new infrastructure burden`.
