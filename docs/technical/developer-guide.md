# 👨‍💻 JARVIS 5.0 - Guia do Desenvolvedor

**Versão Atualizada**: 2026-02-10

---

## 📋 Pré-requisitos

- **Python**: 3.11 ou superior
- **SO**: Windows 10/11 (64-bit)
- **RAM**: 8 GB mínimo (16 GB recomendado)
- **IDE**: VSCode, PyCharm, ou similar
- **Git**: Para controle de versão
- **Conhecimento**: Python intermediário, conceitos de IA

---

## 🚀 Setup de Desenvolvimento

### 1. Clone e Configure

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/PROJECT_JARVIS_5.0.git
cd PROJECT_JARVIS_5.0

# Crie ambiente virtual
python -m venv venv
venv\Scripts\activate

# Instale dependências de desenvolvimento
pip install -r scripts/install/requirements.txt
pip install pytest black flake8  # Ferramentas de dev
```

### 2. Configure IDE (VSCode)

Crie `.vscode/settings.json`:
```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/venv/Scripts/python.exe",
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "files.encoding": "utf8"
}
```

### 3. Configure Variáveis de Ambiente

Crie `.env` na raiz:
```env
# API Keys
GOOGLE_API_KEY=sua_chave_gemini_aqui
OPENAI_API_KEY=sk-...  # Opcional

# Debug
DEBUG=true
LOG_LEVEL=DEBUG
```

---

## 🏗️ Arquitetura do Código

### Estrutura Atualizada (2026-02-10)

```
src/
├── core/                          # Módulos principais
│   ├── intelligence/              # Sistema de IA ⭐
│   │   ├── ai_agent.py           # Agente principal
│   │   ├── brain_router.py       # Roteamento de modelos
│   │   ├── local_brain.py        # Cérebro local (Qwen)
│   │   ├── memory_manager.py     # Memória (ChromaDB)
│   │   └── emotion_detector.py   # Detecção de emoções
│   │
│   ├── audio/                     # Sistema de áudio ⭐
│   │   ├── voice_controller.py   # Controle de voz (STT/TTS)
│   │   ├── enhanced_audio.py     # Áudio aprimorado
│   │   └── advanced_speech_processor.py
│   │
│   ├── vision/                    # Sistema de visão ⭐
│   │   ├── vision_system.py      # Sistema principal
│   │   ├── camera_controller.py  # Controle de câmera
│   │   ├── screen_capture.py     # Captura de tela
│   │   └── ui_detector.py        # Detecção de UI
│   │
│   ├── actions/                   # Sistema de ações ⭐
│   │   ├── advanced_action_controller.py
│   │   ├── workflow_engine.py
│   │   └── system_integrator.py
│   │
│   └── management/                # Gerenciamento ⭐
│       ├── hardware_manager.py
│       ├── maintenance_manager.py
│       └── security_manager_advanced.py
│
├── interface/                     # Interfaces gráficas
│   ├── window_manager.py         # Gerenciador (PyQt6)
│   ├── modern_hud.py             # HUD moderno
│   └── control_dashboard.py      # Dashboard
│
├── learning/                      # Aprendizado ⭐
│   ├── dream_cycle.py            # Ciclo de aprendizado
│   ├── gap_analyzer.py           # Análise de lacunas
│   ├── feedback_loop.py          # Loop de feedback
│   └── continual_learner.py      # Aprendizado contínuo
│
└── utils/                         # Utilitários
    ├── config.py                 # Configurações
    ├── logger.py                 # Sistema de logging
    └── telemetry.py              # Telemetria
```

---

## 🧩 Componentes Principais

### 1. AI Agent (Inteligência)

**Localização**: `src/core/intelligence/ai_agent.py`

```python
from src.core.intelligence.ai_agent import AIAgent

# Criar agente
agent = AIAgent()

# Processar query
response = agent.thinking(
    prompt="Explique aprendizado de máquina",
    context={"user": "William", "topic": "AI"}
)

# Trocar modelo
agent.switch_model("ollama:gemma3:4b")

# Obter modelos disponíveis
models = agent.get_available_models()
# Retorna: ['gemini-flash', 'ollama:gemma3:4b', 'local-brain']
```

**Métodos principais:**
- `thinking(prompt, context)` - Processa query
- `switch_model(model_name)` - Troca modelo ativo
- `get_available_models()` - Lista modelos disponíveis

---

### 2. Brain Router (Roteamento Inteligente)

**Localização**: `src/core/intelligence/brain_router.py`

```python
from src.core.intelligence.brain_router import BrainRouter, PrivacyLevel, LatencyRequirement

router = BrainRouter()

# Escolher melhor modelo para tarefa
model = router.choose_brain(
    task_complexity=0.7,          # 0.0-1.0
    privacy_level=PrivacyLevel.HIGH,
    latency_requirement=LatencyRequirement.LOW
)
# Retorna: "ollama:gemma3:4b" (local, rápido, privado)

