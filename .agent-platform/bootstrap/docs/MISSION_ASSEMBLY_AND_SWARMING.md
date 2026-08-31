# Mission Assembly, Availability & Swarming

## Agent configuration step

A mission should eventually compile through a configuration step before execution:

```text
Intent / Mission
      ↓
Task-family + risk classification
      ↓
Required capabilities
      ↓
Historical similarity / prior experts
      ↓
Available agents + skills + tools + compute
      ↓
Blueprint / topology candidates
      ↓
Communication routes + context routes
      ↓
Budget / authority / gates
      ↓
Resolved Mission Assembly Plan
```

## Swarming is conditional

Swarming is not the default. A temporary swarm should form only when the mission benefits from parallel exploration, diverse expertise, or independent verification.

The assembler should decide:

- fixed owner vs parallel agents;
- active worker vs consulted expert vs passive subscriber;
- maximum participants;
- joining/leaving conditions;
- synchronization/synthesis point;
- conflict resolution;
- authority and final decision ownership.

## Availability

Availability is more than idle/busy:

```text
agent_id
current_load
capabilities
environment/tool access
cost lane
latency expectation
recent relevant experience
health
budget remaining
permission scope
```

Do not make historical success the only routing signal; protect against over-specialization and stale capability evidence.
