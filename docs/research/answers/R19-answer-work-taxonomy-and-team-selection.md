# R19 — Answer: the ALDC work taxonomy, and how a team gets chosen for a ticket

**Filed 2026-08-29.** Pass type `STRUCTURE_CRITIQUE`. Run 1.
Prompt: [`docs/research/R19-work-taxonomy-and-team-selection.md`](../R19-work-taxonomy-and-team-selection.md).

**Basis labels.** World: `MEASURED` / `DERIVED` / `STATED` / `ASSUMED` / `PROXY`.
Design: `REPO-BACKED` (cited `path:line`) / `INFERRED` / `RECOMMENDED` / `EXTERNAL` / `SPECULATIVE`.

---

## ⛔ 0. Independence disclosure — read before weighting anything here

**The blind-first instruction was partially violated, and not by this run.** The prompt requires the
researcher to read `~/repos/wiki/tickets/` before opening `factory/presets.py`. This pass ran in a
**continuing session that had already read `factory/presets.py`** — including all five `type_id`
values, their `seen_in` citations and their `verifier_state` fields — while writing the brief itself
the previous turn.

What was still done blind: the **full ticket sweep** (§2) was executed and read before re-opening any
factory module in this run, and the taxonomy below contains eleven types that `presets.py` does not.
What was **not** blind: the five types `presets.py` already holds were known going in, so the finding
"these five are correct" carries **no independent weight** and is labelled `ASSUMED` throughout.

⭐ **This is itself a finding about the method, not just an apology.** A `STRUCTURE_CRITIQUE` pass
whose brief is written by the same session that then answers it cannot be blind, because writing the
brief requires reading the code. **The brief-writer and the answerer must be different sessions**, or
blind-first is a label rather than a control. `RECOMMENDED` — add this to the dispatch protocol in
`docs/research/README.md`.

---

## 1. Executive thesis

**The highest-leverage thing to build next is not a selector. It is the dispatch record — and before
even that, a two-line fix to `factory/blueprint.py` that closes a certification-laundering hole.**

Three findings, in the order they should be acted on:

1. ⛔ **`TeamSpec.version` is blind to the team's repo and to the team's prohibition.** Proven by
   discriminating test (§6.1). A team certified against `prefect-connectors` with *"must not deploy
   to production"* keeps **the identical version hash** when repointed at another repo with the
   prohibition deleted. The module whose docstring is *"The config that IS the version"*
   (`factory/blueprint.py:1`) lets a certification transfer across exactly the two changes that
   change the blast radius. This is the repo's founding failure mode reproduced inside its own
   versioning primitive.

2. ⛔ **The estate has two run ledgers, they count different populations, and neither records which
   configuration ran.** `.data/runs.jsonl` holds **3 rows, all `FINISHED`** `MEASURED`;
   `g_work_is_attributable` reads a *different* store (`prefect-connectors/.sessions`) and reports
   **14 runs** `MEASURED`. Neither carries a model, an effort level, a blueprint version, or the set
   of configurations that were eligible and not chosen. **No selector can ever be trained on this,
   and no amount of waiting fixes it** — the missing fields are missing at write time.

3. **`presets.py` covers 5 of 16 measured ticket types, and the 11 uncovered ones carry the larger
   blast radius** — incident, auth/token lifecycle, infrastructure, analysis-deliverable,
   schema-extension. The gap is not an oversight to be filled by writing eleven more rows; §3.2
   argues most of them should get a **refusal** rather than a preset, because their verifiers are
   `UNBUILT` and their consumer layer is production.

**What follows from this:** the honest selector for the next two quarters is **stage 1 — a
rule-based eligibility filter that mostly returns "human"** — plus a dispatch record rich enough
that stage 3 becomes reachable in 2027. Anything presented as an optimiser before then is
`SPECULATIVE`.

---

## 2. Blind read of the ticket corpus

**Method.** All 59 ticket pages under `~/repos/wiki/tickets/` were swept for frontmatter tags, H1,
`**Type/Status**` line, and the first `Problem` / `Root cause` / `Summary` / `Symptom` section.
`MEASURED`:

```bash
cd ~/repos/wiki && find tickets -name '*.md' ! -name '_*' | wc -l          # 59
find tickets -name '*.md' ! -name '_*' | awk -F/ '{print $2}' | sort | uniq -c
#   1 aldc   2 dv   11 fusion92   45 gep
```

### 2.1 The taxonomy

Sixteen types. Each row's `seen_in` is the evidence it is a real shape of work; a type with one
ticket is marked `PROVISIONAL`. Consumer layer names where the fix must be validated, per the three
standing gates.

