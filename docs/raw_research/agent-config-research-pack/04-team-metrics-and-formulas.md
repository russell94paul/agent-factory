# Agent-team metrics and formulas

## Measurement rules

1. Every metric states subject, window, unit, basis, source, evaluator version and confidence.
2. Activity metrics are paired with outcome metrics, matching `factory/metrics.py`.
3. Missing instruments report `UNMEASURABLE`, not zero or healthy.
4. Composite scores always expose components and hard caps.
5. Leaderboards do not grant permissions or certifications.
6. Scores are segmented by task family, risk, environment and configuration version.

## Team metric families

| Family | Metrics |
| --- | --- |
| Outcome | terminal contract pass rate, accepted outcomes, target evidence satisfaction, user acceptance |
| Quality | regression escape, reviewer rejection, rework, defect severity, evidence completeness |
| Flow | time-to-first-evidence, time-to-green, blocked time, queue time, handoff delay, WIP |
| Efficiency | cost per accepted outcome, tokens per accepted outcome, tool calls per accepted outcome |
| Coordination | handoff correctness, duplicate work, collision rate, dependency wait, credit concentration |
| Communication | delivery, consumption, actionability, timeliness, information gain, noise, contradiction repair |
| Resilience | recovery rate, mean time to recovery, checkpoint coverage, resume success, rollback readiness |
| Knowledge | required-knowledge coverage, retrieval precision, freshness, provenance, promoted-learning reuse |
| Safety | policy violations, attempted boundary crossings, grader isolation, secret exposure, rollback presence |
| Economics | budget variance, capacity utilization, marginal value, portfolio contribution, support cost |
| Human experience | approval burden, intervention count, trust rating, explanation usefulness, client satisfaction |
| Adaptation | challenger uplift, calibration error, learning transfer, recertification success, configuration drift |

## Agent health

Health describes current operational readiness, not reputation.

Let normalized component scores be:

- (R): runtime/tool reliability
- (C): context integrity
- (P): progress against expected progress
- (V): verification readiness
- (B): budget/time runway
- (K): mission-knowledge coverage
- (L): coordination freshness

Use a weighted geometric mean so a serious weakness cannot be hidden by strong unrelated values:

\[
H = 100R^{0.20}C^{0.20}P^{0.20}V^{0.15}B^{0.10}K^{0.10}L^{0.05}
\]

Hard caps:

- required verification failing: `H ≤ 55`;
- unsafe context exhaustion: `H ≤ 40`;
- essential tool unavailable: `H ≤ 25`;
- required authorization or credential unavailable: `H ≤ 15`;
- instrument failure: overall health is `ERROR` or `UNMEASURABLE`, never a guessed score.

## Team health

Do not average member health. A single critical seat can block the mission.

\[
H_{team} = 100 \times
(H_{critical\ path})^{0.35}
(H_{coordination})^{0.20}
(H_{coverage})^{0.15}
(H_{verification})^{0.15}
(H_{runway})^{0.10}
(H_{resilience})^{0.05}
\]

Each input is normalized to `[0,1]`. `H_critical path` is the geometric mean of active critical-path
seats, not the whole roster.

## Struggle score

\[
S = 100 \times EWMA(
0.25A + 0.20F + 0.15T + 0.15U + 0.10D + 0.10B + 0.05X)
\]

- (A): progress stall
- (F): repeated failures/retries
- (T): context/tool thrashing
- (U): uncertainty/disagreement
- (D): unresolved dependencies
- (B): abnormal token/cost burn
- (X): contradictions with evidence or prior decisions

Suggested thresholds: 40 observe, 55 structured self-diagnosis, 70 bonded helper, 85 pause risky
actions and escalate. Use hysteresis and cooldowns.

## Communication effectiveness

Track messages only when a message has a typed purpose and expected effect.

Let:

- (D): delivery/acknowledgment reliability
- (C): correct consumption of the content
- (A): actionability—the recipient could take the intended action
- (I): information gain or reduction in uncertainty
- (T): timeliness relative to the decision window
- (R): contradiction-resolution effectiveness
- (N): noise/redundancy rate

