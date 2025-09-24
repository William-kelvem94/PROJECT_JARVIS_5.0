# Plugin de voz/texto gratuito usando pyttsx3 (TTS) e SpeechRecognition (STT)

import pyttsx3
import speech_recognition as sr

class VoicePlugin:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.recognizer = sr.Recognizer()

    def speak(self, text: str):
        self.engine.say(text)
        self.engine.runAndWait()

    def listen(self):
        with sr.Microphone() as source:
            print("Fale algo...")
            audio = self.recognizer.listen(source)
        try:
            return self.recognizer.recognize_google(audio, language="pt-BR")
        except Exception as e:
            return f"Erro no reconhecimento: {e}"
