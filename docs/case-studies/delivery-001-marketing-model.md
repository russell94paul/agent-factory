# Delivery #001 — Navira Cross-Channel Marketing Model

## Forensic reconstruction, and the Agent Factory counterfactual

**Compiled 2026-08-31/2026-09-01. Read-only reconstruction. This document is the canonical data
source for the interactive case-study artifact; the artifact must not assert anything this file
does not.**

---

## 0. How to read this document, and what it is allowed to claim

### 0.1 There are two deliveries here, not one, and conflating them would be the first error

| | **Delivery A — the client work** | **Delivery B — the Factory mission** |
|---|---|---|
| What | The Navira cross-channel marketing model: warehouse SQL, a PBI semantic model, a Next.js dashboard, Jira GP-287…GP-325 | `marketing-model-reconstruction-v1` — a bounded, read-only mission to reconstruct what Delivery A actually was |
| When | 2026-05-29 → ongoing (first locked decision 2026-05-29; latest evidence 2026-08-25) | 2026-09-01T00:52:14Z → 2026-09-01T03:14:03Z (UTC, measured from `.data/tasks.jsonl`) |
| Who | Humans and human-directed sessions, no orchestration layer | Agent Factory primitives — `TaskStore`, `claims`, `evidence` — driven manually |
| Evidence quality | Reconstructed at one hop, through R1 and R2 | Measured directly from append-only stores in this session |

**Delivery A is where the commercial damage lives. Delivery B is the instrument that found it.**
Every Agent Factory counterfactual in §7 is a claim about what would have happened *had Delivery A
run on the Factory* — and none of it ran that way, so all of it is `SIMULATED`.

### 0.2 Evidence basis vocabulary — every claim in this document carries one

```
MEASURED      I ran a command against repository state in this session and read the output.
DOCUMENTED    Stated in a repo file I read. The file is cited. One hop from measurement.
DERIVED       Computed from MEASURED or DOCUMENTED values; the computation is shown.
INFERRED      My reasoning. Not stated anywhere. Weakest tier used in this document.
SIMULATED     Counterfactual Agent Factory behaviour. Never observed. Never a claim about the past.
NOT_RECORDED  The record does not hold it. Distinct from zero, and never rendered as one.
```

⛔ **A specific and load-bearing caveat.** Everything about Delivery A reaches this document
**through R1 and R2** — two reconstruction artifacts written on 2026-08-31 that themselves read
primary files and cited line numbers. That is one hop. I have not re-opened `GP-319.md`,
`MARKETING_EFFICIENCY.sql` or `warehouse.ts` myself. So Delivery A facts are marked
`DOCUMENTED (R1)` or `DOCUMENTED (R2)`, never `MEASURED`, however precise the figure looks.
**Two internally-consistent readers is corroboration, not verification** — R1 says exactly this
about its own sources, and the same discipline applies to R1.

### 0.3 What this document deliberately does not do

It does not assign numeric time savings that were not recorded. `estimate_minutes` exists for all
eight mission tasks; **`actual_minutes` was never written for any of them** (MEASURED — no key
matching `actual` appears in `.data/missions/marketing-model-reconstruction-v1.json`, and no
duration event exists in `.data/tasks.jsonl`). So wall-clock figures below are `DERIVED` from event
timestamps with the derivation shown, and everything else is `NOT_RECORDED`.

---

# A. Detailed chronological case study

<!-- anchor: sec-a -->

## A.1 Delivery A — the client work, reconstructed

Twelve steps. Order is established by dated citations inside R1 and R2; where a date is uncertain
it is said so rather than smoothed.

---

### STEP A1 — The measurement law is written

<!-- anchor: step-a1 -->

```
TIME / ORDER              2026-05-29. The earliest dated decision in the record.
TRYING TO ACHIEVE         A defensible way to answer "is our marketing spend working" across
                          Amazon, Google and Meta, when each platform grades its own homework.
WHAT WAS KNOWN            That platform-reported attribution double-counts across channels.
                          That the client had three ad platforms and one profit question.
WHAT WAS ASSUMED          That a tiered vocabulary (Tier 0 spend -> Tier 4 causal) would be
                          shared with the client. NEVER TESTED. R1 grades this ASSUMPTION with
                          no supporting evidence found - claim C-32.
WHAT WAS DONE             Four decisions locked in one sitting: blended MER as the board-level
                          headline; USD as the consolidation target; a 30-day Amazon attribution
                          window; Google/Meta product linkage deferred. Plus the single most
                          durable rule in the estate: platform-attributed value is NEVER summed
                          across channels.
WHAT THE AGENTS DID       Nothing. No agents existed on this work.
EVIDENCE AVAILABLE        The platforms' own API semantics.
NOT YET KNOWN             That the 30-day window would be aliased away at the point of
                          implementation. That MER would be written backwards in this very
                          document. That the tier vocabulary would never reach the client.
WHAT HAPPENED NEXT        The never-sum rule propagated into four independent layers and held.
                          The window label did not.
```

`DOCUMENTED (R1 C-28..C-32, L-18; R2 L1, L2, L7)`. Cites
`cross-channel-marketing-attribution.md:100-103`, `:25-32`, `:21`.

⭐ **This step is the case study's control.** One decision taken here — *never sum across channels*
— was enforced structurally, and R2 found it honoured in the warehouse view, the monthly view, the
frontend field contract and the frontend code. **A locked decision with a structural enforcement
survived three months and four layers. A locked decision recorded only in prose did not.** That
contrast is the whole argument for the Factory, and it was produced by the delivery itself, not by
the Factory.

---

### STEP A2 — The client says, in her own words, what she actually wants

<!-- anchor: step-a2 -->

```
TIME / ORDER              2026-07-08. Lori Beck <-> Heather Tabor (Navira/GEP COO), model review
                          call. 487-line Avoma transcript.
TRYING TO ACHIEVE         Client sign-off on a restructured data model.
WHAT WAS KNOWN            Internally: that a two-model split was probably needed.
WHAT WAS ASSUMED          That the client's objection was about model structure.
WHAT THE CLIENT DID       Stated four things plainly:
                          (1) "we do not wanna, like, change the functionality of that data
                              model... otherwise, we gotta retrain everybody"
                          (2) named four unfamiliar fields by example - "CAC spend to new
                              customer, I have no idea what that is"
                          (3) "I was hoping that... you could just choose a agency and you could
                              choose electric, and then all of the things would still be the same"
                          (4) asked for Google ad spend as a separate column inside the margin
                              calculation, marketplace-specific
EVIDENCE AVAILABLE        A verbatim transcript. The strongest artifact on the account.
NOT YET KNOWN             That this transcript would be cited for months as the source of a
                          request it does not contain.
WHAT HAPPENED NEXT        The transcript was filed. It was not read again for eight weeks.
```

`DOCUMENTED (R1 C-1..C-8)`, transcript `:241`, `:244`, `:250`, `:352`, `:361`.

⭐ **The single most consequential fact in Delivery A is a negative, and it is here.** The client
never asked for a high-level/low-level metric split. R1 searched for it explicitly: *"the words
'high level' and 'low level' do not appear."* Everything in STEP A6 follows from an ask that was
not made.

---

### STEP A3 — Minutes are taken, and two of their own decisions conflict

<!-- anchor: step-a3 -->

```
TIME / ORDER              2026-07-22. Client meeting minute (Lori / Heather / Justin Shuster).
TRYING TO ACHIEVE         Convert A2 into a buildable scope with a date.
WHAT WAS DONE             Decision 1: ADD cross-channel ad-spend columns (UK + Google + Meta,
                          USD-consolidated, by ad type) INTO the Daily model.
                          Decision 4: marketing metrics stay in the Marketing Model ONLY.
                          Decision: agency data flows into the Daily model, ad-spend
                          agency-sliceable.
                          Deadline: two separate models by Fri 2026-07-24.
WHAT WAS ASSUMED          That decisions 1 and 4 were compatible. They are stated 4 lines apart.
EVIDENCE AVAILABLE        The transcript, which resolves the tension. It was not consulted.
NOT YET KNOWN             That the wiki would later compress A2 into "new fields in her daily
                          model = a hard no", which contradicts decision 1 and misstates the
                          client. R1 CONTRADICTION 3.
WHAT HAPPENED NEXT        The over-generalisation entered the architecture page and became the
                          constraint every later designer read.
```

`DOCUMENTED (R1 C-9..C-15, CONTRADICTION 3)`, `meeting-2026-07-22:17-19`, `:37-44`, `:53-58`.

**The honest constraint the evidence supports** — and which no document states — is:
*additions are welcome where they extend a concept the team already uses; additions are rejected
where they introduce vocabulary the team must be retrained on.* R1 derived it. Nothing in Delivery A
carries it.

---

### STEP A4 — The client sends the largest requirement artifact on the account, and it is never answered

<!-- anchor: step-a4 -->

```
TIME / ORDER              Workbook modified 2026-07-29. Analysed 2026-08-04.
WHAT THE CLIENT DID       Nicholas sent "Data Metrics for Advertising Dashboard - Multi-platform
                          APIS.xlsx" - 721 rows x 6 platform columns - with the verbatim note
                          "This table is all the advertising metrics I need ALDC to pull into
                          the data warehouse." He scoped 352 rows out himself. He promised a
                          second table - the dimensions list.
WHAT WAS DONE             A full gap analysis. A cover note. A DRAFT.
WHAT WAS NOT DONE         The reply was never sent. It sits under an explicit hold:
                          "do not send cover-note-draft.md until that lands."
                          The dimensions table has never arrived.
EVIDENCE AVAILABLE        Everything needed to reply.
NOT YET KNOWN             That a dimensional model would be designed while the client's own
                          dimension list remained entirely unspecified.
WHAT HAPPENED NEXT        Three candidate designs were produced anyway (STEP A8).
```

`DOCUMENTED (R1 C-16..C-19, C-37, O-8)`, `gap-analysis.md:3-8`, `:5`, `:11`, `:178-180`,
`cover-note-draft.md:3`.

⛔ **State this to a CEO plainly: the dimensional half of a dimensional model is, as of today,
entirely unspecified by the client, and the client is not aware we are waiting.** The reply that
would ask for it has been written and not sent.

---

### STEP A5 — Two consumers, two schemas, same object names

<!-- anchor: step-a5 -->

```
TIME / ORDER              Caught 2026-08-11 (GP-318). Origin earlier and NOT_RECORDED.
WHAT WAS BELIEVED         That the marketing dashboard and Power BI disagreed because of
                          semantics or caching.
WHAT WAS TRUE             Four objects were read UNQUALIFIED by the dashboard, resolving in the
                          connection's default schema WAREHOUSE_TEST_GP226 - "a second,
                          divergent copy of the same objects. PBI reads the REPORT_COMMON
                          copies, so the dashboard and PBI were fed by different definitions."
                          The GP226 MARKETING_EFFICIENCY copy MISSES Amazon US Sponsored
                          Display - $3,374.90.
WHAT WAS DONE             Four objects repointed and the reason written into the code, at
                          warehouse.ts:88-102.
WHAT WAS NOT DONE         Six objects the dashboard reads are STILL unqualified and still
                          resolve in the divergent schema.
NOT YET KNOWN AT THE TIME How many. R2 counted them on 2026-08-31: ten objects on the marketing
                          path have no repo-managed DDL at all, and five of those are read
                          unqualified.
WHAT HAPPENED NEXT        Nothing. The six remain. They are DEC-2 in the client review.
```

`DOCUMENTED (R2 §0, M18)`, `warehouse.ts:88-102`, `:1218`, `:1224`, `:1246`, `:1273`, `:1497`.

⭐ **This is the canonical wrong-source defect, and the estate's own global rule names it:**
*never infer the source from matching values.* Two objects held the same names and different
contents for an unrecorded period.

---

### STEP A6 — A recollection becomes a design law

<!-- anchor: step-a6 -->

```
TIME / ORDER              Before 2026-08-13. Exact origin NOT_RECORDED.
TRYING TO ACHIEVE         Decide which metrics appear on the Daily model and which on Marketing.
WHAT WAS BELIEVED         That Heather had asked for a "high-level vs low-level" split.
BASIS OF THE BELIEF       "a recollection of Heather's ask" - GP-319:183-184 - with the
                          implementing script's own docstring saying "confirm against the Avoma
                          transcript before this reaches Heather", marked NOT DONE.
WHAT WAS DONE             Engagement metrics (Impressions, Clicks, CTR, CPC, CPM, four quantity
                          measures and the Campaign table) hidden on Daily, visible on Marketing.
                          Recorded in Jira comment 36056 as settled.
WHAT THE AGENTS DID       Nothing; no agents.
EVIDENCE AVAILABLE        The transcript. On disk. Unread since 2026-07-08.
NOT YET KNOWN             That reading it would refute the premise.
WHAT HAPPENED NEXT        GP-318 section D9 REVERSED the hide on PROD-parity grounds - a
                          different and sound reason - and the measurement WIDENED the fix from
                          five objects to ten. The right action, for the wrong reason on file.
                          The phantom justification is still on the client record.
```

`DOCUMENTED (R1 §0.1, CONTRADICTION 1, O-12)`, `GP-319.md:170-184`, `GP-318.md:677-682`.

⭐ **The self-flagged confirmation was owed for weeks and cost one file-read to discharge.** The
document knew it was unverified and said so twice on two pages. Nothing turned that written
knowledge into an actionable obligation.

---

### STEP A7 — A client-agreed scope item is reversed, and the announcement is never made

<!-- anchor: step-a7 -->

```
TIME / ORDER              2026-08-13 (GP-318:214) and 2026-08-25 (GP-319:78).
WHAT WAS AGREED           2026-07-22, minuted: agency data flows into the Daily model.
WHAT WAS DECIDED          "Agency layer removed (Paul's call)"; then "no agency data in either
                          model, and Lectric is being removed."
WHY - AND IT IS A GOOD REASON
                          The Marketing Model is BLOCKED until Lectric is stripped at source.
                          Lectric carries $2.76M of sales with zero cost and zero ad spend.
WHAT IT DOES TO THE CLIENT'S NUMBERS
                          gross -2.13%, net -2.27%, and margin % and TACoS/MER both RISE.
                          GP-319:98 states the obligation in its own words: this "must be
                          announced, not discovered."
WHAT WAS DONE ABOUT THAT  Nothing is on file. Still nothing, as of 2026-09-01.
CLIENT RISK               A client opens the model, sees margin improve, and asks why. The
                          honest answer exists and has not been offered.
```

`DOCUMENTED (R1 C-11, CONTRADICTION 4)`, `GP-318.md:214`, `:216-218`, `GP-319.md:78`, `:96-98`.

---

### STEP A8 — Three designs are produced, and two documents recommend what the next day rejects

<!-- anchor: step-a8 -->

```
TIME / ORDER              2026-08-24 (two recommending docs) then 2026-08-25 (rejection).
WHAT WAS DONE 08-24       nicholas-metric-matrix-readout.md sec6 and attribution-design-
                          decision.md both conclude the shape is "one narrow conformed fact at
                          the core-10 grain" plus per-platform extension facts.
WHAT WAS DECIDED 08-25    GP-319 REJECTS a conformed core fact, with a specific reason: "This
                          client already carries ~14 copies of the marketing family across 6
                          schemas; a 15th worsens the canonical-object problem. Nothing is left
                          to conform."
WHAT WAS NOT DONE         Neither recommending document was marked superseded. Both are on disk.
                          Both are persuasive.
NOT YET KNOWN             Nothing - this was knowable on 2026-08-25. It simply was not written
                          down where the next reader would look.
WHAT HAPPENED NEXT        The trap is still armed. It has not yet fired, because D3 has not run.
```

`DOCUMENTED (R1 CONTRADICTION 7, L-2; R2 relevance)`, `GP-319.md:144-148`.

⛔ R1's verdict, verbatim: *"This is the single highest-risk trap for D3: a designer who finds those
two files first will build the thing GP-319 rejected the next day."*

---

### STEP A9 — The headline metric is written backwards in the document that locks it

<!-- anchor: step-a9 -->

```
TIME / ORDER              Origin NOT_RECORDED. Detected 2026-08-31 by R2.
WHAT THE DOC SAYS         ATTR:29 - "total spend / actual revenue"; ATTR:94 - MER = SPEND /
                          ACTUAL_SALES.
WHAT THE CODE SAYS        MARKETING_EFFICIENCY_MONTHLY.sql:50 - BLENDED_MER =
                          ACTUAL_SALES_GROSS_USD / SPEND_USD.
WHAT THE FRONTEND SAYS    FIELDS.md:38 and metrics.ts:16,:99 - SUM(totalSales)/SUM(spend).
AUTHORITATIVE             The code and the frontend, which agree with each other independently.
CONSEQUENCE               A ~5.0x MER and a ~0.2 MER are the same business fact. The document
                          and the running system disagree on which one the board sees.
```

`DOCUMENTED (R2 S2)`. R2's own verdict: *"the single highest-consequence STALE item."*

⚠ **Do not resolve this silently.** R1 and R2 both preserved the contradiction rather than picking
a side. That is correct and it must survive into the design phase.

---

### STEP A10 — The consumer layer fills the model's gaps with fabricated values

<!-- anchor: step-a10 -->

