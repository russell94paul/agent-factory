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

# CIP-01..20 build the intake platform; CIP-21+ harden agent-factory itself. They are shown as
# separate tracks because their P-labels mean different things — NOT because they are different
# products. Plan §0.4: "the client portal is a front end on B1 and B2 ... It is not a new
# pipeline." §3: "we already own every piece but the front end." So CIP-01..20 build the missing
# B1–B2 surface and CIP-21+ harden the machinery running B3–B7; both are the factory. The AF-*
# rename is ON HOLD — it would formalise a split the plan denies.
PLATFORM_MAX = 20

TITLE_RE = re.compile(r"^(?P<id>[A-Z]+-\d+)\s*-\s*(?P<phase>[A-Z]\d)\s+(?P<title>.+)$")

# ⭐ The absorption backlog titles itself `AB-01 · R3 …` — middot, and the token after it is the
# SOURCE PASS, not a phase. It therefore never matched TITLE_RE, so all 19 rows were counted in
# "tasks skipped" and rendered nowhere. The board that carries CIP-01 — whose entire job is
# "action or reject AB-01..AB-19" — did not show a single one of them. Disclosed only as a skip
# count in build output, which nobody reads. See docs/reviews/divergence-2026-08-29.md.
# The source token is NOT uniform — `R3 `, `R16-outside:`, `R8's`, and AB-19 has none at all — so
# it is captured optionally rather than required. Forcing a shape the data does not have is what
# dropped these rows in the first place.
AB_TITLE_RE = re.compile(r"^(?P<id>AB-\d+)\s*·\s*(?P<title>.+)$")
AB_SOURCE_RE = re.compile(r"^(R\d+)")


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
        m = TITLE_RE.match(t["title"]) or AB_TITLE_RE.match(t["title"])
        if not m:
            skipped += 1
            continue
        tid, title = m.group("id"), m.group("title")
        if "phase" in m.groupdict():
            phase = m.group("phase")
        else:                                   # AB rows: source pass if stated, else "R?"
            sm = AB_SOURCE_RE.match(title)
            phase = sm.group(1) if sm else "R?"
        num = int(tid.split("-")[1])
        track = ("absorption" if tid.startswith("AB")
         else "observed" if tid.startswith("OBS")
         else "platform" if (tid.startswith("CIP") and num <= PLATFORM_MAX)
         else "factory")

        d = dict(detail.get(tid, {}))
        # Tickets from the review carry their source and acceptance as evidence.
        if not d.get("acc") or not d.get("ev"):
            for ev in t.get("evidence", []):
                if ev.get("kind") == "note":
                    d.setdefault("why", ev.get("ref", ""))
                    continue
                src, acc = split_evidence(ev.get("ref", ""))
                d.setdefault("ev", src)
                if acc:
                    d.setdefault("acc", acc)

        tickets.append({
            "id": tid, "p": phase, "t": title, "track": track,
            "e": d.get("e", "M"),
            # ⭐ Dependencies come from the STORE, not from authored prose. Until 2026-08-29 this
            # read d["dep"] out of ticket-detail.json while every ticket's blocked_by sat empty —
            # so the board claimed a DAG "computed from the store" that the store did not hold,
            # and blocked_by was a supported, populated, never-read field. The edges are now
            # `block` events. See docs/reviews/divergence-2026-08-29.md D-1.
            "dep": t.get("blocked_by", []),
            "why": d.get("why", ""),
            "acc": d.get("acc", "<b>No acceptance criterion recorded.</b> Until one exists this is a "
                                "<i>decide</i> ticket, not a <i>build</i> ticket."),
            "ev": d.get("ev", "—"),
            "status": t.get("status", "open"),
        })

    ORDER = {"platform": 0, "factory": 1, "absorption": 2, "observed": 3}
    tickets.sort(key=lambda x: (ORDER.get(x["track"], 9), int(x["id"].split("-")[1])))

    tmpl = (BOARD / "template.html").read_text(encoding="utf-8")
    if "__TICKETS__" not in tmpl:
        sys.exit("template.html has no __TICKETS__ placeholder")
    out = tmpl.replace('"__TICKETS__"', json.dumps(tickets, ensure_ascii=False, indent=1))

    dest = BOARD / "index.html"
    io.open(dest, "w", encoding="utf-8", newline="\n").write(out)

    plat = sum(1 for x in tickets if x["track"] == "platform")
    obs = sum(1 for x in tickets if x["track"] == "observed")
    noacc = sum(1 for x in tickets if "No acceptance criterion" in x["acc"])
    print("wrote %s" % dest.relative_to(ROOT))
    absn = sum(1 for x in tickets if x["track"] == "absorption")
    fac = len(tickets) - plat - obs - absn
    print("  tickets: %d  (platform %d · factory %d · absorption %d · observed %d)"
          % (len(tickets), plat, fac, absn, obs))
    print("  without an acceptance criterion: %d" % noacc)
    if skipped:
        print("  tasks skipped (title not ID - PHASE title): %d" % skipped)
    return 0


if __name__ == "__main__":
    sys.exit(build())
