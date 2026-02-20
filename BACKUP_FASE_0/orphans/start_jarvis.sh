#!/bin/bash
# Compatibility shim — forwards to centralized launcher in scripts/launchers
exec "$(dirname "$0")/scripts/launchers/start_jarvis.sh" "$@"
