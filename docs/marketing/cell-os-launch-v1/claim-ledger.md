# CELL OS launch film — claim ledger

**Built before the script, per `launch-narrative` Phase 0.** Every noun the film speaks or displays
has a row. A row with no evidence path is `VISION` by default, never `SHIPPING` by optimism.

Status vocabulary: `SHIPPING` · `MEASURED` · `PREVIEW` · `VISION` · `REFUTED`.

---

## 0. The fact that governs every row

```bash
python -c "import json;r=[json.loads(l) for l in open('.data/runs.jsonl',encoding='utf-8')];print(len(r),sum(1 for x in r if x.get('outcome')=='PASS'))"
# 10 0
python -c "import json;e=[json.loads(l) for l in open('.data/events.jsonl',encoding='utf-8')];a=[x for x in e if x.get('kind')=='agent_returned'];print(len(a),sorted({str(x.get('dry_run')) for x in a}))"
# 7 ['True']
```

⛔ **No agent has ever completed a real, non-dry-run run in this system.** `README.md` states this in
Part 0, above every other claim, deliberately.

**Consequence for the film, and it is not negotiable:** nothing on screen may depict a *completed
mission* as a present fact. No "1,284 missions run". No success-rate counter. No customer logos. The
film's subject is an **architecture**, and architecture is legitimately presented in the design
register. The moment it borrows the operational register it is false, and falsifiable by anyone who
reads the first screen of the repository.

---

## 1. The ledger

| # | Claim as the brief states it | Repo evidence | Status | Permitted phrasing |
|---|---|---|---|---|
| C1 | An Operative is an agent plus identity, memory, capability, permission, context, tools, evidence, budget | `factory/context.py`, `evidence.py`, `presets.py`; "operative" in 22 files; `README.md` Part III defines the term | **VISION (definitional)** | A definition is not a deployment claim. *"An Operative **is** …"* is permitted — it defines a unit, it does not assert a running system |
| C2 | A Cell is Operatives assembled for one mission | ⛔ `current_vs_proposed.md:270` — Mission Assembly Plan **Specified only**. *"No mission object, schema or lifecycle exists."* `grep -rniE "swarm"` → 1 line, no mechanism | **VISION (definitional)** | Definitional only. Never *"Cells run"*, *"Cells coordinate"* in the indicative |
| C3 | CELL OS is the control layer for artificial organizations | no such runtime exists | **VISION** | *"is built for"*, *"is designed as"* |
| C4 | Org-IR / mission compiler — intent compiles to an organization | `current_vs_proposed.md:107` Research ● Designed ● Specified ●, nothing built. Seed schema marked *seed only*. ⚠ **Category itself contested — `contradictions.md` CN-01** | **VISION ⚠ contested** | *"is designed to compile"*. ⛔ Never *"compiles"*. On-screen maturity chip mandatory |
| C5 | Elastic topologies — cells expand, specialise, collapse | `current_vs_proposed.md:109` topology-as-data Research ● Designed ●. Contrast: `blueprints/orchestrator_team.yaml` — a 3-agent team **built, tested and REJECTED on evidence** (line 103) | **VISION** | *"can expand"*, *"can collapse"*. ⛔ Never imply a multi-agent formation is known to work here — the one we built was rejected |
| C6 | HyperMESH — context as virtual memory, retrieve/authorize/rank/compress/mount | `current_vs_proposed.md:163` Research ● Designed ● Specified ●. ⚠ *"The most contested concept in the corpus"* — `contradictions.md` CN-03 | **VISION ⚠ contested** | *"is designed to work like"*. ⛔ Never *"treats"*, *"mounts"*, *"streams"* in the indicative |
| C7 | Cell Kernel — capability syscalls pass identity, capability, budget, policy, evidence, human authority | Partly real: 30 readiness gates (`factory.readiness.GATES`), `factory/tasks.py:163` raises `EvidenceRequired`. ⛔ But `factory/preflight.py` is **WARN-ONLY; it refuses nothing** (`current_vs_proposed.md:160`) | **MIXED — gate exists, refusal does not** | *"can pass through"* — exactly the brief's own wording, which is already correct. ⛔ Never *"blocks"*, *"denies"*, *"prevents"* |
| C8 | Human authority gate | Design-level. Human gating is estate doctrine, not an enforced runtime path | **VISION** | *"and a human"* — as a list member, not as a mechanism demo |
| C9 | A claim of completion is not an outcome | ⭐ `factory/tasks.py:163` raises `EvidenceRequired`; `factory/evidence.py` classes `TARGET/CONSUMER/REGRESSION/ROLLBACK` with states `SATISFIED/ASSERTED/ABSENT`; graded **Implemented ● Validated ●** (`current_vs_proposed.md:57`) | **MEASURED** | Present indicative permitted. This is one of two rows in the film that has earned it |
| C10 | The verdict lattice — `PASS / FAIL / UNMEASURABLE / ERROR / NOT_RUN` | ⭐ `factory/contract.py:31-37`. Five verdicts, never collapsed. Grounded in ISO/IEC 9646 and TTCN-3 (ITU-T Z.140 §24.2), lattice `none < pass < inconc < fail < error`, ERROR dominates FAIL | **MEASURED** | Present indicative permitted. **This is the film's anchor** — see §3 |
| C11 | `VERIFIED_SUCCESS` as a mission state | ⛔ `grep -rn "VERIFIED_SUCCESS"` across the repo → **0 hits.** The token does not exist | **REFUTED — removed** | ⛔ Does not appear in the film. Replaced by C10, which is real, standards-grounded, and better |
| C12 | `RED → GREEN` mission transition | `.data/runs.jsonl` holds **0 `PASS`**. A green mission has never happened here | **REFUTED as depicted — removed** | ⛔ No red-to-green animation. The lattice replaces it |
| C13 | Shadow Twin — fork a Cell, run a counterfactual organization | `current_vs_proposed.md:129` Research ● Designed ●. ⚠ **Not the same object as `factory/assertions.py`'s `Counterfactual`**, which has no `status` field and is deliberately un-renderable beside a real outcome — a *documentation* object. *"The two must not be conflated"* | **VISION** | *"Fork a Cell"* as an imperative of intent, with the maturity chip on screen. ⛔ Never cite `assertions.py` as its implementation |
| C14 | Evolution Chamber — competing formations scored on a Pareto surface | `current_vs_proposed.md:183` Research ● Designed ●. *"refused by the same unlock as the optimizer"* | **VISION — deliberately gated** | *"becomes something you can measure"* is future-facing enough to pass. Chip mandatory. ⛔ No axis on the Pareto plot carries a number |
| C15 | Many Cells operate a function; one operator directs a synthetic organization | 0 real runs; the one multi-agent blueprint was rejected on evidence | **VISION** | *"could direct"*. ⛔ Never *"directs"*, *"operates"*, *"runs"* |
| C16 | Mission montage — eight objectives compile into eight formations | `docs/research/backlog.yaml` holds **31** candidate mission ids. ⛔ *"Nothing dispatched"* | **VISION** | Objectives shown as **typed input**, never as completed runs. No checkmarks, no durations, no costs |
| C17 | Rendered client-facing artifacts | ⭐ `factory/client_review*.py`, `switchboard*.py`; `docs/evidence/switchboard-p1-2026-09-01/`, `client-review-readiness-2026-09-01/` — `RENDERED_CONFIRMED`, real Chromium, both schemes | **MEASURED** | Not in the 90s cut. ⭐ **Recommended for the extended cut** — it is real, and it is the only thing in the estate a viewer could be shown working today |
| C18 | Connector GreenContract A1–A12 scores 12/12 | `factory/connector_contract.py`; **REPLAYED against one recorded run**; 48 connectors never scored; sensitivity ≠ coverage (`docs/findings.d/F76`) | **PREVIEW** | Only with *"replayed against one recorded corpus"* attached in the same frame. Not in the 90s cut |

