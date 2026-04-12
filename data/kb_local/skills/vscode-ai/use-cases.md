# Casos de Uso — VS Code AI

## 1. Refatoração de código existente
1. `search_files` para localizar o arquivo com a função ou componente.
2. `read_file` para entender o comportamento atual.
3. Defina o objetivo: melhorar legibilidade, reduzir duplicação, extrair helper.
4. `edit_file` para aplicar as mudanças.
5. `execute_command` para validar com testes unitários ou lint.

Exemplo:
- "Refatore `src/components/LoginForm.tsx` para separar o formulário e o estado em hooks reutilizáveis."

## 2. Correção de bugs com explicação
1. `search_files` por arquivos de teste ou pelo nome da função.
2. `read_file` no trecho onde ocorre o erro.
3. `edit_file` com a correção sugerida.
4. `execute_command` rodar o teste específico.

Exemplo:
- "Identifique e corrija o bug no `auth.py` que faz `login()` falhar quando o usuário não tem token."

## 3. Documentação técnica rápida
1. Use `read_file` no arquivo ou módulo alvo.
2. Gere resumo de arquitetura, APIs ou fluxo de dados.
3. `create_file` ou `edit_file` para atualizar README ou docs.

Exemplo:
- "Escreva um README conciso para `PROJECT_JARVIS_5.0` explicando arquitetura, fluxo de memória e comandos de execução."

## 4. Testes e validação
1. `search_files` por arquivos de teste relacionados.
2. `read_file` para ver os casos existentes.
3. `edit_file` para adicionar novos testes.
4. `execute_command` rodar `pytest` ou `npm test`.

Exemplo:
- "Adicione casos de teste para validação de formulário e resposta de erro para `src/api/user.js`."

## 5. IA local e RAG aplicada ao projeto
1. Desenhe o fluxo de ingestão de dados com `read_file` das configurações de embeddings.
2. Modele a arquitetura de recuperação de contexto.
3. `create_file` para registrar o fluxo no vault de conhecimento.

Exemplo:
- "Descreva como integrar Ollama, FAISS e Obsidian Vault para dar memória ao Jarvis local."

## 6. Workflow de deploy ou container
1. `read_file` em `docker-compose.yml` ou `Dockerfile`.
2. `edit_file` para ajustar variáveis de ambiente e comandos.
3. `execute_command` para construir e subir containers.

Exemplo:
- "Atualize o `docker-compose.yml` para incluir serviço de banco de dados PostgreSQL e variáveis secretas."

## 7. Criação de templates de prompt
1. Defina uma tarefa comum.
2. Crie prompt padrão em `skills/vscode-ai/prompts.md`.
3. Use o template em agentes ou scripts.

Exemplo:
- "Gerar prompt padrão para revisão de PR focada em performance e segurança."

## 8. Leituras relacionadas
- Veja `mcp-operators.md` para operadores avançados.
- Veja `advanced-workflows.md` para fluxos mais completos.
