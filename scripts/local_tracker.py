"""A standalone readiness page you can open and refresh without anyone in the loop.

    python scripts/local_tracker.py            # write tracker.html, print the file:// path
    python scripts/local_tracker.py --serve    # serve it; every browser refresh RE-MEASURES
                                               # and the reload button re-reads the CODE;
                                               # sync regenerates the artifact FILE
    python scripts/local_tracker.py --serve --port 8099

The published artifact only changes when someone republishes it. This does not: in --serve mode
each request re-runs the probes against the repositories as they are at that moment, so the
timestamp in the header is the measurement time, not the build time. A tracker that can quietly
show yesterday's state is the drift this whole project exists to remove.

⚠ ONE EXCEPTION, and it is stated here because an unstated one would be exactly that drift. The
`suite` gate shells out to a full pytest run and was 97.6% of every page load, so it is cached
against a content hash of tests/, factory/, scripts/ and the environment, with a 12h ceiling and
PASS-only. **Its headline carries its own age in the same string as its number** — "147 passed
(cached, last run 4m ago)" — which is the rule that makes a cache admissible here. Every other
figure on every page re-ran when you loaded it.

Self-contained: no network, no fonts, no dependencies. Written to tracker.html, which is
gitignored — the page is a view, the probes in factory/readiness.py are the source of truth.
"""
from __future__ import annotations

import datetime
import html
import json
import os
import uuid
import ast
import http.server
import pathlib
import re
import socketserver
import sys
import urllib.parse
import webbrowser

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from factory.readiness import (  # noqa: E402
    CONNECTORS, FACTORY, FAIL, NOT_RUN, PASS, PHASES, UNMEASURABLE, measure)
from factory.board import (  # noqa: E402
    BLOCKED, DONE, READY, board, critical_path)
from factory.lanes import LANES, SIZE, conflicts, recommend, waits_on  # noqa: E402
from factory.findings import by_lane  # noqa: E402
from factory import synthesis as synth  # noqa: E402
from factory import claims as claimlib  # noqa: E402
from factory import operator as opans  # noqa: E402
from factory import worktrees as wt  # noqa: E402
from factory import handoff as ho  # noqa: E402
from factory import runs as runlib  # noqa: E402
from factory import dispatch as dispatchlib  # noqa: E402
from factory import flow as flowlib  # noqa: E402
from factory import goals as goalslib  # noqa: E402
from factory import roadmap as roadlib  # noqa: E402
from factory import schedule as schedlib  # noqa: E402
from factory import sessions as sesslib  # noqa: E402
from factory import dispatch as disp  # noqa: E402
from factory import launch as launchlib  # noqa: E402
from factory import research_run as rrun  # noqa: E402
from factory import teamplan as tplan  # noqa: E402
from factory import control as ctrl  # noqa: E402
from factory import events as evlib  # noqa: E402
from factory import presets as presetlib  # noqa: E402
from factory import provider as provlib  # noqa: E402
from factory import repo as rp  # noqa: E402
from factory import switchboard as sblib  # noqa: E402
from factory import switchboard_render as sbr  # noqa: E402
from factory import switchboard_p1 as sbp1  # noqa: E402
from factory import work as worklib  # noqa: E402

OUT = FACTORY / "tracker.html"

#: dispatch state -> (chip class, label). Five states, five appearances — collapsing NOT SENT into
#: IN FLIGHT is the exact confusion the dispatch module was written to end, so the UI keeps them
#: apart too.
_RCHIP = {
    disp.ANSWERED: ("pass", "ANSWERED"),
    disp.IN_FLIGHT: ("unmeas", "IN FLIGHT"),
    disp.UNDISPATCHED: ("notrun", "NOT SENT"),
    disp.STALE_STATUS: ("fail", "STALE STATUS"),
    disp.UNKNOWN: ("notrun", "UNKNOWN"),
}


def _ago(ts: float) -> str:
    """"3h ago" for a POSIX mtime. Every age on this page is computed at render time.

    Deliberately not stored anywhere. A rendered age that came from a cache is the one number on
    this page that could silently lie about how current it is, so it is re-derived per request —
    which is also why a hard refresh cannot change it.
    """
    secs = max(0.0, datetime.datetime.now().timestamp() - ts)
    if secs < 90:
        return "just now"
    if secs < 5400:
        return "%dm ago" % round(secs / 60)
    if secs < 172800:
        return "%dh ago" % round(secs / 3600)
    return "%dd ago" % round(secs / 86400)

#: (key, href, label). The key is what render() switches on.
TABS = [
    ("tickets", "/", "Tickets"), ("gates", "/gates", "Gates"), ("goals", "/goals", "Goals"),
        ("roadmap", "/roadmap", "Roadmap"),
        ("flow", "/flow", "Flow"), ("lanes", "/lanes", "Lanes"),
        ("sessions", "/sessions", "Sessions"),
        ("research", "/research", "Research"), ("handoff", "/handoff", "Handoff"),
        ("switchboard", "/switchboard", "Switchboard")]

#: Modules whose source can change while the server is running — DERIVED from this file's own
#: imports, never typed out.
#:
#: ⛔ It was typed out, twice, and both lists under-covered. `_HOT` named 6 modules and a second
#: hand-written `_EXTRA` block named 9 more; between them they missed **`factory.flow`,
#: `factory.runs` and `factory.sessions`** — 3 of the 19 factory modules this script imports, one
#: of which (`sessions`) is the entire Sessions tab. So "reload code & re-measure" re-served the
#: session code the process started with and reported success, which is the same claim-of-freshness
#: defect already recorded against `factory.dispatch` in the `_EXTRA` comment below. Fixing that
#: instance by adding a line was treating the symptom: the list is hand-maintained, so it
#: under-covers again on the next import anyone adds.
#:
#: ⭐ Third hand-maintained allow-list to under-cover in one session — after `TeamSpec.version`'s
#: enumerated hash keys and `synthesis.session_prompt`'s `or` fallback. All three looked correct
#: and all three silently omitted something. The rule this file now follows: **if a list can be
#: derived from the thing it is supposed to track, derive it.**
def _own_imports():
    """This file's own `factory` imports, parsed — `(submodules, [(module, [names])])`.

    ⚠ Parsed with `ast`, not regex. The first attempt used a regex and it silently swallowed the
    next twenty lines of the file, "finding" 125 imported names that do not exist — including
    `E402` out of a `# noqa` comment. A deriving step that derives the wrong thing is worse than
    the hand-written list it replaced, because it looks principled.
    """
    tree = ast.parse(pathlib.Path(__file__).read_text(encoding="utf-8", errors="replace"))
    submodules, values = set(), []
    for node in ast.walk(tree):
        if not isinstance(node, ast.ImportFrom) or not node.module:
            continue
        if node.module == "factory":                    # from factory import X as y
            submodules.update(a.name for a in node.names)
        elif node.module.startswith("factory."):        # from factory.X import a, b
            mod = node.module.split(".", 1)[1]
            submodules.add(mod)
            values.append((mod, [a.name for a in node.names]))
    return submodules, values


def _imported_factory_modules() -> tuple:
    """Every `factory.*` module this script imports."""
    return tuple(sorted(_own_imports()[0]))


def _sibling_imports(src: str) -> set:
    """The `factory` modules that one factory module imports, in every form we actually write."""
    found = set()
    for pat in (r"^from \.(\w+) import", r"^from factory\.(\w+) import", r"^import factory\.(\w+)"):
        found.update(re.findall(pat, src, re.M))
    # `from . import claims as claimlib, dispatch as disp` — the alias form, which is how the
    # tracker itself imports every one of its modules.
    for group in re.findall(r"^from \. import (.+)$", src, re.M):
        for part in group.split(","):
            name = part.strip().split(" as ")[0].strip()
            if name.isidentifier():
                found.add(name)
    return found


def _factory_module_closure(seeds: tuple) -> tuple:
    """`seeds` plus every factory module they import, transitively.

    ⛔ **The derivation was still under-covering, one level down.** `_HOT` was derived from this
    file's own imports — which fixed the hand-written list — but `importlib.reload` does NOT
    recurse. So a module this script imports only *through* another one was never reloaded, and
    the button went on reporting success: exactly the false claim of freshness the comment above
    describes, surviving the fix that was supposed to end it.

    Measured 2026-08-31: the direct-import set was **24** modules; the closure is larger, and the
    gap included `factory.verifiers` and `factory.pbi_contract` — the module that decides a
    ticket's verdict and the 12-assertion contract behind it, both reached via `factory.control`.
    Editing a verifier and pressing reload would have re-served the old one and said so happily.

    ⭐ Same lesson as the two before it, one turn further out: **a derived list is only as wide as
    the relation it derives over.** Deriving over "what this file imports" is not the same as
    deriving over "what this process runs", and the second is what the reload button claims.
    """
    pkg = pathlib.Path(__file__).resolve().parent.parent / "factory"
    seen, stack = set(seeds), list(seeds)
    while stack:
        f = pkg / f"{stack.pop()}.py"
        if not f.is_file():
            continue
        for name in _sibling_imports(f.read_text(encoding="utf-8", errors="replace")):
            if name not in seen and (pkg / f"{name}.py").is_file():
                seen.add(name)
                stack.append(name)
    return tuple(sorted(seen))


def _dependency_order(names: tuple) -> list:
    """`names` sorted so a module always follows everything it imports from.

    Reload order is load-bearing and the old comment said so: board and lanes both import from
    readiness, so readiness must be reloaded first or they keep references to the old Gate
    objects. That ordering was maintained by hand in the tuple's literal order — invisible, and
    wrong the moment a new edge appeared. It is now computed from the imports themselves.

    A cycle cannot be ordered; those modules are reloaded last, in name order, and the caller is
    told. Reloading them in *some* order beats refusing to reload at all, but the freshness claim
    for them is weaker and must not be silent.
    """
    pkg = pathlib.Path(__file__).resolve().parent.parent / "factory"
    src = {}
    for n in names:
        f = pkg / f"{n}.py"
        src[n] = f.read_text(encoding="utf-8", errors="replace") if f.is_file() else ""
    deps = {}
    for n in names:
        d = set()
        for m in names:
            if m == n:
                continue
            if (re.search(rf"^from \.{m} import", src[n], re.M)
                    or re.search(rf"^from factory\.{m} import", src[n], re.M)
                    or re.search(rf"^from \. import .*\b{m}\b", src[n], re.M)
                    or re.search(rf"^import factory\.{m}\b", src[n], re.M)):
                d.add(m)
        deps[n] = d
    out, done = [], set()
    while True:
        ready = sorted(n for n in names if n not in done and deps[n] <= done)
        if not ready:
            break
        out.extend(ready)
        done.update(ready)
    cyclic = sorted(n for n in names if n not in done)
    return out + cyclic


def _value_imports() -> list:
    """`(module, [names])` for every `from factory.X import a, b` in this file.

    `import x as y` binds the module object, and `importlib.reload` re-executes a module in place,
    so those aliases see new code for free. `from x import y` binds the VALUE once and does not —
    which is why a rebinding step exists at all. That list was hand-written too; it is now read
    off the same source it is supposed to mirror.
    """
    return _own_imports()[1]


_HOT = tuple(f"factory.{n}"
             for n in _dependency_order(_factory_module_closure(_imported_factory_modules())))

_RELOADED_AT = None
_RELOAD_MSG = None
_SYNC_MSG = None
_ANSWER_MSG = None
_CLAIM_MSG = None
_HANDOFF_NOTE = ""


def launch_command(lane_id: str, make: bool = True):
    """(command_list, prompt_path) for starting `lane_id` in its own terminal. Never spawns."""
    lane = next((l for l in LANES if l.id == lane_id), None)
    if lane is None:
        raise claimlib.ClaimError(f"no lane {lane_id!r}")
    d = FACTORY / ".data" / "lane-prompts"
    d.mkdir(parents=True, exist_ok=True)
    f = d / f"{lane.id}.txt"
    f.write_text(lane.full_prompt, encoding="utf-8")
    # Get-Content -Raw hands the whole file to claude as ONE argument. Interpolating the prompt
    # into the command line instead is how quoting silently truncates it.
    # Each lane runs in its OWN worktree and branch. Three sessions committing to one shared
    # branch is the setup R5 measured at a 41.7% cross-agent conflict rate, mostly structural.
    # `make=False` for a dry run: inspecting the command must not create a branch and a
    # checkout on disk. A dry run with side effects is just a run you did not admit to.
    cwd, note = (wt.ensure(lane.id) if make
                 else (wt.path_for(lane.id), 'would create the worktree'))

    # Prefer wt when present so the tab is titled and lands in the worktree; the cmd fallback
    # relies on Popen's cwd. Neither may contain a ';' — see the note above.
    ps1 = _launch_script(f"lane {lane.id}", f"{lane.title}  ·  {lane.model}", f,
                         LANE_ACCENT.get(lane.id, "38;5;75"), model=lane.model,
                         session_name=f"{lane.id} · {lane.title}")
    w = _wt()
    if w:
        return ([w, "new-tab", "--title", f"{lane.id} · {lane.title}", "--startingDirectory", str(cwd),
                 "--colorScheme", WT_SCHEME,
                 "powershell", "-NoExit", "-ExecutionPolicy", "Bypass", "-File", str(ps1)], f, cwd)
    return (["cmd", "/c", "start", f"lane {lane.id}", "powershell", "-NoExit",
             "-ExecutionPolicy", "Bypass", "-File", str(ps1)], f, cwd)


def start_session_from_handoff(note: str, dry: bool = False):
    """Write the current handoff to a file and open a session already holding it.

    The Handoff tab could generate a handoff and not act on it — you could copy it, and that was
    the whole loop. Copying is the step where a handoff gets skipped at 2am, so this removes it.

    The handoff is written to disk BEFORE the terminal opens, so a failed spawn still leaves the
    text recoverable rather than losing it with the click.
    """
    import subprocess as _sp
    d = FACTORY / ".data" / "handoffs"
    d.mkdir(parents=True, exist_ok=True)
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    f = d / f"session-{stamp}.md"
    f.write_text(ho.session_handoff(note), encoding="utf-8")


    ps1 = _launch_script("handoff session", "session handoff", f, "38;5;110")
    wtexe = _wt()
    cmd = ([wtexe, "new-tab", "--title", "handoff session", "--startingDirectory", str(FACTORY),
            "--colorScheme", WT_SCHEME,
            "powershell", "-NoExit", "-ExecutionPolicy", "Bypass", "-File", str(ps1)]
           if wtexe else
           ["cmd", "/c", "start", "handoff session", "powershell", "-NoExit",
            "-ExecutionPolicy", "Bypass", "-File", str(ps1)])   # Popen gets cwd=FACTORY
    if dry:
        return True, f"DRY RUN — handoff saved to {f.name}, would open {'a wt tab' if wtexe else 'a window'}"
    try:
        _sp.Popen(cmd, cwd=str(FACTORY), close_fds=True)
    except Exception as exc:                                       # noqa: BLE001
        return False, f"handoff saved to {f.name} but no terminal opened ({type(exc).__name__}: {exc})"
    return True, f"new session opened, holding {f.name}"


# ------------------------------------------------------------------ switchboard actions
#
# Both of these live here rather than in `factory/switchboard.py` for the reason `session.py`
# states about itself: the projection answers questions and never dispatches. Spawning a terminal
# is an act, and every other act on this estate is already in this file.

_SB_MSG = None

# ------------------------------------------------------------------ restart / runtime identity
#
# ⭐ `RUNTIME_ID` is generated once per PROCESS. It is what makes "did the restart actually
# happen?" a measurement rather than an assumption: `/healthz` returns it, and the browser only
# reloads when the value it gets back DIFFERS from the one the page was rendered with. A plain
# 200 is not evidence of a restart — the dying process answers 200 too, right up until it exits.
RUNTIME_ID = uuid.uuid4().hex[:12]

#: Exit code the child uses to ask its supervisor for a fresh process. Any other exit means stop.
#: A distinct code is what lets `scripts/switchboard_dev.py` tell "restart me" from "I crashed"
#: without parsing output, so a crash-loop cannot masquerade as a restart loop.
RESTART_EXIT = 97

#: ⛔ Per-process, random, and NEVER derived from anything an attacker can predict or replay
#: across restarts. Present in the served HTML, so it is not a secret from anyone who can already
#: load the page — it is a CSRF token, and that is exactly the threat it closes: a third-party
#: page can make your browser POST here, but it cannot read this value out of our HTML to include
#: it. Set to "" when there is no supervisor, which makes the restart control render as
#: unavailable rather than as a button that kills the server with nothing to bring it back.
RESTART_TOKEN = uuid.uuid4().hex if os.environ.get("SWITCHBOARD_SUPERVISED") == "1" else ""

#: Set by the restart handler; read by `main()` after the server loop ends.
_RESTART_REQUESTED = False


def _spawn(cmd, cwd):
    """The one place the Switchboard opens a terminal. Every spawn here goes through it.

    ⚠ It exists because of a test, and the test was right. Patching `subprocess.Popen` module-wide
    to prove "nothing was opened" also breaks `subprocess.run`, which `switchboard.state()` uses for
    every git and process-table read — so the assertion failed for a reason unrelated to what it
    asserted. One named seam is both easier to patch and a truer statement of the boundary: this
    function is where an act begins.
    """
    import subprocess as _sp
    return _sp.Popen(cmd, cwd=cwd, close_fds=True)


def start_synced(target: str = "", note: str = "", reader: str = "", worktree: str = "",
                 dry: bool = False, gate_handoff: bool = False, require_ready: bool = True,
                 start_mode: str = worklib._tasks.MANUAL_START):
    """Resolve a target canonically, then open a session already holding a measured packet.

    Replaces: generate handoff -> copy -> find terminal -> launch -> paste.

    ⛔ **The target is resolved BEFORE any context is compiled, and an unresolved one is REFUSED.**
    This is the measured P0 defect. `switchboard._packet_target` returns `{}` for a target it does
    not recognise, and every downstream branch reads that as "no single task" — so a typo produced
    a packet titled `# Session start — MARKETING-MODEL-FINALIZATON-01` (one letter wrong) carrying
    the whole mission's critical path, and a session opened believing it was grounded in a piece of
    work that does not exist. Nothing downstream could detect it: the packet was internally
    consistent, and its title was the operator's own typo reflected back.

    The order below is the safety property, and each step gates the next:

        target -> canonical resolution -> readiness -> repo -> conflict -> worktree
        -> context packet -> spawn -> confirm live -> associate -> RUNNING

    ⛔ The bus cursor is advanced LAST, and only on a real spawn that succeeded. Marking traffic
    read before delivery is how a correction gets marked seen by a session that never started.
    """
    # ---- resolve, or refuse -------------------------------------------------------
    resolved = None
    if target:
        try:
            resolved = worklib.resolve(target)
        except worklib.TargetRefused as exc:
            return False, (f"{exc} Nothing was written, no context was compiled and no terminal "
                           f"was opened.")
        except Exception as exc:                                   # noqa: BLE001
            return False, (f"REFUSED: the target {target!r} could not be resolved "
                           f"({type(exc).__name__}: {exc}) — an unresolvable target is not a "
                           f"whole-mission session.")
        if require_ready and not resolved.is_ready:
            bad = [f"{c.name}={c.verdict}" for c in resolved.checks
                   if c.verdict in (worklib.FAIL, worklib.UNMEASURED)]
            return False, (f"REFUSED: {resolved.id} is {resolved.state}, not READY "
                           f"({', '.join(bad) or 'no failing check recorded'}). "
                           f"{resolved.blocked_reason or ''} Readiness is derived; it cannot be "
                           f"overridden from the page.")
        target = resolved.id          # canonical spelling from here on, never the operator's
    d = FACTORY / ".data" / "handoffs"
    d.mkdir(parents=True, exist_ok=True)
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    stem = f"switchboard-{(target or 'session').lower()}-{stamp}"
    md, bnd, events = (None, None, [])
    try:
        st = sblib.state()
        bpath = d / f"{stem}.boundary.json"
        md, bnd, events = sblib.startup_packet(
            target=target, note=note, reader=reader, worktree=worktree, st=st,
            include_gate_handoff=gate_handoff, boundary_path=str(bpath))
    except Exception as exc:                                       # noqa: BLE001
        return False, f"could not build the packet: {type(exc).__name__}: {exc}"

    f = d / f"{stem}.md"
    f.write_text(md, encoding="utf-8")
    bpath.write_text(json.dumps(bnd, indent=1), encoding="utf-8")

    if dry:
        return True, (f"DRY RUN — packet at {f.name} ({len(md):,} bytes) and boundary at "
                      f"{bpath.name}; no terminal opened, and {len(events)} bus event(s) were "
                      f"NOT marked read")

    ps1 = _launch_script(f"switchboard {target or 'session'}",
                         f"start synced · {target or 'session'}", f, "38;5;110",
                         session_name=f"{target or 'session'} · start synced")
    cwd = worktree if worktree and pathlib.Path(worktree).is_dir() else str(FACTORY)
    wtexe = _wt()
    cmd = ([wtexe, "new-tab", "--title", f"switchboard {target or 'session'}",
            "--startingDirectory", cwd, "--colorScheme", WT_SCHEME,
            "powershell", "-NoExit", "-ExecutionPolicy", "Bypass", "-File", str(ps1)]
           if wtexe else
           ["cmd", "/c", "start", f"switchboard {target or 'session'}", "powershell", "-NoExit",
            "-ExecutionPolicy", "Bypass", "-File", str(ps1)])
    try:
        proc = _spawn(cmd, cwd)
    except Exception as exc:                                       # noqa: BLE001
        return False, (f"packet saved to {f.name} but no terminal opened "
                       f"({type(exc).__name__}: {exc}) — nothing was marked read")

    # ---- confirm the spawn, then associate ----------------------------------------
    # ⚠ `Popen` returning is not evidence a session started; it is evidence a process was
    # created. A launcher that exits instantly (wt handing off to an existing window, a missing
    # PowerShell) returns a healthy object and leaves nothing running. So the association below
    # is gated on the process still being alive a moment later, and the Claude session id is
    # recorded ONLY when the registry actually shows it — never assumed from the spawn.
    assoc = ""
    if resolved is not None:
        alive = _confirm_spawn(proc)
        try:
            store = worklib.open_store()
            if alive:
                store.claim(resolved.id, actor="switchboard")
                # ⭐ Recorded separately from `claim`. `claim` says work began; this says who
                # DECIDED it should. The pair is what makes autonomy performance measurable later
                # rather than reconstructed from timestamps and guesswork.
                store.record_start(resolved.id, start_mode, actor="switchboard")
                sid = _await_session(resolved.id)
                if sid:
                    store.attach_session(resolved.id, sid, actor="switchboard")
                    assoc = f"; {resolved.id} is RUNNING, attached to session {sid[:8]}"
                else:
                    assoc = (f"; {resolved.id} is RUNNING — the terminal is alive but no Claude "
                             f"session has registered under it yet, so no session id was "
                             f"attached (it is not claimed to be known)")
            else:
                assoc = (f"; ⚠ the launcher exited immediately, so {resolved.id} was NOT moved to "
                         f"RUNNING and no session was associated — check the terminal")
        except Exception as exc:                                   # noqa: BLE001
            assoc = (f"; ⚠ {resolved.id} could not be moved to RUNNING "
                     f"({type(exc).__name__}: {exc}) — the session is open regardless")

    marked = None
    if reader and events:
        try:
            marked = sblib.deliver(reader, events)
        except Exception as exc:                                   # noqa: BLE001
            return True, (f"session opened holding {f.name}, but the bus cursor for {reader} could "
                          f"not be advanced ({type(exc).__name__}: {exc}) — that traffic will be "
                          f"delivered again, which is the safe direction")
    return True, (f"session opened in {cwd}, holding {f.name}"
                  + assoc
                  + (f"; delivered {len(events)} bus event(s) to {reader} and advanced its cursor "
                     f"to {marked}" if marked else ""))


#: How long to wait before deciding a launcher that exited was a failed spawn. Short, because the
#: only thing being distinguished is "died instantly" from "is running" — a real terminal lives for
#: minutes, a broken launcher is gone in milliseconds.
_SPAWN_CONFIRM_S = 0.8

#: Bounded wait for the Claude session to register itself. `claude` takes a second or two to write
#: its registry entry. Not waiting longer on purpose: an unattached-but-RUNNING piece of work is a
#: true statement the next refresh will improve on, whereas blocking the POST for ten seconds makes
#: the page feel broken and still guarantees nothing.
_SESSION_WAIT_S = 6.0


def _confirm_spawn(proc) -> bool:
    """True when the launched process is still alive shortly after spawn.

    A `Popen` that returns is not evidence of a live session — it is evidence a process was
    created. This is the smallest check that separates the two.
    """
    import time as _t
    if proc is None:
        return False
    deadline = _t.time() + _SPAWN_CONFIRM_S
    while _t.time() < deadline:
        if proc.poll() is not None:
            return False
        _t.sleep(0.1)
    return proc.poll() is None


