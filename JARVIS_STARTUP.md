# JARVIS 5.0 - Sistema de Inicialização

## ⚡ Quick Start

### Opção 1: Iniciar JARVIS (Recomendado)
```batch
start-jarvis.bat
```

Ou clique duas vezes em `start-jarvis.bat` na raiz do projeto.

---

## 📋 Pré-Requisitos

- **Python 3.11+** (instalado e no PATH)
  - [Baixar Python](https://python.org/downloads)
  - ⚠️ **Importante**: Marque "Add Python to PATH" durante instalação
- **Node.js 16+** (opcional, para frontend)
- **Git** (para controle de versão)

### Se Python não estiver no PATH:

1. Instale Python 3.11+: https://python.org/downloads
2. **Durante a instalação, MARQUE a opção "Add Python to PATH"**
3. Reinicie o PC
4. Execute `start-jarvis.bat` novamente

---

## 📁 Estrutura de Inicialização

### Arquivos Principais

```
PROJECT_JARVIS_5.0/
├── start-jarvis.bat          ← EXECUTAR ESTE ARQUIVO (entry point)
├── start.bat                 ← Alias alternativo
├── scripts/
│   ├── common-functions.bat  ← Funções compartilhadas
│   ├── check-prerequisites.bat
│   ├── detect-hardware.bat
│   ├── setup-venv.bat
│   ├── launch-backend.bat
│   ├── launch-frontend.bat
│   └── (outros scripts auxiliares)
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── requirements.txt
│   │   └── ...
│   └── ...
├── frontend/
│   ├── package.json
│   └── ...
├── .venv/                    ← Virtual environment (criado automaticamente)
└── logs/                     ← Logs de boot (criado automaticamente)
```

---

## 🔄 Fluxo de Inicialização

O arquivo `start-jarvis.bat` executa automaticamente:

```
1. VERIFICAÇÃO DE PYTHON
   ↓
2. SONDAGEM DE HARDWARE (GPU detection)
   ↓
3. SANITIZAÇÃO (limpar processos zumbis, liberar portas)
   ↓
4. SETUP DE VENV (criar virtual environment)
   ↓
5. INSTALAR DEPENDÊNCIAS
   ├─ pip upgrade
   ├─ PyTorch (com suporte CUDA se GPU detectada)
   ├─ webrtcvad-wheels
   ├─ resemblyzer
   └─ requirements.txt completo
   ↓
6. VALIDAÇÃO DE IMPORTS
   ↓
7. LANÇAMENTO DO BACKEND (FastAPI + Uvicorn)
   ├─ Health check: GET /health (90s timeout)
   └─ Aguarda: http://127.0.0.1:8000
   ↓
8. LANÇAMENTO DO FRONTEND (Next.js - opcional)
   ├─ Port check (60s timeout)
   └─ Aguarda: http://127.0.0.1:3000
   ↓
✓ JARVIS ONLINE
```

---

## 🎯 Componentes de Boot

### 1. **start-jarvis.bat** (Principal)
- Entry point único
- Detecta Python, Node, GPU
- Gerencia venv
- Instala dependências
- Inicia backend + frontend

### 2. **Arquitetura Modular** (scripts/)
Quando disponível, usa a estrutura modular:
- `check-prerequisites.bat` - Valida Python, Node, npm
- `detect-hardware.bat` - Detecta GPU (NVIDIA, Intel) e define modo
- `setup-venv.bat` - Cria/valida venv e instala pacotes
- `launch-backend.bat` - Inicia FastAPI com health check
- `launch-frontend.bat` - Inicia Next.js (opcional)

### 3. **Fallback Integrado**
Se scripts modulares não existirem, usa lógica integrada no `start-jarvis.bat`.

---

## 💻 Modos de Operação Detectados

O sistema detecta automaticamente o hardware e ativa modos otimizados:

| Hardware | Modo | Device | Whisper | Camera |
|----------|------|--------|---------|--------|
| NVIDIA GPU (≥6GB VRAM) | **PERFORMANCE** | `cuda` | `base` | enabled |
| NVIDIA GPU (<6GB VRAM) | **BALANCED** | `cuda` | `tiny` | enabled |
| Intel Iris Xe/Arc | **INTEL_OPT** | `openvino` | `tiny` | disabled |
| CPU Genérico | **COMPAT** | `cpu` | `tiny` | enabled |

---

## 🌐 URLs Após Boot

Quando JARVIS inicializa com sucesso:

- **Backend Core**: http://127.0.0.1:8000
- **API Docs**: http://127.0.0.1:8000/docs
- **Health Check**: http://127.0.0.1:8000/health
- **Frontend UI**: http://127.0.0.1:3000 (se Node.js disponível)

---

## 📊 Logs

Todos os logs são salvos em `logs/`:

- `boot.log` - Log principal de boot
- `prerequisites-check.log` - Validação de pré-requisitos
- `hardware-detection.log` - Detecção de hardware
- `venv-setup.log` - Setup de ambiente virtual
- `backend-startup.log` - Inicialização do backend
- `frontend-startup.log` - Inicialização do frontend

---

## 🔧 Troubleshooting

### Erro: "Python não encontrado"
```
Solução:
1. Instale Python 3.11+: https://python.org/downloads
2. Marque "Add Python to PATH" durante instalação
3. Reinicie o PC
4. Execute start-jarvis.bat novamente
```

### Erro: "Backend não respondeu"
```
Possíveis causas:
1. Porta 8000 já está em uso
2. Dependências não foram instaladas completamente
3. Erro em backend/app/main.py

Verificar:
- Janela do JARVIS - Backend (contém logs detalhados)
- logs/backend-startup.log
- logs/venv-setup.log
```

### Erro: "Frontend não respondeu"
```
Frontend é OPCIONAL. Verifique:
1. Node.js instalado: where node
2. npm/pnpm instalado: where pnpm
3. logs/frontend-startup.log para detalhes

Backend continuará rodando mesmo se frontend falhar.
```

### Porta em Uso
```
Se uma porta estiver bloqueada:

Liberar porta 8000:
  netstat -ano | findstr :8000
  taskkill /PID <PID> /F

Liberar porta 3000:
  netstat -ano | findstr :3000
  taskkill /PID <PID> /F
```

---

## 📝 Variáveis de Ambiente

Customizáveis via arquivo `.env` na raiz:

```env
# Portas (padrão: 8000, 3000)
BACKEND_PORT=8000
FRONTEND_PORT=3000

# Knowledge Base (default: data/kb_local)
JARVIS_KB_PATH=./data/kb_local

# Mode (auto-detectado, pode ser: PERFORMANCE, BALANCED, INTEL_OPT, COMPAT)
JARVIS_MODE=AUTO

# Device (auto-detectado, pode ser: cuda, openvino, cpu)
JARVIS_AI_DEVICE=AUTO
```

---

## 🚀 Desenvolvimento

### Arquitetura Modular (Avançado)

Se preferir mais controle, rode os scripts individuais:

```batch
REM Apenas check
scripts\check-prerequisites.bat

REM Apenas hardware detection
scripts\detect-hardware.bat

REM Apenas setup de venv
scripts\setup-venv.bat

REM Apenas backend
scripts\launch-backend.bat

REM Apenas frontend
scripts\launch-frontend.bat
```

---

## ⚙️ Configuração Avançada

### Instalar PyTorch com CUDA manualmente
```bash
cd .venv/Scripts
python -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

### Ativar venv manualmente
```batch
.venv\Scripts\activate.bat
```

### Resetar projeto
```batch
REM Limpar venv
rmdir /s /q .venv

REM Limpar logs
rmdir /s /q logs

REM Executar start-jarvis.bat para reinstalar tudo
start-jarvis.bat
```

---

## 📞 Suporte

Se encontrar problemas:

1. Verifique `logs/` para detalhes de erro
2. Confirme que Python 3.11+ está no PATH
3. Verifique conectividade de rede (PyTorch, etc.)
4. Verifique espaço em disco (depends >10GB)

---

**JARVIS 5.0 - OMEGA ADAPTIVE ORCHESTRATOR** ✓
