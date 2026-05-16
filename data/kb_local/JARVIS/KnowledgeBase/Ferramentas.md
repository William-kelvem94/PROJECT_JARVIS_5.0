---
title: "Jarvis Tools and Technologies"
description: "Lista de ferramentas e tecnologias usadas pelo Jarvis e seus papéis no projeto." 
tags:
  - jarvis
  - tools
  - tech
---

# Jarvis Tools and Technologies

Esta nota descreve as ferramentas principais do Jarvis e como cada uma contribui para o ecossistema do projeto.

## 1. WebSocket Nativo (substituiu LiveKit)
- Comunicação de voz em tempo real via WebSocket nativo.
- Transporte de áudio bidirecional para front-end e backend.
- Substituiu o LiveKit como camada de comunicação de voz.

## 2. Piper
- Síntese de voz local (TTS).
- Cria respostas de voz com timbre natural.
- Usado para tornar Jarvis falante e interativo.

## 3. MediaPipe
- Detecção facial e análise de gestos.
- Extração de landmarks e comportamento em vídeo.
- Serve como base para visão multimodal.

## 4. YOLOv8
- Detecção de objetos em tempo real.
- Permite reconhecer elementos do ambiente.
- Útil em automações de visão e alertas de segurança.

## 5. Playwright
- Automação de browser controlada.
- Permite execução autônoma de tarefas web.
- Útil para navegar, preencher formulários e coletar dados.

## 6. FastAPI
- Backend Python eficiente e fácil de escalar.
- Exposição de APIs para agentes, visão e controle.
- Base para orquestração de serviços.

## 7. Next.js
- Interface web moderna para controle e visualização.
- Permite dashboards e páginas interativas.
- Antigamente combinava com LiveKit; agora usa WebSocket nativo.

## 8. Modelos LLM
- Responsável pela inteligência de linguagem.
- Pode usar Gemini, OpenAI ou modelos locais.
- Suporta geração de texto, entendimento e planejamento.

## 9. RAG / FAISS
- Recuperação de informações da KB.
- Indexação semântica dos documentos.
- Permite ao Jarvis responder com base em seu próprio conhecimento.

## 10. Docker e scripts auxiliares
- Facilita o deploy e o gerenciamento de serviços.
- Scripts PowerShell e batch ajudam a iniciar o ambiente.
- Útil para padronizar o setup local.

## Como usar esta nota
- Referencie aqui quando for decidir se deve adicionar uma nova biblioteca ou serviço.
- Atualize sempre que a stack mudar ou houver nova integração importante.
