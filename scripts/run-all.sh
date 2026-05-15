#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

bash "$ROOT/scripts/run-backend.sh" &
BACKEND_PID=$!

bash "$ROOT/scripts/run-frontend.sh" &
FRONTEND_PID=$!

wait "$BACKEND_PID" "$FRONTEND_PID"
