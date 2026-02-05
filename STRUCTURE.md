# 🏗️ JARVIS 5.0 - Estrutura do Projeto

## 📁 Visão Geral da Arquitetura

```
PROJECT_JARVIS_5.0/
├── 🎯 ENTRY POINTS
│   ├── main_singularity.py          # ✅ Orquestrador principal (HUD + Voice + AI)
│   ├── JARVIS.bat                   # ✅ Launcher Windows
│   └── legacy/main.py               # ✅ Sistema antigo (preservado)
│
├── 🖥️ INTERFACE (Nova - Singularity)
│   └── src/interface/
│       ├── hud.py                   # ✅ HUD transparente estilo Iron Man
│       └── __init__.py              # ✅ Exports do módulo
│
├── 🧠 CORE (Sistema Funcional)
│   └── src/core/
│       ├── ai_agent.py              # ✅ Cérebro (Groq + Gemini + Ollama)
│       ├── voice_controller.py      # ✅ STT + TTS + Wake Word
│       ├── camera_controller.py     # ✅ FaceID + Emotion Detection
│       ├── screen_capture.py        # ✅ Captura de tela
│       ├── ocr_processor.py         # ✅ OCR (Tesseract + EasyOCR)
│       ├── action_controller.py     # ✅ Automação (mouse/teclado)
│       ├── local_brain.py           # ✅ LLM local
│       ├── neural_memory.py         # ✅ Memória vetorial
│       ├── hardware_manager.py      # ✅ Detecção GPU/CPU
│       ├── maintenance_manager.py   # ✅ Auto-heal
│       ├── proactive_monitor.py     # ✅ Monitor proativo
│       ├── data_analyzer.py         # ✅ Análise de dados
│       ├── data_organizer.py        # ✅ Organização de dados
│       ├── ui_detector.py           # ✅ Detecção de UI
│       ├── emotion_detector.py      # ✅ Detecção de emoções
│       ├── brain_router.py          # ✅ Roteamento de IA
│       └── ... (31 arquivos total)
│
├── 🌐 JARVIS CORE (Modular - Singularity)
│   └── jarvis_core/
│       ├── brain/                   # ⚠️ Parcialmente implementado
│       │   ├── neural_router.py     # ⏭️ TODO: Integrar
│       │   └── __init__.py
│       ├── senses/                  # ⏭️ TODO: Desenvolver
│       │   ├── vision.py
│       │   ├── hearing.py
│       │   └── __init__.py
│       ├── mouth/                   # ⏭️ TODO: Desenvolver
│       │   ├── tts_engine.py
│       │   └── __init__.py
│       ├── hive_mind/              # ⏭️ TODO: Desenvolver
│       │   ├── rclone_sync.py
│       │   └── __init__.py
│       ├── world/                   # ⏭️ TODO: Desenvolver
│       │   ├── iot_controller.py
│       │   └── __init__.py
│       ├── interface/              # ✅ Movido para src/interface/
│       └── guardian/               # ✅ Implementado
│           ├── safe_mode.py
│           ├── watchdog.py
│           └── __init__.py
│
├── 💾 DATABASE
│   └── src/database/
│       ├── models.py               # ✅ SQLAlchemy models
│       └── __init__.py
│
├── 🛠️ UTILS
│   └── src/utils/
│       ├── config.py               # ✅ Gerenciamento de config
│       ├── helpers.py              # ✅ Funções auxiliares
│       └── web_search_tool.py      # ✅ Busca web
│
├── 📊 DATA
│   └── data/
│       ├── captures/               # Screenshots
│       ├── processed/              # Dados processados
│       ├── exports/                # Exportações
│       └── database.db             # SQLite
│
├── 📝 DOCS
│   └── docs/
│       ├── installation.md         # ✅ Guia de instalação
│       ├── getting_started.md      # ✅ Primeiros passos
│       ├── advanced_features.md    # Recursos avançados
│       └── ... (14 arquivos)
│
├── ⚙️ CONFIG
│   ├── config.yaml                 # ✅ Configuração principal
│   └── requirements*.txt           # ✅ Dependências
│
└── 📚 LEGACY
    └── legacy/
        ├── main.py                 # Sistema antigo
        ├── Jarvis.bat             # Launcher antigo
        └── START_JARVIS.bat       # Launcher antigo
```

