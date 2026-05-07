# 🚀 GUIA DE CORREÇÃO RÁPIDA — JARVIS 5.0

**Status Atual**: 🔴 Sistema com CPU 100% / RAM 96% / LLM Offline

---

## ⚡ CORREÇÃO IMEDIATA (5 minutos)

### **Passo 1: Execute o Script de Correção**

```bash
# Execute este comando
fix-critical.bat
```

**O que ele faz**:
- ✅ Instala dependências faltando (pygame, face_recognition)
- ✅ Valida LLMs disponíveis (LM Studio, Ollama, Gemini, OpenRouter)
- ✅ Aplica throttling de CPU nos agentes
- ✅ Adiciona validação de LLM health
- ✅ Gera relatório de status

---

### **Passo 2: Configurar LLMs (CRÍTICO)**

**Escolha UMA das opções abaixo:**

#### **Opção A: LM Studio (Recomendado - Local)**

```bash
# 1. Abrir LM Studio
# 2. Baixar modelo: Llama 3.2 3B ou similar
# 3. Clicar em "Start Server"
# 4. Verificar porta 1234
```

**Verificar**:
```bash
curl http://localhost:1234/v1/models
```

#### **Opção B: Ollama (Local)**

```bash
# 1. Instalar Ollama (se não tiver)
# Baixar: https://ollama.ai/download

# 2. Iniciar serviço
ollama serve

# 3. Baixar modelo
ollama pull llama3.2:3b

# 4. Verificar
ollama list
```

**Verificar**:
```bash
curl http://localhost:11434/api/tags
```

#### **Opção C: Gemini (Cloud - Backup)**

```bash
# 1. Editar .env
GEMINI_API_KEY=sua_chave_aqui

# 2. Obter chave
# https://ai.google.dev/
```

---

### **Passo 3: Reiniciar Backend**

```bash
# Parar backend atual (Ctrl+C no terminal)
# Ou fechar janelas de PowerShell do Jarvis

# Reiniciar
start-jarvis.bat
```

**Aguardar inicialização** (30-60s):
- ✅ Backend pronto na porta 8000
- ✅ Frontend pronto na porta 3000
- ✅ Telemetria na porta 8001

---

### **Passo 4: Validar Sistema**

```bash
# Verificar saúde dos componentes
curl http://localhost:8000/system/capabilities

# Verificar agentes
curl http://localhost:8000/agents/summary

# Verificar CPU/RAM
curl http://localhost:8000/telemetry/status
```

**Dashboard**: http://localhost:3000

**Métricas esperadas**:
- CPU: < 50%
- RAM: < 70%
- Health: > 90%
- Agentes ativos: 14/14

---

## 🔍 DIAGNÓSTICO AVANÇADO

### **Se CPU/RAM Continuar Alto**

```bash
# Verificar processos Python
tasklist /FI "IMAGENAME eq python.exe"

# Matar processos órfãos
taskkill /F /IM python.exe

# Reiniciar limpo
start-jarvis.bat
```

### **Se LLM Continuar Offline**

```bash
# Verificar logs
type backend\logs\jarvis.log | findstr LLM
type backend\logs\jarvis.log | findstr "lm_studio\|ollama\|gemini"

# Testar manualmente
curl -X POST http://localhost:1234/v1/chat/completions ^
  -H "Content-Type: application/json" ^
  -d "{\"model\": \"llama-3.2-3b-instruct\", \"messages\": [{\"role\": \"user\", \"content\": \"hi\"}]}"
```

### **Se Face Recognition N/C**

```bash
# Instalar manualmente
.\.venv\Scripts\activate
pip install dlib-prebuilt
pip install face_recognition

# Verificar
python -c "import face_recognition; print('OK')"
```

### **Se Pygame N/C (TTS sem som)**

```bash
# Instalar
pip install pygame

# Verificar
python -c "import pygame; pygame.mixer.init(); print('OK')"
```

---

## 📊 MONITORAMENTO

### **Dashboard Principal**

http://localhost:3000

