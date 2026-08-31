# Autonomy Ladder

| Rank | Development behavior | Required proof before promotion |
|---|---|---|
| L0 Manual | Human runs prompts, copies outputs, coordinates sessions | baseline measured |
| L1 Skilled | Claude skills perform bounded missions with durable outputs | repeatable skill success + rollback |
| L2 Orchestrated | Commander compiles task DAG from known workflows | dependency/gate correctness |
| L3 Parallel | isolated workers execute independent branches | worktree/state isolation + synthesis correctness |
| L4 Evaluated | automated reviewers/tests judge against fixed contracts | false-GREEN rate acceptable |
| L5 Adaptive | team/skill/model/context selection uses historical evidence | frozen benchmark + OOS improvement |
| L6 Self-Maintaining | platform detects/proposes repairs to itself | seeded fault detection + gated repair/rollback |
| L7 Experimentally Self-Improving | candidates are generated and promoted under external evals | no evaluator mutation; OOS gain; hard constraints met |

## Recursive build story

```text
L0 builds L1
  ↓
L1 accelerates L2
  ↓
L2 builds L3 faster
  ↓
L3 parallelizes L4
  ↓
L4 makes L5 safe
  ↓
L5 improves organization selection
  ↓
L6 maintains the Factory
  ↓
L7 improves how the Factory builds
```

> **The first recruit is the operator. Each earned rank automates another repeated piece of command burden.**
