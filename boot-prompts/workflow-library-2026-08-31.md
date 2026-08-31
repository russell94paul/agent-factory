# Workflow library — shape × layer, and the marketing model that is still blocked

**Written 2026-08-31, extended the same day with §3a-c after Paul directed the team experiment.**
Supersedes nothing. Runs alongside `run-03-the-missing-middle` (that thread
is DONE and committed by a concurrent session — see §5).

`next:` **run `keel` on the GEP/Navira marketing model as an INSTRUMENTED experiment** the moment
Paul's artifacts land. Everything upstream is built and green.

⭐ **The run is two deliverables, not one.** The client design is the visible half; the other is the
first recorded arm of a comparison this estate has never been able to make. **Do §3a's five setup
steps before spawning anything** — they are cheap, they are unrecoverable afterwards, and skipping
them turns the experiment into a demonstration. Nothing else in this file is on the critical path.

---

## 0. What this session was asked for, and what it actually established

Paul asked for a library of reusable agentic workflows keyed by repo/domain/client/bug/review, a
review of `agent-factory` and `agent-army-research`, and a call on deep research.

⭐ **The finding that reframed it: you already had three workflow layers and they did not know about
each other.** `MEASURED` — `grep -rn "inquest\|conclave\|assay\|vigil\|prospect" factory/ blueprints/
scripts/` returned **nothing**.

| Layer | What | State |
|---|---|---|
| repo-keyed stage machines | `~/.claude/commands/gep-feature.md` (1,925 ln), `prefect-connector.md` (826) | working; durable state in `clients/GEP/tickets/<t>/artifact.yaml` |
| shape-keyed councils | `inquest` `conclave` `assay` `vigil` `prospect` `army` `deep-research` | 31 invocable skills, one with MEASURED evidence on a real ticket (GP-311) |
| ticket-type presets | `factory/presets.py` | now 6 types, 2 verifiers WIRED |

**The design chosen (Paul's call): key on `shape × layer`.** Shape decides the method, layer decides
the verifier/deploy path/rollback. **Client is a context pack, not a key** — the same defect shape
recurs across clients, and keying on client would duplicate every workflow ~19 times.

## 1. Three corrected premises — do not re-derive these

1. **The taxonomy was already done.** `docs/research/answers/R19-answer-work-taxonomy-and-team-selection.md`
   swept all 59 wiki ticket pages → 16 types with dispositions. Re-measured 2026-08-30 and **exact**.
   An independent wiki sweep produced 9 archetypes that map cleanly onto the same 16.
2. ⛔ **`golden-workflow-fit.md` said the Job object was MISSING. It is not** — `artifact.yaml` binds
   ticket → stage_history → per-layer changes → deploy_history → decisions, in production, two live
   instances. What it lacks is an evidence *class* and a *verdict*. Row corrected on disk.
3. ⛔ **Agent Army's founding premise was already falsified by its own Wave 0**
   (`agent-army-research/research/synthesis/W0-foundations.md`) — AOE is organisation-oriented MAS;
   the category name is taken twice in 2026; the novelty claim is refuted on all four components.
   **Recommendation: stop investing there.** 27 of 30 prompts `NOT_RUN`; leave them. That research
   already paid for itself — finding C4 became the fifth verdict, commit `0d4bdb1`.

## 2. What shipped

| | |
|---|---|
| `~/.claude/skills/keel/` | **NEW council — the `design` shape.** Gates: the ask verbatim → the consumer route walked → **the grain declaration written to a file before any design work**. Lenses `surveyor / cartographer / assayer / answerer / lexicographer / devil`, each bought with a measured GP-318/319 defect. Verdicts `MEASURED / DERIVED / NOT-REPORTED / SENTINEL`. Ships a `references/` brief template. |
| `factory/registry.py` | Joins councils ↔ factory. `(shape, layer) → workflow`, versioned by `SKILL.md` content hash. 21 tests. Honestly reports 4 of 9 never run on real work. |
| `factory/presets.py` | `model-design` row added, `verifier_state=AVAILABLE` citing `redesign_contract.R3`. |
| `wiki/scripts/wiki_lint.py` | The lint `CLAUDE.md` §Lint always specified and which had run **once in 193 operations**. Self-testing, refuses to report when blinded. |
| `wiki/concepts/architecture/cross-channel-marketing-dimensional-model.md` | 498 lines of graded external evidence for the marketing design. Committed `b19bfac`. |
| corrections | five verdicts in 3 live docs; stale Agent Army counts; the Job-object row; `army` + `eclipse-app` frontmatter (both were untriggerable — H1 used as trigger). |

## 3. ⭐ The next session's actual job

**Run `keel` on the GEP/Navira marketing model.** Blocked only on Paul's artifacts (Excel field list,
the UI prototype, emails, Avoma summaries — he said he would copy them into the repo).

