"""Render a compiled :class:`factory.case_study.CaseStudy` as one self-contained HTML file.

⛔ This module renders :meth:`CaseStudy.to_dict` and nothing else. It has no access to
``CaseStudy.diagnostics`` by construction, so an operator-only field cannot reach the page through
a renderer mistake.

**Static first, enhancement second.** The gate decision of 2026-09-01 requires that the progressive
scene walkthrough never become necessary to understand the artifact. So every scene's choices,
consequences, actual outcome, later evidence and counterfactual are *in the DOM at all times*, and
the interactive reveal is done with **CSS only** — a radio input and a sibling selector. There is no
JavaScript in the reveal path at all. With scripting disabled the page loses a "walkthrough" mode
toggle and nothing else: every fact stays inspectable, and ``<details>`` disclosure is native.

**Actual history and counterfactual are never rendered by the same component.** The actual outcome
is a ``.actual`` panel; a capability's counterfactual is a ``.cf`` panel that always carries its
maturity chip. :class:`factory.assertions.Counterfactual` has no ``status`` field, so it cannot be
passed to the outcome renderer even by mistake — the separation is structural, and this module only
has to keep it visible.
"""
from __future__ import annotations

import html
from typing import Any, Dict, List, Optional

from .case_study import BLIND_INSTRUMENT, NUMBERLESS, CaseStudy, CLIENT_DELIVERY, FACTORY_MISSION

_TRACK = {
    CLIENT_DELIVERY: ("client", "Client delivery"),
    FACTORY_MISSION: ("factory", "Factory mission"),
}

_MATURITY = {
    "EXERCISED": ("exercised", "Exercised — observed running"),
    "IMPLEMENTED_NOT_EXERCISED": ("impl", "Built — not run here"),
    "SIMULATED": ("sim", "Simulated"),
    "PROPOSED": ("prop", "Proposed — not built"),
}

_STRENGTH = {
    "WOULD_BLOCK": ("s-block", "Would block"),
    "WOULD_INTERCEPT": ("s-intercept", "Would intercept"),
    "WOULD_WARN": ("s-warn", "Would warn"),
    "WOULD_PROVIDE_CONTEXT": ("s-ctx", "Would provide context"),
    "MAY_REDUCE_LIKELIHOOD": ("s-may", "May reduce likelihood"),
    "NO_MATERIAL_EFFECT": ("s-none", "No material effect"),
}

_RISK = {"HIGH": "r-high", "MEDIUM": "r-med", "LOW": "r-low", "NONE": "r-none"}

_STATUS = {
    "CURRENT": ("st-cur", "Current"),
    "STALE": ("st-stale", "Stale"),
    "UNVERIFIED": ("st-unv", "Unverified"),
    "SUPERSEDED": ("st-sup", "Superseded"),
    "REFUTED": ("st-ref", "Refuted"),
    "CONTRADICTED": ("st-con", "Contradicted"),
}

_FRESH = {
    "LIVE": ("f-live", "Live"),
    "LAST_VERIFIED": ("f-lv", "Last verified"),
    "STALE": ("f-stale", "Stale"),
    "UNAVAILABLE": ("f-un", "Source unavailable"),
}


def e(v: Any) -> str:
    """Escape. ``None`` becomes an em dash, never an empty cell that reads as a zero."""
    if v is None or v == "":
        return "—"
    return html.escape(str(v), quote=False)


def _p(v: Any) -> str:
    return f"<p>{e(v)}</p>" if v not in (None, "", "—") else ""


def _chip(cls: str, label: str) -> str:
    return f'<span class="chip {cls}">{e(label)}</span>'


def _refs(refs: List[str]) -> str:
    if not refs:
        return ""
    items = "".join(f"<li><code>{e(r)}</code></li>" for r in refs)
    return (f'<details class="refs"><summary>Evidence ({len(refs)})</summary>'
            f"<ul>{items}</ul></details>")


