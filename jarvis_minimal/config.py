# Minimal Jarvis configuration (safe defaults)
HOTWORD = "jarvis"
OLLAMA_MODEL = "llama"   # change to your local model name available in Ollama
SAMPLE_RATE = 16000
CHUNK_SECONDS = 4
AUTO_TRAIN = True          # user requested full automatic training
AUTO_APPLY_FIXES = False   # keep False by default; trainer writes suggestions to ./autofix
INTERACTIONS_LOG = "data/interactions.jsonl"
TTS_RATE = 150
LISTEN_TIMEOUT = 10       # seconds to listen after wakeword

# Enable Whisper STT? (set True if you want local Whisper and have disk/CPU/GPU resources)
USE_WHISPER = False

# Conversation/context settings
CONTEXT_WINDOW = 6           # number of previous exchanges to include in prompt
SYSTEM_PROMPT = (
    "Você é Jarvis, um assistente pessoal de elite. "
    "Responda SEMPRE em Português do Brasil de forma extremamente útil e precisa. "
    "Mantenha o contexto das últimas interações."
)

# Enable local neural brain? If False, sempre usará apenas Ollama.
USE_LOCAL_BRAIN = True

# Idioma do dispositivo
DEVICE_LANGUAGE = "pt-br"
LANGUAGE_VALIDATION = True  # validar idioma das entradas contra o idioma do dispositivo (nativo)

# TTS backends e preferências
# backends: 'edge-tts' (online, neural), 'pyttsx3' (local, SAPI)
TTS_BACKEND_PREFERENCE = ["edge-tts", "pyttsx3"]  # ordem de preferência, 'auto' behavior
TTS_PYTTSX3_VOICE = None       # nome/exact id da voice pyttsx3 (None = auto)
TTS_EDGE_VOICE = "pt-BR-AntonioNeural"  # voz neural padrão para edge-tts
TTS_VOLUME = 1.0
TTS_RATE = 150


