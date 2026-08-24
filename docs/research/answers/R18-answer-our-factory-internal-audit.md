# R18 — Our own factory, audited from inside the repo

**Answered 2026-08-23.** Pass type `STRUCTURE_CRITIQUE`, independence risk HIGH, run **BLIND-FIRST**
as a Claude Code session in the `agent-factory` checkout on `feat/readiness-generator` @ `b46d27d`.

**Ordering discipline, stated so it can be checked.** Phase 1 read `factory/*.py` and ran the code
with no spec, no finding and no prior answer open. Phase 2 opened `docs/specs/`. Phase 3 opened
`docs/findings.md`, `docs/findings.d/` and the four lane ledgers. Phase 4 opened
`R17-answer-data-engineering-external-survey.md`. Nothing in a later phase was read before the
phase before it was written down. Where a Phase 3 or 4 source turned out to have found something I
had already found blind, I say so and credit it rather than claiming it — that convergence is the
control, and §1.5 is where it is cashed.

**Every internal claim carries `path:line`. A claim without one is labelled an opinion.** All line
numbers were re-opened and confirmed at the point of citation. Where the repo cannot settle
something I write `NOT-DETERMINABLE` and name the test.

**Measurements taken this run.** `python -m factory.readiness` → **8 of 30**;
`python -m factory.launch` → `SUPERVISED-OK` / `UNATTENDED-BLOCKED` (5 gates) /
`OUTPUT-UNCERTIFIED` (6 gates); `python -m pytest` → 246 passed;
`factory.lanes.conflicts()` and `factory.claims.parallel_set()` → 3.

**No credential was requested or used.** The audit did not need one. Three questions it could not
answer without one are marked `NOT-DETERMINABLE` in §1.1 and §4.

---

## 0. Executive answer — the smallest change with the largest effect

> **Three of the thirty readiness probes have no reachable `PASS` path. Two of them are named in
> `factory/launch.py`'s "may I leave it running" gate list and one in its "may I trust the output"
> list — so two of the three questions this factory exists to answer are, today, structurally
> unanswerable no matter what anyone builds. The fix already exists, finished, on an unmerged lane
> branch.**

The three are:

| Gate | Probe | `path:line` | Reachable verdicts |
|---|---|---|---|
| `bounded` | `g_failure_is_bounded` | `factory/readiness.py:253-268` | `FAIL` only |
| `reaper` | `g_orphans_are_reaped` | `factory/readiness.py:799-806` | `FAIL` only |
| `corpus` | `g_corpus_is_tamper_evident` | `factory/readiness.py:543-597` | `FAIL` only |

`bounded` and `reaper` are 2 of the 5 gates in `UNATTENDED_GATES` (`factory/launch.py:41`).
`corpus` is 1 of the 6 in `TRUST_GATES` (`factory/launch.py:46`). `_blockers()`
(`factory/launch.py:79-91`) treats anything not `PASS` as a blocker, and `levels()`
(`factory/launch.py:142-159`) reports `UNATTENDED-OK` / `OUTPUT-CERTIFIABLE` only on an empty
blocker list. **Therefore `UNATTENDED-OK` and `OUTPUT-CERTIFIABLE` are unreachable states of this
program.** The control-plane lane can build a perfect attempt cap and a perfect reaper and the
board will still read `UNATTENDED-BLOCKED`; the corpus can be moved to a repo the agent cannot
write to — via `$AGENT_FACTORY_EVALS`, which `factory/corpus.py:38` already honours and which
`factory/readiness.py:594-596` recommends in its own evidence line — and `corpus` will still read
`FAIL`. `main()` returns `0` only on `n_pass == len(results)` (`factory/readiness.py:1196`), so
`python -m factory.readiness` also cannot exit 0.

**The fix is written and unmerged.** `lane/control-plane` carries `g_failure_is_bounded` at
`:685` and `g_orphans_are_reaped` at `:800` **with reachable `_pass` paths**, plus
`tests/test_readiness_probes_can_pass.py` and `scripts/mutate_readiness_probes.py` — neither of
which exists on HEAD. Its own ledger entry
`.worktrees/control-plane/docs/findings.md:170-196` (F11) names all three probes by the same
AST method I used, independently, a day earlier.

**So the smallest change with the largest effect is a merge, not a build.** Land `lane/control-plane`
(or cherry-pick the three probe fixes plus `tests/test_readiness_probes_can_pass.py`), and add the
`corpus` `_pass` branch the gate's own evidence describes. It moves *may I leave it* from
"unreachable" to "reachable and currently blocked by four real defects", which is the difference
between a target and a wall. Everything else in §1.4 is downstream of that.

**Two second-order items of the same shape, both one-line:**

1. `factory/finish.py:89-92` — the "did this lane write to the ledger?" check is dead. It reads
   `if not entries and _findings.nothing_to_report() == 0`, and `nothing_to_report()`
   (`factory/findings.py:152-156`) counts the literal string `NOTHING TO REPORT` across **all**
   sources globally, not per lane. `docs/findings.md:25` is the ledger's own *instruction* to write
   that string. Measured: `findings.nothing_to_report()` → **1**, and the single match is that
   instruction sentence. The check therefore cannot refuse for any lane, ever. A gate that cannot
   refuse, produced by the ledger's own documentation.
2. `scripts/local_tracker.py:353` — the live lane launcher runs
   `claude{model_flag} (Get-Content -Raw …)` with **no `--max-budget-usd` and no `--max-turns`**.
   `factory/deploy.py:88-92` has both, and `factory/deploy.py` has no caller anywhere in this repo.
   The harness-enforced dollar ceiling R17 rates as the first of its six structures
   [R17 §6, D-44 ✓] is written down in a module nothing runs, and absent from the one that runs.

---

## 1.1 R17's recommendations, audited against our code

R17's answer is a hypothesis. Where it and the code disagree the code wins; those rows say so.
Row ids are R17's own (§0, §4.x, §5, §6, §7, §9, §10 and the `A-`/`B-`/`C-`/`D-`/`E-` claim ids).

