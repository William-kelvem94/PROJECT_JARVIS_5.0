---
title: "Jarvis Knowledge Base Config"
description: "Guia de configuração para apontar o Jarvis à base de conhecimento e ao vault do Obsidian." 
tags:
  - jarvis
  - privados
  - config
  - knowledge
---

# Jarvis Knowledge Base Config

Este arquivo contém as instruções e variáveis de ambiente para configurar o Jarvis com a base de conhecimento correta.

## Caminhos oficiais
- Base de conhecimento do Jarvis:
  `D:\OBSIDIAN\Will\Projetos\Privados\PROJECT_JARVIS_5.0-KnowledgeBase`
- Pasta real do projeto de código:
  `C:\Users\willi\Documents\GitHub\PROJECT_JARVIS_5.0`
- Vault raiz de organização geral:
  `D:\OBSIDIAN\Will`

## Configuração recomendada
### Windows PowerShell
```powershell
$env:JARVIS_KB_PATH = 'D:\OBSIDIAN\Will\Projetos\Privados\PROJECT_JARVIS_5.0-KnowledgeBase'
$env:JARVIS_VAULT_ROOT = 'D:\OBSIDIAN\Will'
```

### Windows CMD
```cmd
set JARVIS_KB_PATH=D:\OBSIDIAN\Will\Projetos\Privados\PROJECT_JARVIS_5.0-KnowledgeBase
set JARVIS_VAULT_ROOT=D:\OBSIDIAN\Will
```

### Variáveis para `.env` (se o Jarvis usar arquivo de configuração)
```
JARVIS_KB_PATH=D:\OBSIDIAN\Will\Projetos\Privados\PROJECT_JARVIS_5.0-KnowledgeBase
JARVIS_PROJECT_ROOT=C:\Users\willi\Documents\GitHub\PROJECT_JARVIS_5.0
JARVIS_VAULT_ROOT=D:\OBSIDIAN\Will
```

## Como Jarvis deve usar isso
- `JARVIS_KB_PATH` deve ser a pasta onde estão os documentos que compõem a consciência do Jarvis.
- `JARVIS_VAULT_ROOT` deve ser a raiz do vault Obsidian, onde estão `Projetos`, `Will-Pessoal/Perfil/Cerebro-Will.md`, `Bem-vindo.md` e outros hubs.

## O que deve estar na base de conhecimento
A base de conhecimento do Jarvis deve conter:
- `PROJECT_JARVIS_5.0.md`
- `PROJECT_JARVIS_5.0-Knowledge.md`
- `PROJECT_JARVIS_5.0-Personality.md`
- `PROJECT_JARVIS_5.0-Architecture.md`
- `PROJECT_JARVIS_5.0-Strategy.md`

## Como expandir a base
- Crie novas notas dentro de `PROJECT_JARVIS_5.0-KnowledgeBase/` sempre que adicionar novos conceitos, regras de persona, fluxos ou arquitetura.
- Use nomes descritivos como `PROJECT_JARVIS_5.0-Tools.md`, `PROJECT_JARVIS_5.0-UseCases.md`, `PROJECT_JARVIS_5.0-DialogFlow.md`.
- Mantenha a pasta como a "mente" do Jarvis: tudo que ele precisa saber deve ter um documento aqui.

## Observação
A pasta original do projeto (`Projetos/Privados/PROJECT_JARVIS_5.0.md`) continua sendo a implementação e a organização do código. Esta pasta de Knowledge Base é a consciência do Jarvis, não o código em si.
