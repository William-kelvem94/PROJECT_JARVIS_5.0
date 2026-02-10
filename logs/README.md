# 📋 JARVIS 5.0 - Logs Directory

Esta pasta armazena todos os arquivos de log gerados pelo sistema JARVIS 5.0.

---

## 📁 **Tipos de Logs**

### **1. Log Principal**
- **Arquivo**: `jarvis.log`
- **Conteúdo**: Log principal do sistema
- **Rotação**: Diária (mantém últimos 7 dias)
- **Nível**: INFO, WARNING, ERROR, CRITICAL

### **2. Logs com Data**
- **Padrão**: `jarvis_auto_YYYYMMDD.log`
- **Exemplo**: `jarvis_auto_20260206.log`
- **Conteúdo**: Logs específicos de execuções automáticas
- **Retenção**: 30 dias

### **3. Logs de Instalação**
- **Arquivo**: `total_installer.log`
- **Conteúdo**: Saída do instalador de dependências
- **Uso**: Troubleshooting de instalação

---

## 🔍 **Estrutura dos Logs**

### **Formato Padrão:**
```
[TIMESTAMP] [LEVEL] [MODULE] - MESSAGE
```

### **Exemplo:**
```
2026-02-09 23:53:18 INFO core.ai_agent - Sistema inicializado
2026-02-09 23:53:19 WARNING core.voice_controller - Edge-TTS timeout
2026-02-09 23:53:20 ERROR core.memory_manager - ChromaDB connection failed
```

---

## 📊 **Níveis de Log**

| Nível | Descrição | Quando Usar |
|-------|-----------|-------------|
| **DEBUG** | Informações detalhadas | Desenvolvimento/Debug |
| **INFO** | Eventos normais | Operação normal |
| **WARNING** | Avisos não críticos | Problemas menores |
| **ERROR** | Erros que afetam funcionalidade | Falhas recuperáveis |
| **CRITICAL** | Erros críticos do sistema | Falhas graves |

---

## 🛠️ **Configuração de Logs**

### **Localização da Config:**
`src/utils/logger.py`

### **Níveis por Módulo:**
```python
# config/logging_config.yaml
loggers:
  core.ai_agent: INFO
  core.voice_controller: WARNING
  core.vision_system: DEBUG
```

---

## 📝 **Visualizar Logs**

### **Últimas 50 linhas:**
```bash
# Windows PowerShell
Get-Content logs\jarvis.log -Tail 50

# CMD
powershell -Command "Get-Content logs\jarvis.log -Tail 50"
```

### **Filtrar por nível:**
```bash
# Apenas erros
Select-String -Path logs\jarvis.log -Pattern "ERROR"

# Apenas warnings e erros
Select-String -Path logs\jarvis.log -Pattern "WARNING|ERROR"
```

### **Logs em tempo real:**
```bash
Get-Content logs\jarvis.log -Wait -Tail 20
```

---

## 🧹 **Limpeza de Logs**

### **Manual:**
```bash
# Remover logs antigos (>30 dias)
Get-ChildItem logs\*.log | Where-Object {$_.LastWriteTime -lt (Get-Date).AddDays(-30)} | Remove-Item

# Remover todos os logs
Remove-Item logs\*.log
```

### **Automática:**
O sistema limpa automaticamente logs com mais de 30 dias.

---

## 🔍 **Análise de Logs**

### **Contar erros:**
```bash
(Select-String -Path logs\jarvis.log -Pattern "ERROR").Count
```

### **Módulos com mais erros:**
```bash
Select-String -Path logs\jarvis.log -Pattern "ERROR" | 
  ForEach-Object { $_.Line -match '\[(.*?)\]' | Out-Null; $matches[1] } | 
  Group-Object | 
  Sort-Object Count -Descending
```

### **Erros nas últimas 24h:**
```bash
$yesterday = (Get-Date).AddDays(-1).ToString("yyyy-MM-dd")
Select-String -Path logs\jarvis.log -Pattern "ERROR" | 
  Where-Object { $_.Line -match $yesterday }
```

---

## 📦 **Backup de Logs**

### **Criar backup:**
```bash
# Comprimir logs
Compress-Archive -Path logs\*.log -DestinationPath logs_backup_$(Get-Date -Format 'yyyyMMdd').zip

# Mover para pasta de backup
Move-Item logs\*.log -Destination backup\logs\
```

---

## 🚨 **Troubleshooting**

### **Log muito grande:**
```bash
# Verificar tamanho
Get-ChildItem logs\jarvis.log | Select-Object Name, @{Name="SizeMB";Expression={$_.Length/1MB}}

# Truncar log (manter últimas 1000 linhas)
Get-Content logs\jarvis.log -Tail 1000 | Set-Content logs\jarvis_temp.log
Move-Item logs\jarvis_temp.log logs\jarvis.log -Force
```

### **Permissões de escrita:**
```bash
# Verificar permissões
icacls logs\

# Dar permissão total
icacls logs\ /grant Users:F
```

### **Log não está sendo criado:**
1. Verificar permissões da pasta `logs/`
2. Verificar configuração em `src/utils/logger.py`
3. Verificar se o diretório existe
4. Verificar espaço em disco

---

## 📋 **Logs Importantes**

### **Startup:**
```
INFO core.main - JARVIS 5.0 iniciando...
INFO core.hardware_manager - Hardware detectado: CPU, RAM, GPU
INFO core.ai_agent - Modelos carregados
INFO core.voice_controller - Sistema de voz pronto
```

### **Erros Comuns:**
```
ERROR core.ai_agent - Ollama não disponível (404)
WARNING core.voice_controller - Edge-TTS timeout
ERROR core.memory_manager - ChromaDB duplicate ID
WARNING core.vision_system - CUDA não disponível
```

---

## 🔗 **Integração com Monitoramento**

### **Enviar logs para arquivo externo:**
```python
import logging
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler(
    'logs/jarvis.log',
    maxBytes=10*1024*1024,  # 10 MB
    backupCount=5
)
```

### **Enviar logs para servidor:**
```python
from logging.handlers import HTTPHandler

http_handler = HTTPHandler(
    'logs.example.com',
    '/api/logs',
    method='POST'
)
```

---

## ⚙️ **Configuração Avançada**

### **Logs Estruturados (JSON):**
```python
import json
import logging

class JSONFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps({
            'timestamp': record.created,
            'level': record.levelname,
            'module': record.module,
            'message': record.getMessage()
        })
```

### **Logs Coloridos (Console):**
```python
from colorlog import ColoredFormatter

formatter = ColoredFormatter(
    "%(log_color)s%(levelname)-8s%(reset)s %(blue)s%(message)s",
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'red,bg_white',
    }
)
```

---

## 📝 **Notas**

- ✅ Logs são rotacionados automaticamente
- ✅ Logs antigos (>30 dias) são removidos
- ✅ Logs não são commitados no Git (`.gitignore`)
- ✅ Formato padrão: `[TIMESTAMP] [LEVEL] [MODULE] - MESSAGE`
- ✅ Encoding: UTF-8

---

**Última Atualização**: 2026-02-09  
**Mantido por**: JARVIS 5.0 Team
