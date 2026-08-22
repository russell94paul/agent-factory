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
import socketserver
import sys
import webbrowser

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from factory.readiness import (  # noqa: E402
    CONNECTORS, FACTORY, FAIL, NOT_RUN, PASS, PHASES, UNMEASURABLE, measure)
from factory.board import (  # noqa: E402
    BLOCKED, DONE, READY, board, critical_path)

OUT = FACTORY / "tracker.html"

#: Modules whose source can change while the server is running, newest-dependency-last: board and
#: lanes both import from readiness, so readiness must be reloaded before them or they keep
#: references to the old Gate objects.
_HOT = ("factory.readiness", "factory.board", "factory.lanes", "factory.schedule")

_RELOADED_AT = None
_RELOAD_MSG = None
_SYNC_MSG = None

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


def render(when: datetime.datetime) -> str:
    results = measure()
    n = sum(1 for _, r in results if r.ok)
    total = len(results)
    pct = round(100 * n / total) if total else 0

    o = ['<!doctype html><html lang="en"><head><meta charset="utf-8">',
         '<meta name="viewport" content="width=device-width,initial-scale=1">',
         '<title>Readiness</title>', f"<style>{CSS}</style></head><body><div class='wrap'>"]
    w = o.append

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
    if _SYNC_MSG:
        okc = 'var(--pass)' if _SYNC_MSG[0] else 'var(--fail)'
        w(f'<div class="sub" style="color:{okc};font-size:13px">{e(_SYNC_MSG[1])}</div>')
    if _RELOAD_MSG:
        okc = 'var(--pass)' if _RELOAD_MSG[0] else 'var(--fail)'
        w(f'<div class="sub" style="color:{okc};font-size:13px">{e(_RELOAD_MSG[1])}</div>')
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
    w('</footer></div></body></html>')
    return "\n".join(o)


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        global _RELOAD_MSG
        global _SYNC_MSG
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
        if self.path not in ("/", "/index.html"):
            self.send_error(404)
            return
        # Re-measure per request. Slower than serving a file, and the entire reason to serve.
        body = render(datetime.datetime.now()).encode("utf-8")
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
        page = render(datetime.datetime.now())
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
