# Future features — the three Paul named, with the evidence for and against each

**Written 2026-08-23.** Proposed in conversation: an **agent-team configuration surface**, an
**optimizer that tunes agent config against requirements**, and the observation that **requirements
have to be refined and clear for agents to succeed**.

All three are good ideas. They are not equally ready, and two of them have measured arguments
*against building them yet* that are stronger than the arguments for. This records all of it, so
the decision is re-openable rather than re-arguable.

⚠ **These are deliberately NOT gates.** A gate in `readiness.py` asserts we are measuring
something; adding one for unbuilt work would make the board report a number about a thing nobody is
doing. When one of these is genuinely next, it earns a gate then.

Neighbour: `product-end-state.md` says what the product is *for*. This says what the surface should
eventually *do*. Neither replaces `architecture-v0.md`, which says what shape it takes.

---

## 1. Agent-team configuration surface — **yes, but read-only first**

### The case for it, and it is real

**The team shape is already decided and the decision is invisible.** `SYNTHESIS.md` §3.1 records
R2's verdict directly: *"Start with one end-to-end implementation agent, not the three-agent
architect → implementer → tester team"* — evidenced across 180 configurations, 5 architectures, 3
model families and 4 agentic benchmarks, where multi-agent averaged **−3.5%** and sequential tasks
degraded **39–70%**.

What *is* supported is **worker + independent reviewer**. R8 called it *"worth one lane
experiment"*, and it is the one team shape this estate has already proven by accident: on
2026-08-22 a reviewer agent found **6 real defects** in a lane's own diff, then another found 4
more — *"three of them mine and one of them severe."*

That knowledge currently lives in prose, in a 1,000-line synthesis, where nothing reads it. Mean-
while `TeamSpec` and `load_team()` exist in `blueprint.py` and **nothing in the estate runs a
TeamSpec**; `blueprints/orchestrator_team.yaml` sits marked superseded with its unlock threshold
inside the file. A surface stating *this is the shape, this is why, and here is the one that was
rejected* would make a settled decision legible instead of re-litigable.

### ⛔ Why not an editor yet

**No TeamSpec has ever executed.** A configuration editor for an object that has never run once is
a dashboard in front of an engine that has not turned over — precisely what this repo's README
forbids: *"Do not add a team, an optimizer or a UI until `pytest tests/test_eval_can_fail.py`
passes."* That gate now passes, so a team is permitted — but permitted to be *built*, not to be
*configured before it exists*.

### The shape worth building

Read-only, and small: the decided team shape, the rejected one kept visible with R2's evidence
(a rejected option is evidence, not clutter), and the live `TeamSpec` if one is ever loaded. It
becomes an editor the day a team runs.

**Unlocks when:** one `TeamSpec` executes end to end and writes a `RECORDED` row to the run ledger.

---

## 2. An optimizer that tunes agent config — ⛔ **not yet, and the reason is measured**

### Why it is tempting

Once a team is configurable, tuning it against requirements is the obvious next move — model,
effort, prompt, tool set, reviewer depth are all knobs, and `factory/runs.py` now measures what each
lane costs, so there is finally an outcome to tune against.

### ⛔ Why it would produce a confident number that means nothing

Two measurements settle this and neither is close.

- **R3 ranked a separate local optimizer process `rank 5`, "mostly theatre."** That is this
  programme's own research, on this programme's own design.
- **The eval corpus is 1 case with 0 strata.** R1 concluded that detecting a blind spot present in
  10% of cases needs **29**. An optimizer searches a configuration space by comparing outcomes; with
  a corpus that cannot distinguish a good config from a bad one, every comparison is noise wearing a
  decimal point.

⭐ **An optimizer on top of an instrument that cannot detect a difference is the 965-run loop
again** — the mechanism in this estate's founding story that ran 965 times, recorded its own 1.6%
success rate, and never adjusted. It was capable. It was not measurable.

**Unlocks when:** the corpus reaches ~29 cases with strata, *and* `test_eval_can_fail` still passes
against the larger corpus — i.e. the harness can still register a failure when the set gets big.

---

## 3. ⭐ Requirements refinement — **build this first, and today proved why**

