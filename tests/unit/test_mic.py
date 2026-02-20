import speech_recognition as sr
import pyaudio


def test_mic():
    print("🧪 Testando Microfone...")
    p = pyaudio.PyAudio()
    info = p.get_host_api_info_by_index(0)
    numdevices = info.get("deviceCount")

    print(f"Dispositivos encontrados: {numdevices}")
    for i in range(0, numdevices):
        if (
            p.get_device_info_by_host_api_device_index(0, i).get("maxInputChannels")
        ) > 0:
            print(
                f"Input Device id {i} - {p.get_device_info_by_host_api_device_index(0, i).get('name')}"
            )

    try:
        r = sr.Recognizer()
        with sr.Microphone() as source:
            print("Ajustando ruído... fale algo em 3 segundos.")
            r.adjust_for_ambient_noise(source, duration=1)
            audio = r.listen(source, timeout=5)
            print("Processando...")
            text = r.recognize_google(audio, language="pt-BR")
            print(f"✅ Mic OK: Ouvi '{text}'")
    except Exception as e:
        print(f"❌ ERRO MIC: {type(e).__name__}: {e}")


if __name__ == "__main__":
    test_mic()
