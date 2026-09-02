# 05 — Evaluation Protocol

## Why this is mandatory

A world UI can feel impressive while being slower. The product claim should therefore be falsifiable:

> ZEUS World earns a primary workflow only when it matches or beats the conventional baseline on measurable operator outcomes, or creates a capability that the baseline does not provide.

## Core metrics

### Efficiency
- time to locate relevant mission/agent/problem;
- time to correct action;
- clicks / pointer actions;
- keystrokes;
- number of page/context switches;
- time spent waiting for view loads/navigation.

### Correctness
- correct target selected;
- correct action chosen;
- missed blocker/anomaly rate;
- unsafe or unintended action rate;
- configuration error rate.

### Situation awareness
After a short exposure, ask:
- What is most urgent?
- What is blocked?
- Why?
- Which team owns it?
- What is waiting on you?
- Which operations are likely to collide?
- Where is uncertainty highest?

### Cognitive load
Use a lightweight workload survey plus behavioral proxies:
- backtracking;
- repeated opens/closes;
- hover hunting;
- search usage;
- accidental commands.

### Agentic quality
- unnecessary agent spawns;
- duplicate work;
- human interventions;
- blocked minutes;
- handoff loss;
- cost per accepted outcome.

## Baseline task suite

### T1 — Find the critical blocker
Given 25 active missions, identify the one requiring immediate intervention and explain why.

**Baseline:** table/status dashboard.
**ZEUS:** satellite/anomaly view.

### T2 — Reinforce a blocked mission
Find the best specialist and provide necessary context.

**Baseline:** agent directory + Slack + mission page.
**ZEUS:** distress request + reinforcement router.

### T3 — Diagnose missing prerequisite
Determine whether a failing agent lacks context, credentials, tool access, environment readiness, or upstream data.

**Baseline:** multiple diagnostic panels.
**ZEUS:** logistics map + exact drill-down.

### T4 — Identify team collision
Two teams are independently changing an overlapping area.

### T5 — Configure a parallel team
Build a team with two scouts, two independent implementers and one reviewer.

**Compare:** form/YAML vs node editor vs formation compiler.

### T6 — Find highest uncertainty
Locate the most consequential unsupported assumption.

### T7 — Review approval request
Make a production/release decision from evidence, risk, diff and rollback.

### T8 — Understand a failed mission
Identify the first consequential divergence point.

**Compare:** logs/chat/Git vs temporal replay.

### T9 — Find a reusable learning
Determine whether a previous mission contains a relevant fix or pattern.

### T10 — Reprioritize portfolio
Given new customer/reliability evidence, determine which mission should move to the front.

### T11 — Explain organizational health
In 30 seconds, summarize what is running, blocked, waiting, risky and over budget.

### T12 — Switch from strategic to exact evidence
Move from company view to the exact code diff/log/evidence item without losing mission context.

## Target thresholds for a concept to graduate

A candidate should generally achieve at least one of:

- >=25% faster median task completion;
- >=40% fewer navigation/context-switch actions;
- materially lower missed-state/error rate;
- materially better situation-awareness score;
- unique capability not available in baseline with acceptable workload.

And it must not cause:

- worse consequential decision accuracy;
- hidden provenance;
- unclear action scope;
- increased unsafe actions;
- major accessibility regression.

## Prototype ladder

1. **Paper/Figma storyboard** — test comprehension only.
2. **Clickable 2D mock** — test navigation/commands with fake data.
3. **Replay prototype** — feed historical mission event traces; no live actions.
4. **Shadow mode** — connected to live state but commands do not execute.
5. **Sandbox command mode** — actions execute only in isolated missions.
6. **Bounded production mode** — only after measured advantage and policy gates.
