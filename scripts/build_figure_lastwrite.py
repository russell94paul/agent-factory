"""Emit the last-write-wins figure, with every coordinate computed from the audit log.

    python scripts/build_figure_lastwrite.py            # print the fragment
    python scripts/build_figure_lastwrite.py --insert   # splice into the artifact

The claim the figure makes: a stage that failed 100 times reports `completed`, because the
terminal verdict reads a field that only remembers the last attempt.

Rule 1 of living-systems-ui: a figure that would look identical if the number were different is
decoration. Every tick here is one recorded event, in recorded order, read from
prefect-connectors/orchestrator/data/audits/pipe_4ba17e16.json at build time. Change the log and
the picture changes.
"""
from __future__ import annotations

import collections
import json
import os
import pathlib
import re
import sys

FACTORY = pathlib.Path(__file__).resolve().parent.parent
CONNECTORS = pathlib.Path(os.environ.get("PREFECT_CONNECTORS", FACTORY.parent / "prefect-connectors"))
AUDIT = CONNECTORS / "orchestrator" / "data" / "audits" / "pipe_4ba17e16.json"
ART = FACTORY / "docs" / "artifacts" / "agent-factory.html"
STAGE = "trigger-run"

MARK = "<!-- FIGURE:last-write-wins -->"


def attempts():
    """The recorded outcome of every attempt at STAGE, in order.

    'open' is a real category, not a rounding error: an attempt that started and recorded no
    terminal event. Folding those into failures would overstate what the log actually says.
    """
    ev = json.load(open(AUDIT, encoding="utf-8"))
    if isinstance(ev, dict):
        ev = ev.get("events", list(ev.values()))
    ev = [e for e in ev if isinstance(e, dict) and e.get("stage_name") == STAGE]
    # One mark per RECORDED TERMINAL EVENT, in recorded order. An earlier version paired each
    # outcome to a preceding start and silently dropped any outcome that had none — it reported
    # 82 failures where the raw counters say 100. A figure that disagrees with every other number
    # on the page is worse than no figure, so this counts events, not inferred attempts.
    seq = [("failed" if e["event_type"] == "stage_failed" else "completed")
           for e in ev if e.get("event_type") in ("stage_failed", "stage_completed")]
    starts = sum(1 for e in ev if e.get("event_type") == "stage_started")
    return seq, max(0, starts - len(seq))


