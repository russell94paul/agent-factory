"""The P1 control surface — NOW first, everything else one tap away.

⭐ **This is a re-ordering, not a replacement.** Every P0 panel still exists and still renders from
`factory.switchboard_render`; what changed is that none of them is *first*. The measured P0
problem was not that a panel was wrong, it was that the page opened on a full DAG, 89 work rows,
every worktree and the raw upstream feed — a database dump that an operator on a phone reads none
of. P1 answers three questions above the fold and defers the rest:

    1. WHAT NEEDS ME?      NEEDS YOU
    2. WHAT SHOULD HAPPEN NEXT?  NEXT
    3. WHAT IS HAPPENING NOW?    RUNNING  (then RECENT, for what just changed)

## Layout

Desktop is a three-column shell — nav rail, action column, inspector — and the inspector is where
detail goes so the centre column can stay a list of decisions. Phone is a **different layout, not
a squeezed one**: one column, a bottom nav, and the inspector becomes a full-width detail panel
reached by a link rather than a side panel nobody can see. Both are CSS-grid over the same markup,
so there is one DOM and no duplicated content to drift.

## ⛔ Rules this file follows

- **No panel is invented to fill space.** An empty NEXT renders the reason it is empty.
- **The primary action is derived from state, and there is exactly one.** `work.PRIMARY_ACTION`.
- **Visibility renders on every work card**, from `Work.visibility`, and it defaults closed. A
  card that omitted it would let PRIVATE work read as unmarked, which is how a private id ends up
  in a screenshot nobody audited.
- **No private evidence in the payload.** Cards carry ids, titles, states and check *names* —
  never evidence bodies. The Inspector shows evidence *references*, which are paths, because a
  path is what an operator needs to go and read the thing under their own authority.
- **Refresh and Restart say what they actually do.** See `_topbar`.
"""
from __future__ import annotations

import html
from typing import List, Optional

from . import switchboard as _sb
from . import work as _work

# --------------------------------------------------------------------------- vocabulary

#: work state -> (glyph, colour var). The glyph carries the state without colour, so the page
#: survives a greyscale screenshot and a colour-blind reader.
STATE_MARK = {
    _work.READY:        ("○", "var(--accent)"),
    _work.RUNNING:      ("●", "var(--accent)"),
    _work.NEEDS_HUMAN:  ("!",      "var(--fail)"),
    _work.BLOCKED:      ("×", "var(--ink3)"),
    _work.WAITING_GATE: ("◓", "var(--unmeas)"),
    _work.DRAFT:        ("◌", "var(--unmeas)"),
    _work.DONE:         ("✓", "var(--pass)"),
    _work.ABANDONED:    ("–", "var(--ink3)"),
}

#: check verdict -> (glyph, colour). UNMEASURED is NOT a tick and NOT a cross: it is its own mark,
#: because rendering it as either would make a gap look like a measurement.
CHECK_MARK = {
    _work.PASS:           ("✓", "var(--pass)"),
    _work.FAIL:           ("×", "var(--fail)"),
    _work.UNMEASURED:     ("?",      "var(--unmeas)"),
    _work.NOT_APPLICABLE: ("–", "var(--ink3)"),
}

#: The secondary nav. `NOW` is the default and the only one that is not a drill-down.
VIEWS = [("now", "NOW"), ("work", "WORK"), ("sessions", "SESSIONS"),
         ("inbox", "INBOX"), ("mission", "MISSION"), ("more", "MORE")]

#: Views reachable only from MORE. Kept off the bottom nav so the phone's four slots stay for the
#: things an operator taps, not the things they occasionally inspect.
MORE_VIEWS = [("activity", "Activity"), ("evidence", "Evidence"), ("worktrees", "Worktrees"),
              ("diagnostics", "Diagnostics"), ("health", "System health")]

