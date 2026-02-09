"""
Senses - Screen Monitor
Monitora mudanças na tela
"""

import logging
from pathlib import Path
import time
from typing import Optional, Callable
import hashlib

logger = logging.getLogger(__name__)

class ScreenMonitor:
    """Monitor de mudanças na tela"""
    
    def __init__(self):
        self.monitoring = False
        self.last_screenshot_hash = None
        self.change_callback = None
        self.cv2 = None
        
        try:
            import cv2
            self.cv2 = cv2
            logger.info("✅ Screen Monitor disponível")
        except ImportError:
            logger.warning("⚠️ OpenCV não disponível")
    
    def start_monitoring(self, callback: Optional[Callable] = None, interval: float = 1.0):
        """Inicia monitoramento"""
        if not self.cv2:
            logger.error("❌ OpenCV necessário para monitoramento")
            return
        
        self.monitoring = True
        self.change_callback = callback
        
        logger.info(f"👁️ Monitoramento iniciado (intervalo: {interval}s)")
        
        import asyncio
        asyncio.create_task(self._monitor_loop(interval))
    
    async def _monitor_loop(self, interval: float):
        """Loop de monitoramento"""
        import asyncio
        
        while self.monitoring:
            changed = self.check_for_changes()
            
            if changed and self.change_callback:
                await self.change_callback()
            
            await asyncio.sleep(interval)
    
    def check_for_changes(self) -> bool:
        """Verifica se tela mudou"""
        if not self.cv2:
            return False
        
        # Capturar screenshot
        screenshot_path = self._capture_screenshot()
        
        if not screenshot_path:
            return False
        
        # Calcular hash
        current_hash = self._calculate_hash(screenshot_path)
        
        # Comparar com anterior
        if self.last_screenshot_hash is None:
            self.last_screenshot_hash = current_hash
            return False
        
        changed = current_hash != self.last_screenshot_hash
        
        if changed:
            logger.debug("📸 Mudança detectada na tela")
            self.last_screenshot_hash = current_hash
        
        return changed
    
    def _capture_screenshot(self) -> Optional[Path]:
        """Captura screenshot"""
        try:
            import pyautogui
            
            screenshot_path = Path("data/temp/screen_monitor.png")
            screenshot_path.parent.mkdir(parents=True, exist_ok=True)
            
            screenshot = pyautogui.screenshot()
            screenshot.save(screenshot_path)
            
            return screenshot_path
        except Exception as e:
            logger.error(f"❌ Erro ao capturar tela: {e}")
            return None
    
    def _calculate_hash(self, image_path: Path) -> str:
        """Calcula hash da imagem"""
        try:
            with open(image_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except:
            return ""
    
    def stop_monitoring(self):
        """Para monitoramento"""
        self.monitoring = False
        logger.info("🛑 Monitoramento parado")


# Instância global
screen_monitor = ScreenMonitor()
