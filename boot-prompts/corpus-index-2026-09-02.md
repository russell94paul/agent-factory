# Boot — the corpus index landed; the corpus is not short of research

**Written 2026-09-02.** Repo `agent-factory` @ `fc78074` (`main`), working tree dirty.
Previous boot prompts in this workstream: none — this is a new lane. Adjacent:
`artifacts-and-venture-2026-09-01.md`, `switchboard-p1-and-finalization-2026-09-01.md`.

---

## `next:` — pick ONE, and none of the top three is a research pass

1. ⛔ **`RB-00A` — convert the two `.docx` and index them.** ~1 hour.
   `docs/raw_research/Beyond_Agent_Armies_Frontier_Architectures.docx` (431 KB) and
   `Agent_Factory_Frontier_Architecture_Prioritization_Pack.docx` (204 KB) have **never been read by
   any pass**. Their titles name the two questions an architecture synthesis must answer, and the
   first bears directly on `contradictions.md` **CN-01** — which was decided without them.
   **Every artifact in `docs/_index/` carries this as a stated limit (`GAP-01`).** Cheapest, highest
   ratio, unblocks `RB-01`/`RB-02`/`RB-05`.
2. **`RB-00D` then `RB-00B` — settle the two tenancy questions, then score a second connector.**
   `docs/research/README.md` §4 q3: *"20 rows across 18 campaigns on one date cannot be unique on
   `(account_id, campaign_id, date)`. If it is one account, the declared primary key is wrong and
   the calibration world is built on a mistake."* ⛔ **Do not score a second connector before that is
   answered** or the error is inherited.
3. **`RB-00C` — complete one real agent run.** Blocked by `F90` (OPEN), which names the fix and its
   order: make the controller **refuse** a ticket whose `repo` is not this checkout, *then* thread
   the repository through. This single item converts ~a dozen research questions into measurements.
4. Only then: `RB-01` (what organisation-oriented MAS already provides) or `RB-02` (trace standards
   — the best-scoped mission in the backlog, because the answer is a standard to accept or reject).

Read `docs/research/dependency_graph.md` before dispatching anything. Maximum safe parallelism is
6 / 10 / 8 / 2 by wave; longest chain is 4 steps.

---

## What shipped

**Twelve new files, one modified.** Nothing else in the repository was touched.

```
docs/_index/corpus_manifest.yaml        168 records covering all 719 corpus files
docs/_index/document_catalog.md         20 subject groups, multi-membership
docs/_index/concept_index.yaml          86 concepts, stable IDs, speculative ones preserved
docs/_index/duplicate_clusters.md       13 clusters — nothing merged or deleted
docs/_index/contradictions.md           28 disagreements — none resolved
docs/_index/supersession_candidates.md  advisory; 5 declared vs candidates, 8 apparent-only
docs/_index/current_vs_proposed.md      112 capability rows
docs/_index/research_gap_candidates.md  42 gaps
docs/_index/high_leverage_concepts.md   14 candidates — no winners selected
docs/_index/repo_snapshot.md            CONFIRMED vs INFERRED throughout, 10 seams
docs/research/backlog.yaml              26 missions, NONE dispatched
docs/research/dependency_graph.md       concurrency + collision analysis
.gitignore                              ← the ONLY modified source file (see below)
```

Plus `agent-factory-research-review-pack.zip` — 616 entries, 3.4 MB, integrity-verified,
leak-checked, **gitignored**. Rebuild from `docs/_index/` at any time.

**Verified:** `git status` shows **0 deletions**. `python -m factory.dispatch`, `synthesis.unsynthesised()`
and `len(readiness.GATES)` all report unchanged. **Full suite exit 0.**

---

## ⛔ Not done — the honest list

| | |
|---|---|
| **The two `.docx` are still unread.** | 635 KB. `GAP-01`. The largest known hole in every deliverable. |
| **The sibling repo `agent-army-research` was not indexed.** | 155 files, 3.6 MB — the *authoritative* home of Agent Army research and of the Wave 0 synthesis that drives CN-01. `GAP-03`. A reviewer without it is missing the research half. |
| **Nothing was dispatched, decided or resolved.** | 28 contradictions open, 42 gaps open, 26 missions unlaunched, 0 of 19 absorption rows closed. **Deliberate** — the corpus-preparation prompt's stop condition forbids proposing an architecture in the same pass. |
| **No Jira ticket, and none invented.** | See below. |
| **Wiki committed, NOT pushed.** | `wiki` @ `39d8452`, **6 commits ahead of `origin/main`** — 5 were already there from earlier sessions. Push is Paul's call. |
| **The review pack has not been sent anywhere.** | It sits in the repo root, gitignored. |
| **`docs/_index/` is uncommitted.** | Untracked in `agent-factory`. Nothing has been staged or committed here. |

---

## ⛔ Jira — there is no ticket, and that is the finding

**This work maps to no Jira ticket.** Checked rather than assumed:

- Jira in this estate is **client work** (`GP-*`, `FU92-*`). This session did **zero** client work.
- A keyword sweep of the 91 tasks in `.data/tasks.jsonl` returned no match for corpus / index /
  review-pack / manifest / catalog.
- The Atlassian MCP is **not available** in this session.

⚠ **The nearest adjacent internal task is `CIP-02 — P0 Publish `docs/corpus/GAPS.md` from the
existing corpus`.** It is **NOT satisfied** — this pass wrote `docs/_index/research_gap_candidates.md`,
a different path with a different shape. **Do not close it**, and do not create a duplicate task for
this work either: `F96` records two duplicate tasks created off exactly this kind of near-match.
Paul's call whether `CIP-02` is now redundant, re-scoped, or still wanted as written.

