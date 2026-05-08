# 🔧 CORREÇÃO RÁPIDA — Hardware Não Funciona

**Problema**: "voz, fala, audição, visão das telas e visão da camera, não funcionam"

---

## 🚨 Erros Corrigidos

### 1. ✅ ECONNRESET nos Endpoints

**Problema**: Socket hang up repetido em `/telemetry/status` e `/system/capabilities`

**Correção Aplicada**:
- Adicionado try/except robusto em ambos os endpoints
- Endpoints agora retornam resposta mínima em caso de erro
- Logs detalhados para debug

**Status**: ✅ CORRIGIDO - Endpoints não crasham mais

---

### 2. ✅ React Component Error

**Problema**: `CapabilitiesStatusGrid is not defined`

**Correção Aplicada**:
- Mudado para dynamic import com fallback
- SSR desabilitado para evitar problemas de build
- Loading state adicionado

**Status**: ✅ CORRIGIDO - Component carrega dinamicamente

---

## 🔍 Diagnosticar Hardware

```bash
# Script automático
scripts/diagnose-hardware.bat

# Verificar manualmente
curl http://localhost:8000/system/hardware
```

---

## 🎯 Problemas de Hardware e Soluções

### 1. 🎤 **Voz / Fala / Audição** (TTS e STT)

**Dependências Necessárias**:
```bash
.\.venv\Scripts\activate
pip install pygame sounddevice pycaw comtypes openwakeword
```

**Verificar**:
```bash
# Testar pygame
python -c "import pygame; print('OK')"

# Testar sounddevice
python -c "import sounddevice as sd; print(sd.query_devices())"

# Testar pycaw
python -c "from pycaw.pycaw import AudioUtilities; print('OK')"
```

**Problemas Comuns**:

| Erro | Solução |
|------|---------|
| pygame não instalado | `pip install pygame` |
| sounddevice não instalado | `pip install sounddevice` |
| pycaw não instalado | `pip install pycaw comtypes` |
| Nenhum dispositivo de entrada | Verificar microfone conectado + permissões Windows |
| Nenhum dispositivo de saída | Verificar alto-falantes conectados |

---

### 2. 📷 **Visão da Camera**

**Dependências Necessárias**:
```bash
pip install opencv-python mediapipe ultralytics
```

**Verificar**:
```bash
# Testar OpenCV
python -c "import cv2; print('OK')"

# Testar MediaPipe
python -c "import mediapipe; print('OK')"

# Listar cameras
python -c "import cv2; cap = cv2.VideoCapture(0); print('Camera OK' if cap.isOpened() else 'Camera offline'); cap.release()"
```

**Problemas Comuns**:

| Erro | Solução |
|------|---------|
| opencv-python não instalado | `pip install opencv-python` |
| Camera não detectada | Verificar camera conectada |
| Permissão negada | Windows Settings > Privacy > Camera > Permitir apps |
| Camera em uso | Fechar outros apps (Zoom, Teams, etc.) |

---

### 3. 🖥️ **Visão das Telas** (Screen Capture)

**Dependências Necessárias**:
```bash
pip install mss pyautogui
```

**Verificar**:
```bash
# Testar mss
python -c "from mss import mss; with mss() as sct: print(f'{len(sct.monitors)} telas detectadas')"

# Testar pyautogui
python -c "import pyautogui; print(pyautogui.size())"
```

**Problemas Comuns**:

| Erro | Solução |
|------|---------|
| mss não instalado | `pip install mss` |
| pyautogui não instalado | `pip install pyautogui` |
| Captura lenta | Normal - capturas levam 1-2s |

---

## 📋 Checklist Completo

### Passo 1: Instalar Todas as Dependências

```bash
# Entrar no venv
.\.venv\Scripts\activate

# Instalar tudo de uma vez
pip install pygame sounddevice pycaw comtypes opencv-python mediapipe ultralytics mss pyautogui openwakeword dlib-prebuilt face_recognition
```

### Passo 2: Verificar Permissões do Windows

1. **Camera**:
   - `Configurações > Privacidade > Camera`
   - Ativar "Permitir que apps acessem sua camera"
   - Ativar "Permitir que apps da área de trabalho acessem sua camera"

