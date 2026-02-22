# system_config.py
# Configuration file for JARVIS 5.0 Ecosystem

import os

# Define recognized command aliases for opening notepad/text editor
# This patch ensures multiple common commands are recognized
COMMAND_ALIASES = {
    "notepad": ["gedit", "xed", "nano", "vi", "code"],
    "list_files": ["ls", "dir"],
    "create_file": ["touch"]
}

# Environment patch to ensure command execution paths are respected
os.environ["PATH"] += ":/usr/bin:/bin"

print("System configuration patched for command execution.")