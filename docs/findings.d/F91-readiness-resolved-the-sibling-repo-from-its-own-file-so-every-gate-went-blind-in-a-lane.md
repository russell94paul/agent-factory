### F91 — `readiness.py` resolved the connectors checkout from its own file, so every gate reading it went blind inside a lane worktree

Found while running the suite from `.worktrees/bootstrap-wave` during the bootstrap wave. The
mutation-anchor tests reported a different failure there than in the primary, which is the tell:
an instrument whose answer depends on where it is standing.

## Why this one stings

`factory/repo.py` exists **specifically** to stop this. Its docstring names the pattern and the
damage:

> `claims.py`, `worktrees.py` and `runs.py` each computed a root, and only `runs.py` got it right
> … The other two used `__file__.parent.parent`, which is correct in the primary checkout and
> **wrong inside a lane worktree**.

`readiness.py` was a third such site and was never converted — the 61 KB module that holds all 30
gates, in a repo whose founding argument is that an instrument which cannot see must say so rather
than return a plausible number.

**And a structural guard for this bug already existed and did not fire.**
`tests/test_repo_root.py::test_no_module_computes_a_shared_data_root_from_its_own_file` was written
after this defect appeared five times, precisely so the sixth would be caught by a rule instead of
by a person. It scans every module for a `__file__`-derived path that builds `.data/`. Its
docstring states the principle it drew the line on:

> anything under `.data/` is estate-wide state and must resolve through `factory.repo`. Git-tracked
> content may legitimately be checkout-relative — that is the real distinction.

`CONNECTORS` is **neither**. It names a *sibling repository*. There is only one
`prefect-connectors`, so it is estate-wide by definition — but it is not under `.data/`, so the
guard never looked at it. ⭐ **The category scheme had two boxes and this needed a third.** A guard
is only as wide as the relation it derives over (F88's rule, one relation further out).

- **BELIEVED** — `readiness.CONNECTORS` names the `prefect-connectors` checkout, so the five
  bounding gates, the mutation-anchor tests and `_suite_fingerprint` all read the same tree
  wherever they run from.

- **ACTUALLY** — `readiness.py:38` was `FACTORY = pathlib.Path(__file__).resolve().parent.parent`,
  and `CONNECTORS` is `FACTORY.parent / "prefect-connectors"`. From a lane worktree `FACTORY`
  resolves to `<primary>/.worktrees/<lane>`, so `CONNECTORS` becomes
  `<primary>/.worktrees/prefect-connectors` — a directory that does not exist and never will.
  `CONNECTORS=` is also hashed into `_suite_fingerprint` (`readiness.py:605`), so the suite cache
  keyed differently in a worktree than in the primary and could not hit from either side.

- **MEASURED BY** — the same import from both checkouts, result predicted before it ran:

  ```
  primary   C:\Users\PaulRussell\repos\prefect-connectors                      exists: True
  lane      C:\Users\PaulRussell\repos\agent-factory\.worktrees\prefect-connectors  exists: False
  ```

  ```bash
  python -c "from factory.readiness import CONNECTORS; print(CONNECTORS, CONNECTORS.is_dir())"
  ```

  Run it once from the repo root and once from any directory under `.worktrees/`. Corroborated
  structurally: `grep -n "FACTORY = " factory/readiness.py` showed no use of `factory.repo`, and
  `readiness.py` imported no sibling module at all.

- **AFFECTS** — `factory/readiness.py` and every gate that reads the connectors checkout, which is
  the five bounding gates plus the mutation harnesses reached through
  `tests/test_mutation_anchors_still_match.py`. Also `factory/board.py`, `roadmap.py`, `flow.py`
  and `goals.py`, which are all derived views over `readiness.GATES` — a gate that measured a
  non-existent path fed a board that reported it.

  ⚠ **The blast radius is bounded by the fact that gates rarely run from a lane today.** Lanes are
  worked by Claude Code sessions, and the tracker serves from the primary. That is luck, not
  design, and it is exactly why this survived: the defect is invisible from the only place anyone
  routinely looks.

- **KIND** — INSTRUMENT

- **CHANGES** — `readiness.py` now imports `factory.repo` and binds `FACTORY = _repo.primary()`,
  matching `worktrees.py:37`. Two tests added to `tests/test_repo_root.py`, which is where this
  bug family lives: a behavioural one asserting `CONNECTORS` is a sibling of the primary and never
  under `.worktrees/`, and a structural one asserting `readiness.py` does not bind `FACTORY` from
  `__file__`. The structural one is the load-bearing half — run from the primary the two
  expressions are the *same path*, so the behavioural assertion passes over the bug and only
  discriminates inside a worktree.

  ⛔ **The `.data/` guard was NOT widened.** Six other modules in `factory/` derive a root from
  `__file__` (`corpus`, `findings`, `plan_gates`, `schedule`, `synthesis`, `workplan`) and every
  one of them stays *inside* the checkout, where checkout-relative is defensible and may be
  intended — a lane reading its own `docs/`. Banning the expression outright would flag six
  legitimate uses to catch one defect, which is how a guard gets disabled. The rule that
  generalises is narrower and is stated here rather than enforced: **a path that leaves this
  repository is estate-wide and must resolve from `repo.primary()`.** Enforcing it needs a
  detector for "derives a sibling path", which does not exist yet.

- **STATUS** — ADOPTED
