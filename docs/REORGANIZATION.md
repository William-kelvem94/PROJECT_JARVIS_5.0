# JARVIS 5.0 — Mapa de Reorganização

## Estratégia

Novos subdiretórios com `__init__.py` que re-exportam dos arquivos originais.
Os arquivos originais **não são movidos** — zero breaking changes.

---

## Nova Hierarquia de Módulos (Facades)

### `app.brain` — Módulos de Raciocínio

```python
from app.brain import brain            # singleton EngineerBrain
from app.brain import EngineerBrain    # classe
from app.brain import SmartRouter      # classe orquestrador LLM
from app.brain import router           # singleton SmartRouter
from app.brain import AutonomousBrain  # classe
from app.brain import autonomous_brain # singleton
from app.brain import NativeBrain      # classe (llama-cpp-python)
from app.brain import get_native_brain # factory function
```

Arquivos originais: `engineer_brain.py`, `smart_router.py`, `autonomous_brain.py`, `native_brain.py`

---

### `app.core` — Pipeline e Persona

```python
from app.core import chat_stream, chat_reply      # pipeline de chat
from app.core import persona                       # singleton PersonaManager
from app.core import PersonaManager               # classe
from app.core import AGENT_INSTRUCTION            # prompt de sistema
from app.core import SESSION_INSTRUCTION          # instrução de sessão
from app.core import load_kb                      # carrega Knowledge Base
```

Arquivos originais: `chat_pipeline.py`, `persona.py`, `prompts.py`, `kb_loader.py`

---

### `app.memory` — Memória Unificada

```python
from app.memory import memory          # singleton UnifiedMemory
from app.memory import UnifiedMemory   # classe (SQLite + ChromaDB + Markdown)
```

Arquivo original: `unified_memory.py`

---

### `app.api` — Rotas e Servidores

```python
from app.api import system_bridge_router   # APIRouter prefixo /system
from app.api import voice_router           # APIRouter WebSocket /ws/voice
from app.api import broadcast_state        # envia status ao HUD
from app.api import broadcast_chunk        # envia chunk de resposta ao HUD
from app.api import telemetry_app          # FastAPI app do dashboard
from app.api import start_telemetry_server # inicia dashboard na porta 8001
```

Arquivos originais: `system_bridge.py`, `voice_websocket.py`, `telemetry_server.py`

---

### `app.security` — Segurança (já subdiretório)

```python
from app.security.sentinel_parser import SentinelParser
from app.security.sentinel_core import SentinelSecurity
from app.security.blackbox import BlackBox
from app.security.biometric_vault import BiometricVault
from app.security.holodeck import HoloDeck
```

---

### `app.voice` — Voz (já subdiretório)

```python
from app.voice.tts_engine import tts_engine
from app.voice.barge_in import barge_in
```

---

### `app.psyche` — Psique (já subdiretório)

```python
from app.psyche.device_awareness import DeviceAwareness
from app.psyche.dream_cycle import DreamCycle
from app.psyche.gap_analyzer import GapAnalyzer
```

---

### `app.perception` — Percepção (já subdiretório)

```python
from app.perception.perception_manager import perception_manager
from app.perception.voice_engine import voice_engine
from app.perception.object_engine import object_engine
from app.perception.face_engine import face_engine
from app.perception.gesture_engine import gesture_engine
```

---

## Backward Compatibility

Todos os imports antigos continuam funcionando sem alteração:

```python
from app.engineer_brain import brain        # ainda funciona
from app.smart_router import SmartRouter    # ainda funciona
from app.chat_pipeline import chat_stream   # ainda funciona
from app.unified_memory import memory       # ainda funciona
from app.system_bridge import router        # ainda funciona
```

---

## Arquivos Criados

| Arquivo                        | Descrição                                   |
|-------------------------------|---------------------------------------------|
| `backend/app/brain/__init__.py`  | Fachada para raciocínio e LLM              |
| `backend/app/core/__init__.py`   | Fachada para pipeline, persona e KB        |
| `backend/app/memory/__init__.py` | Fachada para memória unificada             |
| `backend/app/api/__init__.py`    | Fachada para routers e servidores FastAPI  |

---

## Notas de Implementação

- `app.brain.router` e `app.api.voice_router` são instâncias de `APIRouter` distintas.
- `app.brain.native_brain` começa como `None`; usar `get_native_brain()` para instanciação lazy.
- `app.api.telemetry_app` é uma app FastAPI separada que roda na porta 8001.
- `app.core.persona` é um singleton de `PersonaManager` (não `JarvisPersona`).
