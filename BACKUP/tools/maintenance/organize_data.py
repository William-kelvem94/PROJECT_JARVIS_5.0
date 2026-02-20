import os
import shutil
from pathlib import Path

# Base paths
ROOT = Path(r"c:\Users\willi\Documents\GitHub\PROJECT_JARVIS_5.0")
DATA = ROOT / "data"

# Subdirectories
LOGS = DATA / "logs"
CACHE = DATA / "cache"
DB = DATA / "database"
MEMORY = DATA / "memory"
VISION = DATA / "vision"
AUDIO = DATA / "audio"
SYSTEM = DATA / "system"
TESTS = DATA / "tests"
BACKUPS = DATA / "backups"


def safe_move(src, dst):
    if not src.exists():
        return

    dst.parent.mkdir(parents=True, exist_ok=True)

    try:
        if src.is_dir():
            if dst.exists():
                # Merge contents
                for item in src.iterdir():
                    target = dst / item.name
                    if target.exists():
                        if target.is_dir():
                            shutil.copytree(item, target, dirs_exist_ok=True)
                        else:
                            os.remove(target)
                            shutil.move(str(item), str(target))
                    else:
                        shutil.move(str(item), str(target))
                src.rmdir()
            else:
                shutil.move(str(src), str(dst))
        else:
            if dst.exists():
                os.remove(dst)
            shutil.move(str(src), str(dst))
        print(f"[OK] Moved {src.relative_to(ROOT)} -> {dst.relative_to(ROOT)}")
    except Exception as e:
        print(f"[ERROR] Failed to move {src.name}: {e}")


if __name__ == "__main__":
    print("Starting Data Reorganization...")

    # Create dirs
    for d in [LOGS, CACHE, DB, MEMORY, VISION, AUDIO, SYSTEM, TESTS, BACKUPS]:
        d.mkdir(parents=True, exist_ok=True)

    # 1. Logs
    safe_move(DATA / "jarvis.log", LOGS / "jarvis.log")
    safe_move(DATA / "jarvis_singularity.log", LOGS / "jarvis_singularity.log")
    safe_move(DATA / "EVOLUTION.log", LOGS / "EVOLUTION.log")

    # 2. Database
    safe_move(DATA / "jarvis.db", DB / "jarvis.db")
    safe_move(DATA / "feedback.db", DB / "feedback.db")

    # 3. Cache
    safe_move(DATA / "cache.metadata", CACHE / "metadata.cache")
    safe_move(DATA / "identity_cache.json", CACHE / "identity.json")
    safe_move(DATA / "audio_cache", CACHE / "audio")

    # 4. System
    safe_move(DATA / "system_health.json", SYSTEM / "health.json")
    safe_move(DATA / "system_reports", SYSTEM / "reports")
    safe_move(DATA / "monitoring", SYSTEM / "monitoring")
    safe_move(DATA / "recovery", SYSTEM / "recovery")

    # 5. Vision (Move to VISION)
    safe_move(DATA / "captures", VISION / "captures")
    safe_move(DATA / "processed", VISION / "processed")
    safe_move(DATA / "faces", VISION / "faces")
    safe_move(DATA / "screenshots", VISION / "screenshots")

    # 6. Audio
    safe_move(DATA / "voice", AUDIO / "voice")
    safe_move(DATA / "voice_signatures", AUDIO / "signatures")
    # Don't move 'audio' if it's the same as 'AUDIO_DIR'
    if (DATA / "audio").exists() and (DATA / "audio") != AUDIO:
        safe_move(DATA / "audio", AUDIO / "recordings")

    # 7. Memory (Consolidate in MEMORY)
    safe_move(DATA / "chroma_db", MEMORY / "chroma_db")
    safe_move(DATA / "memories", MEMORY / "short_term")
    safe_move(DATA / "knowledge", MEMORY / "knowledge")
    safe_move(DATA / "learning", MEMORY / "learning")
    safe_move(DATA / "neural_memory", MEMORY / "neural")

    # 8. Tests
    safe_move(DATA / "test_chromadb", TESTS / "chromadb")
    safe_move(DATA / "test_images", TESTS / "images")
    if (DATA / "tests").exists() and (DATA / "tests") != TESTS:
        safe_move(DATA / "tests", TESTS / "legacy_data")

    print("\nCleanup finished.")
