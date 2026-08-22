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
#: One file per finding. A single shared ledger cannot survive parallel lanes: on 2026-08-22
#: three isolated worktrees each read F10 as the last id and appended their own F11 and F12,
#: correctly and incompatibly, because none could observe the others. Separate paths remove the
#: shared write — git never has to reconcile two writers in one place.
FRAGMENTS = LEDGER.parent / "findings.d"

REQUIRED = ("BELIEVED", "ACTUALLY", "MEASURED BY", "AFFECTS")
#: Optional on every entry, but see `Finding.missing`: a finding that declares itself a design
#: consequence must say what changes, or it is an observation wearing a decision's clothes.
OPTIONAL = ("KIND", "CHANGES", "STATUS")
#: CORRECTION   a premise was wrong; fix it and move on
#: INSTRUMENT   a tool lied, or could not see — changes what a measurement is worth
#: DESIGN       the system should be built differently
#: AGENT-DESIGN the agents/lanes/harness should work differently
#: PROCESS      the way we work should change
KINDS = ("CORRECTION", "INSTRUMENT", "DESIGN", "AGENT-DESIGN", "PROCESS")
#: A DESIGN finding with no status is an insight nobody ever decided about. Silence has to mean
#: decided, the same way NOTHING TO REPORT has to mean checked.
STATUSES = ("OPEN", "ADOPTED", "REJECTED", "SUPERSEDED")
DESIGN_KINDS = ("DESIGN", "AGENT-DESIGN")
_HEADING = re.compile(r"^###\s+(F\d+)\s*[—-]\s*(.+?)\s*$", re.M)
_NOTHING = re.compile(r"NOTHING TO REPORT", re.I)


@dataclass(frozen=True)
class Finding:
    id: str
    title: str
    body: str
    fields: Dict[str, str] = field(default_factory=dict)

    @property
    def kind(self) -> str:
        return self.fields.get("KIND", "").strip().upper()

    @property
    def status(self) -> str:
        return self.fields.get("STATUS", "").strip().upper()

    @property
    def missing(self) -> List[str]:
        out = [f for f in REQUIRED if f not in self.fields]
        # Conditional, not absolute. Most findings are corrections and need no design field at
        # all; one that claims a design consequence and then does not name it is the failure this
        # is for — the insight gets filed, admired, and never built.
        if self.kind in DESIGN_KINDS and "CHANGES" not in self.fields:
            out.append("CHANGES")
        if self.kind and self.kind not in KINDS:
            out.append(f"KIND={self.kind} not one of {list(KINDS)}")
        if self.status and self.status not in STATUSES:
            out.append(f"STATUS={self.status} not one of {list(STATUSES)}")
        return out

    @property
    def affects(self) -> str:
        return self.fields.get("AFFECTS", "")


def _split(text: str) -> List[Finding]:
    out: List[Finding] = []
    marks = list(_HEADING.finditer(text))
    for i, m in enumerate(marks):
        body = text[m.end():marks[i + 1].start() if i + 1 < len(marks) else len(text)]
        fields: Dict[str, str] = {}
        for name in REQUIRED + OPTIONAL:
            # The ledger writes fields as **NAME** — value, inside a bullet.
            fm = re.search(rf"\*\*{re.escape(name)}\*\*\s*[—-]?\s*(.+?)(?=\n\s*-\s+\*\*|\Z)",
                           body, re.S)
            if fm:
                fields[name] = " ".join(fm.group(1).split())
        out.append(Finding(m.group(1), m.group(2), body, fields))
    return out


def _sources(path: pathlib.Path | None) -> List[pathlib.Path]:
    """An explicit path is read alone — a caller naming a file means that file, and the tests rely
    on it. The default unions the ledger with every fragment, so entries written the old way still
    count and nothing already committed on a lane branch breaks."""
    if path is not None:
        return [path] if path.is_file() else []
    out = [LEDGER] if LEDGER.is_file() else []
    if FRAGMENTS.is_dir():
        out += sorted(q for q in FRAGMENTS.glob("*.md") if q.name != "README.md")
    return out


def _key(f: "Finding"):
    m = re.match(r"F(\d+)", f.id)
    return (int(m.group(1)) if m else 10 ** 6, f.id)


def load(path: pathlib.Path | None = None) -> List[Finding]:
    seen, out = set(), []
    for p in _sources(path):
        for f in _split(p.read_text(encoding="utf-8")):
            # Same id in both places is a half-finished migration, not two findings. Keep the
            # first rather than reporting a duplicate as malformed.
            if f.id in seen:
                continue
            seen.add(f.id)
            out.append(f)
    return sorted(out, key=_key)


def by_kind(path: pathlib.Path | None = None) -> Dict[str, List[Finding]]:
    """kind -> findings. Unclassified entries land under '' and are not an error: the four
    mandatory fields are the discipline, KIND is the refinement."""
    out: Dict[str, List[Finding]] = {}
    for f in load(path):
        out.setdefault(f.kind, []).append(f)
    return out


def design_debt(path: pathlib.Path | None = None) -> List[Finding]:
    """Findings that say the system or the agents should be built differently, and that nobody
    has decided about yet. This is the list that should shrink, and the reason KIND exists: a
    correction is spent once it is read, a design consequence is not spent until it is built or
    deliberately refused."""
    return [f for f in load(path)
            if f.kind in DESIGN_KINDS and f.status in ("", "OPEN")]


def malformed(path: pathlib.Path | None = None) -> Dict[str, List[str]]:
    """Finding id -> the mandatory fields it is missing. Empty dict is the healthy state."""
    return {f.id: f.missing for f in load(path) if f.missing}


def nothing_to_report(path: pathlib.Path | None = None) -> int:
    """How many lanes closed having checked and found nothing. Counted because it is the
    difference between silence-as-measurement and silence-as-nobody-looked."""
    return sum(len(_NOTHING.findall(p.read_text(encoding="utf-8")))
               for p in _sources(path))


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
