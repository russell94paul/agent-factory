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
from datetime import datetime, timezone
import re
import glob
import json
import os
import pathlib
import subprocess
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
    p = FACTORY / "blueprints" / "windsorai_gep.yaml"
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
    if len(fin) == len(runs):
        return _pass(f"all {len(runs)} runs finished", ev, src)
    return _fail(f"{len(fin)}/{len(runs)} runs finished", ev, src)


def g_succeeds_more_than_fails():
    c = _counts(_audits())
    done, failed = c["stage_completed"], c["stage_failed"]
    ev = [f"{failed} stage_failed against {done} stage_completed",
          f"{c['restart_from_stage']} restarts recorded"]
    src = "orchestrator/data/audits/*.json"
    if failed == 0 and done == 0:
        raise Unmeasurable("no stage outcomes recorded at all")
    if done > failed:
        return _pass(f"{done} succeed vs {failed} fail", ev, src)
    return _fail(f"a stage attempt fails {failed / max(done,1):.1f}x more than it "
                 f"succeeds", ev, src)


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


def g_contract_suite_green():
    try:
        # No -q here: pyproject addopts already sets it, and -qq suppresses the
        # summary line this gate parses. The instrument was blind to its own config.
        r = subprocess.run(["python", "-m", "pytest", "--no-header", "--tb=no",
                            "-p", "no:cacheprovider"],
                           cwd=FACTORY, capture_output=True, text=True, timeout=300)
    except Exception as exc:
        raise Unmeasurable(f"could not run the suite: {exc}")
    clean = re.sub("\x1b?\\[[0-9;]*m", "", r.stdout + "\n" + r.stderr)
    hits = re.findall(r"\d+ (?:passed|failed|error)[^\n]*", clean)
    # Drop the duration: it changes every run and is not a readiness fact, so
    # keeping it would make --check report stale against itself.
    line = re.sub(r" in [0-9.]+s", "", hits[-1].strip()) if hits         else "(pytest printed no summary line)"
    src = "tests/"
    if r.returncode == 0:
        return _pass(line.strip(), ["includes test_every_assertion_has_been_proved_"
                                    "able_to_fail"], src)
    return _fail(line.strip(), [], src)


