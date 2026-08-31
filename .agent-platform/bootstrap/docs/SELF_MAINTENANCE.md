# Self-Maintenance as a First-Class Goal

The platform should eventually help observe, diagnose, repair, upgrade, validate, and roll back:

- agents/prompts/skills;
- knowledge/retrieval;
- schemas;
- workflows/evals;
- integrations;
- services/dependencies;
- infrastructure;
- documentation;
- organization presets.

Governed loop:

```text
OBSERVE
→ DIAGNOSE
→ MAINTENANCE INTENT
→ CONSTRUCT MAINTENANCE ORGANIZATION
→ PROPOSE REPAIR
→ TEST/SIMULATE
→ VERIFY
→ HUMAN/POLICY GATE
→ CANARY
→ DEPLOY
→ OBSERVE
→ ROLLBACK IF REQUIRED
→ LEARN
```

Self-maintenance is an L6 capability, not a reason to grant broad self-modification to L1-L3 agents.
