# Static detector pass — impeccable's 59 rules against `docs/artifacts/agent-factory.html`

**Run 2026-08-22**, gate `chain` (readiness gate list). Companion to
`docs/evidence/render-pass-2026-08-22.md` (Playwright, same file, same day) — this is the other
instrument the render-pass writeup flagged as never having been run.

⚠ **Reproducibility note on the `chain` gate itself.** `factory/readiness.py:775-786`
(`g_impeccable_precedence_settled`) reads `~/.claude/skills/living-systems-ui/SKILL.md` — a file
that lives **outside this repository**, in a separate personal skills checkout (its own git repo,
branch `chore/library-catchup-2026-08-17`, currently uncommitted there). Reinstalling or losing
that skill on this machine, or checking this repo out fresh elsewhere, silently reverts the gate
to FAIL with no record in `agent-factory` of what the precedence ever said. The gate check itself
is also a naive substring match (`if "impeccable" in txt.lower()`) — it cannot tell a real
precedence statement from the word appearing once in a heading, so passing it is not itself
evidence of anything; the content is. For both reasons the precedence text is mirrored verbatim
below so the claim survives independently of that external file.

<details>
<summary>Mirrored verbatim from <code>~/.claude/skills/living-systems-ui/SKILL.md</code>, added under its existing "Read this first — where this sits" section, 2026-08-22</summary>

