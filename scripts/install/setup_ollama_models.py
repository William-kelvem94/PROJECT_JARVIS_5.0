"""
Script para gerenciar modelos do Ollama baseado na configuração AI.
Lê o arquivo ai_config.yaml e garante que os modelos necessários (Ultra/Pro/Fast)
estejam baixados e prontos para uso.
"""

import os
import sys
import yaml
import subprocess
import logging
from pathlib import Path
import time

# Config logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("OllamaManager")

def load_config(root_path):
    config_path = root_path / "config" / "ai_config.yaml"
    if not config_path.exists():
        logger.error(f"Config file not found: {config_path}")
        return None
    
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def is_model_installed(model_name):
    try:
        # Usar captura binária para evitar crash de decode no pipe do Windows
        result = subprocess.run(["ollama", "list"], capture_output=True, text=False)
        output = result.stdout.decode('utf-8', errors='replace')
        return model_name in output
    except Exception as e:
        logger.error(f"Error checking model {model_name}: {e}")
        return False

def pull_model(model_name, background=False):
    if background:
        logger.info(f"🚀 [BACKGROUND] Iniciando download do modelo pesado: {model_name}")
        try:
            if os.name == 'nt':
                # No Windows, cria um processo totalmente independente (nova console minimizada se possível)
                # CREATE_NO_WINDOW (0x08000000) evita abrir janelas chatas
                subprocess.Popen(["ollama", "pull", model_name], 
                                 creationflags=0x08000000 | subprocess.CREATE_NEW_PROCESS_GROUP)
            else:
                subprocess.Popen(["ollama", "pull", model_name], 
                                 start_new_session=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            logger.info(f"✅ Download de {model_name} continua em segundo plano. JARVIS pode iniciar agora.")
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao iniciar download em background: {e}")
            return False

    logger.info(f"⬇️ Pulling model: {model_name} (This may take a while)...")
    try:
        process = subprocess.Popen(["ollama", "pull", model_name], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=False)
        
        while True:
            line_bytes = process.stdout.readline()
            if not line_bytes and process.poll() is not None:
                break
            if line_bytes:
                line = line_bytes.decode('utf-8', errors='replace').strip()
                print(f"   {line}")
                
        if process.returncode == 0:
            logger.info(f"✅ Model {model_name} installed successfully.")
            return True
        else:
            logger.error(f"❌ Failed to install {model_name}.")
            return False
    except Exception as e:
        logger.error(f"❌ Error pulling {model_name}: {e}")
        return False

def main():
    root_path = Path(__file__).parent.parent.parent
    config = load_config(root_path)
    
    if not config or 'brain_router' not in config:
        logger.error("Invalid configuration format.")
        return

    ollama_config = config['brain_router'].get('ollama_models', {})
    
    # === TIER FAST (Mandatório) ===
    # JARVIS precisa de pelo menos o modelo FAST para ser funcional.
    fast_models = ollama_config.get('tier_fast', [])
    if fast_models:
        primary_fast = fast_models[0]
        logger.info(f"\n🔍 Checking TIER_FAST: {primary_fast}...")
        if not is_model_installed(primary_fast):
            logger.info("⚡ Modelo FAST essencial ausente. Instalando agora (Bloqueante)...")
            pull_model(primary_fast, background=False)
        else:
            logger.info(f"✅ Primary FAST model is ready.")

    # === TIER PRO & ULTRA (Background/Opcional) ===
    # Modelos pesados são baixados em segundo plano para não travar o boot.
    for tier in ['tier_pro', 'tier_ultra']:
        models = ollama_config.get(tier, [])
        if not models:
            continue
            
        logger.info(f"\n🔍 Checking {tier.upper()} candidates...")
        primary_model = models[0]
        
        if not is_model_installed(primary_model):
            logger.info(f"🚀 {tier.upper()}: Modelo '{primary_model}' será baixado em background.")
            pull_model(primary_model, background=True)
            # Apenas um download pesado por vez para não matar o notebook
            break # Baixa o PRO primeiro, na próxima vez ele baixa o ULTRA
        else:
            logger.info(f"✅ {tier.upper()} model '{primary_model}' is ready.")

if __name__ == "__main__":
    main()
