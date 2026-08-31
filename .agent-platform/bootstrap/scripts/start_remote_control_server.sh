#!/usr/bin/env bash
set -euo pipefail

CAPACITY="${AF_REMOTE_CAPACITY:-8}"
PREFIX="${AF_REMOTE_PREFIX:-agent-factory}"

if ! command -v claude >/dev/null 2>&1; then
  echo "Claude Code CLI not found on PATH." >&2
  exit 1
fi

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Run this from the Agent Factory git repository root." >&2
  exit 1
fi

echo "Starting Claude Remote Control server"
echo "  spawn mode : worktree"
echo "  capacity   : ${CAPACITY}"
echo "  prefix     : ${PREFIX}"
echo "  sandbox    : enabled"

exec claude remote-control \
  --spawn worktree \
  --capacity "${CAPACITY}" \
  --sandbox \
  --remote-control-session-name-prefix "${PREFIX}"
