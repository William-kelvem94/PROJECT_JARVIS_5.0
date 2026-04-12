# MCP Tools for OpenClaude

## O que é Model Context Protocol (MCP)
MCP é um conjunto de padrões que define como um agente de IA interage com o contexto do projeto, arquivos e o ambiente de desenvolvimento.

## Por que usar MCP
- Organiza ações de IA em etapas claras.
- Reduz erros ao evitar mudanças sem contexto.
- Facilita a validação e documentação de cada passo.
- Torna o uso de agentes repetível e confiável.

## Operadores padrão
- `read_file(path)` — ler o conteúdo de um arquivo.
- `search_files(pattern)` — buscar arquivos por nome ou conteúdo.
- `edit_file(path, changes)` — alterar trechos de arquivos.
- `create_file(path, content)` — criar novo arquivo.
- `append_file(path, content)` — adicionar ao fim de um arquivo.
- `delete_file(path)` — removação segura de arquivo.
- `rename_file(oldPath, newPath)` — mover ou renomear.
- `execute_command(command)` — rodar script, teste ou build.
- `path_exists(path)` — confirmar se o caminho existe.
- `diff_file(oldPath, newPath)` — comparar versões ou mudanças.
- `format_code(path)` — aplicar formatação padrão.

## Padrão de uso
1. Entenda o problema com `read_file` e `search_files`.
2. Planeje a ação em texto curto.
3. Execute mudanças pequenas com `edit_file`.
4. Valide com `execute_command`.
5. Resuma e documente a mudança.

## Exemplos de uso
### Ajuste de interface
- `search_files("src/**/*Login*")`
- `read_file("src/components/LoginForm.tsx")`
- `edit_file("src/components/LoginForm.tsx", "melhorar validação")`
- `execute_command("pnpm lint")`

### Criação de endpoint
- `create_file("backend/routes/auth.py", content)`
- `read_file("backend/app.py")`
- `execute_command("pytest tests/test_auth.py")`

## Boas práticas de MCP
- Nunca edite sem contexto.
- Prefira passos atômicos e reversíveis.
- Confirme a existência do arquivo antes de alterar.
- Use `diff_file` para revisar mudanças.
- Atualize docs sempre que alterar comportamento.

## Aplicação no VS Code
- Use os operadores para agir como um assistente de código.
- Combine `search_files` e `read_file` para evitar erros de path.
- Use `execute_command` para validar no mesmo fluxo.

## Como organizar o workspace
- Mantenha arquivos de skill e prompt em `skills/`.
- Crie notas de processo em `skills/vscode-ai/` quando fizer mudanças significativas.
- Use tags como `#mcp`, `#ai`, `#skill` e `#vscode` nos arquivos de referência.

