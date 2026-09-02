# Experiment Backlog — Highest Information Gain First

## E01 — Spec vs Status split
Implement AgentDefinition `spec` and runtime `status/events`.
**Question:** Does this prevent config/history drift and simplify versioning?
Effort: Low.

## E02 — Frozen Agent Lockfile
Record model/skill/tool/policy/eval versions per mission.
**Question:** Can runs be replayed/explained reliably?
Effort: Low.

## E03 — Quiet vs Loud communication
Same agents/tasks; vary communication phenotype only.
Measure quality, latency, tokens, missed critical info.
Effort: Low–Medium.

## E04 — Communication governor
Add message materiality filtering/batching.
Compare against unrestricted peer chat.
Effort: Medium.

## E05 — Builder + Challenger pair
Compare builder-only vs fixed skeptical peer.
Measure defects caught, latency, cost, false rejection.
Effort: Low–Medium.

## E06 — Relationship stability
Stable agent pairs vs randomized pairings across repeated task family.
Test whether “chemistry” persists after controlling for individual quality.
Effort: Medium.

## E07 — Mission readiness
Block/degrade agents with missing knowledge/tool/certification dimensions.
Measure avoided failures.
Effort: Medium.

## E08 — Predeployment pit crew
Knowledge refresh + tool preflight + micro-eval before mission.
Measure success delta vs cost/latency.
Effort: Medium.

## E09 — Context Quartermaster
Role-shaped context vs raw/shared context.
Measure evidence recall, token volume, outcome.
Effort: Medium.

## E10 — 20-item Global Workspace
Bound shared promoted context.
Compare to shared transcript and no shared memory.
Effort: Medium.

## E11 — Single agent vs team
Same budget; compare best single agent against 2/3/5-agent teams.
Effort: Medium.

## E12 — Topology sweep
Star vs tree vs graph vs capability-routed.
Use fixed agents and benchmark.
Effort: Medium.

## E13 — Optuna/TPE Agent Genome v1
Tune 8–12 high-effect parameters, not the full schema.
Effort: Medium.

## E14 — Factorial parameter sensitivity
Estimate interaction effects for communication × verification × context size × budget.
Effort: Medium.

## E15 — Shadow optimizer promotion
Optimizer-generated candidate runs only in replay/shadow.
Test promotion pipeline and rollback.
Effort: Medium.

## E16 — Quality-diversity archive
Maintain distinct elites for cheap/fast, high-assurance and research-heavy mission niches.
Effort: Medium–High.

## E17 — Capability router
Dynamic staffing from required capability vector.
Compare to static presets.
Effort: Medium.

## E18 — Meta-tool miner
Detect repeated stable tool sequences and propose deterministic macro.
Effort: Medium.

## E19 — Agent KG Mesh projection
Join mission + capability + communication data.
Answer high-value routing/bottleneck queries.
Effort: Medium–High.

## E20 — Counterfactual teammate replacement
Replay same mission with one teammate substituted.
Estimate relationship contribution.
Effort: High.

## E21 — Adaptive communication intensity
Communication starts high during discovery, reduces during execution.
Compare against stationary phenotype.
Effort: High.

## E22 — Population-based configuration schedules
Sandbox-only experiment on phase-dependent parameters.
Effort: High.

## E23 — Org genome search
Search limited team topology + roles + communication policy.
Requires mature eval vault.
Effort: High.

## E24 — Stigmergic blocker field
Agents recruit based on typed mission signals without central routing.
Research only until eval substrate is robust.
Effort: High.

## E25 — Self-maintaining config reconciler
Quarantine degraded versions, route to last certified version, never self-promote.
Effort: High.
