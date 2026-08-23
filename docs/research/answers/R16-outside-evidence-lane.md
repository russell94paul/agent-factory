# R16 — The outside-evidence lane: what the field actually reports, and where our sequencing has no support

**Answered 2026-08-23, from the open web first and our record second.** I did not open
`SYNTHESIS.md` or any file in `answers/` until §1–§5 below were formed. The order matters: this lane
exists to give the inside audit something to be wrong *against*, and a lane that boots from our own
conclusions is worth nothing. Our positions are read and quoted from §6 onward.

**Tiers.** `OBSERVED` — someone ran it and reported a result, or I read the raw artefact myself ·
`DERIVED` — reasoned from something observed, including simulations · `ASSUMED` — asserted without
a mechanism · `MARKETED` — vendor documentation for a capability nobody in the citation has
exercised. No `MARKETED` claim is load-bearing anywhere below. Where the field has published
nothing I say **nobody has published this** rather than filling the gap with the nearest adjacent
literature.

**What "the field" turned out to be.** Five modalities were swept: vendor engineering blogs, the
raw specs and repos (`registry.yaml`, `README.md`, the releases page), one survey with an n,
practitioner complaint threads, and arXiv. The single most important structural fact about the
corpus is this: **almost nobody in it is building what we call a control plane.** When the field
writes "orchestration layer" it means a framework — LangGraph, ADK, a topology — not caps,
reaping, refusal gates and tenant isolation. That mismatch is not a gap in my search; it decides
three of the five verdicts below, and it is stated inline each time rather than papered over.

---

## 0. Executive summary

Six things, ordered by how much they should change what we do.

1. **⛔ §14.3's "three independent sources" is one source read three times.** R13's stated basis is
   *"the measured backlog shows humans are the bottleneck"* and R12's text says *"we saw four agents
   stuck with unanswered questions"* (`R12-answer-session-manager-ui.md:58`). Both reason **from the
   same 2026-08-23 measurement**, which §14.3 lists as the third leg of the tripod. That is one
   measurement plus two passes that read it — the echo the lane brief suspected, confirmed in our
   own text. R13 says so itself: *"there are no studies on AI-agent prompts specifically."*
   **Nobody has published a build-order claim that the notification channel comes first.**

2. **⭐ The strongest external finding we appear not to know: oversight has a capacity, and safety
   is an inverted-U in escalation rate.** *Oversight Has a Capacity: Calibrating Agent Guards to a
   Subjective, Fatiguing Human* (Turan, 11 Aug 2026, arXiv 2606.08919) finds that under a paranoid
   policy escalating **88% of routine actions, attack success reaches ~80%** and is **already 40% at
   just 50 filler actions**, and concludes *"escalating everything is strictly worse than the
   optimum."* `DERIVED` — the author states plainly *"the inverted-U is simulated, not measured."*
   a14 as written names a **channel** and no **routing policy**. A channel with no policy is exactly
   the design that paper puts on the bad side of the curve.

3. **a16 is a much smaller answer than §14.5 claims. The OTel GenAI field set covers 5 of our 15
   version dimensions and misses every one §14.5 says bites.** Read from the raw
   `model/gen-ai/registry.yaml` (72 attributes): it has `gen_ai.prompt.version`,
   `gen_ai.request.model`, `gen_ai.request.reasoning.level`, `gen_ai.tool.definitions` and
   `gen_ai.data_source.id`. It has **nothing** for `contract_version`, `permissions`,
   `sandbox_image`, `harness_version`, `max_turns`, `budget_usd`, `model_routing`, `context_policy`,
   `tool_implementation` or `side_effect_replay` — and **no commit-hash attribute at all**, which
   §14.5 explicitly lists as one it names. `OBSERVED`.

