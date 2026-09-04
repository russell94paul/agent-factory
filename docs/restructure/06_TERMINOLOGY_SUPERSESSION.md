# 06 — Terminology supersession

**Phase 1, read-only.** Measured 2026-09-03 against `827f871`. ⛔ **No rename was performed, and
§6 recommends that none be performed in Phase 2.**

---

## 1. The census

```bash
python scratchpad/term_scan.py        # 1001 text files; .git .venv __pycache__ .worktrees excluded
```

| Term | Occurrences | Files | In `factory/` code? | Concentration |
|---|---:|---:|:---:|---|
| **agent** (bare word) | 8594 | 603 | **yes, pervasively** | `docs/raw_research`=201, `docs/research`=57, `.agent-platform`=57 |
| **Agent Factory** | 1651 | 360 | yes | `docs/raw_research`=105, `.agent-platform`=54, `docs/research`=24 |
| **Switchboard** | 1442 | 139 | **yes — 3 modules, 3,403 lines** | `docs/raw_research`=38, `docs/research`=18 |
| **Agent Army** | 402 | 88 | no | `docs/raw_research`=33, `docs/_index`=13 |
| **Genome** (bare) | 220 | 51 | no | `docs/raw_research`=37, `docs/_index`=7 |
| **Operative** (bare) | 187 | 17 | no | `docs/marketing`=7, `docs/raw_research`=3 |
| **HyperMESH** | 117 | 31 | no | `docs/raw_research`=17, `docs/marketing`=7 |
| **CELL OS** | 103 | 18 | no | **`docs/marketing`=10**, `docs/evidence`=2 |
| **SIHRE** | 62 | 22 | no | `docs/raw_research`=17, `docs/_index`=4 |
| **Shadow Twin** | 38 | 20 | no | `docs/raw_research`=12, `docs/marketing`=4 |
| **CellBus** | 36 | 6 | no | `docs/marketing`=3, `docs/raw_research`=2 |
| **OS-MESH** | 17 | 1 | no | `docs/raw_research` |
| **T-MESH** | 13 | 5 | no | `docs/raw_research` |
| **CELL ADAPT** | 13 | 2 | no | `docs/raw_research` |
| **C-MESH** | 11 | 4 | no | `docs/raw_research` |
| **NERVE** | 11 | 2 | no | `docs/raw_research` |
| **Counterfactual Organization** | 10 | 6 | no | `docs/raw_research`=5 |
| **Mission Contract** | 10 | 9 | no | `docs/raw_research`=6 |
| **AI Operative** | 7 | 4 | no | spread |
| **Operative Cell** | 7 | 5 | no | `docs/marketing`=3 |
| **Cell Mesh** (title case) | 5 | 2 | no | `docs/design`, `docs/raw_research` |
| **CELL Mesh** (upper) | 5 | 1 | no | one file |
| **Mission DAG** | 5 | 5 | **1 — `factory/switchboard_p1.py`** | — |
| **Configuration Genome** | **1** | 1 | no | `docs/raw_research` |
| Domain Plane · Domain Fabric · Domain Data Plane · Domain Genome · DOMAIN-MESH · DOMAIN-DB · CELL-Q | **0** | 0 | no | ⛔ **absent** |

### 1.1 The three facts this table establishes

**⛔ 1.1.1 — The CELL OS vocabulary has zero presence in code.** Across 68 modules and 23,939 lines
of `factory/`, exactly **one** CELL OS term appears: "Mission DAG", once, in `switchboard_p1.py`.
The rename is not a code migration; it is a documentation migration.

**⭐ 1.1.2 — Marketing is ahead of architecture, and both are ahead of code.** `docs/marketing/` is
the top directory for CELL OS (10 of 18 files), Operative (7 of 17), CellBus (3 of 6) and second for
HyperMESH (7 of 31). The launch package uses the new vocabulary fluently for a system whose canonical
architecture is in an unopened ZIP and whose code uses none of it.

⚠ **`docs/marketing/cell-os-launch-v1/claim-ledger.md` is the mitigating fact** and it should be
read before anyone treats this as a problem: it exists precisely to bind each claim to a status
label. Marketing running ahead **with a claim ledger** is disciplined; the risk is that the ledger's
vocabulary and the brief's `PROVEN`/`SPECIFIED`/`PROPOSED` vocabulary are two systems for one job.
**Reconcile them, don't stack them** (`04` §8).

**⛔ 1.1.3 — Seven terms have zero occurrences**, and one has a single occurrence. See §4.

---

## 2. Supersession table