_CSS = """
/* Tokens. Every colour is defined on bare :root first, so no value has its only definition
   inside a media query — a page whose dark block is the only definition renders unstyled for a
   viewer whose system reports neither preference. */
:root{
  --bg:#fbfaf8; --panel:#ffffff; --ink:#1a1a1c; --muted:#5c5c66; --line:#e2e0dc;
  --accent:#2f5d8a; --accent-soft:#eaf1f8;
  --client:#8a4b2f; --client-soft:#f7ede8;
  --factory:#2f6b58; --factory-soft:#e8f2ee;
  --warn:#8a6d2f; --warn-soft:#f8f2e4;
  --danger:#8a2f3a; --danger-soft:#f8e9eb;
  --sim:#5a4b8a; --sim-soft:#efecf8;
  --base:16px; --mono:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
  --sans:system-ui,-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --bg:#131316; --panel:#1b1b1f; --ink:#eceaea; --muted:#a2a2ae; --line:#2e2e35;
    --accent:#8ab4de; --accent-soft:#1c2833;
    --client:#d99b7c; --client-soft:#2b2019;
    --factory:#7fc4ab; --factory-soft:#17261f;
    --warn:#d9bc7c; --warn-soft:#2a2419;
    --danger:#e0919c; --danger-soft:#2c1a1e;
    --sim:#a99ad9; --sim-soft:#211d2e;
  }
}
:root[data-theme="dark"]{
  --bg:#131316; --panel:#1b1b1f; --ink:#eceaea; --muted:#a2a2ae; --line:#2e2e35;
  --accent:#8ab4de; --accent-soft:#1c2833;
  --client:#d99b7c; --client-soft:#2b2019;
  --factory:#7fc4ab; --factory-soft:#17261f;
  --warn:#d9bc7c; --warn-soft:#2a2419;
  --danger:#e0919c; --danger-soft:#2c1a1e;
  --sim:#a99ad9; --sim-soft:#211d2e;
}

*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:var(--base)/1.55 var(--sans);
     -webkit-font-smoothing:antialiased}
.wrap{max-width:1080px;margin:0 auto;padding:32px 20px 96px}
h1,h2,h3,h4{line-height:1.25;margin:0 0 .4em}
h1{font-size:1.9rem;letter-spacing:-.02em}
h2{font-size:1.28rem;letter-spacing:-.01em;margin-top:0}
h3{font-size:1.02rem}
p{margin:0 0 .7em}
code{font-family:var(--mono);font-size:.86em;background:var(--accent-soft);
     padding:.1em .35em;border-radius:4px;word-break:break-word}
a{color:var(--accent)}

.card{background:var(--panel);border:1px solid var(--line);border-radius:12px;
      padding:20px 22px;margin:0 0 18px}
section{margin:0 0 34px;scroll-margin-top:16px}
.shead{display:flex;align-items:baseline;gap:12px;margin:0 0 14px;
       border-bottom:1px solid var(--line);padding-bottom:8px}
.shead .n{font:600 .74rem/1 var(--mono);color:var(--muted);letter-spacing:.1em}
.lede{color:var(--muted);margin:-6px 0 16px}

.chip{display:inline-block;font:600 .68rem/1.6 var(--sans);letter-spacing:.04em;
      padding:.15em .6em;border-radius:999px;border:1px solid var(--line);
      background:var(--panel);color:var(--muted);white-space:nowrap}
.client{background:var(--client-soft);color:var(--client);border-color:transparent}
.factory{background:var(--factory-soft);color:var(--factory);border-color:transparent}
.exercised{background:var(--factory-soft);color:var(--factory);border-color:transparent}
.impl{background:var(--warn-soft);color:var(--warn);border-color:transparent}
.sim,.prop{background:var(--sim-soft);color:var(--sim);border-color:transparent}
.s-block,.s-intercept{background:var(--factory-soft);color:var(--factory);border-color:transparent}
.s-warn,.s-ctx,.s-may{background:var(--warn-soft);color:var(--warn);border-color:transparent}
.s-none{background:var(--panel);color:var(--muted)}
.r-high{background:var(--danger-soft);color:var(--danger);border-color:transparent}
.r-med{background:var(--warn-soft);color:var(--warn);border-color:transparent}
.st-sup,.st-ref,.st-con{background:var(--warn-soft);color:var(--warn);border-color:transparent}
.st-cur{background:var(--factory-soft);color:var(--factory);border-color:transparent}
.f-live{background:var(--factory-soft);color:var(--factory);border-color:transparent}
.f-stale,.f-un{background:var(--warn-soft);color:var(--warn);border-color:transparent}

.grid{display:grid;gap:14px}
@media(min-width:760px){.g2{grid-template-columns:1fr 1fr}.g3{grid-template-columns:repeat(3,1fr)}}

.tile{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:16px 18px}
.tile .k{font:600 .7rem/1.4 var(--sans);letter-spacing:.08em;text-transform:uppercase;
         color:var(--muted)}
.tile .v{font:700 1.6rem/1.2 var(--sans);letter-spacing:-.02em;margin:.15em 0 .1em}
.tile .v.none{font-size:.95rem;font-weight:600;color:var(--muted);letter-spacing:0}
.tile .n{font-size:.8rem;color:var(--muted)}

.scroll{overflow-x:auto;-webkit-overflow-scrolling:touch}
table{border-collapse:collapse;width:100%;font-size:.88rem;min-width:640px}
th,td{text-align:left;vertical-align:top;padding:9px 10px;border-bottom:1px solid var(--line)}
th{font:600 .72rem/1.4 var(--sans);letter-spacing:.06em;text-transform:uppercase;color:var(--muted)}
tbody tr:last-child td{border-bottom:0}

.issue{border-left:3px solid var(--line);padding-left:14px;margin:0 0 16px}
.issue.t-client{border-left-color:var(--client)}
.issue.t-factory{border-left-color:var(--factory)}
.issue h3{margin:0 0 .25em;font-size:.98rem}
.issue .meta{display:flex;flex-wrap:wrap;gap:6px;margin:.4em 0}
.issue .why{color:var(--muted);font-size:.9rem}
.sides{background:var(--warn-soft);border-radius:8px;padding:10px 12px;margin:.5em 0}
.sides .s{margin:0 0 .5em}
.sides .s:last-child{margin:0}
.sides b{color:var(--warn)}

.cf{background:var(--sim-soft);border:1px dashed var(--sim);border-radius:10px;
    padding:12px 14px;margin:.6em 0}
.cf.observed{background:var(--factory-soft);border-style:solid;border-color:var(--factory)}
.cf .cfh{display:flex;flex-wrap:wrap;gap:6px;align-items:center;margin:0 0 .5em}
.cf .cfh b{font-size:.92rem}
.cf p{font-size:.88rem;margin:0 0 .4em}
.cf .rule{font-size:.78rem;color:var(--muted);margin:0}

.actual{background:var(--accent-soft);border-left:3px solid var(--accent);
        border-radius:0 8px 8px 0;padding:12px 14px;margin:.6em 0}
.actual .lbl{font:700 .68rem/1.6 var(--sans);letter-spacing:.1em;color:var(--accent);
             text-transform:uppercase}

/* ---- Scenes: CSS-only progressive reveal. No JavaScript in this path. ---- */
.scene{counter-increment:scene}
.scene .q{font-weight:600;margin:.6em 0 .4em}
.choices{list-style:none;margin:0 0 .6em;padding:0}
.choices li{margin:0 0 6px}
.choices input{position:absolute;opacity:0;width:0;height:0}
.choices label{display:block;border:1px solid var(--line);border-radius:8px;
               padding:9px 12px;cursor:pointer;background:var(--panel);font-size:.92rem}
.choices label:hover{border-color:var(--accent)}
.choices label .key{font:700 .8rem/1 var(--mono);color:var(--muted);margin-right:8px}
.choices input:focus-visible + label{outline:2px solid var(--accent);outline-offset:2px}
.choices input:checked + label{border-color:var(--accent);background:var(--accent-soft)}
.conseq{display:none;font-size:.9rem;color:var(--muted);
        border-left:2px solid var(--line);padding:2px 0 2px 12px;margin:6px 0 0}
.choices input:checked + label + .conseq{display:block}
.conseq .was{display:inline-block;font:700 .66rem/1.6 var(--sans);letter-spacing:.08em;
             color:var(--accent);text-transform:uppercase;margin-right:6px}
.reveal{margin-top:.7em}
.reveal > summary{cursor:pointer;font-weight:600;font-size:.93rem;color:var(--accent);
                  list-style:none}
.reveal > summary::-webkit-details-marker{display:none}
.reveal > summary::before{content:"▸ ";display:inline-block;transition:transform .15s}
.reveal[open] > summary::before{content:"▾ "}

.refs{margin:.5em 0 0}
.refs > summary{cursor:pointer;font-size:.8rem;color:var(--muted)}
.refs ul{margin:.4em 0 0;padding-left:18px;font-size:.8rem}

.note{font-size:.85rem;color:var(--muted);border-left:2px solid var(--warn);
      padding-left:12px;margin:.6em 0}
.recon td .no{color:var(--warn);font-weight:600}
.foot{margin-top:44px;padding-top:16px;border-top:1px solid var(--line);
      font-size:.78rem;color:var(--muted)}
.foot code{font-size:.9em}
.toc{display:flex;flex-wrap:wrap;gap:8px;margin:0 0 26px}
.toc a{font-size:.82rem;text-decoration:none;border:1px solid var(--line);border-radius:999px;
       padding:.25em .8em;color:var(--muted);background:var(--panel)}
.toc a:hover{border-color:var(--accent);color:var(--accent)}
@media print{.toc,.reveal>summary{display:none}.reveal{display:block}.card{break-inside:avoid}}
"""

