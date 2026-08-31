# Roadmap to the Agentic Organization Vision

## Purpose

This roadmap exists for two reasons:

1. keep the build grounded in measurable capability rather than architecture theatre;
2. make progress visible and motivating while the platform gradually takes over more of the coordination work currently performed by the operator.

The roadmap is deliberately **dual-track**:

- **Capability Track** — make Agent Factory more reliable, communicative, knowledgeable, adaptive, and self-maintaining.
- **Value Track** — use those capabilities to build useful software, validate markets, operate bounded products, and learn from real customers.

The commercial track should begin early. It does **not** wait for the final Artificial Organization Platform to exist.

---

## North-star statement

Build a system where a person can express intent and the platform can increasingly:

```text
understand the mission
→ research unknowns
→ recover relevant organizational memory
→ assemble the right agents/skills/tools
→ create mission-specific communication and context routes
→ execute work in parallel where safe
→ evaluate real outcomes
→ learn from success and failure
→ improve its reusable capabilities
→ propose the next useful mission
```

For software ventures, this can extend into:

```text
market signal
→ opportunity hypothesis
→ validation
→ product plan
→ software build
→ launch experiment
→ customer evidence
→ improve / hold / kill / scale
```

The credible goal is **progressively lower-human software operations**, not unrestricted zero-accountability companies.

---

# Rank Progression

## Rank 0 — Manual Command

**State:** human launches prompts/sessions and manually reconciles outputs.

**Unlock condition:** baseline Agent Factory is mapped and measured.

**UI:** repository + current run dashboard.

---

## Rank 1 — Automated Research & Project Memory

**Capabilities:**

- durable `PROJECT_STATE`;
- repo-context compiler;
- Claude Research job compiler + queue + return inbox;
- versioned research manifests;
- automatic research synthesis;
- human-question queue.

**Unlock test:** a fresh Claude session can recover context, compile only the necessary Claude Research jobs, ingest returned reports, synthesize them, and update project state without API billing or manual reconciliation.

**Operator experience:** the human is reduced to triggering prepared Claude Research runs and returning the raw report; prompt design, formatting, synthesis, reconciliation and state updates are automated.

---

## Rank 2 — Hardened Software Factory

**Capabilities:**

- positive GREEN contracts;
- deterministic policy/gates;
- versioned team/config locks;
- reproducible run evidence;
- evaluation harness;
- recovery and rollback.

**Unlock test:** a real task goes RED → GREEN, regression checks remain green, and the exact configuration can be replayed.

**Commercial use:** begin using the Factory for real bounded software delivery and internal product experiments.

---

## Rank 3 — Operations Platform / Build Command

**Capabilities:**

- parallel session/task monitoring;
- dependency graph;
- research jobs;
- artifacts and diffs;
- approvals/blockers;
- Synthesis Inbox;
- cost/outcome view;
- roadmap/rank tracker.

**Unlock test:** several independent workstreams can be managed from one surface without manual terminal bookkeeping.

**Operator experience:** this is the first serious **project-management operating platform** for building the larger system.

---

## Rank 4 — Communication Mesh

**Capabilities:**

- typed agent messages/events;
- capability and availability announcements;
- request-help / offer-help;
- evidence / claim / warning / handoff;
- subscriptions and priority routing;
- anti-loop and deduplication rules;
- observable communication traces.

**Unlock test:** a real mission demonstrates useful cross-agent coordination with measured communication cost and measurable benefit over the baseline.

**Why this rank matters:** communication turns parallel agents into a coordinated organization rather than a collection of independent workers.

---

## Rank 5 — Collective Cognition

**Capabilities:**

- provenance-aware knowledge;
- historical mission retrieval;
- experience summaries;
- expert discovery;
- contradiction/freshness handling;
- role-specific context packets;
- mission-shaped knowledge/context graphs.

**Unlock test:** context compiled from relevant mission history improves quality, cost, speed, or error rate against a frozen baseline.

**Operator experience:** agents begin learning from one another across missions rather than only within a single run.