| # | Type | Seen in | Layers | Consumer layer | Verifier state | Blast radius |
|---|---|---|---|---|---|---|
| 1 | UI control change | GP-327, DV-444 | eclipse, cosmos | rendered dashboard | `WIRED` | one dashboard; **higher if the filter carries a value** |
| 2 | Additive semantic-model change | GP-329, GP-256 | pbi_model | DAX + rendered | `AVAILABLE` | live model worked concurrently |
| 3 | Dimension gap / blank member | GP-328, GP-312 | snowflake, pbi_model, eclipse | DAX **at the dashboard's timeframe** | `AVAILABLE` | every client vendor dashboard (8 measured) |
| 4 | Wrong number the client can see | GP-322, GP-311, GP-282, GP-281 | snowflake | PBI/DAX + rendered | `AVAILABLE` | whole fact; client-visible |
| 5 | Model redesign / legibility | GP-318, GP-319 | pbi_model, snowflake | rendered + client sign-off | `AVAILABLE` | the client's live surface |
| 6 | **New source ingestion / schema extension** | GP-200, GP-203, GP-204, GP-208, GP-257, GP-287 | connector, snowflake, eclipse, pbi_model | warehouse row counts + PBI | `UNBUILT` | new marketplace/feed; deploy-gated |
| 7 | **Connector failure / data freshness** | FU92-394, FU92-421, GP-286, GP-PENDING-infra | connector, vendor_api | landed rows vs source | `AVAILABLE` (the GreenContract) | silent data loss across clients |
| 8 | **Auth / token lifecycle** | FU92-393, FU92-395, FU92-396, FU92-415, FU92-416 | vendor_api, core_api, azure | live API call | `UNBUILT` | silent expiry → looks like a data gap |
| 9 | **RBAC / "Error loading data"** | GP-304, GP-310 | core_api, eclipse, cosmos | rendered surface, **per role** | `UNBUILT` | fails closed for *every* user incl. admins |
| 10 | **Infrastructure / env isolation / CI-CD** | GP-217, GP-218, GP-248, GP-207 | azure, prefect, snowflake | pipeline run + grants | `UNBUILT` | cross-environment; can strand prod |
| 11 | **Usage audit / analysis deliverable** | FU92-420 `PROVISIONAL` | vendor_api, snowflake, client_comms | **the rendered PDF/CSV the client opens** | `UNBUILT` | commercial; **no deploy, no gate** |
| 12 | **Incident / outage** | GP-PENDING-sales-outage, GP-PENDING-infra | snowflake, azure, connector | data flowing again | `UNBUILT` | total; multi-client, multi-day |
| 13 | **Client onboarding / multi-tenant** | GP-254, GP-261 | connector, snowflake, azure | tenant-scoped row counts | `UNBUILT` | **cross-tenant leakage** |
| 14 | **Support / one-off data exclusion** | GP-283, GP-284 | snowflake | drift-immune before/after | `AVAILABLE` | propagates to every downstream view |
| 15 | **Platform app bug** | ALDC-622, DV-506, GP-277, GP-286 | eclipse, core_api | reproduce in the app | `UNBUILT` | one workflow, all tenants |
| 16 | **Scoping / design ticket** | GP-199, GP-225, GP-258, GP-288 | varies | a decision, not a deploy | n/a — **not certifiable** | wrong design costs a quarter |

### 2.2 Five things the tickets say that no preset table currently encodes

`MEASURED`, each from a ticket's own text:

* **A council formation has already been run, and it worked.** GP-311: *"Ran as an
  [[inquest-bug-resolution]] council of five. The council caught **six factual errors in the
  inherited case file** before any of it reached a partner."* This is the estate's only
  `MEASURED` evidence for a multi-agent formation on real work, and §6 argues it does **not**
  contradict R2.
* **Review does not catch this class of defect.** GP-318: *"⭐ The lesson of the day: four defects,
  none found by review"*, and separately *"GP-318 caught 10 self-inflicted defects this way and
  review caught none"* (`factory/presets.py:224-225`). **Pre/post assertion batteries caught what
  human review missed.** That is an argument for verifiers over reviewer agents.
* **The analysis class fails without any deploy.** FU92-420: *"The audit went through **five
  revisions**; v1–v4 were each wrong in a different way and **every correction came from an internal
  reviewer, never from measurement we initiated**."* No change gate would have caught any of them.
* **Accidental controls exist and are worth hunting.** GP-327: Rain Bird had already lost the
  filters, *"which made it a **live control for the post-change shape** — worth looking for that kind
  of accidental control before deploying."* This is control-arm thinking already present in the
  practice and absent from the code.
* **The stated scope of a ticket is routinely wrong.** DV-444: *"Initial ticket framing: 'code change
  to eclipse-2.1.' After investigation, that framing is wrong… the feature branch will close with
  **zero commits**."* GP-318 had **two scoping premises refuted by measurement**. GP-310 documents
  *"The false premise that created the bug"* and *"The wrong fix, and why it was reverted."*

⭐ **The last one is the single most important input to any selector.** A selector that reads the
ticket's stated layer and dispatches a team scoped to it will, on this corpus's evidence, be wrong
often enough to matter. **Scope discovery must be a separate, cheap, human-gated stage before team
formation** — not a step inside the implementation agent's context.

---

## 3. Where the taxonomy and `presets.py` disagree

### 3.1 The disagreements

