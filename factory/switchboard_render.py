"""The Switchboard as one dense screen. Rendering only — every fact arrives from `switchboard.state`.

Split from the projection for the reason `client_review.py`/`client_review_render.py` and
`case_study.py`/`case_study_render.py` are split: the join is the part worth testing, and a test
that has to parse HTML to assert a dependency rule is testing the wrong thing.

Two rules this file follows and the page states about itself:

- **Nothing is invented to fill a panel.** An empty READY list renders as "nothing" with the reason,
  never as a suggestion. A panel that vanishes when empty cannot be told from one that is not wired
  up — the same rule the tracker's inbox panel already states.
- **Every number carries where it came from.** The critical path says it is dependency-ordered and
  not an ETA; peer traffic says it is a nudge and not evidence; a worktree whose dirty count could
  not be read says so rather than rendering clean.
"""
from __future__ import annotations

import html
from typing import Dict, List, Optional

from . import switchboard as _sb

#: state -> (glyph, css colour var). The glyph carries the state on its own, so the page survives
#: being read in a screenshot, over a shoulder, or by someone who cannot separate the colours.
GLYPH: Dict[str, tuple] = {
    _sb.DONE:              ("✓", "var(--pass)"),
    _sb.RUNNING:           ("●", "var(--accent)"),
    _sb.READY:             ("○", "var(--accent)"),
    _sb.READY_IN_PARALLEL: ("◇", "var(--unmeas)"),
    _sb.BLOCKED:           ("×", "var(--ink3)"),
    _sb.NEEDS_HUMAN:       ("!", "var(--fail)"),
    _sb.ABANDONED:         ("–", "var(--ink3)"),
}

CSS = """
.sw{font:13px/1.5 ui-monospace,"Cascadia Code",Consolas,monospace}
.sw section{border:1px solid var(--rule);background:var(--raise);margin:0 0 12px}
.sw section>h2{font:600 11px/1 ui-monospace,monospace;letter-spacing:.14em;text-transform:uppercase;
 color:var(--ink3);margin:0;padding:9px 13px;border-bottom:1px solid var(--rule)}
.sw .bd{padding:11px 13px}
.sw .row{display:grid;grid-template-columns:auto 1fr auto;gap:10px;align-items:baseline;
 padding:6px 0;border-bottom:1px dotted var(--rule)}
.sw .row:last-child{border-bottom:0}
.sw .dim{color:var(--ink3)}
.sw .warn{color:var(--unmeas)}
.sw .bad{color:var(--fail)}
.sw .ok{color:var(--pass)}
.sw .hdr{display:flex;justify-content:space-between;align-items:center;gap:14px;flex-wrap:wrap;
 border-bottom:2px solid var(--ink);padding:0 0 10px;margin:0 0 14px}
.sw .needs{font:700 13px/1 ui-monospace,monospace;letter-spacing:.1em;padding:7px 11px;
 border:2px solid currentColor}
.sw .wave{display:flex;flex-wrap:wrap;gap:6px;align-items:center;margin:0 0 8px}
.sw .node{border:1px solid var(--rule);background:var(--paper);padding:5px 9px;white-space:nowrap;
 text-decoration:none;display:inline-block}
.sw .node b{font-weight:700}
.sw .node.crit{border-color:currentColor;border-width:2px;padding:4px 8px}
.sw .arrow{color:var(--ink3)}
.sw a.btn{display:inline-block;padding:3px 9px;border:1px solid var(--rule);background:var(--paper);
 color:var(--ink);text-decoration:none;font-size:11.5px;letter-spacing:.06em}
.sw a.btn:hover,.sw a.btn:focus{border-color:var(--accent);color:var(--accent)}
.sw .tag{font-size:10px;letter-spacing:.1em;border:1px solid currentColor;padding:1px 5px;
 white-space:nowrap}
.sw details{margin:4px 0 0}
.sw summary{cursor:pointer;color:var(--ink3);font-size:11.5px}
.sw select,.sw textarea,.sw input[type=text]{background:var(--paper);color:var(--ink);
 border:1px solid var(--rule);padding:4px 6px;font:12px ui-monospace,monospace}
.sw label{font-size:11.5px;color:var(--ink3)}
.sw button.btn{background:var(--paper);color:var(--ink);border:1px solid var(--rule)}
.sw pre{margin:6px 0 0;padding:8px 10px;background:var(--paper);border:1px solid var(--rule);
 overflow-x:auto;font-size:11.5px;white-space:pre-wrap}
"""


