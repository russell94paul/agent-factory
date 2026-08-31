# Gamified Mission Control — Product Direction

## Goal

Create an operations interface that makes a large agent/software program understandable, motivating, and fun to operate without turning real engineering state into decorative game mechanics.

The initial UI is a **Build Command** surface for constructing Agent Factory itself. As autonomy increases, the same information model can evolve into a radically different Mission Control interface.

The visual direction may borrow the *feel* of an open-world operations game, military command room, strategy game, and life-simulation dashboard, but should use **original characters, original iconography, and an original visual language** rather than copying GTA, The Sims, or another game's protected characters/trade dress.

---

## Core UI metaphor

Treat the platform as a living base of operations:

```text
HEADQUARTERS
├── Mission Board
├── Operations Room
├── Research & Intelligence
├── Knowledge Archive
├── Engineering Bay
├── Evaluation Range
├── Reliability Corps
├── Venture Studio
├── Compute / Deployment Bay
└── Capability Barracks / Registry
```

The metaphor must map to real system objects. Every visual element should have an operational purpose.

---

## Early build-era UI

The first interface should optimize the operator's actual problem while the platform is being built.

### Main surfaces

**1. Command Map**

- current roadmap/ranks;
- active missions;
- dependency routes;
- blocked fronts;
- upcoming unlock criteria.

**2. Live Operations**

- Claude/agent sessions;
- research jobs;
- deterministic workflow stages;
- worktree/branch;
- status, cost and duration;
- current artifact;
- intervention controls.

**3. Crew / Agent Roster**

Represent each agent/team using an original stylized character/card with:

- role;
- current mission;
- capability certifications;
- experience history;
- model/runtime;
- availability;
- cost profile;
- reliability;
- current context load;
- relationships/handoffs.

**4. Communications Overlay**

Visualize typed communication rather than raw chat spam:

- help request;
- evidence published;
- warning;
- handoff;
- expert consulted;
- claim challenged;
- mission state changed.

A user should be able to turn on the communication graph for one mission and see why information moved between agents.

**5. Synthesis Inbox**

Research reports, reviews, agent outputs and artifacts awaiting reconciliation.

**6. Promotion Board**

Shows roadmap ranks and why each is locked/experimental/provisional/earned.

---

## Gamification that reflects reality

Useful game-like mechanics:

- **Ranks** — unlocked only through predefined evidence;
- **missions** — actual tasks/operations;
- **campaigns** — multi-mission programs or ventures;
- **specializations** — evidence-backed capability families;
- **decorations/badges** — certified outcomes, not participation trophies;
- **base upgrades** — actual platform capabilities becoming available;
- **intel** — market/research/knowledge evidence;
- **readiness** — capability/evaluation/health state;
- **alert level** — real blockers/incidents;
- **supply/logistics** — model budgets, compute, context and tool availability.

Avoid reward mechanics that encourage unnecessary agent activity, message volume, spend or risky autonomy.

---

## UI evolution as autonomy rises

### Era A — Construction Console

Human is a hands-on project commander.

Primary objects: sessions, tasks, branches, prompts, research jobs, artifacts.

### Era B — Mission Command

Human specifies goals and resolves exceptional gates.

Primary objects: missions, organizations, capabilities, evidence, blockers, simulations.

### Era C — Venture / Portfolio Command

Human allocates objectives/resources and evaluates strategic choices.

Primary objects: ventures, market evidence, experiments, unit economics, capability assets, risk.

### Era D — Artificial Organization Observatory

Most routine orchestration is automated.

Primary objects: outcomes, organization health, emerging opportunities, anomalies, policy, strategic alternatives.

The UI should be allowed to evolve rather than preserving a terminal/session-centric metaphor forever.

---

## Example main screen

```text
┌────────────────────────── AGENT ARMY // OPERATIONS ──────────────────────────┐
│ Rank 4: COMMUNICATION MESH     Next promotion: 2/3 evidence gates      │
├───────────────┬─────────────────────────────────┬───────────────────────┤
│ CAMPAIGNS     │ LIVE THEATER                    │ INTELLIGENCE          │
│               │                                 │                       │
│ Agent Factory │  ● ACIP mission     RUNNING     │ 3 research jobs      │
│ Venture 001   │  ● Context KG       REVIEW      │ 7 new claims         │
│ R&D           │  ● Eval harness     GREEN       │ 2 contradictions     │
│ Reliability   │  ▲ Session UI       BLOCKED     │                       │
│               │                                 │ [Synthesis Inbox]     │
├───────────────┼─────────────────────────────────┼───────────────────────┤
│ CREW          │ COMMUNICATION GRAPH             │ COMMAND               │
│ Architect  ★4 │ builder ─evidence→ reviewer     │ [Launch Mission]      │
│ Builder    ★5 │ researcher ─help→ domain expert │ [Approve]             │
│ Reviewer   ★5 │ context service → all workers   │ [Intervene]           │
│ Scout      ★3 │                                 │ [Replay]              │
├───────────────┴─────────────────────────────────┴───────────────────────┤
│ Verified outcomes 42 │ Human interventions 0.7/mission │ Cost/green $X  │
└────────────────────────────────────────────────────────────────────────┘
```

---

## Research questions

- Does spatial/game-like representation improve operator comprehension under many concurrent sessions?
- Which objects should be characters vs graphs vs queues vs tables?
- How can communication events be compressed without hiding causal detail?
- What game mechanics motivate progress without creating Goodhart incentives?
- At what autonomy level should session/process detail disappear from the primary UI?
- How should mobile intervention differ from desktop operations?
