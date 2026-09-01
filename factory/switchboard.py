"""One projection over state that already exists, so the operator can stop visiting terminals.

⭐ **Nothing here is a new source of truth.** Every field is read, on every call, from something
that was already authoritative before this file existed:

    mission + DAG      TaskStore (.data/tasks.jsonl) + .data/missions/<id>.json
    live ownership     factory.claims  (O_EXCL locks, verified against the process table)
    sessions           factory.sessions.inventory()  (registry x jobs x process table)
    human questions    factory.sessions.blocked()    (JOBS, so a question outlives its process)
    upstream traffic   factory.bus.unread(reader)    (per-reader cursor, never advanced here)
    worktrees/HEAD     git worktree list --porcelain, then rev-parse per worktree

The projection is **derived and thrown away**. It is never written to disk, because a stored
projection is the thing the boot prompts kept becoming: correct when written, confidently wrong an
hour later.

## ⛔ Two premises inherited from the brief that measurement killed

**1. `session.brief()` cannot be a Switchboard data source.** The brief was named as "a likely
primary source". It calls `board.board()`, which calls `readiness.measure()`. Timed on this
checkout, 2026-09-01, one cold call each:

    board.board()      413.79 s      30 gates
    session.brief()    801.04 s      (board.board() plus the lane join)
    switchboard.state()  2.01 s      the projection this module returns

A live command page that pays 13 minutes per refresh is a page nobody opens — the exact failure
`docs/specs/control-room.md` §3 records against this tracker at ~19 s, at 42x less. So the mission
DAG is built from the TaskStore, which is a file read, and the gate board stays on the tabs that
already render it.

⚠ `brief()`'s critical path is `['cost', 'ceiling']` — **gate ids, not mission tasks.** It answers
a different question (which of five research lanes to take next) from the one the Switchboard is
for. Even at zero cost it would not have been the DAG the operator asked to see.

**2. `Task.blocked_by` is not the dependency graph.** `TaskStore.unblock()` *removes* the edge:

    D5  blocked_by = []        blocked events = ['D4']     unblock events = ['D4']

so a satisfied dependency leaves no trace in the current field, and a DAG built from `blocked_by`
shows every finished mission as a set of unrelated tasks. The edges are recovered from the
append-only `block` events instead — the store keeps them because it keeps everything. Measured
2026-09-01 against the live marketing-model mission.

## What this deliberately does NOT do

It does not schedule, dispatch, mutate a task, advance a bus cursor, or write a claim. It answers
questions. Slices that act (START SYNCED, dispatch) call the *existing* mechanisms and are wired in
`scripts/local_tracker.py`, where every other control on this estate already lives.
"""
from __future__ import annotations

import datetime as _dt
import json
import pathlib
import subprocess
from typing import Dict, List, Optional, Tuple

from . import bus as _bus
from . import claims as _claims
from . import repo as _repo
from . import sessions as _sessions
from .tasks import ABANDONED as _T_ABANDONED
from .tasks import CLAIMED as _T_CLAIMED
from .tasks import DONE as _T_DONE
from .tasks import TaskStore

# ---------------------------------------------------------------- the UI vocabulary
#
# Six words, and they are not interchangeable with the TaskStore's five. The store says what a
# task *is*; these say what the operator can *do about it now*, which is a join over the store,
# the claim table and the process table. Keeping one vocabulary for both would mean either the
# store grew a scheduling concept or the UI silently reinterpreted `open`.
DONE = "DONE"
RUNNING = "RUNNING"
READY = "READY"
READY_IN_PARALLEL = "READY_IN_PARALLEL"
BLOCKED = "BLOCKED"
NEEDS_HUMAN = "NEEDS_HUMAN"
ABANDONED = "ABANDONED"

#: ⚠ The critical path here is the longest **dependency** chain, not the longest **duration**
#: chain. The manifest does carry `estimate_minutes`, and its own `estimate_basis` says `ASSUMED`
#: — a number written before the run as the hypothesis the run tests. Ranking a path by assumed
#: minutes would publish an ETA derived from a guess, so the path is ordered by dependency depth
#: and this constant is rendered beside it.
CRITICAL_PATH_BASIS = "DEPENDENCY"

#: Session liveness classes that must never be offered a `--resume`.
#: `RUNNING-ATTACHED` and `RUNNING-ORPHANED` are alive — resuming spawns a second process against
#: one transcript, which is the divergent-duplicate failure recorded in control-room.md §5.
#: `UNKNOWN-INSTRUMENT-BLIND` means the process table could not be read at all, so "it exited"
#: is not a measurement, it is the absence of one.
_NOT_RESUMABLE = {_sessions.RUNNING_ATTACHED, _sessions.RUNNING_ORPHANED, _sessions.UNKNOWN}


def _now() -> str:
    return _dt.datetime.now().astimezone().isoformat(timespec="seconds")


def store_path() -> pathlib.Path:
    """The shared task store. `repo.data()` and not `__file__.parent.parent` — see repo.py."""
    return _repo.data() / "tasks.jsonl"


def missions_dir() -> pathlib.Path:
    return _repo.data() / "missions"


# ------------------------------------------------------------------------ missions


