# 🏥 JARVIS 5.0 — Sistema de Health Check em Tempo Real

## 📋 Visão Geral

Sistema completo de monitoramento e análise de saúde de todos os componentes do JARVIS, com **status em tempo real** e **10 agentes especializados** para detecção automática de problemas.

**Data**: 7 de maio de 2026  
**Status**: ✅ IMPLEMENTADO  
**Agentes**: 10 ativos (6 originais + 4 novos especializados)

---

## 🎯 Problema Resolvido

**Antes**:
- ❌ Capabilities mostradas estáticamente
- ❌ Sem verificação real de disponibilidade
- ❌ Camera/microfone/tela não detectados
- ❌ Sem visibilidade de componentes offline
- ❌ Debugging manual necessário

**Agora**:
- ✅ Status em tempo real (atualiza a cada 5s)
- ✅ Verificação real de cada componente
- ✅ Detecção automática de hardware
- ✅ Visibilidade total do sistema
- ✅ 10 agentes detectam e reportam problemas automaticamente

---

## 🏗️ Arquitetura

### 1. Health Checker (`backend/app/health_checker.py`)

Módulo central que verifica a saúde de **19 componentes**:

#### Núcleo Cognitivo (4 componentes)
- **Smart Router**: Roteamento inteligente de queries
- **Memoria Unificada**: Sistema de memória vetorial
- **Engineer Brain**: Raciocínio técnico
- **Persona Adaptativa**: Sistema de personalidade

#### Percepção (4 componentes)
- **Face Engine**: Reconhecimento facial (face_recognition)
- **Gestos**: Detecção de gestos (mediapipe)
- **Objetos**: Detecção de objetos (YOLOv8)
- **Audio em Tempo Real**: Wake word + transcrição

#### Sistema (4 componentes)
- **OS Tools**: Controle de sistema (volume, brightness, screenshots)
- **Browser Engine**: Automação web (Playwright)
- **Capturas**: Screenshots e gravação de tela (mss)
- **Execução Assistida**: Automação de interface (pyautogui)

#### Segurança (4 componentes)
- **Sentinel Parser**: Análise de comandos perigosos
- **BlackBox**: Logging criptografado
- **Holodeck**: Sandbox de testes
- **Biometric Vault**: Armazenamento biométrico

#### Hardware (3 componentes)
- **Camera**: Detecção de webcam (opencv)
- **Microfone**: Detecção de dispositivos de entrada (sounddevice)
- **Espelhamento de Tela**: Captura de tela (mss)

### 2. Multi-Agent System (Expandido)

#### 6 Agentes Originais:
1. **PerformanceAgent** (60s) - CPU, RAM, threads
2. **SystemHealthAgent** (300s) - Disk, services
3. **SecurityAgent** (600s) - Permissions, configs
4. **CodeQualityAgent** (3600s) - Code patterns
5. **UserExperienceAgent** (900s) - Response times
6. **ConnectivityAgent** (60s) - API health

#### 4 Novos Agentes Especializados:
7. **CognitiveHealthAgent** (120s) - Monitora núcleo cognitivo
8. **PerceptionHealthAgent** (90s) - Monitora percepção e hardware
9. **SystemToolsAgent** (180s) - Monitora ferramentas de sistema
10. **SecurityModulesAgent** (300s) - Monitora módulos de segurança

### 3. API Endpoints

#### Novos Endpoints:

```bash
# Status completo de todas as capabilities
GET /system/capabilities

# Status específico de hardware
GET /system/hardware
```

#### Endpoints Existentes:

```bash
# Health check básico
GET /health

# Telemetria geral
GET /telemetry/status

# Sumário de agentes
GET /agents/summary

# Todos os findings
GET /agents/findings

# Apenas críticos
GET /agents/critical
```

### 4. Frontend Component

**Novo componente**: `CapabilitiesStatusGrid`
- ✅ Atualização automática a cada 5 segundos
- ✅ Status colorido por tipo (online/offline/degraded/error)
- ✅ Agrupamento por categoria
- ✅ Métricas de saúde geral
- ✅ Mensagens de erro detalhadas

