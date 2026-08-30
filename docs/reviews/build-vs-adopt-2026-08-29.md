# Build vs adopt — component by component, decided

**Pass:** `/prospect`, six independent lenses, 2026-08-29. **Source:** `docs/BUILD-VS-ADOPT-PROMPT.md`
(277 lines). **Branch:** `feat/readiness-generator` @ `17a6a5a`.
**Method:** every `BET-CHANGING` claim was re-verified by the synthesiser against the primary source
before entering this document. Where my measurement disagreed with a lens's, mine is published and
the divergence is recorded (§8).

---

## 0. ⭐ The sequencing constraint — read this before any verdict

**The factory has never certified a connector. Its own launch gate says so:**

```
May I TRUST what it produced?
  OUTPUT-UNCERTIFIED
    - certified    NOT_RUN      12 assertions have no instrument wired
    - breadth      FAIL         1 case(s), 0 strata — below any calibration threshold
    - suite        FAIL         21 failed, 388 passed, 2 xfailed (0:01:55)
```
<sub>Regenerate: `python -m factory.launch`</sub>

`factory/live_probes.py` wires **A1** and **A5** only, and its own docstring notes both are reachable
*"with no credential and no network call"*. Every other verb inherits `Probes._refuse`. So A2, A3,
A4, A6, A7, A8, A9, A10, A11, A12 — **the entire assertion battery this pass was asked to price an
adoption for, plus the whole tenancy claim** — have never been evaluated against a live target.

**Consequence for this document.** Bets 1, 2 and 3 are migrations priced against interfaces that have
never carried traffic. A9 "semantic invariants" cannot be compared with `pandera` on merit, because
A9 has never done anything. The verdicts below are the best available and several are decisive on
platform or licence grounds that hold regardless — but:

> **No ADOPT verdict in this document should be actioned before one connector is certified end to
> end.** The cheapest path to that is wiring A2 and A7 against `blueprints/windsorai_client_a.yaml`.

This is `devil`'s finding, confirmed independently by the synthesiser. It is not a criticism of the
repo's honesty — `live_probes.py` refuses on purpose, precisely so UNMEASURABLE cannot become PASS
just because *some* instrument exists. That is the system working. It is a statement about what this
research pass can and cannot know.

---

## 1. ⭐ The headline thesis survives, but not as written

The source document's closing prior:

> *"the strongest build case is the refusal semantics — `UNMEASURABLE` as a verdict and evidence-basis
> enforced in code — which I do not recall seeing as a first-class feature in any scorecard or
> data-quality product."*

**That recall is wrong, and it is falsifiable in about four minutes.** Six independent instances of a
non-binary verdict state were found, all in maintained tools or standing standards:

| Source | The state | Read at |
|---|---|---|
| **OpenSSF Scorecard** | `InconclusiveResultScore = -1`, *"returned when no reliable information can be retrieved by a check"* | `checker/check_result.go`, 336 ln |
| **Soda Core** | `CheckOutcome.NOT_EVALUATED` **and** `EXCLUDED` — two states for two different claims | `contracts/contract_verification.py`, 608 ln |
| **datacontract-cli** | `ResultEnum` = `passed, warning, failed, error, info, skipped, unknown` | `model/run.py`, **281 ln** ✅ verified by synthesiser |
| **Dagster** | `EXECUTION_FAILED  # hit some exception`, `SKIPPED  # the check didn't execute` | `asset_check_execution_record.py`, **334 ln** ✅ verified |
| **W3C EARL 1.0** | `earl:CannotTell` — *"an undetermined outcome"*; `earl:NotTested` | W3C Recommendation ✅ verified |
| **XCCDF / NIST IR 7275** | `ERROR`, `UNKNOWN`, `NOT_CHECKED`, `NOT_APPLICABLE`, `NOT_SELECTED` | `xccdf_benchmark.h`, 3,443 ln |

**But every one of them throws it away at the aggregate.** That is the finding:

| Tool | What the score does with "could not measure" |
|---|---|
| OpenSSF Scorecard | **Dropped from the denominator** — 10 of 18 checks inconclusive can still score 10.0/10 |
| OHDSI DQD | `countPassed <- countTotal - countOverallFailed` → **rounds up to passed** |
| XCCDF / OpenSCAP | `ERROR` and `UNKNOWN` are *not* in the ignore list → **score 0.0, identical to FAIL** |
| Great Expectations | `successful = sum(exp.success or False ...)`; `unsuccessful = evaluated - successful` → **no third bucket; `None` coerces to failure** ✅ verified |
| Grafana | "No Data" is a real state — with a configurable **"Set Normal state"** handler that rounds it to healthy |
| pytest | `skipped`/`xfailed` exist and *"don't fail the test suite by default"* |

`factory/readiness.py:1176` computes `n_pass` over `len(results)` — an UNMEASURABLE gate **stays in
the denominator** and holds the board below all-pass. `factory/contract.py:73-85` ranks
`FAIL > UNMEASURABLE > PASS` and never collapses either.

> ### The claim that survives, and it is worth publishing
>
> **The representation problem is solved everywhere. The aggregation problem is solved nowhere.**
> `UNMEASURABLE` as a *state* is twenty years old and standardised. What is uncommon is that it must
> **survive aggregation as a refusal** — not dropped from the denominator (Scorecard, XCCDF), not
> counted as passed (OHDSI), not scored as failed (XCCDF, Great Expectations), and with no
> configuration path to defeat it (Grafana, pytest).

Two supporting notes, both verified:

- **Independent convergence, cite it as corroboration not competition.** Scorecard and `readiness.py`
  arrived separately at the *same two sources* of unmeasurability — an explicit "I checked and could
  not establish an instrument" (`CreateInconclusiveResult` / `raise Unmeasurable`) and a caught
  runtime exception (`CreateRuntimeErrorResult` / `except Exception → UNMEASURABLE`). Both refuse to
  let the second read as a failure.
