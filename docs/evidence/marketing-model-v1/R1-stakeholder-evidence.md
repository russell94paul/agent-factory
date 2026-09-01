# R1 — Stakeholder evidence: what the client actually asked for on the Navira marketing model

**Worker:** R1 · **Mission:** `marketing-model-reconstruction-v1` · **Task:** `fbe2ea4c`
**Resource claim:** `res-gep-evidence`, READ ONLY. Nothing outside this file was written.
**Compiled:** 2026-08-31 · **Subject:** Navira (the modelled entity). GEP is the Jira project / contracting client.

---

## 0. Read this first — three framing facts that change how the ledger below should be used

**0.1 — The single most load-bearing thing I found is a negative.** GP-319 records that the
Daily-vs-Marketing metric boundary rests on *"a recollection of Heather's ask"* and that the
implementing script's own docstring says *"confirm against the Avoma transcript before this reaches
Heather"* — marked **Not done** (`wiki/tickets/gep/GP-319.md:183-184`). **I read that transcript.**
It is at `aldc-launchpad/boot-prompts/navira_data_model_review_meeting_lori_heather.md` (487 lines,
verbatim Lori Beck ↔ Heather Tabor). **It contains no ask to hide engagement metrics, and no
"high-level vs low-level" framing anywhere.** It contains a *different* ask, verbatim, which is
claim C-1 below. The confirmation that was owed can now be discharged: **the recollection is not
supported by the transcript.** See CONTRADICTION 1.

**0.2 — Most of the "design" in the record is ours, not theirs.** The tiered measurement model
(Tiers 0–4), blended MER as the headline, the core-10, the conformed-core-plus-extensions shape, the
three candidate designs, and the Kimball framing are **all ALDC-authored**. The client's own asks are
narrower and more concrete than the architecture built around them. Where a wiki page says
"DECIDED 2026-05-29 (Paul)", that is an ALDC decision on the client's behalf, not a client
requirement — and the pages are honest about this. I have marked every claim with **who said it**.

**0.3 — Jira itself is NOT-VISIBLE to me.** Every claim whose only citation is a Jira comment number
reaches me second-hand through a wiki page or boot prompt. Jira comments `36055 36056 36073 36082`
(GP-319), `35978–35990` and `36066 36067` (GP-318), the GP-319 description, and **Heather's emails of
2026-08-06 and 2026-08-10** are all cited in the record and **none of them are in any repo I can
read**. Ten referenced tickets have no wiki page at all (§ NOT-VISIBLE inventory). A claim resting
only on those is capped at `SUPPORTED`, never `CONFIRMED`.

---

## 1. Claim ledger

Basis vocabulary: `CONFIRMED` = client's own words or a contemporaneous minute of the client saying it ·
`SUPPORTED` = one internal record quotes/paraphrases the client, no primary artefact readable ·
`INFERRED` = we derived it from client-supplied data, client never said it ·
`ASSUMPTION` = no citable source · `UNKNOWN` = the evidence does not settle it.

### A. Asks in the client's own voice (transcript — the strongest evidence on file)

Source for all of A: `aldc-launchpad/boot-prompts/navira_data_model_review_meeting_lori_heather.md`.
Speaker **Heather Tabor** is Navira/GEP's COO (`wiki/entities/clients/active/GEP.md:155`). Lori Beck
is ALDC-side. **Date: 2026-07-08** per `wiki/concepts/architecture/cross-channel-marketing-attribution.md:135`
and the file's own mtime — see CONTRADICTION 2 for a competing date.

| # | Claim | Basis | Source | Expressed | Superseded? |
|---|---|---|---|---|---|
| **C-1** | **Do not change the Daily Data Model the team uses every day.** Verbatim: *"we do not wanna, like, change the functionality of that data model… otherwise, we gotta retrain everybody"* and *"I don't wanna approve this, and then it messes up my data model that I use every single day for my regular business."* | **CONFIRMED** | transcript `:244`, `:250` | 2026-07-08 | **No.** Still the governing constraint. Restated as the two-model split rationale at `cross-channel-marketing-attribution.md:137`. |
| **C-2** | **Unfamiliar new fields appearing in her model are the specific objection** — she names four by example: *"CAC spend to new customer, I have no idea what that is… ACOS take tacos, totally different place. It's never been there before. 5 box percent, totally different place."* | **CONFIRMED** | transcript `:241` | 2026-07-08 | No. This is the legibility complaint at its origin, and it is about **unfamiliarity and relocation**, not about volume of fields. |
| **C-3** | **The shape she expected**: *"I was hoping that, like, you would just choose a like, agency and you could choose electric, and then all of the things would still be the same."* i.e. one new slicer attribute, everything else identical. | **CONFIRMED** | transcript `:250` | 2026-07-08 | No. |
| **C-4** | **Google ad spend as a separate column that is part of the margin calculation, and marketplace-specific.** Verbatim: *"there's ad spend, and then there would be Google ad spend. It'd be a totally separate column that is a part of the margin calculation. But it's also marketplace specific."* | **CONFIRMED** | transcript `:352` | 2026-07-08 | No — **built** as Option B/C1 (`cross-channel-marketing-attribution.md:166-180`). |
| **C-5** | **Ad spend attributed by destination**: *"we do Google ad spend from Google to Amazon, and we do Google ad spend from Google to our Shopify sites… the ad spend to Amazon would be attributed to Amazon. The ad spend to Shopify would be attributed to Shopify."* | **CONFIRMED** | transcript `:361` | 2026-07-08 | Partly. Delivered at **channel** grain (Amazon vs Websites), not specific marketplace — an ALDC narrowing, documented and reasoned at `cross-channel-marketing-attribution.md:176-180`. The client asked "marketplace specific"; we shipped channel. **Flagged, not settled with the client.** |
| **C-6** | **Lectric/agency is sales-only** — client accepts there is no ad spend for it and will validate sales only. Heather: *"I'm all I'm doing is validating the sales?"* Lori: *"we don't have ad spend for them."* | **CONFIRMED** | transcript `:208`, `:145` | 2026-07-08 | No. Matches `navira-marketing-dashboard.md:18`. |
| **C-7** | **UK Amazon ad data is to be merged into the core data model once the client validates it** — Lori, relaying Paul: *"if you guys validate the data, then he'll merge it in with the same logic as the Amazon ad spend data into the data model."* | **CONFIRMED** | transcript `:142`, `:169` | 2026-07-08 | No. The validation is **still not recorded as received** anywhere I can read. |
| **C-8** | **The window ambiguity is the client's own.** Lori says *"For the full year"*; Heather immediately asks *"So it's, like, year to date?"*; Lori: *"Yep."* — same exchange, same figure. | **CONFIRMED** | transcript `:199-204` | 2026-07-08 | No. Independently flagged as live at `docs/evidence/navira-ad-metrics/measurement-contract.md:36-39`. |

