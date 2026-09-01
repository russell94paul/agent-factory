# Client Review UI — v1

## Modes

Support two presentation modes if achievable without destabilizing the implementation.

### Standard

Normal interactive Client Review workspace.

### Live Meeting

Optimized for presenting to a client on a shared screen.

Live Meeting mode should:

- increase information hierarchy;
- hide internal navigation/noise;
- emphasize major outcomes;
- make evidence easy to open;
- emphasize client decisions;
- minimize editable/admin controls;
- avoid exposing internal-only information.

## Recommended layout

### Header

```text
CLIENT / PROJECT

Overall Status       Review Readiness       Decisions
On Track             Ready for Review       1 Required

Last updated: ...
```

### Hero — Since Your Last Review

Example:

```text
7 meaningful changes

✓ Connector implementation completed
✓ Authentication validated
✓ Fresh data landing verified
✓ Regression suite passing

1 decision requires your input
```

This should immediately communicate progress.

## Main navigation

Recommended sections:

```text
OVERVIEW
DELIVERED
EVIDENCE
DECISIONS
RISKS
NEXT
```

Avoid overwhelming the client with Agent Factory's internal complexity.

## Review narrative

The interface should naturally support the presenter telling the story:

```text
1. Here's what you asked us to achieve.

2. Here's what we completed.

3. Here's the evidence that it works.

4. Here's the one thing we need from you.

5. Here's what happens next.
```

That story is more important than showing every internal system capability.

## Evidence interaction

Clicking a delivered outcome should reveal its proof.

Example:

```text
Fresh landing verified ✓

Evidence

✓ Prefect execution successful
✓ Rows landed
✓ Expected schema verified
✓ Freshness check passed
✓ Parity within accepted tolerance

[View technical details]
```

## Decision interaction

Decision cards should be extremely simple.

Example:

```text
DECISION REQUIRED

Production refresh schedule

Recommended
● Daily at 06:00

Alternative
○ Every 4 hours

Impact:
No impact on current delivery date.

[Approve Recommended]
```

## Visual direction

The UI may remain visually distinctive and aligned with Agent Factory / Zeus branding, but meeting usability has priority.

Use animation primarily for:

- state transitions;
- progress;
- highlighting newly completed work;
- opening evidence;
- meaningful pipeline events.

Avoid continuous decorative motion that distracts during conversation.

## Safe demo behavior

The live meeting view must degrade gracefully.

If live integrations are unavailable, stale or uncertain:

- clearly show the last verified state;
- never fabricate live status;
- preserve the last known evidence;
- make refresh failures non-destructive to the presentation.

The presenter should never be left with an empty screen because one backend service is unavailable.
