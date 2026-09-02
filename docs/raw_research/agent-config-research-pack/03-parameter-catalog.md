# Agent and team parameter catalog

This is an exhaustive **v0 taxonomy**, not a claim that every conceivable parameter is desirable.
Fields should enter the executable schema only after a behavior hypothesis and evaluation exist.

## 1. Identity, lineage and presentation

`id`, `schema_version`, `display_name`, `description`, `icon`, `tags`, `created_at`, `created_by`,
`generation`, `parent_config_refs`, `lineage_family`, `variant`, `lifecycle_state`, `deprecation`,
`content_hash`, `certification_refs`, `annotation_labels`.

Identity-changing: parents, executable dependencies and lifecycle state. Usually cosmetic:
display name, icon and description.

## 2. Organizational position

`org_type`, `doctrine`, `formation_type`, `echelon`, `operational_role`, `authority_grade`,
`competency_grade`, `reports_to`, `manages`, `peer_group`, `staff_function`, `decision_rights`,
`delegation_rights`, `escalation_chain`, `scope_of_command`, `span_of_control`, `reserve_status`,
`succession_policy`.

Do not use a single Army rank to infer tools, expertise or permissions.

## 3. Mission applicability

`task_families`, `domains`, `subdomains`, `industries`, `repositories`, `technologies`, `languages`,
`clouds`, `data_systems`, `frameworks`, `artifact_types`, `risk_classes`, `environment_classes`,
`client_scopes`, `jurisdictions`, `mission_exclusions`, `requirement_predicates`,
`minimum_evidence_count`, `minimum_capability_confidence`.

Example specialities: Python, SQL, Snowflake, Prefect, AWS, Azure, Power BI, API integration,
reliability investigation, evidence review and technical design.

## 4. Model and inference

`provider`, `model`, `model_snapshot`, `reasoning_effort`, `temperature`, `top_p`, `max_output`,
`structured_output_schema`, `response_format`, `seed_policy`, `fallback_models`, `routing_policy`,
`model_selection_reason`, `model_escalation_conditions`, `latency_class`, `cost_class`,
`context_window_policy`, `cache_policy`.

## 5. Prompt and behavioral instructions

`system_prompt_ref`, `role_prompt_ref`, `mission_prompt_template`, `prompt_variables`,
`instruction_precedence`, `prohibitions`, `required_behaviors`, `output_contract`,
`self_check_protocol`, `uncertainty_protocol`, `citation_policy`, `assumption_policy`,
`clarification_policy`, `completion_definition`, `refusal_policy`, `style_guide_refs`.

## 6. Bounded “personality” / working temperament

Use behavioral controls rather than fictional biography:

`verbosity`, `directness`, `assertiveness`, `curiosity`, `skepticism`, `risk_tolerance`,
`novelty_appetite`, `persistence`, `patience`, `planning_horizon`, `detail_orientation`,
`evidence_threshold`, `ambiguity_tolerance`, `collaboration_bias`, `delegation_bias`,
`help_seeking_threshold`, `challenge_authority_threshold`, `creative_divergence`,
`convergence_speed`, `reflection_frequency`, `status_reporting_style`, `conflict_style`,
`teaching_depth`, `user_explanation_level`.

Every field should use a bounded enum or `[0,1]` scale and have a stated behavioral expectation.
Do not present these as emotions or mental states.

## 7. Tools and execution surface

`tools`, `tool_versions`, `tool_allowlist`, `tool_denylist`, `tool_scopes`, `tool_call_budget`,
`tool_parallelism`, `tool_timeout`, `tool_retry_policy`, `tool_confirmation_policy`,
`shell_policy`, `filesystem_roots`, `network_policy`, `browser_policy`, `database_policy`,
`code_execution_policy`, `sandbox_profile`, `artifact_write_paths`, `secret_refs`,
`credential_health_requirements`, `external_action_policy`.

## 8. Skills and capability assets

`skill_refs`, `skill_versions`, `skill_priority`, `skill_activation_rules`, `skill_conflicts`,
`skill_prerequisites`, `skill_eval_refs`, `skill_expiry`, `course_completion_refs`,
`simulation_certifications`, `procedural_playbooks`, `prompt_snippets`, `template_refs`,
`capability_evidence_refs`, `known_failure_modes`.

