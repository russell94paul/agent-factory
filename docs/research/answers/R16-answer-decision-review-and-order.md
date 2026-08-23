# R16 — the eighteen decisions, attacked

**Answered 2026-08-23, from the repository and the answers directory, not from the synthesis.**
Every claim below cites a file and a line, or the answer file it came from.

**Tiers, per §5.** `OBSERVED` — I read the source, the answer, or ran it · `REPORTED` — a credible
write-up · `MARKETED` — a vendor says so · `INFERRED` — my reasoning. Nothing here rests on a
`MARKETED` claim, and I have cited no fact about your operators that was not supplied.

⛔ **Independence disclosure, and it is worse than the brief assumes.** The brief was written
expecting an outside model. I am a Claude subagent running inside this repo, on your estate, with
your conventions in front of me. Every pull is toward agreement. I compensated by going to the cited
answer first and forming a verdict before reading what §12–§14 concluded from it, and by re-deriving
every number I could rather than quoting one. That worked for the figures. It cannot fully work for
judgement, so weigh my file-and-line claims as strong and my ordering as partial — exactly as you
weighed R13 run 2 and R14.

**Headline.** Three of the eighteen actions carry a `gate=` edge, and the roadmap's own docstring
says a gated action is the credible kind because its status is `MEASURED` rather than `AUTHORED`.
**All three edges are wrong**, and one of them points at a probe that is structurally incapable of
passing because of a control character committed at `factory/readiness.py:870`. The number that
probe emits — **"0 of 15 dimensions"** — is in four documents, is load-bearing in two arguments, and
is false. The true value is **6 of 15**.

---

## 1. ⭐ The stale and unsupported figures (deliverable c)

### 1.1 "0 of 15 dimensions" is not stale. It is wrong, and the instrument cannot say otherwise.

`OBSERVED`, from the raw bytes of `factory/readiness.py:870`, committed at `HEAD`:

```python
have = [d for d in VERSION_DIMENSIONS if re.search(rf"\x08{d}\x08", body)]
```

Those are **literal U+0008 backspace characters**, not the two-character escape `\b`. Someone wrote
`f"\b{d}\b"` without the `r` prefix, Python resolved `\b` to a backspace, and the file now stores the
control character itself. `sed`, `inspect.getsource` and every editor render it as nothing, which is
why four readers have quoted the output and none has questioned it.

A backspace cannot occur in a Python source file. **The pattern can never match. The gate can only
ever return `0 of 15`, and can only ever FAIL.** Verified by spying on `re.search` inside the live
call — fifteen patterns, fifteen `hit=False`, against a body of 2,312 bytes that demonstrably
contains `prompt` at offset 70.

With the intended word-boundary regex the answer is:

```
6 of 15  —  prompt, model, effort, tools, max_turns, budget_usd  present in factory/blueprint.py
9 missing — tool_implementation, sandbox_image, model_routing, context_policy,
            external_knowledge, permissions, contract_version, harness_version, side_effect_replay
```

The comment at `readiness.py:857-862` marks those first six *"# we have these"*. **The instrument
disagrees with the comment sitting three lines above it, and nobody noticed, because the instrument's
answer was the one that felt right.**

Where the wrong number travelled:

| Document | Use |
|---|---|
| `SYNTHESIS.md` §14.5 | *"directly actionable against the config hash covering 0 of 15 dimensions"* — the basis for action a16 |
| `R13-answer-…-run2.md` §1 | *"Option E (provenance UI) is **blocked** on its own prerequisite — the version hash covers 0 of 15"* — load-bearing |
| `R14-answer-…` §5 | *"the version hash covers 0 of 15 dimensions… Build the fifteen dimensions; do not rename the zero"* — load-bearing |
| `ui-surface-inventory.md` §9 item 2 | listed as one of three things nobody else ships |

Neither conclusion flips — the hash is still incomplete and `contract_version` is still among the
missing — but **the size of the job is nine dimensions, not fifteen**, and a repo whose thesis is
that a green from an instrument that cannot refuse is worthless has been publishing a red from an
instrument that cannot pass. `readiness.py:88-97` already names that as an equal defect.

