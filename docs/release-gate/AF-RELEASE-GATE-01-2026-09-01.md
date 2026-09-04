# AF-RELEASE-GATE-01 — publication boundary for `agent-factory`

**Task** `52407de5` · measured 2026-09-01 10:15–10:50 UTC · local `main` at `bc676d6`
**Status: BLOCKED — requires human authority. Nothing was pushed, nothing was deleted, nothing
was rewritten.**

**Self-classification: NEEDS_SANITIZATION.** Measured, not asserted — a full-token sweep over this
file returns:

| class | in this document |
|---|---|
| credential **values** of any kind | **0** |
| monetary/spend figures, brand name | **0** |
| Snowflake account locator, client database name, admin username | **0** |
| Key Vault **secret names** | **2** — `§14` rotation table only |
| file paths that encode the client name | 6 |
| the engagement named in prose | 1 — `§6`/B1 |

The two secret **names** are deliberate: a rotation recommendation that does not say *which* secret
is unactionable, and both names are already public on `personal/main` in `scripts/credential_use.py`
(§12.2). They are names, never values.

The client-name paths are unavoidable — they are the identifiers of the exposed files — and are
themselves already public, so this document adds nothing new. It is still not unconditionally
`PUSH_SAFE`, and is written and left **uncommitted** on that basis. §13.1–§13.2 raise the bar
further and must be removed wholesale, not redacted, in any public version.

---

## 0. The premise that did not survive measurement

The brief frames this as a decision to be taken **before anything is pushed**. That framing is
wrong, and it is wrong in the direction that matters.

**Client-identifying and client-commercial content is already published on the public remote.**
Not staged, not pending — served by GitHub right now, to anyone, without authentication.

The brief's own gotcha predicted this and was not applied to the already-pushed side of the
boundary:

> ⭐ *"A commit whose subject looks like tooling can still carry a client name in a fixture, a
> screenshot or an evidence file."*

`b28c334` — subject *"docs(findings): three evidenced findings filed, and the R3 identity
prepared"* — added the client-facing review artifact. The brief grouped it under "Findings / boot"
with no warning marker. It is public.

Everything below therefore splits into **exposure already incurred** (§2, needs a decision Paul
alone can take) and **exposure not yet incurred** (§3–§4, the original question).

---

## 1. Exact local-vs-remote commit boundary

| measurement | value | command |
|---|---|---|
| local branch / HEAD | `main` / `bc676d6` | `git rev-parse --abbrev-ref HEAD; git rev-parse HEAD` |
| public remote main | `personal/main` `8b73f4f` | `git rev-parse personal/main` (after `git fetch personal`) |
| ahead of `personal/main` | **20** | `git rev-list --count personal/main..main` |
| behind `personal/main` | **0** | `git rev-list --count main..personal/main` |
| ahead of **all** remote refs | **16** | `git log --oneline main --not --remotes=personal` |
| repo visibility | **PUBLIC** | `gh repo view --json visibility` |
| forks / stars / watchers | **0 / 0 / 0** | `gh api repos/…` |
| repo created | 2026-08-29T19:55:49Z | `gh api repos/…` |

⭐ **The brief's "19 commits ahead" is not the publication boundary.** Twenty commits are ahead of
`personal/main`, but **four of them are already published** on another public branch:

```
b338324  ab9ee86  64dfff5  b28c334   →  refs/heads/reliability/recurrence-preflight
```

Verified per-commit with `git branch -r --contains <sha>`. The public remote carries **six
branches**, not one:

```
main                                       8b73f4f
reliability/recurrence-preflight           b338324   ← carries client content
trial/wave0-rescue                         6872aee
fix/fifth-verdict-apparatus-error          2adf9a2
docs/agent-army-research-separation        ec1c6c6
claude/agent-factory-architecture-doc-…    eb20675
```

A boundary computed only against `personal/main` misses five publication surfaces.

**Unpublished set: 16 commits, 125 files, +25,567 / −40 lines** (`git diff --stat personal/main...main`).

**Local branches.** `docs/agent-army-research-separation`, `fix/fifth-verdict-apparatus-error`,
`reliability/recurrence-preflight` and `switchboard/p0` are all ancestors of `main`
(`git merge-base --is-ancestor` exit 0). Only `mission/marketing-model-v1` is unmerged: **26**
commits ahead of `personal/main`, 0 behind, tip `efb05cf` on no remote ref.

---

## 2. Exposure already incurred — the part that is not a decision about the future

### 2.1 What is public

| surface | measurement |
|---|---|
| files naming the client, `personal/main` | **9** |
| files naming the client, `reliability/recurrence-preflight` | **17** |
| files naming the client, `trial/wave0-rescue` | 9 |
| files naming the client, `claude/agent-factory-architecture-doc-…` | 9 |
| files naming the client, `fix/fifth-verdict-apparatus-error` | 5 |
| files naming the client, `docs/agent-army-research-separation` | 3 |

Regenerate: `git grep -il "<client>" <ref> -- . | wc -l`

⛔ **Correction to the first issue of this document.** It reported *"0 spend files on `personal/main`"*
from `git grep -clE …`. **`-c` and `-l` together is a broken flag combination** — it returned an
empty set, not a zero count, and I read the empty set as a measurement. Re-measured with `-ilE`:

**`personal/main` — the default branch — carries the brand name in 3 files, client spend figures in
2 files, and the Snowflake account locator in 1.** The contamination is not confined to a side
branch. This is the same failure shape the global CLAUDE.md records for `&&`-chained checks: a
command whose output carries a verdict returned a plausible answer instead of an error. See §11 for
what it changes (it moves branch deletion from *sufficient* to *insufficient*).

Three items on `reliability/recurrence-preflight` carry more than the name:

| path | what it is |
|---|---|
| `docs/artifacts/client-review-navira.html` | the **client-facing review artifact**, named for the client |
| `docs/evidence/marketing-model-v1/R1-stakeholder-evidence.md` | stakeholder evidence: brand name + ad-spend figures |
| `docs/evidence/marketing-model-v1/R2-repo-wiki-diff.md` | same class |

`scripts/snowflake_bootstrap_r3.py` on that branch carries a **28-character, real-looking Snowflake
account locator** as a module constant (`ACCOUNT`, line 41). Classified structurally
(len 28, contains `.` and `-`, 5 digits, no placeholder idiom) — **the value was not printed at any
point in this session** and is not reproduced here.

### 2.2 Verified at the consumer's layer, not from local refs

Local remote-tracking refs are not proof of what GitHub serves. Both were fetched from the GitHub
API as an anonymous reader would receive them:

```
gh api ".../contents/docs/evidence/marketing-model-v1/R1-stakeholder-evidence.md?ref=reliability/recurrence-preflight"
  → 200, 43,110 bytes, 12 lines matching client name / brand / spend figures
gh api ".../contents/docs/artifacts/client-review-navira.html?ref=reliability/recurrence-preflight"
  → 200, 5 matching tokens
```

### 2.3 Exposure window

`ab9ee86` authored 2026-08-31 21:22:48 −0700; `b338324` 2026-08-31 21:30:08 −0700. Repo created
2026-08-29. Upper bound on exposure: **~3 days**. The exact push time for
`reliability/recurrence-preflight` is **NOT-RECORDED** — the `/events` API window returned pushes
only for `main`, `docs/agent-army-research-separation` and `feat/readiness-generator`, so the
absence of a reliability push event is a limit of the instrument, not evidence of no push.

0 forks / 0 stars / 0 watchers is **weak** negative evidence. It does not cover anonymous clones,
`git` fetches, crawler indexing or code-search corpora, none of which GitHub reports to the owner.

### 2.4 The rule that decides the remediation

> **For anything already published, the fix is not scrubbing.**

Deleting the branch, rewriting history or force-pushing does **not** un-publish. Treat the client
name, the review artifact, the spend figures and the account locator as **disclosed as of
2026-08-31**, and decide remediation on that basis. Scrubbing afterwards is hygiene, worth doing,
and must never be reported as the fix.

**⛔ This is Paul's call and no session should take it unilaterally.** See §6.

---

## 3. Credential scan — clean, and scoped

**SCOPE** — tracked files at `HEAD` (545 files, `git ls-files | wc -l`), plus a targeted history
sweep for key material across all refs.

