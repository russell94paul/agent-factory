# CELL OS — motion specification

For the **25 vector shots**. Exact values, so two animators produce the same film.

---

## 1. Easing library

Everything in this film uses one of six curves. A seventh curve is a bug.

| Name | Cubic bézier | Use |
|---|---|---|
| `sys-out` | `0.16, 1, 0.3, 1` | the default. Anything arriving, settling, or coming to rest |
| `sys-in` | `0.7, 0, 0.84, 0` | anything leaving, collapsing, or being absorbed |
| `sys-both` | `0.65, 0, 0.35, 1` | topology travel — nodes moving between positions |
| `strike` | `0.2, 0, 0, 1` | type arrival. Fast start, long settle. Never overshoots |
| `settle` | `0.34, 1.3, 0.64, 1` | the only overshoot in the film. Max 8%. Grid cells and ring arrivals only |
| `linear` | — | ⭐ **procedural motion only** — the syscall token (18, 20), typing (11), packet travel (17) |

⭐ **The `linear` rule is the film's most important motion decision.** Eased motion reads as organic;
constant velocity reads as *processed*. Requests, packets and keystrokes are procedural events and
they must not accelerate. Every glowing-agent video on the internet eases everything, which is why
they all look like creatures. This one should look like software.

---

## 2. Type motion — the only permitted forms

| Tier | Form | Timing |
|---|---|---|
| `[DISPLAY]` | opacity 0→1 with a 4 px upward travel, `strike` | 240–300 ms |
| `[DISPLAY]` (wordmark, shots 8, 31) | opacity only, **zero travel**, `strike` | 260 ms |
| `[DISPLAY]` (letter-spacing form, shot 6 only) | tracking +14% → −1.5%, opacity 0→1, `sys-out` | 500 ms |
| `[LABEL]` | opacity 0→1, 2 px travel, `strike` | 90–140 ms |
| `[MONO]` | ⛔ **types or cuts. Never eases, never travels, never fades** | per-char at 22 c/s, or 1-frame cut |

⛔ Forbidden on type, anywhere: scale-up entrances, blur-in, character-by-character stagger on display
type, rotation, 3D flips, glow pulsing, typewriter sound on non-mono tiers.

**Exit rule:** type in this film mostly does not exit — it stacks and stays, or the shot cuts away
from it. Where an exit is required (shot 6's `AGENT`, shot 31's tagline) it is opacity to 0 over
180–200 ms, `sys-in`, with **no travel**. And in shot 6 there is a mandatory **180 ms gap with no
label at all** between the exit and the entrance. The unit is renamed, not relabelled; the gap is
what says so.

---

## 3. Per-shot motion values

Only the values an animator cannot infer. Read alongside `shooting-script.md`.

