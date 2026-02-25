#!/usr/bin/env bash
# start backend and frontend in separate terminals (requires tmux or use two shells)
echo "Starting backend..."
bash scripts/run-backend.sh &

echo "Starting frontend..."
bash scripts/run-frontend.sh &

wait