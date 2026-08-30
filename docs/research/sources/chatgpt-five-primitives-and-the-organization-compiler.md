<!-- FILED 2026-08-29 from a ChatGPT response pasted by Paul in session. Body below is VERBATIM. -->

# SOURCE — "The 5 I would obsess over", a ChatGPT product-architecture response

⚠ **This is not an R-series answer and no prompt of ours produced it.** It is a ChatGPT response
Paul pasted on 2026-08-29. It is kept here as a **source** rather than under
`docs/research/answers/` for the reason that folder's README gives: `factory/synthesis.py` globs
`answers/R[0-9]*-answer*.md` and `tests/test_synthesis_current.py` goes red the moment a file
matching that glob is not named in `SYNTHESIS.md`. Filing it there would be a commitment to
reconcile it immediately and would break `pytest` for every other session until someone did.

⛔ **Basis: `EXTERNAL`, unverified, no citations.** Nothing in it has been checked against this
repo, and it contains no measurements of our estate. Treat every architectural claim as a
*proposal to argue with*, not a finding. In particular the numeric tables it contains
(`71% → 84% → 96%`, `$7.40 → $5.10 → $3.80`, `19m vs 11m`) are **illustrative fabrications made by
the responder to show a shape** — they are not measurements of anything and must never be quoted
as though they were.

⭐ **Two things in it are already true here, and reading it as new would be a mistake.** The
`PASS / FAIL / UNMEASURABLE / NOT_RUN` verdict set in its §2 is `factory/contract.py`, shipped and
enforced; and *"agents perform work, the factory determines whether the work is correct"* is the
README's founding sentence. Its genuinely new material is §1 (Organization Compiler), §4 (fork an
execution from a timestamp and A/B it) and §5 (optimise the org chart rather than the prompt).

**Related:** `docs/research/sources/amt-agent-management-terminal.md` (the other unfiled external
source), `docs/specs/golden-workflow-fit.md`, `docs/research/answers/R19-answer-work-taxonomy-and-team-selection.md`
(which argues the honest selector for the next two quarters is a rule-based eligibility filter that
mostly returns "human", and that anything called an optimiser before the dispatch record exists is
speculative — read alongside §5 below).

---

## VERBATIM RESPONSE BEGINS

The 5 I would obsess over

If I were building this product, I would not build all 18 independently.

I'd center the architecture around five primitives.

1. Organization Compiler

This could become the defining feature.

Instead of:

Task
 ↓
Choose Agent
 ↓
Agent executes

you have:

```
                    MISSION
                       │
                ┌──────▼──────┐
                │ Org Compiler │
                └──────┬──────┘
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
    Understand       Design         Verify
     context          team          success
        │              │              │
        └──────────────┼──────────────┘
                       ▼
                Execution Graph
                       │
       ┌───────────────┼───────────────┐
       ▼               ▼               ▼
     Agent A          Agent B         Agent C
       │               │               │
      MCP            Sandbox          A2A
       │               │               │
       └───────────────┼───────────────┘
                       ▼
                 Evidence Graph
                       │
                       ▼
                Independent Judge
                       │
                 PASS / FAIL
```

The organization itself becomes generated software.

2. Proof-Carrying Agent Work

This is the feature I think could create enormous enterprise value.

Every run produces an Evidence Bundle:

```
Mission
├── requested_outcome
├── success_contract
│
├── execution
│   ├── agent_runs
│   ├── tool_calls
│   ├── changes
│   └── decisions
│
├── evidence
│   ├── tests
│   ├── diffs
│   ├── queries
│   ├── screenshots
│   ├── logs
│   └── validation
│
└── verdict
    ├── PASS
    ├── FAIL
    ├── UNMEASURABLE
    └── NOT_RUN
```

The crucial conceptual change is:

Agents perform work. The factory determines whether the work is correct.

That is much more valuable than another coding-agent wrapper.

3. The Factory Digital Twin

This could make the UI spectacular and genuinely useful.

Imagine opening the Factory and seeing:

```
                         ACME CORP
                            │
             ┌──────────────┴─────────────┐
             │                            │
          Projects                    Knowledge
             │                            │
       Connector-183                Client / ACME
             │
       ┌─────┴───────┐
       │             │
    Mission #91   Mission #94
       │
 ┌─────┼──────────┐
 │     │          │
Scout Builder   Verifier
 │     │          │
API   GitHub   Snowflake
 │     │          │
 └─────┼──────────┘
       │
    Evidence
       │
     PASS
```

