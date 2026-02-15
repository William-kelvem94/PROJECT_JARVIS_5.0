# 🧬 JARVIS 5.0 - Local Brain

**IA Personalizada que Evolui com Você**

---

## 📖 O que é Local Brain?

O **Local Brain** é um modelo de IA **treinado especificamente para você**:
- 🧠 Aprende com suas interações
- 🔒 100% privado (nunca sai do seu PC)
- 🚀 Extremamente rápido (otimizado)
- 🎯 Especializado nas suas necessidades

**Diferença para outros modelos:**
- **Gemini/GPT:** Modelos gerais, não te conhecem
- **Ollama:** Modelos genéricos locais
- **Local Brain:** Treinado COM VOCÊ, PARA VOCÊ

---

## 🏗️ Arquitetura

### Base Model + LoRA Adapter

```
┌─────────────────────────┐
│  Base Model (Llama 3.1) │  ← Modelo pré-treinado
│      8B parameters      │
└────────────┬────────────┘
             │
             ↓
     ┌───────────────┐
     │  LoRA Adapter │  ← Personalização (seus dados)
     │  ~10M params  │
     └───────┬───────┘
             │
             ↓
     ┌───────────────┐
     │  Local Brain  │  ← Modelo final personalizado
     │  (Fine-tuned) │
     └───────────────┘
```

**LoRA (Low-Rank Adaptation):**
- Treina apenas 1% dos parâmetros
- Rápido e eficiente
- Preserva conhecimento geral

---

## 🚀 Inicialização

### Primeira Vez

Local Brain se auto-inicializa ao coletar 100+ feedbacks:

1. **Use JARVIS normalmente** (qualquer modelo)
2. **Dê feedback** no Dashboard (👍 👎)
3. **Aguarde 100 interações**
4. **Treinamento automático** (noite, 22h-6h)
5. **Local Brain READY!** ✅

### Status Atual

**Dashboard → Learning → Local Brain:**

```
Status: 🟡 TRAINING (47/100 feedbacks)
Estimated Ready: 2 days
Quality Score: N/A (not trained yet)
```

ou

```
Status: 🟢 ONLINE
Quality Score: 92.5%
Last Training: 2026-02-09 23:15
Total Interactions: 1,234
```

---

## 🎯 Como Funciona

### Fase 1: Coleta de Dados

JARVIS registra automaticamente:
- Suas perguntas
- Respostas dos modelos
- Seu feedback (👍 👎)
- Correções que você faz

**Armazenado em:** `data/learning/feedback_loop.db`

### Fase 2: Curadoria (Knowledge Distillation)

Sistema seleciona **Golden Commands**:
- Interações com 👍
- Respostas perfeitas
- Conhecimento único seu

**Armazenado em:** `data/learning/golden_commands.json`

### Fase 3: Treinamento (Dream Cycle)

**Quando:** 22h - 6h (CPU < 20%)

**Processo:**
1. Carrega base model (Llama 3.1)
2. Aplica LoRA training com seus dados
3. Valida qualidade
4. Salva checkpoint

**Tempo:** ~1-2 horas (primeira vez), ~20-30min (incrementais)

### Fase 4: Evolução Contínua

Após treinamento inicial, Local Brain continua evoluindo:
- A cada 100 novos feedbacks → re-training
- Ajusta-se às mudanças no seu comportamento
- Melhora continuamente

---

## 🧪 Usar Local Brain

### Método 1: Automático (Brain Router)

```yaml
# config/ai_config.yaml
brain_router:
  mode: "auto"
  task_routing:
    conversation: "local-brain"  # Conversação casual
    personal: "local-brain"      # Assuntos pessoais
```

### Método 2: Manual

**Dashboard → Brain → Select Model:**
- Dropdown: "Local Brain (Personalized)"
- Apply

### Método 3: Comando de Voz

```
"JARVIS, use cérebro local"
"JARVIS, modo personalizado"
```

---

## 📊 Monitoramento

### Métricas de Qualidade

**Dashboard → Learning → Local Brain Metrics:**

```
Quality Score: 92.5% ⭐⭐⭐⭐⭐

Breakdown:
├─ Response Accuracy: 95%
├─ Style Matching: 90%
├─ Context Awareness: 88%
└─ Speed: 0.3s avg

Training History:
├─ Epoch 1: Loss 0.045 (2026-02-01)
├─ Epoch 2: Loss 0.032 (2026-02-05)
└─ Epoch 3: Loss 0.023 (2026-02-09) ← Current
```

### Comparação com Modelos Cloud

**Teste Prático:**

| Pergunta | Gemini Response | Local Brain Response |
|----------|-----------------|----------------------|
| "Como está o projeto?" | "Qual projeto?" ❌ | "O JARVIS 5.0 está 85% completo, falta documentação final" ✅ |
| "Lembre meu compromisso" | "Não tenho acesso a calendário" ❌ | "Reunião amanhã às 14h30 com o cliente sobre IA" ✅ |

Local Brain **conhece seu contexto** porque foi treinado com ele!

---

## ⚙️ Configuração Avançada

### Arquivo: `config/ai_config.yaml`

```yaml
local_brain:
  # Base Model
  base_model: "llama3.1-8b"  # ou mistral-7b
  
  # LoRA Config
  lora:
    rank: 8  # Complexidade do adapter (4, 8, 16)
    alpha: 16
    dropout: 0.1
  
  # Training
  training:
    batch_size: 4
    learning_rate: 0.0001
    epochs: 3
    gradient_accumulation: 4
    
    # Hardware
    device: "cuda"  # ou "cpu"
    mixed_precision: true  # fp16 (economiza VRAM)
  
  # Quality thresholds
  min_quality_score: 80.0  # Mínimo aceitável
  retrain_threshold: 100  # Re-treina a cada N feedbacks
  
  # Deployment
  auto_deploy: true  # Deploy automático após treino
  keep_backups: 3  # Número de checkpoints antigos
```

