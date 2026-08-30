# R19 — The ALDC work taxonomy, and how a team gets chosen for a ticket

**Status: ANSWERED 2026-08-29.** Written 2026-08-29. Answer:
[`answers/R19-answer-work-taxonomy-and-team-selection.md`](answers/R19-answer-work-taxonomy-and-team-selection.md).

**Pass type:** STRUCTURE_CRITIQUE
**Depends on:** R16 (decision review and order) — this pass proposes a *selector*, and R16 is the
pass that says which decisions are still open. Running this first is possible; it will re-litigate
things R16 already settled.

⚠ **The researcher for this pass is a Claude Code session running in the `agent-factory` checkout,
with `~/repos/wiki` and the sibling repos readable.** It is not a web tool and there is no evidence
pack. Read the sources directly. Every internal claim carries `path:line`. A claim with no citation
is an opinion and must be labelled one. Where something cannot be established from the repos, say
`NOT-DETERMINABLE` and name the single command or artefact that would settle it.

⛔ **`STRUCTURE_CRITIQUE` means independence risk HIGH and the run is BLIND-FIRST.** This pass reads
our own code and our own wiki, so it is pulled toward agreeing with us. Form a view from the primary
sources — the tickets and the runbooks — **before** reading `factory/presets.py`, which already
contains an answer to part of this question. Then say where the code and the tickets disagree.

## Run log

| Run | Date | Outcome |
|---|---|---|
| 1 | 2026-08-29 | ANSWERED in-repo. ⚠ **Blind-first partially violated** — the answering session had already read `factory/presets.py` while writing this brief; see §0 of the answer. Findings about the five existing presets carry no independent weight. |

---

## 0. What is different about this pass, and what it must not re-derive

The generic version of this brief asked for a design-from-scratch: *"design a team registry, design a
task lifecycle, design a selector, assess whether this system needs a wiki."* **That brief is wrong
for this repo, in five specific ways, and answering it as written would produce a document that is
already contradicted on disk.**

| The generic brief assumes | What is actually on disk | Consequence for this pass |
|---|---|---|
| No task/ticket→config mapping exists | `factory/presets.py` — 5 types, each with `seen_in` citing a real ticket, a `model_why`, an `escalate_when`, a `prohibition`, and a `verifier_state` | Do **not** invent a preset table. **Extend and attack the one that exists.** |
| A team registry must be designed | `factory/blueprint.py` (`AgentSpec`/`TeamSpec`), `blueprints/*.yaml`, `factory/roadmap.py:181` (`TEAMS`) | Design the *gap*, not the object |
| A planner→implementer→tester team is a formation to catalogue | `blueprints/orchestrator_team.yaml` opens with **⛔ SUPERSEDED BY EVIDENCE 2026-08-21 — DO NOT BUILD THIS TEAM**, citing a 180-configuration study and our own seam-failure history | Any formation catalogue that re-proposes it must first clear R2's stated A/B threshold |
| "Assess whether this system needs a wiki or a memory layer" | A 490-file wiki with a `[[wikilink]]` graph, YAML frontmatter, 59 ticket pages and 13 deployment runbooks; plus Zeus Memory over MCP | The question is not *whether*. It is **which parts are typed enough to be a selector input, and which are prose that must never be** |
| Metrics/monitoring must be designed | `factory/metrics.py` enforces activity/outcome pairing (`GoodhartViolation`); `factory/readiness.py` holds 30 gates; `factory/runs.py` is the run ledger | Design what the ledger must **record at dispatch time** so a selector can ever be trained. See §5 — this is the highest-leverage item in the pass |

⭐ **The one sentence that should govern the whole answer:** *the optimiser is not the missing piece —
the logging schema is.* Nothing in the estate currently records **which configurations were eligible
and were not chosen**, so no amount of future history can answer "was that the right team?". That is
a decision that has to be made before the data accumulates, not after.

### Counts in this brief, with the commands that produced them

Per the standing rule that a hand-typed count re-rots invisibly. All run 2026-08-29.

