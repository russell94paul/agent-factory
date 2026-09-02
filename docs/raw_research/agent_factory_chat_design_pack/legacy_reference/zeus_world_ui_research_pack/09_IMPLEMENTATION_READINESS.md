# 09 — Implementation Readiness Gates

The world should not move into a full build just because the concept is exciting.

## Gate 1 — Primary dense Mission Console exists

The product must already expose the operational truth needed to answer:

- what is running?
- what is blocked?
- why?
- what is waiting on me?
- what evidence exists?
- what changed?
- what did it cost?
- can I intervene/replay?

Reason: the world needs a trustworthy state model to project.

## Gate 2 — Event/state taxonomy is stable enough

At minimum, mission/team/agent/blocker/gate/context/evidence/eval events must exist or be derivable reliably.

## Gate 3 — 10–20 benchmark traces exist

Use real completed and failed missions. The first world prototype should run entirely from replay.

## Gate 4 — Three world interactions beat baseline

Recommended first candidates:

1. ZEUS Satellite anomaly scan.
2. Reinforcement routing/direct deployment.
3. Logistics/readiness diagnosis.

If these do not beat the dense UI, do not assume more animation will fix the problem.

## Gate 5 — Formation compiler proves representational value

Show that at least several recurring team topologies can be configured faster with no loss of explicitness.

## Gate 6 — Accessibility/keyboard equivalence

Every critical command has a non-spatial route:

```text
/zeus blockers
/zeus go M-184
/zeus reinforce M-184
/zeus approvals
/zeus replay M-184
```

Reduced-motion mode must preserve operational content.

## Gate 7 — No Goodhart reward loop

Game rewards are reviewed against bad incentives before social rollout.

## Gate 8 — Social/presence privacy rules

World presence must not accidentally reveal:

- sensitive client context;
- confidential mission names;
- employee performance judgments;
- private agent conversations;
- inactivity as a proxy for employee performance.

## Gate 9 — Technical spike completed

Choose renderer only after comparable prototypes.

## Gate 10 — World and dense UI share the same command/state contracts

No separate “game backend” for operational truth.

---

# Recommended research order

## Wave A — Prove speed
1. RUX-11 World vs Dense UI benchmark.
2. RUX-04 ecological/situation awareness.
3. RUX-02 semantic zoom.
4. Prototype Satellite + target-lock + exact drilldown.

## Wave B — Prove agentic advantage
5. RUX-01 human-swarm command grammar.
6. RUX-03 mixed initiative.
7. RUX-07 formation discovery.
8. Prototype reinforcement + formation compiler.

## Wave C — Prove compounding value
9. RUX-05 cognitive logistics.
10. RUX-06 communication compression.
11. RUX-09 ghost/replay.
12. RUX-10 Intelligence Command.

## Wave D — Add the world/culture layer
13. RUX-08 gamification.
14. RUX-12 accessibility/low-motion.
15. social presence prototype.

---

# Initial BUILD / RESEARCH / DEFER recommendation

## BUILD FIRST (after baseline Mission Console)
- Satellite/anomalies-only view.
- Target-lock + command palette.
- Reinforcement router.
- Command authorization post.
- After-action replay/AAR.

## PROTOTYPE EARLY
- semantic zoom;
- logistics visualization;
- formations;
- fog/uncertainty;
- collision control.

## RESEARCH DEEPLY
- adaptive battlefield layout;
- ghost battalion;
- intent painting;
- counterfactual futures;
- autonomous staff officer;
- autonomous Intelligence Command opportunity selection.

## DEFER UNTIL OPERATIONAL VALUE EXISTS
- full avatar world;
- social buildings;
- cosmetics;
- ranks/collectibles;
- large multiplayer world events.

The social layer can be excellent, but it should arrive on top of a command model already proven faster than ordinary enterprise UI.
