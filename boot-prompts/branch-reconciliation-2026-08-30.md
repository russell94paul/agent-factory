# Boot — reconcile the two remaining branches, and fix the grader they both touch

**Written:** 2026-08-30, 00:40, at the end of the build-vs-adopt session.
**Companions:** `phase-0-event-ledger-2026-08-30.md` (what comes after this),
`build-vs-adopt-2026-08-29.md` (the decision record).

**Scope:** two unmerged branches and one data defect. They are **one sitting, not three**, because
`lane/certify` already contains the fix for the data defect — see §2.

---

## `next:` **Merge `lane/certify` into main, resolving the corpus five lines at a time.**

Not `lane/control-plane-renamed` first: `lane/certify` is 4 commits against 31, its conflicts are
fully characterised below, and it carries the fix for a defect that is currently live on main.
Doing it first also removes the blueprint/corpus question from the other merge's path.

⛔ **Do not merge either branch by taking `--ours` or `--theirs` wholesale.** In both cases each
side is right about something and wrong about something else, and the wrong choice is silent.

---

## 0. State, measured 2026-08-30 00:40

```
main                        7684f7e   local == personal/main   ✅ pushed
feat/readiness-generator    8dc4eac   0 ahead / 1 BEHIND main
```

⚠ **`main` moved past `feat/readiness-generator` tonight.** Main was a **one-commit skeleton from
2026-08-20** until 00:30, when it took 199 commits by fast-forward plus a merge of `lane/artifact`.
**Decide early whether work continues on `feat/readiness-generator` or moves to `main`** — the branch
is now behind, and a session that commits to it will re-diverge immediately. Fast-forwarding it is
one command and probably right:

```bash
git fetch . main:feat/readiness-generator     # only if it is not checked out anywhere
```

**Already merged, nothing to do:** `trial/wave0-rescue` (144 commits, fully contained),
`feature/phase-a-green-contract` (1, contained), `lane/artifact` (5, merged at `7684f7e`),
**`lane/control-plane` (86, fully contained in `lane/control-plane-renamed` — merge the renamed
branch and this one is covered; do not merge both)**.

⚠ **You are not alone in this checkout.** `agent-factory-25` was live and busy at 00:40 with
`factory/readiness.py` and `tests/test_readiness_probes_can_pass.py` **modified but uncommitted** —
and those are the same files `lane/control-plane-renamed` conflicts on. **Check whether that session
has landed its work before starting §3, or you will resolve a conflict against a moving target.**

```bash
git status --short            # anything you did not write is someone else's
python -c "from factory import sessions; print(sessions.collisions())"
```

---

## 1. ⛔ The two rules that govern everything below

**Rule 1 — never `git add` then `git commit` in this checkout.** On 2026-08-29 a concurrent
session's `git add` landed **three of its files inside a commit of mine**, under my message, between
my stage and my commit. Staging by path did not prevent it. Use:

```bash
git commit -F <msgfile> -- <explicit paths>      # bypasses the index entirely
```

Recovery, if it happens anyway: `git reset --soft HEAD~1`, `git restore --staged <their files>`,
re-commit with the pathspec form. The working tree is never touched by a soft reset.

**Rule 2 — merge in a temporary worktree, never by checking out main here.** The primary checkout
holds another session's uncommitted work. This is how tonight's merge was done safely:

```bash
WT="$TMP/merge-main"
git worktree add "$WT" main
cd "$WT" && git merge --no-ff lane/certify        # resolve here
git push personal main:main
cd - && git worktree remove "$WT"
```

---

## 2. ⭐ `lane/certify` — 4 commits, and it already fixes a live defect on main

### What it is

Not a rival implementation. **The same work, forked.** `main`'s `factory/live_probes.py` came from
`6872aee`; the lane's came from `6d60a6b`; they differ by **6 insertions / 23 deletions** (273 lines
vs 256). Then `62597d8` *("redact client identifiers from the public repo")* renamed things on main
only, and the two drifted.