def build() -> str:
    seq, open_ = attempts()
    n = len(seq)
    c = collections.Counter(seq)
    fails, done = c["failed"], c["completed"]
    final = seq[-1]

    # ---- geometry, all derived -------------------------------------------------
    X0, BAND_W, Y, H = 34.0, 486.0, 92.0, 46.0
    pitch = BAND_W / n
    w = max(2.0, pitch - 1.6)
    CELL_X, CELL_W = 604.0, 262.0

    FILL = {"failed": "var(--fail)", "completed": "var(--pass)", "open": "var(--unmeas)"}
    OP = {"failed": ".92", "completed": ".95", "open": ".55"}

    o = []
    a = o.append
    a(MARK)
    a('<figure class="fig rv">')
    a('  <div class="fig-scroll">')
    a(f'  <svg viewBox="0 0 900 320" class="lww" role="img" aria-label="Of {n + open_} recorded attempts '
      f'at the {STAGE} stage, {fails} failed, {done} completed and {open_} recorded no outcome. The pipeline\'s stored status '
      f'for the stage keeps only the last attempt, which was {final}, so the terminal verdict '
      f'computed succeeded.">')

    # -- left label
    a(f'    <text class="lbl" x="{X0}" y="52">THE APPEND-ONLY LOG</text>')
    a(f'    <text class="num" x="{X0}" y="79">{n + open_}</text>')
    a(f'    <text class="lbl2" x="{X0 + 44}" y="79">recorded attempts at '
      f'<tspan class="mono2">{STAGE}</tspan></text>')

    # -- the ticks: one rect per recorded attempt, in recorded order
    a('    <g class="ticks">')
    for i, s in enumerate(seq):
        x = X0 + i * pitch
        a(f'      <rect x="{x:.2f}" y="{Y}" width="{w:.2f}" height="{H}" fill="{FILL[s]}" '
          f'opacity="{OP[s]}" style="--i:{i}"></rect>')
    a('    </g>')

    # -- counts under the band, positioned at each run's own centre of mass
    seen = {"failed": 0, "completed": 0, "open": 0}
    for s in ("failed", "completed", "open"):
        idxs = [i for i, v in enumerate(seq) if v == s]
        if not idxs:
            continue
        cx = X0 + (sum(idxs) / len(idxs)) * pitch
        seen[s] = len(idxs)
    # A key ON the figure. The first version explained what a mark meant only in the caption,
    # and a reader could not identify the marks at all — a figure that needs its caption to be
    # legible has failed.
    a(f'    <text class="key" x="{X0}" y="{Y - 12}">each bar is one recorded attempt '
      f'&#183; left to right in the order they happened</text>')
    a(f'    <rect class="sw f" x="{X0}" y="{Y + H + 12}" width="9" height="9"></rect>')
    a(f'    <text class="cnt f" x="{X0 + 15}" y="{Y + H + 21}">{fails} failed</text>')
    a(f'    <rect class="sw p" x="{X0 + 104}" y="{Y + H + 12}" width="9" height="9"></rect>')
    a(f'    <text class="cnt p" x="{X0 + 119}" y="{Y + H + 21}">{done} completed</text>')
    if open_:
        a(f'    <rect class="sw u" x="{X0 + 236}" y="{Y + H + 12}" width="9" height="9"></rect>')
        a(f'    <text class="cnt u" x="{X0 + 251}" y="{Y + H + 21}">{open_} started, '
          f'no outcome recorded</text>')

    # -- the collapse: every tick funnels to one point
    mid = Y + H / 2
    a('    <g class="funnel">')
    a(f'      <path class="fnl" d="M{X0 + BAND_W + 6},{Y} L{CELL_X - 16},{mid - 13} '
      f'L{CELL_X - 16},{mid + 13} L{X0 + BAND_W + 6},{Y + H} Z"></path>')
    a(f'      <path class="fnl-e" d="M{X0 + BAND_W + 6},{mid} L{CELL_X - 10},{mid}" '
      f'marker-end="url(#lwwArrow)"></path>')
    a('    </g>')

    # -- the cell that survives
    a('    <g class="cell">')
    a(f'      <rect x="{CELL_X}" y="{Y - 8}" width="{CELL_W}" height="{H + 16}" rx="2"></rect>')
    a(f'      <text class="ck" x="{CELL_X + 16}" y="{Y + 12}">'
      f'pipeline[&quot;stages&quot;][{STAGE}]</text>')
    a(f'      <text class="cv" x="{CELL_X + 16}" y="{Y + 36}">status = &quot;{final}&quot;</text>')
    a(f'      <text class="cn" x="{CELL_X + CELL_W - 16}" y="{Y + 36}" text-anchor="end">'
      f'last attempt only</text>')
    a('    </g>')
    a(f'    <text class="lbl" x="{CELL_X}" y="52">WHAT THE VERDICT READS</text>')

    # -- the line of code, and what it returns
    a(f'    <text class="code" x="{X0}" y="222">'
      f'any_failed = any(s[&quot;status&quot;] == &quot;failed&quot; for s in '
      f'pipeline[&quot;stages&quot;])</text>')
    a(f'    <text class="ret" x="{X0}" y="256">&#8594; False</text>')
    a(f'    <text class="ret2" x="{X0 + 76}" y="256">&#8594; final_status = '
      f'<tspan class="win">&quot;succeeded&quot;</tspan></text>')
    a(f'    <text class="foot" x="{X0}" y="290">'
      f'{fails} failures are in the log. None of them are in the field the verdict reads.</text>')

    a('    <defs><marker id="lwwArrow" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="7" '
      'markerHeight="7" orient="auto-start-reverse">'
      '<path d="M0,0 L8,4 L0,8 z" fill="currentColor"></path></marker></defs>')
    a('  </svg>')
    a('  </div>')
    a(f'  <figcaption><b>A stage that failed {fails} times reports <span class="mono2">'
      f'{final}</span>.</b> Every mark is one recorded attempt at <span class="mono2">{STAGE}</span> '
      f'in <span class="mono2">pipe_4ba17e16</span>, in recorded order &mdash; {fails} failed, '
      f'{done} completed'
      + (f', {open_} started and recorded no outcome' if open_ else '') +
      f'. The pipeline stores one status per stage and it keeps only the last attempt, so '
      f'<span class="mono2">any_failed</span> sees <span class="mono2">&quot;{final}&quot;</span> '
      f'and the run closes as <span class="mono2">succeeded</span>. The verdict is not lying: it is '
      f'answering a question about final state, and being read as a claim about history. '
      f'<span class="basis m">measured</span> &mdash; parsed from the run\'s own audit log at build '
      f'time.</figcaption>')
    a('</figure>')
    return "\n".join(o) + "\n"


def main() -> int:
    frag = build()
    if "--insert" not in sys.argv:
        print(frag)
        return 0

    src = ART.read_text(encoding="utf-8")
    if MARK in src:
        # Idempotent: a second run replaces the figure rather than stacking another copy.
        src = re.sub(re.escape(MARK) + r".*?</figure>\n", frag, src, count=1, flags=re.S)
        ART.write_text(src, encoding="utf-8")
        print(f"figure REPLACED in {ART.name}")
        return 0

    # Insert at the end of section 3 — the precedent section. The last-write-wins verdict is a
    # third instance of the same pattern the section describes, and the only one we measured
    # ourselves, so it belongs beside the other two rather than in a section of its own.
    m = re.search(r'<section id="failed">.*?(?=\n</section>)', src, re.S)
    if not m:
        print("could not locate section 3; printing instead")
        print(frag)
        return 2
    src = src[:m.end()] + "\n\n" + frag + src[m.end():]
    ART.write_text(src, encoding="utf-8")
    print(f"figure inserted at the end of section 3 in {ART.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
