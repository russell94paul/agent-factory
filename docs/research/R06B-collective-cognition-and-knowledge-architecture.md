# R06B — Collective cognition, mission-shaped knowledge, and whether this estate needs a graph at all

**Status: WRITTEN 2026-08-31. Not yet dispatched.** Supersedes the draft prompt at
`.agent-platform/bootstrap/research/prompts/R06B_COLLECTIVE_COGNITION.md`, which is `priority:
critical` in `WAVE_0.yaml` and which **no instrument in `factory/` can see** — `grep -rn "R06\|WAVE_0"
factory/*.py` returns nothing, so `python -m factory.dispatch` has never listed it as outstanding.
That blindness is itself a finding; file it.

Companion to `R10-hierarchical-wiki-agent-training.md` (asked whether a hierarchical wiki can *train*
an agnostic pipeline; **answered, and answered no**) and `R4-agnostic-optimizer.md`. R06B asks the
question R10 left open: *given that we already hold nine knowledge stores and one of them already
works, what — specifically, measurably — can none of them do?*

⚠ **Standing rule in this estate: an object named by a handoff is a hypothesis, not a finding.**
Every figure in §2 was measured on 2026-08-31 and carries the command that produced it. Apply the
same suspicion to every vendor and paper claim you report, and tier all of them.

## Run log

| Run | Dispatched | Outcome |
|---|---|---|
| 1 | 2026-08-31 | IN_REPO via the deep-research skill. |

---

## 1. What this pass is, and what it deliberately is not

An earlier draft of this brief (`R-KNOWLEDGE-01`) asked for a six-view "Collective Knowledge Fabric"
— daily-mission, repo-code, failure-repair, client-domain, tool-integration, research-decision — and
asked which graph topology to build it on. **That framing presupposes the answer.** A prompt that
opens with six views and asks you to pick a topology will return six views and a topology, because
nothing in it makes rejection cheap.

So the burden of proof is inverted here. **The null hypothesis is: build nothing.** Every proposed
structure must beat the stores in §2 on a named task, with a number. A pass that returns "yes, build
the fabric" without clearing §3 has failed, not succeeded.

The valuable outcome is a *no with a reason*. This estate has already spent one architecture cycle
building something four research passes had told it not to.

---

## 2. The nine stores that already exist — measured, with commands

Run from `C:\Users\PaulRussell\repos\agent-factory` on 2026-08-31.

| # | Store | Size | Command | What it already answers |
|---|---|---|---|---|
| 1 | `docs/findings.d/` | **28 findings, 2,299 lines** | `ls docs/findings.d/*.md \| grep -v README \| wc -l` | *What did we believe that was false, how was it measured, who inherits it* |
| 2 | `docs/evidence/` | **45 files** | `find docs/evidence -type f \| wc -l` | *What proved a change worked* |
| 3 | `docs/research/` | **56 md** (prompts + answers + packs) | `find docs/research -name '*.md' \| wc -l` | *Why the architecture is the way it is* |
| 4 | `docs/specs/` | **7** | `find docs/specs -type f \| wc -l` | *What was intended* |
| 5 | `boot-prompts/` | **13** | `find boot-prompts -type f \| wc -l` | *Session-to-session handoff state* |
| 6 | `.data/events.jsonl` | **61 events** | `wc -l < .data/events.jsonl` | *What the control plane actually did* |
| 7 | `.sessions/*.jsonl` | **7 transcripts** | `ls .sessions/*.jsonl \| wc -l` | *Raw agent traces* |
| 8 | LLM wiki (`../wiki`) | **492 pages, 894,741 words, ~1.16M tokens** | `find . -name '*.md' -print0 \| xargs -0 cat \| wc -w` | *Client/domain/process knowledge* |
| 9 | Zeus Memory (`cce_*` MCP) | not measured here | — | *Cross-session vector memory* |

Plus `.agent-platform/bootstrap/` (113 files) and `~/.claude/skills/` (the procedural tier).

⚠ **The wiki figure was measured twice.** The first instrument — `cat $(find ... -name '*.md')` —
returned **0 words** because the argument list overflowed silently. The `-print0 | xargs -0` form
returned 894,741. *A zero from an instrument you have not proved can see is not a measurement*, and
this brief tripped over that rule in its own §2. Assume the same failure mode in anything you count.

⚠ **`findings.d` field-coverage counts are inflated by one.** `grep -l '\*\*MEASURED BY\*\*'
docs/findings.d/*.md | wc -l` returns 29 against 28 findings, because `README.md` documents the field
names in a table. Any census of that directory must exclude the README or state that it did not.

