# R15 — Read the field's source, not its README: a repository corpus, then the architecture and UI we should build in

**Status: ANSWERED 2026-08-23.** Written 2026-08-23. Paste the whole file. Attach
`docs/research/ui-surface-inventory.md`, `docs/specs/architecture-v0.md` and
`docs/specs/control-room.md` — or, to send one file, `docs/research/R13-evidence-pack.md`, which
already contains all three. The answer is filed at
`docs/research/answers/R15-answer-source-corpus-crawl.md`.

## Run log

| Run | Dispatched | Outcome |
|---|---|---|
| 1 | 2026-08-23 | Answer filed 2026-08-23. **See SYNTHESIS for what it got wrong** — it contradicts R12 on switchboard's attach behaviour without flagging it, cites a user study that does not exist, and omits section 5.0 entirely. |

> Kept because `factory.dispatch` reads a status line and the presence of an answer file, and by its
> own account cannot see whether a prompt was ever actually pasted anywhere. **Add a row every time
> this prompt is dispatched.**

---

## Who we need you to be

**An engineer who reads other people's repositories for a living and comes back with what the code
does, not what the project says it does.** You clone before you cite. You can open an unfamiliar
80k-line codebase, find the twelve files that carry the design, and describe the architecture from
the call graph rather than the architecture diagram in the wiki — which you have learned is usually
a year out of date and describes an intent that was never finished.

You have built developer tools yourself, so you can tell craft from polish: you know why a list of
50,000 rows scrolls at 120 fps in one app and janks in another, and you can name the technique
rather than the vibe.

**What we are not asking for.** Not a curated awesome-list. Not a feature matrix assembled from
landing pages. Not enthusiasm. We want the corpus a sceptic would assemble, read at source level,
with the divergences between what each project claims and what it implements written down as
findings.

⭐ **This pass exists because reading one repository's source was the single most valuable thing
any research pass has done for us.** R12 was told to adopt a session manager; reading its source
found that it re-uses only PTYs it spawned itself and otherwise starts a *second* process against
the same session id — which would have silently corrupted every lane we run. That finding came
from the code and was invisible in the README. **R15 is that method, applied to a corpus instead of
a single repo.**

---

## 0. Four neighbours — do not re-answer them

| Pass | Asked | State |
|---|---|---|
| **R11** | which concepts do other agent factories make first-class that we have no name for | **ANSWERED** — vendor/concept level. Do not re-survey framework taxonomies |
| **R12** | should we adopt an existing session manager; what must the substrate know | **ANSWERED** — read it, its source-level findings are your control case |
| **R13** | survey the option space — orchestration patterns, desktop stack, latency budget, approval, provenance | **in flight** — R13 reasons about *categories*; you read *repositories* |
| **R14** | is our own decomposition right, and what would make this a joy to use | **in flight** — inward-facing; yours is outward-facing |

**The line between R13 and R15, stated so you do not drift across it:** R13 asks *"what are the
options, and what does the literature say"*. **R15 asks _"what did people actually build, and what
does their code prove is achievable"_.** If you find yourself weighing Electron against Tauri in
the abstract, that is R13's. If you are reporting that a named repo ships an Electron app whose
renderer measurably cold-starts in N ms and whose file-watch drops events on Windows, that is
yours.

If a question you want to answer belongs to a neighbour, **say so and stop** rather than answering
it thinly.

---

## 1. What this system is — it decides what counts as relevant

> **A team of agents did the work, and we can prove it — or we can prove we could not tell.**

**An evidence product, not a process product.** It exists because two earlier mechanisms in this
estate acted with nothing measuring whether the action helped: one produced *233 diagnoses, 234
escalations and 0 fixes over 81 days*; another ran *965 times, recorded its own 1.6% success rate,
and never adjusted*. Both were capable. Neither was measurable.

Four planes, hard boundary between RUN and PROVE — the thing being measured must not be the thing
doing the measuring:

```
APPROVE   humans only. merge · per-secret grant · promote to prod   ← no interface at all today
PROVE     readiness gates · a four-valued contract · findings ledger · run audits
RUN       isolation ladder — T0 git worktree · T1 container · T2 container + ephemeral DB clone
DECIDE    conflict graph · claims · scheduling · caps · budgets · a bespoke build plane at :8765
```

