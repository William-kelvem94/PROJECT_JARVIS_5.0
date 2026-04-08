@echo off
cd /d %~dp0
call venv\Scripts\activate.bat
pip install -r app/requirements.txt
python -c "from app.agents import entrypoint; from livekit.agents.cli import run_app; from livekit.agents import WorkerOptions; run_app(WorkerOptions(entrypoint_fnc=entrypoint))"
pause
