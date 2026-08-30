# Findings ledger — corrected premises, so no lane pays for the same mistake twice

**Read this before starting a lane. Append to it before closing one.**

Parallel lanes fail in a specific way: two sessions independently inherit the same wrong premise
and both build on it. That is not hypothetical here — R1 named Prefect as the cause of the
false-`succeeded` defect, the claim was carried into R3 as an entire question, and nobody checked
it until a one-line grep did. Every entry below is a premise that looked true and was not.

## What belongs here

Only **corrections to things another lane would otherwise believe.** Not progress, not decisions,
not what you built — boot prompts and `docs/evidence/` already carry those. The test is: *would a
session in another lane get this wrong without being told?*

Every entry carries four things, and an entry missing any of them is not a finding:

| Field | Why it is mandatory |
|---|---|
| **BELIEVED** | the premise as another lane would state it, in their words |
| **ACTUALLY** | what is true |
| **MEASURED BY** | the discriminating test, so the reader can re-run it rather than trust you |
| **AFFECTS** | lanes, gates or files that inherit the premise |

⭐ **Closing a lane with nothing to add is itself an entry.** Write `NOTHING TO REPORT` with the
date and lane. Silence has to mean "checked and found nothing", not "nobody looked" — the same
distinction between ZERO and NOT-RECORDED that the contract's four verdicts exist to protect.

---

## 2026-08-22 · session: evaluator isolation + render loop

### F1 — The false `succeeded` has nothing to do with Prefect

- **BELIEVED** — "Prefect's final-state rules let a parent flow return COMPLETED over failed
  children" (R1, then carried into R3 as a whole question).
- **ACTUALLY** — the build plane at `:8765` is a bespoke engine that **does not import Prefect**.
  The verdict is computed from a last-write-wins per-stage status field, so a stage that failed
  100 times and succeeded once contributes nothing to `any_failed`.
- **MEASURED BY** — `grep -n "import prefect" orchestrator/pipelines.py` → no hits, at `3da40f6`.
  One grep. Full write-up in `docs/evidence/false-succeeded-mechanism.md`.
- **AFFECTS** — control-plane lane (`truthful`, `from-history`), and any Prefect-idiom fix. R2's
  recommended primitives are **not available to us** and each must be built; see
  `docs/research/answers/R2-followup.md`.

### F2 — The 5 unmeasured attempts cannot be placed in the sequence

- **BELIEVED** — the 5 `stage_started` events with no outcome can be interleaved into the run
  order, since 115 starts − 110 terminals = 5.
- **ACTUALLY** — walking the log and pairing each start to a following terminal locates **24**
  unterminated starts, not 5. Terminals do not reliably follow their own start, so any placement
  is fabrication. They are drawn past a divider, in no order, and the figure says so.
- **MEASURED BY** — walk `pipe_4ba17e16.json` events for `trigger-run` in order, incrementing on
  `stage_started` and clearing on a terminal; count the starts cleared by another start → 24.
- **AFFECTS** — anything reasoning about attempt ordering, retry counts, or per-attempt cost. The
  earlier version of this inference reported 82 failures where the counters say 100.

### F3 — `grain_confirmed` is not a field, and adding it breaks every blueprint load

- **BELIEVED** — settle the grain question by setting `grain_confirmed` in
  `blueprints/windsorai_client_a.yaml`.
- **ACTUALLY** — `ConnectorTarget` has no such field and `targets.load_target` raises on unknown
  keys by design. Adding it to the YAML breaks every load until the dataclass gains the field.
- **MEASURED BY** — `_ALLOWED = set(ConnectorTarget.__dataclass_fields__)` in `factory/targets.py`;
  `grain_confirmed` is absent.
- **AFFECTS** — grain lane. Add the field to `ConnectorTarget` in the same commit.

### F4 — The loop gates are measuring a three-month-old history

- **BELIEVED** — "3 of 14 runs finished", "a stage fails 6.1× more than it succeeds" and "4
  orphans" describe the system now.
- **ACTUALLY** — all 14 audit files date from **2026-05-26 to 05-28**. Nothing has run in the
  orchestrator since, and it is not currently running (nothing listening on `:8765`). The numbers
  are true of a history that stopped three months ago; the gates do not say so.
