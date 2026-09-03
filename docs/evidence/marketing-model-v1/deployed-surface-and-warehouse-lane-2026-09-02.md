# Deployed surface and the warehouse lane — what was measured, 2026-09-02

**Measured 2026-09-02** against `agent-factory` @ `0d3ba52` (`main`) and
`~/repos/navira-marketing-dashboard` @ working tree. `evidence_class` **CONSUMER** ·
basis **MEASURED** except where a row says otherwise.

This session set out to clear three of the four blockers in
`boot-prompts/switchboard-p1-and-finalization-2026-09-01.md`. **One was cleared, one was already
closed before this session started, one is unchanged and its original verdict was right, and two
rendering checks remain `NOT_RUN` — deliberately, because the only shortcut available to run them
would have manufactured a false GREEN.**

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

1. **The deployed app authenticates with a private key** (`SNOWFLAKE_PRIVATE_KEY`), not a password.
   `R3_CARTOGRAPHY` is password-based, so it is **not** drop-in for the deployed surface even if
   that were wanted. Any plan to repoint production at the read-only identity has a key-generation
   step nobody has costed.
2. **`SNOWFLAKE_SCHEMA` is 31 days newer than every other Snowflake variable** (55d vs 86d). It was
   changed alone, after the rest were set. Whatever it now holds, it is not the value the other
   nine were configured alongside.

⛔ **The value was deliberately not read.** Obtaining it requires `vercel env pull`, which writes
**every** variable — including `SNOWFLAKE_PRIVATE_KEY` and `BASIC_AUTH_PASSWORD` — to disk. Landing
two live secrets on disk to learn one non-secret schema name is a bad exchange, and the operator
declined it. It stays `NOT-VISIBLE`, which is an honest verdict rather than a missing one.

---

## 3. The warehouse lane — `NOT_RUN`, and why the shortcut was refused

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

**What it needs:** port 3010 free, so the lane can start its own server in warehouse mode. PID
40440 is very likely the operator's session and was not killed.

```bash
taskkill /PID 40440 /F     # operator's call, not taken here
cd ~/repos/navira-marketing-dashboard && \
  SNOWFLAKE_ACCOUNT=og35375.canada-central.azure SNOWFLAKE_USER=R3_CARTOGRAPHY \
  SNOWFLAKE_ROLE=R3_CARTOGRAPHY_RO SNOWFLAKE_WAREHOUSE=COMPUTE_WH \
  SNOWFLAKE_DATABASE=TEST_DG1_GEP \
  SNOWFLAKE_PASSWORD="$(az keyvault secret show --vault-name aldc-vault-test \
    --name snowflake-r3-cartography-nonprod --query value -o tsv)" \
  npx playwright test --config=playwright.warehouse.config.ts --reporter=list
```

⭐ **And whoever runs it must check `isWarehouse: true` and a ~110-brand payload BEFORE trusting a
single assertion.** The mode check is not a nicety; it is the difference between the lane measuring
something and the lane decorating a synthetic run.

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
| warehouse-mode rendering | `NOT-EXERCISED` | **`NOT_RUN`** | blocked on port 3010 |
| `DATE RANGE` inertness | `NOT-MEASURED` | **`NOT_RUN`** | same |
| Power BI rendered figures | `NOT-EXERCISED` | ✅ **closed 2026-09-01** | the blocker list was stale |

## Basis register — the weakest claims here

| Claim | Basis |
|---|---|
| The refusal, the grant count, the two brands, `isWarehouse: false`, the 401, the env-var names | **MEASURED** this session, each with its command above |
| `SNOWFLAKE_SCHEMA` is 31 days newer than its siblings | **MEASURED** from `env ls` timestamps; what changed and why is **NOT-RECORDED** |
| "PID 40440 is the operator's session" | ⚠ **ASSUMED.** Measured: the PID, the port and the directory. Ownership was inferred and the process was left alone because of it |
| The deployed app serves warehouse data | ⛔ **NOT ESTABLISHED.** `DATA_SOURCE` exists but its value was not read, and the surface is behind 401. Do not assume either way |
