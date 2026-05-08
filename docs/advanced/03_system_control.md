# Soberania de Hardware — OS-Controller

## Visão Geral

O JARVIS tem controle nativo do sistema operacional via `system_control.py` e `system_bridge.py`.

## SystemControlMatrix (`system_control.py`)

| Funcionalidade | Método | Plataforma |
|----------------|--------|------------|
| Volume master | `set_volume(level)` | Windows (pycaw) |
| Brilho da tela | `set_brightness(level)` | Windows |
| Captura de telas | `capture_screens()` | Cross-platform (mss) |
| Status de hardware | `get_hardware_status()` | Cross-platform (psutil) |

## SystemBridge (`system_bridge.py`)

API REST para o LLM enviar comandos de hardware:
```
POST /system/volume        → Ajusta volume (0.0–1.0)
POST /system/brightness    → Ajusta brilho (0–100)
GET  /system/screenshot    → Captura todos os monitores
GET  /system/status        → Telemetria + consciência espacial
```

## Consciência Espacial

| Estado | CPU | RAM | Comportamento |
|--------|-----|-----|---------------|
| Ocioso | <50% | <90% | Resposta instantânea |
| Equilibrado | 50–85% | <90% | Operação nominal |
| Sobrecarga | ≥85% | ≥90% | Prioriza críticos |

## Referência
- `docs/archive/research/OMEGA_RESEARCH/docs/system_control.md`
- `docs/archive/research/OMEGA_RESEARCH/docs/system_powers.md`
