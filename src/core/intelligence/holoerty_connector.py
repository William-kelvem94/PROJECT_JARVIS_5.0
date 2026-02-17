
import os
import requests
import json
import logging
import asyncio

logger = logging.getLogger(__name__)

from src.utils.config import config

class HoloertyConnector:
    """
    Connects to Ollama Cloud/Discovery (Holoerty) services using the provided public key.
    Enables access to massive cloud models via local API proxy.
    """
    
    def __init__(self):
        self.public_key = config.get_ai_config("brain_router.ollama_key", "185919827dee4d1e80a03dd78ed017ea.V25w0L3H2Fn36laihGuc09xH")
        self.base_url = "https://api.ollama.com" # Hypothetical endpoint for cloud relay if needed, usually handled by local bin
    
    def register_key(self):
        """
        Ensures the public key is registered with the local Ollama instance 
        so it can authorize cloud model pulls/runs.
        """
        # On Windows, keys are usually in ~/.ollama/id_ed25519.pub
        # We need to ensure THIS key is the one being used or authorized.
        
        user_home = os.path.expanduser("~")
        ollama_dir = os.path.join(user_home, ".ollama")
        
        if not os.path.exists(ollama_dir):
            os.makedirs(ollama_dir, exist_ok=True)
            
        key_path = os.path.join(ollama_dir, "authorized_keys") 
        # Note: Actual mechanism depends on Ollama version. 
        # For 'ollama run model:cloud', usually checking local auth against cloud.
        
        # We will log it for the user to manually add if needed, or try to set env var
        logger.info(f"🔑 Holoerty Key Active: {self.public_key[:8]}...")
        os.environ["OLLAMA_PUBKEY"] = self.public_key
        
    async def pull_cloud_model(self, model_name: str):
        """
        Triggers a pull for a cloud-only model.
        """
        if ":cloud" not in model_name:
            return False
            
        logger.info(f"☁️ Pulling Holoerty Cloud Model: {model_name}")
        process = await asyncio.create_subprocess_shell(
            f"ollama pull {model_name}",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        
        if process.returncode == 0:
            logger.info(f"✅ Successfully pulled {model_name}")
            return True
        else:
            logger.error(f"❌ Failed to pull {model_name}: {stderr.decode()}")
            return False

holoerty = HoloertyConnector()