| Claim | Verdict |
|---|---|
| The 5 existing types are real shapes | **Agree** `ASSUMED` — see §0; this run was not blind to them |
| `wrong-number` `seen_in` cites GP-322 only (`presets.py:180`) | **Understated.** GP-311, GP-282 and GP-281 are the same shape. GP-311 in particular is the *second occurrence of the same defect* (ALDC-490 fixed it five weeks earlier at the wrong layer) — a repeat is the strongest possible evidence for a type and it is not cited |
| `dimension-gap` layers = `("snowflake","pbi_model","eclipse")` (`presets.py:152`) | **Agree, and the `escalate_when` is the best row in the file** — *"the warehouse says the data is clean… the answer appeared only in DAX at the DASHBOARD's timeframe"* is exactly GP-328's mechanism |
| 5 types is the coverage | **Disagree — 5 of 16.** And the 11 missing are not the tail |
| `verifier_state` is honest | **Agree, and it is the most valuable field in the module.** 4 of 5 rows are `AVAILABLE`, i.e. *"the mechanism exists; this ticket type has not been put through it"* (`presets.py:41`). `unwired()` (`presets.py:265`) exists precisely to stop the table reading as coverage |

### 3.2 What the 11 uncovered types should get — and it is mostly not a preset

Writing eleven more `Preset` rows would **manufacture the appearance of readiness**, which
`presets.py:29-31` already warns against: *"a preset naming a verifier is a claim that one applies,
not that one has been wired."*

`RECOMMENDED` — three dispositions:

| Disposition | Types | Rationale |
|---|---|---|
| **Preset now** | 7 (connector failure), 14 (support exclusion) | 7 is the one type with a real contract — `factory/connector_contract.py` A1–A12, calibrated. 14 has a proven drift-immune verifier in GP-283 |
| **Refusal row with a named unblocking condition** | 6, 8, 9, 10, 12, 13, 15 | Verifier `UNBUILT` **and** consumer layer is production. The honest row is *"no eligible configuration; unblocks when `<named check>` is wired"* |
| **Out of scope for team formation entirely** | 11 (analysis), 16 (scoping) | Neither produces a diff. 16 produces a decision; 11 produces a document. **Type 11 needs the counting-basis gate, not a team** — see §9 |

⭐ **Type 11 deserves its own paragraph.** FU92-420 is the only ticket in the corpus that damaged a
client relationship, it involved **zero deploys**, and it would pass every gate in this repo
untouched because nothing was ever certified. `RECOMMENDED`: the analysis class gets a
**pre-registration artefact** — counting basis declared and committed *before* the first query runs,
diffed against the published figure at review. That is a contract, but its subject is a **document**,
not a table.

---

## 4. The manual-step ledger

**8 of 13 runbooks name a manual step** `MEASURED`
(`grep -ilE 'manual|by hand' processes/deployment/*.md | wc -l`).

| # | Step | Source | Why manual | Failure it prevents | Verdict |
|---|---|---|---|---|---|
| 1 | Copy each SQL file into the Snowsight UI and execute | `gep-snowflake-pbi-deployment.md:93` | nobody has written the driver | — | **`AUTOMATABLE-NOW`** for TEST |
| 2 | Capture the shared-object list **before** any `CREATE OR REPLACE` | `client-release-checklist.md:30-33` | judgement about scope | `CREATE OR REPLACE` silently drops objects from the share | **`AUTOMATABLE-NOW`** — this is a query, and leaving it to a human is why GP-PENDING-data-share-stability exists |
| 3 | Re-share the affected objects afterwards | `client-release-checklist.md:39` | as above | days of silent staleness (`:337` — dropped mid-day 2026-04-21, failed 13:26 PDT) | **`AUTOMATABLE-NOW`** |
| 4 | Manually trigger the task chain rather than wait for 06:00 PDT | `gep-snowflake-pbi-deployment.md:111-114` | timing choice | validating against unmaterialised tables | **`AGENT-ASSISTED`** |
| 5 | PBI **Desktop** republish for any visual change: download `.pbix`, edit parameters, refresh, save to temp, publish, confirm overwrite | `gep-snowflake-pbi-deployment.md:229-247` | **no API** — binary artefact, GUI-only | — | **`KEEP-HUMAN`** until `.pbip` migration |
| 6 | PBI metadata-only change via `pbi_model_apply.exe` | `gep-snowflake-pbi-deployment.md:17` | already automated | — | **done** — the estate's best automation precedent |
| 7 | Eclipse: manual `workflow_dispatch` with `force_deploy=true` | `eclipse-azure-deployment.md:17,42,62` | mutable GitVersion tag trips `rollback-check` | — | **`AUTOMATABLE-NOW`** (`gh workflow run`) |
| 8 | **Functionally verify on the stage URL before swapping** | `eclipse-azure-deployment.md:44,70,74` | *"a green workflow run is **not** sufficient"* | the 2026-06-17 incident | **`AGENT-ASSISTED`** — this is a render check, and Playwright can do it |
| 9 | `az webapp deployment slot swap` | `eclipse-azure-deployment.md:24` | production cutover | — | **`KEEP-HUMAN`** |
| 10 | Swap **backend first, then frontend** | `eclipse-azure-deployment.md:45,78` | ordering constraint | new frontend 404s against old backend | **`KEEP-HUMAN`** (ordering), agent-checked |
| 11 | Connector image: `ssh`, `cp config-test.json config.json`, `sudo ./build.sh`, answer prompts, Portainer stop/start | `connector-docker-deployment.md:32-83` | interactive prompts, privileged mode | — | **`AUTOMATABLE-AFTER-CERTIFICATION`** |
| 12 | Copy connection/template documents from GitHub into **Production CosmosDB** by hand | `client-release-checklist.md:23-24` | no sync tool | drift between repo and Cosmos (`:18` asks you to diff them) | **`AUTOMATABLE-NOW`** — a diff already exists in the checklist as a manual step |
| 13 | Every secret: Dashlane / `vault/infra-credentials.md` / Key Vault | `connector-docker-deployment.md:78,166,228`; `core-api-local-setup.md:71` | standing rule | — | **`KEEP-HUMAN`** — non-negotiable |
| 14 | Manual Excel upload fallback when the timer is down | `credential-exchange-function-deploy.md:102` | private endpoint unreachable from a laptop (`:112`) | — | **`KEEP-HUMAN`** |
| 15 | Requeue historical partitions in SSMS | `client-release-checklist.md:41` | GUI | — | `NOT-DETERMINABLE` — no runbook detail |

