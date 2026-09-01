"""Render the Client Review in a real browser and prove the meeting surface actually paints.

⭐ **Why this exists.** The global rule is that a query-layer check can pass while every visual is
blank, so a client-facing surface is not done until the rendered page has been loaded and looked
at. ``scripts/render_check_case_study.py`` does this for the case study; this is the same battery
for the artifact that will be on screen in front of the client, plus the three things that are
specific to it:

* **Live Meeting mode is checked as a rendered state, not as source.** It is the mode the meeting
  is actually presented in, it is driven by JavaScript, and nothing until now had ever loaded it.
  The check enters it the way the presenter does (``?mode=meeting``) and re-measures every section.
* **The rendered text is scanned for operator-only strings.** The allow-list is the boundary and
  it is unit-tested, but the boundary protects *fields*; this protects against a leak arriving
  through a hand-written string in the renderer itself.
* **The no-JavaScript path is checked**, because evidence drill-down is ``<details>`` and the page
  claims to work with scripting off. If it ever grows a JS dependency, that claim goes with it.

Usage:
    python scripts/render_check_client_review.py [--html <path>] [--out <dir>]
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re

WIDTHS = (760, 1100, 1440)
SCHEMES = ("light", "dark")

#: Strings that must never appear in rendered text. These are operator vocabulary, internal file
#: layout, and the machine names of the gate's own checks — anything a client reading over a
#: shoulder should not see. Matched against ``innerText``, not the HTML source, so a CSS class
#: name is not a false positive but a visible label is a real one.
FORBIDDEN_TEXT = (
    "diagnostics", "tasks_readable", "narrative_drift", "undeclared_completions",
    "mission_integrity", "MISSION_INTEGRITY_WARNING", ".data/", "tasks.jsonl",
    "C:\\Users", "/home/", "password", "secret", "token", "api_key",
    "Traceback", "None", "null", "undefined",
)

#: Sections the runbook walks through, by the id the renderer actually emits (measured from the
#: built page, not guessed — the first draft of this list guessed "intent" and the page says
#: "asked", which the check caught on its first run).
REQUIRED_SECTIONS = ("summary", "asked", "delivered", "evidence", "decisions", "risks",
                     "next", "acceptance")


def _measure(page):
    return page.evaluate(
        "() => ({"
        "  sections: [...document.querySelectorAll('section')].map(s => ({"
        "     id: s.id, h: Math.round(s.getBoundingClientRect().height)})),"
        "  overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth,"
        "  clipped: [...document.querySelectorAll('h1,h2,h3,.tile .v,.grade,.nstate,.sev')]"
        "     .filter(el => el.scrollWidth > el.clientWidth + 2)"
        "     .map(el => el.textContent.trim().slice(0, 48)),"
        "  text: document.body.innerText,"
        "  navlinks: [...document.querySelectorAll('.rail a')].map(a => a.getAttribute('href')),"
        "  ids: [...document.querySelectorAll('[id]')].map(el => el.id)})")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--html", default="docs/artifacts/client-review-navira.html")
    ap.add_argument("--out", default="docs/evidence/client-review-readiness-2026-09-01")
    a = ap.parse_args(argv)

    repo = pathlib.Path(__file__).resolve().parent.parent
    html = (repo / a.html).resolve()
    out = repo / a.out
    out.mkdir(parents=True, exist_ok=True)
    if not html.exists():
        print(f"no artifact at {html}")
        return 1
    url = html.as_uri()

    from playwright.sync_api import sync_playwright        # noqa: PLC0415

    report = {"artifact": str(html.relative_to(repo)).replace("\\", "/"),
              "bytes": html.stat().st_size, "shots": [], "problems": []}

    def problem(msg):
        report["problems"].append(msg)

    with sync_playwright() as p:
        browser = p.chromium.launch()

        # ---- 1. every width x every scheme x both modes -----------------------------------
        for scheme in SCHEMES:
            for w in WIDTHS:
                for mode in ("standard", "meeting"):
                    ctx = browser.new_context(viewport={"width": w, "height": 1000},
                                              color_scheme=scheme)
                    page = ctx.new_page()
                    errors, failed = [], []
                    page.on("console",
                            lambda m: errors.append(m.text) if m.type == "error" else None)
                    page.on("requestfailed", lambda r: failed.append(r.url))
                    page.goto(url + ("?mode=meeting" if mode == "meeting" else ""),
                              wait_until="load")
                    page.wait_for_timeout(120)               # let the mode toggle settle

                    in_meeting = page.evaluate(
                        "() => document.documentElement.classList.contains('meeting')")
                    m = _measure(page)
                    blank = [s for s in m["sections"] if s["h"] < 20]
                    missing = [s for s in REQUIRED_SECTIONS
                               if s not in [x["id"] for x in m["sections"]]]
                    leaks = [t for t in FORBIDDEN_TEXT if t in m["text"]]

                    name = f"client-review-{mode}-{scheme}-{w}.png"
                    page.screenshot(path=str(out / name), full_page=True)
                    report["shots"].append(
                        {"file": name, "mode": mode, "scheme": scheme, "width": w,
                         "meeting_class_applied": in_meeting,
                         "sections": len(m["sections"]), "blank_sections": blank,
                         "missing_sections": missing, "h_overflow_px": m["overflow"],
                         "clipped": m["clipped"], "text_chars": len(m["text"]),
                         "leaked_strings": leaks,
                         "console_errors": errors, "failed_requests": failed})

                    if mode == "meeting" and not in_meeting:
                        problem(f"{name}: ?mode=meeting did not put the page into meeting mode")
                    if blank:
                        problem(f"{name}: blank section(s) {[b['id'] for b in blank]}")
                    if missing:
                        problem(f"{name}: required section(s) absent {missing}")
                    if m["overflow"] > 1:
                        problem(f"{name}: page scrolls horizontally by {m['overflow']}px")
                    if m["clipped"]:
                        problem(f"{name}: clipped text {m['clipped'][:3]}")
                    if leaks:
                        problem(f"{name}: operator-only string(s) visible: {leaks}")
                    if errors:
                        problem(f"{name}: {len(errors)} console error(s): {errors[:2]}")
                    if failed:
                        problem(f"{name}: {len(failed)} failed request(s): {failed[:2]}")
                    if len(m["text"]) < 2000:
                        problem(f"{name}: only {len(m['text'])} characters of visible text")
                    ctx.close()

        # ---- 2. navigation resolves --------------------------------------------------------
        ctx = browser.new_context(viewport={"width": 1100, "height": 1000})
        page = ctx.new_page()
        page.goto(url, wait_until="load")
        m = _measure(page)
        dangling = [h for h in m["navlinks"]
                    if h and h.startswith("#") and h[1:] not in m["ids"]]
        report["nav"] = {"links": m["navlinks"], "dangling": dangling}
        if dangling:
            problem(f"navigation points at {len(dangling)} target(s) that do not exist: {dangling}")

        # ---- 2b. clicking a nav link must not park the heading under the sticky rail -------
        #
        # Measured rather than assumed: a section screenshot taken with scrollIntoView *did*
        # show the lede under the rail, which looked like a defect until the page's own
        # navigation was driven and the heading landed clear every time. The difference is
        # `scroll-margin`, and it only holds for anchor navigation — so that is what is checked.
        rail_h = page.evaluate("() => {const r=document.querySelector('.rail');"
                               " return r ? Math.round(r.getBoundingClientRect().height) : 0}")
        occluded = []
        for href in [h for h in m["navlinks"] if h and h.startswith("#")]:
            page.click(f".rail a[href='{href}']")
            page.wait_for_timeout(320)
            top = page.evaluate(
                "(sel) => {const h = document.querySelector(sel + ' h2');"
                " return h ? Math.round(h.getBoundingClientRect().top) : 9999}", href)
            if top < rail_h:
                occluded.append({"section": href, "top": top, "rail": rail_h})
        report["nav_occlusion"] = {"rail_height": rail_h, "occluded": occluded}
        if occluded:
            problem(f"clicking navigation parks {len(occluded)} heading(s) under the sticky "
                    f"rail: {occluded}")

        # ---- 3. the meeting toggle is reachable by the presenter ---------------------------
        btn = page.query_selector("#modebtn")
        toggled = None
        if btn is None:
            problem("no meeting-mode button on the page")
        else:
            btn.click()
            page.wait_for_timeout(120)
            toggled = page.evaluate(
                "() => document.documentElement.classList.contains('meeting')")
            if not toggled:
                problem("the meeting-mode button did not enter meeting mode when clicked")
        report["meeting_toggle_click_works"] = toggled

        # ---- 4. no external network dependency, asserted from the browser's own log --------
        externals = [u for u in report["shots"][0]["failed_requests"]]
        req = []
        ctx2 = browser.new_context(viewport={"width": 1100, "height": 900})
        p2 = ctx2.new_page()
        p2.on("request", lambda r: req.append(r.url))
        p2.goto(url, wait_until="load")
        offsite = [u for u in req if not u.startswith("file:")]
        report["requests"] = {"total": len(req), "offsite": offsite}
        if offsite:
            problem(f"the page made {len(offsite)} non-file request(s): {offsite[:3]}")
        ctx2.close()

        # ---- 5. degrade with JavaScript disabled ------------------------------------------
        ctx3 = browser.new_context(viewport={"width": 1100, "height": 1000},
                                   java_script_enabled=False)
        p3 = ctx3.new_page()
        p3.goto(url, wait_until="load")
        nojs = p3.evaluate_handle if False else None
        nojs = {
            "sections": len(p3.query_selector_all("section")),
            "details": len(p3.query_selector_all("details")),
            "text": len(p3.inner_text("body")),
        }
        p3.screenshot(path=str(out / "client-review-nojs-1100.png"), full_page=True)
        report["no_javascript"] = nojs
        if nojs["sections"] < len(REQUIRED_SECTIONS) or nojs["text"] < 2000:
            problem("no-JS: the review did not render without scripting")
        ctx3.close()

        ctx.close()
        browser.close()

    (out / "render-check-client-review.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8")

    print(f"artifact  {report['artifact']}  ({report['bytes']:,} bytes)")
    for s in report["shots"]:
        print(f"  {s['file']:<40} sections={s['sections']} blank={len(s['blank_sections'])} "
              f"overflow={s['h_overflow_px']}px clipped={len(s['clipped'])} "
              f"leaks={len(s['leaked_strings'])} errors={len(s['console_errors'])}")
    print(f"  meeting toggle click works: {report['meeting_toggle_click_works']}")
    print(f"  requests: {report['requests']['total']} total, "
          f"{len(report['requests']['offsite'])} offsite")
    print(f"  no-JS: {report['no_javascript']}")
    print(f"  nav: {len(report['nav']['links'])} link(s), "
          f"{len(report['nav']['dangling'])} dangling, "
          f"{len(report['nav_occlusion']['occluded'])} heading(s) occluded on click")

    if report["problems"]:
        print("\nPROBLEMS")
        for x in report["problems"]:
            print("  -", x)
        return 1
    print("\nRENDERED_CONFIRMED: every section painted at every width, in both colour schemes,"
          "\nin standard and Live Meeting mode; no clipped headings, no horizontal scroll,"
          "\nno console errors, no offsite requests, no operator-only text, and the page still"
          "\nrenders with JavaScript disabled.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
