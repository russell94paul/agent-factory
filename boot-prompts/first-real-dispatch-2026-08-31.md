# The first real dispatch — and the credential problem is solved, not deferred

**Written 2026-08-31.** Supersedes the `next:` of `absence-greens-2026-08-31.md`, whose gate work
is done. Runs alongside `workflow-library-2026-08-31.md` (client delivery), which is untouched.

`next:` **F90 remedy (a) — thread the repository through `worktrees.ensure` and both providers,
with the worktree SPARSE-CHECKED-OUT — then dispatch one real ticket.**

Success is one row in `.data/runs.jsonl` that is not `UNMEASURABLE`. That single row is worth more
than everything in the last three boot prompts combined, because the factory has **never made
anything**: 0 PASS, 0 real dispatches, every `agent_returned` event `dry_run=True`.

---

## 0. State, measured

`main @ e3aba6d`, pushed, clean. **The suite is GREEN** — 636 passed, 1 skipped, 2 xfailed —
for the first time in this programme. The suite-gate cache holds a PASS and returns in **0.0s**.

⚠ **One caveat, unresolved.** Of four full runs, one reported `1 failed, 635 passed` and it did
**not** reproduce in two later runs. There is a flaky test and nobody knows which. A suite that
passes on the second attempt is not reliably green — treat a single green run as weak evidence
until this is identified.

## 1. Why it went green, because it was not a code fix

`prefect-connectors` had been parked on `chore/artefact-homes` since **2026-08-23** with 29
uncommitted files. `agent-factory`'s mutation-anchor test reads that checkout live, and the
anchored lines do not exist on that branch. One `git checkout main` there took this repo from
15 red to 0 — and that cascaded:

```
15 red -> suite never green -> the PASS-only cache never fills -> every tracker render re-pays ~90s
```

⛔ **The parked work was preserved, not discarded, and the reason matters.** Paul's call was that
it need not be kept. `orchestrator/static/flow.js` — 1,132 lines, *"ZEUS FOUNDRY — FLOW: replay a
real pipeline run against the clock it actually ran on"* — was **VERIFIED to exist on no commit
anywhere in that repository's history** and in exactly one place on disk. And
`connector/base/base_connector_rest.py` differs from the version on
`fix/issue-18-base-connector-rest` by **250 diff lines**, so they are not interchangeable. It is
all on `wip/parked-2026-08-23` (3,332 insertions), unpushed. Bin the branch once someone has
looked; do not bin it before.

## 2. ⭐ The finding that makes step 1 ordinary engineering

This was framed for two sessions as a decision about accepting blast radius. **That framing was
wrong.** `~/repos/clients` holds three tracked credential files and an ADR recording that
`__TEMPLATE_ACCOUNT` contains live DISH_DUER identifiers — but a worktree does not have to contain
them.

**Sparse-checkout is per-worktree in git 2.53, and it was tested against the real repo:**

```bash
git worktree add <path> <ref>
git -C <path> sparse-checkout set --no-cone '/*' \
    '!**/account_secret.json' '!**/*client_secrets.json'
```

```
CORE_DEV/account_secret.json                          EXCLUDED
NINTH_CO/eclipse/account_secret.json                  EXCLUDED
KIT_ACE/.../ga_ka_client_secrets.json                 EXCLUDED
docs/decisions/ADR-003-...credentials.md              PRESENT   (documentation — correctly kept)
GEP/ and 1,593 of 1,595 files                         PRESENT
```

The agent gets the work and not the credentials — **a structural exclusion, not a prompt asking it
to behave.** That is what turns remedy (a) from a judgement call into a task.

⚠ Sparse-checkout is not a sandbox. It removes the files from *that worktree*; it does nothing
about ambient scope (`~/.azure`, `gh auth`, the Snowflake creds in the wiki vault) and nothing
about `bash`. Pair it with the post-hoc git change-set check (~100 lines — snapshot the change-set
before, diff after, count appearing/disappearing/**reverting** as modifications) which both prior-art
miners recommended independently and which catches the hole a worktree cannot. See
`concepts/patterns/agent-control-plane-prior-art.md` in the wiki.

## 3. What step 1 actually is

1. `worktrees.ensure(key, repo=...)` — remove the import-time pin. `worktrees.REPO` is
   `_repo.primary()` bound at module scope and no function takes a repository argument.
2. Thread it through `control.RunController._make_worktree` and both providers;
   `control.main()` hard-codes `repo_root=_repo.primary()` for the headless provider too.
3. Sparse-checkout on worktree creation, with the credential globs above.
4. The post-hoc change-set check.
5. **Delete the refusal's reason, not the refusal.** `control.unreachable_repo()` should keep
   refusing a repository the executor genuinely cannot reach — it just stops being every
   cross-repo ticket. Its tests are in `test_control_run.py` and must keep passing in spirit.
6. RED-before for each. Then one live dispatch, `dry_run=False`.

**Honour F90's stated order**: (b) landed first so nothing could ship a false attribution while
(a) was built. Do not undo (b).

## 4. What NOT to do next

- **Not more gate coverage.** 23 of 30 with a ratchet is enough; the last seven each need a fixture
  or a design decision and none blocks a run. `ceiling` in particular needs the *accounting* fixed
  first — the engine's only budget symbol is a TIME budget.
- **Not the Session Console.** `README.md:102` gates it on *"numbers worth looking at"* and the
  ledger is still 0 PASS. After the first runs, not before.
- **Not the bootstrap pack's roadmap.** Everything at Rank 4+ sits behind *one certified team*.
  `.agent-platform/RECONCILIATION.md` says which of its concepts already exist here under other
  names.

## 5. Open, and honest

- **The flaky test** (§0). Unidentified.
- **F71** — lanes still cannot see each other live. `design_debt()` is now `F71, F90`.
- **F90 remedy (a)** — this file's `next:`.
- **`wip/parked-2026-08-23`** in `prefect-connectors`, unpushed, unreviewed.
- **No CI still.** `.github/` does not exist. The suite is green *on one machine*.

## 6. Verify any of this in one command

```bash
python -m pytest -q                                     # expect green; watch for the flake
python -c "from factory import readiness as R; r=R.g_contract_suite_green(); print(r.verdict, r.headline)"
python -c "from factory import findings; print([f.id for f in findings.design_debt()])"
python -c "from factory import presets, verifiers; print(sorted(verifiers.REGISTRY))"
git -C ~/repos/prefect-connectors branch --list 'wip/*'
```