**Canonical** column follows `CELL_OS_Canonical_Terminology_vNext.md` — recovered from
`CELL_OS_Frontier_Audit_Research_Pack_2026-09-02.zip` (SHA-256 `6cc48dc65fa3a922`),
`01_CANONICAL_ONTOLOGY/`. ⛔ **That file is not on disk; nothing in the repository can grep its own
canon.** Surfacing it is Batch 2.

| Existing term | Intended meaning | Canonical term | Action | Affected files |
|---|---|---|---|---|
| Agent Factory | The whole system/product | **CELL OS** | **DEFER** — see §6 | 360 |
| Agent Army | A large multi-agent collection | **Cell Mesh** / **Organization** | **DEFER**; ⚠ also the name of the *sibling repo* | 88 |
| agent (bare) | Conventional LLM agent | **agent** — ⛔ **KEEP** | ⛔ **NO CHANGE** | 603 |
| AI Operative | CELL OS runtime entity | **Operative** | **NORMALISE** — drop "AI" | 4 |
| Operative Cell | Bounded mission unit | **Cell** | ⚠ **UNRESOLVED** — canon flags it | 5 |
| Cell Mesh | Team/topology of Operatives | **Cell Mesh** ✅ | KEEP | 2 |
| CELL Mesh (federation sense) | OS-to-OS federation | **CELL OS Federation Link** / **OS-MESH** | ⭐ **RENAME** — the collision | 1 |
| C-MESH / T-MESH / OS-MESH | Intra-cell / team / org meshes | ⚠ **UNRESOLVED** | AUDIT | 4 / 5 / 1 |
| HyperMESH | Cognition/memory substrate | **HyperMESH** ✅ | KEEP, audit sublabels | 31 |
| NERVE | Human operating surface | **NERVE** ✅ (*Navigation, Execution, Routing, Verification & Escalation*) | KEEP | 2 |
| Switchboard | The built projection + action surface | ⚠ **UNRESOLVED** — see §3 | ⛔ **DO NOT RENAME** | 139 |
| **Configuration Genome** | Versioned config that IS the version | ⭐ **Cell Blueprint / Cell Genome** | **REJECT the brief's term** — §4 | 1 |
| CELL ADAPT | Config optimization from replay | **Evolution Chamber** / **Organizational Architecture Search** | ⚠ UNRESOLVED | 2 |
| SIHRE | Cognitive kernel | ⛔ **expansion undefined** — §5 | AUDIT | 22 |
| CellBus | Typed internal event fabric | **CellBus** ✅ | KEEP | 6 |
| Shadow Twin | Contained candidate config | **Shadow Cell / Shadow Twin** ✅ | KEEP | 20 |
| Counterfactual Organization | Compare org configs | ⚠ not in canon | AUDIT | 6 |
| Mission Contract | Human-intent agreement | **Intent Contract / Mission Contract** ✅ | KEEP | 9 |
| Mission DAG | Execution graph | **WorkGraph / Mission DAG** ✅ | KEEP | 5 |
| Domain Plane / Fabric / Data Plane / Genome, DOMAIN-MESH, DOMAIN-DB | — | ⛔ **not in canon** | **CANNOT ACT** — §4 | **0** |
| CELL-Q | Quant domain | ⛔ **not in canon** | **CANNOT ACT** — §4 | **0** |

---

## 3. Collisions

### ⭐ 3.1 Cell Mesh vs CELL Mesh — the collision the brief predicted, already documented

The brief asks me to *"flag collisions, especially any older use of 'CELL Mesh' for federation that
conflicts with the newer use of 'Cell Mesh' as a team or topology."* **It is real, and the project
already found it.**

`KNOWN_TERMINOLOGY_COLLISIONS.md` (inside the ZIP), row 1:

> | Cell Mesh / CELL Mesh | Used both for an Operative-team topology and for OS-to-OS federation in older material | Reserve Cell Mesh for Operative teams and rename federation? |

And the canonical ontology answers it directly:

> **Cell Mesh** — *"A coordinated team/topology of Operatives. **A Cell Mesh is not OS federation.**"*
> **CELL OS Federation Link** — *"A governed relationship between independent CELL OS environments.
> **Do not call this Cell Mesh.**"*

**Where the old sense survives — exactly one file, five occurrences:**

```bash
grep -rn "CELL Mesh" docs/
# docs/raw_research/CELL_OS_Product_Technical_Design_v0.1_Crossreference_Audit_v1.md:18,72,91,102,420
```

