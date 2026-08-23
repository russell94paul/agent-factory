"""May I run an agent right now — and if so, how far may I trust it?

The readiness board answers "which gates pass". An operator standing in front of it wants a
different thing: **can I press start, and what happens if I walk away.** Those are not the same
question and the board cannot answer the second one by listing the first.

⭐ **Three questions get conflated into one word, "ready", and they have different answers today.**

    MAY I RUN IT?          is there a human who can see it and stop it
    MAY I LEAVE IT?        is it bounded — cap, reaper, ceiling, concurrency
    MAY I TRUST OUTPUT?    is it certified — contract, corpus, version, an evaluator that is
                           a principal the agent cannot impersonate

Answering them separately is the point. On 2026-08-23 the first was YES and the other two were NO,
and a board that renders a single "9 of 30" cannot say that — so an operator reads 30%, concludes
"not yet", and does not start the supervised run that is both safe and *the only way to measure
the loop at all*.

⚠ **The circle this exists to break.** `finishes` and `succeeds` are UNMEASURABLE because no run
has started since the controls landed. They cannot go green until something runs; nothing should
run unattended until they are green. The way out is a supervised run — a human is a cap, a reaper
and a spend ceiling, just an expensive one — and this module says so out loud rather than leaving
the operator to infer that a red board forbids it.

⛔ **What this is NOT.** It is not permission, and it never dispatches anything. It reports what
the gates say and names what a human is standing in for. A SUPERVISED verdict means "the controls
that are missing are ones a watching human replaces" — it does not mean the run is safe to start
against production, which is a judgement no probe here makes.
"""
from __future__ import annotations

from typing import Dict, List

from .readiness import GATES, PASS, measure

#: Bounded execution. Every one of these is a control a human otherwise has to BE.
#:
#: Sourced from the gate list's own `bounded` phase plus the two loop gates that observe whether a
#: run terminates. Not a judgement about which controls matter — it is the phase the build-order
#: research already named as prerequisite 1-2, quoted in board.py.
UNATTENDED_GATES = ("cap", "reaper", "ceiling", "concurrency", "bounded")

#: Whether the OUTPUT can be believed, which is independent of whether the run completes. A run
#: can finish perfectly and produce something nothing can check — that is the liability the PBI
#: team's own boot prompt refuses to build toward.
TRUST_GATES = ("suite", "certified", "corpus", "version", "breadth", "isolated")

#: What a supervised run needs in order to be worth starting: not controls, but OBSERVABILITY.
#: A human substituting for a reaper can only do it if they can see the run and it leaves a
#: record. Both of those became true on 2026-08-23 — the Sessions tab surfaces blocked questions
#: from the jobs registry, and `.data/runs.jsonl` got its first RECORDED rows.
#:
#: Deliberately NOT a gate list. These are facts about this machine, checked in `_observability()`,
#: because no gate measures them and inventing gates to make a level look measured would be the
#: exact dishonesty the UNGATED rule exists to prevent.
SUPERVISED = "SUPERVISED-OK"
SUPERVISED_BLOCKED = "SUPERVISED-BLOCKED"
UNATTENDED = "UNATTENDED-OK"
UNATTENDED_BLOCKED = "UNATTENDED-BLOCKED"
TRUSTED = "OUTPUT-CERTIFIABLE"
TRUST_BLOCKED = "OUTPUT-UNCERTIFIED"
UNGATED = "UNGATED"


def _verdicts(measured=None) -> Dict[str, object]:
    """gate id -> Result, measured on this call. Never cached: a launch decision read off a stale
    board is the failure mode every other surface here is written to avoid.

    `measured` accepts an ALREADY-TAKEN `measure()` list — the `(Gate, Result)` pairs, not a
    dict — so a caller that has just measured for its own reasons does not pay for a second full
    pass. ⛔ It is a *same-instant* reuse, not a cache: the readiness page measures once per
    render and hands the result straight here. Passing anything older re-introduces exactly the
    staleness this docstring refuses, and nothing here can tell the difference — the caller owns
    that promise.
    """
    return {g.id: r for g, r in (measure() if measured is None else measured)}


def _blockers(ids, verdicts) -> List[dict]:
    """The named gates that are not passing, with why — in the order given, which is build order."""
    out = []
    for gid in ids:
        r = verdicts.get(gid)
        if r is None:
            # A named gate that no longer exists is a broken map, not a pass. Same rule as
            # roadmap._validate: an edge that does not resolve must be loud.
            out.append({"gate": gid, "verdict": "MISSING",
                        "headline": "named here but absent from GATES — the map is stale"})
        elif r.verdict != PASS:
            out.append({"gate": gid, "verdict": r.verdict, "headline": r.headline})
    return out


