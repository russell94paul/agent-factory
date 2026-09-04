"""Render check for the Field Manual — open it in a real browser and drive it.

Same route as scripts/render_pass.py and scripts/atlas_render_check.py: the
installed Chrome through Playwright.

    python scripts/manual_render_check.py --shots docs/evidence/manual-2026-09-01/

Beyond painting, this exercises the one thing a static check cannot see: the
Net is a state machine, and a state machine that renders is not the same as a
state machine that advances.
"""
from __future__ import annotations

import argparse
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
PAGE = REPO / "docs" / "artifacts" / "agent-factory-field-manual.html"
WIDTHS = (1500, 1100, 760)
MODES = ("doctrine", "ladder", "net", "mesh", "surfaces", "venture", "revenue")

PROBE = r"""() => {
  const out = {};
  out.h_scroll = document.documentElement.scrollWidth > window.innerWidth + 1;
  out.doc_w = document.documentElement.scrollWidth;
  out.win_w = window.innerWidth;
  out.mode = (document.querySelector('.mode[aria-selected="true"]') || {}).textContent || '?';

  const on = document.querySelector('.view.on');
  out.visible_chars = on ? on.innerText.trim().length : 0;

  const figs = Array.from(document.querySelectorAll('svg.fig')).filter(f => f.getClientRects().length);
  out.figures_visible = figs.length;
  out.figs_no_viewbox = figs.filter(f => !f.getAttribute('viewBox')).length;
  out.figs_no_label = figs.filter(f => !f.getAttribute('aria-label')).length;

  let clipped = 0; out.clip_detail = [];
  figs.forEach(f => {
    const vb = (f.getAttribute('viewBox') || '0 0 0 0').split(/\s+/).map(Number);
    f.querySelectorAll('text,tspan').forEach(t => {
      try {
        const b = t.getBBox();
        if (b.width === 0) return;
        if (b.x + b.width > vb[2] + 1 || b.y + b.height > vb[3] + 1 || b.x < vb[0] - 1) {
          clipped++;
          out.clip_detail.push('"' + (t.textContent || '').slice(0, 30) + '" x=' + b.x.toFixed(0) +
            ' r=' + (b.x + b.width).toFixed(0) + ' vbW=' + vb[2]);
        }
      } catch (e) {}
    });
  });
  out.clipped_text = clipped;

  // page-level overflow only; clipped/scrolling ancestors contain by design
  const clipped_by = e => {
    for (let p = e.parentElement; p && p !== document.body; p = p.parentElement) {
      const ox = getComputedStyle(p).overflowX;
      if (ox === 'hidden' || ox === 'auto' || ox === 'scroll') return true;
    }
    return false;
  };
  const overflow = [];
  document.querySelectorAll('body *').forEach(e => {
    const r = e.getBoundingClientRect();
    if (r.width > window.innerWidth + 2 && r.width > 0 && !clipped_by(e)) {
      const cn = (e.className && typeof e.className === 'object' && 'baseVal' in e.className)
        ? e.className.baseVal : (e.className || '');
      overflow.push(e.tagName + '.' + String(cn).slice(0, 26));
    }
  });
  out.overflowing = overflow.slice(0, 5);

  // the Net's own state, when it is on screen
  const spec = document.querySelector('#spec-body');
  if (spec && spec.getClientRects().length) {
    out.net_fields_set = document.querySelectorAll('#spec-body .fld.set').length;
    out.net_gates_ok = document.querySelectorAll('#gatebox .gate.ok').length;
    out.net_msgs = document.querySelectorAll('#net-feed .msg').length;
    out.net_opts = document.querySelectorAll('#net-opts .opt').length;
  }
  return out;
}"""


