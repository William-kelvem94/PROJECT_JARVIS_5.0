# 🏗️ Arquitetura Enterprise JARVIS - Documentação Completa

## Visão Geral da Arquitetura

A arquitetura JARVIS Enterprise é baseada em **microserviços distribuídos** com comunicação assíncrona via **Event Bus**, orquestração usando **Saga Pattern** e descoberta de serviços através de **Service Registry**.

## Componentes Fundamentais

### 1. Event Bus (Pub-Sub)

**Localização**: `enterprise/core/event_bus.py`

**Responsabilidades**:
- Comunicação assíncrona entre serviços
- Padrão publish-subscribe
- Request-Reply para comunicação síncrona
- Suporte a Redis para distribuição

**Características**:
- ✅ Múltiplos canais
- ✅ Mensagens tipadas (Event, Command, Query, Response)
- ✅ Correlation IDs para rastreamento
- ✅ Timeout configurável

**Fluxo**:
```
Service A → Publish Event → Event Bus → Subscribe Handler → Service B
```

### 2. Service Registry

**Localização**: `enterprise/core/service_registry.py`

**Responsabilidades**:
- Registro de serviços
- Descoberta de serviços (service discovery)
- Health checks automáticos
- Gerenciamento de heartbeats

**Estados de Serviço**:
- `HEALTHY`: Serviço funcionando normalmente
- `DEGRADED`: Serviço com problemas leves
- `UNHEALTHY`: Serviço falhando
- `UNKNOWN`: Status desconhecido

**Lifecycle**:
```
Register → Heartbeat → Health Check → Unregister
```

### 3. Distributed Orchestrator

**Localização**: `enterprise/core/distributed_orchestrator.py`

**Responsabilidades**:
- Orquestração de comandos distribuídos
- Implementação de Saga Pattern
- Compensação automática (rollback)
- Gerenciamento de transações complexas

**Saga Pattern**:
```
Command → Step 1 → Step 2 → Step 3 → Success
          ↓ (se falhar)
          Compensate Step 1
```

**Tipos de Comandos**:
- `open_app`: Abertura de aplicativos
- `complex_workflow`: Workflows multi-serviço
- Custom commands através de extensão

### 4. Enterprise AI Engine

**Localização**: `enterprise/services/ai_engine.py`

**Responsabilidades**:
- Gerenciamento de múltiplos modelos de IA
- Otimização de inferência
- Ensemble de modelos
- Performance tracking

**Componentes**:
- **Model Registry**: Catálogo de modelos disponíveis
- **Inference Optimizer**: Otimização de prompts e contexto
- **Model Ensembler**: Combinação de resultados de múltiplos modelos

**Estratégias de Ensemble**:
- `confidence_weighted`: Média ponderada por confiança
- `majority_vote`: Voto majoritário

### 5. API Gateway

**Localização**: `enterprise/gateway/api_gateway.py`

**Responsabilidades**:
- Ponto de entrada único para clientes
- Roteamento de requisições
- Rate limiting
- Service discovery integration
- Load balancing (futuro)

**Features**:
- ✅ Proxy genérico para serviços
- ✅ Endpoints específicos otimizados
- ✅ Health checks agregados
- ✅ Rate limiting básico

## Arquitetura de Comunicação

```
┌─────────────────────────────────────────────────────────┐
│                    Cliente                               │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP/REST
                     ↓
┌─────────────────────────────────────────────────────────┐
│              API Gateway (Port 8080)                   │
│  - Rate Limiting                                        │
│  - Service Discovery                                    │
│  - Request Routing                                      │
└────────────────────┬────────────────────────────────────┘
                     │
                     ↓
        ┌────────────────────────┐
        │   Service Registry     │
        │   (Descoberta)         │
        └────────┬───────────────┘
                 │
        ┌────────┴───────────────┐
        │                         │
        ↓                         ↓
┌───────────────┐         ┌───────────────┐
│ Event Bus     │         │   Redis       │
│ (Pub-Sub)     │◄────────┤  (Messages)   │
└───────┬───────┘         └───────────────┘
        │
        ├─────────────────┬──────────────────┐
        ↓                 ↓                  ↓
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ Orchestrator │  │  AI Engine   │  │  Automation  │
│   (8001)     │  │   (8002)     │  │   (8003)     │
└──────────────┘  └──────────────┘  └──────────────┘
```

## Padrões Arquiteturais Implementados

### 1. Saga Pattern
Para transações distribuídas que envolvem múltiplos serviços.

**Exemplo**:
```python
# Saga para workflow complexo
steps = [
    SagaStep("step1", "data-pipeline", "/process", {...}),
    SagaStep("step2", "ai-engine", "/analyze", {...}),
    SagaStep("step3", "automation", "/execute", {...})
]

# Execução com compensação automática em caso de falha
saga = CommandSaga(command, steps, event_bus, registry)
result = await saga.execute()
```

