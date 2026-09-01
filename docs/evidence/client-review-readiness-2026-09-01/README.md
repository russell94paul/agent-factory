# Client Review readiness — evidence, 2026-09-01

Measured by the Client Review readiness session. Observation boundary:

```text
HEAD        10c4fe7  (main, clean at session start)
worktree    C:/Users/PaulRussell/repos/agent-factory  (main checkout)
task store  .data/tasks.jsonl — 241 events, D4 closed and D5 claimed at 2026-09-01 00:23:21
mission     .data/missions/marketing-model-reconstruction-v1.json
measured_at 2026-09-01 ~07:20–08:45 UTC
```

⚠ `.data/` is shared and MAIN T was writing to it throughout. Every conclusion below is tied to the
event boundary above; a later close changes the numbers and is *supposed* to.

---

## 1. The finding: ten typed statuses contradicted the record

`narrative-drift.json` in this directory is the raw measurement, taken **before** any fix, by
linking each narrative plan item to the mission's own `labels` map and comparing.

| item | narrative said | record said |
|---|---|---|
| next N-1 → R3 | `BLOCKED` | `DONE` |
| next N-2 → D1 | `NOT_STARTED` | `DONE` |
| next N-3 → D2 | `NOT_STARTED` | `DONE` |
| next N-4 → D3 | `NOT_STARTED` | `DONE` |
| next N-5 → D4 | `NOT_STARTED` | `DONE` |
| next N-6 → D5 | `NOT_STARTED` | `IN_PROGRESS` |
| milestone "Map the available marketing data" | `BLOCKED` | `DONE` |
| milestone "Synthesise requirements" | `NOT_STARTED` | `DONE` |
| milestone "Candidate designs and skeptical review" | `NOT_STARTED` | `DONE` |
| milestone "Recommendation and sign-off" | `NOT_STARTED` | `IN_PROGRESS` |

Basis **MEASURED** — produced by `factory.client_review.resolve_plan_status` against the live
store, not read from a document.

**Client impact had this shipped:** the artifact would have told GEP that the data-cartography
work was *blocked* and that no design work had started, on a day when all of it was closed with
evidence. It would also have carried a risk (`RISK-2`) asking for patience on a pause that had
ended, and a "what happens next" list of six items of which five were already done.

**Why it was invisible:** the compiler read the store for *evidence grounding* and the yaml for
*status*. Both halves worked. Nothing compared them.

### The fix, and why it cannot recur in this shape

The typed statuses were **deleted**, not corrected. Plan items now carry `task:` links resolved
against the mission record, so status, evidence paths, milestone state and risk state are all
DERIVED. There is nothing left to type wrong. The drift check remains live as a guard for anything
a future contributor hand-types, and has both a firing test and a negative control.

---

## 2. Second finding: the D2–D5 evidence is not readable from `main`

```text
docs/evidence/marketing-model-v1/            (main checkout)  R1 R2 R3 D1
.worktrees/mission/docs/evidence/marketing-model-v1/          R1 R2 R3 D1 D2 D3 D4 D5
```

Seven cited artefacts do not resolve from `main`, so four outcomes ground as `CLAIMED` rather than
`VERIFIED`. Basis **MEASURED** (`ls` on both paths; gate output reproduced below).

⛔ **Superseded by operator decision, same day.** This paragraph originally said the fix was for
MAIN T to merge `mission/marketing-model-v1`. That was wrong and is corrected here rather than
only in §8: the branch carries client-identifying and commercially sensitive evidence and is **not
approved for merge or push** to make a projection convenient.

`--root .worktrees/mission` is therefore **the supported delivery path, not a fallback** — a
read-only read of isolated canonical state, from which only the allow-listed projection crosses
into the artifact. Executed, and it clears this check. See `06-D5-REFRESH-CONTRACT.md`.

---

## 3. Third finding: LECTRIC is de-scoped in D4 and in-scope on the client page

`.worktrees/mission/docs/evidence/marketing-model-v1/D4-descope-and-decode.md`, measured
2026-09-01 07:06 UTC, records:

```text
LECTRIC   TARGET SCOPE   CONFIRMED DE-SCOPED
```

The Client Review's `intent.assumptions` still tells the client *"Navira (HOUSE) and Lectric
(AGENCY, sales-only, no ad spend) are the two entities in scope."*

Basis of this observation: **DOCUMENTED** — read from one file in another session's worktree, one
hop from measurement, and that worktree is mutable.

