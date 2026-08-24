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
TABS = [("gates", "/", "Gates"), ("goals", "/goals", "Goals"),
        ("roadmap", "/roadmap", "Roadmap"),
        ("flow", "/flow", "Flow"), ("lanes", "/lanes", "Lanes"),
        ("sessions", "/sessions", "Sessions"),
        ("research", "/research", "Research"), ("handoff", "/handoff", "Handoff")]

#: Modules whose source can change while the server is running, newest-dependency-last: board and
#: lanes both import from readiness, so readiness must be reloaded before them or they keep
#: references to the old Gate objects.
_HOT = ("factory.readiness", "factory.board", "factory.lanes", "factory.schedule", "factory.goals", "factory.roadmap")

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


def start_research_pass(rid: str, dry: bool = False):
    """Prepare a research pass and open a session that runs it here.

    ⛔ An earlier version of this split passes into "launchable" and "you go and paste it". That was
    wrong -- the deep-research skill replaces the paste loop and states that the default is a pass
    runs here. Every pass launches now, and the run log records that it ran LOCALLY, because that
    is what tells the next reader how much independence the answer had.

    Preparation happens BEFORE the spawn, so a failed spawn still leaves the prompt on disk and the
    dispatch recorded, rather than losing both with the click.
    """
    import subprocess as _sp
    try:
        res = rrun.start(rid)
    except rrun.ResearchError as exc:
        return False, f"{rid}: {exc}"
    except Exception as exc:                                       # noqa: BLE001
        return False, f"{rid}: {type(exc).__name__}: {exc}"

    # The session is told to invoke the skill; it is NOT handed a paraphrase of the brief.
    d = FACTORY / ".data" / "research-prompts"
    launch_file = d / f"{rid.upper()}-session.txt"
    launch_file.write_text(res["session_prompt"], encoding="utf-8")

    if dry:
        return True, f"DRY RUN -- {res['note']}; would open a session running {launch_file.name}"

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
        mods = {}
        for name in _HOT:
            m = importlib.import_module(name)
            mods[name] = importlib.reload(m)
        g = globals()
        r, b = mods["factory.readiness"], mods["factory.board"]
        for n in ("CONNECTORS", "FACTORY", "FAIL", "NOT_RUN", "PASS", "PHASES",
                  "UNMEASURABLE", "measure"):
            g[n] = getattr(r, n)
        for n in ("BLOCKED", "DONE", "READY", "board", "critical_path"):
            g[n] = getattr(b, n)
        for n in ("LANES", "SIZE", "conflicts", "recommend", "waits_on"):
            g[n] = getattr(mods["factory.lanes"], n)
        import importlib as _il
        g["by_lane"] = getattr(_il.reload(_il.import_module("factory.findings")), "by_lane")
        # global name(s) -> module, in DEPENDENCY ORDER: a module must come after everything it
        # imports from, or the importers keep references to the old objects. Same rule as _HOT.
        #
        # ⛔ `factory.dispatch` was MISSING from this block entirely, under BOTH of its aliases,
        # so "reload code & re-measure" kept serving the dispatch code the process started with —
        # and reported success. A reload that silently excludes a module is worse than no reload
        # button: it is a claim of freshness. Found 2026-08-23 when a dependency-graph fix did not
        # appear on the page. A list beats nine hand-written lines precisely because a missing
        # entry is now visible as a gap in one place rather than an absence nobody can see.
        _EXTRA = (
            (("synth",), "factory.synthesis"),
            (("disp", "dispatchlib"), "factory.dispatch"),   # after synthesis, before research_run
            (("claimlib",), "factory.claims"),
            (("opans",), "factory.operator"),
            (("wt",), "factory.worktrees"),
            (("ho",), "factory.handoff"),
            (("launchlib",), "factory.launch"),
            (("rrun",), "factory.research_run"),
            (("tplan",), "factory.teamplan"),
        )
        for names, modname in _EXTRA:
            m = _il.reload(_il.import_module(modname))
            for nm in names:
                g[nm] = m
        _RELOADED_AT = datetime.datetime.now()
        # ⚠ Counted, not assumed. This said `len(_HOT)` — 6 — while the block actually reloads 16,
        # so the one number an operator had for "did my edit land" understated by 10, and would
        # not have moved even while `factory.dispatch` was being skipped entirely.
        return True, (f"reloaded {len(_HOT) + len(_EXTRA) + 1} modules, {len(r.GATES)} gates")
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