⛔ **Absent from the transcript, and I looked for each explicitly:** no ask for a star-schema
restructure · no mention of ROAS, MER, TACoS as things she wants · no "high-level vs low-level"
distinction · no request to hide anything · no field-count complaint. The words "high level" and
"low level" do not appear.

### B. Asks recorded in contemporaneous client-meeting minutes

Source: `wiki/processes/distributed-workflow/active/navira/meeting-2026-07-22-model-split-ad-spend.md`,
frontmatter `sources: [client meeting minutes 2026-07-22 (Lori Beck / Heather Tabor / Justin Shuster)]`.
This is a minute, not a transcript — one hop from the client's mouth.

| # | Claim | Basis | Source | Expressed | Superseded? |
|---|---|---|---|---|---|
| **C-9** | **Two models by design**: a cleaned Daily *Sales* Model and a separate Marketing Model, *"so marketing detail doesn't clutter sales users."* | **CONFIRMED** | `meeting-2026-07-22:17-19` | 2026-07-22 | No. Foundational. |
| **C-10** | **Cross-channel ad-spend columns in the Daily model: UK + Google + Meta, USD-consolidated, by ad type (SP / SB / SD)** → users pull **total ad spend per SKU** and **spend by ad type**. | **CONFIRMED** | `meeting-2026-07-22:37-40` | 2026-07-22 | No. Built (`navira-roadmap-status.md:104-107`). ⚠ Note this **adds fields to the Daily model** — see CONTRADICTION 3. |
| **C-11** | **Agency data flows into the Daily model; ad spend must be agency-sliceable.** | **CONFIRMED** | `meeting-2026-07-22:41-42` | 2026-07-22 | Partially reversed on the *Marketing* model: agency layer removal is Paul's later call (`GP-318.md:214`), and GP-319 records *"no agency data in either model"* (Paul, 2026-08-25, `GP-319.md:78`). **This is an ALDC reversal of a client-agreed scope item.** See CONTRADICTION 4. |
| **C-12** | **Business-friendly column names — remove raw Snowflake CAPS/table names.** | **CONFIRMED** | `meeting-2026-07-22:43` | 2026-07-22 | No. Delivered as GP-292, applied 2026-07-24, *"0 visible raw ALL-CAPS columns remain"* (`navira-metric-dictionary.md:12-18`). |
| **C-13** | **Marketing views/metrics stay in the Marketing Model only, not in the Daily model.** | **CONFIRMED** | `meeting-2026-07-22:44` | 2026-07-22 | ⚠ In direct tension with C-10, which puts a marketing layer *into* Daily. Both are in the same minute. |
| **C-14** | **Do NOT build ASIN-level Google/Meta→Amazon attribution.** Blocked on campaign tagging that does not exist; Nicholas owns proposing it. *"Do not build attribution logic — surface spend totals only."* | **CONFIRMED** | `meeting-2026-07-22:53-58` | 2026-07-22 | No. Still the governing constraint. Amazon Attribution (GP-287) is the sanctioned *measured* path around it. |
| **C-15** | **Delivery deadline: two separate models by EOW Fri 2026-07-24.** | **CONFIRMED** | `meeting-2026-07-22:24-25`, `:34` | 2026-07-22 | Overtaken by events; no record of a renegotiated date. |

### C. Nicholas's metric matrix — the client's own written requirement document

