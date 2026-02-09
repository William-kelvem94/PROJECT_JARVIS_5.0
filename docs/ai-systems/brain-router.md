# 🧠 JARVIS 5.0 - Brain Router

**Sistema de Roteamento Inteligente de Modelos de IA**

---

## 📖 Visão Geral

O **Brain Router** é o sistema que decide **qual modelo de IA usar** para cada tarefa, otimizando:
- ⚡ **Performance** (velocidade vs qualidade)
- 💰 **Custo** (modelos gratuitos vs pagos)
- 🔒 **Privacidade** (local vs nuvem)
- 🎯 **Especialização** (escolhe melhor modelo por tipo de tarefa)

---

## 🏗️ Arquitetura

```
User Input
    ↓
Brain Router (Analisador)
    ↓
┌────────┬────────┬────────┬────────┐
│ Gemini │OpenAI  │Ollama  │ Local  │
│ Cloud  │ Cloud  │ Local  │Brain   │
└────────┴────────┴────────┴────────┘
    ↓
Response to User
```

---

## 🎯 Estratégias de Roteamento

### 1. **Auto (Padrão)**

Brain Router analisa a query e decide automaticamente.

**Regras:**
- Queries simples → Ollama local (rápido)
- Queries complexas → Gemini Flash (balanceado)
- Visão/Imagens → Gemini Vision
- Código/Programação → OpenAI GPT-4
- Raciocínio lógico → Gemini Thinking
- Privacidade crítica → Local Brain

**Configuração:**
```yaml
# config/ai_config.yaml
brain_router:
  mode: "auto"
  strategy: "balanced"  # speed, balanced, quality
```

---

### 2. **Priority List (Lista de Prioridade)**

Tenta modelos em ordem até obter sucesso.

**Configuração:**
```yaml
brain_router:
  mode: "priority"
  priority_list:
    - "ollama-local"
    - "gemini-flash"
    - "local-brain"
```

**Fluxo:**
1. Tenta Ollama primeiro
2. Se falhar/estiver offline → Gemini
3. Se falhar → Local Brain (sempre disponível)

---

### 3. **Task-Based (Por Tipo de Tarefa)**

Roteamento baseado no **tipo** de tarefa.

**Configuração:**
```yaml
brain_router:
  mode: "task-based"
  task_routing:
    conversation: "ollama-llama3"
    coding: "openai-gpt4"
    vision: "gemini-vision"
    reasoning: "gemini-thinking"
    creative: "openai-gpt4"
    translation: "ollama-local"
```

**Como Funciona:**
```python
# Brain Router classifica automaticamente
user: "Traduza 'hello' para português"
→ task: "translation"
→ model: "ollama-local"

user: "Escreva um script Python para backup"
→ task: "coding"
→ model: "openai-gpt4"
```

---

### 4. **Load Balancing (Balanceamento de Carga)**

Distribui requisições entre múltiplos modelos para evitar rate limits.

**Configuração:**
```yaml
brain_router:
  mode: "load-balancing"
  models:
    - name: "gemini-flash"
      weight: 60  # 60% das requests
      max_rpm: 60  # rate limit
    
    - name: "ollama-local"
      weight: 30  # 30% das requests
      max_rpm: 1000
    
    - name: "local-brain"
      weight: 10  # 10% (fallback)
      max_rpm: 9999
```

---

## 🤖 Modelos Disponíveis

### Nuvem (Cloud)

| Provider | Model | Custo | Velocidade | Qualidade | Uso |
|----------|-------|-------|------------|-----------|-----|
| **Gemini** | `gemini-2.0-flash-exp` | Grátis* | ⚡⚡⚡ Rápido | ⭐⭐⭐⭐ Alta | Uso geral |
| **Gemini** | `gemini-2.0-flash-thinking-exp` | Grátis* | ⚡⚡ Médio | ⭐⭐⭐⭐⭐ Máxima | Raciocínio complexo |
| **Gemini** | `gemini-1.5-pro` | Pago | ⚡⚡ Médio | ⭐⭐⭐⭐⭐ Máxima | Produção |
| **OpenAI** | `gpt-4` | Pago | ⚡ Lento | ⭐⭐⭐⭐⭐ Máxima | Código/Criatividade |
| **OpenAI** | `gpt-3.5-turbo` | Barato | ⚡⚡⚡ Rápido | ⭐⭐⭐ Boa | Conversação |

