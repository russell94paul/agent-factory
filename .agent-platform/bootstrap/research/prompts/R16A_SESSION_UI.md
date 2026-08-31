# R16A — Session UI & Parallel AI Work Operations


## Required method

- Prefer primary/official/peer-reviewed sources and source code over marketing summaries.
- Separate measured evidence, documented implementation practice, architectural inference, hypothesis, and speculation.
- Find failure cases and negative results, not only success stories.
- Assume the preferred Agent Factory architecture may be unnecessarily complicated; identify simpler alternatives.
- Identify what existed before the LLM era and what materially changes now.
- Where relevant, inspect open-source implementations rather than only papers/blogs.
- Do not recommend a new service/protocol/agent layer unless a real requirement justifies it.

## Required outputs

1. Executive finding
2. Prior-art map
3. Current implementations / systems
4. What works / what fails
5. Constraints and failure modes
6. Architecture implications for Agent Factory
7. `ADOPT | ADAPT | RESEARCH | REJECT` table
8. Minimum viable experiment(s)
9. Falsification conditions
10. Open questions
11. Source list with source-quality notes


## Objective

Design the earliest operator console that materially accelerates managing multiple Claude/research/build workstreams.

## Questions

- What does an operator need beyond terminal multiplexers/task managers?
- Which states/events can be truthfully shown?
- How should blocked/awaiting-human/review/failed states surface?
- Reply/resume/pause/cancel semantics?
- Artifact inspection and Synthesis Inbox patterns?
- DAG/dependency visualization without turning the UI into a graph-editor product?
- How do Paperclip and similar systems solve persistent tasks, sessions, approvals, work products and scanning?
- What is achievable quickly using the current Agent Factory UI/runtime constraints?

## Output requirement

Provide an MVP information architecture, event/data contract, wireframe-level layout and an implementation sequence that can ship early without locking the final Mission Control design.