# The ONLY JavaScript in the page. It adds a theme toggle. It is not in the reveal path, and the
# page is complete without it.
_JS = """
(function(){
  var r=document.documentElement, b=document.getElementById('themer');
  if(!b) return;
  try{ var s=localStorage.getItem('cs-theme'); if(s) r.setAttribute('data-theme',s); }catch(e){}
  b.hidden=false;
  b.addEventListener('click',function(){
    var cur=r.getAttribute('data-theme');
    var next = cur==='dark' ? 'light' : cur==='light' ? 'dark'
             : (matchMedia('(prefers-color-scheme: dark)').matches?'light':'dark');
    r.setAttribute('data-theme',next);
    try{ localStorage.setItem('cs-theme',next); }catch(e){}
  });
})();
"""


def _counterfactual(cf: Optional[Dict[str, Any]]) -> str:
    """Render a capability counterfactual. NEVER the same component as an actual outcome."""
    if not cf:
        return ""
    mat_cls, mat_lab = _MATURITY.get(cf.get("maturity", ""), ("prop", cf.get("maturity", "?")))
    st_cls, st_lab = _STRENGTH.get(cf.get("strength", ""), ("s-none", cf.get("strength", "?")))
    observed = cf.get("maturity") == "EXERCISED"
    rule = ("This capability ran on this delivery and left the evidence named below."
            if observed else
            "SIMULATED. This is what the capability would do — it has not been observed doing it.")
    proof = ""
    if cf.get("exercised_proof"):
        proof = f'<p class="rule">Proof it ran: <code>{e(cf["exercised_proof"])}</code></p>'
    mech = ""
    if cf.get("mechanism_refs"):
        mech = ('<p class="rule">Mechanism: '
                + ", ".join(f"<code>{e(m)}</code>" for m in cf["mechanism_refs"]) + "</p>")
    return f"""<div class="cf{' observed' if observed else ''}">
  <div class="cfh"><b>{e(cf.get('capability'))}</b>{_chip(st_cls, st_lab)}{_chip(mat_cls, mat_lab)}</div>
  {_p(cf.get('expected_effect'))}
  {f'<p class="rule">Remaining human decision: {e(cf.get("remaining_human"))}</p>' if cf.get('remaining_human') else ''}
  {f'<p class="rule">Confidence: {e(cf.get("confidence"))}</p>' if cf.get('confidence') else ''}
  {mech}{proof}
  <p class="rule"><b>{e(rule)}</b></p>
</div>"""


