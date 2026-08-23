"""Which research prompts are waiting, and which ones are lying about it.

`factory.synthesis` catches an answer that landed and was never reconciled. It cannot catch the
failure one step earlier: a prompt that was **written and never sent**. `filed()` globs `answers/`,
so a prompt with no answer is invisible to it by construction — R8, R9 and R10 sat undispatched for
a day and no instrument said so.

⚠ **"No answer yet" is two different states and they need different actions.** A prompt nobody has
sent is waiting on *Paul*; a prompt in flight is waiting on *the researcher*. Collapsing them into
one "pending" bucket is the same error as collapsing UNMEASURABLE into FAIL — it reads as one
situation while being another, and it hides the only one anybody can act on.

So five states, and the fifth exists because the first four assume a status line that R1–R4 predate:

===============  ================================  ===================================
State            Means                             Waiting on
===============  ================================  ===================================
``ANSWERED``     answer filed, status agrees       nobody
``UNDISPATCHED`` declared NOT DISPATCHED, no       **Paul** — it has never been sent
                 answer
``IN_FLIGHT``    declared dispatched, no answer    the researcher
``STALE_STATUS`` answer filed, but the prompt      **the record** — it is contradicting
                 still declares NOT DISPATCHED     itself
``UNKNOWN``      no status line and no answer      nobody knows, which is the finding
===============  ================================  ===================================

**What this deliberately does NOT gate.** It does not assert that zero prompts are undispatched.
Writing a prompt ahead of sending it is the intended workflow — R8, R9 and R10 were all written in
one session on purpose. A gate that failed on queue depth would force you to either dispatch or
delete, and both are worse than knowing. Queue depth is **reported**; only self-contradiction
(``STALE_STATUS``) is **gated**, because that is a document disagreeing with the disk and one of
them is wrong.

**What it cannot catch.** Whether a dispatched prompt was actually pasted anywhere, whether an
answer is any good, or a prompt that declares itself dispatched while sitting in a drafts folder.
It reads two facts — a status line and the presence of a file — and nothing subtler.
"""

from __future__ import annotations

import pathlib
import re
from typing import Dict, List

from factory.synthesis import RESEARCH, filed

#: ``R8-data-engineering-agent-factory.md`` -> ``R8``. README and SUPERSEDED drafts are not prompts.
#:
#: No "not an answer" lookahead here on purpose. :func:`prompts` globs the top level of
#: ``docs/research`` only, and answers live one directory down, so they never collide — whereas a
#: ``(?!answer)`` guard would silently swallow a legitimate prompt called
#: ``R11-answerability-guards.md``. Caught by tests/test_dispatch.py before it ever bit.
_PROMPT = re.compile(r"^(R\d+)-", re.I)

#: ``**Status: NOT DISPATCHED.**`` — the declaration a prompt makes about itself.
_STATUS = re.compile(r"\*\*Status:\s*([^*]+?)\s*\*\*", re.I)

#: Only this phrasing counts as "not sent". Anything else is a claim that it was.
_NOT_SENT = re.compile(r"NOT\s+DISPATCHED", re.I)

ANSWERED = "ANSWERED"
UNDISPATCHED = "UNDISPATCHED"
IN_FLIGHT = "IN_FLIGHT"
STALE_STATUS = "STALE_STATUS"
UNKNOWN = "UNKNOWN"


def prompts(research: pathlib.Path | None = None) -> Dict[str, pathlib.Path]:
    """Research id -> its prompt file.

    Superseded drafts are excluded: ``R3-optimizer-sandbox-SUPERSEDED.md`` is not a live prompt
    and counting it would make R3 look like it had two.
    """
    root = research or RESEARCH
    out: Dict[str, pathlib.Path] = {}
    if not root.is_dir():
        return out
    for f in sorted(root.glob("R[0-9]*.md")):
        if "SUPERSEDED" in f.stem.upper():
            continue
        # A generated evidence pack sits in this directory and matches this glob. Today the real
        # prompt wins only because `R13-architecture-…` sorts before `R13-evidence-pack` and this
        # loop uses setdefault — rename either file and the pack becomes the prompt, silently.
        if f.stem.upper().endswith("-EVIDENCE-PACK"):
            continue
        m = _PROMPT.match(f.name)
        if m:
            out.setdefault(m.group(1).upper(), f)
    return out


