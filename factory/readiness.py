"""Readiness: can an agent team run a connector migration unattended?

This is not a checklist. Every gate below is *measured* from a file at the moment
you run it, and each result carries the path it was measured from. A gate that
cannot be measured says so — it does not quietly pass.

The verdicts are the contract's four, and they are never collapsed:

    PASS         the gate is satisfied, and the instrument was live
    FAIL         the gate is not satisfied
    UNMEASURABLE no instrument could be established — NOT a pass
    NOT_RUN      the work has not started

Run it:  python -m factory.readiness
Point at a different checkout with $PREFECT_CONNECTORS.
"""
from __future__ import annotations

import ast
import collections
import re
import functools
import glob
import hashlib
import json
import os
import sys
import pathlib
import subprocess
import time
from dataclasses import dataclass, field
from typing import Callable, List, Optional

PASS, FAIL, UNMEASURABLE, NOT_RUN = "PASS", "FAIL", "UNMEASURABLE", "NOT_RUN"

FACTORY = pathlib.Path(__file__).resolve().parent.parent
CONNECTORS = pathlib.Path(
    os.environ.get("PREFECT_CONNECTORS", FACTORY.parent / "prefect-connectors")
)


class Unmeasurable(Exception):
    """No instrument could be established. Distinct from a failure."""


# --------------------------------------------------------------------------- model


@dataclass
class Gate:
    id: str
    question: str
    why: str
    probe: Callable[[], "Result"]
    phase: str = "loop"


@dataclass
class Result:
    verdict: str
    headline: str
    evidence: List[str] = field(default_factory=list)
    source: str = ""

    @property
    def ok(self) -> bool:
        return self.verdict == PASS


def _pass(h, ev=None, src=""):
    return Result(PASS, h, ev or [], src)


def _fail(h, ev=None, src=""):
    return Result(FAIL, h, ev or [], src)


def _notrun(h, ev=None, src=""):
    return Result(NOT_RUN, h, ev or [], src)


# --------------------------------------------------------------------------- instruments


#: The date the control primitives landed (cap, bounded, concurrency, reaper, from-history —
#: prefect-connectors `0a5c393`). Runs before it are the OLD, uncontrolled system: real evidence
#: of what happened, and no evidence at all about what the controls do.
#:
#: Two gates were unpassable without this, and not by a margin — by construction (F20/F21).
#: `finishes` required EVERY recorded run to be terminal while four sit at stage_started forever,
#: so each new run raised both sides and equality was unreachable. `succeeds` was an all-time
#: ratio needing 837 net successful stages, permanently carrying one capped incident. A gate that
#: cannot pass is the mirror of one that cannot refuse: it stops measuring the work and starts
#: reporting failure at work already done.
#:
#: ⚠ Windowing is NOT forgiving. An empty window is UNMEASURABLE, never PASS — "no runs since the
#: controls landed" is the honest answer today and must not read as "the controls work". Excluded
#: runs are named in the evidence so nothing hides, and the audits are never deleted, because the
#: `bounded` gate cites them.
MEASURED_SINCE = "2026-08-22"


def _started(run: dict) -> str:
    """Earliest event timestamp in a run, or '' when it carries none."""
    ts = [e.get("timestamp", "") for e in run.get("events", []) if e.get("timestamp")]
    return min(ts) if ts else ""


def _since(runs: List[dict], since: str = MEASURED_SINCE):
    """(in_window, excluded). ISO-8601 sorts lexically, so a prefix compare is the whole test."""
    inw = [r for r in runs if _started(r) >= since]
    ids = {id(r) for r in inw}
    return inw, [r for r in runs if id(r) not in ids]


@functools.lru_cache(maxsize=8)
def _revision_of(root: str) -> str:
    """Uncached body of :func:`revision`, keyed on the checkout so a test may repoint it.

    ⚠ **Cached because it is called from `_basis()`, which several gates call on every
    `measure()`.** Uncached, this shelled out to git twice per call — and on Windows a subprocess
    spawn is expensive enough that it took `tests/test_roadmap.py` (20 tests, each a full
    `measure()`) from seconds to over 100. Caught by the suite timing out, not by review. A
    revision cannot change inside one process without someone deliberately repointing
    `CONNECTORS`, and the key covers that.
    """
    try:
        b = subprocess.run(["git", "-C", root, "rev-parse", "--abbrev-ref", "HEAD"],
                           capture_output=True, text=True, timeout=15)
        h = subprocess.run(["git", "-C", root, "rev-parse", "--short", "HEAD"],
                           capture_output=True, text=True, timeout=15)
        br, sha = (b.stdout or "").strip(), (h.stdout or "").strip()
        if not sha:
            return "unknown-revision"
        return f"{br or 'DETACHED'}@{sha}"
    except Exception:                                              # noqa: BLE001
        return "unknown-revision"


def revision() -> str:
    """What `$PREFECT_CONNECTORS` is checked out at, as `branch@sha`, or a stated unknown.

    ⭐ **A board that names a path but not a revision cannot be compared with itself.** F72
    recorded that this board reads 9 or 10 at the same commit depending only on cwd. F80 is the
    same defect one turn deeper: the bounding controls were built on `lane/control-plane` and the
    board measured `chore/artefact-homes`, so five gates reported controls "missing" that existed
    in the same repository, on a branch nobody had named. Two boards taken an hour apart either
    side of a `git checkout` in a sibling repo are incomparable, and nothing said so.

    Never raises. A revision that cannot be read is `unknown-revision`, which is still a truer
    thing to print than nothing.
    """
    return _revision_of(str(CONNECTORS))


def _basis(extra: str = "") -> str:
    """Every windowed gate states where and when it measured. A number without its basis is the
    defect F72 recorded: this board reads 9 or 10 at the same commit depending only on cwd."""
    return (f"basis: runs since {MEASURED_SINCE} · connectors {CONNECTORS} @ {revision()}"
            + (f" · {extra}" if extra else ""))


def _audits() -> List[dict]:
    """Every recorded pipeline run. Raises rather than returning an empty list —
    a zero from an instrument that cannot see is not a measurement."""
    d = CONNECTORS / "orchestrator" / "data" / "audits"
    if not d.is_dir():
        raise Unmeasurable(f"no audit directory at {d} — set $PREFECT_CONNECTORS")
    files = sorted(glob.glob(str(d / "*.json")))
    if not files:
        raise Unmeasurable(f"{d} holds no run files — nothing to measure")
    runs = []
    for f in files:
        try:
            ev = json.load(open(f, encoding="utf-8"))
        except Exception as exc:  # a corrupt run is not an absent one
            raise Unmeasurable(f"{os.path.basename(f)} will not parse: {exc}")
        if isinstance(ev, dict):
            ev = ev.get("events", list(ev.values()))
        runs.append({"id": os.path.basename(f)[:-5],
                     "events": [e for e in ev if isinstance(e, dict)]})
    return runs


def _events(runs) -> List[dict]:
    return [e for r in runs for e in r["events"]]


def _counts(runs) -> collections.Counter:
    return collections.Counter(e.get("event_type") for e in _events(runs))


# --------------------------------------------------------------------- driving the build plane

#: Imported once. `orchestrator/pipelines.py` is ~100KB and five probes drive it.
_ENGINE: dict = {}


def _engine():
    """Import the build plane's control module and hand it back with its writes muted.

    ⭐ **This exists so a control-plane gate can WATCH A CONTROL REFUSE rather than read the
    source for a word.** `tests/test_readiness_probes_can_pass.py::
    test_the_control_plane_probes_watch_rather_than_grep` has required this since 2026-08-22 and
    there was nothing to call: `_engine` did not exist, so the test was a specification with no
    implementation and five probes went on grepping. The cost of grepping was measured twice —
    `g_concurrency_is_reserved_outside_the_agent` searched case-sensitively for `max_parallel`
    while the code spelled it `MAX_PARALLEL_STAGE_DISPATCH`, and reported "concurrency is bounded
    per wave, not per stage dispatch" about a module that bounds stage dispatch (F81).

    ⛔ **Writes are muted, and that is not optional.** `pipelines._refuse` records an audit event
    *before* handing back the exception — deliberately, so a control cannot fire unseen. But
    `_audits()` reads that same directory, so a probe that drove a control without muting would
    write the evidence another probe then measures. A gate that manufactures its own input is not
    an instrument. `audit_trail._append_event` and `event_bus.emit` are replaced with no-ops for
    the life of the process.

    Raises :class:`Unmeasurable` when the module will not import. An engine that cannot be loaded
    is *not* a failed control — it is no measurement at all, and the difference is the reason the
    four verdicts exist.
    """
    # ⚠ Keyed on the checkout, not a bare flag. `CONNECTORS` is monkeypatched by tests and by
    # anyone comparing two branches, and a cache that ignored it would hand back the engine from
    # whichever checkout was measured first — a probe reporting on a revision it never loaded.
    root = str(CONNECTORS)
    if root in _ENGINE:
        return _ENGINE[root]
    if not (CONNECTORS / "orchestrator" / "pipelines.py").is_file():
        raise Unmeasurable(
            f"no orchestrator/pipelines.py at {CONNECTORS} — set $PREFECT_CONNECTORS to a "
            "checkout that carries the build plane")
    if root not in sys.path:
        sys.path.insert(0, root)
    try:
        import importlib
        # Drop any previously-imported copy: two checkouts share the module name, and the second
        # import would otherwise return the first checkout's module from sys.modules.
        for name in [n for n in list(sys.modules) if n.startswith("orchestrator")]:
            del sys.modules[name]
        mod = importlib.import_module("orchestrator.pipelines")
    except Exception as exc:                                       # noqa: BLE001
        raise Unmeasurable(f"orchestrator.pipelines will not import from {CONNECTORS}: "
                           f"{type(exc).__name__}: {exc}")
    # Mute the two write paths a driven control touches. Best-effort by design: a missing
    # attribute means that write path does not exist in this revision, which is not an error.
    for target, attr in ((getattr(mod, "audit_trail", None), "_append_event"),
                         (getattr(mod, "event_bus", None), "emit")):
        if target is not None and hasattr(target, attr):
            setattr(target, attr, lambda *a, **k: None)
    _ENGINE[root] = mod
    return mod


