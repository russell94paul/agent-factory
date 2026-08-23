# Render pass — Roadmap tab, 2026-08-23

**The first consumer-layer validation of this tab.** Everything before this was render-to-string:
`lt.render(when, tab)` called in a test, asserting the HTML contains expected substrings. That
proves the page is *generated*. It cannot prove the page *looks right*.

Chrome was unreachable for most of the day — `list_connected_browsers` returned `[]` while `/mcp`
reported connected and the extension reported enabled. **Those are two different links in the
chain and neither UI reports on the one between them.** Root cause: the extension was signed out.

## What it proved

| | |
|---|---|
| `roadmap-top-renders.jpg` | the tab paints — nav, parallel panel, critical path, Done band. No error states. |
| `roadmap-blocked-BEFORE-oversized-connectives.jpg` | ⚠ **the defect** — "unlocks" and "waits on" render at the div's default size while every word around them is 11.5px |
| `roadmap-ready-AFTER-fix.jpg` | fixed — the row reads as one line at a consistent size |

## ⭐ The point

The defect was in code that **passed every test**, because the connective words were placed after
the closing `</span>` of the small phase label and inherited the div default. **No string
assertion would ever catch that.** It is obvious in one look and invisible to the suite.

That is the whole argument for the consumer-layer rule, demonstrated on the first day it could be
applied here — and it is why "renders" is a gate in the readiness set rather than a nice-to-have.

Also visible and worth recording: the `suite` gate paints as **"222 passed (cached, last run 8s
ago)"**. The rule that a cached figure carries its age in the same string as the number is not just
implemented, it is legible to a reader who never opens the code.