**Read these six first. They exist and are graded — do not re-research:**
1. `wiki/concepts/architecture/cross-channel-marketing-attribution.md` — the tiered law, locked decisions
2. `wiki/concepts/architecture/cross-channel-marketing-dimensional-model.md` — the external evidence
3. `aldc-launchpad/docs/readouts/gp319-marketing-model-designs.html` — three designs, the core-10
4. `wiki/tickets/gep/GP-319.md` + `GP-318.md` — the defect ledger
5. `clients/FUSION_92/snowflake/warehouse/fct_daily_spend.sql` + `shared_dim_flight.sql` — a working
   cross-channel star over 11 platforms (Navira ingests 3). Closest analogue in the estate.
6. `navira-marketing-dashboard/docs/FIELDS.md` + `src/lib/metrics.ts` — **the exact field contract
   the surface the client likes needs the model to fill**

⚠ **Paul's correction, and it inverts the obvious assumption:** the marketing dashboard reads
**Snowflake directly**; the **Eclipse app** reads PBI. The disliked PBI model and the liked frontend
do not share a data path. Walk it again anyway — that is `keel` Gate 2.

**Honour, do not re-litigate:** GP-319 declared `MARKETING_FCT_ACTIVITY_UNIFIED` canonical and
rebuilt the measure layer on it; a conformed core fact was REJECTED (a 15th copy) and a long/narrow
key-value fact was REJECTED (*the defect is naming*). Metric hierarchy: **Contribution Margin > MER
(blended) > Platform ROAS**, and Platform ROAS is never summed across channels.

**Posture: greenfield alongside.** New objects, nothing live moves until sign-off. Gives an A/B for a
client who is not sure what they want.

**Two human decisions `keel` must surface, not settle:** which ROAS is canonical, and sign-off on
names. Both already open in GP-319.

### ⚠ If the artifacts have not landed, do NOT wait — swap the subject

Paul challenged this on 2026-08-31, correctly: *"I thought we were building agent factory, what has
the marketing model got to do with it?"* The answer is that he nominated it as the first subject when
asked which workflow to build first, and it is client work he needs anyway — so the validation run is
free. **It is the SUBJECT, not the project.** Everything in §2 was built for the factory and none of
it is marketing work.

But `keel` must run on *something* real. `registry.unproven()` prints `4 of 9 have never been run on
real work`, and a council that has never run is **written-and-unwired — the exact defect this repo
exists to catch, with three independent instances already on record.** Running it is what stops it
being decoration.

So if the artifacts are not there, take an internal subject instead and lose nothing:

| fallback subject | why it works | available |
|---|---|---|
| **`agent-factory`'s own board schema** | 76 tasks in `.data/tasks.jsonl` with no lifecycle worth the name — a real grain-and-status design question | now |
| **the wiki's missing `status:` field** | the 2026-08-31 council established the question (`live \| archive \| stale \| abandoned \| superseded-by`); `keel` would produce the schema | now |
| **decline, and leave `keel` DECLARED** | defensible — the registry keeps saying 4 of 9 unproven, which is true and visible | — |

⛔ **What is NOT acceptable is running `keel` on a toy.** A council validated against something with
no consequence tells you the prompt parses, not that the method works.

## 3a. ⭐ Run it as an INSTRUMENTED experiment, not a demonstration

Paul's direction: build a small specialised team, direct the right context to each member, and find
out whether it is more efficient. **The `keel` run is that experiment.** It is real work you need
anyway, so the team is not a toy — but the difference between an experiment and a demonstration is
entirely in what you set up *before* spawning.

### ⛔ Do these five before any agent starts

**1. Write the falsifiable prediction first, to a file.**
In one sentence: *what will the team find that a solo run would miss?* Then check it afterwards and
record whether you were right. `MEASURED 2026-08-30` — the honest prediction for the wiki council
would have been *"it will correct my own numbers"*, and it did, **four times**. Without the
prediction written first, a team always looks worth it afterwards, because you only ever see what it
found and never what a solo run would also have found.

**2. Verify the brief before spawning. One cheap agent, ~2 minutes.**
Its only job: re-run every number in the brief with a positive control. ⛔ **The brief is
simultaneously the highest-leverage artifact and the single largest correlated-error source.** On
2026-08-30 a wrong baseline (37% orphaned, 532 broken links) reached all five lenses at once; two
burned effort re-deriving it before the correction landed. The true figures were 9% and ~38.
Put **raw command output** in the brief, never the synthesiser's summary of it.

