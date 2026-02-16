# JARVIS 5.0 - Evolution Layer Documentation

## 📚 Visão Geral

A **Evolution Layer** (Camada de Evolução) é o sistema de auto-organização, auto-correção e auto-desenvolvimento do JARVIS 5.0. Implementa uma arquitetura autopoiética que permite ao sistema:

- **Auto-observar**: Monitorar continuamente seu próprio estado
- **Auto-diagnosticar**: Identificar e analisar problemas automaticamente
- **Auto-corrigir**: Aplicar correções de forma segura com rollback automático
- **Auto-aprender**: Melhorar com base em experiências passadas

## 🏗️ Arquitetura

### Componentes Principais

```
┌─────────────────────────────────────────────────────────┐
│             Evolution Manager                            │
│  (Coordenador Central)                                   │
└─────────────────────────────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        ▼                 ▼                 ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ Self Observer│  │  Auto Healer │  │Safe Executor │
│  (Sensores)  │  │ (Diagnóstico)│  │  (Correção)  │
└──────────────┘  └──────────────┘  └──────────────┘
        │                 │                 │
        └─────────────────┼─────────────────┘
                          ▼
                  ┌──────────────┐
                  │Knowledge DB  │
                  │(Aprendizado) │
                  └──────────────┘
```

### 1. Self Observer (Auto-Observação)

**Arquivo**: `src/evolution/self_observer.py`

Monitora continuamente o estado do sistema:

- **Métricas de Hardware**: CPU, RAM, GPU (temperatura, utilização)
- **Análise de Código**: Complexidade, imports locais, bare excepts
- **Health Checks**: Verifica subsistemas (Ollama, camera, internet)
- **Integridade de Configuração**: Valida arquivos de configuração

**Exemplo de Relatório**:
```json
{
  "timestamp": "2026-02-16T00:30:00Z",
  "metrics": {
    "cpu_percent": 45.2,
    "memory_percent": 62.1,
    "gpu_temp": 65,
    "gpu_util": 30
  },
  "code_health": {
    "scanned_files": 142,
    "large_files": ["src/core/intelligence/ai_agent.py"],
    "bare_excepts": [{"file": "src/utils/helpers.py", "line": 150}]
  },
  "operational_health": {
    "ollama": true,
    "camera": false,
    "internet": true
  }
}
```

### 2. Auto Healer (Auto-Diagnóstico)

**Arquivo**: `src/evolution/auto_healer.py`

Analisa os relatórios e gera planos de correção:

- **Identifica Problemas**: Extrai issues acionáveis do relatório
- **Consulta Base de Conhecimento**: Verifica soluções anteriores
- **Consulta LLM**: Usa Ollama para gerar novas soluções
- **Prioriza Ações**: Ordena correções por impacto e risco

**Exemplo de Plano de Correção**:
```json
{
  "tipo": "codigo",
  "descricao": "Substituir bare except por tratamento específico",
  "arquivo": "src/utils/helpers.py",
  "linha_inicio": 150,
  "codigo_corrigido": "except Exception as e:\n    logger.error(f'Error: {e}')",
  "problem_hash": "abc123..."
}
```

### 3. Safe Executor (Auto-Correção)

**Arquivo**: `src/evolution/safe_executor.py`

Executa correções de forma segura:

- **Backup Automático**: Cria backup antes de qualquer alteração
- **Validação**: Testa sintaxe e imports após modificação
- **Rollback**: Restaura versão anterior se falhar
- **Registro**: Salva resultados na base de conhecimento

**Fluxo de Execução**:
1. Verifica se arquivo existe
2. Cria backup com timestamp
3. Aplica modificação
4. Valida com `py_compile` e testes
5. Se sucesso: mantém alteração
6. Se falha: restaura backup

### 4. Knowledge Database (Base de Conhecimento)

**Arquivo**: `src/evolution/knowledge_db.py`

Armazena problemas e soluções para aprendizado contínuo:

**Schema do Banco**:
```sql
-- Problemas identificados
CREATE TABLE problems (
    id INTEGER PRIMARY KEY,
    hash TEXT UNIQUE,
    module TEXT,
    description TEXT,
    severity TEXT,
    occurrences INTEGER,
    first_seen TIMESTAMP,
    last_seen TIMESTAMP
);

-- Soluções aplicadas
CREATE TABLE solutions (
    id INTEGER PRIMARY KEY,
    problem_hash TEXT,
    action_type TEXT,
    description TEXT,
    success BOOLEAN,
    impact_score REAL,
    execution_time_ms INTEGER,
    applied_at TIMESTAMP
);

-- Feedback humano
CREATE TABLE human_feedback (
    id INTEGER PRIMARY KEY,
    solution_id INTEGER,
    feedback TEXT,  -- 'positive', 'negative', 'ignore'
    comment TEXT
);
```