def _stage(name: str = "extract", **kw) -> dict:
    """A synthetic stage record. The controls read plain dicts, so driving them needs no fixture."""
    s = {"name": name, "status": "pending", "_attempts": 0, "type": "task"}
    s.update(kw)
    return s


def _pipeline(pid: str = "readiness-probe", stages=None) -> dict:
    return {"id": pid, "stages": list(stages or [_stage()])}


def _refused(fn, *a, **kw):
    """Call a control and report whether it REFUSED. (refused, detail).

    A control that returns normally has allowed the thing; a `ControlRefused` is the refusal we
    are trying to observe; any other exception is an instrument problem, not a verdict, so it
    propagates as Unmeasurable rather than being read as a refusal.
    """
    mod = _engine()
    refused_cls = getattr(mod, "ControlRefused", None)
    if refused_cls is None:
        raise Unmeasurable("the engine defines no ControlRefused — nothing can be observed "
                           "refusing in this revision")
    try:
        fn(*a, **kw)
    except refused_cls as exc:
        return True, str(exc)[:200]
    except Exception as exc:                                       # noqa: BLE001
        raise Unmeasurable(f"driving {getattr(fn, '__name__', fn)} raised "
                           f"{type(exc).__name__}: {exc}")
    return False, "returned without refusing"


def _template(name="connector-migration") -> dict:
    p = CONNECTORS / "orchestrator" / "pipelines.py"
    if not p.is_file():
        raise Unmeasurable(f"no pipelines.py at {p}")
    tree = ast.parse(p.read_text(encoding="utf-8"))
    for n in tree.body:
        t = getattr(n, "target", None) or (
            n.targets[0] if isinstance(n, ast.Assign) and n.targets else None)
        if getattr(t, "id", None) == "PIPELINE_DEFS":
            defs = ast.literal_eval(n.value)
            if name not in defs:
                raise Unmeasurable(f"PIPELINE_DEFS has no '{name}'")
            return defs
    raise Unmeasurable("PIPELINE_DEFS not found in pipelines.py")


def _blueprint() -> dict:
    p = FACTORY / "blueprints" / "windsorai_client_a.yaml"
    if not p.is_file():
        raise Unmeasurable(f"no blueprint at {p}")
    # Deliberately tiny: a real YAML parse would pull a dependency into a probe that must keep
    # working when the environment is broken. It handles scalars, `key: []`, and block lists.
    # It previously dropped block lists entirely -- `allowed_tenants:` set the key to "" and the
    # `- item` lines below it were skipped, so filling in six account ids left the gate still
    # reporting "empty". A probe that cannot see the fix is worse than no probe.
    out, key = {}, None
    for line in p.read_text(encoding="utf-8").splitlines():
        s = line.split("#")[0].rstrip()
        stripped = s.strip()
        if not stripped:
            continue
        if stripped.startswith("- ") or stripped == "-":
            if key is None:
                continue
            if not isinstance(out.get(key), list):
                out[key] = []          # promote: `key:` with nothing after it opens a block list
            out[key].append(stripped[1:].strip().strip("'\""))
            continue
        if ":" in s and not s.startswith(" "):
            key, _, v = s.partition(":")
            key, v = key.strip(), v.strip()
            if v == "[]":
                out[key] = []
            elif v == "":
                out[key] = ""          # may be promoted to a list by the lines beneath it
            else:
                out[key] = v.strip("'\"")
    return out


# --------------------------------------------------------------------------- gates


def g_finishes():
    runs = _audits()
    fin = {r["id"] for r in runs
           if any(e.get("event_type") == "pipeline_completed" for e in r["events"])}
    stuck = [r["id"] for r in runs
             if r["events"] and r["events"][-1].get("event_type") == "stage_started"]
    ev = [f"{len(fin)} of {len(runs)} recorded runs reached pipeline_completed"]
    if stuck:
        ev.append(f"{len(stuck)} sit at stage_started with no terminal event: "
                  + ", ".join(sorted(stuck)))
    src = "orchestrator/data/audits/*.json"
    inw, out = _since(runs)
    ev.append(_basis(f"{len(out)} run(s) started before it are excluded"))
    if not inw:
        raise Unmeasurable(
            f"no run started since {MEASURED_SINCE}, when the controls landed — "
            f"{len(runs)} older run(s) on record, {len(fin)} of them finished. Run the loop.")
    fin_w = [r for r in inw if r["id"] in set(fin)]
    if len(fin_w) == len(inw):
        return _pass(f"all {len(inw)} runs since {MEASURED_SINCE} finished", ev, src)
    return _fail(f"{len(fin_w)}/{len(inw)} runs since {MEASURED_SINCE} finished", ev, src)


def g_succeeds_more_than_fails():
    runs = _audits()
    allc = _counts(runs)
    inw, out = _since(runs)
    src = "orchestrator/data/audits/*.json"
    ev = [f"all-time: {allc['stage_failed']} stage_failed against {allc['stage_completed']} "
          f"stage_completed, {allc['restart_from_stage']} restarts",
          "all-time is NOT the rate now — most of those failures are the 2026-08-14 "
          "uncapped-restart incident, which the cap has since bounded",
          _basis(f"{len(out)} run(s) started before it are excluded")]
    if not inw:
        raise Unmeasurable(
            f"no run started since {MEASURED_SINCE}, when the controls landed — the all-time "
            f"ratio describes the uncontrolled system, not this one. Run the loop.")
    c = _counts(inw)
    done, failed = c["stage_completed"], c["stage_failed"]
    ev.insert(0, f"in window: {failed} stage_failed against {done} stage_completed")
    if failed == 0 and done == 0:
        raise Unmeasurable(f"{len(inw)} run(s) since {MEASURED_SINCE}, but not one stage outcome "
                           "recorded in any of them")
    if done > failed:
        return _pass(f"{done} succeed vs {failed} fail since {MEASURED_SINCE}", ev, src)
    return _fail(f"a stage attempt fails {failed / max(done,1):.1f}x more than it "
                 f"succeeds", ev, src)


def g_failure_is_bounded():
    """Can repetition get past the cap? `cap` asks whether it refuses; this asks whether it holds.

    ⭐ **This probe had exactly one return path — `_fail` — from the day it was written until
    2026-08-30.** It read the audits, computed the worst restart count, and returned "no attempt
    cap on restart" *whatever it found*, including a clean window. It was a constant wearing an
    instrument's clothes, and it sat in `launch.UNATTENDED_GATES` being read as a measurement of
    an unbounded system. Recorded 2026-08-22 in `test_readiness_probes_can_pass.py`'s docstring;
    the fix took eight days to arrive. F81.

    **What "bounded" means here, distinct from `cap`.** `check_attempt_cap` accepts an
    `override_reason` that buys one further attempt, and the estate's own history is the reason:
    on 2026-08-14 an unoverridable cap was got past by *deleting the pipeline*, destroying the
    evidence with the loop. So an override is correct — but it must be **single-shot**. An
    override that can be replayed is not a bound, it is a slower loop. That is the property
    driven below.
    """
    src = f"{CONNECTORS}/orchestrator/pipelines.py :: check_attempt_cap (driven) + audits"
    mod = _engine()
    fn = getattr(mod, "check_attempt_cap", None)
    cap = getattr(mod, "MAX_ATTEMPTS_PER_STAGE", None)
    if fn is None or cap is None:
        raise Unmeasurable("the engine exposes no attempt cap to drive")

    st = _stage(_attempts=int(cap) + 1)
    pl = _pipeline(stages=[st])
    first, _ = _refused(fn, pl, st, "restart_from_stage")
    granted, _ = _refused(fn, pl, st, "restart_from_stage", "one more, investigating")
    # After the override is spent, the SAME stage at the SAME attempt count must refuse again.
    after, _ = _refused(fn, pl, st, "restart_from_stage")

    ev = [f"cap = {cap}",
          f"over the cap -> {'REFUSED' if first else 'ALLOWED'}",
          f"with an override reason -> {'REFUSED' if granted else 'ALLOWED (one grant)'}",
          f"replaying the same override -> {'REFUSED' if after else 'ALLOWED'}"]

    # The audits are history, cited as evidence and never as the verdict: the 2026-08-14 incident
    # is permanent, and a gate whose verdict reads it can never go green no matter what is built.
    try:
        runs = _audits()
        inw, excluded = _since(runs)
        per = []
        for r in inw:
            c = collections.Counter(e.get("stage_name") for e in r["events"]
                                    if e.get("event_type") == "restart_from_stage")
            if c:
                per.append((r["id"],) + c.most_common(1)[0])
        worst = max(per, key=lambda x: x[2]) if per else None
        ev.append(f"in-window runs: {len(inw)}; excluded as pre-controls: {len(excluded)}")
        ev.append(f"worst in-window: {worst[2]} restarts of '{worst[1]}' in {worst[0]}"
                  if worst else "no restart events in the window")
        ev.append(_basis())
    except Unmeasurable as exc:
        ev.append(f"audit history not readable ({exc}) — verdict rests on the driven control")

    ev.append("history: the 2026-08-14 incident is recorded verbatim in pipelines.py — the stage "
              "was 'auto-restarted with no attempt cap' and ten containers took the whole 10-core "
              "canadacentral quota. Cited as evidence, never as this gate's verdict.")

    if first and after and not granted:
        return _pass("failure is bounded: the cap refuses, an override buys exactly one, "
                     "and replay refuses again", ev, src)
    if not first:
        return _fail("no attempt cap on restart", ev, src)
    return _fail("the override is not single-shot — a replayable override is a slower loop",
                 ev, src)