| check | result |
|---|---|
| `.data/`, `.sessions/`, `.worktrees/` tracked? | **no** — `git ls-files .data .sessions .worktrees` empty. Ignores verified, not assumed. |
| key prefixes (`sk-`, `ghp_`, `xox*`, `AKIA`) + PEM blocks at HEAD | **0 hits** |
| `git log --all -S'-----BEGIN'` | 2 commits — `ed02d7b`, `4e076d8`; both are **detector/handler code**, inspected, no key material |
| assigned-secret shapes at HEAD | 6 hits, all **PLACEHOLDER or reference** |

The six: two are prose about where secrets live; one is an HMAC formula; one is the literal string
`unmeasured-a1-does-not-authenticate`; two are **Key Vault secret *names*** in
`scripts/snowflake_bootstrap_r3.py:53,59` (references, not values); one generates a random password
at runtime.

**No committed credentials.** The risk class in this repo is **client-identifying and commercial
information**, not secrets. The Snowflake `ACCOUNT` constant is an *identifier* — attack-surface
disclosure, not compromise — and it does not warrant rotation, but it does warrant not publishing.

---

## 4. Classification of every material item

### 4.1 Marginal exposure if `main` were pushed as-is

Of **35** files at `HEAD` carrying client-identifying or commercial tokens, **14 are already
published byte-identically** on some remote ref. The push would newly expose **21**:

```
boot-prompts/af-release-gate-01.md
boot-prompts/drafts/GP-319-comment-2026-09-01.md
docs/artifacts/client-review-navira.html                     (newer than the published copy)
docs/artifacts/delivery-001-case-study.html
docs/case-studies/delivery-001-marketing-model.md
docs/design/artifact-generator-proposal.md
docs/evidence/client-review-readiness-2026-09-01/README.md
docs/evidence/client-review-readiness-2026-09-01/narrative-drift.json
docs/evidence/client-review-readiness-2026-09-01/render-check-client-review.json
docs/evidence/marketing-model-v1/D1-requirements-and-uncertainty.md
docs/evidence/marketing-model-v1/R3-cartography.md
docs/evidence/marketing-model-v1/R3-preflight-readonly-proof.md
docs/findings.d/F100-…-same-moving-state.md
missions/client-review-v1/05-CLIENT-REVIEW-DEMO-RUNBOOK.md
missions/client-review-v1/06-D5-REFRESH-CONTRACT.md
missions/client-review-v1/reviews/navira-marketing-model.yaml
missions/delivery-001/case-study.yaml
scripts/meeting_ready.py
scripts/render_check_client_review.py
scripts/snowflake_bootstrap_r3.py
tests/test_client_review.py
```

Method: for every sensitive file at `HEAD`, compare its **blob sha** against the blob shas of
sensitive files across all six remote refs. Same blob ⇒ already published.

### 4.2 There is no clean cherry-pick

Sensitive lines **introduced** per unpublished commit (`git show <c> -U0 | grep '^+' | grep -ciE …`):

| commit | +sensitive | commit | +sensitive |
|---|---|---|---|
| `4e076d8` | **72** | `80854d2` | 6 |
| `4fc76a1` | **53** | `262a199` | 5 |
| `7d71a84` | **24** | `01f7e3b` | 4 |
| `10c4fe7` | 1 | `0a8b593` | 1 |
| `bc676d6` | 1 | | |
| `1d6b3a4` `c7b950a` `62cb0e4` `a55da11` `1068f59` `8fba030` `9e05b26` | **0** | | |

The three Switchboard commits and the dependency fix introduce **nothing** sensitive — but they sit
on top of `4e076d8`, `4fc76a1` and `7d71a84` in a linear history. **A push of `main` is
all-or-nothing.** Publishing the clean tooling requires rebuilding it onto `personal/main`, not
selecting commits.

### 4.3 The classification

| item | class | why |
|---|---|---|
| `1d6b3a4` `c7b950a` `62cb0e4` — Switchboard P0 | **PUSH_SAFE (content)** / blocked by ancestry | 0 sensitive lines introduced; cannot ship without their parents |
| `a55da11` — dependency fix | **PUSH_SAFE (content)** / blocked by ancestry | 0 sensitive lines |
| `1068f59` `8fba030` `9e05b26` | **PUSH_SAFE (content)** / blocked by ancestry | 0 sensitive lines |
| `7d71a84` `0a8b593` `262a199` — Client Review record | **NEEDS_SANITIZATION** | client name + review content in `missions/client-review-v1/**`, `docs/evidence/client-review-readiness-*` |
| `4fc76a1` `10c4fe7` — Artifact generator | **NEEDS_SANITIZATION** | generates and commits `docs/artifacts/client-review-navira.html` and `delivery-001-case-study.html`, both carrying spend figures |
| `4e076d8` — R3 identity / cartography | **NEEDS_SANITIZATION** | highest density; warehouse topology + Snowflake account locator |
| `80854d2` `01f7e3b` — D1 / boot | **NEEDS_SANITIZATION** | client-named requirements and uncertainty |
| `bc676d6` — this brief | **NEEDS_SANITIZATION** | names the client and the mission |
| `docs/artifacts/client-review-navira.html` (working tree) | **LOCAL_ONLY** | client-facing deliverable for a named client |
| 13 re-rendered PNGs + `render-check-client-review.json` (working tree) | **LOCAL_ONLY** | screenshots of the above |
| committed copy of the same artifact | **SUPERSEDED** | working tree is the newer render — see §4.4 |
| `docs/evidence/marketing-model-v1/pbi-ad-sales-live-2026-09-01/` (untracked) | **LOCAL_ONLY** | §7 |
| `boot-prompts/drafts/GP-319-comment-2026-09-01.md` | **LOCAL_ONLY** | unposted internal Jira comment for a real client ticket |
| `mission/marketing-model-v1` @ `efb05cf` | **LOCAL_ONLY** | 26 commits, 92 files, **44** carrying client/commercial tokens |
| `scripts/snowflake_bootstrap_r3.py` | **NEEDS_SANITIZATION** | move `ACCOUNT` to env/Key Vault lookup |
| 19 internal Jira ids (`GP-*`, `FU92-*`) in unpublished files | **NEEDS_SANITIZATION** (low) | 53 distinct ids are already public on `main` — this is pre-existing, not new |

### 4.4 The working tree is a regeneration, and the as-of semantics changed

The 15 modified files are **generated output**, not hand edits. The artifact grew 43,457 → 48,213
bytes; text per rendered variant 14,416 → 19,087 chars; summary line *"4 outcomes delivered · 6
awaiting write-up"* → *"10 outcomes delivered"*.

⚠ **The freshness stamp changed `Live` → `Last verified` (08:51 → 09:00 UTC).** That is a change in
the evidence's as-of semantics, not cosmetics. Preserve it: the committed copy asserts a liveness
claim the newer render deliberately withdraws. Classify the committed copy **SUPERSEDED** — do not
publish, do not delete.

---

## 5. Sensitive-data and publication risks, ranked

1. **A client-facing review artifact for a named client is publicly downloadable** — `b28c334` on
   `reliability/recurrence-preflight`. Verified against the GitHub API.
2. **Client ad-spend figures and a third-party brand name are public** — two evidence files, same
   branch. Verified against the GitHub API.
3. **A real-looking Snowflake account locator is public** — same branch. Identifier, not credential.
4. **The client name is public on all six branches** (3–17 files each).
5. **Pushing `main` newly exposes 21 more files** (§4.1), including the client-facing artifact at a
   *newer* revision and an unposted internal Jira comment.
6. **`git add -A` would stage the live PBI capture.** `docs/evidence/` is a tracked directory and
   the package is untracked but **not ignored**. Five sessions share this checkout. This is a live
   hazard, not a hypothetical.
7. **The public repo's test suite cannot pass for any outside reader** (§8).
8. **`git clone` fails on Windows at a deep target path** — `docs/findings.d/F96-…md` is a
   **123-character** repo-relative path. Measured: `fatal: unable to checkout working tree` at a
   ~130-char parent; `git clone` into `C:\tmp\aftest` exits 0. Conditional, not absolute.

---

## 6. Blockers requiring human authority

None of these may be taken by a session.

