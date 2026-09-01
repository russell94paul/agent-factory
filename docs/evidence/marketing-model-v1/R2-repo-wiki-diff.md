# R2 — Repo ⨝ Wiki diff (Navira marketing model)

**Worker** R2 · mission `marketing-model-reconstruction-v1` · task `200deda2` · **READ ONLY**
**Subject:** Navira (GEP is the Jira project / client; Navira is the modelled entity).
**Date:** 2026-08-31. Every claim below cites a file and line I opened. Anything I could not
establish from a file is marked `NOT-VISIBLE` and is never guessed.

**Counts:** LOCKED **14** · STALE **11** · MISSING **23** · PRIOR ART **8**

---

## 0. The correction I was told to verify, not re-derive — CONFIRMED, with evidence

> *"the marketing dashboard reads **Snowflake directly**; the **Eclipse app** reads PBI. The
> disliked PBI model and the liked frontend do not share a data path."*

**Verified against both source trees. It holds, and it is stronger than stated.**

| Evidence | File · line |
|---|---|
| The dashboard imports the Snowflake Node driver | `navira-marketing-dashboard/src/lib/data/providers/warehouse.ts:23` — `import snowflake from "snowflake-sdk";` |
| It opens its own connection from env | `warehouse.ts:2020-2065` — `buildConnection()`, `SNOWFLAKE_ACCOUNT/USER/ROLE/WAREHOUSE`, JWT key-pair auth |
| Default database + schema are hardcoded | `warehouse.ts:2028-2029` — `TEST_DG1_GEP` / `WAREHOUSE_TEST_GP226` |
| The env contract names Snowflake and nothing else | `navira-marketing-dashboard/.env.example` — `SNOWFLAKE_*` only; `DATA_SOURCE=synthetic\|warehouse` |
| Provider switch is the only data path | `src/lib/data/get-provider.ts` — `warehouseProvider` or `syntheticProvider`; no third |
| **Zero PBI/DAX/XMLA references in `src/`** | grep for `power ?bi\|powerbi\|\bdax\b\|xmla\|analysis services\|dataset` over `src/**/*.ts,tsx` returns only `document.documentElement.dataset.theme` (a DOM property), the word "dataset" in test titles, and one code *comment* at `warehouse.test.ts:497`. No client, no endpoint, no query. |

**The stronger finding:** the dashboard and PBI were, for a period, fed by *different definitions of
the same object names*, and the repo records the moment that was caught —
`warehouse.ts:88-102` (GP-318, 2026-08-11):

> *"These four were previously read UNQUALIFIED, which resolved them in the connection's default
> schema (`WAREHOUSE_TEST_GP226`) — a second, divergent copy of the same objects. PBI reads the
> `REPORT_COMMON` copies, so the dashboard and PBI were fed by different definitions"* — the GP226
> `MARKETING_EFFICIENCY` copy *"MISSES Amazon US Sponsored Display ($3,374.90)"*.

So the two consumers do not merely take different routes — they took routes to **objects with the
same name and different contents**, and only four of them have since been repointed. Six objects the
dashboard reads are **still** unqualified and still resolve in `WAREHOUSE_TEST_GP226` (§3, M18).

Neither wiki document states any of this. `cross-channel-marketing-attribution.md:271` calls
`[[navira-marketing-dashboard]]` *"the consumer"* without saying what it reads;
`cross-channel-marketing-dimensional-model.md:410-437` (§8) frames the consumer question entirely as
a Power BI problem. **The docs are silent here, not wrong** — but a design pass that reads only §8
will design for the wrong consumer.

---

## 1. LOCKED — settled decisions the replacement must honour

`ATTR` = `wiki/concepts/architecture/cross-channel-marketing-attribution.md`
`DIM` = `wiki/concepts/architecture/cross-channel-marketing-dimensional-model.md`
`RC` = `clients/GEP/snowflake/report_common/`

### L1 — The six-tier measurement law
`ATTR:25-32`. Tier 0 Spend · 1 Platform ROAS · 2 Blended MER · 3 Product-grounded · 3.5
Contribution Margin · 4 Causal. `ATTR:34`: *"The source of truth is Tier 2 + Tier 3 — both put
**actual orders in the denominator**."* Implemented as the shape of the whole `MARKETING_*` family.

### L2 — ⭐ Platform-attributed value is **never summed across channels**
`ATTR:28` (*"❌ platform-reported; **never sum across channels**"*), restated `ATTR:34`.
This is the single most consistently honoured rule in the estate — it survives into four
independent layers:

| Layer | Where |
|---|---|
| Warehouse | `RC/MARKETING_EFFICIENCY.sql:20-22` — three separate columns `PLATFORM_ATTR_SALES_USD_{AMAZON,GOOGLE,META}`, never one summed column |
| Warehouse | `RC/MARKETING_EFFICIENCY_MONTHLY.sql:46-47` — `-- Tier 1 (labelled, never summed across channels)` |
| Frontend contract | `navira-marketing-dashboard/docs/FIELDS.md:40` — *"**Never** sum platform ROAS or platform-attributed sales across channels → double-count."* |
| Frontend code | `src/lib/data/types.ts:44` and `src/lib/metrics.ts:44-56` (the "Flag-A" docstring); `warehouse.ts:14-21` |

**Verdict on the lead's stated hierarchy:** the "never summed" half is **confirmed and locked**. The
ordering half needs correcting — see L3.

### L3 — ⚠ The locked headline metric is **blended MER**, not Contribution Margin
`ATTR:100`, Decision 1: *"✅ **DECIDED 2026-05-29 (Paul): adopt blended MER** as the board-level
'marketing efficiency' number."* Contribution Margin arrives later as **Tier 3.5**
(`ATTR:31`, `ATTR:111`), explicitly *"coverage-gated"*, and its own headline is scoped to the margin
stack (*"Headline = gross contribution (net − COGS)"*, `ATTR:111`) — not to the model.

So the correct locked ordering is **MER blended (headline) → Contribution Margin (profit view,
coverage-gated) → Platform ROAS (tactical, never summed)**, not
`Contribution Margin > MER > Platform ROAS`. Both docs agree; nothing in the SQL contradicts it.
The distinction matters because Tier 3.5 is gated on COGS coverage (~83%, `ATTR:111`) and on a
client sign-off that has not landed (`ATTR:116-133`) — it cannot be the headline while it is
coverage-gated.

