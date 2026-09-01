"""Render a :class:`factory.client_review.ClientReview` as one self-contained HTML page.

**Demo resilience is the design constraint, not an afterthought.** The output is a single file with
no backend, no build step and no runtime data fetch. Evidence drill-down uses ``<details>``, so it
works with JavaScript disabled; JavaScript adds only the Live Meeting toggle and the section rail.
If every service in the estate is down mid-meeting, this file still opens and still tells the truth
about when it was last verified.

The visual language is a **ledger**, because the subject is a claim ledger: every client-visible
statement carries a grade in a left-hand gutter — VERIFIED / CLAIMED / NO EVIDENCE — so a reader
can scan what is proven versus what is merely asserted without reading a word of the prose.

⛔ This module renders ``to_client_dict()`` and nothing else. It has no access to
``ClientReview.diagnostics`` by construction, so an operator-only field cannot reach the page
through a renderer mistake.
"""
from __future__ import annotations

import html
from typing import Any, Dict, List

from .client_review import (CLAIMED, GROUNDED, LIVE, LAST_VERIFIED, STALE, UNAVAILABLE,
                            UNGROUNDED, UNSUBSTANTIATED, FACTORY_PROPOSED, ClientReview)

# --------------------------------------------------------------------------------------------
# Vocabulary → presentation. One table, so a grade cannot be styled two ways in two places.
# --------------------------------------------------------------------------------------------

_GRADE = {
    GROUNDED:   ("verified", "Evidence verified", "Backed by an artefact on file, measured or derived."),
    CLAIMED:    ("claimed", "Claimed", "Stated by us; the supporting artefact did not resolve."),
    UNGROUNDED: ("none", "No evidence", "Nothing has been attached to this yet."),
}

_FRESH = {
    LIVE:          ("fresh-live", "Live"),
    LAST_VERIFIED: ("fresh-verified", "Last verified"),
    STALE:         ("fresh-stale", "Stale"),
    UNAVAILABLE:   ("fresh-none", "Not available"),
}

_EV_STATUS = {
    "VERIFIED":  ("verified", "Verified"),
    "PRESENT":   ("claimed", "On file"),
    "NOT_FOUND": ("none", "Not found"),
}

_SEVERITY = {"HIGH": "sev-high", "MEDIUM": "sev-med", "LOW": "sev-low"}


def e(v: Any) -> str:
    """Escape for HTML text. ``None`` renders as an em dash, never as the string 'None'."""
    if v is None or v == "":
        return "—"
    return html.escape(str(v))


def _para(v: Any) -> str:
    return e(v)


# --------------------------------------------------------------------------------------------
# Stylesheet
# --------------------------------------------------------------------------------------------

