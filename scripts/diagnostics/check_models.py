import os
from dotenv import load_dotenv
from google import genai

# Carregar .env
load_dotenv(r'C:\Users\willi\Documents\GitHub\PROJECT_JARVIS_5.0\env\.env')
api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key, http_options={'api_version': 'v1beta'})

try:
    print("Listando modelos...")
    for m in client.models.list():
        # No SDK novo, o nome do modelo está em m.name
        # E os métodos suportados em m.supported_generation_methods (se existir)
        # Vamos apenas imprimir o que for relevante
        print(f"- {m.name}")
except Exception as e:
    print(f"Erro: {e}")
