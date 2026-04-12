---
tags: [skills]
---

# Backend Skills - Node/Express/Python

## Prompts para desenvolvimento backend
```
Crie API REST Node/Express com autenticação JWT.
```

## Prompts avançados
- "Implemente um endpoint FastAPI que retorne resultados de busca semântica por FAISS."
- "Adicione tratamento de erros centralizado para todas rotas de API."
- "Crie um serviço Python que consuma o Obsidian Vault e gere embeddings." 

## MCP Tools
- `search_files` para localizar rotas, controllers e serviços.
- `read_file` para revisar handlers, schemas e configurações.
- `edit_file` para alterar lógica de API, validação e resposta.
- `execute_command` para rodar `pytest`, `uvicorn` ou scripts de migração.

## Padrões úteis
- Separe validação, lógica de negócio e camada de persistência.
- Use DTOs ou Pydantic/TypeScript types para contratos claros.
- Trate erros de forma consistente e retorne mensagens de API úteis.
- Documente os endpoints no README ou OpenAPI.

## Exemplo de fluxo
1. `search_files("backend/**/*api*" )`
2. `read_file("backend/app.py")`
3. `edit_file` para adicionar nova rota e validação.
4. `execute_command("pytest tests/test_api.py")`

## Modelos recomendados
- `mistralai/ministral-3-3b`
- `openai/gpt-4o-mini`
