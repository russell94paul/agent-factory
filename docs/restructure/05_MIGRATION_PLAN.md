# 05 — Migration plan

**Phase 1 proposal.** Nothing here has been executed. Execution requires the exact instruction
`APPROVE RESTRUCTURE PHASE 2`.

---

## 0. Decisions required from the operator before Phase 2

Eight. **D-1 and D-3 are blocking** — Phase 2 cannot start safely without them. The rest gate
individual batches and can be answered as those batches come up.

### D-1 — ⛔ BLOCKING. The four live worktrees

```bash
git worktree list
# .worktrees/finalization  e7f92f3 [mission/marketing-model-finalization]
# .worktrees/mission       efb05cf [mission/marketing-model-v1]
# .worktrees/reliability   b338324 [reliability/recurrence-preflight]
# .worktrees/switchboard   1d6b3a4 [switchboard/p0]
```

Four branches hold their own full copies of `docs/` and `factory/`. A restructure on `main` will
conflict with every one of them at merge time — a directory `mv` against a branch that edited files
inside it produces rename/edit conflicts across the whole subtree.

Mitigating fact, measured: **zero tracked files move** (`03` Part 9). Conflict surface is therefore
far smaller than a normal restructure — confined to the ~35 untracked `mv`s (invisible to those
branches anyway) and the edits to `README.md` and `.gitignore`.

| Option | Consequence |
|---|---|
| **A (recommended)** — proceed; the additive shape makes conflicts unlikely | Fastest. Residual risk on `README.md` / `.gitignore` only |
| B — merge or close the four branches first | Safest, and a substantial separate piece of work |
| C — restructure on a branch, merge later | Defers the conflict without removing it |

### D-2 — ⛔ BLOCKING for the phone workflow. Is a cloud checkout in play?

`04` §8.6: a Claude Code session started from a phone operates on a **cloud checkout**, so
`PROJECT_PROGRESS.yaml` must be **committed** to be visible there.

- If the phone workflow matters: `/cell-session-close` must commit the tracker — a *functional*
  requirement, not housekeeping.
- ⛔ It still does **not** imply pushing. `AF-RELEASE-GATE-01` is BLOCKED and the remote is public.
  **If the phone workflow requires a push to a public remote, that is a release-gate decision, not
  a restructure decision, and Phase 2 will not take it.**

**Question:** does the phone workflow need to reach a remote, or is a local-only tracker with
manual sync acceptable for now?

### D-3 — ⛔ BLOCKING. The dirty working tree

17 of the 18 modified files sit in paths a batch touches (`01` §1.2). **Commit or stash them before
Batch 1.** Per your standing preference, Phase 2 will not commit anything without asking.

### D-4 — Terminology scope: does `agent-army-research` rename too?

`~/repos/agent-army-research` (155 md files) is *"the authoritative home of Agent Army research"*.
Renaming vocabulary here alone splits the programme's language across two repos. **Recommendation:
defer the rename entirely** (`06` §6) — which also defers this.

### D-5 — The unreadable CELL OS delivery backlog

`CELL_OS_Delivery_Backlog_v0.2.xlsx` (43,536 B) is the natural seed for the tracker and **cannot be
read** — no `.xlsx` converter exists here. Options: write one (~30 lines, `zipfile` + `sharedStrings.xml`);
export to CSV by hand; or seed the tracker from the migration plan instead (**recommended**, `04` §8.9).

### D-6 — Two different architecture-overview diagrams

`docs/diagrams/CELL OS - Architecture Overview.png` (1,821,873 B) and
`docs/raw_research/CELL_OS_Architecture_Overview_Diagram.png` (1,282,877 B) — **different bytes,
same subject**. Which is current is `UNKNOWN`. Phase 2 will not pick one.

### D-7 — Tracker scope for the first pass

The tracker spec is large. **Recommendation: build §8.1–§8.3 + §8.8 (schema, state model, tests)
in Batch 5, and the UI (§8.5) + forecast engine (§8.4) in Batch 8**, so the data model is proven
before anything renders a date. A forecast engine shipped alongside its first data has nothing to
be tested against.

### D-8 — Is `docs/board/tickets.json` a seed for the ticket set?

It exists with fixtures. Unread in this pass beyond its existence.

---

## 1. Preconditions — checked at the start of Phase 2, and again before every batch

```bash
git rev-parse --abbrev-ref HEAD          # expect: main
git rev-parse --short HEAD               # RECORD IT — compare to 827f871
git status --porcelain | wc -l           # expect: 0 after D-3, else STOP
git worktree list                        # expect: the same 4
python -m pytest 2>&1 | tail -1          # expect: 2 failed, 1016 passed, 2 xfailed
```

⛔ **If `HEAD` differs from the recorded value, STOP.** Multiple sessions share this checkout; git
state moved between commands during this audit. Re-measure, do not assume.

⛔ **If the pytest line differs from the baseline in either direction, STOP.** More failures means
something broke. *Fewer* failures means someone fixed F101 — and the control that proves Phase 2
changed nothing has just been removed.

---

## 2. The ten batches

