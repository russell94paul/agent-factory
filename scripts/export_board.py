#!/usr/bin/env python3
"""Export the task store to a tracked snapshot.

`.data/` is gitignored on purpose (see docs/evidence/machine-local-state-2026-08-22.md):
it is runtime state, and runtime state does not belong in git. But that leaves every
ticket on one machine, which is the same class of loss that doc exists to warn about —
the instrument absent while the output still looks fine.

This writes a DERIVED snapshot. It is not a second record: the store stays
authoritative, this is regenerated, never hand-edited.

    python scripts/export_board.py        # rewrite docs/board/tickets.json
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