#: ⛔ **NO WEBFONT, BY DESIGN.** This page's whole claim is that it opens and tells the truth with
#: no network at all. A `<link>` to a font host is a request that can hang on hotel wifi behind a
#: shared screen, and that silently reflows the page mid-sentence when it finally lands. So the
#: three roles are carried by faces that ship with the presenting machine.
#:
#: The ledger identity survives because the *roles* survive: a sturdy transitional serif for
#: display (Cambria ships with Windows and Office and carries the documentary weight this design
#: wants; Palatino and Iowan Old Style cover macOS), the platform UI face for body copy at
#: screen-share distance, and a real terminal mono for every grade and file path.
#:
#: ⚠ If a webfont is ever reintroduced, `test_the_generated_page_makes_no_external_requests`
#: fails. That test is the control; this comment is only the reason.
_CSS = """
:root{
  --display:Cambria,"Palatino Linotype",Palatino,"Iowan Old Style",ui-serif,Georgia,"Times New Roman",serif;
  --body:-apple-system,BlinkMacSystemFont,"Segoe UI Variable Text","Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;
  --mono:ui-monospace,"Cascadia Mono","Cascadia Code",Consolas,"SF Mono",Menlo,"DejaVu Sans Mono",monospace;
}
:root{
  --paper:#F7F8F7; --raise:#FFFFFF; --sunk:#EFF2F1;
  --ink:#12181C; --ink2:#4A5559;
  --muted:#6C777B; --rule:#D8DEDC; --rule2:#E7ECEA;
  /* ⚠ --base MUST be applied to html, not body. Set on body it scales inherited text but not
     anything sized in rem (every heading, every mono label), so meeting mode grew the paragraphs
     and left the headings behind. Caught in the rendered page, not in review. */
  --accent:#0E6E62; --accent-soft:#E2EFEC;
  --verified:#1F7A4D; --verified-bg:#E6F2EA;
  --claimed:#9A6B10; --claimed-bg:#F7EFDD;
  --none:#8C8C93; --none-bg:#EDEDEF;
  --risk:#A33A2A; --risk-bg:#F6E7E3;
  --base:17px; --lede:1.24rem; --measure:74ch;
  --shadow:0 1px 2px rgba(18,24,28,.05), 0 8px 24px -12px rgba(18,24,28,.12);
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --paper:#0E1316; --raise:#161D21; --sunk:#121A1D;
    --ink:#E6EBEA; --ink2:#B4C0C0; --muted:#8A9799;
    --rule:#26312F; --rule2:#1E2826;
    --accent:#4FBFAC; --accent-soft:#12312D;
    --verified:#5FBE8A; --verified-bg:#122A1E;
    --claimed:#D6A94E; --claimed-bg:#2B2314;
    --none:#8C979A; --none-bg:#1D2427;
    --risk:#E08472; --risk-bg:#2E1A16;
    --shadow:0 1px 2px rgba(0,0,0,.4), 0 8px 24px -12px rgba(0,0,0,.6);
  }
}
:root[data-theme="dark"]{
  --paper:#0E1316; --raise:#161D21; --sunk:#121A1D;
  --ink:#E6EBEA; --ink2:#B4C0C0; --muted:#8A9799;
  --rule:#26312F; --rule2:#1E2826;
  --accent:#4FBFAC; --accent-soft:#12312D;
  --verified:#5FBE8A; --verified-bg:#122A1E;
  --claimed:#D6A94E; --claimed-bg:#2B2314;
  --none:#8C979A; --none-bg:#1D2427;
  --risk:#E08472; --risk-bg:#2E1A16;
  --shadow:0 1px 2px rgba(0,0,0,.4), 0 8px 24px -12px rgba(0,0,0,.6);
}

*{box-sizing:border-box}
html{font-size:var(--base)}
body{
  margin:0; background:var(--paper); color:var(--ink);
  font-family:var(--body);
  font-size:1rem; line-height:1.58; -webkit-font-smoothing:antialiased;
}
h1,h2,h3{font-family:var(--display); font-weight:600;
         text-wrap:balance; margin:0; letter-spacing:-.005em}
.mono{font-family:var(--mono)}
a{color:var(--accent)}
:focus-visible{outline:2px solid var(--accent); outline-offset:3px; border-radius:2px}

.wrap{max-width:1080px; margin:0 auto; padding:0 32px 96px}

/* ---- masthead ------------------------------------------------------------------------- */
.mast{border-bottom:1px solid var(--rule); background:var(--raise); position:relative}
.mast .wrap{padding-top:30px; padding-bottom:24px}
.eyebrow{font-size:.72rem; letter-spacing:.14em; text-transform:uppercase; color:var(--muted)}
.mast h1{font-size:2.05rem; margin:.28em 0 .1em}
.subject{color:var(--ink2); font-size:.95rem; max-width:var(--measure)}

.tiles{display:grid; grid-template-columns:repeat(auto-fit,minmax(210px,1fr)); gap:1px;
       background:var(--rule); border:1px solid var(--rule); margin-top:26px}
.tile{background:var(--raise); padding:16px 18px}
.tile .k{font-size:.7rem; letter-spacing:.13em; text-transform:uppercase; color:var(--muted)}
.tile .v{font-family:var(--display); font-size:1.32rem; margin-top:5px;
         line-height:1.25; font-weight:600}
.tile .n{font-size:.84rem; color:var(--muted); margin-top:3px}

.stamp{display:inline-flex; align-items:center; gap:.45em; font-size:.72rem; letter-spacing:.09em;
       text-transform:uppercase; padding:.3em .62em; border:1px solid currentColor;
       border-radius:2px; font-family:var(--mono)}
.stamp::before{content:""; width:.5em; height:.5em; border-radius:50%; background:currentColor}
.fresh-live{color:var(--verified)} .fresh-verified{color:var(--accent)}
.fresh-stale{color:var(--claimed)} .fresh-none{color:var(--none)}

/* ---- section rail --------------------------------------------------------------------- */
.rail{position:sticky; top:0; z-index:20; background:var(--paper); border-bottom:1px solid var(--rule)}
.rail .wrap{display:flex; gap:2px; padding:0 32px; overflow-x:auto; align-items:stretch}
/* ⚠ Rail sizing is in px, NOT rem, deliberately. Meeting mode raises the rem scale for content;
   if the nav scaled with it the links grew, overflowed, and pushed the mode button off the right
   edge of its own scroll container — the presenter's one control, gone. Meeting mode is supposed
   to REDUCE navigation noise, so chrome holds still while content grows. */
.rail a{font-size:13px; letter-spacing:.1em; text-transform:uppercase; text-decoration:none;
        color:var(--ink2); padding:13px 14px; white-space:nowrap; border-bottom:2px solid transparent}
.rail a:hover{color:var(--ink); border-bottom-color:var(--rule)}
.rail .spacer{flex:1}
.modebtn{align-self:center; margin-left:auto; font-family:var(--mono);
         font-size:12px; letter-spacing:.08em; text-transform:uppercase; cursor:pointer;
         color:var(--ink2); border:1px solid var(--rule);
         border-radius:2px; padding:7px 11px; white-space:nowrap;
         /* Pinned to the right of the scroller so it survives any nav width. The fade makes a
            nav item sliding underneath read as pinned rather than as a clipped label. */
         position:sticky; right:0; background:var(--paper); flex:0 0 auto;
         box-shadow:-14px 0 12px -6px var(--paper)}
.modebtn:hover{color:var(--ink); border-color:var(--accent)}

/* ---- sections ------------------------------------------------------------------------- */
section{padding-top:52px; scroll-margin-top:60px}
.shead{display:flex; align-items:baseline; gap:14px; border-bottom:2px solid var(--ink);
       padding-bottom:9px; margin-bottom:8px}
.shead h2{font-size:1.42rem}
.shead .idx{font-family:var(--mono); font-size:.78rem;
            color:var(--muted); letter-spacing:.06em}
.slede{color:var(--ink2); max-width:var(--measure); margin:14px 0 26px; font-size:1.02rem}

/* ---- the ledger: gutter + body -------------------------------------------------------- */
.entry{display:grid; grid-template-columns:168px 1fr; gap:26px; padding:22px 0;
       border-bottom:1px solid var(--rule2)}
.entry:last-child{border-bottom:none}
.gutter{border-left:3px solid var(--none); padding-left:13px}
.gutter.verified{border-left-color:var(--verified)}
.gutter.claimed{border-left-color:var(--claimed)}
.gutter.none{border-left-color:var(--none)}
.grade{font-family:var(--mono); font-size:.71rem; letter-spacing:.07em;
       text-transform:uppercase; font-weight:500}
.gutter.verified .grade{color:var(--verified)}
.gutter.claimed .grade{color:var(--claimed)}
.gutter.none .grade{color:var(--none)}
.gnote{font-size:.79rem; color:var(--muted); margin-top:5px; line-height:1.42}
.origin{display:inline-block; margin-top:9px; font-family:var(--mono);
        font-size:.66rem; letter-spacing:.08em; text-transform:uppercase; color:var(--muted);
        border:1px dashed var(--rule); border-radius:2px; padding:.22em .5em}
.entry h3{font-size:1.13rem; line-height:1.38}
.entry p{margin:.55em 0 0; max-width:var(--measure); color:var(--ink2)}
.impact{margin-top:12px; padding-left:14px; border-left:2px solid var(--accent-soft);
        color:var(--ink); font-size:.97rem}
.impact b{font-family:var(--mono); font-size:.68rem; letter-spacing:.1em;
          text-transform:uppercase; color:var(--accent); display:block; margin-bottom:2px}

details{margin-top:14px; border:1px solid var(--rule); border-radius:3px; background:var(--raise)}
summary{cursor:pointer; padding:10px 14px; font-family:var(--mono);
        font-size:.76rem; letter-spacing:.06em; text-transform:uppercase; color:var(--ink2);
        list-style:none; display:flex; align-items:center; gap:.6em}
summary::-webkit-details-marker{display:none}
summary::before{content:"+"; color:var(--accent); font-weight:700}
details[open] summary::before{content:"−"}
summary:hover{color:var(--ink)}
.dbody{padding:2px 14px 14px; border-top:1px solid var(--rule2)}
.dbody p{margin:.7em 0; font-size:.95rem}
.src{font-family:var(--mono); font-size:.78rem; color:var(--muted);
     word-break:break-all}

/* ---- intent grid ---------------------------------------------------------------------- */
.two{display:grid; grid-template-columns:repeat(auto-fit,minmax(300px,1fr)); gap:1px;
     background:var(--rule); border:1px solid var(--rule)}
.pane{background:var(--raise); padding:18px 20px}
.pane h3{font-size:.76rem; letter-spacing:.13em; text-transform:uppercase; color:var(--muted);
         font-family:var(--mono); font-weight:500}
.pane ul{margin:.75em 0 0; padding-left:1.15em}
.pane li{margin:.42em 0; color:var(--ink2)}
.pane p{margin:.7em 0 0; color:var(--ink2)}
.objective{font-size:var(--lede); line-height:1.5; color:var(--ink);
           font-family:var(--display); max-width:var(--measure)}

/* ---- stage strip ---------------------------------------------------------------------- */
.stages{display:flex; gap:1px; background:var(--rule); border:1px solid var(--rule);
        margin:22px 0 0; overflow-x:auto}
.stage{background:var(--raise); padding:12px 14px; flex:1; min-width:126px}
.stage .sn{font-family:var(--mono); font-size:.66rem;
           letter-spacing:.08em; color:var(--muted); text-transform:uppercase}
.stage .st{margin-top:4px; font-size:.93rem; line-height:1.3}
.stage.done{background:var(--verified-bg)} .stage.done .sn{color:var(--verified)}
.stage.blocked{background:var(--claimed-bg)} .stage.blocked .sn{color:var(--claimed)}
.stage.now{box-shadow:inset 0 3px 0 var(--accent)}

/* ---- decisions ------------------------------------------------------------------------ */
.decision{border:1px solid var(--rule); background:var(--raise); margin-bottom:20px;
          box-shadow:var(--shadow)}
.decision.blocking{border-left:4px solid var(--accent)}
.dhead{padding:18px 22px 0}
.dflag{font-family:var(--mono); font-size:.68rem; letter-spacing:.11em;
       text-transform:uppercase; color:var(--accent)}
.decision h3{font-size:1.18rem; margin-top:7px; max-width:var(--measure)}
.dctx{padding:0 22px; color:var(--ink2); max-width:var(--measure); margin-top:.6em}
.opts{list-style:none; margin:18px 0 0; padding:0 22px}
.opts li{display:flex; gap:11px; align-items:flex-start; padding:10px 0;
         border-top:1px solid var(--rule2); color:var(--ink2)}
.opts li .r{width:.85em; height:.85em; border-radius:50%; border:1.5px solid var(--none);
            margin-top:.42em; flex:0 0 auto}
.opts li.rec{color:var(--ink); font-weight:600}
.opts li.rec .r{border-color:var(--accent); background:radial-gradient(circle,var(--accent) 42%,transparent 46%)}
.dfoot{margin-top:16px; padding:14px 22px; background:var(--sunk); border-top:1px solid var(--rule);
       font-size:.93rem; color:var(--ink2)}
.dfoot b{font-family:var(--mono); font-size:.68rem; letter-spacing:.1em;
         text-transform:uppercase; color:var(--muted); display:block}

/* ---- risks ---------------------------------------------------------------------------- */
.risk{display:grid; grid-template-columns:168px 1fr; gap:26px; padding:22px 0;
      border-bottom:1px solid var(--rule2)}
.risk:last-child{border-bottom:none}
.sev{font-family:var(--mono); font-size:.71rem; letter-spacing:.08em;
     text-transform:uppercase; padding-left:13px; border-left:3px solid var(--none)}
.sev-high{border-left-color:var(--risk); color:var(--risk)}
.sev-med{border-left-color:var(--claimed); color:var(--claimed)}
.sev-low{border-left-color:var(--none); color:var(--none)}
.owner{font-size:.79rem; color:var(--muted); margin-top:6px}
.needsyou{display:inline-block; margin-top:9px; font-family:var(--mono);
          font-size:.66rem; letter-spacing:.08em; text-transform:uppercase; color:var(--risk);
          background:var(--risk-bg); border-radius:2px; padding:.24em .55em}

/* ---- next ----------------------------------------------------------------------------- */
.nextlist{list-style:none; margin:0; padding:0; counter-reset:n}
.nextlist li{display:grid; grid-template-columns:168px 1fr; gap:26px; padding:16px 0;
             border-bottom:1px solid var(--rule2)}
.nextlist li:last-child{border-bottom:none}
.nstate{font-family:var(--mono); font-size:.71rem; letter-spacing:.07em;
        text-transform:uppercase; color:var(--muted); padding-left:13px;
        border-left:3px solid var(--rule)}
.nstate.blocked{border-left-color:var(--claimed); color:var(--claimed)}
.nextlist .t{font-size:1.03rem}
.nextlist .d{font-size:.87rem; color:var(--muted); margin-top:3px}

/* ---- acceptance ----------------------------------------------------------------------- */
.accept{border:1px solid var(--rule); background:var(--raise); padding:24px 26px; margin-top:8px}
.accept .st{font-family:var(--display); font-size:1.6rem; font-weight:600}
.accept ul{margin:.9em 0 0; padding-left:1.2em; color:var(--ink2)}
.accept li{margin:.35em 0}
.accept .why{font-family:var(--mono); font-size:.7rem;
             letter-spacing:.11em; text-transform:uppercase; color:var(--muted); margin-top:20px}

footer{margin-top:64px; padding-top:20px; border-top:1px solid var(--rule); color:var(--muted);
       font-size:.83rem; display:flex; flex-wrap:wrap; gap:10px 24px}

/* ---- live meeting mode ----------------------------------------------------------------
   The class lands on <html>, so --base moves the rem scale and every heading grows with the
   body copy. On <body> it moved only inherited sizes — see the note beside --base. */
:root.meeting{--base:20px; --measure:66ch; --lede:1.3rem}
.meeting .opsonly{display:none}
.meeting .entry,.meeting .risk,.meeting .nextlist li{grid-template-columns:190px 1fr}
.meeting section{padding-top:66px}

@media (max-width:760px){
  .wrap{padding:0 20px 72px}
  .entry,.risk,.nextlist li{grid-template-columns:1fr; gap:12px}
  .gutter,.sev,.nstate{border-left:none; border-top:3px solid var(--none); padding-left:0;
                       padding-top:9px}
  .gutter.verified{border-top-color:var(--verified)} .gutter.claimed{border-top-color:var(--claimed)}
  .sev-high{border-top-color:var(--risk)} .sev-med{border-top-color:var(--claimed)}
  .nstate.blocked{border-top-color:var(--claimed)}
}
@media print{ .rail,.modebtn{display:none} body{--base:12pt} details{page-break-inside:avoid} }
@media (prefers-reduced-motion:reduce){ *{animation:none!important; transition:none!important} }
"""