The same bug is in one more place: `scripts/file_answers.py:74`, `r"\x08ADK\x08"` where `\bADK\b` was
meant — one scoring term in the router that files these answers is dead. `OBSERVED`; repo-wide sweep
found exactly these two.

### 1.2 F77's correction reached §13.5 and never reached §13.7.1

`SYNTHESIS.md` §13.5 says the 1.2 s figure was *"Wrong by about eight times"* and explains why.
**Eleven lines later, §13.7.1 still reads *"thread the server and parallelise the probes, 9.3 s →
~1.2 s, ~30 lines."*** `OBSERVED`. The correction and the uncorrected action are in the same
document, two sections apart, and only `factory/roadmap.py:73-79` carries the fix.

That is not a stale number surviving by accident. It is **the drift mechanism itself, reproduced
inside the record**: the finding lands in the analysis section, the decision list is not rewritten,
and the decision list is the thing anyone acts from. Ask how many others did — that is exactly the
right question, and §1.1 is the answer.

### 1.3 The 30–45 minute target is a tail statistic wearing a target's clothes

`R8-answer-…` §3, question 4 (`OBSERVED` in the answer): *"The **Anthropic study** on Claude Code
found that 99.9th-percentile autonomous turns lasted ~45 minutes; the median was <1 minute."* No
link, no citation. §13.3 labels it `REPORTED`, which is honest.

Two problems the label does not cover.

1. **A p99.9 of an observed distribution is not a ceiling of the feasible.** It describes the tail of
   what people happened to do. Adopting it as a *target* converts an observation about behaviour into
   a claim about capability — the same move as reading a zero off an instrument you have not proved
   can see.
2. **The unit changed on the way in.** R8 measured *turns*; a10 restates it as an unbroken *run* of a
   connector migration. Those are different quantities. For contrast, your own recorded lanes ran
   1.7 h, 19.4 h and 31.5 h of wall clock (`.data/runs.jsonl`, basis `MEASURED`) — a third quantity
   again, which is precisely why the unit has to travel with the number.

### 1.4 Two smaller ones

- **a7's "27.3 s cold to 0.84 s warm — measured".** `R13-answer-…-run2.md` NOT-SUPPLIED is explicit:
  *"REPORTED by the operator, not re-measured by me."* The roadmap note says "measured" and names no
  measurer. Small, but this programme's rule is that a figure carries its basis.
- **a2 undersells what shipped.** The action and its note say **four** liveness states.
  `factory/sessions.py` defines **five** — the fifth is `UNKNOWN-INSTRUMENT-BLIND`, *"The process
  table could not be read. NOT the same as 'nothing is running'"* (`sessions.py:130-131`, `OBSERVED`).
  That fifth state is the one R12 never proposed and the one carrying the ZERO-vs-NOT-VISIBLE
  discipline. The record is stale in the direction of modesty, which is rarer and still worth fixing.

---

## 2. ⭐ The incoherences, ranked

### 2.1 All three gate-linked actions are wired to gates that cannot decide them

This is the most serious finding in this pass, because `factory/roadmap.py:19-22` claims the exact
opposite property: *"An action linked to a gate takes its status FROM the gate, always… that
asymmetry is the whole design: it makes the hand-maintained part visibly hand-maintained instead of
letting it borrow the credibility of the measured part."*

Three actions carry a gate. `OBSERVED`:

| Action | Gate | What the gate actually measures | Consequence |
|---|---|---|---|
| **a8** "Containerise **agent execution** on one machine" | `isolated` | `g_evaluator_is_a_service` — whether `$AGENT_FACTORY_EVALUATOR` is set and a module other than `readiness.py` defines `class EvaluatorClient` | Set one env var and add a client class and **a8 renders SHIPPED with zero agents in containers** |
| **a10** "Restate the unattended goal as a 30–45 min unbroken run **in the readiness set**" | `finishes` | `g_finishes` (`readiness.py:204-224`) — counts runs reaching `pipeline_completed` in the window. **No duration term anywhere** | a10 is an action to *change this gate*, gated on the *unchanged* gate. Circular, and it flips SHIPPED on runs of any length |
| **a16** "Config hash: adopt the OTel GenAI field set" | `version` | `g_version_hash_is_complete` — **structurally cannot pass** (§1.1) | a16 is pinned at DECIDED forever regardless of what is built |

