# State that lives outside every repository — 2026-08-22

Three things this day's work depends on exist only on one machine. None of them fails loudly if
missing: each one degrades into a *quieter, wrong answer*, which is the failure mode this
programme exists to catch. Recorded here so the loss is recoverable and, more importantly, so the
next person knows the instrument can be absent while the output still looks fine.

## 1. impeccable's detector dependencies — the loud one

`~/.claude/skills/impeccable/node_modules/` is untracked and machine-local. Without it,
`node scripts/detect.mjs` **does not fail**: it falls back to a regex-only engine and reports
**1 finding where the real 59-rule engine reports 313**. Anyone running it fresh would conclude the
artifact was nearly clean. See [[F50]] and [[F53]].

Pinned in `~/.claude/skills/impeccable/package.json` (mirrored beside this file as
`impeccable-package.json`, since the live copy is in no repository):

    npm install --prefix ~/.claude/skills/impeccable

Verified 2026-08-22: all four declared deps resolve from the skill dir, and the degraded run is
distinguishable by the banner `DEGRADED — HTML parser modules unavailable`.

## 2. The lane-attention hook — new today

`~/.claude/hooks/lane-attention.py` makes a lane's terminal ask for attention when it is waiting
on a question: bell, taskbar flash, and a tab-title marker. Three lanes in three tabs otherwise
look identical, and you find the one with a question by clicking through them.

The script is committed at `scripts/hooks/lane-attention.py`. The wiring is not — it lives in
`~/.claude/settings.json`, which is in no repository. To restore, merge into that file (do NOT
replace `UserPromptSubmit`, which already carries other hooks — append):

```json
"preferredNotifChannel": "terminal_bell",
"hooks": {
  "Notification": [
    {"hooks": [{"type": "command",
                "command": "python \"C:/Users/PaulRussell/.claude/hooks/lane-attention.py\" notify",
                "timeout": 8, "async": true}]}
  ],
  "UserPromptSubmit": [
    {"hooks": [{"type": "command",
                "command": "python \"C:/Users/PaulRussell/.claude/hooks/lane-attention.py\" clear",
                "timeout": 5, "async": true}]}
  ]
}
```

⚠ Two things learned building it, both silent-failure shaped:
- `GetConsoleWindow()` is the wrong handle under Windows Terminal — it returns a hidden
  pseudo-console and `FlashWindowEx` on it is a **no-op that returns success**. Find the window by
  owning process name instead.
- A hook's stdout is captured by Claude Code. To reach the actual terminal, write to `CONOUT$`.

Proven, not assumed: `FlashWindowEx` returned `True` against the live WT window (HWND 5048706),
and the pipe-test returned `{"lane": "certify", "hwnd": 5048706}`.

## 3. living-systems-ui's SKILL.md — already mitigated

`~/.claude/skills/living-systems-ui/SKILL.md` carries the impeccable precedence text that gate
`chain` reads (`factory/readiness.py:777`). It is in no repository, so the gate is green because
of an untracked file on one machine. **Mitigated**: the precedence text is mirrored verbatim into
`docs/evidence/impeccable-detector-pass-2026-08-22.md` (commit `1dc8cfb`), so the claim is
reproducible even though the instrument is not.

## The general shape

A gate that reads a file outside version control is measuring the machine, not the work. All three
of these were found the same way — by asking "could this be absent while the output still looks
right?" — and in every case the answer was yes.