# Descobrir modelos Ollama disponíveis
router.discover_ollama_models()

# Verificar status
status = router.get_status()
# Retorna: {"ollama_available": True, "models": [...]}
```

**Níveis de Privacidade:**
- `PrivacyLevel.LOW` - Pode usar cloud
- `PrivacyLevel.MEDIUM` - Prefere local
- `PrivacyLevel.HIGH` - Apenas local

**Requisitos de Latência:**
- `LatencyRequirement.LOW` - <500ms
- `LatencyRequirement.MODERATE` - <2s
- `LatencyRequirement.HIGH` - Qualquer

---

### 3. Voice Controller (Voz)

**Localização**: `src/core/audio/voice_controller.py`

```python
from src.core.audio.voice_controller import VoiceController

vc = VoiceController()

# Speech-to-Text (escutar)
text = vc.listen()
print(f"Você disse: {text}")

# Text-to-Speech (falar)
vc.speak("Olá, senhor. Como posso ajudar?", emotion="neutral")

# Configurar engine
vc.set_voice_engine("edge")  # edge, pyttsx3, xtts

# Listar vozes disponíveis
voices = vc.get_available_voices()
```

**Engines STT:**
- `vosk` - Offline, PT-BR, rápido
- `whisper` - Online, multilíngue, preciso
- `google` - Online, rápido

**Engines TTS:**
- `edge` - Online, neural, natural
- `pyttsx3` - Offline, básico
- `xtts` - Voice cloning

---

### 4. Vision System (Visão)

**Localização**: `src/core/vision/vision_system.py`

```python
from src.core.vision.vision_system import VisionSystem

vision = VisionSystem()

# Capturar tela
frame = vision.capture_screen()

# Detectar objetos (YOLO)
detections = vision.detect_objects(frame)
for det in detections:
    print(f"{det.class_name}: {det.confidence:.2f}")

# Reconhecer texto (OCR)
text = vision.recognize_text(frame)

# Detectar elementos de UI
ui_elements = vision.detect_ui_elements(frame)
```

**Modelos:**
- YOLOv8n - Detecção de objetos
- EasyOCR - Reconhecimento de texto
- MediaPipe - Rastreamento de mãos

---

### 5. Memory Manager (Memória)

**Localização**: `src/core/intelligence/memory_manager.py`

```python
from src.core.intelligence.memory_manager import MemoryManager

memory = MemoryManager()

# Armazenar memória
memory.remember(
    command="Qual é meu projeto atual?",
    response="JARVIS 5.0 - Sistema de IA assistiva",
    context={"user": "William", "timestamp": "2026-02-10"}
)

# Buscar memórias similares
results = memory.recall("projeto", n_results=5)
for result in results:
    print(f"{result['command']} -> {result['response']}")

# Limpar memórias antigas
memory.purge_old_memories(days=30)
```

**Storage**: ChromaDB em `data/chroma_db/`

---

### 6. Dream Cycle (Aprendizado)

**Localização**: `src/learning/dream_cycle.py`

```python
from src.learning.dream_cycle import DreamCycle

dream = DreamCycle()

# Iniciar ciclo de aprendizado
dream.start_dream_cycle()

# Analisar interações do dia
patterns = dream.analyze_day_interactions()

# Treinar em padrões
dream.train_on_patterns(patterns)

# Atualizar base de conhecimento
dream.update_knowledge_base()
```

**Funcionalidades:**
- Análise de padrões de uso
- Treinamento incremental
- Atualização de conhecimento
- Integração com gap_analyzer

---

## 🔧 Desenvolvimento de Features

### Adicionar Novo Modelo de IA

**1. Editar `ai_agent.py`:**
```python
# src/core/intelligence/ai_agent.py

class AIAgent:
    def _init_my_model(self):
        """Inicializa seu modelo"""
        from my_model import MyModel
        self.my_model = MyModel()
    
    def _call_my_model(self, prompt: str) -> str:
        """Chama seu modelo"""
        return self.my_model.generate(prompt)
```

**2. Adicionar em `brain_router.py`:**
```python
# src/core/intelligence/brain_router.py

SUPPORTED_MODELS = {
    "my-model": "MyModelProvider"
}
```

**3. Config em `ai_config.yaml`:**
```yaml
my_model:
  enabled: true
  api_key: "..."
  endpoint: "http://localhost:8000"
```

---

### Adicionar Nova Interface

**1. Criar componente:**
```python
# src/interface/my_interface.py

from PyQt6.QtWidgets import QMainWindow

