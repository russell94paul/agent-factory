# PROPOSED research status — v3 addendum view

⛔ **This is a proposal, not an index.** Eventual destination: `docs/_index/research_status.md`.

⚠ **In its final form this file must be a GENERATED view of `research_registry.yaml`, never
hand-edited**, asserted current by `tests/test_views_are_current` (mirroring
`tests/test_tracker_is_current.py`). `07_RESEARCH_STATUS_AUDIT.md` §6 specifies the hybrid
generated/authored split. Until `scripts/build_research_registry.py` exists, **every count below is
AUTHORED and carries the command that regenerates it.**

**Phase 1 addendum, measured 2026-09-03 against `agent-factory` @ `827f871` (`main`).**
**⭐ Updated after Gate P0-B completed** — record:
[`14_P0B_EXTRACTION_AND_ONTOLOGY_RECONCILIATION.md`](14_P0B_EXTRACTION_AND_ONTOLOGY_RECONCILIATION.md).
⛔ **Nothing dispatched. No Phase 2 migration started.**

---

## 1. The one fact that governs the programme

```bash
python -c "import json;r=[json.loads(l) for l in open('.data/runs.jsonl',encoding='utf-8')];print(len(r))"
# 10
python -c "import json;e=[json.loads(l) for l in open('.data/events.jsonl',encoding='utf-8')];a=[x for x in e if x.get('kind')=='agent_returned'];print(len(a),sorted({str(x.get('dry_run')) for x in a}))"
# 7 ['True']
```

**10 recorded runs · 0 PASS · all 7 `agent_returned` events `dry_run=True`.**

⭐ **The estate has instruments and no observations.** Nineteen research lanes have completed;
twenty-six candidates, eight SIHRE prompts and now ten CELL-DR lanes wait. The subject of all of it —
a team of agents doing real work — has never been measured once.

---

## 2. Queue status

| Queue | Items | Dispatched | Status | Home |
|---|---:|---:|---|---|
| **R** — lane programme | 19 | 18 | 18 `COMPLETED`, 1 `NOT_RUN` (R06B) | `docs/research/` |
| **RB** — candidate backlog | 26 | 0 | `CANDIDATES_NOT_DISPATCHED` | `docs/research/backlog.yaml` |
| **DR** — SIHRE queue | 8 | 0 | all `NOT_RUN` | `docs/raw_research/agent2_sihre_consolidation_pack/research_prompts/` |
| **IN** — inbound pack prompts | 38 | ? | all `STATUS_UNKNOWN` ⚠ contains duplicates | `docs/raw_research/**` |
| **CELL-DR** — v3 forward queue | 10 | 0 | ⭐ **ACCEPTED, NOT ACTIVATED** | `SRC-V3` |

```bash
ls docs/research/R*.md | wc -l                                                          # 19 prompt files
ls docs/research/answers/ | wc -l                                                       # 25
python -c "import yaml;print(len(yaml.safe_load(open('docs/research/backlog.yaml'))['missions']))"   # 26
ls docs/raw_research/agent2_sihre_consolidation_pack/research_prompts/DR0*.md | wc -l    # 8
```

⛔ **`STATUS_UNKNOWN` is not `NOT_RUN`.** The 38 inbound prompts arrived pre-authored; this
repository holds no record of whether they were run before import. Collapsing them would assert
something about work done elsewhere that this repository cannot see.

⛔ **`NOT_RUN` for DR01–DR08 *is* a `ZERO`, not a `NOT-RECORDED`** — `docs/research/answers/` holds
24 answer files for other lanes, so the instrument is proved able to see an answer if one existed.

---

## 3. ⛔ Corrected identifiers — read before citing any RB row

`docs/research/backlog.yaml` numbers its 26 missions **`RB-00A…RB-00F`, then `RB-01…RB-20`.**
It does **not** use a contiguous `RB-01…RB-26`.

```bash
python -c "import yaml; d=yaml.safe_load(open('docs/research/backlog.yaml',encoding='utf-8')); \
print([m['research_id'] for m in d['missions']])"
```

Earlier Phase 1 documents and the v3 ingest instruction cite the contiguous range and reference rows
**by position**, shifting every citation by six. Corrections:

