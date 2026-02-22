"""
Script para gerenciar modelos do Ollama baseado na configuração AI.
Lê o arquivo ai_config.yaml e garante que os modelos necessários (Ultra/Pro/Fast)
estejam baixados e prontos para uso.
"""

import os
import yaml
import subprocess
import logging
from pathlib import Path
import requests

# Config logger
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("OllamaManager")


def load_config(root_path):
    config_path = root_path / "config" / "ai_config.yaml"
    if not config_path.exists():
        logger.error(f"Config file not found: {config_path}")
        return None

    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def is_model_installed(model_name):
    try:
        # Usar captura binária para evitar crash de decode no pipe do Windows
        result = subprocess.run(["ollama", "list"], capture_output=True, text=False)
        output = result.stdout.decode("utf-8", errors="replace")
        return model_name in output
    except Exception as e:
        logger.error(f"Error checking model {model_name}: {e}")
        return False


def pull_model(model_name, background=False):
    if background:
        logger.info(
            f"🚀 [BACKGROUND] Iniciando download do modelo pesado: {model_name}"
        )
        try:
            if os.name == "nt":
                # No Windows, cria um processo totalmente independente (nova console minimizada se possível)
                # CREATE_NO_WINDOW (0x08000000) evita abrir janelas chatas
                subprocess.Popen(
                    ["ollama", "pull", model_name],
                    creationflags=0x08000000 | subprocess.CREATE_NEW_PROCESS_GROUP,
                )
            else:
                subprocess.Popen(
                    ["ollama", "pull", model_name],
                    start_new_session=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            logger.info(
                f"✅ Download de {model_name} continua em segundo plano. JARVIS pode iniciar agora."
            )
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao iniciar download em background: {e}")
            return False

    logger.info(f"⬇️ Pulling model: {model_name} (This may take a while)...")
    try:
        process = subprocess.Popen(
            ["ollama", "pull", model_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=False,
        )

        while True:
            line_bytes = process.stdout.readline()
            if not line_bytes and process.poll() is not None:
                break
            if line_bytes:
                line = line_bytes.decode("utf-8", errors="replace").strip()
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


def check_ollama_service():
    """Checks if Ollama service is running"""
    try:
        requests.get("http://localhost:11434", timeout=2)
        return True
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        logger.error("❌ Ollama service not responding. Please start it first.")
        if os.name == "nt":
            logger.info(
                "ℹ️  On Windows, make sure Ollama is running in the system tray."
            )
        else:
            logger.info("ℹ️  On Linux, run 'ollama serve' in a separate terminal.")
        return False
    except Exception as e:
        logger.error(f"❌ Error checking Ollama service: {e}")
        return False


def main():
    root_path = Path(__file__).resolve().parent.parent.parent
    config_data = load_config(root_path)

    if not config_data or "brain_router" not in config_data:
        logger.error("Invalid configuration format.")
        return

    ollama_config = config_data["brain_router"].get("ollama_models", {})
    required_models = config_data["brain_router"].get("required_models", [])

    # 1. Garantir que o serviço está respondendo
    if not check_ollama_service():
        return

    # 2. Verificar Modelos OBRIGATÓRIOS (Bloqueantes)
    logger.info("🛡️ Verificando Modelos Críticos...")
    for model in required_models:
        if not is_model_installed(model):
            logger.info(f"⚡ Modelo obrigatório ausente: {model}. Instalando agora...")
            pull_model(model, background=False)
        else:
            logger.info(f"✅ Modelo obrigatório presente: {model}")

    # 3. Verificar TIER FAST (Mandatório para Sentinela)
    fast_models = ollama_config.get("tier_fast", [])
    if fast_models:
        primary_fast = fast_models[0]
        if not is_model_installed(primary_fast):
            logger.info(
                f"⚡ Modelo FAST principal '{primary_fast}' ausente. Instalando..."
            )
            pull_model(primary_fast, background=False)
        else:
            logger.info(f"✅ Modelo FAST presente: {primary_fast}")

    # 4. Verificar TIER PRO & ULTRA (Background)
    background_downloads_triggered = False
    for tier in ["tier_pro", "tier_ultra"]:
        models = ollama_config.get(tier, [])
        if not models:
            continue

        primary_model = models[0]
        if not is_model_installed(primary_model):
            if not background_downloads_triggered:
                logger.info(
                    f"🚀 {tier.upper()}: Modelo '{primary_model}' será baixado em background."
                )
                pull_model(primary_model, background=True)
                background_downloads_triggered = (
                    True  # Apenas um download pesado por vez
                )
            else:
                logger.info(
                    f"⏳ {tier.upper()}: Modelo '{primary_model}' agendado para download futuro (background ocupado)."
                )
        else:
            logger.info(f"✅ Modelo {tier.upper()} presente: {primary_model}")


if __name__ == "__main__":
    main()