\*Grátis com limites de rate (15 RPM, 1M TPM)

### Local

| Model | Custo | Velocidade | Qualidade | Hardware |
|-------|-------|------------|-----------|----------|
| **Ollama Llama 3.1** | Grátis | ⚡⚡ Médio | ⭐⭐⭐ Boa | 8GB RAM |
| **Ollama Mistral** | Grátis | ⚡⚡⚡ Rápido | ⭐⭐⭐ Boa | 4GB RAM |
| **Ollama Phi-3** | Grátis | ⚡⚡⚡⚡ Muito Rápido | ⭐⭐ Aceitável | 2GB RAM |
| **Local Brain (LoRA)** | Grátis | ⚡⚡⚡ Rápido | ⭐⭐ Especifico | Variável |

---

## 📊 Análise de Queries

Brain Router analisa:

### 1. **Complexidade**

```python
# Simples (→ Ollama)
"Que horas são?"
"Bom dia"

# Média (→ Gemini Flash)
"Explique como funciona aprendizado de máquina"

# Complexa (→ Gemini Thinking)
"Debata os prós e contras de AGI do ponto de vista ético, técnico e social"
```

### 2. **Tipo de Conteúdo**

```python
# Texto puro (→ Ollama)
"Traduza isso para inglês"

# Visão (→ Gemini Vision)
"O que você vê na tela?"

# Código (→ OpenAI)
"Escreva um algoritmo de busca binária em Python"
```

### 3. **Tamanho do Contexto**

```python
# Contexto pequeno (→ Ollama)
Prompt: 100 tokens

# Contexto médio (→ Gemini Flash)
Prompt: 500-2000 tokens

# Contexto grande (→ Gemini Pro)
Prompt: 5000+ tokens
```

### 4. **Privacidade**

```python
# Dados sensíveis (→ Local Brain)
"Analise meu banco de dados de senhas"

# Dados públicos (→ Cloud)
"Pesquise sobre Python"
```

---

## ⚙️ Configuração Avançada

### Arquivo: `config/ai_config.yaml`

```yaml
brain_router:
  # Modo de operação
  mode: "auto"  # auto, priority, task-based, load-balancing
  
  # Estratégia de seleção
  strategy: "balanced"  # speed, balanced, quality, cost-optimal
  
  # Fallback padrão
  fallback_model: "local-brain"
  
  # Retry configuration
  max_retries: 3
  retry_delay: 2.0  # segundos
  
  # Rate limiting awareness
  respect_rate_limits: true
  
  # Privacy mode
  privacy_mode: false  # Se true, força modelos locais
  
  # Classificação de tarefas
  task_classification:
    enabled: true
    use_keywords: true
    use_ml_classifier: false  # Experimental
  
  # Load balancing
  load_balancing:
    enabled: false
    algorithm: "weighted-round-robin"
    consider_response_time: true
  
  # Logging
  log_routing_decisions: true
  log_model_performance: true
```

---

## 🎛️ Controle via Dashboard

### Control Dashboard → Brain Tab

**Seções:**

#### 🧠 Active Model

```
Current: gemini-2.0-flash-exp
Status: 🟢 ONLINE
Last Response: 1.2s
Routing Mode: AUTO
```

#### 🔀 Quick Switch

Botões rápidos:
- **Gemini Flash** (rápido)
- **Gemini Thinking** (inteligente)
- **Ollama Local** (privado)
- **Local Brain** (offline)

#### 📊 Routing Stats

```
Total Requests: 342
├─ Gemini: 198 (58%)
├─ Ollama: 120 (35%)
└─ Local Brain: 24 (7%)

Avg Response Time:
├─ Gemini: 1.2s
├─ Ollama: 0.8s
└─ Local Brain: 0.3s
```

#### ⚙️ Router Settings

