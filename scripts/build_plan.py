"""Regenerate the build-plan section: velocity, schedule, and one pasteable prompt per lane.

    python scripts/build_plan.py [--insert] [--check] [--target YYYY-MM-DD]

Everything numeric here is measured at build time — gate verdicts from `factory.readiness`,
velocity from the artifact's own git history via `factory.schedule`. The only hand-authored part
is the lane grouping in `factory/lanes.py`, which says so about itself.

**Why this lives on the page rather than in a boot-prompts file.** Paul asked for somewhere he can
open, copy a block, and paste it into a fresh session. Boot prompts remain the durable per-session
home in `aldc-launchpad/boot-prompts/`; this section is the index that points at parallel work and
carries the paste text, generated so it cannot drift the way the tracker section did.

⚠ Prompt blocks wrap (`white-space:pre-wrap`). A `<pre>` with long lines and no wrapping widens
the page, which is the sideways-scroll defect fixed on 2026-08-22 — do not "tidy" that away.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import html
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from factory import schedule as sched                                    # noqa: E402
from factory.lanes import LANES, SIZE, coverage                          # noqa: E402
from factory.readiness import GATES, Unmeasurable                        # noqa: E402

ART = pathlib.Path(__file__).resolve().parent.parent / "docs" / "artifacts" / "agent-factory.html"
MARK = '<section id="plan">'


def e(t) -> str:
    return html.escape(str(t), quote=False)


def _verdicts() -> dict:
    out = {}
    for g in GATES:
        try:
            out[g.id] = g.probe().verdict
        except Unmeasurable:
            out[g.id] = "UNMEASURABLE"
        except Exception:                                                # noqa: BLE001
            out[g.id] = "UNMEASURABLE"
    return out


def build(target: _dt.date | None = None) -> str:
    v = _verdicts()
    o: list[str] = []
    w = o.append
    w(MARK)
    w('  <div class="col sec-h-wrap rv">')
    w('    <div class="sec-n">11 &mdash; the build plan</div>')
    w('    <h2 class="sec-h">What can be built at the same time</h2>')
    w(f'    <p class="sec-sub">{len(LANES)} lanes, grouped so two sessions do not edit the same '
      'file. Gate membership and verdicts are measured; the grouping is a judgement, recorded in '
      '<span class="mono">factory/lanes.py</span> so it can be argued with. Regenerate with '
      '<span class="mono">python scripts/build_plan.py --insert</span>.</p>')
    w('  </div>')

    # ------------------------------------------------------------------ velocity
    w('  <div class="tracker rv">')
    w('    <div class="tracker-head">')
    try:
        vel = sched.velocity()
        proj = sched.projection(vel)
        st = sched.against_target(vel, target)
        w(f'      <h3 class="disp">{vel.last.passed} of {vel.last.total} gates pass</h3>')
        w('      <span class="basis m">velocity MEASURED from git</span>')
        w('    </div>')
        w('    <div style="padding:0 18px 18px">')
        w(f'      <p style="font-size:14px;color:var(--ink-2)">Over {vel.hours:.1f}h of committed '
          f'history, gates passed went <b>{vel.first.passed} &rarr; {vel.last.passed}</b> '
          f'({vel.pass_per_hour:.2f}/h) and the gate set went '
          f'<b>{vel.first.total} &rarr; {vel.last.total}</b> ({vel.scope_per_hour:.2f}/h). '
          f'Remaining went {vel.first.remaining} &rarr; {vel.last.remaining}.</p>')
        if vel.net_remaining_per_hour > 0:
            w('      <p style="font-size:14px;color:var(--ink-2)"><b>The backlog is growing '
              'faster than it is being burned down.</b> That is the expected shape while the '
              'system is still being measured &mdash; measuring is what reveals what is broken '
              '&mdash; but it is why there is no completion date below.</p>')
        if proj["projectable"]:
            w(f'      <p style="font-size:14px"><b>ETA {proj["eta"]:%Y-%m-%d}</b> '
              f'<span class="basis m">DERIVED</span> &mdash; {e(proj["basis"])}</p>')
        else:
            w('      <p style="font-size:14px"><b>Completion: NOT-PROJECTABLE</b> '
              '<span class="basis a">and that is a measurement, not a shrug</span></p>')
            w(f'      <p style="font-size:13px;color:var(--ink-2)">{e(proj["reason"])} '
              f'Will project once {e(proj["criterion"])}.</p>')
        w(f'      <p style="font-size:13px;color:var(--ink-2)">Schedule: '
          f'<b>{e(st["status"])}</b> &mdash; {e(st["detail"])}</p>')
    except sched.Unmeasurable as exc:
        w('      <h3 class="disp">Velocity UNMEASURABLE</h3>')
        w('      <span class="basis a">not a zero</span>')
        w('    </div>')
        w(f'    <div style="padding:0 18px 18px"><p style="font-size:14px">{e(exc)}</p>')
    w('    </div>')
    w('  </div>')

    # ------------------------------------------------------------------ lanes
    for lane in LANES:
        done = [g for g in lane.gates if v.get(g) == "PASS"]
        w('  <div class="tracker rv">')
        w('    <div class="tracker-head">')
        w(f'      <h3 class="disp">{e(lane.title)}</h3>')
        w(f'      <span class="basis {"m" if len(done) == len(lane.gates) else "a"}">'
          f'{len(done)} of {len(lane.gates)} &middot; {e(SIZE[lane.size])}</span>')
        w('    </div>')
        w('    <div style="padding:0 18px 18px">')
        w(f'      <p style="font-size:14px;color:var(--ink-2)">{e(lane.why)}</p>')
        w(f'      <p style="font-size:13px"><span class="mono">{e(lane.repo)}</span> '
          f'&middot; touches <span class="mono">{e(lane.touches)}</span></p>')
        chips = " ".join(
            f'<span class="mono" style="font-size:12px;padding:2px 7px;border:1px solid '
            f'var(--rule);border-radius:2px;white-space:nowrap;color:'
            f'{"var(--pass)" if v.get(g) == "PASS" else "var(--ink-2)"}">{e(g)}</span>'
            for g in lane.gates)
        w(f'      <p style="display:flex;flex-wrap:wrap;gap:6px;margin:10px 0">{chips}</p>')
        if lane.needs_paul:
            w(f'      <p style="font-size:13px;color:var(--unmeas)"><b>Needs Paul:</b> '
              f'{e(lane.needs_paul)}</p>')
        w(f'      <button type="button" class="mono" data-copy="lane-{e(lane.id)}" '
          f'style="font-size:12px;padding:5px 10px;margin:6px 0;cursor:pointer;'
          f'border:1px solid var(--rule);background:var(--surface);color:inherit">'
          f'copy this prompt</button>')
        # pre-wrap, never nowrap: a <pre> with long lines widens the whole page.
        w(f'      <pre id="lane-{e(lane.id)}" class="mono" style="white-space:pre-wrap;'
          f'word-break:break-word;overflow-x:auto;font-size:12px;line-height:1.55;'
          f'padding:12px;border:1px solid var(--rule);background:var(--surface);'
          f'margin:0">{e(lane.full_prompt)}</pre>')
        w('    </div>')
        w('  </div>')

    # ------------------------------------------------------------------ unclaimed
    cov = coverage()
    open_unclaimed = [g for g in cov["unclaimed"] if v.get(g) != "PASS"]
    if open_unclaimed:
        w('  <div class="tracker rv"><div class="tracker-head">')
        w('    <h3 class="disp">Claimed by no lane</h3>')
        w(f'    <span class="basis a">{len(open_unclaimed)} open</span></div>')
        w('    <div style="padding:0 18px 18px"><p style="font-size:14px;color:var(--ink-2)">'
          'Not an error &mdash; but an unclaimed open gate is one nobody has decided who does. '
          f'<span class="mono">{e(", ".join(open_unclaimed))}</span></p></div>')
        w('  </div>')

    w("""  <script>
  document.querySelectorAll('[data-copy]').forEach(function (b) {
    b.addEventListener('click', function () {
      var el = document.getElementById(b.getAttribute('data-copy'));
      if (!el) return;
      var done = function () { var t = b.textContent; b.textContent = 'copied';
                               setTimeout(function () { b.textContent = t; }, 1200); };
      // Clipboard API is unavailable on some hosts; the textarea path is the fallback, and the
      // text is selectable either way so a failure is never a dead end.
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(el.textContent).then(done, function () {});
      } else {
        var ta = document.createElement('textarea');
        ta.value = el.textContent; document.body.appendChild(ta); ta.select();
        try { document.execCommand('copy'); done(); } catch (e) {}
        document.body.removeChild(ta);
      }
    });
  });
  </script>""")
    w("</section>")
    return "\n".join(o)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="build_plan")
    ap.add_argument("--insert", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--target", default=None)
    args = ap.parse_args(argv)
    target = _dt.date.fromisoformat(args.target) if args.target else None
    frag = build(target)

    if not (args.insert or args.check):
        print(frag)
        return 0

    src = ART.read_text(encoding="utf-8")
    if MARK in src:
        new = re.sub(re.escape(MARK) + r".*?\n</section>", frag, src, count=1, flags=re.S)
    else:
        anchor = '<section id="tracker">'
        if anchor not in src:
            print("could not find the tracker section to insert before", file=sys.stderr)
            return 2
        new = src.replace(anchor, frag + "\n\n" + anchor, 1)

    if args.check:
        if new == src:
            print("up to date")
            return 0
        print("STALE: the build-plan section no longer matches the repo")
        return 1
    ART.write_text(new, encoding="utf-8")
    print(f"build-plan section written to {ART.name} ({len(src)} -> {len(new)} chars)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
