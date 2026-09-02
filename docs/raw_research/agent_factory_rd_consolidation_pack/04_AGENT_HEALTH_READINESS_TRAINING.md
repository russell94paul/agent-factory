# Agent Health, Mission Readiness and Dynamic Training

## Health is not one universal score

An Agent can be generally healthy but poorly prepared for a specific mission.

Separate:

- baseline health
- mission readiness
- capability freshness
- knowledge freshness
- context integrity
- resource headroom
- evaluation/certification status

Conceptual baseline:

```text
H_a = f(reliability, tools, knowledge freshness, context integrity, budget, eval status)
```

Mission readiness:

```text
MR(agent, mission)
 = Health
 * SkillFit
 * KnowledgeFit
 * ToolFit
 * Trust
```

Hard blockers should be applied separately rather than hidden inside a blended score.

## Pre-Deployment Skill-Up

Never directly increment the score.

Run interventions, then remeasure.

Possible interventions:

- load mission-specific knowledge
- retrieve prior similar missions
- refresh repo context
- update tool/API docs
- run warm-up capability checks
- resolve stale memory
- remove contradictory context
- allocate more runtime/model budget
- switch model
- add specialist Agent
- adjust communication frequency
- increase verification depth
- reduce concurrent workload

Flow:

```text
Mission Brief
 -> requirements vector
 -> compare to Agent Genome + observed state
 -> readiness gaps
 -> recommended interventions
 -> skill-up
 -> reevaluate
 -> DEPLOY / SUBSTITUTE / ESCALATE
```

## Experience is evidence

Declared profile:

- title
- role
- target specialization
- working style
- tools

Observed profile:

- mission count
- pass rate
- time to green
- cost per success
- rework
- failure modes
- domain performance
- learning velocity
- team-history KPIs

## Curriculum Optimizer

Inputs:

- current capabilities
- recent failures
- historical weakness
- mission forecast
- upcoming tickets
- knowledge freshness
- team capability gaps
- available compute/time

Conceptual training priority:

```text
TrainingPriority(agent, skill)
 =
 SkillGap
 * UpcomingDemand
 * MissionImpact
 * FreshnessRisk
 / TrainingCost
```

Training activities:

- historical replay
- simulated bugs
- docs research
- held-out evals
- repo familiarization
- pairing with specialist
- tool drills
- failure analysis
- shadow missions
- research assignments

Training changes create candidate Agent versions and require recertification.