**R10 §7 counted six overlapping stores and concluded "adding a seventh would be a mistake."**
The census above finds nine. If your recommendation adds a tenth, say explicitly why R10's
consolidation verdict does not apply — do not step around it.

---

## 3. Three standing constraints. Falsify them or inherit them.

These are not background reading. Each is a measured, in-estate result that a "build the fabric"
recommendation must defeat.

### 3.1 R10's verdict — the seventh store

`docs/research/answers/R10-answer-hierarchical-wiki-agent-training.md`:

- §Verdict — feeding a ~1.1M-token corpus is unworkable; performance fell ~24% with 30k irrelevant
  tokens; **memory laundering** means unsupervised write-back corrupts the base silently.
- §7 — *"We already have six overlapping stores… adding a seventh would be a mistake."* One access
  layer over what exists, not a new island.
- §8 — *"do NOT implement the auto-wiki loop or a new retrieval layer before"* (a) a sandbox,
  (b) cost/retrieval instrumentation, (c) an eval corpus of ~30 cases, (d) a control plane that can
  actually refuse a bad result.

**Question for you: has anything changed since 2026-08-23 that makes §8's precondition list
satisfiable, or is the correct answer still "fix the control plane first"?** Check `factory/readiness.py`
and the gate scores rather than taking this brief's word for it.

### 3.2 F84 — the blind instrument

`docs/findings.d/F84-the-zero-consumer-count-was-measured-by-a-blind-grep.md`. A count of zero was
published from a grep that could not see the aliased import form. This is **negative transfer from a
measurement**, observed here, not in a paper. Any retrieval system that returns "no prior art on this
failure" inherits exactly this failure mode.

### 3.3 F86 — the ledger that could not see itself

`docs/findings.d/F86-the-findings-ledger-could-not-see-its-own-last-eight-findings.md`. Eight findings
(F77–F84) were written with `#` instead of `###`, and `factory/findings.py`'s `_HEADING` silently
skipped every one — including F80 and F81, which were corrections about the control plane's own
gates, and F84 above. `test_findings.py` was green throughout, because every check it ran asked its
question only of the findings that had already parsed.

**This is the single most important prior result in this brief.** It is a working knowledge store,
with a parser, a schema and a test suite, that lost a third of its contents without emitting a
warning. Any proposal for a richer structure must say what it does that would have caught this.
"Use a database with a schema" is not an answer — the schema was documented; the *title line* was not.

---

## 4. The candidate views — each must beat the null

Rank these by **immediate value to one engineer doing one day's work**, then by implementation cost.
For each, the required verdict is `BUILD NOW | EXPERIMENT | DEFER | REJECT`, and the required
justification is *what question it answers that §2 cannot*.

1. **Daily mission / work view** — ticket, repo, files, decisions, tests, prior similar missions,
   blockers, owners, applicable tools, known failure patterns. Claimed benefit: less session startup,
   fewer context tokens, less repo rediscovery, fewer clarifying questions.
   *Prior question:* `boot-prompts/` (13 files) already exists to do this. Measure whether it works
   before designing a replacement.
2. **Repo / code intelligence view** — `DEPENDS_ON`, `CALLS`, `READS`, `WRITES`, `TESTED_BY`,
   `OWNED_BY`, `BROKE_IN`, `FIXED_BY`. Compare static code graphs, symbol graphs, dependency graphs,
   repo maps and semantic code retrieval. **Does graph structure measurably improve coding-agent
   outcomes, or does a good repo map plus grep match it?** Find the negative results.
3. **Failure → repair view** — see §5, which is the sharpened form of this and the highest-value
   section of the pass.
4. **Client / domain view** — what must be tenant-isolated vs globally reusable. The wiki (§2, store
   8) already holds this. Say what is missing, not what could exist.
5. **Tool / integration view** — capability, auth, limits, version, supersession, for GitHub /
   Prefect / Snowflake / Databricks / Power BI / Azure / Claude / DGX Spark. Claimed benefit: dynamic
   tool selection at mission-assembly time rather than hardcoding.
6. **Research / decision view** — `SUPPORTS`, `CONTRADICTS`, `SUPERSEDES`, `VALIDATED_BY`,
   `FALSIFIED_BY`, `IMPLEMENTED_AS`. *Prior question:* `docs/research/` (56 files) plus `findings.d`
   already encode most of this in prose. The `SUPERSEDED` status already exists in the findings
   schema, and `R3-optimizer-sandbox-SUPERSEDED.md` shows it in use at file level.