| # | Claim | Basis | Source | Expressed | Superseded? |
|---|---|---|---|---|---|
| **C-16** | **Verbatim ask:** *"This table is all the advertising metrics I need ALDC to pull into the data warehouse."* Workbook *"Data Metrics for Advertising Dashboard - Multi-platform APIS.xlsx"*, sheet `Metric_Matrix_MASTER_v0`, **721 rows × 6 platform columns**. Excludes dimensions, inSite datapoints, SmartScout. | **CONFIRMED** | `aldc-launchpad/docs/evidence/navira-ad-metrics/gap-analysis.md:3-8` (quotes the client directly; the .xlsx is on disk at `docs/evidence/navira-ad-metrics/`) | workbook modified **2026-07-29** | No. This is the single largest client-authored requirement artefact on the account. |
| **C-17** | **The client scoped 352 of the 721 rows out himself** (Media/Entertainment N/A, DSP-only, DSP off-Amazon, DSP/Retail, DSP combined). The live ask is the **369 rows tagged `NOW - Sponsored Ads relevant`**. | **CONFIRMED** | `gap-analysis.md:31-34` — the tags are the client's own column | 2026-07-29 | No. ⚠ Never confirmed *back* to Nicholas — open question O-5. |
| **C-18** | **The client's platform scope is six platforms**: Amazon, Google Ads, Meta Ads, Walmart Connect, Target Roundel, eBay Ads. We ingest **three**. | **CONFIRMED** | `gap-analysis.md:110-114` | 2026-07-29 | No. 64 in-scope rows blocked on client-side API access. |
| **C-19** | **A second table — the dimensions list — was promised by the client and has not been received.** *"Right now we hold campaign ID and campaign name and not much else."* | **CONFIRMED** | `gap-analysis.md:5`, `:178-180` | 2026-07-29 | **No. Still outstanding.** This is likely the larger half of the request and it is entirely unspecified. |
| **C-20** | **The "core-10" (Impressions, Clicks, CTR, CPC, Total cost, Purchases, Sales, Units sold, Cost per purchase, ROAS) is the universal intersection of the client's own matrix** — 10 metrics supported by 5 of 5 non-Amazon platforms, **0 at 4-of-5**. | **INFERRED** | `docs/evidence/gp319/nicholas-metric-matrix-readout.md:15-38` | analysis 2026-08-24 | No — but it is **ours, derived from their data**. The client never named ten metrics. Say "derived from your matrix", never "you asked for these ten". |
| **C-21** | **Designing for the future costs nothing**: the set buildable today (Google ∩ Meta) and the set surviving Walmart+Target+eBay are the **same ten**; CPM is the single canary. | **INFERRED** | `nicholas-metric-matrix-readout.md:109-127` | 2026-08-24 | No. |

### D. The GP-319 marketing-model ask itself

| # | Claim | Basis | Source | Expressed | Superseded? |
|---|---|---|---|---|---|
| **C-22** | **Heather's email of 2026-08-10 set three client priorities**; the third is the Marketing Data Model, which became GP-319 and owns a **gate**: no further marketing-dashboard work until the client signs off that the marketing data is correct. | **SUPPORTED** | `boot-prompts/navira-marketing-model-signoff-gate.md:13-16`, `:75-77`. **The email is not in any repo.** | 2026-08-10 | No. |
| **C-23** | **The client's stated preferred deliverable:** *"the best path forward for the Marketing model would be to put together **a few views in a workbook** for him to review."* ("him" = Nicholas.) | **SUPPORTED** | Heather's email, quoted in GP-319's 2026-08-12 Jira comment, relayed at `boot-prompts/gp319-marketing-model-session-2026-08-23.md:105-108`. **Neither the email nor the Jira comment is readable.** | 2026-08-12 | No. |
| **C-24** | **"Three designs" is ALDC's number, not the client's.** *"'Three designs' appears in no client-sourced text on the ticket."* The description scopes the exploration *"on our end"*; Paul committed to *"several candidate designs"*; three was settled by Paul on 2026-08-23. | **CONFIRMED** (as an internal decision) | `gp319-marketing-model-session-2026-08-23.md:110-114` | 2026-08-23 | No. **Do not inherit "three" as a client requirement.** |
| **C-25** | **Navira's users don't understand how the model is structured** — reported by Justin, via Heather. | **SUPPORTED** | `navira-marketing-model-signoff-gate.md:99-101`. Two hops (Justin → Heather → us), no primary artefact. | 2026-08-06 | No. Note GP-292's friendly names + folders **did not fix it** — same source. |
| **C-26** | **The consumer is Excel PivotTables**, so the field list *is* the product. Third consumer constraint: PBI model · Next.js dashboard reading Snowflake **directly** · Navira's own SQL. | **SUPPORTED** | `gp319-marketing-model-session-2026-08-23.md:116-119` (attributed to Paul, 2026-08-23); corroborated `GP-319.md:22` | 2026-08-23 | No. The "Navira's own SQL (GP-151)" leg is uncited beyond this line — treat as `SUPPORTED`, not measured. |
| **C-27** | **Sheet 1 should be Heather's own hand-built Mastersku ad-spend pivot** — *"the concrete example already in the client thread."* | **SUPPORTED** | `gp319-marketing-model-session-2026-08-23.md:124-125`; delivered as Cookbook tab 1 (`GP-319.md:247-249`) | 2026-08-23 | No. The client thread it refers to is not readable. |

### E. ALDC decisions frequently mistaken for client asks

These are **ours**. Every one is correctly attributed in the wiki; they are listed here so D3 does not
present them back to the client as things the client requested.

