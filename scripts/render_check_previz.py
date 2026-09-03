"""Render check for the CELL OS launch previz — open it in a real browser and drive it.

Same route as scripts/manual_render_check.py and scripts/atlas_render_check.py: the
installed Chrome through Playwright.

    python scripts/render_check_previz.py --shots docs/evidence/cell-os-previz-2026-09-02/

Beyond painting, this exercises the two things a static read cannot see:

  1. The previz is a transport. A timeline that *renders* is not the same as a timeline
     that *advances* — so this presses play and proves the clock moved and the stage
     changed shot.
  2. The page must be complete with no JS and at end-state under reduced motion. A
     previz whose findings are parked at opacity 0 is a blank page for anyone whose
     script did not run.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
PAGE = REPO / "docs" / "marketing" / "cell-os-launch-v1" / "previz.html"
WIDTHS = (1400, 1100, 760)

PROBE = r"""() => {
  const out = {};
  out.h_scroll = document.documentElement.scrollWidth > window.innerWidth + 1;
  out.doc_w = document.documentElement.scrollWidth;
  out.win_w = window.innerWidth;

  // the timeline is built from data — prove every block exists and widths sum to 100%
  const blks = Array.from(document.querySelectorAll('#shotLane .blk'));
  out.shot_blocks = blks.length;
  out.width_sum = +blks.reduce((a, b) => a + parseFloat(b.style.flexBasis || 0), 0).toFixed(2);
  out.vo_blocks = document.querySelectorAll('#voLane .vblk').length;
  out.beat_bands = document.querySelectorAll('#beatLane .bnd').length;
  out.table_rows = document.querySelectorAll('#tbody tr').length;

  // the stage must have painted something
  out.stage_chars = (document.getElementById('sin').innerText || '').trim().length;
  out.tc = (document.getElementById('tc').innerText || '').trim();

  // findings must be visible, not parked
  // signature of the JS-rebuilt table, to compare against the authored static rows
  out.rows_sig = Array.from(document.querySelectorAll('#tbody tr'))
      .map(r => r.cells[0].innerText + ':' + r.cells[1].innerText + ':' + r.cells[2].innerText)
      .join(',');

  const finds = Array.from(document.querySelectorAll('.find'));
  out.finds = finds.length;
  out.finds_invisible = finds.filter(f => parseFloat(getComputedStyle(f).opacity) < 0.9).length;

  // nothing meant to be read may be transparent
  const reads = Array.from(document.querySelectorAll('h1,h2,.lede,td,th,.find p'));
  out.unreadable = reads.filter(e => e.getClientRects().length &&
      parseFloat(getComputedStyle(e).opacity) < 0.5).length;
  return out;
}"""

DRIVE = r"""async () => {
  const tcOf = () => document.getElementById('tc').innerText.trim();
  const shotOf = () => document.getElementById('sid').innerText.trim();
  const before = { tc: tcOf(), shot: shotOf() };
  document.getElementById('play').click();
  await new Promise(r => setTimeout(r, 1400));
  const during = { tc: tcOf(), shot: shotOf() };
  document.getElementById('play').click();          // pause
  await new Promise(r => setTimeout(r, 120));
  const paused = tcOf();
  await new Promise(r => setTimeout(r, 500));
  const stillPaused = tcOf();
  // cue a specific shot by clicking its block — shot 23, the anchor
  document.querySelectorAll('#shotLane .blk')[22].click();
  await new Promise(r => setTimeout(r, 120));
  return { before, during, paused, still_paused: stillPaused,
           cued_tc: tcOf(), cued_shot: shotOf(),
           cued_stage: document.getElementById('sin').innerText.replace(/\s+/g, ' ').trim().slice(0, 90) };
}"""


def main() -> int:
    ap = argparse.ArgumentParser(prog="render_check_previz")
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
            pg.wait_for_timeout(700)
            r = pg.evaluate(PROBE)
            report["widths"][w] = r
            if r["h_scroll"]:
                fails.append(f"{w}px — the page body scrolls sideways ({r['doc_w']} > {r['win_w']})")
            if r["shot_blocks"] != 31:
                fails.append(f"{w}px — {r['shot_blocks']} shot blocks, expected 31")
            if abs(r["width_sum"] - 100.0) > 0.5:
                fails.append(f"{w}px — timeline widths sum to {r['width_sum']}%, expected 100%")
            if r["vo_blocks"] != 20:
                fails.append(f"{w}px — {r['vo_blocks']} narration blocks, expected 20")
            if r["table_rows"] != 31:
                fails.append(f"{w}px — {r['table_rows']} table rows, expected 31")
            if r["stage_chars"] < 5:
                fails.append(f"{w}px — the stage painted nothing ({r['stage_chars']} chars)")
            if r["unreadable"]:
                fails.append(f"{w}px — {r['unreadable']} readable elements below 50% opacity")
            if shots:
                pg.screenshot(path=str(shots / f"previz-{w}.png"), full_page=False)
                if w == WIDTHS[0]:
                    pg.screenshot(path=str(shots / "previz-full.png"), full_page=True)
            pg.close()

        # the transport actually advances, pauses, and cues
        pg = browser.new_page(viewport={"width": 1400, "height": 1000})
        pg.goto(url, wait_until="load")
        pg.wait_for_timeout(500)
        d = pg.evaluate(DRIVE)
        report["gates"]["transport"] = d
        if d["during"]["tc"] == d["before"]["tc"]:
            fails.append(f"transport — pressing play did not advance the clock (stuck at {d['before']['tc']})")
        if d["still_paused"] != d["paused"]:
            fails.append("transport — pause did not stop the clock")
        if not d["cued_shot"].startswith("S23"):
            fails.append(f"transport — cueing block 23 landed on {d['cued_shot']}, expected S23")
        if "UNMEASURABLE" not in d["cued_stage"]:
            fails.append(f"transport — shot 23 stage does not show UNMEASURABLE: {d['cued_stage']!r}")
        if shots:
            pg.screenshot(path=str(shots / "previz-shot23-anchor.png"))
        pg.close()

        # no JS: the page must still be a complete, readable document
        ctx = browser.new_context(viewport={"width": 1400, "height": 1000}, java_script_enabled=False)
        pg = ctx.new_page()
        pg.goto(url, wait_until="load")
        pg.wait_for_timeout(300)
        chars = len(pg.inner_text("body").strip())
        finds_vis = pg.locator(".find").count()
        nojs_rows = pg.locator("#tbody tr").count()
        # the authored static rows are the no-script fallback; they must not drift from S[]
        html = PAGE.read_text(encoding="utf-8")
        body = html[html.index('<tbody id="tbody">'):html.index("</tbody>")]
        static_sig = ",".join(
            f"{m[0]}:{m[1]}:{m[2]}" for m in re.findall(
                r'<td class="n">(\d+)</td><td class="t">([\d:.]+)</td><td class="t">([\d.]+s)</td>',
                body))
        js_sig = report["widths"][WIDTHS[0]]["rows_sig"]
        report["gates"]["no_js"] = {"body_chars": chars, "find_panels": finds_vis,
                                    "static_rows": static_sig.count(",") + 1,
                                    "matches_js": static_sig == js_sig}
        if static_sig != js_sig:
            fails.append("no-js — the authored static rows have drifted from the S[] data "
                         "the transport renders. Re-run the generator.")
        if chars < 3000:
            fails.append(f"no-js — only {chars} characters of readable text; the page is not complete without script")
        if nojs_rows != 31:
            fails.append(f"no-js — {nojs_rows} shot rows without script, expected 31")
        if finds_vis != 5:
            fails.append(f"no-js — {finds_vis} finding panels present, expected 5")
        if shots:
            pg.screenshot(path=str(shots / "previz-nojs.png"), full_page=True)
        ctx.close()

        # reduced motion: everything at END state, nothing hidden
        ctx = browser.new_context(viewport={"width": 1400, "height": 1000}, reduced_motion="reduce")
        pg = ctx.new_page()
        pg.goto(url, wait_until="load")
        pg.wait_for_timeout(600)
        rm = pg.evaluate(PROBE)
        report["gates"]["reduced_motion"] = rm
        if rm["finds_invisible"]:
            fails.append(f"reduced-motion — {rm['finds_invisible']} finding panels below 90% opacity")
        if rm["stage_chars"] < 5:
            fails.append("reduced-motion — the stage painted nothing")
        if shots:
            pg.screenshot(path=str(shots / "previz-reduced-motion.png"), full_page=True)
        ctx.close()

        browser.close()

    report["verdict"] = "PASS" if not fails else "FAIL"
    report["failures"] = fails
    if shots:
        (shots / "render-check-previz.json").write_text(
            json.dumps(report, indent=2), encoding="utf-8")

    print(f"previz render check: {report['verdict']}")
    for w, r in report["widths"].items():
        print(f"  {w}px  blocks={r['shot_blocks']} vo={r['vo_blocks']} rows={r['table_rows']} "
              f"sum={r['width_sum']}% h_scroll={r['h_scroll']} stage_chars={r['stage_chars']}")
    t = report["gates"]["transport"]
    print(f"  transport  {t['before']['tc']} -> {t['during']['tc']} (advanced), "
          f"paused at {t['paused']}, cued {t['cued_shot']}")
    nj = report["gates"]["no_js"]
    print(f"  no-js      {nj['body_chars']} chars, {nj['find_panels']} panels, "
          f"{nj['static_rows']} static rows, matches_js={nj['matches_js']}")
    print(f"  reduced    finds_invisible={report['gates']['reduced_motion']['finds_invisible']}")
    for f in fails:
        print(f"  FAIL: {f}")
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