| # | decision | why it is Paul's |
|---|---|---|
| B1 | **Whether the already-published client content is a notifiable disclosure** under the GEP/Navira engagement | contractual and commercial; a session cannot assess client obligation |
| B2 | **Whether to make the repo private**, delete the five non-`main` branches, or leave them | deleting breaks any existing clone and does not un-publish; both options have costs only Paul can weigh |
| B3 | **Whether `agent-factory` is a public project at all** given that its evidence discipline requires committing client evidence | this is the structural question underneath §7 |
| B4 | **Whether to rewrite history** on `reliability/recurrence-preflight` | force-push is destructive and remediates nothing (§2.4) |
| B5 | **Sign-off on any sanitization mapping** (client → pseudonym, figures → orders of magnitude) before a sanitized push | a wrong mapping publishes the thing it was meant to hide |

---

## 7. Disposition — untracked PBI live-model evidence

`docs/evidence/marketing-model-v1/pbi-ad-sales-live-2026-09-01/` — 7 files:

```
README.md   raw/as-of.json  raw/dax-results.json  raw/instrument-limits.json
raw/measures.json  repro/probe.py  repro/validate.py
```

`raw/measures.json` keys are live Power BI workspace/model names for a real client, including a
production model. `raw/dax-results.json` holds measured values — per-platform sales, cost,
conversions, attributed sales, and the fact-window date range.

**Classification: LOCAL_ONLY. Unconditional.** This is the most commercially sensitive item in the
set and it is the only one still fully unexposed. It must not be committed to this repository in
any form, sanitized or otherwise — the DAX result rows *are* the client's commercial data.

**Recommended disposition:**
1. **Immediately** neutralise risk 6 by ignoring the path — this is reversible, touches nothing
   else, and closes the `git add -A` hazard:
   `docs/evidence/marketing-model-v1/pbi-ad-sales-live-*/` → `.gitignore`.
2. Move the package to the private evidence root (§9) and leave a committed **pointer** in
   `docs/evidence/marketing-model-v1/` naming the package, its as-of, and where it lives — so
   nothing downstream degrades and the record is not lost.
3. `repro/probe.py` and `repro/validate.py` are **PUSH_SAFE in isolation** — they are the
   reproduction scripts, they carry 0 sensitive tokens (measured), and they are the part that has
   reuse value. Publish those two only if the evidence discipline needs a public example.

⛔ Do not delete it. It is authoritative private evidence for the PBI verification dependency, and
the brief forbids deleting authoritative evidence to make publication easier.

---

## 8. Disposition — the `test_case_study.py` defects, and what the brief did not record

### 8.1 The brief's two defects: reproduced exactly

```
tests/test_case_study.py::test_2_completion_counts_declared_tasks_not_duplicated_children
tests/test_case_study.py::test_reconciliation_reports_divergence_rather_than_republishing
```

Primary checkout: **37 passed**. `.worktrees/switchboard`: both **FAIL** with
`assert 'UNAVAILABLE' in ('OK','DIVERGED')`. Mechanism confirmed at `tests/test_case_study.py:28`:
`ROOT = pathlib.Path(__file__).resolve().parent.parent`, then `.data/tasks.jsonl` off `ROOT`.
`.data/` is gitignored, so it exists only in the primary checkout (`.worktrees/mission` has one;
`reliability` and `switchboard` do not).

### 8.2 ⭐ Three corrections to the brief

**(a) `F105` does not exist.** The brief calls this "finding **F105**". `docs/findings.d/` holds
F20, F21, F70–F100 — 34 files. `grep -rln "F105"` across the repo returns **exactly one** file:
the brief itself. The defect was never filed. Citing an id that resolves to nothing is worse than
citing none, because it reads as already-recorded.

**(b) It is a *clone* defect, not a worktree defect.** `.data/` is gitignored, so **every fresh
clone** lacks it. Measured on a clone of `main` at `C:\tmp\aftest`: **21 tests fail.** For a public
repo that is the first thing an outside reader sees.

**(c) The blast radius is 19 tests, not 2.** Clone-only failures beyond the named pair:

| suite | clone | primary | cause |
|---|---|---|---|
| `test_mutation_anchors_still_match.py` | **17 FAIL** | pass | requires a **private sibling repo** via `$PREFECT_CONNECTORS`; `_harnesses()` finds 1 of 2 |
| `test_gate_negative_control_census.py` | 1 FAIL | pass | `.data/`-dependent |

The mutation-anchor suite is a **structural** publication problem: it asserts that both harnesses
were found and deliberately fails rather than skipping, so it can never pass for anyone without
the private `connector` checkout.

### 8.3 ⛔ Two regressions the brief does not mention, in the primary checkout

Both fail **in the primary checkout at `bc676d6`**, and both were introduced by the Switchboard
landing (`62cb0e4` added `factory/switchboard.py` and `factory/switchboard_render.py`; both guard
tests predate it and are already public).

| test | tripped by | verdict |
|---|---|---|
| `test_repo_root.py::test_no_module_computes_a_shared_data_root_from_its_own_file` | `switchboard.py:102` | **false positive** — the matched line is a **docstring stating the rule** (*"`repo.data()` and not `__file__.parent.parent`"*). The module obeys the rule; the guard matches the prohibition's own text. |
| `test_suite_cache.py::test_no_surface_claims_it_caches_nothing` | `switchboard_render.py:458` | **false positive** — same shape; the matched line is user-facing copy saying the page caches nothing. |

Neither is a real defect in the Switchboard. Both are text-matching guards with no exclusion for a
line that quotes the rule it enforces. **The handoff that landed those commits reported the
baseline as two known defects; it is four, and two of them are new.**

✅ **MEASURED, whole-suite.** A full `python -m pytest -q` in the primary checkout at `bc676d6`
ran 10:17–10:33 UTC (16 min — consistent with the brief's warning that gate-board work is minutes
per call) and returned **exactly two failures**, both listed above:

```
FAILED tests/test_repo_root.py::test_no_module_computes_a_shared_data_root_from_its_own_file
FAILED tests/test_suite_cache.py::test_no_surface_claims_it_caches_nothing
```

So the **primary baseline is 2 red, and both are regressions from the Switchboard landing.** The
brief's two named `test_case_study.py` defects do **not** appear — they are green in the primary
checkout and red only outside it. The handoff named the wrong two tests as the baseline.

**Baseline, stated once, as measured:**

| environment | failing | which |
|---|---|---|
| primary checkout `bc676d6` | **2** | the two self-matching guards (§8.3) |
| `.worktrees/switchboard` | + the 2 `test_case_study.py` tests | no `.data/` |
| fresh clone of `main` | **21** | those 2 guards + 2 case-study + 1 gate-census + 17 mutation-anchor (§8.2c) |

**Recommended disposition:** file both classes as findings (next free id is **F101**, not F105) —
one for the clone/sibling-repo test dependency, one for the two self-matching guards — and fix the
guards by excluding string literals and comments from the scan. Do not fold either into unrelated
work.

---

## 9. Recommended repository / private-evidence boundary

The structural cause of every finding above is that **this repo's evidence discipline requires
committing evidence, and some of that evidence is client-confidential.** No push policy fixes that;
only a boundary does.

**Recommended: a two-repo split.**

| | public `agent-factory` | private evidence repo |
|---|---|---|
| holds | `factory/`, `scripts/`, `tests/`, `blueprints/`, `docs/protocol/`, `docs/findings.d/`, `docs/research/`, generic evidence | `docs/evidence/marketing-model-v1/**`, `docs/evidence/client-review-readiness-*/**`, `missions/client-review-v1/**`, `missions/delivery-001/**`, `docs/case-studies/**`, `docs/artifacts/client-review-*.html`, `boot-prompts/drafts/**` |
| rule | no client name, no client figure, no client topology, no internal ticket id | authoritative; never mirrored |
| link | committed **pointers** naming package + as-of + location | — |

Enforce it mechanically, not by policy: a test that fails when a client-name pattern appears
outside the allowlisted paths. A repo that has to remember not to commit client data will fail the
way this one did — in a commit whose subject said "findings filed".

Cheaper interim if the split is deferred: `.gitignore` the client-evidence paths and keep them on
disk only. This preserves evidence-on-disk while making a push structurally unable to carry it.

---

## 10. Exact safe integration and push plan

**Nothing in this plan may run before B1–B5 in §6 are answered. No step here was executed.**

**Phase 0 — stop the bleeding (reversible, no history change).**
1. `.gitignore` the live PBI package path (§7.1). Closes risk 6.
2. Decide B2. If the branches are to go, `git push personal --delete <branch>` reduces *further*
   distribution; it does **not** un-publish, and §2.4 governs how it is reported.

**Phase 1 — establish the boundary (§9).** Until it exists, `main` is unpushable, because every
route to publishing the clean tooling runs through commits that carry client evidence (§4.2).

