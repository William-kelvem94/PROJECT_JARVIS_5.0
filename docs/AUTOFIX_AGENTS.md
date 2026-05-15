# 🤖 JARVIS Auto-Fix Agents — Sistema de Correção Automática

## 🎯 Visão Geral

**Agentes que não apenas detectam, mas CORRIGEM problemas automaticamente.**

Sistema de 4 agentes especializados que monitoram continuamente e aplicam correções quando possível, reduzindo a necessidade de intervenção manual.

**Data**: 7 de maio de 2026  
**Status**: ✅ IMPLEMENTADO  
**Total de Agentes**: 14 (10 análise + 4 auto-fix)

---

## 🆕 Agentes de Auto-Correção (4 Novos)

### 1. **AutoFixAgent** 🔧
**Interval**: 300s (5 min)  
**Função**: Orquestrador de correções automáticas

**Correções Aplicadas**:
- ✅ Cria diretórios faltando (holodeck, blackbox)
- ✅ Detecta dependências ausentes
- ⚠️ Não instala pacotes automaticamente (segurança)

**Como Funciona**:
1. Pega findings CRITICAL e HIGH de outros agentes
2. Analisa o tipo de problema
3. Aplica correção se for seguro
4. Registra ação aplicada

**Exemplo**:
```python
# Finding detectado:
"Módulos de Segurança Não Configurados: holodeck"

# Auto-Fix aplicado:
os.makedirs("data/holodeck", exist_ok=True)
logger.success("Created data/holodeck directory")
```

**Ativar/Desativar**:
```bash
# Ativar (padrão)
set JARVIS_AUTO_FIX=1

# Desativar
set JARVIS_AUTO_FIX=0
```

---

### 2. **DependencyHealthAgent** 📦
**Interval**: 600s (10 min)  
**Função**: Monitora dependências críticas

**Dependências Monitoradas**:
- ✅ face_recognition
- ✅ pygame
- ✅ deepfilternet
- ✅ sounddevice
- ✅ pycaw
- ✅ mediapipe
- ✅ ultralytics

**Findings Gerados**:
```json
{
  "severity": "high",
  "title": "Dependências Críticas Ausentes",
  "description": "3 dependência(s) não instalada(s): pygame, face_recognition, deepfilternet",
  "recommendation": "Execute: .venv\\Scripts\\pip.exe install pygame face_recognition deepfilternet"
}
```

**Benefício**: Detecta exatamente quais dependências estão faltando e fornece o comando exato para instalar.

---

### 3. **EndpointRecoveryAgent** 🌐
**Interval**: 30s  
**Função**: Detecta e recupera endpoints com falha

**Problemas Detectados**:
- ✅ ECONNRESET (socket hang up)
- ✅ Timeouts (>5s)
- ✅ Status codes inválidos

**Endpoints Monitorados**:
- `/health`
- `/telemetry/status`
- `/system/capabilities`

**Auto-Recovery**:
1. Detecta falha de endpoint
2. Aguarda 2 segundos
3. Tenta reconectar
4. Máximo 3 tentativas
5. Se falhar, recomenda reiniciar backend

**Exemplo de Finding**:
```json
{
  "severity": "critical",
  "title": "Socket Error: /telemetry/status",
  "description": "Conexão resetada abruptamente. Erro: ECONNRESET",
  "recommendation": "Verifique se há imports falhando no endpoint. Adicione try/except em cada componente.",
  "metrics": {
    "endpoint": "/telemetry/status",
    "error": "ECONNRESET",
    "recovery_attempted": 2
  }
}
```

**Benefício**: Detecta exatamente qual endpoint está falhando e quantas tentativas de recovery foram feitas.

---

### 4. **AudioSystemRepairAgent** 🔊
**Interval**: 180s (3 min)  
**Função**: Monitora e diagnostica sistema de áudio

**Verificações**:
- ✅ pycaw disponível
- ✅ Dispositivos de áudio detectados
- ✅ pygame instalado para playback

**Findings Gerados**:

**Caso 1: Sistema OK**
```json
{
  "severity": "info",
  "title": "Sistema de Áudio Disponível",
  "description": "pycaw detectou dispositivos de áudio"
}
```

**Caso 2: pycaw ausente**
```json
{
  "severity": "high",
  "title": "pycaw Não Instalado",
  "description": "Biblioteca de controle de áudio não disponível",
  "recommendation": "Execute: pip install pycaw comtypes"
}
```

