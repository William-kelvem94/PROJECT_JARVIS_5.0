# 🚀 JARVIS 5.0 - INICIALIZAÇÃO AUTOMÁTICA

Este sistema agora é **auto-inteligente, auto-corretivo e auto-persistente**.

## 🔧 INSTALAÇÃO EM 1 MINUTO

### Opção 1: Launcher Auto-Curativo (Windows)
Clique duas vezes em **JARVIS_AUTO.bat**.

O sistema vai:
1. Verificar a instalação do Python.
2. Instalar dependências corretas (PyTorch, MSS, etc).
3. Corrigir problemas de importação automaticamente.
4. Iniciar o JARVIS.

### Opção 2: Via Terminal
```bash
python install_system.py --auto-fix
python main.py
```

## 🩹 SISTEMA DE AUTO-CURA
O JARVIS agora detecta e corrige problemas automaticamente:
- ✅ **PyTorch incompatível**: Detecta hardware e instala versão correta (CPU/CUDA).
- ✅ **Dependências faltando**: Instala automaticamente via `pip`.
- ✅ **Import errors**: Corrige caminhos e cria stubs se necessário.
- ✅ **Encoding Windows**: Configura UTF-8 automaticamente no logging.

## 📊 MODO DIAGNÓSTICO
Se encontrar problemas complexos, execute:
```bash
python install_system.py --diagnose
```
Este modo gera um relatório detalhado em `data/system_health.json`.
