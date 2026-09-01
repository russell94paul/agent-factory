# Switchboard redesign — the brief, and the constraints that make it implementable

**For pasting into ChatGPT (or any designer) alongside the files in this folder.**

Everything below is measured from the running system on 2026-09-01, not described from memory.

---

## What this is

A **mission-control surface for operating AI agent sessions**, used mostly from a phone through a
tunnel, sometimes from a desktop. The operator is one person running several Claude Code sessions
across several git repos. It is not a dashboard: nobody browses it. They open it because something
needs them, or because they want to start work.

It answers three questions and defers everything else:

```
1. WHAT NEEDS ME?           2. WHAT SHOULD HAPPEN NEXT?      3. WHAT IS HAPPENING NOW?
```

## Files in this folder

| file | what it is |
|---|---|
| `rendered-*.html` | the **live output**, pulled through the real tunnel. This is what the operator sees. Open them in a browser. |
| `rendered-inspector.html` | the detail panel, open on a real work item |
| `SOURCE-switchboard_p1.py` | the whole UI layer — 1,153 lines, of which 171 are CSS and 14 are render functions |
| `current.css` | just the stylesheet, extracted |
| `theme-tokens.css` | the light/dark variables the page **inherits from its host shell** and does not own |

---

## ⛔ Hard constraints — a redesign that breaks these cannot ship

1. **Server-rendered HTML from Python. No build step, no framework, no npm.** The page is
   assembled by string concatenation in one Python module and served by a stdlib HTTP server.
   React/Vue/Svelte/Tailwind-CLI are all out. Plain CSS in one `<style>` block, plain HTML,
   and a few lines of vanilla JS.

2. **It must work with JavaScript disabled.** Every action is a `<form method="POST">` or an
   `<a href>`. JS is used for exactly two accelerators — Ctrl/Cmd+K focus, and the restart poll —
   and the page is fully operable without both.

3. **It is embedded, not standalone.** The markup is injected into an existing page's `.wrap`
   div. It does not own `<html>`, `<head>` or `<body>`, and it **inherits** its colour tokens:
   `--paper --ink --ink2 --ink3 --rule --raise --pass --fail --unmeas --accent`.
   Both light and dark must work; the host switches on `prefers-color-scheme`.

4. **Phone first, at 390px and 430px.** Validated in real Chromium at both, plus 1440. Zero
   horizontal page scroll is a hard gate — wide content scrolls inside its own container.
   Tap targets ≥ 44px on anything consequential.

5. **One DOM for phone and desktop.** CSS decides the layout; there is no separate mobile
   template, because two templates drift.

6. **These POST routes exist and must keep working** (the buttons are real):
   `/switchboard/create` · `/switchboard/start` · `/switchboard/resolve` ·
   `/switchboard/autonomy` · `/switchboard/dispatch` · `/switchboard/restart`

---

## ⭐ Rules the current design follows, learned the hard way. Keep them.

These are not style preferences. Each one was a defect that reached a human.

- **A control that only navigates must not wear an imperative verb.** 58 buttons said `RESOLVE`,
  `VALIDATE`, `REVIEW OUTCOME` and were links to a detail panel. The operator tapped one on a
  phone and nothing happened.
- **Absence must never render as a value.** "Not measured" is its own mark, not a `0` and not a
  tick. There are four verdicts — PASS / FAIL / UNMEASURED / N/A — and UNMEASURED is never a pass.
- **Every figure carries its basis** — MEASURED / DERIVED / NOT-RECORDED / NOT-VISIBLE.
- **Stale items must not outrank live ones.** Five old questions once filled the whole first
  screen and pushed the one live blocker below several scrolls.
- **A permanently-true alarm is not an alarm.** Repo health showed "26 uncommitted" constantly and
  outranked a live decision; it moved below.
- **State carries a glyph as well as a colour**, so a greyscale screenshot and a colour-blind
  reader both still read it.
- **No aggregate score.** Priority is a coarse band plus the factors that produced it, never a
  decimal, because the weighting is not validated.

---

## The current information architecture

```
TOP BAR   AGENT FACTORY · [search/command] · ↻ Refresh · + CREATE · •••
                                                          └ Restart · Re-measure · Diagnostics
NOW  (default)          WORK      SESSIONS   INBOX   MISSION   MORE
├── NEEDS YOU                                                   ├── Activity
├── NEXT                                                        ├── Evidence
├── RUNNING                                                     ├── Worktrees
├── RECENT                                                      ├── Diagnostics
└── [collapsed: the older panel set]                            └── System health

DESKTOP  nav rail | action column | inspector      PHONE  one column + bottom nav (5 slots)
```

**The card is the unit.** Id, state, visibility, objective, the readiness checks, and exactly
**one** primary action derived from state.

---

## What Paul dislikes — the actual redesign ask

> *"I just don't like the layout and flow."*

Treat that as the brief. The information is right; the **arrangement and the movement through it**
are not. Specific things worth attacking:

- The NOW page is a **vertical stack of four equal-weight sections**. Nothing signals that NEEDS
  YOU matters more than RECENT except position.
- **Density is uniform.** Everything is a bordered card at the same visual weight, so scanning is
  slow and there is no rhythm.
- Getting from a card to its detail is a **full page navigation** that loses your place.
- The desktop three-column shell is under-used — the inspector only appears when something is
  selected, so most of the time it is one narrow column in a wide window.
- The retained older panel set at the bottom of NOW is **~40KB of collapsed markup** that
  contributes nothing visually but sits in the DOM.

## And the feature being added alongside — design for it

A **session console**: pick a session from a dropdown, see its recent output, reply to it. Splits
of 1 / 2 / 4 panes, horizontal or vertical, and pop-out into its own window.

⚠ **It is not a TTY and must not look like one.** It cannot attach to a running process's terminal.
What it genuinely does is read each session's transcript from disk and send a reply through an
existing dispatch route. Design it as a **conversation pane**, not a shell — calling it a terminal
would be the same lie as a button that only navigates.

---

## What a good answer looks like

Not a picture. A redesign that can be implemented as **Python functions returning HTML strings**,
with:

1. the new IA and what moves where, with a reason per move;
2. a CSS strategy using the inherited tokens, light and dark;
3. the phone layout at 390px specifically — what is above the fold, and what the thumb reaches;
4. the console's pane model and how it degrades to one pane on a phone;
5. anything from the "rules learned the hard way" list it would change, **and why it is safe**.