## 9. Knowledge and MESH behavior

`knowledge_domains`, `knowledge_snapshot_refs`, `retrieval_policy`, `retrieval_top_k`,
`relevance_threshold`, `freshness_requirement`, `provenance_requirement`, `confidence_floor`,
`permission_filter`, `mission_scope_filter`, `contradiction_policy`, `knowledge_gap_detection`,
`scan_triggers`, `scan_frequency`, `publish_triggers`, `promotion_policy`, `citation_depth`,
`context_packet_budget`, `compression_policy`, `forgetting/expiry_policy`, `cross_repo_policy`,
`subscriber_topics`, `publisher_topics`, `knowledge_request_routes`.

MESH should mean **Mission-scoped Evidence and Skill Hydration**: a policy-driven system that maps
mission requirements to permissioned knowledge/skill packets, observes gaps during execution and
promotes durable learnings with provenance.

## 10. Memory and context

`working_memory_budget`, `checkpoint_policy`, `checkpoint_triggers`, `summary_policy`,
`context_compaction_threshold`, `context_priority_rules`, `conversation_retention`,
`artifact_retention`, `thread_scope`, `long_term_store_scope`, `episodic_memory_policy`,
`semantic_memory_policy`, `memory_write_permissions`, `memory_read_permissions`,
`memory_conflict_policy`, `handoff_packet_schema`, `resume_policy`, `staleness_threshold`.

## 11. Communication and coordination

`communication_topology`, `allowed_targets`, `channel_types`, `broadcast_policy`,
`need_to_know_policy`, `message_schema`, `message_priority`, `ack_requirement`,
`consumption_confirmation`, `reply_requirement`, `max_message_size`, `frequency_mode`,
`base_frequency`, `adaptive_intensity_formula`, `silence_policy`, `status_report_frequency`,
`handoff_trigger`, `handoff_acceptance_contract`, `alert_thresholds`, `alert_cooldown`,
`deduplication_policy`, `escalation_timeout`, `human_notification_policy`, `meeting/sync_policy`,
`communication_budget`, `noise_budget`.

## 12. Relationships and bonds

`bond_type`, `partner_refs`, `trust_scope`, `shared_context_policy`, `shared_knowledge_policy`,
`mutual_review_policy`, `wake_on_struggle`, `intervention_threshold`, `rescue_permissions`,
`reserve_swarm_capacity`, `complementarity_score`, `familiarity_score`, `handoff_history`,
`relationship_expiry`, `relationship_eval`, `privacy_boundary`.

Suggested bond types: `none`, `peer`, `mentor`, `apprentice`, `cognitive_pair`, `review_pair`,
`observer`, `reserve`, `lineage_parent`, `lineage_descendant`.

## 13. Autonomy, authority and safety

`autonomy_level`, `reversible_action_policy`, `privileged_action_policy`, `human_gates`,
`approval_token_requirements`, `change_scope`, `blast_radius_limit`, `data_classification`,
`tenant_boundary`, `repo_boundary`, `production_access`, `deploy_access`, `merge_access`,
`grader_edit_access`, `eval_corpus_access`, `rollback_requirement`, `evidence_requirement`,
`side_effect_budget`, `emergency_stop_policy`, `incident_escalation`, `audit_level`.

## 14. Workflow and control

`workflow_ref`, `workflow_version`, `stage_roles`, `dependencies`, `parallelism`, `critical_path`,
`entry_conditions`, `exit_conditions`, `termination_conditions`, `retry_conditions`,
`retry_strategy`, `max_attempts`, `backoff`, `failure_routing`, `recovery_routing`,
`checkpoint_stages`, `verification_stages`, `human_gate_stages`, `compensation_steps`,
`rollback_steps`, `timeout_policy`, `pause_policy`, `resume_policy`, `cancellation_policy`.

## 15. Budget and capacity

