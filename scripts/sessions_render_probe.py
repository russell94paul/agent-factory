"""Does the Sessions board actually PAINT, and does every card carry a title and a description?

    python scripts/sessions_render_probe.py [--url http://127.0.0.1:8099/sessions] [--shot out.png]

`curl | grep` proves the bytes are in the response. It does not prove a card rendered, that
its title is visible, or that the "this order means nothing" warning is on screen rather than
clipped behind something. This estate's own rule is that the consumer's layer is the
**rendered surface**, so this drives a real browser and asks the DOM.

⚠ It measures **geometry and computed style**, not appearance. A card painted white-on-white
would pass every assertion here. What it can prove is that each card exists, is non-zero
sized, is inside the viewport, and that its title and description are both non-empty — which
is exactly the failure this surface exists to prevent ("a blank title reads as no work here").

Exit code 0 means every card on the board carries both fields and paints.
"""
from __future__ import annotations

import argparse
import json
import sys

PROBE = r"""
() => {
  const out = {cards: [], banner: null, viewport: window.innerWidth};
  const banner = [...document.querySelectorAll('.card:not([data-card])')]
      .find(c => /No ordering constraints exist/i.test(c.textContent || ''));
  if (banner) {
    const r = banner.getBoundingClientRect();
    out.banner = {w: Math.round(r.width), h: Math.round(r.height),
                  visible: r.width > 0 && r.height > 0};
  }
  // `[data-card]`, NOT `.card`. `.card` is the tracker's generic box and the notices use it
  // too, so selecting on it put two banners into the population and the probe reported them
  // as untitled cards. An instrument has to name its population, not infer it from styling.
  for (const c of document.querySelectorAll('[data-card]')) {
    const r = c.getBoundingClientRect();
    // The title is the first bold line; the description is the block beneath the id line.
    const divs = [...c.querySelectorAll(':scope > div')];
    const title = divs.find(d => (getComputedStyle(d).fontWeight | 0) >= 600);
    const texts = divs.map(d => (d.textContent || '').trim()).filter(Boolean);
    out.cards.push({
      kind: c.getAttribute('data-card'),
      w: Math.round(r.width), h: Math.round(r.height),
      onscreen: r.width > 0 && r.height > 0 && r.right > 0 && r.left < window.innerWidth,
      title: title ? (title.textContent || '').trim() : '',
      blocks: texts.length,
      overflowsRight: Math.round(r.right - document.documentElement.clientWidth),
    });
  }
  out.bodyScrollsX = document.documentElement.scrollWidth >
                     document.documentElement.clientWidth + 1;
  return out;
}
"""


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="http://127.0.0.1:8099/sessions")
    ap.add_argument("--shot", default=None, help="write a PNG here")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("playwright is not installed — UNMEASURABLE, not a pass. pip install playwright")
        return 2

    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1400, "height": 1000})
        resp = pg.goto(a.url, wait_until="networkidle")
        status = resp.status if resp else 0
        data = pg.evaluate(PROBE)
        if a.shot:
            pg.screenshot(path=a.shot, full_page=True)
        b.close()

    if a.json:
        print(json.dumps(data, indent=2))

    fails = []
    if status != 200:
        fails.append(f"HTTP {status}")
    if not data["cards"]:
        fails.append("no [data-card] elements rendered at all — either the page painted "
                     "nothing or the selector no longer matches the markup. Both are "
                     "failures; an instrument that sees nothing has not measured zero.")
    for i, c in enumerate(data["cards"]):
        if not c["onscreen"]:
            fails.append(f"card {i} is not on screen ({c['w']}x{c['h']})")
        if c["h"] < 20:
            fails.append(f"card {i} collapsed to {c['h']}px high")
        # The title is the point of the surface. A card with an empty one is the exact
        # failure `sessions.post` refuses at write time; this checks the read side too.
        if not c["title"]:
            fails.append(f"card {i} rendered with NO visible title")
        if c["blocks"] < 2:
            fails.append(f"card {i} has {c['blocks']} text block(s) — no description visible")
        if c["overflowsRight"] > 0:
            fails.append(f"card {i} overflows the viewport by {c['overflowsRight']}px")
    if data["bodyScrollsX"]:
        fails.append("the page scrolls horizontally")
    if data["banner"] and not data["banner"]["visible"]:
        fails.append("the 'no ordering constraints' warning did not paint")

    print(f"{a.url} — HTTP {status}, {len(data['cards'])} card(s) painted")
    for c in data["cards"]:
        print(f"  [{c['kind']:<7}] {c['w']:>4}x{c['h']:<4} {c['blocks']} block(s)  "
              f"{c['title'][:52]}")
    if data["banner"]:
        print(f"  banner painted: {data['banner']['w']}x{data['banner']['h']}")
    if fails:
        print("\n".join(["", "FAILED:"] + [f"  - {f}" for f in fails]))
        return 1
    print("\nEvery card paints, is on screen, and carries a visible title and description.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