```
TIME / ORDER              Continuous. Measured by R2 on 2026-08-31.
WHAT WAS TRYING TO HAPPEN A dashboard rendering a field contract (types.ts + FIELDS.md) over a
                          warehouse that does not supply every field in it.
WHAT THE CODE DOES        dailyBudget: 0. budgetUsedPct: 0. timeInBudgetPct: 0.
                          status: "active" for EVERY campaign. orders: 0 on every product row.
                          sku renders the ASIN. platformCount = spend > 0 ? 1 : 0 - a boolean
                          wearing a count. conversions treated as 0 on brand/product/platform
                          rows because no REPORT_COMMON object carries the column.
                          FIELDS.md lists five SmartScout fields as "current" against no
                          Snowflake object that exists at all.
ROOT SHAPE                An absence rendering as a number. This is the exact failure class the
                          estate's own analysis gate forbids, shipped to a client surface.
CLIENT RISK               HIGH and quiet. Every one of these renders as a confident zero.
```

`DOCUMENTED (R2 M1..M17, M20)`, `warehouse.ts:867`, `:885`, `:942`, `:967`, `:1031-1034`.

---

### STEP A11 — Channel is jammed into the marketplace axis, and $244,870.44 falls off the report

<!-- anchor: step-a11 -->

```
TIME / ORDER              Origin NOT_RECORDED. Consequence recorded in the lineage doc.
WHAT WAS DONE             MARKETING_EFFICIENCY.sql:65 emits 'Cross-Channel' AS MARKETPLACE_NAME
                          for every Google/Meta row.
WHAT IT COSTS             That member is not a member of SHARED_DIM_MARKETPLACE. 768 rows /
                          $244,870.44 land on Power BI's unknown member and are UNSELECTABLE
                          BY ANY POSITIVE SLICER CHOICE.
WHAT THE RECORD ALREADY SAYS
                          navira-daily-model-lineage.md:215-224 - "Channel must leave the
                          marketplace axis."
WHAT WAS DONE ABOUT IT    Not yet done. The frontend contract already wants it split - Region
                          carries platform and name as two fields.
```

`DOCUMENTED (R2 M24)`.

**A quarter of a million dollars of spend is present in the warehouse and invisible in the report.**
That is the sentence a CEO needs; the mechanism is a dimension-member mismatch.

---

### STEP A12 — The brand vocabulary splits three ways and drops the top spender

<!-- anchor: step-a12 -->

```
TIME / ORDER              Detected 2026-07-14 and 2026-08-31.
WHAT WAS TRUE             MARKETING_EFFICIENCY_PRODUCT.BRAND comes from
                          SHARED_DIM_PRODUCT_BASE.BRAND. The dashboard resolves brand from
                          SHARED_DIM_MARKETPLACE.DEFAULT_VENDOR. Those are two different
                          vocabularies, and the app derives a third in TypeScript.
WHAT IT COST              The old MARKETING_EFFICIENCY_PRODUCT.BRAND aggregation "silently
                          dropped ~31% of Amazon ad spend - including the #1 spender TF
                          Publishing." Separately, a direct PRODUCT_ID = ASIN join matched
                          almost nothing and the old code COALESCE'd to BRAND, "leaving ~27% of
                          cards with an empty Top-products section + a dead drill-down."
WHAT EXISTS TODAY         A SKU<->ASIN bridge rebuilt PER REQUEST in the application from a
                          TRAFFIC fact, load-bearing for three views, and tested by nothing.
```

`DOCUMENTED (R2 M9, M13a, S9)`, `warehouse.ts:1303-1343`, `:1396-1399`.

---

## A.2 Delivery B — the Factory mission, measured

All timestamps UTC, `MEASURED` from `.data/tasks.jsonl`, `.data/claims/*.json` and
`.data/credential-use.jsonl` in this session.

---

### STEP B1 — The premise handed to the mission is corrected before it is planned against

<!-- anchor: step-b1 -->

```
TIME / ORDER              2026-08-31, spec authoring, before any task existed.
TRYING TO ACHIEVE         Run one bounded real mission "using Agent Factory's existing
                          mission/task/DAG/state/claim mechanisms" (ChatGPT revision 1).
WHAT WAS MEASURED         grep -rn --include=*.py -iE '\bmission\b' factory/  -> no matches
                          grep -rn --include=*.py -iE 'depends_on' factory/   -> no matches
FINDING                   "That names two things that do not exist." board.DEPENDS is a GATE
                          dependency map, not a task DAG. lanes.py validates lane gate ids
                          against readiness.GATES at import, so "Snowflake Cartographer" cannot
                          be a lane.
WHAT WAS DONE INSTEAD     TaskStore was identified as already supplying the needed shape -
                          parent/child hierarchy, block/unblock edges, five states, typed
                          evidence with validated basis, and close(require=...) raising
                          EvidenceRequired. "Nothing new is built."
SECOND CORRECTION         The subject is NAVIRA, not "GEP". GEP is the Jira project and the
                          contracting client; Navira is the modelled entity. Without this, R2
                          and R3 would have searched for the wrong object names.
THIRD CORRECTION          ChatGPT's task B ("repo + wiki reconstruction") was already
                          substantially done - two wiki pages written 2026-08-30. B was
                          rescoped from RECONSTRUCT to READ-AND-DIFF.
```

`DOCUMENTED (spec sec 0.1-0.5)`. ⭐ **Three inherited premises corrected before a single task ran.**
Cost: one spec section. This is the highest-return event in either delivery.

---

### STEP B2 — Both load-bearing guards are watched refusing, BEFORE the work they guard

<!-- anchor: step-b2 -->

```
TIME / ORDER              2026-08-31, pre-mission.
WHY                       Spec sec 5: "a guard first exercised during the work it is guarding has
                          not been tested, it has been trusted."
NEGATIVE CONTROL 1        A second claim on res-mission-artifacts while the first is held.
                          WATCHED REFUSING: "res-mission-artifacts is already running as pid
                          2984... Starting a second one would put two agents on the same file,
                          and the loser's work disappears without an error."
NEGATIVE CONTROL 2        Closing a task with no usable evidence.
                          WATCHED REFUSING: "EvidenceRequired: task 2b9aae3b cannot close as
                          done: no MEASURED or DERIVED evidence attached (0 assumed-only
                          item(s))" - and the refused close APPENDED NOTHING (205 rows before
                          and after).
FIRST ATTEMPT FAILED, AND THE FAILURE IS THE LESSON
                          The first claim attempt used a PYTHON pid, got HELD-GONE, and the
                          second claim was granted. That reads as "the detector is inert" and it
                          is not: sessions._running_pids() enumerates claude.exe only, so
                          HELD-GONE was the correct answer to the wrong question.
```

`DOCUMENTED (spec sec 5, sec 5.1)`. ⭐ **A plausible wrong answer was produced by the estate's own
tooling and was caught by re-running unchained.** This is the shape the global CLAUDE.md warns about,
met again.

---

### STEP B3 — A credential is exposed by a deny-list over a markdown table

<!-- anchor: step-b3 -->

```
TIME / ORDER              2026-08-31, extracting Snowflake account details from the vault.
WHAT WAS DONE             Filtered with a DENY-LIST: drop lines containing "password".
WHY IT FAILED             The vault stores credentials in MARKDOWN TABLES. The word "password"
                          is in the header row and never in the data rows. Three plaintext
                          values passed straight through.
BLAST RADIUS              paulrussell - THE SAME PASSWORD IS LISTED FOR og35375 NON-PROD AND
                          wj66376 PRODUCTION. Highest severity.
                          TEST_DG1_CORE_ADMIN - non-prod.
                          MIKESTUARTADMIN - non-prod, issued WITHOUT MFA.
CONTAINMENT               Values were NOT repeated into the checkpoint or any commit. The
                          exposure was ~message 90; a session manager indexes the first ~500
                          chars of the first ~16 messages into a searchable FTS table, and
                          DELETION DOES NOT STICK. So probably outside the window. "Probably is
                          not verified."
THE RULE THAT PREVENTS IT ALLOW-LIST the columns you want (account, user). Never deny-list the
                          ones you do not. A deny-list over free text is a guard only as wide as
                          the relation it derives over.
WHAT MAKES IT SHARP       This is the SAME defect class fixed in readiness.py (F91) that same
                          morning, violated against a credential file that afternoon.
STATUS                    Rotation NOT CONFIRMED. Finding NOT FILED.
```

`DOCUMENTED (checkpoint sec 1)`. ⭐ **The rule went on to become rule 1 of `factory/client_review.py`
within 24 hours** — the module's docstring cites this exact incident as the reason `client_safe()`
is an allow-list. `MEASURED` — I read the docstring.

---

### STEP B4 — The read-only failsafe is found unable to pass, before it is run

<!-- anchor: step-b4 -->

```
TIME / ORDER              2026-08-31, R3 pre-flight design.
THE FAILSAFE AS WRITTEN   Spec sec 2.1 step 1: prove read-only by ATTEMPTING A SCOPED WRITE AND
                          WATCHING IT REFUSED. "A role assumed read-only is an assumption; a
                          role watched refusing a write is a measurement."
THE PROBLEM               snowflake-admin-nonprod is an ADMIN account. It will not refuse.
                          The failsafe cannot pass as written, in TEST or in PROD.
WHAT WAS NOT DONE         Running it anyway and reporting the result as a read-only proof.
                          Spec text: "That is the vacuous-verification shape this repo has now
                          met nine times."
WHAT WAS DONE             Two honest routes put to a human. Paul chose route 1: create a
                          read-only role + user in og35375 so the role STRUCTURALLY refuses.
OUTCOME                   R3 blocked on a human action. Correctly blocked.
```

`DOCUMENTED (checkpoint sec 3, handoff sec 3)`. ⭐ **A verification was refused for being vacuous
before it produced a false green.** The credential retrieval that did happen is logged — exactly one
row, `2026-09-01T01:47:31Z`, task R3, access READ, purpose *"shape only, value never printed. No
Snowflake connection made yet."* `MEASURED` from `.data/credential-use.jsonl`.

---

### STEP B5 — The mission is materialized: 9 tasks, 7 dependency edges, one write

<!-- anchor: step-b5 -->

```
TIME                      2026-09-01T00:52:14Z. All 16 events within 4 milliseconds.
                          MEASURED from .data/tasks.jsonl.
WHAT WAS CREATED          Mission task 0d26cd2f, and eight children:
                          R1 2b9aae3b  R2 3d053975  R3 e397be46
                          D1 1785f5a9  D2 933e6c33  D3 387780b5
                          D4 b1f38c1c  D5 91088e54
DEPENDENCY EDGES          7 block events: D1 blocked by R1, R2, R3; D2 by D1; D3 by D2;
                          D4 by D3; D5 by D4.
CONTRACTS                 .data/missions/marketing-model-reconstruction-v1.json carries, per
                          task: resource_claim, access, capability_class, estimate_minutes,
                          estimate_basis, model, effort, evidence_required, expected_output.
                          ALL EIGHT carry estimate_basis: ASSUMED and model: claude-opus-5,
                          effort: max.
WHAT WAS DELIBERATELY NOT DONE
                          No model routing. "The point of run #1 is to RECORD model and effort
                          per task alongside duration, retries and outcome. Routing optimised
                          before that data exists is a guess wearing a policy's clothes."
```

`MEASURED`. ⭐ **capability_class is the durable field; model is the record of what ran.** A contract
naming `claude-opus-5` rots at the next model release; one naming `DEEP` survives it.

---

### STEP B6 — A search filters the wrong field, returns a false zero, and two duplicate tasks are created

<!-- anchor: step-b6 -->

```
TIME                      2026-09-01T02:13:52Z - 81 minutes and 38 seconds after the tasks it
                          could not find were created. MEASURED.
WHAT WAS BELIEVED         "The mission plan was not materialized into the task store."
WHAT WAS DONE             Searched r.get('task') - THE TASK ID - for the string "R1".
                          It should have searched the title.
WHY THE ZERO LOOKED REAL  Task ids are hex (2b9aae3b). No id contains "R1". The search returned
                          zero and the zero was reported as a finding.
CONSEQUENCE               Two duplicate tasks created: fbe2ea4c (R1) and 200deda2 (R2), both
                          correctly parented to the mission, both with NO dependency edges.
WHAT WAS TRUE ALL ALONG   All eight tasks existed, correctly parented, with a fully wired DAG.
                          25 block events existed.
THE RULE THAT WOULD HAVE CAUGHT IT
                          The repo's own: a zero from an instrument you have not shown can see
                          is not a measurement. A positive control - searching for a title you
                          KNOW exists - costs seconds.
WHEN IT WAS CAUGHT        2026-09-01T03:14:03Z. 3,611 seconds later. DERIVED from the two
                          event timestamps.
```

`MEASURED`. ⭐ **This is the blind-instrument defect, committed on the day six of them were fixed.**

---

### STEP B7 — Wave 1 runs: two of three tasks, 43KB and 44KB of cited evidence

<!-- anchor: step-b7 -->

```
CLAIMS GRANTED            2026-09-01T02:14:04Z - three resource claim files written 5ms apart:
                          res-gep-evidence (R1), res-wiki (R2), res-clients-repo (R2).
                          MEASURED from .data/claims/.
EVIDENCE ATTACHED         2026-09-01T02:25:21Z - both R1 and R2, basis MEASURED, evidence_class
                          TARGET, then closed done. MEASURED.
WALL CLOCK                11 minutes 17 seconds from claim to evidence, for both tasks in
                          parallel. DERIVED (02:25:21 minus 02:14:04).
ESTIMATE                  45 minutes each, basis ASSUMED. DOCUMENTED.
OUTPUT                    R1 43,110 bytes; R2 43,901 bytes. MEASURED via wc -c.
WHAT R1 ESTABLISHED       38 claims with basis, 7 contradictions, 18 locked decisions verified,
                          15 open client questions.
WHAT R2 ESTABLISHED       14 LOCKED, 11 STALE, 23 MISSING, 8 prior-art patterns.
R3                        Never claimed. Never started. Status open, blocked on the human
                          access decision from STEP B4.
```

⚠ **The wall-clock figure is honest but weak, and must be labelled so in the artifact.** Both close
events were written by the mission-manager in the same batch, 0.4ms apart — so 11m17s is the wall
clock of the *recording*, not a measurement of either task's own duration. **`actual_minutes` is
`NOT_RECORDED` for every task in this mission.** The instrumentation table in spec §4 lists thirteen
fields to record per task; **none of them was written anywhere.** See ISSUE M-09.

---

### STEP B8 — The correction, and the two claims of my own that measurement refuted

<!-- anchor: step-b8 -->

```
TIME                      2026-09-01T03:14:03Z. MEASURED.
WHAT WAS DONE             Evidence re-attached to the REAL R1 (2b9aae3b) and R2 (3d053975);
                          both closed done. Both duplicates annotated with an evidence row:
                          "SUPERSEDED - duplicate created in error... Created because a search
                          filtered the task ID instead of the title and returned a false zero."
WHY ANNOTATE, NOT DELETE  TaskStore is append-only. The store cannot be rewritten. The
                          correction is a new event, not an erasure.
SECOND REFUTED CLAIM      "Ticket-level blocked_by is unused" - TRUE when first observed (all
                          189 events carried an empty blocked_by), FALSE now (25 block events
                          exist). It had already propagated into the leads table of
                          docs/specs/client-review-loop-v0.md, which needs that row corrected.
WHO CAUGHT IT             Paul challenged it. DOCUMENTED - handoff sec 0.2: "Paul was right to
                          challenge it."
```

`MEASURED` for the events; `DOCUMENTED` for the attribution.

⛔ **What was NOT corrected, and I measured this in this session:** the R1 artifact's own header
still reads *"Task: `fbe2ea4c`"* and R2's reads *"task `200deda2`"* — **both artifacts name the
superseded duplicate as their provenance.** The task store was corrected; the artifacts it points at
were not. See ISSUE M-02.

---

### STEP B9 — A client-facing review is authored over the mission state, and grounded in code

<!-- anchor: step-b9 -->

```
TIME                      2026-08-31 / 2026-09-01 (Session 3, concurrent).
WHAT WAS BUILT            factory/client_review.py (29.5 KB) + client_review_render.py, and an
                          authored narrative at missions/client-review-v1/reviews/
                          navira-marketing-model.yaml (262 lines).
THREE RULES, EACH FROM A PAID-FOR FAILURE
                          1. The client boundary is an ALLOW-list, never a deny-list -
                             citing the STEP B3 credential exposure by name.
                          2. A guarded word (VERIFIED, DEPLOYED, ACCEPTED, HEALTHY, ON TRACK)
                             is refused unless its evidence resolves on disk AND a task-evidence
                             row carries a basis in evidence.USABLE. It degrades to CLAIMED -
                             not silently dropped, not silently promoted.
                          3. Absence is four things and they never collapse: LIVE /
                             LAST_VERIFIED / STALE / UNAVAILABLE.
THE FIELD THAT MATTERS MOST
                          origin: CLIENT vs FACTORY_PROPOSED, on every delivered item, decision
                          and risk. The yaml says why: "R1 found that most of the 'design' in
                          the record is ALDC-authored rather than client-requested, so
                          conflating the two is the specific failure this field prevents."
WHAT IT PRODUCED          2 open decisions (1 blocking), 3 risks (1 HIGH), 6 next steps with
                          dependencies, acceptance READY_FOR_REVIEW.
```

`MEASURED` (module docstring, yaml contents, line count).

---

# B. Master issue / mistake table

<!-- anchor: sec-b -->

Two blocks: Delivery A (client work, `H`) and Delivery B (Factory mission, `M`).
`Interception type` values: `WOULD_BLOCK` · `WOULD_INTERCEPT` · `WOULD_WARN` ·
`WOULD_PROVIDE_CONTEXT` · `MAY_REDUCE_LIKELIHOOD` · `NO_EFFECT` · `NOT_YET_KNOWN`.

## B.1 Delivery A — the client work

