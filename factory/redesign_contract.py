"""The model-REDESIGN contract — R1-R4, on top of `pbi_contract`'s M1-M12.

A redesign is not a bigger `add-measure`. It is a different shape of change, and the M-contract
is wrong for it in two specific ways that were both measured before this module was written:

⛔ **M1-M12 cannot certify a redesign at all.** `M4-additive-manifest` raises `Unmeasurable`
whenever `additive_only` is false — *"target does not declare additive_only — blast radius
uncertified"*. That is the honest answer while nothing can certify a non-additive change, and it
means a redesign, which renames and deletes by definition, is **permanently UNMEASURABLE**.
Registering `model-redesign` against `verifiers.pbi_model_change` would have wired a gate that
cannot pass — the trap F87 was recorded about. `R2` is the mechanism M4 said was missing, so it
takes M4's place for this ticket type **and only for this ticket type**.

⛔ ⭐ **M1-M12 certify GP-318's signature defect as green.** Measured 2026-08-31: evidence in
which the Brand slicer responds, every visual paints, every anchor holds and `ME Spend` returns
**the grand total for every single brand** scores `PASS=12`. The `model-redesign` preset names
that defect in its own `model_why` — *"a slice that returns the grand total on every member — it
neither errors nor blanks, so it looks healthy"* — and not one of the twelve assertions can see
it. `M11` is satisfied by `responded: True`, which a repainting visual reports whether or not the
number changed. **`interact` asks whether the control responded; `slices` asks whether the numbers
actually moved.** Only the second can see an inert axis, and `R3` is that assertion.

⚠ **What this module does NOT claim.** It does not make a redesign safe, and R1-R4 are not a
complete theory of one. They are the four things GP-318 proved a review misses: the pre-state that
was never captured, the rename whose dependents nobody rewrote, the axis that was inert all along,
and the measures that were captured and then quietly not replayed.
"""
from __future__ import annotations

from typing import List, Optional

from .contract import Assertion, GreenContract, Unmeasurable
from .pbi_contract import PbiTarget, Probes, _close, build_contract

#: The assertion R2 stands in for. Named so the swap is checked rather than assumed — if
#: `pbi_contract` renames it, this module refuses to build instead of silently dropping a check.
REPLACES = "M4-additive-manifest"


def _structured(entries: List) -> bool:
    """Renames/deletions reported as objects rather than bare names.

    A bare `"GASP"` says an object was renamed and says nothing about what pointed at it, which
    is the only part that can break a report. Bare entries are UNMEASURABLE, never PASS.
    """
    return bool(entries) and all(isinstance(e, dict) for e in entries)


