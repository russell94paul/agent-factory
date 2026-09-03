# Deployed surface and the warehouse lane — what was measured, 2026-09-02

**Measured 2026-09-02** against `agent-factory` @ `0d3ba52` (`main`) and
`~/repos/navira-marketing-dashboard` @ working tree. `evidence_class` **CONSUMER** ·
basis **MEASURED** except where a row says otherwise.

This session set out to clear the remaining blockers in
`boot-prompts/switchboard-p1-and-finalization-2026-09-01.md`. Outcome: **two cleared, one already
closed before the session began, one confirmed correct as recorded, and one turned into a measured
FAIL with a named cause.**

⭐ **The headline is §3b.** Warehouse mode does not render **for the read-only identity** — the
dashboard returns **HTTP 500** because `R3_CARTOGRAPHY_RO` cannot resolve
`TEST_DG1_GEP.WAREHOUSE.SALES_FCT_ORDERLINE`. The concern going in was silent blanks; the reality is
a hard error before the first tile.

⛔ **AMENDED 2026-09-03.** This line first said the object *"is not in TEST"* and that warehouse mode
was *"broken for everyone on this branch"*. **Both are retracted.** The next measurement found two
secure views that read from it returning **12,378** and **10,418** rows — which an absent object
cannot do. What is measured is that **R3 cannot reach it**; whether it exists at all needs a
privileged identity. See §3b.

---

## 1. What was cleared — the read-only identity is proved, today

```
account    og35375.canada-central.azure
database   TEST_DG1_GEP      (TEST, not PROD)
identity   R3_CARTOGRAPHY / R3_CARTOGRAPHY_RO
warehouse  COMPUTE_WH
timeout    120s
refusal    ProgrammingError: 003001 (42501) — CREATE TABLE denied on TEST_DG1_GEP.PUBLIC
grants     1227, all within USAGE / SELECT
```

Regenerate:

```bash
python scripts/snowflake_bootstrap_r3.py --verify --warehouse COMPUTE_WH
```

Full evidence: [`R3-preflight-readonly-proof.md`](R3-preflight-readonly-proof.md), rewritten by that
command at `2026-09-02T13:20:29Z`.

⭐ **The write was executed and refused, not skipped.** `--verify` has no path that writes the
evidence file without a refusal: if the `CREATE TABLE` succeeds it drops the probe table and exits
non-zero, and if any grant falls outside `USAGE`/`SELECT`/`REFERENCE_USAGE` it exits non-zero
before writing. This satisfies F99's rule — `verified_at` is evidence of a verification that
happened, not a declarative claim.

⚠ **One retrieval was made**, with the operator's approval, and logged by the script:
`READ snowflake-r3-cartography-nonprod from azure-kv:aldc-vault-test for R3`. The value was fetched
in-process and handed to the driver; it was never printed, written, or placed in argv.

---

## 2. The deployed surface — `NOT-VISIBLE` was the correct verdict all along

The blocker recorded `deployed SNOWFLAKE_SCHEMA` as `NOT-VISIBLE`. That is **confirmed, and it is
not a gap in the record** — the variable exists and is encrypted, which is what `NOT-VISIBLE` means.

**The deployed project is `aldc/navira-marketing-dashboard` → `https://navira-mktg.analyticlabs.io`**
(HTTP **401**, basic auth). Its Production environment, by name only — no value was read:

```
SNOWFLAKE_SCHEMA        Encrypted   Production            55d ago
SNOWFLAKE_PRIVATE_KEY   Encrypted   Production            86d ago
SNOWFLAKE_ACCOUNT       Encrypted   Production            86d ago
SNOWFLAKE_USER          Encrypted   Production            86d ago
SNOWFLAKE_ROLE          Encrypted   Production            86d ago
SNOWFLAKE_WAREHOUSE     Encrypted   Production            86d ago
SNOWFLAKE_DATABASE      Encrypted   Production            86d ago
DATA_SOURCE             Encrypted   Production            86d ago
BASIC_AUTH_USER         Encrypted   Preview, Production   86d ago
BASIC_AUTH_PASSWORD     Encrypted   Preview, Production   86d ago
```

