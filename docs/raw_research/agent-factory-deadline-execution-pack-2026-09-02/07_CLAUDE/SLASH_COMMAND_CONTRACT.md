# Slash Command Contract

These names are **desired semantics**, not mandatory filenames. Claude should inspect existing commands and preserve compatible names.

| Command | Meaning |
|---|---|
| `/af-status` | Show goal, target, current READY/RUNNING/GATE/BLOCKED counts, critical path, active sessions, next action and fallbacks. |
| `/af-run-dag <run>` | Activate the run and start all policy-allowed READY work within concurrency/conflict bounds. |
| `/af-run-critical <target>` | Activate critical-path mode for a target milestone. |
| `/af-pause <run>` | Persist operator pause; running work may finish, no new work starts. |
| `/af-resume <run>` | Clear pause, recompute, start newly eligible work. |
| `/af-phase <id>` | Manual recovery/targeted entry into a DAG node or phase; it does not redefine dependencies. |
| `/af-retry <work-id>` | Re-attempt only after classifying the prior failure and checking attempt budget. |

## Important

After an explicit RUN command, **the user should not need to type the next phase command** when the next node is ungated and policy allows it. The DAG runner owns continuation.