def _await_session(work_id: str):
    """The Claude session id whose name carries `work_id`, or None. Never guesses.

    The launcher sets `CLAUDE_CODE_SESSION_NAME` to a string containing the work id, so this is a
    real join rather than "the newest session", which would attach whichever session happened to
    start last — including one a human opened by hand.
    """
    import re as _re
    import time as _t
    pat = _re.compile(r"(?<![A-Za-z0-9])" + _re.escape(work_id) + r"(?![A-Za-z0-9])", _re.I)
    deadline = _t.time() + _SESSION_WAIT_S
    while _t.time() < deadline:
        try:
            for srow in sesslib.inventory():
                hay = " ".join(str(srow.get(k) or "") for k in ("name", "topic", "detail"))
                if pat.search(hay) and srow.get("session_id"):
                    return str(srow["session_id"])
        except Exception:                                          # noqa: BLE001
            return None
        _t.sleep(0.4)
    return None


def resolve_hold(work_id: str, hold: str = "", decision: str = "", note: str = ""):
    """Release an explicit hold on a piece of work — the operator's decision, recorded.

    ⛔ **This exists because the button did not.** The NEEDS YOU decision card rendered a control
    labelled RESOLVE that was an `<a href>` to the Inspector, and the Inspector carried no control
    to release a hold either. So the page stated that a decision was required, named the person
    required to make it, and offered no way to make it — an inbox that can only ever accumulate.
    Paul hit exactly that on a phone with no laptop access, which is the situation the whole
    surface exists to serve.

    The release is `unblock`, which is already the store's inverse of `block`, plus an evidence row
    so the decision has an author, a time and a reason. `decision` is recorded verbatim: APPROVE
    and REJECT are different answers and both are answers.
    """
    work_id, hold = (work_id or "").strip(), (hold or "").strip()
    if not work_id or not hold:
        return False, "REFUSED: a resolve needs both the work id and the hold it releases."
    try:
        store = worklib.open_store()
        t = store.get(work_id)
    except KeyError:
        return False, f"REFUSED: no canonical work named {work_id!r}."
    except Exception as exc:                                       # noqa: BLE001
        return False, f"could not read the store: {type(exc).__name__}: {exc}"
    if hold not in (t.blocked_by or []):
        return False, (f"REFUSED: {work_id} is not held on {hold!r}. Current holds: "
                       + (", ".join(t.blocked_by) or "none") + ". The page was stale.")
    verdict = (decision or "RESOLVED").upper()[:32]
    try:
        # ⭐ Evidence FIRST. A release that lands with no record of who decided or why is the
        # thing this estate keeps finding: a state change nobody can reconstruct afterwards.
        store.add_evidence(work_id, kind=f"operator decision: {verdict}",
                           ref=f"hold:{hold}", actor="operator", basis="MEASURED")
        if note.strip():
            store._emit({"ts": __import__("time").time(), "actor": "operator", "kind": "note",
                         "task": work_id, "data": {"text": note.strip()[:2000], "hold": hold,
                                                   "decision": verdict}})
        store.unblock(work_id, by=hold, actor="operator")
    except Exception as exc:                                       # noqa: BLE001
        return False, f"could not release the hold: {type(exc).__name__}: {exc}"
    w = next((x for x in worklib.project() if x.id == work_id), None)
    return True, (f"{verdict}: released {hold} on {work_id}"
                  + (f" — now {w.state}" + (f" ({w.blocked_reason[:90]})"
                                            if w.blocked_reason else "") if w else "")
                  + (f'; note recorded' if note.strip() else ""))


def set_autonomy(work_id: str, to: str = "", go: str = "set"):
    """Set the execution policy, or PAUSE / RESUME it.

    ⭐ PAUSE is always available and never conditional. A stop that could be refused because of the
    state it is trying to stop would not be a stop, so it does not check readiness, policy, or
    whether the work is running -- it records the operator's decision and that is that.
    """
    work_id = (work_id or "").strip()
    if not work_id:
        return False, "REFUSED: no work id."
    try:
        store = worklib.open_store()
        store.get(work_id)
    except KeyError:
        return False, f"REFUSED: no canonical work named {work_id!r}."
    except Exception as exc:                                       # noqa: BLE001
        return False, f"could not read the store: {type(exc).__name__}: {exc}"
    try:
        if go == "pause":
            store.pause_autonomy(work_id, True, actor="operator")
            return True, f"{work_id}: autonomy PAUSED — it will not start without you."
        if go == "resume":
            store.pause_autonomy(work_id, False, actor="operator")
            return True, f"{work_id}: autonomy resumed; the policy applies again."
        store.set_autonomy(work_id, to, actor="operator")
    except ValueError as exc:
        return False, f"REFUSED: {exc}"
    except Exception as exc:                                       # noqa: BLE001
        return False, f"could not set autonomy: {type(exc).__name__}: {exc}"
    w = next((x for x in worklib.project() if x.id == work_id), None)
    allowed, why = worklib.guarded_start(w) if w else (False, ["work not found after write"])
    return True, (f"{work_id}: autonomy set to {to}. "
                  + ("It may start without a human when READY."
                     if allowed else
                     "It will still NOT start without a human: " + "; ".join(why[:3])))


def create_work(title: str, objective: str = "", repo: str = "", visibility: str = "PRIVATE",
                work_id: str = "", depends_on: str = "", resource_claim: str = "",
                access: str = "WRITE"):
    """The operator-facing CREATE WORK path. One TaskStore write; no manifest anywhere.

    ⭐ This is the whole of `MANIFEST_CREATION_TOOL_MISSING`. Before it, arbitrary work needed a
    bespoke Python script to build `.data/missions/<id>.json` before the Switchboard could see it.
    Now the work IS the store row, and the manifest is an optional overlay for the one legacy
    mission that predates this.
    """
    title = (title or "").strip()
    if not title:
        return False, "REFUSED: work needs a title — 'what needs doing?' cannot be blank."
    if not (repo or "").strip():
        return False, ("REFUSED: work needs a repository. Without one there is no worktree to "
                       "open, and readiness could never be measured.")
    deps = [d.strip() for d in (depends_on or "").replace(",", " ").split() if d.strip()]
    try:
        w = worklib.create(
            title=title, objective=(objective or "").strip(), repo=repo.strip(),
            visibility=visibility if visibility in worklib._tasks.VISIBILITIES else "PRIVATE",
            work_id=(work_id or "").strip() or None, depends_on=deps,
            resource_claim=(resource_claim or "").strip(),
            access=access if access in ("READ", "WRITE") else "WRITE",
            actor="operator")
    except Exception as exc:                                       # noqa: BLE001
        return False, f"could not create work: {type(exc).__name__}: {exc}"
    return True, (f"created {w.id} — {w.state}"
                  + (f" ({w.blocked_reason})" if w.blocked_reason else "")
                  + f"; visibility {w.visibility}"
                  + (f"; depends on {', '.join(deps)}" if deps else "")
                  + ". Readiness is derived, so it was not created READY.")


def resume_session(session_id: str, dry: bool = False):
    """Resume an exited session — after RE-MEASURING that it is actually exited.

    ⛔ **The rendered page is not the authority.** A page rendered thirty seconds ago can offer a
    RESUME for a session that has since been reattached, and `claude --resume` against a live
    session puts two processes on one transcript. That is the divergent-duplicate failure
    control-room.md §5 records, and it is why liveness is re-read here rather than passed in from
    the link the operator clicked.
    """
    row = next((c for c in sblib.session_cards()
                if c.get("session_id") == session_id), None)
    if row is None:
        return False, f"no session {session_id[:8]} in the registry now — the page was stale"
    if not row["can_resume"]:
        return False, (f"refusing to resume {session_id[:8]}: it is {row['state']}. "
                       + ("It is alive — resuming would put a second process on one transcript. "
                          "Attach to it instead."
                          if row["is_live"] else
                          "Liveness could not be measured, so 'exited' is not established."
                          if not row["liveness_trusted"] else
                          "There is no transcript to resume from; start a new session."))
    cwd = row.get("cwd") or str(FACTORY)
    wtexe = _wt()
    title = (row.get("topic") or row.get("name") or session_id)[:48]
    inner = ["powershell", "-NoExit", "-ExecutionPolicy", "Bypass", "-Command",
             f"claude --resume {session_id}"]
    cmd = ([wtexe, "new-tab", "--title", title, "--startingDirectory", cwd,
            "--colorScheme", WT_SCHEME] + inner
           if wtexe else ["cmd", "/c", "start", title] + inner)
    if dry:
        return True, f"DRY RUN — would resume {session_id[:8]} ({row['state']}) in {cwd}"
    try:
        _spawn(cmd, cwd)
    except Exception as exc:                                       # noqa: BLE001
        return False, f"could not resume {session_id[:8]}: {type(exc).__name__}: {exc}"
    return True, f"resumed {session_id[:8]} in {cwd}"


#: The last dispatch preview or attempt, rendered back into the Switchboard panel. Held in memory
#: only — a dispatch plan is a statement about a moment, and persisting it would create exactly the
#: stale second source of truth this page refuses to have.
_DISPATCH = None


def quick_dispatch(prompt: str, target_session_id: str = "", dry: bool = False):
    """Route a pasted prompt to one Claude session, or refuse and say which choice is missing.

    ⛔ **Refusing is the feature.** P0 prioritises preventing a wrong-session dispatch over
    automating a right one, so anything that does not resolve to exactly one session returns
    REQUIRE_SELECTION and nothing is spawned, opened or copied server-side.

    The routes, and what each actually does:

      SEND        no live process. The session is started here, so the prompt is delivered as its
                  startup prompt through `_launch_script` — the same path every lane in this estate
                  has ever been launched with. This is the only owned input channel, and it is the
                  only place SEND is offered.
      COPY+OPEN   a live or resumable session someone else controls. A resumable one is resumed
                  (safe — it is not alive). A running one is NOT touched: it owns no window handle,
                  so nothing here can raise its tab, and the honest output is its exact identity
                  plus the prompt on the clipboard.
      REFUSE      liveness is UNKNOWN, so neither resume nor spawn is established as safe.
    """
    global _DISPATCH
    try:
        st = sblib.state()
        plan = sblib.dispatch_plan(prompt, target_session_id=target_session_id, st=st)
    except Exception as exc:                                       # noqa: BLE001
        _DISPATCH = None
        return False, f"could not plan the dispatch: {type(exc).__name__}: {exc}"

    _DISPATCH = plan
    if plan["decision"] != "READY":
        return False, f"{plan['decision']} — {plan['why']}"

    d = FACTORY / ".data" / "dispatch"
    d.mkdir(parents=True, exist_ok=True)
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    f = d / f"dispatch-{stamp}.txt"
    f.write_text(prompt, encoding="utf-8")
    plan["prompt_file"] = str(f)

    ch = plan["chosen"]
    who = f"{ch['topic'][:44]} ({ch['state']}, pid {ch['pid']}, {ch['cwd']})"
    if dry:
        return True, (f"DRY RUN — would {plan['route']} to {who}; prompt saved to {f.name}, "
                      f"nothing opened")

    if plan["route"] == sblib.SEND:
        ps1 = _launch_script(f"dispatch {stamp}", f"quick dispatch · {plan['header'] or 'manual'}",
                             f, "38;5;180", session_name=f"{plan['header'] or 'dispatch'} · sent")
        cwd = ch.get("cwd") if ch.get("cwd") and pathlib.Path(ch["cwd"]).is_dir() else str(FACTORY)
        wtexe = _wt()
        cmd = ([wtexe, "new-tab", "--title", f"dispatch {plan['header'] or stamp}",
                "--startingDirectory", cwd, "--colorScheme", WT_SCHEME,
                "powershell", "-NoExit", "-ExecutionPolicy", "Bypass", "-File", str(ps1)]
               if wtexe else
               ["cmd", "/c", "start", "dispatch", "powershell", "-NoExit",
                "-ExecutionPolicy", "Bypass", "-File", str(ps1)])
        try:
            _spawn(cmd, cwd)
        except Exception as exc:                                   # noqa: BLE001
            return False, f"prompt saved to {f.name} but nothing opened: {type(exc).__name__}: {exc}"
        return True, f"SENT — new session opened in {cwd} holding {f.name}"

    if plan["route"] == sblib.COPY_OPEN and ch["state"] == sesslib.EXITED_RESUMABLE:
        ok, msg = resume_session(ch["session_id"])
        return ok, (f"COPY+OPEN — {msg}; the prompt is on your clipboard and saved to {f.name}. "
                    f"Paste it into the resumed session."
                    if ok else f"prompt saved to {f.name}, but {msg}")

    # A live, externally controlled session. Nothing is opened, and the reason is measured.
    return True, (f"COPY+OPEN — prompt copied and saved to {f.name}. Target is {who}. "
                  f"It is alive and this page cannot raise its terminal tab "
                  f"(claude.exe reports MainWindowHandle 0 — the terminal host owns the window), "
                  f"so paste it into that tab. No second process was started.")


def start_research_pass(rid: str, dry: bool = False):
    """Prepare a research pass and open a session that runs it here.

    ⛔ An earlier version of this split passes into "launchable" and "you go and paste it". That was
    wrong -- the deep-research skill replaces the paste loop and states that the default is a pass
    runs here. Every pass launches now, and the run log records that it ran LOCALLY, because that
    is what tells the next reader how much independence the answer had.

    Preparation happens BEFORE the spawn, so a failed spawn still leaves the prompt on disk and the
    dispatch recorded, rather than losing both with the click.

    ⛔ `dry` is passed DOWN to `rrun.start`, never checked here afterwards. It used to be checked
    here, three statements too late: `rrun.start(rid)` had already rebuilt the evidence pack,
    flipped the prompt's `**Status:**` to DISPATCHED and appended a ledger row, and this function
    then printed `DRY RUN --` over the top of it. A dry run that dispatches is worse than none at
    all, because the output says the opposite of what happened.
    """
    import subprocess as _sp
    try:
        res = rrun.start(rid, dry=dry)
    except rrun.ResearchError as exc:
        return False, f"{rid}: {exc}"
    except Exception as exc:                                       # noqa: BLE001
        return False, f"{rid}: {type(exc).__name__}: {exc}"

    if dry:
        # Nothing is written on this path — not even the session file. What WOULD run is in
        # res["session_prompt"] for the caller to inspect.
        return True, (f"DRY RUN -- {res['note']}; would open a session running "
                      f"{rid.upper()}-session.txt")

    # The session is told to invoke the skill; it is NOT handed a paraphrase of the brief.
    d = FACTORY / ".data" / "research-prompts"
    d.mkdir(parents=True, exist_ok=True)
    launch_file = d / f"{rid.upper()}-session.txt"
    launch_file.write_text(res["session_prompt"], encoding="utf-8")

    pt = res["plan"]["pass_type"]
    ps1 = _launch_script(f"research {rid}", f"{rid} · {pt}", launch_file,
                         "38;5;140", session_name=f"{rid} · {pt}")
    wtexe = _wt()
    cmd = ([wtexe, "new-tab", "--title", f"{rid} · {pt}", "--startingDirectory", str(FACTORY),
            "--colorScheme", WT_SCHEME,
            "powershell", "-NoExit", "-ExecutionPolicy", "Bypass", "-File", str(ps1)]
           if wtexe else
           ["cmd", "/c", "start", f"research {rid}", "powershell", "-NoExit",
            "-ExecutionPolicy", "Bypass", "-File", str(ps1)])
    try:
        _sp.Popen(cmd, cwd=str(FACTORY), close_fds=True)
    except Exception as exc:                                       # noqa: BLE001
        return False, (f"{res['note']} -- but no terminal opened "
                       f"({type(exc).__name__}: {exc}). The prompt is on disk.")
    return True, f"{res['note']} -- session opened, running {rid} as {pt}"


def start_synthesis_pass(dry: bool = False):
    """Open a session that reconciles the filed answers into SYNTHESIS.md.

    ⛔ This page used to state, in print, that there is no synthesize button "because synthesis is
    judgement, and a button that cannot exercise it would either fake it or do nothing". That was
    right while the only mechanism was a paste loop. It is superseded for the same reason the
    research paste loop was: the button does not exercise judgement, it DISPATCHES judgement to a
    session in this repo and records that it did. See `factory/synthesis.py` for the full argument.

    ⚠ It still cannot make the reconciliation GOOD — `unsynthesised()` checks mention and
    `unreconciled()` checks mtime, and a session writing one sentence per answer clears both. That
    is said on the page rather than papered over.

    `dry` writes NOTHING, and is checked BEFORE anything is prepared — the defect fixed in
    `start_research_pass` on 2026-08-23, not re-introduced here.
    """
    import subprocess as _sp
    gap = synth.unsynthesised() or synth.unreconciled()
    if not gap:
        return False, ("nothing to reconcile -- SYNTHESIS.md mentions every filed answer and "
                       "postdates all of them")
    try:
        body = synth.session_prompt()
    except Exception as exc:                                       # noqa: BLE001
        return False, f"could not build the reconciling prompt: {type(exc).__name__}: {exc}"

    if dry:
        return True, (f"DRY RUN -- would reconcile {', '.join(gap)} into SYNTHESIS.md "
                      f"({len(body):,}-char session prompt); nothing written")

    # ⛔ Claim BEFORE spawning, or the window is exactly as wide as the thing being guarded.
    # Without this, two clicks opened two sessions each told to write docs/research/SYNTHESIS.md.
    # Two agents on one 76 KB document is last-write-wins and the loser's whole pass vanishes with
    # no error anywhere.
    #
    # ⚠ No pid is recorded, and that is not laziness. The pid we could capture is `wt`'s, which
    # exits within seconds and does NOT own the claude session it hands off to — recording it
    # would make the claim read HELD-GONE almost immediately, i.e. a guard that reports itself
    # free while the session runs. With no pid, `task_holder` returns HELD_UNVERIFIED and this
    # FAILS CLOSED: the second click is refused and told how to release. That matches the module's
    # own rule — a stale claim still blocks, and the refusal says how to clear it, because a
    # control that quietly expires is one you cannot reason about.
    try:
        claimlib.task_claim("synthesis", note="reconciling " + ", ".join(gap))
    except claimlib.ClaimError as exc:
        return False, f"{exc} Release it at /release-task/synthesis if that session is gone."

    d = FACTORY / ".data" / "research-prompts"
    d.mkdir(parents=True, exist_ok=True)
    launch_file = d / "SYNTHESIS-session.txt"
    launch_file.write_text(body, encoding="utf-8")

    title = "synthesis · " + ", ".join(gap)
    ps1 = _launch_script("synthesis", title, launch_file, "38;5;180", session_name=title)
    wtexe = _wt()
    cmd = ([wtexe, "new-tab", "--title", title, "--startingDirectory", str(FACTORY),
            "--colorScheme", WT_SCHEME,
            "powershell", "-NoExit", "-ExecutionPolicy", "Bypass", "-File", str(ps1)]
           if wtexe else
           ["cmd", "/c", "start", "synthesis", "powershell", "-NoExit",
            "-ExecutionPolicy", "Bypass", "-File", str(ps1)])
    try:
        _sp.Popen(cmd, cwd=str(FACTORY), close_fds=True)
    except Exception as exc:                                       # noqa: BLE001
        # Nothing started, so holding the claim would block the next honest attempt for no reason.
        claimlib.task_release("synthesis")
        return False, (f"prompt written to {launch_file.name} -- but no terminal opened "
                       f"({type(exc).__name__}: {exc}). Claim released.")
    return True, (f"session opened -- reconciling {', '.join(gap)} into SYNTHESIS.md. "
                  "It writes that ONE file; re-render this page to see the gap close.")


#: One frame for every session (system identity); the banner accent varies per lane (instance
#: identity). Five differently-coloured windows would read as noise, not information.
WT_SCHEME = "Agent Factory Blue"
LANE_ACCENT = {"control-plane": "38;5;75", "certify": "38;5;79", "judgement": "38;5;140",
               "artifact": "38;5;73", "grain": "38;5;180"}


def _launch_script(name: str, subtitle: str, prompt_file, accent: str = "38;5;75",
                   model: str = "", session_name: str = ""):
    """Write a .ps1 that titles the window, prints a banner, then runs claude.

    ⚠ A .ps1 rather than a -Command string ON PURPOSE. Semicolons are wt's subcommand separator,
    so a multi-statement -Command payload is split by wt and the remainder is launched as a
    program — that is F10, and it cost a real click to find. A file has no such problem.
    """
    d = FACTORY / ".data" / "launch"
    d.mkdir(parents=True, exist_ok=True)
    f = d / f"{name}.ps1"
    esc = chr(27)
    bar = "─" * 58
    # A lane declares its model; the banner has always printed it. Until now the generated
    # script ran a bare `claude`, so every lane actually ran on whatever the session default
    # was — control-plane advertising opus while running sonnet, grain advertising haiku while
    # running something dearer. A banner that names a model the process is not using is worse
    # than no banner: it is a label that reads as verified.
    model_flag = f" --model {model}" if model else ""
    # Every lane session was called "boot pre-flight verification" — the name of whatever
    # session started the tracker — so `claude` peer lists showed three identical rows and the
    # only thing telling them apart was cwd. You cannot address a session you cannot name, and
    # Paul could not tell which window he was looking at. Read at startup by the CLI
    # (control chars stripped, capped at 200), so a lane can state what it is working on.
    sess = (session_name or name).replace("'", "''")
    body = f"""$Host.UI.RawUI.WindowTitle = '{name}'
# The tracker is itself started from a Claude Code session, so it inherits
# CLAUDE_CODE_CHILD_SESSION and every terminal it spawns inherits it too — which turns transcript
# saving OFF in the lane sessions. A lane that runs for an hour and cannot be resumed, with no
# record of what it did, is exactly the loss this programme exists to prevent. Cleared here in the
# script rather than depending on how the server happened to be launched.
Remove-Item Env:CLAUDE_CODE_CHILD_SESSION -ErrorAction SilentlyContinue
$env:CLAUDE_CODE_FORCE_SESSION_PERSISTENCE = '1'
$env:CLAUDE_CODE_SESSION_NAME = '{sess}'
$e = [char]27
Write-Host ""
Write-Host "$e[{accent}m{bar}$e[0m"
Write-Host "$e[{accent}m  AGENT FACTORY $e[0m$e[38;5;250m{subtitle}$e[0m"
Write-Host "$e[38;5;244m  {name}$e[0m"
Write-Host "$e[{accent}m{bar}$e[0m"
Write-Host ""
claude{model_flag} (Get-Content -Raw -Encoding UTF8 -LiteralPath '{prompt_file}')
"""
    # utf-8-SIG: PowerShell 5.1 reads a BOM-less .ps1 as ANSI and mangles the box rules.
    f.write_text(body, encoding="utf-8-sig")
    return f


#: Repositories this estate operates on. A closed list, not a free-text field: a repo that does
#: not exist is a readiness check that can never pass and a worktree that can never open.
KNOWN_REPOS = ("agent-factory", "clients", "connector", "core_api", "wiki")


def _repo_choices():
    """Repositories CREATE WORK may name, this checkout's own repo first.

    ⛔ NOT the worktree list. `git worktree list` reports `.worktrees/p1`, `.worktrees/mission`
    and so on, and their directory names are *lanes of one repository*, not repositories. An
    earlier version derived the choices from them and offered `p1` and `reliability` as repos to
    create work against — four plausible-looking options that name nothing an operator could ever
    clone. The primary checkout's own directory name is the only one of the pair that is a repo.
    """
    seen = []
    try:
        nm = pathlib.Path(str(rp.primary())).name
        if nm:
            seen.append(nm)
    except Exception:                                              # noqa: BLE001
        pass
    for known in KNOWN_REPOS:
        if known not in seen:
            seen.append(known)
    return seen


def _wt() -> str:
    """Windows Terminal, if present. One window with a titled tab per lane beats five loose
    console windows, and it is already installed — building terminals into the web page would be
    a PTY bridge plus a multiplexer, to arrive somewhere worse than wt already is."""
    import shutil
    return shutil.which("wt") or shutil.which("wt.exe") or ""


def start_all_command(lane_ids, make: bool = True, panes: bool = True):
    """One `wt` invocation for every eligible lane.

    `panes=True` opens one tab and splits it, so all sessions are visible at once — what Paul
    asked for. Alternating vertical/horizontal keeps three or four panes near-square rather than
    degrading into slivers. `panes=False` gives a tab each, which is better for working IN one
    since a Claude session wants the vertical room. Both are offered; neither is imposed.
    """
    args, notes = [], []
    for i, lid in enumerate(lane_ids):
        cmd, f, cwd = launch_command(lid, make=make)
        tail = list(cmd[-2:])                # ["-File", "<lane>.ps1"] — styled, semicolon-free
        if i:
            args.append(";")
        verb = ["new-tab"] if (not i or not panes) else ["split-pane", "-V" if i % 2 else "-H"]
        args += verb + ["--title", f"lane {lid}", "--startingDirectory", str(cwd),
                        "--colorScheme", WT_SCHEME,
                        "powershell", "-NoExit", "-ExecutionPolicy", "Bypass"] + tail
        notes.append(lid)
    return ([_wt()] + args) if args else [], notes