Paul's third point was the sharpest and it is the one with same-day evidence:

> *"we would also need to ensure requirements are refined and clear for the agents to succeed."*

### The evidence, all from 2026-08-23

Three research passes failed today. **Not one failed on model capability.** Every one failed on the
quality of what it was given:

| Pass | How it failed | Root cause |
|---|---|---|
| **R8 run 1** | asserted internal facts it could not check; answer discarded | its prompt said *"read R2, R3, R5, R7 first **if you have them**"* — an instruction conditional on access it did not have, naming the *prompt* files rather than the answers |
| **R13 run 1** | §8 migration section invented; struck from the record | never read `ui-surface-inventory.md`, **its own named attachment** — *"Without detail on those, we assume multiple UIs"* |
| **R15** | supported a recommendation with a fabricated user study | *"in our user studies we found…"* — there are no user studies |

⭐ **This is the finding that reorders the other two.** An optimizer tunes *agent configuration*. If
the failures come from *requirement quality*, an optimizer is tuning the wrong variable — and it
will converge, confidently, on a configuration that was never the problem.

### And the fix is already known and proven three times

The repair for R8 was not a better model. It was **shipping the evidence with the question**:

1. A generated pack containing every source the question depends on — `scripts/build_r8_pack.py`,
   and since then R13's and R14's equivalents.
2. One rule, stated in the prompt: **"where the pack and the prompt disagree, the pack wins, and
   the disagreement is a finding we want reported."**
3. One permission: **`NOT-SUPPLIED` beats a plausible assumption.** The last assumption cost a
   whole section.

That pattern is cheap, mechanical, and has now worked three times. **It generalises directly from
research prompts to agent task briefs**, which are the same object: a question plus the evidence it
depends on, handed to something that will answer confidently either way.

### The shape worth building

A **brief compiler**: given a task, assemble the evidence pack the agent needs, state the
pack-wins rule, and refuse to dispatch a brief whose named attachments are missing. That last
clause is the whole value — it is the check that would have caught all three failures above, and
it is a file-existence test, not an AI problem.

**Unlocks:** now. It has no dependency on a team object, an optimizer, or a corpus.

---

## 4. The order these should arrive in, and why

```
1  brief compiler            evidence with every task; refuse a brief missing its attachments
2  team surface (read-only)  make the decided shape legible; editor once a TeamSpec runs
3  optimizer                 only after the corpus can tell two configs apart
```

⚠ **The tempting order is the reverse** — the optimizer is the most interesting, the config surface
is the most visible, and the brief compiler is the least exciting thing on the page. It is also the
only one with three same-day failures arguing for it, and the only one that unblocks nothing else
because nothing else blocks it.

## 5. What would change this document

- A `TeamSpec` executing end to end → promotes the team surface from read-only to editable.
- The corpus reaching ~29 stratified cases → the optimizer stops being theatre.
- A fourth research pass failing for a reason *other* than requirement quality → weakens §3's
  claim that requirement quality is the dominant failure mode. Three is a pattern, not a law.

---

# Second batch — proposed 2026-08-23, later the same day

⚠ **Ideas, not roadmap.** Paul's words. Recorded so they can be argued with; none is scheduled and
none has a gate.

## 6. Interactive project flow — clickable steps that explain themselves

**The idea:** one diagram of the whole sequence, each step clickable to reveal what it does.

**The case for:** the sequence exists but is scattered across four places — `board.DEPENDS` (gate
order), `goals.GOALS` (what we are building toward), `SYNTHESIS` §12.8/§13.7/§14.7 (eighteen
decisions), and the five `PHASES`. Nobody can see it whole, which is why the same questions get
re-asked.

⛔ **The trap, and it is the one that would ruin it:** a flow diagram of steps that exist only in
the diagram is decoration — it would look identical if the project were different. **The steps must
be derived from the existing graphs, or declared in one authored map validated on import the way
`board.DEPENDS` and `dispatch.DEPENDS` already are.** A hand-drawn sequence is a picture of an
intention, and this repo has a rule about those.

**Unlocks:** now, if derived. Never, if drawn.

