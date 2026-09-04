"""Render check for the Atlas — open it in a real browser and report what painted.

Same route as scripts/render_pass.py: drive the installed Chrome through
Playwright. A static check proves the file parses; this proves something
painted, and where.

    python scripts/atlas_render_check.py --shots docs/evidence/atlas-2026-09-01/
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
PAGE = REPO / "docs" / "artifacts" / "agent-factory-atlas.html"
WIDTHS = (1500, 1100, 760)

PROBE = r"""() => {
  const out = {};
  const box = document.body.getBoundingClientRect();
  out.h_scroll = document.documentElement.scrollWidth > window.innerWidth + 1;
  out.doc_w = document.documentElement.scrollWidth;
  out.win_w = window.innerWidth;

  // graph painted?
  // only measure the graph when its view is actually on screen: a hidden
  // view reports zero-size rects for everything, which is not a defect.
  const journeyOn = document.querySelector('#v-journey').classList.contains('on');
  out.journey_on = journeyOn;
  const nodes = journeyOn ? document.querySelectorAll('#graph .gnode') : [];
  const edges = journeyOn ? document.querySelectorAll('#graph .edge') : [];
  out.nodes = nodes.length;
  out.edges = edges.length;
  const vp = document.querySelector('#vp');
  out.vp_transform = vp ? vp.getAttribute('transform') : null;
  // are any node rects actually inside the viewport box after transform?
  let painted = 0, zero = 0;
  nodes.forEach(n => {
    const r = n.getBoundingClientRect();
    if (r.width < 1 || r.height < 1) zero++;
    if (r.width > 1 && r.bottom > 0 && r.top < window.innerHeight * 3) painted++;
  });
  out.nodes_painted = painted;
  out.nodes_zero_size = zero;

  // verdict bar geometry must sum to 100%
  const segs = Array.from(document.querySelectorAll('#vtrack i'));
  out.verdict_segments = segs.length;
  out.verdict_sum = +segs.reduce((a, s) => a + parseFloat(s.style.width), 0).toFixed(2);

  // every figure has a viewBox and an aria-label
  const figs = Array.from(document.querySelectorAll('svg.fig'));
  out.figures = figs.length;
  out.figs_no_viewbox = figs.filter(f => !f.getAttribute('viewBox')).length;
  out.figs_no_label = figs.filter(f => !f.getAttribute('aria-label')).length;

  // text that overflows its own svg viewBox (the clipping defect class)
  let clipped = 0; out.clip_detail = [];
  figs.forEach(f => {
    if (!f.getClientRects().length) return;   // hidden view: getBBox is meaningless
    const vb = (f.getAttribute('viewBox') || '0 0 0 0').split(/\s+/).map(Number);
    f.querySelectorAll('text').forEach(t => {
      try {
        const b = t.getBBox();
        if (b.x + b.width > vb[2] + 1 || b.y + b.height > vb[3] + 1 || b.x < vb[0] - 1) {
          clipped++;
          out.clip_detail.push((f.getAttribute('aria-label')||'?').slice(0,34) + ' :: "' +
            (t.textContent||'').slice(0,28) + '" x=' + b.x.toFixed(0) + ' w=' + b.width.toFixed(0) +
            ' vbW=' + vb[2]);
        }
      } catch (e) {}
    });
  });
  out.clipped_text = clipped;

  // body must have a real (non-transparent) background
  out.body_bg = getComputedStyle(document.body).backgroundColor;

  // no element wider than the viewport
  // Only page-level overflow counts. Content inside a clipping or scrolling
  // ancestor is contained by design — the graph is deliberately wider than the
  // viewport and is panned inside overflow:hidden. Flagging it was an
  // instrument error, not a page defect.
  let overflow = [];
  const clipped_by = e => {
    for (let p = e.parentElement; p && p !== document.body; p = p.parentElement) {
      const ox = getComputedStyle(p).overflowX;
      if (ox === 'hidden' || ox === 'auto' || ox === 'scroll') return true;
    }
    return false;
  };
  document.querySelectorAll('body *').forEach(e => {
    const r = e.getBoundingClientRect();
    if (r.width > window.innerWidth + 2 && r.width > 0 && !clipped_by(e)) {
      const cn = (e.className && typeof e.className === 'object' && 'baseVal' in e.className)
        ? e.className.baseVal : (e.className || '');
      overflow.push(e.tagName + '.' + String(cn).slice(0, 30));
    }
  });
  out.overflowing = overflow.slice(0, 6);
  return out;
}"""


def main() -> int:
    ap = argparse.ArgumentParser(prog="atlas_render_check")
    ap.add_argument("--shots", default=None, help="directory for PNGs")
    a = ap.parse_args()
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("UNMEASURABLE — playwright is not installed. This is not a pass.")
        return 2

    shots = pathlib.Path(a.shots) if a.shots else None
    if shots:
        shots.mkdir(parents=True, exist_ok=True)

    report = {"page": str(PAGE), "widths": {}}
    ok = True
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True)
        # reduced motion must land on the END state, and JS-off must still say something
        for label, kw in (("reduced-motion", {"reduced_motion": "reduce"}),
                          ("no-js", {"java_script_enabled": False})):
            ctx = browser.new_context(viewport={"width": 1400, "height": 900},
                                      color_scheme="dark", **kw)
            pg = ctx.new_page()
            pg.goto(PAGE.as_uri()); pg.wait_for_timeout(1200)
            txt = pg.evaluate("() => document.body.innerText")
            vis = pg.evaluate("""() => {
              let hidden = 0;
              document.querySelectorAll('.rv').forEach(e => {
                if (parseFloat(getComputedStyle(e).opacity) < .9) hidden++;
              });
              return {hidden_rv: hidden, chars: document.body.innerText.trim().length};
            }""")
            print(f"{'OK  ' if vis['chars'] > 400 and not vis['hidden_rv'] else 'FAIL'} "
                  f"{label:<14} text_chars={vis['chars']:<5} hidden_reveal_elements={vis['hidden_rv']}")
            for want in ("PASS", "UNMEASURABLE", "NOT_RUN"):
                if want not in txt:
                    print(f"     FAIL: verdict word {want!r} absent from {label} text")
            if shots:
                pg.screenshot(path=str(shots / f"atlas-{label}.png"))
            ctx.close()

        for theme in ("dark", "light"):
            for w in WIDTHS:
                ctx = browser.new_context(viewport={"width": w, "height": 900},
                                          color_scheme=theme, device_scale_factor=1)
                pg = ctx.new_page()
                errs: list[str] = []
                pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
                pg.on("pageerror", lambda e: errs.append(str(e)))
                pg.goto(PAGE.as_uri())
                pg.wait_for_timeout(1400)
                r = pg.evaluate(PROBE)
                r["console_errors"] = errs[:5]
                report["widths"][f"{theme}-{w}"] = r
                if shots:
                    pg.screenshot(path=str(shots / f"atlas-{theme}-{w}.png"), full_page=False)
                # exercise the other modes once, at the widest dark render
                if theme == "dark" and w == WIDTHS[0]:
                    for m in ("value", "zeus", "sim", "frontier"):
                        pg.click(f'.mode[data-m="{m}"]')
                        pg.wait_for_timeout(500)
                        if m == "sim":
                            pg.click("#s-step"); pg.wait_for_timeout(250)
                            pg.click("#s-step"); pg.wait_for_timeout(250)
                        sub = pg.evaluate(PROBE)
                        sub["console_errors"] = errs[:5]
                        report["widths"][f"mode-{m}"] = sub
                        if shots:
                            pg.screenshot(path=str(shots / f"atlas-mode-{m}.png"), full_page=False)
                ctx.close()
        browser.close()

    for k, r in report["widths"].items():
        bad = []
        if r["nodes"] == 0 and r.get("journey_on"):
            bad.append("no graph nodes")
        if r.get("nodes_zero_size"):
            bad.append(f"{r['nodes_zero_size']} zero-size nodes")
        if r["h_scroll"]:
            bad.append(f"page scrolls sideways ({r['doc_w']} > {r['win_w']})")
        if r["figs_no_viewbox"]:
            bad.append(f"{r['figs_no_viewbox']} figures without viewBox")
        if r["figs_no_label"]:
            bad.append(f"{r['figs_no_label']} figures without aria-label")
        if r["clipped_text"]:
            bad.append(f"{r['clipped_text']} clipped <text>: " + " | ".join(r.get("clip_detail", [])[:4]))
        if r["overflowing"]:
            bad.append("overflow: " + ", ".join(r["overflowing"]))
        if r["console_errors"]:
            bad.append("console: " + " | ".join(r["console_errors"]))
        if r.get("verdict_sum") and abs(r["verdict_sum"] - 100) > 0.1:
            bad.append(f"verdict bar sums to {r['verdict_sum']}, not 100")
        status = "OK  " if not bad else "FAIL"
        if bad:
            ok = False
        print(f"{status} {k:<14} nodes={r['nodes']:<3} painted={r['nodes_painted']:<3} "
              f"edges={r['edges']:<3} figs={r['figures']:<2} " + ("; ".join(bad) if bad else ""))

    print()
    print("RENDERED_CONFIRMED" if ok else "RENDER DEFECTS FOUND")
    if shots:
        print(f"shots → {shots}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