CSS = """
.p1{--gut:14px;font:13px/1.5 ui-monospace,"Cascadia Code",Consolas,monospace;
 padding-bottom:64px}
.p1 *{box-sizing:border-box;min-width:0}
.p1 .shell{display:grid;grid-template-columns:1fr;gap:var(--gut)}
.p1 .rail{display:none}
.p1 .insp{display:none}
.p1.has-insp .insp{display:block}

/* ---- top bar ------------------------------------------------------------- */
.p1 .top{display:flex;align-items:center;gap:8px;flex-wrap:wrap;
 border-bottom:2px solid var(--ink);padding:0 0 10px;margin:0 0 12px}
.p1 .brand{font:700 13px/1 ui-monospace,monospace;letter-spacing:.14em;white-space:nowrap}
.p1 .top form.cmd{flex:1 1 160px;display:flex;gap:6px;min-width:0}
.p1 .top input[type=search]{flex:1;min-width:0;background:var(--paper);color:var(--ink);
 border:1px solid var(--rule);padding:6px 9px;font:12px ui-monospace,monospace;border-radius:5px}
.p1 .top .acts{display:flex;gap:6px;flex-wrap:wrap;align-items:center}

/* ---- buttons ------------------------------------------------------------- */
.p1 .btn{display:inline-block;padding:6px 11px;border:1px solid var(--rule);background:var(--paper);
 color:var(--ink);text-decoration:none;font:600 11.5px/1.35 ui-monospace,monospace;
 letter-spacing:.07em;border-radius:5px;cursor:pointer;white-space:nowrap}
.p1 .btn:hover,.p1 .btn:focus-visible{border-color:var(--accent);color:var(--accent);outline:none}
.p1 .btn.pri{border-color:var(--accent);color:var(--accent);border-width:2px;padding:5px 10px}
.p1 .btn.pri:hover{background:var(--accent);color:var(--bg)}
/* ⛔ A full-width button must WRAP. `.btn` sets white-space:nowrap so inline tags and
   badges never break mid-label; inherited by `.wide` it made the P0 disclosure summary
   524px wide inside a 344px column, which pushed documentElement.scrollWidth to 547 and
   gave the whole page a horizontal scroll at both phone widths. Invisible in a
   screenshot -- the button looked fine, the BODY scrolled sideways. Measured by
   scripts/render_check_switchboard_p1.py. */
.p1 .btn.wide{display:block;width:100%;text-align:center;padding:11px;
 white-space:normal;overflow-wrap:anywhere}
.p1 .btn[aria-disabled=true]{opacity:.45;pointer-events:none}

/* ---- sections ------------------------------------------------------------ */
.p1 .sec{border:1px solid var(--rule);background:var(--raise);margin:0 0 var(--gut);
 border-radius:7px;overflow:hidden}
.p1 .sec>h2{display:flex;align-items:baseline;gap:9px;flex-wrap:wrap;margin:0;
 font:600 11px/1 ui-monospace,monospace;letter-spacing:.15em;text-transform:uppercase;
 color:var(--ink3);padding:10px 13px;border-bottom:1px solid var(--rule)}
.p1 .sec>h2 .n{font-size:11px;color:var(--ink)}
.p1 .sec>h2 .hint{font-weight:400;letter-spacing:0;text-transform:none;color:var(--ink3);
 font-size:11px}
.p1 .sec.alarm{border-color:var(--fail)}
.p1 .sec.alarm>h2{color:var(--fail)}
.p1 .bd{padding:12px 13px}
.p1 .bd>*:first-child{margin-top:0}
.p1 .bd>*:last-child{margin-bottom:0}

/* ---- work card ----------------------------------------------------------- */
.p1 .card{border:1px solid var(--rule);background:var(--paper);border-radius:6px;
 padding:11px 12px;margin:0 0 9px;display:block;color:inherit;text-decoration:none}
.p1 .card:last-child{margin-bottom:0}
.p1 .card.sel{border-color:var(--accent);border-width:2px;padding:10px 11px}
.p1 .card .cid{font:700 12.5px/1.3 ui-monospace,monospace;word-break:break-all;
 display:block;margin:0 0 6px}
.p1 .card .meta{display:flex;gap:7px;flex-wrap:wrap;align-items:center;margin:0 0 7px}
.p1 .card .ttl{color:var(--ink3);font-size:12px;margin:0 0 8px;
 overflow-wrap:anywhere}
.p1 .card .checks{display:flex;gap:10px;flex-wrap:wrap;font-size:11px;color:var(--ink3);
 margin:0 0 9px}
.p1 .card .checks b{font-weight:600;color:var(--ink)}
.p1 .tag{font-size:10px;letter-spacing:.09em;border:1px solid currentColor;padding:1px 6px;
 border-radius:3px;white-space:nowrap;font-weight:600}
.p1 .vis{font-size:10.5px;letter-spacing:.06em;color:var(--ink3);white-space:nowrap}
.p1 .dim{color:var(--ink3)}
.p1 .bad{color:var(--fail)}
.p1 .ok{color:var(--pass)}
.p1 .warn{color:var(--unmeas)}
.p1 .empty{color:var(--ink3);font-size:12px;margin:0}

/* ---- inspector ----------------------------------------------------------- */
.p1 .insp .sec{margin-bottom:var(--gut)}
.p1 .isec{border-top:1px dotted var(--rule);padding:10px 0 0;margin:10px 0 0}
.p1 .isec:first-child{border-top:0;padding-top:0;margin-top:0}
.p1 .isec h3{font:600 10.5px/1 ui-monospace,monospace;letter-spacing:.14em;color:var(--ink3);
 margin:0 0 7px;text-transform:uppercase}
.p1 .kv{display:grid;grid-template-columns:minmax(72px,auto) 1fr;gap:3px 10px;font-size:12px}
.p1 .kv dt{color:var(--ink3)}
.p1 .kv dd{margin:0;overflow-wrap:anywhere}
.p1 code{font-size:11.5px;overflow-wrap:anywhere}

/* ---- lists --------------------------------------------------------------- */
.p1 ul.plain{list-style:none;margin:0;padding:0}
.p1 ul.plain li{padding:6px 0;border-bottom:1px dotted var(--rule);font-size:12px}
.p1 ul.plain li:last-child{border-bottom:0}
.p1 .rec{display:grid;grid-template-columns:1fr auto;gap:4px 10px;align-items:baseline}
.p1 .rec .when{color:var(--ink3);font-size:11px;white-space:nowrap}

/* ---- forms --------------------------------------------------------------- */
.p1 .field{margin:0 0 11px}
.p1 .field label{display:block;font-size:11px;letter-spacing:.08em;color:var(--ink3);
 margin:0 0 4px;text-transform:uppercase}
.p1 input[type=text],.p1 textarea,.p1 select{width:100%;background:var(--paper);color:var(--ink);
 border:1px solid var(--rule);padding:9px 10px;font:13px ui-monospace,monospace;border-radius:5px}
.p1 textarea{min-height:64px;resize:vertical}
.p1 details.adv{margin:10px 0 0;border-top:1px dotted var(--rule);padding-top:9px}
.p1 details.adv summary{cursor:pointer;color:var(--ink3);font-size:11.5px;letter-spacing:.06em}
.p1 details.adv[open] summary{margin-bottom:10px}

/* ---- bottom nav (phone) --------------------------------------------------- */
.p1 .bnav{position:fixed;left:0;right:0;bottom:0;z-index:40;display:grid;
 grid-template-columns:repeat(5,1fr);background:var(--raise);
 border-top:1px solid var(--rule);padding-bottom:env(safe-area-inset-bottom,0)}
.p1 .bnav a{padding:11px 2px;text-align:center;text-decoration:none;color:var(--ink3);
 font:600 9.5px/1.2 ui-monospace,monospace;letter-spacing:.06em}
.p1 .bnav a.on{color:var(--accent);box-shadow:inset 0 2px 0 var(--accent)}
.p1 .bnav a .g{display:block;font-size:14px;line-height:1.1;margin-bottom:2px}
.p1 .bnav a .b{display:inline-block;min-width:15px;background:var(--fail);color:var(--bg);
 border-radius:8px;font-size:9px;padding:0 4px;margin-left:2px}

/* ---- flash --------------------------------------------------------------- */
.p1 .flash{border:1px solid var(--rule);border-left-width:4px;border-radius:5px;padding:9px 12px;
 margin:0 0 var(--gut);font-size:12px}
.p1 .flash.good{border-left-color:var(--pass)}
.p1 .flash.bad{border-left-color:var(--fail)}

/* ---- restart banner ------------------------------------------------------- */
.p1 #rst{display:none;margin:0 0 var(--gut)}
.p1 #rst.on{display:block}

/* ---- the retained P0 block --------------------------------------------------
   ⛔ A COLLAPSED <details> still contributes to documentElement.scrollWidth in Chromium, so the
   P0 panels blew the page 157px wide at 390px and 117px at 430px while being invisible. Measured
   by scripts/render_check_switchboard_p1.py, not by looking at it -- a screenshot of the closed
   page looks completely correct, and the overflow only shows as a body that scrolls sideways.
   The single culprit was one unbreakable Windows path in a session topic.

   Wide content scrolls inside its OWN container; the page body never scrolls horizontally. */
.p1 details.p0{margin:0 0 var(--gut);max-width:100%}
.p1 details.p0>summary{list-style:none;cursor:pointer}
.p1 details.p0>summary::-webkit-details-marker{display:none}
.p1 details.p0 .sw{max-width:100%;overflow-x:auto}
.p1 details.p0 .sw .row,.p1 details.p0 .sw li,.p1 details.p0 .sw td{
 overflow-wrap:anywhere;word-break:break-word}

/* Any long unbreakable token -- a Windows path, a URL, a 64-char id -- wraps rather than widening
   the page. Applied to the text carriers rather than to `*`, so `white-space:nowrap` on tags,
   badges and the nav is not fought. */
.p1 b,.p1 code,.p1 dd,.p1 li,.p1 p,.p1 summary,.p1 .ttl,.p1 .empty{overflow-wrap:anywhere}
.p1 pre{max-width:100%;overflow-x:auto}

/* ---- motion: only where it encodes a transition -------------------------- */
@keyframes p1pulse{0%,100%{opacity:1}50%{opacity:.42}}
.p1 .live{animation:p1pulse 2.4s ease-in-out infinite}
@media (prefers-reduced-motion:reduce){
  .p1 .live{animation:none}
  .p1 *{transition:none!important}
}

/* ---- desktop ------------------------------------------------------------- */
@media (min-width:900px){
  .p1{padding-bottom:0}
  .p1 .shell{grid-template-columns:minmax(140px,168px) minmax(0,1fr);align-items:start}
  .p1.has-insp .shell{grid-template-columns:minmax(140px,168px) minmax(0,1fr) minmax(280px,340px)}
  .p1 .rail{display:block;position:sticky;top:12px}
  .p1 .rail a{display:block;padding:8px 11px;text-decoration:none;color:var(--ink3);
   font:600 11px/1.2 ui-monospace,monospace;letter-spacing:.12em;border-left:2px solid transparent}
  .p1 .rail a.on{color:var(--accent);border-left-color:var(--accent);background:var(--raise)}
  .p1 .rail a:hover{color:var(--ink)}
  .p1 .rail .grp{font-size:9.5px;color:var(--ink3);letter-spacing:.14em;padding:14px 11px 5px;
   opacity:.72}
  .p1 .insp{display:block;position:sticky;top:12px;max-height:calc(100vh - 24px);overflow:auto}
  .p1 .bnav{display:none}
}
"""