## 7. Task / plan page — a prompt box that refines requirements and picks the agent

**The idea:** type what you want, refine it in an embedded session, and have it select the agent or
team best suited.

⭐ **This is §3's brief compiler, arrived at independently — and the valuable half is not the half
it sounds like.** Agent *selection* is the interesting part and the cheap part: there are five
lanes and one supported team shape, so selection is nearly a lookup. **The part that would have
prevented every failure of 2026-08-23 is the refusal** — a brief whose named attachments do not
exist must not dispatch.

R8 run 1, R13 run 1 and R15 all failed with a competent model, a clear question and an incomplete
brief. **None of them would have been saved by picking a different agent.** All three would have
been stopped by a file-existence check.

So build the page, and build the refusal first: assemble the pack, verify every named attachment
resolves, state the pack-wins rule, and refuse otherwise. Selection can be a dropdown until there
is more than one team.

**Unlocks:** now.

## 8. "Run simulations until it completes" — ⛔ the instinct to skip this is right, for a stronger reason than time

Paul's own note is *"we won't have time for this"*. Time is not the binding reason.

**Running until success against an eval that cannot fail is the 965-run loop.** The corpus is 1
case with 0 strata; R1 puts the threshold for detecting a 10%-prevalence blind spot at 29. A
simulation that "completes successfully" against that corpus has demonstrated that it can satisfy
an instrument incapable of refusing it — which is what the retired 965-run mechanism did 965 times
while recording its own 1.6% success rate.

**A detailed boot prompt in the UI is the correct substitute**, and not a consolation: it is the
same evidence-with-the-question pattern that repaired R8, and it works today.

**Unlocks when:** the corpus can fail. Same threshold as §2.

## 9. A Power BI agent — ⛔ blocked on a contract, not on an agent

**The idea:** an agent that designs three data models against the Snowflake warehouse.

**What is missing is not capability.** `factory/connector_contract.py` is A1–A12 and is
connector-shaped. **There is no Power BI contract**, so there is no definition of done for a
data-model change — and this repo's ordering is explicit: contract, then evals, then tasks, then
deploy.

⚠ **And the oracle is harder here than for connectors.** The estate's own standing rule is that a
query-layer check is not a render check: a repoint once passed DAX parity while every visual showed
*"Error loading data"*. So "done" for a PBI model means **rendered**, which an agent cannot
currently verify. Any A1–A12 equivalent has to say how that is established, or the contract will
certify something nobody has looked at.

**The unblocking move is an hour of writing, not an agent:** what are the twelve assertions that
make a data-model change correct, and which of them can be checked without a human opening the
report?

**Unlocks when:** a PBI contract exists and its negative control passes — i.e. it can fail.

## 10. ⭐ Handoffs need a state, not just a type — and the directory is already past the point of sorting

**The idea (Paul, 2026-08-23):** *"we need to ensure all handoffs get their own type or lane."*

**Type is the right instinct and the wrong noun.** `factory/handoff.py` already draws the type
distinction, in its own docstring: `LANE` (one lane finishing, belongs on the lane card) versus
`SESSION` (everything that moved, belongs on its own tab). Today produced a third kind it has no
name for — a **brief written for another live session** (`drafts/r13-rewrite-context-…`), which is
neither a lane closing nor a session ending.

### What the directory actually looks like, measured

```
boot-prompts/          186 files          Jun 39 · Jul 87 · Aug 60
distinct prefixes      183 of 186         ← essentially every file is its own workstream
undated filenames      137 of 186 (74%)
carrying a `next:`      29 of 186 (16%)
mentioning supersession 49 of 186 (26%)
```

⭐ **The load-bearing failure is not missing types. It is that nothing declares which handoff is
CURRENT for anything.** `CLAUDE.md` instructs a session to *"read the newest one matching the ticket
or workstream"* — an instruction that describes an organisation which does not exist: 183 of 186
prefixes are unique, so there is nothing to match against, and 74% carry no date in the filename to
be "newest" by. **The rule is a heuristic over 186 singletons.**

This is the same failure class the research prompts had before `dispatch.py`: state living in prose,
no instrument, and a human doing the sorting from memory. That was worth fixing and this is worth
fixing for the same reason.

