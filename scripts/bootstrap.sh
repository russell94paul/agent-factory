#!/usr/bin/env bash
set -euo pipefail
python -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate 2>/dev/null || source .venv/Scripts/activate
pip install -q -e ".[dev]"
# The browser binary is a separate download that pip cannot perform. Without it the rendered
# validation cannot run, and a client-facing artifact cannot be certified — so bootstrap does it
# rather than leaving an operator to discover it at stage 4 of the meeting command.
echo "--- browser runtime ---"
python -m playwright install chromium
echo "--- gates ---"
pytest -q
echo "--- demo ---"
python -m factory.demo
