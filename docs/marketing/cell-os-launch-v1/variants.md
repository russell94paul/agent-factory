# CELL OS — variants and the compression ledger

---

## 1. The compression ledger — how the brief's 118 s became 90 s

Every one of the brief's twelve sections is accounted for. Nothing was dropped silently.

| Brief section | Orig | New | Disposition |
|---|---|---|---|
| OPENING 0:00–0:08 | 8.0 s | **6.2 s** | kept. Tightened; the point holds 2.6 s instead of 3.5 s |
| INTRODUCE CELL OS 0:08–0:18 | 10.0 s | **10.4 s** | kept, **expanded 0.4 s**. The naming beat is the positioning |
| OS METAPHOR 0:18–0:30 | 12.0 s | **6.0 s** | ⚠ **halved.** The stack morph survives in full; the 8-label subsystem roll is deleted as a beat and becomes the persistent kernel plane instead — see §2 |
| BUILD A CELL 0:30–0:41 | 11.0 s | **9.2 s** | kept. All 8 compilation stages survive, stacked, in silence |
| CELLS CHANGE SHAPE 0:41–0:51 | 10.0 s | **7.2 s** | kept. 5 topologies → 5 topologies, faster travel |
| CONTEXT VIRTUAL MEMORY 0:51–1:01 | 10.0 s | **7.2 s** | kept. All 5 pipeline stages survive; knowledge labels demoted to mesh depth |
| BOUNDED AUTONOMY 1:01–1:11 | 10.0 s | **8.6 s** | kept. All 6 checks survive; the human beat compressed to 1.2 s |
| PROOF NOT CLAIMS 1:11–1:20 | 9.0 s | **11.6 s** | ⭐ **expanded 2.6 s — the only beat given more time than the brief allowed.** It is the film's one measured claim. See `claim-ledger.md` §3 |
| SHADOW TWIN + EVOLUTION 1:20–1:29 | 9.0 s | **7.2 s** | kept, merged into one reel |
| CELL TO ORGANIZATION 1:29–1:38 | 9.0 s | **3.0 s** | ⚠ **cut hard.** One wide shot instead of a sequence. The scale reads in one frame |
| REAL-WORLD MONTAGE 1:38–1:48 | 10.0 s | **4.0 s** | ⚠ **cut hard.** 8 missions → 6, and the estate wide absorbed into it |
| FINAL 1:48–1:58 | 10.0 s | **7.4 s** | kept. All 7 creed lines survive by stacking rather than replacing |
| | **118.0 s** | **88.0 s** | + 2.0 s of the cold open's pre-VO black = **90.0 s** |

### What the cuts actually cost

Stated plainly, because the person approving this should know what they are losing:

1. **`RED → GREEN → VERIFIED_SUCCESS` is gone**, and not for time. `VERIFIED_SUCCESS` returns **0
   hits** in the repository and `.data/runs.jsonl` holds **0 `PASS`** rows. It was replaced by the
   real five-verdict lattice, which is better. This is a correction, not a compression.
2. **The subsystem roll's 3.5 s** bought eight words on screen at 4.6× the legibility ceiling. As the
   persistent kernel plane those eight labels are now on screen for 58 s instead of 3.5 s. **This cut
   improves the film.**
3. **"One Cell can complete a mission / Multiple Cells can operate a function / Connect them"** loses
   its three-stage build and lands as two lines over two shots. ⚠ **This is the film's real loss.**
   The scale-out is the beat most damaged by 90 s, and it is the first thing the extended cut restores.
