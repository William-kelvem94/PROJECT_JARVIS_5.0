# Categorias de Skills para IA no VS Code

## Fullstack
- Frontend: React, Next.js, Vite, Tailwind, componentes, CSS.
- Backend: Node, Express, Python, FastAPI, Flask, autenticação, APIs.
- Database: SQL, Postgres, MySQL, Prisma, MongoDB, Redis.

## IA local
- Modelos: Ollama, Claude, Mistral, Llama, Falcon.
- RAG: embeddings, FAISS, Chroma, memória persistente.
- Agentes: fluxo de prompts, tomada de decisão, data augmentation.
- Memória: ingestão, indexação, recuperação, atualização incremental.

## Infra e DevOps
- Docker, docker-compose, Traefik, nginx.
- Deploy local, containers, CI/CD, scripts de build.
- Configuração de ambiente: `.env`, `docker-compose.yml`, `GitHub Actions`.

## Automação e produtividade
- Scripts de automação (Playwright, Selenium, scraping).
- Integração contínua com testes e lint.
- Documentação, README e templates de projeto.

## Agentes e assistentes
- Prompt chaining para workflows complexos.
- Memória de sessão e contexto em prompt.
- Resultados esperados, validação e fallback.

## MCP & VS Code
- Ações de leitura/escrita: `read_file`, `edit_file`, `create_file`, `search_files`, `execute_command`.
- Workflow iterativo: analisar, planejar, agir, validar, resumir.
- Use alterações pequenas e verificações frequentes.
- Documente cada passo em notas quando trabalhar com IA.
- Use `mcp-operators.md` para entender operadores avançados e regras de segurança.

## Prompt engineering
- Prefira instruções claras, diretas e com contexto técnico.
- Use exemplos e descrições de formato desejado.
- Peça sempre validação ou revisão quando fizer mudanças de código.
- Peça um resumo final com arquivos alterados e comandos executados.

## Notes para VS Code
- Adapte cada skill ao contexto do projeto.
- Use tags `#skill`, `#mcp`, `#vscode`, `#ai` nos arquivos de referência.
- Prefira exemplos práticos em vez de descrições gerais.

## Exemplo de uso
- `skills/vscode-ai/prompts.md` para gerar mensagens de IA.
- `skills/vscode-ai/mcp.md` para definir ações de leitura/edição/comando.
- `skills/fullstack/*.md` para domínios técnicos específicos.
