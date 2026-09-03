# Boot — the TEST data is fine, the reader role is blind, and one grant unblocks two checks

**Written 2026-09-03** at `agent-factory` `86a1dff` (`main`), wiki `a923f9e`.
Supersedes the blocker table in
[`switchboard-p1-and-finalization-2026-09-01.md`](switchboard-p1-and-finalization-2026-09-01.md),
which was **stale in two rows** before this session started.

---

## `next:` — one action, and it is not mine to take

**Restore `SELECT` for `R3_CARTOGRAPHY_RO` on the refreshed `TEST_DG1_GEP.WAREHOUSE` objects.**
That single grant unblocks **both** remaining rendering checks. It needs an identity above the
read-only role, so it is Paul's or an admin's.

Then, in order:

1. Re-run the warehouse lane (command in §3). **Verify `isWarehouse: true` and a ~110-brand payload
   BEFORE trusting any assertion** — the code's own signature is *"2 entities synthetic / ~110
   vendors warehouse"* (`DashboardShell.tsx:26`).
2. Record which filters respond and which sit inert. A silent no-op is a finding, never an
   acceptable default.
3. `DATE RANGE` in warehouse mode — currently `UNMEASURABLE`, not pass or fail.

⛔ **Do not fix the grant by re-granting `SELECT ON ALL` again.** That is what decayed. Prefer a
schema-level future grant or a grant step inside the task chain — see wiki
`gep-snowflake-pbi-deployment` **PD-3**.

---

## What this session established

| | verdict | basis |
|---|---|---|
| R3 read-only identity | ✅ re-proved 2026-09-02 | MEASURED — `CREATE TABLE` refused `003001 (42501)`, 1,227 grants all `USAGE`/`SELECT` |
| TEST marketing-data currency | ✅ **cleared** | MEASURED — 6 objects, current to the measurement day |
| Power BI rendered figures | ✅ closed **2026-09-01**, before this session | the blocker list was stale |
| deployed `SNOWFLAKE_SCHEMA` | `NOT-VISIBLE` — **correct as recorded** | encrypted; reading it exports every secret to disk. Declined |
| warehouse-mode rendering | ⛔ **500 for the reader role** | MEASURED at the rendered layer |
| `DATE RANGE` in warehouse mode | `UNMEASURABLE` | the page never renders; no filter can be exercised |

⭐ **The client-facing measurement worth carrying into any review: Meta's history is 22 months
shorter than Google's.** Meta spend begins **2026-04-20**, Google **2024-06-01**. **Any range before
20 Apr 2026 shows Meta as zero — correctly.** That is coverage, not a defect, and it is exactly the
shape a render check misreads as a broken tile.

---

## The diagnosis, and the wrong one I published first

The dashboard 500s on `TEST_DG1_GEP.WAREHOUSE.SALES_FCT_ORDERLINE`:

```
SQL compilation error:
Object 'TEST_DG1_GEP.WAREHOUSE.SALES_FCT_ORDERLINE' does not exist or not authorized.
```

⛔ **I first concluded the object was absent from TEST. That was wrong and is retracted in
`86a1dff`.** Two `REPORT_COMMON` views that read from it return **12,378** and **10,418** rows. A
secure view executes with its **owner's** rights, so a dependent view succeeding while the caller
fails is the signature of an **under-granted caller**, not of missing data.

**The mechanism.** `WAREHOUSE_SOURCE` copies into `WAREHOUSE` via a task chain (Paul, confirmed:
*"a series of tasks trigger to populate warehouse schema"*, and it is *"a straight copy"* apart from
some utility tables). A task doing `CREATE OR REPLACE` **drops the object and its grants with it**.
`SELECT ON ALL` is point-in-time. Measured: of **34** objects the reader can see in `WAREHOUSE`,
**zero were created after its grant date** — the 27 views top out at 2026-08-12.

⚠ **`ON FUTURE` at database level did not save it.** Leading candidate: a schema-level future grant
takes precedence over a database-level one, making the latter inert for that schema. **Unconfirmed**
— confirming needs `ACCOUNT_USAGE`, which the reader cannot read.

⭐ **This is not new to the estate.** `gep-snowflake-pbi-deployment` **PD-2** already records grants
lost after DDL costing a **14-hour outage** in May — for the *task service* role. This is the same
mechanism on a *reader* role, where nothing gets suspended and a dashboard just 500s. Now written up
as **PD-3** with the three-reading test.

---

## §3 — the exact command, and the two traps in it

```bash
# the worktree still exists at C:/Users/PaulRussell/repos/navira-wt-warehouse (pinned df76dfb,
# node_modules junctioned). Remove it when done: git worktree remove
cd C:/Users/PaulRussell/repos/navira-wt-warehouse && \
  PORT=3101 DATA_SOURCE=warehouse \
  SNOWFLAKE_ACCOUNT=og35375.canada-central.azure SNOWFLAKE_USER=R3_CARTOGRAPHY \
  SNOWFLAKE_ROLE=R3_CARTOGRAPHY_RO SNOWFLAKE_WAREHOUSE=COMPUTE_WH \
  SNOWFLAKE_DATABASE=TEST_DG1_GEP SNOWFLAKE_SCHEMA=WAREHOUSE_TEST_GP226 \
  SNOWFLAKE_PRIVATE_KEY="$(az keyvault secret show --vault-name aldc-vault-test \
    --name snowflake-r3-cartography-nonprod --query value -o tsv | base64 -w0)" \
  npx next dev --webpack --port 3101
```

