"""The crew — GTA-mode personas and vocabulary, in ONE module both views read.

Two rules shaped every line of this file.

**Ids never change.** A lane is `control-plane` in the data forever: branches are `lane/<id>`,
claims key on the id, worktrees are named for it, and `docs/findings.d` routes a correction to a
lane by matching its id inside AFFECTS. Renaming lanes would silently unroute every finding — the
one thing the ledger exists to prevent. So this is a **presentation layer keyed by id**, and the
id is the join.

**Handles are original, and they encode the job.** `docs/specs/gta-mission-narrator-prompt.md` §3
and §21 forbid reproducing GTA dialogue, characters, logos or assets — inspired-by, not
derived-from. Every handle below is invented, and each one says what its lane actually does:
Governor caps a runaway, Sparks wires instruments, Doorman refuses entry. A nickname that encodes
nothing would be decoration, which this repo refuses on figures and refuses here too.
"""
from __future__ import annotations

from typing import Dict, List, Optional

MODES = ("instrument", "gta")

#: lane id -> (handle, what they actually do, one line of character)
CREW: Dict[str, Dict[str, str]] = {
    "control-plane": {
        "handle": "Governor",
        "role": "caps the throttle — attempt caps, concurrency, the reaper",
        "line": "Nothing runs forever on my watch. One stage took a whole region once.",
    },
    "certify": {
        "handle": "Sparks",
        "role": "wires the instruments — probes that actually reach something",
        "line": "A gauge with no wire behind it is a picture of a gauge.",
    },
    "judgement": {
        "handle": "Doorman",
        "role": "decides who gets in — the gates, and making them able to refuse",
        "line": "Twenty-two times asked, twenty-two times waved through. That changes.",
    },
    "artifact": {
        "handle": "Chrome",
        "role": "makes the readout right — the published surface and its detectors",
        "line": "It rendered fine for you. It rendered blank for everyone else.",
    },
    "grain": {
        "handle": "Grit",
        "role": "settles the fine detail — keys, grain, the things everything else assumes",
        "line": "You built the whole world on a primary key nobody checked.",
    },
}

#: Roles that are not lanes but appear in the HUD.
FIGURES: Dict[str, Dict[str, str]] = {
    "evaluator": {"handle": "The Fixer",
                  "role": "certifies, and is not the agent — its own identity, its own credentials",
                  "line": "If you graded your own work, you did not grade anything."},
    "reviewer":  {"handle": "The Lookout",
                  "role": "reads your diff before you close",
                  "line": "Found six in your own commit. Three were yours."},
    "conductor": {"handle": "Safehouse",
                  "role": "where the human works — board, radio, payday",
                  "line": ""},
}

#: instrument term -> gta term. The DOMAIN is translatable.
VOCAB: Dict[str, str] = {
    "lane": "crew",
    "agent": "crew member",
    "session": "crew member",
    "task": "job",
    "gate": "checkpoint",
    "findings": "intel",
    "finding": "intel",
    "claim": "turf",
    "message": "radio",
    "bus": "radio",
    "finish": "payday",
    "worktree": "garage bay",
    "board": "stats",
    "readiness": "stats",
    "evaluator": "the fixer",
    "reviewer": "the lookout",
    "conductor": "safehouse",
    "orphaned": "ghost",
    "tokens": "fuel",
    "budget exceeded": "out of gas",
}

#: Verdicts are renamed but stay DISTINCT — "we did not measure" must never read as "it broke".
VERDICTS: Dict[str, str] = {
    "PASS": "clear",
    "FAIL": "heat",
    "UNMEASURABLE": "no signal",
    "NOT_RUN": "not attempted",
}

#: ⛔ NOT translatable, in any mode. The skin may rename the domain; it may never rename the
#: epistemics. An ASSUMED value stays ASSUMED on a neon HUD, or the skin launders an estimate into
#: a fact — which is the defect this whole estate is built to refuse.
FROZEN = ("MEASURED", "DERIVED", "ASSUMED", "PROXY")


class SkinError(Exception):
    """Refused: the skin was asked to do something that would change a claim."""


def persona(lane_id: str) -> Optional[Dict[str, str]]:
    return CREW.get(lane_id) or FIGURES.get(lane_id)


def name(lane_id: str, mode: str = "instrument") -> str:
    """What to call this lane on screen. Falls back to the id — an unknown lane must still
    render, and rendering it as a blank would hide a lane that exists."""
    if mode != "gta":
        return lane_id
    p = persona(lane_id)
    return p["handle"] if p else lane_id


def term(word: str, mode: str = "instrument") -> str:
    """Translate one domain word. Refuses on an epistemic label rather than returning it
    unchanged: a silent no-op would let a caller believe translation happened."""
    if word in FROZEN:
        raise SkinError(
            f"{word!r} is an epistemic label and is never translated — the skin may rename the "
            "domain, never the basis of a number")
    if mode != "gta":
        return word
    return VOCAB.get(word, word)


def verdict(v: str, mode: str = "instrument") -> str:
    if mode != "gta":
        return v
    return VERDICTS.get(v, v)


def heat(failing: int, total: int) -> Dict[str, object]:
    """Failing gates as a 0-5 wanted level.

    ⚠ Lossy on purpose, so it comes with the means to undo the compression: `stars` is the glance,
    `detail` is the sentence, and callers MUST offer the real gate list behind it. A wanted level
    nobody can drill into is decoration, and this repo does not ship decoration as a control.
    """
    if total <= 0:
        raise SkinError("cannot compute heat with no gates — that is no signal, not zero heat")
    frac = failing / total
    stars = min(5, int(frac * 5) + (1 if failing and frac * 5 < 1 else 0))
    return {"stars": stars, "of": 5, "failing": failing, "total": total,
            "detail": f"{failing} of {total} checkpoints failing",
            "expandable": True}


def roster(mode: str = "instrument") -> List[Dict[str, str]]:
    """Every lane, named for the mode. Ordered as CREW is declared."""
    return [{"id": k, "name": name(k, mode), **v} for k, v in CREW.items()]
