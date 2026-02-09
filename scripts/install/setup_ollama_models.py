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
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True, encoding='utf-8')
        return model_name in result.stdout
    except Exception as e:
        logger.error(f"Error checking model {model_name}: {e}")
        return False

def pull_model(model_name):
    logger.info(f"⬇️ Pulling model: {model_name} (This may take a while)...")
    try:
        # Usar Popen para streamar output se possível, ou apenas esperar
        process = subprocess.Popen(["ollama", "pull", model_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Simples visualização de progresso
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(f"   {output.strip()}")
                
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
    
    # Prioridade de download: Fast -> Pro -> Ultra
    tiers = ['tier_fast', 'tier_pro', 'tier_ultra']
    
    for tier in tiers:
        models = ollama_config.get(tier, [])
        if not models:
            continue
            
        logger.info(f"\n🔍 Checking {tier.upper()} models...")
        
        # Tenta o primeiro modelo da lista (Primary)
        primary_model = models[0]
        if not is_model_installed(primary_model):
            logger.info(f"⚡ Primary model '{primary_model}' missing. Initiating download...")
            pull_model(primary_model)
        else:
            logger.info(f"✅ Primary model '{primary_model}' is ready.")

if __name__ == "__main__":
    main()