4. **⚠ And its maturity is worse than "experimental".** Every attribute in that file is
   `stability: development`; the `gen_ai.*` attributes were **deprecated out of the main semconv
   registry** and moved to a separate repo; that repo has **zero releases** ("There aren't any
   releases here"); and its README's Schema URL section reads, in full, **`TODO`**. You cannot
   version-pin what you emit against it. `OBSERVED` — I read the YAML, the README and the releases
   page.

5. **⚠ a8's gate binding is vacuous, and the roadmap's own `contradictions()` is the reason to
   care.** a8 is *"containerise agent execution on one machine before any cloud step"* wired to
   `gate="isolated"`. Gate `isolated` asks *"Is the evaluator a principal the agent cannot
   impersonate?"* (`readiness.py:1092`) and its probe checks `$AGENT_FACTORY_EVALUATOR` and for a
   module defining `class EvaluatorClient` (`readiness.py:892-897`). **Standing up an evaluator
   service flips a8 to `SHIPPED`/`MEASURED` with zero containers running.** Found while checking the
   external claim; it is cheap to check and cheap to fix.

6. **The cap the outside names and we do not: human review throughput.** Our concurrency answer
   (§14.1, a15) is about writers and files. The field's practitioners name a second ceiling —
   *"with each agent you have more code to review"* — and our own measurement (two green PRs at
   6 and 9 days) **is** that ceiling. We filed it under notification. It is also a concurrency
   finding: **the estate's binding limit last month was not 3 lanes, it was 1 reviewer**, and a
   notification channel does not add review capacity. It makes the queue arrive faster at the
   thing item 2 says degrades under load.

---

## 1. (a) Does the eval harness come before or after the control plane?

### What the field's evidence says

**There is no published evidence on this ordering, because the field does not build our control
plane.** Every source that discusses "orchestration first" means a framework choice. What the field
*does* have hard data on is the ordering of **observability vs evals**, and that data is one-sided.

| Instrument | Adoption | Tier |
|---|---|---|
| Observability (any) | **89%** — 94% among teams with agents in production | `OBSERVED` (self-report) |
| Detailed step/tool tracing | **62%** — 71.5% in production | `OBSERVED` |
| Offline evals on test sets | **52.4%** | `OBSERVED` |
| Online evals | **37.3%** | `OBSERVED` |
| Human review | **59.8%** | `OBSERVED` |
| LLM-as-judge | **53.3%** | `OBSERVED` |

LangChain, *State of Agent Engineering*, **n=1,340, fielded 18 Nov – 2 Dec 2025**; 57% had agents in
production. <https://www.langchain.com/state-of-agent-engineering>

**The 37-point gap between tracing and offline evals is the finding.** Teams instrument the trace
substrate first and build evals later — and every practitioner who has written about the sequence
says the lag is the mistake, not the plan:

> *"Evals get harder to build the longer you wait. Early on, product requirements naturally
> translate into test cases. Wait too long and you're reverse-engineering success criteria from a
> live system."*
> — Anthropic, *Demystifying evals for AI agents*.
> <https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents> · `REPORTED`

> *"We see teams delay building evals because they think they need hundreds of tasks. In reality,
> 20-50 simple tasks drawn from real failures is a great start."* — same source. `REPORTED`

Anthropic's multi-agent research system started evaluating at **~20 queries**, on the grounds that
*"changes tend to have dramatic impacts"* early enough to be visible in a few cases, and graded on
**end state rather than each step** — *"whether it achieved the correct final state"*, so the agent
may find alternative paths. <https://www.anthropic.com/engineering/multi-agent-research-system> ·
`OBSERVED` (they ran it; 90.2% improvement over single-agent Opus 4 on their internal eval, at ~15×
the tokens of a chat interaction).

Hamel Husain's position — the most-cited practitioner text on this — inverts the naive order:
**read real outputs one by one, categorise the failures, and only then choose metrics.** Error
analysis *"takes 2-3 hours but is often the step most teams skip."*
<https://hamel.dev/blog/posts/evals/> · `REPORTED`

**A structural datum, not an opinion:** the OTel GenAI registry now carries
`gen_ai.evaluation.name`, `gen_ai.evaluation.score.value`, `gen_ai.evaluation.score.label` and
`gen_ai.evaluation.explanation`. The standards body models evaluation as a **signal emitted onto the
trace substrate** — telemetry is upstream of evals by construction, not by preference. `OBSERVED`,
raw `registry.yaml`.

**Counter-evidence I went looking for and did not find.** I searched specifically for a team
reporting that they built evals too early and wasted the effort. **Nobody has published this.** The
nearest thing is Anthropic's harness-design post, where an evaluator *agent* became *"unnecessary
overhead"* for easy tasks under a stronger model while *"continu[ing] to give real lift"* at the
capability boundary — that is a claim about runtime scaffolding, not about an eval corpus, and it
does not transfer. <https://www.anthropic.com/engineering/harness-design-long-running-apps> ·
`REPORTED`

### What we decided

§5 — the merged R3/R4 build order, unamended by R5:

```
1  hard external attempt / spend / concurrency budget
2  cloud timeout + cancellation + orphan reaping + restart reconciliation
3  terminal verdict computed from append-only history, not current state
4  refusal-capable gates, with negative drills
5  tenant capability isolation
6  complete attempt/cost telemetry, including failures
7  external evaluator trust boundary (a service, not a directory)
8  expand and freeze the evaluation corpus
9  ── only here ── configuration experiments
```

Control plane 1–5, telemetry 6, evaluator 7, corpus 8.

### Does the evidence support it?

**Partly, and the unsupported part is specific: telemetry at 6.**

- Steps 1–2 and 4–5 have **no external counterpart to contradict** — the field is not building them,
  so their position is neither supported nor opposed. Saying "the evidence supports our control
  plane first" would be reading a silence as agreement. It is a silence.
- **Step 6 is the one position the outside evidence actively argues against.** Every source that
  orders anything puts the trace substrate first: the survey (89% vs 52%), Anthropic ("reverse-
  engineering success criteria from a live system"), Hamel (error analysis *on real traces* precedes
  metric choice), and OTel (evaluation is a span attribute). Placing *"complete attempt/cost
  telemetry, including failures"* sixth means five steps of control-plane work are built and
  debugged against a log that is not yet complete.
- **And our own order may already contradict itself here.** Step 3 is *"terminal verdict computed
  from append-only history"* — that **is** the trace substrate — while step 6 is the telemetry that
  fills it. One of those two is misplaced. This is checkable inside the repo and I have not
  attempted to resolve it; it is named, not settled.

**Verdict: NOT SUPPORTED for step 6's position. NO EXTERNAL EVIDENCE EITHER WAY for steps 1–5.**

---

## 2. (b) Is "build the notification channel first" supported, or is it folklore?

### What the field's evidence says

**Nobody has published a build-order claim for the notification channel.** I searched vendor blogs,
engineering post-mortems, practitioner threads and arXiv on five differently-shaped queries. The
literature that exists is about **where approval gates belong**, not **when to build the channel** —
and what it says cuts against the naive form of our action.

**Finding 1 — a pausable HITL is not a standalone artefact; it sits on durable state.**
LangGraph's HITL exists because *"every step of the graph… reads from and then writes to a
checkpoint of that graph state"*, which is *"what makes it possible to pause execution of the graph
half way through, and then resume after some time."*
<https://www.langchain.com/blog/making-it-easier-to-build-human-in-the-loop-agents-with-interrupt> ·
`MARKETED` (their own product, and the mechanism is documented rather than demonstrated).

The failure mode of skipping that substrate is named concretely: implementing HITL as a blocking
HTTP call fails on hard infrastructure timeouts (*"AWS API Gateway drops connections after 29
seconds"*), process restarts destroying in-memory call stacks, OAuth tokens expiring during the
wait, and pagination cursors going stale.
<https://truto.one/blog/implementing-human-in-the-loop-approval-workflows-for-consequential-saas-api-actions/>
· `DERIVED` — I checked, and this is architectural reasoning; **the author cites no incident,
customer or post-mortem for the "within a week" figure.**

**Finding 2 — ⭐ and this is the one we appear not to know — more notification is not monotonically
better.** *Oversight Has a Capacity: Calibrating Agent Guards to a Subjective, Fatiguing Human*
(Emre Turan, independent researcher, 11 Aug 2026), on 125 hand-labelled agent actions:

| Result | Value |
|---|---|
| Inter-reviewer agreement on risk labels | **κ = 0.52** (moderate — there is no ground truth) |
| Attack success, paranoid policy (88% escalation) | **~80%** ceiling; **40% at 50 filler actions** |
| Attack success, load-aware policy | **0% until ~100 filler actions** — *"roughly 2× the headroom"* |
| Safety-optimal escalation rate, capacity 25 | **64%** escalation, 42% danger-through |
| Conclusion | *"escalating everything is strictly worse than the optimum"* |

<https://arxiv.org/html/2606.08919v1> · **`DERIVED`, and the paper says so itself**: *"the inverted-U
is simulated, not measured"*; reviewer personas are LLM proxies, not humans. It is not proof. It is
the only quantitative treatment of the question in the corpus, and its direction is the opposite of
"surface everything intrusively."

**Finding 3 — approval fatigue is the field's named failure mode for a channel built without a
policy.** The recurring practitioner formulation: reviewers *"skim requests and click approve, and
after 40 times they're no longer reviewing — they're rubber-stamping."*
<https://aipatternbook.com/approval-fatigue> · `ASSUMED` (no measurement behind the number 40).
Cursor is reported to have hit this and moved from gating every step to risk classification, while
Copilot Workspace gates every step — the two live products disagree.

### What we decided

a14: *"Build the notification channel first — three passes and one measurement agree."*
§14.3 assembles the tripod as: the 2026-08-23 measurement (two PRs green at 6 and 9 days; four
agents blocked on unread questions), R12 §4.2 (*alarm absence*, not alarm fatigue), R13 §6 (*"our
failure is not over-alerting (fatigue) but under-alerting"*). *"When three passes and one
measurement agree, stop asking and build it."*

### Does the evidence support it?

**⛔ No — and the internal consensus does not hold up either.**

1. **The three sources are not independent.** §14.3's own quotation of R13 gives its basis as
   *"since the measured backlog shows humans are the bottleneck (agents queue for days)"* — R13 is
   reasoning **from** the measurement. R12 does the same in its own words: *"we saw four agents
   stuck with unanswered questions"* and *"(We saw 4 blocked jobs silently waiting.)"*
   (`R12-answer-session-manager-ui.md:37,58`). **Strip the shared premise and the tripod is one
   measurement and zero independent arrivals.** R12's only external support is the Nielsen Norman
   Group on action-required notifications — a general UX guideline about how a notification should
   behave, not evidence about when to build one.
2. **The measurement is real and it supports something narrower.** Two PRs waiting 6 and 9 days and
   four unread questions is an *unread-queue* problem. It is evidence for **making the pending set
   visible and interrupting**, which is a small thing. It is not evidence for a build order, and it
   is not evidence for an approval plane.
3. **The strongest available research points the other way past a threshold.** Turan's inverted-U
   says a channel with no routing policy is the worst-performing configuration once volume rises. We
   currently run twelve concurrent sessions; the volume side of that curve is not hypothetical.
4. **The dependency is inverted relative to our order.** If the channel is ever to *pause* an agent
   rather than merely alert a human, it needs the durable checkpoint underneath it — which is our
   §5 steps 2 and 3. "Notification first" is only coherent as fire-and-forget alerting.

**Verdict: NOT SUPPORTED as a build-order claim. It is folklore in the precise sense the brief
meant — an internal consensus with one shared premise and no external leg.** The narrow version
("surface the blocked set, and make it interrupt", which is already a3) is supported by the
measurement alone and should be sized accordingly.

---

## 3. (c) When do teams hit the wall that forces containerisation?

### What the field's evidence says

**The wall is hit locally, at the moment permission prompts are turned off on a machine that holds
credentials.** It is not tied to a cloud step at all. The incident record is unusually concrete for
this field:

| Date | Incident | Source tier |
|---|---|---|
| 21 Oct 2025 | `claude-code` issue #10077 — `rm -rf` from root on Ubuntu/WSL2 deleted all user-owned files. **The user was not running `--dangerously-skip-permissions`.** | `OBSERVED`, reported via Docker |
| 28 Nov 2025 | `claude-code` issue #12637 — agent created a directory literally named `~`, then cleaned up with an unquoted `rm -rf ~`; shell expansion took the home directory | `OBSERVED`, reported via Docker |
| 8 Dec 2025 | r/ClaudeAI — *"Claude CLI deleted my entire home directory! Wiped my whole mac."* Command: `rm -rf tests/ patches/ plan/ ~/` | `OBSERVED`, reported via Docker |
| Jan 2026 | Claude Cowork asked to tidy a desktop; 15–27,000 family photos deleted, **Trash bypassed**; recovered only via iCloud's 30-day retention | `OBSERVED`, reported via Docker |
| undated | Pulumi internal Slack: an engineer's agent ran `rm -rf $HOME` **outside the sandbox** | `OBSERVED`, first-party |

<https://www.docker.com/blog/coding-agent-horror-stories-the-rm-rf-incident/> ·
<https://www.pulumi.com/blog/sandboxing-coding-agents-yolo-mode/>

⚠ I have **not** independently opened the two GitHub issues or the Reddit thread; they are
`OBSERVED`-via-Docker, one hop. The Pulumi incident is first-party to its author.

The mechanism the field names is not "the agent went rogue" but the execution model: *"the agent
runs as you, on your filesystem, with your credentials, and nothing sits between the model's
decision and the shell's execution."* Pulumi puts credentials first explicitly — *"my laptop holds
more than source files. It holds AWS credentials, kubeconfigs that point at real clusters, and
Pulumi access tokens"* — and notes agents will read `~/.ssh` on request *"immediately, no protest at
all."*

**Two qualifications the field is firm about, and both are omissions we should check ourselves
against:**

1. **Filesystem isolation alone is not isolation.** Willison: effective isolation needs *both*
   filesystem and network limits — *"without network isolation an agent can exfiltrate SSH keys."*
   Locking egress to a trusted host list is the specific control.
   <https://simonwillison.net/2025/Sep/30/designing-agentic-loops/> · `REPORTED`
2. **A container does not touch prompt injection.** The lethal trifecta — *"access to your private
   data"* + *"exposure to untrusted content"* + *"the ability to externally communicate"* — survives
   containerisation intact, because the sandbox does not remove any of the three.
   <https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/> · `REPORTED`. A practitioner running
   `sbx` in July 2026 says it flatly: the sandbox *"offers no real isolation and no protection
   against prompt injection"*, and *"there is not yet a way to hide or mask individual files in the
   project folder."* <https://www.innoq.com/en/blog/2026/07/trust-but-sandbox/> · `OBSERVED`.

The field's stated trigger is categorical, not staged: *"Stop running coding agents directly on your
host. Containerization or microVM isolation should be the default, not an advanced option."*

### What we decided

a8: *"Containerise agent execution on one machine before any cloud step."* (§13.7.2, from R8's
smallest-impactful-change, justified by *"the first break will be credentials isolation"* and F53.)
§13.1 records the current state: *"local worktree, processes as the user, no network block"* and
*"the operator's own Azure and Snowflake creds, unrestricted."*

### Does the evidence support it?

**Yes on substance — the credentials-first argument is exactly what the field reports — but the
trigger is named too late, and by our own §13.1 the wall is already behind us.**

- ✅ *"The first break will be credentials isolation"* is the single most corroborated claim in this
  document. Pulumi, Docker and Willison independently name credentials as what leaves first.
- ✅ *"First prove isolation locally"* over a cloud cluster is supported: every incident above
  happened on a laptop.
- ⚠ **"Before any cloud step" is the wrong boundary.** The field's boundary is "before running
  unattended on a machine that holds credentials." §13.1 says we run as the user, unrestricted, with
  live Azure and Snowflake creds and no network block. **We are already past the trigger the
  evidence names, and a8 is phrased as though it is ahead of us.** That is a wording change with a
  priority consequence.
- ⚠ **Two controls the field insists on are not visible in a8.** Network egress restriction —
  R5's amendment to §5 step 1 does say *"no network by default"*, so the substance exists at step 1
  but is not carried into a8's text — and an acknowledgement that the container does **nothing** for
  prompt injection. If a8 ships as filesystem isolation only, the estate will have bought protection
  against `rm -rf` and none against exfiltration, which is the failure mode with the worse tail.
- ⚠ **Nobody has published cost or throughput data for containerised agent execution at our size.**
  R8's *"potentially 10+ on a modern server"* has no external counterpart; the field publishes boot
  times, not steady-state throughput.

**Verdict: SUPPORTED in substance, MIS-STATED in trigger, INCOMPLETE in scope (egress + injection).**

---

## 4. (d) Is the OpenTelemetry GenAI field set the real answer for config/version provenance?

### What the spec actually says — read from source, not a blog

**The whole `gen_ai.*` set was deprecated out of the main semantic-conventions registry.** The
canonical registry page now renders, for `gen_ai.agent.id`, `gen_ai.agent.name`,
`gen_ai.agent.description` and `gen_ai.agent.version`, the identical label:
**`Deprecated — Moved to the OpenTelemetry GenAI semantic conventions repository`**.
<https://opentelemetry.io/docs/specs/semconv/registry/attributes/gen-ai/> · `OBSERVED`

In the repository they moved to:

| Fact | Value | Source |
|---|---|---|
| Repository status banner | **`Status: Development`** | `docs/gen-ai/README.md` |
| Stability of every attribute in the registry | **`stability: development`** — no attribute in the file carries any other value | raw `model/gen-ai/registry.yaml` |
| Releases | **"There aren't any releases here"** | <https://github.com/open-telemetry/semantic-conventions-genai/releases> |
| README `## Schema URL` section, in full | **`TODO`** | raw `README.md` |
| Attributes defined | **72** | raw `registry.yaml` |

`OBSERVED` — I read `README.md`, `registry.yaml` and the releases page directly, not a summary.
**Zero releases plus an unwritten Schema URL means telemetry emitted against these conventions today
cannot be version-pinned to the convention that produced it** — which is a pointed thing to discover
about a standard we are adopting *in order to fix version provenance*.

Adoption is thin where it matters, from the repo's own conformance matrix
(`reference/README.md`, generated from committed scenario data): Create-Agent spans in **6**
libraries, Invoke-Agent-Internal in **7**, Plan in **2** (crewai, langchain), Memory in **2**,
Evaluation-Result events in **3**. Inference is the only well-covered signal at 15. `OBSERVED`.

### The field-by-field map against our 15 dimensions

`VERSION_DIMENSIONS` (`readiness.py:859-864`) against the 72 attributes:

| Our dimension | OTel GenAI attribute | Covered? |
|---|---|---|
| `prompt` | `gen_ai.prompt.name`, `gen_ai.prompt.version` — *"The version of the prompt template used."* | ✅ |
| `model` | `gen_ai.request.model`, `gen_ai.response.model` | ✅ |
| `effort` | `gen_ai.request.reasoning.level` — *"The reasoning or thinking effort level requested."* | ✅ |
| `tools` | `gen_ai.tool.definitions` — *"The list of tool definitions available to the GenAI agent or model."* | ✅ (definitions, **not versions**) |
| `external_knowledge` | `gen_ai.data_source.id`, `gen_ai.memory.store.id` | ◐ identifies the source, not its content or version |
| `context_policy` | `gen_ai.conversation.compacted` (a boolean fact about one run) | ✗ no policy identifier |
| `max_turns` | — | ✗ |
| `budget_usd` | — (token counts only; **no cost attribute exists**) | ✗ |
| `tool_implementation` | — | ✗ |
| `sandbox_image` | — | ✗ |
| `model_routing` | — | ✗ |
| `permissions` | — | ✗ |
| `contract_version` | — | ✗ |
| `harness_version` | — (`gen_ai.agent.version` is the agent, not the harness) | ✗ |
| `side_effect_replay` | — | ✗ |

**5 covered, 1 partial, 9 absent.**

### What we decided

a16: *"Config hash: adopt the OTel GenAI field set."* §14.5: *"That is directly actionable against
the config hash covering 0 of 15 dimensions: the dimensions it names — model ID, prompt version,
tool versions, commit hash, agent ID — are the hash."*

### Does the evidence support it?

**⛔ No, as stated. Three specific defects, all checkable against the raw spec.**

1. **The list in §14.5 is wrong in two places.** *"Tool versions"* — the spec has
   `gen_ai.tool.definitions`, the declared schema available to the model, not a version of the
   implementation behind it. *"Commit hash"* — **there is no commit, repo, ref or SHA attribute
   anywhere in the 72.** Two of the five items §14.5 cites as the payoff are not in the artefact.
2. **The dimensions it does cover are not the ones that bite.** `g_version_hash_is_complete`
   singles out `contract_version` as the one that bites now — *"a certification granted under
   contract V4 silently transfers to V5"* (`readiness.py:874-876`). OTel GenAI has no attribute for
   it, nor for `permissions`, `sandbox_image` or `harness_version`. **The adoption closes the easy
   third of the gap and leaves the certification-relevant two-thirds exactly where it was.**
3. **⚠ Category error, and it has a mechanical consequence.** OTel GenAI is an **observability
   vocabulary** — names for span attributes describing what happened during one call. It is not a
   configuration-identity scheme and does not say what to hash. Our gate greps
   `factory/blueprint.py` for our own literal dimension names (`readiness.py:870`), so
   **renaming our dimensions to OTel names would break the gate**, and **adding the names to
   blueprint.py without hashing them would pass it.** Both are false verdicts in opposite
   directions; the second is the shape this project exists to stop.

**What the field says is the real answer for artefact provenance: nobody has one.** The nearest
serious framing — *which model and version produced this change? what prompt or task spec drove it?
which tools was it allowed to call? which tests and evals gated it?* — is answered by adapting
SLSA / in-toto / Sigstore, and its own author concedes the supply-chain toolchain *"was not built
for agents."* No standard purpose-built for agent-artefact provenance exists, and the article's
worked example is ~20 lines of illustrative pseudocode with **no named deployment behind it**.
<https://devops.com/the-agent-proposes-the-pipeline-disposes-controls-for-ai-authored-change/> ·
`ASSUMED`.

**Verdict: NOT SUPPORTED as written.** The defensible version is narrower and worth having anyway:
*adopt OTel GenAI attribute **names** for the five dimensions it covers, so our traces interoperate;
keep our own hash as the authority, and record that ten dimensions have no standard name and are
ours to define.* That is a naming decision, not a provenance answer, and a16 currently reads as the
second.

---

## 5. (e) What actually caps parallel agent work?

### What the field's evidence says

Practitioner threads are the right modality here, and they converge on **three** caps, not one.

**Cap 1 — the git layer (supports us).**

> *"The conflict surface really is at the git layer… if you need human review before merge
> (regulated codebase, production infra), you want gates. Throughput vs. safety."*
> — `reflectt`, <https://news.ycombinator.com/item?id=47284948> · `OBSERVED`

> *"as the project matured… every new feature is cross-cutting and it's impossible to parallelize
> the work without running into conflicts"*
> — `_sinelaw_`, <https://news.ycombinator.com/item?id=46999369> · `OBSERVED`

⭐ The second quote is the sharper one and it is a *worsening* function: the cap is **architectural
coupling**, and it tightens as a codebase matures. Re-scoping what agents touch buys headroom
against file identity; it does not buy headroom against cross-cutting features. Shared hotspot
files — *routes, configs, registries* — are named as the predictable collision sites.
<https://www.augmentcode.com/guides/git-worktrees-parallel-ai-agent-execution>

One practitioner runs an explicit mutex rather than relying on worktrees: *"Before editing ANY
files, you MUST… Check for existing reservations… If another agent holds an exclusive reservation,
DO NOT EDIT those files."* — `bobjordan`,
<https://news.ycombinator.com/item?id=46674404> · `OBSERVED`.

**Cap 2 — human review throughput (we do not name this as a concurrency cap).**

> *"with each agent you have more code to review… if you don't do a good enough division you'll get
> a fair share of merge conflicts to fix later"*
> — `yerik`, <https://news.ycombinator.com/item?id=47903824> · `OBSERVED`

Practitioner consensus lands at **2–4** concurrent agents, *"beyond that the overhead of
coordinating tasks, reviewing outputs, and managing merges starts to outweigh the parallelism
benefit."* <https://www.augmentcode.com/guides/how-to-run-a-multi-agent-coding-workspace> ·
`REPORTED`.

**Cap 3 — synthesis and tooling, which is not a file-conflict cap at all.** Anthropic's research
system runs **3–5 subagents in parallel** at **~15× the tokens of a chat interaction** — read-only
fan-out with zero file conflicts, capped by cost and by the lead agent's ability to synthesise.
Claude Code enforces a **hard default of 20** concurrent subagents (`Concurrent subagent limit
reached`), configurable via `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS`, with excess requests queued.
<https://code.claude.com/docs/en/sub-agents> · `OBSERVED`, read from the docs.

### What we decided

§14.1 / a15: *"Stop surveying orchestration topologies — seven checked, none moves the cap."*
R13: *"raising the concurrency ceiling depends on task structure, not the orchestration style."*
R8, from the other side: change the task structure and the ceiling becomes resource-bound,
*"potentially 10+"*. §14.1 calls the convergence *"the strongest result in this document."*

### Does the evidence support it?

**Yes — this is our best-supported position, and it needs two amendments.**

- ✅ **Topology buys nothing.** Nothing in the practitioner corpus attributes a concurrency ceiling
  to orchestration style. Every account names files, branches, review, tokens or quotas. a15 is
  sound and the survey should stay closed.
- ✅ **Task structure is the lever.** Corroborated by the worktree literature and by `bobjordan`'s
  hand-rolled file-reservation protocol — someone reached for exactly our answer independently.
- ⚠ **Amendment 1: file conflicts cap *writers*, and only writers.** For read-only fan-out the caps
  are synthesis overhead, token cost and a tool-enforced ceiling of 20. §14.1's *"re-scoping what
  they touch buys everything"* is correct for writers and **untested for readers** — and R16's own
  lanes are read-heavy. If the estate's next scaling step is research fan-out rather than lane work,
  the file-conflict answer does not apply to it.
- ⛔ **Amendment 2: the cap we actually hit last month was human review, and we did not file it as
  one.** `yerik`'s *"with each agent you have more code to review"* plus the field's 2–4 consensus
  says review is the binding constraint before files are. **Our own measurement — two green PRs at 6
  and 9 days — is that constraint, measured, and §14.3 files it under notification.** Under
  Turan's result, notifying harder past a reviewer's capacity moves the system down the far side of
  the inverted-U. **The cheapest real concurrency gain available to this estate is not 10 containers
  and not a better topology; it is a second reviewer, or a class of change that does not need one.**
- Note: R14 §0.4 (*`lane` is four objects wearing one string* — work package, conflict key, branch,
  directory, claim key, ledger key) is a **stronger and more specific** version of this finding than
  anything outside, arrived at from our own source. The outside evidence corroborates it; it does
  not improve on it.

**Verdict: SUPPORTED, with the reader case untested and the review-throughput cap missing.**

---

## 6. Where we have no external support at all

Stated plainly, because a decision resting only on our own passes is a finding.

| Decision | External support |
|---|---|
| a14 — build the notification channel first | **None.** No published build-order claim exists. R13 concedes *"no studies on AI-agent prompts specifically."* The three internal legs share one premise. |
| §5 steps 1–5 — control plane before telemetry and evals | **None either way.** The field does not build this control plane, so its silence is not agreement. Step 6's *position* is contradicted; steps 1–5 are simply unexamined by anyone. |
| a10 — 30–45 min unbroken run as the unattended target | **Consistent with**, not supported by. §13.3's ~45-minute figure is `REPORTED` at one hop; I found no published distribution of autonomous-turn durations to corroborate it. |
| a12 — take R8's isolation, drop its scheduling/messaging | **None.** A judgement about our constraints; correctly ours to make. |
| a13 — VS Code extension over desktop app | **Not examined in this lane.** Out of scope; unverified here. |
| R8's *"potentially 10+ agents on a modern server"* | **None.** The field publishes microVM boot times (Firecracker ~100–200 ms), never steady-state agent throughput. It is `ASSUMED`. |
| "10+ concurrent agents is achievable at all" | **Contradicted by practitioner consensus** (2–4), though every one of those reports is about *writers* on a shared repo. |

---

## 7. What I could not settle

- **Whether any team has built our shape of control plane.** I did not find one. That may be a
  search limit rather than an absence — the discriminating test would be an enterprise post-mortem
  that names attempt caps, orphan reaping and refusal gates as *platform* components. I did not
  find one, and I am not claiming they do not exist.
- **The two `claude-code` GitHub issues and the Reddit thread** are cited via Docker's blog at one
  hop. Opening #10077 and #12637 directly is cheap and would promote four `OBSERVED`-via-one-hop
  incidents to first-hand.
- **Whether §5's step 3 and step 6 are the same substrate.** Named in §1; resolving it needs a read
  of our own event log implementation, which is the inside lane's territory, not mine.
- **Cost.** Nothing in the corpus prices containerised agent execution, sandbox overhead, or the
  token multiple of a fan-out at our size beyond Anthropic's *"~15× the tokens of a chat
  interaction"*. Any cost figure in our record is `ASSUMED` until someone runs it.

---

## Sources

Specs and repositories (read at source):
- <https://raw.githubusercontent.com/open-telemetry/semantic-conventions-genai/main/model/gen-ai/registry.yaml>
- <https://raw.githubusercontent.com/open-telemetry/semantic-conventions-genai/main/README.md>
- <https://github.com/open-telemetry/semantic-conventions-genai/releases>
- <https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-agent-spans.md>
- <https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/README.md>
- <https://raw.githubusercontent.com/open-telemetry/semantic-conventions-genai/main/reference/README.md>
- <https://opentelemetry.io/docs/specs/semconv/registry/attributes/gen-ai/>
- <https://code.claude.com/docs/en/sub-agents>

Vendor engineering write-ups:
- <https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents>
- <https://www.anthropic.com/engineering/multi-agent-research-system>
- <https://www.anthropic.com/engineering/harness-design-long-running-apps>
- <https://www.langchain.com/blog/making-it-easier-to-build-human-in-the-loop-agents-with-interrupt>
- <https://developers.googleblog.com/production-ready-ai-agents-5-lessons-from-refactoring-a-monolith/>
- <https://cloud.google.com/blog/topics/startups/four-steps-for-startups-to-build-multi-agent-systems>

Survey data:
- <https://www.langchain.com/state-of-agent-engineering> (n=1,340; 18 Nov – 2 Dec 2025)

Incidents and sandboxing:
- <https://www.docker.com/blog/coding-agent-horror-stories-the-rm-rf-incident/>
- <https://www.pulumi.com/blog/sandboxing-coding-agents-yolo-mode/>
- <https://www.innoq.com/en/blog/2026/07/trust-but-sandbox/> (3 Jul 2026)
- <https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/>
- <https://simonwillison.net/2025/Sep/30/designing-agentic-loops/>

Research:
- <https://arxiv.org/html/2606.08919v1> — Turan, *Oversight Has a Capacity*, 11 Aug 2026

Practitioner threads (Hacker News, via the Algolia API):
- <https://news.ycombinator.com/item?id=47284948> · <https://news.ycombinator.com/item?id=46999369>
- <https://news.ycombinator.com/item?id=47903824> · <https://news.ycombinator.com/item?id=46674404>
- <https://news.ycombinator.com/item?id=46429365>

Practitioner writing (tiered `REPORTED`/`ASSUMED` above):
- <https://hamel.dev/blog/posts/evals/>
- <https://www.augmentcode.com/guides/git-worktrees-parallel-ai-agent-execution>
- <https://www.augmentcode.com/guides/how-to-run-a-multi-agent-coding-workspace>
- <https://truto.one/blog/implementing-human-in-the-loop-approval-workflows-for-consequential-saas-api-actions/>
- <https://devops.com/the-agent-proposes-the-pipeline-disposes-controls-for-ai-authored-change/>
- <https://aipatternbook.com/approval-fatigue>
- <https://towardsdatascience.com/most-ai-agents-fail-in-production-because-theyre-built-backwards/> (no named deployments; `ASSUMED`)
- <https://towardsdatascience.com/building-an-evaluation-harness-for-production-ai-agents-a-12-metric-framework-from-100-deployments/> ("100+ deployments" is a company credential, not third-party verification; `ASSUMED`)
