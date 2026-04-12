---
title: "Jarvis Knowledge Base Integration"
description: "Guia de integração entre a base de conhecimento do Jarvis e o código real do projeto." 
tags:
  - jarvis
  - privados
  - integration
  - knowledge
  - config
---

# Jarvis Knowledge Base Integration

Esta nota descreve como o Jarvis deve integrar a base de conhecimento localizada em `D:\OBSIDIAN\Will\Projetos\Privados\PROJECT_JARVIS_5.0-KnowledgeBase` com o código real do projeto em `C:\Users\willi\Documents\GitHub\PROJECT_JARVIS_5.0`.

- Esta pasta é o segundo cérebro canônico do Jarvis.
- Jarvis deve carregar cada arquivo `.md` dessa pasta como parte do seu conhecimento runtime.

## Objetivo
- Fazer o Jarvis ler e usar a inteligência desta pasta como seu segundo cérebro.
- Manter a separação entre conhecimento e implementação.
- Garantir que o projeto saiba onde estão as notas e como carregá-las no runtime.

## Caminhos e variáveis de ambiente
- `JARVIS_KB_PATH`: caminho para a base de conhecimento.
  - `D:\OBSIDIAN\Will\Projetos\Privados\PROJECT_JARVIS_5.0-KnowledgeBase`
- `JARVIS_PROJECT_ROOT`: caminho para o código real do Jarvis.
  - `C:\Users\willi\Documents\GitHub\PROJECT_JARVIS_5.0`
- `JARVIS_VAULT_ROOT`: raiz do vault Obsidian.
  - `D:\OBSIDIAN\Will`

## Como integrar no código
1. No startup do Jarvis, leia `JARVIS_KB_PATH`.
2. Liste todos os arquivos Markdown `*.md` dentro da pasta.
3. Normalize e remova metadados YAML se necessário.
4. Gere embeddings com o mesmo modelo usado pelo Jarvis.
5. Armazene o índice em FAISS ou outro vetorstore local.
6. Use recuperação por similaridade em queries de usuário.

## Principais componentes de integração
- `loader` de documentos: converte Markdown em texto quebrado por parágrafos.
- `embeddings`: cria vetores baseados nos conteúdos da KB.
- `retriever`: busca trechos relevantes para responder perguntas ou guiar ações.
- `prompt builder`: insere descrições da persona, arquitetura e estratégia.

## Recomendações
- Leia primeiro `PROJECT_JARVIS_5.0-Personality.md` para definir o tom.
- Use `PROJECT_JARVIS_5.0-Architecture.md` e `PROJECT_JARVIS_5.0-Strategy.md` como contexto de alto nível.
- Priorize respostas baseadas em `PROJECT_JARVIS_5.0-Knowledge.md` quando houver dúvida técnica.

## Sincronização e manutenção
- Se um documento for alterado, reindexe a KB.
- Mantenha a pasta `PROJECT_JARVIS_5.0-KnowledgeBase` atualizada com o estado real do projeto.
- Use `RULES.md` para criar novos tópicos e evitar duplicação.

## Notas de implementação
- O código de Jarvis não deve copiar a pasta inteira para dentro do repositório.
- Em vez disso, use variáveis de ambiente para apontar o runtime ao caminho do KB.
- O projeto `C:\Users\willi\Documents\GitHub\PROJECT_JARVIS_5.0` deve carregar o conhecimento dinamicamente.
