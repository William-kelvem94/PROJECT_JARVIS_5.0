# 📊 JARVIS 5.0 - Data Directory

Esta pasta contém todos os dados gerados e utilizados pelo sistema JARVIS 5.0.

---

## 📁 Estrutura de Pastas

### **Dados de Runtime**
```
data/
├── chroma_db/              # Memórias vetoriais (ChromaDB)
├── learning/               # Dados de aprendizado
│   ├── feedback_loop.db   # Feedbacks de usuário
│   ├── golden_commands.json
│   └── training_history.json
├── logs/                   # Logs do sistema
├── memory/                 # Memória de curto prazo
├── neural_memory/          # Memória neural
└── voice_signatures/       # Assinaturas de voz
```

### **Dados de Visão**
```
data/
├── captures/               # Capturas de tela
├── screenshots/            # Screenshots processados
├── faces/                  # Banco de faces (FaceID)
└── test_images/            # Imagens de teste
```

### **Dados de Áudio**
```
data/
├── audio/                  # Arquivos de áudio
└── voice/                  # Dados de voz
```

### **Dados de Sistema**
```
data/
├── cache/                  # Cache temporário
├── temp/                   # Arquivos temporários
├── exports/                # Dados exportados
├── monitoring/             # Dados de monitoramento
├── security/               # Dados de segurança
└── system_reports/         # Relatórios do sistema
```

### **Dados de Desenvolvimento**
```
data/
├── templates/              # Templates
├── workflows/              # Workflows salvos
├── generated_scripts/      # Scripts gerados
└── training_dataset/       # Datasets de treinamento
```

---

## 📄 Arquivos Principais

| Arquivo | Descrição | Tamanho Típico |
|---------|-----------|----------------|
| `jarvis.db` | Database principal (SQLite) | ~600 KB |
| `feedback.db` | Database de feedbacks | ~30 KB |
| `jarvis.log` | Log principal | Variável |
| `jarvis_singularity.log` | Log do launcher | ~2 KB |
| `system_health.json` | Status do sistema | ~500 B |
| `jarvis.lock` | Lock file (execução única) | ~5 B |

---

## 🗑️ Limpeza Automática

### **Arquivos Temporários**
- `cache/` - Limpo a cada 7 dias
- `temp/` - Limpo a cada 1 dia
- `screenshots/` - Mantém últimos 30 dias

### **Logs**
- Rotação automática quando > 10 MB
- Mantém últimos 7 dias
- Compressão de logs antigos

### **Memória**
- `memory/` - Limpo a cada 30 dias
- `neural_memory/` - Mantém permanentemente
- `chroma_db/` - Backup semanal

---

## 🔒 Segurança

### **Dados Sensíveis**
- ✅ `faces/` - Criptografado
- ✅ `voice_signatures/` - Criptografado
- ✅ `security/` - Criptografado
- ✅ `.env` - Nunca commitado

### **Backup**
```bash
# Backup manual
python scripts/backup_data.py

# Localização
C:\Users\<user>\Documents\JARVIS_Backups\
```

---

## 📊 Uso de Espaço Típico

| Categoria | Espaço | Crescimento |
|-----------|--------|-------------|
| **ChromaDB** | ~50 MB | +5 MB/mês |
| **Logs** | ~10 MB | +2 MB/dia (rotação) |
| **Screenshots** | ~100 MB | +10 MB/dia (limpeza) |
| **Faces** | ~20 MB | Estável |
| **Cache** | ~50 MB | Estável (limpeza) |
| **TOTAL** | **~230 MB** | Controlado |

---

## 🧹 Manutenção

### **Limpeza Manual**

```bash
# Limpar cache
python -c "import shutil; shutil.rmtree('data/cache', ignore_errors=True)"

# Limpar temp
python -c "import shutil; shutil.rmtree('data/temp', ignore_errors=True)"

# Limpar screenshots antigos (>30 dias)
python scripts/clean_old_data.py --screenshots --days 30
```

