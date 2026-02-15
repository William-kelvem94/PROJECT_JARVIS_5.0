import sys
import os
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.core.management.maintenance_manager import maintenance_manager

def on_progress(msg):
    print(f"[UI UPDATE] {msg}")

maintenance_manager.on_progress = on_progress

print("=== STARTING SELF-HEALING TEST ===")
maintenance_manager.check_and_repair_all()
print("=== SELF-HEALING TEST COMPLETED ===")
