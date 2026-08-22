# Build GTA Mission Narrator Mode for Agent Factory

You are working inside my existing **Agent Factory / Terminal Configuration** project.

Your task is to implement a **GTA: San Andreas-inspired mission narration system** for the optional `gta` UI mode.

This is **not** a replacement for the current terminal/instrument UI.

The existing UI must remain intact.

The product must support:

```text
Mode:
├── Instrument
└── GTA
```

Switching modes must change only:

- presentation
- terminology
- animation
- sounds
- narrator presentation
- character presentation

It must **never** change:

- underlying state
- counts
- verdicts
- measurements
- agent results
- gate results
- epistemic labels
- readiness
- workflow execution

---

# 1. Core experience

I want GTA mode to feel like a **San Andreas mission control center for AI agents**.

Think:

- mission intros
- crew portraits
- radio chatter
- safehouse UI
- wanted-level / heat visualization
- mission cards
- animated job transitions
- completion cinematics
- checkpoint alerts
- crew dialogue
- agent personalities
- agent portraits
- click an agent and talk to them
- mission narrator
- short audio stings
- dramatic VERIFIED completion animation

It should feel extremely animated, polished and fun while still being a serious operator interface.

The game layer is a **presentation layer over real agent-factory state**.

---

# 2. Narrator concept

Add a configurable **Mission Narrator**.

Do NOT hard-code the narrator directly into workflow logic.

Architecture:

```text
Canonical Factory Event
        ↓
Narration Event Adapter
        ↓
Narration Script Generator
        ↓
Voice Provider
        ↓
Audio Manager
        ↓
UI subtitle + audio + animation
```

Create an abstraction such as:

```text
NarratorProvider
```

with providers such as:

```text
none
browser-tts
local-tts
external-tts
prototype-voice
```

The frontend and workflow engine must not care which provider is active.

This lets us later plug in an appropriately licensed voice without redesigning the application.

---

# 3. Narrator personality

Create an **original mission narrator character** inspired by the tone and pacing of a 1990s West Coast crime-game mission announcer.

Do not copy dialogue from GTA or reproduce copyrighted character dialogue.

Do not impersonate or identify the narrator as CJ.

The narrator should be:

- relaxed
- streetwise
- funny
- concise
- slightly sarcastic
- confident
- observant
- useful rather than distracting

Most lines should be approximately 3–12 seconds.

The narrator should understand the Agent Factory terminology.

Example style:

```text
Crew says they're finished.

Fixer's still checking the work.
```

Or:

```text
Implementation crew cleared the checkpoint.

Reviewer is moving in.
```

Or:

```text
Hold up.

We got four ghosts on the board.
```

Or after genuine verified completion:

```text
That's clean.

Job verified.

Payday.
```

Generate your own original dialogue variants.

---

# 4. VERY IMPORTANT: completion integrity

The narrator must NEVER celebrate because an agent says:

```text
completed
done
finished
success
```

Agent self-reporting is not sufficient.

Completion narration must only occur after the existing authoritative completion path succeeds.

We already have:

```text
factory/finish.py
```

The **PAYDAY / MISSION PASSED** event must be emitted only after the real completion assertions succeed.

Conceptually:

```text
Agent reports completion
        ↓
NO CELEBRATION
        ↓
finish()
        ↓
clean tree ✓
unique commits ✓
ledger entry ✓
required verification ✓
        ↓
VERIFIED_COMPLETION
        ↓
animation
subtitle
audio sting
narrator
```

Never connect completion audio directly to agent output.

This is a critical safety requirement.

---

# 5. Canonical narration events

Create typed events rather than random strings.

Suggested events:

```text
MISSION_STARTED
MISSION_ACCEPTED

CREW_DISPATCHED
CREW_MEMBER_STARTED
CREW_IDLE
CREW_BLOCKED

INTENT_DECLARED

CHECKPOINT_APPROACHING
CHECKPOINT_PASSED
CHECKPOINT_REFUSED

HUMAN_REQUIRED

REVIEW_STARTED
REVIEW_FAILED
REVIEW_PASSED

GHOST_DETECTED

NO_SIGNAL

OUT_OF_GAS

VERIFIED_COMPLETION
PAYDAY

MISSION_ABORTED
MISSION_FAILED
```