| # | Claim | Basis | Source | Expressed |
|---|---|---|---|---|
| **C-28** | **Blended MER is the board-level marketing-efficiency headline.** | **CONFIRMED as an ALDC decision** — *"DECIDED 2026-05-29 (Paul)"* | `cross-channel-marketing-attribution.md:100` | 2026-05-29 |
| **C-29** | **USD is the consolidation target.** | **CONFIRMED as an ALDC decision** (Paul) | `cross-channel-marketing-attribution.md:102` | 2026-05-29 |
| **C-30** | **Amazon headline attribution window = 30 days.** Explicitly *"Revisit only if Navira requests a different window"* — i.e. **the client has never been asked.** | **CONFIRMED as an ALDC decision** (Paul) | `cross-channel-marketing-attribution.md:103` | 2026-05-29 |
| **C-31** | **Google/Meta product linkage deferred, then brand-grounded (Phase 2a).** | **CONFIRMED as an ALDC decision** (Paul) | `cross-channel-marketing-attribution.md:101` | 2026-05-29, updated 2026-06-09 |
| **C-32** | **The whole tiered model (Tiers 0 → 4) is an ALDC construct.** No client artefact references tiers. | **ASSUMPTION** that the client shares this vocabulary — **no supporting evidence found** | `cross-channel-marketing-attribution.md:23-39` | 2026-05-29 |
| **C-33** | **PROD promotion is gated on (a) client sign-off of the design in TEST and (b) trustworthy COGS coverage.** An ALDC-imposed gate. | **CONFIRMED as an ALDC gate** | `cross-channel-marketing-attribution.md:116-133` | 2026-06/07 |
| **C-34** | **PROD promotion of the Marketing Model is gated on Nicholas (Google/Meta validation, YTD) + Heather (Lectric sales).** These are named client validators — but there is **no record of either validation arriving.** | **SUPPORTED** | `cross-channel-marketing-attribution.md:209-210` | 2026-07-08 |

### F. Client validation and sign-off — the state of the record

| # | Claim | Basis | Source |
|---|---|---|---|
| **C-35** | **No client sign-off on the marketing model exists anywhere in the readable record.** GP-319's own deliverable list includes *"client sign-off on correctness"* and the ticket remains open with sign-off outstanding. | **CONFIRMED (as an absence, from an instrument proven able to see the positive case)** — the same corpus records a sign-off *when one happened*: GP-292 *"TRANSITIONED TO DONE 2026-07-24 (TEST-accepted; rendered sign-off accepted at close)"* (`navira-metric-dictionary.md:38`). So the instrument can register acceptance; it registers none here. | `GP-319.md:11-15`, `:255-275` |
| **C-36** | **The UK ad-data validation the client agreed to perform (C-7) is not recorded as delivered.** | **UNKNOWN** — no evidence either way; classify **NOT-RECORDED**, not "the client didn't do it". | transcript `:169`; nothing downstream |
| **C-37** | **Nicholas has never received a reply to his 721-row matrix.** *"Nothing has been sent to Nicholas"*; the cover note is *"DRAFT — Not sent"* and carries a hold: *"do not send `cover-note-draft.md` until that lands."* | **CONFIRMED** | `gap-analysis.md:11`, `cover-note-draft.md:3`, `gap-analysis.md:192-194` |
| **C-38** | **The client has queried our numbers and been right before.** Paul spotted Lectric per-product Sales = $0 against $2.7M real sales; root cause was two real defects. | **CONFIRMED** | `navira-marketing-dashboard.md:295-299` |

---

## 2. CONTRADICTIONS

### ⭐ CONTRADICTION 1 — the Daily/Marketing metric boundary rests on a recollection the transcript does not support

**Side A (the record).** GP-319 §"The §1 boundary, finally recorded": engagement metrics
(Impressions, Clicks, CTR, CPC, CPM + four quantity measures + the `Campaign` table) are **hidden on
Daily, visible on Marketing**, and this *"rests on a recollection of Heather's ask"*, with the
implementing script's docstring saying *"confirm against the Avoma transcript before this reaches
Heather"* — **Not done** (`GP-319.md:170-184`). GP-318 §D9 describes the same hide as coming from
*"a recollection of a 'high-level vs low-level' ask never written into Jira"* (`GP-318.md:677-682`).

**Side B (the transcript).** I read
`aldc-launchpad/boot-prompts/navira_data_model_review_meeting_lori_heather.md` end to end. It
contains **no** high-level/low-level distinction, **no** request to hide any measure, and **no**
discussion of engagement metrics. What it contains is C-1/C-2/C-3: *don't change my model*, *these
new words confuse me*, *I expected one new slicer and everything else the same*.

**Which is stronger: Side B, decisively.** Side A is self-described as unconfirmed recollection and
says so twice on two different pages. Side B is a verbatim transcript. **Verdict: the "high-level vs
low-level ask" is not supported by the only client transcript in the repos.** Whether another call
exists that does contain it is **NOT-VISIBLE** — one Avoma transcript is on disk and this is it.

**Why this matters and is not merely tidy-up:** GP-318 §D9 already *reversed* the hide, on
PROD-parity grounds, and the measurement **widened** the fix from five objects to ten
(`GP-318.md:677-682`). So the right action was taken for a reason unrelated to the client. The
record still carries the phantom ask as live justification. **Correcting a premise is a deliverable
— this one should be corrected wherever it was published, including the Jira comment 36056 that
recorded the boundary as settled.**

### CONTRADICTION 2 — the model-review call is dated 2026-07-08 in one place and 2026-08 in another

`measurement-contract.md:36-37` says *"in the **2026-08** model-review call with Heather, Lori used
'for the full year' and then agreed to 'so it's, like, year to date?'"*. That exchange is at
transcript `:199-204`, and `cross-channel-marketing-attribution.md:135` dates the same Lori↔Heather
review **2026-07-08**; the transcript file's own mtime is 2026-07-08 16:30.