That file *is* the audit that found the collision (*"the name collides with C-/T-/OS-MESH
terminology… RENAME + REFRAME"*), recommending the v0.1 section become **"OS-MESH Federation
Fabric"**.

**⭐ The real problem is not the collision. It is that the fix is unreachable.** The audit names a
section of `CELL_OS_Product_Technical_Design_v0.1.docx` — **which cannot be read here**. So the
repository holds a rename instruction, the register recording it, and the canonical resolution, and
**cannot apply any of them to the document they target.**

**Action:** Batch 2 converts the `.docx`; the rename becomes actionable then. ⛔ **Do not rename in
the audit file** — it is a *record of the old usage*, and editing it destroys the evidence.

### 3.2 Switchboard vs NERVE — ⛔ do not rename

| | Switchboard | NERVE |
|---|---|---|
| Occurrences | **1,442** in 139 files | **11** in 2 files |
| In code | ⭐ **Yes** — `switchboard.py`, `switchboard_p1.py`, `switchboard_render.py` = **3,403 lines** | **No** |
| Tests | `tests/test_switchboard_p1.py` and others | none |
| Branches | `switchboard/p0`, `switchboard/p0-autonomy`, `switchboard/p1` — **one checked out in a live worktree** | none |
| Scripts | `render_check_switchboard.py`, `_p1.py`, `switchboard_dev.py` | none |
| Commands | driven via `af-*` | none |

**Recommendation: `Switchboard` is the implementation, `NERVE` is the product surface it may become.
They are not synonyms yet and should not be merged by a rename.** Renaming 3,403 lines of tested,
branch-active code to match an 11-occurrence aspiration is the highest-risk, lowest-value action
available in this whole restructure — and one live worktree sits on `switchboard/p0`.

⚠ Note the operator has said Switchboard is not needed for the tracker workflow (`04` §8.6). **That
is a reason not to invest in it, not a reason to rename it.**

### 3.3 Operative Cell vs Cell — UNRESOLVED

Canon flags it (*"Is there a real semantic distinction or should one be retired?"*) and does not
decide. 7 occurrences / 5 files, mostly `docs/marketing/`. **Leave both; do not guess.**

### 3.4 "agent" — ⛔ do not touch

8,594 occurrences in 603 files. The brief is explicit: *"Do not globally replace the word `agent`."*
It is correct in at least five senses here — conventional agents, external frameworks (Moise+,
JaCaMo, MCP, A2A, AGNTCY), historical material, comparisons, and **`factory/` code and API names**.
Canon agrees: *"Define Agent as industry baseline and Operative as CELL OS runtime entity."*

⭐ A global replace would also corrupt `docs/raw_research/` (201 files), which is **immutable**.

---

## 4. ⛔ Terms the brief names that the project does not have

| Term | Occurrences | In canonical ontology? | Verdict |
|---|---:|---|---|
| Domain Plane | 0 | ❌ | ⛔ **Not a project term** |
| Domain Fabric | 0 | ❌ | ⛔ Not a project term |
| Domain Data Plane | 0 | ❌ | ⛔ Not a project term |
| Domain Genome | 0 | ❌ | ⛔ Not a project term |
| DOMAIN-MESH | 0 | ❌ | ⛔ Not a project term |
| DOMAIN-DB | 0 | ❌ | ⛔ Not a project term |
| CELL-Q | 0 | ❌ | ⛔ Not a project term |
| **Configuration Genome** | **1** | ❌ — canon says **"Cell Blueprint / Cell Genome"** | ⭐ **Superseded before adoption** |

**⭐ 4.1 — "Configuration Genome" should be rejected, and this is the sharpest terminology finding
in the audit.** The brief asks for `packages/configuration-genome/`. The term has **one occurrence
in one file**, and the project's own canonical ontology **does not contain it** — it names that
concept **Cell Blueprint / Cell Genome**:

> **Cell Blueprint / Cell Genome** — *"The declarative, versioned source specification describing how
> a Cell should be constructed: roles, Operatives, topology, links, capabilities, memory, authority,
> resource policy, assurance, lifecycle and adaptation policy."*

⭐ **And the capability is already built under a third name.** `factory/blueprint.py` implements
`AgentSpec` / `TeamSpec` — *"the config that IS the version"* (`README.md` §VII) — with instances in
`blueprints/*.yaml` and a fan-in of 6. So the concept has **three names**: `blueprint` (in code),
`Cell Blueprint / Cell Genome` (in canon), `Configuration Genome` (in the brief).

**Recommendation: adopt `Cell Genome` as the canonical term, keep `blueprint` in code, and do not
introduce `Configuration Genome` at all.** Adding a fourth name to a three-named concept makes the
ambiguity worse, and canon's own closing rule is *"terminology should reduce ambiguity, not merely
sound distinctive."*

**⛔ 4.2 — The seven zero-occurrence terms cannot be superseded, renamed or adopted.** There is
nothing to act on. `04_PROPOSED_TARGET_STRUCTURE.md` §1 declines to create packages for them; §5
defines the quant boundary in one document instead of a `domains/` tree.

⚠ **Honest caveat, because a zero from a blind instrument is not a measurement.** The scan reads
**text** files. Four CELL OS binaries totalling 669 KB are unreadable here (two `.docx`, one
`.xlsx`, one `.pdf`), and 32 ZIPs were namelist-scanned only. **Several of these seven are plausibly
defined in `CELL_OS_Product_Technical_Design_v0.1.docx`.** For those the correct verdict is
**`NOT-VISIBLE`, not `ZERO`** — and Batch 2's conversion is what resolves it. **Do not create a
package for a term on the strength of a verdict this document marks provisional.**

---

## 5. ⚠ SIHRE — an acronym with no expansion

62 occurrences across 22 files, including 8 research prompts and a whole consolidation pack. **The
repository never says what it stands for.**

```bash
grep -rIn -iE "stands for|acronym" docs/raw_research/agent2_sihre_consolidation_pack/   # 0 hits
```

The pack describes it functionally — *"SIHRE as a domain-general heterogeneous reasoning framework"*,
*"SIHRE can serve as the cognitive kernel of this entity"* — and never expands it. It is also
**absent from `CELL_OS_Canonical_Terminology_vNext.md`**.

**Action: `AUDIT`.** Either expand it in the canonical terminology file or record explicitly that it
is an opaque proper noun. An acronym that 22 files use and none defines is a term whose meaning lives
only in someone's head — the failure mode this whole restructure is organised against.

Same class, smaller: **"OPC"** in `docs/diagrams/CELL OS - Building your first OPC.png` appears
**nowhere else in the repository**. Most likely *Operative Cell*. **UNRESOLVED — do not guess.**

---

## 6. ⭐ Recommendation: defer the rename entirely

**Do not perform the Agent Factory → CELL OS rename in Phase 2.** Four measured reasons:

1. **The canonical ontology is not yet greppable.** It sits inside a ZIP. A rename executed against
   a canon nothing can search is a rename executed against memory.
2. **Three collisions are unresolved by the canon itself** — Operative Cell vs Cell, HyperMESH
   sublabels, C-/T-/OS-MESH. Canon poses them as questions. Renaming now picks answers the project
   has not chosen.
3. ⛔ **The largest single population is immutable.** `docs/raw_research/` holds 105 of 360
   "Agent Factory" files and 33 of 88 "Agent Army" files. The brief forbids altering it. **A rename
   can therefore never be complete**, and a half-done rename is worse than none — it removes the
   ability to tell old material from new by its vocabulary.
4. ⚠ **The sibling repository is named `agent-army-research`** and is *"the authoritative home of
   Agent Army research"* (155 md files). Renaming here alone splits the programme's language across
   two repos. **Decision D-4.**

**Instead, Phase 2 does four cheap, reversible things:**

| # | Action | Cost |
|---|---|---|
| 1 | Surface the two ontology files so the canon is greppable | 2 file reads |
| 2 | Add a terminology section to `docs/architecture/canonical/README.md` mapping code names ↔ canon names, **renaming nothing** | 1 file |
| 3 | Record the 4 unresolved collisions (Operative Cell, mesh sublabels, SIHRE, OPC) as open questions | in the same file |
| 4 | Adopt canon vocabulary **in new documents only** | free |

⭐ **The crosswalk is what a rename is actually for.** A reader hitting `blueprint.py` needs to know
it is the Cell Genome. That is a lookup table, and it costs one file instead of 1,651 edits across
360 files — 105 of which are immutable and could never be edited at all.

---

## 7. Method and limits

**Measured:** 31-term regex census over 1,001 text files (`scratchpad/term_scan.py`); per-term
directory concentration; `factory/` presence by path prefix; both canonical ontology files read in
full from inside the archive; targeted greps for "CELL Mesh", SIHRE expansion, and OPC.

**Not measured:** the four unreadable CELL OS binaries (669 KB) and 32 ZIP interiors. **This is the
governing limit on §4** and every zero there is provisional until Batch 2.

**Not attempted:** any rename, any edit to `docs/raw_research/`, any resolution of a collision the
canonical ontology leaves open.