#: The last quick-dispatch preview, handed in by the caller each render. A dict rather than a
#: module global so `page()` sets it once and both disclosure sites read the same value -- two
#: call sites reading two different plans is a page disagreeing with itself.
_DISPATCH_HOLDER: dict = {}


def _e(t) -> str:
    return html.escape(str(t if t is not None else ""), quote=True)


def _sec(title: str, body: str, n: str = "", hint: str = "", alarm: bool = False,
         sid: str = "") -> str:
    head = f'{_e(title)}'
    if n:
        head += f' <span class="n">{_e(n)}</span>'
    if hint:
        head += f' <span class="hint">{_e(hint)}</span>'
    ida = f' id="{_e(sid)}"' if sid else ""
    return (f'<section class="sec{" alarm" if alarm else ""}"{ida}>'
            f'<h2>{head}</h2><div class="bd">{body}</div></section>')


def _url(view: str = "now", inspect: str = "") -> str:
    q = f"?view={view}" if view != "now" else "?view=now"
    if inspect:
        q += f"&inspect={_e(inspect)}"
    return "/switchboard" + q


# ------------------------------------------------------------------------- work card


def work_card(w: dict, selected: bool = False, view: str = "now",
              compact: bool = False) -> str:
    """One compact work card: id, state, visibility, objective, the checks, one action.

    ⭐ Only what the current decision needs. The full contract, evidence list, dependency detail
    and provenance are in the Inspector — a card carrying all of it is the P0 page again, one
    level down.
    """
    glyph, col = STATE_MARK.get(w["state"], ("◌", "var(--ink3)"))
    vg, vl = w.get("visibility_glyph", "\U0001F512"), w.get("visibility_label", "PRIVATE")
    o = [f'<div class="card{" sel" if selected else ""}">']
    o.append(f'<a class="cid" href="{_url(view, w["id"])}">{_e(w["id"])}</a>')
    o.append('<div class="meta">')
    o.append(f'<span class="tag" style="color:{col}">{glyph} {_e(w["state"])}</span>')
    o.append(f'<span class="vis">{vg} {_e(vl)}</span>')
    if w.get("repo"):
        o.append(f'<span class="vis">{_e(w["repo"])}</span>')
    o.append("</div>")
    sub = w.get("objective") or w.get("title") or ""
    if sub:
        o.append(f'<p class="ttl">{_e(sub[:150])}</p>')

    if not compact:
        o.append('<div class="checks">')
        for c in w.get("checks", []):
            if c["verdict"] == _work.NOT_APPLICABLE:
                continue
            g, cc = CHECK_MARK.get(c["verdict"], ("?", "var(--ink3)"))
            o.append(f'<span><b>{_e(c["name"])}</b> <span style="color:{cc}">{g}</span></span>')
        o.append("</div>")
        if w.get("blocked_reason"):
            o.append(f'<p class="ttl warn" style="margin-bottom:9px">'
                     f'{_e(w["blocked_reason"][:220])}</p>')

    o.append(_primary_action(w, view))
    o.append("</div>")
    return "".join(o)


def _primary_action(w: dict, view: str) -> str:
    """The ONE action this state supports. Everything else lives behind the card's own link.

    ⛔ START SYNCED is a POST form and only for READY work. Rendering it for anything else would
    put a control on screen whose only outcome is a refusal — which teaches the operator that the
    page's buttons are suggestions.
    """
    act = w.get("action") or "—"
    if w["state"] == _work.READY:
        return (f'<form method="POST" action="/switchboard/start" style="margin:0">'
                f'<input type="hidden" name="target" value="{_e(w["id"])}">'
                f'<button class="btn pri wide" name="go" value="1">START SYNCED</button></form>')
    if w["state"] == _work.RUNNING and w.get("session_id"):
        return (f'<a class="btn wide" href="{_url("sessions", w["id"])}">OPEN SESSION</a>')
    return f'<a class="btn wide" href="{_url(view, w["id"])}">{_e(act)}</a>'


# --------------------------------------------------------------------------- NOW


#: Priority band -> colour. The band is coarse ON PURPOSE (see `coordination.prioritise`): the
#: factors are measured, the weighting between them is not validated, and a decimal score would
#: present an unvalidated judgement as precision.
_BAND_COLOUR = {"HIGH PRIORITY": "var(--fail)", "MEDIUM": "var(--unmeas)", "LOW": "var(--ink3)"}


def _why(r: dict) -> str:
    """The priority band and the measured factors that produced it. Never a bare score."""
    band = r.get("priority")
    if not band:
        return ""
    col = _BAND_COLOUR.get(band, "var(--ink3)")
    why = " · ".join(_e(x) for x in (r.get("why") or []))
    return (f'<div style="margin:0 0 5px"><span class="tag" style="color:{col}">{_e(band)}</span>'
            f'<div class="empty" style="margin-top:4px">{why}</div></div>')


