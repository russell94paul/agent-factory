# Agents-as-Configuration: configuration and storage design

## Research question

How should a platform author, validate, compose, version, execute, observe and optimize deeply
configurable agents and teams without turning configuration into an untestable second programming
language?

## Decision

Adopt a four-form configuration lifecycle:

1. **Authoring form:** YAML, optimized for humans and Git review.
2. **Validation form:** JSON-compatible object validated against modular JSON Schema 2020-12 and
   cross-field policy checks.
3. **Resolved form:** canonical JSON with every default, reference, inheritance layer and mission
   overlay resolved.
4. **Observed form:** events and measurements stored separately, linked to the resolved config hash.

```text
base preset
  + organization doctrine
  + domain preset
  + role preset
  + team/relationship overlay
  + mission requirements
  + operator-approved overrides
  = immutable resolved-config.lock.json
```

The resolved file—not the authored YAML—is executed and certified.

## Why YAML, but not YAML alone

YAML is suitable because it is readable, supports comments and already exists in `blueprints/`.
CrewAI and many deployment systems use configuration files for similar authoring benefits. But YAML
has hazards: implicit types, aliases, duplicate keys, loose extension fields and complex merge
behavior. Restrict the supported YAML subset and immediately parse into typed structures.

Rules:

- reject duplicate keys;
- reject unknown keys by default;
- forbid executable tags and arbitrary object construction;
- forbid secrets—only secret references are allowed;
- make inheritance explicit with `extends`, not YAML merge keys;
- resolve environment-dependent values before hashing;
- canonicalize arrays whose order is semantically irrelevant;
- retain source maps so validation errors point to the authored file;
- require `schema_version` and a migration path.

JSON Schema provides a standard vocabulary for document structure and validation and supports
modular references. Use `$id`, `$defs`, `$ref`, `if/then`, and `unevaluatedProperties: false`.
Official sources: https://json-schema.org/learn/getting-started-step-by-step and
https://json-schema.org/understanding-json-schema/structuring

## Where CUE may fit

CUE is attractive for policy-heavy composition because it combines data, schemas and constraints,
and can validate YAML/JSON. It is particularly useful when multiple overlays must unify rather than
silently override one another. Official documentation emphasizes validation-first configuration and
separation of computation from configuration:

- https://cuelang.org/docs/concept/how-cue-enables-configuration/
- https://cuelang.org/docs/concept/configuration-use-case/
- https://cuelang.org/docs/integration/

Recommendation: do **not** require CUE in v1. Start with the repository's Python/YAML stack and JSON
Schema. Evaluate CUE in a research branch when overlay conflicts become difficult to express.

## Repository integration

### Extend rather than replace

`factory/blueprint.py` currently hashes the full behavior-changing `AgentSpec` and `TeamSpec`, using
a deny-list for non-identity fields. Preserve this principle.

Proposed evolution:

```text
AgentSpec (compatibility model)
    ↓ migrate/normalize
AgentConfigV2
    ↓ resolve references + defaults + mission overlay
ResolvedAgentConfig
    ↓ canonical JSON + SHA-256
AgentVersion / certification key
```

Add new modules only along clear responsibilities:

```text
factory/config/
  models.py       typed authored and resolved models
  loader.py       restricted YAML loading and source maps
  compiler.py     inheritance, overlays and canonicalization
  policies.py     cross-field safety/semantic constraints
  identity.py     hashing, lockfile and dependency pins
  migrations.py   schema-version upgrades
  diff.py         semantic config diffs and recertification impact
  matcher.py      requirement filtering and explainable ranking
```

Existing `factory/presets.py` should become either generated from YAML or a typed registry over the
same canonical model. Avoid two sources of truth.

### Strengthen existing bootstrap schemas

The current `mission-assembly.schema.json` requires useful top-level fields, but
`communication_routes`, `context_packets`, `gates` and `budget` accept unconstrained objects. It
also permits unknown fields. This is a sketch, not yet a production contract.

Required changes:

- add `$id` and explicit version;
- use `$defs` for participants, routes, packets, gates and budgets;
- set `unevaluatedProperties: false`;
- require authority, risk, context and evaluation policies;
- reference versioned participant and capability records;
- include mission requirement weights and rejected-candidate explanations;
- distinguish authored assembly from resolved assembly.

The current `capability-record.schema.json` is a strong seed: evidence count, confidence, validity,
cost, latency and evidence references already exist. Extend it with evaluator version, task
distribution, environment, failure modes, calibration and recency decay.

## Data placement matrix