### **Verificar Espaço**

```bash
# Windows PowerShell
Get-ChildItem data -Recurse | Measure-Object -Property Length -Sum

# Python
python -c "from pathlib import Path; print(f'{sum(f.stat().st_size for f in Path('data').rglob('*') if f.is_file()) / 1024 / 1024:.1f} MB')"
```

---

## 🔄 Migração de Dados

### **Exportar Dados**

```python
from src.utils.data_manager import DataManager

dm = DataManager()

# Exportar memórias
dm.export_memories('backup/memories.json')

# Exportar feedbacks
dm.export_feedbacks('backup/feedbacks.json')

# Exportar configurações
dm.export_config('backup/config.yaml')
```

### **Importar Dados**

```python
# Importar de backup
dm.import_memories('backup/memories.json')
dm.import_feedbacks('backup/feedbacks.json')
```

---

## 📝 Estrutura de Databases

### **jarvis.db (SQLite)**

```sql
-- Tabelas principais
CREATE TABLE interactions (
    id INTEGER PRIMARY KEY,
    timestamp TEXT,
    user_input TEXT,
    ai_response TEXT,
    model_used TEXT
);

CREATE TABLE system_events (
    id INTEGER PRIMARY KEY,
    timestamp TEXT,
    event_type TEXT,
    details TEXT
);
```

### **feedback.db (SQLite)**

```sql
CREATE TABLE feedbacks (
    id INTEGER PRIMARY KEY,
    timestamp TEXT,
    user_input TEXT,
    ai_response TEXT,
    feedback TEXT,  -- 'positive', 'negative', 'correction'
    correction TEXT,
    model_used TEXT,
    trained BOOLEAN DEFAULT 0
);
```

---

## ⚠️ Avisos Importantes

### **NÃO Commitar**
- ❌ `*.db` - Databases
- ❌ `*.log` - Logs
- ❌ `faces/` - Dados biométricos
- ❌ `voice_signatures/` - Assinaturas de voz
- ❌ `chroma_db/` - Memórias vetoriais
- ❌ `cache/` - Cache temporário
- ❌ `temp/` - Arquivos temporários

### **Commitar Apenas**
- ✅ `.gitkeep` - Para manter estrutura de pastas
- ✅ `README.md` - Esta documentação
- ✅ `.gitignore` - Configuração Git

---

## 🛠️ Troubleshooting

### **Database corrompido**

```bash
# Verificar integridade
sqlite3 data/jarvis.db "PRAGMA integrity_check;"

# Reparar
python scripts/repair_database.py
```

### **ChromaDB erro**

```bash
# Recriar índice
python -c "from src.core.intelligence.memory_manager import MemoryManager; MemoryManager().rebuild_index()"
```

### **Espaço em disco cheio**

```bash
# Limpar tudo (CUIDADO!)
python scripts/clean_all_data.py --confirm

# Ou limpar seletivamente
python scripts/clean_old_data.py --cache --temp --screenshots
```

---

## 📊 Monitoramento

### **Status do Sistema**

```bash
# Ver status
cat data/system_health.json

# Monitorar em tempo real
python tools/monitor_system.py
```

### **Estatísticas**

```python
from src.utils.data_manager import DataManager

dm = DataManager()
stats = dm.get_statistics()

print(f"Total interactions: {stats['total_interactions']}")
print(f"Total memories: {stats['total_memories']}")
print(f"Disk usage: {stats['disk_usage_mb']} MB")
```

---

## 🔗 Links Úteis

- [Sistema de Memória](../docs/ai-systems/memory-system.md)
- [Aprendizado Contínuo](../docs/ai-systems/learning-system.md)
- [Backup e Restauração](../docs/maintenance/backup-restore.md)

---

**Última Atualização**: 2026-02-10  
**Mantido por**: JARVIS 5.0 Team
