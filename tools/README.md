# 🛠️ JARVIS 5.0 - Tools Directory

Esta pasta contém scripts de diagnóstico, validação e utilitários para o sistema JARVIS 5.0.

---

## 📋 **ÍNDICE DE FERRAMENTAS**

### **1. Diagnósticos Completos** 🏥

#### `full_diagnostics.py` ⭐ **PRINCIPAL**
Diagnóstico completo do sistema com relatório HTML detalhado.

**Uso:**
```bash
python tools/full_diagnostics.py
```

**Verifica:**
- ✅ Informações do sistema (OS, Python, Hardware)
- ✅ Ambiente Python e virtual environment
- ✅ Dependências críticas e versões
- ✅ Stack de ML (torch, transformers, etc)
- ✅ Arquivos de configuração e encoding
- ✅ Estrutura de diretórios
- ✅ Health status dos módulos principais
- ✅ Gera recomendações automáticas
- ✅ Salva relatório HTML em `data/diagnostics/`

---

#### `jarvis_diagnostics.py` ⚡ **RÁPIDO**
Diagnóstico rápido de dependências e conectividade.

**Uso:**
```bash
python tools/jarvis_diagnostics.py
```

**Verifica:**
- ✅ 8 dependências críticas (PyQt6, speech_recognition, etc)
- ✅ 8 módulos core do JARVIS
- ✅ Hardware de áudio (microfones)
- ✅ Conectividade (Ollama + Gemini API)

---

#### `diagnostico.py` 🚀 **BOOT**
Diagnóstico de boot em 6 etapas.

**Uso:**
```bash
python tools/diagnostico.py
```

**Verifica:**
- ✅ Configurações
- ✅ Hardware Manager
- ✅ Banco de Dados
- ✅ AI Agent
- ✅ Visão (FaceRec/MediaPipe)
- ✅ Voz (Vosk/Edge-TTS)

---

### **2. Validação de Features** ✨

#### `validate_p0_p1.py` 🎯 **VALIDAÇÃO COMPLETA**
Valida todas as features P0 e P1 do roadmap.

**Uso:**
```bash
python tools/validate_p0_p1.py
```

**Testa 8 Features:**
- ✅ **P0.1**: Wake Word Detection (Porcupine)
- ✅ **P0.2**: Voice Cloning (XTTS-v2)
- ✅ **P1.1**: Semantic Caching (Vision)
- ✅ **P1.2**: Noise Reduction
- ✅ **P1.3**: Response Caching (Voice)
- ✅ **P1.4**: RAG Reranking (CrossEncoder)
- ✅ **P1.5**: UI-Specific YOLO Training
- ✅ **P1.6**: RAG Upgrade (Jina v3)

**Saída Esperada:**
```
Result: 8/8 features validated
🎉 ALL FEATURES VALIDATED SUCCESSFULLY!
```

---

#### `verify_neural_expansion.py` 🧠 **NEURAL**
Verifica expansão neural Phase 1.

**Uso:**
```bash
python tools/verify_neural_expansion.py
```

**Testa:**
- ✅ Voice Emotion Analysis
- ✅ Cross-Modal Fusion
- ✅ Métodos disponíveis (transcribe_realtime, diarize, etc)

---

### **3. Verificação de Instalação** 📦

#### `verify_install.py` ✅ **INSTALAÇÃO**
Verifica se todas as dependências estão instaladas.

**Uso:**
```bash
python tools/verify_install.py
```

**Verifica 18 módulos:**
- pyautogui, cv2, speech_recognition, pyttsx3, edge_tts
- psutil, pyaudio, customtkinter, mss, pygame
- sqlalchemy, transformers, sentence_transformers, chromadb
- PIL, requests, numpy, googlesearch, fer, librosa, pystray
- pytesseract, spacy, packaging, reportlab, pandas, openpyxl

**Exit Codes:**
- `0` = Tudo OK
- `1` = Faltam pacotes

---

#### `check_binaries.py` 🔍 **BINÁRIOS**
Verifica versões e paths de bibliotecas críticas.

**Uso:**
```bash
python tools/check_binaries.py
```

**Verifica:**
- ✅ numpy (versão + path)
- ✅ torch (versão + path)
- ✅ chromadb (versão + API)
- ✅ onnxruntime
- ✅ sqlite3
- ✅ pysqlite3

---

#### `check_libs.py` 📚 **LIBS ESPECÍFICAS**
Verifica bibliotecas de visão.

