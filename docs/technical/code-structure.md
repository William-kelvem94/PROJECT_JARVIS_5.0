# 🏗️ JARVIS 5.0 - Estrutura de Código

**Guia Completo da Arquitetura do Código**

---

## 📁 Árvore de Diretórios

```
PROJECT_JARVIS_5.0/
├── 📄 main.py                    # Entry point principal
├── 📄 SINGULARITY_LAUNCHER.py    # Sistema de inicialização em stages
├── 📄 requirements.txt            # Dependências Python
├── 📄 START_JARVIS.bat           # Launcher Windows
│
├── 📂 src/                        # Código fonte principal
│   ├── 📂 core/                   # Módulos principais
│   │   ├── 📂 brain/             # Sistema de IA
│   │   │   ├── ai_agent.py      # Agente OpenAI/Gemini
│   │   │   ├── brain_router.py  # Roteamento de modelos
│   │   │   └── context_manager.py
│   │   │
│   │   ├── 📂 voice/             # Sistema de voz
│   │   │   ├── voice_engine.py  # STT/TTS integrado
│   │   │   ├── vad.py           # Voice Activity Detection
│   │   │   └── speaker_verification.py
│   │   │
│   │   └── 📂 vision/            # Sistema de visão
│   │       ├── vision_processor.py
│   │       ├── face_recognition.py
│   │       ├── yolo_detector.py
│   │       └── hand_tracking.py
│   │
│   ├── 📂 interface/              # Interfaces gráficas
│   │   ├── control_dashboard.py # Dashboard completo (PySide6)
│   │   └── hud_overlay.py       # HUD transparente
│   │
│   ├── 📂 learning/               # Sistema de aprendizado
│   │   ├── learning_engine.py   # Orquestrador principal
│   │   ├── feedback_loop.py     # Coleta de feedback
│   │   ├── continual_learner.py # Treinamento contínuo
│   │   ├── knowledge_distiller.py # Golden Commands
│   │   └── dream_cycle.py       # Treinamento noturno
│   │
│   ├── 📂 database/               # Persistência
│   │   ├── chromadb_manager.py  # Vector DB para memórias
│   │   ├── memory_manager.py    # Gerenciamento de memória
│   │   └── config_manager.py    # Configurações
│   │
│   ├── 📂 utils/                  # Utilitários
│   │   ├── system_utils.py      # Info de sistema
│   │   ├── file_utils.py        # Manipulação de arquivos
│   │   └── telemetry.py         # Monitoramento
│   │
│   └── 📂 web/                    # Integração web (futuro)
│       └── api_server.py        # REST API
│
├── 📂 config/                     # Configurações
│   ├── ai_config.yaml            # Config de IA (principal)
│   ├── config.yaml               # Config geral
│   └── settings.json             # Settings do usuário
│
├── 📂 data/                       # Dados persistentes
│   ├── 📂 learning/              # Dados de aprendizado
│   │   ├── feedback_loop.db     # SQLite com feedbacks
│   │   ├── golden_commands.json # Dataset curado
│   │   └── training_history.json
│   │
│   ├── 📂 memories/              # Memórias de longo prazo
│   ├── 📂 logs/                  # Logs do sistema
│   ├── 📂 faces/                 # Banco de faces (FaceID)
│   └── 📂 screenshots/           # Capturas de tela
│
├── 📂 models/                     # Modelos de IA
│   ├── 📂 continual/             # Local Brain + LoRA
│   ├── yolov8n.pt               # YOLO detection
│   └── hand_landmarker.task     # MediaPipe hands
│
├── 📂 docs/                       # Documentação
├── 📂 tests/                      # Testes unitários
└── 📂 scripts/                    # Scripts auxiliares
```

---

## 🧩 Módulos Principais

### 1. 🧠 Brain (src/core/brain/)

#### `ai_agent.py`
**Responsabilidade:** Interface para modelos de IA (Gemini, OpenAI, Ollama)

**Classes principais:**
```python
class AIAgent:
    def __init__(self, model="gemini-flash")
    def thinking(self, prompt: str) -> str
    def switch_brain(self, model: str)
    def record_interaction(self, user_input, response, feedback)
```

**Dependências:**
- `google-generativeai` (Gemini)
- `openai` (OpenAI)
- `requests` (Ollama HTTP)

---

#### `brain_router.py`
**Responsabilidade:** Roteamento inteligente entre modelos

