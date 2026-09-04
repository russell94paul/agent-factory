# Switchboard P0 Functional Spec

## Reuse, do not replace

The live P1 already has:

- NOW-first layout;
- CREATE WORK;
- START SYNCED for READY work;
- APPROVE/REJECT POST controls;
- Inspector;
- evidence references;
- mission DAG disclosure;
- per-work autonomy selector `MANUAL/GUARDED/AUTO`;
- pause/resume autonomy UI;
- priority bands with reasons.

P0 adds only the seams required for mission execution.

## Create screen additions

Add above/around the current generic work fields:

1. **Mission preset**
   - Marketing Model
   - Sales Model
   - Generic Work (existing flow)

2. **Execution preset / team**
   - show only compatible presets;
   - show model/tool/budget summary if already available;
   - do not invent a new team registry if `presets.py`/blueprints already provide the data.

3. **Autonomy**
   - MANUAL
   - GUARDED
   - AUTO

4. **Target/deadline** (optional)
   - scheduler context only;
   - not part of GreenContract.

On submit, a mission preset expands to canonical work in the existing TaskStore.

## Mission/run controls

```text
[ RUN DAG ] [ RUN CRITICAL PATH ] [ PAUSE ] [ RESUME ]
```

Display:

- target milestone;
- READY count;
- RUNNING count;
- WAITING GATE count;
- blocked reason(s);
- current run mode;
- concurrency usage;
- next eligible work and why.

## Auto continuation

When an active run exists:

- completion event -> recompute -> start newly eligible policy-allowed work;
- APPROVE/REJECT -> recompute -> start newly eligible policy-allowed work;
- pause -> no new starts;
- resume -> recompute;
- failure -> block dependents unless policy explicitly classifies retryable.

## Artifact surface

A completed target should make the artifact/evidence references obvious without inlining private evidence bodies.

Minimum:

- artifact name/type/path/reference;
- validation state;
- evidence refs;
- run/session id;
- limitations/unmeasured.

## Do not add tonight

- drag-and-drop graph editor;
- arbitrary org designer;
- organization marketplace;
- simulation controls;
- world map;
- gamification;
- full historical analytics dashboard.
