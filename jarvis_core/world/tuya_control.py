"""
World - Tuya Control
Controle de dispositivos IoT Tuya
"""

import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class SmartHome:
    """Controle de dispositivos Tuya"""
    
    def __init__(self):
        self.devices = {}
        self.tuya_available = False
        
        try:
            import tinytuya
            self.tinytuya = tinytuya
            self.tuya_available = True
            logger.info("✅ TinyTuya disponível")
        except ImportError:
            logger.warning("⚠️ tinytuya não instalado")
    
    def discover_devices(self) -> List[Dict]:
        """Auto-descoberta de dispositivos"""
        if not self.tuya_available:
            return []
        
        try:
            devices = self.tinytuya.deviceScan()
            logger.info(f"🔍 Encontrados {len(devices)} dispositivos")
            return devices
        except Exception as e:
            logger.error(f"❌ Erro na descoberta: {e}")
            return []
    
    def control_light(self, device_id: str, state: bool) -> bool:
        """Liga/desliga lâmpada"""
        if not self.tuya_available:
            return False
        
        try:
            device = self.tinytuya.OutletDevice(device_id, '', '')
            
            if state:
                device.turn_on()
                logger.info(f"💡 Lâmpada {device_id} LIGADA")
            else:
                device.turn_off()
                logger.info(f"💡 Lâmpada {device_id} DESLIGADA")
            
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao controlar luz: {e}")
            return False
    
    def set_brightness(self, device_id: str, brightness: int) -> bool:
        """Define brilho (0-100)"""
        if not self.tuya_available:
            return False
        
        try:
            device = self.tinytuya.OutletDevice(device_id, '', '')
            device.set_brightness(brightness)
            logger.info(f"💡 Brilho {device_id}: {brightness}%")
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao ajustar brilho: {e}")
            return False
    
    def set_color(self, device_id: str, r: int, g: int, b: int) -> bool:
        """Define cor RGB"""
        if not self.tuya_available:
            return False
        
        try:
            device = self.tinytuya.OutletDevice(device_id, '', '')
            device.set_colour(r, g, b)
            logger.info(f"🎨 Cor {device_id}: RGB({r},{g},{b})")
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao definir cor: {e}")
            return False


# Instância global
smart_home = SmartHome()
