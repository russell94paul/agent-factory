# ECHELON 0 · RECON — a verified performance record for prop-futures traders

**Opened 2026-09-01. Status: IN PROGRESS — no go/no-go signed.**
Read-only. No spend. Nothing built. RECON is allowed to return **no**.

---

## The venture under test

> A **portable, tamper-evident performance record** for retail prop-futures traders: the
> `predictions` frozen ledger already built in `neurospect-learn`, fed by **broker-attested fills**
> instead of self-report.

Not a journal. Journals are solved (Tradezella, TraderSync, Edgewonk — Tradezella already ships
Prop Firm Sync). Every one of them is a self-reported log the trader can edit. The proposition here
is the opposite: **a record whose value is that its owner cannot change it.**

---

## Why this venture and not the six in the Field Manual

The topic `leads` was opened first and **killed on measurement** — see
[`leads-no-go-2026-09-01.md`](./leads-no-go-2026-09-01.md).

The replacement was chosen from a landscape sweep of retail prop futures (2026-09-01), which found
four candidate gaps. Ranked:

| # | Gap | Status |
|---|---|---|
| **G1** | No portable, tamper-evident track record for prop-futures traders | ⭐ **This venture** |
| G2 | No *forward-looking* counterparty monitor (all trackers are post-mortems) | Held — real, and unbuildable by affiliates |
| G3 | Nobody independently audits the prop firms' **simulators** | Held — needs licensed market data |
| G4 | Live rule-aware pre-trade guard | ⚠ PARTIAL, not absent — copiers already do much of it |

Two candidate ideas were **killed during the sweep** for already existing, which is why the sweep
ran before the design:

- multi-account risk allocation → Tradecopia / Tradesyncer / SyncFutures / Thor already ship
  per-account drawdown stops, session windows and symbol whitelists.
- firm comparison / payout tracking → saturated, and structurally conflicted (affiliates are paid
  on evaluation sales, so the incentive runs toward "yes, they pay").

---

## The five RECON questions

| # | Question | Verdict |
|---|---|---|
| **Q1a** | Can fill-level history be obtained from a funded account via a firm-sanctioned read-only route? | ✅ **YES** (Topstep) |
| **Q1b** | Can a **third party** obtain it **without holding credentials that can also trade**? | ⛔ **NO** — see below |
| **Q2** | Do firm terms permit a third party to ingest **and publish** account performance? | ⛔ **CONFLICTED — top blocker** |
| **Q3** | Funded accounts are simulated. What can the record honestly attest? | ✅ Answered — see below |
| **Q4** | Who pays? | ❓ OPEN — needs humans, not agents |
| **Q5** | Does publishing a performance record engage FSMA s21 financial promotion? | ⚠ Partly answered — narrower than feared |

---

## Q1a — ACCESS · **YES**, for Topstep, cheaply

`REPORTED` unless marked otherwise.

- TopstepX / ProjectX Gateway API: REST at `api.topstepx.com`, SignalR hubs at `rtc.topstepx.com`.
- **Cost $29/month**, $14.50 with promo code `topstep`. *(Corrects the working assumption that API
  access was free.)*
- ⭐ Topstep explicitly permits, on private servers: *"Historical data storage, Research and
  backtesting, Logging and analytics, A read-only dashboard."* Only order placement is prohibited
  remotely. **This is close to a written description of the product.**
- Third-party connections permitted but unsupported: *"at your own risk… Topstep and ProjectX don't
  affiliate with, endorse, or support any external vendor or platform offering API integrations."*
- ⛔ **Tradovate prop accounts do NOT allow direct API access** — Tradovate community thread, user
  `Frik`, 2024-10-19: *"we know that the Prop Accounts do not allow direct API access."*
  ⚠ **Basis: REPORTED by a user, not confirmed by Tradovate staff in that thread.** A retail
  Tradovate account is different and does expose `fill/list` + `auth/accessTokenRequest`.
