# Render pass — the page was opened in a real browser, and two defects were found

**Run 2026-08-22** against `docs/artifacts/agent-factory.html`, headless Chrome 1400 / 1000 / 700px,
light + dark, `prefers-reduced-motion: reduce`. Reproduce with
`python scripts/render_pass.py --shots docs/evidence/render-2026-08-22`.

> ⚠ **Scope, stated before the results.** This rendered the **local source file**, not the
> published artifact at `claude.ai/code/artifact/50d3ca62…`. The published page is this file
> wrapped in the host's doctype/head/body skeleton with its own CSS reset and `data-theme`
> stamping. Everything below lives in the page's own CSS and JS and is faithfully exercised — but
> **this is not the deployed surface**, and the two defects should be re-confirmed there before
> anyone calls the consumer layer validated. `scripts/render_pass.py --url <artifact-url>` does
> that in one command; it needs a browser profile logged into claude.ai.

---

## How the six-session blocker was removed

`claude-in-chrome` refused for the sixth time — `tabs_context_mcp` → *"Browser extension is not
connected"*, and `list_connected_browsers` → `[]`. Every local component checks out (see
[the diagnosis](#why-claude-in-chrome-was-never-the-only-option)), so rather than keep chasing it,
the render pass now drives the **installed Chrome directly through Playwright**. No extension, no
claude.ai account, no pairing. That dependency is gone permanently.

## Results

| Check | Verdict |
|---|---|
| Every mark the caption claims is painted | **FAIL** — 110 painted, caption says 115 |
| No legend colour without a mark to explain | **FAIL** — amber swatch never drawn |
| Countable bars, not a solid stripe | PASS — 1.72px min gap |
| The reveal fires | PASS — marks at 49.8px, not the at-rest fraction |
| No text overlaps @ 1400 / 1000 / 700px | PASS — none at any width |
| Body never scrolls sideways @ 1400 / 1000px | PASS |
| Body never scrolls sideways @ 700px | **FAIL** — 828px against a 700px viewport |
| Verdict tokens hold — light | PASS — `--fail #A8332A`, `--pass #1F7A4D`, `--unmeas #B07E14` |
| Verdict tokens hold — dark | PASS — `#E4756A` / `#4FBF89` / `#E3A93D` on `rgb(14,20,24)` |
| Reduced motion lands on the end state, unscrolled | PASS — 49.8px with no scrolling |
| Section 10 readiness table renders | PASS — 25 rows, 25 painted |

Screenshots: `docs/evidence/render-2026-08-22/` — `failed-{1400,1000,700}.png`,
`failed-{light,dark}.png`, `failed-reduced-motion.png`, `tracker-*.png`.

---

## ⭐ Defect 1 — the figure declares a category it never draws

The last-write-wins figure states **115 recorded attempts**, captions itself *"each bar is one
recorded attempt"*, and its legend lists three categories with three swatches:

```
■ 100 failed      ■ 10 completed      ■ 5 started, no outcome recorded
  #A8332A            #1F7A4D             #B07E14  <- amber
```

**110 bars are painted. 100 red, 10 green, zero amber.** Visible in both themes once you look;
invisible to every static check that ran before today.

Located at source — `scripts/build_figure_lastwrite.py`:

```python
seq = [("failed" if e["event_type"] == "stage_failed" else "completed")
       for e in ev if e.get("event_type") in ("stage_failed", "stage_completed")]
starts = sum(1 for e in ev if e.get("event_type") == "stage_started")
return seq, max(0, starts - len(seq))          # open_ = 5
```

`FILL` and `OP` both define an `"open"` entry, and `open_` reaches the caption and the legend —
but **nothing ever appends `"open"` to `seq`**, so no amber bar is ever emitted.

⭐ **This is a regression of representation introduced by a correctness fix.** The comment directly
above that code records the previous bug: an earlier version paired outcomes to starts and
"silently dropped any outcome that had none", reporting 82 failures where the counters said 100.
Fixing it to count *terminal events* was right — and it quietly made the 5 no-outcome starts
legend-only.

The irony is worth stating plainly: the category the figure fails to draw is **the unmeasured
one** — the exact distinction (`UNMEASURABLE` is not a pass) that this entire programme exists to
defend. A figure arguing that unmeasured outcomes get dropped, dropping them.

**Two honest fixes, pick one:** append the 5 `"open"` marks to `seq` so 115 bars paint; or change
the caption to *"110 recorded terminal events"* and state the 5 starts separately. Do not leave a
legend entry with nothing to point at.

## Defect 2 — the page scrolls sideways at 700px

`doc.scrollWidth 828` against a `700` viewport. Every `overflow-x: auto` container is *itself*
828px wide, so it is sized by its content instead of containing it:

```
svg  min-width: 720px   inside   DIV.fig-box     (overflow-x: auto, but 828px wide)
svg  min-width: 760px   inside   DIV.fig-scroll  (overflow-x: auto, but 828px wide)
main                                              828px
```

⚠ **The checklist's diagnosis was aimed at the wrong element.** It attributed this to the SVG's
`min-width: 760px` in `#failed`; the `min-width: 720px` figures are equally implicated, and the
actual failure is that an ancestor (`main`) is content-sized, so `overflow-x: auto` never gets a
constrained width to scroll within. The fix is on the *ancestor chain* (`min-width: 0` /
`max-width: 100%` on whatever flex or grid item wraps these), not on the SVGs.

## A third thing, seen but not measured

In the retired-agent diagram the vertical connector from *"and around again — the loop that
closed"* passes **through** the caption line *"THE RETIRED AGENT · 81 DAYS · THE EDGE THAT WOULD
HAVE MATTERED IS THE ONE THAT IS MISSING"*, between "IS" and "THE". The overlap probe checks
text-against-text only, so this is an eyeball observation, not a measurement. Filed, not fixed.

---

## The probe was wrong twice before it was right

Recorded because a probe nobody has audited is not an instrument, and both errors were confident:

1. **"119 marks, 1 inside the band, min gap −201.66px."** `#failed` holds **two** SVGs; the probe
   measured across both and read two stacked figures as one. Now scoped to `svg.lww`.
2. **A text collision on `--max-turns` × `--max-budget-usd` at 100%.** False.
   `--max-budget-usd` is an inline `<code>` that **wraps**, and `getBoundingClientRect()` returns
   the union of its line boxes — which necessarily swallows whatever precedes it on the first
   line. Now compares `getClientRects()` per line box. Both real defects above survived this fix;
   the false one did not.

## Not done

- **The published surface has still not been rendered.** Only the local source. See the scope note.
- **F2 was not run** — the checklist requires removing at least one thing that encodes nothing, and
  nothing was removed. F2 has therefore not been satisfied by this pass.
- **Neither defect is fixed.** Both are located precisely; the fix is a separate decision.
- **`impeccable` has still never been run against the artifact** (gate `chain`). Its 59
  deterministic detector rules are the instrument that would have caught these earlier, and it
  needs no browser.
- **Row-count drift, unresolved:** section 10 renders **25** rows. The checklist says 23; the
  readiness set is now **30** gates. The artifact's table is stale against the gate list.

## Why `claude-in-chrome` was never the only option

Measured 2026-08-22, so nobody re-runs it:

| Link | State |
|---|---|
| Extension installed | ✅ v1.0.85, `fcoeoabgfenejglbffodgkkbkcdhcgfn`, `Default` profile, since 2026-08-06 |
| Extension enabled | ✅ On, service worker + offscreen.html alive, all-sites access |
| Chrome account | ✅ `paulrussell94@gmail.com` — matches Claude Code |
| Enterprise policy | ✅ none (`HKLM`/`HKCU\SOFTWARE\Policies\Google\Chrome` absent) |
| Native messaging host | ✅ registered, manifest allows the exact extension id |
| Native host launcher | ✅ `claude.exe --chrome-native-host` spawns and stays up |
| **Browsers connected to the account** | ❌ **`list_connected_browsers` → `[]`** |

Every link is individually healthy and the account-level registry is still empty, so the failure
sits in the one place not inspectable from outside: the extension's own service-worker connection
state. Chrome has been running since **2026-08-17**; Claude Code was replaced on disk on 08-20 and
again on 08-21. The cheap remaining hypothesis is a stale pairing held across those upgrades, and
the cheap test is reloading the extension or restarting Chrome.

**It no longer blocks anything.** Playwright talks to the same Chrome binary with none of this
chain in the path.