- **MEASURED BY** — `ls -la orchestrator/data/audits/*.json`; `netstat -ano | grep :8765` → empty.
- **AFFECTS** — every loop and judgement gate, and any claim that a control "fixed" a rate. Fixing
  a control changes nothing measurable until runs happen again. Making the gates carry the age of
  their evidence is unclaimed work.

### F5 — Instruments in this repo have produced three confident false results in one session

- **BELIEVED** — a probe that returns a specific number has measured something.
- **ACTUALLY** — three separate false results, all confident, all in one day:
  1. the render probe measured across **both** svgs in `#failed` → *"119 marks, 1 inside the band,
     min gap −201px"*;
  2. it reported a text collision on `--max-turns` × `--max-budget-usd` — false, because
     `getBoundingClientRect()` on a **wrapped inline** returns the union of its line boxes;
  3. the tracker test used `html.escape()` with default `quote=True`, turning `impeccable's` into
     `impeccable&#x27;s`, and reported the `chain` gate missing from a page it was plainly on.
- **MEASURED BY** — each was caught by checking the finding against the DOM before reporting it.
  None would have been caught by re-running the probe.
- **AFFECTS** — every lane. Before reporting a defect, verify it against the thing itself. The
  readiness gate for this already exists in spirit: *a probe must not be able to match its own
  source.*

### F6 — `claude-in-chrome` is not the only way to render, and is not worth waiting for

- **BELIEVED** — the render pass is blocked until the Chrome extension connects.
- **ACTUALLY** — Playwright drives the same installed Chrome with none of that chain in the path.
  `pip install playwright`, then `python scripts/render_pass.py`. The extension chain is healthy
  at every inspectable link (installed, enabled, right account, native host registered and
  spawnable, no policy) and `list_connected_browsers` still returns `[]`.
- **MEASURED BY** — `docs/evidence/render-pass-2026-08-22.md`, which tabulates every link.
- **AFFECTS** — artifact lane, and anyone tempted to spend another session on the extension.

### F7 — I fed R6 a false constraint, and it changed the answer

- **BELIEVED** — stated as fact in `docs/research/R6-automation-and-alerting.md`: *"there is
  currently no runner budget or appetite for one."* I wrote it as a constraint on the question.
- **ACTUALLY** — the same GitHub org already runs three Actions workflows in
  `prefect-connectors` (`ci.yml`, `quality-gate.yml`, `branch-sync.yml`). Actions is available and
  in daily use. `agent-factory` simply has no `.github/workflows` directory, which is an absence,
  not a constraint.
- **MEASURED BY** — `ls prefect-connectors/.github/workflows/` → three files. One command.
- **AFFECTS** — every lane, and R6's answer itself. R6 explicitly deferred *"a full CI on every
  push"* on the strength of my sentence, and instead ranked a nightly scheduled check first. Read
  its Q1 with that correction in hand: CI-on-push may well be the right first move after all, and
  the honest position is that R6 was never asked the real question.

⭐ **This is the F1 pattern, committed by me, inside a prompt whose own Method note warns against
it.** *An object named by a ticket, boot prompt or handoff is a hypothesis, not a finding.* A
constraint asserted in a research prompt is exactly that kind of object, and I asserted one I had
not checked — while telling the reader to check everything I asserted. Before writing a constraint
into a prompt, measure it; a research pass optimises against the world you describe, not the one
you have.

### F8 — Two servers can hold port 8099, and you verify against the stale one

- **BELIEVED** — killing the listener on 8099 and starting a new one means the page you then
  fetch is the page you just built.
- **ACTUALLY** — `local_tracker.py` sets `socketserver.TCPServer.allow_reuse_address = True`, so a
  second process binds the same port happily. `netstat` showed **two** LISTENING entries and curl
  was served by the older one. Every "restart and check" in this session could silently have
  verified against pre-change code.
- **MEASURED BY** — `netstat -ano -p TCP | grep :8099 | grep LISTENING` → two rows, two PIDs. The
  tell was a freshly-started server whose log file stayed empty while the page still answered 200.
- **AFTER** — kill **every** PID on the port, confirm the count is 0, then start one and confirm
  it is 1. Do not kill `head -1`.
- **AFFECTS** — every lane. Any local service verified by restart-then-fetch, and specifically
  anyone trusting a tracker page to reflect the code they just edited.

