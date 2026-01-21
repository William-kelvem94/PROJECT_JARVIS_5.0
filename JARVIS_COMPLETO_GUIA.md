# 🤖 JARVIS COMPLETO - Guia de Uso Total

## 🎉 Bem-vindo ao JARVIS 5.0 - Seu Assistente de IA Completo!

Este guia mostra como usar TODAS as funcionalidades do JARVIS, incluindo:
- 🖥️ **Controle Total do Sistema** (Windows, Linux, Android)
- 🧠 **Treinamento Contínuo Automático**
- 🔍 **Pesquisa Web Inteligente**
- 📚 **Aprendizado Perpétuo**

---

## 🚀 Início Rápido

### 1. Iniciar JARVIS

```bash
# Com Docker (Recomendado)
docker-compose up -d

# Sem Docker
python -m uvicorn core.main:app --reload
```

### 2. Acessar Interface

```
http://localhost:8000
```

### 3. Verificar Status Completo

```bash
curl http://localhost:8000/api/status
```

---

## 🖥️ Controle de Sistema

### Windows

#### Abrir Aplicativos
```bash
curl -X POST http://localhost:8000/api/system/open-app \
  -H "Content-Type: application/json" \
  -d '{
    "app_name": "notepad",
    "target": "local"
  }'
```

**Apps Suportados**:
- `notepad`, `calculator`, `explorer`, `chrome`, `firefox`, `edge`
- `cmd`, `powershell`, `vscode`

#### Executar Comandos PowerShell
```bash
curl -X POST http://localhost:8000/api/system/command \
  -H "Content-Type: application/json" \
  -d '{
    "command": "Get-Process | Select-Object Name, CPU | Sort-Object CPU -Descending | Select -First 5",
    "target": "local"
  }'
```

#### Ver Processos em Execução
```bash
curl http://localhost:8000/api/system/processes?target=local
```

#### Encerrar Processo
```bash
curl -X POST http://localhost:8000/api/system/kill-process \
  -H "Content-Type: application/json" \
  -d '{
    "process_name": "notepad",
    "target": "local"
  }'
```

#### Tirar Screenshot
```bash
curl -X POST http://localhost:8000/api/system/screenshot \
  -H "Content-Type: application/json" \
  -d '{
    "path": "./screenshots/screen.png",
    "target": "local"
  }'
```

### Linux/Ubuntu

#### Abrir Aplicativos
```bash
curl -X POST http://localhost:8000/api/system/open-app \
  -H "Content-Type: application/json" \
  -d '{
    "app_name": "terminal",
    "target": "local"
  }'
```

**Apps Suportados**:
- `terminal`, `firefox`, `chrome`, `vscode`
- `nautilus` (files), `calculator`, `text-editor`

#### Executar Comandos Bash
```bash
curl -X POST http://localhost:8000/api/system/command \
  -H "Content-Type: application/json" \
  -d '{
    "command": "df -h",
    "target": "local"
  }'
```

#### Informações do Sistema
```bash
curl http://localhost:8000/api/system/info?target=local
```

Retorna:
- CPU usage
- Memory (total, used, free)
- Disk usage
- System version

### Android (via ADB)

#### Pré-requisitos
1. Instale Android SDK Platform Tools
2. Habilite USB Debugging no Android
3. Conecte dispositivo via USB ou WiFi

```bash
# Verificar dispositivos conectados
adb devices
```

#### Abrir Aplicativos Android
```bash
curl -X POST http://localhost:8000/api/system/open-app \
  -H "Content-Type: application/json" \
  -d '{
    "app_name": "chrome",
    "target": "android"
  }'
```

**Apps Suportados**:
- `chrome`, `youtube`, `gmail`, `camera`, `gallery`, `settings`

#### Executar Comandos ADB
```bash
curl -X POST http://localhost:8000/api/system/command \
  -H "Content-Type: application/json" \
  -d '{
    "command": "input text \"Hello from JARVIS\"",
    "target": "android"
  }'
```

#### Screenshot Android
```bash
curl -X POST http://localhost:8000/api/system/screenshot \
  -H "Content-Type: application/json" \
  -d '{
    "path": "./screenshots/android.png",
    "target": "android"
  }'
```