- Dropdown: Mode (Auto, Priority, Task-Based, etc.)
- Dropdown: Strategy (Speed, Balanced, Quality)
- Checkbox: Privacy Mode
- Checkbox: Respect Rate Limits

---

## 🧪 Exemplos Práticos

### Exemplo 1: Otimização de Custo

```yaml
brain_router:
  mode: "priority"
  strategy: "cost-optimal"
  priority_list:
    - "ollama-local"  # Grátis, sempre primeiro
    - "gemini-flash"  # Grátis com limites
    - "gpt-3.5-turbo"  # Barato
    - "local-brain"  # Fallback grátis
```

### Exemplo 2: Máxima Qualidade

```yaml
brain_router:
  mode: "priority"
  strategy: "quality"
  priority_list:
    - "gemini-thinking"
    - "gpt-4"
    - "gemini-pro"
```

### Exemplo 3: Privacidade Total

```yaml
brain_router:
  mode: "auto"
  privacy_mode: true
  # Irá usar APENAS modelos locais
  allowed_models:
    - "ollama-local"
    - "local-brain"
```

### Exemplo 4: Especialização por Task

```yaml
brain_router:
  mode: "task-based"
  task_routing:
    # Conversação casual → Local (rápido + grátis)
    conversation: "ollama-llama3"
    
    # Código → OpenAI (melhor para código)
    coding: "openai-gpt4"
    
    # Visão → Gemini (único com visão grátis)
    vision: "gemini-vision"
    
    # Raciocínio → Gemini Thinking (melhor lógica)
    reasoning: "gemini-thinking"
    
    # Criativo → GPT-4 (mais criativo)
    creative: "openai-gpt4"
    
    # Tradução → Local (simples, não precisa cloud)
    translation: "ollama-local"
    
    # Fallback → Local Brain
    default: "local-brain"
```

---

## 📈 Métricas e Monitoramento

### Logs Automáticos

Cada decisão de roteamento é logada:

```
[2026-02-10 15:30:00] [BRAIN-ROUTER] Query: "Escreva código Python"
[2026-02-10 15:30:00] [BRAIN-ROUTER] Classification: task=coding, complexity=medium
[2026-02-10 15:30:00] [BRAIN-ROUTER] Selected: openai-gpt4 (reason: best-for-coding)
[2026-02-10 15:30:03] [BRAIN-ROUTER] Response time: 3.2s, tokens: 450
```

### Arquivo de Estatísticas

`data/monitoring/brain_router_stats.json`

```json
{
  "total_requests": 1234,
  "model_usage": {
    "gemini-flash": 650,
    "ollama-local": 400,
    "local-brain": 184
  },
  "avg_response_time": {
    "gemini-flash": 1.2,
    "ollama-local": 0.8,
    "local-brain": 0.3
  },
  "success_rate": {
    "gemini-flash": 0.98,
    "ollama-local": 0.95,
    "local-brain": 1.0
  },
  "cost_estimate": {
    "gemini": 0.0,
    "openai": 12.50,
    "local": 0.0
  }
}
```

---

## 🔧 Solução de Problemas

### "Sempre usa o mesmo modelo"

**Verificar:**
- Mode está em "auto"?
- Task classification está habilitado?
- Apenas 1 modelo configurado?

### "Falha ao rotear"

**Soluções:**
1. Verificar API keys configuradas
2. Testar cada modelo individualmente
3. Verificar logs: `data/logs/brain_router.log`
4. Fallback funcionando? (Local Brain sempre deve estar disponível)

### "Roteamento lento"

**Otimizações:**
1. Desabilitar ML classifier (use keywords apenas)
2. Reduzir retries: `max_retries: 1`
3. Usar mode "priority" ao invés de "auto"

---

## 🆘 Suporte

- **Aprendizado:** [learning-system.md](learning-system.md)
- **Ollama:** [ollama-integration.md](ollama-integration.md)
- **Arquitetura:** [../architecture/overview.md](../architecture/overview.md)

---

<div align="center">

**Um cérebro. Muitos modelos. Escolhas inteligentes. 🧠**

</div>