- **The mechanism fires, it is not vestigial.** `claimant` named this as the hole in its own headline.
  Closed by the synthesiser: `checks/evaluation/code_review.go` (67 ln) contains
  `case finding.OutcomeNotApplicable: return checker.CreateInconclusiveResult(name, f.Message)`.

### The other three theses

| Thesis | Verdict | The evidence |
|---|---|---|
| **Evidence-basis at the API boundary** | **NARROWED** | The *vocabulary* is NIST prior art — OSCAL `Observation Method` = `EXAMINE / INTERVIEW / TEST / UNKNOWN`, with `Relevant Evidence` at **`min-occurs="0"` — optional**. OSCAL validates a finding with zero evidence; `tasks.py:129` raises. Surviving claim: *the basis label is standardised; enforcing it as a runtime precondition on a state transition is the contribution.* Nearest structural analogue is **Perl taint mode** (30 years old) — a provenance label that makes a privileged operation fatal until explicitly cleared. That is a *good* find: a proven mechanism in a new domain beats an invention. |
| **Mandatory negative controls per gate** | **NARROWED** | The technique is mature in three neighbouring fields — `promtool test rules` (feeds synthetic `input_series` to alert rules, asserts `exp_alerts`), **EICAR** (c.1991; its own page: *"like setting fire to the dustbin in your office to see whether the smoke detector is working"*), Atomic Red Team (last commit 2026-08-28). Uncommon part: making it a **per-gate shipping requirement for a delivery scorecard**. `NOT-FOUND`, not ABSENT — the scorecard-product category is partly behind sales calls. |
| **Spec-and-test as one artefact from a non-technical stakeholder** | ⛔ **PRIOR ART, AND TRIED-AND-FAILED** | This is BDD / Specification by Example verbatim. Cucumber's own creator, 2014: *"most of them completely missed out on the underlying practices such as Specification Workshops"*; teams write scenarios *"after the software"*, *"without any input from business analysts."* **Concordion** — the purest spec-document-is-the-test tool — last release **2023-07-16**, EXISTS-BUT-UNMAINTAINED. The tools that leaned hardest on stakeholder authorship are the dead ones. |

**⭐ The thesis-4 finding is a prediction, not a history.** BDD did not fail on format. It failed
because *the non-technical stakeholder does not fill it in* — an engineer fills it in afterwards and
the artefact degrades into a config file the client has never read but is nominally accountable for.
**If CIP-07 fails, that is how.** The one thing that differentiates it is already in the plan and must
be treated as critical path, not a nice-to-have: **pre-fill from a live schema probe so the client
confirms rather than authors.** BDD had nothing to pre-fill from. Restate the thesis as *"an
acceptance contract the stakeholder confirms rather than authors, pre-populated from a probe of their
live system"* — that version is defensible.

---

## 2. The ten verdicts

| # | Component | Verdict | One-line reason |
|---|---|---|---|
| 1 ⭐ | Data contract format | **ADAPT** | Take ODCS as the *artefact*; keep our validator. It cannot express A7/A8/A12 at all. |
| 2 ⭐ | Assertions over landed data | **BUILD** | A7/A8 are structurally inexpressible; GE fails K2 outright; 76 lines vs a 35 MB dependency. |
| 3 ⭐ | Readiness scorecard | **BUILD** | Category error — 0 of 27 gates are service-maturity shaped. Also the only market leader readable in source (OpsLevel) is binary. |
| 4 | Mutation testing of gates | **BUILD** | Both candidates are exit-code oracles; `mutmut` requires WSL. Cost inversion. |
| 5 | Durable work ledger | **BUILD** | Priced and closed. All three engines fail K1 on Windows/server. The failure mode they solve is one we don't have. |
| 6 ⭐ | Agent orchestration | **ADAPT** | Build the runner (~400 ln). Adopt the Claude Agent SDK as *transport only*. |
| 7 | Intake form → artefact | **ADAPT** | `datacontract edit` + `import --format snowflake` already ship CIP-09/10. Build only the client-language question layer. |
| 8 | Eval corpus + manifest hashing | **BUILD** | Category mismatch — those harnesses score model outputs; we replay connector fixtures. |
| 9 | Column-level lineage | **BUILD** | A thin client on the Power BI Scanner API + `sqlglot`. Every warehouse-native tool stops at the BI edge. |
| 10 | The composite | **BUILD — but publish the discipline, not the code** | Novel as assembled; each part is commodity. Cheap to replicate once described. |

**Plus one ADOPT nobody asked for, and it is the cleanest in the repo — see §3.**

### The detail that decides each one

**1 — Data contracts. ADAPT: take the format, keep the validator.**
ODCS (Apache-2.0, v3.1.0 2025-12-08) is now the consolidated standard — the older Data Contract
Specification carries a deprecation notice pointing at it, which removes fragmentation risk. Its
executor `datacontract-cli` (MIT, v1.1.2 2026-08-26) is real: it connects to Snowflake via
`ibis.snowflake.connect` and executes SQL. **But it cannot express our contract.** Grepping the full
2,929-line JSON Schema, `tenant` appears **once**, contract-level, `"type": "string"`, descriptive —
A12 has no first-class form. A7 (run attribution) and A8 (emitted == landed) have none either, and the
root is `additionalProperties: false` + `unevaluatedProperties: false`, so they go into an untyped
`customProperties` bag that nothing interprets. **A contract whose tenancy scope is an uninterpreted
string is not a contract.**
And the disqualifier for delegating judgement to it: `create_checks.py` (**673 lines** ✅ verified) has
**seven** `logger.warning(...) → return []` paths, and **does not import `Run` at all** — so a declared
rule that cannot compile emits zero checks, never reaches the structured result, and the run still
reports `passed`. *That is `bash-guard.sh` exiting 127, inside the candidate.*
→ **Adopt the artefact so the questionnaire edits a portable standard. Judge it ourselves.**

