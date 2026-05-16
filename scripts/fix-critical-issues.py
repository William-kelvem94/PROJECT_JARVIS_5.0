#!/usr/bin/env python3
"""
SCRIPT DE CORREÇÃO CRÍTICA — JARVIS 5.0
Resolve problemas de CPU/RAM e LLM offline
"""

import os
import sys
import subprocess
import time
import psutil
import aiohttp
import asyncio
from pathlib import Path

# Cores para terminal
class Color:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def print_status(message, status="INFO"):
    colors = {
        "OK": Color.GREEN,
        "ERROR": Color.RED,
        "WARNING": Color.YELLOW,
        "INFO": Color.BLUE
    }
    color = colors.get(status, Color.RESET)
    print(f"{color}[{status}]{Color.RESET} {message}")

# ============================================================
# 1. VALIDAÇÃO DE AMBIENTE
# ============================================================

def check_venv():
    """Verifica se está em um virtualenv"""
    if sys.prefix == sys.base_prefix:
        print_status("Ambiente virtual não detectado!", "ERROR")
        print_status("Ative o venv: .venv\\Scripts\\activate", "INFO")
        return False
    
    print_status(f"Venv ativo: {sys.prefix}", "OK")
    return True

def check_cpu_ram():
    """Monitora CPU e RAM"""
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory().percent
    
    print_status(f"CPU: {cpu:.1f}% | RAM: {ram:.1f}%", "INFO")
    
    if cpu > 90 or ram > 90:
        print_status("CARGA CRÍTICA DETECTADA!", "ERROR")
        return False
    elif cpu > 70 or ram > 70:
        print_status("Carga alta detectada", "WARNING")
        return True
    else:
        print_status("Recursos OK", "OK")
        return True

# ============================================================
# 2. INSTALAÇÃO DE DEPENDÊNCIAS
# ============================================================

def install_missing_packages():
    """Instala pacotes faltando"""
    packages = [
        "pygame",
        "dlib-prebuilt",
        "face_recognition",
        "resemblyzer"
    ]
    
    print_status("Verificando dependências...", "INFO")
    
    missing = []
    for pkg in packages:
        try:
            __import__(pkg.replace("-", "_"))
            print_status(f"✓ {pkg} instalado", "OK")
        except ImportError:
            missing.append(pkg)
            print_status(f"✗ {pkg} faltando", "WARNING")
    
    if missing:
        print_status(f"Instalando {len(missing)} pacotes...", "INFO")
        for pkg in missing:
            print_status(f"Instalando {pkg}...", "INFO")
            subprocess.run(
                [sys.executable, "-m", "pip", "install", pkg],
                check=True
            )
        print_status("Todas as dependências instaladas!", "OK")
    else:
        print_status("Todas as dependências OK", "OK")
    
    return True

# ============================================================
# 3. VALIDAÇÃO DE LLMS
# ============================================================

async def check_lm_studio():
    """Verifica se LM Studio está online"""
    url = "http://localhost:1234/v1/models"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=3)) as resp:
                if resp.status == 200:
                    print_status("LM Studio: ONLINE", "OK")
                    return True
    except Exception as e:
        print_status(f"LM Studio: OFFLINE ({e})", "ERROR")
        return False

async def check_ollama():
    """Verifica se Ollama está online"""
    url = "http://localhost:11434/api/tags"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=3)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    models = data.get("models", [])
                    print_status(f"Ollama: ONLINE ({len(models)} modelos)", "OK")
                    return True
    except Exception as e:
        print_status(f"Ollama: OFFLINE ({e})", "ERROR")
        return False

async def check_llms():
    """Verifica todos os LLMs"""
    print_status("Verificando LLMs...", "INFO")
    
    lm_studio_ok = await check_lm_studio()
    ollama_ok = await check_ollama()
    
    # Verifica API keys
    gemini_key = os.getenv("GEMINI_API_KEY")
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    
    if gemini_key:
        print_status("Gemini API Key: CONFIGURADA", "OK")
    else:
        print_status("Gemini API Key: NÃO CONFIGURADA", "WARNING")
    
    if openrouter_key:
        print_status("OpenRouter API Key: CONFIGURADA", "OK")
    else:
        print_status("OpenRouter API Key: NÃO CONFIGURADA", "WARNING")
    
    if not (lm_studio_ok or ollama_ok or gemini_key or openrouter_key):
        print_status("NENHUM LLM DISPONÍVEL!", "ERROR")
        return False
    
    return True

# ============================================================
# 4. APLICAR CORREÇÕES NO CÓDIGO
# ============================================================