```bash
# in ~/repos/wiki
find tickets -name '*.md' ! -name '_*' | wc -l                      # 59 ticket pages
find tickets -name '*.md' ! -name '_*' | awk -F/ '{print $2}' | sort | uniq -c
                                                                     # gep 45, fusion92 11, dv 2, aldc 1
ls processes/deployment/*.md | wc -l                                 # 13 deployment runbooks
grep -ilE 'manual|by hand' processes/deployment/*.md | wc -l         # 8 of 13 name a manual step
find entities/tools -name '*.md' | wc -l                             # 26 tool pages
find entities/repos -name '*.md' | wc -l                             # 17 repo pages

# in ~/repos/agent-factory
python -c "from factory.presets import PRESETS,WIRED; print(len(PRESETS), sum(1 for p in PRESETS if p.verifier_state==WIRED))"
                                                                     # 5 presets, 1 WIRED
python -c "from factory.readiness import GATES; print(len(GATES))"   # 30 gates
ls factory/*.py | wc -l ; cat factory/*.py | wc -l                   # 40 modules, 9,142 lines
```

Re-run them before citing any of these numbers. If one has moved, **that is a finding.**

---

## 1. The deliverable

A design-authority document, filed as `docs/research/answers/R19-answer-work-taxonomy-and-team-selection.md`,
that a session can build from without re-deciding anything.

**Basis labels are mandatory on every load-bearing claim.** This repo already runs two vocabularies
and they are not interchangeable — use both, in this pairing:

| For claims about the world | For claims about this design |
|---|---|
| `MEASURED` we ran it and have the number · `DERIVED` computed from something measured · `STATED` a written brief or ticket says so · `ASSUMED` nobody has confirmed this · `PROXY` a stand-in for the thing we actually care about | `REPO-BACKED` cited to `path:line` · `INFERRED` reasonable reading of the code's direction · `RECOMMENDED` proposed, not present · `EXTERNAL` supported by an outside system or paper · `SPECULATIVE` interesting, not yet justified |

⛔ **Never present a `RECOMMENDED` or `SPECULATIVE` item in the present tense.** This estate has twice
shipped a mechanism that read as built and was not.

---

## 2. Ground truth — the ecosystem the selector has to live in

**Read these before designing anything.** The selector is worthless if it recommends a team that
cannot reach the system the ticket is about.

### 2.1 The repos an agent can be deployed into

`REPO-BACKED` — `~/repos/wiki/concepts/architecture/repo-integration-map.md`, and the 17 pages under
`entities/repos/`. The map's own framing matters: ALDC is mid-flight on **two overlapping
consolidations** (platform onto `eclipse_exp`; connector data-plane onto Prefect), neither with a
cutover date. A selector that does not know which side of a strangler-fig boundary a ticket sits on
will route work into a repo that is being retired.

| Repo | What work lands here | Deploy path |
|---|---|---|
| `clients` | per-client Eclipse JSON configs + Snowflake warehouse SQL (19 client folders, 150+ connections, 300+ templates, 200+ views) | **manual** — paste into Snowsight |
| `power_bi` | ~94 `.pbix` binaries, Git LFS ~16 GB | XMLA for metadata; **PBI Desktop republish** for visuals |
| `core_api` | Azure Functions control plane, CosmosDB-backed | `func publish` / Azure |
| `eclipse` | Next.js 14 legacy portal | **manual `workflow_dispatch`** container build → `stage` slot → **manual swap** |
| `eclipse_exp` | FastAPI + Next.js 15 successor, 67 RLS Postgres tables, 87 migrations | container |
| `connector` | legacy Docker connector runtime, Portainer on VMs | **ssh + `sudo ./build.sh` + interactive prompts** |
| `prefect-connectors` | the 18-stage build plane; 49 connectors | Prefect deployments — **migration SHELVED 2026-05-28** |
| `flight-check`, `workflows`, `custom-fusion-92-audience-api`, `prospect-site-template` | client-facing products | mixed |
| `agent-factory`, `wiki`, `aldc-launchpad`, `claude_code_enhanced` | the factory itself, and its memory | n/a |

### 2.2 The systems, data stores and external APIs a ticket can be *about*

`REPO-BACKED` — the 26 pages under `entities/tools/`, plus the runbooks.