def g_gates_can_refuse():
    runs = _audits()
    gate_ev = [e for e in _events(runs) if e.get("event_type") == "gate_approved"]
    rejected = [e for e in _events(runs)
                if "reject" in str(e.get("event_type", "")).lower()]
    notes = collections.Counter(
        (e.get("details") or e.get("data") or {}).get("notes", "") for e in gate_ev)
    ev = [f"{len(gate_ev)} gate events recorded, {len(rejected)} of them a refusal"]
    for note, n in notes.most_common():
        ev.append(f'{n} x "{note}"' if note else f"{n} x (empty note)")
    src = "orchestrator/data/audits/*.json"
    if not gate_ev:
        raise Unmeasurable("no gate events recorded — cannot tell whether a gate refuses")
    if rejected:
        return _pass(f"a gate has refused {len(rejected)} times", ev, src)
    return _fail("no gate has ever refused a run", ev, src)


def g_gates_have_checks():
    defs = _template()
    gates = [(k, s) for k, v in defs.items() for s in v.get("stages", [])
             if s.get("type") == "gate"]
    checked = [(k, s) for k, s in gates if s.get("gate_check")]
    ev = [f"{len(checked)} of {len(gates)} gates across all pipelines have a gate_check"]
    for k, s in gates:
        if not s.get("gate_check"):
            ev.append(f"{k}/{s['name']} — {s.get('gate_type')}, check=None")
    src = "orchestrator/pipelines.py :: PIPELINE_DEFS"
    if len(checked) == len(gates):
        return _pass("every gate has a check", ev, src)
    return _fail(f"{len(gates)-len(checked)} gates have no programmatic check", ev, src)


def g_success_means_correct():
    runs = _audits()
    bad = []
    for r in runs:
        fin = any(e.get("event_type") == "pipeline_completed" for e in r["events"])
        f = sum(1 for e in r["events"] if e.get("event_type") == "stage_failed")
        if fin and f:
            bad.append((r["id"], f))
    src = "orchestrator/data/audits/*.json"
    if not bad:
        return _pass("no completed run carried failures", [], src)
    ev = [f"{len(bad)} completed run(s) carried recorded failures"]
    ev += [f"{i} reported completed after {n} stage_failed events" for i, n in bad]
    return _fail("a run reports success over failures it could not see", ev, src)


def g_cost_survives_failure():
    p = CONNECTORS / "orchestrator" / "pipelines.py"
    if not p.is_file():
        raise Unmeasurable(f"no pipelines.py at {p}")
    runs = _audits()
    with_cost = collections.Counter()
    for e in _events(runs):
        d = e.get("details") or e.get("data") or {}
        if isinstance(d, dict) and d.get("cost_usd"):
            with_cost[e.get("event_type")] += 1
    src = "orchestrator/data/audits/*.json"
    ev = [f"events carrying a non-zero cost_usd: "
          + (", ".join(f"{k}={v}" for k, v in with_cost.most_common()) or "none")]
    if with_cost.get("stage_failed"):
        return _pass("failures carry their cost", ev, src)
    ev.append("so a stage that failed 100 times contributes $0.00 — the real spend "
              "is unknown, not small")
    return _fail("cost is recorded only on success", ev, src)


def g_qa_gate_is_general():
    p = CONNECTORS / "orchestrator" / "stage_scripts" / "promotion_ops.py"
    if not p.is_file():
        raise Unmeasurable(f"no promotion_ops.py at {p}")
    txt = p.read_text(encoding="utf-8")
    src = "orchestrator/stage_scripts/promotion_ops.py"
    if "smoke-test-" in txt:
        line = next((i + 1 for i, l in enumerate(txt.splitlines())
                     if "smoke-test-" in l), None)
        return _fail("QA verification targets a smoke-test twin",
                     [f"{src}:{line} builds the deployment name as f\"smoke-test-{{connector}}\"",
                      "so it measures a twin, not the connector's own deployment"], src)
    return _pass("QA verification targets the connector's own deployment", [], src)


#: Where the suite verdict is remembered between renders. Under .data/, which is gitignored.
_SUITE_CACHE = FACTORY / ".data" / "suite-cache.json"

#: The negative control — "every assertion has been proved able to fail" — is the one claim this
#: project rests on, and replaying it from JSON forever would mean nobody ever re-earns it. So the
#: cache expires on a clock as well as on content. 12h costs ~9 s a day and buys a daily re-proof.
_SUITE_TTL_SEC = 12 * 3600

#: Environment the suite's verdict actually depends on. `CONNECTORS` resolves from
#: $PREFECT_CONNECTORS, and `test_measurement_window.py:105` asserts that path appears in gate
#: evidence — so the same bytes measured under a different checkout are a DIFFERENT verdict.
#: Leaving this out reintroduced F72 ("this board reads 9 or 10 at the SAME COMMIT depending only
#: on the cwd") through the cache door.
_SUITE_ENV = ("PREFECT_CONNECTORS", "AGENT_FACTORY_EVALUATOR", "AGENT_FACTORY_EVALS")


def _suite_inputs():
    """Every path whose bytes can change the suite's verdict. Enumerated, not assumed.

    ⚠ `scripts/` belongs here even though it is not a package: `tests/test_tracker_routes.py` and
    `tests/test_roadmap.py` both `from scripts import local_tracker`, so the 1,900-line UI is a
    suite input. Omitting it made the tracker the one file you could edit without invalidating the
    cache — while editing it was the whole activity. `docs/artifacts/agent-factory.html` is here
    for the same reason: `test_tracker_is_current.py` reads it.
    """
    for base in ("tests", "factory", "scripts"):
        d = FACTORY / base
        if d.is_dir():
            for f in sorted(d.rglob("*.py")):
                if "__pycache__" not in f.parts:
                    yield f
    for name in ("pyproject.toml", "docs/artifacts/agent-factory.html"):
        f = FACTORY / name
        if f.is_file():
            yield f


def _suite_fingerprint() -> str:
    """A content hash of everything that could change the suite's verdict.

    NOT a git SHA. A commit SHA is stable across uncommitted edits, which is precisely the state
    you are in while iterating — so a SHA-keyed cache would serve a stale green over code you had
    just broken. Hashing the bytes cannot do that.

    The environment is hashed alongside the bytes because the suite reads it. A fingerprint that
    covers only files is a claim that files are the only input, and here that claim is false.
    """
    h = hashlib.sha256()
    for f in _suite_inputs():
        h.update(str(f.relative_to(FACTORY)).encode())
        h.update(f.read_bytes())
    for k in _SUITE_ENV:
        h.update(f"{k}={os.environ.get(k, '')}".encode())
    h.update(f"CONNECTORS={CONNECTORS}".encode())
    return h.hexdigest()


def _age(seconds: float) -> str:
    """Render an age the way a person reads one. Never rounds up to hide staleness.

    Clamps at zero: a backward clock correction must not render "-3m ago", which reads as a
    glitch and invites the reader to ignore the age altogether.
    """
    s = max(0, int(seconds))
    if s < 60:
        return f"{s}s ago"
    if s < 3600:
        return f"{s // 60}m ago"
    if s < 86400:
        return f"{s // 3600}h {(s % 3600) // 60}m ago"
    return f"{s // 86400}d {(s % 86400) // 3600}h ago"


def _cache_write(payload: dict) -> None:
    """Atomically, or not at all.

    The server is threaded, so two cold viewers can reach this together. `write_text` interleaved
    yields invalid JSON, which the reader swallows and turns into a re-run — a cache miss becoming
    a thundering herd of pytest subprocesses, in an estate whose signature incident is ten
    containers taking the whole core quota.
    """
    try:
        _SUITE_CACHE.parent.mkdir(parents=True, exist_ok=True)
        tmp = _SUITE_CACHE.with_suffix(f".{os.getpid()}.tmp")
        tmp.write_text(json.dumps(payload), encoding="utf-8")
        os.replace(tmp, _SUITE_CACHE)
    except Exception:                                            # noqa: BLE001
        pass       # a cache that cannot be written must not fail the measurement it was speeding


