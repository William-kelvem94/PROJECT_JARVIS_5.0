---
title: "Índice de Decisões — Jarvis"
description: "Decisões importantes registradas com contexto, data e raciocínio."
tags: [jarvis, decisoes, historico]
  - decisao
updated: 2026-04-09
---

# Índice de Decisões — Jarvis

> Quando Will ou o Jarvis tomam uma decisão importante sobre um projeto, arquitetura ou caminho de vida, registra-se aqui.
> Serve para não repetir discussões já resolvidas e entender o "porquê" de cada escolha.

## 📋 Formato de uma Decisão

```markdown
## [YYYY-MM-DD] Título da Decisão
- **Projeto/Contexto:** nome do projeto ou área
- **Decisão:** o que foi decidido (uma linha)
- **Alternativas consideradas:** o que mais foi cogitado
- **Raciocínio:** por que esta opção foi escolhida
- **Impacto:** consequências esperadas
- **Status:** Ativa | Revisada | Cancelada
```

## 🗂️ Decisões Registradas

### [2026-04-09] Vault Obsidian como segundo cérebro do Jarvis
- **Projeto/Contexto:** PROJECT_JARVIS_5.0
- **Decisão:** Usar `D:\OBSIDIAN\Will\JARVIS\` como estrutura de memória persistente do Jarvis
- **Alternativas consideradas:** Somente SQLite, somente Mem0 cloud
- **Raciocínio:** Obsidian é editável pelo Will, legível por humanos, versionável e indexável. Combina com a filosofia de segundo cérebro. O SQLite continua como cache local rápido.
- **Impacto:** Jarvis grava memórias em .md após cada sessão; carrega contexto rico no startup
- **Status:** Ativa

### [2026-04-09] vault_memory.py como módulo escritor
- **Projeto/Contexto:** PROJECT_JARVIS_5.0 backend
- **Decisão:** Criar `backend/app/vault_memory.py` dedicado para escrever memórias no vault
- **Alternativas consideradas:** Escrever direto no kb_loader, usar apenas SQLite
- **Raciocínio:** Separação de responsabilidades — kb_loader lê, vault_memory escreve
- **Impacto:** Memórias persistem entre reinicializações do backend, visíveis no Obsidian
- **Status:** Ativa
