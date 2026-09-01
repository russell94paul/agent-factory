# Client Review — the refresh contract

**Written 2026-09-01 by the Client Review readiness session, against measured state.**
This file answers exactly one question: *when D5 lands, what has to happen before the artifact is
safe to open in front of the client?*

The answer is designed to be as close to nothing as the estate allows.

---

## The one command

```bash
python scripts/meeting_ready.py --root .worktrees/mission --open
```

⛔ **`--root .worktrees/mission` is the supported path, not a workaround.** See
*"The mission branch is not merged, and must not be"* below before changing it.

It does all five steps in order and refuses loudly if any of them is not true:

```text
canonical state → compile → render → gate → rendered validation
```

Exit codes are the contract — `0` safe to open · `1` gate or render refused · `2` no artifact at
all. Add `--open` to open the finished page in a browser.

**There is nothing else to run.** The older three-step sequence in
`05-CLIENT-REVIEW-DEMO-RUNBOOK.md` still works and is still correct; this collapses it.

---

## What MAIN T has to hand over

**Nothing written in prose. Nothing restated. Nothing copy-pasted.**

The Client Review reads `.data/tasks.jsonl` and
`.data/missions/marketing-model-reconstruction-v1.json` directly. Task status, evidence paths,
milestone state, plan state, freshness and completion are all *derived from the record*, not typed
into the narrative. When D5 closes with its evidence, the page changes on the next regeneration
with no yaml edit at all.

Concretely, the handoff is:

```text
1.  close D5 in the task store, with its evidence rows (the normal mission close)
2.  say: "D5 closed, authoritative mission HEAD = <sha>"
3.  regenerate against the approved mission root
```

Step 2 is a sentence, not a document. No analytical prose is copied anywhere.

### This was executed, not assumed

The live store was copied to the scratchpad, D5 was closed in the copy with an evidence row, and
the review was re-assembled against the **unmodified** narrative yaml:

```text
                       before          after a simulated D5 close (no yaml edit)
next N-6                IN_PROGRESS  →  DONE      (basis DERIVED both times)
milestone 6             IN_PROGRESS  →  DONE
completion_percent      88           →  100       (basis DERIVED)
acceptance              NOT_READY    →  READY_FOR_REVIEW
```

Recorded at `docs/evidence/client-review-readiness-2026-09-01/README.md` §6. The real
`.data/tasks.jsonl` was not touched.

## The mission branch is not merged, and must not be

**Operator decision, 2026-09-01.** `mission/marketing-model-v1` is **not approved for merge or
push** in order to make its evidence visible to Client Review. The branch carries
client-identifying and commercially sensitive evidence and stays isolated.

An earlier draft of this contract listed "merge the mission branch" as the preferred step. That
was wrong and is corrected here rather than quietly dropped: **a merge is not a prerequisite, and
requiring one would have widened the audience of sensitive evidence to make a projection
convenient.**

**Measured 2026-09-01.** `docs/evidence/marketing-model-v1/` in the main checkout holds R1, R2, R3
and D1 only. D2, D3, D4 and D5 exist solely in `.worktrees/mission/`. The Client Review resolves
cited evidence against a checkout root, so from `main` those artefacts do not exist and four
outcomes ground as CLAIMED rather than VERIFIED.

The supported delivery path is therefore:

```text
isolated mission canonical + evidence state
        ↓  read-only, --root .worktrees/mission
Client Review compiler
        ↓  allow-list projection  (CLIENT_SAFE, per section)
client-facing artifact
        ↓
rendered validation
```

```bash
python scripts/meeting_ready.py --root .worktrees/mission --open
```

Executed 2026-09-01: the gate's `cited_evidence_resolves` check passes under it, leaving the
write-ups as the single blocker. **Nothing is copied out of the mission branch** — the compiler
reads the evidence to confirm each cited artefact exists and carries a usable basis, and what
crosses into the artifact is the allow-listed projection, never the evidence body.

Two properties of this path are worth stating plainly:

* `--root` is **read-only**. Client Review never writes to the mission worktree.
* The mission worktree is **mutable and owned by another session**, so a result obtained through
  it is only as stable as the worktree at that moment. Regenerate close to the meeting and read
  the freshness stamp, which is exactly what it is for.

### The longer-term interface

The right permanent answer is **not** "merge the branch" and **not** "keep pointing at a live
worktree". It is the smallest safe allow-listed **projection or export of canonical delivery
state** — the task/mission records and the *existence and basis* of each evidence artefact —
published from the isolated branch to somewhere Client Review can read without the evidence
bodies travelling with it.

The allow-list that would govern such an export already exists in
`factory/client_review.py:CLIENT_SAFE`, and `factory/projection.py` already registers and
enforces it. Building the export is not in this session's scope and is not required for the
meeting.

---

## What is still owned by MAIN T after D5

Exactly one thing, and it is the only remaining gate blocker:

```text
BLOCK  completed_work_is_written_up
       5 outcome(s) render as awaiting write-up:
       PENDING-R3, PENDING-D1, PENDING-D2, PENDING-D3, PENDING-D4
```

Five pieces of work are **closed in the record with evidence** and have no client-facing statement
of what they *mean*. The Client Review will not write one — a conclusion about the Navira model is
a semantic claim and belongs to the mission, not to the projection.