def g_contract_suite_green():
    # The suite is 97.6% of a full measure() and every tab pays it. Cache it against the CONTENT
    # of tests/ and factory/ so an unchanged tree is not re-proved on every page refresh.
    #
    # ⚠ The cached verdict carries its age IN THE HEADLINE, never beside it. A number that has
    # been sitting in a cache is a different claim from one measured just now, and this whole
    # project exists because those two got rendered identically somewhere else.
    # ⛔ RECURSION GUARD, and it is load-bearing. This gate shells out to `python -m pytest`. Any
    # test that renders a measuring surface therefore re-enters here, spawns the whole suite again,
    # and that child does the same — an unbounded fan-out that ate 14 processes the first time a
    # test rendered the roadmap tab. A suite cannot measure itself from inside itself anyway: the
    # verdict would be "the run that is still running". So the child reports NOT-RUN and says why.
    if os.environ.get("AGENT_FACTORY_IN_SUITE") == "1":
        return _notrun("suite not re-run from inside itself",
                       ["AGENT_FACTORY_IN_SUITE=1 — this measurement is happening inside a pytest "
                        "run, so shelling out to pytest again would recurse without bound",
                        "the parent run's verdict is the real one"], "tests/")
    fp = _suite_fingerprint()
    try:
        cached = json.loads(_SUITE_CACHE.read_text(encoding="utf-8"))
    except Exception:                                            # noqa: BLE001
        cached = None
    fresh = (cached and cached.get("fingerprint") == fp
             and 0 <= (time.time() - cached["at"]) < _SUITE_TTL_SEC
             # ⚠ Only a PASS is ever served from cache. A cached FAIL is the F20/F21 shape: fix a
             # missing dependency — an environment change, not a byte change — and the board would
             # keep showing red for a suite that now passes. A gate that cannot pass is exactly as
             # broken as one that cannot refuse, so a red verdict is always re-earned.
             and cached.get("verdict") == PASS)
    if fresh:
        age = _age(time.time() - cached["at"])
        return Result(cached["verdict"],
                      f"{cached['headline']} (cached, last run {age})",
                      list(cached.get("evidence", []))
                      + [f"tests/, factory/, scripts/ and the environment are unchanged since "
                         f"that run (sha256 {fp[:12]})",
                         f"cache expires after {_SUITE_TTL_SEC // 3600}h so the negative control "
                         f"is re-earned on a clock, not replayed forever"],
                      cached.get("source", "tests/"))
    try:
        # No -q here: pyproject addopts already sets it, and -qq suppresses the
        # summary line this gate parses. The instrument was blind to its own config.
        env = dict(os.environ, AGENT_FACTORY_IN_SUITE="1")
        r = subprocess.run(["python", "-m", "pytest", "--no-header", "--tb=no",
                            "-p", "no:cacheprovider"],
                           cwd=FACTORY, capture_output=True, text=True, timeout=300, env=env)
    except Exception as exc:
        raise Unmeasurable(f"could not run the suite: {exc}")
    clean = re.sub("\x1b?\\[[0-9;]*m", "", r.stdout + "\n" + r.stderr)
    hits = re.findall(r"\d+ (?:passed|failed|error)[^\n]*", clean)
    # Drop the duration: it changes every run and is not a readiness fact, so
    # keeping it would make --check report stale against itself.
    line = re.sub(r" in [0-9.]+s", "", hits[-1].strip()) if hits         else "(pytest printed no summary line)"
    src = "tests/"
    if r.returncode == 0:
        res = _pass(line.strip(), ["includes test_every_assertion_has_been_proved_"
                                   "able_to_fail"], src)
    else:
        res = _fail(line.strip(), [], src)
    _cache_write({"fingerprint": fp, "at": time.time(), "verdict": res.verdict,
                  "headline": res.headline, "evidence": res.evidence, "source": res.source})
    return res


def g_output_is_certified():
    try:
        r = subprocess.run(["python", "-m", "factory.certify",
                            "blueprints/windsorai_client_a.yaml"], cwd=FACTORY,
                           capture_output=True, text=True, timeout=120)
    except Exception as exc:
        raise Unmeasurable(f"could not run certify: {exc}")
    head = (r.stdout or r.stderr).strip().splitlines()
    line = head[0] if head else "(no output)"
    src = "factory/certify.py"
    n_unmeas = sum(1 for l in head if "[UNMEASURABLE]" in l)
    if r.returncode == 0:
        return _pass(line, [], src)
    if n_unmeas:
        return _notrun(f"{n_unmeas} assertions have no instrument wired",
                       [line, "Probes refuses every instrument by design — this is "
                              "the harness declaring it has not measured, not a failure"],
                       src)
    return _fail(line, [], src)


def g_tenancy_declared():
    bp = _blueprint()
    tenants = bp.get("allowed_tenants") or []
    src = "blueprints/windsorai_client_a.yaml"
    if tenants:
        return _pass(f"{len(tenants)} tenant(s) declared", [str(tenants)], src)
    raise Unmeasurable(
        "allowed_tenants is empty — one ALDC Windsor key returns every client's "
        "accounts, so an unfiltered pull lands CLIENT-B rows in a CLIENT-A table and "
        "nothing downstream can tell. Blast radius is uncertifiable until someone "
        "writes the CLIENT-A account ids down.")


def g_corpus_is_tamper_evident():
    """Is the grader separable from the thing it grades, and is a change to it detectable?

    The first version of this gate checked whether factory/calibration.py existed, which measured
    file layout rather than the property that matters. Moving a file changes nothing if the file
    is still executable code that can construct any world it likes. What matters is:

      EVIDENT     a changed corpus raises instead of scoring differently
      ATTRIBUTED  a verdict names the corpus and hash it was scored against
      SEPARABLE   the corpus imports nothing from factory/, so it can be lifted out

    Separation is not yet ENFORCED — that needs the corpus in a repo the scored agent has no
    write credential for. This gate says so rather than passing on the strength of the other
    three.
    """
    import hashlib as _h
    from . import corpus as _c
    src = "evals/MANIFEST.sha256 + factory/corpus.py"
    try:
        pinned = _c.available()
    except _c.CorpusError as exc:
        return _fail("the corpus does not verify", [str(exc)[:200]], src)
    if not pinned:
        raise Unmeasurable("the manifest lists no corpus — nothing to verify")

    ev = [f"{len(pinned)} corpus file(s) pinned: " + ", ".join(sorted(pinned))]
    bad = []
    for cid in pinned:
        try:
            _c.load(cid)
        except _c.CorpusError as exc:
            bad.append(f"{cid}: {str(exc).splitlines()[0]}")
    if bad:
        return _fail("a pinned corpus does not match its hash", ev + bad, src)
    ev.append("every pinned corpus matches its manifest hash")

    # Is it data, or is it code? Code can construct a different world each import.
    code_corpus = [p for p in (FACTORY / "evals").rglob("*.py")]
    if code_corpus:
        ev.append("executable files under evals/: "
                  + ", ".join(p.name for p in code_corpus))
        return _fail("the corpus contains code, so its content is not fixed by its hash",
                     ev, src)
    ev.append("corpus is data only — no executable files under evals/")

    # Does a verdict carry it?
    if "scored_against" not in (FACTORY / "factory" / "certify.py").read_text(encoding="utf-8"):
        ev.append("certify emits no corpus provenance")
        return _fail("a verdict cannot be tied to the world that produced it", ev, src)
    ev.append("certify records corpus id + sha on every replayed verdict")

    ev.append("NOT ENFORCED: the corpus still lives in a repo this agent can write to. "
              "Tampering is evident, not prevented. $AGENT_FACTORY_EVALS makes the move a "
              "config change.")
    return _fail("tamper-evident, but separation is not enforced", ev, src)


def g_repo_is_durable():
    try:
        r = subprocess.run(["git", "remote"], cwd=FACTORY, capture_output=True,
                           text=True, timeout=30)
    except Exception as exc:
        raise Unmeasurable(f"could not read git remotes: {exc}")
    remotes = [x for x in r.stdout.split() if x]
    src = "git remote"
    if remotes:
        return _pass(f"pushed to {', '.join(remotes)}", [], src)
    return _fail("local git only — no remote",
                 ["one rm -rf from gone"], src)



def g_work_is_attributable():
    """Can a run be tied back to the ticket it was doing?

    This started life in the artifact's "needs a person" list, on the assumption
    that only Paul knew. He did not need to: the orchestrator names each run's
    worktree pipe_<TICKET>_<runid>. A question filed as unanswerable that a probe
    can settle is the same defect as a gate that cannot refuse.
    """
    import re as _re
    d = CONNECTORS / ".sessions"
    runs = _audits()
    if not d.is_dir():
        raise Unmeasurable(f"no .sessions directory at {d} — cannot attribute runs")
    sess = {}
    for name in os.listdir(d):
        m = _re.match(r"pipe_([A-Za-z][A-Za-z0-9-]*-[A-Za-z0-9]+)_([0-9a-f]+)$", name)
        if m:
            sess[m.group(2)] = m.group(1)
    mapped = {r["id"][5:]: sess.get(r["id"][5:]) for r in runs}
    hit = {k: v for k, v in mapped.items() if v}
    real = {k: v for k, v in hit.items() if _re.fullmatch(r"[A-Z]{2,}-\d+", v)}
    src = ".sessions/pipe_<TICKET>_<runid>"
    ev = [f"{len(hit)} of {len(runs)} runs carry a ticket key in their worktree name",
          "tickets: " + ", ".join(sorted(set(real.values())))]
    placeholder = sorted({v for v in hit.values() if v not in real.values()})
    if placeholder:
        ev.append("not real Jira keys: " + ", ".join(placeholder))
    unmapped = sorted(k for k, v in mapped.items() if not v)
    if unmapped:
        ev.append("unattributable: " + ", ".join(unmapped))
    if len(hit) == len(runs) and not placeholder:
        return _pass("every run names its ticket", ev, src)
    return _fail(f"{len(runs) - len(real)} runs cannot be tied to a Jira ticket", ev, src)