### 4.1 ⛔ The finding inside the ledger

**`eclipse-azure-deployment.md:16` documents a CI workflow that reports success on every run and
changes nothing the running app serves.**

> *"`deploy_az_webapp.yaml` ("Deploy to Azure App Service") is a **NO-OP**. It builds Next.js and
> pushes to `wwwroot`, which a container App Service **ignores entirely**. Every run 'succeeds' but
> changes nothing."*

Compounding it, `:150` records that **`rollback-check` is itself a no-op whenever the tag doesn't
change**, and `:27` that GitVersion reuses tags — so *"both slots can share a tag and the rollback
net is degraded."*

This is the `false-succeeded` mechanism this repo was founded on
(`docs/evidence/false-succeeded-mechanism.md`), **live in production tooling, already diagnosed, and
still shipped.** `RECOMMENDED`: the discriminating check an agent must run before believing any
Eclipse deploy is *"does the container digest served by the stage slot differ from the one served
before the run?"* — not *"did the workflow go green?"*

### 4.2 The three automations with the best ratio

`RECOMMENDED`, ranked by (blast radius avoided) ÷ (effort):

1. **Share-capture / re-share around every `CREATE OR REPLACE`** (rows 2–3). Highest ratio in the
   estate. The failure is silent, recurs (`:337`), has its own pending ticket, and the fix is two
   queries. Time saved: `ASSUMED`. **Failures avoided: `MEASURED` — at least one multi-day TEST
   staleness event.**
2. **Stage-slot render verification before swap** (row 8). The runbook calls it *non-negotiable* and
   names the incident that skipping it caused. It is the Consumer-Layer gate, unautomated.
3. **Snowflake TEST deploy driver** (row 1). Pure mechanical time. `ASSUMED` — nobody has timed a
   deploy; the instrument that would measure it is a timestamped phase log, which does not exist.
   `NOT-DETERMINABLE` until one does.

---

## 5. The dispatch record

### 5.1 What is recorded today

`factory/runs.py:144-149` writes: `at`, `lane`, `outcome`, `basis`, `detail`, `problems`, `branch`,
`commits`, `cost`.

**What is absent: everything identifying the configuration.** No model, no effort, no blueprint
version, no ticket key, no contract version, no eligible set, no difficulty. `cost.models` carries a
model list recovered from transcripts (`['claude-opus-5']` in the one recorded row) — that is
`RECONSTRUCTED` telemetry, not a declared configuration.

**Two ledgers, two populations** `MEASURED`:

| Ledger | Rows | Outcomes | Reads from |
|---|---|---|---|
| `.data/runs.jsonl` | **3** | `FINISHED` ×3 | `factory/runs.py:57` — agent-factory lanes |
| orchestrator sessions | **14** | 13 attributable to 6 Jira keys; 1 unattributable | `factory/readiness.py:625` — `prefect-connectors/.sessions` |

⛔ **All three rows in the lane ledger are `FINISHED`. The training set has zero negative examples.**
`runs.py:138-142` explicitly anticipated this — *"A refusal is the row you most want later"* — and
three rows later, none exists. `g_ever_refused` is `FAIL` (§6.2), which is the same fact from the
other side.

### 5.2 The schema

`RECOMMENDED` — one JSON object written **at dispatch**, before the agent starts, and closed at
terminal state. Fields, with the argument for each:

| Field | Why | Without it |
|---|---|---|
| `ticket` | attribution | `attributable` = `FAIL` today |
| `type_id`, `type_basis` | which taxonomy row, and whether a human confirmed it | type drift is invisible |
| `declared_scope` + `discovered_scope` | DV-444, GP-318, GP-310 all had refuted premises | cannot measure how often the ticket lies |
| `difficulty`, `novelty` — **declared before the run** | confounder control | every later comparison is Simpson's paradox |
| `eligible[]` — every config that passed the filter | **the counterfactual** | off-policy evaluation is impossible forever |
| `chosen`, `selection_rule`, `propensity` | argmax vs exploration draw | cannot correct for selection bias |
| `bundle_hash` + the 15 dimensions, each `covered`/`uncovered` | see §6.1 | certifications launder |
| `contract`, `contract_version`, `corpus_id` | `readiness.py:874-876` — *"a certification granted under contract V4 silently transfers to V5"* | verdicts are unattributable |
| `human_wait_s` separate from `agent_s` | the measured #1 cost (`docs/specs/control-room.md`) | optimising the wrong term |
| `escalations[]` with `was_correct` | pairs the activity metric | the 234/0 signature |
| `blast_radius_declared` | multiplier, not term (§7.3) | budget stands in for risk |
| `terminal_verdict` ∈ {PASS, FAIL, UNMEASURABLE, NOT_RUN} | never collapsed | `UNMEASURABLE` reads as pass |

