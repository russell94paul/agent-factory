# CELL OS — generative video prompts

**6 of 31 shots only.** Everything else is vector — see `shooting-script.md` → build split.

⛔ **The rule that makes this package usable: never ask a diffusion model to render text.** It arrives
misspelled, warped, or invented, and the film's entire subject is precise vocabulary. Every frame
carrying the product name, a label, a diagram, a verdict, or a number is built in After Effects,
WebGL or SVG. Generative video contributes exactly one thing here — **volumetric depth, atmosphere
and light** — and it is genuinely better than CG at that.

⛔ **Do not send shots 12, 19, 22, 23 or 30 to any video model.** They are 100% typography and their
legibility *is* the shot.

---

## The consistency bible — prepend to every prompt

```
Style: premium dark technical interface environment. Near-black graphite void, background
#05070B, surfaces #0E131B. Deep dimensional blue #1E5FCC structural light, cyan #38D2E8
active light, restrained violet #7B5CFF accent. No warm colour anywhere except where the
prompt explicitly calls for a single amber source. Photographic, not illustrative.
Volumetric haze, soft falloff, clean specular. Fine film grain 2%. Deep blacks lifted
slightly, never crushed. Shallow depth of field with circular bokeh. Anamorphic-adjacent
but no lens flares. Feels like a real advanced software platform photographed in a dark
room, not like science fiction concept art. Extremely restrained. Nothing decorative.
```

```
NEGATIVE (append to every prompt):
text, letters, words, numbers, typography, captions, watermarks, logos, UI panels, buttons,
menus, HUD, dashboards, charts, graphs, diagrams, code, terminal windows, humans, faces,
hands, bodies, robots, humanoid figures, androids, glowing brains, neural network imagery,
DNA helices, circuit-board cliché, blueprints, lens flares, light streaks, god rays,
explosions, sparks, fire, smoke plumes, lightning, magic particles, glitter, bokeh hearts,
rainbow gradients, teal-and-orange grade, purple-pink cyberpunk, neon signs, rain-slick
streets, office interiors, desks, monitors, server rooms, data centres, cityscapes, space,
planets, nebulae, stock-footage look, motion blur streaks, camera shake, zoom bursts,
oversaturation, vignette, chromatic fringing beyond 0.2px
```

**Continuity method — reference stills, not adjectives.** Render one still per shot from the vector
build first, and pass it as the image reference. Adjectives drift between clips; a reference still
does not. Every prompt below assumes its reference still exists.

**Always request 0.5 s of handle at each end.** A 2.2 s cut is generated as a 3.2 s clip.

