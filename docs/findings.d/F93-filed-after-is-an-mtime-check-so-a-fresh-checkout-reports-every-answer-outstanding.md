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

- **CHANGES** — **none of the three remedies first named.** All three inherited the original
  error, which is that `filed_after` used **time as a proxy for change**: (a) dropping the check
  loses a real signal, (b) git commit times survive a clone but are wrong for uncommitted work,
  and (c) a banked-as-of marker is still a timestamp, still answering *when* rather than *what*.

  ⭐ **The remedy is to bank by CONTENT.** `SYNTHESIS.md` now carries a machine-written block
  recording each answer's sha256 at the moment it was folded in, and the check compares hashes:

  ```
  never_banked   no hash recorded            -> the record has not taken it in at all
  stale          recorded hash != current    -> the record describes an earlier version
  ```

  Not a new idea here — the **third** application of one that already works. `evals/MANIFEST.sha256`
  pins the corpus and verifies on load; `registry.py:104-113` hashes a workflow's own text as its
  version, on the stated ground that *"a `SKILL.md` edited between two runs is a different
  workflow."* An answer edited after the synthesis read it is a different answer.

  ⭐ **It also closes the defect the old docstring called unacceptable in itself.** An mtime is one
  number for the whole file, so *any* write cleared the check for *every* id — a partial
  reconciliation marked the answers it never opened as banked. The 2026-08-29 correction recorded
  that and could only answer it with a rule (*"a partial write must never happen"*). Hashes are
  per answer, so a partial pass banks only what it stamps. **The rule became a property.**

  ⚠ **And the new mechanism opens a gap the old one did not have.** mtime was blunt on purpose: it
  could not be satisfied by writing an id anywhere, only by editing the file after the answer
  landed. A hash *can* be stamped by something that never read the answer. So `outstanding()`
  gained a third key, `banked_but_unmentioned`, reporting any banked id the prose never names.

  ⛔ **That cross-check shipped inert on the first attempt, and its own test caught it.** `bank()`
  writes the ids into the block, and `synthesised()` scans the file for `R\d+` — so banking an
  answer made it "mentioned" and the cross-check could never fire. `_prose()` now strips the block
  before scanning. An inert control, inside the control added to prevent one.

  `unreconciled()` keeps its name and signature, so `dispatch.py:394` and `handoff.py:201` improve
  without changing. The tests moved onto `outstanding()` — they had been asking a weaker question
  than the code since 2026-08-29, which is why nobody saw this.

  **Measured:** every answer's mtime moved ahead of the synthesis, and the record stays clean; a
  genuine one-line edit to R1 reports `stale: ['R1']`; reverting it clears. The suite in a fresh
  worktree went **16 failures to 15** — the same 15 as the primary. The worktree and the primary
  now agree, which is the whole of what this finding said they did not.

- **STATUS** — ADOPTED
