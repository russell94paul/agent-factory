# R10 — Can a hierarchical wiki plus an auto-researcher train a repo-agnostic agentic pipeline?

**Status: NOT DISPATCHED.** Written 2026-08-22. Paste the whole file into ChatGPT Deep Research (or
equivalent). The answer lands beside it as
`docs/research/answers/R10-answer-hierarchical-wiki-agent-training.md`.

Companion to `agent-factory/docs/research/R4-agnostic-optimizer.md` (asked whether the *optimiser*
can be repo-agnostic) and `R8-data-engineering-agent-factory.md` (asks what the factory should be
when the work is data engineering). **R10 asks a different question: whether the thing that makes a
generic pipeline competent in a specific domain can be a curated, hierarchical, self-extending
knowledge base — and whether the loop that extends it compounds or corrupts.**

⚠ **Standing rule in this estate: an object named by a handoff is a hypothesis, not a finding.**
Every figure in §2 was measured on 2026-08-22 and cites its command or file. Apply the same
suspicion to every vendor and paper claim you report, and tier all of them (§9).

---

## 1. The concept being tested

The claim, stated as its author states it, in four parts:

1. **An agnostic agentic pipeline.** One pipeline — plan, act, review, gate, ship — that is not
   written per domain. Pointed at a new repo, client, or problem class, it is *configured*, not
   rebuilt.
2. **Trained with a wiki.** The pipeline's domain competence comes from a curated knowledge base
   rather than from bespoke prompts or a fine-tune. The wiki is what makes the agnostic pipeline
   good at *this* domain.
3. **A hierarchical wiki.** The knowledge base is not a flat pile of documents. It has levels —
   entities, concepts, processes, tickets, daily notes — linked into a graph, so an agent can enter
   at the right altitude and descend.
4. **An auto-researcher.** An agent that detects gaps in the wiki, researches them, and writes back.
   The loop is intended to compound: agents consume the wiki, discover what it is missing, extend
   it, and the next agent inherits the extension.

**The question is whether that eventually works, and what "eventually" costs.** A verdict of *no,
and here is the fact that kills it* is more valuable to us than an encouraging synthesis. We have
already spent one architecture cycle building something four research passes had told us not to.

### 1.1 The word "train" is doing too much work — take it apart first

Before anything else, separate the mechanisms that "train with a wiki" could mean. They have
different evidence bases, different cost curves, and different failure modes, and we suspect the
concept is silently assuming whichever one is convenient at the time:

| | Mechanism | What it would mean here |
|---|---|---|
| **A** | Fine-tuning / continued pretraining on the corpus | Weights change. Corpus is ~1.1M tokens (§2). |
| **B** | Retrieval at inference (RAG, vector or graph) | Wiki is queried per task; chunks enter context. |
| **C** | Structured context assembly | The hierarchy is *compiled* into a prompt — the agent is handed a route through the graph, not a bag of search results. |
| **D** | Agent memory with write-back | The wiki is both read and written during work; it is state, not reference. |
| **E** | Procedure synthesis | Wiki pages become executable skills/tools, not prose the model reads. |

**Which of A–E does the evidence actually support at ~10^6 tokens of proprietary, partly-stale,
partly-wrong internal documentation?** Say explicitly where each fails. We believe our current
practice is an unexamined mixture of B, C and D, and that E may be where the real leverage is — but
that belief is ours, not a finding.

---

## 2. What exists today, measured 2026-08-22

This is not a greenfield proposal. Most of the pieces exist and can be counted.

### 2.1 The substrate inventory — five knowledge stores, already

| Store | Size | Structure | Measured by |
|---|---|---|---|
| LLM wiki (`repos/wiki`) | **481 files, 831,853 words** | 12 top-level dirs; YAML frontmatter on **306** files; path depth 1–9 | `find`/`wc` |
| Boot prompts (`aldc-launchpad/boot-prompts/`) | **183 files, 249,426 words** | flat, dated, one per workstream; cross-repo | `ls`/`wc` |
| Ticket evidence (`docs/evidence/`) | **944 files, 260,736 words** (md only) | one directory per ticket | `find` |
| Per-project agent memory (`~/.claude/.../memory/`) | **95 files** | one fact per file, frontmatter-typed, `[[linked]]` | `ls` |
| Skills (`~/.claude/skills/`) | **81 dirs, 30 invocable** (`SKILL.md`) | two tiers: invocable vs. reference-only | `find` |
| Zeus Memory (vector store, MCP `ccx`) | **NOT MEASURED** | embedding search, async ingest | — |

Plus ~5,700 words of always-loaded instruction (`CLAUDE.md`, global + project).