---

## Rank 6 — Dynamic Mission Assembly

**Capabilities:**

- evidence-backed capability records;
- workload/availability state;
- reusable team blueprints;
- dynamic specialist consultation;
- bounded swarm formation;
- model/tool/runtime selection;
- communication and knowledge routes emitted with the mission plan.

**Unlock test:** different mission classes automatically receive different proven configurations and meet or beat fixed baselines.

---

## Rank 7 — Venture Loop

**Capabilities:**

- Opportunity Intelligence Council;
- monetization/market research waves;
- Venture Compiler;
- customer/market learning fabric;
- launch/economics GREEN contracts;
- product-operation teams.

**Unlock test:** the platform takes one opportunity from research through a bounded MVP/market experiment and produces externally measured evidence without requiring the operator to manually coordinate each phase.

**Commercial target:** low-human subscription software, internal tools, data products, workflow automation, niche B2B utilities, and agent-delivered managed services.

---

## Rank 8 — Portfolio & Capability Economy

**Capabilities:**

- multiple bounded venture experiments;
- budget allocation;
- kill/continue/scale gates;
- best-of-N builds;
- certified agent/team registry;
- reusable capability packages;
- internal or external team/skill marketplace experiments.

**Unlock test:** resource allocation measurably outperforms building opportunities sequentially or by intuition alone.

---

## Rank 9 — Organizational Debugging & Evolution

**Capabilities:**

- causal replay;
- seam attribution;
- candidate generation;
- frozen external evaluation;
- prompt/skill/model/context/topology optimization;
- canary promotion and rollback;
- progressive determinization.

**Unlock test:** one bounded organizational artifact improves under out-of-sample evaluation without changing its own promotion test.

---

## Rank 10 — Self-Maintaining Platform

**Capabilities:**

- platform health/drift monitoring;
- maintenance-intent creation;
- repair organizations;
- safe validation/canary/rollback;
- automatic knowledge writeback.

**Unlock test:** seeded faults in the platform are detected, repaired, verified, and safely promoted through the same governed lifecycle.

---

## Rank 11 — Higher-Order / Federated Artificial Organizations

**Capabilities:**

- multiple organizations and ventures;
- permissioned cross-organization knowledge exchange;
- strategic research and doctrine;
- temporal organizations;
- shared compute/capability allocation;
- federation where it demonstrably beats simpler composition.

**Unlock test:** federation creates measurable value that cannot be achieved more simply.

---

# Five parallel tracks

The ranks are not a single waterfall. Work should proceed in parallel where dependencies allow.

| Track | Near-term objective | North-star contribution |
|---|---|---|
| Reliability & Evaluation | prove GREEN/replay/versioning | trustworthy autonomy |
| Communication & Cognition | ACIP + shared knowledge | collective intelligence |
| Operator Experience | Build Command + roadmap UI | lower coordination burden |
| Commercial / Venture | opportunity → product → evidence | revenue and external feedback |
| Evolution & Maintenance | experiments + repair loops | self-improvement/self-maintenance |

---

# Progress scorecard

Mission Control should show progress toward each rank using **evidence-backed readiness**, not percent-complete guesses.

Suggested dimensions:

```text
Capability implemented        yes/no
Evaluation coverage           measured
Production evidence           count / quality
Reliability                   success rate
Human coordination required   interventions per mission
Cost efficiency               cost per verified outcome
Recovery maturity             replay / retry / rollback coverage
Knowledge reuse               successful reuse rate
Commercial evidence           problem → revenue ladder
```

A rank is `LOCKED`, `EXPERIMENTAL`, `PROVISIONAL`, or `EARNED`.

Do not award rank/XP for token volume, agent count, messages sent, or code churn.

---

# The motivating story

> The first recruit is the operator. Every rank the platform earns removes another repetitive command burden. The Factory first learns to execute, then communicate, then remember, then assemble, then experiment, then maintain itself. Revenue is not a final boss waiting at the end: real products become live missions that teach the organization what the market actually rewards.
