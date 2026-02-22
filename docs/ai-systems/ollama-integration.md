# 🦙 JARVIS 5.0 - Integração Ollama

**Executar Modelos de IA Localmente - 100% Offline e Grátis**

---

## 📖 O que é Ollama?

**Ollama** é uma plataforma que permite executar Large Language Models (LLMs) **localmente** no seu computador:
- 🆓 **100% Gratuito** (sem API keys)
- 🔒 **Privacidade Total** (dados não saem do seu PC)
- ⚡ **Rápido** (sem latência de rede)
- 📦 **Fácil** (instalação em 1 comando)

---

## 🚀 Instalação

### Windows

1. **Download:**
   - Acesse: https://ollama.com/download
   - Baixe: `OllamaSetup.exe`

2. **Instalar:**
   ```bash
   # Execute o instalador
   OllamaSetup.exe
   ```

3. **Verificar:**
   ```bash
   ollama --version
   # Deve retornar: ollama version is X.Y.Z
   ```

### Linux/Mac

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

---

## 📦 Modelos Disponíveis

### Recomendados para JARVIS

| Modelo | RAM | VRAM | Velocidade | Qualidade | Uso |
|--------|-----|------|------------|-----------|-----|
| **llama3.1:8b** | 8GB | 4GB | ⚡⚡⚡ | ⭐⭐⭐⭐ | Melhor geral |
| **mistral:7b** | 6GB | 3GB | ⚡⚡⚡⚡ | ⭐⭐⭐ | Rápido |
| **phi3:3b** | 4GB | 2GB | ⚡⚡⚡⚡⚡ | ⭐⭐ | PCs fracos |
| **codellama:7b** | 6GB | 3GB | ⚡⚡⚡ | ⭐⭐⭐⭐ | Programação |
| **deepseek-coder:6.7b** | 6GB | 3GB | ⚡⚡⚡ | ⭐⭐⭐⭐⭐ | Código avançado |

### Download de Modelo

```bash
# Baixar Llama 3.1 (8B - Recomendado)
ollama pull llama3.1

# Baixar Mistral (rápido)
ollama pull mistral

# Baixar Phi-3 (leve para PCs fracos)
ollama pull phi3

# Baixar CodeLlama (especializado em código)
ollama pull codellama
```

**Tempo de download:** ~5-10 minutos (depende da internet)

---

## ⚙️ Configuração no JARVIS

### 1. Verificar se Ollama está Rodando

```bash
ollama serve
```

Deve retornar: `Ollama is running on http://localhost:11434`

### 2. Configurar em `ai_config.yaml`

**Arquivo:** `config/ai_config.yaml`

```yaml
ai_models:
  ollama:
    enabled: true
    base_url: "http://localhost:11434"
    model: "llama3.1"  # ou mistral, phi3, etc.
    timeout: 30
    
    # Parâmetros de geração
    temperature: 0.7
    top_p: 0.9
    max_tokens: 2048
    
    # Performance
    num_ctx: 4096  # Contexto (quanto maior, mais memória)
    num_gpu: 1  # Quantas GPUs usar (0 = CPU only)
```

### 3. Ativar no Brain Router

```yaml
brain_router:
  mode: "priority"
  priority_list:
    - "ollama-llama3"  # Tenta Ollama primeiro
    - "gemini-flash"   # Fallback para cloud
    - "local-brain"    # Fallback final
```

---

## 🎯 Usar no JARVIS

### Método 1: Comando de Voz

```
"JARVIS, use Ollama local"
"JARVIS, mude para modelo local"
```

### Método 2: Dashboard

1. Control Dashboard → **Brain** tab
2. Dropdown: **Select Model**
3. Escolha: **Ollama - llama3.1**
4. Clique: **Apply**

### Método 3: Via Código

```python
from src.core.brain.ai_agent import AIAgent

agent = AIAgent()
agent.switch_brain("ollama-llama3")

response = agent.thinking("Explique aprendizado de máquina")
print(response)
```

---

## 🧪 Testar Ollama

### Teste no Terminal

