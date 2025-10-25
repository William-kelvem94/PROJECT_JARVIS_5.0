# 🏃 Rodar JARVIS Localmente (Sem Docker)

## 📋 Pré-requisitos

### 1. Python 3.11+
```powershell
# Verificar
python --version

# Se não tiver, baixe em:
# https://www.python.org/downloads/
```

### 2. Node.js 20+
```powershell
# Verificar
node --version

# Se não tiver, baixe em:
# https://nodejs.org/
```

### 3. PostgreSQL (Opcional - pode usar SQLite)
```powershell
# Download:
# https://www.postgresql.org/download/windows/
```

### 4. Redis (Opcional)
```powershell
# Download:
# https://github.com/microsoftarchive/redis/releases
```

### 5. Ollama
```powershell
# Download:
# https://ollama.ai/download/windows
```

---

## 🚀 Setup Rápido (SQLite - Sem Postgres/Redis)

### Backend

```powershell
# 1. Ir para backend
cd D:\Documents\GitHub\PROJECT_JARVIS_3.0\backend

# 2. Criar ambiente virtual
python -m venv venv
.\venv\Scripts\activate

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Criar .env simplificado
@"
DATABASE_URL=sqlite+aiosqlite:///./jarvis.db
REDIS_URL=memory://
OLLAMA_URL=http://localhost:11434
SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
CORS_ORIGINS=http://localhost:3000
DEBUG=True
ENVIRONMENT=development
"@ | Out-File -FilePath .env -Encoding utf8

# 5. Criar banco SQLite
alembic upgrade head

# 6. Iniciar backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Backend rodando em: http://localhost:8000**

### Frontend (Novo Terminal)

```powershell
# 1. Ir para frontend
cd D:\Documents\GitHub\PROJECT_JARVIS_3.0\frontend

# 2. Instalar dependências
npm install

# 3. Criar .env
@"
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
"@ | Out-File -FilePath .env -Encoding utf8

# 4. Iniciar frontend
npm run dev
```

**Frontend rodando em: http://localhost:3000**

### Ollama (Novo Terminal)

```powershell
# 1. Verificar se Ollama está instalado
ollama --version

# 2. Baixar modelo
ollama pull llama2

# 3. Testar
ollama run llama2 "Hello"
```

**Ollama rodando em: http://localhost:11434**

---

## ✅ Acessar

Abra: **http://localhost:3000**

---

## 🔧 Setup Completo (Com PostgreSQL + Redis)

### 1. PostgreSQL

```powershell
# Após instalar PostgreSQL, criar banco:
# Abra pgAdmin ou psql

createdb jarvis_db

# OU no psql:
psql -U postgres
CREATE DATABASE jarvis_db;
\q
```

### 2. Redis

```powershell
# Após instalar, iniciar:
redis-server
```

### 3. Backend com Postgres

```powershell
cd backend
.\venv\Scripts\activate

# Editar .env:
@"
DATABASE_URL=postgresql+asyncpg://postgres:sua_senha@localhost:5432/jarvis_db
REDIS_URL=redis://localhost:6379/0
OLLAMA_URL=http://localhost:11434
SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
CORS_ORIGINS=http://localhost:3000
DEBUG=True
"@ | Out-File -FilePath .env -Encoding utf8

# Migrations
alembic upgrade head

# Iniciar
uvicorn app.main:app --reload
```

---

## 📝 Comandos Úteis

### Backend
```powershell
# Ativar venv
.\venv\Scripts\activate

# Rodar
uvicorn app.main:app --reload

# Testes
pytest

# Migrations
alembic revision --autogenerate -m "description"
alembic upgrade head
```

### Frontend
```powershell
# Dev
npm run dev

# Build
npm run build

# Preview
npm run preview

# Lint
npm run lint
```

### Ollama
```powershell
# Listar modelos
ollama list

# Baixar modelo
ollama pull mistral

# Testar
ollama run llama2

# Remover modelo
ollama rm llama2
```

---

## 🔍 Troubleshooting Local

### "Porta já em uso"
```powershell
# Ver o que está usando a porta
netstat -ano | findstr :8000
netstat -ano | findstr :3000

# Matar processo (substitua PID)
taskkill /PID <numero> /F
```

### "Module not found"
```powershell
# Backend
cd backend
.\venv\Scripts\activate
pip install -r requirements.txt

# Frontend
cd frontend
rm -r node_modules
npm install
```

### "Database connection error"
```powershell
# Usar SQLite temporariamente
# No .env:
DATABASE_URL=sqlite+aiosqlite:///./jarvis.db
```

### "Redis connection error"
```powershell
# Desabilitar Redis temporariamente
# No .env:
REDIS_URL=memory://
```

---

## 🎯 Quando Docker Funcionar

Depois que corrigir o Docker, você pode voltar para o setup Docker que é muito mais fácil:

```powershell
docker-compose up -d --build
```

---

## 💡 Dicas

1. **SQLite é suficiente** para desenvolvimento local
2. **Ollama é essencial** - sem ele o chat não funciona
3. **Redis é opcional** - pode usar memória
4. **Mantenha 3 terminais abertos**: Backend, Frontend, Ollama
5. **Logs**: Olhe os terminais para ver erros

---

## 🆘 Precisa de Ajuda?

- Backend não inicia: Verifique .env e dependências
- Frontend erro 404: Backend está rodando?
- Chat não responde: Ollama está rodando?
- Banco de dados: Use SQLite para simplicidade

---

**Boa sorte! 🚀**