`_validate()` (`roadmap.py:142-165`) checks only that a named gate *exists*. The module's own
docstring concedes this — *"validation only proves an edge resolves, never that the judgement behind
it is right"* — and then the judgement behind all three is wrong. **The half of the roadmap presented
as MEASURED is the half that is unreliable**, which is the inverse of the design intent and, on your
own standing rule, worse than an admitted gap.

**What to do:** drop the edges on a8 and a10 and let them render AUTHORED, which is the honest basis;
fix `readiness.py:870` before touching a16; and add the probe R14 §2.3 already specified — one that
asserts an authored edge's *subject* matches its gate's *question*, because today nothing does.

### 2.2 a14's own citation is contradicted by the two passes that landed after it

a14: *"Build the notification channel first — three passes and one measurement agree."*

R13 run 2 and R14 both landed today, after §14.7 was written, and **both refuse it**, independently
and for different reasons:

> `R13-…-run2.md` §5, refusals: *"(3) any bespoke notification daemon before measuring whether
> GitHub's own notification fired."* And §3: *"Nobody has established whether those 6–9 days were
> **no notification sent** or **notification sent and ignored**. That is NOT-SUPPLIED by the pack, and
> it decides the entire remedy. Building a bespoke queue to fix an unmeasured notification failure is
> the wrong-layer deploy this estate has a standing rule against."*

> `R14-answer-…` §7.1, refusals: *"**Alerting before the `Decision` object exists.** An alert on an
> object with no age, no state and no store is the 233-diagnoses/0-fixes shape again. Model it, then
> watch it."*

The record kept a14 unchanged. This is the brief's own worry about "landed" versus "reconciled"
coming true: R14 is named five times in `SYNTHESIS.md` and its central refusal is not among them.

**The deeper error is that "one measurement" is two measurements with different verdicts.**

| Fact | Instrument state | Verdict |
|---|---|---|
| Four agents blocked on `needs` in `jobs/<id>/state.json` | `sessions.py:252` reads the field; nothing surfaces it; R12 proved no external tool reads it either | **absence PROVEN** — build the interrupt |
| Two PRs green and waiting 6–9 days | GitHub's own notification path never checked | **NOT-MEASURED** — do not build against it |

Collapsing those into "humans are the bottleneck, build a channel" is the ZERO-vs-NOT-VISIBLE
collapse this estate has a rule about, applied to itself.

### 2.3 a3 and a14 are one piece of work, and the answers already name the object

The brief suspected this. It is true, and R14 §5 and §3.6b settle it: *"it should not be built as an
'inbox'. Build it as the **`Decision` queue**, with an agent's question as one `kind` alongside merge,
grant and promote. A separate inbox for agent questions would be the sixth surface."*

R14 §3.6b also supplies the reason this is the missing object rather than a nice one: *"Every other
plane has objects… The one plane where a human is mandatory has no type, no store, no ledger, and no
age… **The absent object and the measured bottleneck are the same thing.**"* And it names the
prototype to generalise rather than replace — `factory/operator.py`, already an answer-to-a-blocker
on disk with a timestamp and a refusal-to-converse bound (`operator.py:55-57, 72-80`).

**Merge a3 and a14 into one action: build `Decision`, generalised from `operator.py`.**

### 2.4 a1 is filed under the wrong reason, and the reason it is filed under has been superseded twice over

§12.8.1 was a *disjunction*: do not adopt **either** because the constraint is retired in writing
**or** because R12 is re-asked with it stated. a18 discharged it. `roadmap.py:55-56` therefore marks
a1 `SUPERSEDED` — which, in this module's own vocabulary, reads as *the prohibition lapsed*.

