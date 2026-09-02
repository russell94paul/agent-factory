# Optimization, Reverse Optimization and Meta-Optimization

## Core distinction

Performance targets are optimization objectives, not configurable evidence.

Example:

```yaml
optimization:
  objective:
    metric: mission_success_rate
    target: 0.98
    direction: maximize
```

The system may search until it finds candidates that approach the target.

The final success rate remains observed evidence from validation/held-out missions.

## Optimization scopes

- skill/tool
- Agent
- Agent Team
- Team Manager
- multi-team
- Army
- Command
- whole project organization

## Optimization surface

Each field should be one of:

- SEARCHABLE
- FROZEN
- POLICY-IMMUTABLE

Example:

```text
Model                         SEARCHABLE
Reasoning                     SEARCHABLE
Prompt                        SEARCHABLE
Tools                         SEARCHABLE
HyperMESH profile             SEARCHABLE
Communication                 FROZEN
Permissions                   POLICY-IMMUTABLE
Evaluator                     POLICY-IMMUTABLE
Mission success definition    POLICY-IMMUTABLE
```

## Mandatory post-run failure analysis

Every simulation should emit an Optimization Postmortem:

- what failed
- where it failed
- why it likely failed
- which config fields contributed
- which interactions may matter
- supporting trace evidence
- next experiments
- confidence

Use a Configuration Attribution Engine to reduce a very large config space to a smaller candidate optimization surface.

## Search techniques

Potential strategy library:

- ablation
- coordinate search
- factorial experiments
- Bayesian optimization
- evolutionary search
- MCTS
- bandits
- quality-diversity
- counterfactual repair
- adversarial search
- Pareto optimization
- random exploration
- local search
- cooperative coevolution
- surrogate-assisted search

## Adaptive Optimizer Portfolio

Do not run all optimizers fully every time.

Use specialization:

- Explorer: broad structural search
- Refiner: sample-efficient improvement
- Repairer: counterfactual/failure repair
- Robustness: reverse ablation

Architecture:

```text
Optimization Mission
 -> Search-Space Analyzer
 -> Optimizer Portfolio
    -> Explorer
    -> Refiner
    -> Repairer
 -> Shared Experiment Memory
 -> Adaptive Budget Manager
 -> promising candidates
 -> reverse/ablation tests
 -> held-out evaluation
 -> certification
```

## Optimizer Racing

Give multiple optimizers small budgets initially.

Allocate more budget to optimizers with better:

- improvement per simulation
- improvement per dollar
- improvement per minute
- failure-resolution rate
- novel-region discovery

Stop weak strategies early.

## Multi-fidelity evaluation

Possible levels:

```text
L0 static config validation
L1 tiny synthetic task
L2 historical mission fragments
L3 full replay subset
L4 complete validation corpus
L5 hidden certification corpus
```

This allows thousands of candidates to be screened cheaply.

## Surrogate performance model

Train:

```text
PredictedPerformance
 = f(Config, Mission, Team, HyperMESH, Optimizer)
```

Use it to screen huge candidate sets before expensive simulation.

Also predict uncertainty to balance exploration versus exploitation.

## Bidirectional Configuration Search

Forward:

```text
FAIL -> minimal change -> PASS
```

Reverse:

```text
PASS -> minimal change -> FAIL
```

Forward teaches what improves.
Reverse teaches what the system depends on.

Use both to build configuration sensitivity and interaction models.

## Contrastive experiment data

Store:

- positive trajectories: config -> PASS
- negative trajectories: config -> FAIL
- contrastive pairs: nearly identical configs with different outcomes

Minimal contrast pairs are especially valuable.

## Meta-Optimizer

Two-level optimization:

Inner:
find the best Agent/Team config.

Outer:
find the best optimization strategy/configuration for discovering that Agent/Team config.

Optimizer Genome fields may include:

- search algorithm sequence
- exploration rate
- mutation rate
- candidate batch
- field grouping
- surrogate
- early stopping
- fidelity schedule
- reverse-search depth
- archive strategy
- parallelism

Avoid uncontrolled recursive optimizer-of-optimizer chains. Two levels are enough until evidence proves more depth is useful.

## Quality-Diversity

Do not preserve only one winner.

Maintain specialized elites:

- best cheap Agent
- fastest Agent
- highest-reliability Agent
- best generalist
- best specialist
- low-token Agent
- low-communication Agent
- research Agent

## Pareto frontier

Keep success, cost, latency, risk and human intervention separate rather than collapsing everything into one score.