### L4 — Contribution Margin definition, and its null-honesty
`ATTR:31` + `ATTR:111`: gross contribution = net sales − COGS; margin-after-ad-spend = gross
contribution − Windsor spend. Implemented verbatim at `RC/MARKETING_EFFICIENCY_MARGIN.sql:71-76`.
**Locked and implemented:** margin is `NULL`, never `0`, where `ORDERLINES_WITH_COGS = 0`
(`MARKETING_EFFICIENCY_MARGIN.sql:71-76`, and the view COMMENT at `:33`:
*"cost unknown => margin N/A, not 0 ... never net-sales-as-margin"*). The frontend enforces the same
rule independently — `src/lib/metrics.ts:84-93`: *"Coercing missing cogs to 0 would fabricate a 100%
margin (the Lectric CM trap)"*, and `types.ts:62-72`.

### L5 — `COGS_COVERAGE_PCT` must be surfaced, not assumed
`ATTR:111` (*"surfaced via `COGS Coverage %`"*) → `RC/MARKETING_EFFICIENCY_MARGIN.sql:70` plus
`ORDERLINES` / `ORDERLINES_WITH_COGS` as raw counts. This is `DIM:173-178`'s `row_count` idea
(ZERO vs NOT-RECORDED as a column) implemented for exactly one measure. Keep it; generalise it (M20).

### L6 — Reporting currency is USD
`ATTR:102`, Decision 3. Implemented — but by a *different mechanism* than the doc names (see S4).

### L7 — Amazon attribution window is 30-day
`ATTR:103`, Decision 4. Implemented at the fact:
`clients/GEP/snowflake/warehouse/marketing_fct_activity.sql:137-140` and `:168-171` —
`SUM(REPORT.PURCHASES30D) AS CONVERSIONS`, `SUM(REPORT.SALES30D) AS SALES_AMOUNT`,
`SUM(REPORT.UNITSSOLDCLICKS30D) AS UNITS_SOLD`.
⚠ **The window is erased by the alias.** No output column anywhere carries `30D`. This is precisely
`DIM:336-344`'s rule (*"two different facts at two different grains and must not share a column
name"*) violated at the point the decision is implemented. Recorded as MISSING M21, not STALE — the
decision is right, the labelling is absent.

### L8 — Google/Meta attribution grain is **CHANNEL**, by design
`ATTR:176-180`: *"Attribution grain = CHANNEL (Amazon vs Websites), by design ... Per-specific-
marketplace would *invent* a US/CA split Amazon never had to."* Honour this; do not be tempted to
push Google/Meta down to marketplace.

### L9 — Amazon-destination Google/Meta spend stays spend-only until Attribution lands
`ATTR:69` and `ATTR:76`: grounding it against total Amazon brand sales *"gave absurd 1500–6800x
ROAS"*. The frontend encodes the same honesty — `types.ts:92-99`: `destSpendAmazon` is *"real
Amazon-driving spend; revenue unmeasurable without Attribution tags"*, and `destSalesAmazon` is
*"undefined until the Attribution feed lands rows"*.