Agents are **Claude Code CLI sessions**, one git worktree and branch each, writing JSONL
transcripts and registering in `~/.claude/sessions/<pid>.json`. Python. Windows-first on the
operator's machine. Snowflake is the warehouse; Prefect 3 is the *run* plane; the build plane is
bespoke and does not import Prefect.

⭐ **Hold that against the corpus.** Nearly every tool in this field manages *processes* or
*conversations*. Almost none can answer **who did this work, under what configuration, and what
proves it was correct.** When you find one that can — even partially, even in an adjacent field
like CI provenance or data lineage — that repository is worth more to us than five agent UIs, and
we want it read in depth.

## 2. The measured state you are designing against, 2026-08-23

```
readiness         10 of 30 gates pass
lanes             5 defined · max 3 concurrent, DERIVED from a file-conflict graph
                  2 of the 5 have never been launched
autonomy          3 of 14 recorded runs finished with no human
gate refusals     0 of 22 gate events were ever a refusal
agent versioning  the config hash covers 0 of 15 dimensions — we cannot say which agent produced what
cost              1.23M output tokens / 322M cache-read / 22.8 h / opus / 25 commits   (one lane)
                  227k output / 55M cache-read / 19.4 h / sonnet / 5 commits           (another)
sessions          12 running on one workstation · 5 shared a single name · 6 shared one directory
blocked agents    4 sat blocked on questions written in plain English that no surface displays
delivery          2 pull requests fully green, waiting 6 and 9 DAYS for a human to merge
UI latency        a tracker page load re-measures everything: 10-19 SECONDS
                  two concurrent requests return empty — the server is single-threaded
```

⭐ **Read the last three together. Our agents are not the queue; our humans are.** Any architecture
that makes agents more visible without making decisions faster has optimised the wrong end, and we
will say so.

---

## 3. The corpus — how to choose it, which is most of the rigour

**Declare your inclusion rule before you search, and publish it with the answer.** A corpus
assembled after seeing what turned up is a conclusion wearing a method's clothes. State:

