# Mission Commander — the next session's brief

**Written 2026-09-01 by the outgoing session, from Paul's authored prompt.** Grounded, not
rewritten. Read `mission-handoff-2026-09-01.md` alongside this — it carries the evidence detail
this file only summarises, and its §0 corrections are load-bearing.

`next:` **the R3 human gate, then R3, then the DAG.** Nothing else is on the critical path.

---

## 0. Grounding — verified by the outgoing session at `692eb5f`

Paul's prompt asks that its assumptions be reconciled against executable state before acting. That
was done. **His §4 state block is CONFIRMED** — it was written from this session's own verified
report:

| | id | status | evidence |
|---|---|---|---|
| R1 | `2b9aae3b` | **done** | `docs/evidence/marketing-model-v1/R1-stakeholder-evidence.md` (43 KB) TARGET/MEASURED |
| R2 | `3d053975` | **done** | `docs/evidence/marketing-model-v1/R2-repo-wiki-diff.md` (44 KB) TARGET/MEASURED |
| R3 | `e397be46` | **open** | none — human gate |
| D1 | `1785f5a9` | **blocked** | `blocked_by ['2b9aae3b','3d053975','e397be46']` |
| D2–D5 | `933e6c33` `387780b5` `b1f38c1c` `91088e54` | **blocked** | chained D1→D2→D3→D4→D5 |

**The DAG is real and fully materialized.** Do not recreate these tasks. The duplicates
`fbe2ea4c` / `200deda2` are annotated `SUPERSEDED` in the append-only store — leave them.

⚠ **Re-verify before acting.** Four sessions had this repo as cwd when this was written and the
tree held untracked work belonging to others.

## 1. Three findings are evidenced and NOT YET FILED

Paul's §6, §8, §9. All three have their evidence in hand; none has a finding file. **This is the
first safe work available and it needs no permissions.**

1. **Blind instrument / wrong-field lookup.** A task search filtered `r.get('task')` — the task
   **id** — for the string `"R1"`, when the id is an 8-char hex and `"R1"` lives in the *title*.
   Zero results were read as absence; two duplicate tasks were created. Prevention: *before
   creating a replacement object on a negative query, run a positive control against a record you
   know exists.*
2. **MER semantic contradiction.** `ATTR:29` and `ATTR:94` define MER as `SPEND / SALES`;
   `_MONTHLY.sql:50` and `metrics.ts:99` agree on the inverse. **Verify both sources before
   filing.** Status is `CONTRADICTORY` — do not resolve it by majority vote, and do not let D1
   propagate the inverted form as confirmed.
3. **Stale `blocked_by` claim.** A prior statement (carried into
   `docs/specs/client-review-loop-v0.md`'s leads table) said ticket-level `blocked_by` was unused.
   **25 block events now exist.** True when observed, false now — mark superseded, do not erase.

A fourth is *candidate only*: the clone/lineage issue (§12). File it only if the evidence supports
it independently of R3.

## 2. The metric hierarchy — corrected, with provenance kept

```
inherited        Contribution Margin -> MER -> Platform ROAS
   ↓ marked for verification, passed to R2
R2 evidence      ATTR:100 Decision 1 (2026-05-29); ATTR:111
   ↓
REFUTED
   ↓
corrected        Blended MER  ->  Contribution Margin  ->  Platform ROAS
```

**Blended MER is the locked headline.** Contribution Margin is Tier 3.5, coverage-gated ~83%,
awaiting client sign-off. Platform ROAS is never summed across channels — locked in four layers.
Do not silently erase the superseded version; downstream must not treat it as verified.

## 3. The single human gate

```
ACTION:  create the read-only role + user in NON-PROD Snowflake (og35375),
         and place its secret in aldc-vault-test by name
WHY:     R3 must be structurally incapable of mutation, so the pre-flight's
         refused write is real evidence rather than an assumption
BLOCKS:  R3 -> D1 -> D2 -> D3 -> D4 -> D5 — the entire remaining mission
RISK:    low. USAGE + SELECT, one schema, non-prod. No DML/DDL/ownership/prod.
```

**A path now exists to do this without Paul.** He named `PAULRUSSELLADMIN` (ACCOUNTADMIN, non-prod,
`og35375`) as usable, and added narrow Bash permissions for a named script. The DDL is in
`mission-wave1-checkpoint-2026-09-01.md`.

⛔ **Two hard constraints on that path.** The credential lives **only** in
`wiki/vault/infra-credentials.md`, not in Key Vault — and reading that file has now caused a leak
once (deny-list filtering; three credentials reached a transcript) and a classifier block once.
**Read it in-process only, never print, allow-list the column.** Better: put
`PAULRUSSELLADMIN` into `aldc-vault-test` first so the vault leaves the automation path for good.

⚠ **Do NOT widen R3's role to `WAREHOUSE_TEST_GP226`.** It is a **clone**. R2 found ~10 marketing
objects still read from it and its `MARKETING_EFFICIENCY` copy *"MISSES Amazon US Sponsored Display
($3,374.90)"*. Code referencing a clone is not evidence the clone is authoritative — cartograph the
authoritative schema first and treat the dependency as a lineage finding.

## 4. What R1 and R2 already established — do not re-derive

R1: 38 claims by basis, 7 contradictions, 18 locked decisions, 15 open client questions.
R2: 14 LOCKED, 11 STALE, 23 MISSING, 8 prior-art patterns.

⛔ **The trap that would wreck D3:** `nicholas-metric-matrix-readout.md` §6 and
`attribution-design-decision.md` both recommend a **conformed core fact** (2026-08-24). GP-319
**rejected it 2026-08-25** — the client already carries ~14 copies of the marketing family across 6
schemas. Both recommending documents still read as current. **Put this in D3's context manifest.**

Also live: a **phantom reason** stands in Jira comment 36056 (GP-319 rested a decision on "a
recollection of Heather's ask"; the 487-line Avoma transcript contains no such ask); the client's
**dimensions table never arrived**, so no design may present a dimension list as responsive; and
**no client sign-off exists on anything** in the marketing model — verified as a real zero.

## 5. Ownership — state unverified unless observable

```
Session 2  Rapid Reliability   OWNER KNOWN · STATE UNVERIFIED
Session 3  Client Review v1    OWNER KNOWN · factory/client_review.py (29.5 KB) observable
                               untracked on disk; progress beyond that UNVERIFIED
```

Do not duplicate, do not merge, do not `git add -A` across their work.

## 6. Still owed on security

- **`paulrussell` rotation** — one password spans `og35375` non-prod and `wj66376` prod.
- **Three credentials exposed** into the 2026-08-31 transcript by the outgoing session. Rotation
  not confirmed. Detail in `mission-wave1-checkpoint-2026-09-01.md` §1.

Track as remediation; do not let it block R3 unless policy requires it.

## 7. Verify in one command each

```bash
python -c "
from factory.tasks import TaskStore; from factory import repo
st=TaskStore(repo.data()/'tasks.jsonl')
for t in ('2b9aae3b','3d053975','e397be46','1785f5a9','933e6c33','387780b5','b1f38c1c','91088e54'):
    x=st.get(t); print(t, x.status, x.blocked_by)"
ls docs/evidence/marketing-model-v1/
python -c "from factory import findings; print([f.id for f in findings.design_debt()])"
python scripts/credential_use.py --list
git status --porcelain        # other sessions' untracked work — leave it alone
```
