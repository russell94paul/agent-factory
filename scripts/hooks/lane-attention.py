#!/usr/bin/env python3
"""Make the terminal tab of a Claude session ASK for attention when it needs input.

Three lanes running in three tabs, and the one with a question looks exactly like the two that
are busy. You find it by clicking through them. This fires on the Notification hook — which is
what Claude Code raises when a session is waiting on a permission prompt or a question — and does
two things a tab cannot do for itself:

  1. Flashes the Windows Terminal window in the taskbar (the "glow"). GetConsoleWindow() is NOT
     the right handle under Windows Terminal — it returns a hidden pseudo-console window and
     flashing it is a silent no-op — so we walk up the process tree to the real WindowsTerminal
     window and flash that.
  2. Marks the tab title with a bell glyph and the lane name, so once the flashing has pulled
     your eyes to the taskbar, the tab itself says which lane. Written to CONOUT$ rather than
     stdout, because a hook's stdout is captured by Claude Code and would never reach the
     terminal.

`clear` mode undoes the title marker. Failure is always silent: an attention hook that crashes a
session is worse than one that does nothing.
"""
import json
import os
import re
import sys

#: Trailing separators, both flavours — a cwd may arrive with either on Windows.
_TRIM = "/" + chr(92)

BELL = "\a"


def lane_name(payload):
    cwd = payload.get("cwd") or os.getcwd()
    base = os.path.basename(cwd.rstrip(_TRIM))
    parent = os.path.basename(os.path.dirname(cwd.rstrip(_TRIM)))
    return base if parent == ".worktrees" else base


def write_console(text):
    """Reach the real terminal, bypassing Claude Code's capture of our stdout."""
    try:
        with open("CONOUT$", "w", encoding="utf-8", errors="replace") as con:
            con.write(text)
            con.flush()
        return True
    except OSError:
        return False


def terminal_hwnd():
    """A visible WindowsTerminal window, or 0.

    Deliberately NOT the process tree. Walking parents from the hook looks precise and is
    brittle: the hook's own console handle is a pseudo-console, the chain differs between a wt
    tab and a bare console, and every failure mode returns 0 — a silent no-op that looks
    identical to success. All lanes live as tabs in one Windows Terminal window anyway, so the
    window is the right granularity: the flash says LOOK HERE, and the bell + title marker say
    which tab. Found by owning process name, which is true from any calling context.
    """
    try:
        import ctypes
        import subprocess
        from ctypes import wintypes
    except ImportError:
        return 0
    try:
        out = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq WindowsTerminal.exe", "/FO", "CSV", "/NH"],
            capture_output=True, text=True, timeout=5).stdout
        pids = {int(m) for m in re.findall(r'"WindowsTerminal\.exe","(\d+)"', out)}
        if not pids:
            return 0

        user32 = ctypes.WinDLL("user32", use_last_error=True)
        found = ctypes.c_void_p(0)

        @ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
        def cb(hwnd, _):
            owner = ctypes.c_ulong(0)
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(owner))
            if owner.value in pids and user32.IsWindowVisible(hwnd):
                # Only a real top-level window has a title; WT keeps hidden helpers too.
                if user32.GetWindowTextLengthW(hwnd) > 0:
                    found.value = hwnd
                    return False
            return True

        user32.EnumWindows(cb, 0)
        return found.value or 0
    except Exception:                                              # noqa: BLE001
        return 0


def flash(hwnd):
    """FlashWindowEx — flash caption AND taskbar button until the window is focused."""
    try:
        import ctypes
        from ctypes import wintypes

        class FLASHWINFO(ctypes.Structure):
            _fields_ = [("cbSize", wintypes.UINT), ("hwnd", wintypes.HWND),
                        ("dwFlags", wintypes.DWORD), ("uCount", wintypes.UINT),
                        ("dwTimeout", wintypes.DWORD)]

        FLASHW_ALL, FLASHW_TIMERNOFG = 0x00000003, 0x0000000C
        info = FLASHWINFO(ctypes.sizeof(FLASHWINFO), hwnd,
                          FLASHW_ALL | FLASHW_TIMERNOFG, 0, 0)
        return bool(ctypes.WinDLL("user32").FlashWindowEx(ctypes.byref(info)))
    except Exception:                                              # noqa: BLE001
        return False


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "notify"
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except (ValueError, OSError):
        payload = {}
    name = lane_name(payload)

    if mode == "clear":
        write_console(f"\033]0;{name}\a")
        return 0

    # Bell first: Windows Terminal puts a bell indicator on the exact tab that rang, which is the
    # cheapest correct answer to "which one".
    write_console(f"{BELL}\033]0;(!) {name} — needs you\a")
    hwnd = terminal_hwnd()
    if hwnd:
        flash(hwnd)
    if os.environ.get("LANE_ATTENTION_DEBUG"):
        print(json.dumps({"lane": name, "hwnd": hwnd, "mode": mode}))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:                                              # noqa: BLE001
        sys.exit(0)   # never break a session over a notification
