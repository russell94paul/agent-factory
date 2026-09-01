# Handoff — Wave 1 done, D1 blocked on R3 alone, and two of my own claims were wrong

**Written 2026-09-01.** Supersedes `mission-wave1-checkpoint-2026-09-01.md` — that file's §1
(credential exposure) still stands and must be read; everything else here is newer.

`next:` **R3 read-only access, then D1.** Nothing else on the mission's critical path is blocked.

---

## 0. ⛔ Two claims I made that measurement refuted. Do not carry either forward.

### 0.1 "The mission plan was not materialized into the task store" — FALSE

**All eight tasks existed**, correctly parented to mission `0d26cd2f`, with a **fully wired DAG**:

```
R1 2b9aae3b ─┐
R2 3d053975 ─┼─▶ D1 1785f5a9 ─▶ D2 933e6c33 ─▶ D3 387780b5 ─▶ D4 b1f38c1c ─▶ D5 91088e54
R3 e397be46 ─┘
```

My search filtered `r.get('task')` — **the task ID** — for the string `"R1"`. It should have
searched the title. **I searched the wrong field, got a zero, and reported the zero as a finding.**
On the strength of it I created two duplicate tasks (`fbe2ea4c`, `200deda2`). Both are annotated
`SUPERSEDED` in the append-only store; the real R1/R2 now carry the evidence and are `done`.

⭐ **This is the blind-instrument defect, committed on the day six of them were fixed.** The rule
that would have caught it is the repo's own: *a zero from an instrument you have not shown can see
is not a measurement.* A positive control — searching for a title you know exists — costs seconds.

### 0.2 "Ticket-level `blocked_by` is unused" — STALE, and Paul was right to challenge it

**25 block events exist and `blocked_by` is populated.** True when first observed (all 189 events
carried an empty `blocked_by`); false now. The DAG above is real, not aspirational. Anything built
on "the DAG field exists and is unused" — including the leads table in
`docs/specs/client-review-loop-v0.md` — needs that row corrected.

## 1. Observable state

`main @ ddea66d`. ⚠ **Untracked in the tree and NOT mine:** `factory/client_review.py` (29.5 KB),
`missions/`, `docs/evidence/marketing-model-v1/`. The first two are Session 3's owned work. **Do
not touch, do not commit, do not `git add -A`.**

| | id | status | evidence |
|---|---|---|---|
| **R1** | `2b9aae3b` | **done** | `docs/evidence/marketing-model-v1/R1-stakeholder-evidence.md` (43 KB), TARGET/MEASURED |
| **R2** | `3d053975` | **done** | `docs/evidence/marketing-model-v1/R2-repo-wiki-diff.md` (44 KB), TARGET/MEASURED |
| **R3** | `e397be46` | **open** | none — blocked on human access decision |
| **D1** | `1785f5a9` | **blocked** | `blocked_by [R1, R2, R3]` — two satisfied, R3 outstanding |

**Session 2 (Rapid Reliability) — ownership known; current state unverified.**
**Session 3 (Client Review v1) — ownership known; `factory/client_review.py` is observable on disk,
progress beyond that unverified.**

## 2. What R1 and R2 established (the mission's real inputs)

R1: 38 claims with basis, 7 contradictions, 18 locked decisions, 15 open client questions.
R2: 14 LOCKED, 11 STALE, 23 MISSING, 8 prior-art patterns.

⭐ **The four that change what D1 and D3 may conclude:**

1. **A phantom reason stands on the client record.** GP-319:183-184 rests a decision on *"a
   recollection of Heather's ask"*; R1 read the actual 487-line Avoma transcript
   (`aldc-launchpad/boot-prompts/navira_data_model_review_meeting_lori_heather.md`) and it contains
   **no such ask**. GP-318 §D9 already reversed the action for a different, sound reason — but the
   phantom reason is still in **Jira comment 36056**. Correcting it is a deliverable.
2. ⛔ **The rejected-design trap.** `nicholas-metric-matrix-readout.md` §6 and
   `attribution-design-decision.md` both recommend a **conformed core fact** (2026-08-24). GP-319
   **rejected it 2026-08-25** — the client already carries ~14 copies of the marketing family across
   6 schemas. Both recommending docs still read as current. **D3 must be told this before it opens
   them.**
3. **The client's own "bigger half" never arrived.** The dimensions table Nicholas promised has
   never been supplied; we hold `campaign_id` + `campaign_name`. No design may present a dimension
   list as *responsive* to a request that was never made.
4. **MER is written backwards in the document that locks it.** `ATTR:29` and `:94` give
   `SPEND / SALES`; `_MONTHLY.sql:50` and `metrics.ts:99` agree on the inverse. Preserve the
   contradiction — do not pick one silently.

**Corrected metric hierarchy** (inherited → marked for verification → R2 evidence → REFUTED):
**Blended MER** (locked headline, `ATTR:100`, Decision 1, 2026-05-29) → **Contribution Margin**
(Tier 3.5, coverage-gated ~83%, awaiting client sign-off, `ATTR:111`) → **Platform ROAS** (never
summed across channels — locked and honoured in four layers).
⛔ The refuted order was *Contribution Margin → MER → Platform ROAS*. I propagated it into R2's own
prompt marked "verify"; it came back refuted. Do not re-inherit it.

## 3. The only human action on the critical path

```
ACTION:  create a read-only Snowflake role + user in the NON-PROD account (og35375),
         and set its password as a new secret in aldc-vault-test
WHY:     R3 is read-only cartography. Paul chose the read-only-role route explicitly and
         ruled out admin-plus-ASSUMED. The role must STRUCTURALLY refuse mutation so the
         pre-flight's scoped write is watched being refused — that refusal is the evidence.
BLOCKS:  R3 -> D1 -> D2 -> D3 -> D4 -> D5. The entire remaining mission.
RISK:    low. USAGE + SELECT on one schema of a non-prod database. No prod, no DML, no DDL,
         no ownership, no grant option.
```

DDL and the scope question are in `mission-wave1-checkpoint-2026-09-01.md` §"R3".
⚠ **Do NOT widen the role to `WAREHOUSE_TEST_GP226`.** It is a **clone**, and code referencing it
is not evidence it is authoritative. R2 found ~10 marketing objects still read from it and its
`MARKETING_EFFICIENCY` copy *"MISSES Amazon US Sponsored Display ($3,374.90)"*. Inspect the
authoritative schema first; treat the clone dependency as a **lineage finding**, not a scope
expansion.

## 4. Still open

- **`paulrussell` rotation** — one password spans non-prod and prod. Separate from R3, still owed.
- **Three credentials exposed by me** into the 2026-08-31 transcript — see the previous checkpoint
  §1. Rotation not confirmed.
- **Findings not yet filed**: the MER contradiction; the blind-search defect in §0.1; the stale
  `blocked_by` claim in §0.2. All three are evidenced and none is filed.
- **Jira comment 36056** correction — Atlassian MCP was unavailable; may need pasting by hand.
- **The unannounced ratio movement** — GP-319:98 says margin % and TACoS/MER both rise and it
  *"must be announced, not discovered."* Nothing on file.

## 5. Verify in one command each

```bash
python -c "
from factory.tasks import TaskStore; from factory import repo
st=TaskStore(repo.data()/'tasks.jsonl')
for t in ('2b9aae3b','3d053975','e397be46','1785f5a9'):
    x=st.get(t); print(t, x.status, x.blocked_by)"
ls docs/evidence/marketing-model-v1/
python scripts/credential_use.py --list
git status --porcelain          # expect Session 3's untracked files — leave them alone
```
