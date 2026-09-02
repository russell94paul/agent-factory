#!/usr/bin/env python3
"""Generate a SHA-256 inventory for raw research artifacts without modifying them."""
from pathlib import Path
import hashlib, json, argparse

parser = argparse.ArgumentParser()
parser.add_argument('--root', type=Path, default=Path('docs/01-research-corpus/raw'))
parser.add_argument('--out', type=Path, default=Path('docs/01-research-corpus/manifests/hash-inventory.jsonl'))
args = parser.parse_args()

rows = []
for p in sorted(args.root.rglob('*')):
    if p.is_file():
        h = hashlib.sha256()
        with p.open('rb') as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b''):
                h.update(chunk)
        rows.append({'path': p.as_posix(), 'sha256': h.hexdigest(), 'bytes': p.stat().st_size})
args.out.parent.mkdir(parents=True, exist_ok=True)
args.out.write_text(''.join(json.dumps(r, ensure_ascii=False)+'\n' for r in rows))
print(f'Wrote {len(rows)} entries to {args.out}')
