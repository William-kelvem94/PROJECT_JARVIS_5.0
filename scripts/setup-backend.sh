#!/usr/bin/env bash
# create virtual environment and install packages
# compatible with Linux (WSL) and macOS; on Windows powershell run
# `python -m venv .venv && .\.venv\Scripts\Activate.ps1` manually.
python3 -m venv venv
source venv/bin/activate
# ensure pip is available in venv
python3 -m pip install --upgrade pip
python3 -m pip install -r backend/app/requirements.txt

# optional: install playwright browsers if running from WSL
python3 -m playwright install