| Data class | Example | Correct store | Versioning/retention |
| --- | --- | --- | --- |
| Declarative intent | role, tools, doctrine, communication policy | Git YAML | Git history + schema version |
| Compiled identity | resolved model/tool versions, exact policies | JSON lockfile/artifact store | Immutable; content addressed |
| Runtime state | queued/running/blocked/current step | Operational DB/event projection | Mutable projection, reconstructable |
| Events | handoff sent, tool failed, gate approved | Append-only event log | Durable ordering and cursor |
| Metrics | latency, health components, communication quality | Time-series/warehouse | Timestamped, basis + confidence |
| Evidence | test result, diff, artifact, source claim | Evidence/object store | Immutable references and provenance |
| Capabilities | Python success under Azure conditions | Relational/analytical store | Bitemporal validity and evidence refs |
| Knowledge | findings, summaries, procedures, source refs | Typed knowledge service/index/graph | Permissions, provenance, freshness |
| Secrets | API credential | Vault | Reference only in configs |
| UI preferences | theme, density, layout | Preference store | User-level; not config identity |

## Identity and certification

Every behavior-changing dependency belongs in the identity hash:

- prompt and prompt template version;
- model provider/name/snapshot and inference settings;
- effort/reasoning policy;
- tool names, tool versions, allow/deny scope;
- skills and versions;
- knowledge snapshot/selection policy;
- memory policy;
- communication policy;
- autonomy and approval gates;
- budgets, turn/retry/timeout limits;
- workflow/topology and handoff contracts;
- verifier/eval contract versions;
- repository and environment scope;
- relationship/bond policies;
- personality/behavior policy when it changes decisions.

Annotations such as display name, icon and human description may be outside identity. The existing
deny-list approach is safer than hand-selecting identity fields.

Produce an impact diff:

```text
cosmetic       no recertification
operational    targeted smoke evaluation
behavioral     task-family recertification
authority      security review + full relevant certification
evaluation     prior scores invalid until recalibrated
```

## Preset and overlay model

Avoid one enormous YAML file. Use composable documents:

```text
presets/base/agent-v2.yaml
presets/doctrines/adaptive-mission-command.yaml
presets/domains/data-platform.yaml
presets/roles/evidence-reviewer.yaml
presets/styles/skeptical-precise.yaml
presets/relationships/cognitive-pair.yaml
presets/teams/reliability-cell.yaml
missions/CLIENT-REV-042.yaml
resolved/CLIENT-REV-042/<hash>.lock.json
```

Precedence must be explicit and conflict-aware. A mission cannot loosen a base prohibition unless
the schema marks that field overridable and policy authorizes the operator.

## Prompt-to-config

The LLM proposes configuration; deterministic code validates and resolves it.

```text
Prompt → requirements extraction → candidate preset refs → proposed overrides
      → schema validation → policy validation → semantic diff → operator approval
      → micro-eval → resolved lockfile
```

Never allow the same proposing agent to silently author, approve, execute and grade its config.

## External pattern findings

- Current CrewAI documentation supports configuration-defined agents/tasks, showing market demand
  for declarative authoring, but also demonstrates that configuration formats evolve; keep an
  internal canonical schema rather than adopting a framework's file as your domain model.
- AutoGen exposes materially different team patterns—round-robin, selector and handoff-driven
  swarm—supporting `topology` and `speaker_selection` as explicit configuration dimensions.
- LangGraph separates thread checkpoints from long-term stores, matching the recommended split
  between current mission state and reusable knowledge.
- OpenTelemetry semantic conventions provide the right model for common metric/event naming across
  agents, teams and runtimes. Use spans for operations with duration and events for meaningful
  checkpoints or state changes.

Sources:

- https://docs.crewai.com/en/concepts/agents
- https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/teams.html
- https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/swarm.html
- https://docs.langchain.com/oss/python/langgraph/persistence
- https://opentelemetry.io/docs/concepts/semantic-conventions/
- https://opentelemetry.io/docs/specs/semconv/general/events/

## Main risk: combinatorial explosion

If 30 independent parameters each have five choices, the naive search space is (5^{30}). The
platform must define:

- frozen parameters;
- conditional parameters applicable only to certain roles/tasks;
- bounded search domains;
- causal hypotheses for each optimized field;
- hierarchical optimization: agent first, then formation, then doctrine;
- champion/challenger promotion thresholds;
- budget and marginal-improvement stop rules;
- recertification scope from semantic diffs.

The product moat is not the number of fields. It is the ability to prove which configuration works,
under what conditions, and why.