#### Informações do Dispositivo
```bash
curl http://localhost:8000/api/system/info?target=android
```

Retorna:
- Model
- Android version
- Battery level
- Connected devices

---

## 🧠 Treinamento Contínuo

### Como Funciona

O JARVIS treina automaticamente enquanto você o usa:

1. **Você usa normalmente** → Conversas são salvas
2. **Sistema monitora qualidade** → Avalia respostas
3. **Acumula 20+ interações** → Prepara treinamento
4. **Treina automaticamente** → Melhora modelo
5. **Avalia e troca modelo** → Sempre usa o melhor

### Status do Treinamento Contínuo

```bash
curl http://localhost:8000/api/continuous-training/status
```

Retorna:
```json
{
  "enabled": true,
  "training_in_progress": false,
  "last_training_check": "2024-01-15T10:30:00",
  "stats": {
    "total_continuous_trainings": 5,
    "model_switches": 2,
    "last_model_switch": "2024-01-15T08:00:00"
  },
  "model_registry": {
    "total_models": 3,
    "best_model": "jarvis-custom-20240115",
    "active_model": "jarvis-custom-20240115",
    "models": [...]
  },
  "config": {
    "training_interval_minutes": 60,
    "min_new_interactions": 20,
    "quality_improvement_threshold": 0.05
  }
}
```

### Forçar Treinamento Imediato

```bash
# Treinamento incremental (rápido)
curl -X POST http://localhost:8000/api/continuous-training/force \
  -H "Content-Type: application/json" \
  -d '{"type": "incremental"}'

# Treinamento completo
curl -X POST http://localhost:8000/api/continuous-training/force \
  -H "Content-Type: application/json" \
  -d '{"type": "full"}'
```

### Habilitar/Desabilitar

```bash
# Habilitar
curl -X POST http://localhost:8000/api/continuous-training/enable

# Desabilitar
curl -X POST http://localhost:8000/api/continuous-training/disable
```

---

## 📊 Registro de Modelos

### Listar Todos os Modelos

```bash
curl http://localhost:8000/api/models/registry
```

Retorna:
```json
{
  "models": [
    {
      "name": "jarvis-custom-20240115",
      "quality_score": 0.85,
      "training_samples": 150,
      "source": "continuous_local",
      "registered_at": "2024-01-15T10:00:00",
      "version": 3
    },
    {
      "name": "jarvis-docker-model",
      "quality_score": 0.78,
      "training_samples": 200,
      "source": "docker",
      "registered_at": "2024-01-14T15:00:00",
      "version": 2
    }
  ],
  "best_model": "jarvis-custom-20240115",
  "active_model": "jarvis-custom-20240115"
}
```

### Comparar Modelos

```bash
curl -X POST http://localhost:8000/api/models/compare \
  -H "Content-Type: application/json" \
  -d '{
    "model_a": "jarvis-custom-20240115",
    "model_b": "jarvis-docker-model"
  }'
```

Retorna:
```json
{
  "model_a": "jarvis-custom-20240115",
  "model_b": "jarvis-docker-model",
  "comparison": {
    "quality": {
      "a": 0.85,
      "b": 0.78,
      "winner": "a"
    },
    "training_samples": {
      "a": 150,
      "b": 200
    },
    "age": {
      "a": "2024-01-15T10:00:00",
      "b": "2024-01-14T15:00:00",
      "newer": "a"
    }
  }
}
```

---

## 🔍 Pesquisa Web

### Busca Simples

```bash
curl "http://localhost:8000/api/research/search?query=machine+learning&num_results=5"
```

### Pesquisa Completa

```bash
curl -X POST http://localhost:8000/api/research/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "latest AI developments",
    "deep_search": true
  }'
```

### Chat com Pesquisa Automática

O JARVIS detecta automaticamente quando precisa pesquisar:

**No Chat ou WebSocket**, apenas diga:
- "Pesquise sobre Python"
- "O que é machine learning?"
- "Quais as notícias sobre IA?"
- "Busque informações sobre..."