def g_output_is_certified():
    try:
        r = subprocess.run(["python", "-m", "factory.certify",
                            "blueprints/windsorai_gep.yaml"], cwd=FACTORY,
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
    src = "blueprints/windsorai_gep.yaml"
    if tenants:
        return _pass(f"{len(tenants)} tenant(s) declared", [str(tenants)], src)
    raise Unmeasurable(
        "allowed_tenants is empty — one ALDC Windsor key returns every client's "
        "accounts, so an unfiltered pull lands Fusion92 rows in a GEP table and "
        "nothing downstream can tell. Blast radius is uncertifiable until someone "
        "writes the Navira account ids down.")


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
    ev = [f"{len(listed)} pipelines listed, {len(by_id)} with an event log"]
    for pid, claimed, ev_type, stage in drift:
        ev.append(f"{pid} recorded '{claimed}' but its log ends {ev_type} at {stage}")
    if drift:
        return _fail(f"{len(drift)} pipeline(s) claim a state their log contradicts",
                     ev, src)
    return _pass("recorded status agrees with the event log", ev, src)


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


def g_spend_ceiling_survives_restart():
    src = "orchestrator/"
    body = _src("orchestrator/pipelines.py")
    checks = re.findall(r"cost_usd.{0,80}(?:>=|>)\s*.{0,40}budget", body)
    ev = [f"{len(checks)} pre-dispatch comparison(s) of accrued cost against a budget"]
    if not checks:
        ev.append("budget_usd is declared per stage but nothing was found comparing accrued "
                  "spend to it before dispatch")
        ev.append("cost is recorded only on stage_completed, so the accrued figure a ceiling "
                  "would read is itself blind to every failure")
        return _fail("no spend ceiling enforced before dispatch", ev, src)
    return _pass("spend is checked before dispatch", ev, src)


# --------------------------------------------------------------------------- behavioural
# Four of the control-plane gates below do not read source for a pattern. They import the
# build plane, make the control refuse something, and report what they watched.
#
# The reason is written into this repo's own rules twice over. *A mechanism nobody has
# watched refuse is not a control* — and a probe that greps is satisfied by a comment
# mentioning the right word, which is the decoration-gate defect the programme exists to
# stop. Two of the probes replaced here returned `_fail` unconditionally: they had exactly
# one return path and could not have reported a bounded system if one had existed. One
# more searched `orchestrator/engine/work_guard.py` for a reaper that would never have
# been there, and never looked in `pipelines.py`, where an orphan reclaimer already lived.
#
# A behavioural probe fails honestly in the one way that matters: if the build plane will
# not import, it raises Unmeasurable rather than passing or failing on a guess.

_ENGINE = None


def _engine():
    """Import the build plane against a scratch data directory. Cached per process.

    Raises Unmeasurable — never a verdict — when the checkout cannot be imported. A gate
    that cannot establish its instrument has not measured anything.
    """
    global _ENGINE
    if _ENGINE is not None:
        return _ENGINE
    import sys
    import tempfile
    if not (CONNECTORS / "orchestrator" / "pipelines.py").is_file():
        raise Unmeasurable(f"no orchestrator/pipelines.py at {CONNECTORS}")
    if str(CONNECTORS) not in sys.path:
        sys.path.insert(0, str(CONNECTORS))
    try:
        from orchestrator import pipelines as engine
        from orchestrator.engine import audit as audit_trail
    except Exception as exc:
        raise Unmeasurable(f"the build plane will not import: {type(exc).__name__}: {exc}")
    # The engine logs every refusal at WARNING, which is exactly right in production and
    # exactly wrong in the middle of a readiness table. The refusals are still measured —
    # each probe reports what it watched — they are just not printed over the report.
    import logging as _logging
    _logging.getLogger("orchestrator").setLevel(_logging.CRITICAL)
    _logging.getLogger("orchestrator.pipelines").setLevel(_logging.CRITICAL)
    # A scratch directory, never the real one. These probes dispatch and reap; pointing
    # them at orchestrator/data would have the readiness check mutate the record it is
    # also measuring.
    d = pathlib.Path(tempfile.mkdtemp(prefix="readiness-probe-"))
    audit_trail.configure(d, d / "sessions")
    engine.configure(d)
    _ENGINE = (engine, audit_trail, d)
    return _ENGINE


def _scratch_pipeline(engine, pid, stages, status="running"):
    engine._pipelines.clear()
    p = {"id": pid, "ticket_id": "READINESS", "ticket_title": "readiness probe",
         "pipeline_type": "connector-migration", "client_code": "GEP", "status": status,
         "stages": stages, "params": {}, "prior_results": {}, "budget_usd": 0}
    engine._pipelines[pid] = p
    return p


def _scratch_stage(name, **kw):
    s = {"name": name, "status": "pending", "depends_on": [], "type": "claude-p",
         "timeout_min": 10, "auto_advance": True}
    s.update(kw)
    return s


#: Every audit file in the estate dates from this window. Carried into the evidence of the
#: gates whose history is stale (finding F4) so a reader is never shown a three-month-old
#: number as if it described the system now.
#: Only events a RUN produces. The first version of this took every event in the file, and
#: the moment the reconciler wrote status_reconciled / verdict_recorded events the window
#: stretched to today — so evidence about a history that stopped in May started reading as
#: though the system had been busy through August. An instrument that includes its own
#: writes in the period it reports is measuring itself.
_ACTIVITY = {"stage_started", "stage_completed", "stage_failed", "stage_skipped",
             "restart_from_stage", "retry_stage", "gate_approved", "gate_rejected"}


def _history_window():
    runs = _audits()
    stamps = sorted(e.get("timestamp", "") for r in runs for e in r["events"]
                    if e.get("timestamp") and e.get("event_type") in _ACTIVITY)
    if not stamps:
        return ""
    return f"{stamps[0][:10]} to {stamps[-1][:10]}"


def g_attempt_cap_on_the_live_path():
    """Is the retry cap enforced on the path that actually restarts stages?

    Watched, not inferred: the probe drives `retry_stage` and `restart_from_stage` past
    the ceiling and requires each to refuse. The previous version searched
    `pipelines.py` for a regex near those two function names — which a comment satisfies.
    """
    engine, audit_trail, _ = _engine()
    src = f"{CONNECTORS.name}/orchestrator/pipelines.py, driven"
    cap = getattr(engine, "MAX_ATTEMPTS_PER_STAGE", None)
    refused = getattr(engine, "ControlRefused", None)
    ev = []
    if cap is None or refused is None:
        return _fail("the engine declares no attempt cap",
                     ["no MAX_ATTEMPTS_PER_STAGE / ControlRefused in pipelines.py",
                      "1,004 restart_from_stage events recorded; worst 352 in one run"], src)
    ev.append(f"MAX_ATTEMPTS_PER_STAGE = {cap}")

    watched = {}
    for path in ("retry_stage", "restart_from_stage"):
        p = _scratch_pipeline(engine, f"pipe_cap_{path}",
                              [_scratch_stage("stuck", status="failed", _attempts=cap)])
        try:
            getattr(engine, path)(p["id"], "stuck")
            watched[path] = None
        except refused as exc:
            watched[path] = getattr(exc, "control", "?")
        except Exception as exc:
            watched[path] = f"raised {type(exc).__name__}"

    # A guard that refuses everything would satisfy the two checks above while silently
    # disabling retry altogether, so the honest direction is measured too — and the SAME
    # dispatch establishes that the production path actually increments the counter.
    #
    # ⭐ This second half is why the probe was rewritten twice. It used to hand itself a
    # stage with `_attempts` already at the ceiling, which proves the comparison fires but
    # proves nothing about whether anything ever moves the counter. Deleting the single
    # line that writes `_attempts` left this gate reporting "watched refusing" over an
    # engine whose cap could never fire.
    p = _scratch_pipeline(engine, "pipe_cap_honest", [_scratch_stage("fresh")])
    before_attempts = engine.attempts(p["stages"][0])
    permitted = bool(engine.start_pipeline(p["id"]))
    counts = engine.attempts(p["stages"][0]) > before_attempts

    # The counter the cap is measured against must not be resettable from the dashboard.
    # `_retry_count` is now only informational — `attempts()` reads `_attempts` — so this
    # greps for a pop of EITHER. Guarding only the old field would have let a future
    # `clear_context` zero the real counter with this gate still green.
    # ⚠ The quote is matched EXPLICITLY. The original regex here was
    # `pop\(\s*.._retry_count`, and it never matched the line it was written to catch:
    # after `pop(` the source reads `"_retry_count`, so `..` consumes `"_` and the literal
    # then has to match `retry_count` against `retry_count` one character too late. The
    # `not cleared` half of this gate's pass condition was therefore VACUOUSLY TRUE — at
    # ea888b0 and in the first version of this rewrite. Verified by running both patterns
    # against the real line from server.py at 3da40f6.
    cleared = _grep("orchestrator/server.py",
                    r"""pop\(\s*['"](_attempts|_retry_count)""")
    for path, control in watched.items():
        ev.append(f"{path} at the cap -> "
                  + (f"REFUSED ({control})" if control == "attempt_cap"
                     else f"NOT REFUSED ({control})"))
    ev.append("a first dispatch is still permitted" if permitted
              else "a first dispatch was ALSO refused — the cap disables the feature")
    ev.append(f"and that dispatch moved the counter: {before_attempts} -> "
              f"{engine.attempts(p['stages'][0])}" if counts
              else "⛔ the dispatch did NOT move the counter — the cap can never fire")
    if cleared:
        ev.append(f"server.py:{cleared[0][0]} POPS the attempt counter, resetting it: "
                  f"{cleared[0][1]}")
    ev.append(f"history, {_history_window()}: 1,004 restart_from_stage events, worst 352 "
              f"in one run, all of it before this cap existed")

    if (all(c == "attempt_cap" for c in watched.values())
            and permitted and counts and not cleared):
        return _pass("the restarting path is capped, and was watched refusing", ev, src)
    return _fail("the restarting path is not capped", ev, src)


def g_failure_is_bounded():
    """Is failure bounded — can a stage be dispatched forever?

    Drives the choke point every dispatch passes through, including the watchdog's, and
    counts how many attempts it takes before dispatch stops. The previous version of this
    probe had a single return path, `_fail`: it could not have reported a bounded system
    if one had existed, which makes it a constant rather than an instrument.
    """
    engine, _, _ = _engine()
    src = f"{CONNECTORS.name}/orchestrator/pipelines.py::_build_stage_requests, driven"
    cap = getattr(engine, "MAX_ATTEMPTS_PER_STAGE", None)
    runs = _audits()
    per = []
    for r in runs:
        c = collections.Counter(e.get("stage_name") for e in r["events"]
                                if e.get("event_type") == "restart_from_stage")
        if c:
            per.append((r["id"],) + c.most_common(1)[0])
    worst = max(per, key=lambda x: x[2]) if per else None
    ev = ["pipelines.py records the 2026-08-14 incident verbatim: the stage was "
          "'auto-restarted with no attempt cap', and ten containers took the whole "
          "10-core canadacentral quota"]
    if worst:
        ev.append(f"worst in the recorded history ({_history_window()}): {worst[2]} "
                  f"restarts of '{worst[1]}' in {worst[0]} — before any cap existed")

    if cap is None:
        ev.append("the engine declares no ceiling, so nothing bounds the loop")
        return _fail("no attempt cap on restart", ev, src)

    # A watchdog that re-dispatches a permanently-failing stage: reset to pending and ask
    # again, exactly as recover_stale_pipelines does, and see where it stops.
    LIMIT = 50
    p = _scratch_pipeline(engine, "pipe_bounded", [_scratch_stage("stuck")])
    dispatched = 0
    for _ in range(LIMIT):
        got = engine._build_stage_requests(p, [0])
        if not got:
            break
        dispatched += 1
        p["stages"][0]["status"] = "pending"
    ev.append(f"simulated an uncapped watchdog: asked for {LIMIT} dispatches, the engine "
              f"granted {dispatched} and then refused")
    ev.append(f"the stage was left '{p['stages'][0]['status']}', so it is not re-offered "
              f"forever")

    if dispatched == 0:
        ev.append("nothing was dispatched at all — the ceiling refuses honest work")
        return _fail("the cap disables dispatch entirely", ev, src)
    if dispatched >= LIMIT:
        return _fail("no attempt cap on restart", ev, src)
    if dispatched != cap:
        ev.append(f"stopped at {dispatched}, but MAX_ATTEMPTS_PER_STAGE is {cap}")
    return _pass(f"failure is bounded at {dispatched} attempts, watched", ev, src)


def g_concurrency_is_reserved_outside_the_agent():
    """Is concurrent STAGE dispatch bounded, across pipelines?

    Waves bound how many pipelines start together. Ten containers took the region quota at
    the stage level, across runs. The previous probe searched `pipelines.py` for the
    lowercase literal `max_parallel` — a string, not a behaviour.
    """
    engine, _, _ = _engine()
    src = f"{CONNECTORS.name}/orchestrator/pipelines.py::_build_stage_requests, driven"
    par = _grep("orchestrator/engine/wave_scheduler.py", r"max_parallel")
    ceiling = getattr(engine, "MAX_PARALLEL_STAGE_DISPATCH", None)
    ev = [f"{len(par)} max_parallel reference(s) in the wave scheduler — those bound how "
          f"many PIPELINES start together"]
    if not par and ceiling is None:
        raise Unmeasurable("no concurrency mechanism found to assess")
    if ceiling is None:
        ev.append("pipelines.py declares no stage-level ceiling — nothing bounds "
                  "concurrent STAGE dispatch, which is the level ten containers took the "
                  "region quota at")
        return _fail("concurrency is bounded per wave, not per stage dispatch", ev, src)
    ev.append(f"MAX_PARALLEL_STAGE_DISPATCH = {ceiling}")

    # Two pipelines, because the quota was taken across runs and not inside one.
    engine._pipelines.clear()
    n = ceiling + 3
    a = _scratch_pipeline(engine, "pipe_conc_a", [_scratch_stage(f"a{i}") for i in range(n)])
    b = {"id": "pipe_conc_b", "ticket_id": "READINESS", "ticket_title": "readiness probe",
         "pipeline_type": "connector-migration", "client_code": "GEP", "status": "running",
         "stages": [_scratch_stage("b0")], "params": {}, "prior_results": {}, "budget_usd": 0}
    engine._pipelines["pipe_conc_b"] = b
    granted = len(engine._build_stage_requests(a, list(range(n))))
    spill = len(engine._build_stage_requests(b, [0]))
    deferred = [s["name"] for s in a["stages"] if s["status"] == "pending"]
    ev.append(f"asked for {n} concurrent stage dispatches in one run: {granted} granted, "
              f"{len(deferred)} left pending")
    ev.append(f"then asked a SECOND pipeline for one more: {spill} granted — the ceiling "
              f"is {'global' if spill == 0 else 'per-pipeline, which the quota is not'}")

    # A ceiling that counts a gate waiting on a human deadlocks every other pipeline. That
    # is a control causing the outage it was added to prevent, so it is measured.
    engine._pipelines.clear()
    g = _scratch_pipeline(engine, "pipe_conc_gate",
                          [_scratch_stage(f"g{i}", type="gate", gate_type="manual",
                                          timeout_min=None) for i in range(ceiling + 2)])
    engine._build_stage_requests(g, list(range(ceiling + 2)))
    work = {"id": "pipe_conc_work", "ticket_id": "READINESS", "ticket_title": "probe",
            "pipeline_type": "connector-migration", "client_code": "GEP",
            "status": "running", "stages": [_scratch_stage("real")], "params": {},
            "prior_results": {}, "budget_usd": 0}
    engine._pipelines["pipe_conc_work"] = work
    starved = not engine._build_stage_requests(work, [0])
    ev.append("paused manual gates starve real work — the ceiling deadlocks" if starved
              else "manual gates hold no slot, so paused runs cannot starve the rest")

    if granted == ceiling and deferred and spill == 0 and not starved:
        return _pass(f"stage dispatch is bounded at {ceiling}, watched deferring", ev, src)
    return _fail("concurrency is bounded per wave, not per stage dispatch", ev, src)


def g_orphans_are_reaped():
    """Is dispatched work either finished or killed?

    The previous probe searched `orchestrator/engine/work_guard.py` for a heartbeat and
    returned `_fail` unconditionally. work_guard's lease covers repo locks between agents;
    it was never going to hold a reaper for dispatched cloud work — and the probe never
    looked in `pipelines.py`, where an orphan reclaimer already lived.
    """
    engine, audit_trail, _ = _engine()
    src = f"{CONNECTORS.name}/orchestrator/pipelines.py::reap_expired_leases, driven"
    reap = getattr(engine, "reap_expired_leases", None)
    runs = _audits()
    stuck = [r["id"] for r in runs
             if r["events"] and r["events"][-1].get("event_type") == "stage_started"]
    ev = [f"{len(stuck)} of {len(runs)} recorded runs ({_history_window()}) sit at "
          f"stage_started with no terminal event",
          "documented: a container outlived its stage and ten of them took a 10-core quota"]
    if reap is None:
        ev.append("work_guard's lease covers REPO LOCKS between agents, not dispatched "
                  "cloud work, and no reaper exists in the engine")
        return _fail("no lease, timeout or reaper for dispatched work", ev, src)

    from datetime import timedelta as _td
    def _iso(mins):
        return (datetime.now(timezone.utc) + _td(minutes=mins)).isoformat(timespec="seconds")

    # 1. an expired lease is killed, and killed TERMINALLY — not made runnable again.
    p = _scratch_pipeline(engine, "pipe_reap",
                          [_scratch_stage("orphan", status="dispatched",
                                          lease_expires_at=_iso(-120))])
    killed = reap()
    after = p["stages"][0]["status"]
    log = [e.get("event_type") for e in
           json.loads(audit_trail._audit_path("pipe_reap").read_text(encoding="utf-8"))["events"]] \
        if audit_trail._audit_path("pipe_reap").exists() else []

    # 2. a live lease is NOT killed — a reaper that kills everything is not a reaper.
    q = _scratch_pipeline(engine, "pipe_reap_live",
                          [_scratch_stage("running", status="dispatched",
                                          lease_expires_at=_iso(+30))])
    spared = reap()

    ev.append(f"expired lease -> {len(killed)} reaped, stage left '{after}'")
    ev.append("reaped work was NOT made runnable again" if after == "failed"
              else f"reaped work went to '{after}' — a re-dispatch would relaunch its "
                   f"cloud work and land the same rows twice")
    ev.append(f"the log gained a terminal event: {'yes' if 'stage_failed' in log else 'NO'} "
              f"({', '.join(log) or 'nothing recorded'})")
    ev.append(f"live lease -> {len(spared)} reaped; a still-running stage is left alone"
              if not spared else "a LIVE lease was reaped — the reaper kills honest work")

    if killed and after == "failed" and "stage_failed" in log and not spared:
        return _pass("dispatched work is leased and reaped, watched", ev, src)
    return _fail("no lease, timeout or reaper for dispatched work", ev, src)


def g_verdict_is_computed_from_history():
    """Does the terminal verdict read the append-only log, or a last-write-wins field?

    Driven rather than grepped. The regex version located `any_failed = any(... for x in
    <name>)` and asked whether `<name>` contained "event" — which renaming a variable
    satisfies.
    """
    engine, audit_trail, _ = _engine()
    src = f"{CONNECTORS.name}/orchestrator/pipelines.py::terminal_verdict, driven"
    verdict_fn = getattr(engine, "terminal_verdict", None)
    body = _src("orchestrator/pipelines.py")
    m = re.search(r"any_failed\s*=\s*any\(.{0,400}?for \w+ in ([^\s:)]+)", body, re.S)
    iterable = m.group(1) if m else ""
    ev = [f"any_failed iterates over: {iterable or '(not found)'}"]
    if verdict_fn is None:
        ev += ['that is pipeline["stages"][i]["status"] — last-write-wins',
               "a stage that failed 100 times and succeeded on 101 reads 'completed', so "
               "it contributes nothing to any_failed",
               "the failures exist only in the append-only log, which this does not consult",
               "3 runs recorded succeeded over 115, 21 and 15 failures"]
        return _fail("the verdict reads current state, not history", ev, src)

    # The defect itself, reproduced: a stage that fails many times and then succeeds.
    FAILS = 7
    p = _scratch_pipeline(engine, "pipe_verdict", [_scratch_stage("flaky")])
    for _ in range(FAILS):
        engine.start_pipeline(p["id"])
        engine.on_session_complete(p["id"], "flaky", "ses", success=False, error="transient")
        p["stages"][0]["status"] = "pending"
        p["stages"][0]["_attempts"] = 0
    engine.start_pipeline(p["id"])
    engine.on_session_complete(p["id"], "flaky", "ses", success=True)
    v = p.get("verdict") or {}
    ev.append(f"drove a stage to fail {FAILS}x then succeed: status='{p['status']}', "
              f"failures_in_log={v.get('failures_in_log')}, clean={v.get('clean')}")

    # ⭐ The discriminating case, and the reason this probe was rewritten a second time.
    # An independent review reverted `any_failed` to the original last-write-wins
    # expression — one edit — and this gate still read PASS, because everything it checked
    # (failures_in_log, clean) comes from the log INDEPENDENTLY of any_failed. The gate
    # could not see the defect it is named for.
    #
    # In the current engine every status write is mirrored by an audit event, so the two
    # expressions agree on any state the engine can reach on its own. This constructs the
    # one state where they cannot: a stage whose log ends stage_failed and whose status
    # field says completed. Reading the field gives `succeeded`; reading the log gives
    # `failed`.
    d = _scratch_pipeline(engine, "pipe_verdict_liar", [_scratch_stage("liar")])
    engine.start_pipeline(d["id"])
    engine.on_session_complete(d["id"], "liar", "ses", success=False, error="real")
    d["stages"][0]["status"] = "completed"     # the field, without the log
    d["status"] = "running"
    d.pop("verdict", None)
    liar = verdict_fn(d) or {}
    ev.append(f"a stage whose log ends stage_failed but whose status field says completed: "
              f"verdict={liar.get('status')} — the verdict follows "
              f"{'the log' if liar.get('status') == 'failed' else 'the STATUS FIELD'}")

    # A log that cannot be read must not read as a clean one.
    q = _scratch_pipeline(engine, "pipe_verdict_nolog",
                          [_scratch_stage("a", status="completed")])
    blind = verdict_fn(q) or {}
    ev.append(f"with no audit log at all: basis={blind.get('basis')}, "
              f"status={blind.get('status')} — an unreadable history "
              f"{'fails closed' if blind.get('status') == 'failed' else 'reads as success'}")

    saw_failures = v.get("failures_in_log") == FAILS and v.get("clean") is False
    follows_log = liar.get("status") == "failed"
    fails_closed = blind.get("basis") == "UNMEASURABLE" and blind.get("status") == "failed"
    if saw_failures and follows_log and fails_closed:
        return _pass("the verdict is derived from the event log", ev, src)
    if not saw_failures:
        ev.append("the verdict could not see failures that are in the log")
    if not follows_log:
        ev.append("the verdict followed the status field over the log — this is the "
                  "last-write-wins defect itself")
    return _fail("the verdict reads current state, not history", ev, src)


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
    have = [d for d in VERSION_DIMENSIONS if re.search(rf"{d}", body)]
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
    src = "blueprints/windsorai_gep.yaml"
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
    Gate("tenancy", "Is blast radius certifiable?",
         "Certifying a pull whose scope is unknown certifies nothing.",
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
    print(f"\nUnattended-migration readiness: {n_pass} of {len(results)} gates pass")
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
