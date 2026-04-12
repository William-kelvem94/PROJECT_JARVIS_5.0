# VS Code AI Skills & MCP

Estrutura de skills e Model Context Protocol (MCP) para usar modelos de IA no VS Code em projetos seus.

## Propósito
- Reunir prompts, padrões e ferramentas para acelerar tarefas de desenvolvimento com IA.
- Oferecer referência clara para usar IA local (OpenClaude, Ollama, Claude) ou APIs.
- Integrar operações de VS Code com leitura/edição de arquivos e comandos de terminal.

## Estrutura
- [[README|Visão geral e como usar]]
- [[INDEX|Índice completo do hub]]
- [[mcp|Padrões de MCP e mapeamento de tools]]
- [[prompts|Prompts prontos para tarefas de código, refatoração e docs]]
- [[mcp-operators|Operadores MCP e regras de ação]]
- [[skills-categories|Categorias de skills por domínio técnico]]
- [[use-cases|Casos de uso passo a passo para tarefas comuns]]
- [[advanced-workflows|Workflows avançados para projetos complexos]]
- [[templates|Modelos de prompt reutilizáveis para agentes de IA]]
- [[quick-start|Comandos específicos para seu ambiente Windows e VS Code]]
- [[project-jarvis-prompts|Prompts focados no projeto PROJECT_JARVIS_5.0]]
- [[mini-agent|Mini-agent de IA com fluxo de leitura/edição/validação]]
- [[direct-agent-prompts|Prompts prontos para copiar e colar no seu chat local]]
- [[best-practices|Boas práticas para usar IA no VS Code de forma segura e eficiente]]
- [[quick-reference|Resumo rápido de operadores, prompts e workflows]]

## Como usar
1. Abra `skills/vscode-ai/README.md` como ponto de entrada.
2. Use `skills/vscode-ai/mcp.md` como referência para padrões de ação.
3. Copie templates de `skills/vscode-ai/prompts.md` para seu agente ou prompt builder.
4. Adapte os exemplos para seu projeto em `Projetos/` ou `Will-Pessoal/`.

## Recomendações importantes
- Marque as notas-chave com tags como `#ai`, `#vscode`, `#mcp`, `#skill`.
- Use o mesmo estilo de naming para pastas de skills: `skills/vscode-ai/`.
- Mantenha as skills curtas e com exemplos práticos.
- Prefira modelos locais quando possível, como Ollama ou Mistral, para segurança e rapidez.

## Casos de uso
- `skills/vscode-ai/use-cases.md` — passo a passo para refatoração, bugfix, documentação, testes, RAG e deploy.
- `skills/vscode-ai/prompts.md` — prompts prontos para tarefas comuns.
- `skills/vscode-ai/mcp.md` — protocolos de ação para agentes e IA.

## Opções de modelos
- Ollama: ideal para IA local e RAG.
- Mistral e Llama: bons para tarefas de desenvolvimento e análise.
- Claude: útil se deseja respostas mais conversacionais.

## Como conectar com seus projetos
1. Abra a pasta do projeto no VS Code.
2. Use `skills/vscode-ai/prompts.md` para gerar prompts específicos.
3. Use `skills/vscode-ai/mcp.md` para guiar passos de leitura e edição.
4. Salve padrões úteis em `skills/vscode-ai/templates.md` ou em `Will-Pessoal/Conhecimento/Leituras.md`.
