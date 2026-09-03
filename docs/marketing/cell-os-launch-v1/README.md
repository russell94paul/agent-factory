<div align="center">

# CELL OS — launch film package v1

**90.0 seconds · 31 shots · 156 words · 25.0 seconds of designed silence**

*Production-ready. A studio, a solo editor, or a generative pipeline can execute this without
asking a follow-up question.*

`docs/marketing/cell-os-launch-v1/` · built 2026-09-02

</div>

---

## What this is

A complete film package, not a treatment. Built with the `launch-film` skill against a claim ledger
built with `launch-narrative`, both created for this task and now routed in
`~/.claude/skills/INDEX.md`.

| File | What it settles |
|---|---|
| `claim-ledger.md` | ⭐ **read first.** Every spoken and on-screen claim, its status, its evidence path, and the phrasing it is permitted |
| `timing.md` | the arithmetic that decided the cut — and the conflict in the brief, stated with both numbers |
| `shooting-script.md` | the look bible, then all 31 shot cards |
| `vo-script.md` | narrator-only script, timing marks, direction, the modal-compliance table |
| `sound-design.md` | 11-cue sonic vocabulary, music arc, ducking map, the silent-social pass |
| `motion-spec.md` | per-shot easings and values for the 25 vector shots |
| `gen-prompts.md` | prompts for the 6 generated shots, with negatives, handles and take counts |
| `variants.md` | the compression ledger, the 118 s extended cut, and the 60/30/15/6 s cutdowns |
| `previz.html` | ⭐ **the watchable one.** Real timings, real type, real narration, a real transport |

---

## The three things a reader should know before opening any of it

**1. The brief could not be shot as written.** Its header asks for 75–90 s; its section timecodes sum
to **118 s**; its 234 words of narration need 101.7 s of speech before a single pause. Resolved as a
90.0 s master with every section accounted for, plus a documented 118 s extended cut. Nothing was
dropped silently — `variants.md` §1 is the ledger.

**2. Two claims in this film are measured. Eighteen are modal, on purpose.** This repository's own
README opens with `10 runs, 0 PASS, all dry_run=True`, and `docs/_index/current_vs_proposed.md`
grades Org-IR, HyperMESH, the Evolution Chamber and the Shadow Twin as **designed or specified,
never built**. So the film says *can*, *is designed to*, *could* — and carries a **maturity chip** in
the lower-left of every mechanism reel reading `● DESIGNED` / `● IMPLEMENTED` / `● VALIDATED`.

⭐ That chip is the best creative decision in the package. A film about a platform whose thesis is
*"do not confuse a declaration with a mechanism"* that labels its own maturity frame by frame is not
hedging — it is a demonstration, and no competitor's launch video can copy it without contradicting
itself.

**3. The brief's climax was invented; the real one is better.** `VERIFIED_SUCCESS` returns **0 hits**
in this repository and `RED → GREEN` cannot be shown as a present fact against `0 PASS` rows. Both
were cut. In their place, the thing `factory/contract.py` actually implements:

> `NOT_RUN < PASS < UNMEASURABLE < FAIL < ERROR`
>
> **"A check whose instrument could not run has not passed."**
>
> Five verdicts, never collapsed. Grounded in ISO/IEC 9646 and carried still by TTCN-3
> (ITU-T Z.140 §24.2).

Every competitor can claim orchestration. None of them ships a verdict meaning *the thing that was
supposed to measure this could not see*. It is shot 23, it holds the screen for **5.6 s** — longer
than any other shot — and it takes the film's only full musical resolution.

---

## Regenerate every count on this page

```bash
# runtime, shot count and the timeline's own geometry
python scripts/render_check_previz.py --shots docs/evidence/cell-os-previz-2026-09-02/

# narration word count, from the delivered script
python - <<'EOF'
import io,re
blk=io.open('docs/marketing/cell-os-launch-v1/vo-script.md',encoding='utf-8').read().split('```')[1]
print(sum(int(m) for m in re.findall(r'\((\d+)w\)', blk)))          # 156
EOF

