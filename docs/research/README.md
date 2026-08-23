# Research — the run order, and the border between each pass

Paul runs these in ChatGPT Deep Research (or equivalent) and files the answers back here. They
exist because the team design is a load-bearing decision with no method behind it, and guessing it
and then measuring it with an instrument we also guessed is how you get a confident answer nobody
checked.

**Live state is `python -m factory.dispatch`, never this file.** The table below says what each
pass is *for*; the instrument says where each one *is*.

---

## 1. The order

```
DONE ─────────────────────────────────────────────────────────────────────────
  R1  eval harness            R2  topology             R3  control plane
  R4  agnostic optimiser      R5  build velocity       R6  automation/alerting
  R7  session manager        R10  wiki training       R11  concept diff
  R12 session substrate

IN FLIGHT ────────────────────────────────────────────────────────────────────
  R8   data-engineering factory + sandboxes      dispatched 08-23, with a 500 KB evidence pack
  R13  the option space: architectures, stacks, latency, approval, provenance
  R14  our own structure, the object model, and the design brief

NEXT TO SEND ─────────────────────────────────────────────────────────────────
  R15  the repository corpus — read the field's SOURCE, then what to fix in ours first

WITHDRAWN ────────────────────────────────────────────────────────────────────
  R9   game-styled supervision UI — dropped 2026-08-23. If an answer arrives, DISCARD it.
       Filing it would make `synthesis` report an answer to a question that no longer exists.
```

### The only hard ordering left

**R3 was the one strict dependency** (it asks how to search a configuration space, and R2 decides
what that space contains) and both are answered. **Nothing among R8, R13, R14 and R15 blocks
anything else** — they read different literatures and different evidence, and serialising them
would cost days for a coupling better handled as a follow-up question in the existing thread.

**So R15 can go now, alongside the three in flight.**

### What the order is really about — acting, not sending

The sequence that matters is not the dispatch order, it is what you do when they land:

```
1.  SETTLE THE TERMINAL QUESTION           ← blocking, and it is a decision, not a research task
2.  R15 §5.0 — fix what we built badly     ← BEFORE any UI work. A new interface over a weak
                                             substrate is a prettier way to be wrong
3.  R13 + R14 + R15 §5.2 — the UI          ← reconcile the three into one position
4.  Then build
```

⛔ **Do not settle the terminal question by taking whichever answer arrives first.** It has been
answered by accident twice — once by a pass restating our own position back to us, once by a pass
that was never told the rule existed. It is stated as an explicit open question in R8, R13, R14 and
R15 precisely so none of them resolves it silently.

---

## 2. The border — what each pass owns, and what it must refuse

The expensive failure in this programme is **two passes answering the same question differently**,
which costs a run and then costs a reconciliation. Every prompt from R12 onward carries a
neighbours table for this reason. The lines:

| Pass | Owns | Must NOT answer |
|---|---|---|
| **R11** | which *concepts* other factories make first-class — vocabulary and framework taxonomy | anything about our code, or which tool to use |
| **R12** | the session-management **substrate**: identity, liveness, attach-vs-resume, the blocked-question channel | the presentation layer; the skin |
| **R13** | the **option space** — orchestration patterns, desktop stacks, latency techniques, approval and provenance **as categories**, reasoned from the literature | our own module structure; and it does not read repositories one by one |
| **R14** | **inward**: is our decomposition right, is the object model right, and the **design brief** — IA, hierarchy, colour, motion, delight | UI stack benchmarking (R13's), vendor concept surveys (R11's) |
| **R15** | **outward, from source**: what people actually built, read repo by repo, extracted to one comparable schema — then what to fix in **ours** first | weighing stacks in the abstract (R13's), or re-surveying framework taxonomies (R11's) |
| **R8** | data-engineering as a domain: the downstream oracle, blast radius, credentials, the isolation ladder | the interface, beyond its own §2.6 strand |

⭐ **The R13 / R15 line is the one most likely to blur, so it is stated in both:** R13 asks *"what
are the options and what does the literature say"*; R15 asks *"what did people actually build, and
what does their code prove is achievable"*. Weighing Electron against Tauri in the abstract is
R13's. Reporting that a named repository ships an Electron app whose renderer cold-starts in N ms
and whose file-watch drops events on Windows is R15's.

**Every prompt is told: if a question belongs to a neighbour, say so and stop, rather than
answering it thinly.** A named handoff is worth more than a thin answer.

---

## 3. Rules that keep the record honest

### ⚠ Every R-series file lives in THIS repo — regardless of which repo the question is about

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

**Proven, not hypothetical:** R10 was written into `aldc-launchpad/docs/research/` on 2026-08-22 and
moved here on 08-23. Its own header told the reader to file the answer at the *relative* path
`docs/research/answers/…`, a directory that does not exist in launchpad — so following the prompt's
own instruction would have put the answer somewhere no instrument reads.

R8 asks about `prefect-connectors`; R10 asked about the `wiki`; R15 reads other people's
repositories entirely. All of them live here anyway.

### A generated evidence pack is not a prompt

`R8-evidence-pack.md` and `R13-evidence-pack.md` are **generated and gitignored** — rebuild with
`scripts/build_r8_pack.py` and its R13 equivalent before dispatch, and scan them before upload,
because they leave the building. They match the `R[0-9]*.md` glob, so `dispatch.prompts()` and the
tracker exclude `*-evidence-pack.md` explicitly. Before that exclusion existed the real prompt won
**by alphabetical luck alone**.

### Add a run-log row every time you dispatch

Every prompt carries one. `dispatch` reads a status line and whether an answer file exists, and by
its own account **cannot see whether a prompt was ever actually pasted anywhere** — so without the
run log, "which did I send, and when?" is not answerable from disk. R1–R7 say `NOT-RECORDED` for
their send dates because they predate the convention, which is not the same as never sent.

### File the raw answer, do not summarise it

The raw answer is the artefact, and the disagreements between passes are the most useful part.
`scripts/file_answers.py` names them by content — a filename is a claim about content, and this
project has already had two answers arrive with their contents **swapped**. It refuses to guess.

### Then reconcile

`SYNTHESIS.md` is the decision record. `tests/test_synthesis_current.py` goes **red** while any
filed answer goes unmentioned — that is the gate working, not a problem to silence. Where a new
answer disagrees with an earlier one, or with something already built, **record the disagreement
and which evidence is stronger. Do not average them.**

---

## 4. Open questions for Paul, not for the researcher

1. **The embedded terminal** — see the ⛔ above. This is the blocking one.
2. **Which Navira account ids are in scope?** Blocks the tenancy assertion, and therefore blocks
   certification of the one green connector.
3. **Is the landing table one account or two?** 20 rows across 18 campaigns on one date cannot be
   unique on `(account_id, campaign_id, date)`. If it is one account, the declared primary key is
   wrong and the calibration world is built on a mistake.