### The shape worth building

Mirror `dispatch.py`, because it already works. A declared **workstream key** and a **state**:

```
CURRENT      the head for its workstream — at most one
SUPERSEDED   another handoff names it, by filename
SPENT        its `next:` was done; kept as record, never as an entry point
ORPHAN       no workstream, no `next:`, nothing points at it
UNCLASSIFIED predates the convention — NOT the same as ORPHAN
```

Plus the type: `BOOT` (session entry, has a `next:`) · `LANE` · `BRIEF` (context for another live
session) · `RECORD` (a closeout with no next action).

⚠ **Do not backfill the 186.** They report `UNCLASSIFIED`, which is a fact about the convention's
age, not about the files. Sorting them retroactively means guessing which of two undated July files
superseded the other, and a wrong guess is worse than an honest gap — the ZERO versus NOT-RECORDED
rule, applied to a directory.

**The test that makes it real:** exactly one `CURRENT` per workstream, asserted. Two heads means the
next session reads the wrong one, which is the failure the whole directory exists to prevent.

⚠ **Another session is building a handoff tab right now** (in `scripts/local_tracker.py`, which also
gained Flow and Goals today). This is the data layer that tab needs. **Coordinate before either is
built**, or two sessions will write two models of the same thing — which is exactly what happened
with R13 this morning.

**Unlocks:** now, and it is small. The instrument is a directory read and five states.

## 11. A wiki of its own for the factory — ⚠ half of this is already refused, and half is the best-supported idea we have

**Raised by Paul, 2026-08-23, explicitly as not urgent.** Logged rather than actioned. It arrives
with more evidence attached than any other entry here, because R10 already answered a version of it.

### The question splits in two, and the halves have opposite verdicts

**"Its own wiki"** — a second corpus, holding the factory's own knowledge. **R10 refused this shape**
(SYNTHESIS §12.6) on two measured grounds:

- **Context degradation.** Accuracy fell ~24% from adding 30k *irrelevant* tokens *even with the
  relevant content present*. The existing wiki is ~1M tokens, roughly forty times the ~25k threshold
  where this begins. A second corpus does not escape that; it adds to it.
- **Memory laundering.** An unsupervised write-back loop turns hallucinated content into
  innocuous-sounding prose that still misleads later reasoning. Safe only two-tier — **confirmed**
  (human-verified) vs **proposed** (auto) — and never auto-absorbed.

**"And wiki design"** — a *designed surface* over the knowledge rather than a bigger pile of it. That
is R10's **mechanism C, structured context assembly**, which carries **the strongest number in the
whole answer**: revisions 3.8 → 2.0, first-draft acceptance 32% → 55%. It was rated *beneficial*
where the corpus idea was rated *no*.

⭐ **So the feature is not "should the factory have a wiki" but "should the factory ASSEMBLE
context deliberately instead of retrieving from a corpus".** Same words, opposite verdicts, and the
distinction is the entire design.

### What is already happening without anyone calling it this

R10's actual top recommendation was **mechanism E — procedure synthesis into invocable skills**,
"the highest-leverage of the five", and explicitly an instruction about `~/.claude/skills/`. The
`deep-research` skill written on 2026-08-23 is one instance: a session's hard-won lessons distilled
into something the model can trigger, rather than a page it must be told to read. **That path is open
and needs no new surface.**

### ⛔ Unlock condition, and it is unusually concrete

**R10's two strongest figures are `REPORTED-unverified`.** It attributes context assembly to *"Swift
et al. 2026"* and skill distillation to *"SkillX"*, and **neither is linked and neither has been
read.** The 32% → 55% number is the reason to build the assembly surface, and it cannot be a design
premise until someone opens the source.

So: **verify those two citations before designing anything.** That is now a small, well-shaped job
for the `deep-research` skill, whose §3 exists for exactly this. If the sources hold, mechanism C is
the best-evidenced thing in the backlog. If they do not, this entry loses its foundation and should
be closed rather than quietly kept.

**Do not add a gate for this.** A gate asserts we are measuring something, and nothing here is being
measured yet.
