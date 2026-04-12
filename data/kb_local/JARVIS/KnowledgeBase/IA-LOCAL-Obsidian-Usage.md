---
title: "IA-LOCAL Obsidian Usage"
description: "Guia de configuração e uso do vault Obsidian clonado para o IA-LOCAL."
tags:
  - obsidian
  - jarvis
  - vault
  - ia-local
  - configuration
---

# IA-LOCAL Obsidian Usage

Este documento apresenta como usar o vault Obsidian clonado em `obsidian_clone` com o projeto IA-LOCAL.

## Estrutura recomendada

O vault clonado deve ser usado como uma cópia local legível pelo agente.

- `obsidian_clone/` é a cópia do vault original
- O projeto IA-LOCAL lê os arquivos `*.md` dentro desse diretório
- Não é necessário modificar o vault original para testar o agente local

## Onde colocar as notas IA-LOCAL

Recomenda-se criar notas em:

- `JARVIS/KnowledgeBase/` para conhecimento do agente
- `JARVIS/Aprendizado/` para evolução e aprendizado contínuo
- `JARVIS/Memorias/` para fatos importantes e histórico ativo

## Como o agente ingere o conteúdo

1. O `ObsidianVault` localiza todos os arquivos Markdown no vault.
2. O conteúdo de cada nota é carregado como texto puro.
3. O texto é dividido em chunks menores para memorização.
4. Cada chunk é adicionado ao `MemoryManager` como memória do tipo `knowledge`.

## Recomendações de organização

- Use títulos claros com `#`, `##`, `###`.
- Crie páginas de resumo para áreas importantes:
  - `IA-LOCAL-Local-Agent.md`
  - `IA-LOCAL-Configuration.md`
  - `IA-LOCAL-Workflow.md`
- Use tags e metadados YAML para classificar conteúdos.

## Ações que podem ser adicionadas

- Registrar decisões do agente em `JARVIS/Decisoes/`.
- Criar planos e objetivos em `JARVIS/Projetos/`.
- Usar `JARVIS/Contexto-Atual/` para anotações de contexto de execução.

## Próximos upgrades

- Adicionar um módulo de escrita para criar novas notas a partir de prompts de IA.
- Implementar um índice de notas recentes para acelerar buscas.
- Separar notas de configuração, ideias e ações do agente.
