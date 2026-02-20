from src.core.management.maintenance_manager import maintenance_manager
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def on_progress(msg):
    print(f"[UI UPDATE] {msg}")


maintenance_manager.on_progress = on_progress

print("=== STARTING SELF-HEALING TEST ===")
maintenance_manager.check_and_repair_all()
print("=== SELF-HEALING TEST COMPLETED ===")