**Flagged as `WAIT FOR D5`, then resolved by operator authority the same day.** LECTRIC is not
part of target-state scope. The Client Review representation was updated — and only the
representation; D4's evidence was not touched and the LECTRIC metric path was not repaired.
LECTRIC moved from `intent.assumptions` (in scope) to `intent.exclusions`, using the contract's
existing field rather than a new status constant, because the repository has none
(`grep -rn 'DE_SCOPED\|de-scoped' factory/` → no matches). The un-verified half is carried
explicitly in `unresolved_ambiguities`: excluding it from a design is not removing it from a
running system, and removal ordering and dangling consumers are stated as **not verified**. The
three rendered sentences are quoted in §8.

---

## 4. Rendered validation — RENDERED_CONFIRMED

`render-check-client-review.json` and 13 screenshots in this directory. Executed, not inferred:

```text
3 widths (760 / 1100 / 1440) x 2 colour schemes x 2 modes (standard / Live Meeting) = 12 loads
  8 sections painted in every one          0 blank
  0 clipped headings                        0 horizontal overflow
  0 console errors                          0 failed requests
  0 operator-only strings in innerText      0 offsite requests (1 request total, file:)
  meeting-mode button click                 works
  7 nav links                               0 dangling, 0 headings occluded on click
  JavaScript disabled                       8 sections, 9 <details>, 13,260 chars of text
```

The nav-occlusion check exists because a section screenshot taken with `scrollIntoView` *appeared*
to show the lede under the sticky rail. Driving the page's own navigation instead showed every
heading landing clear at 112px against a 50px rail. The apparent defect was in the measuring
instrument. That is now a check rather than a memory.

---

## 5. Gate output at the observation boundary

```text
MEETING GATE  NOT_READY
  ok    canonical_state_readable           task store read; 101 evidence row(s)
  ok    freshness                          LAST_VERIFIED (verified 2026-09-01 07:23 UTC)
  ok    narrative_matches_canonical_state  no typed status contradicts the record
BLOCK   completed_work_is_written_up       5 outcome(s) render as awaiting write-up
BLOCK   cited_evidence_resolves            7 cited artefact(s) not on disk in this checkout
  ok    no_status_rendered_without_a_basis every plan status is DERIVED from the task store
  ok    no_unsubstantiated_claim           no claim degraded
  ok    required_sections_populated        9 outcome(s), 2 evidence, 2 decisions, 6 next
  ok    client_boundary_holds              allow-list projection and backstop scan both pass
 warn   mission_record_integrity           8 declared vs 10 observed children
 warn   risks_still_current                RISK-2 shown as resolved from the record
```

With `--root .worktrees/mission`, `cited_evidence_resolves` passes and only
`completed_work_is_written_up` blocks.

---

## 5b. D5 closed mid-session, and the simulation below became a measurement

**Measured 2026-09-01 01:51:35** — MAIN T closed D5 while this session was running. The
simulation in §6 was written before that and is left as written; it predicted the behaviour, and
the real close then produced it. Re-grounded state at the end of the session:

```text
D5                   done                    (was: claimed)
next N-6             DONE, basis DERIVED     (was: IN_PROGRESS)
gate, --root worktree  NOT_READY, ONE blocker: 6 outcomes awaiting write-up
```

### A malformed evidence ref, found by the gate

D5's close carried four evidence rows. One of them is:

```text
ref    docs/evidence/marketing-model-v1/D5-recommendation.md (see 0a - sign-off and its limits)
basis  ASSUMED
```

A path with prose appended. It can never resolve as a filesystem path, and it produced a gate
blocker on an outcome that was otherwise fine — the *same file* is cited separately at basis
`DERIVED` with a clean path.

**Resolved in Client Review, correctly rather than defensively.** Derived evidence lists now take
only rows whose basis is in `evidence.USABLE` (`MEASURED` / `DERIVED`). An `ASSUMED` row is not
proof, so it never belonged behind a client-facing "Proof it works" disclosure regardless of
whether its path resolved. The blocker disappeared as a side effect of the right rule, not by
special-casing the string. Test + negative control:
`test_a_derived_evidence_list_takes_only_rows_with_a_usable_basis`.

⛔ **The row itself is not repaired here** — the task store is the mission's. Flagged to MAIN T.

---

## 6. The refresh contract's central claim, executed rather than asserted

The claim is *"when D5 closes, the artifact updates with no edit to the narrative."* That was
tested by copying the live store into the scratchpad, appending a D5 evidence row and close event,
and re-assembling against the **unmodified** yaml. Basis **MEASURED**.

