# Artifact Generator — architecture proposal

**Written 2026-09-01. Architecture only. No production code changed.**
**Fixture:** `docs/case-studies/delivery-001-marketing-model.md` (2,206 lines).
**Gate:** human architecture approval before any implementation.

---

## 0. The recommendation in one paragraph

**Do not build an Artifact Generator.** `factory/client_review.py` already is one — canonical state
plus an authored narrative, folded into a typed view model, projected through an allow-list, handed
to a renderer that emits self-contained themed HTML with a presentation mode. It is 738 lines, it
works, and it is the exact five-layer pipeline the brief sketches. The correct move is to **extract
its two generic organs, add three contracts that Delivery #001 proves are missing, and add one
second artifact type.** Four new modules, one refactor, one authored fixture, one test file. No
service, no database, no template engine, no markdown parser, no `ArtifactSpec` DSL.

---

# 1. Repository-grounded existing-state inventory

## 1.1 The pipeline that already exists

`MEASURED` — read in this session, with line citations.

```
.data/tasks.jsonl          append-only, 217 events        }
.data/missions/*.json      mission record + contracts     }  CANONICAL STATE
files on disk              evidence artefacts             }
missions/.../*.yaml        authored narrative (262 lines) }  AUTHORED NARRATIVE
        |
        |  client_review.assemble()                 factory/client_review.py:397-547
        v
ClientReview dataclass     typed view model           factory/client_review.py:331-368
  + Outcome / EvidenceItem / Decision / Risk / NextItem   :271-329
  + diagnostics (operator-only, structurally unprojectable)
        |
        |  .to_client_dict()  -> client_safe() per section   :347-368, :172-184
        v
client-safe payload
        |
        |  client_review_render.render_html(cr)     factory/client_review_render.py:486
        v
self-contained HTML        docs/artifacts/client-review-navira.html (378 lines)
```

**The brief's proposed architecture and the shipped code are the same shape.** The brief calls the
layers Adapter / Compiler / View Model / Renderer; the code calls them `assemble()`, `ClientReview`,
`to_client_dict()`, `render_html()`. There is no architectural gap to close — only a genericity gap.

## 1.2 What is already generic and is currently trapped inside one artifact type

| Organ | Where it lives now | Generic? | Evidence |
|---|---|---|---|
| **Client-safe allow-list boundary** — `CLIENT_SAFE`, `client_safe()`, `_scan()`, `_FORBIDDEN_SUBSTRINGS`, `LeakError` | `client_review.py:117-184` | **Fully.** Nothing in it is review-specific except the section names | `:172-184` takes `(section, row)` and is already table-driven |
| **Grounding gate** — `GROUNDED / CLAIMED / UNGROUNDED / UNSUBSTANTIATED`, `is_guarded()`, `ground()`, `enforce()` | `client_review.py:190-233` | **Fully.** Operates on `(refs, evidence rows, root)` | `:199-221` — two independent halves: file resolves **and** a task-evidence row carries a `USABLE` basis |
| **Freshness** — `LIVE / LAST_VERIFIED / STALE / UNAVAILABLE`, `freshness()` | `client_review.py:239-258` | **Fully.** Takes a timestamp and a readability flag | `:57-60`, `:100-101` |
| **Origin** — `CLIENT / FACTORY_PROPOSED` | `client_review.py:74-75` | **Fully.** Applies to any artifact that mixes what the client asked for with what we proposed | validated at `:454` |
| **Renderer chrome** — theme-aware CSS with all three theme states, `?mode=meeting`, escaping, section helpers | `client_review_render.py:78-350` | **Mostly.** `_CSS` at `:78`, dark at `:99-112`, meeting mode at `:336` (localStorage `cr-meeting`), `e()` escape at `:51` | section renderers `_delivered/_decisions/_risks/_next/_stages` at `:367-484` are type-specific |
| **Semantic-state visual register** — `_GRADE` (`:29-33`) renders **3** states as a left gutter ledger; `UNSUBSTANTIATED` is **not a grade** but a status flag (`:400-401`) whose explanatory note is `.opsonly`, hidden in meeting mode | `client_review_render.py:29-40` | **Pattern.** `_FRESH`/`_GRADE`/`CHIP` are all state→(css-class,label) dicts | the pattern generalises; the specific tables do not |
| **Counting-basis discipline** — `_completion()` declares its population before counting | `client_review.py:548-583` | **Pattern, not code.** Must be re-applied per artifact | `:557-571` — the comment block naming the 8-vs-10 basis decision |
| **Source-defect reporting** — `mission_integrity()` | `client_review.py:584-633` | **Fully.** "A defensive calculation that silently absorbs a source defect is how that defect becomes permanently invisible" | `:592-598` |

## 1.3 Canonical state modules an artifact layer would read

`MEASURED` — module list from `ls factory/` (50 modules, flat, no subpackages).

| Module | Supplies | Used by client_review today? |
|---|---|---|
| `factory/tasks.py` | `TaskStore` over `.data/tasks.jsonl`; `Task` with `status / parent / blocked_by / evidence / events`; states `OPEN CLAIMED BLOCKED DONE ABANDONED`; `close(require=)` → `EvidenceRequired` | **Yes** — `:412-419` |
| `factory/evidence.py` | classes `TARGET/CONSUMER/REGRESSION/ROLLBACK`; states `SATISFIED/ASSERTED/ABSENT`; `USABLE = ("MEASURED","DERIVED")`; `Coverage`, `coverage()` | **Yes** — the grounding states are aliases of the evidence states (`:66-68`) |
| `factory/findings.py` | reads `docs/findings.md` **union** `docs/findings.d/*.md`. `Finding` requires `BELIEVED / ACTUALLY / MEASURED BY / AFFECTS` (`findings.py:31`) with a `missing` property | **No** — unused by the review, and a **direct precedent for `Issue`** |
| `factory/events.py` / `runs.py` | 9 closed event kinds with mandatory verdicts; `RECORDED/RECONSTRUCTED/NOT-RECORDED` | **No** — and Delivery #001 wrote to neither |
| `factory/claims.py` | resource locks in `.data/claims/*.json` (⚠ **a lock, not an assertion** — the name is already taken) | **No** |
| `factory/contract.py` | five verdicts incl. `UNMEASURABLE` kept out of `FAIL` | **No** |
| `scripts/local_tracker.py` | 2,882 lines, stdlib `http.server`, 9 operator-facing tabs | **No** — separate surface |