Each event should have structured metadata.

Example:

```json
{
  "event": "CHECKPOINT_REFUSED",
  "crew": "implementation",
  "checkpoint": "tests",
  "reason": "3 tests failed",
  "basis": "MEASURED",
  "timestamp": "..."
}
```

Narration should be generated from event data.

---

# 6. Preserve epistemic labels

These labels MUST remain exactly:

```text
MEASURED
DERIVED
ASSUMED
PROXY
```

Do not GTA-reskin them.

They represent epistemic meaning rather than presentation terminology.

Also:

```text
UNMEASURABLE
```

must remain semantically distinct from:

```text
FAIL
```

GTA mode may display:

```text
NO SIGNAL
```

as presentation text, but the underlying state must still be `UNMEASURABLE`.

---

# 7. Agent conversations

Crew members should be clickable.

Clicking an agent opens a communication panel.

Show:

```text
Portrait
Name
Role
State
Current job
Current checkpoint
Current intent
Turf/claim held
Recent radio messages
```

Then provide a text box:

```text
Talk to crew member...
```

For the real tracker, route communication through the existing:

```text
factory/bus.py
```

and, where supported:

```text
SendMessage
```

For static prototypes, simulate the conversation.

---

# 8. Show intent BEFORE action

This is one of the most important features.

Before an agent performs a meaningful action, surface its intent.

Example:

```text
IMPLEMENTER

NEXT MOVE

Modify:
connectors/hubspot/auth.py

Reason:
OAuth refresh handling does not retry expired tokens.

Expected impact:
Restore failed connector authentication.

[Allow]
[Stop]
[Inspect]
```

The UI should make it easy for an operator to see:

> What is this agent about to do?

before it happens.

Do not hide this in logs.

---

# 9. Narration UI

Whenever narration occurs, display subtitles even if audio is disabled.

Example:

```text
┌────────────────────────────────────┐
│ RADIO — DISPATCHER                 │
│                                    │
│ “Fixer's checking the work.        │
│ Nobody gets paid yet.”             │
└────────────────────────────────────┘
```

Possible presentation:

- animated radio waveform
- portrait
- subtitle
- typewriter reveal
- speaker indicator
- small radio-channel identifier

Keep narration short.

Do not block the user interface while narration is playing.

---

# 10. Audio controls

Audio must be:

```text
OFF by default
```

Add settings:

```text
Narrator
[ Off / On ]

Mission Stings
[ Off / On ]

Volume
[──────────]

Voice
[ Mission Dispatcher ▼ ]
```

Persist these settings in the existing design-system/settings system.

Do not create another settings subsystem.

---

# 11. Sound only on state changes

Do NOT play a sound every time the UI rerenders.

Create a proper audio event manager.

Sounds should fire only when state transitions occur.

Suggested sounds:

```text
mission-start
checkpoint-passed
checkpoint-refused
human-required
crew-blocked
ghost-detected
verified-payday
```

Add rate limiting.

Multiple rapid events should not create an audio pile-up.

Implement:

- queueing
- deduplication
- cooldown
- priority
- interrupt rules

Critical alerts can interrupt low-priority ambience.

---

# 12. VERIFIED completion cinematic

When — and only when — `VERIFIED_COMPLETION` occurs, GTA mode should run a short cinematic.

Example sequence:

```text
workflow reaches VERIFIED_COMPLETION
        ↓
background dims slightly
        ↓
crew cards settle
        ↓
large center typography
        ↓
JOB VERIFIED
        ↓
smaller:
PAYDAY
        ↓
completion sting
        ↓
narrator line
        ↓
summary card
```

Summary could show:

```text
JOB VERIFIED

Implementation Crew
✓ 12 tests passed
✓ Review passed
✓ Ledger recorded
✓ Clean worktree

Duration: unavailable

PAYDAY
```

IMPORTANT:

If duration/tokens/cost are not instrumented, show:

```text
NO SIGNAL
```

or omit the metric.

Never invent a number.

---

# 13. Current ground truth

The interface must be capable of truthfully rendering:

```text
Readiness:
9 / 30

Gate events ever refused:
0 / 22

Runs finishing with no human:
3 / 14

Ghost runs:
4

Maximum concurrent crews:
3

Fuel instrumentation:
UNMEASURABLE
```

Do not create a fuel gauge containing made-up data.

If fuel is uninstrumented, GTA mode might render:

```text
FUEL
NO SIGNAL
```

rather than a percentage.

---

# 14. Heat / wanted-level visualization

We may map failing readiness gates to a GTA-style 5-star heat display.

However this MUST NOT destroy information.

Example:

```text
HEAT
★★★★☆
```

Clicking the stars must open the real gate list:

```text
READINESS — 9 / 30

✓ Gate A
✓ Gate B
✕ Gate C
? Gate D — UNMEASURABLE
...
```

The stars are a summary visualization only.

The real 30-gate data remains authoritative.

If you cannot design this without hiding information, do not use the stars.

---

# 15. Terminology mapping

Create ONE centralized mapping module.

Example:

```js
const TERMINOLOGY = {
  instrument: {
    lane: "Lane",
    agent: "Agent Session",
    task: "Task",
    gate: "Gate",
    ledger: "Findings Ledger",
    claim: "Claim",
    bus: "Bus",
    finish: "Finish",
    conductor: "Conductor",
    readiness: "Readiness",
    worktree: "Worktree",
    evaluator: "Evaluator",
    reviewer: "Independent Reviewer"
  },

  gta: {
    lane: "Crew",
    agent: "Crew Member",
    task: "Job",
    gate: "Checkpoint",
    ledger: "Intel",
    claim: "Turf",
    bus: "Radio",
    finish: "Payday",
    conductor: "Safehouse",
    readiness: "Stats",
    worktree: "Garage Bay",
    evaluator: "The Fixer",
    reviewer: "The Lookout"
  }
};
```

Do not scatter GTA terminology throughout HTML.

Both modes consume this module.

---

# 16. One state model, two views

There must be ONE canonical state model.

Conceptually:

```text
FactoryState
       ↓
┌──────────────┬──────────────┐
│ Instrument UI│ GTA UI       │
└──────────────┴──────────────┘
```

Never create:

```text
InstrumentState
GTAState
```

The skin cannot own business truth.

---

# 17. Mode-switch invariant test

Create an automated test specifically for this.

Start a workflow.

Capture canonical assertions.

Example:

```json
{
  "readiness": [9, 30],
  "ghosts": 4,
  "state": "running",
  "basis": "MEASURED",
  "checkpoint_results": [...],
  "active_crews": 3
}
```

Switch:

```text
Instrument → GTA
```

Capture the same assertions again.

Diff them.

Expected:

```text
NO DIFFERENCE
```

Then switch:

```text
GTA → Instrument
```

and repeat.

Only presentation-specific values may change.

---

# 18. Accessibility

GTA mode must remain usable with:

```text
prefers-reduced-motion
```

Reduced motion should substitute:

```text
large movement → fade
camera movement → static emphasis
continuous animation → state indicator
flashing → icon + label
```

Also ensure:

- full keyboard navigation
- visible focus indicators
- subtitles for every narrator line
- audio never carries unique information
- colour never carries unique information
- state includes text/icon/shape
- screen-reader labels
- high contrast
- no seizure-risk flashing

---

# 19. Progressive enhancement

The system should still communicate useful information if JavaScript fails.

Important workflow truth should exist in readable markup where practical.

The GTA layer is enhancement.

It must not be the sole mechanism for communicating workflow status.

---

# 20. Animation philosophy

The brief is:

> Extremely animated.

But animation should communicate something.

Use animation for:

```text
state transition
agent movement
handoff
job progression
checkpoint progression
message transmission
verification
failure
human intervention
crew contention
completion
```

Avoid meaningless constant movement.

One ambient decorative effect is acceptable.

Everything else should correspond to system state.

---

# 21. Visual direction

Aim for:

```text
1990s West Coast
San Andreas mission screen
CRT
spray-paint accents
street map
radio scanner
safehouse
mission dossier
crew portraits
wanted-level HUD
garage/workshop
neon night city
```

