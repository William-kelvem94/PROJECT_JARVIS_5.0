# 🏥 Health Checking em Tempo Real - Guia Rápido

## 🎯 O Que Foi Implementado

Sistema completo de monitoramento em tempo real que verifica automaticamente:

### 19 Componentes Monitorados

#### 🧠 Núcleo Cognitivo (4)
- Smart Router
- Memoria Unificada
- Engineer Brain
- Persona Adaptativa

#### 👁️ Percepção (4)
- Face Engine
- Gestos
- Objetos
- Audio em Tempo Real

#### ⚙️ Sistema (4)
- OS Tools
- Browser Engine
- Capturas
- Execução Assistida

#### 🛡️ Segurança (4)
- Sentinel Parser
- BlackBox
- Holodeck
- Biometric Vault

#### 💻 Hardware (3)
- **Camera** ⭐
- **Microfone** ⭐
- **Espelhamento de Tela** ⭐

### 10 Agentes Especializados

**6 Originais**:
1. PerformanceAgent
2. SystemHealthAgent
3. SecurityAgent
4. CodeQualityAgent
5. UserExperienceAgent
6. ConnectivityAgent

**4 Novos** ⭐:
7. **CognitiveHealthAgent** - Monitora núcleo cognitivo
8. **PerceptionHealthAgent** - Monitora percepção e hardware
9. **SystemToolsAgent** - Monitora ferramentas de sistema
10. **SecurityModulesAgent** - Monitora módulos de segurança

---

## 🚀 Como Usar

### 1. Testar o Sistema

```batch
# Validar implementação
scripts/test-health-system.bat
```

O script testa:
- ✅ Endpoint `/system/capabilities`
- ✅ Endpoint `/system/hardware`
- ✅ Endpoint `/agents/summary`
- ✅ Contagem de 19 componentes
- ✅ Verificação de 10 agentes

### 2. Ver Status via API

```bash
# Status completo (19 componentes)
curl http://localhost:8000/system/capabilities

# Status específico de hardware
curl http://localhost:8000/system/hardware

# Ver agentes ativos (deve mostrar 10)
curl http://localhost:8000/agents/summary
```

### 3. Acessar Dashboard

```
http://localhost:3000
```

**Features do Dashboard**:
- ✅ Status em tempo real (atualiza a cada 5s)
- ✅ Indicadores coloridos por status
- ✅ Health percentage do sistema
- ✅ Detalhamento de cada componente

---

## 📊 Status Types

| Status | Cor | Significado |
|--------|-----|-------------|
| `online` | 🟢 Verde | Funcionando perfeitamente |
| `offline` | 🔴 Vermelho | Não disponível |
| `degraded` | 🟡 Amarelo | Funcionando parcialmente |
| `error` | 🔴 Vermelho | Erro detectado |
| `initializing` | 🔵 Azul | Inicializando |
| `not_configured` | ⚪ Cinza | Não configurado |

---

## 🔍 Verificar Problemas

### Camera/Microfone Offline?

```bash
# Ver status de hardware
curl http://localhost:8000/system/hardware

# Ver findings relacionados
curl http://localhost:8000/agents/findings | grep -i "hardware"
```

**Ação**: Conecte os dispositivos e reinicie o sistema.

### Componente NOT_CONFIGURED?

```bash
# Ver detalhes
curl http://localhost:8000/system/capabilities | jq '.capabilities | .. | select(.status? == "not_configured")'
```

**Ação**: Alguns módulos não são críticos (smart_router, holodeck). Outros precisam ser instalados (face_recognition, mediapipe).

### Health Percentage Baixo?

```bash
# Ver problemas críticos
curl http://localhost:8000/agents/critical
```

**Ação**: Corrija os problemas HIGH e CRITICAL primeiro.

---

## 📈 Endpoints Disponíveis

| Endpoint | Descrição | Refresh |
|----------|-----------|---------|
| `GET /system/capabilities` | Status de todos os 19 componentes | Manual |
| `GET /system/hardware` | Status de camera/mic/tela | Manual |
| `GET /agents/summary` | Sumário dos 10 agentes | Manual |
| `GET /agents/findings` | Todos os findings | Manual |
| `GET /agents/critical` | Apenas HIGH/CRITICAL | Manual |

**Frontend**: Atualização automática a cada 5 segundos.

---

## ✅ Validação

### Checklist

