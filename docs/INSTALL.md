# Instruções de Instalação e Execução

Este guia cobre instalação manual, execução separada e ambientes alternativos.
Para boot normal, siga primeiro `docs/guides/JARVIS_STARTUP.md` e use `start-jarvis.bat`.

## 1. Pré-requisitos

- Python 3.11+
- Node.js 18+
- npm / pnpm
- Git
- (Opcional) Docker / Docker Compose

## 2. Configuração básica

1. Copie o template de ambiente:
   ```powershell
   copy frontend\.env.example .env
   ```
2. Preencha as chaves necessárias em `.env`.
3. Se for rodar o frontend sozinho, copie também as variáveis para `frontend/.env.local`.

> Nunca commite `.env` com segredos reais.

## 3. Boot oficial

Use apenas um destes caminhos:

- `start-jarvis.bat` na raiz do repositório
- `docs/guides/JARVIS_STARTUP.md` para o fluxo e troubleshooting

## 4. Frontend isolado

```powershell
cd frontend
pnpm install
pnpm dev
```

Acesse `http://localhost:3000`.

## 5. Backend isolado

```powershell
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install --upgrade pip
pip install -r app/requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Teste:

```powershell
curl http://localhost:8000/health
```

## 6. Scripts auxiliares

- `scripts/run-backend.sh`
- `scripts/run-frontend.sh`
- `scripts/run-all.sh`

## 7. Docker

Se o suporte Docker estiver completo no seu ambiente, use o `docker-compose.yml` da raiz.
O arquivo `docker/docker-compose.yml` é apenas referência histórica.

## 8. Testes

```powershell
cd backend
pytest tests
```
