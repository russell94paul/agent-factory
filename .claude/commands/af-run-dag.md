---
description: Agent Factory — start every policy-allowed READY node in a run, within concurrency and conflict bounds.
---
Run id: $ARGUMENTS

```
python -m factory.autonomy plan --run $ARGUMENTS
```

Show the plan first. Then start it through the pump, which is the only thing that may act:

```
python -c "import sys;sys.path.insert(0,'scripts');import local_tracker as lt;print(lt.run_control('$ARGUMENTS','dag')[1])"
```

⛔ Each start opens a real terminal running a real agent. Report exactly which nodes started and
which were refused, with the refusal text. Never re-run this to "retry" a failed start — a failure
is recorded on the mandate deliberately and is cleared by
`python -m factory.autonomy clear-failure --run <run> --work <id>`.

After it returns, the run continues on its own: it wakes on APPROVE/REJECT, on RESUME, and once
per Switchboard page load. Do not ask for a new command per node.