* **Warehouses / DBs:** Snowflake (`TEST_DG1_GEP`, `PROD_DG1_GEP`, `QA_DG1_ALDC_QA`,
  `PROD_DG1_ALDC_LIBRARY`, reader accounts, **data shares**, tasks, the 06:00 PDT materialisation
  window), CosmosDB (Eclipse app/dashboard/filter documents), Postgres (eclipse_exp RLS; portal
  `app_report`), SQL Server.
* **Reporting:** Power BI — PPU capacity, XMLA endpoint, TOM + Roslyn via `pbi_model_apply.exe`,
  **MSAL device-code auth with a specific approved public client id**, `.pbix` in LFS.
* **Cloud / infra:** Azure (Functions, App Service + `stage` slot, Key Vault `aldc-vault-test` /
  `aldc-vault-prod`, Blob, Container Apps), Docker + Portainer on VMs (Kamloops, Coquitlam),
  Proxmox, NFS mounts, Cloudflare DNS, GitHub Actions.
* **Orchestration:** Prefect 3 at `prefect.analyticlabs.io` (QA/UAT/Prod work pools) — **shelved**;
  the live path is still the legacy Eclipse `/work/pick` poll.
* **External vendor APIs (the most common source of a ticket):** Windsor.ai, Amazon Ads + SP-API +
  Amazon Attribution, Google Ads, Google Analytics, Meta/Facebook, Microsoft/Bing Ads, LinkedIn,
  Trade Desk, Viant, NetSuite, SellerCloud, Airtable, DIOS, Mailjet.
* **Process surfaces:** Jira (projects `GP`, `FU92`, `DV`, `ALDC`, `SHIP`), Confluence, the wiki,
  Zeus Memory over MCP, Postman, Dashlane, Nextcloud.

### 2.3 The eight authorities that already constrain any answer

`REPO-BACKED` — `~/.claude/CLAUDE.md` and this repo's `README.md`. **These are not preferences. A
design that violates one is rejected, not debated.**

1. **Evidence-Gated Changes** — prove the target with a *discriminating* test; never infer the source
   from matching values; **never inherit a target from a ticket or handoff without walking the
   consumer route yourself**.
2. **Consumer-Layer / Dashboard-UI Validation** — for any dashboard or UI change, "the consumer's
   layer" is the **rendered surface**, not the query. A DAX check can pass while every visual shows
   "Error loading data" (proven, GP-293).
3. **Evidence-Gated Analysis** — declare the counting basis *before* producing a number; enumerate
   the population; **a zero from an instrument you have not proved can still see is not a
   measurement**; separate `ZERO` / `NOT-RECORDED` / `NOT-VISIBLE` / `NOT-RETAINED`.
4. **Credential handling** — ask before retrieving any secret, every time. One approval covers one
   retrieval.
5. **The four verdicts, never collapsed** — `PASS` / `FAIL` / `UNMEASURABLE` / `NOT_RUN`.
   `UNMEASURABLE` is not a pass.
6. **Activity metrics are paired with outcome metrics** — `factory/metrics.py` raises
   `GoodhartViolation` if they are not.
7. **Append-only, evidence-gated task closure** — `factory/tasks.py`.
8. **Counts carry their regeneration command.**

---

## 3. The work taxonomy — the part this pass exists for

`factory/presets.py` holds **5 types, generalised from real tickets, of which 1 has a `WIRED`
verifier.** All five are Navira/PBI/Eclipse *delivery* shapes. The 59 ticket pages in the wiki
contain materially more shapes than that, and the uncovered ones include the classes with the
largest blast radius.

**Task 3.1 — Derive the taxonomy from the tickets, blind.** Read every page under
`~/repos/wiki/tickets/` **before** opening `factory/presets.py`. Produce a type table where each row
carries:

* `type_id`, title
* `seen_in` — **at least two real ticket ids.** A type with one ticket behind it is an anecdote;
  say so and mark it `PROVISIONAL`.
* the **layers** it touches (`snowflake`, `pbi_model`, `eclipse`, `cosmos`, `core_api`, `connector`,
  `prefect`, `azure`, `vendor_api`, `client_comms`)
