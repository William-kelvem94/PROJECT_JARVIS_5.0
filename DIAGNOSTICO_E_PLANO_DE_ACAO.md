# JARVIS 5.0 — Diagnóstico Completo e Plano de Ação

> Gerado em: 2026-05-17
> Escopo: Análise completa do PROJECT_JARVIS_5.0 (1090 commits, ~23k linhas)

---

## Sumário Executivo

O PROJECT_JARVIS_5.0 **NÃO FUNCIONA** por 4 causas raiz:

1. **Python 3.11 não instalado + `.venv` ausente + zero dependências instaladas**
2. **`ENABLE_PERCEPTION=false` no `.env`** desativa voz/visão/câmera
3. **WebSocket binário nunca foi implementado** — a migração do LiveKit removeu o streaming de áudio mas não criou substituto
4. **Mix tóxico threading + asyncio** no `voice_engine.py` — cria event loop novo a cada comando de voz

Comparação com o protótipo original (Jarvis-main, 125 linhas):
- **Jarvis-main**: LiveKit + Gemini Realtime = 1 modelo fazia STT+LLM+TTS+VAD, tudo cloud, funcionava
- **PROJECT_JARVIS_5.0**: 23x mais código, zero funcionalidade de voz — pipeline de áudio incompleto

---

## 1. voice_engine.py — 7 Bugs Críticos

| # | Bug | Linha | Impacto |
|---|-----|-------|---------|
| 1 | `_fire()` **nunca é chamado** — sistema de callbacks é dead code | 347-352 | `_on_voice_event` do perception_manager nunca executa |
| 2 | Speaker ID em chunk de 0.5s **sempre falha** (precisa ≥1s) | 459 vs 282 | Wake word bloqueada para todos os speakers |
| 3 | `asyncio.new_event_loop()` cria/destroi loop a cada chamada | 481, 513 | Vazamento de recursos + WebSocket called no loop errado |
| 4 | STT bloqueante deixa o sistema **surdo** durante transcrição | 429 | Perde áudio enquanto transcreve |
| 5 | DeepFilterNet roda em **cada chunk** de 0.5s | 444 | CPU pesado mesmo em idle |
| 6 | `ThreadPoolExecutor` duplicado e nunca shut down | 30, 362 | Threads órfãos |
| 7 | `_voice_buffer` sem limite — **OOM potencial** | 409 | Crash em ruído contínuo |

### Detalhes

#### Bug 1: `_fire()` nunca chamado
```python
# voice_engine.py:339-352
_callbacks: List[Callable[[VoiceResult], None]] = []

def add_callback(fn):
    _callbacks.append(fn)

def _fire(result: VoiceResult):
    for cb in _callbacks:
        try:
            cb(result)
        except Exception as e:
            logger.error(f"[VoiceEngine] Callback error: {e}")
```
`_fire()` é definido mas **nunca invocado** em nenhum lugar do arquivo. Isso significa que:
- `main.py:46` registra `perception_manager._on_voice_event` como callback
- Mas o callback nunca é disparado
- Toda a "Blindagem Sensorial" do perception_manager é dead code

#### Bug 2: Speaker ID em chunk de 0.5s
```python
# voice_engine.py:459 — chunk de 0.5s (8000 samples a 16kHz)
speaker, conf = identify_speaker(chunk_cleaned)

# voice_engine.py:282 — precisa de pelo menos 1 segundo
if len(wav) < SAMPLE_RATE:  # SAMPLE_RATE = 16000
    return None, 0.0
```
O chunk do wake word tem apenas 8000 samples (0.5s), mas `identify_speaker` rejeita qualquer áudio menor que 16000 samples (1s). **Resultado: speaker validation SEMPRE falha.**

#### Bug 3: `asyncio.new_event_loop()` em thread
```python
# voice_engine.py:476-485
def _notify_hud(status, transcript="", response=""):
    try:
        from app.voice_websocket import broadcast_state
        loop = asyncio.new_event_loop()       # NOVO loop a cada chamada
        loop.run_until_complete(broadcast_state(status, transcript, response))
        loop.close()
    except Exception:
        pass  # Se der erro, loop.close() nunca é chamado → LEAK
```
Problemas:
- Cria um event loop novo a cada notificação (caro)
- Se `broadcast_state` falhar, o loop vaza recursos
- O WebSocket do FastAPI está bound ao loop principal do uvicorn — chamar de outro loop é undefined behavior

