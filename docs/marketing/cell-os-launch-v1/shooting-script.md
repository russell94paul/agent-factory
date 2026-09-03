# CELL OS — shooting script

**90.0 s · 31 shots · 24 fps · 3840×2160 · master 16:9**

Timings are authoritative to ±0.2 s. **VO in-points are fixed; cuts flex to them.**

> **`SILENT` convention:** a shot marked `SILENT` means *no new narration line begins in it*. The
> tail of the preceding line may resolve into it — and in three places it deliberately does, so the
> line's last word lands on the cut. Marked where it matters.

---

## The look bible

Pin these once. Every shot obeys them; a shot that needs an exception says so in its NOTE field.

### Palette

| Token | Hex | Reserved for |
|---|---|---|
| `void` | `#05070B` | background. Never pure black except shots 1 and 31 |
| `graphite` | `#0E131B` | surfaces, panels, the kernel plane |
| `edge` | `#1B2430` | hairlines, grid, inactive structure |
| `blue` | `#1E5FCC` | **structure** — boundaries, planes, architecture. The load-bearing colour |
| `cyan` | `#38D2E8` | **activity** — live pathways, the primary Cell, anything moving now |
| `violet` | `#7B5CFF` | ⚠ **the counterfactual, and nothing else.** Shadow twin and evolution chamber only. Using it elsewhere breaks the film's only colour-coded argument |
| `amber` | `#E8A33D` | ⚠ **the human, and refusal.** Two uses, both meaning "a person must decide". Never decorative, never a button |
| `bone` | `#E6ECF2` | display type |
| `slate` | `#8A97A8` | label type, chips, mono |

One warm value in the entire film. When amber appears at 0:53 it should feel like the first warm
thing in ninety seconds, because it is.

### Type

| Tier | Family | Weight | Tracking | Case |
|---|---|---|---|---|
| `[DISPLAY]` | Neue Haas Grotesk Display / Söhne · fallback Inter Tight | 500 | −1.5% | UPPER |
| `[LABEL]` | same | 450 | +8% | UPPER |
| `[MONO]` | Berkeley Mono / JetBrains Mono | 400 | +2% | as written |
| `[BODY]` | same as display | 400 | 0 | sentence |

Only `[DISPLAY]` and `[LABEL]` animate. `[MONO]` types or cuts — it never eases, because real
terminals do not ease.

### Camera and optics

- 35 mm for spatial architecture · 50 mm for object beats · 85 mm for the single human shot (20).
- Permitted moves: slow push, lateral parallax, orbit ≤ 12°/s, pull-back.
- ⛔ Forbidden: whip pan, handheld shake, dutch tilt, snap zoom, rack focus as punctuation.
- Max camera velocity 0.6 scene-units/s. Every move eases in and out — nothing starts at speed.
- Depth of field shallow at 50/85 mm, near-deep at 35 mm. Bokeh circular, not hexagonal.

### Grade and grain

`grain 2.0%` (fine, static-free) · `bloom threshold 0.82, radius 0.6` · `chromatic aberration 0.15 px,
edges only` · `black point lifted to 4/255` — never crushed, the depth lives in the shadows ·
`highlight rolloff soft`. Shots 21–23 graded **+1/3 stop** (see `claim-ledger.md` §2 — the film gets
visibly more solid as it moves from designed to measured).

### Persistent overlays

1. **Maturity chip** — lower-left, 11 px `[MONO]`, 42% opacity, rising to 70% for 0.4 s on change.
   `● DESIGNED` / `● IMPLEMENTED` / `● VALIDATED`. Present from shot 9 to shot 28. Absent in the
   cold open and the creed. Sourced from `claim-ledger.md`.
2. **Kernel plane** — introduced in shot 10 and never removed until shot 28: a graphite plane at the
   scene's base carrying eight `[LABEL]`s at 22% opacity —
   `CELL KERNEL · CELL IMAGES · OPERATIVE THREADS · CONTEXT MEMORY · CAPABILITY SYSCALLS · HYPERMESH · EVIDENCE LEDGER · MISSION SCHEDULER`.
   ⭐ **This is where the brief's 8-label subsystem roll went.** As a dedicated 3.5 s beat it violated
   the density ceiling by 4.6× (`timing.md` §4) and read as a word list. As permanent set dressing it
   is legible across sixty seconds, costs zero runtime, and makes every later shot feel like it is
   happening *inside* an operating system.

---

## A — COLD OPEN · 0:00.0–0:06.2

```
SHOT 1              IN 0:00.0   OUT 0:02.6   DUR 2.6s
BEAT     Cold open
FRAME    Pure black. At 0:00.9 a single point ignites at frame centre — 3 px core,
         cyan, with a 40 px falloff. Nothing else. No grid, no horizon.
TEXT     none
CAMERA   35mm, static, then a 0.2-unit push beginning 0:01.8 (imperceptible, felt)
MOTION   Point opacity 0 → 1 over 700ms, cubic-out. Falloff breathes ±6% at 0.4 Hz.
VO       SILENT
SOUND    SUB.PULSE  (38–55 Hz sine, 1400ms, no attack transient)
CLAIM    none
BUILD    VECTOR
NOTE     Resist adding anything. The 2.6s of near-nothing is what makes shot 5 land.
```

