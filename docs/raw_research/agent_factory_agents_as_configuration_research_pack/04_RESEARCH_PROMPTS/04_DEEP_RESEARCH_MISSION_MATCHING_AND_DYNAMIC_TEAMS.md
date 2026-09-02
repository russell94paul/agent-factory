# Deep Research Prompt 04 — Mission Matching + Dynamic Team Formation

You are designing the mission routing and organization construction layer for Agent Factory.

## Core question

How should Agent Factory choose:

`mission -> agent(s) -> team composition -> topology -> workflow -> model/tool allocation`

to maximize outcome quality while controlling cost, risk and coordination overhead?

## Research relevant prior art

Investigate:

- multi-agent task allocation;
- coalition formation;
- matching theory;
- bipartite matching;
- assignment algorithms;
- workforce scheduling;
- competency matrices;
- skills-based routing;
- recommender systems;
- contextual bandits;
- mixture-of-experts routing;
- model routers;
- portfolio optimization;
- project team composition;
- team diversity research;
- transactive memory;
- shared mental models;
- organizational design;
- distributed systems scheduling;
- operations research.

## Mission representation

Propose a Mission Requirement Vector / Mission Contract containing:

- domain;
- required skills;
- preferred skills;
- minimum capability;
- risk;
- time;
- cost;
- security;
- permissions;
- tool needs;
- environment;
- autonomy limits;
- verification needs;
- lifecycle;
- temporal horizon;
- uncertainty;
- expected output;
- definition of green.

## Candidate representation

For each agent:
- capability vector;
- confidence;
- evidence freshness;
- learned performance by mission class;
- current health;
- availability;
- cost;
- latency;
- tool access;
- permissions;
- team affinity / compatibility;
- historical contribution.

## Team formation

Research how to optimize:
- skill coverage;
- complementarity;
- redundancy;
- communication overhead;
- manager load;
- handoff count;
- parallelism;
- cost;
- risk;
- diversity of hypotheses;
- failure isolation.

Explicitly model the fact that adding agents can reduce performance through coordination cost.

## Topology selection

Compare:
- single senior agent;
- manager-worker hierarchy;
- parallel specialists;
- debate;
- critic/reviewer;
- sequential pipeline;
- swarm;
- committee;
- incident command;
- factory line;
- persistent guild + temporary squad.

Determine which mission features predict topology choice.

## Matching model maturity ladder

Design a path from:

### v0
Rules / manually weighted scoring.

### v1
Empirical performance tables by mission class.

### v2
Calibrated success predictors.

### v3
Contextual bandit / adaptive router.

### v4
Multi-objective organization optimizer.

### v5
Simulation + offline counterfactual evaluation before deployment.

## Credit assignment

Research how Agent Factory can estimate:
- marginal contribution of each agent;
- whether a specialist was actually needed;
- whether communication improved the outcome;
- whether manager coordination justified its cost;
- whether a cheaper topology would have succeeded.

## Output

Produce:

1. Mission contract specification
2. Agent candidate profile
3. Team compatibility/profile model
4. Matching algorithm comparison
5. Team formation objective function
6. Coordination-cost model
7. Topology selection strategy
8. Dynamic reconfiguration strategy
9. Credit-assignment approach
10. Cold-start strategy
11. Exploration vs exploitation policy
12. Simulation/offline-eval design
13. UI/UX for recommendations
14. MVP algorithm
15. Long-term learning architecture
16. Experiment matrix