def _needs_you(st: dict, view: str) -> str:
    rows = (st.get("now") or {}).get("needs_you") or []
    if not rows:
        return ('<p class="empty">Nothing is waiting on you. No session has written a question '
                'and no work is in NEEDS_HUMAN.</p>')
    o = []
    for r in rows[:_sb.NOW_CAP]:
        if r["kind"] == "WORK" and r.get("work"):
            o.append(_why(r) + work_card(r["work"], view=view))
            continue
        q = (r.get("questions") or [{}])[0]
        live = r.get("live")
        badge = ('<span class="tag live" style="color:var(--fail)">! ACTIVE</span>' if live
                 else '<span class="tag" style="color:var(--ink3)">NO SESSION / STALE</span>')
        who = q.get("topic") or q.get("name") or q.get("session_id") or "unattributed"
        o.append(
            _why(r) +
            f'<div class="card"><div class="meta">{badge}'
            f'<span class="vis">{_e(str(q.get("state") or "state unknown"))}</span></div>'
            f'<p class="ttl" style="color:var(--ink)">{_e(str(q.get("needs") or q.get("detail") or "a question with no text"))[:260]}</p>'
            f'<p class="ttl">from {_e(str(who)[:90])} · joined to no canonical work, so it '
            f'is shown unattributed rather than filtered</p>'
            f'<a class="btn wide" href="{_url("inbox")}">RESPOND</a></div>')
    if len(rows) > _sb.NOW_CAP:
        o.append(f'<a class="btn wide" href="{_url("inbox")}">'
                 f'{len(rows) - _sb.NOW_CAP} more in INBOX</a>')
    return "".join(o)


def _next(st: dict, view: str) -> str:
    now = st.get("now") or {}
    rows = now.get("next") or []
    o = []
    if rows:
        o += [work_card(w, view=view) for w in rows[:_sb.NOW_CAP]]
    else:
        drafts, waiting = now.get("draft_count") or 0, len(now.get("waiting") or [])
        o.append('<p class="empty">Nothing is READY. '
                 + (f'{drafts} piece(s) of work are DRAFT — they have an unmeasured readiness '
                    f'check, most often no declared repository. ' if drafts else "")
                 + (f'{waiting} are waiting on a dependency. ' if waiting else "")
                 + 'READY is derived, never chosen, so this list is empty because the checks say '
                   'so.</p>')
    wait = now.get("waiting") or []
    if wait:
        o.append('<div style="margin-top:11px">')
        for w in wait[:3]:
            deps = ", ".join(w.get("depends_on") or [])
            o.append(f'<div class="card"><a class="cid" href="{_url(view, w["id"])}">'
                     f'{_e(w["id"])}</a><div class="meta">'
                     f'<span class="tag" style="color:var(--ink3)">× WAITING</span>'
                     f'<span class="vis">{_e(w.get("visibility_glyph",""))} '
                     f'{_e(w.get("visibility_label",""))}</span></div>'
                     f'<p class="ttl">Waiting on: {_e(deps or "an unnamed blocker")}</p></div>')
        o.append("</div>")
    return "".join(o)


def _running(st: dict, view: str) -> str:
    rows = (st.get("now") or {}).get("running") or []
    if not rows:
        live = [s for s in st.get("sessions") or [] if s.get("is_live")]
        return ('<p class="empty">No work is RUNNING. '
                + (f'{len(live)} live session(s) exist but none is associated with a piece of '
                   f'canonical work — see SESSIONS.' if live else
                   'No live sessions either.') + '</p>')
    return "".join(work_card(w, view=view) for w in rows[:_sb.NOW_CAP])


def _recent(st: dict) -> str:
    rows = st.get("recent") or []
    if not rows:
        return '<p class="empty">No work transitions recorded yet.</p>'
    o = ['<ul class="plain">']
    for r in rows:
        o.append(f'<li class="rec"><span>{_e(r["verb"])} · '
                 f'<code>{_e(r["work_id"])}</code> <span class="dim">'
                 f'{_e((r.get("title") or "")[:60])}</span></span>'
                 f'<span class="when">{_e(r.get("ago",""))}</span></li>')
    o.append("</ul>")
    return "".join(o)


def _repo_health(st: dict) -> str:
    h = st.get("repo_health") or {}
    if h.get("ok"):
        return ""
    if not h.get("total"):
        return ""
    return _sec("⚠ Repo health",
                f'<p class="ttl warn">{_e(h.get("headline",""))}</p>'
                f'<a class="btn" href="{_url("worktrees")}">INSPECT</a>',
                n=f'{len(h.get("dirty") or [])} dirty', alarm=True)


# ------------------------------------------------------------------------ CREATE WORK


def create_form(st: dict, repos: Optional[List[str]] = None) -> str:
    """The operator-facing create flow. Two required fields, everything else derived.

    ⭐ The operator does not name a manifest, a task id, a worktree, a bus reader, a session id or
    a context packet. Those are the `MANIFEST_CREATION_TOOL_MISSING` seam: every one of them was a
    thing a human had to construct in Python before work could exist. The id is derived from the
    title and is *shown* under Advanced so it stays predictable and overridable, not hidden.
    """
    ids = sorted(w["id"] for w in st.get("work") or [])
    o = ['<form method="POST" action="/switchboard/create">']
    o.append('<div class="field"><label for="cw-t">What needs doing?</label>'
             '<input type="text" id="cw-t" name="title" required maxlength="200" '
             'placeholder="Finish the client delivery" autocomplete="off"></div>')
    o.append('<div class="field"><label for="cw-o">Objective</label>'
             '<textarea id="cw-o" name="objective" maxlength="1200" '
             'placeholder="What done looks like."></textarea></div>')
    o.append('<div class="field"><label for="cw-r">Repository</label>'
             '<select id="cw-r" name="repo" required>')
    for r in (repos or ["agent-factory"]):
        o.append(f'<option value="{_e(r)}">{_e(r)}</option>')
    o.append('</select></div>')
    o.append('<div class="field"><label for="cw-v">Visibility</label>'
             '<select id="cw-v" name="visibility">')
    for v in (_work._tasks.PRIVATE, _work._tasks.REVIEW_REQUIRED, _work._tasks.PUBLIC):
        g, lbl = _work.VISIBILITY_MARK[v]
        o.append(f'<option value="{_e(v)}">{g} {_e(lbl)}</option>')
    o.append('</select></div>')

    o.append('<details class="adv"><summary>Advanced ▸</summary>')
    o.append('<div class="field"><label for="cw-id">Work id (derived from the title if blank)'
             '</label><input type="text" id="cw-id" name="work_id" maxlength="64" '
             'pattern="[A-Za-z0-9._-]{1,64}" placeholder="MARKETING-MODEL-FINALIZATION-01"></div>')
    o.append('<div class="field"><label for="cw-d">Depends on (existing work id)</label>'
             '<input type="text" id="cw-d" name="depends_on" list="p1-workids" '
             'maxlength="64" placeholder="none"></div>')
    o.append('<datalist id="p1-workids">'
             + "".join(f'<option value="{_e(i)}">' for i in ids[:400]) + '</datalist>')
    o.append('<div class="field"><label for="cw-c">Resource claim (declares a conflict domain)'
             '</label><input type="text" id="cw-c" name="resource_claim" maxlength="80" '
             'placeholder="none declared — reported conflict-free"></div>')
    o.append('<div class="field"><label for="cw-a">Access</label><select id="cw-a" name="access">'
             '<option value="WRITE">WRITE</option><option value="READ">READ</option>'
             '</select></div>')
    o.append('</details>')
    o.append('<button class="btn pri wide" name="go" value="1">CREATE WORK</button>')
    o.append('<p class="empty" style="margin-top:9px">Readiness is derived after creation. New '
             'work is DRAFT until every check can be measured — it is never created READY.</p>')
    o.append('</form>')
    return "".join(o)


