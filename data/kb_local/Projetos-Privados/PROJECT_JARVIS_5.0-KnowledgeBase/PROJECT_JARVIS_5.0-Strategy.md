---
title: "PROJECT_JARVIS_5.0 Strategy"
description: "Estratégia do Jarvis duplicada para a base de conhecimento dedicada." 
tags:
  - jarvis
  - privados
  - strategy
  - assistant
---

# PROJECT_JARVIS_5.0 Strategy

Esta nota é a cópia da estratégia do Jarvis para a base de conhecimento dedicada.

## Missão do projeto
Criar um assistente multimodal que combine voz em tempo real, visão de ambiente e execução de tarefas para oferecer um Jarvis autônomo de uso pessoal e profissional.

## Proposta de valor
- Para o usuário: controle mais natural do computador com voz e visão.
- Para o produto: provar um agente que pode ser executado localmente ou em uma infraestrutura híbrida.
- Para o vault: elevar o nível de Jarvis para multimodalidade real e integração com desktop.

## Público e cenários
**Usuário primário**
- Produtores de conteúdo, desenvolvedores e power users que precisam de um assistente PC mais avançado.

**Cenários**
- ditado e comandos por voz com feedback visual.
- reconhecimento de gestos/face para contexto de interação.
- automação de browser e workflows com LiveKit e Playwright.

## Métricas de sucesso
- Latência de voz < 1.5s em fluxo local.
- Reconhecimento de gesto/face estável em 70% dos casos.
- Execução autônoma de workflow sem falha em 85%.
- Redução de interação manual em fluxos de 3 tarefas.

## Hipóteses-chave
- A multimodalidade é o diferencial competitivo do Jarvis.
- LiveKit é a escolha certa para voz em tempo real neste MVP.
- É viável usar YOLOv8 nano para visão leve em hardware comum.
- O browser automation pode ser confiável com Playwright e scripts robustos.

## Situação atual
- Stack atual: FastAPI, Next.js, LiveKit, MediaPipe e Playwright.
- Problemas principais: dependência Gemini e falta de stack offline consolidado.
- Gap técnico: não há claro pipeline de produção para agentes.

## Arquitetura estratégica
- `backend/` = agentes, inferência LLM, integração de visão e voz.
- `frontend/` = dashboard Next.js com visualização e controles.
- `agents/` = workers gRPC, orchestrator e plan.
- `vision/` = MediaPipe, YOLOv8 e OCR de tela.
- `audio/` = LiveKit, Piper TTS e voz em tempo real.

## Roadmap estratégico
### Fase 1 — MVP offline multimodal (4 semanas)
- Implementar backend Ollama local e Piper TTS.
- Adicionar visão leve com YOLOv8 nano.
- Validar fluxo de voz + detecção de objeto.
- Criar protótipo de dashboard e log.

### Fase 2 — Produção e agentes (8 semanas)
- Preparar Docker Swarm local para múltiplos serviços.
- Criar gRPC agents e integração com VSCode extension.
- Padronizar monitoramento e estado de agentes.

### Fase 3 — Autonomia e workflows (16 semanas)
- Construir LangGraph ou orquestração semelhante.
- Adicionar OCR de tela e parsing de comandos.
- Testar workflows autônomos e devolutiva de status.

## Dependências e decisões
- Voz: LiveKit vs Piper + stream local.
- Modelo: Gemini como fallback ou não?
- Visão: MediaPipe + YOLOv8 vs modelo heavier.
- Automação: Playwright no desktop vs browser headless.

## Riscos
- Hardware exigente para multimodalidade.
- Complexidade elevada ao combinar voz, visão e agents.
- Dependência de Gemini encarece o produto.
- Automação de browser é frágil e depende de foco/estado.

## Decisões pendentes
- Priorizar offline total ou usar arquitetura híbrida?
- Lançar funcionalidade de visão primeiro ou voz primeiro?
- Quais agentes devem ser autônomos e quais acionados manualmente?

## Diário de Bordo
- 09/04/2026 10:56:11 — nota criada com versão inicial de estratégia.
- 09/04/2026 10:56:14 — roadmap multimodal definido.

## Próximas ações imediatas
- Confirmar o fluxo de voz em LiveKit e Piper.
- Testar YOLOv8 nano em hardware alvo.
- Definir arquitetura de agentes e gRPC.
- Documentar cenário de uso e critério de aceitação.

## Referências
- [[../EstudosPesquisas/PROJECT_JARVIS_5.0|Pesquisa PROJECT_JARVIS_5.0]]
- [[../EstudosPesquisas/AI-Local-Gratuita|AI Local Gratuita]]
- [[../Plano-de-Acao|Plano de Ação]]