**Phase 2 — publish the clean tooling, by rebuild not by cherry-pick.**
1. Branch from `personal/main` (`8b73f4f`) — *not* from local `main`.
2. Port the Switchboard P0 sources, tests and its own render evidence as a fresh commit set,
   omitting every path in the §9 private column.
3. Gate: `git grep -ilE '<client>|<brand>|<figures>' HEAD` must return **0** on that branch, and
   the same grep must return 0 against the branch's full diff, not just its tree.
4. Fix the two self-matching guards (§8.3) so the branch is green in the primary checkout.
5. Clone it fresh to a short path and run the suite. Publishing a repo whose suite fails on clone
   is a defect that arrives with every reader.
6. Only then open a PR to `personal/main`.

**Phase 3 — the remainder** (client review, artifact generator, D1, R3 cartography) stays
**NEEDS_SANITIZATION** and does not move until B5 gives a signed-off mapping.

**`mission/marketing-model-v1` is not merged, not rebased and not touched.** The brief forbids
merging it to ease publication, and its 44 sensitive files confirm the standing decision.

---

## Regeneration

Every count in this document was measured 2026-09-01 and carries its command. Re-run before acting:

```bash
git fetch personal
git rev-list --count personal/main..main                 # 20
git log --oneline main --not --remotes=personal | wc -l  # 16
git ls-remote --heads personal                           # 6 branches
git ls-files | wc -l                                     # 545
git ls-files docs/findings.d | wc -l                     # 34
git diff --stat personal/main...main | tail -1           # 125 files
```

---

# PART II — REMEDIATION PLAN

**Written 2026-09-01 after containment commit `ab13977`. This is a plan. Nothing in Part II was
executed.** No branch deleted, no force-push, no history rewrite, no amend of any pre-existing
commit, no private evidence scrubbed, nothing pushed. No secret was retrieved from any vault at any
point in this session, and no credential value appears anywhere in this document.

## 11. Exposure inventory — exact refs, exact SHAs, exact classes

Re-measured 2026-09-01 after `git fetch personal`. Regenerate with `git ls-remote --heads personal`
and `git grep -ilE <pattern> <ref> -- . | wc -l`.

| remote ref | SHA | client name | spend figures | brand | internal Jira ids | account locator | prod vault/secret names |
|---|---|---|---|---|---|---|---|
| `refs/heads/main` | `8b73f4f` | 9 | **2** | **3** | 29 | **1** | **3** |
| `refs/heads/reliability/recurrence-preflight` | `b338324` | **17** | **4** | **7** | 42 | **2** | 3 |
| `refs/heads/trial/wave0-rescue` | `6872aee` | 9 | 0 | 1 | 3 | 0 | 0 |
| `refs/heads/fix/fifth-verdict-apparatus-error` | `2adf9a2` | 5 | 0 | 1 | 22 | 0 | 1 |
| `refs/heads/docs/agent-army-research-separation` | `ec1c6c6` | 3 | 0 | 1 | 7 | 0 | 1 |
| `refs/heads/claude/agent-factory-architecture-doc-by7il6` | `eb20675` | 9 | 0 | 1 | 2 | 0 | 1 |

**All six refs expose client-identifying material. Five of six expose a prod or non-prod vault
identifier. There is no clean ref.**

**Forks: 0.** `gh api repos/russell94paul/agent-factory` → `forks_count: 0`, `network_count: 0`,
`stargazers: 0`, `subscribers: 0`, and `/forks` returns an empty list. **No public fork exists as at
2026-09-01 10:15 UTC.** This is the single most favourable fact in the whole assessment and it is
perishable — it is the reason a visibility change is worth doing now rather than after deliberation.

⚠ It is **weak** negative evidence. It does not cover anonymous clones, unauthenticated fetches,
crawler indexing, or third-party code-search corpora. GitHub reports none of those to the owner.
Verdict on "has anyone taken a copy": **NOT-VISIBLE**, not ZERO.

## 12. Commercial/client material vs credential-like material

### 12.1 Merely commercial or client-identifying — no credential dimension

| where | what |
|---|---|
| `reliability/…` `docs/artifacts/client-review-navira.html` (`b28c334`) | client-facing review artifact |
| `reliability/…` `docs/evidence/marketing-model-v1/R1-…md`, `R2-…md` (`ab9ee86`) | ad-spend figures, third-party brand |
| `main` `boot-prompts/mission-commander-…md`, `mission-handoff-…md` | a single ad-spend figure each |
| `main` `docs/specs/marketing-model-reconstruction-v1.md`, `docs/research/answers/R4-…md` | brand + client name + Jira keys |
| all six refs | client name; 2–42 internal Jira ids per ref |

**Nothing here is rotatable.** These are facts about a client's business. The only remediations are
visibility change, history rewrite, or acceptance.

### 12.2 Credential-*like* — identifiers and targeting information, never values

Concentrated in two published files:

**`scripts/snowflake_bootstrap_r3.py`** — on `reliability/recurrence-preflight` (274 lines):

| constant | published? | class |
|---|---|---|
| `ACCOUNT` (28 chars, `<locator>.<region>.<cloud>`) | **yes** | connection endpoint identifier |
| `DATABASE` (12 chars, client-named TEST db) | **yes** | topology |
| `VAULT` (15 chars, the **non-prod** Azure Key Vault) | **yes** | secret-store name |
| `ADMIN_SECRET` (23 chars, Key Vault secret **name**) | **yes** | secret name, not value |
| `RO_SECRET` / `RO_USER` / `RO_ROLE` | **yes** | the read-only identity this script creates |
| `ADMIN_USER` | **published value differs from local value** | see 12.3 |

**`scripts/credential_use.py`** — on `personal/main`, lines 4 and 74: usage examples naming the
**production** Key Vault and the **production** admin secret name. `docs/research/R19-…md:128` adds
infrastructure topology (Blob, Container Apps, Docker/Portainer on named-site VMs).

⛔ **Correction, from the Step 0 capture (§20).** §12.2 as first written attributed the *full*
credential-like tuple to `snowflake_bootstrap_r3.py` on `reliability/recurrence-preflight`, and only
the account locator to `main`. The class-labelled capture shows that is wrong:

`boot-prompts/mission-wave1-checkpoint-2026-09-01.md`, introduced in **`ddea66d`**, is on
**`main`** and carries **all four** credential-like classes at once — account locator, client TEST
database, Key Vault name and Key Vault secret name.

**The complete targeting tuple is on the default branch**, not only on a side branch. It reaches
`main` through a *boot prompt*, not through the Snowflake script — which is why §18 insists
`boot-prompts/` be reviewed file-by-file rather than re-admitted as a class, and why §16's
"deletion cannot clear `main`" verdict holds for the credential-like material too, not just the
commercial material.

Also newly measured: the client TEST database name appears on **all six** refs, including the two
research branches and the architecture-spec branch.

### 12.3 ⭐ The one genuinely good result: the real admin username is NOT published

The published copy names an admin user **19 characters** long. The local unpublished copy
(`4e076d8`) names a different, **16-character** personal-admin account. Compared by equality
in memory, values not printed:

```
published ADMIN_USER == local HEAD ADMIN_USER  ->  False
published ADMIN_USER == "TEST_DG1_CORE_ADMIN"  ->  True
ADMIN_SECRET / VAULT / DATABASE  published == HEAD  ->  True
```

The published name is the one the repo's own comment documents as **wrong** — it holds only `USAGE`,
is marked *"Do NOT use"* in the wiki, and a measured login with the paired secret returned
`250001 (08001) Incorrect username or password`. The published file is therefore a **decoy admin
user beside a real endpoint**. The correct admin username, and the wiki citations that bind secret
to user, exist only in the unpublished commit.

## 13. Can the credential-like value be traced to a real credential source?

**Yes — and it was traced without printing it, and without opening any vault.**

Method: the locator was extracted in-process, written to a scratch file, and used as a
`grep -rlF` needle. It was never echoed to the transcript, never passed as a tool argument, and the
sibling repos' `vault/` directories were excluded from every scan.

| repo | files containing the same account locator |
|---|---|
| `repos/clients` | **9** |
| `repos/connector` | **5** |
| `repos/wiki` (with `vault/` excluded) | **43** |

**57 files across three private repos.** This is not a scratch or throwaway account: it is the live
Snowflake deployment the whole estate is built against. The published identifier is real.