```
SHOT 2              IN 0:02.6   OUT 0:04.8   DUR 2.2s
BEAT     Cold open
FRAME    The point holds at 30% frame height. Below it, one line of display type.
TEXT     [DISPLAY]  THE AI INDUSTRY BUILT AGENTS.
CAMERA   static
MOTION   Type strikes in per-word, 3 words at 90ms intervals, opacity + 4 px rise,
         cubic-out. No blur, no scale.
VO       L01 @ 0:02.9  "AI gave us agents."                                  (4w)
SOUND    room tone enters, −38 dB
BUILD    VECTOR
NOTE     Past tense on screen, past tense in the read. The film's premise is that this
         sentence is already history.
```

```
SHOT 3              IN 0:04.8   OUT 0:06.2   DUR 1.4s
BEAT     Cold open
FRAME    Three small nodes at the triangle points around the centre point, connected by
         1 px `edge` lines. They contract inward and merge.
TEXT     [LABEL] MODEL · [LABEL] PROMPT · [LABEL] TOOLS  →  [MONO] AGENT
CAMERA   static, 50mm
MOTION   Nodes travel inward over 600ms, expo-in. On contact the three labels
         cross-dissolve to `AGENT` in mono. Total 1.0s, then 0.4s hold.
VO       SILENT
SOUND    AGENT.TICK ×3, one per node arrival (dry digital transient, 2–4 kHz, 60ms)
CLAIM    C1 — definitional
BUILD    VECTOR
NOTE     `AGENT` is mono and small. Every later unit label is display and larger. The type
         hierarchy is carrying the argument about scale.
```

## B — THE FRACTURE · 0:06.2–0:08.4

```
SHOT 4              IN 0:06.2   OUT 0:08.4   DUR 2.2s
BEAT     Fracture
FRAME    The frame's implied edges crack outward. What was the whole image is revealed as
         one illuminated cell in a vast dark lattice extending past frame in all axes.
         `AGENT` is now one node among ~400, and is the only lit one.
CAMERA   35mm. Rapid pull-back, 0.9 units over 1.4s, expo-out — the film's fastest move
         and the only one that exceeds 0.6 u/s. Licensed exception.
MOTION   Lattice draws from centre outward, 1 px `edge` lines, 55% coverage by 0:07.6.
         Do not fill it — the emptiness is the point.
VO       L02 @ 0:06.4  "But an agent is only one intelligent process."       (8w)
         tail resolves into shot 5
SOUND    SUB.PULSE drops out on the cut. 300ms of near-silence, then music enters
         at 0:07.2 — sub-bass + a slow four-note arpeggio, ~62 BPM
BUILD    PLATE+VECTOR — generated volumetric depth, vector lattice composited
NOTE     The one shot in the film permitted to feel abrupt.
```

## C — THE NAME · 0:08.4–0:18.6

```
SHOT 5              IN 0:08.4   OUT 0:11.0   DUR 2.6s
BEAT     The name
FRAME    Push back in to the single lit node. Eight thin rings accrete around it in
         sequence, each carrying one label on its circumference.
TEXT     [LABEL] IDENTITY · MEMORY · CAPABILITIES · PERMISSIONS · CONTEXT · TOOLS ·
         EVIDENCE · BUDGET
CAMERA   50mm, slow push 0.3 units, orbit 8° left
MOTION   Rings arrive at 240ms intervals, each scaling 1.15 → 1.0 with a 120ms overshoot
         settle. Labels fade in 60ms after their ring lands. STACKING, not replacing —
         all eight are on screen and legible by 0:10.6.
VO       L03 @ 0:10.6  "An Operative is an agent with identity, memory,
                        capability and limits."                             (11w)
SOUND    UI.LABEL ×8, near-silent ticks 5–7 kHz, 18ms, descending in level
CLAIM    C1 — VISION (definitional). Chip not yet on screen.
BUILD    VECTOR
NOTE     Eight labels in 2.2s only works because they stack. If any label leaves before
         0:11.0 the shot is unreadable. See `timing.md` §4.
```

```
SHOT 6              IN 0:11.0   OUT 0:14.0   DUR 3.0s
BEAT     The name
FRAME    The ringed object holds. The mono `AGENT` label beneath it dissolves and is
         replaced by display type at 2.4× the size.
TEXT     [MONO] AGENT  →  [DISPLAY] AI OPERATIVE
CAMERA   50mm, continue orbit, now 5°/s
MOTION   `AGENT` opacity → 0 over 200ms. 180ms of no label at all. Then `AI OPERATIVE`
         strikes in, letter-spacing animating from +14% to −1.5% over 500ms, cubic-out.
VO       (L03 continues, out 0:15.2)
SOUND    a single low harmonic swell, 90 Hz, 900ms
CLAIM    C1
BUILD    VECTOR
NOTE     The 180ms with no label is the most important frame-level decision in the beat.
         The unit is renamed, not relabelled — there must be a gap.
```

```
SHOT 7              IN 0:14.0   OUT 0:17.2   DUR 3.2s
BEAT     The name
FRAME    Pull back. Five more Operatives fade up around the first. They move into a
         deliberate formation — not a circle, an asymmetric working arrangement with two
         forward, one central, two lateral. A luminous `blue` boundary closes around them.
TEXT     [DISPLAY] OPERATIVE CELL   (arrives 0:16.1, lower third)
CAMERA   35mm, pull back 0.7 units, easing to rest by 0:16.4
MOTION   Operatives fade up 0:14.2–0:14.9. Formation travel 1.1s, cubic-in-out. Boundary
         draws as a closing arc, 640ms, then a single 8% pulse outward.
VO       L04 @ 0:15.6  "A Cell is Operatives, assembled for one mission."    (8w)
SOUND    CELL.BOOT — deep harmonic expansion, 80 Hz → 3 kHz, 2200ms, the film's
         first genuinely full sound
CLAIM    C2 — ⚠ VISION. `Mission Assembly Plan` is Specified only; no mission object
         exists. Definitional phrasing only.
BUILD    VECTOR + generated volumetric light inside the boundary
NOTE     The formation must look *designed*, not organic. No swarming, no flocking, no
         orbiting. These are workers in positions.
```

