# 🏗️ JARVIS 5.0 - Estrutura de Código (ATUALIZADO)

**Guia Completo da Arquitetura do Código - Versão 2026-02-09**

---

## ⚠️ **IMPORTANTE: Estrutura Atualizada**

Esta documentação reflete a estrutura **REAL** do projeto após reorganização completa.  
**Última atualização**: 2026-02-09 23:56

---

## 📁 Árvore de Diretórios Atual

```
PROJECT_JARVIS_5.0/
├── 📄 main.py                      # Entry point principal
├── 📄 SINGULARITY_LAUNCHER.py      # Sistema de inicialização em stages
├── 📄 START_JARVIS.bat             # Launcher Windows
│
├── 📂 src/                          # Código fonte principal
│   ├── 📂 core/                     # Módulos principais ⭐ REORGANIZADO
│   │   │
│   │   ├── 📂 intelligence/         # Sistema de IA (NOVO)
│   │   │   ├── ai_agent.py         # Agente principal de IA
│   │   │   ├── brain_router.py     # Roteamento inteligente de modelos
│   │   │   ├── local_brain.py      # Cérebro local (Qwen/Phi)
│   │   │   ├── memory_manager.py   # Gerenciamento de memória (ChromaDB)
│   │   │   ├── neural_memory.py    # Memória neural
│   │   │   └── emotion_detector.py # Detecção de emoções
│   │   │
│   │   ├── 📂 audio/                # Sistema de áudio (NOVO)
│   │   │   ├── voice_controller.py # Controle de voz (STT/TTS)
│   │   │   ├── enhanced_audio.py   # Áudio aprimorado
│   │   │   └── advanced_speech_processor.py # Processamento avançado
│   │   │
│   │   ├── 📂 vision/               # Sistema de visão (NOVO)
│   │   │   ├── vision_system.py    # Sistema de visão principal
│   │   │   ├── camera_controller.py # Controle de câmera
│   │   │   ├── screen_capture.py   # Captura de tela
│   │   │   ├── ui_detector.py      # Detecção de UI
│   │   │   └── advanced_vision_pipeline.py # Pipeline avançado
│   │   │
│   │   ├── 📂 actions/              # Sistema de ações (NOVO)
│   │   │   ├── advanced_action_controller.py # Controle de ações
│   │   │   ├── workflow_engine.py  # Engine de workflows
│   │   │   └── system_integrator.py # Integração de sistema
│   │   │
│   │   ├── 📂 management/           # Gerenciamento (NOVO)
│   │   │   ├── hardware_manager.py # Gerenciamento de hardware
│   │   │   ├── maintenance_manager.py # Manutenção automática
│   │   │   └── security_manager_advanced.py # Segurança
│   │   │
│   │   ├── 📂 engine/               # Motor principal
│   │   ├── 📂 iot/                  # IoT e dispositivos
│   │   ├── 📂 security/             # Segurança
│   │   │
│   │   ├── orchestrator.py          # Orquestrador principal
│   │   └── enhanced_audio.py        # Áudio (legacy)
│   │
│   ├── 📂 interface/                # Interfaces gráficas
│   │   ├── window_manager.py       # Gerenciador de janelas (PyQt6)
│   │   ├── modern_hud.py           # HUD moderno
│   │   ├── control_dashboard.py    # Dashboard de controle
│   │   └── draggable_hud.py        # HUD arrastável
│   │
│   ├── 📂 learning/                 # Sistema de aprendizado ⭐
│   │   ├── dream_cycle.py          # Ciclo de aprendizado noturno
│   │   ├── gap_analyzer.py         # Análise de lacunas de conhecimento
│   │   ├── feedback_loop.py        # Loop de feedback
│   │   ├── continual_learner.py    # Aprendizado contínuo
│   │   └── knowledge_distiller.py  # Destilação de conhecimento
│   │
│   └── 📂 utils/                    # Utilitários
│       ├── config.py               # Configurações
│       ├── logger.py               # Sistema de logging
│       ├── telemetry.py            # Telemetria
│       └── system_utils.py         # Utilitários de sistema
│
├── 📂 config/                       # Configurações
│   ├── ai_config.yaml              # Config de IA (PRINCIPAL) ⭐
│   ├── config.yaml                 # Config geral
│   └── settings.json               # Settings do usuário
│
├── 📂 data/                         # Dados persistentes
│   ├── 📂 chroma_db/               # ChromaDB (memórias vetoriais)
│   ├── 📂 learning/                # Dados de aprendizado
│   ├── 📂 logs/                    # Logs do sistema
│   ├── 📂 faces/                   # Banco de faces (FaceID)
│   └── 📂 voice_signatures/        # Assinaturas de voz
│
├── 📂 models/                       # Modelos de IA
│   ├── 📂 speech/                  # Modelos de voz
│   │   └── vosk-model-small-pt-0.3/ # Vosk PT-BR
│   ├── 📂 vision/                  # Modelos de visão
│   │   ├── yolov8n.pt             # YOLO v8 Nano (PRINCIPAL)
│   │   └── hand_landmarker.task   # MediaPipe hands
│   ├── 📂 training/                # Modelos em treinamento
│   │   └── continual/             # Aprendizado contínuo
│   └── 📂 yolo/                    # Modelos YOLO adicionais
│       └── DOWNLOAD.md            # Instruções de download
│
├── 📂 tools/                        # Ferramentas de diagnóstico ⭐
│   ├── full_diagnostics.py         # Diagnóstico completo
│   ├── validate_p0_p1.py           # Validação de features
│   ├── jarvis_diagnostics.py       # Diagnóstico rápido
│   └── benchmark_p0.py             # Benchmarks
│
├── 📂 tests/                        # Testes
│   ├── test_evolution_complete.py  # Testes de evolução
│   ├── test_god_mode_complete.py   # Testes god mode
│   └── validate_functions.py       # Validação de funções
│
├── 📂 scripts/                      # Scripts auxiliares
│   ├── auto_configurator.py        # Configuração automática
│   ├── auto_healer.py              # Auto-reparo
│   ├── 📂 install/                 # Scripts de instalação
│   │   ├── total_installer.py     # Instalador completo
│   │   ├── setup.py               # Setup
│   │   └── requirements.txt       # Dependências
│   └── 📂 debug/                   # Scripts de debug
│
├── 📂 logs/                         # Logs (runtime)
│   ├── jarvis.log                  # Log principal
│   └── README.md                   # Documentação de logs
│
└── 📂 docs/                         # Documentação
    ├── README.md                   # Índice principal
    ├── 📂 getting-started/         # Guias de início
    ├── 📂 ai-systems/              # Sistemas de IA
    ├── 📂 technical/               # Documentação técnica
    └── 📂 user-guide/              # Guia do usuário
```