#: Fewest pipelines `truthful` must actually compare before a green means anything. Not tuned —
#: chosen as "more than the one it was silently passing on". Raise it when the population grows;
#: the number matters far less than the fact that zero-or-one can no longer read as agreement.
_TRUTHFUL_FLOOR = 3


def g_status_matches_reality():
    """Does a pipeline's recorded status agree with its own event log?

    Same shape as the completed-over-failures gate, one level up: there the run
    lied about its stages, here the record lies about the run.
    """
    f = CONNECTORS / "orchestrator" / "data" / "pipelines.json"
    if not f.is_file():
        raise Unmeasurable(f"no pipelines.json at {f}")
    try:
        listed = json.load(open(f, encoding="utf-8")).get("pipelines", [])
    except Exception as exc:
        raise Unmeasurable(f"pipelines.json will not parse: {exc}")
    if not listed:
        raise Unmeasurable("pipelines.json records no pipelines — nothing to compare")
    by_id = {r["id"]: r for r in _audits()}
    TERMINAL = {"pipeline_completed", "stage_failed", "stage_skipped"}
    drift = []
    for pl in listed:
        run = by_id.get(pl.get("id"))
        if not run or not run["events"]:
            continue
        last = run["events"][-1]
        claimed = (pl.get("status") or "").lower()
        if claimed in ("running", "created") and last.get("event_type") in TERMINAL:
            drift.append((pl["id"], claimed, last.get("event_type"),
                          last.get("stage_name")))
    src = "orchestrator/data/pipelines.json vs audits"
    # How many pipelines this gate was ACTUALLY able to compare. Everything above `continue`s past
    # a pipeline with no event log, so `listed` is the population offered and this is the
    # population measured. They are not the same number and the gate used to report only the first.
    compared = [pl for pl in listed
                if by_id.get(pl.get("id")) and by_id[pl["id"]]["events"]]
    ev = [f"{len(listed)} pipelines listed, {len(by_id)} with an event log, "
          f"{len(compared)} actually compared",
          f"{len(by_id) - len(compared)} event log(s) never examined — this gate iterates "
          f"pipelines.json, not the audits, so a run with a log but no entry is invisible to it"]
    for pid, claimed, ev_type, stage in drift:
        ev.append(f"{pid} recorded '{claimed}' but its log ends {ev_type} at {stage}")
    if drift:
        return _fail(f"{len(drift)} pipeline(s) claim a state their log contradicts",
                     ev, src)
    # ⭐ comparable != 0 BEFORE looking at the score. On 2026-08-23 this gate reported
    # "recorded status agrees with the event log" having compared exactly ONE pipeline, while 13
    # event logs went unexamined — and `from-history`, the FAIL it declares a dependency on, was
    # simultaneously naming three runs "recorded succeeded over 115, 21 and 15 failures". Those
    # are precisely the records this gate exists to catch, and they sat in the 13.
    #
    # A run where nothing could be compared has no recorded disagreements and therefore scores
    # perfect. That is the false-certification shape the parity gate already closed structurally
    # in the connector pipeline; the lesson was learned there and not carried here.
    if len(compared) < _TRUTHFUL_FLOOR:
        raise Unmeasurable(
            f"only {len(compared)} pipeline(s) could be compared (floor is {_TRUTHFUL_FLOOR}) — "
            f"a green over a population this small is not evidence that records agree with their "
            f"logs, it is evidence that almost nothing was looked at. Widen the population to the "
            f"{len(by_id)} runs that HAVE logs before this can pass.")
    return _pass(f"recorded status agrees with the event log, over {len(compared)} compared",
                 ev, src)


# --------------------------------------------------------------------------- build-order gates
# One gate per prerequisite in docs/research/SYNTHESIS.md section 5. Four research passes agreed
# these must be true BEFORE any configuration search, because an optimiser scoring an unbounded,
# unreapable, unattributable loop learns the control plane's mistakes rather than correctness.


def _src(rel: str) -> str:
    f = CONNECTORS / rel
    if not f.is_file():
        raise Unmeasurable(f"no {rel} at {CONNECTORS} — cannot inspect the control plane")
    return f.read_text(encoding="utf-8", errors="replace")


def _grep(rel: str, pattern: str):
    """(line_number, text) for each match. Reading source is the only instrument available
    without credentials; a gate that needs a live system says UNMEASURABLE instead."""
    out = []
    for i, line in enumerate(_src(rel).splitlines(), 1):
        if re.search(pattern, line):
            out.append((i, line.strip()))
    return out


def g_attempt_cap_on_the_live_path():
    """Is the retry cap enforced on the path that actually restarts stages?

    ⭐ **Driven, not grepped.** This probe used to search `pipelines.py` for a regex spanning
    3,000 characters from `def restart_from_stage` to any of four ceiling-ish tokens. A comment
    mentioning `max_attempts` satisfied it, and the lane being graded writes the comments. Now it
    calls `check_attempt_cap` and watches what happens.

    **Both directions are required.** A cap that refuses a stage on its first attempt is as broken
    as one that never refuses, and only one of those two failures looks like a failure. So the
    control must refuse over the cap AND allow under it; either half alone is not the control.
    """
    src = f"{CONNECTORS}/orchestrator/pipelines.py :: check_attempt_cap (driven)"
    mod = _engine()
    cap = getattr(mod, "MAX_ATTEMPTS_PER_STAGE", None)
    fn = getattr(mod, "check_attempt_cap", None)
    if fn is None or cap is None:
        return _fail("no attempt cap on the dispatch path",
                     ["the engine exposes no check_attempt_cap/MAX_ATTEMPTS_PER_STAGE",
                      "1,004 restart_from_stage events recorded; worst 352 in one run"], src)

    over = _stage(_attempts=int(cap) + 1)
    under = _stage(_attempts=0)
    refused_over, why = _refused(fn, _pipeline(stages=[over]), over, "restart_from_stage")
    refused_under, _ = _refused(fn, _pipeline(stages=[under]), under, "restart_from_stage")

    ev = [f"cap declared: MAX_ATTEMPTS_PER_STAGE = {cap}",
          f"driven at {cap + 1} attempts -> {'REFUSED' if refused_over else 'ALLOWED'}",
          f"driven at 0 attempts -> {'REFUSED' if refused_under else 'ALLOWED'}",
          "1,004 restart_from_stage events recorded historically; worst 352 in one run"]
    if refused_over:
        ev.append(f"refusal said: {why}")
    if refused_over and not refused_under:
        return _pass("the restarting path is capped, and the cap was watched refusing", ev, src)
    if refused_under:
        return _fail("the cap refuses work that is under the limit", ev, src)
    return _fail("a cap exists on a path that did not run", ev, src)


def g_spend_ceiling_survives_restart():
    """Is accrued spend compared to a budget BEFORE a stage is dispatched?

    Driven like its four neighbours, and the answer today is that there is nothing to drive:
    measured 2026-08-30 against `lane/control-plane` — the branch that carries the cap, the
    dispatch ceiling and the reaper — the only budget symbol in the engine is
    `TERMINATION_BUDGET_SEC`, which is a **time** budget for the reap sweep. No spend control
    exists on any branch.

    ⛔ **Two things must be built, in this order, and building only the second is worse than
    building neither.** The gate's long-standing evidence line names the precondition: *cost is
    recorded only on `stage_completed`*. A ceiling reading that figure is blind to every failed
    attempt — and failures are what a runaway loop is made of. Compare accrued-cost-so-far to a
    budget on top of failure-blind accounting and the board goes green over a ceiling that
    cannot hold, which is the single worst outcome available here.

      1. record cost on **every** terminal stage event, not only on success
      2. compare the accrued figure to `budget_usd` before dispatch, and refuse through
         `_refuse` so the refusal is auditable like the other three controls

    F77 is the other half: RUN-01 as written is two tickets in two repositories, and only the
    `prefect-connectors` half can move this gate.
    """
    src = f"{CONNECTORS}/orchestrator/pipelines.py :: (no spend control to drive)"
    mod = _engine()
    ceiling_fn = next((getattr(mod, n) for n in
                       ("check_spend_ceiling", "check_budget", "check_cost_ceiling")
                       if callable(getattr(mod, n, None))), None)
    budget_syms = sorted(n for n in dir(mod)
                         if ("BUDGET" in n or "COST" in n or "SPEND" in n) and n.isupper())
    ev = [f"budget-ish constants on the engine: {budget_syms or 'none'}",
          "TERMINATION_BUDGET_SEC is a TIME budget for the reap sweep, not a spend ceiling"
          if "TERMINATION_BUDGET_SEC" in budget_syms else "",
          "budget_usd is declared per stage and nothing compares accrued spend to it "
          "before dispatch",
          "cost is recorded only on stage_completed, so the accrued figure a ceiling would "
          "read is itself blind to every failure — fix the accounting before the ceiling"]
    ev = [e for e in ev if e]
    if ceiling_fn is None:
        return _fail("no spend ceiling enforced before dispatch", ev, src)

    over = _stage(cost_usd=10_000.0, budget_usd=1.0)
    refused, why = _refused(ceiling_fn, _pipeline(stages=[over]), over, "dispatch")
    under = _stage(cost_usd=0.0, budget_usd=1_000.0)
    refused_under, _ = _refused(ceiling_fn, _pipeline(stages=[under]), under, "dispatch")
    ev += [f"driven at $10,000 against a $1 budget -> {'REFUSED' if refused else 'ALLOWED'}",
           f"driven at $0 against a $1,000 budget -> "
           f"{'REFUSED' if refused_under else 'ALLOWED'}"]
    if refused:
        ev.append(f"refusal said: {why}")
    if refused and not refused_under:
        return _pass("spend is checked before dispatch, and the ceiling was watched refusing",
                     ev, src)
    return _fail("no spend ceiling enforced before dispatch", ev, src)


