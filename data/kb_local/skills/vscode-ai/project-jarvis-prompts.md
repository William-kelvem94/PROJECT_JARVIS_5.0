---
tags: [skills]
---

# Prompts para PROJECT_JARVIS_5.0

Este arquivo contém prompts focados no projeto `PROJECT_JARVIS_5.0`, com ênfase em IA local, RAG, memória e integração.

## Arquitetura e visão
- "Descreva a arquitetura ideal de `PROJECT_JARVIS_5.0` considerando backend Python, front-end Next.js e memória local no Obsidian Vault."
- "Liste os componentes necessários para adicionar voz e visão ao Jarvis, incluindo captura, inferência e resposta."
- "Explique como o fluxo de dados deve percorrer do frontend até a camada de RAG e resposta do modelo."

## Memória e RAG
- "Explique um pipeline de ingestão para o Vault Obsidian: leitura de notas, geração de embeddings e armazenamento em FAISS."
- "Sugira como o Jarvis deve recuperar contexto da memória para perguntas relacionadas a projetos anteriores."
- "Descreva a diferença entre memória episódica e memória de longo prazo em `PROJECT_JARVIS_5.0`."

## Desenvolvimento do backend
- "Crie um endpoint FastAPI que receba texto, gere embeddings e execute busca semântica no FAISS."
- "Implemente um módulo Python `vault_memory.py` que adicione e consulte memórias do Obsidian."
- "Adicione tratamento de erros ao serviço de conversão de voz para texto no backend."

## Frontend e experiência de usuário
- "Projetar um componente de chat em Next.js que exiba histórico de conversa e permita interações por voz."
- "Descreva como exibir resultados de busca semântica no frontend com relevância e fonte."
- "Crie uma UI simples para editar, salvar e consultar memórias no Jarvis."

## Testes e validação
- "Gere casos de teste que validem a rota de chat e o pipeline de memória no backend."
- "Escreva um teste de integração que garanta que uma pergunta sobre histórico retorne contexto correto."
- "Crie um conjunto de fixtures para simular documentos do Obsidian e buscas por embeddings."

## Documentação e README
- "Crie uma seção `Como funciona` para o README de `PROJECT_JARVIS_5.0` explicando voz, visão, RAG e memória."
- "Escreva instruções de configuração local do projeto, incluindo `docker compose`, `.env` e dependências."
- "Liste comandos essenciais para iniciar o projeto em desenvolvimento no Windows."

## Prompt de melhoria contínua
- "Sugira 5 melhorias de curto prazo para tornar o Jarvis mais confiável em ambiente local."
- "Proponha refatorações para reduzir acoplamento entre o frontend Next.js e o backend Python."
- "Identifique possíveis pontos de falha no fluxo de memória e indique como monitorá-los."
