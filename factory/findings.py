"""Read `docs/findings.md` as data, so a lane can be shown only the corrections that hit it.

The ledger already required every entry to name what it **AFFECTS**. Prose is the right format for
a human reading the whole file, and the wrong format for a session about to start one lane — it
has to read six entries to discover that one of them matters. So AFFECTS is parsed, matched
against real lane and gate ids, and surfaced per lane.

**Matching is by declared id, not by keyword.** An entry that affects the control-plane lane says
so by naming a lane id or a gate id that belongs to it. Fuzzy text matching would quietly attach
findings to lanes that merely share a word, and a false attachment is worse than none: it trains
people to skim the section.

An entry missing any of the four mandatory fields is not a finding, and `malformed()` names it.
`tests/test_findings.py` fails the suite on one, which is what stops the ledger degrading into a
notes file.
"""
from __future__ import annotations

import pathlib
import re
from dataclasses import dataclass, field
from typing import Dict, List

LEDGER = pathlib.Path(__file__).resolve().parent.parent / "docs" / "findings.md"

REQUIRED = ("BELIEVED", "ACTUALLY", "MEASURED BY", "AFFECTS")
_HEADING = re.compile(r"^###\s+(F\d+)\s*[—-]\s*(.+?)\s*$", re.M)
_NOTHING = re.compile(r"NOTHING TO REPORT", re.I)


@dataclass(frozen=True)
class Finding:
    id: str
    title: str
    body: str
    fields: Dict[str, str] = field(default_factory=dict)

    @property
    def missing(self) -> List[str]:
        return [f for f in REQUIRED if f not in self.fields]

    @property
    def affects(self) -> str:
        return self.fields.get("AFFECTS", "")


def _split(text: str) -> List[Finding]:
    out: List[Finding] = []
    marks = list(_HEADING.finditer(text))
    for i, m in enumerate(marks):
        body = text[m.end():marks[i + 1].start() if i + 1 < len(marks) else len(text)]
        fields: Dict[str, str] = {}
        for name in REQUIRED:
            # The ledger writes fields as **NAME** — value, inside a bullet.
            fm = re.search(rf"\*\*{re.escape(name)}\*\*\s*[—-]?\s*(.+?)(?=\n\s*-\s+\*\*|\Z)",
                           body, re.S)
            if fm:
                fields[name] = " ".join(fm.group(1).split())
        out.append(Finding(m.group(1), m.group(2), body, fields))
    return out


def load(path: pathlib.Path | None = None) -> List[Finding]:
    p = path or LEDGER
    if not p.is_file():
        return []
    return _split(p.read_text(encoding="utf-8"))


def malformed(path: pathlib.Path | None = None) -> Dict[str, List[str]]:
    """Finding id -> the mandatory fields it is missing. Empty dict is the healthy state."""
    return {f.id: f.missing for f in load(path) if f.missing}


def nothing_to_report(path: pathlib.Path | None = None) -> int:
    """How many lanes closed having checked and found nothing. Counted because it is the
    difference between silence-as-measurement and silence-as-nobody-looked."""
    p = path or LEDGER
    return len(_NOTHING.findall(p.read_text(encoding="utf-8"))) if p.is_file() else 0


def by_lane(path: pathlib.Path | None = None) -> Dict[str, List[Finding]]:
    """lane id -> findings whose AFFECTS names that lane, or a gate belonging to it."""
    from .lanes import LANES
    out: Dict[str, List[Finding]] = {l.id: [] for l in LANES}
    for f in load(path):
        text = f.affects.lower()
        # "affects every lane" is the commonest important case and the id/gate match misses it
        # entirely — which left F5, the one about instruments returning false results, attached
        # to nothing. A finding that matters everywhere must not be shown nowhere.
        everywhere = bool(re.search(r"\b(every|all)\s+lanes?\b", text))
        for lane in LANES:
            hit = everywhere or lane.id.lower() in text or any(
                re.search(rf"\b{re.escape(g)}\b", text) for g in lane.gates)
            if hit:
                out[lane.id].append(f)
    return out


def unattached(path: pathlib.Path | None = None) -> List[str]:
    """Findings no lane picks up.

    Not an error — "affects every lane" is a real and common answer, and this session's F5 is
    exactly that. But a finding nobody will be shown is worth being able to see, because the
    likeliest cause is an AFFECTS field written in prose that names nothing checkable.
    """
    attached = {f.id for fs in by_lane(path).values() for f in fs}
    return [f.id for f in load(path) if f.id not in attached]