### 13.1 Corroboration — second instrument, and the reconciliation

The counts above were produced twice, by two independent implementations run at different times:

| instrument | `clients` | `connector` | `wiki` |
|---|---|---|---|
| Python `pathlib.rglob` + substring, skipping `/.git/` and any `vault/` | 9 | 5 | 43 |
| GNU `grep -rlF` with `--exclude-dir={.git,vault,node_modules,.venv}` | 9 | 5 | 43 |

**Exact agreement on all three, with different traversal and different exclusion mechanics.** No
divergence to investigate. §13's provenance conclusion is corroborated, not single-sourced.

### 13.2 ⭐ What the counts hid, and what it turned out to be

The second instrument returned **paths**, not just totals — and one of them is credential-shaped:
`clients/GEP/scripts/.env`. A count alone would never have surfaced it. Checked immediately, without
reading the file:

| question | measured | verdict |
|---|---|---|
| is `ALDC-io/clients` public? | `gh repo view --json visibility` → **PRIVATE** | not exposed |
| is the `.env` tracked? | `git ls-files` → **0** | never committed |
| is it ignored? | `git check-ignore -v` → `.gitignore:3:.env` | ignore verified, not assumed |
| is `ALDC-io/connector` public? | **PRIVATE** | not exposed |
| are the `connector` hits tracked? | `.prefect/prefect.db`, `__pycache__/*.pyc`, both scripts → **0 tracked** | local artifacts only |
| are the `clients` hits tracked? | `CORE_DEV/account.json`, `GEP/eclipse/capacity.json` → **tracked** | normal config, in a **private** repo |

⛔ **The `.env` was not read.** Its existence beside this locator is exactly the shape that would
matter, so it was resolved by metadata alone — visibility, tracked-status, ignore-rule. Reading it
would have required permission under the global credential rule and was not necessary.

**Result: the trace adds no new exposure.** The locator is routine internal knowledge across the
estate (43 wiki files, including standup notes going back to May), tracked only inside private
repositories. Its **only public disclosure remains the two `agent-factory` refs in §11.** This
strengthens the §14 verdict that the locator is not rotatable and is best treated as permanently
disclosed — and it leaves the rotation recommendations unchanged.

⚠ **This subsection raises this document's own sanitization bar.** It names private-repo paths
including a `.env`. Sanitizing for any public version means removing §13.1–§13.2 wholesale, not
redacting within them.

⛔ **`repos/wiki/vault/infra-credentials.md` was NOT read, and no `az keyvault secret show` was
run.** Per the global credential rule that needs explicit permission, and the trace did not require
it — matching the locator in non-vault files establishes provenance on its own.

## 14. Which credentials require rotation or revocation

**Measured first: no credential value has ever been committed to this repository.**

| sweep | scope | result |
|---|---|---|
| key prefixes (`sk-`, `ghp_`, `xox*`, `AKIA`, `eyJ`) + PEM blocks | all **six** remote refs | **0 hits on every ref** |
| `git log --all -S'-----BEGIN'` | 359 commits, all local refs | 2 commits, both **detector/handler code**, inspected |
| `git log --all -S'snowflakecomputing.com'` | all refs | 0 |
| assigned-secret shapes at `HEAD` | 545 tracked files | 6 hits, all placeholder or secret-*name* |

**Therefore: nothing is compromised, and nothing requires rotation as incident response.**

Recommendations below are **risk reduction**, and each is Paul's call:

| identity | recommendation | reasoning |
|---|---|---|
| `prod-dg1-core-admin` in `aldc-vault-prod` | **Rotate — highest priority of the three** | its vault name *and* secret name are on the **default branch**, the most-indexed ref. Value not exposed; what changed is that a prod admin secret is now a *named* target with a known store. |
| `snowflake-admin-nonprod` in `aldc-vault-test` | **Rotate — moderate** | published beside the real endpoint and database. Mitigating: non-prod, and the published username is the wrong one. |
| `snowflake-r3-cartography-nonprod` (RO identity) | **Optional** | read-only by construction; the DDL grants `USAGE` + `SELECT` only, deliberately enumerated. Lowest value to an attacker. |
| the Snowflake account locator | **Not rotatable** | it is a hostname component. It cannot be changed without migrating the account. Treat as permanently disclosed. |
| the 16-char personal admin username | **No action** | not published (§12.3). Keep it that way — it is in unpublished `4e076d8`. |

⭐ **Do not report rotation as remediation of the disclosure.** Rotating changes what a future
attacker can use; it does not retract the endpoint, the vault names, the client name, the artifact
or the figures. Those are disclosed as of 2026-08-31 and stay disclosed.

## 15. Safest containment sequence after visibility is changed

Ordered so each step is reversible until the one after it, and so nothing destroys evidence a later
step needs.

**Step 0 — before touching visibility: capture the evidence of the exposure.**

```bash
git fetch personal
git ls-remote --heads personal              > docs/release-gate/exposure-refs-<date>.txt
gh api repos/russell94paul/agent-factory    > docs/release-gate/exposure-repo-<date>.json
gh api repos/russell94paul/agent-factory/forks
```

Once the repo is private these become unverifiable from outside. If B1 ever needs answering to a
client, this snapshot is the only contemporaneous record that forks were 0.

**Step 1 — flip visibility to private.** One action; retracts all six refs simultaneously; destroys
nothing; fully reversible. Strictly better than deleting branches, which would leave `main` exposed
anyway (§11).

**Step 2 — re-verify from outside.** `gh api …/contents/…?ref=reliability/recurrence-preflight`
must now return 404 unauthenticated. Do not accept the settings page as proof; check the served
surface, the same way the exposure was confirmed.

**Step 3 — decide B1** (client notification) with the Step 0 snapshot in hand. Steps 4+ proceed in
parallel; B1 does not block engineering.

**Step 4 — rotate per §14**, prod → non-prod → optional. Rotating after the repo is private is
strictly better: it closes the window between rotation and any re-publication.

**Step 5 — build the clean base (§18), and only then consider re-publication.**

⚠ **Ordering constraint:** never delete a remote branch before Step 0. Deletion removes the ability
to demonstrate what was exposed, while removing none of the exposure.

## 16. Which refs can be deleted, versus what would require history rewriting

| ref | can deletion alone clear it? | why |
|---|---|---|
| `reliability/recurrence-preflight` | **Yes, for its unique content** — it holds the only public copies of the review artifact, the two spend-evidence files and the bootstrap script | its 4 commits are not on `main` |
| `trial/wave0-rescue` | Yes | unique content is client-name only |
| `fix/fifth-verdict-apparatus-error` | Yes | " |
| `docs/agent-army-research-separation` | Yes | " |
| `claude/agent-factory-architecture-doc-by7il6` | Yes | " |
| **`refs/heads/main`** | **No.** | it is the default branch and is itself contaminated |

**The depth that decides it.** The earliest contaminated file on published `main` —
`docs/research/answers/R4-answer-agnostic-optimizer.md`, brand name — was added in `b6e5e72` on
**2026-08-21**. That is **302 commits before the public tip**, of **315** total on `main`
(`git rev-list --count b6e5e72..personal/main` / `git rev-list --count personal/main`). The newest
is `8b73f4f` — the tip commit itself.

> **A history rewrite of `main` would have to touch ~96% of the repository's history, and would
> still not un-publish anything.**

Not a proportionate action, and §2.4 governs why it would not be a fix even if it were.
**Recommendation: do not rewrite history. Do not force-push. Change visibility instead (§15), and
build forward from a clean base (§18).**

Branch deletion remains worth doing *after* Step 0 — it reduces further distribution and shrinks the
surface if visibility is ever flipped back — but it must never be described as remediation.

## 17. Preventing recontamination from existing worktrees and clones

The contaminated objects exist in **four working trees on this machine**, plus any clone taken from
the public remote. Every one of them can re-push what a visibility change just retracted.

| location | branch | state |
|---|---|---|
| `C:/…/agent-factory` (primary) | `main` | `ab13977`, 21 commits ahead of `personal/main` |
| `.worktrees/mission` | `mission/marketing-model-v1` | `efb05cf` — 26 ahead, 44 sensitive files, never published |
| `.worktrees/reliability` | `reliability/recurrence-preflight` | `b338324` — **this is the branch that leaked** |
| `.worktrees/switchboard` | `switchboard/p0` | `1d6b3a4`, ancestor of `main` |