```
c80ce56  certify(A1,A5): fix six real defects an opus review found in the probe wiring
c4dc92d  docs(findings): renumber F11/F12 -> F30/F31 per cross-lane id-block scheme
9eba253  certify(A1,A5): evidence file + findings entries (F11, F12)
6d60a6b  certify(A1,A5): wire real instruments for windsorai@GEP config + regression suite
```

8 files, +754/−8. Five conflict:

```
CONFLICT (content):  evals/MANIFEST.sha256
CONFLICT (content):  evals/corpus/windsorai-2026-08-20.json
CONFLICT (content):  factory/certify.py
CONFLICT (add/add):  factory/live_probes.py
CONFLICT (add/add):  tests/test_live_probes.py
```

### ⭐ The corpus conflict looks enormous and is not — it is FIVE LINES

`git diff` reports 213 insertions / 213 deletions because the two sides are formatted differently
(6,762 bytes vs 6,534, both LF). **With `--ignore-all-space` the real difference is 5 lines, and
each side is right about a different half:**

| Line | main | lane/certify | **TAKE** |
|---|---|---|---|
| `"client"` | `CLIENT-A` | `GEP` | ⬅ **main** — the redaction was deliberate |
| `"table"` | `QA_DG1_CLIENT-A_…` | `QA_DG1_GEP_…` | ⬅ **main** |
| `"id"` | `dep-windsorai-client-a` | `dep-windsorai-gep` | ⬅ **main** |
| `constructed[0]` | `WindsorAiConnection` | **`WindsorAIConnection`** | ➡ **lane** — the real class |
| `constructed[1]` | `WindsorAiOptions` | **`WindsorAIOptions`** | ➡ **lane** |

Reproduce it before trusting this table:

```bash
git diff --ignore-all-space main:evals/corpus/windsorai-2026-08-20.json \
                            lane/certify:evals/corpus/windsorai-2026-08-20.json
```

### ⭐ Why the class-name half matters — this is the defect that is live on main right now

**`main`'s corpus records class names that do not exist.** The real classes capitalise the
initialism: `WindsorAIConnection`, `WindsorAIOptions`. Proven by running the instrument:

```bash
python -c "import sys; sys.path.insert(0,'.'); from factory.live_probes import WindsorAiGepProbes; print(WindsorAiGepProbes().config({}))"
# {'constructed': ['WindsorAIConnection', 'WindsorAIOptions'], 'accounts': [...6...], 'fields_count': 27}
```

`blueprints/windsorai_client_a.yaml:23-25` carries the same wrong names, under a comment that says
**"DERIVED from … naming convention. Not yet read from source."** A guess, honestly labelled as a
guess — falsified within seconds of a real instrument being pointed at it, on 2026-08-29 (F79).

⚠ **And the corpus's provenance claims `"MEASURED — replayed from the run's own evidence"`.** A real
run would have constructed the real classes. **That field was authored from the blueprint's guess,
not measured** — so the corpus carries a fabricated-by-inheritance value under a MEASURED label.
`lane/certify` already has it right. Say so explicitly in the re-pin `--why`, labelled as the
inference it is.

### The blueprint half — do NOT just fix it on its own

Correcting `blueprints/windsorai_client_a.yaml` to the real class names **turns A1 green and breaks
5 calibration tests**, because main's corpus records the wrong names and `calibration_target()` reads
the class names from the *blueprint*. That was tested on 2026-08-29 and reverted:

```
test_connector_contract.py::test_known_good_world_is_green                          FAILED
test_connector_contract.py::test_assertion_fails_when_its_subject_breaks[A1-…]      FAILED
test_connector_contract.py::test_an_unscoped_target_cannot_certify_tenancy          FAILED
test_evaluator_isolation.py::test_the_known_good_world_still_scores_green_…         FAILED
test_evaluator_isolation.py::test_a_verdict_can_be_read_back_but_not_written        FAILED
```

