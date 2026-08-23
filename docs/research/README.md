# Research — three prompts, in order

Paul runs these in ChatGPT Deep Research (or equivalent) and sends the answers back. They exist
because the team design is a load-bearing decision with no method behind it, and guessing it and
then measuring it with an instrument we also guessed is how you get a confident answer nobody
checked.

| # | File | Question | Order |
|---|---|---|---|
| R1 | `R1-eval-harness.md` | Grade the eval harness we built; what did we get wrong? | first |
| R2 | `R2-topology.md` | One agent or a team — and is our 3-role sketch defensible? | any time |
| R3 | `R3-control-plane-and-optimizer.md` | Bounding, orphan reaping, sandbox, tenancy — optimizer last | ready now |
| R4 | `R4-agnostic-optimizer.md` | Can it work on *any* repo? Fitness discovery, transfer, prior art | parallel with R3 |

**Only one hard ordering: R3 last.** R3 asks how to search a configuration space, and R2's topology
decides what that space contains — so R3 written before R2 lands would search the wrong thing.

**R1, R2 and R4 are standalone and should be run in parallel.** Every fenced block carries its own
context and none references another's output. An earlier version of this file said R1 -> R2 -> R3
strictly; that overstated it and would have cost days of serialised Deep Research runs for a
coupling better handled as a follow-up question. Once R1 lands, ask in the **R2 thread**: *"R1
concluded [X] about what makes agent work measurable — does that change your recommendation on team
composition or the tester role?"* R1 shapes how we would measure whether a team wins; it does not
change what the literature already reports.

**R4 runs in parallel with R3.** Different literature — R3 asks how to search and how to bound it,
R4 asks whether the thing being searched can be made repo-agnostic at all. Neither depends on the
other. R4 also covers the prior art the first three miss: DSPy/MIPROv2, GEPA, TextGrad, Trace,
OpenEvolve, AlphaEvolve — the closest existing work to an agent-config optimizer, which R3 asks
about only obliquely via `autoresearch`.

**Each file is standalone.** Copy everything inside the fenced block — it carries its own context,
its own measured figures, and its own constraints. Nothing outside the fence needs to go with it.

## Save answers here

```
docs/research/answers/R1-answer.md
docs/research/answers/R2-answer.md
docs/research/answers/R3-answer.md
docs/research/answers/R4-answer.md
```

Then tell Claude which have landed. Do not paraphrase them into a summary first — the raw answer
is the artefact, and the disagreements between the three are the most useful part.

## ⚠ Every R-series file lives in THIS repo — regardless of which repo the question is about

Prompt and answer both, always `agent-factory/docs/research/`. Not launchpad, not the repo the
question happens to concern. This is not tidiness — it is the only place the instrument can see:

```python
# factory/synthesis.py
RESEARCH = <agent-factory>/docs/research
ANSWERS  = RESEARCH / "answers"
filed()  = glob ANSWERS/"R[0-9]*.md"
```

`filed()` globs exactly one directory. An answer filed anywhere else can never appear in
`unsynthesised()`, so `tests/test_synthesis_current.py` can never go red for it — the pass gets a
permanent free ride from the currency gate, and a research record that silently omits a landed
answer is the failure this programme exists to prevent.

**Proven, not hypothetical:** R10 was written into `aldc-launchpad/docs/research/` on 2026-08-22
and moved here on 08-23. Its own header told the reader to file the answer at the *relative* path
`docs/research/answers/…`, a directory that does not exist in launchpad — so following the prompt's
own instruction would have put the answer somewhere no instrument reads.

R8 asks about `prefect-connectors`; R10 asks about the `wiki`. Both live here anyway.

## What is in them that was not in the 2026-08-20 draft

The original prompts (`agent-factory-research-prompts.md`, kept for its Part 0 reasoning) were
written before the contract existed and before the pipeline had been measured. These three carry:

- **R1 asks for a critique, not a design.** The GreenContract is built — 12 assertions, four
  verdicts, a mutation registry, calibrated on a real run. R1 hands over the six design decisions
  and asks which are sound, which are folklore, which are harmful. A "here is what we built, grade
  it" prompt returns more actionable output than "how would we build one".
- **All three carry the 2026-08-21 measurements** — 1,001 failures against 165 completions, 3 of
  14 runs finishing, 22 gate events with zero refusals, 5 of 7 gates with no check, 352 restarts
  of a single stage, cost recorded only on success. These did not exist when the drafts were
  written and they are the strongest evidence in the prompts.
- **Every figure is marked `[M]` measured or `[R]` inherited-and-not-re-verified.** The `[R]`
  figures come from `prefect-connectors/docs/AUTORESEARCH_REVIEW.md` (the 49 modules / 59% import
  failure at lines 122 and 128, the 976 failures, the 233-diagnoses agent, the 965-run loop). They
  are real but were not re-measured on 2026-08-21, and the prompts tell the researcher to treat
  them as weaker.
- **Each prompt gives permission to say "build less".** R2 can conclude one agent beats a team;
  R3's first deliverable is a yes/no on whether to build the optimizer at all. A research answer
  that validates everything we sketched would be a wasted run.

## Two things deliberately NOT asked

- **Nothing about the UI, the "agentic gym", agent-army tiers, or the ten team types.** Part 0 of
  the original review argued that six of those items are downstream of the eval harness and cannot
  be specified before it exists. That argument still holds.
- **Nothing that needs a credential.** These are literature questions. No Snowflake, Prefect or
  vendor secret is involved in answering them.

## Open questions for Paul, not for the researcher

1. **Which Navira account ids are in scope?** Blocks the tenancy assertion, and therefore blocks
   certification of the one green connector.
2. **Is the landing table one account or two?** 20 rows across 18 campaigns on one date cannot be
   unique on `(account_id, campaign_id, date)`. If it is one account, the declared primary key is
   wrong and the calibration world is built on a mistake.
3. **Which Jira ticket does this work belong to?** Nothing in either repo records one.
