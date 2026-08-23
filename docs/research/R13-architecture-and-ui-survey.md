# R13 — Architecture and UI survey · RUN 2: four questions run 1 left open

**Status: ANSWERED 2026-08-23 (run 1). Run 2 rewritten and pending — see the run log.** Rewritten 2026-08-23 for run 2. Paste the whole file and attach
`docs/research/R13-evidence-pack.md`. The answer is filed at
`docs/research/answers/R13-answer-architecture-and-ui-survey-run2.md`.

## Run log

| Run | Dispatched | Outcome |
|---|---|---|
| 2 | pending | Rewritten as a narrow repair. Four questions only; the survey is not to be redone. |
| 1 | 2026-08-23 | Answer filed and **reconciled into `SYNTHESIS.md` §14 — most of it was adopted.** Strong on the stack decision, the approval survey and provenance. ⚠ It never read `ui-surface-inventory.md`, its own named attachment, so §8 was guesswork and was discounted. It also deferred on the terminal question rather than arguing it. |

> `dispatch` reads a status line and whether an answer file exists; by its own account it cannot see
> whether a prompt was ever pasted anywhere. **Add a row when the paste is confirmed, not when it is
> announced.**

---

## Who we need you to be

**Someone who has been handed a good report and asked to finish it, not to write it again.**

Run 1 of this brief was strong and is already adopted. You are not being asked to survey the field —
that is done. You are being asked for **depth on four specific things**, three of which run 1 got
wrong or skipped, and one it answered without noticing it had contradicted itself.

⚠ **A long answer is a failed answer here.** Run 1 was roughly 5,000 words of survey. If run 2 is
that length, you have re-surveyed instead of repaired. We would rather have 1,500 words that settle
four questions than 5,000 that restate a conclusion we already hold.

---

## 0. What is CLOSED — re-opening any of it is a wasted run

Run 1 settled these and other passes have since corroborated them. They are decisions now.

| Closed | Established by |
|---|---|
| **Platform: a VS Code extension**, not a desktop app — the operator already lives in VS Code, so cold start is nothing, and Monaco, LSP, Git and diffs come free. Electron out on weight | **your own run 1 §2**, and it beat a competing pass that wanted Rust/Tauri |
| **Topology is closed** — you surveyed seven orchestration patterns and none raises the 3-lane cap | your run 1 §1 |
| **The ceiling is a *file-conflict* artefact** — a container plus its own DB clone per agent makes it resource-bound | another pass, which your own line about "task structure" predicted |
| **Notification is the first thing to build** | your run 1 executive summary, plus two independent sources |
| **Provenance: the OTel GenAI field set** as the config-hash dimensions | your run 1 §5 |

⛔ **Do not re-argue the embedded terminal.** It is settled: escape hatch, never the primary
surface. Four passes were asked to argue it on the merits and none did — one restated our position,
one supported it with a fabricated user study, and run 1 of this brief deferred to the operator. The
fault was ours for stating our position inside the question. It is now a constraint. **Design
accordingly and do not spend a paragraph on it.**

---

## 1. ⛔ The defect that caused this run — and the rule that fixes it

Run 1 §8 said, verbatim:

> *"We must build on top of the existing four interfaces (and one dead one). **Without detail on
> those, we assume multiple UIs (CLI, web panel, maybe Slack bot).**"*

`ui-surface-inventory.md` was the attachment named in run 1's own header, and it describes those
surfaces precisely. It was not read. **The entire migration section was therefore invented and has
been struck from our record.**

**The rule for run 2, and it is not negotiable:**

1. **The evidence pack is attached and it is the only admissible source for facts about us.**
   Everything below is a handoff, and in this estate a handoff is a hypothesis.
2. **Where the pack and this prompt disagree, the pack wins**, and the disagreement is a finding we
   want reported.
3. **If something you need is not in the pack, write `NOT-SUPPLIED` and name it.** Do not infer it,
   and do not fall back on a plausible assumption. **The last assumption cost a whole section.**

---

## 2. The four questions

### 2.1 The migration — against the real surfaces this time

Five interfaces exist. They are described in §A of the pack. **Read that before writing a word of
this section.**

For each: keep, absorb, or retire — and in what order. What runs in parallel with what. What must
**not** be built yet.

⭐ **The dead one is the most instructive, and run 1 never saw it.** `platform/master` was the
platform half of a monorepo; it stopped moving in June 2026 while the operations half carried every
ticket. **Tell us what that failure predicts about the thing you are recommending we build**, and
what would have to be true for the VS Code extension not to end the same way. This is the question
we most want answered, and you are best placed to answer it, having chosen the platform.

### 2.2 The latency budget — grounded, not from guidelines

