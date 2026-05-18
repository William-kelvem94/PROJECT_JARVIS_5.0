# Inteligência Híbrida — SmartRouter

## Visão Geral

O `smart_router.py` decide qual modelo LLM usar baseado na complexidade da query.

## Modos Cognitivos

| Modo | Gatilho | Modelo | Latência |
|------|---------|--------|----------|
| **Rápido** | Queries factuais, comandos simples | Local (LM Studio/Ollama) | Baixa |
| **Profundo** | Análises, refatoração, planejamento | Nuvem (Gemini/OpenRouter) | Média |

## Hierarquia de Modelos

```
1. Gemini 2.5 Flash (Primário Nuvem) — alta complexidade
2. LM Studio (Primário Local) — baixa latência, privacidade
3. Ollama (Secundário Local) — redundância
4. OpenRouter (Failover Final) — múltiplos modelos
```

## Critérios de Classificação

- **Token count** → Gemini para contextos > 8k tokens
- **Keywords** ("analise", "otimize", "planeje") → Pensamento Profundo
- **Hardware state** → redireciona se GPU > 90%

## Referência
- `docs/archive/research/PROJECT_SOPHISTICATION/docs/inteligencia_hibrida.md`
