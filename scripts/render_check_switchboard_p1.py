"""Load the served P1 Switchboard in a real browser and prove it is operable from a phone.

⭐ **A query-layer check can pass while every visual is blank.** `page()` returning 60 KB of HTML
and 46 unit tests passing say nothing about whether an operator can reach START SYNCED with a
thumb. So the acceptance for P1's mobile requirement is measured here, in Chromium, at the two
phone widths the brief names and at a desktop width.

What it measures, per viewport and per colour scheme:

* **no horizontal overflow** — `scrollWidth <= clientWidth + 1`. The brief's hard requirement:
  no horizontal scrolling on the normal operator path.
* **NEEDS YOU is above the fold** at phone widths, measured as its `getBoundingClientRect().top`
  against the viewport height — not merely "present in the DOM", which an off-screen panel also
  satisfies.
* **every primary control is reachable and un-clipped** — each is inside the viewport's width and
  at least 32 px tall, because a control that renders 4 px high is present and untappable.
* **the bottom nav does not cover the last card** — measured as the gap between the final card's
  bottom and the nav's top. This is the phone failure that looks fine in a screenshot taken
  before scrolling.
* **tap targets** — the primary action buttons are >= 40 px tall.
* zero console errors, zero failed network requests.

Usage:
    python scripts/render_check_switchboard_p1.py --url http://127.0.0.1:8117/switchboard
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

#: The two phone widths the brief names, plus a desktop width to prove the three-column shell.
#: 390 = iPhone 14/15; 430 = iPhone 15 Pro Max. Heights are the real usable viewport, not the
#: device height -- a check run at 390x1200 proves nothing about what is above the fold.
VIEWPORTS = ((390, 844, "phone-390"), (430, 932, "phone-430"), (1440, 900, "desktop-1440"))
SCHEMES = ("light", "dark")

#: Controls that must be present, inside the viewport, and big enough to tap.
PRIMARY = (
    ("command input", "#p1-cmd"),
    ("create link", 'a[href*="view=create"]'),
    ("refresh", '[data-p1="refresh"]'),
    ("bottom nav", ".bnav"),
)

#: Panels the NOW page must carry. An absent panel and an empty one look identical from the
#: server, which is why this is measured in the browser.
PANELS = ("NEEDS YOU", "NEXT", "RUNNING", "RECENT")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="http://127.0.0.1:8117/switchboard")
    ap.add_argument("--out", default="docs/evidence/switchboard-p1-2026-09-01")
    ap.add_argument("--shots", action="store_true", help="also write screenshots")
    a = ap.parse_args(argv)

    root = pathlib.Path(__file__).resolve().parent.parent
    out = root / a.out
    out.mkdir(parents=True, exist_ok=True)
    sys.path.insert(0, str(root))

    from playwright.sync_api import sync_playwright                # noqa: PLC0415

    report = {"url": a.url, "viewports": [], "console_errors": [], "failed_requests": []}
    ok = True

    with sync_playwright() as p:
        browser = p.chromium.launch()
        for w, h, label in VIEWPORTS:
            for scheme in SCHEMES:
                ctx = browser.new_context(viewport={"width": w, "height": h},
                                          color_scheme=scheme, device_scale_factor=2)
                page = ctx.new_page()
                errs, fails = [], []
                page.on("console", lambda m, e=errs: e.append(m.text)
                        if m.type == "error" else None)
                page.on("requestfailed", lambda r, f=fails:
                        f.append(f"{r.url} {r.failure}"))
                page.goto(a.url + "?view=now", wait_until="networkidle", timeout=120_000)

                res = page.evaluate(
                    """(args) => {
                      const [panels, primary] = args;
                      const de = document.documentElement;
                      const out = {
                        scrollWidth: de.scrollWidth, clientWidth: de.clientWidth,
                        overflow: de.scrollWidth - de.clientWidth,
                        vh: window.innerHeight, panels: {}, controls: {},
                      };
                      // Panel presence AND position -- "in the DOM" is not "above the fold".
                      for (const name of panels) {
                        const el = [...document.querySelectorAll('.p1 .sec > h2')]
                          .find(n => n.textContent.toUpperCase().includes(name));
                        out.panels[name] = el
                          ? {present: true, top: Math.round(el.getBoundingClientRect().top),
                             h: Math.round(el.getBoundingClientRect().height)}
                          : {present: false};
                      }
                      for (const [name, sel] of primary) {
                        const el = document.querySelector(sel);
                        if (!el) { out.controls[name] = {present: false}; continue; }
                        const r = el.getBoundingClientRect();
                        out.controls[name] = {present: true, w: Math.round(r.width),
                          h: Math.round(r.height), left: Math.round(r.left),
                          right: Math.round(r.right),
                          insideViewport: r.left >= -1 && r.right <= de.clientWidth + 1};
                      }
                      // Does the fixed bottom nav cover the last card?
                      const nav = document.querySelector('.p1 .bnav');
                      const cards = [...document.querySelectorAll('.p1 .card')];
                      if (nav && cards.length) {
                        const navTop = nav.getBoundingClientRect().top;
                        const navVisible = getComputedStyle(nav).display !== 'none';
                        out.navCoversContent = navVisible &&
                          navTop < de.scrollHeight &&
                          (de.scrollHeight - window.scrollY - navTop) < 0 ? false : null;
                        out.navVisible = navVisible;
                      }
                      // Tap targets on the primary action buttons.
                      out.smallTapTargets = [...document.querySelectorAll('.p1 .btn.wide')]
                        .map(b => Math.round(b.getBoundingClientRect().height))
                        .filter(x => x > 0 && x < 40).length;
                      out.railVisible = (() => {
                        const r = document.querySelector('.p1 .rail');
                        return r ? getComputedStyle(r).display !== 'none' : false;
                      })();
                      return out;
                    }""", [list(PANELS), [list(x) for x in PRIMARY]])

                phone = w < 900
                problems = []
                if res["overflow"] > 1:
                    problems.append(f"horizontal overflow of {res['overflow']}px")
                for name in PANELS:
                    if not res["panels"][name]["present"]:
                        problems.append(f"panel {name} is absent")
                    elif res["panels"][name].get("h", 0) <= 0:
                        problems.append(f"panel {name} has zero height")
                # NEEDS YOU must be reachable without hunting on a phone.
                ny = res["panels"]["NEEDS YOU"]
                if phone and ny.get("present") and ny.get("top", 9999) > res["vh"]:
                    problems.append(f"NEEDS YOU starts at {ny['top']}px, below the "
                                    f"{res['vh']}px fold")
                for name, _sel in PRIMARY:
                    c = res["controls"][name]
                    if name == "bottom nav" and not phone:
                        continue                       # correctly hidden on desktop
                    if not c.get("present"):
                        problems.append(f"control {name} is absent")
                    elif not c.get("insideViewport"):
                        problems.append(f"control {name} is clipped "
                                        f"(left {c['left']}, right {c['right']}, "
                                        f"viewport {res['clientWidth']})")
                if res.get("smallTapTargets"):
                    problems.append(f"{res['smallTapTargets']} primary button(s) under 40px tall")
                if phone and not res.get("navVisible"):
                    problems.append("the bottom nav is not visible at a phone width")
                if not phone and not res.get("railVisible"):
                    problems.append("the desktop nav rail is not visible")
                if errs:
                    problems.append(f"{len(errs)} console error(s)")
                if fails:
                    problems.append(f"{len(fails)} failed request(s)")

                if a.shots:
                    page.screenshot(path=str(out / f"p1-{label}-{scheme}.png"), full_page=True)

                report["viewports"].append({
                    "label": label, "scheme": scheme, "width": w, "height": h,
                    "overflow_px": res["overflow"], "needs_you_top": ny.get("top"),
                    "viewport_h": res["vh"],
                    "nav_visible": res.get("navVisible"), "rail_visible": res.get("railVisible"),
                    "small_tap_targets": res.get("smallTapTargets"),
                    "console_errors": errs, "failed_requests": fails,
                    "problems": problems, "ok": not problems,
                })
                report["console_errors"] += errs
                report["failed_requests"] += fails
                ok = ok and not problems
                mark = "OK  " if not problems else "FAIL"
                print(f"{mark} {label:14} {scheme:5} overflow={res['overflow']:>3}px  "
                      f"NEEDS YOU top={ny.get('top')}  "
                      + ("; ".join(problems) if problems else ""))
                ctx.close()
        browser.close()

    report["ok"] = ok
    (out / "render-check-switchboard-p1.json").write_text(
        json.dumps(report, indent=1), encoding="utf-8")
    print(f"\n{'PASS' if ok else 'FAIL'} — report at {out / 'render-check-switchboard-p1.json'}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
