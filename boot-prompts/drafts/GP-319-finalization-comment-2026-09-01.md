# DRAFT Jira comment — finalization pass (GP-319?)

⚠ **Needs pasting by hand.** The Atlassian MCP is unavailable in this session, so nothing was
posted.

⚠ **VERIFY THE KEY BEFORE PASTING.** `GP-319` is inherited from
`boot-prompts/drafts/GP-319-comment-2026-09-01.md`, which itself chose the key *by content match,
not from a branch name*, and is **also still unposted**. Two drafts now point at one unverified
key. Confirm the key covers the cross-channel marketing model before pasting either, and paste the
earlier draft first — it describes the design pass this one continues.

⛔ **No wiki links below** — the wiki is private. Everything points at branch/commit.

---

Finalization pass over the cross-channel marketing model. **Nothing deployed. No Snowflake write,
no PBI edit, no repoint. No credential was retrieved or used.**

**Where the work is:** branch `mission/marketing-model-finalization` in `agent-factory`, forked
from `mission/marketing-model-v1` at `efb05cf`, commits `1ed4277` → `e7f92f3`. Evidence under
`docs/evidence/marketing-model-v1/FINALIZATION-01-status.md`.

## The defect that mattered

**The documented command for regenerating the client review produced a client-facing document that
understated its own evidence.** The runbook passes `--tasks .data/tasks.jsonl`, relative to the
working directory, and tells the operator to regenerate *"shortly before the meeting"*. Run from
the primary checkout that is correct. Run from any git worktree and it resolves to a `.data/`
containing no task store, and the artefact degrades:

```
from a worktree     grounding 4x ASSERTED    status 4x UNSUBSTANTIATED
                    freshness UNAVAILABLE    completion_basis UNAVAILABLE
resolved correctly  grounding 4x SATISFIED   status 4x Complete
                    freshness LAST_VERIFIED  completion_basis DERIVED
```

Same narrative, same code, different directory. The degradation is **visible rather than silent** —
the rendered page says UNSUBSTANTIATED four times — so this was never an overclaim. It is the
opposite, and still serious: the client would receive a document reporting four fully evidenced
delivered outcomes as unsubstantiated, produced by the command the runbook prescribes, at the
moment it prescribes it.

Fixed three ways: the default now resolves through the shared repo root; a relative `.data/…` path
falls back to that root; and writing the artefact is **refused** when the finished document
understates itself. The refusal was proven (it exits non-zero and writes no file) and the runbook
text is corrected.

## Also closed

- A test asserting the review's grounding was RED in every worktree and GREEN only in the primary —
  it was detecting its own broken input, not a regression.
- The `.gitignore` rule protecting the **live Power BI capture for a named client** did not exist on
  the mission branch (added to `main` after that branch forked). It read as safe only because the
  capture is not present in that worktree — an absence of a file, not a guard. Ported and proven
  with a real file: 0 paths staged.
- The recommendation's outstanding evidence citation is back-filled — deliberately **not** by
  committing the capture, which would stage client commercial data. Its offline validator was
  re-run: ALL PASS, exit 0.
- The dashboard test suite recorded as "NOT RUN, blocked by a live session" — **108 passed**. The
  collision premise was stale by three weeks (file mtime 2026-08-11).
- A flagged suspicion that a zero ROAS could render as a real number was **checked and found not to
  be a defect**: both surfaces gate on the same condition.

## TEST vs PROD

**TEST only, and read-only within TEST.** No production object was read, written or repointed.
No credential retrieved.

## Validated how, and at which layer

- **Query/logic layer:** 751 tests pass on the branch; 17 mechanical checks re-derive every
  load-bearing figure in the design documents from machine-generated measurement tables.
- **Rendered layer:** the regenerated client artefact was loaded in real Chromium — 8 sections
  painted at 760 / 1100 / 1440 px, light and dark, in standard and presentation mode; 0 blank
  panels, 0 clipped headings, 0 horizontal scroll, 0 console errors, 0 offsite requests,
  0 operator-only text, and it still renders with JavaScript disabled.

⚠ Validated at **760 px and above only**. Phone widths are unmeasured.

## Open — and what unblocks each

Four items are blocked on **one credential decision**, not on analysis:

| open | verdict | unblocked by |
|---|---|---|
| deployed schema name | NOT-VISIBLE | reading the deployment environment |
| warehouse-mode rendering | NOT-EXERCISED | a read-only-proved credential |
| date-range control inertness in warehouse mode | NOT-MEASURED | the same |
| every Power BI rendered figure | NOT-EXERCISED | a reporting-service credential |

Two are decisions rather than measurements: whether to wire the second, currently unconsumed fact,
and the three client questions. ⚠ One of those client questions must be **enumerated before it is
asked** — the previously cited count of 16 is unreproducible (enumerations give 12 and 14).

**The architectural recommendation stands.** Nothing in this pass contradicts it and its reopen
condition was not triggered.
