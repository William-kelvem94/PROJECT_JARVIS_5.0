# 🚀 JARVIS 5.0 - Guia de Instalação

## 📋 Requisitos do Sistema

### Mínimo
- **SO**: Windows 10/11 (64-bit)
- **Python**: 3.10 ou superior
- **RAM**: 4 GB
- **Espaço**: 2 GB livre
- **Microfone**: Para comandos de voz
- **Webcam**: Opcional (para FaceID)

### Recomendado
- **SO**: Windows 11
- **Python**: 3.11+
- **RAM**: 8 GB ou mais
- **GPU**: NVIDIA (para aceleração)
- **SSD**: Para melhor performance

---

## 🔧 Instalação Rápida

### Método 1: Launcher Automático (Recomendado)

1. **Clone o repositório**
```bash
git clone https://github.com/seu-usuario/PROJECT_JARVIS_5.0.git
cd PROJECT_JARVIS_5.0
```

2. **Execute o launcher**
```bash
JARVIS.bat
```

Pronto! O launcher instala tudo automaticamente.

---

### Método 2: Instalação Manual

1. **Clone o repositório**
```bash
git clone https://github.com/seu-usuario/PROJECT_JARVIS_5.0.git
cd PROJECT_JARVIS_5.0
```

2. **Instale Python 3.10+**
- Download: https://www.python.org/downloads/
- ⚠️ Marque "Add Python to PATH"

3. **Instale dependências**
```bash
# Dependências essenciais
python -m pip install PyQt6

# Dependências completas
pip install -r requirements.txt
```

4. **Execute JARVIS**
```bash
python main_singularity.py
```

---

## 📦 Dependências

### Essenciais (Auto-instaladas)
```
PyQt6>=6.0.0          # Interface HUD
```

### Core (requirements.txt)
```
numpy<2
opencv-python
SpeechRecognition
pyttsx3
edge-tts
pygame
psutil
pyaudio
mss
sqlalchemy
pillow
pytesseract
vosk
```

### Avançadas (requirements_advanced.txt)
```
torch>=2.0.0
transformers>=4.30.0
easyocr>=1.7.0
openai-whisper>=20231117
google-generativeai>=0.3.0
ultralytics>=8.0.0
```

---

## ⚙️ Configuração

### 1. API Keys (Opcional)

Edite `config.yaml`:

```yaml
brain:
  groq_api_key: "gsk_..."      # https://console.groq.com
  gemini_api_key: "AI..."      # https://makersuite.google.com
```

### 2. Configurações de Voz

```yaml
senses:
  hearing_model: "base"        # tiny, base, small, medium, large

mouth:
  tts_engine: "edge"          # edge, xtts
  voice: "pt-BR-FranciscaNeural"
```

### 3. Interface

```yaml
interface:
  hud_enabled: true
  transparency: 0.9
  orb_color: "#00D9FF"
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

### PyAudio falha (Windows)
```bash
# Baixe wheel pré-compilado:
# https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio

# Instale o arquivo .whl baixado:
pip install PyAudio‑0.2.11‑cp310‑cp310‑win_amd64.whl
```

### Face Recognition falha
```bash
# Requer CMake e dlib
# Veja: docs/install_face_recognition.md

# Ou desabilite em config.yaml:
# (Face recognition é opcional)
```

### Erro de encoding (emojis)
✅ Já corrigido em `main_singularity.py`
- UTF-8 configurado automaticamente

---

## 🧪 Verificação da Instalação

### Teste 1: Python
```bash
python --version
# Deve mostrar: Python 3.10.x ou superior
```

### Teste 2: PyQt6
```bash
python -c "from PyQt6.QtWidgets import QApplication; print('PyQt6 OK')"
```

### Teste 3: Voice
```bash
python -c "import speech_recognition; print('Voice OK')"
```

### Teste 4: HUD
```bash
python src/interface/hud.py
# Deve aparecer reator pulsante
```

### Teste 5: Sistema Completo
```bash
python main_singularity.py
# Deve iniciar HUD + Voice + AI
```

---

## 📁 Estrutura Pós-Instalação

```
PROJECT_JARVIS_5.0/
├── data/                   # Criado automaticamente
│   ├── captures/
│   ├── processed/
│   └── database.db
├── logs/                   # Criado automaticamente
│   └── jarvis_singularity.log
└── config.yaml            # Suas configurações
```

---

## 🚀 Próximos Passos

1. ✅ Instalação completa
2. ⏭️ Configure API keys (opcional)
3. ⏭️ Execute `JARVIS.bat`
4. ⏭️ Teste dizendo "Jarvis"
5. ⏭️ Leia [HOW_TO_START.md](../HOW_TO_START.md)

---

## 💡 Dicas

- **Primeira execução**: Pode demorar (download de modelos)
- **GPU**: Detectada automaticamente se disponível
- **Offline**: Funciona sem API keys (IA local)
- **Logs**: Veja `jarvis_singularity.log` para debug

---

**Instalação concluída!** 🎉

Execute `JARVIS.bat` para começar!