```
SHOT 8              IN 0:17.2   OUT 0:18.6   DUR 1.4s
BEAT     The name
FRAME    Everything recedes to 18% opacity and defocuses. Title card, centred.
TEXT     [DISPLAY] CELL OS
         [BODY]    Operating System for Operative Cells
CAMERA   locked. Zero movement — the only fully static frame between shots 1 and 29.
MOTION   Wordmark opacity 0 → 1 over 260ms, cubic-out, no travel. Subtitle 140ms later.
         Then absolute stillness for 900ms.
VO       SILENT — but L04's final word "mission" lands at 0:17.2, on the cut.
         ⭐ The wordmark strikes on the last syllable. This is the sync of the film.
SOUND    CELL.BOOT resolves. Music sustains a single note. No new cue.
CLAIM    C3 — VISION
BUILD    VECTOR
NOTE     1.4s feels long in the edit and is correct. Do not trim it. If the wordmark and
         the last syllable are more than 2 frames apart, re-cut to the audio.
```

## D — THE FRAME · 0:18.6–0:24.6

```
SHOT 9              IN 0:18.6   OUT 0:21.2   DUR 2.6s
BEAT     The frame
FRAME    Four stacked horizontal planes in `edge`, receding in z, labelled bottom-up.
         Cold, diagrammatic, deliberately unglamorous.
TEXT     [LABEL] HARDWARE / OPERATING SYSTEM / PROCESSES / APPLICATIONS
CHIP     ● DESIGNED  — first appearance, lower-left
CAMERA   35mm, slight lateral parallax left→right, 0.25 units
MOTION   Planes draw bottom-up, 160ms apart. Labels arrive with their plane. Stacked.
VO       L05 @ 0:19.2  "An operating system manages processes and permissions."  (7w)
SOUND    UI.LABEL ×4
CLAIM    none — this is the known world
BUILD    VECTOR
NOTE     This shot should be the plainest in the film. It is the "before" and it must
         look like a textbook so that shot 10 looks like a proposal.
```

```
SHOT 10             IN 0:21.2   OUT 0:24.6   DUR 3.4s
BEAT     The frame
FRAME    The four planes morph in place — same geometry, new labels, and the second plane
         thickens and lights `blue` to become the kernel plane that persists for the rest
         of the film.
TEXT     [LABEL] MODELS + COMPUTE / CELL OS / OPERATIVE CELLS / SYNTHETIC ORGANIZATIONS
         then, at 22% opacity across the kernel plane, the eight subsystem labels
         (see look bible → persistent overlays)
CAMERA   35mm, continue parallax, then a 0.3-unit push toward the CELL OS plane
MOTION   Labels cross-fade in place, 120ms, staggered 90ms bottom-up. Plane 2 thickens
         over 700ms and its light ramps 0 → 100% over 900ms. The eight subsystem labels
         fade to 22% between 0:23.1 and 0:24.4, staggered 90ms, and STAY.
VO       L06 @ 0:22.6  "CELL OS is built for organizations."                 (6w)
SOUND    a low structural "settle" — 60 Hz thump with a 400ms tail
CLAIM    C3 — VISION. *"is built for"* is the permitted phrasing; never *"manages"*.
BUILD    VECTOR
NOTE     Same geometry, different labels. The morph, not a cut, is the whole argument:
         this is the same kind of object, one layer up.
```

## E — REEL 1 · COMPILE A CELL · 0:24.6–0:33.8

```
SHOT 11             IN 0:24.6   OUT 0:27.2   DUR 2.6s
BEAT     Reel 1
FRAME    CELL Studio. A single transparent panel floating in the graphite environment,
         one input field, everything else empty. Restraint is the design statement — no
         sidebars, no toolbars, no fake menus.
TEXT     [MONO] mission ▸ Launch a new digital product.
CHIP     ● DESIGNED
CAMERA   50mm, static with a 0.15-unit drift
MOTION   The mission text types at 22 chars/s with a 1-frame block caret. No easing —
         mono does not ease. Caret blinks at 1.6 Hz after the last character.
VO       L07 @ 0:25.4  "Describe the objective."                             (3w)
SOUND    key transients, dry, 8 per second, −28 dB, no two identical
BUILD    VECTOR
NOTE     ⛔ No hand, no cursor arrow, no mouse. The operator is present only as typing.
```

```
SHOT 12             IN 0:27.2   OUT 0:31.0   DUR 3.8s
BEAT     Reel 1
FRAME    Below the input, a vertical compilation chain assembles downward — eight stages,
         each a thin panel with a 1 px connector to the next.
TEXT     [MONO] MISSION INTENT ↓ MISSION CONTRACT ↓ CAPABILITY REQUIREMENTS ↓
         OPERATIVE SELECTION ↓ TEAM TOPOLOGY ↓ ORG-IR ↓ CELL IMAGE ↓ BOOT
CHIP     ● DESIGNED   ⚠ Org-IR is the corpus's most contested category (CN-01)
CAMERA   50mm, slow downward tilt tracking the chain, 0.4 units
MOTION   Stages arrive 380ms apart, each 90ms opacity + 6 px rise. STACKING — all eight
         visible and legible from 0:30.1. Connector lines draw 1 px, 140ms, cyan.
VO       SILENT — ⭐ enforced. 8 labels + narration in 3.8s is unreadable
         (`timing.md` §4). The chain is the sentence.
SOUND    SYSCALL.ROUTE ×8, precise routed clicks, 45ms, pitched down 40 cents per stage
BUILD    VECTOR
NOTE     This is the film's densest legitimate figure and it works only because it stacks
         and nobody is talking. Cutting to a wide before 0:30.1 destroys it.
```

