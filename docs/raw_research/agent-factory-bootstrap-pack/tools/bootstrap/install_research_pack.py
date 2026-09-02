#!/usr/bin/env python3
"""Safely copy this bootstrap pack into an existing agent-factory repo.

Dry-run is the default. Existing files are never overwritten unless --overwrite is supplied.
"""
from pathlib import Path
import argparse, shutil

parser = argparse.ArgumentParser()
parser.add_argument('target_repo', type=Path)
parser.add_argument('--apply', action='store_true', help='actually copy files')
parser.add_argument('--overwrite', action='store_true')
args = parser.parse_args()

pack = Path(__file__).resolve().parents[2]
target = args.target_repo.resolve()

if not target.exists() or not target.is_dir():
    raise SystemExit(f'Target repo does not exist: {target}')

skip_parts = {'.git', '__pycache__'}
ops = []
for src in pack.rglob('*'):
    if not src.is_file() or any(p in skip_parts for p in src.parts):
        continue
    rel = src.relative_to(pack)
    # Avoid copying the installer recursively only if target happens to be the pack itself.
    dst = target / rel
    if dst.exists() and not args.overwrite:
        ops.append(('SKIP_EXISTS', rel))
    else:
        ops.append(('COPY', rel))
        if args.apply:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)

for action, rel in ops:
    print(f'{action:12} {rel}')

if not args.apply:
    print('\nDry run only. Re-run with --apply after reviewing the plan.')