def _e(t) -> str:
    return html.escape(str(t if t is not None else ""), quote=True)


def _sec(title: str, body: str, note: str = "") -> str:
    n = f'<span class="dim" style="font-weight:400;letter-spacing:0;text-transform:none">{note}</span>' if note else ""
    return f'<section><h2>{title} {n}</h2><div class="bd">{body}</div></section>'


# ------------------------------------------------------------------------- panels


def _dag(st: dict) -> str:
    by_label = {r["label"]: r for r in st["tasks"]}
    crit = set(st["critical_path"])
    if not st["waves"]:
        return '<p class="dim">No mission DAG — see WARNINGS below for why.</p>'

    out = []
    for i, wave in enumerate(st["waves"]):
        chips = []
        for lbl in wave:
            r = by_label.get(lbl, {})
            g, col = GLYPH.get(r.get("state", ""), ("?", "var(--ink3)"))
            cls = "node crit" if lbl in crit else "node"
            chips.append(
                f'<span class="{cls}" style="color:{col}" '
                f'title="{_e(r.get("title", ""))}">'
                f'<b>{_e(lbl)}</b> {g} '
                f'<span class="dim" style="font-size:10.5px">{_e(r.get("state", ""))}</span></span>')
        out.append('<div class="wave">' + '<span class="arrow">→</span>'.join(chips) + '</div>')
        if i < len(st["waves"]) - 1:
            out.append('<div class="arrow" style="margin:-4px 0 4px 6px">↓</div>')

    rows = []
    for r in st["tasks"]:
        g, col = GLYPH.get(r["state"], ("?", "var(--ink3)"))
        why = r.get("blocked_reason") or ""
        c = r.get("contract") or {}
        meta = " · ".join(x for x in [
            c.get("resource_claim", ""),
            c.get("access", ""),
            f'ev {r["evidence"]}',
            f'owner {r["owner"]}' if r.get("owner") else "",
        ] if x)
        rows.append(
            f'<div class="row"><span style="color:{col}"><b>{_e(r["label"])}</b> {g}</span>'
            f'<span>{_e(r["title"][:96])}'
            + (f'<br><span class="warn">{_e(why)}</span>' if why else "")
            + f'<br><span class="dim" style="font-size:11px">{_e(meta)}</span></span>'
            f'<span class="dim">{_e(r["state"])}</span></div>')
    out.append('<details><summary>every task, with its declared contract</summary>'
               + "".join(rows) + '</details>')
    return "".join(out)


def _parallel(st: dict) -> str:
    par, ready = st["ready_in_parallel"], st["ready"]
    if not par and not ready:
        running = ", ".join(st["running"]) or "nothing"
        return ('<p class="dim">Nothing in this mission is startable right now. '
                f'Running: <b>{_e(running)}</b>. Everything else is DONE or waits on it.<br>'
                '⚠ This panel only knows tasks in the mission manifest. Work outside the mission '
                '(this Switchboard branch included) has no task row and is not counted here — see '
                'WORKTREES.</p>')
    by = {r["label"]: r for r in st["tasks"]}
    out = []
    for lbl in ready + par:
        r = by[lbl]
        tag = "ON CRITICAL PATH" if lbl in ready else "PARALLEL-SAFE"
        col = "var(--accent)" if lbl in ready else "var(--unmeas)"
        c = r.get("contract") or {}
        out.append(
            f'<div class="row"><span class="tag" style="color:{col}">{tag}</span>'
            f'<span><b>{_e(lbl)}</b> {_e(r["title"][:90])}<br>'
            f'<span class="dim" style="font-size:11px">claims '
            f'{_e(c.get("resource_claim") or "NOTHING DECLARED")} '
            f'{_e(c.get("access") or "")}'
            + (f' · cannot run beside {_e(", ".join(r["conflicts_with"]))}'
               if r["conflicts_with"] else "")
            + '</span></span><span></span></div>')
    return "".join(out)