def g_concurrency_is_reserved_outside_the_agent():
    """Is concurrent STAGE dispatch bounded — the level at which ten containers took a quota?

    ⛔ **This probe reported a false FAIL for eight days because of one letter's case.** It ran
    `re.search(r"max_parallel", _src("orchestrator/pipelines.py"))` — case-sensitively — while the
    code spells the constant `MAX_PARALLEL_STAGE_DISPATCH`. It therefore announced *"nothing
    bounds concurrent STAGE dispatch"* about a module containing a dispatch ceiling, a
    `_DISPATCH_LOCK`, and a `dispatch_ceiling` refusal event. **A zero from an instrument nobody
    proved could see is not a measurement** — the identical defect review finding D-2 recorded,
    where a document was reported missing over a case-sensitive grep. F81.

    Now driven: fill the ceiling and confirm no slots remain, then empty it and confirm they do.
    """
    src = f"{CONNECTORS}/orchestrator/pipelines.py :: dispatched_slots_in_use (driven)"
    mod = _engine()
    ceiling = getattr(mod, "MAX_PARALLEL_STAGE_DISPATCH", None)
    in_use = getattr(mod, "dispatched_slots_in_use", None)
    if ceiling is None or in_use is None:
        return _fail("concurrency is bounded per wave, not per stage dispatch",
                     ["the engine exposes no stage-level dispatch ceiling",
                      "wave_scheduler bounds how many PIPELINES start together, which is not "
                      "the level at which ten containers took the region quota"], src)

    saved = dict(getattr(mod, "_pipelines", {}))
    try:
        mod._pipelines.clear()
        empty = in_use()
        stages = [_stage(f"s{i}", status="dispatched") for i in range(int(ceiling) + 2)]
        mod._pipelines["readiness-probe"] = _pipeline("readiness-probe", stages)
        full = in_use()
        # A manual gate must NOT consume a slot: two paused runs would otherwise starve
        # everything else, which is a ceiling causing the outage it was added to prevent.
        mod._pipelines.clear()
        gate = _stage("await-human", status="dispatched", type="gate", gate_type="manual")
        mod._pipelines["readiness-probe"] = _pipeline("readiness-probe", [gate])
        manual = in_use()
    finally:
        mod._pipelines.clear()
        mod._pipelines.update(saved)

    ev = [f"ceiling declared: MAX_PARALLEL_STAGE_DISPATCH = {ceiling}",
          f"with no dispatched stages, slots in use = {empty}",
          f"with {int(ceiling) + 2} dispatched stages, slots in use = {full} "
          f"(free = {int(ceiling) - full})",
          f"a dispatched MANUAL gate counts as {manual} slot(s) — a human being asked a "
          f"question must not hold the scarce resource"]
    if empty == 0 and full > ceiling and manual == 0:
        return _pass("stage dispatch is bounded, and the ceiling was driven past its limit",
                     ev, src)
    return _fail("concurrency is bounded per wave, not per stage dispatch", ev, src)


def g_orphans_are_reaped():
    """Is dispatched work either finished or killed — or can it sit at `stage_started` forever?

    ⭐ **Like `bounded`, this probe had one return path and it was `_fail`.** It counted heartbeat
    mentions in `work_guard.py`, appended three canned lines, and returned "no lease, timeout or
    reaper for dispatched work" unconditionally. No input could satisfy it. Meanwhile
    `orchestrator/engine/cloud_reaper.py` and `reap_expired_leases` exist, with 965 lines of tests
    behind them, and the gate reported their absence with confidence. F81.

    ⚠ **The reaper's own third verdict is the thing to preserve.** A dispatched stage with neither
    a lease nor a `started_at` is NOT-MEASURABLE, not expired — the reaper says so itself and
    collects those separately rather than killing them. A probe that treated "not reaped" as "not
    working" would be pressuring the engine to kill work it cannot measure, which is worse than
    the orphan.
    """
    src = f"{CONNECTORS}/orchestrator/pipelines.py :: reap_expired_leases (driven)"
    mod = _engine()
    reap = getattr(mod, "reap_expired_leases", None)
    if reap is None:
        return _fail("no lease, timeout or reaper for dispatched work",
                     ["the engine exposes no reap_expired_leases",
                      "work_guard's lease covers REPO LOCKS between agents, not dispatched "
                      "cloud work",
                      "4 of 14 runs sit at stage_started with no terminal event"], src)

    import datetime as _dt
    now = _dt.datetime.now(_dt.timezone.utc)
    expired = (now - _dt.timedelta(hours=6)).isoformat()
    future = (now + _dt.timedelta(hours=6)).isoformat()

    saved = dict(getattr(mod, "_pipelines", {}))
    try:
        mod._pipelines.clear()
        dead = _stage("orphan", status="dispatched", lease_expires_at=expired)
        alive = _stage("healthy", status="dispatched", lease_expires_at=future)
        mod._pipelines["readiness-probe"] = _pipeline("readiness-probe", [dead, alive])
        reaped = reap()
        names = {r.get("stage") or r.get("stage_name") for r in (reaped or [])
                 if isinstance(r, dict)}
        dead_status, alive_status = dead.get("status"), alive.get("status")
    except Exception as exc:                                       # noqa: BLE001
        raise Unmeasurable(f"driving reap_expired_leases raised {type(exc).__name__}: {exc}")
    finally:
        mod._pipelines.clear()
        mod._pipelines.update(saved)

    ev = [f"drove the reaper over one stage with a 6h-EXPIRED lease and one with a live lease",
          f"reaped: {sorted(n for n in names if n) or 'nothing'}",
          f"expired stage ended as '{dead_status}'; live stage ended as '{alive_status}'",
          "the reaper never re-dispatches — it closes the stage so the run can reach a "
          "terminal state and stop holding a slot"]
    took_the_dead = "orphan" in names or dead_status not in (None, "dispatched")
    spared_the_live = "healthy" not in names and alive_status == "dispatched"
    if took_the_dead and spared_the_live:
        return _pass("dispatched work is reaped when its lease expires, and only then", ev, src)
    if not took_the_dead:
        return _fail("no lease, timeout or reaper for dispatched work", ev, src)
    return _fail("the reaper killed a stage whose lease had not expired", ev, src)


def g_verdict_is_computed_from_history():
    """Does the terminal verdict read the append-only log, or a last-write-wins field?

    ⭐ **The drive is a discriminating test, and the two candidate implementations disagree.**
    Hand `terminal_verdict` a pipeline whose every stage reads `completed` — current state says
    unambiguously *succeeded* — but whose history cannot be read. A verdict computed from
    `pipeline["stages"]` returns **succeeded**. A verdict computed from the log cannot read the
    log, so it must decline: `failed`, `basis=UNMEASURABLE`, failing closed. The answer separates
    the two mechanisms; no regex over the source can.

    That failure mode is not hypothetical — `docs/evidence/false-succeeded-mechanism.md` records
    three runs marked succeeded over 115, 21 and 15 failures, because a stage that failed 100
    times and succeeded on the 101st reads `completed`.
    """
    src = f"{CONNECTORS}/orchestrator/pipelines.py :: terminal_verdict (driven)"
    mod = _engine()
    fn = getattr(mod, "terminal_verdict", None)
    if fn is None:
        raise Unmeasurable("the engine exposes no terminal_verdict to drive")

    pl = _pipeline("readiness-probe-no-such-history",
                   [_stage("a", status="completed"), _stage("b", status="completed")])
    try:
        out = fn(pl)
    except Exception as exc:                                       # noqa: BLE001
        raise Unmeasurable(f"driving terminal_verdict raised {type(exc).__name__}: {exc}")

    if not isinstance(out, dict):
        return _fail("the verdict reads current state, not history",
                     [f"terminal_verdict returned {out!r}, which carries no basis field",
                      "a verdict with no basis cannot say whether the log was read"], src)

    status, basis = out.get("status"), out.get("basis")
    ev = [f"drove terminal_verdict on a pipeline whose stages all read 'completed' and whose "
          f"history is absent",
          f"returned status={status!r} basis={basis!r}",
          "a state-derived verdict returns 'succeeded' here; a history-derived one cannot read "
          "the log and must fail closed",
          "3 runs were recorded succeeded over 115, 21 and 15 failures — "
          "docs/evidence/false-succeeded-mechanism.md"]
    if status == "failed" and basis == "UNMEASURABLE":
        return _pass("the verdict is derived from the event log, and fails closed when the log "
                     "cannot be read", ev, src)
    if status == "succeeded":
        return _fail("the verdict reads current state, not history", ev, src)
    return _fail("the verdict did not fail closed on an unreadable log", ev, src)


