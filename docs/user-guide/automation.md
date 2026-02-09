# 🤖 JARVIS 5.0 - Automação

**Crie Rotinas e Scripts Personalizados**

---

## 📖 O que é Automação?

Automação no JARVIS permite criar:
- **Rotinas programadas** (executar tarefas em horários específicos)
- **Scripts personalizados** (comandos customizados)
- **Workflows multi-etapas** (sequências de ações)
- **Triggers inteligentes** (ações baseadas em eventos)

---

## 🎯 Tipos de Automação

### 1. Scripts Simples

Arquivos Python executados sob comando.

**Localização:** `data/generated_scripts/`

**Exemplo:** `abrir_projetos.py`

```python
# data/generated_scripts/abrir_projetos.py
import os
import subprocess

def executar():
    """Abre VSCode e navegador com GitHub"""
    # Abrir VSCode
    subprocess.Popen(["code", "C:\\Users\\willi\\Documents\\GitHub"])
    
    # Abrir GitHub no navegador
    subprocess.Popen(["start", "https://github.com"], shell=True)
    
    return "Projetos abertos com sucesso!"
```

**Uso:**
```
"JARVIS, executar abrir projetos"
```

---

### 2. Rotinas Agendadas

Tarefas executadas automaticamente em horários específicos.

**Arquivo:** `config/automations.yaml`

```yaml
schedules:
  - name: "Backup Diário"
    time: "23:00"
    script: "backup_system.py"
    enabled: true
  
  - name: "Relatório Matinal"
    time: "08:00"
    script: "morning_briefing.py"
    days: ["mon", "tue", "wed", "thu", "fri"]
    enabled: true
  
  - name: "Lembrete de Reunião"
    time: "14:30"
    script: "meeting_reminder.py"
    days: ["wed"]
    enabled: false
```

**Script exemplo:** `backup_system.py`

```python
import shutil
from datetime import datetime

def executar():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"C:\\Backups\\jarvis_{timestamp}"
    
    # Backup de arquivos importantes
    shutil.copytree("data/memories", f"{backup_path}/memories")
    shutil.copytree("data/learning", f"{backup_path}/learning")
    
    return f"Backup criado em: {backup_path}"
```

---

### 3. Workflows Multi-Etapas

Sequências complexas de ações.

**Arquivo:** `config/workflows.yaml`

```yaml
workflows:
  - name: "Iniciar Trabalho"
    trigger: "voice"  # ou "time", "event"
    command: "começar trabalho"
    steps:
      - action: "open_app"
        params:
          app: "vscode"
      
      - action: "open_url"
        params:
          url: "https://github.com"
      
      - action: "open_app"
        params:
          app: "spotify"
      
      - action: "set_volume"
        params:
          level: 30
      
      - action: "speak"
        params:
          text: "Ambiente de trabalho configurado, senhor."
  
  - name: "Modo Foco"
    trigger: "voice"
    command: "ativar modo foco"
    steps:
      - action: "close_app"
        params:
          app: "discord"
      
      - action: "close_app"
        params:
          app: "spotify"
      
      - action: "set_notifications"
        params:
          enabled: false
      
      - action: "speak"
        params:
          text: "Modo foco ativado. Sem distrações."
```

**Uso:**
```
"JARVIS, começar trabalho"
"JARVIS, ativar modo foco"
```

---

### 4. Triggers Inteligentes

Ações baseadas em eventos do sistema.

**Arquivo:** `config/triggers.yaml`

```yaml
triggers:
  - name: "Detecção de Rosto Desconhecido"
    event: "unknown_face_detected"
    action: "send_notification"
    params:
      title: "JARVIS Alerta"
      message: "Rosto desconhecido detectado na câmera"
  
  - name: "CPU Alta"
    event: "cpu_usage"
    condition: "> 80%"
    duration: "5 minutes"
    action: "run_script"
    params:
      script: "optimize_system.py"
  
  - name: "Aprendizado Completo"
    event: "training_completed"
    action: "speak"
    params:
      text: "Treinamento concluído com sucesso, senhor."
```

---

## 🛠️ Criando Seus Scripts

### Template Básico

```python
# data/generated_scripts/meu_script.py

def executar():
    """
    Descrição do seu script aqui.
    Esta função será chamada pelo JARVIS.
    """
    
    # Seu código aqui
    resultado = "Tarefa executada!"
    
    # Retorne uma mensagem
    return resultado

# Opcional: função de inicialização
def setup():
    """Executado uma vez ao carregar"""
    pass

# Opcional: função de limpeza
def cleanup():
    """Executado ao descarregar script"""
    pass
```

### Exemplos Práticos

#### 1. Organizador de Downloads

```python
# organizar_downloads.py
import os
import shutil

def executar():
    downloads = "C:\\Users\\willi\\Downloads"
    
    # Criar pastas por tipo
    folders = {
        "Images": [".jpg", ".png", ".gif"],
        "Documents": [".pdf", ".docx", ".txt"],
        "Videos": [".mp4", ".avi", ".mkv"],
        "Archives": [".zip", ".rar", ".7z"]
    }
    
    moved = 0
    for folder, extensions in folders.items():
        folder_path = os.path.join(downloads, folder)
        os.makedirs(folder_path, exist_ok=True)
        
        for file in os.listdir(downloads):
            if any(file.endswith(ext) for ext in extensions):
                shutil.move(
                    os.path.join(downloads, file),
                    os.path.join(folder_path, file)
                )
                moved += 1
    
    return f"{moved} arquivos organizados!"
```

