@echo off
cd /d "c:\Users\willi\Documents\GitHub\PROJECT_JARVIS_5.0\backend"
call venv\Scripts\activate
python -c "
import sys
sys.path.insert(0, '.')
from app.agents import entrypoint
from livekit.agents import cli
cli.run_app(cli.WorkerOptions(entrypoint_fnc=entrypoint))
"
pause