**2 — Assertions over landed data. BUILD.**
A7 is **ABSENT** across the category: every framework's "freshness" is `max(ts)` vs `now()` — recency,
which is the A6-shaped check our own `A6→A7` comment already calls insufficient. None can express
*rows carry this run's session id*. A8 is **structurally** absent — the emitted count lives on the
connector's side, not in the warehouse. A10 has one real candidate (GE's
`ExpectQueryResultsToMatchComparison`, a genuine second-instrument check Part 4 did not know existed),
but both instruments must be GE Data Sources and ours is an arbitrary API.
K2 kill, verified: GE's statistics are `unsuccessful = evaluated - successful` with
`successful = sum(exp.success or False ...)` — an expectation whose instrument crashed is counted as
*failing*, and `None` coerces into that bucket. No third bucket exists without an API change.
K4: our A7–A10 bodies are **76 lines** (`connector_contract.py:189-264`); GE's wheel is **35.1 MB** on
21 core deps incl. scipy/numpy/pandas. Soda Core is 0.2 MB and has the better verdict model — but is
**Elastic License 2.0**: *"You may not move, change, disable, or circumvent the license key
functionality."* Adopting an instrument you are contractually forbidden to modify, in a repo whose
thesis is that instruments must be provably able to fail, is self-defeating.
→ **Optional future seam:** delegate the *body* of `a9` to `pandera` (MIT, 0.8 MB) if the questionnaire
grows A9's vocabulary past ~5 invariant kinds. At 37 lines today it does not pay. **Don't take it yet.**

**3 — Readiness scorecard. BUILD, for a reason the framing did not anticipate.**
`grep -cE "^def g_" factory/readiness.py` → **27**. Zero are service-maturity checks. They ask things
like *"Has R2 been asked whether to move the build plane onto Prefect?"* and *"Does this work have a
ticket, or a decision that it needs none?"* This is a project's self-audit of its own open research
questions. Part 4 put Cortex/OpsLevel/Port/Soundcheck in this row on the strength of the word
"scorecard". Adopting one would delete no line and add an unrelated instrument.
Secondary finding, obtained without a sales call: **OpsLevel is binary.** Their published Go client
(`opslevel-go/enum.go`, 3,540 ln) has `CheckResultStatusEnum = failed | passed`. The market-leading
commercial service-maturity scorecard has two result states.

**4 — Mutation testing of gates. BUILD.**
`mutmut` README, verbatim: *"Mutmut must be run on a system with `fork` support. This means that if you
want to run on windows, you must run inside WSL."* ✅ verified — that is K1 verbatim.
Both `mutmut` and `cosmic-ray` judge a mutant by a test command's **exit code**. Our harness needs
strictly finer judgement and already has it — `mutate_readiness_probes.py:219`:
`ok = before == "PASS" and after == "FAIL"`, with a comment recording that `!= "PASS"` wrongly accepted
UNMEASURABLE and ERROR, because *"a control-plane gate must REFUSE, not merely fail to measure."*
**An exit-code oracle cannot express that.** This is a K2 failure in the component that exists to
protect K2. Migration would delete ~15 lines of harness and require rewriting the ~107-line curated
mutant table — where the actual findings are encoded — into generated mutants you cannot aim.

**5 — Durable work ledger. BUILD. Priced and closed; do not reopen.**
Restate ships **40 distribution files, 0 for Windows** (manylinux/musllinux/macosx only) — the hardest
K1 fail. Temporal needs a running Temporal Service. DBOS needs PostgreSQL — honest that there is *"no
additional infrastructure"* beyond it, but Postgres *is* the infrastructure, operated on one Windows
workstation for a 3-row ledger.
The deeper point: the failure mode durable execution exists to solve — replay a half-executed function
— **is one we do not have.** Crash mid-run is covered by `claims.task_holder` + on-disk `AttemptLedger`;
lane races by `claims._exclusive()`; torn writes by skip-unparseable-line. The one adjacent thing we
*do* want (resuming a half-finished agent run) is better served by the SDK's own `resume` /
`fork_session`, because the state worth resuming is the conversation, not our Python stack.
If concurrency ever does arrive, the next step is **`sqlite3` in WAL mode** — stdlib, zero deps,
ships on Windows — not Temporal. Nobody had priced that.

**6 — Agent orchestration. ADAPT — and the inherited recommendation is overturned.**
`boot-prompts/execution-plane-2026-08-30.md` says *"adopting a maintained runner gets the interface AND
the implementation."* **False for all six Part 4 candidates.** They cover **3 of 8** requirements;
worktree isolation, lane claiming, the persisted retry ledger, the event ledger and the verdict model
are ABSENT from every one — you build those either way.
Two are disqualified outright, both ✅ verified by the synthesiser:
- **AutoGen** README: *"AutoGen is now in maintenance mode. It will not receive new features or
  enhancements and is community managed going forward."* Part 4 lists it as a live lead. It is a corpse.
- **CrewAI**'s core abstraction *is* the topology R2 rejected — agents are `role`/`goal`/`backstory`;
  the hierarchical process *"automatically assigns a manager to the defined crew."*
  `blueprints/orchestrator_team.yaml` opens `⛔ SUPERSEDED BY EVIDENCE` on a 180-configuration study.
  It cannot be layered below `GreenContract` because it owns the control flow.
SWE-agent (v1.1.0, 2025-05-22) and Aider (v0.86.0, 2025-08-09) fail K3 on releases. LangGraph does not
force a topology but drags **`langsmith>=0.3.45,<1.0.0` as the first entry of `langchain-core`'s
mandatory `dependencies`** ✅ verified — a hosted telemetry client, by default, for three lanes.
**The arithmetic:** ~370–510 new lines hand-rolled, ~310–420 with the SDK, on top of **1,682 lines that
already exist and work**. Your "200-line runner" is optimistic by ~2× and is the right order of
magnitude. LangGraph alone costs 150–300 lines of event-model adaptation *plus* the framework.
**The one thing worth adopting is the Claude Agent SDK** (MIT, v0.2.148 2026-08-28) — and its cost is
*negative*, because `deploy.py:230-234` already hard-codes `--max-turns`, `--max-budget-usd`,
`--output-format stream-json`, `--model` against an **undocumented, unversioned, unpinned argv
surface**. Adopting the SDK does not add a vendor coupling; it makes an existing invisible one typed
and pinnable, with a `windows-latest` CI job. It has no verdict model to collapse, so it sits cleanly
below `GreenContract`.
*Open, cheap, worth doing first:* `deploy.py:98-110` records `limit=UNDETERMINED` on every non-zero exit
because *"the CLI gives us no documented signal distinguishing a cap-kill from a crash."* The SDK's
`ResultMessage` carries `stop_reason` and `terminal_reason`. If either enumerates budget exhaustion,
adopting it **converts a live UNDETERMINED in our own code into a measurement.** One run past
`max_budget_usd` settles it, ~$1.

