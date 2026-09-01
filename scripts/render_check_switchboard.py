"""Load the served /switchboard in a real browser and prove every panel paints.

⭐ **A query-layer check can pass while every visual is blank.** `render()` returning 25 KB of HTML
and the tests passing say nothing about whether the operator sees anything — the estate has already
been bitten by a surface that passed its data check and rendered "Error loading data" in every
visual. So the Switchboard is not done until the rendered page has been loaded and looked at.

Shape copied from `render_check_case_study.py`, which established that the locally installed
`playwright` package drives a real Chromium here even when both MCP browser backends are
unreachable.

What it measures, per viewport and per colour scheme:

* every panel `<section>` inside `.sw` has a non-zero rendered height, and every panel named in
  `EXPECTED` is present — a page that silently drops the NEEDS YOU panel is the failure mode this
  exists to catch, because an absent panel and an empty one look identical from the server;
* the page does not scroll horizontally;
* zero console errors and zero failed network requests;
* ⭐ **the rendered NEEDS YOU count equals the count the projection measured** — the one check that
  proves the number on screen came from `switchboard.state()` and not from a template.

Usage:
    python scripts/render_check_switchboard.py --url http://127.0.0.1:8110/switchboard
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

WIDTHS = (900, 1280, 1600)
SCHEMES = ("light", "dark")

#: Panel headings that must exist on every render. The list is the acceptance question set from the
#: brief, turned into things a browser can look for.
EXPECTED = ("CRITICAL PATH", "READY IN PARALLEL", "START SYNCED", "NEEDS YOU", "SESSIONS",
            "QUICK DISPATCH", "UPSTREAM", "WORKTREES", "WARNINGS")

#: Controls that must be present and correctly wired. A form that renders but posts nowhere is the
#: same class of defect as a panel that paints nothing.
CONTROLS = ('form[action="/switchboard/start"]', 'select[name="target"]',
            'select[name="worktree"]', 'select[name="reader"]', 'textarea[name="note"]',
            'button[name="dry"]',
            'form[action="/switchboard/dispatch"]', 'textarea#qd-prompt',
            'select[name="session"]', 'button#qd-go')


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="http://127.0.0.1:8110/switchboard")
    ap.add_argument("--out", default="docs/evidence/switchboard-p0-2026-09-01")
    a = ap.parse_args(argv)

    root = pathlib.Path(__file__).resolve().parent.parent
    out = root / a.out
    out.mkdir(parents=True, exist_ok=True)

    sys.path.insert(0, str(root))
    from factory import switchboard as sb                          # noqa: PLC0415

    # Measured BEFORE the browser opens, from the same function the page calls. If the rendered
    # badge disagrees with this, the page is displaying something other than measured state — which
    # is the whole property under test.
    expected_needs = sb.state()["needs_you_count"]

    from playwright.sync_api import sync_playwright                # noqa: PLC0415

    report = {"url": a.url, "expected_needs_you": expected_needs, "shots": [], "problems": []}

    with sync_playwright() as p:
        browser = p.chromium.launch()
        for scheme in SCHEMES:
            for w in WIDTHS:
                ctx = browser.new_context(viewport={"width": w, "height": 1100},
                                          color_scheme=scheme)
                page = ctx.new_page()
                errs, fails = [], []
                page.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
                page.on("requestfailed",
                        lambda r: fails.append(f"{r.method} {r.url}"))
                resp = page.goto(a.url, wait_until="networkidle")
                if resp is None or resp.status != 200:
                    report["problems"].append(
                        f"{scheme}/{w}: HTTP {getattr(resp, 'status', 'no response')}")
                    ctx.close()
                    continue

                panels = page.evaluate("""() => [...document.querySelectorAll('.sw section')]
                    .map(s => ({h: s.getBoundingClientRect().height,
                                t: (s.querySelector('h2')||{}).textContent||''}))""")
                for pn in panels:
                    if pn["h"] <= 0:
                        report["problems"].append(
                            f"{scheme}/{w}: panel {pn['t'].strip()[:40]!r} rendered zero height")
                seen = " ".join(pn["t"].upper() for pn in panels)
                for want in EXPECTED:
                    if want not in seen:
                        report["problems"].append(f"{scheme}/{w}: panel {want} is missing entirely")

                for sel in CONTROLS:
                    if page.locator(sel).count() == 0:
                        report["problems"].append(f"{scheme}/{w}: control {sel} is not on the page")

                badge = (page.locator(".sw .needs").first.inner_text() or "").strip()
                if str(expected_needs) not in badge:
                    report["problems"].append(
                        f"{scheme}/{w}: badge {badge!r} does not carry the measured count "
                        f"{expected_needs}")

                over = page.evaluate(
                    "() => document.documentElement.scrollWidth - "
                    "document.documentElement.clientWidth")
                if over > 1:
                    report["problems"].append(f"{scheme}/{w}: page scrolls horizontally by {over}px")

                if errs:
                    report["problems"].append(f"{scheme}/{w}: {len(errs)} console error(s): {errs[:3]}")
                if fails:
                    report["problems"].append(f"{scheme}/{w}: {len(fails)} failed request(s): {fails[:3]}")

                # ⛔ Added after a look at a screenshot caught what every selector check missed:
                # both dry-run buttons rendered as invisible text, because `.sw button.btn` set a
                # background and never a colour, so the browser default (black) sat on a near-black
                # dark-mode ground. A control that exists in the DOM and cannot be read is not a
                # control — and "the element is present" cannot see that.
                unreadable = page.evaluate("""() => [...document.querySelectorAll('.sw button')]
                    .filter(b => {
                      const s = getComputedStyle(b);
                      const p = c => c.match(/\d+/g).slice(0,3).map(Number);
                      const [r,g,bl] = p(s.color), bg = p(s.backgroundColor);
                      const lum = ([r,g,b]) => 0.2126*r + 0.7152*g + 0.0722*b;
                      return Math.abs(lum([r,g,bl]) - lum(bg)) < 40;
                    }).map(b => b.textContent.trim().slice(0,30))""")
                for u in unreadable:
                    report["problems"].append(
                        f"{scheme}/{w}: button {u!r} has too little contrast to read")

                size = page.evaluate("() => document.documentElement.outerHTML.length")
                if size > 120_000:
                    report["problems"].append(
                        f"{scheme}/{w}: the page is {size:,} bytes — a command page that large "
                        f"means a panel is rendering an archive rather than a nudge")
                report.setdefault("page_bytes", size)

                shot = out / f"switchboard-{scheme}-{w}.png"
                page.screenshot(path=str(shot), full_page=True)
                report["shots"].append({"scheme": scheme, "width": w, "file": shot.name,
                                        "panels": len(panels), "badge": badge})
                ctx.close()
        browser.close()

    (out / "render-check.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    print(f"\n{len(report['shots'])} shot(s) -> {out}")
    if report["problems"]:
        print(f"\n⛔ {len(report['problems'])} problem(s)")
        return 1
    print("\n✅ every panel painted in both schemes at every width")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