---

## 📊 Status Types

```python
class ComponentStatus(Enum):
    ONLINE = "online"              # ✅ Funcionando perfeitamente
    OFFLINE = "offline"            # ❌ Não disponível
    DEGRADED = "degraded"          # ⚠️ Funcionando parcialmente
    ERROR = "error"                # 🔴 Erro detectado
    INITIALIZING = "initializing"  # 🔄 Inicializando
    NOT_CONFIGURED = "not_configured"  # ⚙️ Não configurado
```

---

## 🚀 Como Usar

### Verificar Status via API

```bash
# Ver status completo
curl http://localhost:8000/system/capabilities | jq

# Resposta:
{
  "capabilities": {
    "nucleo_cognitivo": {
      "title": "Nucleo cognitivo",
      "components": [
        {
          "name": "Smart router",
          "status": "online",
          "available": true,
          "message": "Roteamento inteligente ativo"
        },
        // ...
      ]
    },
    "percepcao": { /* ... */ },
    "sistema": { /* ... */ },
    "seguranca": { /* ... */ },
    "hardware": { /* ... */ }
  },
  "summary": {
    "total": 19,
    "online": 15,
    "offline": 2,
    "degraded": 1,
    "error": 0,
    "not_configured": 1,
    "health_percentage": 78.9
  }
}
```

### Ver Findings de Saúde

```bash
# Findings de saúde dos novos agentes
curl http://localhost:8000/agents/findings | jq '.findings[] | select(.title | contains("Health"))'

# Exemplo:
{
  "agent_type": "health",
  "severity": "critical",
  "title": "Hardware de Percepção Offline",
  "description": "Hardware necessário não disponível: camera, microphone",
  "recommendation": "Verifique se camera, microphone está(ão) conectado(s) e funcionando. Reinicie o sistema se necessário.",
  "timestamp": "2026-05-07T14:30:00"
}
```

### Frontend - Dashboard

Acesse: `http://localhost:3000`

O dashboard agora mostra:
- ✅ Status em tempo real de todos os componentes
- ✅ Indicadores coloridos (verde/vermelho/amarelo)
- ✅ Métricas de saúde geral (% de componentes online)
- ✅ Atualização automática a cada 5 segundos

---

## 🔍 Detecção de Problemas

### Exemplos de Problemas Detectados

#### 1. Hardware Offline (CRITICAL)
```json
{
  "title": "Hardware de Percepção Offline",
  "severity": "critical",
  "description": "Camera e microfone não detectados",
  "recommendation": "Conecte os dispositivos e reinicie"
}
```

#### 2. Componentes Não Configurados (MEDIUM)
```json
{
  "title": "Módulos de Segurança Não Configurados",
  "severity": "medium",
  "description": "Holodeck não configurado",
  "recommendation": "Configure o diretório holodeck"
}
```

#### 3. Componentes Degradados (HIGH)
```json
{
  "title": "Componentes de Percepção Degradados",
  "severity": "high",
  "description": "Face engine não disponível",
  "recommendation": "Instale face_recognition"
}
```

---

## 📈 Métricas e Monitoramento

### Health Percentage

```python
health_percentage = (online_components / total_components) * 100

# Interpretação:
# 90-100%: Sistema saudável ✅
# 70-89%:  Sistema funcional ⚠️
# 50-69%:  Sistema degradado 🟠
# 0-49%:   Sistema crítico 🔴
```

### Intervalos de Verificação

- **CognitiveHealthAgent**: 120s (2 min)
- **PerceptionHealthAgent**: 90s (1.5 min)
- **SystemToolsAgent**: 180s (3 min)
- **SecurityModulesAgent**: 300s (5 min)

### Atualização do Frontend

- **Polling**: A cada 5 segundos
- **Automatic refresh**: Sim
- **Error handling**: Sim, com fallback

---

## 🛠️ Troubleshooting

### Problema: Camera/Microfone Offline

