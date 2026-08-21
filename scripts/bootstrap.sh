#!/usr/bin/env bash
set -euo pipefail
python -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate 2>/dev/null || source .venv/Scripts/activate
pip install -q -e ".[dev]"
echo "--- gates ---"
pytest -q
echo "--- demo ---"
python -m factory.demo