⭐ **The `eligible[]` field is the whole point.** It costs nothing to write and cannot be
reconstructed later. Every other field can be backfilled with effort; this one is gone the moment
the run starts.

### 5.3 What it makes answerable

| Question | Today | With the record |
|---|---|---|
| Was that the right team? | no | yes — chosen vs eligible, same type, same difficulty band |
| Does opus beat sonnet on `wrong-number`? | no | yes, at N≈12 per arm (§7.4) |
| How often is the ticket's stated scope wrong? | no | **yes — and this is the cheapest high-value number in the design** |
| Is the selector better than the fixed default? | no | yes — regret account (§7.5) |
| Did escalation help? | no | yes |

---

## 6. Two defects found while designing the filter

### 6.1 ⛔ `TeamSpec.version` is blind to `repo` and to the team-level `prohibition`

`REPO-BACKED` — `factory/blueprint.py:43-52`. `TeamSpec` declares `repo` (`:43`) and `prohibition`
(`:44`); `version` (`:47-52`) hashes only `{team, topology, contract, agents}`.

**Discriminating test, result predicted before running** (prediction: identical hashes):

```python
t1 = TeamSpec(name='t', purpose='x', agents=[a], repo='prefect-connectors',
              prohibition='must not deploy to prod')
t2 = TeamSpec(name='t', purpose='x', agents=[a], repo='SOME-OTHER-REPO', prohibition='')
t1.version == t2.version     # -> True   d9f8107a11d6 == d9f8107a11d6
```

`MEASURED`. **A team certified in one repo under a production prohibition keeps its certification
when repointed at another repo with the prohibition removed.** Those are the two edits that change
blast radius, and the version — the object the README stakes certification on — cannot see either.

`AgentSpec.version` (`:31-33`) hashes `asdict(self)` and is correct; the defect is `TeamSpec` only.

**And the gate cannot catch it.** `g_version_hash_is_complete` (`readiness.py:867-879`) greps
`blueprint.py`'s **file text** for each dimension name. `repo` and `prohibition` are present in the
file, so a text-grep sees them regardless of whether they are hashed. The probe cannot distinguish
*"the field exists"* from *"the field is in the hash"* — the same self-matching-probe class the file
itself warns about 20 lines later (`:885-888`, the probe that *"MATCHED ITS OWN SOURCE"* and returned
a false green).

`RECOMMENDED`: hash `asdict(self)` minus `purpose`, and change the gate to compare two constructed
specs rather than grep source.

### 6.2 The correction: **6 of 15, not 0 of 15**

`docs/specs/product-end-state.md:66` states the config hash covers **"0 of 15"** identity dimensions.
The live gate reports **6 of 15** — `prompt, model, effort, tools, max_turns, budget_usd` present;
`tool_implementation, sandbox_image, model_routing, context_policy, external_knowledge, permissions,
contract_version, harness_version, side_effect_replay` missing `MEASURED`.

**This brief's own §5.1 repeated the "0 of 15" figure, inherited from that spec without re-measuring.**
Per the standing rule that correcting an inherited premise is a deliverable, the correction is filed
here and the prompt should be amended. The substantive claim survives — 9 dimensions are genuinely
absent, `contract_version` most damagingly — but *"the hash covers nothing"* is false and
overstates the case in a way that would have made §6.1's real defect harder to see.

---

## 7. The eligibility filter, its negative control, and the score

### 7.1 Gate state, measured

`python -c "from factory.readiness import measure; ..."` → **30 gates: 9 `PASS`, 17 `FAIL`,
3 `UNMEASURABLE`, 1 `NOT_RUN`** `MEASURED`. The ones that decide whether a selector may exist:

| Gate | Verdict | Consequence |
|---|---|---|
| `cap`, `ceiling`, `concurrency`, `reaper`, `bounded` | `FAIL` ×5 | **no bound on retries, spend, concurrency or abandonment** |
| `refuses` | `FAIL` | no gate has ever refused a run |
| `attributable` | `FAIL` | 2 of 14 runs untied to a ticket |
| `from-history` | `FAIL` | terminal verdict not computed from history |
| `finishes`, `succeeds` | `UNMEASURABLE` ×2 | the two outcome metrics a selector would optimise **cannot currently be read** |
| `certified` | `NOT_RUN` | nothing certified |

⛔ **A selector whose objective function is `UNMEASURABLE` is not a selector.** `finishes` and
`succeeds` are precisely the outcome terms any score would maximise. Building a ranker before those
two report a number is optimising against a gauge that is dark — the `UNMEASURABLE`-as-`PASS`
collapse, one level up.

