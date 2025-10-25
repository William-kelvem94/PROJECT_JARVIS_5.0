# 🚀 Como Executar o JARVIS - Guia Rápido

## Opção 1: Docker (Recomendado)

### Pré-requisitos
- Docker Desktop instalado
- WSL2 configurado

### Executar
```powershell
.\INSTALL_AND_RUN.ps1
```

Se der erro de WSL:
1. Execute `INSTALAR_WSL.ps1` **como Administrador**
2. Reinicie o Windows
3. Execute `INSTALL_AND_RUN.ps1` novamente

---

## Opção 2: Local (Sem Docker) ⭐ MAIS FÁCIL

### Pré-requisitos
- Python 3.11+
- Node.js 20+

### Executar
```powershell
.\START_LOCAL_COMPLETO.ps1
```

Este script vai:
1. ✅ Instalar Ollama automaticamente
2. ✅ Baixar modelo LLM (~4GB)
3. ✅ Configurar Backend + Frontend
4. ✅ Abrir navegador automaticamente

### 100% FUNCIONAL!
- LLM real (não é mock!)
- Todas as funcionalidades
- Interface completa

---

## 📊 Comparação

| Característica | Docker | Local |
|----------------|--------|-------|
| Funcionalidades | ✅ Todas | ✅ Todas |
| LLM Real | ✅ Sim | ✅ Sim |
| Setup | Médio | Fácil |
| Velocidade | Normal | Rápido |
| Isolamento | ✅ Sim | ❌ Não |

---

## ⚡ Início Super Rápido

**Windows com problemas no Docker? Use local:**

```powershell
.\START_LOCAL_COMPLETO.ps1
```

**Pronto! Em 10 minutos está rodando!**

---

## 🌐 Acessar

Após iniciar (qualquer modo):

- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/api/docs
- **Health Check**: http://localhost:8000/health

---

## 🛑 Parar

### Docker
```powershell
docker-compose -f docker-compose.simple.yml down
```

### Local
Feche as janelas PowerShell que foram abertas

---

## 📚 Mais Informações

- **Problemas com WSL/Docker**: `INSTALAR_WSL_GUIA.md`
- **Detalhes técnicos**: `README.md`
- **Quickstart**: `QUICKSTART.md`