def declared(path: pathlib.Path) -> str | None:
    """The status a prompt declares about itself, or None when it never says.

    None is not a failure — R1–R4 were written before the convention existed. It is the reason
    :data:`UNKNOWN` has to be its own state rather than being folded into IN_FLIGHT.
    """
    try:
        head = path.read_text(encoding="utf-8", errors="replace")[:2000]
    except OSError:
        return None
    m = _STATUS.search(head)
    return m.group(1).strip() if m else None


def state(
    research: pathlib.Path | None = None,
    answers: pathlib.Path | None = None,
) -> Dict[str, str]:
    """Research id -> one of the five states. The whole module, minus presentation."""
    have = _answered_ids(answers)
    out: Dict[str, str] = {}
    for rid, path in prompts(research).items():
        said = declared(path)
        not_sent = bool(said and _NOT_SENT.search(said))
        if rid in have:
            out[rid] = STALE_STATUS if not_sent else ANSWERED
        elif not_sent:
            out[rid] = UNDISPATCHED
        elif said:
            out[rid] = IN_FLIGHT
        else:
            out[rid] = UNKNOWN
    return out


def _answered_ids(answers: pathlib.Path | None) -> set[str]:
    if answers is None:
        return set(filed())
    ids: set[str] = set()
    if not answers.is_dir():
        return ids
    for f in sorted(answers.glob("R[0-9]*.md")):
        m = re.match(r"^(R\d+)-answer", f.name, re.I)
        if m:
            ids.add(m.group(1).upper())
    return ids


def undispatched(
    research: pathlib.Path | None = None,
    answers: pathlib.Path | None = None,
) -> List[str]:
    """Written, never sent. Waiting on a human — this is the actionable queue."""
    return _in(state(research, answers), UNDISPATCHED)


def stale_status(
    research: pathlib.Path | None = None,
    answers: pathlib.Path | None = None,
) -> List[str]:
    """Answer filed, prompt still says NOT DISPATCHED. The record contradicts the disk.

    Empty is the healthy state, and this is the only condition worth failing a test over.
    """
    return _in(state(research, answers), STALE_STATUS)


def _in(mapping: Dict[str, str], want: str) -> List[str]:
    return sorted((k for k, v in mapping.items() if v == want), key=_num)


def _num(rid: str) -> int:
    return int(rid[1:])


def render(
    research: pathlib.Path | None = None,
    answers: pathlib.Path | None = None,
) -> str:
    """One compact block — what is waiting, and on whom."""
    st = state(research, answers)
    if not st:
        return "No research prompts found."
    lines = ["Research dispatch state", ""]
    for rid in sorted(st, key=_num):
        lines.append(f"  {rid:<4} {st[rid]}")
    waiting = undispatched(research, answers)
    stale = stale_status(research, answers)
    lines.append("")
    if waiting:
        lines.append(f"⚠ {len(waiting)} written and never sent: {', '.join(waiting)} — waiting on Paul.")
    else:
        lines.append("Nothing written-and-unsent.")
    if stale:
        lines.append(
            f"⛔ {len(stale)} contradict themselves: {', '.join(stale)} — an answer is filed but the "
            "prompt still declares NOT DISPATCHED."
        )
    return "\n".join(lines)


def main() -> None:
    print(render())


if __name__ == "__main__":  # pragma: no cover
    main()


