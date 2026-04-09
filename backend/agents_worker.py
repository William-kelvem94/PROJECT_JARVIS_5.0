#!/usr/bin/env python3
"""
JARVIS 5.0 - LiveKit Agent Worker (Entry point CLI)
Execute: python backend/agents_worker.py
"""

import sys
from pathlib import Path

base_dir = Path(__file__).resolve().parents[1]  # backend
project_root = base_dir.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(base_dir))

from dotenv import load_dotenv
from livekit.agents import cli, WorkerOptions
from src.core.agents import entrypoint

load_dotenv(project_root / '.env', override=False)
load_dotenv(project_root / 'env' / '.env', override=True)

if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
        )
    )

