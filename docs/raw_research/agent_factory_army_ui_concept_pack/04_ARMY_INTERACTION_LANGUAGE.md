# Army Interaction Language

## Core terminology

| Domain term | World term | Meaning |
|---|---|---|
| portfolio | strategic command | company-wide operations |
| domain | theatre | coherent operational area |
| project | campaign | set of related operations |
| mission | operation | bounded objective with success criteria |
| task | objective | desired state / subgoal |
| agent team | squad | small execution group |
| multi-team | task force | dynamically assembled cross-specialty unit |
| team topology | formation | reusable execution arrangement |
| unknown | fog | uncertainty / missing evidence |
| context/tools/access | supply | execution prerequisites |
| communication | signals/radio | typed org communication |
| knowledge | intelligence | relevant evidence / context |
| approval | command authorization | governed action gate |
| permission/autonomy | rules of engagement | action authority |
| monitoring | surveillance | health / anomaly view |
| evaluation | training range / war game | controlled comparison |
| retrospective | after-action review | learning extraction |
| reusable pattern | doctrine | validated operational pattern |
| historical failure family | known threat | recurring failure pattern |

## Suggested shortcuts

- `SPACE` — Strike Command
- `T` — Target Lock
- `V` — Surveillance View
- `R` — Replay
- `I` — Intelligence Drop
- `F` — Formation
- `G` — Go To
- `/` — Ask Command

## Principle

World terminology is allowed to be playful, but backend/API names should stay clear and conventional. The visual layer may say **Operation**, while the domain model can continue using `mission_id` if that is already established.
