#!/bin/bash
# JARVIS 5.0 Startup Script

# Ensure we are in the project root
cd "$(dirname "$0")"

echo "Starting JARVIS 5.0..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 not found"
    exit 1
fi

# Check dependencies
python3 scripts/install/setup_jarvis.py --quick-check
if [ $? -ne 0 ]; then
    echo "Dependencies missing or check failed. Running full setup..."
    # Use --no-scripts to prevent overwriting this script while running
    python3 scripts/install/setup_jarvis.py --no-scripts
    if [ $? -ne 0 ]; then
        echo "Error: Setup failed. Please check the logs and try again."
        exit 1
    fi
fi

# Start JARVIS
python3 main.py "$@"