⭐ **Read that table as the finding it is.** The estate already has five-to-six knowledge substrates
with overlapping content and no single retrieval path. The project's own standing instruction says
*"do not create a fifth artefact home."* **A recommendation that adds a sixth store is a
recommendation to lose.** Tell us whether the correct move is consolidation, federation, or a
routing layer over what exists — and what the prior art says about each.

### 2.2 The hierarchy, as it actually exists

| Figure | Value | Basis |
|---|---|---|
| Wikilink instances | **5,498** | MEASURED, `grep -o` over all `.md` |
| Distinct link targets (filtered to plausible page names) | **454** | MEASURED |
| Targets resolving to a real file | **282** | MEASURED |
| Targets resolving to nothing — dangling | **172 (≈38%)** | MEASURED |
| Files carrying frontmatter tags | 306 of 481 (64%) | MEASURED |
| Files at path depth ≥6 | 156 of 481 (32%) | MEASURED |

**38% of the graph's edges point at pages that do not exist.** In the author's model that is a
feature — a dangling `[[link]]` marks a gap worth filling, which is precisely the auto-researcher's
input queue. In a retrieval model it is a broken index. **Which is it, and does any prior art treat
dangling links as a work queue rather than a defect?** This is one of the two or three questions we
most want answered.

### 2.3 The domain, and why generic agent research usually misses it

The work is **data engineering**, not software engineering: vendor API → Azure container →
Prefect 3 → Snowflake → BI/chat surfaces. Four things break the usual assumptions, and an answer
that ignores them has not read the brief:

1. **The oracle is downstream and expensive.** A warehouse view can be syntactically perfect, pass
   every test, deploy cleanly, and be wrong in a way visible only when a dashboard renders a number
   a human recognises as impossible. A query-layer check is *not* a render check — a repoint here
   once passed DAX parity while every visual showed "Error loading data".
2. **Blast radius is not bounded by the repo.** `git revert` does not undo a `CREATE OR REPLACE`
   that stripped an ownership grant on a live data share.
3. **Correctness is a measurement, not a test.** "Did this change only what it should?" is a
   before/after row-count and delta question at production scale.
4. **Much of what an agent needs to know is in no repo at all.** Which object the dashboard actually
   reads; which of two identically-valued tables is the live one; that a named ticket's stated
   premise was wrong. **That is exactly the class of knowledge the wiki holds — which is why the
   concept is plausible at all.**

### 2.4 The pipeline half, measured (carried from R8)

| Figure | Value |
|---|---|
| Readiness gates passing | 9 of 30 |
| Runs finishing with no human | 3 of 14 |
| Gate events that were ever a **refusal** | **0 of 22** |
| Max concurrent agent lanes (from the real conflict graph) | 3 |
| Cross-agent conflict rate on a shared branch | 41.7% |
| Eval corpus | **1 case, 0 strata** (a 10%-prevalence blind spot needs ~29 cases to be seen once) |
| Dimensions covered by the agent version hash | **0 of 15** |
| Sandboxing / cost instrumentation | none / none |

⭐ **A gate set observed refusing zero times out of 22, and a corpus of one, mean we currently have
no instrument that could detect the wiki making things worse.** Any answer that recommends the loop
must also say what instrument would catch it failing (§7).

---

## 3. Question 1 — does "agnostic pipeline + domain knowledge pack" decompose at all?

The concept assumes a clean seam: a generic pipeline on one side, swappable domain knowledge on the
other. Test that assumption rather than accepting it.

- **Where is the seam actually, in systems that have tried it?** What stays invariant across
  domains — control flow, gates, review structure, tool protocol — and what unavoidably leaks into
  the "generic" half? Name the leaks concretely.
- **Study the systems that already ship this shape**, and label each OBSERVED vs. MARKETED: Claude
  Code's `CLAUDE.md` + skills + subagents; Cursor/Windsurf rules files; Devin's "knowledge";
  Cognition's playbooks; Aider's repo map; Sourcegraph Cody context; OpenHands microagents;
  LangGraph/CrewAI/AutoGen role configs; Amazon Q Developer customisations. **Which of these
  demonstrably transfers across repositories, with published evidence rather than a launch post?**
- **Is there a measured effect size anywhere** for "same agent + domain knowledge pack" vs. "same
  agent, no pack" on a real task suite? SWE-bench and its variants mostly hold knowledge constant —
  if the literature cannot answer this, say so plainly, and say what the closest evidence is.
- **What does the agnostic framing cost?** R4 asked the parallel question about the optimiser. If
  portability must be designed in now rather than retrofitted later, we need to know that before
  building, because retrofitting is the expensive branch.

---

## 4. Question 2 — is *hierarchy* load-bearing, or decoration?

