import ctypes
from ctypes import wintypes
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

def set_system_volume(level):
    """
    Seta o volume do sistema Windows.
    :param level: Float entre 0.0 e 1.0
    """
    try:
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = interface.QueryInterface(IAudioEndpointVolume)
        volume.SetMasterVolumeLevelScalar(level, None)
        return True
    except Exception as e:
        print(f"Erro ao ajustar volume: {e}")
        return False

if __name__ == "__main__":
    # Teste: Volume 50%
    set_system_volume(0.5)
    print("Volume ajustado para 50%")
