# ECHELON 0 · RECON — `leads` (planning filings → installers) · **NO-GO**

**Signed off 2026-09-01. Verdict: NO. Nothing was built. This is a success.**

The Field Manual's `leads` topic: *public planning / permit filings become qualified, timed leads*,
sold to solar / EV-charger / heat-pump installers. Its ECHELON 0 first move was *"read one council's
planning portal for 30 days and produce a clean table of applications matching one filter."*

It never got that far. The national open dataset was measured first, because it was the cheapest
thing to falsify, and it failed on four independent counts.

---

## What was measured

`MEASURED` — one streaming pass over the full bulk CSV, 100,627 rows.

```
python scripts/recon_planning_data_probe.py
```

Dataset: `planning-application` on `planning.data.gov.uk`
(bulk: `https://files.planning.data.gov.uk/dataset/planning-application.csv`, 44,513,805 bytes).

| Test | Result | Verdict |
|---|---|---|
| **Coverage** | **4 LPAs** of ~317 in England — Camden 77,499 · Worthing 13,629 · Adur 7,585 · Doncaster 1,914 | ⛔ 1.3%, and 77% of the file is one council |
| **Freshness** | newest `entry-date` **2025-09-09**; bulk file `Last-Modified` 2025-09-09 | ⛔ **357 days stale.** The entire wedge was "filings are days earlier" |
| **Contactability** | `address-text` 98.1% · `point` 98.1% · `uprn` **0.0%** · `geometry` **0.0%** · **no applicant-name or agent-name column exists at all** | ⛔ An address is not a person |
| **Signal** | of 100,627 filings: solar 1,286 (1.3%) · heat pump 548 (0.5%) · EV charging 145 (0.1%) · battery 32 (0.03%) | ⚠ Thin |
| **Filterability** | `planning-application-type` **0.0%** populated · `development-classification` 18.8% | ⛔ Cannot filter the population |
| **Licence** | `ogl3`, Crown copyright — commercial re-use permitted | ✅ The only green light |

Dataset `phase` is `alpha`. One data-quality tell: max `decision-date` is **2046-08-15**, a
typo'd future date that survived into the published file.

---

## The two structural findings, which matter more than the numbers

**1 · The clean route has no people in it; the route with people has no clean licence.**
The OGL-licensed national dataset carries no applicant or agent identity — so it cannot produce a
lead. The data that *does* carry identity lives on ~317 individual council portals, each with its own
terms of use, reachable only by crawling. That is not one legal question, it is 317.

**2 · ⭐ The legislation is actively destroying the signal.**
SI 2025/560 (in force 29 May 2025) rewrote Class G of GPDO Schedule 2 Part 14 and **widened**
permitted development for air source heat pumps — scrapped the 1 m boundary rule, raised the volume
cap 0.6 m³ → 1.5 m³, allowed two units on detached houses, and permitted cooling. Part 14 was
amended again on 27 August 2026 (SI 2026/896), adding plug-in solar provisions.

Every widening moves work *out* of the planning system. A lead product built on planning filings for
domestic solar and heat pumps is betting against the direction of the law.

Domestic EV charge points are already permitted development under Schedule 2 Part 2 Classes D and E,
outside listed buildings and scheduled monuments.

---

## Instrument limits — recorded so a later session does not mistake them for findings

⚠ Six council portal `robots.txt` files were probed. **Four hostnames did not resolve from this
sandbox** (`curl` exit 6 — DNS) and Camden resolved but timed out (exit 28). Only
`planning.birmingham.gov.uk` genuinely answered (a real IIS 404, i.e. no `robots.txt`).

`http 000` is a connection failure, **not** an absent file. The portal terms-of-service lane was
therefore only partially reachable and is recorded as **NOT-VISIBLE**, not as ZERO.

This did not change the verdict — the venture was already dead on coverage and freshness before the
ToS question mattered.

---

## Why this is the right outcome

RECON's job is to be allowed to say no, cheaply, before anything is built. It cost one afternoon and
one 44 MB download. Had the phase been skipped, the first three months would have gone into a
scraper for a signal that is 1.3% of a dataset covering 1.3% of the country, refreshed annually,
with no contact route, in a category the government keeps deregulating.

Superseded by [`verified-record-echelon0-2026-09-01.md`](./verified-record-echelon0-2026-09-01.md).