**Stronger evidence: 2026-07-08.** Two independent artefacts (the wiki architecture page and the
file's own timestamp) against one prose reference. Consequence: a measurement contract that
motivates its window ambiguity from a call it dates a month late. Low blast radius, but it is the
kind of date slip that the client can catch, and FU92-420's lesson is that four implied dates in one
document is how credibility goes.

### CONTRADICTION 3 — "no new fields in Daily" vs "add cross-channel ad-spend columns to Daily"

`cross-channel-marketing-attribution.md:137` states Heather's constraint as *"new fields/relationships
in her daily model = a **hard no**"*. Two weeks later the 2026-07-22 minute records decision 1:
**add** UK+Google+Meta ad-spend columns, by ad type, per SKU, into the Daily model
(`meeting-2026-07-22:37-40`) — and decision 4 in the *same* minute says marketing metrics stay in the
Marketing Model only (`:44`).

**Neither is wrong; the summary is.** The transcript resolves it: Heather's objection (C-2) is to
**unfamiliar, relocated** fields, and her own ask (C-4) is for a Google-spend column *inside the
margin calculation* — a new field she explicitly wants. **The "hard no on new fields" framing is an
over-generalisation of C-1 and it will mislead a designer.** The honest rule the evidence supports:
*additions are welcome where they extend a concept the team already uses; additions are rejected
where they introduce vocabulary the team has to be retrained on.* That is a much more useful
constraint and it is the one the client actually stated.

### CONTRADICTION 4 — agency in the Daily model: client-agreed, then reversed by us

C-11 (client minute, 2026-07-22): agency data flows into the Daily model, ad spend agency-sliceable.
`GP-318.md:214` (2026-08-13): *"Agency layer removed (Paul's call — agency gets its own model
later)"*. `GP-319.md:78` (2026-08-25): *"no agency data in either model, and Lectric is being
removed."*

**Both are accurately recorded; the contradiction is real and unreconciled with the client.** The
reversal has a good technical reason (the Marketing Model is **blocked** until Lectric is stripped at
source — `GP-318.md:216-218`; and Lectric carries $2.76M of sales with zero cost and zero ad spend,
so stripping it **moves client-visible ratios**: gross −2.13%, net −2.27%, margin % and TACoS/MER
both *rise* — `GP-319.md:96-98`). **Stronger evidence: the technical measurement.** But the client
agreed to something else in a minuted meeting, and **`GP-319.md:98` itself says the ratio movement
"must be announced, not discovered."** No announcement is on file.

### CONTRADICTION 5 — GP-296 blocks sign-off / GP-296 was never a blocker

Same page, two sections. `GP-319.md:17-18`: *"Blocked by GP-296 (the $2.72M divergence, **unassigned**
— the last blocker on correctness sign-off)"*. `GP-319.md:265-268`: *"**GP-296 is REFUTED, not open**
— measured 2026-08-12: delta **$0.00** on NAVIRA's sales anchor across all three copies… It is **not**
a blocker and never was."* And `GP-318.md:820` still lists it as *"the blocker on correctness
sign-off."*

**Stronger evidence: the refutation** — it carries a measurement, a date, and a decomposition (the
whole $264,836 difference sits 100% inside LECTRIC). The blocking claim carries none. **Consequence
for D3: do not treat the marketing model design as blocked by GP-296.** The action GP-319 names is
closing the ticket, and it has not been done, so a fresh reader will inherit a stale blocker.

### CONTRADICTION 6 — "Purchases is absent" vs "Purchases needs no pipeline work"

`nicholas-metric-matrix-readout.md:64`: **Purchases** — *"⛔ **absent.**"* `GP-319.md:158-159`: *"Add
`Purchases` from the existing `CONVERSIONS` column… **two of the ten 'absent' core metrics need no
pipeline work at all.**"* `gap-analysis.md:72`: `purchasesSameSku30d` is **landed and populated in
prod**, 26,388 rows, 16,177 of 23,661 (68%), and thrown away at the view layer.

**Reconcilable, and all three are right about different layers** — absent from the *PBI model*,
present in the *warehouse*, discarded at the *view*. But they are stated as flat facts in three
artefacts with no cross-reference, and a designer reading only the first will scope pipeline work
that does not exist. **The strongest statement is `gap-analysis.md`'s**, because it cites row counts
from a live prod query.

### CONTRADICTION 7 — a conformed core fact: recommended twice, then rejected

`nicholas-metric-matrix-readout.md:143-148` (2026-08-24) concludes the matrix *"is describing a
different shape: **one narrow conformed fact at the core-10 grain**… per-platform extension facts."*
`attribution-design-decision.md:60-78` (2026-08-24) restates it as **the** scalable shape.
`GP-319.md:144-148` (2026-08-25) **rejects a conformed core fact in the warehouse**.

**The rejection is later and is the standing decision** (see LOCKED-2). But the two documents
recommending the rejected shape are still on disk, undated-in-body as superseded, and both are
persuasive. **This is the single highest-risk trap for D3: a designer who finds those two files
first will build the thing GP-319 rejected the next day.**

---

## 3. DECISIONS ALREADY LOCKED — honour, do not re-litigate

The three the mission named are **all verified**. Fourteen more found.

