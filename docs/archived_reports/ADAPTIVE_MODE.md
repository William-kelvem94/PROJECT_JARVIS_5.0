# JARVIS AGI - Modo Adaptativo (All-in-One)

## 🧠 Visão Geral

O **Modo Adaptativo** é o modo de operação padrão do JARVIS Singularity AGI. Ao invés de ter que escolher manualmente entre diferentes modos de operação, o Modo Adaptativo integra automaticamente todos os comportamentos de forma inteligente e contextual.

## 🎯 Conceito: "Tudo em 1"

O Modo Adaptativo combina dinamicamente os seguintes comportamentos:

### 1. **Modo Ativo** 🚀
- **Quando**: Alta confiança + Input do usuário
- **Comportamento**: Responde imediatamente
- **Exemplo**: User: "Crie um arquivo Python" → JARVIS cria instantaneamente

### 2. **Modo Passivo** 👀
- **Quando**: Sem input do usuário + Observação
- **Comportamento**: Observa e aprende padrões silenciosamente
- **Exemplo**: Monitora uso de aplicativos para aprender rotinas

### 3. **Modo Aprendizagem** 📚
- **Quando**: Baixa confiança + Oportunidade de aprender
- **Comportamento**: Busca ativamente melhorar conhecimento
- **Exemplo**: User: "Configure X" + Baixa confiança → JARVIS: "Posso tentar, mas prefere que eu pesquise primeiro?"

### 4. **Modo Exploração** 🔍
- **Quando**: Confiança média + Situação não-urgente
- **Comportamento**: Tenta novas abordagens de forma segura
- **Exemplo**: Testa diferentes maneiras de resolver um problema

### 5. **Modo Seguro** 🛡️
- **Quando**: Situação crítica + Baixa confiança
- **Comportamento**: Apenas ações comprovadas, pede confirmação
- **Exemplo**: User: "Erro crítico no sistema" + Baixa confiança → JARVIS pede mais informações

## 🔄 Como Funciona

### Matriz de Decisão

```
┌─────────────────────────────────────────────────────────────┐
│                    MODO ADAPTATIVO                          │
│                 (Decisão Automática)                        │
└─────────────────────────────────────────────────────────────┘
                           ↓
        ┌──────────────────┴──────────────────┐
        │   Avaliar Contexto                  │
        │   • Confiança                       │
        │   • Urgência                        │
        │   • Criticidade                     │
        │   • Input do usuário                │
        │   • Histórico                       │
        └──────────────────┬──────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────────┐
│                    ÁRVORE DE DECISÃO                         │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  Situação CRÍTICA + Confiança BAIXA?                        │
│  ├─ SIM → [MODO SEGURO] Pedir esclarecimento               │
│  └─ NÃO → Continuar...                                      │
│                                                              │
│  Input do usuário + Confiança ALTA (≥80%)?                  │
│  ├─ SIM → [MODO ATIVO] Responder imediatamente             │
│  └─ NÃO → Continuar...                                      │
│                                                              │
│  Não-urgente + Confiança MÉDIA (50-80%)?                    │
│  ├─ SIM → 30% chance [MODO EXPLORAÇÃO] Tentar nova forma   │
│  └─ NÃO → Continuar...                                      │
│                                                              │
│  Input do usuário + Confiança ADEQUADA (≥60%)?             │
│  ├─ SIM → [MODO ATIVO] Responder normalmente               │
│  └─ NÃO → Continuar...                                      │
│                                                              │
│  Input do usuário + Confiança BAIXA (<60%)?                │
│  ├─ SIM → [MODO APRENDIZAGEM] Aprender e pedir ajuda       │
│  └─ NÃO → Continuar...                                      │
│                                                              │
│  Sem input + Alta confiança para sugestão (≥70%)?          │
│  ├─ SIM → 20% chance [MODO ATIVO] Sugerir proativamente    │
│  └─ NÃO → Continuar...                                      │
│                                                              │
│  Padrão:                                                     │
│  └─ [MODO PASSIVO] Observar e aprender padrões              │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

## 📊 Exemplos Práticos

### Exemplo 1: Alta Confiança - Resposta Imediata
```python
User: "Qual é o clima hoje?"
Contexto: Confiança = 95%
Decisão: [ADAPTIVE-ACTIVE] Responder imediatamente
Ação: "Hoje está ensolarado, 25°C..."
```

### Exemplo 2: Baixa Confiança - Aprendizagem
```python
User: "Configure o protocolo MQTT no servidor"
Contexto: Confiança = 45%, Não-urgente
Decisão: [ADAPTIVE-LEARNING] Aprender e orientar
Ação: "Não tenho certeza total. Posso pesquisar ou você prefere me ensinar?"
```

### Exemplo 3: Situação Crítica - Modo Seguro
```python
User: "ERRO CRÍTICO: Sistema travando!"
Contexto: Confiança = 50%, Crítico = True
Decisão: [ADAPTIVE-SAFE] Ação segura apenas
Ação: "Situação crítica detectada. Pode descrever exatamente o que aconteceu?"
```

### Exemplo 4: Exploração Segura
```python
User: "Organize meus arquivos"
Contexto: Confiança = 65%, Não-urgente
Decisão: [ADAPTIVE-EXPLORE] 30% chance de explorar
Ação: "Vou tentar uma nova forma de organizar. Posso mostrar primeiro?"
```

### Exemplo 5: Sugestão Proativa
```python
User: [Sem input]
Contexto: Sexta 19h, Steam aberto, Confiança sugestão = 85%
Decisão: [ADAPTIVE-ACTIVE] 20% chance de sugerir
Ação: "Detectei que você geralmente joga agora. Quer que eu configure o modo gaming?"
```

### Exemplo 6: Observação Silenciosa
```python
User: [Sem input]
Contexto: Atividade normal, sem padrões claros
Decisão: [ADAPTIVE-PASSIVE] Observar
Ação: [Silencioso] Monitora e aprende padrões
```

## 🎮 Configuração

### Ativação (Padrão)
O Modo Adaptativo é ativado automaticamente ao iniciar o JARVIS:

```python
from src.core.autonomy import AutonomyCore, AutonomyMode
from pathlib import Path

