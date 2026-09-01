# D1 — Requirements & uncertainty synthesis (Navira marketing model)

**Written 2026-09-01** from `R1-stakeholder-evidence.md`, `R2-repo-wiki-diff.md` and
`R3-cartography.md` — the committed evidence, not the handoff's summary of it.
`evidence_class` **TARGET** · basis **DERIVED** (this document derives; its inputs measure).

D1 states what the model must do, what is genuinely settled, and what is not. **It resolves
nothing that the evidence leaves open.** Where the record contradicts itself the contradiction is
carried forward intact, because a synthesis that quietly picks a winner is how an assumption
becomes a requirement.

---

## 0. The classification, and why each row carries one

Every row below is labelled with exactly one basis. The labels are not decoration — D2 selects
questions from them, D3 may only build on some of them, and D4 exists to attack the weakest.

| label | means | may D3 build on it? |
|---|---|---|
| `MEASURED` | someone ran an instrument and recorded the result | **yes** |
| `DOCUMENTED` | written in a client-authored or contemporaneous artefact | **yes** |
| `KNOWN` | client's own words, in a transcript or minute we hold | **yes** |
| `DERIVED` | follows from measured/documented facts by stated reasoning | yes, with the derivation shown |
| `ASSUMED` | believed, no citable source | **no** — must be promoted or dropped first |
| `CONTRADICTORY` | two sources disagree and neither has been retired | **no** — needs a decision |
| `NOT_RECORDED` | should exist, does not, and the absence is itself the finding | **no** |
| `REQUIRES_CLIENT_DECISION` | only the client can settle it | **no** — D5 gate |
| `REQUIRES_TECHNICAL_VERIFICATION` | settleable by us, with work not yet done | **no** — becomes a D2/D3 task |

⭐ **A basis is a claim about provenance, not about confidence.** `DOCUMENTED` says a document
exists, not that the document is right — S2 below is `DOCUMENTED` on both sides and still
`CONTRADICTORY`.

---

## 1. Requirements — what the model must do

### 1.1 From the client's own voice (`KNOWN`)

These come from the 487-line Lori Beck ↔ Heather Tabor transcript or contemporaneous minutes.
R1 counts **19 CONFIRMED** client claims; the ones that constrain a dimensional design are:

| id | Requirement | basis |
|---|---|---|
| **RQ-1** | Cross-channel marketing efficiency must be answerable in one place — spend against actual revenue, not platform-reported conversion value | `KNOWN` |
| **RQ-2** | Per-channel platform ROAS must remain visible for in-channel optimisation | `KNOWN` |
| **RQ-3** | Product/SKU-level efficiency for Amazon, via the existing product bridge | `KNOWN` |
| **RQ-4** | UK data merges into the core model | `KNOWN` (agreed 2026-07-08) |
| **RQ-5** | Profit, not only top-line — margin after ad spend | `KNOWN` |

### 1.2 ALDC design decisions frequently mistaken for client asks (`DOCUMENTED`)

⛔ **R1 §0.2 is load-bearing and is repeated here because D3 will otherwise inherit it wrongly:**
the Tier 0–4 model, blended MER as headline, the core-10, the conformed-core-plus-extensions shape
and the Kimball framing are **all ALDC-authored**. A wiki line reading *"DECIDED 2026-05-29 (Paul)"*
is our decision on the client's behalf. It is binding on us; it is **not** evidence of a client
requirement, and it must not be presented to the client as one.

R1 counts **6** such decisions and is explicit about each.

### 1.3 Constraints the replacement must honour (`DOCUMENTED`, from R2's 14 LOCKED)

| id | Constraint | why it binds |
|---|---|---|
| **L2** | Platform-attributed value is **never summed across channels** | honoured in four layers; violating it is the classic double-count |
| **L3** | The locked headline is **blended MER** — *not* Contribution Margin | `ATTR:100` Decision 1, 2026-05-29 |
| **L4/L5** | Contribution Margin is coverage-gated; `COGS_COVERAGE_PCT` must be **surfaced, not assumed** | a hidden coverage gap renders as a confident wrong margin |
| **L7** | Amazon attribution window is 30-day | |
| **L8** | Google/Meta attribution grain is **CHANNEL**, by design | not a limitation to design away |
| **L10** | Ratios are `SUM(num)/SUM(den)` computed at the semantic layer | never an average of ratios |
| **L11** | Multi-tenancy is `ENTITY_CODE`; cross-tenant bleed is the **catastrophic** failure mode | |
| **L12** | The agency dimension is dimension-sourced, never a hardcoded label | |
| **L13** | There is **no canonical cross-channel marketing star today** — we are building the first | this is the mission |
| **L14** | One name for the cost column, never aliased | |

