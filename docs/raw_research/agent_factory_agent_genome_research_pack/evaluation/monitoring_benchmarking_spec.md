# Monitoring & Benchmarking Specification

## Observability levels

### L0 — Infrastructure
API/model/tool availability, quotas, execution errors, queue time.

### L1 — Agent execution
Latency, cost, tokens, tool calls, retries, context size, failure class.

### L2 — Cognition / evidence
Evidence coverage, unsupported claims, contradiction capture, calibration, retrieval precision/recall.

### L3 — Communication / relationships
Message rate, semantic density, novelty, acknowledgements, routing, duplicates, critical-message misses, handoff quality.

### L4 — Team
Role coverage, coordination overhead, rework, manager bottleneck, parallelism, team success.

### L5 — Organization
Mission outcome, cost/accepted outcome, resilience, knowledge reuse, governance, human attention.

### L6 — Evolution
Performance drift, config sensitivity, generalization, benchmark saturation, promotion/rollback rates.

## Metric catalog — do not optimize all of these

### Outcome
- mission_success
- accepted_output
- red_to_green
- first_pass_success
- regression_rate
- escaped_defect_rate

### Efficiency
- cost_per_accepted_outcome
- time_to_green
- latency
- tool_calls
- context_tokens
- queue_time
- idle_dependency_time

### Communication
- useful_message_rate
- message_to_action_conversion
- duplicate_information_rate
- missed_critical_message_rate
- evidence_propagation_latency
- communication_tokens
- unresolved_request_age
- acknowledgement_rate
- clarification_loop_count
- graph_centralization
- communication_congestion

### Context / knowledge
- material_evidence_recall
- context_precision
- stale_context_rate
- provenance_coverage
- contradiction_capture
- knowledge_reuse
- retrieval_duplication
- workspace_hit_rate

### Agent capability
- mission_capability_fit
- skill_freshness
- calibration
- recent_reliability
- domain_success
- failure_recurrence

### Relationship
- pair_success_delta
- handoff_success
- teammate_response_latency
- disagreement_resolution
- duplicate_work
- complementarity_estimate

### Team/organization
- role_coverage
- manager_span
- critical_path_blocked_time
- escalation_rate
- recovery_time
- cross_team_handoff_count
- organization_reconfiguration_count

### Trust/safety
- policy_violation
- unsupported_claim_rate
- evidence_completeness
- version_pin_completeness
- replayability
- shadow_disagreement
- human_override
- rollback_success

## Mission readiness

Do not use a flat average that can hide one catastrophic weakness.

Use a constrained or geometric aggregation, e.g.:

```text
Readiness(agent, mission) =
geomean(
  capability_fit,
  knowledge_freshness,
  recent_reliability,
  tool_environment,
  context_capacity,
  model_suitability,
  communication_fit,
  policy_certification
)
```

Also enforce hard blockers:
- missing mandatory permission;
- failed certification;
- unavailable required tool;
- known stale critical knowledge;
- risk class beyond authority.

## Benchmark vault

Each benchmark case needs:
- mission ID;
- task family;
- immutable inputs;
- expected outcome/green contract;
- failure evidence where applicable;
- allowed tools/environment;
- risk class;
- scoring;
- benchmark version;
- hidden/test designation.

## Required comparisons

1. Best single agent vs multi-agent.
2. Same model, different config.
3. Same config, different model.
4. Same agents, different communication topology.
5. Same team, different workspace/context policy.
6. Stable relationships vs randomized team.
7. Human-crafted vs optimizer-discovered config.
8. No skill-up vs predeployment skill-up.
9. Baseline vs Shadow Reviewer.
10. Static blueprint vs dynamically staffed capability team.

## Credit assignment

Do not infer contribution from message count or token count.

Research:
- leave-one-agent-out ablation;
- leave-one-component-out ablation;
- counterfactual replay;
- Shapley-like approximations where affordable;
- causal graphs;
- temporal contribution tracing;
- critical-evidence lineage.

Store uncertainty on contribution estimates.
