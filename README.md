# 🤖 JARVIS AI Assistant v3.0

> **Assistente de IA Conversacional Completo com Arquitetura de Plugins**

Sistema profissional de IA conversacional com integração local (Ollama), plugins extensíveis (Voice, DeepSeek, Alexa), interface moderna React/TypeScript, e arquitetura completa Docker-ready.

![Version](https://img.shields.io/badge/version-3.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-brightgreen.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-00a393.svg)
![React](https://img.shields.io/badge/React-18.2-61dafb.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

---

## ✨ Features

### 🚀 Core
- ✅ **LLM Local Real** - Integração com Ollama (Llama2, Mistral, etc.)
- ✅ **Streaming em Tempo Real** - WebSocket com respostas progressivas
- ✅ **Autenticação JWT** - Sistema completo de login/registro
- ✅ **Banco de Dados** - PostgreSQL com histórico de conversas
- ✅ **Cache Redis** - Sessões e rate limiting
- ✅ **Sistema de Plugins** - Arquitetura extensível com hot-reload

### 🎨 Interface
- ✅ **Frontend Moderno** - React + TypeScript + Tailwind CSS
- ✅ **Design Futurista** - Glassmorphism, gradientes, animações
- ✅ **Responsivo** - Mobile-first design
- ✅ **Dark Mode** - Interface otimizada para longas sessões

### 🔌 Plugins Disponíveis
- ✅ **Voice Plugin** - Whisper STT + pyttsx3 TTS
- ✅ **DeepSeek Plugin** - Integração com API DeepSeek
- ✅ **Alexa Plugin** - Amazon Alexa Skills Kit

### 🛠️ DevOps
- ✅ **Docker & Docker Compose** - Deploy completo com um comando
- ✅ **Nginx Reverse Proxy** - Load balancing e SSL ready
- ✅ **Alembic Migrations** - Versionamento de banco de dados
- ✅ **Logging Avançado** - JSON logs com rotação
- ✅ **Health Checks** - Monitoramento de serviços

---

## 📋 Pré-requisitos

- Docker & Docker Compose
- (Opcional) NVIDIA GPU para Ollama

---

## 🚀 Quick Start

### 1. Clone o repositório
```bash
git clone https://github.com/seu-usuario/PROJECT_JARVIS_3.0.git
cd PROJECT_JARVIS_3.0
```

### 2. Configure as variáveis de ambiente
```bash
cp .env.example .env
# Edite .env com suas configurações
```

### 3. Inicie os serviços
```bash
docker-compose up -d
```

### 4. Aguarde a inicialização (primeira vez demora ~2-5min)
```bash
docker-compose logs -f backend
```

### 5. Acesse a aplicação
- **Frontend**: http://localhost
- **API Docs**: http://localhost:8000/api/docs
- **Backend Health**: http://localhost:8000/health

### 6. Primeiro acesso
1. Acesse http://localhost
2. Clique em "Registre-se"
3. Crie sua conta
4. Faça login e comece a usar!

---

## 🏗️ Arquitetura

```
PROJECT_JARVIS_3.0/
├── backend/                 # FastAPI Backend
│   ├── app/
│   │   ├── api/            # Rotas REST
│   │   │   └── routes/     # Auth, Chat, WebSocket, etc.
│   │   ├── core/           # Configuração, DB, Security
│   │   ├── models/         # SQLAlchemy Models
│   │   ├── schemas/        # Pydantic Schemas
│   │   ├── services/       # Business Logic
│   │   │   └── llm_service.py  # Integração Ollama
│   │   └── plugins/        # Sistema de Plugins
│   │       ├── voice_plugin.py
│   │       ├── deepseek_plugin.py
│   │       └── alexa_plugin.py
│   ├── alembic/            # Database Migrations
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/               # React + TypeScript Frontend
│   ├── src/
│   │   ├── components/     # Componentes React
│   │   │   ├── layout/    # Layout components
│   │   │   └── ui/        # UI components
│   │   ├── pages/          # Páginas da aplicação
│   │   ├── hooks/          # Custom Hooks (WebSocket)
│   │   ├── store/          # Zustand State Management
│   │   └── lib/            # API Client, Utils
│   ├── Dockerfile
│   ├── package.json
│   └── tailwind.config.js
│
├── nginx/                  # Nginx Config
│   └── nginx.conf
│
├── docker-compose.yml      # Orquestração de serviços
├── .env.example           # Exemplo de configuração
└── README.md              # Este arquivo
```

---

## 🔧 Configuração Avançada

### Ollama Models

Por padrão, o sistema usa `llama2`. Para adicionar outros modelos:

```bash
# Entre no container do Ollama
docker exec -it jarvis_ollama bash

# Baixe um modelo
ollama pull mistral
ollama pull codellama
ollama pull llama2:13b
```

### Plugins

#### Voice Plugin
Requer arquivos de áudio para STT:
```python
# Exemplo de uso no backend
from app.plugins.voice_plugin import VoicePlugin

plugin = VoicePlugin()
await plugin.initialize()

# Transcrever áudio
result = await plugin.transcribe_audio("audio.wav", language="pt")

# Text-to-Speech
await plugin.speak_text("Olá! Sou o Jarvis.", output_path="output.wav")
```

#### DeepSeek Plugin
Configure a API key no `.env`:
```bash
DEEPSEEK_API_KEY=your_api_key_here
```

#### Alexa Plugin
Configure credenciais Alexa no `.env`:
```bash
ALEXA_CLIENT_ID=your_client_id
ALEXA_CLIENT_SECRET=your_client_secret
```

---

## 📡 API Endpoints

### Autenticação
- `POST /api/v1/auth/register` - Registrar novo usuário
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/refresh` - Refresh token
- `POST /api/v1/auth/logout` - Logout

### Chat
- `POST /api/v1/chat` - Enviar mensagem (REST)
- `WS /api/v1/ws/chat?token=<JWT>` - Chat em tempo real (WebSocket)

### Conversas
- `GET /api/v1/conversations` - Listar conversas
- `POST /api/v1/conversations` - Criar conversa
- `GET /api/v1/conversations/{id}` - Obter conversa com mensagens
- `PUT /api/v1/conversations/{id}` - Atualizar conversa
- `DELETE /api/v1/conversations/{id}` - Deletar conversa

### Plugins (Admin)
- `GET /api/v1/plugins` - Listar plugins
- `POST /api/v1/plugins/{name}/enable` - Ativar plugin
- `POST /api/v1/plugins/{name}/disable` - Desativar plugin

**Documentação completa**: http://localhost:8000/api/docs

---

## 🛠️ Desenvolvimento

### Backend
```bash
cd backend

# Criar virtualenv
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt

# Rodar em modo dev
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend

# Instalar dependências
npm install

# Rodar em modo dev
npm run dev
```

### Migrations
```bash
# Criar nova migration
docker exec jarvis_backend alembic revision --autogenerate -m "description"

# Aplicar migrations
docker exec jarvis_backend alembic upgrade head

# Rollback
docker exec jarvis_backend alembic downgrade -1
```

---

## 🧪 Testes

```bash
# Backend tests
docker exec jarvis_backend pytest

# Frontend tests
cd frontend && npm test
```

---

## 📊 Monitoramento

### Logs
```bash
# Todos os serviços
docker-compose logs -f

# Apenas backend
docker-compose logs -f backend

# Apenas frontend
docker-compose logs -f frontend
```

### Health Checks
- Backend: http://localhost:8000/health
- PostgreSQL: `docker exec jarvis_postgres pg_isready`
- Redis: `docker exec jarvis_redis redis-cli ping`

---

## 🐛 Troubleshooting

### Ollama não inicializa
```bash
# Verificar logs
docker logs jarvis_ollama

# Verificar se tem GPU disponível
nvidia-smi  # Para NVIDIA GPUs
```

### Erro de conexão com banco
```bash
# Verificar se PostgreSQL está rodando
docker ps | grep postgres

# Recriar banco
docker-compose down -v
docker-compose up -d postgres
```

### Frontend não conecta no backend
Verifique as variáveis de ambiente no `.env`:
```bash
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

---

## 🚀 Deploy em Produção

### 1. Configure segredos fortes
```bash
# Gerar secret key forte
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 2. Use HTTPS
Configure SSL no Nginx:
```nginx
server {
    listen 443 ssl http2;
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    # ...
}
```

### 3. Environment em produção
```bash
ENVIRONMENT=production
DEBUG=False
LOG_LEVEL=INFO
```

### 4. Backup do banco
```bash
# Backup
docker exec jarvis_postgres pg_dump -U jarvis jarvis_db > backup.sql

# Restore
cat backup.sql | docker exec -i jarvis_postgres psql -U jarvis jarvis_db
```

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

---

## 📝 License

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## 👨‍💻 Autor

**Jarvis Team**

- GitHub: [@seu-usuario](https://github.com/seu-usuario)

---

## 🙏 Agradecimentos

- [FastAPI](https://fastapi.tiangolo.com/) - Framework web moderno
- [Ollama](https://ollama.ai/) - LLMs locais
- [React](https://react.dev/) - Biblioteca UI
- [Tailwind CSS](https://tailwindcss.com/) - Framework CSS
- [PostgreSQL](https://www.postgresql.org/) - Banco de dados
- [Redis](https://redis.io/) - Cache e sessões

---

## 📞 Suporte

Para suporte, abra uma [issue](https://github.com/seu-usuario/PROJECT_JARVIS_3.0/issues) ou entre em contato.

---

<div align="center">
  
**⭐ Se este projeto foi útil, deixe uma estrela! ⭐**

Made with ❤️ by Jarvis Team

</div>
