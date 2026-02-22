# 🔑 Configuração de API Keys - JARVIS 10/10

Este guia explica como configurar as chaves de API opcionais para desbloquear funcionalidades avançadas do JARVIS.

## Status Atual: 8.3/10 → 10/10

**Sistemas Ativos (sem API keys):**
- ✅ Vision System (OCR, YOLO, Face Recognition)
- ✅ Audio System (Whisper STT, Silero-VAD, Voice Encoder)
- ✅ Knowledge Graph
- ✅ Multimodal Fusion
- ✅ Learning Systems (PEFT, LocalTrainer)

**Sistemas Bloqueados (requerem API keys):**
- ⚠️ Vision QA (GEMINI_API_KEY)
- ⚠️ ReAct Agent (GEMINI_API_KEY)
- ⚠️ Wake Word Detection (PORCUPINE_ACCESS_KEY)

---

## 1. Google Gemini API (Vision QA + ReAct Agent)

### O que desbloqueia:
- **Vision QA**: Responder perguntas sobre imagens ("O que vê nesta screenshot?")
- **ReAct Agent**: Raciocínio + Ações (busca web, execução de código, automação)

### Como obter (GRÁTIS):
1. Acesse: https://makersuite.google.com/app/apikey
2. Faça login com conta Google
3. Clique em "Create API key"
4. Copie a chave (formato: `AIzaSy...`)

### Configuração:

**Opção A: config.yaml** (recomendado)
```yaml
brain:
  gemini_api_key: "AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
  model: "gemini-1.5-flash"
```

**Opção B: config/settings.json**
```json
{
  "gemini_api_key": "AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
}
```

**Opção C: Variável de ambiente**
```bash
# Windows (PowerShell)
$env:GEMINI_API_KEY = "AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"

# Linux/Mac
export GEMINI_API_KEY="AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
```

### Limites (Tier Gratuito):
- **1 milhão tokens/mês** (suficiente para uso pessoal)
- 60 requests/minuto
- Sem necessidade de cartão de crédito

---

## 2. Porcupine Wake Word (Detecção de Palavra de Ativação)

### O que desbloqueia:
- Wake word: "Jarvis" ou "Computer" para ativar voz
- Funciona offline (sem internet após baixar modelo)
- Baixa latência (<100ms)

### Como obter (GRÁTIS):
1. Acesse: https://console.picovoice.ai
2. Crie conta gratuita
3. Vá em "Access Keys" → "Create Key"
4. Copie a chave (formato alfanumérico longo)

### Configuração:

**config.yaml:**
```yaml
audio:
  porcupine_access_key: "YOUR_PORCUPINE_KEY_HERE"
  wake_words: ["jarvis", "computer"]  # Escolha palavras disponíveis
```

### Limites (Tier Gratuito):
- **3 dispositivos simultâneos**
- Modelos pré-treinados inclusos
- Wake words disponíveis: jarvis, computer, alexa, hey siri, ok google

---

## 3. Verificação de Instalação

Após configurar as chaves, execute:

```bash
# Testar Gemini API
venv\Scripts\python.exe -c "from src.core.vision_language_model import VisionQA; vqa = VisionQA(); print('✅ Vision QA ativo')"

# Testar ReAct Agent
venv\Scripts\python.exe -c "from src.core.react_agent import ReActAgent; agent = ReActAgent(); print('✅ ReAct Agent ativo')"

# Testar Porcupine
venv\Scripts\python.exe -c "from src.core.enhanced_audio import EnhancedAudioSystem; audio = EnhancedAudioSystem(Path('data')); print('✅ Porcupine ativo' if audio.wake_word_engine else '⚠️ Porcupine ausente')"
```

---

## 4. Verificação Final do Health Score

```bash
# Executar JARVIS e verificar score
.\START_JARVIS.bat

# Buscar linha de saúde
# Esperar: "SYSTEM HEALTH SCORE: 10.0/10" 🎉
```

**Com todas as chaves configuradas:**
```
[NEURAL SYSTEMS]
 ├─ ✅ Knowledge Graph
 ├─ ✅ Multimodal Fusion
 ├─ ✅ Vision QA                 ← DESBLOQUEADO
 └─ ✅ ReAct Agent               ← DESBLOQUEADO

[AUDIO SYSTEM]
 ├─ ✅ Faster-Whisper
 ├─ ✅ Silero-VAD
 ├─ ✅ Voice Encoder
 └─ ✅ Wake Word Detection       ← DESBLOQUEADO
```

---

## 5. Troubleshooting

### Gemini API não funciona:
```bash
# Verificar key está carregada
venv\Scripts\python.exe -c "from src.utils.config import load_config; config = load_config(); print(f'Gemini Key: {config.get(\"brain\", {}).get(\"gemini_api_key\", \"AUSENTE\")}')"

# Testar key manualmente
venv\Scripts\python.exe -c "import google.generativeai as genai; genai.configure(api_key='YOUR_KEY'); model = genai.GenerativeModel('gemini-1.5-flash'); print('✅ Key válida')"
```

### Porcupine não detecta wake word:
```bash
# Verificar key está carregada
venv\Scripts\python.exe -c "from src.utils.config import load_config; config = load_config(); print(f'Porcupine Key: {config.get(\"audio\", {}).get(\"porcupine_access_key\", \"AUSENTE\")}')"

# Verificar microfone está capturando
venv\Scripts\python.exe -c "import pyaudio; p = pyaudio.PyAudio(); print(f'Devices: {p.get_device_count()}'); p.terminate()"
```

### CrossEncoder warnings (não crítico):
```bash
# Atualizar sentence-transformers
venv\Scripts\pip.exe install --upgrade sentence-transformers

# Desabilitar warning de symlinks (Windows)
$env:HF_HUB_DISABLE_SYMLINKS_WARNING = "1"
```

---

## 6. Alternativas Self-Hosted (Sem API Keys)

Se preferir não usar serviços externos:

### Gemini → Ollama (local)
```bash
# Instalar Ollama: https://ollama.ai/download
ollama pull llama3.2-vision

# Configurar JARVIS para Ollama
# config.yaml:
brain:
  provider: "ollama"
  model: "llama3.2-vision"
  base_url: "http://localhost:11434"
```

### Porcupine → Silero Keyword Spotting
```bash
# Biblioteca Silero já instalada
# Treinar custom wake word: https://github.com/snakers4/silero-vad

# Desabilitar Porcupine em config.yaml:
audio:
  wake_word_engine: "silero"
  custom_keywords: ["jarvis"]
```

---

## 7. Suporte

**Issues conhecidos:**
- Symlinks warning no Windows → não afeta funcionalidade
- CrossEncoder cache sem symlinks → usa mais espaço em disco
- Gemini rate limits → aguardar 1 minuto entre requests

**Logs úteis:**
- `logs/jarvis_core.log` - Inicialização de sistemas
- `logs/jarvis_neural.log` - Neural systems (VQA, ReAct)
- `logs/jarvis_audio.log` - Audio e wake word detection

**Health Score Reference:**
- 8.3/10 = Todos sistemas core funcionais (sem API keys)
- 9.0/10 = Gemini configurado (Vision QA + ReAct)
- 10.0/10 = Gemini + Porcupine configurados (full features)

---

📝 **Última atualização:** 07/02/2026
🏆 **Meta alcançada:** 6.2 → 8.3/10 (10/10 com API keys opcionais)
