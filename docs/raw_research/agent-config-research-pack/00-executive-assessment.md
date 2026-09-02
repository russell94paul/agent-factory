# Executive assessment

## Short answer

**Agents-as-Configuration is likely a core differentiator, but “more parameters” is not itself an
advantage.** The advantage comes from parameters that are:

- behaviorally meaningful;
- versioned as identity;
- measurable in controlled tasks;
- constrained by policy;
- matchable to mission requirements;
- attributable to outcomes;
- safe to optimize without editing the grader.

An agent with 500 decorative personality fields is less useful than one with 40 causal, certified
parameters. Every behavior-changing field multiplies the search and recertification space.

## What the repository already has

The current repository is not a blank slate:

- `factory/blueprint.py` already defines `AgentSpec`, `TeamSpec`, content-derived version IDs and
  the rule that the configuration is the identity.
- `factory/presets.py` already provides evidence-labelled starting configurations with reasons,
  escalation conditions, budgets, prohibitions and verifier state.
- `factory/metrics.py` already enforces the correct Goodhart rule: activity metrics require an
  outcome anchor.
- `factory/registry.py` already distinguishes proven, declared and unbuilt workflows.
- `factory/readiness.py` already demonstrates honest `PASS / FAIL / UNMEASURABLE / ERROR / NOT_RUN`
  measurement semantics.
- `factory/handoff.py`, `factory/bus.py` and `docs/agent-communication.md` already separate durable
  records from live delivery.
- `.agent-platform/bootstrap/schemas/mission-assembly.schema.json` and
  `capability-record.schema.json` are early contracts for mission assembly and evidence-backed
  capability.

Therefore: extend those seams. Do not create a parallel configuration product.

## Honest evaluation of the new ideas

### Highest-value concepts

1. **Configuration compiler and resolved lockfile** — foundational.
2. **Mission-to-agent/team matcher** using evidence-backed capabilities — foundational.
3. **Pre-deployment readiness uplift** with measured before/after state — high value.
4. **Adaptive communications doctrine** — high value after a second real team exists.
5. **Team metrics and confidence-labelled health** — essential for the UI and optimizer.
6. **MESH knowledge acquisition policy** — promising if defined as a mission-scoped knowledge
   routing and promotion protocol, not as an all-to-all shared memory.
7. **Sentinel observer** — useful as a read-only, fully audited event consumer.
8. **Portfolio operations loop** — high future business value after the factory can reliably ship.

### Valuable metaphors that require engineering renaming

| Metaphor | Core primitive |
| --- | --- |
| Last-minute skill-up / pick-me-up | Pre-deployment Readiness Uplift Planner |
| CIA / undercover agent | Audited Sentinel / Intelligence Observer |
| Agent family | Persistent capability lineage and bonded specialization cluster |
| Agent age | Generation, experience horizon and knowledge maturity |
| Married agents | Permissioned cognitive bond / high-trust handoff relationship |
| Personality | Bounded behavioral policy profile |
| Army rank | Authority grade, competency grade and operational role—separate fields |

These names preserve the creativity in the UI while keeping the backend precise.

### Ideas that should not be implemented literally

- **Artificially increasing all health scores before deployment.** This corrupts the instrument.
  The system may improve readiness and forecast uplift, but health moves only after measurement.
- **Using spare token capacity merely to reach a limit.** That optimizes consumption, not value.
  Use a surplus-capacity queue that only dispatches positive-expected-value, bounded tasks.
- **Storing live metrics in YAML.** YAML is versioned intent; metrics are timestamped observations.
- **All agents constantly reading the whole wiki.** This increases cost, latency and data exposure.
  Use event-triggered, mission-scoped retrieval and explicit knowledge packets.
- **A universal leaderboard.** Use outcome-specific boards; never grant authority from rank.
- **Immediate deep Army hierarchy.** The current repository correctly requires one certified team
  plus evidence that another organizational tier improves outcomes.

## Recommended platform layers

```text
Authoring      YAML presets, prompt-to-config, UI form
Contracts      JSON Schema + semantic/policy validation
Compilation    inheritance, overlays, references, defaults, secret refs
Resolution     mission-specific immutable JSON lockfile + content hash
Execution      existing control plane, deterministic verifiers, agents
Observation    events, traces, logs, measurements, costs, evidence
Learning       capability records, calibration, title/certification review
Optimization   champion/challenger search within bounded parameter spaces
Experience     Switchboard, Config Studio, Family/Lineage, Portfolio Operations
```

## Storage recommendation

| Information | Store | Reason |
| --- | --- | --- |
| Agent/team/mission presets | YAML in Git | Human review, diffs and versioning |
| Schema and policy | JSON Schema plus Python/CUE policy checks | Machine validation and composition |
| Resolved runnable configuration | Canonical JSON lockfile | Stable hashing and reproducibility |
| Secrets | Vault references only | Never place values in configuration |
| Run events and communication | Append-only event store | Replay, ordering and auditability |
| Metrics/time series | Metrics backend / analytical tables | Windowing, aggregation and alerting |
| Capability evidence | Relational records plus evidence refs | Queryable mission matching |
| Knowledge objects | Typed object store/index/graph | Provenance, permissions and retrieval |
| UI preferences | User preference store | Not part of agent identity |

## Immediate recommendation

Do not begin with Family UI, Army ranks or an optimizer. Begin with:

1. `AgentConfigV2` schema and compatibility mapper from existing `AgentSpec`.
2. resolved lockfile/compiler with every behavior-changing field in the identity hash;
3. capability/requirement contracts and a transparent baseline matcher;
4. metric definitions with event instrumentation;
5. pre-deployment readiness uplift in **recommend-only** mode;
6. one same-budget pilot comparing baseline versus recommended configuration.

That sequence tests whether configuration depth produces better outcomes before expanding the
configuration surface.

