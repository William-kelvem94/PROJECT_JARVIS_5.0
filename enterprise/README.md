# 🏗️ JARVIS Enterprise - Arquitetura de Microserviços

## Visão Geral

Arquitetura enterprise-level baseada em microserviços com comunicação assíncrona, orquestração distribuída e alta disponibilidade.

## Estrutura de Microserviços

```
enterprise/
├── core/                      # Componentes Core
│   ├── event_bus.py          # Event Bus para mensageria
│   ├── service_registry.py   # Registry de serviços
│   └── distributed_orchestrator.py  # Orquestração distribuída
├── services/                  # Microserviços
│   └── ai_engine.py          # Motor de IA empresarial
├── gateway/                   # API Gateway
│   └── api_gateway.py        # Gateway principal
└── docker-compose.enterprise.yml  # Orquestração Docker
```

## Componentes Principais

### 1. Event Bus

Sistema de mensageria pub-sub para comunicação assíncrona entre serviços.

**Features:**
- Suporte a Redis para distribuição
- Fallback em memória para desenvolvimento
- Request-Reply pattern
- Múltiplos canais

**Uso:**
```python
from enterprise.core.event_bus import EventBus, Event, EventType

event_bus = EventBus(use_redis=True)

# Publicar evento
event = Event(
    id="event-123",
    type=EventType.COMMAND,
    source="service-a",
    destination="service-b",
    payload={"action": "execute"},
    timestamp=datetime.now()
)
await event_bus.publish(event, channel="commands")

# Inscrever em canal
async def handler(event: Event):
    print(f"Recebido: {event.payload}")

event_bus.subscribe("commands", handler)
```

### 2. Service Registry

Descoberta e registro de serviços com health checks automáticos.

**Features:**
- Registro automático de serviços
- Heartbeat monitoring
- Health status tracking
- Service discovery

**Uso:**
```python
from enterprise.core.service_registry import ServiceRegistry

registry = ServiceRegistry()

# Registrar serviço
registry.register(
    name="ai-engine",
    version="1.0.0",
    host="ai-engine",
    port=8002,
    endpoints=["/generate", "/analyze"]
)

# Descobrir serviço
service_url = registry.get_service_url("ai-engine", "/generate")
```

### 3. Distributed Orchestrator

Orquestração distribuída com padrão Saga para transações complexas.

**Features:**
- Saga Pattern para transações distribuídas
- Compensação automática (rollback)
- Execução paralela de steps
- Retry e error handling

**Uso:**
```python
from enterprise.core.distributed_orchestrator import (
    DistributedOrchestrator, Command
)

orchestrator = DistributedOrchestrator(event_bus, service_registry)

command = Command(
    id="cmd-123",
    type="complex_workflow",
    payload={"data": "..."},
    source="user"
)

result = await orchestrator.process_command(command)
```

### 4. Enterprise AI Engine

Motor de IA com suporte a múltiplos modelos e ensemble.

**Features:**
- Model Registry
- Inference Optimization
- Model Ensembling
- Performance Metrics

**Uso:**
```python
from enterprise.services.ai_engine import EnterpriseAIEngine

ai_engine = EnterpriseAIEngine()

result = await ai_engine.enhanced_inference(
    prompt="Análise este documento",
    context={"document": "..."},
    requirements={"max_latency_ms": 1000}
)
```

## Deploy com Docker Compose

```bash
# Iniciar todos os serviços
docker-compose -f enterprise/docker-compose.enterprise.yml up -d

# Ver logs
docker-compose -f enterprise/docker-compose.enterprise.yml logs -f

# Parar serviços
docker-compose -f enterprise/docker-compose.enterprise.yml down
```

## Serviços Disponíveis

1. **Gateway** (8080) - API Gateway principal
2. **Core Orchestrator** (8001) - Orquestração distribuída
3. **AI Engine** (8002) - Motor de IA
4. **Automation Engine** (8003) - Automação
5. **Memory Manager** (8004) - Gerenciamento de memória
6. **Monitoring Dashboard** (8005) - Dashboard de monitoramento
7. **Redis** (6379) - Event Bus
8. **Ollama** (11434) - Servidor LLM

## Exemplos de Uso

### Enviar Comando via Gateway

```bash
curl -X POST http://localhost:8080/api/ai/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Explique quantum computing",
    "context": {}
  }'
```

### Listar Serviços

```bash
curl http://localhost:8080/api/services
```

### Health Check

```bash
curl http://localhost:8080/health
```

## Arquitetura de Comunicação

```
Client
  ↓
API Gateway (8080)
  ↓
Event Bus (Redis)
  ↓
┌─────────────┬─────────────┬─────────────┐
│ Orchestrator│  AI Engine  │ Automation │
│   (8001)    │   (8002)    │   (8003)   │
└─────────────┴─────────────┴─────────────┘
       ↓              ↓              ↓
  Service Registry ← Redis → Event Bus
```

## Próximos Passos

1. Implementar serviços restantes:
   - Voice Processor
   - Security Layer
   - Data Pipeline
   - Skill Registry

2. Adicionar recursos:
   - Authentication/Authorization
   - Rate Limiting avançado
   - Circuit Breakers por serviço
   - Distributed Tracing
   - Metrics Collection

3. Melhorias:
   - Auto-scaling
   - Load balancing
   - Service mesh (Istio/Linkerd)
   - Observabilidade completa

## Documentação Técnica

- [Event Bus API](./docs/event_bus.md)
- [Service Registry API](./docs/service_registry.md)
- [Orchestrator Patterns](./docs/orchestrator.md)
- [AI Engine Guide](./docs/ai_engine.md)

