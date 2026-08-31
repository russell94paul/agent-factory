#!/usr/bin/env python3
"""Compile a YAML research wave into Claude Research prompt packets.

No API calls are made. The output is a deterministic queue for the operator to
run through Claude Research using an existing Claude subscription.
"""
from __future__ import annotations
import argparse, json, shutil
from datetime import datetime, timezone
from pathlib import Path
try:
    import yaml
except ImportError as exc:
    raise SystemExit("PyYAML is required. Run: python -m pip install -r scripts/requirements.txt") from exc

RETURN_CONTRACT = """# Return Contract — {job_id}\n\nRun the accompanying PROMPT.md in Claude Research. Return the report without manually summarizing it.\n\nThe report should contain:\n1. Executive findings\n2. Evidence table\n3. Prior art / implementations\n4. Successes, failures, and limitations\n5. Contradictions / unresolved questions\n6. Evidence labels: EMPIRICAL / PRACTICE / INFERENCE / SPECULATION\n7. Agent Factory architecture impact\n8. Simplest viable recommendation\n9. What not to build\n10. Falsification experiments\n11. Sources/citations\n12. Final marker: RESEARCH_ID: {job_id}\n\nSave or paste the raw report verbatim into RAW_REPORT.md in this job directory.\n"""

HEADER = """\n\n---\n\n## Bootstrap Research Execution Contract\n\nYou are running this as a Claude Research job for the Agent Factory program.\n\n- Research ID: **{job_id}**\n- Challenge the preferred architecture; assume it may be over-engineered.\n- Clearly separate measured evidence, implementation practice, inference, and speculation.\n- Prefer primary sources, empirical work, official docs/specs, and original repositories.\n- Identify existing implementations and failures before proposing new machinery.\n- End with the exact line: `RESEARCH_ID: {job_id}`.\n"""

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('manifest')
    ap.add_argument('--out', required=True)
    args=ap.parse_args()
    manifest_path=Path(args.manifest).resolve()
    # Pack root assuming research/manifests/*.yaml; fallback to cwd search.
    pack_root=manifest_path.parent.parent.parent if manifest_path.parent.name == 'manifests' else Path.cwd()
    m=yaml.safe_load(manifest_path.read_text(encoding='utf-8')) or {}
    out=Path(args.out).resolve(); queue=out/'queue'; queue.mkdir(parents=True, exist_ok=True)
    jobs=m.get('jobs', []) or []
    job_ids={j['id'] for j in jobs}
    lines=[f"# Claude Research Queue — {m.get('wave', manifest_path.stem)}", "", f"Objective: {m.get('objective','')}", "", "This queue uses Claude Research on the operator's subscription. No API key is required.", ""]
    now=datetime.now(timezone.utc).isoformat()
    for j in jobs:
        jid=j['id']; deps=j.get('depends_on',[]) or []
        bad=[d for d in deps if d not in job_ids]
        if bad: raise SystemExit(f"{jid}: unknown dependencies: {bad}")
        src=(pack_root/j['prompt']).resolve()
        if not src.exists(): raise SystemExit(f"{jid}: prompt not found: {src}")
        jdir=queue/jid; jdir.mkdir(parents=True, exist_ok=True)
        prompt=src.read_text(encoding='utf-8').rstrip()+HEADER.format(job_id=jid)+"\n"
        (jdir/'PROMPT.md').write_text(prompt,encoding='utf-8')
        (jdir/'RETURN_CONTRACT.md').write_text(RETURN_CONTRACT.format(job_id=jid),encoding='utf-8')
        raw=jdir/'RAW_REPORT.md'
        if not raw.exists(): raw.write_text('',encoding='utf-8')
        status='READY_FOR_CLAUDE_RESEARCH' if not deps else 'BLOCKED_BY_RESEARCH'
        meta={
            'id':jid,'wave':m.get('wave'), 'priority':j.get('priority','medium'),
            'execution_surface':'claude_research','prompt_source':j['prompt'],
            'depends_on':deps,'status':status,'prepared_at':now,
            'raw_report':'RAW_REPORT.md'
        }
        (jdir/'JOB.json').write_text(json.dumps(meta,indent=2)+"\n",encoding='utf-8')
        deptext=', '.join(deps) if deps else 'none'
        lines += [f"## {jid}", f"- Priority: **{j.get('priority','medium')}**", f"- Status: **{status}**", f"- Depends on: {deptext}", f"- Prompt: `queue/{jid}/PROMPT.md`", f"- Return to: `queue/{jid}/RAW_REPORT.md`", ""]
    (out/'RESEARCH_QUEUE.md').write_text('\n'.join(lines),encoding='utf-8')
    print(out/'RESEARCH_QUEUE.md')
    return 0
if __name__=='__main__': raise SystemExit(main())
