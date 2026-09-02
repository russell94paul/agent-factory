# Simulation & Hypertuning Architecture

## Principle

Do not optimize one scalar “Agent Score.”

Maintain a Pareto frontier for mission families.

Candidate objectives:
- maximize mission quality;
- maximize reliability;
- maximize first-pass success;
- minimize cost;
- minimize latency;
- minimize human attention;
- minimize communication overhead;
- maximize evidence/provenance completeness;
- maximize knowledge reuse.

Guardrails:
- policy violations = hard failure;
- unsupported-claim threshold;
- regression ceiling;
- budget ceiling;
- minimum calibration;
- minimum replayability.

## Unit of optimization

A trial should have:

```text
MissionSnapshot
+ EnvironmentSnapshot
+ AgentGenome(s)
+ RelationshipPolicy
+ CommunicationTopology
+ OrgIR
+ Randomness/seed metadata
+ EvaluationContract
```

## Hierarchical search

Do not mutate all dimensions simultaneously at first.

### Phase 1 — single-agent microbenchmarks
Tune:
- reasoning/control;
- context policy;
- tool policy;
- communication when interacting with a fixed harness;
- budget.

### Phase 2 — pair / relationship experiments
Freeze good single-agent configs, then tune:
- reviewer-builder pairing;
- challenge/deference;
- communication rate;
- context sharing;
- handoff policies.

### Phase 3 — team topology
Tune:
- team size;
- roles;
- manager ratio;
- topology;
- workspace;
- routing.

### Phase 4 — organization
Tune:
- multiple teams;
- temporal layers;
- federation;
- governance;
- shadow/challenger deployment.

This drastically reduces combinatorial explosion.

## Search algorithms

Use several optimizers because the space is mixed and non-stationary:

- **Random search + early stopping:** mandatory baseline.
- **TPE/Bayesian optimization:** efficient for a moderate subset of parameters.
- **ASHA/Hyperband:** terminate poor configurations early where partial mission metrics are predictive.
- **Population Based Training:** interesting for adaptive schedules (e.g., communication intensity or reasoning effort changing over mission phase), but must not copy unvalidated production state.
- **Evolutionary / genetic search:** useful for categorical structures and topology.
- **MAP-Elites / Quality Diversity:** preserve multiple elite agent/team species for different mission niches.
- **MCTS / code-graph search:** useful for workflow/topology generation.
- **Reflective language optimization:** use trajectory analysis to propose config changes, but proposals remain candidates.

## Multi-objective trial score

Store vector values rather than collapsing too early:

```yaml
fitness:
  quality: 0.91
  reliability: 0.94
  cost_usd: 2.10
  latency_seconds: 210
  human_attention_minutes: 1.2
  communication_tokens: 8400
  provenance_coverage: 0.98
  knowledge_reuse: 0.64
```

Only rank after applying mission-specific constraints.

## Anti-overfitting

Required:
- frozen training mission set;
- frozen validation mission set;
- hidden held-out test;
- time-based holdout;
- mission-family holdout;
- adversarial/failure cases;
- benchmark versioning;
- no optimizer access to held-out labels;
- refresh benchmarks as configs become saturated.

## Replication

LLM execution is stochastic.

For candidate promotion:
- repeated trials;
- confidence interval;
- effect size;
- comparison against fixed baseline;
- ablation of major changed parameters.

## Promotion pipeline

```text
candidate genome
→ schema/type check
→ policy check
→ micro eval
→ replay benchmark
→ held-out benchmark
→ shadow twin
→ canary
→ certified preset
```

## Optimization archive

Never keep only the winner.

Maintain:
- configuration lineage;
- mutation ancestry;
- benchmark version;
- mission niche;
- Pareto rank;
- failure modes;
- sensitivity analysis;
- promotion/retirement history.

This becomes the empirical memory of Agent Factory itself.