#### 2. Relatório de Sistema

```python
# relatorio_sistema.py
import psutil
from datetime import datetime

def executar():
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    
    report = f"""
    === RELATÓRIO DO SISTEMA ===
    Data: {datetime.now().strftime("%d/%m/%Y %H:%M")}
    
    CPU: {cpu}%
    RAM: {ram}%
    Disk: {disk}%
    
    Status: {"✅ Normal" if cpu < 80 else "⚠️ Alta Carga"}
    """
    
    # Salvar relatório
    with open("data/system_reports/latest.txt", "w") as f:
        f.write(report)
    
    return report
```

#### 3. Lembrete Inteligente

```python
# lembrete.py
from datetime import datetime, timedelta
import json

def executar(mensagem, minutos=30):
    """Cria lembrete que será anunciado depois"""
    
    alarm_time = datetime.now() + timedelta(minutes=minutos)
    
    reminder = {
        "mensagem": mensagem,
        "horario": alarm_time.isoformat()
    }
    
    # Salvar em arquivo de lembretes
    reminders_file = "data/memories/reminders.json"
    reminders = []
    
    try:
        with open(reminders_file, "r") as f:
            reminders = json.load(f)
    except FileNotFoundError:
        pass
    
    reminders.append(reminder)
    
    with open(reminders_file, "w") as f:
        json.dump(reminders, f, indent=2)
    
    return f"Lembrete criado para daqui {minutos} minutos: {mensagem}"
```

---

## 🎛️ Gerenciar Automações via Dashboard

### Control Dashboard → System → Automations

**Funcionalidades:**

1. **📋 Lista de Scripts**
   - Ver todos scripts em `generated_scripts/`
   - Executar manualmente
   - Editar no VSCode
   - Deletar

2. **⏰ Agendamentos**
   - Ver rotinas agendadas
   - Habilitar/Desabilitar
   - Adicionar nova rotina
   - Logs de execução

3. **🔀 Workflows**
   - Gerenciar workflows multi-etapas
   - Testar workflow manualmente
   - Ver histórico de execuções

4. **⚡ Triggers**
   - Listar eventos disponíveis
   - Configurar novos triggers
   - Ativar/Desativar

---

## 🧰 Ferramentas Auxiliares

### Módulos Disponíveis

JARVIS oferece módulos para facilitar automações:

```python
# Importar módulos do JARVIS
from src.core.brain.ai_agent import AIAgent
from src.core.voice.voice_engine import VoiceEngine
from src.core.vision.vision_processor import VisionProcessor
from src.utils.system_utils import SystemUtils

def executar():
    # Usar IA
    agent = AIAgent()
    resposta = agent.thinking("Qual o sentido da vida?")
    
    # Falar
    voice = VoiceEngine()
    voice.speak("42, senhor.")
    
    # Capturar câmera
    vision = VisionProcessor()
    frame = vision.capture_frame()
    
    # Info do sistema
    utils = SystemUtils()
    cpu = utils.get_cpu_usage()
    
    return f"CPU: {cpu}%"
```

---

## 📅 Expressões de Tempo

Para agendamentos avançados, use expressões **cron-like**:

```yaml
schedules:
  - name: "Backup Semanal"
    cron: "0 2 * * SUN"  # Todo domingo às 2h
    script: "backup_completo.py"
  
  - name: "Limpeza Diária"
    cron: "0 1 * * *"  # Todo dia à 1h
    script: "limpar_cache.py"
  
  - name: "Relatório Mensal"
    cron: "0 9 1 * *"  # Dia 1 de cada mês às 9h
    script: "relatorio_mensal.py"
```

**Formato:** `minuto hora dia mês dia_semana`

---

## 🔒 Segurança

### Boas Práticas

1. **Nunca execute scripts de fontes não confiáveis**
2. **Revise scripts antes de agendar**
3. **Limite permissões (não execute como Admin sem necessidade)**
4. **Faça backups antes de scripts de limpeza**

### Sandboxing

Scripts rodam no ambiente do JARVIS com acesso limitado:
- Sem acesso a arquivos de sistema críticos
- Timeout de 5 minutos (configurable)
- Logs de todas execuções

---

## 🆘 Solução de Problemas

### "Script não executa"

**Verificar:**
1. Sintaxe do Python está correta?
2. Função `executar()` está definida?
3. Dependências instaladas?
4. Logs em `data/logs/automation.log`

### "Agendamento não dispara"

**Verificar:**
1. `enabled: true` no YAML?
2. Formato de hora correto? (24h: "14:30")
3. JARVIS está rodando no horário?
4. Timezone configurado corretamente?

### "Workflow trava"

**Soluções:**
1. Adicione delays entre steps:
   ```yaml
   - action: "wait"
     params:
       seconds: 2
   ```
2. Verifique logs de cada step
3. Teste steps individualmente

---

## 📚 Próximos Passos

- **Dashboard:** [dashboard.md](dashboard.md)
- **Comandos:** [voice-commands.md](voice-commands.md)
- **Aprendizado:** [learning-system.md](../ai-systems/learning-system.md)

---

<div align="center">

**Automatize tudo. JARVIS nunca dorme. 🤖**

</div>