| # | Decision | Verified at | Date | Note |
|---|---|---|---|---|
| **L-1** ✅ | **`MARKETING_FCT_ACTIVITY_UNIFIED` is canonical** — *"Declare it canonical — it already is — and rebuild the measure layer on it."* | `GP-319.md:141-142` | 2026-08-25 | Supersedes the earlier *"C now, A next"* recommendation on the same page (`:126`). Corroborated: it carries cost, clicks, impressions **and conversions** for all five platforms at campaign × ad-group × product × date × marketplace grain (`GP-319.md:231-232`), and it is a **view**, not a materialized table (`GP-318.md:582`). |
| **L-2** ✅ | **A conformed core fact in the warehouse is REJECTED.** *"It would create a new table for figures that already live in one object and already reconcile to the cent… This client already carries ~14 copies of the marketing family across 6 schemas; a 15th worsens the canonical-object problem. Nothing is left to conform."* | `GP-319.md:144-148` | 2026-08-25 | See CONTRADICTION 7 — two earlier docs recommend the opposite. |
| **L-3** ✅ | **A long/narrow `(grain, METRIC_KEY, METRIC_VALUE)` fact is REJECTED**, and this was *"the re-test the AC owed"*. Reason: *"the core is 10 metrics wide with a per-source tail; a key-value fact makes every query a pivot and destroys the plain star with a real product edge, while fixing nothing — the defect is naming."* | `GP-319.md:149-152` | 2026-08-25 | **Rejected twice independently** — first at `gap-analysis.md:144-147` (2026-08-04) on different grounds: *"the collapse to ~10 base events removes the problem it solves — column count was never the threat."* Two instruments, same verdict. |
| **L-4** | **Curating the surface alone is insufficient** — it ships *on top* of the measure-layer fix, never instead of it. Alone it leaves the two-platform hard-code live, purchases missing, and 16 ROAS measures with no default. | `GP-319.md:151-153` | 2026-08-25 | |
| **L-5** | **Deprecate by description + display folder, NEVER by rename.** Additive only, because the model is client-visible and *"additive means we live with them."* | `GP-319.md:155-160` | 2026-08-25 | Reinforced by Kimball's own 2014 worksheet shipping `Display Name` separate from `Column Name` — *"the fix is a display layer, not a rename"* (`cross-channel-marketing-dimensional-model.md:470-474`). |
| **L-6** | **Put the scope in the measure name.** *"A platform allow-list living inside a DAX literal is invisible at the field list, invisible in the relationship graph, and reads to everyone downstream as a data defect. Three sessions on this ticket chased it as one."* | `GP-319.md:234-236` | 2026-08-25 | The single most transferable lesson on the ticket. |
| **L-7** | **`PRODUCT_ID = '-1'` ($457,425 / 15.6% of ad spend) gets an explicit `(no product key)` row. DO NOT allocate it** — *"that is invention."* No join or connector fix recovers it; the platform reported a campaign-level aggregate *instead of* a product. | `GP-319.md:188-191` | 2026-08-25 | Product-keyable ad spend tops out at **84.35%**. |
| **L-8** | **A product relationship on the product-grain marketing table is ILLEGAL, not merely undone** — `Product[ASIN]` is not unique (9,754 ASINs on >1 row, 89.7% of the table). | `GP-319.md:194-195` | 2026-08-25 | Hard structural constraint. Any design assuming that edge is void. |
| **L-9** | **No stored ratios.** All 91 derived rows (CTR, CPC, CPM, ROAS, cost-per-X, rates) become semantic-layer measures, defined once. | `gap-analysis.md:138`, `:32-34` | 2026-08-04 | Externally corroborated: Kimball *"store the fully additive components… and sum these before calculating the final non-additive fact"* (`cross-channel-marketing-dimensional-model.md:150-154`). |
| **L-10** | **Not-reported is NULL, never 0.** *"A 0 reads as 'we measured none' when the truth is 'the source doesn't report it'."* | `gap-analysis.md:142`, `cover-note-draft.md:60-66` | 2026-08-04 | The account's most expensive recurring defect class — GP-318 items 2 and 3 are the same error in opposite directions (`GP-318.md:153`). |
| **L-11** | **Two-model split rule:** a feature goes in the Marketing Model **iff** it adds a relationship/dim to the star. Purely additive-to-the-Amazon-star features may stay in Daily. | `cross-channel-marketing-attribution.md:149-153` | 2026-07-08 | |
| **L-12** | **Model-naming convention:** environment is conveyed by the **workspace** (`GEP Test Models` / `GEP Prod Models`), never the dataset name. Datasets carry no `(Test)`/`(Prod)` suffix. | `cross-channel-marketing-attribution.md:141-147` | 2026-07-09 | |
| **L-13** | **Google/Meta ad-spend attribution grain is CHANNEL (Amazon vs Websites), by design** — because Google/Meta data carries only destination channel. *"Per-specific-marketplace would invent a US/CA split Amazon never had to."* | `cross-channel-marketing-attribution.md:176-180` | 2026-07-08 | ⚠ This is our narrowing of client ask C-5, which said "marketplace specific". |
| **L-14** | **Amazon-destination Google/Meta spend stays spend-only** — grounding it against total Amazon brand sales gave absurd 1500–6800× ROAS. Amazon Attribution (GP-287) is the only sanctioned measured path. | `cross-channel-marketing-attribution.md:76`, `:217-242` | 2026-06-09 / 2026-07-15 | |
| **L-15** | **Parsing `Brand_ASIN` out of campaign names for attribution is REJECTED** — partial by construction (~$33k of $106.5k unparseable), depends on Quartile's free-text convention, does not generalise, and *"is a PROXY presented as a measurement."* Amazon's own API draws the distinction the parse destroys (`attributedSales14d` vs `brandHaloAttributedSales14d`). | `attribution-design-decision.md:8-30` | 2026-08-24 | Supersedes the earlier "option 1" recommendation in `google-meta-to-amazon-attribution.md` §6. |
| **L-16** | **Guards use `ISFILTERED`, never `ISCROSSFILTERED`.** `ISCROSSFILTERED('T')` is true when T *or anything related to T* is filtered; most added tables hang off `Date`, so it blanks every ordinary date pivot. **Propagation, not adjacency.** | `GP-318.md:309-312`, `GP-319.md` via `answerability-guard` | 2026-08-17 | Cost two failed fix passes to learn. |
| **L-17** | **Meta per-product grounding (Phase 2c) is deferred; SmartScout is out of scope entirely.** | `cross-channel-marketing-attribution.md:113`; `navira-marketing-dashboard.md:273` | 2026-06-09 / 2026-07-17 | |
| **L-18** | **Never let platform-reported value masquerade as ground truth.** Two clearly-separated layers: platform-reported (tactical) and ground-truth from actual orders (strategic). **Never sum platform-attributed sales across channels** ("Flag A"). | `cross-channel-marketing-attribution.md:21`; enforced structurally at `navira-metric-dictionary.md:98-105` | 2026-05-29 | The one design law with a *structural* enforcement already shipped. |