It did not. A **substantive** answer arrived in between and is not cited in a1's note: switchboard
cannot read the `needs` field the questions are written in (§12.3, R12's own §2, `OBSERVED`), and it
has no liveness concept at all — it issues `claude --resume <id>` and delegates the guard to a CLI it
cannot see (a11, R13 run 2 §4, re-verified against the raw file). Those are reasons not to adopt that
survive any decision about terminals.

Also worth stating plainly, because `roadmap.py` does not: **a1 reverses the recommendation of the
pass it cites.** R12's executive summary and §6 both say *"Adopt Switchboard"*. §12.8.1 is honest
about that (*"the recommendation is not wrong; it is unqualified"*); the action text is not, and the
action text is what `python -m factory.roadmap` prints.

**Honest state: `DECIDED — do not adopt, on evidence`, note citing a11 and §12.3.** Not `SUPERSEDED`.

### 2.5 The 7-versus-13 incoherence the brief handed me is already resolved — in an answer the record did not absorb

The brief says *"the synthesis never says, because the two were written a section apart."* It does
not need to. `R13-…-run2.md` §1 answers it directly and landed today:

- Surface 2 (the tracker): **KEEP the engine, ABSORB the emitter — last.** *"its value is
  `factory.readiness` / `board` / `lanes` as functions; the 1,894-line HTML writer is the replaceable
  half."*
- *"The extension is admissible only when it can **subtract** surface 2's emitter, not sit beside
  it"* — because `platform/master` *"did not die of Electron, of Windows, or of scope — it died
  because a second surface rendered the same idea from a source that could not go stale."*
- And §5, refusals: *"(6) **the VS Code extension, for now.**"*

So a7 is **not** throwaway: it made the engine fast, and the engine is what an extension would call.
The real incoherence is that **a13 is stated as an unconditional decision when the most recent pass
refuses to build it**, and the sequencing answer sat unread in the answers directory while §14.7 was
being written.

**Honest version of a13:** *"If a surface is built, it is a VS Code extension, not a desktop app —
and it is not admissible until it can subtract the tracker's emitter."* That is a ranking plus a
precondition, not a decision to build.

There is a second reason to weaken a13. R13 run 1's entire argument for VS Code is *"the line past
which we rebuild an IDE"* — Monaco, LSP, Git, diffs. R13 run 2 §3 then removes the plane that needed
any of them: APPROVE leaves the building and becomes a GitHub PR. DECIDE, RUN and PROVE need a gate
board, a run list and evidence text. **The justification for the platform choice evaporated with the
plane it was justifying**, and nothing in §14.2 revisits it.

### 2.6 a4 and a5 rest on an instrument a6 shows to be unreliable

R11's own summary: *"Of these, none were already present under our names (`PRESENT`) and none simply
map to our terminology (`RENAMED`)… Verdicts: `PRESENT`: 0; `RENAMED`: 0."* Across ~30 concepts.

a6 exists because that is false — `factory/runs.py` implements the observability direction R11 filed
as wholly ABSENT. R11's *only* claim about this repo (*"our `deploy.py` just writes an opaque
transcript log"*) is the one claim anyone checked, and it was wrong. R11 cites no file in this repo
anywhere.

An audit of our side that scored 0/30 and was wrong on the single item checked cannot then be the
evidence for a4 (*"record the guardrail gap as a real absence"*). **a4's conclusion is still right**,
but its evidence is not R11's vendor survey — it is your own worked example in §12.5, the
`terminate_prefect_flow_run` defect that sent CANCELLING before the ownership check. That is one
observed case of the class, from your estate, and it is worth more than nine vendor bullets.

**Honest version of a4:** cite the CANCELLING defect as the evidence; mark R11 as corroboration of
vocabulary only.

### 2.7 a15's stated reason is a sample; its real support is a convergence, and its real cause is elsewhere

*"Seven checked, none moves the cap."* Seven is a sample of a population nobody enumerated —
structurally the same move your own analysis rule forbids. The conclusion is nonetheless well
supported, and by something stronger than the note claims: **R8 §1 and R13 §1 each enumerated seven
patterns independently and converged.** Two instruments agreeing is the control.

But the cause was supplied only by R14 §3.2, and it is not in any action: **`lane` is one string
doing seven jobs** — work package, conflict key, git branch (`worktrees.py:80`), directory
(`worktrees.py:50`), claim key (`claims.py:71`), session identity (`sessions.py:143-146`), ledger key
(`runs.py:232`), bus channel (`bus.py:78`). *"Therefore two agents cannot work one lane, because the
lane **is** the branch."*

### 2.8 a8's payoff is refuted by R14, and a8 is the most expensive action on the list

R8's argument for containerising is the concurrency ceiling: *"~N… potentially 10+ on a modern
server"*. R14 §3.2 refutes it directly: *"R8's containerisation recommendation raises the ceiling
only if the branch identity is separable from the work identity; today it is not, and **no amount of
isolation changes that**. This is a modelling constraint wearing a resource constraint's clothes."*

a8 still has a real payoff — blast radius, and F53 is genuine evidence — but **it is right for a
different reason than the one recorded**, and its prerequisite (the `Workstream`/`Attempt` split) is
not on the list at all.

### 2.9 a6 is true about code and unproven about data

a6 is `SHIPPED`. The module is real and its cost figures are `MEASURED` from transcripts —
`.data/runs.jsonl` today holds three RECORDED lanes with token, cache and wall-clock figures. So the
narrowing of R11 is correct.

But R14 §7.5 found the producer disconnected, and **it is still disconnected today**:
`scripts/local_tracker.py:1838-1853` — the "run preflight & finish" button — calls
`ho.write_lane_handoff`, then `claimlib.release(lane_id)` **unconditionally, before `fails` is used
on the next line**, and never calls `factory.finish`. No push, no bus announce, no `runs.record()`.
`OBSERVED`. `finish.py:12-14` exists specifically to prevent that: *"A lane that 'finished' with a
dirty tree… has not finished — it has stopped, and releasing its claim would advertise a lie to the
next session."*

The ledger has entries only because someone ran the CLI. And every recorded outcome is `FINISHED` —
**three of three, zero REFUSED** — in a repo whose `refuses` gate says a control never observed
refusing is decoration.

**Honest version of a6:** the instrument exists and is correct; its principal producer is cut, and it
has never recorded a bad outcome, so it cannot yet corroborate anything.

### 2.10 a9 asserts an enforceability it does not have

R8 §3.2 gives the rule. §13.2 and a9 add *"enforceable in code, no new discipline."* Nothing in this
repo enforces it, no gate measures it, and a9 carries no `gate=`. Today it **is** new discipline —
a runbook line, which is the category R8 was asked to move away from.

**Honest version:** adopt the rule *and* write the probe, or label it a convention until the probe
exists.

### 2.11 Where I agree, one line each

- **a2** — R12 §4.1 named the states; `sessions.py` shipped them (and one more). Correct, and it is
  engine rather than emitter, so a13 does not obsolete it.
- **a5** — R10 Mechanism E is the strongest of its five and the recommendation follows. See §3.4 for
  the half of R10 §7 that was dropped.
- **a11** — settled, re-verified against the raw file, and the sharper reading (no guard, delegated to
  something it cannot see) is better than either source pass.
- **a12** — R8's Kafka and Prefect recommendations contradict constraints its own prompt supplied.
  Taking the isolation half is right.
- **a17** — R13 §8 says in its own text that it never read the inventory. Discounting it is correct.
- **a18** — right, and reached well: §14.6's reasoning (a question you cannot ask neutrally must be
  settled, not asked a fifth time) is a method finding worth more than the answer. R14 §7.4 assents
  without being asked to.