**No draft was written to `boot-prompts/drafts/`** because there is no ticket to paste it into.
Writing one would be fabricating a ticket key.

⚠ Two *other* Jira drafts remain unposted from earlier sessions:
`boot-prompts/drafts/GP-319-comment-2026-09-01.md` and `…-finalization-comment-2026-09-01.md`.
Still unposted. Untouched by this session.

---

## The five things a cold session must not re-derive

1. ⭐ **`factory/assertions.py` already defines the built-vs-proposed vocabulary.**
   `EXERCISED / IMPLEMENTED_NOT_EXERCISED / SIMULATED / PROPOSED`, enforced by a dataclass that
   **raises**: a maturity claiming code must name `module:line`; one claiming it *ran* must cite
   `exercised_proof`; below `EXERCISED` the basis is **forced** to `SIMULATED` *"whatever the
   authored file said"*. `Counterfactual` has no `status` field, so it is structurally
   un-renderable beside a real outcome. **Do not invent a seventh maturity vocabulary.**
   It generalises to `readiness.py`, `presets.py`, `registry.py` — `HL-04`.

2. ⭐ **Five of the nine inbound packs carry the same source file byte-for-byte.**
   `Agent Factory Vision.txt`, 21,179 bytes, **six copies**; the ZEUS pack, **three**. 22
   exact-duplicate groups measured. *"Nine packs converge on Org-IR"* is **one source reformatted
   nine times.** Regenerate:
   ```bash
   python -c "
   import pathlib,hashlib,collections
   s=collections.defaultdict(list)
   for r in ('docs','.agent-platform','blueprints','missions','evals','boot-prompts'):
       for p in pathlib.Path(r).rglob('*'):
           if p.is_file(): s[hashlib.sha256(p.read_bytes()).hexdigest()].append(p.as_posix())
   print(sum(1 for v in s.values() if len(v)>1))"
   ```

3. ⚠ **Any import-graph instrument must resolve `from . import x as _x`.**
   This pass's first version handled only `from .x import y` and reported **38** modules with zero
   consumers against a true **14** (and those 14 are entry points — 20 modules carry `__main__`).
   That is `F84`'s exact class, **third instance in this repo**. Method note kept in
   `repo_snapshot.md` §4 rather than the fix quietly applied.

4. ⚠ **Never run a de-duplication script over `docs/evidence/`.** Five byte-identical PNG pairs are
   **no-JS negative controls** — a capture identical to its JS-enabled sibling is the *proof* that
   static rendering is complete. Deleting either half destroys the evidence. `DC-08`.

5. ⚠ **`docs/corpus/` has never existed.** `docs/CORPUS-AND-DESIGN-PROMPT.md` asks for it and was
   never run. **Three** separate prompts asked for a corpus index, each specifying a different
   deliverable shape, and **none of the three had run** before this pass. The bootstrap pack's
   scaffolding is still empty: `artifacts: []`, `concepts: []`, a 0-byte `claims.jsonl`.

---

## The one modified source file

`.gitignore` gained six lines ignoring `agent-factory-research-review-pack.zip`.

**Reason, not a preference:** the zip carries the client-identifying content
`AF-RELEASE-GATE-01` §4.1 enumerates, and an untracked-but-not-ignored artifact in a checkout
**shared by five sessions** is precisely the hazard §5 item 6 calls *"a live hazard, not a
hypothetical"* — one `git add -A` would stage 3.4 MB of client content into a repo whose remote is
**public**. Same shape and same remedy as the live PBI capture two entries above it.

Revert if you would rather the zip were tracked; nothing depends on the line.

---

## Gotchas earned

- ⚠ **A bash heredoc mangled a backslash again**, exactly as CLAUDE.md warns.
  `.replace('\\','/')` inside `<<'PYEOF'` arrived as an unterminated string literal. **Second
  confirmed instance.** Use the Write tool for any script containing a backslash — it worked first
  time.
- ⚠ **`set(cells[1]) <= set('-: ')` is True for an empty cell** (the empty set is a subset of
  everything), which silently dropped **80 of 128** table rows from a self-parse. The wrong count
  looked plausible. *A statistic parsed from your own document needs a row-count check against the
  raw line count.*
- **`rsync` does not exist in this Git Bash.** Use Python `shutil` for tree copies.
- **`pytest -q` exceeds the 120 s foreground timeout** (954 tests) — use `run_in_background`.
  `readiness.measure()` is 542 s cold.
- **`git log --diff-filter=A` scoped by pathspec** gives first-commit dates cheaply for a whole
  corpus in one call. For `docs/raw_research/**` it is the **import** date, not the authoring date —
  every manifest record there carries `creation_date_basis: import_date_not_authoring_date`.

---

## Where to look first

| Question | File |
|---|---|
| What exists in code? | `docs/agent-army/CURRENT_STATE.md` — ⭐ **outranks every index here**, cites `file:line` |
| What is built vs proposed? | `docs/_index/current_vs_proposed.md` |
| What does the corpus disagree with itself about? | `docs/_index/contradictions.md` |
| What is missing, and is it really research? | `docs/_index/research_gap_candidates.md` |
| What should I do next, and what can run in parallel? | `docs/research/backlog.yaml` + `dependency_graph.md` |
| What did a previous reconciliation already conclude? | `.agent-platform/RECONCILIATION.md` |