`budget_usd`, `token_budget`, `turn_budget`, `time_budget`, `tool_budget`, `compute_budget`,
`parallel_agent_cap`, `reserve_budget`, `retry_budget`, `research_budget`, `communication_budget`,
`budget_warning_threshold`, `budget_stop_threshold`, `surplus_capacity_policy`,
`capacity_reset_window`, `expected_value_floor`, `marginal_value_stop`, `cost_allocation_tags`.

## 16. Evaluation, certification and learning

`green_contract`, `verifier_refs`, `evaluator_version`, `eval_corpus_hash`, `negative_controls`,
`unseen_eval_policy`, `baseline_ref`, `champion_ref`, `acceptance_threshold`, `confidence_interval`,
`minimum_sample`, `regression_policy`, `side_effect_checks`, `calibration_policy`,
`recertification_triggers`, `certification_expiry`, `title_review_trigger`, `promotion_policy`,
`demotion_policy`, `learning_update_policy`, `failure_attribution_policy`, `credit_assignment`.

## 17. Observability and health

`trace_policy`, `span_attributes`, `event_types`, `log_level`, `metric_set`, `health_formula_ref`,
`struggle_formula_ref`, `health_caps`, `measurement_window`, `ewma_alpha`, `heartbeat_policy`,
`stall_threshold`, `thrash_threshold`, `error_budget`, `alert_rules`, `metric_basis`,
`metric_confidence`, `telemetry_sampling`, `retention`, `redaction`, `dashboard_views`.

## 18. Output and artifact policy

`output_types`, `output_schema`, `artifact_template`, `naming_policy`, `destination_refs`,
`provenance_manifest`, `citation_manifest`, `diff_requirement`, `test_report_requirement`,
`rollback_artifact_requirement`, `client_review_policy`, `quality_checks`, `render_checks`,
`accessibility_checks`, `publish_gate`, `retention_policy`.

## 19. Team-level configuration

### Identity and purpose

`team_id`, `team_type`, `purpose`, `north_star`, `mission_families`, `domain`, `repositories`,
`technologies`, `clients`, `risk_class`, `lifecycle`, `version`, `owner`.

### Composition and hierarchy

`manager`, `members`, `seats`, `required_roles`, `optional_roles`, `reserve_roles`, `topology`,
`hierarchy`, `span_of_control`, `staffing_constraints`, `subteams`, `external_participants`,
`human_roles`, `substitution_policy`, `scaling_policy`.

### Working style and architecture

`working_style`, `planning_mode`, `execution_mode`, `review_mode`, `decision_mode`,
`conflict_resolution`, `workflow`, `state_model`, `shared_context`, `artifact_contract`,
`handoff_contract`, `verifier_separation`, `grader_separation`, `deployment_model`,
`isolation_model`, `parallelism`, `synchronization_points`.

### Communication, sharing and alerting

`communication_topology`, `sharing_scope`, `frequency_policy`, `scan_policy`, `publish_policy`,
`alert_routes`, `severity_model`, `ack_policy`, `handoff_policy`, `wiki_policy`, `MESH_policy`,
`communication_effectiveness_formula`, `noise_budget`, `meeting_budget`, `human_escalations`.

### Team metrics

`outcome_metrics`, `quality_metrics`, `flow_metrics`, `efficiency_metrics`,
`communication_metrics`, `coordination_metrics`, `resilience_metrics`, `knowledge_metrics`,
`safety_metrics`, `economic_metrics`, `user_value_metrics`, `north_star_metric`,
`activity_outcome_pairs`, `measurement_basis`, `confidence_policy`, `dashboard_thresholds`.

## Fields an agent may change

Do not ask only whether a field is configurable. Classify mutation authority:

| Mutability | Meaning | Examples |
| --- | --- | --- |
| `immutable` | Requires new version and human-reviewed config | authority, grader, prohibitions |
| `mission_overlay` | Operator/matcher may change before lock | task refs, context packet, budget within cap |
| `adaptive_bounded` | Agent may adjust within declared range | scan interval, reasoning effort, tool retry |
| `self_proposed` | Agent can propose; approval required | new tool, skill, partner, title |
| `runtime_state` | Not configuration; emitted as events | health observation, progress, current blocker |

This table is more important than adding another personality field.

