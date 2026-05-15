#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
FRONTEND_DIR="$ROOT/frontend"

cd "$FRONTEND_DIR"

if command -v pnpm >/dev/null 2>&1; then
  pnpm install
  exec pnpm dev
fi

if command -v corepack >/dev/null 2>&1; then
  corepack pnpm install
  exec corepack pnpm dev
fi

if command -v npm >/dev/null 2>&1; then
  npm install
  exec npm run dev
fi

echo "Neither pnpm nor npm found" >&2
exit 1
