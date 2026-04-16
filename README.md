# 🤖 Project Jarvis 5.0

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-000000?style=flat&logo=nextdotjs)](https://nextjs.org)

**Project Jarvis 5.0** é um ecossistema de assistência inteligente de próxima geração, integrando processamento de linguagem natural avançado, visão computacional e interações em tempo real. Construído com uma arquitetura monorepo robusta, combina a performance do Python no backend com a fluidez do Next.js no frontend, operando de forma 100% nativa e local.

---

## ✨ Funcionalidades Principais

- 🎙️ **Interação por Voz Local**: Latência ultra-baixa usando WebSockets nativos e processamento PCM local.
- 🧠 **Cérebro Híbrido**: Integração dinâmica com LM Studio (Local AI) e Gemini Fallback.
- 🖼️ **Visão Computacional**: Processamento e análise de imagens/vídeos em tempo real.
- 📊 **Dashboard de Monitoramento**: Acompanhamento de recursos do sistema e status da IA no HUD de Engenharia.
- 🛠️ **Automação de Sistema**: Capacidade de executar comandos e gerenciar tarefas locais.

---

## 🛠️ Stack Tecnológica

### Backend (Processamento & IA)
- **FastAPI**: Gateway de API de alta performance.
- **WebSocket**: Comunicação bidirecional para voz e telemetria.
- **Faster-Whisper & Edge-TTS**: Motores locais de STT e TTS.
- **Python-dotenv**: Gerenciamento seguro de configurações.
- **Psutil & Loguru**: Monitoramento robusto e logging avançado.

### Frontend (Interface & UX)
- **Next.js 15**: Framework React ultra-rápido.
- **Tailwind CSS & Shadcn/UI**: Design moderno e responsivo.
- **Framer Motion**: Micro-animações premium.
- **Native Web Audio API**: Processamento de áudio diretamente no browser.

---

## 🚀 Começando

### Pré-requisitos
- Node.js (v18+) e PNPM.
- Python 3.12+.
- Chave de API do Google Gemini (opcional para fallback).
- LM Studio rodando na rede local (opcional para 100% offline).

### Configuração de Ambiente

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/William-kelvem94/PROJECT_JARVIS_5.0.git
   cd PROJECT_JARVIS_5.0
   ```

2. **Variáveis de Ambiente:**
   Copie `env/.env.example` para `env/.env` e preencha as chaves necessárias.
   
   **Nova (KB):** Configure os caminhos de Obsidian para o Jarvis:
   ```
   JARVIS_KB_PATH=D:\OBSIDIAN\Will\Projetos\Privados\PROJECT_JARVIS_5.0-KnowledgeBase
   JARVIS_VAULT_ROOT=D:\OBSIDIAN\Will
   ```
   - `JARVIS_KB_PATH` deve apontar para a pasta de notas do Jarvis que será ingerida como base de conhecimento.
   - `JARVIS_VAULT_ROOT` é a raiz geral do seu vault Obsidian e pode ser usada para organização e futuras integrações.
   
   JARVIS carrega automaticamente os arquivos `.md` dessa KB durante o startup.
   Veja `docs/KB_SETUP.md` para um guia completo de configuração, organização e boas práticas.

3. **Backend Setup:**
   ```bash
   cd backend
   python -m venv venv
   # No Windows:
   .\venv\Scripts\activate
   # No Linux/Mac:
   source venv/bin/activate
   pip install -r app/requirements.txt
   ```

4. **Frontend Setup:**
   ```bash
   cd ../frontend
   pnpm install
   ```

---

## 🚦 Execução

Para facilitar o desenvolvimento, use o launcher oficial:

- **Iniciar Tudo:** Execute `start-jarvis.bat` na raiz.
- **Backend:** `cd backend && uvicorn app.main:app --reload`
- **Frontend:** `cd frontend && pnpm dev`

---

## 📂 Estrutura Fullstack Native

```text
├── backend/app/main.py             # Entry point FastAPI
├── backend/app/voice_websocket.py  # Motor de Voz WebSocket Local
├── frontend/context/JarvisContext.tsx # Gerenciador de Estado UI
└── start-jarvis.bat                # Launcher Auto-Suficiente
```

Para entender o fluxo completo de voz, visão, memória e IA, consulte `docs/ARCHITECTURE.md`.

---

## 📄 Licença
MIT - [LICENSE](frontend/LICENSE)

**Senior by William Kelvem + Antigravity AI**

## 🧪 Scripts úteis
- `pnpm dev` — inicia o frontend em modo dev.
- `pnpm start` — inicia o frontend em modo normal.
- `pnpm backend:dev` — inicia o backend FastAPI com reload.
- `pnpm docker:up` — sobe backend e frontend em containers.
- `pnpm docker:down` — derruba os containers.
- `pnpm test` — executa os testes unitários do backend.

---

## 📂 Estrutura Fullstack Senior

```text
├── backend/app/main.py     # FastAPI + LiveKit token
├── frontend/app/App.tsx    # LiveKit UI + reconnect
├── src/core/agents.py      # Gemini Realtime PRO
└── start-jarvis.bat        # Launcher 100%
```

Para entender o fluxo completo de voz, visão, memória e IA, consulte `docs/ARCHITECTURE.md`.

---

## 📄 Licença
MIT - [LICENSE](frontend/LICENSE)

**Senior by William Kelvem + BLACKBOXAI**