def _issue(i: Dict[str, Any]) -> str:
    tcls, tlab = _TRACK.get(i.get("track", ""), ("", i.get("track", "")))
    chips = [_chip(tcls, tlab)]
    if i.get("client_risk") and i["client_risk"] != "NONE":
        chips.append(_chip(_RISK.get(i["client_risk"], ""), f"Client risk {i['client_risk'].lower()}"))
    if i.get("still_open"):
        chips.append(_chip("r-med", "Still open"))
    if i.get("escape_distance") is not None:
        chips.append(_chip("", f"Escape {i['escape_distance']} → {i.get('potential_escape', '?')}"))
    if i.get("basis"):
        chips.append(_chip("", e(i["basis"])))
    sides = ""
    if i.get("sides"):
        rows = "".join(
            f'<p class="s"><b>{e(s.get("position"))}</b><br>'
            f'<span class="why">{e(s.get("source"))}</span></p>' for s in i["sides"])
        sides = (f'<div class="sides"><p class="why"><b>Preserved contradiction — '
                 f'{len(i["sides"])} positions, neither resolved:</b></p>{rows}</div>')
    causes = " · ".join(e(c) for c in (i.get("root_causes") or []))
    return f"""<div class="issue t-{tcls}" id="issue-{e(i.get('id'))}">
  <h3>{e(i.get('id'))} — {e(i.get('title'))}</h3>
  <div class="meta">{''.join(chips)}</div>
  {_p(i.get('what_happened'))}
  <p class="why"><b>Why:</b> {e(i.get('why'))}</p>
  <p class="why"><b>Root cause:</b> {causes or '—'} · <b>Introduced:</b> {e(i.get('stage_introduced'))}
     · <b>Detected:</b> {e(i.get('stage_detected'))}</p>
  {sides}
  {_counterfactual(i.get('counterfactual'))}
  {_refs(i.get('evidence_refs') or [])}
</div>"""


