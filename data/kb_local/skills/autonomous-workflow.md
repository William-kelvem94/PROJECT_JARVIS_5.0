# Autonomous Agent Workflows (AAW)

## Visão Geral
Este workflow define como um agente autônomo (como Antigravity ou JARVIS) deve interagir com este vault para maximizar a eficiência e manter a organização.

## Protocolo de Atuação
1. **Mapeamento Prévio:** Antes de qualquer alteração, o agente deve ler `Bem-vindo.md` e `Projetos.md`.
2. **Respeito às Cores:** Toda nova nota deve conter tags presentes no `Graph-Legenda.md` para manter a integridade visual.
3. **Memória Ativa:** Ao realizar mudanças estruturais, o agente deve registrar uma entrada em `JARVIS/Memorias/Episodicas/` com o resumo da sessão.
4. **Decisões Documentadas:** Mudanças em lógica ou arquitetura de projetos devem gerar um arquivo em `JARVIS/Decisoes/`.

## Ciclo de Trabalho (S.S.O.)
- **S**can: Escaneie o diretório e os arquivos de contexto.
- **S**ync: Garanta que os links internos e MOCs estão atualizados.
- **O**ptimize: Melhore a legibilidade e a estética da nota gerada.

## Ferramentas MCP Recomendadas
- `read_vault_file`: Para ler contexto profundo.
- `search_vault`: Para encontrar conexões entre projetos distantes.

---
*Este workflow foi gerado em colaboração com Antigravity durante a sessão de perfeccionamento do vault.* #skills #mcp #workflow
