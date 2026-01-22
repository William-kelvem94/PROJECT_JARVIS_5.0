# 🎯 Quick Start - JARVIS 5.0 Novos Recursos

## Instalação Rápida

### 1. Instalação Básica (Funciona sem dependências extras)

```bash
# Clone o repositório (se ainda não clonou)
git clone <repo-url>
cd PROJECT_JARVIS_5.0

# Instale dependências básicas
pip install -r requirements.txt
```

**✅ Recursos disponíveis:**
- ✅ Memória persistente
- ✅ Sistema de segurança
- ✅ Task decomposition
- ✅ Integração manager
- ❌ Voz avançada (requer instalação adicional)
- ❌ Calendar/Email (requer configuração)

### 2. Instalação Completa (Todos os recursos)

```bash
# Instalar todas as dependências opcionais
pip install openai-whisper sounddevice soundfile TTS pvporcupine
pip install google-auth-oauthlib google-api-python-client
pip install SpeechRecognition pyttsx3

# Para GPU (muito mais rápido)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

**✅ Todos os recursos disponíveis:**
- ✅ Whisper STT (reconhecimento de alta qualidade)
- ✅ Coqui TTS (voz natural)
- ✅ Wake word detector
- ✅ Calendar/Email (após configuração)
- ✅ Segurança e permissões
- ✅ Task decomposition

---

## 🚀 Uso Rápido

### Exemplo 1: JARVIS Básico (Sem dependências extras)

```python
from jarvis_integration import quick_start

# Iniciar JARVIS em modo básico
jarvis = quick_start(mode="basic")

# Processar comando
response = jarvis.process_command("pesquisar clima hoje")
print(response)

# Ver status
print(jarvis.get_status())
```

**Saída esperada:**
```
Comando recebido: pesquisar clima hoje
{
  'voice_available': True,
  'calendar_available': False,
  'email_available': False,
  'security_enabled': True,
  'task_planning_enabled': False,
  'wake_word_active': None
}
```

---

### Exemplo 2: Teste dos Recursos

```bash
# Executar script de demonstração
python exemplos_jarvis_5.py
```

Este script testa todos os módulos e mostra:
- ✅ Quais recursos estão funcionando
- ⚠️ Quais precisam de instalação adicional
- 📝 Como usar cada recurso

**Saída esperada:**
```
============================================================
    🤖 JARVIS 5.0 - Demonstração de Recursos
============================================================

EXEMPLO 8: Memória Persistente
✅ Memória persistente ativa!
📊 Conversas: 4, Preferências: 2

EXEMPLO 4: Sistema de Segurança
✅ Sistema de segurança ativo!
✅ Pesquisar (permitido), ❌ Deletar arquivo (bloqueado)

...
```

---

### Exemplo 3: Usando Memória Persistente

```python
from modules.memory.persistent_memory import PersistentMemory

# Inicializar memória
memory = PersistentMemory()

# Salvar conversa
memory.save_conversation("user", "Qual é o clima hoje?")
memory.save_conversation("assistant", "Está ensolarado com 25°C")

# Recuperar histórico
history = memory.get_conversation_history(limit=10)
for msg in history:
    print(f"{msg['role']}: {msg['content']}")

# Salvar preferências
memory.save_user_preference("idioma", "pt-BR")
memory.save_user_preference("voz_velocidade", 150)

# Recuperar preferência
idioma = memory.get_user_preference("idioma")
```

---

### Exemplo 4: Sistema de Segurança

```python
from modules.system.security_module import SecurityManager, PermissionLevel

# Inicializar
security = SecurityManager()

# Definir nível de permissão
security.set_permission_level(PermissionLevel.USER)

# Verificar permissões
if security.check_permission("open_app"):
    print("Permitido abrir aplicativo")

# Verificar comando perigoso
is_safe, reason = security.is_safe_command("rm -rf /")
if not is_safe:
    print(f"BLOQUEADO: {reason}")

