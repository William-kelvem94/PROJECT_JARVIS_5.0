import sys
from pathlib import Path

base_dir = Path(__file__).resolve().parents[1]
project_root = base_dir.parent
sys.path.insert(0, str(project_root))

from livekit.agents import cli, WorkerOptions
from src.core.agents import entrypoint

cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
print("Worker rodando! Agent pronto para rooms.")
