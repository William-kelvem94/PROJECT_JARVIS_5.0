# 🔧 JARVIS 5.0 - Guia de Troubleshooting

## Índice
- [Problemas Críticos (P0)](#problemas-críticos-p0)
- [Problemas Comuns (P1)](#problemas-comuns-p1)
- [Otimizações e Ajustes](#otimizações-e-ajustes)
- [Ferramentas de Diagnóstico](#ferramentas-de-diagnóstico)
- [FAQ](#faq)

---

## Problemas Críticos (P0)

### ❌ Erro: c10.dll falha ao carregar (WinError 1114)

**Sintomas:**
```
[WinError 1114] Uma rotina de inicialização da biblioteca de vínculo dinâmico (DLL) falhou
Error loading "...\torch\lib\c10.dll" or one of its dependencies
```
- EasyOCR não disponível (OCR disabled)
- Ultralytics não disponível (YOLO detection disabled)
- faster-whisper não disponível (STT disabled)
- torch não carrega

**Causa Raiz:**
PyTorch requer Visual C++ Runtime libraries (msvcp140.dll, vcruntime140.dll) que não estão instaladas ou estão corrompidas.

**Solução:**

1. **Instalar Visual C++ Redistributables 2015-2022:**
   ```
   Download: https://aka.ms/vs/17/release/vc_redist.x64.exe
   ```
   - Execute o instalador com permissões de administrador
   - **IMPORTANTE**: Reinicie o computador após instalação
   - Verifique instalação: Painel de Controle → Programas → "Microsoft Visual C++ 2015-2022"

2. **Verificar instalação:**
   ```bash
   venv\Scripts\python -c "import torch; print('Torch OK:', torch.__version__)"
   ```

3. **Se persistir, reinstalar PyTorch:**
   ```bash
   venv\Scripts\pip uninstall torch torchvision torchaudio -y
   venv\Scripts\pip install torch==2.2.2 torchvision==0.17.2 torchaudio==2.2.2
   ```

---

### ❌ Erro: NumPy 2.x incompatibilidade

**Sintomas:**
```
A module that was compiled using NumPy 1.x cannot be run in NumPy 2.4.2 as it may crash
```
- Sistema falha ao importar torch, whisper, face_recognition
- Crashes aleatórios em operações ML

**Causa Raiz:**
NumPy 2.x foi instalado, mas PyTorch 2.2.2, OpenAI Whisper e outras bibliotecas foram compiladas para NumPy 1.x.

**Solução:**

1. **Verificar versão do NumPy:**
   ```bash
   venv\Scripts\python -c "import numpy; print(numpy.__version__)"
   ```

2. **Se for 2.x, fazer downgrade:**
   ```bash
   venv\Scripts\pip uninstall numpy torch face-recognition ultralytics easyocr -y
   venv\Scripts\pip install "numpy==1.26.4"
   venv\Scripts\pip install -r requirements.txt
   ```

3. **Validar:**
   ```bash
   venv\Scripts\python -c "import numpy, torch; print(f'NumPy: {numpy.__version__}, Torch: {torch.__version__}')"
   ```
   - **Deve mostrar:** `NumPy: 1.26.4, Torch: 2.2.2+cpu`

**Prevenção:**
- Sempre usar ambiente virtual (venv)
- Não instalar pacotes globalmente
- Respeitar versões travadas em requirements.txt

---

### ❌ Erro: ModuleNotFoundError: No module named 'onnxruntime'

**Sintomas:**
- Crash report menciona onnxruntime faltando
- Algumas features de inferência ONNX não funcionam

**Causa Raiz:**
Dependência onnxruntime estava comentada em requirements.txt.

**Solução:**
```bash
venv\Scripts\pip install onnxruntime==1.17.0
```

---

## Problemas Comuns (P1)

### ⚠️  Testes falhando: MockVoice.speak() got unexpected keyword argument 'wait'

**Sintomas:**
```bash
python tests\rigorous_stark_test.py
# StarkRigorousTester._setup_mocks.<locals>.MockVoice.speak() got an unexpected keyword argument 'wait'
```

**Causa Raiz:**
Mock de teste não corresponde à assinatura real do método `speak()` em voice_controller.

**Solução:**
✅ **JÁ CORRIGIDO NESTA VERSÃO**

Se encontrar o erro, atualize `tests/rigorous_stark_test.py`:
```python
class MockVoice:
    def __init__(self): 
        self._is_speaking = False
    def speak(self, text, mode='online', wait=False):  # Adicionar wait=False
        pass
    def stop(self): 
        pass
```

---

### ⚠️  Gesture Controller: 'NoneType' object has no attribute 'process'

**Sintomas:**
- Crashes ao processar frames de gesture recognition
- Erro: `AttributeError: 'NoneType' object has no attribute 'process'`

**Causa Raiz:**
Singleton `gesture_controller` é acessado antes de `start_background_loading()` completar.

**Solução:**
✅ **JÁ CORRIGIDO NESTA VERSÃO**

Proteção adicionada em `gesture_controller.py`:
```python
def process_frame(self, frame):
    if not MEDIAPIPE_AVAILABLE or self.hands is None:
        return frame, "MediaPipe Not Ready"
    # ... resto do código
```

---

### ⚠️  Erro de Encoding: 'charmap' codec can't decode byte 0x8d

**Sintomas:**
- Falha ao carregar config.yaml ou settings.json
- Erro: `UnicodeDecodeError: 'charmap' codec can't decode byte 0x8d`

**Causa Raiz:**
Arquivos de configuração contêm caracteres UTF-8 mas sistema tenta ler com encoding padrão Windows (cp1252).

**Solução 1 - Corrigir arquivos:**
1. Abrir arquivo problemático no VS Code
2. Canto inferior direito: clicar no encoding atual
3. Selecionar "Save with Encoding" → "UTF-8"
4. Salvar

**Solução 2 - Forçar UTF-8 no código:**
✅ **JÁ APLICADO em config.py**

Todos os `open()` agora usam `encoding='utf-8'`:
```python
with open(config_file, 'r', encoding='utf-8') as f:
    content = f.read()
```

---

### ⚠️  Face Recognition: compute_face_descriptor() incompatible arguments

**Sintomas:**
- Logs inundados com erros de face_recognition
- Mensagem: `compute_face_descriptor(): incompatible function arguments`
- Consumo alto de CPU no loop de câmera

**Causa Raiz:**
API `compute_face_descriptor()` não é para uso direto. Deve-se usar `face_encodings()`.

**Solução:**
Verificar se `camera_controller.py` usa a API correta:
```python
# ❌ ERRADO (gera erro)
descriptor = face_recognition.compute_face_descriptor(model, frame, location)

# ✅ CORRETO
face_encodings_list = face_recognition.face_encodings(
    frame,
    known_face_locations=[face_location],
    num_jitters=1,
    model='large'
)
if face_encodings_list:
    descriptor = face_encodings_list[0]
```

---

## Otimizações e Ajustes

### 🚀 Logs crescendo infinitamente

**Problema:** `jarvis_singularity.log` com 50MB+ consumindo disco.

**Solução:**
✅ **Sistema de log rotation implementado**

Usar novo `LoggingConfig`:
```python
from src.utils.logging_config import LoggingConfig

logger = LoggingConfig.setup_rotating_logger(
    logger_name="jarvis",
    log_file=Path("data/logs/jarvis_singularity.log"),
    max_bytes=10*1024*1024,  # 10MB
    backup_count=5            # 5 backups = 50MB total
)
```

---

### 🚀 Boot lento (>30 segundos)

**Causas comuns:**
1. Modelos ML carregando na inicialização
2. ChromaDB carregando embeddings grandes
3. Imports bloqueando event loop

**Soluções:**

1. **Lazy loading de modelos:**
   ```python
   # Adiar carregamento até primeira uso
   self.model = None
   
   def _ensure_model(self):
       if self.model is None:
           self.model = load_heavy_model()
   ```

2. **Background loading:**
   ```python
   threading.Thread(target=self._load_models, daemon=True).start()
   ```

3. **Profile startup:**
   ```bash
   python -m cProfile -o startup.prof main.py
   python -m pstats startup.prof
   ```

---

### 🚀 Status UNKNOWN em todos os módulos

**Problema:** `SYSTEM_PULSE.md` mostra todos módulos como 🟡 UNKNOWN.

**Causa:** Health checks não implementados ou orchestrator não atualiza status.

**Solução:**
✅ **Métodos `get_module_status()` implementados no orchestrator**

Verificar saúde do sistema:
```python
from src.core.orchestrator import StarkOrchestrator

orchestrator = StarkOrchestrator(jarvis_core)
health = orchestrator.get_system_health()
print(health)  # {'vision': 'ONLINE', 'audio': 'ONLINE', ...}
```

---

## Ferramentas de Diagnóstico

### 🔬 Script de Diagnóstico Completo

Execute para análise automática de todo o sistema:

```bash
venv\Scripts\python tools\full_diagnostics.py
```

**Output:**
- Verifica versões de dependências
- Testa carregamento de DLLs (c10.dll)
- Valida encoding de configs
- Health check de todos módulos
- **Gera relatório HTML em `data/diagnostics.html`**

---

### 🧪 Testes Específicos

**Testar stack ML:**
```bash
venv\Scripts\python -c "import torch; import easyocr; import ultralytics; print('ML Stack: OK')"
```

**Testar visão:**
```bash
venv\Scripts\python -c "from src.core.vision.vision_system import vision_system; print(vision_system)"
```

**Testar áudio:**
```bash
venv\Scripts\python -c "from src.core.audio.voice_controller import voice_controller; print(voice_controller)"
```

**Testar suite completa:**
```bash
venv\Scripts\python tests\rigorous_stark_test.py
```

---

### 📊 Verificar Logs

**Logs principais:**
```
data/logs/jarvis_singularity.log  # Log principal do sistema
data/logs/vision.log              # Subsistema de visão
data/logs/audio.log               # Subsistema de áudio
data/logs/errors.log              # Apenas erros
```

**Buscar erros recentes:**
```bash
# PowerShell
Get-Content data\logs\jarvis_singularity.log -Tail 50 | Select-String "ERROR|CRITICAL"

# CMD
powershell "Select-String -Path 'data\logs\jarvis_singularity.log' -Pattern 'ERROR|CRITICAL' | Select-Object -Last 20"
```

---

## FAQ

### ❓ O sistema inicia mas não responde a comandos de voz

**Checklist:**
1. Microfone configurado como padrão no Windows
2. Permissões de microfone concedidas
3. Vosk model baixado em `models/vosk-model-small-pt-0.3/`
4. `config.yaml` → `audio.wake_word_enabled: false` (ou configure wake word)

**Teste rápido:**
```bash
venv\Scripts\python tests\test_mic.py
```

---

### ❓ Face recognition não funciona

**Possíveis causas:**
1. **Biblioteca não instalada** (requer Visual C++ Build Tools)
   ```bash
   pip install dlib face-recognition
   ```
2. **Nenhuma face cadastrada** em `data/faces/`
3. **Câmera não detectada**

**Teste:**
```bash
venv\Scripts\python tests\test_face_recognition.py
```

---

### ❓ GUI não abre / Tela preta

**Checklist:**
1. PyQt6 instalado corretamente
2. Drivers de vídeo atualizados
3. Não está rodando via SSH/RDP (GUI requer sessão local)

**Forçar modo dashboard:**
```python
# Em config.yaml
interface:
  hud_enabled: false  # Desabilita HUD overlay
```

---

### ❓ Consumo alto de CPU/RAM

**Análise:**
```bash
venv\Scripts\python tools\benchmark_p0.py
```

**Otimizações:**
1. Desabilitar vision loop contínuo se não usar:
   ```yaml
   # config.yaml
   senses:
     vision_level: "fast"  # ou "disabled"
   ```

2. Limitar modelos ML:
   ```yaml
   vision:
     yolo_enabled: false  # Desabilita YOLO
   ```

3. Reduzir qualidade TTS:
   ```yaml
   mouth:
     tts_engine: "pyttsx3"  # Mais leve que edge-tts
   ```

---

### ❓ Como atualizar o sistema?

```bash
git pull origin main
venv\Scripts\pip install -r requirements.txt --upgrade
venv\Scripts\python tools\full_diagnostics.py  # Verificar saúde
```

---

### ❓ Como fazer backup/restore?

**Backup:**
```bash
# Backup de dados do usuário
xcopy data\* backup\data\ /E /I /Y
xcopy config\* backup\config\ /E /I /Y
```

**Restore:**
```bash
xcopy backup\data\* data\ /E /I /Y
xcopy backup\config\* config\ /E /I /Y
```

---

## 📞 Suporte

**Se nada resolver:**

1. **Gerar diagnóstico completo:**
   ```bash
   venv\Scripts\python tools\full_diagnostics.py
   ```

2. **Coletar informações:**
   - Arquivo `data/diagnostics.html`
   - Logs recentes de `data/logs/`
   - Output de `venv\Scripts\pip list`
   - Screenshot do erro (se aplicável)

3. **Abrir issue no GitHub** com todas as informações acima

---

**Última atualização:** 2026-02-08  
**Versão:** JARVIS 5.0 - Singularity Architecture