## 1.4 What the mission pack demands, and what already satisfies it

`DOCUMENTED` — `missions/client-review-v1/`.

- **Live Meeting mode** exists and is specified in three places (`02-CLIENT-REVIEW-SPEC.md:11-15`,
  `04-DEFINITION-OF-DONE.md:16`, `05-CLIENT-REVIEW-DEMO-RUNBOOK.md:18`) and is **implemented**:
  *"the button top-right, the `m` key, or `?mode=meeting` in the URL"*, matching
  `client_review_render.py:336`. **This is a renderer presentation mode, and it already generalises.**
- **Degrade gracefully** (`02-CLIENT-REVIEW-SPEC.md:147`) is implemented as the optional-source
  contract in `assemble()`: *"A missing task store yields `UNAVAILABLE` freshness and ungrounded
  outcomes — a degraded but honest review — rather than an exception"* (`:405-407`).
- `docs/specs/client-review-loop-v0.md` reserves scope authority: *a review may PROPOSE; only
  explicit approval updates approved scope.* `client_review.py`'s docstring already honours this and
  says so.

## 1.5 What does not exist — measured, not assumed

| Absent thing | Command | Result |
|---|---|---|
| Intent Contract object | `grep -ril intent_contract factory/ scripts/` | **0 files** |
| Any schema/template/contract versioning | `grep -rn "SCHEMA_VERSION\|CONTRACT_VERSION\|TEMPLATE_VERSION\|__version__" factory/ scripts/ --include=*.py` | **1 hit**, and it is the package version: `factory/__init__.py:2  __version__ = "0.1.0"`. No schema, contract or template versioning exists |
| Any golden-file / snapshot test pattern | `grep -rln "golden\|snapshot\|.expected" tests/` | **0 files** across 44 test files |
| A second combined projection | modules read | only `client_review.py` folds multiple sources |
| A persisted compiled artifact / manifest / cache | `.data/` listing | **none of a cross-module projection.** One narrow exception: `readiness.py:617` caches suite results to `.data/suite-cache.json` |
| Memory service / vector store / RAG | `RECON.md` §1 | **none.** Sole runtime dep is `pyyaml` |

---

# 2. The finding that decides the architecture

**`client_review.py` is not "a client review feature". It is an artifact compiler that happens to
have exactly one artifact type compiled into it.**

Three things prove it:

1. `assemble()` takes *paths*, not review-specific objects, and every source but the narrative is
   optional (`:397-407`).
2. `client_safe()` is table-driven on a section name (`:172-184`) — the table is the only
   review-specific part.
3. `render_html()` takes the typed view model and calls `to_client_dict()` itself (`:486-488`) — the
   allow-list is *inside* the render path, so a renderer physically cannot reach `diagnostics`.

So the architecture question is not "what should we build" but **"which two organs come out, and what
is the second artifact type?"**

⛔ **And there is a trap in the brief worth naming.** The instinct to build a generic
`ArtifactSpec`/`ArtifactCompiler`/`ArtifactManifest` platform *before* there is a second artifact type
is the same error the case study documents as `OBLIGATION_WRITTEN_IN_PROSE` — ceremony that describes
a capability instead of exercising one. **We have one artifact type today. Generalising from one
example produces a framework shaped like that one example, with extra nouns.** The proposal below
generalises from *two*, which is the minimum honest number.

---

# 3. Proposed architecture

```
                     CANONICAL STATE                      AUTHORED NARRATIVE
        .data/tasks.jsonl  (append-only, 217 events)      missions/*/reviews/*.yaml
        .data/missions/*.json                             missions/*/case-study/*.yaml
        docs/evidence/**, docs/case-studies/**            (prose the Factory cannot derive)
        docs/findings.d/**
                            |                                      |
                            +------------------+-------------------+
                                               |
                                    ARTIFACT COMPILER
                       client_review.assemble()   case_study.assemble()
                       - resolves every evidence ref against disk
                       - grades grounding from real task-evidence rows
                       - derives progress / freshness from event timestamps
                       - REFUSES on the validation rules in section 12
                                               |
                                    TYPED VIEW MODEL
                       ClientReview                CaseStudy
                                               |
                                    PROJECTION BOUNDARY
                       to_client_dict() -> projection.safe(section, row)
                       allow-list per section; diagnostics has no entry, so it cannot cross
                                               |
                                        RENDERER
                       client_review_render      case_study_render
                       shared: theme CSS, escaping, presentation mode, manifest footer
                                               |
                                     SELF-CONTAINED HTML
```

**Shared organs, extracted once:**

```
factory/projection.py     the allow-list boundary + leak backstop        (extracted, unchanged)
factory/assertions.py     grounding + freshness + temporal + counterfactual + maturity
                          (grounding/freshness extracted unchanged; three new contracts added)
```

**Why a package (`factory/artifact/`) is NOT proposed:** the repo is flat — 50 modules, no
subpackages. Two new flat modules match the surrounding code. A package would be the first of its
kind in the tree and buys nothing at this size.

## 3.1 "Why can this not simply be a module?" — answered for every new thing

| Proposed | Service? | DB? | Answer |
|---|---|---|---|
| `factory/projection.py` | No | No | It **is** a module — an extraction of `client_review.py:117-184`, byte-for-byte behaviour. It gets its own file only because it is a **security boundary** and deserves its own test file and its own review surface |
| `factory/assertions.py` | No | No | A module. Extraction plus three dataclasses. Cannot live in `claims.py` — **that name is taken by the resource lock** and conflating a lock with an assertion is exactly the confusion the case study documents |
| `factory/case_study.py` | No | No | A module, mirroring `client_review.py`. A second artifact type is a second `assemble()` + a second view model — not a plugin system |
| `factory/case_study_render.py` | No | No | A module, mirroring `client_review_render.py` |
| `missions/delivery-001/case-study.yaml` | No | No | A data file, exactly as `navira-marketing-model.yaml` is |
| Compiled HTML | No | No | A build output in `docs/artifacts/`, regenerable from source. **Never** read back as input |
| **Artifact registry / spec DSL / template engine** | — | — | **Not proposed.** Two artifact types do not need a registry. Revisit at four |
| **Artifact database** | — | — | **Not proposed, and specifically argued against** — see §5 |

---

# 4. Component responsibilities