def _sessions(st: dict) -> str:
    if not st["sessions"]:
        return '<p class="dim">No sessions in the registry. ZERO, measured — not a missing panel.</p>'
    out = []
    for s in st["sessions"]:
        live = s["is_live"]
        col = ("var(--accent)" if s["state"] == "RUNNING-ATTACHED"
               else "var(--unmeas)" if live or not s["liveness_trusted"]
               else "var(--ink3)")
        act = _e(s["action"])
        # ⛔ A resume link exists ONLY for EXITED-RESUMABLE. Every other class renders the action
        # as text, so the page cannot offer a click that would spawn a duplicate.
        btn = (f'<a class="btn" href="/switchboard/resume/{_e(s["session_id"])}">RESUME</a>'
               if s["can_resume"] and s.get("session_id") else f'<span class="dim">{act}</span>')
        needs = s.get("needs") or ""
        out.append(
            f'<div class="row"><span class="tag" style="color:{col}">{_e(s["state"])}</span>'
            f'<span><b>{_e((s.get("topic") or s.get("name") or "(unnamed)")[:72])}</b><br>'
            f'<span class="dim" style="font-size:11px">'
            f'{_e(s.get("repo") or "?")} · {_e(s.get("where") or "?")}'
            f' · pid {_e(s.get("pid"))} · {_e(s.get("kind") or "?")}'
            f' · job {_e(s.get("job_state") or "—")}'
            f' · id {_e((s.get("session_id") or "")[:8])}</span>'
            + (f'<br><span class="bad">needs: {_e(needs[:110])}</span>' if needs else "")
            + f'</span>{btn}</div>')
    return "".join(out)


def _needs(st: dict) -> str:
    q = st["needs_you"]
    if not q:
        return ('<p class="ok">✓ Nothing waiting on you. Read from '
                '<code>~/.claude/jobs/*/state.json</code> on this refresh — ZERO is a measurement, '
                'and this panel renders at zero on purpose.</p>')
    out = []
    for r in q:
        where = " · ".join(x for x in [r.get("repo") or "", r.get("where") or "",
                                       r.get("mission_label") or ""] if x)
        st_ = r.get("state") or "?"
        # A question outlives its process. NO-SESSION is the normal, expected case for the oldest
        # ones — and the oldest are the ones a session-keyed inbox used to hide.
        how = ("open it" if st_ == "RUNNING-ATTACHED"
               else "resume it" if st_ == "EXITED-RESUMABLE"
               else "the session that asked is gone — answer it wherever the work now lives")
        out.append(
            f'<div class="row"><span class="tag bad">{_e(st_)}</span>'
            f'<span><b>{_e(str(r.get("needs"))[:200])}</b><br>'
            f'<span class="dim" style="font-size:11px">'
            f'{_e(where or "no repo/lane recorded")} · job {_e(r.get("job_id") or "?")}'
            f' · {how}</span>'
            + (f'<br><span class="dim" style="font-size:11px">suggested: '
               f'{_e(str(r.get("suggested_reply"))[:120])}</span>'
               if r.get("suggested_reply") else "")
            + '</span><span></span></div>')
    return "".join(out)


def _upstream(st: dict) -> str:
    """One channel, rendered once.

    ⛔ This rendered a full block per reader until 2026-09-01, when 16 readers with unread traffic
    made this panel 211,485 bytes on a page whose other seven panels totalled ~12 KB. The bus is
    one channel that several readers have not caught up on; the same message sixteen times is not
    sixteen messages.
    """
    u, dg = st["upstream"], st.get("upstream_digest") or {"events": [], "not_shown": 0}
    if not u:
        return ('<p class="dim">No unread peer traffic on <code>.data/bus/</code>. '
                'Cursors are per reader and are <b>not</b> advanced by opening this page.</p>')

    senders = sorted({e["from"] for e in dg["events"]})
    out = ['<div class="dim" style="font-size:11.5px;margin:0 0 6px">'
           'behind: ' + " · ".join(f'<b>{_e(r["reader"])}</b> {r["unread"]}' for r in u)
           + ' &nbsp;—&nbsp; peer traffic is a nudge, not durable evidence; the durable version of '
             'a correction is in <code>docs/findings.d/</code></div>',
           # ⛔ COLLAPSED BY DEFAULT. This is a command page the brief asks to keep to one screen,
           # and an unread backlog is the one panel that grows without bound — 21 events pushed
           # every other panel below the fold on 2026-09-01. The COUNT is always visible, because
           # that is the part that changes a decision; the text is one click away.
           f'<details><summary>{dg["total"]} unread event(s) from '
           f'{_e(", ".join(senders)) or "nobody"} — read them</summary>']
    for e in dg["events"]:
        clip = (f' <span class="dim">+{e["clipped"]} more chars — read it in the session, not here</span>'
                if e["clipped"] else "")
        refs = (f'<br><span class="dim" style="font-size:11px">refs: '
                f'{_e(", ".join(e["refs"]))}</span>' if e["refs"] else "")
        out.append(
            f'<div class="row"><span class="tag warn">{_e(e["kind"].upper())}</span>'
            f'<span><b>{_e(e["from"])}</b> '
            f'<span class="dim" style="font-size:11px">{_e(e["at"][:19])} · unread by '
            f'{len(e["unread_by"])}</span><br>{_e(e["text"])}{clip}{refs}</span>'
            '<span></span></div>')
    if dg["not_shown"]:
        out.append(f'<div class="row"><span class="tag dim">…</span><span class="dim">'
                   f'{dg["not_shown"]} older event(s) not shown — this is a nudge surface, not an '
                   f'archive</span><span></span></div>')
    out.append("</details>")
    return "".join(out)