---

## 🔗 Fluxo de Execução

### Sistema Atual (Singularity)

```
JARVIS.bat
    ↓
main_singularity.py
    ↓
┌─────────────────────────────────────┐
│   SingularityCore                   │
│                                     │
│  ┌──────────────────────────────┐  │
│  │  Thread 1: GUI (Main)        │  │
│  │  - JarvisHUD (PyQt6)         │  │
│  │  - Reator pulsante           │  │
│  │  - Estados visuais           │  │
│  └──────────────────────────────┘  │
│                                     │
│  ┌──────────────────────────────┐  │
│  │  Thread 2: Brain (Asyncio)   │  │
│  │  - AI Agent                  │  │
│  │  - Camera Controller         │  │
│  │  - Asyncio loop              │  │
│  └──────────────────────────────┘  │
│                                     │
│  ┌──────────────────────────────┐  │
│  │  Thread 3: Voice             │  │
│  │  - Wake word detection       │  │
│  │  - Command processing        │  │
│  │  - Callbacks → HUD           │  │
│  └──────────────────────────────┘  │
└─────────────────────────────────────┘
```

---

## ✅ Componentes Implementados

### Interface
- [x] **HUD Transparente** (`src/interface/hud.py`)
  - ReactorWidget (reator pulsante)
  - JarvisHUD (overlay transparente)
  - Click-through
  - 5 estados visuais

### Core Funcional
- [x] **AI Agent** (`src/core/ai_agent.py`)
  - Groq + Gemini + Ollama
  - Brain Router
  - Processamento de comandos
  
- [x] **Voice Controller** (`src/core/voice_controller.py`)
  - Wake word (Vosk)
  - STT (Google/Whisper)
  - TTS (Edge/pyttsx3)
  
- [x] **Camera Controller** (`src/core/camera_controller.py`)
  - FaceID
  - Emotion detection
  
- [x] **Automação** (`src/core/action_controller.py`)
  - Mouse/Teclado
  - Programas
  - Arquivos

### Orquestrador
- [x] **main_singularity.py**
  - Threading (GUI + Brain + Voice)
  - Asyncio
  - Callbacks
  - Logging

---

## ⏭️ Componentes Pendentes

### Jarvis Core (Modular)

#### 1. Brain Híbrido
- [ ] `jarvis_core/brain/neural_router.py`
  - Roteamento inteligente Groq/Gemini
  - Fallback para local
  - Cache de respostas

#### 2. Senses (Sentidos)
- [ ] `jarvis_core/senses/vision.py`
  - Integração com screen_capture
  - Análise de imagens
  - Detecção de objetos
  
- [ ] `jarvis_core/senses/hearing.py`
  - Integração com voice_controller
  - Análise de áudio
  - Diarização

#### 3. Mouth (Comunicação)
- [ ] `jarvis_core/mouth/tts_engine.py`
  - TTS neural (XTTS)
  - Edge-TTS
  - Barge-in

#### 4. Hive Mind (Sync)
- [ ] `jarvis_core/hive_mind/rclone_sync.py`
  - Sync com Google Drive
  - Consciência distribuída
  - Merge de memórias

#### 5. World (IoT)
- [ ] `jarvis_core/world/iot_controller.py`
  - Integração Alexa (Fauxmo)
  - Tuya devices
  - Home automation

---

## 🔌 Integrações Necessárias

### 1. Brain Router → AI Agent
```python
# Em main_singularity.py
from jarvis_core.brain.neural_router import neural_router

# Substituir:
self.brain.process_command(text)

# Por:
neural_router.process(text, context={"hud": self.hud})
```

