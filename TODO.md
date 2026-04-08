# TODO: Fix Pylance Errors in PROJECT_JARVIS_5.0

## Plan Progress Tracker

### 1. [ ] Setup Virtual Environment (backend/app/)
   - cd backend/app
   - python -m venv venv
   - venv\Scripts\activate (Windows)

### 2. [x] Install Dependencies (run manually: cd backend/app && venv\\Scripts\\activate && pip install -r requirements.txt mem0ai pydantic-settings)
   - pip install -r requirements.txt mem0ai pydantic-settings

### 3. [x] Fix src/core/agents.py (removed unused imports: noise_cancellation, RoomInputOptions; fixed mem0ai import)
   - Add imports: from .prompts import AGENT_INSTRUCTION, SESSION_INSTRUCTION
   - Import mem0ai
   - Remove unused: RoomInputOptions, noise_cancellation
   - Add type ignores where needed

### 4. [ ] Migrate config/settings.py to Pydantic V2
   - Replace @validator with @field_validator
   - pip install pydantic-settings already in step 2

### 5. [ ] Clean unused imports
   - main.py: remove unused settings
   - routes.py: remove unused entrypoint
   - system_tools.py: minor fixes

### 6. [ ] Test & Verify
   - Reload VSCode window
   - pip list | grep -E 'livekit|loguru|mem0|GPUtil'
   - uvicorn app.main:app --reload
   - Check Pylance errors gone

### Next: Mark as [x] when complete, then attempt_completion

