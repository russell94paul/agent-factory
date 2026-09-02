# Agent Team Configuration + Health Ontology

## Team configuration fields

### Identity / lifecycle
- Team ID
- Name
- Version
- Preset
- Team Type
- Mission Class
- Lifecycle
- Temporal Horizon
- Autonomy Level

### Purpose
- North Star
- Objectives
- Success Definition
- Mission Applicable Specialities
- Required Skills
- Preferred Skills
- Domain

### Operating environment
- Repositories
- Technologies
- Environments
- Tools
- Data domains
- External systems

### Organization
- Architecture
- Topology
- Workflow
- Working Style
- Hierarchy
- Manager
- Delegation Model
- Decision Model
- Escalation Model
- Human gate model

### Communication
- Communication Mode
- Communication Frequency
- Sharing Frequency
- Alerting Frequency
- Acknowledgement requirements
- Shared Context Strategy
- Handoff Protocol
- Synchronization Policy

### Output / performance
- Feature Output
- Task Throughput
- Accepted Output
- Rework Rate
- Defect Rate
- Time-to-Green
- Cost per Accepted Outcome
- Human Intervention Rate

### Team composition
- Capability Coverage
- Skill Redundancy
- Skill Complementarity
- Specialization Diversity
- Bus Factor / single-point-of-failure risk
- Workload Balance
- Parallelism Efficiency
- Coordination Overhead

### Team health
- Shared Mental Model
- Situation Awareness
- Knowledge Distribution
- Knowledge Freshness
- Tool Health
- Memory Health
- Security Health
- Budget Health
- Manager Load
- Dependency Coupling
- Bottleneck Score
- Outcome Reliability
- Handoff Integrity
- Synchronization
- Communication Efficiency

## Communication Effectiveness

Do not optimize for number of messages.

Candidate conceptual formula:

CE =
  w1 * relevance
+ w2 * actionability
+ w3 * timeliness
+ w4 * shared_state_convergence
+ w5 * useful_information_novelty
- w6 * noise
- w7 * delay

Possible observable measures:
- % messages consumed;
- % messages causing useful state updates;
- alerts leading to correct action;
- duplicate communication rate;
- missed dependency rate;
- handoff correction rate;
- information latency;
- contradiction rate;
- stale information rate;
- percentage of coordination messages that do not affect outcome.

## Shared knowledge principle

Do not aim for total knowledge duplication.

Target:
- shared mission understanding;
- shared awareness of critical state;
- differentiated specialist expertise;
- known "who knows what";
- reliable escalation/routing.

This may be more efficient than loading all context into every agent.

## Key experiments

1. Compare communication cadence vs performance.
2. Compare duplicated context vs specialized context.
3. Compare central manager vs peer coordination.
4. Compare one senior generalist vs specialist team.
5. Measure rework introduced by handoffs.
6. Estimate marginal value of each agent seat.
7. Detect when communication becomes coordination overhead.