#: A run-log row: ``| 1 | 2026-08-23 | Answer filed. |``
_ROW = re.compile(r"^\|\s*([0-9]+|—|-)\s*\|\s*([^|]*?)\s*\|\s*(.*?)\s*\|\s*$", re.M)


def run_log(path: pathlib.Path) -> List[Dict[str, str]]:
    """The dispatch rows a prompt records about itself.

    The record `dispatch.state()` reads is a *declaration*; this is a *history*. The module's own
    docstring admits it cannot see whether a prompt was ever pasted anywhere, and on 2026-08-23
    that gap bit twice: nobody could say which prompts had been uploaded, and R14 was recorded as
    dispatched on the strength of "running 13 and 14 now" — an intention, not an observation — when
    only R13 went.

    ⚠ So a row here is only as good as the moment it was written. **Write it when the paste is
    confirmed, never when it is announced.** A row that says a send happened when it did not is
    worse than no row, because it reads as evidence.
    """
    try:
        head = path.read_text(encoding="utf-8", errors="replace")[:4000]
    except OSError:
        return []
    if "## Run log" not in head:
        return []
    block = head.split("## Run log", 1)[1]
    out = []
    for run, when, outcome in _ROW.findall(block):
        if run.lower() in ("run", "---", "") or set(when) <= {"-"}:
            continue                       # the header row and the markdown rule
        out.append({"run": run, "dispatched": when, "outcome": outcome})
    return out


#: Why each state needs a human, in the order a human should act on it. Ordering is a JUDGEMENT and
#: is written down here rather than implied, so it can be argued with instead of guessed at.
_ACTION = {
    STALE_STATUS: (0, "reconcile the record",
                   "the document contradicts the disk and one of them is wrong"),
    UNDISPATCHED: (2, "send it", "written and waiting on you — nothing is working on it"),
    UNKNOWN: (3, "declare a status", "no status line, so no instrument can place it"),
    IN_FLIGHT: (4, "wait", "a researcher has it"),
    ANSWERED: (5, "nothing", "filed and reconciled"),
}


def order(research=None, answers=None, syn_unreconciled=None) -> List[Dict[str, str]]:
    """What to do next, ranked, each with the reason — highest priority first.

    Reconciling beats dispatching on purpose. An unread answer is work already paid for and not yet
    banked; sending another prompt while one sits unreconciled spends money to widen a backlog.
    """
    if syn_unreconciled is None:
        try:
            from .synthesis import unreconciled
            syn_unreconciled = set(unreconciled())
        except Exception:                                          # noqa: BLE001
            syn_unreconciled = set()
    else:
        syn_unreconciled = set(syn_unreconciled)

    rows = []
    for rid, st in state(research, answers).items():
        # ⚠ A prompt can be ANSWERED and still be waiting on Paul: R13 was answered once, then
        # rewritten for a run 2 that has not been sent. None of the five states expresses that —
        # they describe a prompt, and this is a fact about its NEXT run — so the run log is asked.
        # Without this the board says "nothing to do" while a rewritten prompt sits unsent.
        pending = any((r.get("dispatched") or "").strip().lower() in ("pending", "tbd", "")
                      for r in run_log(prompts(research).get(rid, pathlib.Path("/nonexistent"))))
        if rid in syn_unreconciled:
            rank, action, why = 1, "reconcile it into SYNTHESIS", (
                "answered, and filed after the synthesis was last written — the answer is paid for "
                "and not yet banked")
        elif pending and st == ANSWERED:
            rank, action, why = 2, "send the next run", (
                "answered once, and a further run is written and waiting on you — the run log says "
                "pending")
        else:
            rank, action, why = _ACTION.get(st, (6, "?", ""))
        rows.append({"id": rid, "state": st, "rank": rank, "action": action, "why": why,
                     "runs": len(run_log(prompts(research).get(rid, pathlib.Path("/nonexistent"))))})
    return sorted(rows, key=lambda r: (r["rank"], int(r["id"][1:])))