**Blueprint and corpus must move together, in one commit.** That is why this is the same sitting as
the merge.

⛔ **The attractive shortcut is a trap.** `calibration_target()` (`factory/calibration.py:40-47`)
already overrides `allowed_tenants` from the corpus so *"the world and the target cannot drift
apart"*, and it is tempting to extend that to the class names. **Don't.** In calibration `CtxProbes`
returns the corpus's recorded `constructed` list and A1 compares it against the target's *declared*
classes. Sourcing both from the corpus makes A1 compare the world to itself — **an assertion that
cannot fail**, the exact anti-pattern `wiki/concepts/patterns/answerability-guard.md` names. The
override is safe for tenants because the rows are a separate record; it is vacuous for class names.

### The other three conflicts

- **`factory/live_probes.py`** (add/add). Base on **main's 273-line version** — it carries tonight's
  `LIVE_CLIENTS` fix (§below) and the `_BlindWindsorAiProbes` distinction. Then read the lane's
  `c80ce56` *"fix six real defects an opus review found in the probe wiring"* and port anything main
  lacks. **That commit is the highest-value unread thing in this merge** — six reviewed defect fixes.
- **`tests/test_live_probes.py`** (add/add). Same rule: main's version has two controls added
  2026-08-29 that must survive — `test_shipped_blueprint_resolves_to_a_live_instrument` and
  `test_live_clients_covers_the_shipped_blueprints_client`. Union the two files; do not choose.
- **`factory/certify.py`**. Main's live path is now
  `build_contract(target, probes_for(target)).run({})` (`8dc4eac`). Keep it.
- **`evals/MANIFEST.sha256`** — do not hand-merge. Resolve the corpus first, then **re-pin** (§below).
- **`blueprints/windsorai_gep.yaml`** vs `windsorai_client_a.yaml` — the lane has the pre-redaction
  filename. **Keep main's `windsorai_client_a.yaml` and delete the lane's**; the redaction was
  deliberate. Check git does not record it as a rename and silently resurrect the old name.

### Re-pinning — the sanctioned path, and it refuses to run without a reason

```bash
python scripts/pin_corpus.py --why "the recorded constructed classes carried the blueprint's guessed \
names; the real classes capitalise the initialism (WindsorAIConnection/WindsorAIOptions), measured \
by WindsorAiGepProbes.config() against the prefect-connectors checkout. lane/certify already had \
this right; main's copy inherited the guess under a MEASURED provenance label."
```

Its own docstring: *"the only sanctioned way to change the pin … refuses to run without a stated
reason, because 'why did the grader change' is exactly the question a silent re-pin destroys."*
It prints old and new hashes and a diff summary. **Commit the corpus and the manifest in the same
commit, with the `--why` text in the message.**

### Definition of done for §2

```bash
# 1. the live path produces real verdicts, and A1 is now green
python -m factory.certify blueprints/windsorai_client_a.yaml
#    expect: A1 PASS "constructed 2 classes, 6 account(s)"
#            A5 FAIL  "1 failing test(s)"      <- REAL, the sibling suite has one
#            10 UNMEASURABLE, aggregate FAIL, exit 1

# 2. calibration still green
python -m factory.certify blueprints/windsorai_client_a.yaml --calibrate
#    must print "REPLAYED, not a live measurement"

# 3. no regression — the discriminating subset, 90 passed on 2026-08-29 both sides
python -m pytest -q -p no:cacheprovider tests/test_connector_contract.py tests/test_contract.py \
  tests/test_corpus.py tests/test_blueprint.py tests/test_evaluator_isolation.py \
  tests/test_measurement_window.py tests/test_eval_can_fail.py

# 4. the probe controls survive
python -m pytest -q tests/test_live_probes.py
```