### 2. Event-Driven Architecture
Comunicação assíncrona baseada em eventos.

**Vantagens**:
- Desacoplamento de serviços
- Escalabilidade horizontal
- Resiliência a falhas
- Fácil adição de novos serviços

### 3. Service Discovery
Registro automático e descoberta de serviços.

**Processo**:
1. Serviço inicia e se registra
2. Envia heartbeats periódicos
3. Registry monitora saúde
4. Outros serviços descobrem via registry

### 4. API Gateway Pattern
Ponto único de entrada para todos os serviços.

**Benefícios**:
- Centralização de autenticação
- Rate limiting
- Logging e monitoramento
- Versionamento de APIs

## Deployment

### Docker Compose

Todos os serviços são orquestrados via Docker Compose:

```bash
docker-compose -f enterprise/docker-compose.enterprise.yml up -d
```

### Serviços Incluídos

1. **Redis**: Event Bus distribuído
2. **Ollama**: Servidor de modelos LLM
3. **Gateway**: API Gateway
4. **Core Orchestrator**: Orquestração distribuída
5. **AI Engine**: Motor de IA
6. **Automation Engine**: Automação
7. **Memory Manager**: Gerenciamento de memória
8. **Monitoring Dashboard**: Dashboard de monitoramento

## Próximas Implementações

### Fase 1: Serviços Restantes
- [ ] Voice Processor Service
- [ ] Security Layer Service
- [ ] Data Pipeline Service
- [ ] Skill Registry Service

### Fase 2: Recursos Avançados
- [ ] Authentication/Authorization (OAuth2/JWT)
- [ ] Distributed Tracing (OpenTelemetry)
- [ ] Metrics Collection (Prometheus)
- [ ] Logging Centralizado (ELK Stack)
- [ ] Service Mesh (Istio/Linkerd)

### Fase 3: Alta Disponibilidade
- [ ] Auto-scaling (Kubernetes)
- [ ] Load Balancing avançado
- [ ] Circuit Breakers por serviço
- [ ] Health Checks avançados
- [ ] Disaster Recovery

### Fase 4: Observabilidade
- [ ] Dashboard de métricas em tempo real
- [ ] Alertas configuráveis
- [ ] Análise de performance
- [ ] Capacity Planning
- [ ] Predictive Analytics

## Exemplos de Uso

### Enviar Comando Distribuído

```python
from enterprise.core.distributed_orchestrator import Command, DistributedOrchestrator

command = Command(
    id="cmd-001",
    type="complex_workflow",
    payload={"data": "..."},
    source="user"
)

orchestrator = DistributedOrchestrator(event_bus, service_registry)
result = await orchestrator.process_command(command)
```

### Publicar Evento

```python
from enterprise.core.event_bus import Event, EventType

event = Event(
    id="evt-001",
    type=EventType.EVENT,
    source="service-a",
    destination=None,
    payload={"action": "completed"},
    timestamp=datetime.now()
)

await event_bus.publish(event, channel="events")
```

### Registrar Serviço

```python
from enterprise.core.service_registry import ServiceRegistry

registry = ServiceRegistry()

registry.register(
    name="my-service",
    version="1.0.0",
    host="my-service",
    port=8080,
    endpoints=["/api/endpoint1", "/api/endpoint2"]
)

# Enviar heartbeats periódicos
while True:
    registry.heartbeat("my-service")
    await asyncio.sleep(30)
```

## Métricas e Monitoramento

### Métricas Coletadas

- **Latência de requisições**: Por serviço e endpoint
- **Taxa de erros**: Erros por serviço
- **Throughput**: Requisições por segundo
- **Disponibilidade**: Uptime por serviço
- **Health status**: Status de cada serviço

### Endpoints de Monitoramento

- `GET /health`: Health check agregado
- `GET /api/services`: Lista de serviços e status
- `GET /metrics`: Métricas coletadas (futuro)

## Segurança

### Implementado
- ✅ Rate limiting básico
- ✅ Service isolation
- ✅ Health checks

### Planejado
- [ ] Authentication (OAuth2)
- [ ] Authorization (RBAC)
- [ ] TLS/SSL encryption
- [ ] API keys management
- [ ] Audit logging

## Escalabilidade

### Horizontal Scaling

Todos os serviços são stateless e podem ser escalados horizontalmente:

```bash
docker-compose -f enterprise/docker-compose.enterprise.yml up -d --scale ai-engine=3
```

### Auto-scaling (Futuro)

Com Kubernetes:
- Pod autoscaling baseado em CPU/Memory
- HPA (Horizontal Pod Autoscaler)
- Predictive scaling

## Resiliência

### Implementado
- ✅ Circuit Breakers (nos módulos base)
- ✅ Retry com backoff
- ✅ Saga compensation
- ✅ Health checks

### Planejado
- [ ] Circuit breakers por serviço
- [ ] Bulkhead pattern
- [ ] Timeout handling avançado
- [ ] Fallback strategies

