# Approved concepts

Agent Army concepts that have been **accepted for product development** in this repository.

## Status: none

**No Agent Army concept has been approved for implementation.** This table is empty on purpose,
and an empty table is the correct output today rather than a gap to be filled.

| CONCEPT | DECISION DATE | SUPPORTING RESEARCH | ADR | OWNER | IMPLEMENTATION STATUS |
|---|---|---|---|---|---|
| _(none)_ | — | — | — | — | — |

## Why it is empty

⚠ **Corrected 2026-08-30.** Items 1 and 2 below previously read *"contains no answers — all 29
`NOT_RUN`"* and *"`research/synthesis/` is empty"*. **Both are now false — Wave 0 has run.** The
table is still empty, but for reasons 3 and 4, which is a different and much sharper statement.
`MEASURED`:

```bash
cd ~/repos/agent-army-research
ls research/answers/*.md | wc -l                     # 3   (R00, R01, R02)
ls research/synthesis/*.md | wc -l                   # 1   (W0-foundations.md)
ls research/prompts/*.md | wc -l                     # 26  (R20-R45)
grep -c NOT_RUN research/RESEARCH-MANIFEST.yaml      # 27
```

Approval requires four things. **Two now exist; two still do not:**

1. ✅ **A research answer.** Three: `R00`, `R01`, `R02`. ⚠ Each carries an
   `independence_declaration` recording that it ran as **local subagents, not an external model** —
   weaker on independence, stronger on file-and-line claims. Weight accordingly.
2. ✅ **A synthesis.** `research/synthesis/W0-foundations.md`. ⭐ **It falsified the programme's
   founding premise** — AOE is organisation-oriented MAS, the category name is occupied twice
   (arXiv:2602.13275, arXiv:2607.25446), and the novelty claim is refuted on all four components.
   Its own instruction: *"Do not apply these until a human accepts this synthesis."* A synthesis
   that demolishes is still a synthesis, and it has already paid for itself — finding C4 became
   commit `0d4bdb1`, the fifth verdict.
3. ⛔ **A decision.** ADR-0001..0007 in the research repo are *research* ADRs — they record how the
   programme will work (separate repo, event log as source, no random agent animation, offline-first
   evolution). None of them approves a product change here.
4. ⛔ **The product precondition.** `README.md` gates Agent Army work on *"one certified team, plus
   evidence a tier helps"*. No team is certified. `blueprints/orchestrator_team.yaml` is the one
   multi-agent team that was designed, and it was **rejected on evidence** — see
   [CURRENT_STATE.md](CURRENT_STATE.md) §"The finding that matters most".

Point 4 is independent of points 1–3. Even a fully synthesised, ADR-backed research conclusion
would still meet the certified-team gate in this repository.

## What approval requires

An entry may be added here only when **all** of the following exist:

```text
research answer          agent-army-research/research/answers/R__-answer-*.md
evidence audit           applied to that answer
wave synthesis           research/synthesis/W_-*.md
canonical spec updated   ontology/ | architecture/ | governance/
architecture decision    an ADR that decides, not one that describes
approved handoff         implementation-handoffs/approved/*.md
```

Then, and only then, add a row here and a matching row in
[IMPLEMENTATION_HANDOFFS.md](IMPLEMENTATION_HANDOFFS.md).

## Row format

| Field | Rule |
|---|---|
| `CONCEPT` | The specific mechanism, not the theme. "Typed organizational events", not "observability". |
| `DECISION DATE` | The date the ADR was accepted. Absolute, never relative. |
| `SUPPORTING RESEARCH` | Path to the **synthesis**, not to a raw answer. One answer is not a basis. |
| `ADR` | Path to the ADR. An approval with no ADR is a preference. |
| `OWNER` | A person. "The team" is not an owner. |
| `IMPLEMENTATION STATUS` | Must match [CURRENT_STATE.md](CURRENT_STATE.md). If they disagree, CURRENT_STATE is right — it cites code. |

## What must never appear here

- A concept that reads well in `architecture/` but has no answer behind it.
- A concept approved because it is already half-built. That is a `PARTIAL` row in
  [CURRENT_STATE.md](CURRENT_STATE.md), and back-filling approval to match code inverts the flow
  this directory exists to protect.
- A whole research wave. Approval is per mechanism, so it can be reversed per mechanism.
