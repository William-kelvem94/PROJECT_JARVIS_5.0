import logging
import requests
from typing import Dict, Any, Optional
from src.utils.config import config

logger = logging.getLogger("JARVIS-IOT")

class IOTManager:
    """
    Gerencia dispositivos inteligentes (Phase 4).
    Focado inicialmente em Home Assistant via API REST.
    """

    def __init__(self):
        self.ha_url = config.get_setting('iot.ha_url', 'http://homeassistant.local:8123')
        self.ha_token = config.get_setting('iot.ha_token', None)
        self.is_configured = self.ha_token is not None

    def control_device(self, device_id: str, command: str, params: Optional[Dict[str, Any]] = None) -> bool:
        """
        Envia comando para um dispositivo.
        
        Args:
            device_id: ID da entidade no HA (ex: light.living_room)
            command: ServiÃ§o a ser chamado (ex: turn_on, turn_off)
            params: Atributos extras
        """
        if not self.is_configured:
            logger.warning("âš ï¸ Home Assistant nÃ£o configurado. Adicione 'iot.ha_token' ao ai_config.yaml")
            return False

        try:
            domain = device_id.split('.')[0] if '.' in device_id else 'homeassistant'
            url = f"{self.ha_url}/api/services/{domain}/{command}"
            
            headers = {
                "Authorization": f"Bearer {self.ha_token}",
                "Content-Type": "application/json",
            }
            
            payload = {"entity_id": device_id}
            if params:
                payload.update(params)

            logger.info(f"ðŸ  Enviando comando IoT: {domain}.{command} para {device_id}")
            response = requests.post(url, headers=headers, json=payload, timeout=5)
            
            if response.status_code in [200, 201]:
                return True
            else:
                logger.error(f"âŒ Erro HA ({response.status_code}): {response.text}")
                return False

        except Exception as e:
            logger.error(f"âŒ Falha crÃ­tica no comando IoT: {e}")
            return False

    def get_state(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Busca o estado atual de uma entidade"""
        if not self.is_configured: return None
        
        try:
            url = f"{self.ha_url}/api/states/{entity_id}"
            headers = {"Authorization": f"Bearer {self.ha_token}"}
            response = requests.get(url, headers=headers, timeout=5)
            return response.json() if response.status_code == 200 else None
        except Exception:
            return None

# InstÃ¢ncia global
iot_manager = IOTManager()
