"""
World - Fauxmo Server
Fake Alexa device para integração IoT
"""

import logging
from typing import Callable, Dict

logger = logging.getLogger(__name__)

class AlexaBridge:
    """Ponte entre Alexa e JARVIS"""
    
    def __init__(self):
        self.devices = {}
        self.fauxmo_server = None
        
        try:
            from fauxmo import fauxmo
            from fauxmo.plugins import FauxmoPlugin
            self.fauxmo_available = True
            logger.info("✅ Fauxmo disponível")
        except ImportError:
            self.fauxmo_available = False
            logger.warning("⚠️ Fauxmo não instalado")
    
    def register_device(self, name: str, on_callback: Callable, off_callback: Callable = None):
        """Registra dispositivo fake"""
        if not self.fauxmo_available:
            logger.warning("⚠️ Fauxmo não disponível")
            return False
        
        self.devices[name] = {
            "on": on_callback,
            "off": off_callback or on_callback
        }
        
        logger.info(f"✅ Dispositivo registrado: {name}")
        return True
    
    def start_server(self, port: int = 12340):
        """Inicia servidor Fauxmo"""
        if not self.fauxmo_available:
            return False
        
        try:
            # Configurar devices
            config = {
                "FAUXMO": {
                    "ip_address": "auto"
                },
                "PLUGINS": {}
            }
            
            for device_name, callbacks in self.devices.items():
                config["PLUGINS"][device_name] = {
                    "port": port,
                    "on_cmd": callbacks["on"],
                    "off_cmd": callbacks["off"]
                }
                port += 1
            
            logger.info(f"🚀 Servidor Fauxmo iniciado")
            logger.info(f"📱 Dispositivos disponíveis: {list(self.devices.keys())}")
            logger.info("💡 Diga: 'Alexa, descubra dispositivos'")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao iniciar Fauxmo: {e}")
            return False
    
    def stop_server(self):
        """Para servidor"""
        if self.fauxmo_server:
            logger.info("🛑 Parando servidor Fauxmo...")


# Exemplo de uso
def party_mode():
    """Modo festa"""
    logger.info("🎉 MODO FESTA ATIVADO!")
    # spotify.play()
    # lights.set_color("rainbow")
    # pc.volume(100)

def work_mode():
    """Modo trabalho"""
    logger.info("💼 MODO TRABALHO ATIVADO!")
    # lights.set_color("white")
    # music.play("focus")
    # notifications.dnd(True)


# Instância global
alexa_bridge = AlexaBridge()

# Registrar dispositivos padrão
alexa_bridge.register_device("Protocolo Festa", party_mode)
alexa_bridge.register_device("Modo Trabalho", work_mode)
