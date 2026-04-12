# Boas Práticas — VS Code AI

Este guia reúne boas práticas para usar IA no VS Code e manter a organização do seu vault.

## Estrutura de trabalho
- Use `skills/vscode-ai/README.md` como hub principal.
- Separe prompts, workflows e templates em arquivos diferentes.
- Mantenha as anotações do projeto em `skills/vscode-ai/` e não misture com código de produção.
- Use tags como `#ai`, `#mcp`, `#vscode`, `#skill` para localizar rapidamente.

## Como perguntar ao agente
- Seja específico e objetivo.
- Forneça contexto: nome do projeto, arquivo, requisito.
- Peça ações passo a passo quando o problema for maior.
- Use follow-ups para ajustar o resultado.

## Evite erros comuns
- Não edite arquivos sem ler o contexto primeiro.
- Não aplique mudanças extensas sem validação.
- Não use um prompt genérico para tarefas técnicas complexas.
- Sempre documente a mudança ou crie uma nota de processo.

## Validação
- Execute testes sempre que alterar código.
- Use `pnpm lint`, `pytest` ou o stack de validação do projeto.
- Se não houver testes, crie pelo menos um caso simples para a mudança.
- Use `diff_file` ou revisão manual para confirmar alterações.

## Fluxo ideal de IA
1. `search_files` para localizar o arquivo.
2. `read_file` para entender o contexto.
3. Planeje a alteração em texto.
4. `edit_file` para aplicar mudanças pequenas.
5. `execute_command` para validar.
6. `summarize` e documente o resultado.

## Integração com o projeto
- Relacione cada skill ao projeto em `Projetos/` ou `Will-Pessoal/`.
- Use `skills/vscode-ai/project-jarvis-prompts.md` para tarefas específicas.
- Crie notes de processo em `Will-Pessoal/Conhecimento/Leituras.md` se o aprendizado for valioso.

## Atualização contínua
- Revise e melhore estes arquivos a cada nova experiência.
- Adicione novos templates quando identificar tarefas recorrentes.
- Atualize `skills/vscode-ai/README.md` com novas referências e links.
