# 🔧 Guia Completo: Instalar WSL2 e Rodar JARVIS no Docker

## Passo 1: Executar como Administrador

1. **Clique com botão direito** no arquivo `INSTALAR_WSL.ps1`
2. Selecione: **"Executar com PowerShell"** ou **"Executar como Administrador"**
3. Se aparecer aviso de segurança, clique **"Sim"**

## Passo 2: Reiniciar Windows

Após o script terminar, **REINICIE O WINDOWS** (obrigatório!)

## Passo 3: Configurar Docker Desktop

Depois de reiniciar:

1. Abra **Docker Desktop**
2. Vá em: **Settings** (ícone de engrenagem)
3. **General** → Marque ✅ **"Use the WSL 2 based engine"**
4. **Apply & Restart**

## Passo 4: Rodar o Projeto

Abra PowerShell normal (não precisa admin) e execute:

```powershell
cd D:\Documents\GitHub\PROJECT_JARVIS_3.0
.\INSTALL_AND_RUN.ps1
```

---

## ⚠️ Alternativa: Se WSL não instalar

Se o WSL continuar dando erro, você tem 2 opções:

### Opção A: Instalar WSL manualmente

1. Abra **PowerShell como Administrador** e execute:

```powershell
# Habilitar recursos
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart

# Reiniciar Windows
Restart-Computer
```

2. Depois de reiniciar, abra **PowerShell como Administrador** novamente:

```powershell
# Instalar WSL2
wsl --install

# Definir versão 2 como padrão
wsl --set-default-version 2
```

### Opção B: Usar modo local (SEM Docker)

Se Docker/WSL for muito problemático, rode localmente:

```powershell
.\START_LOCAL_COMPLETO.ps1
```

Este modo:
- ✅ É **100% FUNCIONAL** (não é demo!)
- ✅ Usa Ollama no Windows
- ✅ Backend + Frontend completos
- ✅ Banco de dados SQLite local
- ✅ Todos os recursos funcionando

---

## 📋 Resumo Rápido

| Passo | Comando |
|-------|---------|
| 1. Instalar WSL | `INSTALAR_WSL.ps1` (como Admin) |
| 2. Reiniciar | Obrigatório! |
| 3. Configurar Docker | Settings > WSL 2 |
| 4. Rodar projeto | `INSTALL_AND_RUN.ps1` |

**OU**

| Modo Local (sem Docker) |
|-------------------------|
| `START_LOCAL_COMPLETO.ps1` |

---

## ✅ Verificar se WSL está OK

Execute no PowerShell:

```powershell
wsl --version
wsl --list --verbose
```

Se aparecer uma lista de distribuições, está OK! ✅

---

## 🆘 Problemas?

- **WSL não instala**: Use modo local com `START_LOCAL_COMPLETO.ps1`
- **Docker não funciona**: Use modo local com `START_LOCAL_COMPLETO.ps1`
- **Erro 740**: Execute PowerShell como Administrador

## 🚀 Modo local é completo!

Não se preocupe se Docker não funcionar. O modo local é **totalmente funcional**:
- LLM real com Ollama
- Backend completo
- Frontend completo
- Todas as funcionalidades

A única diferença é que não usa containers Docker.

