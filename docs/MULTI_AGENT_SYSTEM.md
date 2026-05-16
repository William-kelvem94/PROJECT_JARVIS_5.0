# 🤖 JARVIS Multi-Agent Analysis System

Sistema avançado de análise multi-agente que monitora continuamente diferentes aspectos do JARVIS e propõe melhorias automaticamente.

## 📋 Visão Geral

O sistema Multi-Agent Analysis é composto por **14 agentes especializados (10 de análise + 4 auto-fix)** que trabalham de forma independente e contínua, cada um focado em um aspecto específico do sistema.

## 🎯 Agentes Disponíveis

### 1. PerformanceAgent 🚀
**Intervalo**: 60 segundos  
**Foco**: Desempenho do sistema

**Monitora**:
- Uso de CPU (threshold: 80%)
- Uso de RAM (threshold: 85%)
- Contagem de threads ativas (threshold: 150)

**Exemplo de Finding**:
```json
{
  "severity": "high",
  "title": "High CPU Usage Detected",
  "description": "CPU usage is at 92.5%, exceeding threshold of 80%",
  "recommendation": "Consider optimizing heavy computation tasks or distributing load. Check for infinite loops or blocking operations.",
  "metrics": {"cpu_percent": 92.5}
}
```

---

### 2. SystemHealthAgent 🏥
**Intervalo**: 300 segundos (5 minutos)  
**Foco**: Saúde geral do sistema

**Monitora**:
- Espaço em disco (alerta em 90%+)
- Status de serviços críticos
- Perception Manager ativo
- Integridade de componentes core

**Exemplo de Finding**:
```json
{
  "severity": "critical",
  "title": "Low Disk Space",
  "description": "Disk usage is at 95.2%",
  "recommendation": "Clean up temporary files, logs, or consider expanding storage.",
  "metrics": {"disk_percent": 95.2, "disk_free_gb": 12.5}
}
```

---

### 3. SecurityAgent 🔒
**Intervalo**: 600 segundos (10 minutos)  
**Foco**: Segurança e configurações sensíveis

**Monitora**:
- Privilégios de execução
- Configurações inseguras
- Exposição de credenciais
- Compliance com best practices

**Exemplo de Finding**:
```json
{
  "severity": "low",
  "title": "Running as Administrator",
  "description": "JARVIS is running with administrator privileges",
  "recommendation": "Consider running with standard user privileges unless admin access is required."
}
```

---

### 4. CodeQualityAgent 📝
**Intervalo**: 3600 segundos (1 hora)  
**Foco**: Qualidade do código

**Monitora**:
- Padrões deprecados
- Code smells
- Conformidade com PEP 8
- Imports não utilizados

**Capacidade de Extensão**: Pode ser integrado com ferramentas como pylint, flake8, mypy.

---

### 5. UserExperienceAgent 👤
**Intervalo**: 900 segundos (15 minutos)  
**Foco**: Experiência do usuário

**Monitora**:
- Tempos de resposta (threshold: 2s)
- Latência de interações
- Feedback do usuário
- Patterns de uso

**Exemplo de Finding**:
```json
{
  "severity": "medium",
  "title": "Slow Response Times",
  "description": "Average response time is 2.8s, exceeding threshold of 2.0s",
  "recommendation": "Optimize processing pipeline, consider caching, or use faster models.",
  "metrics": {"avg_response_time": 2.8, "sample_count": 47}
}
```

---

## 🔌 Integração com JARVIS

### Inicialização Automática

O sistema é iniciado automaticamente no `lifespan` do FastAPI:

```python
# backend/app/main.py
from .multi_agent_analysis import start_multi_agent_analysis

@asynccontextmanager
async def lifespan(app: FastAPI):
    # ... outras inicializações
    
    # Start Multi-Agent Analysis
    start_multi_agent_analysis()
    
    yield
    
    # Cleanup
    stop_multi_agent_analysis()
```

### Endpoints da API

#### 1. Sumário Geral
```bash
GET /agents/summary

# Resposta
{
  "total_findings": 23,
  "by_severity": {
    "critical": 2,
    "high": 5,
    "medium": 10,
    "low": 4,
    "info": 2
  },
  "by_agent": {
    "PerformanceAgent": 8,
    "SystemHealthAgent": 5,
    "SecurityAgent": 3,
    "CodeQualityAgent": 4,
    "UXAgent": 3
  }
}
```

#### 2. Todos os Findings
```bash
GET /agents/findings?severity=high

# Resposta
{
  "findings": [...],
  "total": 5
}
```

#### 3. Apenas Críticos
```bash
GET /agents/critical

# Resposta
{
  "critical_findings": [...],
  "count": 7
}
```

---

## 💻 Uso Programático

### Obter Orchestrator
```python
from app.multi_agent_analysis import get_orchestrator

orchestrator = get_orchestrator()
```

### Obter Findings de um Agente Específico
```python
from app.multi_agent_analysis import get_orchestrator, AgentType

orchestrator = get_orchestrator()
perf_agent = orchestrator.agents[AgentType.PERFORMANCE]
findings = perf_agent.get_findings()
```

### Registrar Novo Agente
```python
from app.multi_agent_analysis import BaseAgent, AgentType, Finding, Severity

class CustomAgent(BaseAgent):
    def __init__(self):
        super().__init__(AgentType.SYSTEM_HEALTH, "MyCustomAgent", check_interval=120)
    
    async def analyze(self):
        findings = []
        # ... sua lógica de análise
        return findings

# Registrar
orchestrator = get_orchestrator()
orchestrator.register_agent(CustomAgent())
```

