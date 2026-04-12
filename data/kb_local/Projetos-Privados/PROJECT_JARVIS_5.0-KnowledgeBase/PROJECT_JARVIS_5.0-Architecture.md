---
title: "PROJECT_JARVIS_5.0 Architecture"
description: "Arquitetura do Jarvis duplicada para a base de conhecimento." 
tags:
  - jarvis
  - privados
  - architecture
  - assistente
---

# PROJECT_JARVIS_5.0 Architecture

Esta nota descreve a arquitetura do Jarvis para a base de conhecimento dedicada.

## 1. Visão de alto nível
Jarvis deve ser composto por camadas:
- **Entrada**: voz, texto, visão, browser, contexto do usuário.
- **Processamento**: NLU, gerenciamento de diálogo, memória e persona.
- **Ferramentas**: código, automação de browser, buscas, RAG.
- **Saída**: voz, texto, visão, ações.

## 2. Camadas principais
### 2.1 Interface multimodal
- Voz: LiveKit, Piper TTS.
- Visão: MediaPipe, YOLOv8, OCR.
- Texto: chat, prompts, notas.
- Browser/PC: Playwright, automações.

### 2.2 Core do assistente
- NLU/Intents
- Diálogo e estado
- Memória de sessão e de usuário
- Persona e tom
- Regras de segurança

### 2.3 Integração de IA
- LLM local (Ollama)
- RAG com FAISS
- Prompt templates
- Fallbacks

### 2.4 Ferramentas
- Code helper
- Task planner
- Browser automation
- Personal support
- Analytics

## 3. Fluxo de dados
1. Entrada multimodal
2. Preprocessamento (STT, OCR, visão)
3. NLU e intenção
4. Recuperação de memória
5. Decisão de ação
6. Execução
7. Resposta

## 4. Memória
- Sessão
- Projeto
- Usuário
- Conhecimento

## 5. Infraestrutura
- Backend: FastAPI
- Frontend: Next.js
- Comunicação: LiveKit, WebSockets
- Persistência: Postgres/SQLite, FAISS

## 6. Segurança
- Permissões
- Logs
- Privacidade
- Consentimento

## 7. Evolução
- Modularizar Core, Tools, Persona, Knowledge
- Testar fluxos conversacionais
- Atualizar com feedback

**Texto duplicado do conhecimento para facilitar a construção da consciência do Jarvis.**