```text
                          before D5 closes        after (simulated close, no yaml edit)
next N-6 (Recommendation)  IN_PROGRESS  DERIVED    DONE  DERIVED
milestone "Recommendation
  and sign-off"            IN_PROGRESS             DONE
completion_percent         88  DERIVED             100  DERIVED
acceptance                 NOT_READY               READY_FOR_REVIEW
gate                       NOT_READY               NOT_READY  (write-ups only)
```

The remaining blocker after a real D5 close is the same single one: six closed tasks
(R3, D1–D5) whose client-facing meaning nobody has written. Nothing else needs a human.

⚠ The simulation wrote only to the scratchpad. `.data/tasks.jsonl` was not modified.

---

## 7. Vocabulary note — what the contract can and cannot express

The readiness brief asked for `MEASURED / DOCUMENTED / DERIVED / UNVERIFIED / CONTRADICTORY /
NOT_RECORDED / DE_SCOPED`. Measured against `factory/assertions.py`:

| asked for | in the repo? |
|---|---|
| MEASURED, DERIVED, DOCUMENTED, NOT_RECORDED, CONTRADICTORY | **yes** — `assertions.BASES`, used as-is |
| UNVERIFIED | no such constant. The repo expresses it as `NOT_RECORDED` for a plan status and `CLAIMED` / `UNGROUNDED` for a claim's grounding. Both used; nothing invented |
| DE_SCOPED | ⛔ **absent from the repo entirely** (`grep -rn 'DE_SCOPED\|de-scoped' factory/ tests/ scripts/` → no hits in code). Not added, per the brief's own instruction not to invent status types. This is why finding 3 above is a flag and not a rendered state |

---

## 8. Closing state — the gate cleared, and the chain worked end to end

**Measured 2026-09-01 09:00 UTC, `main @ 1068f59`, root `.worktrees/mission`.**

MAIN T closed D5 and then supplied the six outcome write-ups through the boundary this session
prepared — `delivered:` entries carrying `task:` links, **no hand-typed `status:`, no
`evidence_refs:`** (committed by that session as `0a8b593`). Nothing was copy-pasted between
sessions and no analytical prose was restated.

```text
MEETING GATE  READY_WITH_WARNINGS
  ok    canonical_state_readable            task store read; 110 evidence row(s)
  ok    freshness                           LIVE (verified 2026-09-01 09:00 UTC)
  ok    narrative_matches_canonical_state   no typed status contradicts the record
  ok    completed_work_is_written_up        every completed task is written up
  ok    no_status_rendered_without_a_basis  every plan status is DERIVED from the task store
  ok    cited_evidence_resolves             every cited artefact resolves on disk
  ok    no_unsubstantiated_claim            no claim degraded
  ok    required_sections_populated         10 outcomes, 2 evidence, 2 decisions, 6 next
  ok    client_boundary_holds               allow-list projection and backstop scan both pass
 warn   mission_record_integrity            8 declared vs 10 observed children
 warn   risks_still_current                 RISK-2 shown as resolved from the record

RENDER   RENDERED_CONFIRMED          meeting_ready exit 0 · render_check exit 0
```

**SAFE TO OPEN IN FRONT OF THE CLIENT**, with two presenter notes, neither of which is a defect.

### One test had to be corrected, and the correction is the interesting part

`test_the_navira_review_assembles_and_renders` grounded the real narrative against *this*
checkout. Under the operator decision that the mission branch stays isolated, that asserted a
state the approved architecture guarantees will never hold. It passed only while the narrative
happened to cite R1/R2 evidence alone, and failed the moment the D-task write-ups landed — a
green test that was green for the wrong reason. Corrected in `1068f59` to build from the same
root the artifact is built from.

### LECTRIC, as rendered to the client

Three statements, verified by reading the built page's `innerText`:

```text
· not part of the target-state model; exists in the estate today and in the historical record;
  this phase does not remove it. Historical values are not carried forward.
· its known metric defect is NOT a repair requirement and no fix is proposed or costed.
· removal ordering and dangling consumers have NOT been verified, and that is not claimed as done.
```

---

## Reproduce everything here

```bash
python scripts/meeting_ready.py --root .worktrees/mission   # compile + render + gate + browser
python scripts/render_check_client_review.py          # the browser pass alone
python -m pytest tests/test_client_review.py tests/test_client_review_readiness.py
```