def _observability() -> List[dict]:
    """What a supervising human needs in order to actually supervise. Facts, not gates."""
    from pathlib import Path
    from . import sessions as _s

    root = Path(__file__).resolve().parent.parent
    ledger = root / ".data" / "runs.jsonl"
    out = [
        {"what": "a run leaves a durable record",
         "ok": ledger.is_file(),
         "detail": (f"{sum(1 for _ in ledger.open(encoding='utf-8'))} row(s) in .data/runs.jsonl"
                    if ledger.is_file() else
                    ".data/runs.jsonl does not exist — a finished lane leaves no trace")},
        {"what": "a blocked agent's question reaches a human",
         "ok": _s.JOBS.is_dir(),
         "detail": (f"{len(_s.blocked())} question(s) waiting, surfaced oldest-first"
                    if _s.JOBS.is_dir() else "no jobs registry — questions cannot be seen")},
        {"what": "liveness is measured, not inferred",
         "ok": _s._running_pids() is not None,
         "detail": ("the process table is readable" if _s._running_pids() is not None else
                    "the process table could not be read — a session's state would be a guess")},
    ]
    return out


def levels(measured=None) -> List[dict]:
    """The three questions, answered separately, measured now.

    Order is deliberate: run, leave, trust. Each is strictly harder than the one before it, and an
    operator reads down until the answer stops being yes.

    `measured` is a same-render `measure()` result to reuse; see `_verdicts`.
    """
    v = _verdicts(measured)
    obs = _observability()
    obs_bad = [o for o in obs if not o["ok"]]

    return [
        {"question": "May I RUN an agent, with me watching?",
         "state": SUPERVISED if not obs_bad else SUPERVISED_BLOCKED,
         "blockers": [{"gate": "-", "verdict": "MISSING", "headline": o["what"]} for o in obs_bad],
         "checks": obs,
         "means": ("Yes — and the missing bounded controls are ones you are standing in for. "
                   "You are the cap, the reaper and the spend ceiling. That is expensive and it "
                   "is legitimate. ⭐ It is also the ONLY way `finishes` and `succeeds` can stop "
                   "being UNMEASURABLE, because they need a run to have happened."),
         "not_means": "It does not mean safe against production. No probe here judges that."},

        {"question": "May I LEAVE it running, unattended?",
         "state": UNATTENDED if not _blockers(UNATTENDED_GATES, v) else UNATTENDED_BLOCKED,
         "blockers": _blockers(UNATTENDED_GATES, v),
         "checks": [],
         "means": "Every control a walking-away human gives up is proven to exist.",
         "not_means": ("Each red gate below is a specific way a run can consume something without "
                       "stopping. Ten containers once ate an entire region quota for three hours "
                       "because a stage timed out, nothing killed the container, and restart had "
                       "no cap — that is `reaper` and `bounded` in one incident.")},

        {"question": "May I TRUST what it produced?",
         "state": TRUSTED if not _blockers(TRUST_GATES, v) else TRUST_BLOCKED,
         "blockers": _blockers(TRUST_GATES, v),
         "checks": [],
         "means": "The output can be certified by something the agent cannot be.",
         "not_means": ("Independent of the two above: a run can finish cleanly and produce "
                       "something nothing can check. Output you cannot certify is not a "
                       "deliverable, it is a liability.")},
    ]


def teams(measured=None) -> List[dict]:
    """Per-team launch state, taking UNGATED seriously.

    A team with no gates is not at 0%. It has no contract, so there is nothing to measure and a
    percentage would be invented progress — the same distinction `blocked()` draws between a
    question with no session and one that was never asked.
    """
    from .roadmap import TEAMS

    v = _verdicts(measured)
    out = []
    for name, spec in TEAMS.items():
        gids = list(spec.get("gates") or [])
        if not gids:
            out.append({"team": name, "state": UNGATED, "passing": None, "of": 0,
                        "blockers": [], "intent": spec.get("intent", ""),
                        "note": spec.get("unblock") or
                                "no contract exists, so there is nothing to gate"})
            continue
        bad = _blockers(gids, v)
        out.append({"team": name,
                    "state": UNATTENDED if not bad else UNATTENDED_BLOCKED,
                    "passing": len(gids) - len(bad), "of": len(gids),
                    "blockers": bad, "intent": spec.get("intent", ""),
                    "note": ""})
    return out


def summary(measured=None) -> str:
    """One line for a CLI or a banner. The first level whose answer is not yes."""
    for lv in levels(measured):
        if lv["blockers"]:
            n = len(lv["blockers"])
            return f"{lv['state']} — {lv['question']} blocked by {n} gate(s)"
    return f"{TRUSTED} — every level clear"


def main(argv=None) -> int:
    for lv in levels():
        print(f"\n{lv['question']}\n  {lv['state']}")
        for b in lv["blockers"]:
            print(f"    - {b['gate']:<12} {b['verdict']:<12} {b['headline']}")
        for c in lv.get("checks") or []:
            print(f"    {'OK ' if c['ok'] else 'NO '} {c['what']} — {c['detail']}")
    print("\nTeams")
    for t in teams():
        head = (f"{t['passing']} of {t['of']}" if t["passing"] is not None else "UNGATED")
        print(f"  {t['team']:<34} {head:<10} {t['state']}")
        if t["note"]:
            print(f"      {t['note'][:150]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
