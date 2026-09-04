# 08 — Validation and rollback plan

**Phase 1 proposal.** Measured 2026-09-03 against `827f871`.

---

## 1. The pre-migration baseline — recorded before anything changes

⛔ **Capture this immediately before Batch 1 and store it as `docs/restructure/baseline-<sha>.txt`.**
Every post-batch check compares against it. A baseline captured *after* a change is not a baseline.

```bash
git rev-parse HEAD                              > baseline.txt   # expect 827f871…
git status --porcelain                         >> baseline.txt   # expect EMPTY after D-3
git worktree list                              >> baseline.txt   # expect the same 4
git ls-files | wc -l                           >> baseline.txt   # 892
find . -path ./.git -prune -o -type f -print | wc -l           >> baseline.txt
python -m pytest 2>&1 | tail -1                >> baseline.txt
find docs .agent-platform blueprints missions evals boot-prompts -type f | wc -l >> baseline.txt
python scratchpad/census.py baseline-census.tsv                  # 1079 files + SHA-256 each
```

### 1.1 Measured baseline, 2026-09-03

| Instrument | Value | Verdict |
|---|---|---|
| `pytest` | **`2 failed, 1016 passed, 2 xfailed, 7 warnings in 252.85s`** | ⚠ **AMBER** |
| Tracked files | 892 | — |
| Files in working tree (ex `.git/.data/.sessions/.worktrees/__pycache__`) | 1,079 | — |
| Files under indexed roots | 888 | ⚠ manifest claims 719 |
| Working tree | **DIRTY** — 18 modified, 51 untracked entries | ⛔ blocks Batch 1 |
| Worktrees | 4, on 4 branches | ⚠ Decision D-1 |
| Credential-shaped strings | 2, both deliberate test fixtures | ✅ instrument proved live |
| `.data/runs.jsonl` | 10 rows, **0 `PASS`**; 7/7 `agent_returned` `dry_run=True` | ⚠ measured directly today |

⛔ **The two failures are pre-existing and must not be fixed by Phase 2.**

```
tests/test_findings.py::test_every_finding_carries_all_four_mandatory_fields
  findings missing mandatory fields: {'F101': ['BELIEVED', 'ACTUALLY', 'MEASURED BY']}
tests/test_findings.py::test_every_finding_reaches_at_least_one_lane
  findings attached to no lane: ['F101']
```

⭐ **They are the control.** *"Same 2 failures, same 1016 passes"* is a far stronger statement than
*"green"* — it proves the suite is still discriminating. **Fixing F101 during the migration would
remove the only evidence that Phase 2 changed nothing**, and would let a new failure hide behind a
green line. Fix it in a separate, clearly-labelled session, before or after — never during.

---

## 2. ⛔ Blocking preconditions

| # | Precondition | Check | If it fails |
|---|---|---|---|
| 1 | Working tree clean | `git status --porcelain \| wc -l` = 0 | **STOP.** 17 of 18 modified files sit in paths the batches touch |
| 2 | `HEAD` = recorded | `git rev-parse HEAD` | **STOP, re-measure.** Sessions share this checkout; state moved during this audit |
| 3 | Worktree decision D-1 | operator | **STOP** |
| 4 | Baseline captured | `baseline-<sha>.txt` exists | **STOP** |
| 5 | pytest = baseline | `tail -1` matches | **STOP** — *fewer* failures is also a stop (§1.1) |

⚠ **Precondition 2 is re-checked before EVERY batch, not once.** During this read-only audit, a
`cd` in one parallel command changed the working directory another command then ran in. Concurrent
sessions on one checkout are a measured hazard here, not a theoretical one.

---

## 3. Per-batch protocol

### 3.1 Before

1. Re-check preconditions 1, 2, 5.
2. ⭐ **Write the inverse-move manifest first** (§3.4).
3. Record the batch's expected file-count delta.

### 3.2 After

```bash
python -m pytest 2>&1 | tail -1        # must equal baseline EXACTLY
git status --porcelain                 # every entry must be an INTENDED change
python scratchpad/census.py after.tsv  # diff against baseline-census.tsv
python -c "import yaml,glob; [yaml.safe_load(open(f,encoding='utf-8')) for f in glob.glob('docs/**/*.yaml',recursive=True)]"
```

**Four invariants, checked every batch:**

| # | Invariant | Command | Why |
|---|---|---|---|
| I1 | **No tracked artifact disappeared** | `git ls-files \| wc -l` ≥ 892 | The plan moves **zero** tracked files, so this must never drop |
| I2 | **`docs/raw_research/` hashes unchanged** | `awk` compare on the census | ⛔ Immutability. Not recoverable by re-running |
| I3 | **No previously-ignored path is now visible** | `git status --porcelain \| grep -f ignored-paths.txt` | ⛔ One rule covers a live client-data capture |
| I4 | **Runtime `docs/` paths still resolve** | `grep -rn "docs/findings\|docs/research\|docs/artifacts\|docs/evidence" factory/*.py` then `test -e` each | ⭐ These fail **silently** |