---

## 4. OPEN QUESTIONS FOR THE CLIENT

The two the mission named are **verified open**. Twelve more found. Ordered by how much they change a design.

| # | Question | Basis for it being open | Blocks |
|---|---|---|---|
| **O-1** ✅ | **Which ROAS is canonical?** **16 visible ROAS measures** exist with no stated default — Platform ROAS ×3, Calibrated ×3, Calibrated (Capped) ×3, Margin ROAS, MER (Blended), Grounded ROAS, and more. *"An Excel user picks one at random and gets an answer that is defensible in isolation and irreconcilable with a colleague's."* | `GP-319.md:161-163`; `nicholas-metric-matrix-readout.md:66`, `:73-76` | **Tier 0 build.** Named explicitly as one of *"two human decisions first."* |
| **O-2** ✅ | **Sign-off on the new measure names**, because they land on a client-visible model and additive means we live with them. | `GP-319.md:163-164` | **Tier 0 build.** |
| **O-3** | **Capped or uncapped Calibrated ROAS?** They diverge hard for Navira (calibration factor ≈ 6.4): uncapped gives Amazon 32.5x / Google 18.0x / Meta 6.4x; capped collapses to Platform ROAS (5.05 / 2.80 / 0.99x). Both built. *"Decision belongs to Navira."* Surfaced **2026-06-05**; no answer on file **~3 months later**. | `cross-channel-marketing-attribution.md:255-262` | Compounds O-1 — this is a *second* ROAS ambiguity underneath the first. |
| **O-4** | **Is the `Amazon (Ads API)` column in Nicholas's matrix blank because Amazon is the reference taxonomy, or because it wasn't filled in?** Empty in **all 721 rows**. Blank and "Not available" render identically to a reader. *"It changes whether '236 Amazon-only metrics' is a finding or an artifact of an unfilled column."* | `nicholas-metric-matrix-readout.md:77-89`; `gap-analysis.md:169-172` | The largest single ambiguity in the client's own requirement doc. One line of reply settles it. |
| **O-5** | **Confirm the 352 non-NOW rows are out of scope for v1.** | `gap-analysis.md:173` | Scope of GP-320. |
| **O-6** | **Does Navira run Sponsored Display at all?** Now partly answered by measurement — SD ran and **our feed stopped** (942 rows, 2024-06-27 → 2026-06-05, $3,374.90); the question remaining is whether the *intermittency* (nothing 2025-09 → 2026-03) is real behaviour. Verdict recorded as **UNVERIFIED, not ZERO**. | `gap-analysis.md:186-191`; `GP-319.md:269-272`; `gp319_sd_zero_verdict.json` | Whether add-to-cart / DPV / branded-searches totals need an "SB-only" caveat. |
| **O-7** | **Are Walmart Connect / Target Roundel / eBay Ads in scope for v1, and can the client provide API access?** 64 in-scope rows, no connector, no credentials. *"The biggest piece of genuine work in the request."* | `gap-analysis.md:110-114`, `:177` | Whether the model must be built for 6 platforms or 3. Note C-21: **it costs nothing to design for six**. |
| **O-8** | **The dimensions table Nicholas promised has never arrived** — and it is *"likely the bigger half."* We hold campaign_id + campaign_name and nothing else: no brand, portfolio, ad type, targeting, match type, placement. | `gap-analysis.md:5`, `:178-180` | **Any dimensional design.** This is the largest unspecified surface in the whole engagement. |
| **O-9** | **Are `Purchases` and `Cost per Purchase` in scope for the model, or declared out?** Two of the durable ten; both Google and Meta already report them; the model has neither. | `nicholas-metric-matrix-readout.md:104-105`, `:161-163` | See CONTRADICTION 6 — the pipeline work is smaller than the question implies. |
| **O-10** | **What window does "last year" mean?** W1 calendar 2025 / W2 YTD 2026 / W3 trailing 12m / W4 last 12 complete months. The client used two of these in one exchange (C-8). Material: Meta begins 2026-04-20 (so W1 contains **no Meta at all**); UK begins 2026-03-08. | `measurement-contract.md:27-39`; transcript `:199-204` | Every quoted total. |
| **O-11** | **TACoS formula rebase** — to `spend ÷ total sales`. The *relabel* shipped; the *formula* rebase is held, **client-gated on Lori's "advertising cost" answer** (GP-303). | `navira-metric-dictionary.md:39-41`, `:92-96` | Whether TACoS has one definition or two. GP-318 B25 measured *"one definition, two date ranges"* (`GP-318.md:460`). |
| **O-12** | **Was the ask that produced the Daily/Marketing metric-visibility boundary ever real?** Per CONTRADICTION 1, no client artefact supports it. | `GP-319.md:183-184` (self-flagged unconfirmed); transcript, read | The boundary's justification. The *fix* is already correct on other grounds; the *record* is not. |
| **O-13** | **Did the client ever validate the UK ad data (C-7)?** Agreed 2026-07-08; no record of arrival. Classify **NOT-RECORDED**. | transcript `:169` | The UK merge into the core model. |
| **O-14** | **Did Navira run Meta advertising in 2025?** Our first Meta data is 2026-04-20. Until asked, **W1 Meta is `ZERO` or `NOT-RECORDED` — unresolved**, and publishing it as zero would be a claim about the client's behaviour. | `measurement-contract.md:129` | Any 2025 cross-channel total. |
| **O-15** | **The brand→entity ownership decision.** Named as an open client-side decision gating GP-318's sign-off; no detail beyond the name. | `GP-318.md:398`, `:400-402` | Entity scoping. Under-specified even as a question — **needs restating before it can be asked.** |

