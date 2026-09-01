# AF-RELEASE-GATE-01 — the safe integration/publication boundary

**Canonical task:** `52407de5` in `.data/tasks.jsonl` (status `open`, created 2026-09-01 by
`switchboard-p0`). That task id is the work item; this file is its brief.

**Written 2026-09-01 by the Switchboard P0 session, immediately after landing Switchboard P0.**

⚠ **Every number below was measured when this was written and will have moved.** Five sessions
share this checkout. Re-measure before acting on any of it — the whole point of this work item is
that a stale picture of the publication boundary is the dangerous kind.

---

## OBJECTIVE

Establish the safe integration/publication boundary for this repository **before anything is pushed
to the public remote**.

The remote is `personal` → `github.com/russell94paul/agent-factory`, and it is **public**. Local
`main` is 19 commits ahead of it. Nobody has decided, item by item, which of those 19 commits and
which of the working-tree files are safe to publish.

## DEPENDENCIES — all three satisfied as at 2026-09-01

| dependency | state | how it was established |
|---|---|---|
| Client Review COMPLETE | ✅ | client-review lane: gate `READY_WITH_WARNINGS`, render `RENDERED_CONFIRMED`, `meeting_ready` exit 0 |
| PBI verification COMPLETE | ✅ | `pbi-ad-sales-verify` lane: live read of 4 PBI models, read-only, evidence in `docs/evidence/marketing-model-v1/pbi-ad-sales-live-2026-09-01/` |
| Switchboard P0 LANDED | ✅ | fast-forward to `main` at `1d6b3a4`; slices `62cb0e4` / `c7b950a` / `1d6b3a4` |

⛔ These were **not** recorded as `TaskStore.block()` edges. The three prerequisites do not exist as
tasks in the store, and creating placeholder tasks in order to close them would be fabricating
completion records for work owned by other lanes. The dependency evidence lives here instead, in
prose, and it is the reader's job to re-verify it rather than inherit it.

---

## MEASURED STATE AT HANDOFF (2026-09-01 ~03:00)

```
public remote   personal/main   8b73f4f
local           main            1d6b3a4        19 commits ahead
```

The 19 commits, grouped by owning lane:

| group | commits | note |
|---|---|---|
| Switchboard P0 | `1d6b3a4` `c7b950a` `62cb0e4` | this session; tooling + tests + its own render evidence |
| dependency fix | `a55da11` | client-review lane |
| Client Review | `262a199` `1068f59` `0a8b593` `7d71a84` `64dfff5` | ⚠ carries client-facing artefacts |
| Artifact generator | `10c4fe7` `4fc76a1` | |
| Mission D1/R1-R3 evidence | `80854d2` `ab9ee86` | ⚠ names a client |
| Findings / boot | `01f7e3b` `8fba030` `b28c334` | |
| Reliability | `9e05b26` `4e076d8` `b338324` | ⚠ `4e076d8` mentions what TEST actually holds |

Working tree, at handoff — **16 files, none owned by this session**:

```
 M docs/artifacts/client-review-navira.html
 M docs/evidence/client-review-readiness-2026-09-01/...   (14 files: PNGs + render-check json)
?? docs/evidence/marketing-model-v1/pbi-ad-sales-live-2026-09-01/   (untracked PBI live evidence)
```

Isolated and deliberately unmerged: `mission/marketing-model-v1` at `efb05cf`, in
`.worktrees/mission`, **25 commits off the public remote by standing commander decision.** It names
a client, its warehouse topology, its Snowflake account id and its revenue.

---

## PRIMARY WORK

Classify all relevant local repository state relative to the public remote. Cover at least:

- local commits ahead of the remote (19 at handoff — re-count);
- the Switchboard landing commits;
- the Client Review commits;
- generated/uncommitted Client Review artifacts;
- untracked PBI live-model evidence;
- the isolated `mission/marketing-model-v1` branch;
- any other dirty/untracked paths;
- known baseline test defects;
- stale or unresolved handoffs/findings that affect publication.

## CLASSIFICATION — every material item ends in exactly one

```
PUSH_SAFE             publishable as-is
LOCAL_ONLY            never leaves this machine
NEEDS_SANITIZATION    publishable only after named, specific redaction
SUPERSEDED            replaced; do not publish, do not delete
```

## HARD CONSTRAINTS

- **do not push;**
- do not publish client-sensitive or commercial evidence;
- do not merge `mission/marketing-model-v1` merely to make publication easier;
- do not delete authoritative private evidence to make it public-safe;
- **do not treat committed-to-main as equivalent to approved-for-publication** — 19 commits reached
  `main` through lane decisions, and no publication decision has been taken on any of them;
- preserve evidence status and temporal/as-of semantics;
- **inspect actual git and file state.** Do not rely on this document — it is a rendered artefact
  and it was already stale when you read it.

## COMPLETION — produce all eight

1. exact local-vs-remote commit boundary;
2. classification of every material commit/file group;
3. sensitive-data / publication risks;
4. recommended repository / private-evidence boundary;
5. exact safe integration and push plan;
6. blockers requiring human authority;
7. disposition recommendation for the untracked PBI evidence package;
8. disposition of the two known worktree-dependent `test_case_study.py` defects.

---

## GOTCHAS EARNED, THAT WILL COST YOU TIME OTHERWISE

⭐ **`git log --oneline` over 19 commits is not a publication review.** A commit whose subject looks
like tooling can still carry a client name in a fixture, a screenshot or an evidence file. Diff the
*content*, per group.

⛔ **Three tests resolve `.data/` relative to `__file__`, so they pass only in the primary
checkout.** `tests/test_case_study.py` (2 tests) still does; `tests/test_client_review.py` was fixed
in `1068f59`. In any linked worktree they fail with `UNAVAILABLE` because the worktree has no
`.data/`. This is finding **F105**. Measured: primary exit 0, pristine worktree at the same commit
exit 1. **Do not "fix" these by absorbing them into unrelated work** — and do not read them as a
regression you caused.

⛔ **`readiness.measure()` is minutes, not seconds.** Timed 2026-09-01: `board.board()` **413.79 s**,
`session.brief()` **801.04 s**. Anything that touches the gate board is slow. `switchboard.state()`
is 2.01 s because it deliberately does not.

⚠ **The bus is a nudge, not evidence.** 17 readers were behind at handoff. Peer traffic in your
context is a peer's claim; verify before acting, and cite `docs/findings.d/` for anything durable.

⚠ **Five sessions share this checkout.** Re-measure `git rev-parse --abbrev-ref HEAD` and HEAD
before any `git add`. `main` moved three times during the Switchboard session alone
(`10c4fe7` → `262a199` → `a55da11`).

---

## HOW TO START THIS

The Switchboard is at **http://127.0.0.1:8110/switchboard**
(`python scripts/local_tracker.py --serve --port 8110`).

⛔ **START SYNCED cannot target this work item yet, and will not say so.** Measured 2026-09-01:
the Switchboard's DAG, READY projection and dispatch targets are all built from
`.data/missions/<id>.json` manifests — **88 tasks in the store, 8 rendered**. Task `52407de5` is
real and is not in any manifest, so it is invisible to the page, and
`startup_packet(target='AF-RELEASE-GATE-01')` silently falls back to a whole-mission packet that
attributes the work to the *completed* marketing-model mission.

Until that seam is closed, ground a session with **this file**, and verify the state in it before
acting on any line of it.