**7 — Intake form. ADAPT — most of CIP-09/10 already exists.**
`datacontract edit <file>` starts a **local FastAPI/uvicorn server on 127.0.0.1:4243**, serves the
editor from assets **vendored into the pip package** (*"the editor works offline without any CDN
access"*), and **mounts `/test` on the same server** so the editor's Run-test button executes the
contract's checks against real declared servers. Editing the spec and running the acceptance test are
one UI over one file — the plan's load-bearing claim, already shipped.
`snowflake_importer.py` (576 ln) opens a live connection, queries `information_schema.table_privileges`,
and emits a populated contract — that is **CIP-09** ("clients confirm rather than type"). There are 32
importers including `powerbi_importer.py`.
**What is still BUILD, and it was always the hard part:** it is an engineer's editor over ~100 ODCS
fields, not a 20–30 question client questionnaire in business language. No auth, no per-client RLS —
`check_filename()` refuses every path but the one on the command line, bound to 127.0.0.1. CIP-12 and
CIP-13 are untouched.
⚠ Two checks before this touches a client: the editor ships an **AI Assistant** (docs say disabled by
default in the Docker image, requires `AI_ENDPOINT`/`AI_API_KEY`) — **NOT-VERIFIED for the bundled pip
build**; confirm it is off or contract content leaves the estate. And read `CUSTOMIZATION.md` first —
if the form can be cut to a business-language subset, the BUILD half shrinks to near zero. It is the
highest-value unread document in this area.
Part 4's own leads die: **Formbricks** needs PostgreSQL + Redis + a Next.js app under Docker Compose
(K1 FAIL) and is **AGPLv3** with a proprietary EE tier. `react-jsonschema-form`/JSONForms are React
rendering libraries — no hosting, no auth, and **neither pre-fills from a probe**, so the probe is our
code either way.

**8 — Eval corpus. BUILD. Different aisle entirely.**
Inspect, promptfoo, DeepEval, Ragas score **model outputs**. Our `evals.py` replays **connector
fixtures** through a contract and asserts a verdict; `mutate_and_expect_failure` asserts the contract
goes non-green when the world is broken. No model in the loop. On the discriminating question —
manifest hashing of a held-out corpus **verified at score time** — **NOT-FOUND** in any of them
(Inspect's 41 sha256 hits are Git-LFS pointer detection; promptfoo's 22 are cache identity).
Two off-list worth knowing: **vcrpy** (MIT, v8.3.0 2026-07-04) is the mature form of record/replay for
an HTTP connector — Part 4 looked in the wrong aisle entirely. **DVC** is the mature answer to pinning
a held-out corpus, but verifies on `pull`/`repro`, not inside `load()` at score time, and has no notion
of stamping the hash onto the verdict — take it *underneath* the corpus only if it moves to a repo the
agent cannot write, which `corpus.py`'s `$AGENT_FACTORY_EVALS` already permits at zero cost.

**9 — Lineage. BUILD a thin client. The brief's hypothesis was half right.**
Right half: warehouse-native tools stop at the warehouse edge. **OpenLineage is ABSENT at the BI
boundary** — all 11 `integration/` entries enumerated, no BI tool of any kind. dbt exposures are a
*declaration* — a human types which dashboard reads which model, which is exactly the inherited-target
failure our own rules forbid.
Wrong half: **DataHub and OpenMetadata do cross into Power BI** — DataHub ships an `m_query/`
subpackage that parses Power BI M/Mashup expressions to resolve which warehouse tables a semantic model
reads. Both need Kafka/ES/MySQL server stacks → K1 FAIL as platforms, though `acryl-datahub`'s
ingestion side is pip-installable and its m_query parser is the load-bearing piece.
**The off-list answer Part 4 missed entirely: the Power BI Scanner API** (`POST .../admin/workspaces/
getInfo`), which returns `datasetExpressions` (DAX and Mashup queries), `datasetSchema`, `lineage` and
`datasourceDetails`. That is the one instrument that can answer the question this estate keeps getting
wrong. Tier: **DOCUMENTED — nobody here has called it.**
⭐ **A K2 trap that is a design requirement, not a nicety:** Microsoft's own page states that
`datasetSchema`/`datasetExpressions` return data only if tenant metadata scanning is *fully enabled*.
**An empty response because the tenant setting is off is UNMEASURABLE, not "no lineage."** A client
built without that distinction will report "the dashboard reads nothing" and be believed.

**10 — The composite. Novel as assembled; publish the discipline, not the code.**
Nearest commercial neighbour is **Airbyte**, and it occupies the adjacent square precisely. Its support
levels are ownership/SLA labels — *"built and maintained by the Airbyte team"* — **no level's criteria
cite a measured runtime result**. 27 of its 29 QA checks are static/metadata. But its **Connector
Acceptance Tests** do require live credentials and a real read, and contain a genuine UNMEASURABLE
analogue: streams must all emit data **or be declared in `empty_streams` with bypass reasons required
at higher strictness**. Declare-and-justify-your-empty-window is the closest commercial thing to our
semantics — read their implementation before publishing.
**And the gap is where we stand:** Airbyte ships an **AI Assistant that generates connectors**, whose
docs require no live-run evidence before publish — *"you can run tests to ensure the setup is correct"*
and *"since it's an AI-based tool, you should still review the output."* **Optional tests plus human
review is exactly what this system exists to replace.** That sentence is the positioning.
Honest caveat: decomposed, (a) live-run evidence as certification input is commodity, (b) an
absence-of-instrument verdict is commodity, (c) refusing to let (b) be configured into a pass, inside
(a), proven by per-gate negative controls, is not found. The assembly is architectural, not technical —
**cheap to replicate once described.** The publishable asset is the discipline and the failure stories
behind each rule, not the implementation.

---

## 3. ⭐ The best ADOPT in the repo, and nobody was looking for it

**`claims.py:200-247` should be `tox-dev/filelock`.**

`filelock` — Unlicense, **zero transitive dependencies**, last release **3.32.4 on 2026-08-23** —
exists precisely to handle the Windows/POSIX divergence including timeouts and abandonment.

`grep -rn "filelock"` across this repo returns **nothing**. It appears in no code, no doc, no
`pyproject.toml`. **Part 4 has no "locking" row at all** — the sponsor's recall never generated the
category, so the search never ran. This is the direct answer to question 3 of the source document
(*"what am I about to build that already exists and I clearly do not know about?"*) — except it is
already built, and it is carrying a bug the author has already been bitten by. From `claims.py`'s own
comment:

> *"⚠ PermissionError, not just FileExistsError. On Windows, `O_CREAT|O_EXCL` against a file that
> another thread is concurrently deleting raises EACCES rather than EEXIST… **Twenty racing threads
> reproduce it every time; two rarely do.**"*

That is a bug report against hand-rolled locking, written by the person who hand-rolled it.
It adds one zero-dependency package, deletes ~48 lines, and **changes no verdict semantics whatsoever
— a lock is not a judgement**, so K2 does not apply. It passes K1/K2/K3/K4 without argument.

**Runner-up, larger and not recommended yet:** `scripts/local_tracker.py` is **2,554 lines** of
hand-rolled HTTP server, the largest file in the repo, and it *caused* the bug above — from
`claims.py:200-209`: the claim check-then-write *"was atomic only because `socketserver.TCPServer`
handled one request at a time — an accident of the transport… Threading the server on 2026-08-23
removed it, and `/start/<lane>` is a GET."* A GET that mutates state is something every mature web
framework's idiom prevents by default. Part 4 has no row for the tracker either. Flagged, not
recommended — it is a large change and §0 applies.

---

## 4. ⛔ Prerequisite for *any* adoption — this is not a follow-up

**There is no gate protecting the dependency surface, and today there is nothing to protect.**

```
pyproject.toml:6   dependencies = ["pyyaml>=6.0"]
```
<sub>Regenerate: `sed -n '1,12p' pyproject.toml`</sub>

Measured 2026-08-29: **no `uv.lock`, no `poetry.lock`, no `requirements.txt`, no `Pipfile.lock`, no
`constraints.txt`. No `.github/` directory at all — so no CI.** None of the 27 readiness gates measures
a dependency. `readiness.py:171` hand-parses YAML inside a probe rather than import it, because *"a
real YAML parse would pull a dependency into a probe that must keep working when the environment is
broken"* — the minimalism is deliberate policy, not accident.

The repo has a gate for a **corpus byte** changing (`corpus.py:89-96` raises `CorpusError` on hash
mismatch) and **no gate for its grader's dependencies changing.**

> **A minor-version release of an adopted tool that collapses a four-state model into three would land
> in this repo with nothing between it and `GreenContract`.**

And the systemic K1 risk that makes this urgent: of the starred candidates,
**datacontract-cli, Great Expectations, Soda Core, Dagster, LangGraph and CrewAI have zero Windows CI
between them — 0 of 68 workflow files.** Pure-Python packaging means they will *install*; it does not
mean a path-handling or subprocess bug would ever be caught upstream. **Any ADOPT on those means "we
are the Windows CI," as a standing cost.**

**The adapter tax, uncounted everywhere.** Every ADOPT is really adopt + adapter + version obligation.
`contract.py:52-58` converts *any* instrument exception to UNMEASURABLE — *"a crash is not a pass."*
Every adopted tool returns a boolean or boolean-plus-message, so each adapter must decide, for that
library's every failure mode, whether "no result" means FAIL or UNMEASURABLE. **Four ADOPT verdicts =
four new places where UNMEASURABLE can silently become FAIL**, and no test guards an adapter boundary
today because no adapter exists.

---

## 5. Tickets — every ADOPT/ADAPT verdict, with migration cost as acceptance criterion

✅ **LOADED into `.data/tasks.jsonl` 2026-08-29** via the `TaskStore` API (not hand-written JSONL),
after a shadow-copy dry run that showed 70 → 75 tickets with **zero status regressions**. Ledger
went 165 → 185 events. Rollback: `scratchpad/tasks.jsonl.backup-204818`.

⚠ **Three of the eight drafts below were NOT created, because they duplicate tickets that already
exist.** The prior external review was caught proposing two tickets for code that already existed;
this pass checked first. Those three became **evidence attached to the existing ticket** instead:

| Draft | Disposition | Existing ticket |
|---|---|---|
| `BVA-00` certify one connector | **not created** — duplicate | `CIP-05 - P1 Certify that connector A1-A12 against a recorded run` *(blocked)*, `task=1f220a7c`, +1 evidence promoting it to the gate on all adoption |
| `BVA-03` SDK-inside-a-hand-built-runner | **not created** — duplicate | `RUN-03 - R2 Execute a TeamSpec — the missing middle` *(open)*, `task=47113a09`, +2 evidence carrying the BUILD verdict and the line-by-line pricing |
| `BVA-05` rescope CIP-09/CIP-10 | **not created** — duplicate | `CIP-09` *(blocked)*, `task=711c9d13`, +1 · `CIP-10` *(blocked)*, `task=1108baa0`, +1 |

**Created (5):** `BVA-01` `771630bd` · `BVA-02` `377b70f0` · `BVA-04` `56546789` ·
`BVA-06` `c295ce8e` · `BVA-07` `cd2a7aa5` — each with an acceptance citation carrying its migration
cost and a note carrying its evidence, bases mixed `MEASURED`/`DERIVED` rather than blanket-OBSERVED.

The original eight drafts are retained below as the record of what was proposed.
**`CIP-05` and `BVA-01` gate the rest.**

```json
[
{"id":"BVA-00","phase":"P0","title":"Certify one connector end-to-end before actioning any adoption","why":"python -m factory.launch prints 'certified NOT_RUN — 12 assertions have no instrument wired'; live_probes wires only A1 and A5, both credential-free and network-free. Every migration cost below is priced against an interface that has never carried traffic.","depends_on":[],"acceptance":"python -m factory.certify against blueprints/windsorai_client_a.yaml returns a verdict other than NOT_RUN, with A2 and A7 instrumented against a live target; the run's basis is stated MEASURED not REPLAYED","evidence":"factory/live_probes.py:1-14; factory/connector_contract.py (10 _refuse sites); python -m factory.launch","effort":"L","tier":"OBSERVED","source":"prospect/devil 2026-08-29"},

{"id":"BVA-01","phase":"P0","title":"Add g_dependencies_are_pinned — a lockfile gate, prerequisite to any ADOPT","why":"dependencies = ['pyyaml>=6.0'] with no lockfile, no CI and no gate among the 27. An adopted tool's minor release could collapse a four-state model with nothing between it and GreenContract. The repo gates a corpus byte changing and not its grader's dependencies.","depends_on":[],"acceptance":"A lockfile exists and is current; readiness shows dependencies-pinned PASS; a test asserts the verdict enum of every adopted judgement library and FAILS when a member is removed (negative control required)","evidence":"pyproject.toml:6; ls uv.lock poetry.lock requirements.txt -> absent; ls .github -> absent; grep -cE '^def g_' factory/readiness.py -> 27","effort":"S","tier":"OBSERVED","source":"prospect/devil 2026-08-29"},

{"id":"BVA-02","phase":"P1","title":"Adopt tox-dev/filelock in claims.py, delete the hand-rolled _exclusive()","why":"Unlicense, zero transitive deps, last release 3.32.4 on 2026-08-23, exists to handle exactly the Windows EACCES-vs-EEXIST race claims.py:225 documents having been bitten by. A lock is not a judgement, so K2 does not apply. filelock appears nowhere in this repo; Part 4 has no locking row.","depends_on":["BVA-01"],"acceptance":"claims.py:200-247 (~48 lines) deleted in favour of filelock; the 20-concurrent-thread race test still passes on Windows; no change to any verdict; migration cost recorded as lines deleted vs lines added","evidence":"factory/claims.py:200-247; grep -rn filelock . -> no hits; api.github.com/repos/tox-dev/filelock/releases/latest","effort":"S","tier":"OBSERVED","source":"prospect/devil 2026-08-29"},

{"id":"BVA-03","phase":"P1","title":"Adopt the Claude Agent SDK as transport inside a hand-built RunController","why":"deploy.py:230-234 already hard-codes --max-turns/--max-budget-usd/--output-format stream-json against an undocumented unpinned argv surface. The SDK (MIT, v0.2.148 2026-08-28, windows-latest CI) makes that coupling typed and pinnable and has no verdict model to collapse. The six Part 4 frameworks cover 3 of 8 requirements; AutoGen is in maintenance mode and CrewAI's core abstraction is the topology R2 rejected.","depends_on":["BVA-00","BVA-01"],"acceptance":"A vertical slice task -> RunController -> SDK -> worktree -> recorded events -> GreenContract verdict, with a fake provider driven identically in a test; SDK pinned exactly; migration cost recorded as ~40-60 lines rewritten in deploy.py:229-265 against ~370-510 lines of new runner code","evidence":"factory/deploy.py:98-110,229-265; api.github.com/repos/anthropics/claude-agent-sdk-python/releases/latest; microsoft/autogen README maintenance banner; crewAIInc/crewAI README","effort":"L","tier":"OBSERVED","source":"prospect/scout-orchestration 2026-08-29"},

{"id":"BVA-04","phase":"P2","title":"Reshape ConnectorTarget onto ODCS as the contract artefact, keeping our validator","why":"ODCS (Apache-2.0, v3.1.0) is the consolidated standard — the older Data Contract Specification carries a deprecation notice pointing at it. Adopting the format makes the questionnaire an editor for a portable artefact. But ODCS cannot express A7, A8 or A12 (tenant appears once in 2,929 lines of JSON Schema, contract-level, descriptive), and datacontract-cli silently drops uncompilable rules, so judgement stays ours.","depends_on":["BVA-00"],"acceptance":"ConnectorTarget's 22 fields map to ODCS fields or to a documented customProperties extension, field by field; factory/contract.py unchanged; a negative control proves a rule that fails to compile is REFUSED rather than reported passed; migration cost recorded as the field-mapping table","evidence":"factory/connector_contract.py:26-58; ODCS schema/odcs-json-schema-latest.json (2,929 ln, 1 tenant hit at line 31); datacontract-cli create_checks.py (673 ln, 7 logger.warning->return [] paths, no Run import)","effort":"M","tier":"OBSERVED","source":"prospect/scout-contracts 2026-08-29"},

{"id":"BVA-05","phase":"P2","title":"Rescope CIP-09/CIP-10 onto datacontract edit + import --format snowflake","why":"datacontract edit already serves a local offline FastAPI editor on 127.0.0.1:4243 and mounts /test on the same server — spec and acceptance test as one artefact, shipped. snowflake_importer.py (576 ln) already emits a pre-filled contract from information_schema, which is CIP-09. What remains is the business-language question layer, which was always the hard part.","depends_on":["BVA-04"],"acceptance":"CIP-09/CIP-10 rescoped in the plan with the delta stated; CUSTOMIZATION.md read and the answer recorded on whether the form can be cut to a 20-30 question business-language subset; the editor's AI Assistant proven OFF in the bundled pip build before any client contract touches it; migration cost recorded as unwritten-work displaced","evidence":"datacontract-cli command_edit.py (382 ln); imports/snowflake_importer.py (576 ln); docs/CLIENT-INTAKE-PLATFORM-PLAN.md:253-256","effort":"M","tier":"OBSERVED","source":"prospect/scout-contracts 2026-08-29"},

{"id":"BVA-06","phase":"P2","title":"One adapter contract + a mutation-tested battery for every adopted boundary","why":"contract.py:52-58 converts any instrument exception to UNMEASURABLE. Every adopted tool returns a boolean. Each adapter must decide, per failure mode, whether no-result means FAIL or UNMEASURABLE — four adoptions is four new places UNMEASURABLE can silently become FAIL, and no test guards an adapter boundary today. Uniform precedence is the product; component-by-component adoption can be individually rational and collectively destroy it.","depends_on":["BVA-02","BVA-03","BVA-04"],"acceptance":"A single adapter contract exists; one test battery proves every adapter maps instrument-absent to UNMEASURABLE and not FAIL; each mapping is mutation-tested via mutate_and_expect_failure; the battery FAILS when an adapter is broken","evidence":"factory/contract.py:52-58,73-85; no adapter exists today","effort":"M","tier":"DERIVED","source":"prospect/devil 2026-08-29"},

{"id":"BVA-07","phase":"P3","title":"Retitle the public write-up: UNMEASURABLE must survive aggregation","why":"The claim as drafted ('I do not recall seeing UNMEASURABLE as a first-class feature in any scorecard or data-quality product') is falsifiable in four minutes by opening ossf/scorecard checker/check_result.go. Six tools and standards have the state. None keeps it through the score: Scorecard drops it from the denominator, OHDSI rounds it up to passed, XCCDF and GE score it as failed, Grafana ships a switch to call it healthy, pytest greens it by default.","depends_on":[],"acceptance":"The write-up claims only that UNMEASURABLE must survive aggregation as a refusal — not dropped, not passed, not failed, with no config path to defeat it — and cites Scorecard, OHDSI summarizeResults.R, XCCDF result_scoring.c and GE expectation_validation_result.py as the contrast set","evidence":"ossf/scorecard checker/check_result.go:336; OHDSI summarizeResults.R (83 ln); openscap result_scoring.c:81-98; GE expectation_validation_result.py (846 ln); W3C EARL10-Schema","effort":"S","tier":"OBSERVED","source":"prospect/claimant + scholar 2026-08-29"}
]
```

---

## 6. Corrections to the source document — publish these wherever it has been quoted

Per the estate rule that *correcting an inherited premise is a deliverable*:

| # | Claim in `BUILD-VS-ADOPT-PROMPT.md` | Correction |
|---|---|---|
| 1 | *"I do not recall seeing UNMEASURABLE as a first-class feature in any scorecard or data-quality product"* | **Wrong.** It is first-class in OpenSSF Scorecard (a scorecard product), Soda Core and datacontract-cli (data-quality products), and XCCDF (an ISO/NIST standard). The narrowed claim in §1 survives all of them. |
| 2 | Part 4 lists **AutoGen** as a live lead | **Maintenance mode**, redirects to Microsoft Agent Framework. TRIED-AND-FAILED, and it reads exactly like good news. |
| 3 | Part 4: *"Agent orchestration… cheapest place to adopt"* | **Overturned.** The frameworks cover 3 of 8 requirements. Cheapest place to adopt is **locking** (`filelock`), a category Part 4 has no row for. |
| 4 | Part 4 lists **Schemata** as a data-contract lead | **EXISTS-BUT-UNMAINTAINED** — last release v0.3, 2023-05-08. K3 fail by three years. |
| 5 | Part 4 lists **dbt-expectations** and **deepchecks** | Both **EXISTS-BUT-UNMAINTAINED** — 2024-09-10 and 2024-12-15 respectively. |
| 6 | Part 4: intake forms → **Formbricks** | K1 FAIL (Postgres + Redis + Next.js under Docker Compose) and AGPLv3 with a proprietary EE tier. |
| 7 | Measured size table (`factory/` 8,886 · `tests/` 3,873 · `docs/` 54,232 across 89) | **All four stale on the day written.** Measured at `17a6a5a`: `factory/` **9,227** across 40 files · `tests/` **4,684** across 31 · `docs/` **56,125** across 93. |
| 8 | *"304 tests passing"* (repeated across boot prompts) | **Three different numbers, none reproducible without its condition.** 301 `def test_` definitions, **388 passed / 21 failed / 2 xfailed** on execution today, 304 from an unrecorded sibling-repo state. The suite is currently **RED**. |
| 9 | `local_tracker.py` at 2,470 lines | **2,554** today. |
| 10 | My own brief §5(b), circulated to the council | **Wrong** — I wrote that Scorecard had "no `-1`-style discrete value". `InconclusiveResultScore = -1` is a named exported constant with two dedicated constructors and special handling in both the aggregate and the renderer. I read a docs page where the answer was in source. Recorded because it is the exact failure this pass exists to prevent. |
| 11 | My own brief §5(a) | **Wrong hedge** — OHDSI's `Not Applicable` triggers are `tableIsMissing` / `tableIsEmpty` (`numDenominatorRows == 0`) / `fieldIsEmpty`: availability, i.e. our empty-window rule. OHDSI fails for a better reason — arithmetic, not semantics. |
| 12 | `docs/reviews/external/verification.md:43` — *"deploy.py / tasks.py / metrics.py / evals.py have no live callers"* | **Now stale for `tasks.py`.** `TaskStore` is imported by `scripts/export_board.py:16` and `scripts/local_tracker.py:827`. Do not price bet 5 as replacing dead code. |

---

## 7. Kill-shots — status, in the headline not the appendix

| # | Kill-shot | Status |
|---|---|---|
| 1 | **Nothing has ever been certified; 12 assertions uninstrumented** | ⛔ **UNANSWERED.** It is the §0 sequencing constraint and it gates every ADOPT here. |
| 2 | **No gate protects the dependency surface** | ⛔ **UNANSWERED** — converted to `BVA-01` as a prerequisite. |
| 3 | The adapter tax is uncounted | **PARTIALLY ANSWERED** — converted to `BVA-06`; the cost is real and now visible, not eliminated. |
| 4 | Component-by-component scoring cannot see the composite | **PARTIALLY ANSWERED** by `BVA-06`; the risk stands wherever adoptions land in different sessions. |
| 5 | Opportunity cost — an adoption programme is one of three lanes | ⛔ **UNANSWERED.** `RUN-01…04` are all open with `cap`/`ceiling`/`concurrency`/`reaper`/`bounded` all FAIL; CIP-07 is on the critical path and open; **the ledger holds 71 tasks with 5 closed and 18 blocked.** This project's binding constraint is finishing things, not choosing components. |
| 6 | The repo maintains code with no callers and calls it a platform | **ANSWERED IN PART** — true for `RepoDeployer` and `EvalSuite`, **false for `tasks.py`** (correction 12). |

**Arguments `devil` dropped on contact with evidence, recorded so the strong ones aren't discounted
with them:** the "304 tests all break" argument (only ~113 of 301 touch verdict semantics); and the
maintenance argument for BUILD — **K3 kills almost nothing here**; the live candidates are nearly all
released within weeks. Where BUILD wins it wins on platform, licence, verdict semantics or arithmetic,
never on the incumbent being dead.

---

## 8. Instrument log — what could and could not be seen

Per the rule that a zero from an instrument you have not proved can see is not a measurement.

| Instrument | Status | Proof |
|---|---|---|
| `WebFetch` → `raw.githubusercontent.com` | **WORKS** | Verbatim enum text returned repeatedly |
| `WebFetch` → `api.github.com` | **WORKS, then rate-limits** | Clean data, then HTTP 403 after ~8 calls unauthenticated |
| `WebFetch` negative control | **PASSES** | A nonexistent repo path returns a clean 404 |
| `gh api` (authenticated, `russell94paul`) | **WORKS** | `repos/ossf/scorecard/contents/checks/evaluation` → 39 entries |
| ⛔ `gh api search/code` / `gh search code` | **BLIND — do not trust its zeros** | Positive control: searching `InconclusiveResultScore repo:ossf/scorecard` returned **0** for a string verified to exist. The token is a `gho_` OAuth token without code-search scope. **Every code-search zero in this pass is NOT-VISIBLE, not ABSENT.** |
| ⚠ `WebSearch` | **NOISY — never a finding** | One probe confused "Great Expectations" the DQ library with **a dating service** and reported its complaints. Used as lead generation only; no finding here rests on it. |
| ⚠ `WebFetch` as a *source-reading* instrument | **DOCUMENTED-tier, not OBSERVED** | It returns a small model's summary. `claimant` found it gave a materially incomplete read of OHDSI's `summarizeResults.R` that `curl` + `cat` settled as fact. **Recommendation for the next pass: mandate `curl`/`gh` for any claim that will carry a verdict.** |

**Line-count divergences between synthesiser and lenses** — substance agreed every time, references did
not. Almost certainly different refs (`main` vs `develop` vs a pinned tag). Published numbers are the
synthesiser's own, fetched from the ref named: `create_checks.py` 673 (lens said 996) · Dagster
`asset_check_execution_record.py` 334 (286) · GE `expectation_validation_result.py` 846 (766/1,087).
**Any of these quoted downstream must carry its ref.**

**BLOCKED ON ACCESS — named, not assumed empty:**

| Fact | What would settle it |
|---|---|
| **Cortex** and **Port** result-state enums | A trial account + one scorecard-scores API response. ABSENT from public source, not from the product. |
| **Backstage + Soundcheck** check states | A Spotify Plugins licence. |
| **Soda Cloud** reconciliation checks; whether `soda-core` v4 runs fully keyless | A Soda Cloud account. This one matters — keyless Soda at 0.2 MB with a five-member `CheckOutcome` would be the most interesting adopt in the field. |
| **dbt** test status enum | `dbt-core@main` is now the Rust "Fusion" engine; the Python `TestStatus` enum is no longer at the documented path. ~30 min in `crates/dbt-schemas/`. **A live migration under a candidate, and not in Part 4.** |
| Whether anyone runs GE / Soda / Dagster / LangChain **on bare Windows in anger** | UNSEARCHABLE — private Slack/Discord. |
| `ResultMessage.stop_reason` / `terminal_reason` values | One SDK run past `max_budget_usd`, ~$1. Would convert a live `UNDETERMINED` in `deploy.py` into a measurement. |
| Power BI Scanner API returning populated `datasetExpressions` for a real GEP workspace | A Fabric admin or service principal with `Tenant.Read.All`, **plus tenant metadata scanning confirmed ON**. Highest-value single next action for component 9. |

**`scholar`'s refusal list** (a method that never refused anything had no bar): all WebSearch prose;
`verdict.systems` (MARKETED — landing page, pricing, no repo, no docs); `aiagentcertify.com` (not
fetched, deliberate skip); its own prior about SARIF `open`/`review` semantics (spec fetch truncated —
reported NOT-FOUND rather than written from memory); and all claims about ISO/IEC GUM, MCAR/MAR/MNAR
and medical indeterminate results — **the conceptual-literature lane is only ~half searched**, omitted
rather than asserted.

---

## 9. What was NOT done

- ~~No tickets were written~~ ✅ **Done 2026-08-29** — 5 created, 4 existing tickets given evidence.
  See §5 for the disposition table and the three drafts that were duplicates.
- **Nothing committed.** `docs/research/SYNTHESIS.md` remains dirty from the reconciliation session
  and `docs/specs/golden-workflow-fit.md` plus four `factory/`/`tests/` files are another session's
  untracked work — all untouched. Stage by exact path.
- **Nothing installed, no vendor contacted, no account created, no terms agreed.**
- **No candidate was executed.** Every verdict rests on reading source, packaging metadata, CI
  matrices and release APIs. The two highest-value executions, both cheap, are named in §8.