O sistema automaticamente:
1. Detecta necessidade de busca
2. Busca na web
3. Adiciona contexto
4. Responde com fontes

---

## 💬 Usando o Chat

### Via WebSocket (Recomendado)

```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onopen = () => {
  ws.send(JSON.stringify({
    content: "Pesquise sobre inteligência artificial"
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  if (data.type === 'stream') {
    // Token sendo transmitido
    console.log(data.content);
  } else if (data.type === 'stream_end') {
    // Resposta completa
    console.log('Completo:', data.content);
  }
};
```

### Via REST API

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Abra o notepad",
    "system": "Você é JARVIS"
  }'
```

---

## 🎯 Casos de Uso Completos

### 1. Automatizar Tarefas no Windows

```python
import requests

base_url = "http://localhost:8000"

# 1. Abrir aplicativo
requests.post(f"{base_url}/api/system/open-app", json={
    "app_name": "chrome"
})

# 2. Aguardar um pouco
import time
time.sleep(2)

# 3. Tirar screenshot
requests.post(f"{base_url}/api/system/screenshot", json={
    "path": "./screenshots/chrome.png"
})

# 4. Ver processos
response = requests.get(f"{base_url}/api/system/processes")
print(response.json())
```

### 2. Controlar Android Remotamente

```bash
# Desbloquear e abrir YouTube
curl -X POST http://localhost:8000/api/system/command \
  -H "Content-Type: application/json" \
  -d '{"command": "input keyevent 82", "target": "android"}'

sleep 1

curl -X POST http://localhost:8000/api/system/open-app \
  -H "Content-Type: application/json" \
  -d '{"app_name": "youtube", "target": "android"}'

# Tirar screenshot
curl -X POST http://localhost:8000/api/system/screenshot \
  -H "Content-Type: application/json" \
  -d '{"path": "./screenshots/android-youtube.png", "target": "android"}'
```

### 3. Treinamento Personalizado

```bash
# 1. Usar JARVIS normalmente (acumular 50+ interações)

# 2. Verificar dados disponíveis
curl http://localhost:8000/api/training/dataset/stats

# 3. Treinar modelo customizado
curl -X POST http://localhost:8000/api/training/workflow \
  -H "Content-Type: application/json" \
  -d '{
    "type": "full",
    "config": {
      "model": {
        "base_model": "codellama:7b",
        "custom_model_name": "jarvis-personal",
        "temperature": 0.7
      }
    }
  }'

# 4. Verificar modelo registrado
curl http://localhost:8000/api/models/registry

# 5. Sistema automaticamente usa o melhor modelo!
```

### 4. Pesquisa e Resposta Fundamentada

```bash
# Via chat, pergunte:
# "Pesquise sobre as últimas novidades em IA generativa"

# O JARVIS:
# 1. Detecta necessidade de pesquisa
# 2. Busca em DuckDuckGo e Wikipedia
# 3. Agrega informações
# 4. Responde com contexto e fontes
```

---

## ⚙️ Configuração Avançada

### Ajustar Intervalo de Treinamento Contínuo

```bash
curl -X POST http://localhost:8000/api/training/config/update \
  -H "Content-Type: application/json" \
  -d '{
    "updates": {
      "auto_training": {
        "retrain_interval_hours": 12
      }
    }
  }'
```

### Threshold de Qualidade

```bash
curl -X POST http://localhost:8000/api/training/config/update \
  -H "Content-Type: application/json" \
  -d '{
    "updates": {
      "auto_training": {
        "quality_threshold": 0.7,
        "min_interactions_for_incremental": 30
      }
    }
  }'
```

---

## 🐳 Uso com Docker

### Treinar Localmente e no Docker

```bash
# 1. Treinar localmente
curl -X POST http://localhost:8000/api/training/workflow \
  -H "Content-Type: application/json" \
  -d '{"type": "full"}'

# 2. Modelo é automaticamente registrado
# 3. Sistema escolhe melhor modelo (local ou docker)
# 4. Continuous training integra ambos
```

### Compartilhar Modelos entre Local e Docker

Os modelos são salvos em `./data/models/` que pode ser:
- Volume do Docker
- Diretório compartilhado
- Sincronizado entre ambientes

```yaml
# docker-compose.yml
volumes:
  - ./data:/app/data  # Compartilhar modelos
