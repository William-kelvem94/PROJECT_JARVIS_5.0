"""
MÃ³dulo de captura de tela
ResponsÃ¡vel por capturar screenshots e gravaÃ§Ãµes de tela
"""

import time
import threading
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Callable

logger = logging.getLogger(__name__)

# Imports opcionais com graceful fallback
try:
    import mss
    MSS_AVAILABLE = True
except ImportError:
    MSS_AVAILABLE = False
    logger.warning("mss nÃ£o disponÃ­vel. Instale com: pip install mss")

try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False
    logger.warning("pyautogui nÃ£o disponÃ­vel")

try:
    from PIL import Image, ImageDraw
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    logger.warning("PIL/Pillow nÃ£o disponÃ­vel")

try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    logger.warning("opencv nÃ£o disponÃ­vel")

from src.utils.config import config
from src.utils.helpers import FileHelper, ImageHelper
from src.database.models import db_manager, Capture

class ScreenCapture:
    """Classe principal para captura de tela"""

    def __init__(self):
        if not MSS_AVAILABLE:
            logger.error("ScreenCapture: mss nÃ£o disponÃ­vel. MÃ³dulo desativado.")
            self.enabled = False
            return
            
        self.enabled = True
        self.capture_active = False
        self.recording_active = False
        self.capture_thread = None
        self.recording_thread = None
        
        # Thread-local storage for mss instances
        self.thread_local = threading.local()

        # ConfiguraÃ§Ãµes
        self.capture_delay = config.get_setting('capture.capture_delay', 0.5)
        self.default_format = config.get_setting('capture.default_format', 'PNG')
        self.quality = config.get_setting('capture.quality', 95)

        # Callbacks
        self.on_capture_complete: Optional[Callable[[str], None]] = None
        self.on_recording_complete: Optional[Callable[[str], None]] = None

        logger.info("MÃ³dulo de captura de tela inicializado")

    def _get_sct(self):
        """Retorna instÃ¢ncia de mss especÃ­fica para a thread atual"""
        if not self.enabled or not MSS_AVAILABLE:
            return None
        if not hasattr(self.thread_local, "sct"):
            self.thread_local.sct = mss.mss()
        return self.thread_local.sct

    def capture_fullscreen(self, save_path: Optional[str] = None,
                          capture_type: str = 'manual',
                          monitor_index: Optional[int] = None) -> Optional[str]:
        """
        Captura tela completa ou de um monitor especÃ­fico
        """
        if not self.enabled or not MSS_AVAILABLE:
            logger.warning("Screen capture nÃ£o disponÃ­vel (mss nÃ£o instalado)")
            return None
            
        try:
            sct = self._get_sct()
            if not sct:
                return None
            
            # Selecionar monitor
            if monitor_index is not None and monitor_index < len(sct.monitors):
                monitor = sct.monitors[monitor_index]
            elif capture_type == 'monitor' or capture_type == 'agent':
                # Capturar monitor onde estÃ¡ o cursor
                monitor = self._get_monitor_under_cursor(sct)
            else:
                monitor = sct.monitors[0]  # Todos os monitores

            screenshot = sct.grab(monitor)

            # Converter para PIL Image
            if not PIL_AVAILABLE:
                logger.error("PIL nÃ£o disponÃ­vel para salvar imagem")
                return None
            img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")

            # Salvar captura
            return self._save_capture(img, save_path, capture_type, 'fullscreen')

        except Exception as e:
            logger.error(f"Erro na captura de tela completa: {e}")
            return None

    def capture_all_monitors(self) -> List[str]:
        """Captura cada monitor individualmente e retorna lista de caminhos"""
        paths = []
        try:
            sct = self._get_sct()
            count = len(sct.monitors)
                
            for i in range(1, count):
                path = self.capture_fullscreen(monitor_index=i, capture_type='monitor_batch')
                if path:
                    paths.append(path)
        except Exception as e:
            logger.error(f"Erro ao capturar monitores: {e}")
        return paths

    def _get_monitor_under_cursor(self, sct_instance=None) -> Dict[str, Any]:
        """Identifica qual monitor contÃ©m o cursor do mouse atualmente"""
        try:
            if sct_instance:
                monitors = sct_instance.monitors
            else:
                monitors = self._get_sct().monitors
                    
            x, y = pyautogui.position()
            for monitor in monitors[1:]:
                if (monitor['left'] <= x < monitor['left'] + monitor['width'] and
                    monitor['top'] <= y < monitor['top'] + monitor['height']):
                    return monitor
            return monitors[1] # Fallback para o primeiro se falhar
        except:
             return self._get_sct().monitors[1]

    def capture_region(self, region: Tuple[int, int, int, int],
                      save_path: Optional[str] = None,
                      capture_type: str = 'manual') -> Optional[str]:
        """
        Captura regiÃ£o especÃ­fica da tela
        """
        try:
            x, y, width, height = region

            # Usar pyautogui para captura de regiÃ£o (mais confiÃ¡vel)
            screenshot = pyautogui.screenshot(region=(x, y, width, height))

            # Salvar captura
            return self._save_capture(screenshot, save_path, capture_type, 'region')

        except Exception as e:
            logger.error(f"Erro na captura de regiÃ£o: {e}")
            return None

    def capture_window(self, window_title: str,
                      save_path: Optional[str] = None,
                      capture_type: str = 'auto') -> Optional[str]:
        """
        Captura janela especÃ­fica por tÃ­tulo
        """
        try:
            # Encontrar janela pelo tÃ­tulo usando pyautogui
            window = pyautogui.getWindowsWithTitle(window_title)
            if not window:
                logger.warning(f"Janela com tÃ­tulo '{window_title}' nÃ£o encontrada")
                return None

            window = window[0]

            # Capturar regiÃ£o da janela
            region = (window.left, window.top, window.width, window.height)
            return self.capture_region(region, save_path, capture_type)

        except Exception as e:
            logger.error(f"Erro na captura de janela '{window_title}': {e}")
            return None

    def _save_capture(self, image: Any, save_path: Optional[str], 
                     capture_type: str, capture_method: str) -> Optional[str]:
        """
        Salva a imagem capturada e registra no banco de dados
        """
        try:
            # Gerar caminho se nÃ£o fornecido
            if not save_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:18]
                filename = f"capture_{timestamp}.{self.default_format.lower()}"
                save_path = str(config.CAPTURES_DIR / filename)

            # Garantir diretÃ³rio
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)

            # Salvar imagem
            if isinstance(image, Image.Image):
                image.save(save_path, quality=self.quality, optimize=True)
                width, height = image.size
            else:
                # Assumindo que pode ser outro formato se necessÃ¡rio no futuro
                logger.warning("Formato de imagem desconhecido para salvar")
                return None

            # Calcular hash e tamanho
            file_hash = FileHelper.get_file_hash(save_path)
            file_size_mb = Path(save_path).stat().st_size / (1024 * 1024)

            # Registrar no banco de dados
            session = db_manager.get_session()
            try:
                new_capture = Capture(
                    filename=Path(save_path).name,
                    file_path=str(save_path),
                    file_hash=file_hash,
                    file_size_mb=file_size_mb,
                    capture_type=capture_type,
                    capture_method=capture_method,
                    width=width,
                    height=height,
                    format=self.default_format,
                    quality=self.quality,
                    processing_status='pending'
                )
                session.add(new_capture)
                session.commit()
                
                logger.info(f"Captura salva: {save_path} (ID: {new_capture.id})")
                
                # Notificar callback
                if self.on_capture_complete:
                    self.on_capture_complete(str(save_path))
                    
            except Exception as db_error:
                session.rollback()
                # Se for erro de hash duplicado, apenas logar como debug (nÃ£o Ã© crÃ­tico)
                if "UNIQUE constraint failed" in str(db_error) and "file_hash" in str(db_error):
                    logger.debug(f"Captura duplicada ignorada (hash jÃ¡ existe): {save_path}")
                    # Retornar o path mesmo assim pois a imagem foi salva
                else:
                    logger.error(f"Erro ao registrar captura no banco: {db_error}")
            finally:
                session.close()
                
            return str(save_path)

        except Exception as e:
            logger.error(f"Erro ao salvar captura: {e}")
            return None
        finally:
            # ðŸ†• AUTO-CLEANUP (ProteÃ§Ã£o de Disco)
            self._cleanup_old_captures()

    def _cleanup_old_captures(self):
        """MantÃ©m apenas as 100 capturas mais recentes para evitar saturaÃ§Ã£o de disco"""
        try:
            captures = sorted(config.CAPTURES_DIR.glob("capture_*.png"), key=lambda x: x.stat().st_mtime)
            if len(captures) > 100:
                for old_file in captures[:-100]:
                     try:
                         old_file.unlink()
                         # logger.debug(f"Caputura antiga removida: {old_file.name}")
                     except: pass
        except Exception as e:
            logger.warning(f"Falha no cleanup de capturas: {e}")



            
    # Skipping start_area_selection for brevity as it was just a print

    def start_screen_recording(self, region: Optional[Tuple[int, int, int, int]] = None,
                              output_path: Optional[str] = None,
                              duration: Optional[int] = None) -> bool:
        """
        Inicia gravaÃ§Ã£o de tela
        """
        if self.recording_active:
            logger.warning("GravaÃ§Ã£o jÃ¡ estÃ¡ ativa")
            return False

        try:
            self.recording_active = True
            self.recording_thread = threading.Thread(
                target=self._record_screen_thread,
                args=(region, output_path, duration)
            )
            self.recording_thread.daemon = True
            self.recording_thread.start()

            logger.info("GravaÃ§Ã£o de tela iniciada")
            return True

        except Exception as e:
            logger.error(f"Erro ao iniciar gravaÃ§Ã£o: {e}")
            self.recording_active = False
            return False

    def _record_screen_thread(self, region: Optional[Tuple[int, int, int, int]],
                            output_path: Optional[str], duration: Optional[int]):
        """Thread para gravaÃ§Ã£o de tela"""
        try:
            # Configurar codec e saÃ­da
            if not output_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = str(config.CAPTURES_DIR / f"recording_{timestamp}.avi")

            # Definir regiÃ£o
            sct = self._get_sct()
            if region:
                x, y, width, height = region
            else:
                monitor = sct.monitors[0]
                x, y, width, height = monitor["left"], monitor["top"], monitor["width"], monitor["height"]

            # Configurar writer do OpenCV
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            fps = 10  # 10 FPS Ã© suficiente para a maioria dos casos
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

            start_time = time.time()
            frame_count = 0

            logger.info(f"Iniciando gravaÃ§Ã£o: {output_path}")

            while self.recording_active:
                # Verificar duraÃ§Ã£o mÃ¡xima
                if duration and (time.time() - start_time) >= duration:
                    break

                # Capturar frame
                screenshot = sct.grab({"left": x, "top": y, "width": width, "height": height})
                frame = np.frombuffer(screenshot.bgra, dtype=np.uint8)
                frame = frame.reshape((height, width, 4))[:, :, :3]  # Remover canal alpha

                # Escrever frame
                out.write(frame)
                frame_count += 1

                # Pequena pausa para nÃ£o sobrecarregar CPU
                time.sleep(0.1)

            # Finalizar gravaÃ§Ã£o
            out.release()
            
            self.recording_active = False

            logger.info(f"GravaÃ§Ã£o finalizada: {frame_count} frames salvos em {output_path}")

            # Chamar callback se definido
            if self.on_recording_complete:
                try:
                    self.on_recording_complete(output_path)
                except Exception as e:
                    logger.error(f"Erro no callback de gravaÃ§Ã£o: {e}")

        except Exception as e:
            logger.error(f"Erro na thread de gravaÃ§Ã£o: {e}")
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
        """Retorna informaÃ§Ãµes dos monitores disponÃ­veis"""
        monitors = []
        try:
            sct = self._get_sct()
            for i, monitor in enumerate(sct.monitors[1:], 1):  # Pular monitor 0 (todo)
                monitors.append({
                    'id': i,
                    'x': monitor['left'],
                    'y': monitor['top'],
                    'width': monitor['width'],
                    'height': monitor['height'],
                    'is_primary': i == 1
                })
        except Exception as e:
            logger.error(f"Erro ao obter info do monitor: {e}")
            
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
                # Adicionar cursor (implementaÃ§Ã£o bÃ¡sica)
                # Nota: ImplementaÃ§Ã£o completa do cursor requer bibliotecas adicionais
                # como pywin32 no Windows
                logger.info("Screenshot com cursor capturado (cursor nÃ£o renderizado)")

            return screenshot

        except Exception as e:
            logger.error(f"Erro na captura com cursor: {e}")
            return None

# InstÃ¢ncia global
screen_capture = ScreenCapture()