### 3.3 Stop rules

⛔ **Stop the batch and report. Never hide a failure, never proceed past one.**

- pytest differs from baseline **in either direction**.
- Any hash under `docs/raw_research/` changed.
- A previously-ignored path appears in `git status`.
- Any runtime `docs/` path no longer resolves.
- `git ls-files | wc -l` decreased.

### 3.4 ⭐ Rollback — and why `git` is not enough here

**Tracked files: fully covered by git.** Zero tracked files move (`03` Part 9), so
`git checkout -- .` restores the tracked tree completely.

⛔ **Untracked files: git covers none of it.** ~35 `mv`s and 29 `RETIRE`s involve untracked files.
`git revert`, `git checkout` and `git reset` **cannot undo any of them** — git never knew they
existed. This is the single largest rollback gap in the plan, and it is invisible to anyone who
assumes a git repo is recoverable by git.

**Mitigation — an executable inverse-move manifest, written BEFORE each batch runs:**

```bash
# docs/restructure/rollback/batch-04-inverse.sh   (generated, never hand-written)
mv "docs/archive/combined-execution-research-v2-2026-09-02/00_START_HERE.md" \
   "docs/combined-execution-research-v2-2026-09-02/00_START_HERE.md"
# … one line per move, exact inverse, reverse order
```

Each manifest is **verified by dry-run before the batch executes** (every source exists, no
destination is occupied), and the census hash of every moved file is recorded so rollback can be
*proved* complete, not assumed.

⛔ **No deletion occurs in any batch**, so no rollback ever needs to restore content — only
locations.

---

## 4. Validation inventory — what exists, and what does not

The brief asks for formatting, lint, unit, integration, build, link, schema, duplicate and
documentation-reference checks. **Most do not exist in this repository.** Stating that plainly is
required; substituting a weaker check while implying the stronger one ran is not acceptable.

| Requested | Available? | What runs instead | Limitation |
|---|---|---|---|
| Formatting | ⛔ **NO** — no black/ruff config | — | **Not checked.** Not introduced by this migration |
| Lint | ⛔ **NO** — no linter configured | `python -m compileall factory scripts tests` | Syntax only. **Not a lint** |
| Unit tests | ✅ **YES** | `pytest` — 1,018 tests | ⚠ Baseline is AMBER (2 fail) |
| Integration | ⚠ **PARTIAL** | `python -m factory.demo` (end-to-end on a fake connector) | Fake connector, not a real run |
| Build | ✅ **YES** | `pip install -e .` | Trivial — one dep |
| Link check | ⛔ **NO** tool | Custom: resolve all 219 relative `.md` links | ⚠ **Written for this migration; itself unvalidated.** Test it on a known-broken link first |
| Schema validation | ⚠ **PARTIAL** | `yaml.safe_load` on every `.yaml`; `json.load` on every `.json` | **Parse-only.** No schema is enforced except the new `factory/progress.py` |
| Duplicate detection | ✅ **YES** | `scratchpad/census.py` SHA-256 | Reliable |
| Doc-reference check | ⚠ **PARTIAL** | I4 above | Covers `factory/` only, not `scripts/`/`tests/` docstrings |
| **Rendered-surface** | ✅ **YES** | 8 existing `render_check_*.py` + new `render_check_tracker.py` | ⭐ The strongest instrument here |

⭐ **The repository's strongest validation is rendered-surface capture, not tests.** Eight render
checks already write labelled light/dark × 760/1100/1440 evidence into `docs/evidence/`. The tracker
UI is validated the same way — and per the estate's own rule, **a query-layer pass is not a rendered
pass**: a repoint here once passed DAX parity while every visual showed "Error loading data".

---

## 5. Batch 9 — full verification

### 5.1 Structural

| Check | Pass condition |
|---|---|
| `pytest` | **exactly** `2 failed, 1016 passed, 2 xfailed` |
| `pip install -e ".[dev]"` | succeeds |
| `python -m factory.demo` | completes |
| `git ls-files \| wc -l` | ≥ 892 |
| All `.yaml` / `.json` | parse |
| `docs/raw_research/` census | **byte-identical** to baseline |
| Runtime `docs/` paths (I4) | all resolve |
| `.gitignore` | every rule names an existing path; nothing newly visible |
| 219 relative `.md` links | resolve |

### 5.2 Content

