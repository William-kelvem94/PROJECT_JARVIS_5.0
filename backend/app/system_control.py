import logging
import psutil
import pyautogui
import screen_brightness_control as sbc
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from screeninfo import get_monitors

# Configure logging for SystemControlMatrix
logger = logging.getLogger("JARVIS.SystemControlMatrix")

class SystemControlMatrix:
    """
    SystemControlMatrix is the core hardware and OS orchestration layer for JARVIS.
    It provides low-level control over system volume, brightness, screen capture,
    and hardware telemetry.
    """

    def __init__(self):
        logger.info("Initializing SystemControlMatrix core...")
        # Initialize pycaw devices with multiple fallback methods
        self.volume_control = None
        
        # Method 1: Standard pycaw initialization
        try:
            devices = AudioUtilities.GetSpeakers()
            if devices is None:
                raise RuntimeError("No audio devices found")
            
            interface = devices.Activate(
                IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            self.volume_control = cast(interface, POINTER(IAudioEndpointVolume))
            logger.info("Audio control interface initialized successfully (Method 1).")
        
        except AttributeError as e:
            # Method 2: Try without cast
            logger.warning(f"Method 1 failed ({e}), trying Method 2...")
            try:
                devices = AudioUtilities.GetSpeakers()
                if devices:
                    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                    self.volume_control = interface
                    logger.info("Audio control initialized via Method 2 (no cast).")
            except Exception as e2:
                logger.error(f"Method 2 failed: {e2}")
        
        except Exception as e:
            # Method 3: Try alternative pycaw API
            logger.warning(f"Standard initialization failed ({e}), trying Method 3...")
            try:
                from pycaw.api.audioclient import IAudioClient
                from pycaw.api.endpointvolume import IAudioEndpointVolume as IAudioEndpointVolumeAPI
                
                devices = AudioUtilities.GetSpeakers()
                if devices and hasattr(devices, 'QueryInterface'):
                    self.volume_control = devices.QueryInterface(IAudioEndpointVolumeAPI)
                    logger.info("Audio control initialized via Method 3 (QueryInterface).")
                else:
                    raise RuntimeError("QueryInterface not available")
            
            except Exception as e3:
                # Method 4: Complete fallback - disable audio control
                logger.error(f"Method 3 failed: {e3}")
                logger.warning("All audio initialization methods failed. Audio control will be disabled.")
                logger.info("This is not critical - system will continue without volume control.")
                self.volume_control = None

    def set_volume(self, level: float):
        """
        Sets the master system volume.
        :param level: Float between 0.0 (mute) and 1.0 (max)
        """
        try:
            if self.volume_control is None:
                raise RuntimeError("Volume control interface not available.")

            # Clamp value between 0.0 and 1.0
            clamped_level = max(0.0, min(1.0, level))
            self.volume_control.SetMasterVolumeLevelScalar(clamped_level, None)
            logger.info(f"System volume set to {clamped_level * 100:.1f}%")
            return {"status": "success", "volume": clamped_level}
        except Exception as e:
            logger.error(f"Error setting volume: {e}")
            return {"status": "error", "message": str(e)}

    def set_brightness(self, level: int):
        """
        Sets the system screen brightness.
        :param level: Integer between 0 and 100
        """
        try:
            # Clamp value between 0 and 100
            clamped_level = max(0, min(100, level))
            sbc.set_brightness(clamped_level)
            logger.info(f"System brightness set to {clamped_level}%")
            return {"status": "success", "brightness": clamped_level}
        except Exception as e:
            logger.error(f"Error setting brightness: {e}")
            return {"status": "error", "message": str(e)}

    def capture_screens(self):
        """
        Captures all connected monitors and saves them as screenshots.
        Returns a list of paths to the captured images.
        """
        try:
            monitors = get_monitors()
            captured_files = []

            for i, m in enumerate(monitors):
                # Define capture region for each monitor
                region = (m.x, m.y, m.width, m.height)
                filename = f"screenshot_monitor_{i}.png"
                screenshot = pyautogui.screenshot(region=region)
                screenshot.save(filename)
                captured_files.append(filename)

            logger.info(f"Captured {len(monitors)} screen(s).")
            return {"status": "success", "files": captured_files}
        except Exception as e:
            logger.error(f"Error capturing screens: {e}")
            return {"status": "error", "message": str(e)}

    def get_hardware_status(self):
        """
        Retrieves current hardware utilization (CPU, RAM, VRAM).
        """
        try:
            cpu_usage = psutil.cpu_percent(interval=0.1)
            ram = psutil.virtual_memory()

            # VRAM detection
            vram_info = "N/A (Requires GPUtil)"
            try:
                import GPUtil
                gpus = GPUtil.getGPUs()
                if gpus:
                    vram_info = f"{gpus[0].memoryUsed}MB / {gpus[0].memoryTotal}MB ({gpus[0].memoryUtil*100:.1f}%)"
            except ImportError:
                pass

            status = {
                "cpu_usage_percent": cpu_usage,
                "ram_used_gb": round(ram.used / (1024**3), 2),
                "ram_total_gb": round(ram.total / (1024**3), 2),
                "ram_usage_percent": ram.percent,
                "vram_status": vram_info
            }
            logger.info(f"Hardware Status: CPU {cpu_usage}%, RAM {ram.percent}%")
            return {"status": "success", "data": status}
        except Exception as e:
            logger.error(f"Error retrieving hardware status: {e}")
            return {"status": "error", "message": str(e)}

# Singleton instance for core integration
system_control_matrix = SystemControlMatrix()