```bash
# Testar diretamente
ollama run llama3.1

# Chat interativo
> Olá, como você está?
```

### Teste via API

```bash
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.1",
  "prompt": "Por que o céu é azul?"
}'
```

### Teste no JARVIS

1. Dashboard → Brain → **Test Brain**
2. Digite: "Explique física quântica"
3. Clique: **Send**

Se funcionar, verá resposta gerada localmente! 🎉

---

## 🔧 Otimização de Performance

### Para GPUs NVIDIA

Ollama usa automaticamente GPU se disponível.

**Verificar uso de GPU:**
```bash
nvidia-smi
```

**Forçar uso de GPU:**
```yaml
# ai_config.yaml
ollama:
  num_gpu: 1  # ou 99 para usar todas GPUs disponíveis
```

### Para PCs sem GPU (CPU Only)

Use modelos menores:

```yaml
ollama:
  model: "phi3:3b"  # Modelo leve
  num_gpu: 0  # Força CPU
  num_thread: 8  # Threads da CPU
```

### Reduzir Uso de RAM

```yaml
ollama:
  num_ctx: 2048  # Reduz contexto (padrão: 4096)
```

Isso reduz memória mas limita tamanho de conversas.

---

## 📊 Comparação: Ollama vs Cloud

| Característica | Ollama Local | Gemini Cloud |
|----------------|--------------|--------------|
| **Custo** | 🆓 Grátis | 🆓 Grátis (com limites) |
| **Velocidade** | ⚡⚡⚡ Rápido | ⚡⚡ Médio (depende internet) |
| **Privacidade** | 🔒 100% Local | ☁️ Dados na nuvem |
| **Qualidade** | ⭐⭐⭐ Boa | ⭐⭐⭐⭐ Excelente |
| **Hardware** | GPU recomendada | Não precisa |
| **Internet** | ❌ Não precisa | ✅ Obrigatório |
| **Rate Limits** | ❌ Sem limites | ✅ 15 RPM / 1M TPM |

**Quando usar Ollama:**
- Privacidade crítica
- Sem internet disponível
- Hardware bom (8GB+ RAM)
- Muitas requisições

**Quando usar Gemini:**
- Máxima qualidade
- Tarefas complexas
- Hardware fraco
- Visão/Imagens

---

## 🎨 Modelos Especializados

### Para Código

```bash
ollama pull codellama:7b
ollama pull deepseek-coder:6.7b
```

```yaml
brain_router:
  task_routing:
    coding: "ollama-codellama"
```

### Para Português

Llama 3.1 tem bom suporte a português!

```bash
ollama pull llama3.1
```

### Para Raciocínio Lógico

```bash
ollama pull qwen2.5:14b  # Excelente para matemática/lógica
```

---

## 🔧 Solução de Problemas

### "Ollama is not running"

**Soluções:**
1. Abrir terminal e rodar: `ollama serve`
2. No Windows, verificar serviço: `services.msc` → "Ollama"
3. Reinstalar Ollama

### "Model not found"

**Baixar modelo:**
```bash
ollama pull llama3.1
```

**Verificar modelos instalados:**
```bash
ollama list
```

### "Out of memory"

**Soluções:**
1. Usar modelo menor: `phi3:3b`
2. Reduzir contexto: `num_ctx: 2048`
3. Fechar outros programas

### "Very slow on CPU"

**Normal!** Modelos são pesados.

**Soluções:**
1. Usar modelo leve: `phi3`
2. Comprar GPU 😅
3. Usar Gemini cloud

---

## 📚 Recursos Adicionais

- **Site Oficial:** https://ollama.com
- **Todos os Modelos:** https://ollama.com/library
- **GitHub:** https://github.com/ollama/ollama
- **Discord:** https://discord.gg/ollama

---

## 🆘 Suporte JARVIS

- **Brain Router:** [brain-router.md](brain-router.md)
- **Local Brain:** [local-brain.md](local-brain.md)
- **Performance:** [../maintenance/performance.md](../maintenance/performance.md)

---

<div align="center">

**Sua IA. Seu PC. Sem Limitações. 🦙**

</div>
