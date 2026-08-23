# Sessions board — evidence

A handoff that lives only in a terminal has not been handed anywhere. This adds a **card**
that outlives the session, carries a **title and a description** so a reader knows what it is
about without opening it, and states what must run before it.

`python -m factory.sessions` · `python -m factory.sessions --cards` · tracker `/sessions`

## ⚠ Where this is posted, and who sees it

**localhost only.** Paul chose the local tracker over Jira, the Zeus board or a published
artifact. That is a deliberate choice and it is recorded here because it bounds the claim:
*"so people know what it's about"* is satisfied for anyone at this machine and for a future
session reading the store, and for nobody else. `.data/cards.jsonl` is gitignored, so a card
does not travel with the repo either.

## Three constraints, deliberately not merged

Running order is not one relation, and collapsing them is how a board asserts an order it
cannot justify.

| relation | meaning | derived from | basis |
|---|---|---|---|
| `after` | this session's gates depend on gates another owns | `board.DEPENDS` | MEASURED |
| `blocked_by_gate` | depends on a gate **no session owns** — no ordering fixes it | `board.DEPENDS` | MEASURED |
| `conflicts` | two sessions edit the same file — cannot run *concurrently* | `lanes.Lane.touches` | ⚠ ASSUMED |

⭐ **`conflicts` is not ordering.** Either order is fine; both at once is a merge conflict. A
reader who treats one as a dependency waits for something that was never going to unblock.

## ⛔ The headline finding: there is no ordering

Projecting `DEPENDS` onto lanes yields **no lane-to-lane edge at all**. Every authored
dependency is either inside one lane (`truthful`←`from-history`, both control-plane) or points
at a gate no lane owns (`certified`←`isolated`). So the board **says so**, in red, rather than
rendering name order as a sequence — `running_order()` always returns waves, and a reader
cannot tell a derived order from an alphabetical one unless the page tells them.

That is measured, not a gap in the projection. As `DEPENDS` grows the edges appear here with
nothing re-typed, which is the point of deriving rather than declaring.

## What it did find

- **`certify` is blocked by `isolated`, which no session owns.** Not a scheduling problem —
  nobody is assigned to it.
- **Two file collisions.** `control-plane ↔ judgement` on `orchestrator/pipelines.py` was
  already in the boot prompt. **`certify ↔ grain` on `factory/connector_contract.py` was
  written down nowhere** — same hazard, discovered by computing it.
- **12 gates belong to no session**, so running every lane on the board still leaves them.

## Validated at the rendered layer, not the response body

`curl | grep` proves bytes are in the response. `scripts/sessions_render_probe.py` drives real
Chromium and asks the DOM:

```
http://127.0.0.1:8099/sessions — HTTP 200, 6 card(s) painted
  [session] 1056x146  5 block(s)  Run impeccable at the readout
  [session] 1056x223  8 block(s)  Wire one instrument
  [session] 1056x172  6 block(s)  Bound the loop
  [session] 1056x176  7 block(s)  Settle the landing-table grain
  [session] 1056x172  6 block(s)  Make the gates able to refuse
  [handoff] 1056x96   3 block(s)  Control-plane lane close-out
  banner painted: 1056x72
Every card paints, is on screen, and carries a visible title and description.
```

760px: 6 cards, no horizontal scroll. Screenshots beside this file.

⚠ **Stated limit:** it measures geometry and computed style, not appearance. A card painted
white-on-white would pass every assertion.

### The probe's own defect, found and fixed

Its first run reported **two untitled cards**. They were the *notices* — the tracker's `.card`
class is a generic box and the banners use it too, so the probe had inferred its population
from styling. Cards are now tagged `[data-card]` and the probe selects on that. It also now
**fails on an empty population** rather than reporting green, because an instrument that sees
nothing has not measured zero — finding F34, in an instrument written after F34.

## Refusals, watched

| action | result |
|---|---|
| post with a blank title | `refused: a card needs a title — 'so people know what it's about' is the surface's only job` |
| post with a blank description | `refused: a card needs a description. A title says what it is called; a description says what it is about, and they are not the same` |
| post with an empty body | `refused: a card with no body is a heading` |
| post for an unknown session | refused, and names the sessions that exist |
| a corrupt line in the store | raises — a skipped card is a handoff that stopped existing with nobody told |

## Tests

`tests/test_sessions.py` — 18, including that a cycle **raises** rather than being
linearised, that conflicts never leak into `after`, and that the report keeps its disclaimer
exactly while no edges exist (the assertion flips branch automatically if any are added).

Two defects the tests found before anything shipped:

1. **Cards posted in the same second could not be ordered.** `created` had second precision, so
   a stable sort returned them oldest-first while claiming newest-first. For an append-only log
   the write order *is* the history, so it is now the authority and the clock is the tiebreak.
2. A test asserted a phrase that **wraps across a line** in the rendered report, so it checked a
   pattern that could never match — finding F19, inside a test written to enforce honesty.

## Not done

- **Nothing posts a card automatically.** The checkpoint protocol still writes a boot prompt;
  posting a card is a button a human presses. Wiring `session_handoff` to post on close would
  make the card the default rather than the diligent path.
- **`conflicts` is parsed from prose.** `Lane.touches` is a human sentence, so the first token
  of each comma-separated clause is taken as the path. It finds both real collisions today and
  it is the weakest inference in the module.
- **A card cannot be closed or assigned.** It is a record, not a task — `factory.tasks` is the
  place for state, and the two are not joined.
