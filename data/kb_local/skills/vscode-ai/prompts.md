---
tags: [skills]
---

# Prompt Templates para VS Code AI

## Padrões de prompt
- Seja específico: inclua arquivo, objetivo e formato de saída.
- Peça passos numerados quando a tarefa for complexa.
- Oriente o estilo: "Use linguagem objetiva" ou "Responda como desenvolvedor sênior".
- Use follow-up para ajustar detalhes após a primeira resposta.

## Desenvolvimento
- "Crie um componente React com Tailwind para [descrição específica]."
- "Implemente um endpoint REST em Express que salve dados de usuário no banco Postgres."
- "Adicione autenticação JWT ao `backend/auth.js` usando middleware." 
- "Refatore `src/App.tsx` para separar componente de layout e lógica de formulário."

## Correção de bugs
- "Análise `src/service.py` e corrija o erro de `NoneType` na função `process_data`."
- "Explique por que este teste `tests/test_user.py` está falhando e proponha a correção."

## Refatoração
- "Extraia a lógica de validação de `signup.js` para um helper reutilizável."
- "Melhore a legibilidade deste código sem alterar seu comportamento." 
- "Converta esta função callback em async/await com tratamento de erro." 

## Documentação
- "Gere README para o projeto `Projetos/Outros/Gestor Aluguel 2.0` com instalação, uso e deploy." 
- "Crie comentário JSDoc para `src/utils/validators.ts`."
- "Escreva um resumo de arquitetura para o projeto `PROJECT_JARVIS_5.0` focando em IA local e memória." 

## Testes
- "Crie testes unitários em Jest para `src/components/LoginForm.tsx`."
- "Adicione caso de teste que valida input vazio em `tests/test_auth.py`."
- "Gere dados fake para teste de integração em `tests/fixtures/user.json`."

## IA local e RAG
- "Descreva o fluxo de dados de RAG para `Jarvis` usando Ollama, embeddings e FAISS." 
- "Sugira uma arquitetura para memória persistente no Vault Obsidian usando Python." 
- "Liste os passos para integrar um LLM local com pesquisa semântica e recuperação de contexto." 
- "Crie um diagrama texto passo a passo para ingestão de documentos, geração de embeddings e recuperação de contexto no Jarvis." 
- "Explique como configurar um pipeline local de `text-embedding-3-large` com FAISS e busca semântica." 

## Prompt de arquitetura
- "Explique a arquitetura de `PROJECT_JARVIS_5.0` com foco em backend, front-end e memória local." 
- "Liste os componentes necessários para construir um agente que usa voz, visão e RAG." 
- "Sugira uma divisão de módulos para um projeto Next.js + FastAPI + Docker." 

## Prompt de revisão de código
- "Revise o trecho de código abaixo e identifique problemas de segurança, performance ou estilo."
- "Avalie se este serviço API tem boa separação de responsabilidades e sugira melhorias."
- "Compare duas implementações e indique qual é mais simples de manter."

## Prompt de explicação de lógica
- "Explique em linguagem clara o que faz a função `handleSubmit` neste componente." 
- "Resuma os passos desta pipeline de dados em uma lista numerada." 
- "Descreva o propósito e os efeitos colaterais desta função de inicialização."

## Prompt de documentação
- "Gere uma seção `How it works` para o README deste microserviço." 
- "Crie um resumo de arquitetura em até 5 frases para um stakeholder não técnico." 
- "Escreva um changelog curto para as mudanças feitas neste commit." 

## Prompt de design de teste
- "Gere casos de teste para validar entrada inválida e falhas de autenticação." 
- "Escreva um teste de integração que verifica a rota `/api/login`."
- "Crie dados de teste fake para usuários e pedidos." 

## Uso com MCP
- "Use `search_files` para localizar o arquivo onde a função `initApp` é definida."
- "Use `read_file` no arquivo encontrado e depois `edit_file` para adicionar logs de debug."
- "Após a edição, execute `npm test` para validar a mudança."
- "Configure um ambiente Python com `pyproject.toml`, `venv`, `pre-commit` e `pytest`."

## Uso com MCP
- "Use `search_files` para localizar o arquivo onde a função `initApp` é definida."
- "Use `read_file` no arquivo encontrado e depois `edit_file` para adicionar logs de debug."
- "Após a edição, execute `npm test` para validar a mudança."