1. **The inclusion rule** — what makes a repository in-scope (e.g. *"open source, ships a UI or a
   supervision layer over long-running agent or job processes, commit within the last 6 months"*).
2. **How you enumerated** — the searches, topics, awesome-lists, package registries and citation
   trails you actually walked, and in what order.
3. **The exclusion log** — repositories that met the rule and were dropped anyway, and why. This is
   as informative as the inclusions.
4. **The cut-off** — how you decided the corpus was complete rather than large enough to stop.

⚠ **This estate has been burned by sampling.** An audit here once produced counts of 5 → 10 → 114 →
33 → ~13 for the same question, because each pass sampled instead of enumerating. **"I read forty
repositories against a stated rule and here are the six that matter" is a finding. "Here are eight
interesting projects" is a hint.**

### 3.1 Cover the whole chain, not one link

We are not only after agent UIs. The chain we need built runs **decide → run → prove → approve**,
and the most transferable ideas will come from fields that solved one link decades ago. Cover at
minimum:

| Link | What we want from repositories in this band |
|---|---|
| **Multi-process supervision** | how N long-running child processes are owned, named, addressed, restarted, and reattached after the parent dies |
| **Agent orchestration / coding agents** | how a run is represented, what state is durable, what the human sees mid-run, how a question reaches them |
| **Session & terminal management** | identity, attach vs resume, PTY handling, what survives a crash, Windows reality |
| **Pipeline / workflow observability** | run history, DAG rendering, retries, replay, and how "this run" is made addressable forever |
| **Provenance & supply chain** | attestation formats, signing, what a build claims about itself, whether a verifier is a separate principal |
| **Review & approval surfaces** | how a diff plus its evidence is presented for a yes/no, batching, delegation, and audit of the decision |
| **Local-first desktop devtools** | the craft band — cold start, virtualised lists, incremental invalidation, offline state, packaging on Windows |
| **Eval / experiment tracking** | how a configuration is pinned to a result so a verdict cannot outlive the config that earned it |

### 3.2 A floor, not a ceiling

Candidates from our own knowledge, offered so the corpus cannot come back thinner than this.
**Every one is a hypothesis: verify it exists, is active, and is what we think it is — and drop it
with a reason if not.** Do not let this list bound the search; the inclusion rule governs.

```
supervision / sessions   doctly/switchboard (our control case — re-verify R12's finding)
                         tmux/tmux · zellij-org/zellij · wez/wezterm · charmbracelet/bubbletea
coding agents            All-Hands-AI/OpenHands · princeton-nlp/SWE-agent · Aider-AI/aider
                         cline/cline · continuedev/continue · block/goose
frameworks w/ runtime    langchain-ai/langgraph · crewAIInc/crewAI · microsoft/autogen
observability / eval     langfuse/langfuse · Arize-ai/phoenix · OpenTelemetry GenAI conventions
workflow + run history   temporalio/temporal · dagster-io/dagster · apache/airflow
                         argoproj/argo-workflows · PrefectHQ/prefect (we run this)
provenance               in-toto/in-toto · slsa-framework/slsa · sigstore/cosign
approval / portals       spotify/backstage · GitHub & GitLab agent flows (docs where source is closed)
desktop craft            tauri-apps/tauri · wailsapp/wails · jesseduffield/lazygit · microsoft/vscode
```

**Closed-source products are still in scope as `MARKETED`/`REPORTED` evidence** — Warp, Devin,
Factory.ai, Cursor, Copilot Workspace — but they may not carry a design premise (§7), and please
keep them visibly separate from the read-the-source tier.

---

## 4. The extraction — the same questions of every repository

**Comparability is the whole point.** Answer the same schema for each repo you read in depth, so
the corpus can be tabulated rather than narrated. Where a field does not apply, write `N/A`; where
you could not determine it, write `NOT-DETERMINED` and say what you would have had to read.

```
repo · stars/commits/last-commit/licence · language & UI stack
UNIT OF WORK        what object represents one piece of work; is it durable, addressable, replayable
IDENTITY            how a run/session/agent is named; what survives restart; collision behaviour
LIVENESS            how "alive" is determined — process table, registry, heartbeat, file mtime, inferred
ATTACH              can it connect to a process it did not spawn? what happens if it tries?
STATE               where truth lives: memory, SQLite, files, server. what is cached, can it go stale,
                    is staleness shown to the user
CONCURRENCY         how parallel work is bounded; is there a conflict model at all
HUMAN-IN-THE-LOOP   how the tool asks a human something, and what happens when two ask at once
PROVENANCE          what the tool can prove afterwards about who/what/which-config produced an artefact
APPROVAL            is there a surface for accepting or rejecting the work; what does it show
PERFORMANCE         measured or documented numbers — cold start, list virtualisation, watch fidelity
WINDOWS             does the interesting part work there, or is it POSIX-with-a-Windows-build
SECURITY            process isolation, credential handling, what a compromised renderer could reach
CLAIM vs CODE       ⭐ any capability the README asserts that the source does not implement
```

⭐ **The `CLAIM vs CODE` row is the highest-value field in this brief.** Every divergence you find
is a finding we want stated plainly, with the file and line. It is also the field that justifies
the whole pass: we can read marketing ourselves.

**Read in depth, not broadly, where it counts.** We would rather have **six repositories read
properly** — entry point, main loop, state layer, the two hardest problems in the domain — than
thirty summarised from their docs. Say explicitly which tier each repo was read at:
`SOURCE-READ` · `DOCS-READ` · `LISTED-ONLY`.

---

## 5. Then synthesise — the architecture and the UI we should build in

This is the deliverable the corpus exists to support. **Be opinionated and commit.**

### 5.0 First: what OUR system gets wrong that the corpus already solved

⭐ **This section comes before the architecture and before the UI, deliberately, and it is the one
the operator asked for.** The point of reading forty repositories is not only to design what comes
next — it is to find the things we built badly that somebody else already solved properly, and to
fix those *before* a single pixel changes. A new interface over a weak substrate is a prettier way
to be wrong.

So: **a ranked list of defects in our system that the corpus exposes.** For each one:

- **what we do**, with the file and line in our code;
- **what the corpus does instead**, with the repository, file and line;
- **the failure it prevents** — concretely, not "better practice";
- **the cost to change**, and whether it is a prerequisite for the UI or independent of it.

Rank by *what breaks if we do not*, not by effort. We would rather see three items we cannot argue
with than fifteen we skim.

Candidates we already suspect are weak — confirm, refute, or ignore in favour of what you actually
find, and **the ones we have not thought of are the ones we are paying for**:

| Ours | The suspicion |
|---|---|
| a claim is a file, not a lock, and **not a process** (`claims.py`, untested) | everyone solving this has a liveness model; ours let a second agent into a live worktree |
| the live channel is **per-worktree** and holds one event in the estate (`bus.py`) | lanes cannot see each other; is a bus even the right primitive here |
| state lives in **five roots under two conventions** — `parent.parent/.data` vs the primary worktree | what do mature projects do about state location in a multi-checkout world |
| the evaluator is **not a separate principal** — R3 called it *"mostly theatre"* | how does anyone make a verifier genuinely independent, in-process or not |
| the config hash covers **0 of 15 dimensions** | provenance is worthless if the artefact cannot name the config that produced it |
| the conflict graph is **file-locality only**, capping us at 3 | is a resource conflict graph the answer, and who has built one |
| 30 probes re-measured **serially, 10–19 s a page**, and silent caching is forbidden | how does anyone stay always-current and instant at once |
| `0 of 22` gate events were ever a **refusal** | a gate that has never refused has not been shown to work |

**If the honest answer to a row is "your version is fine, the field does no better", say that.** A
row we can stop worrying about is worth as much as a defect.

### 5.1 The architecture

One recommended architecture, argued, with the runner-up named and the reason it lost. It must say:

- **What the durable unit of work is** for us, and what it replaces in what we have today.
- **Where state lives**, how it stays current without a silent cache, and what the invalidation
  model is.
- **How the RUN/PROVE boundary is enforced in code** — today our evaluator is not a separate
  principal, which R3 called *"mostly theatre"*, and we know it.
- **What raises the 3-lane ceiling**, or an argument that it should not be raised yet.
- **Which pieces are stolen from which repository**, named, with what we would have to change.

### 5.2 The UI we build in

Not a dashboard — **the surface an operator lives in all day while several agents work.** Say:

- **The primary object on screen** and why. (Our current tabs are lanes, gates, findings, sessions.
  If the right primary object is none of those, say so — that is exactly the kind of finding we
  want.)
- **The screens, in priority order**, and what each is for. If your answer includes a screen that
  only exists because it is easy to render, cut it yourself.
- **How a blocked agent's question reaches the human**, and what the human sees to answer it in
  seconds. Our measured latency is *days*. Our failure is **alarm absence**, not alarm fatigue.
- **The approval surface**, including the harder half: **could a non-engineer safely approve agent
  work, and what would they have to see?** Has any repository in the corpus tried it?
- **What it feels like.** Latency budget in milliseconds for first paint, interaction-to-response,
  and full re-measure — with the technique that buys each, named.
- **The research flow itself — design it, because it is one of our worst.** This document you are
  reading was produced by, and will be filed through, a loop that is almost entirely manual and has
  already lost track of itself. Measured on 2026-08-23:

  ```
  write the prompt in an editor  ->  open a tab and copy it  ->  paste into a browser
  ->  wait hours  ->  download `deep-research-report (3).md`  ->  move it into answers/
  ->  run a classifier that guesses which prompt it answers FROM ITS CONTENT
  ->  run a currency check  ->  hand-write the reconciliation
  ```

  What actually went wrong, none of it hypothetical: the operator **could not tell which prompts he
  had already sent**, because dispatch state was a status string a human edits and nothing recorded
  the moment of dispatch. Four answers arrived as `deep-research-report (N).md` and **two were
  byte-identical duplicates** of one run. Filenames carry no identity, so answers must be classified
  by reading them — this project has already had two arrive with their contents **swapped**. And a
  generated evidence pack matched the prompt glob and rendered a source file into the research tab.

  So: **what should the surface for running research passes look like?** Composing a prompt against
  a live view of what is already asked and answered; dispatching without a copy-paste round trip if
  anything in the corpus has solved that; tracking what is in flight and for how long; ingesting an
  answer without a filename dance; showing where two passes disagree. **Does any repository in the
  corpus manage long-running external work like this, and what does its interface do?** If nothing
  does, say so — that is a finding, and we will design it ourselves.

- **The first screen to build**, and the measurement that would prove it worked.

### 5.3 Sequenced, because we are not starting clean

Four interfaces already exist and one is dead. Give the migration: the smallest change with the
largest effect, what runs in parallel with what exists, what is retired and when, and **what must
not be built yet.**

---

## 6. Constraints — a recommendation that breaks one of these is not usable

- **Windows-first** on the operator's machine. WSL is available; say exactly what changes.
- **Small team.** Anything needing a platform team to operate is wrong regardless of merit.
- **Three concurrent lanes today.** A design assuming ten agents answers a question we do not have.
- **Per-secret human approval is a hard rule.** No batch-approval of credentials, ever, however
  elegant. Batch-approving *file reads* is a separate question and is open.
- **No unlabelled stale numbers.** A cached figure carries its age in the same string as the figure,
  or it is not shown.
- **The existing instrument panel is added to, never removed.**
- **Evidence-gated deploys**: prove the target object, validate at the layer the consumer reads,
  prove no regression, capture a rollback, then deploy.

### ⚠ Two questions to answer deliberately, not by accident

1. **The embedded terminal.** We have a standing rule that no terminal is embedded in a page; the
   operator's current position is that terminal mode should *exit* — an escape hatch, not the
   interface. **R13 owns the argument.** Your job is the evidence: **what does the corpus actually
   do**, how many of the tools you read embed a terminal, what did the ones that did not do
   instead, and did any project visibly move in either direction? Report it as data. Do not restate
   our position back to us — a prior pass did exactly that, and another was never told the rule
   existed and recommended a tool the rule had ruled out.
2. **Build vs adopt vs fork.** A conclusion of *"repository X is 80% of this, fork it"* is a better
   outcome than a design, and we are not attached to building. If that is the answer, say it in the
   first paragraph and cost the fork honestly: what we inherit, what we must patch, and what we
   lose that we have today (lanes, claims, gates, the four-valued verdict).

## 7. Deliverable shape

1. **Executive answer** — the architecture and the first screen, in under 300 words. Build, adopt or
   fork, decided.
2. **The corpus method** — inclusion rule, enumeration walk, exclusion log, cut-off, read-tier per
   repo.
3. **The extraction table** — §4's schema, one row per repository.
4. **`CLAIM vs CODE` divergences** — every one found, with file and line.
5. **What to fix in ours first** (§5.0) — ranked, each with our file/line, their
   file/line, the failure it prevents, and whether it blocks the UI work.
6. **The architecture** (§5.1), with the runner-up and why it lost.
7. **The UI** (§5.2), screens in priority order, with the latency budget.
8. **The question-to-human channel**, and the approval surface including the non-engineer question.
9. **The sequenced migration** (§5.3).
10. **What you would refuse to build, and why.**
11. **What you could not determine, named** — see §8.

## 8. Tier every claim, and name what you could not see

`OBSERVED` — you read the source or ran it · `REPORTED` — a credible postmortem, paper or
production write-up · `MARKETED` — the vendor or README says so and nobody independent confirmed it
· `INFERRED` — your reasoning from the above.

**A `MARKETED` claim may not be used as a design premise.** We have been burned specifically by
this: a gate that reported PASS while measuring nothing, a detector that silently degraded to
reporting 1 finding where the real engine reports 313, and a launcher that announced one model
while running another. **Assume any capability whose source or documentation you have not seen is
absent until proven otherwise.**

And distinguish these four, which are not the same and must never collapse into "it doesn't do
that":

```
ABSENT          you read the source and the capability is not there
NOT-DETERMINED  you did not read enough to say
UNREADABLE      closed source, obfuscated, or behind a paywall
NOT-SUPPLIED    we owed you a document and did not provide it — name it and we will
```

**A gap you name is worth more to us than a gap you fill.**
