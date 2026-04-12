# Operadores MCP para VS Code AI

Este arquivo descreve operadores de ação comuns para agentes que usam MCP em projetos de código.

## Operadores básicos
- `read_file(path)` — lê o conteúdo de um arquivo.
- `search_files(pattern)` — busca arquivos por nome ou conteúdo.
- `edit_file(path, changes)` — aplica mudanças específicas em um arquivo.
- `create_file(path, content)` — cria um novo arquivo.
- `append_file(path, content)` — adiciona conteúdo ao final de um arquivo.
- `delete_file(path)` — remove um arquivo.
- `rename_file(oldPath, newPath)` — renomeia ou move um arquivo.
- `execute_command(command)` — roda um comando no terminal para validar ou gerar resultados.
- `path_exists(path)` — verifica se um arquivo ou diretório existe.
- `diff_file(oldPath, newPath)` — compara versões ou visualiza alterações.
- `format_code(path)` — aplica formatação padrão ao arquivo.

## Operadores auxiliares
- `list_dir(path)` — lista arquivos e pastas em um diretório.
- `get_file_stats(path)` — retorna tamanho, data de modificação e existência.
- `read_yaml(path)` — lê dados estruturados de YAML.
- `write_yaml(path, data)` — grava dados estruturados em YAML.

## Padrões de uso
### 1. Contexto antes da mudança
Sempre comece com:
- `search_files` para localizar o arquivo alvo.
- `read_file` para ler o contexto completo.
- `path_exists` para confirmar o local correto.

### 2. Planos seguros
- Defina o objetivo em texto claro.
- Liste quais arquivos serão tocados.
- Faça mudanças pequenas e localizadas com `edit_file`.
- Use `format_code` quando for editar código.

### 3. Validação imediata
- `execute_command` para rodar testes, lint ou build.
- `diff_file` para revisar alterações antes de finalizar.
- `read_file` no resultado ou documentação atualizada.

### 4. Documentação de ação
- Após mudanças, escreva um resumo curto.
- Use o próprio agente para criar notas de revisão em `skills/vscode-ai/`.

## Exemplo de fluxo de MCP com operadores
1. `search_files("src/**/*service.py")`
2. `read_file("src/service.py")`
3. `edit_file("src/service.py", "adicionar tratamento de exceção")`
4. `format_code("src/service.py")`
5. `execute_command("pytest tests/test_service.py")`
6. `diff_file("src/service.py", "src/service.py")` (ou outro método de diff)

## Regras de segurança
- Não execute `delete_file` sem confirmar o backup ou a ausência de dependência.
- Não altere grandes blocos sem um plano e sem rodar validação.
- Para mudanças críticas, crie sempre um arquivo de teste ou nota de `skills/vscode-ai`.
- Evite edições múltiplas sem `diff_file` e resumo final.

## Nível de detalhe
- Use `read_file` com trecho se o arquivo for grande.
- Use `search_files` com termos específicos em vez de adivinhar o caminho.
- Prefira `append_file` quando estiver adicionando exemplos, docs ou novos casos de teste.