# Comando crítico requer confirmação
if security.requires_confirmation("shutdown"):
    confirmed = security.request_confirmation(
        "shutdown",
        "Desligar o sistema"
    )
    if confirmed:
        print("Comando confirmado")
```

---

### Exemplo 5: Task Decomposition

```python
from modules.processing.task_decomposition import TaskDecomposer, TaskExecutor

# Criar decompositor e executor
decomposer = TaskDecomposer()
executor = TaskExecutor()

# Decompor tarefa complexa
plan = decomposer.decompose("Enviar email para João sobre reunião amanhã")

# Ver tarefas geradas
print(f"Plano: {len(plan.tasks)} tarefas")
for task in plan.tasks:
    print(f"- {task.description} ({task.action})")

# Registrar handlers
def open_app_handler(params):
    print(f"Abrindo app: {params}")
    return {"success": True}

executor.register_handler("open_app", open_app_handler)
# ... registrar outros handlers

# Executar plano
success = executor.execute_plan(plan)
print(f"Plano executado: {success}")
```

---

## 🎤 Recursos Avançados de Voz

### Whisper STT (Requer instalação)

```bash
pip install openai-whisper sounddevice soundfile
```

```python
from modules.input.whisper_module import WhisperModule

# Inicializar Whisper
whisper = WhisperModule(model_name="base", language="pt")

# Gravar e transcrever
text = whisper.listen(duration=5.0)
print(f"Você disse: {text}")

# Ou transcrever arquivo
text = whisper.transcribe_file("audio.wav")
```

**Modelos disponíveis:**
- `tiny` - Mais rápido, menos preciso (~1GB VRAM)
- `base` - Bom equilíbrio (recomendado) (~1GB VRAM)
- `small` - Mais preciso (~2GB VRAM)
- `medium` - Muito preciso (~5GB VRAM)
- `large` - Máxima qualidade (~10GB VRAM)

---

### Coqui TTS - Voz Natural (Requer instalação)

```bash
pip install TTS sounddevice soundfile
```

```python
from modules.input.advanced_tts import AdvancedTTSModule

# Inicializar TTS
tts = AdvancedTTSModule(backend="coqui", language="pt")

# Falar texto
tts.speak("Olá, eu sou o JARVIS!")

# Modo assíncrono (não bloqueia)
tts.speak_async("Processando sua requisição...")

# Salvar em arquivo
audio_file = tts.speak(
    "Bem-vindo ao JARVIS 5.0",
    output_file="welcome.wav",
    play_audio=False
)
```

---

### Wake Word Detector (Requer instalação)

```bash
pip install pvporcupine  # Ou apenas SpeechRecognition para versão simples
```

```python
from modules.input.wake_word_detector import SimpleWakeWordDetector

def on_wake_word(keyword):
    print(f"JARVIS ativado! ({keyword})")
    # Processar comando aqui

# Inicializar detector
detector = SimpleWakeWordDetector(
    keywords=["jarvis", "hey jarvis"],
    callback=on_wake_word
)

# Iniciar detecção
detector.start()
print("Diga 'Hey JARVIS' para ativar...")

# Manter rodando
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    detector.stop()
```

---

## 🔗 Integrações (Google Calendar e Gmail)

### 1. Obter Credenciais do Google

1. Acesse: https://console.cloud.google.com/
2. Crie um projeto novo
3. Habilite as APIs:
   - Google Calendar API
   - Gmail API
4. Crie credenciais OAuth 2.0
5. Baixe o arquivo JSON
6. Salve em:
   - `config/calendar_credentials.json` (para calendar)
   - `config/email_credentials.json` (para email)

### 2. Instalar Dependências

```bash
pip install google-auth-oauthlib google-api-python-client
```

### 3. Usar Calendar

```python
from modules.action.calendar_integration import CalendarIntegration
from datetime import datetime, timedelta

# Inicializar
calendar = CalendarIntegration(provider="google")

