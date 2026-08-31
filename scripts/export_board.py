#!/usr/bin/env python3
"""Export the task store to a tracked snapshot.

`.data/` is gitignored on purpose (see docs/evidence/machine-local-state-2026-08-22.md):
it is runtime state, and runtime state does not belong in git. But that leaves every
ticket on one machine, which is the same class of loss that doc exists to warn about —
the instrument absent while the output still looks fine.

This writes a DERIVED snapshot. It is not a second record: the store stays
authoritative, this is regenerated, never hand-edited.

    python scripts/export_board.py            # rewrite docs/board/tickets.json
    python scripts/export_board.py --summary  # print the figure the showcase renders

⭐ ``--summary`` exists because a regeneration command that does not reproduce the *rendered*
figure is only half a control. ``docs/artifacts/project.html`` cited this script beside its
"N of M tickets closed" line, but the script emitted the task list and never computed that
pair — so the number still had to be transcribed by hand, and it drifted anyway (71 -> 76
in two days, the second drift on the same figure). The command now prints exactly what the
page renders, so the two can be compared without reading JSON.

⛔ Note what this still does NOT do: nothing asserts the page matches. Carrying a command is
not a control until something runs it — the same gap as a lint that is fully specified and
has run once in 193 operations.
"""
import json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from factory.tasks import TaskStore

ROOT = pathlib.Path(__file__).resolve().parent.parent
store = TaskStore(ROOT / ".data" / "tasks.jsonl")
tasks = sorted(store.all(), key=lambda t: t.title)
out = {
    "_generated_by": "python scripts/export_board.py",
    "_authoritative_source": ".data/tasks.jsonl (append-only, gitignored)",
    "_note": "DERIVED snapshot for recovery and for rendering the board. Never hand-edit.",
    "count": len(tasks),
    "tasks": [t.to_dict() for t in tasks],
}
dest = ROOT / "docs" / "board" / "tickets.json"
dest.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
print("wrote %s — %d tasks" % (dest.relative_to(ROOT), len(tasks)))

if "--summary" in sys.argv:
    # "closed" = done + abandoned. An abandoned ticket is closed: it will not be worked
    # again. Collapsing it into "open" would overstate the backlog, and into "done" would
    # claim work that never happened.
    closed = sum(1 for t in tasks if t.to_dict().get("status") in ("done", "abandoned"))
    print("%d of %d tickets closed" % (closed, len(tasks)))
