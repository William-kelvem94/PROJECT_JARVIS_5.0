# 🤖 JARVIS IA 5.0 - Assistente IA Local Gratuito

<div align="center">

![JARVIS](https://img.shields.io/badge/JARVIS-5.0-blue?style=for-the-badge)
![Ollama](https://img.shields.io/badge/Ollama-Local-green?style=for-the-badge)
![Docker](https://img.shields.io/badge/Docker-Ready-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge)

**Assistente de IA 100% Local, Gratuito e Profissional**

[🚀 Instalação Rápida](#-instalação-rápida) • [📖 Documentação](docs/INSTALL.md) • [🎯 Uso](#-como-usar)

</div>

---

## ✨ Características

### Core Features
- ✅ **100% Local** - Tudo roda na sua máquina, sem dependências de APIs externas
- ✅ **Gratuito** - Usa modelos open-source gratuitos via Ollama
- ✅ **Docker Ready** - Inicia tudo com um comando
- ✅ **Múltiplos Modelos** - Suporte para codellama, deepseek-coder, llama2, mistral e mais
- ✅ **Interface Web Moderna** - Chat em tempo real via WebSocket
- ✅ **API REST Completa** - Integre com qualquer aplicação
- ✅ **Plugins Modulares** - Sistema extensível de plugins
- ✅ **Produção Ready** - Pronto para deploy

### 🆕 Enhanced Features (New!)
- 🎤 **Wake Word Detection** - Ativação por voz com "Jarvis"
- 📅 **Google Calendar** - Integração completa com agenda
- 🌤️ **Weather Service** - Informações meteorológicas em tempo real
- 📰 **News Headlines** - Notícias atualizadas
- 📚 **Wikipedia Integration** - Consultas de conhecimento geral
- 📧 **Email Service** - Envio de emails por comando
- 🎭 **Entertainment** - Piadas, curiosidades e frases inspiradoras

**[📖 Ver Documentação Completa das Novas Features](docs/ENHANCED_FEATURES.md)**

---

## 🚀 Instalação Rápida

### Pré-requisitos

1. **Docker Desktop** - [Download](https://www.docker.com/products/docker-desktop)
2. **Ollama** (opcional, se não usar Docker) - [Download](https://ollama.com/download)

### Iniciar com Docker (Recomendado)

```powershell
# Clonar repositório (se aplicável)
git clone <seu-repositorio>

# Iniciar tudo
docker-compose -f docker/docker-compose.yml up -d

# Acessar interface
# http://localhost:8000
```

### Instalação Manual

```powershell
# 1. Instalar Ollama
# Baixe: https://ollama.com/download/OllamaSetup.exe

# 2. Baixar modelos
ollama pull codellama:7b
ollama pull deepseek-coder:6.7b

# 3. Instalar dependências Python
pip install -r requirements.txt

# 4. Iniciar servidor
python -m uvicorn core.main:app --reload
```

**📖 Veja o [Guia Completo de Instalação](docs/INSTALL.md)**

---

## 🎯 Como Usar

### 🆕 Demo das Novas Features

Teste todas as novas funcionalidades interativamente:

```bash
# Demo interativo com todas as features
python demo_enhanced_features.py
```

Modos disponíveis:
- **Modo Texto** - Entrada por teclado (não precisa de microfone)
- **Modo Voz** - Ativação por wake word "Jarvis"
- **Testes Rápidos** - Teste automático de todas as features

### Interface Web

1. Acesse: http://localhost:8000
2. Digite sua mensagem
3. Receba resposta em tempo real

### API REST

```bash
# Status do sistema
curl http://localhost:8000/api/status

# Chat
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Olá, JARVIS!"}'
```

### WebSocket

```javascript
const ws = new WebSocket('ws://localhost:8000/ws');
ws.onmessage = (e) => console.log(e.data);
ws.send('Olá, JARVIS!');
```

---

## 📦 Modelos Suportados

### Para Programação
- `codellama:7b` - Melhor para código Python, JavaScript
- `deepseek-coder:6.7b` - Especializado em programação
- `starcoder:1b` - Leve e rápido

### Para Conversação
- `llama2:7b` - Modelo geral versátil
- `mistral:7b` - Conversacional e rápido
- `neural-chat:7b` - Focado em diálogo

### Download Rápido

```powershell
.\scripts\setup-ollama.ps1
```

---

## 🏗️ Estrutura do Projeto

```
PROJECT_JARVIS_5.0/
├── core/               # Lógica principal
│   ├── main.py        # Servidor FastAPI
│   ├── jarvis.py      # Classe principal
│   ├── local_llm.py   # Integração Ollama
│   └── config.py      # Configurações
├── plugins/            # Plugins modulares
├── web/                # Interface web
├── config/             # Arquivos de configuração
├── scripts/            # Scripts utilitários
├── docs/               # Documentação
├── docker/             # Arquivos Docker
│   ├── docker-compose.yml
│   └── Dockerfile
└── requirements.txt    # Dependências Python
```

---

## ⚙️ Configuração

### `config/config.json`

```json
{
  "llm_provider": "ollama",
  "ollama_base_url": "http://localhost:11434",
  "ollama_model": "codellama:7b",
  "voice_api": "local",
  "web_interface": true
}
```

### Variáveis de Ambiente

```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=codellama:7b
LLM_PROVIDER=ollama
```

---

## 🔧 Comandos Úteis

### Docker

```powershell
# Iniciar
docker-compose -f docker/docker-compose.yml up -d

# Parar
docker-compose -f docker/docker-compose.yml down

# Ver logs
docker-compose -f docker/docker-compose.yml logs -f jarvis

# Reconstruir com otimizações
.\scripts\docker-rebuild.ps1

# Monitorar performance
.\scripts\docker-monitor.ps1
```

### Ollama

```powershell
# Listar modelos
ollama list

# Baixar modelo
ollama pull codellama:7b

# Remover modelo
ollama rm codellama:7b
```

---

## 🎨 Recursos

- ✅ Chat em tempo real
- ✅ API REST completa
- ✅ WebSocket para comunicação bidirecional
- ✅ Gerenciamento de modelos
- ✅ Suporte a plugins
- ✅ Interface web responsiva
- ✅ Logs detalhados

---

## 📊 Requisitos

### Mínimo
- RAM: 8GB
- Disco: 10GB
- CPU: Dual-core 2GHz+

### Recomendado
- RAM: 16GB+
- Disco: 20GB+
- CPU: Quad-core 3GHz+
- GPU: NVIDIA 6GB+ VRAM (opcional, acelera muito)

---

## 🐛 Troubleshooting

### Ollama não conecta
```powershell
# Verificar se está rodando
curl http://localhost:11434/api/tags

# Reiniciar
ollama serve
```

### Docker não inicia
```powershell
# Ver logs
docker-compose logs -f

# Reconstruir
docker-compose -f docker/docker-compose.yml up --build -d
```

**Veja mais em [INSTALL.md](docs/INSTALL.md#-troubleshooting)**

---

## 📚 Documentação

- [Guia Completo de Instalação](docs/INSTALL.md)
- [🆕 Enhanced Features - Novas Funcionalidades](docs/ENHANCED_FEATURES.md)
- [Otimizações de Performance](docs/PERFORMANCE.md)
- [API Documentation](http://localhost:8000/docs) (após iniciar)
- [Modelos Disponíveis](docs/README_MODELS.md)

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Sinta-se livre para:
- Reportar bugs
- Sugerir features
- Enviar pull requests

---

## 📄 Licença

Este projeto é open-source e gratuito para uso pessoal e comercial.

---

## 🙏 Agradecimentos

### Core Technologies
- **Ollama** - Por tornar IA local acessível
- **FastAPI** - Framework web moderno
- **Comunidade Open Source** - Por todos os modelos disponíveis

### 🆕 Inspirado Pelos Melhores JARVIS Projects
As novas features foram inspiradas e combinadas dos melhores projetos JARVIS open-source:
- **[llm-guy/jarvis](https://github.com/llm-guy/jarvis)** - Wake word detection & conversation management
- **[Gladiator07/JARVIS](https://github.com/Gladiator07/JARVIS)** - Comprehensive integrations (Calendar, Weather, News, Wikipedia)
- **[kishanrajput23/Jarvis-Desktop-Voice-Assistant](https://github.com/kishanrajput23/Jarvis-Desktop-Voice-Assistant)** - Voice control patterns
- **[danilofalcao/jarvis](https://github.com/danilofalcao/jarvis)** - Multi-model AI concepts
- **[Code-A2Z/jarvis](https://github.com/Code-A2Z/jarvis)** - Security & authentication patterns
- **[projectswithdigambar/jarvis](https://github.com/projectswithdigambar/jarvis)** - Desktop automation ideas

Um agradecimento especial a todos os desenvolvedores desses projetos por suas contribuições inovadoras! 🙏

---

<div align="center">

**Desenvolvido com ❤️ usando tecnologias Open Source**

[⭐ Dê uma estrela se gostou!](#)

</div>
