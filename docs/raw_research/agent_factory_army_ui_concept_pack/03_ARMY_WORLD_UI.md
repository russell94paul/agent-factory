# Battlefield View — Army World UI

## Thesis

The Battlefield View should use military command concepts as **information compression**:

- position = ownership / priority
- movement = workflow
- formation = execution topology
- front line = urgency
- supply = context/tools/access/compute
- radio = communication
- fog = uncertainty
- threat markers = risk/failure
- after-action = retrospective / learning
- commander's intent = success criterion

## 10 foundational world concepts

### 1. Global Operations Map
Projects/campaigns, operations, squads, objectives and threats are spatially organized.

**Replaces:** project selector, portfolio page, status dashboard.

### 2. Commander's Intent
A frozen objective/constraint surface remains visible throughout execution.

**Replaces:** disconnected OKR/strategy pages.

### 3. Front Line
Urgent, high-leverage or blocking operations occupy the visible frontline.

**Replaces:** priority sorting / P0–P3 scanning.

### 4. Unit Formations
Spatial arrangements compile to workflow/team topology.

**Replaces:** some DAG / team-config editing.

### 5. Fog of War
Unknown, unsupported or low-confidence mission regions are literally obscured.

**Replaces:** hidden uncertainty metadata.

### 6. Supply Lines
Context, credentials, tools, compute and upstream dependencies are logistics.

**Replaces:** many dependency/context/preflight pages.

### 7. Signals Network
Communication paths and channels are visible at team/mission/company levels.

**Replaces:** transcript/event-feed scanning for many coordination tasks.

### 8. Operations Tempo
Queues and bottlenecks become motion/traffic/congestion.

**Replaces:** some latency and queue charts.

### 9. Tactical Zoom
Company → campaign → operation → task force → squad → agent → task/tool/file.

**Replaces:** repetitive sidebar drill-down.

### 10. Battle Rhythm
Scheduled and recurring activities become visible operational cycles.

**Replaces:** some scheduler/calendar/cron monitoring.

## 10 direct-action features

### Target Lock
Select any object and make all context panes follow it.

### Strike Command
Cursor-local command overlay inferred from target context.

### Deploy Reinforcements
Drag a team/specialist to a problem; generate handoff and permissions automatically.

### Distress Signal
Route help using expertise, history, availability and authority.

### Intelligence Drop
Attach evidence or findings to a mission/team/agent/memory target.

### Hot Drop Specialist
Instantly deploy a context-prepared specialist.

### Fire Mission
Choose desired outcome (diagnose/fix/research/red-team/optimize); compiler builds the team/workflow.

### Surveillance Mode
Hide normal activity; show only incidents, blockers, abnormal cost, uncertainty, queues and approvals.

### After-Action Replay
Replay the operational battlefield and causal sequence.

### One-click AAR
Summarize result, cost, interventions, successful tactics, failures, reusable learning and doctrine candidates.

## Environmental storytelling mapped to real state

| Operational state | Battlefield representation |
|---|---|
| incident | base/operation under attack |
| agent blocked | unit pinned |
| missing context | intelligence supply severed |
| stale knowledge | outdated map / stale intelligence |
| queue | physical congestion |
| duplicate work | friendly units converging on same target |
| regression | counterattack / recaptured objective |
| deploy | insertion / convoy / launch |
| research | recon patrol |
| uncertainty | fog |
| approval | command authorization |
| cost spike | supply burn warning |
| loop | unit circling / stuck patrol |
| successful outcome | objective captured |
| rollback | tactical withdrawal |