---

## 🧩 Módulos Principais (Estrutura Atual)

### 1. 🧠 Intelligence (src/core/intelligence/)

#### `ai_agent.py`
**Responsabilidade:** Interface principal para modelos de IA

**Classes principais:**
```python
class AIAgent:
    def __init__(self)
    def thinking(self, prompt: str, context: dict = None) -> str
    def switch_model(self, model_name: str)
    def get_available_models() -> List[str]
```

**Modelos suportados:**
- Gemini (Flash, Pro)
- Ollama (Local - gemma3:4b, qwen2.5, llama3.2)
- Local Brain (Qwen 0.5B/1.5B)

---

#### `brain_router.py`
**Responsabilidade:** Roteamento inteligente entre modelos

**Classes principais:**
```python
class BrainRouter:
    def choose_brain(
        task_complexity: float,
        privacy_level: PrivacyLevel,
        latency_requirement: LatencyRequirement
    ) -> str
```

**Lógica de roteamento:**
1. Verifica modo offline
2. Analisa privacidade (HIGH → local obrigatório)
3. Verifica modelos Ollama disponíveis
4. Seleciona tier (ULTRA/PRO/FAST) baseado em recursos
5. Fallback para cloud se necessário

---

#### `local_brain.py`
**Responsabilidade:** Cérebro local (Qwen/Phi) sem internet