| Previously cited as | Correct ID | The ID actually cited names |
|---|---|---|
| RB-17 — error correlation between agent configurations | **RB-11** | a crosswalk for the six evidence vocabularies |
| RB-12 — which config parameters change outcomes | **RB-06** | credit assignment across a team |
| RB-09 — the store-capability question | **RB-03** | an evaluation protocol for org and team designs |
| RB-15 — ablation | **RB-09** | rank ladder versus absence table |
| RB-01…RB-06 — the six `NOT_RESEARCH` rows | **RB-00A…RB-00F** | five prior-art/foundational lanes and one comparison |
| RB-03 — complete one real agent run | **RB-00C** | what none of the existing knowledge stores can do |

⭐ **In every case the row actually named is a plausible-looking research item, so the error does not
announce itself.**

---

## 4. Two statuses that must never be collapsed

`run_status` ≠ `absorption_status`.

`docs/absorption-backlog.md` exists precisely because completed answers were not absorbed, and
`docs/findings.d/F75` records *"both reconciliation checks passed over three unabsorbed answers."*

⭐ **A completed research pass whose findings nothing acted on is the 965-run loop again: it
measured, and nothing changed.**

---

## 5. CELL-DR forward queue — four readiness axes

⭐ **Absent mission history blocks empirical calibration and promotion. It does not block prior-art
research, mathematical formulation, architecture design or experiment design.**

| Lane | RESEARCH | EXPERIMENT | IMPL | PROMOTION | Blocked by |
|---|---|---|---|---|---|
| CELL-DR-01 Canonical architecture | ⭐ **READY** | n/a | ⛔ | ⛔ | — ⚠ apply TD-7, TD-8, E-01 to the prompt |
| CELL-DR-02 Link Fabric | ⭐ **READY** on the **rescoped** spec (`16`) | ⛔ no harness | ⛔ TD-6 undecided | ⛔ | ⛔ **do not dispatch the v3 original** |
| CELL-DR-03 HyperMESH | ⚠ READY_ON_DEPENDENCY | ⛔ P0-E | ⛔ | ⛔ | CELL-DR-01 |
| CELL-DR-04 Operative Kernel | ✅ READY_ON_DEPENDENCY | ⛔ P0-E | ⚠ **PARTIAL** | ⛔ | DR-01, DR-03 |
| CELL-DR-05 SIHRE | ✅ READY_ON_DEPENDENCY | ⛔ **HARD** | ⛔ | ⛔ | DR-03, DR-04 |
| CELL-DR-06 CELL ADAPT | ✅ READY_ON_DEPENDENCY | ⛔ **HARD** | ⚠ **PARTIAL** | ⛔ | DR-04, DR-05 |
| CELL-DR-07 Mesh / Foundry / MESA | ✅ READY_ON_DEPENDENCY | ⛔ P0-E | ⛔ | ⛔ | DR-02, DR-05, DR-06 |
| CELL-DR-08 Domain Plane | ⛔ **BLOCKED_LOCAL** | ⛔ | ⛔ | ⛔ | ⭐ **a Domain design record that does not exist** |
| CELL-DR-09 CELL-Q | ⛔ BLOCKED_LOCAL | ⛔ no dataset | ⛔ | ⛔ **OUT OF SCOPE** | DR-08 |
| CELL-DR-10 Final synthesis | ⛔ NOT_READY | n/a | ⛔ | ⛔ | all prior lanes |

**`PARTIAL`, not `PROVEN`, for CELL-DR-04 and CELL-DR-06.** `contract.py`, `evals.py` and
`calibration.py` exist with tests — that proves implementation *anchors*, not the end-to-end
evaluation architecture or operational effectiveness.

---

## 6. Local gates — these block dispatch, and none is research

| Gate | Status | The measurement |
|---|---|---|
| **P0-A** Source intake | ✅ **COMPLETE** | 3 external sources hashed in-archive and post-extraction, byte-identical; reconciliation written |
| **P0-B** Make canon visible | ⭐ **COMPLETE** | ontology surfaced (3-way hash match); both `.docx` converted at **100% body coverage**; `.xlsx` read (3,288 cells); `.pdf` extracted (576 lines). ⚠ NERVE/Switchboard surfacing remains open |
| **P0-C** Corpus integrity | ⛔ **OPEN, and widened** | **719 claimed vs 916 measured** — delta **197**. ⭐ Was 898 before P0-B ran: **surfacing canon adds unindexed files, so P0-C's gap grows every time P0-B does its job** |
| **P0-D** Migration safety | ⛔ **OPEN** | 5 worktrees, **18** modified tracked files, 54 untracked paths; AMBER baseline not re-measured |
| **P0-E** Observation | ⛔ **OPEN** | **10 runs, 0 PASS, 7/7 dry-run** — `RB-00C` |

