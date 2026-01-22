# 🎓 Guia Completo de Treinamento - JARVIS 5.0

## 📚 Visão Geral

O JARVIS agora possui um **sistema completo de treinamento** que permite:

1. ✅ **Treinamento Real** - Usa Ollama Modelfile para criar modelos customizados
2. ✅ **Aprendizado Contínuo** - Coleta interações automaticamente
3. ✅ **Auto-Treinamento** - Treina automaticamente quando qualidade cai
4. ✅ **Treinamento Incremental** - Adiciona novos dados ao modelo existente

---

## 🚀 Como Funciona

### 1. **Coleta Automática de Dados**

Todas as interações entre você e o JARVIS são automaticamente:
- Salvas no banco de dados persistente
- Agrupadas em pares query-resposta
- Preparadas para treinamento

**Requisitos para Treinar:**
- Mínimo de **50 interações** coletadas
- Pelo menos **50 pares** query-resposta válidos

### 2. **Treinamento Inicial**

Quando você tem dados suficientes:

```bash
# Via Interface Web
1. Clique no indicador "Treinamento" no header
2. Clique em "🚀 Iniciar Treinamento"
3. Aguarde (pode levar alguns minutos)

# Via API
POST /api/training/start
{
  "base_model": "codellama:7b",
  "custom_name": "jarvis-custom"
}
```

O sistema irá:
1. Coletar todas as interações salvas
2. Criar um Modelfile do Ollama com exemplos
3. Gerar um modelo customizado `jarvis-custom`
4. Salvar metadados do treinamento

### 3. **Auto-Treinamento**

O sistema monitora automaticamente:
- **Qualidade das respostas** - Se cai abaixo de 60%, treina
- **Período** - Retreino incremental a cada 24 horas
- **Novos dados** - Quando há 20+ novas interações

### 4. **Treinamento Incremental**

Adiciona novos dados ao modelo existente:

```bash
# Via Interface
Clique em "🔄 Treinamento Incremental"

# Via API
POST /api/training/incremental
```

---

## 📊 Dashboard de Treinamento

Acesse via interface web (clique no indicador de treinamento no header):

**Métricas Mostradas:**
- ✅ Status: Pronto para treinar ou Coletando dados
- 📈 Interações Coletadas: Quantos pares você tem
- 🎯 Qualidade Atual: Qualidade média das respostas
- ⏰ Último Treinamento: Quando foi treinado pela última vez
- 📅 Próximo Treinamento: Quando será o próximo treinamento automático

---

## ⚙️ Configuração

### Parâmetros do Auto-Trainer

No código (`core/auto_trainer.py`):

```python
min_interactions_for_training = 50      # Mínimo para primeiro treinamento
min_interactions_for_incremental = 20   # Mínimo para incremental
quality_threshold = 0.6                 # Threshold de qualidade (60%)
retrain_interval_hours = 24             # Intervalo entre retreinos
```

### Usar Modelo Customizado

Após treinar, você pode usar o modelo customizado:

1. No `config/config.json`:
```json
{
  "ollama_model": "jarvis-custom"
}
```

2. Ou via variável de ambiente:
```bash
OLLAMA_MODEL=jarvis-custom
```

---

## 🔍 Monitoramento

### Status via API

```bash
GET /api/training/status
```

Retorna:
```json
{
  "training_status": {
    "can_train": true,
    "pairs_available": 75,
    "status": "ready"
  },
  "auto_trainer": {
    "current_quality": 0.75,
    "should_train": false,
    "last_training": "2024-01-15T10:30:00",
    "next_scheduled_training": "2024-01-16T10:30:00"
  }
}
```

### Logs

O sistema registra todas as ações:
- Coleta de dados
- Início/fim de treinamento
- Decisões de auto-treinamento
- Erros e avisos

---

## 🎯 Boas Práticas

1. **Use o JARVIS normalmente** - Quanto mais interações, melhor
2. **Aguarde coletar 50+ interações** antes do primeiro treinamento
3. **Deixe o auto-treinamento ativo** - Ele melhora automaticamente
4. **Monitore qualidade** - Use o dashboard para ver progresso
5. **Treinamento incremental periódico** - Mantém modelo atualizado

---

## ❓ Troubleshooting

### "Interações insuficientes"
- Você precisa de pelo menos 50 interações
- Continue usando o JARVIS normalmente
- Verifique em `/api/training/status`

### "Erro ao criar modelo"
- Verifique se Ollama está rodando
- Confirme que o modelo base existe (`ollama list`)
- Verifique logs em `./logs/`

### "Treinamento demora muito"
- Normal! Pode levar 5-15 minutos
- Primeiro treinamento é mais demorado
- Treinamentos incrementais são mais rápidos

### "Modelo customizado não melhora"
- Aguarde mais interações (100+)
- Treinamento incremental ajuda
- Verifique qualidade no dashboard

---

## 🔬 Como Funciona Internamente

### 1. Modelfile do Ollama

O sistema cria um arquivo `.Modelfile` com:
- Modelo base (`FROM codellama:7b`)
- Sistema prompt customizado
- Exemplos de few-shot learning (últimas 20 interações)

### 2. Armazenamento

Dados salvos em:
- `./data/memory.db` - SQLite com histórico
- `./data/training/*.Modelfile` - Modelfiles gerados
- `./data/training/*.json` - Datasets completos

### 3. Auto-Treinamento

O `AutoTrainer` monitora:
- Qualidade a cada interação
- Verifica necessidade a cada 10 interações
- Agenda treinamento incremental a cada 50 interações
- Retreino periódico a cada 24 horas

---

## 📈 Próximos Passos

- [ ] Fine-tuning com PyTorch/Transformers
- [ ] Integração com HuggingFace
- [ ] Treinamento distribuído
- [ ] A/B testing de modelos
- [ ] Métricas avançadas de qualidade

---

**🎉 Pronto! Agora seu JARVIS aprende sozinho!**