---

## 🔧 Treinamento Manual

Se não quiser esperar Dream Cycle:

### Via Dashboard

1. Dashboard → **Learning** tab
2. Seção **Training Controls**
3. Clique **🚀 Start Training Now**
4. Aguarde conclusão (~30-60min)

### Via Terminal

```bash
python -m src.learning.continual_learner --train-now
```

### Via Script

```python
from src.learning.continual_learner import ContinualLearner

learner = ContinualLearner()
learner.train_model()
```

---

## 💾 Gestão de Modelos

### Localização

```
models/continual/
├── base_model/           # Llama 3.1 base
├── lora_adapters/        # Seus adapters personalizados
│   ├── checkpoint_001/
│   ├── checkpoint_002/
│   └── checkpoint_003/   # ← Mais recente
├── golden_commands.json  # Dataset curado
└── training_stats.json   # Histórico de treino
```

### Backup

**Automático:**
- JARVIS faz backup antes de cada training

**Manual:**
```bash
# Copiar checkpoint atual
cp -r models/continual/lora_adapters/checkpoint_003 C:\Backups\
```

### Rollback

Se novo modelo ficou pior:

```python
# Dashboard → Learning → Rollback to Previous
```

Ou manualmente renomeie:
```bash
cd models/continual/lora_adapters
mv checkpoint_003 checkpoint_003_bad
mv checkpoint_002 checkpoint_003
```

---

## 🎓 Ensinar Local Brain

### Método 1: Feedback Direto

Use normalmente, dê 👍 ou 👎:

```
Você: "JARVIS, qual é meu projeto atual?"
JARVIS (Gemini): "Não sei."
Você: [👎 Bad Response] + Correção: "É o JARVIS 5.0"
```

Isso vai pro dataset de treinamento!

### Método 2: Golden Commands

Crie comandos exemplares:

**Dashboard → Learning → Add Golden Command:**
```yaml
Input: "Como está o clima?"
Expected Output: "Verificando WeatherAPI... Brasília: 28°C, ensolarado."
Context: "Sempre use WeatherAPI para clima"
```

### Método 3: Upload de Dataset

Se você tem dados históricos:

```python
from src.learning.knowledge_distiller import KnowledgeDistiller

distiller = KnowledgeDistiller()

# Adicionar batch de exemplos
examples = [
    {"input": "Oi", "output": "Olá William, como posso ajudar?"},
    {"input": "Obrigado", "output": "Por nada, senhor. Disponha sempre."},
]

distiller.add_golden_commands(examples)
```

---

## 🔒 Privacidade & Segurança

### O que Local Brain Armazena?

- ✅ Suas perguntas e preferências
- ✅ Padrões de uso
- ✅ Conhecimento fornecido por você

### O que NÃO armazena?

- ❌ Senhas ou dados sensíveis (filtrados automaticamente)
- ❌ Dados não relacionados ao JARVIS
- ❌ Informações não confirmadas

### Dados Nunca Saem do PC

- ❌ Não enviados para cloud
- ❌ Não compartilhados
- ❌ Não vendidos

**100% seu. 100% privado.**

---

## 📈 Performance

### Hardware Recomendado

| Component | Mínimo | Recomendado | Ideal |
|-----------|--------|-------------|-------|
| **RAM** | 8 GB | 16 GB | 32 GB |
| **GPU** | - | GTX 1060 (6GB) | RTX 3060+ (12GB) |
| **Storage** | 10 GB | 20 GB | 50 GB SSD |
| **CPU** | 4 cores | 8 cores | 16 cores |

### Benchmarks

**Inferência (geração de resposta):**
- RTX 3060: ~50 tokens/s (~0.3s resposta)
- GTX 1060: ~20 tokens/s (~0.8s resposta)
- CPU only: ~5 tokens/s (~3s resposta)

**Treinamento:**
- RTX 3060: ~30-60 min (primeira vez)
- GTX 1060: ~1-2 horas
- CPU only: ~4-8 horas ⚠️

---

## 🔧 Solução de Problemas

### "Local Brain not trained yet"

**Normal!** Precisa de 100 feedbacks primeiro.

**Acelerar:**
1. Use JARVIS intensivamente
2. Dê feedback em TODAS interações
3. Ou force treino: Dashboard → Start Training Now

### "Training failed: Out of Memory"

**Soluções:**
1. Reduzir batch_size: `4` → `2` ou `1`
2. Ativar mixed_precision: `true`
3. Usar modelo base menor: `llama3.1-8b` → `phi3-3b`
4. Fechar outros programas

### "Quality score baixo (<80%)"

**Melhorar:**
1. Dar mais feedbacks (precisa de volume)
2. Ser consistente nas correções
3. Adicionar Golden Commands manualmente
4. Aumentar epochs: `3` → `5`

### "Respostas genéricas"

**Causa:** Pouco treinamento específico

**Solução:**
1. Adicionar mais Golden Commands do SEU contexto
2. Usar mais o Local Brain (ele aprende em uso)
3. Dar feedback específico

---

## 🆘 Suporte

- **Aprendizado:** [learning-system.md](learning-system.md)
- **Training:** [model-training.md](model-training.md)
- **Ollama:** [ollama-integration.md](ollama-integration.md)

---

<div align="center">

**Sua IA. Sua personalidade. Seu conhecimento. 🧬**

*"The best AI is the one that knows you."*

</div>