Until they are written, the artifact does not lie: each renders as an explicit non-final entry
titled with the client wording a human already chose for that task in `next[]`, carrying its real
evidence, and saying in the page's own words that the write-up *"is not final and is not being
presented as a conclusion."*

**Ownership, restated because it is the whole point of this boundary:** MAIN T owns the semantic
meaning of D3/D4/D5. The Client Review session does not write these summaries, and did not write
them — the template below is held open to receive them. Anything that arrives here is client
*wording* for a conclusion MAIN T reached, never a conclusion authored by the projection.

⛔ **Statuses and evidence references must keep deriving mechanically.** Do not hand-type
`status:` or `evidence_refs:` back into the narrative while adding a write-up. That is exactly the
coupling this session removed, and re-introducing it in one entry re-opens the whole class.

**To clear the blocker,** add a `delivered:` entry per task to
`missions/client-review-v1/reviews/navira-marketing-model.yaml`. Two prose fields each:

```yaml
  - id: D-D3
    task: D3                  # links to the mission record; status and evidence come from there
    title: <client-facing title>
    origin: CLIENT | FACTORY_PROPOSED
    summary: >-
      <what we found, in the client's language>
    business_impact: >-
      <why it matters to them>
    # evidence_refs: omitted on purpose — derived from the task's own evidence rows
```

Omit `evidence_refs` and `status`. Both are read from the record. Retyping a path the append-only
store already holds is a way to get it wrong.

---

## The full refresh sequence

```text
1.  MAIN T closes D5 with evidence, and says: authoritative mission HEAD = <sha>
2.  MAIN T supplies the outcome write-ups (summary + business_impact per task).
    This is the only step that needs a human, and it clears the last blocker.
3.  python scripts/meeting_ready.py --root .worktrees/mission --open
```

⛔ **No merge. No push. No copy-pasted analytical prose.** Step 3 reads the isolated mission
state read-only; step 2 is the only thing anyone types, and it is client wording, not findings.

If step 2 is skipped, step 3 still produces a rendered, validated, honest artifact — it just
reports `NOT_READY`, and the outstanding items are visibly marked pending. That is the fallback,
and it is deliberate: the page degrades, it does not fail.

---

## What the gate checks, and why each one exists

Every check derives from a contract the module already enforced; the gate is where they are read
together. Each has a test that makes it fire *and* a test that makes it pass —
`tests/test_client_review_readiness.py`.

| check | blocks? | exists because |
|---|---|---|
| `canonical_state_readable` | BLOCK | a review built from nothing renders a confident empty page |
| `freshness` | BLOCK on UNAVAILABLE, WARN on STALE | an unverifiable timestamp is not a fresh one |
| `narrative_matches_canonical_state` | BLOCK | **the 2026-09-01 defect** — see below |
| `completed_work_is_written_up` | BLOCK | an omitted section is indistinguishable from a complete one |
| `no_status_rendered_without_a_basis` | BLOCK | a status nobody checked is a guess in the shape of one |
| `cited_evidence_resolves` | BLOCK | a degrade to CLAIMED is not a diagnosis; name the file |
| `no_unsubstantiated_claim` | BLOCK | a guarded word that lost its evidence must not be on screen |
| `required_sections_populated` | BLOCK | the runbook walks these; an empty one derails the meeting |
| `client_boundary_holds` | BLOCK | if the allow-list projection raises, nothing may be shown |
| `mission_record_integrity` | WARN | mission control's to reconcile, presenter's to know |
| `risks_still_current` | WARN | a resolved risk is good news, not a defect |

### The defect the drift check exists for

Measured 2026-09-01 against the live store, before any change:

```text
next N-1  R3        narrative BLOCKED      record DONE
next N-2  D1        narrative NOT_STARTED  record DONE
next N-3  D2        narrative NOT_STARTED  record DONE
next N-4  D3        narrative NOT_STARTED  record DONE
next N-5  D4        narrative NOT_STARTED  record DONE
next N-6  D5        narrative NOT_STARTED  record IN_PROGRESS
milestone Map the available marketing data      BLOCKED     → DONE
milestone Synthesise requirements               NOT_STARTED → DONE
milestone Candidate designs and skeptical review NOT_STARTED → DONE
milestone Recommendation and sign-off           NOT_STARTED → IN_PROGRESS
```

Ten hand-typed statuses, each one wrong, each one about to render to a client as fact — including
telling them that the data-cartography work was *blocked* on the day it completed. The raw
measurement is at `docs/evidence/client-review-readiness-2026-09-01/narrative-drift.json`.

The typed statuses have since been deleted from the narrative and replaced with `task:` links, so
this class of error is now structurally unavailable: there is nothing left to type wrong. The
drift check remains as a live guard for anything a future contributor types by hand.

---

## Rendered validation

```bash
python scripts/render_check_client_review.py
```

Loads the built file in real Chromium at three widths × two colour schemes × standard and Live
Meeting mode, and asserts every section paints, nothing is clipped, nothing scrolls sideways, no
console errors, no offsite requests, no operator-only string is *visible*, navigation resolves, the
meeting-mode button actually works when clicked, and the page still renders with JavaScript off.
Screenshots and a JSON report land in `docs/evidence/client-review-readiness-2026-09-01/`.

`scripts/meeting_ready.py` runs this for you. Use `--no-render` only where no browser exists — and
note that the result is then `SOURCE_CODE_IMPLIES`, never `RENDERED_CONFIRMED`.
