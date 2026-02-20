# 🔧 JARVIS Dependency Troubleshooting Guide

## Problema: torch/torchvision aparecem como MISSING

### Sintomas
```
❌ torch                     MISSING
❌ torchvision               MISSING
```

### Causas Comuns
1. **PyTorch não instalado** - Nunca foi instalado
2. **DLL Error 1114** - PyTorch instalado mas DLLs do sistema faltando
3. **Versão incompatível** - Python ou NumPy incompatível
4. **Ambiente virtual errado** - Instalado no Python do sistema, não no VENV

---

## Soluções

### ✅ Solução 1: Quick Fix (RECOMENDADO)
Execute `START_JARVIS.bat` e escolha opção **1 - Quick Fix**

Ou manualmente:
```powershell
cd C:\Users\willi\Documents\GitHub\PROJECT_JARVIS_5.0
venv\Scripts\python.exe scripts\install\quick_fix_torch.py
```

### ✅ Solução 2: Instalação Manual (CPU)
```powershell
cd C:\Users\willi\Documents\GitHub\PROJECT_JARVIS_5.0
venv\Scripts\python.exe -m pip uninstall torch torchvision torchaudio -y
venv\Scripts\python.exe -m pip install torch==2.2.2 torchvision==0.17.2 torchaudio==2.2.2 --index-url https://download.pytorch.org/whl/cpu
```

### ✅ Solução 3: Com NVIDIA GPU (CUDA)
```powershell
cd C:\Users\willi\Documents\GitHub\PROJECT_JARVIS_5.0
venv\Scripts\python.exe -m pip uninstall torch torchvision torchaudio -y
venv\Scripts\python.exe -m pip install torch>=2.4.0 torchvision>=0.19.0 torchaudio>=2.4.0 --index-url https://download.pytorch.org/whl/cu121
```

---

## Verificação Pós-Instalação

### Teste Rápido
```powershell
venv\Scripts\python.exe scripts\test_pytorch.py
```

### Validar Todas as Dependências
```powershell
venv\Scripts\python.exe scripts\validate_dependencies.py
```

---

## FAQ: Erros Específicos

### 🔴 Erro: "DLL load failed while importing torch"
**Causa**: Faltam Visual C++ Redistributables no Windows

**Solução**:
1. Baixe e instale: https://aka.ms/vs/17/release/vc_redist.x64.exe
2. Reinicie o computador
3. Execute Quick Fix novamente

---

### 🔴 Erro: "numpy.dtype size changed"
**Causa**: Incompatibilidade numpy 2.x vs torch

**Solução**:
```powershell
venv\Scripts\python.exe -m pip install "numpy<2.0"
venv\Scripts\python.exe -m pip install --force-reinstall --no-cache-dir torch torchvision
```

---

### 🔴 Erro: "ModuleNotFoundError: No module named 'torch'"
**Causa**: PyTorch não está instalado no ambiente virtual correto

**Solução**: Verifique se está usando o Python do VENV:
```powershell
# ERRADO (Python do sistema)
python scripts\validate_dependencies.py

# CORRETO (Python do VENV)
venv\Scripts\python.exe scripts\validate_dependencies.py
```

---

### 🔴 Erro: Package installed but import fails (⚠️)
**Sintomas**:
```
⚠️  torch                     INSTALLED (Import Failed - DLL Issue)
```

**Causa**: PyTorch instalado mas DLLs danificadas ou incompatíveis

**Solução**:
```powershell
# Remove completamente
venv\Scripts\python.exe -m pip uninstall torch torchvision torchaudio -y

# Reinstala fresh
venv\Scripts\python.exe scripts\install\quick_fix_torch.py
```

---

## Verificação de Ambiente

### Checar qual Python está sendo usado:
```powershell
where python
# Deve mostrar: C:\Users\willi\Documents\GitHub\PROJECT_JARVIS_5.0\venv\Scripts\python.exe PRIMEIRO
```

### Verificar versão do Python:
```powershell
venv\Scripts\python.exe --version
# Deve ser Python 3.11.x
```

### Verificar NumPy:
```powershell
venv\Scripts\python.exe -c "import numpy; print(numpy.__version__)"
# Deve ser < 2.0 (ex: 1.26.4)
```

---

## Arquivos de Log

Quando algo falha, verifique:
- `total_installer.log` - Logs de instalação
- `data\logs\launcher.log` - Logs do launcher
- `data\logs\crash_report.json` - Relatório do último crash

---

## Suporte Adicional

Se nenhuma solução funcionar:

1. **Limpar completamente e reinstalar**:
```powershell
# Remove VENV
rmdir /s /q venv

# Remove cache pip
venv\Scripts\python.exe -m pip cache purge

# Reinstala tudo
INSTALL_JARVIS.bat
```

2. **Reportar issue** com:
   - Saída completa do `validate_dependencies.py`
   - Conteúdo de `total_installer.log`
   - Versão do Windows e Python
   - Se tem GPU NVIDIA

---

## Status do Sistema

### ✅ Sistema Saudável
```
✅ PyQt6                     OK
✅ cv2                       OK
✅ numpy                     OK
✅ torch                     OK
✅ torchvision               OK
✅ ultralytics               OK
✅ onnxruntime               OK
✅ transformers              OK
✅ sentence_transformers     OK
✅ chromadb                  OK
```

### ⚠️ Sistema Parcialmente Funcional
```
✅ PyQt6                     OK
✅ cv2                       OK
✅ numpy                     OK
⚠️  torch                     INSTALLED (Import Failed)
⚠️  torchvision               INSTALLED (Import Failed)
✅ ultralytics               OK
```
**Ação**: Execute Quick Fix

### ❌ Sistema Não Funcional
```
✅ PyQt6                     OK
❌ torch                     MISSING
❌ torchvision               MISSING
```
**Ação**: Execute INSTALL_JARVIS.bat ou Quick Fix