### L10 — Ratios are `SUM(numerator)/SUM(denominator)`, computed at the semantic layer
`DIM:150-153` (Kimball, *"store the fully additive components"*), `DIM:456-459` (*"Reject the
ratios"*), `FIELDS.md:29`, `metrics.ts:1-6`. `MARKETING_EFFICIENCY` honours it — the daily view emits
no ratio column at all (`MARKETING_EFFICIENCY.sql:8-27`). `_MONTHLY` does not (S10).

### L11 — Multi-tenancy is `ENTITY_CODE`, and cross-tenant bleed is the catastrophic failure
`ATTR:96`. Implemented on every object: `ENTITY_CODE` is column 1 of
`MARKETING_EFFICIENCY`, `_PRODUCT`, `_MONTHLY`, `_MARGIN`, `_GOOGLE_BRAND`, `_GOOGLE_PRODUCT`,
`MARKETING_MMM_INPUT`, `MARKETING_INCREMENTALITY_PRELIM`, `MARKETING_DIM_AGENCY`.
`FIELDS.md:41`: *"**Always** slice by `ENTITY_CODE` (NAVIRA vs LECTRIC)."*
⚠ The rule has one implemented exception that is *not* a design choice: `SALES_FCT_ORDERLINE` has no
`ENTITY_CODE`, so the dashboard derives it from `COMPANY_NAME <> 'Lectric eBike'`
(`warehouse.ts:79-82`, `1427-1432`). That is a string comparison standing in for a tenancy key.

### L12 — The agency dimension is dimension-sourced, never a hardcoded label
`RC/MARKETING_DIM_AGENCY.sql:10-14` (`ENTITY_CODE`, `AGENCY`, `ENTITY_ROLE` = HOUSE/AGENCY).
`types.ts:266-268`: *"Dimension-sourced so it scales as agencies are added — never a hardcoded
label."* This is the only real conformed dimension on the marketing path, and it is 3 columns wide.

### L13 — There is no canonical cross-channel marketing star; we are building one
`DIM:27-49`. *"Kimball has published nothing on digital marketing or advertising attribution"*
(`DIM:31-35`); *"we are not adopting a standard. We are building one"* (`DIM:47`). The defensible
move is Fivetran's conformed column names + Kimball structure (`DIM:47-49`, `DIM:230-240`).
Locked as *posture*: do not put *"Kimball says"* in front of a client on attribution (`DIM:375-379`).

### L14 — Pick one name for the cost column and never alias it
`DIM:71-76`: four vendor names for spend, *"Zero convergence on the most-used column in the domain.
Pick one, document it, never alias it."* The estate currently uses **three**: `COST` (the fact),
`SPEND_USD` (`MARKETING_EFFICIENCY`), `GOOGLE_SPEND_USD` (`_GOOGLE_BRAND:11`), plus
`SPEND_PLATFORM_AMOUNT`/`ACTUAL_NET_AMOUNT` in FUSION_92. Locking L14 means fixing this.

---

## 2. STALE — where the implemented SQL contradicts a wiki statement

### ⭐ S1 — "No view joins spend to actual sales" is false; the view exists and is canonical
| | |
|---|---|
| **Doc says** | `ATTR:53` — *"**Reconciliation view (spend ⨝ actual sales)** — ❌ **the real missing piece**. No view joins `MARKETING_FCT_ACTIVITY` to `SALES_FCT_*`. This is what Tiers 2–3 need built."* |
| **Code says** | `RC/MARKETING_EFFICIENCY.sql:108-152` — `COMBINED` unions ad spend (`AMZ_USD`, `GM_DAY`) with `SALES_DAY` (from `WAREHOUSE.SALES_FCT_ORDERLINE`, `:74-85`) and `LECTRIC_USD` (from `WAREHOUSE_SOURCE.SALES_FCT_LECTRIC_AMAZON_ORDERLINE`, `:86-107`) and aggregates them into one row set. |
| **Authoritative** | **The code.** The gap table at `ATTR:45-55` is a snapshot from before Phase 1 shipped and was never re-baselined; the Phase table 30 lines lower (`ATTR:109`) marks Phase 1 as prerequisite-satisfied. A design pass reading the gap table will re-specify a view that already exists. |

### ⭐ S2 — MER is written **inverted** in the attribution doc
| | |
|---|---|
| **Doc says** | `ATTR:29` — *"total spend ÷ **actual revenue**"*; `ATTR:94` — `MER = SPEND / ACTUAL_SALES` |
| **Code says** | `RC/MARKETING_EFFICIENCY_MONTHLY.sql:50` — `BLENDED_MER = ROUND(ACTUAL_SALES_GROSS_USD / NULLIF(SPEND_USD,0), 4)` |
| **Frontend says** | `FIELDS.md:38` — `MER = SUM(total_sales) / SUM(spend)`; `metrics.ts:16` and `:99` — `mer: safeDiv(sum.totalSales, sum.spend)` |
| **Authoritative** | **The code and the frontend, which agree with each other.** The doc's own formula is what `ATTR:34-38` elsewhere calls TACoS's shape. This is the headline metric (L3) written backwards in the document that locks it. |

⛔ This is the single highest-consequence STALE item. A ~5.0x MER and a ~0.2 MER are the same
business fact, and the doc and the code disagree on which one the board sees.

### S3 — "Meta dropped" vs Meta shipped
| | |
|---|---|
| **Doc says (three times, inconsistently)** | `ATTR:101` Decision 2 — *"Meta dropped (no product id + negligible spend)"*; `ATTR:113` Phase 2c — *"Deferred — connector exposes no per-product id ... **Not pursued.**"*; but `ATTR:67` — *"**`product_id` DOES return per-product rows** ... *(corrected 2026-06-09 — earlier 'no per-product id' was a field-catalog scan miss)*"*; and `ATTR:181-191` — *"C3 (Meta) UNBLOCKED ... ✅ **SHIPPED 2026-07-08**"* |
| **Code says** | Meta is a first-class branch: `MARKETING_EFFICIENCY.sql:28-36` (`META_FIRST` CTE), `:68` (`PLATFORM_ID IN ('Google Ads','Meta Facebook Ads')`), `:117/119/127-131` (`SPEND_USD_META`, `PLATFORM_ATTR_SALES_USD_META`); `_MONTHLY:11,14,21,24,57,61`; `MARKETING_MMM_INPUT.sql:11,27`; `MARKETING_INCREMENTALITY_PRELIM.sql:29-31`. The dashboard reads `MARKETING_META_SPEND_BY_DEST` (`warehouse.ts:1222-1225`). |
| **Authoritative** | **The code.** Decision 2 and Phase 2c are superseded by their own page and were never struck. A reader who stops at the Decisions block concludes Meta is out of scope. |

### S4 — Meta spend has three different values in one document
`ATTR:67` — *"$8,158 total spend"*; `ATTR:113` — *"Meta spend is negligible ($6,667)"*;
`ATTR:184` and `:190` — *"All **13** Meta campaigns ($14,668)"* / *"reconciles $14,668.24"*.
No basis, window, or as-of date is attached to any of the three. `NOT-VISIBLE` which is current — I
did not query Snowflake. **Authoritative: none of them.** Under the analysis gate, none is
publishable as written; the figure needs a stated window and a regeneration command.

### S5 — The currency mechanism the doc names is not the one the code uses
| | |
|---|---|
| **Doc says** | `ATTR:55` — *"reuse the existing consolidated-rate / FX rates mechanism"*; `ATTR:102` — *"All spend converted to USD via `CONSOLIDATED_RATE`"*; `ATTR:95` — *"preserve original-currency columns (currency-triple convention)"* |
| **Code says** | `MARKETING_EFFICIENCY.sql:37-43` builds `FX_USD` from `WAREHOUSE.SHARED_FCT_EXCHANGE_RATE` (`TO_CURRENCY_ID='USD'`, `FROM_CURRENCY_ID IN ('CAD','GBP','MXN','BRL')`, `EXCHANGE_DATE BETWEEN '2024-01-01' AND CURRENT_DATE()`), applied at `:56-62` as `COST_LOCAL * COALESCE(FX.RATE, 1)`. `CONSOLIDATED_RATE` appears **nowhere** in any `report_common/MARKETING_*.sql`. |
| **Authoritative** | **The code.** `CONSOLIDATED_RATE` is the *sales*-side mechanism (already baked into `SALES_GROSS_CONSOLIDATED`); spend uses a different one. Two mechanisms, one doc sentence. |

Two consequences the doc does not record: (a) `COALESCE(FX.RATE, 1)` **silently treats a missing
rate as parity** — a missing GBP rate makes £1 = $1 with no signal, which is exactly the
`NOT-RECORDED`-rendering-as-a-number failure the analysis gate forbids; (b) the currency-triple the
doc promises at `ATTR:95` is **not delivered** — see M19.

### S6 — The proposed spine grain and column names do not match what shipped
| | |
|---|---|
| **Doc says** | `ATTR:93-94` — *"**Spine grain:** `ENTITY_CODE × MARKETPLACE × ACTIVITY_DATE`"*, columns `SPEND_CONSOLIDATED`, `PLATFORM_ATTRIBUTED_VALUE`, `ACTUAL_SALES_CONSOLIDATED`, `BLENDED_ROAS`, `MER` |
| **Code says** | Grain is `ENTITY_CODE × MARKETPLACE_NAME × ACTIVITY_DATE × **PLATFORM**` — `MARKETING_EFFICIENCY.sql:147-152` (`GROUP BY 1,2,3,4`), the 4th key added by GP-318 A3 (`:110`, `:124`). **None of the five proposed column names exist.** Actual: `SPEND_USD`, `PLATFORM_ATTR_SALES_USD_{AMAZON,GOOGLE,META}`, `ACTUAL_SALES_GROSS_USD`/`_NET_USD`. `BLENDED_ROAS` and `MER` are not columns on any object; `BLENDED_MER` exists only on `_MONTHLY:17`. |
| **Authoritative** | **The code.** ⛔ A design that reuses the doc's names ships a wrong-object-name spec — the specific failure this mission was warned about. |

The grain change has a documented cost: `MARKETING_EFFICIENCY_MARGIN.sql:39-45` has to
*re-aggregate the platform grain away* before the COGS join, *"Without this the join fans out ~2x and
duplicates COGS"* — and the view COMMENT (`:33`) states *"This view intentionally carries NO
platform"*. So the estate now has two sibling objects at two grains and margin is unavailable at the
platform grain by construction.

### S7 — "Both capped and uncapped are built" — only capped exists in the warehouse
| | |
|---|---|
| **Doc says** | `ATTR:257-262` — *"**Both are now built in the Sandbox model**"*; capped lives in *"warehouse `MARKETING_EFFICIENCY_MONTHLY`"*, uncapped is *"the Sandbox measure"*; *"**Recommendation:** default the dashboard to **uncapped**"* |
| **Code says** | `RC/MARKETING_EFFICIENCY_MONTHLY.sql:52-54` — `LEAST(1, ...)` only. There is **no uncapped column** on any `report_common` object. The frontend consumes `calibratedRoasAmazon/Google/Meta` (`types.ts:305-307`) — i.e. the **capped** values — so the dashboard is currently rendering the option the doc recommends *against*. |
| **Authoritative** | **The code** for what exists. The recommendation is unimplemented and the client decision at `ATTR:262` is still open. |

### S8 — "Only 3 ingested channels" is right; "7 branches" is not the shape of the fact any more
`ATTR:49` describes `MARKETING_FCT_ACTIVITY` as *"7 branches, grain
`PLATFORM·CAMPAIGN·AD_GROUP·PROFILE·PRODUCT_ID·DATE·MARKETPLACE·ENTITY_CODE`"*. The object the
consumer layer actually reads is `WAREHOUSE.MARKETING_FCT_ACTIVITY_UNIFIED`
(`warehouse.ts:1497`, `:1588`, `:1627`, `:622`), which **has no repo DDL at all** (§3, M18) — I can
see the name and its columns-in-use (`ENTITY_CODE, CAMPAIGN_ID, PLATFORM_ID, PRODUCT_ID,
MARKETPLACE_NAME, ACTIVITY_DATE, COST, SALES_AMOUNT, CONVERSIONS, CLICKS, IMPRESSIONS`) but
`NOT-VISIBLE` as a definition. The 8-part grain claim cannot be verified from the repo.

### S9 — `SHARED_DIM_PRODUCT_BASE` is called "the keystone for Tier 3" — the consumer does not use it
| | |
|---|---|
| **Doc says** | `ATTR:51` — *"`SHARED_DIM_PRODUCT_BASE` maps `PRODUCT.ID` ↔ `ASIN` ... **This is the keystone for Tier 3** — and it **already exists**"* |
| **Code says** | The *warehouse* view uses it (`MARKETING_EFFICIENCY_PRODUCT.sql:29-40`). The **frontend does not**: `warehouse.ts:1303-1343` builds its own `asin2vendor` and `sku2asin` crosswalks from `TRAFFIC_FCT_ACTIVITY`, with the comment *"a direct `dm.PRODUCT_ID = p.ASIN` join is ASIN-vs-SKU and matches almost nothing — the OLD code silently COALESCE'd to `p.BRAND`, splitting products into a DIFFERENT vocabulary ... leaving ~27% of cards with an empty Top-products section + a dead drill-down (verified 2026-07-14)"*. |
| **Authoritative** | **The code.** The keystone exists but does not span the keyspace the consumer needs; the working bridge is an ad-hoc CTE over a *traffic* fact, rebuilt on every request. |

### S10 — `DIM`'s "no stored ratio columns" is violated by two shipped objects
`DIM:150-153`: *"⛔ **No `ctr`, `cpc`, `cpm`, `cpa`, `roas` columns.**"*
Violated by `MARKETING_EFFICIENCY_MONTHLY.sql:50` (`BLENDED_MER`), `:52` (`ATTR_CALIBRATION_FACTOR`),
`:55-57` (`CALIBRATED_SALES_USD_*`), `:59-61` (`CALIBRATED_ROAS_*`); and by
`MARKETING_INCREMENTALITY_PRELIM.sql:37-38` (`ELASTICITY_ESTIMATE`, `R_SQUARED`).
**Authoritative: the code, with a caveat.** These sit on a *monthly aggregate* view, not the atomic
fact, and the calibration factor is genuinely non-decomposable — so this is a defensible deviation,
but it is an undocumented one. It must be stated as a deviation, not left as a silent contradiction,
or the rule erodes.

### S11 — The build reference the docs point at is outside both repos
`ATTR:264` points teams at `aldc-launchpad/pbi_ops/navira_marketing_data_dictionary.md` as *"the
elite grounding doc"*, and `ATTR:71-77`, `:110-112`, `:188`, `:212-213` cite ~10 more
`aldc-launchpad/` scripts as the evidence for shipped work. **`NOT-VISIBLE` — `aldc-launchpad` was
not in my read scope.** Flagging it because the load-bearing evidence for Phases 2a/2b/C1/C3 lives
in a third repo that neither `clients` nor `navira-marketing-dashboard` can see, and the objects
those scripts created (`MARKETING_GOOGLE_*`, `MARKETING_*_BY_DEST`, `MARKETING_ATTRIBUTED_*`) have
**no repo-managed DDL anywhere in `clients/GEP`** (M18).

---

## 3. MISSING — what the frontend field contract needs that no implemented object provides

This is the section that matters. Method: `types.ts` (`MetricInput` + `Brand`/`Product`/`Campaign`/
`Platform`/`Region`) and `FIELDS.md` are the contract; `warehouse.ts` is where the contract meets the
warehouse. **Anywhere `warehouse.ts` hardcodes a value, invents a crosswalk, or hides a column, the
model failed to supply something.** Every one below is a specific column name.

### ⭐⭐ The three most consequential

**M1 — `MARKETING_EFFICIENCY` has no `CLICKS` and no `IMPRESSIONS`. Two contracted metrics
cannot be computed from the headline object.**
`FIELDS.md:36-37` contracts `CTR = SUM(clicks)/SUM(impressions)` and `Avg CPC = SUM(spend)/SUM(clicks)`.
`metrics.ts:97-98` computes both. But `MARKETING_EFFICIENCY.sql:8-27` — the full output column list —
contains neither. Measured: `grep -l 'CLICKS' report_common/MARKETING_*.sql` returns
**`MARKETING_EFFICIENCY_PRODUCT.sql` only**, and that only since GP-318 1(a)
(`MARKETING_EFFICIENCY_PRODUCT.sql:63-64,141-144`).
Consequence: the dashboard must open a **second, unreconciled query against the raw fact** to get
reach — `warehouse.ts:610-624` (`act` CTE over `MARKETING_FCT_ACTIVITY_UNIFIED`), then LEFT JOIN it
back onto the efficiency rows at `:641-645`. Spend and reach for the same (platform, region, day)
therefore come from two objects with two date floors and no reconciliation test between them.
**Needed columns on the spine: `CLICKS`, `IMPRESSIONS`, `CONVERSIONS` (M2).**

**M2 — No `CONVERSIONS` on any `REPORT_COMMON` object.**
`MetricInput.conversions` (`types.ts:56-61`) — *"only the campaign fact populates it today;
brand/product/platform rows omit it (treated as 0)"*. `Region.conversions` (`types.ts:277-278`) is a
required field. The column exists only on `MARKETING_FCT_ACTIVITY_UNIFIED` (read at
`warehouse.ts:620`, `:1610`). So a conversion count and the spend it came from live on different
objects, and the brand/product/platform views silently carry `0` — a fabricated zero for a metric
that is simply not on the object.

**M3 — No campaign-grain USD spend. An entire dashboard view is disabled because of it.**
`warehouse.ts:1555-1559`, verbatim:
> *"⚠ COST currency: reconciled vs `MARKETING_EFFICIENCY.SPEND_USD_*` — Amazon ≈ USD (within ~1%),
> Meta == USD exactly, but **Google COST runs ~13% high** (local currency / FX...). So COST is NOT
> trustworthy blended USD spend; **the Campaign view hides spend/Ad Sales/ROAS by default in
> warehouse mode**"*

and `mapCampaigns` (`warehouse.ts:1005-1010`): *"COST + SALES_AMOUNT are NATIVE currency (Amazon
US/Meta = USD; Amazon CA/Google = local, **no `CURRENCY_CODE` column yet**)"*.
`MARKETING_FCT_ACTIVITY_UNIFIED` carries `COST` with **no currency column and no USD sibling**. The
FX consolidation exists only *inside* `MARKETING_EFFICIENCY`, at a grain (marketplace × day) that has
already destroyed the campaign key.
**Needed: `SPEND_USD` + `CURRENCY_CODE` + `COST_LOCAL` at campaign grain** — the currency triple
`ATTR:95` promised. Until then the Campaign lens ships with its money columns switched off.

