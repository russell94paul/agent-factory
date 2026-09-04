"""Capture every tab of the local tracker as a standalone HTML file, measuring ONCE.

    python scripts/capture_tracker_ui.py [OUTDIR]

`local_tracker.render()` calls `measure()` once per page, and a cold `measure()` was timed at
416 s on 2026-09-01 — so fetching the ten tabs over HTTP costs an hour and gives ten pages
measured at ten different moments. This measures once and renders every tab against that single
snapshot, which is both ~10x faster and more honest: the ten pages then describe the same instant.

`research` and `switchboard` skip measurement inside `render()` already (board.board() did not
return inside 120 s), so they cost nothing here either way.

Output is self-contained — local_tracker inlines its CSS and loads no fonts, no network, no JS
dependencies — so each file opens standalone from disk.
"""
from __future__ import annotations

import datetime
import pathlib
import sys
import zipfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import local_tracker  # noqa: E402


def main() -> int:
    out = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "tracker-ui"
    out.mkdir(parents=True, exist_ok=True)

    print("measuring once (cold measure was 416 s on 2026-09-01) ...", flush=True)
    t0 = datetime.datetime.now()
    snapshot = local_tracker.measure()
    took = (datetime.datetime.now() - t0).total_seconds()
    print(f"  measured {len(snapshot)} gates in {took:.1f}s\n", flush=True)

    # Freeze it. render() calls measure() per page; every page now shares one instant.
    local_tracker.measure = lambda *a, **k: snapshot

    when = datetime.datetime.now()
    written = []
    for i, (key, _href, label) in enumerate(local_tracker.TABS, start=1):
        path = out / f"{i:02d}-{key}.html"
        t = datetime.datetime.now()
        try:
            html = local_tracker.render(when, tab=key)
        except Exception as exc:  # a tab that cannot render is a finding, not a crash
            print(f"  {label:<12} FAILED  {type(exc).__name__}: {exc}", flush=True)
            continue
        path.write_text(html, encoding="utf-8")
        dt = (datetime.datetime.now() - t).total_seconds()
        print(f"  {label:<12} {len(html):>8,} bytes  {dt:5.1f}s  -> {path.name}", flush=True)
        written.append(path)

    zp = out.parent / "agent-factory-tracker-ui.zip"
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
        for p in written:
            z.write(p, p.name)
    print(f"\n{len(written)}/{len(local_tracker.TABS)} tabs captured")
    print(f"zip: {zp}  ({zp.stat().st_size:,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
