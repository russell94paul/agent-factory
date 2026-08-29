#!/usr/bin/env python3
"""Generate the board artifact from the task store.

The board must never be hand-maintained. Three ticket-record systems already
disagree in this estate; a fourth that drifts from `.data/tasks.jsonl` would be
the same failure with a nicer font.

So the split is:

    .data/tasks.jsonl          AUTHORITATIVE — existence, status, evidence
    docs/board/ticket-detail.json  authored prose only (why / acceptance / deps)
    docs/board/template.html   the page, with a "__TICKETS__" placeholder
    docs/board/index.html      GENERATED — never edit, it is overwritten

Run:
    python scripts/export_board.py          # store  -> docs/board/tickets.json
    python scripts/build_board_artifact.py  # + prose -> docs/board/index.html

Then publish `docs/board/index.html` to the existing artifact URL, so saved
ticket states survive.
"""
import io
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
BOARD = ROOT / "docs" / "board"

# CIP-01..20 are the Client Intake Platform. CIP-21+ came from the external
# review and are agent-factory hardening — mis-prefixed, pending rename to AF-*.
# The board shows that honestly rather than pretending one track.
PLATFORM_MAX = 20

TITLE_RE = re.compile(r"^(?P<id>[A-Z]+-\d+)\s*-\s*(?P<phase>[PF]\d)\s+(?P<title>.+)$")


def load_tasks():
    p = BOARD / "tickets.json"
    if not p.is_file():
        sys.exit("no %s — run scripts/export_board.py first" % p.relative_to(ROOT))
    return json.loads(p.read_text(encoding="utf-8"))["tasks"]


def load_detail():
    p = BOARD / "ticket-detail.json"
    if not p.is_file():
        return {}
    return json.loads(p.read_text(encoding="utf-8")).get("detail", {})


def split_evidence(ref):
    """`<source> | acceptance: <criterion>` -> (source, acceptance)."""
    if "| acceptance:" in ref:
        src, acc = ref.split("| acceptance:", 1)
        return src.strip(), acc.strip()
    return ref.strip(), ""


def build():
    tasks, detail = load_tasks(), load_detail()
    tickets, skipped = [], 0

    for t in tasks:
        m = TITLE_RE.match(t["title"])
        if not m:
            skipped += 1
            continue
        tid, phase, title = m.group("id"), m.group("phase"), m.group("title")
        num = int(tid.split("-")[1])
        track = "platform" if (tid.startswith("CIP") and num <= PLATFORM_MAX) else "factory"

        d = dict(detail.get(tid, {}))
        # Tickets from the review carry their source and acceptance as evidence.
        if not d.get("acc") or not d.get("ev"):
            for ev in t.get("evidence", []):
                src, acc = split_evidence(ev.get("ref", ""))
                d.setdefault("ev", src)
                if acc:
                    d.setdefault("acc", acc)

        tickets.append({
            "id": tid, "p": phase, "t": title, "track": track,
            "e": d.get("e", "M"),
            "dep": d.get("dep", []),
            "why": d.get("why", ""),
            "acc": d.get("acc", "<b>No acceptance criterion recorded.</b> Until one exists this is a "
                                "<i>decide</i> ticket, not a <i>build</i> ticket."),
            "ev": d.get("ev", "—"),
            "status": t.get("status", "open"),
        })

    tickets.sort(key=lambda x: (x["track"] != "platform", int(x["id"].split("-")[1])))

    tmpl = (BOARD / "template.html").read_text(encoding="utf-8")
    if "__TICKETS__" not in tmpl:
        sys.exit("template.html has no __TICKETS__ placeholder")
    out = tmpl.replace('"__TICKETS__"', json.dumps(tickets, ensure_ascii=False, indent=1))

    dest = BOARD / "index.html"
    io.open(dest, "w", encoding="utf-8", newline="\n").write(out)

    plat = sum(1 for x in tickets if x["track"] == "platform")
    noacc = sum(1 for x in tickets if "No acceptance criterion" in x["acc"])
    print("wrote %s" % dest.relative_to(ROOT))
    print("  tickets: %d  (platform %d · factory %d)" % (len(tickets), plat, len(tickets) - plat))
    print("  without an acceptance criterion: %d" % noacc)
    if skipped:
        print("  tasks skipped (title not ID - PHASE title): %d" % skipped)
    return 0


if __name__ == "__main__":
    sys.exit(build())