### Campaign entity — 4 more

| # | Contract field | Contract cite | What the warehouse provides | Where it is faked |
|---|---|---|---|---|
| M4 | `dailyBudget` | `types.ts:195`, `FIELDS.md:104` ("current") | nothing | `warehouse.ts:1032` — `dailyBudget: 0` |
| M5 | `budgetUsedPct` | `types.ts:197`, `FIELDS.md:105` | nothing (no spend-vs-budget pacing object) | `warehouse.ts:1033` — `budgetUsedPct: 0` |
| M6 | `timeInBudgetPct` | `types.ts:198`, `FIELDS.md:106` | nothing | `warehouse.ts:1034` — `timeInBudgetPct: 0` |
| M7 | `status` (`active`/`paused`/`archived`) | `types.ts:196`, `FIELDS.md:103` | only `CAMPAIGN_STATE` on `MARKETING_DIM_CAMPAIGN_ATTRS` (no repo DDL, M18) | `warehouse.ts:1031` — `status: "active"` **for every campaign** |

`MARKETING_DIM_CAMPAIGN_ATTRS.BUDGET_AMOUNT` (`warehouse.ts:1626`, surfaced as
`campaignBudgetAmount`) is a *native-currency campaign budget*, not a daily budget and not a
utilisation. M4–M6 need a pacing measure: `BUDGET_DAILY_USD`, `SPEND_USD`, and a same-day
`TIME_IN_BUDGET_PCT` at campaign×day grain.