def _scene(s: Dict[str, Any]) -> str:
    info = "".join(f"<li>{e(x)}</li>" for x in (s.get("information_available") or []))
    choices = []
    for c in (s.get("choices") or []):
        cid = f"sc-{s['id']}-{c.get('key')}"
        was = ('<span class="was">This is what happened</span>' if c.get("was_actual") else "")
        choices.append(
            f'<li><input type="radio" name="sc-{e(s["id"])}" id="{e(cid)}">'
            f'<label for="{e(cid)}"><span class="key">{e(c.get("key"))}</span>'
            f'{e(c.get("label"))}</label>'
            f'<p class="conseq">{was}{e(c.get("consequence"))}</p></li>')
    imp = s.get("impact") or {}
    imp_rows = "".join(
        f"<tr><th>{e(k.title())}</th><td>{e(v)}</td></tr>"
        for k, v in imp.items() if k != "kpi_ref" and v)
    return f"""<article class="card scene" id="scene-{e(s.get('id'))}">
  <h3>Scene {e(s.get('order'))} — {e(s.get('title'))}</h3>
  {_p(s.get('context'))}
  {f'<p class="why"><b>What you know at this point:</b></p><ul>{info}</ul>' if info else ''}
  <p class="q">{e(s.get('question'))}</p>
  <ul class="choices">{''.join(choices)}</ul>
  <details class="reveal"><summary>Show what actually happened</summary>
    <div class="actual"><div class="lbl">Actual history</div>{_p(s.get('actual_outcome'))}</div>
  </details>
  <details class="reveal"><summary>Show what was only discovered later</summary>
    {_p(s.get('later_evidence'))}
  </details>
  <details class="reveal"><summary>Show the Agent Factory counterfactual</summary>
    {_counterfactual(s.get('counterfactual'))}
  </details>
  {f'<div class="scroll"><table><tbody>{imp_rows}</tbody></table></div>' if imp_rows else ''}
  {_refs(s.get('evidence_refs') or [])}
</article>"""


def _kpi(k: Dict[str, Any]) -> str:
    numberless = k.get("measurability") in NUMBERLESS
    if numberless or k.get("value") in (None, ""):
        val = f'<div class="v none">{e(k.get("measurability"))}</div>'
    else:
        unit = f' <span class="n">{e(k.get("unit"))}</span>' if k.get("unit") else ""
        val = f'<div class="v">{e(k.get("value"))}{unit}</div>'
    warn = ('<div class="n"><b>Blind instrument</b> — the instrument exists and cannot see this.</div>'
            if k.get("measurability") == BLIND_INSTRUMENT else "")
    return f"""<div class="tile">
  <div class="k">{e(k.get('name'))}</div>
  {val}
  <div class="n">{e(k.get('basis'))}</div>
  {warn}
  <div class="n">{e(k.get('method'))}</div>
</div>"""