**Classes principais:**
```python
class LocalBrain:
    def __init__(self, model_size="0.5B")
    def generate(self, prompt: str) -> str
    def load_model()
    def unload_model()
```

**Modelos:**
- Qwen 0.5B (ultra-rápido)
- Qwen 1.5B (balanceado)
- Phi-2 (alternativa)

---

#### `memory_manager.py`
**Responsabilidade:** Gerenciamento de memória com ChromaDB

**Classes principais:**
```python
class MemoryManager:
    def remember(self, command: str, response: str, context: dict)
    def recall(self, query: str, n_results: int = 5) -> List[dict]
    def purge_old_memories(self, days: int = 30)
```

**Storage:** ChromaDB em `data/chroma_db/`

---

### 2. 🎤 Audio (src/core/audio/)

#### `voice_controller.py`
**Responsabilidade:** Controle completo de voz (STT/TTS)

**Classes principais:**
```python
class VoiceController:
    def listen(self) -> str  # Speech-to-Text
    def speak(self, text: str, emotion: str = "neutral")  # Text-to-Speech
    def set_voice_engine(self, engine: str)
```

**Engines STT:**
- Vosk (offline, PT-BR)
- Whisper (online, multilíngue)
- Google Speech Recognition

**Engines TTS:**
- Edge-TTS (online, neural)
- pyttsx3 (offline, básico)
- XTTS-v2 (voice cloning)

---

### 3. 👁️ Vision (src/core/vision/)

#### `vision_system.py`
**Responsabilidade:** Sistema de visão principal

**Classes principais:**
```python
class VisionSystem:
    def capture_screen() -> np.ndarray
    def detect_objects(frame) -> List[Detection]
    def recognize_face(frame) -> Optional[str]
    def detect_ui_elements(frame) -> List[UIElement]
```

**Modelos:**
- YOLOv8n (object detection)
- MediaPipe (hand tracking)
- EasyOCR (text recognition)

---

### 4. 🎓 Learning (src/learning/)

#### `dream_cycle.py`
**Responsabilidade:** Aprendizado durante inatividade

**Classes principais:**
```python
class DreamCycle:
    def start_dream_cycle()
    def analyze_day_interactions()
    def train_on_patterns()
    def update_knowledge_base()
```

**Funcionalidades:**
- Análise de padrões de uso
- Treinamento incremental
- Atualização de conhecimento
- Integração com gap_analyzer

---

#### `gap_analyzer.py`
**Responsabilidade:** Análise de lacunas de conhecimento

**Classes principais:**
```python
class KnowledgeGapAnalyzer:
    def analyze_gaps() -> List[Gap]
    def generate_research_tasks() -> List[Task]
    def update_knowledge()
```

---

### 5. 🖥️ Interface (src/interface/)

#### `window_manager.py`
**Responsabilidade:** Gerenciamento de janelas (PyQt6)

**Classes principais:**
```python
class WindowManager:
    def __init__(self, app: QApplication)
    def show_main_window()
    def show_hud()
    def toggle_dashboard()
```

---

#### `modern_hud.py`
**Responsabilidade:** HUD moderno e transparente

**Classes principais:**
```python
class ModernHUD(QMainWindow):
    def update_status(self, status: str)
    def show_thinking_animation()
    def display_response(self, text: str)
```

---

## 🔄 Fluxo de Execução Atualizado

### Inicialização (SINGULARITY_LAUNCHER.py)

```
START_JARVIS.bat
    ↓
SINGULARITY_LAUNCHER.py
    ↓
[STAGE 0] Infrastructure Check
├─ Verifica Python 3.11+
├─ Valida venv
└─ Prepara ambiente
    ↓
[STAGE 1] Environment Validation
├─ Testa imports críticos
├─ Valida YAML configs (ai_config.yaml)
└─ Conecta ChromaDB
    ↓
[STAGE 2] Core Systems
├─ HardwareManager.initialize()
├─ BrainRouter.discover_ollama_models()
├─ VoiceController.setup()
└─ VisionSystem.load_models()
    ↓
[STAGE 2.7] Learning Systems ⭐
├─ DreamCycle.initialize()
├─ GapAnalyzer.start()
├─ MemoryManager.connect()
└─ FeedbackLoop.resume()
    ↓
[STAGE 3] GUI Launch
├─ WindowManager.initialize()
├─ ModernHUD.show() (padrão)
└─ ou ControlDashboard.show()
    ↓
✅ SINGULARITY CORE ENGAGED
```