### F9 — ast.parse does not catch every SyntaxError; compile() does

- **BELIEVED** — `ast.parse(src)` passing means a patched module is syntactically valid.
- **ACTUALLY** — it builds the tree only. Symbol-table errors are invisible to it: `global X`
  appearing after X is used elsewhere in the same function parses cleanly and fails at compile.
  A patch script printed "wired and parses" and the server then refused to start.
- **MEASURED BY** — on the same source, `ast.parse(t)` succeeded and `compile(t, "f.py", "exec")`
  raised `SyntaxError: name '_HANDOFF_NOTE' is used prior to global declaration`.
- **AFFECTS** — every lane, and any patch-then-verify loop. Use `compile(src, name, "exec")`:
  same cost, catches strictly more.

### F10 — Windows Terminal eats semicolons in the command you hand it

- **BELIEVED** — `wt new-tab ... powershell -Command "Set-Location X; claude Y"` runs both halves.
- **ACTUALLY** — `;` is **wt's own subcommand separator**. It splits the invocation there and
  tries to launch the remainder as a program. The observable result is a tab that opens in the
  right directory and does nothing else, plus
  `error 2147942402 (0x80070002) ... The system cannot find the file specified`.
- **MEASURED BY** — Paul's first real click. Every prior test was a dry run that inspected the
  command without executing it, so nothing had exercised wt's parsing.
- **AFFECTS** — every lane, since any of them can launch a terminal. Put **no semicolons** in the `-Command` payload;
  use `--startingDirectory` for the cwd. And note the lesson under it: a dry run proves the
  command you built, never the thing that will parse it.

## 2026-08-22 · session: artifact lane — gate `chain`, impeccable's detector

### F50 — `node scripts/detect.mjs` silently under-counts to 1 finding without four npm packages

- **BELIEVED** — running impeccable's bundled detector directly
  (`node ~/.claude/skills/impeccable/scripts/detect.mjs <file> --json`) runs the real 59-rule pass.
- **ACTUALLY** — the static-HTML engine needs `htmlparser2`, `css-select`, `css-tree`, `domutils`,
  none of which ship with the skill. Without them it falls back to regex matching and prints
  `DEGRADED — HTML parser modules unavailable` **to stderr only** — stdout still returns
  well-formed JSON, just 1 finding instead of 313 on the same file, and the exit code is non-zero
  either way so it doesn't distinguish the two modes.
- **MEASURED BY** — `node scripts/detect.mjs docs/artifacts/agent-factory.html --json` → 1 finding,
  stderr shows `DEGRADED`. After `cd ~/.claude/skills/impeccable && npm install htmlparser2
  css-select css-tree domutils --no-save` → 313 findings, stderr empty.
- **AFFECTS** — every lane that runs impeccable's detector on this machine for the first time.
  Install the four packages first, or a "clean" result is actually an unmeasured one. Also: `npx
  impeccable detect` sidesteps the missing-deps problem but resolves the **npm-published** version
  (3.6.0 observed) rather than the **locally installed skill** (4.1.1, whose registry file —
  `scripts/detector/registry/antipatterns.mjs`, 59 `id:` entries — is what "59 deterministic
  detector rules" actually refers to). The two happened to match byte-for-byte on this file; don't
  assume they stay in sync.

### F51 — a bulk `low-contrast` finding count is not evidence until checked in a real browser — proven both ways, including on my own draft

- **BELIEVED** (my own first draft of `docs/evidence/impeccable-detector-pass-2026-08-22.md`) —
  cross-referencing 56 of 258 `low-contrast` findings against the page's CSS token definitions and
  finding them cross-theme-impossible was enough to call **251 of 258 (97%)** proven false
  positives, corroborated by a render-pass check that (it turned out, on inspection) never reads
  any element's text color at all.
- **ACTUALLY** — an independent opus `reviewer` pass caught the overclaim: the grep covered only
  56 rows: 195 of the 258 (the `#000000 on #141b21` rows) were simultaneously claimed "proven" in
  one paragraph and "not dismissed, recorded as open" two paragraphs later — a direct
  self-contradiction that shipped uncaught. Correcting it required going further than the original
  grep-only proof: opening the real file in the real, installed Chrome via Playwright and sweeping
  every element's actual computed color/background across both themes. That found: **zero** of the
  258 static findings correspond to anything a real browser paints (dark mode: 1 genuine near-miss
  at 4.41:1, not among the 258; light mode: 225 genuine near-misses, none of them the pairs the
  static detector reported — a real, different, previously-unreported defect the static noise had
  buried).
- **MEASURED BY** — `docs/evidence/impeccable-detector-pass-2026-08-22.md`, "⭐ The low-contrast
  finding is ~100% noise" section, which keeps the retracted claim visible with a revision note
  rather than silently overwriting it.
- **AFFECTS** — every lane, and reinforces F5. A grep against source that proves *some* findings
  false does not license folding *adjacent, unproven* findings into the same verdict — and a cited
  "corroborating instrument" must be checked to actually measure the thing it's cited for (F5's
  html.escape() and cross-both-svgs failures were exactly this: an instrument assumed to see
  something it structurally could not). The fix that actually worked was cheaper than the
  reverse-engineering that failed twice: don't trace a third-party static tool's internals to
  defend a claim — open the real artifact in a real browser and measure the disputed property
  directly.

