# JARVIS 5.0 — API Reference

> Documentação automática dos endpoints REST da API FastAPI.

## Base URL
- Backend: `http://localhost:8000`
- Telemetry: `http://localhost:8001`

## Endpoints Principais

### `GET /health`
Retorna status do sistema e métricas de hardware/percepção.

### `POST /chat`
Envia mensagem para o pipeline de IA.

### `GET /memory`
Recupera memórias do usuário.

### `GET /screenshots`
Lista screenshots recentes.

### `GET /vault-stats`
Estatísticas do vault Obsidian.

### `POST /vault-memory`
Salva memória episódica no vault.

### `POST /notes`
Cria nota rápida no vault.

### `GET /logs`
Lista datas de logs disponíveis.

### `GET /logs/{date}`
Retorna logs de uma data específica.

### `GET /telemetry/status`
Telemetria completa do sistema.

### `GET /telemetry/history`
Histórico de telemetria.

### `GET /system/capabilities`
Status de todos os componentes monitorados.

### `GET /system/hardware`
Status específico de hardware (câmera, mic, tela).

### `GET /agents/summary`
Resumo de todos os agentes de análise.

### `GET /agents/findings`
Findings dos agentes (opcional: ?severity=high).

### `GET /agents/critical`
Apenas findings críticos/altos.

## Endpoints WebSocket

### `WS /ws/voice`
Conexão bidirecional para telemetria do HUD de voz.

## Endpoints do Sistema (System Bridge)

### `GET /system/volume`
### `POST /system/volume`
### `GET /system/brightness`
### `POST /system/brightness`
### `GET /system/screenshot`
### `GET /system/status`