| Component | Owns | Must never |
|---|---|---|
| `tasks.py` / `evidence.py` / `.data/*` | Delivery truth. Append-only | Be written by an artifact compiler |
| Authored narrative yaml | Prose the Factory cannot derive: client-facing wording, scene text, the *claim* half of a counterfactual | Assert an outcome status that evidence does not support — the compiler downgrades it |
| `projection.py` | The client boundary | Redact silently. `_scan()` **raises**, because a silent redaction hides a broken boundary (`:153-170`) |
| `assertions.py` | Grounding, freshness, temporal state, counterfactual strength, capability maturity | Know what a client review or a case study is |
| `case_study.py` / `client_review.py` | Folding sources into one typed view model; declaring counting bases; refusing on validation failure | Mutate state. Repair a source defect — `mission_integrity()` **reports, never repairs** (`:600-601`) |
| Renderers | Visual register per semantic state | Reach past `to_client_dict()`. Render a `SIMULATED` counterfactual in the same component as an observed outcome |

---

# 5. Source-of-truth boundaries

| Layer | Status | Rule |
|---|---|---|
| `.data/tasks.jsonl`, `.data/missions/*.json`, `.data/claims/` | **CANONICAL** | Append-only. Artifacts read; artifacts never write |
| Evidence artefacts on disk (`docs/evidence/**`, `docs/case-studies/**`) | **CANONICAL for their own content** | Referenced by path (+ anchor). **Never parsed** |
| Authored narrative yaml | **CANONICAL for wording and for authored judgement only** | Every factual claim carries `evidence_refs`. A claim whose refs do not resolve is downgraded, not published |
| Typed view model | **DERIVED** | In-memory. Never persisted as input |
| Client-safe payload | **DERIVED** | May be emitted as JSON for a consumer; never read back |
| Compiled HTML | **DERIVED, disposable** | Regenerable. If it disagrees with source, source wins |
| Manifest block in the HTML | **DERIVED** | Input paths + hashes + versions + `as_of`; the staleness detector |

### 5.1 The forensic markdown — the one genuinely contested boundary

The brief forbids markdown parsing and forbids a second truth store. Both are right, and together
they leave exactly one honest arrangement:

```
docs/case-studies/delivery-001-marketing-model.md
        CANONICAL for the long-form forensic narrative. Human-authored, human-reviewed.
        Referenced by  path#anchor.  NEVER parsed.

missions/delivery-001/case-study.yaml
        CANONICAL for the STRUCTURED claims the artifact renders:
        scenes, issues, counterfactuals, KPI baselines, temporal assertions.
        Every entry carries evidence_refs pointing INTO the markdown by anchor,
        and/or into .data/ task-evidence rows.
```

⛔ **This creates a real drift risk and the proposal must not pretend otherwise.** It is precisely the
`H20 / FIELDS.md` failure in the case study — *a contract document transcribed from a source and then
drifted from it*, five fields listed "current" against nothing that exists. So the arrangement is
only acceptable **with the anchor validator in P0**: every `path#anchor` must resolve to a real
heading in the real file, or compilation fails. That converts drift from silent to loud. Without the
validator, this boundary should be rejected and the yaml generated from the markdown instead.

**Staleness detection:** the manifest records a sha256 of every input. A compiled artifact whose
recorded hash differs from the current file is `STALE` and says so in its own footer.

---

# 6. Minimal canonical contracts

Only what Delivery #001 proves is needed. Suggested names from the brief are kept where they earn
their place and deleted where they do not.

## 6.1 Kept from the brief

### `EvidenceBasis` — extend the existing enum, do not invent one

`factory/evidence.py` already has `MEASURED / DERIVED / ASSUMED` validated at write time, and
`USABLE = ("MEASURED","DERIVED")`. The case study needed four more: `DOCUMENTED`, `INFERRED`,
`SIMULATED`, `NOT_RECORDED`, and the brief adds `ESTIMATED` and `CONTRADICTORY`.

```
MEASURED       ran a command against real state
DERIVED        computed from measured/documented, computation shown
DOCUMENTED     stated in a cited file — ONE HOP, and the hop is the point
INFERRED       reasoning, stated nowhere
ESTIMATED      a figure with a stated method and no measurement
SIMULATED      counterfactual. never observed
NOT_RECORDED   the record does not hold it. NOT zero
CONTRADICTORY  two sources disagree and neither wins yet
```

⚠ **`USABLE` must stay `("MEASURED","DERIVED")` and must not grow.** `DOCUMENTED` is one hop from
measurement and is honest for a case study — but if it entered `USABLE`, a `DOCUMENTED` claim would
promote a guarded word to `VERIFIED`. **The new bases are display vocabulary; the promotion gate is
unchanged.** This is the single most important line in the contract section.

### `TemporalAssertion` — ⛔ **CORRECTED: extend `factory/context.py`, do not invent this**

**My first draft of this section proposed a new dataclass. The inventory pass refuted it.**
`factory/context.py` already carries the temporal contract, and already *enforces* the exact rule
this proposal was written to add:

```
context.py:51-53   CURRENT   checked against its source, and it agreed
                   STALE     checked, and the source has moved since
                   UNVERIFIED never checked against its source   <-- the DEFAULT
context.py:88-90   confidence: MEASURED | DERIVED | STATED | ASSUMED
                   checked:    ISO date last checked against `source`. Empty means never.
context.py:109     if self.status == CURRENT and not self.checked:  -> REFUSES
context.py:21      "UNVERIFIED is the default status, not CURRENT."
```

⭐ **A ref cannot be called `CURRENT` without a date. That is `CLAIM_WITHOUT_AN_AS_OF`, already
built, already refusing.** It has three consumers today (`claims.py`, `lanes.py`,
`tests/test_context_pack.py`) and the case study is a fourth.

**And the miss is the finding.** I proposed inventing a contract the repo already had, in a proposal
whose own fixture names `KNOWLEDGE_AVAILABLE_BUT_NOT_CONSUMED` as the largest failure pattern — 8 of
37 issues. It was caught by an inventory sweep, which is the manual version of the Known-Failure
Preflight this document recommends building. **That is the strongest available argument for the
capability, and it should be recorded as such rather than quietly corrected.**

**Revised proposal — additive, ~25 lines:**

