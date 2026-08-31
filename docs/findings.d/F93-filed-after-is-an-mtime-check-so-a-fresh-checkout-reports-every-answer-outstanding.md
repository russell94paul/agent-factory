### F93 — `outstanding()["filed_after"]` compares file mtimes, so any fresh checkout reports every research answer outstanding, and the test that would catch it asks a weaker question than the code

Found by running the suite from a newly created worktree during the bootstrap wave. Not a
regression — the defect is latent in the primary and invisible there because its mtimes are old.

## What a fresh checkout does to an mtime comparison

`git worktree add` (and `git clone`, and any CI checkout) writes every file at once, in whatever
order it walks the tree. Measured in `.worktrees/bootstrap-wave`, seconds after creation:

```
SYNTHESIS.md   2026-08-31 04:52:31.012247
R1-answer...   2026-08-31 04:52:31.017525      <- 5 ms later
R10-answer...  2026-08-31 04:52:31.021271
R11-answer...  2026-08-31 04:52:31.024587
```

Every answer is therefore "filed after the synthesis was last written", by milliseconds of write
ordering. `filed_after` returned **all 18 ids**; in the primary checkout the same call returns
`[]`. Nothing about the repository's content differs between the two — only the timestamps a
checkout happened to assign.

- **BELIEVED** — `outstanding()` reports research answers the synthesis has not banked, so a red
  `test_synthesis_current.py` means someone must go and reconcile something.

- **ACTUALLY** — it reports that in the primary, and reports *everything* anywhere else.
  `outstanding()` has two halves (`factory/synthesis.py:65-86`): `never_mentioned`, a real content
  check over `SYNTHESIS.md`, and `filed_after`, a modification-time comparison. The module
  docstring already names mtime as fragile — *"any write to SYNTHESIS.md clears it for every id,
  so a partial reconciliation marks the whole set banked"* — but the failure runs the other way
  too, and harder: a checkout that writes the answers last marks the whole set unbanked.

  ⚠ **`agent-factory` has no CI** (`.github/` does not exist), which is the only reason this has
  never fired. The first CI run on a clean clone would open with 18 phantom outstanding answers.

- **MEASURED BY** — the same call from both checkouts of the same commit, result predicted before
  it ran:

  ```bash
  python -c "from factory import synthesis; print(synthesis.outstanding())"
  ```
  ```
  primary    never_mentioned: []   filed_after: []
  worktree   never_mentioned: []   filed_after: ['R1','R2',...,'R19']    # 18 ids
  ```

  Corroborated by the mtimes above, and by `tests/test_synthesis_current.py::
  test_the_prompt_names_the_actual_gap` passing in the primary and failing in the worktree with no
  code change between them.

- **AFFECTS** — **every lane**, and that is the literal answer rather than a shrug: a lane *is* a
  worktree (`factory/worktrees.py:38`), and a worktree is exactly the fresh checkout this misfires
  in. Any lane that renders the research tab or is handed `session_prompt()` is told to reconcile
  eighteen answers that are already banked. Code: `factory/synthesis.py`,
  `tests/test_synthesis_current.py`, and `scripts/local_tracker.py`, which renders the
  reconciliation prompt.

## ⭐ And the test asks a different question from the code it tests

Worth separating, because it is the reason this was invisible rather than merely rare.
`test_the_prompt_names_the_actual_gap` computes:

```python
gap = unsynthesised()          # never_mentioned ONLY
text = prompt()                # driven by outstanding() = never_mentioned + filed_after
if not gap:
    assert "Nothing to reconcile" in text
```

`prompt()` stopped using `unsynthesised()` on 2026-08-29 — `synthesis.py:68-73` records exactly
that change, and why:

> **Both must drive the prompt, and until 2026-08-29 only the first did.** `prompt()` used
> `unsynthesised()` alone … an `or`, so the *stronger* check was consulted only when the weaker one
> was already satisfied.

The code was fixed. **The test was not.** It still measures the old, weaker half, so it can only
notice a disagreement when `filed_after` is empty — which, in the primary, it always is. A test
whose model of the answer is one revision behind the code's cannot report the difference: this is
the F86 shape (*a validator that only inspects what it parsed*) applied to a function boundary
rather than a parser.

- **KIND** — DESIGN

- **CHANGES** — none. Recorded before choosing a remedy, because there are three and they are not
  equivalent. **(a)** Drop `filed_after` and keep only the content check — honest, loses a real
  signal. **(b)** Replace mtime with the git commit time of each path (`git log -1 --format=%ct`),
  which survives any checkout but costs a subprocess per answer and is wrong for uncommitted work.
  **(c)** Record the reconciliation point *inside* `SYNTHESIS.md` — a banked-as-of marker per id —
  so the claim is data rather than an inference from the filesystem. (c) is the only one that
  makes the check mean what it says, and it is the largest. Whichever is chosen, the test must be
  moved onto `outstanding()` so it asks the same question as the code.

- **STATUS** — OPEN
