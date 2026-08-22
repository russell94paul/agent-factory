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
> - **On a genuine conflict, split by domain, not by seniority.** `artifact-motion`'s
>   `references/QUALITY_GATES.md` is authoritative for anything touching motion, reduced-motion behavior, or
>   whether a figure's geometry is computed from a real measured number — `impeccable`'s detector has no
>   rule for any of that and is not a vote on it. `impeccable`'s detector is authoritative for the generic
>   UI-quality lane it actually measures — contrast, spacing, typography, AI-slop tells — where the four
>   Artifact skills state principles (rule 3, "every number carries its basis"; "seamless, not a card grid")
>   but do not run a deterministic scan.
> - **A finding from `impeccable`'s detector is a claim, not a fact, until checked against the rendered
>   page.** Its static-HTML engine does not evaluate `@media` blocks and only partially resolves CSS custom
>   properties across `:root[data-theme]` variants — a page that swaps its whole palette under
>   `prefers-color-scheme` or a `data-theme` attribute (the pattern `artifact-design` itself mandates) can
>   produce contrast findings quoting colors the browser never actually pairs. Verify a sample against the
>   source before acting on a bulk finding; don't let an uninstalled-parser degraded run (`DEGRADED — HTML
>   parser modules unavailable`, falling back to regex) stand in for the real 59-rule pass either — install
>   `htmlparser2`, `css-select`, `css-tree`, `domutils` alongside `scripts/detect.mjs` first.

</details>

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
| `low-contrast` | 258 | **~97% are a detector artifact — see below.** A handful are unresolved. |
| `undersized-ui-text` | 25 | Not independently checked this pass. |
| `all-caps-body` | 11 | Not independently checked this pass. |
| `tiny-text` | 9 | Not independently checked this pass. |
| `side-tab` | 5 | Matches source directly (`border-left:3px solid var(--accent)`) — real. |
| `cramped-padding` | 3 | Not independently checked this pass. |
| `hero-eyebrow-chip` | 1 | Not independently checked this pass. |
| `wide-tracking` | 1 | Not independently checked this pass. |

## ⭐ The low-contrast finding is dominated by a false-positive class, proven by token cross-reference

`low-contrast`'s 258 findings collapse to 10 distinct `text-color on bg-color` pairs. The two
largest, **251 of 258 (97%)**, pair a hex value that exists **only** in this page's dark-theme
token block with a hex value that exists **only** in the light-theme block:

| Snippet | Count | Text color is only… | Background color is only… |
|---|---|---|---|
| `#000000 on #141b21` | 195 | *(unresolved — see below)* | `--surface`, dark (`docs/artifacts/agent-factory.html:21,31`) |
| `#828e97 on #ffffff` | 32 | `--ink-3`, dark (`:22,32`) | `--raise`, light (`:8`) |
| `#a9b4bc on #ffffff` | 18 | `--ink-2`, dark (`:22,32`) | `--raise`, light (`:8`) |
| `#e7ecef on #ffffff` | 6 | `--ink`, dark (`:22,32`) | `--raise`, light (`:8`) |
| `#000000 on #0e1418` | 1 | *(unresolved)* | `--paper`, dark (`:21,31`) |

**A browser can never paint any of these five pairs.** `grep -n "828E97\|A9B4BC\|E7ECEF" docs/artifacts/agent-factory.html`
returns only the two dark-token definition lines (`:22`, `:32`) — those hex values are never
hand-written elsewhere, so the only way text paints `#828e97` is the dark theme being active, and
the only way a `--raise` background paints `#ffffff` is the light theme being active. One page,
one theme, one paint. The pairing is a **contradiction**, not an edge case.

The mechanism: the detector's own source documents the class. `scripts/detector/rules/checks.mjs:181-186`
— *"In jsdom mode the detector can't resolve `var(--X)` color tokens, so a dark section sitting
between the text and the body's decorative gradient is invisible to us — we end up measuring
contrast against \[the wrong] bg."* `css-cascade.mjs:34` separately states `@media` blocks are
ignored outright. Between the two, this page's `--ink`/`--ink-2`/`--ink-3` custom properties
resolve inconsistently against its `--raise`/`--surface`/`--paper` properties across the same
static pass — some elements pick up the dark declaration (`:root[data-theme="dark"]`, a plain
attribute-selector rule, not `@media`-wrapped, so it *is* read), others don't, and the two streams
get paired as if they belonged to one render.

**Corroborating instrument:** `docs/evidence/render-pass-2026-08-22.md` already rendered this
exact file with Playwright in a real dark-mode browser and reported *"Verdict tokens hold — dark:
PASS — `#E4756A` / `#4FBF89` / `#E3A93D` on `rgb(14,20,24)`."* No black text was observed there.
Two independent instruments — a real browser and a token-definition grep — agree the dark theme
renders correctly; only the static jsdom-cascade path disagrees, and it disagrees with itself
(mismatched theme streams) more than with reality.

**Not dismissed as false positives:** the remaining 7 findings, all same-theme pairs
(`#e7ecef on #6fb3d6`, `#6fb3d6 on #6fb3d6`, `#828e97 on #6fb3d6`, `#a9b4bc on #6fb3d6`,
`#e3a93d on #6fb3d6` — all dark-only tokens against `--accent`) and the `#000000` pairs above
(text color not attributable to any token, so not provably cross-theme either way). These need a
targeted browser check before either fixing or discarding them — recorded as open, not closed
either direction.

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

Both directions are real. The static detector is fast, browser-free, and caught a real AI-slop
tell the render pass never checks for — but on this file its dominant output (258 of 313
findings) is mostly noise from its own documented `var()`-resolution weakness on a two-theme
token stylesheet, discoverable only by cross-referencing the findings against the source rather
than trusting the count. The render pass caught a semantic defect (missing legend bar) and a
layout defect (700px overflow) that a rule-based scanner has no way to express. Neither
instrument, alone, is "impeccable's detector would have caught these earlier" in the way the
render-pass doc speculated — it would not have caught either defect. It caught a different,
real one.