| Need | Existing | Action |
|---|---|---|
| basis vocabulary | `CONFIDENCE = MEASURED / DERIVED / STATED / ASSUMED` | **reuse** — and note it already distinguishes `STATED` from `ASSUMED`, which the case study wanted |
| as-of | `checked` + the `CURRENT`-requires-`checked` refusal | **reuse unchanged** |
| provenance | `source` (required, non-empty) | **reuse** |
| observed vs re-checked | one `checked` field only | **add** `observed` alongside `checked`; absence of `checked` renders "not re-checked" |
| superseded / refuted / contradicted | absent — only `CURRENT/STALE/UNVERIFIED` | **add** `SUPERSEDED`, `REFUTED`, `CONTRADICTED` to `STATUSES`, plus `superseded_by` |
| the case-study kinds | 8 kinds, none forensic | **add** `CaseStudyClaim` to `KINDS` |

⚠ **This edits a module with three live consumers, so it is a breaking-change risk the gate must
price.** Purely additive enum members and one new optional field should be safe; `test_context_pack.py`
passing untouched is the acceptance test. If the gate prefers isolation, the fallback is a thin
case-study-local subclass — but **not** a parallel vocabulary.

### `CapabilityCounterfactual` — the fix for the SIMULATED→PROVEN slide

```
capability          "Known-Failure Preflight"
strength            WOULD_BLOCK | WOULD_INTERCEPT | WOULD_WARN
                    | WOULD_PROVIDE_CONTEXT | MAY_REDUCE_LIKELIHOOD | NO_MATERIAL_EFFECT
maturity            EXERCISED | IMPLEMENTED_NOT_EXERCISED | SIMULATED | PROPOSED
basis               EvidenceBasis   -- SIMULATED unless maturity is EXERCISED
mechanism_refs      module:line for anything claimed IMPLEMENTED or EXERCISED
expected_effect     prose
remaining_human     what a human still decides
confidence          HIGH | MEDIUM | LOW, with a reason
```

⭐ **The structural guarantee the brief asks for, and how to get it for free.**
`CapabilityCounterfactual` **has no `status` field and no `grounding` field.** It is therefore not
duck-type-compatible with `Outcome`, and it physically cannot be passed to the delivered-outcomes
renderer. The anti-flattening rule is enforced by the type, not by a convention a future contributor
must remember. Two compiler rules complete it:

- `maturity == EXERCISED` requires at least one `mechanism_refs` entry **and** a resolvable
  task-evidence row with a `USABLE` basis. Otherwise → compile error.
- `maturity in (SIMULATED, PROPOSED)` forces `basis = SIMULATED` regardless of what the yaml says.

Delivery #001 baseline, `MEASURED`: Source Cartography and Intent Contract are
`IMPLEMENTED_NOT_EXERCISED` / `PROPOSED` — the cartography task R3 is the blocked one, and
`grep -ril intent_contract` returns 0. **The two capabilities the story most wants to celebrate are
the two least exercised.** The contract must make that visible, not smooth it.

### `CaseStudyScene` — see §7

## 6.2 Deleted from the brief, with reasons

| Concept | Verdict | Why |
|---|---|---|
| `ArtifactSpec` | **Delete for P0** | With two artifact types, the "spec" is the `assemble()` function signature. A declarative spec layer is a second way to say the same thing |
| `ArtifactViewModel` (as a base class) | **Delete** | `ClientReview` and `CaseStudy` share no fields. An empty base class is ceremony. They share *functions* (`projection`, `assertions`), which is the right kind of sharing |
| `ArtifactManifest` (as a module) | **Reduce to ~30 lines inside the renderer** | Input paths + sha256 + versions + `as_of`, emitted into the HTML. Real value, no module needed |
| `ArtifactClaim` | **Merge into `TemporalAssertion`** | Two names for one thing |
| Artifact registry / plugin loader | **Delete** | Two types. Revisit at four |

---

# 7. Forensic case-study model

The minimum contract that supports the nine scenes in the fixture and plausible future
retrospectives. Deliberately under-modelled.

```
CaseStudy
  delivery            id, name, client, subject, window
  companion           OPTIONAL link to the investigating delivery   <-- the A/B relationship
  summary             the executive rows
  timeline            [ TimelineStep ]
  issues              [ Issue ]
  patterns            [ Pattern ]          root patterns over issues
  scenes              [ CaseStudyScene ]
  kpis                [ KpiBaseline ]
  lessons             [ Lesson ]
  diagnostics         operator-only, no allow-list entry

TimelineStep
  id, order, occurred_at (+ precision: EXACT | DAY | MONTH | UNKNOWN)
  track               CLIENT_DELIVERY | FACTORY_MISSION      <-- keeps A and B unflattened
  intent, known, believed, assumed, unknown
  evidence_available  [ ref ]
  action_taken
  assertions          [ TemporalAssertion ]

Issue
  id, track, stage_introduced, stage_detected
  title, what_happened, why, root_causes[], mistake_types[]
  escape_distance     int | None, with the boundary model named
  still_open          bool
  client_risk         HIGH | MEDIUM | LOW | NONE
  counterfactual      CapabilityCounterfactual | None
  evidence_refs       [ ref ]

CaseStudyScene
  id, step_ref
  context, information_available   only what was knowable then
  question
  choices             [ { key, label, consequence, was_actual: bool } ]
  actual_outcome
  later_evidence                   revealed only after a choice
  counterfactual      CapabilityCounterfactual
  impact              { technical, client, company, kpi_ref }

KpiBaseline
  id, name, value | None, basis (EvidenceBasis), measurability, method, regeneration_command
```

### 7.1 The A/B relationship is a first-class field, not a convention

`track` on every `TimelineStep` and every `Issue`, plus `companion` on `CaseStudy`, is the whole
mechanism. It is one enum and one link, and it makes the brief's diagram renderable:

```
CLIENT DELIVERY (track=CLIENT_DELIVERY)  --investigated by-->  FACTORY MISSION (track=FACTORY_MISSION)
                                                                        |
                                                        reveals failure modes on BOTH tracks
                                                                        |
                                                                 drives Lessons
```

⛔ **The compiler must refuse a `CaseStudy` whose issues are all on one track.** Delivery #001 has 25
`CLIENT_DELIVERY` and 12 `FACTORY_MISSION` issues; a case study that renders only the first kind is
the "Agent Factory would have fixed everything" artifact the brief forbids. **Make it a validation
rule, not an editorial intention** — that is the brief's §5 turned into a mechanism, and the
recursion is the point.

### 7.2 What is deliberately NOT modelled

Branching narrative state, scoring, viewer persistence, multi-path outcomes. A scene has one actual
path and one counterfactual. The choices exist to make the reader commit before the reveal — not to
simulate alternate histories.

---

# 8. Client Review integration

