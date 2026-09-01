### F97 — the document that locks MER defines it as the reciprocal of what three code layers compute, and the doc's formula is already shipped under a different name

Filed 2026-09-01. First surfaced by R2 (`docs/evidence/marketing-model-v1/R2-repo-wiki-diff.md`
:171-173); **every source below was re-opened and read directly for this file**, not inherited from
R2's summary.

## The two definitions, measured

| Side | Source | Formula |
|---|---|---|
| **Doc** | `wiki/concepts/architecture/cross-channel-marketing-attribution.md:29` | *"total spend ÷ **actual revenue**"* |
| **Doc** | same file `:94` | `MER = SPEND / ACTUAL_SALES` |
| **Warehouse** | `clients/GEP/snowflake/report_common/MARKETING_EFFICIENCY_MONTHLY.sql:50` | `BLENDED_MER = ROUND(ACTUAL_SALES_GROSS_USD / NULLIF(SPEND_USD,0), 4)` |
| **Frontend** | `navira-marketing-dashboard/src/lib/metrics.ts:99` | `mer: safeDiv(sum.totalSales, sum.spend)` |
| **Frontend** | same file `:16` (docstring) | `mer: number; // totalSales / spend` |
| **Field spec** | `navira-marketing-dashboard/docs/FIELDS.md:38` | `SUM(total_sales) / SUM(spend)` |

Doc says **SPEND / SALES**. Warehouse, frontend and field spec all say **SALES / SPEND**. These are
reciprocals, not roundings — for the same period they cannot both be the number on the slide.

## ⭐ The discriminator that makes this concrete rather than pedantic

`metrics.ts:95`, four lines above the MER definition:

```ts
tacos: safeDiv(sum.spend, sum.totalSales),
```

**The doc's MER formula is already implemented in production — as TACoS.** So a reader who takes
the wiki at its word and computes "MER" gets the dashboard's TACoS, exactly, and will reconcile it
against `BLENDED_MER` and find the two disagree by a factor of MER². This is not a naming quibble;
it is one number with two live definitions, one of which collides with a *different* named metric
on the same screen.

## The document also disagrees with itself

`:37` of the same wiki page: *"a **falling** MER at constant spend is a real warning sign."* Under
`SALES / SPEND` a falling MER means less revenue per dollar — a warning. Under the same page's own
`SPEND / SALES` at `:94`, a falling value means spend shrank relative to revenue, which is the
opposite of a warning. The narrative sides with the code; the two formula statements do not.

⛔ **This is deliberately NOT resolved here.** The evidence points one way, but three sources
agreeing is a majority, not a proof, and `ATTR:100 Decision 1 (2026-05-29)` locked *"blended MER"*
as the headline without writing the fraction. The status is **CONTRADICTORY** until a human
resolves which is authoritative. D1 must carry the contradiction, not a winner.

- **BELIEVED** — MER is defined; the attribution architecture page locks it, and downstream work
  can quote `MER = SPEND / ACTUAL_SALES` from `:94` as settled.

- **ACTUALLY** — MER has two live definitions that are reciprocals of each other. The locking
  document states one at `:29` and `:94`, argues for the other in prose at `:37`, and all three
  implementing layers ship the other. The doc's stated formula is separately implemented as TACoS
  at `metrics.ts:95`.

- **MEASURED BY** — opening each of the six cited locations directly and reading the fraction:
  ```bash
  sed -n '29p;37p;94p' ~/repos/wiki/concepts/architecture/cross-channel-marketing-attribution.md
  sed -n '50p'         ~/repos/clients/GEP/snowflake/report_common/MARKETING_EFFICIENCY_MONTHLY.sql
  sed -n '16p;95p;99p' ~/repos/navira-marketing-dashboard/src/lib/metrics.ts
  sed -n '38p'         ~/repos/navira-marketing-dashboard/docs/FIELDS.md
  ```

- **AFFECTS** — the mission DAG first: **D1** (requirements synthesis — must inherit
  `CONTRADICTORY`, never a resolved form), then D2, D3 and D5 downstream. The corrected metric
  hierarchy, whose **headline is Blended MER** — the contradiction sits on the top-line number, not
  a peripheral one. `wiki/concepts/architecture/cross-channel-marketing-attribution.md`, and any
  client-facing readout that prints a MER figure. Beyond the mission it reaches **every lane** that
  publishes a named ratio: the transferable rule is that a metric's *locking document* is not
  automatically its definition of record, and agreement between three implementing layers is a
  majority rather than a proof.

- **KIND** — DESIGN

- **CHANGES** — one canonical MER fraction must be written into
  `wiki/concepts/architecture/cross-channel-marketing-attribution.md` at both `:29` and `:94`,
  agreeing with whichever layer the client's sign-off names as authoritative, with the superseded
  form kept and marked rather than deleted; and the page must state explicitly that
  `SPEND / SALES` is TACoS, so the two can never be re-conflated. **The choice is a human
  decision and this finding does not make it.** Until it is made, no design or client artifact may
  print a MER value without naming its fraction beside it.

- **STATUS** — OPEN
