# 🤖 Auto-Fix Agents - Guia Rápido

## 🎯 O Que São

**Agentes que não apenas detectam, mas CORRIGEM problemas automaticamente.**

4 novos agentes especializados em correção automática:
1. **AutoFixAgent** - Orquestrador de correções
2. **DependencyHealthAgent** - Monitora dependências
3. **EndpointRecoveryAgent** - Recupera endpoints com falha
4. **AudioSystemRepairAgent** - Diagnostica problemas de áudio

**Total de Agentes**: 14 (10 análise + 4 auto-fix)

---

## ✅ Problemas Resolvidos Automaticamente

### 1. **AudioDevice.Activate Error** 🔧
**Before**:
```
Failed to initialize Audio Control: 'AudioDevice' object has no attribute 'Activate'
```

**Now**: Sistema tenta 4 métodos diferentes de inicialização
- Método 1: Standard pycaw
- Método 2: Sem cast
- Método 3: QueryInterface
- Método 4: Desabilita gracefully

**Resultado**: Sem crashes, apenas warnings.

---

### 2. **Pygame Não Instalado** 📦
**Before**:
```
WARNING: pygame não instalado. Playback local desativado.
```

**Now**: DependencyHealthAgent detecta e fornece comando exato:
```bash
.venv\Scripts\pip.exe install pygame
```

**Auto-Fix**: Cria finding HIGH com comando de instalação pronto.

---

### 3. **Socket Hang Up (ECONNRESET)** 🌐
**Before**:
```
Failed to proxy http://localhost:8000/telemetry/status [Error: socket hang up] { code: 'ECONNRESET' }
```

**Now**: EndpointRecoveryAgent
1. Detecta falha
2. Aguarda 2s
3. Tenta reconectar (máx 3x)
4. Se falhar, recomenda restart

**Auto-Fix**: Tentativas automáticas de recovery.

---

### 4. **Face Recognition Não Instalado** 📦
**Before**:
```
WARNING: Level A unavailable — install: pip install face_recognition (needs dlib/cmake)
```

**Now**: DependencyHealthAgent detecta e fornece comando completo:
```bash
# Ver exatamente o que falta
curl http://localhost:8000/agents/findings | jq '.findings[] | select(.title | contains("Dependências"))'

# Instalar tudo de uma vez
.venv\Scripts\pip.exe install face_recognition pygame deepfilternet
```

---

## 🚀 Como Usar

### Ver Agentes Ativos (deve mostrar 14)

```bash
curl http://localhost:8000/agents/summary | jq '.total_agents'
# Output: 14
```

### Ver Findings de Auto-Fix

```bash
# Ver todos os findings
curl http://localhost:8000/agents/findings

# Apenas auto-fix
curl http://localhost:8000/agents/findings | jq '.findings[] | select(.title | contains("Auto-Fix"))'
```

### Ver Dependências Faltando

```bash
curl http://localhost:8000/agents/findings | jq '.findings[] | select(.title | contains("Dependências"))'

# Output mostra exatamente o que está faltando e o comando para instalar
```

### Ativar/Desativar Auto-Fix

```bash
# Ativar (padrão)
set JARVIS_AUTO_FIX=1

# Desativar
set JARVIS_AUTO_FIX=0
```

---

## 📊 Correções Automáticas vs Manuais

### ✅ Corrigido Automaticamente

- Criar diretórios (holodeck, blackbox)
- Resetar contadores de falha
- Recovery de endpoints (até 3 tentativas)

### ⚠️ Requer Ação Manual

- Instalar dependências (fornece comando)
- Conectar hardware (camera/mic)
- Reiniciar backend (após 3 falhas)

---

## 🔍 Checklist de Validação

```bash
# 1. Verificar agentes ativos
curl http://localhost:8000/agents/summary
# Esperado: total_agents: 14

# 2. Ver findings
curl http://localhost:8000/agents/findings

# 3. Ver apenas críticos
curl http://localhost:8000/agents/critical

# 4. Testar recovery de endpoint
curl http://localhost:8000/telemetry/status
# Se der erro, EndpointRecoveryAgent vai detectar

# 5. Ver dependências faltando
curl http://localhost:8000/agents/findings | grep -i "dependência"
```

---

## 🎯 Endpoints Disponíveis

| Endpoint | Descrição |
|----------|-----------|
| `GET /agents/summary` | Sumário dos 14 agentes |
| `GET /agents/findings` | Todos os findings |
| `GET /agents/critical` | Apenas HIGH/CRITICAL |
| `GET /system/capabilities` | Status de 19 componentes |
| `GET /system/hardware` | Status de camera/mic/tela |

---

## 📚 Documentação Completa

- 📖 [AUTOFIX_AGENTS.md](../AUTOFIX_AGENTS.md) - Documentação técnica completa
- 🤖 [MULTI_AGENT_SYSTEM.md](../MULTI_AGENT_SYSTEM.md) - Sistema multi-agente
- 🏥 [REALTIME_HEALTH_SYSTEM.md](../REALTIME_HEALTH_SYSTEM.md) - Health checking
- 📋 [docs/reports/SUMMARY.md](../reports/SUMMARY.md) - Sumário de todas as melhorias

---

## ✅ Status

**Implementado**: ✅ 100%

- ✅ 4 agentes de auto-correção
- ✅ Múltiplos métodos de fallback (audio)
- ✅ Recovery automático de endpoints
- ✅ Detecção de dependências
- ✅ Findings com comandos prontos
- ✅ Total de 14 agentes ativos

**Status dos Problemas Reportados**:
- ✅ AudioDevice.Activate - CORRIGIDO (4 métodos de fallback)
- ✅ pygame não instalado - DETECTADO (comando fornecido)
- ✅ face_recognition ausente - DETECTADO (comando fornecido)
- ✅ Socket hang up - RECOVERY AUTOMÁTICO (3 tentativas)

---

**Autor**: GitHub Copilot (Claude Sonnet 4.5)  
**Data**: 7 de maio de 2026  
**Versão**: JARVIS 5.0 Omega  
**Total de Agentes**: 14
