# Referência Rápida — VS Code AI

Use este arquivo como atalho rápido para operadores, prompts e workflows essenciais.

## Operadores principais
- `search_files(pattern)` — localiza arquivos ou trechos.
- `read_file(path)` — lê o conteúdo completo.
- `edit_file(path, changes)` — modifica o arquivo.
- `create_file(path, content)` — cria um novo arquivo.
- `execute_command(command)` — roda testes, builds ou scripts.

## Fluxo mínimo
1. `search_files` para localizar contexto.
2. `read_file` para entender o arquivo.
3. Planeje a mudança em texto.
4. `edit_file` para aplicar.
5. `execute_command` para validar.
6. `summarize` as alterações.

## Principais arquivos de skill
- `skills/vscode-ai/README.md` — entrada do hub.
- `skills/vscode-ai/mcp.md` — padrões de ação.
- `skills/vscode-ai/mcp-operators.md` — operadores MCP detalhados.
- `skills/vscode-ai/prompts.md` — prompts prontos.
- `skills/vscode-ai/templates.md` — modelos de prompt.
- `skills/vscode-ai/advanced-workflows.md` — workflows avançados.
- `skills/vscode-ai/best-practices.md` — boas práticas.
- `skills/vscode-ai/direct-agent-prompts.md` — prompts prontos para chat.

## Comandos essenciais para Jarvis
- `pnpm install`
- `pnpm lint`
- `pytest`
- `python -m unittest`
- `docker compose up --build`

## Prompt rápido para usar no chat
"Você é um assistente de desenvolvimento. Encontre o arquivo relevante, leia o contexto, aplique a mudança e valide com testes. Em seguida, forneça um resumo das alterações." 

## Notas de organização
- Use `skills/vscode-ai` como camada de referência para IA.
- Use `skills/fullstack` para domínios de frontend, backend e database.
- Use `skills/mcp-tools.md` se quiser uma visão geral e exemplos de MCP.