_JS = """
(function(){
  var b=document.documentElement, k='cr-meeting';
  function set(on){ b.classList.toggle('meeting',on);
    var t=document.getElementById('modebtn'); if(t) t.textContent = on ? 'Exit meeting mode' : 'Live meeting mode';
    try{ localStorage.setItem(k, on?'1':'0'); }catch(e){} }
  var q = location.search.indexOf('mode=meeting')>-1;
  var s = null; try{ s = localStorage.getItem(k); }catch(e){}
  set(q || s==='1');
  var btn=document.getElementById('modebtn');
  if(btn) btn.addEventListener('click', function(){ set(!b.classList.contains('meeting')); });
  document.addEventListener('keydown', function(ev){
    if(ev.key==='m' && !/^(INPUT|TEXTAREA)$/.test(ev.target.tagName)) set(!b.classList.contains('meeting'));
  });
})();
"""


# --------------------------------------------------------------------------------------------
# Section renderers
# --------------------------------------------------------------------------------------------

def _shead(idx: str, title: str, lede: str = "") -> str:
    out = (f'<div class="shead"><span class="idx">{e(idx)}</span><h2>{e(title)}</h2></div>')
    if lede:
        out += f'<p class="slede">{_para(lede)}</p>'
    return out


def _list_pane(title: str, items: List[str]) -> str:
    if not items:
        return (f'<div class="pane"><h3>{e(title)}</h3>'
                f'<p class="src">None recorded.</p></div>')
    li = "".join(f"<li>{_para(i)}</li>" for i in items)
    return f'<div class="pane"><h3>{e(title)}</h3><ul>{li}</ul></div>'


