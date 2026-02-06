# 🔧 JARVIS SINGULARITY - Guia de Solução de Problemas

## 📋 Índice
1. [Problemas de Instalação](#problemas-de-instalação)
2. [Problemas de Dependências](#problemas-de-dependências)
3. [Problemas de Execução](#problemas-de-execução)
4. [Problemas de Interface](#problemas-de-interface)
5. [Problemas de Voz](#problemas-de-voz)
6. [Problemas de IA](#problemas-de-ia)
7. [Códigos de Erro](#códigos-de-erro)

---

## 🚀 Início Rápido - Modo Autônomo

### Windows - Launcher Autônomo

O `JARVIS_SINGULARITY.bat` agora é **totalmente autônomo** e faz:

```batch
# Execute com duplo-clique ou:
JARVIS_SINGULARITY.bat
```

**O que ele faz automaticamente:**
1. ✅ Solicita privilégios de administrador
2. ✅ Detecta e instala Python (se necessário)
3. ✅ Cria ambiente virtual
4. ✅ Instala todas as dependências
5. ✅ Valida estrutura do projeto
6. ✅ Inicia o JARVIS
7. ✅ Auto-restart em caso de falha (até 3 tentativas)

**Logs:** Tudo é registrado em `jarvis_launcher.log`

---

## 🔍 Problemas de Instalação

### ❌ Python não encontrado

**Sintoma:**
```
Python nao encontrado no PATH!
```

**Solução Automática:**
O launcher tentará instalar automaticamente via:
1. Windows Package Manager (winget)
2. Chocolatey (se disponível)

**Solução Manual:**
1. Baixe Python 3.10+ de [python.org](https://www.python.org/downloads/)
2. **IMPORTANTE:** Marque "Add Python to PATH" durante instalação
3. Reinicie o terminal
4. Execute novamente `JARVIS_SINGULARITY.bat`

**Verificar instalação:**
```bash
python --version
# Deve mostrar: Python 3.10.x ou superior
```

---

### ❌ Ambiente Virtual não cria

**Sintoma:**
```
Falha ao criar ambiente virtual
```

**Causas possíveis:**
- Falta de permissões
- Espaço em disco insuficiente
- Python não configurado corretamente

**Soluções:**
```bash
# 1. Execute como Administrador
# Clique direito no JARVIS_SINGULARITY.bat > Executar como administrador

# 2. Criar ambiente virtual manualmente
python -m venv venv

# 3. Ativar ambiente virtual
venv\Scripts\activate

# 4. Instalar dependências
pip install -r requirements_singularity.txt
```

---

### ❌ Erro ao instalar dependências

**Sintoma:**
```
Erro ao instalar dependencias
```

**Solução 1: Atualizar pip**
```bash
python -m pip install --upgrade pip
```

**Solução 2: Instalar pacotes críticos individualmente**
```bash
pip install PyQt6
pip install numpy==1.26.4
pip install torch==2.6.0  # SECURITY: Use 2.6.0+ to avoid CVEs
pip install opencv-python
```

**Solução 3: Usar requirements alternativos**
```bash
# Se requirements_singularity.txt falhar, tente:
pip install -r requirements_advanced.txt
```

---

## 📦 Problemas de Dependências

### ❌ NumPy 2.x incompatível

**Sintoma:**
```
numpy 2.0 is not compatible with this version of torch
```

**Causa:**
NumPy 2.x quebra compatibilidade com PyTorch e Whisper

**Solução:**
```bash
# Desinstalar NumPy 2.x
pip uninstall numpy -y

# Instalar versão compatível
pip install numpy==1.26.4

# Reinstalar requirements
pip install -r requirements_singularity.txt
```

---

### ❌ Erro de importação PBKDF2

**Sintoma:**
```
cannot import name 'PBKDF2' from 'cryptography'
```

**Solução:**
```bash
pip install --upgrade cryptography==42.0.5
```

---

### ❌ PyQt6 não encontrado

**Sintoma:**
```
No module named 'PyQt6'
```

**Solução:**
```bash
# Instalar PyQt6
pip install PyQt6==6.6.1

# Se falhar, instalar componentes separadamente
pip install PyQt6-Qt6
pip install PyQt6-sip
```

---

### ❌ Torch não encontrado ou incompatível

**Sintoma:**
```
No module named 'torch'
```

**Solução (CPU version):**
```bash
pip install torch==2.6.0 torchaudio==2.6.0 --index-url https://download.pytorch.org/whl/cpu
```

**Solução (GPU version - NVIDIA):**
```bash
pip install torch==2.6.0 torchaudio==2.6.0 --index-url https://download.pytorch.org/whl/cu118
```

**IMPORTANTE:** Sempre use torch 2.6.0 ou superior para evitar vulnerabilidades de segurança (RCE, heap overflow, use-after-free).

---

## 🎮 Problemas de Execução

### ❌ Entry point não encontrado

**Sintoma:**
```
Entry point nao encontrado!
```

**Solução:**
```bash
# Verificar se existe main.py ou main_singularity.py
dir main*.py

# Se não existir, executar setup_manager
python setup_manager.py

# Ele promoverá main_singularity.py para main.py
```

---

### ❌ Erro ao importar módulos

**Sintoma:**
```
ModuleNotFoundError: No module named 'src.core.ai_agent'
```

**Solução:**
```bash
# 1. Verificar estrutura
python validate_project.py

# 2. Se estrutura OK, problema pode ser PYTHONPATH
# Executar do diretório raiz:
cd C:\Path\To\PROJECT_JARVIS_5.0
python main.py
```

---

### ❌ Sistema reinicia constantemente

**Sintoma:**
```
Tentativa 1 de 3...
Tentativa 2 de 3...
```

**Causa:**
Erro crítico que causa crash imediato

**Solução:**
1. Verificar logs: `type jarvis_launcher.log`
2. Executar validador: `python validate_project.py`
3. Desabilitar auto-restart temporariamente:
   - Editar `JARVIS_SINGULARITY.bat`
   - Mudar `MAX_RETRIES=0`

---

## 🖥️ Problemas de Interface

### ❌ HUD não aparece

**Sintomas:**
- Sistema inicia mas HUD não aparece
- Apenas console visível

**Soluções:**

**1. Verificar PyQt6:**
```bash
python -c "import PyQt6; print('PyQt6 OK')"
```

**2. Testar HUD isoladamente:**
```bash
python src/interface/hud.py
```

**3. Verificar drivers de vídeo:**
- Atualizar drivers da placa de vídeo
- Verificar suporte a OpenGL

**4. Modo Mock (teste):**
Se HUD real falhar, sistema usa HUD Mock automaticamente

---

### ❌ HUD congela ou não responde

**Sintoma:**
HUD aparece mas não atualiza estado

**Causa:**
Thread bloqueado ou problema no event loop

**Solução:**
```bash
# 1. Verificar se está usando versão correta
python -c "from interface.ai_worker import AIWorker; print('V2 OK')"

# 2. Testar AIWorker
python -c "from interface.ai_worker import AIWorker; w = AIWorker(); print('Worker OK')"
```

---

### ❌ HUD aparece em posição errada

**Solução:**
1. Fechar JARVIS
2. Deletar arquivo de configuração de posição (se existir)
3. Reiniciar - HUD volta para posição padrão

---

## 🎤 Problemas de Voz

### ❌ Wake word não detecta

**Sintomas:**
- Dizer "Jarvis" não ativa sistema
- Console não mostra "Wake word detectado"

**Soluções:**

**1. Verificar microfone:**
```bash
# Windows: Configurações > Sistema > Som > Entrada
# Testar microfone e ajustar volume
```

**2. Verificar dependências de voz:**
```bash
pip install SpeechRecognition
pip install pyaudio
pip install vosk
```

**3. Testar reconhecimento:**
```bash
python -c "import speech_recognition as sr; print('SR OK')"
```

**4. Ajustar sensibilidade em `config.yaml`:**
```yaml
voice:
  energy_threshold: 300  # Diminuir = mais sensível
  dynamic_energy: true
```

---

### ❌ Erro "PyAudio não encontrado"

**Sintoma:**
```
No module named 'pyaudio'
```

**Solução Windows:**
```bash
# Baixar wheel pré-compilado
# Para Python 3.10:
pip install pipwin
pipwin install pyaudio

# OU instalar direto:
pip install pyaudio
```

**Se falhar:**
1. Baixar wheel de: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
2. Instalar: `pip install PyAudio‑0.2.11‑cp310‑cp310‑win_amd64.whl`

---

### ❌ TTS não funciona

**Sintoma:**
Sistema processa comandos mas não fala

**Soluções:**

**1. Verificar TTS engine:**
```bash
python -c "import pyttsx3; engine = pyttsx3.init(); engine.say('Teste'); engine.runAndWait()"
```

**2. Alternativa Edge-TTS:**
```bash
pip install edge-tts
```

**3. Verificar config.yaml:**
```yaml
mouth:
  tts_engine: "edge"  # ou "pyttsx3"
  voice: "pt-BR-FranciscaNeural"
```

---

## 🤖 Problemas de IA

### ❌ AI não responde

**Sintomas:**
- Comando processado mas sem resposta
- HUD fica azul (thinking) indefinidamente

**Soluções:**

**1. Verificar API keys:**
```bash
# Verificar variável de ambiente
echo %GOOGLE_API_KEY%

# Se vazio, configurar:
set GOOGLE_API_KEY=sua_chave_aqui
```

**2. Verificar config.yaml:**
```yaml
brain:
  groq_api_key: "gsk_..."
  gemini_api_key: "AIza..."
```

**3. Testar AI isoladamente:**
```bash
python -c "from core.ai_agent import ai_agent; print(ai_agent.process_command('olá'))"
```

---

### ❌ Erro "API key inválida"

**Solução:**
1. Obter nova key:
   - Groq: https://console.groq.com
   - Gemini: https://makersuite.google.com/app/apikey
2. Atualizar em `config.yaml`
3. Reiniciar JARVIS

---

### ❌ Respostas muito lentas

**Causa:**
Usando modelo local ou conexão lenta

**Soluções:**

**1. Usar Groq (mais rápido):**
```yaml
brain:
  router: "groq"
```

**2. Verificar Ollama local:**
```bash
# Se quiser usar local
curl http://localhost:11434
```

---

## 📊 Códigos de Erro

| Código | Significado | Solução |
|--------|-------------|---------|
| 0 | Encerramento normal | Nenhuma ação necessária |
| 1 | Erro genérico | Verificar logs em `jarvis_launcher.log` |
| 130 | Interrompido (Ctrl+C) | Normal - usuário interrompeu |
| 2 | Validação falhou | Executar `python validate_project.py` |

---

## 🛠️ Ferramentas de Diagnóstico

### Validador de Projeto

Valida toda estrutura, sintaxe e dependências:

```bash
python validate_project.py
```

**Verifica:**
- ✅ Estrutura de diretórios
- ✅ Arquivos críticos
- ✅ Sintaxe de todos .py
- ✅ Imports
- ✅ Dependências instaladas
- ✅ Configuração
- ✅ Entry points

---

### Setup Manager

Reorganiza e instala:

```bash
python setup_manager.py
```

**Faz:**
- Cria estrutura de pastas
- Move arquivos legados para backup
- Promove main_singularity.py para main.py
- Instala dependências

---

### Logs

**jarvis_launcher.log:**
- Registro de todas operações do launcher
- Útil para diagnosticar problemas de inicialização

**jarvis_singularity.log:**
- Log da aplicação principal
- Erros de runtime

---

## 🆘 Suporte

### Auto-diagnóstico rápido

```bash
# 1. Validar projeto
python validate_project.py

# 2. Verificar Python e pip
python --version
pip --version

# 3. Verificar dependências críticas
python -c "import PyQt6, torch, numpy; print('OK')"

# 4. Ver logs
type jarvis_launcher.log
```

---

### Resetar instalação

Se tudo falhar, reset completo:

```bash
# 1. Deletar ambiente virtual
rmdir /s /q venv

# 2. Limpar cache pip
pip cache purge

# 3. Executar launcher novamente
JARVIS_SINGULARITY.bat
```

---

## 📞 Obtendo Ajuda

1. 🔍 **Buscar no log:** `jarvis_launcher.log`
2. 🧪 **Executar validador:** `python validate_project.py`
3. 📖 **Ler documentação:** `README.md`, `HOW_TO_START.md`
4. 🐛 **Reportar issue:** GitHub Issues

---

## ✅ Checklist de Verificação

Antes de reportar problema, verificar:

- [ ] Python 3.10+ instalado
- [ ] Executando como Administrador
- [ ] Antivírus não bloqueando
- [ ] Espaço em disco suficiente (>5GB)
- [ ] Internet conectada (para download de deps)
- [ ] `validate_project.py` passou
- [ ] Logs verificados

---

**Última Atualização:** 06/02/2026  
**Versão:** 2.0 - Autonomous Launcher
