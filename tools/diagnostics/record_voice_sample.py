import pyaudio
import wave
import os
from pathlib import Path

def record_voice_sample():
    SAMPLE_RATE = 22050
    DURATION = 10  # 10 seconds
    OUTPUT_PATH = "data/voice_signatures/william.wav"

    # Ensure directory exists
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    p = pyaudio.PyAudio()
    
    try:
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=SAMPLE_RATE, input=True)

        print("\n" + "="*50)
        print("🎤 JARVIS VOICE CLONING - ASSINATURA DE VOZ")
        print("="*50)
        print("Fale naturalmente por 10 segundos...")
        print("Variações de entonação ajudam na qualidade.")
        print("Iniciando em 3... 2... 1...")
        
        frames = []
        for i in range(0, int(SAMPLE_RATE / 1024 * DURATION)):
            data = stream.read(1024)
            frames.append(data)

        print("\n✅ Gravação concluída!")

        stream.stop_stream()
        stream.close()
        p.terminate()

        # Salvar
        with wave.open(OUTPUT_PATH, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes(b''.join(frames))

        print(f"📦 Assinatura salva em: {OUTPUT_PATH}")
        print("="*50 + "\n")
        
    except Exception as e:
        print(f"❌ Erro ao gravar: {e}")
        p.terminate()

if __name__ == "__main__":
    record_voice_sample()
