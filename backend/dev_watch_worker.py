import os
import sys
from pathlib import Path

from watchfiles import run_process

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT))

if __name__ == '__main__':
    os.chdir(str(BASE_DIR))
    python_path = sys.executable.replace('\\', '/')
    target = f'"{python_path}" "{BASE_DIR / "agents_worker.py"}" start'

    print(f"[DevWorker] Watching backend files and restarting on change...")
    run_process(
        '.',
        target=target,
        target_type='command',
        watch_filter='python',
        ignore_permission_denied=True,
        recursive=True,
        grace_period=0.5,
    )
