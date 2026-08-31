### F95 — a Claude Code hook costs a whole interpreter start on every tool call, so the second hook you register is more expensive than the first one's job

Found while adding a checkout-moved advisory, which was about to be registered as a second
`PreToolUse` hook. Measured before registering rather than after, which is the only reason it was
not registered.

## The numbers

Five invocations each, same machine, same payload, 2026-08-31:

```
python -c "pass"                     114 ms      the interpreter floor
scripts/hooks/lane-bus.py            213 ms      already registered, fires on EVERY tool call
git-tree-moved.py (standalone)       202 ms      what a second hook would have cost
```

⭐ **A hook is not a callback, it is a process.** Every tool call in every session pays a full
Python start before a single line of hook logic runs, and `lane-bus.py` — whose common case is
*"not in a lane, return 0"* — costs 213ms to decide that. Registering the advisory separately
would have taken the per-tool-call tax to roughly **415ms**, for a warning designed to fire a
handful of times a day.

- **BELIEVED** — a hook that exits early in its common case is cheap, so a second one for a
  different concern is close to free.

- **ACTUALLY** — the early exit is the cheapest part. The cost is fixed and paid up front, before
  the hook can decide it has nothing to do, and it scales with the *number of registered hooks*
  rather than with how often they fire.

- **MEASURED BY** — timing loops against each entry point, and then against the merged version:

  ```
  two separate hooks       ~415 ms   (213 + 202, projected)
  merged, import unguarded   273 ms   (+60 ms on every call — the import itself)
  merged, import gated       217 ms   (+4 ms — free)
  ```

  The middle row is the one worth keeping: folding the checker in still cost +60ms per call until
  the `importlib` load was gated behind a free substring test (`if "git " in cmd`), because the
  import was being paid by every `ls` and `pytest` too. **Where you put the guard matters more
  than what the guard checks.**

- **AFFECTS** — **every lane**, and every session on this machine besides. A hook fires in all of
  them; there is no lane this tax is not paid in. Code: `scripts/hooks/lane-bus.py`,
  `scripts/hooks/git-tree-moved.py`, and by implication `lane-attention.py`, which is registered
  on two events.

  ⚠ **This is an estate-wide tax nobody had priced.** `lane-bus.py` is registered in the *global*
  `~/.claude/settings.json`, so it fires in every repository, not only this one — including
  sessions that will never be in a lane and for which its answer is always `return 0`.

- **KIND** — DESIGN

- **CHANGES** — the advisory is **imported by `lane-bus.py`, not registered**. One interpreter
  start, both jobs, no change to `~/.claude/settings.json`, and the import is gated so a non-git
  command pays nothing. `advisory()` is a plain function returning text-or-None; `main()` is kept
  so it can be exercised standalone, which is how the cases were proved.

  ⭐ **The rule to carry forward: hooks are a fixed budget, not a list.** Before registering a new
  one, ask whether an existing hook on the same event can call it. A second process to decide
  "nothing to do" is the most expensive way to decide nothing.

  ⚠ **Two defects were committed while writing this control**, both caught before it shipped, both
  the shapes this repo already collects:
  - it called `sessions.live_sessions()`, which **does not exist**, behind a `hasattr` guard — so
    the contention branch would have been permanently dead and its absence would have looked
    exactly like *"no contention"*. The real function is `contended_repos()`. An inert control,
    written inside a control.
  - `advisory()` did not honour its own documented *"any error at all → nothing"* contract; only
    its callers did. Its own test failed with `RuntimeError('boom')` and a no-raise wrapper was
    added. **A function that promises not to raise should keep that promise itself rather than
    relying on every caller to.**
  - and the test file's first version resolved the hooks directory from `repo.primary()`, so run
    from a lane it would have tested the *primary's* copy of the code rather than the code under
    test. That is F91 for a third time in two days: `repo.primary()` is right for shared **state**
    and wrong for the **source you are exercising**.

- **STATUS** — ADOPTED