### 5. Evolution Manager (Gerenciador)

**Arquivo**: `src/evolution/evolution_manager.py`

Coordena todos os componentes:

- Inicialização ordenada dos módulos
- Controle de ciclo de vida
- Gatilhos de manutenção
- Interface de status

## 🚀 Uso

### Instalação de Dependências

```bash
pip install psutil aiofiles requests
# Opcional para GPU NVIDIA:
pip install pynvml
```

### Inicialização Básica

```python
from src.evolution import evolution_manager

async def main():
    # Iniciar o sistema de evolução
    await evolution_manager.start(
        observer_interval=300,  # 5 minutos entre observações
        auto_heal=True,         # Habilitar correção automática
        initial_scan=True       # Executar scan inicial
    )
    
    # Seu código principal aqui
    try:
        while True:
            await asyncio.sleep(1)
    finally:
        # Desligar ordenadamente
        await evolution_manager.stop()
```

### Gatilhos Manuais

```python
# Trigger manual de manutenção
await evolution_manager.trigger_maintenance()

# Desabilitar auto-correção temporariamente
evolution_manager.disable_auto_heal()

# Reabilitar
evolution_manager.enable_auto_heal()

# Obter status
status = evolution_manager.get_status()
print(status)
```

### Verificar Estatísticas

```python
from src.evolution import knowledge_db

# Obter estatísticas da base de conhecimento
stats = knowledge_db.get_statistics()
print(f"Total de problemas: {stats['total_problems']}")
print(f"Taxa de sucesso: {stats['success_rate']}%")

# Buscar soluções para um problema específico
solutions = knowledge_db.get_successful_solutions("problem_hash_123")
```

## 📡 Integração com Event Bus

O sistema publica e assina eventos via Event Bus:

### Eventos Publicados

```python
# Relatório de observação (a cada ciclo)
EventType.SYSTEM_OBSERVER_REPORT
# Data: relatório completo do sistema

# Plano de diagnóstico gerado
EventType.SYSTEM_DIAGNOSTIC_PLAN
# Data: {"plan": [ações corretivas]}

# Correção bem-sucedida
EventType.SYSTEM_CORRECTION_SUCCEEDED
# Data: {"action": detalhes da ação}

# Correção falhou
EventType.SYSTEM_CORRECTION_FAILED
# Data: {"action": detalhes da ação}
```

### Assinando Eventos

```python
from src.core.infrastructure.async_event_bus import event_bus, EventType

def on_correction(event):
    print(f"Correção aplicada: {event.data}")

# Assinar eventos de correção
event_bus.subscribe(
    EventType.SYSTEM_CORRECTION_SUCCEEDED,
    on_correction
)
```

## 🔒 Segurança

### Limites e Proteções

1. **Arquivos Protegidos**: Núcleo do sistema não é modificado automaticamente
2. **Backups Automáticos**: Todo arquivo modificado tem backup em `data/backups/auto/`
3. **Validação Obrigatória**: Syntax check antes de aceitar mudanças
4. **Rollback Automático**: Restauração em caso de falha
5. **Limite de Tentativas**: Máximo de 3 tentativas por problema

### Arquivos Protegidos

Por padrão, os seguintes diretórios são protegidos:
- `src/core/infrastructure/`
- `src/core/config/system_manifest.py`
- `src/evolution/` (o próprio sistema de evolução)

### Sandbox

Todas as execuções de código gerado ocorrem em ambiente isolado antes de serem aplicadas ao sistema real.

## 🧪 Testes

### Executar Testes

```bash
# Todos os testes da Evolution Layer
pytest tests/unit/test_evolution_layer.py -v

# Apenas tests do Knowledge Database
pytest tests/unit/test_evolution_layer.py::TestKnowledgeDatabase -v

# Apenas tests do Self Observer
pytest tests/unit/test_evolution_layer.py::TestSelfObserver -v
```

### Demo Interativo

```bash
# Executar demonstração completa
python demo_evolution.py
```

A demo mostra:
- Inicialização dos componentes
- Scan inicial do sistema
- Status dos componentes
- Estatísticas da base de conhecimento
- Controle de auto-healing
- Shutdown ordenado

## 📊 Métricas e Monitoramento

### Métricas Coletadas

**Hardware**:
- CPU: Percentual de uso, frequência
- Memória: Total, usado, percentual
- GPU: Temperatura, utilização, memória (NVIDIA)
- Disco: Espaço usado, percentual
- Rede: Bytes enviados/recebidos

**Código**:
- Arquivos grandes (>500 linhas)
- Funções grandes (>50 linhas)
- Imports locais (dentro de funções)
- Bare excepts (sem tratamento específico)
- Complexidade ciclomática

