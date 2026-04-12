---
tags: [skills]
---

# Prompts Prontos para Agente de Chat Local

Use estes prompts diretamente no seu agente de chat local (Ollama, OpenClaude, Claude, etc.). Eles foram formulados para o projeto `PROJECT_JARVIS_5.0` e para tarefas de desenvolvimento em VS Code.

## 1. Diagnóstico rápido de projeto
"Você é um assistente de desenvolvimento. Analise o projeto `PROJECT_JARVIS_5.0` e indique:
1. Quais são os principais componentes de backend, frontend e memória?
2. Quais arquivos parecem ser responsáveis pelo fluxo de RAG?
3. Quais são os dois maiores riscos de implementação deste projeto?"

## 2. Corrigir bug no backend
"Encontre e corrija o bug no backend de `PROJECT_JARVIS_5.0` relacionado ao processamento de entrada de voz. Explique o problema e o que foi alterado. Ao final, sugira um teste que valide a correção."

## 3. Melhorar a arquitetura de memória
"Sugira uma arquitetura de memória persistente para `PROJECT_JARVIS_5.0`, usando Obsidian Vault, embeddings e FAISS. Explique passo a passo onde cada componente deve ser implementado e como os dados devem ser consultados."

## 4. Criar endpoint RAG
"Crie um endpoint FastAPI para `PROJECT_JARVIS_5.0` que receba texto, gere embeddings e busque documentos relevantes em FAISS. Forneça o código do endpoint e explique como ele deve ser testado."

## 5. Gerar documentação para o README
"Escreva uma seção `Como funciona` para o README de `PROJECT_JARVIS_5.0` explicando:
- como a voz entra no sistema,
- como a busca semântica é realizada,
- como a memória é consultada,
- como o resultado é enviado ao usuário."

## 6. Criar componente de chat no frontend
"Descreva um componente Next.js para chat que mostra mensagens de usuário e respostas do Jarvis. Inclua como exibir histórico, status de carregamento e falhas de conexão."

## 7. Testes para pipeline de memória
"Gere casos de teste para o pipeline de memória do Jarvis, incluindo:
- Ingestão de novo documento,
- Geração de embeddings,
- Busca de contexto relevante,
- Resposta baseada na memória correta."

## 8. Revisão de código rápida
"Revise o trecho de código abaixo e identifique melhorias de performance, segurança e estilo. Se necessário, proponha o código revisado." 

## 9. Sugestão de melhorias de curto prazo
"Liste 5 melhorias de curto prazo para tornar `PROJECT_JARVIS_5.0` mais estável e confiável em ambiente local. Priorize mudanças que possam ser implementadas esta semana."

## 10. Check-list de deploy local
"Crie um checklist simples para rodar `PROJECT_JARVIS_5.0` localmente em Windows, incluindo:
- setup de ambiente,
- variáveis de ambiente,
- comandos de build,
- validações básicas.
"

## Uso
- Copie qualquer prompt e cole no chat do agente.
- Se quiser, adicione contexto específico do seu repositório antes do prompt (por exemplo, nomes de arquivos ou funções). 
- Use prompts de follow-up para pedir explicações mais detalhadas ou ajustes.