**Answer to the brief's question:** Client Review becomes an **artifact type** — one compiler + one
view model + one renderer — with its projection boundary and grounding gate promoted to shared
modules. It is **not** rewritten, **not** wrapped, and **not** reduced to a "presentation mode".

| Brief's option | Verdict |
|---|---|
| Artifact Type | ✅ **This one.** `client_review.py` + `client_review_render.py`, unchanged in behaviour |
| Client-Safe Projection | ✅ **Extracted and shared** — `projection.py`. The case study gets the same boundary free |
| View Model | ✅ Already is one (`ClientReview`, `:331`) |
| Renderer | ✅ Already is one (`render_html`, `:486`) |
| Presentation Mode | ✅ Already exists (`?mode=meeting`, `:336`) and generalises to any renderer |

**Exact change to `client_review.py` in P0:** delete lines `117-184` and `190-258`; import the same
names from `projection` and `assertions`. Public API unchanged. `tests/test_client_review.py` must
pass **untouched** — that is the acceptance test for the refactor, and if it needs editing, the
extraction was wrong.

**Preserved without modification:** allow-list, freshness, evidence drill-down, Live Meeting mode,
acceptance computation, risks, decisions, evidence-grounded language, and the declared-set completion
basis with its `mission_integrity` warning.

---

# 9. Evidence, temporal and counterfactual semantics — where each is enforced

| Semantic | Enforced by | Failure mode it prevents |
|---|---|---|
| `USABLE` promotion gate | `assertions.ground()` — file resolves **and** a task-evidence row carries `MEASURED`/`DERIVED` | A guarded word becoming `VERIFIED` on prose |
| Guarded-word downgrade | `assertions.enforce()` → `UNSUBSTANTIATED` | "DEPLOYED" with nothing behind it |
| Four-state absence | `assertions.freshness()` | "no risks" from a register that could not be read |
| Absence ≠ zero | compiler: a `KpiBaseline` with `value is None` renders its `basis`, never `0` | `ABSENCE_RENDERED_AS_A_NUMBER` — 5 of 37 issues |
| As-of | `TemporalAssertion.observed_at` required; `rechecked_at` absence rendered | `CLAIM_WITHOUT_AN_AS_OF` — 6 of 37 |
| Counterfactual honesty | `CapabilityCounterfactual` has no `status` field → structurally cannot enter the outcomes renderer | `SIMULATED + UNEXERCISED` reading as `PROVEN` |
| Contradiction preserved | `CONTRADICTORY` basis requires ≥2 `sides[]`, each with its own refs | MER silently resolved to one direction |
| Client safety | `projection.safe()` allow-list + `LeakError` backstop | The 2026-08-31 deny-list credential exposure |
| Track balance | compiler refuses a single-track case study | "the Factory would have fixed everything" |

---

# 10. Delivery #001 as baseline #1 — honest KPI classification

`MEASURED` / `DERIVED` from this session and the fixture. **No numbers invented.**

| KPI | Verdict | Delivery #001 value | Basis |
|---|---|---|---|
| **Defect Escape Distance** | **DERIVABLE NOW** | median **3** (11 Delivery-A escapes); Factory-track median **2** (4 escapes) | `DERIVED` — fixture §D.3 |
| **Known-Failure Recurrence** | **MEASURABLE NOW** | **2** (M-01 blind zero, M-05 deny-list) | `MEASURED` |
| **Evidence Coverage** | **MEASURABLE NOW** | **2 of 8** declared tasks carry `MEASURED` evidence = 25% | `MEASURED` — `evidence.coverage()` exists |
| **Escaped Defects** | **DERIVABLE NOW** | 25 client-track issues with a recorded detection stage; **6 still open** (divergent objects) | `DERIVED` |
| **Time to First Verified Value** | **DERIVABLE NOW** (Factory track only) | mission created `00:52:14Z` → first `MEASURED` evidence `02:25:21Z` = **93 min** | `DERIVED` |
| **Blocked Time** | **PARTIALLY MEASURABLE** | R3 blocked from `00:52:14Z`, unresolved. Block events carry `ts`, so this is derivable **going forward** | `DERIVED`, incomplete |
| **Decision Latency** | **PARTIALLY MEASURABLE** | O-3 surfaced 2026-06-05, no answer ~3 months later. Derivable from documented dates; **no decision store exists** | `DOCUMENTED` |
| **Clarification Burden** | **PARTIALLY MEASURABLE** | 15 open client questions counted; round-trips not recorded | `DOCUMENTED` |
| **Rework** | **PARTIALLY MEASURABLE** | as *count*: H21 = 2 fix passes, H22 = 3 sessions. As *time*: `NOT_RECORDED` | `DOCUMENTED` |
| **Concurrent Delivery Capacity** | ⛔ **NOT MEASURABLE — the instrument is blind** | 3 claims exist, **all pid 17172**; R3 never claimed. The store cannot currently distinguish 3 sessions from 1 | `MEASURED` |
| **Delivery Predictability** | **REQUIRES NEW INSTRUMENTATION** | estimates exist (all `ASSUMED`); `actual_minutes` **does not exist for any task** | `MEASURED` absence |
| **Request → Accepted Production Outcome** | **NOT RECORDED** | no acceptance event type exists; **zero client sign-offs** in the whole corpus | `MEASURED` absence |
| **First-Pass Acceptance** | **NOT RECORDED** | same — and R1 C-35 proves the instrument *can* see acceptance, because it recorded GP-292's | `DOCUMENTED` |
| **Cost per Accepted Outcome** | **NOT RECORDED** | `runs.py` has a cost basis field; this mission wrote **zero** run rows | `MEASURED` absence |
| **Human Engineering Effort** | **NOT RECORDED** | none of spec §4's 13 instrumentation fields was written | `MEASURED` absence |
| **Reuse Rate** | **NOT RECORDED** | no recipe/pattern registry exists | `MEASURED` absence |
| **Onboarding Time** | **NOT RECORDED** | no instrumentation | — |

**Summary: 4 measurable/derivable now, 4 partial, 1 blind, 1 needs instrumentation, 7 not recorded.**
That is the honest baseline, and **publishing the gaps is the deliverable** — a Command Center
showing 17 green KPIs would be the `ABSENCE_RENDERED_AS_A_NUMBER` failure committed by the artifact
that documents it.

---

# 11. P0 / P1 / P2

## P0 — the vertical slice (recommended scope for the next session)

