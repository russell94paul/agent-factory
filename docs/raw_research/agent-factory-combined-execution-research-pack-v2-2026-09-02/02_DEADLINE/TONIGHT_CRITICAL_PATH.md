# Deadline Critical Path

## Goal

By 12:00 Pacific, demonstrate:

> **Switchboard → create/select Marketing mission → select execution preset/team → launch → observe state → auto-advance safe nodes → human gate if needed → inspect evidence/artifacts → meeting-ready deliverable.**

The already-validated Marketing artifact is the safety net and must remain independently launchable.

## Parallel lanes

```text
LANE A — DELIVERY SAFETY                LANE B — MISSION/RUNTIME
revalidate existing meeting artifact    inspect current start/create routes
preserve known-good launch path          build thin preset -> TaskStore adapter
               |                                      |
               |                                      v
               |                          LANE C — SWITCHBOARD UI
               |                          preset/team + run controls
               |                                      |
               |                                      v
               |                          LANE D — AUTONOMY PUMP
               |                          RUN DAG / critical / auto resume
               |                                      |
               +----------------------+---------------+
                                      v
                         INTEGRATION / FRESH MARKETING RUN
                                      |
                                      v
                           VERIFY + MEETING ARTIFACT
                                      |
                              [HUMAN DELIVERY GATE]

LANE E — SALES PATCH (parallel, bounded, no dependency on Switchboard until Marketing is proven)
```

## Gate sequence

### Gate 0 — State re-measured

Pass only when Claude has inspected the live checkout rather than assuming the review pack equals current HEAD.

Must report:

- branch/HEAD;
- dirty/untracked paths;
- active worktrees/sessions/claims;
- current test baseline;
- whether `factory/switchboard_p1.py`, the create/start/resolve routes, autonomy fields and guarded-start mechanism are present in the live checkout;
- exact current known-good Marketing artifact launch command/path.

### Gate 1 — Meeting artifact protected

Before platform edits, confirm the known-good Marketing artifact can still be generated/opened from its existing path. If it cannot, restore this before doing Switchboard work.

### Gate 2 — Mission preset adapter works without UI

A deterministic invocation creates the Marketing run's canonical work and dependency edges using the existing TaskStore/event model.

No generic Org-IR. No second task ledger.

### Gate 3 — Switchboard creates Marketing mission

P1 CREATE can select:

- mission preset: Marketing Model;
- compatible execution/team preset;
- autonomy: Manual / Guarded / Auto;
- optional deadline/target;
- visibility.

Created work appears through the normal canonical work projection.

### Gate 4 — RUN DAG works

A POST/command starts eligible work through the existing start/guard mechanism.

Acceptance:

- no direct bypass of readiness;
- max concurrency enforced;
- conflicts/claims respected;
- Manual work not auto-started;
- Guarded work starts only when `guarded_start_allowed` is true;
- paused run does not advance.

### Gate 5 — approval resumes

When a node is waiting on a human hold, downstream work does not start. After APPROVE/REJECT records the decision, an active autonomous run recomputes and starts newly eligible nodes without a second manual start command.

### Gate 6 — fresh Marketing vertical slice

Run from Switchboard. At least one stage must invoke an actual agent with `dry_run=False` **if the live repo can do so without violating existing safety/refusal rules**.

If live execution is blocked by a measured infrastructure defect, record the exact blocker and use the fallback path; do not weaken the control to manufacture a PASS.

### Gate 7 — output verified

The result must expose:

- final deliverable/artifact reference;
- task states;
- evidence references;
- any unmeasured/unsupported claims;
- run/session provenance.

### Gate 8 — Sales patch

Complete bounded Sales changes. Only integrate a Sales mission preset into Switchboard if doing so cannot jeopardize Marketing delivery.

## Stop-loss rule

If any new implementation starts threatening Gate 1 or Gate 7, revert to the known-good Marketing launch path and present the already-validated artifact. A platform milestone is not allowed to turn a client-ready delivery into a missed meeting.
