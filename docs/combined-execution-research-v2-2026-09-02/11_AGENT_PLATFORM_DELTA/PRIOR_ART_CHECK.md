# Targeted Prior-Art / Current-Platform Check

This check was limited to the `.agent-platform` mechanisms that materially affect the synthesis.

## Execution surfaces — current Claude Code substrate exists

Anthropic's current Claude Code Remote Control documentation supports:

- local execution with local filesystem, MCP, tools and project configuration;
- server-mode session spawning;
- `--spawn worktree` for isolated on-demand sessions;
- a bounded `--capacity <N>` concurrency setting;
- sandboxing options;
- separate cloud/web sessions for cloud execution.

**Architecture implication:** the source pack's Execution Surface Policy is implementable as a routing policy over existing Claude surfaces. Do not build a remote-execution platform just to obtain this behavior. Verify the installed CLI version/flags at runtime before depending on a specific option.

## Capability discovery — reuse A2A semantics where appropriate

The current A2A protocol standardizes Agent Cards containing identity, capabilities, security requirements and skills, and supports discovery via well-known documents or registries/catalogs.

**Architecture implication:** an Agent Factory capability registry should not invent another generic agent discovery vocabulary. Its differentiated layer is the **evidence-backed certification envelope**: exact config binding, eval history, conditions, reliability/regression, cost/latency, validity and provenance.

## Tracing / message causality — prefer OpenTelemetry semantics

OpenTelemetry semantic conventions define common spans, metrics, logs and events; its messaging conventions explicitly cover cross-component context propagation, and GenAI conventions are maintained as a dedicated semantic-conventions area.

**Architecture implication:** `correlation_id`, `causation_id`, message creation context and trajectory semantics should first be mapped onto OpenTelemetry rather than becoming an isolated proprietary trace protocol.

## Result

These checks strengthen three decisions:

1. Promote Execution Surface Routing as a near-term scheduler feature.
2. Extend the existing registry with evidence/certification while reusing standard discovery concepts.
3. Keep the existing RB-02 trace-standards mission and explicitly include the `.agent-platform` message envelope as an input.