class MyInterface(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        # Seu código de UI aqui
        pass
```

**2. Integrar em `window_manager.py`:**
```python
# src/interface/window_manager.py

from src.interface.my_interface import MyInterface

class WindowManager:
    def show_my_interface(self):
        self.my_interface = MyInterface()
        self.my_interface.show()
```

---

### Adicionar Sistema de Aprendizado

**1. Criar learner:**
```python
# src/learning/my_learner.py

class MyLearner:
    def __init__(self):
        self.data = []
    
    def learn(self, data):
        """Aprende com dados"""
        self.data.append(data)
        self.train()
    
    def train(self):
        """Treina modelo"""
        pass
```

**2. Integrar em `dream_cycle.py`:**
```python
# src/learning/dream_cycle.py

from src.learning.my_learner import MyLearner

class DreamCycle:
    def __init__(self):
        self.my_learner = MyLearner()
    
    def start_dream_cycle(self):
        # Usar seu learner
        self.my_learner.learn(data)
```

---

## 🧪 Testes

### Executar Testes

```bash
# Todos os testes
python -m pytest tests/

# Teste específico
python tests/test_evolution_complete.py

# Com coverage
python -m pytest tests/ --cov=src
```

### Criar Novo Teste

```python
# tests/test_my_feature.py

import pytest
from src.core.intelligence.ai_agent import AIAgent

def test_ai_agent_thinking():
    """Testa processamento de query"""
    agent = AIAgent()
    response = agent.thinking("Olá")
    assert response is not None
    assert len(response) > 0

def test_model_switching():
    """Testa troca de modelo"""
    agent = AIAgent()
    agent.switch_model("ollama:gemma3:4b")
    assert agent.current_model == "ollama:gemma3:4b"
```

---

## 📊 Debugging

### Logs

```python
# Usar logger do projeto
from src.utils.logger import get_logger

logger = get_logger(__name__)

logger.debug("Mensagem de debug")
logger.info("Informação")
logger.warning("Aviso")
logger.error("Erro")
logger.critical("Crítico")
```

**Logs salvos em**: `logs/jarvis.log`

### Breakpoints

```python
# Adicionar breakpoint
breakpoint()  # Python 3.7+

# Ou usar debugger do VSCode
# F9 para adicionar breakpoint
# F5 para iniciar debug
```

### Telemetria

```python
from src.utils.telemetry import telemetry

# Registrar evento
telemetry.log_event("feature_used", {
    "feature": "voice_command",
    "duration": 1.5
})

# Ver estatísticas
stats = telemetry.get_stats()
```

---

## 📝 Convenções de Código

### Estilo

```python
# Use snake_case para funções e variáveis
def my_function(param_name):
    local_variable = 10

# Use PascalCase para classes
class MyClass:
    pass

# Use UPPER_CASE para constantes
MAX_RETRIES = 3
DEFAULT_MODEL = "gemini-flash"

# Docstrings em todas as funções públicas
def process_data(data: dict) -> str:
    """
    Processa dados de entrada.
    
    Args:
        data: Dicionário com dados
    
    Returns:
        String processada
    """
    pass
```

### Imports

```python
# Ordem de imports:
# 1. Standard library
import os
import sys
from pathlib import Path

# 2. Third-party
import numpy as np
import torch
from PyQt6.QtWidgets import QMainWindow

# 3. Local
from src.core.intelligence.ai_agent import AIAgent
from src.utils.logger import get_logger
```

---

## 🔒 Segurança

### Dados Sensíveis

```python
# NUNCA commitar API keys
# Use .env
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

# NUNCA fazer:
api_key = "AIza..."  # ❌
```

### Validação de Input

```python
def process_user_input(text: str) -> str:
    # Validar input
    if not text or len(text) > 1000:
        raise ValueError("Input inválido")
    
    # Sanitizar
    text = text.strip()
    
    return text
```

---

## 📚 Recursos

### Documentação
- [Estrutura de Código](code-structure.md)
- [Brain Router](../ai-systems/brain-router.md)
- [Sistema de Aprendizado](../ai-systems/learning-system.md)

### Ferramentas
```bash
# Validação
python tools/validate_project.py

# Diagnóstico
python tools/jarvis_diagnostics.py

# Formatação
black src/
flake8 src/
```

---

## 🤝 Contribuindo

### Workflow

1. **Fork** o projeto
2. **Clone** seu fork
3. **Crie branch** (`git checkout -b feature/nova-feature`)
4. **Desenvolva** e teste
5. **Commit** (`git commit -am 'Adiciona nova feature'`)
6. **Push** (`git push origin feature/nova-feature`)
7. **Pull Request**

### Checklist PR

- [ ] Código formatado (black)
- [ ] Testes passando
- [ ] Documentação atualizada
- [ ] Sem API keys commitadas
- [ ] Changelog atualizado

---

## 🆘 Suporte

### Issues Comuns

**Import Error:**
```python
# Certifique-se de estar no diretório raiz
import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))
```

**Modelo não encontrado:**
```bash
# Baixar modelos
python scripts/install/download_models.py
```

**ChromaDB erro:**
```bash
# Reinstalar
pip uninstall chromadb -y
pip install chromadb==0.4.18
```

---

<div align="center">

**Desenvolvido com ❤️ para o futuro da IA assistiva**

*Última atualização: 2026-02-10*

</div>
