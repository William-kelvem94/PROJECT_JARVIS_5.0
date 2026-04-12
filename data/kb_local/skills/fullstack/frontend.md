---
tags: [skills]
---

# Frontend Skills - React/Vue/JS

## Prompts para OpenClaude
```
Crie um componente React com Tailwind para [descrição].
```

## Prompts avançados
- "Implemente um componente de chat com histórico e estado de carregamento em Next.js."
- "Melhore a acessibilidade deste formulário para usuários de teclado e leitores de tela."
- "Refatore este componente para usar um hook personalizado de validação."

## Ferramentas MCP
- `search_files` para localizar componentes e estilos.
- `read_file` para revisar JSX/TSX e CSS.
- `edit_file` para atualizar componentes, classes ou hooks.
- `execute_command` para rodar `pnpm lint` e `pnpm test`.

## Padrões úteis
- Separe layout de lógica usando hooks e componentes menores.
- Use utilitários de CSS como Tailwind em vez de estilos inline quando possível.
- Mantenha componentes com uma única responsabilidade.
- Teste interações com testes de integração ou Playwright.

## Exemplo de fluxo
1. `search_files("src/components/**/*Form*" )`
2. `read_file("src/components/LoginForm.tsx")`
3. `edit_file` para melhorar validação e acessibilidade.
4. `execute_command("pnpm lint && pnpm test")`

## Modelos recomendados
- `mistralai/ministral-3-3b`
- `openai/gpt-4o-mini`