⭐ **L3 and the corrected hierarchy.** The inherited order *Contribution Margin → MER → Platform
ROAS* was **REFUTED** by R2 against `ATTR:100`/`ATTR:111`. The correct order is
**Blended MER → Contribution Margin → Platform ROAS**. The refuted version must not be
re-inherited, and must not be silently deleted either — downstream needs to know it was tested.

---

## 2. Contradictions carried forward — `CONTRADICTORY`

**None of these is resolved here.** Each needs a decision or a measurement, and each is named so
D3 cannot build over it by accident.

| id | Contradiction | why D1 will not settle it |
|---|---|---|
| **X-1** | **MER is defined as the reciprocal of what three code layers compute.** Doc (`ATTR:29`, `:94`) says `SPEND / SALES`; `_MONTHLY.sql:50`, `metrics.ts:99`, `FIELDS.md:38` say `SALES / SPEND`. The doc's formula is **already shipped as TACoS** (`metrics.ts:95`), and the doc argues *against its own formula* at `:37`. | Three layers agreeing is a **majority, not a proof**, and `ATTR:100` locked "blended MER" without writing the fraction. Filed as **F97**. ⛔ This sits on the **headline metric**. |
| **X-2** | **Source-of-truth: the clone.** `WAREHOUSE_TEST_GP226` holds **32** `MARKETING_*` objects against **35** across all authoritative schemas, and **5 exist under no authoritative name**. R2 found ~10 marketing objects still *reading* from it, and its `MARKETING_EFFICIENCY` copy misses Amazon US Sponsored Display ($3,374.90). | A clone simultaneously **ahead in surface area and behind in data**. Code referencing it is not evidence it is authoritative. `MEASURED` by R3. |
| **X-3** | **The metric-visibility boundary rests on a phantom reason.** GP-319:183-184 rests a decision on *"a recollection of Heather's ask"*; the transcript contains no such ask. | The remedy already shipped for a **different, sound** reason (GP-318 §D9). The *record* is still wrong, in **Jira comment 36056**. Correcting it is a deliverable, not a design input. |
| **X-4** | "No new fields in Daily" vs "add cross-channel ad-spend columns to Daily" | R1 CONTRADICTION 3 |
| **X-5** | Agency in the Daily model: client-agreed, then reversed by us | R1 CONTRADICTION 4 |
| **X-6** | GP-296 blocks sign-off / GP-296 was never a blocker | R1 CONTRADICTION 5; GP-296 has **no wiki page** — unreadable |
| **X-7** | "Purchases is absent" vs "Purchases needs no pipeline work" | R1 CONTRADICTION 6 |
| **X-8** | ⛔ **A conformed core fact was recommended twice and then rejected.** `nicholas-metric-matrix-readout.md` §6 and `attribution-design-decision.md` both recommend it (2026-08-24); **GP-319 rejected it 2026-08-25** — the client already carries ~14 copies of the marketing family across 6 schemas. **Both recommending documents still read as current.** | ⭐ **This is the trap that would wreck D3.** It must be in D3's context manifest before D3 opens either document. |
| **X-9** | The model-review call is dated 2026-07-08 in one place, 2026-08 in another | R1 CONTRADICTION 2 |

---

## 3. What is missing — `NOT_RECORDED`

An absence recorded as an absence, never as a zero.