```bash
find docs .agent-platform blueprints missions evals boot-prompts -type f | wc -l    # 916  (claimed 719)
git worktree list | wc -l                                                          # 5
git status --porcelain | grep -c '^ M'                                             # 18
```

⛔ **Two sequencing corrections to v3 §10, both concerning P0-E:**
1. It is scheduled **after** Waves D and E, which are the waves it unblocks. Move it to Local 0.
2. It is gated behind the documentation migration (*"After the safe migration gates permit it"*).
   Nothing about completing one agent run requires the docs to be reorganised first. **Unbind it.**

---

## 7. Terminology decisions — ⭐ ten open, awaiting user approval

**Authoritative record and full evidence: `14_P0B_EXTRACTION_AND_ONTOLOGY_RECONCILIATION.md` §7.**
⛔ **P0-B surfaced and recommended. It ruled on nothing.**

| # | Decision | Status | Owner |
|---|---|---|---|
| TD-1 | ⭐ **Cell Mesh — team topology or OS federation?** | ⛔ **DIRECT CONTRADICTION** between two surfaced sources | CELL-DR-01 |
| TD-2 | Federation layer name | OPEN | CELL-DR-01 |
| TD-3 | C-MESH / T-MESH / OS-MESH | ⛔ **0 in every canonical source** | CELL-DR-01 |
| TD-4 | SIHRE expansion | ✅ **CLOSED** — *Self-Improving Heterogeneous Reasoning Ensemble* (`SOURCED`, v2 Lane 05) | — |
| TD-5 | OPC | ⛔ OPEN — customer-facing, undefined everywhere | CELL-DR-01 |
| TD-6 | ⭐ **Link Fabric vs CellBus** | ⛔ OPEN — **CellBus is the incumbent on evidence** | CELL-DR-02 |
| TD-7 | Blueprint / Genome / **Image** / **`TeamSpec`** | ⭐ **five names; two have code, none has both** | CELL-DR-01 |
| TD-8 | ⭐ **Operative Kernel vs CELL Kernel** | ⛔ **NEW from P0-B** — `Operative Kernel` = 0 everywhere | CELL-DR-01 |
| TD-9 | Organism vs Organization | ⛔ **NEW from P0-B** — a genuine tie | CELL-DR-01 |
| TD-10 | Operative Cell — retire or define | OPEN — defined nowhere | CELL-DR-01 |

**Two of the original six are covered by the existing `KNOWN_TERMINOLOGY_COLLISIONS.md`. Four were
not — and P0-B added three more the register never contemplated.**

---

## 8. Absorption status — unchanged and still the quiet risk

| | Count |
|---|---:|
| Completed R-lane answers | 18 |
| Answers with a recorded absorption disposition | ⚠ **not tracked in any index today** |
| Open absorption rows | `docs/absorption-backlog.md` — `RB-00F` filed to disposition them |

⛔ **`COMPLETED` means an answer file exists. It does not mean the answer was absorbed.** The
registry carries both fields and must never collapse them.

---

## 9. What changes this file next

1. `scripts/build_research_registry.py` is written and every mechanical field becomes GENERATED.
2. ~~Gate P0-B completes and 13 `ABSENT (corroborated)` verdicts become measured verdicts.~~
   ⭐ **DONE 2026-09-03 — 24 verdicts resolved to `ZERO (MEASURED)`.** `14` §5.2.
3. Gate P0-C completes and the 179-file index delta closes.
4. Gate P0-E completes and `EXPERIMENT_READINESS` moves off `BLOCKED_OBSERVATION` for the first time.

⚠ **Do not hand-edit a count in this file.** `~/.claude/skills/INDEX.md` claimed 63 skills, was
corrected to 235 files, and measured 303 three weeks later — in a file whose own text warns about
exactly this. Every number above carries its command; use the command.
