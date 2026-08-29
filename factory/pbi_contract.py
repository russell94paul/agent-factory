"""The Power BI model-change GreenContract — M1 through M12.

Mirrors :mod:`factory.connector_contract`, and for the same reason: **a model an agent produces
that nothing can check is not a deliverable, it is a liability.** This file exists BEFORE any
Power BI agent, per `boot-prompts/power-bi-data-model-designer.md`, because the ordering is the
whole lesson — build the thing that certifies the output first.

**Every assertion states a positive fact that must be observed.** None is satisfied by the absence
of an error. Power BI has the identical SILENT-EMPTY shape the connector runtime has, one layer
up: on **GP-293** a repoint **passed DAX parity while every visual rendered "Error loading data"**
from a stale `dataset_name`. "The DAX query returned rows" is compatible with a completely dead
report.

**Facts arrive through probes, and a probe that cannot run raises Unmeasurable.**

⭐ **The two assertions that matter most cannot be made from XMLA/DAX at all** — *every visual
paints* (M10) and *each slicer responds* (M11). They are declared here anyway, and their default
probe raises `Unmeasurable`. That is the central design decision of this file, and it is
deliberate:

    A contract that quietly DROPS the two assertions only a renderer can make is a contract that
    certifies the wrong layer — and would have returned GREEN on GP-293 while every visual was
    broken.

So they are present and loud. An estate with no renderer wired gets `UNMEASURABLE` for the whole
contract, which is the honest verdict: *we did not observe a failure, and emphatically did not
observe a pass.* Wiring Chrome (working as of 2026-08-23 16:31 — it had been signed out, not
broken) is what turns them green.

⛔ **What this contract does NOT do.** It does not deploy, does not mutate a model, and does not
decide whether a change is a good idea. It reports what was observed. `66151728` is the client's
LIVE surface with two reports bound; nothing here is a licence to write to it.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .contract import GreenContract, Unmeasurable

#: Money comparisons are floats out of DAX and floats out of Snowflake. An exact `==` on
#: 82_135.29 is a test that fails for reasons that have nothing to do with the change.
DEFAULT_TOLERANCE = 0.01


@dataclass
class PbiTarget:
    """What "green" means for ONE model change against ONE dataset.

    Everything here is an expectation the contract holds the world to. The world arrives
    separately, through probes — never from this object.
    """

    dataset_id: str
    dataset_name: str = ""
    workspace: str = ""

    #: ⚠ Declared, and asserted against what was actually written (M2). GP-301 shipped a ticket
    #: marked Done that was scoped TEST-only and left the identical defect live in PROD for 3.5
    #: months. A scope nobody checks is a note, not a control.
    environment: str = "TEST"                       # TEST | PROD
    allow_environments: List[str] = field(default_factory=lambda: ["TEST"])

    #: The rollback artefact, captured BEFORE mutation. A rollback saved afterwards is a copy of
    #: the damage.
    rollback_path: str = ""

    #: ⛔ Additive manifest. A TOM rename does NOT rewrite the DAX that references the old name,
    #: and `66151728` has two live reports bound, so a rename is a broken visual.
    additive_only: bool = True
    protected_objects: List[str] = field(default_factory=list)

    #: Fields this change is permitted to write. Anything else written is a finding — see M3.
    writable_fields: List[str] = field(default_factory=list)

    #: measure name -> expected value. The GP-318 anchors are the shape:
    #: GASP 82,135.29 · ME Spend 2,890,054.50 · MEP Grounded Spend 2,432,043.61
    anchors: Dict[str, float] = field(default_factory=dict)
    tolerance: float = DEFAULT_TOLERANCE

    #: measure name -> value BEFORE the change, for measures the change must NOT move.
    baseline: Dict[str, float] = field(default_factory=dict)

    #: ⭐ Measures whose source genuinely does not report a value. These must evaluate to BLANK,
    #: never 0. This is the defect class that produced GP-318's B26: 17 months of literal
    #: `$0.00` where the truth was "the source does not report it". A `0` reads as "we measured
    #: none"; that is a claim about the client's business that we did not measure.
    must_be_blank_not_zero: List[str] = field(default_factory=list)

    #: Reports bound to this dataset. ⚠ ENUMERATED, never assumed — on this very dataset,
    #: neither bound report binds a single Sales Measures field, yet 38 of 70 guarded measures
    #: live there. An assumed binding list is how the largest part of a change ships unobserved.
    bound_reports: List[str] = field(default_factory=list)

    #: Minimum rows a refresh must have moved for it to count as data rather than metadata.
    #: The client's Marketing model has had no real refresh since 2026-07-23 — its last three
    #: took ~0.5s, which is metadata only.
    min_refresh_seconds: float = 5.0


class Probes:
    """The instruments. Each returns observed facts, or raises Unmeasurable.

    Subclass to talk to XMLA/TOM, the Power BI REST API, Snowflake and a renderer. The base class
    refuses everything, which is the correct default: an unconfigured harness reports
    UNMEASURABLE, never PASS.

    ⭐ Note `render` and `interact` sit here as first-class instruments alongside `model` and
    `dax`, rather than being left out because they are hard. Their absence must be *reported*, not
    *silent*.
    """

    def _refuse(self, what: str):
        raise Unmeasurable(f"no instrument configured for {what}")

    def model(self, ctx: dict) -> dict: self._refuse("model metadata (XMLA/TOM)")
    def rollback(self, ctx: dict) -> dict: self._refuse("rollback artefact")
    def writes(self, ctx: dict) -> dict: self._refuse("what the change actually wrote")
    def refresh(self, ctx: dict) -> dict: self._refuse("refresh history")
    def dax(self, ctx: dict) -> dict: self._refuse("DAX evaluation")
    def source(self, ctx: dict) -> dict: self._refuse("warehouse source of truth")
    def bindings(self, ctx: dict) -> dict: self._refuse("report field bindings")
    def render(self, ctx: dict) -> dict: self._refuse(
        "a RENDERER — no visual has been observed to paint. XMLA and DAX cannot make this "
        "observation; on GP-293 DAX parity passed while every visual showed 'Error loading data'")
    def interact(self, ctx: dict) -> dict: self._refuse(
        "an INTERACTION harness — no slicer has been observed to respond. A silent no-op filter "
        "is a finding, never an acceptable default")


class CtxProbes(Probes):
    """Probes that read the world out of the context dict.

    For the eval corpus and calibration: a mutation is just a different value under the same key,
    so a harness can break one fact at a time and prove the contract notices. A missing or None
    key means the instrument could not run — UNMEASURABLE, not FAIL.
    """

    def _get(self, ctx: dict, key: str) -> dict:
        val = ctx.get(key)
        if val is None:
            raise Unmeasurable(f"no observation for '{key}'")
        if isinstance(val, Exception):
            raise val
        return val

    def model(self, ctx): return self._get(ctx, "model")
    def rollback(self, ctx): return self._get(ctx, "rollback")
    def writes(self, ctx): return self._get(ctx, "writes")
    def refresh(self, ctx): return self._get(ctx, "refresh")
    def dax(self, ctx): return self._get(ctx, "dax")
    def source(self, ctx): return self._get(ctx, "source")
    def bindings(self, ctx): return self._get(ctx, "bindings")
    def render(self, ctx): return self._get(ctx, "render")
    def interact(self, ctx): return self._get(ctx, "interact")


def _close(a: float, b: float, tol: float) -> bool:
    return abs(float(a) - float(b)) <= tol


def build_contract(target: PbiTarget, probes: Optional[Probes] = None) -> GreenContract:
    """Assemble the M1-M12 contract for one model change.

    Ordered preflight -> model layer -> consumer layer, because the consumer-layer checks are the
    expensive ones and a preflight failure means they would have proved nothing.
    """
    p = probes or Probes()
    c = GreenContract(f"pbi-model-change/{target.dataset_id}")

    # ------------------------------------------------------------------ preflight
    def m1(ctx):
        """The rollback exists and is real, BEFORE anything is written."""
        rb = p.rollback(ctx)
        if not rb.get("path"):
            return False, "no rollback artefact captured"
        if not rb.get("captured_before_change"):
            return False, (f"{rb.get('path')} was captured AFTER the change — that is a copy of "
                           "the damage, not a rollback")
        if not rb.get("bytes"):
            return False, f"{rb.get('path')} is empty"
        if rb.get("parses") is False:
            return False, f"{rb.get('path')} does not parse as TMSL/JSON — it cannot be applied"
        return True, f"{rb.get('path')} captured pre-change, {rb.get('bytes'):,} bytes, parses"

    def m2(ctx):
        """The dataset written to is the one declared, in an environment the change is scoped to.

        ⚠ Identity by ID, never by matching values. Two datasets can hold identical numbers and
        be different datasets — that inference caused a wrong-layer deploy and revert on CLIENT-A
        "Missing COGs", and again on GP-318 where the named fact was innocent.
        """
        w = p.writes(ctx)
        got = w.get("dataset_id")
        if got != target.dataset_id:
            return False, f"wrote to dataset {got}, contract targets {target.dataset_id}"
        env = w.get("environment")
        if env not in target.allow_environments:
            return False, (f"wrote to {env}; this change is scoped to "
                           f"{', '.join(target.allow_environments)}")
        return True, f"{target.dataset_id} in {env}, as scoped"

    def m3(ctx):
        """⭐ Every field written was appended or had its prior value asserted first.

        `_gp318_b26_falsezero_fix.py` asserted the live EXPRESSION before overwriting it — and set
        `Description` wholesale, destroying 693 characters of GP-317 guidance including two
        operational warnings. Guarding one field and not the other is guarding nothing.
        """
        w = p.writes(ctx)
        fields = w.get("fields") or []
        if not fields:
            raise Unmeasurable("the change reported no field-level writes to inspect")
        unguarded = [f["field"] for f in fields
                     if not (f.get("appended") or f.get("prior_asserted"))]
        if unguarded:
            return False, (f"{len(unguarded)} field(s) overwritten without appending or "
                           f"asserting the prior value: {', '.join(unguarded)}")
        if target.writable_fields:
            stray = [f["field"] for f in fields if f["field"] not in target.writable_fields]
            if stray:
                return False, f"wrote field(s) outside the declared scope: {', '.join(stray)}"
        return True, f"{len(fields)} field write(s), each appended or prior-asserted"

    def m4(ctx):
        """Additive manifest: nothing renamed, nothing deleted.

        A TOM rename does not rewrite DAX references. `66151728` is the client's live surface.
        """
        if not target.additive_only:
            raise Unmeasurable("target does not declare additive_only — blast radius uncertified")
        w = p.writes(ctx)
        renamed = w.get("renamed") or []
        deleted = w.get("deleted") or []
        if renamed or deleted:
            bad = [f"renamed {r}" for r in renamed] + [f"deleted {d}" for d in deleted]
            return False, "; ".join(bad) + " — a rename does not rewrite dependent DAX"
        touched = set(w.get("touched") or [])
        clobbered = sorted(touched & set(target.protected_objects))
        if clobbered:
            return False, f"modified protected object(s): {', '.join(clobbered)}"
        return True, f"additive — {len(w.get('added') or [])} added, 0 renamed, 0 deleted"

    # ------------------------------------------------------------- model layer
    def m5(ctx):
        """The refresh moved DATA, not metadata.

        Three consecutive ~0.5s refreshes on the client's Marketing model are metadata-only, and
        a model that has not really refreshed since 2026-07-23 will make a client disagree for
        the wrong reason and cost a multi-day round trip.
        """
        r = p.refresh(ctx)
        if r.get("status") != "Completed":
            return False, f"last refresh ended {r.get('status')}"
        dur = r.get("duration_seconds")
        if dur is None:
            raise Unmeasurable("refresh history carries no duration")
        if dur < target.min_refresh_seconds:
            return False, (f"refresh took {dur}s, under the {target.min_refresh_seconds}s floor "
                           "— that is a metadata refresh, no data moved")
        parts = r.get("partition_dates") or []
        if len(set(parts)) > 1:
            return False, (f"partitions {len(set(parts))} distinct dates apart inside one model: "
                           f"{sorted(set(parts))}")
        return True, f"refresh Completed in {dur}s"

    def m6(ctx):
        """The changed measures evaluate to their anchors."""
        if not target.anchors:
            raise Unmeasurable("no anchors declared — correctness of the change is unmeasurable")
        d = p.dax(ctx)
        vals = d.get("measures")
        if vals is None:
            raise Unmeasurable("DAX probe returned no measure values")
        wrong, missing = [], []
        for name, want in target.anchors.items():
            if name not in vals:
                missing.append(name)
            elif vals[name] is None or not _close(vals[name], want, target.tolerance):
                wrong.append(f"{name}: got {vals[name]}, expected {want}")
        if missing:
            # A measure that does not evaluate is not a failed value, it is an absent instrument.
            raise Unmeasurable(f"measure(s) did not evaluate: {', '.join(missing)}")
        if wrong:
            return False, "; ".join(wrong)
        return True, f"{len(target.anchors)} anchor(s) within {target.tolerance}"

    def m7(ctx):
        """⭐ No regression: measures outside the change are unchanged.

        ⚠ Enumerated, never sampled. A 30-day `SUM(total)==SUM(clicks)` equality held while 38
        individual rows disagreed over full history. A healthy aggregate is not a healthy
        population.
        """
        if not target.baseline:
            raise Unmeasurable("no baseline captured — regression is unmeasurable, not absent")
        d = p.dax(ctx)
        vals = d.get("measures")
        if vals is None:
            raise Unmeasurable("DAX probe returned no measure values")
        moved, unseen = [], []
        for name, before in target.baseline.items():
            if name not in vals:
                unseen.append(name)
            elif vals[name] is None or not _close(vals[name], before, target.tolerance):
                moved.append(f"{name}: was {before}, now {vals[name]}")
        if unseen:
            raise Unmeasurable(
                f"{len(unseen)} baseline measure(s) not evaluated, so no-regression covers only "
                f"part of the population: {', '.join(unseen)}")
        if moved:
            return False, f"{len(moved)} out-of-scope measure(s) moved: " + "; ".join(moved)
        return True, f"{len(target.baseline)} out-of-scope measure(s) unchanged"

    def m8(ctx):
        """⭐ Not-reported renders BLANK, never 0.

        GP-318's B26: 17 months of literal `$0.00` where the source simply does not report the
        value. A `0` is a measurement claim. Absence is not zero, and a drift detector that
        treats BLANK as `0.00` scores a false-zero-introducing candidate clean.
        """
        if not target.must_be_blank_not_zero:
            raise Unmeasurable(
                "target declares no not-reported measures — the false-zero class is uncertified")
        d = p.dax(ctx)
        blanks = d.get("blankness")
        if blanks is None:
            raise Unmeasurable(
                "DAX probe did not distinguish BLANK from 0 — the one thing this assertion needs")
        zeros = [n for n in target.must_be_blank_not_zero if blanks.get(n) == "ZERO"]
        absent = [n for n in target.must_be_blank_not_zero if n not in blanks]
        if absent:
            raise Unmeasurable(f"blankness not observed for: {', '.join(absent)}")
        if zeros:
            return False, (f"{len(zeros)} measure(s) render 0 where the source reports nothing: "
                           f"{', '.join(zeros)}")
        return True, f"{len(target.must_be_blank_not_zero)} not-reported measure(s) render BLANK"

    def m9(ctx):
        """The model agrees with the warehouse — an independent second instrument.

        M6 checks the model against a number we wrote down. M9 checks it against the source. That
        is what separates "correct" from "consistently wrong", and it is the same split as the
        connector contract's A9 vs A10.
        """
        d, src = p.dax(ctx), p.source(ctx)
        expected = src.get("measures")
        if expected is None:
            raise Unmeasurable("warehouse probe returned no comparable values")
        vals = d.get("measures") or {}
        diffs = [f"{k}: warehouse {v}, model {vals.get(k)}"
                 for k, v in expected.items()
                 if k not in vals or vals[k] is None or not _close(vals[k], v, target.tolerance)]
        if diffs:
            return False, "; ".join(diffs)
        return True, f"model == warehouse for {len(expected)} measure(s)"

    # ---------------------------------------------------------- consumer layer
    def m10(ctx):
        """⭐ EVERY VISUAL PAINTS. The assertion XMLA cannot make.

        GP-293 is the whole argument: a repoint passed DAX parity while every visual rendered
        "Error loading data" from a stale `dataset_name`. Server-side data paths, name/ID
        resolution, RBAC and caching all fail AFTER the query succeeds.

        With no renderer wired this raises Unmeasurable, and the contract's verdict becomes
        UNMEASURABLE rather than PASS. That is the point: the estate must be told it has not
        looked, not allowed to infer it looked and saw nothing wrong.
        """
        r = p.render(ctx)
        reports = r.get("reports")
        if reports is None:
            raise Unmeasurable("renderer returned no report observations")
        if not target.bound_reports:
            raise Unmeasurable(
                "no bound reports declared — enumerate them; an assumed binding list is how the "
                "largest part of a change ships unobserved")
        unseen = [rid for rid in target.bound_reports if rid not in reports]
        if unseen:
            raise Unmeasurable(f"no render observation for report(s): {', '.join(unseen)}")
        broken = []
        for rid in target.bound_reports:
            obs = reports[rid]
            bad = obs.get("visuals_errored") or []
            blank = obs.get("visuals_blank") or []
            total = obs.get("visuals_total")
            if total is None:
                raise Unmeasurable(f"report {rid} reported no visual count")
            if total == 0:
                return False, f"report {rid} rendered 0 visuals"
            if bad or blank:
                broken.append(f"{rid}: {len(bad)} errored, {len(blank)} blank of {total}")
        if broken:
            return False, "; ".join(broken)
        painted = sum(reports[r_]["visuals_total"] for r_ in target.bound_reports)
        return True, f"{painted} visual(s) painted across {len(target.bound_reports)} report(s)"

    def m11(ctx):
        """Each slicer/filter responds. A silent no-op is a finding, never a default.

        The standing rule is to record which components respond and which are inert. An inert
        filter that nobody wrote down is indistinguishable from one nobody tried.
        """
        i = p.interact(ctx)
        controls = i.get("controls")
        if controls is None:
            raise Unmeasurable("interaction harness returned no control observations")
        if not controls:
            raise Unmeasurable("no slicers or filters were exercised — inertness is unmeasured")
        inert = [c["name"] for c in controls if not c.get("responded")]
        if inert:
            return False, f"{len(inert)} control(s) inert: {', '.join(inert)}"
        return True, f"{len(controls)} control(s) responded"

    def m12(ctx):
        """Bindings are enumerated, and the change's fields are actually reachable by a consumer.

        ⚠ On `66151728`, neither bound report binds a single Sales Measures field while 38 of 70
        guarded measures live there. A change to a field nothing binds is not wrong — but calling
        it validated is. PBIR nests visual config as escaped JSON, so an unescaped scan returns 0
        bound entities: that is NOT-VISIBLE, not ZERO.
        """
        b = p.bindings(ctx)
        if b.get("escaped_json_decoded") is False:
            raise Unmeasurable(
                "binding scan did not decode PBIR's escaped visual JSON — 0 bound entities here "
                "is NOT-VISIBLE, not ZERO")
        bound = b.get("bound_fields")
        if bound is None:
            raise Unmeasurable("binding probe returned no field list")
        changed = set((p.writes(ctx).get("touched") or []))
        if not changed:
            raise Unmeasurable("no changed objects reported — reachability is unmeasurable")
        reachable = sorted(changed & set(bound))
        unreachable = sorted(changed - set(bound))
        if not reachable:
            return False, (f"none of the {len(changed)} changed object(s) is bound by any report "
                           f"— the change cannot have been observed at the consumer layer")
        detail = f"{len(reachable)} of {len(changed)} changed object(s) bound by a report"
        if unreachable:
            detail += f"; {len(unreachable)} not bound (record, do not assume harmless)"
        return True, detail

    c.add("M1-rollback-captured-first", m1,
          description="a rollback saved after the change is a copy of the damage")
    c.add("M2-target-is-the-declared-dataset", m2,
          description="identity by id and environment, never by matching values")
    c.add("M3-every-field-appended-or-asserted", m3,
          description="guarding one field and not the other is guarding nothing")
    c.add("M4-additive-manifest", m4,
          description="no rename, no delete — TOM does not rewrite dependent DAX")
    c.add("M5-refresh-moved-data", m5,
          description="a 0.5s refresh is metadata; no data moved")
    c.add("M6-anchors-hold", m6, description="the changed measures evaluate to their anchors")
    c.add("M7-no-regression", m7, description="out-of-scope measures enumerated and unchanged")
    c.add("M8-absence-renders-blank", m8, description="not-reported is BLANK, never 0")
    c.add("M9-warehouse-agreement", m9, description="independent second instrument")
    c.add("M10-every-visual-paints", m10,
          description="⭐ the assertion XMLA cannot make — GP-293")
    c.add("M11-controls-respond", m11, description="a silent no-op filter is a finding")
    c.add("M12-change-is-reachable", m12, description="bindings enumerated, not assumed")
    return c


#: The assertions that NO XMLA/DAX instrument can satisfy, named so a caller can report the gap
#: honestly instead of discovering it as an UNMEASURABLE with no explanation.
RENDER_ONLY = ("M10-every-visual-paints", "M11-controls-respond")


def unmeasurable_without_renderer() -> List[str]:
    """What stays dark until a renderer is wired. Published so the gap is a stated fact."""
    return list(RENDER_ONLY)