Every batch: **smallest coherent group → write the inverse-move manifest → execute → validate →
record → stop on failure.** No batch proceeds while the previous one is red.

---

### Batch 1 — Indexes and intake conventions
**Risk: LOW · Reversible: fully (all creations + one YAML edit)**

1. `mkdir docs/_incoming/`; write `README.md` with the 5-clause intake contract (`04` §3).
2. Write `scripts/build_corpus_index.py` — emits mechanical fields only (path/bytes/sha256/
   first_committed), **merges** existing interpretive fields, never overwrites them.
3. Run it. Delta `corpus_manifest.yaml`: `coverage.files_on_disk_in_scope: 719` → 888; add records
   for the 63 uncovered files; **amend the `AF-RAW-LOOSE` bundle** so the CELL OS artifacts it
   silently swept up are enumerated (`01` §0.2).
4. Append DC-14, DC-15, DC-16 to `duplicate_clusters.md` (`02` Part D).
5. Create `research_registry.yaml` + `research_status.md` (`07`).

**Validate:** all `_index/*.yaml` parse; `coverage` matches its own regeneration command; **the 168
pre-existing records are byte-identical** (`git diff --stat` shows additions only).

⛔ **Stop condition:** any pre-existing record changed. The interpretive layer is the corpus's most
expensive artifact and this pass must not touch it.

---

### Batch 2 — Raw and synthesized research
**Risk: MED · Reversible: fully (copies + untracked mv)**

1. **EXTRACT** the two ontology files from `CELL_OS_Frontier_Audit_Research_Pack_2026-09-02.zip` to
   `docs/architecture/canonical/terminology/`, each with a provenance header naming the archive and
   its SHA-256 `6cc48dc65fa3a922`. ⛔ **Targeted two-file read-out. Not an unzip.**
2. Convert the two `.docx` with `scripts/docx_to_md.py` → `docs/raw_research/converted/`.
   **Verify extraction coverage** the way GAP-01 did: raw `<w:t>` chars vs md-stripped chars,
   expect ~100%. Record the figure. **Report figures not extracted as a residual gap.**
3. `COPY` the Crossreference Audit to `docs/research/syntheses/`; leave a stub at the original path
   pointing to the copy. ⛔ **The original is not moved or edited** — `raw_research/` is immutable.
4. `mv` the two rendered HTML artifacts to `docs/artifacts/incoming/`.
5. `mv` the root `CELL_OS_NERVE_…zip` to `docs/_incoming/`.

**Validate:** `sha256sum` on every source before and after — **must be unchanged**; the two `.docx`
originals unmodified; conversion coverage recorded; **`find docs/raw_research -type f | wc -l`
decreases by exactly 3** (the two HTML + nothing else — the audit COPY leaves a stub).

⛔ **Stop condition:** any hash under `docs/raw_research/` changes. That is the immutability rule
failing, and it is not recoverable by re-running.

---

### Batch 3 — Canonical and proposed architecture
**Risk: LOW · Reversible: fully**

1. `docs/architecture/canonical/README.md` — the 10-tier precedence rule (`04` §4).
2. `docs/architecture/proposed/README.md` — "nothing here is implemented".
3. Seven `proposed/*.md` stubs, each stating its **measured occurrence count** and `0 in code`.
4. `docs/decisions/README.md` + ADR-0001 (records `04` §1).
5. `mv docs/diagrams/ docs/architecture/diagrams/` (4 untracked files).
6. `COPY` the raw-research overview PNG alongside; **both kept**, D-6 unresolved and labelled.

**Validate:** every `proposed/*.md` occurrence count reproduces from `scratchpad/term_scan.py`;
`canonical/README.md` links resolve; no file in `canonical/` lacks a code or test citation.

⛔ **Stop condition:** anything lands in `canonical/` that cannot cite code, a test or measured
evidence. That is the one rule the whole structure exists to enforce.

---

### Batch 4 — Product, UX, NERVE
**Risk: MED (the RETIRE) · Reversible: by recorded inverse mv only**

1. `docs/product/README.md` — pointer index. **No file moves.**
2. Link-check `docs/combined-execution-research-v2-2026-09-02/` — if **anything** references it, stop
   and report.
3. If clear: `mv` all 28 files to `docs/archive/combined-execution-research-v2-2026-09-02/`, with a
   `RETIRED.md` naming the surviving copy and the hash evidence (DC-14).

⛔ **Stop condition:** any inbound reference. ⚠ All 28 are untracked — **`git revert` cannot undo
this**. The inverse-move manifest is the only rollback.

---

### Batch 5 — Evidence, project status, tracker data model
**Risk: MED · Reversible: fully (all creations)**

1. `docs/status/` + `PROJECT_PROGRESS.yaml` seeded from **this plan's ten batches** (`04` §8.9).
2. `factory/progress.py` — load/validate/write. ⛔ Raises on `COMPLETE` without `acceptance_evidence`.
3. `docs/status/examples/PROJECT_PROGRESS.example.yaml` — 12 tickets, 10 synthetic active days.
4. `tests/test_progress.py` — the schema, evidence-gate and view-currency tests (`04` §8.8).
5. Generate `project_progress.json` + `PROJECT_PROGRESS.md`.
6. **Wire `factory/roadmap.py` gate verdicts into `verification_status`** — completion stays anchored
   to measured gates, not self-report.