| R17 row | Recommendation | Our state, with `path:line` | Verdict |
|---|---|---|---|
| §0, C-31/C-35/C-32/C-37/C-22 ✓ | Build the Snowflake **grant envelope**: one role per lane, managed-access schema, owns nothing in prod and no policy object, no `MANAGE GRANTS`, `DEFAULT_SECONDARY_ROLES = ()`, network policy, resource monitor | The repo contains **no Snowflake role, grant or connection code at all** — no `GRANT`, no `USE ROLE`, no connector import under `factory/`. The only warehouse contact contemplated is a single query in a lane prompt (`factory/lanes.py:206-210`), gated on a human (`factory/lanes.py:217`). Nothing to audit, and nothing enforcing anything | **BUILDABLE** — no code blocks it; it is a Snowflake-side change plus one launcher change. What grants the lane user *actually* holds today is **NOT-DETERMINABLE** (see §4) |
| §0, A-24 ✓ / A-25 | **Do not raise lane concurrency** — under a fixed conflict graph the ceiling is α(G) and no topology enlarges it | We already cap at 3 and say so: `docs/specs/terminal-configuration.md:125-127` ("Cap simultaneous lanes at 3 until measured otherwise"). `factory/claims.parallel_set()` returns `['control-plane','artifact','grain']` | **ALREADY-BUILT** — but for a weaker reason than we think; see §1.2 |
| §4.2 step 1, B-16/B-17/B-20/B-21 ✓ | Turn on `strictAllowlist: true` + `network.tlsTerminate` + `credentials.envVars[].mode:"mask"` from **user/managed** settings. "Highest protection-per-unit-of-work in this survey… runs in WSL2, already on the box" | `~/.claude/settings.json` has keys `env, availableModels, hooks, statusLine, effortLevel, autoUpdatesChannel, tui, voice, skipWorkflowUsageWarning, theme, agentPushNotifEnabled, voiceEnabled, preferredNotifChannel` — **no `sandbox`, `network` or `credentials` block**. And lanes are launched into **PowerShell on native Windows**, not WSL2: `scripts/local_tracker.py:136-141` builds `[wt, new-tab, …, "powershell", "-NoExit", "-ExecutionPolicy", "Bypass", "-File", ps1]` | **BLOCKED as the launcher is built** — R17's own B-15 ✓ says the sandbox is unsupported on native Windows. BUILDABLE only if lane launch moves into WSL2, which is a rewrite of `_launch_script` (`scripts/local_tracker.py:310-354`), not a settings edit. ⚠ **R17 assumed the box runs lanes in WSL2. It does not.** |
| §4.2 step 2, B-23/B-24 ✓ | Set `"allowUnsandboxedCommands": false` — the escape hatch fires with no prompt in auto-allow mode | Not set. And our exposure is **larger** than the one R17 describes: `factory/deploy.py:92` and the live `prefect-connectors/orchestrator/server.py:731` pass `--dangerously-skip-permissions` outright, on the stated policy that "isolation is what earns the elevated permission" (`docs/research/agent-factory-research-prompts.md:287`). There is no sandbox to disable because there is no sandbox | **BUILDABLE**, and the recommendation understates our case — see §1.2(3) |
| §4.2 step 3, B-65/B-66/B-67 | **Probe the Snowflake credential shape** (key-pair cannot be sentinel-substituted; test whether a PAT is) before designing the credential architecture. "One hour of work; it decides the whole credential architecture" | Nothing in the repo connects to Snowflake, so the shape is unrecorded. The `grain` lane declares the blocker up front (`factory/lanes.py:217` `needs_paul="Snowflake credential approval…"`) and `factory/operator.py:27` gives the operator a place to answer it | **BUILDABLE** — one approved credential and one hour. Currently **NOT-DETERMINABLE** which auth shape our accounts use |
| §4.2 step 4, B-71 | Move the Key Vault read **out of the agent**; a launcher outside the sandbox reads AKV and passes sentinels in | The rule exists as a *prompt* — `factory/lanes.py:141-145` ("STOP and ask Paul before touching any vault or Key Vault secret"), plus the estate-wide credential rule. The launcher that would hold the secret already exists: `scripts/local_tracker.launch()` at `:388-424` claims, then spawns | **BUILDABLE, and cheaper than R17 assumes** — the launcher is written. What is missing is that today the rule is an instruction the agent could ignore, which is R17 §4.3's whole point turned on us |
| §4.3, C-31 ✓ / C-35 ✓ | ⭐ **Every genuinely mandatory control is a Snowflake grant; every conventional one is a tool control.** If the sandbox must hold against an agent that ignores its prompt, enforcement lives in the RBAC graph | `docs/specs/architecture-v0.md:99-102` claims "The tier is declared in the agent spec and enforced by the DECIDE plane." **`factory/blueprint.py:19-33` `AgentSpec` has no `tier` field** — the fields are `name, role, model, effort, prompt, tools, max_turns, budget_usd, prohibition`. And `factory/deploy.py:88-92` passes only `--max-turns`, `--max-budget-usd`, `--model`: **`tools` and `prohibition` reach no process** | **R17 is right and our spec is refuted by our own code.** Verdict on R17: BUILDABLE. Verdict on `architecture-v0.md:99`: **WRONG — it describes behaviour the code does not have** |
| §4.4(a), C-41/C-40/C-42 ✓/C-28 | Clone economics **survivable**; the multiplier is warehouse-per-lane × the 60-second minimum, not lane count. Share warehouses, size them, clone into `TRANSIENT`, use `--defer` | No warehouse configuration exists in this repo | **BUILDABLE.** Our actual warehouse sizing/sharing is **NOT-DETERMINABLE** |
| §4.4(b), C-17 ✓/C-19 ✓/C-18 ✓ | ⛔ **A clone of an imported (shared) database does not exist.** Any lane touching share-consumed data has *no* isolation story | Our one contract target is `QA_DG1_GEP_PREFECT_PR.WINDSORAI__PR.google_ads_CAMPAIGN` (`blueprints/windsorai_gep.yaml:15`, basis MEASURED). Whether that database is share-consumed is **not recorded anywhere in the repo** | **NOT-DETERMINABLE.** Settles with `SHOW DATABASES LIKE 'QA_DG1_GEP_PREFECT_PR'` (an imported DB reports an `origin`), or by adding a declared `share_consumed:` field to the blueprint. ⭐ **Until it is answered, `architecture-v0.md:85`'s T2 tier is undefined for our only real target** |
| §4.5, C-57/C-65/C-46/E-33 | ⭐ **DIFFERENT edges, not fewer.** The file-level graph "over-counts syntactic conflicts and under-counts semantic ones to zero" | Confirmed, and **stronger than R17 could know**: `factory/lanes.py:251-254` `_touch_set()` does not read files at all — it splits the hand-written prose field `touches` on commas and takes `.split()[0]` of each part. `factory/lanes.py:8-11` labels the grouping `ASSUMED` in the module docstring | **ALREADY-CONTRADICTED in our favour on the diagnosis; `architecture-v0.md:89-90`'s consequence 1 is WRONG.** See §1.2(1) |
| §4.6, C-68/C-69/C-70/C-65 | The consumer-layer oracle is serial and un-branchable. **"Invest in the oracle, not the clone"** | Our oracle gate is `rendered` (`factory/readiness.py:981-994`), which passes on `d.glob("render-pass-*.md")` being non-empty. It measures **that a file exists**, not that anyone looked. It is one of the 8 currently-passing gates | **BUILDABLE and high-value** — R17 is right, and our oracle is a filename |
| §4.7, B-71/B-57/D-51 | An isolation **receipt**: connections attempted with the deciding rule, denied-count provably non-zero-able, credential non-possession, zero `dangerouslyDisableSandbox`, signed and produced outside the agent runtime. ⛔ **"None describes what the agent did to a shared warehouse"** | `factory/runs.py:136-154` records `at, lane, outcome, basis, detail, problems, branch, commits, cost`. Nothing records hosts contacted, files written outside the worktree, or DB verbs. There is no proxy to produce one | **BLOCKED for the network half** (no sandbox on native Windows, per B-15 ✓); **BUILDABLE for the filesystem half** (a `git status` + a diff of `~/.claude` mtimes is cheap); **BLOCKED for the DB half** by C-52's 3-hour `ACCESS_HISTORY` latency, exactly as R17 says |
| §4.8 item 1, D-44 ✓ / D-43 | **A hard, dollar-denominated, harness-enforced spend ceiling that pauses.** Do not delegate the budget to the agent | ⭐ `scripts/local_tracker.py:353` launches `claude{model_flag} (…)` with **no budget flag and no turn cap**. `factory/deploy.py:88-92` has `--max-turns` and `--max-budget-usd` and **`factory/deploy.py` has no caller in this repo** | **BUILDABLE — and it is the cheapest real control on this list.** One f-string in `_launch_script` |
| §4.8 item 4, D-25 ✓ | ⭐ **An abort verb the agent is allowed to use, rewarded by the harness.** "An agent with no exit will fabricate one" | The harness **punishes** stopping: `factory/finish.py:84-92` refuses a close with no commits or no ledger entry, and `factory/runs.py:41` defines `ABANDONED` — which **nothing in `factory/` or `scripts/` ever writes** (grep: three definitions, zero writers) | **BUILDABLE, cheap, and currently inverted.** An honest ABANDONED outcome plus a `finish(abandoned=…)` path is a dozen lines |
| §4.8 item 6, D-31 ✓ | Human approval at volume is not a control — 17% FNR, 93% approve rate | ⭐ We already **measure** this and it reads exactly as predicted: `g_gates_have_checks` (`factory/readiness.py:289-301`) → "2 of 7 gates across all pipelines have a `gate_check`", 5 `manual, check=None`; `g_gates_can_refuse` (`factory/readiness.py:271-286`) → "22 gate events recorded, 0 of them a refusal", `14 x "auto-pilot: conditions met"` | **ALREADY-BUILT as an instrument.** R17 supplies the field's number for a thing our board already reports locally |
| §5 items 1-2, D-24 ✓ | A gate must be provably capable of failing; a zero must be demonstrated by injecting a known-bad | Half built: `tests/test_eval_can_fail.py` exists and `factory/readiness.py:500-501` cites `test_every_assertion_has_been_proved_able_to_fail`. The **other half** — a gate provably capable of *passing* — exists only on `lane/control-plane` (`tests/test_readiness_probes_can_pass.py`, `scripts/mutate_readiness_probes.py`), and HEAD has three probes that cannot pass | **BUILDABLE by merge** — see §0 |
| §5 item 3, D-25 ✓ / D-27 | ⭐ **A gate the agent can edit is not a gate.** "Hiding tests from agents reduces cheating success rate to near zero" | `factory/readiness.py:594-596` says it in its own evidence line: "NOT ENFORCED: the corpus still lives in a repo this agent can write to… `$AGENT_FACTORY_EVALS` makes the move a config change." `factory/corpus.py:38` honours that env var already. And the agent's write radius is the whole host — see §1.2(2) | **BUILDABLE** (env var + a repo the lane holds no credential for), and the gate that would report it **cannot pass** — see §0 |
| §6 row 1, A-13 ✓ | **Generator/critic with an external critic: make it structural.** ~15-25% marginal cost; three reviewers cost ~20% of five workers | The reviewer is a **paragraph in a prompt**: `factory/lanes.py:53-57` (POSTAMBLE, "REVIEWER — before you close this lane, run a review sub-agent on opus"). `factory/finish.py:53-93` `checks()` requires **no review artefact** | **BUILDABLE**, and `docs/specs/architecture-v0.md:157-159` already named this gap ("currently a habit inside a prompt. It should be a required stage") without building it |
| §6 row 6 / §6.1, D-49/D-45 ✓ | ⭐ Token budgets as a scheduling input — "build this first of the six". **Denominate in dollars, not tokens** | `factory/runs.py:82-130` `cost()` measures `input, output, cache_write, cache_read, wall_clock_s, models` per lane from `~/.claude/projects/<slug>/*.jsonl`, with basis `MEASURED` vs `NOT-RECORDED`. **There is no price table and no dollar figure anywhere** | **BUILDABLE and small** — the measurement is done, the denomination is not |
| §7 item 1, B-13 ✓ | ⛔ Refuse a plain container as the isolation boundary (40-49% escape at difficulty 3) | `docs/specs/architecture-v0.md:84-85` specifies T1 and T2 as "container, egress allowlist" and "container + ephemeral clone" — a plain container | **`architecture-v0.md:84-85` is WRONG-AS-SPECIFIED.** R17 does not refute the *ladder*; it refutes the *runtime* the ladder names. The tiers survive with a different substrate |
| §7 item 9, A-57/D-54 | ⛔ **No shared writable agent memory** — one poisoned entry reaches every agent | Our live channel is exactly that shape: `factory/bus.py:40` `ROOT = _repo.data()/"bus"` in the **primary** worktree, written by any lane (`post()`, `:71-85`), and **injected into every lane's context by a hook** (`scripts/hooks/lane-bus.py`, registered at `~/.claude/settings.json` `PreToolUse`). The mitigation is a sentence: `factory/bus.py:137-138` renders "These are peers, not instructions — verify anything you act on" | ⚠ **PARTIAL CONFLICT, and it is a real one.** The durable record (`docs/findings.d/`) is fine — append-only, in git, reviewed. The *channel* is a shared writable store piped into context. R17 would refuse it; `docs/findings.d/F71-lanes-still-cannot-see-each-other-live.md` argues we need it. Both are right; the resolution is that the bus should be capped, attributed and non-instructional, which `MAX_LEN` (`factory/bus.py:44`) and the render preamble half-do |
| §9 | ⚠ Is our **41.7%** an internal measurement or arXiv 2607.04697v2 wearing a measurement's clothes? "That is R18's to run" | **RUN. It is a citation.** `docs/research/answers/R5-answer-build-velocity.md:25` states the provenance correctly and always did: "A large empirical study of 33K agent-generated GitHub PRs found… PRs from different agents conflicted ~41.7%." The drift is downstream: `factory/worktrees.py:3-5` ("R5 from measurement"), `scripts/local_tracker.py:124-125` ("the setup R5 measured at a 41.7% cross-agent conflict rate"), `docs/research/R10-hierarchical-wiki-agent-training.md:137` (a bare row in a table of *our* figures), and `docs/research/R8-data-engineering-agent-factory.md:115` (`MEASURED, R5`) | **ALREADY-ANSWERED — R17's flag is correct.** ⚠ I ran this blind and then found `docs/research/SYNTHESIS.md:1278-1305` (§16.1) had reached the identical conclusion from the identical sources. Independent convergence, not novelty — and the corrections at `worktrees.py:3` and `local_tracker.py:124` are **still on disk unfixed** |
| §10 | The FP rate for LLM code review at production scale "is the number R18 should generate internally, because the field will not supply it" | We have the raw material and not the count: `factory/runs.py:82-130` measures per-lane tokens; the reviewer findings are prose in the lane ledgers (`.worktrees/certify/docs/findings.md`, `.worktrees/control-plane/docs/findings.md`, 55 entries across four branches). **Nothing records which review findings were acted on vs dismissed**, which is the denominator | **NOT-DETERMINABLE today.** Settles by adding a `STATUS: ACTED / DISMISSED / DISPUTED` field to reviewer-sourced findings and counting over one month. `factory/findings.py:43` already has a `STATUSES` vocabulary to extend |

---

## 1.2 The isolation ladder — is `architecture-v0.md` right?

### (1) Is `max independent set = 3` genuinely a file-conflict property?

**No. It is a property of a five-element hand-written list, and it does not measure files.**

Constructed by hand from `factory/lanes.py:95-219` and confirmed by running `conflicts()`:

```
node            repo                touch set (as _touch_set computes it)
control-plane   prefect-connectors  {orchestrator/pipelines.py}                    :102,:103
certify         agent-factory       {factory/connector_contract.py}                :129,:130
judgement       prefect-connectors  {orchestrator/pipelines.py}                    :154,:155
artifact        agent-factory       {docs/artifacts/agent-factory.html,
                                     ~/.claude/skills/}                            :176,:177
grain           agent-factory       {blueprints/windsorai_gep.yaml,
                                     factory/connector_contract.py}                :200,:201

edges           control-plane — judgement      (orchestrator/pipelines.py)
                certify       — grain          (factory/connector_contract.py)
α(G) = 3        {control-plane, certify, artifact} and three other triples
```

`OBSERVED` — `factory.lanes.conflicts()` returns
`{"control-plane":["judgement"],"certify":["grain"],"judgement":["control-plane"],"artifact":[],"grain":["certify"]}`
and `factory.claims.parallel_set()` returns `['control-plane','artifact','grain']`.
`docs/specs/terminal-configuration.md:13-18` states this correctly and is the more honest of the
two specs.

**Five things the number is actually a property of, none of them "files":**

1. **It is not computed from the filesystem.** `factory/lanes.py:251-254` `_touch_set()` reads the
   `touches` field — a **prose string**, as its own docstring says: *"`touches` is prose with commas
   in it, deliberately — it is read by humans first."* It splits on commas and takes `.split()[0]`.
   `"orchestrator/pipelines.py gate definitions"` (`:155`) happens to yield the right token because
   the path was written first. Had it been written *"the gate definitions in
   orchestrator/pipelines.py"* the token would be `the`, the `control-plane — judgement` edge would
   silently vanish, and the ceiling would read 4. **The graph is one word-order away from being
   different, with no error.** `factory/lanes.py:8-11` labels the grouping `ASSUMED` in the module
   docstring, which is honest; `docs/specs/architecture-v0.md:30` then relabels the derived ceiling
   `DERIVED`, which launders it.