- Apex prohibits *fully automated bots* (termination + fund confiscation). ⚠ That is a rule about
  **execution**, not about **reading**. Do not treat it as a bar on ingest without checking.

### Market data is NOT required

The core product needs **account** endpoints only — fills, times, sizes, equity, and the trader's
own pre-committed calls. It does **not** need an exchange feed.

| Product | Market data licence |
|---|---|
| The verified record | **No** |
| Charts / replay / MAE-MFE / slippage-vs-reference | Yes |
| G3 simulator audit | Yes, unavoidably |

⚠ One open item: confirm that republishing **your own fill prices** is not caught by exchange
redistribution terms. Reasoning says no — a fill is a transaction record, not a market data feed —
but that is `DERIVED`, not cited.

---

## Q1b — ATTESTATION · ⛔ **NO on the ideal**

`REPORTED`, from the ProjectX Gateway API documentation and TopstepX help.

- Auth is **JWT, 24-hour tokens**, via `POST /api/Auth/loginKey` with `userName` + `apiKey`.
- The trader **mints the key themselves**: TopstepX → Settings → API → Add API Key. So this is *not*
  password sharing, which is better than assumed.
- ⛔ **But there is no read-only scope.** The documentation states the API key *"grants full trading
  access to every eligible account under your profile and should never be shared."*

**Therefore the ideal trust model is unavailable.** A service cannot ask a trader for a credential
that can liquidate their funded accounts, in direct contradiction of the vendor's own instruction,
and simultaneously claim to be the trustworthy party in the arrangement.

### The design consequence — apply the E5 doctrine

`neurospect-learn` §E5 already settled the equivalent problem: the app cannot see a TradingView
replay, so it cannot prove the user did not peek — *and claiming otherwise would have been the one
unrecoverable error.* What it proves instead is that **the record cannot lie**.

The same move applies here, and it is the honest one:

> We cannot prove the trader did not intercept the pull.
> We prove instead that **the record was sealed at the moment of pull and has not changed since.**

Concretely: a **service-published, versioned ingest agent** runs on the trader's own machine holding
their own key; it hashes on receipt and submits the sealed record. That yields **tamper-evident**,
not tamper-proof. It is materially stronger than an editable CSV and materially weaker than a
server-side pull, and the published attestation must say exactly that.

Three options were considered and two rejected:

| Option | Verdict |
|---|---|
| Service holds the trader's API key and pulls server-side | ⛔ Rejected — full trading access; vendor says never share; likely a custody/regulated-activity question of its own |
| Trader exports and uploads a file | ⛔ Rejected — collapses the proof entirely; this is just a journal |
| **Sealed ingest agent, trader-hosted, hash-on-receipt** | ✅ **The workable second-best** |

**The right long-term ask** is a read-only API scope from ProjectX/Topstep. It is consistent with
their own published policy — they already sanction a "read-only dashboard" — so it is a legitimate
feature request rather than a fantasy. It is not a dependency for v1.

---

## Q3 — WHAT THE RECORD CAN HONESTLY ATTEST · ✅ answered

⭐ The structural fact that governs everything: **at nearly every retail futures prop firm in 2026 —
Apex and Lucid among those named — the funded account is a simulated environment paying real cash.**
Orders reach a simulated matching engine, not the exchange. `REPORTED`.

So a verified record from a prop account **is not a verified record of trading in the market**.
Anyone who claims otherwise is lying. The attestation must read approximately:

> This record attests that the call preceded the outcome, that it was not edited after commitment,
> and that the fills are as the firm reported them.
> **It does not attest that these fills occurred in the market**, because funded accounts are
> simulated.

**This sentence is the differentiator, not the disclaimer.** Nobody else in the market will say it.

---

## Q2 — PERMISSION · ⛔ **CONFLICTED. This is now the top blocker.**

`REPORTED`, from Topstep's own Terms of Use and help pages. **Topstep's documents contradict each
other**, and the contradiction sits exactly on this venture.

