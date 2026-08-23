# Product end state — what this is for, stated so a research pass can design against it

**Written 2026-08-23.** It did not exist before today, and that is a finding in itself: **R8, R13
and R14 were all dispatched without it.** Three research passes are being asked what to build while
carrying no statement of what the thing is *for* commercially, which is how you get an architecture
that is excellent at the wrong objective.

Sources, so nothing here is invented: the commercial brief
`aldc-launchpad/docs/readouts/zeus-foundry-brief.html` (18 Aug 2026, measured against
`prefect-connectors` @ `d04c577`), this repo's `README.md`, and the measurements in
`docs/research/ui-surface-inventory.md`. Every line carries its basis:

`MEASURED` we ran it and have the number · `DERIVED` computed from something measured ·
`STATED` a written brief or decision says so · `ASSUMED` **nobody has confirmed this — see §7**

---

## 1. The two products

`STATED` — the 18 Aug brief. Names are placeholders chosen in that document and cheap to change;
the argument does not depend on them.

| | **Zeus Chat** | **Zeus Foundry** |
|---|---|---|
| Is | enterprise knowledge and institutional memory | pipeline construction, proof and assurance |
| Holds | client decisions, meeting outcomes, credential history, why a thing was built that way | the 18-stage migration procedure, its gates, its evidence and its watchers |
| Serves | anyone who would otherwise ask a colleague — and any agent that would otherwise proceed without context | data engineers running migrations; delivery leads; clients who want the proof rather than the assurance |
| Reached via | MCP — queryable by people and by agents | the build plane at `:8765` |

> **"Zeus Chat holds what the company knows. Zeus Foundry builds the data pipelines that feed it —
> and refuses to call one finished until it can show the evidence."**

⭐ **The suite's thesis in one line: a migration becomes a repeatable, costed, evidenced procedure
instead of an expert's private project — and a silent failure becomes something the system notices
before the client does.** `STATED`

## 2. Where `agent-factory` sits, and why it exists separately

Foundry's pipeline has **agent stages**: stages where an LLM reads a legacy connector, diffs it
category by category, implements what is missing, and commits a real diff. Three of those stages
are **71.4% of a migration's active time** `MEASURED`.

**`agent-factory` is what builds, versions and certifies the agents that run those stages.** Foundry
is the procedure; this repo is the manufacture and the assay of the workers inside it. That
division is why the two are separate repos and why this one's founding claim is narrower than the
product's:

> **A team of agents did the work, and we can prove it — or we can prove we could not tell.**

```
agent-factory        builds + certifies the agents        ← this repo: blueprints, GreenContract, gates
prefect-connectors   Foundry — the 18-stage build plane   ← the procedure the agents execute
Prefect 3 on Azure   the run plane                        ← where connectors actually execute
aldc-launchpad       evidence, boot prompts, ops SQL      ← the memory layer
```

**The build plane never runs a connector; the run plane never builds one.** `STATED` A fix to one is
invisible in the other, and that is the single most useful thing to understand about the system.

## 3. The end state, in the order it has to arrive

| Horizon | End state | Where we are, measured |
|---|---|---|
| **1. A team migrates one connector** | an agent team takes a connector from legacy to production through the 18 stages, and the GreenContract certifies the result `PASS` — not `UNMEASURABLE` | **1 of 49 connectors proven end to end** `MEASURED`. Zero have been migrated by a *team* |
| **2. The procedure is repeatable by anyone** | a new engineer runs the same 18 stages the senior one does, with the same gates and the same refusals — the pipeline *is* the runbook | the lane loop works but **nothing about it is repeatable without the person who invented it** `MEASURED` |
| **3. Teams are assembled, not hardcoded** | pick a ticket, compose a team (roles, models, effort, tool scope, isolation tier, contract version), version it, run it, certify it — with the config hash pinned to the verdict | `TeamSpec` exists and **nothing in the estate runs one** `MEASURED`. The hash covers **0 of 15** identity dimensions |
| **4. It runs unattended** | agents work without a human in the loop except where a human is *required* — merge, per-secret grant, promotion to prod | **3 of 14** recorded runs finished with no human `MEASURED` |
| **5. It is sellable** | a client is shown a parity report against their own historical data, with checks and verdicts named — not a screenshot of a green tick | the parity machinery exists in Foundry; **no client has been shown one** `ASSUMED` — see §7 |

## 4. What the money argument actually rests on — and it is not time saved

⭐ **The strongest evidence the product has is five faults that every green light missed.** None of
them is a time saving. All `MEASURED`:

| Fault | Why it matters |
|---|---|
| A connector ran **~24 times reporting COMPLETED with zero tables** in its schema | a green run plane meant nothing; this is why the watcher is deterministic code, not an agent |
| A migration judged on **22% of itself** — one of eleven flows triggered | every downstream signal read healthy because *some* rows landed; the shortfall read as missing implementation and nearly sent four people to rewrite working code |
| A correct connector scored **30.2%** | the check was measuring the wrong grain — 14,517 distinct full rows against 4,381 distinct business keys; on the key itself both sides measured **4,381 exactly** |
| A **false certification reproduced before it shipped** | the production baseline is itself 4.86× duplicated; without a relative duplication budget a pipeline writing a correct row set 16 times over would have scored PASS/100%/no failures and auto-approved |
| **Ten containers, one quota, three invisible hours** | a list never cleared between partitions turned 30 uploads into 465; the timeout path recorded no error text at all |

**And the measurement that points the next round of work away from the software:** a proven
migration was **21.6 minutes of active stage time inside 8 h 20 m of wall clock — 4.3%** `MEASURED`.
The pipeline is not the bottleneck. **Waiting for a human to review and merge is.** Automating the
build did not remove the wait; it made the wait visible and attributable.

> ⭐ **This is the number any architecture or UI recommendation must move.** Today, in this repo,
> two PRs are fully green and have waited **6 and 9 days**, and four agents sat blocked on questions
> written in plain English that no surface displays. `MEASURED` An architecture that renders agents
> more beautifully while the merge queue stays at nine days has optimised the wrong end.

## 5. What it replaces, reduces and retains

Stated conservatively on purpose. **Foundry replaces a class of manual coordination work; it
replaces no platform.** `STATED`

| Replaced | Reduced | Retained |
|---|---|---|
| hand-written migration runbooks | Prefect UI (embedded behind an auth proxy) | Prefect 3 — the run plane |
| ad-hoc SQL worksheets for before/after | GitHub Actions checked by hand | Snowflake — the warehouse |
| spreadsheet migration trackers | Snowflake console for verification | Jira — the system of record |
| manual ticket status updates | Slack/Teams status pings | GitHub and its CI |
| "has it deployed yet?" polling | separate cost spreadsheets | Azure Key Vault, Blob, ACI |
| tribal knowledge of recurring faults | standalone health dashboards | the legacy stack, until every connector migrates |

**The honest one-liner:** it does not consolidate the platform bill. It consolidates **the human
coordination layer between the platforms already being paid for** — and that layer is where the
migration hours and the undetected faults both live. `STATED`

## 6. The estate this has to get through

`MEASURED` — established by importing every module, not by reading code, which is the difference
between an inventory and a guess:

```
49  connector modules in the estate
 7  live on Prefect v3 today
13  importable, not yet migrated
29  do not import at all  — 20 of the 29 fail on the SAME missing file
 1  proven end to end
```

Most modules have a v3 file and a deployment, **and none of that is evidence of a working
migration.** Concluding *"already complete"* was the most common way a pipeline run was wasted, and
the agent prompts now say so explicitly.

⭐ **The scale sets the shape of the ask.** 48 connectors remain. At one human-supervised migration
per engineer-day this is not a tooling problem, it is a staffing one — which is the argument for a
team that runs unattended, and therefore for everything in §3.

## 7. ⚠ ASSUMED — nobody has confirmed these, and they change the answer

**Do not let a research pass treat these as settled.** Each one materially changes what should be
built:

1. **Is this productised and sold, or internal tooling that makes one agency faster?** The 18 Aug
   brief is written as a *product brief* with buyers and a with/without analysis, which implies
   external. Nothing else in either repo confirms a commercial intent, a price, or a customer.
2. **Who is the buyer, and do they ever open the UI?** §3 horizon 5 says clients are shown proof.
   If a client — a non-engineer — ever opens a surface, the **approval plane is a product surface**,
   not an internal one, and it is currently the plane with no interface at all.
3. **One estate or many?** The launchpad record notes a reframe — *configurable per client, not
   migrate wholesale*. If the end state is N client estates, multi-tenancy stops being a backlog
   item and becomes an architectural premise.
4. **What is the timeline?** 48 connectors and a 3-lane ceiling imply a rate. No date has been
   stated anywhere, so no design can currently be judged too slow.

**Answering these four is Paul's, not a researcher's.** Until they are answered, a pass reading this
document should treat §3 horizons 1–4 as firm and horizon 5 as `ASSUMED`, and should say which of
its recommendations would change under each reading.