4. **Two missions** are cut from the montage (*"Design the next product."*, *"Improve the organization
   itself."*). ⚠ The second is a genuine loss — self-improvement is a distinctive claim — but at
   0.33 s per beat it could not be read.

---

## 2. The extended cut — 118 s

The brief as written, once the corrections are applied. **Recommended as the primary asset for a
website, a keynote, or a documentation page** — anywhere a viewer chose to watch. The 90 s master is
for feeds, where they did not.

Restores, in priority order:

| # | Restore | Cost | Why it matters |
|---|---|---|---|
| 1 | Scale-out as a **three-stage build** — one Cell, then a function, then the estate — with the brief's third VO line | +6.0 s | fixes the 90 s cut's worst compromise |
| 2 | **Mission montage to 8**, at 0.55 s each | +4.5 s | *"Improve the organization itself."* becomes readable |
| 3 | ⭐ **A new reel: the rendered artifact.** `factory/client_review*.py` and `switchboard*.py` produce real client-facing surfaces, `RENDERED_CONFIRMED` in real Chromium (`docs/evidence/switchboard-p1-2026-09-01/`). Chip `● VALIDATED` | +7.0 s | **the only thing in the estate a viewer could be shown working today.** In a longer film this is the second-strongest beat after the verdict lattice |
| 4 | **Subsystem roll restored as a beat**, at 8 labels over 6.0 s (1.3/s — inside the ceiling) | +6.0 s | the kernel plane stays as well; the beat introduces it |
| 5 | Longer holds throughout — title card to 2.4 s, the `UNMEASURABLE` hold to 2.5 s, the creed to 11 s | +4.5 s | the 90 s cut's holds are at their minimum, not their optimum |
| | | **+28.0 s → 118.0 s** | |

VO budget for the extended cut: `(118 − 26) × 2.4 × 0.92 = 203 words`. The brief's original 234 still
does not fit; 203 does, so the extended cut restores roughly 47 of the 78 words cut from the master.

---

## 3. Cutdowns

All derived from the 90 s master. **None re-times the master** — they cut whole shots, so nothing has
to be re-animated.

### 60 s — paid social, pre-roll
Shots 1–13, 18–23, 26, 28–31. Drops reel 2 (elastic), reel 3 (context) and reel 6 (fork).
⭐ Keeps reel 5 whole, including the full 5.6 s verdict shot. **The verdict lattice survives every
cutdown in this document.** VO: L01–L08, L13–L16, L19, L20 = 105 words.

### 30 s — feed, bumper
Shots 1–8, 18–23, 31. The premise, the name, the kernel refusal, the verdict, the card.
VO: L01, L02, L04, L13, L15, L16 = 42 words. Runtime 29.6 s.
⭐ This is the strongest cutdown in the set, because at 30 s the film becomes *only* the two true
claims. The shortest version is the most honest one — worth noticing.

### 15 s — retargeting
Shots 1, 2, 8, 21, 23, 31. VO: L01, L15, L16 = 22 words. Runtime 15.2 s.
Ends on the wordmark with no creed.

### 6 s — bumper
Shots 8 and 31 only. No VO. `OS.SIGNATURE` over the wordmark and the closing line.

---

## 4. Crops

| Crop | Use | Requirements |
|---|---|---|
| 16:9 | master, web, YouTube, keynote | source of truth |
| 9:16 | vertical feeds | ⚠ Shots 9, 10, 22, 23 and 26 are **horizontally composed** and do not survive a centre crop. Each needs a reflowed vertical layout — the verdict lattice is already vertical and crops cleanly; the 4×3 evidence grid becomes 2 columns; the 7-cell mesh becomes a vertical stack. **Budget for 5 reflows, not 5 crops.** |
| 1:1 | feed | as 9:16, less severe. Shots 22 and 26 still need reflow |
| 4:5 | feed | crops from 1:1 |

⛔ Burned-in captions on every crop except 16:9. Matched to `vo-script.md` in-points, never
auto-generated — L16 is ten words and each one is load-bearing.

---

## 5. Non-film assets this package already contains

Worth saying, because three deliverables fall out of the work at near-zero extra cost:

1. **The 11-cue sound library** (`sound-design.md` §5) — the sonic brand. It outlives this film and
   should be versioned separately.
2. **The look bible** (`shooting-script.md`) — the palette, type and semantic colour rules are a
   complete visual identity for a landing page, docs and decks. The amber-means-a-human-decides rule
   in particular should propagate to the product UI.
3. **The maturity chip** — ⭐ a disclosure device that belongs on the website, the docs and the
   product itself, not just in the film. It is the estate's honesty doctrine rendered as an interface
   component, and it is the most reusable thing in this package.