---

## 5. NOT-VISIBLE inventory — sources the reconstruction needs and cannot reach

Recorded as `NOT-VISIBLE` rather than inferred, per the stop conditions.

- **Jira, entirely.** GP-319 comments `36055 36056 36073 36082`; GP-318 comments `35978 35979 35980
  35981 35984 35988 35990 36066 36067`; both ticket **descriptions**. Every claim citing them is
  second-hand.
- **Heather's emails of 2026-08-06 and 2026-08-10.** The 08-10 email sets the three client
  priorities that define GP-317/318/319. Not in any repo.
- **Ten referenced tickets have no wiki page:** GP-290, GP-292, GP-295, GP-296, GP-301, GP-303,
  GP-317, GP-320, GP-321, GP-325. Verified by directory listing of `wiki/tickets/gep/`.
  GP-296 and GP-317 are load-bearing in several claims above.
- **Any Avoma transcript other than the single Lori↔Heather call.** One is on disk. Whether others
  exist is unknown; absence of a file is not evidence of absence of a call.
- **`Data Metrics for Advertising Dashboard - ALDC annotated.xlsx`** — on disk at
  `docs/evidence/navira-ad-metrics/`, binary, not opened by me. Its 721-row content reaches me only
  through `gap-analysis.md` and `nicholas-metric-matrix-readout.md`, which **agree** with each other
  on every figure I could cross-check (721 rows, 369 NOW, 352 out-of-scope, 91 derived, empty Amazon
  column). Two internally-consistent readers is corroboration, not verification.
- **The "client thread"** containing Heather's hand-built Mastersku pivot (C-27).
- **`navira-data-issue-register.md`** (`aldc-launchpad/navira-dashboard-redesign/reports/`) — cited
  as the DQ register in two places; not read in this pass.
- **The GP-319 three-designs readout** `docs/readouts/gp319-marketing-model-designs.html` (81KB) —
  grepped for client-ask language, not read in full. It returned **no** client-attributed
  requirement statements, only references to Nicholas's matrix. Its designs figure is separately
  recorded as flawed (`GP-319.md:134-138`).

---

## 6. Claim count by basis

| Basis | Count | Claim ids |
|---|---:|---|
| `CONFIRMED` — client's own words or a contemporaneous minute | **19** | C-1…C-9, C-10…C-15, C-16…C-19, C-24, C-35, C-37, C-38 *(C-28…C-31, C-33 are CONFIRMED **as ALDC decisions**, counted separately below)* |
| `CONFIRMED (as an ALDC decision, not a client ask)` | **6** | C-28, C-29, C-30, C-31, C-33, C-24 |
| `SUPPORTED` — one internal record quotes the client, no readable primary | **7** | C-22, C-23, C-25, C-26, C-27, C-34, and the "Navira's own SQL" leg of C-26 |
| `INFERRED` — derived by us from client data; client never said it | **2** | C-20, C-21 |
| `ASSUMPTION` — no citable source | **1** | C-32 (that the client shares the Tier 0–4 vocabulary) |
| `UNKNOWN` / NOT-RECORDED | **2** | C-36, and O-13/O-14 as questions |
| **Total ledger claims** | **38** | C-1 … C-38 |

**Contradictions: 7. Locked decisions verified: 18 (the 3 named + 15 more). Open client questions: 15 (the 2 named + 13 more).**

---

## 7. The three sharpest things, if only three are read

1. **The metric-visibility boundary rests on a client ask that the only client transcript does not
   contain.** The confirmation GP-319 owed has now been performed and it comes back negative. The
   remedy already shipped for a different, better reason; the *justification* on the record is
   phantom and should be corrected where it was published.

2. **A conformed core fact was recommended by two ALDC documents on 2026-08-24 and rejected by
   GP-319 on 2026-08-25.** Both recommending documents are still on disk and read as current. Any
   designer who finds them first will build the rejected thing. The rejection is the standing
   decision and its reason is specific: *the client already carries ~14 copies of the marketing
   family across 6 schemas; a 15th worsens the canonical-object problem.*

3. **The client's largest requirement is half-delivered and the other half was never sent.**
   Nicholas's 721-row matrix has a fully analysed reply sitting **unsent** under an explicit hold,
   and the **dimensions table — "likely the bigger half" — has never arrived.** So the dimensional
   half of a dimensional model is, as of today, entirely unspecified by the client. No design should
   present a dimension list as responsive to a request that has not been made.

**And one plain absence worth stating on its own: there is no client sign-off on anything in the
marketing model.** That is a real ZERO, not a blind instrument — the same corpus records GP-292's
acceptance when it happened.
