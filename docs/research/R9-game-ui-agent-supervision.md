# R9 — A game-styled supervision UI for autonomous agents: does the skin help or hurt?

**Status: NOT DISPATCHED.** Written 2026-08-22. Paste the whole file. The answer lands beside it as
`docs/research/answers/R9-answer-game-ui-agent-supervision.md`.

Read `R8-data-engineering-agent-factory.md` §2.6 first — this is the split-out of that strand, and
R8 explicitly invited the split. R8 asks what the factory should *be*; this asks what the operator
should *see* when several autonomous agents are working at once.

---

## 0. The proposal, stated plainly so you can disagree with it

We run 3 concurrent AI agents and want to run more. Today they appear as terminal panes: one per
agent, coloured, titled, with a bell and taskbar flash when one needs a human. Honest, and it is a
terminal multiplexer.

The proposal is a **second presentation mode** — selectable from a dropdown, the existing
instrument panel never removed — modelled on an open-world game HUD:

- agents as **characters** you click to select and talk to, with visible state and idle behaviour
- a **wanted level** encoding failing gates (20 of 30 failing → high heat)
- jobs as **missions**, with a briefing before dispatch and a completion sting
- a **theme tune / audio cue on job completion**
- heavy, deliberate animation throughout

**The question is not "can this be built".** It obviously can. The question is whether it makes an
operator *more accurate and faster* at supervising N agents, or whether it makes them slower and
more confident — which is the worst combination and would kill the idea.

---

## 1. What we already hold ourselves to, which the skin must not break

This estate's recurring defect is a surface that reports success while measuring nothing: a gate
that reported PASS while checking nothing, a detector that silently degraded to 1 finding where the
real engine reports 313, a launcher that announced the model it was running while running another.
So a game skin arrives with three hard constraints, and **a recommendation that cannot satisfy all
three is a recommendation to not build it**:

1. **A completion sting must fire only on a *verified* completion.** Celebrating a run that
   "succeeded" over failures it could not see is exactly our `truthful` defect — 3 runs reported
   completed after 115, 21 and 15 recorded stage failures. A jingle on that is a lie with a
   soundtrack.
2. **Provenance must survive the reskin.** Every number we show carries MEASURED / DERIVED /
   ASSUMED / PROXY. If the skin drops those labels, it launders estimates into facts.
3. **State must never be carried by style alone.** Colour, animation and audio are all secondary
   channels; shape, label or position must also distinguish a state.

---

## 2. The questions

### 2.1 Does game UI actually help supervision? — the load-bearing question

Find the evidence, not the opinion.

- What does the research on **supervisory control of multiple autonomous systems** say — UAV/drone
  operator studies, industrial process control, air-traffic, RTS-game telemetry? Operator span of
  control, attention switching cost, and where accuracy collapses as N rises.
- **Does gamification improve or degrade vigilance tasks?** There is a real literature on
  gamification harming accuracy in monitoring work. Where does it help, where does it hurt?
- **Alarm fatigue.** Clinical alarm research is the mature field here. What transfers to an agent
  console, and what does it say about a completion sound that fires many times an hour?
- Is there a documented case of a **game-styled interface used for real operational work** that was
  measured rather than admired?

Answer directly: **at what N does a spatial, character-based view beat a list?** Our honest guess is
that a list wins at 3 and loses at 15, but we have no evidence for that and would rather be
corrected.

### 2.2 Character-based agent representation

- What is the state of the art for representing an **autonomous process as a character** — status,
  intent, and confidence — without implying more agency than exists?
- **Anthropomorphism risk**: does giving an agent a face and a voice make operators trust it more
  than its track record justifies? This matters commercially: our agents are wrong often enough
  that mis-calibrated trust is a real hazard.
- How should **an agent's intent be shown *before* it acts**, so an operator can intervene? This is
  the single most valuable interaction we do not have.
- Click-to-select and **talk to an agent mid-task**: what are the interaction patterns for steering
  a running autonomous process, and what does interruption cost it?

### 2.3 Audio as an information channel

- What is genuinely known about **earcons / auditory icons** in operations? What can audio encode
  that visuals cannot — and specifically, is audio good at *peripheral* awareness while attention is
  elsewhere?
