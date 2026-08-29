# External review prompt — for DeepSeek (or any model with no filesystem access)

**Written 2026-08-29.** Use when handing the agent-factory corpus to an outside model.

Two things make this different from `docs/CORPUS-AND-DESIGN-PROMPT.md`:

- That prompt runs **in-repo**. More than half of it is *measurement of things on disk* — it says
  "run `python -m factory.certify`". An external model cannot do any of that.
- This one must return output **we can load back into the board without retyping**, so the ticket
  section specifies a strict JSON schema rather than prose.

---

## ⚠ Before you upload anything

You are sending internal engineering documents to a third-party model. Check each file for:

- **Credentials.** Never upload `.env`, anything under `wiki/vault/`, `blueprints/*.yaml` with
  connection strings, or `.data/` exports that may embed tokens.
- **Client-identifying detail.** This repository was redacted to `CLIENT-A` / `CLIENT-B` on
  2026-08-29 — keep it that way, and check any file you add from outside it. The analysis never
  needs a real client name, and an external model has no reason to hold one. Note the redaction
  covers the working tree only: **git history still carries the original names.**
- **The security backlog.** Do not upload `council-room.html` or anything enumerating open
  credential exposures.

Everything below assumes a redacted upload.

---

## What to upload — the minimum set that makes the answer good

Ranked by value per token. Uploading more is not better; uploading the wrong things buries the
signal.

| # | File | Why it is essential |
|---|---|---|
| 1 | `docs/CLIENT-INTAKE-PLATFORM-PLAN.md` | the plan being critiqued — without it the model invents a different project |
| 2 | `docs/absorption-backlog.md` | AB-01…AB-19, the conclusions nobody actioned. **This is the work.** |
| 3 | `docs/findings.md` + `docs/findings.d/F70…F76` | corrected premises another lane would otherwise repeat |
| 4 | `docs/research/SYNTHESIS.md` §17 | the reconciliation that found seven false "not landed" claims |
| 5 | `docs/research/agent-factory-concept-inventory.md` | what concepts already exist, so it proposes nothing already built |
| 6 | `README.md` (agent-factory) | the contract/evals/blueprint/metrics ordering and *why* it is that order |
| 7 | `workflow-kit/README.md` | the four gates and the `jq` failure that motivated them |
| 8 | `workflow-kit/templates/intake.md` | the contract schema the portal is a UI over |
| 9 | `ALDC Ontology AutoGeneration Assessment.md` | the elicitation method — §"Source 2: Questionnaire" |
| 10 | `AOR_RMRR_explainer_note_final.md` | the learning metrics, the confound, the guarded formula |

Optional, only if the model has room: two or three `docs/research/answers/R*.md` that the plan
leans on hardest (R14, R17, R18). **Do not upload all eighteen** — the corpus's own diagnosis is
that it has too much unabsorbed research already.

---

## The prompt

Copy everything below the line.

---

You are a principal engineer reviewing a partially-built internal platform for a small
data-analytics consultancy. You have been given that team's own research corpus. Your job is
**not** to research anything new. It is to consolidate what they already concluded, find what they
missed, and return work items they can execute.

### The situation, so you do not have to infer it

**ALDC** is a data-analytics consultancy. One engineer, working with AI agents, delivers for
~19 clients. The work is: connect a client's data sources, land the data in Snowflake, build a
dimensional warehouse and a Power BI or Superset model, and serve dashboards the client makes
decisions on. Roughly 84% of their commits are agent co-authored, so **the bottleneck is not
writing code — it is verifying it.**

**The problem being solved.** On a recent first delivery the engineer had "a high-level idea, but
no detailed spec, and no validation that each new API connector had the data the client expected."
Missing fields were discovered in week six rather than at kickoff. They want a client-facing intake
that produces a machine-checkable specification, so a field the client never declared cannot
silently be missing later.

**What already exists and is verified working** (do not propose building these):

- A **contract-and-certification system**. A delivery is scored against twelve assertions — the
  exact image resolves, the run completed, rows landed, *emitted == landed*, semantic invariants
  hold, landed agrees with source per business key, no credential leaked, every row inside the
  declared tenant. It currently returns all twelve PASS, and — importantly — it labels its own
  result *"REPLAYED, not a live measurement"* when scoring against a recorded run.
- A **negative control**: a test that proves the contract is *able to fail*. Their rule is that no
  gate ships without one, after they found a guard that had blocked nothing for months because it
  depended on a binary that was not installed and exited the wrong code.
- **Four enforcement gates**: a pre-tool guard, a commit-message ticket requirement, a staged-diff
  secret scan, and a CI evidence gate. Each has a two-directional test — it must block bad input
  **and** let legitimate work through.
- **Provisioning CLIs**: multi-tenant client onboarding, Snowflake provisioning, portal + row-level
  security, and a Snowflake→Power BI schema generator.