# Criar evento
tomorrow = datetime.now() + timedelta(days=1)
event = calendar.create_event(
    summary="Reunião com equipe",
    start_time=tomorrow.replace(hour=15, minute=0),
    description="Discutir projeto JARVIS",
    attendees=["joao@email.com"]
)

# Listar próximos eventos
events = calendar.list_events(max_results=5)
for event in events:
    print(f"- {event['summary']}")

# Próximo compromisso
next_event = calendar.get_next_event()
```

### 4. Usar Email

```python
from modules.action.email_integration import EmailIntegration

# Inicializar
email = EmailIntegration(provider="gmail")

# Enviar email
email.send_email(
    to="destinatario@email.com",
    subject="Relatório JARVIS",
    body="Segue o relatório..."
)

# Ver emails não lidos
unread = email.list_messages(query="is:unread")
print(f"{len(unread)} emails não lidos")

# Últimos emails
latest = email.get_latest_messages(count=5)
for msg in latest:
    print(f"- {msg['subject']} ({msg['from']})")
```

---

## 📊 Status dos Recursos

Execute para ver quais recursos estão disponíveis:

```python
from jarvis_integration import quick_start

jarvis = quick_start(mode="full")
status = jarvis.get_status()

print("Status do Sistema:")
for key, value in status.items():
    symbol = "✅" if value else "❌"
    print(f"{symbol} {key}: {value}")
```

**Saída esperada:**

```
Status do Sistema:
✅ voice_available: True
❌ calendar_available: False (requer configuração)
❌ email_available: False (requer configuração)
✅ security_enabled: True
✅ task_planning_enabled: True
❌ wake_word_active: None (requer instalação)
```

---

## 🐛 Troubleshooting

### Erro: "Whisper não disponível"

```bash
pip install openai-whisper sounddevice soundfile numpy
```

### Erro: "Coqui TTS não disponível"

```bash
pip install TTS sounddevice soundfile
```

### Erro: "Google API não disponível"

```bash
pip install google-auth-oauthlib google-api-python-client
```

### Erro: "numpy not found" ou "name 'np' is not defined"

```bash
pip install numpy<2.0.0
```

### Calendar/Email não funcionam

1. Verifique se credenciais estão em `config/calendar_credentials.json`
2. Primeira execução abrirá navegador para autorização
3. Token será salvo em `config/token.pickle` ou `config/gmail_token.pickle`

---

## 📚 Documentação Completa

- **[MELHORIAS_JARVIS_5.0.md](MELHORIAS_JARVIS_5.0.md)** - Documentação completa de todos os recursos
- **[exemplos_jarvis_5.py](exemplos_jarvis_5.py)** - Exemplos práticos de uso
- **[jarvis_integration.py](jarvis_integration.py)** - API de integração

---

## 🎯 Próximos Passos

1. **Testar recursos básicos:**
   ```bash
   python exemplos_jarvis_5.py
   ```

2. **Instalar recursos de voz:**
   ```bash
   pip install openai-whisper TTS sounddevice soundfile
   ```

3. **Configurar integrações:**
   - Obter credenciais do Google
   - Configurar Calendar e Gmail

4. **Personalizar configurações:**
   - Editar `config/security.json`
   - Ajustar preferências

5. **Integrar com seu projeto:**
   ```python
   from jarvis_integration import quick_start
   jarvis = quick_start(mode="full")
   ```

---

## 💡 Dicas

- Use `mode="basic"` se não quiser instalar dependências extras
- Use `mode="voice"` para recursos de voz avançados
- Use `mode="full"` para todos os recursos
- Wake word funciona melhor com Porcupine (requer API key)
- Whisper `base` é o melhor equilíbrio qualidade/velocidade
- Coqui TTS pode demorar na primeira execução (baixa modelos)

---

## 🤝 Suporte

Problemas ou dúvidas? Abra uma issue ou consulte a documentação completa em `MELHORIAS_JARVIS_5.0.md`.

---

<div align="center">

**JARVIS 5.0 - Seu Assistente Pessoal Inteligente**

✨ Desenvolvido com tecnologias Open Source ✨

</div>