def _shead(n: str, title: str, lede: str = "") -> str:
    return (f'<div class="shead"><span class="n">{e(n)}</span><h2>{e(title)}</h2></div>'
            + (f'<p class="lede">{e(lede)}</p>' if lede else ""))


def render_html(cs: CaseStudy) -> str:
    d = cs.to_dict()
    dl, comp, meta = d["delivery"], d["companion"], d["meta"]
    fcls, flab = _FRESH.get(meta.get("freshness_state"), _FRESH["UNAVAILABLE"])

    n_client = sum(1 for i in d["issues"] if i.get("track") == CLIENT_DELIVERY)
    n_factory = sum(1 for i in d["issues"] if i.get("track") == FACTORY_MISSION)
    n_open = sum(1 for i in d["issues"] if i.get("still_open"))
    cfs = [i.get("counterfactual") for i in d["issues"] + d["scenes"] if i.get("counterfactual")]
    n_exercised = sum(1 for c in cfs if c.get("maturity") == "EXERCISED")
    n_numberless = sum(1 for k in d["kpis"] if k.get("measurability") in NUMBERLESS)

    summary_rows = "".join(
        f"<tr><td><b>{e(r.get('issue'))}</b></td><td>{e(r.get('why'))}</td>"
        f"<td>{e(r.get('detected'))}</td><td>{e(r.get('ideal_interception'))}</td>"
        f"<td>{e(r.get('capability'))}</td><td>{e(r.get('benefit'))}</td></tr>"
        for r in d["summary"])

    tl_rows = ""
    for s in d["timeline"]:
        tcls, tlab = _TRACK.get(s.get("track", ""), ("", ""))
        scls, slab = _STATUS.get(s.get("status", ""), ("", s.get("status", "")))
        sup = (f'<p class="note">Superseded by: {e(s.get("superseded_by"))}</p>'
               if s.get("superseded_by") else "")
        rechecked = ("" if s.get("checked") else
                     '<p class="note">Established once and never re-checked — '
                     'this reads as “true as of the observed date”, not as “true”.</p>')
        tl_rows += f"""<div class="issue t-{tcls}">
  <h3>{e(s.get('title'))}</h3>
  <div class="meta">{_chip(tcls, tlab)}{_chip(scls, slab)}
    {_chip('', e(s.get('occurred_at')) + ' · ' + e(s.get('precision')))}</div>
  <p class="why"><b>Trying to achieve:</b> {e(s.get('intent'))}</p>
  <p class="why"><b>Known:</b> {e(s.get('known'))}</p>
  <p class="why"><b>Believed:</b> {e(s.get('believed'))}</p>
  <p class="why"><b>Assumed:</b> {e(s.get('assumed'))}</p>
  <p class="why"><b>Not yet known:</b> {e(s.get('unknown'))}</p>
  {_p(s.get('action'))}
  <p class="why"><b>Observed:</b> {e(s.get('observed'))} · <b>Re-checked:</b> {e(s.get('checked'))}</p>
  {sup}{rechecked}{_refs(s.get('evidence_refs') or [])}
</div>"""

    pattern_cards = "".join(
        f"""<div class="card">
  <h3>{e(p.get('name'))}</h3>
  <div class="meta">{_chip('r-med', str(p.get('count')) + ' issues')}</div>
  {_p(p.get('statement'))}
  <p class="why"><b>In this record:</b> {' · '.join(e(x) for x in (p.get('issue_ids') or []))}</p>
  {_p(p.get('note'))}
</div>""" for p in d["patterns"])

    lesson_rows = "".join(
        f"""<div class="issue t-factory">
  <h3>{e(l.get('id'))} — {e(l.get('capability'))}</h3>
  {_p(l.get('observation'))}
  <p class="why"><b>Root cause:</b> {e(l.get('root_cause'))}</p>
  <p class="why"><b>Change:</b> {e(l.get('change'))}</p>
  <p class="why"><b>Measurement:</b> {e(l.get('measurement'))}
     · <b>Baseline:</b> {e(l.get('baseline'))}</p>
  <p class="why"><b>Delivery #002 target:</b> {e(l.get('target_002'))}</p>
</div>""" for l in d["lessons"])

    rec = d["reconciliation"]
    rec_rows = "".join(
        f"<tr><td>{e(r.get('label'))}</td><td><code>{e(r.get('task'))}</code></td>"
        f"<td>{e(r.get('claimed'))}</td><td>{e(r.get('actual'))}</td>"
        f"<td class=\"{'no' if r.get('verdict') != 'CURRENT' else ''}\">{e(r.get('verdict'))}</td></tr>"
        for r in rec.get("rows", []))
    rec_note = ""
    if rec.get("status") == "DIVERGED":
        rec_note = ('<p class="note">The narrative was written at a point in time and the task '
                    'store has moved since. The compiler re-checked every claim and reports the '
                    'divergence rather than republishing a stale fact under a fresh timestamp. '
                    'It reports; it does not repair — correcting the narrative belongs to its '
                    'author.</p>')

    shas = " · ".join(f"{e(k)} <code>{e(v)}</code>" for k, v in (meta.get("source_sha") or {}).items())

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(dl.get('name'))} — Delivery #001 forensic case study</title>
<style>{_CSS}</style>
</head>
<body>
<div class="wrap">

