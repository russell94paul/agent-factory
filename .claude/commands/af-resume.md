---
description: Agent Factory — clear an operator pause, recompute, and start newly eligible work.
---
Run id: $ARGUMENTS

```
python -c "import sys;sys.path.insert(0,'scripts');import local_tracker as lt;print(lt.run_control('$ARGUMENTS','resume')[1])"
```

This clears the pause AND pumps, because a resume that only records a flag leaves the operator
pressing a second button for the thing they just asked for.

(`python -m factory.autonomy resume --run <id>` clears the flag without starting anything — use
that when you want to unpause but not act.)