Regenerate (names only; `env ls` never prints a value):

```bash
vercel link --yes --project navira-marketing-dashboard --scope aldc   # in a scratch dir
vercel env ls
```

⭐ **Two facts worth carrying that the listing gives away for free.**

1. **The deployed app authenticates with a private key** (`SNOWFLAKE_PRIVATE_KEY`), under
   `authenticator: "SNOWFLAKE_JWT"` — *"password sign-ins require MFA, which a headless app can't
   satisfy"* (`warehouse.ts:2038`).
   ⛔ **CORRECTED after this file was first committed.** This row originally said *"`R3_CARTOGRAPHY`
   is password-based, so it is not drop-in."* **Both halves were wrong.** `R3_CARTOGRAPHY` is
   **key-pair too** — proved when a password connection returned `250001` and the working path
   turned out to branch on `-----BEGIN` (see §3). So the auth methods **match**, and repointing the
   deployed surface at the read-only identity needs no key-generation step, only the existing PEM
   base64-encoded. Whether it *should* be repointed is a separate decision and is not taken here.
2. **`SNOWFLAKE_SCHEMA` is 31 days newer than every other Snowflake variable** (55d vs 86d). It was
   changed alone, after the rest were set. Whatever it now holds, it is not the value the other
   nine were configured alongside.

⛔ **The value was deliberately not read.** Obtaining it requires `vercel env pull`, which writes
**every** variable — including `SNOWFLAKE_PRIVATE_KEY` and `BASIC_AUTH_PASSWORD` — to disk. Landing
two live secrets on disk to learn one non-secret schema name is a bad exchange, and the operator
declined it. It stays `NOT-VISIBLE`, which is an honest verdict rather than a missing one.

---

## 3. The warehouse lane — two refused attempts, then a pinned worktree that ran

`playwright.warehouse.config.ts` (GP-288) is the right instrument: it runs the app against live
`TEST_DG1_GEP` on port 3101 and asserts **presence / non-blank / positivity**, never exact figures,
because *"the goal is 'the client never sees a silent —/$0/0.0x where real data is expected'"*.

**Attempt 1 — the webServer could not start.**

```
[WebServer] ⨯ Another next dev server is already running.
- PID: 40440   Dir: C:\Users\PaulRussell\repos\navira-marketing-dashboard
Error: Process from config.webServer was not able to start. Exit code: 1
[exited with code 0]
```

⚠ **Note the last line.** `[exited with code 0]` is the *pipeline's* status — the run was piped to
`tail`. The test never executed. Reported as `NOT_RUN`; had the pipeline status been believed this
would have been filed as a pass over a run that did not happen.

**Attempt 2 — reuse the running server. Refused on measurement.**

The reuse was authorised on a stated condition: it is valid only if that server is itself in
warehouse mode. `src/components/insite/DashboardShell.tsx:26` supplies the discriminating test in
the code's own words — brand options are *"2 entities synthetic / ~110 vendors warehouse"*.

```bash
curl -s http://localhost:3010/ | grep -oE '.{80}isWarehouse.{120}'
```

```
"brandOptions":[{"id":"navira","name":"Navira"},{"id":"lectric","name":"Lectric"}],"isWarehouse":false
                                                                    ...  "isWarehouse":false
```

**Two brands. `isWarehouse: false`, twice.** The server on 3010 is **synthetic**.

