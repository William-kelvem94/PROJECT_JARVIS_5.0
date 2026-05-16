# JARVIS 5.0 — Índice de Troubleshooting

> Centraliza todas as guias de resolução de problemas.

## Problemas e Soluções

| Problema | Guia | Prioridade |
|----------|------|------------|
| Setup inicial / primeira execução | [JARVIS_STARTUP.md](guides/JARVIS_STARTUP.md) | ⭐ |
| Quick-fix de 5 minutos | [QUICKFIX_GUIDE.md](guides/QUICKFIX_GUIDE.md) | ⭐ |
| Hardware / câmera / áudio | [HARDWARE_FIX.md](guides/HARDWARE_FIX.md) | ⭐ |
| Conectividade / ECONNRESET | [CONNECTIVITY_README.md](guides/CONNECTIVITY_README.md) | ⭐ |
| Sistema de saúde / agentes | [HEALTH_SYSTEM_README.md](guides/HEALTH_SYSTEM_README.md) | ⭐ |
| Auto-fix agents | [AUTOFIX_README.md](guides/AUTOFIX_README.md) | ⭐ |
| Soluções detalhadas por issue | [SOLUTIONS_FOR_REPORTED_ISSUES.md](SOLUTIONS_FOR_REPORTED_ISSUES.md) | 📘 |
| Correção de conectividade (técnico) | [CONNECTIVITY_FIX.md](CONNECTIVITY_FIX.md) | 📘 |

## Diagnóstico Rápido

1. Execute `scripts\fix-critical.bat` para correção automática
2. Verifique se o backend está online: `curl http://localhost:8000/health`
3. Verifique os logs em tempo real no painel de telemetria: `http://localhost:8001`
4. Consulte o status dos agentes: `curl http://localhost:8000/agents/summary`