**M8 — No campaign type / ad-product column, and no parse-status column.**
`Campaign.type` (`types.ts:192`) is derived by **splitting the campaign name on whitespace/underscore/
hyphen and matching SP/SB/SBV/SD tokens** — `warehouse.ts:988-1001`, with `:977-987` recording
*"`MARKETING_DIM_CAMPAIGN` has NO type column (probed 2026-07-16: cols = `CAMPAIGN_ID`,
`CAMPAIGN_KEY`, `CAMPAIGN_NAME`) ... Live coverage: 97.2% classify ... the 2.8% legacy agency schemes
(OW_/OP_/BR_…) plus ALL Google/Meta return null"*.
This is exactly the hazard `DIM:403-407` names: *"Positional `SPLIT_PART` on agency-authored names
shifts every field by one when a delimiter is missing — **and the row still parses**. Carry a
`taxonomy_parse_status` column (`PARSED | MALFORMED | LEGACY | UNPARSED`)."*
Measured: `taxonomy_parse` / `parse_status` appear **nowhere** in `clients/GEP/**/*.sql`.
**Needed: `AD_PRODUCT` on the campaign dim, plus `TAXONOMY_PARSE_STATUS`.**

### Brand entity — 4

**M9 — There is no marketing brand/vendor dimension. Brand is derived from a *marketplace* dim.**
The dashboard resolves brand as `SHARED_DIM_MARKETPLACE.DEFAULT_VENDOR`, deduped —
`warehouse.ts:1453-1459`, `:1322-1323`, `:1589-1591`. `SHARED_DIM_MARKETPLACE` is product×marketplace
grain (`warehouse.ts:73-76`). Meanwhile `MARKETING_EFFICIENCY_PRODUCT.BRAND` exists
(`MARKETING_EFFICIENCY_PRODUCT.sql:10,36,132-133`) but is sourced from
`SHARED_DIM_PRODUCT_BASE.BRAND` — **a different vocabulary**, and the code says so at
`warehouse.ts:1396-1399`: the old `MARKETING_EFFICIENCY_PRODUCT.BRAND` aggregation *"silently dropped
~31% of Amazon ad spend — including the #1 spender TF Publishing"*.
**Needed: one conformed `MARKETING_DIM_BRAND` (`BRAND_KEY`, `BRAND_NAME`, `ENTITY_CODE`) that both
the spend side and the sales side join to.** Two brand vocabularies is the defect; a third derived in
TypeScript is the symptom.

| # | Contract field | Cite | Provided? | Faked at |
|---|---|---|---|---|
| M10 | `Brand.storefrontUrl` | `types.ts:112`, `FIELDS.md:69` ("current") | no | `warehouse.ts:942` — `storefrontUrl: ""` |
| M11 | `Brand.platformCount` | `types.ts:115`, `FIELDS.md:72` | no | `warehouse.ts:967` — `spend > 0 ? 1 : 0` (a boolean wearing a count) |
| M12 | `smartScout.{marketShare,searchRank,buyBoxPct,weightedRating,reviewCount}` | `FIELDS.md:73-77`, all marked **"current"** | **no SmartScout object exists in Snowflake at all** | not in `types.ts` any more — the fields were dropped from the warehouse `Brand` shape entirely |