**Sistema**:
- Threads ativas
- Objetos no garbage collector
- Conexões abertas
- Arquivos abertos

## 🎯 Casos de Uso

### 1. Correção Automática de Bare Excepts

**Problema Detectado**:
```python
try:
    risky_operation()
except:
    pass  # Silent failure!
```

**Correção Aplicada**:
```python
try:
    risky_operation()
except Exception as e:
    logger.error(f"Error in risky_operation: {e}")
```

### 2. Detecção de Imports Locais

**Problema Detectado**:
```python
def process_image():
    from PIL import Image  # Import local
    # ...
```

**Ação Sugerida**: Mover import para o topo do arquivo

### 3. Configuração Ausente

**Problema Detectado**: `ai.provider` não configurado

**Correção Aplicada**: Define valor padrão ou solicita intervenção humana

## 🔄 Ciclo de Vida

### Gatilhos de Ativação

1. **Ao Iniciar**: Scan inicial para detectar problemas críticos
2. **Periódico**: A cada N segundos (configurável)
3. **Sob Demanda**: Via comando de voz ou API
4. **Após Erro**: Quando um módulo falha repetidamente

### Fases do Ciclo

```
1. OBSERVAÇÃO
   ↓
2. DIAGNÓSTICO
   ↓
3. CORREÇÃO
   ↓
4. VALIDAÇÃO
   ↓
5. APRENDIZADO
```

## 🛠️ Configuração Avançada

### Personalizar Intervalo de Observação

```python
# Observação mais frequente (1 minuto)
await evolution_manager.start(observer_interval=60)

# Observação menos frequente (10 minutos)
await evolution_manager.start(observer_interval=600)
```

### Modo Observação Apenas

```python
# Desabilitar auto-correção
await evolution_manager.start(auto_heal=False)

# Ou desabilitar depois de iniciar
evolution_manager.disable_auto_heal()
```

### Limpeza de Registros Antigos

```python
# Remover problemas não vistos há mais de 90 dias
knowledge_db.cleanup_old_records(days=90)
```

## 📈 Estatísticas e Análise

### Visualizar Estatísticas

```python
stats = knowledge_db.get_statistics()

print(f"""
Estatísticas da Base de Conhecimento:
- Total de problemas: {stats['total_problems']}
- Total de soluções: {stats['total_solutions']}
- Taxa de sucesso: {stats['success_rate']}%

Módulos mais afetados:
""")

for module in stats['top_affected_modules']:
    print(f"  - {module['module']}: {module['count']} problemas")
```

### Adicionar Feedback Humano

```python
# Adicionar feedback positivo
knowledge_db.add_human_feedback(
    solution_id=123,
    feedback="positive",
    comment="Resolveu o problema perfeitamente!"
)

# Adicionar feedback negativo
knowledge_db.add_human_feedback(
    solution_id=124,
    feedback="negative",
    comment="Causou novos erros"
)
```

## 🐛 Troubleshooting

### Problema: LLM não responde

**Causa**: Ollama não está rodando ou não está acessível

**Solução**:
```bash
# Verificar se Ollama está rodando
curl http://localhost:11434/api/tags

# Iniciar Ollama
ollama serve
```

### Problema: Database locked

**Causa**: Múltiplas instâncias tentando acessar o banco

**Solução**: Use apenas uma instância do Evolution Manager por processo

### Problema: Auto-correção não funciona

**Verificar**:
1. Auto-heal está habilitado? `evolution_manager.auto_heal_enabled`
2. Ollama está configurado? Check `system_manifest.ai.ollama_host`
3. Há problemas na fila? Verificar logs

## 🔮 Roadmap Futuro

- [ ] Integração com dashboard web para visualização em tempo real
- [ ] Suporte para geração de novos módulos (auto-desenvolvimento)
- [ ] Múltiplos modelos LLM para validação cruzada
- [ ] Métricas de performance e alertas proativos
- [ ] Exportação de relatórios em PDF/HTML
- [ ] API REST para controle externo
- [ ] Integração com sistemas de CI/CD

## 📚 Referências

- Documentação completa: `docs/evolution_layer.md`
- Testes: `tests/unit/test_evolution_layer.py`
- Demo: `demo_evolution.py`
- Código fonte: `src/evolution/`

## 🤝 Contribuindo

Para adicionar novos tipos de problemas ou correções:

1. Adicionar detecção em `self_observer.py`
2. Adicionar lógica de identificação em `auto_healer.py`
3. Adicionar handler de correção em `safe_executor.py`
4. Criar testes em `test_evolution_layer.py`

## 📄 Licença

Este componente faz parte do projeto JARVIS 5.0.
