---
title: "PROJECT_JARVIS_5.0 (Clonado)"
source: "C:/Users/willi/Documents/GitHub/PROJECT_JARVIS_5.0"
language: Python
private: true
description: "Jarvis 5.0 monorepo FastAPI + Next.js + LiveKit voice AI, visão face/gesture, browser autonomy."
updated: "16h ago"
tags:
  - projetos
  - privados
  - privados
  - python
  - nextjs
  - livekit
  - ai-vision
---

# PROJECT_JARVIS_5.0 [[../Projetos.md|Projetos]] [[GitHub-Completo]]

**Private Clone | FastAPI/Next.js | Atualizado 16h ago**

Ecossistema Jarvis: voz real-time, Gemini/OpenAI, visão face/gesture/voice (MediaPipe), browser Playwright autonomy, dashboard monitoring.

**Estrutura**:
- `backend/` (agents_worker.py, app/main.py)
- `frontend/` (Next.js shadcn Tailwind, agent-audio-visualizer)
- `docker/`, scripts monitor-heartbeat.ps1, start-jarvis.bat

**Run**: `start-jarvis.bat`

## Execução e implementação
- O clone contém o monorepo de Jarvis completo, dividido entre backend, frontend, agentes e scripts de deploy.
- O ponto de partida atual é o `start-jarvis.bat`, mas é preciso documentar e versionar os comandos de desenvolvimento individuais.
- O foco imediato deve ser:
  - validar o fluxo de voz e TTS;
  - testar os serviços de visão com MediaPipe/YOLOv8;
  - estabilizar a orquestração de agentes via gRPC ou outro middleware.

## Base de conhecimento e arquitetura
- [[PROJECT_JARVIS_5.0-KnowledgeBase/README|Knowledge Base do Jarvis]]
- [[PROJECT_JARVIS_5.0-Knowledge|Base de Conhecimento Jarvis]]
- [[PROJECT_JARVIS_5.0-Personality|Persona Jarvis]]
- [[PROJECT_JARVIS_5.0-Architecture|Arquitetura Jarvis]]
- [[PROJECT_JARVIS_5.0-Strategy|Estratégia Jarvis]]
- [[PROJECT_JARVIS_5.0-KnowledgeBase/PROJECT_JARVIS_5.0-SecondBrain|Segundo Cérebro do Jarvis]]
- [[PROJECT_JARVIS_5.0-KnowledgeBase/PROJECT_JARVIS_5.0-Integration|Integração da KB com projeto]]
- [[PROJECT_JARVIS_5.0-KnowledgeBase/PROJECT_JARVIS_5.0-UseCases|Use Cases do Jarvis]]
- [[PROJECT_JARVIS_5.0-KnowledgeBase/PROJECT_JARVIS_5.0-Tools|Ferramentas do Jarvis]]
- [[PROJECT_JARVIS_5.0-KnowledgeBase/PROJECT_JARVIS_5.0-Map|Mapa da KB do Jarvis]]
- [[PROJECT_JARVIS_5.0-KnowledgeBase/INDEX|Índice da KB do Jarvis]]
- [[PROJECT_JARVIS_5.0-KnowledgeBase/RULES|Regras da KB do Jarvis]]
- [[PROJECT_JARVIS_5.0-KnowledgeBase/CONFIG|Configuração da Knowledge Base]]
- `PROJECT_JARVIS_5.0-KnowledgeBase` é o segundo cérebro canônico do Jarvis; o assistente deve consumir esta pasta primeiro.

## Configuração do Jarvis
- Base de conhecimento oficial: `D:\OBSIDIAN\Will\Projetos\Privados\PROJECT_JARVIS_5.0-KnowledgeBase`
- Pasta real do projeto de código: `[PROJECT_ROOT]`
- Vault raiz de organização: `D:\OBSIDIAN\Will`
- Sugestão de variável de ambiente:
  - `JARVIS_KB_PATH=D:\OBSIDIAN\Will\Projetos\Privados\PROJECT_JARVIS_5.0-KnowledgeBase`
  - `JARVIS_PROJECT_ROOT=[PROJECT_ROOT]`
  - `JARVIS_VAULT_ROOT=D:\OBSIDIAN\Will`

> Nota: Esta pasta de Knowledge Base é a consciência do Jarvis. O código do projeto vive em `[PROJECT_ROOT]`.

## Status técnico
- Backend: `backend/agents_worker.py`, `backend/app/main.py`.
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
- O uso de Gemini no backend aumenta custo e risco de dependência.

## Próximos passos específicos
- Extrair e documentar os comandos de `backend/`, `frontend/` e `docker/`.
- Criar uma checklist de setup local para novo desenvolvedor.
- Registrar o estado atual do modelo de voz e do modelo de visão.

**Links**: [[GitHub-Completo]] #mediapipe #fastapi