* the **consumer layer** the fix must be validated at — and which of the three gates in §2.3 applies
* the **deterministic verifier** that should own the verdict, and its honest `WIRED` / `AVAILABLE` /
  `UNBUILT` state
* **blast radius** — what breaks if this goes wrong, in the worst realistic case
* what only a human can settle

The following are candidate types visible in the ticket corpus. **Treat this list as a hypothesis to
attack, not a finding** — the same standing rule this estate applies to a ticket or a handoff. Add,
merge and delete freely, and say why.

| Candidate type | Tickets seen in | Covered by `presets.py`? |
|---|---|---|
| UI control change (Eclipse/Cosmos config) | GP-327, DV-444 | yes — `ui-control`, the only `WIRED` row |
| Additive semantic-model change | GP-329, GP-256 | yes — `add-measure` |
| Dimension gap / blank member | GP-328, GP-312 | yes — `dimension-gap` |
| A wrong number the client can see | GP-322, GP-311, GP-282 | yes — `wrong-number` |
| Model redesign / legibility | GP-318, GP-319 | yes — `model-redesign` |
| **New source ingestion / schema extension** | GP-200, GP-203, GP-204, GP-208, GP-257, GP-287 | **no** |
| **Connector failure / data freshness** | FU92-394, FU92-421, GP-286, GP-PENDING-infra | **no** |
| **Auth / token lifecycle** | FU92-393, FU92-395, FU92-396, FU92-415, FU92-416 | **no** |
| **RBAC / "Error loading data"** | GP-304, GP-310 | **no** |
| **Infrastructure / environment isolation / CI-CD** | GP-217, GP-218, GP-248, GP-207 | **no** |
| **Usage audit / analysis deliverable** | FU92-420 | **no** — and this is the class that produced five wrong client answers with zero deploys |
| **Incident / outage** | GP-PENDING-sales-data-outage, GP-PENDING-infra-connector-failures | **no** |
| **Client onboarding / multi-tenant** | GP-254, GP-261 | **no** |
| **Support / one-off data exclusion** | GP-283, GP-284 | **no** |
| **Platform app bug** | ALDC-622, DV-506, GP-277 | **no** |
| **Scoping / design ticket** | GP-199, GP-225, GP-258, GP-288 | **no** |

**Task 3.2 — For each uncovered type, say whether it should get a preset at all.** Some should not.
A type whose verifier is `UNBUILT` and whose blast radius is production data cannot be
auto-dispatched, and writing a preset for it manufactures the appearance of readiness. Where that is
your conclusion, the row's honest content is a **refusal with a named unblocking condition**.

---

## 4. Manual deployment — what is manual, what should stay manual, and what is one script away

`MEASURED` — 8 of 13 deployment runbooks name a manual step. The interesting question is not "how
much is manual" but **which manual steps are load-bearing human judgement and which are just
unautomated.**

**Task 4.1 — Build the manual-step ledger.** One row per manual step across the 13 runbooks, each
with: the runbook and line, what the human actually does, *why* (judgement / no API / nobody has
written it / safety), the failure it prevents, and a verdict of **`KEEP-HUMAN` / `AGENT-ASSISTED` /
`AUTOMATABLE-NOW` / `AUTOMATABLE-AFTER-CERTIFICATION`**.

Known steps to start from, all `REPO-BACKED`:

* **Snowflake deploy is copy-paste into the Snowsight UI**, per file
  (`processes/deployment/gep-snowflake-pbi-deployment.md:93`). The runbook's own key principle:
  *"Code merge does NOT auto-deploy. Snowflake and Power BI deploys are always manual steps."*
* **The 06:00 PDT materialisation window** — rows deployed during the day do not appear in
  `WAREHOUSE.*` until the next window unless a task is manually triggered through the Snowsight
  Graph tab.
* **The data-share trap** — `CREATE OR REPLACE TABLE/VIEW` **removes the object from the share**.
  The shared-object list must be captured first (`client-release-checklist.md:30`). This is the
  clearest example in the estate of a blast radius that is invisible at the layer you are editing.