```
SHOT 13             IN 0:31.0   OUT 0:33.8   DUR 2.8s
BEAT     Reel 1
FRAME    `BOOT` flares. The chain collapses upward into a Cell boundary and six Operatives
         resolve inside it, each labelled.
TEXT     [LABEL] RESEARCH · STRATEGY · PRODUCT · ENGINEERING · MARKETING · REVIEW
CHIP     ● DESIGNED
CAMERA   35mm, pull back 0.5 units as the Cell forms
MOTION   Chain collapse 420ms, expo-in. Boundary draws 500ms. Operatives resolve from
         0:32.0, 110ms apart, with their labels. Settle by 0:33.2.
VO       L08 @ 0:31.2  "CELL OS is designed to compile intent into an
                        organization."                                       (10w)
SOUND    CELL.BOOT, 2200ms, one octave above shot 7's
CLAIM    C4 — VISION ⚠ contested. *"is designed to compile"*. ⛔ Never *"compiles"*.
BUILD    VECTOR + generated interior light
NOTE     Six roles, six labels, 1.2s. Legible because they arrive with the object rather
         than as a list.
```

## F — REEL 2 · ELASTIC ORGANIZATIONS · 0:33.8–0:41.0

```
SHOT 14             IN 0:33.8   OUT 0:37.0   DUR 3.2s
BEAT     Reel 2
FRAME    The Cell reduces to a single Operative. Then it divides into a parallel research
         row of four. Then the row reorganises into a specialist build formation of three
         with different node geometry.
TEXT     [LABEL] ONE OPERATIVE → PARALLEL RESEARCH → SPECIALIST BUILD
         (each replaces the last, lower third, 1.0s apiece)
CHIP     ● DESIGNED
CAMERA   35mm, orbit 10°/s right — the film's most kinetic sustained move
MOTION   Each topology change is a physical rearrangement, 520ms, cubic-in-out, with
         nodes travelling along visible paths. ⛔ No cross-dissolves between formations.
         The shapes must be seen to *move*.
VO       L09 @ 0:35.6  "Teams don't have to stay static."                    (6w)
SOUND    a soft mechanical re-seat per change — 3 events, 180ms, 200–900 Hz
CLAIM    C5 — VISION. ⚠ See ledger: the one multi-agent formation this estate built was
         **rejected on evidence**. Nothing may imply a working formation.
BUILD    VECTOR
NOTE     This is the "make it visually dramatic" beat. Drama comes from the travel paths,
         not from speed or glow.
```

```
SHOT 15             IN 0:37.0   OUT 0:41.0   DUR 4.0s
BEAT     Reel 2
FRAME    Build formation → builder + verifier pair (two nodes, asymmetric, a hard
         bidirectional link) → a shadow review layer fades up *above* the pair in violet
         → everything collapses back to one Operative.
TEXT     [LABEL] BUILDER + VERIFIER → SHADOW REVIEW
         [DISPLAY] ELASTIC ORGANIZATIONS   (arrives 0:39.6)
CHIP     ● DESIGNED
CAMERA   35mm, orbit decelerating to rest, then a 0.3-unit push on the collapse
MOTION   Pair forms 480ms. Shadow layer fades up 0:38.4, violet, 30% opacity, offset
         +0.4 units in z. Collapse 0:39.9–0:40.6, expo-in, nodes converging to one.
         `ELASTIC ORGANIZATIONS` strikes over the collapse.
VO       L10 @ 0:38.2  "Cells can expand under uncertainty, and collapse
                        when it changes."                                    (10w)
SOUND    FORK.SPLIT (first, quiet use — stereo split, 700ms) on the shadow layer;
         a descending harmonic on the collapse
CLAIM    C5 — VISION. *"can expand"*, *"can collapse"* — modal, per ledger.
BUILD    VECTOR
NOTE     ⭐ First appearance of violet. It means counterfactual here and it means
         counterfactual at 1:08. Nowhere else.
```

## G — REEL 3 · CONTEXT AS VIRTUAL MEMORY · 0:41.0–0:48.2

```
SHOT 16             IN 0:41.0   OUT 0:44.4   DUR 3.4s
BEAT     Reel 3
FRAME    Push through the boundary into a single Operative. Its active context is a small
         luminous cyan ring, deliberately *small*. Beyond it, filling the entire volume
         to the frame edges and past them, a vast blue knowledge mesh.
TEXT     [DISPLAY] HYPERMESH   (arrives 0:43.0, small, upper left, not centred)
         [LABEL] research · previous missions · customer knowledge · code · evidence ·
                 doctrine · documents   (at 26% opacity, distributed in the mesh depth)
CHIP     ● DESIGNED   ⚠ the corpus's single most contested concept (CN-03)
CAMERA   50mm push through, then 35mm as the volume opens. Continuous, no cut.
MOTION   The ring holds steady. The mesh parallaxes at three depths at 0.7 / 0.4 / 0.15
         relative rates. Labels surface and sink continuously — never all legible at once.
VO       L11 @ 0:42.9  "Context is designed to work like virtual memory."    (8w)
SOUND    MESH.SWEEP begins — filtered noise sweep 400 Hz → 8 kHz, 900ms, wide stereo
CLAIM    C6 — VISION ⚠ contested. ⛔ Never *"treats"*, *"mounts"*, *"streams"*.
BUILD    PLATE+VECTOR — generated volumetric mesh, vector ring and labels
NOTE     ⭐ The ratio is the argument: the ring must be visually ~1/400th of the mesh.
         If the ring looks big the shot says the opposite of the line.
```