**Caso 3: pygame ausente**
```json
{
  "severity": "high",
  "title": "Pygame Não Instalado",
  "description": "Playback de áudio local não disponível",
  "recommendation": "Execute: pip install pygame"
}
```

**Benefício**: Diagnóstico preciso do problema de áudio com solução específica.

---

## 📊 Total de Agentes (14)

### Agentes de Análise (10)
1. PerformanceAgent
2. SystemHealthAgent
3. SecurityAgent
4. CodeQualityAgent
5. UserExperienceAgent
6. ConnectivityAgent
7. CognitiveHealthAgent
8. PerceptionHealthAgent
9. SystemToolsAgent
10. SecurityModulesAgent

### Agentes de Auto-Correção (4) ⭐ NOVO
11. **AutoFixAgent**
12. **DependencyHealthAgent**
13. **EndpointRecoveryAgent**
14. **AudioSystemRepairAgent**

---

## 🚀 Como Usar

### Ver Findings de Auto-Fix

```bash
# Ver todos os findings
curl http://localhost:8000/agents/findings

# Filtrar apenas auto-fix
curl http://localhost:8000/agents/findings | jq '.findings[] | select(.title | contains("Auto-Fix"))'
```

### Ver Sumário dos Agentes

```bash
curl http://localhost:8000/agents/summary

# Deve mostrar:
{
  "total_agents": 14,
  "agents_running": 14,
  ...
}
```

### Ativar/Desativar Auto-Fix

```bash
# Windows
set JARVIS_AUTO_FIX=1
start-jarvis.bat

# Linux/Mac
export JARVIS_AUTO_FIX=1
./start-jarvis.sh
```

---

## 🔍 Correções Aplicadas Automaticamente

### ✅ Correções Seguras (Auto-Aplicadas)

1. **Criar Diretórios**
   ```python
   os.makedirs("data/holodeck", exist_ok=True)
   os.makedirs("data", exist_ok=True)
   ```

2. **Resetar Contadores de Falha**
   - Limpa tentativas de recovery após sucesso

### ⚠️ Correções Não Automáticas (Segurança)

1. **Instalar Dependências**
   - Detecta faltando
   - Fornece comando exato
   - Não instala automaticamente

2. **Reiniciar Serviços**
   - Detecta necessidade
   - Recomenda ação manual
   - Não reinicia automaticamente

3. **Conectar Hardware**
   - Detecta camera/mic offline
   - Recomenda verificação física
   - Não pode auto-corrigir

---

## 📈 Benefícios

### Para Usuários
- ✅ **Menos intervenção manual**: Problemas simples são corrigidos automaticamente
- ✅ **Diagnóstico preciso**: Sabe exatamente o que está errado
- ✅ **Comandos prontos**: Copia e cola para corrigir
- ✅ **Visibilidade total**: Vê o que foi auto-corrigido

### Para Desenvolvedores
- ✅ **Auto-healing**: Sistema se auto-repara
- ✅ **Logs detalhados**: Todas as ações registradas
- ✅ **Segurança**: Não faz mudanças perigosas automaticamente
- ✅ **Extensível**: Fácil adicionar novas correções

### Para Operação
- ✅ **Redução de downtime**: Problemas corrigidos em segundos
- ✅ **Prevenção proativa**: Detecta antes de virar problema
- ✅ **Métricas de recovery**: Quantas tentativas, taxa de sucesso
- ✅ **Alertas inteligentes**: Apenas problemas que precisam de atenção

---

## 🛡️ Segurança

### Princípios de Auto-Correção Segura

1. **Nunca Instalar Pacotes Automaticamente**
   - Pode ter conflitos de versão
   - Pode baixar pacotes maliciosos
   - Sempre requer confirmação manual

2. **Nunca Modificar Código**
   - Pode introduzir bugs
   - Pode quebrar funcionalidade
   - Sempre requer review

3. **Nunca Reiniciar Serviços Automaticamente**
   - Pode causar perda de dados
   - Pode interromper operações críticas
   - Sempre requer confirmação manual

4. **OK para Criar Diretórios**
   - Operação idempotente
   - Não afeta dados existentes
   - Seguro para auto-aplicar

5. **OK para Resetar Contadores**
   - Apenas estado interno
   - Não afeta sistema externo
   - Seguro para auto-aplicar

---

## 📚 Exemplos de Uso

### Exemplo 1: Diretório Faltando

**Before**:
```bash
curl http://localhost:8000/agents/findings

# Finding:
{
  "title": "Módulos de Segurança Não Configurados",
  "description": "holodeck não configurado"
}
```

