# 🎓 Guia Completo de Treinamento Avançado - JARVIS 5.0

## 📚 Visão Geral

O JARVIS 5.0 agora possui um **sistema completo e profissional de treinamento de IA** que permite:

1. ✅ **Treinamento Multi-Modal** - Conversação, código e documentos
2. ✅ **Preparação Automática de Dados** - Coleta e filtragem inteligente
3. ✅ **Workflows Flexíveis** - Treinamento completo, incremental e rápido
4. ✅ **Auto-Treinamento Inteligente** - Melhoria contínua automática
5. ✅ **Configuração Granular** - Controle total sobre hiperparâmetros

---

## 🚀 Início Rápido

### 1. Verificar Status do Sistema

```bash
curl http://localhost:8000/api/training/comprehensive-status
```

Retorna status completo incluindo:
- Status de treinamento atual
- Auto-trainer status
- Estatísticas do dataset
- Configuração atual

### 2. Iniciar Treinamento Rápido

Para um treinamento rápido com dados existentes:

```bash
curl -X POST http://localhost:8000/api/training/workflow \
  -H "Content-Type: application/json" \
  -d '{
    "type": "quick"
  }'
```

### 3. Treinamento Completo

Para um treinamento completo com preparação de dataset:

```bash
curl -X POST http://localhost:8000/api/training/workflow \
  -H "Content-Type: application/json" \
  -d '{
    "type": "full",
    "config": {
      "model": {
        "base_model": "codellama:7b",
        "custom_model_name": "jarvis-custom"
      }
    }
  }'
```

---

## 🎯 Tipos de Treinamento

### 1. Treinamento Completo (`full`)

**Quando usar**: Primeira vez ou retreinamento completo do modelo

**O que faz**:
1. Coleta todos os dados disponíveis
2. Prepara e filtra dataset por qualidade
3. Divide em train/validation/test
4. Treina modelo do zero usando Ollama Modelfile
5. Valida modelo treinado

**Tempo**: ~5-15 minutos

**Exemplo**:
```json
{
  "type": "full",
  "config": {
    "model": {
      "base_model": "codellama:7b",
      "custom_model_name": "jarvis-custom",
      "temperature": 0.7
    },
    "dataset": {
      "min_interactions": 50,
      "include_conversations": true,
      "include_code_examples": true,
      "include_documents": false
    }
  }
}
```

### 2. Treinamento Incremental (`incremental`)

**Quando usar**: Adicionar novos dados ao modelo existente

**O que faz**:
1. Coleta apenas dados novos desde último treinamento
2. Adiciona ao modelo existente
3. Retreina incrementalmente

**Tempo**: ~2-5 minutos

**Exemplo**:
```json
{
  "type": "incremental"
}
```

### 3. Treinamento Rápido (`quick`)

**Quando usar**: Testes rápidos ou ajustes menores

**O que faz**:
1. Usa dados já coletados sem preparação completa
2. Cria Modelfile rapidamente
3. Treina modelo base

**Tempo**: ~1-3 minutos

**Exemplo**:
```json
{
  "type": "quick"
}
```

---

## ⚙️ Configuração Avançada

### Estrutura de Configuração

```json
{
  "model": {
    "base_model": "codellama:7b",
    "custom_model_name": "jarvis-custom",
    "model_type": "conversational",
    "context_length": 4096,
    "temperature": 0.7,
    "top_p": 0.9,
    "top_k": 40,
    "repeat_penalty": 1.1
  },
  "dataset": {
    "min_interactions": 50,
    "min_quality_score": 0.5,
    "max_samples": 10000,
    "include_code_examples": true,
    "include_conversations": true,
    "include_documents": false,
    "train_test_split": 0.8,
    "validation_split": 0.1
  },
  "training": {
    "learning_rate": 0.0001,
    "batch_size": 32,
    "num_epochs": 10,
    "warmup_steps": 100,
    "optimizer": "adamw",
    "scheduler": "linear"
  },
  "auto_training": {
    "enabled": true,
    "quality_threshold": 0.6,
    "retrain_interval_hours": 24,
    "min_interactions_for_training": 50,
    "min_interactions_for_incremental": 20
  }
}
```

### Configurações Pré-definidas

#### Para Conversação
```bash
curl -X POST http://localhost:8000/api/training/config/load \
  -H "Content-Type: application/json" \
  -d '{"name": "conversation"}'
```

Configuração otimizada para chat:
- Modelo base: `llama2:7b`
- Temperature: 0.8 (mais criativo)
- Foco em conversas

#### Para Código
```bash
curl -X POST http://localhost:8000/api/training/config/load \
  -H "Content-Type: application/json" \
  -d '{"name": "code"}'
```