def build_redesign_contract(target: PbiTarget, probes: Optional[Probes] = None) -> GreenContract:
    """M1-M12 with M4 replaced by R2, plus R1, R3 and R4 in the layer each belongs to."""
    p = probes or Probes()

    # ------------------------------------------------------------------ preflight
    def r1(ctx):
        """The pre-state was captured BEFORE the overwrite, across the whole population.

        The preset's prohibition is explicit: *"Must not overwrite live model state without
        asserting the before state first."* M1 covers the rollback artefact — a file you could
        re-apply. This is the measured before-state, which is what a pre/post battery replays
        against, and they are different things: a TMSL backup tells you nothing about what the
        model evaluated to.

        ⚠ Population, never sample. GP-318 audited 356 measures. A redesign checked against the
        measures somebody thought to list is checked against their memory.
        """
        if not target.population:
            raise Unmeasurable(
                "the population was not enumerated — a redesign checked against a sample is not "
                "checked. Declare every measure that existed before the change")
        pre = p.pre_state(ctx)
        if not pre.get("captured_before_change"):
            return False, ("the before-state was recorded AFTER the overwrite — that is a "
                           "measurement of the damage, not a baseline to replay against")
        vals = pre.get("measures")
        if vals is None:
            raise Unmeasurable("the pre-state probe returned no measure values")
        missing = [m for m in target.population if m not in vals]
        if missing:
            raise Unmeasurable(
                f"{len(missing)} of {len(target.population)} measure(s) have no pre-state, so "
                f"whether the change moved them cannot be known: {', '.join(missing[:6])}"
                + (" ..." if len(missing) > 6 else ""))
        return True, f"{len(target.population)} measure(s) captured before the overwrite"

    def r2(ctx):
        """Every rename and deletion carries its dependents, enumerated and rewritten.

        Replaces M4 for this ticket type. M4's job was to refuse a non-additive change outright,
        because a **TOM rename does not rewrite the DAX that references the old name** and the
        dataset has live reports bound. A redesign has to rename; what must hold is not that it
        did not, but that every rename's dependents were found and fixed.

        M4's protected-object check is kept — a redesign is still not licence to touch the
        objects the target declared off limits.
        """
        w = p.writes(ctx)
        touched = set(w.get("touched") or [])
        clobbered = sorted(touched & set(target.protected_objects))
        if clobbered:
            return False, f"modified protected object(s): {', '.join(clobbered)}"

        # ⛔ `w.get("renamed") or []` collapsed two different facts into one value: the agent
        # reporting an empty list, and the agent never writing the key at all. Verified
        # 2026-08-31 — `{}` and `{"renamed": [], "deleted": []}` both returned
        # PASS / "nothing renamed or deleted — additive after all", indistinguishably.
        #
        # ⭐ The correct reasoning is already in this function, twelve lines below, for the
        # dependents list: *"An absent list is NOT-VISIBLE, not 'nothing depends on it' —
        # enumerate, never assume."* The same sentence applies one level up. A redesign whose
        # evidence file never mentions renames has not reported that it renamed nothing; it has
        # reported nothing, and R2 is the assertion about renames.
        reported = [k for k in ("renamed", "deleted") if k in w]
        if not reported:
            raise Unmeasurable(
                "the evidence file reports neither 'renamed' nor 'deleted', so whether this "
                "redesign renamed anything is unmeasured. An absent key is NOT-VISIBLE, not "
                "'additive after all' — report both keys, empty if genuinely empty")

        changes = list(w.get("renamed") or []) + list(w.get("deleted") or [])
        if not changes:
            return True, (f"nothing renamed or deleted — additive after all "
                          f"(declared explicitly: {', '.join(sorted(reported))})")
        if not _structured(changes):
            raise Unmeasurable(
                f"{len(changes)} rename/deletion(s) reported as bare names, so whether anything "
                "still points at them is unmeasured. A TOM rename does not rewrite dependent "
                "DAX — report each as an object with its dependents")

        unenumerated = [c for c in changes if c.get("dependents") is None]
        if unenumerated:
            raise Unmeasurable(
                f"{len(unenumerated)} rename/deletion(s) list no dependents. An absent list is "
                "NOT-VISIBLE, not 'nothing depends on it' — enumerate, never assume")

        broken = [f"{c.get('object')} ({len(c.get('dependents') or [])} dependent(s))"
                  for c in changes
                  if (c.get("dependents") or []) and not c.get("dependents_rewritten")]
        if broken:
            return False, ("renamed or deleted with dependents left pointing at the old name: "
                           + "; ".join(broken))
        n_deps = sum(len(c.get("dependents") or []) for c in changes)
        return True, f"{len(changes)} rename/deletion(s), {n_deps} dependent(s) rewritten"

    # ------------------------------------------------------------------ model layer
    def r4(ctx):
        """Every captured measure was replayed. The 'post' half of the pre/post battery.

        ⚠ This is a COVERAGE assertion, not a value one. M7 checks that the measures declared
        out-of-scope did not move; R4 checks that nothing captured was quietly dropped from the
        comparison. A battery that captures 356 and replays 40 has not found that 316 are fine —
        it has not looked at them, and the difference is the whole point of this repository.
        """
        pre = p.pre_state(ctx)
        before = pre.get("measures")
        if before is None:
            raise Unmeasurable("the pre-state probe returned no measure values to replay against")
        d = p.dax(ctx)
        after = d.get("measures")
        if after is None:
            raise Unmeasurable("DAX probe returned no measure values")
        unreplayed = [m for m in before if m not in after]
        if unreplayed:
            raise Unmeasurable(
                f"{len(unreplayed)} of {len(before)} captured measure(s) were never replayed, so "
                f"the battery covered part of the population: {', '.join(unreplayed[:6])}"
                + (" ..." if len(unreplayed) > 6 else ""))
        return True, f"all {len(before)} captured measure(s) replayed after the change"

    # ------------------------------------------------------------------ consumer layer
    def r3(ctx):
        """⭐ No declared axis is inert — the assertion the M-contract cannot make.

        GP-318's defect class, in the preset's own words: *a slice that returns the grand total
        on every member — it neither errors nor blanks, so it looks healthy.* M11 asks whether
        the control responded, and a repainting visual reports `responded: True` whether or not
        the number changed. This asks whether the numbers differed.

        ⚠ An unexercised pair is UNMEASURABLE, never PASS. "We did not slice that measure by
        that dimension" is not evidence that slicing it works.
        """
        if not target.must_slice_by:
            raise Unmeasurable(
                "no measure/dimension pair was declared as needing to slice, so the defect this "
                "ticket type exists to find — an axis that returns the grand total on every "
                "member — is unmeasured. Declaring none is not the same as finding none")
        obs = p.slices(ctx).get("measures")
        if obs is None:
            raise Unmeasurable("the slicing harness returned no per-member values")

        unexercised, thin, inert = [], [], []
        for measure, dims in target.must_slice_by.items():
            for dim in dims:
                cell = (obs.get(measure) or {}).get(dim)
                if not cell or cell.get("values") is None:
                    unexercised.append(f"{measure} by {dim}")
                    continue
                values = [v for v in cell["values"] if v is not None]
                if len(values) < 2:
                    thin.append(f"{measure} by {dim} ({len(values)} member(s))")
                    continue
                if len({round(float(v), 6) for v in values}) > 1:
                    continue
                total = cell.get("grand_total")
                same = values[0]
                if total is not None and _close(same, total, target.tolerance):
                    inert.append(f"{measure} by {dim}: every member returns {same}, which IS the "
                                 "grand total — the measure is ignoring the filter context")
                else:
                    inert.append(f"{measure} by {dim}: every member returns the same {same}")

        if unexercised:
            raise Unmeasurable(
                f"{len(unexercised)} declared pair(s) were never sliced, so inertness is "
                f"unmeasured for them: {', '.join(unexercised[:6])}"
                + (" ..." if len(unexercised) > 6 else ""))
        if thin:
            raise Unmeasurable(
                "a single member cannot show whether an axis slices: " + "; ".join(thin[:6]))
        if inert:
            return False, "; ".join(inert)
        n = sum(len(d) for d in target.must_slice_by.values())
        return True, f"{n} axis/axes each produced differing values across their members"

    # ------------------------------------------------------------------ assembly
    base = build_contract(target, p)
    names = [a.name for a in base.assertions]
    if REPLACES not in names:
        # ⛔ Refuse rather than silently ship a redesign contract with one fewer check than it
        # thinks it has. If pbi_contract renames M4, this must be looked at, not guessed past.
        raise RuntimeError(
            f"{REPLACES!r} is not in the M-contract ({names}) — redesign_contract replaces it "
            "with R2 and cannot verify the substitution happened")

    out: List[Assertion] = []
    for a in base.assertions:
        if a.name == REPLACES:
            out.append(Assertion("R2-renames-carry-their-dependents", r2,
                                 description="a rename does not rewrite dependent DAX; this says"
                                             " somebody did"))
            continue
        out.append(a)
        if a.name == "M1-rollback-captured-first":
            out.append(Assertion("R1-pre-state-captured-over-the-population", r1,
                                 description="the before state was measured first, and covers"
                                             " every measure rather than a sample"))
        elif a.name == "M7-no-regression":
            out.append(Assertion("R4-every-captured-measure-was-replayed", r4,
                                 description="the battery replayed everything it captured"))
        elif a.name == "M11-controls-respond":
            out.append(Assertion("R3-no-axis-is-inert", r3,
                                 description="the control responded AND the numbers differed"
                                             " across its members"))
    return GreenContract(f"pbi-model-redesign/{target.dataset_id}", out)
