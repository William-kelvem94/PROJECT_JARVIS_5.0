@echo off
cd /d %~dp0
call venv\Scripts\activate.bat
pip install -r app/requirements.txt
python -c "import sys; sys.argv = ['-c', 'start']; from src.core.agents import entrypoint; from livekit.agents.cli import run_app; from livekit.agents import WorkerOptions; run_app(WorkerOptions(entrypoint_fnc=entrypoint))"
pause