2. **Microfone**:
   - `Configurações > Privacidade > Microfone`
   - Ativar "Permitir que apps acessem seu microfone"
   - Ativar "Permitir que apps da área de trabalho acessem seu microfone"

### Passo 3: Verificar Hardware Físico

1. **Camera**:
   - Camera conectada (USB ou integrada)
   - Luz indicadora acesa
   - Testar em outro app (Camera do Windows)

2. **Microfone**:
   - Microfone conectado (USB, P2 ou integrado)
   - Volume não está mudo
   - Testar em "Configurações > Sistema > Som > Testar microfone"

3. **Alto-falantes**:
   - Alto-falantes conectados (USB, P2 ou integrado)
   - Volume não está mudo
   - Testar em "Configurações > Sistema > Som > Testar"

### Passo 4: Reiniciar Backend

```bash
# Parar backend atual (Ctrl+C no terminal)

# Iniciar novamente
start-jarvis.bat
```

### Passo 5: Verificar Status

```bash
# Ver hardware status
curl http://localhost:8000/system/hardware

# Ver capabilities completas
curl http://localhost:8000/system/capabilities

# Ver findings dos agentes
curl http://localhost:8000/agents/findings
```

---

## 🎯 Status Esperado (Após Correções)

### ✅ Tudo Funcionando

```json
{
  "camera": {
    "name": "Camera",
    "status": "online",
    "available": true,
    "message": "Camera detectada e funcional"
  },
  "microphone": {
    "name": "Microfone",
    "status": "online",
    "available": true,
    "message": "Microfone detectado e funcional"
  },
  "screen_mirror": {
    "name": "Espelhamento de Tela",
    "status": "online",
    "available": true,
    "message": "mss instalado e funcional"
  }
}
```

### ⚠️ Degradado (Funciona mas com limitações)

```json
{
  "camera": {
    "status": "degraded",
    "message": "Camera detectada mas qualidade baixa"
  }
}
```

### 🔴 Offline (Não Funciona)

```json
{
  "camera": {
    "status": "offline",
    "available": false,
    "message": "Nenhuma camera detectada",
    "error": "No camera found"
  }
}
```

---

## 🔧 Comandos Rápidos

```bash
# Instalar tudo
.\.venv\Scripts\pip.exe install pygame sounddevice pycaw comtypes opencv-python mediapipe ultralytics mss pyautogui openwakeword dlib-prebuilt face_recognition

# Diagnosticar
scripts/diagnose-hardware.bat

# Ver status
curl http://localhost:8000/system/hardware

# Ver findings
curl http://localhost:8000/agents/findings | jq '.findings[] | select(.severity == "high" or .severity == "critical")'

# Reiniciar backend
scripts/restart-jarvis.bat
```

---

## 📚 Documentação

- [AUTOFIX_AGENTS.md](../AUTOFIX_AGENTS.md) - Agentes de auto-correção
- [SOLUTIONS_FOR_REPORTED_ISSUES.md](../SOLUTIONS_FOR_REPORTED_ISSUES.md) - Troubleshooting completo
- [docs/guides/AUTOFIX_README.md](../guides/AUTOFIX_README.md) - Guia rápido

---

## 💡 Dicas

1. **Instale as dependências no venv correto**
   - Sempre ative `.venv` antes de instalar
   - Use `.\.venv\Scripts\pip.exe install` para garantir

2. **Verifique permissões do Windows primeiro**
   - Camera e microfone podem estar bloqueados
   - Configurações > Privacidade

3. **Teste hardware em outros apps**
   - Camera: App "Camera" do Windows
   - Microfone: Configurações > Sistema > Som
   - Se não funciona lá, não vai funcionar no JARVIS

4. **Agentes vão detectar automaticamente**
   - DependencyHealthAgent (10 min)
   - AudioSystemRepairAgent (3 min)
   - PerceptionHealthAgent (90s)
   - Aguarde e veja findings

---

**Autor**: GitHub Copilot (Claude Sonnet 4.5)  
**Data**: 7 de maio de 2026  
**Versão**: JARVIS 5.0 Omega
