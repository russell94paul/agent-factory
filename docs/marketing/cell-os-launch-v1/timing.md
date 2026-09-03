# Timing arithmetic — decided before the script, per `launch-film` Phase 1

## 1. The conflict in the brief, stated with both numbers

| | Value |
|---|---|
| Runtime the brief's header requests | **75–90 s** |
| Sum of the brief's own section timecodes (0:00 → 1:58) | **118 s** |
| Words of narration in the brief as written | **234** |
| That narration at 2.3 w/s (understated read) | **101.7 s of speech alone**, before a single pause |

The brief cannot be shot as written inside its own stated runtime. The section plan is a **118-second
film**. Resolved rather than silently chosen:

- **Primary deliverable — 90.0 s.** The top of the requested range. Every one of the brief's twelve
  sections survives; two are merged, two are cut, one is *expanded*. See `variants.md` for the ledger
  of what each change costs.
- **Extended cut — 118 s**, documented as a labelled variant, not shipped as the master.

⚠ 90 s is the top of the range on purpose. At 75 s the mechanism reels drop from six to four and the
film becomes a teaser; the brief's content does not fit a teaser.

## 2. The budget

```
runtime target        T   = 90.0 s
silent beats          S   = 16.0 s     design assumption at budget time
                                        (cold open, title hold, one dense-figure hold,
                                         the verdict hold, the creed)
speech window         T−S = 74.0 s
delivery rate         r   = 2.4 words/sec
                            understated, deliberate. 2.8–3.2 is an ad read and the brief
                            explicitly rejects that register
gross budget          74.0 × 2.4        = 177.6 words
pause reserve         −8%               = −14.2 words
────────────────────────────────────────────────────────
VO WORD BUDGET                          = 163 words
```

## 3. Actual, measured

```bash
# regenerates the delivered word count from vo-script.md
python - <<'EOF'
import io,re
blk=io.open('vo-script.md',encoding='utf-8').read().split('```')[1]
print(sum(int(m) for m in re.findall(r'\((\d+)w\)', blk)))   # 156
EOF
```


| | Value |
|---|---|
| VO word budget | 163 |
| **Delivered** | **156** |
| Headroom | 7 words |
| Speech at 2.4 w/s | 65.0 s |
| Pause available inside the speech window | 74.0 − 65.0 = **9.0 s** across 20 lines ≈ 0.45 s mean inter-line rest |
| Compression against the brief | 234 → 156 words, **−33.3%** |

The 9.0 s of distributed rest is what buys the "intentional pauses" the brief's voiceover note asks
for. It is a budgeted quantity, not a hope.

**Reconciliation against the delivered cut.** The `S = 16.0 s` above was the assumption made *before*
the shooting script existed. The delivered script's designated holds measure **18.8 s** — cold open
2.9, title card 1.3, compilation chain 4.6, evidence grid 2.7, verdict lattice 1.8, creed 5.5. Rerun
the budget on the real number:

```
(90.0 − 18.8) × 2.4 × 0.92 = 157.2 words
```

Delivered **156**. The script fits the pre-hoc budget with 7 words spare and the post-hoc budget with
1 word spare. Stated both ways because only the second one was measured, and a budget that only
survives its own assumption is not a budget.

## 4. Information density check

Ceiling: **one new named concept per 2 s of screen time**, and a viewer cannot read on-screen text
while absorbing different spoken words.

| Shot | Named concepts | Dur | Density | Verdict |
|---|---|---|---|---|
| 5 — Operative attribute rings | 8 | 2.6 s | 3.1 /s | ⛔ over ceiling → stacked, VO carries only the definition |
| 12 — compilation chain | 8 | 3.8 s | 2.1 /s | ⛔ over ceiling → stacked, **VO silenced** |
| 25 — evolution chamber (5 formations + 5 axes) | 10 | 3.6 s | 2.8 /s | ⚠ over → axes demoted to a 30% legend, read as one object |
| 26 — functional cells | 7 | 3.0 s | 2.3 /s | ⚠ over → labels arrive with their objects, not as a list |
| 30 — creed block | 7 | 1.4 s | 5.0 /s | ⛔ **worst in the film** → stacked accretion, VO silent |
| 27 — mission montage | 6 | 2.0 s | 3.0 /s | ✓ permitted — six *cuts*, not six readings. Rhythm, not comprehension |
| all others | ≤ 3 | ≥ 2.0 s | ≤ 1.3 /s | ✓ |

**The fix is a craft answer, not a compromise: stack, do not replace.** Text that accretes and
*stays* is read as one glanceable object rather than as eight sequential readings. Sequential
replacement at 0.4 s/label is unreadable; eight labels striking into a persistent grid at 0.4 s
intervals is a legible 3.8-second figure. Applied to shots 5, 12, 26 and 30.

Two structural consequences, both enforced in the shooting script:

1. **Shots 12, 22, 27 and 30 carry no narration at all.** Where dense on-screen text lands, the
   narrator is silent; where the narrator speaks, on-screen text is at most one display line. This is
   why the word count came in *under* budget — the silence is load-bearing, not left over.
2. ⭐ **The brief's 8-label subsystem roll was deleted as a beat.** At 3.5 s it violated the ceiling
   by 4.6× and read as a word list. Those eight labels are now the **persistent kernel plane**
   (`shooting-script.md` → look bible), on screen at 22% opacity from shot 10 to shot 28 — a density
   of 0.13 /s, legible across sixty seconds, costing zero runtime, and making every later shot feel
   like it is happening inside an operating system. The list became the set.

## 5. Frame rate and master format

| | Value | Why |
|---|---|---|
| Master | 3840 × 2160, **24 fps**, Rec.709, ProRes 4444 | 24 fps is the cinematic cadence the brief asks for, and every move here is slow enough that judder never appears |
| Optional matte | 2.39:1 letterbox as a graded variant | Full-frame 16:9 is the safer web master; the matte is a choice, not the default |
| Safe area | nothing load-bearing in the top or bottom 12% | protects the 9:16 and 1:1 crops in `variants.md` |
| Loudness | master **−14 LUFS**, social **−16 LUFS**, true peak −1 dBTP | |

⚠ **Vector UI motion is animated on 24s (one position per frame), not on 12s.** Stepped UI animation
at 24 fps reads as stutter on a product surface; the whole point of the look is that it feels like
real software.
