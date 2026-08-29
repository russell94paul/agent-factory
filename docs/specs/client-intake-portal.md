# Client intake portal — design, 2026-08-29

Readout: https://claude.ai/code/artifact/0b01e843-cb59-4fdc-bee9-cecfbb0d1909

Status: **design only.** Nothing here is built. Paul asked for a brainstorm; this is the record of
what was decided, what was measured, and what was deliberately deferred.

## The three decisions Paul made this session

| Question | Answer | Consequence |
|---|---|---|
| Does a non-engineer open it? | **Internal now, client-facing path designed in** | §7 of `product-end-state.md` is *deferred, not resolved* — see the tripwire below |
| What is the first slice? | Contract-authoring — **the client's answers ARE the contract** — plus an assisted layer so the client is never asked to invent an answer | Slices 1–2 below |
| Where does an answer land? | **Internal ticket in our own UI**, which then creates a linked Jira issue | Our record is the original; Jira is a projection |

## The finding that reframed the build

The questions already exist. `aldc-launchpad/docs/evidence/client-a-intake/` holds a triaged, machine-readable
intake store for one real client:

```bash
cd aldc-launchpad/docs/evidence/client-a-intake
python -c "import json;d=json.load(open('triage.json'));r=d['rows'];print(len(r), d['counts'], sum(1 for x in r if str(x.get('question_for_client') or '').strip()))"
# 36 {'UNDERSPECIFIED': 21, 'DUPLICATE': 7, 'RESEARCH': 5, 'SHIPPED': 2, 'NOT_A_TICKET': 1} 25
```

- **36** client requests triaged; **21 UNDERSPECIFIED** (58%) — they could not become a ticket.
- **25 of 36** already carry a drafted `question_for_client`.
- **9 drafts**, all 9 carrying a `blocking_question`.
- **0** have a surface the client can answer in.

⭐ **The portal is a render target for a question store that already exists**, not a new
question-authoring capability. Designing it as a blank questionnaire rebuilds the finished half.

## The second join point — the form IS `ConnectorTarget`

`factory/connector_contract.py` defines `ConnectorTarget` with a block commented `# canary
expectations`. **A9 (semantic invariants) reads its entire meaning from that block**, and every
field in it is a question a client can answer in a sentence:

| Field A9 reads | The client's question |
|---|---|
| `required_keys` + `key_column` | which accounts/markets must *all* appear |
| `non_null_positive` | which numbers may never be blank or negative |
| `primary_key` | one row per *what* |
| `date_column` + `run_date` | which column is the reporting date |
| `expect_rows` | is an empty day ever legitimate |
| `allowed_tenants` + `tenant_column` | whose data may land here (A12) |

**Generate the form from the dataclass, never by hand** — same rule `factory/board.py` states about
boards (verified: its docstring records a hand-typed board that drifted). Then adding an assertion
adds a question, and the form cannot ask for something nothing checks.

## ⛔ The load-bearing rule — unanswered is NOT-RECORDED, never a default

Proven in our own code. From A9, above the completeness check:

> *"Found by calibration: with this list empty, A9 passed a partial extraction that had dropped an
> entire account."*

An unanswered question and a declared "no constraint" both produce an empty list. Collapsing them
made a green verdict out of a broken load. So every control is **three-state**:

1. **Declared** — compiles to a live assertion.
2. **Declared not-applicable** — a real, different answer; compiles to a recorded exemption.
3. **Unanswered** — emits *no value at all*; the contract reports `UNMEASURABLE`.

And every cell carries provenance. Only the first two compile:

| Provenance | Compiles to |
|---|---|
| `CLIENT-DECLARED` / `CLIENT-CONFIRMED` | live assertion |
| `PROPOSED-UNANSWERED` (probe, chat or precedent drafted it) | `NOT_RUN` |
| `INFERRED` | `UNMEASURABLE` until confirmed |

**A proposal is never an answer.** If a pre-filled suggestion becomes a live assertion because nobody
unticked it, the portal manufactures consent and then certifies against it.

## Making it seamless (Paul's follow-up) — propose, never interrogate

Elicitation runs **backwards from the outcome**, not forwards from the schema. Three aids, all of
which write `PROPOSED-UNANSWERED` and nothing else:

1. **Probe-grounded options** — offer the source's *actual* observed fields with sample values.
2. **A goal box that drafts rows** — "weekly spend by campaign, by channel, six markets" drafts
   `primary_key` / `required_keys` / `non_null_positive` as proposed rows; the transcript is retained
   as the reason each row exists.
3. **Precedent** — prior contracts from similar connectors, with their source named.

Feasibility answered at the moment of asking, with three verdicts that must never collapse:
`AVAILABLE` (observed in a probe, with its date) · `ABSENT` (probed, not there) · `UNPROBED` (we have
not looked). An `ABSENT` on day one is the "realising some missing values/fields" moment moved from
week six to minute five.

## The boundary, inherited from `factory/evaluator.py`

**The client authors the expectation and never the verdict.** There must be no field anywhere in the
portal through which a client can influence their own grade — the same property `Submission`'s
three-field vocabulary enforces on the agent. The verdict crosses back rendered in the client's own
sentence: *"you asked that all 6 markets appear — 6 of 6 landed, 0 nulls."*

