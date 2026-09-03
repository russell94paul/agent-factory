---
description: Agent Factory — persist an operator pause on a run. Running work may finish; nothing new starts.
---
Run id: $ARGUMENTS

```
python -m factory.autonomy pause --run $ARGUMENTS
```

PAUSE is unconditional and always available — a stop that could be refused because of the state it
is trying to stop would not be a stop. It cancels nothing that is already running; it only stops
new starts. Say both of those things when you report it.
