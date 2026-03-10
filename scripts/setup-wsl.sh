#!/usr/bin/env bash
# helper script for people running the repo inside WSL2
# this assumes you have already installed a Linux distro (Ubuntu) via WSL
# and that the project directory is available under /mnt/<drive>.
# execute from the repo root inside the WSL shell.

set -euo pipefail

echo "Configuring WSL environment for Jarvis..."

# ensure Python and node exist
sudo apt update && sudo apt install -y python3 python3-venv python3-pip nodejs npm git curl

# create backend virtualenv and install
./scripts/setup-backend.sh

# frontend dependencies
cd frontend
npm install
cd -

echo "WSL environment ready. Use 'npm run dev' in frontend and 'uvicorn backend.app.main:app' in backend."