> ### Where `impeccable` sits in this chain
>
> `impeccable` is a fifth design authority with a trigger broad enough to fire on the same work: "design,
> redesign, shape, critique, audit, polish… a frontend interface" covers a living-systems page just as
> much as a product UI. Its scope is not the same as the four skills above, and it does not outrank them.
>
> - **`impeccable` never owns a self-contained Artifact's build decisions.** Its workflow — `init` /
>   `new-work`, `PRODUCT.md` / `DESIGN.md`, the hook-driven edit loop, `live` browser iteration — assumes
>   a persistent project with a repo and a running dev server. A living-systems page has neither: it is one
>   HTML file with no build step, calibrated by `artifact-design` and modeled by this skill. Never let
>   `impeccable`'s routing open a `new-work`/`shape` flow on top of an Artifact in place of `artifact-design`'s
>   own calibration — that is scope creep from a skill whose default target is a full product surface, not
>   a single figure.
> - **`impeccable`'s *detector* is a useful, optional, additive check — after the four above, not instead
>   of them.** Run it (`node .claude/skills/impeccable/scripts/detect.mjs <file> --json`, or `npx impeccable
>   detect`) as a supplementary static/browser pass over a *finished* artifact. Its 59 deterministic rules
>   catch generic frontend anti-patterns — AI-slop visual tells (side-tab borders, hero-eyebrow chips),
>   computed WCAG contrast ratios, undersized/tiny text, cramped padding — that the other four skills do
>   not enumerate as checklist items. It needs no browser for the static engine and nothing here replaces
>   running it.
> - **On a genuine conflict, split by domain, not by seniority.** `artifact-motion` — and this skill's own
>   `references/QUALITY_GATES.md`, which operationalizes it for a living-systems page — is authoritative for
>   anything touching motion, reduced-motion behavior, or whether a figure's geometry is computed from a
>   real measured number: `impeccable`'s detector has no rule for any of that and is not a vote on it.
>   `impeccable`'s detector is authoritative for the generic UI-quality lane it actually measures —
>   contrast, spacing, typography, AI-slop tells — where the four Artifact skills state principles (rule 3,
>   "every number carries its basis"; "seamless, not a card grid") but do not run a deterministic scan.
> - **A finding from `impeccable`'s detector is a claim, not a fact, until checked against the rendered
>   page.** Its static-HTML engine does not evaluate `@media` blocks and only partially resolves CSS custom
>   properties across `:root[data-theme]` variants — a page that swaps its whole palette under
>   `prefers-color-scheme` or a `data-theme` attribute (the pattern `artifact-design` itself mandates) can
>   produce contrast findings quoting colors the browser never actually pairs. Verify a sample against the
>   source before acting on a bulk finding; don't let an uninstalled-parser degraded run (`DEGRADED — HTML
>   parser modules unavailable`, falling back to regex) stand in for the real 59-rule pass either — install
>   `htmlparser2`, `css-select`, `css-tree`, `domutils` alongside `scripts/detect.mjs` first.

</details>

*(Corrected once already: the conflict-authority bullet originally pointed at
`artifact-motion`'s `references/QUALITY_GATES.md`. That directory doesn't exist —
`artifact-motion` ships only `SKILL.md`; the file lives at
`living-systems-ui/references/QUALITY_GATES.md`, this skill's own. Caught by the same
`reviewer` pass noted below; fixed in the live file and re-mirrored here.)*

⚠ **Both defects that render pass doc found are already fixed on this branch**, by commit
`330742d fix(artifact): draw the category the figure declared, stop the sideways scroll, make
drift fail the suite` — landed after that doc was written, before this pass ran. Re-running
`python scripts/render_pass.py` just now: **every check passes**, 115/115 marks painted including
5 amber, 700px viewport `scrollWidth 700 vs client 700`. The "what render pass caught" section
below describes what that instrument found on the pre-fix file (historical, from the cited doc) —
not a currently-open defect. It stands as evidence of what the *class* of check can catch that the
static detector structurally cannot, which is the question this pass exists to answer.

## Reproduce

```
node ~/.claude/skills/impeccable/scripts/detect.mjs docs/artifacts/agent-factory.html --json
```

⚠ **This silently under-counts on a fresh checkout.** The bundled static-HTML engine needs
`htmlparser2`, `css-select`, `css-tree`, `domutils`; none ship with the skill. Without them it
falls back to **regex matching** and prints `DEGRADED — HTML parser modules unavailable` **to
stderr only** — the JSON on stdout still comes back well-formed, just with 1 finding instead of
313, and exits non-zero either way so exit code alone doesn't tell you which mode ran. Fix:

```
cd ~/.claude/skills/impeccable && npm install htmlparser2 css-select css-tree domutils --no-save
```

`npx impeccable detect` sidesteps the missing-deps problem but is **not the same instrument** —
it resolves whatever `impeccable` is published on the npm registry (**3.6.0** here), not the
skill installed locally (**4.1.1**, whose registry file is the one the readiness gate's evidence
line — "59 deterministic detector rules" — actually counts:
`scripts/detector/registry/antipatterns.mjs`, 59 `id:` entries). On this file the two versions'
output happened to match byte-for-byte (313 findings, identical breakdown) — that is a
coincidence worth re-checking on a rule change, not a guarantee the two stay in sync.

## Result: 313 findings, 0 errors, all `warning` severity

| Rule | Count | Verdict after checking against the source |
|---|---|---|
| `low-contrast` | 258 | **All 258 are a detector artifact, verified against a real browser — see below.** A real, smaller, different contrast defect (225 near-miss failures, light theme only) was hiding underneath and is reported there instead. |
| `undersized-ui-text` | 25 | Not independently checked this pass. |
| `all-caps-body` | 11 | Not independently checked this pass. |
| `tiny-text` | 9 | Not independently checked this pass. |
| `side-tab` | 5 | Matches source directly (`border-left:3px solid var(--accent)`) — real. |
| `cramped-padding` | 3 | Not independently checked this pass. |
| `hero-eyebrow-chip` | 1 | Not independently checked this pass. |
| `wide-tracking` | 1 | Not independently checked this pass. |

## ⭐ The low-contrast finding is ~100% noise — and a real, different, smaller defect was hiding under it

**Revision note, same day.** The paragraphs below replace an earlier version of this section that
overstated its own proof and got caught by an independent `reviewer` pass. Kept for the record,
corrected in place: the earlier draft folded 196 of the 258 findings (`#000000 on #141b21` ×195,
`#000000 on #0e1418` ×1) into a "97% proven false positive" headline on the strength of a grep
that only ever covered 56 of them (the `#828e97`/`#a9b4bc`/`#e7ecef` rows). It then separately,
two paragraphs later, listed those same 196 as "not dismissed… recorded as open" — a direct
self-contradiction a careful reader would have caught before I did. It also cited a corroborating
instrument (`render-pass-2026-08-22.md`'s dark-token check) that never actually reads any
element's text color — only three named CSS variables and the body background — so "no black text
was observed there" was never something that check could have observed. And it cited two source
lines as the detector's own documented mechanism; both citations were wrong (one documents an
already-suppressed alpha-fallback class, the other is scoped to an unrelated border pre-pass, and
the real cascade builder *does* flatten `@media` blocks — see below). None of that changes the
verdict, only how it's supported. Corrected, with real measurements this time:

**56 of 258 are provably impossible by token cross-reference**, same as before. `low-contrast`'s
258 findings collapse to 10 distinct `text-color on bg-color` pairs; three of them pair a hex
value that exists **only** in this page's dark-theme token block with a hex value that exists
**only** in the light-theme block:

| Snippet | Count | Text color is only… | Background color is only… |
|---|---|---|---|
| `#828e97 on #ffffff` | 32 | `--ink-3`, dark (`docs/artifacts/agent-factory.html:22,32`) | `--raise`, light (`:8`) |
| `#a9b4bc on #ffffff` | 18 | `--ink-2`, dark (`:22,32`) | `--raise`, light (`:8`) |
| `#e7ecef on #ffffff` | 6 | `--ink`, dark (`:22,32`) | `--raise`, light (`:8`) |

`grep -n "828E97\|A9B4BC\|E7ECEF" docs/artifacts/agent-factory.html` returns only the two
dark-token definition lines — those hex values are never hand-written elsewhere, so the only way
text paints `#828e97` is the dark theme being active, and the only way a `--raise` background
paints `#ffffff` is the light theme being active. One page, one theme, one paint; the pairing is a
contradiction. (`#ffffff` as a *background* specifically is real, not a further artifact: the
detector's own comment at `checks.mjs:~1765` — *"Guessing white here is what flooded dark themes
with false `on #ffffff` findings"* — records that it deliberately refuses to guess white and only
reports it when a real `--raise:#FFFFFF` resolves, which the light theme's own token, correctly,
does.)

**The other 202 (the 196 `#000000` findings, plus the 6 remaining same-theme-accent pairs) are
false positives too — proven directly, not inferred.** Rather than keep reverse-engineering the
static tool's internals (the previous draft's failure mode), this pass opened the real, current
file in the real, installed Chrome via Playwright — `color-scheme: dark` and `color-scheme: light`
separately, `getComputedStyle` on every element with direct text — and asked the only question
that matters: **does anything actually paint black text, or any of the other disputed pairs, in
this browser?**

```
dark:  776 elements checked with direct text, 3 have computed color rgb(0,0,0) —
       and all 3 are <title> and <style> tags: never rendered, not text a visitor sees.
       Zero real black text anywhere in the dark theme.
```

That is decisive for both `#000000` rows (196 findings) and, by the same run, the remaining 6
same-theme-accent findings never appeared as a genuine failure either — a real WCAG check across
every element in the actual dark render found exactly **one** contrast failure, and it isn't any
of the 258 reported ones:

```
dark:  1 real near-miss — --ink-3 (rgb(130,142,151)) on --accent-soft (rgb(21,42,56)),
       ratio 4.41, needs 4.5. 0.09 short. Not in the static detector's output at all.
```

**Light mode has a real, previously-unreported defect the static pass never surfaced,** buried
under its own noise: the same real-browser WCAG sweep against `color-scheme: light` found **225
genuine failures**, none of them coincidentally matching any of the 258 static findings above
(different colors entirely — the static pass's light-mode noise used dark-theme hexes paired with
`#ffffff`; the real light-mode failures use light-theme's own `--ink-3`/`--unmeas` tokens against
light-theme's own surfaces):

| Real color pair (light theme, both tokens genuine) | Ratio | Needed | Count |
|---|---|---|---|
| `--ink-3` `rgb(108,118,126)` on `--surface` `rgb(248,249,250)` | 4.40 | 4.5 | 144 |
| `--ink-3` `rgb(108,118,126)` on `--paper` `rgb(238,240,242)` | 4.06 | 4.5 | 56 |
| `--unmeas` `rgb(176,126,20)` on `--surface` `rgb(248,249,250)` | ~3.15–3.2 | 4.5 | 19 |
| `--unmeas` `rgb(176,126,20)` on `--paper` `rgb(238,240,242)` | ~3.15–3.2 | 4.5 | 3 |
| (3 further one-off pairs, same tokens, minor variants) | 3.8–4.4 | 4.5 | 3 |

All 225 are near-misses (worst measured: 3.15:1, none below 3.0), not gross failures — `--ink-3`
captions/labels/breadcrumb numerals across the whole light theme sit ~0.1–0.4 short of AA, and the
`--unmeas` amber verdict token used as bold 11.5px text (not large enough to qualify for the 3.0
large-text threshold) sits further short at ~3.15–3.2:1. This is a real, minor, systemic light-mode
contrast shortfall on this page. Neither the static detector (buried it under 258 false hits using
the wrong theme's colors) nor the original render pass (asserts nothing about text-color contrast
at all — see the retraction above) had found it before this pass.

Reproduce: `python scripts/render_pass.py` does not run this check; it was written as a one-off
Playwright script for this pass (`checked = document.querySelectorAll('body *')` with direct
text, WCAG luminance formula, `bgFor()` walking ancestors for the first opaque
`background-color`, evaluated once per `color_scheme`). Not currently committed as a reusable
script — worth promoting into `scripts/` if contrast checking is wanted as a standing gate.

**What actually caused the static tool's 196 `#000000` findings, mechanically:** not conclusively
traced, and not asserted as more than a lead this time. `css-cascade.mjs:236` seeds every
element's `color` from `STATIC_DEFAULT_STYLE = { color: 'rgb(0, 0, 0)', ... }` — the CSS spec
initial value — before inheritance is applied, so wherever inheritance from `body`'s
`color:var(--ink)` fails to reach a descendant, black is exactly what falls out. A same-page SVG
`<text fill="…">` repro (this page has 151 `<text>` elements, and SVG paints via `fill`, not
`color`) did not reproduce the finding in isolation, so that specific theory is ruled out, not
confirmed. Left open rather than re-guessed a third time.

## What the 59 static rules caught that the render pass (2026-08-22) did not

- `side-tab` (5×) — an AI-slop visual tell (`border-left:3px solid var(--accent)` on rounded
  cards) the render pass never looked for; it only checked marks/overlap/scroll/tokens/reduced
  motion. Not evaluated for genuineness beyond confirming the source line matches; not obviously
  a defect (a left accent border is a legitimate design choice, not automatically wrong), but it
  is a check the render pass structurally does not run.
- `undersized-ui-text` / `tiny-text` / `all-caps-body` / `cramped-padding` /
  `hero-eyebrow-chip` / `wide-tracking` — typography/spacing heuristics with no render-pass
  analogue. Not independently verified this pass; flagged for a follow-up rather than reported as
  either confirmed or dismissed.
- Static analysis needs **no browser and no render loop** — it ran in under a second once the
  parser deps were installed, versus the render pass's six-session blocker on `claude-in-chrome`
  before it found a working path via Playwright.

## What the render pass caught that the static 59-rule detector structurally cannot

- **Defect 1 (render-pass doc) — the legend promises an amber "5 started, no outcome recorded"
  bar and the figure never draws one.** No rule in the 59-rule registry
  (`ai-color-palette`, `low-contrast`, … `wide-tracking`) checks whether a legend swatch has a
  corresponding mark. That is a **semantic/data-correctness** claim specific to this figure's own
  caption — a generic anti-pattern scanner has no model of what "one bar per recorded attempt"
  means and cannot check a page's claims against its own drawing. Only reading the figure (or its
  generator, `scripts/build_figure_lastwrite.py`) catches this.