# ------------------------------------------------------------------------- INSPECTOR


def _downstream(st: dict, wid: str) -> List[str]:
    from . import coordination as _coord
    try:
        return _coord.downstream_blocked(wid, st.get("work") or [])
    except Exception:                                              # noqa: BLE001
        return []


def inspector(st: dict, wid: str, view: str) -> str:
    """The universal Inspector. Detail lives here so the centre column stays a list of decisions.

    Sections are the same for every object kind so the shape is learnable; a kind that has nothing
    for a section renders the section saying so rather than dropping it, because an absent section
    and an unwired one look identical.
    """
    w = next((x for x in st.get("work") or [] if x["id"] == wid), None)
    if w is None:
        return _sec("Inspector", f'<p class="empty">No canonical work with id '
                                 f'<code>{_e(wid)}</code>. Nothing was opened.</p>')
    glyph, col = STATE_MARK.get(w["state"], ("◌", "var(--ink3)"))
    vg, vl = w.get("visibility_glyph", ""), w.get("visibility_label", "")
    o = []

    o.append('<div class="isec"><h3>Summary</h3>')
    o.append(f'<p style="margin:0 0 7px;font-weight:700;word-break:break-all">{_e(w["id"])}</p>')
    o.append(f'<div class="meta" style="display:flex;gap:7px;flex-wrap:wrap;margin:0 0 8px">'
             f'<span class="tag" style="color:{col}">{glyph} {_e(w["state"])}</span>'
             f'<span class="vis">{vg} {_e(vl)}</span></div>')
    o.append(f'<p class="ttl" style="color:var(--ink)">{_e(w.get("title",""))}</p>')
    if w.get("objective"):
        o.append(f'<p class="ttl">{_e(w["objective"])}</p>')
    o.append("</div>")

    o.append('<div class="isec"><h3>State</h3><dl class="kv">')
    o.append(f'<dt>store</dt><dd>{_e(w.get("status",""))}</dd>')
    o.append(f'<dt>action</dt><dd>{_e(w.get("action",""))}</dd>')
    o.append(f'<dt>repo</dt><dd>{_e(w.get("repo") or "— none declared")}</dd>')
    o.append(f'<dt>owner</dt><dd>{_e(w.get("owner") or "—")}</dd>')
    o.append(f'<dt>session</dt><dd>{_e(w.get("session_id") or "— not attached")}</dd>')
    o.append(f'<dt>mission</dt><dd>{_e(w.get("mission") or "— standalone")}</dd>')
    o.append("</dl></div>")

    o.append('<div class="isec"><h3>Readiness</h3><ul class="plain">')
    for c in w.get("checks", []):
        g, cc = CHECK_MARK.get(c["verdict"], ("?", "var(--ink3)"))
        o.append(f'<li><span style="color:{cc}">{g}</span> <b>{_e(c["name"])}</b> '
                 f'<span class="dim">{_e(c["verdict"])}</span><br>'
                 f'<span class="dim">{_e(c.get("detail",""))}</span></li>')
    o.append('</ul><p class="empty" style="margin-top:7px">READY requires every check to be an '
             'explicit PASS. UNMEASURED is not a pass.</p></div>')

    o.append('<div class="isec"><h3>Autonomy</h3><dl class="kv">')
    o.append(f'<dt>policy</dt><dd>{_e(w.get("autonomy", "MANUAL"))}</dd>')
    o.append(f'<dt>paused</dt><dd>{"YES — the operator stop outranks the policy" if w.get("autonomy_paused") else "no"}</dd>')
    o.append(f'<dt>last start</dt><dd>{_e(w.get("start_mode") or "— never started, or started before the mode was recorded")}</dd>')
    allowed = w.get("guarded_start_allowed")
    o.append(f'<dt>guarded</dt><dd>{"may start without a human" if allowed else "will NOT start without a human"}</dd>')
    o.append("</dl>")
    stops = w.get("guarded_stop_reasons") or []
    if stops:
        o.append('<ul class="plain">'
                 + "".join(f'<li class="dim">{_e(x)}</li>' for x in stops[:8]) + "</ul>")
    o.append('<p class="empty" style="margin-top:6px">GUARDED decides; it does not act. P1 ships '
             'no loop that starts work on a timer — starting is still a tap.</p>')
    o.append(f'<form method="POST" action="/switchboard/autonomy" style="margin-top:8px;'
             f'display:flex;gap:6px;flex-wrap:wrap">'
             f'<input type="hidden" name="work_id" value="{_e(w["id"])}">'
             f'<select name="to" aria-label="Autonomy policy">'
             + "".join(f'<option value="{a}"{" selected" if w.get("autonomy") == a else ""}>{a}'
                       f'</option>' for a in ("MANUAL", "GUARDED", "AUTO"))
             + '</select><button class="btn" name="go" value="set">SET</button>'
             f'<button class="btn" name="go" value="{"resume" if w.get("autonomy_paused") else "pause"}">'
             f'{"RESUME AUTONOMY" if w.get("autonomy_paused") else "PAUSE AUTONOMY"}</button>'
             f'</form>')
    o.append("</div>")

    o.append('<div class="isec"><h3>Coordination</h3><dl class="kv">')
    o.append(f'<dt>blocks</dt><dd>{len(_downstream(st, w["id"]))} downstream item(s)</dd>')
    o.append(f'<dt>handoffs</dt><dd>{"session attached" if w.get("session_id") else "none recorded"}</dd>')
    o.append(f'<dt>conflicts</dt><dd>{_e(", ".join(w.get("conflicts_with") or []) or "none declared")}</dd>')
    o.append("</dl></div>")

    o.append('<div class="isec"><h3>Dependencies</h3>')
    if w.get("depends_on") or w.get("depends_on_artifacts"):
        o.append('<ul class="plain">')
        for d in w.get("depends_on") or []:
            dr = next((x for x in st["work"] if x["id"] == d), None)
            stt = dr["state"] if dr else "NOT IN STORE"
            o.append(f'<li><code>{_e(d)}</code> — <b>{_e(stt)}</b></li>')
        for a in w.get("depends_on_artifacts") or []:
            o.append(f'<li>artefact <code>{_e(a.get("ref",""))}</code> '
                     f'<span class="dim">({_e(a.get("kind","artifact"))}, satisfied when '
                     f'{_e(a.get("satisfied_when","EXISTS"))})</span></li>')
        o.append("</ul>")
    else:
        o.append('<p class="empty">None declared.</p>')
    o.append("</div>")

    o.append('<div class="isec"><h3>Evidence</h3>')
    refs = w.get("evidence_refs") or []
    if refs:
        o.append('<ul class="plain">'
                 + "".join(f'<li><code>{_e(r)}</code></li>' for r in refs[:20]) + "</ul>")
        o.append('<p class="empty" style="margin-top:6px">References only. The artefacts are read '
                 'from disk under your own authority — this page never inlines their content.</p>')
    else:
        o.append(f'<p class="empty">{w.get("evidence", 0)} row(s), no references.</p>')
    o.append("</div>")

    o.append('<div class="isec"><h3>Provenance</h3><dl class="kv">')
    o.append(f'<dt>source</dt><dd>{"mission manifest overlay" if w.get("from_manifest") else "canonical work in the task store"}</dd>')
    o.append(f'<dt>store</dt><dd><code>{_e(str(_work.store_path()))}</code></dd>')
    o.append(f'<dt>parent</dt><dd>{_e(w.get("parent") or "—")}</dd>')
    o.append("</dl></div>")

    if w.get("contract"):
        o.append('<details class="adv"><summary>Advanced ▸</summary><dl class="kv">')
        for k, v in sorted((w.get("contract") or {}).items()):
            o.append(f'<dt>{_e(k)}</dt><dd>{_e(v)}</dd>')
        o.append("</dl></details>")

    return _sec("Inspector", "".join(o), n=w["state"])