**One artifact, end to end, on real evidence: the Delivery #001 Interactive Forensic Case Study.**

```
1. EXTRACT   factory/projection.py      from client_review.py:117-184   no behaviour change
2. EXTRACT   factory/assertions.py      from client_review.py:190-258   no behaviour change
             + ADD CapabilityCounterfactual, Maturity, EvidenceBasis
             + ADD anchor resolution (path#anchor) to ground()
2b. EXTEND   factory/context.py        additive: SUPERSEDED/REFUTED/CONTRADICTED,
             `observed`, `superseded_by`, CaseStudyClaim kind.  DO NOT invent a
             parallel temporal contract - context.py already refuses CURRENT-without-a-date
3. REFACTOR  factory/client_review.py   import from 1 and 2; delete the extracted bodies
             ACCEPTANCE: tests/test_client_review.py passes UNTOUCHED
4. ADD       factory/case_study.py      assemble() + CaseStudy view model + validation rules
5. ADD       factory/case_study_render.py   renderer, reusing the theme CSS and meeting mode
6. ADD       missions/delivery-001/case-study.yaml   authored fixture: 9 scenes, ~15 issues,
             the 4 patterns, the KPI table, the A/B track split
7. ADD       tests/test_case_study.py   the 11 fixture assertions from section 13
8. OUTPUT    docs/artifacts/delivery-001-case-study.html
```

**Eight items. Four new modules. One refactor. Nothing else.**

⚠ **The scope call I am putting to the gate.** The brief names the *Delivery Command Center* with ten
sections as the first target. I recommend **P0 ships the forensic case study only**, because that is
the part backed by real evidence today. Six of the ten Command Center sections (Roadmap, Business
Value, Standardized Onboarding, Delivery Measurement across deliveries, Project Progress beyond one
mission, Executive Summary spanning deliveries) have **no second delivery to compare against** and
would be authored prose in a shell — the exact thing the case study calls
`OBLIGATION_WRITTEN_IN_PROSE`. **The Command Center becomes credible at Delivery #002.** If the gate
disagrees, the cheapest honest version is a Command Center whose non-evidenced sections render
`NOT_RECORDED` states rather than content.

## P1 — the reusable generator

- Third artifact type (Delivery Command Center) — proving genericity with **three** examples, not two.
- Extract the shared renderer chrome (`_CSS`, `e()`, meeting mode, manifest footer) into
  `factory/render_chrome.py` — **only once two renderers have diverged enough to show what is
  genuinely shared.** Extracting it in P0 would guess.
- Golden-artifact regression (§14).
- Instrument the P0 gaps: per-task `actual_minutes`, an acceptance event, a distinct pid per claim.
- Emit the client-safe payload as JSON for a consumer other than the HTML renderer.

## P2 — artifact compilation platform

Only if a fourth artifact type and a second consumer both exist. Multiple artifact families, an
artifact registry, template management, artifact-usefulness evaluation, export ecosystem, automatic
maintenance. **Nothing here is justified by current evidence.**

---

# 12. Validation and evaluation strategy

## 12.1 Compilation FAILS (raises) on

| Rule | Precedent |
|---|---|
| An `evidence_ref` naming a file that does not exist | new — today `ground()` downgrades to `CLAIMED`; for a case study a dangling ref is an authoring bug |
| A `path#anchor` whose anchor is not a real heading | **new, and load-bearing** — this is what makes §5.1 acceptable |
| `maturity == EXERCISED` with no `mechanism_refs` or no `USABLE` evidence row | new |
| A `CONTRADICTORY` claim with fewer than 2 `sides[]` | new |
| A `TemporalAssertion` with no `observed_at` | new |
| A `CaseStudy` whose issues are all on one `track` | new |
| An unknown projection section | exists — `client_review.py:178-182` |
| An `origin` not in `ORIGINS` | exists — `:454` |
| A client-visible string hitting the deny backstop | exists — `LeakError`, `:153-170` |

## 12.2 Compilation WARNS (renders, loudly) on

Freshness `UNAVAILABLE` · `mission_integrity` `WARNING` (exists) · a guarded word downgraded to
`UNSUBSTANTIATED` (exists) · a KPI with `basis = NOT_RECORDED` · an input hash that no longer matches
the manifest · a renderer asked for a semantic state it has no visual register for.

## 12.3 Acceptance criteria for the generator itself

| Criterion | How it is checked |
|---|---|
| **Grounding** | Every rendered claim resolves to an evidence basis, or renders its basis explicitly. Test: no rendered string carries a guarded word with grounding < `GROUNDED` |
| **Accuracy** | Test: the MER contradiction renders as `CONTRADICTORY` with both sides visible |
| **Temporal correctness** | Test: an assertion with `rechecked_at is None` never renders as bare "true" |
| **Counterfactual honesty** | Test: no `CapabilityCounterfactual` with `maturity != EXERCISED` appears inside the outcomes component (enforced by type; asserted anyway) |
| **Client safety** | Test: a narrative containing a forbidden substring raises `LeakError`; a field added to the view model does **not** appear in the payload |
| **Freshness** | Test: with the task store absent, the artifact renders and says `UNAVAILABLE` |
| **Determinism** | Test: two compilations of the same inputs produce byte-identical HTML except the `as_of` field |
| **Renderer contract inherited** | The second renderer must satisfy the two the first already does: `test_the_generated_page_makes_no_external_requests` and `test_every_font_role_resolves_through_a_token` (`tests/test_client_review.py:354`, `:375`). Promote both to a shared renderer-contract test |
| **Regression** | The 11 fixture assertions in §13 |
| **Visual coherence** | Rendered at 700/1000/1400px, light and dark, with a deliberately broken input; screenshots stored under `docs/evidence/` per the global consumer-layer rule |
| **Usefulness** | A reader can answer the brief's seven questions from the artifact alone — checked by a human at the gate, not by a test |

---

# 13. Delivery #001 as the executable test fixture

Eleven assertions from the brief, each mapped to real state. These are semantic tests over real
data, not synthetic fixtures.