M12 is a contract/implementation divergence in the *contract document*: `FIELDS.md` lists five
SmartScout fields as "current" and `types.ts:108-118` no longer has a `smartScout` member. `FIELDS.md`
is dated 2026-06-06 and self-describes as transcribed from `types.ts` (`FIELDS.md:12-14`) — it has
since drifted from it.

### Product entity — 5

| # | Contract field | Cite | Provided? | Evidence |
|---|---|---|---|---|
| M13 | `Product.sku` | `types.ts:154`, `FIELDS.md:89` ("current", column label "SKU") | **no** — `MARKETING_EFFICIENCY_PRODUCT` is ASIN-keyed only (`:5-17`) | `warehouse.ts:867` — `sku: resolved ? asin : ""` — **the SKU column renders the ASIN** |
| M14 | `Product.rating`, `reviewCount` | `FIELDS.md:90-91` ("current") | no source | dropped from `types.ts:148-160` |
| M15 | `Product.onPromo` | `FIELDS.md:92` | no source | dropped from `types.ts` |
| M16 | `Product.launchDate` | `FIELDS.md:93` | no source | dropped from `types.ts` |
| M17 | product-grain `ORDERS` | `MetricInput.orders`, `types.ts:50` | **no** — `MARKETING_EFFICIENCY_PRODUCT.sql:5-17` has `ACTUAL_UNITS` but no `ORDERS`, unlike `MARKETING_EFFICIENCY.sql:26` | `warehouse.ts:885` — `orders: 0` on every product row |

**M13a — the SKU↔ASIN bridge itself is missing and is rebuilt per-request in the app.**
`warehouse.ts:1329-1343` (`sku2asin`) and `:1303-1327` (`asin2vendor`) are window-function CTEs over
`TRAFFIC_FCT_ACTIVITY` picking a dominant `CHILD_ASIN` per `PRODUCT_ID`. `types.ts:120-131` records
the coverage probe (*"98.9% of ad spend / 94.4% of edges / 97.7% of campaigns"*). This bridge is
load-bearing for the Product view, the Campaign↔Product edges, and the brand vocabulary — and it is
**not a warehouse object**. If the traffic fact's coverage shifts, three views move and nothing
tests it.

### Cross-channel / grounding — 3 objects with no repo DDL

**M18 — ⭐ Ten objects the marketing path depends on have no repo-managed definition.**
Measured (`grep -rl "CREATE OR REPLACE.*<name>" clients/GEP --include=*.sql`, then a bare-name
sweep):

| Object | Read by | Repo DDL |
|---|---|---|
| `MARKETING_FCT_ACTIVITY_UNIFIED` | `warehouse.ts:1497,1588,1627,622`; `MARKETING_EFFICIENCY.sql:34` | ❌ referenced only |
| `MARKETING_FCT_ACTIVITY_PREPROD` | `MARKETING_EFFICIENCY.sql:51,67`; `_PRODUCT.sql:72`; `_GOOGLE_BRAND.sql:20` | ❌ referenced only |
| `MARKETING_DIM_CAMPAIGN_ATTRS` | `warehouse.ts:71-72,1634` | ❌ **no mention anywhere in `clients/GEP`** |
| `MARKETING_GOOGLE_SPEND_BY_DEST` | `warehouse.ts:1218` | ❌ no mention |
| `MARKETING_META_SPEND_BY_DEST` | `warehouse.ts:1224` | ❌ no mention |
| `MARKETING_ATTRIBUTED_SALES_BY_DEST` | `warehouse.ts:1246` | ❌ no mention |
| `MARKETING_ATTRIBUTED_ROAS_BY_BRAND` | `warehouse.ts:1273` | ❌ no mention |
| `MARKETING_GOOGLE_CAMPAIGN_BRAND` | `_GOOGLE_BRAND.sql:32` | ❌ referenced only |
| `MARKETING_GOOGLE_PRODUCT_SPEND` | `_GOOGLE_PRODUCT.sql:17` | ❌ referenced only |
| `MARKETING_GOOGLE_OFFER_SKU` | `_GOOGLE_PRODUCT.sql:23` | ❌ referenced only |

Five of these are read **unqualified** by the dashboard (`warehouse.ts:1218,1224,1246,1273,1497`),
i.e. they resolve in `WAREHOUSE_TEST_GP226` — the very schema the GP-318 note at `warehouse.ts:88-102`
identifies as *"a second, divergent copy"*. So the estate's newest cross-channel features
(destination spend, Amazon Attribution, per-brand attributed ROAS) sit entirely on objects that are
(a) undefined in source control and (b) in the schema known to diverge from the canonical one.
The columns they must supply, from the queries that read them:
- `MARKETING_GOOGLE_SPEND_BY_DEST`: `ENTITY_CODE, ACTIVITY_DATE, DEST_CHANNEL, SPEND_USD_GOOGLE`
- `MARKETING_META_SPEND_BY_DEST`: `ENTITY_CODE, ACTIVITY_DATE, DEST_CHANNEL, SPEND_USD_META`
- `MARKETING_ATTRIBUTED_SALES_BY_DEST`: `ENTITY_CODE, ACTIVITY_DATE, CHANNEL_TAG, ATTRIBUTED_SALES_USD_14D`
- `MARKETING_ATTRIBUTED_ROAS_BY_BRAND`: `BRAND, ACTIVITY_DATE, CHANNEL_TAG, ATTRIBUTED_SALES_USD_14D, GOOGLE_AMAZON_SPEND_USD`

### Structural columns the `DIM` doc recommends and nothing implements — 5

Measured: `grep -rliE 'grain_level|data_origin|row_count|metric_basis|taxonomy_parse'` over
`clients/GEP/**/*.sql` returns **zero files**.

