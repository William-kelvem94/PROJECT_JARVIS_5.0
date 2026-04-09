import sys
from pathlib import Path

from watchfiles import run_process

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT))


def start_worker() -> None:
    import agents_worker
    sys.argv = ['agents_worker.py', 'start']
    agents_worker.cli.run_app(agents_worker.WorkerOptions(entrypoint_fnc=agents_worker.entrypoint))


if __name__ == '__main__':
    print("[DevWorker] Watching backend files and restarting on change...")
    run_process(
        '.',
        target=start_worker,
        target_type='function',
        watch_filter='python',
        ignore_permission_denied=True,
        recursive=True,
        grace_period=0.5,
    )