**Any view whose function is already discharged by a store in §2 is REJECTED, not DEFERRED.**
Say which.

---

## 5. The failure ledger: gap analysis, not greenfield design

⛔ **Do not design a Failure Intelligence Graph. One exists.** `docs/findings.d/` carries, today:

- `BELIEVED` / `ACTUALLY` / `MEASURED BY` / `AFFECTS` — mandatory, present on all 28 (`grep -l` above).
- `KIND` (`CORRECTION | INSTRUMENT | DESIGN | AGENT-DESIGN | PROCESS`) — 22 of 28.
- `CHANGES` — mandatory when KIND is DESIGN/AGENT-DESIGN; `malformed()` rejects a design finding
  without one.
- `STATUS` (`OPEN | ADOPTED | REJECTED | SUPERSEDED`) — 22 of 28.
- `[[F86]]` wikilinks between findings; per-lane id blocks so isolated worktrees cannot collide.
- A parser (`factory/findings.py`), `design_debt()` (open DESIGN findings — *the list that should
  shrink*), `by_kind()`, `by_lane()`, `malformed()`, `unattached()`.
- A regression test that derives the expected set from the directory and fails on any invisible file.
- The convention that `NOTHING TO REPORT` is itself an entry, so silence means *checked*.

**The question is what it structurally cannot do.** Measured absences — every one of these greps
returns 0 or ~0 across the 28 findings:

```
failure_family   0     time_to_fix   0     root_cause    0
similar_to       0     component     0     environment   1
```

So the artifact the original brief wanted —

```
failure_family: oauth_invalid_client
observations: 58
best_known_repair_path: [classify signature, inspect secret binding, ...]
median_time_before: X   median_time_after: Y   success_rate: Z
candidate_prevention: credential preflight
candidate_meta_tool: validate_oauth_environment
```

— **is not derivable from what we record.** There is no family key to group on, no timing to compute a
median from, no environment field to constrain applicability, no success/failure outcome per attempt.

**Answer these, in order:**

1. Which of those absences are worth closing, at what cost, and *would a closed one have changed a
   decision we actually made?* Walk at least three real findings (F84, F86, F93 are good candidates)
   and say what the enriched schema would have bought.
2. Is 28 findings enough population for clustering, or is the honest answer "too few to mine — keep
   writing prose and revisit at N=100"? **This is a live possible verdict. Say so if it is true.**
3. Prior art: case-based reasoning, incident management, SRE post-mortem corpora, AIOps, fault
   localisation, causal graphs, troubleshooting KBs, autonomic computing, self-healing systems,
   failure-pattern mining. *At what corpus size do these techniques start to pay?* That number is the
   answer to question 2.
4. **Negative transfer is the central risk, not retrieval quality.** A repair that worked in one
   environment is wrong in another. How is that detected — not prevented in principle, *detected in
   this estate*? F84 is the worked example: the instrument was blind and the answer looked clean.
5. Do not optimise for shortest repair path. Any ranking must carry success probability, risk,
   environment similarity, confidence, applicability constraints, cost and blast radius.

### 5.1 The scheduled optimiser — earn it or reject it

A `Failure Optimizer` that periodically clusters failures, finds repeated root causes, compares repair
sequences, proposes preflight checks and mines meta-tool candidates. **Given the answer to 5.2, is
this justified now, at N=28, or is it a job for N=200?** If deferred, say what the trigger is.

Same treatment for: Knowledge Gardener, Stale Knowledge Detector, Contradiction Resolver, Graph
Compactor, Repair Path Optimizer, Experience Distiller, Meta-tool Candidate Miner. For each that
survives: trigger/frequency, input, algorithm, output, metrics, **human gate**, risk, and what must
remain deterministic.

⚠ R10's memory-laundering result applies directly to every one of these jobs. An optimiser that
writes back unsupervised is the auto-researcher R10 rejected, wearing a different hat.

---

## 6. Mission-shaped context projection

The one genuinely novel idea in the original brief, and the one worth the most scrutiny:

```
global knowledge → mission classification → subgraph retrieval
                 → mission-specific projection → role-specific context packets
```

Compare honestly against: flat semantic search, vector RAG, GraphRAG, hybrid BM25+vector+graph,
persisted knowledge graphs, temporal graphs, event-sourced knowledge, case-based reasoning.

**The sharp sub-question: should structure be *generated per mission* rather than *persisted
globally*?** A projection compiled on demand from flat sources has no staleness problem, no
contradiction-propagation problem, and no migration cost — three of the four hardest problems in the
persisted-graph design disappear. If that is right, most of §4 collapses into a retrieval-and-assembly
problem and the graph is never materialised. **Test that hypothesis seriously; it may be the finding.**

