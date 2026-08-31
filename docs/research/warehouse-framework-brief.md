# Research brief — a standardised, agent-buildable client warehouse framework

**Written 2026-08-30.** Runnable as-is: paste into `deep-research` in this repo, or into an external
deep-research tool. Filed here rather than as `R<n>` on purpose — `factory/dispatch.py` globs
`docs/research/R[0-9]*.md` at module scope, and this is a brief for a *different* programme, not a
row in the R1–R19 dispatch table.

**Pass type:** STRUCTURE_CRITIQUE + EXTERNAL SURVEY (both — see §6).
**Commissioned because:** a lot of new clients are arriving, and there is no framework for building
their warehouses. Today each client is hand-built and two of them have already diverged into
different house styles.

---

## 0. Why this is being asked now, with the measurements

Re-run every number before citing it. A hand-typed count re-rots invisibly, and this estate has had
**four blind instruments in nine days** (F79, F80, F81, F84), three of which returned a *plausible
number* rather than an error.

```bash
cd ~/repos/clients
ls -d */ | wc -l                                          # client folders
ls -d */snowflake 2>/dev/null | wc -l                     # with a warehouse
ls docs/decisions/*.md | wc -l                            # ADRs

cd ~/repos/wiki
ls processes/deployment/*.md | wc -l                      # deployment runbooks
grep -ilE 'manual|by hand' processes/deployment/*.md | wc -l   # naming a manual step
```

**Measured 2026-08-30:** 19 client folders in `clients`; 13 deployment runbooks, **8 of which name a
manual step**; 3 ADRs.

⭐ **The divergence that motivates the whole brief.** Two clients, both "ALDC standard", have
different physics:

| | GEP | Fusion92 |
|---|---|---|
| Object type | `CREATE OR REPLACE SECURE VIEW` | `CREATE OR REPLACE DYNAMIC TABLE` |
| Refresh | scheduled tasks, **triggered manually** | `TARGET_LAG='1 hour'` / `DOWNSTREAM`, automatic |
| Domain | e-commerce (sales, inventory, purchasing, margin) | media (spend, flights, campaigns) |
| Deploy | **paste each file into the Snowsight UI** | same |

Neither is wrong. But nothing decides which a *new* client gets, and nobody has written down what the
choice depends on. That is the question.

**Two more measured facts that constrain any answer:**
- `deploy.py` is local-only — **bus factor 1**, and there is no CI/CD for Snowflake at all.
- `wiki/concepts/architecture/workflow-analysis-current-vs-future.md` enumerates **16 named gaps**,
  including: no cross-DB comparison, no schema-drift detection, no automated freshness monitoring, no
  rollback mechanism, no environment promotion gate, no DDL version tracking, no TEST-vs-PROD
  comparison.

---

## 1. The question

> **What is the right framework for building a client's Snowflake warehouse such that (a) a new
> client can be stood up from a template rather than hand-built, (b) the parts that genuinely differ
> per client are isolated from the parts that do not, and (c) an agent can generate, deploy and
> verify it safely — with the deploy gated on evidence rather than on a human remembering the
> runbook?**

Three sub-questions, in dependency order. **Do not answer 3 before 1.**

1. **What is the layered model?** What is standard, what is per-client, what is per-source — and
   where exactly is the seam between them?
2. **What builds it?** dbt vs Snowflake Dynamic Tables vs the current hand-rolled SQL + `deploy.py`.
   Decided on *our* constraints, not on vendor claims.
3. **What makes it agent-safe?** What must be true before an agent may generate and deploy a client
   warehouse unattended, and which of those things are true today?

---

## 2. What must be read first — do not design before reading these

⛔ **The most dangerous lead is the tidiest one.** The best-written existing document is the one most
likely to propagate an error into the design. Flag it explicitly before you start.

