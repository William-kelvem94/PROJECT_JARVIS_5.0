# ⚡ Início Rápido - JARVIS IA 5.0

## 🚀 Setup em 3 Passos

### 1️⃣ Instalar Docker Desktop
**Download**: https://www.docker.com/products/docker-desktop

### 2️⃣ Iniciar JARVIS
```powershell
docker-compose up -d
```

### 3️⃣ Acessar Interface
**URL**: http://localhost:8000

---

## 📥 Baixar Modelos (Primeira Vez)

Após iniciar o Docker, baixe os modelos:

```powershell
# Entrar no container Ollama
docker exec -it jarvis_ollama ollama pull codellama:7b
docker exec -it jarvis_ollama ollama pull deepseek-coder:6.7b
docker exec -it jarvis_ollama ollama pull llama2:7b
```

Ou use o script:
```powershell
.\scripts\setup-ollama.ps1
```

---

## ✅ Verificar se Está Funcionando

```powershell
# Status
curl http://localhost:8000/api/status

# Listar modelos
curl http://localhost:8000/api/models
```

---

## 🎯 Primeira Conversa

1. Abra: http://localhost:8000
2. Digite: "Olá, JARVIS!"
3. Aguarde resposta (primeira vez pode demorar ~10-30s)

---

## 🛑 Parar

```powershell
docker-compose down
```

---

## 🆘 Problemas?

### Porta 8000 ocupada?
```yaml
# Edite docker-compose.yml
ports:
  - "8001:8000"  # Use outra porta
```

### Ollama não conecta?
```powershell
# Verificar logs
docker-compose logs ollama

# Reiniciar
docker-compose restart ollama
```

---

**Pronto! Agora você tem uma IA local funcionando! 🎉**