```bash
# 1. Verificar status
curl http://localhost:8000/system/hardware

# 2. Verificar findings
curl http://localhost:8000/agents/findings | grep -i "hardware"

# 3. Testar manualmente
python -c "import cv2; cap = cv2.VideoCapture(0); print('Camera:', cap.isOpened())"
python -c "import sounddevice; print('Devices:', len(sounddevice.query_devices()))"
```

### Problema: Componente NOT_CONFIGURED

```bash
# Ver detalhes do componente
curl http://localhost:8000/system/capabilities | jq '.capabilities | .. | select(.status? == "not_configured")'

# Exemplo de output:
{
  "name": "Smart router",
  "status": "not_configured",
  "message": "Módulo smart_router não encontrado",
  "error": "Module not implemented yet"
}
```

**Solução**: Implementar o módulo ou ignorar se não for crítico.

### Problema: Alto Número de Erros

```bash
# Ver todos os erros
curl http://localhost:8000/agents/critical

# Ver componentes com erro
curl http://localhost:8000/system/capabilities | jq '.capabilities | .. | select(.status? == "error")'
```

---

## 📚 Estrutura de Resposta

### `/system/capabilities`

```typescript
interface CapabilitiesResponse {
  capabilities: {
    nucleo_cognitivo: CapabilityGroup;
    percepcao: CapabilityGroup;
    sistema: CapabilityGroup;
    seguranca: CapabilityGroup;
    hardware: CapabilityGroup;
  };
  summary: {
    total: number;
    online: number;
    offline: number;
    degraded: number;
    error: number;
    not_configured: number;
    health_percentage: number;
  };
  timestamp: string;
}

interface CapabilityGroup {
  title: string;
  components: ComponentHealth[];
}

interface ComponentHealth {
  name: string;
  status: 'online' | 'offline' | 'degraded' | 'error' | 'initializing' | 'not_configured';
  available: boolean;
  message: string;
  details?: Record<string, any>;
  error?: string | null;
}
```

---

## 🎯 Benefícios

### Para Usuários
- ✅ **Visibilidade total**: Sabe exatamente o que está funcionando
- ✅ **Feedback instantâneo**: Status atualiza em tempo real
- ✅ **Diagnóstico fácil**: Mensagens claras sobre problemas
- ✅ **Confiabilidade**: Sabe que pode confiar no sistema

### Para Desenvolvedores
- ✅ **Debug rápido**: Identifica problemas imediatamente
- ✅ **Health checks automáticos**: Não precisa testar manualmente
- ✅ **Findings detalhados**: Agentes reportam problemas com contexto
- ✅ **Extensível**: Fácil adicionar novos componentes

### Para Operação
- ✅ **Monitoramento 24/7**: 10 agentes sempre ativos
- ✅ **Alertas automáticos**: Findings críticos/high reportados
- ✅ **Métricas centralizadas**: Health percentage do sistema
- ✅ **Histórico**: Todos os findings são registrados

---

## 🔧 Implementação Técnica

### Health Check Example

```python
def check_face_engine(self) -> ComponentHealth:
    """Verifica Face Engine (reconhecimento facial)."""
    try:
        import face_recognition
        return ComponentHealth(
            name="Face engine",
            status=ComponentStatus.ONLINE,
            available=True,
            message="Reconhecimento facial disponível (Level A)",
            details={
                "library": "face_recognition",
                "level": "A (identity)"
            },
            dependencies=["camera"]
        )
    except ImportError:
        return ComponentHealth(
            name="Face engine",
            status=ComponentStatus.NOT_CONFIGURED,
            available=False,
            message="face_recognition não instalado",
            error="pip install face_recognition"
        )
```

### Agent Example

```python
class PerceptionHealthAgent(BaseAgent):
    """Agente que monitora saúde do sistema de percepção."""
    
    def __init__(self):
        super().__init__(AgentType.SYSTEM_HEALTH, "PerceptionHealthAgent", check_interval=90)
    
    async def analyze(self) -> List[Finding]:
        findings = []
        checker = get_health_checker()
        
        # Verificar hardware
        hardware_status = {
            "camera": checker.last_check.get("camera"),
            "microphone": checker.last_check.get("microphone"),
            "screen_mirror": checker.last_check.get("espelhamento_tela")
        }
        
        offline_hardware = [
            hw_name for hw_name, health in hardware_status.items()
            if health and not health.available
        ]
        
        if offline_hardware:
            findings.append(Finding(
                agent_type=self.agent_type,
                severity=Severity.CRITICAL,
                title="Hardware de Percepção Offline",
                description=f"Hardware não disponível: {', '.join(offline_hardware)}",
                recommendation="Conecte os dispositivos e reinicie"
            ))
        
        return findings
```