### 7.2 The filter (stage 1)

`RECOMMENDED` — runs first, returns a possibly-empty set, in this order:

1. `type_id` unknown or unconfirmed → **empty** (scope discovery first)
2. verifier for this type is `UNBUILT` → **empty**
3. target contract reports `UNMEASURABLE` → **empty**
4. touches PROD → **empty** (human)
5. requires a secret → **empty** (standing rule)
6. repo is on the retiring side of a strangler-fig boundary → **empty**, with the successor named
7. `bundle_hash` certification expired or granted under a different `contract_version` → **empty**
8. any of `cap`/`ceiling`/`concurrency`/`reaper` is `FAIL` → **empty for every unattended run**

**Applying rule 8 alone against today's gate state, the filter returns empty for every unattended
run in the estate.** `DERIVED`. That is the correct answer and the UI must show it as a refusal with
its reason, not as an error.

### 7.3 The negative control

`RECOMMENDED`, non-optional, modelled on
`tests/test_connector_contract.py::test_every_assertion_has_been_proved_able_to_fail`:

```
test_every_filter_rule_has_been_proved_able_to_return_empty
```

One fixture per rule that must trip it, asserting the eligible set is empty **and** that the reason
names the rule. A filter with a rule no fixture can trip is a rule that does not exist.

Second control: `test_selector_refuses_when_objective_is_unmeasurable` — with `finishes`
`UNMEASURABLE`, the selector must refuse rather than fall back to a default.

### 7.4 The score (stage 2)

Only over a non-empty eligible set:

```
score = P(pass | type, difficulty, bundle) × value(type)
        ────────────────────────────────────────────────
        cost_agent + cost_human_wait + blast_radius × P(fail | …)
```

Three constraints:

* **Blast radius is a multiplier on the failure term, not an additive cost.** Removing an empty
  Eclipse filter (GP-327: one dashboard, reversible) and `CREATE OR REPLACE` on a shared Snowflake
  view (drops it from the share, silently, for days) are not the same decision at any budget.
* **`cost_human_wait` is first-class.** `docs/specs/control-room.md` measures four agents blocked on
  unread plain-English questions, one on a four-second yes/no. An agent that needs Paul when Paul is
  unavailable should score below a slower one that does not.
* **Every activity term is paired** per `factory/metrics.py:37-47`. In particular **escalation must
  carry `was_correct`**, or the maximum-scoring policy is *escalate everything* — 234 escalations,
  0 fixes, and a dashboard that climbs.

### 7.5 Staging, honest N, and the regret account

| Stage | Needs | Reachable? |
|---|---|---|
| 1 Rule-based filter | the taxonomy + `verifier_state` | **now** |
| 2 Hand-scored ranker | §7.4 weights, authored | **now**, weights `ASSUMED` |
| 3 Eval-backed | a contract per type; 1 of 16 has one | 2027 at current rate |
| 4 Historical | ≈**12 terminal runs per (type × bundle) arm** with the §5.2 record | **not before mid-2027** |
| 5 Bandit / search | ≥10 arms × stage-4 N, non-stationarity handled | `SPECULATIVE` |

**The N.** Stage 4's ≈12-per-arm is `DERIVED`, not measured: detecting the ≥10pp absolute gain R2
set as its unlock threshold, at conventional power, needs roughly that many paired terminal outcomes
per arm — and paired only because difficulty is declared (§5.2). Against **3 recorded lane runs, all
`FINISHED`**, and 14 orchestrator runs carrying no configuration at all, the estate is **two orders
of magnitude short**.

⛔ **A bandit at this N would fit noise and present it as policy.** Stage 5 is `SPECULATIVE` and
should not appear on a roadmap.

**The regret account.** Baseline = R2's prescription: one worker agent, non-LLM verifier in a clean
environment, human on privileged operations. For the selector to be more than theatre it must show,
on the same tickets and the same authoritative verifier, either ≥10pp terminal-success gain at equal
budget or ≥20% lower cost at indistinguishable success — R2's own thresholds
(`blueprints/orchestrator_team.yaml:22-30`). **Until the dispatch record exists, that comparison
cannot be computed, and the honest statement is that the selector's value is `NOT-DETERMINABLE`.**

---

## 8. Formations and teams

### 8.1 The R2 constraint, and what GP-311 does and does not change

`blueprints/orchestrator_team.yaml:1-30` rejects planner→implementer→tester with evidence: a
180-configuration study, multi-agent averaging −3.5%, sequential shared-state tasks degrading 39–70%,
and *"our own measured failures were ALL seam failures."*

GP-311's council of five caught six factual errors. **This does not overturn R2, and the distinction
is the useful part:**

* R2's rejected topology is a **sequential handoff chain on shared state** — each agent's output is
  the next one's input, and every seam is a place to lose information.
* `inquest` is a **parallel council on orthogonal lenses with a human arbiter** — no agent consumes
  another's output; the human reconciles. There are no seams to fail.

`INFERRED`, and it yields a rule: **parallelism over orthogonal views of the same artefact is
cheap and safe; sequential handoff on shared mutable state is what R2 measured and rejected.**

