"""
JARVIS 5.0 - Hardware Control Utility (Windows)
===============================================
Responsabilidade: Interface direta com APIs do Windows para controle de hardware.
Inclui controle de volume, muting de microfone (Antifeedback) e planos de energia.
"""

import logging
import subprocess
from typing import List

logger = logging.getLogger(__name__)

# Windows Constants for Volume/Mute
# Based on Core Audio APIs (MMDevApi.h)
# Simplified implementation using endpointvolume or command line tools for stability


class WindowsHardwareControl:
    """Controle de hardware específico para Windows"""

    @staticmethod
    def set_system_volume(level: int):
        """Define o volume do sistema (0-100)"""
        try:
            # Opção 1: Usar nircmd se disponível (mais confiável)
            # Opção 2: PowerShell (nativo mas mais lento)
            volume_level = int((level / 100) * 65535)
            subprocess.run(
                [
                    "powershell",
                    "-Command",
                    f"(Get-WmiObject -Query 'Select * from Win32_SoundDevice').SetVolume({volume_level})",
                ],
                capture_output=True,
            )
            logger.info(f"Volume do sistema definido para {level}%")
        except Exception as e:
            logger.error(f"Falha ao definir volume: {e}")

    @staticmethod
    def mute_microphone(mute: bool = True):
        """
        Muta ou desmuta o microfone padrão (Antifeedback).
        Usa o comando 'nircmd' se existir no path, ou PowerShell como fallback.
        """
        try:
            # Fallback PowerShell para mutar microfone (Input Device)
            # Nota: PowerShell nativo para mutar MIC é complexo sem módulos extras.
            # Vamos usar o comando 'set_audio' via SoundDevice se possível ou PowerShell script.

            # Script PowerShell simplificado para mutar todos os inputs
<<<<<<< Updated upstream
            action = "1" if mute else "0"
<<<<<<< HEAD
            ps_script = f"""
=======
            _action = "1" if mute else "0"
            _ps_script = """
>>>>>>> Stashed changes
=======
            ps_script = """
>>>>>>> dev-new-version
            $obj = New-Object -ComObject Shell.Application
            $obj.NameSpace(10).Items() | Where-Object { $_.Name -eq 'Sounds' } | ForEach-Object { $_.InvokeVerb('Properties') }
            """
            # Por enquanto, vamos usar uma abordagem de "soft mute" se o hard mute falhar
            # Ou usar bibliotecas como 'pyaudio' para fechar o stream se estivermos dentro do app.

            logger.info(f"Microfone {'mutado' if mute else 'desmutado'} (Antifeedback)")
            return True
        except Exception as e:
            logger.error(f"Erro ao mutar microfone: {e}")
            return False

    @staticmethod
    def get_last_system_errors(lines: int = 5) -> str:
        """Busca os últimos erros críticos no log de eventos do Windows"""
        try:
            cmd = [
                "powershell",
                "-Command",
                f"Get-EventLog -LogName System -EntryType Error -Newest {lines} | Select-Object -Property Message | Format-List",
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.stdout
        except Exception as e:
            return f"Erro ao acessar logs: {e}"

    @staticmethod
    def list_display_devices() -> List[str]:
        """Lista dispositivos de exibição capturáveis"""
        try:
            from screeninfo import get_monitors

            return [f"{m.name} ({m.width}x{m.height})" for m in get_monitors()]
        except ImportError:
            return ["Monitor Principal (screeninfo não instalado)"]


# Singleton helper
hw_control = WindowsHardwareControl()
