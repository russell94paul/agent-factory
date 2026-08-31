---
name: research-wave-runner
description: Compile a YAML research wave into dependency-aware Claude Research prompt packets and a prioritized queue. This version does not call any paid API.
---

# Research Wave Runner — Claude Subscription Mode

This skill prepares research; it does not launch an API job.

## Flow

```text
manifest
→ dependency check
→ prompt packet generation
→ READY / BLOCKED queue
→ Claude Research human-trigger step
→ ingest
→ synthesis
```

## Run

```bash
python <pack>/scripts/prepare_claude_research_wave.py \
  <pack>/research/manifests/WAVE_0.yaml \
  --out .agent-platform/research
```

The command creates:

- `.agent-platform/research/RESEARCH_QUEUE.md`
- one directory per research job under `.agent-platform/research/queue/`
- `JOB.json`, `PROMPT.md`, and `RETURN_CONTRACT.md` for every job

Do not prepare or run research questions already answered by current repository evidence.

When reports return, verify/ingest them and invoke `research-synthesizer`.