### 8.2 The catalogue

| Formation | Best for | Reach | Forbidden | Readiness |
|---|---|---|---|---|
| **Solo worker + non-LLM verifier** | types 1, 2, 7, 14 | one repo, one worktree | PROD; self-certifying | **`READY-NOW`** — R2's prescription |
| **Adversarial council + human arbiter** (`inquest`) | types 4, 12 | read-only across repos | writing anything | **`READY-NOW`** — `MEASURED` on GP-311 |
| **Measurement council** (`assay`) | type 11 | warehouse read-only | the client-facing artefact | **`READY-NOW`**, human-gated |
| **Watcher** (`vigil`) | recurring ops (§9) | monitoring surfaces | remediation | **`NEEDS-reaper`, `NEEDS-cap`** |
| **Render-validation pair** | types 1, 3, 5, 9 | stage slot + Playwright | swapping slots | **`NEEDS-` a wired render check** |
| Planner → implementer → tester | — | — | — | **`BLOCKED-BY-R2`** |
| Swarm with arbiter | — | — | — | **`BLOCKED-BY-R2`** + `refuses`=`FAIL` |
| Long-running maintenance crew | — | — | — | **`NEEDS-reaper`, `NEEDS-ceiling`, `NEEDS-cap`** |

⭐ **Three of the four `READY-NOW` formations already exist as skills** (`inquest`, `assay`, `vigil`)
and one of them has `MEASURED` evidence on a real ticket. **The selector's job is routing to these,
not designing successors to them.** `RECOMMENDED` — the team registry's first entries should be the
Council skills, versioned by their `SKILL.md` content hash so `external_knowledge` and
`context_policy` become hashable dimensions (two of the nine missing from §6.2).

---

## 9. Recurring operations, and what silence means

Per the `vigil` standard: a watcher whose silence has not been proved to mean health is not a watcher.

| Operation | Disposition | What silence means today |
|---|---|---|
| Data-share gap detection | `AGENT-ASSISTED` | ⛔ **`NOT-VISIBLE`** — GP-PENDING-data-share-stability exists *because* silence meant nothing; the 2026-04-21 drop was found by a failure, not a watcher |
| Connector failure sweep | `SEMI-AUTOMATED` | ⛔ **`NOT-VISIBLE`** — FU92-421's LinkedIn accounts stopped at a single shared instant and nothing noticed; GP-286's CSV connector *silently drops the entire file* |
| Token-expiry watch | `MANUAL` | ⛔ **`NOT-RECORDED`** — FU92-416 records two live connectors whose token lifespan is *unknown and undocumented* |
| 06:00 PDT materialisation | `AGENT-ASSISTED` | `NOT-VISIBLE` unless the task chain is queried |
| Snowflake credit check | `AGENT-ASSISTED` | `ZERO` is meaningful — billing is a live instrument |
| PBI refresh / XMLA token | `SEMI-AUTOMATED` | `NOT-RECORDED` |
| Jira triage (GP/FU92/DV) | `MANUAL` | n/a |
| Client QA queue | `MANUAL` | n/a |
| Eclipse deploy health | `AGENT-ASSISTED` | ⛔ **actively misleading** — §4.1 |

⛔ **Six of nine are `NOT-VISIBLE` or `NOT-RECORDED`, and three of those have a ticket proving a real
failure went unnoticed.** `RECOMMENDED`: no watcher is promoted to `AUTOMATED` until it has been
made to fire end-to-end through its scheduled path. Automating a blind watcher converts an unknown
into a false reassurance.

---

## 10. Memory typing, staleness, citation

| Layer | Typed enough for a selector? |
|---|---|
| Ticket frontmatter (`tags`, `aliases`) | **Yes** — 59/59 have `tags`; the corpus's only machine-readable index |
| `**Type/Status**` lines | **No** — free text, present on ~⅓ `MEASURED` |
| Prose sections | **No — cite, never parse** |
| Gate verdicts (`readiness.measure()`) | **Yes** — typed, live |
| `.data/runs.jsonl` | **Structurally yes, semantically empty** (§5.1) |
| Eval corpus (`evals/MANIFEST.sha256`) | **Yes, and must stay agent-immutable** |
| Zeus Memory | `NOT-DETERMINABLE` — not inspected this pass |

**Never agent-editable:** the eval corpus and its manifest; `docs/findings.d/`; the append-only task
store (`factory/tasks.py:5-9`); any `seen_in` citation.

**Staleness.** `blueprints/windsorai_client_a.yaml` carries a tenant list verified 2026-05-29 and
used in August, annotated in the file: *"A `PASS` on A12 means 'the landing matched what we
declared', not 'what we declared is still correct'."* `RECOMMENDED` — every certification carries
`certified_at` + `valid_until`; the filter refuses an expired bundle (rule 7); expiry is a **refusal
with a re-measurement command**, never a downgrade to a warning.

**Citation.** A memory that influences a dispatch is recorded as `{source_path, line, read_at,
content_hash}` in the dispatch record. When it is later found wrong, the affected dispatches are
enumerable — the FU92-420 problem in reverse.

---

## 11. Roadmap

