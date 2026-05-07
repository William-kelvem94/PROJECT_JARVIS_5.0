# Scripts JARVIS 5.0

Diretório centralizado de scripts de automação, inicialização e diagnóstico.

> O ponto de entrada oficial continua sendo `start-jarvis.bat` na raiz.
> O arquivo `scripts/start-jarvis.bat` é suporte modular, não substitui o entry point principal.
> Para Docker, o compose oficial é `docker-compose.yml` na raiz do repositório.

## Principais entradas

- `start-jarvis.bat` — boot adaptativo do JARVIS (Windows)
- `start.bat` — alias legado para boot

### Fluxo recomendado

1. `start-jarvis.bat`
2. `scripts/start-jarvis.bat` (modo modular interno)
3. `scripts/run-all.sh` (Linux/WSL)

### Raiz do projeto

- O repositório original continua sendo `PROJECT_JARVIS_5.0`
- Não dependa de caminhos absolutos de máquina
- Use a raiz calculada pelos próprios scripts

## Ambientes

- `.env` na raiz é a fonte principal de configuração
- `env/.env` é apenas override local quando necessário
- `frontend/.env.example` documenta as variáveis do frontend

## Scripts de apoio

- `check-prerequisites.bat` — valida Python, Node e gerenciadores
- `detect-hardware.bat` — detecta GPU e define modo
- `setup-venv.bat` — cria/atualiza o virtualenv
- `launch-backend.bat` — sobe o backend FastAPI
- `launch-frontend.bat` — sobe o frontend quando disponível
- `run-backend.sh` / `run-frontend.sh` / `run-all.sh` — atalhos para Unix-like

## Diagnóstico

- `auditoria_jarvis.py` — auditoria estática do código-fonte
- `verify_jarvis.py` — verificação funcional do ecossistema
- `diagnostics/` — checks pontuais e testes manuais