Also: is a graph database needed at all, or does SQLite/Postgres + structured records + hybrid search
carry this estate for several years? Answer with the §2 numbers, not in general.

---

## 7. Temporal validity, provenance, quality

Only for structures that survived §4–§6.

- Valid-time vs transaction-time vs bitemporal; versioned nodes and edges; superseded architecture;
  config and software versions; obsolete repairs; stale runbooks; changing API behaviour.
- Provenance, confidence, evidence quality, contradiction handling, freshness, dedup, source
  authority, uncertainty, negative-transfer protection.
- **What may an agent write automatically, and what requires validation before becoming doctrine?**
  The findings schema's answer today is that a DESIGN finding must carry `CHANGES` and a `STATUS`
  ruling — a human decision gate encoded as a required field. Is that sufficient, and does it
  generalise?
- Client isolation: what must never leave a tenant, and how is a globally reusable lesson safely
  derived from a client-specific case?

---

## 8. Benchmark — against our corpus, or admit we cannot

Design an evaluation comparing:

- **A** — no memory, fresh agent
- **B** — flat semantic/vector retrieval over §2 as-is
- **C** — typed structured retrieval
- **D** — mission-shaped projection
- **E** — hybrid graph + semantic

Metrics: time to first useful action; task completion time; context/token size; precision@k; recall;
human clarification count; retry count; root-cause time; repair success rate; repeat-failure rate;
**negative-transfer rate**; regressions; knowledge reuse rate; cost; operator interventions.

**Build the dataset from what exists — `findings.d` (28), `docs/evidence/` (45), `.data/events.jsonl`
(61), `.sessions/` (7) — and report first whether that is enough to distinguish A from B at all.**
R10 §9 set a decision rule of ≥20% fewer interventions or ≥15% more correct outputs at p<0.05, over
~30 cases. **With 61 control-plane events and 7 transcripts, is that test even powered?** If the
answer is no, the top recommendation of this pass is *instrument first, then measure*, and the graph
question stays unanswered on purpose. That is an acceptable and possibly correct outcome.

If C and D do not beat B, do not build the graph complexity.

---

## Required method

- Primary, official, peer-reviewed sources and source code over marketing summaries. Inspect
  open-source implementations, not only papers and blogs.
- Separate measured evidence, documented practice, architectural inference, hypothesis, speculation.
- **Find failure cases and negative results, not only success stories.**
- Assume the preferred architecture is unnecessarily complicated; identify simpler alternatives.
- Identify what existed before the LLM era and what materially changes now.
- Do not recommend a new service, protocol or agent layer unless a real requirement justifies it.
- Every load-bearing citation verified against the real artefact before it is promoted to a finding.

## Required outputs

1. Executive finding — including whether the null (build nothing) survives.
2. §2 census re-verified, with any store this brief missed or miscounted.
3. Ranked daily-productivity use cases — value to one engineer's day, then cost.
4. Prior-art map, tiered.
5. What works / what fails in the field.
6. **Failure-ledger gap analysis** (§5) — the schema delta, with the corpus-size threshold.
7. Failure Optimizer: justified now, or deferred with a named trigger.
8. Mission-shaped projection design, and the per-mission-vs-persisted verdict.
9. Recommended architecture, or the reasoned refusal to recommend one.
10. Sub-view / boundary structure — logical view vs physical separation, per boundary.
11. Temporal, provenance and quality model, for surviving structures only.
12. Security and client-isolation model.
13. Benchmark design + the power analysis on our actual corpus.
14. Simplest viable MVP, and **what not to build yet**.
15. 30 / 60 / 90-day path.
16. Experiments that would falsify this pass's own recommendation.
17. Risks and failure modes.
18. Implementation implications for Agent Factory — named files under `factory/`.
19. Research gaps.
20. Source list with quality notes.

**Final table.** Every proposed subsystem: `BUILD NOW | EXPERIMENT | DEFER | REJECT`.
**Every major conclusion labelled:** `[EMPIRICAL] [PRACTICE] [INFERENCE] [HYPOTHESIS] [SPECULATIVE]`.

## Falsification conditions

State, before you conclude, what would have changed your recommendation. At minimum:

- What corpus size would flip the "too few findings to mine" verdict?
- What measurement would prove the persisted graph beats the on-demand projection?
- What would prove R10 §8's "fix the control plane first" no longer binds?

The recommendation optimises for one engineer's useful daily work in this repo — not for
graph sophistication, and not for a platform nobody is yet running.