```
SHOT 17             IN 0:44.4   OUT 0:48.2   DUR 3.8s
BEAT     Reel 3
FRAME    A five-stage pipeline resolves between the mesh and the ring. Selected knowledge
         travels it as discrete packets — countable, not a stream. The ring fills to ~60%
         and stops. It does not fill completely.
TEXT     [LABEL] RETRIEVE → AUTHORIZE → RANK → COMPRESS → MOUNT
CHIP     ● DESIGNED
CAMERA   50mm, slow lateral track along the pipeline, 0.4 units
MOTION   Stages arrive 300ms apart, stacking. Packets: exactly 11, visibly individual,
         travelling 900ms each, staggered. AUTHORIZE rejects 2 of them — they dim to
         `edge` and fall away. ⭐ The rejection is the shot's most valuable 200ms.
VO       L12 @ 0:46.7  "Each Operative mounts only what the objective needs."  (8w)
SOUND    MESH.SWEEP resolves; SYSCALL.ROUTE ×5 for the stages; a muted low tick for
         each of the 2 rejections
CLAIM    C6 — VISION
BUILD    VECTOR
NOTE     The ring stopping at 60% and the two rejected packets are what make this a
         mechanism instead of a light show. Neither is optional.
```

## H — REEL 4 · BOUNDED AUTONOMY · 0:48.2–0:56.8

```
SHOT 18             IN 0:48.2   OUT 0:50.8   DUR 2.6s
BEAT     Reel 4
FRAME    An Operative emits a call. It travels as a discrete mono-labelled token toward a
         luminous blue boundary that reads as *thick* — a wall, not a line.
TEXT     [MONO] production.deploy()
         [DISPLAY] CELL KERNEL   (on the boundary, 0:49.6)
CHIP     ● IMPLEMENTED  — chip changes here. 30 readiness gates exist
                          (`factory.readiness.GATES`); `tasks.py:163` raises
                          `EvidenceRequired`
CAMERA   50mm, tracking the token, slight lead
MOTION   Token travels 1.6s, constant velocity — no easing. Deliberate, procedural.
         The boundary brightens 20% as it approaches.
VO       L13 @ 0:50.2  "Autonomy is not authority."                          (4w)
SOUND    SYSCALL.ROUTE, then a rising 90 Hz tension pad under the travel
CLAIM    C7 — MIXED
BUILD    VECTOR
NOTE     Constant velocity, not eased. This is a request being processed, not a
         creature approaching.
```

```
SHOT 19             IN 0:50.8   OUT 0:54.6   DUR 3.8s
BEAT     Reel 4
FRAME    The token halts at the boundary. Six check rows resolve to its left, each
         evaluating in sequence. Five tick cyan. The sixth marks amber ✕.
TEXT     [MONO] IDENTITY ✓ / CAPABILITY ✓ / BUDGET ✓ / POLICY ✓ / EVIDENCE ✓ /
                HUMAN AUTHORITY ✕
         [DISPLAY] AUTHORIZATION REQUIRED   (0:53.6, amber)
CHIP     ● IMPLEMENTED  ⚠ NOTE: `factory/preflight.py` is WARN-ONLY — it refuses
                          nothing. See ledger C7. The film shows the designed gate.
CAMERA   50mm, locked. Stillness is the point — the system has stopped.
MOTION   Rows resolve 380ms apart. Each ✓ is a 90ms cyan flash settling to 70%.
         The ✕ takes 520ms — slower than the passes — and the token visibly stops
         rather than fading. `AUTHORIZATION REQUIRED` strikes with no travel.
VO       L14 @ 0:52.4  "Important actions can pass permissions, budget, policy,
                        evidence, and a human."                              (11w)
SOUND    EVIDENCE.LOCK ×5 (glass/metal, 220ms) for the passes;
         KERNEL.DENY on the ✕ — muted low pulse, 60–90 Hz, 500ms, ⛔ NO reverb tail.
         Music ducks 4 dB on the deny and holds there.
CLAIM    C7, C8
BUILD    VECTOR
NOTE     ⭐ The refusal must feel like *competence*, not failure. Amber, not red. The
         five passes are fast and the one stop is slow — that asymmetry is the design.
```

```
SHOT 20             IN 0:54.6   OUT 0:56.8   DUR 2.2s
BEAT     Reel 4
FRAME    Cut to the film's only human presence: a hand, 85 mm, shallow, in near-darkness,
         lit only by the amber of the surface it touches. No face. No body. No office.
         Then cut back — the boundary opens and the token passes through.
TEXT     [MONO] AUTHORIZED   (0:55.9, brief, small)
CAMERA   85mm on the hand, 1.2s. Then 50mm on the boundary.
MOTION   The hand contact is a single unhurried press — no tap, no swipe. Boundary
         aperture opens 340ms; token resumes at its original constant velocity.
VO       SILENT (L14's tail resolves to 0:57.0 across this cut)
SOUND    a single warm low tone on contact — the only warm sound in the film.
         Then SYSCALL.ROUTE, then EVIDENCE.LOCK as it passes.
CLAIM    C8 — VISION
BUILD    PLATE (shot or generated) + VECTOR composite
NOTE     The brief permits brief stock-office imagery. Don't use it. A hand and amber
         light in the dark is stronger and cheaper than any office.
```