Configuração otimizada para programação:
- Modelo base: `codellama:7b`
- Temperature: 0.2 (mais preciso)
- Foco em exemplos de código

#### Uso Geral
```bash
curl -X POST http://localhost:8000/api/training/config/load \
  -H "Content-Type: application/json" \
  -d '{"name": "default"}'
```

Configuração balanceada:
- Modelo base: `mistral:7b`
- Temperature: 0.7
- Todos os tipos de dados

---

## 📊 Preparação de Dataset

### Verificar Dados Disponíveis

```bash
curl http://localhost:8000/api/training/dataset/stats
```

Retorna:
```json
{
  "total_interactions": 150,
  "user_messages": 150,
  "assistant_messages": 150,
  "can_prepare_dataset": true,
  "min_required": 50
}
```

### Preparar Dataset Manualmente

```bash
curl -X POST http://localhost:8000/api/training/dataset/prepare \
  -H "Content-Type: application/json" \
  -d '{
    "include_new_only": false
  }'
```

### Fontes de Dados

O sistema coleta dados de múltiplas fontes:

1. **Conversação** (`conversation`)
   - Histórico de chat com JARVIS
   - Pares pergunta-resposta
   - Qualidade média: 0.5-0.8

2. **Código** (`code`)
   - Interações contendo código
   - Exemplos de programação
   - Qualidade média: 0.7-0.9

3. **Documentos** (`document`)
   - Arquivos `.txt` e `.md` em `./data/documents/`
   - Seções de documentação
   - Qualidade média: 0.6-0.8

### Filtro de Qualidade

O sistema automaticamente filtra amostras por:

1. **Comprimento apropriado**
   - Input: 10-500 caracteres
   - Output: 20-2000 caracteres

2. **Diversidade de vocabulário**
   - Mínimo de palavras únicas

3. **Ausência de padrões ruins**
   - Erros explícitos
   - Respostas negativas
   - Limitações do sistema

4. **Completude**
   - Respostas terminadas corretamente

**Score mínimo padrão**: 0.5 (configurável)

---

## 🤖 Auto-Treinamento

### Como Funciona

O sistema monitora automaticamente:

1. **Qualidade das Respostas**
   - Calcula score a cada interação
   - Dispara retreino se cair abaixo de 60%

2. **Intervalo Periódico**
   - Retreino automático a cada 24 horas
   - Apenas se houver dados novos suficientes

3. **Novos Dados**
   - Treina quando acumular 20+ novas interações
   - Treinamento incremental

### Habilitar/Desabilitar

Auto-treinamento é **habilitado por padrão**.

Para desabilitar:
```bash
curl -X POST http://localhost:8000/api/training/config/update \
  -H "Content-Type: application/json" \
  -d '{
    "updates": {
      "auto_training": {
        "enabled": false
      }
    }
  }'
```

### Configurar Thresholds

```bash
curl -X POST http://localhost:8000/api/training/config/update \
  -H "Content-Type: application/json" \
  -d '{
    "updates": {
      "auto_training": {
        "quality_threshold": 0.7,
        "retrain_interval_hours": 48,
        "min_interactions_for_incremental": 30
      }
    }
  }'
```

---

## 📈 Monitoramento

### Status Completo

```bash
curl http://localhost:8000/api/training/comprehensive-status
```

Retorna informações detalhadas:

```json
{
  "training_status": {
    "is_training": false,
    "current_stage": "idle",
    "progress": 0.0,
    "message": "Sistema pronto"
  },
  "auto_trainer_status": {
    "auto_train_enabled": true,
    "current_quality": 0.75,
    "quality_threshold": 0.6,
    "should_train": false,
    "last_training": "2024-01-15T10:30:00",
    "next_scheduled_training": "2024-01-16T10:30:00",
    "total_trainings": 5
  },
  "training_manager_status": {
    "custom_models": ["jarvis-custom"],
    "pairs_available": 150,
    "can_train": true,
    "status": "ready"
  },
  "dataset_stats": {
    "total_interactions": 150,
    "can_prepare_dataset": true
  },
  "configuration": {
    "model": { "base_model": "codellama:7b" },
    "auto_training": { "enabled": true }
  }
}
```

### Durante Treinamento

O campo `training_status` mostra progresso em tempo real:

```json
{
  "is_training": true,
  "current_stage": "training_model",
  "progress": 65.0,
  "message": "Treinando modelo..."
}
```

Estágios possíveis:
- `initializing` (0-5%)
- `preparing_dataset` (5-30%)
- `training_model` (30-80%)
- `validating` (80-95%)
- `finalizing` (95-100%)
- `completed` (100%)

---

## 🎨 Casos de Uso