def _delivered(rows: List[dict], evidence: List[dict]) -> str:
    if not rows:
        return ('<p class="slede">No outcomes have been recorded for this review period.</p>')
    by_src = {ev.get("source"): ev for ev in evidence}
    out = []
    for r in rows:
        cls, label, note = _GRADE.get(r.get("grounding"), _GRADE[UNGROUNDED])
        status = r.get("status", "")
        origin = ('<span class="origin">We proposed this</span>'
                  if r.get("origin") == FACTORY_PROPOSED else
                  '<span class="origin">You asked for this</span>')
        refs = r.get("evidence_refs") or []
        drill = ""
        if refs:
            items = []
            for ref in refs:
                ev = by_src.get(ref, {})
                st_cls, st_lab = _EV_STATUS.get(ev.get("status", "NOT_FOUND"), _EV_STATUS["NOT_FOUND"])
                items.append(
                    f'<p><span class="grade" style="color:var(--{st_cls})">{e(st_lab)}</span> — '
                    f'{_para(ev.get("label") or "Supporting artefact")}</p>'
                    f'<p>{_para(ev.get("summary"))}</p>'
                    f'<p class="src">{e(ref)}</p>')
            drill = ('<details><summary>Proof it works</summary>'
                     f'<div class="dbody">{"".join(items)}</div></details>')
        out.append(
            f'<div class="entry"><div class="gutter {cls}">'
            f'<div class="grade">{e(label)}</div>'
            f'<div class="gnote">{e(note)}</div>{origin}</div>'
            f'<div><h3>{e(r.get("title"))}</h3>'
            f'<p>{_para(r.get("summary"))}</p>'
            + (f'<div class="impact"><b>Why it matters to you</b>{_para(r.get("business_impact"))}</div>'
               if r.get("business_impact") else "")
            + (f'<p class="src opsonly">Status: {e(status)}</p>'
               if status == UNSUBSTANTIATED else "")
            + drill + '</div></div>')
    return "".join(out)