---

## 📊 Severidades

O sistema usa 5 níveis de severidade:

| Severidade | Uso | Cor Sugerida | Ação |
|-----------|-----|--------------|------|
| **CRITICAL** | Falhas sistêmicas, risco de crash | 🔴 Red | Ação imediata |
| **HIGH** | Problemas sérios que afetam funcionamento | 🟠 Orange | Ação urgente |
| **MEDIUM** | Degradação de performance ou experiência | 🟡 Yellow | Resolver em breve |
| **LOW** | Pequenos problemas ou melhorias | 🔵 Blue | Backlog |
| **INFO** | Informações, sem problema real | ⚪ Gray | Apenas info |

---

## 🎨 Integração com Frontend

### React/Next.js Component Example

```typescript
// components/AgentFindings.tsx
import { useState, useEffect } from 'react';

interface Finding {
  agent_type: string;
  severity: string;
  title: string;
  description: string;
  recommendation: string;
  timestamp: string;
  metrics?: Record<string, any>;
}

export function AgentFindings() {
  const [findings, setFindings] = useState<Finding[]>([]);
  const [summary, setSummary] = useState<any>(null);

  useEffect(() => {
    // Poll every 30 seconds
    const interval = setInterval(async () => {
      const summaryRes = await fetch('/agents/summary');
      const summaryData = await summaryRes.json();
      setSummary(summaryData);

      const findingsRes = await fetch('/agents/findings?severity=high');
      const findingsData = await findingsRes.json();
      setFindings(findingsData.findings);
    }, 30000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div>
      <h2>System Analysis</h2>
      {summary && (
        <div className="summary">
          <span>Total: {summary.total_findings}</span>
          <span className="critical">Critical: {summary.by_severity.critical}</span>
          <span className="high">High: {summary.by_severity.high}</span>
        </div>
      )}
      
      <div className="findings">
        {findings.map((f, i) => (
          <div key={i} className={`finding ${f.severity}`}>
            <h3>{f.title}</h3>
            <p>{f.description}</p>
            <p className="recommendation">💡 {f.recommendation}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
```

---

## 🔧 Configuração

### Ajustar Intervalos

```python
# Editar backend/app/multi_agent_analysis.py

class PerformanceAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            AgentType.PERFORMANCE, 
            "PerformanceAgent", 
            check_interval=30  # ← Altere aqui (em segundos)
        )
```

### Ajustar Thresholds

```python
class PerformanceAgent(BaseAgent):
    def __init__(self):
        super().__init__(...)
        self.cpu_threshold = 70.0  # ← CPU %
        self.ram_threshold = 80.0  # ← RAM %
        self.thread_threshold = 200  # ← Thread count
```

---

## 📈 Métricas e Logging

### Estrutura de Log

```
2026-05-07 10:30:15 | INFO | [MultiAgent] Orchestrator initialized
2026-05-07 10:30:15 | INFO | [MultiAgent] Registered agent: PerformanceAgent
2026-05-07 10:30:16 | INFO | [PerformanceAgent] Starting analysis loop
2026-05-07 10:31:20 | WARNING | [PerformanceAgent] HIGH: High CPU Usage Detected
2026-05-07 10:32:45 | ERROR | [SystemHealthAgent] CRITICAL: Low Disk Space
```

### Métricas Incluídas nos Findings

Cada finding pode incluir métricas específicas:
- CPU/RAM percentages
- Response times
- Disk space disponível
- Thread counts
- Custom metrics

---

## 🚀 Roadmap

### Planejado
- [ ] Auto-fix para problemas comuns
- [ ] Machine Learning para prever problemas
- [ ] Integração com Grafana/Prometheus
- [ ] Histórico temporal de findings
- [ ] Alertas via email/webhook
- [ ] Dashboard web dedicado

### Possíveis Novos Agentes
- **DatabaseAgent**: Monitor queries, connections, locks
- **NetworkAgent**: Monitor latência, bandwidth, conexões
- **ModelAgent**: Monitor accuracy, inference time dos modelos de IA
- **ResourceAgent**: Monitor GPU, VRAM, disk I/O

---

## 🤝 Contribuindo

Para adicionar um novo agente:

1. Crie uma classe que herda de `BaseAgent`
2. Implemente o método `analyze()`
3. Registre no `get_orchestrator()`

```python
class MyAgent(BaseAgent):
    def __init__(self):
        super().__init__(AgentType.SYSTEM_HEALTH, "MyAgent", check_interval=300)
    
    async def analyze(self) -> List[Finding]:
        findings = []
        
        # Sua lógica aqui
        if problema_detectado:
            findings.append(Finding(
                agent_type=self.agent_type,
                severity=Severity.HIGH,
                title="Título do Problema",
                description="Descrição detalhada",
                recommendation="O que fazer"
            ))
        
        return findings

# Registrar em get_orchestrator()
_orchestrator.register_agent(MyAgent())
```

---

## 📚 Referências

- [FastAPI Lifespan Events](https://fastapi.tiangolo.com/advanced/events/)
- [Async Programming in Python](https://docs.python.org/3/library/asyncio.html)
- [Monitoring Best Practices](https://sre.google/sre-book/monitoring-distributed-systems/)

---

**Versão**: 1.0.0  
**Autor**: GitHub Copilot  
**Data**: 7 de maio de 2026
