# JARVIS 5.0 — Structure Audit

## What I found

### Clear redundancy / aliasing
- `frontend/context/JarvisContext.tsx` is only a backward-compat re-export of `frontend/lib/context/jarvis-context.tsx`.
- `frontend/hooks/useVoice` is imported by the app, but the actual implementation lives in `frontend/hooks/use-voice.ts`.
  - Added a small compatibility shim so both paths work.

### Likely orphan / archive folders
These look like historical or research material rather than runtime code:
- `FUTURE_IMPLEMENTATIONS/`
- `OMEGA_RESEARCH/`
- `PROJECT_SOPHISTICATION/`

### Runtime folders that should stay distinct
- `backend/` → Python API/runtime
- `frontend/` → Next.js UI/runtime
- `scripts/` → launch/diagnostic scripts
- `tests/` and `backend/app/tests/` → keep test ownership explicit
- `docs/` → user-facing documentation and architecture notes
- `src/` → shared/core TypeScript/Python support code

## Safe organization moves

### 1) Normalize hook naming in frontend
Keep implementation files in one convention and add thin shims only when imports already depend on the old path.

### 2) Keep research archives out of runtime paths
If these folders are historical notes, mark them clearly as archive/reference so they don't look like active app code.

### 3) Reduce split test ownership where possible
There are backend tests in both:
- `backend/app/tests/`
- `tests/`

That can be confusing; if no import paths depend on it, prefer one canonical test home per runtime.

### 4) Clarify `docker/` vs root `docker-compose.yml`
There are duplicate Docker entrypoints:
- `docker-compose.yml`
- `docker/docker-compose.yml`

Treat the root file as canonical; keep the nested file as historical/reference only.

Prefer one canonical compose file and keep the other as a thin reference, if needed.

## Recommendation
Best low-risk next step:
1. Keep current code layout.
2. Add compatibility shims for naming mismatches.
3. Move/archive only clearly historical folders after confirming nothing imports them.