#### Bug 4: STT bloqueante
```python
# voice_engine.py:429 — roda dentro do _audio_loop() (thread principal de áudio)
transcript = transcribe_offline(segment)
```
`whisper.transcribe()` é uma chamada bloqueante que pode levar segundos. Enquanto transcreve, **o sistema fica surdo** — não detecta wake word nem captura áudio.

#### Bug 5: DeepFilterNet em cada chunk
```python
# voice_engine.py:444
chunk_cleaned = _apply_noise_suppression(chunk)  # DeepFilterNet neural net
```
DeepFilterNet é uma rede neural pesada. Rodar em cada chunk de 0.5s mesmo durante idle causa CPU usage desnecessário.

#### Bug 6: ThreadPoolExecutor duplicado
```python
# voice_engine.py:30
_command_executor = ThreadPoolExecutor(max_workers=4)
# ...
# voice_engine.py:362 — DUPLICADO!
_command_executor = ThreadPoolExecutor(max_workers=4)
```
O primeiro é orphanado e nunca usado. Nenhum dos dois é nunca shut down.

#### Bug 7: `_voice_buffer` sem limite
```python
# voice_engine.py:409
_voice_buffer.append(chunk)  # Cresce indefinidamente
```
Se VAD nunca detecta silêncio (ruído contínuo), o buffer cresce até OOM.

---

## 2. WebSocket — JSON-only, Zero Áudio Binário

| Componente | Status |
|------------|--------|
| WebSocket endpoint definido | Sim — `/ws/voice` |
| JSON status server → client | Sim — `idle`, `listening`, `thinking`, `speaking` |
| JSON text chunks server → client | Sim — `response_chunk` |
| Manual trigger client → server | Sim — `manual_trigger` |
| **Áudio binário browser → server** | **NÃO IMPLEMENTADO** |
| **Áudio binário server → browser** | **NÃO IMPLEMENTADO** |
| **Mic do browser enviado ao server** | **NÃO** — captura mas nunca manda |
| **TTS streamado pro browser** | **NÃO** — toca nos speakers do servidor via pygame |
| LiveKit no codebase | **Removido completamente** |

### Backend (`voice_websocket.py`)
- `receive()` — usa texto, NÃO `receive_bytes()`
- `send_json()` — só envia JSON status
- **Zero `send_bytes()` no código**

### Frontend (`jarvis-context.tsx`)
- `ws.binaryType = 'arraybuffer'` — configurado mas inútil
- Handler binário existe mas **nunca recebe dados**
- `getUserMedia` captura mic mas **nunca envia chunks ao server**
- `ScriptProcessorNode` declarado mas **nunca conectado**

### Frontend (`use-voice.ts`)
- `if (typeof event.data !== 'string') { return; }` — **ignora binário explicitamente**
- Só envia: `JSON.stringify({ type: "manual_trigger" })`

---

## 3. Configuração — `.env` Desativa Funcionalidade Core

### `backend/.env`
```
GEMINI_API_KEY=AIzaSyCL...
OPENROUTER_API_KEY=sk-or-v1-0ec054...
DEBUG_MODE=true
ENABLE_PERCEPTION=false    ← CRÍTICO: desativa voz/câmera/visão
```

### `backend/app/config.py`
| Setting | Valor | Impacto |
|---------|-------|---------|
| `DEVICE_TYPE` | `cpu` | Sem GPU |
| `GPU_ENABLED` | `False` | Toda inferência em CPU |
| `LOW_VRAM_MODE` | `True` | Perfil conservativo |
| `OLLAMA_ENABLED` | `False` | LLM local desativado |
| `ENABLE_GC` | `False` | GC otimização desligada |

---

## 4. Dependências — 35 Mortas, 1 Faltando, Zero `.venv`

### Virtual Environment
| Caminho | Existe? |
|---------|---------|
| `backend/.venv` | **NÃO** |
| `backend/app/.venv` | **NÃO** |

