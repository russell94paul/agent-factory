# Mission Readiness + READY-UP

## Core distinction

Do not collapse these into one score:

- **Capability** — ability to perform a type of work.
- **Health** — current operational condition.
- **Availability** — can accept work now.
- **Mission Readiness** — suitability for this mission now.
- **Deployability** — readiness plus policy/security/permissions.
- **Fitness** — measured performance after the mission.

An agent may have excellent general health but poor readiness for a specific Azure authentication incident.

## Agent Health Vector candidate

- reasoning health;
- instruction adherence;
- calibration;
- context health;
- context freshness;
- context saturation;
- memory health;
- knowledge freshness;
- tool availability;
- tool reliability;
- integration health;
- model reliability;
- communication health;
- workload health;
- budget health;
- security health;
- recent eval health.

## Mission Requirement Vector

A mission can compile to weighted requirements such as:

- Python;
- Azure;
- OAuth;
- SQL;
- debugging;
- repository familiarity;
- incident response;
- risk tolerance;
- verification depth;
- required tools;
- required permissions;
- time constraint;
- budget constraint.

## Initial readiness model

A simple first-pass model:

R = weighted_sum(capability_i * health_i * freshness_i) - penalties

Penalties may include:

- missing permission;
- broken tool;
- severe skill gap;
- stale context;
- unresolved security issue;
- context saturation;
- insufficient budget;
- unreliable dependency.

Do not assume a linear weighted formula is optimal. Research learned models and calibrated probability-of-success approaches.

## READY-UP

READY-UP is a pre-deployment conditioning optimizer.

Inputs:
- mission requirement vector;
- agent/team capability profile;
- current health;
- time to deployment;
- cost budget;
- risk constraints;
- security policy.

Candidate interventions:
- load skill capsule;
- retrieve similar historical missions;
- retrieve recent failures/incidents;
- refresh documentation;
- refresh repository topology;
- prefetch dependencies;
- warm tool connections;
- verify credentials;
- switch model;
- change reasoning budget;
- increase verification;
- add specialist;
- add reviewer;
- alter topology;
- alter communication cadence;
- reduce autonomy;
- run micro-eval.

Optimization target:

> Maximize expected mission success/readiness subject to time, cost, security and risk constraints.

## Example

Current:
- readiness: 0.72
- required: 0.87
- deployment in: 12 minutes
- budget: $2

Candidate actions:

| Intervention | Time | Cost | Expected Δ Readiness |
|---|---:|---:|---:|
| Azure skill capsule | 40 sec | .10 | +.08 |
| Retrieve prior incidents | 25 sec | .08 | +.05 |
| Repository topology refresh | 60 sec | .12 | +.03 |
| Add Azure specialist | 20 sec | .60 | +.12 |
| Full re-eval | 18 min | 4.00 | +.17 |

The optimizer should choose the best feasible combination.

## UI idea

Mission card:

- recommended agent/team;
- base fit;
- current health;
- mission readiness;
- readiness threshold;
- identified gaps;
- recommended READY-UP actions;
- projected readiness;
- projected cost/time;
- deployability;
- remaining warnings.

Primary action:

**READY-UP & DEPLOY**
