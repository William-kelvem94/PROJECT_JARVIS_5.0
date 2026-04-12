---
title: "PROJECT_JARVIS_5.0 Second Brain"
description: "Definição e regras do segundo cérebro do Jarvis, incluindo ingestão de conhecimento e prioridades de uso." 
tags:
  - jarvis
  - second-brain
  - knowledge
  - ingestion
---

# PROJECT_JARVIS_5.0 Second Brain

Esta nota define o segundo cérebro do Jarvis e como ele deve consumir todo o conteúdo da pasta `PROJECT_JARVIS_5.0-KnowledgeBase`.

## O que é o segundo cérebro
- É a fonte de verdade do Jarvis para conhecimento, persona, arquitetura, estratégia e casos de uso.
- Não é apenas uma coleção de notas; é o contexto usado em tempo real pelo assistente.
- O segundo cérebro está em:
  `D:\OBSIDIAN\Will\Projetos\Privados\PROJECT_JARVIS_5.0-KnowledgeBase`

## O que Jarvis deve consumir
- Todas as notas Markdown (`*.md`) dentro de `PROJECT_JARVIS_5.0-KnowledgeBase`.
- Prioridade:
  1. `PROJECT_JARVIS_5.0-Knowledge.md`
  2. `PROJECT_JARVIS_5.0-Personality.md`
  3. `PROJECT_JARVIS_5.0-Architecture.md`
  4. `PROJECT_JARVIS_5.0-Strategy.md`
  5. `PROJECT_JARVIS_5.0-UseCases.md`
  6. `PROJECT_JARVIS_5.0-Tools.md`
  7. `PROJECT_JARVIS_5.0-Integration.md`
  8. `PROJECT_JARVIS_5.0-SecondBrain.md`
  9. `PROJECT_JARVIS_5.0-Map.md`
  10. `PROJECT_JARVIS_5.0.md`
  11. `PROJECT_JARVIS_5.0-README/INDEX/CONFIG/RULES`

## Porque esta pasta importa
- Ela é o segundo cérebro do Jarvis e deve estar alinhada com o código em `C:\Users\willi\Documents\GitHub\PROJECT_JARVIS_5.0`.
- O código local deve usar `JARVIS_KB_PATH` para carregar o conhecimento.
- Qualquer duplicata fora desta pasta deve ser tratada como referência ou histórico, não como verdade principal.

## Como organizar a ingestão
- Leia e normalize todos os arquivos Markdown.
- Use embeddings e RAG para cada documento.
- Marque a prioridade de cada nota e use a ordem para montar o prompt base.
- Reindexar sempre que `RULES.md`, `INDEX.md`, `CONFIG.md` ou qualquer documento estratégico mudar.

## Regras do segundo cérebro
- Mantenha apenas um caminho canônico para o conhecimento: esta pasta.
- Crie novas notas com prefixo `PROJECT_JARVIS_5.0-`.
- Atualize `INDEX.md` sempre que adicionar ou remover páginas.
- Use `RULES.md` para manter consistência.
- Trate `PROJECT_JARVIS_5.0-KnowledgeBase` como o local que Jarvis deve consultar primeiro.

## Nota para o código
- `JARVIS_KB_PATH` deve apontar para `D:\OBSIDIAN\Will\Projetos\Privados\PROJECT_JARVIS_5.0-KnowledgeBase`
- `JARVIS_PROJECT_ROOT` deve apontar para `C:\Users\willi\Documents\GitHub\PROJECT_JARVIS_5.0`
- O Jarvis deve carregar a pasta inteira como `secondBrain` antes de executar ações.