| # | Stage introduced | Issue | What happened | Why it happened | Root cause | Evidence available at the time? | Detection stage | Downstream impact | Rework / delay | Client risk | AF capability | Interception type | Ideal interception stage | Evidence |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **H1** | Internal decision (pre 08-13) | Metric-visibility boundary rests on a recollection the transcript does not contain | Engagement metrics hidden on Daily, visible on Marketing; recorded in Jira 36056 as settled | A remembered ask was written into the record as a requirement; the doc flagged it unconfirmed and nothing acted on the flag | `UNVERIFIED_ASSUMPTION` + `MISSING_VERIFICATION` + `HUMAN_MEMORY_DEPENDENCY` | **YES** — the transcript was on disk and unread | R1, 2026-08-31 (8 weeks) | Shaped the model; the fix already shipped for a different reason (GP-318 D9), so the *action* is right and the *record* is wrong | `NOT_RECORDED` | **HIGH** — a phantom client requirement stands on the client's own ticket | Typed Claims + Evidence requirements | `WOULD_INTERCEPT` | At the moment the claim entered the record | R1 §0.1, CONTRADICTION 1; `GP-319.md:183-184` |
| **H2** | Design (2026-08-24/25) | Two ALDC docs recommend a conformed core fact rejected the next day; neither marked superseded | Both read as current on disk | No supersession mechanism over documents | `DOCUMENTATION_DRIFT` + `CONTRADICTORY_SOURCES` | **YES** — the rejection is dated one day later | R1, 2026-08-31 | Trap armed for D3; **has not yet fired** | 0 so far | **HIGH if it fires** — would build a 15th copy of a family that already has ~14 across 6 schemas | Contradiction detection + Organizational Memory | `WOULD_WARN` | At the rejection (08-25) | R1 CONTRADICTION 7; `GP-319.md:144-148` |
| **H3** | Documentation | MER written inverted (`SPEND/SALES`) in the doc that locks it | Doc and running system disagree on the board headline | A formula typed once, never cross-checked against the implementation | `DOCUMENTATION_DRIFT` + `SEMANTIC_CONTRACT_GAP` | **YES** — code and frontend both readable and agreeing | R2, 2026-08-31 | Anyone specifying from the doc inverts the headline metric | `NOT_RECORDED` | **HIGH** — 5.0x vs 0.2 for the same fact | Semantic Contracts | `WOULD_INTERCEPT` | At doc authoring, by a definition-vs-implementation check | R2 S2; `ATTR:29,:94` vs `_MONTHLY.sql:50` |
| **H4** | Implementation | Four objects read unqualified, resolving in a divergent schema copy | Dashboard and PBI fed by different definitions of the same names | Default-schema resolution; no qualification convention enforced | `WRONG_SOURCE_OR_POPULATION` + `ENVIRONMENT_DRIFT` | Partially — required a probe, not a read | GP-318, 2026-08-11 | Corrected for 4; **6 still divergent** | 1 corrective pass, ongoing | **HIGH** — the GP226 copy misses $3,374.90 of Amazon SD spend | Source Cartography | `WOULD_INTERCEPT` | Before the first query against an unqualified name | R2 §0; `warehouse.ts:88-102` |
| **H5** | Implementation | Ten marketing-path objects have no repo-managed DDL; five read unqualified | The newest cross-channel features sit entirely on objects undefined in source control and in the divergent schema | Objects created outside the repo-managed path (`aldc-launchpad` scripts) | `MISSING_PROVENANCE` + `ENVIRONMENT_DRIFT` | **YES** — a grep would have found it any day | R2, 2026-08-31 | No rollback, no review, no lineage for the newest features | `NOT_RECORDED` | **HIGH** — unreviewable production dependencies | Source Cartography + Provenance | `WOULD_WARN` | At first reference from repo-managed code | R2 M18 |
| **H6** | Documentation | Gap table says "no view joins spend to actual sales — the real missing piece"; the view exists and is canonical | A snapshot from before Phase 1 shipped, never re-baselined | `STALE_CONTEXT` + `DOCUMENTATION_DRIFT` | **YES** — the phase table 30 lines lower already marks Phase 1 satisfied | R2, 2026-08-31 | A design pass would re-specify existing work | 0 so far | MEDIUM — wasted build | Contradiction detection | `WOULD_WARN` | At Phase 1 close | R2 S1; `ATTR:53` vs `MARKETING_EFFICIENCY.sql:108-152` |
| **H7** | Documentation | "Meta dropped" stated three times inconsistently in one page while Meta shipped | Reader stopping at the Decisions block concludes Meta is out of scope | Superseded statements never struck | `DOCUMENTATION_DRIFT` | **YES** — same page corrects itself 80 lines later | R2, 2026-08-31 | Scope misread | 0 so far | MEDIUM | Contradiction detection | `WOULD_WARN` | At the 2026-06-09 correction | R2 S3 |
| **H8** | Documentation | Meta spend has three values in one doc ($8,158 / $6,667 / $14,668), none with a window or as-of date | None is publishable as written | Figures typed without their basis | `MISSING_PROVENANCE` | **YES** | R2, 2026-08-31 | Any quoted Meta total is unsafe | 0 | **HIGH if published** — this is the FU92-420 shape | Evidence requirements (basis-per-figure) | `WOULD_BLOCK` | At the moment each figure was written | R2 S4 |
| **H9** | Documentation | The proposed spine grain and all five proposed column names do not exist | A design reusing them ships a wrong-object-name spec | Doc written ahead of build and never reconciled | `DOCUMENTATION_DRIFT` + `SEMANTIC_CONTRACT_GAP` | **YES** | R2, 2026-08-31 | Exactly the failure the mission was warned about | 0 so far | MEDIUM | Semantic Contracts | `WOULD_INTERCEPT` | At build, by reconciling emitted columns to the spec | R2 S6 |
| **H10** | Implementation | `COALESCE(FX.RATE, 1)` treats a missing rate as parity | A missing GBP rate makes £1 = $1 with no signal | Defensive coalesce with no absence channel | `SEMANTIC_CONTRACT_GAP` | **YES** | R2, 2026-08-31 | Silent currency error | `NOT_RECORDED` | **HIGH** — an absence rendering as a number, on money | Semantic Contracts (absence typing) | `WOULD_INTERCEPT` | At code review | R2 S5 |
| **H11** | Implementation | Three brand vocabularies; the warehouse aggregation silently dropped ~31% of Amazon ad spend including the #1 spender | Brand totals wrong; ~27% of cards had an empty top-products section and a dead drill-down | No conformed brand dimension on the marketing path | `WRONG_SOURCE_OR_POPULATION` + `SEMANTIC_CONTRACT_GAP` | Partially — required a coverage probe | 2026-07-14 / R2 2026-08-31 | Fixed in the app by an ad-hoc crosswalk, not in the model | ≥1 fix pass | **HIGH** — client-visible wrong totals | Semantic Contracts + Typed Claims (coverage) | `WOULD_WARN` | At the first brand aggregation | R2 M9, S9, M13a |
| **H12** | Implementation | Channel jammed into the marketplace axis; 768 rows / $244,870.44 orphaned onto PBI's unknown member | Spend present in the warehouse and unselectable in the report | A relabel that creates a non-member of the dimension | `SEMANTIC_CONTRACT_GAP` | **YES** — the lineage doc records it | Lineage doc; re-surfaced by R2 | Cross-channel spend invisible to any positive slicer choice | Not yet fixed | **HIGH** — a quarter of a million dollars missing from a report | Semantic Contracts + Task DAG validation | `WOULD_INTERCEPT` | At the relabel | R2 M24; `navira-daily-model-lineage.md:215-224` |
| **H13** | Implementation | Campaign type derived by positional string split; no parse-status column | 97.2% classify; 2.8% legacy plus **all** Google/Meta return null, and a malformed row still parses | Parsing a business attribute out of a free-text name | `SEMANTIC_CONTRACT_GAP` + `MISSING_PROVENANCE` | **YES** — the dimensional-model doc names this exact hazard and prescribes `taxonomy_parse_status` | R2, 2026-08-31 | Silent misclassification | `NOT_RECORDED` | MEDIUM | Semantic Contracts | `WOULD_WARN` | At the parse | R2 M8; `DIM:403-407` |
| **H14** | Semantic model | 16 visible ROAS measures, no stated default | "An Excel user picks one at random and gets an answer defensible in isolation and irreconcilable with a colleague's" | Measures added incrementally with no canonical designation | `SEMANTIC_CONTRACT_GAP` + `MISSING_TASK_OR_DEPENDENCY` | **YES** | GP-319, 2026-08-25 | Named as one of two human decisions gating the Tier-0 build | Blocks build | **HIGH** — irreconcilable numbers between colleagues | Human Attention Router + Client Review | `WOULD_BLOCK` | At the second ROAS measure | R1 O-1 |
| **H15** | Consumer layer | Contracted fields fabricated: `dailyBudget:0`, `status:"active"` for every campaign, `orders:0`, SKU renders the ASIN, `platformCount` is a boolean | Confident zeros and defaults on a client surface | The field contract outruns the warehouse and the app fills the gap | `SEMANTIC_CONTRACT_GAP` + `MISSING_VERIFICATION` | **YES** — every one is a literal in the code | R2, 2026-08-31 | The client reads fabricated values as measurements | `NOT_RECORDED` | **HIGH and quiet** | Semantic Contracts + Continuous acceptance | `WOULD_BLOCK` | At contract-to-source reconciliation | R2 M1–M17 |
| **H16** | Scope | A client-agreed scope item (agency in Daily) reversed with no announcement, while client-visible ratios move | Margin % and TACoS/MER both rise; GP-319 itself says this "must be announced, not discovered"; nothing on file | The reversal had a sound technical reason and no communication obligation attached to it | `COMMUNICATION_FAILURE` + `MISSING_TASK_OR_DEPENDENCY` | **YES** — the obligation is written on the same page | Still open | Client may discover a ratio movement unannounced | Still owed | **HIGH — reputational** | Client Review + Human Attention Router | `WOULD_BLOCK` | At the reversal | R1 CONTRADICTION 4; `GP-319.md:96-98` |
| **H17** | Ticket state | GP-296 listed as "the last blocker on correctness sign-off" on two pages while refuted (delta $0.00) on 2026-08-12 | A fresh reader inherits a stale blocker | Refutation recorded; the blocking statements were never retracted and the ticket never closed | `STALE_CONTEXT` + `KNOWLEDGE_AVAILABLE_BUT_NOT_CONSUMED` | **YES** — same page, 250 lines apart | R1, 2026-08-31 | Design work treated as blocked when it is not | `NOT_RECORDED` | MEDIUM | Contradiction detection | `WOULD_WARN` | At the refutation | R1 CONTRADICTION 5 |
| **H18** | Cross-layer | "Purchases is absent" stated flatly in three artifacts describing three different layers, with no cross-reference | Landed and populated in prod (26,388 rows, 68% coverage) and discarded at the view layer | Each artifact was right about its own layer and none named its layer | `SEMANTIC_CONTRACT_GAP` + `MISSING_PROVENANCE` | **YES** | R1, 2026-08-31 | A designer reading the first scopes pipeline work that does not exist | 0 so far | MEDIUM — wasted build | Semantic Contracts (layer-qualified claims) | `WOULD_WARN` | At the second statement | R1 CONTRADICTION 6 |
| **H19** | Client comms | The client's 721-row requirement doc has an analysed reply that was never sent; the promised dimensions table never arrived | The dimensional half of a dimensional model is unspecified, and the client does not know we are waiting | A hold with no expiry and no owner | `MISSING_TASK_OR_DEPENDENCY` + `COMMUNICATION_FAILURE` | **YES** | R1, 2026-08-31 | **Any dimensional design** | Ongoing | **HIGHEST — commercial** | Intent Contract + Human Attention Router | `WOULD_BLOCK` | At the hold | R1 C-19, C-37, O-8 |
| **H20** | Documentation | `FIELDS.md` lists five SmartScout fields as "current" against no Snowflake object that exists at all | Contract doc drifted from the type definition it was transcribed from | `DOCUMENTATION_DRIFT` | **YES** | R2, 2026-08-31 | Contract promises what nothing supplies | 0 | MEDIUM | Semantic Contracts | `WOULD_INTERCEPT` | At the `types.ts` change | R2 M12 |
| **H21** | Semantic model | `ISCROSSFILTERED` used where `ISFILTERED` was required; blanked every ordinary date pivot | Propagation vs adjacency | `KNOWLEDGE_NOT_AVAILABLE` | No — this had to be learned | GP-318, 2026-08-17 | Two failed fix passes | **2 fix passes** | MEDIUM | Known-Failure Preflight | `WOULD_PROVIDE_CONTEXT` (first time) / `WOULD_INTERCEPT` (recurrence) | Second occurrence | R1 L-16 |
| **H22** | Semantic model | A platform allow-list living inside a DAX literal, invisible at the field list and in the relationship graph | Read downstream as a data defect | `MISSING_PROVENANCE` | **YES** in principle | GP-319 | **Three sessions chased it as a data defect** | 3 sessions | MEDIUM | Provenance + Organizational Memory | `WOULD_PROVIDE_CONTEXT` | Second session | R1 L-6 |
| **H23** | Documentation | The model-review call dated 2026-07-08 in two places and "2026-08" in a third | A measurement contract motivates its window ambiguity from a call it dates a month late | `DOCUMENTATION_DRIFT` | **YES** | R1, 2026-08-31 | Low blast radius, high credibility cost | 0 | LOW–MEDIUM | Contradiction detection | `WOULD_WARN` | At authoring | R1 CONTRADICTION 2 |
| **H24** | Implementation | Source precedence enforced by a hand-maintained `PLATFORM_ID IN (...)` literal | Fails **silently and doubly** if a feed moves between the base fact and `_PREPROD` | The correct control (an anti-join on the natural key) already ships in FUSION_92 | `KNOWLEDGE_AVAILABLE_BUT_NOT_CONSUMED` | **YES** — in a sibling client's repo | R2, 2026-08-31 | Latent silent double-count | 0 so far | **HIGH if it fires** | Organizational Memory + Delivery Recipes | `WOULD_PROVIDE_CONTEXT` | At the union's authoring | R2 P1, M22 |
| **H25** | Consumer layer | The SKU↔ASIN bridge is rebuilt per request in the app, not a warehouse object; three views depend on it; nothing tests it | Load-bearing infrastructure outside the model and outside test | A workaround that worked and was never promoted | `SYSTEM_DESIGN_GAP` + `MISSING_VERIFICATION` | **YES** | R2, 2026-08-31 | If the traffic fact's coverage shifts, three views move silently | `NOT_RECORDED` | **HIGH** | Task DAG validation + Reliability instrumentation | `WOULD_WARN` | At the workaround | R2 M13a |

## B.2 Delivery B — the Factory mission

