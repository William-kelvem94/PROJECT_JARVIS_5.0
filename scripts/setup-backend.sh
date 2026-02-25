#!/usr/bin/env bash
# create virtual environment and install packages
python -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r backend/app/requirements.txt
