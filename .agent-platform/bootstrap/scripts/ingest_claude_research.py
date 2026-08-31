#!/usr/bin/env python3
"""Validate a manually returned Claude Research report and mark it ready."""
from __future__ import annotations
import argparse, json
from datetime import datetime, timezone
from pathlib import Path

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--job-dir',required=True); args=ap.parse_args()
    d=Path(args.job_dir).resolve(); meta_path=d/'JOB.json'; raw_path=d/'RAW_REPORT.md'
    if not meta_path.exists(): raise SystemExit(f"Missing {meta_path}")
    meta=json.loads(meta_path.read_text(encoding='utf-8')); jid=meta['id']
    if not raw_path.exists() or not raw_path.read_text(encoding='utf-8').strip():
        raise SystemExit(f"RAW_REPORT.md is empty for {jid}")
    raw=raw_path.read_text(encoding='utf-8')
    marker=f"RESEARCH_ID: {jid}"
    warnings=[]
    if marker not in raw: warnings.append(f"missing exact research marker: {marker}")
    if len(raw.split()) < 300: warnings.append("report is unusually short; verify Research completed")
    status='READY_FOR_SYNTHESIS' if not warnings else 'NEEDS_REVIEW'
    result={'id':jid,'status':status,'checked_at':datetime.now(timezone.utc).isoformat(),'warnings':warnings,'word_count':len(raw.split())}
    (d/'INGEST_STATUS.json').write_text(json.dumps(result,indent=2)+"\n",encoding='utf-8')
    meta['status']=status; meta['ingested_at']=result['checked_at']; meta_path.write_text(json.dumps(meta,indent=2)+"\n",encoding='utf-8')
    print(json.dumps(result,indent=2))
    return 0 if status=='READY_FOR_SYNTHESIS' else 2
if __name__=='__main__': raise SystemExit(main())
