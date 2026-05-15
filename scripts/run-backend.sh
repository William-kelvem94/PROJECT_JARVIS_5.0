#!/usr/bin/env bash
set -euo pipefail

# activate venv and start uvicorn from repo root
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PYTHON="$ROOT/.venv/bin/python"

cd "$ROOT/backend"

if [ ! -x "$PYTHON" ]; then
  echo "Missing venv python: $PYTHON" >&2
  exit 1
fi

exec "$PYTHON" -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
