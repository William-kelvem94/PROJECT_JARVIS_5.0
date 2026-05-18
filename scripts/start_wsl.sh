#!/usr/bin/env bash
# start backend and frontend in WSL and log output
cd "$(dirname "$0")/.." || exit 1
source venv/bin/activate
mkdir -p logs
nohup uvicorn backend.app.main:app --reload --host 0.0.0.0 --log-level info > logs/uvicorn.log 2>&1 &
echo "backend started with PID $!"
cd frontend || exit 1
nohup npm run dev > ../logs/frontend.log 2>&1 &
echo "frontend started with PID $!"