**3. Four lenses, not six. Size to independent work units, never to ambition.**
`army`'s own rule. For `keel` on the marketing model, collapse `answerer` and `lexicographer` for the
first pass — both read the same artefact, and the second only sharpens the first.

**4. Tier the models. The 2026-08-30 run overspent by an estimated 2–3x.**

| lens | model | why |
|---|---|---|
| `surveyor` (grain) | **opus** | the decision that cannot be undone later |
| `devil` (numbers against the design) | **opus** | it killed the premise last time; pay for it |
| `assayer` (coverage %) | **sonnet** | measurement against real rows, mechanical once scoped |
| `cartographer` (conformance) | **sonnet** | cardinality and key checks are queries |

⭐ The lesson from the wiki council: **behaviour beat structure.** The two lenses that changed the
verdict ran empirical trials and measured cost. The two that measured structure produced excellent
data that moved nothing. Weight the team toward *testing what happens*, not *describing what is*.

**5. Direct context by POINTER SET, not prose — this is the actual experiment.**
Today every lens got one shared brief plus a paragraph. Instead: the brief carries only shared
invariants (raw gate output, the constraints, the read-only rule), and **each lens receives the
specific files and commands its link owns.**

`factory/context.py` was built for exactly this — `ContextPack.of_kind()` — and **has never had a
real caller.** Wiring it here validates the schema against one real client workflow, which is the
precondition its own docstring names for building any wiki→pack pipeline. That makes this run worth
more than its own output.

---

## 3b. Continuous improvement — the ledger, and what "success" is allowed to mean

⛔ **Efficiency claims are currently unfalsifiable, because no baseline exists.** R19's central
finding applies directly: *the optimiser is not the missing piece — the logging schema is.* A team
run that records nothing produces a feeling, not a measurement, and the fields are **missing at
write time and unrecoverable afterwards.**

### Record per lens, at dispatch

`shape` · `layer` · `lens` · `model` · `effort` · `turns` · `cost` · `context_kinds[]` (which
`ContextPack` kinds it was handed) · `findings[]` · **`survived_verification`** · `human_acted` ·
`refusals[]` (what it declined to measure, and the access it named).

### ⛔ The definition of success, and the ones that are forbidden

| | |
|---|---|
| **NOT success** | the agent finished · it exited 0 · it produced a report · it found N things |
| **success** | a finding **survived adversarial verification** AND a human **acted on it** |

This is not pedantry. This estate retired an agent with **233 diagnoses, 234 escalations and 0
fixes** over 81 days, and a loop that ran **965 times, recorded its own 1.6% success rate, and never
adjusted.** Both were capable. Neither was measurable. `factory/metrics.py` already raises
`GoodhartViolation` on an activity metric with no paired outcome — **the ledger must inherit that
refusal, not merely display its result.**

### Seed the baseline from 2026-08-30, retrospectively

The wiki council is a usable first data point and costs nothing to record now: 5 lenses, all opus,
~12 major findings, **4 of which corrected the synthesiser and survived**, premise refuted and the
recommendation changed as a result. That is one arm. The `keel` run is the second, and two arms
carrying the same record are the first honest comparison this estate will have had.

⚠ Honest caution to carry: the wiki council produced ~30k words to support *"don't do it, write four
pages."* The synthesis burden fell entirely on the orchestrator and was heavy. **For a narrower
question that is a bad trade** — the cost valve matters as much as the method.

---

## 3c. The pattern flagger — and the one thing that decides whether it is worth building

Paul wants a mechanism that identifies recurring process patterns in agentic runs and flags them.
The detection is the easy half. **The pairing is the whole design.**

### What it detects, all from artifacts the run already produces

| signal | what it means | example from 2026-08-30 |
|---|---|---|
| **correction** | an agent overturned a synthesiser claim | 4 of them — the baseline, the denominator, the "lost" lane, the filter choice |
| **convergence** | ≥2 lenses independently reach the same finding | librarian + cartographer + retriever all found the 152 `sources/` inflation → **candidate for a deterministic check instead of an agent** |
| **rework** | the same command re-derived by ≥2 lenses | an alias-aware resolver, built three separate times → **belongs in the brief template** |
| **refusal** | a lens returned *"unmeasurable — needs X"* | "no Jira access" → a capability gap, not a failure |
| **dud** | a lens whose findings did not survive verification | → wrong model tier, or a lens duplicating another |

