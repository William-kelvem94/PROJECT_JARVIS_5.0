# JARVIS 5.0 Structure Audit

## Current Classification

### Canonical runtime
- `backend/` - Python API/runtime.
- `frontend/` - Next.js cockpit.
- `scripts/` - launch, setup, diagnostics, and maintenance scripts.
- `docker-compose.yml` - root compose entrypoint.
- `docker/` - supporting Docker assets and alternate compose file.

### Runtime data and local assets
- `.venv/` - active Python virtual environment.
- `node_modules/` and `frontend/node_modules/` - local Node dependencies.
- `data/` and `backend/data/` - runtime persistence and knowledge mirrors.
- `backend/models/` - heavy ML models, including `yolov8n.pt`.
- `logs/` - generated logs; only `.gitkeep` should be kept in Git.

### Archive/reference
- `docs/archive/research/FUTURE_IMPLEMENTATIONS/`
- `docs/archive/research/OMEGA_RESEARCH/`
- `docs/archive/research/PROJECT_SOPHISTICATION/`

These are historical research/prototype folders and are not part of the active runtime.

## Cleanup Completed

- Removed stale root virtual environments:
  - `.venv.broken-20260507012850/`
  - `.venv.broken-official-20260507080330/`
- Removed stale backend virtual environment:
  - `backend/venv.broken-20260507012850/`
- Removed generated caches and temporary folders:
  - `.next/`
  - `.pytest_cache/`
  - `backend/.pytest_cache/`
  - `backend/__pycache__/`
  - `debug/`
  - `temp_audio/`
  - `backend/temp_audio/`
  - `tools/installers/`
- Moved research folders into `docs/archive/research/`.
- Moved `yolov8n.pt` from the root into `backend/models/`.

## Preventive Changes

- `scripts/setup-venv.bat` now removes old `.venv.broken-*` backups by default before recreating a venv.
- Set `JARVIS_KEEP_BROKEN_VENVS=1` only when you intentionally want to preserve a broken environment for debugging.
- Backend object detection now looks for `yolov8n.pt` in `backend/models/` or `JARVIS_MODELS_PATH`.
- Root structure is documented in `docs/ROOT_STRUCTURE.md`.

## Known Local Issue

- The active `.venv/` still exists but its `pyvenv.cfg` points to
  `C:\Users\willi\AppData\Local\Programs\Python\Python311\python.exe`.
- In this shell that base interpreter is unavailable, so `.venv\Scripts\python.exe` cannot start.
- The environment was preserved because deleting it without a working Python runtime would make backend recovery harder.
- Recommended recovery: install/restore Python 3.11, then recreate with `JARVIS_FORCE_RECREATE_VENV=1 start-jarvis.bat`.

## Remaining Intentional Root Files

The root now keeps only repository/tool metadata and launch shims:

- Tool files: `.dockerignore`, `.env`, `.env.example`, `.flake8`, `.gitattributes`, `.gitignore`.
- Workspace metadata: `package.json`, `pnpm-lock.yaml`, `pnpm-workspace.yaml`, `pyrightconfig.json`.
- Canonical project files: `README.md`, `LICENSE`, `docker-compose.yml`.
- User-facing launch shims: `start-jarvis.bat`, `start.bat`.

Quick guides, reports, audits, and utility scripts were moved into `docs/` and `scripts/`.
