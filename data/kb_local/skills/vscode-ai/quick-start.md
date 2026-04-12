# Quick Start — VS Code AI

Este guia mostra como configurar rapidamente o ambiente de IA no seu workspace `d:\Documents\GitHub\Will-obsidian`.

## 1. Abra o vault no VS Code
- Execute:
  ```powershell
  code d:\Documents\GitHub\Will-obsidian
  ```
- Use o workspace principal para acessar `skills/`, `Projetos/`, `Will-Pessoal/` e `JARVIS/`.

## 2. Configure o ambiente Python
- Crie e ative o virtualenv:
  ```powershell
  python -m venv .venv
  .\.venv\Scripts\Activate.ps1
  ```
- Atualize pip:
  ```powershell
  python -m pip install --upgrade pip
  ```
- Instale dependências básicas (se houver `requirements.txt` ou `pyproject.toml`):
  ```powershell
  pip install -r requirements.txt
  ```

## 3. Configure o ambiente Node.js
- Instale dependências se houver `package.json`:
  ```powershell
  pnpm install
  ```
- Use `pnpm` como padrão quando o projeto indicar.

## 4. Instale um modelo local de IA
- Para Ollama local, baixe e instale o Ollama.
- Carregue modelo local recomendado, por exemplo:
  ```powershell
  ollama pull llama2
  ```
- Para usar Mistral localmente, instale via Ollama ou outro runtime compatível.

## 5. Configure variáveis de ambiente básicas
- Crie um arquivo `.env` na raiz do projeto com:
  ```env
  JARVIS_VAULT_ROOT=D:\Documents\GitHub\Will-obsidian
  JARVIS_PROJECT_ROOT=D:\Documents\GitHub\Will-obsidian\Projetos\Privados\PROJECT_JARVIS_5.0
  ```
- No PowerShell, você também pode definir temporariamente:
  ```powershell
  $env:JARVIS_VAULT_ROOT = 'D:\Documents\GitHub\Will-obsidian'
  ```

## 6. Inicie o projeto PROJECT_JARVIS_5.0
- Abra a pasta do projeto se precisar isolar o código:
  ```powershell
  code d:\Documents\GitHub\Will-obsidian\Projetos\Privados\PROJECT_JARVIS_5.0
  ```
- Se houver Docker:
  ```powershell
  docker compose up --build
  ```
- Se houver backend Python:
  ```powershell
  .\.venv\Scripts\Activate.ps1
  python backend/app.py
  ```

## 7. Valide com testes e lint
- Execute testes Python:
  ```powershell
  pytest
  ```
- Execute lint Javascript/TypeScript:
  ```powershell
  pnpm lint
  ```

## 8. Use o mini-agent de IA no VS Code
- Abra `skills/vscode-ai/mini-agent.md`.
- Copie os prompts e fluxos para seu agente local ou extensão de chat.

## Dicas rápidas
- Use `skills/vscode-ai/prompts.md` para gerar tarefas automaticamente.
- Use `skills/vscode-ai/mcp.md` para guiar ações de leitura/edição/execução.
- Salve escolhas úteis em `skills/vscode-ai/templates.md`.
