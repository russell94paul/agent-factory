# Paste this into ChatGPT with the zip attached

---

You are redesigning the **layout and flow** of an operator control surface. I am attaching a zip.
Open `REDESIGN-BRIEF.md` first — it has the measured constraints — then look at the
`rendered-*.html` files, which are the **live output** of the current page, and `current.css`.

**Your deliverable is a design specification precise enough that a coding agent can implement it
without asking follow-up questions.** Not a mockup, not an image, not a mood board. I will hand
your output to a coding agent that edits Python.

## What the thing is

A mission-control page for operating several AI coding agents at once. One operator — me. I open
it because something needs me, or because I want to start work. **I use it mostly on a phone
through a tunnel**, sometimes on a desktop. Nobody browses it.

It answers three questions: **what needs me · what should happen next · what is happening now.**

## Non-negotiable constraints — a redesign that breaks these cannot be built

1. **Server-rendered HTML built by string concatenation in Python.** No React, Vue, Svelte,
   Tailwind CLI, npm, or build step of any kind. Plain CSS in one `<style>` block, plain HTML,
   a few lines of vanilla JS at most.
2. **It must work with JavaScript disabled.** Every action is a `<form method="POST">` or `<a href>`.
3. **It is embedded in a host page.** It does not own `<html>/<head>/<body>` and it **inherits**
   its colour variables: `--paper --ink --ink2 --ink3 --rule --raise --pass --fail --unmeas --accent`.
   Light and dark both have to work.
4. **390px phone first.** Zero horizontal page scroll is a hard gate. Tap targets ≥44px.
5. **One DOM for phone and desktop** — CSS decides layout. Two templates drift.

## What I actually dislike (this is the brief)

The information is right. The **arrangement and the movement through it** are wrong.

- The main page is four stacked sections of equal visual weight. Nothing says NEEDS YOU matters
  more than RECENT except that it is higher up.
- Density is uniform — everything is a bordered card at the same weight, so scanning is slow.
- Going from a card to its detail is a full page navigation that loses my place.
- On desktop the third column is empty most of the time.
- There is ~40KB of collapsed legacy markup at the bottom of the main page.

## Rules I will not give up — they each came from a real failure

- A control that only navigates must **not** wear an imperative verb ("RESOLVE", "VALIDATE").
- Absence must never render as a value. "Not measured" is its own mark — never a 0, never a tick.
- Every number carries its basis: MEASURED / DERIVED / NOT-RECORDED / NOT-VISIBLE.
- Stale items must not outrank live ones; a permanently-true alarm is not an alarm.
- State carries a glyph as well as a colour (greyscale screenshots, colour-blind readers).
- No aggregate score. Priority is a coarse band plus the factors that produced it.

If you want to change any of these, say which, and make the safety argument.

## Also design this new surface

A **session console**: pick a session per pane, read its recent conversation, reply to it.
1 / 2 / 4 panes, horizontal or vertical, pop-out into its own window.
⚠ It is **not** a terminal and must not look like one — it cannot attach to a process. It reads a
transcript and sends a reply. Design it as a conversation pane. On a phone it must degrade to one.

## Give me back

1. **The new information architecture** — what moves where, one sentence of reasoning per move.
2. **The 390px layout specifically**: what is above the fold, what the thumb reaches, what collapses.
3. **The desktop layout** and what earns the third column.
4. **A visual hierarchy system** — how many levels of density/weight, and which content sits at each.
5. **The card anatomy** — what is on it, what is not, and where the rest goes.
6. **The console pane model** and its phone degradation.
7. **CSS approach** using the inherited variables, light and dark.
8. **What you would delete.** I would rather remove things than add them.

Be concrete and opinionated. Where you are trading something off, name the trade.
