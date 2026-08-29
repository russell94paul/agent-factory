"""The forward plan, expressed as measurements rather than as a task list.

    python -m factory.plan_gates

⭐ **There is no task list in this file, and that is deliberate.** `factory.board` already learned
this lesson and states it: a hand-typed list whose *status* is computed is *"a hand-maintained board
wearing a computed status, which is the same defect as a checkbox grid with nicer wiring."*

So every item of forward work is a **gate** — a question with a probe that answers it from the repo
as it is right now. A gate that passes is done and leaves the board. A gate that fails is the work.
Nobody ticks anything, and a board that disagrees with the repo is not possible.

⛔ **These are NOT the thirty readiness gates, and must never be summed with them.**
`factory.readiness` answers *"can an agent team run a connector migration unattended?"* and measures
against `prefect-connectors`. This module answers *"how far along is the platform build?"* and
measures against this repo and its neighbours. Adding the two scores together produces a number
about nothing. That conflation has already been made once in this estate and had to be corrected —
a `10 of 30` was quoted as platform progress when it measured a different repo's orchestrator.

**Every probe reads the world.** None takes an argument saying what the answer should be, and none
reads a file whose only purpose is to record the answer. If a probe cannot look, it raises
`Unmeasurable` and the gate reports `UNMEASURABLE` — never `FAIL`, because *"I could not look"* and
*"I looked and it was wrong"* are different facts.
"""
from __future__ import annotations

import json
import pathlib
import subprocess
from typing import Callable, List

from .readiness import (
    FAIL,
    NOT_RUN,
    PASS,
    UNMEASURABLE,
    Gate,
    Result,
    Unmeasurable,
    _fail,
    _notrun,
    _pass,
)

FACTORY = pathlib.Path(__file__).resolve().parent.parent
REPOS = FACTORY.parent
CLIENTS = REPOS / "clients"

#: Grouped by what the group is FOR, not by sprint. A phase is a question an operator asks.
PLAN_PHASES = {
    "land": "Is the finished work landed?",
    "surface": "Can an operator see the work?",
    "trace": "Can a change be traced to what asked for it?",
    "retry": "Does a retry know more than the attempt before it?",
}


def _git(*args, cwd=FACTORY) -> str:
    try:
        r = subprocess.run(["git", *args], cwd=str(cwd), capture_output=True,
                           text=True, timeout=30)
    except Exception as exc:                                       # noqa: BLE001
        raise Unmeasurable(f"git {' '.join(args)} failed: {exc}")
    return r.stdout.strip()


def _tracker_html() -> str:
    """The RENDERED page, not the generator.

    ⭐ Checking the generator's imports would pass the moment somebody adds an import line, whether
    or not anything reaches the page. A query-layer check is not a render check — a lesson this
    estate has paid for more than once.
    """
    p = FACTORY / "tracker.html"
    if not p.is_file():
        raise Unmeasurable("tracker.html not generated — run scripts/local_tracker.py")
    return p.read_text(encoding="utf-8", errors="replace")


# --------------------------------------------------------------------------------- land
#: The four commits that fix cap / from-history / reaper / concurrency. Measured 2026-08-29 as
#: living only on `lane/control-plane`, absent from the working branch.
_GATE_FIX = ["040fe79", "4e321d2", "3e6416b", "38ff8f0"]


def g_gate_fixes_landed():
    missing = []
    for sha in _GATE_FIX:
        try:
            subprocess.run(["git", "merge-base", "--is-ancestor", sha, "HEAD"],
                           cwd=str(FACTORY), capture_output=True, timeout=30, check=True)
        except subprocess.CalledProcessError:
            missing.append(sha)
        except Exception as exc:                                   # noqa: BLE001
            raise Unmeasurable(f"could not test ancestry of {sha}: {exc}")
    src = "git merge-base --is-ancestor <sha> HEAD"
    if not missing:
        return _pass(f"all {len(_GATE_FIX)} gate-fix commits are in HEAD", [], src)
    return _fail(
        f"{len(missing)} of {len(_GATE_FIX)} gate-fix commits are NOT in this branch",
        [f"missing: {', '.join(missing)}",
         "they live on lane/control-plane; measured 2026-08-29",
         "⚠ measuring readiness on this branch understates what is built"], src)


def g_work_reaches_main():
    """Has anything ever been merged back to `main`?"""
    counts = _git("rev-list", "--left-right", "--count", "main...HEAD")
    src = "git rev-list --left-right --count main...HEAD"
    if not counts:
        raise Unmeasurable("could not compare HEAD against main")
    try:
        main_ahead, head_ahead = (int(x) for x in counts.split())
    except ValueError:
        raise Unmeasurable(f"unexpected rev-list output: {counts!r}")
    if head_ahead == 0:
        return _pass("HEAD adds nothing beyond main", [], src)
    return _fail(f"{head_ahead} commits on this branch have never reached main",
                 [f"main is {main_ahead} ahead of HEAD",
                  "six branches diverged from main; none merged back"], src)


