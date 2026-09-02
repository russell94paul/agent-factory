# Missions, Campaigns & Gamification

## Campaign
A larger outcome containing multiple operations.

Example:

```text
CAMPAIGN THUNDER ROAD
Goal: migrate all legacy connectors
Operations: 18
Task forces: 5
Success: 11/18 GREEN
```

## Operation
The world projection of a mission.

```text
OPERATION IRON GATE
Objective: Restore vendor API ingestion
Commander's Intent: Restore service without weakening auth controls
Theatre: Integration
Priority: Front Line
Formation: Spearhead
Intelligence: 82%
Supply: 100%
Readiness: GREEN
```

## Objectives
- Primary Objective
- Secondary Objective
- Optional Objective
- Abort / safety criteria

## Known Threats
Recurring failure families can be represented as known threats.

Example:

```text
KNOWN THREAT AUTH-004
OAuth Credential Failure
Encounters: 4
Previous fixes: 3
Successful permanent fixes: 0
Status: RECURRING
```

## Escalation by recurrence

- 1st occurrence → classify + learn
- 2nd → retrieve prior incident + notify commander
- 3rd → specialist reinforcement + RCA
- 4th → doctrine review + Advanced Projects Command
- 5th → War Game / structural prevention experiment

## Completion
Operation completion can trigger:

- AAR
- learning extraction
- doctrine candidate creation
- rank / experience updates
- campaign progress
- environmental celebration

Gamification should reward **verified outcomes and useful learning**, not message volume, token usage or raw activity.
