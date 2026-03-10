#!/usr/bin/env bash
# create virtual environment and install packages
# compatible with Linux (WSL) and macOS; on Windows powershell run
# `python -m venv .venv && .\.venv\Scripts\Activate.ps1` manually.
python -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r backend/app/requirements.txt

# optional: install playwright browsers if running from WSL
python -m playwright install

