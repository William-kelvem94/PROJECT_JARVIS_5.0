#!/usr/bin/env bash
# activate venv and start uvicorn
source venv/bin/activate
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
