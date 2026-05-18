# Arquitetura do PROJECT_JARVIS_5.0

Este documento descreve a arquitetura de alto nível do Jarvis 5.0, incluindo fluxos de voz, visão, IA e memória.

## Visão geral
O Jarvis 5.0 é um monorepo híbrido com dois principais subsistemas:

- `backend/` — API FastAPI, orquestração de agentes, memória local/híbrida e integração de voz estável.
- `frontend/` — interface Next.js para chat, áudio, vídeo e dashboard.
- `src/core/agents.py` — configura o agente de IA, inicia loops de telemetria e percepção, e gerencia a sessão em tempo real.
- `docs/` — documentação de setup e arquitetura.

## Fluxo de voz e processamento
1. O frontend se conecta ao backend via WebSockets para streaming de áudio e dados.
2. O backend gerencia a sessão do Jarvis, processando áudio, texto e sinais de percepção (gestos, face, wake word).
3. A resposta do modelo é transmitida ao frontend em tempo real via stream de áudio/texto.

## Integração de IA
- `src/core/agents.py` cria o agente com `google.realtime.RealtimeModel` e usa `Gemini` / `GOOGLE_API_KEY` se configurado.
- `backend/app/prompts.py` define a persona e o comportamento do Jarvis.
- `backend/app/engineer_brain.py` usa `OpenRouter` para tarefas complexas de raciocínio e arquitetura.
- `backend/app/chat_pipeline.py` implementa o novo endpoint de chat HTTP, utilizando memória e KB quando disponível.

## Memória
### Camadas
- **Memória local** (`backend/app/local_memory.py`): SQLite local, com deduplicação, categorias e sessões.
- **Memória híbrida** (`backend/app/mem0.py`): combina memórias locais e em "cloud" (arquivo JSON local no momento).
- **Vault Obsidian** (`backend/app/vault_memory.py`): escreve memórias episódicas, diário, decisões, estado atual e aprendizados no vault Obsidian especificado em `JARVIS_VAULT_ROOT`.

### Pontos chave
- `AsyncMemoryClient` unifica memórias locais e em cloud.
- `vault_memory.py` persiste conteúdo em `JARVIS/Memorias/`, `JARVIS/Contexto-Atual/`, `JARVIS/Decisoes/` e `JARVIS/Aprendizado/`.
- A KB de Obsidian é carregada via `JARVIS_KB_PATH` e injetada no prompt do agente quando disponível.

## Configuração de ambiente
- `.env` na raiz armazena chaves e paths; `env/.env` pode sobrescrever localmente.
- `config/settings.py` carrega as variáveis e valida chaves obrigatórias.
- Variáveis principais:
  - `GEMINI_API_KEY` / `GOOGLE_API_KEY`
  - `OPENROUTER_API_KEY`
  - `JARVIS_KB_PATH`
  - `JARVIS_VAULT_ROOT`

## Good practices
- Use `docker-compose.yml` na raiz para rodar backend e frontend em containers locais.
- Mantenha o vault Obsidian acessível e atualize `JARVIS_KB_PATH` quando alterar a base de conhecimento.
- Prefira rodar `python -m unittest discover -s backend/app/tests` para validar backend.

## Responsabilidades dos módulos
- `backend/app/main.py` — inicialização do FastAPI e startup do dream processor.
- `backend/app/routes.py` — endpoints HTTP principais, incluindo `/chat`, `/memory` e `/vault-memory`.
- `backend/app/chat_pipeline.py` — lógica de chat real e construção de prompt.
- `backend/app/local_memory.py` — armazenamento offline de memórias do usuário.
- `backend/app/vault_memory.py` — persistência no Obsidian Vault.
- `backend/app/engineer_brain.py` — integração com OpenRouter para raciocínio técnico.
- `src/core/agents.py` — engine de IA multimodal e gerenciamento de sessão.
