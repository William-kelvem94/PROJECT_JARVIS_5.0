import sys
from pathlib import Path

from watchfiles import run_process
from watchfiles.filters import PythonFilter

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT))


def start_worker() -> None:
    # O agents_worker.py foi descontinuado na migração para arquitetura nativa (Fase 2).
    # Agora utilizamos o próprio Uvicorn com hot-reload para o desenvolvimento.
    import uvicorn
    print("[DevWorker] Iniciando Backend Jarvis v5.0 com Auto-Reload...")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == '__main__':
    start_worker()
