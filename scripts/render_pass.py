"""Render pass — open the page in a real browser and check what actually painted.

**Why this exists.** `claude-in-chrome` refused to connect for six sessions, so no render pass had
ever been run and five defects shipped into the published figure with a human finding every one.
This drives the *installed* Chrome directly through Playwright — no extension, no claude.ai
account, no pairing. Removing that dependency is the point.

    pip install playwright
    python scripts/render_pass.py                       # local source file
    python scripts/render_pass.py --url https://…       # a deployed surface
    python scripts/render_pass.py --shots out/          # also write PNGs

⚠ **What this does and does not prove.** By default it renders
`docs/artifacts/agent-factory.html` — the *source*. The published artifact is that file wrapped in
the host's doctype/head/body skeleton with its own CSS reset and `data-theme` stamping. Everything
the checklist asks about lives in the page's own CSS and JS and is faithfully exercised here, but a
local render is **not** the deployed surface and evidence written from it must say so. Pass
`--url` for the real thing.

⚠ **This probe has already been wrong twice, in ways worth remembering.**
  1. It measured across BOTH svgs in `#failed` and reported *"119 marks, 1 inside the band, min
     gap -201px"* — geometry from two stacked figures read as one. Now scoped to `svg.lww`.
  2. It called a text collision on `--max-turns` x `--max-budget-usd`. False: the second is an
     inline `<code>` that WRAPS, and `getBoundingClientRect()` returns the union of its line
     boxes, which necessarily swallows whatever precedes it. Now compares `getClientRects()`.

A static check proves the file parses. This proves something painted, and where.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
DEFAULT = REPO / "docs" / "artifacts" / "agent-factory.html"
WIDTHS = (1400, 1000, 700)

# ---------------------------------------------------------------- in-page probes

OVERLAP_JS = r"""
() => {
  const vis = el => {
    const s = getComputedStyle(el);
    if (s.display === 'none' || s.visibility === 'hidden' || parseFloat(s.opacity) < 0.05) return false;
    const r = el.getBoundingClientRect();
    return r.width > 1 && r.height > 1;
  };
  const hasOwnText = el => [...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim());
  const nodes = [...document.querySelectorAll('body *')].filter(e => hasOwnText(e) && vis(e));
  const name = e => e.tagName + (typeof e.className === 'string' && e.className
                                 ? '.' + e.className.split(' ')[0] : '');
  const out = [];
  for (let i = 0; i < nodes.length; i++) {
    for (let j = i + 1; j < nodes.length; j++) {
      const a = nodes[i], b = nodes[j];
      if (a.contains(b) || b.contains(a)) continue;
      // Per-line client rects, NOT the union bounding box. A wrapped inline element's bounding
      // box covers whatever shares its first line, which is a guaranteed false positive.
      let area = 0, smaller = Infinity;
      for (const ra of a.getClientRects()) {
        for (const rb of b.getClientRects()) {
          const iw = Math.min(ra.right, rb.right) - Math.max(ra.left, rb.left);
          const ih = Math.min(ra.bottom, rb.bottom) - Math.max(ra.top, rb.top);
          if (iw <= 1 || ih <= 1) continue;
          if (iw * ih > area) area = iw * ih;
          smaller = Math.min(smaller, ra.width * ra.height, rb.width * rb.height);
        }
      }
      if (area < 6 || !isFinite(smaller) || area / smaller < 0.15) continue;
      out.push({ a: name(a), b: name(b),
                 atext: a.textContent.trim().slice(0, 45), btext: b.textContent.trim().slice(0, 45),
                 overlap: Math.round(area), pct: Math.round(100 * area / smaller) });
    }
  }
  return out.sort((x, y) => y.pct - x.pct).slice(0, 25);
}
"""

MARKS_JS = r"""
() => {
  const s = document.querySelector('#failed svg.lww');
  if (!s) return { error: 'no #failed svg.lww' };
  const box = r => r.getBoundingClientRect();
  const all = [...s.querySelectorAll('rect')].filter(r => !(r.getAttribute('class') || '').includes('sw'));
  const marks = all.filter(r => box(r).width < 10).map(r => {
    const b = box(r);
    return { x: b.left, y: b.top, w: b.width, h: b.height, bottom: b.bottom,
             fill: getComputedStyle(r).fill };
  }).sort((p, q) => p.x - q.x);
  if (!marks.length) return { error: 'no marks in svg.lww' };
  const fills = {};
  marks.forEach(m => { fills[m.fill] = (fills[m.fill] || 0) + 1; });
  const swatches = {};
  [...s.querySelectorAll('rect.sw')].forEach(r => { swatches[r.getAttribute('class')] = getComputedStyle(r).fill; });
  const gaps = [];
  for (let i = 1; i < marks.length; i++) gaps.push(marks[i].x - (marks[i - 1].x + marks[i - 1].w));
  const heights = marks.map(m => m.h);
  const texts = [...s.querySelectorAll('text')].map(t => t.textContent.trim());
  const claimed = texts.find(t => /^[0-9]+$/.test(t));
  return {
    count: marks.length, claimed_in_caption: claimed ? Number(claimed) : null,
    fills, legend_swatches: swatches,
    // A legend colour with no mark is a category the figure DECLARES and never DRAWS.
    swatches_with_no_mark: Object.entries(swatches)
      .filter(([, c]) => !Object.keys(fills).includes(c)).map(([k, c]) => k + '=' + c),
    h_min: Math.min(...heights), h_max: Math.max(...heights),
    row_top: Math.min(...marks.map(m => m.y)), row_bottom: Math.max(...marks.map(m => m.bottom)),
    uniform_row: (Math.max(...heights) - Math.min(...heights)) < 0.6,
    zero_width: marks.filter(m => m.w <= 0.4).length,
    min_gap: Math.min(...gaps), touching: gaps.filter(g => g < 0.4).length,
  };
}
"""

OVERFLOW_JS = r"""
() => {
  const vw = document.documentElement.clientWidth;
  const wide = [...document.querySelectorAll('body *')]
    .filter(e => parseFloat(getComputedStyle(e).minWidth) > vw);
  return {
    viewport: vw,
    doc_scroll_width: document.documentElement.scrollWidth,
    main_width: Math.round((document.querySelector('main') || document.body).getBoundingClientRect().width),
    min_width_offenders: wide.map(e => ({
      tag: e.tagName, minWidth: getComputedStyle(e).minWidth,
      width: Math.round(e.getBoundingClientRect().width),
      parent: e.parentElement.tagName + '.' + (typeof e.parentElement.className === 'string' ? e.parentElement.className : ''),
      parent_overflow_x: getComputedStyle(e.parentElement).overflowX,
      parent_width: Math.round(e.parentElement.getBoundingClientRect().width),
    })).slice(0, 4),
  };
}
"""

TABLE_JS = r"""
() => {
  const sec = document.querySelector('#tracker');
  if (!sec) return { error: 'no #tracker section' };
  const rows = [...sec.querySelectorAll('tbody tr')];
  return { rows: rows.length,
           painted: rows.filter(r => r.getBoundingClientRect().height > 2).length,
           group_headers: [...sec.querySelectorAll('tbody tr th')].length };
}
"""

TOKENS_JS = r"""
() => {
  const cs = getComputedStyle(document.documentElement);
  const out = {};
  ['--fail', '--pass', '--unmeas'].forEach(n => {
    const v = cs.getPropertyValue(n).trim(); if (v) out[n] = v;
  });
  out['body-bg'] = getComputedStyle(document.body).backgroundColor;
  out['body-fg'] = getComputedStyle(document.body).color;
  return out;
}
"""


def scroll_through(page) -> None:
    """Fire every IntersectionObserver, then return to the top. A reveal that never fired leaves
    the marks at their at-rest height, which looks like a layout bug in a screenshot."""
    height = page.evaluate("document.body.scrollHeight")
    y = 0
    while y < height:
        page.mouse.wheel(0, 600)
        page.wait_for_timeout(55)
        y += 600
    page.wait_for_timeout(900)
    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(400)


def run(target: str, shots: pathlib.Path | None) -> dict:
    from playwright.sync_api import sync_playwright

    report: dict = {"target": target, "widths": {}, "themes": {}, "reduced_motion": {}}
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True)
        try:
            for w in WIDTHS:
                pg = browser.new_page(viewport={"width": w, "height": 1100})
                pg.goto(target, wait_until="load")
                scroll_through(pg)
                geom = pg.evaluate("""() => ({
                    docScrollW: document.documentElement.scrollWidth,
                    docClientW: document.documentElement.clientWidth })""")
                report["widths"][w] = {
                    "horizontal_scroll": geom["docScrollW"] > geom["docClientW"] + 1,
                    "geometry": geom,
                    "text_overlaps": pg.evaluate(OVERLAP_JS),
                    "overflow": pg.evaluate(OVERFLOW_JS),
                    "marks": pg.evaluate(MARKS_JS),
                    "table": pg.evaluate(TABLE_JS),
                }
                if shots:
                    shots.mkdir(parents=True, exist_ok=True)
                    pg.locator("#failed").screenshot(path=str(shots / f"failed-{w}.png"))
                    pg.locator("#tracker").screenshot(path=str(shots / f"tracker-{w}.png"))
                pg.close()

            for scheme in ("light", "dark"):
                ctx = browser.new_context(viewport={"width": 1400, "height": 1100},
                                          color_scheme=scheme)
                pg = ctx.new_page()
                pg.goto(target, wait_until="load")
                pg.evaluate(f"document.documentElement.setAttribute('data-theme','{scheme}')")
                scroll_through(pg)
                report["themes"][scheme] = {"tokens": pg.evaluate(TOKENS_JS),
                                            "marks": pg.evaluate(MARKS_JS)}
                if shots:
                    pg.locator("#failed").screenshot(path=str(shots / f"failed-{scheme}.png"))
                pg.close()
                ctx.close()

            ctx = browser.new_context(viewport={"width": 1400, "height": 1100},
                                      reduced_motion="reduce")
            pg = ctx.new_page()
            pg.goto(target, wait_until="load")
            pg.wait_for_timeout(900)          # deliberately unscrolled: the at-rest state
            report["reduced_motion"]["no_scroll"] = pg.evaluate(MARKS_JS)
            if shots:
                pg.locator("#failed").screenshot(path=str(shots / "failed-reduced-motion.png"))
            pg.close()
            ctx.close()
        finally:
            browser.close()
    return report


def verdicts(r: dict) -> list:
    """(verdict, check, detail). UNMEASURABLE where the probe could not look — never a pass."""
    out = []
    w0 = r["widths"][WIDTHS[0]]
    m = w0["marks"]
    if m.get("error"):
        out.append(("UNMEASURABLE", "the marks paint", m["error"]))
    else:
        claimed = m.get("claimed_in_caption")
        ok = m["zero_width"] == 0 and m["uniform_row"] and (claimed is None or m["count"] == claimed)
        out.append((("PASS" if ok else "FAIL"), "every mark the caption claims is painted",
                    f"{m['count']} painted, caption claims {claimed}; fills {m['fills']}; "
                    f"{m['zero_width']} zero-width; uniform row {m['uniform_row']}"))
        orphan = m.get("swatches_with_no_mark") or []
        out.append((("PASS" if not orphan else "FAIL"),
                    "no legend colour without a mark to explain",
                    "every swatch has marks" if not orphan
                    else f"declared but never drawn: {orphan}"))
        out.append((("PASS" if m["touching"] == 0 else "FAIL"),
                    "countable bars, not a solid stripe",
                    f"min gap {m['min_gap']:.2f}px between adjacent marks"))
        out.append((("PASS" if m["h_max"] > 12 else "FAIL"), "the reveal fires",
                    f"tallest mark {m['h_max']:.1f}px"
                    + ("" if m["h_max"] > 12 else " — stuck at the at-rest fraction")))

    for w in WIDTHS:
        d = r["widths"][w]
        ov = d["text_overlaps"]
        out.append((("PASS" if not ov else "FAIL"), f"no text overlaps @ {w}px",
                    "none" if not ov else
                    f"{len(ov)} pair(s), worst {ov[0]['pct']}%: "
                    f"{ov[0]['atext'][:30]!r} x {ov[0]['btext'][:30]!r}"))
        off = d["overflow"]["min_width_offenders"]
        out.append((("PASS" if not d["horizontal_scroll"] else "FAIL"),
                    f"body never scrolls sideways @ {w}px",
                    f"doc scrollWidth {d['geometry']['docScrollW']} vs client "
                    f"{d['geometry']['docClientW']}"
                    + ("" if not (d["horizontal_scroll"] and off) else
                       f"; widened by {off[0]['tag']} min-width {off[0]['minWidth']} in "
                       f"{off[0]['parent']} — that container has overflow-x:"
                       f"{off[0]['parent_overflow_x']} but is itself {off[0]['parent_width']}px, "
                       f"so it is sized by its content instead of containing it")))

    for scheme in ("light", "dark"):
        t = r["themes"][scheme]["tokens"]
        have = [k for k in ("--fail", "--pass", "--unmeas") if k in t]
        out.append((("PASS" if len(have) == 3 else "FAIL"), f"verdict tokens hold — {scheme}",
                    f"{ {k: t[k] for k in have} }, body bg {t.get('body-bg')}"))

    rm = r["reduced_motion"]["no_scroll"]
    if rm.get("error"):
        out.append(("UNMEASURABLE", "reduced motion lands on the end state", rm["error"]))
    else:
        out.append((("PASS" if rm["h_max"] > 12 else "FAIL"),
                    "reduced motion lands on the end state, unscrolled",
                    f"tallest mark {rm['h_max']:.1f}px with no scrolling"))

    tb = w0["table"]
    if tb.get("error"):
        out.append(("UNMEASURABLE", "section 10 readiness table renders", tb["error"]))
    else:
        out.append((("PASS" if tb["painted"] == tb["rows"] and tb["rows"] > 0 else "FAIL"),
                    "section 10 readiness table renders",
                    f"{tb['rows']} rows, {tb['painted']} painted"))
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="render_pass")
    ap.add_argument("--url", default=None, help="render a deployed surface instead of the local file")
    ap.add_argument("--shots", default=None, help="directory for PNGs")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    target = args.url or DEFAULT.as_uri()
    report = run(target, pathlib.Path(args.shots) if args.shots else None)
    if args.json:
        print(json.dumps(report, indent=2, default=str))
        return 0

    print(f"render pass against {target}\n")
    worst = 0
    for verdict, check, detail in verdicts(report):
        print(f"  [{verdict:12}] {check}\n                 {detail}")
        worst = max(worst, {"PASS": 0, "UNMEASURABLE": 1, "FAIL": 2}[verdict])
    print()
    print({0: "every check passed.", 1: "UNMEASURABLE is not a pass.", 2: "FAIL — see above."}[worst])
    return 0 if worst == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