# ------------------------------------------------------------------------- top bar


#: ⭐ The two controls mean different things and the page says so in the controls themselves.
#:
#: `Refresh` re-requests the page. The server re-derives every figure on that request — nothing on
#: the Switchboard is cached — but the Python already loaded into the running process is the Python
#: that answers. Editing `factory/work.py` and pressing Refresh gives you the OLD code with FRESH
#: data, and a control that called that a reload would be lying about which of the two moved.
#:
#: `Restart Switchboard` replaces the server process, so the next response comes from re-imported
#: source. It is a POST with a per-process token — never a GET, and never parameterised.
#: `Re-measure` is the THIRD thing, and it already existed: `/reload` calls
#: `local_tracker.hot_reload()`, which `importlib.reload`s all 38 `factory.*` modules and re-binds
#: the by-value imports. It genuinely re-serves edited domain code. It cannot reload
#: `scripts/local_tracker.py` itself — a module cannot reload the code running inside it — which is
#: exactly the gap `Restart Switchboard` fills. Three controls, three true statements.
REFRESH_MEANS = "re-requests this page: the server re-measures, the loaded Python is unchanged"
REMEASURE_MEANS = "re-imports the factory modules (not local_tracker.py itself), then re-measures"
RESTART_MEANS = "replaces the whole server process, so every edited file is re-imported"


def _topbar(st: dict, view: str, token: str = "") -> str:
    now = st.get("now") or {}
    n = now.get("needs_you_count") or 0
    o = ['<div class="top">']
    o.append('<span class="brand">AGENT FACTORY</span>')
    o.append('<form class="cmd" method="GET" action="/switchboard" role="search">'
             '<input type="hidden" name="view" value="work">'
             '<input type="search" name="q" id="p1-cmd" placeholder="Search / command…" '
             'aria-label="Search work or run a command" autocomplete="off" list="p1-cmds">'
             '<button class="btn" type="submit">GO</button></form>')
    o.append('<div class="acts">')
    o.append(f'<a class="btn" href="{_url(view)}" title="{_e(REFRESH_MEANS)}" '
             f'data-p1="refresh" rel="nofollow">↻ Refresh</a>')
    o.append(f'<a class="btn pri" href="{_url("create")}">+ CREATE</a>')
    o.append('<details class="adv" style="margin:0;border:0;padding:0;position:relative">'
             '<summary class="btn" style="list-style:none">•••</summary>'
             '<div style="position:absolute;right:0;top:calc(100% + 5px);z-index:50;'
             'background:var(--raise);border:1px solid var(--rule);border-radius:6px;'
             'padding:8px;min-width:210px;display:grid;gap:6px">')
    if token:
        o.append('<form method="POST" action="/switchboard/restart" style="margin:0" '
                 'id="p1-restart-form">'
                 f'<input type="hidden" name="token" value="{_e(token)}">'
                 '<button class="btn wide" type="submit" id="p1-restart" '
                 f'title="{_e(RESTART_MEANS)}">Restart Switchboard</button></form>')
    else:
        o.append('<span class="empty">Restart is unavailable — this server was not started '
                 'under <code>scripts/switchboard_dev.py</code>, so nothing would bring it '
                 'back up.</span>')
    o.append(f'<a class="btn wide" href="/reload" title="{_e(REMEASURE_MEANS)}">Re-measure '
             f'(reload factory modules)</a>')
    o.append(f'<a class="btn wide" href="{_url("diagnostics")}">Diagnostics</a>')
    o.append('</div></details>')
    o.append('</div></div>')

    o.append('<datalist id="p1-cmds">'
             '<option value="ready">Work that is READY</option>'
             '<option value="running">Work that is RUNNING</option>'
             '<option value="needs">Work that needs a human</option>'
             '<option value="blocked">Work that is blocked</option>'
             '<option value="draft">Work that is DRAFT</option>'
             '</datalist>')
    if n:
        o.append(f'<div class="flash bad"><b>{n}</b> item(s) need you. '
                 f'<a href="{_url("inbox")}">Open the inbox →</a></div>')
    return "".join(o)


def _rail(view: str, st: dict) -> str:
    now = st.get("now") or {}
    o = ['<nav class="rail" aria-label="Sections">']
    for key, label in VIEWS:
        badge = ""
        if key == "now" and (now.get("needs_you_count") or 0):
            badge = f' ({now["needs_you_count"]})'
        o.append(f'<a href="{_url(key)}" class="{"on" if view == key else ""}">'
                 f'{_e(label)}{badge}</a>')
    o.append('<div class="grp">MORE</div>')
    for key, label in MORE_VIEWS:
        o.append(f'<a href="{_url(key)}" class="{"on" if view == key else ""}">{_e(label)}</a>')
    o.append("</nav>")
    return "".join(o)


#: Four tabs plus CREATE. Deliberately five slots and no more: a bottom nav that needs a scroll is
#: a menu, and the whole point of it is that every destination is one thumb-reach away.
BOTTOM = [("now", "NOW", "▣"), ("work", "WORK", "▤"), ("create", "CREATE", "＋"),
          ("sessions", "SESSIONS", "◉"), ("more", "MORE", "⋯")]


def _bottomnav(view: str, st: dict) -> str:
    n = (st.get("now") or {}).get("needs_you_count") or 0
    o = ['<nav class="bnav" aria-label="Primary">']
    for key, label, glyph in BOTTOM:
        on = "on" if view == key or (view in dict(MORE_VIEWS) and key == "more") else ""
        b = f'<span class="b">{n}</span>' if key == "now" and n else ""
        o.append(f'<a href="{_url(key)}" class="{on}"><span class="g">{glyph}</span>'
                 f'{_e(label)}{b}</a>')
    o.append("</nav>")
    return "".join(o)


# --------------------------------------------------------------------------- the views