The distinctive part of the concept is that the wiki is hierarchical rather than flat. That is a
testable claim about retrieval and reasoning, not a matter of taste.

- **What is the evidence that hierarchical or graph structure beats flat chunking + embeddings**,
  and at what corpus size does the crossover happen? Cover at minimum: GraphRAG and its independent
  replications, RAPTOR-style recursive summarisation, HippoRAG, knowledge-graph and ontology-driven
  RAG, hierarchical/multi-hop retrieval, and the honest negative results. Include the cost side —
  index build cost, staleness cost, maintenance cost per document changed.
- ⭐ **The size fact that may kill the whole retrieval layer: the wiki is ~832k words ≈ 1.1M tokens,
  and the session model here is a 1M-context Opus.** The entire knowledge base is within an order of
  magnitude of *fitting in the context window*. So:
  - At what corpus size does retrieval start beating "select the right 200k tokens and paste them"?
  - What does the long-context literature (lost-in-the-middle, context rot, effective vs. advertised
    context) say about the quality of that paste at 200k–1M tokens on **reasoning** tasks rather
    than needle-retrieval tasks?
  - Is the correct architecture here **hierarchical routing into a small context** rather than
    retrieval at all — i.e. mechanism **C**, not **B**, from §1.1?
- **Which hierarchy actually helps?** Taxonomy by entity type (our current cut: entities / concepts
  / processes / tickets / daily)? By abstraction level? By recency? By provenance strength? Is there
  evidence that a particular cut outperforms the others, or is the finding that *any* consistent
  structure beats none?
- **Who has built a hierarchical knowledge base explicitly for machine consumers**, and what did
  they learn — Wikipedia/Wikidata's structure and governance, Zettelkasten/Obsidian practice,
  enterprise ontologies, Palantir-style semantic layers, dbt's semantic layer, data catalogues
  (Amundsen, DataHub, OpenMetadata)? **Data catalogues are the closest existing thing to our wiki
  and are rarely mentioned in agent research — say whether that adjacency is real or superficial.**

---

## 5. Question 3 — the auto-researcher, and whether the loop compounds or corrupts

This is the part we are least confident in and most attached to. Argue against it properly.

- **Named failure modes, with prior art.** Self-generated-content contamination and model collapse;
  error propagation through a corpus later agents treat as ground truth; confident fabrication
  written in the register of a verified fact; drift where the wiki describes a system that no longer
  exists; volume growth outpacing curation until retrieval degrades. **Which of these are
  demonstrated, which are theorised, and which have a published mitigation that actually works?**
- **Study the systems that write knowledge autonomously:** Stanford STORM (Wikipedia-like article
  generation from research), Deep Research products as a class, Generative Agents' memory stream and
  reflection tree, MemGPT/Letta, Zep/Graphiti temporal knowledge graphs, mem0, A-MEM, Voyager's
  skill library, Reflexion/self-refine lineages, and the automated-scientist systems (AI Scientist
  and its critiques). **For each: does the written artefact measurably improve later performance,
  measured how, and does the improvement survive iteration — or decay?**
- ⭐ **The provenance question.** This estate's standing rules already require every published figure
  to carry a basis label — `MEASURED | DERIVED | ASSUMED | PROXY` — and to keep distinct verdicts
  distinct (`ZERO` vs `NOT-RECORDED` vs `NOT-VISIBLE` vs `NOT-RETAINED`) rather than collapsing them
  into "zero". **Should the wiki enforce the same at page and claim level, and does anyone do this?**
  What is the evidence that provenance tiering inside a corpus changes downstream agent behaviour,
  as opposed to being metadata that no retrieval path reads?
- **What gate must an auto-researcher pass before it writes?** Human review of every page does not
  scale and is the thing the concept exists to escape. Sampled review? A quarantine tier that
  retrieval down-weights? Provenance-required writes? A second agent whose only job is to refute?
  **What is the cheapest gate with evidence behind it?**
- **Model the contamination, do not merely warn about it.** What does the corpus look like after 100
  auto-written pages if the gate is imperfect at, say, 10%? What does that do to retrieval quality
  and to downstream task success?
- **The correction path.** When the wiki is *wrong* — not missing, wrong — what mechanism removes the
  error and everything derived from it? Wikipedia has one and it is social. What is the machine
  analogue, and has anyone made it work?

---

## 6. Question 4 — write-back during work, not just research