<header class="card">
  <div class="meta" style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:10px">
    {_chip(fcls, flab)}{_chip('', 'Read-only projection')}{_chip('', e(meta.get('compiler_version')))}
    <button id="themer" hidden class="chip" style="cursor:pointer">Theme</button>
  </div>
  <h1>Delivery #001 — {e(dl.get('name'))}</h1>
  <p class="lede">Forensic reconstruction and Agent Factory counterfactual.
     Client: {e(dl.get('client'))} · Subject: {e(dl.get('subject'))} · {e(dl.get('window'))}</p>
  <div class="grid g3">
    <div class="tile"><div class="k">Issues on the client delivery</div>
      <div class="v">{n_client}</div><div class="n">{n_open} still open across both tracks</div></div>
    <div class="tile"><div class="k">Issues on the Factory mission</div>
      <div class="v">{n_factory}</div><div class="n">the investigation produced its own failures</div></div>
    <div class="tile"><div class="k">Capabilities actually exercised</div>
      <div class="v">{n_exercised}<span class="n"> of {len(cfs)}</span></div>
      <div class="n">the rest are simulated and marked as such</div></div>
  </div>
  <p class="note"><b>How to read this.</b> Two deliveries are described, not one: the client work,
     and the Factory mission that investigated it. Both produced failures, and the compiler refuses
     to build this page from only one of them. Every capability claim carries a maturity chip —
     only <b>{n_exercised}</b> of {len(cfs)} were observed running; the rest are simulated and
     cannot be read as proven.</p>
</header>

<nav class="toc">
  <a href="#exec">Executive summary</a><a href="#overview">Overview</a>
  <a href="#timeline">Timeline</a><a href="#issues">Issues</a><a href="#patterns">Root patterns</a>
  <a href="#walkthrough">Walkthrough</a><a href="#kpis">KPIs</a><a href="#gaps">Instrumentation gaps</a>
  <a href="#lessons">Lessons</a><a href="#recon">Reconciliation</a>
</nav>

<section id="exec">
  {_shead('01', 'Executive summary',
          'The findings that change a decision, each with where it was caught and where it should have been.')}
  <div class="card scroll"><table>
    <thead><tr><th>Issue</th><th>Why it happened</th><th>Where detected</th>
      <th>Ideal interception</th><th>Capability</th><th>Expected benefit</th></tr></thead>
    <tbody>{summary_rows}</tbody></table></div>
</section>