def manifests() -> List[dict]:
    """Every mission contract on disk, newest first. Empty list when there are none."""
    d = missions_dir()
    if not d.is_dir():
        return []
    out = []
    for f in sorted(d.glob("*.json")):
        try:
            m = json.loads(f.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        m["_id"] = f.stem
        m["_mtime"] = f.stat().st_mtime
        out.append(m)
    return sorted(out, key=lambda m: m["_mtime"], reverse=True)


def _edges(store: TaskStore, ids: List[str]) -> Dict[str, List[str]]:
    """task id -> the task ids it was ever blocked by, from the append-only event log.

    ⛔ Not `Task.blocked_by`. See the module docstring: `unblock` deletes the edge from that field,
    so a mission whose dependencies are all satisfied renders as eight unrelated tasks.
    """
    known = set(ids)
    out: Dict[str, List[str]] = {}
    for tid in ids:
        try:
            t = store.get(tid)
        except KeyError:
            out[tid] = []
            continue
        seen, deps = set(), []
        for ev in t.events:
            if ev.kind != "block":
                continue
            by = ev.data.get("by")
            # Only edges INSIDE this mission. A block by something outside it is real, and it is
            # reported as a warning rather than drawn into a graph the manifest cannot name.
            if by in known and by not in seen:
                seen.add(by)
                deps.append(by)
        out[tid] = deps
    return out


def waves(edges: Dict[str, List[str]]) -> List[List[str]]:
    """Topological levels: everything whose blockers all landed in an earlier level.

    Same derivation `scripts/mission_marketing_model.py::waves` uses for the plan, so the page and
    the plan cannot disagree about what is parallel. A cycle (which the store permits, because it
    never checked) leaves tasks unplaced rather than looping forever — the caller reports them.
    """
    placed: set = set()
    remaining = {k: set(v) for k, v in edges.items()}
    out: List[List[str]] = []
    while remaining:
        level = sorted(k for k, deps in remaining.items() if deps <= placed)
        if not level:
            break                      # a cycle, or an edge to something not in `edges`
        out.append(level)
        placed |= set(level)
        for k in level:
            remaining.pop(k)
    return out


def _longest_chain(edges: Dict[str, List[str]]) -> List[str]:
    """The longest dependency chain, ending at whichever task nothing else depends on.

    Depth-first with memoisation over a graph of eight nodes; the shape is `board.critical_path`'s,
    which does the same thing over the gate graph. Ties break on the task id so the rendered path
    does not jitter between refreshes for no reason.
    """
    depth: Dict[str, Tuple[int, List[str]]] = {}

    def walk(tid: str, seen: frozenset) -> Tuple[int, List[str]]:
        if tid in depth:
            return depth[tid]
        if tid in seen:
            return (0, [])                             # cycle guard, never a crash
        best: Tuple[int, List[str]] = (0, [])
        for dep in edges.get(tid, []):
            n, path = walk(dep, seen | {tid})
            if (n, path) > best:
                best = (n, path)
        got = (best[0] + 1, best[1] + [tid])
        depth[tid] = got
        return got

    if not edges:
        return []
    return max((walk(t, frozenset()) for t in sorted(edges)), key=lambda r: r[0])[1]


def _chain_ties(edges: Dict[str, List[str]]) -> int:
    """How many DISTINCT chains share the maximum length.

    ⚠ Rendered beside the path, because printing one chain over a graph with three parallel roots
    implies a linearity that is not there. On the live marketing-model mission R1, R2 and R3 all
    feed D1 and all sit at depth 1, so the printed head is whichever one sorts first — a
    presentation artefact that would otherwise read as a finding about the work.

    ⛔ The first version of this counted *endpoints* at maximum depth and returned 1 for exactly
    that graph, reporting no ambiguity in the one place the ambiguity lives. The tie is at the
    head, not the tail, so the count has to be over paths: the number of longest chains ending at
    a node is the sum over its deepest predecessors, or 1 when it has none.
    """
    if not edges:
        return 0
    depth: Dict[str, int] = {}
    paths: Dict[str, int] = {}

    def walk(tid: str, seen: frozenset) -> Tuple[int, int]:
        if tid in depth:
            return depth[tid], paths[tid]
        if tid in seen:
            return 0, 1                                    # cycle guard, never a crash
        deps = [(d, walk(d, seen | {tid})) for d in edges.get(tid, [])]
        best = max([r[0] for _d, r in deps] or [0])
        depth[tid] = best + 1
        paths[tid] = sum(n for _d, (dd, n) in deps if dd == best) or 1
        return depth[tid], paths[tid]

    for t in sorted(edges):
        walk(t, frozenset())
    top = max(depth.values())
    return sum(paths[t] for t in edges if depth[t] == top)


# ------------------------------------------------------------------- state mapping


def _conflicts(contracts: Dict[str, dict], ids: List[str]) -> Dict[str, List[str]]:
    """task id -> the other tasks it cannot safely run beside, from declared resource claims.

    Two tasks conflict when they name the same `resource_claim` and **at least one of them writes
    it**. Two readers of the same Snowflake role are not a conflict and must not be reported as
    one — over-reporting a conflict is how a scheduler that nobody believes gets ignored, which is
    the same end state as one that under-reports.

    ⚠ A task with **no declared resource claim** conflicts with nothing here. That is a stated
    limitation, not a safety property: absence of a declaration is not evidence of isolation. It
    is surfaced as a warning by `state()`.
    """
    out: Dict[str, List[str]] = {t: [] for t in ids}
    for a in ids:
        ca = contracts.get(a) or {}
        ra, wa = ca.get("resource_claim"), (ca.get("access") == "WRITE")
        if not ra:
            continue
        for b in ids:
            if b == a:
                continue
            cb = contracts.get(b) or {}
            if cb.get("resource_claim") != ra:
                continue
            if wa or cb.get("access") == "WRITE":
                out[a].append(b)
    return {k: sorted(v) for k, v in out.items()}


def _task_rows(store: TaskStore, manifest: dict) -> List[dict]:
    """One row per labelled mission task, with its dependency edges and declared contract."""
    labels: Dict[str, str] = manifest.get("labels") or {}
    contracts: Dict[str, dict] = manifest.get("contracts") or {}
    by_id = {tid: lbl for lbl, tid in labels.items()}
    ids = list(by_id)
    edges = _edges(store, ids)
    clash = _conflicts(contracts, ids)

    rows = []
    for tid in ids:
        try:
            t = store.get(tid)
        except KeyError:
            rows.append({"task_id": tid, "label": by_id[tid], "title": "", "missing": True,
                         "status": None, "owner": None, "evidence": 0,
                         "depends_on": [], "conflicts_with": [], "contract": contracts.get(tid, {})})
            continue
        rows.append({
            "task_id": tid,
            "label": by_id[tid],
            "title": t.title,
            "missing": False,
            "status": t.status,
            "owner": t.owner,
            "evidence": len(t.evidence),
            "evidence_refs": [str(ev.get("ref", "")) for ev in t.evidence],
            "depends_on": [by_id[d] for d in edges[tid]],
            "depends_on_ids": list(edges[tid]),
            "conflicts_with": [by_id[c] for c in clash.get(tid, [])],
            "contract": contracts.get(tid, {}),
        })
    order = {lbl: i for i, lbl in enumerate(sorted(labels))}
    rows.sort(key=lambda r: order.get(r["label"], 99))
    return rows


def classify(rows: List[dict], critical: List[str],
             needs_by_label: Optional[Dict[str, List[dict]]] = None) -> List[dict]:
    """Attach the UI state to every row. This is the only place a task becomes READY.

    The order of the tests is the design, and each one has a reason it comes where it does:

    1. `done` / `abandoned` are terminal. Nothing about liveness changes them.
    2. **A written question outranks everything else.** A task whose session is blocked on a human
       is `NEEDS_HUMAN` even while its process is alive — because the operator's next action is
       the answer, not the observation that something is running.
    3. `claimed` is `RUNNING`. It is what the store says, and the store is written by the agent.
    4. An unsatisfied dependency is `BLOCKED`. Never READY.
    5. ⛔ **A live conflicting writer is also `BLOCKED`**, even with every dependency satisfied.
       This is the rule the brief calls out explicitly, and it is the one a dependency-only
       scheduler gets wrong: two agents writing one resource is the collision the DAG cannot see.
    6. What survives all of that is `READY`, and `READY_IN_PARALLEL` only if it is additionally
       **off the critical path** — the operator's question is "what can I start that does not
       fight the thing I care about", and a critical-path task is that thing, not a spare seat.
    """
    needs_by_label = needs_by_label or {}
    running = {r["label"] for r in rows if r["status"] == _T_CLAIMED}
    done = {r["label"] for r in rows if r["status"] == _T_DONE}
    crit = set(critical)

    for r in rows:
        r["blocked_reason"] = ""
        if r["status"] == _T_DONE:
            r["state"] = DONE
            continue
        if r["status"] == _T_ABANDONED:
            r["state"] = ABANDONED
            continue
        if needs_by_label.get(r["label"]):
            r["state"] = NEEDS_HUMAN
            continue
        if r["status"] == _T_CLAIMED:
            r["state"] = RUNNING
            continue

        unmet = [d for d in r["depends_on"] if d not in done]
        if unmet:
            r["state"] = BLOCKED
            r["blocked_reason"] = "waits on " + ", ".join(unmet)
            continue
        live_clash = sorted(c for c in r["conflicts_with"] if c in running)
        if live_clash:
            r["state"] = BLOCKED
            r["blocked_reason"] = ("a live writer holds "
                                   + (r["contract"].get("resource_claim") or "the same resource")
                                   + " — " + ", ".join(live_clash))
            continue
        r["state"] = READY if r["label"] in crit else READY_IN_PARALLEL
    return rows


# ------------------------------------------------------------------------ sessions


def _needs_by_label(questions: List[dict], rows: List[dict]) -> Dict[str, List[dict]]:
    """Best-effort join from a blocked session's question to a mission label.

    ⚠ **Best-effort, and it says so.** A job's `state.json` carries no task id — nothing in the
    substrate links a written question to a TaskStore row. The only join available is textual: a
    label like `D5` appearing as a word in the session's own name/topic/detail. A question that
    does not join is **never dropped**; it lands in `needs_you` unlabelled, because the inbox's
    whole reason to exist is that a question must not be filtered by the thing that produced it.
    """
    import re
    out: Dict[str, List[dict]] = {}
    labels = [r["label"] for r in rows]
    for q in questions:
        hay = " ".join(str(q.get(k) or "") for k in ("name", "topic", "detail", "needs", "where"))
        for lbl in labels:
            if re.search(rf"\b{re.escape(lbl)}\b", hay):
                out.setdefault(lbl, []).append(q)
                q["mission_label"] = lbl
                break
    return out


def session_cards(inventory: Optional[List[dict]] = None) -> List[dict]:
    """Session rows with the actions their measured state actually supports.

    ⛔ `resume` is False for every live class AND for `UNKNOWN-INSTRUMENT-BLIND`. Offering resume
    on a live session spawns a second process against one transcript; offering it on UNKNOWN
    claims the process table was read when it was not.
    """
    inv = _sessions.inventory() if inventory is None else inventory
    out = []
    for s in inv:
        st = s.get("state")
        out.append(dict(
            s,
            can_resume=(st == _sessions.EXITED_RESUMABLE),
            can_open=(st == _sessions.RUNNING_ATTACHED),
            is_live=(st in (_sessions.RUNNING_ATTACHED, _sessions.RUNNING_ORPHANED)),
            liveness_trusted=(st != _sessions.UNKNOWN),
            action=_action_for(st),
        ))
    return out


def _action_for(st: Optional[str]) -> str:
    return {
        _sessions.RUNNING_ATTACHED: "OPEN",
        _sessions.RUNNING_ORPHANED: "ATTACH VIA /agents — DO NOT DUPLICATE",
        _sessions.EXITED_RESUMABLE: "RESUME",
        _sessions.EXITED_GONE: "NEW SESSION",
        _sessions.UNKNOWN: "⚠ LIVENESS UNKNOWN — do not resume",
    }.get(st or "", "—")


# ---------------------------------------------------------------------------- bus


def bus_readers() -> List[str]:
    """Every reader the bus knows about: anyone who has written, and anyone who has a cursor.

    Both halves matter. A lane that has only ever *read* has a cursor and no file; a lane that has
    only ever *written* has a file and no cursor. Taking one source lists half the estate.
    """
    root = _bus.ROOT
    if not root.is_dir():
        return []
    names = {f.stem for f in root.glob("*.jsonl")}
    names |= {f.name[len(".cursor-"):-len(".json")]
              for f in root.glob(".cursor-*.json")}
    return sorted(n for n in names if n)


#: Display caps for the digest. The bus caps one message at `bus.MAX_LEN` (2000 chars), which is
#: the right cap for DELIVERY into a session's context and much too generous for a command page.
DIGEST_EVENTS = 40
DIGEST_CHARS = 420


def upstream(readers: Optional[List[str]] = None) -> List[dict]:
    """Unread peer traffic per reader — **counts and senders only, never the text.**

    ⛔ This returned a fully rendered block per reader until the traffic got real. Measured
    2026-09-01 with 16 readers holding unread events: the Upstream panel alone was **211,485
    bytes**, on a page whose other seven panels total ~12 KB. The bus is ONE channel that many
    readers have not caught up on, so rendering the same event once per reader duplicated every
    message sixteen times. The text now lives in `upstream_digest()`, deduplicated.

    **Reads only — no cursor is advanced anywhere in here.** `bus.mark_read` is called AFTER
    delivery, by the thing that delivered it. Marking on render would mean opening this page counts
    as a session having seen the traffic, which is how a correction gets lost.
    """
    out = []
    for r in (readers if readers is not None else bus_readers()):
        try:
            evs = _bus.unread(r)
        except _bus.BusError:
            continue
        if not evs:
            continue
        out.append({
            "reader": r,
            "unread": len(evs),
            "latest": evs[-1].get("at", ""),
            "from": sorted({e.get("from", "?") for e in evs}),
            # Peer traffic is a nudge, not evidence. Carried on the row so the surface cannot
            # render it without the caveat, and so a finding reference stays reachable.
            "basis": "PEER-TRAFFIC — a nudge, not durable evidence; verify before acting",
            "refs": sorted({ref for e in evs for ref in (e.get("refs") or [])}),
        })
    return sorted(out, key=lambda r: r["unread"], reverse=True)


def upstream_digest(readers: Optional[List[str]] = None) -> dict:
    """The distinct unread events, ONCE, newest first, each truncated for display.

    Deduplicated on (at, from, kind) because one post is unread by every reader that has not caught
    up, and sixteen copies of a message is not sixteen messages. Each event carries `unread_by` so
    the page can still answer "who has not seen this" without repeating the body.

    ⚠ Truncated on purpose, and it says by how much. This is a NUDGE surface: the durable version
    of a correction is in `docs/findings.d/`, and the full text reaches a session through the
    startup packet or the lane-bus hook, not through a dashboard.
    """
    rs = readers if readers is not None else bus_readers()
    seen: Dict[tuple, dict] = {}
    for r in rs:
        try:
            evs = _bus.unread(r)
        except _bus.BusError:
            continue
        for e in evs:
            key = (e.get("at", ""), e.get("from", ""), e.get("kind", ""))
            row = seen.get(key)
            if row is None:
                text = str(e.get("text", ""))
                row = seen[key] = {
                    "at": e.get("at", ""), "from": e.get("from", "?"),
                    "kind": e.get("kind", "note"),
                    "text": text[:DIGEST_CHARS],
                    "clipped": max(0, len(text) - DIGEST_CHARS),
                    "refs": list(e.get("refs") or []), "unread_by": [],
                }
            row["unread_by"].append(r)
    rows = sorted(seen.values(), key=lambda r: r["at"], reverse=True)
    for r in rows:
        r["unread_by"] = sorted(set(r["unread_by"]))
    return {"events": rows[:DIGEST_EVENTS],
            "total": len(rows),
            "not_shown": max(0, len(rows) - DIGEST_EVENTS)}


# ---------------------------------------------------------------------- worktrees


def worktrees() -> List[dict]:
    """Every git worktree with its branch and HEAD, read from git rather than the filesystem.

    `factory.worktrees.status()` only sees directories directly under `<primary>/.worktrees` whose
    name is a lane id, and computes `commits_ahead` against `lane/<id>` — a branch that does not
    exist for a mission worktree, so it reports `?`. This asks git the general question instead,
    because the Switchboard has to describe worktrees that are not lanes.
    """
    primary = _repo.primary()
    try:
        p = subprocess.run(["git", "-C", str(primary), "worktree", "list", "--porcelain"],
                           capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return []
    out, cur = [], {}
    for line in (p.stdout or "").splitlines():
        if line.startswith("worktree "):
            if cur:
                out.append(cur)
            cur = {"path": line[len("worktree "):].strip()}
        elif line.startswith("HEAD "):
            cur["head"] = line[len("HEAD "):].strip()[:7]
        elif line.startswith("branch "):
            cur["branch"] = line[len("branch "):].strip().replace("refs/heads/", "")
        elif line.strip() == "detached":
            cur["branch"] = "(detached)"
    if cur:
        out.append(cur)
    for w in out:
        w["primary"] = pathlib.Path(w["path"]).resolve() == primary.resolve()
        w["dirty"] = _dirty(w["path"])
    return out


def _dirty(path: str) -> Optional[int]:
    """Count of uncommitted entries, or None when git could not be asked.

    None, not 0. A clean tree and an unreadable one must not render the same — that is the false
    green `factory/repo.py` was written about.
    """
    try:
        p = subprocess.run(["git", "-C", str(path), "status", "--porcelain"],
                           capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    if p.returncode != 0:
        return None
    return len([ln for ln in p.stdout.splitlines() if ln.strip()])


# --------------------------------------------------------------------- the projection


def state(mission_id: Optional[str] = None, cheap: bool = False) -> dict:
    """The whole Switchboard, measured now. Derived on every call; never persisted.

    `cheap=True` skips exactly one thing: the `git worktree list` subprocess, so a test can
    exercise the join without a checkout. It is not an optimisation for the page — the page pays
    for the truth — and it deliberately does **not** skip the session inventory or the human
    inbox. An earlier version did, and that is a session-keyed filter on the inbox wearing a
    performance flag's clothes.
    """
    warn: List[str] = []
    mans = manifests()
    chosen = None
    if mans:
        chosen = next((m for m in mans if m["_id"] == mission_id), None) if mission_id else mans[0]
        if chosen is None:
            warn.append(f"no mission manifest named {mission_id!r}; showing {mans[0]['_id']}")
            chosen = mans[0]
    else:
        warn.append("no mission manifest under .data/missions — the DAG panel has nothing to show")

    sp = store_path()
    store = None
    if sp.is_file():
        try:
            store = TaskStore(sp)
        except Exception as exc:                                    # noqa: BLE001
            warn.append(f"task store unreadable: {type(exc).__name__}: {exc}")
    else:
        warn.append(f"no task store at {sp}")

    rows: List[dict] = []
    critical: List[str] = []
    ties = 0
    lvls: List[List[str]] = []
    mission: dict = {}
    if chosen and store is not None:
        rows = _task_rows(store, chosen)
        ids = [r["task_id"] for r in rows]
        edges = _edges(store, ids)
        by_id = {r["task_id"]: r["label"] for r in rows}
        lvls = [[by_id[t] for t in lvl] for lvl in waves(edges)]
        critical = [by_id[t] for t in _longest_chain(edges)]
        ties = _chain_ties(edges)
        placed = {lbl for lvl in lvls for lbl in lvl}
        cyc = sorted(set(by_id.values()) - placed)
        if cyc:
            warn.append("dependency cycle or dangling edge — unplaced: " + ", ".join(cyc))

        mt = chosen.get("mission_task")
        mtask = None
        if mt:
            try:
                mtask = store.get(mt)
            except KeyError:
                warn.append(f"manifest names mission task {mt} which is not in the store")
        mission = {"id": chosen["_id"], "title": chosen.get("mission", chosen["_id"]),
                   "task_id": mt, "status": getattr(mtask, "status", None),
                   "manifest_path": str(missions_dir() / (chosen["_id"] + ".json"))}

        # Mission children the manifest does not name. Two exist on this machine from an earlier
        # `--create`; the store is append-only so they cannot be deleted, only reported.
        if mt:
            named = set(chosen.get("labels", {}).values()) | {mt}
            strays = [t for t in store.all() if t.parent == mt and t.id not in named]
            if strays:
                warn.append(f"{len(strays)} mission child task(s) are not in the manifest and are "
                            f"not shown on the DAG: "
                            + ", ".join(f"{t.id} ({t.status})" for t in strays[:6]))
        undeclared = [r["label"] for r in rows
                      if not (r["contract"] or {}).get("resource_claim")]
        if undeclared:
            warn.append("no resource claim declared for " + ", ".join(undeclared)
                        + " — they are reported conflict-free, which is an absence of a "
                          "declaration, not evidence of isolation")

    # ---- sessions and the human inbox -----------------------------------------
    # ⛔ `cheap` does NOT reach here, and the first version of it did — which is the exact defect
    # this whole panel exists to prevent. A flag that quietly empties the human inbox is a
    # session-keyed filter wearing a performance optimisation's clothes, and it was caught by
    # `test_a_blocked_question_survives_the_process_that_asked_it` rather than by reading.
    # `cheap` skips ONE thing: the git subprocess in `worktrees()`.
    inv: List[dict] = []
    questions: List[dict] = []
    try:
        inv = _sessions.inventory()
    except Exception as exc:                                        # noqa: BLE001
        warn.append(f"session inventory unreadable: {type(exc).__name__}: {exc}")
    try:
        questions = _sessions.blocked()
    except Exception as exc:                                        # noqa: BLE001
        warn.append(f"blocked-question inbox unreadable: {type(exc).__name__}: {exc}")
    cards = session_cards(inv)
    blind = [c for c in cards if not c["liveness_trusted"]]
    if blind:
        warn.append(f"{len(blind)} session(s) report UNKNOWN liveness — the process table could "
                    f"not be read, so 'exited' is not a measurement for them")

    nbl = _needs_by_label(questions, rows)
    rows = classify(rows, critical, nbl)

    # ---- live claims -----------------------------------------------------------
    try:
        held = _claims.active()
    except Exception:                                               # noqa: BLE001
        held = {}
    claim_rows = [{"key": k, "who": getattr(c, "who", ""), "note": getattr(c, "note", ""),
                   "age": c.human_age() if hasattr(c, "human_age") else "",
                   "stale": bool(getattr(c, "stale", False))}
                  for k, c in sorted(held.items())]

    try:
        traffic = upstream()
        digest = upstream_digest()
    except Exception as exc:                                        # noqa: BLE001
        traffic, digest = [], {"events": [], "total": 0, "not_shown": 0}
        warn.append(f"bus unreadable: {type(exc).__name__}: {exc}")

    return {
        "measured_at": _now(),
        "mission": mission,
        "missions": [{"id": m["_id"], "title": m.get("mission", m["_id"])} for m in mans],
        "critical_path": critical,
        "critical_path_basis": CRITICAL_PATH_BASIS,
        # >1 means several chains are equally long and the printed one is just the first by id.
        # Rendered, so the page cannot imply a linearity the graph does not have.
        "critical_path_ties": ties,
        "waves": lvls,
        "tasks": rows,
        "ready": [r["label"] for r in rows if r["state"] == READY],
        "ready_in_parallel": [r["label"] for r in rows if r["state"] == READY_IN_PARALLEL],
        "running": [r["label"] for r in rows if r["state"] == RUNNING],
        "sessions": cards,
        "needs_you": questions,
        "needs_you_count": len(questions),
        "claims": claim_rows,
        "upstream": traffic,
        "upstream_digest": digest,
        "worktrees": [] if cheap else worktrees(),
        "warnings": warn,
    }


# ------------------------------------------------------------- SLICE B: start synced
#
# ⛔ `handoff.session_handoff()` is NOT on the default path here, and that is a measured decision
# rather than a preference. It calls `readiness.measure()`, the same path that put `board.board()`
# at 413.79 s and `session.brief()` at 801.04 s on 2026-09-01. A START SYNCED button that takes
# thirteen minutes is a button the operator routes around at 2am — the exact friction this slice
# exists to remove. It is offered as an explicit, labelled, slow option instead.


def boundary(st: Optional[dict] = None) -> dict:
    """The state boundary a startup packet was written at.

    This is the thing a new session re-measures against. It is deliberately small and made of
    facts that MOVE — a HEAD, a task status, a claim, a bus position. Recording something that
    cannot change would make the check pass for the wrong reason.
    """
    st = state() if st is None else st
    return {
        "measured_at": st["measured_at"],
        "heads": {w.get("branch") or w["path"]: w.get("head") for w in st["worktrees"]},
        "tasks": {r["label"]: r["status"] for r in st["tasks"]},
        "claims": sorted(c["key"] for c in st["claims"]),
        "bus": {u["reader"]: u["latest"] for u in st["upstream"]},
    }


def reground(recorded: dict, st: Optional[dict] = None) -> List[str]:
    """What has moved since `recorded` was taken. An empty list means the packet is still current.

    ⭐ **The markdown packet is a rendered artefact; this is the authority.** A handoff written
    twenty minutes ago reads exactly as confidently as one written now, and this estate has already
    paid for treating old prose as current. So the packet carries its boundary, and the session it
    starts is instructed to call this before doing anything — a non-empty return is
    `REGROUND REQUIRED`, not a warning to note and move past.
    """
    st = state() if st is None else st
    now = boundary(st)
    out: List[str] = []
    for br, head in (recorded.get("heads") or {}).items():
        cur = now["heads"].get(br)
        if cur is None:
            out.append(f"worktree/branch {br} no longer exists")
        elif cur != head:
            out.append(f"{br} moved {head} -> {cur}")
    for br in now["heads"]:
        if br not in (recorded.get("heads") or {}):
            out.append(f"new worktree/branch since the packet: {br}")
    for lbl, stt in (recorded.get("tasks") or {}).items():
        cur = now["tasks"].get(lbl)
        if cur != stt:
            out.append(f"task {lbl} moved {stt} -> {cur}")
    was, isnow = set(recorded.get("claims") or []), set(now["claims"])
    for k in sorted(isnow - was):
        out.append(f"a claim was taken since the packet: {k}")
    for k in sorted(was - isnow):
        out.append(f"a claim was released since the packet: {k}")
    for rd, at in (now["bus"] or {}).items():
        if at != (recorded.get("bus") or {}).get(rd):
            out.append(f"new unread bus traffic for {rd}")
    return out


def _packet_target(target: str, st: dict) -> dict:
    """Resolve a target label to the row it names, or an empty dict for a whole-session packet."""
    return next((r for r in st["tasks"] if r["label"] == target), {}) if target else {}


#: The handshake the generated session is required to run before it does anything. `{boundary_path}`
#: is filled in by whoever writes the packet to disk.
#:
#: ⚠ It is a COMMAND, not a request to be careful. "Re-ground if things have changed" is advice a
#: session can satisfy by feeling confident; `reground()` returning a non-empty list is not.
HANDSHAKE = """## SESSION START — run this BEFORE anything else

Do not act on a single line above until you have re-derived it here. This packet is a **rendered
artefact**; the structured state it was built from is the authority, and it may have moved.

```
python -m factory.switchboard --reground "{boundary_path}"
```

- prints `READY` and exits 0  -> start work.
- prints `REGROUND REQUIRED` and exits 1  -> list what moved, re-read current state with
  `python -m factory.switchboard --state`, and rebuild your understanding from that. Do **not**
  merge an observation taken under the old boundary with one taken under the new one.

Then confirm each of these from measurement, not from this document:

    verify identity          which session am I, and does anything else hold this work
    verify task              the task id above still exists and is in the status stated
    verify worktree          `git rev-parse --show-toplevel` matches the worktree above
    verify branch            `git rev-parse --abbrev-ref HEAD` matches the branch above
    verify HEAD/state        `git rev-parse --short HEAD` matches, or say what moved
    verify dependencies      every blocker above is still DONE
    read upstream traffic    the peer traffic above is a NUDGE, not evidence — verify before acting
    verify no live writer    no other live session holds a conflicting resource claim

Print **READY** when all eight hold, or **REGROUND REQUIRED** with the list. Do not start work
having printed neither.
"""


def startup_packet(target: str = "", note: str = "", reader: str = "",
                   worktree: str = "", st: Optional[dict] = None,
                   include_gate_handoff: bool = False,
                   boundary_path: str = "<the .json beside this file>",
                   ) -> Tuple[str, dict, List[dict]]:
    """(markdown, boundary, the bus events the packet contains). Writes nothing; marks nothing read.

    The third return value is the traffic the packet CARRIES. The caller marks it read only once
    the packet has actually been delivered — see `deliver()`. Returning it rather than marking it
    here is what makes "never advance a cursor before delivery" a property of the shape, instead of
    a rule someone has to remember at the call site.
    """
    st = state() if st is None else st
    row = _packet_target(target, st)
    bnd = boundary(st)
    events: List[dict] = []
    if reader:
        try:
            events = _bus.unread(reader)
        except _bus.BusError:
            events = []

    m = st.get("mission") or {}
    wt = next((w for w in st["worktrees"]
               if w["path"] == worktree or (w.get("branch") or "") == worktree), None)
    if wt is None:
        wt = next((w for w in st["worktrees"] if w.get("primary")), {})
        wt_basis = "DEFAULTED to the primary checkout — the operator chose no worktree"
    else:
        wt_basis = "chosen by the operator at dispatch"

    L: List[str] = []
    L += [f"# Session start — {target or 'mission'} · {st['measured_at']}", "",
          "Generated by `factory.switchboard.startup_packet`. Every value below was **measured "
          "when this was written**, by the same functions the Switchboard page reads. Nothing here "
          "is remembered from a previous session.", ""]

    L += ["## Identity", "",
          f"- **target** — {target or '(whole session, no single task)'}",
          f"- **mission** — {m.get('title') or '(none)'}"]
    if row:
        c = row.get("contract") or {}
        L += [f"- **task id** — `{row['task_id']}` · status **{row['status']}** · "
              f"switchboard state **{row['state']}**",
              f"- **title** — {row['title']}",
              f"- **resource claim** — {c.get('resource_claim') or '⚠ NONE DECLARED'} "
              f"({c.get('access') or '?'})",
              f"- **declared model / effort** — {c.get('model') or '?'} / {c.get('effort') or '?'}",
              f"- **evidence attached** — {row['evidence']}"]
        if row.get("evidence_refs"):
            L += ["- **evidence pointers** — " + ", ".join(f"`{r}`" for r in row["evidence_refs"])]
    L += [""]

    L += ["## Working state", "",
          f"- **worktree** — `{wt.get('path', '?')}` ({wt_basis})",
          f"- **branch** — `{wt.get('branch', '?')}` · **HEAD** `{wt.get('head', '?')}`",
          "- **uncommitted** — " + (str(wt.get("dirty")) if wt.get("dirty") is not None
                                    else "⚠ UNREADABLE — git could not be asked, so this is not "
                                         "a report of a clean tree"),
          ""]

    L += ["## Dependencies", ""]
    if row:
        if row["depends_on"]:
            for d in row["depends_on"]:
                dr = next((x for x in st["tasks"] if x["label"] == d), {})
                L.append(f"- `{d}` — **{dr.get('state', '?')}** ({dr.get('status', '?')})")
        else:
            L.append("- none declared")
        if row.get("blocked_reason"):
            L += ["", f"⛔ **{row['blocked_reason']}**"]
    else:
        L.append(f"- critical path ({CRITICAL_PATH_BASIS.lower()} order): "
                 + (" -> ".join(st["critical_path"]) or "none"))
        if (st.get("critical_path_ties") or 0) > 1:
            L.append(f"- ⚠ {st['critical_path_ties']} chains are equally long; the head shown is "
                     f"only the first by id")
    L += [""]

    L += ["## Live ownership and conflicts", "",
          f"- running now: {', '.join(st['running']) or 'nothing'}"]
    if row and row["conflicts_with"]:
        L.append(f"- `{target}` shares a resource claim with {', '.join(row['conflicts_with'])} "
                 f"— do not write it while one of those is live")
    for c in st["claims"]:
        L.append(f"- claim `{c['key']}` held by {c['who'] or '?'} "
                 f"({c['age']}{', STALE' if c['stale'] else ''})")
    if not st["claims"]:
        L.append("- no lane or task claims are held")
    L += [""]

    if events:
        L += ["## Upstream traffic delivered with this packet", "",
              "```", _bus.render(events), "```", "",
              "⚠ **Peer traffic is a nudge, not durable evidence.** The durable version of a "
              "correction lives in `docs/findings.d/`. Verify anything you act on; never promote a "
              "peer message into truth.", ""]
    elif reader:
        L += ["## Upstream traffic", "", f"- nothing unread for `{reader}`", ""]

    if st["needs_you"]:
        L += ["## Questions waiting on a human", ""]
        for q in st["needs_you"][:8]:
            L.append(f"- **{str(q.get('needs'))[:160]}** ({q.get('state')})")
        L += ["", "These outlive the sessions that asked them. If one of them is yours, it is "
                  "still open.", ""]

    if include_gate_handoff:
        from . import handoff as _handoff
        L += ["## Generated gate handoff", "",
              "⏱ This section ran `readiness.measure()`, which is why the packet was slow.", "",
              _handoff.session_handoff(note), ""]
    elif note.strip():
        L += ["## Note from the operator", "", note.strip(), ""]

    if st["warnings"]:
        L += ["## Warnings on the state this packet was built from", ""]
        L += [f"- {x}" for x in st["warnings"]] + [""]

    L += [HANDSHAKE.replace("{boundary_path}", boundary_path), ""]
    return "\n".join(L), bnd, events


def deliver(reader: str, events: List[dict]) -> Optional[str]:
    """Advance a reader's cursor — ONLY once the packet carrying `events` actually reached them.

    ⛔ Never from a render path, and never from a dry run. `bus.mark_read` is documented as "called
    AFTER delivery, so a crash re-delivers rather than drops", and what this guards is silent:
    traffic marked as seen by a session that never started.
    """
    if not reader or not events:
        return None
    return _bus.mark_read(reader, upto=events[-1].get("at"))


# ---------------------------------------------------------- SLICE C: quick dispatch
#
# P0 prioritises **preventing a wrong-session dispatch** over automating a right one. Everything
# below therefore either resolves to exactly one target or refuses and asks. There is no LLM router
# and no fuzzy scoring: a header either matches a declared alias as a whole phrase, or it does not.

#: header phrase -> the aliases that mean it. **BASIS: AUTHORED**, in the open, for the same reason
#: `session.LANE_SHAPE` is authored in the open — a person has to say what "MAIN T" means, and the
#: honest place to say it is one declared table rather than a guess made per dispatch.
#:
#: ⚠ These are matched as WHOLE PHRASES against the first few lines of a pasted prompt. They are
#: deliberately not matched against the body: a prompt that merely mentions client review in passing
#: is not addressed to it, and treating a mention as an address is exactly the wrong-session
#: dispatch this slice exists to stop.
TARGET_ALIASES: Dict[str, Tuple[str, ...]] = {
    "MAIN T":             ("main t", "main-t", "maint"),
    "CLIENT REVIEW":      ("client review", "client-review", "client-review-readiness"),
    "ARTIFACT GENERATOR": ("artifact generator", "artifact-generator", "project artifact"),
    "SWITCHBOARD":        ("switchboard", "switchboard-p0"),
}

#: How many leading lines of a pasted prompt count as "the header".
HEADER_LINES = 6

# Dispatch routes, in the order of how much of the channel we actually own.
SEND = "SEND"                    # we spawn the process, so we own its input by construction
COPY_OPEN = "COPY+OPEN"          # we open what we can and leave one paste to the operator
COPY_ONLY = "COPY"               # we cannot open anything; copy and name the target precisely
REFUSE = "REFUSE"


def _validate_aliases() -> None:
    """Fail at import if two headers claim the same alias.

    An ambiguous table would make routing non-deterministic while still looking declarative, which
    is worse than no table. Same reason `session._validate` runs at import.
    """
    seen: Dict[str, str] = {}
    for header, aliases in TARGET_ALIASES.items():
        for a in aliases:
            if a in seen and seen[a] != header:
                raise ImportError(
                    f"TARGET_ALIASES is ambiguous: {a!r} is claimed by both {seen[a]!r} "
                    f"and {header!r}, so a prompt carrying it has no deterministic target")
            seen[a] = header


_validate_aliases()


def header_of(prompt: str) -> dict:
    """Which declared target a pasted prompt names, from its first lines only. No LLM, no scoring.

    Returns `matched` (the header phrases found), and refuses to pick when there is not exactly
    one. Two matches is not a tie to be broken — it is a prompt whose address is genuinely unclear,
    and the operator is the one who knows.
    """
    import re
    head = "\n".join((prompt or "").splitlines()[:HEADER_LINES]).lower()
    matched: List[str] = []
    for hdr, aliases in TARGET_ALIASES.items():
        for a in aliases:
            # Whole phrase, bounded. "maint" must not fire inside "maintenance", and "switchboard"
            # must not fire inside a longer word.
            if re.search(rf"(?<![a-z0-9]){re.escape(a)}(?![a-z0-9-])", head):
                matched.append(hdr)
                break
    return {"matched": sorted(set(matched)),
            "deterministic": len(set(matched)) == 1,
            "header": matched[0] if len(set(matched)) == 1 else None}


def _target_sessions(header: str, cards: List[dict]) -> List[dict]:
    """Live-or-resumable sessions whose own topic/name carries the header's aliases.

    ⚠ The join is textual because there is nothing else to join on: a session registry entry has a
    name, a cwd and a topic, and none of them is a lane id or a task id. This is stated rather than
    hidden, and it is why the result is a RECOMMENDATION that still requires the operator to
    confirm rather than an address the page acts on.
    """
    import re
    if not header:
        return []
    aliases = TARGET_ALIASES.get(header, ())
    out = []
    for c in cards:
        hay = " ".join(str(c.get(k) or "") for k in ("topic", "name", "where", "cwd")).lower()
        if any(re.search(rf"(?<![a-z0-9]){re.escape(a)}(?![a-z0-9-])", hay) for a in aliases):
            out.append(c)
    # A live session outranks a dead one as a dispatch target, but neither is dropped.
    rank = {_sessions.RUNNING_ATTACHED: 0, _sessions.RUNNING_ORPHANED: 1,
            _sessions.EXITED_RESUMABLE: 2, _sessions.UNKNOWN: 3, _sessions.EXITED_GONE: 4}
    return sorted(out, key=lambda c: rank.get(c.get("state"), 9))


def route_for(state_: Optional[str]) -> Tuple[str, str]:
    """(route, why) for a target in this liveness state. The measured capability matrix.

    ⛔ **`SEND` appears exactly once, and only where the channel is owned by construction.**
    Measured on this machine, 2026-09-01:

    * every live `claude.exe` reports `MainWindowHandle = 0` — the terminal host owns the window,
      so there is no per-session window to raise and "open the target session" is not achievable
      for a running session. 8 of 8 processes checked.
    * `~/.claude/sessions/<pid>.json` does carry a `messagingSocketPath` named pipe per session,
      and **no code in this estate reads or writes it**. Its protocol is undocumented and
      unverified here. Writing an unknown frame into the pipe of a live session — MAIN T's
      included — is not a P0 experiment, so it is recorded as the identified-but-unproven route
      and nothing claims to use it.
    * what IS proven is the channel the repo already runs on: a session we spawn ourselves takes
      its prompt as an argument (`_launch_script` -> `claude (Get-Content -Raw <prompt>)`), which
      is how every lane in this estate has ever been started.

    So SEND is offered for a session that does not exist yet, and for nothing else.
    """
    if state_ == _sessions.EXITED_GONE or state_ is None:
        return SEND, ("no live process — the session is spawned here, so its prompt is delivered "
                      "as its startup prompt through the same path every lane uses")
    if state_ == _sessions.EXITED_RESUMABLE:
        return COPY_OPEN, ("resumed here (safe: it is not alive), and the prompt is copied for one "
                           "paste — a prompt riding along with an interactive --resume is not "
                           "proven, so it is not claimed")
    if state_ == _sessions.RUNNING_ATTACHED:
        return COPY_OPEN, ("alive and externally controlled. It owns no window handle, so its "
                           "terminal tab cannot be raised from here; the prompt is copied and the "
                           "exact identity shown so the right tab is findable")
    if state_ == _sessions.RUNNING_ORPHANED:
        return COPY_OPEN, ("alive but detached. Use the background-agent path (`claude agents`, "
                           "then `claude attach <id>`); a second process is never started here")
    if state_ == _sessions.UNKNOWN:
        return REFUSE, ("liveness could not be measured, so neither 'it is safe to resume' nor "
                        "'it is safe to spawn' is established")
    return COPY_ONLY, "no route is known for this state"


def dispatch_plan(prompt: str, target_session_id: str = "",
                  st: Optional[dict] = None) -> dict:
    """What would happen if this prompt were dispatched. Decides nothing and spawns nothing.

    The whole contract of P0 dispatch is here: **a plan that does not resolve to exactly one
    session returns `REQUIRE_SELECTION`**, and the caller refuses to act on it.
    """
    st = state() if st is None else st
    cards = st["sessions"]
    hdr = header_of(prompt)
    chosen = next((c for c in cards if c.get("session_id") == target_session_id),
                  None) if target_session_id else None

    candidates = _target_sessions(hdr["header"], cards) if hdr["header"] else []
    plan = {
        "matched_headers": hdr["matched"],
        "header": hdr["header"],
        "candidates": [{"session_id": c.get("session_id"), "state": c.get("state"),
                        "topic": (c.get("topic") or c.get("name") or "")[:80],
                        "cwd": c.get("cwd"), "repo": c.get("repo")} for c in candidates],
        "chosen": None, "route": None, "why": "", "decision": "REQUIRE_SELECTION",
        "prompt_bytes": len((prompt or "").encode("utf-8")),
    }

    if not (prompt or "").strip():
        plan["why"] = "there is no prompt to dispatch"
        return plan

    if chosen is None:
        if not hdr["matched"]:
            plan["why"] = ("no declared header was found in the first "
                           f"{HEADER_LINES} lines — choose the target explicitly")
            return plan
        if not hdr["deterministic"]:
            plan["why"] = ("this prompt names " + " and ".join(hdr["matched"])
                           + " — two addresses is not a tie to break, choose one")
            return plan
        if len(candidates) != 1:
            plan["why"] = (f"header {hdr['header']} matched {len(candidates)} session(s); "
                           + ("no session carries that header, so pick one or start a new session"
                              if not candidates else
                              "more than one session carries that header and they are not "
                              "distinguishable from the registry — choose which"))
            return plan
        chosen = next(c for c in cards if c.get("session_id") == candidates[0]["session_id"])

    route, why = route_for(chosen.get("state"))
    plan["chosen"] = {"session_id": chosen.get("session_id"), "state": chosen.get("state"),
                      "topic": (chosen.get("topic") or chosen.get("name") or "")[:80],
                      "cwd": chosen.get("cwd"), "repo": chosen.get("repo"),
                      "pid": chosen.get("pid"), "kind": chosen.get("kind"),
                      "job_state": chosen.get("job_state"), "needs": chosen.get("needs") or ""}
    plan["route"] = route
    plan["why"] = why
    plan["decision"] = "REFUSE" if route == REFUSE else "READY"
    return plan


def main(argv: Optional[List[str]] = None) -> int:
    """`python -m factory.switchboard --reground <boundary.json>` — the handshake's own instrument.

    It exists as a command because the generated packet tells a session to run it, and a handshake
    step that requires the session to compose a working one-liner is a handshake step that gets
    skipped.
    """
    import argparse
    import sys
    ap = argparse.ArgumentParser(prog="factory.switchboard")
    ap.add_argument("--reground", metavar="BOUNDARY_JSON",
                    help="compare a packet's recorded boundary against measured state now")
    ap.add_argument("--state", action="store_true", help="print the whole projection as JSON")
    a = ap.parse_args(argv)

    if a.state:
        print(json.dumps(state(), indent=1, default=str))
        return 0
    if a.reground:
        try:
            rec = json.loads(pathlib.Path(a.reground).read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            print(f"REGROUND REQUIRED — the boundary itself is unreadable: {exc}", file=sys.stderr)
            return 1
        moved = reground(rec)
        if not moved:
            print(f"READY — state is unchanged since {rec.get('measured_at', '?')}")
            return 0
        print(f"REGROUND REQUIRED — {len(moved)} thing(s) moved since "
              f"{rec.get('measured_at', '?')}:")
        for mv in moved:
            print(f"  - {mv}")
        return 1
    ap.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
