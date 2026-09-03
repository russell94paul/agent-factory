# CELL OS — sound design

**90.0 s · master −14 LUFS · true peak −1 dBTP · 48 kHz / 24-bit · stereo, with a mono fold-down check**

The premise: **sonic branding is a small set of recurring cues with fixed meanings**, not a music bed
with whooshes on the cuts. Eleven cues. Each one means exactly one thing, every time it appears. That
repetition *is* the branding — a viewer who watches twice learns the vocabulary without being told.

⛔ Forbidden throughout, per the brief: risers used as punctuation, cinematic braams, laser zaps,
gaming UI blips, explosions, whooshes on cuts, vinyl crackle, ticking clocks.

---

## 1. The cue sheet

| Cue | Trigger (meaning, not shot) | Character | Band | Dur | Shots |
|---|---|---|---|---|---|
| `SUB.PULSE` | the void, before anything exists | pure sine, no attack transient, slow bloom | 38–55 Hz | 1400 ms | 1 |
| `AGENT.TICK` | one process activates | dry digital transient, no tail, no pitch | 2–4 kHz | 60 ms | 3 |
| `CELL.BOOT` | an organization comes into being | deep harmonic expansion, fundamental rising through its own overtones | 80 Hz → 3 kHz | 2200 ms | 7, 13 |
| `MESH.SWEEP` | knowledge is retrieved | filtered noise sweep, wide stereo, no resonant peak | 400 Hz → 8 kHz | 900 ms | 16, 17 |
| `SYSCALL.ROUTE` | a capability call is routed | precise routed click, two-band, dry | 1.2 kHz + 3.5 kHz | 45 ms | 12 (×8), 18, 20, 27 (×6) |
| `KERNEL.DENY` | authority is withheld | muted low pulse. ⛔ **no reverb tail** — the sound stops as the request stops | 60–90 Hz | 500 ms | 19 |
| `EVIDENCE.LOCK` | a proof is accepted | short glass-on-metal lock, tight transient, small bright tail | 900 Hz–6 kHz | 220 ms | 19 (×5), 20, 22 (×6) |
| `FORK.SPLIT` | a counterfactual branches | mono collapsing to hard L/R — the same sound in two places | full | 700 ms | 15 (quiet), 24 (full) |
| `VERDICT.RESOLVE` | the system reaches a conclusion | restrained harmonic resolution, a perfect fifth, no cadence flourish | 110 Hz + 165 Hz + air | 1800 ms | 23 |
| `UI.LABEL` | a label appears | near-silent tick, barely present | 5–7 kHz | 18 ms | 5 (×8), 9 (×4), 25 (×5) |
| `OS.SIGNATURE` | the product is named | deep cinematic signature tone, resolving *into* silence rather than out of it | 55 Hz fundamental + 4th/5th | 3200 ms | 31 |

**Rules that make the vocabulary hold:**

1. `EVIDENCE.LOCK` never fires for anything that is not evidence. It is the film's most-used cue and
   its meaning must stay exact — six locks in shot 22 and five in shot 19 teach the viewer what the
   sound means, and one misuse un-teaches it.
2. `KERNEL.DENY` has **no tail**. Every other cue decays; this one stops. That absence is the sound of
   a boundary.
3. `UI.LABEL` is capped at **8 per shot** and always descends in level. It is texture, not information.
4. `FORK.SPLIT` appears twice — quietly at 0:38 and fully at 1:08. The first is a rehearsal the viewer
   does not know they are hearing.
5. ⭐ `VERDICT.RESOLVE` fires **once in the film**, at 1:03.5. Nothing else resolves harmonically. If
   it appears anywhere else the anchor beat loses its only structural privilege.

---

## 2. Music arc

~62 BPM. Sub-bass, a slow four-note arpeggio, a sustained string-adjacent pad, no percussion until
1:15.6 and even then only a low pulse. No melody a viewer could hum — the film is not selling a mood.

