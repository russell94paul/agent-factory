### F84 — "2,041 lines, zero consumers" was 574, and the grep that said otherwise could not see the only consumer

The headline measurement in `boot-prompts/run-03-the-missing-middle-2026-08-30.md` §0 — the one it
says "should decide what gets built next" — was produced by a command that is structurally blind to
the import form its only consumer uses.

## The claim

> | `factory/dispatch.py` | 441 | **0** |
> | `factory/claims.py` | 390 | **0** |
> | `factory/presets.py` | 309 | **0** |
> | `factory/runs.py` | 289 | **0** |
> | `factory/deploy.py` | 265 | **0** |
> | `factory/launch.py` | 217 | **0** |
> | `factory/worktrees.py` | 130 | **0** |
>
> ⭐ **Just over 2,000 lines of working, tested machinery that nothing calls.**

Its regeneration command, quoted in the same section:

```bash
grep -rln "from factory.$f import\|from .$f import" --include=*.py factory/ scripts/
```

## What it cannot see

`scripts/local_tracker.py` — the only production consumer of any of them — imports **every**
factory module as `from factory import <name> as <alias>`:

```python
from factory import claims as claimlib      # 29 call sites
from factory import dispatch as dispatchlib # + `as disp`, 10 call sites between them
from factory import launch as launchlib     #  6 call sites
from factory import runs as runlib          #  5 call sites
from factory import worktrees as wt         #  4 call sites
```

Neither alternative in that grep matches that line. **The instrument returned zero for five modules
with 54 call sites between them.**

## Measured

Against the committed tree at `3e33a1a`, before this session added anything:

```bash
# in a clean export of HEAD, so the measurement is not contaminated by the working tree:
TMP=$(mktemp -d); git archive HEAD factory scripts | tar -x -C "$TMP"
for f in dispatch claims presets runs deploy launch worktrees blueprint; do
  printf "%-10s %5s  " $f $(wc -l < "$TMP/factory/$f.py")
  grep -rlE "from (factory|)\.?${f} import|from factory import [^#]*\b${f}\b" --include=*.py \
    "$TMP/factory/" "$TMP/scripts/" | grep -v "factory/$f.py" | grep -v demo | sed "s|$TMP/||" | tr '\n' ' '
  echo
done; rm -rf "$TMP"
```

| module | lines | boot-prompt grep | actually | consumer |
|---|---|---|---|---|
| `dispatch.py` | 441 | 0 | **1** | `local_tracker.py` |
| `claims.py` | 390 | 0 | **1** | `local_tracker.py` |
| `runs.py` | 289 | 0 | **1** | `local_tracker.py` |
| `launch.py` | 217 | 0 | **1** | `local_tracker.py` |
| `worktrees.py` | 130 | 0 | **1** | `local_tracker.py` |
| `presets.py` | 309 | 0 | **0** ✅ | — |
| `deploy.py` | 265 | 0 | **0** ✅ | — |

**Unwired: 574 lines, not 2,041.** The figure was wrong by 3.5×.

## Why the conclusion survives, and gets better

RUN-03 was still the right thing to build, and the corrected number says so more sharply than the
inflated one did. The two genuinely unwired modules are **exactly the two on the execution path**:

- `presets.py` — choose a configuration for a ticket
- `deploy.py` — run an agent under that configuration, bounded

Every module that *was* wired is a **reporting** surface the tracker renders: which lanes are
claimed, which research is undispatched, what a lane spent, whether you may press start. So the
estate had a complete reporting layer and no execution layer, and the reporting layer was reporting
on work that no code in this repository could start.

⭐ That is a cleaner statement of "the missing middle" than *2,041 lines nothing calls* ever was —
and it explains why the tracker looked healthy the whole time. **The inflated number made the
problem sound like neglect. The real number shows it was a shape.**

## The rule

⛔ **A code-search zero without a positive control is NOT-VISIBLE, not ABSENT.** Already written
down in this repo's own rules — against `gh api search/code`, which returned 0 for a string
verified to exist. The same failure recurred four hours later in a local `grep`, in the document
that quotes the rule.

The positive control costs one line and would have caught it: point the same command at a module
you *know* has a consumer, and check it says so.

```bash
# does this grep form find ANY consumer at all?
grep -rln "from factory.readiness import" --include=*.py scripts/
# -> scripts/build_plan.py, scripts/build_tracker.py, scripts/local_tracker.py   ✅ instrument live
```

That control passes — which is the subtle part. The grep is not broken; it is **narrow**, and its
narrowness aligns exactly with one import style. A control that proves the instrument works in
general does not prove it can see the specific thing you are counting. The population has to be
enumerated in the instrument's own terms.

See also `F80` (the board measuring the wrong branch) and `F81` (three probes that could not see).
This is the fourth blind instrument in nine days, and the second where the blindness was invisible
because the instrument returned a plausible number rather than an error.

## The ledger fields

Added 2026-08-31 when [[F86]] made this file visible to `findings.load()` for the first time. The
body above is the finding; these are the mandatory fields the parser reads.

- **BELIEVED** — `boot-prompts/run-03-the-missing-middle-2026-08-30.md` §0: *"Just over 2,000
  lines of working, tested machinery that nothing calls"* — 2,041 lines across seven modules at
  zero consumers, offered as "the single fact that should decide what gets built next".

- **ACTUALLY** — 574 lines across two modules. `dispatch`, `claims`, `runs`, `launch` and
  `worktrees` each had a consumer the whole time — `scripts/local_tracker.py`, 54 call sites
  between them — reached as `from factory import X as Y`, an import form the counting grep does
  not match. Wrong by 3.5×.

- **MEASURED BY** — the same count re-run against a clean `git archive` export of `3e33a1a`, with
  the pattern widened to the aliased import form; command and per-module results in the table
  above. The instrument's own blindness is demonstrated rather than asserted: the narrow pattern
  returns 0 for `claims.py` while `local_tracker.py` calls it 29 times.

- **AFFECTS** — every lane, because it is a rule about instruments rather than about one module:
  any session that counts callers, consumers, usages or references with a code search inherits
  it. Concretely it corrects §0 of the RUN-03 boot prompt, which is annotated in place.

- **KIND** — INSTRUMENT

- **STATUS** — ADOPTED