**Controls, cheapest first:**

1. **Make the public remote push-refusing locally.** One command, no history change, reversible, and
   it stops every session in every worktree — worktrees share the repository's config:
   ```
   git remote set-url --push personal DISABLED_see_docs/release-gate/AF-RELEASE-GATE-01
   ```
   The URL text is what a session sees when a push fails, so make it name this document. Restore
   with `git remote set-url --push personal <url>` when a clean base exists.
2. **A `pre-push` hook that refuses on pattern match** — reject if the pushed range introduces the
   client name, brand, spend figures or vault identifiers. This is the control that survives the
   remote URL being restored, and the one that would have prevented `b28c334`.
3. **A test that fails when client patterns appear outside allowlisted paths** — the only control
   that catches contamination at *commit* time rather than push time. `b28c334`'s subject was
   *"docs(findings): three evidenced findings filed"*; no human review of subjects would have caught
   it, and no push-time gate helps a repo that is already public.
4. **Do not delete the worktrees.** `.worktrees/mission` holds authoritative unpublished evidence,
   and the release gate forbids deleting private evidence to ease publication.
5. **Existing outside clones cannot be controlled.** No local measure reaches them. This is the
   residual risk a visibility change does not close, and it is why §2.4 stands.

## 18. Clean base for future Agent Factory development

**Do not branch future public work from any current ref.** All six are contaminated (§11), and
`main`'s contamination reaches 302 commits deep (§16).

**Recommended: a new repository, seeded by content, not by history.**

| | |
|---|---|
| **base** | a fresh `git init` — **no** shared history with `agent-factory`, so no object is reachable from the old graph |
| **seeded with** | `factory/`, `scripts/` (minus the Snowflake and client-review scripts), `tests/`, `blueprints/`, `docs/protocol/`, `evals/`, `evaluator_service/` |
| **excluded** | `docs/evidence/**`, `missions/**`, `docs/case-studies/**`, `docs/artifacts/client-review-*`, `boot-prompts/**`, `docs/research/answers/**` — pending per-file review, not blanket re-admission |
| **admission gate** | `git grep -ilE '<client>\|<brand>\|<figures>\|<vault names>\|GP-[0-9]+\|FU92-[0-9]+'` returns **0** over the whole tree **and** over the full diff of every commit, enforced as a test inside the repo |
| **`agent-factory` becomes** | private, permanently — the working repository where evidence may live |

Rationale for a new repository over an orphan branch: an orphan branch inside the same repository
still shares an object database, so the contaminated blobs remain fetchable by SHA and reachable
through any dangling reference GitHub retains. A separate repository has no such edge.

⛔ **`boot-prompts/` must be reviewed file-by-file, not re-admitted as a class.** Three of the
contaminated files on published `main` are boot prompts, and the account locator's only appearance
on `main` is in one. Boot prompts are written fast, at the end of sessions, quoting whatever the
session was holding — which is exactly why they carry client figures.

## 19. What this part does NOT establish

- **Whether anyone took a copy.** NOT-VISIBLE (§11). 0 forks is not 0 readers.
- **When `reliability/recurrence-preflight` was pushed.** NOT-RECORDED — the `/events` API returned
  pushes for three other refs only, so its absence is an instrument limit, not evidence.
- **Whether the disclosure is contractually notifiable.** Outside a session's competence (B1).
- **That §12–§14 cover every sensitive class.** They cover the classes searched: client name, brand,
  four spend figures, Jira keys, vault and secret names, account locator, and credential-value
  shapes. A class nobody thought to grep for would not appear. The §18 admission gate is the durable
  fix precisely because it does not depend on anyone remembering to run these greps again.

---

# PART III — STEP 0 EVIDENCE CAPTURE (executed) + PUBLIC-FIRST PATH (plan only)

## 20. Step 0 — the before-state, captured while it is still measurable

**Executed 2026-09-01 11:20:41 UTC. Read-only. Nothing was changed, committed or pushed.**

| | |
|---|---|
| script | `docs/release-gate/capture_public_exposure.py` |
| input | `docs/release-gate/patterns.local.txt` — **LOCAL_ONLY** |
| output | `docs/release-gate/step0-20260901T112041Z/` — `manifest.json`, `ls-remote-heads.txt` |
| class | **LOCAL_ONLY**, uncommitted, unpushed |

### 20.1 The instrument was proven before it was believed

A 404 from an instrument that cannot return 200 is not a measurement. The script **refuses to
capture** unless three controls pass, and they are recorded in the manifest:

| control | expected | measured |
|---|---|---|
| known-public path | 200 | **200** |
| absent path | 404 | **404** |
| known-**private** repo (`ALDC-io/clients`) | 404 | **404** |

⭐ The private-repo control does double duty: it proves the request is genuinely **unauthenticated**.
An authenticated `curl` would have returned 200 for a repo Paul can read, and every "publicly
retrievable" verdict would have been an artefact of his own credentials. It also proves the
instrument **can register the change Step 1 will make** — private reads as 404 through this exact
path — so a later re-run is a real before/after, not a hopeful one.

### 20.2 What was captured

| measurement | value |
|---|---|
| captured at | `2026-09-01T11:20:41+00:00` |
| repository | `russell94paul/agent-factory`, `visibility: public`, default branch `main` |
| **forks / network / stars / watchers** | **0 / 0 / 0 / 0**; `/forks` list empty |
| remote refs captured | **6**, each with exact SHA |
| matching path-ref pairs | **179** |
| distinct paths | **74** |
| **anonymously retrievable** | **179 of 179 — every one returned HTTP 200** |
| credential-like pairs | **15** (metadata only, no values) |

Per-ref, every branch README also returned 200 — all six refs are publicly served:

```
main                                          8b73f4f    44 paths
reliability/recurrence-preflight              b338324    66 paths
fix/fifth-verdict-apparatus-error             2adf9a2    30 paths
docs/agent-army-research-separation           ec1c6c6    14 paths
claude/agent-factory-architecture-doc-by7il6  eb20675    12 paths
trial/wave0-rescue                            6872aee    13 paths
```

⚠ 74 distinct paths exceeds the 9/17 figures in §11 because this capture includes the **Jira-key**
class, which §11 counted separately. It is a superset, and every entry carries its own class labels,
so the narrower counts remain recoverable from the manifest.

### 20.3 What the package deliberately does not contain

Verified, not asserted — `grep -rcioE '<brand>|<figures>|<locator>|<vault names>|<secret names>|<db>'`
over the whole package returns **0** in both files:

- **no file contents.** Paths, blob SHAs, blob byte-sizes and HTTP status codes only.
- **no credential values.** Credential-like entries carry exactly: `path`, `ref`, `ref_sha`,
  `classes`, `introducing_commit`, `blob_sha`, `blob_bytes`, `anonymous_http_status`, plus
  `classification`, `value_captured: false`, `appears_live: UNKNOWN`,
  `rotation_status: UNKNOWN-NOT-INDEPENDENTLY-VERIFIED`.

`appears_live` and `rotation_status` are left **UNKNOWN by design**. §13 established the account
locator is real by independent trace, and §14 established nothing has been rotated — but the
capture tool must not inherit a conclusion from a document. A human sets those fields.

### 20.4 The script carries no client tokens

Search patterns are read from an external file, so `capture_public_exposure.py` itself contains no
client name, brand, figure, account or vault identifier. **The script is publishable; only its input
is not.** That is the same shape §18 recommends for the admission gate, and it means this tool can
move to the clean public base unchanged.

### 20.5 ⛔ Hazard this step introduced, and did not close

`docs/release-gate/patterns.local.txt` contains the account locator, both Key Vault names and three
secret names. It sits **untracked but NOT ignored**, under a tracked directory, in a checkout five
sessions share — the exact condition that `ab13977` closed for the PBI package.

Mitigating: every value in it is already published (§11), so committing it would expose nothing new.
Not mitigating: it is a concentrated list, and the condition is the one that caused this incident.

**Recommended next micro-action, not taken** (it needs a second commit, which was not authorised):

```
docs/release-gate/          # LOCAL_ONLY: exposure evidence, patterns, and the gate report
```

Until then, `git add -A` in this checkout will stage the patterns file, the Step 0 package and this
report.

---

## 21. PUBLIC-FIRST PATH — how to keep Agent Factory public

Public-first is achievable. It is **not** achievable by cleaning up what exists, because §16 measured
the contamination at 302 of 315 commits on `main`. It is achievable by building the public line
forward from a base that never had the contamination, and demoting the current repository to the
private working repo it has actually been all along.

