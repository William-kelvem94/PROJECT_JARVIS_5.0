# system_config.py
# Configuration file for JARVIS 5.0 Ecosystem
import os
import sys

# Detect OS
is_windows = os.name == 'nt'

# Define recognized command aliases based on OS
if is_windows:
    COMMAND_ALIASES = {
        "notepad": ["notepad", "write", "code"],
        "list_files": ["dir", "ls"],
        "create_file": ["type nul >", "echo. >"]
    }
    # Windows path separator
    os.environ["PATH"] += f";{os.getcwd()}"
else:
    COMMAND_ALIASES = {
        "notepad": ["nano", "vi", "vim", "gedit"],
        "list_files": ["ls", "dir"],
        "create_file": ["touch"]
    }
    os.environ["PATH"] += ":/usr/bin:/bin"

print(f"System configuration patched for {os.name} command execution.")