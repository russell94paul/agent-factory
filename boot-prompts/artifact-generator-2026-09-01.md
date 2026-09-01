# Artifact Generator P0 — shipped, unrendered, uncommitted

**Written 2026-09-01.** New workstream; supersedes nothing. Runs alongside
`mission-handoff-2026-09-01.md` (the mission itself, which **another session advanced past this
file's fixture** — see §3).

`next:` **Commit the P0 slice (Paul's call), then do the render check P0 owes.** Nothing else is
blocked.

---

## 0. ⛔ Read first — three things that are NOT done

1. **Nothing is committed.** Twelve paths are untracked or modified in `agent-factory`. Paul's rule
   is ask-before-commit and I did not ask before the context checkpoint fired. **Verify HEAD before
   staging** — this checkout moved twice under me during the session.
2. **The rendered surface was never visually verified.** Playwright's browser cannot reach this
   machine's localhost; the Chrome extension was not connected. I ran structural checks instead
   (balanced tags, every CSS var defined on bare `:root`, all three theme layers, zero external
   URLs). **That does not satisfy the consumer-layer rule in the global CLAUDE.md and there are no
   screenshots.** This is the single largest gap in the slice.
3. **The GP-319 correction is drafted and unposted** —
   `boot-prompts/drafts/GP-319-comment-2026-09-01.md`. Atlassian MCP was unavailable (no Jira tools
   in the roster). It needs pasting by hand. Ticket key verified against the wiki page frontmatter,
   not a branch name.

## 1. What exists now

```
factory/projection.py        100  extracted allow-list boundary + leak backstop, keyed by artifact
factory/assertions.py        278  extracted grounding/freshness + Counterfactual, Maturity, bases
factory/forensic_source.py   203  the prose boundary validator (anchors only, NOT a md parser)
factory/case_study.py        614  second compiler + typed view model + validation rules
factory/case_study_render.py 603  second renderer, CSS-only reveal
tests/test_case_study.py     378  11 fixture assertions + 17 negative controls
missions/delivery-001/case-study.yaml  1474  the authored forensic record
docs/case-studies/delivery-001-marketing-model.md   2351  prose + 72 anchors
docs/design/artifact-generator-proposal.md           736  the approved architecture
docs/artifacts/delivery-001-case-study.html          105KB generated output
factory/client_review.py     -116/+27  now delegates; PUBLIC API UNCHANGED
factory/context.py           +53/-4    additive: 3 statuses, observed, superseded_by, 1 kind
```

**Regenerate:**
```bash
python -m factory.case_study missions/delivery-001/case-study.yaml \
  --tasks .data/tasks.jsonl --mission .data/missions/marketing-model-reconstruction-v1.json \
  --out docs/artifacts/delivery-001-case-study.html
```

## 2. Verify in one command each

```bash
python -m pytest -q                          # expect 769 passed, 2 xfailed
python -m pytest tests/test_client_review.py -q   # 42, and the FILE MUST BE UNTOUCHED
python -m pytest tests/test_context_pack.py -q    # 9, untouched — the additive-change proof
python -m factory.case_study missions/delivery-001/case-study.yaml \
  --tasks .data/tasks.jsonl --mission .data/missions/marketing-model-reconstruction-v1.json
git status --porcelain                       # 12 paths; NOTHING committed
```

⚠ The suite takes ~3m30s. The baseline before this work was **732 passed, 2 xfailed** — if you see
732, the new tests are not being collected.

⛔ **The 769 figure was measured at `4e076d8`. HEAD is now `8fba030` (F100 gains a second instance) —
another session committed after my measurement.** Three commits landed under this session in total.
**Re-run the suite before trusting 769**, and re-measure HEAD before staging anything.

## 3. ⭐ The mission moved under this fixture, and that is the demo

`marketing-model-reconstruction-v1` advanced mid-session: **R3 and D1 both closed** (commit
`4e076d8`, another session). The authored record still claims R3 `open` and D1 `blocked`.

**The compiler detects this and reports `DIVERGED`, showing both values.** It reports and does not
repair — correcting a narrative belongs to its author. Do not "fix" the yaml to match; the
divergence is currently the best live evidence that the artifact is a projection and not a second
truth store. If you do reconcile it, reconcile the *narrative prose too*, or you will create the
`FIELDS.md` drift the validator exists to prevent.

⚠ `tests/test_case_study.py::test_2_...` asserts **50%** completion. That is live-state-dependent and
**will fail as the mission advances**. It is a semantic assertion over a moving store — decide
deliberately whether to pin it to a snapshot or let it track.

## 4. Gotchas earned, so they are not re-learned

- ⛔ **An extraction is a copy, not a re-derivation.** `GUARDED_WORDS` and the `freshness()` boundary
  were both reconstructed from memory and both were wrong (17-member frozenset, not my list;
  `<=` not `>=` at the STALE boundary). Diff against the file before wiring.
- ⚠ **The leak backstop cannot tell a credential from prose about one.** It fired twice on
  legitimate narrative. Reword; do not weaken it. It errs safe.
- ⚠ **`mechanism_refs` must be plain paths.** `module.py:1-40` cannot resolve on disk.
- ⚠ **Heredocs broke twice this session** on quoting, exactly as the global CLAUDE.md warns. Use
  Write/Edit for any content with quotes or escapes.
- **`assertions.PROMOTABLE` must stay `("MEASURED","DERIVED")`.** A test pins it. Adding
  `DOCUMENTED` would let every claim read out of a document promote itself to VERIFIED.

## 5. ⭐ The meta-finding — preserve it, do not upgrade it

A `TemporalAssertion` contract was fully designed before an inventory sweep found
`factory/context.py:109` already refusing `CURRENT` without a `checked` date. **The design process
for the tool that documents `KNOWLEDGE_AVAILABLE_BUT_NOT_CONSUMED` committed it.**

It is recorded as issue `M-13` and scene 10 in the case study, classified **`MANUAL INVENTORY
INTERCEPTED`** with a future preflight at `MAY_REDUCE_LIKELIHOOD`. ⛔ **Do not let a later session
turn this into "Known-Failure Preflight caught it."** It does not exist. The findings ledger is
machine-read and nothing consumes it as a precondition.

## 6. Open, and not done

| | Item | Owner |
|---|---|---|
| 1 | **Commit the slice** — ask Paul first | Paul |
| 2 | **The render check** — screenshots 700/1000/1400px, light + dark, into `docs/evidence/` | next session |
| 3 | **Paste the GP-319 comment** from `boot-prompts/drafts/` | Paul |
| 4 | **M-02**: R1 and R2 still name superseded task ids in their own headers | next session |
| 5 | **M-07**: extend R2's scope to `aldc-launchpad/docs/readouts/` — 3 designs read by nobody | next session |
| 6 | Rotate the three exposed credentials — **still unconfirmed**, one spans production | Paul |
| 7 | 19 of 37 issues are not yet in the fixture (18 are; 9 per track) | optional |

## 7. What P1 should be — recommended at the gate, not started

1. Fix the three provenance defects the fixture documents — **stale artifact headers first**. A
   record whose own evidence carries wrong provenance is a weak demonstration of provenance.
2. The render check item 2 above owes.
3. **Extract the shared renderer chrome** — now that two renderers exist and have diverged, what is
   genuinely common is visible rather than guessed. Deliberately not done in P0.
4. **The Delivery Command Center as the third artifact type** — three examples prove genericity;
   two do not. The gate deferred it because six of its ten sections have no evidence until
   Delivery #002.
5. Instrument the gaps the artifact renders as absent: per-task `actual_minutes`, an acceptance
   event, a distinct session pid per claim. Those three turn K-9, K-8 and K-10 from states into
   numbers.

⛔ **Do not start the Command Center before 1–3.**