## I — REEL 5 · THE VERDICT ⭐ · 0:56.8–1:08.4

> ⭐ **This is the anchor of the film.** It is the only reel whose subject is built, tested,
> validated and standards-grounded (`factory/contract.py`, `factory/evidence.py`,
> `current_vs_proposed.md:57`). It gets the most screen time of any reel, the +1/3 stop grade, and
> the film's only full musical resolution. See `claim-ledger.md` §3.

```
SHOT 21             IN 0:56.8   OUT 0:59.6   DUR 2.8s
BEAT     Reel 5
FRAME    An Operative emits a mono token. It travels toward the ledger surface — and is
         held. It does not pass, and it does not shatter. It simply is not accepted.
TEXT     [MONO] TASK COMPLETE
         [DISPLAY] A CLAIM IS NOT AN OUTCOME   (0:58.4)
CHIP     ● VALIDATED  — chip changes. Grade +1/3 stop from this shot.
CAMERA   50mm, static
MOTION   Token travels 900ms then stops dead — 0 frames of deceleration. Holds, inert,
         for 700ms. `A CLAIM IS NOT AN OUTCOME` strikes beneath it.
VO       L15 @ 0:57.6  "A claim of completion is not an outcome."      (8w) ⭐
SOUND    the token's travel tone simply *ceases*. 400ms of no sound at all — the
         longest silence since the cold open.
CLAIM    C9 — **MEASURED.** Present indicative permitted. `tasks.py:163` raises
         `EvidenceRequired`.
BUILD    VECTOR
NOTE     ⛔ Do not explode, reject, or red-flag the token. The system is unimpressed,
         not alarmed. Inertness is the performance.
```

```
SHOT 22             IN 0:59.6   OUT 1:02.8   DUR 3.2s
BEAT     Reel 5
FRAME    A 4 × 3 grid resolves: four evidence classes down, three states across. Cells
         populate as evidence arrives from off-frame — six labelled artefacts flying in
         and locking into rows.
TEXT     [LABEL] rows: TARGET · CONSUMER · REGRESSION · ROLLBACK
         [LABEL] cols: SATISFIED · ASSERTED · ABSENT
         [MONO] arriving: TEST · DIFF · ARTIFACT · DEPLOYMENT · EVALUATION · APPROVAL
         [DISPLAY] EVIDENCE LEDGER   (1:01.9)
CHIP     ● VALIDATED
CAMERA   35mm, very slow push, 0.2 units
MOTION   Grid draws 400ms. Artefacts arrive 0:60.3–1:01.6, 220ms apart, each locking into
         a cell with a 60ms scale overshoot. ⭐ One row resolves to `ASSERTED`, not
         `SATISFIED` — visibly weaker than its neighbours, and left that way.
VO       SILENT (L15's tail resolves to 1:00.9)
SOUND    EVIDENCE.LOCK ×6 — short glass/metal locks, 220ms, ascending in pitch;
         the `ASSERTED` row's lock is duller and lower
BUILD    VECTOR
CLAIM    C9 — MEASURED. Exact vocabulary from `factory/evidence.py:48,68-70`.
NOTE     ⭐ The one `ASSERTED` row is the most credible frame in the entire film. A launch
         video that shows its own grid incomplete is making a claim nobody can fake.
```

```
SHOT 23             IN 1:02.8   OUT 1:08.4   DUR 5.6s
BEAT     Reel 5 — the anchor
FRAME    The grid recedes. Five verdicts draw as a vertical monotone lattice, ordered,
         each connected to the next. Then four of them dim to 30% and one remains lit.
TEXT     [MONO]  NOT_RUN  <  PASS  <  UNMEASURABLE  <  FAIL  <  ERROR
         [DISPLAY] UNMEASURABLE   (1:05.4, centred, alone)
         [LABEL]  ISO/IEC 9646 · TTCN-3 · ITU-T Z.140 §24.2   (1:06.8, 30% opacity,
                  lower right, small)
CHIP     ● VALIDATED
CAMERA   35mm, static until 1:06.2, then a 0.25-unit push onto UNMEASURABLE
MOTION   Lattice draws bottom-up 1:02.8–1:03.5, 140ms per verdict, connectors 1 px.
         Held. At 1:05.0 four verdicts dim over 500ms; UNMEASURABLE brightens to 100%
         and its display-type restatement fades up beneath it.
VO       SILENT 1:02.8–1:03.5 — the lattice draws in silence.
         L16 @ 1:03.6  "A check whose instrument could not run
                        has not passed."                              (10w) ⭐⭐
         out 1:07.8. Then 0.6s of hold on UNMEASURABLE, silent.
SOUND    VERDICT.RESOLVE at 1:03.5 — restrained harmonic resolution, a perfect fifth,
         1800ms. ⭐ The film's only full musical resolution. Music then reduces to a
         single sustained note.
CLAIM    C10 — **MEASURED.** `factory/contract.py:31-37`. Present indicative permitted.
         The ISO/TTCN-3 attribution is real and load-bearing — this is not our invention,
         and saying so is what makes it credible.
BUILD    VECTOR
NOTE     ⭐⭐ The most important shot in the film. Every competitor can claim
         orchestration. None ships a verdict meaning *"the thing that was supposed to
         measure this could not see."* Give it the full 5.6s. If the film must lose
         four seconds, take them from shots 24, 26 and 27 — never from here.
         ⛔ The word UNMEASURABLE is never spoken. It is only ever read.
```

