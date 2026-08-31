# Six gates that greened on an absence, and the hook tax nobody had priced

**Written 2026-08-31, overnight, unattended.** Continues
`bootstrap-and-instruments-2026-08-31.md`, whose §4 named the six gates as the sharpest unfixed
thing on the board. They are fixed. Its `next:` — F90 remedy (a) — is untouched and still the
thing that unblocks the first real run.

`next:` **extend the mutation harness to the gates that measure agent-factory itself.** 25 of 30
readiness gates have never had a negative control, and the five that do all point at the
*connectors* repo — so every gate measuring this repo is outside it. That is not a coincidence with
the six repaired below; it is the reason for them.

---

## 0. State

Branch **`fix/absence-greens`**, two commits, **unpushed**, worktree `.worktrees/absence-greens`.
Main is `ee4bc8d` and untouched by this work.

```
da23ddb  fix(gates): six gates reported PASS over an absence, and four cited no evidence
d79fe41  feat(hooks): warn when the checkout moved under you, and pay nothing extra for it
```

Suite: **16 failures before, the same 16 after** — no regression. (16 in a worktree, 15 in the
primary; the extra is F93, which is fresh-checkout-only.)

## 1. What shipped

**Six gates returned PASS over an absence rather than a measurement, and four cited no evidence at
all.** Each was confirmed with a discriminating test whose result was predicted from the source
*before* it ran. All six predictions were correct — recorded in `docs/findings.d/F94`.

| Gate | The absence that passed |
|---|---|
| `g_success_means_correct` | one run that only ever **failed**; nothing completed |
| `g_gates_have_checks` | every gate deleted — `0 == 0` |
| `g_qa_gate_is_general` | `promotion_ops.py` present but **emptied** |
| `g_repo_is_durable` | a remote **named** by a `git remote` that exited **128** |
| `g_evaluator_is_a_service` | `AGENT_FACTORY_EVALUATOR=totally-not-a-service` |
| `redesign_contract` `R2` | evidence file that **never mentions renames** |

⭐ Two are worse than an empty population. `g_repo_is_durable` **asserted a word it never tested** —
the headline says *pushed*, the only command run was `git remote`, its exit code was never
inspected. `g_evaluator_is_a_service` printed *"the evaluator is a separate principal"* directly
above its own evidence line reading *"health check: NO ANSWER — configured is not running"*, over
an environment variable **the graded party sets itself**.

⚠ **The board does not move.** All five readiness gates return the identical verdict in the real
estate before and after — the real populations are non-empty and the real endpoint is well-formed.
Only `g_repo_is_durable`'s headline changed, from asserted to measured. **The fixes bite only in
the degenerate cases that were silently green.**

**And a checkout-moved advisory** (F95), because HEAD moved twice under the previous session. It is
silent inside a worktree — the worktree *is* the control — silent on reads, silent on a session's
first write, and it never returns a permission decision.

⭐ **It is imported by `lane-bus.py`, not registered, and that was a measurement not a preference:**
a hook is a process, `lane-bus.py` costs **213ms on every tool call** against a **114ms**
interpreter floor, and a second hook would have made it ~415ms. Gated behind a free substring test,
the advisory adds **+4ms**. **No change to `~/.claude/settings.json` is needed** — and none was
made, deliberately, while Paul was asleep.

## 2. What is NOT done

- **Nothing pushed.** Both commits are local.
- **The 15 mutation-anchor failures are unchanged and are still not this repo's defect.**
  `prefect-connectors` is parked on `chore/artefact-homes` @ `8b7c68d`, created **2026-08-23 by
  Paul**, with **29 uncommitted files**. The anchors and `mutate_control_plane.py` exist only on
  its `main`. Moving it is destructive to whatever those 29 files are — **Paul must decide**, and
  it is the only thing standing between the suite and green.
- ⛔ **The larger half of F94 is untouched: 19 further readiness gates have no negative control.**
  Six were found by inventory. Nobody has shown the rest can fail, and
  `tests/test_readiness_probes_can_pass.py` says at `:14-19` that it only proves a PASS branch is
  *written* — *"a probe guarded by `if False:` would satisfy this test."*
- **F90 remedy (a) not started**, and it is still the only thing that unblocks a real dispatch.
- **F93 still OPEN** — three non-equivalent remedies named, none chosen.
- **The hook is not registered anywhere.** It rides inside `lane-bus.py`, which is already wired in
  the global settings, so merging this branch activates it. That is worth knowing before merging.
- **`.agent-platform/` still untracked and not gitignored**; `F90-*.md` still untracked in the
  primary.

## 3. Gotchas earned overnight

- ⭐ **`repo.primary()` is right for shared STATE and wrong for the SOURCE you are exercising.**
  Third occurrence in two days. A test that resolved the hooks directory from it would have
  exercised the *primary's* copy of the code while claiming to test the branch's.
- **A hook is a process, not a callback.** Before registering one, ask whether an existing hook on
  the same event can call it. A second process to decide "nothing to do" is the most expensive way
  to decide nothing.
- **Where you put the guard matters more than what it checks** — the folded-in advisory still cost
  +60ms/call until the `importlib` load was gated behind `if "git " in cmd`.
- **A function that promises not to raise should keep that promise itself.** `advisory()` relied on
  its callers; its own test failed with `RuntimeError('boom')`.
- Two of the three defects committed while *writing a control* were inert-control and
  location-dependent-verdict — the shapes this repo already collects. Writing about a defect family
  is not protection from it.

## 4. How to verify any of this in one command each

```bash
python -m pytest tests/test_gates_refuse_an_empty_population.py -q   # 15, the six gates
python -m pytest tests/test_tree_moved_advisory.py -q                # 15, the advisory
python -c "from factory import findings; print(len(findings.load()), findings.unattached())"
git log --oneline main..fix/absence-greens
```
