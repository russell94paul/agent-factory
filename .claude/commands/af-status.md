---
description: Agent Factory — goal, target, deadline, READY/RUNNING/GATE/BLOCKED counts, critical path, and what the planner would do next.
---
Run this and report the output verbatim, then say in one line what the operator's next act is:

```
python -m factory.autonomy status
```

It prints, per run: mode, target, deadline (scheduling context only — it never changes what PASS
means), concurrency usage, and a reason for every candidate. Do not summarise a count you did not
read from the output.

If it reports no runs, say so and offer `/af-run-dag` after a mission is created — do not invent a
run id.