**Against — Terms of Use:**

> *"Access to your Account and the Services is protected by login Data, which you are prohibited
> from making available to, or sharing with, any third party."*

> ⛔ *"You may not **transfer or combine your Account's performance**, service parameters, Data, or
> any other information **between products** or with any other User."*

**For — TopstepX API Access help page:**

> Permitted on private servers: *"Historical data storage, Research and backtesting, Logging and
> analytics, A read-only dashboard."*
> Third-party connections are permitted but unsupported — *"at your own risk."*

### What survives the contradiction

The **login-data clause resolves cleanly in favour of the trader-hosted design** and independently
confirms Q1b's conclusion from a primary source rather than by inference: a sealed ingest agent
running on the trader's own machine, holding the trader's own key, **never makes login data
available to a third party.** The key does not leave the machine. Any server-side-pull design is
squarely prohibited by this clause.

⚠ **The performance-transfer clause does not resolve, and I cannot resolve it.** Two readings:

| Reading | Consequence |
|---|---|
| Aimed at **gaming evaluations** — combining or moving performance between Topstep products/accounts to manufacture a pass | Venture unaffected |
| Read literally — account performance data may not be moved into another product at all | ⛔ Venture prohibited on its primary platform |

Evidence that the narrow reading is the operative one in practice: **TradesViz auto-imports from
TopstepX/ProjectX and Tradesyncer ships a ProjectX connection**, both openly, and Topstep's own API
page sanctions third-party connections and read-only analytics. Tolerated practice is not a legal
opinion.

⛔ **ACTION: this clause needs a solicitor, not an agent.** It is the single item most likely to kill
the venture, it cannot be resolved by more reading, and it should be resolved **before** any ingest
code is written. A second route worth pursuing in parallel: ask Topstep directly, in writing, whether
a trader-hosted read-only export to a third-party analytics product is permitted. A written yes is
worth more than any amount of inference.

Not yet checked: Apex, Tradeify, Take Profit Trader, MyFundedFutures equivalents.

---

## Q5 — REGULATORY · ⚠ narrower than feared, with one favourable argument

`REPORTED`. **This is research, not legal advice.**

- Most retail prop firms are **not directly FCA-authorised** — they hold no client money and issue
  simulated accounts rather than taking deposits, so they largely sit outside the regulated-activity
  perimeter.
- **But FSMA s21 applies regardless of authorisation.** An unauthorised person must not, in the
  course of business, communicate an invitation or inducement to engage in investment activity
  unless approved by an authorised person or exempt. The FCA applies financial-promotion rules to
  anyone marketing to UK residents, wherever they are based.
- **PERG 8** is directly on point: performance tables and comparisons *become* inducements when
  there is an actual or implied recommendation that something is a good buy. Any reference to past
  performance must carry a past-performance warning.

### What this means for the three versions of the product

| Version | s21 exposure |
|---|---|
| A trader's **own** record, published as a factual, non-recommendatory statement | ⚠ Low — but tone and framing decide it, and a past-performance warning is required |
| **Rankings / leaderboards** that imply some traders are better buys | ⛔ High — this is where PERG 8 says a table becomes an inducement |
| **Routing capital** to traders on the strength of the record | ⛔ Highest — likely arranging deals in investments; needs authorisation |

⭐ **The favourable argument, and it is a real one.** The same fact that weakens the product's claim
may also keep it out of scope: **prop-firm sim accounts are not real investments.** A record of
performance in a simulator arguably is not a record of "investment activity" at all, so s21 may
simply not bite the core product. The symmetry is neat — *what stops it being proof of trading is
also what stops it being a financial promotion* — but it is `DERIVED`, it is exactly the sort of
argument that fails in the specific, and it must be put to a solicitor rather than relied on.

**Practical line for v1:** publish the trader's own record, factual and non-recommendatory, with the
past-performance warning and the Q3 attestation sentence. **No leaderboards. No capital routing.**
Both are the interesting version; both are the regulated version.