def launch(lane_id: str, dry: bool = False):
    """Claim, then spawn. Returns (ok, message). The claim runs FIRST so a conflicting lane is
    refused before anything is started."""
    import subprocess
    # Refuse BEFORE claiming. A claim is an intent, not a process: a lane whose claim was released
    # while its session was still alive would otherwise accept a second agent into the same
    # worktree — the shared-checkout arrangement this whole model exists to avoid.
    try:
        from factory import sessions as _sess
        running = _sess.live(lane_id)
    except Exception:                                              # noqa: BLE001
        running = []
    if running:
        return False, ("{} already has {} live session(s) ({}) in its worktree — close them first. "
                       "Two agents on one branch is the 41.7% conflict case.").format(
                           lane_id, len(running),
                           ", ".join(str(s["pid"]) + ":" + str(s["status"]) for s in running))
    try:
        claimlib.claim(lane_id, who="launched from tracker")
    except claimlib.ClaimError as exc:
        return False, str(exc)
    try:
        cmd, f, cwd = launch_command(lane_id, make=not dry)
    except claimlib.ClaimError as exc:
        claimlib.release(lane_id)
        return False, str(exc)
    if dry:
        claimlib.release(lane_id)
        return True, f"DRY RUN, nothing started — worktree {cwd.name}, prompt {f.name}"
    try:
        subprocess.Popen(cmd, cwd=str(cwd), close_fds=True)
    except Exception as exc:                                       # noqa: BLE001
        # Roll the claim back: a lane marked running with no session is worse than an unclaimed
        # one, because it blocks its conflicts for nothing.
        claimlib.release(lane_id)
        return False, f"could not start a terminal ({type(exc).__name__}: {exc}); claim released"
    return True, (f"started {lane_id} in a new terminal, in its own worktree "
                  f"({cwd.name}) on branch lane/{lane_id}")


# ---------------------------------------------------------------------------------------------
# ⭐ Ticket runs — the supervised path, routed through `factory.control`.
#
# This is the wiring that decides whether RUN-03 built an assembly line or a sixth unwired module.
# Before it, the only path that actually started an agent was `launch()` above: a generated `.ps1`
# running a bare `claude`, with no preset, no configuration record, no verdict and no ledger row.
# `presets`, `worktrees`, `claims`, `deploy`, `runs` and `blueprint` had **zero consumers between
# them** — just over 2,000 lines of tested machinery nothing called.
#
# ⚠ The terminal is still a terminal. Nothing here replaces the supervised path or pretends to
# watch it; `SupervisedProvider` reports `observable=False`, so the controller records the run as
# UNMEASURABLE rather than inferring an outcome from a window having opened. What changes is that
# the run now leaves a record — which configuration was chosen, which four were not, and under
# what rule — and that record cannot be reconstructed after the fact.

def _ticket_spawn(ticket_id: str):
    """A spawn callable for `SupervisedProvider`: opens the same terminal `launch()` opens.

    Injected rather than built into the provider so this file keeps owning its own `.ps1`/`wt`
    machinery — F10 (semicolons are `wt`'s subcommand separator) lives here and should stay here.
    """
    def spawn(spec, task, wtpath):
        import subprocess as _sp
        d = FACTORY / ".data" / "launch"
        d.mkdir(parents=True, exist_ok=True)
        f = d / f"ticket-{ticket_id}.txt"
        f.write_text(f"{spec.prompt}\n\nTASK:\n{task}\n", encoding="utf-8")
        title = f"ticket {ticket_id}"
        ps1 = _launch_script(title, f"{spec.role} · {spec.model}", f, "38;5;179",
                             model=spec.model, session_name=f"{ticket_id} · {spec.role}")
        wtexe = _wt()
        cmd = ([wtexe, "new-tab", "--title", title, "--startingDirectory", str(wtpath),
                "--colorScheme", WT_SCHEME, "powershell", "-NoExit",
                "-ExecutionPolicy", "Bypass", "-File", str(ps1)]
               if wtexe else
               ["cmd", "/c", "start", title, "powershell", "-NoExit",
                "-ExecutionPolicy", "Bypass", "-File", str(ps1)])
        return f"pid {_sp.Popen(cmd, cwd=str(wtpath), close_fds=True).pid}"
    return spawn


def run_ticket(ticket_id: str, title: str = "", type_id: str = "", task: str = "",
               dry: bool = False):
    """Run one ticket through the controller, supervised. Returns (ok, message).

    ⚠ `pid=None` on the claim is deliberate. The pid this process could record is the *tracker's*,
    not the agent terminal's, so recording it would make the claim look live exactly as long as
    the tracker runs and dead the moment it stops — neither of which is a fact about the agent.
    With no pid, `claims.task_holder` returns HELD_UNVERIFIED and a second launch is **refused**
    with "not being able to look is not proof that nothing is there", which is the correct answer.
    Release it from the Research tab when the session is done.
    """
    ticket = ctrl.Ticket(id=ticket_id.strip(), title=title.strip() or ticket_id.strip(),
                         task=task, type_id=(type_id or None))
    if not ticket.id:
        return False, "no ticket id given"

    if dry:
        el, chosen, rule = ctrl.eligible(ticket)
        if not chosen:
            return False, f"nothing eligible under: {rule}"
        lines = "; ".join(("-> " if x["chosen"] else "") + x["id"] for x in el)
        return True, (f"DRY RUN, nothing started — worktree would be .worktrees/{ticket.key}, "
                      f"rule: {rule}; eligible: {lines}")

    provider = provlib.SupervisedProvider(spawn=_ticket_spawn(ticket.key))
    controller = ctrl.RunController(
        provider,
        claim=lambda key: claimlib.task_claim(key, pid=None, who="tracker ticket run",
                                              note=ticket.title[:120]))
    try:
        res = controller.run(ticket)
    except claimlib.ClaimError as exc:
        return False, str(exc)
    except Exception as exc:                                       # noqa: BLE001
        return False, f"{type(exc).__name__}: {exc}"

    if res.verdict.value == "ERROR":
        return False, f"{ticket.id}: {res.detail}"
    if res.verdict.value == "NOT_RUN":
        return False, f"{ticket.id}: {res.detail}"
    return True, (f"{ticket.id} started under preset '{res.preset_id}' in .worktrees/"
                  f"{ticket.key} — verdict {res.verdict.value} at dispatch (a supervised run's "
                  f"outcome is not observable from here). run {res.run_id}")


def _answer_path(prompt: pathlib.Path) -> pathlib.Path:
    """docs/research/R5-build-velocity.md -> docs/research/answers/R5-answer-build-velocity.md

    Derived from the PROMPT filename, never from anything the browser sends, so the request
    cannot choose where a file lands.
    """
    parts = prompt.stem.split("-", 1)
    tail = parts[1] if len(parts) > 1 else "answer"
    return prompt.parent / "answers" / f"{parts[0]}-answer-{tail}.md"


#: Uploads are capped. An answer larger than this is not an answer, it is an accident.
MAX_UPLOAD = 2 * 1024 * 1024


def _parse_multipart(raw: bytes, content_type: str) -> dict:
    """Return {field_name: text} for a multipart/form-data body.

    Hand-rolled because Python 3.13 removed `cgi`. Deliberately minimal: this serves one form on
    loopback, so it handles the parts that form sends and refuses to guess at anything else.
    Filenames are read but NOT used to build a path — the destination is derived from the prompt
    stem, so an upload cannot choose where it lands.
    """
    marker = "boundary="
    if marker not in content_type:
        return {}
    boundary = content_type.split(marker, 1)[1].strip().strip('"')
    sep = b"--" + boundary.encode()
    out = {}
    for chunk in raw.split(sep):
        if not chunk.strip(b"-\r\n"):
            continue
        head, _, payload = chunk.partition(b"\r\n\r\n")
        if not _:
            continue
        headers = head.decode("utf-8", "replace")
        m = re.search(r'name="([^"]+)"', headers)
        if not m:
            continue
        out[m.group(1)] = payload.rstrip(b"\r\n").decode("utf-8", "replace")
    return out


def _log_answer_attempt(stem, ctype, n, ok, msg):
    """Every upload attempt, to disk.

    The only diagnostic this path had was a print() to stdout, and the tracker is normally started
    with -WindowStyle Hidden — so a refused upload was completely invisible: no file appeared, no
    message was seen, and the honest report was "it does not persist". A failure nobody can see is
    indistinguishable from one that did not happen.
    """
    try:
        d = FACTORY / ".data"
        d.mkdir(parents=True, exist_ok=True)
        import datetime as _dt
        rec = {"at": _dt.datetime.now().isoformat(timespec="seconds"),
               "stem": stem, "content_type": ctype, "bytes": n, "ok": bool(ok), "msg": str(msg)}
        with (d / "answer-log.jsonl").open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec) + chr(10))
    except Exception:                                              # noqa: BLE001
        pass          # logging must never be the reason an upload fails


def save_answer(stem: str, body: str):
    """Write a pasted research answer. Returns (ok, message).

    Refuses to overwrite: an answer already filed is evidence, and silently replacing it would
    lose the first one. Same write-once rule as the verdict store.
    """
    rdir = FACTORY / "docs" / "research"
    match = next((f for f in rdir.glob("R[0-9]*.md") if f.stem == stem), None)
    if match is None:
        return False, f"no research prompt with stem {stem!r}"
    if not body.strip():
        return False, "nothing pasted — an empty answer is not an answer"
    dest = _answer_path(match)
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        return False, f"{dest.name} already exists — refusing to overwrite a filed answer"
    dest.write_text(body.replace("\r\n", "\n"), encoding="utf-8")
    return True, f"saved {dest.name} ({len(body):,} chars) — the gate will see it on next measure"

#: The generators that write into docs/artifacts/agent-factory.html, in the order they must run:
#: the figure and the plan change the file, and the tracker section carries the headline that
#: factory.schedule later reads out of git, so it goes last.
_GENERATORS = (
    ("figure", ["scripts/build_figure_lastwrite.py", "--insert"]),
    ("plan", ["scripts/build_plan.py", "--insert"]),
    ("tracker", ["scripts/build_tracker.py"]),
)


def sync_artifact():
    """Regenerate every generated section of the artifact FILE. Returns (ok, message).

    Deliberately reports the byte delta rather than "done": a generator that silently did
    nothing and a generator that worked look identical otherwise, and this whole project is
    about not letting those two be the same signal.
    """
    global _SYNC_MSG
    import subprocess
    art = FACTORY / "docs" / "artifacts" / "agent-factory.html"
    before = art.stat().st_size if art.is_file() else 0
    notes, ok = [], True
    for label, args in _GENERATORS:
        r = subprocess.run([sys.executable, *args], cwd=FACTORY, capture_output=True,
                           text=True, encoding="utf-8", errors="replace")
        if r.returncode != 0:
            ok = False
            notes.append(f"{label} FAILED: {(r.stderr or r.stdout).strip().splitlines()[-1][:120]}")
        else:
            notes.append(label)
    after = art.stat().st_size if art.is_file() else 0
    delta = after - before
    tail = "no change" if delta == 0 else f"{delta:+,} bytes"
    return ok, f"artifact file synced ({', '.join(notes)}) — {tail}"



def hot_reload():
    """Re-import the probe modules and rebind the names this script imported by value.

    `from x import y` binds y once. importlib.reload() replaces the module object but does NOT
    rebind names already imported into this namespace, so reloading without this rebinding step
    is a no-op that looks like it worked — which is worse than not having the button.

    Returns (ok, message). A syntax error mid-edit is reported on the page rather than crashing
    the server, because the whole point is to keep editing without restarting.
    """
    global _RELOADED_AT
    import importlib
    try:
        # Reload every factory module this file imports, in dependency order. Both the set and
        # the order are DERIVED (see `_HOT`) — nothing here is a list to keep in step by hand.
        mods = {}
        for name in _HOT:
            mods[name] = importlib.reload(importlib.import_module(name))

        # Rebind only what was imported BY VALUE. `import x as y` aliases point at the module
        # object, which `reload` re-executes in place, so they are already current; a
        # `from x import y` name is a stale copy until it is re-read. That list is derived too.
        g, rebound, missing = globals(), 0, []
        for mod, names in _value_imports():
            m = mods.get(f"factory.{mod}")
            if m is None:
                continue
            for n in names:
                if hasattr(m, n):
                    g[n] = getattr(m, n)
                    rebound += 1
                else:
                    missing.append(f"{mod}.{n}")

        _RELOADED_AT = datetime.datetime.now()
        gates = len(mods["factory.readiness"].GATES) if "factory.readiness" in mods else 0
        # ⚠ Counted from what actually ran, never from a literal. The old message added two
        # hand-maintained list lengths and was wrong by 10 for a while, and would not have moved
        # even while `factory.dispatch` was skipped entirely.
        msg = f"reloaded {len(mods)} modules, rebound {rebound} names, {gates} gates"
        if missing:
            # A name this file imports that its module no longer exports. The page keeps serving
            # the stale value, so say so rather than reporting a clean reload.
            msg += f" — ⚠ {len(missing)} name(s) no longer exported: {', '.join(missing[:4])}"
        return True, msg
    except Exception as exc:                                          # noqa: BLE001
        return False, f"{type(exc).__name__}: {exc}"


CHIP = {PASS: ("pass", "pass"), FAIL: ("fail", "fail"),
        UNMEASURABLE: ("unmeas", "unmeasurable"), NOT_RUN: ("notrun", "not run")}

CSS = """
:root{--paper:#faf9f7;--ink:#16150f;--ink2:#4a473d;--ink3:#84806f;--rule:#e2ddd2;
 --raise:#f2efe8;--pass:#1f7a4d;--fail:#b3341f;--unmeas:#a06a12;--notrun:#84806f;--accent:#2b4c9b}
@media(prefers-color-scheme:dark){:root{--paper:#12120f;--ink:#f2f0ea;--ink2:#b8b4a8;
 --ink3:#7d7a6e;--rule:#2b2a24;--raise:#1b1a16;--pass:#5cc38a;--fail:#f2795e;--unmeas:#e0aa4a;
 --notrun:#7d7a6e;--accent:#7ba0f0}}
*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--ink);
 font:15px/1.6 ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif}
.wrap{max-width:1100px;margin:0 auto;padding:34px 22px 70px}
h1{font-size:27px;margin:0 0 4px;letter-spacing:-.01em}
.sub{color:var(--ink3);font-size:13px;font-family:ui-monospace,"Cascadia Code",Consolas,monospace}
.head{border-bottom:2px solid var(--ink);padding-bottom:16px;margin-bottom:24px}
.score{display:flex;align-items:baseline;gap:12px;margin:18px 0 8px}
.score b{font-size:40px;line-height:1;letter-spacing:-.02em}
.score span{color:var(--ink2);font-size:15px}
.bar{height:7px;background:var(--rule);position:relative;margin:10px 0 6px}
.bar i{position:absolute;inset:0 auto 0 0;background:var(--pass);display:block}
.phase{margin:30px 0 0;border:1px solid var(--rule);background:var(--raise)}
.phase>header{display:flex;justify-content:space-between;align-items:baseline;gap:14px;
 padding:13px 16px;border-bottom:1px solid var(--rule);flex-wrap:wrap}
.phase h2{font-size:17px;margin:0}
.count{font-family:ui-monospace,monospace;font-size:11.5px;letter-spacing:.09em;
 text-transform:uppercase;color:var(--ink3);border:1px solid var(--rule);padding:2px 7px}
.g{padding:15px 16px;border-bottom:1px solid var(--rule);display:grid;
 grid-template-columns:104px 1fr;gap:14px}
.g:last-child{border-bottom:0}
.chip{font-family:ui-monospace,monospace;font-size:10.5px;letter-spacing:.09em;
 text-transform:uppercase;border:1px solid currentColor;padding:3px 7px;display:inline-block}
.chip.pass{color:var(--pass)}.chip.fail{color:var(--fail)}
.chip.unmeas{color:var(--unmeas)}.chip.notrun{color:var(--notrun)}
.q{font-weight:600}
.hl{color:var(--ink2);margin-top:2px}
ul{margin:8px 0 0 17px;padding:0;font-size:13.5px;color:var(--ink3);line-height:1.55}
li{margin:2px 0}
.why{margin-top:7px;font-size:12.5px;color:var(--ink3);font-style:italic}
.src{margin-top:6px;font-family:ui-monospace,monospace;font-size:11.5px;color:var(--ink3)}
footer{margin-top:34px;padding-top:16px;border-top:1px solid var(--rule);
 color:var(--ink3);font-size:13px}
code{font-family:ui-monospace,monospace;background:var(--raise);padding:1px 5px;
 border:1px solid var(--rule);font-size:12.5px}
@media(max-width:620px){.g{grid-template-columns:1fr}}
.t{padding:12px 16px;border-bottom:1px solid var(--rule);display:grid;
 grid-template-columns:78px 26px 1fr;gap:12px;align-items:start}
.t:last-child{border-bottom:0}
.st{font-family:ui-monospace,monospace;font-size:10px;letter-spacing:.09em;text-transform:uppercase;
 border:1px solid currentColor;padding:2px 5px;display:inline-block;white-space:nowrap}
.st.done{color:var(--pass)}.st.ready{color:var(--accent)}
.st.blocked{color:var(--ink3)}.st.declared{color:var(--unmeas)}
.sz{font-family:ui-monospace,monospace;font-size:11px;color:var(--ink3);text-align:center;
 border:1px solid var(--rule);padding:1px 0}
.tt{font-weight:600}
.tw{font-size:13px;color:var(--ink3);margin-top:3px;line-height:1.5}
.dep{font-family:ui-monospace,monospace;font-size:11.5px;color:var(--ink3);margin-top:4px}
.own{font-size:12px;color:var(--unmeas);margin-top:3px}
.par{border:1px solid var(--accent);background:var(--raise);padding:15px 17px;margin:26px 0 0}
.par h3{margin:0 0 8px;font-size:15px}
.par ul{margin:0 0 0 17px;font-size:14px;color:var(--ink2)}
.par li{margin:3px 0}
"""


def e(t) -> str:
    return html.escape(str(t), quote=False)


def _tok(n) -> str:
    """302442227 -> 302M. Nine-digit token counts are read wrong by a factor of ten at a glance.

    Never rounds to zero: a lane that spent 400 tokens must not render as `0k`, because "cheap"
    and "nothing ran" are different findings and this panel exists to keep them apart.
    """
    n = int(n or 0)
    for div, suf in ((1_000_000_000, "B"), (1_000_000, "M"), (1_000, "k")):
        if n >= div:
            return f"{n / div:.2f}{suf}" if n < div * 10 else f"{n / div:.0f}{suf}"
    return str(n)


