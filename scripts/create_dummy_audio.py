import wave
import struct


def create_silent_wav(filename, duration=1.0):
    sample_rate = 44100
    num_samples = int(sample_rate * duration)

    with wave.open(filename, "w") as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 2 bytes per sample (16-bit)
        wav_file.setframerate(sample_rate)

        # Write silence
        for _ in range(num_samples):
            wav_file.writeframes(struct.pack("h", 0))


if __name__ == "__main__":
    create_silent_wav(
        r"c:\Users\willi\Documents\GitHub\PROJECT_JARVIS_5.0\data\voice_signatures\jarvis_reference.wav"
    )
    print("Created silent reference audio.")