def check(label, r):
    bad = []
    if r["visible_chars"] < 300:
        bad.append(f"only {r['visible_chars']} chars visible")
    if r["h_scroll"]:
        bad.append(f"page scrolls sideways ({r['doc_w']} > {r['win_w']})")
    if r["figs_no_viewbox"]:
        bad.append(f"{r['figs_no_viewbox']} figures without viewBox")
    if r["figs_no_label"]:
        bad.append(f"{r['figs_no_label']} figures without aria-label")
    if r["clipped_text"]:
        bad.append(f"{r['clipped_text']} clipped text: " + " | ".join(r["clip_detail"][:3]))
    if r["overflowing"]:
        bad.append("overflow: " + ", ".join(r["overflowing"]))
    if r.get("console"):
        bad.append("console: " + " | ".join(r["console"]))
    print(f"{'OK  ' if not bad else 'FAIL'} {label:<20} chars={r['visible_chars']:<5} "
          f"figs={r['figures_visible']:<2} " + ("; ".join(bad) if bad else ""))
    return not bad


def main() -> int:
    ap = argparse.ArgumentParser(prog="manual_render_check")
    ap.add_argument("--shots", default=None)
    a = ap.parse_args()
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("UNMEASURABLE — playwright is not installed. This is not a pass.")
        return 2
    shots = pathlib.Path(a.shots) if a.shots else None
    if shots:
        shots.mkdir(parents=True, exist_ok=True)

    ok = True
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True)

        # reduced motion + no JS
        for label, kw in (("reduced-motion", {"reduced_motion": "reduce"}),
                          ("no-js", {"java_script_enabled": False})):
            ctx = browser.new_context(viewport={"width": 1400, "height": 900},
                                      color_scheme="dark", **kw)
            pg = ctx.new_page()
            pg.goto(PAGE.as_uri())
            pg.wait_for_timeout(1200)
            n = pg.evaluate("() => ({chars: document.body.innerText.trim().length, "
                            "hidden: [...document.querySelectorAll('.rv')]"
                            ".filter(e => parseFloat(getComputedStyle(e).opacity) < .9).length})")
            good = n["chars"] > 500 and not n["hidden"]
            print(f"{'OK  ' if good else 'FAIL'} {label:<20} chars={n['chars']:<5} hidden_reveals={n['hidden']}")
            ok = ok and good
            if shots:
                pg.screenshot(path=str(shots / f"manual-{label}.png"))
            ctx.close()

        for theme in ("dark", "light"):
            for w in WIDTHS:
                ctx = browser.new_context(viewport={"width": w, "height": 940}, color_scheme=theme)
                pg = ctx.new_page()
                errs: list[str] = []
                pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
                pg.on("pageerror", lambda e: errs.append(str(e)))
                pg.goto(PAGE.as_uri())
                pg.wait_for_timeout(1100)
                r = pg.evaluate(PROBE); r["console"] = errs[:3]
                ok = check(f"{theme}-{w}", r) and ok
                if shots and w == WIDTHS[0]:
                    pg.screenshot(path=str(shots / f"manual-{theme}-doctrine.png"))

                # every mode, once, at the widest dark render
                if theme == "dark" and w == WIDTHS[0]:
                    for m in MODES:
                        pg.click(f'.mode[data-m="{m}"]')
                        pg.wait_for_timeout(450)
                        if m == "net":
                            # drive the state machine: 3 chip answers, one NOT_RECORDED
                            for _ in range(2):
                                pg.click("#net-opts .opt:first-child"); pg.wait_for_timeout(220)
                            nr = pg.query_selector("#net-opts .opt.nr")
                            if nr:
                                nr.click(); pg.wait_for_timeout(220)
                        if m == "venture":
                            pg.click('.topic[data-k="sheet"]'); pg.wait_for_timeout(320)
                        sub = pg.evaluate(PROBE); sub["console"] = errs[:3]
                        ok = check(f"mode-{m}", sub) and ok
                        if m == "net":
                            print(f"     net state: fields_set={sub.get('net_fields_set')} "
                                  f"gates_ok={sub.get('net_gates_ok')} msgs={sub.get('net_msgs')}")
                            if not sub.get("net_fields_set"):
                                print("     FAIL: the Net rendered but never advanced")
                                ok = False
                        if shots:
                            pg.screenshot(path=str(shots / f"manual-mode-{m}.png"))
                ctx.close()
        browser.close()

    print()
    print("RENDERED_CONFIRMED" if ok else "RENDER DEFECTS FOUND")
    if shots:
        print(f"shots → {shots}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
