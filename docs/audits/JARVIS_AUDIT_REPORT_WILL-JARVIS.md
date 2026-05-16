# JARVIS Audit Report — branch WILL-JARVIS

## Escopo
Auditoria read-only do repositório clonado em `/home/willi/.openclaw/workspace/jarvis_repo` na branch `WILL-JARVIS`.

## Resumo executivo
O projeto é um monorepo híbrido com frontend Next.js e backend FastAPI, mas está em estado irregular: há divergências entre docs e código, rotas duplicadas, testes quebrados por conflito de merge, e riscos relevantes de segurança por dados sensíveis versionados e endpoints sem autenticação. O repo parece funcional em partes, mas ainda não está confiável como base estável.

## Visão geral da arquitetura
- Frontend: `frontend/` (Next.js 15 / React)
- Backend: `backend/` (FastAPI, roteamento LLM, memória, percepção, voz)
- Config central: `config/`
- Documentação: `docs/`
- Scripts operacionais: `scripts/`, `start*.bat`, `docker-compose.yml`

Fluxo aparente:
UI → HTTP/WebSocket → backend → roteador LLM/memória/percepção/voz → telemetria/estado de volta à UI.

## Achados críticos

### 1) Dados sensíveis versionados no repositório
- Evidência: `data/kb_local/**`, `backend/data/**`, `data/memories.json`, `backend/data/jarvis_local.db`, logs e notas pessoais.
- Impacto: exposição de histórico, contexto local, possivelmente caminhos e dados privados.
- Severidade: **Crítico**

### 2) Endpoints locais sem autenticação visível
- Evidência em `backend/app/routes.py` e `backend/app/system_bridge.py`:
  - `/memory`, `/logs`, `/logs/{date}`, `/screenshots`, `/screenshots/{filename}`, `/vault-memory`
  - `/system/volume`, `/system/brightness`, `/system/screenshot`, `/system/status`
- Impacto: se o backend sair do localhost, vira vazamento/controle remoto.
- Severidade: **Crítico**

## Achados altos

### 3) Execução de shell com `shell=True`
- Evidência: `backend/app/tools/system_executor.py`, `backend/app/tools/ai_tools.py`
- Impacto: superfície de comando frágil; whitelist ajuda, mas não elimina risco.
- Severidade: **Alta**

### 4) Variáveis sensíveis carregadas do ambiente
- Evidência: `backend/app/config.py` usa `GEMINI_API_KEY`, `OPENROUTER_API_KEY` etc.
- Impacto: risco operacional se `.env`/logs forem versionados ou expostos.
- Severidade: **Alta**

### 5) Frontend com rota de voice WebSocket divergente do backend
- Evidência: `frontend/.env.example`, `frontend/lib/context/jarvis-context.tsx` usam `ws://.../ws/voice-stream`; backend expõe `/ws/voice`.
- Impacto: conexão padrão quebra quando env não é definido.
- Severidade: **Alta**

## Achados médios

### 6) Testes quebrados por conflito de merge
- Evidência: `backend/tests/test_routes.py` contém `<<<<<<< HEAD` / `>>>>>>> main`.
- Impacto: `SyntaxError`, suíte não coleta esse arquivo.
- Severidade: **Média/Alta**

### 7) Imports/pacote inconsistentes nos testes
- Evidência: uso misto de `backend.app...` e `app...`.
- Impacto: falhas dependendo do `sys.path`.
- Severidade: **Média**

### 8) Rotas duplicadas e contrato inconsistente
- Evidência: `backend/app/main.py` e `backend/app/routes.py` duplicam `POST /chat`; `/health` diverge entre código e testes.
- Impacto: comportamento ambíguo e CI frágil.
- Severidade: **Média**

### 9) HUD pode ficar preso em “speaking”
- Evidência: `frontend/app/page.tsx` mantém `status === "speaking"` mesmo quando há resposta
- Impacto: UI pode parecer travada após a primeira resposta
- Severidade: Média

### 10) Polling agressivo
- Evidência: polling de `/health`, `/api/status`, `/logs/{date}` a cada 5s sem verificação de visibilidade
- Impacto: carga/ruído desnecessário
- Severidade: Média

## Achados de documentação/operação

### 11) Docs e scripts discordam sobre fluxo de inicialização
- Evidência: `README.md`, `docs/guides/JARVIS_STARTUP.md`, `docs/INSTALL.md`, `scripts/launch-backend.bat`, `scripts/run-backend.sh`
- Impacto: fácil seguir o caminho de setup errado
- Severidade: Média

### 12) Caminho do script de inicialização do backend parece errado
- Evidência: `scripts/launch-backend.bat` verifica `..\..\.venv\Scripts\activate.bat` após `cd backend`
- Impacto: inicialização pode falhar mesmo com venv válido
- Severidade: Média

### 13) Scripts shell usam caminhos de módulo inconsistentes
- Evidência: `scripts/run-backend.sh` usa `backend.app.main:app` enquanto o código expõe `app.main:app`
- Impacto: fragilidade operacional
- Severidade: Média

## Prioridades recomendadas

### P1
- Remover conflito de merge em `backend/tests/test_routes.py`
- Corrigir inconsistências de import-path nos testes
- Consolidar `/chat` e `/health` em um único contrato
- Corrigir incompatibilidade de rota WS de voz

### P2
- Remover dados sensíveis versionados / DB local / artefatos de browser
- Adicionar autenticação/proteções a endpoints de controle local
- Revisar uso de `shell=True` e restringir execução de comandos

### P3
- Alinhar docs e scripts com o fluxo de inicialização real
- Reduzir polling agressivo no frontend
- Normalizar nomenclatura/versionamento no repositório

**Arquivo salvo**: `/home/willi/.openclaw/workspace/jarvis_repo/JARVIS_AUDIT_REPORT_WILL-JARVIS.txt`

---

> **Nota**: Este arquivo estava truncado originalmente. O conteúdo completo foi restaurado a partir da versão `.txt`. 