**Indicadores**:
- 🟢 Verde: OK (< 70%)
- 🟡 Amarelo: Alto (70-90%)
- 🔴 Vermelho: Crítico (> 90%)

### **Telemetria em Tempo Real**

http://localhost:8001/status

**JSON**:
```json
{
  "cpu": 45.2,
  "ram": 68.5,
  "agents_active": 14,
  "health_percentage": 92,
  "llm_status": {
    "lm_studio": true,
    "ollama": false,
    "gemini": true
  }
}
```

### **Logs**

```bash
# Backend
tail -f backend\logs\jarvis.log

# Agentes
tail -f backend\logs\agents.log

# Telemetria
tail -f backend\logs\telemetry.log
```

---

## 🛠️ CORREÇÕES MANUAIS (Avançado)

### **Reduzir Agentes Ativos**

Editar: `backend/app/multi_agent_analysis.py`

```python
# Desabilitar agentes não críticos
ENABLED_AGENTS = [
    "PerformanceAgent",      # Mantém
    "SystemHealthAgent",     # Mantém
    "EndpointRecoveryAgent", # Mantém
    # "CodeQualityAgent",    # Desabilita (pesado)
    # "UserExperienceAgent", # Desabilita
]
```

### **Aumentar Intervalos**

Editar: `backend/app/multi_agent_analysis.py`

```python
# Aumentar check_interval dos agentes
PerformanceAgent(check_interval=120),  # 60 → 120s
CognitiveHealthAgent(check_interval=300),  # 120 → 300s
```

### **Desabilitar Perception Contínua**

Editar: `backend/app/perception/perception_manager.py`

```python
# Adicionar frame skip
self.frame_skip = 3  # Processa 1 em cada 3 frames

# No loop de captura:
if self.frame_counter % self.frame_skip != 0:
    continue
```

---

## 📋 CHECKLIST RÁPIDO

- [ ] ✅ Script fix-critical.bat executado
- [ ] ✅ LM Studio ou Ollama rodando
- [ ] ✅ Backend reiniciado
- [ ] ✅ Dashboard acessível (http://localhost:3000)
- [ ] ✅ CPU < 50%
- [ ] ✅ RAM < 70%
- [ ] ✅ Chat respondendo
- [ ] ✅ 14 agentes ativos
- [ ] ✅ Health > 90%

---

## 🆘 SUPORTE

### **Problema: CPU ainda alto**
- Reduzir número de agentes
- Aumentar intervalos
- Desabilitar perception contínua

### **Problema: LLM não responde**
- Verificar se LM Studio/Ollama estão ativos
- Verificar logs: `backend\logs\jarvis.log`
- Testar manualmente com curl

### **Problema: Frontend crashando**
- Limpar cache: `cd frontend && pnpm clean`
- Rebuild: `pnpm build`
- Verificar logs do navegador (F12)

### **Problema: Agentes não funcionam**
- Verificar: `curl http://localhost:8000/agents/summary`
- Reiniciar backend
- Verificar logs: `backend\logs\agents.log`

---

## 📚 DOCUMENTAÇÃO COMPLETA

- 📄 [LAUDO_TECNICO_COMPLETO.md](LAUDO_TECNICO_COMPLETO.md) - Análise completa
- 📄 [AUTOFIX_AGENTS.md](docs/AUTOFIX_AGENTS.md) - Agentes de auto-correção
- 📄 [SOLUTIONS_FOR_REPORTED_ISSUES.md](docs/SOLUTIONS_FOR_REPORTED_ISSUES.md) - Troubleshooting
- 📄 [jarvis_native_architecture.md](docs/jarvis_native_architecture.md) - Arquitetura de voz
- 📄 [LOCAL_ARCHITECTURE_V5.md](docs/LOCAL_ARCHITECTURE_V5.md) - Arquitetura offline

---

**Última atualização**: 7 de maio de 2026  
**Status**: Sistema identificado e correções disponíveis  
**Tempo estimado de correção**: 5-10 minutos