### 2. Senses → Core
```python
# Integrar vision
from jarvis_core.senses.vision import vision_engine
vision_engine.analyze(screenshot_path)

# Integrar hearing
from jarvis_core.senses.hearing import hearing_engine
hearing_engine.process(audio_data)
```

### 3. Hive Mind → Singularity
```python
# Adicionar em brain_loop
if config.get_setting('hive_mind.enabled'):
    from jarvis_core.hive_mind.rclone_sync import sync_manager
    sync_manager.start_sync()
```

---

## 📊 Status de Desenvolvimento

| Módulo | Status | Progresso | Prioridade |
|--------|--------|-----------|------------|
| HUD Interface | ✅ Completo | 100% | Alta |
| Voice Controller | ✅ Completo | 100% | Alta |
| AI Agent | ✅ Completo | 100% | Alta |
| Camera/FaceID | ✅ Completo | 100% | Média |
| Automação | ✅ Completo | 100% | Alta |
| Brain Router | ⚠️ Parcial | 30% | Alta |
| Senses (Vision) | ⏭️ Pendente | 0% | Média |
| Senses (Hearing) | ⏭️ Pendente | 0% | Baixa |
| Mouth (TTS Neural) | ⏭️ Pendente | 0% | Média |
| Hive Mind | ⏭️ Pendente | 0% | Baixa |
| World (IoT) | ⏭️ Pendente | 0% | Baixa |

---

## 🎯 Roadmap de Integração

### Fase 1: Sistema Base (✅ Completo)
- [x] HUD transparente
- [x] Voice integration
- [x] AI Agent básico
- [x] Orquestrador

### Fase 2: Brain Híbrido (⏭️ Próximo)
- [ ] Implementar neural_router
- [ ] Integrar com main_singularity
- [ ] Testes de roteamento
- [ ] Fallback para local

### Fase 3: Senses Avançados
- [ ] Vision engine
- [ ] Hearing engine
- [ ] Integração com HUD

### Fase 4: Hive Mind
- [ ] Rclone sync
- [ ] Merge de memórias
- [ ] Multi-device

### Fase 5: IoT & Automação
- [ ] World controller
- [ ] Integração Alexa
- [ ] Smart home

---

## 🔧 Dependências por Módulo

### Core (Essenciais)
```
PyQt6              # HUD
SpeechRecognition  # Voice
pyttsx3            # TTS
opencv-python      # Vision
pytesseract        # OCR
sqlalchemy         # Database
```

### Avançadas (Opcionais)
```
torch              # Neural networks
transformers       # LLMs
openai-whisper     # STT avançado
google-generativeai # Gemini
easyocr            # OCR neural
face-recognition   # FaceID
```

### Hive Mind
```
# Rclone (externo)
# Instalação: https://rclone.org/downloads/
```

---

## 📝 Notas de Desenvolvimento

### Código Funcional (Não Mexer)
- `src/core/voice_controller.py` - Wake word funciona!
- `src/core/ai_agent.py` - Processamento funciona!
- `src/core/maintenance_manager.py` - Auto-heal funciona!

### Código em Transição
- `jarvis_core/brain/` - Migração em andamento
- `jarvis_core/senses/` - Aguardando implementação

### Código Legacy (Preservado)
- `legacy/main.py` - Sistema antigo completo
- Mantido para referência e fallback

---

## 🚀 Como Contribuir

### Adicionar Novo Módulo
1. Criar em `jarvis_core/[modulo]/`
2. Implementar interface padrão
3. Adicionar testes
4. Integrar em `main_singularity.py`
5. Atualizar documentação

### Modificar Existente
1. Verificar se não quebra integrações
2. Manter compatibilidade
3. Atualizar testes
4. Documentar mudanças

---

**Última Atualização**: 05/02/2026  
**Versão**: 2.0 - Singularity with HUD  
**Status**: Sistema base completo, módulos avançados pendentes
