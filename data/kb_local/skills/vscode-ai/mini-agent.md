# Mini-Agent de IA para VS Code

Este mini-agent é um guia de fluxo para usar IA no VS Code com leitura, edição e validação de código.

## Objetivo
Criar um agente leve que:
- entenda o contexto do código,
- faça mudanças seguras,
- valide com testes,
- produza um resumo final.

## Ferramentas suportadas
- `search_files`
- `read_file`
- `edit_file`
- `create_file`
- `execute_command`

## Fluxo do mini-agent
1. **Entender o contexto**
   - Localize os arquivos relevantes.
   - Leia o conteúdo e as funções envolvidas.

2. **Planejar a mudança**
   - Defina o objetivo final em 2-3 frases.
   - Liste os passos: arquivos, mudanças e validações.

3. **Executar**
   - Faça alterações com `edit_file`.
   - Crie arquivos novos quando necessário.

4. **Validar**
   - Rode testes ou lint.
   - Verifique se não há regressões.

5. **Resumir**
   - Crie um breve resumo da mudança.
   - Liste arquivos alterados e comandos executados.

## Exemplo de prompt do agente
"Você é um assistente de desenvolvimento. Meu objetivo é [objetivo].
Use `search_files` para encontrar arquivos relevantes em `Projetos/Privados/PROJECT_JARVIS_5.0`, depois `read_file` para entender o contexto.
Planeje as mudanças necessárias, aplique-as com `edit_file` e valide com `execute_command`.
No final, escreva um resumo curto das alterações e dos resultados." 

## Regras do mini-agent
- Antes de editar, sempre leia o arquivo completo relevante.
- Não faça mudanças amplas em mais de três arquivos sem plano.
- Se o projeto tiver testes, execute-os após a alteração.
- Sempre preserve comentários e estilo existentes quando possível.

## Exemplo de caso real
1. Objetivo: corrigir bug no backend de voz.
2. Passos:
   - `search_files` por `voice` e `audio` em `PROJECT_JARVIS_5.0`.
   - `read_file` do módulo de captura de voz.
   - `edit_file` para melhorar tratamento de entrada.
   - `execute_command` para rodar o teste de integração.
   - `summarize` as mudanças.

## Configuração de uso no VS Code
- Abra o arquivo `skills/vscode-ai/mini-agent.md` para consulta.
- Use o prompt no seu chat de IA local (OpenClaude, Ollama ou outro).
- Opcional: crie um comando personalizado no VS Code para carregar este fluxo.

## Sugestão de metas
- Adicionar novo endpoint de RAG.
- Melhorar documentação de `PROJECT_JARVIS_5.0`.
- Criar testes para a memória persistente.
