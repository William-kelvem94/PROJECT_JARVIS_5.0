"""
JARVIS Hardware - Monitoramento e Controle de Hardware
Sistema agnóstico que se adapta automaticamente ao hardware
"""

import os
import platform
import time
from typing import Dict, Any, Optional, List
from pathlib import Path

import config

class HardwareMonitor:
    """
    Monitor de hardware inteligente que se adapta ao dispositivo.
    Detecta automaticamente Galaxy Book2 vs Desktop.
    """

    def __init__(self):
        self.system = platform.system().lower()
        self.is_docker = self._check_docker()
        self.hardware_info = self._detect_hardware()

        # Inicializar monitores específicos
        self.monitors = {
            "cpu": self._init_cpu_monitor(),
            "memory": self._init_memory_monitor(),
            "disk": self._init_disk_monitor(),
            "temperature": self._init_temperature_monitor(),
            "battery": self._init_battery_monitor() if self.hardware_info["is_laptop"] else None,
            "gpu": self._init_gpu_monitor() if self.hardware_info["is_desktop"] else None
        }

    def _check_docker(self) -> bool:
        """Verifica se está rodando em Docker."""
        return (
            os.path.exists('/.dockerenv') or
            os.environ.get('DOCKER_CONTAINER') == 'true' or
            os.path.exists('/proc/1/cgroup') and 'docker' in open('/proc/1/cgroup').read()
        )

    def _detect_hardware(self) -> Dict[str, Any]:
        """Detecta automaticamente o hardware."""
        info = {
            "system": self.system,
            "architecture": platform.architecture()[0],
            "processor": platform.processor(),
            "hostname": platform.node(),
            "is_docker": self.is_docker
        }

        # Detectar tipo de dispositivo
        if self.system == "windows":
            info.update(self._detect_windows_hardware())
        elif self.system == "linux":
            info.update(self._detect_linux_hardware())
        else:
            info.update({
                "is_laptop": False,
                "is_desktop": True,
                "device_type": "unknown"
            })

        return info

    def _detect_windows_hardware(self) -> Dict[str, Any]:
        """Detecta hardware específico do Windows."""
        try:
            import subprocess

            # Verificar bateria (PowerShell)
            battery_cmd = 'powershell "Get-WmiObject Win32_Battery | Select-Object -First 1 | ConvertTo-Json"'
            result = subprocess.run(battery_cmd, capture_output=True, text=True, timeout=5)

            has_battery = result.returncode == 0 and result.stdout.strip()

            # Verificar se é Galaxy Book (Samsung)
            samsung_cmd = 'powershell "Get-WmiObject Win32_ComputerSystem | Select-Object Manufacturer | ConvertTo-Json"'
            samsung_result = subprocess.run(samsung_cmd, capture_output=True, text=True, timeout=5)

            is_samsung = "samsung" in samsung_result.stdout.lower() if samsung_result.returncode == 0 else False

            return {
                "is_laptop": has_battery,
                "is_desktop": not has_battery,
                "device_type": "galaxy_book" if is_samsung and has_battery else ("laptop" if has_battery else "desktop"),
                "manufacturer": "Samsung" if is_samsung else "Unknown"
            }

        except Exception as e:
            print(f"Erro detectando hardware Windows: {e}")
            return {
                "is_laptop": False,
                "is_desktop": True,
                "device_type": "desktop",
                "manufacturer": "Unknown"
            }

    def _detect_linux_hardware(self) -> Dict[str, Any]:
        """Detecta hardware específico do Linux."""
        try:
            # Verificar bateria
            battery_paths = [
                "/sys/class/power_supply/BAT0",
                "/sys/class/power_supply/BAT1"
            ]
            has_battery = any(Path(p).exists() for p in battery_paths)

            # Verificar fabricante
            manufacturer = "Unknown"
            try:
                with open("/sys/class/dmi/id/sys_vendor", "r") as f:
                    manufacturer = f.read().strip()
            except:
                pass

            return {
                "is_laptop": has_battery,
                "is_desktop": not has_battery,
                "device_type": "laptop" if has_battery else "desktop",
                "manufacturer": manufacturer
            }

        except Exception as e:
            print(f"Erro detectando hardware Linux: {e}")
            return {
                "is_laptop": False,
                "is_desktop": True,
                "device_type": "desktop",
                "manufacturer": "Unknown"
            }

    def _init_cpu_monitor(self):
        """Inicializa monitoramento de CPU."""
        try:
            import psutil
            return {"psutil": True}
        except ImportError:
            return {"psutil": False}

    def _init_memory_monitor(self):
        """Inicializa monitoramento de memória."""
        try:
            import psutil
            return {"psutil": True}
        except ImportError:
            return {"psutil": False}

    def _init_disk_monitor(self):
        """Inicializa monitoramento de disco."""
        try:
            import psutil
            return {"psutil": True}
        except ImportError:
            return {"psutil": False}

    def _init_temperature_monitor(self):
        """Inicializa monitoramento de temperatura."""
        if self.system == "windows":
            try:
                import wmi
                return {"wmi": True, "wmi_conn": wmi.WMI()}
            except ImportError:
                return {"wmi": False}
        elif self.system == "linux":
            # Verificar sensores
            try:
                import subprocess
                result = subprocess.run(["sensors"], capture_output=True, text=True)
                return {"sensors_available": result.returncode == 0}
            except:
                return {"sensors_available": False}
        return {}

    def _init_battery_monitor(self):
        """Inicializa monitoramento de bateria."""
        if not self.hardware_info["is_laptop"]:
            return None

        try:
            import psutil
            return {"psutil": True}
        except ImportError:
            return {"psutil": False}

    def _init_gpu_monitor(self):
        """Inicializa monitoramento de GPU."""
        try:
            import GPUtil
            return {"gputil": True}
        except ImportError:
            return {"gputil": False}

    def get_system_info(self) -> Dict[str, Any]:
        """Retorna informações completas do sistema."""
        info = self.hardware_info.copy()

        # Adicionar métricas em tempo real
        info.update({
            "cpu": self.get_cpu_info(),
            "memory": self.get_memory_info(),
            "disk": self.get_disk_info(),
            "temperature": self.get_temperature_info(),
            "timestamp": time.time()
        })

        if self.hardware_info["is_laptop"]:
            info["battery"] = self.get_battery_info()

        if self.hardware_info["is_desktop"]:
            info["gpu"] = self.get_gpu_info()

        return info

    def get_cpu_info(self) -> Dict[str, Any]:
        """Retorna informações da CPU."""
        try:
            import psutil

            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()

            return {
                "usage_percent": cpu_percent,
                "cores": cpu_count,
                "frequency_mhz": cpu_freq.current if cpu_freq else None,
                "available": True
            }
        except Exception as e:
            return {
                "error": str(e),
                "available": False
            }

    def get_memory_info(self) -> Dict[str, Any]:
        """Retorna informações da memória."""
        try:
            import psutil

            mem = psutil.virtual_memory()
            return {
                "total_gb": round(mem.total / (1024**3), 2),
                "used_gb": round(mem.used / (1024**3), 2),
                "free_gb": round(mem.available / (1024**3), 2),
                "usage_percent": mem.percent,
                "available": True
            }
        except Exception as e:
            return {
                "error": str(e),
                "available": False
            }

    def get_disk_info(self) -> Dict[str, Any]:
        """Retorna informações dos discos."""
        try:
            import psutil

            disks = []
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disks.append({
                        "mount": partition.mountpoint,
                        "total_gb": round(usage.total / (1024**3), 2),
                        "used_gb": round(usage.used / (1024**3), 2),
                        "free_gb": round(usage.free / (1024**3), 2),
                        "usage_percent": usage.percent
                    })
                except:
                    continue

            return {
                "disks": disks,
                "available": True
            }
        except Exception as e:
            return {
                "error": str(e),
                "available": False
            }

    def get_temperature_info(self) -> Dict[str, Any]:
        """Retorna informações de temperatura."""
        try:
            if self.system == "windows":
                return self._get_windows_temperature()
            elif self.system == "linux":
                return self._get_linux_temperature()
            else:
                return {"available": False, "reason": "Sistema não suportado"}
        except Exception as e:
            return {
                "error": str(e),
                "available": False
            }

    def _get_windows_temperature(self) -> Dict[str, Any]:
        """Obtém temperatura no Windows."""
        try:
            if not self.monitors["temperature"].get("wmi"):
                return {"available": False, "reason": "WMI não disponível"}

            wmi_conn = self.monitors["temperature"]["wmi_conn"]
            temperature_info = wmi_conn.query("SELECT * FROM Win32_TemperatureProbe")

            temperatures = []
            for probe in temperature_info:
                if probe.CurrentReading:
                    # Convert from tenths of degrees Celsius to Celsius
                    temp_c = (probe.CurrentReading - 2732) / 10.0 if probe.CurrentReading > 1000 else probe.CurrentReading / 10.0
                    temperatures.append({
                        "sensor": probe.Name or "CPU",
                        "temperature_c": round(temp_c, 1)
                    })

            return {
                "sensors": temperatures,
                "available": len(temperatures) > 0
            }
        except Exception as e:
            return {
                "error": str(e),
                "available": False
            }

    def _get_linux_temperature(self) -> Dict[str, Any]:
        """Obtém temperatura no Linux."""
        try:
            import subprocess

            # Tentar usar lm-sensors
            if self.monitors["temperature"].get("sensors_available"):
                result = subprocess.run(["sensors"], capture_output=True, text=True, timeout=5)

                if result.returncode == 0:
                    # Parse output (simplified)
                    lines = result.stdout.split('\n')
                    sensors = []

                    for line in lines:
                        if '°C' in line and ':' in line:
                            parts = line.split(':')
                            if len(parts) >= 2:
                                sensor_name = parts[0].strip()
                                temp_part = parts[1].split('°C')[0].strip()
                                try:
                                    temp_c = float(temp_part.replace('+', ''))
                                    sensors.append({
                                        "sensor": sensor_name,
                                        "temperature_c": temp_c
                                    })
                                except:
                                    continue

                    return {
                        "sensors": sensors,
                        "available": len(sensors) > 0
                    }

            return {"available": False, "reason": "Sensores não disponíveis"}

        except Exception as e:
            return {
                "error": str(e),
                "available": False
            }

    def get_battery_info(self) -> Dict[str, Any]:
        """Retorna informações da bateria (apenas laptops)."""
        if not self.hardware_info["is_laptop"]:
            return {"available": False, "reason": "Não é um laptop"}

        try:
            import psutil

            battery = psutil.sensors_battery()
            if battery:
                return {
                    "percent": battery.percent,
                    "time_left_hours": round(battery.secsleft / 3600, 2) if battery.secsleft != psutil.POWER_TIME_UNLIMITED else None,
                    "is_plugged": battery.power_plugged,
                    "available": True
                }
            else:
                return {"available": False, "reason": "Bateria não detectada"}

        except Exception as e:
            return {
                "error": str(e),
                "available": False
            }

    def get_gpu_info(self) -> Dict[str, Any]:
        """Retorna informações da GPU (foco em desktops parrudos)."""
        if not self.hardware_info["is_desktop"]:
            return {"available": False, "reason": "Não é um desktop"}

        try:
            if not self.monitors["gpu"].get("gputil"):
                return {"available": False, "reason": "GPUtil não disponível"}

            import GPUtil

            gpus = GPUtil.getGPUs()
            gpu_info = []

            for gpu in gpus:
                gpu_info.append({
                    "name": gpu.name,
                    "memory_used_mb": gpu.memoryUsed,
                    "memory_total_mb": gpu.memoryTotal,
                    "memory_free_mb": gpu.memoryFree,
                    "memory_usage_percent": gpu.memoryUtil * 100,
                    "gpu_usage_percent": gpu.load * 100,
                    "temperature_c": gpu.temperature
                })

            return {
                "gpus": gpu_info,
                "available": len(gpu_info) > 0
            }

        except Exception as e:
            return {
                "error": str(e),
                "available": False
            }

    def get_health_status(self) -> Dict[str, Any]:
        """Retorna status geral de saúde do hardware."""
        info = self.get_system_info()

        status = {
            "overall": "healthy",
            "warnings": [],
            "critical": []
        }

        # Verificar CPU
        if info.get("cpu", {}).get("available"):
            cpu_usage = info["cpu"]["usage_percent"]
            if cpu_usage > 90:
                status["critical"].append(f"CPU sobrecarregada: {cpu_usage}%")
                status["overall"] = "critical"
            elif cpu_usage > 80:
                status["warnings"].append(f"CPU alta utilização: {cpu_usage}%")
                if status["overall"] == "healthy":
                    status["overall"] = "warning"

        # Verificar memória
        if info.get("memory", {}).get("available"):
            mem_usage = info["memory"]["usage_percent"]
            if mem_usage > 95:
                status["critical"].append(f"Memória crítica: {mem_usage}%")
                status["overall"] = "critical"
            elif mem_usage > 85:
                status["warnings"].append(f"Memória alta: {mem_usage}%")
                if status["overall"] == "healthy":
                    status["overall"] = "warning"

        # Verificar temperatura
        if info.get("temperature", {}).get("available"):
            for sensor in info["temperature"].get("sensors", []):
                temp = sensor["temperature_c"]
                if temp > 90:
                    status["critical"].append(f"Temperatura crítica: {sensor['sensor']} {temp}°C")
                    status["overall"] = "critical"
                elif temp > 80:
                    status["warnings"].append(f"Temperatura alta: {sensor['sensor']} {temp}°C")
                    if status["overall"] == "healthy":
                        status["overall"] = "warning"

        # Verificar bateria (laptops)
        if self.hardware_info["is_laptop"] and info.get("battery", {}).get("available"):
            battery = info["battery"]
            if battery["percent"] < 10 and not battery["is_plugged"]:
                status["critical"].append(f"Bateria crítica: {battery['percent']}%")
                status["overall"] = "critical"
            elif battery["percent"] < 20 and not battery["is_plugged"]:
                status["warnings"].append(f"Bateria baixa: {battery['percent']}%")
                if status["overall"] == "healthy":
                    status["overall"] = "warning"

        return status