---

## What is already built, and what is not

⚠ Verified against code, not against the handoff — the wiki's claims were checked because the
premise "none of this is built" and the wiki's "E1–E6 BUILT" cannot both be true.

**The wiki did not overstate.** `MEASURED` 2026-09-01 via the GitHub API:

| Fact | How |
|---|---|
| Alembic `0001` → `0012`, including `0011_predictions.py` and `0012_rest_days.py` | `gh api .../contents/api/alembic/versions` |
| 114 `.py` files, 22 test files | `gh api .../git/trees/HEAD?recursive=1` |
| `0011` contains `trg_predictions_freeze_the_call`, `ck_predictions_reveal_follows_commit`, server-stamped `committed_at`, and **no `is_deleted` column** — documented in the migration as *"the denominator can only ever GROW"* | raw fetch of `0011_predictions.py` |

**So the hard part exists.** What does not exist: any ingest of broker data, any deployment, any
user, any pricing that isn't a static page. `neurospect-prototype` is the only live surface
(`https://russell94paul.github.io/neurospect-prototype/`, built from `gh-pages`) and it is a
marketing site — correctly labelled *Illustrative* / *Demo* / *Not Financial Advice* on the
performance page, which was checked.

`SIHRE-Framework` (249 files) is documentation and research only — **zero code**. `INDEX.md`
lists `Walkthrough/` and `Implementation Guide/` sections that do not exist in the tree.

---

## Still open — nothing is signed until these are answered

**Ranked by what most likely kills the venture.**

1. ⛔ **Q2's performance-transfer clause — SOLICITOR, and before any ingest code.** *"You may not
   transfer or combine your Account's performance… between products."* Two readings, one fatal.
   Cannot be resolved by more reading. Run a written question to Topstep in parallel.
2. ⚠ **Q4 · DEMAND.** Traders wanting portability, or allocators wanting a better signal than
   "passed a sim eval". Darwinex proves the model in **forex**; nothing allocates on track record in
   futures. **This needs five conversations with real traders. No agent can substitute for it.**
3. ⚠ **Q5 · the "simulated accounts aren't investments" argument** is favourable and load-bearing
   and `DERIVED`. Put it to a solicitor with Q2 in the same conversation — one bill, two answers.
4. **Q2 for the other firms.** Apex, Tradeify, Take Profit Trader, MyFundedFutures.
5. **Q1b follow-up.** Are ProjectX API keys revocable and rotatable per-key? Is a read-only scope on
   any roadmap? A read-only scope would dissolve most of Q1b and half of Q2.
6. Confirm the Tradovate prop-account restriction against a **primary** source, not a user post.

---

## If it goes GO, the first thing built is a contract that can fail

ECHELON I, not ECHELON 0:

> Every published record reconciles to a broker-attested fill, and a **deliberately altered record
> is refused.**

Then break a record on purpose and watch the contract catch it. Per the Field Manual gate: *the
contract must be seen refusing at least once before you trust a single green run.*

---

## Provenance of every claim above

`MEASURED` — I ran the command this session, in this repo or against the GitHub API.
`REPORTED` — a source says so; I did not verify independently.
`DERIVED` — reasoned from something measured or reported.

⚠ Much of the landscape sweep drew on affiliate-funded comparison sites, whose incentive runs
toward "yes, they pay". Every figure taken from them is `REPORTED` and should be treated as a
prior, not a finding. The industry-size and firm-count numbers (≈50–60 active futures prop firms;
80+ prop-firm shutdowns 2020–2026, **mostly forex, not futures**) are in that category.

⭐ The forex/futures distinction was checked deliberately: the widely-cited "80–100 prop firms
collapsed" figure is dominated by **forex/CFD** firms (Smart Prop Trader, My Forex Funds, True
Forex Funds, SurgeTrader…). Futures prop firms run on Rithmic/Tradovate/ProjectX and were largely
insulated. **Conflating the two would have poisoned the whole analysis.**
