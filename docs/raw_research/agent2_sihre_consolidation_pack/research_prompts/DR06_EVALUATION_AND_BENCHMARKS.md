# DR06 — Evaluation Framework for Agent 2.0

Design an evaluation system capable of proving whether the added architecture improves anything.

Required dimensions:
- mission outcome,
- test-backed correctness,
- cost,
- latency,
- calibration,
- abstention quality,
- recovery after drift,
- failure correlation,
- human rework,
- tail risk,
- verification efficiency,
- knowledge reuse,
- contextual trust quality,
- robustness under tool/model changes.

Require:
- temporal train/validation/test splits,
- holdout regimes,
- counterfactual replay,
- ablation studies,
- component contribution analysis,
- bootstrap/statistical uncertainty,
- Goodhart-resistant metrics.

Compare:
- single best agent,
- static team,
- fixed planner/executor/reviewer,
- SIHRE-routed agent,
- covariance-aware team,
- contextual-trust team,
- full Agent 2.0.

Return:
- benchmark design,
- minimum sample sizes where possible,
- metric definitions,
- experiment matrix,
- stop/go criteria for each major feature.