def _worktrees(st: dict) -> str:
    if not st["worktrees"]:
        return '<p class="dim">git could not be asked about worktrees.</p>'
    out = []
    for w in st["worktrees"]:
        d = w.get("dirty")
        dirty = ("clean" if d == 0 else f"{d} uncommitted"
                 if isinstance(d, int) else "⚠ dirty state UNREADABLE")
        col = "var(--pass)" if d == 0 else "var(--unmeas)" if isinstance(d, int) else "var(--fail)"
        out.append(
            f'<div class="row"><span class="tag" style="color:{col}">'
            f'{"PRIMARY" if w.get("primary") else "WORKTREE"}</span>'
            f'<span><b>{_e(w.get("branch") or "?")}</b> '
            f'<span class="dim">@{_e(w.get("head") or "?")}</span><br>'
            f'<span class="dim" style="font-size:11px">{_e(w["path"])} · {dirty}</span></span>'
            f'<span class="dim">{dirty}</span></div>')
    return "".join(out)


def _warnings(st: dict) -> str:
    if not st["warnings"]:
        return '<p class="ok">✓ No warnings this measurement.</p>'
    return "".join(f'<div class="row"><span class="tag warn">⚠</span>'
                   f'<span>{_e(w)}</span><span></span></div>' for w in st["warnings"])


# ------------------------------------------------------- SLICE B: the START SYNCED control


def _opts(pairs, selected="") -> str:
    return "".join(f'<option value="{_e(v)}"{" selected" if v == selected else ""}>{_e(lab)}</option>'
                   for v, lab in pairs)


def _start_synced(st: dict) -> str:
    """The control that replaces: generate handoff, copy, find terminal, launch, paste.

    ⭐ **Everything the SECURITY section requires beside a dispatch is rendered here** — target,
    task/lane, worktree and the live state of what is running — because the failure that matters is
    not a malformed packet, it is a correct packet delivered to the wrong session.
    """
    by = {r["label"]: r for r in st["tasks"]}
    targets = [("", "— whole session (no single task) —")]
    for r in st["tasks"]:
        targets.append((r["label"], f'{r["label"]} · {r["state"]} · {r["title"][:52]}'))
    wts = [(w["path"], f'{w.get("branch") or "?"} @ {w.get("head") or "?"} — {w["path"]}')
           for w in st["worktrees"]]
    readers = [("", "— deliver no bus traffic —")]
    for u in st["upstream"]:
        readers.append((u["reader"], f'{u["reader"]} ({u["unread"]} unread)'))
    for r in _sb.bus_readers():
        if r not in [x[0] for x in readers]:
            readers.append((r, f"{r} (nothing unread)"))

    running = ", ".join(st["running"]) or "nothing"
    body = [
        '<form method="POST" action="/switchboard/start">',
        '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:10px">',
        f'<label>target task<br><select name="target" style="width:100%">{_opts(targets)}</select></label>',
        f'<label>worktree<br><select name="worktree" style="width:100%">{_opts(wts)}</select></label>',
        f'<label>deliver bus traffic for<br><select name="reader" style="width:100%">{_opts(readers)}</select></label>',
        '</div>',
        '<label style="display:block;margin:9px 0 0">note for the next session (the only part no '
        'instrument can see)<br>'
        '<textarea name="note" rows="3" style="width:100%;font:12px ui-monospace,monospace"></textarea></label>',
        '<label style="display:block;margin:7px 0 0;font-size:11.5px" class="dim">'
        '<input type="checkbox" name="gate" value="1"> also run the full gate handoff '
        '<b>(slow — this is the <code>readiness.measure()</code> path, timed at 413.8 s for '
        '<code>board.board()</code> and 801.0 s for <code>session.brief()</code> on 2026-09-01)</b>'
        '</label>',
        '<div style="margin:10px 0 0;display:flex;gap:8px;align-items:center;flex-wrap:wrap">',
        '<button name="dry" value="1" class="btn" style="cursor:pointer">PACKET ONLY (dry)</button>',
        '<button name="dry" value="" class="btn" style="cursor:pointer;border-color:var(--accent);'
        'color:var(--accent);font-weight:700">START SYNCED</button>',
        f'<span class="dim" style="font-size:11.5px">running now: <b>{_e(running)}</b> · '
        f'{len(st["sessions"])} session(s) in the registry · '
        f'{st["needs_you_count"]} question(s) waiting</span>',
        '</div>',
        '<p class="dim" style="font-size:11.5px;margin:9px 0 0">The packet carries measured '
        'identity, worktree, branch, HEAD, dependency state, live conflicts, evidence pointers and '
        'the unread traffic for the reader chosen above &mdash; plus a boundary file and a '
        'handshake the new session must run before acting. '
        '<b>A bus cursor is advanced only after a real spawn succeeds</b>, never on a dry run.</p>',
        '</form>',
    ]
    return "".join(body)