## J — REEL 6 · FORK AND EVOLVE · 1:08.4–1:15.6

```
SHOT 24             IN 1:08.4   OUT 1:12.0   DUR 3.6s
BEAT     Reel 6
FRAME    Open on 0.4s of near-black. A running Cell resolves, then freezes — every node
         and pathway stops mid-motion. It splits laterally into two complete Cells that
         separate in z: cyan left, violet right. They begin executing *differently* —
         visibly different internal topologies and pathway activity.
TEXT     [MONO] fork()   (1:09.2)
         [LABEL] PRIMARY CELL / SHADOW CELL   (1:10.4)
CHIP     ● DESIGNED  — chip reverts. ⚠ Grade returns to base.
CAMERA   35mm, static during the freeze, then a slow lateral drift revealing the z gap
MOTION   Freeze is absolute — 0 motion for 320ms, including the camera. Split travels
         620ms, cubic-out, with a visible 0.6-unit z separation. Divergent activity
         begins immediately and never re-syncs.
VO       L17 @ 1:08.9  "Fork a Cell. Challenge it with a shadow twin."       (9w)
SOUND    FORK.SPLIT — mono collapsing to hard L/R, 700ms. ⭐ On headphones this should
         be the film's most physical moment.
CLAIM    C13 — VISION. ⚠ Not `assertions.py`'s `Counterfactual`, which is a documentation
         object with no `status` field. The corpus forbids conflating them.
BUILD    VECTOR
NOTE     The two Cells must run *different* strategies, not mirrored ones. Mirroring says
         "copy"; divergence says "counterfactual".
```

```
SHOT 25             IN 1:12.0   OUT 1:15.6   DUR 3.6s
BEAT     Reel 6
FRAME    Pull back into a large volume — the evolution chamber. Five distinct formations
         occupy it, each a different topology. A five-axis surface plots them.
TEXT     [DISPLAY] EVOLUTION CHAMBER   (1:12.4)
         [LABEL] SOLO EXPERT · SPECIALIST PIPELINE · PARALLEL SWARM · COMMAND TREE ·
                 HYBRID CELL
         [LABEL] axes: SUCCESS · COST · TIME · EVIDENCE · REWORK
CHIP     ● DESIGNED  — ⚠ gated: refused by the same unlock as the optimizer
CAMERA   35mm, sustained pull-back 1.1 units, orbit 6°/s
MOTION   Formations fade up 180ms apart. The surface draws as a wireframe over 900ms,
         with the five formations as points on it, violet for the shadow lineage.
         A frontier edge highlights, then holds.
VO       L18 @ 1:13.1  "Team design becomes something you can measure."      (7w)
SOUND    a wide, quiet harmonic bed; UI.LABEL ×5 for the formations
CLAIM    C14 — VISION, deliberately gated.
BUILD    PLATE+VECTOR
NOTE     ⛔ **No axis carries a number and no formation carries a score.** Per ledger C14:
         there is no measurement, so there is no scale. Shape and relative position only.
         A single fabricated "94%" here would invalidate the whole film.
```

## K — SCALE-OUT · 1:15.6–1:22.6

```
SHOT 26             IN 1:15.6   OUT 1:18.6   DUR 3.0s
BEAT     Scale-out
FRAME    Hard pull-back. The chamber becomes one node among seven functional Cells
         arranged across a wide mesh, each labelled, each with visibly different internal
         density. Structured signal traffic runs between them along the mesh.
TEXT     [LABEL] RESEARCH · PRODUCT · ENGINEERING · CONTENT · CUSTOMER · OPERATIONS ·
                 RELIABILITY
         [MONO] cellbus ▸ signal   (small, on two of the pathways)
CHIP     ● DESIGNED
CAMERA   35mm, the film's largest move — 2.4 units back over 3.0s, easing to rest
MOTION   Cells resolve 140ms apart. Traffic: discrete signals, not flows — countable
         packets on ~9 routes. One Cell (OPERATIONS) sits marginally forward in z and
         its routes touch all six others.
VO       L19 @ 1:16.5  "One Cell, one mission. Many Cells, one function."    (8w)
SOUND    music re-enters at full width; a low swell rising with the pull-back
CLAIM    C15 — VISION. ⛔ Never *"operates"*, *"runs"*, *"coordinates"*.
BUILD    PLATE+VECTOR
NOTE     Discrete countable signals, not glowing flows. The difference between a systems
         diagram and a screensaver is whether you could count the traffic.
```

```
SHOT 27             IN 1:18.6   OUT 1:20.6   DUR 2.0s
BEAT     Scale-out
FRAME    Montage. Six mission strings type and compile into six visibly different
         formations. 0.33s each. Cut on the compile, never on the result.
TEXT     [MONO] "Research a new market." / "Build the application." /
                "Operate customer support." / "Create a content campaign." /
                "Monitor production." / "Investigate a failure."
CHIP     ● DESIGNED
CAMERA   locked per beat, six hard cuts. No movement — the cuts carry the rhythm.
MOTION   Each: text present on frame 1, formation resolves over 220ms, hold 110ms, cut.
VO       SILENT
SOUND    SYSCALL.ROUTE ×6, one per cut, ascending
CLAIM    C16 — VISION. ⛔ **No checkmarks, no durations, no costs, no results.** These are
         objectives being *compiled*, never missions being *completed*. `backlog.yaml`
         holds 31 candidate missions and nothing has been dispatched.
BUILD    VECTOR
NOTE     Six formations must be *distinguishable at 0.33s*. If two look alike, cut one and
         give the time to the other five.
```

