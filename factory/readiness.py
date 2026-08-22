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


def g_failure_is_bounded():
    runs = _audits()
    per = []
    for r in runs:
        c = collections.Counter(e.get("stage_name") for e in r["events"]
                                if e.get("event_type") == "restart_from_stage")
        if c:
            per.append((r["id"],) + c.most_common(1)[0])
    worst = max(per, key=lambda x: x[2]) if per else None
    src = "orchestrator/pipelines.py:456 + audits"
    ev = ["pipelines.py records the 2026-08-14 incident verbatim: the stage was "
          "'auto-restarted with no attempt cap', and ten containers took the whole "
          "10-core canadacentral quota"]
    if worst:
        ev.append(f"worst observed: {worst[2]} restarts of '{worst[1]}' in {worst[0]}")
    return _fail("no attempt cap on restart", ev, src)


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

GATES: List[Gate] = [
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
    "judgement": "Can it tell success from failure?",
    "certification": "Can its output be certified?",
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