\[
CE = 100(0.15D + 0.25C + 0.20A + 0.15I + 0.10T + 0.10R + 0.05(1-N))
\]

The most important component is correct consumption: a delivered handoff that is misunderstood is
not effective communication.

Pair communication activities with outcomes:

| Activity | Required outcome anchor |
| --- | --- |
| Messages sent | Correctly consumed messages |
| Wiki scans | Decisions corrected or gaps closed |
| Alerts generated | Valid actionable alerts |
| Handoffs created | Accepted and correctly consumed handoffs |
| Meetings/syncs | Blockers resolved or decisions made |
| Knowledge uploads | Reused, verified knowledge objects |

## Feature output

`number_of_features` is an activity metric and is unsafe alone.

Use:

\[
Feature\ Yield = \frac{accepted\ features\ retaining\ target\ evidence\ after\ window}
{features\ attempted}
\]

Pair with:

- accepted features;
- escaped defects per feature;
- user adoption/value signal;
- cost per retained feature;
- median time to green;
- rework rate.

## Mission knowledge

For required knowledge items (r), each with importance (w_r):

\[
K = 100\frac{\sum_r w_r c_r f_r p_r}{\sum_r w_r}
\]

Where (c) is confidence, (f) freshness and (p) provenance quality. A missing critical
requirement cannot be compensated by knowing many irrelevant facts.

## Mission matching

First apply hard constraints: permissions, domain minimums, required tools, repository scope,
availability, risk/certification and prohibitions. Then rank eligible candidates:

\[
Match = 100(
0.25Capability +
0.15TaskSimilarity +
0.15Knowledge +
0.10Reliability +
0.10CostFit +
0.10LatencyFit +
0.10Complementarity +
0.05CommunicationFit)
\]

Return score, confidence, evidence count, missing requirements and rejection reasons. Do not hide
the uncertainty behind one percentage.

## Pre-deployment Readiness Uplift Planner

### Inputs

- time until deployment;
- mission requirement graph and risk;
- current agent/team health components;
- capability evidence and expiry;
- known failure modes;
- available skills, knowledge packets, tools, models, substitutes and reserves;
- micro-eval durations/costs;
- hard permissions and operator gates.

### Candidate actions

- refresh a mission-critical knowledge packet;
- run a tool/credential/symbol-resolution probe;
- perform context compaction and checkpoint;
- attach a specialist skill or replace an expired version;
- run a short task-specific micro-eval;
- substitute an agent/model with stronger evidence;
- add a reviewer or bonded helper;
- reduce mission scope;
- delay deployment when no safe uplift exists.

### Selection formula

For intervention (i):

\[
Priority_i =
\frac{ExpectedRiskReduction_i \times Confidence_i \times Criticality_i}
{Time_i + \lambda Cost_i + \mu CoordinationOverhead_i}
\]

Choose the best feasible set under remaining time, budget and policy constraints. This is a bounded
knapsack/portfolio problem, not a command to “increase all scores.”

Record:

```text
health_before
action_applied
expected_uplift + confidence
measurement_performed
health_after
remaining_gap
decision: deploy | narrow | substitute | delay | refuse
```

Health changes only from the post-action measurement. Expected uplift is stored separately.

## Surplus capacity optimization

Do not maximize tokens used. Maximize expected retained value:

\[
QueueScore =
\frac{P(success) \times ExpectedValue \times Reusability \times Reversibility}
{ExpectedTokens + CostPenalty + RiskPenalty}
\]

Eligibility requirements:

- bounded and reversible;
- no production mutation;
- no grader/eval-corpus changes;
- clear verifier;
- checkpointable before reset;
- positive value floor;
- stop if meaningful progress cannot complete in the remaining window.

## Leaderboards

Use separate boards for terminal success, cost efficiency, handoff quality, rescue effectiveness,
research usefulness, knowledge reuse and reliability. Require minimum samples and show confidence
intervals. Titles/certifications use evaluation rules, not raw leaderboard position.