# --------------------------------------------------------- SLICE C: the quick-dispatch control


def _dispatch_panel(st: dict, plan=None) -> str:
    """Paste a prompt, see exactly which session it would reach, then act.

    ⭐ **Identity is rendered before the act, not after it.** The SECURITY requirement is that a
    dispatch shows target, task/lane, worktree and session state near the button — because the
    failure that costs something is not a malformed prompt, it is a correct prompt delivered to the
    wrong session. PREVIEW resolves the target and spawns nothing, so the operator can look before
    committing.
    """
    cards = st["sessions"]
    opts = [("", "— resolve from the prompt's header —")]
    for c in cards:
        sid = c.get("session_id") or ""
        opts.append((sid, f'{c.get("state")} · {(c.get("topic") or c.get("name") or "?")[:52]} '
                          f'· {c.get("where") or "?"}'))

    known = " · ".join(sorted(_sb.TARGET_ALIASES))
    out = [
        '<form method="POST" action="/switchboard/dispatch" id="qd-form">',
        '<textarea id="qd-prompt" name="prompt" rows="5" placeholder="Paste the prompt. '
        'A recognised header on one of its first '
        f'{_sb.HEADER_LINES} lines routes it deterministically." '
        'style="width:100%;font:12px ui-monospace,monospace"></textarea>',
        f'<div class="dim" style="font-size:11px;margin:4px 0 7px">recognised headers: '
        f'<b>{_e(known)}</b> — matched as whole phrases, no LLM router, no fuzzy scoring</div>',
        '<div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap">',
        f'<label>target<br><select name="session" style="min-width:330px">{_opts(opts)}</select></label>',
        '</div>',
        '<div style="margin:9px 0 0;display:flex;gap:8px;flex-wrap:wrap">',
        '<button name="dry" value="1" class="btn" style="cursor:pointer">PREVIEW (resolve only)</button>',
        '<button name="dry" value="" id="qd-go" class="btn" style="cursor:pointer;'
        'border-color:var(--accent);color:var(--accent);font-weight:700">COPY + DISPATCH</button>',
        '</div>',
        '</form>',
        # The clipboard half of COPY+OPEN happens HERE, in the browser, because that is the only
        # place with a clipboard. The server half opens what it safely can. Copy failing must never
        # block the dispatch, so the submit is not conditional on it.
        '<script>(function(){var f=document.getElementById("qd-form"),'
        'b=document.getElementById("qd-go"),t=document.getElementById("qd-prompt");'
        'if(!f||!b||!t)return;b.addEventListener("click",function(){'
        'try{if(navigator.clipboard&&navigator.clipboard.writeText){'
        'navigator.clipboard.writeText(t.value);}}catch(e){}});})();</script>',
    ]

    if plan:
        out.append(_plan_readout(plan))
    else:
        out.append('<p class="dim" style="font-size:11.5px;margin:10px 0 0">'
                   'Nothing dispatched this session. PREVIEW resolves the target and spawns '
                   'nothing.</p>')
    return "".join(out)