Click any node.

You see:

current activity
task
owner
model
context
tools
upstream/downstream dependencies
state transitions
token usage
cost
duration
historical reliability
evidence
outputs
permissions
memory retrieved
errors
similar previous executions

OpenTelemetry's GenAI conventions are increasingly making model/agent/tool span instrumentation portable, including model IDs, token consumption, latency and tool execution information.

So I would build your visual model on top of trace/event primitives rather than inventing telemetry exclusively for the UI.

4. The Agent Time Machine

This is where it starts feeling futuristic.

You open a failed execution:

```
10:31 Research
10:34 API inspected
10:39 Plan produced
10:44 Code modified
10:48 Tests failed
10:51 Agent changed strategy
10:57 Validation failed
```

Click:

10:39 — Fork execution

Then choose:

```
Original
Claude X
Toolset V4
Planner V7

          VS

Experiment
GPT X
Toolset V5
Planner V9
```

Run both.

Factory reports:

```
                Original      Branch
Success           71%          94%
Time              19m          11m
Cost              $3.84        $2.91
Tool calls         41           27
Retries             7            1
Evidence          8/12         12/12
```

Now debugging an agent becomes experimental science.

5. Organizational Evolution

This is probably the deepest concept.

Don't optimize merely:

prompt
model
temperature

Optimize the organization.

For example:

```
Team 184

Planner
  ├── API Researcher
  ├── Repo Researcher
  └── Context Researcher

Implementation Lead
  ├── Backend Agent
  ├── Test Agent
  └── Migration Agent

Verification Lead
  ├── Data Validator
  ├── Contract Validator
  └── Regression Validator
```

The Factory measures Team 184 against Team 183.

Eventually you have:

```
Team                   Success     Cost     Human help
────────────────────────────────────────────────────────
connector-team-v12       71%       $7.40       28%
connector-team-v19       84%       $5.10       14%
connector-team-v31       96%       $3.80        3%
```

And therefore:

You don't just accumulate code.

You accumulate better ways of organizing intelligence.

That is a seriously interesting moat.

One feature I think could become your signature

Call it something like:

Forge

or

Genesis Engine

or

Organization Compiler

User types:

"The HubSpot connector stopped ingesting contacts for Client A after Wednesday. Diagnose it, fix it, validate historical data, make sure it can't regress and document what happened."

Factory responds visually:

```
UNDERSTANDING MISSION...

Detected domains
● Client context
● HubSpot API
● Data engineering
● Python
● Orchestration
● Warehouse validation
● Regression testing

Generating organization...

                        COMMANDER
                           │
              ┌────────────┼─────────────┐
              │            │             │
           RESEARCH      BUILD        VERIFY
              │            │             │
       ┌──────┼─────┐      │      ┌──────┼──────┐
       ▼      ▼     ▼      ▼      ▼      ▼      ▼
     API    Logs   Wiki   Code   Source Warehouse E2E
```

Then:

"Estimated 7 agents / 11 tools / 4 verification gates / 18 minutes / $4.20."

You hit:

DEPLOY TEAM

And watch the organization come alive.

That is enormously more compelling than:

"Start agent."

The closed loop is the actual product

I'd structure the entire Factory around:

```
┌──────────────┐
│  UNDERSTAND  │
└──────┬───────┘
       ▼
┌──────────────┐
│     FORM     │
│ organization │
└──────┬───────┘
       ▼
┌──────────────┐
│   SIMULATE   │
└──────┬───────┘
       ▼
┌──────────────┐
│   EXECUTE    │
└──────┬───────┘
       ▼
┌──────────────┐
│    VERIFY    │
└──────┬───────┘
       ▼
┌──────────────┐
│    LEARN     │
└──────┬───────┘
       ▼
┌──────────────┐
│   EVOLVE     │
└──────┬───────┘
       │
       └──────────────► next mission
```

That final EVOLVE step is what most systems are missing.

LangGraph, CrewAI, provider SDKs and similar systems can provide execution primitives. MCP can provide tool interoperability. A2A can provide agent interoperability. OpenTelemetry can provide standardized telemetry.

Agent Factory can own the layer above all of them:

## VERBATIM RESPONSE ENDS

*(The response ends mid-sentence after the colon. Nothing has been added, completed or trimmed.)*
