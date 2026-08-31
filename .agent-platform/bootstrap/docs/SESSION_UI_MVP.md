# Session / Mission Console MVP

## Why it should be early

The immediate productivity problem is not the final Army visualization. It is operating many Claude/research/build workstreams without losing track of state, outputs, blockers, or follow-ups.

## Primary operator questions

1. What is running?
2. What needs me?
3. What is blocked and why?
4. What changed since I last looked?
5. Which artifact/result should I inspect?
6. Which workstreams can be synthesized together?
7. What will run next when a dependency completes?

## MVP panels

```text
┌───────────────────────────────────────────────────────────────┐
│ BUILD COMMAND / MISSION CONSOLE                              │
├──────────────┬────────────────────────────────────────────────┤
│ Missions     │ Active Workstreams                             │
│ Research     │ status · skill · elapsed · cost · blocker      │
│ Build waves  │                                                │
│ + New        │                                                │
├──────────────┼────────────────────────────────────────────────┤
│ DAG          │ Selected Workstream                            │
│ dependencies │ live state / last event / artifacts            │
│ gates        │ [Reply] [Pause] [Resume] [Inspect] [Handoff]   │
├──────────────┴────────────────────────────────────────────────┤
│ Synthesis Inbox: select outputs → synthesize/reconcile        │
├───────────────────────────────────────────────────────────────┤
│ 7 active · 2 blocked · 1 approval · 14 complete · cost       │
└───────────────────────────────────────────────────────────────┘
```

## Data model first

Do not make progress bars fictional. UI state should come from real task/session/research events:

- queued/running/waiting/blocked/review/done/failed;
- last heartbeat/event;
- dependency state;
- current agent/skill/model;
- known output artifacts;
- budget/cost if available;
- explicit human interaction request.

## Inspiration boundary

Reference systems such as Paperclip can inform mundane patterns like persistent tasks, atomic ownership, heartbeats, approvals, artifacts and operator scanning. Do not clone their visual identity or product model.