def render(when: datetime.datetime, tab: str = "gates", team: str = "") -> str:
    # Research needs no measurement, and a full measure is ~10s of probes. Paying that to read a
    # prompt was the main reason this page felt slow.
    results = measure() if tab != "research" else []
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
         '<title>Readiness</title>', f"<style>{CSS}</style></head><body><div class='wrap'>"]
    w = o.append
    w(f'<nav style="padding:22px 0 4px">{nav}</nav>')
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

    if tab == "gates":
        w('<div class="head">')
        w('<h1>Can a team run a migration unattended?</h1>')
        w(f'<div class="sub">measured {e(when.strftime("%Y-%m-%d %H:%M:%S"))} local &middot; '
          f'refresh this page to re-measure</div>')
        # Refresh re-measures; reload re-reads the CODE. They are different things and the page says
        # so, because conflating them is exactly how this page sat on a 23-gate list for hours.
        reloaded = (f' &middot; code reloaded {_RELOADED_AT.strftime("%H:%M:%S")}'
                    if _RELOADED_AT else ' &middot; code as at server start')
        w(f'<div class="sub" style="margin-top:10px">'
          f'<a href="/reload" style="display:inline-block;padding:6px 12px;border:1px solid '
          f'var(--rule);border-radius:3px;background:var(--raise);color:var(--ink);'
          f'text-decoration:none;font-size:13px">&#8635; reload code &amp; re-measure</a>'
          f'<a href="/sync" style="display:inline-block;margin-left:8px;padding:6px 12px;'
          f'border:1px solid var(--rule);border-radius:3px;background:var(--raise);'
          f'color:var(--ink);text-decoration:none;font-size:13px">&#8681; sync artifact file</a>'
          f'<span style="color:var(--ink3);font-size:12.5px">&nbsp; refresh re-measures'
          f'{reloaded}</span></div>')
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

        # Contended repos, above everything except a blocked session. A repo with uncommitted work
        # and several sessions alive is the shape that produced fc71b6a — one session ran `git add`
        # across a directory another was mid-edit in, swept up a half-finished file, and shipped a
        # HEAD that did not import.
        #
        # ⛔ This panel names a CONDITION, never a culprit. Nothing records which session touched
        # which file, so `attribution` is NOT-MEASURABLE and the wording must stay that way — a row
        # that guessed would be believed.
        if contended:
            w('<div class="par" style="margin-top:14px;border-color:var(--unmeas)">')
            w(f'<h3 style="margin-top:0;color:var(--unmeas)">&#9888; {len(contended)} repo(s) hold '
              f'uncommitted work while more than one session is alive</h3>')
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
        w('<div class="par" style="margin-top:34px;border-color:'
          + ("var(--unmeas)" if gap else "var(--rule)") + '">')
        w('<h3 style="margin-top:0">Decision record</h3>')
        if gap:
            w(f'<p style="font-size:13.5px;color:var(--ink2);margin:0 0 8px">'
              f'<b>SYNTHESIS.md does not mention {e(", ".join(gap))}</b>, which have filed '
              f'answers. The record has fallen behind the research it reconciles.</p>')
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
        # Deliberately not "up to date": the check asserts MENTION, not engagement. There is no
        # synthesize button because synthesis is judgement, and a button that cannot exercise it
        # would either fake it or do nothing.
        w('<p style="font-size:12px;color:var(--ink3);margin:8px 0 0">Checks that each answer is '
          '<i>mentioned</i>, not that it was engaged with &mdash; it catches a record nobody '
          'touched, and nothing subtler. There is no synthesize button: synthesis is judgement.'
          '</p>')
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
        global _ANSWER_MSG, _CLAIM_MSG, _HANDOFF_NOTE
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
        um = re.match(r"^/unanswer/([a-z0-9-]+)$", self.path.rstrip("/"))
        if um:
            ok = opans.clear(um.group(1))
            _CLAIM_MSG = (True, f"cleared the answer for {um.group(1)}" if ok else "nothing to clear")
            self.send_response(303); self.send_header("Location", "/lanes"); self.end_headers()
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
        route = {"/": "gates", "/index.html": "gates", "/flow": "flow",
                 "/goals": "goals", "/roadmap": "roadmap",
                 "/lanes": "lanes", "/sessions": "sessions", "/research": "research",
                 "/handoff": "handoff"}.get(parsed.path.rstrip("/") or "/")
        if route is None:
            self.send_error(404)
            return
        sel = (urllib.parse.parse_qs(parsed.query or "").get("team") or [""])[0]
        # Re-measure per request. Slower than serving a file, and the entire reason to serve.
        body = render(datetime.datetime.now(), route, team=sel).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        print(f"  re-measured for {self.address_string()}")


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
        page = render(datetime.datetime.now(), "gates")
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
            print("\nstopped.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