# --------------------------------------------------------------------------------- surface
def g_sessions_are_rendered():
    """`factory.sessions` is imported by the tracker but has no section on the page."""
    html = _tracker_html()
    src = "grep the rendered tracker.html"
    hits = [w for w in ("contended", "live session", "collision", "duplicate session")
            if w.lower() in html.lower()]
    if hits:
        return _pass(f"the page shows live-session state ({', '.join(hits)})", [], src)
    return _fail("the page shows lanes but not who is working in them",
                 ["factory/sessions.py exposes live_by_lane, contended_repos, duplicates",
                  "local_tracker.py imports it; nothing reaches the page"], src)


def g_presets_are_rendered():
    html = _tracker_html()
    src = "grep the rendered tracker.html"
    if "preset" in html.lower():
        return _pass("presets reach the page", [], src)
    return _fail("presets exist but no operator can see them",
                 ["factory/presets.py holds 5 measured ticket types"], src)


def g_the_plan_is_on_a_screen():
    """`roadmap.py` and `goals.py` are the only modules the tracker does not import."""
    p = FACTORY / "scripts" / "local_tracker.py"
    if not p.is_file():
        raise Unmeasurable("scripts/local_tracker.py not found")
    body = p.read_text(encoding="utf-8", errors="replace")
    src = "grep imports in scripts/local_tracker.py"
    missing = [m for m in ("roadmap", "goals", "plan_gates") if f"factory import {m}" not in body
               and f"factory.{m}" not in body]
    if not missing:
        return _pass("the plan and its goals reach the page", [], src)
    return _fail(f"{len(missing)} planning module(s) never reach the page",
                 [f"absent: {', '.join(missing)}",
                  "this is why the forward plan is not on a screen"], src)


# --------------------------------------------------------------------------------- trace
def g_a_run_names_its_work_item():
    """Runs record lane, outcome and cost — but nothing says which request asked for them."""
    p = FACTORY / "factory" / "runs.py"
    if not p.is_file():
        raise Unmeasurable("factory/runs.py not found")
    body = p.read_text(encoding="utf-8", errors="replace")
    src = "grep for a work-item field in factory/runs.py"
    if any(k in body for k in ('"ticket"', "'ticket'", '"work_item"', "'work_item'")):
        return _pass("a run carries the work item that asked for it", [], src)
    return _fail("no run can be traced back to the request that caused it",
                 ["the trail from request to evidence must be rebuilt by hand",
                  "one field also serves the board and the filterable artefact view"], src)


def g_the_warehouse_layer_is_representable():
    """Client tickets track two of the three layers."""
    arts = sorted(CLIENTS.glob("*/tickets/*/artifact.yaml"))
    src = "read clients/*/tickets/*/artifact.yaml"
    if not arts:
        raise Unmeasurable(f"no artifact.yaml found under {CLIENTS}")
    without = []
    for a in arts:
        body = a.read_text(encoding="utf-8", errors="replace")
        if "snowflake:" not in body:
            without.append(a.parent.name)
    if not without:
        return _pass(f"all {len(arts)} ticket artefacts can describe the warehouse layer", [], src)
    return _fail(f"{len(without)} of {len(arts)} artefacts cannot describe the warehouse layer",
                 [f"missing a snowflake key: {', '.join(without)}",
                  "changes tracks eclipse and pbi_model only",
                  "the warehouse carries the largest manual step and cannot be represented"], src)


def g_dwell_time_is_measurable():
    """`stage_history` records dates, so time in stage below a day cannot be expressed."""
    arts = sorted(CLIENTS.glob("*/tickets/*/artifact.yaml"))
    src = "read stage_history entries in clients/*/tickets/*/artifact.yaml"
    if not arts:
        raise Unmeasurable(f"no artifact.yaml found under {CLIENTS}")
    dated = 0
    for a in arts:
        for line in a.read_text(encoding="utf-8", errors="replace").splitlines():
            s = line.strip()
            if s.startswith(("entered:", "exited:")) and "T" not in s and "null" not in s:
                dated += 1
    if dated == 0:
        return _pass("stage transitions carry a time, so dwell is measurable", [], src)
    return _fail(f"{dated} stage transitions record a date with no time",
                 ["dwell below a day is UNMEASURABLE",
                  "the state model cannot measure the bottleneck it exists to expose"], src)