**Classes principais:**
```python
class BrainRouter:
    def route_query(self, query: str) -> str
    def classify_task(self, query: str) -> TaskType
    def select_model(self, task: TaskType) -> str
```

**Lógica:**
1. Analisa query (complexidade, tipo, privacidade)
2. Consulta `ai_config.yaml` (routing rules)
3. Retorna modelo ideal

---

### 2. 🎤 Voice (src/core/voice/)

#### `voice_engine.py`
**Responsabilidade:** STT (Speech-to-Text) e TTS (Text-to-Speech)

**Classes principais:**
```python
class VoiceEngine:
    def __init__(self)
    def listen(self) -> str  # STT
    def speak(self, text: str)  # TTS
    def set_microphone(self, device_index: int)
```

**Engines suportados:**
- **STT:** faster-whisper, whisper, vosk
- **TTS:** pyttsx3, elevenlabs, azure

---

### 3. 👁️ Vision (src/core/vision/)

#### `vision_processor.py`
**Responsabilidade:** Processamento de imagens/vídeo

**Classes principais:**
```python
class VisionProcessor:
    def capture_frame(self) -> np.ndarray
    def yolo_detect(self, frame) -> List[Detection]
    def recognize_face(self, frame) -> Optional[str]
    def detect_hands(self, frame) -> List[HandLandmark]
```

**Modelos:**
- YOLOv8n (object detection)
- DeepFace (face recognition)
- MediaPipe (hand tracking)

---

### 4. 🎓 Learning (src/learning/)

#### `learning_engine.py`
**Responsabilidade:** Orquestrador de todos sistemas de aprendizado

**Classes principais:**
```python
class LearningEngine:
    def __init__(self)
    def initialize_all_systems(self)
    def record_interaction(self, user_input, response, feedback)
    def trigger_training(self)
```

**Subsistemas:**
- `FeedbackLoop` - Coleta feedback
- `ContinualLearner` - Treinamento LoRA
- `KnowledgeDistiller` - Curadoria de Golden Commands
- `DreamCycle` - Treinamento noturno

---

#### `feedback_loop.py`
**Responsabilidade:** Armazenar todas interações

**Classes principais:**
```python
class FeedbackLoop:
    def record_feedback(self, interaction: dict)
    def get_pending_feedbacks(self) -> List[dict]
    def mark_as_trained(self, feedback_ids: List[int])
```

**Storage:** SQLite (`data/learning/feedback_loop.db`)

**Schema:**
```sql
CREATE TABLE feedbacks (
    id INTEGER PRIMARY KEY,
    timestamp TEXT,
    user_input TEXT,
    ai_response TEXT,
    feedback TEXT,  -- 'positive', 'negative', 'correction'
    correction TEXT,
    model_used TEXT,
    trained BOOLEAN DEFAULT 0
);
```

---

#### `continual_learner.py`
**Responsabilidade:** Treinar Local Brain com LoRA

**Classes principais:**
```python
class ContinualLearner:
    def train_model(self)
    def prepare_dataset(self) -> Dataset
    def evaluate_model(self) -> float
    def deploy_model(self)
```

**Tecnologias:**
- `transformers` (Hugging Face)
- `peft` (LoRA implementation)
- `torch` (PyTorch)

---

### 5. 🖥️ Interface (src/interface/)

#### `control_dashboard.py`
**Responsabilidade:** Dashboard completo (PySide6/Qt)

**Classes principais:**
```python
class ControlDashboard(QMainWindow):
    def __init__(self)
    def setup_tabs(self)
    def refresh_status(self)
```

**Tabs:**
1. Brain - Controle de IA
2. Voice - Config de voz
3. Vision - Config de visão
4. Learning - Sistema de aprendizado ⭐
5. Logs - Visualização de logs
6. System - Info de sistema

---

## 🔄 Fluxo de Execução

### Inicialização (SINGULARITY_LAUNCHER.py)

```
START_JARVIS.bat
    ↓
SINGULARITY_LAUNCHER.py
    ↓
[STAGE 0] Infrastructure Check
├─ Verifica Python/venv
├─ Valida paths
└─ Prepara ambiente
    ↓
[STAGE 1] Environment Validation
├─ Testa imports
├─ Verifica YAML configs
└─ Conecta DBs
    ↓
[STAGE 2] Model Initialization
├─ Carrega YOLOv8n
├─ Inicializa AI Agent
└─ Prepara STT/TTS engines
    ↓
[STAGE 2.7] Learning Systems ⭐
├─ LearningEngine.initialize_all_systems()
├─ FeedbackLoop.connect()
├─ ContinualLearner.check_status()
└─ DreamCycle.schedule()
    ↓
[STAGE 3] GUI Launch
├─ HUD Overlay (padrão)
└─ ou Control Dashboard
    ↓
✅ SINGULARITY CORE ENGAGED
```