⚠ **Trap 1 — `R3_CARTOGRAPHY` is KEY-PAIR, not password.** `SNOWFLAKE_PRIVATE_KEY` as base64 PKCS8
PEM, `authenticator: SNOWFLAKE_JWT`. A password attempt returns
`250001 (08001) Incorrect username or password` — **with the correct secret, user and role**. It
reads as a bad credential and is a wrong auth *method*, and it cost this session a detour back
toward the vault. F99's identity binding must carry the auth method.

⚠ **Trap 2 — `--webpack` is load-bearing.** Next 16 defaults to Turbopack, which rejects a junctioned
`node_modules`: *"Symlink [project]/node_modules is invalid, it points out of the filesystem root"*.
Webpack follows the junction. Without that flag the worktree route needs a full `npm install`.

⚠ **Trap 3 — the `.next` lock is per-DIRECTORY, not per-port.** MEASURED: the lane set `PORT=3101`
and Next still refused, naming the *Dir*. A second dev server in the same directory cannot start,
whatever port you give it. That is why the worktree exists.

---

## Reusable probes this session left behind

```bash
python scripts/probe_test_data_currency.py       # 6 objects: presence, rows, date window
python scripts/probe_object_reachability.py FQN  # ABSENT_OR_INVISIBLE / UNAUTHORIZED_SELECT / READABLE
python scripts/probe_absent_vs_invisible.py      # the 4-reading triangulation
```

All three import `_connect` from `scripts/snowflake_bootstrap_r3.py` rather than reimplementing
auth, so they inherit the key-pair branch and the credential-use log.

⚠ **`probe_object_reachability.py` uses `LIMIT 1`, not `COUNT(*)`, on purpose.** Its first version
answered an *authorization* question with a count, timed out at 120s against a fact table, and
reported nothing at all.

---

## ⛔ Not done — the honest list

- **Nothing is pushed.** Six `agent-factory` commits are local only: `0d3ba52`, `ff9a51e`, `d9a0c5f`,
  `70a4f0d`, `86a1dff` (+ `48fae74`, another session's). Wiki `a923f9e` also unpushed.
- **The decisive lineage query was never run** — it needs privileges above the reader:
  ```sql
  SELECT REFERENCED_SCHEMA, REFERENCED_OBJECT_NAME FROM SNOWFLAKE.ACCOUNT_USAGE.OBJECT_DEPENDENCIES
  WHERE REFERENCING_OBJECT_NAME = 'MARKETING_EFFICIENCY';
  SHOW VIEWS LIKE 'SALES_FCT_ORDERLINE' IN SCHEMA TEST_DG1_GEP.WAREHOUSE;
  ```
- **The worktree at `navira-wt-warehouse` was left in place**, with a `node_modules` junction.
- ⚠ **My wiki commit `a923f9e` swept in three `standup/*.md` files and a JSON that were another
  session's untracked work** — `git add -A` where a scoped add belonged. Additive docs, nothing
  broken, but it is the 2026-08-23 hazard and I caused it.
- **`WAREHOUSE_SOURCE` vs `WAREHOUSE` was NOT repointed.** Every `GEP/snowflake/warehouse/*.sql`
  builds into `WAREHOUSE_SOURCE`; nothing in `clients` creates `WAREHOUSE.SALES_FCT_ORDERLINE`; the
  copy is done by the task chain. Since the copy is by design, **the dashboard's reference is
  correct** and no repoint is wanted — recorded because two hours were spent establishing it.
- **`MARKETING_ATTRIBUTED_SALES_BY_DEST` ends 2026-09-01**, one day behind the other four. Refresh
  lag vs source boundary: **NOT-ESTABLISHED**.
- **Deployed `SNOWFLAKE_SCHEMA` is 31 days newer than its nine siblings** (55d vs 86d) — changed
  alone, for a reason nothing records. Worth one question to whoever changed it.

## Jira / ticket state

- ✅ **Comment `36270` posted to GP-318** — *"Navira — Google ad spend in the Data Model: get the TEST
  Data Model fully working and client-reviewable"*, status `GEP QA`. **The key was verified via the
  API, not inferred from a branch name.**
- ⓘ **GP-319 is `Customer Cancelled`** as of 2026-09-02. Two comments drafted for it sit unposted in
  `boot-prompts/drafts/` and should not be posted without a decision.

## Gotchas earned

1. **A basis register cannot see the wrong subject.** `F101`: a false conclusion shipped *with* a
   correctly formatted MEASURED/DERIVED split, because the register grades the inference from
   evidence to claim and is blind to whether the evidence concerns the right object. Target
   identification sits upstream of every basis label.
2. **`| tail -N` on a list sorted newest-first is an unmeasured filter.** It discarded the row that
   mattered and produced two published falsehoods (`F101`).
3. **A piped exit code is the pipeline's, not the command's.** `[exited with code 0]` appeared
   directly beneath `Exit code: 1`. Believing it files a `NOT_RUN` as a pass.
4. **`python -c` mangles backslashes exactly as heredocs do.** A `\\n` inside a replacement string
   became a real newline and corrupted a code block. Use Write/Edit for backslash content.