| # | Assertion | Real anchor | Expected |
|---|---|---|---|
| 1 | Wrong-field lookup / duplicate tasks | `.data/tasks.jsonl` @`02:13:52Z`, `fbe2ea4c`, `200deda2` | Issue `M-01` renders `escape_distance = 4`, `still_open` for the header half |
| 2 | 10 observed vs 8 declared; 40% vs 25% | `_completion()` + `mission_integrity()` | Client figure = **25%**, basis `DERIVED`; integrity `WARNING` present in diagnostics and **absent** from the client payload |
| 3 | Corrected metric hierarchy | handoff §2 | `TemporalAssertion` state `REFUTED`, with the superseding assertion linked |
| 4 | MER contradiction | R2 S2 | basis `CONTRADICTORY`, ≥2 sides, **not** resolved to one direction |
| 5 | Source/clone ambiguity | R2 §0, M18 | Issue `H4`/`H5`; counterfactual capability = Source Cartography, maturity `IMPLEMENTED_NOT_EXERCISED` |
| 6 | F91 knowledge-known-not-consumed | checkpoint §1 | Issue `M-05` carries pattern `KNOWLEDGE_AVAILABLE_BUT_NOT_CONSUMED`; counterfactual `WOULD_BLOCK`, maturity `PROPOSED` |
| 7 | Stale superseded task IDs in artifact headers | `R1:3`, `R2:3` | Issue `M-02` present, `still_open = True` |
| 8 | R2 required access it did not have | spec §0.5 vs R2 method note | Issue `M-07`; counterfactual = Typed Handoff + ACK/NACK, maturity `PROPOSED` |
| 9 | Parallelism not proven | `.data/claims/*.json`, all pid 17172 | KPI *Concurrent Delivery Capacity* renders **blind-instrument**, not a number |
| 10 | Routing instrumentation `NOT_RECORDED` | mission json vs spec §4 | KPI *Delivery Predictability* renders `NOT_RECORDED`, **never 0** |
| 11 | Client Review actually intercepted vs Factory counterfactuals | `client_review.py` + navira yaml | Client Review capability = `EXERCISED` with `mechanism_refs`; Source Cartography and Intent Contract are **not** — and the artifact shows the difference visually |

⭐ **Assertions 9 and 10 are the load-bearing ones**, for the same reason the mission's negative
controls 3 and 4 were: the others can pass over an absence. 9 and 10 fail loudly if the generator
ever renders a missing measurement as a value.

---

# 14. Self-maintainability

| Capability | Phase | Why |
|---|---|---|
| Claim validation (refs, anchors, maturity, contradiction arity) | **P0** | Without it, §5.1's markdown boundary is unsafe |
| Manifest with input hashes + versions + `as_of` | **P0** | ~30 lines; buys determinism and staleness detection |
| Staleness detection | **P0** | Free from the manifest |
| The 11 semantic regression assertions | **P0** | The fixture is the test suite |
| Golden-artifact comparison | **P1** | Needs a stable renderer first; a golden file over a churning renderer is noise |
| Schema drift detection | **P1** | Needs a second consumer of the payload |
| Template version comparison / rollback | **P2** | No templates in P0 — the renderer is code under git |
| Broken-render detection (screenshot diff) | **P1** | Manual render checks in P0, per the global consumer-layer rule |
| Artifact usefulness evaluation | **P2** | Needs readers and a second delivery |

---

# 15. Risks, and what NOT to build

| # | Risk | Mitigation |
|---|---|---|
| **R1** | **The yaml drifts from the forensic markdown** — the `FIELDS.md` failure, committed by the artifact that documents it | Anchor validator in P0, non-negotiable. If the gate cuts it, reject §5.1 and generate the yaml from the markdown instead |
| **R2** | **Generalising from one example.** Extracting shared chrome now would produce a framework shaped like the client review | Extract only `projection` and `assertions` in P0 — both already generic. Defer renderer-chrome extraction to P1, after two renderers exist |
| **R3** | **The refactor breaks a working client-facing surface** before a real meeting | `tests/test_client_review.py` must pass **untouched**. If it needs editing, revert |
| **R4** | **The artifact flatters the Factory.** 25 of 37 issues are client-track; the temptation is to render those and mute the 12 | Single-track compile refusal (§7.1). Make it structural |
| **R5** | **Scope creep to the ten-section Command Center** with six sections of authored prose | P0 = case study only. Command Center at Delivery #002 |
| **R6** | **`DOCUMENTED` creeping into `USABLE`** and silently promoting one-hop claims to verified | Assert in a test that `USABLE == ("MEASURED","DERIVED")` |
| **R7** | Concurrent sessions on this checkout (3 peer sessions busy on this repo now) touching `factory/` | Re-measure HEAD before edits; the extraction touches one existing file |

### Explicitly do NOT build

Markdown parser · artifact database · artifact registry / plugin loader · `ArtifactSpec` DSL ·
template engine (the renderer is Python under git) · a service boundary of any kind · a base
`ArtifactViewModel` class · bitemporal belief store · branching narrative engine · SSE/live push
(measured absent, and timestamp-based freshness is better for demo resilience) · a second Client
Review.

---

# 16. Exact files added or changed in P0

| File | Action | Est. lines | Note |
|---|---|---|---|
| `factory/projection.py` | **new (extract)** | ~95 | `CLIENT_SAFE`-style tables keyed by artifact type; `safe()`, `_scan()`, `LeakError`. Behaviour identical |
| `factory/assertions.py` | **new (extract + add)** | ~150 | `ground/enforce/is_guarded/freshness` moved verbatim; `EvidenceBasis`, `CapabilityCounterfactual`, `Maturity`, `resolve_anchor()` added. ⛔ **No `TemporalAssertion`** — that extends `context.py` instead |
| `factory/client_review.py` | **modified** | −140 / +6 | delete `:117-184`, `:190-258`; import. **Public API unchanged** |
| `factory/case_study.py` | **new** | ~340 | `assemble()`, `CaseStudy` + child dataclasses, validation rules, declared counting bases |
| `factory/case_study_render.py` | **new** | ~430 | mirrors `client_review_render.py`; reuses its theme CSS and `?mode=meeting` pattern; manifest footer |
| `missions/delivery-001/case-study.yaml` | **new (authored)** | ~700 | 9 scenes, ~15 issues, 4 patterns, 17 KPI rows, A/B tracks |
| `tests/test_case_study.py` | **new** | ~260 | the 11 assertions |
| `factory/context.py` | **modified** | +25 | 3 status members, `observed`, `superseded_by`, 1 kind. **Additive only.** Acceptance: `tests/test_context_pack.py` passes untouched |
| `tests/test_projection.py` | **new** | ~70 | boundary tests, incl. "a new field does not publish" |
| `docs/artifacts/delivery-001-case-study.html` | **output** | — | generated, disposable |
| `docs/case-studies/delivery-001-marketing-model.md` | **modified** | +anchors | add stable heading anchors for the yaml to cite |

