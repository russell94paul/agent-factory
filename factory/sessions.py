"""Session cards — a handoff somebody can pick up, and the order sessions must run in.

    python -m factory.sessions          # the running order, and why it is what it is
    python -m factory.sessions --cards  # what has been handed off so far

A handoff that lives only in a terminal has not been handed anywhere. `factory.handoff`
already *generates* one from measured state; this posts it as a **card** that outlives the
session, carries a title and a description so a reader knows what it is about without
opening it, and says what must run before it.

## Three different constraints, deliberately not merged

Running order is not one relation. Collapsing them into a single "depends" list is how a
board ends up asserting an order it cannot justify.

| relation | meaning | derived from | basis |
|---|---|---|---|
| `after` | this session's gates depend on gates another session owns | `board.DEPENDS` | MEASURED — authored design knowledge, validated on import |
| `blocked_by_gate` | it depends on a gate **no session owns**, so no ordering can fix it | `board.DEPENDS` | MEASURED |
| `conflicts` | two sessions edit the same file, so they cannot run *concurrently* | `lanes.Lane.touches` | ⚠ ASSUMED — `touches` is a judgement, not a probe (lanes.py says so itself) |

⭐ **`conflicts` is not ordering.** It says "not at the same time", not "this one first".
Either order is fine; both at once is a merge conflict. They are reported separately because
a reader who treats a conflict as a dependency will wait for something that was never going
to unblock them.

## ⛔ What this currently finds, and why the honest answer is "nothing"

Projecting `DEPENDS` onto lanes today yields **no lane-to-lane edge at all**. Every authored
dependency is either *inside* one lane (`truthful`←`from-history`, both control-plane;
`ceiling`←`cost` and `refuses`←`checks`, both judgement) or points at a gate no lane owns
(`certified`←`isolated`). So the sessions are **unordered by dependency**, and this module
says so rather than rendering declaration order as if it meant something.

That is a real statement about the estate, not a gap in the projection: five lanes grouped by
file locality do not inherit the gate graph's shape. As `DEPENDS` grows the edges will appear
here without anything being re-typed — which is the point of deriving it.

The constraints that *do* exist today are the other two columns, and one of them was not
written down anywhere before this module computed it.
"""
from __future__ import annotations

import dataclasses
import datetime as _dt
import json
import pathlib
import re
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set

from .board import DEPENDS
from .lanes import LANES
from .readiness import GATES

FACTORY = pathlib.Path(__file__).resolve().parent.parent
CARDS = FACTORY / ".data" / "cards.jsonl"


# --------------------------------------------------------------------------- derivation


def gate_owner() -> Dict[str, str]:
    """gate id -> the session that owns it. A gate in two lanes would be a bug in `lanes`."""
    out: Dict[str, str] = {}
    for lane in LANES:
        for g in lane.gates:
            if g in out:
                raise ValueError(
                    f"gate {g!r} is claimed by both {out[g]!r} and {lane.id!r}; a gate worked "
                    f"by two sessions has no owner and no running order")
            out[g] = lane.id
    return out


def unowned_gates() -> List[str]:
    """Gates no session owns. Not an error — several are handover or certification gates
    nobody grouped into a lane — but a dependency *on* one cannot be resolved by ordering."""
    owned = set(gate_owner())
    return sorted({g.id for g in GATES} - owned)


def after() -> Dict[str, List[str]]:
    """session -> sessions that must finish first, derived from `board.DEPENDS`.

    A session depends on another when one of its gates depends on a gate that session owns.
    Self-edges are dropped: a dependency inside one lane is sequencing *within* a session,
    which is the session's own business and not a running order between sessions.
    """
    owner = gate_owner()
    out: Dict[str, List[str]] = {}
    for lane in LANES:
        deps: Set[str] = set()
        for g in lane.gates:
            for d in DEPENDS.get(g, []):
                o = owner.get(d)
                if o and o != lane.id:
                    deps.add(o)
        out[lane.id] = sorted(deps)
    return out


def blocked_by_gate() -> Dict[str, List[str]]:
    """session -> gates it depends on that NO session owns.

    Distinct from `after` and much worse: no running order unblocks these, because nobody is
    scheduled to do them. `certify` depends on `isolated`, and `isolated` is in no lane.
    """
    owner = gate_owner()
    out: Dict[str, List[str]] = {}
    for lane in LANES:
        ext = {d for g in lane.gates for d in DEPENDS.get(g, []) if d not in owner}
        if ext:
            out[lane.id] = sorted(ext)
    return out