⛔ **A1 `PASS` is the goal; aggregate `PASS` is a bug.** Ten assertions remain uninstrumented, so the
contract must still report `FAIL` or `UNMEASURABLE` and exit non-zero. **If the aggregate goes green,
something is rounding up — stop and find it.** That is the whole thesis of this repo in one check.

---

## 3. `lane/control-plane-renamed` — 31 commits, and one number should scare you

Merge **only** this branch; `lane/control-plane` (86 commits) is fully contained in it.

27 files, **+6,426/−82**. Most is new and conflict-free — `factory/workplan.py` (390),
`scripts/mutate_readiness_probes.py` (240), `scripts/dashboard_cap_override_probe.py` (292),
`scripts/sessions_render_probe.py`, `scripts/reconcile_pipeline_records.py`, and three test files.
**Only two files conflict:**

```
CONFLICT (content):  factory/readiness.py       598 added / 338 removed
CONFLICT (content):  scripts/local_tracker.py   183 added / 1,451 REMOVED
```

⛔ **That 1,451 is the danger.** It does **not** mean the lane deletes 1,451 lines of work. It means
**main's tracker grew by ~1,451 lines after this lane branched** — main's is 2,575 lines today. A
naive `--theirs`, or accepting the lane's file wholesale, **deletes most of the tracker.**

**Resolve it the other way round: keep main's `local_tracker.py` as the base and port the lane's
123-line delta onto it.** Read `git diff main...lane/control-plane-renamed -- scripts/local_tracker.py`
and apply the intent, not the file.

`factory/readiness.py` is a genuine reconciliation of two evolutions of the same gates. ⚠ **And a
live session had it modified and uncommitted at 00:40** — resolve against what is committed, after
that session lands, not against a moving working tree.

**What this branch is worth reading before merging** — the log is unusually honest and several
commits are corrections of its own earlier claims:

```
c5c7e83  test(reaper): the test proving F30 fixed had F30's own defect
02f5391  docs(findings): correct F32's basis — 288 is DERIVED, and the audit sizes are simulation figures
a031241  docs(evidence): the regeneration command in this file was the trap
2fa93c7  docs(control-plane): what the independent read found, including that this file was wrong
```

⚠ **Findings-number collisions are a live hazard across these branches.** `lane/certify` renumbered
`F11/F12 → F30/F31`; `lane/artifact` renumbered `F11-F13 → F50-F52`; and on 2026-08-29 two sessions
independently produced colliding `F78` and `F79` (resolved when the other session renumbered to
`F80/F81` after being told). **Check `ls docs/findings.d/` and `docs/findings.md` for duplicate ids
after every merge**, and prefer a block per branch.

### Definition of done for §3

```bash
python -m factory.launch            # states its own basis; use this, NOT pytest, as the baseline
python -m factory.readiness
wc -l scripts/local_tracker.py      # must still be ~2,575+, NOT ~1,100
```

⚠ **Do not use `pytest -q` as the baseline.** ~20 tests read the `prefect-connectors` checkout live
and other sessions move it. On 2026-08-29 the count moved **388 → 409 within one hour** with no
change from the measuring session, and the suite takes **20+ minutes** because `test_live_probes`
shells out to the sibling repo's 826-test suite several times. **Never quote a suite number without
the command AND the sibling condition:**

```bash
git -C ../prefect-connectors branch --show-current      # was: chore/artefact-homes
git -C ../prefect-connectors status --porcelain | wc -l # was: 29
python -c "from factory.readiness import CONNECTORS; print((CONNECTORS/'tests'/'orchestrator'/'mutate_control_plane.py').is_file())"   # was: False
```

The 21 failures seen on 2026-08-29 were **that missing file**, not a regression. Do not "fix" them.

---

## 4. What is NOT done, plainly

- **Neither merge is started.** Both branches are exactly as they were.
- **The blueprint is still wrong on main.** `windsorai_client_a.yaml:23-25` declares
  `WindsorAiConnection`/`WindsorAiOptions`; A1 correctly reports `FAIL` because of it. It was
  corrected on 2026-08-29 and **deliberately reverted** because it breaks 5 calibration tests until
  the corpus moves with it.