### F52 — `scripts/render_pass.py`'s all-PASS does not mean the page's text contrast is fine

- **BELIEVED** — a lane reading `render-pass-2026-08-22.md` or a fresh `python
  scripts/render_pass.py` all-PASS could reasonably conclude the artifact's contrast is clean —
  the doc even reports specific token hex values under "Verdict tokens hold".
- **ACTUALLY** — `render_pass.py` asserts on exactly three named CSS variables
  (`--fail`/`--pass`/`--unmeas`) and the body background; it contains no general per-element WCAG
  contrast check and never reads `getComputedStyle(el).color` for any element other than
  `document.body`. A real sweep (this session, Playwright, both `color-scheme`s, every element
  with direct text) found the page's light theme has **225 genuine near-miss contrast failures**
  (`--ink-3` captions/labels at ~4.06–4.44:1 against light surfaces, the `--unmeas` amber verdict
  token at ~3.15–3.2:1 as bold 11.5px text) — all against a 4.5:1 requirement neither prior
  instrument checked.
- **MEASURED BY** — `docs/evidence/impeccable-detector-pass-2026-08-22.md`, same section as F51;
  `grep -n "body-fg\|getComputedStyle" scripts/render_pass.py` shows the one uncollected read.
- **AFFECTS** — every lane treating render-pass PASS as a general design-quality signal. It checks
  what it checks (marks/legend/gaps/reveal/overlap/scroll/named-token-values/reduced-motion) and
  nothing else; contrast is not one of the things it checks. Not fixed this pass — recorded as an
  open, real, minor defect. The one-off contrast-sweep script used to find it is not currently
  committed; worth promoting into `scripts/` if a standing contrast gate is wanted.

### F53 — the fix for F50 is itself unreproducible, one level up: `node_modules` is untracked and machine-local

- **BELIEVED** (implicit in how F50 was fixed) — running `npm install htmlparser2 css-select
  css-tree domutils --no-save` in `~/.claude/skills/impeccable` once settles the question; the
  313-finding detector pass and the follow-up real-browser contrast sweep are both reproducible
  from here.
- **ACTUALLY** — `cd ~/.claude/skills/impeccable && git status --short node_modules` returns `??
  node_modules/` — untracked, not gitignored either, in the same personal skills checkout (its own
  git repo, outside `agent-factory`) that F50's SKILL.md precedence fix already lives in. This is
  the exact same class of gap this lane already spent effort closing for the `chain` gate's
  evidence (see `docs/evidence/impeccable-detector-pass-2026-08-22.md`'s reproducibility note) —
  one level up. Reinstalling the skill, or running any of this on a different machine, silently
  reverts the detector to the F50 degraded mode with no record of why the counts changed.
- **MEASURED BY** — `git status --short node_modules` inside `~/.claude/skills/impeccable`.
- **AFFECTS** — every lane relying on `docs/evidence/impeccable-detector-pass-2026-08-22.md`'s
  313-finding count or its real-browser contrast sweep being reproducible as stated. Not fixed
  this pass (no package.json exists in that skill directory to pin the versions installed, and
  creating one is a change to a shared personal tool outside this repo's scope, not something to
  do unprompted). Flagged so the next lane doesn't assume `npm install` once was enough.