def _decisions(rows: List[dict]) -> str:
    if not rows:
        return '<p class="slede">Nothing currently requires a decision from you.</p>'
    out = []
    for d in rows:
        blocking = bool(d.get("blocking"))
        flag = ("Blocking — work behind this is paused" if blocking
                else "Not blocking — everything else continues")
        rec = (d.get("recommendation") or "").strip()
        opts = d.get("options") or []
        li = "".join(
            f'<li class="{"rec" if i == 0 else ""}"><span class="r"></span>'
            f'<span>{_para(o)}</span></li>' for i, o in enumerate(opts))
        out.append(
            f'<div class="decision {"blocking" if blocking else ""}">'
            f'<div class="dhead"><div class="dflag">{e(flag)}</div>'
            f'<h3>{e(d.get("question"))}</h3></div>'
            f'<p class="dctx">{_para(d.get("context"))}</p>'
            + (f'<div class="dctx" style="margin-top:1em"><b>Our recommendation.</b> '
               f'{_para(rec)}</div>' if rec else "")
            + (f'<ul class="opts">{li}</ul>' if li else "")
            + f'<div class="dfoot"><b>Effect on delivery</b>'
              f'{_para(d.get("delivery_impact"))}</div></div>')
    return "".join(out)


def _risks(rows: List[dict]) -> str:
    if not rows:
        return '<p class="slede">No delivery risks are currently open.</p>'
    out = []
    for r in rows:
        sev = (r.get("severity") or "MEDIUM").upper()
        out.append(
            f'<div class="risk"><div class="sev {_SEVERITY.get(sev, "sev-med")}">{e(sev)}'
            f'<div class="owner">Owned by {e(r.get("owner") or "ALDC")}</div>'
            + ('<span class="needsyou">Needs a decision from you</span>'
               if r.get("client_action_required") else "")
            + '</div><div>'
            f'<h3>{e(r.get("title"))}</h3>'
            f'<p>{_para(r.get("impact"))}</p>'
            + (f'<div class="impact"><b>What we are doing about it</b>'
               f'{_para(r.get("mitigation"))}</div>' if r.get("mitigation") else "")
            + '</div></div>')
    return "".join(out)


