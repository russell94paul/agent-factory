# Bootstrap pack installed, three instruments repaired, and the run that still cannot happen

**Written 2026-08-31.** Supersedes nothing. Runs alongside `workflow-library-2026-08-31.md`, whose
`next:` (run `keel` on the GEP marketing model) is untouched and still the client-facing priority.

`next:` **decide F90 remedy (a)** — thread the repository through `worktrees.ensure` and the
providers — or accept that the first supervised run cannot happen. Nothing else unblocks it, and
everything upstream of it is now green and fast.

---

## 0. The one-line state

`main @ d5c0af4`, **unpushed**. Suite runs in **112s** (was ~2100s). 15 failures remain and **none
of them is this repo's defect** — see §4.

## 1. What this session was asked for, and what it actually established

Paul asked to install an externally-generated "autonomous bootstrap pack" and let it drive a
build programme. The pack is installed and **deliberately inert**. The reason is the finding:

⭐ **The pack proposes building, as novel, a programme this estate already falsified.**
`agent-army-research/research/synthesis/W0-foundations.md` (2026-08-30) concludes AOE is
organisation-oriented MAS, the category name is taken twice in 2026 (Waites `arXiv:2602.13275`;
**IMACS** `arXiv:2607.25446` *is* the organizational-compiler thesis), and the novelty claim is
refuted on all four components. `README.md:94-104` independently gates Agent Army behind **one
certified team**, and `.data/runs.jsonl` is 10 rows with **0 PASS**.

The pack is a research scaffold and a prior-art pointer. Treated as a build plan it starts six
ranks above the evidence. That judgement is written up in `.agent-platform/RECONCILIATION.md` with
a disposition per concept; read that rather than the pack.

⛔ **Two corrected premises — do not re-derive these.**
1. The two bootstrap ZIPs in `~/Downloads` are **byte-identical** (SHA256 `BEE61D23…`). There was
   never an older paid-API pack to guard against. `agent-factory-deep-review-pack.zip` is a
   different thing — a snapshot of this repo, not a rival bootstrap.
2. `factory/certify.py` **does not import `readiness`**. The old "the suite invokes itself"
   framing is wrong; there is no cycle. See F92.

## 2. What shipped — `d5c0af4`

| | |
|---|---|
| **F90 remedy (b)** | `control.unreachable_repo()` refuses a ticket whose `repo` the executor cannot reach, before the worktree, the claim or the attempt. RED-before proven: without it `gp-329` scores **PASS** for a run recorded against `clients` that happened in `agent-factory`. |
| **F91** | `readiness.py` computed the estate root from `__file__`, so from a lane `CONNECTORS` resolved to `.worktrees/prefect-connectors` — a path that does not exist. Every gate reading the connectors checkout went blind in a lane. Now `_repo.primary()`. |
| **F92** | `g_output_is_certified` had no `AGENT_FACTORY_IN_SUITE` guard and a **120s outer timeout against a 300s inner** one. Fixed; this is the entire 19× speedup. |
| **F93** | **OPEN, not fixed.** `filed_after` compares mtimes; a fresh checkout reports all 18 research answers outstanding. |

Measured: full suite **~2100s → 112s**; `tests/test_roadmap.py` **never completed → 39s**.

## 3. ⭐ The next session's actual job

**Decide F90 remedy (a).** Both presets with a runnable verifier (`add-measure`, `model-redesign`)
are `pbi_model` work living in `~/repos/clients`. Remedy (b) now *correctly refuses* them, so the
first real dispatch is blocked by design until the repository is threaded through
`worktrees.ensure` and the providers. That is the feature F90 named, and it is the only thing
standing between this repo and its first non-`UNMEASURABLE` run row.

Everything else upstream is done: the contract is calibrated, the suite is fast, the refusal is
honest, and the ledger records it.

## 4. What is NOT done — the honest list

- **Nothing is pushed.** `d5c0af4` is local only. `git log --branches --not --remotes` before
  assuming otherwise.
- **The suite is not green: 15 failures.** All in `tests/test_mutation_anchors_still_match.py`, and
  **not this repo's defect.** `~/repos/prefect-connectors` is parked on `chore/artefact-homes`
  @ `8b7c68d`, created **2026-08-23 by Paul**, carrying **29 uncommitted files**. The anchored
  lines and `tests/orchestrator/mutate_control_plane.py` do not exist on that branch; both are on
  its `main`. Moving it is destructive to whatever those 29 files are. **Paul must decide.**
- ⛔ **Six readiness gates go green on an absence, and 25 of 30 have never been mutation-tested.**
  Verified by me at `readiness.py:511` — `g_success_means_correct`, the gate named for this
  estate's signature failure, returns `_pass("no completed run carried failures", [], src)` with an
  **empty evidence list and no population floor**. It passes when nothing ever completed. The fix
  pattern is ten lines below it (`g_status_matches_reality` computes and reports its measured
  population). The other five are listed in this session's transcript; they need **one consistent
  approach**, not six separate patches, and each changes a verdict on the operator's board.
- ⛔ **A blueprint can silence its own assertions.** Proved by execution elsewhere this session:
  blanking three fields scores `PASS (PASS=12)` on the exact defect A3 exists to catch, because
  `evaluator_service/service.py:148-162` `_enforce_target_floor` checks only four fields of twelve.
  The shipped blueprint **already** ships `pinned_test_revision:""` and `expected_image_digest:""`,
  so A5's and A3's checks are already inert.
- **F90 remedy (a) not started.** F93 filed with three non-equivalent remedies, none chosen.
- **`docs/findings.d/F90-*.md` is still untracked** in the working tree — Paul's file from an
  earlier session, deliberately not swept into this branch. It needs committing.
- **`.agent-platform/` is untracked and not gitignored** — 112 files a `git add -A` would sweep in.
- **No CI still.** `.github/` does not exist, which is why F93 has never fired.

## 5. Gotchas earned

- **`git worktree add` breaks `test_synthesis_current.py`** and it is not your change — F93. Verify
  any new failure against the primary checkout before believing it.
- **Bash heredocs mangle backslashes here.** A test docstring containing `C:\Users\...` arrived as
  a broken escape and would not compile. Use Write/Edit for anything with a backslash.
- **This checkout moves under you.** `main` went `6d9e94a → aef21e7` mid-session from a concurrent
  session. Re-measure `git rev-parse HEAD` immediately before every `add`/`commit`.
- Teammate agents' final reports did not route back automatically; they had to be asked explicitly
  via `SendMessage`.

## 6. Where the durable state lives — do not create a second one

`boot-prompts/README.md` is the router and the only maintained boot file. Corrected premises are
`docs/findings.d/`, read as data by `factory/findings.py`. The roadmap is **derived** by
`factory/roadmap.py` and has no task list on principle. Research lives in the sibling repo
`agent-army-research`. The pack's `PROJECT_STATE.template.yaml` is deliberately unfilled and its
research-queue script deliberately unrun; `.agent-platform/README.md` says why.
