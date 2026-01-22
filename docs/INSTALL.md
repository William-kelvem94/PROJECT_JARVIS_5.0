# 🚀 Guia de Instalação - JARVIS IA 5.0

## 📋 Pré-requisitos

### 1. Instalar Docker Desktop
🔗 **Download**: https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe

### 2. Instalar Git (opcional, para clonar repositório)
🔗 **Download**: https://github.com/git-for-windows/git/releases/download/v2.45.1.windows.1/Git-2.45.1-64-bit.exe

---

## 🛠️ Instalação Rápida com Docker

### Método 1: Docker Compose (Recomendado)

```powershell
# 1. Iniciar todos os serviços (Ollama + JARVIS)
docker-compose up -d

# 2. Verificar status
docker-compose ps

# 3. Ver logs
docker-compose logs -f jarvis

# 4. Acessar interface
# http://localhost:8000
```

### Método 2: Instalação Manual

#### Passo 1: Instalar Ollama Localmente

1. Baixe: https://ollama.com/download/OllamaSetup.exe
2. Instale e inicie o Ollama
3. Baixe modelos essenciais:

```powershell
ollama pull codellama:7b
ollama pull deepseek-coder:6.7b
ollama pull llama2:7b
ollama pull mistral:7b
```

#### Passo 2: Instalar JARVIS

```powershell
# Criar ambiente virtual
python -m venv venv
venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt

# Iniciar servidor
python -m uvicorn core.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 📦 Modelos Recomendados

### Para Programação (Código)
- `codellama:7b` - Melhor para código Python, JavaScript, etc.
- `deepseek-coder:6.7b` - Especializado em programação

### Para Conversação Geral
- `llama2:7b` - Modelo geral versátil
- `mistral:7b` - Conversacional e rápido
- `neural-chat:7b` - Focado em diálogo

### Para Tarefas Específicas
- `starcoder:1b` - Leve e rápido para código simples
- `dolphin-mistral:7b` - Melhor para instruções detalhadas

### Baixar Todos os Essenciais

```powershell
# Execute o script
.\scripts\setup-ollama.ps1
```

---

## ⚙️ Configuração

### Arquivo `config/config.json`

```json
{
  "llm_provider": "ollama",
  "ollama_base_url": "http://localhost:11434",
  "ollama_model": "codellama:7b",
  "voice_api": "local",
  "web_interface": true
}
```

### Variáveis de Ambiente (Docker)

No `docker-compose.yml` ou `.env`:

```env
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL=codellama:7b
LLM_PROVIDER=ollama
```

---

## 🎯 Uso

### Interface Web
1. Abra: http://localhost:8000
2. Digite sua mensagem no chat
3. Receba resposta do JARVIS

### API REST

```bash
# Status do sistema
curl http://localhost:8000/api/status

# Chat
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Olá, JARVIS!"}'

# Listar modelos
curl http://localhost:8000/api/models

# Baixar modelo
curl -X POST "http://localhost:8000/api/models/pull?model_name=codellama:7b"
```

### WebSocket

```javascript
const ws = new WebSocket('ws://localhost:8000/ws');
ws.onmessage = (e) => console.log(e.data);
ws.send('Olá, JARVIS!');
```

---

## 🔧 Troubleshooting

### Ollama não está conectado

```powershell
# Verificar se Ollama está rodando
curl http://localhost:11434/api/tags

# Reiniciar Ollama
ollama serve
```

### Docker não inicia

```powershell
# Parar tudo
docker-compose down

# Reconstruir
docker-compose up --build -d

# Ver logs
docker-compose logs -f
```

### Modelo não encontrado

```powershell
# Listar modelos instalados
ollama list

# Baixar modelo específico
ollama pull codellama:7b

# Verificar no JARVIS
curl http://localhost:8000/api/models
```

### Porta 8000 em uso

Edite `docker-compose.yml` e altere:

```yaml
ports:
  - "8001:8000"  # Use outra porta
```

---

## 📊 Requisitos de Sistema

### Mínimo
- **RAM**: 8GB (para modelos 7B)
- **Disco**: 10GB livres
- **CPU**: Dual-core 2GHz+

### Recomendado
- **RAM**: 16GB+
- **Disco**: 20GB+ livres
- **CPU**: Quad-core 3GHz+ ou GPU NVIDIA com CUDA
- **GPU**: NVIDIA com 6GB+ VRAM (opcional, acelera muito)

---

## 🚀 Performance

### Primeira Execução
- Download de modelos: 5-30 minutos (depende da internet)
- Primeira resposta: 10-30 segundos (modelo carrega)
- Respostas seguintes: 1-5 segundos

### Otimizações
1. Use GPU se disponível (acelera 10x)
2. Modelos menores (1B-3B) são mais rápidos
3. Ajuste `num_predict` para respostas mais curtas

---

## 📝 Próximos Passos

1. ✅ Instalar Docker
2. ✅ Baixar modelos
3. ✅ Iniciar JARVIS
4. 🎉 Começar a usar!

---

## 💡 Dicas

- Comece com `codellama:7b` - equilíbrio perfeito
- Use `deepseek-coder:6.7b` para código complexo
- `mistral:7b` é excelente para conversação
- Mantenha 2-3 modelos instalados (não precisa de todos)

---

## 🆘 Suporte

- Ver logs: `docker-compose logs -f jarvis`
- Status: http://localhost:8000/api/status
- Verificar Ollama: http://localhost:11434/api/tags

---

**Desenvolvido com ❤️ usando Ollama - IA Local Gratuita e Open Source**