def g_corpus_has_breadth():
    """One real success is a fixture, not a calibration."""
    from . import corpus as _c
    src = "evals/corpus/"
    try:
        pinned = _c.available()
    except _c.CorpusError as exc:
        return _fail("the corpus does not verify", [str(exc)[:160]], src)
    strata = set()
    for cid in pinned:
        doc = _c.load(cid)
        strata.update(doc.get("strata") or [])
    ev = [f"{len(pinned)} corpus case(s), {len(strata)} declared stratum/strata",
          "R1 graded one-run calibration FOLKLORE: a blind spot affecting 10% of a stratum "
          "needs 29 cases for a 95% chance of being seen once",
          "target is two distributions — a regression corpus of every distinct historical "
          "failure, and a challenge corpus across 15 mechanisms — neither prevalence-weighted"]
    if len(pinned) >= 29 and len(strata) >= 15:
        return _pass(f"{len(pinned)} cases across {len(strata)} strata", ev, src)
    return _fail(f"{len(pinned)} case(s), {len(strata)} strata — below any calibration threshold",
                 ev, src)


# The dimensions R2 named as missing from a config hash. An agent is not a name; it is everything
# here, and anything absent is something a certification silently transfers across.
VERSION_DIMENSIONS = [
    "prompt", "model", "effort", "tools", "max_turns", "budget_usd",          # we have these
    "tool_implementation", "sandbox_image", "model_routing", "context_policy",
    "external_knowledge", "permissions", "contract_version", "harness_version",
    "side_effect_replay",
]


def g_version_hash_is_complete():
    src = "factory/blueprint.py"
    body = (FACTORY / "blueprint.py").read_text(encoding="utf-8")         if (FACTORY / "blueprint.py").is_file() else         (FACTORY / "factory" / "blueprint.py").read_text(encoding="utf-8")
    have = [d for d in VERSION_DIMENSIONS if re.search(rf"\b{d}\b", body)]
    missing = [d for d in VERSION_DIMENSIONS if d not in have]
    ev = [f"{len(have)} of {len(VERSION_DIMENSIONS)} dimensions in the hashed config",
          "missing: " + ", ".join(missing)]
    if "contract_version" in missing:
        ev.append("contract_version is the one that bites now — a certification granted under "
                  "contract V4 silently transfers to V5")
    if not missing:
        return _pass("the hash covers every declared dimension", ev, src)
    return _fail(f"{len(missing)} dimensions absent from the version", ev, src)


def g_evaluator_is_a_service():
    """R3 ranked the isolation options; a separate local process is 'mostly theatre'.

    ⚠ The first version of this probe grepped factory/*.py for EVALUATOR_URL and friends — and
    MATCHED ITS OWN SOURCE, because those strings appear in the very regex doing the searching.
    It returned PASS: "an evaluator service is configured", when none exists. A self-matching
    probe producing a false green is the failure this project exists to stop, reproduced inside
    the instrument. It now asks a question source text cannot answer by accident: is an endpoint
    actually configured, and is there a module that is not this one implementing it.
    """
    src = "$AGENT_FACTORY_EVALUATOR + factory/"
    endpoint = os.environ.get("AGENT_FACTORY_EVALUATOR", "").strip()
    impl = [f.name for f in (FACTORY / "factory").glob("*.py")
            if f.name not in ("readiness.py", "__init__.py")
            and "class EvaluatorClient" in f.read_text(encoding="utf-8", errors="replace")]
    ev = [f"$AGENT_FACTORY_EVALUATOR: {endpoint or '(unset)'}",
          f"client implementation: {', '.join(impl) or 'none'}"]

    # The old PASS text read "configured and reachable" while measuring neither reachability nor
    # who answered. A gate that asserts a word it never tested is the same species of defect as a
    # probe matching its own source, so both words are now measured — and reported as evidence
    # rather than folded into the pass condition, because this gate asks whether the evaluator IS
    # a separate principal, not whether it happens to be up this second.
    live, mode = None, "unconfigured"
    if endpoint:
        from .evaluator import EvaluatorClient, endpoint_mode
        mode = endpoint_mode(endpoint)
        try:
            live = EvaluatorClient(endpoint, timeout=1.5).health()
        except Exception as exc:                                   # noqa: BLE001
            ev.append(f"health check: NO ANSWER ({type(exc).__name__}) — configured is not running")
    if live:
        ev.append(f"health check: answered as {live.get('identity', 'unidentified')}, "
                  f"bundle {str(live.get('bundle_sha256', ''))[:12]}, "
                  f"corpus {live.get('corpus_id', '?')}, "
                  f"{live.get('verdicts_recorded', 0)} verdict(s) recorded")
        ev.append(f"the submission vocabulary it accepts: {live.get('submission_fields')} "
                  "— no corpus, no manifest, no evaluator")

    # ⚠ Deployment rank is not design rank, and this gate must not let the two be confused. Same
    # code on loopback and in a container with a managed identity gives very different protection.
    if mode == "loopback":
        ev.append("deployment: LOOPBACK — R3 rank 5, 'mostly theatre'. Same uid can write the "
                  "verdict store and restart the evaluator; the design is rank 1 and the "
                  "remaining gap is a managed identity the agent sandbox does not hold, which is "
                  "a deployment change, not a code change")
    elif mode == "remote":
        ev.append("deployment: REMOTE — rank 1 shape. Confirm the agent sandbox cannot obtain "
                  "the evaluator's identity before treating this as isolation")

    ev += ["the agent supplies {artifact_uri, artifact_sha256, run_id} and nothing else; the "
           "corpus, the manifest and the assertion set are resolved by the service",
           "known hole: the contract is parameterised by a blueprint the graded party writes. "
           "A target floor and the artefact hash narrow it; a pinned per-connector target closes "
           "it, and nobody has written one",
           "R3's ranking: external evaluator service with its own identity is rank 1; a separate "
           "local process is rank 5 and 'mostly theatre'",
           "'Moving only the files to another directory changes nothing; moving "
           "ownership/credentials out of the agent's capability set does'"]
    if endpoint and impl:
        return _pass(f"the evaluator is a separate principal ({mode} deployment)", ev, src)
    return _notrun("the evaluator is not yet a separate principal", ev, src)




# --------------------------------------------------------------------------- handover gates
# Things I first filed as "no probe can settle this". Most of that was a failure of imagination:
# an unasked question is measurable by whether its answer exists, and a decision is measurable by
# whether it was written down. A gate that says "ask a human" is a gate that stopped looking.


def _research_answer(pattern: str):
    d = FACTORY / "docs" / "research" / "answers"
    if not d.is_dir():
        raise Unmeasurable(f"no answers directory at {d}")
    return sorted(f.name for f in d.glob(pattern))


def _followup_gate(n: int, subject: str):
    def probe():
        src = "docs/research/answers/"
        hits = _research_answer(f"R{n}-followup*.md")
        ev = [f"looking for docs/research/answers/R{n}-followup*.md",
              f"subject: {subject}"]
        if hits:
            # "dispatched", not "answered": these files hold the QUESTION, and the gate's
            # own NOTRUN text is "not asked yet". A gate that tracks asking must not read
            # as though it tracked answering.
            return _pass(f"dispatched: {hits[0]}", ev, src)
        return _notrun("not asked yet", ev, src)
    return probe


g_r1_followup = _followup_gate(1, "does anything else depend on the Prefect misattribution?")
g_r2_followup = _followup_gate(2, "our build plane is not Prefect — move onto it, or reimplement?")
g_r3_followup = _followup_gate(3, "terminal verdict from append-only history, and its negative control")


def g_render_pass_recorded():
    """Has anyone actually looked at the published surface and written down what they saw?

    Not "can Claude reach a browser" — that is a capability, not a state. The state that matters
    is whether a render pass HAPPENED and left evidence, by whoever ran it.
    """
    d = FACTORY / "docs" / "evidence"
    src = "docs/evidence/render-pass-*.md"
    hits = sorted(f.name for f in d.glob("render-pass-*.md")) if d.is_dir() else []
    ev = ["a static check proves the file parses, not that a visual painted",
          "five defects shipped into the published figure and a human found every one"]
    if hits:
        return _pass(f"recorded: {hits[-1]}", ev, src)
    return _fail("no render pass has been recorded", ev, src)


def g_impeccable_precedence_settled():
    """A fifth design authority with a broad trigger needs its place stated, once, in writing."""
    chain = pathlib.Path.home() / ".claude" / "skills" / "living-systems-ui" / "SKILL.md"
    src = "~/.claude/skills/living-systems-ui/SKILL.md"
    if not chain.is_file():
        raise Unmeasurable(f"no skill chain document at {src}")
    txt = chain.read_text(encoding="utf-8", errors="replace")
    ev = ["impeccable installed 2026-08-21 — 1 skill, 23 commands, 59 deterministic detector rules",
          "its trigger overlaps artifact-design, artifact-motion and living-systems-ui"]
    if "impeccable" in txt.lower():
        return _pass("the chain names impeccable", ev, src)
    return _fail("impeccable's place in the skill chain is unstated", ev, src)


def g_grain_declared():
    """Is the landing-table grain settled, or still an open question in a comment?"""
    bp = _blueprint()
    src = "blueprints/windsorai_client_a.yaml"
    val = str(bp.get("grain_confirmed") or "").strip()
    ev = ["20 rows across 18 campaigns on one date cannot be unique on "
          "(account_id, campaign_id, date) under a single account",
          "if the real table holds one account the declared primary key is wrong, and the "
          "calibration world is built on a mistake",
          "set grain_confirmed in the blueprint once someone has queried the table"]
    if val:
        return _pass(f"grain declared: {val}", ev, src)
    return _fail("the landing-table grain is still an open question", ev, src)


