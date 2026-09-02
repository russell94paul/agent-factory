# Deep Research Prompt 02 — Agent Health + Mission Readiness

You are researching a health/readiness architecture for Agent Factory.

## Core hypothesis

An AI agent should not have one generic "health score."

Separate:

- capability;
- health;
- availability;
- mission readiness;
- deployability;
- fitness/outcome.

Research whether this separation is theoretically and operationally sound.

## Cross-domain prior art

Deeply investigate transferable mechanisms from:

- SRE/service health;
- Kubernetes startup/liveness/readiness probes;
- aviation preflight;
- aircraft mission readiness;
- military readiness models;
- crew resource management;
- medicine/surgical checklists;
- manufacturing readiness;
- robotics;
- distributed systems;
- cognitive-load research;
- human factors;
- team readiness;
- sports readiness;
- reliability engineering;
- fault diagnosis;
- predictive maintenance.

Do not use metaphors superficially. Extract computable mechanisms.

## Agent Health Vector

Develop a candidate ontology for:

- reasoning health;
- instruction adherence;
- calibration;
- hallucination/error propensity;
- context health;
- context freshness;
- context saturation;
- memory health;
- retrieval quality;
- knowledge freshness;
- tool health;
- integration health;
- dependency health;
- model health;
- communication health;
- workload health;
- budget/resource health;
- security health;
- recent evaluation health.

For each metric define:
- unit/range;
- measurement source;
- sampling frequency;
- whether it is causal or proxy;
- likely failure modes;
- gaming risk;
- acceptable confidence.

## Team Health Vector

Research metrics for:

- capability coverage;
- skill complementarity;
- redundancy;
- specialization diversity;
- shared mental model;
- shared situation awareness;
- knowledge distribution;
- "who knows what";
- communication efficiency;
- handoff integrity;
- synchronization;
- coordination overhead;
- manager load;
- bottleneck risk;
- workload balance;
- dependency coupling;
- parallelism efficiency;
- team reliability.

## Communication Effectiveness

Design a measurable formula that rewards:
- relevance;
- actionability;
- timeliness;
- shared-state convergence;
- useful novelty.

Penalize:
- noise;
- redundancy;
- latency;
- contradictions;
- unnecessary coordination.

Do not optimize message count.

## Mission Readiness

Design a model that maps:

Mission Requirement Vector
+
Agent/Team Capability
+
Current Health
+
Freshness/Confidence
+
Tool/Permission State
+
Time/Cost/Risk constraints

to:

- calibrated probability of mission success;
- readiness score;
- deployability decision;
- explanation of gaps.

Compare:
- deterministic weighted scoring;
- rules/gates;
- Bayesian methods;
- reliability models;
- learned classifiers/regressors;
- survival/time-to-failure methods;
- calibrated success probability.

Recommend an MVP and a future learned version.

## READY-UP / Mission Conditioning

Design a pre-deployment optimizer that can choose interventions such as:

- load skill capsule;
- retrieve similar missions;
- retrieve recent incidents;
- refresh repo topology;
- refresh docs;
- verify tools/credentials;
- increase reasoning/verification;
- change model;
- add specialist;
- add reviewer;
- alter topology;
- alter communication cadence;
- reduce autonomy;
- run targeted micro-eval.

The optimizer should maximize expected mission success/readiness under:
- time;
- cost;
- risk;
- security;
- authority.

Research suitable optimization approaches:
- knapsack;
- constrained optimization;
- bandits;
- value-of-information;
- Bayesian decision theory;
- scheduling.

## Output

Produce:

1. Health/readiness conceptual model
2. Agent Health Vector
3. Team Health Vector
4. Communication Effectiveness model
5. Mission Readiness formula/model
6. Confidence/calibration strategy
7. READY-UP optimizer design
8. Readiness gates
9. Telemetry/data requirements
10. UI design implications
11. Anti-Goodhart controls
12. Experiments and benchmarks
13. MVP implementation plan
14. Future learned-model roadmap
15. Clear list of unknowns and speculative elements
