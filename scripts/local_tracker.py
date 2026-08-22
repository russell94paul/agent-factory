"""A standalone readiness page you can open and refresh without anyone in the loop.

    python scripts/local_tracker.py            # write tracker.html, print the file:// path
    python scripts/local_tracker.py --serve    # serve it; every browser refresh RE-MEASURES
                                               # and the reload button re-reads the CODE;
                                               # sync regenerates the artifact FILE
    python scripts/local_tracker.py --serve --port 8099

The published artifact only changes when someone republishes it. This does not: in --serve mode
each request re-runs every probe against the repositories as they are at that moment, so the
timestamp in the header is the measurement time, not the build time. A tracker that can quietly
show yesterday's state is the drift this whole project exists to remove.

Self-contained: no network, no fonts, no dependencies. Written to tracker.html, which is
gitignored — the page is a view, the probes in factory/readiness.py are the source of truth.
"""
from __future__ import annotations

import datetime
import html
import http.server
import pathlib
import re
import socketserver
import sys
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

OUT = FACTORY / "tracker.html"

#: (key, href, label). The key is what render() switches on.
TABS = [("gates", "/", "Gates"), ("lanes", "/lanes", "Lanes"),
        ("research", "/research", "Research"), ("handoff", "/handoff", "Handoff")]

#: Modules whose source can change while the server is running, newest-dependency-last: board and
#: lanes both import from readiness, so readiness must be reloaded before them or they keep
#: references to the old Gate objects.
_HOT = ("factory.readiness", "factory.board", "factory.lanes", "factory.schedule")

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
    inner = (f"Set-Location -LiteralPath '{cwd}'; "
             f"Write-Host '{note} - {lane.id}' -ForegroundColor Cyan; "
             f"claude --model {lane.model} (Get-Content -Raw -LiteralPath '{f}')")
    return (["cmd", "/c", "start", f"lane {lane.id}", "powershell", "-NoExit",
             "-ExecutionPolicy", "Bypass", "-Command", inner], f, cwd)


def launch(lane_id: str, dry: bool = False):
    """Claim, then spawn. Returns (ok, message). The claim runs FIRST so a conflicting lane is
    refused before anything is started."""
    import subprocess
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
        g["synth"] = _il.reload(_il.import_module("factory.synthesis"))
        g["claimlib"] = _il.reload(_il.import_module("factory.claims"))
        g["opans"] = _il.reload(_il.import_module("factory.operator"))
        g["wt"] = _il.reload(_il.import_module("factory.worktrees"))
        g["ho"] = _il.reload(_il.import_module("factory.handoff"))
        _RELOADED_AT = datetime.datetime.now()
        return True, f"reloaded {len(_HOT)} modules, {len(r.GATES)} gates"
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


def render(when: datetime.datetime, tab: str = "gates") -> str:
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
          f'font-family:ui-monospace,monospace">&#9654; start all {len(ready_now)} eligible</a>')
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

    if tab == "research":
        # ---------------------------------------------------------------- research prompts
        rdir = FACTORY / "docs" / "research"
        adir = rdir / "answers"
        pending = []
        if rdir.is_dir():
            for f in sorted(rdir.glob("R[0-9]*.md")):
                # R[0-9]* not R* — the plain glob matched README.md and offered it as a research
                # prompt. A directory scan is only as good as its pattern.
                stem = f.name.split("-")[0]
                answered = adir.is_dir() and any(a.name.startswith(f"{stem}-answer") or
                                                 a.name.startswith(f"{stem}-followup-answer")
                                                 for a in adir.glob("*.md"))
                if not answered:
                    pending.append(f)
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
            w('<h1>Research</h1>')
            w(f'<div class="sub">Nothing outstanding &mdash; every written prompt has a filed '
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
                w('<div class="par" style="margin-top:16px">')
                w(f'<h3>{e(first)}</h3>')
                w(f'<p style="font-size:12.5px;color:var(--ink3);margin:0 0 8px">'
                  f'<code>docs/research/{e(f.name)}</code> &middot; {len(body):,} chars</p>')
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
                w('<div class="par" style="margin-top:12px">')
                w(f'<h3 style="margin-top:0">{e(first)}</h3>')
                w(f'<p style="font-size:12.5px;color:var(--ink3);margin:0">'
                  f'<code>docs/research/answers/{e(a.name)}</code> &middot; '
                  f'{a.stat().st_size:,} bytes</p>')
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
          'color:var(--ink);font-family:ui-monospace,monospace">regenerate with this note</button>')
        w('</form>')
        text = ho.session_handoff(_HANDOFF_NOTE)
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
        global _ANSWER_MSG, _CLAIM_MSG
        import urllib.parse
        if self.path.rstrip("/") == "/handoff":
            global _HANDOFF_NOTE
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
            done, skipped = [], []
            for lid in claimlib.parallel_set():
                lane = next((l for l in LANES if l.id == lid), None)
                # A lane whose declared blocker is unanswered would launch and immediately ask.
                # Skipping it here is the whole point of pre-answering.
                if lane is not None and lane.needs_paul and not opans.get(lid):
                    skipped.append(f"{lid} (blocker unanswered)")
                    continue
                ok, msg = launch(lid)
                (done if ok else skipped).append(lid if ok else f"{lid} ({msg})")
            _CLAIM_MSG = (bool(done), "started " + (", ".join(done) or "nothing")
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
        route = {"/": "gates", "/index.html": "gates",
                 "/lanes": "lanes", "/research": "research",
                 "/handoff": "handoff"}.get(self.path.rstrip("/") or "/")
        if route is None:
            self.send_error(404)
            return
        # Re-measure per request. Slower than serving a file, and the entire reason to serve.
        body = render(datetime.datetime.now(), route).encode("utf-8")
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

    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("127.0.0.1", port), Handler) as httpd:
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