# Inicializa com Modo Adaptativo (padrão)
autonomy = AutonomyCore(
    data_dir=Path("data/learning"),
    initial_mode=AutonomyMode.ADAPTIVE,  # Padrão
    confidence_threshold=0.6
)

autonomy.start()
```

### Ajuste de Sensibilidade
```python
# Mais cauteloso (threshold maior)
autonomy = AutonomyCore(
    data_dir=Path("data/learning"),
    confidence_threshold=0.7  # Só age com 70%+ de confiança
)

# Mais agressivo (threshold menor)
autonomy = AutonomyCore(
    data_dir=Path("data/learning"),
    confidence_threshold=0.5  # Age com 50%+ de confiança
)
```

## 🔍 Monitoramento

### Verificar Decisões
```python
# Processar uma situação
from src.core.autonomy import DecisionContext

context = DecisionContext(
    user_input="Crie um script Python",
    current_task="coding",
    system_state={"confidence": 0.85}
)

decision = autonomy.process_situation(context)

print(f"Decisão: {decision.decision_type.value}")
print(f"Ação: {decision.action}")
print(f"Confiança: {decision.confidence:.2f}")
print(f"Raciocínio: {decision.reasoning}")
```

### Estatísticas
```python
# Ver estatísticas do modo adaptativo
stats = autonomy.get_statistics()
print(f"Total de decisões: {stats['total_decisions']}")
print(f"Por tipo: {stats['decisions_by_type']}")
print(f"Taxa de sucesso: {stats['successful_actions']}/{stats['total_decisions']}")
```

## 🎯 Vantagens do Modo Adaptativo

### ✅ Vantagens

1. **Zero Configuração Manual**
   - Não precisa escolher modos
   - Funciona automaticamente
   - Adapta-se ao contexto

2. **Comportamento Inteligente**
   - Cauteloso quando necessário
   - Ágil quando possível
   - Sempre aprendendo

3. **Melhor Experiência do Usuário**
   - Responde rápido quando sabe
   - Pede ajuda quando não sabe
   - Não faz besteira em situações críticas

4. **Evolução Contínua**
   - Aprende com cada interação
   - Melhora com o tempo
   - Personaliza-se ao usuário

5. **Segurança Integrada**
   - Detecção automática de riscos
   - Modo seguro em situações críticas
   - Sempre pede confirmação quando incerto

### ⚖️ Comparação com Modos Separados

| Aspecto | Modos Separados | Modo Adaptativo |
|---------|----------------|-----------------|
| Configuração | Manual | Automática |
| Flexibilidade | Limitada ao modo | Total |
| Inteligência | Fixa | Contextual |
| Experiência | Pode ser frustrante | Fluida |
| Aprendizado | Limitado ao modo | Contínuo |
| Segurança | Depende do modo | Sempre ativa |

## 🔧 Troubleshooting

### "JARVIS está muito cauteloso"
```python
# Reduzir threshold de confiança
autonomy.decision_engine.confidence_threshold = 0.5
```

### "JARVIS está muito agressivo"
```python
# Aumentar threshold de confiança
autonomy.decision_engine.confidence_threshold = 0.7
```

### "Quero forçar um modo específico temporariamente"
```python
# Ainda é possível usar modos legados se necessário
from src.core.autonomy import AutonomyMode

# Temporariamente só observar
autonomy.set_mode(AutonomyMode.LEARNING)

# Voltar ao adaptativo
autonomy.set_mode(AutonomyMode.ADAPTIVE)
```

## 📈 Métricas de Performance

O Modo Adaptativo rastreia:

- **Confiança média por tipo de tarefa**
- **Taxa de sucesso por contexto**
- **Tempo de resposta médio**
- **Número de explorações vs explorações**
- **Evolução da confiança ao longo do tempo**

```python
# Ver métricas detalhadas
metrics = autonomy.meta_learning_controller.get_statistics()
print(f"Tarefas dominadas: {metrics['mastered_tasks']}")
print(f"Tendência de melhoria: {metrics['performance_trends']['improvement_rate']:.2%}")
```

## 🎓 Conclusão

O **Modo Adaptativo** é a evolução natural da IA:
- **Inteligente**: Decide o melhor comportamento automaticamente
- **Adaptável**: Muda conforme o contexto
- **Seguro**: Cauteloso quando necessário
- **Eficiente**: Rápido quando possível
- **Evolutivo**: Sempre melhorando

É o verdadeiro "Tudo em 1" - todos os comportamentos integrados de forma inteligente! 🚀

---

**Modo Adaptativo = IA que pensa antes de agir, mas age rápido quando sabe!** 🧠⚡
