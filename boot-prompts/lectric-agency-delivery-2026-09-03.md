# Boot — Lectric agency data: delivery decision + share build

**Written 2026-09-03.** Supersedes nothing; first boot prompt for this workstream.
**Ticket:** **GP-330** — "Navira — deliver Lectric agency sales data: one-off extract vs
persistent Snowflake share (client decision pending)", created 2026-09-03, status
Consulting/Design, assigned Paul. Split out of **GP-254** ("Lectric eBikes Integration — Agency
Test", **status Done**), which now carries the audit comment. Related: GP-297 (Lectric COGS),
GP-294 (TEST/PROD parity), GP-231 (multi-tenant connectors), GP-311 (Unknown rows).

`next:` **Wait on Justin's answer. Build nothing until it lands.** Paul emailed him 2026-09-03
asking whether it is a one-off dump or persistent delivery on a daily schedule. The answer changes
the work, and the connector stays on meanwhile so no history is lost either way.

---

## Where this actually stands

A client question ("how do we get Lectric sales to Justin?") turned into a read-only audit. Nothing
was deployed and nothing changed. Paul then emailed Justin on 2026-09-03 with the clarifying
question, so the ball is with the client.

**The Lectric dataset is real and TEST-only.** `TEST_DG1_GEP.WAREHOUSE.SALES_FCT_ORDERLINE` where
`ENTITY_CODE='LECTRIC'`:

| metric | value |
|---|---|
| order lines | 5,310 |
| orders | 5,008 |
| products (ASINs) | 29 |
| units | 5,713 |
| gross USD | $2,822,972 |
| span | 2024-05-31 → 2026-09-03 |

**The API connector is live and healthy** in TEST Cosmos — template
`e7eaf791-88cc-5b88-bad6-9883a651cb19`, `status=active`, US only, 67 partitions all with
`run_count > 0`, firing daily ~10:0x UTC. It is landing data right now.

**TEST vs PROD parity is a clean pass.** The only column difference is `ENTITY_CODE` (118 vs 117).
PROD has no `AMAZON_LECTRIC` schema. Paul confirmed this is intended: *"we don't promote past
test."*

## Blockers and open threads

1. **⛔ BLOCKING — client decision, now with the client.** Paul **emailed Justin on 2026-09-03**
   asking whether it is a one-off dump or consistent/persistent delivery pulled daily. Awaiting
   reply. The sent text is not in the repo — only the numbers it quoted (above) are recorded.
2. **⚠ The two options are NOT equally ready.** One-off extract works today. **A share requires
   PROD promotion first** (Lectric rows + `ENTITY_CODE` are TEST-only). Do not offer both as
   same-day options.
3. **Jira is up to date.** GP-330 created with the full technical brief; GP-254 carries the audit
   comment (id `36274`); GP-330 carries the client-contact comment (id `36273`). ⚠ The first
   comment attempt was classifier-blocked and a later retry succeeded — **the block is transient,
   so retry before concluding the MCP is unavailable.**
4. **The share view is specified, not built.** ~24 live columns, sales-only (COGS/margin/fees
   excluded per Paul), `LINE_STATUS <> 'Unknown'` filter. Three decisions still open: is
   `CUSTOMER_ID` in (98.9% populated, privacy call)? are the `_TRANSACTION` local-currency twins
   in? `DELIVERY_DATE` is only 3.8% populated and `RETURN_DATE` is stored as **TEXT** — both
   dropped, revisit if delivery reporting matters.
5. **Measurement scripts are NOT committed.** They live in a session scratchpad
   (`prod_orderline_profile.py`, `parity_v2.py`, `parity_columns.py`, `test_lectric_dataset.py`,
   `null_company_bucket.py`, `share_column_census.py`, `lectric_template_live.py`,
   `lectric_schedule_state.py`). Every number in the Jira draft is reproducible only by re-running
   them. Committing them to a repo evidence folder is outstanding.
6. **Decide whether to leave the connector running.** ~2 months unattended. Deactivation is a
   template flip (`--apply` **without** `--activate`), not an agent kill — there is no agent.
7. ~~GP-254 is Done while delivery is undecided~~ — resolved: delivery now lives on **GP-330**.
   GP-254 can stay closed; the connector's on/off decision belongs to GP-330.

## Gotchas earned — read before touching any of this

- ⭐ **A bounded `min_date` is a fact about the feed, never about the data.** Both Paul and I read
  `min_date=2026-07-01` as evidence Lectric had no history. It has 27 months. Two loads coexist: a
  one-off backfill from 2024-05 plus the connector appending since July.
- ⭐ **Snowflake returns the same conflated `002003` for "object does not exist" and "you have no
  grant."** My verdict classifier read a permission failure as a missing table and invalidated a
  whole parity run *including its own control*. Establish existence via `INFORMATION_SCHEMA` (needs
  no object grant) **before** any SELECT. The same handler then mislabelled a timeout (`000604`) and
  a compilation error (`000904`) as NO-GRANT — **report error codes verbatim, never reclassify.**
- ⭐ **`WAREHOUSE.SALES_FCT_ORDERLINE` blinks out of existence hourly.** It is
  `CREATE OR REPLACE`d by `task_warehouse_orderline` (cron `50 * * * *`). I measured it vanishing
  from `INFORMATION_SCHEMA` between two of my own runs, and a query against it timed out
  mid-rebuild. **Sharing that object directly would give Justin unexplainable intermittent
  failures** — a share wants a `DATA_SHARE` object refreshed once after the DAG, not the live table.
- ⭐ **`BY_LAST_UPDATE` cannot backfill.** The live template uses
  `GET_FLAT_FILE_ALL_ORDERS_DATA_BY_LAST_UPDATE_GENERAL`; partitions walk *update* dates, so a
  historical re-pull will not re-emit quiet 2024 orders. GP-254's own 2026-06-05 note says the same
  thing measured: *"`BY_LAST_UPDATE` returns empty for >30-day/historical ranges — use
  `BY_ORDER_DATE` + calendar-month chunks."* Two independent routes, same conclusion.
- ⭐ **No field selection exists in the live Cosmos template.** It pulls the whole flat file, so any
  column Amazon emits already lands. **Adding warehouse columns is SQL-only** — no template change,
  no Cosmos deploy, no Amazon backfill. The staging table already holds 7 columns the orderline view
  discards: `SELLER_SKU`, `MARKETPLACE`, `PURCHASE_DATE`, `FULFILLMENT_CHANNEL`, `ORDER_STATUS`,
  `ADDRESS_SHIP_COUNTRY`, `ENTITY_NAME`.
- ⭐ **`--plan` on `_deploy_lectric_cosmos_test.py` never connects to Cosmos.** It returns before the
  client is constructed and just echoes the git JSON. It is a pre-apply preview, **not a diff.** To
  read the live doc, query `work_template` directly with a read-only Cosmos key.
- ⭐ **32 of 78 numeric columns in the PROD orderline fact are inert** — never non-zero. Census
  before sharing. Details now in `wiki/concepts/architecture/star-schema-convention.md`.
- ⚠ **`re.sub` processes backslash escapes in the replacement string.** A Windows path via `repr()`
  had its `\\` collapsed, `\Users` became a broken unicode escape, and the generated file would not
  parse. Use a function replacement plus forward slashes, and **assert the generated source parses**
  rather than eyeballing escapes. Same family as the CLAUDE.md heredoc hazard.
- ⚠ **The PowerShell here-string `@'…'@` is a syntax error in the Bash tool.** Use `git commit -F
  <file>` for any multi-line message.
- ⚠ **A killed background grep prints a clean-looking empty result.** One reached 1 of ~60 repos and
  I published "zero PROD grants anywhere" off it. Re-swept scoped and the claim held, but the
  instrument had never been shown able to see.
- ⚠ **Do not select `queue_messages` from `work_partition`.** It is a blob field; printing its
  distribution burned a large slice of context for no information.

## Credentials — what works and what does not

| target | identity | source | status |
|---|---|---|---|
| PROD Snowflake | **`PROD_DG1_CORE_ADMIN` / ACCOUNTADMIN** | `aldc-vault-prod` / `snowflake-prod-admin` | ✅ works |
| TEST Snowflake | `R3_CARTOGRAPHY` / `R3_CARTOGRAPHY_RO` (key-pair) | `aldc-vault-test` / `snowflake-r3-cartography-nonprod` | ✅ works, read-only proven |
| TEST Cosmos | — | `az cosmosdb keys list --name aldctestcsdb1c01` → `primaryReadonlyMasterKey` | ✅ works |
| PROD Snowflake | `PAULRUSSELL` / SYSADMIN | `snowflake-prod-admin` | ❌ `250001` auth failure (2 attempts, stopped to avoid lockout) |
| PROD/TEST via dashboard | `NAVIRA_MKT_RO` | — | ❌ dead end: no `.secrets/` key locally, prod Vercel vars Sensitive, local `.env` is **ACCOUNTADMIN on the `WAREHOUSE_TEST_GP226` clone**, and every documented grant is TEST-scoped |

Prod account is **`wj66376.canada-central.azure`** (locator `WJ66376`); non-prod is `og35375`.
Lectric SP-API creds exist in **4 of 5 vaults** (dev/test/qa/prod, all one vintage 2026-05-28;
`aldc-cred-vault-qa` has none) — needed only for `--apply`, never for a read.

⚠ `wiki/entities/repos/navira-marketing-dashboard.md:242` says `NAVIRA_MKT_RO` "reads the table
live … probed with the app's own `.env`" but **drops the repo's own qualifier** — `PROGRESS.md:54`
adds *"role locally = ACCOUNTADMIN"*. Do not inherit that wiki line.

## Key paths

- Warehouse SQL: `clients/GEP/snowflake/warehouse/sales_fct_orderline.sql` — Lectric UNION branch
  `:740-860`, GP-311 guard + its rollback scar `:125-136`, Lectric no-FX copy `:788`
- Lectric staging DDL: `clients/GEP/snowflake/warehouse/sales_fct_lectric_amazon_orderline.sql`
- Consumer view: `clients/GEP/snowflake/report_common/MARKETING_EFFICIENCY.sql:83-107` (filters
  orderline to NAVIRA, rebuilds Lectric with FX)
- Eclipse template/connection: **branch `feature/paulrussell/lectric-scheduled-connector`** in
  `clients` — `GEP/eclipse/templates/amazon_lectric/all_orders_report.json`,
  `GEP/eclipse/connections/lectric_amazon_seller_central.json`. **Not merged to `GEP/development`**,
  so they are absent from the default checkout — read them with `git show <branch>:<path>`.
- Superseded 4-marketplace variant: branch `feature/paulrussell/gp-254/lectric-agency-onboarding`
- Deploy tool: `aldc-launchpad/warehouse_ops/_deploy_lectric_cosmos_test.py`
- Jira draft: `boot-prompts/drafts/GP-254-comment-2026-09-03.md`
- Wiki: `tickets/gep/GP-254.md`, `concepts/architecture/star-schema-convention.md`, `log.md`
  (committed `ebb9a37`)

## What was NOT done

- **No rendered/consumer-layer validation.** Query layer only. No PBI model opened, no dashboard
  loaded. Every claim here is about what SQL returns, not what a person sees.
- **Client email text has no repo copy** — it was sent from Paul's Outlook; only the figures it
  quoted are recorded here.
- **Share view not built.** No DDL written.
- **Scripts not committed.**
- **Nothing committed in agent-factory** — this file and the Jira draft are new and untracked.
- The mechanism by which partitions are picked **without an agent doc** is unproven — only that
  execution demonstrably happens.