* **Power BI is split** — metadata-only changes go through `pbi_model_apply.exe` (TOM + Roslyn,
  MSAL device-code, token cached to `%LOCALAPPDATA%`); **anything touching visual layout still
  requires a PBI Desktop republish**.
* **Eclipse deploys are a manual `workflow_dispatch` to the `stage` slot, then a manual swap** — and
  the *other* workflow, "Deploy to Azure App Service", **is a no-op that reports success on every
  run** (`eclipse-azure-deployment.md:16`). A green CI run that changed nothing is the exact failure
  mode this repo was built to catch; say what an agent would have to check to tell the difference.
* **Connector image builds are `ssh` + `cp config-test.json config.json` + `sudo ./build.sh` with
  interactive prompts**, then Portainer.
* **Secret retrieval** — Dashlane, the wiki vault, and Azure Key Vault. Human approval per
  retrieval, by standing rule.

**Task 4.2 — Name the three automations with the best ratio of measured time saved to blast
radius**, with the evidence for the "measured" half. If the time is not measured, say `ASSUMED` and
name the instrument that would measure it.

---

## 5. Selection — how a ticket gets a team, staged honestly

⭐ **This is the section the pass will be judged on.** The brief it replaces asked for
"rule-based → score-based → eval-backed → historical → bandit". That staging is fine and is not the
hard part. **The hard part is that stages 3–5 are unreachable with the data currently recorded, and
nothing in the estate is on a path to record it.**

### 5.1 The prerequisite nobody has built: the dispatch record

`REPO-BACKED` — `factory/runs.py` is the lane run ledger, written because "a finished lane currently
leaves no trace at all". `docs/specs/product-end-state.md` states the config hash covers **0 of 15**
identity dimensions.

**Design the dispatch record.** At the moment a team is chosen, what must be written down so that,
months later, someone can ask "was that the right choice?" and get an answer rather than a story.
At minimum, argue for or against each of:

* the **eligible set** — every configuration that passed the eligibility filter and was *not*
  chosen. Without this there is no counterfactual and no off-policy evaluation, ever.
* the **selection propensity** — was this the argmax, or an exploration draw? Under what rule?
* the **full bundle hash** — model, effort, prompt version, skill versions, tool scope, isolation
  tier, contract version, memory/corpus snapshot. State which of the 15 dimensions are covered today
  and which are not.
* the **declared difficulty and novelty**, recorded **before** the run. Matching on ticket type
  alone is confounded by difficulty; without a pre-declared covariate every later comparison is
  Simpson's paradox wearing a dashboard.
* the **human-time cost** — wall-clock spent waiting on a person, separately from agent time.
* the **escalation** — what was escalated, to whom, and whether the escalation was *correct*.

### 5.2 The eligibility filter comes before the score

Design a **hard filter that runs first and can return an empty set.** Candidate conditions:
no wired verifier for this type; the contract for the target layer is `UNMEASURABLE`; the ticket
touches PROD; a secret would be needed; the repo is on the retiring side of a strangler-fig
boundary; the certification of the candidate bundle has expired.

⛔ **A selector that always returns a team is the 965-run loop again.** Specify the **negative
control**: the test that proves the selector *can* refuse, and the fixture that makes it refuse.
This is the direct analogue of `test_every_assertion_has_been_proved_able_to_fail` and the pass
should treat it as non-optional.

### 5.3 Scoring, and what it must not be

Design the score. Be explicit that **cost-of-being-wrong is not cost-of-the-run**: removing an empty
Eclipse filter and issuing `CREATE OR REPLACE` against a shared Snowflake view are not the same
decision at any budget. Blast radius must be a multiplier, not a term.

Pair every activity signal with an outcome signal, per `factory/metrics.py`. In particular:
**escalation rate must be outcome-paired or the selector will converge on configurations that
escalate everything** — safe, useless, and exactly the retired agent's 233 diagnoses / 234
escalations / 0 fixes.

### 5.4 Say plainly when the optimiser becomes legitimate

`MEASURED` — 59 ticket pages exist and 14 runs have been recorded. **State the N, per ticket type,
at which each stage stops overfitting**, and say which stage the estate can honestly reach in the
next quarter. If the answer is "stage 2 for the next year", say that. An answer that recommends a
bandit at this N is wrong and will be treated as a failed pass.