```
SHOT 28             IN 1:20.6   OUT 1:22.6   DUR 2.0s
BEAT     Scale-out
FRAME    Widest frame in the film. Hundreds of Cells and pathways across the full volume,
         the kernel plane visible far below, the HyperMESH visible far behind. Depth in
         four distinct layers. Still legible as *structure*, never as noise.
TEXT     none. The chip fades out at 1:22.0 and does not return.
CAMERA   35mm, continued slow pull-back, coming to complete rest at 1:22.4
MOTION   Global parallax at four depths. Activity everywhere but nothing hurried.
VO       L20 @ 1:20.3  "Connect them, and one operator could direct a
                        synthetic organization."                             (10w)
                        out 1:24.5
SOUND    full bed, widest stereo image of the film
CLAIM    C15 — VISION. ⭐ *"could direct"* — the modal is audible and it is what makes
         the sentence true. See ledger C15.
BUILD    PLATE+VECTOR — generated volumetric depth is essential here
NOTE     ⛔ Legibility over density. If the wide reads as abstract texture rather than as
         an organisation, reduce the count until structure returns.
```

## L — THE CREED · 1:22.6–1:30.0

```
SHOT 29             IN 1:22.6   OUT 1:25.4   DUR 2.8s
BEAT     Creed
FRAME    The volume falls away to `void`. Two lines, centred, stacking.
TEXT     [DISPLAY] THE MODEL IS NOT THE SYSTEM.
         [DISPLAY] THE AGENT IS NOT THE ORGANIZATION.
CAMERA   locked, zero movement, and it stays locked to the end of the film
MOTION   Line 1 strikes 1:22.9, 240ms opacity, no travel. Line 2 strikes 1:23.9 and
         line 1 REMAINS. Stacking.
VO       SILENT — and it stays silent for the remaining 7.4s.
SOUND    ⭐ **Music drops out at 1:22.6.** Room tone only, −40 dB. The single most
         reliable move in a launch film, and the script has been building 90 seconds
         of density specifically to spend it here.
BUILD    VECTOR
NOTE     L20's tail resolves at 1:24.5, over line 2. That is the last human sound.
```

```
SHOT 30             IN 1:25.4   OUT 1:28.0   DUR 2.6s
BEAT     Creed
FRAME    The two lines dim to 20%. One line arrives beneath them at full weight. Then a
         seven-line mono block accretes to its right.
TEXT     [DISPLAY] THE CELL IS THE NEW UNIT OF INTELLIGENT WORK.   (1:25.6)
         [MONO] BUILD CELLS. / BOOT MISSIONS. / MOUNT KNOWLEDGE. /
                ALLOCATE CAPABILITIES. / PROVE OUTCOMES. / FORK POSSIBILITIES. /
                EVOLVE ORGANIZATIONS.                              (1:26.4 →, 0.20s apart)
CAMERA   locked
MOTION   Display line 300ms. Then seven mono lines at 200ms intervals — each strikes and
         STAYS, building a legible block by 1:27.7. ⭐ Sequential replacement here is
         unreadable (`timing.md` §4); accretion is not.
VO       SILENT
SOUND    one dry mono tick per creed line, 14ms, −34 dB, ascending. Nothing else.
BUILD    VECTOR
NOTE     Seven lines in 1.4s reads as one object, not as seven readings. Do not stagger
         them further; do not dissolve any of them out.
```

```
SHOT 31             IN 1:28.0   OUT 1:30.0   DUR 2.0s
BEAT     Creed
FRAME    Everything clears. Wordmark, centred. Tagline beneath. Then, at 1:29.0, two
         final lines replace the tagline in place.
TEXT     [DISPLAY] CELL OS
         [BODY]    Compile intelligence into organizations.   (1:28.3 → 1:29.0)
         [DISPLAY] DON'T JUST PROMPT AN AGENT.                 (1:29.0)
         [DISPLAY] ENGINEER THE ORGANIZATION.                  (1:29.3)
CAMERA   locked
MOTION   Wordmark 260ms, no travel. Tagline 140ms later. At 1:29.0 the tagline
         cross-dissolves (180ms) to the two closing lines, which stack.
         Full fade to black 1:29.7 → 1:30.0.
VO       SILENT
SOUND    OS.SIGNATURE — deep cinematic signature tone, 3200ms, beginning at 1:28.0 and
         resolving *into* the black. The last 300ms of the film is sound over black.
BUILD    VECTOR
NOTE     ⚠ Four text elements in 2.0s is the film's tightest card and the one place the
         90 s cut shows strain. If it does not read in the previz, take 0.6s from shot 27
         (montage, 6 → 5 missions) and give it here. Do NOT take it from shot 23.
```

---

## Build split summary

| Build | Shots | Count |
|---|---|---|
| **VECTOR** (AE / WebGL / SVG) | 1, 2, 3, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 17, 18, 19, 21, 22, 23, 24, 27, 29, 30, 31 | **25** |
| **PLATE+VECTOR** | 4, 16, 20, 25, 26, 28 | **6** |
| **PLATE only** | — (the hand in shot 20 is a plate inside a composite) | 0 |

⭐ **25 of 31 shots are vector.** That is the correct ratio for this film and it is deliberate: every
frame carrying the product's name, labels, architecture or verdicts is built in a tool that renders
type correctly. Generative video is used only for volumetric depth, atmosphere and light — the six
`PLATE+VECTOR` shots — where a diffusion model's weakness (it cannot spell) never appears.

⛔ **Do not send shots 12, 19, 22, 23 or 30 to a generative video model under any circumstances.**
They are 100% typography and their legibility *is* the shot.