### 21.1 The clean public base for P1

⭐ **There is no clean commit in this repository to branch from.** All six remote refs are
contaminated (§11), and the earliest contaminated file on `main` predates 302 of its 315 commits.
"Branch from an earlier good commit" is not available.

**Recommended base: a new repository, `git init`, zero shared history — seeded by content.**

| | |
|---|---|
| **base** | fresh `git init`; **no** shared object database with `agent-factory` |
| **seed** | `factory/`, `tests/`, `blueprints/`, `evals/`, `evaluator_service/`, `docs/protocol/`, `scripts/` minus the Snowflake and client-review scripts, plus `docs/release-gate/capture_public_exposure.py` (§20.4) |
| **excluded pending per-file review** | `docs/evidence/**`, `missions/**`, `docs/case-studies/**`, `docs/artifacts/client-review-*`, `boot-prompts/**`, `docs/research/answers/**` |
| **admission gate** | a test in the repo: the class patterns return **0** over the whole tree *and* over every commit's full diff |

An **orphan branch inside `agent-factory` is not a substitute**: it shares the object database, so
contaminated blobs stay fetchable by SHA and reachable through any dangling ref GitHub retains. The
separation has to be at the repository boundary to be real.

### 21.2 Can P1 begin before historical remediation? — **YES**

**Yes, and it is the correct order.** P1 does not depend on any remediation decision, because:

1. The new repository shares no history, so nothing it contains can be contaminated by what
   `agent-factory` holds.
2. Remediation of the existing exposure is a *disclosure* decision (B1) and a *visibility* decision
   (B2). Neither blocks writing code into a clean repo.
3. §2.4 stands regardless: nothing done later un-publishes what is already out. Waiting therefore
   buys nothing, while the product line stalls.

**One hard precondition before P1's first commit:** the admission gate must exist and pass **in the
new repo, on commit 1**. A gate added at commit 40 has 39 commits it never checked, and this whole
incident is what that looks like.

**Recommended working shape:** develop P1 in its own checkout, not a worktree of `agent-factory`.
Worktrees share the parent repository's config, remotes and object store — which is convenient for
lanes and exactly wrong for a boundary. A worktree of a contaminated repo cannot be a clean base.

### 21.3 Which remote refs must eventually be removed or rebuilt

| ref | disposition | note |
|---|---|---|
| `trial/wave0-rescue` | **delete** after Step 0 | unique content is client-name + Jira keys |
| `fix/fifth-verdict-apparatus-error` | **delete** after Step 0 | " |
| `docs/agent-army-research-separation` | **delete** after Step 0 | " |
| `claude/agent-factory-architecture-doc-by7il6` | **delete** after Step 0 | " |
| `reliability/recurrence-preflight` | **delete** after Step 0 — **highest value** | holds the only public copies of the client review artifact, the two spend-evidence files and the bootstrap script |
| **`main`** | **cannot be cleared by deletion or rebuild** | default branch, contaminated 302 commits deep, and it carries the full credential-like tuple (§12.2 correction) |

Deletion reduces further distribution. **It is not remediation** (§2.4) and must never be reported
as such. `main` is dispositioned by the visibility decision (B2), not by ref surgery.

### 21.4 Can a clean public branch be built without inheriting the sensitive history? — **YES, in a new repo. NO, in this one.**

- **In a new repository: yes.** Content-seeded, no shared objects, gate on commit 1.
- **In `agent-factory`: no.** Every mechanism that keeps the branch in this repo — orphan branch,
  filtered rebuild, squash — leaves the original objects in the same database, reachable by SHA and
  retained by GitHub's dangling-object cache. The branch would *look* clean and not *be* isolated.

### 21.5 The private evidence/state boundary that must coexist

| | public P1 repo | private `agent-factory` |
|---|---|---|
| holds | the product: factory, tests, protocol, blueprints, generic tooling | client evidence, missions, case studies, client artifacts, boot prompts, the release-gate record |
| client name / brand / figures | **never** — enforced by the admission gate | expected |
| vault, account, database identifiers | **never** | expected |
| evidence discipline | generic evidence only, no client subject | authoritative; unchanged |
| link between them | committed **pointers** naming package + as-of + location; never mirrored content | — |

⭐ **The structural lesson to encode, not just remember:** this repository's evidence discipline
*requires* committing evidence, and some evidence is client-confidential. Those two facts are
incompatible in one public repository, and no push policy reconciles them — only a repository
boundary does. `b28c334` was subject-lined *"docs(findings): three evidenced findings filed"* and
carried a client-facing artifact; no review of commit subjects would ever have caught it.

### 21.6 Actions required before the next public push — in order

**To `agent-factory` (the currently-public repo): none. Do not push to it again.** It is 21 commits
ahead, and §4.1 measured that pushing `main` would newly expose 21 files. Recommended posture until
B2 is decided:

```
git remote set-url --push personal DISABLED_see_docs/release-gate/AF-RELEASE-GATE-01
```
One command, reversible, no history change, and it binds **every worktree** because worktrees share
the repository config.

**To the new public P1 repo, before its first push:**

1. ✅ **Step 0 captured** — done, §20.
2. ⬜ Commander decisions **B1** (client notification), **B2** (visibility), **B3** (public project
   posture). B1 and B2 do not block P1 (§21.2); B3 shapes what P1 is.
3. ⬜ Create the new repository **private first**. Prove the gate works, then flip to public — the
   reverse order is how this incident happened.
4. ⬜ **Admission gate in place and passing on commit 1.**
5. ⬜ Seed by content per §21.1; no `git remote add` pointing at `agent-factory`.
6. ⬜ Clone the new repo fresh to a **short path** and run the suite — publishing a repo whose suite
   fails on clone ships a defect to every reader (§8.2b measured 21 failures for a fresh clone of
   `agent-factory`, 17 of them requiring a private sibling repo).
7. ⬜ Fix the two self-matching guards (§8.3) so the public suite is green.
8. ⬜ `docs/release-gate/` ignored or moved out (§20.5) before any commit that could sweep it.

**Nothing in §21 was executed.** No repository created, no ref deleted, no visibility changed, no
push, no history rewrite.

---

# PART IV — P1 DEVELOPMENT BOUNDARY (`AF-SWITCHBOARD-P1-CONTROL-UX`)

**Planning only. Nothing executed: no worktree created, no branch created, no push, no visibility
change, no ref deleted, no history rewritten.**

## 22. The boundary, measured

### 22.1 P1 safe base — `ab13977`

**Exact SHA: `ab13977d16809409229c6f26e74b2d0361b25fe2`** (`main`, verified as tip at 2026-09-01
11:5x UTC; five sessions share this checkout, so re-measure before use).

**Why this and not `1d6b3a4`.** Only two commits separate Switchboard P0's tip from `main`:

```
ab13977  chore(gitignore): the live PBI capture cannot be staged by accident   <- containment
bc676d6  docs(boot): AF-RELEASE-GATE-01 …                                      <- 1 sensitive line
1d6b3a4  feat(switchboard): quick dispatch …                                   <- P0 tip
```

`ab13977` is the **only base that carries the containment control**. Basing P1 at `1d6b3a4` would
give it a checkout in which `git add -A` re-stages the live PBI capture. That is a worse trade than
inheriting one contaminated boot prompt, which is inert for local development.

**Does it include client-sensitive/publication-risk history? YES — unavoidably.** `ab13977`'s
ancestry contains every contaminated commit in §4.3, and its contamination reaches 302 commits deep
(§16). **There is no clean base in this repository.** That fact does not block P1; it determines the
*publication* route (§22.4), not the *development* route.

### 22.2 P1 branch and worktree

| | |
|---|---|
| branch | `switchboard/p1` — free, verified `git branch --list` empty |
| worktree | `.worktrees/p1` — free, verified absent |
| command | `git worktree add .worktrees/p1 -b switchboard/p1 ab13977` |

**A worktree is right here, and this is the opposite of §21.2's advice for the clean public base.**
The two cases differ:

- **The clean public base must NOT be a worktree** — it would share the contaminated object
  database, so isolation would be cosmetic.
- **P1 development SHOULD be a worktree** — it is deliberately *inside* the private plane. What it
  needs is isolation from the five sessions on the primary checkout, not isolation from the objects.

⭐ **Measured, because the `.data/` finding predicts the opposite:** a worktree is fully functional
for P1.