- **The corpus on main still carries the wrong class names** under a `MEASURED` provenance label.
- **`factory/events.py` does not exist.** Phase 0 has not started — see
  `phase-0-event-ledger-2026-08-30.md`. This branch work is its predecessor, not a substitute.
- **No connector has been certified.** `certified NOT_RUN`, `breadth 1 case, 0 strata`. A1/A5 now
  produce real verdicts; ten assertions still have no instrument.
- **`lane/certify`'s `c80ce56` — "six real defects an opus review found" — has not been read by
  anyone on main.** It is the most likely source of a defect main still has.

---

## 5. Gotchas earned, all measured

- ⛔ **`git add` + `git commit` is unsafe here** (Rule 1). Use `git commit -F msg -- <paths>`.
- ⛔ **`gh api search/code` and `gh search code` are BLIND on this workstation** — they returned **0**
  for a string verified to exist, **with no error** (a `gho_` OAuth token without code-search scope).
  **A code-search zero without a positive control is NOT-VISIBLE, not ABSENT.** Use
  `gh api repos/OWNER/REPO/contents/PATH` or fetch raw files.
- ⚠ **`WebFetch` returns a small model's *summary*, even of raw source** — `DOCUMENTED`-tier, never
  `OBSERVED`. Use `curl`/`gh api` for anything that will carry a verdict.
- ⚠ **A `git diff` line count is not a difficulty estimate.** The corpus showed 213/213 and was five
  lines. Always re-check with `--ignore-all-space` before deciding a merge is hard.
- ⚠ **A hand-maintained list drifts silently.** `probes_for` matched `client == "GEP"` while the
  redaction had renamed the blueprint to `CLIENT-A`, so it fell through to the refusing base class and
  reported *"no instrument configured"* — **byte-identical to the pre-wiring baseline. Nothing
  failed.** Fifth such list in this repo (`TeamSpec.version`, `synthesis.session_prompt`,
  `local_tracker._HOT`, `lanes.LANES`, `probes_for`). **If a list can be derived from the thing it
  tracks, derive it, and pair it with a test that fails when it drifts.**
- ⚠ **`factory/lanes.py` is stale.** The `certify` lane's prompt says *"no probe is wired to
  anything"* and tells an agent to build A1/A5 — work that shipped in `6872aee`. **Do not launch it.**
  `control-plane` and `judgement` both `touch=orchestrator/pipelines.py`, i.e. the **other repo**.
- ⚠ **Four of five bounding gates cannot move from this repo** — `cap`, `ceiling`, `concurrency`,
  `reaper` all grep `prefect-connectors` (F77, F78). Their staying red says nothing about work here.
  **The movable verdicts are `certified`, `breadth`, `corpus`.**

---

## 6. Where things live

| Path | What |
|---|---|
| `factory/certify.py:105` | The live path. Now `probes_for(target)`; was hard-coded `Probes()` |
| `factory/live_probes.py` | `WindsorAiGepProbes` (A1/A5, no credential needed) · `probes_for` · `LIVE_CLIENTS` |
| `factory/calibration.py:40-47` | `calibration_target()` — overrides tenants only. **Do not extend to class names** |
| `blueprints/windsorai_client_a.yaml:23-25` | The wrong class names. Fix WITH the corpus, not alone |
| `evals/corpus/windsorai-2026-08-20.json` | The known-good world. 5 real lines differ from the lane |
| `scripts/pin_corpus.py` | The only sanctioned re-pin. Refuses without `--why` |
| `docs/findings.d/F77, F78, F79` | Which repo each gate reads; the unwired instrument |
| `docs/reviews/build-vs-adopt-2026-08-29.md` | Why build not adopt; what UNMEASURABLE must survive |
| `boot-prompts/phase-0-event-ledger-2026-08-30.md` | What comes after this |