⛔ **So the lane was not run against it.** Every assertion in the warehouse spec — presence,
non-blank, positivity — would have **passed on fabricated data**, producing a GREEN that meant
nothing. That is exactly the failure the lane exists to catch (*"the class of bug a synthetic run
passes straight over"*), and it is the blind-instrument family this estate has now met six times.
A refused run is a better outcome than a green one over the wrong provider.

**Attempt 3 — a pinned worktree, which worked.** See §3b for the result. The route that avoided
the operator entirely:

```bash
cd ~/repos/navira-marketing-dashboard
git worktree add --detach C:/Users/PaulRussell/repos/navira-wt-warehouse df76dfb
cmd //c mklink //J "<worktree>/node_modules" "<repo>/node_modules"    # a junction, not a copy
```

⚠ **And the junction does not survive Turbopack.** Next 16 defaults to it and refuses:
*"Symlink [project]/node_modules is invalid, it points out of the filesystem root"*. Running
`npx next dev --webpack` instead works — webpack follows the junction. That one flag is the
difference between this lane being runnable in a worktree and needing a full `npm install`.

**What the earlier attempts needed:** the `.next` lock released, so the lane could start its own
server in warehouse mode. ⚠ **It is a per-DIRECTORY lock, not a port collision** — MEASURED: the lane set `PORT=3101`
via `webServer.env` and Next still refused, naming the **Dir**. Changing the port does not help.
PID 40440 is very likely the operator's session and was not killed.

```bash
taskkill /PID 40440 /F     # operator's call, not taken here
cd ~/repos/navira-marketing-dashboard && \
  SNOWFLAKE_ACCOUNT=og35375.canada-central.azure SNOWFLAKE_USER=R3_CARTOGRAPHY \
  SNOWFLAKE_ROLE=R3_CARTOGRAPHY_RO SNOWFLAKE_WAREHOUSE=COMPUTE_WH \
  SNOWFLAKE_DATABASE=TEST_DG1_GEP \
  SNOWFLAKE_PRIVATE_KEY="$(az keyvault secret show --vault-name aldc-vault-test \
    --name snowflake-r3-cartography-nonprod --query value -o tsv | base64 -w0)" \
  npx playwright test --config=playwright.warehouse.config.ts --reporter=list
```

⛔ **CORRECTED 2026-09-02, after this file was first committed.** The command above originally
passed `SNOWFLAKE_PASSWORD`. **That was wrong and would have failed.** `R3_CARTOGRAPHY` is
**key-pair**, not password: `scripts/snowflake_bootstrap_r3.py:157` branches on `-----BEGIN` in the
retrieved credential, and `warehouse.ts:2038-2041` wants `SNOWFLAKE_PRIVATE_KEY` as a
**base64-encoded PKCS8 PEM** with `authenticator: "SNOWFLAKE_JWT"` — because *"password sign-ins
require MFA, which a headless app can't satisfy."*

⭐ **How the error presents is the reusable part.** A password attempt against a key-pair identity
returns:

```
250001 (08001): Failed to connect to DB … Incorrect username or password was specified.
```

That reads as *a wrong credential* and is actually *a wrong auth method* — with the correct secret,
the correct user and the correct role. It sent this session looking at the vault for a better
password when nothing was wrong with the one it had. **F99's identity binding must therefore carry
the auth METHOD, not just account/user/role/scope**, or its own failure mode is indistinguishable
from a bad password.

⭐ **And whoever runs it must check `isWarehouse: true` and a ~110-brand payload BEFORE trusting a
single assertion.** The mode check is not a nicety; it is the difference between the lane measuring
something and the lane decorating a synthetic run.

---

## 3a. ✅ TEST holds current marketing data — the "greenfield" concern is retired

**MEASURED 2026-09-02** as `R3_CARTOGRAPHY_RO`, read-only, against the schema the app defaults to
(`warehouse.ts:2029`). This was run **before** the render lane on purpose: the lane asserts
presence/non-blank/positivity, so if these tables were empty it would fail *correctly* and the
failure would be filed against the dashboard instead of against the data.

```
TEST_DG1_GEP.WAREHOUSE_TEST_GP226 — 31 objects visible to R3_CARTOGRAPHY_RO

  PRESENT_WITH_DATA   MARKETING_FCT_ACTIVITY_UNIFIED       rows=916,051   ACTIVITY_DATE 2024-01-01 -> 2026-09-02
  PRESENT_WITH_DATA   MARKETING_ATTRIBUTED_ROAS_BY_BRAND   rows=3,623     ACTIVITY_DATE 2024-01-01 -> 2026-09-02
  PRESENT_WITH_DATA   MARKETING_ATTRIBUTED_SALES_BY_DEST   rows=829       ACTIVITY_DATE 2024-06-01 -> 2026-09-01
  PRESENT_WITH_DATA   MARKETING_GOOGLE_SPEND_BY_DEST       rows=1,548     ACTIVITY_DATE 2024-06-01 -> 2026-09-02
  PRESENT_WITH_DATA   MARKETING_META_SPEND_BY_DEST         rows=135       ACTIVITY_DATE 2026-04-20 -> 2026-09-02
  PRESENT_WITH_DATA   SHARED_DIM_MARKETPLACE               rows=21,901    (no date column)
```

⭐ **All six objects the dashboard reads are present and current to today.**
`mission-wave1-checkpoint-2026-09-01.md` §3 flagged TEST's currency as unverified, citing a Navira
re-land that was *"planned, not executed"* and Lectric's *"greenfield in TEST (no objects)"*. **That
condition is retired for these six objects.** ⚠ It is retired *for these six only* — the claim is
about the objects enumerated above, not about TEST as a whole.

⛔ **AND THE FINDING THAT MATTERS FOR READING THE RENDER LANE: Meta's history is 22 months shorter
than Google's.**

| | first | last | rows |
|---|---|---|---|
| `MARKETING_GOOGLE_SPEND_BY_DEST` | **2024-06-01** | 2026-09-02 | 1,548 |
| `MARKETING_META_SPEND_BY_DEST` | **2026-04-20** | 2026-09-02 | 135 |

**Any date range starting before 2026-04-20 will show Meta spend as zero or blank — correctly.**
That is data coverage, not a dashboard defect, and it is exactly the shape a render check misreads:
a blank tile where the reader expects a number. The lane must interpret a Meta blank against this
window before calling it a failure, and a client-facing surface showing a 2024 range needs to say
why Meta is absent rather than showing a silent `—`.

⚠ Also noted, minor: `MARKETING_ATTRIBUTED_SALES_BY_DEST` ends **2026-09-01**, one day behind the
other four. Whether that is a refresh lag or a source boundary is **NOT-ESTABLISHED**.

Regenerate — the probe imports `_connect` from `scripts/snowflake_bootstrap_r3.py` rather than
reimplementing auth, so it inherits the key-pair branch and the credential-use log:

```bash
python scripts/probe_test_data_currency.py      # see §3 note on auth
```

---

## 3b. ⛔ WAREHOUSE MODE DOES NOT RENDER — the sales fact is not in TEST

**MEASURED 2026-09-02.** The lane was finally run, in a **pinned worktree** at `df76dfb` with
`node_modules` junctioned, so the operator's own dev server was never touched. The dashboard
**started, served, and returned HTTP 500**:

```
OperationFailedError: SQL compilation error:
Object 'TEST_DG1_GEP.WAREHOUSE.SALES_FCT_ORDERLINE' does not exist or not authorized.
```

⭐ **This is the answer to "warehouse-mode rendering is NOT-EXERCISED", and it is not the answer
anyone was expecting.** The concern was silent blanks and zeros. The actual behaviour is a hard
500 on the first request — the surface does not render at all.

### `does not exist` OR `not authorized`? They are different worlds, so they were separated

Snowflake deliberately conflates the two so it cannot leak the existence of hidden objects. Good
security, useless as a measurement: one branch means *the data was never landed in TEST*, the other
means *the reading role is under-granted*, and the fixes are unrelated. `scripts/probe_object_reachability.py`
resolves it against the catalogue:

```
ABSENT_OR_INVISIBLE   TEST_DG1_GEP.WAREHOUSE.SALES_FCT_ORDERLINE
    schema WAREHOUSE IS visible and lists 34 objects, but not SALES_FCT_ORDERLINE
    nearest names present: EXTRACT_SALES_BY_DAY, EXTRACT_SALES_DETAIL, SALES_FCT_BUDGET,
      SALES_FCT_COST_HISTORY, SALES_FCT_ORDERLINE_PREBUILD_ROLLBACK,
      SALES_FCT_ORDERLINE_RB_20260708, SALES_FCT_SCOL_GP259A_VAL
```

**The schema is readable and lists 34 objects. The table is not one of them — but two rollback
copies of it are**, one stamped `RB_20260708`. That shape says a rebuild made backups and the
primary was dropped or renamed and never restored.

`REPORT_COMMON`, the schema GP-318 repoints toward, does not have it either:

```
ABSENT_OR_INVISIBLE   TEST_DG1_GEP.REPORT_COMMON.SALES_FCT_ORDERLINE
    schema REPORT_COMMON IS visible and lists 17 objects, but not SALES_FCT_ORDERLINE
    nearest names present: RETAIL_DAILY_SALES_DATE, RETAIL_DAILY_SALES_FACT,
      RETAIL_DAILY_SALES_LOCATION
```

### It is not my worktree, and it is not stale code

MEASURED in both states, so nobody has to wonder whether the pinned checkout caused it:

```bash
grep -n "SALES_FCT_TABLE\s*=" src/lib/data/providers/warehouse.ts   # working tree
git show df76dfb:src/lib/data/providers/warehouse.ts | grep -n SALES_FCT_ORDERLINE
```

Both give `warehouse.ts:82`:

```ts
const SALES_FCT_TABLE = "TEST_DG1_GEP.WAREHOUSE.SALES_FCT_ORDERLINE";
```

⭐ **The committed state and the operator's uncommitted working tree are identical on this line.**
`df76dfb` is *"fix(GP-318): repoint the efficiency family reads to REPORT_COMMON (canonical)"*, and
the file carries **11** `REPORT_COMMON` references — so the efficiency family was repointed and
**the sales fact was left pointing at an object that is no longer there**. Warehouse mode is
therefore broken for everyone, on the current branch, not just for this run.

⛔ **CORRECTED 2026-09-03 — the lean above was wrong, and the diagnosis has changed.**

This section originally read: *"`R3_CARTOGRAPHY_RO` holds `SELECT ON ALL` and `ON FUTURE` tables and
views in the database, so an existing object ought to appear in its `INFORMATION_SCHEMA`. That makes
**ABSENT** much the likelier branch."* **The next measurement pointed the other way**, and it was a
measurement this session should have taken before writing that sentence.

`scripts/probe_absent_vs_invisible.py` — three readings side by side:

```
1. role-visible objects named SALES_FCT_ORDERLINE* in WAREHOUSE
   SHOW VIEWS   -> 0: []
   SHOW TABLES  -> 2: ['SALES_FCT_ORDERLINE_PREBUILD_ROLLBACK', 'SALES_FCT_ORDERLINE_RB_20260708']

2. direct SELECT as R3 — the dashboard's own path
   REFUSED -> 002003 (42S02): SQL compilation error

3. the secure-view chain that depends on it (executes with OWNER's rights)
   MARKETING_EFFICIENCY         rows=12,378
   MARKETING_EFFICIENCY_MARGIN  rows=10,418

4. lineage — the decisive instrument
   SNOWFLAKE.ACCOUNT_USAGE.OBJECT_DEPENDENCIES not readable by this role
```

⭐ **Reading 3 is the one that breaks the earlier conclusion.** Per the repo, five `report_common`
views read `FROM WAREHOUSE.SALES_FCT_ORDERLINE` — and two of them return **12,378** and **10,418**
rows in TEST right now. **A secure view executes with its owner's rights, but owner's rights cannot
conjure an object that is not there.** So either:

| | branch | consequence |
|---|---|---|
| **A** | The object **exists** and `R3_CARTOGRAPHY_RO` simply lacks `SELECT` on it | The 500 is an **under-granted role**. The fix is a grant. Warehouse mode may be broken **only for R3** — the deployed app runs as a different Snowflake user which may well hold the grant |
| **B** | The **deployed** `MARKETING_EFFICIENCY` in TEST differs from its repo file and reads elsewhere | The object may indeed be gone, and the repo does not describe what is deployed |

⚠ **Branch B is not hypothetical.** `wiki/tickets/gep/GP-318.md` records that **11 of 15
`REPORT_COMMON` objects had no file anywhere in `clients`** — *"REPORT_COMMON was almost entirely
unmanaged"*. So a deployed view diverging from the repo is a documented condition here, not a
stretch.

⛔ **Neither branch can be settled with `R3_CARTOGRAPHY_RO`**, and this is a real instrument limit,
not a gap in effort: `SHOW`/`INFORMATION_SCHEMA` expose only what a role holds privileges on,
`ACCOUNT_USAGE.OBJECT_DEPENDENCIES` is denied to it, and a secure view's DDL is hidden from
non-owners. **The decisive reading needs a privileged identity**, and it is one query:

```sql
-- as an admin: settles branch A vs B outright
SELECT REFERENCED_SCHEMA, REFERENCED_OBJECT_NAME, REFERENCED_OBJECT_DOMAIN
FROM SNOWFLAKE.ACCOUNT_USAGE.OBJECT_DEPENDENCIES
WHERE REFERENCING_OBJECT_NAME = 'MARKETING_EFFICIENCY';

SHOW VIEWS LIKE 'SALES_FCT_ORDERLINE' IN SCHEMA TEST_DG1_GEP.WAREHOUSE;   -- exists at all?
```

### What survives the correction, and what does not

| Claim | Status |
|---|---|
| The dashboard returns HTTP 500 in warehouse mode as `R3_CARTOGRAPHY` | ✅ **MEASURED, stands** |
| `R3_CARTOGRAPHY_RO` cannot see or select `WAREHOUSE.SALES_FCT_ORDERLINE` (`002003`) | ✅ **MEASURED, stands** |
| `warehouse.ts:82` is identical at `df76dfb` and in the working tree | ✅ **MEASURED, stands** |
| Two rollback copies exist and the primary is not role-visible | ✅ **MEASURED, stands** |
| *"The sales fact is not in TEST"* | ⛔ **RETRACTED — NOT ESTABLISHED.** Reading 3 is evidence against it |
| *"Warehouse mode is broken for everyone on this branch"* | ⛔ **RETRACTED — NOT ESTABLISHED.** Measured broken **for R3**; the deployed app authenticates as a different user whose grants were never checked |

⭐ **And the repo says the schema convention is the other one.** Every `GEP/snowflake/warehouse/*.sql`
builds into **`WAREHOUSE_SOURCE`**, never `WAREHOUSE` —
`create or replace secure view WAREHOUSE_SOURCE.SALES_FCT_ORDERLINE(...)`. **Nothing in `clients`
creates `WAREHOUSE.SALES_FCT_ORDERLINE`**, yet five `report_common` views read from it. MEASURED,
and readable by R3:

```
READABLE   TEST_DG1_GEP.WAREHOUSE_SOURCE.SALES_FCT_ORDERLINE   VIEW
```

So a third possibility sits underneath both branches: the `WAREHOUSE` schema is populated by
something outside the repository, and `WAREHOUSE_SOURCE` is where the managed definition lives.
⛔ **Which of the two the dashboard SHOULD read is a decision, not a measurement**, and it is not
taken here — the wiki's own GP-318 census counts `SALES_FCT_ORDERLINE` among objects with live
entity-scoping consequences, so repointing it is a data-ownership call with a blast radius.

⛔ **Not fixed here, deliberately.** Three candidates exist — the two rollback copies and whatever
GP-318 intends as canonical — and picking one by name similarity is exactly the wrong-target failure
this session already paid for once (`F101`). Naming the successor is the data owner's call.

### What this means for the two rendering blockers

| | verdict | why |
|---|---|---|
| warehouse-mode rendering | ⛔ **FAIL — measured** | HTTP 500 on `/`, missing sales fact. Not a blank; a hard error |
| `DATE RANGE` inertness in warehouse mode | **NOT-MEASURABLE** | the page never renders, so no filter can be exercised. This is `UNMEASURABLE`, not `FAIL` — the instrument could not look |

⭐ **And the Meta window from §3a never got to matter.** It was measured before the lane on the
theory that a blank Meta tile would be misread as a defect. The lane never reached a tile. The
measurement stands and will matter the moment the sales fact is restored — that is the difference
between a prerequisite and a wasted step.

---

## 4. One blocker was already closed before this session

The blocker list records *"every Power BI rendered figure — `NOT-EXERCISED` — needs a DAX
instrument"*. **That instrument exists and ran on 2026-09-01**, producing
[`pbi-ad-sales-live-2026-09-01/`](pbi-ad-sales-live-2026-09-01/) with a repro script and raw DAX
results. It settled the live definition of `Actual - Marketing - Ad Sales` and moved two claims from
`PARTIALLY_CONFIRMED` / `DOCUMENTED` to **MEASURED**.

The blocker table was written before that session landed. ⚠ It uses **no service account** — token
acquisition rides the operator's existing `az` session in the `aldc.io` tenant.

⭐ **Carry this one:** that package records that a DAX error returns **HTTP 200 with an empty row
list**, not a failed request. An instrument treating empty-as-zero there reports a clean nothing.

---

## 5. Status after this session

| Item | Before | After | Basis |
|---|---|---|---|
| R3 read-only identity | proved 2026-09-01 | ✅ **re-proved 2026-09-02** | MEASURED — refusal watched |
| deployed `SNOWFLAKE_SCHEMA` | `NOT-VISIBLE` | **`NOT-VISIBLE`** (confirmed correct) | MEASURED that it exists and is encrypted |
| TEST marketing-data currency | UNVERIFIED since 2026-09-01 | ✅ **cleared** — 6 objects, current to today | MEASURED, §3a |
| warehouse-mode rendering | `NOT-EXERCISED` | ⛔ **FAIL for R3** — HTTP 500, object unresolvable | MEASURED, §3b. ⚠ Cause is under-granted role **or** absent object; not yet separated |
| `DATE RANGE` inertness | `NOT-MEASURED` | **UNMEASURABLE** — the page never renders | §3b |
| Power BI rendered figures | `NOT-EXERCISED` | ✅ **closed 2026-09-01** | the blocker list was stale |

## Basis register — the weakest claims here

| Claim | Basis |
|---|---|
| The refusal, the grant count, the two brands, `isWarehouse: false`, the 401, the env-var names | **MEASURED** this session, each with its command above |
| `SNOWFLAKE_SCHEMA` is 31 days newer than its siblings | **MEASURED** from `env ls` timestamps; what changed and why is **NOT-RECORDED** |
| "PID 40440 is the operator's session" | ⚠ **ASSUMED.** Measured: the PID, the port and the directory. Ownership was inferred and the process was left alone because of it |
| The deployed app serves warehouse data | ⛔ **NOT ESTABLISHED.** `DATA_SOURCE` exists but its value was not read, and the surface is behind 401. Do not assume either way |