| # | Stage introduced | Issue | What happened | Why it happened | Root cause | Evidence available at the time? | Detection stage | Downstream impact | Rework | Client risk | AF capability | Interception type | Ideal interception stage | Evidence |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **M-01** | Mission materialization check | A search filtered the task **ID** for "R1" instead of the title; the zero was reported as a finding | Two duplicate tasks created (`fbe2ea4c`, `200deda2`), each with no dependency edges | No positive control on a search that returned zero | `INSTRUMENTATION_GAP` + `MISSING_VERIFICATION` + `REPEATED_FAILURE_NOT_LEARNED_FROM` | **YES** — a positive control costs seconds | Self-caught, 3,611s later (MEASURED) | Wave 1 ran under duplicate ids; evidence landed on the wrong tasks; the artifacts still carry the wrong ids (M-02) | 1 correction pass; both duplicates annotated SUPERSEDED | LOW — internal only | Known-Failure Preflight + Provenance | `WOULD_INTERCEPT` | At the search, by requiring a positive control before a zero is actionable | `.data/tasks.jsonl` events @02:13:52Z and @03:14:03Z |
| **M-02** | Artifact authoring | **Both evidence artifacts name the superseded duplicate as their own provenance** — R1 header says task `fbe2ea4c`, R2 says `200deda2` | The store was corrected; the artifacts were not | The correction was applied to the mutable-by-append store and not propagated to the immutable prose | `MISSING_PROVENANCE` + `MANUAL_HANDOFF` | Yes, at correction time | **This session, 2026-09-01. Not previously recorded.** | An auditor tracing R1's provenance lands on a task annotated SUPERSEDED | 2 header edits | LOW | Provenance (bidirectional) | `WOULD_INTERCEPT` | At the SUPERSEDED annotation | `R1:3`, `R2:3` vs `.data/tasks.jsonl` |
| **M-03** | Inherited context | Metric hierarchy inherited as *Contribution Margin > MER > Platform ROAS* | Propagated into R2's own prompt **marked "verify"**; came back **REFUTED**; corrected order is MER (headline) → Contribution Margin (Tier 3.5, coverage-gated) → Platform ROAS | Inherited from a prior thread with no provenance | `STALE_CONTEXT` — **handled correctly** | Yes | R2, by design | **None.** It never became mission knowledge | 0 | NONE | Typed Claims (already exercised, manually) | `WOULD_INTERCEPT` — and effectively did, by hand | At inheritance | Handoff §2; R2 L3 |
| **M-04** | Prior observation | "Ticket-level `blocked_by` is unused" — true when observed (189 events, all empty), false later (25 block events) | Propagated into the leads table of `docs/specs/client-review-loop-v0.md` | A true observation with no expiry, carried forward as a standing fact | `STALE_CONTEXT` + `MISSING_PROVENANCE` | Not at observation time; yes later | **Paul challenged it** | One filed spec carries a wrong row | 1 row correction, **still owed** | LOW | Typed Claims (observation + as-of) | `WOULD_WARN` | At re-use in a second document | Handoff §0.2 |
| **M-05** | Credential extraction | A **deny-list** over a markdown credential table let three plaintext passwords into a session transcript; one spans non-prod **and production** | Values reached a transcript indexed by a session manager whose deletion does not stick | A guard only as wide as the relation it derives over | `SEMANTIC_CONTRACT_GAP` + `REPEATED_FAILURE_NOT_LEARNED_FROM` | **YES** — the identical defect class (F91) was fixed that same morning | Self-caught same session | **Rotation not confirmed. Finding not filed.** | Rotation owed | **HIGH — security** | Known-Failure Preflight | `WOULD_BLOCK` | Before the extraction, by refusing deny-list filters over credential sources | Checkpoint §1 |
| **M-06** | R3 pre-flight design | The read-only failsafe **cannot pass as written** — the account is admin and will not refuse a write | Caught before running; two honest routes put to a human; route 1 chosen | The spec assumed a role it did not verify | `UNVERIFIED_ASSUMPTION` — **caught pre-execution** | Yes | Pre-execution, by reading the spec against the credential | R3 blocked. **Correctly.** | Human action owed | NONE — this is the control working | Evidence requirements + Human Attention Router | `WOULD_BLOCK` — and effectively did | Pre-execution | Checkpoint §3 |
| **M-07** | Scope handoff | **Spec §0.5 put `aldc-launchpad/docs/readouts/` in R2's scope; R2's method note records `aldc-launchpad` as NOT-VISIBLE and outside its read scope.** Nothing reconciled the two | The three existing GP-319 designs were read by neither worker (R1 grepped the HTML, did not read it) | A scope instruction in prose, with no acknowledgement channel and no completeness check | `MANUAL_HANDOFF` + `MISSING_VERIFICATION` + `SEMANTIC_CONTRACT_GAP` | **YES** — the spec said it explicitly and warned that missing it would be "a blind instrument" | **This session, 2026-09-01. Not previously recorded.** | R2's prior-art section covers FUSION_92 (8 valuable patterns) but **not the three designs the spec named**. D3 will open them cold | R2 scope extension owed | MEDIUM — D3 may re-derive existing designs | **Typed Handoff + ACK/NACK** | `WOULD_BLOCK` | At dispatch, by requiring the worker to ACK or NACK each scope item | Spec §0.5 vs R2 "Method note" |
| **M-08** | Execution | **Acceptance check 1 is not satisfied by the record.** It requires "three `task_claim` grants, three concurrent sessions"; three claim files exist but **all carry pid 17172 and actor `mission-manager`** — one process — and **R3 never claimed at all** | Parallelism was asserted in the spec and not demonstrated by the store | `INSTRUMENTATION_GAP` + `MISSING_VERIFICATION` | Yes | **This session, 2026-09-01. Not previously recorded.** | The mission's headline claim ("three tasks ran in parallel") is **unproven** — and the spec itself says checks 1, 2 and 5 "can pass over an absence" | Re-run or re-word | LOW internal, **HIGH if published** | Reliability instrumentation | `WOULD_BLOCK` | At claim time, by requiring a distinct `claude.exe` pid per claim | `.data/claims/*.json`, all pid 17172 |
| **M-09** | Instrumentation | **The routing dataset — the stated point of run 1 — was not captured.** Spec §4 lists 13 per-task fields; none is written anywhere. `estimate_minutes` exists (all `ASSUMED`); `actual_minutes` does not exist | The instrument was specified in prose and never built | `INSTRUMENTATION_GAP` + `MISSING_TASK_OR_DEPENDENCY` | Yes | **This session** | Run 1 cannot answer whether `capability_class` predicted difficulty — the one honest thing it could have produced about routing | Instrument build owed before run 2 | LOW | Reliability instrumentation | `WOULD_BLOCK` | At mission creation, by making the contract refuse to close without an actual | `.data/missions/*.json` vs spec §4 |
| **M-10** | Execution plane | The mission produced **zero rows** in `.data/runs.jsonl` and `.data/events.jsonl` (last event `2026-08-31T04:50:35Z`, before the mission) | Manual launching deliberately routes around F90, so no provider, no run record, no verdict | `SYSTEM_DESIGN_GAP` — **a deliberate, documented trade** | Yes | Known and accepted in the spec | The mission is invisible to every instrument except `TaskStore` | Accepted | LOW | Reliability instrumentation | `NO_EFFECT` today; `WOULD_INTERCEPT` once F90 is fixed | After F90 remedy (a) | `.data/events.jsonl` tail; spec §0.3 |
| **M-11** | Task ownership | **`TaskStore.claim` was never called on any mission task** — zero `claim` events across all 11 mission task ids (3 claim events exist in the whole store, none on this mission) | Resource claims were used; task ownership was not | `INSTRUMENTATION_GAP` | Yes | **This session** | Who owned which task is `NOT_RECORDED` in the store; it is recoverable only from prose | 0 | LOW | Typed Handoff | `WOULD_WARN` | At worker launch | `.data/tasks.jsonl` kind census |
| **M-12** | Wave planning | R3 blocked on a human access decision; D1 blocked on R3 alone | 2 of 3 Wave-1 tasks delivered; the entire D-chain sits behind one human action | `ACCESS_OR_PERMISSION_BLOCKER` — **correctly scoped, not a mistake** | Yes | Known at planning | The mission delivered its unblocked half and stopped | None | NONE — and the client review says so in the client's own language | Task DAG validation | `WOULD_INTERCEPT` (scoping the blocker) — **and did** | At planning | Handoff §3; yaml RISK-2 |

---

# C. Root-cause analysis

<!-- anchor: sec-c -->

## C.1 Frequency by mechanism

`MEASURED` by counting the root-cause column above. Multi-cause issues are counted once per cause,
so the total exceeds the issue count (25 + 12 = 37 issues; 52 cause attributions).

| Root cause | Delivery A | Delivery B | Total | Issues |
|---|---:|---:|---:|---|
| `SEMANTIC_CONTRACT_GAP` | 9 | 2 | **11** | H3, H9, H10, H11, H12, H13, H14, H15, H18, M-05, M-07 |
| `DOCUMENTATION_DRIFT` | 7 | 0 | **7** | H2, H3, H6, H7, H9, H20, H23 |
| `MISSING_PROVENANCE` | 5 | 2 | **7** | H5, H8, H13, H18, H22, M-02, M-04 |
| `MISSING_VERIFICATION` | 3 | 3 | **6** | H1, H15, H25, M-01, M-07, M-08 |
| `STALE_CONTEXT` | 2 | 2 | **4** | H6, H17, M-03, M-04 |
| `MISSING_TASK_OR_DEPENDENCY` | 3 | 1 | **4** | H14, H16, H19, M-09 |
| `INSTRUMENTATION_GAP` | 0 | 4 | **4** | M-01, M-08, M-09, M-11 |
| `WRONG_SOURCE_OR_POPULATION` | 2 | 0 | **2** | H4, H11 |
| `ENVIRONMENT_DRIFT` | 2 | 0 | **2** | H4, H5 |
| `COMMUNICATION_FAILURE` | 2 | 0 | **2** | H16, H19 |
| `UNVERIFIED_ASSUMPTION` | 1 | 1 | **2** | H1, M-06 |
| `REPEATED_FAILURE_NOT_LEARNED_FROM` | 0 | 2 | **2** | M-01, M-05 |
| `KNOWLEDGE_AVAILABLE_BUT_NOT_CONSUMED` | 2 | 0 | **2** | H17, H24 |
| `SYSTEM_DESIGN_GAP` | 1 | 1 | **2** | H25, M-10 |
| `CONTRADICTORY_SOURCES` | 1 | 0 | **1** | H2 |
| `HUMAN_MEMORY_DEPENDENCY` | 1 | 0 | **1** | H1 |
| `MANUAL_HANDOFF` | 0 | 2 | **2** | M-02, M-07 |
| `KNOWLEDGE_NOT_AVAILABLE` | 1 | 0 | **1** | H21 |
| `ACCESS_OR_PERMISSION_BLOCKER` | 0 | 1 | **1** | M-12 |

⭐ **The headline: `KNOWLEDGE_NOT_AVAILABLE` accounts for exactly one issue out of thirty-seven.**
Almost nothing here failed because the knowledge did not exist. It failed because the knowledge was
written somewhere the next actor did not read, or was true when written and not when used, or had no
mechanism attached that could stop work.

## C.2 Mistake-type classification

| Type | Issues | Count | Can Agent Factory address it? |
|---|---|---:|---|
| `SYSTEM_DESIGN_GAP` | H12, H14, H15, H25, M-09, M-10 | 6 | **Yes** — this is what the Factory is for |
| `DOCUMENTATION_ERROR` | H3, H6, H7, H8, H9, H20, H23 | 7 | **Partly** — contradiction detection warns; it cannot author |
| `VERIFICATION_FAILURE` | H1, H15, M-01, M-06, M-07, M-08 | 6 | **Yes** — evidence requirements and ACK/NACK |
| `BAD_OR_STALE_INPUT` | H6, H17, M-03, M-04 | 4 | **Yes** — typed claims with an as-of |
| `PROCESS_GAP` | H16, H19, H22, M-11 | 4 | **Yes** — human attention router, intent contract |
| `TOOLING_GAP` | H4, H5, H13, H24 | 4 | **Partly** — source cartography and recipes |
| `COMMUNICATION_FAILURE` | H16, H19 | 2 | **Partly** — the Factory can route the obligation; a human still writes the email |
| `HUMAN_DECISION_ERROR` | H1 (the recollection), M-05 (the deny-list) | 2 | **Partly** — preflight blocks the known shape; it cannot stop a novel judgement |
| `AGENT_REASONING_ERROR` | M-01 (searched the wrong field) | 1 | **Yes** — positive controls as a preflight |
| `MISSING_INFORMATION` | H19 (the dimensions table), R1's NOT-VISIBLE inventory | 2 | **No** — the Factory can *mark* it and route it; it cannot supply it |
| `ENVIRONMENT_DRIFT` | H4, H5 | 2 | **Partly** — cartography detects; it does not prevent |

⛔ **Two categories the Factory cannot fix and must not claim to.** `MISSING_INFORMATION` — the
client's dimensions table does not exist and no mechanism conjures it. And `KNOWLEDGE_NOT_AVAILABLE`
(H21, `ISCROSSFILTERED`) — a thing nobody knew until it was learned. The Factory's honest claim on
both is *the second occurrence*, never the first.

---

# D. Defect propagation and escape distance

<!-- anchor: sec-d -->

## D.1 Boundary model

<!-- anchor: sec-d-1 -->

**Delivery A boundaries** (a "meaningful workflow boundary" is a handover where the next actor could
have re-derived the fact and did not):

```
S1 client conversation
S2 internal record (wiki / Jira / minute)
S3 warehouse SQL
S4 semantic model (PBI) / view layer
S5 consumer surface (dashboard, Excel, client's eyes)
S6 client review / sign-off
S7 reconstruction audit (R1 / R2)
```

**Delivery B boundaries:**

```
T1 premise / inherited context
T2 mission spec
T3 task store materialization
T4 worker dispatch
T5 worker execution
T6 evidence artifact
T7 mission state / handoff
T8 client review projection
```

## D.2 The five deepest escapes

<!-- anchor: sec-d-2 -->

### H1 — the phantom client ask

```
S1  client says "don't change my model" (2026-07-08)
        v
S2  recorded as a "high-level vs low-level" ask, self-flagged UNCONFIRMED
        v
S3  implementing script written; its docstring says "confirm before this reaches Heather" - NOT DONE
        v
S4  metrics hidden on Daily, visible on Marketing
        v
S5  the boundary is what users see
        v
S6  recorded in Jira comment 36056 as SETTLED - it reaches the client's own record
        v
S7  R1 reads the transcript: no such ask exists
```

```
Introduced:       S2
Detected:         S7
Escape distance:  5

Agent Factory ideal interception:   S2 (at the moment the claim entered the record)
Potential escape distance:          0
```

`DERIVED`. ⭐ **The docstring flag is the whole argument.** Written knowledge that a claim was
unverified existed at S3 and travelled to S7 without ever becoming an obligation. **Typed Claims
turn that comment into a state a task cannot close over.**

### H3 — MER inverted in the locking document

```
S2  ATTR:29 / :94 write MER = SPEND / ACTUAL_SALES
        v
S3  MARKETING_EFFICIENCY_MONTHLY.sql:50 implements the inverse
        v
S4  the monthly view is what the semantic layer reads
        v
S5  FIELDS.md and metrics.ts agree with the code, not the doc
        v
S7  R2 finds the disagreement
```

```
Introduced:       S2
Detected:         S7
Escape distance:  4  (S2 -> S3 -> S4 -> S5 -> S7)

Ideal interception:  S3 - the first implementation that had to choose a direction
Potential escape:    1
```

⚠ **Nothing was built wrong.** The code is right and has been right throughout. **The escape is the
document's, and its cost is paid by the next person who specifies from it.**

### H4 / H5 — the divergent schema

```
S3  four objects read UNQUALIFIED; they resolve in WAREHOUSE_TEST_GP226
        v
S4  PBI reads the REPORT_COMMON copies
        v
S5  the dashboard and the Eclipse app show different numbers for the same metric
        v
S6  GP-318 catches it 2026-08-11 and repoints FOUR
        v
S7  R2 counts SIX still divergent and TEN with no repo DDL
```

```
Introduced:       S3
Detected:         S5/S6 for four objects; S7 for the remaining six
Escape distance:  2 (first tranche) / 4 (second tranche - STILL OPEN)

Ideal interception:  S3 - before the first query against an unqualified name
Potential escape:    0
```

⭐ **Six objects are still escaped today.** This is the only issue in the case study that is
simultaneously detected, documented, quantified, and unfixed — which is exactly why it is `DEC-2` in
the client review rather than a silent internal task.

### H19 — the unsent reply

```
S1  client sends 721 rows and promises a dimensions table (2026-07-29)
        v
S2  full gap analysis produced; cover note DRAFTED
        v
S2  a hold is placed: "do not send until that lands"
        v
[the hold has no owner, no expiry, and no downstream dependency edge]
        v
S3/S4 three candidate designs produced against an unspecified dimension list (2026-08-24)
        v
S7  R1: "no design should present a dimension list as responsive to a request that was never made"
```

```
Introduced:       S2 (the hold)
Detected:         S7
Escape distance:  4

Ideal interception:  S2 - a hold is a task with an owner and a next check
Potential escape:    0
```

### M-01 — the false zero in the mission itself

```
T3  search filters r.get('task') for "R1"; task ids are hex; returns zero
        v
T3  the zero is reported as a finding: "the plan was not materialized"
        v
T3  two duplicate tasks created
        v
T4  resource claims taken naming the duplicate ids
        v
T5  workers execute under the duplicate ids
        v
T6  evidence attached to the duplicates; artifacts write the duplicate ids into their headers
        v
T7  re-query by TITLE: all eight tasks existed all along. 3,611 seconds elapsed.
```

```
Introduced:       T3
Detected:         T7
Escape distance:  4
STILL ESCAPED:    T6 - both artifact headers still name the superseded duplicates (ISSUE M-02)

Ideal interception:  T3 - a positive control before a zero becomes actionable
Potential escape:    0
```

`MEASURED` — 3,611s is the difference between the two event timestamps.

## D.3 Escape-distance summary

<!-- anchor: sec-d-3 -->

| Issue | Introduced | Detected | Escape | AF ideal | Potential escape | Reduction |
|---|---|---|---:|---|---:|---:|
| H1 phantom ask | S2 | S7 | **5** | S2 | 0 | **5** |
| H19 unsent reply | S2 | S7 | **4** | S2 | 0 | **4** |
| H3 MER inverted | S2 | S7 | **4** | S3 | 1 | **3** |
| H5 no repo DDL | S3 | S7 | **4** | S3 | 0 | **4** |
| M-01 false zero | T3 | T7 | **4** | T3 | 0 | **4** |
| H12 orphaned channel | S3 | S4→doc | **3** | S3 | 0 | **3** |
| H2 rejected-design trap | S2 | S7 | **3** (not yet fired) | S2 | 0 | **3** |
| H15 fabricated fields | S4 | S7 | **3** | S4 | 0 | **3** |
| H17 stale blocker | S2 | S7 | **3** | S2 | 0 | **3** |
| H4 divergent schema | S3 | S6 | **2** (+4 for the remaining six) | S3 | 0 | **2–4** |
| M-07 scope not read | T2 | T7+ | **3** | T4 | 0 | **3** |
| H21 ISCROSSFILTERED | S4 | S4 | **0** | — | — | 0 (learning, not escape) |
| M-03 metric hierarchy | T1 | T5 | **1** | T1 | 1 | **0 — already optimal** |
| M-06 vacuous failsafe | T2 | T2 | **0** | T2 | 0 | **0 — caught in place** |

**Median escape distance across the eleven Delivery-A escapes: 3.** `DERIVED`.
**Median across the four Delivery-B escapes: 2.** `DERIVED` — and two of the four (M-03, M-06) were
caught at or adjacent to introduction, which is what the mechanisms are for.

⛔ **Do not read the Delivery-B median as proof the Factory works.** The mission was small, recent,
and run by an operator who wrote the spec. The honest claim is narrower: **the two issues caught at
distance 0–1 were caught by mechanisms the spec named in advance** (verify-before-inherit; refuse a
vacuous verification), and the four that escaped were the ones with no mechanism attached.

---

# E. Agent Factory interception matrix

<!-- anchor: sec-e -->

