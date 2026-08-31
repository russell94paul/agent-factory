# RREF2 — Super Simple Software Factory: Pattern Mining, Not Cloning

## Objective
Study `https://github.com/disler/super-simple-software-factory` as a reference implementation for agentic software-factory mechanics. Extract concepts, invariants, workflow patterns, observability ideas, and failure-handling techniques that could accelerate Agent Factory. Do **not** copy product identity, UI, branding, or implementation wholesale.

## Why it matters
This reference appears to implement several problems Agent Factory is already solving or planning to solve: deterministic orchestration around bounded coding-agent phases, typed cross-phase handoff, acceptance gates, per-agent configuration, trace storage, resumable corrections, and a skill that can stamp reusable factory machinery into a repo.

## Required questions
1. Which problems overlap materially with the current Agent Factory?
2. Which patterns are already implemented better in Agent Factory and should be ignored here?
3. Which patterns are simpler than our current/proposed design and should challenge our assumptions?
4. How does deterministic code own sequencing, retries, gates, and acceptance?
5. How are agent phases distinguished from deterministic/code phases?
6. How are structured envelopes used at seams, and where would our event/evidence contracts need to go beyond them?
7. How are read/write boundaries enforced for agents?
8. How are retries/corrections handled without throwing away useful session state?
9. How are models/prompts/tools/harnesses configured and varied per role/phase?
10. How is observability structured, and what could inform our Session Console and Organizational Debugger?
11. What does the “skill stamps the factory into a repo” pattern teach us about our bootstrap-commander and reusable skill architecture?
12. Which concepts should be classified `ADOPT CONCEPT | ADAPT | EXPERIMENT | REJECT`?

## Special comparison targets
Compare against these Agent Factory principles:
- deterministic policy enforcement;
- positive GREEN assertions;
- versioned behavioral artifacts;
- Prefect as current run plane;
- Claude Code agents/seats;
- mission-level context and future shared cognition;
- future dynamic team/organization assembly.

## Required falsification
Actively search for cases where the reference's simpler architecture is sufficient and our proposed architecture is unnecessary. Also identify cases where its linear/phase-oriented model would break down for swarms, cross-team knowledge, long-running missions, event-driven communication, or multi-organization behavior.

## Do not copy
- product branding or naming;
- visual design or layouts verbatim;
- prompts verbatim;
- code wholesale;
- terminology merely because it is convenient.

If a code-level technique is materially useful, describe the pattern and provenance rather than copying implementation text.

## Required outputs
- `SUMMARY.md`
- `PATTERN_MATRIX.md`
- `AGENT_FACTORY_COMPARISON.md`
- `SIMPLIFICATION_CHALLENGES.md`
- `EXPERIMENT_CANDIDATES.md`
- `ARCHITECTURE_DELTAS.md`

Every pattern must be labeled with one of:
`ADOPT_CONCEPT | ADAPT | EXPERIMENT | REJECT`
