# 🧠 JARVIS 5.0 — Ecossistema de Inteligência Adaptativa

**Just A Rather Very Intelligent System** — um assistente de IA multimodal, autoconsciente do hardware onde roda, integrado a um segundo cérebro humano (Obsidian) e com motor de raciocínio em cascata.

---

## 🏗️ Arquitetura

```
┌──────────────────────────────────────────────────────────────┐
│                     FRONTEND (Next.js 15)                     │
│                Porta 3000 — Luxury Cockpit                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐ │
│  │ OrbCore  │  │ HudRing  │  │ Console  │  │ StatsStrip   │ │
│  └──────────┘  └──────────┘  └──────────┘  └──────────────┘ │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│                   BACKEND (FastAPI + Uvicorn)                  │
│                Porta 8000 (API) + Porta 8001 (Telemetria)     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐ │
│  │FaceEngine│  │YOLOv8    │  │Whisper   │  │Silero VAD    │ │
│  │(MediaPp) │  │(objetos) │  │(STT)     │  │(barge-in)    │ │
│  └──────────┘  └──────────┘  └──────────┘  └──────────────┘ │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐    │
│  │  Motor de IA em Cascata                              │    │
│  │  LM Studio → Gemini (cache 5min) → OpenRouter        │    │
│  │  Todos com streaming e timeout otimizado (5s)        │    │
│  └──────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Segundo Cérebro (Obsidian Vault)                       │   │
│  │  Grafo com NetworkX e memórias relacionadas             │   │
│  │  Leitura de memórias, TODOs, personas                  │   │
│  └──────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
```

---

## 🖥️ Hardware Suportado

| Máquina | Perfil | Detalhes |
|---------|--------|----------|
| Notebook | **CPU Moderno** | i7-12ª, 16GB RAM + swap, Intel Iris Xe |
| Desktop | **Força Bruta (CUDA)** | i3-10ª, 16GB RAM + swap, SSD DRAM-less, GTX 1050 Ti 4GB |

- Detecção automática de GPU
- Modelos de voz: `tiny` (GPU) ou `base` (CPU)
- Modo `LOW_VRAM` para GPUs com < 5GB
- Modo offline com Ollama

---

## 🚀 Quick Start

### Pré-requisitos

- Python 3.10+
- Node.js 20+
- pnpm (`npm install -g pnpm`)
- Git
- [LM Studio](https://lmstudio.ai/) (opcional, para modo offline total)

### Instalação

```bash
git clone https://github.com/William-kelvem94/PROJECT_JARVIS_5.0.git
cd PROJECT_JARVIS_5.0
```

### Executar

**Windows:** Duplo clique em `start-jarvis.bat`

**Manual:**
```bash
# Terminal 1 — Backend
cd backend
..\venv\Scripts\activate
uvicorn app.main:app --reload --port 8000

# Terminal 2 — Telemetria
uvicorn app.telemetry_server:app --port 8001

# Terminal 3 — Frontend
cd frontend
pnpm dev
```

### Acessar

| Serviço | URL |
|---------|-----|
| Cockpit | http://localhost:3000 |
| API | http://localhost:8000 |
| Telemetria | http://localhost:8001 |
| Dashboard | http://localhost:8001 |

---

## 🧪 Testes

```bash
cd backend
python -m pytest tests/ -v
```

---

## 🛠️ Tecnologias

**Backend:** Python, FastAPI, PyTorch, Ultralytics, MediaPipe, faster-whisper, Silero VAD, edge-tts, aiohttp, NetworkX, psutil

**Frontend:** Next.js 15, Tailwind CSS 4, Motion, Lucide React, Shadcn UI

**DevOps:** GitHub Actions, Windows Batch

---

## 🤝 Contribuindo

1. Faça um fork do projeto
2. Crie uma branch (`git checkout -b feat/nova-feature`)
3. Commit suas mudanças (`git commit -m 'feat: nova feature'`)
4. Push para a branch (`git push origin feat/nova-feature`)
5. Abra um Pull Request

---

## 📋 Próximos Passos

- [ ] Modo offline total (LLM local com Ollama)
- [ ] Internacionalização (i18n)
- [ ] Testes de integração com o frontend
- [ ] Dashboard de telemetria avançada