def render(when: datetime.datetime, tab: str = "tickets", team: str = "",
           view: str = "now", inspect: str = "", q: str = "",
           panes: str = "", lay: str = "1", popout: bool = False) -> str:
    # Research needs no measurement, and a full measure is ~10s of probes. Paying that to read a
    # prompt was the main reason this page felt slow.
    # ⛔ `switchboard` joins the same list as `research`, and for a stronger reason.
    # `measure()` reaches `board.board()`, which did not return inside 120 s when timed on
    # 2026-09-01. A command page that pays that per refresh is a page nobody opens, which is
    # the failure control-room.md §3 already records against this tracker at ~19 s.
    results = measure() if tab not in ("research", "switchboard") else []
    n = sum(1 for _, r in results if r.ok)
    total = len(results)
    pct = round(100 * n / total) if total else 0
    nav = "".join(
        f'<a href="{href}" style="display:inline-block;padding:7px 14px;margin-right:6px;'
        f'font-size:13px;text-decoration:none;border:1px solid var(--rule);border-radius:3px;'
        f'background:{"var(--ink)" if tab == key else "var(--raise)"};'
        f'color:{"var(--paper)" if tab == key else "var(--ink2)"}">{label}</a>'
        for key, href, label in TABS)

    o = ['<!doctype html><html lang="en"><head><meta charset="utf-8">',
         '<meta name="viewport" content="width=device-width,initial-scale=1">',
         '<title>Agent Factory</title>', f"<style>{CSS}</style></head><body><div class='wrap'>"]
    w = o.append
    w(f'<nav style="padding:22px 0 4px">{nav}</nav>')
    # Reload lives in the shared header, not on one tab. It was gates-only until
    # 2026-08-29, which meant changing the landing tab silently removed it.
    # ⚠ Refresh RE-MEASURES; reload RE-READS THE CODE. Keep the distinction visible —
    # conflating them is how this page sat on a stale gate list for hours.
    _rl = (f'code reloaded {_RELOADED_AT.strftime("%H:%M:%S")}'
           if _RELOADED_AT else 'code as at server start')
    w('<div style="padding:2px 0 10px">'
      '<a href="/reload" style="display:inline-block;padding:6px 12px;border:1px solid '
      'var(--rule);border-radius:3px;background:var(--raise);color:var(--ink);'
      'text-decoration:none;font-size:13px">&#8635; reload code &amp; re-measure</a>'
      '<a href="/sync" style="display:inline-block;margin-left:8px;padding:6px 12px;'
      'border:1px solid var(--rule);border-radius:3px;background:var(--raise);'
      'color:var(--ink);text-decoration:none;font-size:13px">&#8681; sync artifact file</a>'
      f'<span style="color:var(--ink3);font-size:12.5px">&nbsp; refresh re-measures &middot; {_rl}</span>'
      '</div>')
    if _SYNC_MSG:
        okc = 'var(--pass)' if _SYNC_MSG[0] else 'var(--fail)'
        w(f'<div class="sub" style="color:{okc};font-size:13px">{e(_SYNC_MSG[1])}</div>')
    if _ANSWER_MSG:
        okc = 'var(--pass)' if _ANSWER_MSG[0] else 'var(--fail)'
        w(f'<div class="sub" style="color:{okc};font-size:13px">{e(_ANSWER_MSG[1])}</div>')
    if _CLAIM_MSG:
        okc = 'var(--pass)' if _CLAIM_MSG[0] else 'var(--fail)'
        w(f'<div class="sub" style="color:{okc};font-size:13px">{e(_CLAIM_MSG[1])}</div>')
    if _RELOAD_MSG:
        okc = 'var(--pass)' if _RELOAD_MSG[0] else 'var(--fail)'
        w(f'<div class="sub" style="color:{okc};font-size:13px">{e(_RELOAD_MSG[1])}</div>')

    if tab == "tickets":
        # ------------------------------------------------------------------ tickets
        # Progress on THIS project, read from the same append-only store the board
        # reads. No second copy of the truth: if a ticket is closed anywhere, it is
        # closed here. Counts are computed per render, never cached.
        import collections as _c
        try:
            from factory.tasks import TaskStore as _TS
            # ⛔ `rp.data()` and not a `__file__`-relative path. This read the store out of
            # whichever checkout the server happened to run from, so serving the tracker from a
            # worktree showed ZERO closed tickets on the Tickets tab -- an empty store rendering
            # as "no progress" rather than as "no store". Caught by the widened structural guard
            # in tests/test_repo_root.py, not by anyone looking at the page.
            _tasks = _TS(rp.data() / "tasks.jsonl").all()
        except Exception as _exc:                                  # noqa: BLE001
            _tasks = None
            _terr = "%s: %s" % (type(_exc).__name__, _exc)

        # ---------------------------------------------------------------- inbox
        # ⭐ Questions agents wrote when they blocked. `sessions.blocked()` has been
        # correct since 2026-08-23 — it reads JOBS/*/state.json so a question outlives
        # the process that asked it — and until now NOTHING RENDERED IT. Its only two
        # callers were launch.py (which prints the count, inside a 9-minute command)
        # and a roadmap note. So the August fix took the display from "2 of 5 shown"
        # to "0 of 5 shown", and two credential requests sat unanswered and unseen.
        #
        # Rendered FIRST, above the ticket counts, because a question waiting on a
        # human outranks any amount of progress reporting.
        #
        # ⚠ The panel renders even when the count is zero. An inbox that disappears
        # when empty cannot be told apart from an inbox that is not wired up — which
        # is the exact failure this panel exists to end. ZERO is a measurement; a
        # missing panel is not.
        try:
            from factory import sessions as _sx
            _q, _qerr = _sx.blocked(), None
        except Exception as _exc:                                      # noqa: BLE001
            _q, _qerr = None, "%s: %s" % (type(_exc).__name__, _exc)

        def _age(rec):
            """`waiting_since` is a unix timestamp (float), not an ISO date string."""
            try:
                d = datetime.datetime.now().timestamp() - float(rec.get("waiting_since"))
                if d < 3600:
                    return "%dm" % (d // 60)
                if d < 86400:
                    return "%dh" % (d // 3600)
                return "%dd" % (d // 86400)
            except Exception:                                          # noqa: BLE001
                return "?"

        w('<div class="par" style="margin:0 0 18px;border-color:var(--unmeas)">')
        if _qerr is not None:
            w('<h3 style="margin:0;color:var(--fail)">Inbox unreadable &mdash; %s</h3>' % e(_qerr))
        elif not _q:
            w('<h3 style="margin:0;color:var(--pass)">Inbox: 0 questions waiting</h3>'
              '<p style="font-size:13px;color:var(--ink3);margin:6px 0 0">Read from '
              '<code>~/.claude/jobs/*/state.json</code> on every refresh. Shown at zero on '
              'purpose &mdash; a panel that vanishes when empty is indistinguishable from one '
              'that was never wired.</p>')
        else:
            _live = [r for r in _q if r.get("answerable")]
            w('<h3 style="margin:0;color:var(--unmeas)">Inbox &mdash; %d question(s) waiting '
              '&middot; %d answerable</h3>' % (len(_q), len(_live)))
            w('<p style="font-size:13px;color:var(--ink3);margin:6px 0 10px">Oldest first, '
              'across every session alive or dead &mdash; a question is a fact on disk and '
              'outlives the process that asked it. <b>Liveness says how to answer, never '
              'whether to show.</b></p>')
            for _r in _q:
                _ok = bool(_r.get("answerable"))
                _col = "var(--pass)" if _ok else "var(--notrun)"
                _tag = "answerable" if _ok else "orphaned &mdash; %s" % e(str(_r.get("state") or "?"))
                _who = e(str(_r.get("name") or _r.get("lane") or _r.get("job_id") or "?")[:28])
                _txt = " ".join(str(_r.get("needs") or "").split()) or "(no question text)"
                w('<div style="border-left:3px solid %s;padding:2px 0 2px 11px;margin:0 0 11px">' % _col)
                w('<div style="font-size:11px;color:%s;font-family:ui-monospace,monospace">'
                  '%s &middot; waited %s &middot; %s</div>' % (_col, _who, _age(_r), _tag))
                w('<div style="font-size:14px;color:var(--ink);margin:3px 0 0">%s</div>' % e(_txt[:400]))
                _sug = " ".join(str(_r.get("suggested_reply") or "").split())
                if _sug:
                    w('<div style="font-size:12.5px;color:var(--ink3);margin:3px 0 0">'
                      'suggested reply: <i>%s</i></div>' % e(_sug[:160]))
                w('</div>')
        w('</div>')

        # ---------------------------------------------------------------- run a ticket
        # ⭐ The assembly line, and the first surface from which a preset can actually start
        # anything. Rendered with the recorded runs beside it on purpose: a record nobody reads is
        # decoration, and this estate has already shipped an inbox that was correct for six days
        # while nothing displayed it.
        try:
            _runs_seen = [evlib.fold(r) for r in evlib.runs()]
            _rerr = None
        except Exception as _exc:                                      # noqa: BLE001
            _runs_seen, _rerr = [], "%s: %s" % (type(_exc).__name__, _exc)

        w('<div class="par" style="margin:0 0 18px">')
        w('<h3 style="margin-top:0">Run a ticket</h3>')
        w('<p style="font-size:13px;color:var(--ink2);margin:0 0 10px">Ticket &rarr; preset '
          '&rarr; TeamSpec &rarr; one agent in its own worktree &rarr; a verdict assigned by '
          '<code>GreenContract</code> &rarr; a row in <code>.data/runs.jsonl</code>. The terminal '
          'is supervised, so the controller records <b>UNMEASURABLE</b> at dispatch rather than '
          'inferring an outcome from a window having opened &mdash; <b>you</b> are the cap, the '
          'reaper and the spend ceiling. What is new is that the run leaves a record of '
          '<i>which configuration was chosen and which were not</i>, which cannot be '
          'reconstructed afterwards.</p>')
        w('<form method="POST" action="/run-ticket" style="display:flex;gap:7px;flex-wrap:wrap;'
          'align-items:center;font-size:13px">')
        w('<input name="ticket" placeholder="ticket id" required '
          'style="padding:6px 9px;border:1px solid var(--rule);border-radius:5px;'
          'background:var(--bg);color:var(--ink);font-family:ui-monospace,monospace;width:200px">')
        w('<input name="title" placeholder="what it asks for" '
          'style="padding:6px 9px;border:1px solid var(--rule);border-radius:5px;'
          'background:var(--bg);color:var(--ink);flex:1;min-width:220px">')
        w('<select name="type" style="padding:6px 9px;border:1px solid var(--rule);'
          'border-radius:5px;background:var(--bg);color:var(--ink)">')
        w('<option value="">(no type &mdash; all %d eligible, cheapest taken)</option>'
          % len(presetlib.PRESETS))
        for _p in presetlib.PRESETS:
            w('<option value="%s">%s &middot; %s &middot; $%.2f &middot; verifier %s</option>'
              % (e(_p.type_id), e(_p.type_id), e(_p.model), _p.budget_usd,
                 e(_p.verifier_state)))
        w('</select>')
        w('<button name="dry" value="1" style="padding:6px 12px;border:1px solid var(--rule);'
          'border-radius:5px;background:var(--bg);color:var(--ink2);cursor:pointer">plan only'
          '</button>')
        w('<button name="dry" value="" style="padding:6px 14px;border:1px solid var(--pass);'
          'border-radius:5px;background:var(--bg);color:var(--pass);cursor:pointer">start</button>')
        w('</form>')

        _un = presetlib.unwired()
        if _un:
            w('<p style="font-size:12.5px;color:var(--unmeas);margin:10px 0 0">&#9888; %d of %d '
              'presets name a verifier nobody has wired (%s). A run under one of those ends '
              'UNMEASURABLE however cleanly it goes &mdash; nothing can say whether the ticket\'s '
              'work was done, and reporting that as a pass is the collapse this whole page '
              'exists to refuse.</p>'
              % (len(_un), len(presetlib.PRESETS), e(", ".join(p.type_id for p in _un))))

        w('<div style="margin-top:14px;border-top:1px solid var(--rule);padding-top:11px">')
        if _rerr is not None:
            w('<div style="color:var(--fail);font-size:13px">event stream unreadable &mdash; %s</div>'
              % e(_rerr))
        elif not _runs_seen:
            w('<div style="font-size:13px;color:var(--ink3)">No runs recorded in '
              '<code>.data/events.jsonl</code>. That is <b>NOT-RECORDED</b>, not zero: nothing '
              'has executed a TeamSpec through the controller on this machine yet. Shown at zero '
              'on purpose &mdash; same rule as the inbox above.</div>')
        else:
            w('<div style="font-size:12.5px;color:var(--ink3);margin:0 0 8px">%d recorded run(s) '
              '&middot; newest last &middot; read from <code>.data/events.jsonl</code></div>'
              % len(_runs_seen))
            for _r in _runs_seen[-8:]:
                _v = str(_r.get("verdict") or "no verdict recorded")
                _vc = {"PASS": "var(--pass)", "FAIL": "var(--fail)",
                       "UNMEASURABLE": "var(--unmeas)", "ERROR": "var(--fail)",
                       "NOT_RUN": "var(--notrun)"}.get(_v, "var(--notrun)")
                _el = _r.get("eligible") or _r.get("considered") or []
                _not = [x.get("id") for x in _el if not x.get("chosen")]
                w('<div style="border-left:3px solid %s;padding:2px 0 2px 11px;margin:0 0 10px">'
                  % _vc)
                w('<div style="font-family:ui-monospace,monospace;font-size:11.5px;color:%s">'
                  '%s &middot; %s &middot; %s</div>'
                  % (_vc, e(str(_r.get("ticket") or "?")), e(_v),
                     e(str(_r.get("chosen") or "no preset chosen"))))
                w('<div style="font-size:12.5px;color:var(--ink3);margin:2px 0 0">rule: %s</div>'
                  % e(str(_r.get("rule") or "?")))
                if _not:
                    w('<div style="font-size:12.5px;color:var(--ink3);margin:1px 0 0">'
                      'eligible, not taken: %s</div>' % e(", ".join(str(x) for x in _not)))
                w('</div>')
        w('</div>')
        w('</div>')

        w('<div class="head">')
        w('<h1>Agent Factory &mdash; where the work stands</h1>')
        if _tasks is None:
            w('<div class="sub" style="color:var(--fail)">could not read the task store &mdash; '
              + e(_terr) + '</div></div>')
        else:
            # ⚠ Every prefix must appear here. A prefix that does not is not dropped —
            # it lands in "other", which is COUNTED AND SHOWN below. On 2026-08-29 RUN
            # was missing and 7 tickets vanished from the total while the page still
            # reported a confident "3 of 64".
            _lane = lambda t: ("run" if t.title.startswith("RUN-")
                               else "platform" if t.title.startswith("CIP-") and int(t.title.split("-")[1].split()[0]) <= 20
                               else "factory" if t.title.startswith("CIP-")
                               else "absorption" if t.title.startswith("AB-")
                               else "observed" if t.title.startswith("OBS-")
                               else "other")
            _done = lambda t: t.status in ("done", "abandoned")
            _by = _c.defaultdict(list)
            for _t in _tasks:
                _by[_lane(_t)].append(_t)
            _tracked = [t for t in _tasks if _lane(t) != "other"]
            _unclassified = [t for t in _tasks if _lane(t) == "other"]
            _nd = sum(1 for t in _tracked if _done(t))
            w('<div class="sub">%d of %d tickets closed &middot; re-read from '
              '<code>.data/tasks.jsonl</code> on every refresh &middot; the board is a view of this '
              'same store, never a second copy</div>' % (_nd, len(_tracked)))
            w('</div>')

            _order = [("run", "Ticket in, team runs it",
                       "acceptance is a gate id in `python -m factory.launch` — done is a verdict moving"),
                      ("platform", "Client Intake Platform", "the questionnaire becomes the acceptance test"),
                      ("factory", "Factory hardening", "no dependencies; none on the critical path"),
                      ("observed", "Observed in flight", "surfaced mid-work; each carries its promotion rule"),
                      ("absorption", "Absorption backlog", "conclusions reached and never actioned")]
            for _k, _label, _why in _order:
                _rows = _by.get(_k) or []
                if not _rows:
                    continue
                _d = sum(1 for t in _rows if _done(t))
                _frac = _d / len(_rows) if _rows else 0
                _col = "var(--pass)" if _frac == 1 else ("var(--unmeas)" if _frac else "var(--fail)")
                w('<div class="par" style="margin-top:14px">')
                w('<h3 style="margin-top:0">%s <span style="font-weight:400;color:%s;'
                  'font-family:ui-monospace,monospace;font-size:13px">%d of %d</span></h3>'
                  % (e(_label), _col, _d, len(_rows)))
                w('<div style="height:7px;background:var(--rule);border-radius:3px;margin:6px 0 8px">'
                  '<div style="height:7px;width:%.1f%%;background:%s;border-radius:3px"></div></div>'
                  % (_frac * 100, _col))
                w('<p style="font-size:13px;color:var(--ink2);margin:0 0 8px">%s</p>' % e(_why))
                _open = [t for t in _rows if not _done(t)][:6]
                if _open:
                    w('<div style="font-family:ui-monospace,monospace;font-size:11.5px;'
                      'color:var(--ink2);line-height:1.7">')
                    for _t in _open:
                        w('&middot; %s<br>' % e(_t.title[:96]))
                    if len(_rows) - _d > len(_open):
                        w('<span style="opacity:.6">&hellip; and %d more open</span>'
                          % (len(_rows) - _d - len(_open)))
                    w('</div>')
                w('</div>')

            if _unclassified:
                w('<div class="par" style="margin-top:14px;border-color:var(--unmeas)">')
                w('<h3 style="margin-top:0;color:var(--unmeas)">%d ticket(s) this page cannot classify</h3>'
                  % len(_unclassified))
                w('<p style="font-size:13px;color:var(--ink2);margin:0 0 6px">Shown rather than '
                  'dropped. A prefix missing from the lane map is a fact about this page, not a '
                  'reason to omit the ticket &mdash; and omitting them is how the total read '
                  '&ldquo;3 of 64&rdquo; while the store held 5 of 68.</p>')
                w('<div style="font-family:ui-monospace,monospace;font-size:11.5px;color:var(--ink2)">')
                for _t in _unclassified[:8]:
                    w('&middot; %s<br>' % e(_t.title[:92]))
                w('</div></div>')

            w('<div class="par" style="margin-top:22px">')
            w('<h3 style="margin-top:0">What this page does not tell you</h3>')
            w('<p style="font-size:13px;color:var(--ink2);margin:0">A closed ticket is a claim that '
              'work happened, not evidence that it worked. For that, see the <b>Gates</b> tab &mdash; '
              'it asks whether a team can run a migration unattended, which is the acceptance test '
              'this whole project is measured by. Tickets moving while gates stay red is the '
              'failure mode worth watching for.</p>')
            w('</div>')

    if tab == "gates":
        w('<div class="head">')
        w('<h1>Can a team run a migration unattended?</h1>')
        w(f'<div class="sub">measured {e(when.strftime("%Y-%m-%d %H:%M:%S"))} local &middot; '
          f'refresh this page to re-measure</div>')
        # Refresh re-measures; reload re-reads the CODE. They are different things and the page says
        # so, because conflating them is exactly how this page sat on a 23-gate list for hours.
        # The published page is a SEPARATE copy. Saying so on the page is the cheapest possible
        # guard against reading a stale artifact as current state — which already happened.
        w('<div class="sub" style="color:var(--ink3);font-size:12.5px;margin-top:4px">'
          'sync rewrites the local <code>docs/artifacts/agent-factory.html</code>. '
          'Publishing to claude.ai is a separate step &mdash; the published page only moves when '
          'someone republishes it.</div>')
        # ---------------------------------------------------------- launch readiness
        # ABOVE the score deliberately. The score answers "how many gates pass"; an operator
        # standing here is asking "may I press start", and those have different answers today —
        # RUN is yes while LEAVE and TRUST are no. A single percentage cannot say that, so a
        # reader takes 30% to mean "not yet" and does not start the supervised run that is both
        # safe and the only way `finishes` and `succeeds` can stop being UNMEASURABLE.
        #
        # `results` is reused rather than re-measured: same render, same instant. See
        # launch._verdicts — reuse is the caller's promise, and this is the only caller that
        # can make it.
        lvls = launchlib.levels(results)
        LCHIP = {launchlib.SUPERVISED: "pass", launchlib.SUPERVISED_BLOCKED: "fail",
                 launchlib.UNATTENDED: "pass", launchlib.UNATTENDED_BLOCKED: "fail",
                 launchlib.TRUSTED: "pass", launchlib.TRUST_BLOCKED: "fail",
                 launchlib.UNGATED: "notrun"}
        w('<div class="par" style="border-color:var(--ink);margin:20px 0 0">')
        w('<h3 style="margin-bottom:4px">Three questions, not one number</h3>')
        w('<p style="font-size:13px;color:var(--ink3);margin:0 0 4px">Read down until the answer '
          'stops being yes. Each level is strictly harder than the one above it, and they are '
          'independent &mdash; a run can finish cleanly and still produce something nothing can '
          'check. Measured on the same pass as the gates below.</p>')
        for lv in lvls:
            cls = LCHIP.get(lv["state"], "notrun")
            w('<div style="display:grid;grid-template-columns:170px 1fr;gap:14px;'
              'padding:13px 0 0;margin-top:11px;border-top:1px solid var(--rule)">')
            w(f'<div><span class="chip {cls}">{e(lv["state"])}</span></div>')
            w('<div>')
            w(f'<div class="q">{e(lv["question"])}</div>')
            w(f'<div class="hl" style="font-size:13.5px">{e(lv["means"])}</div>')
            # The RUN level is answered by facts about this machine, not by gates — no gate
            # measures whether a human can see the run — so it shows its checks, pass or fail.
            for c in lv.get("checks") or []:
                col = "var(--pass)" if c["ok"] else "var(--fail)"
                w(f'<div style="font-family:ui-monospace,monospace;font-size:11.5px;margin-top:4px">'
                  f'<span style="color:{col}">{"OK" if c["ok"] else "NO"}</span> '
                  f'<span style="color:var(--ink2)">{e(c["what"])}</span> '
                  f'<span style="color:var(--ink3)">&mdash; {e(c["detail"])}</span></div>')
            if lv["blockers"]:
                names = " &middot; ".join(e(b["gate"]) for b in lv["blockers"])
                w(f'<div class="dep">blocked by: {names}</div>')
                w('<ul>' + "".join(
                    f'<li><b>{e(b["gate"])}</b> <span style="color:var(--fail)">'
                    f'{e(b["verdict"])}</span> &mdash; {e(b["headline"])}</li>'
                    for b in lv["blockers"]) + '</ul>')
            w(f'<div class="why">{e(lv["not_means"])}</div>')
            w('</div></div>')
        # UNGATED is not 0%. A team with no contract has nothing to measure, and rendering it as
        # a percentage would invent progress — the same distinction the board draws between a
        # gate that FAILED and one that was never run.
        w('<div style="padding:13px 0 0;margin-top:11px;border-top:1px solid var(--rule)">')
        for t in launchlib.teams(results):
            head = (f'{t["passing"]} of {t["of"]}' if t["passing"] is not None else "no contract")
            tc = LCHIP.get(t["state"], "notrun")
            w(f'<div style="font-size:13px;margin:0 0 5px">'
              f'<span class="chip {tc}">{e(t["state"])}</span> '
              f'<b>{e(t["team"])}</b> '
              f'<span style="color:var(--ink3);font-family:ui-monospace,monospace;'
              f'font-size:11.5px">{e(head)}</span>'
              + (f'<div style="color:var(--ink3);font-size:12px;margin:1px 0 0 2px">'
                 f'{e(t["note"])}</div>' if t["note"] else '') + '</div>')
        w('</div>')
        w('</div>')

        w(f'<div class="score"><b>{n}</b><span>of {total} gates pass</span></div>')
        w(f'<div class="bar"><i style="width:{pct}%"></i></div>')
        w(f'<div class="sub">factory {e(FACTORY)}<br>connectors {e(CONNECTORS)}</div>')
        w('</div>')

        for phase, title in PHASES.items():
            rows = [(g, r) for g, r in results if g.phase == phase]
            if not rows:
                continue
            ok = sum(1 for _, r in rows if r.ok)
            w('<section class="phase"><header>')
            w(f'<h2>{e(title)}</h2><span class="count">{ok} of {len(rows)}</span>')
            w('</header>')
            for g, r in rows:
                cls, label = CHIP[r.verdict]
                w('<div class="g">')
                w(f'<div><span class="chip {cls}">{label}</span></div>')
                w('<div>')
                w(f'<div class="q">{e(g.question)}</div>')
                w(f'<div class="hl">{e(r.headline)}</div>')
                if r.evidence:
                    w('<ul>' + "".join(f"<li>{e(x)}</li>" for x in r.evidence) + '</ul>')
                w(f'<div class="why">{e(g.why)}</div>')
                if r.source:
                    w(f'<div class="src">{e(r.source)}</div>')
                w('</div></div>')
            w('</section>')

    if tab == "gates":
        # ------------------------------------------------------------------ the work
        rows = board()
        n_done = sum(1 for _, _, st, _ in rows if st == DONE)
        ready = [(g, r) for g, r, st, _ in rows if st == READY]
        blocked = [(g, r, u) for g, r, st, u in rows if st == BLOCKED]
        CH = {DONE: ("done", "done"), READY: ("ready", "ready"), BLOCKED: ("blocked", "blocked")}

        w('<div class="head" style="margin-top:44px">')
        w('<h1>What is left</h1>')
        w(f'<div class="sub">generated from the {len(rows)} gates above &middot; nothing typed by hand '
          f'&middot; {n_done} done, {len(ready)} can start now, {len(blocked)} blocked</div>')
        w('</div>')

        if ready:
            w('<div class="par">')
            w(f'<h3>{len(ready)} can run in parallel right now</h3>')
            w('<p style="font-size:13.5px;color:var(--ink3);margin:0 0 8px">No unmet dependency '
              'between any of these. Computed from the dependency graph, not judged.</p>')
            w('<ul>' + "".join(f'<li>{e(g.question)}</li>' for g, _ in ready) + '</ul>')
            w('</div>')

        if blocked:
            w('<section class="phase" style="margin-top:26px"><header>')
            w(f'<h2>Blocked</h2><span class="count">{len(blocked)}</span></header>')
            for g, r, unmet in blocked:
                w('<div class="t">')
                w('<div><span class="st blocked">blocked</span></div>')
                w('<div class="sz">&mdash;</div>')
                w(f'<div><div class="tt">{e(g.question)}</div>')
                w(f'<div class="tw">{e(r.headline)}</div>')
                w(f'<div class="dep">waits on: {e(", ".join(unmet))}</div></div></div>')
            w('</section>')

        cp = critical_path()
        w('<div class="par" style="border-color:var(--rule)">')
        w('<h3>Longest dependency chain</h3>')
        w(f'<p style="font-family:ui-monospace,monospace;font-size:13.5px;margin:0">'
          f'{e(" &rarr; ".join(cp))}</p>'.replace("&amp;rarr;", "&rarr;"))
        w('<p style="font-size:13px;color:var(--ink3);margin:8px 0 0">This is the part that cannot be '
          'parallelised away. Everything else can be done alongside it.</p>')
        w('</div>')

    if tab == "lanes":
        # ---------------------------------------------------------------- lanes
        verdict = {g.id: r.verdict for g, r in results}
        passing = {gid for gid, v in verdict.items() if v == PASS}
        lane_waits, lane_conflicts = waits_on(passing), conflicts()
        lane_findings = by_lane()
        ready_lanes = [l.id for l in LANES if not lane_waits[l.id]]
        # ------------------------------------------------------- team filter, in sequence
        # ⛔ NOT a membership filter. A team's declared gates are not self-contained -- the
        # pipeline team declares 7 and needs 10, because `finishes` needs `from-history`,
        # `succeeds` needs `general` and `ceiling` needs `cost`. Show only the declared 7 and the
        # operator reaches step 2 and is blocked by a step this page hid from them. teamplan takes
        # the closure and MARKS what it pulled in.
        w('<div class="head" style="margin-top:44px">')
        w('<h1>Follow one team in sequence</h1>')
        w('<div class="sub">steps are dependency layers &mdash; everything in a step can be done '
          'in parallel, and a step cannot start until the one above it is done</div>')
        w('<div style="margin-top:12px;display:flex;gap:7px;flex-wrap:wrap">')
        for nm in [""] + tplan.teams():
            on = (nm == team)
            href = "/lanes" + (f"?team={urllib.parse.quote(nm)}" if nm else "")
            w(f'<a href="{href}" style="display:inline-block;padding:6px 12px;font-size:12.5px;'
              f'text-decoration:none;border:1px solid var(--rule);border-radius:3px;'
              f'background:{"var(--ink)" if on else "var(--raise)"};'
              f'color:{"var(--paper)" if on else "var(--ink2)"}">{e(nm or "all lanes")}</a>')
        w('</div>')
        w('</div>')

        if team:
            try:
                tp = tplan.plan(team, rows=board())
            except KeyError:
                tp = None
                w(f'<div class="par" style="border-color:var(--fail)">'
                  f'<h3 style="margin-top:0">No team called {e(team)}</h3></div>')
            if tp and tp["state"] == tplan.UNGATED:
                # ⭐ An empty list here would read as "nothing to do". It is not zero steps, it is
                # zero MEASURABLE steps -- the same distinction launch.py protects with UNGATED.
                w('<div class="par" style="border-color:var(--notrun)">')
                w(f'<h3 style="margin-top:0"><span class="chip notrun">UNGATED</span> '
                  f'{e(tp["team"])}</h3>')
                w(f'<p style="font-size:13.5px;color:var(--ink2);margin:0 0 8px">'
                  f'{e(tp["note"])}</p>')
                w('<p style="font-size:12.5px;color:var(--ink3);margin:0"><b>This is not 0%.</b> '
                  'There is nothing to sequence because nothing can be measured yet &mdash; the '
                  'first step is to write the contract, which is not itself a gate.</p>')
                w('</div>')
            elif tp:
                pulled = sum(1 for st in tp["steps"] for i in st["items"] if not i["declared"])
                w('<div class="par">')
                w(f'<h3 style="margin-top:0">{tp["total"]} steps in {len(tp["steps"])} '
                  f'&middot; {tp["done"]} done, {tp["ready"]} ready, {tp["blocked"]} blocked</h3>')
                w(f'<p style="font-size:13px;color:var(--ink3);margin:0">'
                  f'{tp["declared"]} declared by the team'
                  + (f' &middot; <b>{pulled} pulled in as prerequisites</b> it did not declare '
                     f'but cannot finish without' if pulled else '')
                  + f' &middot; lanes involved: {e(", ".join(tp["lanes"])) or "none"}</p>')
                if tp["unowned"]:
                    # These are not oversights. finishes/succeeds are UNMEASURABLE because nothing
                    # has RUN -- no edit moves them. Saying "no lane" without saying why would send
                    # somebody looking for a file to change.
                    w(f'<p style="font-size:12.5px;color:var(--unmeas);margin:8px 0 0">'
                      f'&#9888; <b>{len(tp["unowned"])} step(s) no lane claims</b>: '
                      f'<code>{e(", ".join(tp["unowned"]))}</code> &mdash; check whether these are '
                      f'unassigned work or steps that need a <b>run</b> rather than an edit.</p>')
                w('</div>')
                for st in tp["steps"]:
                    w('<section class="phase" style="margin-top:18px"><header>')
                    w(f'<h2>Step {st["n"]}</h2><span class="count">{len(st["items"])} '
                      f'gate(s), parallel</span></header>')
                    for i in st["items"]:
                        cls = {"done": "done", "ready": "ready"}.get(i["status"], "blocked")
                        w('<div class="t">')
                        w(f'<div><span class="st {cls}">{e(i["status"])}</span></div>')
                        w(f'<div class="sz">{"&#9679;" if i["declared"] else "&#9675;"}</div>')
                        w(f'<div><div class="tt">{e(i["question"])}</div>')
                        w(f'<div class="tw">{e(i["headline"])}</div>')
                        lane = (f'lane: {e(i["lane"])}' if i["lane"] else
                                '<b style="color:var(--unmeas)">no lane claims this step</b>')
                        extra = ('' if i["declared"] else
                                 ' &middot; prerequisite, not declared by this team')
                        w(f'<div class="dep"><code>{e(i["gate"])}</code> &middot; {lane}{extra}'
                          f'</div></div></div>')
                    w('</section>')
                w('<p style="font-size:12px;color:var(--ink3);margin:10px 0 0">'
                  '&#9679; declared by the team &nbsp; &#9675; pulled in as a prerequisite. '
                  'Order is a topological layering of the dependency graph, not an authored plan.'
                  '</p>')

        w('<div class="head" style="margin-top:44px">')
        w('<h1>Start a lane</h1>')
        w(f'<div class="sub">{len(LANES)} lanes &middot; <b>{len(ready_lanes)} can start now</b> '
          '&middot; copy a prompt into a fresh session</div>')
        held = claimlib.active()
        pset = claimlib.parallel_set(passing)
        if held:
            rows = "".join(
                f'<li style="margin-bottom:3px"><code>{e(c.lane)}</code> &mdash; claimed '
                f'{e(c.human_age())} by {e(c.who)}'
                + ('  <b style="color:var(--unmeas)">STALE</b>' if c.stale else '')
                + f' &middot; <a href="/release/{e(c.lane)}">release</a></li>'
                for c in held.values())
            w('<div class="par" style="margin-top:12px;border-color:var(--unmeas)">')
            w(f'<h3 style="margin-top:0">{len(held)} lane(s) claimed</h3>')
            w(f'<ul style="margin:6px 0 0 16px;padding:0;font-size:13px">{rows}</ul>')
            w('<p style="font-size:12px;color:var(--ink3);margin:8px 0 0">A claim is a file, not a '
              'lock &mdash; nothing here can tell a working session from a dead one, so a stale claim '
              'still blocks and says it is stale. It blocks the <i>button</i>; it cannot stop someone '
              'opening a terminal anyway.</p>')
            w('</div>')
        w('<div class="par" style="margin-top:12px">')
        w(f'<h3 style="margin-top:0">{len(pset)} can run at the same time</h3>')
        w(f'<p style="font-size:13.5px;color:var(--ink2);margin:0">'
          f'<code>{e(" · ".join(pset))}</code></p>')
        ready_now = [l for l in pset
                     if not (next((x for x in LANES if x.id == l), None).needs_paul
                             and not opans.get(l))]
        w(f'<a href="/start-all" style="display:inline-block;font-size:12.5px;padding:7px 14px;'
          f'margin:10px 0 0;border:1px solid var(--pass);border-radius:3px;'
          f'background:var(--pass);color:var(--paper);text-decoration:none;'
          f'font-family:ui-monospace,monospace">&#9654; start all {len(ready_now)} in one split view</a>')
        w('<a href="/start-all?layout=tabs" style="display:inline-block;font-size:12.5px;'
          'padding:7px 14px;margin:10px 0 0 6px;border:1px solid var(--rule);border-radius:3px;'
          'background:var(--raise);color:var(--ink);text-decoration:none;'
          'font-family:ui-monospace,monospace">or as separate tabs</a>')
        if len(ready_now) < len(pset):
            held_back = [l for l in pset if l not in ready_now]
            w(f'<p style="font-size:12px;color:var(--unmeas);margin:6px 0 0">'
              f'{e(", ".join(held_back))} held back &mdash; answer the blocker above and it '
              f'joins the set.</p>')
        wts = wt.status()
        if wts:
            rows = "".join(
                f'<li><code>{e(x["lane"])}</code> &middot; branch <code>lane/{e(x["lane"])}</code>'
                + (' &middot; <b style="color:var(--unmeas)">uncommitted changes</b>' if x["dirty"] else '')
                + f' &middot; {e(x["commits_ahead"])} commit(s) ahead</li>' for x in wts)
            w(f'<p style="font-size:12.5px;color:var(--ink2);margin:10px 0 0"><b>Worktrees:</b></p>')
            w(f'<ul style="margin:4px 0 0 16px;padding:0;font-size:12.5px">{rows}</ul>')
            w('<p style="font-size:12px;color:var(--ink3);margin:6px 0 0">Never removed '
              'automatically &mdash; a worktree can hold the only copy of a session&rsquo;s work. '
              'Remove one deliberately with <code>git worktree remove</code>.</p>')
        w('<p style="font-size:12px;color:var(--ink3);margin:8px 0 0">The largest set with no shared '
          'files between them, taken greedily down the recommendation order. Five lanes have no '
          'unmet dependency; only these can be worked <i>together</i>.</p>')
        w('</div>')

        # ------------------------------------------------------------------ past runs
        # Until `factory/runs.py` there was nothing to render here at all: finish() deletes the
        # claim, the bus is per-worktree, and an hour after a lane closed it was indistinguishable
        # from one that never launched. Every figure below carries its basis, because most of this
        # history is RECONSTRUCTED after the fact and saying so is the difference between a
        # measurement and a guess.
        rows = runlib.report()
        shown = [r for r in rows if r["basis"] != runlib.NOT_RECORDED]
        never = [r for r in rows if r["basis"] == runlib.NOT_RECORDED]
        w('<div class="par" style="margin-top:12px">')
        w(f'<h3 style="margin-top:0">Past runs &mdash; {len(shown)} of {len(rows)} lanes have '
          f'a history</h3>')
        if not shown:
            w('<p style="font-size:13px;color:var(--ink3);margin:0">Nothing recorded yet. That is '
              '<b>NOT-RECORDED</b>, not zero &mdash; no lane has closed since the ledger existed.</p>')
        for r in shown:
            c = r["cost"]
            out_col = {runlib.FINISHED: "var(--pass)", runlib.REFUSED: "var(--fail)"}.get(
                r.get("outcome"), "var(--unmeas)")
            label = r.get("outcome") or r["basis"]
            w('<div style="margin:10px 0 0;padding:8px 0 0;border-top:1px solid var(--rule)">')
            w(f'<div style="font-size:13.5px"><code>{e(r["lane"])}</code> '
              f'<span style="color:var(--ink3)">{e(r.get("title", ""))}</span> '
              f'<b style="color:{out_col};font-family:ui-monospace,monospace;font-size:11.5px">'
              f'{e(label)}</b>'
              f'<span style="color:var(--ink3);font-size:11.5px"> &middot; basis '
              f'{e(r["basis"])} &middot; {e(r["runs"])} recorded run(s)</span></div>')
            bits = []
            if r.get("commits") is not None:
                bits.append(f'{r["commits"]} commit(s)')
            if r.get("dirty"):
                bits.append('<b style="color:var(--unmeas)">uncommitted changes</b>')
            if c["basis"] == runlib.MEASURED:
                bits.append(f'{_tok(c["output"])} out')
                bits.append(f'{_tok(c["cache_read"])} cache read')
                bits.append(f'{c["wall_clock_s"] / 3600:.1f}h')
                bits.append(e(", ".join(m.replace("claude-", "") for m in c["models"]) or "?"))
                bits.append(f'{c["sessions"]} session(s)')
            else:
                bits.append('<span style="color:var(--ink3)">cost NOT-RECORDED</span>')
            w(f'<div style="font-size:12.5px;color:var(--ink2);margin-top:3px">'
              f'{" &middot; ".join(bits)}</div>')
            # The reason this panel exists: a lane that refused to close, and why.
            for p in (r.get("problems") or []):
                w(f'<div style="font-size:12px;color:var(--fail);margin-top:3px">&#9888; {e(p)}</div>')
            if r.get("detail") and r.get("outcome"):
                w(f'<div style="font-size:12px;color:var(--ink3);margin-top:2px">{e(r["detail"])}</div>')
            w('</div>')
        if never:
            w(f'<p style="font-size:12.5px;color:var(--ink3);margin:10px 0 0">'
              f'<b>Never launched:</b> {e(", ".join(x["lane"] for x in never))} &mdash; reported '
              f'NOT-RECORDED rather than zero, because no instrument has ever seen them run.</p>')
        w('<p style="font-size:12px;color:var(--ink3);margin:8px 0 0">'
          '<b>RECORDED</b> means <code>finish()</code> wrote the row as it happened, so the outcome '
          'is the lane&rsquo;s own claim. <b>RECONSTRUCTED</b> is derived afterwards from git and '
          'the session transcripts &mdash; it can say what a lane cost and committed, but not '
          'whether it <i>finished</i>, so no outcome is shown. Cost is measured from the '
          '<code>usage</code> block on every assistant message, never estimated.</p>')
        w('</div>')

        ranked = recommend(passing)
        if ranked:
            top, _, why = ranked[0]
            w('<div class="par" style="margin-top:12px;border-color:var(--pass)">')
            w(f'<h3 style="margin-top:0">Start here: {e(top.title)} '
              f'<span style="font-weight:400;color:var(--ink3);font-size:13px">'
              f'&middot; <code>{e(top.id)}</code></span></h3>')
            w(f'<p style="font-size:13.5px;color:var(--ink2);margin:0 0 6px">{e(why)}</p>')
            if len(ranked) > 1:
                rest = " &middot; ".join(f'{e(l.title)} <span style="color:var(--ink3)">'
                                         f'({e(l.id)})</span>' for l, _, _ in ranked[1:])
                w(f'<p style="font-size:12.5px;color:var(--ink3);margin:0">then: {rest}</p>')
            w('<p style="font-size:12px;color:var(--ink3);margin:8px 0 0">The inputs are measured '
              '&mdash; gate verdicts, the dependency graph, file conflicts. The <b>weighting is a '
              'judgement</b>, written down in <code>factory/lanes.py::recommend</code> so you can '
              'disagree with it rather than guess what it did.</p>')
            w('</div>')
        w('<div class="sub" style="font-size:12.5px;color:var(--ink3);margin-top:6px">'
          '<b>waits on</b> is derived from gate dependencies &mdash; the work is not ready. '
          '<b>conflicts with</b> is derived from the files a lane writes &mdash; the work is ready '
          'but the seat is taken. Two different reasons not to start, and only one of them is about '
          'the dependency graph.</div>')
        w('</div>')
        for lane in LANES:
            done_n = sum(1 for gid in lane.gates if verdict.get(gid) == PASS)
            chips = " ".join(
                f'<span style="font-family:ui-monospace,monospace;font-size:11.5px;padding:1px 6px;'
                f'border:1px solid var(--rule);border-radius:2px;'
                f'color:{"var(--pass)" if verdict.get(gid) == PASS else "var(--ink3)"}">{e(gid)}</span>'
                for gid in lane.gates)
            w('<div class="par" style="margin-top:16px">')
            w(f'<h3>{e(lane.title)} <span style="font-weight:400;color:var(--ink3);font-size:13px">'
              f'&middot; {done_n} of {len(lane.gates)} done &middot; {e(SIZE[lane.size])}</span></h3>')
            w(f'<p style="font-size:13.5px;color:var(--ink2);margin:0 0 8px">{e(lane.why)}</p>')
            w(f'<p style="font-size:12.5px;color:var(--ink3);margin:0 0 8px">'
              f'<code>{e(lane.repo)}</code> &middot; touches <code>{e(lane.touches)}</code></p>')
            w(f'<p style="font-size:12.5px;color:var(--ink3);margin:0 0 8px">'
              f'run this session on <b style="color:var(--ink)">{e(lane.model)}</b> &mdash; '
              f'{e(lane.model_why)}</p>')
            hits = lane_findings.get(lane.id) or []
            if hits:
                items = "".join(
                    f'<li style="margin-bottom:3px"><b>{e(h.id)}</b> {e(h.title)}</li>' for h in hits)
                w(f'<div style="font-size:12.5px;color:var(--ink2);margin:0 0 8px;padding:8px 10px;'
                  f'border-left:2px solid var(--unmeas);background:var(--paper)">'
                  f'<b>Read before starting &mdash; corrections that hit this lane:</b>'
                  f'<ul style="margin:6px 0 0 16px;padding:0">{items}</ul></div>')
            waits, clash = lane_waits[lane.id], lane_conflicts[lane.id]
            if waits:
                w(f'<p style="font-size:12.5px;color:var(--unmeas);margin:0 0 8px">'
                  f'<b>waits on:</b> {e(", ".join(waits))}</p>')
            else:
                w('<p style="font-size:12.5px;color:var(--pass);margin:0 0 8px">'
                  '<b>no unmet dependency &mdash; can start now</b></p>')
            if clash:
                w(f'<p style="font-size:12.5px;color:var(--fail);margin:0 0 8px">'
                  f'<b>cannot run at the same time as:</b> {e(", ".join(clash))} '
                  f'&mdash; shared files</p>')
            w(f'<p style="display:flex;flex-wrap:wrap;gap:5px;margin:0 0 10px">{chips}</p>')
            if lane.needs_paul:
                w(f'<p style="font-size:12.5px;color:var(--unmeas);margin:0 0 8px">'
                  f'<b>Needs Paul:</b> {e(lane.needs_paul)}</p>')
                ans = opans.get(lane.id)
                if ans and not ans.get('broken'):
                    w(f'<div style="font-size:12.5px;color:var(--pass);margin:0 0 8px;padding:8px 10px;border-left:2px solid var(--pass);background:var(--paper)">'
                      f'<b>Answered {e(ans["at"][:16])}</b> &middot; <a href="/unanswer/{e(lane.id)}">clear</a><br>{e(ans["text"])}</div>')
                else:
                    w(f'<form method="POST" action="/answer-blocker" style="margin:0 0 8px">'
                      f'<input type="hidden" name="lane" value="{e(lane.id)}">'
                      f'<textarea name="text" rows="2" placeholder="answer it now and the session never has to ask" style="width:100%;box-sizing:border-box;font-size:12px;padding:7px;border:1px solid var(--rule);border-radius:3px;background:var(--paper);color:var(--ink);font-family:ui-monospace,monospace"></textarea>'
                      f'<button type="submit" style="font-size:12px;padding:4px 10px;margin-top:5px;cursor:pointer;border:1px solid var(--rule);border-radius:3px;background:var(--raise);color:var(--ink);font-family:ui-monospace,monospace">record answer</button></form>')
            blocked = claimlib.blockers(lane.id, held)
            mine = held.get(lane.id)
            if mine:
                w(f'<p style="font-size:12.5px;color:var(--unmeas);margin:0 0 8px">'
                  f'<b>CLAIMED</b> {e(mine.human_age())} by {e(mine.who)}'
                  + ('  &mdash; <b>STALE</b>' if mine.stale else '')
                  + f' &middot; <a href="/release/{e(lane.id)}">release</a></p>')
            elif blocked:
                names = ", ".join(b.lane for b in blocked)
                w(f'<p style="font-size:12.5px;color:var(--fail);margin:0 0 8px">'
                  f'<b>BLOCKED</b> &mdash; {e(names)} is claimed and shares files with this lane. '
                  f'Release it, or pick one from the parallel set above.</p>')
            if mine:
                w(f'<form method="POST" action="/finish" style="margin:0 0 10px;padding:9px 10px;'
                  f'border-left:2px solid var(--pass);background:var(--paper)">'
                  f'<input type="hidden" name="lane" value="{e(lane.id)}">'
                  f'<div style="font-size:12.5px;color:var(--ink2);margin-bottom:6px">'
                  f'<b>Finish this lane.</b> Runs the preflight, writes a handoff to '
                  f'boot-prompts/, releases the claim. Everything measurable is generated &mdash; '
                  f'this box is the part no instrument can see.</div>'
                  f'<textarea name="note" rows="2" placeholder="where it got to, and what the '
                  f'next session must not re-derive" style="width:100%;box-sizing:border-box;'
                  f'font-size:12px;padding:7px;border:1px solid var(--rule);border-radius:3px;'
                  f'background:var(--surface);color:var(--ink);'
                  f'font-family:ui-monospace,monospace"></textarea>'
                  f'<button type="submit" style="font-size:12px;padding:4px 10px;margin-top:5px;'
                  f'cursor:pointer;border:1px solid var(--rule);border-radius:3px;'
                  f'background:var(--raise);color:var(--ink);'
                  f'font-family:ui-monospace,monospace">run preflight &amp; finish</button>'
                  f'</form>')
            w(f'<button type="button" data-copy="ln-{e(lane.id)}" style="font-size:12px;'
              f'padding:5px 10px;margin-bottom:8px;cursor:pointer;border:1px solid var(--rule);'
              f'border-radius:3px;background:var(--raise);color:var(--ink);'
              f'font-family:ui-monospace,monospace">copy prompt</button>')
            if not mine:
                dis = ' opacity:.45;pointer-events:none;' if blocked else ''
                if not blocked:
                    w(f'<a href="/start/{e(lane.id)}" style="display:inline-block;font-size:12px;'
                      f'padding:5px 10px;margin:0 0 8px 6px;border:1px solid var(--pass);'
                      f'border-radius:3px;background:var(--pass);color:var(--paper);'
                      f'text-decoration:none;font-family:ui-monospace,monospace">'
                      f'&#9654; start on {e(lane.model)}</a>')
                w(f'<a href="/claim/{e(lane.id)}" style="display:inline-block;font-size:12px;'
                  f'padding:5px 10px;margin:0 0 8px 6px;border:1px solid var(--rule);'
                  f'border-radius:3px;background:var(--raise);color:var(--ink);'
                  f'text-decoration:none;font-family:ui-monospace,monospace;{dis}">'
                  f'{"blocked - a conflicting lane is running" if blocked else "reserve (I start it myself)"}</a>')
            # pre-wrap: a <pre> of long lines would widen the page, which is a defect already fixed
            # once today on the artifact. Do not "tidy" this to nowrap.
            w(f'<pre id="ln-{e(lane.id)}" style="white-space:pre-wrap;word-break:break-word;'
              f'font-family:ui-monospace,monospace;font-size:11.5px;line-height:1.55;margin:0;'
              f'padding:10px;border:1px solid var(--rule);border-radius:3px;background:var(--paper);'
              f'color:var(--ink2);max-height:230px;overflow:auto">{e(lane.full_prompt)}</pre>')
            w('</div>')

    if tab == "sessions":
        # ------------------------------------------------------------------ sessions
        # The question this answers is "which of these twelve terminals is which, and which are
        # waiting on me" — which nothing answered before, because the three sources that know are
        # never joined: the session registry (written by the session), jobs/<id>/state.json
        # (written by the agent, and carrying a `needs` question in English) and the process table
        # (the only one that knows whether anything is still running).
        inv = sesslib.inventory()
        blocked = [r for r in inv if r["needs"]]
        collisions = sesslib.collisions()
        contended = [r for r in sesslib.contended_repos() if r["contended"]]
        running = [r for r in inv if r["state"].startswith("RUNNING")]
        w('<div class="head" style="margin-top:44px">')
        w('<h1>Sessions</h1>')
        w(f'<div class="sub">{len(running)} running &middot; '
          f'<b style="color:{"var(--fail)" if blocked else "var(--ink3)"}">{len(blocked)} waiting '
          f'on you</b> &middot; {len(inv)} known to the registry</div>')
        w('</div>')

        # Contended repos, above everything except a blocked session. THE SET IS DELIBERATELY WIDE
        # and must stay so: every live session's cwd plus the primary, NOT 'this project'.
        # Narrowing it to the factory would delete the one signal it exists for — proven again
        # 2026-08-29, when a session whose cwd was `neurospect-learn` made six commits into
        # `agent-factory` while a second session edited the same two files.
        # A repo with uncommitted work
        # and several sessions alive is the shape that produced fc71b6a — one session ran `git add`
        # across a directory another was mid-edit in, swept up a half-finished file, and shipped a
        # HEAD that did not import.
        #
        # ⛔ This panel names a CONDITION, never a culprit. Nothing records which session touched
        # which file, so `attribution` is NOT-MEASURABLE and the wording must stay that way — a row
        # that guessed would be believed.
        if contended:
            w('<div class="par" style="margin-top:14px;border-color:var(--unmeas)">')
            w(f'<h3 style="margin-top:0;color:var(--unmeas)">&#9888; Live sessions could be '
              f'writing to {len(contended)} repo(s) that hold uncommitted work</h3>')
            # The set is the blast radius, not the project. Said on the page, because a heading
            # naming an unrelated repo otherwise reads as the tracker having lost its own scope.
            w('<p style="font-size:12px;color:var(--ink3);margin:6px 0 0">'
              '<b>These are not this project.</b> They are the blast radius: a session&rsquo;s cwd '
              'says where it <i>started</i>, not what it writes to, so the set is every live '
              'session&rsquo;s cwd plus the primary worktree. A repo here may be unrelated to the '
              'factory and still be somewhere a live agent can reach.</p>')
            for r in contended:
                here = r["sessions_with_this_cwd"]
                cwd_note = (f'{here} session(s) started here'
                            if here else
                            '<b>no session has this as its working directory</b> &mdash; which is '
                            'why the cwd-based check says nothing about it')
                w(f'<div style="margin:8px 0 0;padding:8px 0 0;border-top:1px solid var(--rule)">'
                  f'<div style="font-size:13.5px"><b>{e(r["name"])}</b> '
                  f'<span style="color:var(--ink3);font-size:11.5px">'
                  f'{e(r["dirty"])} uncommitted file(s) &middot; {cwd_note}</span></div>'
                  f'<div style="font-size:11.5px;color:var(--ink3);margin-top:2px">'
                  f'{e(r["path"])}</div></div>')
            w('<p style="font-size:12px;color:var(--ink3);margin:10px 0 0">'
              '<b>Attribution is NOT-MEASURABLE.</b> Nothing records which session wrote which '
              'file, so this reports a hazard and not a culprit. Before staging here: '
              '<code>git fetch</code>, stage <b>explicit paths</b>, and never '
              '<code>git add -A</code>. The pre-commit hook '
              '(<code>scripts/hooks/pre-commit-imports.py</code>) catches the consequence &mdash; '
              'a committed tree that does not import &mdash; but it cannot catch a clobber that '
              'still compiles.</p>')
            w('</div>')

        # Blocked first, always. A blocked agent is the only kind a human can unblock, and these
        # questions were sitting unread in a file nothing opened.
        if blocked:
            w('<div class="par" style="margin-top:14px;border-color:var(--fail)">')
            w(f'<h3 style="margin-top:0;color:var(--fail)">'
              f'&#9888; {len(blocked)} session(s) are asking you a question</h3>')
            for r in blocked:
                w('<div style="margin:10px 0 0;padding:8px 0 0;border-top:1px solid var(--rule)">')
                w(f'<div style="font-size:13.5px"><b>{e(r["lane"] or r["repo"] or "?")}</b> '
                  f'<span style="color:var(--ink3);font-size:11.5px">pid {e(r["pid"])} &middot; '
                  f'{e(r["state"])} &middot; {e(r["where"])}</span></div>')
                w(f'<div style="font-size:13.5px;color:var(--ink);margin-top:4px">'
                  f'&ldquo;{e(r["needs"])}&rdquo;</div>')
                if r["topic"]:
                    w(f'<div style="font-size:12px;color:var(--ink3);margin-top:3px">'
                      f'opened with: {e(r["topic"])}</div>')
                w('</div>')
            w('</div>')

        if collisions:
            w('<div class="par" style="margin-top:12px;border-color:var(--unmeas)">')
            w(f'<h3 style="margin-top:0">{len(collisions)} directory(ies) hold more than one '
              f'running session</h3>')
            for cwd, rs in collisions.items():
                w(f'<div style="font-size:12.5px;margin-top:4px"><code>{e(cwd)}</code> &mdash; '
                  f'{len(rs)} sessions (pids {e(", ".join(str(x["pid"]) for x in rs))})</div>')
            w('<p style="font-size:12px;color:var(--ink3);margin:8px 0 0">Two agents in one '
              'directory is the arrangement the lane model exists to avoid &mdash; and on '
              '2026-08-22 it happened for real, three sessions on one branch. Nothing collided, '
              'which was luck rather than a control (F73: a claim is not a process).</p>')
            w('</div>')

        w('<div class="par" style="margin-top:12px">')
        w('<h3 style="margin-top:0">Every session</h3>')
        colour = {sesslib.RUNNING_ATTACHED: "var(--pass)",
                  sesslib.RUNNING_ORPHANED: "var(--unmeas)",
                  sesslib.EXITED_RESUMABLE: "var(--ink3)",
                  sesslib.EXITED_GONE: "var(--ink3)",
                  sesslib.UNKNOWN: "var(--fail)"}
        for r in inv:
            w('<div style="margin:9px 0 0;padding:7px 0 0;border-top:1px solid var(--rule)">')
            bits = [f'pid {e(r["pid"])}']
            if r["status"]:
                bits.append(e(r["status"]))
            if r["tokens"]:
                bits.append(f'{_tok(r["tokens"])} tok')
            if r["in_flight"]:
                bits.append(f'{e(r["in_flight"])} in flight')
            w(f'<div style="font-size:13.5px"><b>{e(r["lane"] or r["repo"] or "?")}</b> '
              f'<span style="color:var(--ink3);font-size:12px">{e(r["where"])}</span> '
              f'<b style="color:{colour.get(r["state"], "var(--ink3)")};'
              f'font-family:ui-monospace,monospace;font-size:11px">{e(r["state"])}</b>'
              f'<span style="color:var(--ink3);font-size:11.5px"> &middot; '
              f'{" &middot; ".join(bits)}</span></div>')
            # The opening prompt, NOT the registry name — five live sessions shared one name.
            if r["topic"]:
                w(f'<div style="font-size:12.5px;color:var(--ink2);margin-top:3px">'
                  f'{e(r["topic"])}</div>')
            elif r["name"]:
                w(f'<div style="font-size:12.5px;color:var(--ink3);margin-top:3px">'
                  f'label: {e(r["name"])} <i>(no transcript &mdash; label is not unique)</i></div>')
            if r["detail"] and not r["needs"]:
                w(f'<div style="font-size:12px;color:var(--ink3);margin-top:2px">'
                  f'{e(r["detail"][:160])}</div>')
            if r["state"] == sesslib.RUNNING_ORPHANED:
                w('<div style="font-size:12px;color:var(--unmeas);margin-top:3px">'
                  'no terminal of its own &mdash; reach it with <code>claude agents</code>. '
                  '<code>--resume</code> will refuse, and forcing it starts a SECOND process on '
                  'one session id.</div>')
            elif r["state"] == sesslib.EXITED_RESUMABLE:
                w(f'<div style="font-size:12px;color:var(--ink3);margin-top:3px">'
                  f'<code>claude --resume {e(r["session_id"][:8])}…</code> from '
                  f'<code>{e(r["where"])}</code></div>')
            w('</div>')
        w('<p style="font-size:12px;color:var(--ink3);margin:10px 0 0">'
          'Identity is the <b>opening prompt</b>, not the session name: on 2026-08-23 five live '
          'sessions were all called <code>boot pre-flight verification</code>, inherited from the '
          'boot prompt that spawned them. Names cannot be changed after startup, so this reads '
          'what each session was actually asked. <b>RUNNING-ATTACHED</b> owns a terminal; '
          '<b>RUNNING-ORPHANED</b> is alive with none; <b>EXITED-RESUMABLE</b> has a transcript to '
          'come back to; <b>EXITED-GONE</b> does not. If the process table cannot be read every '
          'row says <b>UNKNOWN</b> rather than pretending nothing is running.</p>')
        w('</div>')

    if tab == "goals":
        # ------------------------------------------------------------------ goals
        # The 30 gates answer one question — can a team run a migration unattended. The operator
        # has three, and they cut across phases, so `factory/goals.py` groups gates by goal.
        # ⚠ The GROUPING is a judgement and is printed in full below rather than hidden behind a
        # percentage: a progress bar over the wrong set is a confident-looking lie.
        gp = goalslib.progress()
        cov = goalslib.coverage()
        w('<div class="head" style="margin-top:44px">')
        w('<h1>Goals</h1>')
        w(f'<div class="sub">three things we are building &middot; '
          f'{sum(g["passing"] for g in gp)} of {sum(g["total"] for g in gp)} of their gates '
          f'passing &middot; re-measured just now</div>')
        w('</div>')

        for g in gp:
            frac = g["passing"] / g["total"] if g["total"] else 0
            col = "var(--pass)" if frac == 1 else ("var(--unmeas)" if frac else "var(--fail)")
            w('<div class="par" style="margin-top:14px">')
            w(f'<h3 style="margin-top:0">{e(g["goal"])} '
              f'<span style="font-weight:400;color:{col};font-family:ui-monospace,monospace;'
              f'font-size:13px">{g["passing"]} of {g["total"]}</span></h3>')
            # The bar IS passing/total. Change the number and the picture changes.
            w(f'<div style="height:7px;background:var(--rule);border-radius:3px;margin:6px 0 8px">'
              f'<div style="height:7px;width:{frac*100:.1f}%;background:{col};border-radius:3px">'
              f'</div></div>')
            w(f'<p style="font-size:13px;color:var(--ink2);margin:0">{e(g["why"])}</p>')
            chips = " ".join(
                f'<span style="font-family:ui-monospace,monospace;font-size:11.5px;padding:1px 6px;'
                f'border:1px solid var(--rule);border-radius:2px;color:'
                f'{"var(--pass)" if x["verdict"] == "PASS" else "var(--ink3)"}">{e(x["id"])}</span>'
                for x in g["gates"])
            w(f'<div style="margin-top:8px">{chips}</div>')
            if g["basis"] != "MEASURED":
                w('<p style="font-size:12px;color:var(--unmeas);margin:8px 0 0">'
                  '<b>NOT-MEASURED</b> — every gate here is UNMEASURABLE or NOT_RUN. That is a fact '
                  'about the instrument, not about the work, and it is not the same as 0%.</p>')
            w('</div>')

        # Velocity, in its own words. It refuses to project and says why — that refusal is the
        # most useful line on the page and paraphrasing it would soften it.
        w('<div class="par" style="margin-top:14px">')
        w('<h3 style="margin-top:0">How fast, and when</h3>')
        try:
            rep = schedlib.report()
        except Exception as exc:                                   # noqa: BLE001
            rep = f"schedule unavailable: {type(exc).__name__}: {exc}"
        w(f'<pre style="font-size:12px;color:var(--ink2);white-space:pre-wrap;margin:0;'
          f'font-family:ui-monospace,monospace">{e(rep)}</pre>')
        w('</div>')

        w('<div class="par" style="margin-top:12px;border-color:var(--unmeas)">')
        w('<h3 style="margin-top:0">&#9888; What this page does not cover</h3>')
        w(f'<p style="font-size:13px;color:var(--ink2);margin:0">These three goals span '
          f'<b>{cov["covered"]} of {cov["total"]}</b> gates. '
          f'<b>{len(cov["uncovered"])} are in no goal at all</b>: '
          f'<code>{e(", ".join(cov["uncovered"]))}</code></p>')
        w('<p style="font-size:12px;color:var(--ink3);margin:8px 0 0">'
          'Shown because a goals page implies the goals are the whole picture, and here they are '
          'not. A gate in no goal is a gate nobody is counting toward anything &mdash; which is how '
          'the <code>version</code> gate went unowned long enough to report a figure that could '
          'never have been anything else.</p>')
        w('<p style="font-size:12px;color:var(--ink3);margin:8px 0 0">'
          '<b>The grouping is the one authored judgement here.</b> Every number is measured; which '
          'gates constitute a goal is a decision, and it lives in <code>factory/goals.py::GOALS</code> '
          'so it can be argued with. It is validated on import &mdash; a goal naming a deleted gate '
          'breaks the build rather than quietly shrinking.</p>')
        w('</div>')

    if tab == "roadmap":
        # ------------------------------------------------------------------ roadmap
        # Everything here is a JOIN over board(), not a task list. `board()` already computes
        # DONE/READY/BLOCKED per gate and its own docstring states the rule this tab renders:
        # everything READY is parallelisable BY DEFINITION. So the sequence is not drawn, and a
        # roadmap whose steps were typed by hand would look identical if the project changed —
        # which is this repo's test for a figure that is only decoration.
        wv = roadlib.waves()
        ch = roadlib.chain()
        tm = roadlib.teams()
        acts = roadlib.actions()
        contras = roadlib.contradictions()
        up = roadlib.unplaced()
        done_n = len(wv[0]["gates"])
        ready_n = len(wv[1]["gates"])
        blocked_n = len(wv[2]["gates"])
        tot = done_n + ready_n + blocked_n

        w('<div class="head" style="margin-top:44px">')
        w('<h1>Roadmap</h1>')
        w(f'<div class="sub">{done_n} of {tot} gates done &middot; '
          f'<b>{ready_n} can start right now, in parallel</b> &middot; {blocked_n} blocked '
          f'&middot; re-measured just now</div>')
        w('</div>')

        # ---- the headline claim, and it is computed ------------------------------------------
        w('<div class="par" style="margin-top:14px">')
        w('<h3 style="margin-top:0">How much of this is parallel</h3>')
        w(f'<p style="font-size:13px;color:var(--ink2);margin:0"><b>{ready_n} of the '
          f'{ready_n + blocked_n} remaining gates have every dependency already satisfied.</b> '
          f'They are parallelisable by definition &mdash; not by a scheduling judgement someone '
          f'made, but because READY <i>means</i> nothing is left to wait for. The only thing '
          f'capping how many run at once is people and machines, not the dependency graph.</p>')
        w(f'<p style="font-size:12.5px;color:var(--ink3);margin:8px 0 0">Derived from '
          f'<code>factory/board.py::board()</code> on this request. Add a gate and it appears '
          f'here; make one pass and it leaves. There is no list to maintain.</p>')
        w('</div>')

        # ---- the critical path ---------------------------------------------------------------
        if ch:
            w('<div class="par" style="margin-top:12px;border-color:var(--fail)">')
            w('<h3 style="margin-top:0">The chain parallelism cannot remove</h3>')
            hops = []
            for i, h in enumerate(ch):
                col = {"DONE": "var(--pass)", "READY": "var(--ink)",
                       "BLOCKED": "var(--ink3)"}.get(h["status"], "var(--ink3)")
                arrow = ('<span style="color:var(--ink3);margin:0 8px">&rarr;</span>'
                         if i else "")
                hops.append(
                    f'{arrow}<span style="font-family:ui-monospace,monospace;font-size:13px;'
                    f'padding:3px 9px;border:1px solid {col};border-radius:3px;color:{col}">'
                    f'{e(h["id"])}<span style="font-size:10.5px;opacity:.75"> '
                    f'{e(h["status"] or "?")}</span></span>')
            w(f'<div style="margin:4px 0 8px">{"".join(hops)}</div>')
            w('<p style="font-size:12.5px;color:var(--ink3);margin:0">The longest chain of unmet '
              'dependencies. Every other gate can be worked around it; this one is strictly '
              'sequential, so it sets the floor on how fast the whole board can finish no matter '
              'how many run in parallel.</p>')
            w('</div>')

        # ---- ⭐ computed contradictions --------------------------------------------------------
        # A gate DONE while a gate it declares a dependency on has not passed. Exactly one of two
        # things is true and both matter. This panel appears only when the condition holds.
        if contras:
            w('<div class="par" style="margin-top:12px;border-color:var(--fail)">')
            w(f'<h3 style="margin-top:0">&#9888; {len(contras)} gate(s) pass while a dependency '
              f'they declare does not</h3>')
            for c in contras:
                pairs = ", ".join(f"<code>{e(k)}</code> is {e(str(v))}"
                                  for k, v in c["unmet_verdicts"].items())
                w(f'<p style="font-size:13px;color:var(--ink2);margin:0 0 6px">'
                  f'<code><b>{e(c["id"])}</b></code> is <b style="color:var(--pass)">PASS</b>, '
                  f'but it depends on {pairs}.</p>')
            w('<p style="font-size:12.5px;color:var(--ink3);margin:8px 0 0">'
              '<b>Exactly one of these is true, and neither is harmless.</b> Either the edge is '
              'wrong &mdash; we asserted a prerequisite that is not really one, and the roadmap '
              'is sequencing work that could already have started &mdash; or <b>the pass is '
              'vacuous</b>: the gate is green over the thing it is named for. This estate has been '
              'bitten by the second before, when three gates passed over an intact control-plane '
              'defect and the readiness count did not move. <b>A check that would still pass with '
              'the function body deleted is not measuring the function</b>, and a check that does '
              'not need its own prerequisite earns the same suspicion.</p>')
            w('<p style="font-size:12px;color:var(--ink3);margin:8px 0 0">Computed on every load '
              'from <code>roadmap.contradictions()</code>. This panel disappears by itself when '
              'the condition stops holding &mdash; it is not a note somebody left.</p>')
            w('</div>')

        # ---- the waves -------------------------------------------------------------------------
        for band in wv:
            if not band["gates"]:
                continue
            col = {"DONE": "var(--pass)", "READY": "var(--ink)",
                   "BLOCKED": "var(--ink3)"}[band["key"]]
            w('<section class="phase" style="margin-top:14px"><header>')
            w(f'<h2 style="color:{col}">{e(band["title"])}</h2>'
              f'<span class="count">{len(band["gates"])}</span>')
            w('</header>')
            w(f'<p style="font-size:12.5px;color:var(--ink3);margin:0 0 10px">'
              f'{e(band["why"])}</p>')
            for g in band["gates"]:
                # ⚠ The connective words carry their OWN font-size. Placed bare after the phase
                # span they inherited the div default and rendered noticeably larger than every
                # word around them — invisible to a render-to-string test, obvious on sight, and
                # caught only by the first real render pass on 2026-08-23.
                _sm = 'font-size:11.5px;color:var(--ink3)'
                unl = (f'<span style="{_sm}"> &middot; unlocks </span>'
                       f'<code style="font-size:11.5px">{e(", ".join(g["unlocks"]))}</code>'
                       if g["unlocks"] else "")
                wait = (f'<span style="{_sm}"> &middot; waits on </span>'
                        f'<code style="font-size:11.5px;color:var(--fail)">'
                        f'{e(", ".join(g["unmet"]))}</code>' if g["unmet"] else "")
                w(f'<div style="padding:7px 0;border-top:1px solid var(--rule)">'
                  f'<code style="font-size:13px;color:{col}"><b>{e(g["id"])}</b></code>'
                  f'<span style="font-size:11.5px;color:var(--ink3);margin-left:8px">'
                  f'{e(g["phase"])}</span>{unl}{wait}'
                  f'<div style="font-size:12.5px;color:var(--ink2);margin-top:3px">'
                  f'{e(g["headline"])}</div></div>')
            w('</section>')

        # ---- the two named teams ---------------------------------------------------------------
        w('<div class="head" style="margin-top:36px"><h1>The two agent teams</h1>')
        w('<div class="sub">the end states someone named out loud &mdash; '
          '<b>AUTHORED</b>, because no probe can infer a goal</div></div>')
        for t_ in tm:
            if t_["basis"] == "UNGATED":
                w('<div class="par" style="margin-top:12px;border-color:var(--unmeas)">')
                w(f'<h3 style="margin-top:0">{e(t_["team"])} '
                  f'<span style="font-weight:400;color:var(--unmeas);'
                  f'font-family:ui-monospace,monospace;font-size:13px">UNGATED</span></h3>')
                w(f'<p style="font-size:13px;color:var(--ink2);margin:0">{e(t_["intent"])}</p>')
                w(f'<p style="font-size:12.5px;color:var(--unmeas);margin:8px 0 0">'
                  f'{e(t_["unblock"])}</p>')
                w('<p style="font-size:12px;color:var(--ink3);margin:8px 0 0">'
                  'Shown as <b>UNGATED</b>, deliberately not as 0%. "Nothing is measuring this" '
                  'and "this is measured at zero" are different claims and only one of them is '
                  'about the work.</p>')
                w('</div>')
                continue
            frac = t_["passing"] / t_["total"] if t_["total"] else 0
            col = "var(--pass)" if frac == 1 else ("var(--unmeas)" if frac else "var(--fail)")
            w('<div class="par" style="margin-top:12px">')
            w(f'<h3 style="margin-top:0">{e(t_["team"])} '
              f'<span style="font-weight:400;color:{col};font-family:ui-monospace,monospace;'
              f'font-size:13px">{t_["passing"]} of {t_["total"]}</span></h3>')
            w(f'<div style="height:7px;background:var(--rule);border-radius:3px;margin:6px 0 8px">'
              f'<div style="height:7px;width:{frac*100:.1f}%;background:{col};border-radius:3px">'
              f'</div></div>')
            w(f'<p style="font-size:13px;color:var(--ink2);margin:0">{e(t_["intent"])}</p>')
            chips = " ".join(
                f'<span style="font-family:ui-monospace,monospace;font-size:11.5px;padding:1px 6px;'
                f'border:1px solid var(--rule);border-radius:2px;color:'
                f'{"var(--pass)" if x["verdict"] == "PASS" else ("var(--ink)" if x["status"] == "READY" else "var(--ink3)")}">'
                f'{e(x["id"])}</span>' for x in t_["gates"])
            w(f'<div style="margin-top:8px">{chips}</div>')
            if t_["ready_now"]:
                w(f'<p style="font-size:12.5px;color:var(--ink2);margin:8px 0 0">'
                  f'<b>Startable today:</b> <code>{e(", ".join(t_["ready_now"]))}</code> '
                  f'&mdash; nothing upstream is holding them.</p>')
            if t_["blocked_on"]:
                w(f'<p style="font-size:12.5px;color:var(--ink3);margin:6px 0 0">'
                  f'Named blocker: <code>{e(t_["blocked_on"])}</code>.</p>')
            w('</div>')

        # ---- the eighteen decided actions -------------------------------------------------------
        gated = sum(1 for a in acts if a["basis"] == "MEASURED")
        w('<div class="head" style="margin-top:36px"><h1>The eighteen decided actions</h1>')
        w(f'<div class="sub">from SYNTHESIS &sect;12.8, &sect;13.7 and &sect;14.7 &middot; '
          f'{gated} of {len(acts)} have a gate that can check them</div></div>')
        w('<div class="par" style="margin-top:12px;border-color:var(--unmeas)">')
        w('<p style="font-size:12.5px;color:var(--ink2);margin:0"><b>Each was written the day its '
          'own pass landed, and none knew what the others would say.</b> Nobody has checked that '
          'they are consistent with each other or that the order is right &mdash; that is R16\'s '
          'job and R16 is correctly held until R13 run 2 and R14 land. Treat the set as decided, '
          'not as verified.</p>')
        w(f'<p style="font-size:12px;color:var(--ink3);margin:8px 0 0">Where an action has a '
          f'<b>gate</b>, its state comes from the gate and is labelled <b>MEASURED</b>. The other '
          f'{len(acts) - gated} carry an <b>AUTHORED</b> state, which is a person\'s claim and is '
          f'styled to look weaker because it is.</p>')
        w('</div>')
        _ASTATE = {"SHIPPED": "var(--pass)", "DECIDED": "var(--ink2)",
                   "SUPERSEDED": "var(--ink3)"}
        for a in acts:
            col = _ASTATE.get(a["state"], "var(--ink3)")
            bas = ('<span style="font-size:10.5px;padding:1px 5px;border-radius:2px;'
                   'background:var(--ink);color:var(--paper)">MEASURED</span>'
                   if a["basis"] == "MEASURED" else
                   '<span style="font-size:10.5px;padding:1px 5px;border:1px solid var(--rule);'
                   'border-radius:2px;color:var(--ink3)">AUTHORED</span>')
            gtxt = (f' &middot; gate <code>{e(a["gate"])}</code> is {e(str(a["verdict"]))}'
                    if a["gate"] else "")
            w(f'<div style="padding:9px 0;border-top:1px solid var(--rule)">'
              f'<span style="font-family:ui-monospace,monospace;font-size:11.5px;color:{col};'
              f'font-weight:600">{e(a["state"])}</span> {bas} '
              f'<span style="font-size:11.5px;color:var(--ink3)">{e(a["source"])}</span>{gtxt}'
              f'<div style="font-size:13px;color:var(--ink2);margin-top:3px">'
              f'{e(a["text"])}</div>')
            if a["note"]:
                w(f'<div style="font-size:12px;color:var(--ink3);margin-top:5px;'
                  f'padding-left:10px;border-left:2px solid var(--rule)">'
                  f'{e(a["note"])}</div>')
            w('</div>')

        # ---- the honest denominator ------------------------------------------------------------
        w('<div class="par" style="margin-top:16px;border-color:var(--unmeas)">')
        w('<h3 style="margin-top:0">&#9888; What this roadmap does not account for</h3>')
        w(f'<p style="font-size:13px;color:var(--ink2);margin:0">The three goals and the two teams '
          f'together span <b>{up["placed"]} of {up["total"]}</b> gates. '
          f'<b>{len(up["unplaced"])} belong to no goal and no team</b>: '
          f'<code>{e(", ".join(up["unplaced"]))}</code></p>')
        w('<p style="font-size:12px;color:var(--ink3);margin:8px 0 0">'
          'Stated because <b>a roadmap implies completeness and this one does not have it.</b> '
          'A gate on no roadmap is work nobody is counting toward anything &mdash; and several of '
          'these are load-bearing: <code>cost</code> blocks <code>ceiling</code>, '
          '<code>from-history</code> blocks <code>finishes</code>, and <code>checks</code> blocks '
          '<code>refuses</code>. They are not offcuts; they are unplaced.</p>')
        w('</div>')

    if tab == "flow":
        # ------------------------------------------------------------------ flow
        # The readiness graph, laid out from the gate list and the dependency map rather than
        # drawn. Adding a gate moves the picture; `board._validate()` already refuses to import if
        # an edge names a gate that does not exist, so the figure cannot outlive its data.
        nodes, edges, crit = flowlib.layout()
        per_phase = flowlib.counts()
        passing = sum(c["passing"] for c in per_phase)
        total = sum(c["total"] for c in per_phase)
        blocked = sum(1 for n in nodes.values() if n["state"] == "BLOCKED")
        w('<div class="head" style="margin-top:44px">')
        w('<h1>Flow</h1>')
        w(f'<div class="sub">{passing} of {total} gates passing &middot; {len(edges)} dependency '
          f'edge(s) &middot; {blocked} blocked &middot; re-measured just now</div>')
        w('</div>')

        w('<div class="par" style="margin-top:14px;overflow-x:auto">')
        w(flowlib.svg())
        w('</div>')

        # Legend. Mandatory: a diagram whose grammar is not stated is a diagram the reader guesses at.
        w('<div class="par" style="margin-top:12px">')
        w('<h3 style="margin-top:0">How to read it</h3>')
        w('<p style="font-size:13px;color:var(--ink2);margin:0">'
          '<b style="color:var(--pass)">&#9679; PASS</b> &middot; '
          '<b style="color:var(--fail)">&#9632; FAIL</b> &middot; '
          '<b style="color:var(--unmeas)">&#9670; UNMEASURABLE</b> &middot; '
          '<b style="color:var(--ink3)">&#9675; NOT_RUN</b></p>')
        w('<p style="font-size:12.5px;color:var(--ink3);margin:8px 0 0">'
          'Each verdict has its own <b>glyph as well as a colour</b>, because colour alone cannot '
          'carry state &mdash; and because <b>UNMEASURABLE is not a worse FAIL</b>. It means the '
          'instrument could not see, which is a different claim and sometimes the more urgent one.'
          '</p>')
        w('<p style="font-size:12.5px;color:var(--ink3);margin:8px 0 0">'
          'A <b>dashed, faded box</b> is <b>BLOCKED</b> &mdash; it cannot start until something '
          'upstream passes, which is a different situation from failing and is drawn differently. '
          'A <b>solid coloured edge</b> is an <i>unmet</i> dependency: the reason its target cannot '
          'begin. A <b>faint dashed edge</b> is a dependency already satisfied &mdash; history, kept '
          'because removing it would make the graph look simpler than it is.</p>')
        if crit:
            w(f'<p style="font-size:12.5px;color:var(--ink2);margin:8px 0 0">'
              f'The <b style="color:var(--fail)">heavy red path</b> is the <b>critical path</b>: '
              f'<code>{e(" &rarr; ".join(crit))}</code> &mdash; the longest chain of unmet '
              f'dependencies, and the one thing no amount of parallelism removes.</p>')
        w('<p style="font-size:12px;color:var(--ink3);margin:8px 0 0">'
          'Every figure here is <b>MEASURED</b> &mdash; the bar under each phase is '
          'passing&divide;total from the same <code>measure()</code> call that drew the nodes, not '
          'a chosen width. Every figure here re-ran when you loaded it &mdash; with one stated '
          'exception, the <code>suite</code> gate, which is cached and says so in its own '
          'headline. A page that claimed to cache nothing while caching something would make '
          'every other number on it unreliable.</p>')
        w('</div>')

        # The shape worth noticing, computed rather than asserted.
        early = [c for c in per_phase if c["phase"] in ("loop", "bounded")]
        late = [c for c in per_phase if c["phase"] in ("certification", "handover")]
        ep, et = sum(c["passing"] for c in early), sum(c["total"] for c in early)
        lp, lt = sum(c["passing"] for c in late), sum(c["total"] for c in late)
        if et and lt and (lp / lt) > (ep / et):
            w('<div class="par" style="margin-top:12px;border-color:var(--unmeas)">')
            w('<h3 style="margin-top:0">&#9888; Progress is inverted</h3>')
            w(f'<p style="font-size:13px;color:var(--ink2);margin:0">The <b>foundational</b> phases '
              f'are at <b>{ep} of {et}</b>, while <b>handover and certification</b> are at '
              f'<b>{lp} of {lt}</b>. The gates nearest the finish are passing and the ones the whole '
              f'thing rests on are not.</p>')
            w('<p style="font-size:12px;color:var(--ink3);margin:8px 0 0">Computed from the phase '
              'counts on every load, not asserted &mdash; if the ordering changes this panel stops '
              'appearing by itself.</p>')
            w('</div>')

    if tab == "research":
        # ------------------------------------------------------------------ what to do next
        # Three failures on 2026-08-23 produced this panel, and each is guarded here:
        #   1. "which prompts did I upload?" was unanswerable — nothing recorded a dispatch.
        #   2. R14 was recorded as sent on the strength of an intention, and never went.
        #   3. R8's answer landed while the currency gate stayed green, because SYNTHESIS.md
        #      mentioned R8 three times in the FUTURE tense.
        todo = [r for r in dispatchlib.order() if r["rank"] <= 4]
        late = synth.unreconciled()
        w('<div class="par" style="margin-top:14px'
          + (';border-color:var(--fail)' if late else '') + '">')
        w('<h3 style="margin-top:0">What to do next</h3>')
        if not todo:
            w('<p style="font-size:13px;color:var(--ink3);margin:0">Nothing outstanding — every '
              'prompt is filed and reconciled.</p>')
        for r in todo:
            colour = {1: "var(--fail)", 0: "var(--fail)", 2: "var(--unmeas)"}.get(
                r["rank"], "var(--ink3)")
            runs = r["runs"]
            w(f'<div style="margin:9px 0 0;padding:7px 0 0;border-top:1px solid var(--rule)">'
              f'<span style="font-family:ui-monospace,monospace;font-size:12px;color:var(--ink3)">'
              f'{e(r["id"])}</span> '
              f'<b style="color:{colour}">{e(r["action"])}</b>'
              f'<span style="font-size:11.5px;color:var(--ink3)"> &middot; {e(r["state"])} '
              f'&middot; {e(runs)} recorded run(s)</span>'
              f'<div style="font-size:12.5px;color:var(--ink2);margin-top:2px">{e(r["why"])}</div>'
              f'</div>')
        w('<p style="font-size:12px;color:var(--ink3);margin:9px 0 0">'
          '<b>Reconciling outranks dispatching, deliberately.</b> An unread answer is work already '
          'paid for and not yet banked; sending another prompt while one sits unreconciled spends '
          'money to widen a backlog. The ordering is a judgement and lives in '
          '<code>factory/dispatch.py::_ACTION</code> so it can be argued with rather than guessed '
          'at.</p>')
        w('</div>')

        # The currency gate, and the reason there are two of them.
        w('<div class="par" style="margin-top:12px">')
        w('<h3 style="margin-top:0">Is the record current?</h3>')
        w(f'<p style="font-size:13px;margin:0">Never mentioned in the synthesis: '
          f'<b>{e(", ".join(synth.unsynthesised()) or "none")}</b><br>'
          f'Filed <i>after</i> the synthesis was last written: '
          f'<b style="color:{"var(--fail)" if late else "var(--pass)"}">'
          f'{e(", ".join(late) or "none")}</b></p>')
        w('<p style="font-size:12px;color:var(--ink3);margin:8px 0 0">'
          'Two checks because the first one is weak on its own. It asks whether the synthesis '
          '<i>mentions</i> an id — and on 2026-08-23 R8\'s answer was filed while the document '
          'said, three times, that R8 was <i>still outstanding</i>. The id was mentioned, in the '
          'future tense, and the gate went green over an answer nobody had read. The second check '
          'compares modification times, which cannot be satisfied by writing an id anywhere.</p>')
        w('</div>')


        # ---------------------------------------------------------------- research prompts
        rdir = FACTORY / "docs" / "research"
        adir = rdir / "answers"
        pending = []
        if rdir.is_dir():
            # Skip generated evidence packs: they match this glob, are hundreds of KB, and
            # embed this file's own source — which is how the tab-leak guard went red on a string
            # from local_tracker.py rather than from any lane content.
            for f in sorted(x for x in rdir.glob("R[0-9]*.md")
                            if not x.stem.upper().endswith("-EVIDENCE-PACK")):
                # R[0-9]* not R* — the plain glob matched README.md and offered it as a research
                # prompt. A directory scan is only as good as its pattern.
                stem = f.name.split("-")[0]
                answered = adir.is_dir() and any(a.name.startswith(f"{stem}-answer") or
                                                 a.name.startswith(f"{stem}-followup-answer")
                                                 for a in adir.glob("*.md"))
                if not answered:
                    pending.append(f)
        # ---------------------------------------------------------------- one-glance state strip
        # Derived from factory.dispatch on every request — the same function `python -m
        # factory.dispatch` prints, so the page and the CLI cannot disagree about what "answered"
        # means. There is no client-side state here and nothing is remembered between requests:
        # a hard refresh re-derives every chip from the files on disk and cannot clear one.
        dstate = disp.state()
        counts = {}
        for v in dstate.values():
            counts[v] = counts.get(v, 0) + 1
        order = sorted(dstate, key=lambda k: (int(k[1:]) if k[1:].isdigit() else 999, k))
        w('<div class="head" style="margin-top:34px">')
        w('<h1>Research</h1>')
        w('<div class="sub">'
          + ' &middot; '.join(f'{counts[k]} {_RCHIP[k][1].lower()}'
                              for k in (disp.ANSWERED, disp.IN_FLIGHT, disp.UNDISPATCHED,
                                        disp.STALE_STATUS, disp.UNKNOWN) if counts.get(k))
          + '</div>')
        w('</div>')
        w('<div style="display:flex;flex-wrap:wrap;gap:7px;margin-top:14px">')
        for rid in order:
            cls, label = _RCHIP.get(dstate[rid], ("notrun", dstate[rid]))
            done = dstate[rid] == disp.ANSWERED
            w(f'<div style="border:1px solid var(--rule);border-left:3px solid var(--{cls});'
              f'background:var(--raise);padding:5px 9px;display:flex;gap:8px;align-items:baseline'
              f'{";opacity:.62" if done else ""}">'
              f'<b style="font-family:ui-monospace,monospace;font-size:12.5px">{e(rid)}</b>'
              f'<span class="chip {cls}">{e(label)}</span></div>')
        w('</div>')
        w('<p style="font-size:12px;color:var(--ink3);margin:9px 0 0">Completed passes are dimmed '
          'and green-edged. Every chip is re-derived from <code>docs/research/</code> on each '
          'request &mdash; <b>a refresh cannot clear one</b>, and none of it is stored in the '
          'browser.</p>')

        gap = synth.unsynthesised()
        late = synth.unreconciled()
        runnable = gap or late
        w('<div class="par" style="margin-top:34px;border-color:'
          + ("var(--unmeas)" if runnable else "var(--rule)") + '">')
        w('<h3 style="margin-top:0">Decision record</h3>')
        if gap:
            w(f'<p style="font-size:13.5px;color:var(--ink2);margin:0 0 8px">'
              f'<b>SYNTHESIS.md does not mention {e(", ".join(gap))}</b>, which have filed '
              f'answers. The record has fallen behind the research it reconciles.</p>')
        # ---------------------------------------------------- the reconcile control
        # ⛔ There used to be no button here, and the page said so in print. That reasoning held
        # while the only mechanism was a paste loop; it does not now. The button dispatches
        # judgement to a session, it does not perform it. See factory/synthesis.py.
        # A claim already held means a session is reconciling right now. Rendering an enabled
        # button that then refuses on POST is a control that lies about its own availability —
        # so the state is shown here, with the release route, exactly as a lane claim is.
        _sv, _sheld = claimlib.task_holder("synthesis")
        held = _sv != claimlib.HELD_GONE
        w('<div style="display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin:0 0 10px">')
        if runnable and not held:
            w('<form method="POST" action="/synthesize/start" style="margin:0">'
              '<button type="submit" style="font-size:12.5px;padding:6px 12px;cursor:pointer;'
              'border:1px solid var(--accent);border-radius:3px;background:var(--raise);'
              'color:var(--accent);font-weight:600;font-family:ui-monospace,monospace">'
              'reconcile it here</button></form>')
            w(f'<span style="font-size:12px;color:var(--ink3)">opens a session that reads '
              f'{e(", ".join(runnable))} in full and writes <code>SYNTHESIS.md</code> &mdash; '
              f'<b>that one file only</b></span>')
        elif runnable and held:
            since = ""
            try:
                import datetime as _dtm
                _s = _dtm.datetime.fromisoformat((_sheld or {}).get("since", ""))
                since = " · started " + claimlib.Claim("synthesis", _s, "").human_age()
            except Exception:                                       # noqa: BLE001
                pass
            w('<button type="button" disabled title="a reconcile session already holds this" '
              'style="font-size:12.5px;padding:6px 12px;cursor:not-allowed;border:1px solid '
              'var(--rule);border-radius:3px;background:var(--raise);color:var(--ink3);'
              'font-family:ui-monospace,monospace">reconcile it here</button>')
            w(f'<span style="font-size:12px;color:var(--ink3)"><b>a session is reconciling '
              f'now</b>{e(since)} &mdash; a second one would write the same file and the loser\'s '
              f'pass would vanish. <a href="/release-task/synthesis">release</a> if it is gone.'
              f'</span>')
        else:
            w('<button type="button" disabled title="nothing outstanding to reconcile" '
              'style="font-size:12.5px;padding:6px 12px;cursor:not-allowed;border:1px solid '
              'var(--rule);border-radius:3px;background:var(--raise);color:var(--ink3);'
              'font-family:ui-monospace,monospace">reconcile it here</button>')
            w('<span style="font-size:12px;color:var(--ink3)">nothing outstanding</span>')
        w('</div>')
        if runnable:
            w('<div class="dep" style="margin:-2px 0 10px">⚠ This dispatches the judgement, it '
              'does not perform it &mdash; and <b>neither check below can tell a real '
              'reconciliation from one sentence per answer</b>. Read what it writes.</div>')
            w('<button type="button" data-copy="synth-prompt" style="font-size:12px;'
              'padding:5px 10px;margin-bottom:8px;cursor:pointer;border:1px solid var(--rule);'
              'border-radius:3px;background:var(--raise);color:var(--ink);'
              'font-family:ui-monospace,monospace">copy reconciling prompt</button>')
            w(f'<pre id="synth-prompt" style="white-space:pre-wrap;word-break:break-word;'
              f'font-family:ui-monospace,monospace;font-size:11.5px;line-height:1.55;margin:0;'
              f'padding:10px;border:1px solid var(--rule);border-radius:3px;'
              f'background:var(--paper);color:var(--ink2);max-height:220px;overflow:auto">'
              f'{e(synth.prompt())}</pre>')
        else:
            w('<p style="font-size:13.5px;color:var(--ink2);margin:0">'
              '<code>docs/research/SYNTHESIS.md</code> mentions every filed answer.</p>')
        # Deliberately not "up to date": the check asserts MENTION, not engagement. The
        # no-synthesize-button rule that used to live here is superseded — a button can now open a
        # session that does the reading, which is a different thing from a button that fakes it.
        # What has NOT changed is that neither check can see whether the reading happened.
        w('<p style="font-size:12px;color:var(--ink3);margin:8px 0 0">Checks that each answer is '
          '<i>mentioned</i>, not that it was engaged with &mdash; it catches a record nobody '
          'touched, and nothing subtler. The button above dispatches the judgement to a session; '
          'it does not exercise it, and <b>a run that writes one sentence per answer clears both '
          'checks</b>.</p>')
        w('</div>')

        # Always render the heading, even with nothing outstanding: a nav link to a blank page
        # reads as broken, and "everything is answered" is a real and useful state to see.
        filed = sorted(adir.glob("R[0-9]*-answer*.md")) if adir.is_dir() else []
        if not pending:
            w('<div class="head" style="margin-top:44px">')
            w('<h1>Nothing outstanding</h1>')
            w(f'<div class="sub">Every written prompt has a filed '
              f'answer. Write a new one into <code>docs/research/</code> as '
              f'<code>R&lt;n&gt;-&lt;topic&gt;.md</code> and it appears here automatically.</div>')
            w('</div>')
        if pending:
            w('<div class="head" style="margin-top:44px">')
            w('<h1>Run a research pass</h1>')
            w(f'<div class="sub">{len(pending)} prompt(s) written and not yet answered &middot; '
              'paste into Deep Research; the answer lands in '
              '<code>docs/research/answers/</code></div>')
            w('</div>')
            for f in pending:
                body = f.read_text(encoding="utf-8")
                first = next((ln.lstrip("# ").strip() for ln in body.splitlines()
                              if ln.startswith("# ")), f.stem)
                rid = f.name.split("-")[0].upper()
                cls, label = _RCHIP.get(dstate.get(rid, ""), ("notrun", "UNKNOWN"))
                w(f'<div class="par" style="margin-top:16px;border-left:3px solid var(--{cls})">')
                w(f'<h3>{e(first)} <span class="chip {cls}">{e(label)}</span></h3>')
                w(f'<p style="font-size:12.5px;color:var(--ink3);margin:0 0 8px">'
                  f'<code>docs/research/{e(f.name)}</code> &middot; {len(body):,} chars &middot; '
                  f'written {e(_ago(f.stat().st_mtime))}</p>')
                # ------------------------------------------------ dispatch control
                # ⛔ THREE passes, THREE meanings of "start", and one label would lie about two.
                # Only a CLAUDE_CODE pass runs here; R16 and R17 are pasted into somebody else's
                # product, so their button prepares the payload and RECORDS the send rather than
                # claiming to have made it. A launcher that announced the model it was running
                # while running a different one is already in this repo's findings ledger.
                try:
                    pl = rrun.plan(rid, dstate)
                except Exception as exc:                            # noqa: BLE001
                    pl = None
                    w(f'<div class="dep">could not read the declarations in this prompt: '
                      f'{e(type(exc).__name__)}</div>')
                if pl:
                    ok = pl["eligible"] == rrun.READY
                    w('<div style="display:flex;gap:10px;align-items:center;flex-wrap:wrap;'
                      'margin:0 0 10px">')
                    if ok:
                        w(f'<form method="POST" action="/research/start" style="margin:0">'
                          f'<input type="hidden" name="id" value="{e(pl["id"])}">'
                          f'<button type="submit" style="font-size:12.5px;padding:6px 12px;'
                          f'cursor:pointer;border:1px solid var(--accent);border-radius:3px;'
                          f'background:var(--raise);color:var(--accent);font-weight:600;'
                          f'font-family:ui-monospace,monospace">{e(pl["action"])}</button></form>')
                    else:
                        w(f'<button type="button" disabled title="{e(pl["why"])}" '
                          f'style="font-size:12.5px;padding:6px 12px;cursor:not-allowed;'
                          f'border:1px solid var(--rule);border-radius:3px;background:var(--raise);'
                          f'color:var(--ink3);font-family:ui-monospace,monospace">'
                          f'{e(pl["action"] or "no action")}</button>')
                    risk = pl.get("risk") or ""
                    rc = ("var(--fail)" if risk in ("SEVERE", "HIGH")
                          else "var(--unmeas)" if risk == "MEDIUM" else "var(--ink3)")
                    w(f'<span style="font-size:12px;color:var(--ink3)">'
                      f'<b>{e(pl.get("pass_type", ""))}</b> &middot; {e(pl.get("shape", ""))}'
                      + (f' &middot; independence risk <b style="color:{rc}">{e(risk)}</b>'
                         if risk else '')
                      + (f' &middot; pack <code>{e(pl["pack"])}</code>' if pl["pack"] else '')
                      + '</span>')
                    w('</div>')
                    if not ok:
                        w(f'<div class="dep" style="margin:-4px 0 10px">'
                          f'{e(pl["eligible"])} &mdash; {e(pl["why"])}</div>')
                    else:
                        # Say what the click actually spends, before it is spent.
                        w('<div class="dep" style="margin:-4px 0 10px">opens a session here that '
                          'invokes the <code>deep-research</code> skill against this brief, and '
                          'marks the prompt DISPATCHED. The answer is written straight to '
                          '<code>docs/research/answers/</code> &mdash; <b>no paste, no upload</b>.'
                          + ('  ⛔ BLIND-FIRST: this pass reads our own material, so it forms a '
                             'view from the primary source before reading our conclusions.'
                             if pl.get("risk") in ("HIGH", "SEVERE") else '')
                          + '</div>')
                w(f'<button type="button" data-copy="rs-{e(f.stem)}" style="font-size:12px;'
                  f'padding:5px 10px;margin-bottom:8px;cursor:pointer;border:1px solid var(--rule);'
                  f'border-radius:3px;background:var(--raise);color:var(--ink);'
                  f'font-family:ui-monospace,monospace">copy full prompt</button>')
                w(f'<pre id="rs-{e(f.stem)}" style="white-space:pre-wrap;word-break:break-word;'
                  f'font-family:ui-monospace,monospace;font-size:11.5px;line-height:1.55;margin:0;'
                  f'padding:10px;border:1px solid var(--rule);border-radius:3px;'
                  f'background:var(--paper);color:var(--ink2);max-height:260px;overflow:auto">'
                  f'{e(body)}</pre>')
                dest = _answer_path(f).name
                w('<form method="POST" action="/answer" enctype="multipart/form-data" '
                  'style="margin-top:12px">')
                w(f'<input type="hidden" name="stem" value="{e(f.stem)}">')
                w(f'<div style="font-size:12.5px;color:var(--ink3);margin-bottom:6px">'
                  f'Saved as <code>docs/research/answers/{e(dest)}</code> &mdash; the path the gate '
                  f'reads. There is no &ldquo;notify Claude&rdquo; button because this page has no '
                  f'channel to a session; <b>the saved file is the signal</b>, and a session watching '
                  f'that directory picks it up.</div>')
                w('<div style="margin-bottom:8px"><input type="file" name="file" '
                  'accept=".md,.txt,.markdown,text/plain,text/markdown" '
                  'style="font-size:12px;color:var(--ink2)">'
                  '<span style="font-size:12px;color:var(--ink3)"> &nbsp;upload a file, '
                  '<b>or</b> paste below &mdash; the file wins if you do both</span></div>')
                w('<textarea name="body" rows="6" placeholder="…or paste the answer here, then save" '
                  'style="width:100%;box-sizing:border-box;font-family:ui-monospace,monospace;'
                  'font-size:11.5px;line-height:1.5;padding:10px;border:1px solid var(--rule);'
                  'border-radius:3px;background:var(--paper);color:var(--ink)"></textarea>')
                w('<button type="submit" style="font-size:12px;padding:6px 12px;margin-top:8px;'
                  'cursor:pointer;border:1px solid var(--rule);border-radius:3px;'
                  'background:var(--raise);color:var(--ink);font-family:ui-monospace,monospace">'
                  'save answer</button>')
                w('</form>')
                w('</div>')
        if filed:
            w('<div class="head" style="margin-top:40px">')
            w('<h1>Answered</h1>')
            w(f'<div class="sub">{len(filed)} filed &middot; the prompt drops off the list above '
              'once its answer lands</div>')
            w('</div>')
            for a in filed:
                first = next((ln.lstrip("# ").strip()
                              for ln in a.read_text(encoding="utf-8", errors="replace").splitlines()
                              if ln.startswith("# ")), a.stem)
                st = a.stat()
                w('<div class="par" style="margin-top:12px;border-left:3px solid var(--pass)">')
                w(f'<h3 style="margin-top:0">{e(first)} '
                  f'<span class="chip pass">ANSWERED</span></h3>')
                w(f'<p style="font-size:12.5px;color:var(--ink3);margin:0">'
                  f'<code>docs/research/answers/{e(a.name)}</code> &middot; '
                  f'{st.st_size:,} bytes &middot; filed {e(_ago(st.st_mtime))}</p>')
                w('</div>')

    if tab == "switchboard":
        # ⭐ One join over state that already existed, rendered by `factory.switchboard_p1`.
        # The tab body is deliberately thin: everything that could be wrong lives in the
        # projection, where a test can reach it without parsing HTML.
        #
        # P0's `switchboard_render.page` is NOT deleted — it is the MISSION view, reached from
        # the nav. Every panel it renders is still on the estate; none of them is first.
        try:
            _st = sblib.state()
            if view == "dispatch":
                w(sbr.page(_st, dispatch=_DISPATCH))
            else:
                # Read-and-clear: a flash that survived a refresh would read as a live condition
                # rather than as the outcome of the act that produced it.
                global _SB_MSG
                _flash, _SB_MSG = _SB_MSG, None
                w(sbp1.page(_st, view=view, inspect=inspect, q=q,
                            token=RESTART_TOKEN, runtime=RUNTIME_ID,
                            flash=_flash, repos=_repo_choices(), dispatch=_DISPATCH,
                            panes=panes, lay=lay, popout=popout))
        except Exception as _exc:                                  # noqa: BLE001
            # A command page that 500s tells the operator nothing. A command page that says
            # WHICH instrument failed tells them where to look, and keeps the nav reachable.
            w('<div class="par" style="border-color:var(--fail)">'
              '<h3 style="margin:0;color:var(--fail)">Switchboard could not measure</h3>'
              '<p style="font-size:13px;margin:8px 0 0"><code>%s: %s</code></p>'
              '<p style="font-size:13px;color:var(--ink3);margin:6px 0 0">Nothing was written. '
              'The other tabs are unaffected.</p></div>'
              % (e(type(_exc).__name__), e(_exc)))

    if tab == "handoff":
        w('<div class="head" style="margin-top:34px">')
        w('<h1>Hand this session on</h1>')
        w('<div class="sub">Generated from measured state &mdash; gate verdicts, velocity, '
          'claims, worktrees, ledger and decision record. The only part you write is the bit '
          'no instrument can see.</div>')
        w('</div>')
        w('<form method="POST" action="/handoff" style="margin-top:16px">')
        w('<div style="font-size:13px;color:var(--ink2);margin-bottom:6px">'
          'What were you part-way through, and what would you warn the next session about?</div>')
        w('<textarea name="note" rows="4" placeholder="the part the repo cannot tell them" '
          'style="width:100%;box-sizing:border-box;font-family:ui-monospace,monospace;'
          'font-size:12px;padding:9px;border:1px solid var(--rule);border-radius:3px;'
          'background:var(--paper);color:var(--ink)"></textarea>')
        w('<button type="submit" style="font-size:12.5px;padding:6px 14px;margin-top:8px;'
          'cursor:pointer;border:1px solid var(--rule);border-radius:3px;background:var(--raise);'
          'color:var(--ink);font-family:ui-monospace,monospace">add this note to the handoff below</button>')
        w('</form>')
        text = ho.session_handoff(_HANDOFF_NOTE)
        w('<form method="POST" action="/new-session" style="display:inline">')
        w(f'<input type="hidden" name="note" value="{e(_HANDOFF_NOTE)}">')
        w('<button type="submit" style="font-size:12.5px;padding:6px 14px;margin:14px 6px 8px 0;'
          'cursor:pointer;border:1px solid var(--pass);border-radius:3px;background:var(--pass);'
          'color:var(--paper);font-family:ui-monospace,monospace">'
          '&#9654; open a new session with this handoff</button>')
        w('</form>')
        w('<button type="button" data-copy="handoff-text" style="font-size:12.5px;'
          'padding:6px 14px;margin:14px 0 8px;cursor:pointer;border:1px solid var(--rule);'
          'border-radius:3px;background:var(--raise);color:var(--ink);'
          'font-family:ui-monospace,monospace">copy handoff</button>')
        w(f'<pre id="handoff-text" style="white-space:pre-wrap;word-break:break-word;'
          f'font-family:ui-monospace,monospace;font-size:11.5px;line-height:1.55;margin:0;'
          f'padding:12px;border:1px solid var(--rule);border-radius:3px;background:var(--paper);'
          f'color:var(--ink2)">{e(text)}</pre>')
        w('<p style="font-size:12px;color:var(--ink3);margin:10px 0 0">Paste this into a fresh '
          'session. For a durable copy, a lane writes its own note to '
          '<code>aldc-launchpad/boot-prompts/</code> when you finish it below.</p>')

    w('<footer>')
    w('<p><b>UNMEASURABLE is not a pass.</b> A gate with no instrument says so rather than '
      'waving through; that distinction is the point of the whole harness.</p>')
    w('<p>Every row is measured from a file at the moment shown above and names the path it came '
      'from. Nothing here is hand-maintained, so a wrong row means a wrong repo, not a stale '
      'page. Probes live in <code>factory/readiness.py</code>.</p>')
    w('<p><b>The work list is the gate list.</b> Every gate that is not passing is a task, and a '
      'gate that passes stops being one. There is no second list to keep in sync, so the board '
      'cannot describe work nobody measures or omit work somebody does. The only authored part is '
      'which task must precede which, and a stale edge fails on import.</p>')
    w('<p>Regenerate: <code>python scripts/local_tracker.py</code> &middot; '
      'serve and re-measure on refresh: <code>python scripts/local_tracker.py --serve</code> '
      '&middot; check the published artifact still matches: '
      '<code>python scripts/build_tracker.py --check</code></p>')
    w("""</footer></div>
<script>
document.querySelectorAll('[data-copy]').forEach(function (b) {
  b.addEventListener('click', function () {
    var el = document.getElementById(b.getAttribute('data-copy'));
    if (!el) return;
    var label = b.textContent;
    var done = function () { b.textContent = 'copied';
                             setTimeout(function () { b.textContent = label; }, 1200); };
    // The textarea path is the fallback where the Clipboard API is unavailable. The text is
    // selectable either way, so a failure is never a dead end.
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(el.textContent).then(done, function () {});
    } else {
      var ta = document.createElement('textarea');
      ta.value = el.textContent; document.body.appendChild(ta); ta.select();
      try { document.execCommand('copy'); done(); } catch (err) {}
      document.body.removeChild(ta);
    }
  });
});
</script></body></html>""")
    return "\n".join(o)


class Handler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        global _ANSWER_MSG, _CLAIM_MSG, _HANDOFF_NOTE, _SB_MSG
        import urllib.parse
        if self.path.rstrip("/") == "/finish":
            raw = self.rfile.read(int(self.headers.get("Content-Length") or 0)).decode("utf-8", "replace")
            f = urllib.parse.parse_qs(raw, keep_blank_values=True)
            lane_id = (f.get("lane") or [""])[0]
            try:
                path, checks = ho.write_lane_handoff(lane_id, (f.get("note") or [""])[0])
                fails = [c["check"] for c in checks if not c["ok"]]
                claimlib.release(lane_id)
                _CLAIM_MSG = (not fails,
                              f"finished {lane_id} — handoff at {path.name}, claim released"
                              + (f"; ⚠ {len(fails)} preflight check(s) failed: "
                                 + ", ".join(fails) if fails else "; preflight all green"))
            except Exception as exc:                                # noqa: BLE001
                _CLAIM_MSG = (False, f"could not finish {lane_id}: {type(exc).__name__}: {exc}")
            print(f"  finish: {_CLAIM_MSG[1]}")
            self.send_response(303); self.send_header("Location", "/lanes"); self.end_headers()
            return
        if self.path.rstrip("/") == "/switchboard/dispatch":
            raw = self.rfile.read(int(self.headers.get("Content-Length") or 0)).decode("utf-8", "replace")
            q = urllib.parse.parse_qs(raw, keep_blank_values=True)
            _CLAIM_MSG = quick_dispatch(
                (q.get("prompt") or [""])[0],
                target_session_id=(q.get("session") or [""])[0].strip(),
                dry=bool((q.get("dry") or [""])[0]))
            print(f"  switchboard/dispatch: {_CLAIM_MSG[1]}")
            self.send_response(303); self.send_header("Location", "/switchboard")
            self.send_header("Cache-Control", "no-store"); self.end_headers()
            return
        if self.path.rstrip("/") == "/switchboard/create":
            raw = self.rfile.read(int(self.headers.get("Content-Length") or 0)).decode("utf-8", "replace")
            q = urllib.parse.parse_qs(raw, keep_blank_values=True)
            _SB_MSG = create_work(
                title=(q.get("title") or [""])[0],
                objective=(q.get("objective") or [""])[0],
                repo=(q.get("repo") or [""])[0],
                visibility=(q.get("visibility") or ["PRIVATE"])[0],
                work_id=(q.get("work_id") or [""])[0],
                depends_on=(q.get("depends_on") or [""])[0],
                resource_claim=(q.get("resource_claim") or [""])[0],
                access=(q.get("access") or ["WRITE"])[0])
            print(f"  switchboard/create: {_SB_MSG[1]}")
            self.send_response(303)
            self.send_header("Location", "/switchboard?view=now" if _SB_MSG[0]
                             else "/switchboard?view=create")
            self.send_header("Cache-Control", "no-store"); self.end_headers()
            return
        if self.path.rstrip("/") == "/switchboard/resolve":
            raw = self.rfile.read(int(self.headers.get("Content-Length") or 0)).decode("utf-8", "replace")
            q = urllib.parse.parse_qs(raw, keep_blank_values=True)
            _SB_MSG = resolve_hold(
                (q.get("work_id") or [""])[0],
                hold=(q.get("hold") or [""])[0],
                decision=(q.get("go") or [""])[0],
                note=(q.get("note") or [""])[0])
            print(f"  switchboard/resolve: {_SB_MSG[1]}")
            self.send_response(303)
            self.send_header("Location", "/switchboard?view=now")
            self.send_header("Cache-Control", "no-store"); self.end_headers()
            return
        if self.path.rstrip("/") == "/switchboard/autonomy":
            raw = self.rfile.read(int(self.headers.get("Content-Length") or 0)).decode("utf-8", "replace")
            q = urllib.parse.parse_qs(raw, keep_blank_values=True)
            _SB_MSG = set_autonomy(
                (q.get("work_id") or [""])[0].strip(),
                to=(q.get("to") or [""])[0].strip(),
                go=(q.get("go") or [""])[0].strip())
            print(f"  switchboard/autonomy: {_SB_MSG[1]}")
            self.send_response(303)
            self.send_header("Location", "/switchboard?view=now&inspect="
                             + urllib.parse.quote((q.get("work_id") or [""])[0].strip()[:64]))
            self.send_header("Cache-Control", "no-store"); self.end_headers()
            return
        if self.path.rstrip("/") == "/switchboard/restart":
            ok, why = self._restart_allowed()
            if not ok:
                print(f"  switchboard/restart: REFUSED — {why}")
                self.send_response(403)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write(f"REFUSED: {why}\n".encode("utf-8"))
                return
            # ⛔ The action is FIXED. Nothing from the request reaches it — no command, no path,
            # no argument, no shell. The only effect this endpoint can have is "this process
            # exits with RESTART_EXIT", and the supervisor decides what that means.
            globals()["_RESTART_REQUESTED"] = True
            print("  switchboard/restart: accepted — exiting for the supervisor to replace")
            body = json.dumps({"restarting": True, "runtime": RUNTIME_ID}).encode("utf-8")
            self.send_response(202)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Connection", "close")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)
            try:
                self.wfile.flush()
            except Exception:                                       # noqa: BLE001
                pass
            # Shut the accept loop down from another thread; `shutdown()` blocks if called from
            # inside a handler on the serving thread, which would deadlock the very request that
            # is trying to answer.
            import threading as _th
            _th.Thread(target=self.server.shutdown, daemon=True).start()
            return
        if self.path.rstrip("/") == "/switchboard/start":
            raw = self.rfile.read(int(self.headers.get("Content-Length") or 0)).decode("utf-8", "replace")
            q = urllib.parse.parse_qs(raw, keep_blank_values=True)
            _CLAIM_MSG = start_synced(
                target=(q.get("target") or [""])[0].strip(),
                note=(q.get("note") or [""])[0],
                reader=(q.get("reader") or [""])[0].strip(),
                worktree=(q.get("worktree") or [""])[0].strip(),
                # The submit button's own value carries the mode, exactly as /run-ticket does.
                # A dry run that dispatches is worse than none at all.
                dry=bool((q.get("dry") or [""])[0]),
                gate_handoff=bool((q.get("gate") or [""])[0]))
            _SB_MSG = _CLAIM_MSG
            print(f"  switchboard/start: {_CLAIM_MSG[1]}")
            self.send_response(303); self.send_header("Location", "/switchboard")
            self.send_header("Cache-Control", "no-store"); self.end_headers()
            return
        if self.path.rstrip("/") == "/run-ticket":
            raw = self.rfile.read(int(self.headers.get("Content-Length") or 0)).decode("utf-8", "replace")
            q = urllib.parse.parse_qs(raw, keep_blank_values=True)
            _CLAIM_MSG = run_ticket(
                (q.get("ticket") or [""])[0], title=(q.get("title") or [""])[0],
                type_id=(q.get("type") or [""])[0],
                # ⚠ The submit button's own value carries the mode, so "plan only" and "start" are
                # two buttons on one form rather than a checkbox somebody forgets to tick. A dry
                # run that dispatches is worse than none at all — that lesson is already recorded
                # against `start_research_pass`, which checked its flag three statements too late.
                dry=bool((q.get("dry") or [""])[0]))
            print(f"  run-ticket: {_CLAIM_MSG[1]}")
            self.send_response(303); self.send_header("Location", "/"); self.end_headers()
            return
        if self.path.rstrip("/") == "/research/start":
            raw = self.rfile.read(int(self.headers.get("Content-Length") or 0)).decode("utf-8", "replace")
            q = urllib.parse.parse_qs(raw, keep_blank_values=True)
            _CLAIM_MSG = start_research_pass((q.get("id") or [""])[0],
                                             dry="dry" in (q.get("mode") or []))
            print(f"  research/start: {_CLAIM_MSG[1]}")
            self.send_response(303)
            self.send_header("Location", "/research")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            return
        if self.path.rstrip("/") == "/synthesize/start":
            raw = self.rfile.read(int(self.headers.get("Content-Length") or 0)).decode("utf-8", "replace")
            q = urllib.parse.parse_qs(raw, keep_blank_values=True)
            _CLAIM_MSG = start_synthesis_pass(dry="dry" in (q.get("mode") or []))
            print(f"  synthesize/start: {_CLAIM_MSG[1]}")
            self.send_response(303)
            self.send_header("Location", "/research")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            return
        if self.path.rstrip("/") == "/new-session":
            raw = self.rfile.read(int(self.headers.get("Content-Length") or 0)).decode("utf-8", "replace")
            q = urllib.parse.parse_qs(raw, keep_blank_values=True)
            _HANDOFF_NOTE = (q.get("note") or [""])[0]
            _CLAIM_MSG = start_session_from_handoff(_HANDOFF_NOTE,
                                                    dry="dry" in (q.get("mode") or []))
            print(f"  new-session: {_CLAIM_MSG[1]}")
            self.send_response(303); self.send_header("Location", "/handoff"); self.end_headers()
            return
        if self.path.rstrip("/") == "/handoff":
            raw = self.rfile.read(int(self.headers.get("Content-Length") or 0)).decode("utf-8", "replace")
            _HANDOFF_NOTE = (urllib.parse.parse_qs(raw, keep_blank_values=True).get("note") or [""])[0]
            self.send_response(303); self.send_header("Location", "/handoff"); self.end_headers()
            return
        if self.path.rstrip("/") == "/answer-blocker":
            raw = self.rfile.read(int(self.headers.get("Content-Length") or 0)).decode("utf-8", "replace")
            f = urllib.parse.parse_qs(raw, keep_blank_values=True)
            try:
                opans.record((f.get("lane") or [""])[0], (f.get("text") or [""])[0])
                _CLAIM_MSG = (True, f"answer recorded for {(f.get('lane') or [''])[0]} — it will "
                                    "be appended to that lane's prompt")
            except opans.OperatorError as exc:
                _CLAIM_MSG = (False, str(exc))
            self.send_response(303); self.send_header("Location", "/lanes"); self.end_headers()
            return
        if self.path.rstrip("/") != "/answer":
            self.send_error(404)
            return
        try:
            n = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            n = 0
        ctype = self.headers.get("Content-Type", "")
        if n > MAX_UPLOAD:
            _ANSWER_MSG = (False, f"body is {n:,} bytes, over the {MAX_UPLOAD:,} cap")
            self.send_response(303)
            self.send_header("Location", "/")
            self.end_headers()
            return
        blob = self.rfile.read(n) if n else b""
        if ctype.startswith("multipart/form-data"):
            form = _parse_multipart(blob, ctype)
            stem, pasted, uploaded = form.get("stem", ""), form.get("body", ""), form.get("file", "")
        else:
            q = urllib.parse.parse_qs(blob.decode("utf-8", "replace"), keep_blank_values=True)
            stem, pasted, uploaded = ((q.get("stem") or [""])[0], (q.get("body") or [""])[0], "")
        # The file wins when both are supplied: picking a file is the more deliberate act, and
        # silently preferring a half-filled textarea over it would be the wrong surprise.
        _ANSWER_MSG = save_answer(stem, uploaded or pasted)
        _log_answer_attempt(stem, ctype, n, _ANSWER_MSG[0], _ANSWER_MSG[1])
        print(f"  answer: {_ANSWER_MSG[1]}")
        self.send_response(303)
        self.send_header("Location", "/research")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()

    def do_GET(self):
        global _RELOAD_MSG
        global _SYNC_MSG
        global _CLAIM_MSG
        import urllib.parse
        # ⭐ The readiness endpoint the restart poll reads. It returns the PROCESS identity, not
        # merely a 200: the browser reloads only when `runtime` differs from the one its page was
        # rendered with, so the dying process answering one last 200 cannot be mistaken for a
        # completed restart. Deliberately the cheapest handler on the server — it measures
        # nothing, because a health check that runs the projection would be unavailable during
        # exactly the moments it exists to observe.
        if urllib.parse.urlparse(self.path).path.rstrip("/") == "/healthz":
            payload = json.dumps({"ok": True, "runtime": RUNTIME_ID, "pid": os.getpid(),
                                  "supervised": bool(RESTART_TOKEN)}).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(payload)
            return
        # The escape hatch for a task claim whose session is gone. A guard with no release is a
        # wedged button, and this module's own rule is that a stale claim blocks but always says
        # how to clear it — never expires quietly.
        tm = re.match(r"^/release-task/([a-z0-9-]+)$", self.path.rstrip("/"))
        if tm:
            dropped = claimlib.task_release(tm.group(1))
            _CLAIM_MSG = (True, f"released the {tm.group(1)} claim" if dropped
                          else f"no {tm.group(1)} claim to release")
            self.send_response(303); self.send_header("Location", "/research"); self.end_headers()
            return
        um = re.match(r"^/unanswer/([a-z0-9-]+)$", self.path.rstrip("/"))
        if um:
            ok = opans.clear(um.group(1))
            _CLAIM_MSG = (True, f"cleared the answer for {um.group(1)}" if ok else "nothing to clear")
            self.send_response(303); self.send_header("Location", "/lanes"); self.end_headers()
            return
        rm_ = re.match(r"^/switchboard/resume/([A-Za-z0-9-]{1,64})$",
                       urllib.parse.urlparse(self.path).path.rstrip("/"))
        if rm_:
            dry = "dry=1" in (urllib.parse.urlparse(self.path).query or "")
            _CLAIM_MSG = resume_session(rm_.group(1), dry=dry)
            print(f"  switchboard/resume: {_CLAIM_MSG[1]}")
            self.send_response(303); self.send_header("Location", "/switchboard")
            self.send_header("Cache-Control", "no-store"); self.end_headers()
            return
        if self.path.rstrip("/") == "/start-all":
            import subprocess as _sp
            dry = "dry=1" in (urllib.parse.urlparse(self.path).query or "")
            eligible, skipped = [], []
            for lid in claimlib.parallel_set():
                lane = next((l for l in LANES if l.id == lid), None)
                # A lane whose declared blocker is unanswered would launch and immediately ask.
                # Skipping it here is the whole point of pre-answering.
                if lane is not None and lane.needs_paul and not opans.get(lid):
                    skipped.append(f"{lid} (blocker unanswered)")
                    continue
                # Claim BEFORE building the command, so a lane that cannot be claimed never
                # reaches the terminal, and a partial failure leaves no orphan claims.
                try:
                    claimlib.claim(lid, who="start-all")
                    eligible.append(lid)
                except claimlib.ClaimError as exc:
                    skipped.append(f"{lid} ({exc})")
            done = []
            if eligible and _wt():
                panes = "layout=tabs" not in (urllib.parse.urlparse(self.path).query or "")
                cmd, done = start_all_command(eligible, make=not dry, panes=panes)
                if dry:
                    for lid in eligible:
                        claimlib.release(lid)
                    _CLAIM_MSG = (True, f"DRY RUN — one wt window, {len(done)} tab(s): "
                                        + ", ".join(done))
                    self.send_response(303); self.send_header("Location", "/lanes"); self.end_headers()
                    return
                try:
                    _sp.Popen(cmd, close_fds=True)
                except Exception as exc:                            # noqa: BLE001
                    for lid in eligible:
                        claimlib.release(lid)
                    done, skipped = [], skipped + [f"all ({type(exc).__name__}: {exc})"]
            elif eligible:
                # No Windows Terminal: fall back to one window each rather than doing nothing.
                for lid in eligible:
                    claimlib.release(lid)
                    ok, msg = launch(lid)
                    (done if ok else skipped).append(lid if ok else f"{lid} ({msg})")
            _CLAIM_MSG = (bool(done),
                          (f"started {len(done)} lane(s) in one Windows Terminal window: "
                           + ", ".join(done) if done and _wt()
                           else "started " + (", ".join(done) or "nothing"))
                          + ("; skipped " + "; ".join(skipped) if skipped else ""))
            print(f"  start-all: {_CLAIM_MSG[1]}")
            self.send_response(303); self.send_header("Location", "/lanes"); self.end_headers()
            return
        lm = re.match(r"^/start/([a-z0-9-]+)$", urllib.parse.urlparse(self.path).path.rstrip("/"))
        if lm:
            dry = "dry=1" in (urllib.parse.urlparse(self.path).query or "")
            _CLAIM_MSG = launch(lm.group(1), dry=dry)
            print(f"  start: {_CLAIM_MSG[1]}")
            self.send_response(303)
            self.send_header("Location", "/lanes")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            return
        m = re.match(r"^/(claim|release)/([a-z0-9-]+)$", self.path.rstrip("/"))
        if m:
            verb, lane = m.group(1), m.group(2)
            try:
                if verb == "claim":
                    c = claimlib.claim(lane, who="via tracker")
                    _CLAIM_MSG = (True, f"claimed {c.lane} — copy its prompt and start a session")
                else:
                    ok = claimlib.release(lane)
                    _CLAIM_MSG = (True, f"released {lane}" if ok else f"{lane} was not claimed")
            except claimlib.ClaimError as exc:
                _CLAIM_MSG = (False, str(exc))
            print(f"  {verb}: {_CLAIM_MSG[1]}")
            self.send_response(303)
            self.send_header("Location", "/lanes")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            return
        if self.path.rstrip("/") == "/sync":
            _SYNC_MSG = sync_artifact()
            self.send_response(303)
            self.send_header("Location", "/")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            print(f"  sync: {_SYNC_MSG[1]}")
            return
        if self.path.rstrip("/") == "/reload":
            _RELOAD_MSG = hot_reload()
            self.send_response(303)
            self.send_header("Location", "/")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            print(f"  hot reload: {_RELOAD_MSG[1]}")
            return
        # ⛔ This used `self.path` raw, so ANY query string 404'd -- `/lanes?team=X` was
        # unreachable and the failure looked like a broken link rather than a parsing bug.
        parsed = urllib.parse.urlparse(self.path)
        route = {"/": "tickets", "/index.html": "tickets", "/tickets": "tickets",
                 "/gates": "gates", "/flow": "flow",
                 "/goals": "goals", "/roadmap": "roadmap",
                 "/lanes": "lanes", "/sessions": "sessions", "/research": "research",
                 "/handoff": "handoff",
                 "/switchboard": "switchboard"}.get(parsed.path.rstrip("/") or "/")
        if route is None:
            self.send_error(404)
            return
        qs = urllib.parse.parse_qs(parsed.query or "")
        sel = (qs.get("team") or [""])[0]
        # ⛔ Every one of these reaches HTML. `view` and `inspect` are constrained here rather
        # than escaped at each use: `view` to the known set, `inspect` to the task-id character
        # class. A reflected value that reaches an attribute is the one injection this page could
        # actually have, and the closed set removes the class rather than the instance.
        _view = (qs.get("view") or ["now"])[0][:32]
        if _view not in dict(sbp1.VIEWS) and _view not in dict(sbp1.MORE_VIEWS) \
                and _view not in ("create", "dispatch"):
            _view = "now"
        _insp = (qs.get("inspect") or [""])[0][:64]
        if not re.fullmatch(r"[A-Za-z0-9._-]{0,64}", _insp or ""):
            _insp = ""
        _q = (qs.get("q") or [""])[0][:80]
        # Console state. `panes` is a comma-separated list of session ids and reaches HTML and a
        # filesystem glob, so it is constrained to the id character class here rather than escaped
        # at each use -- the same closed-set rule `inspect` follows.
        _panes = ",".join([x for x in (qs.get("panes") or [""])[0].split(",")
                           if re.fullmatch(r"[A-Za-z0-9._-]{1,128}", x)][:4])
        _lay = (qs.get("lay") or ["1"])[0][:4]
        _popout = bool((qs.get("popout") or [""])[0])
        # Re-measure per request. Slower than serving a file, and the entire reason to serve.
        body = render(datetime.datetime.now(), route, team=sel,
                      view=_view, inspect=_insp, q=_q,
                      panes=_panes, lay=_lay, popout=_popout).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    #: Hosts a same-origin request may legitimately carry. The server binds loopback only, so a
    #: request whose Origin names anything else is either a cross-site POST or a proxy that is
    #: rewriting the origin — and neither is a case where killing the server is the right answer.
    _LOCAL_HOSTS = ("127.0.0.1", "localhost", "[::1]", "::1")

    def _restart_allowed(self):
        """Four independent conditions, ALL required. Returns (ok, why-not).

        ⭐ This is a remote-control action: the Switchboard is reachable from a phone through a
        tunnel, so "it is local" is a property of the *socket*, not of the person. Each condition
        closes a different door and none of them is sufficient alone:

        1. **Supervised.** With no supervisor there is nothing to bring the server back, so the
           honest answer to "restart" is that it cannot, not a process that exits into silence.
        2. **Loopback peer.** The listening socket is bound to loopback, and this re-checks the
           actual peer address rather than trusting that.
        3. **Token match.** A per-process random value embedded in our own HTML. This is the CSRF
           control: another site can make the browser POST here, but the same-origin policy stops
           it reading this value to include. Compared with `secrets.compare_digest`, because a
           token compared with `==` leaks its prefix through timing.
        4. **Same-origin.** `Origin`/`Referer`, when present, must name a loopback host. A
           form-encoded POST is not preflighted, so this is the header that distinguishes a click
           on our page from a cross-site form submission.

        ⛔ Note what is NOT here: nothing reads a command, a path, an argument or an environment
        variable from the request. There is no `/restart?command=` because there is no parameter
        at all — the handler's whole effect is a fixed exit code.
        """
        import secrets as _secrets
        if not RESTART_TOKEN:
            return False, ("this server is not supervised, so a restart would exit into nothing. "
                           "Start it with scripts/switchboard_dev.py.")
        peer = (self.client_address[0] if self.client_address else "") or ""
        if peer not in self._LOCAL_HOSTS:
            return False, f"restart is loopback-only; this request came from {peer!r}"
        try:
            n = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            return False, "unreadable Content-Length"
        if n > 4096:
            return False, "restart takes no payload beyond its token"
        raw = self.rfile.read(n).decode("utf-8", "replace")
        got = (urllib.parse.parse_qs(raw, keep_blank_values=True).get("token") or [""])[0]
        if not got or not _secrets.compare_digest(str(got), RESTART_TOKEN):
            return False, "missing or stale restart token — reload the page and try again"
        # ⛔ SAME-ORIGIN means "matches the origin this request was sent TO" -- compared against
        # the request's own Host header, NOT against a loopback allow-list.
        #
        # The first version compared against `_LOCAL_HOSTS` and it broke the one case this whole
        # feature exists for. Reached through the phone tunnel the page's own origin IS the tunnel
        # hostname, so the browser sends `Origin: https://<id>.ngrok-free.app` and the check
        # refused the page's own button:
        #
        #     REFUSED: cross-origin restart refused (Origin: 'abc123.ngrok-free.app')
        #
        # The button rendered, the tap did nothing, and the operator would have walked back to the
        # laptop -- which is precisely the trip the control was built to remove. Measured
        # 2026-09-01; every earlier test hit 127.0.0.1 directly and sent no Origin at all, so the
        # whole security suite passed while the real path was broken.
        #
        # Comparing to Host keeps the CSRF property intact and is in fact the stricter, standard
        # check: a third-party page POSTing here carries ITS origin, which cannot match our Host,
        # whether we are reached on localhost or through a tunnel.
        host_hdr = (self.headers.get("Host") or "").strip()
        want = urllib.parse.urlparse("//" + host_hdr).hostname or host_hdr.split(":")[0]
        for hdr in ("Origin", "Referer"):
            v = self.headers.get(hdr)
            if not v:
                continue                       # form POSTs may omit it; the token still gates
            got = urllib.parse.urlparse(v).hostname or ""
            if got and want and got.lower() == want.lower():
                continue                       # same origin as the page that was served
            if got in self._LOCAL_HOSTS and want in self._LOCAL_HOSTS:
                continue                       # 127.0.0.1 vs localhost are the same server
            return False, (f"cross-origin restart refused ({hdr} host {got!r} does not match the "
                           f"host this request was sent to, {want!r})")
        return True, ""

    def log_message(self, fmt, *args):
        print(f"  re-measured for {self.address_string()}")


def _exit_code_for_supervisor() -> int:
    """`RESTART_EXIT` when the UI asked for a restart, 0 for an ordinary stop.

    The supervisor distinguishes the two by code alone, so a crash can never be mistaken for a
    restart request and re-launched forever.
    """
    return RESTART_EXIT if _RESTART_REQUESTED else 0


def main(argv=None) -> int:
    argv = list(argv if argv is not None else sys.argv[1:])
    serve = "--serve" in argv
    port = 8099
    if "--port" in argv:
        try:
            port = int(argv[argv.index("--port") + 1])
        except (IndexError, ValueError):
            print("--port needs a number", file=sys.stderr)
            return 2

    if not serve:
        page = render(datetime.datetime.now(), "tickets")
        OUT.write_text(page, encoding="utf-8")
        url = OUT.resolve().as_uri()
        print(f"wrote {OUT}  ({len(page):,} bytes)")
        print(f"open  {url}")
        print("\nThis is a snapshot. For a page that re-measures on every refresh:")
        print("  python scripts/local_tracker.py --serve")
        if "--open" in argv:
            webbrowser.open(url)
        return 0

    # THREADED, deliberately. A plain TCPServer serialises every request, so a browser's
    # favicon fetch — or a second person looking at the same page — queues behind a render that
    # takes tens of seconds, and the tab shows nothing but a spinner the whole time. The page is
    # for watching several sessions at once; a server that can only answer one viewer at a time
    # is the wrong shape for that.
    class _Threaded(socketserver.ThreadingTCPServer):
        daemon_threads = True        # ctrl-c must not hang on an in-flight render
        allow_reuse_address = True

    with _Threaded(("127.0.0.1", port), Handler) as httpd:
        url = f"http://127.0.0.1:{port}/"
        print(f"readiness tracker on {url}")
        print("every refresh re-runs all probes against the repos as they are now")
        print("ctrl-c to stop\n")
        if "--open" in argv:
            webbrowser.open(url)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            # Ctrl+C stops the child AND, because the supervisor sees exit 0, stops the
            # supervisor too. A wrapper that survived Ctrl+C would be a process the operator
            # cannot kill from the terminal they started it in.
            print("\nstopped.")
            return 0
    # serve_forever() also returns when the restart handler calls shutdown(). The exit CODE is
    # what tells the supervisor which of the two happened -- a crash must never be replaced with
    # a fresh child, or a broken build becomes an infinite relaunch loop.
    code = _exit_code_for_supervisor()
    if code == RESTART_EXIT:
        print(f"restart requested by the UI -- exiting {code} for the supervisor")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
