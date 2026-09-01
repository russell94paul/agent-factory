"""The prose boundary — machine-validated, because structured code depends on it.

The forensic reconstruction for a delivery is long-form prose that a human wrote and reviewed. The
structured case-study record cites *into* it. That is a dependency of code on prose, and the gate
decision of 2026-09-01 states the invariant it has to satisfy:

    If structured code depends on prose structure, the prose boundary must be machine-validated.

⛔ **This is not a Markdown parser and must never become one.** It recognises exactly one construct:

    <!-- anchor: some-stable-id -->

on a line of its own. Nothing else in the file is read, so the prose can be re-edited, re-worded,
re-headed and re-ordered without breaking anything, and the only way to break a citation is to
delete the anchor a citation names — which is precisely the event that should be loud.

⭐ **Why an explicit marker rather than slugified heading text.** Heading text is editorial; it gets
reworded, and a reworded heading would silently break every reference to it. Worse, two headings can
slugify to the same anchor and the collision is invisible. An explicit id is a contract the author
declared on purpose. This is the same reasoning that made ``ENTITY_CODE`` a key rather than a
``COMPANY_NAME`` string comparison in the delivery this case study is about.

The failure mode this module exists to prevent is named in the fixture it validates: ``FIELDS.md``
listed five fields as "current" against a source that no longer had them, because a document
transcribed from another document drifted from it with nothing checking. A dangling anchor is that
same defect, and here it raises.
"""
from __future__ import annotations

import pathlib
import re
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Sequence, Tuple

from . import assertions as _assertions

#: The one construct this module recognises. Anchored to line start so a mention of the syntax
#: inside a code fence (as in this docstring) is not itself an anchor.
_ANCHOR = re.compile(r"^<!--\s*anchor:\s*([A-Za-z0-9][A-Za-z0-9._-]*)\s*-->\s*$")


class SourceError(ValueError):
    """The prose boundary is broken. Always loud — never a partial, authoritative-looking artifact."""


@dataclass
class Source:
    """One validated prose file and the anchors it declares."""
    path: str
    anchors: Dict[str, int] = field(default_factory=dict)
    line_count: int = 0
    sha256: str = ""

    def has(self, anchor: str) -> bool:
        return anchor in self.anchors


def _digest(text: str) -> str:
    import hashlib
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def read(path: pathlib.Path) -> Source:
    """Read one prose file and index its anchors.

    Raises on a duplicate anchor. A duplicate is worse than a missing one: a citation would resolve
    to whichever came first, and the artifact would look correct while pointing somewhere nobody
    intended.
    """
    path = pathlib.Path(path)
    if not path.exists():
        raise SourceError(f"forensic source {path} does not exist")
    text = path.read_text(encoding="utf-8")
    lines = text.split("\n")
    found: Dict[str, int] = {}
    dupes: List[str] = []
    for n, line in enumerate(lines, 1):
        m = _ANCHOR.match(line.strip())
        if not m:
            continue
        key = m.group(1)
        if key in found:
            dupes.append(f"{key!r} at lines {found[key]} and {n}")
        else:
            found[key] = n
    if dupes:
        raise SourceError(
            f"{path}: duplicate anchor(s) — {'; '.join(dupes)}. An anchor must occur exactly once; "
            "a citation to a duplicated anchor resolves to whichever came first and looks correct.")
    return Source(path=str(path).replace("\\", "/"), anchors=found,
                  line_count=len(lines), sha256=_digest(text))


@dataclass
class RefReport:
    """The result of checking a set of references against the filesystem and the prose anchors."""
    checked: int = 0
    resolved: List[str] = field(default_factory=list)
    missing_file: List[str] = field(default_factory=list)
    missing_anchor: List[str] = field(default_factory=list)
    malformed: List[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not (self.missing_file or self.missing_anchor or self.malformed)

    def problems(self) -> List[str]:
        out = []
        for r in self.malformed:
            out.append(f"malformed reference: {r}")
        for r in self.missing_file:
            out.append(f"file does not exist: {r}")
        for r in self.missing_anchor:
            out.append(f"anchor not declared in its file: {r}")
        return out


def check_refs(refs: Iterable[str], root: pathlib.Path,
               sources: Dict[str, Source] | None = None) -> RefReport:
    """Resolve every reference. ``path`` must exist; ``path#anchor`` must also declare the anchor.

    ⚠ An anchor pointing into a file with **no** anchors at all is reported as a missing anchor, not
    excused. A prose file that has never been anchored cannot support citations into it, and
    treating "no anchors declared" as "anchors not required" is how the boundary would quietly stop
    being checked.
    """
    root = pathlib.Path(root)
    sources = sources if sources is not None else {}
    rep = RefReport()
    for ref in refs:
        if not ref:
            continue
        rep.checked += 1
        try:
            rel, anchor = _assertions.split_ref(ref)
        except _assertions.AssertionError_:
            rep.malformed.append(ref)
            continue
        target = root / rel
        if not target.exists():
            rep.missing_file.append(ref)
            continue
        if anchor is None:
            rep.resolved.append(ref)
            continue
        key = str(rel).replace("\\", "/")
        if key not in sources:
            try:
                sources[key] = read(target)
            except SourceError:
                rep.missing_anchor.append(ref)
                continue
        if sources[key].has(anchor):
            rep.resolved.append(ref)
        else:
            rep.missing_anchor.append(ref)
    return rep


def require(refs: Iterable[str], root: pathlib.Path,
            sources: Dict[str, Source] | None = None, what: str = "reference") -> RefReport:
    """:func:`check_refs`, but raise on any problem. Use where a dangling ref is a build failure."""
    rep = check_refs(refs, root, sources)
    if not rep.ok:
        bullets = "\n  - ".join(rep.problems())
        raise SourceError(
            f"{len(rep.problems())} broken {what}(s):\n  - {bullets}\n"
            "Compilation stops here rather than emitting an artifact whose citations point at "
            "nothing — a partial artifact that looks authoritative is worse than no artifact.")
    return rep


def unique_ids(rows: Sequence[dict], where: str, key: str = "id") -> List[str]:
    """Return the ids in `rows`, raising if any is missing, blank or duplicated."""
    seen: Dict[str, int] = {}
    out: List[str] = []
    for i, row in enumerate(rows):
        rid = str((row or {}).get(key, "")).strip()
        if not rid:
            raise SourceError(f"{where}[{i}] has no {key}. Every record needs a stable identifier.")
        if rid in seen:
            raise SourceError(
                f"{where}: duplicate {key} {rid!r} at positions {seen[rid]} and {i}. "
                "Identifiers are how records cross-reference; a duplicate makes a reference "
                "ambiguous and the ambiguity is invisible in the rendered page.")
        seen[rid] = i
        out.append(rid)
    return out


def require_refs_exist(needed: Iterable[Tuple[str, str]], known: Iterable[str],
                       where: str) -> None:
    """Every ``(field, target_id)`` must name something in `known`.

    This is the "references to issue IDs / findings do not silently point to missing objects" rule.
    A scene naming a timeline step that was renamed would otherwise render an empty panel.
    """
    known_set = set(known)
    bad = [f"{fld} -> {tid!r}" for fld, tid in needed if tid and tid not in known_set]
    if bad:
        raise SourceError(
            f"{where}: {len(bad)} cross-reference(s) point at records that do not exist:\n  - "
            + "\n  - ".join(bad))
