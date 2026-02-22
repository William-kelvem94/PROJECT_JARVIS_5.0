# Treinamento Externo JARVIS 5.0

Este documento explica como treinar componentes do JARVIS externamente, sem iniciar o sistema completo.

## Métodos de Treinamento Disponíveis

### 1. **Local Trainer (LLM Fine-tuning)**
- **Arquivo**: `src/learning/trainer.py`
- **Descrição**: Fine-tuning de Large Language Models usando LoRA/QLoRA
- **Modelos suportados**: Llama-3, Mistral, Phi, Gemma
- **Recursos**: 4-bit/8-bit quantization, checkpoint management

### 2. **Distributed Trainer**
- **Arquivo**: `src/learning/distributed_trainer.py`
- **Descrição**: Treinamento distribuído multi-GPU
- **Recursos**: Gradient synchronization, data parallelism

### 3. **Learning Engine (Orquestrador)**
- **Arquivo**: `src/learning/learning_engine.py`
- **Descrição**: Orquestrador central de todos os sistemas de aprendizado
- **Componentes**:
  - Continual Learner (Auto-training)
  - Feedback Loop (RLHF/DPO)
  - Knowledge Distiller (Golden Commands)
  - Dream Cycle (Nighttime Training)
  - Model Registry (Versioning & A/B Testing)
  - Metrics Dashboard (Real-time monitoring)

### 4. **Vision Learner**
- **Arquivo**: `src/learning/vision_learner.py`
- **Descrição**: Treinamento de modelos de visão computacional
- **Recursos**: YOLO training, incremental learning

### 5. **Emotion Voice Trainer**
- **Arquivo**: `src/learning/emotion_voice_trainer.py`
- **Descrição**: Treinamento de modelos de voz emocional

### 6. **Study Mode (Estudo Baseado em Tópicos)**
- **Arquivo**: `src/learning/knowledge_distiller.py`
- **Descrição**: Gera automaticamente dados de treinamento baseados em tópicos/prompts
- **Recursos**: Pesquisa contextual, geração de exemplos, distilação de conhecimento

### 7. **Outros Componentes**
- **Dream Cycle**: `src/learning/dream_cycle.py` - Simulações criativas
- **Feedback Loop**: `src/learning/feedback_loop.py` - Coleta e processamento de feedback
- **Neural Curiosity**: `src/learning/neural_curiosity.py` - Exploração autônoma

## Como Treinar Externamente

### Usando o Script Externo

1. **Preparar configuração**:
   ```bash
   # Edite config/training_config.yaml com suas configurações
   ```

2. **Executar treinamento**:
   ```bash
   # Treinamento de LLM
   python scripts/external_trainer.py --component llm --config config/training_config.yaml

   # Estudo sobre um tópico específico
   python scripts/external_trainer.py --component study --topic "Machine Learning" --config config/training_config.yaml

   # Outros componentes disponíveis:
   # vision, distributed, continual, feedback, dream, emotion
   ```

3. **Componentes disponíveis**:
   - `llm`: Fine-tuning de LLMs
   - `vision`: Treinamento de visão
   - `distributed`: Treinamento distribuído
   - `continual`: Aprendizado contínuo
   - `feedback`: Loop de feedback
   - `dream`: Ciclo de sonho
   - `emotion`: Voz emocional
   - `study`: Geração automática de dados baseada em tópicos

### Treinamento Manual (Importando Diretamente)

```python
from src.learning.trainer import LocalTrainer

# Configurar treinamento
trainer = LocalTrainer(
    model_name="microsoft/DialoGPT-medium",
    dataset_path="data/training_data/conversations.json",
    output_dir="models/fine_tuned"
)

# Executar treinamento
trainer.train()
```

## Regras Automatizadas de Aprendizado

O sistema JARVIS possui várias regras automatizadas que são respeitadas mesmo no treinamento externo:

### 1. **Sanity Checks**
- Validação de dados antes do treinamento
- Verificação de consistência do modelo
- Monitoramento de overfitting

### 2. **Feedback Loops**
- Coleta automática de feedback
- Reinforcement Learning from Human Feedback (RLHF)
- Direct Preference Optimization (DPO)

### 3. **Safety Constraints**
- Validação ética dos dados
- Prevenção de bias prejudiciais
- Limites de recursos computacionais

### 4. **Auto-healing**
- Recuperação automática de falhas
- Otimização de performance
- Ajuste dinâmico de hiperparâmetros

### 5. **Versioning & Registry**
- Controle de versão de modelos
- A/B testing automático
- Rollback seguro

## Exemplo de Configuração Completa

```yaml
# config/training_config.yaml
llm_config:
  model_name: "microsoft/DialoGPT-medium"
  dataset_path: "data/training_data/conversations.json"
  output_dir: "models/fine_tuned"
  training_args:
    num_train_epochs: 3
    learning_rate: 5e-5
    per_device_train_batch_size: 4
```

## Monitoramento

Durante o treinamento, você pode monitorar o progresso através dos logs e do Metrics Dashboard integrado ao sistema.

## Modo Study: Treinamento Baseado em Conhecimento

O modo `study` permite que o JARVIS aprenda sobre qualquer tópico automaticamente, gerando dados de treinamento estruturados.

### Como Funciona

1. **Entrada**: Você fornece um tópico (ex: "Inteligência Artificial", "Física Quântica")
2. **Pesquisa Contextual**: O sistema pesquisa e coleta informações relevantes
3. **Geração de Exemplos**: Cria pares de perguntas/respostas, contextos, e dados estruturados
4. **Distilação**: Organiza o conhecimento em formato ideal para treinamento
5. **Saída**: Arquivo JSON com dados prontos para treinamento

### Exemplo de Uso

```bash
# Estudar sobre um tópico específico
python scripts/external_trainer.py --component study --topic "Redes Neurais" --config config/training_config.yaml

# O sistema irá:
# 1. Pesquisar sobre Redes Neurais
# 2. Gerar exemplos de treinamento
# 3. Salvar em data/learning/training_data/study_Redes_Neurais.json
```

### Dados Gerados

O arquivo de saída contém:
- **Contextos**: Textos explicativos sobre o tópico
- **Perguntas/Respostas**: Pares Q&A gerados
- **Exemplos**: Casos práticos e aplicações
- **Metadados**: Informações sobre a fonte e relevância

### Integração com Treinamento

Após gerar os dados, você pode usar outros modos para treinar:
```bash
# Primeiro gera dados
python scripts/external_trainer.py --component study --topic "Python Programming"

# Depois treina o LLM com os dados gerados
python scripts/external_trainer.py --component llm --config config/training_config.yaml
```