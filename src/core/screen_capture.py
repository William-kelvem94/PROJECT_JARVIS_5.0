"""
Módulo de captura de tela
Responsável por capturar screenshots e gravações de tela
"""

import time
import threading
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Callable
import mss
import pyautogui
from PIL import Image, ImageDraw
import cv2
import numpy as np
from src.utils.config import config
from src.utils.helpers import FileHelper, ImageHelper
from src.database.models import db_manager, Capture

logger = logging.getLogger(__name__)

class ScreenCapture:
    """Classe principal para captura de tela"""

    def __init__(self):
        self.capture_active = False
        self.recording_active = False
        self.capture_thread = None
        self.recording_thread = None
        self.sct = mss.mss()

        # Configurações
        self.capture_delay = config.get_setting('capture.capture_delay', 0.5)
        self.default_format = config.get_setting('capture.default_format', 'PNG')
        self.quality = config.get_setting('capture.quality', 95)

        # Callbacks
        self.on_capture_complete: Optional[Callable[[str], None]] = None
        self.on_recording_complete: Optional[Callable[[str], None]] = None

        logger.info("Módulo de captura de tela inicializado")

    def capture_fullscreen(self, save_path: Optional[str] = None,
                          capture_type: str = 'manual') -> Optional[str]:
        """
        Captura tela completa

        Args:
            save_path: Caminho personalizado para salvar (opcional)
            capture_type: Tipo da captura (manual, auto, timer)

        Returns:
            Caminho do arquivo salvo ou None se erro
        """
        try:
            # Capturar tela usando mss (mais rápido)
            monitor = self.sct.monitors[0]  # Monitor principal
            screenshot = self.sct.grab(monitor)

            # Converter para PIL Image
            img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")

            # Salvar captura
            return self._save_capture(img, save_path, capture_type, 'fullscreen')

        except Exception as e:
            logger.error(f"Erro na captura de tela completa: {e}")
            return None

    def capture_region(self, region: Tuple[int, int, int, int],
                      save_path: Optional[str] = None,
                      capture_type: str = 'manual') -> Optional[str]:
        """
        Captura região específica da tela

        Args:
            region: Tupla (x, y, width, height)
            save_path: Caminho personalizado para salvar
            capture_type: Tipo da captura

        Returns:
            Caminho do arquivo salvo ou None se erro
        """
        try:
            x, y, width, height = region

            # Usar pyautogui para captura de região (mais confiável)
            screenshot = pyautogui.screenshot(region=(x, y, width, height))

            # Salvar captura
            return self._save_capture(screenshot, save_path, capture_type, 'region')

        except Exception as e:
            logger.error(f"Erro na captura de região: {e}")
            return None

    def capture_window(self, window_title: str,
                      save_path: Optional[str] = None,
                      capture_type: str = 'auto') -> Optional[str]:
        """
        Captura janela específica por título

        Args:
            window_title: Título da janela
            save_path: Caminho personalizado para salvar
            capture_type: Tipo da captura

        Returns:
            Caminho do arquivo salvo ou None se erro
        """
        try:
            # Encontrar janela pelo título usando pyautogui
            window = pyautogui.getWindowsWithTitle(window_title)
            if not window:
                logger.warning(f"Janela com título '{window_title}' não encontrada")
                return None

            window = window[0]

            # Capturar região da janela
            region = (window.left, window.top, window.width, window.height)
            return self.capture_region(region, save_path, capture_type)

        except Exception as e:
            logger.error(f"Erro na captura de janela '{window_title}': {e}")
            return None

    def start_area_selection(self) -> Optional[Tuple[int, int, int, int]]:
        """
        Inicia seleção de área interativa

        Returns:
            Tupla (x, y, width, height) da área selecionada ou None
        """
        try:
            logger.info("Iniciando seleção de área...")

            # Minimizar interface principal se existir
            # (Será implementado quando a GUI for criada)

            # Usar pyautogui para seleção
            # Nota: pyautogui não tem seleção visual nativa,
            # então usaremos uma abordagem diferente

            print("Clique e arraste para selecionar a área...")
            print("Pressione ESC para cancelar")

            # Para implementação completa, precisaremos de uma GUI customizada
            # Por enquanto, retornamos None
            return None

        except Exception as e:
            logger.error(f"Erro na seleção de área: {e}")
            return None

    def start_screen_recording(self, region: Optional[Tuple[int, int, int, int]] = None,
                              output_path: Optional[str] = None,
                              duration: Optional[int] = None) -> bool:
        """
        Inicia gravação de tela

        Args:
            region: Região para gravar (opcional)
            output_path: Caminho de saída (opcional)
            duration: Duração em segundos (opcional)

        Returns:
            True se iniciou com sucesso
        """
        if self.recording_active:
            logger.warning("Gravação já está ativa")
            return False

        try:
            self.recording_active = True
            self.recording_thread = threading.Thread(
                target=self._record_screen_thread,
                args=(region, output_path, duration)
            )
            self.recording_thread.daemon = True
            self.recording_thread.start()

            logger.info("Gravação de tela iniciada")
            return True

        except Exception as e:
            logger.error(f"Erro ao iniciar gravação: {e}")
            self.recording_active = False
            return False

    def stop_screen_recording(self) -> bool:
        """
        Para gravação de tela

        Returns:
            True se parou com sucesso
        """
        if not self.recording_active:
            logger.warning("Nenhuma gravação ativa para parar")
            return False

        try:
            self.recording_active = False

            if self.recording_thread and self.recording_thread.is_alive():
                self.recording_thread.join(timeout=5)

            logger.info("Gravação de tela parada")
            return True

        except Exception as e:
            logger.error(f"Erro ao parar gravação: {e}")
            return False

    def start_timer_capture(self, interval_seconds: int,
                           max_captures: Optional[int] = None,
                           region: Optional[Tuple[int, int, int, int]] = None) -> bool:
        """
        Inicia captura automática por timer

        Args:
            interval_seconds: Intervalo entre capturas
            max_captures: Número máximo de capturas (opcional)
            region: Região para capturar (opcional)

        Returns:
            True se iniciou com sucesso
        """
        if self.capture_active:
            logger.warning("Captura por timer já está ativa")
            return False

        try:
            self.capture_active = True
            self.capture_thread = threading.Thread(
                target=self._timer_capture_thread,
                args=(interval_seconds, max_captures, region)
            )
            self.capture_thread.daemon = True
            self.capture_thread.start()

            logger.info(f"Captura por timer iniciada (intervalo: {interval_seconds}s)")
            return True

        except Exception as e:
            logger.error(f"Erro ao iniciar captura por timer: {e}")
            self.capture_active = False
            return False

    def stop_timer_capture(self) -> bool:
        """
        Para captura por timer

        Returns:
            True se parou com sucesso
        """
        if not self.capture_active:
            logger.warning("Nenhuma captura por timer ativa para parar")
            return False

        try:
            self.capture_active = False

            if self.capture_thread and self.capture_thread.is_alive():
                self.capture_thread.join(timeout=5)

            logger.info("Captura por timer parada")
            return True

        except Exception as e:
            logger.error(f"Erro ao parar captura por timer: {e}")
            return False

    def _save_capture(self, image: Image.Image, save_path: Optional[str],
                     capture_type: str, capture_method: str) -> Optional[str]:
        """Salva captura no disco e registra no banco"""
        try:
            # Gerar nome de arquivo se não fornecido
            if not save_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"capture_{timestamp}.{self.default_format.lower()}"
                save_path = str(config.CAPTURES_DIR / filename)

            # Garantir diretório existe
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)

            # Salvar imagem
            if self.default_format.upper() == 'PNG':
                image.save(save_path, 'PNG', optimize=True)
            elif self.default_format.upper() == 'JPEG':
                image.save(save_path, 'JPEG', quality=self.quality, optimize=True)
            else:
                image.save(save_path, self.default_format.upper())

            # Calcular informações do arquivo
            file_hash = FileHelper.get_file_hash(save_path)
            file_size_mb = FileHelper.get_file_size_mb(save_path)

            # Verificar se já existe captura com mesmo hash
            existing_capture = db_manager.get_capture_by_hash(file_hash)
            if existing_capture:
                logger.info(f"Captura duplicada encontrada: {existing_capture.file_path}")
                # Remover arquivo duplicado
                Path(save_path).unlink()
                return existing_capture.file_path

            # Registrar no banco de dados
            capture = Capture(
                filename=Path(save_path).name,
                file_path=save_path,
                file_hash=file_hash,
                file_size_mb=file_size_mb,
                capture_type='screenshot',
                capture_method=capture_method,
                width=image.width,
                height=image.height,
                format=self.default_format,
                quality=self.quality,
                processing_status='pending'
            )

            db_manager.execute_in_session(lambda session: session.add(capture))

            logger.info(f"Captura salva: {save_path}")

            # Chamar callback se definido
            if self.on_capture_complete:
                try:
                    self.on_capture_complete(save_path)
                except Exception as e:
                    logger.error(f"Erro no callback de captura: {e}")

            return save_path

        except Exception as e:
            logger.error(f"Erro ao salvar captura: {e}")
            return None

    def _record_screen_thread(self, region: Optional[Tuple[int, int, int, int]],
                            output_path: Optional[str], duration: Optional[int]):
        """Thread para gravação de tela"""
        try:
            # Configurar codec e saída
            if not output_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = str(config.CAPTURES_DIR / f"recording_{timestamp}.avi")

            # Definir região
            if region:
                x, y, width, height = region
            else:
                monitor = self.sct.monitors[0]
                x, y, width, height = monitor["left"], monitor["top"], monitor["width"], monitor["height"]

            # Configurar writer do OpenCV
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            fps = 10  # 10 FPS é suficiente para a maioria dos casos
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

            start_time = time.time()
            frame_count = 0

            logger.info(f"Iniciando gravação: {output_path}")

            while self.recording_active:
                # Verificar duração máxima
                if duration and (time.time() - start_time) >= duration:
                    break

                # Capturar frame
                screenshot = self.sct.grab({"left": x, "top": y, "width": width, "height": height})
                frame = np.frombuffer(screenshot.bgra, dtype=np.uint8)
                frame = frame.reshape((height, width, 4))[:, :, :3]  # Remover canal alpha

                # Escrever frame
                out.write(frame)
                frame_count += 1

                # Pequena pausa para não sobrecarregar CPU
                time.sleep(0.1)

            # Finalizar gravação
            out.release()
            self.recording_active = False

            logger.info(f"Gravação finalizada: {frame_count} frames salvos em {output_path}")

            # Chamar callback se definido
            if self.on_recording_complete:
                try:
                    self.on_recording_complete(output_path)
                except Exception as e:
                    logger.error(f"Erro no callback de gravação: {e}")

        except Exception as e:
            logger.error(f"Erro na thread de gravação: {e}")
            self.recording_active = False

    def _timer_capture_thread(self, interval_seconds: int,
                            max_captures: Optional[int],
                            region: Optional[Tuple[int, int, int, int]]):
        """Thread para captura por timer"""
        capture_count = 0

        logger.info("Thread de captura por timer iniciada")

        while self.capture_active:
            try:
                # Verificar limite de capturas
                if max_captures and capture_count >= max_captures:
                    break

                # Capturar
                if region:
                    self.capture_region(region, capture_type='timer')
                else:
                    self.capture_fullscreen(capture_type='timer')

                capture_count += 1

                # Aguardar intervalo
                time.sleep(interval_seconds)

            except Exception as e:
                logger.error(f"Erro na captura por timer: {e}")
                time.sleep(1)  # Pausa de erro

        self.capture_active = False
        logger.info(f"Thread de captura por timer finalizada. Total de capturas: {capture_count}")

    def get_monitor_info(self) -> List[Dict[str, Any]]:
        """Retorna informações dos monitores disponíveis"""
        monitors = []
        for i, monitor in enumerate(self.sct.monitors[1:], 1):  # Pular monitor 0 (todo)
            monitors.append({
                'id': i,
                'x': monitor['left'],
                'y': monitor['top'],
                'width': monitor['width'],
                'height': monitor['height'],
                'is_primary': i == 1
            })

        return monitors

    def take_screenshot_with_cursor(self, save_path: Optional[str] = None) -> Optional[str]:
        """
        Captura screenshot incluindo o cursor do mouse

        Returns:
            Caminho do arquivo salvo ou None se erro
        """
        try:
            # Capturar tela
            screenshot = self.capture_fullscreen(save_path)

            if screenshot:
                # Adicionar cursor (implementação básica)
                # Nota: Implementação completa do cursor requer bibliotecas adicionais
                # como pywin32 no Windows
                logger.info("Screenshot com cursor capturado (cursor não renderizado)")

            return screenshot

        except Exception as e:
            logger.error(f"Erro na captura com cursor: {e}")
            return None

# Instância global
screen_capture = ScreenCapture()