Run 1 gave targets from user-perception guidelines and named no mechanism. We have since measured
the real thing:

```
factory.readiness.measure()   30 gates, 9.39 SECONDS, serial
  suite                       9.16 s  = 97.6%  <-- shells out to `python -m pytest`
  the other 29 gates          0.23 s  =  2.4%
the server                    socketserver.TCPServer — single-threaded,
                              so two concurrent requests return EMPTY
```

⚠ **We had this wrong and are telling you so, because the wrong version is the obvious one.** We
first reasoned "30 independent I/O-bound probes, an 8-wide pool, 9.3/8 = 1.2 s". **That is wrong by
about eight times.** One gate shells out to a full pytest subprocess; it is a single indivisible
task, and **parallel speedup floors at the slowest task, not at total÷width.** A pool takes this
from 9.39 s to 9.16 s. **Do not recommend concurrency here** — it is the intuitive answer and it is
worth almost nothing.

The hard constraint that makes this interesting: **we forbid a silently cached figure.** A surface
that can quietly show yesterday's state is the drift this project exists to remove, so every number
must be able to say how old it is.

**So: what buys what, in milliseconds, against those numbers?** Dependency-tracked invalidation,
event-sourcing, virtualisation, optimistic rendering, push — run 1 listed them all and costed none.

⭐ **The real question, given the shape above, is what to do about one 9-second task that cannot be
subdivided.** Take it out of the request path and cache it against the git SHA of the code it tests?
Run it on a schedule and render it with its age attached — which our own *"a cached figure carries
its age in the same string"* rule permits? Something else? **That single decision is worth more than
every other technique on the list combined, and we want it costed and argued.**

If the honest answer is "cache the suite result and stop, the rest is premature", say that — it is
more useful than an architecture.

### 2.3 ⭐ The contradiction run 1 did not notice

Run 1 recommended **a VS Code extension** as the platform. Run 1 also recommended **an approval
surface a non-engineer could use** — a PM or an auditor reviewing agent-produced work.

**A non-engineer does not have VS Code open.** Those two recommendations do not obviously fit
together, and run 1 never checked.

So: does the approval surface live inside the extension, somewhere else entirely, or does its
existence break the platform decision? If it lives elsewhere, what is it, and what does maintaining
two surfaces cost a small team? Run 1 also reported that **no off-the-shelf tool targets business
users reviewing code changes** — so this is unbuilt ground, and we would rather know that sharply
than approximately.

### 2.4 A source-read that settles a live contradiction

Two of our passes read the same repository and reported opposite things, both claiming to have read
the source:

| | Claim |
|---|---|
| One pass | `doctly/switchboard` **never attaches** to a process it did not spawn; a session running outside it is treated as not running, and it **spawns a second process against the same session id** |
| The other | *"ATTACH: Yes — it can attach to any running session… not just those it spawned"* |

**Read `doctly/switchboard`'s `open-terminal` handler and settle it.** Specifically: when
`activeSessions` does not contain the requested session id, does it attach to the existing process,
or spawn a new one with `--resume`? **Quote the code.**

This matters beyond the tool. A terminal dying while its agent kept working is a failure we actually
had, and "spawns a duplicate against a live session id" is that failure by design. If neither answer
is right, say so — a third reading is the most valuable outcome available here.

---

## 3. Constraints

Windows-first · small team, no platform team to operate anything · three concurrent lanes today ·
per-secret human approval is a hard rule · **no unlabelled stale numbers** · the existing instrument
panel is added to, never removed · the terminal is an escape hatch, and that is settled.

## 4. Deliverable

1. **The migration** (§2.1), against the five real surfaces, with what the dead one predicts.
2. **The latency budget** (§2.2), in milliseconds, ordered, with the honest "stop here" line.
3. **The approval-surface fit** (§2.3) — inside the extension, elsewhere, or fatal to the platform.
4. **The switchboard reading** (§2.4), with the code quoted.
5. **What you would refuse to build**, and what we should delete.

**Nothing else.** No orchestration survey, no stack comparison, no terminal discussion. If you find
yourself writing one, you are answering run 1's brief instead of this one.

## 5. Tier every claim

`OBSERVED` — you read the source or ran it · `REPORTED` — a credible postmortem or paper ·
`MARKETED` — a vendor says so and nobody independent confirmed it · `INFERRED` — your reasoning.

**A `MARKETED` claim may not be a design premise.** And one specific warning, because it has already
happened here: **do not cite evidence about us that you have not been given.** A previous pass
supported a recommendation with *"in our user studies we found…"* — there were no user studies. If
you want to claim something about our operators, ask for it, or mark it `NOT-SUPPLIED`.