Distinct from the auto-researcher: agents doing real work discover facts as a by-product (this
object is the one the dashboard reads; this ticket's stated premise was false). Today those land in
boot prompts and per-fact memory files, by hand.

- Is there evidence that **work-derived** knowledge capture outperforms **research-derived**
  capture, or vice versa? Our prior is that the by-product is far more valuable per token, because
  it was measured rather than synthesised — test that prior, do not adopt it.
- **What should trigger a write?** Every session? Only a correction of a prior belief? Only a
  finding that contradicted the substrate?
- **How is a correction represented** so the superseded claim stops being retrieved? Our wiki marks
  supersession in prose, which retrieval does not honour. Is there a working pattern — temporal
  knowledge graphs, bitemporal validity, tombstones, claim-level versioning?

---

## 7. Question 5 — how would we know it is working?

We will judge the answer by this section. **An architecture we cannot measure is one we will believe
in regardless of results — and this estate has already shipped a gate set that refused nothing, 22
times out of 22.**

- **Design the A/B.** Same task class, same agent bundle, wiki-on vs. wiki-off. What is the unit of
  observation? How many cases before a difference is detectable, given that our own eval work says a
  10%-prevalence effect needs ~29 cases to be seen once?
- **What is the metric** when the domain oracle is a rendered dashboard and a human's judgement?
  Task success is too coarse. Candidates: rediscovery cost (did the agent re-derive a fact the wiki
  already held?), correction rate, human interventions per run, wrong-layer deploys avoided.
  **Which of these have precedent, and which are we inventing?**
- **What is the leading indicator of corruption**, observable before a wrong answer ships? Corpus
  growth vs. citation concentration? Fraction of retrieved chunks that are auto-written?
  Contradiction density between pages?
- **Design the falsification.** What observation, within 30 days, would prove the concept does not
  work for us? If you cannot name one, say that the concept is unfalsifiable at our scale — that is
  itself a finding worth having.

---

## 8. Question 6 — the honest verdict, and the alternative

1. **Does this eventually work?** Answer directly. Distinguish *works in principle*, *works at our
   corpus scale*, *works with our team size (about 4 engineers)*, and *works unattended*.
2. **What is the single fact most likely to kill it**, and can we observe that fact today?
3. **What would you build instead**, if the answer is no or partly-no? Include the possibility that
   the right answer is unglamorous: fewer stores, better search over what exists, a skills/procedure
   library (mechanism **E**) rather than a prose corpus, or simply pasting the right 200k tokens.
4. **Build order.** Given 9-of-30 readiness gates, no sandbox, no cost instrumentation and a
   one-case eval corpus, **does knowledge infrastructure come before or after fixing those?** Prior
   research passes here converged on *fix the control plane first* and were ignored once; if that is
   the answer again, say so bluntly.
5. **The cheapest decisive experiment.** One thing, runnable in two weeks by one engineer, whose
   result would change the plan either way. Name the measurement **and the decision rule before the
   result**.

---

## 9. How to report evidence

Tier **every** claim you make, inline:

- **OBSERVED** — you read the primary source: a measured result, a reproducible benchmark, a
  post-mortem with numbers.
- **DERIVED** — your reasoning from observed facts. Show the step.
- **REPORTED** — a credible secondary account you could not verify.
- **MARKETED** — a vendor or launch claim. **A marketed claim may not be used as a design premise.**

Additional rules:

- **Separate "no evidence found" from "evidence of absence."** If the literature has not tested
  something, say *not tested*, not *does not work*.
- **Prefer negative results and post-mortems** to launch announcements. Systems that were tried and
  abandoned are more informative here than systems being sold.
- **Give dates.** This field moves monthly; a 2023 result about context windows may be obsolete.
- Where you cite a benchmark, say what it measures and what it does not.

## 10. Deliverable format

1. **Verdict** — one paragraph, up front. Does it work? What kills it?
2. **The five mechanisms (§1.1)** — a table, each with an evidence verdict and a recommendation.
3. **Hierarchy** — load-bearing or not? At what corpus size? Which cut?
4. **The auto-researcher** — compound or corrupt, with the modelled contamination and the gate you
   recommend.
5. **Consolidation** — what happens to the six existing stores. Merge, federate, or route?
6. **Measurement plan** — the A/B, the metrics, the leading indicator of corruption, the
   falsification.
7. **Build order** — what to do first, and explicitly what NOT to build yet and what would unlock it.
8. **The two-week decisive experiment**, with its decision rule stated in advance.
9. **Sources**, tiered, dated, each with a one-line note on what it actually demonstrated.

**What a bad answer looks like**, so you can avoid writing one: a survey of RAG techniques; a
recommendation to adopt a named framework; an enthusiastic yes with a phased roadmap and no
measurement; advice that ignores the downstream oracle and the five stores that already exist; any
use of a vendor claim as a premise. **If the honest answer is that this does not work yet at our
scale, say so in the first paragraph and spend the rest of the document on what does.**