| # | Column | `DIM` cite | Why it matters here |
|---|---|---|---|
| M19 | `SPEND_LOCAL` + `CURRENCY_CODE` on the output (the currency triple) | `DIM:313-328`, `ATTR:95` | `CURRENCY_CODE` exists only inside CTEs (`MARKETING_EFFICIENCY.sql:38,48,59-60,91,103-105`) and is **never emitted**. Every view outputs `*_USD` only, with `COALESCE(RATE,1)` (S5). A consumer cannot tell a converted number from an unconverted one. |
| M20 | `ROW_COUNT` (raw rows processed) | `DIM:173-178` | The estate has this for exactly one measure (`ORDERLINES`/`ORDERLINES_WITH_COGS`, L5) and nowhere else. Without it, `MARKETING_EFFICIENCY`'s `SPEND_USD_GOOGLE = 0` on every Amazon row (`MARKETING_EFFICIENCY.sql:116`) is indistinguishable from a real zero. |
| M21 | `METRIC_BASIS` / window-bearing names | `DIM:147`, `DIM:336-344` | L7: the 30-day window is aliased away at `marketing_fct_activity.sql:137-140`. `SALES_AMOUNT` is a 30-day click-dated modelled figure named as if it were a measurement. |
| M22 | `DATA_ORIGIN_KEY` | `DIM:160-172` | `MARKETING_EFFICIENCY.sql:50-51` unions `MARKETING_FCT_ACTIVITY` with `MARKETING_FCT_ACTIVITY_PREPROD` **filtered by a hardcoded `PLATFORM_ID IN (...)` literal list**. Add a platform to both sources and the union double-counts silently, with no column that makes it detectable. |
| M23 | `GRAIN_LEVEL` | `DIM:136-137`, `DIM:155-159` | `MARKETING_EFFICIENCY_PRODUCT.sql:48-52` COALESCEs an unresolved product key to the string `'(UNRESOLVED)'` and `:78` excludes `PRODUCT_ID = '-1'` — i.e. campaign-level rows are dropped, not labelled. `warehouse.ts:1407-1409` calls the residual *"the honest ~9% spend residual"*. A `GRAIN_LEVEL` column would make it a first-class member instead of an exclusion. |

### One more, structural

**M24 — Channel has no axis of its own; Google/Meta are jammed into the marketplace column.**
`MARKETING_EFFICIENCY.sql:65` — `'Cross-Channel' AS MARKETPLACE_NAME` for every Google/Meta row.
`warehouse.ts:601,606,615-616` mirrors it as `'Cross-channel'` (note: **different casing** —
`Cross-Channel` in SQL, `Cross-channel` in the app; the app never joins the two so it does not break,
but it is two spellings of one member). The consequence is recorded in
`wiki/concepts/architecture/navira-daily-model-lineage.md:215-224`: the relabel creates a member that
is *"not a member of `SHARED_DIM_MARKETPLACE`"*, orphaning **768 rows / $244,870.44** onto PBI's
unknown member, unselectable by any positive slicer choice — and *"**Channel must leave the
marketplace axis**"*. The frontend field contract already wants this separated: `Region` carries
`platform` and `name` as two fields (`types.ts:270-273`). **Needed: `DESTINATION_CHANNEL` (or
`CHANNEL_KEY`) as its own column on the spine, with `MARKETPLACE_NAME` left NULL/`N/A` for
non-marketplace-tagged spend.**

---

## 4. PRIOR ART TO REUSE — FUSION_92's working cross-channel star

`FUSION_92/snowflake/warehouse_utility/fct_platform_spend.sql` unions **10 direct-platform branches**
(measured: `grep -c 'INNER JOIN FLIGHT_PLATFORM_IDS'` = 10) — Meta, Google Ads (pre-merged with
Google Search Ads in `COMBINED_GOOGLE_ADS_AND_SEARCH_ADS`, `:245-248`), CM360, DV360, LinkedIn,
Microsoft Ads, Viant, Advantage360, Trade Desk, Amazon DSP — plus a manual-entry branch in
`fct_daily_spend.sql:174-212`. Navira ingests three. Six patterns worth carrying, one to reject.

### P1 — ⭐ Source precedence enforced by an anti-join, not by a hardcoded platform list
`fct_daily_spend.sql:204-212`:
```sql
FROM WAREHOUSE_UTILITY.FCT_MANUAL_SPEND AS MANUAL_SPEND
WHERE NOT EXISTS (
    SELECT 1 FROM MARKED_PLATFORM_SPEND
    WHERE MARKED_PLATFORM_SPEND.FLIGHT_ID = MANUAL_SPEND.FLIGHT_ID
)
```
with the reasoning stated at `:4-8` — *"in order to make sure that no manual data comes through when
there is direct data we **only allow one source per flight**"*, and `:204-207` recording that the
*previous* date-window approach let both through.
**Carry across to:** `MARKETING_EFFICIENCY.sql:50-51`, where the same problem is solved by
`WHERE PLATFORM_ID IN ('Amazon Ads Sponsored Products','Amazon Ads Sponsored Display')` — a
hand-maintained literal that must be edited whenever a feed moves between the base fact and
`_PREPROD`, and which fails **silently and doubly** if it drifts. An anti-join on the natural key
cannot drift. This is M22's control, already shipping in the estate.

### P2 — ⭐ Fan-out is detected, split, and then *disclosed on the row*
`fct_daily_spend.sql:42-71` builds `DUPLICATE_PLATFORM_SPEND` (group by the platform key tuple,
`HAVING COUNT(DISTINCT FLIGHT_KEY) > 1`) → `MARKED_PLATFORM_SPEND` attaches `FLIGHT_COUNT` and
`ALL_FLIGHT_IDS` → `:148-165` divides **every** metric by `FLIGHT_COUNT` → `:135-136` emits
`ALL_FLIGHT_IDS` and `FLIGHT_COUNT` **as output columns**.
That last step is the important one: a consumer can see that a row was split and by how much. It is
`DIM:160-172`'s `data_origin_key` argument — *"makes the breakdown hazard detectable rather than
merely avoided by convention"* — in the estate today. The honest caveat is on the row too
(`:12-15`: *"At the flight level, split flights will not match the expected amounts"*).
**Carry across as:** `SPLIT_FACTOR` + `SPLIT_ACROSS_KEYS` on any Navira object that allocates one
platform row across several business keys — which is exactly what a destination-channel or
brand-grounding allocation does.

### P3 — A conformed platform key built by convention, and a dim that pre-declares every member
`shared_dim_flight.sql:292-293` — `PLATFORM_ID = COALESCE(ORIGIN,'Unknown') || '-' ||
COALESCE(PLATFORM,'Unknown')`, `PLATFORM_KEY = SHA2(PLATFORM_ID)`.
`shared_dim_platform.sql:54-64` — the dim is the **full origin × platform cross-product**
(`FULL OUTER JOIN ... ON TRUE`), so *"a combination ... that would not exist if we just pull platform
IDs from dim flight"* still has a member. `:43` seeds an explicit `'Unknown'` member.
**Carry across:** Navira has **no platform dimension on the marketing path**. `PLATFORM` is a CASE
expression inside the view (`MARKETING_EFFICIENCY.sql:110`, `:124`), and `NULL` for sales-only rows
(`:136`, `:142`). Pre-declaring members is also the fix for M24's orphan and for `DIM:274-276`'s
special-member rule (`0` Missing / `-1` Unknown / `-2` N/A) — FUSION_92 does the `Unknown` half
already.