Contracts are frozen and hashed as **v*n***. A run certified against v3 while the client is on v5 is
its own verdict — `CERTIFIED-AGAINST-SUPERSEDED` — not a pass and not a failure.

## Where it lands — decision capture already exists

Measured across `clients/CLIENT-A/tickets/*/artifact.yaml` (2 tickets): **2 of 2 carry populated
`decisions`** (8 total), 1 carries a change request.

```bash
cd clients && python -c "
import pathlib,yaml
for f in sorted(pathlib.Path('CLIENT-A/tickets').glob('*/artifact.yaml')):
    d=yaml.safe_load(f.read_text(encoding='utf-8')) or {}
    print(f.parent.name, len(d.get('decisions') or []), len(d.get('change_requests') or []))"
```

⚠ **Corrects the 2026-08-29 boot prompt**, which recorded `decisions` and `change_requests` as
"both unused" and the ticket count as 3. GP-199's entry reads *"Client (Justin Shuster) approved
Approach A via email 2026-05-01"* — it already records **who approved, through what channel, on what
date**. The portal makes that line the product of a click rather than a transcription, and the
channel becomes `via portal`, which is the difference between a claim and a receipt.

Object model, and the nearest existing thing for each:

| Object | Nearest existing thing |
|---|---|
| Engagement (carries `tenant_id`) | — |
| Request (client's words + triage verdict) | `triage.json` rows ✅ exists |
| Question (+ answer, + provenance) | `question_for_client` ✅ exists |
| Contract v*n* | `ConnectorTarget` ✅ exists |
| Decision | `artifact.yaml: decisions` ✅ in use |
| Ticket (holds the Jira link) | `drafts.json` ✅ exists |
| Verdict | `certify` + evaluator service ✅ exists |
| Artifact | REGISTRY.md — 26 in gallery, 8 with no source, 13 orphaned |

Side benefit: giving artifacts an engagement to belong to is the cheapest fix on the table for the
8 sourceless / 13 orphaned artifacts.

## Tenant-shaped now, client-facing later

**Day one, near-free:** `tenant_id` on every row including internal ones; every read through one
`who_am_i()` returning the single internal principal; question text written for a non-engineer from
the start; no engagement-scoped query that bypasses the tenant filter.

**Deferred, correctly:** auth, per-client isolation testing, an auditable access log, session
management, and the higher bar a green verdict must clear in front of a paying client.

⛔ **Tripwire — write this beside the code.** `product-end-state.md` §7: if a non-engineer ever opens
a surface, the approval plane is a *product* surface, not an internal one — an architecture change,
not a feature. **The moment anyone proposes sending a portal link to a client, that reopens §7.** It
is not a deployment task.

## Five ways this ships broken

1. **A silent default becomes a promise** — the A9 defect at the source instead of the sink; same
   shape as the `COALESCE` that would have published "$0 ad spend" across 23 marketplaces whose true
   verdict was NOT-RECORDED.
2. **A proposal counted as consent.**
3. **`UNPROBED` rendered as available** — a feasibility answer from an instrument not proved able to see.
4. **Progress theatre** — a stage bar that moves because someone typed. Today's `stage_history` has
   dates not times and no event citation; a transition must name the event that caused it.
5. **A green light against a superseded contract.**

## Build order

| Slice | What | Status |
|---|---|---|
| 1 | One answer → one assertion; **prove it can FAIL** | unblocked |
| 2 | Render the 25 existing questions; answers write back with provenance | unblocked |
| 3 | Probe-grounded feasibility | ⛔ **BLOCKED** |
| 4 | Chat drafts proposed rows | after 1–2 |
| 5 | Shell, progress, Jira link | after 1–2 |

⛔ **Slice 3 is genuinely blocked**, not merely unstarted. It needs observed field lists from real
connector runs, and `agent-factory/evals/corpus/` holds exactly one fixture
(`windsorai-2026-08-20.json`) which §2(b) of the boot prompt shows cannot be broadened from disk.
Synthesising it would make every feasibility answer a `PROXY` wearing a measurement's clothes.
Slices 1 and 2 do not depend on it.

## Honesty note on which bottleneck this attacks

The portal attacks the **client-response** bottleneck (the CLIENT-A domain). It does not attack the
connector-delivery bottleneck, whose measured shape is different: one migration was **21.6 minutes of
active stage time inside 8 h 20 m of wall clock — 4.3%** (`MEASURED`, `docs/specs/product-end-state.md`).
Two domains, two bottlenecks. Recording this now prevents the portal being judged later against a
problem it was never aimed at.

## Open — Paul's calls, not mine

- **Does an answer bind?** If the client declares "spend is never null" and it is null at source, the
  contract says FAIL either way — but the portal must render *"the connector is wrong"* or *"the
  expectation was wrong"*, and those are different conversations.
- **Does the client see red?** A visible failing assertion is both the transparency that makes the
  portal valuable and the thing that generates a phone call. Commercial call.
- **Jira issue per request or per contract?** 36 requests produced 9 drafts; one ticket per answered
  question would produce 25 — probably wrong.
- **Which engagement is slice 2 aimed at?** The 25 live questions belong to one real client. Pointing
  slice 2 at that real backlog validates the portal against real content on day one.

**Recommendation for next session:** slices 1 and 2, both unblocked, both against the real
`triage.json` rather than a fixture.
