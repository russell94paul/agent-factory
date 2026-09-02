# High-Leverage Frameworks & Concepts to Mine

These are **research candidates**, not instructions to replace the existing Agent Factory stack.

## 1. Kubernetes CRD + Controller pattern
Transfer:
- AgentDefinition / TeamDefinition / OrganizationDefinition as declarative resources.
- controller reconciles desired certified organization state with observed runtime state.
- status is separate from spec.

High leverage insight:
**`spec` vs `status`** maps directly onto genotype vs phenotype/observed state.

## 2. Nix/Guix / lockfile thinking
Transfer:
- immutable configuration identity;
- transitive dependency pinning;
- exact reproducibility;
- rollback to known-good configuration.

Use for:
AgentLockfile including model/skill/tool/policy/eval versions.

## 3. Open Policy Agent / policy-as-code
Transfer:
- configuration can be expressive while authority/safety remains externally enforceable.
- optimizer cannot mutate its own governance constraints.

## 4. FIPA ACL / speech acts
Transfer:
Messages are typed communicative actions, not arbitrary chat.

Research candidate types:
REQUEST, INFORM, PROPOSE, COMMIT, EVIDENCE, CONTRADICTION, BLOCKER, HANDOFF, ESCALATE.

## 5. OpenTelemetry-style traces
Transfer:
- every agent/tool/message/eval operation becomes traceable;
- causality can cross agent/team boundaries;
- config/model/tool versions ride with traces.

## 6. MASEval
High leverage:
Evaluate the **system**—topology, orchestration, context, error handling—not only the model.

## 7. MultiAgentBench
High leverage:
Use multiple communication topologies and collaboration-specific milestones in evaluation.

## 8. SILO-BENCH
High leverage:
Explicitly test the communication-reasoning gap. Agent Factory should optimize useful information transfer, not communication volume.

## 9. ADAS
High leverage:
Treat agent design itself as a search/discovery problem, while retaining Agent Factory's safety and evaluation gates.

## 10. AgentSquare
High leverage:
Modular agent search suggests a useful decomposition of design dimensions and performance prediction to avoid evaluating every candidate.

## 11. AFlow
High leverage:
Workflows can be represented as a search space and improved from execution feedback.

## 12. GEPA
High leverage:
Natural-language reflection over trajectories can propose interpretable changes. Use it as a **candidate generator**, not an unbounded production updater.

## 13. Optuna
High leverage:
Practical multi-objective / TPE search for early Agent Genome experiments.

## 14. Ray Tune / Population Based Training
High leverage:
Parallel search and adaptive schedules. Especially interesting for parameters that may change over mission phases, such as reasoning budget or communication intensity.

## 15. MAP-Elites / Quality Diversity
High leverage:
Do not converge to one “super-agent.” Maintain different elites:
- cheap/fast;
- research-heavy;
- high-assurance;
- incident-response;
- ambiguous-requirements;
- long-horizon.

## 16. Toyota Production System / Andon / Jidoka
Transfer:
- agents raise typed Andon events on blockers/uncertainty/contract violations;
- stop-the-line conditions;
- root-cause learning;
- optimize flow rather than local utilization.

## 17. Theory of Constraints
Transfer:
Mission graph bottleneck detection and resource reallocation should optimize the system bottleneck, not keep every agent busy.

## 18. Crew Resource Management
Research:
Communication discipline, challenge of authority, explicit acknowledgement, error reporting, checklist/preflight concepts.

## 19. Erlang/OTP supervision
Transfer:
Recovery policies should be typed:
restart / resume / replan / escalate / replace / quarantine, with bounded blast radius.

## 20. Digital twins
Transfer:
Shadow Twin is the organizational digital twin. Evaluate counterfactual config changes against replay/live shadow evidence.

## 21. Statistical Process Control
Transfer:
Agent/team performance drift should be monitored longitudinally; not every bad run means mutate the config.

## 22. Contextual bandits
Transfer:
Once multiple certified variants exist, route missions adaptively while preserving exploration budget and safety constraints.

## 23. Design of Experiments
Transfer:
Before black-box hypertuning thousands of dimensions, use factorial/ablation experiments to identify high-effect parameters and interactions.

This may save more compute than any optimizer.