- **Defect 2 (render-pass doc) — the page scrolls sideways at a 700px viewport.** The static-HTML
  engine takes no `--viewport` argument (`--viewport` only applies to URL/Puppeteer scans per
  `detect.mjs --help`) and this run used the default HTML-file code path, which does not lay out
  the page at any width. `docs/artifacts/agent-factory.html` was scanned once, unconditioned on
  viewport, and produced zero overflow-related findings (`clipped-overflow-container`,
  `body-text-viewport-edge`, `first-viewport-column-overflow` are all in the 59-rule registry but
  none fired) — because the static path never lays the page out narrow enough to trigger them.
  Confirming that would need the Puppeteer URL path (`npx impeccable detect file://… --viewport
  700x844`), not installed this pass (would need `npm install puppeteer`, a much heavier
  dependency than the four parser packages above — not pulled in, out of scope for "needs no
  browser").
- The connector-through-caption text overlap the render pass logged as *"seen but not measured"*
  in the retired-agent diagram: `text-occlusion` exists in the 59-rule registry but lives in the
  browser-only engine (`detect-antipatterns-browser.js`), not the static one this pass ran — so it
  was in scope for neither instrument this run.

## Net

All three directions are real, once checked. The static detector is fast, browser-free, and
caught a real AI-slop tell the render pass never checks for — but on this file its dominant
output (258 of 313 findings) is entirely noise from resolving this page's two-theme token
stylesheet inconsistently, confirmed (not inferred) by opening the real file in a real browser and
finding zero of the disputed pairs actually paint. The render pass caught a semantic defect
(missing legend bar) and a layout defect (700px overflow) that a rule-based scanner has no way to
express, and asserts nothing about text contrast at all. And the real-browser check run for this
pass found a fourth thing neither prior instrument reported: a genuine, minor, light-theme-only
contrast shortfall (225 near-misses, `--ink-3` captions and the `--unmeas` verdict token against
light surfaces, worst 3.15:1 against a 4.5 requirement) that the static detector's own noise had
buried. Neither instrument, alone, is "impeccable's detector would have caught these earlier" in
the way the render-pass doc speculated — it would not have caught either of its own two prior
defects, and its headline finding on this file was net-negative signal until checked against a
real render. The one real defect it correctly flagged (`side-tab`) came with 257 red herrings
attached to the same rule category.
