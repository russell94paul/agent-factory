# Metrics, Health & Recurring Failure Rate

## Recurring Failure Rate is first-class

Simple failure rate does not distinguish novel failures from the organization repeatedly making the same mistake.

### Recurring Failure Rate (RFR)

```text
RFR = recurring incident occurrences / total incident occurrences
```

Use **incidents**, not raw failed attempts.

Example:

- 40 incidents
- 14 match an existing failure family
- RFR = 35%

## Failure hierarchy

```text
Attempt Failure
  ↓
Incident
  ↓
Failure Fingerprint
  ↓
Failure Family
  ↓
Recurrence
  ↓
Prior Response / Doctrine / Knowledge
```

Retries inside one incident are not separate recurrences.

## Failure fingerprint

Suggested fields:

- failure family
- subsystem
- component
- root cause
- stage
- error/signature
- dependency
- semantic fingerprint
- prior remediation

## Additional recurrence metrics

### Recurring Incident Count
Absolute recurrence volume.

### Failure Family Frequency
Top recurring classes.

### Time to Recurrence
How soon a supposedly resolved problem returns.

### Post-Fix Recurrence Rate

```text
fixed failure families that recur / failure families marked fixed
```

Measures whether fixes are actually durable.

### Preventable Recurrence Rate (PRR)

```text
recurrences where adequate preventive knowledge/control existed / all recurring incidents
```

This is an organizational learning metric.

## Organizational Learning Failure diagnosis

For a recurrence where prevention should have been possible:

1. Did relevant knowledge exist?
2. Was it retrieved?
3. Was it delivered to the correct unit?
4. Was it understood?
5. Was it followed?
6. Was the doctrine itself effective?

Classify failure as:

- knowledge gap
- retrieval failure
- communication failure
- context/prompt failure
- execution failure
- doctrine failure

## Top-level Army Health candidate metrics

- Operation Success Rate
- First-Pass Success
- Recurring Failure Rate
- Preventable Recurrence Rate
- Cost per Accepted Outcome
- Time-to-Green
- Human Intervention Rate
- Knowledge Reuse Rate
- Doctrine Effectiveness
- Readiness
- Evaluation Pass Rate
- Rework Rate
- Gate Rejection Rate

## Hierarchical aggregation

RFR should be queryable at any node:

```text
Engineering Command        6%
Integration Corps          8%
Connector Division        11%
API Battalion             17%
Authentication Company    31%
OAuth Squad               42%
```

This can directly drive the Battlefield View: high-recurrence units become visually urgent and may trigger improvement missions.

## Recurrence response policy

See `schemas/failure_recurrence.schema.yaml`.