# the facts the claim ledger is gated on
python -c "import json;r=[json.loads(l) for l in open('.data/runs.jsonl',encoding='utf-8')];print(len(r),sum(1 for x in r if x.get('outcome')=='PASS'))"   # 10 0
grep -rc "VERIFIED_SUCCESS" --include=*.py --include=*.md factory/ docs/specs/ | grep -v ':0' | wc -l   # 0
```

---

## Rendered validation

`previz.html` is a client- and studio-facing surface, so it is gated the way every rendered surface
in this estate is — real Chrome, three widths, plus the two states a document must survive.

```bash
python scripts/render_check_previz.py --shots docs/evidence/cell-os-previz-2026-09-02/
```

```
previz render check: PASS
  1400px  blocks=31 vo=20 rows=31 sum=100% h_scroll=False stage_chars=44
  1100px  blocks=31 vo=20 rows=31 sum=100% h_scroll=False stage_chars=44
   760px  blocks=31 vo=20 rows=31 sum=100% h_scroll=False stage_chars=44
  transport  0:17.1 -> 0:18.6 (advanced), paused at 0:18.6, cued S23 · I · VECTOR
  no-js      5308 chars, 5 panels, 31 static rows, matches_js=True
  reduced    finds_invisible=0
```

What each gate is for, since a render check that only proves paint proves little:

| Gate | Why it exists |
|---|---|
| `sum=100%` | every timeline block's width is computed from its real duration. If the widths do not sum to 100% the figure is lying about the pacing |
| `transport advanced / paused / cued` | ⭐ a timeline that *renders* is not a timeline that *advances*. This presses play, proves the clock moved, proves pause stopped it, and proves clicking block 23 lands on the `UNMEASURABLE` frame |
| `no-js 31 static rows, matches_js=True` | the 31 shot rows are authored statically so the page is a complete document with no script — and the check asserts they have not drifted from the data the transport renders |
| `reduced finds_invisible=0` | nothing is parked at `opacity:0` waiting on an observer |

⚠ **One defect this check caught and the fix.** The first run failed `no-js` at 2,644 characters —
the shot table and timeline were JS-built, so with script off the page lost the entire cut. The rows
are now authored in the HTML with a drift assertion holding them to the data. A previz nobody
rendered is a document with ambitions.

Evidence, including screenshots at all three widths, the shot-23 anchor frame, the no-JS pass and the
reduced-motion pass: `docs/evidence/cell-os-previz-2026-09-02/`.

---

## What a studio still has to decide

Stated so the gaps are visible rather than discovered:

1. **Voice casting.** Direction, register and phrasing are specified; the voice is not. `vo-script.md`
   recommends auditioning an engineer rather than a narrator.
2. **The music bed.** Arc, BPM, entry and drop-out points are specified to the frame; the composition
   is not. The 11 cues matter more than the bed and should be built first — they are the sonic brand
   and they outlive this film.
3. **Which generative engine.** `gen-prompts.md` is engine-agnostic with per-engine notes. Only 6 of
   31 shots are affected, and shot 20a is faster to shoot on a phone than to generate.
4. **The five vertical reflows.** Shots 9, 10, 22, 23 and 26 are horizontally composed and do not
   survive a centre crop to 9:16. Budget reflows, not crops — `variants.md` §4.
5. **The final card.** Four text elements in 2.0 s is the package's tightest moment. If it does not
   read in the previz, take 0.6 s from shot 27. ⛔ Never from shot 23.

---

## ⛔ Before this goes anywhere outward

Nothing in this package has been published, sent, or shown outside this repository. Both skills that
produced it require an explicit per-destination approval, and the film makes forward-looking claims
about subsystems this repository grades as unbuilt. Approval for the previz is not approval for the
film; approval for the film is not approval for a landing page.

The one paragraph to read before approving anything: `claim-ledger.md` §4, *Refused* — the list of
things this package declined to say, written down so the refusals are auditable rather than invisible.
