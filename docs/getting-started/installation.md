# 🚀 JARVIS 5.0 - Guia de Instalação

**Versão Atualizada**: 2026-02-10

---

## 📋 Requisitos do Sistema

### Mínimo
- **SO**: Windows 10/11 (64-bit)
- **Python**: 3.11 ou superior ⭐
- **RAM**: 8 GB
- **Espaço**: 10 GB livre
- **Microfone**: Para comandos de voz
- **Webcam**: Opcional (para FaceID)

### Recomendado
- **SO**: Windows 11
- **Python**: 3.11+
- **RAM**: 16 GB ou mais
- **GPU**: NVIDIA GTX 1060+ (6GB VRAM)
- **SSD**: Para melhor performance
- **Internet**: Para modelos cloud (Gemini)

---

## 🔧 Instalação Automática (Recomendado)

### Método 1: Launcher Completo

1. **Clone o repositório**
```bash
git clone https://github.com/seu-usuario/PROJECT_JARVIS_5.0.git
cd PROJECT_JARVIS_5.0
```

2. **Execute o instalador**
```bash
# Windows
START_JARVIS.bat
```

O launcher faz TUDO automaticamente:
- ✅ Cria ambiente virtual
- ✅ Instala todas as dependências
- ✅ Baixa modelos de IA
- ✅ Configura Ollama
- ✅ Inicia o sistema

---

## 🛠️ Instalação Manual

### 1. Clone o Repositório
```bash
git clone https://github.com/seu-usuario/PROJECT_JARVIS_5.0.git
cd PROJECT_JARVIS_5.0
```

### 2. Instale Python 3.11+
- Download: https://www.python.org/downloads/
- ⚠️ **IMPORTANTE**: Marque "Add Python to PATH"

### 3. Crie Ambiente Virtual
```bash
python -m venv venv
venv\Scripts\activate
```

### 4. Instale Dependências
```bash
# Instalar via script
python scripts/install/total_installer.py

# OU manualmente
pip install -r scripts/install/requirements.txt
```

### 5. Configure API Keys (Opcional)
Crie arquivo `.env` na raiz:
```env
GOOGLE_API_KEY=sua_chave_gemini_aqui
```

### 6. Instale Ollama (Opcional - para IA local)
```bash
# Download: https://ollama.ai/download
# Após instalar:
ollama pull gemma3:4b
```

### 7. Execute JARVIS
```bash
python SINGULARITY_LAUNCHER.py
```

---

## 📦 Dependências

### Core (Essenciais)
```txt
# IA
google-generativeai>=0.8.0
transformers>=4.36.0
torch==2.2.2
sentence-transformers>=2.2.0

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
requests>=2.31.0
```

### Modelos de IA (Auto-download)
- ✅ YOLOv8n (6.5 MB) - Detecção de objetos
- ✅ MediaPipe Hand Landmarker (7.8 MB) - Rastreamento de mãos
- ✅ Vosk PT-BR Small (~40 MB) - Reconhecimento de voz

---

## ⚙️ Configuração

### 1. Configuração Principal (`config/ai_config.yaml`)

```yaml
# Modelos Ollama (Local)
ollama_models:
  tier_ultra:
    - deepseek-r1:7b
  tier_pro:
    - gemma3:4b      # ⭐ Recomendado
    - qwen2.5:7b
  tier_fast:
    - gemma3

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

### 2. API Keys (`.env`)
```env
# Google Gemini (Obrigatório para cloud)
GOOGLE_API_KEY=AIza...

# Opcional
OPENAI_API_KEY=sk-...
```

### 3. Configurações de Voz
```yaml
# Em config/ai_config.yaml
voice:
  stt_engine: "vosk"        # vosk, whisper
  tts_engine: "edge"        # edge, pyttsx3
  language: "pt-BR"
```

---

## 🧪 Verificação da Instalação

### Teste Automático
```bash
# Executar validação completa
python tools/validate_project.py

# Diagnóstico rápido
python tools/jarvis_diagnostics.py

# Diagnóstico completo com HTML
python tools/full_diagnostics.py
```

### Testes Manuais

#### 1. Python
```bash
python --version
# Deve mostrar: Python 3.11.x ou superior
```

#### 2. Dependências Core
```bash
python -c "from PyQt6.QtWidgets import QApplication; print('PyQt6 OK')"
python -c "import torch; print('PyTorch OK')"
python -c "import cv2; print('OpenCV OK')"
```

#### 3. Modelos de IA
```bash
# Verificar YOLOv8
python -c "from ultralytics import YOLO; m = YOLO('models/vision/yolov8n.pt'); print('YOLO OK')"

