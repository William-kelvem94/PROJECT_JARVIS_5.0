Arquivos globais de configuração para linting, formatação e tooling.

## Knowledge Base (Nova)
- `JARVIS_KB_PATH`: Caminho absoluto para a pasta de KB do Jarvis dentro do seu vault Obsidian.
  - Recomendado: use uma subpasta dedicada ao projeto, como `PROJECT_JARVIS_5.0-KnowledgeBase`.
  - O Jarvis lê arquivos `.md` dessa pasta para injetar conhecimento no contexto do agente.
- `JARVIS_VAULT_ROOT`: Raiz principal do seu vault Obsidian.
  - Use apenas para organizar o ambiente geral.
  - Opcional, mas útil para futuras features que precisem buscar o vault inteiro.

### Exemplo de organização
- `D:\OBSIDIAN\Will` — vault raiz geral.
- `D:\OBSIDIAN\Will\Projetos\Privados\PROJECT_JARVIS_5.0-KnowledgeBase` — KB específica do Jarvis.

Exemplo em `env/.env`:
```
JARVIS_KB_PATH=D:\OBSIDIAN\Will\Projetos\Privados\PROJECT_JARVIS_5.0-KnowledgeBase
JARVIS_VAULT_ROOT=D:\OBSIDIAN\Will
```

> Para melhor desempenho, prefira apontar `JARVIS_KB_PATH` para a pasta de notas que realmente deve ser usada pelo Jarvis, e não para o vault inteiro.

JARVIS usa esta KB para orientação precisa em projetos, documentação e decisões. A raiz do vault é um dado de organização adicional, não o local principal de ingestão.

Para o guia completo de organização e uso da KB do Jarvis, veja `../docs/KB_SETUP.md`.
