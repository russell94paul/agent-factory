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
