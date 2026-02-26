## 6. Otimização e Monitoramento

Adicione scripts de monitoramento para evitar travamentos:

```powershell
cd scripts
./monitor-heartbeat.ps1
```
Este script reinicia backend/frontend se travarem.

O backend expõe `/health` para checagem.
# Instruções de Instalação e Execução

Este guia leva você do zero até um Jarvis funcional em sua máquina Windows.

---

## 1. Pré-requisitos

- Node.js (v18+)
- Python 3.11+ instalado e disponível no PATH
- `npm` (vem com Node)
- (Opcional) Docker/Docker Compose para rodar em contêineres


## 2. Variáveis de Ambiente

1. Copie o template:
   ```powershell
   copy env\.env.example env\.env
   ```
2. Preencha as chaves de API dentro de `env\.env` (GEMINI, LIVEKIT, etc.).
3. Para que o frontend/Next consiga ler as variáveis do lado do servidor, copie o arquivo
   raiz para `frontend/.env.local` ou exporte as mesmas variáveis no ambiente. Por exemplo:
   ```powershell
   copy env\.env frontend\.env.local
   ```
   (o script `start-jarvis.bat` faz isso automaticamente).
4. **Importante:** tenha sempre o backend rodando antes de iniciar o frontend. O
   frontend monta componentes pesados (visualizador, captura de microfone) apenas
   quando a sessão estiver realmente conectada – mas se o servidor estiver ausente,
   ele pode tentar reconectar indefinidamente, consumindo CPU e mostrando "sessão
   finalizada". Use `start-jarvis.bat` ou lance o backend manualmente.
5. Se preferir, também atualize `frontend\.env.example` e `backend\.env.example`.

> **Atenção:** nunca comite o arquivo `.env` com informações reais.

---

## 3. Preparar o Frontend

1. Instale o gerenciador pnpm (uma vez):
   ```powershell
   npm install -g pnpm
   ```
2. Vá para a pasta do frontend e instale dependências:
   ```powershell
   cd frontend
   # se "pnpm" não estiver no PATH, use npx:
   pnpm install        # ou `npx pnpm install`
   ```
3. Execute o servidor de desenvolvimento:
   ```powershell
   pnpm dev            # ou `npx pnpm dev`
   ```
   - O app ficará disponível em `http://localhost:3000`.
   - Não é necessário estar no virtualenv Python; comandos Node são independentes.

---

## 4. Preparar o Backend

1. Crie e ative um ambiente virtual Python:
   ```powershell
   cd backend
   python -m venv venv
   .\venv\Scripts\activate
   ```
2. Atualize o pip e instale dependências:
   ```powershell
   pip install --upgrade pip
   pip install -r app/requirements.txt
   ```
3. Execute o servidor FastAPI:
   ```powershell
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
   - O serviço responde em `http://localhost:8000`.
   - Teste: `curl http://localhost:8000/health` deve retornar `{"status":"ok"}`.


## 5. Atalho com scripts

Na raiz do repositório você encontra helpers:

```powershell
bash scripts/run-backend.sh    # prepara venv e inicia backend
bash scripts/run-frontend.sh   # instala pnpm e inicia frontend
bash scripts/run-all.sh        # rodar ambos (em shells distintos ou tmux)
```

Além disso existe um batch para Windows que abre duas janelas automaticamente:

```bat
start-jarvis.bat
```

Ao executar ele:

1. Cria/atualiza o `venv` e instala dependências Python (se ainda não existir).
2. Abre uma janela com o backend (`uvicorn`).
3. Abre uma janela com o frontend (`pnpm dev` via `npx`).

Para usar em PowerShell, execute `bash scripts/run-backend.sh` ou `.
start-jarvis.bat` diretamente.

---

## 6. Usando Docker

1. Configure `env/.env` com as mesmas variáveis.
2. Execute:
   ```powershell
   cd docker
   docker compose up --build
   ```
3. O frontend estará em `localhost:3000` e o backend em `localhost:8000`.

---

## 7. Testes

- Testes backend (Python):
  ```powershell
  cd backend
  .\venv\Scripts\activate
  pytest tests
  ```
- Frontend não possui testes automatizados por enquanto.

---

## 8. Próximos passos de desenvolvimento

- Implemente rotas reais (`/chat`, `/memory`, `/livekit-token`).
- Consuma essas rotas no frontend (`frontend/app/api` ou diretamente com `fetch`).
- Substitua o stub de memória (`mem0.py`) pelo cliente real.
- Atualize `integration-plan.md` conforme evoluir.

Boa codificação! 🚀
