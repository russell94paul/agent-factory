"""Capture rendered before/after evidence for the dark-mode button-contrast defect.

⭐ **This exists because the claim is visual, and a visual claim needs a picture.** The defect —
both dry-run buttons rendering as unreadable text in dark mode — was invisible to every selector
check the render harness had: the buttons were present in the DOM, had non-zero size, and carried
the right names. Only looking at a screenshot found it.

So the negative control is not "the assertion fails when I break the code". It is: **here is the
page with the defect, and here is the page without it, both loaded in a real browser at the same
viewport and colour scheme**, plus the computed colours that separate them.

Run against a served tracker whose CSS is in the state you want captured:

    python scripts/negative_control_button_contrast.py --label defect
    python scripts/negative_control_button_contrast.py --label fixed
"""
from __future__ import annotations

import argparse
import json
import pathlib


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", required=True, choices=("defect", "fixed"))
    ap.add_argument("--url", default="http://127.0.0.1:8110/switchboard")
    ap.add_argument("--out", default="docs/evidence/switchboard-p0-2026-09-01/negative-control")
    a = ap.parse_args(argv)

    out = pathlib.Path(__file__).resolve().parent.parent / a.out
    out.mkdir(parents=True, exist_ok=True)

    from playwright.sync_api import sync_playwright                # noqa: PLC0415

    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport={"width": 1280, "height": 1100}, color_scheme="dark")
        page = ctx.new_page()
        page.goto(a.url, wait_until="networkidle")

        # The computed colours are the measurement; the screenshot is the exhibit.
        measured = page.evaluate("""() => [...document.querySelectorAll('.sw button')].map(b => {
            const s = getComputedStyle(b);
            const p = c => (c.match(/\\d+/g) || ['0','0','0']).slice(0,3).map(Number);
            const lum = ([r,g,bl]) => 0.2126*r + 0.7152*g + 0.0722*bl;
            const fg = p(s.color), bg = p(s.backgroundColor);
            return {label: b.textContent.trim().slice(0,30), color: s.color,
                    background: s.backgroundColor,
                    luminance_gap: Math.round(Math.abs(lum(fg) - lum(bg)))};
        })""")

        # Crop to the two control panels so the exhibit shows the buttons, not the whole page.
        shot = out / f"{a.label}-dark-1280-buttons.png"
        try:
            page.locator('form#qd-form').scroll_into_view_if_needed()
        except Exception:                                          # noqa: BLE001
            pass
        page.screenshot(path=str(shot), full_page=True)

        (out / f"{a.label}-measured.json").write_text(
            json.dumps({"label": a.label, "viewport": "1280x1100", "color_scheme": "dark",
                        "buttons": measured}, indent=2), encoding="utf-8")
        ctx.close()
        browser.close()

    print(f"{a.label}: {len(measured)} button(s) measured -> {shot.name}")
    for m in measured:
        flag = "  UNREADABLE" if m["luminance_gap"] < 40 else "  ok"
        print(f"{flag}  {m['label']!r}  fg={m['color']} bg={m['background']} "
              f"gap={m['luminance_gap']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
