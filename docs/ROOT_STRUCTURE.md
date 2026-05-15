# Root Structure

This is the canonical organization for `PROJECT_JARVIS_5.0`.

## Runtime

- `backend/` - FastAPI backend, perception, memory, security, health checks, and voice runtime.
- `frontend/` - Next.js cockpit UI.
- `scripts/` - Windows launch, setup, diagnostics, and support scripts.
- `docker-compose.yml` - canonical compose entrypoint from the repository root.
- `docker/` - secondary Docker assets and alternate compose definitions.
- `start-jarvis.bat` - root launcher shim for double-click startup.
- `start.bat` - legacy root alias for `start-jarvis.bat`.

## Configuration

- `.env` - primary local backend configuration. Do not commit real secrets.
- `.env.example` - root environment template.
- `.dockerignore`, `.flake8`, `.gitattributes`, `.gitignore` - tool configuration files expected at repo root.
- `package.json`, `pnpm-lock.yaml`, `pnpm-workspace.yaml`, `pyrightconfig.json` - workspace/package/type-check metadata expected at repo root.
- `env/` - optional local environment profiles and examples.
- `frontend/.env.example` - frontend-only public variables.
- `config/` - static project configuration.

## Data And Models

- `data/` - local runtime data, memory, captures, and knowledge mirrors.
- `backend/data/` - backend-owned local persistence.
- `backend/models/` - heavy ML model files such as `yolov8n.pt`.
- `logs/` - generated runtime logs.

## Documentation And Archives

- `docs/` - active documentation, installation notes, architecture, audits, and reports.
- `docs/guides/` - quick-start, health, connectivity, hardware, and troubleshooting guides.
- `docs/reports/` - executive summaries and status reports.
- `docs/audits/` - technical audits and laudos.
- `docs/archive/research/` - historical research/prototype material that is not active runtime.

## Development Support

- `tests/` - root-level tests.
- `backend/app/tests/` - backend package tests.
- `src/` - shared/core support code kept outside app runtimes.
- `tools/` - utility scripts. Downloaded installers are generated artifacts and should not be kept.
- `ci/` and `.github/` - CI/CD support.

## Generated Or Disposable

These should stay out of source control and can be regenerated:

- `.venv/`, `node_modules/`, `frontend/node_modules/`
- `.next/`, `frontend/.next/`, `.pytest_cache/`, `__pycache__/`
- `.venv.broken-*`, `backend/venv.broken-*`
- `debug/`, `temp_audio/`, `backend/temp_audio/`, `tools/installers/`

If a generated folder appears in the root and is not listed above, classify it before wiring code to
it. The root should remain mostly entrypoints, package metadata, config templates, and runtime
directories.