| Shot | Element | Values |
|---|---|---|
| 1 | point | opacity 0→1, 700 ms, `sys-out`. Falloff radius breathes ±6% at 0.4 Hz, sine, continuous |
| 2 | headline | 3 words, 90 ms stagger, `strike`, 4 px rise |
| 3 | node convergence | travel 600 ms, `sys-in`, from 0.28 frame-width radius to centre. Labels cross-dissolve 120 ms at contact |
| 4 | lattice draw | radial from centre, 55% coverage by 1.4 s, 1 px `edge`. ⛔ Never exceeds 55% |
| 5 | 8 rings | 240 ms stagger. Each: scale 1.15→1.0, `settle`, 320 ms. Label +60 ms after its ring, `strike` |
| 6 | label swap | `AGENT` out 200 ms `sys-in` → **180 ms empty** → `AI OPERATIVE` in 500 ms tracking form |
| 7 | formation | 5 operatives fade 0→1 over 700 ms staggered 40 ms; travel to position 1.1 s `sys-both`; boundary arc draws 640 ms `sys-out` then one 8% outward pulse, 300 ms |
| 8 | wordmark | 260 ms opacity, zero travel. Subtitle +140 ms. Then **900 ms of absolute stillness** — camera, type and background all frozen |
| 9 | 4 planes | draw bottom-up, 160 ms stagger, each 220 ms `sys-out`. Labels arrive with their plane |
| 10 | plane morph | labels cross-fade in place 120 ms, staggered 90 ms bottom-up. Plane 2 thickness 1→4 units over 700 ms; emission 0→100% over 900 ms `sys-out`. 8 subsystem labels fade to 22% between 4.5 s and 5.8 s, 90 ms stagger, then **hold for the next 58 seconds** |
| 11 | typing | 22 chars/s, `linear`. Block caret, 1 frame wide, blinks 1.6 Hz after the last char |
| 12 | compile chain | 8 stages, 380 ms stagger, each 90 ms opacity + 6 px rise `strike`. Connector 1 px cyan, draws 140 ms `linear`. ⭐ All 8 legible and static from 3.3 s |
| 13 | collapse + boot | chain collapse 420 ms `sys-in`; boundary 500 ms; 6 operatives from 1.0 s, 110 ms stagger; settle by 2.2 s |
| 14 | topology travel | 3 changes, 520 ms each, `sys-both`, nodes on **visible paths**. ⛔ No cross-dissolve between formations |
| 15 | pair + shadow + collapse | pair forms 480 ms; shadow layer fades to 30% violet over 400 ms at +0.4 z; collapse 700 ms `sys-in`, all nodes converging to one point |
| 16 | mesh parallax | three depths at 0.7 / 0.4 / 0.15 relative rate. Ring holds absolutely steady — it is the only static element |
| 17 | packets | ⭐ **exactly 11**, individually countable, 900 ms travel each, `linear`, 80 ms stagger. **2 rejected at AUTHORIZE** — dim to `edge` over 180 ms and fall 0.3 units, `sys-in`. Ring fills 0→60% over 2.4 s and **stops at 60%** |
| 18 | syscall token | travel 1.6 s, **`linear`, constant velocity**. Boundary emission +20% over 1.2 s |
| 19 | 6 checks | 380 ms stagger. Each ✓: 90 ms cyan flash to 100%, settling to 70% over 200 ms. ⭐ The ✕ takes **520 ms** — slower than every pass. Token velocity → 0 in **1 frame**, no deceleration |
| 20 | aperture | boundary opens 340 ms `sys-out`; token resumes at its **original** velocity, `linear`. ⛔ Never faster after approval |
| 21 | token stop | travels 900 ms `linear`, then 0 velocity in **0 frames**. Holds inert 700 ms. ⛔ No shatter, no flash, no red |
| 22 | evidence grid | grid draws 400 ms; 6 artefacts arrive 220 ms apart, each locking with a `settle` overshoot (max 8%), 260 ms. ⭐ One row resolves to `ASSERTED` — 60% opacity, and **stays that way** |
| 23 | verdict lattice | draws bottom-up 140 ms per verdict, 1 px connectors. Hold 1.5 s. Then 4 verdicts → 30% over 500 ms while `UNMEASURABLE` → 100% over 500 ms; display restatement fades up +200 ms. Camera push 0.25 units from 3.4 s |
| 24 | fork | ⭐ **absolute freeze, 320 ms — including the camera.** Then split 620 ms `sys-out`, 0.6 z separation. Divergent internal activity begins immediately and **never re-syncs** |
| 25 | chamber | 5 formations fade 180 ms apart; wireframe surface draws 900 ms; frontier edge highlights 400 ms then holds |
| 26 | mesh | 7 cells resolve 140 ms apart. Signals: discrete packets on 9 routes, `linear`, 3 in flight at any moment — **countable** |
| 27 | montage | per beat: text on frame 1, formation resolves 220 ms `sys-out`, hold 110 ms, hard cut. 6 × 0.33 s |
| 28 | estate | 4-layer parallax at 0.8 / 0.5 / 0.25 / 0.1. Camera **at complete rest** for the final 0.4 s |
| 29 | creed lines | line 1 `strike` 240 ms; line 2 +1.0 s and line 1 **remains** |
| 30 | creed block | display line 300 ms; then 7 mono lines, **200 ms apart, each striking and staying**. Block legible and complete at 2.3 s |
| 31 | final card | wordmark 260 ms; tagline +140 ms; at 1.0 s tagline cross-dissolves 180 ms to the two closing lines, stacked 300 ms apart; fade to black over final 300 ms |

---

## 4. The maturity chip

| | |
|---|---|
| Position | lower-left, 48 px from left, 44 px from bottom (4K), inside safe area |
| Type | 11 px `[MONO]`, +8% tracking, `slate` |
| Dot | 5 px circle, 3 px gap. `slate` for DESIGNED · `blue` for IMPLEMENTED · `cyan` for VALIDATED |
| Rest opacity | 42% |
| On change | rises to 70% over 200 ms, holds 400 ms, returns over 600 ms `sys-out` |
| Present | shot 9 → shot 28. Fades out at 1:22.0 over 400 ms and never returns |
| Absent | shots 1–8 (cold open, before the product is named) and 29–31 (the creed) |

Changes at: shot 9 `● DESIGNED` · shot 18 `● IMPLEMENTED` · shot 21 `● VALIDATED` · shot 24 back to
`● DESIGNED`.

⭐ **The chip going backwards at shot 24 is deliberate and it is the point.** A film that only ever
upgrades its own status badge is marketing; one that downgrades itself on the way into the shadow-twin
beat is a status report. Do not "fix" it.

---

## 5. Grade ramp

| Shots | Exposure | Why |
|---|---|---|
| 1–20 | base | |
| 21–23 | **+1/3 stop**, ramped over 400 ms at the shot 20→21 cut | the measured reel. The film gets visibly more solid where the claims get true |
| 24–28 | base, ramped back over 600 ms | back to designed |
| 29–31 | base −1/6 stop, and the void goes to true `#000000` at 1:22.6 over 300 ms | ⭐ the picture goes quiet with the music |

---

## 6. Build notes

- **After Effects** — shots 2, 3, 5, 6, 8, 9, 10, 11, 12, 19, 21, 22, 23, 27, 29, 30, 31 (type-led).
  Everything type-led belongs where kerning is controllable.
- **WebGL / three.js or Blender** — shots 1, 7, 13, 14, 15, 17, 18, 24 (3D topology with real z).
  ⭐ Shots 14 and 24 need genuine 3D node travel; faking them in 2.5D is visible.
- **Compositing** — the six `PLATE+VECTOR` shots. Generated plate on the bottom, vector on top,
  matched grain applied **last, to the composite** — never to the layers separately, or the vector
  will read as a sticker.
- **Delivery** — ProRes 4444 per shot with handles, then one conform. Not one long comp.
