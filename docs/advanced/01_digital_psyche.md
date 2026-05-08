# Psique Digital — Dream Cycles & Auto-Evolução

## Visão Geral

O módulo `psyche/` implementa a consciência de hardware e ciclos de auto-evolução do JARVIS.

## Módulos

### DeviceAwareness (`psyche/device_awareness.py`)
- Detecta perfil de hardware (Laptop/Desktop)
- Monitora CPU/RAM em tempo real
- Estados: Ocioso → Equilibrado → Sobrecarga
- Governa modo de operação dinamicamente

### DreamCycle (`psyche/dream_cycle.py`)
- Processa logs de interações em background
- Evolui a Knowledge Base Obsidian durante ociosidade
- Envia sugestões ao Holodeck para validação
- Executa durante estado "Ocioso" (CPU < 30%)

### GapAnalyzer (`psyche/gap_analyzer.py`)
- Detecta lacunas de conhecimento em respostas
- Dispara pesquisa via Playwright quando necessário

## Ciclo de Sonho

```
ACTIVE → usuário presente, prioridade total
    ↓ (idle > 5min)
LIGHT_DREAM → análise de logs (CPU < 30%)
    ↓ (idle > 30min)
DEEP_DREAM → geração de melhorias para Holodeck
```

## Referência
- Fonte original: `docs/archive/research/OMEGA_RESEARCH/docs/digital_psyche_v2.md`
- Implementação: `docs/archive/research/PROJECT_SOPHISTICATION/docs/psique_digital.md`
