# `findings.d/` — one file per finding

**Write new findings here, as a new file. Do not append to `docs/findings.md`.**

`load()` reads this directory *and* `../findings.md`, so the existing entries still count and
nothing already on a lane branch breaks. New entries belong here.

## Why a directory

On 2026-08-22 three lanes appended to `findings.md` from three isolated worktrees. Each read F10
as the last id and took the next number — correctly, independently, and incompatibly. Three F11s,
three F12s, and a merge that would have silently destroyed two of each, in the file whose entire
job is stopping a lane from paying twice for the same mistake.

Worktree isolation is a feature, so the ledger cannot be one mutable file. Separate paths cannot
conflict. Ids still matter — they are how `[[F20]]` resolves — but they are a naming convention
now, not a lock on a shared file. Blocks: control-plane F20-F29, certify F30-F39, judgement
F40-F49, artifact F50-F59, grain F60-F69, non-lane sessions F70+.

Filename: `<id>-<slug>.md`. `ls docs/findings.d/` is the index.

## The four mandatory fields

Unchanged, and still the whole discipline. Without **MEASURED BY** a finding is an opinion;
without **AFFECTS** nobody downstream is shown it.

| Field | Why |
|---|---|
| **BELIEVED** | the premise as another lane would state it, in their words |
| **ACTUALLY** | what is true |
| **MEASURED BY** | the discriminating test, so a reader can re-run it rather than trust you |
| **AFFECTS** | lanes, gates or files that inherit the premise |

## The three optional fields — for findings that outlive their fix

Most findings are corrections: read it, fix it, done. Some are not. A correction is spent once
it has been read; a **design consequence is not spent until it is built or deliberately refused**,
and the ledger had no way to tell those apart — so they were filed, admired, and never acted on.

- **KIND** — `CORRECTION` (a premise was wrong) · `INSTRUMENT` (a tool lied, or could not see —
  changes what a measurement is worth) · `DESIGN` (the system should be built differently) ·
  `AGENT-DESIGN` (the agents, lanes or harness should work differently) · `PROCESS` (how we work
  should change).
- **CHANGES** — **mandatory when KIND is DESIGN or AGENT-DESIGN.** What must be built differently,
  and where it lands. A design consequence that does not name its change is an observation
  wearing a decision's clothes, and `malformed()` will reject it.
- **STATUS** — `OPEN` · `ADOPTED` · `REJECTED` · `SUPERSEDED`. A design finding with no decision
  is an insight nobody ever ruled on. Silence has to mean *decided*, the same way
  `NOTHING TO REPORT` has to mean *checked*.

`design_debt()` lists every DESIGN/AGENT-DESIGN finding still OPEN. **That is the list that should
shrink.** `by_kind()` groups the whole ledger. Unclassified entries are not an error — the four
mandatory fields are the discipline, KIND is the refinement.

⭐ Closing a lane with nothing to add is still itself an entry: write `NOTHING TO REPORT` with the
date and lane. Silence must mean checked, not unlooked-at.