| Real problem | Current mechanism | Agent Factory feature | Exact interception mechanism | Current maturity | What still needs building | KPI |
|---|---|---|---|---|---|---|
| A remembered ask becomes a requirement (H1) | A prose flag in a docstring | **Typed Claims** | Every claim carries `basis` ∈ {CONFIRMED, SUPPORTED, INFERRED, ASSUMPTION, UNKNOWN} and a `source`. A claim below `SUPPORTED` cannot be cited as a client requirement; a verification task is auto-created and the claim cannot reach `CONFIRMED` without evidence | **Partial.** `evidence.py` validates `MEASURED/DERIVED/ASSUMED` and `close(require=...)` raises `EvidenceRequired` — proven refusing. R1 applied a five-level client-claim vocabulary **by hand** | The client-claim vocabulary as a type, not prose; auto-created verification tasks; a citation check | % of published client requirements whose basis is CONFIRMED or SUPPORTED **with a resolvable source** |
| Documents recommending a rejected design still read as current (H2, H6, H7, H17, H20, H23) | Nothing | **Contradiction detection** + **Organizational Memory** | A decision event supersedes the documents that argued the other way; opening one surfaces the supersession | **Absent.** `RECON.md` measured: no memory service, no vector store, no RAG, no graph db; sole runtime dep is `pyyaml` | A decision→document supersession edge and a reader-side warning | Documents open on disk that a later decision contradicts, unmarked |
| A metric defined one way in the doc and the inverse in code (H3, H9, H10, H13, H18, H20) | Human reading | **Semantic Contracts** | The definition is the artifact; SQL, DAX and TypeScript are checked against it, and a mismatch fails the contract | **Absent under that name.** `contract.py` (5 verdicts), `pbi_contract.py` (M1–M12), `redesign_contract.py` (R1–R4) exist — this is contract machinery aimed at deploys, not definitions | A metric-definition object and a definition↔implementation reconciler | Metric definitions with ≥1 implementation disagreeing |
| Two objects, same name, different contents (H4, H5) | A code comment written after the fact | **Source Cartography** | Every object reference resolves to a fully-qualified target with an authority verdict before first use; an unqualified reference is a finding, not a default | **Absent.** R3 — the cartography task — is the blocked task. **The capability's first exercise has not happened** | The cartography pass itself, and an unqualified-reference check in CI | Unqualified object references in consumer code |
| Fabricated zeros on a client surface (H15, H10, H12) | Convention | **Semantic Contracts** + **Continuous acceptance** | A contracted field with no source cannot render a value; it renders `NOT_REPORTED` | **Partial and real.** `client_review.py` rule 3 keeps LIVE/LAST_VERIFIED/STALE/UNAVAILABLE distinct; `contract.py` keeps `UNMEASURABLE` out of `FAIL`; `MARKETING_EFFICIENCY_MARGIN` already does NULL-not-zero for one measure | Extending the four-state absence rule from the review projection down into the field contract | Contracted fields rendering a literal with no source |
| 16 ROAS measures, no default; a reversal that must be announced (H14, H16) | Human memory | **Human Attention Router** + **Client Review** | A decision with `blocking: true` and `client_action_required` is routed and cannot be silently carried; the review surfaces it in the client's language | **Working, first exercise complete.** The Navira review carries 2 decisions (1 blocking), 3 risks (1 HIGH), `origin: CLIENT` vs `FACTORY_PROPOSED` on every item | Delivery of the review to a client, and an acceptance event | Blocking decisions open >N days with no client contact |
| A hold with no owner (H19) | A line in a draft | **Intent Contract** + **Task DAG validation** | A hold is a task with an owner, a dependency edge and a next check; work that depends on the held item is `BLOCKED`, visibly | **Partial.** `TaskStore.block/unblock` is real and proven — the mission's own D1 is correctly `BLOCKED` on R3 alone. An **Intent Contract object does not exist**: `grep -ril intent_contract factory/ scripts/` returns empty | The Intent Contract as a first-class object | Holds with no owner or no next-check date |
| A known control exists in a sibling client's repo and is not used (H24) | Nothing | **Organizational Memory** + **Delivery Recipes** | The anti-join precedence pattern is a recipe; authoring a source union offers it | **Absent.** R2 found the pattern **manually**, by reading FUSION_92 | A recipe library seeded from measured prior art | Recurrence of a pattern a recipe already covers |
| The same defect class repeats (M-01 blind zero, M-05 deny-list, H21 ISCROSSFILTERED) | `docs/findings.d/` — 28 filed findings (`ls docs/findings.d/F*.md | wc -l`), read as data by `factory/findings.py` | **Known-Failure Preflight** | Before a task of a matching shape runs, the prior findings of that class are shown and the specific guard is required | **Partial.** The findings ledger is real and machine-read. **Nothing consumes it as a preflight** — F91 was fixed the same morning M-05 repeated it | The preflight itself: a shape→finding matcher at task launch | Known-failure recurrence rate |
| A scope item in the spec that the worker never read (M-07) | Prose in a spec | **Typed Handoff** + **ACK/NACK** | Each scope item is an item the worker must ACK (read) or NACK (cannot reach); a silent omission is impossible | **Absent.** `.data/handoffs/` holds three files, all from 2026-08-22, none from this mission | The handoff contract and the ACK channel | Scope items with neither an ACK nor a NACK |
| Parallelism asserted, not demonstrated (M-08); the routing dataset never captured (M-09) | Prose in the spec | **Reliability instrumentation** | Per-task actuals recorded as events; a claim of parallelism is derived from the store, never typed by hand | **Partial.** `runs.py` draws `RECORDED/RECONSTRUCTED/NOT-RECORDED`; `events.py` has 9 closed kinds with mandatory verdicts. **This mission wrote to neither** | A task-execution event that carries duration, model, effort and outcome | % of tasks with a `RECORDED` actual |
| The client's dimensions table does not exist (H19 second half); Jira and two email threads are unreadable (R1 §5) | — | — | — | — | — | **`NO MATERIAL EFFECT`.** The Factory can mark these `NOT-VISIBLE` and route the ask. **It cannot supply information nobody has given us.** R1 already did the marking, by hand and correctly |
| `ISCROSSFILTERED` vs `ISFILTERED`, first occurrence (H21) | — | — | — | — | — | **`NO MATERIAL EFFECT` on the first occurrence.** Nobody knew. Known-Failure Preflight claims only the second |
| F90 — a certified team runs in the wrong repository (M-10) | The mission routes around it manually | Mission Compiler / provider path | — | **Blocked.** F90 unfixed; the mission deliberately avoids the provider path | F90 remedy (a) + sparse checkout | Runs whose verdict is not `UNMEASURABLE` |

---

# F. What worked well

<!-- anchor: sec-f -->

Only practices the evidence supports. Each is a candidate for doctrine.

### F1 — Correcting an inherited premise before planning against it

<!-- anchor: worked-f1 -->

```
WHAT WORKED     Three inherited premises were measured and corrected BEFORE any task existed:
                (a) "use the existing mission/DAG mechanisms" - neither exists in factory/;
                (b) the subject is Navira, not GEP;
                (c) task B was already done and was rescoped from RECONSTRUCT to READ-AND-DIFF.
WHY IT WORKED   Each was a two-command measurement. (a) was two greps. (b) was a directory
                listing of wiki/entities/clients/active/. (c) was two file mtimes.
EVIDENCE        Spec sec 0.1-0.5. DOCUMENTED.
DOCTRINE?       YES. This is already the global rule ("an object named by a ticket, boot prompt
                or handoff is a HYPOTHESIS, not a finding") and it earned its keep here. It
                should become a required first section of every mission spec.
```

### F2 — Exercising both load-bearing guards before the work they guard

<!-- anchor: worked-f2 -->

```
WHAT WORKED     The claim conflict guard and the EvidenceRequired guard were each watched
                REFUSING, before Wave 1.
WHY IT WORKED   Spec sec 5, verbatim: "a guard first exercised during the work it is guarding has
                not been tested, it has been trusted." And the acceptance table honestly grades
                its own checks: 1, 2 and 5 "can pass over an absence; 3 and 4 cannot."
EVIDENCE        Spec sec 5 - both refusals quoted verbatim, and the refused close appended
                nothing (205 rows before and after). DOCUMENTED.
DOCTRINE?       YES, with a strengthening: M-08 shows check 1 was NOT proved and the spec had
                already said it could pass over an absence. The doctrine is not "run negative
                controls" - it is "grade every acceptance check by whether it can pass over an
                absence, and treat the ones that can as unproven until demonstrated."
```

### F3 — Marking a claim for verification instead of inheriting it

<!-- anchor: worked-f3 -->

```
WHAT WORKED     The metric hierarchy arrived from a prior thread as Contribution Margin > MER >
                Platform ROAS. It was propagated into R2's prompt MARKED "VERIFY". R2 refuted it
                with evidence from two docs and the SQL.
WHY IT WORKED   The inheritance carried a state, not just a value. The wrong order never became
                mission knowledge and never reached a design.
EVIDENCE        Handoff sec 2: "I propagated it into R2's own prompt marked 'verify'; it came back
                refuted. Do not re-inherit it." DOCUMENTED.
DOCTRINE?       YES - and this is the single clearest argument for Typed Claims in the whole
                case study, because the mechanism was applied BY HAND and worked. Escape
                distance 1. Automating it removes the dependence on the operator remembering.
```

### F4 — Parallelising only genuinely disjoint work, and scoping the blocker rather than the mission

<!-- anchor: worked-f4 -->

```
WHAT WORKED     Wave 1 was [R1, R2, R3] - all READ on disjoint resources. When R3 blocked on a
                human credential decision, R1 and R2 ran anyway and delivered 87KB of cited
                evidence. D1-D5 were left serial because they all WRITE res-mission-artifacts.
WHY IT WORKED   The parallelism decision was made from the resource claims, not from ambition.
                The blocker was scoped to one task, not escalated to the mission.
EVIDENCE        Spec sec 2; handoff sec 1 (R1/R2 done, R3 open, D1 blocked on R3 ALONE);
                yaml RISK-2 states the same fact in client language: "the two reconstruction
                tasks that did not need it are complete, so the pause has not idled the whole
                workstream." DOCUMENTED.
DOCTRINE?       YES.
```

### F5 — Preserving contradictions instead of resolving them silently

<!-- anchor: worked-f5 -->

```
WHAT WORKED     R1 recorded SEVEN contradictions and picked a side only where the evidence
                supported one, saying which side and why. R2 did the same with eleven STALE
                items. The MER inversion (the highest-consequence one) was explicitly NOT
                resolved: "Preserve the contradiction - do not pick one silently."
WHY IT WORKED   A silently resolved contradiction is indistinguishable from a fact. A preserved
                one is a decision waiting for an owner - and DEC-1 in the client review is
                exactly that, put to the client in their own language.
EVIDENCE        R1 sec 2; R2 sec 2; handoff sec 2 item 4; yaml DEC-1. DOCUMENTED.
DOCTRINE?       YES.
```

### F6 — Refusing a verification that could only be vacuous

<!-- anchor: worked-f6 -->

```
WHAT WORKED     The read-only pre-flight was found unable to pass (an admin account will not
                refuse a write) and was NOT run as theatre.
WHY IT WORKED   Spec text names the pattern by name and by count: "the vacuous-verification
                shape this repo has now met nine times."
EVIDENCE        Checkpoint sec 3. DOCUMENTED.
DOCTRINE?       YES. State it as: a verification whose instrument cannot produce the negative
                result is not a verification. This generalises the global "blind instrument"
                rule from measurement to VERIFICATION.
```

### F7 — Read-only discovery with a logged, value-free credential touch

<!-- anchor: worked-f7 -->

```
WHAT WORKED     Exactly one credential row exists: 2026-09-01T01:47:31Z, R3, READ, purpose
                "shape only, value never printed. No Snowflake connection made yet." The
                logging script REFUSES a value-shaped argument and was watched refusing one -
                and the log file is not created by a refused call, so a rejected value never
                reaches disk.
WHY IT WORKED   The standing grant moved the human gate from BEFORE retrieval to AFTER it, so
                the "after" had to be real and checkable. It is.
EVIDENCE        .data/credential-use.jsonl (MEASURED, one row); spec sec 2.1. 
DOCTRINE?       YES - with M-05 as the counterweight in the same session. The LOG worked; the
                EXTRACTION did not. Both belong in the doctrine.
```

### F8 — Separating what the client asked for from what we chose on their behalf

<!-- anchor: worked-f8 -->

```
WHAT WORKED     R1 section E lists six ALDC decisions "frequently mistaken for client asks" and
                grades them CONFIRMED AS AN ALDC DECISION - a distinct verdict. The client
                review carries origin: CLIENT vs FACTORY_PROPOSED on EVERY delivered item,
                decision and risk.
WHY IT WORKED   R1's finding 0.2: "Most of the 'design' in the record is ours, not theirs."
                Without the distinction, a review hands a client their own words and our
                inferences in the same voice.
EVIDENCE        R1 sec 0.2, sec E; yaml origin: field on 5 delivered items, 2 decisions, 3 risks.
                DOCUMENTED / MEASURED.
DOCTRINE?       YES. This is the highest-value single field in the client review model.
```

### F9 — An append-only correction rather than an erasure

<!-- anchor: worked-f9 -->

```
WHAT WORKED     When the duplicate tasks were found, they were ANNOTATED SUPERSEDED with the
                reason - "a search filtered the task ID instead of the title and returned a
                false zero" - not deleted.
WHY IT WORKED   The store cannot be rewritten, so the correction is a new event. The mistake and
                its reason are now permanent evidence, which is why this case study can measure
                it to the second.
EVIDENCE        .data/tasks.jsonl @03:14:03Z, two evidence rows. MEASURED.
DOCTRINE?       YES.
```

---

# G. What Agent Factory ALREADY helped with, during this delivery

<!-- anchor: sec-g -->

⛔ **Strictly what ran. Nothing aspirational.** Each row names the module and the observed effect.

| Mechanism | Module | What it actually did | Evidence |
|---|---|---|---|
| **Append-only task store with parent/child hierarchy** | `factory/tasks.py` | Held the mission as a parent task and eight children; 217 events total in the store, 28 on this mission. Made the duplicate-task error **measurable to the second** three weeks after the fact | `MEASURED` — `.data/tasks.jsonl` |
| **Dependency edges that actually block** | `factory/tasks.py` `block/unblock` | 7 edges wired at creation. D1 is `BLOCKED` on R1, R2, R3 — two satisfied, R3 outstanding. The block is real, not prose | `MEASURED` |
| **Evidence with a validated basis** | `factory/evidence.py` | `basis` validated to `MEASURED / DERIVED / ASSUMED`; `evidence_class` to `TARGET / CONSUMER / REGRESSION / ROLLBACK`. Both R1 and R2 closed with `MEASURED` + `TARGET` | `MEASURED` |
| **Cannot close without evidence** | `close(require=...)` → `EvidenceRequired` | **Watched refusing** before the mission: *"task 2b9aae3b cannot close as done: no MEASURED or DERIVED evidence attached"* — and the refused close appended nothing | `DOCUMENTED` (spec §5) |
| **Resource claims that refuse a second writer** | `factory/claims.py` | **Watched refusing** before the mission, with the consequence stated in the refusal: *"the loser's work disappears without an error"* | `DOCUMENTED` (spec §5) |
| **Credential-use log that refuses a value** | `scripts/credential_use.py` | One row written; a value-shaped argument watched being refused, exit 1, and no file created by the refused call | `MEASURED` + `DOCUMENTED` |
| **Findings ledger read as data** | `factory/findings.py` over `docs/findings.d/` | 28 findings on disk (`ls docs/findings.d/F*.md | wc -l`), machine-readable. It supplied the F90/F91 context that shaped the mission's design — F90 is **why** the mission runs manually | `MEASURED` (file count) + `DOCUMENTED` (spec §0.3) |
| **Client Review projection with grounded language** | `factory/client_review.py` | Refuses to render `VERIFIED / DEPLOYED / ACCEPTED / HEALTHY / ON TRACK` unless a file resolves **and** a task-evidence row carries a `USABLE` basis; degrades to `CLAIMED` rather than dropping or promoting. Allow-list client boundary. Four-state freshness | `MEASURED` (docstring + module) |
| **`origin: CLIENT` vs `FACTORY_PROPOSED`** | the review model | Applied to all 5 delivered items, 2 decisions and 3 risks in the Navira review | `MEASURED` (yaml) |

**And the honest negative:** the Factory's **execution plane did not run at all**. Zero rows in
`.data/runs.jsonl` from this mission; the last `.data/events.jsonl` row predates it. No provider, no
dispatch, no verdict. That was the deliberate trade that routed around F90 — and it means the
mission is invisible to every reliability instrument the repo owns.

---

# H. What FUTURE Agent Factory capabilities would have changed

<!-- anchor: sec-h -->

Everything in this section is `SIMULATED`.

### H.1 Typed Claims — against H1 (the phantom ask)

<!-- anchor: cf-h-1 -->

**Actual**

```
recollection of a client ask
        v
written into the record as a requirement
        v
flagged "confirm against the transcript" in a docstring
        v
implemented as a metric-visibility boundary
        v
recorded in Jira comment 36056 as SETTLED
        v
R1 reads the transcript 8 weeks later - REFUTED
```

**With Agent Factory**

```
recollection of a client ask
        v
claim created, basis = ASSUMPTION, source = "recollection", as_of = <date>
        v
a verification task is created automatically, blocking, owner named
        v
the claim CANNOT reach CONFIRMED without a resolvable source
        v
any artifact citing it as a client requirement fails the citation check
        v
the transcript is read - REFUTED - and the refutation propagates to every citing artifact
```

