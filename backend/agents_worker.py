#!/usr/bin/env python3
"""
JARVIS 5.0 - LiveKit Agent Worker (Entry point CLI)
Execute: python backend/agents_worker.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
from livekit.agents import cli, WorkerOptions
from app.agents import entrypoint

load_dotenv(override=True)

if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
        )
    )