def _next(rows: List[dict]) -> str:
    if not rows:
        return '<p class="slede">No further outcomes are planned in this phase.</p>'
    out = []
    for n in rows:
        st = (n.get("status") or "NOT_STARTED").replace("_", " ")
        blocked = (n.get("status") == "BLOCKED")
        out.append(
            f'<li><div class="nstate {"blocked" if blocked else ""}">{e(st)}</div>'
            f'<div><div class="t">{e(n.get("title"))}</div>'
            f'<div class="d">{_para(n.get("blocked_reason") or ("After: " + n["dependency"] if n.get("dependency") else ""))}</div>'
            f'</div></li>')
    return f'<ul class="nextlist">{"".join(out)}</ul>'


def _stages(progress: Dict[str, Any]) -> str:
    ms = progress.get("milestones") or []
    if not ms:
        return ""
    cells = []
    for i, m in enumerate(ms, 1):
        st = (m.get("status") or "NOT_STARTED").upper()
        cls = "done" if st == "DONE" else ("blocked" if st == "BLOCKED" else "")
        now = " now" if st not in ("DONE",) and all(
            (x.get("status") or "").upper() == "DONE" for x in ms[:i - 1]) else ""
        cells.append(f'<div class="stage {cls}{now}"><div class="sn">{st.replace("_", " ")}</div>'
                     f'<div class="st">{e(m.get("title"))}</div></div>')
    return f'<div class="stages">{"".join(cells)}</div>'


