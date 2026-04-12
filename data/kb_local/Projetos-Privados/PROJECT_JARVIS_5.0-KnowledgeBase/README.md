---
title: "PROJECT_JARVIS_5.0 Knowledge Base"
description: "Pasta de base de conhecimento do Jarvis para armazenar tudo que o assistente precisa saber." 
tags:
  - jarvis
  - privados
  - knowledge
  - base
  - assistant
---

# PROJECT_JARVIS_5.0 Knowledge Base

Esta pasta é a base de conhecimento dedicada do Jarvis. Ela contém cópias dos principais documentos e da estratégia que o assistente precisa ter como sua "consciência".

## Objetivo
- Manter um conjunto separado de notas que representam o conhecimento e a persona do Jarvis.
- Permitir que a inteligência acesse uma versão consolidada do que já foi definido sobre o projeto.
- Preservar a organização original de projetos em `Projetos/Privados/PROJECT_JARVIS_5.0.md` e `Projetos/EstudosFocados/PROJECT_JARVIS_5.0.md`.

## Arquivos desta pasta
### Entrada da KB
- [[README|README.md]] — guia principal da base de conhecimento e do uso da pasta.
- [[INDEX|INDEX.md]] — índice textual dos arquivos e seus propósitos.
- [[CONFIG|CONFIG.md]] — configurações e variáveis de ambiente para apontar o Jarvis à base de conhecimento.
- [[RULES|RULES.md]] — regras e governança da KB.
- [[PROJECT_JARVIS_5.0-Map|PROJECT_JARVIS_5.0-Map.md]] — estrutura e relações entre notas.
- [[PROJECT_JARVIS_5.0-SecondBrain|PROJECT_JARVIS_5.0-SecondBrain.md]] — definição e ingestão do segundo cérebro.

### Conhecimento principal
- [[PROJECT_JARVIS_5.0|PROJECT_JARVIS_5.0.md]] — visão geral do projeto e estado atual.
- [[PROJECT_JARVIS_5.0-Knowledge|PROJECT_JARVIS_5.0-Knowledge.md]] — domínio técnico e humano do Jarvis.
- [[PROJECT_JARVIS_5.0-Personality|PROJECT_JARVIS_5.0-Personality.md]] — persona, tom e estilo do Jarvis.
- [[PROJECT_JARVIS_5.0-Architecture|PROJECT_JARVIS_5.0-Architecture.md]] — arquitetura de alto nível do assistente.
- [[PROJECT_JARVIS_5.0-Strategy|PROJECT_JARVIS_5.0-Strategy.md]] — estratégia e roadmap multimodal.
- [[MOVIDO|MOVIDO.md]] — notas de migração e arquivos movidos para o novo vault.

### Integração e execução
- [[PROJECT_JARVIS_5.0-Integration|PROJECT_JARVIS_5.0-Integration.md]] — como integrar a KB com o código Jarvis.
- [[PROJECT_JARVIS_5.0-UseCases|PROJECT_JARVIS_5.0-UseCases.md]] — casos de uso prioritários do Jarvis.
- [[PROJECT_JARVIS_5.0-Tools|PROJECT_JARVIS_5.0-Tools.md]] — tecnologias e ferramentas usadas pelo projeto.

## Como usar
- Considere esta pasta como a "mente" do Jarvis.
- Use os arquivos daqui para alimentar modelos, fazer RAG ou montar o contexto do assistente.
- Mantenha a pasta sincronizada com as versões originais se algo mudar.

## Caminhos e configuração
- Base de conhecimento do Jarvis:
  `D:\OBSIDIAN\Will\Projetos\Privados\PROJECT_JARVIS_5.0-KnowledgeBase`
- Pasta real do projeto de código:
  `C:\Users\willi\Documents\GitHub\PROJECT_JARVIS_5.0`
- Vault raiz de organização:
  `D:\OBSIDIAN\Will`

### Instruções de configuração
Se o Jarvis suportar variáveis de ambiente ou `.env`, configure:
```powershell
$env:JARVIS_KB_PATH = 'D:\OBSIDIAN\Will\Projetos\Privados\PROJECT_JARVIS_5.0-KnowledgeBase'
$env:JARVIS_PROJECT_ROOT = 'C:\Users\willi\Documents\GitHub\PROJECT_JARVIS_5.0'
$env:JARVIS_VAULT_ROOT = 'D:\OBSIDIAN\Will'
```

### Comando sugerido para Jarvis
- variável: `JARVIS_KB_PATH`
- valor: `D:\OBSIDIAN\Will\Projetos\Privados\PROJECT_JARVIS_5.0-KnowledgeBase`

### Estrutura interna
Esta pasta deve conter:
- `PROJECT_JARVIS_5.0.md`
- `PROJECT_JARVIS_5.0-Knowledge.md`
- `PROJECT_JARVIS_5.0-Personality.md`
- `PROJECT_JARVIS_5.0-Architecture.md`
- `PROJECT_JARVIS_5.0-Strategy.md`
- `PROJECT_JARVIS_5.0-Integration.md`
- `PROJECT_JARVIS_5.0-UseCases.md`
- `PROJECT_JARVIS_5.0-Tools.md`
- `PROJECT_JARVIS_5.0-SecondBrain.md`
- `PROJECT_JARVIS_5.0-Map.md`
- `CONFIG.md`
- `RULES.md`

## Expansão contínua
- Sempre que Jarvis aprender algo novo, crie uma nova nota aqui.
- Use nomes consistentes: `PROJECT_JARVIS_5.0-<Tema>.md`.
- Esta pasta é a consciência dele. O código fica em `Projetos/Privados/PROJECT_JARVIS_5.0.md`.
