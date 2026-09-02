# DR02 — Cognitive Portfolio Theory for Agent/Team Selection

Research whether portfolio theory, ensemble diversity, error covariance, risk parity, robust optimization, and Bayesian model averaging can be transferred into agent/expert composition.

Core hypothesis:

> The best team is not the set of individually best agents. It is the set with the best expected mission utility after accounting for correlated failure, cost, latency, and tail risk.

Investigate:
- measures of error dependence,
- correlation vs mutual information vs copulas,
- diversity measures from ensemble learning,
- Markowitz-style optimization,
- robust portfolio optimization,
- risk parity,
- CVaR optimization,
- Bayesian model averaging,
- mixture-of-experts gating,
- online expert advice,
- contextual bandits.

Design:
1. a mathematical objective for Agent Factory,
2. estimators that work with sparse mission history,
3. methods to avoid unstable covariance estimates,
4. temporal validation under drift,
5. a practical experiment using historical repo tasks,
6. metrics for diversity contribution,
7. failure cases where diversification hurts.

Return pseudocode and a minimal data schema.