# --------------------------------------------------------------------------------------------
# Page
# --------------------------------------------------------------------------------------------

def render_html(cr: ClientReview) -> str:
    """Render the client-safe payload. Never touches ``cr.diagnostics``."""
    d = cr.to_client_dict()
    proj, rev, intent = d["project"], d["review"], d["intent"]
    acc, prog = d["acceptance"], d["progress"]

    fresh_cls, fresh_lab = _FRESH.get(rev.get("freshness_state"), _FRESH[UNAVAILABLE])
    blocking_n = sum(1 for x in d["decisions"] if x.get("blocking")
                     and (x.get("status") or "OPEN").upper() == "OPEN")
    open_n = len(d["decisions"])
    grounded_n = sum(1 for x in d["delivered"] if x.get("grounding") == GROUNDED)
    needs_you = blocking_n + sum(1 for r in d["risks"] if r.get("client_action_required"))

    pct = prog.get("completion_percent")
    pct_txt = f"{pct}%" if pct is not None else "Not measurable"
    pct_note = ("Derived from completed workstreams" if prog.get("completion_basis") == "DERIVED"
                else "No measurable basis available")

    hero_line = (f"{grounded_n} outcome{'s' if grounded_n != 1 else ''} delivered with evidence"
                 if grounded_n else "No evidence-backed outcomes yet")
    hero_sub = (f"{needs_you} thing{'s' if needs_you != 1 else ''} need"
                f"{'' if needs_you != 1 else 's'} your input" if needs_you
                else "Nothing currently needs your input")

    unmet = acc.get("unmet") or []
    unmet_html = "".join(f"<li>{e(u)}</li>" for u in unmet)

    ev_rows = []
    for ev in d["evidence"]:
        st_cls, st_lab = _EV_STATUS.get(ev.get("status", "NOT_FOUND"), _EV_STATUS["NOT_FOUND"])
        ev_rows.append(
            f'<div class="entry"><div class="gutter {st_cls}">'
            f'<div class="grade">{e(st_lab)}</div>'
            f'<div class="gnote">{e(ev.get("basis", "").title())} evidence'
            + (f', {e(ev.get("evidence_class", "").lower())} class' if ev.get("evidence_class") else "")
            + f'</div></div><div><h3>{e(ev.get("label"))}</h3>'
              f'<p>{_para(ev.get("summary"))}</p>'
              f'<p class="src">{e(ev.get("source"))}'
            + (f' · verified {e(ev.get("verified_at"))}' if ev.get("verified_at") else "")
            + '</p></div></div>')

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(proj.get('name', 'Client Review'))}</title>
<!-- No external resources. Everything this page needs is in the file. -->
<style>{_CSS}</style>
</head>
<body>