def p0_block(st: dict, dispatch=None, expanded: bool = False) -> str:
    """Every P0 panel, in one disclosure. Present on NOW, expanded on MISSION.

    ⭐ **Retained, not removed — and deliberately not first.** The brief's instruction is that the
    full DAG, the whole worktree table, the raw upstream feed and the large START SYNCED
    configuration form must not *dominate* the default page. It does not say they should stop
    existing: START SYNCED with an explicit target, QUICK DISPATCH and the mission DAG are the
    working P0 primitives this mission was told not to replace unnecessarily.

    So they are exactly where progressive disclosure puts them: one tap down, fully functional,
    with every control still wired to the same route it was wired to in P0. The NOW page above
    answers the three questions; this answers everything else.
    """
    from . import switchboard_render as _p0
    body = _p0.page(st, dispatch=dispatch)
    return (f'<details class="p0"{" open" if expanded else ""}>'
            f'<summary class="btn wide" style="margin-bottom:10px">'
            f'{"▾" if expanded else "▸"} Mission DAG, START SYNCED form, quick dispatch, '
            f'upstream and worktrees</summary>{body}</details>')


def _view_now(st: dict, view: str) -> str:
    now = st.get("now") or {}
    o = [_repo_health(st)]
    o.append(_sec("Needs you", _needs_you(st, view), n=str(now.get("needs_you_count") or 0),
                  hint="live questions first; stale ones are marked, never hidden",
                  alarm=bool(now.get("needs_you_count")), sid="needs-you"))
    o.append(_sec("Next", _next(st, view), n=str(now.get("next_count") or 0),
                  hint="READY is derived from the checks, never chosen", sid="next"))
    o.append(_sec("Running", _running(st, view), n=str(now.get("running_count") or 0),
                  hint="work first; pid and session detail are in the Inspector", sid="running"))
    o.append(_sec("Recent", _recent(st), hint="work transitions, not raw bus traffic",
                  sid="recent"))
    o.append(p0_block(st, dispatch=_DISPATCH_HOLDER.get("plan")))
    return "".join(o)


def _view_work(st: dict, view: str, q: str = "") -> str:
    rows = st.get("work") or []
    ql = (q or "").strip().lower()
    alias = {"ready": _work.READY, "running": _work.RUNNING, "needs": _work.NEEDS_HUMAN,
             "blocked": _work.BLOCKED, "draft": _work.DRAFT, "done": _work.DONE,
             "gate": _work.WAITING_GATE}
    note = ""
    if ql in alias:
        rows = [w for w in rows if w["state"] == alias[ql]]
        note = f"filtered to {alias[ql]}"
    elif ql:
        rows = [w for w in rows
                if ql in w["id"].lower() or ql in (w.get("title") or "").lower()
                or ql in (w.get("objective") or "").lower()]
        note = f"matching {q!r}"
    body = ("".join(work_card(w, view=view, compact=True) for w in rows[:60])
            if rows else f'<p class="empty">No canonical work {note or "in the store"}.</p>')
    if len(rows) > 60:
        body += f'<p class="empty">{len(rows) - 60} more not shown — narrow the search.</p>'
    return _sec("Work", body, n=str(len(rows)),
                hint=note or "every piece of canonical work in the task store")


def _view_inbox(st: dict, view: str) -> str:
    rows = (st.get("now") or {}).get("needs_you") or []
    if not rows:
        return _sec("Inbox", '<p class="empty">Nothing is waiting on you.</p>', n="0")
    o = []
    for r in rows:
        if r["kind"] == "WORK" and r.get("work"):
            o.append(work_card(r["work"], view=view))
            continue
        q = (r.get("questions") or [{}])[0]
        live = r.get("live")
        o.append(
            f'<div class="card"><div class="meta">'
            + (f'<span class="tag live" style="color:var(--fail)">! ACTIVE</span>' if live
               else '<span class="tag" style="color:var(--ink3)">NO SESSION / STALE</span>')
            + f'<span class="vis">{_e(str(q.get("state") or ""))}</span></div>'
            f'<p class="ttl" style="color:var(--ink)">'
            f'{_e(str(q.get("needs") or q.get("detail") or ""))[:400]}</p>'
            f'<p class="ttl">from {_e(str(q.get("topic") or q.get("name") or "unattributed"))[:100]}'
            f'</p>'
            f'<p class="empty">What happens if you do not answer: the session stays blocked and '
            f'the work it was doing does not advance.</p></div>')
    return _sec("Inbox", "".join(o), n=str(len(rows)),
                hint="a question that joined to no work is shown unattributed, never filtered")


def _view_sessions(st: dict) -> str:
    cards = st.get("sessions") or []
    if not cards:
        return _sec("Sessions", '<p class="empty">No sessions in the registry.</p>', n="0")
    o = ['<ul class="plain">']
    for c in cards:
        cls = "bad" if not c.get("liveness_trusted") else ("ok" if c.get("is_live") else "dim")
        o.append(f'<li><b>{_e(str(c.get("topic") or c.get("name") or c.get("session_id",""))[:70])}'
                 f'</b><br><span class="{cls}">{_e(c.get("state",""))}</span> · '
                 f'<span class="dim">{_e(c.get("action",""))}</span><br>'
                 f'<code class="dim">{_e(str(c.get("session_id",""))[:12])}</code></li>')
    o.append("</ul>")
    return _sec("Sessions", "".join(o), n=str(len(cards)),
                hint="a live session is never offered RESUME — that spawns a second process")


def _view_more(st: dict) -> str:
    o = ['<ul class="plain">']
    for key, label in MORE_VIEWS:
        o.append(f'<li><a class="btn wide" href="{_url(key)}">{_e(label)}</a></li>')
    o.append("</ul>")
    return _sec("More", "".join(o), hint="everything the default page defers")


def _view_diagnostics(st: dict) -> str:
    o = []
    warn = st.get("warnings") or []
    o.append(_sec("Warnings", ('<ul class="plain">'
                               + "".join(f'<li class="warn">{_e(x)}</li>' for x in warn)
                               + "</ul>") if warn else
                  '<p class="empty">No warnings.</p>', n=str(len(warn))))
    sig = st.get("coordination") or []
    if sig:
        rows = ['<ul class="plain">']
        for g in sig:
            cls = "warn" if g["basis"] not in ("MEASURED", "DERIVED") else ""
            rows.append(f'<li class="rec"><span><b>{_e(g["name"])}</b><br>'
                        f'<span class="dim">{_e(g.get("limit",""))}</span></span>'
                        f'<span class="when {cls}">{_e(g["value"])} '
                        f'<span class="dim">[{_e(g["basis"])}]</span></span></li>')
        rows.append("</ul>")
        o.append(_sec("Coordination", "".join(rows), n=str(len(sig)),
                      hint="directly measured signals — deliberately NOT summed into one "
                           "percentage; the denominator for that is not yet defined"))
    o.append(_sec("Measurement", (
        f'<dl class="kv"><dt>measured</dt><dd>{_e(st.get("measured_at",""))}</dd>'
        f'<dt>work rows</dt><dd>{len(st.get("work") or [])}</dd>'
        f'<dt>sessions</dt><dd>{len(st.get("sessions") or [])}</dd>'
        f'<dt>store</dt><dd><code>{_e(str(_work.store_path()))}</code></dd></dl>'
        f'<p class="empty" style="margin-top:8px">Every figure above was derived on this request. '
        f'The one cached value in this page\'s dependency closure is the repository root, which '
        f'is a path that cannot change while the process lives.</p>')))
    return "".join(o)