### Backend — Dead Dependencies (7)
| Pacote | Status |
|--------|--------|
| `requests` | Listado, nunca importado |
| `Pillow` | Listado, nunca importado |
| `webrtcvad-wheels` | Listado, nunca importado |
| `librosa` | Listado, nunca importado |
| `faiss-cpu` | Listado, nunca importado |
| `pytest-asyncio` | Listado, nunca importado |
| `pytest-mock` | Listado, nunca importado |
| `httpx` | Listado, nunca importado |
| `torchvision` | Listado, nunca importado |
| `torchaudio` | Listado, nunca importado |
| `mem0ai` | Listado, nunca importado |

### Backend — Missing Dependency (1)
| Pacote | Usado em | Status |
|--------|----------|--------|
| `resemblyzer` | `voice_engine.py` (4 imports) | **Não está nos requirements** |

### Frontend — Dead Dependencies (23)
| Pacote | Status |
|--------|--------|
| `@radix-ui/react-collapsible` | Nunca importado |
| `@radix-ui/react-dialog` | Nunca importado |
| `@radix-ui/react-dismissable-layer` | Nunca importado |
| `@radix-ui/react-dropdown-menu` | Nunca importado |
| `@radix-ui/react-hover-card` | Nunca importado |
| `@radix-ui/react-popover` | Nunca importado |
| `@radix-ui/react-scroll-area` | Nunca importado |
| `@radix-ui/react-use-controllable-state` | Nunca importado |
| `@rive-app/react-webgl2` | Nunca importado |
| `@xyflow/react` | Nunca importado |
| `ai` | Nunca importado |
| `cmdk` | Nunca importado |
| `embla-carousel-react` | Nunca importado |
| `jose` | Nunca importado |
| `media-chrome` | Nunca importado |
| `nanoid` | Nunca importado |
| `shiki` | Nunca importado |
| `streamdown` | Nunca importado |
| `three` | Nunca importado |
| `tokenlens` | Nunca importado |
| `vanta` | Nunca importado |
| `@testing-library/user-event` | Nunca importado |
| `tw-animate-css` | Nunca importado |

### Conflitos de Versão
| Conflito | Detalhe |
|----------|---------|
| `pydantic-settings` | `requirements-base.txt` (sem versão) vs `requirements.txt.mem0` (==2.5.2) |
| `faiss-cpu` vs CUDA | Se usar `requirements-torch-cu118.txt`, deveria usar `faiss-gpu` |
| `next` vs `eslint-config-next` | 15.5.9 vs 15.5.2 (minor mismatch) |

---

## Plano de Ação — 5 Fases

### Fase 1 — Corrigir o Básico (1-2h)

- [ ] `ENABLE_PERCEPTION=true` no `backend/.env`
- [ ] Criar `.venv`: `python -m venv backend/.venv`
- [ ] Limpar `requirements-base.txt` — remover 11 deps mortas
- [ ] Limpar `requirements-torch-cpu.txt` — remover `torchvision`, `torchaudio`
- [ ] Remover `requirements.txt.mem0` (mem0ai não é usado)
- [ ] Adicionar `resemblyzer` aos requirements
- [ ] Limpar `package.json` frontend — remover 23 deps mortas
- [ ] Instalar dependências: `pip install -r backend/app/requirements.txt`

### Fase 2 — Corrigir voice_engine.py (3-4h)

- [ ] Conectar `_fire()` ao pipeline de áudio (chamar quando wake word detectada)
- [ ] Corrigir speaker ID: acumular chunks até ter ≥1s antes de chamar `identify_speaker()`
- [ ] Substituir `asyncio.new_event_loop()` por `asyncio.run_coroutine_threadsafe()` no loop principal
- [ ] Mover STT para thread separada (não bloquear audio loop)
- [ ] Limitar `_voice_buffer` com max size (ex: 30 chunks = 15s)
- [ ] Remover `ThreadPoolExecutor` duplicado (linha 30)
- [ ] Adicionar `executor.shutdown()` no cleanup
- [ ] Mover DeepFilterNet para rodar apenas durante active listening, não em idle
- [ ] Log PortAudio status errors em vez de ignorar
- [ ] Adicionar thread safety ao `_callbacks` (usar `threading.Lock`)

### Fase 3 — Implementar WebSocket Binário (4-6h)