**After** (5 minutos depois):
```bash
# Auto-Fix aplicado:
{
  "title": "Auto-Fix Applied: Módulos de Segurança Não Configurados",
  "description": "Correção automática aplicada: Created data/holodeck directory"
}

# Verificar:
dir data\holodeck
# Diretório existe!
```

---

### Exemplo 2: Dependência Faltando

**Before**:
```bash
# Logs mostram:
WARNING: pygame não instalado

# Agent detecta:
{
  "title": "Pygame Não Instalado",
  "recommendation": "Execute: pip install pygame"
}
```

**Action** (manual):
```bash
.venv\Scripts\pip.exe install pygame
```

**After**:
```bash
# Próxima verificação (10 min):
{
  "title": "Pygame Disponível",
  "description": "Sistema de TTS funcional"
}
```

---

### Exemplo 3: Endpoint com Socket Hang Up

**Before**:
```bash
# Frontend logs:
Failed to proxy http://localhost:8000/telemetry/status [Error: socket hang up] { code: 'ECONNRESET' }

# Agent detecta:
{
  "severity": "critical",
  "title": "Socket Error: /telemetry/status",
  "description": "ECONNRESET",
  "recommendation": "Verifique imports do endpoint",
  "metrics": {
    "recovery_attempted": 0
  }
}
```

**Auto-Recovery** (30 segundos):
```bash
# Tentativa 1: aguarda 2s, tenta reconectar
# Se falhar: Tentativa 2
# Se falhar: Tentativa 3
# Se falhar: Recomenda reiniciar backend

# Finding atualizado:
{
  "title": "Endpoint Recovery Failed: /telemetry/status",
  "description": "Tentativas excedidas (3/3)",
  "recommendation": "Reinicie o backend: scripts/restart-jarvis.bat",
  "metrics": {
    "recovery_attempted": 3
  }
}
```

---

## ✅ Validação

### Verificar Se Agentes Estão Ativos

```bash
curl http://localhost:8000/agents/summary | jq

# Esperado:
{
  "total_agents": 14,
  "agents_running": 14,
  "agents": [
    ...
    {
      "name": "AutoFixAgent",
      "type": "health",
      "running": true
    },
    {
      "name": "DependencyHealthAgent",
      "type": "health",
      "running": true
    },
    {
      "name": "EndpointRecoveryAgent",
      "type": "health",
      "running": true
    },
    {
      "name": "AudioSystemRepairAgent",
      "type": "health",
      "running": true
    }
  ]
}
```

### Testar Auto-Fix

```bash
# 1. Criar problema (deletar diretório)
rmdir /s data\holodeck

# 2. Aguardar 5 minutos (interval do AutoFixAgent)

# 3. Verificar se foi criado automaticamente
dir data\holodeck
# Deve existir!

# 4. Ver finding de auto-fix
curl http://localhost:8000/agents/findings | jq '.findings[] | select(.title | contains("Auto-Fix"))'
```

---

## 🎯 Roadmap

### Próximas Correções Automáticas

1. **Database Cleanup Agent**
   - Limpa logs antigos automaticamente
   - Remove arquivos temporários
   - Otimiza banco de dados

2. **Model Download Agent**
   - Baixa modelos faltando (YOLOv8)
   - Verifica integridade
   - Atualiza quando necessário

3. **Config Repair Agent**
   - Corrige arquivos .env malformados
   - Restaura configs padrão
   - Valida sintaxe

4. **Network Optimization Agent**
   - Ajusta timeouts automaticamente
   - Otimiza pool de conexões
   - Detecta e corrige rate limits

---

## 📖 Documentação Relacionada

- 📋 [docs/reports/SUMMARY.md](reports/SUMMARY.md) - Sumário executivo
- 🤖 [MULTI_AGENT_SYSTEM.md](./MULTI_AGENT_SYSTEM.md) - Sistema multi-agente original
- 🏥 [REALTIME_HEALTH_SYSTEM.md](./REALTIME_HEALTH_SYSTEM.md) - Health checking
- 🌐 [CONNECTIVITY_FIX.md](./CONNECTIVITY_FIX.md) - Correção de proxy

---

**Autor**: GitHub Copilot (Claude Sonnet 4.5)  
**Data**: 7 de maio de 2026  
**Versão**: JARVIS 5.0 Omega  
**Total de Agentes**: 14 (10 análise + 4 auto-fix)