| check, run in `.worktrees/switchboard` | result |
|---|---|
| `tests/test_switchboard.py` | **62 passed** |
| `factory.repo.data()` resolves to | `…/agent-factory/.data` — the **primary** checkout |
| `.data/` therefore readable from the worktree | **yes** |

F105 does not bite Switchboard: the three `.data/`-fragile tests resolve the root from `__file__`,
while `switchboard.py` uses `repo.data()` and correctly reaches the shared store. **P1 can serve
real state from its worktree.**

**May P1 read existing private local evidence without committing it? YES.** Reading is unrestricted
— `docs/evidence/**`, `.data/`, the mission worktree, this report. Two mechanical guarantees now
exist against accidental commit: the live PBI capture is ignored by `ab13977`, and `.data/`,
`.sessions/`, `.worktrees/` were already ignored (verified untracked, not merely listed). **The
remaining gap is `docs/release-gate/`** — see §22.5 item 1.

### 22.3 SAFE TO DEVELOP LOCALLY vs SAFE TO PUSH PUBLICLY

These are different properties and must never be collapsed.

| | SAFE TO DEVELOP LOCALLY | SAFE TO PUSH PUBLICLY |
|---|---|---|
| test | does work here risk *new* disclosure? | does this content, and everything reachable from it, contain client material? |
| `ab13977` as a base | ✅ **YES** | ❌ **NO** — 302-deep contamination |
| Switchboard P0 sources | ✅ YES | ✅ content clean (§22.4), ❌ **blocked by ancestry** |
| reading private evidence | ✅ YES | ❌ never |
| P1's own new commits | ✅ YES | ⚠ only after replay onto a clean base |

⭐ **The load-bearing point: a commit's content and its ancestry are separately classified.** A
commit can be perfectly clean and still be unpublishable because you cannot push it without pushing
its parents. That is why P1 develops on `ab13977` and *publishes* by replay, never by push.

### 22.4 Classification of the local Switchboard/client-review/tooling lineage

Basis: **sensitive lines introduced by each commit's own diff** —
`git show <sha> -U0 | grep '^+' | grep -ciE <classes>`. Content, not ancestry.

**A — safe to retain directly** (clean content; replay as-is onto a clean base):

| commit | subject | +sensitive |
|---|---|---|
| `ab13977` | `chore(gitignore)` containment | 0 |
| `1d6b3a4` | switchboard: quick dispatch | 0 |
| `c7b950a` | switchboard: start synced | 0 |
| `62cb0e4` | switchboard: one page over state | 0 |
| `a55da11` | deps: ask every environment question | 0 |
| `1068f59` | client-review: e2e test asserted a forbidden root | 0 |
| `8fba030` | findings: F100 second instance | 0 |
| `9e05b26` | merge: RAPID-RELIABILITY-01 | 0 |

**B — safe for local development, MUST be replayed/rebuilt before public push:** every commit in A.
None of them can be pushed as-is, because each has contaminated ancestry. **A and B are the same
set** — that is the finding, not an oversight.

**C — contains sensitive history, do not publish:**

| commit | +sensitive | what it introduces |
|---|---|---|
| `4e076d8` | **72** | R3 cartography, warehouse topology, the credential-like tuple |
| `4fc76a1` | **53** | artifact generator; commits the client review artifact + case study |
| `7d71a84` | **24** | client review record |
| `80854d2` | 6 | D1 requirements, client-named |
| `262a199` | 5 | readiness record close-out |
| `01f7e3b` | 4 | D3 boot prompt |
| `bc676d6` | 1 | the release-gate brief itself |
| `0a8b593` | 1 | six outcome write-ups |
| `10c4fe7` | 1 | artifact classification + render evidence |

**Already public — a separate class, past the decision point:** `b338324`, `ab9ee86`, `64dfff5`,
`b28c334`. Disclosed 2026-08-31; §2.4 governs.

**Switchboard P0's file set is clean, measured file-by-file** — `factory/switchboard.py`,
`factory/switchboard_render.py`, `tests/test_switchboard.py`,
`scripts/render_check_switchboard.py`, `scripts/negative_control_button_contrast.py` and its three
evidence JSONs all return **0**. One exception:

⚠ **`scripts/local_tracker.py:1273`** — a form placeholder reading
`placeholder="ticket id, e.g. GP-327"`. Not client data, but it publishes an internal Jira key
format and a real ticket number in the UI. **One-line fix, and it is P1's own file** — change the
example to a generic token before any replay.

⭐ **The render evidence is clean, but not by design.** Switchboard screenshots show task titles from
`.data/`, so they *could* carry client names. Measured now: **0 of 253 task events** and **0 mission
manifests** mention the client or brand. P1 inherits a clean store — it should treat that as a
property to preserve and re-check before committing new screenshots, not as a guarantee.

### 22.5 Minimum gate before ANY future public push

1. ⬜ **Close the `docs/release-gate/` hazard.** `patterns.local.txt` holds the account locator, both
   vault names and three secret names; the Step 0 manifest and this report sit beside it —
   untracked, **not ignored**, in a shared checkout. One `.gitignore` line.
2. ⬜ **Disable pushes to the contaminated remote** —
   `git remote set-url --push personal DISABLED_see_docs/release-gate/AF-RELEASE-GATE-01`.
   Reversible, no history change, binds every worktree because worktrees share the config.
3. ⬜ **Commander decisions B1 / B2 / B3** (§6).
4. ⬜ **Clean public repository created private-first**, content-seeded, no shared history, no remote
   pointing at `agent-factory` (§21.1).
5. ⬜ **Admission gate passing on commit 1** — class patterns return 0 over the tree *and* over every
   commit's full diff.
6. ⬜ **Replay class A/B content** onto that base; fix `local_tracker.py:1273` en route.
7. ⬜ **Fix the two self-matching guards** — `test_repo_root.py` and `test_suite_cache.py` fail in
   the primary checkout *and* in a worktree (measured both). Both are false positives tripped by
   Switchboard's own prose.
8. ⬜ **Fresh clone to a short path, suite green.** A fresh clone of `agent-factory` fails 21 tests;
   17 need a private sibling repo via `$PREFECT_CONNECTORS`.

**Not executed.**

### 22.6 Remote ref dispositions — planning only

| ref | SHA | disposition |
|---|---|---|
| `reliability/recurrence-preflight` | `b338324` | **DELETE** (highest value — sole public copy of the client artifact, both spend-evidence files, the bootstrap script). Not remediation. |
| `trial/wave0-rescue` | `6872aee` | **DELETE** |
| `fix/fifth-verdict-apparatus-error` | `2adf9a2` | **DELETE** |
| `docs/agent-army-research-separation` | `ec1c6c6` | **DELETE** |
| `claude/agent-factory-architecture-doc-by7il6` | `eb20675` | **DELETE** |
| **`main`** | `8b73f4f` | **HISTORY REMEDIATION — not achievable proportionately.** 302 of 315 commits contaminated; carries the full credential-like tuple. Disposition is the **visibility decision (B2)**, not ref surgery. |
| **RECONSTRUCTION** | — | **none of these refs.** Reconstruction happens in the *new* repository (§21.1), not by rebuilding a ref here. |
| **NO ACTION** | — | none. Every current public ref requires a decision. |

⛔ All deletions occur **after** Step 0 (captured, §20) and none of them un-publish anything.

### 22.7 Private plane — the minimum P1 should assume

Deliberately narrow. Three rules, no new platform:

1. **The private plane is this repository.** `agent-factory` is the private working repo: client
   evidence, missions, boot prompts, `.data/`, the release-gate record. P1 reads all of it freely.
2. **Client execution state stays in `.data/` and `docs/evidence/`, and is reached only through
   `factory.repo`.** `repo.data()` already resolves correctly from a worktree (measured). P1 must
   not add a module that computes a data root from `__file__` — that is what `test_repo_root.py`
   exists to prevent, and P1 will be fixing that guard anyway.
3. **The public plane is a future separate repository, and nothing crosses by mirroring** — only by
   deliberate replay through the admission gate. Pointers, never copies.

That is the whole architecture. Anything more is out of scope for P1.

### 22.8 Verdict

**`P1 LOCAL DEVELOPMENT: GO`** — isolation is sufficient, and the isolation was measured rather than
assumed: worktree suite green (62/62), shared `.data/` reachable, containment commit in the base,
publication route separated from the development route.
