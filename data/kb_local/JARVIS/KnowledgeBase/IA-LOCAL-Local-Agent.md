---
title: "IA-LOCAL Local Agent"
description: "Documentação do agente IA-LOCAL rodando localmente com Obsidian como base de conhecimento."
tags:
  - ia-local
  - jarvis
  - agent
  - local
  - obsidian
---

# IA-LOCAL Local Agent

Este documento descreve o agente local IA-LOCAL, seu fluxo de conhecimento e como ele usa o vault Obsidian copiado.

## Visão geral

IA-LOCAL agora roda completamente local:

- Modelo de linguagem local usando `llama-cpp-python`
- Memória vetorial local com FAISS
- Embeddings gerados com `sentence-transformers`
- Vault Obsidian copiado em `obsidian_clone` como fonte de conhecimento

O agente não depende de APIs externas para gerar respostas, exceto se algum módulo de voz ou TTS precisar de suporte adicional.

## Componentes principais

1. **LocalLLM**
   - Backend: `llama-cpp-python`
   - Modelo local configurado por `LOCAL_MODEL_PATH`
   - Não exige OpenAI, OpenRouter ou Gemini para o fluxo principal

2. **MemoryManager**
   - Armazena memórias em `memory.db`
   - Cria e gerencia embeddings em `embeddings.pkl`
   - Usa FAISS para busca semântica

3. **ObsidianVault**
   - Lê notas Markdown do vault local copiado
   - Separa o conteúdo em chunks e ingere como memórias de conhecimento

4. **Conversation**
   - Constrói o prompt local com histórico curto e fatos relevantes
   - Executa o modelo local sem APIs externas

## Fluxo de uso

1. Ao iniciar, IA-LOCAL carrega o `.env`.
2. O `OBSIDIAN_VAULT_PATH` aponta para `obsidian_clone`.
3. Todas as notas `*.md` são lidas e ingeridas.
4. Perguntas do usuário usam as memórias relevantes e o contexto do histórico.
5. O modelo local gera respostas diretamente.

## O que o agente pode fazer aqui

- Responder perguntas baseadas no conteúdo do vault.
- Reter contexto de conversa em memória local.
- Relembrar fatos importantes e dados técnicos do vault.
- Operar offline sem chave de API externa.

## Limitações atuais

- Não há criação automática de novas notas no vault.
- Não há edição ou sincronização bidirecional com o Obsidian original.
- O modelo local pode ser mais lento ou menos preciso que um serviço em nuvem.
- O vault é lido como texto — formatação avançada e plugins do Obsidian não são interpretados.

## Próximos passos recomendados

- Criar um módulo de escrita no vault para gerar notas a partir de ideias do Jarvis.
- Adicionar gerenciamento de tarefas e templates no próprio Obsidian.
- Implementar um indexador incremental para atualizar apenas notas novas.
- Construir uma interface de controle para gerar novos arquivos Markdown automaticamente.
