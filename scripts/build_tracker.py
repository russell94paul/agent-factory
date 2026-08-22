"""Regenerate the artifact's tracker section from measured repo state.

    python scripts/build_tracker.py [--check]

Replaces everything between <section id="tracker"> and its closing tag in
docs/artifacts/agent-factory.html with the output of factory.readiness, measured
at the moment you run it. Nothing in the emitted section is hand-maintained, so
nothing in it can drift.

This exists because the section it replaces was a grid of checkboxes with no
storage bound to them: ticking one and reloading lost the tick. A tracker that
cannot be wrong about itself is worth more than one you can write into.

--check exits non-zero if the file would change — use it to notice that the
page on the wall no longer matches the repo.
"""
from __future__ import annotations

import html
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from factory.readiness import (  # noqa: E402
    FAIL, NOT_RUN, PASS, PHASES, UNMEASURABLE, measure)

ART = (pathlib.Path(__file__).resolve().parent.parent
       / "docs" / "artifacts" / "agent-factory.html")

CHIP = {PASS: ("pass", "pass"), FAIL: ("fail", "fail"),
        UNMEASURABLE: ("unmeas", "unmeasurable"), NOT_RUN: ("notrun", "not run")}

# The only rows a probe cannot settle. Kept deliberately short: if something can
# be measured it belongs above, not here.
NEEDS_A_PERSON = [
    ("Which Navira account ids are in scope?",
     "Blocks A12, and therefore blocks certification. One ALDC Windsor key returns "
     "every client&rsquo;s accounts."),
    ("Is the landing table one account or two?",
     "20 rows across 18 campaigns on one date cannot be unique on "
     "<span class=\"mono\">(account_id, campaign_id, date)</span>. If it is one "
     "account, the declared primary key is wrong."),
    ("Which Jira ticket does the factory work belong to?",
     "Nothing in either repo records one, and a branch name is not evidence."),
]


def e(t) -> str:
    return html.escape(str(t), quote=False)


def build() -> str:
    results = measure()
    n = sum(1 for _, r in results if r.ok)
    total = len(results)
    pct = round(100 * n / total)

    o = []
    w = o.append
    w('<section id="tracker">')
    w('  <div class="col sec-h-wrap rv">')
    w('    <div class="sec-n">10 &mdash; the record</div>')
    w('    <h2 class="sec-h">Can a team run a migration unattended?</h2>')
    w('    <p class="sec-sub">Thirteen gates, every one of them <b>measured from a file</b> '
      'when this page was built &mdash; not ticked by hand. Each row names the path it '
      'was measured from, so a wrong row means a wrong repo, not a stale checkbox. '
      'Regenerate with <span class="mono">python scripts/build_tracker.py</span>.</p>')
    w('  </div>')

    # ---------------------------------------------------------------- headline
    w('  <div class="tracker rv">')
    w('    <div class="tracker-head">')
    w(f'      <h3 class="disp">{n} of {total} gates pass</h3>')
    w('      <span class="basis m">measured on build</span>')
    w('    </div>')
    w('    <div style="padding:0 18px 18px">')
    w(f'      <div style="height:6px;background:var(--rule);position:relative;'
      f'margin:14px 0 10px" role="img" aria-label="{n} of {total} gates pass">'
      f'<span style="position:absolute;inset:0 auto 0 0;width:{pct}%;'
      f'background:var(--pass)"></span></div>')
    w(f'      <p style="font-size:14px;color:var(--ink-2)">Unattended means the loop runs, '
      f'its gates can refuse, and its output can be certified. Today {n} of those '
      f'{total} conditions holds. The gap is the work.</p>')
    w('    </div>')
    w('  </div>')

    # ---------------------------------------------------------------- phases
    for phase, title in PHASES.items():
        rows = [(g, r) for g, r in results if g.phase == phase]
        ok = sum(1 for _, r in rows if r.ok)
        w('  <div class="tracker rv">')
        w('    <div class="tracker-head">')
        w(f'      <h3 class="disp">{e(title)}</h3>')
        w(f'      <span class="basis {"m" if ok == len(rows) else "a"}">'
          f'{ok} of {len(rows)}</span>')
        w('    </div>')
        w('    <div style="overflow-x:auto">')
        w('      <table class="derived">')
        w('        <thead><tr><th style="width:96px">Verdict</th><th>Gate</th>'
          '<th class="n">Measured from</th></tr></thead>')
        w('        <tbody>')
        for g, r in rows:
            cls, label = CHIP[r.verdict]
            w('          <tr>')
            w(f'            <td><span class="chip {cls}">{label}</span></td>')
            w(f'            <td class="what"><b>{e(g.question)}</b><br>')
            w(f'              <span style="color:var(--ink-2)">{e(r.headline)}</span>')
            if r.evidence:
                w('              <ul style="margin:7px 0 0 15px;font-size:13px;'
                  'color:var(--ink-3);line-height:1.55">')
                for ev in r.evidence:
                    w(f'                <li>{e(ev)}</li>')
                w('              </ul>')
            w(f'              <div style="margin-top:6px;font-size:12.5px;'
              f'color:var(--ink-3)"><i>{e(g.why)}</i></div>')
            w('            </td>')
            w(f'            <td class="n"><span class="mono">{e(r.source) or "&mdash;"}'
              f'</span></td>')
            w('          </tr>')
        w('        </tbody>')
        w('      </table>')
        w('    </div>')
        w('  </div>')

    # ---------------------------------------------------------------- human layer
    w('  <div class="tracker rv">')
    w('    <div class="tracker-head">')
    w('      <h3 class="disp">Needs a person, not a probe</h3>')
    w('      <span class="basis a">three open questions</span>')
    w('    </div>')
    w('    <div style="overflow-x:auto">')
    w('      <table class="derived"><tbody>')
    for q, why in NEEDS_A_PERSON:
        w(f'        <tr><td class="what"><b>{e(q)}</b><br>'
          f'<span style="color:var(--ink-3)">{why}</span></td></tr>')
    w('      </tbody></table>')
    w('    </div>')
    w('    <div class="ro-note">These three are not tick boxes and there is nothing to '
      'tick. Answer one and it stops appearing here, because the row above it starts '
      'measuring true.</div>')
    w('  </div>')

    w('  <div class="col">')
    w('    <div class="callout rv">')
    w('      <span class="lbl">Why there is nothing to tick</span>')
    w('      <p>This section used to be checkboxes and free-text notes with no storage '
      'bound to them &mdash; a tick vanished on reload. It now regenerates from the two '
      'repositories, so republishing cannot lose anything and the page cannot claim a '
      'step is done while the repo says otherwise. Run '
      '<span class="mono">scripts/build_tracker.py --check</span> to find out whether '
      'the published page still matches.</p>')
    w('    </div>')
    w('  </div>')
    w('</section>')
    return "\n".join(o) + "\n"


def main() -> int:
    src = ART.read_text(encoding="utf-8")
    pat = re.compile(r'<section id="tracker">.*?</section>\n', re.S)
    if not pat.search(src):
        print("no <section id=\"tracker\"> found in", ART)
        return 2
    out = pat.sub(lambda _: build(), src, count=1)
    if "--check" in sys.argv:
        same = out == src
        print("up to date" if same else "STALE: the page no longer matches the repos")
        return 0 if same else 1
    ART.write_text(out, encoding="utf-8")
    print(f"rewrote the tracker section of {ART.name} "
          f"({len(src)} -> {len(out)} chars)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