| id | Absence | consequence |
|---|---|---|
| **N-1** | ⭐ **The client's dimensions table never arrived** — described by Nicholas as *"likely the bigger half"*. We hold `campaign_id` + `campaign_name` and nothing else: no brand, portfolio, ad type, targeting, match type, placement. | **Blocks any dimensional design from claiming completeness.** No design may present a dimension list as *responsive* to a request that was never fulfilled. |
| **N-2** | **No client sign-off exists on anything in the marketing model.** Verified as a **real zero** — the instrument was shown able to see one. | D5 cannot claim acceptance. |
| **N-3** | **`MARKETING_EFFICIENCY` has no `CLICKS` and no `IMPRESSIONS`** — yet `FIELDS.md:36-37` contracts CTR and Avg CPC from them. The dashboard opens a **second, unreconciled query** against the raw fact and LEFT JOINs it back. | Spend and reach for the same (platform, region, day) come from two objects, two date floors, **no reconciliation test**. |
| **N-4** | **No `CONVERSIONS` on any `REPORT_COMMON` object.** Brand/product/platform rows carry `0`. | ⛔ **A fabricated zero for a metric that is simply not on the object** — an absence rendering as a number, the exact defect class this estate has paid for before. |
| **N-5** | **No campaign-grain USD spend.** `COST` has no currency column and no USD sibling; Google COST runs **~13% high**. | An entire dashboard view — the Campaign lens — **ships with its money columns switched off**. |
| **N-6** | Jira is entirely **NOT-VISIBLE**; 10 referenced tickets have no wiki page (GP-290/292/295/296/301/303/317/320/321/325). Heather's 2026-08-06 and 08-10 emails are in no repo. | Every claim citing them is capped at `SUPPORTED`, never `CONFIRMED`. |
| **N-7** | UK ad-data validation (agreed 2026-07-08) — no record of arrival. | `NOT_RECORDED`, not "didn't happen". |

---

## 4. Decisions required — `REQUIRES_CLIENT_DECISION`

R1 verified **15** open client questions. These are the ones that change the shape of a design;
each is an obligation on D5, not a thing D3 may assume.

| id | Decision | blocks |
|---|---|---|
| **CD-1** | ⭐ **Which ROAS is canonical?** **16 visible ROAS measures**, no stated default. *"An Excel user picks one at random and gets an answer defensible in isolation and irreconcilable with a colleague's."* | **Tier 0 build.** Named as one of *"two human decisions first."* |
| **CD-2** | **Sign-off on new measure names** — they land on a client-visible model and additive means we live with them. | **Tier 0 build.** |
| **CD-3** | **Capped or uncapped Calibrated ROAS?** They diverge hard (calibration factor ≈ 6.4): uncapped Amazon 32.5x / Google 18.0x / Meta 6.4x; capped collapses to Platform ROAS. **Both built.** Surfaced 2026-06-05, unanswered ~3 months. | Compounds CD-1 — a *second* ROAS ambiguity beneath the first. |
| **CD-4** | **Is the `Amazon (Ads API)` column blank because Amazon is the reference taxonomy, or unfilled?** Empty in all **721 rows**; blank and "not available" render identically. | *"Whether '236 Amazon-only metrics' is a finding or an artifact."* One line of reply settles it. |
| **CD-5** | **Walmart Connect / Target Roundel / eBay Ads in scope?** 64 in-scope rows, no connector, no credentials. | 3 platforms or 6. ⭐ Note: **it costs nothing to design for six.** |
| **CD-6** | **`Purchases` / `Cost per Purchase` in scope?** Two of the durable ten; both Google and Meta report them; the model has neither. | See X-7 — pipeline work is smaller than the question implies. |
| **CD-7** | ⭐ **What window does "last year" mean?** Calendar 2025 / YTD 2026 / trailing 12m / last 12 complete months. **The client used two of these in one exchange.** Material: Meta begins 2026-04-20, so calendar-2025 contains **no Meta at all**. | **Every quoted total.** |
| **CD-8** | **Did Navira run Meta advertising in 2025?** Our first Meta data is 2026-04-20. | Until asked, 2025 Meta is `ZERO`-or-`NOT_RECORDED`, **unresolved**. Publishing it as zero would be a claim about the client's behaviour. |
| **CD-9** | TACoS formula rebase to `spend ÷ total sales` — relabel shipped, rebase held on Lori's "advertising cost" answer. | Whether TACoS has one definition or two. |
| **CD-10** | The brand→entity ownership decision. | ⚠ **Under-specified even as a question — needs restating before it can be asked.** |