**Always generate at master ratio (16:9, 3840×2160 or the engine's maximum), never at the crop.**

---

## SHOT 4 — the fracture · 2.2 s cut → generate 3.2 s

```
A single point of cyan light, isolated in a vast dark volume. The camera pulls back rapidly
and smoothly, revealing that the point is one illuminated node inside an immense
three-dimensional lattice of thin dark blue structural lines extending in every direction
beyond frame. The lattice is sparse and mostly empty — dark space dominates. Only the
central node is lit; every other intersection is unlit dark blue. Volumetric haze gives
depth. The move decelerates to rest.
```
- **Camera:** rapid dolly back, ~0.9 units over 1.4 s, exponential-out. The film's only fast move.
- **Lens:** 35 mm, near-deep focus.
- **Motion:** camera only. The lattice itself does not move, pulse, or animate.
- **Handle:** 0.5 s hold at the start on the isolated point; 0.5 s at rest at the end.
- **Composite:** the vector lattice and the `AGENT` label replace the generated lattice in the final;
  the generated plate supplies volumetric depth and haze **behind** it.
- **Engine notes:** if the model fills the lattice too densely, add `sparse, mostly empty, 5% density`
  and reduce guidance. Density is the single most common failure on this shot.

---

## SHOT 16 — HyperMESH · 3.4 s cut → generate 4.4 s

```
The camera moves slowly through a boundary membrane into an immense interior volume. In the
foreground a small tight ring of cyan light, sharply in focus, occupying a very small part
of the frame. Beyond and behind it, filling the entire volume to the edges of frame and far
past them, an enormous three-dimensional mesh of deep blue interconnected nodes at many
depths, receding into haze. Three distinct depth layers parallax at different rates. The
foreground ring is tiny by comparison with the mesh — the size difference is extreme and
deliberate. Cool, vast, quiet.
```
- **Camera:** continuous push through, 50 mm narrowing to 35 mm as the volume opens. No cut.
- **Motion:** parallax only. Nodes may surface and sink very slowly. ⛔ No flowing particles, no
  travelling light along the mesh — that is added as vector in shot 17.
- **⭐ Critical:** the ring must read as roughly **1/400th** of the mesh volume. If the ring looks
  large, the shot argues the opposite of the narration. Regenerate rather than compromise.
- **Handle:** 0.5 s each end.
- **Composite:** ring, `HYPERMESH` wordmark and all seven knowledge labels are vector.
- **Engine notes:** most models make the foreground element too dominant. Prompt the ring as
  `a very small distant ring of light in the near foreground` and add scale words — `immense`,
  `cathedral-scale`, `receding for kilometres`.

---

## SHOT 20a — the human · 1.2 s cut → generate 2.2 s

```
Extreme close-up of a single human hand in near-total darkness, lit only by warm amber light
rising from the surface beneath it. The hand presses down once, slowly and deliberately —
a single unhurried contact, not a tap. Only the hand and part of the forearm are visible.
No face, no body, no room, no desk, no device. The background is pure darkness. Shallow
depth of field, 85mm. The amber light is the only warm colour in the frame.
```
- **Camera:** 85 mm, locked, shallow. Bokeh circular.
- **Motion:** one press. No second gesture, no withdrawal, no hesitation.
- **Handle:** 0.5 s before contact, 0.5 s after.
- **Negative override:** ⚠ remove `hands` and `humans` from the negative list **for this shot only**.
  Keep `faces`, `bodies`, `robots`, `androids`.
- **Engine notes:** hands are the classic diffusion failure — expect to generate 15–30 takes for one
  usable 1.2 s. **Shooting this is faster and cheaper than generating it:** one hand, one desk lamp
  with an amber gel, a black cloth, a phone camera in 4K. Recommended.
- ⛔ The brief permits brief stock-office imagery. Do not use it. A hand and amber light in the dark
  is stronger than any office, and it is the only human presence in ninety seconds — it should feel
  singular.

---

## SHOT 25 — the evolution chamber · 3.6 s cut → generate 4.6 s

```
The camera pulls back and orbits slowly through an immense dark chamber. Suspended within it,
five distinct clusters of connected nodes, each cluster a visibly different geometric
arrangement — one single bright node, one linear chain, one wide dispersed field, one
branching hierarchy, one mixed irregular form. Deep blue structural light throughout, with
one cluster lit in restrained violet. Between and beneath them, a vast faint wireframe
surface curving through the space. Cool, spacious, still. Nothing hurried.
```
- **Camera:** 35 mm, sustained pull-back ~1.1 units, orbit 6°/s.
- **Motion:** camera only; clusters hold their shapes.
- **Handle:** 0.5 s each end.
- **Composite:** `EVOLUTION CHAMBER`, all five formation names and all five axis labels are vector.
- ⛔ **No numbers, no scores, no scale on the surface.** Per `claim-ledger.md` C14 there is no
  measurement, so there is no scale — one fabricated "94%" here would invalidate the whole film.
- **Engine notes:** ask for the five clusters as `five clearly different shapes, well separated`. Models
  homogenise repeated elements; if all five look alike, generate the violet one separately and
  composite it in.

---

## SHOT 26 — the functional mesh · 3.0 s cut → generate 4.0 s

```
Wide shot. Seven separate clusters of connected nodes distributed across a broad horizontal
plane in a dark volume, each cluster internally dense but distinct from the others, with a
different internal density in each. Thin lines of deep blue connect the clusters across the
gaps. The camera pulls back steadily and comes to rest, revealing the full arrangement.
Volumetric haze between the clusters gives separation and depth. One cluster sits slightly
forward of the others. Structured and legible, never chaotic.
```
- **Camera:** 35 mm, the film's largest move — 2.4 units back over 3.0 s, easing to complete rest.
- **Motion:** camera only. ⛔ No travelling light on the connections — the discrete `cellbus` signals
  are vector, and they must be countable.
- **Handle:** 0.5 s each end.
- **Composite:** all seven cell names, the `cellbus ▸ signal` labels and the signal packets are vector.
- **Engine notes:** `legible, structured, separated, not chaotic, not a swarm`. Prompt against
  organic motion explicitly — `no flocking, no swarming, static arrangement`.

---

## SHOT 28 — the estate · 2.0 s cut → generate 3.0 s

```
The widest possible view of an immense dark computational volume. Hundreds of small
node-clusters distributed across four clearly distinct depth layers, connected by faint
deep-blue pathways. Far below, a vast horizontal plane in graphite. Far behind, an enormous
faint mesh receding into haze. Activity is present everywhere but nothing moves quickly.
The image reads as organised structure rather than as noise — layered, deep, calm, immense.
The camera drifts backward and comes to complete rest.
```
- **Camera:** 35 mm, slow continued pull-back, at complete rest by the end of the clip.
- **Motion:** four-layer parallax. Slow.
- **Handle:** 0.5 s each end. ⚠ The camera **must** be at rest for the final 0.4 s — shot 29 cuts to
  a locked frame and a moving camera into a locked cut is the one edit that would feel cheap here.
- **⭐ Critical:** legibility over density. If it reads as abstract texture rather than as an
  organisation, reduce the cluster count until structure returns. Generate a 200-cluster and a
  400-cluster version and pick in the previz.
- **Engine notes:** this is the hardest shot to generate and the easiest to overcook. `calm`,
  `organised`, `layered`, `architectural`, `not busy`, `not chaotic`.

---

## Budget and pipeline notes

| | |
|---|---|
| Shots to generate | 6 (4, 16, 20a, 25, 26, 28) |
| Total generated runtime in the cut | 15.4 s of 90.0 s (**17%**) |
| Clip length to request | cut + 1.0 s of handle |
| Realistic take counts | shots 4, 16, 25, 26: 8–15 takes each · shot 28: 20–30 (density) · shot 20a: 15–30 if generated, **1–3 if shot practically** |
| Recommended | shoot 20a on a phone with an amber-gelled lamp. Generate the other five |

**Pipeline order — do not reverse it:**
1. Build the **vector** film complete, with grey placeholder plates in the six generated slots.
2. Watch it in the previz. Fix timing there, where it is free.
3. Render one reference still per generated slot from the finished vector build.
4. *Then* generate, with those stills as references.

Generating first and cutting to the footage afterwards is how a film ends up with beautiful shots in
the wrong order and a title card that lands after the music has already resolved.
