#!/usr/bin/env python
"""Instantiate `marketing-model-reconstruction-v1` in the existing TaskStore.

    python scripts/mission_marketing_model.py --plan     # print, write nothing
    python scripts/mission_marketing_model.py --create   # create it (idempotent)
    python scripts/mission_marketing_model.py --status   # where the mission is now

⭐ **Nothing new is built.** The mission is a parent task; every task is a child of it; dependencies
are `TaskStore.block()` edges. `factory/` has no `mission` concept and no `depends_on` field — both
were checked on 2026-08-31 and neither exists — but `create(parent=…)` plus `block()` supply exactly
the shape, and `2da0c097` ("Absorption backlog") already uses parent/child this way, so this is the
house pattern rather than an invention.

⚠ **The store is append-only, so re-running must not duplicate.** `--create` looks for the mission
by title first and refuses if it is already there. Append-only means a mistake is permanent: there
is no delete, only an `abandoned` close.

**Contract fields live beside the store, not in it.** `Task` carries id/title/owner/parent/status/
blocked_by/evidence and nothing else — no estimate, no capability class, no resource claim. Rather
than widen a core dataclass for one mission, the contract is written to
`.data/missions/<id>.json` keyed by task id. If a second mission needs the same fields, *that* is
the evidence for widening `Task`; one mission is not.

⛔ **Estimates here are ASSUMED and recorded before launch on purpose.** They are the hypothesis the
run tests. Do not tune them after seeing an actual — that turns the dataset into a record of
hindsight. See `docs/specs/marketing-model-reconstruction-v1.md` §4.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from factory.tasks import TaskStore                                        # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
STORE = ROOT / ".data" / "tasks.jsonl"
MANIFEST = ROOT / ".data" / "missions" / "marketing-model-reconstruction-v1.json"

MISSION = "marketing-model-reconstruction-v1 — GEP cross-channel marketing model (READ ONLY)"
ACTOR = "paul"

#: label, title, blocked_by(labels), resource claim, access, capability class, estimate (minutes)
#: Capability classes are ASSUMED — a hypothesis the run tests, not a routing rule it obeys.
#: Every task runs the Opus 5 / effort-max baseline in run 1 regardless.
TASKS = [
    ("R1", "Stakeholder & client-evidence reconstruction — what GEP actually asked for, and when",
     [], "res-gep-evidence", "READ", "STRONG", 45),
    # ⚠ R2 must read BOTH repos. Three prior Navira designs live in aldc-launchpad/docs/readouts/
    # (gp319-marketing-model-designs.html, NAVIRA-MARKETING-MODEL-GUIDE.html/.pdf), not in the wiki.
    # A diff that reads one repo and reports "no prior design exists" is a blind instrument.
    ("R2", "Repo + wiki + aldc-launchpad DIFF — the 2 wiki pages AND the 3 launchpad readouts; "
           "what is locked, stale, missing",
     [], "res-wiki-clients-repo", "READ", "STRONG", 45),
    ("R3", "Snowflake / data cartography — what marketing data exists, at what grain, what keys",
     [], "res-snowflake-read", "READ", "STRONG", 60),
    ("D1", "Requirements & uncertainty synthesis — CONFIRMED / SUPPORTED / INFERRED / ASSUMPTION / UNKNOWN",
     ["R1", "R2", "R3"], "res-mission-artifacts", "WRITE", "DEEP", 45),
    ("D2", "Analytical question catalogue — the questions the model must answer",
     ["D1"], "res-mission-artifacts", "WRITE", "STRONG", 30),
    ("D3", "Candidate dimensional designs — run `keel`; declare the grain FIRST",
     ["D2"], "res-mission-artifacts", "WRITE", "DEEP", 90),
    ("D4", "Skeptical review — try to falsify D3's grain and key claims",
     ["D3"], "res-mission-artifacts", "WRITE", "DEEP", 45),
    ("D5", "Recommendation + human sign-off",
     ["D4"], "res-mission-artifacts", "WRITE", "STRONG", 30),
]


def waves(edges: dict) -> list:
    """Derive the parallel waves from the dependency edges. Computed, never typed.

    A wave is every task whose blockers have all landed in an earlier wave. This is the number the
    mission's parallelism claim rests on, so it is derived from the same edges the store holds
    rather than asserted in prose beside them.
    """
    done, out, remaining = set(), [], {k: set(v) for k, v in edges.items()}
    while remaining:
        ready = sorted(k for k, deps in remaining.items() if deps <= done)
        if not ready:
            raise SystemExit(f"cycle or unreachable dependency among {sorted(remaining)}")
        out.append(ready)
        done |= set(ready)
        for k in ready:
            remaining.pop(k)
    return out


def _existing(store: TaskStore):
    return next((t for t in store.all() if t.title == MISSION), None)


def plan() -> None:
    edges = {lbl: deps for lbl, _t, deps, *_ in TASKS}
    w = waves(edges)
    by = {lbl: (title, claim, access, cap, est) for lbl, title, _d, claim, access, cap, est in TASKS}
    seq = sum(t[6] for t in TASKS)
    wall = sum(max(by[l][4] for l in wave) for wave in w)
    print(f"MISSION  {MISSION}\n")
    for i, wave in enumerate(w, 1):
        tag = "PARALLEL" if len(wave) > 1 else "serial"
        print(f"  wave {i}  ({tag}, {len(wave)} task(s), {max(by[l][4] for l in wave)}m)")
        for l in wave:
            title, claim, access, cap, est = by[l]
            print(f"    {l:<3} {est:>3}m  {cap:<7} {access:<5} {claim:<22} {title[:44]}")
    print(f"\n  sequential estimate   {seq}m ({seq/60:.1f}h)")
    print(f"  parallel wall-clock   {wall}m ({wall/60:.1f}h)   <- the prediction run 1 tests")
    print(f"  claimed saving        {seq - wall}m")
    print("\n  ⚠ estimates and capability classes are ASSUMED, recorded before launch.")


def create() -> None:
    store = TaskStore(STORE)
    if (t := _existing(store)) is not None:
        raise SystemExit(
            f"mission already exists as {t.id} ({t.status}). The store is append-only — creating it "
            f"again would leave two missions with the same title and no way to tell which is real. "
            f"Use --status.")

    mid = store.create(MISSION, actor=ACTOR)
    ids, contracts = {}, {}
    for lbl, title, _deps, claim, access, cap, est in TASKS:
        tid = store.create(f"{lbl} · {title}", actor=ACTOR, parent=mid)
        ids[lbl] = tid
        contracts[tid] = {"label": lbl, "resource_claim": claim, "access": access,
                          "capability_class": cap, "estimate_minutes": est,
                          "estimate_basis": "ASSUMED",
                          "model": "claude-opus-5", "effort": "max",
                          "evidence_required": "ANALYSIS",
                          "expected_output": f"docs/evidence/marketing-model-v1/{lbl}.md"}
    for lbl, _t, deps, *_ in TASKS:
        for d in deps:
            store.block(ids[lbl], by=ids[d], actor=ACTOR)

    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(
        {"mission": MISSION, "mission_task": mid, "labels": ids, "contracts": contracts,
         "spec": "docs/specs/marketing-model-reconstruction-v1.md"}, indent=2), encoding="utf-8")
    print(f"created mission {mid} with {len(ids)} tasks")
    print(f"manifest -> {MANIFEST}")


def remanifest() -> None:
    """Rebuild the manifest from the store + TASKS, without touching the append-only store.

    Needed because the contract fields live beside the store rather than in it, so a correction to
    a claim key, estimate or capability class must be re-derivable. It matches tasks by the `<label>
    ·` prefix in the title — the label is the only stable join, since task ids are uuids the store
    generated. Existing task ids are preserved; nothing is created.
    """
    store = TaskStore(STORE)
    if (m := _existing(store)) is None:
        raise SystemExit("mission not created yet — run --create")
    by_label = {t.title.split(" · ", 1)[0]: t.id
                for t in store.all() if t.parent == m.id and " · " in t.title}
    missing = [lbl for lbl, *_ in TASKS if lbl not in by_label]
    if missing:
        raise SystemExit(f"cannot rebuild — no task in the store for {missing}")
    contracts = {by_label[lbl]: {"label": lbl, "resource_claim": claim, "access": access,
                                 "capability_class": cap, "estimate_minutes": est,
                                 "estimate_basis": "ASSUMED",
                                 "model": "claude-opus-5", "effort": "max",
                                 "evidence_required": "ANALYSIS",
                                 "expected_output": f"docs/evidence/marketing-model-v1/{lbl}.md"}
                 for lbl, _t, _d, claim, access, cap, est in TASKS}
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(
        {"mission": MISSION, "mission_task": m.id, "labels": by_label, "contracts": contracts,
         "spec": "docs/specs/marketing-model-reconstruction-v1.md"}, indent=2), encoding="utf-8")
    print(f"rebuilt manifest for {m.id} — {len(contracts)} contracts, store untouched")


def status() -> None:
    store = TaskStore(STORE)
    if (m := _existing(store)) is None:
        raise SystemExit("mission not created yet — run --create")
    man = json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.exists() else {}
    contracts = man.get("contracts", {})
    print(f"MISSION {m.id}  {m.status}  {m.title}\n")
    for t in store.all():
        if t.parent != m.id:
            continue
        c = contracts.get(t.id, {})
        blockers = [contracts.get(b, {}).get("label", b[:6]) for b in t.blocked_by]
        state = "BLOCKED_DEPENDENCY" if blockers else t.status.upper()
        print(f"  {c.get('label','??'):<3} {t.id}  {state:<19} "
              f"{c.get('estimate_minutes','?'):>3}m {c.get('capability_class',''):<7} "
              f"ev={len(t.evidence)}  " + (f"waits on {','.join(blockers)}" if blockers else ""))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--plan", action="store_true")
    g.add_argument("--create", action="store_true")
    g.add_argument("--status", action="store_true")
    g.add_argument("--remanifest", action="store_true",
                   help="rebuild the contract manifest from TASKS; does not touch the store")
    a = ap.parse_args(argv)
    for name, fn in (("plan", plan), ("create", create),
                     ("status", status), ("remanifest", remanifest)):
        if getattr(a, name):
            fn()
            return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
