"""Render the compiled case study in a real browser and prove every section paints.

⭐ **Why this exists as a script rather than a one-off.** The global rule is that a query-layer check
can pass while every visual is blank, so a dashboard/report/UI change is not done until the rendered
surface has been loaded and looked at. The case-study artifact is exactly such a surface, and P0
shipped without this — both MCP browser backends were unreachable (Playwright's browser cannot see
this machine's localhost; the Chrome extension was not connected). The local `playwright` package
*is* installed with a real Chromium, so the check is available; it just had to be driven directly.

What it measures, per viewport and per colour scheme:

* every top-level ``<section>`` has a non-zero rendered height — a section that compiles and paints
  nothing is the failure this exists to catch;
* the page does not scroll horizontally (``scrollWidth <= clientWidth + 1``);
* zero console errors and zero failed network requests — the page claims to be self-contained, and
  a request that 404s would falsify that;
* ⭐ the walkthrough works with **JavaScript disabled**, because the reveal path is meant to be CSS
  only. This is the one check that would catch a regression turning progressive disclosure into a
  hard dependency.

Usage:
    python scripts/render_check_case_study.py [--out docs/evidence/<dir>] [--html <path>]
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

WIDTHS = (700, 1000, 1400)
SCHEMES = ("light", "dark")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--html", default="docs/artifacts/delivery-001-case-study.html")
    ap.add_argument("--out", default="docs/evidence/artifact-generator-2026-09-01")
    a = ap.parse_args(argv)

    root = pathlib.Path(__file__).resolve().parent.parent
    html = (root / a.html).resolve()
    out = root / a.out
    out.mkdir(parents=True, exist_ok=True)
    if not html.exists():
        print(f"no artifact at {html}")
        return 1
    url = html.as_uri()

    from playwright.sync_api import sync_playwright        # noqa: PLC0415

    report = {"artifact": str(html.relative_to(root)).replace("\\", "/"),
              "bytes": html.stat().st_size, "shots": [], "problems": []}

    with sync_playwright() as p:
        browser = p.chromium.launch()
        for scheme in SCHEMES:
            for w in WIDTHS:
                ctx = browser.new_context(viewport={"width": w, "height": 1000},
                                          color_scheme=scheme)
                page = ctx.new_page()
                errors, failed = [], []
                page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
                page.on("requestfailed", lambda r: failed.append(r.url))
                page.goto(url, wait_until="load")

                # Every section must actually paint. A zero-height section is the whole point.
                sections = page.evaluate(
                    "() => [...document.querySelectorAll('section')].map(s => ({"
                    "  id: s.id, h: Math.round(s.getBoundingClientRect().height)}))")
                blank = [s for s in sections if s["h"] < 20]

                overflow = page.evaluate(
                    "() => document.documentElement.scrollWidth - "
                    "document.documentElement.clientWidth")

                name = f"case-study-{scheme}-{w}.png"
                page.screenshot(path=str(out / name), full_page=True)
                shot = {"file": name, "scheme": scheme, "width": w,
                        "sections": len(sections), "blank_sections": blank,
                        "h_overflow_px": overflow,
                        "console_errors": errors, "failed_requests": failed}
                report["shots"].append(shot)
                if blank:
                    report["problems"].append(f"{name}: blank section(s) {[b['id'] for b in blank]}")
                if overflow > 1:
                    report["problems"].append(f"{name}: page scrolls horizontally by {overflow}px")
                if errors:
                    report["problems"].append(f"{name}: {len(errors)} console error(s)")
                if failed:
                    report["problems"].append(f"{name}: {len(failed)} failed request(s)")
                ctx.close()

        # ---- the static-degradation check, which is the load-bearing one -------------------
        ctx = browser.new_context(viewport={"width": 1000, "height": 1000},
                                  java_script_enabled=False)
        page = ctx.new_page()
        page.goto(url, wait_until="load")
        nojs = page.evaluate(
            "() => ({"
            "  scenes: document.querySelectorAll('.scene').length,"
            "  choices: document.querySelectorAll('.choices label').length,"
            "  conseq: document.querySelectorAll('.conseq').length,"
            "  reveals: document.querySelectorAll('details.reveal').length,"
            "  cf: document.querySelectorAll('.cf').length,"
            "  text: document.body.innerText.length})")
        page.screenshot(path=str(out / "case-study-nojs-1000.png"), full_page=True)
        report["no_javascript"] = nojs
        if nojs["scenes"] < 1 or nojs["conseq"] < 1 or nojs["text"] < 10000:
            report["problems"].append("no-JS: the walkthrough did not render without scripting")
        ctx.close()
        browser.close()

    (out / "render-check.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"artifact  {report['artifact']}  ({report['bytes']:,} bytes)")
    for s in report["shots"]:
        print(f"  {s['file']:<28} sections={s['sections']} blank={len(s['blank_sections'])} "
              f"overflow={s['h_overflow_px']}px errors={len(s['console_errors'])} "
              f"failed_req={len(s['failed_requests'])}")
    print(f"  no-JS: {report['no_javascript']}")
    if report["problems"]:
        print("\nPROBLEMS")
        for x in report["problems"]:
            print("  -", x)
        return 1
    print("\nall sections painted, no overflow, no console errors, no failed requests,"
          "\nand the walkthrough renders with JavaScript disabled.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
