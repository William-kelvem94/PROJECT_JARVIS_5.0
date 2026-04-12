import sys
from pathlib import Path

base_dir = Path(__file__).resolve().parents[1]
project_root = base_dir.parent
sys.path.insert(0, str(project_root))

from livekit.agents import cli, WorkerOptions
from src.core.agents import entrypoint

if len(sys.argv) == 1:
    sys.argv = [sys.argv[0], "start"]

cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, load_threshold=0.95))
print("Worker rodando! Agent pronto para rooms.")