#### Backend
- [ ] `voice_websocket.py`: usar `receive_bytes()` para receber PCM chunks
- [ ] Buffer de áudio no WebSocket para acumular chunks
- [ ] Integrar buffer do WebSocket com pipeline STT do voice_engine
- [ ] `send_bytes()` para enviar áudio TTS ao browser
- [ ] Suporte a barge-in: detectar áudio do usuário enquanto JARVIS fala

#### Frontend
- [ ] Conectar `ScriptProcessorNode` ao WebSocket (`ws.send(audioChunk)`)
- [ ] Reproduzir áudio recebido via `AudioContext.decodeAudioData()`
- [ ] Remover handler de binary no `use-voice.ts` ou unificar com `jarvis-context.tsx`
- [ ] Indicador visual de "ouvindo" / "falando"

### Fase 4 — Pipeline de Áudio Completo (3-4h)

- [ ] Pipeline async puro: STT → LLM → TTS sem threads desnecessárias
- [ ] GPU alternada: STT usa 2GB → descarrega → LLM usa 3GB → descarrega → TTS na CPU
- [ ] VAD correto com Silero (já existe em `barge_in.py`)
- [ ] Remover DeepFilterNet de cada chunk (usar apenas durante active listening)
- [ ] Integrar `_fire()` com `perception_manager._on_voice_event`
- [ ] Testar wake word + speaker validation + transcrição + resposta TTS

### Fase 5 — Testes e Validação (2-3h)

- [ ] Teste de wake word com speaker conhecido
- [ ] Teste de streaming áudio browser ↔ server
- [ ] Teste de barge-in (interromper JARVIS falando)
- [ ] Teste de memória (sem OOM em uso prolongado)
- [ ] Teste de CPU usage em idle
- [ ] Teste de múltiplos speakers
- [ ] Validação de `ENABLE_PERCEPTION=true` com câmera/mic

---

## Arquitetura Proposta — JARVIS 5.0 REAL

### Stack Leve (~500 linhas vs 23.000 atuais)

| Componente | Tecnologia | VRAM |
|------------|------------|------|
| STT | faster-whisper (tiny) | 2GB |
| LLM | Ollama/Qwen3-4B | 3GB |
| TTS | Kokoro-82M | CPU |
| VAD | Silero VAD | CPU |
| Wake Word | openWakeWord | CPU |

### GPU Alternada
```
STT (2GB) → descarrega GPU → LLM (3GB) → descarrega GPU → TTS (CPU)
Total: cabe na GTX 1050 Ti 4GB
```

### WebSocket Bidirecional
```
Browser (mic) → PCM chunks → WebSocket → Server (STT) → LLM → TTS → PCM chunks → Browser (speaker)
```

### Dependências Python (~12 vs 61 atuais)
```
fastapi, uvicorn, faster-whisper, openwakeword, sounddevice,
silero-vad, kokoro-tts, numpy, pydantic-settings, loguru,
ollama (python client), websockets
```

### Dependências npm (~5 vs 40+)
```
next, react, react-dom, typescript, tailwindcss
```

---

## Bugs Corrigidos Nesta Sessão

| # | Bug | Arquivo | Status |
|---|-----|---------|--------|
| 1 | `get_spatial_awareness()` não existia | `system_control.py` | Corrigido |
| 2 | `set_brightness`, `capture_screens`, `__init__` chamavam módulos `None` | `system_control.py` | Corrigido |
| 3 | Imports unused em `perception_manager.py` | `perception_manager.py` | Corrigido |
| 4 | Engine modules exportados como `None` | `perception/__init__.py` | Corrigido |
| 5 | `capture_frame()` não existia | `perception_tools.py` | Corrigido |
| 6 | Endpoints `async def` com código síncrono bloqueante | `system_bridge.py` | Corrigido (asyncio.to_thread) |
| 7 | `on_wake_word` e `on_gesture` dead code | `perception_manager.py` | Corrigido |
| 8 | `logging` stdlib sem handlers (logs silenciosos) | `system_control.py`, `system_bridge.py` | Corrigido (loguru) |
| 9 | `basicConfig` duplicado | `gap_analyzer.py`, `dream_cycle.py` | Corrigido (loguru) |
| 10 | `if not perception_manager` sempre truthy | `multi_agent_analysis.py` | Corrigido |
| 11 | `_on_voice_event` sem guarda `VoiceResult is None` | `perception_manager.py` | Corrigido |
