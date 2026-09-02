# 07 — Metrics, Failure Recurrence & Army Health

## Recurring Failure Rate (RFR)

Failure rate and recurring failure rate are different.

Basic definition:

`RFR = repeated failure occurrences / total failure occurrences`

RFR answers:
> How much of our failure volume comes from problems we have already encountered?

## Event model

Do not count retries as separate recurrences.

Hierarchy:
- Attempt Failure
- Incident
- Failure Fingerprint
- Failure Family
- Recurrence
- Previous Response
- Prevention Knowledge/Control
- Outcome

Example:
One mission retries the same failing operation three times = one incident with three failed attempts.

If the same root-cause family returns on later dates = recurrence.

## Failure fingerprint

Potential fields:
- failure_family
- subsystem
- component
- root_cause
- stage
- error_signature
- semantic_embedding/fingerprint
- affected_dependency
- prior_remediation

Do not rely on literal error-string equality.

## Recurrence metric suite

### 1. Recurring Failure Rate
Repeated failure occurrences / all failure occurrences.

### 2. Recurring Incident Count
Number of later incidents matching a previous failure family.

### 3. Failure Family Frequency
Occurrences by root cause family.

### 4. Time to Recurrence
Elapsed time from remediation/closure to next incident in same family.

### 5. Post-Fix Recurrence Rate
Failure families marked fixed that later recur / failure families marked fixed.

### 6. Preventable Recurrence Rate
Recurring incidents where sufficient preventive knowledge/control already existed / recurring incidents.

### 7. Doctrine Effectiveness
How often documented/encoded doctrine prevents or resolves the failure class.

### 8. Knowledge Reuse Rate
How often relevant prior experience is actually retrieved and used.

### 9. First-Pass Success
Mission succeeds without rework/retry/escalation.

### 10. Human Intervention Rate
How often a human must step into a mission.

## Organizational learning chain

For a recurring failure, inspect:

1. Did preventive knowledge exist?
2. Was it retrieved?
3. Was it delivered to the correct actor?
4. Was it understood?
5. Was the correct doctrine/action followed?
6. Did the doctrine actually work?

Failure classification:
- knowledge missing,
- retrieval failure,
- routing/communication failure,
- context compilation failure,
- execution/compliance failure,
- doctrine failure,
- structural prevention missing.

## Escalation by recurrence

Example policy:

Occurrence 2:
- retrieve prior incident,
- notify squad commander.

Occurrence 3:
- specialist reinforcement,
- mandatory root-cause analysis,
- escalate one org level.

Occurrence 4:
- doctrine review,
- Advanced Projects Command investigation.

Occurrence 5:
- war-game structural prevention,
- require validated systemic fix.

## Metric inheritance

Metrics should aggregate at every organization node.

Example:
- OAuth Squad RFR: 42%
- Authentication Company: 31%
- API Battalion: 17%
- Connector Division: 11%
- Integration Corps: 8%
- Engineering Command: 6%

This makes recurrence hotspots visible spatially.

## Suggested top-level Army Health scorecard

- Mission Success Rate
- First-Pass Success
- Recurring Failure Rate
- Preventable Recurrence Rate
- Time-to-Green
- Cost per Accepted Outcome
- Human Intervention Rate
- Rework Rate
- Knowledge Reuse Rate
- Doctrine Effectiveness
- Readiness
- Evaluation Pass Rate
- Gate Rejection Rate
- Outcome Regression Rate