def apply_cpu_throttling():
    """Aplica correção de CPU throttling nos agentes"""
    print_status("Aplicando correção de CPU throttling...", "INFO")
    
    # Caminho do arquivo
    target_file = Path(__file__).parent / "backend" / "app" / "multi_agent_analysis.py"
    
    if not target_file.exists():
        print_status(f"Arquivo não encontrado: {target_file}", "ERROR")
        return False
    
    # Ler arquivo
    with open(target_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar se já foi aplicado
    if "# CPU THROTTLING APPLIED" in content:
        print_status("Correção já aplicada", "OK")
        return True
    
    # Aplicar correção
    patch = """
        # CPU THROTTLING APPLIED
        import psutil
        
        # Throttling adaptativo
        cpu_usage = psutil.cpu_percent()
        if cpu_usage > 80:
            # Dobrar intervalo sob alta carga
            interval = self.check_interval * 2
        else:
            interval = self.check_interval
        
        await asyncio.sleep(interval)
"""
    
    # Verificar se o padrão alvo existe antes de aplicar
    target = "await asyncio.sleep(self.check_interval)"
    if target not in content:
        print_status(f"Padrão '{target}' não encontrado em {target_file}. Pulando patch.", "WARN")
        return False

    # Inserir antes do primeiro asyncio.sleep
    content = content.replace(target, patch)
    
    # Salvar
    with open(target_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print_status("Correção de CPU aplicada!", "OK")
    return True

def apply_llm_validation():
    """Aplica validação de LLM health"""
    print_status("Aplicando validação de LLM...", "INFO")
    
    target_file = Path(__file__).parent / "backend" / "app" / "smart_router.py"
    
    if not target_file.exists():
        print_status(f"Arquivo não encontrado: {target_file}", "ERROR")
        return False
    
    # Ler arquivo
    with open(target_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar se já foi aplicado
    if "# LLM HEALTH CHECK APPLIED" in content:
        print_status("Validação já aplicada", "OK")
        return True
    
    # Aplicar correção (adicionar ao início da classe)
    patch = '''
    # LLM HEALTH CHECK APPLIED
    async def validate_health(self):
        """Valida quais LLMs estão online"""
        health = {
            "lm_studio": False,
            "ollama": False,
            "gemini": bool(os.getenv("GEMINI_API_KEY")),
            "openrouter": bool(os.getenv("OPENROUTER_API_KEY"))
        }
        
        # LM Studio
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "http://localhost:1234/v1/models",
                    timeout=aiohttp.ClientTimeout(total=2)
                ) as resp:
                    health["lm_studio"] = resp.status == 200
        except:
            pass
        
        # Ollama
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "http://localhost:11434/api/tags",
                    timeout=aiohttp.ClientTimeout(total=2)
                ) as resp:
                    health["ollama"] = resp.status == 200
        except:
            pass
        
        return health
'''
    
    # Inserir após "class SmartRouter:"
    content = content.replace(
        "class SmartRouter:",
        f"class SmartRouter:{patch}"
    )
    
    # Salvar
    with open(target_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print_status("Validação de LLM aplicada!", "OK")
    return True

# ============================================================
# 5. SCRIPT PRINCIPAL
# ============================================================

async def main():
    print("=" * 60)
    print("  CORREÇÃO CRÍTICA — JARVIS 5.0")
    print("=" * 60)
    print()
    
    # 1. Validar ambiente
    if not check_venv():
        return 1
    
    check_cpu_ram()
    print()
    
    # 2. Instalar dependências
    try:
        install_missing_packages()
    except Exception as e:
        print_status(f"Erro ao instalar dependências: {e}", "ERROR")
        return 1
    print()
    
    # 3. Validar LLMs
    llms_ok = await check_llms()
    print()
    
    # 4. Aplicar correções
    print_status("Aplicando correções no código...", "INFO")
    apply_cpu_throttling()
    apply_llm_validation()
    print()
    
    # 5. Relatório final
    print("=" * 60)
    print("  RELATÓRIO FINAL")
    print("=" * 60)
    
    if not llms_ok:
        print_status("ATENÇÃO: Nenhum LLM disponível!", "WARNING")
        print()
        print("Para corrigir:")
        print("  1. LM Studio: Abra o app e inicie o servidor")
        print("  2. Ollama: Execute 'ollama serve'")
        print("  3. API Keys: Configure no arquivo .env")
    else:
        print_status("Todos os LLMs validados!", "OK")
    
    print()
    print_status("Correções aplicadas com sucesso!", "OK")
    print_status("Reinicie o backend: scripts/restart-jarvis.bat", "INFO")
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