def _paths(lane) -> Set[str]:
    """The files a session edits, normalised to (repo, path) so two repos with a same-named
    file do not read as a collision.

    ⚠ Parsed from prose. `Lane.touches` is a human sentence — "orchestrator/pipelines.py gate
    definitions" — so the first token of each comma-separated clause is taken as the path and
    the rest as commentary. That is a heuristic over an ASSUMED field, and it is the weakest
    inference in this module; it is written down rather than hidden so it can be argued with.
    """
    out = set()
    for clause in re.split(r",", lane.touches or ""):
        clause = clause.strip()
        if not clause:
            continue
        out.add(f"{lane.repo}/{clause.split()[0]}")
    return out


def conflicts() -> Dict[str, Dict[str, List[str]]]:
    """session -> {other session: the shared paths}. Mutual exclusion, NOT ordering."""
    out: Dict[str, Dict[str, List[str]]] = {}
    for a in LANES:
        for b in LANES:
            if a.id >= b.id:
                continue
            shared = sorted(_paths(a) & _paths(b))
            if shared:
                out.setdefault(a.id, {})[b.id] = shared
                out.setdefault(b.id, {})[a.id] = shared
    return out


@dataclass(frozen=True)
class Session:
    id: str
    title: str
    description: str
    repo: str
    touches: str
    gates: List[str]
    after: List[str]
    blocked_by_gate: List[str]
    conflicts: Dict[str, List[str]]
    wave: int
    needs_paul: str = ""

    @property
    def headline(self) -> str:
        """One line a reader can scan on a board without opening the card."""
        return f"{self.id} — {self.title}"


def running_order() -> List[List[str]]:
    """Sessions grouped into waves: everything in wave N may run once wave N-1 is done.

    Raises on a cycle rather than picking an arbitrary order — an unsatisfiable ordering is a
    design error in `DEPENDS`, and silently linearising it hides that.

    ⚠ A wave says nothing about running its members *concurrently*. Two sessions in the same
    wave may still be in `conflicts`, which is a separate relation entirely.
    """
    deps = {k: set(v) for k, v in after().items()}
    waves: List[List[str]] = []
    placed: Set[str] = set()
    while len(placed) < len(deps):
        ready = sorted(s for s, d in deps.items() if s not in placed and d <= placed)
        if not ready:
            stuck = sorted(set(deps) - placed)
            raise ValueError(
                f"cycle in the session dependency graph among {stuck} — derived from "
                f"board.DEPENDS, so the cycle is there")
        waves.append(ready)
        placed |= set(ready)
    return waves


def sessions() -> List[Session]:
    """Every session, in running order, carrying its title, description and constraints."""
    a, b, c = after(), blocked_by_gate(), conflicts()
    wave_of = {s: i for i, w in enumerate(running_order()) for s in w}
    by_id = {l.id: l for l in LANES}
    out: List[Session] = []
    for sid in sorted(by_id, key=lambda s: (wave_of[s], s)):
        lane = by_id[sid]
        out.append(Session(
            id=lane.id,
            title=lane.title,
            description=lane.why,
            repo=lane.repo,
            touches=lane.touches,
            gates=list(lane.gates),
            after=a.get(sid, []),
            blocked_by_gate=b.get(sid, []),
            conflicts=c.get(sid, {}),
            wave=wave_of[sid],
            needs_paul=lane.needs_paul,
        ))
    return out


# --------------------------------------------------------------------------- cards


@dataclass(frozen=True)
class Card:
    """A posted handoff. Append-only: a card is a record of what was said at a moment, so it
    is never edited — a later handoff for the same session is a new card, and the pair is the
    history. Same rule as `factory.tasks`, for the same reason."""
    id: str
    kind: str                      # "lane" | "session"
    session: Optional[str]
    title: str
    description: str
    created: str
    body: str
    gates: List[str] = field(default_factory=list)
    after: List[str] = field(default_factory=list)
    conflicts: List[str] = field(default_factory=list)
    blocked_by_gate: List[str] = field(default_factory=list)
    author: str = ""

    def to_json(self) -> dict:
        return dataclasses.asdict(self)


class CardError(Exception):
    """A card was refused. The message says which field was missing and why it matters."""