---

## 5. Settleable by us — `REQUIRES_TECHNICAL_VERIFICATION`

These need no client. Each becomes a candidate D2 question or D3 pre-work.

| id | Verification | why it is not yet answered |
|---|---|---|
| **TV-1** | ⭐ **Prove the grain of every candidate fact.** R3 identified key-shaped columns **by naming convention only**. | A column called `CAMPAIGN_ID` is a *hypothesis* about the grain. Uniqueness has not been tested. **This is D3's first obligation.** |
| **TV-2** | **Resolve X-2**: is `WAREHOUSE_TEST_GP226` a stale copy, an ahead-of-main development branch, or a configuration defect? | R3 deliberately did not widen scope to the clone. |
| **TV-3** | **Reconcile spend-vs-reach** across `MARKETING_EFFICIENCY` and `MARKETING_FCT_ACTIVITY_UNIFIED` (N-3): two date floors, no test. | |
| **TV-4** | **Establish TEST's data currency.** R3 measured structure; a Navira re-land into TEST was *planned, not executed*, and Lectric confirmed greenfield for the agency slice. | ⛔ **Structure in TEST is trustworthy; row-level distribution is not.** No grain claim may rest on a TEST row count. |
| **TV-5** | Open `Data Metrics for Advertising Dashboard - ALDC annotated.xlsx` (721 rows) directly. | Reaches us only through two readers that agree with each other — ⭐ *"two internally-consistent readers is corroboration, not verification."* |
| **TV-6** | Read `navira-data-issue-register.md`; cited as the DQ register twice, never read. | |

---

## 6. Obligations that bind D2–D5

Surfaced here rather than buried, so no downstream task inherits them silently.

```
D2  must generate questions that discriminate CD-1, CD-3, CD-7 — the three
    ambiguities that change every number, not merely more questions.
    Must NOT treat X-1 as resolved.

D3  MUST receive X-8 in its context manifest BEFORE it opens
    nicholas-metric-matrix-readout.md or attribution-design-decision.md.
    Both still read as current; GP-319 rejected their recommendation.
    MUST declare the grain in writing before designing (TV-1).
    MUST NOT present a dimension list as responsive to the client (N-1).
    MUST NOT rest any grain claim on a TEST row count (TV-4).

D4  Falsification targets, in order: TV-1 (grain), X-1 (MER), X-2 (clone
    authority), N-4 (the fabricated conversions zero).

D5  Cannot claim client acceptance — N-2 is a verified real zero.
    Carries CD-1..CD-10 as the decision list.
    Owes the X-3 correction to Jira comment 36056.
```

---

## 7. What D1 deliberately did not do

- **Did not resolve X-1.** The evidence leans one way; leaning is not deciding, and the majority
  belongs to code that could equally be three consistent implementations of one original error.
- **Did not widen scope to the clone** to settle X-2.
- **Did not promote any `SUPPORTED` claim to `CONFIRMED`.** Jira is `NOT-VISIBLE`; second-hand
  stays second-hand.
- **Did not treat R3's naming-convention keys as a grain.** They are labelled as hypotheses in R3
  and remain hypotheses here.
- **Did not delete the refuted metric hierarchy** — downstream must know it was tested and failed,
  not merely that the current one is current.

## 8. Counts, each regenerable

```bash
# client claims by basis, contradictions, locked decisions, open questions
grep -c '^| \*\*C-' docs/evidence/marketing-model-v1/R1-stakeholder-evidence.md
grep -c '^### .*CONTRADICTION' docs/evidence/marketing-model-v1/R1-stakeholder-evidence.md
# MARKETING_* inventory, authoritative vs scratch
python scripts/snowflake_bootstrap_r3.py --cartograph --warehouse COMPUTE_WH
```

| | count | source |
|---|---:|---|
| client claims in R1's ledger | 38 | R1 §6 |
| contradictions carried forward | 9 | §2 above (7 from R1 + X-1 + X-2) |
| locked constraints | 14 | R2 §1 |
| open client decisions | 10 of 15 shaping design | §4 |
| technical verifications owed | 6 | §5 |
| `MARKETING_*` objects | 84 (35 authoritative / 49 scratch) | R3 `MEASURED` |