```
INTERCEPTION:
WOULD_INTERCEPT

WHY:
The recollection would still have been recorded - the Factory does not improve memory. What it
prevents is the recollection becoming a CONFIRMED client requirement, and it prevents an artifact
that cites it as one from being published.

EXPECTED EFFECT:
Escape distance 5 -> 0. The phantom would never have reached Jira comment 36056.

REMAINING HUMAN DECISION:
Someone still has to read the transcript. The Factory schedules it; it does not perform it.

CONFIDENCE:
HIGH on the mechanism - the refusal primitive (EvidenceRequired) exists and was watched refusing.
MEDIUM on the outcome - it depends on a claim-typing layer that does not exist yet.
```

### H.2 Source Cartography — against H4/H5 (the divergent schema)

<!-- anchor: cf-h-2 -->

**Actual**

```
implementation references four object names, unqualified
        v
they resolve in the connection's default schema (WAREHOUSE_TEST_GP226)
        v
PBI reads the REPORT_COMMON copies of the same names
        v
two consumers, two definitions, same names
        v
caught 2026-08-11 after a $3,374.90 discrepancy is chased
        v
four repointed; SIX STILL DIVERGENT; TEN have no repo DDL at all
```

**With Agent Factory**

```
implementation references an object name
        v
provenance check: is this reference fully qualified?
        v
NO -> AUTHORITY UNKNOWN
        v
a Source Cartography task is created, scoped to that reference
        v
the reference is a SCOPED BLOCKER - only work depending on it stops
        v
unrelated work continues
        v
cartography returns: two objects, same name, different contents, in two schemas
        v
the divergence is a FINDING with a lineage record, not a surprise in a reconciliation
```

```
INTERCEPTION:
WOULD_INTERCEPT

WHY:
An unqualified reference is a hypothesis about which object you are reading. The Factory's rule -
never infer the source from matching values - is already global doctrine; cartography is the
mechanism that enforces it before the first query rather than after the first discrepancy.

EXPECTED EFFECT:
The four-object tranche: escape 2 -> 0. The six still-divergent objects would never have
accumulated, because each unqualified reference would have been a blocker at authoring.

REMAINING HUMAN DECISION:
Which copy is authoritative. The Factory establishes that they differ; a human decides which wins.

CONFIDENCE:
MEDIUM. The capability's FIRST EXERCISE HAS NOT HAPPENED - R3 is the cartography task and it is
blocked. This is a design claim, not an observed one, and the artifact must say so.
```

### H.3 Known-Failure Preflight — against M-05 (the deny-list) and M-01 (the false zero)

<!-- anchor: cf-h-3 -->

**Actual**

```
F91 fixed on the morning of 2026-08-31: a guard is only as wide as the relation it derives over
        v
that afternoon: a DENY-LIST is used to filter a credential file
        v
the vault stores credentials in markdown TABLES; "password" is in the header, not the data rows
        v
three plaintext passwords reach a session transcript, one spanning non-prod AND prod
```

**With Agent Factory**

```
task shape recognised: "extract from a credential source"
        v
Known-Failure Preflight matches F91 and the deny-list class
        v
the prior evidence is SHOWN, and the specific guard is REQUIRED: allow-list the columns
        v
a deny-list filter over a credential source is REFUSED
        v
the extraction proceeds with an allow-list, or does not proceed
```

```
INTERCEPTION:
WOULD_BLOCK

WHY:
This is the strongest interception claim in the document, because the knowledge existed, in this
repo, in a finding filed hours earlier. Nothing consumed it. That is not a knowledge problem - it
is an operationalisation problem, and it is exactly what a preflight is.

EXPECTED EFFECT:
Three credentials not exposed. One rotation - the paulrussell password spanning non-prod and
production - not owed.

REMAINING HUMAN DECISION:
None for the known shape. A novel extraction shape would still get through.

CONFIDENCE:
HIGH. The findings ledger is real and machine-read TODAY (factory/findings.py over
docs/findings.d/). The missing piece is a shape matcher at task launch, not a knowledge base.
```