def _plan_readout(plan: dict) -> str:
    """The identity block. Everything the operator needs to catch a wrong target before acting."""
    dec = plan.get("decision")
    col = ("var(--pass)" if dec == "READY" else "var(--fail)" if dec == "REFUSE"
           else "var(--unmeas)")
    rows = [f'<div class="row" style="border-top:1px solid var(--rule);margin-top:10px;'
            f'padding-top:9px"><span class="tag" style="color:{col}">{_e(dec)}</span>'
            f'<span><b>{_e(plan.get("route") or "no route")}</b> — {_e(plan.get("why"))}</span>'
            f'<span class="dim">{plan.get("prompt_bytes", 0):,}b</span></div>']

    ch = plan.get("chosen")
    if ch:
        rows.append(
            '<div class="row"><span class="tag" style="color:var(--accent)">TARGET</span>'
            f'<span><b>{_e(ch.get("topic"))}</b><br>'
            f'<span class="dim" style="font-size:11px">'
            f'state {_e(ch.get("state"))} · pid {_e(ch.get("pid"))} · '
            f'{_e(ch.get("kind") or "?")} · job {_e(ch.get("job_state") or "—")}<br>'
            f'worktree/cwd <code>{_e(ch.get("cwd"))}</code><br>'
            f'session id <code>{_e(ch.get("session_id"))}</code></span>'
            + (f'<br><span class="bad">this session is blocked on: '
               f'{_e(str(ch.get("needs"))[:120])}</span>' if ch.get("needs") else "")
            + '</span><span></span></div>')
    if plan.get("matched_headers"):
        rows.append('<div class="row"><span class="tag dim">HEADER</span>'
                    f'<span>matched {_e(", ".join(plan["matched_headers"]))}</span>'
                    '<span></span></div>')
    for c in plan.get("candidates") or []:
        rows.append('<div class="row"><span class="tag dim">CANDIDATE</span>'
                    f'<span>{_e(c.get("state"))} · {_e(c.get("topic"))}<br>'
                    f'<span class="dim" style="font-size:11px">{_e(c.get("cwd"))}</span></span>'
                    '<span></span></div>')
    if plan.get("prompt_file"):
        rows.append('<div class="row"><span class="tag dim">SAVED</span>'
                    f'<span><code>{_e(plan["prompt_file"])}</code></span><span></span></div>')
    return "".join(rows)


# --------------------------------------------------------------------------- page


def page(st: Optional[dict] = None, dispatch: Optional[dict] = None) -> str:
    """The whole Switchboard as one HTML fragment, for embedding in the tracker's `.wrap`."""
    st = _sb.state() if st is None else st
    n = st["needs_you_count"]
    ncol = "var(--fail)" if n else "var(--pass)"
    m = st.get("mission") or {}
    title = m.get("title") or "no mission"

    o = [f"<style>{CSS}</style>", '<div class="sw">']
    o.append(
        '<div class="hdr"><div>'
        '<div style="font:700 15px/1.2 ui-monospace,monospace;letter-spacing:.1em">SWITCHBOARD</div>'
        f'<div class="dim" style="margin-top:3px">{_e(title[:96])}</div></div>'
        f'<div class="needs" style="color:{ncol}">NEEDS YOU — {n}</div></div>')
    o.append(f'<div class="dim" style="margin:-6px 0 12px">measured {_e(st["measured_at"])} '
             f'· nothing on this page is cached · refresh re-measures</div>')

    ties = st.get("critical_path_ties") or 0
    tie_note = (f' · ⚠ {ties} chains are equally long, so the head shown is only the first by id'
                if ties > 1 else "")
    o.append(_sec("Critical path", _dag(st),
                  note=f'longest {st["critical_path_basis"].lower()} chain — '
                       f'{" → ".join(st["critical_path"]) or "none"} · not a duration, not an ETA'
                       + tie_note))
    o.append(_sec("Ready in parallel", _parallel(st),
                  note="dependencies satisfied AND no live conflicting writer"))
    o.append(_sec("Start synced", _start_synced(st),
                  note="opens a session already holding a measured packet — no copy, no paste"))
    o.append(_sec("Needs you", _needs(st),
                  note="read from jobs, so a question outlives the session that asked it"))
    o.append(_sec("Sessions", _sessions(st),
                  note="registry × jobs × process table · resume offered only for EXITED-RESUMABLE"))
    o.append(_sec("Quick dispatch", _dispatch_panel(st, dispatch),
                  note="deterministic header routing · refuses rather than guesses a target"))
    o.append(_sec("Upstream", _upstream(st),
                  note="peer traffic is a nudge, not durable evidence"))
    o.append(_sec("Worktrees", _worktrees(st), note="git worktree list, then rev-parse"))
    o.append(_sec("Warnings", _warnings(st)))
    o.append("</div>")
    return "".join(o)