---

### Interação do Usuário

```
User: "Olá JARVIS"
    ↓
VoiceEngine.listen()
    ↓ (STT)
"Olá JARVIS" (texto)
    ↓
BrainRouter.route_query()
    ↓
AIAgent.thinking("Olá JARVIS")
    ↓ (LLM)
"Sim, senhor. Como posso ajudar?" (resposta)
    ↓
VoiceEngine.speak()
    ↓ (TTS)
🔊 Áudio
    ↓
LearningEngine.record_interaction() ⭐
    ↓
FeedbackLoop.save_to_db()
```

---

## 📦 Dependências Críticas

### Core

```txt
# IA
google-generativeai>=0.8.0
openai>=1.0.0
transformers>=4.36.0
peft>=0.7.0  # LoRA
torch>=2.1.0

# Visão
opencv-python>=4.8.0
mediapipe>=0.10.0
ultralytics>=8.0.0  # YOLOv8
deepface>=0.0.79

# Voz
faster-whisper>=0.10.0
pyttsx3>=2.90
pyaudio>=0.2.13

# GUI
PySide6>=6.6.0
pyqtgraph>=0.13.3

# Database
chromadb>=0.4.18
sqlite3 (built-in)

# Utils
PyYAML>=6.0
psutil>=5.9.0
```

---

## 🧪 Pontos de Extensão

### Adicionar Novo Modelo de IA

**1. Editar `ai_agent.py`:**
```python
class AIAgent:
    def _init_my_model(self):
        # Seu código de inicialização
        pass
    
    def _call_my_model(self, prompt):
        # Seu código de inferência
        pass
```

**2. Adicionar em `brain_router.py`:**
```python
SUPPORTED_MODELS = {
    "my-model": "MyModelProvider"
}
```

**3. Config em `ai_config.yaml`:**
```yaml
ai_models:
  my_model:
    enabled: true
    api_key: "..."
```

---

### Adicionar Nova Tab no Dashboard

**1. Editar `control_dashboard.py`:**
```python
def setup_tabs(self):
    # ... tabs existentes ...
    
    # Nova tab
    my_tab = QWidget()
    self.tabs.addTab(my_tab, "🎯 My Feature")
    self._setup_my_tab(my_tab)

def _setup_my_tab(self, parent):
    layout = QVBoxLayout()
    # Seu UI aqui
    parent.setLayout(layout)
```

---

### Adicionar Novo Sistema de Aprendizado

**1. Criar `src/learning/my_learner.py`:**
```python
class MyLearner:
    def __init__(self):
        pass
    
    def learn(self, data):
        pass
```

**2. Integrar em `learning_engine.py`:**
```python
class LearningEngine:
    def __init__(self):
        self.my_learner = MyLearner()
    
    def initialize_all_systems(self):
        self.my_learner.initialize()
```

---

## 🔍 Debugging

### Logs Importantes

```python
# Ativar logging detalhado
import logging
logging.basicConfig(level=logging.DEBUG)

# Logs são salvos em:
data/logs/jarvis.log
data/logs/brain_router.log
data/logs/learning.log
```

### Breakpoints Úteis

**1. Antes de chamar IA:**
```python
# src/core/brain/ai_agent.py, linha ~150
def thinking(self, prompt):
    breakpoint()  # <-- adicione aqui
    response = self._call_model(prompt)
```

**2. No roteamento:**
```python
# src/core/brain/brain_router.py, linha ~80
def route_query(self, query):
    task = self.classify_task(query)
    breakpoint()  # <-- veja classificação
    model = self.select_model(task)
```

**3. No aprendizado:**
```python
# src/learning/learning_engine.py, linha ~100
def record_interaction(self, ...):
    breakpoint()  # <-- veja o que é salvo
    self.feedback_loop.record(...)
```

---

## 🆘 Suporte

- **Arquitetura:** [../architecture/overview.md](../architecture/overview.md)
- **API:** [api-reference.md](api-reference.md)
- **Contribuição:** [contributing.md](contributing.md)

---

<div align="center">

**Código limpo. Arquitetura sólida. Extensível. 🏗️**

</div>