---

## 3. What is missing

### 3.1 ⭐ The eval corpus — one file, and the thing every pass assumed someone else had

`OBSERVED`: `evals/corpus/` contains exactly **one** file, `windsorai-2026-08-20.json`, 6,747 bytes,
last modified 2026-08-21 19:17. `evals/MANIFEST.sha256` pins that one file.

- R1 asked for ≥29 cases.
- R8 §4 repeats it, attributed to R1: *"Maintain a corpus of ≥29 varied data cases (per R1)."*
- R10 §8 makes it a **precondition for its own recommendation**: *"do NOT implement… before… (c)
  expanding our eval corpus from 1 case to ~30."*
- The gate exists and asks the question — `breadth`, *"One real success is a fixture. Calibration
  needs strata and counts."*

**No action among the eighteen names it.** Both passes cited it to R1 and moved on; §12.8 and §13.7
neither adopted nor refused it. This is precisely the shape the brief asked me to look for, and it is
the same shape as `0 of 22 refusals`: **the GreenContract certifies agent output, and the certifier
is calibrated on n=1.** A certifier that has only ever seen one case has not been shown able to
refuse a second.

### 3.2 The `Workstream` / `Attempt` split

R14 §3.2. It is the prerequisite for a8's stated payoff, it is why `runs.report()` collapses a list
to one row and discards the rest (`runs.py:238`), and it is why cost-per-outcome — your own named
differentiator — is a division that cannot yet be performed. Not on the list.