| Time | Event | Level |
|---|---|---|
| 0:00.0 | nothing. `SUB.PULSE` only | — |
| 0:02.6 | room tone enters | −38 dB |
| 0:06.0 | ⭐ 300 ms of near-total silence on the fracture cut | — |
| 0:07.2 | **music enters** — sub-bass + arpeggio | −24 dB |
| 0:17.2 | title card: the arpeggio drops out, one sustained note under the wordmark | −20 dB |
| 0:18.6 | pad enters, arpeggio returns | −18 dB |
| 0:31.0 | **build 1** — a second voice joins on the Cell boot | −15 dB |
| 0:48.2 | **build 2** — 90 Hz tension pad rises through reel 4 | −13 dB |
| 0:53.8 | ⛔ **duck 4 dB on `KERNEL.DENY` and hold there.** The music does not recover until 1:03.5 | −17 dB |
| 0:56.8 | reel 5 opens *below* the previous level. The quietest sustained passage in the film | −19 dB |
| 0:59.2 | ⭐ 400 ms of total silence after the token stops dead | — |
| 1:03.5 | **full resolution** — `VERDICT.RESOLVE`, the only one | −11 dB |
| 1:05.0 | reduce to a single sustained note | −20 dB |
| 1:15.6 | re-enter at full width for the scale-out, low pulse joins | −12 dB |
| 1:22.6 | ⭐⭐ **music stops.** Room tone only for 7.4 s | −40 dB |
| 1:28.0 | `OS.SIGNATURE` alone | −13 dB |
| 1:29.7 | signature resolves into the black. The last 300 ms is sound over nothing | fade |

⭐ **The 1:22.6 drop-out is what the preceding ninety seconds of density is for.** It is the most
reliable emotional move available in a launch film and it only works if nothing earlier has spent it.
Do not add a final swell under the creed. Do not add one under the wordmark either — `OS.SIGNATURE`
is the swell.

---

## 3. Ducking and bus structure

```
MASTER
├── VO           −6 dB sidechain trigger on MUSIC   attack 120ms / release 400ms
│                high-pass 90 Hz · de-essed · 3:1 comp at −18 dBFS · no reverb
├── CUES         −2 dB sidechain from VO. Cues are never ducked by music
├── MUSIC        receives both sidechains. Ceiling −11 dB
└── ROOM TONE    static, −38 dB, present from 0:02.6 to 1:30.0 without a gap
```

**The room tone never stops** — not in the drop-out, not in the silences. Four times in this film the
music and cues go to nothing; if the room tone went with them the cut would read as a technical fault
rather than as a held breath. The three designated total silences (0:06.0, 0:59.2, and the 1:22.6
drop) are silences *of music*, not of audio.

VO always sits at least 6 dB above the bed. Check it at the four densest moments: 0:31.2, 0:52.4,
1:03.6, 1:20.3.

---

## 4. The silent-social pass

⚠ **This film will mostly be watched muted.** Every load-bearing sound needs a visual equivalent, and
five of them do not have one yet:

| Cue | Carries | Visual equivalent required |
|---|---|---|
| `KERNEL.DENY` | the refusal | already visual — the amber ✕ and the token stopping dead ✓ |
| `EVIDENCE.LOCK` | proof accepted | already visual — the 60 ms scale overshoot on each grid cell ✓ |
| `VERDICT.RESOLVE` | the conclusion | ⛔ **needs one** — add a single 1 px `cyan` underline drawing beneath `UNMEASURABLE` over 400 ms |
| `FORK.SPLIT` | the branch | already visual — the z separation ✓ |
| `OS.SIGNATURE` | the product landing | ⛔ **needs one** — 4% scale settle on the wordmark over 500 ms, cubic-out |
| the 1:22.6 drop-out | the change of register | ⛔ **needs one** — the void goes from `#05070B` to true `#000000` over 300 ms at 1:22.6. The image itself gets quieter |

⭐ That last one is the best idea in this document. **Make the picture go silent too.**

**Captions:** burned-in for the social crops, `[MONO]` at 60% opacity, bottom third, inside the safe
area, one line at a time, matched to the VO in-points in `vo-script.md`. Never auto-generated — L16
is ten words and every one of them matters.

---

## 5. Deliverables

```
cellos_master_90s.wav          48/24 stereo, −14 LUFS, −1 dBTP
cellos_master_90s_mono.wav     fold-down check — verify KERNEL.DENY and SUB.PULSE survive
cellos_social_90s.wav          −16 LUFS, high-passed at 60 Hz for phone speakers
stems/vo.wav  stems/music.wav  stems/cues.wav  stems/roomtone.wav
cellos_mne.wav                 music + effects, no VO, for localisation
cue_library/*.wav              the 11 cues as individual assets — ⭐ these are the sonic brand
                               and they outlive this film. Version and keep them.
```

⚠ **Phone-speaker check is mandatory.** `SUB.PULSE`, `KERNEL.DENY` and `OS.SIGNATURE` all live below
90 Hz and will be inaudible on a phone. The social mix needs each of them re-voiced with an audible
harmonic at 180–220 Hz, or three of the film's most meaningful moments simply do not exist for most
of its audience.