Include a **regret account**: how would we know the selector is better than the fixed default of
"one sonnet worker, non-LLM verifier, human on privileged operations"? If that cannot be measured,
the selector is theatre and the pass should say so.

---

## 6. Teams and formations

`blueprints/orchestrator_team.yaml` records a rejected hypothesis and keeps it deliberately —
planner → implementer → tester was tested and rejected, with an explicit unlock threshold (**≥10pp
absolute terminal-success gain at the same budget on the same tasks and the same authoritative
verifier, or ≥20% lower cost at indistinguishable success, no increase in side effects, every
mandatory handoff ≥99% accepted-and-correctly-consumed**).

**Design the formation catalogue against that constraint, not around it.** For each formation:
purpose, roles, tool scope, required contract, prohibitions, evidence requirements, when *not* to
use it, and — the field that matters — **`READY-NOW` / `NEEDS-<named gate>` / `BLOCKED-BY-R2`**.

Ground the team designs in the taxonomy from §3 rather than in generic categories. The teams this
estate would actually staff look like: connector migration, data-quality / wrong-number
investigation, consumer-layer validation (rendered surface, Playwright), release readiness,
incident response, analysis-and-measurement (the FU92-420 class, which needs the counting-basis gate
more than it needs agents), auth/credential lifecycle, wiki/documentation, and repo onboarding.
**For each, state which of the 26 tools and which repos it needs reach into, and what it is
forbidden to touch.**

---

## 7. Recurring operations

Replace the generic startup-process list with the ones this company actually has. Candidates,
`DERIVED` from the tickets and runbooks: connector failure sweep; data-share gap detection
(GP-PENDING-data-share-stability); Snowflake credit check; Prefect / legacy work-pick health; PBI
refresh and XMLA token expiry; the 06:00 PDT materialisation confirmation; Jira triage across GP /
FU92 / DV; the client QA queue; token-expiry watch across the vendor APIs in §2.2.

For each: `MANUAL` / `SEMI-AUTOMATED` / `AGENT-ASSISTED` / `AUTOMATED-AFTER-CERTIFICATION`, plus
**what its silence means.** A watcher whose silence has not been proved to mean health is not a
watcher — that is the `vigil` standard and it applies here.

---

## 8. Memory, and the line agents must not cross

The wiki exists and is large. The design question is **typing**, not adoption.

* What is **structured enough to be a selector input** — ticket frontmatter, tags, `seen_in`
  citations, gate verdicts, run ledger rows?
* What is **prose that must stay prose** and be *cited* rather than parsed?
* What must be **append-only and never agent-editable** — the eval corpus (`evals/MANIFEST.sha256`),
  the findings ledger, the task store?
* **Staleness.** `blueprints/windsorai_client_a.yaml` carries a tenant list verified 2026-05-29 and
  used in August, with the staleness annotated in the file. Design the general mechanism: does a
  certification expire, and what does a selector do with an expired one?
* **Citation in evidence.** When a memory influences a decision, how does it appear in the evidence
  trail so the decision can be re-audited when the memory turns out to be wrong?

---

## 9. Output format

1. Executive thesis — one page, and it must contain the single highest-leverage thing to build next
2. Blind read of the ticket corpus — the taxonomy, derived before reading `presets.py`
3. Where the taxonomy and `presets.py` disagree, and which is right
4. The manual-step ledger, with verdicts
5. The dispatch record — the schema, and what it makes answerable that today is not
6. The eligibility filter, its negative control, and the score
7. Staging, with the honest N per stage and the regret account
8. Formations and teams, each with its readiness verdict
9. Recurring operations, each with what its silence means
10. Memory typing, staleness and citation
11. Roadmap — phases with files, tests and completion criteria, ordered so nothing is built before
    its precondition
12. Risks and anti-patterns, led by the ones this estate has already committed once
13. What this pass could not determine, and the command that would settle each

Mermaid where a picture carries something prose cannot. Tables where they carry more than prose.
**Be direct and attack weak assumptions, including the ones in this brief.** A pass that agrees with
everything above has not done its job — this brief was written by the same estate it is auditing.