- Distinguishable sound design for: job complete · gate refused · agent blocked on a human · budget
  exceeded. **How many distinct cues can an operator reliably tell apart?**
- Browser autoplay policy in practice, mute-by-default expectations, and the accessibility
  requirement that audio is never the only channel.
- **How quickly does a completion sting become irritating** at our event rate, and what do mature
  tools do — rate-limit, escalate, or only sound on state *changes*?

### 2.4 Animation budget

- Where does heavy animation help comprehension of a running system, and where is it just cost?
  `artifact-motion`'s position is that motion must encode reveal, magnitude, continuity or
  mechanism, and anything else is filler. Does the research agree?
- **Performance**: N animated agents plus a live event stream, in a browser, without a hot laptop.
  Canvas vs SVG vs DOM at what element counts? What do real game-like web UIs actually use?
- Reduced-motion: what is the *equivalent* experience, not the degraded one?

### 2.5 Terminology and the reskin

We intend a full vocabulary change in the game mode — lanes to crews, tasks to jobs, gates to
checkpoints, failing gates to a wanted level, the findings ledger to intel, the conductor pane to a
safehouse.

- Does a **domain metaphor** aid or impede expert operators over time? Novices often gain and
  experts often lose; is that supported?
- **Dual-vocabulary risk**: two names for one thing across two modes. Is that a known cost — and how
  do systems that ship "simple/advanced" modes handle the mapping without splitting the team's
  language? We need to be able to say a sentence in a standup that means the same thing in both.
- Is **wanted-level-as-failing-gates** good information design? It maps a real 0–30 measurement onto
  a familiar 0–5 scale, which is either an excellent encoding or a lossy one that hides which gates.

### 2.6 Reference implementations to study

Read the source or the postmortem, not the trailer:

- Game HUDs whose job is genuinely dense state: RTS command interfaces, Factorio/Satisfactory
  production overlays, EVE Online's industry and fleet UI, flight-sim and DCS instrument panels.
- Ops tools with deliberate personality: anything from the observability space that took a stylistic
  swing and either kept it or reverted it — **and why they reverted, if they did**.
- Agent-supervision products shipping now: what does their multi-agent view actually look like, and
  what did they abandon?
- Web tech for animated, clickable, character-driven scenes that stay accessible.

---

## 3. Constraints any recommendation must respect

- **The instrument panel is never removed.** Game mode is a selectable presentation over the same
  state, chosen from a dropdown. Both modes read the same simulation model; neither gets its own
  private truth.
- **Self-contained artifact target**: one HTML file, strict CSP, no external hosts except Google
  Fonts, assets inlined as data URIs, ≤16MB. That is a hard budget for audio and sprites — say what
  fits.
- Must degrade: `prefers-reduced-motion`, JS disabled, audio blocked or muted, keyboard-only.
- Windows + Chrome primary.

## 4. What a good answer looks like

- **Opinionated, and willing to say don't build it.** If the evidence says a game skin degrades
  supervision accuracy, say so — we will build the dropdown anyway for demos, but we will know what
  it costs and will not put it in front of an operator making a decision.
- **Sourced and tiered**: `OBSERVED` (you read it or ran it) · `REPORTED` (paper or postmortem) ·
  `MARKETED` (vendor claim, unconfirmed) · `INFERRED`. **A MARKETED claim may not be a design premise.**
- **Costed** in build effort and in asset budget against the 16MB ceiling.
- Concrete: a recommended HUD layout, a sound set, an animation budget, and a terminology mapping —
  or a reasoned refusal of each.

## 5. Deliverable shape

1. The answer to §2.1 first: does this help, at what N, and with what caveat.
2. Character representation and the anthropomorphism/trust finding.
3. Audio: what to encode, how many cues, rate-limiting.
4. Animation budget and rendering technology.
5. Terminology: recommended mapping, or a case against the metaphor.
6. A layout proposal.
7. What you would refuse, and the measurement that would change your mind.

## 6. Out of scope

The underlying simulation model, the agent architecture, and anything about how agents are built —
that is R8. This is entirely about the surface a human looks at.