2. **Nothing computes a maximum independent set.** `factory/claims.py:284-296` `parallel_set()` is
   greedy over `recommend()` order and says so at `:288-290` (*"Greedy… rather than a true
   maximum-independent-set"*). The "3" in `architecture-v0.md:30` is a hand-count of a five-node
   graph, correct today, and computed by no code.
3. **It is `len(LANES)` minus a matching, so it scales with authoring, not with work.** Five lanes
   with two disjoint edges gives 3. Eight lanes with the same two edges would give 6. Adding lanes
   raises the ceiling; the ceiling is not a fact about the codebase.
4. **The edges cross repos and the isolation does not.** `control-plane` and `judgement` — the pair
   that produces one of the two edges — both have `repo="prefect-connectors"`
   (`factory/lanes.py:102,:154`). But `factory/worktrees.py:37-38` roots `ROOT` at
   `_repo.primary()/".worktrees"` of **agent-factory only**. A lane worktree gives those two lanes a
   private copy of `agent-factory` and **no isolation whatsoever on `orchestrator/pipelines.py`,
   which is the file the edge is about.** The conflict graph's only real edge is between two lanes
   whose conflict the worktree mechanism does not cover. Conversely, `certify` and `grain` *do* get
   private copies of `factory/connector_contract.py`, so their edge is not a filesystem conflict at
   all — it is a *merge* conflict, deferred. **`conflicts()` mixes two different kinds of edge and
   calls both "cannot run together".**
5. **`_touch_set()` compares bare relative paths with no repo qualifier.** Two lanes in two
   different repos both touching a path spelled `src/main.py` would get a spurious edge; the same
   file reached by two spellings gets none.

**What edges would a *data* lane add — does the graph shrink, grow, or change shape?**

**It changes shape, and it grows in a dimension the graph has no vertex type for.** R17 §4.5 reaches
this from outside; from inside the code the mechanism is visible. A T2 data lane per
`architecture-v0.md:85` writes into its own clone schema, so its `touches` string names no file any
other lane names, so `_touch_set()` returns a disjoint set, so `conflicts()` adds **zero edges** and
`parallel_set()` grows by one. That is `architecture-v0.md:89-90`'s consequence 1 exactly — and it
is an artefact of the instrument, not a finding about the world. The conflicts a data lane really
adds are ones `_touch_set()` structurally cannot represent, because it only knows about path strings:

| Real edge a data lane adds | Why `conflicts()` cannot see it | R17 corroboration |
|---|---|---|
| Two lanes resolving `ref('dim_customer')` to the same physical relation | The namespace is not a path | C-57 |
| Two lanes queued behind `MAX_CONCURRENCY_LEVEL = 8` on a shared warehouse — one times out and reports a **false negative** | Compute is not a path | C-46 |
| A masking or row-access policy object, changed from one lane, enforced account-wide | The object is in no lane's schema | C-13, C-32 |
| A shared upstream changing what every other lane's lineage means | The manifest is not in `touches` | C-58 |
| Polysemy — two lanes producing two correct-looking numbers for one dimension | No file changed, nothing failed | E-33, C-72 |

⭐ **The honest statement of our ceiling.** It is not 3 because three lanes is what one machine can
hold, and not 3 because the files conflict. It is 3 because *five work packages were written down
and two pairs of them were labelled with the same path string*. `architecture-v0.md:36-39`'s "the
ceiling is not a concurrency limit, it is a *file* limit" is **half right**: it is not a concurrency
limit, and it is not a file limit either — it is a **labelling** limit.

**The real ceiling, and it is the one both specs already name.** `docs/specs/terminal-configuration.md:29`
Option B — split `pipelines.py`'s gate definitions into their own module — removes one of the two
edges and takes α(G) from 3 to **4**. Splitting `factory/connector_contract.py` removes the other and
takes it to **5**. `factory/claims.py:53-57` records R14's stronger version: `lane` is "four objects
wearing one string — work package, file-conflict key, git branch, directory, claim key, ledger key",
and *that*, not topology, is why the cap will not move. **That is the correct diagnosis and it is
already in the code as a comment.**

### (2) What host state stays shared across lanes — the full enumeration

`factory/worktrees.py` gives each lane a private checkout of **agent-factory** and a private branch.
That is the entire isolation. Everything below is shared, read from
`factory/worktrees.py`, `factory/repo.py`, `factory/sessions.py`, `factory/runs.py`,
`factory/bus.py`, `factory/claims.py`, `factory/operator.py`, `factory/corpus.py`,
`factory/readiness.py` and `scripts/local_tracker.py`. F53 (`~/.claude/skills/`) is the last row of
group C; the rest I found by reading.

**A. Shared by design — the coordination state (`_repo.data()` = the PRIMARY's `.data/`)**

| What | `path:line` | Shared because | If a lane corrupts it |
|---|---|---|---|
| `.data/claims/*.json` + `.claim.lock` | `factory/claims.py:42`, `:214` | a claim one lane cannot see is not a claim (`factory/repo.py:22-24`) | two agents in one worktree — F73 |
| `.data/bus/*.jsonl` + `.cursor-*.json` | `factory/bus.py:40`, `:104-105` | a per-worktree bus is not a bus (`factory/bus.py:37-39`) | a lane's cursor is advanced past unread corrections |
| `.data/runs.jsonl` | `factory/runs.py:58-59` | one ledger, not one per lane | the only record a lane ran |
| `.data/operator/<lane>.json` | `factory/operator.py:27` | Paul answers in the primary, the lane reads in its worktree | operator-supplied text is appended to a spawned prompt (`factory/operator.py:9-12`) |
| `.data/lane-prompts/*.txt`, `.data/launch/*.ps1`, `.data/handoffs/` | `scripts/local_tracker.py:117-119`, `:318-320`, `:365-367` | written by the tracker under `FACTORY` | **a lane can rewrite the script that launches another lane** |

**B. Shared and NOT by design — resolvers that still use `__file__.parent.parent`**

`factory/repo.py:22-24` states the rule: *"State shared between lanes must resolve to the primary
worktree, or it is not shared."* Two modules still do not.

| What | `path:line` | Consequence |
|---|---|---|
| `factory/launch.py:99-100` — `root = Path(__file__).resolve().parent.parent; ledger = root/".data"/"runs.jsonl"` | run from a lane worktree this reads *that worktree's* `.data`, which is gitignored and absent, so `_observability()` returns `ok: False` and `levels()` reports `SUPERVISED-BLOCKED` (`factory/launch.py:132-134`) | **Latent, not live** — `factory/launch.py` exists on no lane branch today (checked all four). It is armed the moment a lane branch carries it. Exactly the F72 / `factory/repo.py:10-20` shape, unfixed |
| `factory/readiness.py:35-37` — `CONNECTORS = FACTORY.parent/"prefect-connectors"` | from a lane worktree this resolves to `agent-factory/.worktrees/prefect-connectors`, **which exists right now** (`git worktree list` + `ls .worktrees/`) | **Live.** Every lane's `python -m factory.readiness` measures a sibling lane's checkout. Named in `docs/findings.d/F72…md` and again, more precisely, in `.worktrees/certify/docs/findings.md:166-197` (F30) — flagged there rather than fixed, "shared file, out of this lane's scope" |
| `factory/findings.py:24` — `LEDGER = __file__.parent.parent/"docs"/"findings.md"` | per-worktree, so `finish.checks()` run from the primary cannot see a finding a lane committed on its own branch | Correct-ish (findings are in git and merge with the branch) but it means the `finish()` ledger check reads a different ledger than the lane wrote — moot today because that check is dead (§0) |
| `factory/demo.py:15` — `DATA = Path(".data")` | relative to **cwd** | demo module, no caller in the launch path; low stakes |

**C. Shared because it is the operator's home directory — nothing scopes it**

| What | `path:line` | Why it matters |
|---|---|---|
| `~/.claude/sessions/*.json` | `factory/sessions.py:27` | the liveness instrument behind `finish()`'s refusal (`factory/finish.py:67-72`) and `launch()`'s pre-claim refusal (`scripts/local_tracker.py:394-402`) |
| `~/.claude/jobs/<id>/state.json` | `factory/sessions.py:117` | the blocked-questions inbox — `factory/launch.py:107-110` makes it one of the three facts gating `SUPERVISED-OK` |
| `~/.claude/projects/<slug>/*.jsonl` | `factory/runs.py:45`, `factory/sessions.py:118` | **the entire cost measurement** and the session-identity `_topic()` |
| `~/.claude/settings.json` | verified live — `PreToolUse` → `scripts/hooks/lane-bus.py` | **the bus delivery mechanism is registered outside the repo.** Clone this repo on another machine and the channel is decoration again |
| `~/.claude/skills/living-systems-ui/SKILL.md` | `factory/readiness.py:999` | gate `chain` PASSES on `"impeccable" in txt.lower()` (`:1006`) — a substring of a file outside the repo. F53 |
| `~/.claude/skills/impeccable/node_modules/` | `.worktrees/artifact/docs/findings.md:238-256` (F53) | untracked, machine-local; the detector silently degrades without it |
| The whole `~/.claude/skills/` tree | `factory/lanes.py:177` — the `artifact` lane **declares it as a touch target** | one lane writing there changes every other lane's and every future session's behaviour, instantly |

**D. Shared because it is the same machine, same user, same shell**

| What | `path:line` | |
|---|---|---|
| The **git object store** | `factory/worktrees.py:89-91` — `git worktree add` | worktrees share `.git`. `remove()` refuses a dirty tree (`:112-115`) but nothing stops a lane running `git gc`, `git reflog expire`, or rewriting another lane's branch |
| `repos/prefect-connectors` — the object of measurement | `factory/readiness.py:35-37` | ~15 of 30 probes read it. It is in no worktree; every lane writes to the same copy |
| Sibling repos: `aldc-launchpad` | `factory/readiness.py:1033` (gate `ticket`) | a probe reads a drafts folder two repos away |
| `evals/` + `evals/MANIFEST.sha256` — **the grader** | `factory/corpus.py:38-39`; admitted at `factory/readiness.py:594-596` | the agent can write the corpus it is graded against |
| The full **process environment**, inherited into every lane | `scripts/local_tracker.py:172` `Popen(cmd, cwd=…)`; `prefect-connectors/orchestrator/server.py:734` `env = {**os.environ, …}` | any credential exported in the shell that started the tracker propagates into every lane |
| **Network** | — | no egress control exists anywhere in `factory/` or `scripts/` |
| **The console / Windows Terminal window** | `scripts/local_tracker.py:366-383` `start_all_command` | one `wt` process; a lane can `wt` at other tabs |
| The **tracker server** itself, on a fixed port | `scripts/local_tracker.py:2357-2362` (now `ThreadingTCPServer`) | F8 records two servers holding one port and verifying against the stale one |

**E. What is genuinely private per lane** — the worktree directory, its git index and `HEAD`, its
branch `lane/<id>`, the terminal tab, and the `claude` process's own context. That is the list.

⭐ **"What breaks first if we scale to remote sandboxes."** Not the filesystem — group A already
resolves to a single primary and would become a network service cleanly. **Group C breaks first**,
because four instruments (`sessions`, `runs`, the bus hook, the `chain` gate) are joins against the
operator's home directory *on this machine*. A remote lane has a different `~/.claude`, so:
`sessions.live()` returns `[]` → `finish()` stops refusing a close on a live session (F73's guard
gone); `runs.cost()` returns `NOT-RECORDED` → the only cost measurement disappears; the `PreToolUse`
hook is unregistered → the bus stops being delivered; and gate `chain` goes `UNMEASURABLE`
(`factory/readiness.py:1002`). **Three controls and one gate fail the moment a lane is not on this
laptop, and none of them fails loudly.**

### (3) Is the tier assignment enforceable, or only declarable?

**Only declarable — and today not even that, because there is nowhere to declare it.**

`docs/specs/architecture-v0.md:99-100` says: *"The tier is declared in the agent spec and enforced by
the DECIDE plane. An agent that asks for a verb its tier does not carry is refused, and the refusal
is an audit event."* Against the code:

| The claim | The code | Verdict |
|---|---|---|
| "declared in the agent spec" | `factory/blueprint.py:19-33` — `AgentSpec` fields are `name, role, model, effort, prompt, tools, max_turns, budget_usd, prohibition`. **No `tier`** | `path:line` refutation. `architecture-v0.md:119`'s `tier: T2` is a YAML sketch with no dataclass behind it |
| "enforced by the DECIDE plane" | The only thing that spawns a lane is `scripts/local_tracker.launch()` (`:388-424`) → `Popen` → a `.ps1` (`:310-354`) → `claude{model_flag} (Get-Content …)` at `:353`. No permission mode, no allowed-tools, no sandbox, no network policy, no separate OS user, no container | There is no DECIDE plane in the execution path. The only thing scoped per lane is `--startingDirectory` |
| T0 = "repo files only. **No network egress, no DB verbs**" (`:83`) | Nothing restricts either. The lane runs as the operator with the operator's full environment | An instruction |
| "An agent that asks for a verb its tier does not carry is refused" | `factory/deploy.py:88-92` builds the CLI argv and **`spec.tools` and `spec.prohibition` appear nowhere in it**. `factory/deploy.py` has no caller | Two fields nothing reads |
| — | `factory/deploy.py:92` passes `--dangerously-skip-permissions`, commented `# safe ONLY because wt is an isolated worktree`. The live version is `prefect-connectors/orchestrator/server.py:731`, and the estate's written policy is `docs/research/agent-factory-research-prompts.md:287`: *"`--dangerously-skip-permissions` **only** when running in a worktree… Isolation is what earns the elevated permission"* | ⛔ **The premise is false and §1.2(2) is the proof.** A worktree is a directory, not a boundary. A skip-permissions agent whose cwd is `.worktrees/certify` can write `~/.claude/skills/` (gate `chain`), `~/.claude/settings.json` (the bus hook), `~/.claude/sessions/` and `~/.claude/jobs/` (the liveness and inbox instruments), the primary's `.data/` (claims, bus, operator answers, the run ledger), `evals/MANIFEST.sha256` (its own grader), `repos/prefect-connectors` (the object of measurement), and the primary checkout. **Every instrument the readiness board reads is inside the write radius of the agent it measures.** |

**The verdict, in the brief's own words: a tier an agent can exceed is a prompt, not a control — and
ours is not yet even a prompt, because `AgentSpec` has no field to put it in.** R17 §4.3's rule is
the right correction and it generalises past Snowflake: the only tier assignments that will ever be
enforceable are the ones expressed as something the agent's process cannot reach — a grant, an OS
credential, a settings scope the agent cannot write (B-20 ✓). `architecture-v0.md`'s tiers, as
written, are three prose paragraphs. `architecture-v0.md:130-132` states the governing rule
correctly — *"A spec with a field nothing reads is worse than no field… Every field needs a test
asserting it reaches the process"* — and `factory/blueprint.py` + `factory/deploy.py` violate it
two files away, with `tools` and `prohibition`.

---

## 1.3 Current vs recommended

Every "current" cell cites `path:line` and is `OBSERVED`. Every "recommended" cell cites an R17 row.

| Dimension | Current, with `path:line` | R17's recommendation | Gap |
|---|---|---|---|
| **Isolation unit** | git worktree of **agent-factory only**, on the operator's machine, launched as bare `claude` in PowerShell — `factory/worktrees.py:37-38`, `scripts/local_tracker.py:136-141`, `:353`. Two of five lanes work in a repo the worktree does not cover (`factory/lanes.py:102,:154`) | Not a plain container (§7.1, B-13 ✓ — 40-49% escape at difficulty 3). Locally Docker sbx; in Azure, ACA dynamic sessions with Hyper-V isolation, having priced the E16 pool (§4.1, B-47 ✓, B-48 ✓) | **Total.** No sandbox of any kind. And B-15 ✓ blocks the cheap option on native Windows |
| **Concurrency ceiling** | **3** — α(G) of a 5-node, 2-edge graph built from a prose field. `factory/lanes.py:251-254`, `:257-270`; greedy `factory/claims.py:284-296` | **Do not raise it** (§0, A-24 ✓/A-25 — α(G) is an invariant; no topology enlarges it) | **None on the number.** Large on the *reason*: our α(G) is not a fact about conflicts (§1.2(1)) |
| **Scheduling** | A weighted score, judgement not measurement, stated in the docstring — `factory/lanes.py:331-343` (+100 unblocks / −40 needs-Paul / −60 conflicting-lane-running / −6 per gate). Conflicts are **not** applied by `runnable_now()` (`:300-304`) | Token/dollar budgets as a **scheduling input** — "build this first of the six" (§6 row 6, D-44 ✓/D-43) | Cost is measured (`factory/runs.py:82-130`) and **feeds nothing** in `recommend()` |
| **Communication** | Split by design: durable record `docs/findings.d/` (`factory/findings.py:29`); live channel `.data/bus/` one append-only file per writer (`factory/bus.py:40,:71-85`), delivered by a `PreToolUse` hook registered in `~/.claude/settings.json` | Durable record append-only and **read-only to agents**; ⛔ no shared writable memory (§6 row 5, §7.9, A-57) | The split is right and R17 §3.1 names it. The channel is a shared writable store injected into context; the mitigation is a sentence at `factory/bus.py:137-138`. ⚠ Delivery only fires for cwd under `.worktrees/<lane>` (`factory/bus.py:148-157`), so the two `prefect-connectors` lanes never receive traffic |
| **Failure handling** | `finish()` asserts then pushes then releases, and **never merges** — `factory/finish.py:96-140`. Refusals are recorded before the raise (`:107`). A failed push does not release the claim (`:113-119`). ⚠ The ledger assertion is **dead** (`:89-92`, §0). ⚠ `runs.ABANDONED` (`factory/runs.py:41`) is written by nothing | An **abort verb the agent may use, rewarded by the harness** — cut GPT-5 cheating 54%→9% (§4.8 item 4, D-25 ✓). Checkpoint-and-resume over restart | The close protocol is genuinely good and R17 does not improve it. What is missing is the *other* exit: our harness punishes stopping and has no honest ABANDONED path |
| **Evaluation** | 30 gates, four never-collapsed verdicts (`factory/readiness.py:7-12`), each carrying its source. **8 pass.** ⛔ 3 probes cannot pass (`:253-268`, `:543-597`, `:799-806`). ⚠ **All 8 passing gates are declarative** — file-exists (`:961-973`, `:981-994`), substring (`:997-1008`), non-empty-list (`:530-540`), `git remote` non-empty (`:600-611`), regex-in-a-draft (`:1026-1045`). **Every gate that measures behaviour is FAIL, UNMEASURABLE or NOT_RUN** | A gate is honest when you can state, from a run you performed, the last time it failed and why, and a deliberately-broken input in the current window produces a non-zero (§5). The gate must be **outside the agent's write radius** (§5.3, D-25 ✓/D-27) | The verdict vocabulary is better than the field's. The *population* is the problem: 8 green lights, none of which any behaviour had to produce. And `durable` (`:609`) announces "pushed to origin" having measured only that a remote is configured — the same defect `:900-904` criticises elsewhere in the same file |
| **Cost control** | Measured, per lane, retroactively, in **tokens** — `factory/runs.py:82-130`; live: control-plane 1.47M out / 453M cache-read on `claude-opus-5`, certify and artifact on `claude-sonnet-5`, judgement and grain `NOT-RECORDED`. ⛔ **No ceiling of any kind on the launch path** — `scripts/local_tracker.py:353` has no `--max-budget-usd` and no `--max-turns`; `factory/deploy.py:88-92` has both and has no caller | Hard, **dollar-denominated**, harness-enforced ceiling that **pauses** (§4.8 item 1, D-44 ✓). Denominate in dollars because Claude 4.7+ tokenise ~30% higher (§6.1, D-49). Size on p99, not the mean (D-48) | ⭐ Measurement done, **enforcement absent**, denomination wrong. This is the largest gap-to-effort ratio in the table |
| **Credential boundary** | Per-secret human approval, as an **instruction** — `factory/lanes.py:141-145`, `:217`; `factory/operator.py:9-12`. Real enforcement: none. `--dangerously-skip-permissions` (`factory/deploy.py:92`, `prefect-connectors/orchestrator/server.py:731`), full env inheritance (`server.py:734`), no egress control anywhere | Sentinel substitution at a proxy, from user/managed settings the agent cannot write — "that *is* per-secret approval, made structural" (§4.2, B-16 ✓/B-20 ✓). ⛔ Short-lived tokens **minted by the agent** are self-service (B-69). ⛔ Snowflake key-pair **cannot** be sentinel-substituted and gives no signal that it failed (§7.6, B-65/B-66) | R17 hands us the exact structural version of the rule we already hold as a convention — and B-15 ✓ says the mechanism needs WSL2, which our launcher does not use. **The nearest enforceable thing on Windows today is the Snowflake grant envelope, not the proxy** |
| **Data blast radius** | Unbounded and unmodelled. No Snowflake code in `factory/`; the only contemplated query is a prompt string (`factory/lanes.py:206-210`). `g_tenancy_declared` (`factory/readiness.py:530-540`) PASSES on six account ids in a YAML — and the gate title was already honestly retitled "**declared, not verified**" (`:1138-1140`) | Grants, not instructions (§4.3): managed access, own nothing in prod, own **no policy object**, `DEFAULT_SECONDARY_ROLES = ()`, network policy, resource monitor on every reader account (C-75 ✓ — reader compute is billed to us with no ceiling). ⛔ A clone of a share does not exist (C-17 ✓) | **Total, and the highest-consequence row.** Also: R17 §4.7 — an isolation receipt can be perfect while the damage is total, because **no receipt describes what the agent did to a shared warehouse** |
| **Observability** | Good, and genuinely ahead of the field: three-way liveness (`factory/sessions.py:30-50`, `HELD-LIVE/GONE/UNVERIFIED` at `factory/claims.py:96-98`), a blocked-questions inbox read from `JOBS` not the session list (`factory/sessions.py:284-357`), `contended_repos()` with `attribution: NOT-MEASURABLE` stated (`:390-450`), a run ledger with `RECORDED/RECONSTRUCTED/NOT-RECORDED` (`factory/runs.py:42`), and `factory/launch.py` splitting one word into three questions | "Two executions with the same answer may differ in reliability, safety, and auditability"; **there is no adopted trace standard** — `NOT-SUPPLIED`, rolling your own is the only option (§4.7, D-51) | ⭐ **This is the column where we are ahead.** R17 found the field has no answer here; we have a partial one. What is missing is the *isolation* half of the receipt, and the process/filesystem part of it is cheap |

### Is worktree-on-one-machine a stepping stone or a dead end?

**A stepping stone for the code plane; a dead end for everything the ladder was invented for — and
the honest answer is that it was never load-bearing enough to be either.**

**Why it is a stepping stone.** The parts of `factory/` that matter are not about worktrees. The
claim protocol with three liveness verdicts (`factory/claims.py:96-123`), the close protocol that
refuses (`factory/finish.py:53-93`), the record/channel split (`factory/bus.py:10-16`), the run
ledger's `RECORDED / RECONSTRUCTED / NOT-RECORDED` basis (`factory/runs.py:20-23`), the four gate
verdicts (`factory/readiness.py:7-12`), and the run/leave/trust split (`factory/launch.py:7-12`) are
**substrate-independent**. They are a distributed-systems protocol that currently happens to run on
one filesystem. `factory/repo.py` already forced every piece of shared state through one resolver —
which is exactly the refactor you would do before making it a service. Nothing there has to be
thrown away.

**Why it is a dead end.** Three separate reasons, each with code behind it:

1. **It provides no isolation for the thing that has blast radius.** It isolates the repo. The risk
   is DDL on a shared warehouse (R17 §4.3), credentials in the process environment
   (`prefect-connectors/orchestrator/server.py:734`), and the operator's home directory (§1.2(2)
   group C). A worktree touches none of them, and `--dangerously-skip-permissions`
   (`factory/deploy.py:92`) is granted **on the strength of the worktree**, which is the premise
   §1.2(3) refutes.
2. **The ceiling it is blamed for is not its fault.** α(G) = 3 comes from a five-item list and a
   prose field (§1.2(1)). Moving to remote sandboxes would not change it, because nothing about
   remoteness changes `_touch_set()`. Anyone who migrates expecting concurrency will be
   disappointed for the reason R17 §4.5 gives from outside and `factory/claims.py:53-57` gives from
   inside: `lane` is one word doing six jobs.
3. **Four instruments are joins against `~/.claude` on this laptop** (§1.2(2)E). A remote lane
   silently loses `finish()`'s liveness guard, the cost measurement, bus delivery, and gate `chain`
   — none loudly. **That is the migration's real bill, and it is not the scheduler.**

⭐ **The framing both specs get wrong.** `architecture-v0.md:23-41` presents "worktree → container →
clone" as a ladder you climb for **concurrency**. It is not. Every rung buys **blast-radius
containment**, and only the rungs that end in a *grant* or a *credential the agent cannot reach* buy
anything at all. Climbing it for concurrency is climbing it for the one thing it does not sell.

---

## 1.4 The migration sequence, rewritten

`docs/specs/architecture-v0.md:181-194` is treated here as a hypothesis and **not ratified**. Two of
its seven steps are already done, one is refuted by R17, and none of them address the three
unpassable gates — which means, on `factory/launch.py`'s own yardstick, its ordering cannot move
*may I leave it* at all.

**Cross-check against the run/leave/trust split (`factory/launch.py:132-159`). A step that moves
none of the three is decoration.**

| # | Step | Moves | Why here | Cost |
|---|---|---|---|---|
| **1** | ⭐ **Merge `lane/control-plane`'s three probe fixes + `tests/test_readiness_probes_can_pass.py`, and give `g_corpus_is_tamper_evident` a `_pass` branch.** | **LEAVE + TRUST** — from *unreachable* to *reachable* | Two of five `UNATTENDED_GATES` and one of six `TRUST_GATES` are constants (§0). Until this lands, every other step on this list is unmeasurable by the board that is supposed to score it. ⚠ `git merge-tree HEAD lane/control-plane` reports conflicts in `factory/readiness.py`, `factory/sessions.py` and `scripts/local_tracker.py` — cherry-pick the probes if the full merge is too wide | hours |
| **2** | ⭐ **Put `--max-budget-usd` and `--max-turns` on the live launch path**, from the lane's own `AgentSpec`, and add a price table so `runs.cost()` reports dollars | **RUN + LEAVE** | `scripts/local_tracker.py:353` has neither; `factory/deploy.py:88-92` has both in a module nothing calls. R17 §6 rates this first of six [D-44 ✓]; R17 §6.1 says denominate in dollars [D-49]. The measurement already exists (`factory/runs.py:82-130`) | hours |
| **3** | **Fix the two dead checks.** `factory/finish.py:89-92` — make the ledger check per-lane (search that lane's own entries for `NOTHING TO REPORT`, not the global count). `factory/readiness.py:609` — measure a push (`git rev-list --count @{u}..HEAD`), not a configured remote | **LEAVE** | Both are gates that cannot refuse, in a repo whose thesis is that such a gate is worse than none. Both are one line | hours |
| **4** | **Make `readiness.py`'s `CONNECTORS` prefer the canonical path unconditionally**, per `.worktrees/certify/docs/findings.md:166-197` (F30), and route `.data` in `factory/launch.py:99-100` through `_repo.data()` | **RUN** | The board currently reads a sibling lane's checkout from any worktree, and `.worktrees/prefect-connectors` exists **today**. Paid for twice already (F72, certify F30) and fixed in neither place | hours |
| **5** | ⭐ **Run the loop once, supervised, and record it.** | **RUN → LEAVE** | `finishes` and `succeeds` are UNMEASURABLE because nothing has started since `MEASURED_SINCE = "2026-08-22"` (`factory/readiness.py:98`, `:218-220`, `:238-240`). `factory/launch.py:19-23` names this circle explicitly and is right. ⚠ **It goes at 5, not 1** — running it before step 1 produces evidence two of the five gates it should move are constitutionally unable to record | hours |
| **6** | **Allocate finding-id blocks per lane, and make a duplicate id an error.** | neither directly — **but it protects every ledger claim the other steps rest on** | F70's fix converted a *loud* merge conflict into a *silent* semantic loss. Five ids collide across four branches with different meanings; `factory/findings.py:121-123` `continue`s past a duplicate by design. See §1.5 | hours |
| **7** | **Build the Snowflake grant envelope** — one role per lane, managed-access schema, owns nothing in prod, owns **no policy object**, `DEFAULT_SECONDARY_ROLES = ()`, network policy, resource monitor incl. reader accounts | **LEAVE + a blast radius nothing else touches** | R17 §0/§4.3 [C-31 ✓, C-35 ✓, C-32, C-37, C-75 ✓]. It is the only control in either survey an agent cannot ignore by ignoring its prompt. Needs Paul + ACCOUNTADMIN; needs no repo change to *start* | days |
| **8** | **Probe the Snowflake credential shape** — is our auth key-pair or PAT, and does masking actually swap it? | **TRUST** | R17 §4.2 step 3 and §7.6 [B-65/B-66]: key-pair cannot be sentinel-substituted and **the tooling gives no signal that it failed**. One hour, one approved credential, decides the whole credential architecture. ⚠ Sequenced after 7 because the grant envelope is useful whichever way this resolves | hours |
| **9** | **Reviewer as a required close stage**, not a POSTAMBLE paragraph — a review artefact `finish.checks()` refuses without | **TRUST** | `factory/lanes.py:53-57` is a prompt; `factory/finish.py:53-93` requires nothing. R17 §6 row 1 [A-13 ✓]: external critic works, three reviewers cost ~20% of five workers. `architecture-v0.md:157-159` already made this argument and did not build it | days |
| **10** | **Move `evals/` behind `$AGENT_FACTORY_EVALS` into a repo the lane holds no write credential for** | **TRUST** | `factory/corpus.py:38` already honours the variable; `factory/readiness.py:594-596` already names the gap. R17 §5.3 [D-25 ✓, D-27]. ⚠ Only meaningful **after** step 1, because the gate that would report it cannot currently pass | days |
| **11** | **An abort verb, and an honest `ABANDONED` outcome** | **RUN + TRUST** | `factory/runs.py:41` defines it; nothing writes it. R17 §4.8 item 4 [D-25 ✓]: "an agent with no exit will fabricate one" | hours |
| **12** | **Corpus strata: 1 case → 29+ across ≥15 strata** | **TRUST** | `factory/readiness.py:851` is the pass condition and we are at `1 case, 0 strata`. Genuinely weeks, and genuinely necessary before any certification means anything | weeks |

### What must NOT be built yet, and why

| Not yet | Reason, with a citation |
|---|---|
| ⛔ **A container as the isolation boundary** — including `architecture-v0.md:84-85`'s T1/T2 as written | R17 §7.1 [B-13 ✓]: 40-49% escape for a frontier model, authors say treat plain Docker as insufficient by default. Building it would buy a *feeling* of isolation while §1.2(2) groups C and D stay wide open. **If a runtime boundary is built, it must be the Hyper-V-isolated or microVM kind [B-47 ✓], priced first [B-48 ✓].** |
| ⛔ **The T2 ephemeral clone** | Two independent reasons. (a) R17 §4.4(b) [C-17 ✓]: a clone of an imported database **does not exist**, and whether our only target is share-consumed is **NOT-DETERMINABLE** (§1.1). (b) R17 §4.5: cloning removes the one edge our graph already catches cheaply and adds three it cannot represent. Do step 7 first — the grant envelope is what the clone was a proxy for |
| ⛔ **Raising lane concurrency past 3** | R17 §0 [A-24 ✓/A-25]: α(G) is an invariant; no topology enlarges it. And [E-17 ✓]: at 22,000 developers, throughput +33.7% while review time +441.5% and no-review merges +31.3%. **A saturated evidence gate does not present as a queue, it presents as a bypass** — and our gate is one human. If the number must move, move it by *splitting the files* (`terminal-configuration.md:29`, Option B: 3 → 4), not by adding lanes |
| ⛔ **A best-of-N tournament whose judge decides the merge** | R17 §7.10 [D-40, D-56 κ≈0.10-0.21, D-57]. And §6.1: judging full trajectories costs more than generating them |
| ⛔ **A self-improving prompt loop** | R17 §7.8 [D-53, D-24, D-26]. It is a reward-hacking engine pointed at a gate that, per §1.2(2)D, the agent can already write to |
| ⛔ **Agent-to-agent request/response** | `architecture-v0.md:153-155` and `docs/findings.d/F71…md` both say wait for a real case. R17 §10 corroborates: **no shipped mechanism for injecting context into a running agent exists in the field**, and [A-2 ✓] Anthropic states the lead agent cannot steer a live subagent. Nothing to copy and no case yet |
| ⛔ **Remote / distributed execution** | Not because it is wrong, but because §1.2(2)E is the bill: four controls silently degrade the moment `~/.claude` is not this machine's. Fix the resolvers (step 4) and add a receipt before, not after |
| ⚠ **`--simulate`** (`terminal-configuration.md:174-188`) — not forbidden, but not step 1 | It is not built (grep: no `simulate` in `factory/` or `scripts/local_tracker.py`). It would have caught F10 and is cheap. But it moves *none* of run/leave/trust — it reduces the cost of finding launcher defects, which is real and second-order. Put it after step 5, when there is a real run to rehearse against |

⭐ **What `architecture-v0.md:181-194` got wrong, item by item.** Its step 1 ("run the loop once") is
right and is my step 5, demoted because the board cannot yet score it. Its step 2 ("instrument cost")
is **already done** — `factory/runs.py:82-130` measures tokens, wall clock and models per lane, and
`factory/runs.py:28-29` says so explicitly, closing `terminal-configuration.md:121-123` and its §8
open item; the spec is stale on its own repo. Its step 3 ("AgentSpec + a real version hash") rests on
"the `hash` gate wants 15 dimensions and covers **0**" (`:109`, repeated at `:187`), which is
**false**: `g_version_hash_is_complete` measures **6 of 15**, live, and the `0` was a U+0008 bug
already found and fixed (`docs/research/SYNTHESIS.md:1098-1131`, §15.1). Its step 4 ("T1 container")
is refuted by [B-13 ✓]. Its step 6 (T2 clone) is blocked by [C-17 ✓]. **And its list contains no step
that would make `bounded`, `reaper` or `corpus` capable of passing** — so as sequenced, it cannot
move *may I leave it* even if executed perfectly.

---

## 1.5 What the ledger already answered — nobody should pay twice

Six corrections were paid for and have not been carried. Each is cited by finding id and `path:line`.

**1. `F11` (control-plane) already found the three unpassable probes, a day before I did, by the same
method.** `.worktrees/control-plane/docs/findings.md:170-196`: *"`g_failure_is_bounded` and
`g_orphans_are_reaped` each had **exactly one return path, `_fail`**… A third,
`g_corpus_is_tamper_evident`… is the same shape."* It records the fix as
`tests/test_readiness_probes_can_pass.py`, "which asserts every gate has a reachable PASS **and** a
way of refusing", with `corpus` allowlisted `xfail`. That test and `scripts/mutate_readiness_probes.py`
exist on `lane/control-plane` and **on no other branch**. HEAD's `factory/readiness.py:253-268`,
`:543-597` and `:799-806` are unfixed. ⚠ `factory/launch.py` — written *after* F11 was filed, on the
primary — built its entire three-level model on top of two of them.

**2. `F20` and `F21` (primary, both ADOPTED) established the rule and it was applied to two gates
only.** `docs/findings.d/F20-…md`: *"A gate that cannot pass is the mirror of the decoration-gate this
repo already refuses — it stops being a measurement and becomes a wall."* `readiness.py:87-92` quotes
that lesson in its own comment block. It was applied to `finishes` and `succeeds` and to nothing else.
**F20's own `AFFECTS` field names "the `reaper` it is building"** — and `reaper` is one of the three.

**3. `SYNTHESIS §15.1` found a fourth instance and stated the general rule.** `docs/research/SYNTHESIS.md:1098-1113`:
a `f"\b…"` without the `r` put a literal backspace in `g_version_hash_is_complete`'s regex, so it
*"could only ever return `0 of 15` and could only ever FAIL"*, and *"`readiness.py:88-97` already names
an instrument that cannot pass as an equal defect. We were publishing one."* That one was fixed — my
live run reads `6 of 15`, confirming it. **So this defect class has now been met four times, is
documented in three places, and three live instances remain on HEAD.**

**4. `F70` was fixed at the file level and the failure moved to the id level — where it is now
silent.** `docs/findings.d/F70-…md` records three worktrees each appending their own F11 and F12, and
its `CHANGES` says ids *"become a naming convention rather than a lock on a shared file, allocated in
per-lane blocks."* The blocks were never allocated. Measured across the four lane ledgers and the
primary:

| id | Meaning A | Meaning B |
|---|---|---|
| **F20** | "Gate `finishes` can never pass" — `docs/findings.d/` | "An instrument that counts its own writes reports the wrong period" — `lane/control-plane`, `lane/control-plane-renamed` |
| **F21** | "Gate `succeeds` is an all-time ratio" — `docs/findings.d/` | "`pipelines.py` has no in-process lock" — `lane/control-plane`, `lane/control-plane-renamed` |
| **F30** | "A sibling lane's transient worktree can silently shadow the canonical checkout" — `lane/certify` | "A budget that 'defers' work defers nothing" — `lane/control-plane` |
| **F31** | "A blueprint's connector class names were guessed" — `lane/certify` | "An `except` guard that checks a clause EXISTS cannot see it made dead" — `lane/control-plane` |
| **F32** | "`windsorai_gep.yaml`'s `primary_key` still doesn't match" — `lane/certify` | "A retry loop with no attempt cap" — `lane/control-plane` |

⛔ **And the loss is silent.** `git merge-tree --write-tree HEAD lane/certify` reports **no conflict
in `docs/findings.md`** (the appends are in non-overlapping regions). `git merge-tree HEAD
lane/control-plane` conflicts in `factory/readiness.py`, `factory/sessions.py` and
`scripts/local_tracker.py` — **not in `docs/findings.md`**. So git will merge the ledger cleanly, and
then `factory/findings.py:116-126` `load()` — which reads `LEDGER` first, then fragments, and
`continue`s past any id already seen (`:121-123`, commented *"Same id in both places is a
half-finished migration, not two findings"*) — will **silently drop the `docs/findings.d/` F20 and
F21**, i.e. the two ADOPTED design findings that say a gate which cannot pass is a defect. Simulated
and confirmed this run. **F70's fix converted a loud merge conflict into a silent semantic loss, and
nothing in the repo detects a duplicate id** — `malformed()` (`factory/findings.py:147-149`) checks
required fields only. There are **55 findings across four unmerged branches** waiting on this.

**5. `F30` (certify) already named `readiness.py`'s `CONNECTORS` resolution and flagged rather than
fixed it.** `.worktrees/certify/docs/findings.md:190-197`: *"every lane's `python -m factory.readiness`
is currently measuring control-plane's working state whenever that sibling worktree exists"* — and it
does exist, right now. `docs/findings.d/F72-…md` found the same thing from the other direction.
`factory/readiness.py:35-37` is unchanged. F30's general rule is worth quoting because it also
indicts `factory/launch.py:99-100`: *"never let existence-at-call-time break the tie."*

**6. Our own ledger's line citations have drifted, exactly as the brief warned.** Checked at the point
of citation:

| Finding | Cites | Actually |
|---|---|---|
| F72 | `readiness.py:33` for `CONNECTORS` | `factory/readiness.py:35-37` |
| F72 | `readiness.py:811` for the `aldc-launchpad` resolution | `factory/readiness.py:1033` |
| F20 | `readiness.py:175` for the pass condition | `g_finishes` is `factory/readiness.py:204-224`, condition at `:222-223` |
| F21 | `readiness.py:188` / `:180-190` | `g_succeeds_more_than_fails` is `factory/readiness.py:227-250` |
| F71 | `local_tracker.py:1181` — "a plain `socketserver.TCPServer`, single threaded" | `scripts/local_tracker.py:2357-2362`, now `socketserver.ThreadingTCPServer` |

**Substance holds in all five; precision does not in any.** F71's case matters most: its rejection of
option (c) — a threaded broker — rested partly on the tracker being single-threaded, and it no longer
is. That premise should be re-examined before F71 is closed on its recorded reasoning.

**One more the ledger has not yet been told.** The `suite` gate returned **`FAIL "1 failed, 245
passed"`** and then, at the same commit ~8 minutes later, **`PASS "246 passed"`**. `_suite_fingerprint()`
(`factory/readiness.py:392-409`) hashes the **bytes of the working tree**, deliberately, so a
concurrent session's uncommitted edit changes the verdict. `git status` showed the tree dirty from
another session at both points. That is F72's defect on the **time** axis rather than the cwd axis: a
board number that depends on when you ran it relative to another agent's save. Attribution is
`NOT-MEASURABLE` in the sense `factory/sessions.py:399-404` already defines.

---

## 4. Claims table

`OBSERVED` — I read the file or ran it · `REPORTED` — a finding, prior answer or evidence doc ·
`INFERRED` — my reasoning from the above · `NOT-DETERMINABLE` — and what would settle it.

| # | Claim | Tier | Source | What would falsify it |
|---|---|---|---|---|
| 1 | `g_failure_is_bounded` has no reachable `_pass`; it returns `_fail` unconditionally | OBSERVED | `factory/readiness.py:253-268`; AST walk of every `g_*` probe | A `_pass` branch in that function |
| 2 | `g_orphans_are_reaped` has no reachable `_pass` | OBSERVED | `factory/readiness.py:799-806` | same |
| 3 | `g_corpus_is_tamper_evident` has no reachable `_pass` on any branch, including the one where all four sub-checks succeed | OBSERVED | `factory/readiness.py:543-597` | same |
| 4 | `bounded` and `reaper` are 2 of the 5 `UNATTENDED_GATES`; `corpus` is 1 of the 6 `TRUST_GATES` | OBSERVED | `factory/launch.py:41`, `:46` | a different membership list |
| 5 | ⇒ `UNATTENDED-OK` and `OUTPUT-CERTIFIABLE` are unreachable states of `factory/launch.py` | INFERRED (1-4 + `factory/launch.py:79-91`, `:142-159`) | — | any code path returning those states with a non-`PASS` named gate |
| 6 | `lane/control-plane` carries fixed versions of probes 1 and 2 (`:685`, `:800`) plus `tests/test_readiness_probes_can_pass.py` and `scripts/mutate_readiness_probes.py`; HEAD carries none of them | OBSERVED | AST walk of `.worktrees/control-plane/factory/readiness.py`; `ls` on both trees | those files existing on HEAD |
| 7 | F11 on `lane/control-plane` named all three probes independently, by the same AST method | REPORTED | `.worktrees/control-plane/docs/findings.md:170-196` | a different finding text |
| 8 | The conflict graph is 5 nodes, 2 edges, α(G)=3 | OBSERVED | `factory.lanes.conflicts()`; `factory.claims.parallel_set()`; `factory/lanes.py:95-219` | a third edge |
| 9 | Edges are computed from a hand-written prose `touches` field, not from files | OBSERVED | `factory/lanes.py:251-254`, `:8-11`, `:103/:130/:155/:177/:201` | `_touch_set` reading the filesystem or git |
| 10 | Reordering the words in one `touches` string would silently delete an edge and change the ceiling to 4 | INFERRED (9 + `.split()[0]`) | — | a validator rejecting a `touches` value with no path in it |
| 11 | Nothing in the repo computes a maximum independent set; `parallel_set()` is greedy and says so | OBSERVED | `factory/claims.py:284-296`, esp. `:288-290` | an exact MIS implementation |
| 12 | Worktrees isolate `agent-factory` only; the two lanes forming the `pipelines.py` edge work in `prefect-connectors`, which is not isolated | OBSERVED | `factory/worktrees.py:37-38`; `factory/lanes.py:102`, `:154` | a `prefect-connectors` worktree per lane |
| 13 | `~/.claude/{sessions,jobs,projects,settings.json,skills}` are shared, unscoped, and carry four instruments plus one gate | OBSERVED | `factory/sessions.py:27`,`:117`,`:118`; `factory/runs.py:45`; `factory/readiness.py:999`; live read of `~/.claude/settings.json` (`PreToolUse` → `scripts/hooks/lane-bus.py`) | any per-lane scoping of `$HOME` |
| 14 | A remote lane silently loses `finish()`'s liveness guard, the cost measurement, bus delivery and gate `chain` | INFERRED (13 + `factory/finish.py:67-72`, `factory/runs.py:86-87`, `factory/bus.py:148-157`, `factory/readiness.py:1002`) | — | any of those four degrading loudly |
| 15 | `AgentSpec` has no `tier` field, so `architecture-v0.md:99`'s "declared in the agent spec" describes nothing | OBSERVED | `factory/blueprint.py:19-33` vs `docs/specs/architecture-v0.md:99`, `:119` | a `tier` field |
| 16 | `spec.tools` and `spec.prohibition` reach no process | OBSERVED | `factory/deploy.py:88-92` | either appearing in the argv |
| 17 | The live launch path passes no permission mode, no allowed-tools, no sandbox, no budget and no turn cap | OBSERVED | `scripts/local_tracker.py:112-141`, `:310-354`, esp. `:353` | any such flag in `_launch_script` |
| 18 | `--dangerously-skip-permissions` is granted on the premise that a worktree is a boundary | OBSERVED | `factory/deploy.py:92`; `prefect-connectors/orchestrator/server.py:731`; policy at `docs/research/agent-factory-research-prompts.md:287` | the flag being conditional on something else |
| 19 | ⇒ Every instrument the readiness board reads is inside the write radius of the agent it measures | INFERRED (13 + 18 + `factory/corpus.py:38-39` + `factory/readiness.py:594-596`) | — | any instrument on a filesystem the lane cannot write |
| 20 | `finish()`'s ledger check cannot refuse: `nothing_to_report()` is a global count and matches the ledger's own instruction sentence | OBSERVED — `findings.nothing_to_report()` → 1, sole match `docs/findings.md:25` | `factory/finish.py:89-92`; `factory/findings.py:152-156` | a per-lane count, or that string absent from the ledger header |
| 21 | Gate `durable` announces "pushed to origin" having measured only that a remote is configured | OBSERVED | `factory/readiness.py:600-611`, esp. `:606-609` | a `rev-list @{u}..HEAD` in that probe |
| 22 | All 8 currently-passing gates are declarative (file-exists / substring / non-empty-list / remote-configured / regex-in-a-draft); every behavioural gate is FAIL, UNMEASURABLE or NOT_RUN | OBSERVED | `python -m factory.readiness` (8/30) + `factory/readiness.py:961-973`, `:981-994`, `:997-1008`, `:530-540`, `:600-611`, `:1026-1045` | any behavioural gate passing |
| 23 | Cost is measured per lane in tokens, wall clock and model, with an honest `NOT-RECORDED` basis; no dollar figure exists | OBSERVED | `factory/runs.py:82-130`, `:128-130`; live `runs.report()` | a price table in the repo |
| 24 | `runs.cost()["wall_clock_s"]` is the first-to-last transcript span across **all** sessions in that cwd, not lane runtime — control-plane reads 113,408 s (31.5 h) | OBSERVED | `factory/runs.py:92-127`; live `runs.report()` | per-session segmentation in that function |
| 25 | `runs.ABANDONED` is defined and written by nothing | OBSERVED | `factory/runs.py:41`; grep over `factory/` and `scripts/` | any writer |
| 26 | Five finding ids collide across four branches with different meanings (F20, F21, F30, F31, F32) | OBSERVED | `_split()` over all five ledgers, this run | the titles matching |
| 27 | The collision merges cleanly in git and is then silently dropped by `load()` | OBSERVED — `git merge-tree` shows no `findings.md` conflict for `lane/certify` or `lane/control-plane`; simulated `load()` drops `docs/findings.d/` F20 and F21 | `factory/findings.py:116-126`, esp. `:121-123` | `load()` raising on a duplicate id |
| 28 | `readiness.py`'s `CONNECTORS` still resolves to `.worktrees/prefect-connectors` from any lane, and that worktree exists today | OBSERVED | `factory/readiness.py:35-37`; `git worktree list` | the resolver preferring the canonical path |
| 29 | `factory/launch.py:99-100` resolves `.data` per-worktree, the F70/F71 shape — **latent**, because no lane branch carries `launch.py` today | OBSERVED (code) + OBSERVED (absence on all four branches) | `factory/launch.py:99-100`; `ls .worktrees/*/factory/launch.py` | that module using `_repo.data()` |
| 30 | The bus hook fires only for cwd under `.worktrees/<lane>`, so the two `prefect-connectors` lanes never receive traffic | OBSERVED | `factory/bus.py:148-157`; `scripts/hooks/lane-bus.py:35-37` | lane identity derived from something other than cwd |
| 31 | The bus delivery mechanism is registered in `~/.claude/settings.json`, outside the repo | OBSERVED — live read | `PreToolUse` → `scripts/hooks/lane-bus.py` | a repo-scoped hook registration |
| 32 | The `suite` gate returned FAIL then PASS at the same commit ~8 min apart, with the tree dirty from another session | OBSERVED (two runs this session) | `factory/readiness.py:392-409`, `:462-506` | a fingerprint over committed bytes only |
| 33 | Our 41.7% is a citation (arXiv 2607.04697v2), not an internal measurement; R5 always said so; four downstream places lost the attribution | OBSERVED | `docs/research/answers/R5-answer-build-velocity.md:25`; drift at `factory/worktrees.py:3-5`, `scripts/local_tracker.py:124-125`, `docs/research/R10-…:137`, `docs/research/R8-…:115` | an internal conflict-rate measurement log predating 2026-07-07 |
| 34 | `docs/research/SYNTHESIS.md:1278-1305` reached the same conclusion on claim 33 independently | REPORTED | that file (⚠ uncommitted, modified by another session while I read it) | — |
| 35 | `architecture-v0.md:34` ("Cost unknown — MEASURED, nothing records tokens or wall clock") is stale | OBSERVED | `factory/runs.py:28-29`, `:82-130` vs `docs/specs/architecture-v0.md:34`, `:186` | `cost()` not returning `MEASURED` |
| 36 | `architecture-v0.md:109`/`:187` ("the hash gate… covers **0**" / "0 of 15") is wrong; the live figure is 6 of 15 | OBSERVED (live gate output) + REPORTED (`docs/research/SYNTHESIS.md:1098-1131`) | `factory/readiness.py:867-879` | the gate reporting 0 |
| 37 | `terminal-configuration.md:174-188`'s `--simulate` is not built | OBSERVED | grep over `factory/` and `scripts/local_tracker.py` | a simulate mode |
| 38 | `factory/deploy.py` has no caller in this repo | OBSERVED | grep for `RepoDeployer` / `run_agent` outside `factory/deploy.py` and the worktree copies | any import of it |
| 39 | R17 §4.2 step 1's "runs in WSL2, already on the box" does not describe our launcher, which spawns PowerShell on native Windows | OBSERVED | `scripts/local_tracker.py:136-141`; R17 [B-15 ✓] | a WSL2 launch path |
| 40 | Whether `QA_DG1_GEP_PREFECT_PR` is a share-consumed (imported) database | **NOT-DETERMINABLE** | `blueprints/windsorai_gep.yaml:15` records the name and nothing else | `SHOW DATABASES LIKE 'QA_DG1_GEP_PREFECT_PR'` (an imported DB reports an `origin`), or a declared `share_consumed:` field. **Needs a credential — not requested** |
| 41 | What grants the lane's Snowflake role actually holds today | **NOT-DETERMINABLE** | no role/grant code exists in the repo | `SHOW GRANTS TO ROLE <r>` from a scratch session, or an exported role model committed to the repo. **Needs a credential — not requested** |
| 42 | Our own FP rate for LLM code review (R17 §10's ask) | **NOT-DETERMINABLE** | 55 reviewer-sourced findings across four branches, none carrying an acted/dismissed disposition | Extend `factory/findings.py:43` `STATUSES` with `ACTED / DISMISSED / DISPUTED`, require it on reviewer-sourced entries, count over one month |
| 43 | Whether `architecture-v0.md`'s T2 clone economics hold for us | **NOT-DETERMINABLE** | no warehouse configuration in this repo | Our warehouse sizes, `AUTO_SUSPEND` values and whether lanes would share one — plus claim 40 |

---

## 5. Outside evidence lane

Run in parallel with §0–§4, **web-only and repo-blind**: the lane was forbidden to read this
checkout, so it could not be pulled toward agreeing with us. Its brief was narrowed to the
structural questions R17 left open, per §3 (the field survey is R17's and was not re-derived).
Every claim below carries a URL its lane fetched; the ones marked ✓✓ were **re-fetched and
re-read by the orchestrator**, not taken on the lane's word.

### 5.1 The headline, and where it converges with §1.2(3)

> *"Every organisation that has actually built a capability tier for a coding agent puts the
> boundary in the kernel or the hypervisor, and says explicitly that anything above that line is
> not a boundary."*

⭐ **The two lanes reached §1.2(3)'s verdict from opposite directions and never saw each other's
work.** §1.2(3) got there by reading `factory/blueprint.py:19-33` and finding no `tier` field; the
web lane got there by reading Anthropic's own docs. Independent convergence is the strongest signal
this pass produced, and it is worth more than either lane alone.

**There are three tiers of realness, not two, and `architecture-v0.md` does not distinguish them:**

| Tier | Mechanism | Holds against |
|---|---|---|
| **Declared** | `CLAUDE.md`, a system prompt, a lane prompt | nothing — a model that chooses to comply |
| **Harness-enforced** | permission rules, evaluated pre-execution by the CLI | a model, but string-matched and leaky by the vendor's own account |
| **OS/RBAC-enforced** | seatbelt / bubblewrap / a Snowflake grant | the process, whatever the model decided |

✓✓ https://code.claude.com/docs/en/sandboxing — *"The operating system enforces the sandbox
boundary on the running process, so it holds regardless of what the model chose to run and even if
an allowed command does more than its name suggests."* `OBSERVED`

✓✓ https://code.claude.com/docs/en/permissions — on `CLAUDE.md` guidance: *"This shapes what Claude
tries but doesn't enforce a boundary."* `OBSERVED` — **the vendor says in one sentence what
§1.2(3) proves about our ladder.**

### 5.2 Why a deny-list tier would not have worked anyway

`architecture-v0.md:83`'s T0 says "no DB verbs". Even with permission rules configured — which
§1.1 shows we have none of — the mechanism does not reach that far:

✓✓ https://code.claude.com/docs/en/permissions — *"Read and Edit deny rules apply to Claude's
built-in file tools and to file commands Claude Code recognizes in Bash… **They don't apply to
arbitrary subprocesses that read or write files indirectly, like a Python or Node script that opens
files itself.**"* `OBSERVED`

A `deny: Bash(snowsql *)` does not stop `python -c "import snowflake.connector"`. The same page
calls argument-constraining Bash patterns *"fragile"* in its own voice. **A verb-level tier is
unenforceable in principle unless the credential is absent** — which is the same place §1.2(3) and
R17 §4.3 land.

And the escape hatches are the agent's to take (all `OBSERVED`, same sandboxing page): the model
*"may retry the command with the `dangerouslyDisableSandbox` parameter"*; a sandbox that cannot
start *"shows a warning and runs commands without sandboxing"* by default; `excludedCommands` *"has
no equivalent managed-only lockdown"*; and a sandboxed command can write *"shell startup files,
executables on `$PATH`, or `~/.claude/settings.json`"* and *"use them to widen its own access on the
next run"* — which is §1.2(2) group C restated by the vendor as a threat model.

### 5.3 ⛔ The Windows finding — this corroborates §1.1's BLOCKED verdict from outside

Three independent vendors, all `OBSERVED`:

- Claude Code: *"The sandbox is built into Claude Code and runs on macOS, Linux, and WSL2. **Native
  Windows is not supported.**"*
- Devin CLI (https://docs.devin.ai/cli/sandbox): *"OS-level sandboxing is not currently supported on
  Windows"*
- Cursor (https://cursor.com/blog/agent-sandboxing): Windows means *"the Linux sandbox running
  inside WSL2"*; a native equivalent is *"significantly harder"*

§1.1 marked R17's sandbox recommendation **BLOCKED as the launcher is built**, because
`scripts/local_tracker.py:136-141` launches lanes into native PowerShell. The outside lane reaches
the same wall without ever seeing that line. **On this host, T0's "no network egress, no DB verbs"
has no available enforcement mechanism at all — it is not a weak control, it is a sentence.**

### 5.4 The egress allowlist is the wrong thing to build T1 on

`architecture-v0.md:84` specifies T1 as "container + egress allowlist". The published record on
hostname allowlists is four independent, dated failures:

| # | Failure | Tier | Source |
|---|---|---|---|
| 1 | **Domain fronting — vendor-documented against itself**: *"code running inside the sandbox can potentially use domain fronting or similar techniques to reach hosts outside the allowlist"* | `OBSERVED` ✓✓ | code.claude.com/docs/en/sandboxing |
| 2 | **CVE-2025-66479** — *"network sandboxing was not properly enforced when the sandbox policy lacked configured allowed domains"* (`< 0.0.16`). **The most restrictive possible policy meant allow-everything** | `OBSERVED` ✓✓ | api.osv.dev/v1/vulns/CVE-2025-66479 |
| 3 | **Exfiltration through a correctly-allowed host** — *"Every function reachable through any domain on an allowlist is now an attack surface. Allowing api.anthropic.com meant allowing file uploads to arbitrary Anthropic accounts."* | `OBSERVED` | anthropic.com/engineering/how-we-contain-claude |
| 4 | **Allowlisted-command poisoning, CVE-2026-22708** — injection sets `PATH`/aliases so a *trusted* command runs a payload | `OBSERVED` | github.com/cursor/cursor/security/advisories/GHSA-82wg-qcm4-fp2w |

And the vendor's verdict on building your own: *"Battle-tested hypervisors, syscall filters, and
container runtimes have survived more adversarial attention than anything you'll build"* … *"the
standard primitives held while our own work around them exposed flaws"* (`OBSERVED`,
anthropic.com/engineering/how-we-contain-claude). ⭐ **The primitives held; the bespoke proxy is what
broke.** A one-engineer bespoke proxy has *less* adversarial review than Anthropic's, not more.

This also independently confirms §1.1's `WRONG-AS-SPECIFIED` on `architecture-v0.md:84-85`: R17 §7
refuses a plain container on escape rates; the web lane refuses the *allowlist* on breach history.
**Two different refutations of the same two lines.**

### 5.5 ⭐ What the outside lane made visible in our own code — the un-taken boundary

This is the one finding neither lane could have produced alone: the web lane supplied the
documentation, and the orchestrator then walked our route. **`OBSERVED`, verified in both
directions.**

Claude Code enforces **four worktree isolation checks** that a session cannot switch off
(✓✓ https://code.claude.com/docs/en/worktrees): it blocks an `Edit`/`Write`/`NotebookEdit`
targeting the main checkout; blocks a Bash/PowerShell command whose working directory resolves
there; blocks git redirects via `-C`, `--git-dir`, `GIT_DIR`, `GIT_WORK_TREE` or a `cd`; and blocks
commands whose shape it cannot verify. In the doc's own words: **"You can't turn this check off."**

⛔ **We do not get any of it.** Those checks apply while a session *is isolated in a worktree* —
started with `--worktree`, entered with `EnterWorktree`, or resumed into one. We create worktrees
with plain `git worktree add` (`factory/worktrees.py:89-91`) and launch a **bare `claude`**
(`scripts/local_tracker.py:353`) with `cwd` set to the worktree (`scripts/local_tracker.py:420`).
`--worktree` appears **nowhere** in this repo outside prose about other tools, and
`docs/research/answers/R12-answer-session-manager-ui.md:39` says it plainly: *"We use Git
sub-worktrees manually."*

**So the one enforced, free, already-installed boundary that would have stopped a lane writing to
the primary checkout is the one we opted out of** — while simultaneously granting
`--dangerously-skip-permissions` on the stated grounds that the worktree *is* the boundary
(`factory/deploy.py:92`, `docs/research/agent-factory-research-prompts.md:287`). §1.2(3) proves the
premise false from the inside; this shows the fix was sitting in the launcher flag all along.

⚠ **It is not a free swap and should not be sequenced as one.** `--worktree` puts worktrees under
`.claude/worktrees/<name>` on a `worktree-<name>` branch, which is not `.worktrees/<lane>` on
`lane/<id>` — and `factory/worktrees.py:38,56` and `factory/finish.py:34` all resolve the lane path
by that convention. Adopting it means either a `WorktreeCreate` hook or moving the convention.
**Scope it as a spike, not a one-liner** — and note it buys filesystem containment only, not the
network or DB containment §1.3 says is the actual blast radius.

### 5.6 A correction to the outside lane — Windows cuts the other way here

The web lane flagged, as dangerous shared state, that a *"Yes, and don't ask again"* approval in one
worktree *"applies in the main checkout and in every other worktree of the repository, and it
survives the worktree's removal"* — a cross-tier capability leak inside the isolation mechanism.

✓✓ **Re-fetched, and the very next sentence exempts us:** *"On Windows and the other cases where
Claude Code keeps the local file in the starting directory, the rule stays with that worktree."*

This host is Windows 11. **The leak does not apply**, so it is correctly absent from §1.2(2) — that enumeration reached the right answer by reading our code, not by knowing this exemption existed. Recorded
because it is the shape of error this pass exists to catch: the lane's quote was verbatim and
accurate, and its *verdict for us* was still wrong. `NOT-APPLICABLE (platform)`.

Same class, opposite sign: `.worktreeinclude` — the mechanism that copies `.env` and
`config/secrets.json` into every new worktree — is a **Claude Code** feature applied to worktrees
*Claude Code creates*. Ours are created by `git worktree add`, so it never runs. We are not exposed
to it today, and we would acquire that exposure the moment §5.5 is adopted. **Note it before
adopting, not after.**

### 5.7 The concurrency ceiling, from outside

Two independent practitioners, both `REPORTED`, both isolating with git worktrees:

- Addy Osmani (addyosmani.com/blog/code-agent-orchestra/): *"3-5 teammates is the sweet spot"*;
  *"Don't run more agents than you can meaningfully review"*; ⭐ *"The bottleneck is no longer
  generation. **It's verification.**"*
- codeongrass.com — practical range *"2–5 … sessions simultaneously"*, binding constraint named as
  **API rate limits**; and, exactly on point for §1.3: *"Git worktrees handle filesystem isolation
  cleanly. **They do not handle anything about what your code does when it runs.**"*

**Our α(G) = 3 lands where two independent practitioners put the ceiling — and neither of them
reaches it via a conflict graph.** §1.2(1) shows ours is a five-row prose table; the field says the
number is right for reasons that have nothing to do with the mechanism we derive it from. ⚠ **Both
figures are rules of thumb with no denominator** — do not promote either to a measurement.

Faros AI's telemetry (22,000 developers, 4,000+ teams) reports median review time **up 441.5%** and
incidents-per-PR **up 242.7%** at high AI adoption — but the lane checked the methodology and found
the comparison is each organisation's own lowest-vs-highest adoption period with **no absolute
baselines published**. `REPORTED, direction only — do not cite the magnitude.`

### 5.8 Q3 — nobody has built T2. `ABSENT`.

The lane searched Snowflake, Databricks, dbt Cloud, Neon, PlanetScale, Dolt, LakeFS, Nessie and
Tinybird for a system that gives an *automated agent* an ephemeral branch **and enforces** that
production is unreachable from inside it.

**It found none.** The closest published thing (Neon + Cloudflare Sandboxes) injects a branch-scoped
`DATABASE_URL` as an env var, with **no mechanism preventing use of a production connection string
and no automated teardown** — auto-expiry is listed as a future extension. `ABSENT`.

⭐ **This is a finding, not a gap.** `architecture-v0.md:85`'s T2 is not a pattern we are late to
adopt; it is **unvalidated in the field**. Combined with §1.1's `NOT-DETERMINABLE` on whether our
one real target is share-consumed — which R17 §4.4(b) shows would make T2 *undefined* for it — T2 is
the least evidence-backed rung on the ladder and should be sequenced last, which §1.4 already does.

**Teardown is the documented failure mode.** ✓ https://docs.snowflake.com/en/user-guide/tables-storage-considerations
— dropped-clone storage is retained and billed until Time Travel expires, surfacing as
`RETAINED_FOR_CLONE_BYTES`. `OBSERVED`. A published orphan-clone **cost incident**: `ABSENT` — nobody
publishes their warehouse bill mistakes. Design T2 as though it exists: `DATA_RETENTION_TIME_IN_DAYS
= 0`, a lane tag and TTL per clone, and reconciliation against `TABLE_STORAGE_METRICS` rather than
`SHOW SCHEMAS`.

### 5.9 Q4 — what the field says it built too early

One answer dominates, and it is **not** about isolation: **teams build the multi-agent topology
before the verification, and the topology turns out to be the wrong investment.**

- Microsoft's Azure SRE Agent collapsed 50+ specialised agents and 100+ narrow tools back to a
  handful of generalists with broad CLI-shaped tools. ⚠ `REPORTED` — **the primary page is
  JS-rendered and the lane could not read it; it is corroborated only through secondaries. Verify
  before quoting.**
- Anthropic, `OBSERVED` (claude.com/blog/building-multi-agent-systems-when-and-how-to-use-them):
  *"Multi-agent implementations typically use **3-10x more tokens** than single-agent approaches for
  equivalent tasks"*, and decomposition should be **context-centric, not role-centric**.
- Gartner's ">40% of agentic AI projects cancelled by end-2027" is a **forecast, `MARKETED`**, with a
  self-selected 3,412-attendee poll behind it. **Do not cite it as evidence anything has happened.**

⚠ **The Anthropic guidance targets splitting *one task* into planner/implementer/tester. Our lanes
split *independent tasks*, which is the case it endorses. Do not over-apply it to the lane design.**

**UNSEARCHABLE — and this is the finding.** The lane searched rollbacks and abandonments across
several phrasings and found uniformly launch posts and vendor content. The one genuine reversal it
found was publishable *because the team sells the agent*. **Failure is not published, so the
literature's silence is not evidence of rarity — weight it below this repo's own ledger**, which is
what §1.5 does.

### 5.10 ⛔ Figures the outside lane refuted — do not cite these

The lane was instructed to verify every citation and reported four widely-circulated figures that do
not survive contact with their sources. Recorded here so nobody in this estate spends the check
again:

| Figure | Verdict |
|---|---|
| "98% more PRs / 91% increase in review time" (attrib. Moderne) | **The fetched article contains no such figures.** Fabricated upstream |
| "Multi-agent systems consume 4–220× more tokens (UIUC, 7 datasets, 6 models)" | **The paper could not be found.** Repeated confidently by ≥2 secondaries |
| "9.82 GB in 20 minutes" (worktree disk blowup) | No primary source |
| "Median sandbox TTI 690 ms across the top 10 providers" | No methodology, no provider list, vendor-authored (sells the fix) |

This is the same failure mode R17 §10 found three instances of, and the same one this pass's own
§7.2 caught in our brief. **The field's agent-infrastructure numbers are unusually contaminated.
Fetch before citing, every time.**

### 5.11 ⚠ Where the outside view is WRONG for one laptop — read this before acting on §5.2–§5.4

The lane was required to argue against its own findings. It is right to, and this materially
softens the severity of §1.2(3) without changing its verdict.

**1. The threat model does not transfer, and this is the big one.** Almost every source in §5.2–§5.4
is about containing an **adversary** — prompt injection from untrusted repos, exfiltration to an
attacker's account. Our lanes run on our own code, on our own laptop, with the operator present. The
realistic failure is **an agent doing something expensive and wrong to production** — a
`CREATE OR REPLACE` on the wrong schema — not an adversary tunnelling out over DNS. Domain fronting,
null-byte parser differentials and metadata-server SSRF are close to irrelevant here.

⭐ **Which is why the cheap control is the right one: a T0/T1 lane must not *possess* a credential
that can write to production.** Credential absence beats egress filtering, costs nothing, cannot be
domain-fronted, and needs no sandbox — so it works on native Windows today. **This is the same
conclusion §1.2(3) reaches from `factory/blueprint.py`, and it is the single point on which both
lanes and R17 §4.3 agree.** It is why §1.4's sequence is right to put the grant envelope above the
container.

**2. "Human review is the ceiling" assumes PRs and a second human.** Osmani's 3–5 and Faros's 441%
both measure organisations where a *different* person reviews. Here one person is author,
orchestrator and reviewer, and can review by **outcome** (did the gate pass?) rather than by diff —
which is exactly what `factory/readiness.py` is for. The published ceiling is not measuring our
bottleneck. ⚠ It cuts both ways: there is also no second pair of eyes.

**3. Most "you need containers" advice is written by vendors selling containers**, and priced for
teams with real infrastructure. On one laptop, port and daemon collisions are *visible* failures —
the server does not start and you know at once. Annoying, not dangerous. §1.2(2)'s genuinely
dangerous rows are the ones where **an instrument is inside the write radius of the agent it
measures**, and those are unaffected by this discount.

**4. Where the outside view holds regardless of scale.** The Windows finding (§5.3) is not a
threat-model question — the mechanism does not exist on this host, so any tier claiming OS
enforcement is claiming something false. And "do not build your own proxy" (§5.4) holds *harder* at
our scale, not less.

---

## 6. How this lane ran — both halves

**What this lane did better than an outside model could.** It read the source and ran it. Every
structural claim above was checked against bytes on disk at the line cited, and the load-bearing
ones were confirmed by execution rather than by reading: `factory.lanes.conflicts()` and
`claims.parallel_set()` for the ceiling; an AST walk over all 27 probe functions for the
unpassable-gate claim; `findings.nothing_to_report()` returning 1 for the dead `finish()` check;
`git merge-tree` plus a simulated `findings.load()` for the silent-drop claim; two runs of
`python -m factory.readiness` and `python -m factory.launch`. R8's failure — an answer with zero
file paths against a pack whose rule was "cite a file and a line" — is the thing this format exists
to prevent, and the way to prevent it is to be in the checkout. Four of the findings in §0 and §1.5
are of a kind no evidence pack could have carried, because they are facts about **what the code does
not contain**: a missing `_pass` branch, a missing caller, a missing `tier` field, a missing budget
flag. An absence is invisible in an excerpt.

**Where it was weaker, and it is the declared risk of a `STRUCTURE_CRITIQUE`.** This lane is *us*.
It read our code, in our vocabulary, having absorbed our arguments for why each shape is right — and
those arguments are good, which is precisely what makes them hard to resist. Three concrete costs:

1. **I checked our claims and largely did not question our questions.** The 30 gates were audited
   for whether each can pass, refuse and be cheated. I did not seriously ask whether *these thirty*
   are the right thirty, or whether "unattended migration readiness" is even the right frame. R17,
   with no access to us, was free to say "your 3 of 14 is normal-to-good, not a defect" (§4.8,
   [D-10 ✓, D-17 ✓]). Nothing in my Phase 1 view produced a reframing of that size, and I am not
   confident that is because none was available.
2. **Blind-first bought less independence on the specs than on the code.** By the time I opened
   `architecture-v0.md` I had a code-grounded view, and attacking it was easy. But the *lane
   ledgers* in Phase 3 had already found my headline (F11), and I cannot fully rule out that the
   direction I searched in Phase 1 — "which probes can refuse, which can pass" — is itself a habit
   this repo trained into me through its own docstrings, which say it repeatedly
   (`factory/readiness.py:87-92`, `factory/lanes.py:56-57`, `factory/claims.py:191-195`). The
   convergence with F11 is genuine and I found it before reading it; whether it is *independent* is
   a weaker claim than I would like.
3. **I could not price anything.** Every cost question — the E16 session pool, the warehouse bill,
   whether cloning is affordable — is `NOT-DETERMINABLE` from this repo and had to be inherited from
   R17. The lane that can read the code is the lane that cannot read an invoice.

**What I could not determine, and why.** Four things, listed as claims 40-43. Three need a
credential I deliberately did not request (whether our target database is share-consumed; what
grants the lane role holds; our warehouse configuration) — R17 §4.4(b) makes the first of these
decisive for T2, so it is the highest-value unanswered question in this document, and it costs one
`SHOW DATABASES`. The fourth — our own false-positive rate for LLM code review, which R17 §10 says
the field will not supply and R18 should generate — is not blocked by a credential but by a missing
field: 55 reviewer-sourced findings exist across four branches and not one records whether it was
acted on. That is a denominator we could start collecting this week and cannot reconstruct
retroactively.

**Citations I found to be wrong.** Five, all in our own ledger, all substance-holds/precision-fails,
listed in §1.5 item 6. One of them matters beyond bookkeeping: F71 rejected a threaded broker partly
because `scripts/local_tracker.py` was single-threaded, and it is now `ThreadingTCPServer` at
`:2357-2362`, so that finding should be reopened on its own terms rather than closed on its recorded
reasoning. Separately, two claims in `docs/specs/architecture-v0.md` are false against the current
code and are still being cited: `:34` (cost unrecorded) and `:109`/`:187` (hash covers 0 of 15).

---

## 7. Orchestrator verification ledger — what was checked, and what changed

Per the skill's §3: no citation was promoted to a finding without being opened. This is what the
orchestrator re-verified **independently of both lanes**, and the result honestly reported.

### 7.1 Re-verified and CONFIRMED — substance and line numbers both

| Claim | Where | How checked | Result |
|---|---|---|---|
| α(G) = 3, graph is two disjoint edges + one isolated vertex | `factory/lanes.py:251-270` | Built the graph by hand and brute-forced the true maximum independent set | ✓ `('control-plane','certify','artifact')`. **Independently reproduced before reading Lane A** |
| `_touch_set()` reads prose, not files | `factory/lanes.py:251-254` | Read the function; printed every lane's touch set | ✓ Exact. Also: the test is **exact string-set intersection**, so a parent/child path overlap (`docs/artifacts/` vs `docs/artifacts/x.html`) produces **no edge** — an additional silent under-count |
| `parallel_set()` is greedy, not a true MIS | `factory/claims.py:283-296` | Read it; ran it | ✓ Returns `['control-plane','artifact','grain']`. Its own docstring says so |
| Three probes have no reachable `PASS` | `readiness.py:253-268`, `:799-806`, `:543-597` | Read every exit path | ✓ **Confirmed exactly.** Note `g_corpus_is_tamper_evident`'s *happy* path also terminates in `_fail` at `:597` |
| Two launch levels are therefore unreachable | `factory/launch.py:41`, `:46` | Read both tuples | ✓ `UNATTENDED_GATES` contains `reaper` + `bounded`; `TRUST_GATES` contains `corpus` |
| The `finish()` ledger check is dead | `finish.py:89-92`, `findings.py:152-156` | Read both; **ran** `findings.nothing_to_report()` | ✓ Returns **1**. The conjunct can never be true |
| `factory/deploy.py` has no caller | repo-wide grep | Searched `factory/`, `scripts/`, `tests/` | ✓ Zero callers. The only mention is `scripts/build_r13_pack.py:93` **asserting that it executes AgentSpec** — a false claim in our own docs |
| Lane B's Claude Code sandboxing/permissions quotes | 2 vendor pages | **Re-fetched both** | ✓ Verbatim and accurate |
| Lane B's CVE-2025-66479 | OSV API | **Re-fetched** | ✓ Accurate: `< 0.0.16`, empty allowlist meant allow-all |

### 7.2 Corrected — substance held, the verdict did not

| Claim | Correction |
|---|---|
| Lane B: worktree permission approvals leak across lanes | **Verbatim quote correct; wrong for this host.** The next sentence exempts Windows. Not applicable here — see §5.6 |
| **The brief's own `F53` citation** | ⛔ `F53` **does not resolve in the primary repo.** `docs/findings.md` holds F1–F10; `docs/findings.d/` holds F20, F21, F70–F74. F53 exists only at `.worktrees/artifact/docs/findings.md:238` — an **unmerged lane branch**. Its subject is also narrower than the brief implies: an untracked, machine-local `node_modules` under `~/.claude/skills/impeccable`, i.e. a *reproducibility* gap, not cross-lane visibility of skill edits. The brief's underlying point survives; its citation does not resolve for any reader of the primary checkout |
| Finding ids "collide" (brief §2) | **Understated.** They do not merely collide, they are **already ambiguous in the record**: `F20` is *"Gate `finishes` can never pass"* in `docs/findings.d/` and *"An instrument that counts its own writes reports the wrong period"* on `lane/control-plane`; `F30`–`F32` mean different things on `lane/certify` and `lane/control-plane`. **A bare `FNN` citation in this estate is unresolvable without naming a branch** — which is what §1.5 step 6 fixes and why it ranks where it does |

### 7.3 How this pass ran — both halves, and what it cost

**LOCAL SUBAGENTS**, via the `deep-research` skill, in this checkout: one deep repo lane
(blind-first, opus), one repo-blind web lane (opus) dispatched in the same message so neither could
see the other, plus orchestrator verification throughout.

**This pass was less independent than an outside model, and far stronger on file-and-line claims.**
Both halves are true.

*Less independent:* the deep lane read our brief, our specs and our prior answers, and an agent
inside this estate is pulled toward agreement. §2's compensations were applied — strict blind-first
phasing (code → strawman → our findings → R17, in that order), a genuinely repo-blind second lane,
and independent orchestrator re-derivation of the two highest-stakes claims **before** reading the
lane's version of them. The convergences in §5.1 and §5.11 are load-bearing precisely because the
lanes could not see each other.

*Stronger on file-and-line claims:* R8's failure — an answer with **zero** file paths against a pack
whose own rule was "cite a file and a line" — is what this format exists to prevent. Four of the
findings here are facts about **what the code does not contain** (a missing `_pass` branch, a
missing caller, a missing `tier` field, a missing budget flag), and an absence is invisible in an
evidence pack. §5.5 exists only because a web lane and a repo lane were both in play.

**Weigh §0, §1.1, §1.2 and §7.1 as strong** — they are file-and-line claims re-verified by
execution. **Weigh §1.4's ordering and §5.11's judgement as partial**, the same way R13 run 2 and
R14 were weighed.

⚠ **What this pass did not do.** It touched no credential — so every claim about what our lane user
can actually reach in Snowflake is `NOT-DETERMINABLE`, as §1.1 says in four rows. That is the
brief's §3 working as intended, and it is also the largest single hole in the audit: **the blast
radius that §1.3 calls the real one is the one thing this pass could not measure.**