**The same mechanism against M-01:** the false zero is the *blind instrument* class, of which this
repo has filed multiple instances (F84 is literally *"the zero consumer count was measured by a
blind grep"*). A preflight on any task whose output is a count or a zero would require a positive
control. `WOULD_INTERCEPT`, escape 4 → 0.

### H.4 Typed Handoff + ACK/NACK — against M-07 (the scope item never read)

<!-- anchor: cf-h-4 -->

**Actual**

```
spec sec 0.5: "R2's scope therefore includes aldc-launchpad/docs/readouts/, not only the wiki.
A diff that reads one repo and reports 'no prior design exists' would be a blind instrument -
three designs already exist."
        v
R2 dispatched with the spec as prose
        v
R2 method note: "NOT-VISIBLE: the aldc-launchpad repo (S11)"
        v
nothing reconciles the two
        v
the three GP-319 designs are read by NEITHER worker
```

**With Agent Factory**

```
handoff contract carries scope items as a typed list
        v
worker must ACK (read) or NACK (cannot reach, with a reason) EACH item
        v
aldc-launchpad/docs/readouts/ receives neither
        v
the task cannot close - a scope item with no verdict is not a completed scope
        v
either R2 reads it, or R2 NACKs it and the gap is a visible finding with an owner
```

```
INTERCEPTION:
WOULD_BLOCK

WHY:
The spec did not merely mention the repo - it PREDICTED the exact failure ("would be a blind
instrument") and the failure happened anyway. Prose cannot enforce itself. An ACK/NACK channel
converts a scope instruction into an obligation with a verdict.

EXPECTED EFFECT:
Either the three prior designs enter the reconstruction, or their absence is a named gap D3
inherits. Today it is neither.

REMAINING HUMAN DECISION:
Whether to grant the read scope. A NACK is a legitimate answer.

CONFIDENCE:
HIGH on the mechanism's necessity - this is measured, not theorised. MEDIUM on the build: no
handoff contract exists (.data/handoffs/ holds three files, all from 2026-08-22).
```

### H.5 Intent Contract + Human Attention Router — against H19 (the unsent reply) and H16 (the unannounced reversal)

<!-- anchor: cf-h-5 -->

**Actual**

```
client sends 721 rows; promises a dimensions table
        v
gap analysis + cover note produced; a HOLD is placed with no owner and no expiry
        v
three candidate designs produced against an unspecified dimension list
        v
separately: a client-agreed scope item is reversed; the record itself says the ratio movement
"must be announced, not discovered"; no announcement is made
        v
both surface only when a reconstruction reads the whole record
```

**With Agent Factory**

```
the client's request becomes an INTENT CONTRACT: what was asked, by whom, when, unresolved parts
        v
"dimensions table outstanding" is a dependency edge, not a sentence
        v
every design task depending on it is BLOCKED and says why, in the client's own language
        v
the hold on the reply is a task with an owner and a next-check date
        v
the reversal's "must be announced" obligation is a task with client_action_required = true
        v
the Human Attention Router surfaces both as blocking client decisions
        v
the Client Review renders them in the client's language, with origin: CLIENT vs FACTORY_PROPOSED
```

```
INTERCEPTION:
WOULD_BLOCK on the design tasks; WOULD_INTERCEPT on the communication.

WHY:
Neither of these is a knowledge failure. Both obligations are WRITTEN DOWN, in our own record,
in our own words. They failed because a sentence is not a mechanism.

EXPECTED EFFECT:
Three candidate designs would not have been produced against an unspecified dimension list
without that being stated on their face. The ratio movement would have been announced.

REMAINING HUMAN DECISION:
Someone still writes the email and sends it. The Factory routes and blocks; it does not speak
to the client.

CONFIDENCE:
MEDIUM-HIGH. Half of this SHIPPED and ran - the Client Review projection exists, the blocking
decision exists, origin: is populated. The Intent Contract does not exist: measured,
grep -ril intent_contract factory/ scripts/ returns empty.
```

### H.6 Where Agent Factory would have made NO MATERIAL EFFECT

<!-- anchor: cf-h-6 -->

| Issue | Why the Factory does not help |
|---|---|
| **H19b — the client's dimensions table does not exist** | No mechanism conjures information the client has not sent. The Factory marks it `NOT-VISIBLE` and routes the ask. R1 already did both, by hand and correctly. |
| **R1 §5 — Jira, two email threads, ten ticketless GP-numbers** | `NOT-VISIBLE` is a *correct verdict*, not a defect to intercept. Fixing it means granting read access, which is an access decision, not an orchestration one. |
| **H21 — `ISCROSSFILTERED` vs `ISFILTERED`, first occurrence** | Nobody knew. Known-Failure Preflight claims the second occurrence and must not claim the first. |
| **M-10 — no rows in `runs.jsonl`** | This is the Factory's own execution plane being deliberately bypassed. It is a consequence of F90, not something a capability would have caught. |
| **The `keel` design quality itself (D3, unrun)** | The Factory constrains *how* a design is arrived at — grain declared first, measures censused, absence typed. It does not make the design good. That remains a modelling judgement. |

---

# I. Interactive simulation storyboard

<!-- anchor: sec-i -->

Nine scenes. Each reveals **only what was known at that point**, takes a viewer decision, then
reveals the later evidence. `SIMULATED` applies to every "Agent Factory intervention" panel.

---

## SCENE 1 — The premise you were handed

<!-- anchor: scene-1 -->

**CONTEXT.** You have been told to run the first real mission "using Agent Factory's existing
mission/task/DAG/state/claim mechanisms."

**WHAT YOU KNOW.** The repo has a `factory/` package with ~50 modules. The instruction sounds
authoritative. It came from a reviewer whose job is to make the plan better.

**QUESTION FOR THE VIEWER**

> The plan names four mechanisms. What do you do first?

| | Choice | Consequence |
|---|---|---|
| **A** | Start building against the four named mechanisms | Two of them do not exist. `lanes.py` validates lane gate ids against `readiness.GATES` **at import**, so your first lane fails at import time and you spend the session debugging a plan, not running it |
| **B** | Ask the reviewer to clarify | Costs a round trip. The reviewer does not have the repo open |
| **C** | Grep for each of the four names before planning against any of them | Two greps. `\bmission\b` → no matches. `depends_on` → no matches |
| **D** | Assume they exist under different names and adapt as you go | The adaptation is invisible; nobody can tell later which parts of the plan were real |

**WHAT ACTUALLY HAPPENED.** C. Two greps, run before a task existed. `board.DEPENDS` turned out to
be a *gate* dependency map, not a task DAG. **But `TaskStore` already supplied the exact shape
needed** — hierarchy, dependency edges, five states, typed evidence, and a close that refuses
without proof. *"Nothing new is built."*

**AGENT FACTORY INTERVENTION**

```
INHERITED PREMISE
      v
PROVENANCE CHECK  -  who measured this, and when?
      v
UNVERIFIED
      v
two greps
      v
2 of 4 mechanisms REFUTED, 1 rescoped, 1 renamed
      v
plan written against the system that EXISTS
```

**BUSINESS IMPACT.** The most expensive failure in a delivery is building correctly against a
premise nobody checked. Two greps is the cheapest control in this entire case study.

---

## SCENE 2 — Whose model is it, anyway?

<!-- anchor: scene-2 -->

**CONTEXT.** The mission task's title says *"GEP cross-channel marketing model."* That came from a
boot prompt, which came from a ticket. GEP is the client. It is not wrong.

**WHAT YOU KNOW.** GEP is a client. The Jira project is `GP-*`. Nothing suggests a problem.

**QUESTION**

> You are about to dispatch two workers to search a wiki and two source repos for objects
> belonging to this model. What name do they search for?

| | Choice | Consequence |
|---|---|---|
| **A** | "GEP" — it is the client name on the ticket | `wiki/entities/clients/active/` holds exactly two clients. Every marketing object is named for something else |
| **B** | Both, and see what comes back | Doubles the search and buries the finding in noise |
| **C** | Check what the ticket's own readout is titled first | `GP-319`'s readout is **"Navira Marketing Model Designs"** — 2 Navira mentions, **0 GEP mentions** |
| **D** | Search for object-name prefixes in the SQL directly | Works, but you would not know which entity you had found |

**WHAT ACTUALLY HAPPENED.** C. **GEP is the Jira project and the contracting client; Navira is the
modelled entity** (`MARKETING_DIM_AGENCY`, `ENTITY_ROLE` = HOUSE). The spec recorded the correction
and left the task title unchanged — *the append-only store cannot be rewritten, and the client name
is accurate.*

**LATER EVIDENCE.** R2's entire `MISSING` section is a list of `MARKETING_*` object names. A search
for "GEP" would have returned the schema path and nothing else.

**BUSINESS IMPACT.** Two workers were about to spend an hour each searching for the wrong noun.
A five-minute check redirected both.

---

## SCENE 3 — The credential you are about to read

<!-- anchor: scene-3 -->

**CONTEXT.** R3 needs Snowflake read access. Credentials live in a wiki vault file. A standing
grant covers retrieval from this repo. You want the account and user, not the password.

**WHAT YOU KNOW.** The file contains passwords. You must not let one into the transcript. You have
a filter in mind.

**QUESTION**

> How do you extract the account and user without extracting a password?

| | Choice | Consequence |
|---|---|---|
| **A** | Filter out every line containing "password" | The vault stores credentials in **markdown tables**. "password" is in the header row and **never in the data rows**. Three plaintext values pass straight through |
| **B** | Allow-list only the account and user columns | Nothing else can escape, including fields nobody has thought about yet |
| **C** | Read the whole file and be careful | The value is in the transcript the moment it renders |
| **D** | Ask Paul to paste just the account name | Safe, slow, and the standing grant exists precisely to avoid this |

**WHAT ACTUALLY HAPPENED.** **A.** Three plaintext passwords reached the session transcript. One —
`paulrussell` — is listed for **`og35375` non-prod AND `wj66376` PRODUCTION**. `MIKESTUARTADMIN` was
recorded as issued **without MFA**.

**LATER EVIDENCE — and this is the part that stings.** `docs/evidence/switchboard-security-preflight-2026-08-31.md`
records that a session manager indexes the first ~500 characters of the first ~16 messages into a
substring-searchable FTS table, **and that deletion does not stick.** The exposure was around message
90 — *probably* outside that window. **Probably is not verified.**

And: **the identical defect class — a guard only as wide as the relation it derives over — was fixed
in `readiness.py` (F91) that same morning.**

**AGENT FACTORY INTERVENTION**

```
TASK SHAPE:  extract from a credential source
      v
KNOWN-FAILURE PREFLIGHT  -  matches F91, deny-list class
      v
PRIOR EVIDENCE SHOWN, GUARD REQUIRED: allow-list the columns
      v
a deny-list filter over a credential source is REFUSED
      v
extraction proceeds with an allow-list, or does not proceed
```

**BUSINESS IMPACT.** One password spanning non-prod and production. Rotation is owed and **not
confirmed**. The rule went on to become **rule 1 of `factory/client_review.py`** within a day — the
client boundary is an allow-list, never a deny-list — which is the estate learning, expensively.

---

## SCENE 4 — The read-only proof that cannot fail

<!-- anchor: scene-4 -->

**CONTEXT.** The mission spec requires proving read-only access by **attempting a scoped write and
watching it be refused**. *"A role assumed read-only is an assumption; a role watched refusing a
write is a measurement."*

**WHAT YOU KNOW.** You have `snowflake-admin-nonprod` in `aldc-vault-test`. The environment is TEST,
so a mistake is recoverable. The pre-flight is written and ready to run.

**QUESTION**

> Do you run the pre-flight?

| | Choice | Consequence |
|---|---|---|
| **A** | Run it. TEST is recoverable and the mission is read-only anyway | The account is **admin**. It will not refuse. You would record a pass from an instrument structurally incapable of failing |
| **B** | Skip the pre-flight; the mission writes nothing | An unproven assumption becomes an unwritten one |
| **C** | Run it and record read-only as `ASSUMED`, not `MEASURED`, citing TEST recoverability as the compensating control | Honest. Weaker. Still workable |
| **D** | Stop, and ask for a read-only role that structurally refuses | Blocks R3 on a human. Makes the pre-flight mean what it says |

**WHAT ACTUALLY HAPPENED.** The problem was spotted **before the pre-flight ran**, and both C and D
were put to a human. **Paul chose D.** R3 is blocked, correctly, on creating a read-only role in
`og35375`.

**WHAT WAS EXPLICITLY REFUSED.** *"What must not happen: running the pre-flight against an admin
account and reporting it as a read-only proof. That is the vacuous-verification shape this repo has
now met **nine times**."*

**BUSINESS IMPACT.** One blocked task, and one green light **not** manufactured. The rest of Wave 1
ran regardless — the blocker was scoped to R3, not escalated to the mission. The client review says
this in the client's own words: *"the pause has not idled the whole workstream."*

---

## SCENE 5 — The search that returns zero

<!-- anchor: scene-5 -->

**CONTEXT.** You are about to run Wave 1. First, confirm the mission's tasks exist in the store.

**WHAT YOU KNOW.** You wrote the mission spec. You believe the tasks were created. You run a search
over `.data/tasks.jsonl` filtering `r.get('task')` for `"R1"`.

**IT RETURNS ZERO.**

**QUESTION**

> What do you conclude?

| | Choice | Consequence |
|---|---|---|
| **A** | The plan was never materialized. Create the tasks | Two duplicate tasks with no dependency edges. Wave 1 runs under the wrong ids |
| **B** | Run a positive control — search for something you *know* is in the store — before acting on the zero | You discover the field you filtered is the **task ID**, which is hex. No id contains "R1" |
| **C** | Check the mission JSON, which lists the ids | The `labels` block maps `R1 → 2b9aae3b` directly. Ten seconds |
| **D** | Ask someone | Slower, and the answer is on disk |

**WHAT ACTUALLY HAPPENED.** **A.** Two duplicate tasks created at `02:13:52Z` — 81 minutes and 38
seconds after the tasks it could not find were created.

**LATER EVIDENCE.** All eight tasks existed, correctly parented to the mission, with a **fully wired
DAG**. Twenty-five block events existed. The search filtered the ID; it should have filtered the
title.

**THE CORRECTION.** At `03:14:03Z` — **3,611 seconds later** — evidence was re-attached to the real
tasks and both duplicates annotated `SUPERSEDED` with the reason. The store is append-only, so the
mistake is permanent evidence. That is why this scene can be timed to the second.

**AND WHAT IS STILL WRONG.** Both evidence artifacts *still* name the superseded duplicates in their
own headers — R1 says task `fbe2ea4c`, R2 says `200deda2`. **The store was corrected; the artifacts
it points at were not.** Measured in this session; not previously recorded.

**AGENT FACTORY INTERVENTION**

```
SEARCH RETURNS ZERO
      v
INSTRUMENT-SIGHT CHECK  -  has this search been shown able to return non-zero?
      v
NO
      v
POSITIVE CONTROL REQUIRED before the zero is actionable
      v
control fails -> the search is blind, not the store empty
      v
zero is NOT a finding
```

**BUSINESS IMPACT.** Internal only, this time. **The same shape, pointed at a client, is FU92-420** —
five wrong client answers with zero deploys, every correction driven by the client's pushback.

---

## SCENE 6 — Two documents, one day apart

<!-- anchor: scene-6 -->

**CONTEXT.** You are about to design candidate dimensional models. Two documents on disk, both dated
2026-08-24, both persuasive, both conclude the same thing: the right shape is **one narrow conformed
fact at the core-10 grain**, with per-platform extension facts.

**WHAT YOU KNOW.** They are recent. They cite the client's own 721-row matrix. They agree with each
other. Nothing marks either as superseded.

**QUESTION**

> Do you build it?

| | Choice | Consequence |
|---|---|---|
| **A** | Yes — two independent documents agree | You build the thing that was **rejected the next day** |
| **B** | Check for a later decision on the same question before opening either | `GP-319`, 2026-08-25, rejects a conformed core fact explicitly |
| **C** | Build it and flag it for review | The review is where the rejection surfaces, after the work |
| **D** | Ask the client | The client has no view on warehouse object counts |

**WHAT ACTUALLY HAPPENED.** The trap has **not yet fired** — D3 has not run. R1 found it first and
named it: *"the single highest-risk trap for D3: a designer who finds those two files first will
build the thing GP-319 rejected the next day."*

**THE REJECTION'S REASON, WHICH MATTERS.** *"It would create a new table for figures that already
live in one object and already reconcile to the cent… This client already carries **~14 copies of the
marketing family across 6 schemas**; a 15th worsens the canonical-object problem. Nothing is left to
conform."*

**AGENT FACTORY INTERVENTION**

```
DOCUMENT OPENED
      v
CONTRADICTION CHECK against later decisions on the same question
      v
GP-319 2026-08-25 REJECTS this shape
      v
the document is surfaced WITH its supersession
      v
the design proceeds from the standing decision, not the superseded recommendation
```

**BUSINESS IMPACT.** A fifteenth copy of a marketing table family in a client warehouse that already
has fourteen across six schemas — built confidently, from good-faith reading of two good documents.

---

## SCENE 7 — The headline metric, upside down

<!-- anchor: scene-7 -->

**CONTEXT.** You are writing the specification for the board-level marketing-efficiency number. You
open the architecture page that locks it.

**WHAT YOU KNOW.** `ATTR:29` — *"total spend ÷ actual revenue."* `ATTR:94` — `MER = SPEND / ACTUAL_SALES`.
The page is the decision record. It says `DECIDED 2026-05-29 (Paul)`.

**QUESTION**

> Do you specify `MER = SPEND / SALES`?

| | Choice | Consequence |
|---|---|---|
| **A** | Yes — it is the locking document and it says so twice | You ship a spec whose headline metric is the reciprocal of the running system's |
| **B** | Check the implementation before specifying from the doc | `_MONTHLY.sql:50` computes `ACTUAL_SALES_GROSS_USD / SPEND_USD` — the inverse |
| **C** | Pick whichever looks more sensible | ~5.0 and ~0.2 are both defensible-looking numbers |
| **D** | Preserve the contradiction and escalate it as a decision | Slower. Correct |

**WHAT ACTUALLY HAPPENED.** R2 chose B and then D. It found **three** implementations that agree
with each other and disagree with the doc: the SQL, `FIELDS.md`, and `metrics.ts` at two separate
lines. Its verdict: *"the single highest-consequence STALE item."*

And the handoff makes the discipline explicit: **"Preserve the contradiction — do not pick one
silently."**

**LATER EVIDENCE.** The doc's own formula is what the same page elsewhere calls **TACoS's** shape.
So the error is not random — it is a metric definition that migrated into its neighbour's slot.

**BUSINESS IMPACT.** *"A ~5.0x MER and a ~0.2 MER are the same business fact, and the doc and the
code disagree on which one the board sees."* Nothing was ever built wrong. **The cost is paid by
every future person who specifies from the document rather than the code.**

---

## SCENE 8 — What the dashboard shows when the warehouse has nothing

<!-- anchor: scene-8 -->

**CONTEXT.** The dashboard has a field contract — `types.ts` plus `FIELDS.md`. The warehouse does not
supply every field in it.

**WHAT YOU KNOW.** The contract lists `dailyBudget`, `budgetUsedPct`, `timeInBudgetPct`, campaign
`status`, product `sku`, product `orders`, brand `platformCount`. The views must render.

**QUESTION**

> What does the app render for a contracted field with no source?

| | Choice | Consequence |
|---|---|---|
| **A** | `0` / a sensible default — the view must not break | `dailyBudget: 0`, `orders: 0`, `status: "active"` for **every** campaign, `sku` rendering the **ASIN**, `platformCount = spend > 0 ? 1 : 0` — a boolean wearing a count |
| **B** | Render a `NOT_REPORTED` state the user can see | The view is honest and slightly uglier |
| **C** | Hide the column entirely | The contract silently shrinks and nobody knows why |
| **D** | Fail the contract until the warehouse supplies it | Nothing ships |

**WHAT ACTUALLY HAPPENED.** **A**, across at least twelve fields.

**AND — CRUCIALLY — THE SAME CODEBASE DOES B ELSEWHERE, DELIBERATELY.** `MARKETING_EFFICIENCY_MARGIN`
returns `NULL`, never `0`, where COGS coverage is zero, with the view comment *"cost unknown => margin
N/A, not 0 … never net-sales-as-margin"*, and the frontend enforces the same rule independently:
*"Coercing missing cogs to 0 would fabricate a 100% margin (the Lectric CM trap)."*

**So the estate knows the rule, states it, and enforces it structurally — for one measure.**

**AGENT FACTORY INTERVENTION**

```
CONTRACTED FIELD
      v
SOURCE RESOLUTION  -  which object supplies this?
      v
NONE
      v
the field renders NOT_REPORTED - a literal is REFUSED
      v
the missing source becomes a task with an owner
```

**BUSINESS IMPACT.** A client reads `Daily budget: 0`, `Orders: 0`, `Status: Active` and has no way
to tell a measurement from a placeholder. This is the same failure class that put **our own engineers'
debugging folders** into a client-facing CSV on FU92-420 — an artifact read as a template rather than
as the client would read it.

---

## SCENE 9 — What you tell the client

<!-- anchor: scene-9 -->

**CONTEXT.** Wave 1 is done. R1 and R2 delivered 87KB of cited evidence. R3 is blocked on an internal
credential rotation. You owe the client a review.

**WHAT YOU KNOW.** You have seven contradictions, eleven stale statements, twenty-three missing
columns, a phantom client requirement, six divergent warehouse objects, and an unfixed exposure of
your own.

**QUESTION**

> What goes in the client review?

| | Choice | Consequence |
|---|---|---|
| **A** | Progress and next steps. The findings are internal | The client learns about the phantom requirement when it changes their model |
| **B** | Everything, in engineering language | 23 missing column names is not a client communication |
| **C** | The findings that change **their** decisions, in their language, separated into what they asked for and what we chose | Two decisions, one blocking. Three risks, one HIGH. Every item marked `CLIENT` or `FACTORY_PROPOSED` |
| **D** | Wait until R3 unblocks and review the whole thing at once | The blocking decision (`DEC-1`) gates requirements synthesis. Waiting costs the delivery |

**WHAT ACTUALLY HAPPENED.** **C.** The review carries:

- **`DEC-1` (blocking, origin `CLIENT`)** — *"This split has been treated as your requirement.
  Re-reading the meeting transcript in full, we cannot find you asking for it… Rather than quietly
  keeping a rule we cannot source, we would like you to settle it."* Three options, one recommended.
- **`DEC-2` (non-blocking, `FACTORY_PROPOSED`)** — repoint the six divergent objects now, or as part
  of the rebuild.
- **`RISK-1` (HIGH)** — *"Two of your surfaces can still report different numbers for the same
  metric."*
- **`RISK-2` (MEDIUM)** — the cartography pause, stated as ALDC-internal, `client_action_required: false`.
- **`RISK-3` (MEDIUM)** — *"Part of the requirement record is not readable by us, and is graded
  accordingly."*

**WHAT THE MECHANISM GUARANTEES.** `factory/client_review.py` will not render `VERIFIED`,
`DEPLOYED`, `ACCEPTED`, `HEALTHY` or `ON TRACK` unless a file resolves on disk **and** a task-evidence
row carries a `MEASURED` or `DERIVED` basis. An unsupported outcome degrades to `CLAIMED` — *not
silently dropped, and not silently promoted.*

**BUSINESS IMPACT.** *"A design decision that has shaped the model for months turns out not to be
traceable to anything you said. Correcting it now is cheap; discovering it after the rebuild is
not."* That is the client-facing sentence, and it is already written.

---

# J. Executive summary table

<!-- anchor: sec-j -->

Presentation-quality. Ordered by client risk, then by escape distance.

| Issue | Why it happened | Where detected | Ideal interception | Agent Factory feature | Expected benefit |
|---|---|---|---|---|---|
| **A design law built on a client request that was never made** | A recollection entered the record as a requirement; the doc flagged it unverified and nothing acted on the flag | Reconstruction audit, 8 weeks later | The moment the claim entered the record | Typed Claims + Evidence requirements | Escape 5 → 0. A phantom requirement never reaches the client's ticket |
| **The client's largest requirement has an unsent reply, and its bigger half never arrived** | A hold with no owner and no expiry | Reconstruction audit | At the hold | Intent Contract + Human Attention Router | Designs cannot be produced against an unspecified dimension list without that being visible |
| **Two of the client's surfaces read differently-defined objects with the same names** | Unqualified references resolving in a divergent schema copy | Chasing a $3,374.90 discrepancy; **six objects still divergent** | Before the first query against an unqualified name | Source Cartography | Escape 2 → 0; the six-object backlog never accumulates |
| **$244,870.44 of spend present in the warehouse and unselectable in the report** | Channel jammed into the marketplace axis, creating a non-member of the dimension | Lineage analysis | At the relabel | Semantic Contracts + Task DAG validation | Cross-channel spend addressable by a positive slicer choice |
| **~31% of Amazon ad spend silently dropped, including the #1 spender** | Three brand vocabularies, no conformed brand dimension | Coverage probe, then the reconstruction | At the first brand aggregation | Semantic Contracts + Typed Claims (coverage) | Wrong client-visible totals caught at authoring |
| **The board headline metric is written backwards in the document that locks it** | A formula typed once, never reconciled to the implementation | Reconstruction audit | At the first implementation that chose a direction | Semantic Contracts | Escape 4 → 1. The document and the system stop disagreeing |
| **Twelve contracted fields render fabricated values on a client surface** | The field contract outran the warehouse; the app filled the gap with literals | Reconstruction audit | At contract-to-source reconciliation | Semantic Contracts + Continuous acceptance | The client can tell a measurement from a placeholder |
| **A client-agreed scope item reversed with no announcement, while client-visible ratios move** | The reversal had a sound reason and no communication obligation attached | Still open | At the reversal | Client Review + Human Attention Router | The client is told before they discover it |
| **16 ROAS measures with no canonical default** | Measures added incrementally with no designation | Ticket analysis | At the second ROAS measure | Human Attention Router + Client Review | Colleagues stop getting irreconcilable answers |
| **Two documents recommend a design rejected the next day; neither marked superseded** | No supersession mechanism over documents | Reconstruction audit — **trap still armed** | At the rejection | Contradiction detection + Organizational Memory | A 15th copy of a 14-copy table family never gets built |
| **A deny-list over a credential table exposed three passwords, one spanning prod** | A guard only as wide as the relation it derives over — the same class fixed hours earlier | Same session, self-caught | Before the extraction | Known-Failure Preflight | Three credentials not exposed; one prod rotation not owed |
| **A search filtered the wrong field, returned zero, and the zero became a finding** | No positive control on a search that returned nothing | Self-caught, 3,611s later | At the search | Known-Failure Preflight (positive control) | Escape 4 → 0. No duplicate tasks, no wrong provenance in the artifacts |
| **A named scope item was never read and never refused** | Scope delivered as prose with no acknowledgement channel | **This audit** | At dispatch | Typed Handoff + ACK/NACK | Three existing designs enter the reconstruction, or their absence is a named gap |
| **"Three tasks ran in parallel" is unproven by the record** | Parallelism asserted in prose; three claims share one pid and R3 never claimed | **This audit** | At claim time | Reliability instrumentation | The mission's headline claim becomes measurable rather than asserted |
| **The routing dataset — the stated point of run 1 — was never captured** | 13 instrumentation fields specified in prose, none written | **This audit** | At mission creation | Reliability instrumentation | Run 2 can answer whether `capability_class` predicts difficulty |

---

# K. Most important failure patterns

<!-- anchor: sec-k -->

Individually these are fifteen issues. Structurally they are **four**.

## PATTERN 1 — `KNOWLEDGE_AVAILABLE_BUT_NOT_CONSUMED`

<!-- anchor: pattern-1 -->

```
H1   the transcript was on disk, unread for 8 weeks, while a docstring said to read it
H2   the rejection was dated ONE DAY after the documents it rejected
H6   the same page marks Phase 1 satisfied 30 lines below the gap table that denies it
H7   the same page corrects itself 80 lines below the "Meta dropped" decision
H17  a $0.00 refutation sits 250 lines from the blocking claim it refutes
H24  the correct source-precedence control ships TODAY in a sibling client's repo
M-05 F91 - the identical defect class - was fixed the SAME MORNING
M-07 the spec named the scope AND predicted the exact failure of missing it

8 of 37 issues.  Every one of them: the knowledge existed, in our own record,
                 and the next actor did not consume it.
```

⭐ **This is the single most important finding in the case study.** It is not a knowledge problem. It
is an **operationalisation** problem: a sentence is not a mechanism. Every remedy is the same shape —
turn the written knowledge into something that *acts*: a preflight, a supersession edge, a blocking
claim state, an ACK.

## PATTERN 2 — `ABSENCE RENDERED AS A NUMBER`

<!-- anchor: pattern-2 -->

```
H10  COALESCE(FX.RATE, 1)  -  a missing rate becomes parity, silently
H12  'Cross-Channel' AS MARKETPLACE_NAME  -  $244,870.44 onto an unknown member
H15  dailyBudget: 0, orders: 0, status: "active", sku = ASIN, platformCount = boolean
M-01 a search returns zero and the zero is reported as a finding
H8   three Meta spend figures with no window, no as-of, no basis

5 of 37 issues.  And the estate ALREADY KNOWS THE RULE and enforces it
                 structurally - for exactly one measure (COGS coverage).
```

⭐ **The counter-example is the argument.** `MARKETING_EFFICIENCY_MARGIN` returns `NULL` not `0`, and
says why in the view comment, and the frontend independently enforces the same rule. **One measure
got the treatment. Nothing generalised it.** `client_review.py`'s four-state absence model
(`LIVE / LAST_VERIFIED / STALE / UNAVAILABLE`) is the generalisation, and it currently lives only in
the review projection.

## PATTERN 3 — `A CLAIM WITHOUT AN AS-OF`

<!-- anchor: pattern-3 -->

```
H3   MER written once, never reconciled to the implementation
H6   a gap table snapshot, never re-baselined
H17  a blocker refuted and never retracted
H20  FIELDS.md transcribed from types.ts and drifted from it
H23  one call, three dates
M-04 "blocked_by is unused" - TRUE when observed, FALSE when re-used

6 of 37 issues.  Each was TRUE when written.  None carried the date it was
                 true, or the source it was true of.
```

**The remedy is one field, not a system:** every claim carries `as_of` and `source`. R1 and R2 both
did this manually — every claim in R1 carries `Basis`, `Source` and `Expressed`; every row in R2
cites a file and line. **The discipline is proven; the enforcement is not built.**

## PATTERN 4 — `AN OBLIGATION WRITTEN IN PROSE`

<!-- anchor: pattern-4 -->

```
H1   "confirm against the Avoma transcript before this reaches Heather"  -  Not done
H16  "must be announced, not discovered"                                 -  Nothing on file
H19  "do not send cover-note-draft.md until that lands"                  -  Hold, no owner
M-07 "R2's scope therefore includes aldc-launchpad/docs/readouts/"       -  Not read
M-09 13 instrumentation fields specified in spec sec 4                    -  None written

5 of 37 issues.  In every case WE WROTE THE OBLIGATION DOWN OURSELVES,
                 in our own words, and nothing enforced it.
```

⭐ **The cheapest and most under-built capability in the whole matrix.** Four of these five are one
sentence away from being a task with an owner and a dependency edge. `TaskStore.block()` already
exists and already works — the mission's own D1 is correctly blocked on R3 alone. **The primitive is
built. It is not being pointed at prose obligations.**

---

# L. What Delivery #001 teaches Agent Factory

<!-- anchor: sec-l -->

Six lessons. Each names a measurement so Delivery #002 can be graded rather than described.

### LESSON 1 — Operationalise the findings ledger

<!-- anchor: lesson-1 -->

```
OBSERVATION
Previous failure evidence existed and later actors did not consume it. Eight of thirty-seven
issues. In the sharpest case, F91 was fixed on the morning of 2026-08-31 and the identical
defect class - a guard only as wide as the relation it derives over - was committed against a
credential file that afternoon.

ROOT CAUSE
KNOWLEDGE_AVAILABLE_BUT_NOT_CONSUMED. Execution history is STORED (28 findings in
docs/findings.d/, machine-read by factory/findings.py) and NOT OPERATIONALIZED. Nothing consumes
the ledger as a precondition.

CAPABILITY
Known-Failure Preflight. NEW as a mechanism; the knowledge base exists today.

CHANGE TO AGENT FACTORY
A shape matcher at task launch: task shape -> matching prior findings -> the specific guard is
shown AND REQUIRED. Seed it with the three shapes this delivery proves: deny-list over a
credential source; a zero from an unproven instrument; an unqualified object reference.

MEASUREMENT
Known-failure recurrence rate: incidents whose class already has a filed finding, per mission.
Delivery #001 baseline: 2 (M-01 blind zero, M-05 deny-list). MEASURED.

DELIVERY #002 TARGET
0. A repeated known failure should never occur without the later run having been shown the prior
evidence and having declined the guard explicitly.
```

### LESSON 2 — A prose obligation must become a task

<!-- anchor: lesson-2 -->

```
OBSERVATION
Five obligations were written down by us, in our own words, and none was enforced: "confirm
against the transcript before this reaches Heather" (Not done); "must be announced, not
discovered" (nothing on file); "do not send until that lands" (a hold with no owner); "R2's
scope includes aldc-launchpad/docs/readouts/" (not read); thirteen instrumentation fields
(none written).

ROOT CAUSE
MISSING_TASK_OR_DEPENDENCY. A sentence carries no state, no owner and no blocking power.

CAPABILITY
Intent Contract (NEW - measured absent: grep -ril intent_contract factory/ scripts/ is empty) on
top of TaskStore.block (EXISTING and proven - D1 is correctly BLOCKED on R3 alone).

CHANGE TO AGENT FACTORY
Any spec sentence of obligation shape - "confirm", "must be announced", "do not send until",
"scope includes", "record per task" - becomes a task with an owner, a next-check date and a
dependency edge. The mission cannot close over an open obligation.

MEASUREMENT
Obligations declared in a mission spec vs obligations materialized as tasks.
Delivery #001 baseline: 5 declared, 0 materialized. MEASURED.

DELIVERY #002 TARGET
100% materialized, or explicitly waived with a reason recorded in the store.
```

### LESSON 3 — Instrument the run, or run 1 answers nothing about run 2

<!-- anchor: lesson-3 -->

```
OBSERVATION
Spec section 4 lists thirteen per-task instrumentation fields and calls the coordination cost "the
point, not a by-product." NONE was written. estimate_minutes exists for all eight tasks, all
basis ASSUMED; actual_minutes does not exist. And acceptance check 1 - "three task_claim grants,
three concurrent sessions" - is not satisfied: three claim files exist, ALL carrying pid 17172
and actor mission-manager, and R3 never claimed at all.

ROOT CAUSE
INSTRUMENTATION_GAP. The instrument was specified in prose and never built. The spec even warned
that checks 1, 2 and 5 "can pass over an absence" - and check 1 then did exactly that.

CAPABILITY
Reliability instrumentation. PARTIAL - runs.py already draws RECORDED / RECONSTRUCTED /
NOT-RECORDED, and events.py has nine closed kinds with mandatory verdicts. This mission wrote to
neither.

CHANGE TO AGENT FACTORY
A task-execution event carrying start, end, model, effort, retries and outcome. The task contract
refuses to close without an actual_minutes, exactly as it already refuses to close without
evidence. Reuse the EvidenceRequired shape - it is proven refusing.

MEASUREMENT
Percentage of tasks with a RECORDED actual, and percentage of acceptance checks demonstrated
rather than asserted.
Delivery #001 baseline: 0% and 2 of 5 (checks 3 and 4). MEASURED.

DELIVERY #002 TARGET
100% RECORDED actuals. Every acceptance check demonstrated, or explicitly labelled as capable of
passing over an absence.
```

### LESSON 4 — Typed Claims, because the manual version already worked

<!-- anchor: lesson-4 -->

```
OBSERVATION
Two claims were inherited into this mission. The one MARKED "verify" (the metric hierarchy) was
refuted at escape distance 1 and never became mission knowledge. The one NOT marked (blocked_by
is unused) propagated into a filed spec and had to be challenged by a human.

ROOT CAUSE
STALE_CONTEXT, with the mechanism's effectiveness demonstrated by the contrast between the two.

CAPABILITY
Typed Claims. PARTIAL - evidence.py validates basis and close(require=) refuses; R1's five-level
client-claim vocabulary (CONFIRMED / SUPPORTED / INFERRED / ASSUMPTION / UNKNOWN) was applied
BY HAND, to 38 claims, with a source on every one.

CHANGE TO AGENT FACTORY
Promote R1's vocabulary from prose convention to type. A claim carries basis, source and as_of.
A claim below SUPPORTED cannot be cited as a client requirement. Inheriting a claim across a
session boundary REQUIRES a verification task.

MEASUREMENT
Claims inherited across a session boundary with no verification state.
Delivery #001 baseline: 1 of 2 (blocked_by). MEASURED.

DELIVERY #002 TARGET
0. And: percentage of published client requirements whose basis is CONFIRMED or SUPPORTED with a
resolvable source. Delivery #001 baseline from R1: 19 CONFIRMED + 7 SUPPORTED of 38 = 68%.
```

### LESSON 5 — The scope of a handoff needs a verdict, not a reading

<!-- anchor: lesson-5 -->

```
OBSERVATION
The spec put aldc-launchpad/docs/readouts/ in R2's scope AND PREDICTED THE EXACT FAILURE of
missing it: "a diff that reads one repo and reports 'no prior design exists' would be a blind
instrument - three designs already exist." R2's method note records aldc-launchpad as
NOT-VISIBLE and outside its read scope. Nothing reconciled the two. The three designs were read
by neither worker.

ROOT CAUSE
MANUAL_HANDOFF. Prose cannot enforce itself, however precisely it predicts its own failure.

CAPABILITY
Typed Handoff + ACK/NACK. NEW - .data/handoffs/ holds three files, all from 2026-08-22, none from
this mission.

CHANGE TO AGENT FACTORY
Scope becomes a typed list. The worker ACKs (read) or NACKs (cannot reach, with a reason) each
item. A task cannot close with an item carrying neither. A NACK is a legitimate answer and
becomes a visible gap with an owner.

MEASUREMENT
Scope items with neither an ACK nor a NACK, per task.
Delivery #001 baseline: at least 1 of R2's ~4 scope items. MEASURED.

DELIVERY #002 TARGET
0.
```

### LESSON 6 — Generalise the absence rule the estate already enforces once

<!-- anchor: lesson-6 -->

```
OBSERVATION
Five issues are the same defect: an absence rendered as a number. And the estate ALREADY KNOWS
THE RULE - MARKETING_EFFICIENCY_MARGIN returns NULL not 0 where COGS coverage is zero, says so
in its view comment, and the frontend enforces it independently ("Coercing missing cogs to 0
would fabricate a 100% margin - the Lectric CM trap"). One measure got the treatment. Twelve
contracted fields on the same dashboard did not.

ROOT CAUSE
SEMANTIC_CONTRACT_GAP. A rule enforced by convention at one site instead of by type at every
site.

CAPABILITY
Semantic Contracts. PARTIAL and real - client_review.py rule 3 keeps LIVE / LAST_VERIFIED /
STALE / UNAVAILABLE distinct, and contract.py keeps UNMEASURABLE out of FAIL. Both exist. Neither
reaches the field contract.

CHANGE TO AGENT FACTORY
Extend the four-state absence model from the review projection down into the field contract. A
contracted field with no resolvable source renders NOT_REPORTED and cannot render a literal.
Adopt R2's five prescribed structural columns as the warehouse-side expression of the same rule:
GRAIN_LEVEL, DATA_ORIGIN_KEY, ROW_COUNT, METRIC_BASIS, TAXONOMY_PARSE_STATUS - measured present
in ZERO files today.

MEASUREMENT
Contracted fields rendering a literal with no source. Delivery #001 baseline: at least 12.
DOCUMENTED (R2 M1-M17).

DELIVERY #002 TARGET
0 in any client-facing surface the Factory publishes.
```

---

# M. Evidence discipline — the register for this document

<!-- anchor: sec-m -->

Every load-bearing claim, its basis, and how to regenerate it.

| Claim | Basis | Regeneration |
|---|---|---|
| Mission has 9 tasks, 7 dependency edges, created 2026-09-01T00:52:14Z | `MEASURED` | `python -c "import json,io;[print(r) for r in map(json.loads,io.open('.data/tasks.jsonl',encoding='utf-8')) if r.get('task','').startswith(('0d26','2b9a','3d05','e397','1785','933e','3877','b1f3','9108'))]"` |
| Zero `claim` events on any mission task (3 in the whole store, none on this mission) | `MEASURED` | census `kind` over `.data/tasks.jsonl`, filtered to the 11 mission ids |
| Duplicate tasks created 02:13:52Z, superseded 03:14:03Z — 3,611s | `MEASURED` / `DERIVED` | timestamp difference of the two events |
| Three claim files, all pid 17172, actor `mission-manager`; R3 never claimed | `MEASURED` | `cat .data/claims/task--res-*.json` |
| `actual_minutes` does not exist for any task; all 8 `estimate_basis` are `ASSUMED` | `MEASURED` | `cat .data/missions/marketing-model-reconstruction-v1.json` |
| Exactly one credential-use row, READ, value never printed, no connection made | `MEASURED` | `cat .data/credential-use.jsonl` |
| The mission produced zero rows in `.data/events.jsonl` (last row 2026-08-31T04:50:35Z) | `MEASURED` | `tail -1 .data/events.jsonl` |
| R1 = 43,110 bytes, R2 = 43,901 bytes | `MEASURED` | `wc -c docs/evidence/marketing-model-v1/*.md` |
| R1 and R2 headers name the superseded duplicate task ids | `MEASURED` | `head -5` of each evidence file, vs the `SUPERSEDED` rows in `.data/tasks.jsonl` |
| Spec §0.5 puts `aldc-launchpad/docs/readouts/` in R2's scope; R2's method note records it NOT-VISIBLE | `MEASURED` | `docs/specs/marketing-model-reconstruction-v1.md` §0.5 vs `R2-repo-wiki-diff.md` "Method note" |
| 28 filed findings in `docs/findings.d/` | `MEASURED` | `ls docs/findings.d/F*.md \| wc -l` |
| `client_review.py` rule 1 cites the 2026-08-31 deny-list credential exposure by name | `MEASURED` | module docstring, `factory/client_review.py:1-40` |
| The Navira review yaml carries 5 delivered items, 2 decisions, 3 risks, 6 next steps, all with `origin` | `MEASURED` | `missions/client-review-v1/reviews/navira-marketing-model.yaml` |
| No Intent Contract object exists | `MEASURED` (via `RECON.md`, which shows the command) | `grep -ril intent_contract factory/ scripts/` |
| Every Delivery-A fact (H1–H25) | `DOCUMENTED (R1)` / `DOCUMENTED (R2)` — **one hop** | the cited line in `R1-stakeholder-evidence.md` or `R2-repo-wiki-diff.md`, each of which cites its own primary file and line |
| Wave 1 wall clock 11m17s | `DERIVED`, **weak** — both closes were batched by the mission-manager 0.4ms apart, so this measures the recording, not the tasks | timestamp difference |
| Every Agent Factory counterfactual in §H and §I | `SIMULATED` | none — these were never observed |
| Time saved, cost avoided, hours of rework | `NOT_RECORDED` | nothing in the estate records them, and this document does not invent them |

### M.1 Three claims this document deliberately refuses to make

1. **"Agent Factory would have prevented X."** Every counterfactual is labelled `SIMULATED` and
   names the mechanism, its current maturity, and what remains to be built. Two capabilities that
   sound central — Source Cartography and Intent Contract — have **never been exercised**; the
   cartography task is the blocked one.
2. **"The mission proved parallel execution."** It did not. Three claims share one pid and R3 never
   claimed. The spec itself warned that check 1 could pass over an absence, and it did.
3. **"Run 1 produced the routing dataset."** It did not. That was the stated point of run 1 and it
   is `NOT_RECORDED`.

---

# N. Open items this reconstruction created or confirmed

<!-- anchor: sec-n -->

Ordered by cost of leaving them.

| # | Item | Owner | Status |
|---|---|---|---|
| 1 | **Rotate the three exposed credentials** — `paulrussell` first; it spans non-prod **and production** | Paul | **Not confirmed** |
| 2 | Create the read-only Snowflake role in `og35375` so R3's pre-flight can measure rather than assume | Paul | Open — blocks R3 → D1 → D2 → D3 → D4 → D5 |
| 3 | Correct Jira comment **36056** — the metric boundary's justification is a phantom ask | ALDC | Open; Atlassian MCP unavailable, may need pasting by hand |
| 4 | Announce the ratio movement from stripping Lectric (`GP-319:98`: *"must be announced, not discovered"*) | ALDC | Open, owed since 2026-08-25 |
| 5 | **Fix the provenance in R1 and R2's own headers** — both name superseded duplicate task ids | This session's finding | **New** |
| 6 | **Extend R2's scope to `aldc-launchpad/docs/readouts/`** — the three GP-319 designs are read by nobody | This session's finding | **New** |
| 7 | File the unfiled findings: the deny-list credential defect; the blind-search defect; the stale `blocked_by` claim; the MER contradiction | ALDC | Open — all four evidenced, none filed |
| 8 | Correct the `blocked_by` row in `docs/specs/client-review-loop-v0.md`'s leads table | ALDC | Open |
| 9 | Mark `nicholas-metric-matrix-readout.md` §6 and `attribution-design-decision.md` as superseded before D3 opens them | ALDC | Open — **this trap is armed** |
| 10 | Send the reply to Nicholas and ask for the dimensions table | ALDC | Open since 2026-08-04 |
| 11 | Build the per-task instrumentation before run 2, or run 2 answers nothing run 1 did not | ALDC | **New** |

---

## Appendix — the numbers a CEO will ask about

Every one traced. `DOCUMENTED (R1)` or `DOCUMENTED (R2)` means one hop from a cited file and line.

| Figure | What it is | Basis |
|---|---|---|
| **$457,425** | Ad spend (15.6%) carrying `PRODUCT_ID = '-1'` — a campaign-level aggregate reported *instead of* a product. Locked decision: give it an explicit `(no product key)` row; **do not allocate it — "that is invention"** | `DOCUMENTED (R1 L-7)` |
| **84.35%** | The ceiling on product-keyable ad spend | `DOCUMENTED (R1 L-7)` |
| **$244,870.44 / 768 rows** | Cross-channel spend orphaned onto Power BI's unknown member, unselectable by any positive slicer choice | `DOCUMENTED (R2 M24)` |
| **~31%** | Amazon ad spend silently dropped by the old brand aggregation — **including the #1 spender, TF Publishing** | `DOCUMENTED (R2 M9)` |
| **~27%** | Product cards left with an empty top-products section and a dead drill-down by an ASIN/SKU join that matched almost nothing | `DOCUMENTED (R2 S9)` |
| **$3,374.90** | Amazon US Sponsored Display spend missing from the divergent `WAREHOUSE_TEST_GP226` copy | `DOCUMENTED (R2 §0)` |
| **$2.76M** | Lectric sales with zero cost and zero ad spend; stripping it moves gross −2.13%, net −2.27%, and **raises** margin % and TACoS/MER | `DOCUMENTED (R1 CONTRADICTION 4)` |
| **~14 copies / 6 schemas** | Existing copies of the marketing table family — the stated reason a conformed core fact was rejected | `DOCUMENTED (R1 L-2)` |
| **16** | Visible ROAS measures with no stated default | `DOCUMENTED (R1 O-1)` |
| **721 / 369 / 352** | Rows in the client's own metric matrix; rows tagged live; rows the client scoped out himself | `DOCUMENTED (R1 C-16, C-17)` |
| **10** | Marketing-path objects with no repo-managed DDL; **5** of them read unqualified into the divergent schema | `DOCUMENTED (R2 M18)` |
| **6** | Objects the dashboard still reads unqualified today — `DEC-2` in the client review | `DOCUMENTED (R2 §0)` |
| **38 / 7 / 18 / 15** | R1's claims with basis / contradictions / locked decisions verified / open client questions | `DOCUMENTED (R1 §6)` |
| **14 / 11 / 23 / 8** | R2's LOCKED / STALE / MISSING / prior-art patterns | `DOCUMENTED (R2 header)` |
| **0** | Client sign-offs on anything in the marketing model — **a real ZERO from an instrument proven able to see the positive case**, because the same corpus recorded GP-292's acceptance when it happened | `DOCUMENTED (R1 C-35)` |
