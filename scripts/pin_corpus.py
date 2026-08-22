"""Re-pin the eval corpus, deliberately.

    python scripts/pin_corpus.py --why "re-measured the landing grain against the live table"

The corpus is hashed in evals/MANIFEST.sha256 and verified on every load, so changing it without
re-pinning breaks every run — which is the point. This script is the only sanctioned way to
change the pin, and it refuses to run without a stated reason, because "why did the grader
change" is exactly the question a silent re-pin destroys.

It prints the old and new hashes and the diff summary. Commit the manifest and the corpus in the
same commit, and put the --why text in the commit message.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CORPUS_ROOT = ROOT / "evals"
MANIFEST = CORPUS_ROOT / "MANIFEST.sha256"


def _read_manifest() -> dict:
    if not MANIFEST.is_file():
        return {}
    out = {}
    for line in MANIFEST.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            sha, _, rel = line.partition("  ")
            out[rel.strip()] = sha.strip()
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="pin_corpus")
    ap.add_argument("--why", required=True,
                    help="why the corpus changed. Recorded, and required.")
    ap.add_argument("--check", action="store_true",
                    help="report drift without re-pinning; exits non-zero if anything moved")
    args = ap.parse_args(argv)

    if len(args.why.strip()) < 12:
        print("--why must be a real reason, not a placeholder.", file=sys.stderr)
        return 2

    old = _read_manifest()
    files = sorted(p for p in CORPUS_ROOT.rglob("*.json") if p.is_file())
    if not files:
        print(f"no corpus files under {CORPUS_ROOT}", file=sys.stderr)
        return 2

    lines, moved = [], []
    for p in files:
        rel = p.relative_to(CORPUS_ROOT).as_posix()
        sha = hashlib.sha256(p.read_bytes()).hexdigest()
        lines.append(f"{sha}  {rel}")
        if old.get(rel) != sha:
            moved.append((rel, old.get(rel), sha))

    for rel, was, now in moved:
        print(f"{rel}\n  was {was or '(unpinned)'}\n  now {now}")
        try:
            doc = json.loads(p.read_text(encoding="utf-8")) if False else None
        except Exception:
            doc = None
    if not moved:
        print("corpus matches its manifest — nothing to re-pin.")
        return 0

    if args.check:
        print(f"\n{len(moved)} corpus file(s) differ from the pin. Not re-pinning (--check).")
        return 1

    MANIFEST.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nre-pinned {len(moved)} file(s).")
    print(f"reason recorded: {args.why}")
    print("\nCommit the corpus and the manifest together, and put the reason in the message.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