---

### Interação do Usuário (Atualizado)

```
User: "JARVIS, qual o clima?"
    ↓
VoiceController.listen()
    ↓ (Vosk STT)
"JARVIS, qual o clima?" (texto)
    ↓
BrainRouter.choose_brain(
    task_complexity=0.3,
    privacy_level=LOW,
    latency_requirement=MODERATE
)
    ↓ (Retorna: "ollama:gemma3:4b")
AIAgent.thinking("qual o clima?", model="ollama:gemma3:4b")
    ↓ (Ollama local)
"A temperatura atual é 25°C..." (resposta)
    ↓
VoiceController.speak(response, emotion="neutral")
    ↓ (Edge-TTS)
🔊 Áudio
    ↓
MemoryManager.remember(command, response, context) ⭐
    ↓
ChromaDB.upsert()
```

---

## 📦 Dependências Críticas (Atualizadas)

### Core (requirements.txt)

```txt
# IA
google-generativeai>=0.8.0
transformers>=4.36.0
torch==2.2.2
sentence-transformers>=2.2.0

# Ollama (HTTP client)
requests>=2.31.0

# Visão
opencv-python>=4.8.0
mediapipe>=0.10.0
ultralytics>=8.0.0
easyocr>=1.7.0

# Voz
vosk>=0.3.45
edge-tts>=6.1.0
pyttsx3>=2.90

# GUI
PyQt6>=6.6.0

# Database
chromadb>=0.4.18

# Utils
PyYAML>=6.0
psutil>=5.9.0
```

---

## 🆕 Mudanças Principais vs Documentação Antiga

| Aspecto | Antigo | Novo (Atual) |
|---------|--------|--------------|
| **Estrutura core/** | `brain/`, `voice/`, `vision/` | `intelligence/`, `audio/`, `vision/`, `actions/`, `management/` |
| **AI Agent** | `core/brain/ai_agent.py` | `core/intelligence/ai_agent.py` |
| **Voice** | `core/voice/voice_engine.py` | `core/audio/voice_controller.py` |
| **Memory** | `database/memory_manager.py` | `core/intelligence/memory_manager.py` |
| **Brain Router** | `core/brain/brain_router.py` | `core/intelligence/brain_router.py` |
| **Learning** | `learning/learning_engine.py` | `learning/dream_cycle.py` + `gap_analyzer.py` |
| **Models** | `models/continual/` | `models/vision/`, `models/speech/`, `models/training/` |
| **Tools** | Não existia | `tools/` com diagnósticos completos |

---

## 🔧 Configuração Principal

### `config/ai_config.yaml` (Estrutura Atual)

```yaml
# Modelos Ollama (Local)
ollama_models:
  tier_ultra:
    - deepseek-r1:7b
  tier_pro:
    - gemma3:4b      # ✅ Instalado
    - qwen2.5:7b
    - llama3.2
  tier_fast:
    - gemma3         # ✅ Instalado
    - qwen2.5:3b

# Modelos Cloud
cloud_models:
  gemini:
    flash: gemini-1.5-flash
    pro: gemini-1.5-pro

# Brain Router
brain_router:
  offline_mode: false
  discovery_interval: 300
  ollama_url: "http://localhost:11434"
```

---

## 🆘 Suporte

- **Estrutura Atualizada:** Este documento
- **Instalação:** [../getting-started/installation.md](../getting-started/installation.md)
- **AI Systems:** [../ai-systems/brain-router.md](../ai-systems/brain-router.md)
- **Troubleshooting:** [../maintenance/troubleshooting.md](../maintenance/troubleshooting.md)

---

<div align="center">

**Estrutura Reorganizada. Código Modular. Pronto para Produção. 🏗️**

*Última Atualização: 2026-02-09 23:56*

</div>
