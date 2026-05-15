#!/usr/bin/env bash
set -euo pipefail

# create virtual environment and install packages
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r backend/app/requirements.txt
