@echo off
cd /d "c:\Users\willi\Documents\GitHub\PROJECT_JARVIS_5.0\backend"
call venv\Scripts\activate
python -c "import sys; sys.path.insert(0, '.'); from livekit.agents.cli import run_app; from app.agents import entrypoint; run_app(livekit.agents.WorkerOptions(entrypoint_fnc=entrypoint))"
pause