### 1. Treinar JARVIS para Conversar Sobre Python

1. Use JARVIS normalmente, faça perguntas sobre Python
2. Acumule 50+ interações
3. Execute treinamento:

```bash
curl -X POST http://localhost:8000/api/training/workflow \
  -H "Content-Type: application/json" \
  -d '{
    "type": "full",
    "config": {
      "model": {
        "base_model": "codellama:7b",
        "custom_model_name": "jarvis-python"
      },
      "dataset": {
        "include_code_examples": true,
        "include_conversations": true
      }
    }
  }'
```

4. Use o modelo customizado:
```bash
# Atualizar config para usar modelo customizado
export OLLAMA_MODEL=jarvis-python
```

### 2. Melhoria Contínua Automática

1. Habilite auto-treinamento (já vem habilitado)
2. Use JARVIS normalmente
3. Sistema treina automaticamente quando necessário
4. Modelo melhora sozinho ao longo do tempo

### 3. Treinamento com Documentação Customizada

1. Adicione seus documentos em `./data/documents/`
2. Configure para incluir documentos:

```bash
curl -X POST http://localhost:8000/api/training/config/update \
  -H "Content-Type: application/json" \
  -d '{
    "updates": {
      "dataset": {
        "include_documents": true
      }
    }
  }'
```

3. Execute treinamento completo

---

## 🔍 Troubleshooting

### "Interações insuficientes"

**Problema**: Não há dados suficientes para treinar

**Solução**:
- Continue usando JARVIS normalmente
- Mínimo: 50 interações
- Verifique: `GET /api/training/dataset/stats`

### "Modelo não melhora"

**Problema**: Modelo customizado não apresenta melhorias

**Possíveis causas**:
1. Poucos dados (< 100 interações)
2. Dados de baixa qualidade
3. Configuração inadequada

**Soluções**:
- Acumule mais interações (200+)
- Verifique qualidade no dataset stats
- Ajuste `min_quality_score` para 0.6+
- Use treinamento incremental periodicamente

### "Treinamento demora muito"

**Normal**: Primeiro treinamento pode levar 5-15 minutos

**Se demorar mais**:
- Verifique se Ollama está rodando
- Verifique recursos disponíveis (RAM, CPU)
- Use `type: "quick"` para testes rápidos

### "Erro ao criar modelo"

**Verificações**:
1. Ollama está rodando?
   ```bash
   curl http://localhost:11434/api/tags
   ```

2. Modelo base existe?
   ```bash
   ollama list
   ```

3. Espaço em disco suficiente?

**Solução**:
```bash
# Baixar modelo base se necessário
ollama pull codellama:7b

# Verificar logs
docker-compose logs -f jarvis
```

---

## 🎓 Boas Práticas

### 1. Coleta de Dados

✅ **Faça**:
- Use JARVIS naturalmente
- Faça perguntas variadas
- Interaja com diferentes tópicos

❌ **Evite**:
- Perguntas repetitivas
- Respostas de uma palavra
- Interações sem sentido

### 2. Configuração

✅ **Faça**:
- Comece com configuração padrão
- Ajuste gradualmente baseado em resultados
- Mantenha min_quality_score >= 0.5

❌ **Evite**:
- Mudar muitos parâmetros de uma vez
- min_quality_score muito alto (> 0.8)
- Batch sizes muito grandes para hardware limitado

### 3. Treinamento

✅ **Faça**:
- Primeiro treinamento: `full`
- Atualizações: `incremental`
- Testes: `quick`
- Deixe auto-treinamento ativo

❌ **Evite**:
- Treinar com < 50 interações
- Retreinamento completo desnecessário
- Desabilitar auto-treinamento sem motivo

---

## 📚 Próximos Passos

Funcionalidades planejadas:

- [ ] Fine-tuning com PyTorch/Transformers
- [ ] A/B testing de modelos
- [ ] Métricas avançadas de qualidade
- [ ] Dashboard web de treinamento
- [ ] Treinamento distribuído
- [ ] Integração com HuggingFace Hub

---

## 🆘 Suporte

**Dúvidas?**
- Consulte logs: `docker-compose logs -f jarvis`
- Status: `GET /api/training/comprehensive-status`
- Issues: GitHub repository

**Documentação Adicional**:
- [GUIA_TREINAMENTO.md](GUIA_TREINAMENTO.md) - Guia básico
- [GUIA_CONHECIMENTO_HUGGINGFACE.md](GUIA_CONHECIMENTO_HUGGINGFACE.md) - Knowledge Base e HuggingFace
- [ANALISE_PROJETO.md](ANALISE_PROJETO.md) - Análise do projeto

---

🎉 **Agora seu JARVIS aprende e melhora automaticamente!**