| Check | Pass condition |
|---|---|
| Index currency | `corpus_manifest.yaml` `coverage` matches its own regeneration command |
| Index preservation | the 168 pre-existing records byte-identical; **additions only** |
| Canonical purity | ⛔ every file in `docs/architecture/canonical/` cites code, a test, or measured evidence |
| Proposed honesty | every `proposed/*.md` states its measured occurrence count and `0 in code` |
| Duplicates | 54 groups still present; **0 deleted** |
| Secrets | credential scan returns only the 2 known fixtures |
| Provenance | every extracted/converted file carries source path + SHA-256 |

### 5.3 ⭐ The falsifiable structural test

From `04` §7 — the claim the whole structure makes:

> Pick three CELL OS concepts at random. Resolve *"is this built?"* **from the document's path
> alone.** Check each answer against `docs/agent-army/CURRENT_STATE.md` (code-measured, tier 2).

**Pass:** all three agree. **Fail:** any disagreement — and **the instrument is right, the structure
is wrong.** This is the only check that tests whether the restructure achieved anything, rather than
whether it broke anything.

### 5.4 Tracker-specific (if Batch 8 ran)

| Check | Pass condition |
|---|---|
| `test_complete_requires_evidence` | ⭐ **demonstrated failing** on a bad fixture before passing on a good one |
| `test_forecast_refuses_below_eight_active_days` | ⭐ **demonstrated firing** |
| `test_forecast_is_reproducible` | same seed → same P50/P80 |
| `test_forecast_moves_in_the_right_direction` | +velocity earlier; +scope later; +blocker ≥ |
| `test_no_progress_number_is_hand_written_in_html` | passes |
| `test_every_ticket_command_resolves` | every `session_command` names a real ticket |
| Views current | regenerated `.json`/`.md` byte-identical to disk |
| **Rendered pass** | all 7 views paint, 3 breakpoints × 2 themes + no-JS |
| **Interaction pass** | every board filter toggled; **inert ones recorded as findings** |

⛔ **Two negative controls (starred) outrank every positive test.** `factory/evals.py` exists to
answer *"can the contract actually fail?"* An evidence gate and a forecast honesty-gate that have
never been seen refusing are in precisely the position `README.md` Part I is organised against:
capable, unmeasured.

---

## 6. Final verdict rule

| Verdict | Condition |
|---|---|
| **`GREEN`** | All required validation passed |
| **`AMBER`** | Completed with documented limitations |
| **`RED`** | Validation failed, or the repository is not operational |

### ⚠ 6.1 `GREEN` is unreachable, and this is known before Phase 2 starts

`GREEN` requires *"all required validation passed."* The baseline carries **2 pre-existing failures
that Phase 2 must not fix** (§1.1), and **five validation classes do not exist** (§4: formatting,
lint, real integration, schema enforcement, complete doc-reference).

> ## **The honest best outcome is `AMBER`.**

⭐ **Stating this now is the point.** At the end of a long migration there is real pressure to reach
a colour — and the cheapest route to `GREEN` would be to fix F101 and delete the control. Naming the
ceiling in advance removes the temptation and makes `AMBER` the *expected* result rather than a
disappointment.

`AMBER` will be reported with the exact limitations enumerated: 2 pre-existing failures (unrelated,
unfixed, deliberately), 5 absent validation classes, ~35 untracked moves recoverable only by inverse
manifest, 4 unreadable CELL OS binaries, and 4 worktrees whose branches were not reconciled.

**`RED` if:** pytest degrades, a `raw_research/` hash changes, a runtime path stops resolving, an
ignored path becomes visible, or a tracked file disappears.

---

## 7. What this plan cannot validate

Stated plainly, because an unstated limitation reads as a covered one.

| Cannot validate | Why | Consequence |
|---|---|---|
| That the new structure is *better* | No instrument for it | §5.3 is the closest available, and it is a proxy |
| That the 4 unreadable CELL OS binaries don't contradict the plan | ⛔ 669 KB unreadable; no `.xlsx`/`.pdf` converter | Verdicts in `06` §4 stay **provisional** |
| That the 4 worktree branches will merge cleanly | Not measured; merging is a separate decision | Decision D-1 |
| That no client-identifying content exists in moved files | AF-RELEASE-GATE-01 measured it and found it **already public**, and is **BLOCKED** | ⛔ Unchanged by this migration. **No push.** |
| That the forecast engine's numbers are *right* | Only that it is reproducible, refuses without history, and moves in the right direction | ⚠ **A reproducible wrong number is still wrong.** ⭐ Its real validation is comparing a P50 against an actual completion — which cannot happen until a milestone completes |
| That documentation *content* is correct | Only that links resolve and files exist | Out of scope |

⭐ **The last row deserves emphasis.** The tracker will produce a date on day one, and nothing will
have tested that date against reality. Per `README.md` §V.2 its basis is **`PROXY`** until at least
one milestone completes — and `04` §8.5 requires the UI to render it as such rather than as a
measured number in a small font.