### 3.3 The `Decision` object

§2.3 above. The one plane where a human is mandatory has no type. Not on the list, and it is the
object both a3 and a14 are groping toward.

### 3.4 R10 §7's other half — consolidate, do not add

a5 took *"skills over corpus"* and dropped the recommendation it sat inside: *"We already have six
overlapping stores… Adding a seventh would be a mistake… **retire or merge at least one.**"* R10
names boot-prompts as the candidate. That collides with a live estate rule (`aldc-launchpad/CLAUDE.md`:
*"Do not create a fifth artefact home"* — boot-prompts is the designated one for five repos), so
dropping it may well have been right. **The record does not say it was considered**, which means the
next reader will re-derive it.

### 3.5 Nobody owns the instruments

Three wrong gate edges (§2.1), a probe that cannot pass (§1.1), a self-matching probe already caught
once (`g_evaluator_is_a_service`'s docstring), and F72's cwd-dependent 9-or-10. R14 §2.3 specified
exactly one probe of this kind — assert `claims.ROOT` and `worktrees.ROOT` resolve identically from
the primary and from every worktree — and called it *"a probe that can refuse, on a control that has
never been watched refusing."* Nothing on the eighteen is about the measuring apparatus.

---

## 4. The order I would actually do them in

The stated bottleneck is human decision latency: two PRs at 6–9 days, four agents blocked on unread
questions. My first three do move it; item 0 costs one character and is a precondition for arguing
about anything.

**0. Fix `readiness.py:870` (and `file_answers.py:74`).** *Cost: one character each.* *Unblocks:*
every provenance argument, which is currently being had from a false number in four documents.
*If done third:* a16 stays unpassable, and "0 of 15" gets quoted a fifth time.

**1. Measure the notification path on the two waiting PRs.** *Cost: ~1 hour — open the two
`prefect-connectors` PRs and establish whether a notification was delivered to a subscribed human.*
*Unblocks:* a14, by either confirming or killing it. *What breaks if third:* you build a channel
against an unmeasured failure; if the answer is "delivered and ignored", the 6–9 days recur with a
new sound attached. *This is the item that moves the number*, because it is the only one that tells
you which remedy moves it. `R13-…-run2.md` §3 is right and it is the cheapest measurement on the
list.

**2. Fix `/finish` — `local_tracker.py:1838-1853`.** *Cost: hours.* Check `fails` before releasing;
call `factory.finish` so the branch is pushed, the bus is told and `runs.record()` fires. *Unblocks:*
a6's instrument becoming corroborating rather than merely present, and the `refuses` gate having any
chance of a non-zero. *If third:* it fires every time, and every occurrence converts a failed preflight
into a green banner and a released claim — the exact lie `finish.py` was written to prevent.

**3. Build `Decision`, generalised from `operator.py` — a3 and a14 merged.** *Cost: days.* Ship the
half whose absence is proven (the `needs` questions) regardless of what step 1 returns; add the PR
kind only if step 1 says a notification was never delivered. *If third:* nothing — this one is
genuinely order-tolerant after step 1, which is why it is not first.

**4. Re-wire or drop the three gate edges (§2.1).** *Cost: minutes to decide.* *Unblocks:* the
roadmap being readable. *If third:* the board manufactures up to three false SHIPPEDs, and every
ordering decision after that is read off a lying instrument.

**5. Corpus breadth, 1 → ~30.** *Cost: the largest here, and it is why it is fifth rather than
absent.* *Unblocks:* `breadth` and, with `isolated`, `certified`. *If deferred further:* the product
claim is "we can prove a team did the work", and the prover has seen one case.

**Where a8 goes: sixth or later, and here is why**, since the record has it second. Its stated payoff
is refuted (§2.8), its real payoff is blast radius rather than concurrency, its gate does not measure
it, its prerequisite (`Workstream`/`Attempt`) is unwritten, and it is the most expensive item on the
list. Nothing about it moves the 6–9 days.

**a13 does not appear at all**, per §2.5: it is a ranking held in reserve, not work.

---

## 5. The one decision most likely to be wrong

**a14 — "Build the notification channel first."**

It is the action with the strongest-sounding note (*"three passes and one measurement agree"*), and
that note is the reason to distrust it: the agreement was counted before the two most grounded passes
had answered, and both of them refuse it (§2.2). Its "one measurement" is two measurements with
different instrument states, one proven-absent and one never checked. Being the *first* action makes
it the most expensive one to get wrong, because everything sequenced behind it inherits the error.

**What would prove me wrong, precisely:** open the two `prefect-connectors` PRs that waited 6 and 9
days and establish whether GitHub delivered a notification to a subscribed human. If **no**
notification was ever delivered, a14 as written is correct, my step 1 collapses into it, and the
channel is the first move. If a notification **was** delivered and ignored, a14 would have shipped a
louder version of a channel that already worked, and the remedy is ownership and routing — not a
daemon.

**And the honest inverse, per §0 of the brief:** the decision I would most like to fault and cannot
is **a18**. Four passes were paid for an answer to the terminal question and none answered it; the
response — settle it as a decision and delete it from every brief — is the correct handling of a
question that cannot be asked neutrally. What would change my mind is a pass that was given the
question with the constraint *removed* and still argued for the escape hatch on the merits; nothing
in this directory is that, and R14 §7.4's assent is explicitly assent, not argument.

---

## NOT-SUPPLIED

- **Whether the two 6–9 day PRs generated a delivered notification.** This decides §4 step 1 and
  §5. Nothing in the repo or the answers measures it. `R13-…-run2.md` flagged it and it is still open.
- **Whether the "Anthropic study" behind the 30–45 minute figure exists as cited.** R8 gives no link
  and I did not go looking outside the repo.
- **What OTel GenAI's field set actually contains.** I did not read the specification. From how R11
  (§"Observability") and R13 (§5) both describe it — per-call spans for model, tool and token
  telemetry — it is `INFERRED` that it cannot cover `contract_version`, `harness_version`,
  `side_effect_replay` or `sandbox_image`, which are per-configuration identity rather than per-call
  telemetry. If that is right, **a16 as written cannot close its own gate even after §1.1 is fixed**,
  and the honest version is R14's: *build the nine dimensions; the field set is a naming convention
  for the ones you already have.* Someone should read the spec and settle it.
- **I did not run `measure()` or the tracker.** Another session is working in this checkout and the
  suite gate writes a cache file and shells pytest. Every figure above comes from reading source,
  reading `.data/`, or calling individual gate functions directly. No timing figure here is mine.
