"""Render check for the CELL//OS Command Deck — open it in real Chrome and drive it.

Same route as scripts/render_check_previz.py and scripts/manual_render_check.py.

    python scripts/render_check_deck.py --shots docs/evidence/cell-os-deck-2026-09-02/

Beyond painting, this exercises what a static read cannot see:

  1. Seven tabs that actually switch, with exactly one panel visible at a time.
  2. Seven architecture layers that open on click and reveal their services.
  3. The prototype is a live builder — adding an operative must redraw the mesh
     with more nodes and more links, and re-scoring must change the score.
  4. No-JS: every tab panel's content is still present and readable, because the
     tab shell hides panels with the `hidden` attribute that JS manages.
  5. Reduced motion: nothing parked at opacity 0, logo animation stopped.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
PAGE = REPO / "docs" / "marketing" / "cell-os-launch-v1" / "cell-os-deck.html"
WIDTHS = (1400, 1100, 760)
TABS = ["t-over", "t-arch", "t-first", "t-proto", "t-cases", "t-guide", "t-film"]

PROBE = r"""() => {
  const out = {};
  out.h_scroll = document.documentElement.scrollWidth > window.innerWidth + 1;
  out.doc_w = document.documentElement.scrollWidth;
  out.win_w = window.innerWidth;
  out.tabs = document.querySelectorAll('.tab').length;
  out.panels = document.querySelectorAll('[role=tabpanel]').length;
  out.visible_panels = [...document.querySelectorAll('[role=tabpanel]')].filter(p => !p.hidden).length;
  out.layers = document.querySelectorAll('.ldet').length;
  out.tables = document.querySelectorAll('table').length;

  // the logo must actually have decoded, not just be present in markup
  const img = document.querySelector('img.logo');
  out.logo_present = !!img;
  out.logo_loaded = !!img && img.complete && img.naturalWidth > 0;
  out.logo_w = img ? img.naturalWidth : 0;

  // nothing meant to be read may be transparent
  const reads = [...document.querySelectorAll('h1,h2,h3,.lede,td,th,.card p,.uc dd')]
      .filter(e => e.getClientRects().length);
  out.readable_checked = reads.length;
  out.unreadable = reads.filter(e => parseFloat(getComputedStyle(e).opacity) < 0.5).length;

  const vis = document.querySelector('[role=tabpanel]:not([hidden])');
  out.visible_chars = vis ? vis.innerText.trim().length : 0;
  out.visible_id = vis ? vis.id : null;

  // svg hygiene
  const svgs = [...document.querySelectorAll('svg')].filter(s => s.getClientRects().length);
  out.svgs_visible = svgs.length;
  out.svgs_no_viewbox = svgs.filter(s => !s.getAttribute('viewBox')).length;
  out.svgs_no_label = svgs.filter(s => !s.getAttribute('aria-label')).length;
  return out;
}"""

DRIVE = r"""async () => {
  const wait = ms => new Promise(r => setTimeout(r, ms));
  const out = {};

  // 1. every tab switches, and exactly one panel shows
  out.tab_walk = [];
  for (const id of ['t-over','t-arch','t-first','t-proto','t-cases','t-guide','t-film']) {
    document.getElementById(id).click();
    await wait(70);
    const vis = [...document.querySelectorAll('[role=tabpanel]')].filter(p => !p.hidden);
    out.tab_walk.push({ tab:id, visible:vis.length, id:vis[0] ? vis[0].id : null,
                        chars: vis[0] ? vis[0].innerText.trim().length : 0 });
  }

  // 2. architecture layers open and reveal services
  document.getElementById('t-arch').click();
  await wait(60);
  const dets = [...document.querySelectorAll('.ldet')];
  out.layer_open = [];
  for (const d of dets) {
    d.querySelector('summary').click();
    await wait(45);
    out.layer_open.push({ open: d.open, svcs: d.querySelectorAll('.svc').length,
                          io: d.querySelectorAll('.io .box').length });
  }
  // accordion: opening the last should have closed the others
  out.simultaneously_open = dets.filter(d => d.open).length;

  // 3. the prototype is live
  document.getElementById('t-proto').click();
  await wait(60);
  const nodes = () => document.querySelectorAll('#meshSvg circle').length;
  const score = () => parseInt((document.querySelector('#simOut .sv') || {}).textContent || '0', 10);
  // the rounded overall can coincide across configs; the component vector is the
  // discriminating signal for "is this actually computed from the configuration"
  const vec = () => [...document.querySelectorAll('#simOut .simrow b')].map(b => b.textContent.trim()).join('/');
  out.seed_roster = document.querySelectorAll('#roster .op').length;
  out.seed_nodes = nodes();
  out.seed_score = score();
  out.seed_vec = vec();

  document.getElementById('opname').value = 'Probe Operative';
  document.querySelectorAll('#roleChips .chip')[3].click();   // Executor
  document.getElementById('addOp').click();
  await wait(60);
  out.after_add_roster = document.querySelectorAll('#roster .op').length;
  out.after_add_nodes = nodes();

  document.getElementById('runSim').click();
  await wait(60);
  out.after_add_score = score();
  out.after_add_vec = vec();
  out.warn_after_add = !!document.querySelector('#simOut .gate');

  // switching topology must redraw with a different link count, measured on the
  // 5-operative roster — not after a clear, or both counts collapse to zero
  const linkCount = () => document.querySelectorAll('#meshSvg line').length;
  out.star_links = linkCount();
  document.querySelectorAll('#topoChips .chip')[3].click();   // Mesh
  await wait(60);
  out.mesh_links = linkCount();

  // an Executor with no independent Validator is the riskiest shape in the set —
  // the prototype must say so. This runs last because it clears the roster.
  document.getElementById('clearOps').click();
  await wait(40);
  document.querySelectorAll('#topoChips .chip')[0].click();   // back to Star
  document.getElementById('opname').value = 'Lone Executor';
  document.querySelectorAll('#roleChips .chip')[3].click();   // Executor
  document.getElementById('addOp').click();
  await wait(40);
  document.getElementById('runSim').click();
  await wait(70);
  out.exec_only_warn = ((document.querySelector('#simOut .gate') || {}).innerText || '');

  document.getElementById('clearOps').click();
  await wait(50);
  out.cleared_nodes = nodes();
  out.cleared_empty = !!document.querySelector('#meshSvg .empty');
  return out;
}"""


def main() -> int:
    ap = argparse.ArgumentParser(prog="render_check_deck")
    ap.add_argument("--shots", default=None)
    a = ap.parse_args()
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("UNMEASURABLE — playwright is not installed. This is not a pass.")
        return 2
    if not PAGE.exists():
        print(f"UNMEASURABLE — {PAGE} does not exist. This is not a pass.")
        return 2

    shots = pathlib.Path(a.shots) if a.shots else None
    if shots:
        shots.mkdir(parents=True, exist_ok=True)
    url = PAGE.as_uri()
    report: dict = {"page": str(PAGE.relative_to(REPO)), "widths": {}, "gates": {}}
    fails: list[str] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True)

        for w in WIDTHS:
            pg = browser.new_page(viewport={"width": w, "height": 1000})
            pg.goto(url, wait_until="load")
            pg.wait_for_timeout(800)
            r = pg.evaluate(PROBE)
            report["widths"][w] = r
            if r["h_scroll"]:
                fails.append(f"{w}px — page body scrolls sideways ({r['doc_w']} > {r['win_w']})")
            if r["tabs"] != 7:
                fails.append(f"{w}px — {r['tabs']} tabs, expected 7")
            if r["panels"] != 7:
                fails.append(f"{w}px — {r['panels']} panels, expected 7")
            if r["visible_panels"] != 1:
                fails.append(f"{w}px — {r['visible_panels']} panels visible, expected exactly 1")
            if r["layers"] != 7:
                fails.append(f"{w}px — {r['layers']} architecture layers, expected 7")
            if not r["logo_loaded"]:
                fails.append(f"{w}px — the logo did not decode (present={r['logo_present']})")
            if r["unreadable"]:
                fails.append(f"{w}px — {r['unreadable']} readable elements below 50% opacity")
            if r["svgs_no_viewbox"]:
                fails.append(f"{w}px — {r['svgs_no_viewbox']} visible svg without a viewBox")
            if r["svgs_no_label"]:
                fails.append(f"{w}px — {r['svgs_no_label']} visible svg without an aria-label")
            if shots:
                pg.screenshot(path=str(shots / f"deck-{w}.png"))
            pg.close()

        # drive it
        pg = browser.new_page(viewport={"width": 1400, "height": 1000})
        pg.goto(url, wait_until="load")
        pg.wait_for_timeout(600)
        d = pg.evaluate(DRIVE)
        report["gates"]["drive"] = d

        for row in d["tab_walk"]:
            if row["visible"] != 1:
                fails.append(f"tab {row['tab']} — {row['visible']} panels visible, expected 1")
            if row["chars"] < 400:
                fails.append(f"tab {row['tab']} — only {row['chars']} chars of content")
        for i, L in enumerate(d["layer_open"], 1):
            if not L["open"]:
                fails.append(f"layer {i} — did not open on click")
            if L["svcs"] < 4:
                fails.append(f"layer {i} — {L['svcs']} services revealed, expected >= 4")
            if L["io"] != 4:
                fails.append(f"layer {i} — {L['io']} io boxes, expected 4")
        if d["simultaneously_open"] != 1:
            fails.append(f"accordion — {d['simultaneously_open']} layers open at once, expected 1")
        if d["seed_roster"] != 4:
            fails.append(f"prototype — seeded with {d['seed_roster']} operatives, expected 4")
        if d["seed_score"] < 1:
            fails.append("prototype — no score on load; it must open in a working state")
        if d["after_add_roster"] != d["seed_roster"] + 1:
            fails.append("prototype — adding an operative did not grow the roster")
        if d["after_add_nodes"] <= d["seed_nodes"]:
            fails.append(f"prototype — mesh did not redraw ({d['seed_nodes']} → {d['after_add_nodes']} nodes)")
        if d["after_add_vec"] == d["seed_vec"]:
            fails.append(f"prototype — component scores unchanged after the roster changed "
                         f"({d['seed_vec']}); the score is not computed from the configuration")
        if "Validator" not in d.get("exec_only_warn", ""):
            fails.append("prototype — an Executor with no Validator did not raise the "
                         "independence warning, which is the riskiest shape it must flag")
        if d["mesh_links"] <= d["star_links"]:
            fails.append(f"prototype — Mesh topology ({d['mesh_links']} links) not denser than Star ({d['star_links']})")
        if d["cleared_nodes"] or not d["cleared_empty"]:
            fails.append("prototype — Clear did not empty the mesh")
        if shots:
            pg.screenshot(path=str(shots / "deck-prototype.png"))
            pg.evaluate("() => document.getElementById('t-arch').click()")
            pg.wait_for_timeout(200)
            pg.evaluate("() => document.querySelectorAll('.ldet')[3].querySelector('summary').click()")
            pg.wait_for_timeout(250)
            pg.screenshot(path=str(shots / "deck-architecture-layer4.png"))
        pg.close()

        # no JS: content must still be there
        ctx = browser.new_context(viewport={"width": 1400, "height": 1000}, java_script_enabled=False)
        pg = ctx.new_page()
        pg.goto(url, wait_until="load")
        pg.wait_for_timeout(400)
        chars = len(pg.inner_text("body").strip())
        layers = pg.locator(".ldet").count()
        svcs = pg.locator(".svc").count()
        report["gates"]["no_js"] = {"body_chars": chars, "layers": layers, "services": svcs}
        if chars < 6000:
            fails.append(f"no-js — only {chars} chars readable; the page is not a complete document without script")
        if layers != 7:
            fails.append(f"no-js — {layers} layers present, expected 7")
        if svcs < 40:
            fails.append(f"no-js — {svcs} service tiles present, expected >= 40")
        if shots:
            pg.screenshot(path=str(shots / "deck-nojs.png"), full_page=True)
        ctx.close()

        # reduced motion
        ctx = browser.new_context(viewport={"width": 1400, "height": 1000}, reduced_motion="reduce")
        pg = ctx.new_page()
        pg.goto(url, wait_until="load")
        pg.wait_for_timeout(700)
        rm = pg.evaluate(PROBE)
        anim = pg.evaluate(
            "() => getComputedStyle(document.querySelector('img.logo')).animationName")
        report["gates"]["reduced_motion"] = {"unreadable": rm["unreadable"], "logo_animation": anim}
        if rm["unreadable"]:
            fails.append(f"reduced-motion — {rm['unreadable']} readable elements below 50% opacity")
        if anim not in ("none", ""):
            fails.append(f"reduced-motion — logo still animating ({anim})")
        if shots:
            pg.screenshot(path=str(shots / "deck-reduced-motion.png"))
        ctx.close()

        browser.close()

    report["verdict"] = "PASS" if not fails else "FAIL"
    report["failures"] = fails
    if shots:
        (shots / "render-check-deck.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(f"deck render check: {report['verdict']}")
    for w, r in report["widths"].items():
        print(f"  {w}px  tabs={r['tabs']} panels={r['panels']}/{r['visible_panels']}vis "
              f"layers={r['layers']} logo={r['logo_w']}px h_scroll={r['h_scroll']} "
              f"unreadable={r['unreadable']}")
    d = report["gates"]["drive"]
    print(f"  tab walk   {[t['chars'] for t in d['tab_walk']]} chars per panel")
    print(f"  layers     opened={sum(1 for L in d['layer_open'] if L['open'])}/7 "
          f"services={[L['svcs'] for L in d['layer_open']]} accordion_open={d['simultaneously_open']}")
    print(f"  prototype  roster {d['seed_roster']}→{d['after_add_roster']} "
          f"nodes {d['seed_nodes']}→{d['after_add_nodes']} "
          f"score {d['seed_score']}→{d['after_add_score']} vec {d['seed_vec']}→{d['after_add_vec']} "
          f"links star={d['star_links']} mesh={d['mesh_links']} warn_add={d['warn_after_add']}")
    nj = report["gates"]["no_js"]
    print(f"  no-js      {nj['body_chars']} chars, {nj['layers']} layers, {nj['services']} services")
    print(f"  reduced    unreadable={report['gates']['reduced_motion']['unreadable']} "
          f"logo_anim={report['gates']['reduced_motion']['logo_animation']}")
    for f in fails:
        print(f"  FAIL: {f}")
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
