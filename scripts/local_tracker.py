"""A standalone readiness page you can open and refresh without anyone in the loop.

    python scripts/local_tracker.py            # write tracker.html, print the file:// path
    python scripts/local_tracker.py --serve    # serve it; every browser refresh RE-MEASURES
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

OUT = FACTORY / "tracker.html"

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

    w('<footer>')
    w('<p><b>UNMEASURABLE is not a pass.</b> A gate with no instrument says so rather than '
      'waving through; that distinction is the point of the whole harness.</p>')
    w('<p>Every row is measured from a file at the moment shown above and names the path it came '
      'from. Nothing here is hand-maintained, so a wrong row means a wrong repo, not a stale '
      'page. Probes live in <code>factory/readiness.py</code>.</p>')
    w('<p>Regenerate: <code>python scripts/local_tracker.py</code> &middot; '
      'serve and re-measure on refresh: <code>python scripts/local_tracker.py --serve</code> '
      '&middot; check the published artifact still matches: '
      '<code>python scripts/build_tracker.py --check</code></p>')
    w('</footer></div></body></html>')
    return "\n".join(o)


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
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
