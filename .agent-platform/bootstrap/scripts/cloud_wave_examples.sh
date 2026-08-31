#!/usr/bin/env bash
set -euo pipefail

cat <<'EOF'
Examples only — edit the tasks for the approved build DAG.
Each claude --remote call creates an independent cloud session.

claude --remote "Read the approved spec and perform a read-only architecture review. Do not modify code."
claude --remote "Implement the isolated task assigned to this branch, run targeted tests, and summarize evidence."
claude --remote "Review the proposed change against the GREEN contract and report failures without merging."

Monitor cloud sessions in claude.ai/code or with /tasks from a local Claude Code session.
EOF