| Artefact | Why |
|---|---|
| `wiki/concepts/architecture/star-schema-convention.md` | The canonical naming, SHA2 surrogate key, currency-triple and date-dim rules. **This is the standard. The framework formalises it; it does not replace it.** |
| `clients/__TEMPLATE_ACCOUNT/` | The template that already exists. ⚠ ADR-003 says it **contains real credentials** — read that ADR before touching it. |
| `clients/docs/decisions/ADR-00{1,2,3}.md` | Connection-template UUID linkage; **Snowflake schema divergence** (ADR-002 is directly on this question); template credentials. |
| `wiki/concepts/architecture/workflow-analysis-current-vs-future.md` | The 16-gap table. Any framework that does not close several of these is not worth building. |
| `wiki/processes/deployment/gep-snowflake-pbi-deployment.md` | The flagship runbook — 11 phases, 8 numbered pitfalls. The thing a framework has to automate. |
| `wiki/concepts/architecture/cross-channel-marketing-dimensional-model.md` | The external dimensional evidence, already gathered and graded. **Do not re-research it.** |
| `clients/FUSION_92/snowflake/warehouse/` and `clients/GEP/snowflake/warehouse/` | The two divergent implementations, side by side. |
| `factory/redesign_contract.py`, `factory/connector_contract.py` | The only calibrated contracts in the estate. A framework's verification layer should extend these, not invent a third vocabulary. |

---

## 3. What the answer must contain

### 3.1 The layered model

A framework is only useful if the seam is in the right place. Propose the layers and, for each, state
**what varies and what must not**:

```
standard         identical for every client — dim_date, dim_currency, naming, key strategy
domain pack      e-commerce | media/agency | (a third?) — the fact families a domain implies
client           the genuinely per-client part — which is WHAT, exactly?
source           per connector — landing shape, grain, incremental strategy
```

⭐ **The load-bearing question is the third row.** Enumerate what is *actually* client-specific across
the 19 client folders, with evidence. Our own suspicion is that most apparent per-client variation is
really per-*domain* or per-*source* variation that was hand-written each time — but that is `ASSUMED`
and the pass must test it, not inherit it.

For each layer: how is it versioned, how does a client inherit an upgrade, and **what happens when the
standard changes after 30 clients are on it?** A framework with no upgrade story is a template.

### 3.2 The build-tool decision

`dbt` vs **Dynamic Tables** vs **status quo**. Judge against our constraints, not the feature matrix:

- **Deploy is manual paste into Snowsight**, and there is no CI. What does each option require before
  it can be deployed at all?
- **Bus factor 1** on the deploy path.
- Fusion92 already runs Dynamic Tables with `TARGET_LAG`; GEP runs manually-triggered tasks. **A
  recommendation that ignores one of these is not a recommendation for this estate.**
- `CREATE OR REPLACE` **strips ownership and silently drops objects from a data share** — this has
  caused at least one multi-day staleness event and has its own pending ticket. Any tool must
  preserve `COPY GRANTS`, and the answer must say how.
- Snowflake cost: Dynamic Tables refresh on a lag, which is a standing spend. Quantify it.

Verdicts: `ADOPT | ADAPT | BUILD | DEFER`, one per option, each with the evidence and the condition
that would change it.

### 3.3 The agent-safety layer

This is the part with no published answer, and the reason the pass is worth running.

- What must be **true** before an agent may generate a client warehouse? Before it may *deploy* one?
- Which of those are true today? Measure — do not assume. Start from
  `python -m factory.launch`, which answers three separate questions (*may I run / may I leave it
  running / may I trust the output*) and currently returns **SUPERVISED-OK / UNATTENDED-BLOCKED /
  OUTPUT-UNCERTIFIED**.
- What is the **verification contract** for a generated warehouse — the `A1–A12` equivalent? What
  assertion can be *watched refusing*? ⛔ A contract nobody has watched refuse is decoration; that is
  this repo's standing rule and the reason `connector_contract` is trusted and `pbi_contract` was not.
- **Rollback.** `CREATE OR REPLACE` on a shared object is destructive and silent. What does capture
  -before-mutation look like when the mutation is generated?
