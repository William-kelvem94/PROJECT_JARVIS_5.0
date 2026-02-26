# Project Jarvis 5.0

Monorepo para assistente Jarvis com frontend Next.js e backend Python.

## Estrutura
Veja `integration-plan.md` para detalhes completos.

## Setup local
1. Copie `env/.env.example` para `env/.env` e adicione chaves.
2. Execute `pnpm install` (na raiz instalará frontend) ou `cd frontend && pnpm install`.
3. Configure ambiente Python:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate
   pip install -r app/requirements.txt
   ```
4. Rode backend: `uvicorn backend.app.main:app --reload`
5. Rode frontend: `cd frontend && pnpm dev`

## Scripts
Veja `scripts/` para helpers (`run-backend.sh`, `run-frontend.sh`, `run-all.sh`).

### Monitoramento automático
Para evitar lentidão e travamentos, rode o script de monitoramento:

```powershell
cd scripts
./monitor-heartbeat.ps1
```
Esse script reinicia backend/frontend se travarem.

O backend expõe `/health` para checagem.

## Deploy
Use Dockerfiles em `docker/` e `docker/docker-compose.yml`.

## CI/CD
A pipeline está em `.github/workflows/ci.yml`.

## Observações
- Armazene chaves de API de forma segura.
- Use `shared/` para tipos e utilitários comuns.
