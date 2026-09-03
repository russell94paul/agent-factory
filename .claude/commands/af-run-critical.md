---
description: Agent Factory — start only the policy-allowed READY ancestors of a target milestone; leave unrelated work alone.
---
Target milestone: $ARGUMENTS

Find the run whose target this is (`python -m factory.autonomy status`), then:

```
python -c "import sys;sys.path.insert(0,'scripts');import local_tracker as lt;print(lt.run_control('<run-id>','critical')[1])"
```

Selection is the ancestor closure of the target over the TASK dependency graph — not
`board.DEPENDS`, which is a different graph at a different scale (platform readiness gates).

⛔ Unrelated work is DEPRIORITISED, never dropped. If you find yourself wanting to abandon a node
to make the target reachable, stop: automatic scope degradation is deliberately absent, and
skipping a required node needs a human decision with provenance.