---

## 2. The disclosure mechanism — the maturity chip

The brief asks for research-stage capability to read as vision rather than as deployment. A trailing
legal disclaimer does not achieve that; nobody reads frame 2,160. **Put the status in the frame that
makes the claim.**

A persistent chip, lower-left, 11px mono, `+8%` tracking, 42% opacity rising to 70% on state change:

```
● DESIGNED      the subsystem on screen is specified, not built     (C4 C5 C6 C13 C14 C15 C16)
● IMPLEMENTED   the code exists and is tested                       (C7, partially)
● VALIDATED     it ran here, on real state, and was observed        (C9 C10 C17)
```

⭐ **This is the single best creative decision available in this brief.** A film about a platform
whose thesis is *"do not confuse a declaration with a mechanism"* that labels its own maturity
frame-by-frame is not hedging — it is a demonstration. It is also the one thing in the film that no
competitor's launch video can copy without contradicting itself, which is the definition of
defensible positioning.

Shots carrying `● VALIDATED` — 22, 23, 24 — should be graded one stop brighter than the `● DESIGNED`
shots. The film gets visibly more solid as it moves from what is designed to what is measured. The
grade carries the argument.

---

## 3. The finding the brief did not know it had

The brief orders eight mechanism reels and buries the evidence reel seventh. **Reel 5 (shots 22–24)
is the only reel in the film that is built, tested, validated and standards-grounded** — and its
content is stronger than anything invented for it:

> Five verdicts, never collapsed. `PASS`, `FAIL`, `UNMEASURABLE`, `ERROR`, `NOT_RUN`.
> A check whose instrument could not run **has not passed.**
> — `factory/contract.py`, paraphrasing its own docstring

`UNMEASURABLE` is the category-defining object in this entire product, not `Cell`. Every competitor
can claim orchestration. None of them ship a verdict that means *"the thing that was supposed to
measure this could not see."* The recommendation carried into the shooting script:

1. Reel 5 gets the most screen time of any reel (**8.0s**) and the film's only full musical resolution.
2. The invented `VERIFIED_SUCCESS` / `RED → GREEN` sequence is cut (C11, C12) and its seconds are
   given to the real lattice.
3. `UNMEASURABLE` is the one label in the film that is allowed to sit alone on screen in silence.

---

## 4. Refused

Written down so the refusals are auditable, not invisible:

- `VERIFIED_SUCCESS` — token does not exist (C11).
- `RED → GREEN` mission transition — 0 `PASS` rows in the ledger (C12).
- Any count of missions, agents, hours saved, or success rate — no basis exists.
- Any customer name, logo, or testimonial.
- Any frame implying a multi-agent formation is known to work in this estate — the one that was built
  was **rejected on evidence** (C5).
- `assertions.py`'s `Counterfactual` as the Shadow Twin's implementation — different object, and the
  corpus explicitly forbids conflating them (C13).
- The word "autonomous" unqualified, anywhere.