```

---

## 📈 Monitoramento

### Dashboard Completo

```bash
# Status de tudo
curl http://localhost:8000/api/training/comprehensive-status
```

Retorna:
- Training status atual
- Auto-trainer status
- Continuous training status
- Dataset statistics
- Model registry
- Configuration atual

### Logs em Tempo Real

```bash
# Docker
docker-compose logs -f jarvis

# Local
tail -f ./logs/jarvis.log
```

---

## 🔒 Segurança

### Permissões Necessárias

**Windows**:
- Executar como Administrador (para alguns comandos)

**Linux**:
- Permissões de usuário para apps e comandos
- `sudo` pode ser necessário para alguns comandos

**Android**:
- USB Debugging habilitado
- Autorizar conexão ADB no dispositivo

### Comandos Perigosos

⚠️ **CUIDADO**: O JARVIS pode executar QUALQUER comando no sistema!

**Evite**:
- `rm -rf /` (Linux)
- `Format-Volume` (Windows)
- Comandos destrutivos sem confirmação

**Recomendação**: Implemente whitelist de comandos em produção.

---

## 🎓 Melhores Práticas

### 1. Treinamento Contínuo

✅ **Faça**:
- Deixe habilitado por padrão
- Use JARVIS regularmente
- Monitore qualidade via status

❌ **Evite**:
- Desabilitar sem motivo
- Forçar treinamento muito frequente
- Ignorar métricas de qualidade

### 2. Controle de Sistema

✅ **Faça**:
- Teste comandos em ambiente seguro primeiro
- Use apps conhecidos
- Monitore processos ativos

❌ **Evite**:
- Comandos destrutivos
- Executar como root/admin sem necessidade
- Encerrar processos críticos do sistema

### 3. Modelos

✅ **Faça**:
- Compare modelos periodicamente
- Mantenha histórico de versões
- Use modelo ativo recomendado

❌ **Evite**:
- Trocar modelos manualmente sem razão
- Deletar modelos sem backup
- Ignorar recomendações de qualidade

---

## 🆘 Troubleshooting

### "System controller não disponível"

**Causa**: Sistema não detectado corretamente

**Solução**:
- Verifique logs de inicialização
- Confirme suporte para seu OS
- Reinstale dependências

### "ADB não disponível"

**Causa**: Android SDK não instalado

**Solução**:
```bash
# Windows (com Chocolatey)
choco install adb

# Linux
sudo apt install android-tools-adb

# macOS
brew install android-platform-tools
```

### "Continuous training não inicia"

**Causa**: Configuração incorreta ou dados insuficientes

**Solução**:
- Verifique `api/continuous-training/status`
- Acumule mais interações
- Verifique logs para erros

### "Modelo não melhora"

**Causa**: Poucos dados ou dados de baixa qualidade

**Solução**:
- Acumule 100+ interações variadas
- Verifique qualidade no dataset stats
- Ajuste `min_quality_score`
- Use treinamento full ao invés de incremental

---

## 📚 Documentação Adicional

- [API_DOCUMENTATION.md](API_DOCUMENTATION.md) - API completa
- [GUIA_TREINAMENTO_AVANCADO.md](GUIA_TREINAMENTO_AVANCADO.md) - Treinamento detalhado
- [README.md](README.md) - Visão geral do projeto

---

🎉 **Parabéns! Agora você tem um JARVIS completamente funcional!**

**O que você pode fazer**:
- ✅ Controlar Windows, Linux e Android
- ✅ Treinar modelo continuamente
- ✅ Pesquisar na web automaticamente
- ✅ Sistema sempre usa o melhor modelo
- ✅ Aprendizado perpétuo enquanto usa

**Próximos Passos**:
1. Use JARVIS normalmente
2. Deixe treinamento contínuo ativo
3. Monitore status periodicamente
4. Aproveite a melhoria automática!

---

**Dúvidas?** Consulte a documentação ou logs do sistema.
