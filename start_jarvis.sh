#!/bin/bash
# JARVIS 5.0 Startup Script

echo "Starting JARVIS 5.0..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 not found"
    exit 1
fi

# Check dependencies
python3 scripts/install/setup_jarvis.py --quick-check

# Start JARVIS
python3 main.py "$@"