---

## 📊 Dashboard Visual

O novo componente `CapabilitiesStatusGrid` mostra:

```
┌─────────────────────────────────────────────────────┐
│  Online: 15/19   Offline: 2/19   Health: 78%       │
└─────────────────────────────────────────────────────┘

┌─────────────── Nucleo cognitivo ───────────────────┐
│ Smart router               [ONLINE]                 │
│ Memoria unificada          [ERROR]                  │
│ Engineer brain             [ONLINE]                 │
│ Persona adaptativa         [ONLINE]                 │
└─────────────────────────────────────────────────────┘

┌─────────────────── Percepcao ──────────────────────┐
│ Face engine                [NOT_CONFIGURED]         │
│ Gestos                     [ONLINE]                 │
│ Objetos                    [ONLINE]                 │
│ Audio em tempo real        [DEGRADED]               │
└─────────────────────────────────────────────────────┘

... (Sistema, Segurança, Hardware)
```

**Cores**:
- 🟢 Verde: ONLINE
- 🔴 Vermelho: OFFLINE / ERROR
- 🟡 Amarelo: DEGRADED
- 🔵 Azul: INITIALIZING
- ⚪ Cinza: NOT_CONFIGURED

---

## ✅ Validação

### Testar Health Checker

```bash
# 1. Iniciar backend
cd backend
python -m uvicorn app.main:app --reload

# 2. Verificar endpoints
curl http://localhost:8000/system/capabilities

# 3. Verificar agentes
curl http://localhost:8000/agents/summary

# Deve mostrar:
# - total_agents: 10
# - agents_running: 10
# - 4 novos agentes listados
```

### Testar Frontend

```bash
# 1. Iniciar frontend
cd frontend
npm run dev

# 2. Acessar
# http://localhost:3000

# 3. Verificar
# - Status cards atualizando a cada 5s
# - Componentes com cores corretas
# - Métricas de saúde visíveis
```

---

## 🎉 Resultado Final

### Antes vs Depois

| Aspecto | Antes | Agora |
|---------|-------|-------|
| Status | Estático | ✅ Tempo real (5s) |
| Verificação | Manual | ✅ Automática |
| Agentes | 6 | ✅ 10 especializados |
| Hardware | Não detectado | ✅ Detectado (camera/mic/screen) |
| Componentes | 0 | ✅ 19 monitorados |
| Health % | N/A | ✅ 0-100% |
| Findings | Genéricos | ✅ Específicos por subsistema |

### Status do Sistema

✅ **100% IMPLEMENTADO**

- ✅ Health checker completo (19 componentes)
- ✅ 10 agentes especializados
- ✅ 2 novos endpoints
- ✅ Frontend com status em tempo real
- ✅ Detecção automática de hardware
- ✅ Findings específicos por categoria
- ✅ Documentação completa

---

## 📖 Documentação Relacionada

- 📋 [SUMMARY.md](../SUMMARY.md) - Sumário executivo
- 🤖 [MULTI_AGENT_SYSTEM.md](./MULTI_AGENT_SYSTEM.md) - Sistema multi-agente
- 🌐 [CONNECTIVITY_FIX.md](./CONNECTIVITY_FIX.md) - Correção de proxy
- 📝 [IMPROVEMENTS_2026-05-07.md](./IMPROVEMENTS_2026-05-07.md) - Todas as melhorias

---

**Autor**: GitHub Copilot (Claude Sonnet 4.5)  
**Data**: 7 de maio de 2026  
**Versão**: JARVIS 5.0 Omega  
**Agentes Ativos**: 10  
**Componentes Monitorados**: 19
