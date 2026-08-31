# Workflow library — shape × layer, and the marketing model that is still blocked

**Written 2026-08-31.** Supersedes nothing. Runs alongside `run-03-the-missing-middle` (that thread
is DONE and committed by a concurrent session — see §5).

`next:` **run `keel` on the GEP/Navira marketing model the moment Paul's artifacts land.**
Everything upstream of that is built and green. Nothing else in this file is on the critical path.

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
| `wiki/concepts/architecture/cross-channel-marketing-dimensional-model.md` | 498 lines of graded external evidence for the marketing design. ⚠ **UNCOMMITTED.** |
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