### ⛔ Emission without acceptance is the 234/0 signature in a new costume

**Every flag carries `accepted | declined | pending`, and the flagger reports its own acceptance
rate.** Where the acceptance rate is unknown it reports `UNMEASURABLE` — never *"N patterns
identified"*, which is an activity metric wearing an outcome's clothes.

This is not hypothetical. **Every promotion mechanism in this estate has a firing rate of zero:**
`potential-tickets.md` 15 in / 0 out over four months · `action-items.md` has never moved a single
item Open→Done in its entire life · FU92-420's explicitly-generalisable lessons still trapped in a
ticket body · 47 of 52 trackers stale inside `active/` · the wiki `lint` run **once in 193
operations**. ⭐ **A flagger that only emits will join that graveyard within a month. Build the
acceptance half first, or do not build it.**

### Precondition, stated plainly

**The dispatch record (§3b) must exist before the flagger.** A flagger over a run that recorded
nothing is inferring patterns from prose. Sequence: **record → run twice → then detect.** Anything
presented as pattern detection before two recorded arms is `SPECULATIVE` — R19 says exactly this
about its own selector, for the same reason.

## 4. Open threads, ranked

1. **Marketing artifacts** — the only blocker on the critical path.
2. **`potential-tickets.md` holds two live security items** — an expired Azure AD client secret
   logged 2026-07-24, and a committed `CORE_API_CLIENT_TOKEN` in GEP PBIX files. Untriaged four
   months. **Highest time-sensitivity of anything found this session, and unrelated to any of it.**
3. **Nothing is committed** in either repo. `cross-channel-marketing-dimensional-model.md` is linked
   from `index.md` and untracked — any clone loses it and breaks that link.
4. **Wiki: 4 pages + `status:`** — `status:` first (zero blast radius, unblocks the rest), then
   `GP-293` (42 refs, never written), `confirm-consumer-source` (4 refs, cited from the flagship
   runbook at the evidence gate), `transaction_currency_handling` (cited from `star-schema-convention`),
   Fusion92 deployment runbook.
5. **The warehouse-framework research** — brief written at `docs/research/warehouse-framework-brief.md`,
   not run. Paul wants it as a diagrammed technical design doc.
6. **North star logged** to project memory with three constraints. First falsifiable milestone: the
   unblock queue (`R14 §0.6` independently reached the same conclusion).

## 5. Gotchas earned — these cost real time

- ⛔ **A concurrent session is committing to BOTH repos.** It landed 8 commits in `agent-factory`
  during this session (including `redesign_contract.py`) and has `log.md` +
  `entities/projects/agent-factory.md` + `vacuous-verification.md` open in the wiki. **The git index
  is shared.** Check `git log --oneline -5` before assuming anything about HEAD.
- ⛔ **`presets.py` moved under me** — `ui-control` went WIRED→available, `add-measure` and
  `model-redesign` went →wired. Re-read before quoting a verifier state.
- ⭐ **Every uncontrolled count in this session was wrong by a plausible amount.** Broken links
  `1,146 → 38`; orphans `37% → 9%`; denominator `491 → 335 → 331`. **Run a positive control before
  quoting any number**, and for a negative claim prove the instrument can return a positive.
- **Syntax must be validated before resolution** — a permissive normaliser rescued 16 of 17
  malformed links and reported them green.
- **Never aggregate freshness by directory `max()`**; filter mechanical edits by per-file line count,
  never files-per-commit.
- `python -m factory.launch` takes ~9 minutes and prints nothing until done — use `python -u`.
- **Never use `pytest -q` as a baseline** — ~20 tests read the `prefect-connectors` checkout live.
  Run targeted files; `tests/test_roadmap.py` hangs.
- Heredoc + f-string escaping bit three times when patching Python via `python - <<'PY'`. Prefer
  line-based inserts located by plain substring.

## 6. What is NOT done — the honest list

- **`keel` has never been run.** It is `DECLARED`, not `PROVEN`, and `registry.unproven()` says so.
- **Nothing committed, nothing pushed, no PR** in either repo.
- **No Jira comment** — this session maps to no client ticket, and the Atlassian MCP is unavailable.
- **No rendered validation of anything**, because nothing was deployed.
- The wiki council was **read-only**; not one repair it recommended has been applied.
- `wiki_lint.py` is **not in CI** — `agent-factory` has no `.github/` at all.
- The 87 frozen `processes/` runbooks are **proven frozen, NOT proven wrong.** Do not let anyone
  convert "froze in May" into "is wrong" without re-deriving each against live infrastructure.
