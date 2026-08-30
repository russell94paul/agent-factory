# Boot — the last two branches, re-measured after main moved

✅ **CLOSED 2026-08-30 06:10. Both halves are done and this workstream is finished — but ONE OF THEM DID NOT GO THE WAY THIS FILE PLANNED. Read the second bullet before acting on anything below.**

1. **`lane/control-plane-renamed` — MERGED** (`6bd12f3`). Branch and worktree deleted after verifying
   full containment in main.

2. ⛔ **`lane/certify` — DECLINED, NOT MERGED. Branch and `.worktrees/certify` are DELETED.**
   This file's own banner said *"do not delete that branch or worktree until it merges."* It was
   deleted on Paul's explicit approval, and the reason is that **merging it would have done damage**,
   not merely been redundant. Measured before deciding:

   | what the merge would have done | evidence |
   |---|---|
   | re-added the **un-redacted** `blueprints/windsorai_gep.yaml` | main renamed it to `windsorai_client_a.yaml` in the client-name redaction (`62597d8`). This repo is public. |
   | reverted the corpus re-pin done hours earlier (`485ad12`) | main's `evals/MANIFEST.sha256` carries the corrected hash **and** the `HISTORY IS LOAD-BEARING` warning restored after `pin_corpus.py` ate it (F82). The lane's is the old bare hash. |
   | downgraded `factory/live_probes.py` | main's version defines **every** function the lane's does, plus the `probes_for` fix from `8dc4eac`. Checked with `comm` on the two symbol lists — the lane-only set is **empty**. |

   Its substance already reached main by a better route (wave0-rescue, plus the peer's fixes):
   findings **F30/F31 are already in `docs/findings.md`** and
   `docs/evidence/live-probes-a1-a5-2026-08-22.md` **already exists on main**. The branch was stale,
   not pending. **Nothing was lost — but if you were relying on that worktree, it is gone.**

**Everything in §2 below about resolving `lane/certify`'s seven conflicts is now moot.** The corpus
reasoning in it is still good reading; the plan is not to be executed.

**Where the estate actually stands now:** no `lane/*` branches remain in either repo except
`trial/wave0-rescue`, which is already merged and left alone only because another session has it
checked out. `prefect-connectors main` is `0195e59`; `agent-factory main` is `6bd12f3`.

---


⚠ **HALF DONE, 2026-08-30 05:25.** `lane/control-plane-renamed` **landed** (`6bd12f3`, 05:22) — its figures here are spent. **`lane/certify` is still out**: 4 commits, worktree at `.worktrees/certify`. Read this file only for that half, and do not delete that branch or worktree until it merges. See `README.md` in this folder.

**Written:** 2026-08-30, 01:40. **Supersedes `branch-reconciliation-2026-08-30.md`**, whose conflict
figures were measured before three merges landed and are now wrong in both directions. That file is
kept for its reasoning; **this one has the numbers.**

**Scope:** merge `lane/certify` (4 commits) and `lane/control-plane-renamed` (31) into main. Nothing
else is open. The blueprint/corpus defect that dominated the earlier prompt is **fixed and merged**.

---

## `next:` **Merge `lane/certify` into main. Its corpus conflict is three lines and main wins all three.**

Not the bigger branch first: 4 commits against 31, and every one of its seven conflicts is
characterised below with a decision already made. `lane/control-plane-renamed` got **harder** tonight
(§3) and should be done second, deliberately, not in the same push.

⛔ **Never resolve either branch with `--ours` or `--theirs` wholesale.** In both, each side is right
about something. The wrong choice is silent, and in `lane/control-plane-renamed` it deletes **1,268
lines of the tracker.**

---

## 0. State, measured 2026-08-30 01:40

```
main                      c191920   local == personal/main   ✅ pushed
feat/readiness-generator  d5309a8   fully merged into main
```

main was a **one-commit skeleton from 2026-08-20** until 00:30 tonight. It has since taken:

| | |
|---|---|
| `feat/readiness-generator` | 199 commits, fast-forward |
| `lane/artifact` | 5 commits, docs-only, 0 conflicts |
| `485ad12` | blueprint + corpus + manifest, re-pinned via `pin_corpus.py --why` |
| `bc957f4` | restored the manifest history the re-pin deleted → **F82** |
| `508cfc3` | five control-plane probes now **drive** `orchestrator.pipelines` instead of grepping it (by `agent-factory-25`) |
| `d5309a8` | boot-prompt corrections for F80 and its own retired premise |

**Already contained, nothing to do:** `trial/wave0-rescue` (144), `feature/phase-a-green-contract`
(1), `lane/artifact` (5), **`lane/control-plane` (86 — fully inside `lane/control-plane-renamed`;
merge the renamed branch and this is covered, do not merge both).**

⚠ **`agent-factory-25` was live through this session** and its work is now in main. Check whether it
is still running before you touch `factory/readiness.py` or `tests/test_readiness_probes_can_pass.py`:

```bash
git status --short
python -c "from factory import sessions; print(sessions.collisions())"
```

---

## 1. ⛔ Two rules, both earned tonight

**Rule 1 — never `git add` then `git commit` here.** A concurrent session's `git add` landed **three
of its files inside a commit of mine**, under my message, between my stage and my commit. Staging by
path did not prevent it.

```bash
git commit -F <msgfile> -- <explicit paths>      # bypasses the index entirely
```

Recovery: `git reset --soft HEAD~1` (working tree untouched), `git restore --staged <their files>`,
re-commit with the pathspec form.

**Rule 2 — merge in a temporary worktree. Never check out main in this checkout.** It holds other
sessions' uncommitted work. Every merge tonight was done this way:

```bash
WT="$TMP/merge-main"; git worktree add "$WT" main
cd "$WT" && git merge --no-ff lane/certify        # resolve here
git push personal main:main
cd - && git worktree remove "$WT"
```

---

## 2. `lane/certify` — 4 commits, **7 conflicts**, all decided

```
c80ce56  certify(A1,A5): fix six real defects an opus review found in the probe wiring
c4dc92d  docs(findings): renumber F11/F12 -> F30/F31 per cross-lane id-block scheme
9eba253  certify(A1,A5): evidence file + findings entries (F11, F12)
6d60a6b  certify(A1,A5): wire real instruments for windsorai@GEP config + regression suite
```

⚠ **It went 5 → 7 conflicts tonight** because main's blueprint and `docs/findings.md` both changed.

**Not a rival implementation — the same work, forked.** main's `factory/live_probes.py` came from
`6872aee`, the lane's from `6d60a6b`; they differ by ~6 insertions / 23 deletions. Then `62597d8`
("redact client identifiers") renamed things on main only and they drifted.

| Conflict | Resolution | Why |
|---|---|---|
| `evals/corpus/…json` | **main, all 3 lines** | see below |
| `evals/MANIFEST.sha256` | **do not hand-merge** — re-pin after (§2.2) | |
| `blueprints/windsorai_client_a.yaml` | **main** | carries the corrected classes + MEASURED basis (`485ad12`) |
| `blueprints/windsorai_gep.yaml` (lane only) | **delete it** | pre-redaction filename; check git does not record a rename and resurrect it |
| `factory/certify.py` | **main** | live path is now `build_contract(target, probes_for(target))` |
| `factory/live_probes.py` (add/add) | **union, main as base** | main has `LIVE_CLIENTS` + `_BlindWindsorAiProbes`; then port anything from `c80ce56` |
| `tests/test_live_probes.py` (add/add) | **union, main as base** | main has two controls that must survive |
| `docs/findings.md` | **union** | then check for duplicate ids (§4) |

### 2.1 The corpus is three lines, and main is right about all three

Re-measured 01:40 — the two class-name rows are **gone**, resolved on main in `485ad12`:

```
-  "client": "CLIENT-A"                          +  "client": "GEP"
-  "table": "QA_DG1_CLIENT-A_PREFECT_PR…"        +  "table": "QA_DG1_GEP_PREFECT_PR…"
-  "id": "dep-windsorai-client-a"                +  "id": "dep-windsorai-gep"
```

**Take main's side on every one — the redaction was deliberate.** Verify before trusting this:

```bash
git diff --ignore-all-space main:evals/corpus/windsorai-2026-08-20.json \
                            lane/certify:evals/corpus/windsorai-2026-08-20.json
```

⚠ `git diff` without `--ignore-all-space` reports **213/213** because the two are formatted
differently (6,762 vs 6,534 bytes, both LF). **A diff line count is not a difficulty estimate.**

### 2.2 ⛔ After re-pinning, restore the manifest history BY HAND

`pin_corpus.py` rebuilds `MANIFEST.sha256` from `rglob` and **drops every `#` line** — its reader
skips comments, its writer destroys them. It deleted a four-line audit record on 2026-08-30, restored
manually. **F82. The script is unfixed.** A warning sits at the top of the manifest.

```bash
python scripts/pin_corpus.py --check --why "…"     # inspect drift first, re-pins nothing
python scripts/pin_corpus.py --why "…"             # then re-pin
# then: re-add the superseded `#` lines, including the one you just superseded
```

### 2.3 The highest-value unread thing in this merge

**`c80ce56` — "fix six real defects an opus review found in the probe wiring."** Six reviewed defect
fixes to code main also has. **Read it before resolving `live_probes.py`**; it is the most likely
source of a defect main still carries.

### 2.4 Definition of done

```bash
python -m factory.certify blueprints/windsorai_client_a.yaml
#   A1 PASS "constructed 2 classes, 6 account(s)"
#   A5 FAIL "1 failing test(s)"      <- REAL, the sibling suite has one
#   10 UNMEASURABLE, aggregate FAIL, exit 1

python -m factory.certify blueprints/windsorai_client_a.yaml --calibrate
#   PASS (12), and it MUST print "REPLAYED, not a live measurement"

python -m pytest -q -p no:cacheprovider tests/test_connector_contract.py tests/test_contract.py \
  tests/test_corpus.py tests/test_blueprint.py tests/test_evaluator_isolation.py \
  tests/test_measurement_window.py tests/test_eval_can_fail.py      # 90 passed, baseline
python -m pytest -q tests/test_live_probes.py                        # 17 passed, baseline
```

⛔ **A1 `PASS` is the goal; aggregate `PASS` is a bug.** Ten assertions still have no instrument. If
the aggregate goes green, something is rounding up — **stop and find it.**

---

## 3. `lane/control-plane-renamed` — 31 commits, and tonight made it HARDER

⚠ **Re-measured 01:40, after `508cfc3` landed on main:**

| | before tonight | **now** |
|---|---|---|
| conflicts | 2 | **4** |
| `factory/readiness.py` | 598+ / 338− | **598+ / 685−** |
| `tests/test_readiness_probes_can_pass.py` | *(clean)* | **add/add conflict** |

`508cfc3` rewrote the same five control-plane probes this branch touches. **Both sides now
independently rewrote `readiness.py`'s probes — main's drive the engine, the lane's are the earlier
generation.** Read `508cfc3` first; main's version is very likely the one to keep, and the lane's
31 commits are worth mining for what main lacks rather than merging wholesale.

### ⛔ The number that should stop you

```
scripts/local_tracker.py    main: 2,575 lines    lane: 1,307 lines
```

**That is not the lane deleting 1,268 lines of work — it is main's tracker having grown by that much
since the lane branched.** Taking the lane's file, or `--theirs`, **destroys half the tracker.**

**Keep main's `local_tracker.py` as the base and port the lane's delta onto it.** Read
`git diff main...lane/control-plane-renamed -- scripts/local_tracker.py` and apply the *intent*.

### What is worth having

27 files, most new and conflict-free: `factory/workplan.py` (390), `scripts/mutate_readiness_probes.py`
(240), `scripts/dashboard_cap_override_probe.py` (292), `scripts/sessions_render_probe.py`,
`scripts/reconcile_pipeline_records.py`, three test files.

Its log is unusually honest — several commits correct its own earlier claims:

```
c5c7e83  test(reaper): the test proving F30 fixed had F30's own defect
02f5391  docs(findings): correct F32's basis — 288 is DERIVED, and the audit sizes are simulation figures
a031241  docs(evidence): the regeneration command in this file was the trap
2fa93c7  docs(control-plane): what the independent read found, including that this file was wrong
```

### Definition of done

```bash
python -m factory.launch        # states its own basis — use this, NOT pytest, as the baseline
python -m factory.readiness
wc -l scripts/local_tracker.py  # MUST still be ~2,575+, not ~1,300
```

---

## 4. Measuring anything here — read before quoting a number

⛔ **`pytest -q` is not the baseline.** ~20 tests read the `prefect-connectors` checkout live and
other sessions move it. The count went **388 → 409 inside one hour** with no change from the
measuring session, and a full run takes **20+ minutes** because `test_live_probes` shells out to the
sibling repo's 826-test suite several times. Use `factory.launch` / `factory.readiness` — they state
their own basis.

⭐ **F80 — the board measures the wrong BRANCH, not just the wrong repo.** F78 established which
repository each gate reads; F80 which *revision*.
`tests/orchestrator/mutate_control_plane.py` **exists** on `prefect-connectors`' `lane/control-plane`
(**147 ahead of its main, 0 behind, already on origin**), while `CONNECTORS` points at a checkout on
`chore/artefact-homes` where it is absent. **Four gates flip when pointed at the right revision:**

| gate | `chore/artefact-homes@8b7c68d` | `lane/control-plane@7f10752` |
|---|---|---|
| `cap` · `bounded` · `concurrency` · `reaper` · `from-history` | FAIL / UNMEASURABLE | **PASS** |
| `ceiling` | FAIL | FAIL |

**So the ~21 test failures are an artefact of the revision under measurement, not a regression, and
not "a missing file" either.** Set `$PREFECT_CONNECTORS` deliberately, or record `branch@sha` beside
any number. `readiness.revision()` now exists for that.

⚠ **`ceiling` is real on every branch and does not flip.** The only budget symbol in the engine is
`TERMINATION_BUDGET_SEC` — a *time* budget for the reap sweep — and cost is recorded only on
`stage_completed`, so the accrued figure a ceiling would read is **blind to every failure.**
**Fix the accounting before building the comparison**, or the gate goes green over a ceiling that
cannot hold. F77 and `agent-factory-25` reached this independently.

⛔ **Do not merge `prefect-connectors`' `lane/control-plane` to satisfy a gate.** 147 commits into a
production orchestrator's main is Paul's call.

⚠ **`tests/test_roadmap.py` hangs** — >200s, `rc=124`. Measured pre-existing on both sides of another
session's changes. Not yours.

⚠ **Findings ids collide across branches.** `lane/certify` renumbered `F11/F12 → F30/F31`;
`lane/artifact` `F11-F13 → F50-F52`; and two sessions independently produced colliding `F78`/`F79`
on 2026-08-29 (resolved to `F80/F81`). **`F83` is the next free id.** Check
`ls docs/findings.d/ && grep -o 'F[0-9]\+' docs/findings.md | sort -u` after every merge.

---

## 5. ⭐ Should the next session convene a council?

**For the merges themselves: no.** `prospect`'s own rule is not to convene for a decision already
made or a question one file settles, and §2 has every `lane/certify` conflict decided with the
evidence beside it. Five lenses would find five reasons and none would be load-bearing.

**For what comes after the merges: yes, and specifically `conclave`.** The real risk here is not
choosing wrong — it is choosing wrong **silently**. A merge resolution that takes the wrong side
produces a working tree, a green-looking board and no error. That is exactly `conclave`'s shape: a
diff exists, its defects are unknown, and its failure mode is a plausible-looking result nobody
re-verifies.

**Run it on the combined `main..HEAD` diff after both merges, with the lenses aimed at
wrong-side resolution, not at code style:**

| Lens | Assignment |
|---|---|
| **correctness** | For every conflicted hunk, which side survived and does the evidence support it? Name any hunk where the *other* side was right. |
| **gating integrity** | Can `A1`–`A12` still each report `FAIL` *and* `UNMEASURABLE` independently? Does any resolution let `UNMEASURABLE` become `PASS`? Mutate one and prove the gate still refuses. |
| **blast radius** | Did `scripts/local_tracker.py` lose lines? Did `factory/readiness.py` lose a probe? Did the manifest lose history again? |
| **provenance** | Every `MEASURED` label in the merged blueprint and corpus — is it actually measured, or inherited like the class names were? |
| **`devil`** | Argue the merge should be reverted. What did it quietly destroy that no test covers? |

⭐ **The single highest-value question to hand a council here**, because it is the shape this repo
keeps hitting and no gate catches it:

> **"Which file did this merge leave present, correct-looking, and wired to nothing?"**

Five instances so far — `blocked_by`, `RepoDeployer`, the tracker's `/finish` button, `EvalSuite`,
`live_probes` — and **every one was found by grepping for callers, never by a gate.**

`inquest` is the right sibling if a defect actually surfaces afterwards; `assay` only if the question
becomes "how many/how much". Not `prospect` — nothing here is a bet.

---

## 6. What is NOT done

- **Neither merge is started.** Both branches are untouched.
- **`pin_corpus.py` still eats the manifest's comment history** (F82). Restored by hand once; unfixed.
- **Not measured:** whether an *earlier* re-pin already lost history nobody restored. The 2026-08-29
  entry survived only by being most recent. `git log -p -- evals/MANIFEST.sha256` is the only place
  older records could exist, and **it has not been read.**
- **`factory/events.py` does not exist.** Phase 0 has not started —
  `boot-prompts/phase-0-event-ledger-2026-08-30.md`.
- **No connector is certified.** A1 passes; ten assertions have no instrument; `breadth` is
  *1 case, 0 strata*.
- **`c80ce56`'s six reviewed defect fixes have never been read by anyone on main.**

---

## 7. Where things live

| Path | What |
|---|---|
| `factory/certify.py:105` | The live path — `probes_for(target)` |
| `factory/live_probes.py` | `WindsorAiGepProbes` (A1/A5, no credential) · `probes_for` · `LIVE_CLIENTS` |
| `factory/calibration.py:40-47` | `calibration_target()` — overrides tenants only. ⛔ **Do not extend to class names**: `CtxProbes` returns the corpus's `constructed` list, so sourcing both from the corpus makes A1 compare the world to itself — an assertion that cannot fail |
| `blueprints/windsorai_client_a.yaml:23-40` | The corrected classes, basis `MEASURED` |
| `evals/MANIFEST.sha256` | Audit chain + the F82 warning. `5c0d63ea…` is current |
| `scripts/pin_corpus.py` | The only sanctioned re-pin. Refuses without `--why`. **Eats history** |
| `docs/findings.d/F77–F82` | Which repo · which branch · the unwired instrument · the re-pin that ate its trail |
| `docs/reviews/build-vs-adopt-2026-08-29.md` | Why build not adopt; what UNMEASURABLE must survive |
| `boot-prompts/phase-0-event-ledger-2026-08-30.md` | What comes after these merges |
