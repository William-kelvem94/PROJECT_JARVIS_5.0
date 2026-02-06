# 🪟 Guia de Instalação para Windows

## 🚀 Instalação Rápida (Recomendada)

### Passo 1: Executar o Launcher
```bash
JARVIS.bat
```

O launcher automaticamente:
1. ✅ Verifica se Python está instalado
2. ✅ Cria ambiente virtual
3. ✅ Instala dependências
4. ✅ Inicia o JARVIS

**NOTA:** Algumas dependências podem falhar (ex: dlib) - isto é **normal** e o sistema funcionará mesmo assim.

---

## ⚠️ Problemas Comuns no Windows

### 1. "JARVIS.bat abre e fecha imediatamente"

**Causa:** Arquivos necessários não encontrados ou erro de instalação.

**Solução:**
```bash
# Verifique os logs
type jarvis_launcher.log

# Execute manualmente para ver erros
python main.py
```

### 2. "dlib failed to build" ou "Building wheel for dlib failed"

**Causa:** dlib requer Visual C++ Build Tools para compilar no Windows.

**Solução 1 - Ignorar (Recomendado):**
O sistema funciona perfeitamente sem dlib. O dlib é usado apenas para reconhecimento facial (FaceID), que é um recurso opcional.

```bash
# Continue a instalação normalmente - o erro pode ser ignorado
```

**Solução 2 - Instalar Build Tools (Opcional):**
Se você realmente precisa do FaceID:

1. Instale [Visual Studio Build Tools](https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2022)
2. Durante instalação, selecione "Desktop development with C++"
3. Depois instale dlib:
   ```bash
   pip install dlib
   pip install face-recognition
   ```

**Solução 3 - Usar versão pré-compilada:**
```bash
# Baixe wheel pré-compilado do PyPI ou use conda
conda install -c conda-forge dlib
```

### 3. "Python não encontrado" ou "python is not recognized"

**Solução:**
1. Instale Python 3.10+ de [python.org](https://www.python.org/downloads/)
2. Durante instalação, **marque "Add Python to PATH"**
3. Reinicie o terminal
4. Verifique: `python --version`

### 4. "ModuleNotFoundError: No module named 'PyQt6'"

**Solução:**
```bash
# Instale manualmente
pip install PyQt6==6.6.1
```

### 5. "numpy.dtype size changed" ou conflitos numpy

**Causa:** Versão incompatível do numpy.

**Solução:**
```bash
# Desinstale e reinstale versão correta
pip uninstall numpy -y
pip install numpy==1.26.4
```

---

## 🔧 Instalação Manual (Se o launcher falhar)

### 1. Criar ambiente virtual
```bash
python -m venv venv
venv\Scripts\activate
```

### 2. Atualizar pip
```bash
python -m pip install --upgrade pip
```

### 3. Instalar pacotes críticos primeiro
```bash
pip install numpy==1.26.4
pip install PyQt6==6.6.1
pip install opencv-python
```

### 4. Instalar dependências principais
```bash
# Instalar tudo
pip install -r requirements.txt

# OU instalar sem dependências problemáticas
pip install -r requirements.txt --no-deps
pip install -r requirements.txt
```

### 5. Executar JARVIS
```bash
python main.py
```

---

## 📦 Dependências Opcionais

Estas dependências podem falhar na instalação mas **NÃO** impedem o funcionamento:

| Pacote | Usado para | Necessário? |
|--------|------------|-------------|
| `dlib` | Reconhecimento facial (FaceID) | ❌ Opcional |
| `face-recognition` | Reconhecimento facial | ❌ Opcional |
| `mediapipe` | Detecção de gestos | ❌ Opcional |
| `whisper` | Transcrição de voz avançada | ❌ Opcional |
| `easyocr` | OCR multilíngue | ⚠️ Recomendado |

### Recursos Essenciais (Sempre Funcionam):
- ✅ Interface HUD
- ✅ Captura de tela
- ✅ Controle por voz básico
- ✅ AI Agent (Groq/Gemini)
- ✅ Automação de sistema

---

## 🐛 Debug Avançado

### Ver logs detalhados
```bash
# Logs do launcher
type jarvis_launcher.log

# Logs do sistema
type data\logs\singularity.log
```

### Testar imports
```bash
python -c "import PyQt6; print('PyQt6 OK')"
python -c "import cv2; print('OpenCV OK')"
python -c "import torch; print('Torch OK')"
```

### Verificar versões
```bash
pip list | findstr numpy
pip list | findstr PyQt6
pip list | findstr torch
```

### Instalar em modo verbose
```bash
pip install -r requirements.txt -v
```

---

## 💡 Dicas

### 1. Use ambiente virtual
Sempre use venv para evitar conflitos com outros projetos Python:
```bash
python -m venv venv
venv\Scripts\activate
```

### 2. Mantenha pip atualizado
```bash
python -m pip install --upgrade pip
```

### 3. Instale dependências gradualmente
Se tiver problemas, instale em grupos:
```bash
# Grupo 1: Core
pip install numpy==1.26.4 Pillow PyQt6

# Grupo 2: Visão
pip install opencv-python mss

# Grupo 3: IA
pip install torch transformers

# Grupo 4: Opcionais (podem falhar - OK)
pip install dlib face-recognition mediapipe
```

### 4. Limpe cache do pip
Se tiver erros persistentes:
```bash
pip cache purge
pip install -r requirements.txt --no-cache-dir
```

---

## 🎯 Verificação de Instalação

Depois de instalar, teste:

```bash
# 1. Validar sistema
python validate.py

# 2. Testar imports críticos
python -c "from PyQt6.QtWidgets import QApplication; print('GUI: OK')"
python -c "import cv2; print('Vision: OK')"
python -c "import torch; print('AI: OK')"

# 3. Executar JARVIS
python main.py
```

---

## 📞 Ainda com Problemas?

1. ✅ Verifique `jarvis_launcher.log`
2. ✅ Execute `python validate.py`
3. ✅ Verifique [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
4. ✅ Procure o erro específico na documentação
5. ✅ Abra uma [issue no GitHub](https://github.com/William-kelvem94/PROJECT_JARVIS_5.0/issues)

---

## ✅ Instalação Bem-Sucedida?

Após instalação, você deve ver:
```
✅ JARVIS ONLINE
🔵 HUD transparente no canto da tela
🎤 Sistema aguardando comandos de voz
```

**Atalhos de teclado:**
- `Ctrl+Shift+J` - Toggle Dashboard
- `Ctrl+Shift+H` - Toggle HUD
- `Ctrl+Shift+X` - Ocultar tudo

---

**Última atualização:** 2026-02-06  
**Versão:** JARVIS Singularity v2.0  
**Plataforma:** Windows 10/11