### P4 — Supertype/subtype, shipped
Every branch of `fct_platform_spend.sql` emits the **identical** column list and explicitly `NULL`s
what the platform cannot supply: Meta `NULL AS CONVERSIONS` (`:175`), Microsoft `NULL AS REACH` and
all five video columns (`:497-504`), Amazon DSP `NULL AS REACH/CONVERSIONS` (`:781-782`). The
Google-only impression-share family (`ELIGIBLE_IMPRESSIONS`, `RANK_LOST_IMPRESSIONS`,
`BUDGET_LOST_IMPRESSIONS`, `TOP_IMPRESSIONS`, `ABSOLUTE_TOP_IMPRESSIONS`) is `NULL` on all nine other
branches (`:183-187`, `:379-383`, …) and real only at `:235-243`.
This is `DIM:257-276` — Kimball's supertype/subtype — as a shipped artefact, and it is the answer to
M1/M2: the intersection (`spend, clicks, impressions, conversions, conv_value`) goes on the spine and
the platform-specific tail is `NULL`, never absent.

### P5 — ⭐ Reconstruct the additive denominator instead of storing the ratio
`fct_platform_spend.sql:230-243`:
```sql
-- When impression share is below 0.1 all values are shown as 0.09999 ... the total lost share
-- (rank_lost + budget_lost) represents the opposite proportion of search_impression_share
IFF(GOOGLE_ADS.SEARCH_IMPRESSION_SHARE < 0.1,
    DIV0(IMPRESSIONS, 1 - SEARCH_RANK_LOST_IMPRESSION_SHARE - SEARCH_BUDGET_LOST_IMPRESSION_SHARE),
    DIV0(IMPRESSIONS, SEARCH_IMPRESSION_SHARE)) AS ELIGIBLE_IMPRESSIONS,
```
It turns a non-additive vendor ratio into an additive count, documents the vendor's `0.09999`
sentinel, and picks the more accurate of two reconstructions.
**Carry across directly.** Navira's `MARKETING_FCT_PLATFORM_DETAIL` stores the ratios raw, and
`types.ts:365-377` admits the cost: *"The impression-share/ROAS ratios and `META_REACH` have no safe
SUM/SUM path at this grain ... so summing or averaging them across days would silently misrepresent
them (a Flag-A-style error)"* — so the whole `PlatformDetail` feed is served at day grain and cannot
be rolled up. FUSION_92 already solved this exact problem on the same Google fields.

### P6 — A money ladder of named columns with documented fallbacks and a guarded divisor
`fct_daily_spend.sql:102-119`: `SPEND_PLATFORM_AMOUNT` → `ACTUAL_NET_AMOUNT` → `ACTUAL_GROSS_AMOUNT`
→ `ACTUAL_GM`, each `COALESCE`ing the platform's own value ahead of a computed one, with
`GREATEST(0.0001, (1 - (COMMISSION + DAX_TECH)))` guarding the divisor (`:115-117`) and the
dependency order stated at `fct_platform_spend.sql:121-125` (*"from platform down to gm each depends
on the one above it"*).
**Carry across to** the Navira margin ladder (`MARKETING_EFFICIENCY_MARGIN.sql:71-77`), which has the
same shape (`ACTUAL_SALES_NET_USD` → `CONTRIBUTION_MARGIN_USD` → `MARGIN_AFTER_AD_SPEND_USD` →
`ACTUAL_MARGIN_NET_LOADED_USD`) but states the dependency order only in the view COMMENT.

### P7 — Multi-source dimension conflation with explicit precedence and a carved-out exception
`shared_dim_flight.sql:17-21` and `:117-121` state the precedence (Dax > Smartsheet > legacy) *and*
its one exception in prose before the SQL: *"If there is any data for a flight from Dax flight check
all fields are kept from the app. EXCEPT for the platform IDs"* → `:163-166`
`IFF(HAS_PLATFORM_IDS, DAX.PLATFORM_ACCOUNT_ID, SMARTSHEET.PLATFORM_AD_ACCOUNT_ID)`, with
`HAS_PLATFORM_IDS` defined once at `:28-33`. Non-Dax rows enter via `NOT EXISTS` (`:262-267`).
**Carry across:** Navira's equivalent conflation (base fact vs `_PREPROD`) has no such statement and
no such guard — see P1.

### P8 — ⛔ What NOT to carry across: FUSION_92's currency handling
`fct_daily_spend.sql:121` and `fct_spend.sql:35,56,104,143,182` carry `ACCOUNT_CURRENCY` on every
spend row; `fct_platform_spend.sql:132` defaults it (`COALESCE(ACCOUNT_CURRENCY,'USD')`) and three
branches set it `NULL` outright (`:274` — *"NOTE currency fields caused an issue in Windsor"*, `:366`,
`:627`, `:697`). **No exchange-rate join exists in either fact** — grep for `exchange|_usd|rate` over
`warehouse/fct_daily_spend.sql`, `fct_spend.sql`, `shared_dim_currency.sql` returns only
`ACCOUNT_CURRENCY` passthroughs and the currency *dimension* (`shared_dim_currency.sql`, which holds
`CURRENCY_ID`/`CURRENCY_NAME` and **no rate**).
So FUSION_92 sums spend across currencies — the exact hole `DIM:238-240` identifies in Fivetran
(*"the most-deployed public ad model sums spend across currencies"*). Navira already does better
(`MARKETING_EFFICIENCY.sql:37-43`). **Take P1–P7; leave P8.**

---

## Method note

Everything above is from files. I did not connect to Snowflake, used no credential, and wrote no
file outside this one. Where a claim rests on a count, the command that produced it is stated inline.
Object names were taken from `CREATE OR REPLACE` headers and from the SQL string literals in
`warehouse.ts` — never from a wiki page, because five of the wiki's object names (S6) do not exist.

**Files read in full:** the two wiki docs; `navira-daily-model-lineage.md`; all nine
`clients/GEP/snowflake/report_common/MARKETING_*.sql`; `FUSION_92/.../fct_daily_spend.sql`,
`shared_dim_flight.sql`, `fct_platform_spend.sql`, `shared_dim_platform.sql`;
`navira-marketing-dashboard/docs/FIELDS.md`, `src/lib/metrics.ts`, `src/lib/data/types.ts`,
`src/lib/data/get-provider.ts`, `.env.example`; and `src/lib/data/providers/warehouse.ts`
lines 1-130, 565-684, 854-1054, 1143-1682 (of 2300).

**`NOT-VISIBLE`:** the `aldc-launchpad` repo (S11); live Snowflake row counts and current spend
figures (S4); the DDL of the ten objects in M18.
