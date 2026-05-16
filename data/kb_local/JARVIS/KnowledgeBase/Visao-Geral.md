---
title: "PROJECT_JARVIS_5.0 (Knowledge Base)"
description: "Cópia da visão geral do projeto Jarvis para a base de conhecimento." 
tags:
  - jarvis
  - knowledge
  - project
---

# PROJECT_JARVIS_5.0 (Knowledge Base)

**Private Clone | FastAPI/Next.js | Atualizado 16h ago**

Ecossistema Jarvis: voz real-time (WebSocket nativo), LLMs (OpenAI/Ollama), visão face/gesture/voice (MediaPipe), browser Playwright autonomy, dashboard monitoring.

**Estrutura**:
- `backend/` (app/main.py, app/multi_agent_analysis.py)
- `frontend/` (Next.js shadcn Tailwind, agent-audio-visualizer)
- `docker/`, scripts monitor-heartbeat.ps1, start-jarvis.bat

**Run**: `start-jarvis.bat`

## Execução e implementação
- O clone contém o monorepo de Jarvis completo, dividido entre backend, frontend, agentes e scripts de deploy.
- O ponto de partida atual é o `start-jarvis.bat`, mas é preciso documentar e versionar os comandos de desenvolvimento individuais.
- O foco imediato deve ser:
  - validar o fluxo de voz e TTS;
  - testar os serviços de visão com MediaPipe/YOLOv8;
  - estabilizar a orquestração de agentes via middleware nativo.

## Base de conhecimento e arquitetura
- [[PROJECT_JARVIS_5.0-Knowledge|Base de Conhecimento Jarvis]]
- [[PROJECT_JARVIS_5.0-Personality|Persona Jarvis]]
- [[PROJECT_JARVIS_5.0-Architecture|Arquitetura Jarvis]]
- [[PROJECT_JARVIS_5.0-Strategy|Estratégia Jarvis]]

## Status técnico
- Backend: `backend/app/main.py` (agents_worker.py removido).
- Frontend: `frontend/` com Next.js shadcn e interfaces de agente.
- Orquestração: scripts em `docker/`, monitor-heartbeat e `start-jarvis.bat`.
- Dependências principais: Playwright, MediaPipe, modelos LLM, Node.js/React.

## Roadmap de implementação
1. Documentar o conjunto de serviços e seus papéis.
2. Criar um diagrama simples de fluxos de voz, visão e agentes.
3. Estabelecer os scripts de desenvolvimento para cada serviço.
4. Validar integração básica de backend + frontend.
5. Definir prova de conceito de visão leve e automação do browser.

## Riscos de execução
- O workspace pode ficar pesado se todos os serviços forem executados juntos.
- A automação via Playwright exige cuidado com foco de tela e estado do browser.
- O uso de modelos externos (Gemini/OpenAI) no backend aumenta custo e risco de dependência.

## Próximos passos específicos
- Extrair e documentar os comandos de `backend/`, `frontend/` e `docker/`.
- Criar uma checklist de setup local para novo desenvolvedor.
- Registrar o estado atual do modelo de voz e do modelo de visão.

**Links**: [[GitHub-Completo]] #mediapipe #fastapi