# Verificar Vosk
python -c "from vosk import Model; print('Vosk OK')"
```

#### 4. Ollama (se instalado)
```bash
ollama list
# Deve mostrar: gemma3:4b ou outros modelos
```

#### 5. Sistema Completo
```bash
python SINGULARITY_LAUNCHER.py
# Deve iniciar sem erros
```

---

## 📁 Estrutura Pós-Instalação

```
PROJECT_JARVIS_5.0/
├── venv/                   # Ambiente virtual (criado)
├── data/                   # Dados (criado automaticamente)
│   ├── chroma_db/         # Memórias vetoriais
│   ├── learning/          # Dados de aprendizado
│   ├── logs/              # Logs do sistema
│   └── faces/             # Banco de faces
├── models/                 # Modelos de IA
│   ├── vision/
│   │   ├── yolov8n.pt    # ✅ Baixado
│   │   └── hand_landmarker.task  # ✅ Baixado
│   └── speech/
│       └── vosk-model-small-pt-0.3/  # ✅ Baixado
├── logs/                   # Logs runtime
│   └── jarvis.log
└── .env                    # Suas API keys (criar)
```

---

## 🐛 Solução de Problemas

### Python não encontrado
```bash
# Verifique instalação
python --version

# Se não funcionar, tente:
py --version

# Reinstale Python de python.org
# ⚠️ MARQUE "Add Python to PATH"
```

### PyQt6 falha ao instalar
```bash
# Atualize pip
python -m pip install --upgrade pip

# Instale PyQt6
python -m pip install PyQt6

# Se falhar, instale wheel primeiro
python -m pip install wheel
python -m pip install PyQt6
```

### PyTorch falha (Windows)
```bash
# Use o instalador automático
python scripts/install/quick_fix_torch.py

# OU instale manualmente (CPU)
pip install torch==2.2.2 torchvision==0.17.2 --index-url https://download.pytorch.org/whl/cpu
```

### ChromaDB erro de DLL
```bash
# Reinstale com versão específica
pip uninstall chromadb -y
pip install chromadb==0.4.18
```

### Ollama não encontrado
```bash
# Baixe de: https://ollama.ai/download
# Após instalar:
ollama serve  # Inicia servidor
ollama pull gemma3:4b  # Baixa modelo
```

### Erro de encoding (emojis)
✅ Já corrigido automaticamente
- UTF-8 configurado em todos os scripts

### Modelos não encontrados
```bash
# Execute download manual
python scripts/install/download_models.py
```

---

## 🚀 Próximos Passos

1. ✅ **Instalação completa**
2. ⏭️ **Configure API keys** (`.env`)
3. ⏭️ **Instale Ollama** (opcional, para IA local)
4. ⏭️ **Execute** `START_JARVIS.bat`
5. ⏭️ **Teste** dizendo "JARVIS"
6. ⏭️ **Leia** [quick-start.md](quick-start.md)

---

## 💡 Dicas Importantes

### Primeira Execução
- ⏱️ Pode demorar (download de modelos)
- 🌐 Requer internet (para Gemini)
- 💾 Ocupa ~2 GB de espaço

### Performance
- 🎮 **GPU**: Detectada automaticamente (CUDA)
- 🔌 **Offline**: Funciona com Ollama local
- ⚡ **Rápido**: Gemma3:4b responde em ~1s

### Segurança
- 🔒 API keys em `.env` (não commitar!)
- 🛡️ Dados locais em `data/`
- 🔐 Modo privado disponível (força local)

---

## 📊 Requisitos de Hardware por Funcionalidade

| Funcionalidade | RAM | GPU | Espaço |
|----------------|-----|-----|--------|
| **Básico** (Voz + Cloud) | 4 GB | - | 2 GB |
| **Visão** (YOLO + OCR) | 8 GB | Recomendado | 5 GB |
| **Ollama Local** (Gemma3) | 8 GB | - | 8 GB |
| **Completo** (Tudo) | 16 GB | GTX 1060+ | 15 GB |

---

## 🆘 Suporte

### Documentação
- 📚 [Guia Rápido](quick-start.md)
- 🧠 [Brain Router](../ai-systems/brain-router.md)
- 🎓 [Sistema de Aprendizado](../ai-systems/learning-system.md)

### Ferramentas
```bash
# Validação completa
python tools/validate_project.py

# Diagnóstico
python tools/jarvis_diagnostics.py

# Verificar features
python tools/validate_p0_p1.py
```

### Logs
- 📄 `logs/jarvis.log` - Log principal
- 📄 `logs/jarvis_auto_*.log` - Logs automáticos
- 📄 `logs/total_installer.log` - Log de instalação

---

**Instalação concluída!** 🎉

Execute `START_JARVIS.bat` para começar!

---

<div align="center">

**Desenvolvido com ❤️ para o futuro da IA assistiva**

*Última atualização: 2026-02-10*

</div>