def _view_worktrees(st: dict) -> str:
    wts = st.get("worktrees") or []
    if not wts:
        return _sec("Worktrees", '<p class="empty">git could not be asked, or none exist.</p>')
    o = ['<ul class="plain">']
    for w in wts:
        d = w.get("dirty")
        mark = ('<span class="warn">UNREADABLE — not a report of a clean tree</span>'
                if d is None else (f'<span class="bad">{d} uncommitted</span>' if d
                                   else '<span class="ok">clean</span>'))
        o.append(f'<li><b>{_e(w.get("branch") or "(detached)")}</b> '
                 f'<code class="dim">{_e(w.get("head",""))}</code><br>{mark}<br>'
                 f'<code class="dim">{_e(w["path"])}</code></li>')
    o.append("</ul>")
    return _sec("Worktrees", "".join(o), n=str(len(wts)))


def _view_evidence(st: dict) -> str:
    rows = [w for w in st.get("work") or [] if w.get("evidence_refs")]
    if not rows:
        return _sec("Evidence", '<p class="empty">No work carries evidence references.</p>')
    o = ['<ul class="plain">']
    for w in rows[:40]:
        o.append(f'<li><code>{_e(w["id"])}</code> — {len(w["evidence_refs"])} reference(s)'
                 f'<br><span class="dim">'
                 + ", ".join(f'<code>{_e(r)}</code>' for r in w["evidence_refs"][:4])
                 + "</span></li>")
    o.append("</ul>")
    return _sec("Evidence", "".join(o), n=str(len(rows)),
                hint="references only — this page never inlines evidence content")


# --------------------------------------------------------------------------- the page

#: Bounded restart poll. Every number is a decision:
#: - 400 ms between polls: fast enough that the phone feels reconnected, slow enough that a
#:   restarting server is not hit with a poll per frame.
#: - 40 attempts (~16 s): a local process re-imports in well under a second; anything past this is
#:   a failure to report, not a slower success to wait for.
#: - the poll compares the server's RUNTIME ID, not merely that a 200 came back. A 200 from the
#:   process that has not exited yet would otherwise read as "restarted" and reload the same code.
RESTART_JS = """
(function(){
 var f=document.getElementById('p1-restart-form');if(!f)return;
 var b=document.getElementById('p1-restart'),n=document.getElementById('rst');
 var was=document.body.getAttribute('data-runtime')||'';
 f.addEventListener('submit',function(ev){
  ev.preventDefault();
  if(b.getAttribute('aria-disabled')==='true')return;      /* repeated clicks cannot stack */
  b.setAttribute('aria-disabled','true');b.textContent='RESTARTING…';
  if(n){n.className='on';n.textContent='RESTARTING SWITCHBOARD…';}
  fetch(f.action,{method:'POST',body:new FormData(f),credentials:'same-origin'})
   .catch(function(){})                    /* the server dies mid-response; that is the success */
   .then(function(){setTimeout(poll,600);});
  var tries=0;
  function poll(){
   if(++tries>40){if(n)n.textContent='RESTART DID NOT COMPLETE — the server did not come back. '
     +'Check the supervisor terminal.';b.removeAttribute('aria-disabled');
     b.textContent='Restart Switchboard';return;}
   fetch('/healthz',{cache:'no-store'}).then(function(r){return r.json();}).then(function(j){
    if(j&&j.runtime&&j.runtime!==was){
     if(n)n.textContent='SWITCHBOARD UPDATED — reloading…';
     location.reload();
    }else{setTimeout(poll,400);}
   }).catch(function(){setTimeout(poll,400);});
  }
 });
})();
"""

#: Ctrl/Cmd+K focuses the command input. An accelerator only — the input is visible and tappable
#: on every viewport, so the page is fully operable with this script absent.
CMDK_JS = """
(function(){document.addEventListener('keydown',function(e){
 if((e.ctrlKey||e.metaKey)&&(e.key==='k'||e.key==='K')){
  var i=document.getElementById('p1-cmd');if(i){e.preventDefault();i.focus();i.select();}}});})();
"""


def page(st: Optional[dict] = None, view: str = "now", inspect: str = "", q: str = "",
         token: str = "", runtime: str = "", flash: Optional[tuple] = None,
         repos: Optional[List[str]] = None, dispatch=None) -> str:
    """The whole P1 Switchboard. One DOM; CSS decides whether it is a phone or a desk.

    `runtime` is the server's per-process id. It is stamped on `<body>` so the restart poll can
    tell a NEW process from the one it just asked to exit — a 200 from the dying process is not a
    restart, and treating it as one reloads the same code and reports success.
    """
    st = _sb.state() if st is None else st
    _DISPATCH_HOLDER["plan"] = dispatch
    view = view if view in dict(VIEWS) or view in dict(MORE_VIEWS) or view in ("create",) else "now"
    has_insp = bool(inspect)

    o = [f"<style>{CSS}</style>",
         f'<div class="p1{" has-insp" if has_insp else ""}" data-runtime="{_e(runtime)}">']
    o.append(_topbar(st, view, token))
    o.append('<div id="rst" class="flash bad" role="status" aria-live="polite"></div>')
    if flash:
        ok, msg = flash
        o.append(f'<div class="flash {"good" if ok else "bad"}">{_e(msg)}</div>')

    o.append('<div class="shell">')
    o.append(_rail(view, st))
    o.append('<main>')
    if view == "now":
        o.append(_view_now(st, view))
    elif view == "work":
        o.append(_view_work(st, view, q))
    elif view == "create":
        o.append(_sec("Create work", create_form(st, repos),
                      hint="the system derives the manifest, id, worktree, reader and packet"))
    elif view == "inbox":
        o.append(_view_inbox(st, view))
    elif view == "sessions":
        o.append(_view_sessions(st))
    elif view == "mission":
        o.append(p0_block(st, dispatch=_DISPATCH_HOLDER.get("plan"), expanded=True))
    elif view == "more":
        o.append(_view_more(st))
    elif view == "diagnostics":
        o.append(_view_diagnostics(st))
    elif view == "worktrees":
        o.append(_view_worktrees(st))
    elif view == "evidence":
        o.append(_view_evidence(st))
    elif view == "activity":
        o.append(_sec("Activity", _recent(st), hint="work transitions"))
        from . import switchboard_render as _p0
        o.append(_p0._sec("Upstream", _p0._upstream(st),
                          note="peer traffic — a nudge, not durable evidence"))
    elif view == "health":
        o.append(_view_diagnostics(st))
        o.append(_view_worktrees(st))
    o.append("</main>")
    if has_insp:
        o.append(f'<aside class="insp" aria-label="Inspector">{inspector(st, inspect, view)}</aside>')
    o.append("</div>")

    o.append(_bottomnav(view, st))
    o.append("</div>")
    o.append(f"<script>{RESTART_JS}{CMDK_JS}</script>")
    return "".join(o)