def g_work_has_a_ticket():
    """Either a ticket key exists, or a decision that none is needed was written down.

    Both are acceptable outcomes. What is not acceptable is neither — an open question quietly
    aging in a drafts folder.
    """
    import re as _re
    d = FACTORY.parent / "aldc-launchpad" / "boot-prompts" / "drafts"
    src = "aldc-launchpad/boot-prompts/drafts/"
    if not d.is_dir():
        raise Unmeasurable(f"no drafts directory at {d}")
    for f in d.glob("*jira*.md"):
        txt = f.read_text(encoding="utf-8", errors="replace")
        m = _re.search(r"^TICKET:\s*([A-Z]{2,}-\d+|NONE-BY-DECISION)\s*$", txt, _re.M)
        if m:
            return _pass(f"{m.group(1)}", [f"declared in {f.name}"], src)
    return _fail("no ticket, and no recorded decision that none is needed",
                 ["a draft comment is ready but has no key",
                  "resolve by putting a line `TICKET: ALDC-123` or `TICKET: NONE-BY-DECISION` "
                  "at the top of the draft"], src)

GATES: List[Gate] = [
    Gate("r1-followup", "Has R1 been asked what else depended on the misattribution?",
         "A correction that never reaches the source leaves the rest of that answer unaudited.",
         g_r1_followup, "handover"),
    Gate("r2-followup", "Has R2 been asked whether to move the build plane onto Prefect?",
         "Its prescription assumed Prefect primitives we do not have. The highest-value "
         "unasked question.",
         g_r2_followup, "handover"),
    Gate("r3-followup", "Has R3 been asked the false-succeeded correction?",
         "Its Q4 was aimed at the wrong plane.",
         g_r3_followup, "handover"),
    Gate("rendered", "Has anyone looked at the published surface and recorded it?",
         "A static check proves the file parses, not that a visual painted.",
         g_render_pass_recorded, "handover"),
    Gate("chain", "Is impeccable's place in the skill chain stated?",
         "Five design authorities with overlapping triggers, and precedence decided mid-build "
         "is precedence decided by accident.",
         g_impeccable_precedence_settled, "handover"),
    Gate("grain", "Is the landing-table grain settled?",
         "The calibration world assumes an arrangement nobody has confirmed.",
         g_grain_declared, "handover"),
    Gate("ticket", "Does this work have a ticket, or a decision that it needs none?",
         "Either is fine. Neither is an open question quietly aging in a drafts folder.",
         g_work_has_a_ticket, "handover"),
    Gate("cap", "Is the retry cap enforced on the path that restarts?",
         "A cap on a path nothing uses is not a cap.",
         g_attempt_cap_on_the_live_path, "bounded"),
    Gate("ceiling", "Is spend checked before dispatch?",
         "A ceiling read from a figure blind to failures is not a ceiling.",
         g_spend_ceiling_survives_restart, "bounded"),
    Gate("concurrency", "Is concurrent dispatch bounded outside the agent?",
         "Ten containers took a region quota; waves bound pipelines, not stages.",
         g_concurrency_is_reserved_outside_the_agent, "bounded"),
    Gate("reaper", "Is dispatched work either finished or killed?",
         "Four runs sit at stage_started forever; containers outlive their stage.",
         g_orphans_are_reaped, "bounded"),
    Gate("from-history", "Is the terminal verdict computed from history?",
         "Current state cannot answer a question about what it cost to get there.",
         g_verdict_is_computed_from_history, "judgement"),
    Gate("breadth", "Does the eval corpus have enough breadth to calibrate?",
         "One real success is a fixture. Calibration needs strata and counts.",
         g_corpus_has_breadth, "certification"),
    Gate("version", "Does the version hash cover what makes an agent an agent?",
         "Anything unhashed is something a certification silently transfers across.",
         g_version_hash_is_complete, "certification"),
    Gate("isolated", "Is the evaluator a principal the agent cannot impersonate?",
         "Tamper-evidence is not a trust boundary; a separate directory is not either.",
         g_evaluator_is_a_service, "certification"),
    Gate("finishes", "Does a run finish without a human?",
         "Unattended means the pipeline reaches its terminal stage on its own.",
         g_finishes, "loop"),
    Gate("succeeds", "Do stages succeed more often than they fail?",
         "A loop that mostly fails cannot be left alone, however good its gates.",
         g_succeeds_more_than_fails, "loop"),
    Gate("bounded", "Is failure bounded?",
         "Without an attempt cap one stuck stage consumes the whole quota.",
         g_failure_is_bounded, "loop"),
    Gate("refuses", "Has any gate ever refused a run?",
         "A gate never observed refusing is decoration. Same rule as an eval.",
         g_gates_can_refuse, "judgement"),
    Gate("checks", "Do the gates have programmatic checks?",
         "A manual gate with check=None is a human clicking approve, not a control.",
         g_gates_have_checks, "judgement"),
    Gate("attributable", "Can a run be tied to the ticket it was doing?",
         "Unattributable work cannot be reported on, priced, or handed back.",
         g_work_is_attributable, "judgement"),
    Gate("truthful", "Does a recorded status match its own event log?",
         "A record that contradicts its log is the success-over-failures defect "
         "one level up.",
         g_status_matches_reality, "judgement"),
    Gate("honest", "Does a completed run mean the work was correct?",
         "This is the estate's signature failure: success reported over an unseen "
         "population.",
         g_success_means_correct, "judgement"),
    Gate("cost", "Is cost observable when things fail?",
         "An optimiser cannot price a path whose failures are free.",
         g_cost_survives_failure, "judgement"),
    Gate("general", "Can QA validate any connector, not one?",
         "A gate that can only pass for a twin cannot certify a fleet.",
         g_qa_gate_is_general, "judgement"),
    Gate("suite", "Is the certification suite green and honest?",
         "Green is worthless unless every assertion has been shown able to fail.",
         g_contract_suite_green, "certification"),
    Gate("certified", "Is the output actually certified?",
         "The contract must measure a live run, not a replayed one.",
         g_output_is_certified, "certification"),
    # Retitled 2026-08-23. It read "Is blast radius certifiable?" and passed on a non-empty
    # `allowed_tenants` list — so a PASS announced that blast radius was certifiable while meaning
    # "somebody wrote six account ids down". The blueprint says those were verified 2026-05-29,
    # ~12 weeks before it was written, and carries "Confirm against a live pull before activation".
    # Declared and verified are different claims and only one of them is measured here.
    Gate("tenancy", "Is a tenant scope DECLARED? (declared, not verified)",
         "Certifying a pull whose scope is unknown certifies nothing — but a declared list is "
         "not a confirmed one, and this gate cannot tell you the ids are still right.",
         g_tenancy_declared, "certification"),
    Gate("corpus", "Is the grader tamper-evident and separable?",
         "An agent that can edit its own grader is not graded — and a silent edit is "
         "worse than a loud one.",
         g_corpus_is_tamper_evident, "certification"),
    Gate("durable", "Does the factory survive this machine?",
         "Unpushed work is one accident from gone.",
         g_repo_is_durable, "certification"),
]

PHASES = {
    "loop": "Can the loop run?",
    "bounded": "Is it bounded? (build order 1-2)",
    "judgement": "Can it tell success from failure?",
    "certification": "Can its output be certified?",
    "handover": "Is it handed over honestly?",
}


def measure() -> List[tuple]:
    out = []
    for g in GATES:
        try:
            r = g.probe()
        except Unmeasurable as exc:
            r = Result(UNMEASURABLE, str(exc).split(" — ")[0][:80], [str(exc)], "")
        except Exception as exc:  # an instrument that broke is not a failing gate
            r = Result(UNMEASURABLE, f"probe raised {type(exc).__name__}",
                       [str(exc)[:300]], "")
        out.append((g, r))
    return out


def main() -> int:
    results = measure()
    n_pass = sum(1 for _, r in results if r.ok)
    glyph = {PASS: "PASS", FAIL: "FAIL", UNMEASURABLE: "UNMEAS", NOT_RUN: "NOTRUN"}
    # F72: this board reads 9 or 10 at the SAME COMMIT depending only on the cwd it ran from,
    # because CONNECTORS resolves relative to FACTORY. A headline quoted without its basis is
    # not a measurement, so the basis travels WITH the number, not two lines below it where a
    # copy-paste loses it.
    print(f"\nUnattended-migration readiness: {n_pass} of {len(results)} gates pass"
          f"  [connectors: {CONNECTORS.name} · loop measured since {MEASURED_SINCE}]")
    print(f"factory      {FACTORY}")
    print(f"connectors   {CONNECTORS}\n")
    for phase, title in PHASES.items():
        rows = [(g, r) for g, r in results if g.phase == phase]
        ok = sum(1 for _, r in rows if r.ok)
        print(f"  {title}  [{ok}/{len(rows)}]")
        for g, r in rows:
            print(f"    {glyph[r.verdict]:7} {g.question:52} {r.headline}")
            for e in r.evidence:
                print(f"            . {e}")
        print()
    print("UNMEASURABLE is not a pass.")
    return 0 if n_pass == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
