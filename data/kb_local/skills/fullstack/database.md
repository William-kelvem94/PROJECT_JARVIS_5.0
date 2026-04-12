---
tags: [skills]
---

# Database Skills - SQL/NoSQL

## Prompts para design de dados
```
Crie schema Postgres para e-commerce.
Gere migrations Prisma.
```

## Prompts avançados
- "Projete um modelo de dados para armazenar memórias de usuário com versão e timestamp."
- "Otimize esta consulta SQL para reduzir joins e melhorar a performance."
- "Escreva uma migration Prisma para adicionar um índice semântico aos dados de embeddings."

## MCP Tools
- `search_files` para encontrar models, migrations e queries.
- `read_file` para revisar schema, consultas e scripts.
- `edit_file` para ajustar campos, índices e relacionamentos.
- `execute_command` para rodar `npx prisma migrate dev` ou testes de banco.

## Padrões úteis
- Modele dados para consultas reais, não apenas para armazenamento.
- Use índices e normalização quando necessário.
- Mantenha a consistência de naming entre entidades e campos.
- Crie migrations pequenas e revertíveis.

## Exemplo de fluxo
1. `search_files("prisma/schema.prisma")`
2. `read_file("prisma/schema.prisma")`
3. `edit_file` para adicionar novos campos ou índices.
4. `execute_command("npx prisma migrate dev")`

## Modelos recomendados
- `mistralai/ministral-3-3b`
- `openai/gpt-4o-mini`

## Exemplo de uso em Mongo
- `search_files("src/**/*mongo*" )`
- `read_file("src/db/mongo.py")`
- `edit_file` para melhorar pipeline de agregação.