- What must stay human? Name it, and say why. Secrets and PROD promotion are already
  non-negotiable — what else?

### 3.4 The visual deliverable

The output is a **technical design document with real figures**, not prose with a diagram bolted on.

Per `~/.claude/CLAUDE.md`: load **`artifact-design`** first, then **`artifact-motion`** (a mechanism,
a pipeline and a before/after are all in play), then **`artifact-diagramming`** for the inline-SVG
mechanics. **A readout that reads as flat prose is a design failure — and so is motion that encodes
nothing.**

Figures that must exist:
1. **The layer stack**, with the seam between standard and per-client drawn explicitly.
2. **The bus matrix** — business processes × conformed dimensions, for both domain packs.
3. **Today vs proposed**, as a real before/after — showing where the 8 manual steps go.
4. **The deploy path**, with the human gates marked and the blast radius of each hop.
5. **A worked example**: one real new client, end to end, from template to verified rows.

Every figure's geometry computed from the estate's own measured numbers. No decorative charts.

---

## 4. Method and rules

- **Basis on every load-bearing claim.** Two vocabularies, both required, in this pairing:
  - about the world — `MEASURED` · `DERIVED` · `STATED` · `ASSUMED` · `PROXY`
  - about the design — `REPO-BACKED` (cite `path:line`) · `INFERRED` · `RECOMMENDED` · `EXTERNAL` ·
    `SPECULATIVE`
- ⛔ **Never present a `RECOMMENDED` or `SPECULATIVE` item in the present tense.** This estate has
  twice shipped a mechanism that read as built and was not.
- **A fetch summary is a lead, not evidence.** Open the artefact. In one recent wave two WebFetch
  summaries were wrong *in opposite directions*, and both decisive findings came from opening the
  actual file.
- **A vendor claim may not underwrite a design.** `MARKETED` is never a design premise.
- **A code-search zero without a positive control is NOT-VISIBLE, not ABSENT** (F84 — a grep returned
  0 for five modules with 54 call sites between them, because it was blind to one import form).
- **Enumerate the population; never sample and generalise.** 19 client folders is a small enough set
  to check exhaustively. "I looked at GEP and Fusion92" is a hint, not a finding.
- Where something cannot be established, say **`NOT-DETERMINABLE`** and name the single command or
  artefact that would settle it.

---

## 5. Deliverable

`docs/research/answers/warehouse-framework-answer.md` plus the published design artifact.

Sections, in order:

1. **The layered model**, with the seam justified against enumerated evidence from all 19 clients.
2. **What is actually per-client** — the measured list, and what turned out not to be.
3. **The build-tool verdict** — `ADOPT|ADAPT|BUILD|DEFER` per option, with the unlock condition.
4. **The verification contract** — assertions, and which have been watched refusing.
5. **The agent-safety ladder** — what is true now, what each next rung requires.
6. **Migration** — how GEP and Fusion92 reach the framework, or why they should not.
7. **NOW vs LATER**, using this estate's test: *can this be reconstructed afterwards?* If the
   information is lost at write time it is NOW; if it can be rebuilt later, it waits.
8. **What this pass could not determine**, with the command that would settle each.

---

## 6. What would make this pass fail

Stated up front so the failure is recognisable from inside it.

- **Designing a framework nobody can deploy.** If the answer requires CI that does not exist and does
  not say so, it is a wish.
- **Recommending dbt because it is the industry answer.** It may well be right — but the reasoning has
  to run through *manual Snowsight deploys*, *bus factor 1*, *`COPY GRANTS`*, and *an existing Dynamic
  Tables client*, or it is a recommendation for somebody else's estate.
- **Treating the two house styles as a mistake to be corrected.** They may encode a real difference
  between an e-commerce and a media client. Establish which before flattening them.
- **A 40-page document with one diagram.** See §3.4.
- ⛔ **Producing an agent-safety section that reads as built.** Today's honest answer is
  *supervised-only*, and any ladder must start from there.
