# R07 — Evaluation, Certification & Green Contracts


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

Design outcome-based evaluation for agents, teams and organizations, especially real software/data-platform tasks, while preventing false success and self-evaluation capture.

## Questions

- Positive GREEN assertions and RED→GREEN methodology?
- Private eval-set construction from historical failures/known-good fixes?
- Hidden/frozen/out-of-sample separation?
- Activity vs outcome metrics?
- Team credit/seam attribution?
- Evaluator independence and grader disagreement?
- Regression/re-certification rules after prompt/model/tool/skill changes?
- Leading indicators of degradation?