<section id="overview">
  {_shead('02', 'The two deliveries')}
  <div class="grid g2">
    <div class="card"><div class="meta">{_chip('client', 'Client delivery')}</div>
      <h3>{e(dl.get('name'))}</h3>
      <p class="why">{e(dl.get('window'))}</p>
      <p>{e(dl.get('subject'))}</p></div>
    <div class="card"><div class="meta">{_chip('factory', 'Factory mission')}</div>
      <h3>{e(comp.get('name'))}</h3>
      <p class="why">{e(comp.get('window'))}</p>
      <p>{e(comp.get('relationship'))}</p></div>
  </div>
</section>

<section id="timeline">
  {_shead('03', 'Forensic timeline',
          'What was known, believed and assumed at each step — and what was not yet knowable.')}
  <div class="card">{tl_rows}</div>
</section>

<section id="issues">
  {_shead('04', 'Issues, mistakes and contradictions',
          'Colour marks the track. A preserved contradiction is never resolved to one side.')}
  <div class="card">{''.join(_issue(i) for i in d['issues'])}</div>
</section>

<section id="patterns">
  {_shead('05', 'Root patterns',
          'Individually these are separate issues. Structurally they are four.')}
  <div class="grid g2">{pattern_cards}</div>
</section>

<section id="walkthrough">
  {_shead('06', 'Forensic walkthrough',
          'Each scene shows only what was knowable then. Choose, then reveal. '
          'Choosing changes nothing about what happened — actual history is fixed.')}
  <p class="note">This walkthrough needs no JavaScript. Every consequence, outcome and
     counterfactual is present in the page; the reveal is CSS and native disclosure. Your choice is
     a reading aid — it never rewrites the historical outcome.</p>
  {''.join(_scene(s) for s in d['scenes'])}
</section>

<section id="kpis">
  {_shead('07', 'Delivery measurement',
          f'{len(d["kpis"]) - n_numberless} of {len(d["kpis"])} carry a number. '
          f'The other {n_numberless} render their state instead of an invented figure.')}
  <div class="grid g3">{''.join(_kpi(k) for k in d['kpis'])}</div>
</section>

<section id="gaps">
  {_shead('08', 'Instrumentation gaps',
          'What this delivery could not measure, stated as a gap rather than as a zero.')}
  <div class="card scroll"><table>
    <thead><tr><th>Measure</th><th>State</th><th>Why it cannot be measured yet</th></tr></thead>
    <tbody>{''.join(
        f"<tr><td>{e(k.get('name'))}</td><td>{_chip('r-med', e(k.get('measurability')))}</td>"
        f"<td>{e(k.get('method'))}</td></tr>"
        for k in d['kpis'] if k.get('measurability') in NUMBERLESS)}</tbody></table></div>
</section>

<section id="lessons">
  {_shead('09', 'What Delivery #001 teaches Delivery #002',
          'Each lesson carries a baseline and a target, so #002 can be graded rather than described.')}
  <div class="card">{lesson_rows}</div>
</section>

<section id="recon">
  {_shead('10', 'Reconciliation against live state',
          'The narrative is a point-in-time account. The task store moves.')}
  <div class="card">
    <div class="meta">{_chip('st-sup' if rec.get('status') == 'DIVERGED' else 'st-cur',
                             'Narrative vs store: ' + e(rec.get('status')))}</div>
    <div class="scroll"><table>
      <thead><tr><th>Task</th><th>Id</th><th>Narrative says</th><th>Store says</th>
        <th>Verdict</th></tr></thead>
      <tbody>{rec_rows}</tbody></table></div>
    {rec_note}
  </div>
</section>

<div class="foot">
  <p>Compiled {e(meta.get('compiled_at'))} · freshness <b>{e(flab)}</b> ·
     last verified {e(meta.get('last_verified_at'))} · basis {e(meta.get('basis'))}</p>
  <p>Narrative <code>{e(meta.get('narrative_sha'))}</code> · Prose source {shas or '—'}</p>
  <p>This page is a projection of Agent Factory state. It holds no delivery state of its own,
     needs no running backend, and is regenerated by
     <code>python -m factory.case_study missions/delivery-001/case-study.yaml --out &lt;path&gt;</code>.
     If it disagrees with the task store, the task store is right.</p>
</div>

</div>
<script>{_JS}</script>
</body>
</html>"""
