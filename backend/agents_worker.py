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

# Explicitly set the path to avoid DLL loading issues
import os
ffi_path = base_dir / "venv" / "Lib" / "site-packages" / "livekit" / "rtc" / "resources" / "livekit_ffi.dll"
if ffi_path.exists():
    os.environ["LIVEKIT_LIB_PATH"] = str(ffi_path)

if __name__ == "__main__":
    if len(sys.argv) == 1:
        sys.argv = [sys.argv[0], "start"]

    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            load_threshold=0.95
        )
    )