But maintain modern enterprise usability.

Do not reproduce copyrighted GTA logos, artwork, character assets, voice clips or game files.

Create original assets inspired by the aesthetic.

---

# 22. Performance prerequisite

Before adding heavy animation to the real tracker, inspect its server architecture.

Current known issue:

```text
socketserver.TCPServer
~19 second page loads
~30 probes per load
concurrent requests can return empty
```

Do not hide this with animation.

Investigate and propose/fix:

- threaded or async request handling
- decoupling expensive probes from page requests
- background state collection
- cached snapshots
- event-driven state updates
- SSE/WebSocket updates where appropriate
- TTLs
- probe concurrency
- stale-data indicators

The UI should render cached/current state immediately and receive updates asynchronously.

---

# 23. Prototype location

Start by examining:

```text
docs/artifacts/orchestration-bench.html
```

It already contains useful concepts such as:

- state machine
- inspector
- configuration rail
- basis chips
- design tokens
- rendering tests

Prototype the GTA mode seam there first if appropriate.

Then port the validated design into the real tracker/orchestrator.

Do not duplicate logic unnecessarily.

---

# 24. Browser verification

Use Playwright.

Do not consider the implementation complete based on source inspection.

Test:

```text
desktop
smaller desktop
mode switching
agent selection
agent conversation panel
reduced motion
audio off
audio on
keyboard navigation
heat expansion
UNMEASURABLE rendering
verified completion
failed completion
```

Take screenshots.

Actually inspect the rendered output.

Watch particularly for CSS selectors unintentionally affecting nested elements.

We have previously had selectors such as:

```css
.claim span {
  display: block;
}
```

incorrectly alter unrelated nested components.

Scope selectors carefully.

---

# 25. Behaviour tests, not text coincidence

Avoid tests such as:

```text
expect(page.textContent()).toContain("lanes win")
```

if that text could appear in an explanatory paragraph.

Test actual state or DOM semantics.

Prefer:

```text
data-state
data-basis
aria attributes
structured event state
canonical state snapshot
```

Tests should prove behaviour, not accidental text matches.

---

# 26. Build phases

Implement in this order.

## Phase 1 — Mode seam

Build:

- `instrument | gta`
- dropdown
- persisted setting
- terminology module
- shared state model
- invariant test

Stop and verify before proceeding.

---

## Phase 2 — Crew UI

Build:

- crew cards
- portraits
- roles
- jobs
- state
- turf
- clickable agents
- character personality
- idle behavior

---

## Phase 3 — Communication

Build:

- agent conversation pane
- radio messages
- intent-before-action
- SendMessage/bus integration where possible

---

## Phase 4 — Narration + audio

Build:

- NarratorProvider
- event → narration adapter
- subtitles
- audio manager
- rate limiting
- mute/default-off
- mission stings
- verified-completion narration

---

## Phase 5 — Animation

Only after everything above works:

- mission intros
- crew transitions
- handoff animation
- checkpoint transitions
- radio animation
- ghost alerts
- completion cinematic
- heat visualization
- tasteful ambient layer

---

# 27. Deliverables

I want you to:

1. Inspect the existing repo before making architectural decisions.

2. Identify the existing state model, settings system, event bus and completion pathway.

3. Produce a concise implementation plan.

4. Implement Phase 1 first.

5. Verify it.

6. Then continue through the remaining phases where practical.

7. Reuse existing components instead of building parallel systems.

8. Add automated tests.

9. Run Playwright.

10. Capture screenshots.

11. Report anything that is still simulated rather than connected to production state.

12. Explicitly state whether the finished UI has been visually inspected by a human or only by automated browser tooling.

---

# 28. Final quality bar

The finished system should feel like:

> **GTA: San Andreas mission control crossed with an AI agent command center.**

But underneath the game presentation it must remain stricter than the original UI about truth.

The coolest possible failure mode is NOT:

```text
MISSION FAILED
```

The coolest possible failure mode is:

```text
NO SIGNAL

We don't have an instrument for this yet.
```

That philosophy should run through the entire implementation.

Build spectacle around **truth**, not instead of it.