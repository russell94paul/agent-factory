# Claude Phase 1 Addendum — Ingest CELL OS Research Manifest v3

Use this prompt in the active agent-factory restructuring session after attaching:

- CELL_OS_Deep_Research_Manifest_v3.md
- CELL_OS_Optimized_Deep_Research_Prompt_Manifest_v2.md
- SIHRE_Recommended_Deep_Research_Report_Queue_Legacy.md
- DESIGN_DELTA_SINCE_SIHRE_QUEUE.md

## Mission

Perform a bounded Phase 1 addendum that ingests, compares and classifies the attached research-planning artifacts.

Do not restart Phase 1. Do not begin Phase 2. Do not dispatch external research. Do not move existing tracked files.

The attached v3 manifest was produced after review of the measured Phase 1 summary and DESIGN_DELTA_SINCE_SIHRE_QUEUE.md. It is a proposed forward research control document, not evidence that its proposed components exist in code.

## Required interpretations

### 1. Preserve measured repository truth

Retain the measured Phase 1 baseline, including:

- agent-factory at 827f871 on main at the audit snapshot;
- one Python distribution and flat factory package;
- 68 runtime modules and 23,939 lines;
- contract.py as the dependency centre;
- PyYAML as the only runtime dependency;
- no JS/TS production application or monorepo tooling;
- existing hard-coded documentation paths;
- existing index requiring a delta rather than replacement;
- AMBER baseline with 1,016 passed, 2 failed and 2 xfailed tests;
- ten recorded runs, zero PASS and seven agent-returned dry runs;
- no measured runtime implementation of the named next-generation CELL OS concepts.

Remeasure any snapshot value before using it after migration.

### 2. Treat new design concepts honestly

The v3 concepts that were absent from the prior repository are user-approved external design inputs.

Classify them as PROPOSED_EXTERNAL, not IMPLEMENTED, PROVEN or CANONICAL.

Repository absence does not automatically reject an approved research question. It means the concept needs provenance, specification, research and evaluation before promotion.

### 3. Separate four readiness dimensions

For every lane report separately:

1. RESEARCH_READINESS
2. EXPERIMENT_READINESS
3. IMPLEMENTATION_READINESS
4. PROMOTION_READINESS

A lack of real mission history can block empirical calibration and promotion without blocking prior-art research, mathematical formulation, architecture design or experiment design.

One non-dry-run mission is a runtime smoke test. It is not enough to estimate correlated failure or mission-performance covariance. Those require repeated comparable missions across relevant task classes, conditions and seeds.

Homeostasis and immunity research may use synthetic fault injection before a naturally observed drift event. Operational threshold promotion still requires longitudinal evidence.

Ablation protocols may be designed before real mission history and exercised on controlled benchmarks. External-validity claims remain blocked until representative observations exist.

### 4. Preserve prior-art nuance

Existing organizational-computation and organizational-compiler prior art can refute a broad novelty claim without refuting the usefulness of an Org-IR or compiler component.

Separate:

- novelty of a primitive;
- novelty of a combination;
- implementation differentiation;
- practical utility.

### 5. Treat evaluation maturity accurately

The existence and unit testing of contract.py, evals.py and calibration.py prove implementation anchors.

They do not prove the complete end-to-end evaluation architecture or operational effectiveness. Use PARTIAL unless stronger evidence exists.

### 6. Resolve terminology rather than declaring it settled

Surfacing the canonical ontology closes the missing-file portion of repository DR08, but explicit decisions may still be required for:

- Operative Cell versus Cell;
- Cell Blueprint versus Cell Genome versus Configuration Genome;
- C-MESH, T-MESH and OS-MESH;
- SIHRE expansion;
- OPC;
- Link versus CellBus semantics.

Do not introduce a fourth synonym for blueprint.py.

## Required work

1. Hash and inventory every attached source.
2. Record that v2, v3 and the legacy twenty-report queue originated outside the earlier repository corpus.
3. Read v2 and v3 completely.
4. Read the legacy twenty-report queue completely.
5. Compare all three with:
   - repository DR01–DR08;
   - R1–R19 and R06B;
   - RB-01–RB-26;
   - the canonical ontology;
   - current_vs_proposed;
   - the Phase 1 design delta.
6. Complete or replace the blocked comparison in DESIGN_DELTA_SINCE_SIHRE_QUEUE.md.
7. Produce an old-to-v3 mapping for every prompt.
8. Confirm that Link semantics has explicit coverage.
9. Confirm that completed NERVE research is reused and only integration gaps remain.
10. Confirm that the Domain family and CELL-Q are recorded as proposed external design inputs.
11. Verify that CELL-Q remains limited to historical replay, synthetic environments, offline experiments and paper research.
12. Identify missing topics, duplicated lanes and sequencing errors.
13. Update the proposed research registry and NEXT_RESEARCH_RUN.
14. Do not dispatch any lane.

## Required disposition vocabulary

For every old prompt use one of:

- COMPLETED_REUSE
- MERGED_INTO_V3
- NARROW_FOLLOWUP
- LOCAL_MEASUREMENT
- IMPLEMENTATION_TICKET
- DEFERRED_EXPERIMENT
- SUPERSEDED
- REJECTED

## Required Phase 1 addendum outputs

Update or create only within the paths allowed by the current Phase 1 protocol:

- revised DESIGN_DELTA_SINCE_SIHRE_QUEUE.md;
- RESEARCH_MANIFEST_V3_RECONCILIATION.md;
- proposed research_registry.yaml update;
- proposed research_status.md update;
- NEXT_RESEARCH_RUN.md;
- V3_ACTIVATION_DECISION.md.

If the current protocol does not permit one of those final paths, write its proposed content under docs/restructure and provide the eventual destination. Do not silently violate the Phase 1 write boundary.

## Activation decision

Return:

1. Whether v3 is complete enough to supersede v2.
2. Which v3 lanes are research-ready.
3. Which lanes are blocked only for experiments or promotion.
4. Which local P0 actions remain.
5. The exact attachment set for the first approved research lane.
6. Whether Phase 2 remains blocked.
7. The single next action.

Use one final status:

- V3_ACCEPTED_NOT_ACTIVATED
- V3_REVISION_REQUIRED
- V3_ACTIVATED_FOR_CELL_DR_01

Do not use V3_ACTIVATED_FOR_CELL_DR_01 unless all activation conditions in the v3 manifest are evidenced.

Finish with:

    PHASE 1 V3 ADDENDUM COMPLETE
    No external research dispatched.
    No Phase 2 migration started.