**Net: 5 new modules/tests, 3 modified files, 1 authored fixture, 1 build output.**
No new dependency. `pyyaml` remains the sole runtime dep.

---

# 17. Open architectural decisions for the gate

| # | Question | My recommendation |
|---|---|---|
| **Q1** | **P0 = forensic case study only, or the full ten-section Command Center?** | **Case study only.** Six Command Center sections have no evidence behind them until Delivery #002. This is the biggest scope call and it is yours |
| **Q2** | **Is `docs/case-studies/*.md` canonical-with-anchors (§5.1), or generated from the yaml?** | **Canonical-with-anchors, conditional on the anchor validator shipping in P0.** Without the validator, generate it instead — an unvalidated transcription is the `FIELDS.md` defect |
| **Q3** | Should the case study be **client-safe** at all, or operator/internal-only? | **Operator/internal for P0.** It names our own failures, an unrotated credential exposure, and client commercial figures. Give it its own projection table with a **narrower** allow-list, and decide client-facing derivatives later |
| **Q4** | Does `EvidenceBasis` belong in `factory/evidence.py` (extending a canonical enum) or in `assertions.py` (display vocabulary)? | **`assertions.py`.** Keeping it out of `evidence.py` is what stops `DOCUMENTED` leaking into `USABLE`. Costs one import; buys the promotion gate |
| **Q5** | Do we fix the three open provenance defects (R1/R2 stale headers, R2 scope, mission integrity) **before** building the artifact on them? | **Fix the two cheap ones first** (headers, integrity note). An artifact whose own fixture carries a known-wrong provenance is not a credible demonstration of provenance |
| **Q6** | Does the artifact ship as a published Artifact (claude.ai URL) or a repo file? | **Repo file in P0.** It contains client commercial figures and an unrotated credential incident. Publishing is a separate, deliberate decision |
| **Q7** | Who authors the 700-line yaml — transcribed from the markdown in one pass, or built incrementally scene by scene? | **One transcription pass, then the validator.** Incremental authoring against a validator that does not exist yet is how drift starts |

---

| **Q8** | **`context.py` is edited additively, or the case study gets an isolated subclass?** It has 3 live consumers (`claims.py`, `lanes.py`, `test_context_pack.py`) | **Edit additively.** Purely additive enum members plus one optional field; acceptance is `test_context_pack.py` passing untouched. A parallel vocabulary is the defect this whole document argues against |
| **Q9** | **Does `client-review-loop-v0.md`'s gate — *"Do not build UI yet… Build no UI until that lifecycle runs"* — bind this work?** | **My reading: no.** That gate governs the *ClientReview decision lifecycle* (11 contracts: ReviewCandidate → Storage boundary) and its client-facing UI. A forensic case study is an internal artifact over completed state and proposes no scope. **But it is your gate and I will not self-exempt from it** |
| **Q10** | **`04-DEFINITION-OF-DONE.md:37-44` explicitly cut "animated mission replay" and "historical time machine" as nice-to-haves.** A nine-scene progressive-reveal case study is adjacent to both | **Surfaced, not resolved.** The distinction I would draw: the cut items are *decoration over live delivery state*; this is *a forensic record of completed state with evidence citations*. If you read them as the same thing, the honest P0 is the static executive/issue/KPI artifact with no scene mechanic |

---

# 18. Corrections the inventory pass forced on this proposal

Recorded rather than silently applied, because the pattern is the point.

| # | My first draft said | Measured | Consequence |
|---|---|---|---|
| **C1** | Invent a `TemporalAssertion` dataclass | `context.py:51-53,88-90,109` already carries status, confidence, `source`, `checked`, **and refuses `CURRENT` without a date** | Contract deleted; replaced with a ~25-line additive extension. ⭐ **I committed `KNOWLEDGE_AVAILABLE_BUT_NOT_CONSUMED` inside the proposal about it** |
| **C2** | `docs/findings.d/` is the findings source | `findings.py` reads `docs/findings.md` **union** `docs/findings.d/*.md` | The 28-file count is a subset. `Finding`'s `BELIEVED / ACTUALLY / MEASURED BY / AFFECTS` + `missing` is a **direct precedent for `Issue`** — reuse the shape |
| **C3** | Nothing persists a derived artifact | `readiness.py:617` caches suite results to `.data/suite-cache.json` | Narrow, not a projection cache. Claim qualified |
| **C4** | The renderer handles four grounding states | `_GRADE` renders **three**; `UNSUBSTANTIATED` is a status flag whose note is `.opsonly` — **hidden in Live Meeting mode** | Preserve as-is: the client still sees the downgraded *status*; only the operator note hides. **Verify this at implementation** — if the downgrade itself hides in meeting mode, that is a defect in the surface used in front of clients |
| **C5** | One artifact-generation idiom exists | **Two.** `render_html()` f-string (`client_review_render.py:486`), and `--insert`-into-checked-in-HTML build scripts driven by `sync_artifact()` (`local_tracker.py:745-775`) for `agent-factory.html` | **Pick the `render_html()` idiom.** The `--insert` idiom makes a checked-in HTML file both source and output, which is the second-truth-store failure this proposal exists to avoid |
| **C6** | 44 test files | **40** test files, 8,496 lines; `tests/test_client_review.py` alone is **484 lines / 36 tests** | Strengthens R3's mitigation — the extraction has a real safety net, not a nominal one |


---

# 19. Recommended architecture and recommended P0 — the two-line version

**Architecture.** `client_review.py` is already the artifact compiler. Extract `projection.py` and
`assertions.py`; add `CapabilityCounterfactual` with a `maturity` enum and an anchor-resolving
`ground()`; **extend `context.py` additively for the temporal contract rather than inventing one —
it already refuses `CURRENT` without a date**; add `case_study.py` + `case_study_render.py` as the
second artifact type. Canonical state stays canonical, the authored yaml holds only what the Factory cannot derive,
and compiled HTML is disposable. No service, no database, no template engine, no markdown parser.

**P0.** Nine items, four new modules, two additive refactors whose acceptance test is that
`tests/test_client_review.py` passes untouched — producing one real artifact:
`docs/artifacts/delivery-001-case-study.html`, compiled from real task state, real evidence rows and
an authored fixture, with eleven semantic regression assertions of which two exist specifically to
fail if a missing measurement is ever rendered as a number.

**Stopping here for the architecture gate.**