**Uso:**
```bash
python tools/check_libs.py
```

**Verifica:**
- ✅ face_recognition (versão)
- ✅ dlib (CUDA status)
- ✅ cv2 (versão)

---

### **4. Utilitários Especiais** 🛠️

#### `benchmark_p0.py` ⚡ **PERFORMANCE**
Benchmark de performance P0.

**Uso:**
```bash
python tools/benchmark_p0.py
```

**Testa:**
- ✅ OCR Latency (5 tentativas)
- ✅ Target: <500ms com GPU
- ✅ Boot Time Analysis

**Saída Esperada:**
```
>> OCR AVG: 350ms | ✅ PASS
```

---

#### `record_voice_sample.py` 🎤 **VOZ**
Grava amostra de voz para clonagem.

**Uso:**
```bash
python tools/record_voice_sample.py
```

**Configuração:**
- Duração: 10 segundos
- Sample Rate: 22050 Hz
- Formato: WAV mono
- Salva em: `data/voice_signatures/william.wav`

**Instruções:**
1. Execute o script
2. Fale naturalmente por 10 segundos
3. Varie a entonação para melhor qualidade
4. Arquivo será salvo automaticamente

---

#### `jarvis_health_json.py` 📊 **JSON**
Health check em formato JSON (útil para CI/CD).

**Uso:**
```bash
python tools/jarvis_health_json.py
```

**Saída:**
```json
{
  "dependencies": {
    "PyQt6": "OK",
    "torch": "OK",
    ...
  },
  "core_modules": {
    "core.ai_agent": "OK",
    ...
  },
  "hardware": {
    "mics": ["Microfone (Realtek...)", ...]
  },
  "env": {
    "GOOGLE_API_KEY": "SET"
  }
}
```

---

## 🚀 **FLUXO DE TRABALHO RECOMENDADO**

### **Após Instalação:**
```bash
# 1. Verificar instalação básica
python tools/verify_install.py

# 2. Diagnóstico completo
python tools/full_diagnostics.py

# 3. Validar features P0+P1
python tools/validate_p0_p1.py

# 4. Benchmark de performance
python tools/benchmark_p0.py
```

### **Troubleshooting:**
```bash
# Diagnóstico rápido
python tools/jarvis_diagnostics.py

# Verificar binários específicos
python tools/check_binaries.py
python tools/check_libs.py

# Health check JSON
python tools/jarvis_health_json.py > health.json
```

### **Antes de Deploy:**
```bash
# Validação completa
python tools/full_diagnostics.py
python tools/validate_p0_p1.py
python tools/verify_neural_expansion.py
```

---

## 📝 **NOTAS IMPORTANTES**

### **Paths Corrigidos** ✅
Todos os scripts agora usam `Path(__file__).parent.parent` para garantir paths corretos independente do diretório de execução.

### **Compatibilidade**
- ✅ Windows 10/11
- ✅ Python 3.11+
- ✅ Virtual Environment recomendado

### **Logs**
Alguns scripts geram logs em:
- `data/diagnostics/` - Relatórios HTML
- `data/logs/` - Logs de execução

---

## 🆘 **TROUBLESHOOTING COMUM**

### **Erro: "Module not found"**
```bash
# Certifique-se de estar no ambiente virtual
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Reinstale dependências
pip install -r requirements.txt
```

### **Erro: "No module named 'src'"**
```bash
# Execute do diretório raiz do projeto
cd C:\Users\willi\Documents\GitHub\PROJECT_JARVIS_5.0
python tools/script_name.py
```

### **Erro: "Ollama offline"**
```bash
# Inicie o Ollama
ollama serve

# Ou verifique se está rodando
curl http://localhost:11434
```

---

## 📊 **ESTATÍSTICAS**

- **Total de Scripts**: 11
- **Linhas de Código**: ~1,500
- **Cobertura de Testes**: 8 features P0+P1
- **Tempo de Execução**: <30s (diagnóstico completo)

---

## 🔄 **ATUALIZAÇÕES**

### **v1.1 (2026-02-09)**
- ✅ Corrigidos paths em `diagnostico.py`, `jarvis_diagnostics.py`, `jarvis_health_json.py`
- ✅ Adicionado README.md
- ✅ Validação completa da pasta

### **v1.0 (Inicial)**
- ✅ 11 scripts de diagnóstico e validação
- ✅ Suporte completo para P0+P1 features

---

**Desenvolvido por**: William (JARVIS 5.0 Team)  
**Última Atualização**: 2026-02-09