# --------------------------------------------------------------------------------- retry
def g_a_cap_kill_is_distinguishable():
    """The `limit` field exists; nothing populates it with a real observation."""
    p = FACTORY / "factory" / "deploy.py"
    if not p.is_file():
        raise Unmeasurable("factory/deploy.py not found")
    body = p.read_text(encoding="utf-8", errors="replace")
    src = "grep for a LIMIT_HIT producer in factory/deploy.py"
    if "LIMIT_HIT" not in body:
        return _fail("a cap-kill is recorded as an ordinary failure",
                     ["the retry is told to change approach when it only ran out of room"], src)
    produced = body.count("limit=LIMIT_HIT")
    if produced:
        return _pass(f"a cap-kill is distinguishable ({produced} producer(s))", [], src)
    return _notrun("the field exists; nothing has ever set it",
                   ["every real dispatch records UNDETERMINED",
                    "needs a documented CLI signal or a stream-json transcript parse",
                    "⚠ NOT_RUN, not FAIL — the distinction is built, the detection is not"], src)


PLAN_GATES: List[Gate] = [
    Gate("gate-fixes-landed", "Are the finished gate fixes on this branch?",
         "readiness measured on a branch missing them understates what is built",
         g_gate_fixes_landed, "land"),
    Gate("reaches-main", "Has any of this work reached main?",
         "six branches diverged and none merged back; nothing is durable until one does",
         g_work_reaches_main, "land"),
    Gate("sessions-rendered", "Can an operator see who else is in a repo?",
         "a tree drifted 88 to 90 files mid-session and nothing surfaced it",
         g_sessions_are_rendered, "surface"),
    Gate("presets-rendered", "Can an operator see the ticket presets?",
         "a preset nobody can open is a table, not a tool",
         g_presets_are_rendered, "surface"),
    Gate("plan-on-a-screen", "Is the forward plan visible anywhere?",
         "roadmap and goals exist and are the only modules the tracker never imports",
         g_the_plan_is_on_a_screen, "surface"),
    Gate("run-names-work-item", "Can a run be traced to the request that caused it?",
         "without it the trail from request to evidence is rebuilt by hand six months later",
         g_a_run_names_its_work_item, "trace"),
    Gate("warehouse-representable", "Can a ticket describe a warehouse change?",
         "the layer with the largest manual step is absent from the state model",
         g_the_warehouse_layer_is_representable, "trace"),
    Gate("dwell-measurable", "Can time-in-stage be measured?",
         "dates without times cannot express the wait the whole platform exists to reduce",
         g_dwell_time_is_measurable, "trace"),
    Gate("cap-kill-detected", "Is running out of room distinguishable from being wrong?",
         "otherwise a retry is told to change an approach that was working",
         g_a_cap_kill_is_distinguishable, "retry"),
]

_ids = [g.id for g in PLAN_GATES]
if len(_ids) != len(set(_ids)):
    raise ValueError(f"duplicate plan gate id(s): {sorted({i for i in _ids if _ids.count(i) > 1})}")
for _g in PLAN_GATES:
    if _g.phase not in PLAN_PHASES:
        raise ValueError(f"{_g.id}: phase {_g.phase!r} is not one of {sorted(PLAN_PHASES)}")


def measure_plan() -> List[tuple]:
    """(gate, result) for every plan gate. An exception inside a probe becomes UNMEASURABLE."""
    out = []
    for g in PLAN_GATES:
        try:
            res = g.probe()
        except Unmeasurable as exc:
            res = Result(UNMEASURABLE, str(exc), ["the instrument could not run"], "")
        except Exception as exc:                                   # noqa: BLE001
            res = Result(UNMEASURABLE, f"probe raised {type(exc).__name__}: {exc}",
                         ["an unexpected error is NOT a failure of the thing measured"], "")
        out.append((g, res))
    return out


def main() -> int:
    rows = measure_plan()
    done = sum(1 for _, r in rows if r.verdict == PASS)
    print(f"Platform build: {done} of {len(rows)} gates pass   "
          f"[NOT the 30 readiness gates — different question, different repo]\n")
    for phase, title in PLAN_PHASES.items():
        in_phase = [(g, r) for g, r in rows if g.phase == phase]
        if not in_phase:
            continue
        ok = sum(1 for _, r in in_phase if r.verdict == PASS)
        print(f"  {title}  [{ok}/{len(in_phase)}]")
        for g, r in in_phase:
            mark = {PASS: "DONE  ", FAIL: "TODO  ",
                    UNMEASURABLE: "UNMEAS", NOT_RUN: "NOTRUN"}[r.verdict]
            print(f"    {mark}  {g.question:<52} {r.headline}")
            for e in r.evidence:
                print(f"            . {e}")
            if r.source:
                print(f"            source: {r.source}")
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
