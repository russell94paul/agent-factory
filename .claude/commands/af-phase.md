---
description: Agent Factory — manual recovery. Start one specific node through the normal start mechanism.
---
Work id: $ARGUMENTS

```
python -c "import sys;sys.path.insert(0,'scripts');import local_tracker as lt;print(lt.start_synced(target='$ARGUMENTS', note='manual recovery via /af-phase')[1])"
```

⛔ **This is an entry point into the DAG, not a source of sequencing truth.** It does not redefine
dependencies, does not mark anything satisfied, and does not skip a gate: `start_synced` resolves
the target canonically and refuses anything that is not READY. If it refuses, the answer is in the
refusal — fix the condition, do not route around it.

Use it when a run has stalled on one node and you want that node started under your own authority
rather than the policy's. An operator's explicit tap is allowed to start GUARDED or MANUAL work;
that is why the mechanism does not consult the autonomy policy.
