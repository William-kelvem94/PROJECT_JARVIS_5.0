# 🚀 Quick Start Guide - JARVIS AI Assistant

## ⚡ Instalação Rápida (5 minutos)

### Pré-requisitos
- Docker Desktop instalado e rodando
- 8GB+ RAM disponível
- (Opcional) NVIDIA GPU para melhor performance

### Passo a Passo

#### 1. Clone o Repositório
```bash
git clone https://github.com/seu-usuario/PROJECT_JARVIS_3.0.git
cd PROJECT_JARVIS_3.0
```

#### 2. Instalação Automática (Recomendado)
```bash
# Linux/Mac
make install

# Windows (PowerShell)
./scripts/start.sh  # Se tiver WSL ou Git Bash
# OU use o Docker Compose manualmente:
docker-compose up -d --build
```

#### 3. Aguarde a Inicialização
```bash
# Acompanhe os logs
docker-compose logs -f backend

# Aguarde até ver:
# "Jarvis AI Assistant started successfully!"
```

#### 4. Acesse a Aplicação
Abra seu navegador em: **http://localhost**

#### 5. Crie sua Conta
1. Clique em "Registre-se"
2. Preencha:
   - Usuário: `admin`
   - Email: `admin@jarvis.local`
   - Senha: `Admin@123` (ou qualquer senha forte)
3. Clique em "Criar Conta"

#### 6. Faça Login
Use as credenciais que você criou

#### 7. Comece a Conversar! 🎉
Digite sua primeira mensagem no chat!

---

## 📱 Uso Básico

### Chat
1. Digite sua mensagem na caixa de texto
2. Pressione Enter ou clique em "Enviar"
3. Aguarde a resposta em tempo real (streaming)

### Criar Nova Conversa
- Clique no botão "+" na barra lateral
- Ou vá para `/chat` no menu

### Ver Conversas Antigas
- Menu lateral > "Chat"
- Lista de conversas aparece
- Clique para abrir

### Configurações
- Menu lateral > "Settings"
- Altere email, nome, senha

### Plugins
- Menu lateral > "Plugins"
- Ative/Desative plugins disponíveis

---

## 🔧 Comandos Úteis

### Makefile (Linux/Mac)
```bash
make help          # Ver todos os comandos
make up            # Iniciar serviços
make down          # Parar serviços
make logs          # Ver logs
make restart       # Reiniciar
make test          # Rodar testes
make clean         # Limpar tudo
```

### Docker Compose (Qualquer sistema)
```bash
# Iniciar
docker-compose up -d

# Parar
docker-compose down

# Ver logs
docker-compose logs -f

# Reiniciar um serviço
docker-compose restart backend

# Ver status
docker-compose ps
```

---

## 🤖 Gerenciar Modelos Ollama

### Listar Modelos Instalados
```bash
make ollama-list
# OU
docker exec jarvis_ollama ollama list
```

### Baixar Novos Modelos
```bash
# Mistral (melhor que Llama2, mais rápido)
make ollama-pull MODEL=mistral

# CodeLlama (para código)
make ollama-pull MODEL=codellama

# Llama2 13B (mais inteligente, mais lento)
make ollama-pull MODEL=llama2:13b

# OU manualmente:
docker exec jarvis_ollama ollama pull mistral
```

### Modelos Recomendados

| Modelo | Tamanho | Uso | RAM Necessária |
|--------|---------|-----|----------------|
| `llama2` | ~4GB | Geral (padrão) | 8GB |
| `mistral` | ~4GB | Melhor qualidade | 8GB |
| `codellama` | ~4GB | Programação | 8GB |
| `llama2:13b` | ~7GB | Alta qualidade | 16GB |
| `phi` | ~1.5GB | Rápido, leve | 4GB |

---

## 🔍 Troubleshooting

### "Backend não conecta"
```bash
# Verificar se está rodando
docker ps | grep jarvis

# Ver logs de erro
docker logs jarvis_backend

# Reiniciar
docker-compose restart backend
```

### "Ollama muito lento"
```bash
# Use modelo menor
make ollama-pull MODEL=phi

# Ou remova Ollama do docker-compose.yml
# e use API externa (OpenAI, DeepSeek)
```

### "Erro 'Port already in use'"
```bash
# Parar todos os serviços
docker-compose down

# Verificar portas em uso
# Linux/Mac:
lsof -i :8000
lsof -i :3000

# Windows (PowerShell):
netstat -ano | findstr :8000
```

### "Frontend mostra página em branco"
```bash
# Limpar cache do navegador
# Rebuildar frontend
docker-compose build frontend
docker-compose restart frontend
```

### "Database migration error"
```bash
# Resetar banco (APAGA TODOS OS DADOS!)
docker-compose down -v
docker-compose up -d postgres
sleep 5
docker-compose up -d backend
make migrate
```

---

## 💡 Dicas

### Performance
1. **Use SSD** para melhor performance do Docker
2. **Aumente RAM** do Docker Desktop (Settings > Resources)
3. **GPU NVIDIA**: O Ollama usa automaticamente se disponível

### Desenvolvimento
```bash
# Rodar apenas DB + Redis (economiza recursos)
make dev

# Depois rode manualmente:
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Em outro terminal:
cd frontend
npm install
npm run dev
```

### Backup
```bash
# Backup do banco
make backup-db

# Restaurar
make restore-db
```

### Atualização
```bash
# Puxar atualizações
git pull origin main

# Rebuild e restart
docker-compose down
docker-compose up -d --build
make migrate
```

---

## 🎯 Próximos Passos

1. **Explore os Plugins**
   - Ative o Voice Plugin para STT/TTS
   - Configure DeepSeek se tiver API key

2. **Personalize**
   - Troque o modelo Ollama
   - Ajuste temperatura nas conversas
   - Customize a interface

3. **Integre**
   - Use a API REST (docs em /api/docs)
   - Conecte com Alexa Skills
   - Crie seus próprios plugins

4. **Deploy**
   - Siga o guia de produção no README.md
   - Configure SSL com Let's Encrypt
   - Use cloud provider (AWS, GCP, Azure)

---

## 📚 Documentação Completa

- **README Principal**: `README.md`
- **API Docs**: http://localhost:8000/api/docs
- **Código-fonte**: Explore `backend/` e `frontend/`

---

## 🆘 Suporte

- **Issues**: https://github.com/seu-usuario/PROJECT_JARVIS_3.0/issues
- **Discussões**: https://github.com/seu-usuario/PROJECT_JARVIS_3.0/discussions

---

**Divirta-se com o JARVIS! 🤖✨**