| Phase | Goal | Files | Tests | Done when |
|---|---|---|---|---|
| **0** | Close the version hole | `factory/blueprint.py`, `factory/readiness.py:867` | two constructed specs differ in `repo` → different version; ditto `prohibition` | §6.1 test inverts |
| **1** | Dispatch record | `factory/dispatch_record.py`, `factory/runs.py` | round-trip; **refuses to write without `eligible[]`** | one real run recorded with all §5.2 fields |
| **2** | Taxonomy + refusal rows | `factory/presets.py` | every row has ≥2 `seen_in`; refusal rows carry an unblocking condition | 16 types represented, 11 as refusals |
| **3** | Eligibility filter | `factory/selector.py` | `test_every_filter_rule_has_been_proved_able_to_return_empty` | every rule has a tripping fixture |
| **4** | Unblock the bounds | — | — | `cap`, `ceiling`, `concurrency`, `reaper` all `PASS` |
| **5** | Make the objective readable | `factory/readiness.py` | — | `finishes` and `succeeds` stop reporting `UNMEASURABLE` |
| **6** | Share-capture automation | `clients` | replace-then-verify on a shadow share | rows 2–3 of §4 automated |
| **7** | Render verification | `factory/pbi_contract.py` + Playwright | a blank visual must `FAIL` | row 8 of §4 automated |
| **8** | Hand-scored ranker | `factory/selector.py` | regret vs baseline computable | §7.5 comparison runs |

**Ordering constraint:** phases 0–3 are independent of 4–5 and should run first; **phase 8 must not
start until 5 completes**, because a ranker maximising an `UNMEASURABLE` objective is the failure
this repo exists to prevent.

---

## 12. Risks and anti-patterns

1. ⛔ **Certification laundering** — §6.1. Already live.
2. ⛔ **A probe that greps its own subject's source text** — `readiness.py:867-879` vs `:885-888`.
   The repo documents this failure and then commits it in the next function.
3. ⛔ **A green CI run that changes nothing** — §4.1. Live in `eclipse`, diagnosed, still shipped.
4. **Training on an all-success ledger** — 3 rows, 3 `FINISHED`. Any model fit to this predicts
   success unconditionally and will be right 100% of the time on its training set.
5. **Filling the preset table to look ready** — §3.2.
6. **Treating `UNMEASURABLE` as a soft pass** — `finishes` and `succeeds` are the objective.
7. **Inheriting a number without re-measuring** — §6.2, committed by this brief.
8. **Confusing parallel councils with sequential handoff chains** — §8.1; conflating them either
   forfeits a working formation or resurrects a rejected one.

---

## 13. What this pass could not determine

| Question | Verdict | Command / artefact that would settle it |
|---|---|---|
| Time cost of a manual Snowflake deploy | `NOT-DETERMINABLE` | a timestamped phase log; none exists |
| Do the 14 orchestrator runs and the 3 lane runs overlap? | `NOT-DETERMINABLE` | `ls prefect-connectors/.sessions` + join on ticket key — `.sessions` is absent from this checkout (`ls .sessions` → 0) |
| Is Zeus Memory queryable as typed selector input? | `NOT-DETERMINABLE` | `mcp__ccx__cce_memory_search` against a known ticket key |
| Does `pbi_model_apply.exe` cover relationships as well as measures? | `NOT-DETERMINABLE` | `pbi_model_apply --help`; `pbi-model-apply-wrapper.md` implies yes, unverified |
| How often is a ticket's stated scope wrong? | `NOT-DETERMINABLE` — 3 instances found (DV-444, GP-318 ×2, GP-310), denominator unknown | the `declared_scope`/`discovered_scope` pair in §5.2; **this is the strongest single argument for building the record** |
| Are the 5 existing presets the right 5? | `ASSUMED` — §0 | a genuinely blind second pass by a different session |
| What does `succeeds` need to stop being `UNMEASURABLE`? | `NOT-DETERMINABLE` | read `g_succeeds_more_than_fails` and its `Unmeasurable` raise path |

---

### Appendix — regeneration commands

```bash
cd ~/repos/wiki
find tickets -name '*.md' ! -name '_*' | wc -l                                  # 59
find tickets -name '*.md' ! -name '_*' | awk -F/ '{print $2}' | sort | uniq -c  # 45/11/2/1
ls processes/deployment/*.md | wc -l                                            # 13
grep -ilE 'manual|by hand' processes/deployment/*.md | wc -l                    # 8

cd ~/repos/agent-factory
python -c "from factory.presets import PRESETS,WIRED; print(len(PRESETS), sum(1 for p in PRESETS if p.verifier_state==WIRED))"   # 5 1
python -c "
from factory.readiness import measure
import collections; print(collections.Counter(r.verdict for _,r in measure()))"  # PASS 9, FAIL 17, UNMEASURABLE 3, NOT_RUN 1
python -c "from factory import runs; h=runs.history(); print(len(h), {r['outcome'] for r in h})"  # 3 {'FINISHED'}
python -c "
import factory.readiness as R; r=R.g_version_hash_is_complete()
print(r.verdict, r.evidence[0])"                                                 # FAIL, 6 of 15
```

All figures re-measured 2026-08-29. A figure that has moved is a finding.
