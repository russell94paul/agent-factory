# Evaluation and Promotion Gates

Any major agent/team/organization change should define measurable promotion evidence before broad deployment.

## Minimum gate shape

1. **Specific objective** — what outcome should improve?
2. **Baseline** — what happens without the change?
3. **RED evidence** — a recorded failure or inadequacy the change is meant to address.
4. **GREEN evidence** — the change demonstrably fixes/improves the target.
5. **Regression suite** — existing accepted behavior remains green.
6. **Cost / latency** — improvement is not purchased with unacceptable resource growth.
7. **Human-gate metrics** — rejection/rework/escalation are tracked when humans review output.
8. **Safety / blast radius** — permissions and rollback reflect the risk class.
9. **Replay / provenance** — decisions, tool calls, inputs and outputs are inspectable enough to diagnose failures.
10. **Post-promotion measurement** — production outcomes determine whether the candidate stays promoted.

For self-improvement systems, add holdout/hidden evals and periodic metric review to reduce optimization gaming.