**Validate:** `pytest tests/test_progress.py` green; **`test_complete_requires_evidence` demonstrated
failing** on a deliberately malformed fixture before it passes on a good one; regenerated views match
disk byte-for-byte.

⛔ **Stop condition:** the evidence gate cannot be made to fire. An evidence gate never seen refusing
is exactly the "capable but unmeasured" shape `README.md` Part I is organised against.

---

### Batch 6 — Code
**Risk: LOW · Reversible: fully**

**Nothing moves.** Two files are added (`progress.py`, `forecast.py` — the latter in Batch 8).
Record in ADR-0001 the two refactor candidates found and deliberately not taken:
`readiness.py` (1,948 lines, fan-in 16) and `registry.py` (fan-in 1).

**Validate:** `git diff --stat factory/` shows additions only.

---

### Batch 7 — Links, imports, references
**Risk: MED · Reversible: fully**

1. Re-run the runtime-path grep (`03` Part 1). **Expect every hard-coded `docs/` path to still
   resolve.**
2. Fix `README.md` §VII: `66 modules, 22,817 lines` → measured values **plus the regeneration
   command**, per its own §V.3.
3. Add the six new directories to §VII.
4. Rewrite only links into moved paths (of 219 relative `.md` links).
5. ⛔ **Verify `.gitignore`**: every rule still names an existing path, and **nothing previously
   ignored is now visible to `git status`**.

⛔ **Stop condition:** `git status` shows a previously-ignored path. One of those rules covers a live
client-data capture; that is a release-gate incident, not a migration hiccup.

---

### Batch 8 — Commands, forecast engine, tracker UI
**Risk: HIGH (`forecast.py`) · Reversible: fully**

1. Eight `/cell-*` commands, following the `af-*` shape (frontmatter `description:`, fenced command,
   *"do not summarise a count you did not read"*).
2. `/cell-work` — ⭐ the ticket-ID entry point (`04` §8.6).
3. `factory/forecast.py` — the Dynamic Due Date Engine (`04` §8.4).
4. `tests/test_forecast.py` — including both negative controls.
5. `docs/artifacts/cell-os-tracker.html` — 7 views, fetching `project_progress.json`.
6. `scripts/render_check_tracker.py` — light/dark × 760/1100/1440 + no-JS → `docs/evidence/`.

**Validate:**
- `test_forecast_refuses_below_eight_active_days` — **demonstrated firing.**
- `test_forecast_is_reproducible` — same seed, same P50/P80.
- `test_forecast_moves_in_the_right_direction` — +velocity earlier, +scope later, +blocker ≥.
- `test_no_progress_number_is_hand_written_in_html`.
- `test_every_ticket_command_resolves`.
- **Rendered-surface pass: every view paints, at every breakpoint, in both themes.** A query-layer
  pass is not a rendered pass — proven in this estate by a repoint that passed DAX parity while
  every visual showed "Error loading data".
- Toggle every filter on the ticket board and **record which respond and which are inert.** A silent
  no-op is a finding, never an acceptable default.

⛔ **Stop conditions:** the forecast produces a date with fewer than 8 active days; any view fails to
paint; any filter is inert and undocumented.

---

### Batch 9 — Full verification
**Risk: LOW · See `08_VALIDATION_AND_ROLLBACK_PLAN.md`**

Includes the falsifiable structural test from `04` §7: **resolve three concepts from path alone and
check against `docs/agent-army/CURRENT_STATE.md`.** If the paths disagree with the code-measured
instrument, the structure is wrong.

---

### Batch 10 — Final report
Produces `09_MIGRATION_EXECUTION_LOG.md`, `10_POST_MIGRATION_VALIDATION.md`,
`11_REPOSITORY_HANDOFF.md`, ending in `GREEN` / `AMBER` / `RED` on evidence.

⚠ **`GREEN` is already unreachable and this is known in advance.** `GREEN` requires *"all required
validation passed"*; the baseline carries 2 pre-existing failures that Phase 2 must not fix.
**The realistic best outcome is `AMBER` with the limitation documented** — which is the honest
verdict, not a downgrade. Stating it now prevents the end-of-migration temptation to fix F101 in
order to reach a colour.

---

## 3. What this plan deliberately does not do

- **No file is deleted.** 29 are retired to `docs/archive/`; nothing is removed.
- **No duplicate is merged.** DC-16 is explicitly left alone — DC-08 records that byte-identity
  between an artifact and its fallback *is the proof the fallback is not stale*.
- **No global rename.** `06` §6 recommends deferring the Agent Factory → CELL OS rename entirely.
- **Nothing is promoted to canonical without evidence.** Only two files enter `canonical/`, both
  extracted verbatim from the project's own ontology.
- **No push, no history rewrite, no force-reset, no commit without asking.**
- **`docs/raw_research/` is never edited.** Four `COPY`s out; zero writes in.
- **No brokerage, no live financial execution, no credential-bearing path** (`04` §5).
- **The 2 failing tests are not fixed.** They are the control.
