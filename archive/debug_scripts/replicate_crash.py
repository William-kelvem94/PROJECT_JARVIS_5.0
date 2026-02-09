import os
import sys
import logging
from pathlib import Path

# Replicando patches do main.py
os.environ["OMP_WAIT_POLICY"] = "PASSIVE"
os.environ["MKL_THREADING_LAYER"] = "INTEL"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CRASH-TEST")

def test_crash_replication():
    try:
        logger.info("Importando torch (simulando main core)...")
        import torch
        logger.info(f"Torch version: {torch.__version__}")
        
        # Simulando HardwareManager (10 threads como no log do usuário)
        logger.info("Configurando threads do torch (10)...")
        torch.set_num_threads(10)
        
        logger.info("Importando faster-whisper...")
        from faster_whisper import WhisperModel
        
        logger.info("Iniciando carga do modelo base (float32)...")
        # Criando o modelo
        model = WhisperModel("base", device="cpu", compute_type="float32")
        logger.info("✅ SUCESSO! Modelo carregado sem crash.")
        
    except Exception as e:
        logger.error(f"❌ Erro capturado: {e}")
    except BaseException as e:
        logger.error(f"❌ Erro base capturado: {e}")

if __name__ == "__main__":
    test_crash_replication()
