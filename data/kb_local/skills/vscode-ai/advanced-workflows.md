# Workflows Avançados — VS Code AI

Workflows avançados ajudam a aplicar MCP de forma estruturada em projetos complexos.

## 1. Bug triage + correção
### Objetivo
Identificar, corrigir e validar um bug com segurança.

### Passos
1. `search_files` pelo erro ou pelo arquivo associado.
2. `read_file` do arquivo alvo e testes relacionados.
3. `plan` com:
   - causa provável,
   - mudança necessária,
   - testes a rodar.
4. `edit_file` para corrigir.
5. `execute_command("pytest caminho/teste")`.
6. `diff_file` ou `review` para confirmar.
7. `summarize` com o que mudou e por quê.

### Exemplo
- Bug: `login()` falha com input vazio.
- Passos: validar input, normalizar dados, mensagem clara ao usuário.

## 2. Refatoração incremental
### Objetivo
Melhorar legibilidade e modularidade sem alterar comportamento.

### Passos
1. `search_files` por módulos grandes ou repetidos.
2. `read_file` em trechos com lógica pesada.
3. `plan` extraindo helpers/serviços.
4. `edit_file` para aplicar extração.
5. `execute_command("pnpm lint && npm test")`.
6. `reflect` sobre ganhos de clareza.

### Exemplo
- Separar validação de formulário de renderização de UI.
- Transformar função longa em 2-3 helpers simples.

## 3. Adicionar funcionalidade com testes
### Objetivo
Implementar uma feature e garantir cobertura.

### Passos
1. Leia os requisitos no arquivo de especificação ou issue.
2. `search_files` por rotas, serviços e testes existentes.
3. `plan` com endpoints, validações e UI.
4. `edit_file` no backend/frontend.
5. `create_file` para novos testes.
6. `execute_command` rodar testes específicos.
7. Documente a feature em README.

### Exemplo
- Feature: endpoint de geração de embeddings e busca semântica.
- Testes: entrada válida, entrada inválida, fallback de erro.

## 4. Pipeline de documentação e release
### Objetivo
Atualizar documentação e preparar para deploy.

### Passos
1. `read_file` do README atual e changelog.
2. `search_files` por seções de deploy e setup.
3. `edit_file` para atualizar instruções de instalação.
4. `create_file` se necessário para novos guias.
5. `execute_command("pnpm lint")` para validar docs se você usa markdown lint.
6. `summarize` na nota de release.

### Exemplo
- Documentar como rodar Jarvis localmente com Ollama e Obsidian.
- Incluir exemplos de `.env` e `docker compose`.

## 5. Integração RAG e IA local
### Objetivo
Configurar e documentar o fluxo de memória e recuperação de contexto.

### Passos
1. `read_file` das configurações de embeddings e do Vault Obsidian.
2. `plan` a arquitetura de ingestão, embeddings e busca.
3. `edit_file` para ajustar rotas e handlers.
4. `create_file` para diagramas de fluxo ou notas de arquitetura.
5. `execute_command` para testes de integração específicos.
6. `reflect` em como a memória será usada em consultas futuras.

### Exemplo
- Arquitetura: ingestão → embeddings → FAISS → consulta.
- Validar com pergunta de contexto histórico.

## 6. Revisão de PR e monitoramento
### Objetivo
Analisar um PR ou mudança crítica com atenção a qualidade.

### Passos
1. `search_files` no diff ou no branch alvo.
2. `read_file` das mudanças principais.
3. `plan` itens de revisão: segurança, performance, estilo.
4. `summarize` com feedback e sugestões.

### Exemplo
- Revisar um PR que adiciona autenticação JWT.
- Conferir endpoints, validação e fluxo de login.

## 7. Checklist de agentes
- Sempre peça contexto se não houver detalhes suficientes.
- Verifique paths antes de editar.
- Execute validações automáticas.
- Documente mudanças em `skills/vscode-ai/` ou no próprio projeto.
