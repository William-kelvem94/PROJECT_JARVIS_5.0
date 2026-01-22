# 🚀 JARVIS 5.0 - Melhorias Implementadas

## Visão Geral

Este documento descreve as melhorias implementadas no JARVIS 5.0 para transformá-lo em um assistente pessoal completo e funcional, baseado na análise do projeto.

## 📋 Índice

1. [Fase 1: Voz e Interação Natural](#fase-1-voz-e-interação-natural)
2. [Fase 2: Memória e Personalização](#fase-2-memória-e-personalização)
3. [Fase 3: Automação Avançada](#fase-3-automação-avançada)
4. [Fase 4: Segurança e Produção](#fase-4-segurança-e-produção)
5. [Instalação](#instalação)
6. [Uso](#uso)
7. [Roadmap](#roadmap)

---

## Fase 1: Voz e Interação Natural

### 🎤 Whisper Module - STT de Alta Qualidade

**Arquivo:** `modules/input/whisper_module.py`

Reconhecimento de voz offline usando OpenAI Whisper, oferecendo qualidade superior ao Google STT.

**Características:**
- Reconhecimento offline de alta qualidade
- Suporte a múltiplos idiomas
- 5 modelos disponíveis (tiny, base, small, medium, large)
- Suporte a GPU para aceleração

**Modelos Disponíveis:**
| Modelo | Parâmetros | Velocidade | Qualidade | VRAM |
|--------|------------|------------|-----------|------|
| tiny   | 39M        | Muito rápido | Básica | ~1GB |
| base   | 74M        | Rápido     | Boa    | ~1GB |
| small  | 244M       | Médio      | Muito boa | ~2GB |
| medium | 769M       | Lento      | Excelente | ~5GB |
| large  | 1550M      | Muito lento | Máxima | ~10GB |

**Exemplo de Uso:**
```python
from modules.input.whisper_module import WhisperModule

# Inicializar módulo
whisper = WhisperModule(model_name="base", language="pt")

# Gravar e transcrever
text = whisper.listen(duration=5.0)
print(f"Você disse: {text}")

# Transcrever arquivo
text = whisper.transcribe_file("audio.wav")
```

**Instalação:**
```bash
pip install openai-whisper sounddevice soundfile
```

---

### 🔔 Wake Word Detector - "Hey JARVIS"

**Arquivo:** `modules/input/wake_word_detector.py`

Detecção de palavra de ativação para interação hands-free.

**Características:**
- Detecção contínua em background
- Baseado em Porcupine (alta precisão)
- Baixo consumo de recursos
- Fallback para reconhecimento simples

**Exemplo de Uso:**
```python
from modules.input.wake_word_detector import WakeWordDetector

def on_wake_word(keyword_index):
    print("JARVIS ativado!")
    # Iniciar escuta

# Com Porcupine (requer API key)
detector = WakeWordDetector(
    access_key="YOUR_PORCUPINE_KEY",
    keywords=["jarvis"],
    callback=on_wake_word
)
detector.start()

# Ou versão simples (sem API key)
from modules.input.wake_word_detector import SimpleWakeWordDetector
simple_detector = SimpleWakeWordDetector(
    keywords=["jarvis", "hey jarvis"],
    callback=on_wake_word
)
simple_detector.start()
```

**Obter API Key:**
- Acesse: https://console.picovoice.ai/
- Crie conta gratuita
- Copie sua Access Key

---

### 🔊 Advanced TTS - Voz Natural

**Arquivo:** `modules/input/advanced_tts.py`

Text-to-Speech de alta qualidade usando Coqui TTS.

**Características:**
- Voz muito mais natural que pyttsx3
- Suporte a múltiplos idiomas e speakers
- Modelos multi-speaker (vozes diferentes)
- Geração de áudio em arquivo ou reprodução direta

**Modelos Recomendados:**
- **Português:** `tts_models/pt/cv/vits` ou `tts_models/multilingual/multi-dataset/xtts_v2`
- **Inglês:** `tts_models/en/ljspeech/tacotron2-DDC`
- **Multilingual:** `tts_models/multilingual/multi-dataset/xtts_v2` (melhor qualidade)

**Exemplo de Uso:**
```python
from modules.input.advanced_tts import AdvancedTTSModule

# Inicializar
tts = AdvancedTTSModule(backend="coqui", language="pt")

# Falar texto
tts.speak("Olá, eu sou o JARVIS!")

# Salvar em arquivo
audio_file = tts.speak(
    "Bem-vindo ao JARVIS 5.0",
    output_file="welcome.wav",
    play_audio=False
)

# Modo assíncrono (não bloqueia)
tts.speak_async("Processando sua requisição...")
```

**Instalação:**
```bash
pip install TTS sounddevice soundfile
```

---

## Fase 2: Memória e Personalização

### 💾 Persistent Memory (Já Implementado)

**Arquivo:** `modules/memory/persistent_memory.py`

Sistema de memória persistente usando SQLite para armazenar:
- Histórico de conversas
- Preferências do usuário
- Estado do sistema
- Contexto de sessões

**Melhorias Sugeridas:**
- [ ] Adicionar busca semântica com embeddings
- [ ] Implementar aprendizado de preferências automático
- [ ] Adicionar sistema de tags para memórias
- [ ] Criar API de consulta de memórias por contexto

**Exemplo de Uso:**
```python
from modules.memory.persistent_memory import PersistentMemory

memory = PersistentMemory()

# Salvar conversa
memory.save_conversation("user", "Qual é o clima hoje?")
memory.save_conversation("assistant", "Hoje está ensolarado.")

# Recuperar histórico
history = memory.get_conversation_history(limit=10)

# Salvar preferências
memory.save_user_preference("voz_velocidade", 150)
memory.save_user_preference("idioma_preferido", "pt-BR")

# Recuperar preferência
speed = memory.get_user_preference("voz_velocidade", default=100)
```

---

## Fase 3: Automação Avançada

### 🧠 Task Decomposition Engine

**Arquivo:** `modules/processing/task_decomposition.py`

Sistema de planejamento e execução de tarefas complexas.

**Características:**
- Decompõe tarefas complexas em etapas simples
- Gerencia dependências entre tarefas
- Execução sequencial respeitando ordem
- Verificação de resultados
- Retry automático em caso de falha

**Exemplo de Uso:**
```python
from modules.processing.task_decomposition import TaskDecomposer, TaskExecutor

# Criar decompositor
decomposer = TaskDecomposer(llm_client=your_llm)

# Decompor tarefa
plan = decomposer.decompose("Enviar email para João avisando sobre reunião amanhã às 14h")

# Executar plano
executor = TaskExecutor()
executor.register_handler("open_app", lambda params: open_app(params))
executor.register_handler("compose_email", lambda params: compose_email(params))
executor.register_handler("send_email", lambda params: send_email(params))

success = executor.execute_plan(plan)

# Ver progresso
status = executor.get_plan_status()
print(f"Progresso: {status['progress']['percentage']}%")
```

**Fluxo de Execução:**
```
Requisição: "Agendar reunião com Maria amanhã às 15h"
    ↓
TaskDecomposer analisa e cria plano:
    ├── Task 1: Abrir calendário
    ├── Task 2: Criar evento (depende Task 1)
    └── Task 3: Enviar convite para Maria (depende Task 2)
    ↓
TaskExecutor executa sequencialmente:
    ✓ Task 1 concluída
    ✓ Task 2 concluída
    ✓ Task 3 concluída
    ↓
Resultado: "Reunião agendada com sucesso!"
```

---

### 📅 Calendar Integration

**Arquivo:** `modules/action/calendar_integration.py`

Integração com Google Calendar e Outlook.

**Características:**
- Criar, listar, atualizar e deletar eventos
- Enviar convites automaticamente
- Verificar próximos compromissos
- Suporte a recorrências

**Exemplo de Uso:**
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
    location="Sala de conferências",
    attendees=["joao@email.com", "maria@email.com"]
)

# Listar próximos eventos
events = calendar.list_events(max_results=5)
for event in events:
    print(f"- {event['summary']} em {event['start']['dateTime']}")

# Próximo compromisso
next_event = calendar.get_next_event()
print(f"Próximo: {next_event['summary']}")
```

**Configuração:**
1. Acesse [Google Cloud Console](https://console.cloud.google.com/)
2. Crie projeto e habilite Google Calendar API
3. Baixe credenciais OAuth 2.0
4. Salve em `config/calendar_credentials.json`

---

### 📧 Email Integration

**Arquivo:** `modules/action/email_integration.py`

Integração com Gmail e Outlook.

**Características:**
- Enviar emails (texto simples ou HTML)
- Ler mensagens
- Buscar emails
- Marcar como lido/não lido
- Verificar emails não lidos

**Exemplo de Uso:**
```python
from modules.action.email_integration import EmailIntegration

# Inicializar
email = EmailIntegration(provider="gmail")

# Enviar email
email.send_email(
    to="destinatario@email.com",
    subject="Relatório diário",
    body="Segue o relatório do dia...",
    cc=["copia@email.com"]
)

# Listar emails não lidos
unread = email.list_messages(query="is:unread")
print(f"{len(unread)} emails não lidos")

# Ler últimos emails
latest = email.get_latest_messages(count=5)
for msg in latest:
    print(f"- De: {msg['from']}")
    print(f"  Assunto: {msg['subject']}")
    print(f"  Preview: {msg['snippet']}")

# Buscar emails
results = email.search_messages("from:joao@email.com")
```

**Configuração:**
1. Acesse [Google Cloud Console](https://console.cloud.google.com/)
2. Crie projeto e habilite Gmail API
3. Baixe credenciais OAuth 2.0
4. Salve em `config/email_credentials.json`

---

## Fase 4: Segurança e Produção

### 🔒 Security Module

**Arquivo:** `modules/system/security_module.py`

Sistema completo de segurança e permissões.

**Características:**
- 4 níveis de permissão (Guest, User, Power User, Admin)
- Whitelist de comandos por nível
- Blacklist de padrões perigosos
- Confirmação para ações críticas
- Audit logging
- Sandboxing para comandos

**Níveis de Permissão:**
| Nível | Acesso |
|-------|--------|
| Guest (0) | Apenas leitura, sem acesso ao sistema |
| User (1) | Acesso limitado, comandos seguros |
| Power User (2) | Acesso avançado, alguns comandos de sistema |
| Admin (3) | Acesso completo ao sistema |

**Exemplo de Uso:**
```python
from modules.system.security_module import SecurityManager, PermissionLevel

# Inicializar
security = SecurityManager()

# Autenticar usuário (opcional)
if security.authenticate("usuario", "senha"):
    print("Autenticado!")

# Definir nível de permissão
security.set_permission_level(PermissionLevel.USER)

# Verificar permissão
if security.check_permission("open_app"):
    # Executar ação
    pass

# Verificar se comando é seguro
is_safe, reason = security.is_safe_command("rm -rf /")
if not is_safe:
    print(f"Comando bloqueado: {reason}")

# Verificar se requer confirmação
if security.requires_confirmation("delete_file important.txt"):
    confirmed = security.request_confirmation(
        "delete_file important.txt",
        "Deletar arquivo importante.txt"
    )
    if confirmed:
        # Executar
        pass

# Ver audit log
logs = security.get_audit_log(limit=50)
for log in logs:
    print(f"{log['timestamp']}: {log['action']} by {log['user']}")
```

**Configuração de Segurança:**

Arquivo `config/security.json`:
```json
{
  "require_authentication": false,
  "enable_command_whitelist": true,
  "enable_sandboxing": true,
  "require_confirmation_for_critical": true,
  "allowed_commands": {
    "1": ["search", "open_app", "play_music"],
    "2": ["file_operations", "system_info"],
    "3": ["*"]
  },
  "critical_commands": [
    "delete_file", "shutdown", "format",
    "install_package", "kill_process"
  ],
  "blacklisted_patterns": [
    "rm\\s+-rf\\s+/",
    "format\\s+c:"
  ]
}
```

---

## 📦 Instalação

### Instalação Completa

```bash
# 1. Clonar repositório
git clone <repo-url>
cd PROJECT_JARVIS_5.0

# 2. Instalar dependências principais
pip install -r requirements.txt

# 3. Instalar dependências de voz (opcional mas recomendado)
pip install openai-whisper sounddevice soundfile TTS pvporcupine

# 4. Instalar integrações (opcional)
pip install google-auth-oauthlib google-api-python-client

# 5. Para GPU (opcional - muito mais rápido)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### Instalação Mínima (Sem Novos Módulos)

```bash
pip install -r requirements.txt
# Sistema funciona normalmente com módulos básicos
```

### Instalação por Fase

**Fase 1 - Voz:**
```bash
pip install openai-whisper sounddevice soundfile TTS pvporcupine
```

**Fase 3 - Integrações:**
```bash
pip install google-auth-oauthlib google-api-python-client
```

---

## 🎯 Uso

### Exemplo Completo - Assistente com Voz

```python
from modules.input.whisper_module import WhisperModule
from modules.input.advanced_tts import AdvancedTTSModule
from modules.input.wake_word_detector import SimpleWakeWordDetector
from modules.memory.persistent_memory import PersistentMemory
from modules.system.security_module import SecurityManager

# Inicializar módulos
whisper = WhisperModule(model_name="base")
tts = AdvancedTTSModule(backend="coqui")
memory = PersistentMemory()
security = SecurityManager()

def process_command(text):
    """Processa comando do usuário."""
    # Salvar na memória
    memory.save_conversation("user", text)
    
    # Verificar segurança
    if not security.check_permission(text):
        response = "Você não tem permissão para esse comando"
    else:
        # Processar comando (seu código aqui)
        response = f"Processando: {text}"
    
    # Salvar resposta
    memory.save_conversation("assistant", response)
    
    # Falar resposta
    tts.speak(response)

def on_wake_word(keyword):
    """Callback quando wake word detectada."""
    tts.speak("Sim, senhor?")
    
    # Escutar comando
    command = whisper.listen(duration=5.0)
    if command:
        process_command(command)

# Iniciar detector de wake word
detector = SimpleWakeWordDetector(
    keywords=["jarvis", "hey jarvis"],
    callback=on_wake_word
)

print("JARVIS ativo. Diga 'Hey JARVIS' para começar...")
detector.start()

# Manter rodando
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    detector.stop()
    print("JARVIS desativado.")
```

---

## 🗺️ Roadmap

### ✅ Implementado
- [x] Whisper STT offline
- [x] Coqui TTS para voz natural
- [x] Wake word detector
- [x] Sistema de segurança e permissões
- [x] Task decomposition engine
- [x] Calendar integration
- [x] Email integration
- [x] Persistent memory (já existia)

### 🚧 Em Desenvolvimento
- [ ] Browser automation (Selenium/Playwright)
- [ ] IoT integration (Home Assistant)
- [ ] Workflow automation system
- [ ] Conversação contínua (sem cliques)
- [ ] Voice profiles (múltiplos usuários)

### 📅 Planejado
- [ ] Docker sandboxing para comandos
- [ ] Integração com Microsoft Outlook
- [ ] Plugin para IDEs (VSCode)
- [ ] Mobile app (Android/iOS)
- [ ] Aprendizado de preferências automático
- [ ] Sistema de recomendações

---

## 📊 Comparação Antes/Depois

| Feature | JARVIS 5.0 (Antes) | JARVIS 5.0 (Agora) | Alexa/Siri |
|---------|-------------------|-------------------|------------|
| **Voz Natural** | ⚠️ Básico (pyttsx3) | ✅ Excelente (Whisper + Coqui) | ✅ Excelente |
| **Wake Word** | ❌ Não | ✅ Sim ("Hey JARVIS") | ✅ Sim |
| **Controle Sistema** | ✅ Completo | ✅ Completo + Seguro | ❌ Limitado |
| **Memória** | ⚠️ Curto prazo | ✅ Persistente | ✅ Longo prazo |
| **Task Planning** | ❌ Não | ✅ Sim (decomposição) | ⚠️ Limitado |
| **Calendário** | ❌ Não | ✅ Google Calendar | ✅ Sim |
| **Email** | ❌ Não | ✅ Gmail | ✅ Sim |
| **Segurança** | ⚠️ Básica | ✅ Completa | ✅ Completa |
| **Privacidade** | ✅ 100% Local | ✅ 100% Local | ❌ Cloud |
| **Custo** | ✅ Gratuito | ✅ Gratuito | 💰 Grátis com limites |

---

## 🎓 Próximos Passos

1. **Teste os novos módulos:**
   - Whisper para STT
   - Coqui TTS para voz natural
   - Wake word detector

2. **Configure integrações:**
   - Google Calendar
   - Gmail

3. **Ajuste segurança:**
   - Defina níveis de permissão
   - Configure whitelist
   - Teste confirmações

4. **Experimente automação:**
   - Crie tarefas complexas
   - Teste task decomposition

5. **Personalize:**
   - Ajuste velocidade da voz
   - Configure preferências
   - Treine seu perfil

---

## 📚 Documentação Adicional

- [API Documentation](API_DOCUMENTATION.md)
- [Guia de Instalação](INSTALL.md)
- [Arquitetura](ARCHITETURA.md)
- [Guia de Treinamento](GUIA_TREINAMENTO.md)

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Áreas de interesse:
- Browser automation
- IoT integrations
- Mobile app
- Workflow templates
- Voice profiles

---

## 📄 Licença

Este projeto é open-source e gratuito para uso pessoal e comercial.

---

<div align="center">

**JARVIS 5.0 - Seu Assistente Pessoal Inteligente**

Desenvolvido com ❤️ usando tecnologias Open Source

</div>
