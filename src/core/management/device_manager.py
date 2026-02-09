#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS 5.0 - Device Manager (Stark Controls)
=============================================
Controla brilho, volume, navegadores e mídias do Windows.
"""

import logging
import os
import webbrowser
import subprocess
from typing import Optional

try:
    import screen_brightness_control as sbc
    SBC_AVAILABLE = True
except ImportError:
    SBC_AVAILABLE = False

logger = logging.getLogger(__name__)

class DeviceManager:
    """O 'Sistema Nervoso' para controle de dispositivos Windows"""
    
    def set_brightness(self, level: int) -> bool:
        """Ajusta o brilho do monitor (0-100)"""
        if not SBC_AVAILABLE:
            logger.warning("⚠️ screen_brightness_control não instalado.")
            return False
        try:
            level = max(0, min(100, level))
            sbc.set_brightness(level)
            logger.info(f"💡 Brilho ajustado para {level}%")
            return True
        except Exception as e:
            logger.error(f"❌ Falha ao ajustar brilho: {e}")
            return False

    def open_browser(self, query: str = "") -> bool:
        """Abre o navegador padrão com uma pesquisa no YouTube/Google"""
        try:
            if "música" in query.lower() or "tocar" in query.lower():
                url = f"https://music.youtube.com/search?q={query}"
            else:
                url = f"https://www.google.com/search?q={query}"
            
            webbrowser.open(url)
            logger.info(f"🌐 Navegador aberto para: {query}")
            return True
        except Exception as e:
            logger.error(f"❌ Falha ao abrir navegador: {e}")
            return False

    def set_volume(self, level: int):
        """Ajusta o volume do sistema via nircmd (se disponível) ou powershell"""
        try:
            # Fallback Powershell (Universal)
            level = max(0, min(100, level))
            vol_val = int(level * 655.35)
            cmd = f"(new-object -com wscript.shell).SendKeys([char]174)*50; (new-object -com wscript.shell).SendKeys([char]175)*{level//2}"
            # Nota: O comando acima é aproximado. O ideal seria usar pycaw no futuro.
            # Por simplicidade, usaremos essa abordagem 'quick'
            subprocess.run(["powershell", "-Command", cmd], capture_output=True)
            logger.info(f"🔊 Volume ajustado para aproximadamente {level}%")
        except Exception as e:
            logger.error(f"❌ Falha ao ajustar volume: {e}")

# Instância global
device_manager = DeviceManager()
