# Product Vision & UI Layers

## North-star interaction thesis

The interface should not be a dashboard that happens to contain agents. It should be an **IDE for directing an artificial organization**.

### Traditional IDE

`file → code → build → test`

### Current AI IDE

`prompt → agent → code → review`

### Agent Factory / Army model

`intent → mission compiler → organization → coordinated execution → evaluation → learning → evolution`

## Two UI projections

### 1. Command Console — primary

Build first. Dense, precise, engineer-first.

Must support:

- mission creation and launch
- team / agent configuration
- execution graph
- progress and blockers
- handoffs and communication
- context and evidence
- artifacts and diffs
- approvals / authority
- costs and budgets
- evals / GREEN criteria
- replay and causal debugging
- organization changes

### 2. Battlefield View — secondary

Animated, spatial and highly gamified. It should be **faster for awareness and coordination**, not replace code/log/table-heavy tasks.

Best-fit responsibilities:

- portfolio / theatre awareness
- priority and frontline visualization
- anomaly spotting
- team topology
- communications
- context/logistics health
- reinforcement and redeployment
- organizational bottlenecks
- remote presence and culture

## The world is a projection, not the source of truth

```text
                 SHARED DOMAIN / EVENT STATE
                           │
               ┌───────────┴───────────┐
               │                       │
         COMMAND CONSOLE          BATTLEFIELD VIEW
         dense / precise          spatial / ambient
               │                       │
               └────── TYPED COMMANDS ─┘
                           │
                    governance / RBAC
```

## Design success criterion

A gamified interaction should be retained only if it:

- reduces operator time,
- reduces context switching,
- improves situation awareness,
- improves coordination,
- reduces missed risks,
- improves engagement without Goodhart incentives,
- or exposes a genuinely new capability.

The world should lose to a traditional UI whenever precision, dense comparison, long text, code, SQL or detailed configuration is better served conventionally.