- A **versioned blueprint format** where the config *is* the version, plus paired activity/outcome
  metrics and a frozen evaluator whose corpus sits behind a checksum manifest.

**What is proposed but not built:** the client questionnaire, the portal, the learning metrics
(coverage and helpfulness), a write gate that rejects low-grounding writes, and a causal test.

**The diagnosed failure mode of this team, in their own words:** *"Seven sentences say an answer
has not landed. All seven are false."* They have eighteen research passes and nineteen concluded
items that never reached a decision record. **Their gap is absorption, not knowledge.**

### Hard rules

1. **Do not open a new research question.** If you believe one is unavoidable, you may propose it
   only by naming **which uploaded document failed to cover it, by filename and section**. A
   proposal without that citation will be discarded.
2. **Do not propose anything already built.** Check the list above and the concept inventory first.
   If you are unsure whether something exists, say so explicitly rather than assuming it does not.
3. **Label every claim** `OBSERVED` (stated in an uploaded document — cite it),
   `DERIVED` (your reasoning from those documents — show the step), `ASSUMED` (you are supplying it),
   or `EXTERNAL` (general industry knowledge, not from these files). Untiered claims are discarded.
4. **Distinguish BUILT / PROPOSED / REJECTED everywhere**, including in diagrams. A diagram that
   draws a proposal like a built component convinces its own author.
5. **Never state a count you cannot source.** If you want a number that is not in the documents,
   write `NOT-SUPPLIED` and name what you would need. Do not estimate silently.
6. **Trade-offs, not recommendations alone.** Every option you propose states what it costs and
   what it forecloses. A recommendation with no downside listed will be treated as unconsidered.
7. **Optimise for one engineer.** Anything requiring a second full-time person, a new vendor
   contract, or more than two weeks before first value is out of scope — say so and give the
   cheaper version.

### Deliverables — return all five, in this order, in these formats

**D1 — Absorption verdicts.** For each AB item in `absorption-backlog.md`, one line:
`AB-nn | ACTION | one sentence` where ACTION is `DO` (worth doing — say the smallest version),
`REJECT` (say why, in writing — this is a legitimate and useful outcome), or
`MERGE-INTO <AB-nn or CIP-nn>`. Do not skip items; if you cannot judge one, mark it
`INSUFFICIENT` and name what you would need.

**D2 — The technical diagram set.** Five Mermaid diagrams, one per layer, each fenced as
` ```mermaid `. Every node classed `built`, `proposed`, or `rejected` using:

```
classDef built fill:#E2EDE7,stroke:#2C6A4A,stroke-width:2px
classDef proposed fill:#F5EEDC,stroke:#8A6B1E,stroke-dasharray:5 4
classDef rejected fill:#F6E5E2,stroke:#96342F,stroke-dasharray:2 3
```

- **L1 Elicitation** — client question → contract field → the check that settles it. One claim:
  nothing is asked that does not become checkable.
- **L2 Contract** — the record's own state machine: DRAFT → AGREED → CERTIFIED → SUPERSEDED, with
  the transition condition written on each edge.
- **L3 Execution** — source → connector → storage → warehouse → model → dashboard, with the
  client boundary drawn as a real line and what may cross it labelled.
- **L4 Assurance** — the twelve assertions and four gates, drawn as the path a change actually
  takes, including **any path that bypasses a gate**.
- **L5 Learning** — capture → store → retrieve → measure → adapt, with the evaluator drawn
  **outside** the loop and the write gate drawn as a valve on Store.

Then one paragraph per diagram: what it shows that prose cannot, and the single most likely way
it is wrong.

**D3 — Optimisations, specific to this use case.** 8–15 items. Each exactly:

```
TITLE        one line
TIER         OBSERVED | DERIVED | ASSUMED | EXTERNAL
SOURCE       filename §section, or "external"
CHANGE       what to do differently
COSTS        what it costs or forecloses
EVIDENCE     what would show it worked — and what would falsify it
```

Prioritise: things that remove a step rather than add one; things that make an existing mechanism
fire rather than adding a mechanism; anything letting the questionnaire ask fewer questions for
the same spec completeness.

**D4 — Board items, as JSON only.** A single fenced ` ```json ` block, an array of objects,
no prose inside it:

```json
[{"id":"CIP-21","phase":"P2","title":"one line, imperative",
  "why":"the failure it prevents","depends_on":["CIP-08"],
  "acceptance":"the check that settles it — must be falsifiable",
  "evidence":"the artefact that proves it","effort":"S|M|L",
  "tier":"OBSERVED|DERIVED|ASSUMED","source":"filename §section"}]
```

`CIP-01`…`CIP-20` already exist — **start new items at CIP-21**. If you would change an existing
one, emit it with its original id and a `"revises":"reason"` field.

**D5 — What you could not judge.** Everything the uploads did not let you assess, and the single
file that would most improve your answer. Be specific; "more context" is not an answer.

### Two things to get right