<header class="mast">
  <div class="wrap">
    <div class="eyebrow">Client delivery review · {e(proj.get('client'))}</div>
    <h1>{e(proj.get('name'))}</h1>
    <p class="subject">{e(proj.get('subject'))}</p>
    <div class="tiles">
      <div class="tile"><div class="k">Overall status</div>
        <div class="v">{e(rev.get('status'))}</div>
        <div class="n">{pct_txt} of this phase complete · {e(pct_note)}</div></div>
      <div class="tile"><div class="k">Review readiness</div>
        <div class="v">{e((acc.get('status') or '').replace('_', ' ').title())}</div>
        <div class="n">{len(unmet)} item{'s' if len(unmet) != 1 else ''} outstanding</div></div>
      <div class="tile"><div class="k">Needs your input</div>
        <div class="v">{needs_you}</div>
        <div class="n">{blocking_n} blocking · {open_n - blocking_n} non-blocking</div></div>
      <div class="tile"><div class="k">State of this page</div>
        <div class="v" style="font-size:1rem;margin-top:8px">
          <span class="stamp {fresh_cls}">{e(fresh_lab)}</span></div>
        <div class="n">{e(rev.get('last_verified_at') or 'no verification recorded')}</div></div>
    </div>
  </div>
</header>

<nav class="rail"><div class="wrap">
  <a href="#asked">What you asked for</a>
  <a href="#delivered">Delivered</a>
  <a href="#evidence">Evidence</a>
  <a href="#decisions">Decisions</a>
  <a href="#risks">Risks</a>
  <a href="#next">What's next</a>
  <a href="#acceptance">Acceptance</a>
  <button class="modebtn" id="modebtn" type="button">Live meeting mode</button>
</div></nav>

<div class="wrap">

<section id="summary">
  {_shead('00', 'Where this stands')}
  <p class="objective">{e(hero_line)}. {e(hero_sub)}.</p>
  <p class="slede">{e(rev.get('last_review_at') and 'Changes shown are since your last review.'
                     or 'This is the first review of this project, so everything below is new.')}</p>
  {_stages(prog)}
</section>

<section id="asked">
  {_shead('01', 'What you asked for',
          'Our current understanding of the outcome you asked us to deliver. If any of this is '
          'wrong, it is the most valuable thing you can correct today.')}
  <p class="objective">{_para(intent.get('objective'))}</p>
  <div class="two" style="margin-top:26px">
    {_list_pane('Acceptance criteria', intent.get('acceptance_criteria') or [])}
    {_list_pane('Requirements', intent.get('requirements') or [])}
    {_list_pane('Assumptions we are working under', intent.get('assumptions') or [])}
    {_list_pane('Explicitly out of scope', intent.get('exclusions') or [])}
  </div>
  <div class="two" style="margin-top:1px">
    {_list_pane('Still unresolved', intent.get('unresolved_ambiguities') or [])}
  </div>
</section>

<section id="delivered">
  {_shead('02', 'What we delivered',
          'Outcomes, not tasks. The grade in the left margin says whether the claim is backed by '
          'an artefact we can show you, or is only our assertion.')}
  {_delivered(d['delivered'], d['evidence'])}
</section>

<section id="evidence">
  {_shead('03', 'Proof it works',
          'A green status should never mean "trust us". Each artefact below is a file we can open '
          'in front of you, and each carries how it was established.')}
  {''.join(ev_rows) or '<p class="slede">No evidence artefacts are on file yet.</p>'}
</section>

<section id="decisions">
  {_shead('04', 'What we need from you',
          'Only decisions that genuinely need you. Anything that can safely continue without an '
          'answer is continuing.')}
  {_decisions(d['decisions'])}
</section>

<section id="risks">
  {_shead('05', 'Risks and blockers',
          'Surfaced rather than left buried in an engineering tool. Where we own it, we say so.')}
  {_risks(d['risks'])}
</section>

<section id="next">
  {_shead('06', "What happens next", 'The next outcomes, not the next internal tasks.')}
  {_next(d['next'])}
</section>

<section id="acceptance">
  {_shead('07', 'Review and acceptance')}
  <div class="accept">
    <div class="st">{e((acc.get('status') or '').replace('_', ' ').title())}</div>
    <p style="max-width:var(--measure);color:var(--ink2)">{_para(acc.get('notes'))}</p>
    {'<div class="why">Not yet ready for acceptance because</div><ul>' + unmet_html + '</ul>'
     if unmet else '<div class="why">All acceptance conditions are met</div>'}
  </div>
</section>

<footer>
  <span>Page generated {e(rev.get('last_updated'))}</span>
  <span>Delivery state last verified {e(rev.get('last_verified_at') or 'never')}</span>
  <span>Freshness: {e(fresh_lab)}</span>
  <span class="opsonly">Basis: {e(rev.get('basis'))}</span>
</footer>

</div>
<script>{_JS}</script>
</body>
</html>
"""