```bash
# 1. Backend rodando?
curl http://localhost:8000/health

# 2. Capabilities funcionando?
curl http://localhost:8000/system/capabilities | jq '.summary'

# 3. Agentes ativos?
curl http://localhost:8000/agents/summary | jq '.total_agents'
# Esperado: 10

# 4. Frontend acessível?
# http://localhost:3000
```

### Teste Completo

```batch
# Executar suite de testes
scripts/test-health-system.bat
```

**Resultado esperado**:
- ✅ 4 testes passaram
- 📊 19 componentes detectados
- 🤖 10 agentes ativos
- 💚 Health percentage visível

---

## 🎯 Exemplo de Resposta

### `/system/capabilities`

```json
{
  "capabilities": {
    "nucleo_cognitivo": {
      "title": "Nucleo cognitivo",
      "components": [
        {
          "name": "Smart router",
          "status": "not_configured",
          "available": false,
          "message": "Módulo não implementado"
        }
      ]
    },
    "hardware": {
      "title": "Hardware",
      "components": [
        {
          "name": "camera",
          "status": "offline",
          "available": false,
          "message": "Câmera não detectada",
          "error": "Camera not available"
        },
        {
          "name": "microfone",
          "status": "offline",
          "available": false,
          "message": "Nenhum microfone detectado"
        },
        {
          "name": "espelhamento_tela",
          "status": "online",
          "available": true,
          "message": "Captura de tela funcionando"
        }
      ]
    }
  },
  "summary": {
    "total": 19,
    "online": 12,
    "offline": 4,
    "degraded": 1,
    "error": 0,
    "not_configured": 2,
    "health_percentage": 63.2
  }
}
```

### `/agents/summary`

```json
{
  "total_agents": 10,
  "agents_running": 10,
  "agents": [
    {
      "name": "PerformanceAgent",
      "type": "performance",
      "running": true,
      "interval": 60
    },
    {
      "name": "CognitiveHealthAgent",
      "type": "health",
      "running": true,
      "interval": 120
    },
    {
      "name": "PerceptionHealthAgent",
      "type": "health",
      "running": true,
      "interval": 90
    }
    // ... 7 mais
  ]
}
```

---

## 🛠️ Troubleshooting

### Problema: Endpoint não responde

```bash
# Verificar se backend está rodando
netstat -ano | findstr :8000

# Se não estiver, iniciar
cd backend
python -m uvicorn app.main:app --reload
```

### Problema: Health percentage = 0%

**Causa**: Backend não iniciou corretamente ou imports falharam.

**Solução**:
```bash
# 1. Verificar logs
type logs\jarvis_*.log | findstr ERROR

# 2. Validar dependências
scripts/validate-improvements.bat

# 3. Testar imports manualmente
python -c "from app.health_checker import get_health_checker; print('OK')"
```

### Problema: Agentes não aparecem

**Causa**: Multi-agent system não inicializou.

**Solução**:
```bash
# Verificar se está no lifespan
python -c "from app.main import app; print('OK')"

# Ver logs de inicialização
type logs\jarvis_*.log | findstr "MultiAgent"
```

---

## 📚 Documentação Completa

- 📖 [REALTIME_HEALTH_SYSTEM.md](../REALTIME_HEALTH_SYSTEM.md) - Documentação técnica completa
- 🤖 [MULTI_AGENT_SYSTEM.md](../MULTI_AGENT_SYSTEM.md) - Sistema multi-agente
- 📋 [docs/reports/SUMMARY.md](../reports/SUMMARY.md) - Sumário de todas as melhorias

---

## 🎉 Resultado

**Status**: ✅ IMPLEMENTADO E FUNCIONAL

- ✅ 19 componentes monitorados
- ✅ 10 agentes especializados
- ✅ 2 novos endpoints
- ✅ Frontend em tempo real (5s)
- ✅ Detecção de camera/mic/tela
- ✅ Health percentage do sistema
- ✅ Findings específicos por categoria

**Health Percentage**:
- 🟢 90-100%: Sistema saudável
- 🟡 70-89%: Sistema funcional
- 🟠 50-69%: Sistema degradado
- 🔴 0-49%: Sistema crítico

---

**Autor**: GitHub Copilot (Claude Sonnet 4.5)  
**Data**: 7 de maio de 2026  
**Versão**: JARVIS 5.0 Omega