- The team's most expensive recurring error is **inheriting a premise**: a ticket names the object
  it assumes is at fault, and the real cause is two hops away. Where the uploads assert a cause,
  ask whether it was *measured* or *assumed*, and say which.
- Their learning metric already failed once in an instructive way: an apparent 18-point signal
  turned out to measure **repetition, not learning** — successful work repeats, failed work
  scatters, so a similarity-based comparison finds priors for successes automatically. Any metric
  you propose must state what confound would produce the same reading if nothing were learned.

---

## Variant B — the repo is public and the model can browse it

Use this **in addition to** the prompt above when the model has web access to the repository. It
turns the pass from "critique these documents" into "find where the documents and the code
disagree", which is a strictly better question — and one the uploads alone cannot answer.

⚠ **This variant is only honest if the repo is genuinely public.** Verified 2026-08-29:
`russell94paul/agent-factory` is PUBLIC; `russell94paul/aldc-launchpad` is PRIVATE, so any claim
about `workflow-kit/` must come from the uploaded copy, not from browsing.

Append this to the prompt:

---

**You also have web access to the repository these documents describe:**

```
https://github.com/russell94paul/agent-factory
raw files: https://raw.githubusercontent.com/russell94paul/agent-factory/main/<path>
```

**Your highest-value deliverable is now D0, and it comes first.**

**D0 — Document/code divergence.** The uploaded documents describe intentions. The repository is
what exists. Find every place they disagree. For each:

```
CLAIM        what the document says, quoted
SOURCE       document filename §section
REALITY      what the repository actually contains
VERIFIED_AT  the raw URL you fetched, and the line or symbol you read
VERDICT      CONFIRMED | STALE | CONTRADICTED | UNVERIFIABLE
IMPACT       what a reader would do wrong believing the document
```

Rules for D0, and they are the whole point:

1. **Fetch the file. Do not infer it from the document.** A claim you did not open is
   `UNVERIFIABLE`, not `CONFIRMED`. Say which you could not reach and why.
2. **Quote the repository, not the document, in the REALITY field.** If those two fields say the
   same thing in different words, you have not verified anything.
3. **A `STALE` verdict is a success, not a criticism.** This team's known failure is a document
   describing a state the code has moved past. Finding those is the job.
4. Prioritise, in this order: (a) claims about what is BUILT vs PROPOSED — the most damaging
   error class; (b) claims about what a test or gate enforces; (c) counts of any kind; (d) file
   paths and module names that may have moved or been deleted.

**Start with these five, because they are the load-bearing ones.** Report each explicitly even if
it confirms:

- `README.md` states a status for the twelve-assertion certification (`A1`…`A12`) and for whether
  "the instruments are wired". **Read `factory/certify.py`, `factory/contract.py` and
  `tests/test_connector_contract.py` and say what the code actually supports.** If the README and
  the code disagree, that is D0's first row.
- The documents claim a negative control exists proving the evaluator can fail. **Find that test.
  Name the file and the assertion.** If you cannot find it, say `UNVERIFIABLE` — do not assume.
- The documents describe a blueprint format where "the config IS the version". **Read
  `factory/blueprint.py` and `blueprints/*.yaml`** and say whether the format supports that claim.
- The documents reference an eval corpus behind a checksum manifest. **Read `evals/` and report how
  many recorded runs it actually holds.** The count matters more than the mechanism.
- `docs/absorption-backlog.md` lists AB-01…AB-19 as unactioned. **Check `.data/tasks.jsonl` and the
  git log** for evidence any of them were since closed. An item closed in the store but open in the
  document is exactly the divergence class this deliverable exists for.

**Then extend the other deliverables with what browsing showed you:**

- **D1** — an AB item with code behind it is `DO` with the smallest remaining step named; one whose
  mechanism already exists is `MERGE` or `REJECT`, and say which file made you decide.
- **D2** — class a node `built` only if you *read the code*. A node you inferred from prose is
  `proposed`. State, under each diagram, which nodes you verified and which you assumed.
- **D3** — an optimisation that the code already implements is worthless. Check first, and say
  where you checked.
- **D4** — every ticket cites the file its work touches. A ticket with no repository anchor is a
  guess and will be dropped.

**Do not clone, fork, run, or modify anything.** Read only. Also: do not report the repository's
history as evidence of current state — a deleted file is not a feature, and a commit message is a
claim, not a measurement.

---

## When the answer comes back

1. **Verify before ingesting.** Every `OBSERVED` claim cites a file and section — check a sample
   against the real file. An external model with no filesystem cannot be trusted on file contents,
   and misattributed citations are the known failure mode.
2. **Load D4 directly**: the JSON is shaped for `factory.tasks.TaskStore.create()`.
3. **Treat D2 diagrams as proposals** until the `built` classing is checked against what exists.
4. **File D1 rejects in writing** — a rejected AB item is closed, not ignored, and that is the
   point of the backlog.