def post(kind: str, body: str, session: Optional[str] = None, title: str = "",
         description: str = "", author: str = "") -> Card:
    """Post a handoff as a card. Returns it.

    **A card without a title and a description is refused.** That is the whole point of the
    surface: a board of untitled cards is a list of things somebody must open before they can
    decide whether to open it. For a session card both are derived from `lanes.py` when not
    supplied, so the common path needs neither typed — but an empty one is an error, not a
    default, because a silently-blank title reads as "no work here".
    """
    if kind not in ("lane", "session"):
        raise CardError(f"kind must be 'lane' or 'session', not {kind!r}")
    if not (body or "").strip():
        raise CardError("a card with no body is a heading; write the handoff first")

    if kind == "lane":
        if not session:
            raise CardError("a lane card must name its session")
        s = next((x for x in sessions() if x.id == session), None)
        if s is None:
            raise CardError(f"{session!r} is not a session; known: "
                            f"{', '.join(x.id for x in sessions())}")
        title = title or s.title
        description = description or s.description
        gates, aft, blocked = s.gates, s.after, s.blocked_by_gate
        conf = sorted(s.conflicts)
    else:
        gates, aft, blocked, conf = [], [], [], []

    if not (title or "").strip():
        raise CardError("a card needs a title — 'so people know what it's about' is the "
                        "surface's only job")
    if not (description or "").strip():
        raise CardError("a card needs a description. A title says what it is called; a "
                        "description says what it is about, and they are not the same")

    card = Card(id=uuid.uuid4().hex[:12], kind=kind, session=session,
                title=title.strip(), description=description.strip(),
                created=_dt.datetime.now().isoformat(timespec="microseconds"),
                body=body, gates=gates, after=aft, conflicts=conf,
                blocked_by_gate=blocked, author=author)
    CARDS.parent.mkdir(parents=True, exist_ok=True)
    with CARDS.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(card.to_json(), ensure_ascii=False) + "\n")
    return card


def cards(session: Optional[str] = None) -> List[Card]:
    """Every posted card, newest first. A corrupt line raises rather than being skipped —
    silently dropping a card is how a handoff stops existing without anyone being told."""
    if not CARDS.exists():
        return []
    out: List[Card] = []
    for n, line in enumerate(CARDS.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            out.append(Card(**json.loads(line)))
        except Exception as exc:                                   # noqa: BLE001
            raise CardError(f"{CARDS.name} line {n} will not load: {exc}") from exc
    if session:
        out = [(i, c) for i, c in enumerate(out) if c.session == session]
    else:
        out = list(enumerate(out))
    # Ordered by APPEND POSITION, with the timestamp only as a coarse key. Two cards posted
    # in the same second have identical `created` values, and a stable sort then returns them
    # oldest-first while claiming to be newest-first — measured, by a test that posted two
    # cards in one second. For an append-only log the write order IS the history, so it is
    # the authority here and the clock is the tiebreak, not the other way round.
    return [c for _, c in sorted(out, key=lambda p: (p[1].created, p[0]), reverse=True)]


# --------------------------------------------------------------------------- cli


def _report() -> str:
    L: List[str] = ["Session running order", ""]
    waves = running_order()
    a = after()
    if not any(a.values()):
        L += ["⛔ NO ORDERING CONSTRAINTS EXIST between sessions today.",
              "",
              "   Every edge in board.DEPENDS is either inside one session or points at a gate",
              "   no session owns, so the sessions below are printed in name order and that",
              "   order means nothing. This is measured, not a gap in the projection — do not",
              "   read the list as a sequence.", ""]
    for i, w in enumerate(waves):
        L.append(f"  wave {i}: {', '.join(w)}")
    L.append("")

    for s in sessions():
        L.append(f"── {s.headline}")
        L.append(f"   {s.description}")
        L.append(f"   repo {s.repo} · touches {s.touches}")
        L.append(f"   gates: {', '.join(s.gates)}")
        L.append(f"   after: {', '.join(s.after) if s.after else '(nothing)'}")
        if s.blocked_by_gate:
            L.append(f"   ⛔ blocked by gates NO session owns: {', '.join(s.blocked_by_gate)}")
        for other, paths in sorted(s.conflicts.items()):
            L.append(f"   ⚠ cannot run beside {other} — both edit {', '.join(paths)}")
        if s.needs_paul:
            L.append(f"   needs Paul: {s.needs_paul}")
        L.append("")

    orphan = unowned_gates()
    if orphan:
        L += [f"{len(orphan)} gate(s) belong to no session: {', '.join(orphan)}",
              "Nothing schedules them, so nothing will pick them up by running a lane.", ""]
    return "\n".join(L)


def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--cards", action="store_true", help="list posted handoff cards")
    args = ap.parse_args(argv)
    if args.cards:
        cs = cards()
        if not cs:
            print("No cards posted yet.")
            return 0
        for c in cs:
            print(f"{c.created}  [{c.kind}] {c.title}")
            print(f"    {c.description}")
            if c.after:
                print(f"    after: {', '.join(c.after)}")
            if c.conflicts:
                print(f"    ⚠ conflicts with: {', '.join(c.conflicts)}")
            print()
        return 0
    print(_report())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
