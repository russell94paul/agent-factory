# Sources and Repository Evidence

## Agent Factory repository

- `factory/blueprint.py` — current `AgentSpec`, `TeamSpec`, serialization and config hashing.
- `factory/presets.py` — evidence-labelled presets, escalation triggers, caps and prohibitions.
- `factory/metrics.py` — activity/outcome pairing and Goodhart checks.
- `factory/readiness.py` — PASS/FAIL/UNMEASURABLE/NOT_RUN/ERROR readiness measurements.
- `factory/teamplan.py` — dependency closure, ownership gates and parallel execution layers.
- `factory/registry.py` — declared, proven and unbuilt workflow registry.
- `docs/agent-communication.md` — durable record/live channel split and current one-way bus limit.
- `docs/agent-army/CURRENT_STATE.md` — implemented seams and explicit preconditions for Army work.
- `docs/agent-army/APPROVED_CONCEPTS.md` — no Agent Army concept is currently approved.
- `blueprints/orchestrator_team.yaml` — rejected three-agent sequential blueprint and evidence caveats.
- `.agent-platform/bootstrap/schemas/mission-assembly.schema.json` — mission assembly contract with underspecified nested objects.
- `.agent-platform/bootstrap/schemas/capability-record.schema.json` — existing capability/evidence record seed.

Repository: <https://github.com/russell94paul/agent-factory>

## Configuration and observability references

- JSON Schema, Getting Started: <https://json-schema.org/learn/getting-started-step-by-step>
- JSON Schema, Structuring and `$ref`: <https://json-schema.org/understanding-json-schema/structuring>
- JSON Schema, Object validation: <https://json-schema.org/understanding-json-schema/reference/object>
- CUE, Configuration use case: <https://cuelang.org/docs/concept/configuration-use-case/>
- CUE, How CUE enables configuration: <https://cuelang.org/docs/concept/how-cue-enables-configuration/>
- CUE integrations: <https://cuelang.org/docs/integration/>
- OpenTelemetry semantic conventions: <https://opentelemetry.io/docs/concepts/semantic-conventions/>
- OpenTelemetry event semantic conventions: <https://opentelemetry.io/docs/specs/semconv/general/events/>

## Current agent-framework patterns

- CrewAI YAML configuration: <https://docs.crewai.com/en/concepts/agents>
- AutoGen team patterns: <https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/teams.html>
- AutoGen Swarm and handoffs: <https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/swarm.html>
- LangGraph persistence: <https://docs.langchain.com/oss/python/langgraph/persistence>
- LangGraph memory: <https://docs.langchain.com/oss/python/langgraph/add-memory>

These are design inputs, not proof that a pattern improves Agent Factory. Proposed changes still
need repository-specific evaluation and negative controls.
